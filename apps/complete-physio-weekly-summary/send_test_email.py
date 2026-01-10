"""
Send a test email with sample Complete Physio data
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to access credentials
sys.path.insert(0, '/Users/john/railway-apps')

from email_formatter import EmailFormatter
from email_sender import EmailSender

# Set environment variables for test
os.environ['SENDER_EMAIL'] = 'hello@johnisaacson.co.uk'  # Change this to your Gmail
os.environ['RECIPIENT_EMAILS'] = 'hello@johnisaacson.co.uk'

# Gmail credentials - read from parent directory
import json
import pickle

# Load credentials
with open('/Users/john/railway-apps/credentials.json', 'r') as f:
    creds_data = json.load(f)
os.environ['GMAIL_CREDENTIALS_JSON'] = json.dumps(creds_data)

# Load token (convert pickle to JSON format expected by email_sender)
with open('/Users/john/railway-apps/token.pickle', 'rb') as f:
    token_data = pickle.load(f)

# Convert token to JSON format
token_json = {
    'token': token_data.token,
    'refresh_token': token_data.refresh_token,
    'token_uri': token_data.token_uri,
    'client_id': token_data.client_id,
    'client_secret': token_data.client_secret,
    'scopes': token_data.scopes
}
os.environ['GMAIL_TOKEN_JSON'] = json.dumps(token_json)

print("="*60)
print("COMPLETE PHYSIO WEEKLY SUMMARY - TEST EMAIL")
print("="*60)
print(f"\nSending test email to: hello@johnisaacson.co.uk")
print("\nGenerating sample content...\n")

# Create sample data that looks like real Complete Physio content
instagram_posts = [
    {
        'date': datetime.now() - timedelta(days=1),
        'caption': '💪 5 exercises for stronger shoulders! Swipe through to see our physio-approved routine for building shoulder stability and preventing injury.',
        'url': 'https://www.instagram.com/p/sample1/',
        'likes': 342,
        'type': 'carousel'
    },
    {
        'date': datetime.now() - timedelta(days=3),
        'caption': 'New blog post 📝 Everything you need to know about managing lower back pain at home. Link in bio!',
        'url': 'https://www.instagram.com/p/sample2/',
        'likes': 289,
        'type': 'image'
    },
    {
        'date': datetime.now() - timedelta(days=5),
        'caption': 'Client success story! 🎉 From chronic knee pain to running 5k. Read their journey on our blog.',
        'url': 'https://www.instagram.com/p/sample3/',
        'likes': 567,
        'type': 'video'
    }
]

youtube_entries = [
    {
        'date': datetime.now() - timedelta(days=2),
        'title': 'How to Fix Your Posture in 5 Minutes | Complete Physio',
        'url': 'https://www.youtube.com/watch?v=sample1',
        'description': 'Quick and effective posture exercises you can do at your desk. Perfect for office workers experiencing neck and shoulder pain.'
    },
    {
        'date': datetime.now() - timedelta(days=6),
        'title': 'Runner\'s Knee: Causes, Prevention & Treatment',
        'url': 'https://www.youtube.com/watch?v=sample2',
        'description': 'Learn everything about patellofemoral pain syndrome from our expert physiotherapists. Includes rehabilitation exercises.'
    }
]

blog_entries = [
    {
        'date': datetime.now() - timedelta(days=1),
        'title': 'Understanding Chronic Pain: A Comprehensive Guide for Patients',
        'url': 'https://complete-physio.co.uk/blog/chronic-pain-guide',
        'description': 'Chronic pain affects millions. Learn about the latest evidence-based treatments and self-management strategies from our expert team.'
    },
    {
        'date': datetime.now() - timedelta(days=4),
        'title': 'Sports Injury Prevention: Essential Tips for Runners',
        'url': 'https://complete-physio.co.uk/blog/running-injury-prevention',
        'description': 'Prevent common running injuries with our comprehensive guide covering warm-ups, strength training, and recovery protocols.'
    },
    {
        'date': datetime.now() - timedelta(days=5),
        'title': 'Ultrasound-Guided Injections: What You Need to Know',
        'url': 'https://www.ultrasound-guided-injections.co.uk/blog/injection-guide',
        'description': 'Explore how ultrasound-guided injections can provide targeted relief for joint and soft tissue conditions.'
    }
]

newsletter_entries = [
    {
        'date': datetime.now() - timedelta(days=7),
        'title': 'Complete Physio Newsletter - January 2026 Edition',
        'url': 'https://completephysio.com/newsletter/january-2026',
        'description': 'Monthly updates including new clinic services, team highlights, patient success stories, and exclusive health tips from our physiotherapy experts.'
    }
]

print(f"✓ Instagram posts: {len(instagram_posts)}")
print(f"✓ YouTube videos: {len(youtube_entries)}")
print(f"✓ Blog posts: {len(blog_entries)}")
print(f"✓ Newsletters: {len(newsletter_entries)}")
print(f"\nTotal items: {len(instagram_posts) + len(youtube_entries) + len(blog_entries) + len(newsletter_entries)}")

# Generate email
print("\n" + "="*60)
print("Generating email...")
print("="*60)

formatter = EmailFormatter()
subject, html_body, text_body = formatter.create_weekly_summary(
    instagram_posts, youtube_entries, blog_entries, newsletter_entries
)

print(f"\n✓ Subject: {subject}")
print(f"✓ HTML length: {len(html_body)} characters")

# Save preview
preview_file = '/tmp/complete_physio_test_email.html'
with open(preview_file, 'w') as f:
    f.write(html_body)
print(f"✓ Preview saved to: {preview_file}")

# Send email
print("\n" + "="*60)
print("Sending email via Gmail API...")
print("="*60)

try:
    sender = EmailSender()
    success = sender.send_weekly_summary(subject, html_body, text_body)

    if success:
        print("\n" + "="*60)
        print("✅ TEST EMAIL SENT SUCCESSFULLY!")
        print("="*60)
        print(f"\nCheck your inbox at: hello@johnisaacson.co.uk")
        print("\nThe email contains:")
        print("  • 3 Instagram posts")
        print("  • 2 YouTube videos")
        print("  • 3 Blog posts")
        print("  • 1 Newsletter")
        print("\nAll links are clickable and will open in new tabs.")
    else:
        print("\n❌ Failed to send email. Check the errors above.")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Make sure credentials.json and token.pickle are valid")
    print("2. Check that Gmail API is enabled")
    print("3. Verify the sender email matches your Gmail account")
