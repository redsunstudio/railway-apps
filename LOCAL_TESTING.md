# Local Testing Guide

> **Golden Rule**: Always test locally before deploying to Railway!

---

## Why Test Locally?

- Catch errors before they break production
- Faster feedback (no waiting for deployment)
- Saves Railway credits
- Easier to debug

---

## Prerequisites

### For Python Apps
```bash
# Check Python is installed
python --version  # Should be 3.8+

# Install pip if needed
python -m ensurepip --upgrade
```

### For Node.js Apps
```bash
# Check Node is installed
node --version  # Should be 18+

# Check npm is installed
npm --version
```

---

## Testing Python Apps (Flask)

### 1. Set Up Environment

```bash
# Navigate to the app
cd apps/youtube-news-scraper  # or your app folder

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your test values
nano .env  # or use any editor
```

**Example .env file:**
```
SENDER_EMAIL=your-test-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com
SCHEDULE_TIME=07:00
PORT=5000
```

### 3. Run the App

```bash
# Run Flask directly
python app.py

# Or run with Gunicorn (like production)
gunicorn app:app --bind 0.0.0.0:5000
```

### 4. Test the Endpoints

Open another terminal:
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test status endpoint
curl http://localhost:5000/status

# Test manual scrape (if available)
curl http://localhost:5000/scrape

# Or just open in browser
open http://localhost:5000
```

### 5. Stop the App
Press `Ctrl+C` in the terminal running the app.

---

## Testing Node.js Apps

### 1. Set Up Environment

```bash
# Navigate to the app
cd apps/starter-app  # or your app folder

# Install dependencies
npm install
```

### 2. Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your test values
nano .env
```

### 3. Run the App

```bash
# Run normally
npm start

# Or run with auto-reload (development)
npm run dev
```

### 4. Test the Endpoints

```bash
# Test health endpoint
curl http://localhost:3000/health

# Test API
curl http://localhost:3000/api

# Or open in browser
open http://localhost:3000
```

---

## Testing Specific Features

### Testing Email Sending

**Option 1: Test Mode (No Real Email)**
```bash
# Set test mode in .env
TEST_MODE=true

# Run the app - emails will be logged, not sent
python app.py
```

**Option 2: Send to Yourself**
```bash
# Set yourself as recipient in .env
RECIPIENT_EMAIL=your-own-email@gmail.com

# Trigger manual email
curl http://localhost:5000/test-email
```

### Testing the Scraper

```bash
# Run scraper directly
python scraper.py

# Or use the API endpoint
curl http://localhost:5000/scrape
```

### Testing Scheduled Tasks

```bash
# Don't wait for schedule - trigger manually
curl http://localhost:5000/trigger

# Or modify schedule for testing
# In .env:
SCHEDULE_TIME=NOW  # Some apps support this
```

---

## Quick Test Commands

### Python (One-Liner)
```bash
cd apps/youtube-news-scraper && source venv/bin/activate && python app.py
```

### Node.js (One-Liner)
```bash
cd apps/starter-app && npm install && npm start
```

### Test All Endpoints
```bash
# Create a test script
cat > test_endpoints.sh << 'EOF'
#!/bin/bash
BASE_URL="http://localhost:5000"

echo "Testing health..."
curl -s "$BASE_URL/health" | head -c 100
echo ""

echo "Testing status..."
curl -s "$BASE_URL/status" | head -c 200
echo ""

echo "Testing root..."
curl -s "$BASE_URL/" | head -c 100
echo ""
EOF

chmod +x test_endpoints.sh
./test_endpoints.sh
```

---

## Common Test Scenarios

### Scenario 1: "I changed the email template"

```bash
# 1. Start the app
python app.py

# 2. Trigger test email
curl http://localhost:5000/test-email

# 3. Check your inbox
# 4. Make adjustments, repeat
```

### Scenario 2: "I added a new news source"

```bash
# 1. Edit news_sources.json
# 2. Run scraper directly
python scraper.py

# 3. Check output for your new source
# 4. If working, test full flow
python app.py
```

### Scenario 3: "I added a new API endpoint"

```bash
# 1. Start the app
python app.py

# 2. Test your new endpoint
curl http://localhost:5000/your-new-endpoint

# 3. Check response and logs
```

### Scenario 4: "I'm not sure if my code works"

```bash
# 1. Test the specific file
python -c "from scraper import scrape_all; print(scrape_all())"

# 2. Or use Python interactive mode
python
>>> from scraper import scrape_all
>>> results = scrape_all()
>>> print(results)
>>> exit()
```

---

## Debugging Tips

### View All Logs
```bash
# Run with debug mode
FLASK_DEBUG=1 python app.py

# Or for more verbose output
python app.py 2>&1 | tee debug.log
```

### Check for Syntax Errors
```bash
# Python syntax check
python -m py_compile app.py

# If no output, syntax is OK!
```

### Check Dependencies
```bash
# List installed packages
pip list

# Check if package is installed
pip show flask

# Install missing package
pip install package-name
```

### Port Already in Use?
```bash
# Find what's using the port
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=5001 python app.py
```

---

## Testing Checklist

Before pushing to production:

- [ ] App starts without errors
- [ ] Health endpoint returns 200
- [ ] Main functionality works (scraping, emails, etc.)
- [ ] No sensitive data in logs
- [ ] Environment variables are not hardcoded
- [ ] Error handling works (try wrong inputs)

---

## Test vs Production Environment Variables

| Variable | Local (.env) | Production (Railway) |
|----------|--------------|----------------------|
| `PORT` | `5000` | Set by Railway |
| `DEBUG` | `true` | `false` |
| `TEST_MODE` | `true` | `false` |
| `SENDER_EMAIL` | Your test email | Production email |
| `RECIPIENT_EMAIL` | Your email | Real recipients |

---

## Quick Reference

```bash
# Start Python app
cd apps/your-app && python app.py

# Start Node app
cd apps/your-app && npm start

# Test health
curl http://localhost:5000/health

# View logs
tail -f app.log

# Stop app
Ctrl+C
```

---

*Test early, test often! It's much easier to fix bugs locally than in production.*
