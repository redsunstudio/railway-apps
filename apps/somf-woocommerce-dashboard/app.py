"""
SOMF WooCommerce Dashboard - Backend API
Connects to WooCommerce REST API to fetch subscription and revenue data
Version: 1.3 - Instant cold-start with SQLite preload on startup
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging
import threading
import time
import sqlite3
import atexit

# APScheduler for background refresh
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# WooCommerce API Configuration
WC_URL = os.getenv('WC_URL', 'https://www.stateofmindfitness.com')
WC_CONSUMER_KEY = os.getenv('WC_CONSUMER_KEY')
WC_CONSUMER_SECRET = os.getenv('WC_CONSUMER_SECRET')

# Cache configuration
CACHE_DURATION = 300  # 5 minutes in seconds
cache = {
    'metrics': {'data': None, 'timestamp': None},
    'subscriptions': {'data': None, 'timestamp': None},  # Cache all subscriptions
    'orders': {},  # keyed by date range
    'pending_cancellations': {'data': None, 'timestamp': None},
    'pending_payments': {'data': None, 'timestamp': None},
    'historical_members': {},  # keyed by days
    'historical_revenue': {}   # keyed by days
}
cache_lock = threading.Lock()

# Last API sync tracking
last_api_sync = None

# Database configuration
DB_PATH = os.getenv('DB_PATH', '/app/data/contacted.db')


def init_db():
    """Initialize SQLite database for tracking contacted members and caching data"""
    # Ensure directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table for contacted members
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacted_members (
            subscription_id INTEGER PRIMARY KEY,
            contacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            contacted_by TEXT
        )
    ''')

    # Table for persistent cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache_data (
            cache_key TEXT PRIMARY KEY,
            data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_member_contacted(subscription_id):
    """Check if a member has been marked as contacted"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM contacted_members WHERE subscription_id = ?', (subscription_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result


def mark_member_contacted(subscription_id, contacted_by=None):
    """Mark a member as contacted"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO contacted_members (subscription_id, contacted_at, contacted_by)
        VALUES (?, CURRENT_TIMESTAMP, ?)
    ''', (subscription_id, contacted_by))
    conn.commit()
    conn.close()


def unmark_member_contacted(subscription_id):
    """Remove contacted status from a member"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacted_members WHERE subscription_id = ?', (subscription_id,))
    conn.commit()
    conn.close()


def get_all_contacted_ids():
    """Get all contacted subscription IDs"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT subscription_id FROM contacted_members')
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids


def save_cache_to_db(cache_key, data):
    """Save cache data to SQLite for persistence across restarts"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO cache_data (cache_key, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (cache_key, json.dumps(data)))
        conn.commit()
        conn.close()
        logger.info(f"Saved {cache_key} to persistent cache")
    except Exception as e:
        logger.error(f"Failed to save {cache_key} to DB: {e}")


