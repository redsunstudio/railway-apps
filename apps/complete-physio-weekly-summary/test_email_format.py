"""
Quick test to preview the simplified email format
"""

from datetime import datetime, timedelta
from email_formatter import EmailFormatter

# Create sample data
formatter = EmailFormatter()

instagram_posts = [
    {
        'date': datetime.now() - timedelta(days=1),
        'caption': 'Great session today working on shoulder mobility exercises. Remember to warm up properly!',
        'url': 'https://instagram.com/p/sample1',
        'likes': 156,
        'type': 'image'
    },
    {
        'date': datetime.now() - timedelta(days=3),
        'caption': 'New blog post alert! Check out our latest article on managing lower back pain.',
        'url': 'https://instagram.com/p/sample2',
        'likes': 203,
        'type': 'image'
    }
]

youtube_entries = [
    {
        'date': datetime.now() - timedelta(days=2),
        'title': 'How to Improve Your Posture in 5 Minutes',
        'url': 'https://youtube.com/watch?v=sample',
        'description': 'Quick and effective posture exercises you can do anywhere.'
    }
]

blog_entries = [
    {
        'date': datetime.now() - timedelta(days=1),
        'title': 'Understanding Chronic Pain: A Comprehensive Guide',
        'url': 'https://complete-physio.co.uk/blog/sample',
        'description': 'Learn about the causes, symptoms, and treatment options for chronic pain conditions.'
    },
    {
        'date': datetime.now() - timedelta(days=4),
        'title': 'Sports Injury Prevention Tips for Runners',
        'url': 'https://complete-physio.co.uk/blog/sample2',
        'description': 'Essential advice for runners to prevent common injuries and stay healthy.'
    }
]

newsletter_entries = [
    {
        'date': datetime.now() - timedelta(days=5),
        'title': 'Complete Physio Newsletter - January 2026',
        'url': 'https://completephysio.com/newsletter/jan',
        'description': 'Monthly updates, new services, and health tips from our team.'
    }
]

# Generate email
subject, html, text = formatter.create_weekly_summary(
    instagram_posts, youtube_entries, blog_entries, newsletter_entries
)

print("="*60)
print("EMAIL PREVIEW - Simplified Format")
print("="*60)
print(f"\nSubject: {subject}\n")

# Save HTML to file for viewing in browser
output_file = '/tmp/complete_physio_email_preview.html'
with open(output_file, 'w') as f:
    f.write(html)

print(f"✓ HTML email saved to: {output_file}")
print("\nOpen this file in your browser to see the preview!")
print("\n" + "="*60)

# Show plain text version
print("\nPLAIN TEXT VERSION:")
print("="*60)
print(text)
