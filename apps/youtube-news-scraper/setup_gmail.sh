#!/bin/bash

# Gmail Setup Helper Script for YouTube News Scraper
# This script helps you configure Gmail credentials interactively

set -e

echo "================================================"
echo "  YouTube News Scraper - Gmail Setup Helper"
echo "================================================"
echo ""
echo "This script will help you set up Gmail for your news scraper."
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi
fi

echo "First, you need to generate a Gmail App Password."
echo ""
echo "📋 Steps to get your App Password:"
echo "1. Go to: https://myaccount.google.com/apppasswords"
echo "2. Choose 'Mail' for app"
echo "3. Choose 'Other' for device, enter 'YouTube News Scraper'"
echo "4. Click Generate"
echo "5. Copy the 16-character password (remove spaces)"
echo ""
echo "Press ENTER when you're ready to continue..."
read

# Collect information
echo ""
echo "Please enter your Gmail credentials:"
echo ""

read -p "Gmail address (sender): " SENDER_EMAIL
echo ""

read -p "Gmail App Password (16 chars, no spaces): " SENDER_PASSWORD
echo ""

read -p "Email to receive digests (can be same): " RECIPIENT_EMAIL
echo ""

read -p "Daily email time (24hr format, e.g., 07:00): " SCHEDULE_TIME
SCHEDULE_TIME=${SCHEDULE_TIME:-07:00}
echo ""

# Create .env file
cat > .env << EOF
# Gmail Configuration
SENDER_EMAIL=$SENDER_EMAIL
SENDER_PASSWORD=$SENDER_PASSWORD
RECIPIENT_EMAIL=$RECIPIENT_EMAIL

# SMTP Settings (defaults for Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Scheduler Settings
SCHEDULE_TIME=$SCHEDULE_TIME
RUN_ON_STARTUP=false

# Flask Configuration
PORT=3000
FLASK_ENV=production
EOF

echo "✅ Created .env file successfully!"
echo ""

# Test the configuration
echo "Would you like to test the email configuration now?"
read -p "Run test email? (Y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "Testing email configuration..."
    echo ""

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment and test
    source venv/bin/activate

    # Install dependencies if needed
    if ! pip show flask > /dev/null 2>&1; then
        echo "Installing dependencies..."
        pip install -q -r requirements.txt
    fi

    echo ""
    echo "Sending test email..."
    python email_sender.py

    echo ""
    echo "✅ Test complete! Check your inbox at $RECIPIENT_EMAIL"
else
    echo ""
    echo "Skipping test. You can test later with:"
    echo "  python email_sender.py"
fi

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Your Gmail is now configured for the scraper."
echo ""
echo "Next steps:"
echo "1. Test locally: python app.py"
echo "2. Deploy to Railway: railway up"
echo "3. Set Railway variables: railway variables set SENDER_EMAIL=\"$SENDER_EMAIL\""
echo ""
echo "See GMAIL_SETUP.md for detailed documentation."
echo ""