def load_cache_from_db(cache_key):
    """Load cache data from SQLite"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT data, updated_at FROM cache_data WHERE cache_key = ?', (cache_key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            data = json.loads(row['data'])
            updated_at = row['updated_at']
            logger.info(f"Loaded {cache_key} from persistent cache (updated: {updated_at})")
            return data, updated_at
        return None, None
    except Exception as e:
        logger.error(f"Failed to load {cache_key} from DB: {e}")
        return None, None


def preload_cache_from_db():
    """Preload all cached data from SQLite into memory on startup.

    This runs BEFORE the scheduler starts, so the first request
    gets instant response from memory instead of waiting for SQLite.
    """
    global _loaded_from_db, last_api_sync

    logger.info("PRELOAD: Loading cached data from SQLite into memory...")
    loaded_any = False

    try:
        # Load subscriptions
        subs_data, subs_time = load_cache_from_db('subscriptions')
        if subs_data:
            with cache_lock:
                cache['subscriptions'] = {
                    'data': subs_data,
                    'timestamp': datetime.now()
                }
            logger.info(f"PRELOAD: Loaded {len(subs_data)} subscriptions from SQLite")
            loaded_any = True

        # Load metrics
        metrics_data, metrics_time = load_cache_from_db('metrics')
        if metrics_data:
            with cache_lock:
                cache['metrics'] = {
                    'data': metrics_data,
                    'timestamp': datetime.now()
                }
            logger.info(f"PRELOAD: Loaded metrics from SQLite")
            loaded_any = True

        if loaded_any:
            _loaded_from_db = True
            last_api_sync = datetime.now()
            logger.info("PRELOAD: Cache preloaded successfully - ready for instant responses!")
        else:
            logger.info("PRELOAD: No cached data in SQLite - will fetch fresh on first request")

    except Exception as e:
        logger.error(f"PRELOAD: Failed to preload cache: {e}")


# Initialize database on startup
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

# Flag to track if we've loaded from DB
_loaded_from_db = False

# Preload cache from SQLite into memory for instant responses
try:
    preload_cache_from_db()
except Exception as e:
    logger.error(f"Failed to preload cache: {e}")


# Background refresh flag
_refresh_in_progress = False

# APScheduler instance
scheduler = BackgroundScheduler(daemon=True)
_scheduler_started = False


def get_wc_auth():
    """Get WooCommerce API authentication"""
    return HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET)


def wc_api_request(endpoint, params=None):
    """Make a request to WooCommerce REST API"""
    global last_api_sync

    url = f"{WC_URL}/wp-json/wc/v3/{endpoint}"
    try:
        response = requests.get(
            url,
            auth=get_wc_auth(),
            params=params or {},
            timeout=30
        )
        response.raise_for_status()
        last_api_sync = datetime.now()
        return response.json(), response.headers
    except requests.exceptions.RequestException as e:
        logger.error(f"WooCommerce API error: {e}")
        raise


def fetch_all_subscriptions():
    """Fetch all subscriptions from WooCommerce API with pagination"""
    all_subscriptions = []
    page = 1
    per_page = 100

    while True:
        try:
            data, headers = wc_api_request('subscriptions', {
                'page': page,
                'per_page': per_page
            })

            if not data:
                break

            all_subscriptions.extend(data)

            # Check if there are more pages
            total_pages = int(headers.get('X-WP-TotalPages', 1))
            if page >= total_pages:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error fetching subscriptions page {page}: {e}")
            break

    return all_subscriptions


def get_cached_subscriptions(allow_api_fetch=False):
    """Get subscriptions from cache - NEVER blocks waiting for API.

    This function always returns instantly from cache.
    If no cache exists, returns empty list and triggers background refresh.
    Set allow_api_fetch=True only for background refresh operations.
    """
    # Check memory cache first
    with cache_lock:
        cached = cache['subscriptions']
        if cached['data'] is not None:
            logger.info(f"Using memory cached subscriptions ({len(cached['data'])} items)")
            return cached['data']

    # Try loading from SQLite (persistent cache)
    db_data, db_time = load_cache_from_db('subscriptions')
    if db_data:
        logger.info(f"Using SQLite cached subscriptions ({len(db_data)} items)")
        with cache_lock:
            cache['subscriptions'] = {
                'data': db_data,
                'timestamp': datetime.now()
            }
        return db_data

    # No cache available - either return empty or fetch if allowed
    if allow_api_fetch:
        # Only used by background refresh - OK to block here
        logger.info("Background refresh: Fetching fresh subscriptions from WooCommerce")
        data = fetch_all_subscriptions()

        # Update memory cache
        with cache_lock:
            cache['subscriptions'] = {
                'data': data,
                'timestamp': datetime.now()
            }

        # Persist to SQLite
        save_cache_to_db('subscriptions', data)
        return data
    else:
        # User-facing request - return empty and trigger background refresh
        logger.warning("No cached subscriptions available - returning empty, triggering background refresh")
        start_background_refresh()
        return []


def get_pending_cancellation_members():
    """Get all members with pending-cancel status including contact details"""
    subscriptions = get_cached_subscriptions()
    contacted_ids = get_all_contacted_ids()

    pending_cancel_members = []
    for sub in subscriptions:
        if sub.get('status', '').lower() == 'pending-cancel':
            billing = sub.get('billing', {})

            member = {
                'subscription_id': sub.get('id'),
                'first_name': billing.get('first_name', ''),
                'last_name': billing.get('last_name', ''),
                'email': billing.get('email', ''),
                'phone': billing.get('phone', ''),
                'next_payment_date': sub.get('next_payment_date_gmt', ''),
                'end_date': sub.get('end_date_gmt', ''),
                'total': sub.get('total', '0'),
                'contacted': sub.get('id') in contacted_ids
            }
            pending_cancel_members.append(member)

    # Sort by name
    pending_cancel_members.sort(key=lambda x: (x['first_name'], x['last_name']))

    return pending_cancel_members


def get_pending_payment_members():
    """Get all members with pending payment status including contact details"""
    subscriptions = get_cached_subscriptions()
    contacted_ids = get_all_contacted_ids()

    pending_payment_members = []
    for sub in subscriptions:
        if sub.get('status', '').lower() == 'pending':
            billing = sub.get('billing', {})

            member = {
                'subscription_id': sub.get('id'),
                'first_name': billing.get('first_name', ''),
                'last_name': billing.get('last_name', ''),
                'email': billing.get('email', ''),
                'phone': billing.get('phone', ''),
                'next_payment_date': sub.get('next_payment_date_gmt', ''),
                'end_date': sub.get('end_date_gmt', ''),
                'total': sub.get('total', '0'),
                'contacted': sub.get('id') in contacted_ids
            }
            pending_payment_members.append(member)

    # Sort by name
    pending_payment_members.sort(key=lambda x: (x['first_name'], x['last_name']))

    return pending_payment_members


def fetch_orders_for_period(start_date, end_date):
    """Fetch orders within a date range from WooCommerce API"""
    all_orders = []
    page = 1
    per_page = 100

    while True:
        try:
            data, headers = wc_api_request('orders', {
                'page': page,
                'per_page': per_page,
                'after': start_date.isoformat(),
                'before': end_date.isoformat(),
                'status': 'completed,processing'
            })

            if not data:
                break

            all_orders.extend(data)

            total_pages = int(headers.get('X-WP-TotalPages', 1))
            if page >= total_pages:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error fetching orders page {page}: {e}")
            break

    return all_orders


def get_cached_orders(start_date, end_date, allow_api_fetch=False):
    """Get orders from cache - NEVER blocks waiting for API.

    This function always returns instantly from cache.
    If no cache exists, returns empty list.
    Set allow_api_fetch=True only for background refresh operations.
    """
    # Create a cache key based on date range (normalize to date only for better caching)
    cache_key = f"{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}"

    # Determine if this is MTD or prior month for DB storage
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    is_mtd = start_date.date() == month_start.date()
    db_key = 'mtd_orders' if is_mtd else 'prior_month_orders'

    # Check memory cache first
    with cache_lock:
        cached = cache['orders'].get(cache_key, {'data': None, 'timestamp': None})
        if cached['data'] is not None:
            logger.info(f"Using memory cached orders for {cache_key}")
            return cached['data']

    # Try loading from SQLite (persistent cache)
    db_data, db_time = load_cache_from_db(db_key)
    if db_data:
        logger.info(f"Using SQLite cached orders for {db_key}")
        with cache_lock:
            cache['orders'][cache_key] = {
                'data': db_data,
                'timestamp': datetime.now()
            }
        return db_data

    # No cache available - either return empty or fetch if allowed
    if allow_api_fetch:
        # Only used by background refresh - OK to block here
        logger.info(f"Background refresh: Fetching orders for {cache_key} from WooCommerce")
        data = fetch_orders_for_period(start_date, end_date)

        # Update memory cache
        with cache_lock:
            cache['orders'][cache_key] = {
                'data': data,
                'timestamp': datetime.now()
            }

        # Persist to SQLite
        save_cache_to_db(db_key, data)
        return data
    else:
        # User-facing request - return empty
        logger.warning(f"No cached orders for {cache_key} - returning empty")
        return []


def calculate_metrics():
    """Calculate all KPI metrics from WooCommerce data"""
    subscriptions = get_cached_subscriptions()

    # Count subscriptions by status
    status_counts = {
        'active': 0,
        'on-hold': 0,
        'pending': 0,
        'pending-cancel': 0,
        'cancelled': 0,
        'expired': 0
    }

    for sub in subscriptions:
        status = sub.get('status', '').lower()
        if status in status_counts:
            status_counts[status] += 1

    # Calculate month-to-date revenue
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = now

    mtd_orders = get_cached_orders(month_start, month_end)
    mtd_revenue = sum(float(order.get('total', 0)) for order in mtd_orders)

    # Calculate prior month revenue
    prior_month_start = (month_start - relativedelta(months=1))
    prior_month_end = month_start - timedelta(seconds=1)

    prior_orders = get_cached_orders(prior_month_start, prior_month_end)
    prior_revenue = sum(float(order.get('total', 0)) for order in prior_orders)

    return {
        'active': status_counts['active'],
        'on-hold': status_counts['on-hold'],
        'pending': status_counts['pending'],
        'pending-cancel': status_counts['pending-cancel'],
        'monthly_revenue': f"£{mtd_revenue:,.2f}",
        'prior_month_revenue': f"£{prior_revenue:,.2f}",
        'last_api_connection': last_api_sync.strftime('%Y-%m-%d %H:%M:%S') if last_api_sync else None
    }


def get_cached_metrics():
    """Get metrics from cache - NEVER blocks waiting for API.

    This function always returns instantly from cache.
    If no cache exists, returns placeholder data and triggers background refresh.
    """
    # Check memory cache first
    with cache_lock:
        cached = cache['metrics']
        if cached['data']:
            logger.info("Using memory cached metrics")
            return cached['data'], 'cache'

    # Try loading from SQLite (persistent cache)
    db_data, db_time = load_cache_from_db('metrics')
    if db_data:
        logger.info("Using SQLite cached metrics")
        with cache_lock:
            cache['metrics'] = {
                'data': db_data,
                'timestamp': datetime.now()
            }
        return db_data, 'sqlite_cache'

    # No cache available - return placeholder and trigger background refresh
    logger.warning("No cached metrics available - returning placeholder, triggering background refresh")
    start_background_refresh()

    # Return placeholder data so dashboard still loads
    placeholder = {
        'active': 0,
        'on-hold': 0,
        'pending': 0,
        'pending-cancel': 0,
        'monthly_revenue': '£0.00',
        'prior_month_revenue': '£0.00',
        'last_api_connection': None,
        'loading': True  # Flag for frontend to show loading state
    }
    return placeholder, 'loading'


def calculate_historical_members(days):
    """Calculate historical active member counts"""
    # This would ideally use WooCommerce subscription history
    # For now, we'll fetch current data and simulate historical trend
    subscriptions = get_cached_subscriptions()
    current_active = sum(1 for s in subscriptions if s.get('status') == 'active')

    # Get subscription dates to build historical data
    historical_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Build daily counts based on subscription start/end dates
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')

        # Count active subscriptions on this date
        active_count = 0
        for sub in subscriptions:
            sub_start = sub.get('date_created', '')
            sub_end = sub.get('end_date', '')

            try:
                start_dt = datetime.fromisoformat(sub_start.replace('Z', '+00:00'))
                start_dt = start_dt.replace(tzinfo=None)

                # Check if subscription was active on this date
                if start_dt.date() <= current_date.date():
                    # If no end date or end date is after current date
                    if not sub_end or sub_end == '':
                        if sub.get('status') in ['active', 'on-hold', 'pending-cancel']:
                            active_count += 1
                    else:
                        try:
                            end_dt = datetime.fromisoformat(sub_end.replace('Z', '+00:00'))
                            end_dt = end_dt.replace(tzinfo=None)
                            if end_dt.date() >= current_date.date():
                                active_count += 1
                        except:
                            if sub.get('status') in ['active', 'on-hold', 'pending-cancel']:
                                active_count += 1
            except Exception as e:
                continue

        # Use current count as fallback if calculation seems off
        if active_count == 0:
            active_count = current_active

        historical_data.append({
            'date': date_str,
            'active_count': active_count
        })

        current_date += timedelta(days=1)

    return historical_data


def calculate_historical_revenue(days):
    """Calculate historical revenue data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Get all orders in the range (cached)
    orders = get_cached_orders(start_date, end_date)

    # Group by date
    daily_revenue = {}
    current_date = start_date
    while current_date <= end_date:
        daily_revenue[current_date.strftime('%Y-%m-%d')] = 0.0
        current_date += timedelta(days=1)

    # Sum order totals by date
    for order in orders:
        order_date = order.get('date_created', '')
        try:
            dt = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
            date_key = dt.strftime('%Y-%m-%d')
            if date_key in daily_revenue:
                daily_revenue[date_key] += float(order.get('total', 0))
        except:
            continue

    # Calculate cumulative prior month revenue for each day
    historical_data = []
    for date_str in sorted(daily_revenue.keys()):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        # Calculate prior month's total revenue as of this date
        prior_month_start = (date_obj.replace(day=1) - relativedelta(months=1))
        prior_month_end = date_obj.replace(day=1) - timedelta(days=1)

        # Sum revenue for prior month
        prior_revenue = 0.0
        for order in orders:
            order_date = order.get('date_created', '')
            try:
                dt = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                if prior_month_start <= dt.replace(tzinfo=None) <= prior_month_end:
                    prior_revenue += float(order.get('total', 0))
            except:
                continue

        # If no prior month orders in our fetched data, estimate based on pattern
        if prior_revenue == 0:
            # Use the current prior month total as baseline
            prior_revenue = sum(daily_revenue.values()) * 0.9

        historical_data.append({
            'date': date_str,
            'revenue': round(prior_revenue, 2)
        })

    return historical_data


