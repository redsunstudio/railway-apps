"""
Background scheduler for periodic tweet fetching
Runs every 2 hours to ensure no tweets are missed
"""

import os
import logging
import threading
import time
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from scraper import TwitterListScraper
from lists_manager import ListsManager
from database import store_tweets, cleanup_old_tweets, record_fetch, get_tweet_count

logger = logging.getLogger(__name__)

# Configuration
FETCH_INTERVAL_HOURS = int(os.environ.get('FETCH_INTERVAL_HOURS', 2))
RETENTION_DAYS = int(os.environ.get('RETENTION_DAYS', 30))

# Global scheduler instance
_scheduler = None
_scheduler_lock = threading.Lock()


def fetch_all_lists():
    """Fetch tweets from all configured lists"""
    logger.info("Starting scheduled fetch for all lists...")

    lists_manager = ListsManager()
    scraper = TwitterListScraper()

    lists = lists_manager.get_all_lists()
    if not lists:
        logger.info("No lists configured, skipping fetch")
        return

    total_new = 0
    for lst in lists:
        if not lst.get('enabled', True):
            continue

        list_id = lst['list_id']
        list_url = lst['url']
        list_name = lst.get('name', list_id)

        try:
            logger.info(f"Fetching list: {list_name} ({list_id})")

            # Scrape tweets
            tweets = scraper.scrape_list(list_url)

            if tweets:
                # Store in database
                stored, new_count = store_tweets(list_id, tweets)
                total_new += new_count

                # Record successful fetch
                record_fetch(list_id, len(tweets), new_count, 'success')

                # Update last fetched time
                lists_manager.update_last_fetched(list_id)

                logger.info(f"List {list_name}: found {len(tweets)} tweets, {new_count} new")
            else:
                record_fetch(list_id, 0, 0, 'empty', 'No tweets found')
                logger.warning(f"List {list_name}: no tweets found")

        except Exception as e:
            logger.error(f"Error fetching list {list_name}: {e}")
            record_fetch(list_id, 0, 0, 'error', str(e))

        # Small delay between lists to avoid rate limiting
        time.sleep(2)

    logger.info(f"Scheduled fetch complete. {total_new} new tweets stored.")


def cleanup_task():
    """Periodic cleanup of old tweets"""
    logger.info(f"Running cleanup task (retention: {RETENTION_DAYS} days)...")
    deleted = cleanup_old_tweets(RETENTION_DAYS)
    logger.info(f"Cleanup complete. {deleted} old tweets removed.")


def start_scheduler():
    """Start the background scheduler"""
    global _scheduler

    with _scheduler_lock:
        if _scheduler is not None:
            logger.info("Scheduler already running")
            return _scheduler

        logger.info(f"Starting scheduler (fetch interval: {FETCH_INTERVAL_HOURS}h, retention: {RETENTION_DAYS}d)")

        _scheduler = BackgroundScheduler(
            timezone='UTC',
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 3600
            }
        )

        # Add fetch job - runs every N hours
        _scheduler.add_job(
            fetch_all_lists,
            trigger=IntervalTrigger(hours=FETCH_INTERVAL_HOURS),
            id='fetch_all_lists',
            name='Fetch tweets from all lists',
            replace_existing=True
        )

        # Add cleanup job - runs daily
        _scheduler.add_job(
            cleanup_task,
            trigger=IntervalTrigger(days=1),
            id='cleanup_old_tweets',
            name='Cleanup old tweets',
            replace_existing=True
        )

        _scheduler.start()
        logger.info("Scheduler started successfully")

        # Run initial fetch in background after a short delay
        threading.Timer(10, fetch_all_lists).start()

        return _scheduler


def stop_scheduler():
    """Stop the background scheduler"""
    global _scheduler

    with _scheduler_lock:
        if _scheduler is not None:
            _scheduler.shutdown(wait=False)
            _scheduler = None
            logger.info("Scheduler stopped")


def get_scheduler_status():
    """Get current scheduler status"""
    global _scheduler

    if _scheduler is None:
        return {'running': False}

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None
        })

    return {
        'running': _scheduler.running,
        'jobs': jobs,
        'fetch_interval_hours': FETCH_INTERVAL_HOURS,
        'retention_days': RETENTION_DAYS
    }


def trigger_fetch_now():
    """Manually trigger an immediate fetch"""
    logger.info("Manual fetch triggered")
    threading.Thread(target=fetch_all_lists, daemon=True).start()
    return True


if __name__ == '__main__':
    # Test scheduler
    logging.basicConfig(level=logging.INFO)
    start_scheduler()

    try:
        while True:
            time.sleep(60)
            print(f"Status: {get_scheduler_status()}")
    except KeyboardInterrupt:
        stop_scheduler()
