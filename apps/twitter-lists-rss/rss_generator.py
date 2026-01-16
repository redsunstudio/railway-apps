"""
RSS Feed Generator
Generates RSS 2.0 feeds from scraped tweet data
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone
import html
import re
import os


class RSSGenerator:
    """Generates RSS feeds from tweet data"""

    def __init__(self):
        self.base_url = os.getenv('BASE_URL', 'http://localhost:3000')

    def generate(self, list_id, list_name, list_url, tweets):
        """
        Generate an RSS 2.0 feed from tweets

        Args:
            list_id: The Twitter list ID
            list_name: Human-readable name for the list
            list_url: Original Twitter list URL
            tweets: List of tweet dictionaries

        Returns:
            RSS XML string
        """
        # Create root RSS element
        rss = ET.Element('rss')
        rss.set('version', '2.0')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        rss.set('xmlns:dc', 'http://purl.org/dc/elements/1.1/')

        # Create channel
        channel = ET.SubElement(rss, 'channel')

        # Channel metadata
        title = ET.SubElement(channel, 'title')
        title.text = f"Twitter List: {list_name}"

        link = ET.SubElement(channel, 'link')
        link.text = list_url

        description = ET.SubElement(channel, 'description')
        description.text = f"RSS feed for Twitter list: {list_name}"

        language = ET.SubElement(channel, 'language')
        language.text = 'en'

        # Last build date
        last_build = ET.SubElement(channel, 'lastBuildDate')
        last_build.text = self._format_rss_date(datetime.now(timezone.utc))

        # Generator
        generator = ET.SubElement(channel, 'generator')
        generator.text = 'Twitter Lists RSS Converter'

        # Atom self link
        atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
        atom_link.set('href', f"{self.base_url}/feed/{list_id}")
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')

        # TTL (time to live in minutes)
        ttl = ET.SubElement(channel, 'ttl')
        ttl.text = '15'

        # Add items for each tweet
        for tweet in tweets:
            item = self._create_item(tweet)
            channel.append(item)

        # Generate pretty XML
        return self._prettify(rss)

    def _create_item(self, tweet):
        """Create an RSS item from a tweet"""
        item = ET.Element('item')

        # Title - use first 100 chars of content or author name
        title = ET.SubElement(item, 'title')
        content = tweet.get('content', '')
        author = tweet.get('author', {})
        username = author.get('username', 'unknown')
        name = author.get('name', username)

        # Create a meaningful title
        if content:
            # Remove URLs from title, truncate
            clean_content = re.sub(r'https?://\S+', '', content).strip()
            title_text = clean_content[:100]
            if len(clean_content) > 100:
                title_text += '...'
            title.text = f"@{username}: {title_text}" if title_text else f"Tweet by @{username}"
        else:
            title.text = f"Tweet by @{username}"

        # Link
        link = ET.SubElement(item, 'link')
        link.text = tweet.get('url', '')

        # GUID
        guid = ET.SubElement(item, 'guid')
        guid.set('isPermaLink', 'true')
        guid.text = tweet.get('url', tweet.get('id', ''))

        # Description (full content with HTML formatting)
        description = ET.SubElement(item, 'description')
        description.text = self._format_description(tweet)

        # Author
        dc_creator = ET.SubElement(item, '{http://purl.org/dc/elements/1.1/}creator')
        dc_creator.text = f"@{username}"

        # Publication date
        pub_date = ET.SubElement(item, 'pubDate')
        timestamp = tweet.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    dt = datetime.now(timezone.utc)
            else:
                dt = timestamp
            pub_date.text = self._format_rss_date(dt)
        else:
            pub_date.text = self._format_rss_date(datetime.now(timezone.utc))

        return item

    def _format_description(self, tweet):
        """Format tweet content as HTML description"""
        content = tweet.get('content', '')
        author = tweet.get('author', {})
        stats = tweet.get('stats', {})
        media = tweet.get('media', [])

        # Escape HTML in content
        content_html = html.escape(content)

        # Convert URLs to links
        content_html = re.sub(
            r'(https?://[^\s]+)',
            r'<a href="\1">\1</a>',
            content_html
        )

        # Convert @mentions to links
        content_html = re.sub(
            r'@(\w+)',
            r'<a href="https://twitter.com/\1">@\1</a>',
            content_html
        )

        # Convert hashtags to links
        content_html = re.sub(
            r'#(\w+)',
            r'<a href="https://twitter.com/hashtag/\1">#\1</a>',
            content_html
        )

        # Build full description
        parts = []

        # Author info
        username = author.get('username', 'unknown')
        name = author.get('name', username)
        parts.append(f'<p><strong>{html.escape(name)}</strong> <a href="https://twitter.com/{username}">@{username}</a></p>')

        # Tweet content
        parts.append(f'<p>{content_html}</p>')

        # Media
        for m in media:
            if m.get('type') == 'image':
                parts.append(f'<p><img src="{html.escape(m.get("url", ""))}" alt="Tweet image" style="max-width:100%;" /></p>')

        # Stats
        if stats:
            stat_parts = []
            if stats.get('retweets'):
                stat_parts.append(f"{stats['retweets']} retweets")
            if stats.get('likes'):
                stat_parts.append(f"{stats['likes']} likes")
            if stats.get('replies'):
                stat_parts.append(f"{stats['replies']} replies")
            if stat_parts:
                parts.append(f'<p style="color:#666;font-size:0.9em;">{" | ".join(stat_parts)}</p>')

        return '\n'.join(parts)

    def _format_rss_date(self, dt):
        """Format datetime for RSS (RFC 822)"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime('%a, %d %b %Y %H:%M:%S %z')

    def _prettify(self, elem):
        """Return pretty-printed XML string"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding=None)


# Test
if __name__ == '__main__':
    generator = RSSGenerator()

    test_tweets = [
        {
            'id': '123456789',
            'author': {'username': 'testuser', 'name': 'Test User'},
            'content': 'This is a test tweet with a link https://example.com and @mention and #hashtag',
            'url': 'https://twitter.com/testuser/status/123456789',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'stats': {'retweets': 100, 'likes': 500},
            'media': []
        }
    ]

    rss = generator.generate(
        list_id='12345',
        list_name='Test List',
        list_url='https://twitter.com/i/lists/12345',
        tweets=test_tweets
    )

    print(rss)
