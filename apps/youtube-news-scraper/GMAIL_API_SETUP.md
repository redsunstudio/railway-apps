# Gmail API Setup Guide

The Gmail API uses HTTPS instead of SMTP, which works perfectly on Railway! This guide will walk you through setting it up.

## Why Gmail API?

- **Works on Railway** - Uses HTTPS (port 443) instead of blocked SMTP ports
- **More secure** - OAuth2 instead of app passwords
- **More reliable** - Better delivery rates
- **No SMTP limitations** - Bypasses cloud platform restrictions

## Setup Steps (10 minutes)

### Step 1: Enable Gmail API in Google Cloud Console

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing:
   - Click the project dropdown at the top
   - Click "NEW PROJECT"
   - Name it: "YouTube News Scraper"
   - Click "CREATE"

3. Enable Gmail API:
   - Go to https://console.cloud.google.com/apis/library
   - Search for "Gmail API"
   - Click "Gmail API"
   - Click "ENABLE"

### Step 2: Create OAuth 2.0 Credentials

1. Go to https://console.cloud.google.com/apis/credentials
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure OAuth consent screen first:
   - Click "CONFIGURE CONSENT SCREEN"
   - Choose "External" (unless you have Google Workspace)
   - Fill in:
     - App name: "YouTube News Scraper"
     - User support email: your email
     - Developer contact: your email
   - Click "SAVE AND CONTINUE"
   - Skip scopes (click "SAVE AND CONTINUE")
   - Add your email as a test user
   - Click "SAVE AND CONTINUE"

4. Back to credentials, click "CREATE CREDENTIALS" → "OAuth client ID"
5. Choose "Desktop app"
6. Name it: "YouTube News Scraper Desktop"
7. Click "CREATE"
8. **Download the JSON file** - click "DOWNLOAD JSON"
9. Rename the file to `credentials.json`

### Step 3: Generate Token (Authorize the App)

Run this script to generate your token:

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper

# Create auth script
cat > generate_token.py << 'EOF'
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    creds = None

    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("Download it from Google Cloud Console")
        return

    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Extract token info
    token_info = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    # Read credentials.json
    with open('credentials.json', 'r') as f:
        creds_data = json.load(f)

    print("\n✅ Authorization successful!")
    print("\n📋 Copy these values to your Railway environment variables:\n")
    print("GMAIL_CREDENTIALS_JSON=")
    print(json.dumps(creds_data))
    print("\nGMAIL_TOKEN_JSON=")
    print(json.dumps(token_info))
    print("\n")

    # Save to .env for local testing
    with open('.env', 'a') as f:
        f.write(f"\n# Gmail API Credentials\n")
        f.write(f'GMAIL_CREDENTIALS_JSON=\'{json.dumps(creds_data)}\'\n')
        f.write(f'GMAIL_TOKEN_JSON=\'{json.dumps(token_info)}\'\n')

    print("✅ Also saved to .env for local testing")

if __name__ == '__main__':
    main()
EOF

# Install dependencies and run
pip install -r requirements.txt
python generate_token.py
```

**This will:**
1. Open your browser
2. Ask you to log in to Gmail
3. Ask for permission to send emails
4. Generate token and print the values

### Step 4: Set Railway Environment Variables

Copy the values from the previous step and set them in Railway:

```bash
# The script outputs these - copy the full JSON strings
railway variables --set 'GMAIL_CREDENTIALS_JSON={"installed":{"client_id":"..."}}'
railway variables --set 'GMAIL_TOKEN_JSON={"token":"...","refresh_token":"..."}'

# Also keep these
railway variables --set "SENDER_EMAIL=hello@johnisaacson.co.uk"
railway variables --set "RECIPIENT_EMAIL=hello@johnisaacson.co.uk"
```

**Important:** Make sure to wrap the JSON in single quotes when setting Railway variables!

### Step 5: Deploy and Test

```bash
# Commit changes
git add -A
git commit -m "Add Gmail API support"
git push

# Deploy
railway up

# Test
curl -X POST -H "Content-Type: application/json" -d '{}' https://your-app.railway.app/api/test-email
```

## Quick Local Test

```bash
cd /Users/john/railway-apps/apps/youtube-news-scraper

# Make sure you have credentials in .env
python app.py

# In another terminal
curl -X POST -H "Content-Type: application/json" -d '{}' http://localhost:3000/api/test-email
```

## Troubleshooting

### "credentials.json not found"
- Download from Google Cloud Console
- Place in `/Users/john/railway-apps/apps/youtube-news-scraper/`

### "The user has not completed the registration"
- Go back to OAuth consent screen
- Add your email as a test user

### "Access blocked: This app's request is invalid"
- Make sure OAuth consent screen is configured
- Authorized redirect URI should be `http://localhost` for desktop apps

### "Invalid grant" error
- Token expired - regenerate by running `python generate_token.py` again

## Security Notes

1. **Never commit credentials.json or token.pickle to git** (already in .gitignore)
2. Keep your JSON strings secure in Railway variables
3. Gmail API has daily limits (10,000 emails/day for free tier)
4. Tokens auto-refresh, so they work long-term

## Alternative: Simpler OAuth Flow

If the above is too complex, use this simplified approach:

```python
# Just set these in Railway:
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
# App will automatically fall back to SMTP locally
```

Then only use Gmail API on Railway where SMTP is blocked.

## What's Next?

Once set up, your app will:
1. Automatically use Gmail API on Railway (HTTPS)
2. Fall back to SMTP locally for testing
3. Send beautiful email digests daily at 7 AM

The Gmail API works perfectly on Railway because it uses HTTPS (port 443) which is never blocked! 🎉
