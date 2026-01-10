"""
Email Formatter Module
Creates beautiful HTML email summaries
"""

from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailFormatter:
    def __init__(self):
        pass

    def create_weekly_summary(self, instagram_posts, youtube_entries, blog_entries, newsletter_entries):
        """
        Create formatted HTML email from all content sources

        Args:
            instagram_posts: List of Instagram post dicts
            youtube_entries: List of YouTube RSS entry dicts
            blog_entries: List of blog RSS entry dicts
            newsletter_entries: List of newsletter RSS entry dicts

        Returns:
            tuple: (subject, html_body, text_body)
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        date_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"

        subject = f"Complete Physio Weekly Summary - {date_range}"

        # Create HTML email
        html_body = self._create_html(
            date_range, instagram_posts, youtube_entries, blog_entries, newsletter_entries
        )

        # Create text fallback
        text_body = self._create_text(
            date_range, instagram_posts, youtube_entries, blog_entries, newsletter_entries
        )

        return subject, html_body, text_body

    def _create_html(self, date_range, instagram_posts, youtube_entries, blog_entries, newsletter_entries):
        """Create simple, easy-to-digest HTML email body"""

        total_items = len(instagram_posts) + len(youtube_entries) + len(blog_entries) + len(newsletter_entries)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.5;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        .header {{
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #333;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 24px;
            color: #333;
        }}
        .header .date {{
            color: #666;
            font-size: 14px;
        }}
        .summary {{
            background: #f5f5f5;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
        .summary p {{
            margin: 5px 0;
            font-size: 14px;
        }}
        .section {{
            margin-bottom: 35px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 1px solid #ddd;
        }}
        .item {{
            margin-bottom: 20px;
        }}
        .item-link {{
            color: #0066cc;
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            display: block;
            margin-bottom: 5px;
        }}
        .item-link:hover {{
            text-decoration: underline;
        }}
        .item-meta {{
            color: #666;
            font-size: 13px;
            margin-bottom: 5px;
        }}
        .item-text {{
            color: #555;
            font-size: 14px;
            line-height: 1.4;
        }}
        .no-content {{
            color: #999;
            font-style: italic;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Complete Physio Weekly Summary</h1>
        <div class="date">{date_range}</div>
    </div>

    <div class="summary">
        <p><strong>This week's activity:</strong></p>
        <p>Instagram: {len(instagram_posts)} posts | YouTube: {len(youtube_entries)} videos | Blog: {len(blog_entries)} posts | Newsletter: {len(newsletter_entries)} editions</p>
        <p><strong>Total:</strong> {total_items} items</p>
    </div>
"""

        # Add sections (only if they have content)
        html += self._format_instagram_section(instagram_posts)
        html += self._format_rss_section(youtube_entries, "YouTube Videos", "")
        html += self._format_rss_section(blog_entries, "Blog Posts", "")
        html += self._format_newsletter_section(newsletter_entries)

        # Footer
        html += """
    <div class="footer">
        Automated weekly summary • Generated """ + datetime.now().strftime('%B %d, %Y') + """
    </div>
</body>
</html>
"""

        return html

    def _format_instagram_section(self, posts):
        """Format Instagram posts section - simple and clean"""
        if not posts:
            return ""

        html = '<div class="section"><div class="section-title">Instagram</div>\n'

        for post in sorted(posts, key=lambda x: x['date'], reverse=True):
            caption = post['caption'][:150] + '...' if len(post['caption']) > 150 else post['caption']
            caption = caption.replace('\n', ' ')  # Remove line breaks

            html += f"""
        <div class="item">
            <a href="{post['url']}" class="item-link" target="_blank">View Post</a>
            <div class="item-meta">{post['date'].strftime('%b %d, %Y')} • {post['likes']} likes</div>
            <div class="item-text">{caption}</div>
        </div>
"""

        html += '</div>'
        return html

    def _format_rss_section(self, entries, title, emoji):
        """Format RSS feed section - simple and clean"""
        if not entries:
            return ""

        html = f'<div class="section"><div class="section-title">{title}</div>\n'

        for entry in sorted(entries, key=lambda x: x['date'], reverse=True):
            html += f"""
        <div class="item">
            <a href="{entry['url']}" class="item-link" target="_blank">{entry['title']}</a>
            <div class="item-meta">{entry['date'].strftime('%b %d, %Y')}</div>
"""
            if entry.get('description'):
                description = entry['description'][:200] + '...' if len(entry['description']) > 200 else entry['description']
                html += f'            <div class="item-text">{description}</div>\n'

            html += '        </div>\n'

        html += '</div>'
        return html

    def _format_newsletter_section(self, newsletters):
        """Format newsletter section - title only, no links"""
        if not newsletters:
            return ""

        html = '<div class="section"><div class="section-title">Newsletters</div>\n'

        for newsletter in sorted(newsletters, key=lambda x: x['date'], reverse=True):
            # Clean up title - remove [Test] prefix if present
            title = newsletter['title'].replace('[Test] ', '')

            html += f"""
        <div class="item">
            <div class="item-link" style="cursor: default; color: #333;">{title}</div>
            <div class="item-meta">{newsletter['date'].strftime('%b %d, %Y')}</div>
        </div>
"""

        html += '</div>'
        return html

    def _create_text(self, date_range, instagram_posts, youtube_entries, blog_entries, newsletter_entries):
        """Create plain text email fallback"""
        text = f"""
COMPLETE PHYSIO WEEKLY SUMMARY
{date_range}
{'='*60}

SUMMARY:
- Instagram Posts: {len(instagram_posts)}
- YouTube Videos: {len(youtube_entries)}
- Blog Posts: {len(blog_entries)}
- Newsletters: {len(newsletter_entries)}

"""

        # Instagram
        text += f"\n{'='*60}\nINSTAGRAM ({len(instagram_posts)} posts)\n{'='*60}\n"
        if instagram_posts:
            for post in sorted(instagram_posts, key=lambda x: x['date'], reverse=True):
                text += f"\n{post['date'].strftime('%b %d, %Y')}\n"
                text += f"{post['url']}\n"
                caption = post['caption'][:150] + '...' if len(post['caption']) > 150 else post['caption']
                text += f"{caption}\n"
                text += f"❤️ {post['likes']} likes\n"
        else:
            text += "No Instagram posts this week\n"

        # YouTube
        text += f"\n{'='*60}\nYOUTUBE ({len(youtube_entries)} videos)\n{'='*60}\n"
        if youtube_entries:
            for entry in sorted(youtube_entries, key=lambda x: x['date'], reverse=True):
                text += f"\n{entry['date'].strftime('%b %d, %Y')}\n"
                text += f"{entry['title']}\n"
                text += f"{entry['url']}\n"
        else:
            text += "No YouTube videos this week\n"

        # Blog
        text += f"\n{'='*60}\nBLOG ({len(blog_entries)} posts)\n{'='*60}\n"
        if blog_entries:
            for entry in sorted(blog_entries, key=lambda x: x['date'], reverse=True):
                text += f"\n{entry['date'].strftime('%b %d, %Y')}\n"
                text += f"{entry['title']}\n"
                text += f"{entry['url']}\n"
        else:
            text += "No blog posts this week\n"

        # Newsletter
        text += f"\n{'='*60}\nNEWSLETTER ({len(newsletter_entries)} editions)\n{'='*60}\n"
        if newsletter_entries:
            for entry in sorted(newsletter_entries, key=lambda x: x['date'], reverse=True):
                text += f"\n{entry['date'].strftime('%b %d, %Y')}\n"
                text += f"{entry['title']}\n"
                text += f"{entry['url']}\n"
        else:
            text += "No newsletters this week\n"

        text += f"\n\n{'='*60}\n"
        text += f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"

        return text


def test_formatter():
    """Test the email formatter"""
    formatter = EmailFormatter()

    # Sample data
    instagram_posts = [
        {
            'date': datetime.now() - timedelta(days=1),
            'caption': 'Test Instagram post with a caption',
            'url': 'https://instagram.com/p/test',
            'likes': 123,
            'image_url': 'https://picsum.photos/400/400',
            'type': 'image'
        }
    ]

    youtube_entries = [
        {
            'date': datetime.now() - timedelta(days=2),
            'title': 'Test YouTube Video',
            'url': 'https://youtube.com/watch?v=test',
            'description': 'Test video description',
            'thumbnail': 'https://picsum.photos/400/300'
        }
    ]

    blog_entries = []
    newsletter_entries = []

    subject, html, text = formatter.create_weekly_summary(
        instagram_posts, youtube_entries, blog_entries, newsletter_entries
    )

    print(f"Subject: {subject}\n")
    print(f"HTML length: {len(html)} characters")
    print(f"Text length: {len(text)} characters")

    # Save to file for preview
    with open('/tmp/test_email.html', 'w') as f:
        f.write(html)
    print("\nHTML preview saved to /tmp/test_email.html")


if __name__ == "__main__":
    test_formatter()
