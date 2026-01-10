#!/usr/bin/env python3
"""
Simple test to send email immediately
"""

import os
import sys
import json
import pickle

# Set environment variables
os.environ['SENDER_EMAIL'] = 'hello@johnisaacson.co.uk'
os.environ['RECIPIENT_EMAILS'] = 'hello@johnisaacson.co.uk,chrismyers@complete-physio.co.uk,davebaker@complete-physio.co.uk,david@complete-physio.co.uk'
os.environ['TEST_MODE'] = 'true'

# Content source URLs
os.environ['INSTAGRAM_USERNAME'] = 'completephysio'
os.environ['YOUTUBE_RSS_URL'] = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCzqxBIw58_WDqxYWWwq_L8Q'
os.environ['BLOG_RSS_URL'] = 'https://complete-physio.co.uk/feed/'
os.environ['BLOG2_RSS_URL'] = 'https://www.ultrasound-guided-injections.co.uk/feed/'
os.environ['NEWSLETTER_RSS_URL'] = 'https://zapier.com/engine/rss/5614589/completenewsletter'

# Load Gmail credentials
print("Loading Gmail credentials...")
with open('/Users/john/railway-apps/credentials.json', 'r') as f:
    creds = json.load(f)
    os.environ['GMAIL_CREDENTIALS_JSON'] = json.dumps(creds)
    print(f"✓ Loaded credentials: {creds.get('installed', {}).get('client_id', 'Unknown')[:20]}...")

with open('/Users/john/railway-apps/token.pickle', 'rb') as f:
    token = pickle.load(f)
    token_dict = {
        'token': token.token,
        'refresh_token': token.refresh_token,
        'token_uri': token.token_uri,
        'client_id': token.client_id,
        'client_secret': token.client_secret,
        'scopes': list(token.scopes) if hasattr(token.scopes, '__iter__') else [token.scopes]
    }
    os.environ['GMAIL_TOKEN_JSON'] = json.dumps(token_dict)
    print(f"✓ Loaded token with refresh_token: {bool(token.refresh_token)}")

print("\n" + "="*60)
print("TESTING EMAIL SEND")
print("="*60)

# Import and run
try:
    from main import CompletePhysioSummary

    print("\nInitializing app...")
    app = CompletePhysioSummary()

    print("\nRunning summary generation and send...")
    success = app.generate_and_send_summary()

    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS! Check hello@johnisaacson.co.uk")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ FAILED - See errors above")
        print("="*60)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
