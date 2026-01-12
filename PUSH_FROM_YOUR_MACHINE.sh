#!/bin/bash
#
# FINAL DEPLOYMENT INSTRUCTIONS
# Run this from YOUR local machine (not Claude's environment)
#

echo "════════════════════════════════════════════════════════"
echo "  YouTube Scraper - Deploy Claude's Fixes"
echo "════════════════════════════════════════════════════════"
echo ""
echo "STATUS: Claude has merged all fixes locally but cannot"
echo "        push to GitHub due to git proxy restrictions."
echo ""
echo "SOLUTION: You need to push from your machine where you"
echo "          have proper GitHub credentials."
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

cat << 'EOF'

OPTION 1: Push the existing local main branch
----------------------------------------------
If you're in the Claude Code environment with a terminal:

cd /home/user/railway-apps
git push origin main

The local main branch already has all fixes merged!


OPTION 2: Pull and push from your own machine
----------------------------------------------
If you're on your own computer:

cd ~/railway-apps  # or wherever your repo is
git fetch origin
git checkout main
git pull origin main
git push origin main


OPTION 3: Via GitHub Web UI
----------------------------
1. Go to: https://github.com/redsunstudio/railway-apps
2. Click "Pull requests"
3. Click "New pull request"
4. Base: main
5. Compare: claude/fix-scraper-email-notification-Pf0Ow
6. Click "Create pull request"
7. Click "Merge pull request"


WHAT HAPPENS AFTER PUSH:
-------------------------
1. Railway detects push to main
2. Builds new version (30-60 seconds)
3. Deploys automatically
4. App restarts with version 1.2.1


HOW TO VERIFY DEPLOYMENT:
--------------------------
# Wait 60 seconds after push, then:

curl https://cheerful-serenity-production-3e99.up.railway.app/health

# Should show: "version": "1.2.1"


CHECK DIAGNOSTICS:
------------------
curl https://cheerful-serenity-production-3e99.up.railway.app/api/diagnostics

This will show:
- Which env vars are SET vs NOT SET
- Email sender configuration
- Scheduler status
- Why the 0700 email failed


VIEW LOGS:
----------
curl https://cheerful-serenity-production-3e99.up.railway.app/api/logs?limit=100

Look for:
- "❌ CRITICAL: Error starting scheduler" (shows exact error)
- "Using Gmail API for email sending" (confirms email method)
- "Next scheduled run: 2026-01-13 07:00:00" (confirms schedule)


TEST EMAIL:
-----------
curl -X POST https://cheerful-serenity-production-3e99.up.railway.app/api/test-email \
  -H "Content-Type: application/json" -d '{}'


═══════════════════════════════════════════════════════════════

COMMITS READY TO DEPLOY (10 total):
-----------------------------------
aa87b49 - Fix critical logger bug + enhanced scheduler logging
c3b7372 - Bump version to 1.2.0
4c01e38 - Add logging and diagnostics endpoints
0815a6f - Add environment checker script
ce7e6f0 - Improve diagnostics endpoint (v1.2.1)
91728cc - Add deployment status documentation
48502be - Add one-command merge and deploy script
f9da9a4 - Add comprehensive deployment guide
06ac53e - Merge commit (all fixes)

FILES CHANGED:
--------------
- apps/youtube-news-scraper/app.py (logger fix, diagnostics)
- apps/youtube-news-scraper/scheduler.py (enhanced logging)
- apps/youtube-news-scraper/check_env.py (new validator)
- DEPLOYMENT_STATUS.md (technical analysis)
- HOW_TO_DEPLOY_FIXES.md (deployment guide)
- merge-and-deploy.sh (deployment script)

═══════════════════════════════════════════════════════════════

After deployment, the diagnostics will tell you EXACTLY why
the 0700 email didn't send and what needs to be fixed.

EOF