def get_cached_historical_members(days):
    """Get historical members from cache or fetch fresh"""
    cache_key = str(days)
    with cache_lock:
        cached = cache['historical_members'].get(cache_key, {'data': None, 'timestamp': None})
        now = datetime.now()

        if cached['data'] and cached['timestamp']:
            age = (now - cached['timestamp']).total_seconds()
            if age < CACHE_DURATION:
                return cached['data'], 'cache'

        try:
            data = calculate_historical_members(days)
            cache['historical_members'][cache_key] = {
                'data': data,
                'timestamp': now
            }
            return data, 'api'
        except Exception as e:
            logger.error(f"Error calculating historical members: {e}")
            if cached['data']:
                return cached['data'], 'stale_cache'
            raise


def get_cached_historical_revenue(days):
    """Get historical revenue from cache or fetch fresh"""
    cache_key = str(days)
    with cache_lock:
        cached = cache['historical_revenue'].get(cache_key, {'data': None, 'timestamp': None})
        now = datetime.now()

        if cached['data'] and cached['timestamp']:
            age = (now - cached['timestamp']).total_seconds()
            if age < CACHE_DURATION:
                return cached['data'], 'cache'

        try:
            data = calculate_historical_revenue(days)
            cache['historical_revenue'][cache_key] = {
                'data': data,
                'timestamp': now
            }
            return data, 'api'
        except Exception as e:
            logger.error(f"Error calculating historical revenue: {e}")
            if cached['data']:
                return cached['data'], 'stale_cache'
            raise


