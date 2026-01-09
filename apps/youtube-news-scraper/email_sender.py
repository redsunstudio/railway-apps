import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List
import os
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')

        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            raise ValueError("Email configuration missing. Set SENDER_EMAIL, SENDER_PASSWORD, and RECIPIENT_EMAIL environment variables.")

    def _create_html_email(self, articles: List[dict]) -> str:
        """Create HTML email content"""
        today = datetime.now().strftime("%B %d, %Y")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    border-bottom: 3px solid #ff0000;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                h1 {{
                    color: #ff0000;
                    margin: 0;
                    font-size: 28px;
                }}
                .date {{
                    color: #666;
                    font-size: 14px;
                    margin-top: 5px;
                }}
                .article {{
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }}
                .article:last-child {{
                    border-bottom: none;
                }}
                .source {{
                    display: inline-block;
                    background-color: #f0f0f0;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    color: #666;
                    margin-bottom: 8px;
                    font-weight: 500;
                }}
                .article-title {{
                    font-size: 18px;
                    margin: 10px 0;
                }}
                .article-title a {{
                    color: #1a73e8;
                    text-decoration: none;
                    font-weight: 500;
                }}
                .article-title a:hover {{
                    text-decoration: underline;
                }}
                .article-date {{
                    color: #666;
                    font-size: 13px;
                    margin-bottom: 8px;
                }}
                .article-summary {{
                    color: #555;
                    font-size: 14px;
                    line-height: 1.5;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                }}
                .no-articles {{
                    text-align: center;
                    padding: 40px;
                    color: #666;
                }}
                .count {{
                    background-color: #e8f5e9;
                    color: #2e7d32;
                    padding: 8px 16px;
                    border-radius: 4px;
                    display: inline-block;
                    margin-top: 10px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📺 YouTube News Digest</h1>
                    <div class="date">{today}</div>
                    <div class="count">{len(articles)} new article{'s' if len(articles) != 1 else ''} found</div>
                </div>
        """

        if not articles:
            html += """
                <div class="no-articles">
                    <p>No new YouTube news or updates found in the last 24 hours.</p>
                    <p>Check back tomorrow for the latest updates!</p>
                </div>
            """
        else:
            for article in articles:
                summary_html = f'<div class="article-summary">{article["summary"]}</div>' if article.get('summary') else ''
                date_html = f'<div class="article-date">📅 {article["published_date"]}</div>' if article.get('published_date') else ''

                html += f"""
                <div class="article">
                    <span class="source">{article['source']}</span>
                    <div class="article-title">
                        <a href="{article['url']}" target="_blank">{article['title']}</a>
                    </div>
                    {date_html}
                    {summary_html}
                </div>
                """

        html += """
                <div class="footer">
                    <p>This is an automated daily digest of YouTube news and updates.</p>
                    <p>Powered by Railway • Generated by YouTube News Scraper</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def send_digest(self, articles: List[dict]) -> bool:
        """Send email digest with articles"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = f"📺 YouTube News Digest - {datetime.now().strftime('%B %d, %Y')} ({len(articles)} updates)"
            message['From'] = self.sender_email
            message['To'] = self.recipient_email

            # Create HTML content
            html_content = self._create_html_email(articles)

            # Create plain text fallback
            text_content = f"YouTube News Digest - {datetime.now().strftime('%B %d, %Y')}\n\n"
            text_content += f"Found {len(articles)} articles:\n\n"

            for article in articles:
                text_content += f"Source: {article['source']}\n"
                text_content += f"Title: {article['title']}\n"
                text_content += f"URL: {article['url']}\n"
                if article.get('published_date'):
                    text_content += f"Date: {article['published_date']}\n"
                if article.get('summary'):
                    text_content += f"Summary: {article['summary']}\n"
                text_content += "\n" + "-" * 80 + "\n\n"

            # Attach parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            message.attach(part1)
            message.attach(part2)

            # Send email - try SSL first (port 465), then fallback to TLS (port 587)
            logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}")

            try:
                # Try SSL connection (port 465) first - works better on Railway
                if self.smtp_port == 465:
                    with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                        server.login(self.sender_email, self.sender_password)
                        server.send_message(message)
                else:
                    # Use TLS connection (port 587)
                    with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                        server.starttls()
                        server.login(self.sender_email, self.sender_password)
                        server.send_message(message)

                logger.info(f"Email sent successfully to {self.recipient_email}")
                return True

            except Exception as smtp_error:
                # If primary method fails and we're on 587, try 465
                if self.smtp_port == 587:
                    logger.warning(f"Port 587 failed: {smtp_error}. Trying port 465 (SSL)...")
                    try:
                        with smtplib.SMTP_SSL(self.smtp_server, 465) as server:
                            server.login(self.sender_email, self.sender_password)
                            server.send_message(message)
                        logger.info(f"Email sent successfully via port 465 to {self.recipient_email}")
                        return True
                    except Exception as ssl_error:
                        logger.error(f"Port 465 also failed: {ssl_error}")
                        raise
                else:
                    raise

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


if __name__ == '__main__':
    # Test email sender
    test_articles = [
        {
            'title': 'YouTube Tests New Feature for Creators',
            'url': 'https://example.com/article1',
            'source': 'TechCrunch',
            'published_date': 'January 9, 2026',
            'summary': 'YouTube is testing a new feature that could change how creators interact with their audience.'
        },
        {
            'title': 'APK Teardown Reveals Upcoming YouTube Update',
            'url': 'https://example.com/article2',
            'source': 'Android Authority',
            'published_date': 'January 8, 2026',
            'summary': 'Latest teardown shows YouTube is working on improved comment moderation tools.'
        }
    ]

    sender = EmailSender()
    sender.send_digest(test_articles)
