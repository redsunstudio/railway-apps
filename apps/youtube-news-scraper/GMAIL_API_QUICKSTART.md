# Gmail API Quick Start (5 minutes)

**This works on Railway!** Gmail API uses HTTPS instead of SMTP.

## Step 1: Enable Gmail API (2 min)

1. Go to https://console.cloud.google.com/
2. Create project: "YouTube News Scraper"
3. Enable Gmail API: https://console.cloud.google.com/apis/library/gmail
4. Click "ENABLE"

## Step 2: Create Credentials (2 min)

1. Go to https://console.cloud.google.com/apis/credentials
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. Configure consent screen if prompted:
   - External user type
   - App name: "YouTube News Scraper"
   - Add your email as test user
4. Create "Desktop app" OAuth client
5. **Download JSON** and save as `credentials.json` in this folder

## Step 3: Generate Token (1 min)

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper
python3 generate_gmail_token.py
```

This will:
- Open your browser
- Ask you to authorize
- Generate and save credentials
- Show Railway commands to copy

## Step 4: Set Railway Variables

Copy the commands from step 3 output and run them:

```bash
railway variables --set 'GMAIL_CREDENTIALS_JSON={"installed":{...}}'
railway variables --set 'GMAIL_TOKEN_JSON={"token":"...",...}'
```

## Step 5: Deploy & Test

```bash
railway up

# Test
curl -X POST -H "Content-Type: application/json" -d '{}' https://cheerful-serenity-production-3e99.up.railway.app/api/test-email
```

Check your email! 📧

## Done!

Your app now uses Gmail API on Railway (which works!) and falls back to SMTP locally.

## Need Help?

See [GMAIL_API_SETUP.md](GMAIL_API_SETUP.md) for detailed guide with screenshots and troubleshooting.
