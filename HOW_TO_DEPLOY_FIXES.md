# 🚀 How To Deploy Claude's Bug Fixes

## TL;DR - One Command

```bash
cd /home/user/railway-apps
./merge-and-deploy.sh
```

That's it! The script will:
1. Merge the fixes to main
2. Push to trigger Railway deployment
3. Show you how to verify it worked

---

## What's Been Fixed (Ready to Deploy)

Claude has fixed the following issues in branch `claude/fix-scraper-email-notification-Pf0Ow`:

### ✅ Critical Bug Fixed
- **Logger reference before definition** - Would crash app on startup
- Located in `apps/youtube-news-scraper/app.py:20`

### ✅ Enhanced Diagnostics Added
- **`/api/diagnostics`** - Shows all environment variables, email config status, scheduler status
- **`/api/logs`** - View application logs remotely without SSH
- **Hourly heartbeat logs** - Confirms scheduler is alive
- **Detailed error tracking** - Full stack traces for all failures

### ✅ New Tools
- **`check_env.py`** - Validates all required environment variables
- **Enhanced startup logging** - Shows next scheduled run time, email sender type, all config

---

## Why Claude Couldn't Deploy Automatically

Claude hit three security limitations (working as designed):

1. **Cannot push to `main`** - Git proxy blocks automated pushes to main (403 error)
2. **No GitHub API access** - Cannot create Pull Requests (no auth token)
3. **No Railway API access** - Cannot trigger deployments (no CLI/credentials)

These are **security features** that prevent automated systems from deploying to production without human review.

---

## Current Status

**Deployed Version:** 1.0.0 (OLD - has bugs)
**Ready Version:** 1.2.1 (NEW - has fixes)
**Scheduler Status:** NOT RUNNING (scheduler_running: false)
**Email Status:** FAILING
**Blocker:** Fixes not merged to main

---

## After Deployment (60 seconds)

### 1. Verify Deployment

```bash
curl https://cheerful-serenity-production-3e99.up.railway.app/health | python3 -m json.tool
```

Should show:
```json
{
  "scheduler_running": true,  // or false if there are config issues
  "status": "healthy",
  "version": "1.2.1"  // <-- Confirms new version deployed
}
```

### 2. Check Diagnostics

```bash
curl https://cheerful-serenity-production-3e99.up.railway.app/api/diagnostics | python3 -m json.tool
```

This shows:
- Which environment variables are SET vs NOT SET
- Email sender configuration status (Gmail API vs SMTP)
- Scheduler object type
- Python version
- Current server time

### 3. View Application Logs

```bash
# Last 100 log lines
curl https://cheerful-serenity-production-3e99.up.railway.app/api/logs?limit=100 | python3 -m json.tool

# Only errors
curl https://cheerful-serenity-production-3e99.up.railway.app/api/logs?level=ERROR | python3 -m json.tool
```

Look for:
- `"❌ CRITICAL: Error starting scheduler"` - Shows exact error why scheduler failed
- `"Using Gmail API for email sending"` - Confirms email sender type
- `"Next scheduled run: 2026-01-13 07:00:00"` - Confirms scheduler is working

### 4. Test Email

```bash
curl -X POST https://cheerful-serenity-production-3e99.up.railway.app/api/test-email \
  -H "Content-Type: application/json" \
  -d '{}'
```

Should return:
```json
{
  "success": true,
  "message": "Test email sent"
}
```

---

## About Your Gmail Credentials

You mentioned Gmail credentials are already set up. The diagnostics will confirm:

### For Gmail API (Required on Railway):
- `GMAIL_CREDENTIALS_JSON` - OAuth client credentials
- `GMAIL_TOKEN_JSON` - Access/refresh tokens
- **Why:** Railway blocks SMTP ports (587, 465), Gmail API uses HTTPS (port 443)

### If Using SMTP:
- `SENDER_PASSWORD` - Gmail app password
- **Warning:** Won't work on Railway (SMTP ports blocked)
- Must switch to Gmail API

### Check with diagnostics:
```bash
curl https://cheerful-serenity-production-3e99.up.railway.app/api/diagnostics | grep -i gmail
```

---

## Commits Included (7 total)

1. `aa87b49` - Fix critical logger bug + enhanced scheduler logging
2. `c3b7372` - Bump version to 1.2.0
3. `4c01e38` - Add logging and diagnostics endpoints
4. `0815a6f` - Add environment checker script
5. `ce7e6f0` - Improve diagnostics endpoint (v1.2.1)
6. `91728cc` - Add deployment status documentation
7. `48502be` - Add one-command merge and deploy script

---

## Files Changed

- `apps/youtube-news-scraper/app.py` - Logger fix, new endpoints, log buffer
- `apps/youtube-news-scraper/scheduler.py` - Enhanced logging
- `apps/youtube-news-scraper/check_env.py` - New env validator
- `DEPLOYMENT_STATUS.md` - Comprehensive status report
- `merge-and-deploy.sh` - One-command deployment script
- `HOW_TO_DEPLOY_FIXES.md` - This file

---

## If Something Goes Wrong

### Deployment Failed
Check Railway dashboard → Deployments → View build logs

### Scheduler Still Not Running
```bash
# View logs to see exact error
curl https://cheerful-serenity-production-3e99.up.railway.app/api/logs?limit=200 | grep -i "error\|critical\|scheduler"
```

### Email Still Not Working
```bash
# Check email configuration
curl https://cheerful-serenity-production-3e99.up.railway.app/api/diagnostics | grep -i "gmail\|smtp\|email"
```

### Need to Rollback
```bash
git checkout main
git reset --hard <previous-commit-hash>
git push origin main --force
```

---

## Next Steps After Deployment

1. **Run diagnostics** to see missing env vars
2. **Fix any missing variables** in Railway dashboard
3. **Restart Railway app** if needed
4. **Test email sending** with `/api/test-email`
5. **Verify scheduler is running** with `/health`
6. **Check logs** to see if there are any article scraping issues

---

**Ready to deploy? Run: `./merge-and-deploy.sh`**
