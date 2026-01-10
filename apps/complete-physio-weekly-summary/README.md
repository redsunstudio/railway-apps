# Complete Physio Weekly Summary

Automated weekly summary emails for Complete Physio's content across Instagram, YouTube, Blog, and Newsletter.

## Features

- **Instagram**: Web scraping of recent posts with captions, likes, and images
- **YouTube**: RSS feed parsing for new videos
- **Blog Posts**: RSS feed parsing from two Complete Physio blogs
- **Newsletter**: RSS feed parsing of newsletter editions
- **Automated Scheduling**: Runs every Friday at 3:00 PM UK time
- **Beautiful Emails**: HTML formatted with statistics, images, and links
- **Multiple Recipients**: Send to team or multiple stakeholders
- **Railway Hosting**: Runs 24/7 in the cloud

## Setup Guide

### Step 1: Gmail API Setup

You'll need Gmail API credentials to send emails. Follow the existing guide in your `railway-apps` folder:

```bash
# From the railway-apps directory
cat GMAIL_API_SETUP.md
```

Or run the setup script:

```bash
cd /Users/john/railway-apps
./setup_gmail.sh
```

This will generate:
- `credentials.json` - Gmail API credentials
- `token.json` - OAuth2 access token

### Step 2: Configure Environment Variables

1. Copy the example environment file:

```bash
cd apps/complete-physio-weekly-summary
cp .env.example .env
```

2. Edit `.env` and fill in your values:

```bash
# Content sources (already configured for Complete Physio)
INSTAGRAM_USERNAME=completephysio
YOUTUBE_RSS_URL=https://www.youtube.com/feeds/videos.xml?channel_id=UCzqxBIw58_WDqxYWWwq_L8Q
BLOG_RSS_URL=https://complete-physio.co.uk/post-sitemap.xml
BLOG2_RSS_URL=https://www.ultrasound-guided-injections.co.uk/post-sitemap.xml
NEWSLETTER_RSS_URL=https://zapier.com/engine/rss/5614589/completenewsletter

# Email configuration
SENDER_EMAIL=your-email@gmail.com
RECIPIENT_EMAILS=client1@example.com,client2@example.com

# Gmail API credentials (copy from credentials.json and token.json)
GMAIL_CREDENTIALS_JSON={"installed":{...}}
GMAIL_TOKEN_JSON={"token":"...","refresh_token":"..."}
```

**Important**: For `GMAIL_CREDENTIALS_JSON` and `GMAIL_TOKEN_JSON`, you need to:
- Open `credentials.json` and copy the entire contents as a single line
- Open `token.json` and copy the entire contents as a single line
- Paste them into the `.env` file

### Step 3: Test Locally

1. Install dependencies:

```bash
cd apps/complete-physio-weekly-summary
pip install -r requirements.txt
```

2. Test individual modules:

```bash
# Test Instagram scraper
python instagram_scraper.py

# Test RSS parser
python rss_parser.py

# Test email formatter
python email_formatter.py
```

3. Run a test summary (sends email immediately):

```bash
# Set test mode to run immediately
export TEST_MODE=true
python main.py
```

### Step 4: Deploy to Railway

#### Option A: Via Railway Dashboard (Recommended)

1. Push this app to GitHub:

```bash
cd /Users/john/railway-apps
git add apps/complete-physio-weekly-summary/
git commit -m "Add Complete Physio weekly summary app"
git push
```

