# Gunicorn configuration for SOMF WooCommerce Dashboard
import os
import threading

# Basic settings
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = 2
threads = 4
timeout = 120

# Don't use preload since each worker needs its own cache warming
preload_app = False

def post_worker_init(worker):
    """Called just after a worker has been initialized.

    Start cache warming in a background thread for each worker.
    This ensures the WooCommerce data is fetched before user requests.
    """
    worker.log.info(f"Worker {worker.pid} initialized - starting cache pre-warm")

    def warm_cache():
        try:
            from app import get_cached_subscriptions, get_cached_orders, logger
            from datetime import datetime, timedelta
            from dateutil.relativedelta import relativedelta

            logger.info(f"Worker {worker.pid}: Pre-warming subscriptions cache...")
            get_cached_subscriptions()
            logger.info(f"Worker {worker.pid}: Subscriptions cache warmed")

            # Also pre-warm orders for current and prior month (used by metrics)
            logger.info(f"Worker {worker.pid}: Pre-warming orders cache...")
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            prior_month_start = month_start - relativedelta(months=1)
            prior_month_end = month_start - timedelta(seconds=1)

            # Fetch MTD orders
            get_cached_orders(month_start, now)
            # Fetch prior month orders
            get_cached_orders(prior_month_start, prior_month_end)

            logger.info(f"Worker {worker.pid}: All caches pre-warmed successfully")
        except Exception as e:
            worker.log.error(f"Worker {worker.pid}: Cache pre-warm failed: {e}")

    # Start warming in background so worker can start accepting requests
    t = threading.Thread(target=warm_cache, daemon=True)
    t.start()

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting SOMF Dashboard")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server ready - workers will pre-warm their caches")
