"""
RSS Feed Parser Module
Parses RSS feeds for YouTube, Blog, and Newsletter
"""

import feedparser
from datetime import datetime, timedelta
import logging
import ssl
import urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSParser:
    def __init__(self):
        # Disable SSL verification for local testing (Railway will have proper certs)
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass

    def parse_feed(self, feed_url, days=7, feed_type='generic'):
        """
        Parse RSS feed and return entries from the last N days

        Args:
            feed_url: RSS feed URL
            days: Number of days to look back (default 7)
            feed_type: Type of feed ('youtube', 'blog', 'newsletter', 'generic')

        Returns:
            List of entry dictionaries with keys: date, title, url, description, thumbnail
        """
        try:
            logger.info(f"Parsing {feed_type} RSS feed: {feed_url}")

            feed = feedparser.parse(feed_url)

            if feed.bozo and feed.entries:
                logger.debug(f"Feed has bozo flag but has entries: {feed.bozo_exception}")
            elif feed.bozo:
                logger.warning(f"Feed parsing issue: {feed.bozo_exception}")

            entries = []
            cutoff_date = datetime.now() - timedelta(days=days)

            for entry in feed.entries:
                # Parse date from various possible fields
                entry_date = self._parse_entry_date(entry)

                if entry_date and entry_date < cutoff_date:
                    continue

                parsed_entry = {
                    'date': entry_date or datetime.now(),
                    'title': entry.get('title', 'No Title'),
                    'url': entry.get('link', ''),
                    'description': self._clean_description(entry.get('summary', entry.get('description', ''))),
                    'thumbnail': self._extract_thumbnail(entry),
                    'feed_type': feed_type
                }

                entries.append(parsed_entry)

            logger.info(f"Found {len(entries)} {feed_type} entries from the last {days} days")
            return entries

        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {str(e)}")
            return []

    def _parse_entry_date(self, entry):
        """Extract and parse date from RSS entry"""
        # Try different date fields
        for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, date_field):
                date_tuple = getattr(entry, date_field)
                if date_tuple:
                    try:
                        return datetime(*date_tuple[:6])
                    except:
                        pass

        # Try string parsing
        for date_field in ['published', 'updated', 'created']:
            if date_field in entry:
                try:
                    from dateutil import parser
                    return parser.parse(entry[date_field])
                except:
                    pass

        return None

    def _clean_description(self, description):
        """Clean HTML and truncate description"""
        import re

        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', description)
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        # Truncate to 300 characters
        if len(clean) > 300:
            clean = clean[:297] + '...'

        return clean

    def _extract_thumbnail(self, entry):
        """Extract thumbnail/image URL from RSS entry"""
        # Try media:thumbnail
        if 'media_thumbnail' in entry and entry.media_thumbnail:
            return entry.media_thumbnail[0].get('url', '')

        # Try media:content
        if 'media_content' in entry and entry.media_content:
            return entry.media_content[0].get('url', '')

        # Try enclosure
        if 'enclosures' in entry and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'image' in enclosure.get('type', ''):
                    return enclosure.get('href', '')

        # Try to find image in content
        if 'content' in entry:
            import re
            content = str(entry.content)
            img_match = re.search(r'<img[^>]+src="([^"]+)"', content)
            if img_match:
                return img_match.group(1)

        return ''


def test_parser():
    """Test function to verify RSS parsing works"""
    parser = RSSParser()

    # Test with a known RSS feed
    test_feeds = {
        'YouTube': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCBJycsmduvYEL83R_U4JriQ',  # Sample
        'Blog': 'https://www.completephysio.co.uk/feed'  # Example blog feed
    }

    for feed_type, feed_url in test_feeds.items():
        print(f"\n{'='*60}")
        print(f"Testing {feed_type} feed")
        print(f"{'='*60}")

        entries = parser.parse_feed(feed_url, days=30, feed_type=feed_type.lower())

        if entries:
            print(f"\nFound {len(entries)} entries:")
            for entry in entries[:2]:  # Show first 2
                print(f"\n- Date: {entry['date']}")
                print(f"  Title: {entry['title']}")
                print(f"  URL: {entry['url']}")
                print(f"  Description: {entry['description'][:100]}...")
        else:
            print(f"No entries found for {feed_type}")


if __name__ == "__main__":
    test_parser()
