# Quick Setup Guide - Complete Physio Weekly Summary

Get your weekly summary app running in 15 minutes!

## Prerequisites

- Gmail account for sending emails
- GitHub account (for Railway deployment)
- Railway account (free - sign up at [railway.app](https://railway.app))

## Step-by-Step Setup

### 1. Gmail API Setup (5 minutes)

You need Gmail API credentials to send emails. Use the setup script from your parent directory:

```bash
cd /Users/john/railway-apps
./setup_gmail.sh
```

This will:
1. Guide you through creating a Google Cloud project
2. Enable Gmail API
3. Create OAuth2 credentials
4. Generate `credentials.json` and `token.json`

**Keep these files safe!** You'll need them for Railway.

### 2. Configure Recipients (2 minutes)

You need to provide:
- **Sender email**: Your Gmail address (the one you set up API for)
- **Recipient emails**: Who receives the weekly summary (can be multiple)

Write them down now:
```
Sender: ___________________________
Recipients: ________________________
```

### 3. Prepare Credentials for Railway (3 minutes)

Railway needs your Gmail credentials as environment variables. We need to convert the JSON files to single-line strings:

#### Get GMAIL_CREDENTIALS_JSON:

```bash
cd /Users/john/railway-apps
cat credentials.json | tr -d '\n'
```

Copy the output (entire thing).

#### Get GMAIL_TOKEN_JSON:

```bash
cat token.json | tr -d '\n'
```

Copy the output (entire thing).

Save both somewhere temporarily - you'll paste them into Railway.

### 4. Push to GitHub (2 minutes)

```bash
cd /Users/john/railway-apps
git add apps/complete-physio-weekly-summary/
git commit -m "Add Complete Physio weekly summary app"
git push
```

### 5. Deploy to Railway (5 minutes)

#### A. Create Project

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `railway-apps` repository
5. Set root directory to: `apps/complete-physio-weekly-summary`

#### B. Add Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
# Content Sources (already configured for Complete Physio)
INSTAGRAM_USERNAME=completephysio
YOUTUBE_RSS_URL=https://www.youtube.com/feeds/videos.xml?channel_id=UCzqxBIw58_WDqxYWWwq_L8Q
BLOG_RSS_URL=https://complete-physio.co.uk/post-sitemap.xml
BLOG2_RSS_URL=https://www.ultrasound-guided-injections.co.uk/post-sitemap.xml
NEWSLETTER_RSS_URL=https://zapier.com/engine/rss/5614589/completenewsletter

# Email Configuration (CHANGE THESE!)
SENDER_EMAIL=your-email@gmail.com
RECIPIENT_EMAILS=client1@example.com,client2@example.com

# Gmail API Credentials (paste your converted JSON strings)
GMAIL_CREDENTIALS_JSON=<paste the credentials.json single-line string here>
GMAIL_TOKEN_JSON=<paste the token.json single-line string here>

# App Configuration
TEST_MODE=false
```

**Important Notes**:
- Replace `SENDER_EMAIL` with your Gmail address
- Replace `RECIPIENT_EMAILS` with actual recipient email(s) (comma-separated)
- For `GMAIL_CREDENTIALS_JSON` and `GMAIL_TOKEN_JSON`, paste the entire single-line strings you created in step 3
- Make sure `TEST_MODE=false` for production (runs on schedule)

#### C. Deploy

Click **"Deploy"** and wait for Railway to build and start your app.

### 6. Verify It's Working (2 minutes)

#### Check Logs

In Railway dashboard, go to **"Deployments"** tab and check logs. You should see:

```
Weekly Scheduler Started
Schedule: Every Friday at 3:00 PM UK time
Next run: [date/time]
Running initial job immediately for testing...
```

#### Check Your Email

The app runs once immediately on startup (for testing), so you should receive a test email within a few minutes!

---

## What Happens Next?

- App runs **24/7 on Railway**
- Sends email **every Friday at 3 PM UK time**
- Collects content from **last 7 days** across all sources
- Beautiful HTML email with **statistics and links**

## Testing

Want to test before Friday? Set `TEST_MODE=true` in Railway variables:

1. Go to Railway dashboard
2. Variables tab
3. Change `TEST_MODE=false` to `TEST_MODE=true`
4. App will run immediately and send an email
5. Change back to `TEST_MODE=false` when done

## Troubleshooting

### Not receiving emails?

1. Check Railway logs for errors
2. Verify `SENDER_EMAIL` and `RECIPIENT_EMAILS` are correct
3. Check spam/junk folder
4. Verify Gmail API token hasn't expired (regenerate if needed)

### Railway app keeps crashing?

1. Check logs for specific error
2. Verify all environment variables are set
3. Ensure `GMAIL_CREDENTIALS_JSON` and `GMAIL_TOKEN_JSON` are valid JSON (single line)
4. Try regenerating Gmail tokens

### Instagram scraping not working?

- Complete Physio's Instagram must be **public**
- If rate limited, app will retry next week
- Check logs for specific errors

### RSS feeds not working?

Test RSS URLs manually:
```bash
curl https://complete-physio.co.uk/post-sitemap.xml
```

If they return XML, they're working.

## Cost

- **Railway**: ~$2-3/month (well within $5 free tier)
- **Gmail API**: Free unlimited
- **Total**: Free!

## Need Help?

1. Check [README.md](README.md) for full documentation
2. Review Railway logs for specific errors
3. Test locally first: `TEST_MODE=true python main.py`

---

## Quick Reference

**Railway Dashboard**: [railway.app/dashboard](https://railway.app/dashboard)

**Schedule**: Every Friday at 3:00 PM UK time

**Content Sources**:
- Instagram: @completephysio
- YouTube: RSS feed
- Blog: 2 Complete Physio blogs
- Newsletter: Zapier RSS feed

**Logs Command** (if using Railway CLI):
```bash
railway logs
```

---

You're all set! Your first weekly summary will arrive this Friday at 3 PM UK time. 📊✨
