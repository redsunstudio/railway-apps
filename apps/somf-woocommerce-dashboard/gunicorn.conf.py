# Gunicorn configuration for SOMF WooCommerce Dashboard
import os
import threading

# Basic settings
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = 1  # Single worker to simplify caching
threads = 8  # More threads to handle concurrent requests
timeout = 300  # 5 minutes to handle slow WooCommerce API
graceful_timeout = 300

# Don't use preload since each worker needs its own cache warming
preload_app = False

def post_worker_init(worker):
    """Called just after a worker has been initialized."""
    worker.log.info(f"Worker {worker.pid} initialized")

    # Start background refresh after a delay (allows worker to start accepting requests first)
    def delayed_refresh():
        import time
        time.sleep(5)  # Wait 5 seconds for worker to be fully ready
        try:
            from app import start_background_refresh, logger
            logger.info(f"Worker {worker.pid}: Starting background data refresh")
            start_background_refresh()
        except Exception as e:
            worker.log.error(f"Worker {worker.pid}: Background refresh failed: {e}")

    import threading
    t = threading.Thread(target=delayed_refresh, daemon=True)
    t.start()

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting SOMF Dashboard")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server ready - workers will pre-warm their caches")
