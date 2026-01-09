from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Welcome to your Railway Python API!',
        'endpoints': {
            'health': '/health',
            'api': '/api'
        }
    }), 200

# Example API endpoint
@app.route('/api', methods=['GET'])
def api():
    return jsonify({
        'message': 'API is working!',
        'environment': os.getenv('FLASK_ENV', 'production')
    }), 200

# Example POST endpoint
@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({
        'received': data,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# 404 handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404

# 500 handler
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