# ============ API Routes ============

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('index.html')


@app.route('/embed')
def embed():
    """Serve embeddable widget for Squarespace/external sites"""
    return render_template('embed.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'wc_configured': bool(WC_CONSUMER_KEY and WC_CONSUMER_SECRET)
    })


@app.route('/api/cache-status')
def api_cache_status():
    """Get current cache status - useful for frontend to show data freshness"""
    with cache_lock:
        subs_cached = cache['subscriptions']['data'] is not None
        subs_count = len(cache['subscriptions']['data']) if subs_cached else 0
        subs_time = cache['subscriptions']['timestamp']

        metrics_cached = cache['metrics']['data'] is not None
        metrics_time = cache['metrics']['timestamp']

    return jsonify({
        'subscriptions_cached': subs_cached,
        'subscriptions_count': subs_count,
        'subscriptions_updated': subs_time.isoformat() if subs_time else None,
        'metrics_cached': metrics_cached,
        'metrics_updated': metrics_time.isoformat() if metrics_time else None,
        'last_api_sync': last_api_sync.isoformat() if last_api_sync else None,
        'refresh_in_progress': _refresh_in_progress,
        'scheduler_running': _scheduler_started
    })


@app.route('/api/metrics')
def api_metrics():
    """Get current KPI metrics"""
    try:
        data, source = get_cached_metrics()
        return jsonify({
            'success': True,
            'data': data,
            'source': source,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
    except Exception as e:
        logger.error(f"Error in /api/metrics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/historical-active-members')
def api_historical_members():
    """Get historical active member counts"""
    try:
        days = int(request.args.get('days', 30))
        days = min(max(days, 7), 365)  # Clamp between 7 and 365

        data, source = get_cached_historical_members(days)
        return jsonify({
            'success': True,
            'data': data,
            'period_days': days,
            'source': source
        })
    except Exception as e:
        logger.error(f"Error in /api/historical-active-members: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/historical-revenue')
def api_historical_revenue():
    """Get historical revenue data"""
    try:
        days = int(request.args.get('days', 30))
        days = min(max(days, 7), 365)  # Clamp between 7 and 365

        data, source = get_cached_historical_revenue(days)
        return jsonify({
            'success': True,
            'data': data,
            'period_days': days,
            'source': source
        })
    except Exception as e:
        logger.error(f"Error in /api/historical-revenue: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def background_refresh():
    """Refresh cache in background without blocking requests.

    This is the main hourly job that fetches fresh data from WooCommerce API.
    """
    global _refresh_in_progress, last_api_sync
    if _refresh_in_progress:
        logger.info("Background refresh already in progress, skipping")
        return

    _refresh_in_progress = True
    start_time = time.time()
    logger.info("=== Starting scheduled background cache refresh ===")

    try:
        # 1. Fetch fresh subscriptions from WooCommerce API
        logger.info("Background refresh: Fetching subscriptions...")
        subs_start = time.time()
        fresh_subscriptions = fetch_all_subscriptions()
        subs_time = time.time() - subs_start

        with cache_lock:
            cache['subscriptions'] = {
                'data': fresh_subscriptions,
                'timestamp': datetime.now()
            }
        save_cache_to_db('subscriptions', fresh_subscriptions)
        logger.info(f"Background refresh: Updated {len(fresh_subscriptions)} subscriptions in {subs_time:.1f}s")

        # 2. Fetch fresh orders for MTD and prior month
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prior_month_start = (month_start - relativedelta(months=1))
        prior_month_end = month_start - timedelta(seconds=1)

        logger.info("Background refresh: Fetching MTD orders...")
        mtd_orders = fetch_orders_for_period(month_start, now)
        mtd_key = f"{month_start.strftime('%Y-%m-%d')}_{now.strftime('%Y-%m-%d')}"
        with cache_lock:
            cache['orders'][mtd_key] = {
                'data': mtd_orders,
                'timestamp': datetime.now()
            }
        save_cache_to_db('mtd_orders', mtd_orders)
        logger.info(f"Background refresh: Updated {len(mtd_orders)} MTD orders")

        logger.info("Background refresh: Fetching prior month orders...")
        prior_orders = fetch_orders_for_period(prior_month_start, prior_month_end)
        prior_key = f"{prior_month_start.strftime('%Y-%m-%d')}_{prior_month_end.strftime('%Y-%m-%d')}"
        with cache_lock:
            cache['orders'][prior_key] = {
                'data': prior_orders,
                'timestamp': datetime.now()
            }
        save_cache_to_db('prior_month_orders', prior_orders)
        logger.info(f"Background refresh: Updated {len(prior_orders)} prior month orders")

        # 3. Calculate and cache metrics
        logger.info("Background refresh: Calculating metrics...")
        status_counts = {
            'active': 0,
            'on-hold': 0,
            'pending': 0,
            'pending-cancel': 0,
            'cancelled': 0,
            'expired': 0
        }

        for sub in fresh_subscriptions:
            status = sub.get('status', '').lower()
            if status in status_counts:
                status_counts[status] += 1

        mtd_revenue = sum(float(order.get('total', 0)) for order in mtd_orders)
        prior_revenue = sum(float(order.get('total', 0)) for order in prior_orders)

        fresh_metrics = {
            'active': status_counts['active'],
            'on-hold': status_counts['on-hold'],
            'pending': status_counts['pending'],
            'pending-cancel': status_counts['pending-cancel'],
            'monthly_revenue': f"£{mtd_revenue:,.2f}",
            'prior_month_revenue': f"£{prior_revenue:,.2f}",
            'last_api_connection': last_api_sync.strftime('%Y-%m-%d %H:%M:%S') if last_api_sync else None
        }

        with cache_lock:
            cache['metrics'] = {
                'data': fresh_metrics,
                'timestamp': datetime.now()
            }
        save_cache_to_db('metrics', fresh_metrics)

        total_time = time.time() - start_time
        logger.info(f"=== Background cache refresh COMPLETE in {total_time:.1f}s ===")
        logger.info(f"    Subscriptions: {len(fresh_subscriptions)}, MTD Orders: {len(mtd_orders)}, Prior Orders: {len(prior_orders)}")

    except Exception as e:
        logger.error(f"Background refresh FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        _refresh_in_progress = False


def start_background_refresh():
    """Start background refresh in a separate thread"""
    t = threading.Thread(target=background_refresh, daemon=True)
    t.start()
    return t


@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """Force refresh all cached data (runs in background, returns immediately)"""
    # Start refresh in background so user doesn't have to wait
    start_background_refresh()
    return jsonify({
        'success': True,
        'message': 'Cache refresh started in background'
    })


@app.route('/api/refresh-sync', methods=['POST'])
def api_refresh_sync():
    """Force refresh all cached data synchronously (for debugging)"""
    global cache
    import time
    start = time.time()

    # Clear memory cache
    with cache_lock:
        cache = {
            'metrics': {'data': None, 'timestamp': None},
            'subscriptions': {'data': None, 'timestamp': None},
            'orders': {},
            'pending_cancellations': {'data': None, 'timestamp': None},
            'pending_payments': {'data': None, 'timestamp': None},
            'historical_members': {},
            'historical_revenue': {}
        }

    try:
        # Fetch subscriptions directly (not cached)
        logger.info("SYNC REFRESH: Fetching subscriptions...")
        subs_start = time.time()
        subs = fetch_all_subscriptions()
        subs_time = time.time() - subs_start
        logger.info(f"SYNC REFRESH: Got {len(subs)} subscriptions in {subs_time}s")

        # Update cache
        with cache_lock:
            cache['subscriptions'] = {
                'data': subs,
                'timestamp': datetime.now()
            }
        save_cache_to_db('subscriptions', subs)

        # Calculate metrics
        logger.info("SYNC REFRESH: Calculating metrics...")
        metrics_start = time.time()
        metrics = calculate_metrics()
        metrics_time = time.time() - metrics_start
        logger.info(f"SYNC REFRESH: Calculated metrics in {metrics_time}s")

        with cache_lock:
            cache['metrics'] = {
                'data': metrics,
                'timestamp': datetime.now()
            }
        save_cache_to_db('metrics', metrics)

        total_time = time.time() - start
        return jsonify({
            'success': True,
            'subscriptions_count': len(subs),
            'subscriptions_time': round(subs_time, 2),
            'metrics': metrics,
            'metrics_time': round(metrics_time, 2),
            'total_time': round(total_time, 2)
        })
    except Exception as e:
        logger.error(f"SYNC REFRESH failed: {e}")
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/pending-cancellations')
def api_pending_cancellations():
    """Get list of members with pending cancellation status"""
    try:
        members = get_pending_cancellation_members()
        return jsonify({
            'success': True,
            'data': members,
            'count': len(members),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
    except Exception as e:
        logger.error(f"Error in /api/pending-cancellations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/pending-payments')
def api_pending_payments():
    """Get list of members with pending payment status"""
    try:
        members = get_pending_payment_members()
        return jsonify({
            'success': True,
            'data': members,
            'count': len(members),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
    except Exception as e:
        logger.error(f"Error in /api/pending-payments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/member/contacted', methods=['POST'])
def api_mark_contacted():
    """Mark a member as contacted"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        contacted = data.get('contacted', True)
        contacted_by = data.get('contacted_by')

        if not subscription_id:
            return jsonify({
                'success': False,
                'error': 'subscription_id is required'
            }), 400

        if contacted:
            mark_member_contacted(subscription_id, contacted_by)
        else:
            unmark_member_contacted(subscription_id)

        return jsonify({
            'success': True,
            'subscription_id': subscription_id,
            'contacted': contacted
        })
    except Exception as e:
        logger.error(f"Error in /api/member/contacted: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/member/contacted/<int:subscription_id>', methods=['GET'])
def api_get_contacted_status(subscription_id):
    """Get contacted status for a specific member"""
    try:
        contacted = is_member_contacted(subscription_id)
        return jsonify({
            'success': True,
            'subscription_id': subscription_id,
            'contacted': contacted
        })
    except Exception as e:
        logger.error(f"Error in /api/member/contacted/{subscription_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============ APScheduler Setup ============

def init_scheduler():
    """Initialize and start the APScheduler for background refresh.

    This sets up:
    1. Hourly background refresh job
    2. Initial refresh on startup (after a short delay to let the app start)
    """
    global _scheduler_started

    if _scheduler_started:
        logger.info("Scheduler already started, skipping")
        return

    try:
        # Add hourly refresh job
        scheduler.add_job(
            func=background_refresh,
            trigger=IntervalTrigger(hours=1),
            id='hourly_refresh',
            name='Hourly cache refresh from WooCommerce',
            replace_existing=True,
            max_instances=1,  # Prevent overlapping executions
            coalesce=True     # Combine missed runs into one
        )

        # Add initial startup refresh only if no cached data was preloaded
        # If cache was preloaded from SQLite, skip the immediate refresh
        if not _loaded_from_db:
            scheduler.add_job(
                func=background_refresh,
                trigger='date',
                run_date=datetime.now() + timedelta(seconds=10),
                id='startup_refresh',
                name='Initial cache refresh on startup',
                replace_existing=True,
                max_instances=1
            )
            logger.info("No preloaded cache - scheduling startup refresh in 10s")
        else:
            logger.info("Cache preloaded from SQLite - skipping startup refresh")

        # Start the scheduler
        scheduler.start()
        _scheduler_started = True
        logger.info("APScheduler started - hourly refresh scheduled")

        # Register shutdown handler
        atexit.register(lambda: scheduler.shutdown(wait=False))

    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


# Start scheduler when module is loaded (for gunicorn)
# Only start if not in debug/reloader mode to avoid duplicate schedulers
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    init_scheduler()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    # For local development, start scheduler if not already started
    if not _scheduler_started:
        init_scheduler()

    logger.info(f"Starting SOMF Dashboard on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
