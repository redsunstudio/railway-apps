"""
Instagram Scraper Module
Scrapes recent Instagram posts using instaloader library
"""

import instaloader
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramScraper:
    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
        )

    def get_recent_posts(self, username, days=7):
        """
        Get Instagram posts from the last N days

        Args:
            username: Instagram username (without @)
            days: Number of days to look back (default 7)

        Returns:
            List of post dictionaries with keys: date, caption, url, likes, image_url
        """
        try:
            logger.info(f"Fetching Instagram posts for @{username} from last {days} days")

            profile = instaloader.Profile.from_username(self.loader.context, username)
            posts = []

            cutoff_date = datetime.now() - timedelta(days=days)

            for post in profile.get_posts():
                # Stop if we've gone back too far
                if post.date_utc.replace(tzinfo=None) < cutoff_date:
                    break

                posts.append({
                    'date': post.date_utc.replace(tzinfo=None),
                    'caption': post.caption or '',
                    'url': f"https://www.instagram.com/p/{post.shortcode}/",
                    'likes': post.likes,
                    'image_url': post.url,
                    'type': 'image' if not post.is_video else 'video'
                })

            logger.info(f"Found {len(posts)} posts from the last {days} days")
            return posts

        except Exception as e:
            logger.error(f"Error scraping Instagram for @{username}: {str(e)}")
            return []


def test_scraper():
    """Test function to verify Instagram scraping works"""
    scraper = InstagramScraper()
    # Test with a public account
    posts = scraper.get_recent_posts("instagram", days=7)

    if posts:
        print(f"\nFound {len(posts)} posts:")
        for post in posts[:3]:  # Show first 3
            print(f"\n- Date: {post['date']}")
            print(f"  Caption: {post['caption'][:100]}...")
            print(f"  URL: {post['url']}")
            print(f"  Likes: {post['likes']}")
    else:
        print("No posts found")


if __name__ == "__main__":
    test_scraper()
