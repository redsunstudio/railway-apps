# Railway Email Issue & Solutions

## The Problem

Railway blocks outbound SMTP connections on both ports 587 (TLS) and 465 (SSL) for security reasons. This prevents direct Gmail SMTP from working.

**Error:** `[Errno 101] Network is unreachable`

## ✅ Your App Status

**Everything else works perfectly:**
- Scraper is working (found 9 articles from YouTube sources)
- Web API is running at https://cheerful-serenity-production-3e99.up.railway.app
- Rate limiting is working
- All code is deployed and ready

**Only issue:** Email sending is blocked by Railway's network policy.

## Solutions

### Option 1: Use SendGrid (Recommended - Free & Works on Railway)

SendGrid has a free tier (100 emails/day) and works perfectly with Railway.

**Setup:**
1. Sign up at https://sendgrid.com (free tier)
2. Create an API key:
   - Settings → API Keys → Create API Key
   - Choose "Full Access" or "Mail Send"
   - Copy the key

3. Update Railway variables:
```bash
railway variables --set "SMTP_SERVER=smtp.sendgrid.net"
railway variables --set "SMTP_PORT=587"
railway variables --set "SENDER_EMAIL=apikey"
railway variables --set "SENDER_PASSWORD=YOUR_SENDGRID_API_KEY"
railway variables --set "SENDER_NAME=YouTube News Scraper"
```

4. Redeploy:
```bash
railway up
```

**Pros:**
- Free (100 emails/day)
- Works perfectly with Railway
- Reliable delivery
- Good reputation

**Cons:**
- Need to create another account

### Option 2: Test Locally (Works Now!)

Your Gmail setup will work perfectly when running locally.

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper

# Set up Gmail (if not done yet)
./setup_gmail.sh

# Run the app locally
python app.py
```

Then test:
```bash
# Send test email
curl -X POST -H "Content-Type: application/json" -d '{}' http://localhost:3000/api/test-email

# Or trigger full scrape + email
curl -X POST -H "Content-Type: application/json" -d '{}' http://localhost:3000/api/run-now
```

**This will work because your local machine isn't blocking SMTP ports!**

**To run daily:**
- Keep your computer on
- App runs locally and sends emails via Gmail
- Railway hosts the web interface

### Option 3: Use Resend (Modern Alternative)

Resend is a modern email API that works great with Railway.

1. Sign up at https://resend.com (free tier: 100 emails/day)
2. Get API key
3. Install resend:
   - Add `resend==0.7.0` to requirements.txt
   - Update email_sender.py to use Resend API instead of SMTP

### Option 4: Run on Different Platform

These platforms allow SMTP:
- **DigitalOcean App Platform** - SMTP allowed
- **Fly.io** - SMTP allowed
- **Your own VPS** (Linode, DigitalOcean Droplet) - Full control

## Recommended Approach

**For now:**
1. Run locally to test and verify everything works with Gmail
2. Get your daily emails working on your local machine

**For production (choose one):**
1. **SendGrid** (easiest, free, 5 minutes setup)
2. **Resend** (modern, developer-friendly)
3. Keep running locally (simplest if computer is always on)

## Testing Right Now

Want to see it work immediately? Run locally:

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper

# Set environment variables
export SENDER_EMAIL="hello@johnisaacson.co.uk"
export SENDER_PASSWORD="lttdkhfvqprqivil"
export RECIPIENT_EMAIL="hello@johnisaacson.co.uk"
export SCHEDULE_TIME="07:00"

# Run it
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then in another terminal:
```bash
curl -X POST -H "Content-Type: application/json" -d '{}' http://localhost:3000/api/run-now
```

**Check your email** - you should have a beautiful YouTube news digest! 📧

## Next Steps

What would you like to do?
1. Set up SendGrid (I can help)?
2. Test locally first to see it working?
3. Try a different hosting platform?

The scraper itself is perfect - we just need to pick an email solution that works with Railway's network restrictions.
