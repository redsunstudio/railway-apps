"""
Complete Physio Weekly Summary - Main Application
Collects content from Instagram, YouTube, Blog, and Newsletter
Sends weekly email summary every Friday afternoon
"""

import os
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

from instagram_scraper import InstagramScraper
from rss_parser import RSSParser
from email_formatter import EmailFormatter
from email_sender import EmailSender
from scheduler import WeeklyScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global status tracker
app_status = {
    'scheduler_running': False,
    'last_run': None,
    'version': '1.0.0',
    'start_time': datetime.now().isoformat()
}


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP server for health checks"""

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'scheduler_running': app_status['scheduler_running'],
                'last_run': app_status['last_run'],
                'version': app_status['version'],
                'start_time': app_status['start_time']
            }

            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass


class CompletePhysioSummary:
    def __init__(self):
        """Initialize all modules and load configuration"""
        logger.info("Initializing Complete Physio Weekly Summary")

        # Load configuration from environment variables
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME', 'completephysio')
        self.youtube_rss = os.getenv('YOUTUBE_RSS_URL', '')
        self.blog_rss = os.getenv('BLOG_RSS_URL', '')
        self.blog2_rss = os.getenv('BLOG2_RSS_URL', '')  # Second blog
        self.newsletter_rss = os.getenv('NEWSLETTER_RSS_URL', '')

        # Initialize modules
        self.instagram_scraper = InstagramScraper()
        self.rss_parser = RSSParser()
        self.email_formatter = EmailFormatter()
        self.email_sender = EmailSender()

        logger.info("Initialization complete")

    def collect_all_content(self):
        """
        Collect content from all sources (Instagram, YouTube, Blog, Newsletter)

        Returns:
            tuple: (instagram_posts, youtube_entries, blog_entries, newsletter_entries)
        """
        logger.info("="*60)
        logger.info("Starting content collection from all sources")
        logger.info("="*60)

        # Collect Instagram posts
        logger.info("\n1. Collecting Instagram posts...")
        instagram_posts = []
        if self.instagram_username:
            instagram_posts = self.instagram_scraper.get_recent_posts(
                self.instagram_username, days=7
            )
            logger.info(f"   ✓ Found {len(instagram_posts)} Instagram posts")
        else:
            logger.warning("   ⚠ Instagram username not configured")

        # Collect YouTube videos
        logger.info("\n2. Collecting YouTube videos...")
        youtube_entries = []
        if self.youtube_rss:
            youtube_entries = self.rss_parser.parse_feed(
                self.youtube_rss, days=7, feed_type='youtube'
            )
            logger.info(f"   ✓ Found {len(youtube_entries)} YouTube videos")
        else:
            logger.warning("   ⚠ YouTube RSS URL not configured")

        # Collect blog posts (combining both blogs)
        logger.info("\n3. Collecting blog posts...")
        blog_entries = []
        if self.blog_rss:
            blog1_entries = self.rss_parser.parse_feed(
                self.blog_rss, days=7, feed_type='blog'
            )
            blog_entries.extend(blog1_entries)
            logger.info(f"   ✓ Found {len(blog1_entries)} posts from Complete Physio blog")

        if self.blog2_rss:
            blog2_entries = self.rss_parser.parse_feed(
                self.blog2_rss, days=7, feed_type='blog'
            )
            blog_entries.extend(blog2_entries)
            logger.info(f"   ✓ Found {len(blog2_entries)} posts from Ultrasound Injections blog")

        if not self.blog_rss and not self.blog2_rss:
            logger.warning("   ⚠ Blog RSS URLs not configured")

        logger.info(f"   ✓ Total blog posts: {len(blog_entries)}")

        # Collect newsletters
        logger.info("\n4. Collecting newsletters...")
        newsletter_entries = []
        if self.newsletter_rss:
            newsletter_entries = self.rss_parser.parse_feed(
                self.newsletter_rss, days=7, feed_type='newsletter'
            )
            logger.info(f"   ✓ Found {len(newsletter_entries)} newsletters")
        else:
            logger.warning("   ⚠ Newsletter RSS URL not configured")

        logger.info("\n" + "="*60)
        logger.info("Content collection complete")
        logger.info(f"Total items: {len(instagram_posts) + len(youtube_entries) + len(blog_entries) + len(newsletter_entries)}")
        logger.info("="*60)

        return instagram_posts, youtube_entries, blog_entries, newsletter_entries

    def generate_and_send_summary(self):
        """Main task: collect content and send weekly summary email"""
        try:
            # Update last run time
            app_status['last_run'] = datetime.now().isoformat()

            # Collect all content
            instagram_posts, youtube_entries, blog_entries, newsletter_entries = self.collect_all_content()

            # Generate email
            logger.info("\nGenerating email summary...")
            subject, html_body, text_body = self.email_formatter.create_weekly_summary(
                instagram_posts, youtube_entries, blog_entries, newsletter_entries
            )
            logger.info(f"✓ Email generated: {subject}")

            # Send email
            logger.info("\nSending email...")
            success = self.email_sender.send_weekly_summary(subject, html_body, text_body)

            if success:
                logger.info("\n" + "="*60)
                logger.info("✅ WEEKLY SUMMARY SENT SUCCESSFULLY")
                logger.info("="*60)
            else:
                logger.error("\n" + "="*60)
                logger.error("❌ FAILED TO SEND WEEKLY SUMMARY")
                logger.error("="*60)

            return success

        except Exception as e:
            logger.error(f"\n❌ Error generating and sending summary: {str(e)}")
            raise

    def run_scheduler(self):
        """Start the scheduler to run weekly summaries every Friday"""
        logger.info("Starting weekly scheduler...")
        app_status['scheduler_running'] = True

        scheduler = WeeklyScheduler(self.generate_and_send_summary)
        scheduler.run_forever()

    def run_once(self):
        """Run the summary generation once (for testing)"""
        logger.info("Running summary generation once (test mode)")
        return self.generate_and_send_summary()


def start_health_server():
    """Start the health check HTTP server in a background thread"""
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()


def main():
    """Main entry point"""
    # Start health check server in background thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    app = CompletePhysioSummary()

    # Check if running in test mode
    test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'

    if test_mode:
        logger.info("="*60)
        logger.info("TEST MODE - Running once")
        logger.info("="*60)
        app.run_once()
    else:
        logger.info("="*60)
        logger.info("PRODUCTION MODE - Starting scheduler")
        logger.info("="*60)
        app.run_scheduler()


if __name__ == "__main__":
    main()
