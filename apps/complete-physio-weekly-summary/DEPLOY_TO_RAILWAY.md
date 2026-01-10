# Deploy Complete Physio Weekly Summary to Railway

## Quick Deploy Guide (15 minutes)

Your app is ready to deploy! Follow these steps to get it running 24/7 on Railway.

---

## Step 1: Push to GitHub (3 minutes)

```bash
cd /Users/john/railway-apps

# Add all files
git add .

# Commit
git commit -m "Add Complete Physio weekly summary app"

# Push to GitHub
git push
```

If you don't have a GitHub repository yet:

```bash
# Create new repo at https://github.com/new
# Name it: railway-apps
# Don't initialize with README

# Then:
git remote add origin https://github.com/YOUR_USERNAME/railway-apps.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create Railway Project (2 minutes)

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `railway-apps` repository
5. Railway will ask for the root directory - enter: `apps/complete-physio-weekly-summary`
6. Click **"Deploy"**

---

## Step 3: Set Up Gmail API (5 minutes)

### Get Gmail Credentials

You need to convert your Gmail credentials to single-line JSON strings for Railway.

**From your terminal:**

```bash
cd /Users/john/railway-apps

# Get GMAIL_CREDENTIALS_JSON
cat credentials.json | tr -d '\n'
# Copy the entire output

# Get GMAIL_TOKEN_JSON
python3 -c "
import pickle
import json
with open('token.pickle', 'rb') as f:
    t = pickle.load(f)
    print(json.dumps({
        'token': t.token,
        'refresh_token': t.refresh_token,
        'token_uri': t.token_uri,
        'client_id': t.client_id,
        'client_secret': t.client_secret,
        'scopes': t.scopes
    }))
