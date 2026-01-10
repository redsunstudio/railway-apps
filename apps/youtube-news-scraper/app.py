from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime
import threading
import logging
import json

from scheduler import NewsScheduler
from scraper import YouTubeNewsScraper
from email_sender import EmailSender

# Try to import Gmail API sender (optional)
try:
    from gmail_api_sender import GmailAPISender
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    logger.warning("Gmail API not available, falling back to SMTP")

load_dotenv()

# Determine which email sender to use
def get_email_sender():
    """Get appropriate email sender based on available credentials"""
    # Check if Gmail API credentials are available
    if GMAIL_API_AVAILABLE and os.getenv('GMAIL_CREDENTIALS_JSON') and os.getenv('GMAIL_TOKEN_JSON'):
        logger.info("Using Gmail API for email sending")
        return GmailAPISender()
    else:
        logger.info("Using SMTP for email sending")
        return EmailSender()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global scheduler instance
scheduler = None
scheduler_thread = None


def start_scheduler_in_background():
    """Start the scheduler in a background thread"""
    global scheduler
    try:
        scheduler = NewsScheduler()
        scheduler.start()
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")


# Start scheduler immediately when module loads (for Gunicorn)
scheduler_thread = threading.Thread(target=start_scheduler_in_background, daemon=True)
scheduler_thread.start()
logger.info("🚀 Started background scheduler thread")


# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'scheduler_running': scheduler is not None,
        'dashboard_enabled': True,
        'version': '1.1.0'
    }), 200


# Root endpoint - serve dashboard
@app.route('/', methods=['GET'])
def root():
    # Check if request accepts HTML (browser) or JSON (API client)
    if 'text/html' in request.headers.get('Accept', ''):
        return render_template('dashboard.html')
    else:
        return jsonify({
            'message': 'YouTube News Scraper API',
            'version': '1.1.0',
            'endpoints': {
                'dashboard': '/',
                'health': '/health',
                'test_scrape': '/api/test-scrape',
                'test_email': '/api/test-email',
                'manual_run': '/api/run-now',
                'sources': '/api/sources',
                'update_sources': '/api/update-sources'
            }
        }), 200


# Dashboard endpoint
@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')


# Test scraping endpoint
@app.route('/api/test-scrape', methods=['GET'])
def test_scrape():
    """Test the scraper without sending email"""
    try:
        scraper = YouTubeNewsScraper()
        articles = scraper.scrape_all()
        articles_dict = [article.to_dict() for article in articles]

        return jsonify({
            'success': True,
            'articles_found': len(articles_dict),
            'articles': articles_dict
        }), 200
    except Exception as e:
        logger.error(f"Error testing scraper: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Test email endpoint
@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email sending with sample data"""
    try:
        data = request.get_json()
        articles = data.get('articles', [])

        if not articles:
            # Use sample data if none provided
            articles = [
                {
                    'title': 'Test Article: YouTube Announces New Feature',
                    'url': 'https://example.com/test',
                    'source': 'Test Source',
                    'published_date': datetime.now().strftime('%B %d, %Y'),
                    'summary': 'This is a test email from your YouTube News Scraper.'
                }
            ]

        email_sender = get_email_sender()
        success = email_sender.send_digest(articles)

        return jsonify({
            'success': success,
            'message': 'Test email sent' if success else 'Failed to send email'
        }), 200 if success else 500

    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Manual run endpoint
@app.route('/api/run-now', methods=['POST'])
def run_now():
    """Manually trigger a scrape and email"""
    try:
        scraper = YouTubeNewsScraper()
        articles = scraper.scrape_all()
        articles_dict = [article.to_dict() for article in articles]

        email_sender = get_email_sender()
        success = email_sender.send_digest(articles_dict)

        return jsonify({
            'success': success,
            'articles_found': len(articles_dict),
            'message': 'Digest sent successfully' if success else 'Failed to send digest'
        }), 200 if success else 500

    except Exception as e:
        logger.error(f"Error in manual run: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Get sources endpoint
@app.route('/api/sources', methods=['GET'])
def get_sources():
    """Get list of configured news sources"""
    try:
        scraper = YouTubeNewsScraper()
        sources = scraper.config['sources']

        return jsonify({
            'success': True,
            'sources': sources,
            'total': len(sources),
            'enabled': len([s for s in sources if s.get('enabled', True)])
        }), 200
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Update sources endpoint
@app.route('/api/update-sources', methods=['POST'])
def update_sources():
    """Update news sources configuration"""
    try:
        data = request.get_json()
        new_sources = data.get('sources', [])

        if not new_sources:
            return jsonify({
                'success': False,
                'error': 'No sources provided'
            }), 400

        # Read current config
        config_path = os.path.join(os.path.dirname(__file__), 'news_sources.json')
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Update sources
        config['sources'] = new_sources

        # Write back to file
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info("Sources configuration updated successfully")

        return jsonify({
            'success': True,
            'message': 'Sources updated successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error updating sources: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 404 handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404


# 500 handler
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=start_scheduler_in_background, daemon=True)
    scheduler_thread.start()
    logger.info("🚀 Started background scheduler thread")

    # Start Flask app
    port = int(os.getenv('PORT', 3000))
    logger.info(f"🌐 Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
