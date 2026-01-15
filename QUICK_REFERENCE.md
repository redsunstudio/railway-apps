# Quick Reference: What Each File Does

> **Bookmark this page!** Use it to find the right file to edit.

---

## Project Structure at a Glance

```
railway-apps/
├── 📁 apps/                    # Your actual applications
│   ├── youtube-news-scraper/   # Daily YouTube news emails
│   ├── complete-physio-weekly-summary/  # Weekly content digest
│   └── starter-app/            # Demo/test app
│
├── 📁 templates/               # Copy these to make new apps
│   ├── node-api/               # Express.js template
│   ├── python-api/             # Flask template
│   └── nextjs-app/             # Next.js template
│
├── 📁 scripts/                 # Automation scripts
├── 📁 dashboard/               # Web dashboard UI
└── 📄 (root files)             # Main app + config
```

---

## Root Level Files

### Application Files (The Code)

| File | What It Does | When to Edit |
|------|--------------|--------------|
| `app.py` | Main Flask web server, API endpoints, health checks | Adding new API routes, changing dashboard |
| `scraper.py` | Fetches news from websites/RSS feeds | Changing how content is scraped |
| `scheduler.py` | Runs tasks at scheduled times | Changing scheduling logic (prefer env vars) |
| `email_sender.py` | Sends emails via SMTP | Changing email format or SMTP settings |
| `gmail_api_sender.py` | Sends emails via Gmail API | Only if using Gmail API method |
| `news_sources.json` | List of news sources to scrape | **Adding/removing news sources** |
| `check_env.py` | Validates environment variables | Rarely - only if adding new env vars |

### Configuration Files (Don't Touch Unless Necessary)

| File | What It Does | Risk Level |
|------|--------------|------------|
| `requirements.txt` | Python dependencies | **Medium** - Edit to add packages |
| `package.json` | NPM config & scripts | **Medium** - Edit to add scripts |
| `Procfile` | How Railway runs the app | **High** - Don't touch |
| `railway.json` | Railway project settings | **High** - Don't touch |
| `railway.toml` | Railway build settings | **High** - Don't touch |
| `nixpacks.toml` | Build system config | **High** - Don't touch |
| `.gitignore` | Files Git ignores | Low - Rarely need to change |
| `.env.example` | Template for env vars | Low - Update when adding new env vars |

### Documentation Files (Safe to Edit)

| File | What It Does |
|------|--------------|
| `README.md` | Main project documentation |
| `START_HERE.md` | Entry point for new users |
| `QUICK_START.md` | Fast setup guide |
| `SIMPLE_GUIDE.md` | Non-technical guide |
| `PROJECT_OVERVIEW.md` | High-level summary |
| `CHECKLIST.md` | Progress tracking |
| `DEPLOYMENT_STATUS.md` | Current deployment state |
| `HOW_TO_DEPLOY_FIXES.md` | Fix deployment issues |
| `DEVELOPMENT_SOPS.md` | This workflow guide |

---

## YouTube News Scraper (`apps/youtube-news-scraper/`)

| File | Purpose | Common Edits |
|------|---------|--------------|
| `app.py` | Web server & API | Add endpoints, change responses |
| `scraper.py` | News fetching logic | Change scraping patterns |
| `scheduler.py` | Daily scheduling | Rarely (use env vars instead) |
| `email_sender.py` | Email formatting & sending | Change email template/style |
| `gmail_api_sender.py` | Gmail API integration | Only for API method |
| `news_sources.json` | Sources to scrape | **Add/remove/edit sources** |
| `requirements.txt` | Python packages | Add new dependencies |
| `Procfile` | Run command | Don't touch |
| `railway.toml` | Railway config | Don't touch |

### news_sources.json Structure
```json
{
  "sources": [
    {
      "name": "Source Name",
      "url": "https://example.com/feed",
      "type": "rss"  // or "html"
    }
  ]
}
```

---

## Complete Physio App (`apps/complete-physio-weekly-summary/`)

| File | Purpose | Common Edits |
|------|---------|--------------|
| `main.py` | Main application entry | Core app logic |
| `instagram_scraper.py` | Scrapes Instagram | Change IG scraping |
| `rss_parser.py` | Parses RSS feeds | Change feed handling |
| `email_formatter.py` | HTML email templates | **Change email look** |
| `email_sender.py` | Sends emails | SMTP settings |
| `scheduler.py` | Weekly scheduling | Rarely (use env vars) |
| `requirements.txt` | Python packages | Add dependencies |
| `sources.json` | Content sources | Add/remove sources |

---

## Templates (`templates/`)

### Node.js API (`templates/node-api/`)
```
node-api/
├── index.js          # Main Express server
├── package.json      # Dependencies & scripts
└── README.md         # Setup instructions
```

### Python API (`templates/python-api/`)
```
python-api/
├── app.py            # Main Flask server
├── requirements.txt  # Python dependencies
├── Procfile          # Run command
└── README.md         # Setup instructions
```

### Next.js App (`templates/nextjs-app/`)
```
nextjs-app/
├── pages/            # Page components
├── package.json      # Dependencies
└── README.md         # Setup instructions
```

---

## Scripts (`scripts/`)

| Script | What It Does | How to Run |
|--------|--------------|------------|
| `create-app.sh` | Creates new app from template | `npm run create-app` |
| `deploy-all.sh` | Deploys all apps | `npm run deploy-all` |

---

## File Types Explained

### By Extension

| Extension | Type | Editor |
|-----------|------|--------|
| `.py` | Python code | Any code editor |
| `.js` | JavaScript code | Any code editor |
| `.json` | Configuration data | Any code editor |
| `.md` | Documentation (Markdown) | Any text editor |
| `.txt` | Plain text | Any text editor |
| `.toml` | Configuration | Any text editor |
| `.sh` | Shell script | Any text editor |
| `.html` | Web page | Any code editor |
| `.env` | Environment variables | Text editor (KEEP SECRET!) |

### Special Files (No Extension)

| File | Purpose |
|------|---------|
| `Procfile` | Tells Railway how to run the app |
| `.gitignore` | Files Git should ignore |
| `.env` | Local environment variables |

---

## What to Edit for Common Tasks

### "I want to change email content"
→ Edit `email_sender.py` or `email_formatter.py`

### "I want to add a new news source"
→ Edit `news_sources.json` or `sources.json`

### "I want to change when emails are sent"
→ Update `SCHEDULE_TIME` in Railway dashboard (not code!)

### "I want to add a new Python package"
→ Add to `requirements.txt`, then redeploy

### "I want to add a new API endpoint"
→ Edit `app.py` or `main.py`

### "I want to change the web dashboard"
→ Edit `dashboard/index.html`

### "I want to create a new app"
→ Run `npm run create-app` or copy a template

---

## Color-Coded Safety Guide

```
🟢 SAFE TO EDIT
   - Documentation (.md files)
   - news_sources.json / sources.json
   - Email templates
   - Dashboard HTML

🟡 EDIT WITH CARE
   - app.py, main.py (main application)
   - scraper.py (scraping logic)
   - requirements.txt (dependencies)
   - package.json

🔴 DON'T TOUCH (unless you know what you're doing)
   - Procfile
   - railway.json / railway.toml
   - nixpacks.toml
   - .gitignore
```

---

## Quick Find Commands

```bash
# Find a file by name
find . -name "filename.py"

# Find files containing text
grep -r "search text" .

# List all Python files
find . -name "*.py"

# List all JSON files
find . -name "*.json"
```

---

*Use this as your map! When in doubt, check here first.*