"
# Copy this output too
```

Keep these somewhere safe - you'll paste them into Railway in the next step.

---

## Step 4: Add Environment Variables in Railway (5 minutes)

In Railway dashboard, go to your project → **Variables** tab.

Add these environment variables (click "New Variable" for each):

### Content Sources (Already Configured)
```bash
INSTAGRAM_USERNAME=completephysio
YOUTUBE_RSS_URL=https://www.youtube.com/feeds/videos.xml?channel_id=UCzqxBIw58_WDqxYWWwq_L8Q
BLOG_RSS_URL=https://complete-physio.co.uk/feed/
BLOG2_RSS_URL=https://www.ultrasound-guided-injections.co.uk/feed/
NEWSLETTER_RSS_URL=https://zapier.com/engine/rss/5614589/completenewsletter
```

### Email Configuration
```bash
SENDER_EMAIL=hello@johnisaacson.co.uk
RECIPIENT_EMAILS=hello@johnisaacson.co.uk
```

**Note:** For `RECIPIENT_EMAILS`, you can add multiple recipients separated by commas:
```bash
RECIPIENT_EMAILS=hello@johnisaacson.co.uk,client@example.com,team@example.com
```

### Gmail API Credentials
```bash
GMAIL_CREDENTIALS_JSON=<paste the single-line credentials.json from Step 3>
GMAIL_TOKEN_JSON=<paste the single-line token JSON from Step 3>
```

### App Configuration
```bash
TEST_MODE=true
```

**Important:** Set `TEST_MODE=true` initially so it sends a test email immediately when deployed!

---

## Step 5: Deploy & Test (2 minutes)

1. After adding all variables, Railway will automatically redeploy
2. Go to **"Deployments"** tab
3. Click on the latest deployment
4. Click **"View Logs"**
5. You should see:
   ```
   Running initial job immediately for testing...
   Collecting content...
   ✓ Found X Instagram posts
   ✓ Found X YouTube videos
   ✓ Found X blog posts
   ✓ Found X newsletters
   Sending email...
   ✅ Email sent successfully!
   ```

6. **Check your inbox at hello@johnisaacson.co.uk** - you should receive the test email!

---

## Step 6: Switch to Production Mode (1 minute)

Once you've confirmed the test email looks good:

1. Go back to **Variables** tab in Railway
2. Change `TEST_MODE=true` to `TEST_MODE=false`
3. Railway will redeploy automatically

Now the app will:
- Run 24/7 on Railway
- Send weekly summaries every **Friday at 3:00 PM UK time**
- Collect content from the last 7 days

---

## Verify It's Working

Check the Railway logs to see:

```
Weekly Scheduler Started
Schedule: Every Friday at 3:00 PM UK time
Next run: [date/time]
```

You're done! The app is now running 24/7 in the cloud! 🎉

---

## What to Expect

### First Email
- Sent immediately when `TEST_MODE=true`
- Contains real Complete Physio content from last 7 days

### Weekly Emails (after switching to production)
- Sent every Friday at 3:00 PM UK time
- Includes:
  - Instagram posts (with links)
  - YouTube videos (with links)
  - Blog posts (with links)
  - Newsletters (title only, no links)
- Simple, easy-to-digest format

---

## Managing Recipients

To add or change recipients:

1. Go to Railway → Variables
2. Edit `RECIPIENT_EMAILS`
3. Add emails separated by commas:
   ```
   RECIPIENT_EMAILS=email1@example.com,email2@example.com,email3@example.com
   ```
4. Railway will redeploy automatically

---

## Troubleshooting

### Not receiving emails?

1. Check Railway logs for errors
2. Verify `SENDER_EMAIL` matches your Gmail account
3. Verify `RECIPIENT_EMAILS` is correct
4. Check spam/junk folder
5. Ensure Gmail token hasn't expired

### Gmail Token Expired?

If you see token errors in logs:

1. Regenerate token locally:
   ```bash
   cd /Users/john/railway-apps
   ./setup_gmail.sh
   ```

2. Get new token JSON:
   ```bash
   python3 -c "
   import pickle, json
   t = pickle.load(open('token.pickle', 'rb'))
   print(json.dumps({
       'token': t.token,
       'refresh_token': t.refresh_token,
       'token_uri': t.token_uri,
       'client_id': t.client_id,
       'client_secret': t.client_secret,
       'scopes': t.scopes
   }))
   "
   ```

3. Update `GMAIL_TOKEN_JSON` in Railway variables

### No content found?

Check if Complete Physio has posted in the last 7 days:
- Instagram: @completephysio
- YouTube: Check the channel
- Blog: https://complete-physio.co.uk/feed/

### App keeps restarting?

1. Check logs for specific error
2. Verify all environment variables are set correctly
3. Ensure JSON strings are valid (single line, no line breaks)

---

## Monitoring

### View Logs
```bash
# If you have Railway CLI installed:
railway logs

# Or via Railway dashboard:
# Go to Deployments → Click deployment → View Logs
```

### Check Next Run Time
Look in logs for:
```
Next run: [Friday at 15:00 UTC]
```

---

## Cost

- **Railway Free Tier**: $5/month credit
- **Estimated Usage**: ~$2-3/month
- **Well within free tier!**

---

## Making Changes

To update the app:

```bash
# Make changes to code locally
git add .
git commit -m "Update weekly summary app"
git push

# Railway auto-deploys from GitHub!
```

---

## Support

- **Railway Docs**: https://docs.railway.app
- **Full README**: See [README.md](README.md)
- **Quick Setup**: See [SETUP.md](SETUP.md)

---

## Quick Reference

**Railway Dashboard**: https://railway.app/dashboard

**Schedule**: Every Friday at 3:00 PM UK time

**Content Sources**:
- Instagram: @completephysio
- YouTube: UCzqxBIw58_WDqxYWWwq_L8Q
- Blog 1: complete-physio.co.uk
- Blog 2: ultrasound-guided-injections.co.uk
- Newsletter: Zapier RSS feed

**Current Recipients**: hello@johnisaacson.co.uk

---

You're all set! Your Complete Physio weekly summary will now be sent automatically every Friday! 📊✨
