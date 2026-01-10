"""
Email Sender Module
Sends weekly summary emails using Gmail API
"""

import base64
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    """Send emails using Gmail API (works on Railway)"""

    def __init__(self):
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.recipient_emails = os.getenv('RECIPIENT_EMAILS', '').split(',')
        self.recipient_emails = [email.strip() for email in self.recipient_emails if email.strip()]

        # Gmail API uses OAuth2 tokens instead of passwords
        self.credentials_json = os.getenv('GMAIL_CREDENTIALS_JSON')
        self.token_json = os.getenv('GMAIL_TOKEN_JSON')

        if not self.sender_email or not self.recipient_emails:
            raise ValueError("Email configuration missing. Set SENDER_EMAIL and RECIPIENT_EMAILS environment variables.")

        if not self.credentials_json or not self.token_json:
            raise ValueError("Gmail API credentials missing. Set GMAIL_CREDENTIALS_JSON and GMAIL_TOKEN_JSON environment variables.")

        self.service = self._create_gmail_service()

    def _create_gmail_service(self):
        """Create Gmail API service"""
        try:
            # Parse credentials from environment variable (JSON string)
            creds_info = json.loads(self.credentials_json)
            token_info = json.loads(self.token_json)

            logger.info("Creating Gmail API credentials...")
            logger.info(f"Has refresh_token: {bool(token_info.get('refresh_token'))}")
            logger.info(f"Has client_id: {bool(creds_info.get('client_id') or token_info.get('client_id'))}")
            logger.info(f"Has client_secret: {bool(creds_info.get('client_secret') or token_info.get('client_secret'))}")

            # Get client_id and client_secret from either source
            # (credentials.json for installed apps, or token.json if already there)
            if 'installed' in creds_info:
                client_id = creds_info['installed']['client_id']
                client_secret = creds_info['installed']['client_secret']
                token_uri = creds_info['installed']['token_uri']
            else:
                client_id = creds_info.get('client_id') or token_info.get('client_id')
                client_secret = creds_info.get('client_secret') or token_info.get('client_secret')
                token_uri = creds_info.get('token_uri', 'https://oauth2.googleapis.com/token')

            # Create credentials object with all required fields
            creds = Credentials(
                token=token_info.get('token'),
                refresh_token=token_info.get('refresh_token'),
                token_uri=token_uri,
                client_id=client_id,
                client_secret=client_secret,
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )

            # Build Gmail API service
            service = build('gmail', 'v1', credentials=creds)
            logger.info("✅ Gmail API service created successfully")
            return service

        except Exception as e:
            logger.error(f"❌ Failed to create Gmail API service: {e}")
            logger.error(f"Credentials format: {type(creds_info)}")
            logger.error(f"Token format: {type(token_info)}")
            raise

    def send_weekly_summary(self, subject, html_body, text_body):
        """
        Send weekly summary email to all recipients using CC

        Args:
            subject: Email subject line
            html_body: HTML email content
            text_body: Plain text fallback

        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email

            # First recipient is To, rest are CC
            message['To'] = self.recipient_emails[0]
            if len(self.recipient_emails) > 1:
                cc_recipients = ', '.join(self.recipient_emails[1:])
                message['Cc'] = cc_recipients
                logger.info(f"Sending to: {self.recipient_emails[0]}, CC: {cc_recipients}")
            else:
                logger.info(f"Sending to: {self.recipient_emails[0]}")

            # Attach parts
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            message.attach(part1)
            message.attach(part2)

            # Encode message for Gmail API
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send via Gmail API
            logger.info(f"Sending email via Gmail API")
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"✅ Email sent successfully to all recipients")
            return True

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


if __name__ == '__main__':
    # Test the email sender
    sender = EmailSender()

    test_subject = "Test Email - Complete Physio Weekly Summary"
    test_html = """
    <html>
        <body>
            <h1>Test Email</h1>
            <p>This is a test email from the Complete Physio Weekly Summary system.</p>
        </body>
    </html>
    """
    test_text = "Test Email\n\nThis is a test email from the Complete Physio Weekly Summary system."

    sender.send_weekly_summary(test_subject, test_html, test_text)