2. Go to [Railway Dashboard](https://railway.app/dashboard)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `railway-apps` repository
5. Choose the `apps/complete-physio-weekly-summary` directory
6. Add environment variables in Railway dashboard (same as your `.env` file)
7. Deploy!

#### Option B: Via Railway CLI

```bash
cd apps/complete-physio-weekly-summary

# Login to Railway
railway login

# Create new project
railway init

# Add environment variables
railway variables set SENDER_EMAIL="your-email@gmail.com"
railway variables set RECIPIENT_EMAILS="client1@example.com,client2@example.com"
railway variables set INSTAGRAM_USERNAME="completephysio"
# ... (add all other variables)

# Deploy
railway up
```

### Step 5: Configure Environment Variables in Railway

In Railway dashboard, add all environment variables from your `.env` file:

```
INSTAGRAM_USERNAME=completephysio
YOUTUBE_RSS_URL=https://www.youtube.com/feeds/videos.xml?channel_id=UCzqxBIw58_WDqxYWWwq_L8Q
BLOG_RSS_URL=https://complete-physio.co.uk/post-sitemap.xml
BLOG2_RSS_URL=https://www.ultrasound-guided-injections.co.uk/post-sitemap.xml
NEWSLETTER_RSS_URL=https://zapier.com/engine/rss/5614589/completenewsletter
SENDER_EMAIL=your-email@gmail.com
RECIPIENT_EMAILS=client1@example.com,client2@example.com
GMAIL_CREDENTIALS_JSON={...}
GMAIL_TOKEN_JSON={...}
TEST_MODE=false
```

## How It Works

1. **Scheduler starts** when deployed to Railway
2. **Runs every Friday at 3 PM UK time**
3. **Collects content** from all 4 sources (last 7 days)
4. **Formats beautiful HTML email** with statistics and links
5. **Sends to all recipients** via Gmail API
6. **Logs everything** for monitoring

## Email Format

The weekly summary email includes:

- **Header**: Date range and summary statistics
- **Instagram Section**: Posts with captions, likes, and images
- **YouTube Section**: Video titles with thumbnails and links
- **Blog Section**: Posts from both blogs with descriptions
- **Newsletter Section**: Newsletter editions with links
- **Footer**: Timestamp and automation info

## Customization

### Change Schedule

Edit [scheduler.py](scheduler.py:25):

```python
# Change from Friday 3 PM to Monday 9 AM
schedule.every().monday.at("09:00").do(self.job)
```

### Change Lookback Period

Edit [main.py](main.py:47) to change from 7 days:

```python
instagram_posts = self.instagram_scraper.get_recent_posts(
    self.instagram_username, days=14  # Changed from 7 to 14
)
```

### Customize Email Design

Edit [email_formatter.py](email_formatter.py) to change:
- Colors (search for `#0066cc`)
- Layout and styling
- Section order
- Content truncation

## Monitoring

View logs in Railway dashboard:

```bash
# Or via CLI
railway logs
```

Logs show:
- Content collection progress
- Number of items found per source
- Email sending status
- Next scheduled run time

## Troubleshooting

### Instagram Scraping Issues

Instagram may block requests if:
- Account is private
- Rate limiting occurs
- Network restrictions

**Solutions**:
- Ensure account is public
- Add delays between requests
- Use Railway's IP address (already handled)

### RSS Feed Not Working

**Check**:
- RSS URL is accessible
- Feed format is valid
- Network connectivity

**Test**:
```bash
curl -I https://complete-physio.co.uk/post-sitemap.xml
```

### Gmail API Errors

**Common issues**:
- Token expired: Regenerate using `./setup_gmail.sh`
- Wrong credentials: Check `GMAIL_CREDENTIALS_JSON`
- Permissions: Ensure Gmail API is enabled

### No Emails Sent

**Check**:
1. Railway app is running (not sleeping)
2. Environment variables are set correctly
3. Test mode is `false` for production
4. Check Railway logs for errors

## Testing

### Test Individual Components

```bash
# Test Instagram
python instagram_scraper.py

# Test RSS
python rss_parser.py

# Test Email Formatter
python email_formatter.py

# Test Email Sender (sends real email!)
python email_sender.py
```

### Test Full Flow

```bash
# Run once immediately
TEST_MODE=true python main.py
```

### Test on Railway

Set `TEST_MODE=true` in Railway environment variables, then check logs.

## Cost

**Railway Hosting**:
- Free tier: $5/month credit
- Estimated usage: ~$2-3/month (runs once per week)
- Well within free tier limits

**Gmail API**:
- Free (unlimited sends)

## Support

For issues:
1. Check Railway logs
2. Test locally first
3. Verify all environment variables
4. Check Gmail API credentials
5. Review [troubleshooting section](#troubleshooting)

## File Structure

```
complete-physio-weekly-summary/
├── main.py                  # Main application entry point
├── instagram_scraper.py     # Instagram web scraping
├── rss_parser.py           # RSS feed parser
├── email_formatter.py      # Email template generator
├── email_sender.py         # Gmail API email sender
├── scheduler.py            # Weekly scheduling
├── requirements.txt        # Python dependencies
├── Procfile               # Railway process configuration
├── railway.json           # Railway deployment config
├── runtime.txt            # Python version
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Updates

To update the app after making changes:

```bash
# Commit changes
git add .
git commit -m "Update weekly summary app"
git push

# Railway auto-deploys from GitHub
```

---

**Created**: January 2026
**Author**: Claude Code
**Purpose**: Automated weekly content summary for Complete Physio
