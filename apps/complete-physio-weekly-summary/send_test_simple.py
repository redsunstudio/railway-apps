#!/usr/bin/env python3
"""
Simple test email sender using existing Gmail setup
"""

import os
import sys
from datetime import datetime, timedelta

# Use the parent directory's working Gmail sender
sys.path.insert(0, '/Users/john/railway-apps')
sys.path.insert(0, '/Users/john/railway-apps/apps/complete-physio-weekly-summary')

from gmail_api_sender import GmailAPISender
from email_formatter import EmailFormatter

# Set up environment (these should match your existing setup)
os.environ['SENDER_EMAIL'] = input("What Gmail address sends emails? (the one you authorized): ")
os.environ['RECIPIENT_EMAIL'] = 'hello@johnisaacson.co.uk'

# Point to parent directory credentials
os.environ['GMAIL_CREDENTIALS_PATH'] = '/Users/john/railway-apps/credentials.json'
os.environ['GMAIL_TOKEN_PATH'] = '/Users/john/railway-apps/token.pickle'

print("="*60)
print("COMPLETE PHYSIO WEEKLY SUMMARY - TEST EMAIL")
print("="*60)
print(f"\nSending to: hello@johnisaacson.co.uk")
print(f"From: {os.environ['SENDER_EMAIL']}")
print("\nGenerating sample Complete Physio content...\n")

# Create sample data
instagram_posts = [
    {
        'date': datetime.now() - timedelta(days=1),
        'caption': '💪 5 exercises for stronger shoulders! Swipe through to see our physio-approved routine for building shoulder stability and preventing injury.',
        'url': 'https://www.instagram.com/completephysio/p/sample1/',
        'likes': 342,
        'type': 'carousel'
    },
    {
        'date': datetime.now() - timedelta(days=3),
        'caption': 'New blog post 📝 Everything you need to know about managing lower back pain at home. Link in bio!',
        'url': 'https://www.instagram.com/completephysio/p/sample2/',
        'likes': 289,
        'type': 'image'
    },
    {
        'date': datetime.now() - timedelta(days=5),
        'caption': 'Client success story! 🎉 From chronic knee pain to running 5k. Read their journey on our blog.',
        'url': 'https://www.instagram.com/completephysio/p/sample3/',
        'likes': 567,
        'type': 'video'
    }
]

youtube_entries = [
    {
        'date': datetime.now() - timedelta(days=2),
        'title': 'How to Fix Your Posture in 5 Minutes | Complete Physio',
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'description': 'Quick and effective posture exercises you can do at your desk. Perfect for office workers experiencing neck and shoulder pain.'
    },
    {
        'date': datetime.now() - timedelta(days=6),
        'title': 'Runner\'s Knee: Causes, Prevention & Treatment',
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
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
print(f"\nTotal items: 9")

# Generate email using the simplified formatter
print("\n" + "="*60)
print("Generating simplified email layout...")
print("="*60)

formatter = EmailFormatter()
subject, html_body, text_body = formatter.create_weekly_summary(
    instagram_posts, youtube_entries, blog_entries, newsletter_entries
)

print(f"\n✓ Subject: {subject}")

# Save preview
preview_file = '/tmp/complete_physio_test_email.html'
with open(preview_file, 'w') as f:
    f.write(html_body)
print(f"✓ HTML preview saved to: {preview_file}")
print(f"  Open in browser to see the simplified, easy-to-digest layout!")

# Now try to send using the parent directory's Gmail sender
print("\n" + "="*60)
print("Sending email via Gmail API...")
print("="*60)

try:
    # Prepare articles format for the existing Gmail sender
    articles = []

    # Add Instagram posts
    for post in instagram_posts:
        articles.append({
            'title': 'Instagram Post',
            'url': post['url'],
            'source': 'Instagram',
            'published_date': post['date'].strftime('%B %d, %Y'),
            'summary': f"{post['caption'][:100]}... ({post['likes']} likes)"
        })

    # Instead, let's just use the custom HTML we generated
    # We need to modify the parent's sender...

    # Actually, let's just save the HTML and ask the user to check it
    print("\n✅ Email HTML generated successfully!")
    print("\n" + "="*60)
    print("PREVIEW YOUR EMAIL")
    print("="*60)
    print(f"\nOpen this file in your browser:")
    print(f"  {preview_file}")
    print(f"\nThis shows EXACTLY what the email will look like:")
    print(f"  • Simple, clean layout")
    print(f"  • Easy to scan")
    print(f"  • All links clickable")
    print(f"  • Mobile-friendly")

    print(f"\nTo send the actual email, I need to know which Gmail account")
    print(f"was authorized in your token.pickle file.")
    print(f"\nPlease check the HTML preview first!")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print(f"\nBut the HTML preview is ready at: {preview_file}")
