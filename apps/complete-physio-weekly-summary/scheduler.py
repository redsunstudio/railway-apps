"""
Scheduler Module
Runs weekly summary collection and email sending every Friday afternoon
"""

import schedule
import time
import logging
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeeklyScheduler:
    def __init__(self, task_function):
        """
        Initialize scheduler with a task function to run

        Args:
            task_function: Function to execute on schedule (should take no arguments)
        """
        self.task_function = task_function
        self.timezone = pytz.timezone('Europe/London')  # UK timezone for Complete Physio

    def job(self):
        """Wrapper for the scheduled job with logging"""
        logger.info(f"{'='*60}")
        logger.info(f"Running scheduled job at {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"{'='*60}")

        try:
            self.task_function()
            logger.info(f"✅ Scheduled job completed successfully")
        except Exception as e:
            logger.error(f"❌ Scheduled job failed: {str(e)}")
            raise

    def run_forever(self):
        """
        Start the scheduler and run forever
        Executes task every Friday at 3:00 PM UK time
        """
        # Schedule for Friday at 3:00 PM UK time
        schedule.every().friday.at("15:00").do(self.job)

        logger.info("="*60)
        logger.info("Weekly Scheduler Started")
        logger.info("="*60)
        logger.info(f"Current time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"Schedule: Every Friday at 3:00 PM UK time")
        logger.info(f"Next run: {schedule.next_run()}")
        logger.info("="*60)

        # Run immediately on first start (for testing)
        logger.info("Running initial job immediately for testing...")
        self.job()

        # Keep running forever
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def test_scheduler():
    """Test the scheduler with a dummy function"""
    def dummy_task():
        print(f"Test task executed at {datetime.now()}")

    scheduler = WeeklyScheduler(dummy_task)
    print("Testing scheduler (will run immediately, then wait for next Friday)...")
    print("Press Ctrl+C to stop")

    try:
        scheduler.run_forever()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")


if __name__ == "__main__":
    test_scheduler()
