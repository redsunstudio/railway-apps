# YouTube News Scraper - Setup Guide

Follow these steps to get your YouTube news scraper running on Railway in under 10 minutes.

## Step 1: Get Gmail App Password (3 minutes)

Your scraper needs to send emails. Here's how to set up Gmail:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already enabled
3. Go back to Security settings
4. Scroll to **"App passwords"**
5. Click **"App passwords"**
6. Select **"Mail"** and your device
7. Click **Generate**
8. Copy the 16-character password (it looks like: `abcd efgh ijkl mnop`)
9. Save it somewhere safe - you'll need it in Step 3

## Step 2: Push to GitHub (if not done yet)

```bash
cd /Users/john/railway-apps

# Push to GitHub
git push origin main
```

If you haven't set up the remote yet, see the main [START_HERE.md](../../START_HERE.md) guide.

## Step 3: Deploy to Railway

### Option A: Via Railway Dashboard (Recommended)

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `railway-apps` repository
5. Railway will ask which folder to deploy - select `apps/youtube-news-scraper`
6. Click **"Deploy"**

### Option B: Via Railway CLI

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper

# Login to Railway (if not done yet)
export PATH="$HOME/.railway:$PATH"
railway login

# Initialize project
railway init

# Deploy
railway up
```

## Step 4: Set Environment Variables

In Railway Dashboard:

1. Go to your project
2. Click on **"Variables"** tab
3. Add these variables:

```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop
RECIPIENT_EMAIL=your-email@gmail.com
SCHEDULE_TIME=07:00
```

Or via CLI:

```bash
railway variables set SENDER_EMAIL=your-email@gmail.com
railway variables set SENDER_PASSWORD="your-16-char-app-password"
railway variables set RECIPIENT_EMAIL=your-email@gmail.com
railway variables set SCHEDULE_TIME=07:00
```

## Step 5: Test It!

Get your Railway app URL:
- Dashboard: Click your service → Settings → copy the domain
- CLI: `railway domain`

Then test the endpoints:

```bash
# Replace YOUR-APP-URL with your Railway URL
export APP_URL=https://your-app.railway.app

# Check if app is healthy
curl $APP_URL/health

# Test scraping (shows what articles it finds)
curl $APP_URL/api/test-scrape

# Send a test email to yourself
curl -X POST $APP_URL/api/test-email

# Manually trigger a full scrape + email
curl -X POST $APP_URL/api/run-now
```

## Done!

Your scraper is now running 24/7 on Railway. You'll receive your first automated email tomorrow at 7:00 AM with the latest YouTube news!

## Customization

### Change Email Time

```bash
railway variables set SCHEDULE_TIME=08:00
# Then restart: railway restart
```

### Add More News Sources

1. Edit [news_sources.json](news_sources.json)
2. Add your new source:
   ```json
   {
     "name": "New Source",
     "url": "https://example.com/youtube",
     "type": "html",
     "keywords": ["youtube", "creator"],
     "enabled": true
   }
   ```
3. Commit and push:
   ```bash
   git add apps/youtube-news-scraper/news_sources.json
   git commit -m "Add new news source"
   git push
   ```
4. Railway auto-deploys!

### Disable a Source

Edit [news_sources.json](news_sources.json) and set `"enabled": false` for any source, then push.

## Monitoring

View logs in real-time:
```bash
railway logs
```

Check app status:
```bash
railway status
```

## Troubleshooting

### Not receiving emails?

1. Check Railway logs: `railway logs`
2. Verify Gmail App Password is correct
3. Test manually: `curl -X POST $APP_URL/api/test-email`
4. Check spam folder

### Emails have no articles?

This is normal if there's no YouTube news in the last 24 hours. To test with any results:

1. Set `RUN_ON_STARTUP=true` in Railway variables
2. Or use: `curl -X POST $APP_URL/api/run-now`

### App keeps restarting?

Check logs for errors. Common issues:
- Missing environment variables
- Invalid Gmail credentials
- Python dependency issues

## Cost Estimate

Railway Pricing:
- **Free tier**: $5/month credit
- **This app**: ~$2-3/month (very lightweight)
- **With free tier**: Essentially free!

## Support

- Check the main [README.md](README.md) for full documentation
- View Railway logs: `railway logs`
- Railway docs: https://docs.railway.app
