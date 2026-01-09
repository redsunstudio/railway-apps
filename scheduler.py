import schedule
import time
from datetime import datetime
import logging
import os
from scraper import YouTubeNewsScraper
from email_sender import EmailSender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsScheduler:
    def __init__(self):
        self.scraper = YouTubeNewsScraper()
        self.email_sender = EmailSender()
        self.schedule_time = os.getenv('SCHEDULE_TIME', '07:00')  # Default 7 AM

    def run_daily_scrape(self):
        """Execute daily scraping and email sending"""
        logger.info("=" * 80)
        logger.info(f"Starting daily scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        try:
            # Scrape all sources
            logger.info("Scraping news sources...")
            articles = self.scraper.scrape_all()

            # Convert articles to dict format
            articles_dict = [article.to_dict() for article in articles]

            logger.info(f"Found {len(articles_dict)} articles to send")

            # Send email digest
            logger.info("Sending email digest...")
            success = self.email_sender.send_digest(articles_dict)

            if success:
                logger.info("✅ Daily digest sent successfully!")
            else:
                logger.error("❌ Failed to send daily digest")

        except Exception as e:
            logger.error(f"❌ Error during daily scrape: {e}", exc_info=True)

        logger.info("=" * 80)
        logger.info(f"Completed daily scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

    def start(self):
        """Start the scheduler"""
        logger.info(f"🚀 YouTube News Scraper started")
        logger.info(f"📅 Scheduled to run daily at {self.schedule_time}")
        logger.info(f"📧 Emails will be sent to: {self.email_sender.recipient_email}")

        # Schedule the daily job
        schedule.every().day.at(self.schedule_time).do(self.run_daily_scrape)

        # Also run once immediately for testing (optional - remove in production if not desired)
        run_on_startup = os.getenv('RUN_ON_STARTUP', 'false').lower() == 'true'
        if run_on_startup:
            logger.info("🔄 Running immediate test scrape...")
            self.run_daily_scrape()

        # Keep running
        logger.info("⏰ Scheduler is running. Press Ctrl+C to stop.")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == '__main__':
    try:
        scheduler = NewsScheduler()
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("\n👋 Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
