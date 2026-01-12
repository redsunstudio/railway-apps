#!/bin/bash
#
# Merge claude's fixes and trigger Railway deployment
# Run this from anywhere: ./merge-and-deploy.sh
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  YouTube Scraper - Deploy Bug Fixes${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📋 What this script will do:${NC}"
echo "  1. Checkout main branch"
echo "  2. Merge claude/fix-scraper-email-notification-Pf0Ow"
echo "  3. Push to origin main"
echo "  4. Railway will auto-deploy (60 seconds)"
echo "  5. Show you how to check the deployment"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Aborted.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 1: Fetching latest changes...${NC}"
git fetch origin

echo -e "${YELLOW}Step 2: Checking out main...${NC}"
git checkout main

echo -e "${YELLOW}Step 3: Pulling latest main...${NC}"
git pull origin main

echo -e "${YELLOW}Step 4: Merging bug fixes...${NC}"
git merge claude/fix-scraper-email-notification-Pf0Ow -m "Merge claude's fixes: Logger bug, diagnostics, enhanced logging"

echo -e "${YELLOW}Step 5: Pushing to main...${NC}"
git push origin main

echo ""
echo -e "${GREEN}✅ SUCCESS! Merge complete and pushed to main.${NC}"
echo ""
echo -e "${YELLOW}⏳ Railway is now deploying... (takes ~60 seconds)${NC}"
echo ""
echo -e "${BLUE}📊 Check deployment status:${NC}"
echo ""
echo "  # Wait 60 seconds, then check version:"
echo "  curl https://cheerful-serenity-production-3e99.up.railway.app/health"
echo ""
echo "  # Should show: \"version\": \"1.2.1\""
echo ""
echo -e "${BLUE}🔍 After deployment, run diagnostics:${NC}"
echo ""
echo "  # See all environment variables:"
echo "  curl https://cheerful-serenity-production-3e99.up.railway.app/api/diagnostics"
echo ""
echo "  # View application logs:"
echo "  curl https://cheerful-serenity-production-3e99.up.railway.app/api/logs?limit=50"
echo ""
echo -e "${BLUE}📧 Test email sending:${NC}"
echo ""
echo "  curl -X POST https://cheerful-serenity-production-3e99.up.railway.app/api/test-email \\"
echo "    -H 'Content-Type: application/json' -d '{}'"
echo ""
echo -e "${GREEN}Done! The diagnostics will show you exactly what's wrong with the email config.${NC}"
echo ""
