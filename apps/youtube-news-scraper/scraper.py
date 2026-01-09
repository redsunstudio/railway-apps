import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict
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

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _is_recent(self, date_str: str, max_days: int = 1) -> bool:
        """Check if article is within the max_days threshold"""
        try:
            if not date_str:
                return True  # Include if no date available

            # Try parsing various date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%a, %d %b %Y %H:%M:%S %Z']:
                try:
                    article_date = datetime.strptime(date_str, fmt)
                    cutoff_date = datetime.now() - timedelta(days=max_days)
                    return article_date >= cutoff_date
                except ValueError:
                    continue

            return True  # Include if date parsing fails
        except Exception as e:
            logger.warning(f"Date parsing error: {e}")
            return True

    def _fetch_page(self, url: str) -> str:
        """Fetch page content"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
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

                                    # Try to find date
                                    date_elem = element.find(['time', 'span'], class_=lambda x: x and ('date' in x or 'time' in x))
                                    published_date = date_elem.get_text(strip=True) if date_elem else None

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
        """Scrape all enabled sources"""
        all_articles = []

        for source in self.config['sources']:
            try:
                articles = self.scrape_source(source)
                all_articles.extend(articles)
                logger.info(f"Found {len(articles)} articles from {source['name']}")
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")

        # Remove duplicates based on title similarity
        unique_articles = self._deduplicate_articles(all_articles)

        logger.info(f"Total unique articles found: {len(unique_articles)}")
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
