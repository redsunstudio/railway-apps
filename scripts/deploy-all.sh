#!/bin/bash

# Deploy all apps to Railway
# Usage: ./deploy-all.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
APPS_DIR="$PROJECT_ROOT/apps"

echo -e "${GREEN}Deploying all Railway apps...${NC}"
echo ""

# Check if apps directory exists
if [ ! -d "$APPS_DIR" ]; then
    echo "No apps directory found. Create some apps first!"
    exit 1
fi

# Count apps
APP_COUNT=$(ls -1 "$APPS_DIR" | wc -l | tr -d ' ')

if [ "$APP_COUNT" -eq 0 ]; then
    echo "No apps found in apps/ directory"
    exit 0
fi

echo "Found $APP_COUNT app(s)"
echo ""

# Deploy each app
for app_dir in "$APPS_DIR"/*; do
    if [ -d "$app_dir" ]; then
        app_name=$(basename "$app_dir")
        echo -e "${YELLOW}Deploying: $app_name${NC}"

        cd "$app_dir"

        # Check if railway is initialized
        if [ ! -f ".railway/config.json" ] && [ ! -f "railway.json" ]; then
            echo "  ⚠️  Railway not initialized for $app_name"
            echo "  Run: cd apps/$app_name && railway init"
        else
            railway up
            echo -e "${GREEN}  ✓ Deployed $app_name${NC}"
        fi

        echo ""
    fi
done

echo -e "${GREEN}All deployments complete! 🚀${NC}"
