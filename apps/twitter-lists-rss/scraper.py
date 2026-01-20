"""
Twitter List Scraper
Scrapes tweets from public Twitter lists using Apify
"""

import re
import logging
import requests
from datetime import datetime, timezone
import os
import time

logger = logging.getLogger(__name__)

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
APIFY_ACTOR = 'apidojo/twitter-list-scraper'


class TwitterListScraper:
    """Scrapes Twitter lists using Apify"""

    def __init__(self):
        self.session = requests.Session()
        if APIFY_TOKEN:
            self.session.headers.update({
                'Authorization': f'Bearer {APIFY_TOKEN}',
                'Content-Type': 'application/json'
            })

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
        Scrape tweets from a Twitter list using Apify
        """
        if not APIFY_TOKEN:
            logger.error("APIFY_TOKEN not set")
            return []

        list_info = self.parse_list_url(url)
        if not list_info:
            logger.error(f"Could not parse URL: {url}")
            return []

        try:
            # Start the Apify Actor
            run_url = f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/runs"

            # Prepare input based on list type
            actor_input = {
                "maxItems": max_tweets
            }

            if list_info['type'] == 'numeric':
                actor_input["listIds"] = [list_info['list_id']]
            else:
                # For named lists, use the URL directly
                actor_input["startUrls"] = [url]

            logger.info(f"Starting Apify actor with input: {actor_input}")

            # Start the run
            response = self.session.post(
                run_url,
                json=actor_input,
                params={'token': APIFY_TOKEN},
                timeout=30
            )

            if response.status_code != 201:
                logger.error(f"Failed to start Apify actor: {response.status_code} - {response.text}")
                return []

            run_data = response.json()
            run_id = run_data['data']['id']
            logger.info(f"Apify run started: {run_id}")

            # Wait for the run to complete (poll every 2 seconds, max 2 minutes)
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
            max_wait = 120
            waited = 0

            while waited < max_wait:
                time.sleep(2)
                waited += 2

                status_response = self.session.get(
                    status_url,
                    params={'token': APIFY_TOKEN},
                    timeout=10
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data['data']['status']

                    if status == 'SUCCEEDED':
                        logger.info(f"Apify run completed successfully")
                        break
                    elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                        logger.error(f"Apify run failed with status: {status}")
                        return []

                    logger.debug(f"Apify run status: {status}, waited {waited}s")

            if waited >= max_wait:
                logger.error("Apify run timed out")
                return []

            # Get the results from the dataset
            dataset_id = status_data['data']['defaultDatasetId']
            dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"

            dataset_response = self.session.get(
                dataset_url,
                params={'token': APIFY_TOKEN, 'limit': max_tweets},
                timeout=30
            )

            if dataset_response.status_code != 200:
                logger.error(f"Failed to get dataset: {dataset_response.status_code}")
                return []

            items = dataset_response.json()
            tweets = self._parse_apify_results(items)

            logger.info(f"Successfully scraped {len(tweets)} tweets via Apify")
            return tweets

        except Exception as e:
            logger.error(f"Error scraping with Apify: {e}")
            return []

    def _parse_apify_results(self, items):
        """Parse Apify dataset items into our tweet format"""
        tweets = []

        for item in items:
            try:
                # Extract tweet ID
                tweet_id = item.get('id_str') or item.get('id') or ''

                # Extract author info
                user = item.get('user', {})
                username = user.get('screen_name') or user.get('username') or 'unknown'
                name = user.get('name') or username

                # Extract content
                content = item.get('full_text') or item.get('text') or ''

                # Extract timestamp
                created_at = item.get('created_at')
                if created_at:
                    try:
                        # Twitter format: "Mon Jan 15 10:30:00 +0000 2024"
                        timestamp = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
                    except:
                        timestamp = datetime.now(timezone.utc)
                else:
                    timestamp = datetime.now(timezone.utc)

                # Extract stats
                stats = {
                    'replies': item.get('reply_count', 0),
                    'retweets': item.get('retweet_count', 0),
                    'likes': item.get('favorite_count', 0)
                }

                # Extract media
                media = []
                entities = item.get('entities', {})
                media_entities = entities.get('media', [])
                for m in media_entities:
                    media_url = m.get('media_url_https') or m.get('media_url')
                    if media_url:
                        media.append({
                            'type': m.get('type', 'image'),
                            'url': media_url
                        })

                # Build tweet URL
                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}" if tweet_id else ''

                tweets.append({
                    'id': str(tweet_id),
                    'author': {
                        'username': username,
                        'name': name
                    },
                    'content': content,
                    'url': tweet_url,
                    'timestamp': timestamp.isoformat() if timestamp else None,
                    'stats': stats,
                    'media': media
                })

            except Exception as e:
                logger.debug(f"Error parsing tweet: {e}")
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

    if APIFY_TOKEN:
        tweets = scraper.scrape_list(test_url, max_tweets=5)
        print(f"Found {len(tweets)} tweets")

        for tweet in tweets[:3]:
            print(f"\n--- Tweet ---")
            print(f"Author: @{tweet['author']['username']}")
            print(f"Content: {tweet['content'][:100]}...")
    else:
        print("APIFY_TOKEN not set - skipping scrape test")
