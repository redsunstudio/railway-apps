"""
Twitter Lists to RSS Converter
Converts public Twitter/X lists into RSS feeds
With persistent storage and scheduled fetching
"""

from flask import Flask, jsonify, request, render_template, Response, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timezone, timedelta
import json

from scraper import TwitterListScraper
from rss_generator import RSSGenerator
from lists_manager import ListsManager
from database import (
    get_tweets_for_list, get_tweets_for_week, store_tweets,
    get_fetch_stats, get_tweet_count, init_database
)
from scheduler import start_scheduler, get_scheduler_status, trigger_fetch_now

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize database
init_database()

# Initialize managers
lists_manager = ListsManager()
scraper = TwitterListScraper()
rss_generator = RSSGenerator()

# Start background scheduler
start_scheduler()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    scheduler_status = get_scheduler_status()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'scheduler': scheduler_status
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Main page - list management UI"""
    return render_template('index.html')


@app.route('/api/lists', methods=['GET'])
def get_lists():
    """Get all configured lists"""
    try:
        lists = lists_manager.get_all_lists()
        return jsonify({
            'success': True,
            'lists': lists,
            'total': len(lists)
        }), 200
    except Exception as e:
        logger.error(f"Error getting lists: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/lists', methods=['POST'])
def add_list():
    """Add a new Twitter list"""
    try:
        data = request.get_json()
        list_url = data.get('url', '').strip()
        name = data.get('name', '').strip()

        if not list_url:
            return jsonify({
                'success': False,
                'error': 'List URL is required'
            }), 400

        # Parse and validate the list URL
        list_info = scraper.parse_list_url(list_url)
        if not list_info:
            return jsonify({
                'success': False,
                'error': 'Invalid Twitter list URL'
            }), 400

        # Use provided name or generate from URL
        if not name:
            name = f"List {list_info['list_id']}"

        # Add to manager
        new_list = lists_manager.add_list(
            list_id=list_info['list_id'],
            url=list_url,
            name=name
        )

        if new_list:
            return jsonify({
                'success': True,
                'list': new_list,
                'message': 'List added successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'List already exists'
            }), 409

    except Exception as e:
        logger.error(f"Error adding list: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/lists/<list_id>', methods=['DELETE'])
def delete_list(list_id):
    """Delete a Twitter list"""
    try:
        success = lists_manager.delete_list(list_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'List deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'List not found'
            }), 404
    except Exception as e:
        logger.error(f"Error deleting list: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/lists/<list_id>', methods=['PUT'])
def update_list(list_id):
    """Update a Twitter list"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()

        if not name:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400

        updated = lists_manager.update_list(list_id, name=name)
        if updated:
            return jsonify({
                'success': True,
                'list': updated,
                'message': 'List updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'List not found'
            }), 404
    except Exception as e:
        logger.error(f"Error updating list: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/feed/<list_id>', methods=['GET'])
def get_feed(list_id):
    """Get RSS feed for a specific list (serves from database)"""
    try:
        # Get list info
        list_info = lists_manager.get_list(list_id)
        if not list_info:
            return jsonify({
                'success': False,
                'error': 'List not found'
            }), 404

        # Get days parameter (default: 30 days)
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 500, type=int)

        # Get tweets from database
        tweets = get_tweets_for_list(list_id, limit=limit, days=days)

        # Generate RSS
        rss_content = rss_generator.generate(
            list_id=list_id,
            list_name=list_info['name'],
            list_url=list_info['url'],
            tweets=tweets
        )

        return Response(
            rss_content,
            mimetype='application/rss+xml',
            headers={
                'Content-Type': 'application/rss+xml; charset=utf-8',
                'Cache-Control': 'public, max-age=300'
            }
        )

    except Exception as e:
        logger.error(f"Error generating feed for {list_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/feed/<list_id>/preview', methods=['GET'])
def preview_feed(list_id):
    """Preview tweets from a list (JSON format)"""
    try:
        list_info = lists_manager.get_list(list_id)
        if not list_info:
            return jsonify({
                'success': False,
                'error': 'List not found'
            }), 404

        tweets = scraper.scrape_list(list_info['url'])

        return jsonify({
            'success': True,
            'list': list_info,
            'tweets': tweets,
            'count': len(tweets)
        }), 200

    except Exception as e:
        logger.error(f"Error previewing feed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/preview', methods=['POST'])
def preview_url():
    """Preview tweets from a URL before adding"""
    try:
        data = request.get_json()
        list_url = data.get('url', '').strip()

        if not list_url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        # Parse and validate
        list_info = scraper.parse_list_url(list_url)
        if not list_info:
            return jsonify({
                'success': False,
                'error': 'Invalid Twitter list URL'
            }), 400

        # Try to scrape
        tweets = scraper.scrape_list(list_url)

        return jsonify({
            'success': True,
            'list_id': list_info['list_id'],
            'tweets': tweets[:5],  # Preview first 5
            'total_count': len(tweets)
        }), 200

    except Exception as e:
        logger.error(f"Error previewing URL: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/digest/<list_id>/weekly', methods=['GET'])
def weekly_digest(list_id):
    """Get a weekly digest of tweets (last 7 days)"""
    try:
        list_info = lists_manager.get_list(list_id)
        if not list_info:
            return jsonify({
                'success': False,
                'error': 'List not found'
            }), 404

        # Get tweets from last 7 days
        tweets = get_tweets_for_week(list_id)

        # Group by day
        days = {}
        for tweet in tweets:
            ts = tweet.get('timestamp', '')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    day_key = dt.strftime('%Y-%m-%d')
                except:
                    day_key = 'unknown'
            else:
                day_key = 'unknown'

            if day_key not in days:
                days[day_key] = []
            days[day_key].append(tweet)

        # Sort days
        sorted_days = sorted(days.items(), key=lambda x: x[0], reverse=True)

        return jsonify({
            'success': True,
            'list': list_info,
            'period': {
                'start': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                'end': datetime.now(timezone.utc).isoformat()
            },
            'total_tweets': len(tweets),
            'days': [{'date': day, 'tweets': t, 'count': len(t)} for day, t in sorted_days]
        }), 200

    except Exception as e:
        logger.error(f"Error generating digest: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/digest/<list_id>/weekly.rss', methods=['GET'])
def weekly_digest_rss(list_id):
    """Get weekly digest as RSS feed"""
    try:
        list_info = lists_manager.get_list(list_id)
        if not list_info:
            return jsonify({
                'success': False,
                'error': 'List not found'
            }), 404

        tweets = get_tweets_for_week(list_id)

        rss_content = rss_generator.generate(
            list_id=list_id,
            list_name=f"{list_info['name']} (Weekly)",
            list_url=list_info['url'],
            tweets=tweets
        )

        return Response(
            rss_content,
            mimetype='application/rss+xml',
            headers={
                'Content-Type': 'application/rss+xml; charset=utf-8',
                'Cache-Control': 'public, max-age=300'
            }
        )

    except Exception as e:
        logger.error(f"Error generating weekly RSS: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/lists/<list_id>/stats', methods=['GET'])
def list_stats(list_id):
    """Get statistics for a list"""
    try:
        list_info = lists_manager.get_list(list_id)
        if not list_info:
            return jsonify({
                'success': False,
                'error': 'List not found'
            }), 404

        stats = get_fetch_stats(list_id)

        return jsonify({
            'success': True,
            'list': list_info,
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fetch', methods=['POST'])
def trigger_fetch():
    """Manually trigger a fetch of all lists"""
    try:
        trigger_fetch_now()
        return jsonify({
            'success': True,
            'message': 'Fetch triggered successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error triggering fetch: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scheduler', methods=['GET'])
def scheduler_status():
    """Get scheduler status"""
    try:
        status = get_scheduler_status()
        return jsonify({
            'success': True,
            'scheduler': status
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    logger.info(f"Starting Twitter Lists RSS on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
