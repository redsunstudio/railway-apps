# Quick Start - Get Running in 5 Minutes

Since this is for your personal use, here's the fastest way to get your YouTube news scraper running.

## Step 1: Get Gmail App Password (2 minutes)

1. Open: https://myaccount.google.com/apppasswords
2. Select **Mail** → **Other (Custom)** → Type "YouTube Scraper"
3. Click **Generate**
4. Copy the 16-character password (remove spaces)

## Step 2: Run Setup Script (1 minute)

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper
./setup_gmail.sh
```

Enter your details when prompted:
- Gmail address
- App password (from Step 1)
- Email to receive digests (probably same Gmail)
- Time to receive emails (default: 07:00)

The script will test your configuration immediately!

## Step 3: Deploy to Railway (2 minutes)

```bash
# Deploy the app
railway init
railway up

# Set the same credentials in Railway
railway variables set SENDER_EMAIL="your-email@gmail.com"
railway variables set SENDER_PASSWORD="your-app-password"
railway variables set RECIPIENT_EMAIL="your-email@gmail.com"
railway variables set SCHEDULE_TIME="07:00"

# Get your app URL
railway domain
```

## Step 4: Test It

```bash
# Manual trigger to test immediately
curl -X POST https://your-app.railway.app/api/run-now
```

Check your email - you should have a digest!

## Done!

Starting tomorrow, you'll get a daily email at 7 AM with:
- Latest YouTube feature announcements
- APK teardown discoveries
- Beta feature tests
- Creator-related news

## Adding More Sources Later

Just edit `news_sources.json` and push:

```bash
# Edit the file to add new sources
# Then:
git add apps/youtube-news-scraper/news_sources.json
git commit -m "Add new news source"
git push

# Railway auto-deploys!
```

## Useful Commands

```bash
# View logs
railway logs

# Test scraper without sending email
curl https://your-app.railway.app/api/test-scrape

# Send test email
curl -X POST https://your-app.railway.app/api/test-email

# Manual run (scrape + email)
curl -X POST https://your-app.railway.app/api/run-now
```

That's it! Your personal YouTube news monitoring system is now running 24/7 in the cloud.
