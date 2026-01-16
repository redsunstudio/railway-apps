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
    # Note: Cache warming disabled for debugging - will warm on first request

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting SOMF Dashboard")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server ready - workers will pre-warm their caches")
