#!/bin/bash

echo "=================================================="
echo "RAILWAY ENVIRONMENT VARIABLES GENERATOR"
echo "=================================================="
echo ""
echo "Copy and paste these into Railway Variables tab:"
echo ""
echo "=================================================="
echo "GMAIL_CREDENTIALS_JSON"
echo "=================================================="

cat /Users/john/railway-apps/credentials.json | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin)))"

echo ""
echo ""
echo "=================================================="
echo "GMAIL_TOKEN_JSON"
echo "=================================================="

python3 << 'PYEOF'
import pickle
import json

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

print(json.dumps(token_dict))
PYEOF

echo ""
echo ""
echo "=================================================="
echo "OTHER ENVIRONMENT VARIABLES"
echo "=================================================="
echo "INSTAGRAM_USERNAME=completephysio"
echo "YOUTUBE_RSS_URL=https://www.youtube.com/feeds/videos.xml?channel_id=UCzqxBIw58_WDqxYWWwq_L8Q"
echo "BLOG_RSS_URL=https://complete-physio.co.uk/feed/"
echo "BLOG2_RSS_URL=https://www.ultrasound-guided-injections.co.uk/feed/"
echo "NEWSLETTER_RSS_URL=https://zapier.com/engine/rss/5614589/completenewsletter"
echo "SENDER_EMAIL=hello@johnisaacson.co.uk"
echo "RECIPIENT_EMAILS=hello@johnisaacson.co.uk"
echo "TEST_MODE=true"
echo ""
echo "=================================================="
echo "After test email works, change TEST_MODE to false"
echo "=================================================="
