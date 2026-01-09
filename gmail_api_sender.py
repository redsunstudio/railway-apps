import base64
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List
import logging

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GmailAPISender:
    """Email sender using Gmail API instead of SMTP (works on Railway!)"""

    def __init__(self):
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')

        # Gmail API uses OAuth2 tokens instead of passwords
        self.credentials_json = os.getenv('GMAIL_CREDENTIALS_JSON')
        self.token_json = os.getenv('GMAIL_TOKEN_JSON')

        if not all([self.sender_email, self.recipient_email]):
            raise ValueError("Email configuration missing. Set SENDER_EMAIL and RECIPIENT_EMAIL environment variables.")

        if not self.credentials_json or not self.token_json:
            raise ValueError("Gmail API credentials missing. Set GMAIL_CREDENTIALS_JSON and GMAIL_TOKEN_JSON environment variables.")

        self.service = self._create_gmail_service()

    def _create_gmail_service(self):
        """Create Gmail API service"""
        try:
            # Parse credentials from environment variable (JSON string)
            creds_info = json.loads(self.credentials_json)
            token_info = json.loads(self.token_json)

            # Create credentials object
            creds = Credentials(
                token=token_info.get('token'),
                refresh_token=token_info.get('refresh_token'),
                token_uri=creds_info.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=creds_info.get('client_id'),
                client_secret=creds_info.get('client_secret'),
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )

            # Build Gmail API service
            service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API service created successfully")
            return service

        except Exception as e:
            logger.error(f"Failed to create Gmail API service: {e}")
            raise

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
                    <p>Powered by Railway • Generated by YouTube News Scraper • Sent via Gmail API</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def send_digest(self, articles: List[dict]) -> bool:
        """Send email digest using Gmail API"""
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

            # Encode message for Gmail API
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send via Gmail API
            logger.info(f"Sending email via Gmail API to {self.recipient_email}")
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"✅ Email sent successfully to {self.recipient_email}")
            return True

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


if __name__ == '__main__':
    # Test the Gmail API sender
    test_articles = [
        {
            'title': 'Test: YouTube Announces New Feature',
            'url': 'https://example.com/test',
            'source': 'Test Source',
            'published_date': datetime.now().strftime('%B %d, %Y'),
            'summary': 'This is a test email sent via Gmail API.'
        }
    ]

    sender = GmailAPISender()
    sender.send_digest(test_articles)
