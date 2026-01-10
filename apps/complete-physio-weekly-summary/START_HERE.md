# 🎯 Complete Physio Weekly Summary - START HERE

**Automated weekly email summaries for all Complete Physio content**

---

## ✅ What This App Does

Automatically collects and sends a **beautiful weekly email summary** every **Friday at 3 PM UK time** with:

- 📸 **Instagram posts** from @completephysio
- 🎥 **YouTube videos** from Complete Physio channel
- 📝 **Blog posts** from both Complete Physio blogs
- 📧 **Newsletters** sent via Zapier RSS feed

All formatted in a clean, professional email with:
- Summary statistics dashboard
- Direct links to all content
- Thumbnail images
- Post captions and descriptions

---

## 🚀 Quick Start

### Option 1: Follow the Step-by-Step Guide (Recommended)
👉 **Open [SETUP.md](SETUP.md)** for detailed setup instructions (15 minutes)

### Option 2: Quick Overview
👉 **Open [README.md](README.md)** for full documentation

---

## 📋 What You Need

Before starting, gather:

1. ✅ **Gmail account** (for sending emails)
2. ✅ **GitHub account** (for deployment)
3. ✅ **Railway account** (free - sign up at [railway.app](https://railway.app))
4. ✅ **Recipient email addresses** (who gets the weekly summary)

That's it!

---

## 🎯 Setup Checklist

- [ ] Set up Gmail API credentials ([SETUP.md](SETUP.md))
- [ ] Push code to GitHub
- [ ] Deploy to Railway
- [ ] Add environment variables
- [ ] Test email delivery
- [ ] Verify schedule is running

**Time needed**: 15 minutes total

---

## 📊 What Gets Included

### Sources Already Configured:
- **Instagram**: `@completephysio`
- **YouTube**: Complete Physio channel RSS
- **Blog #1**: complete-physio.co.uk
- **Blog #2**: ultrasound-guided-injections.co.uk
- **Newsletter**: Zapier RSS feed

All URLs are pre-configured! You just need to set up email sending.

---

## 📅 Schedule

**Sends**: Every Friday at 3:00 PM UK time
**Lookback**: Last 7 days of content
**Recipients**: Multiple recipients supported (comma-separated)

---

## 💰 Cost

- **Railway hosting**: ~$2-3/month (within $5 free tier)
- **Gmail API**: Free
- **Total**: **FREE** ✨

---

## 🛠️ Files Overview

```
complete-physio-weekly-summary/
│
├── START_HERE.md           ← You are here!
├── SETUP.md                ← Step-by-step setup guide
├── README.md               ← Full documentation
│
├── main.py                 ← Main application
├── instagram_scraper.py    ← Instagram posts
├── rss_parser.py          ← YouTube/Blog/Newsletter
├── email_formatter.py     ← Email template
├── email_sender.py        ← Gmail API sender
├── scheduler.py           ← Weekly scheduling
│
├── requirements.txt       ← Python dependencies
├── Procfile              ← Railway configuration
├── railway.json          ← Railway settings
├── .env.example          ← Configuration template
└── .gitignore           ← Git ignore rules
```

---

## 🎬 Next Steps

### Step 1: Read the Setup Guide
Open [SETUP.md](SETUP.md) and follow the steps.

### Step 2: Test Locally (Optional)
```bash
cd /Users/john/railway-apps/apps/complete-physio-weekly-summary
pip install -r requirements.txt
TEST_MODE=true python main.py
```

### Step 3: Deploy to Railway
Follow [SETUP.md](SETUP.md) section 5.

---

## ✨ Features

- **Fully automated** - Set it and forget it
- **Beautiful HTML emails** - Professional design with stats
- **Multiple sources** - Instagram, YouTube, Blog, Newsletter
- **Reliable** - Runs 24/7 on Railway cloud
- **Easy to customize** - Change schedule, design, or sources
- **Multiple recipients** - Send to team or clients

---

## 📞 Need Help?

1. **Setup issues**: See [SETUP.md](SETUP.md) troubleshooting section
2. **Full documentation**: See [README.md](README.md)
3. **Test locally first**: Use `TEST_MODE=true`
4. **Check Railway logs**: View in Railway dashboard

---

## 🎯 Ready?

👉 **Open [SETUP.md](SETUP.md) now** to get started!

Your first weekly summary will arrive this Friday at 3 PM UK time. 🚀

---

**Created**: January 2026
**Platform**: Railway
**Runtime**: Python 3.11
**Schedule**: Weekly (Fridays 3 PM UK)
