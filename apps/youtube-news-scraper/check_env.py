#!/usr/bin/env python3
"""
Environment checker for Railway deployment
Run this to diagnose configuration issues
"""
import os
import sys

def check_env():
    """Check all required environment variables"""
    print("=" * 80)
    print("🔍 YouTube News Scraper - Environment Check")
    print("=" * 80)

    required_vars = {
        'SENDER_EMAIL': os.getenv('SENDER_EMAIL'),
        'RECIPIENT_EMAIL': os.getenv('RECIPIENT_EMAIL'),
        'SCHEDULE_TIME': os.getenv('SCHEDULE_TIME', '03:00 (default)'),
    }

    optional_vars = {
        'RUN_ON_STARTUP': os.getenv('RUN_ON_STARTUP', 'false (default)'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com (default)'),
        'SMTP_PORT': os.getenv('SMTP_PORT', '587 (default)'),
    }

    gmail_api_vars = {
        'GMAIL_CREDENTIALS_JSON': os.getenv('GMAIL_CREDENTIALS_JSON'),
        'GMAIL_TOKEN_JSON': os.getenv('GMAIL_TOKEN_JSON'),
    }

    smtp_vars = {
        'SENDER_PASSWORD': os.getenv('SENDER_PASSWORD'),
    }

    print("\n📋 REQUIRED CONFIGURATION:")
    print("-" * 80)
    all_ok = True
    for key, value in required_vars.items():
        if value and value != 'NOT SET':
            print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: NOT SET")
            all_ok = False

    print("\n⚙️  OPTIONAL CONFIGURATION:")
    print("-" * 80)
    for key, value in optional_vars.items():
        print(f"ℹ️  {key}: {value}")

    print("\n📧 EMAIL SENDER CONFIGURATION:")
    print("-" * 80)

    # Check Gmail API
    gmail_api_ok = all(gmail_api_vars.values())
    if gmail_api_ok:
        print("✅ Gmail API credentials: CONFIGURED")
        print(f"   - GMAIL_CREDENTIALS_JSON: {len(gmail_api_vars['GMAIL_CREDENTIALS_JSON'])} characters")
        print(f"   - GMAIL_TOKEN_JSON: {len(gmail_api_vars['GMAIL_TOKEN_JSON'])} characters")
    else:
        print("❌ Gmail API credentials: NOT CONFIGURED")
        for key, value in gmail_api_vars.items():
            status = "SET" if value else "NOT SET"
            print(f"   - {key}: {status}")

    # Check SMTP
    smtp_ok = bool(smtp_vars['SENDER_PASSWORD'])
    if smtp_ok:
        print("✅ SMTP credentials: CONFIGURED")
        print(f"   - SENDER_PASSWORD: {len(smtp_vars['SENDER_PASSWORD'])} characters")
    else:
        print("❌ SMTP credentials: NOT CONFIGURED")

    print("\n" + "=" * 80)

    # Final verdict
    if not all_ok:
        print("❌ CONFIGURATION INCOMPLETE")
        print("\nMissing required variables. The app will not function.")
        return False

    if not gmail_api_ok and not smtp_ok:
        print("❌ NO EMAIL SENDER CONFIGURED")
        print("\nYou need either Gmail API or SMTP credentials.")
        print("\nFor Railway, Gmail API is REQUIRED because SMTP ports are blocked.")
        return False

    if gmail_api_ok:
        print("✅ CONFIGURATION COMPLETE - Gmail API")
        print("\nAll required variables are set. Using Gmail API for email sending.")
        print("This is the recommended configuration for Railway.")
    elif smtp_ok:
        print("⚠️  CONFIGURATION COMPLETE - SMTP")
        print("\nUsing SMTP for email sending.")
        print("⚠️  WARNING: Railway blocks SMTP ports 587 and 465.")
        print("⚠️  Email sending will FAIL on Railway. Use Gmail API instead.")

    print("=" * 80)
    return True

if __name__ == '__main__':
    success = check_env()
    sys.exit(0 if success else 1)
