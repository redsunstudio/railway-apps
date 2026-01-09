import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import json
import os
import time
import random
from typing import List, Dict
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsArticle:
    def __init__(self, title: str, url: str, source: str, published_date: str = None, summary: str = None):
        self.title = title
        self.url = url
        self.source = source
        self.published_date = published_date
        self.summary = summary

    def to_dict(self):
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date,
            'summary': self.summary
        }


class YouTubeNewsScraper:
    def __init__(self, config_path='news_sources.json'):
        self.config = self._load_config(config_path)
        self.headers = {
            'User-Agent': self.config['scraping_settings']['user_agent']
        }
        self.timeout = self.config['scraping_settings']['request_timeout']

        # Rate limiting
        self.request_count = defaultdict(int)
        self.last_request_time = defaultdict(float)
        self.min_delay = self.config['scraping_settings'].get('min_delay_seconds', 2)
        self.max_delay = self.config['scraping_settings'].get('max_delay_seconds', 5)
        self.max_retries = self.config['scraping_settings'].get('max_retries', 3)
        self.retry_delay = self.config['scraping_settings'].get('retry_delay_seconds', 5)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _is_recent(self, date_str: str, max_days: int = 1) -> bool:
        """Check if article is within the max_days threshold (strict 24 hours)"""
        try:
            if not date_str:
                # No date = assume old, exclude it
                logger.debug(f"No date provided, excluding article")
                return False

            # Normalize date string
            date_str = date_str.strip()

            # Try parsing various date formats
            date_formats = [
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%a, %d %b %Y %H:%M:%S %Z',
                '%a, %d %b %Y %H:%M:%S %z',
                '%B %d, %Y',
                '%b %d, %Y',
                '%d %B %Y',
                '%d %b %Y',
                '%Y/%m/%d',
                '%m/%d/%Y',
                '%d-%m-%Y',
            ]

            article_date = None
            for fmt in date_formats:
                try:
                    article_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue

            # If still couldn't parse, try dateutil as fallback
            if not article_date:
                try:
                    from dateutil import parser
                    article_date = parser.parse(date_str)
                except:
                    # Can't parse date = exclude it to be safe
                    logger.debug(f"Could not parse date '{date_str}', excluding article")
                    return False

            # Check if within last 24 hours
            # Make both timezone-aware or both timezone-naive for comparison
            cutoff_date = datetime.now() - timedelta(days=max_days)

            # If article_date has timezone info, make cutoff_date aware too
            if article_date.tzinfo is not None and article_date.tzinfo.utcoffset(article_date) is not None:
                # Article date is timezone-aware, make cutoff timezone-aware (UTC)
                from datetime import timezone
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_days)
            else:
                # Article date is naive, make sure cutoff is naive too
                cutoff_date = datetime.now() - timedelta(days=max_days)

            is_recent = article_date >= cutoff_date

            if not is_recent:
                logger.debug(f"Article date {article_date} is older than {cutoff_date}, excluding")

            return is_recent

        except Exception as e:
            logger.warning(f"Date parsing error for '{date_str}': {e}")
            return False  # Exclude if error

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL for rate limiting"""
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def _rate_limit_delay(self, domain: str):
        """Apply rate limiting delay based on domain"""
        current_time = time.time()
        last_request = self.last_request_time.get(domain, 0)
        time_since_last = current_time - last_request

        # Calculate required delay with randomization to appear more human-like
        required_delay = random.uniform(self.min_delay, self.max_delay)

        if time_since_last < required_delay:
            sleep_time = required_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s for {domain}")
            time.sleep(sleep_time)

        self.last_request_time[domain] = time.time()
        self.request_count[domain] += 1

    def _fetch_page(self, url: str, retry_count: int = 0) -> str:
        """Fetch page content with rate limiting and retry logic"""
        domain = self._get_domain(url)

        try:
            # Apply rate limiting
            self._rate_limit_delay(domain)

            logger.debug(f"Fetching {url} (attempt {retry_count + 1}/{self.max_retries + 1})")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            # Handle rate limiting responses
            if response.status_code == 429:  # Too Many Requests
                if retry_count < self.max_retries:
                    retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                    logger.warning(f"Rate limited by {domain}. Retrying after {retry_after}s")
                    time.sleep(retry_after)
                    return self._fetch_page(url, retry_count + 1)
                else:
                    logger.error(f"Max retries exceeded for {url}")
                    return None

            response.raise_for_status()
            logger.info(f"Successfully fetched {domain} ({len(response.text)} bytes)")
            return response.text

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            if retry_count < self.max_retries:
                time.sleep(self.retry_delay)
                return self._fetch_page(url, retry_count + 1)
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            if retry_count < self.max_retries:
                time.sleep(self.retry_delay)
                return self._fetch_page(url, retry_count + 1)
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    def _extract_articles_generic(self, html: str, source_name: str, keywords: List[str]) -> List[NewsArticle]:
        """Generic article extraction using common HTML patterns"""
        articles = []

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Common article selectors
            article_selectors = [
                'article',
                '.post',
                '.article',
                '.entry',
                '[class*="post"]',
                '[class*="article"]',
                '.search-result',
                '.story'
            ]

            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:10]:  # Limit to first 10 matches
                        title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)

                            # Check if title contains relevant keywords
                            if any(keyword.lower() in title.lower() for keyword in keywords):
                                link_elem = element.find('a', href=True)
                                if link_elem:
                                    url = link_elem['href']
                                    if url.startswith('/'):
                                        url = source_name + url

                                    # Try to find date - multiple strategies
                                    published_date = None

                                    # Strategy 1: Look for <time> tag with datetime attribute
                                    time_elem = element.find('time')
                                    if time_elem and time_elem.get('datetime'):
                                        published_date = time_elem.get('datetime')
                                    elif time_elem:
                                        published_date = time_elem.get_text(strip=True)

                                    # Strategy 2: Look for date/time in class names
                                    if not published_date:
                                        date_elem = element.find(['span', 'div'], class_=lambda x: x and ('date' in x.lower() or 'time' in x.lower()))
                                        if date_elem:
                                            published_date = date_elem.get_text(strip=True)

                                    # Strategy 3: Look for common date patterns in text
                                    if not published_date:
                                        import re
                                        text = element.get_text()
                                        # Match patterns like "Jan 9, 2026" or "January 9, 2026"
                                        date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}', text)
                                        if date_match:
                                            published_date = date_match.group(0)

                                    # Try to find summary
                                    summary_elem = element.find(['p', 'div'], class_=lambda x: x and ('excerpt' in x or 'summary' in x))
                                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else None

                                    articles.append(NewsArticle(
                                        title=title,
                                        url=url,
                                        source=source_name,
                                        published_date=published_date,
                                        summary=summary
                                    ))
                    break  # If we found articles with this selector, stop trying others

        except Exception as e:
            logger.error(f"Error extracting articles from {source_name}: {e}")

        return articles

    def _try_rss_feed(self, base_url: str, source_name: str) -> List[NewsArticle]:
        """Try to find and parse RSS feed"""
        articles = []

        # Common RSS feed paths
        rss_paths = ['/feed/', '/rss/', '/feed', '/rss', '/atom.xml', '/feed.xml']

        for path in rss_paths:
            try:
                feed_url = base_url.rstrip('/') + path
                feed = feedparser.parse(feed_url)

                if feed.entries:
                    for entry in feed.entries[:5]:
                        articles.append(NewsArticle(
                            title=entry.get('title', 'No title'),
                            url=entry.get('link', ''),
                            source=source_name,
                            published_date=entry.get('published', None),
                            summary=entry.get('summary', None)
                        ))
                    break  # Found working feed
            except Exception as e:
                continue

        return articles

    def scrape_source(self, source: dict) -> List[NewsArticle]:
        """Scrape a single news source"""
        if not source.get('enabled', True):
            return []

        logger.info(f"Scraping: {source['name']}")
        articles = []

        # Fetch page content
        html = self._fetch_page(source['url'])
        if not html:
            return articles

        # Extract articles using generic method
        articles = self._extract_articles_generic(
            html,
            source['name'],
            source.get('keywords', [])
        )

        # If no articles found, try RSS feed
        if not articles:
            logger.info(f"Trying RSS feed for {source['name']}")
            articles = self._try_rss_feed(source['url'], source['name'])

        # Filter by date
        max_days = self.config['scraping_settings']['article_age_days']
        recent_articles = [
            article for article in articles
            if self._is_recent(article.published_date, max_days)
        ]

        # Limit number of articles
        max_articles = self.config['scraping_settings']['max_articles_per_source']
        return recent_articles[:max_articles]

    def scrape_all(self) -> List[NewsArticle]:
        """Scrape all enabled sources with rate limiting"""
        all_articles = []
        enabled_sources = [s for s in self.config['sources'] if s.get('enabled', True)]

        logger.info(f"Starting scrape of {len(enabled_sources)} sources")
        start_time = time.time()

        for idx, source in enumerate(enabled_sources, 1):
            try:
                logger.info(f"[{idx}/{len(enabled_sources)}] Scraping {source['name']}...")
                articles = self.scrape_source(source)
                all_articles.extend(articles)
                logger.info(f"✓ Found {len(articles)} articles from {source['name']}")
            except Exception as e:
                logger.error(f"✗ Error scraping {source['name']}: {e}")

        # Remove duplicates based on title similarity
        unique_articles = self._deduplicate_articles(all_articles)

        elapsed = time.time() - start_time
        logger.info(f"Scraping complete in {elapsed:.1f}s")
        logger.info(f"Total: {len(all_articles)} articles, {len(unique_articles)} unique")
        logger.info(f"Request stats: {dict(self.request_count)}")

        return unique_articles

    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique = []

        for article in articles:
            # Normalize title for comparison
            normalized = article.title.lower().strip()
            if normalized not in seen_titles:
                seen_titles.add(normalized)
                unique.append(article)

        return unique


if __name__ == '__main__':
    # Test the scraper
    scraper = YouTubeNewsScraper()
    articles = scraper.scrape_all()

    print(f"\nFound {len(articles)} articles:\n")
    for article in articles:
        print(f"Source: {article.source}")
        print(f"Title: {article.title}")
        print(f"URL: {article.url}")
        print(f"Date: {article.published_date}")
        print("-" * 80)
