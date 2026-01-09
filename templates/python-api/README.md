# Python Flask API Template for Railway

A production-ready Flask API template configured for Railway deployment.

## Features

- Flask web framework
- CORS enabled
- Environment variable support
- Health check endpoint
- Error handling
- JSON request/response
- Gunicorn production server

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run development server
python app.py
```

The API will be available at `http://localhost:3000`

### Deploy to Railway

#### Option 1: Via Dashboard
1. Push this folder to GitHub
2. Go to railway.app/dashboard
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Done! Railway auto-detects Python and deploys

#### Option 2: Via CLI
```bash
railway init
railway up
```

## Endpoints

- `GET /` - Welcome message with API info
- `GET /health` - Health check endpoint
- `GET /api` - Example API endpoint
- `POST /api/echo` - Echo back the request body

## Environment Variables

Railway automatically provides:
- `PORT` - The port your app should listen on

Add your own in Railway dashboard or via CLI:
```bash
railway variables set API_KEY=your-secret-key
```

## Production Server

This template uses Gunicorn as the production WSGI server (configured in Procfile).

## Adding a Database

### PostgreSQL with SQLAlchemy
```bash
# Add to requirements.txt
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23

# Add database via Railway CLI
railway add postgresql

# Use in your code
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
```

## Testing

```bash
# Test health endpoint
curl http://localhost:3000/health

# Test API endpoint
curl http://localhost:3000/api

# Test POST endpoint
curl -X POST http://localhost:3000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## Troubleshooting

**App won't start on Railway:**
- Check logs: `railway logs`
- Ensure Procfile exists and is correct
- Verify all dependencies in requirements.txt

**Import errors:**
- Ensure all packages are in requirements.txt
- Run `pip freeze > requirements.txt` to capture all deps
