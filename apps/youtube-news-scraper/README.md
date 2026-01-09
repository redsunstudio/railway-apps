# YouTube News Scraper

Automated daily news scraper that monitors YouTube-related news sources and sends email digests every morning at 7 AM.

## Features

- Scrapes 9 news sources for YouTube updates, features, and announcements
- Monitors APK teardowns and beta feature reports
- Sends beautiful HTML email digests daily
- Easy to add new sources via JSON configuration
- Manual trigger via API endpoints
- Runs 24/7 on Railway
- Built-in rate limiting and retry logic to avoid being blocked
- Randomized delays between requests to appear more human-like
- Automatic handling of 429 (Too Many Requests) responses

## News Sources Monitored

1. **YouTube Official Blog** - Official announcements
2. **Android Authority** - APK Teardowns
3. **9to5Google** - YouTube Teardowns
4. **Android Police** - YouTube Coverage
5. **XDA Developers** - APK Teardowns
6. **TestingCatalog** - Beta & Experiment Tracking
7. **TechCrunch** - YouTube News
8. **The Verge** - YouTube Coverage
9. **Social Media Today** - Creator Economy News

## Quick Start

### 1. Set Up Gmail App Password

**Quick Setup (Recommended):**
```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper
./setup_gmail.sh
```

The script will guide you through getting your Gmail App Password and test the configuration.

**Manual Setup:**
See [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed step-by-step instructions.

**Quick Summary:**
1. Enable 2-Step Verification in your Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Copy the 16-character password (remove spaces)

### 2. Configure Environment Variables

Create a `.env` file or set these in Railway:

```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=your-email@gmail.com
SCHEDULE_TIME=07:00
```

### 3. Local Testing

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Test the scraper
python scraper.py

# Test email sending
python email_sender.py

# Run the full app
python app.py
```

### 4. Deploy to Railway

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper

# Initialize Railway project
railway init

# Set environment variables in Railway
railway variables set SENDER_EMAIL=your-email@gmail.com
railway variables set SENDER_PASSWORD=your-app-password
railway variables set RECIPIENT_EMAIL=your-email@gmail.com
railway variables set SCHEDULE_TIME=07:00

# Deploy
railway up
```

## API Endpoints

Once deployed, your app exposes these endpoints:

### GET /health
Health check endpoint
```bash
curl https://your-app.railway.app/health
```

### GET /api/test-scrape
Test scraping without sending email
```bash
curl https://your-app.railway.app/api/test-scrape
```

### POST /api/test-email
Send a test email
```bash
curl -X POST https://your-app.railway.app/api/test-email
```

### POST /api/run-now
Manually trigger a scrape and email
```bash
curl -X POST https://your-app.railway.app/api/run-now
```

### GET /api/sources
View configured news sources
```bash
curl https://your-app.railway.app/api/sources
```

## Adding New Sources

Edit `news_sources.json` and add a new source:

```json
{
  "name": "Your News Source",
  "url": "https://example.com/youtube-news",
  "type": "html",
  "keywords": ["youtube", "feature", "update"],
  "enabled": true
}
```

Then redeploy:
```bash
railway up
```

## Configuration

### Email Settings

- `SENDER_EMAIL` - Your Gmail address
- `SENDER_PASSWORD` - Gmail app password (NOT your regular password)
- `RECIPIENT_EMAIL` - Where to send digests (can be same as sender)
- `SMTP_SERVER` - Default: smtp.gmail.com
- `SMTP_PORT` - Default: 587

### Scheduler Settings

- `SCHEDULE_TIME` - Time to send daily digest (24-hour format, e.g., "07:00")
- `RUN_ON_STARTUP` - Set to "true" to test immediately on startup

### Scraping Settings

Edit `news_sources.json`:
- `max_articles_per_source` - Max articles per source (default: 5)
- `article_age_days` - Only include articles from last N days (default: 1)
- `request_timeout` - Timeout for web requests in seconds (default: 10)
- `min_delay_seconds` - Minimum delay between requests to same domain (default: 2)
- `max_delay_seconds` - Maximum delay between requests to same domain (default: 5)
- `max_retries` - Number of retry attempts for failed requests (default: 3)
- `retry_delay_seconds` - Delay before retrying failed requests (default: 5)

## Troubleshooting

### Email not sending?

1. Verify Gmail App Password is correct (not your regular password)
2. Check that 2-Step Verification is enabled in Google Account
3. Test with the `/api/test-email` endpoint
4. Check Railway logs: `railway logs`

### Not finding articles?

1. Test scraper directly: `python scraper.py`
2. Some sources may have changed their HTML structure
3. Check Railway logs for errors
4. Try the `/api/test-scrape` endpoint to see what's being found

### Scheduler not running?

1. Check Railway logs to ensure app is running
2. Verify `SCHEDULE_TIME` is in 24-hour format (e.g., "07:00" not "7:00 AM")
3. Set `RUN_ON_STARTUP=true` to test immediately

## File Structure

```
youtube-news-scraper/
├── app.py                  # Main Flask app with API endpoints
├── scraper.py              # Web scraping logic
├── email_sender.py         # Email generation and sending
├── scheduler.py            # Daily scheduling logic
├── news_sources.json       # Source configuration (easy to edit!)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
└── README.md              # This file
```

## How It Works

1. **Scheduler** runs in background thread, checks every minute
2. At **7:00 AM** (configurable), triggers scraping job
3. **Scraper** visits all enabled sources in `news_sources.json`
4. Extracts articles matching keywords from last 24 hours
5. **Email Sender** creates beautiful HTML digest
6. Sends email via Gmail SMTP
7. Process repeats daily

## Support

Check Railway logs for debugging:
```bash
railway logs
```

View app status:
```bash
railway status
```

Stop the app:
```bash
railway down
```

## License

MIT
