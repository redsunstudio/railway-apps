# Gmail Setup Guide for YouTube News Scraper

This guide will walk you through setting up Gmail to send your daily news digests.

## Why App Passwords?

Gmail requires "App Passwords" for third-party apps (like your scraper) to send emails. This is more secure than using your regular password.

## Prerequisites

- A Gmail account
- 2-Step Verification must be enabled

## Step-by-Step Setup

### Step 1: Enable 2-Step Verification (if not already enabled)

1. Go to https://myaccount.google.com/security
2. Scroll down to "How you sign in to Google"
3. Click on **"2-Step Verification"**
4. Follow the prompts to set it up (usually involves your phone number)
5. Once enabled, go back to the Security page

### Step 2: Generate App Password

1. Go to https://myaccount.google.com/apppasswords
   - Or: https://myaccount.google.com/security → "2-Step Verification" → scroll down → "App passwords"

2. You may need to sign in again

3. Click **"Select app"** dropdown
   - Choose **"Mail"**

4. Click **"Select device"** dropdown
   - Choose **"Other (Custom name)"**
   - Type: **"YouTube News Scraper"**

5. Click **"Generate"**

6. Google will show you a 16-character password like:
   ```
   abcd efgh ijkl mnop
   ```

7. **IMPORTANT:** Copy this password immediately!
   - You won't be able to see it again
   - Save it somewhere safe (password manager, notes)

### Step 3: Configure Your Scraper

Now you have three options depending on where you're running the app:

#### Option A: Local Testing (using .env file)

Create a `.env` file in the youtube-news-scraper folder:

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=abcdefghijklmnop
RECIPIENT_EMAIL=your-email@gmail.com
SCHEDULE_TIME=07:00
```

**Note:** Remove the spaces from the app password (make it one continuous string)

#### Option B: Railway Deployment (via Dashboard)

1. Go to https://railway.app/dashboard
2. Click on your `youtube-news-scraper` project
3. Click on **"Variables"** tab
4. Click **"New Variable"**
5. Add these one by one:

| Variable Name | Value |
|--------------|-------|
| SENDER_EMAIL | your-email@gmail.com |
| SENDER_PASSWORD | abcdefghijklmnop |
| RECIPIENT_EMAIL | your-email@gmail.com |
| SCHEDULE_TIME | 07:00 |

#### Option C: Railway Deployment (via CLI)

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper

railway variables set SENDER_EMAIL="your-email@gmail.com"
railway variables set SENDER_PASSWORD="abcdefghijklmnop"
railway variables set RECIPIENT_EMAIL="your-email@gmail.com"
railway variables set SCHEDULE_TIME="07:00"
```

### Step 4: Test It!

#### Local Test:

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper
source venv/bin/activate
python email_sender.py
```

You should receive a test email!

#### Railway Test:

```bash
# Get your Railway app URL
railway domain

# Test sending email (replace URL with yours)
curl -X POST https://your-app.railway.app/api/test-email
```

Check your inbox for the test email!

## Troubleshooting

### "Username and Password not accepted"

**Cause:** You're using your regular Gmail password instead of the App Password

**Fix:**
1. Generate a new App Password (see Step 2 above)
2. Make sure to remove all spaces from the password
3. Update your environment variables

### "2-Step Verification is not enabled"

**Cause:** You need to enable 2-Step Verification first

**Fix:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Then generate App Password

### App Password option not showing

**Causes:**
- 2-Step Verification not enabled
- Google Workspace account with admin restrictions
- Recently enabled 2-Step (wait a few minutes)

**Fix:**
1. Confirm 2-Step Verification is fully enabled
2. Wait 10-15 minutes after enabling 2-Step
3. Try this direct link: https://myaccount.google.com/apppasswords

### Still getting errors?

**Check your credentials:**

```bash
# Local testing
cat .env | grep EMAIL

# Railway
railway variables
```

**View logs:**

```bash
# Local
python app.py
# Watch for email-related errors

# Railway
railway logs
# Look for authentication errors
```

## Security Best Practices

1. **Never commit .env file to git** (already in .gitignore)
2. **Don't share your App Password** (treat it like a regular password)
3. **Revoke App Passwords you're not using:**
   - Go to https://myaccount.google.com/apppasswords
   - Delete unused passwords
4. **Use different email if concerned:**
   - Create a separate Gmail for sending
   - Your main email receives the digests

## Alternative Email Services

If you prefer not to use Gmail, you can configure other SMTP services:

### SendGrid (100 free emails/day)

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=apikey
SENDER_PASSWORD=your-sendgrid-api-key
```

### Mailgun (Free tier available)

```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SENDER_EMAIL=your-mailgun-email
SENDER_PASSWORD=your-mailgun-password
```

### Outlook/Hotmail

```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-outlook@outlook.com
SENDER_PASSWORD=your-outlook-password
```

## Quick Reference

### Gmail Settings

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=16-char-app-password
RECIPIENT_EMAIL=where-to-receive@gmail.com
```

### Test Commands

```bash
# Local test
python email_sender.py

# Railway test
curl -X POST https://your-app.railway.app/api/test-email

# Manual scrape + email
curl -X POST https://your-app.railway.app/api/run-now
```

## Need Help?

1. Check Railway logs: `railway logs`
2. Test locally first with `python email_sender.py`
3. Verify App Password has no spaces
4. Make sure 2-Step Verification is enabled
5. Try generating a new App Password

---

Once set up, you'll receive beautiful email digests every morning at 7 AM with the latest YouTube news! 📧
