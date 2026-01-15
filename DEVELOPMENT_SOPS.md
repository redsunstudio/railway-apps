# Development SOPs (Standard Operating Procedures)

> **For Beginners**: This guide tells you exactly what to do, step-by-step. Just follow the commands!

---

## Table of Contents
1. [Daily Workflow](#1-daily-workflow)
2. [Creating a New App](#2-creating-a-new-app)
3. [Editing an Existing App](#3-editing-an-existing-app)
4. [Deployment Checklist](#4-deployment-checklist)
5. [Environment Variables](#5-environment-variables)
6. [Git Workflow](#6-git-workflow)
7. [Common Commands Cheatsheet](#7-common-commands-cheatsheet)

---

## 1. Daily Workflow

### Starting Your Day
```bash
# 1. Open terminal and navigate to project
cd ~/railway-apps

# 2. Make sure you have latest code
git pull origin main

# 3. Check status
git status
```

### Making Changes (The Safe Way)
```bash
# 1. Create a new branch for your changes
git checkout -b my-new-feature

# 2. Make your changes to files...

# 3. Test locally (see LOCAL_TESTING.md)

# 4. Save your changes
git add .
git commit -m "Describe what you changed"

# 5. Push to GitHub
git push -u origin my-new-feature

# 6. Railway auto-deploys from GitHub!
```

### End of Day
```bash
# Always commit your work
git add .
git commit -m "WIP: what I was working on"
git push
```

---

## 2. Creating a New App

### Option A: Use the Script (Easiest)
```bash
# Run the create-app script
npm run create-app

# Follow the prompts:
# - Enter app name (e.g., "my-cool-app")
# - Choose template (node-api, python-api, or nextjs-app)
```

### Option B: Manual Creation
```bash
# 1. Copy a template
cp -r templates/python-api apps/my-new-app

# 2. Navigate to your new app
cd apps/my-new-app

# 3. Update the app name in package.json or requirements.txt

# 4. Create Railway project (in Railway dashboard)
#    - Go to railway.app
#    - New Project > Deploy from GitHub repo
#    - Set root directory to: apps/my-new-app
```

### After Creating
- [ ] Update README.md with your app description
- [ ] Add environment variables in Railway dashboard
- [ ] Test the deployment

---

## 3. Editing an Existing App

### Before You Edit - STOP and Check!

| What You Want to Do | File to Edit |
|---------------------|--------------|
| Change scraping logic | `scraper.py` |
| Change email content/format | `email_sender.py` or `email_formatter.py` |
| Change schedule time | `scheduler.py` OR Railway env var `SCHEDULE_TIME` |
| Add new news source | `news_sources.json` |
| Change API endpoints | `app.py` or `main.py` |
| Add new dependency | `requirements.txt` (Python) or `package.json` (Node) |

### Safe Editing Process

```bash
# 1. Navigate to the app
cd apps/youtube-news-scraper  # or whichever app

# 2. Create a backup branch
git checkout -b backup-before-changes
git checkout -b my-changes

# 3. Make your edits

# 4. Test locally first!
python app.py  # or npm start

# 5. If it works, commit and push
git add .
git commit -m "Changed X to do Y"
git push -u origin my-changes
```

### DO NOT Edit These Files (Unless You Know What You're Doing)
- `Procfile` - Controls how Railway runs your app
- `railway.json` / `railway.toml` - Railway configuration
- `nixpacks.toml` - Build configuration
- `.gitignore` - Git settings

---

## 4. Deployment Checklist

### Before Deploying
- [ ] Code runs locally without errors
- [ ] All required environment variables are set in Railway
- [ ] No secrets/passwords in code (use env vars!)
- [ ] Changes are committed to git

### Deployment Steps
```bash
# 1. Commit all changes
git add .
git commit -m "Ready for deployment: description"

# 2. Push to main branch (auto-deploys)
git checkout main
git merge my-changes
git push origin main

# 3. Monitor in Railway dashboard
#    - Check build logs
#    - Check deploy logs
#    - Verify app is running
```

### After Deploying
- [ ] Check Railway dashboard for green status
- [ ] Test the live URL
- [ ] Check logs for errors: Railway Dashboard > Your App > Logs

### If Deployment Fails
1. Check build logs in Railway
2. Common issues:
   - Missing dependency in requirements.txt
   - Syntax error in code
   - Missing environment variable
3. See TROUBLESHOOTING.md for fixes

---

## 5. Environment Variables

### What Are They?
Environment variables store secrets and configuration outside your code. Never put passwords in code!

### Where to Set Them

| Location | When to Use |
|----------|-------------|
| Railway Dashboard | Production (live app) |
| `.env` file locally | Local development |
| `.env.example` | Template for others (NO real values!) |

### Setting in Railway
1. Go to [railway.app](https://railway.app)
2. Select your project
3. Click on your service
4. Go to "Variables" tab
5. Add variables one by one OR use "Raw Editor"

### Common Variables for Your Apps

**YouTube News Scraper:**
```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=where-to-send@example.com
SCHEDULE_TIME=07:00
USE_GMAIL_API=false
```

**Complete Physio App:**
```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAILS=email1@example.com,email2@example.com
SCHEDULE_DAY=friday
SCHEDULE_TIME=15:00
```

### Creating Local .env File
```bash
# 1. Copy the example
cp .env.example .env

# 2. Edit with your values
nano .env  # or use any text editor

# 3. NEVER commit .env to git!
#    (it's already in .gitignore)
```

---

## 6. Git Workflow

### Basic Commands You Need

```bash
# Check what's changed
git status

# See what branch you're on
git branch

# Switch to main branch
git checkout main

# Create new branch
git checkout -b branch-name

# Save changes
git add .
git commit -m "Your message"

# Push to GitHub
git push -u origin branch-name

# Get latest code
git pull origin main
```

### The Golden Rules

1. **Never work directly on `main`** - Always create a branch
2. **Commit often** - Small commits are easier to undo
3. **Write clear commit messages** - Future you will thank you
4. **Pull before you push** - Avoid conflicts

### If You Mess Up

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes (CAREFUL!)
git checkout -- .

# Go back to main and start fresh
git checkout main
git pull origin main
```

---

## 7. Common Commands Cheatsheet

### Navigation
```bash
cd ~/railway-apps          # Go to project root
cd apps/youtube-news-scraper   # Go to specific app
cd ..                      # Go up one folder
ls                         # List files
pwd                        # Show current location
```

### Python Apps
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Run with environment variables
python -c "from dotenv import load_dotenv; load_dotenv()" && python app.py
```

### Node.js Apps
```bash
# Install dependencies
npm install

# Run locally
npm start

# Run in development mode (auto-reload)
npm run dev
```

### Git (Most Used)
```bash
git status                 # What's changed?
git add .                  # Stage all changes
git commit -m "message"    # Save changes
git push                   # Upload to GitHub
git pull                   # Download from GitHub
```

### Railway CLI (Optional)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up

# View logs
railway logs
```

---

## Quick Decision Tree

```
I want to...
│
├─► Add a new feature to existing app
│   └─► See "Editing an Existing App" section
│
├─► Create a brand new app
│   └─► See "Creating a New App" section
│
├─► Fix a bug
│   └─► 1. Create branch
│       2. Fix the code
│       3. Test locally
│       4. Commit & push
│
├─► Change when emails are sent
│   └─► Update SCHEDULE_TIME in Railway dashboard
│
├─► Add a new news source
│   └─► Edit news_sources.json
│
├─► Something is broken!
│   └─► See TROUBLESHOOTING.md
│
└─► I don't know what to do
    └─► Ask for help! Create a GitHub issue
```

---

## Need More Help?

- **QUICK_REFERENCE.md** - What each file does
- **LOCAL_TESTING.md** - How to test before deploying
- **TROUBLESHOOTING.md** - Common problems & solutions
- **README.md** - Project overview

---

*Last updated: January 2026*
