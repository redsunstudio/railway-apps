"""
Twitter List Scraper
Scrapes tweets from public Twitter lists without using the official API
Uses multiple methods: Nitter instances, syndication API, and direct scraping
"""

import re
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time
import random
from urllib.parse import urlparse, urljoin
import json

logger = logging.getLogger(__name__)

# Nitter instances to try (public instances)
NITTER_INSTANCES = [
    'https://nitter.privacydev.net',
    'https://nitter.poast.org',
    'https://nitter.woodland.cafe',
    'https://nitter.1d4.us',
    'https://nitter.kavin.rocks',
    'https://nitter.unixfox.eu',
]


class TwitterListScraper:
    """Scrapes Twitter lists using multiple fallback methods"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.working_nitter = None

    def parse_list_url(self, url):
        """
        Parse a Twitter/X list URL and extract the list ID
        Supports formats:
        - https://twitter.com/i/lists/1234567890
        - https://x.com/i/lists/1234567890
        - https://twitter.com/username/lists/listname
        """
        if not url:
            return None

        url = url.strip()

        # Pattern for numeric list ID
        numeric_pattern = r'(?:twitter\.com|x\.com)/i/lists/(\d+)'
        match = re.search(numeric_pattern, url)
        if match:
            return {
                'list_id': match.group(1),
                'type': 'numeric'
            }

        # Pattern for named lists (username/lists/listname)
        named_pattern = r'(?:twitter\.com|x\.com)/([^/]+)/lists/([^/?\s]+)'
        match = re.search(named_pattern, url)
        if match:
            username = match.group(1)
            listname = match.group(2)
            return {
                'list_id': f"{username}_{listname}",
                'username': username,
                'listname': listname,
                'type': 'named'
            }

        return None

    def scrape_list(self, url, max_tweets=50):
        """
        Scrape tweets from a Twitter list
        Tries multiple methods in order of reliability
        """
        tweets = []

        # Try Nitter first (most reliable for RSS-like data)
        tweets = self._try_nitter(url, max_tweets)
        if tweets:
            logger.info(f"Successfully scraped {len(tweets)} tweets via Nitter")
            return tweets

        # Try direct scraping with guest token
        tweets = self._try_guest_api(url, max_tweets)
        if tweets:
            logger.info(f"Successfully scraped {len(tweets)} tweets via guest API")
            return tweets

        # Try syndication endpoint
        tweets = self._try_syndication(url, max_tweets)
        if tweets:
            logger.info(f"Successfully scraped {len(tweets)} tweets via syndication")
            return tweets

        logger.warning(f"Could not scrape tweets from {url}")
        return []

    def _try_nitter(self, url, max_tweets):
        """Try to fetch from Nitter instances"""
        list_info = self.parse_list_url(url)
        if not list_info:
            return []

        # Shuffle instances to distribute load
        instances = NITTER_INSTANCES.copy()
        if self.working_nitter:
            # Try working instance first
            instances.remove(self.working_nitter)
            instances.insert(0, self.working_nitter)
        else:
            random.shuffle(instances)

        for nitter_base in instances:
            try:
                # Nitter list URL format
                if list_info['type'] == 'numeric':
                    nitter_url = f"{nitter_base}/i/lists/{list_info['list_id']}"
                else:
                    nitter_url = f"{nitter_base}/{list_info['username']}/lists/{list_info['listname']}"

                logger.info(f"Trying Nitter: {nitter_url}")

                response = self.session.get(nitter_url, timeout=15)
                if response.status_code == 200:
                    tweets = self._parse_nitter_html(response.text, nitter_base)
                    if tweets:
                        self.working_nitter = nitter_base
                        return tweets[:max_tweets]

            except requests.RequestException as e:
                logger.debug(f"Nitter {nitter_base} failed: {e}")
                continue
            except Exception as e:
                logger.debug(f"Error parsing Nitter response: {e}")
                continue

            time.sleep(0.5)  # Rate limiting

        return []

    def _parse_nitter_html(self, html, base_url):
        """Parse tweets from Nitter HTML"""
        tweets = []
        soup = BeautifulSoup(html, 'html.parser')

        # Find tweet containers
        tweet_items = soup.find_all('div', class_='timeline-item')

        for item in tweet_items:
            try:
                tweet = self._extract_nitter_tweet(item, base_url)
                if tweet:
                    tweets.append(tweet)
            except Exception as e:
                logger.debug(f"Error extracting tweet: {e}")
                continue

        return tweets

    def _extract_nitter_tweet(self, item, base_url):
        """Extract tweet data from a Nitter timeline item"""
        # Skip retweet indicators, pinned tweets, etc.
        if item.find('div', class_='retweet-header'):
            return None

        # Get author info
        fullname_elem = item.find('a', class_='fullname')
        username_elem = item.find('a', class_='username')

        if not username_elem:
            return None

        username = username_elem.get_text(strip=True).replace('@', '')
        fullname = fullname_elem.get_text(strip=True) if fullname_elem else username

        # Get tweet content
        content_elem = item.find('div', class_='tweet-content')
        content = content_elem.get_text(strip=True) if content_elem else ''

        # Get tweet link and ID
        tweet_link = item.find('a', class_='tweet-link')
        tweet_url = ''
        tweet_id = ''
        if tweet_link:
            href = tweet_link.get('href', '')
            tweet_url = f"https://twitter.com{href.replace('#m', '')}"
            # Extract tweet ID from URL
            id_match = re.search(r'/status/(\d+)', href)
            if id_match:
                tweet_id = id_match.group(1)

        # Get timestamp
        time_elem = item.find('span', class_='tweet-date')
        timestamp = None
        if time_elem:
            time_link = time_elem.find('a')
            if time_link:
                title = time_link.get('title', '')
                try:
                    # Nitter format: "Jan 15, 2024 · 10:30 AM UTC"
                    timestamp = self._parse_nitter_date(title)
                except:
                    timestamp = datetime.now(timezone.utc)

        if not timestamp:
            timestamp = datetime.now(timezone.utc)

        # Get stats
        stats = {}
        stat_container = item.find('div', class_='tweet-stat')
        if stat_container:
            for stat in stat_container.find_all('div', class_='icon-container'):
                icon = stat.find('span', class_=True)
                value = stat.get_text(strip=True)
                if icon:
                    classes = icon.get('class', [])
                    if 'icon-comment' in classes:
                        stats['replies'] = self._parse_stat(value)
                    elif 'icon-retweet' in classes:
                        stats['retweets'] = self._parse_stat(value)
                    elif 'icon-heart' in classes:
                        stats['likes'] = self._parse_stat(value)

        # Get media
        media = []
        media_container = item.find('div', class_='attachments')
        if media_container:
            for img in media_container.find_all('img'):
                src = img.get('src', '')
                if src:
                    if src.startswith('/'):
                        src = urljoin(base_url, src)
                    media.append({'type': 'image', 'url': src})

        return {
            'id': tweet_id,
            'author': {
                'username': username,
                'name': fullname
            },
            'content': content,
            'url': tweet_url,
            'timestamp': timestamp.isoformat() if timestamp else None,
            'stats': stats,
            'media': media
        }

    def _parse_nitter_date(self, date_str):
        """Parse Nitter date format"""
        # Clean up the string
        date_str = date_str.replace(' · ', ' ').replace(' UTC', '')
        formats = [
            '%b %d, %Y %I:%M %p',
            '%b %d, %Y %H:%M',
            '%d %b %Y %I:%M %p',
            '%Y-%m-%d %H:%M:%S',
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return datetime.now(timezone.utc)

    def _parse_stat(self, value):
        """Parse stat value like '1.2K' or '500'"""
        if not value:
            return 0
        value = value.strip().upper()
        if 'K' in value:
            return int(float(value.replace('K', '')) * 1000)
        elif 'M' in value:
            return int(float(value.replace('M', '')) * 1000000)
        try:
            return int(value)
        except:
            return 0

    def _try_guest_api(self, url, max_tweets):
        """Try Twitter's guest API (may require guest token)"""
        # This method attempts to use Twitter's public endpoints
        # Note: This may be blocked or rate-limited
        list_info = self.parse_list_url(url)
        if not list_info or list_info['type'] != 'numeric':
            return []

        try:
            # Get guest token
            guest_token = self._get_guest_token()
            if not guest_token:
                return []

            list_id = list_info['list_id']
            api_url = f"https://api.twitter.com/2/lists/{list_id}/tweets"

            headers = {
                'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'x-guest-token': guest_token,
            }

            response = self.session.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_api_response(data)

        except Exception as e:
            logger.debug(f"Guest API failed: {e}")

        return []

    def _get_guest_token(self):
        """Get a guest token for API access"""
        try:
            headers = {
                'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            }
            response = self.session.post(
                'https://api.twitter.com/1.1/guest/activate.json',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get('guest_token')
        except:
            pass
        return None

    def _parse_api_response(self, data):
        """Parse Twitter API response"""
        tweets = []
        # This is a simplified parser - actual API response structure may vary
        if 'data' in data:
            for tweet_data in data['data']:
                tweets.append({
                    'id': tweet_data.get('id', ''),
                    'content': tweet_data.get('text', ''),
                    'url': f"https://twitter.com/i/status/{tweet_data.get('id', '')}",
                    'timestamp': tweet_data.get('created_at'),
                    'author': {'username': 'unknown', 'name': 'Unknown'},
                    'stats': {},
                    'media': []
                })
        return tweets

    def _try_syndication(self, url, max_tweets):
        """Try Twitter's syndication/embed endpoint"""
        list_info = self.parse_list_url(url)
        if not list_info:
            return []

        try:
            # Twitter syndication for timelines
            # Note: This may not work for all lists
            if list_info['type'] == 'numeric':
                syndication_url = f"https://syndication.twitter.com/srv/timeline-list/list/{list_info['list_id']}"

                response = self.session.get(syndication_url, timeout=10)
                if response.status_code == 200:
                    return self._parse_syndication_response(response.text)

        except Exception as e:
            logger.debug(f"Syndication failed: {e}")

        return []

    def _parse_syndication_response(self, html):
        """Parse syndication HTML response"""
        tweets = []
        soup = BeautifulSoup(html, 'html.parser')

        # Syndication uses different HTML structure
        for tweet_div in soup.find_all('div', {'data-tweet-id': True}):
            try:
                tweet_id = tweet_div.get('data-tweet-id', '')
                content = tweet_div.find('p', class_='timeline-Tweet-text')
                author = tweet_div.find('span', class_='timeline-Tweet-author')

                tweets.append({
                    'id': tweet_id,
                    'content': content.get_text(strip=True) if content else '',
                    'url': f"https://twitter.com/i/status/{tweet_id}",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'author': {
                        'username': author.get_text(strip=True) if author else 'unknown',
                        'name': author.get_text(strip=True) if author else 'Unknown'
                    },
                    'stats': {},
                    'media': []
                })
            except Exception as e:
                logger.debug(f"Error parsing syndication tweet: {e}")
                continue

        return tweets


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    scraper = TwitterListScraper()

    test_url = "https://x.com/i/lists/2008820508356435973"
    print(f"Testing URL: {test_url}")

    info = scraper.parse_list_url(test_url)
    print(f"Parsed info: {info}")

    tweets = scraper.scrape_list(test_url)
    print(f"Found {len(tweets)} tweets")

    for tweet in tweets[:3]:
        print(f"\n--- Tweet ---")
        print(f"Author: @{tweet['author']['username']}")
        print(f"Content: {tweet['content'][:100]}...")
