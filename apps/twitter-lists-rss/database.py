"""
Database module for persistent tweet storage
Uses SQLite for simplicity and portability
"""

import sqlite3
import os
import logging
import json
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager
from threading import Lock

logger = logging.getLogger(__name__)

# Database file location
DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'tweets.db'))

# Thread-safe lock for database operations
_db_lock = Lock()


def get_db_path():
    """Get the database path, ensuring directory exists"""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return DB_PATH


@contextmanager
def get_connection():
    """Get a database connection with proper cleanup"""
    conn = sqlite3.connect(get_db_path(), timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database tables"""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Tweets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tweet_id TEXT UNIQUE NOT NULL,
                    list_id TEXT NOT NULL,
                    author_username TEXT,
                    author_name TEXT,
                    content TEXT,
                    tweet_url TEXT,
                    timestamp TEXT,
                    stats TEXT,
                    media TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Index for efficient queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tweets_list_id
                ON tweets(list_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tweets_timestamp
                ON tweets(timestamp DESC)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tweets_fetched_at
                ON tweets(fetched_at)
            ''')

            # Fetch history table (track when lists were last fetched)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fetch_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id TEXT NOT NULL,
                    fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    tweets_found INTEGER DEFAULT 0,
                    new_tweets INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'success',
                    error_message TEXT
                )
            ''')

            conn.commit()
            logger.info("Database initialized successfully")


def store_tweets(list_id, tweets):
    """
    Store tweets in the database

    Args:
        list_id: The Twitter list ID
        tweets: List of tweet dictionaries

    Returns:
        Tuple of (total_stored, new_count)
    """
    if not tweets:
        return 0, 0

    new_count = 0
    stored_count = 0

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()

            for tweet in tweets:
                tweet_id = tweet.get('id')
                if not tweet_id:
                    continue

                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO tweets
                        (tweet_id, list_id, author_username, author_name, content,
                         tweet_url, timestamp, stats, media, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        tweet_id,
                        list_id,
                        tweet.get('author', {}).get('username', ''),
                        tweet.get('author', {}).get('name', ''),
                        tweet.get('content', ''),
                        tweet.get('url', ''),
                        tweet.get('timestamp', ''),
                        json.dumps(tweet.get('stats', {})),
                        json.dumps(tweet.get('media', [])),
                        datetime.now(timezone.utc).isoformat()
                    ))

                    if cursor.rowcount > 0:
                        new_count += 1
                    stored_count += 1

                except sqlite3.Error as e:
                    logger.error(f"Error storing tweet {tweet_id}: {e}")
                    continue

            conn.commit()

    logger.info(f"Stored {stored_count} tweets for list {list_id} ({new_count} new)")
    return stored_count, new_count


def get_tweets_for_list(list_id, limit=100, days=None):
    """
    Get tweets for a specific list

    Args:
        list_id: The Twitter list ID
        limit: Maximum number of tweets to return
        days: Only return tweets from the last N days

    Returns:
        List of tweet dictionaries
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        query = '''
            SELECT * FROM tweets
            WHERE list_id = ?
        '''
        params = [list_id]

        if days:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            query += ' AND timestamp >= ?'
            params.append(cutoff)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        tweets = []
        for row in rows:
            tweets.append({
                'id': row['tweet_id'],
                'author': {
                    'username': row['author_username'],
                    'name': row['author_name']
                },
                'content': row['content'],
                'url': row['tweet_url'],
                'timestamp': row['timestamp'],
                'stats': json.loads(row['stats']) if row['stats'] else {},
                'media': json.loads(row['media']) if row['media'] else []
            })

        return tweets


def get_tweets_for_week(list_id):
    """Get all tweets from the last 7 days for a list"""
    return get_tweets_for_list(list_id, limit=500, days=7)


def get_tweet_count(list_id, days=None):
    """Get count of tweets for a list"""
    with get_connection() as conn:
        cursor = conn.cursor()

        query = 'SELECT COUNT(*) as count FROM tweets WHERE list_id = ?'
        params = [list_id]

        if days:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            query += ' AND timestamp >= ?'
            params.append(cutoff)

        cursor.execute(query, params)
        return cursor.fetchone()['count']


def cleanup_old_tweets(retention_days=30):
    """
    Remove tweets older than retention period

    Args:
        retention_days: Number of days to keep tweets

    Returns:
        Number of tweets deleted
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()

    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM tweets WHERE fetched_at < ?
            ''', (cutoff,))

            deleted = cursor.rowcount
            conn.commit()

    if deleted > 0:
        logger.info(f"Cleaned up {deleted} tweets older than {retention_days} days")

    return deleted


def record_fetch(list_id, tweets_found, new_tweets, status='success', error_message=None):
    """Record a fetch attempt in history"""
    with _db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fetch_history
                (list_id, tweets_found, new_tweets, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (list_id, tweets_found, new_tweets, status, error_message))
            conn.commit()


def get_fetch_stats(list_id):
    """Get fetch statistics for a list"""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Last fetch
        cursor.execute('''
            SELECT * FROM fetch_history
            WHERE list_id = ?
            ORDER BY fetched_at DESC LIMIT 1
        ''', (list_id,))
        last_fetch = cursor.fetchone()

        # Total tweets
        cursor.execute('''
            SELECT COUNT(*) as total FROM tweets WHERE list_id = ?
        ''', (list_id,))
        total = cursor.fetchone()['total']

        # Tweets this week
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) as weekly FROM tweets
            WHERE list_id = ? AND timestamp >= ?
        ''', (list_id, week_ago))
        weekly = cursor.fetchone()['weekly']

        return {
            'total_tweets': total,
            'weekly_tweets': weekly,
            'last_fetch': dict(last_fetch) if last_fetch else None
        }


# Initialize database on module load
init_database()
