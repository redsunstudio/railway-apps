#!/usr/bin/env python3
"""
Send test email with REAL Complete Physio data
Collects actual content from Instagram, YouTube, Blog, and Newsletter
"""

import os
import sys

# Add paths
sys.path.insert(0, '/Users/john/railway-apps')
sys.path.insert(0, '/Users/john/railway-apps/apps/complete-physio-weekly-summary')

from instagram_scraper import InstagramScraper
from rss_parser import RSSParser
from email_formatter import EmailFormatter
import json
import pickle

print("="*60)
print("COMPLETE PHYSIO - REAL DATA TEST EMAIL")
print("="*60)

# Get sender email from user
sender_email = input("\nWhat Gmail address should send the email? (the one you authorized): ").strip()
if not sender_email:
    print("❌ No email provided. Exiting.")
    sys.exit(1)

print(f"\n✓ Sending from: {sender_email}")
print(f"✓ Sending to: hello@johnisaacson.co.uk")

# Set up environment variables
os.environ['SENDER_EMAIL'] = sender_email
os.environ['RECIPIENT_EMAILS'] = 'hello@johnisaacson.co.uk'

# Load Gmail credentials
with open('/Users/john/railway-apps/credentials.json', 'r') as f:
    creds_data = json.load(f)
os.environ['GMAIL_CREDENTIALS_JSON'] = json.dumps(creds_data)

with open('/Users/john/railway-apps/token.pickle', 'rb') as f:
    token_data = pickle.load(f)

token_json = {
    'token': token_data.token,
    'refresh_token': token_data.refresh_token,
    'token_uri': token_data.token_uri,
    'client_id': token_data.client_id,
    'client_secret': token_data.client_secret,
    'scopes': token_data.scopes
}
os.environ['GMAIL_TOKEN_JSON'] = json.dumps(token_json)

# Now import email sender after env vars are set
from email_sender import EmailSender

print("\n" + "="*60)
print("COLLECTING REAL COMPLETE PHYSIO CONTENT")
print("="*60)

# Initialize scrapers/parsers
instagram_scraper = InstagramScraper()
rss_parser = RSSParser()

# 1. Scrape Instagram
print("\n1. Scraping Instagram @completephysio...")
instagram_posts = instagram_scraper.get_recent_posts('completephysio', days=7)
print(f"   ✓ Found {len(instagram_posts)} posts")

# 2. Parse YouTube RSS
print("\n2. Parsing YouTube RSS feed...")
youtube_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCzqxBIw58_WDqxYWWwq_L8Q'
youtube_entries = rss_parser.parse_feed(youtube_url, days=7, feed_type='youtube')
print(f"   ✓ Found {len(youtube_entries)} videos")

# 3. Parse Blog RSS (both blogs)
print("\n3. Parsing blog RSS feeds...")
blog_url1 = 'https://complete-physio.co.uk/post-sitemap.xml'
blog_url2 = 'https://www.ultrasound-guided-injections.co.uk/post-sitemap.xml'

blog_entries = []
blog1_entries = rss_parser.parse_feed(blog_url1, days=7, feed_type='blog')
print(f"   ✓ Found {len(blog1_entries)} posts from Complete Physio blog")

blog2_entries = rss_parser.parse_feed(blog_url2, days=7, feed_type='blog')
print(f"   ✓ Found {len(blog2_entries)} posts from Ultrasound Injections blog")

blog_entries = blog1_entries + blog2_entries
print(f"   ✓ Total blog posts: {len(blog_entries)}")

# 4. Parse Newsletter RSS
print("\n4. Parsing newsletter RSS feed...")
newsletter_url = 'https://zapier.com/engine/rss/5614589/completenewsletter'
newsletter_entries = rss_parser.parse_feed(newsletter_url, days=7, feed_type='newsletter')
print(f"   ✓ Found {len(newsletter_entries)} newsletters")

print("\n" + "="*60)
print("CONTENT COLLECTION COMPLETE")
print("="*60)
total_items = len(instagram_posts) + len(youtube_entries) + len(blog_entries) + len(newsletter_entries)
print(f"\nTotal items collected: {total_items}")

if total_items == 0:
    print("\n⚠️  Warning: No content found from the last 7 days")
    print("This might be normal if Complete Physio hasn't posted recently.")
    response = input("\nSend email anyway with empty content? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)

# Generate email
print("\n" + "="*60)
print("GENERATING EMAIL")
print("="*60)

formatter = EmailFormatter()
subject, html_body, text_body = formatter.create_weekly_summary(
    instagram_posts, youtube_entries, blog_entries, newsletter_entries
)

print(f"\n✓ Subject: {subject}")
print(f"✓ HTML length: {len(html_body)} characters")

# Save preview
preview_file = '/tmp/complete_physio_real_data_email.html'
with open(preview_file, 'w') as f:
    f.write(html_body)
print(f"✓ Preview saved to: {preview_file}")

# Show summary of what's in the email
if instagram_posts:
    print(f"\nInstagram posts ({len(instagram_posts)}):")
    for post in instagram_posts[:3]:
        print(f"  • {post['date'].strftime('%b %d')} - {post['caption'][:50]}...")

if youtube_entries:
    print(f"\nYouTube videos ({len(youtube_entries)}):")
    for video in youtube_entries[:3]:
        print(f"  • {video['date'].strftime('%b %d')} - {video['title']}")

if blog_entries:
    print(f"\nBlog posts ({len(blog_entries)}):")
    for post in blog_entries[:3]:
        print(f"  • {post['date'].strftime('%b %d')} - {post['title']}")

if newsletter_entries:
    print(f"\nNewsletters ({len(newsletter_entries)}):")
    for newsletter in newsletter_entries[:3]:
        print(f"  • {newsletter['date'].strftime('%b %d')} - {newsletter['title']}")

# Send email
print("\n" + "="*60)
confirm = input("Send this email to hello@johnisaacson.co.uk? (y/n): ")
if confirm.lower() != 'y':
    print("\nCancelled. Preview saved at:", preview_file)
    sys.exit(0)

print("\nSending email via Gmail API...")
print("="*60)

try:
    sender = EmailSender()
    success = sender.send_weekly_summary(subject, html_body, text_body)

    if success:
        print("\n" + "="*60)
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("="*60)
        print(f"\nCheck your inbox at: hello@johnisaacson.co.uk")
        print(f"\nThe email contains REAL Complete Physio content from the last 7 days:")
        print(f"  • {len(instagram_posts)} Instagram posts")
        print(f"  • {len(youtube_entries)} YouTube videos")
        print(f"  • {len(blog_entries)} Blog posts")
        print(f"  • {len(newsletter_entries)} Newsletters")
        print(f"\nAll links are real and clickable!")
        print(f"\nPreview also saved at: {preview_file}")
    else:
        print("\n❌ Failed to send email. Check errors above.")
        print(f"Preview saved at: {preview_file}")

except Exception as e:
    print(f"\n❌ Error sending email: {str(e)}")
    print(f"\nPreview saved at: {preview_file}")
    import traceback
    traceback.print_exc()
