import schedule
import time
from datetime import datetime
import logging
import os
from scraper import YouTubeNewsScraper
from email_sender import EmailSender

# Try to import Gmail API sender
try:
    from gmail_api_sender import GmailAPISender
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_email_sender():
    """Get appropriate email sender based on available credentials"""
    if GMAIL_API_AVAILABLE and os.getenv('GMAIL_CREDENTIALS_JSON') and os.getenv('GMAIL_TOKEN_JSON'):
        logger.info("Using Gmail API for email sending")
        return GmailAPISender()
    else:
        logger.info("Using SMTP for email sending")
        return EmailSender()


class NewsScheduler:
    def __init__(self):
        self.scraper = YouTubeNewsScraper()
        self.email_sender = get_email_sender()
        self.schedule_time = os.getenv('SCHEDULE_TIME', '03:00')  # Default 3 AM UTC (7 AM UAE)

    def run_daily_scrape(self):
        """Execute daily scraping and email sending"""
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info(f"🎬 Starting daily scrape at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        try:
            # Scrape all sources
            logger.info("🔍 Scraping news sources...")
            scrape_start = datetime.now()
            articles = self.scraper.scrape_all()
            scrape_duration = (datetime.now() - scrape_start).total_seconds()

            # Convert articles to dict format
            articles_dict = [article.to_dict() for article in articles]

            logger.info(f"✅ Scraping completed in {scrape_duration:.2f} seconds")
            logger.info(f"📰 Found {len(articles_dict)} articles to send")

            if len(articles_dict) == 0:
                logger.warning("⚠️  No articles found to send. Skipping email.")
            else:
                # Log article sources breakdown
                sources = {}
                for article in articles_dict:
                    source = article.get('source', 'Unknown')
                    sources[source] = sources.get(source, 0) + 1
                logger.info(f"📊 Articles by source: {sources}")

                # Send email digest
                logger.info("📤 Sending email digest...")
                email_start = datetime.now()

                try:
                    success = self.email_sender.send_digest(articles_dict)
                    email_duration = (datetime.now() - email_start).total_seconds()

                    if success:
                        logger.info(f"✅ Email digest sent successfully in {email_duration:.2f} seconds!")
                        logger.info(f"📧 Sent to: {self.email_sender.recipient_email}")
                    else:
                        logger.error(f"❌ Failed to send email digest (returned False after {email_duration:.2f} seconds)")
                        logger.error(f"📧 Attempted to send to: {self.email_sender.recipient_email}")

                except Exception as email_error:
                    logger.error(f"❌ Exception while sending email: {email_error}", exc_info=True)

        except Exception as e:
            logger.error(f"❌ Error during daily scrape: {e}", exc_info=True)
            logger.error(f"🔍 Error type: {type(e).__name__}")

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        logger.info("=" * 80)
        logger.info(f"🏁 Completed daily scrape at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏱️  Total duration: {total_duration:.2f} seconds")
        logger.info("=" * 80)

    def start(self):
        """Start the scheduler"""
        logger.info("=" * 80)
        logger.info(f"🚀 YouTube News Scraper started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📅 Scheduled to run daily at {self.schedule_time}")
        logger.info(f"📧 Emails will be sent to: {self.email_sender.recipient_email}")

        # Log email sender type
        email_sender_type = type(self.email_sender).__name__
        logger.info(f"📨 Email sender type: {email_sender_type}")

        # Log environment info
        logger.info(f"🌍 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⚙️  SCHEDULE_TIME env var: {os.getenv('SCHEDULE_TIME', 'not set (using default 03:00)')}")
        logger.info(f"⚙️  RUN_ON_STARTUP env var: {os.getenv('RUN_ON_STARTUP', 'not set (using default false)')}")
        logger.info("=" * 80)

        # Schedule the daily job
        job = schedule.every().day.at(self.schedule_time).do(self.run_daily_scrape)

        # Log next run time
        next_run = schedule.next_run()
        if next_run:
            logger.info(f"⏰ Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

        # Also run once immediately for testing (optional - remove in production if not desired)
        run_on_startup = os.getenv('RUN_ON_STARTUP', 'false').lower() == 'true'
        if run_on_startup:
            logger.info("🔄 Running immediate test scrape (RUN_ON_STARTUP=true)...")
            self.run_daily_scrape()

        # Keep running
        logger.info("⏰ Scheduler is running. Press Ctrl+C to stop.")
        logger.info("=" * 80)

        # Track iterations for periodic status updates
        iteration = 0

        while True:
            schedule.run_pending()

            # Log scheduler status every 60 minutes (60 iterations)
            iteration += 1
            if iteration % 60 == 0:
                next_run = schedule.next_run()
                if next_run:
                    logger.info(f"💓 Scheduler heartbeat - Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}, Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logger.warning("⚠️  No scheduled jobs found!")

            time.sleep(60)  # Check every minute


if __name__ == '__main__':
    try:
        scheduler = NewsScheduler()
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("\n👋 Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
