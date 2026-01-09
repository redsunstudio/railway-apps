#!/bin/bash

# Railway App Creation Script
# Usage: ./create-app.sh <app-name> <template>
# Example: ./create-app.sh my-api node-api

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if app name is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: App name is required${NC}"
    echo "Usage: ./create-app.sh <app-name> <template>"
    echo "Available templates: node-api, python-api, nextjs-app"
    exit 1
fi

# Check if template is provided
if [ -z "$2" ]; then
    echo -e "${RED}Error: Template is required${NC}"
    echo "Available templates: node-api, python-api, nextjs-app"
    exit 1
fi

APP_NAME=$1
TEMPLATE=$2
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_PATH="$PROJECT_ROOT/templates/$TEMPLATE"
APP_PATH="$PROJECT_ROOT/apps/$APP_NAME"

# Check if template exists
if [ ! -d "$TEMPLATE_PATH" ]; then
    echo -e "${RED}Error: Template '$TEMPLATE' not found${NC}"
    echo "Available templates:"
    ls -1 "$PROJECT_ROOT/templates"
    exit 1
fi

# Check if app already exists
if [ -d "$APP_PATH" ]; then
    echo -e "${RED}Error: App '$APP_NAME' already exists${NC}"
    exit 1
fi

echo -e "${GREEN}Creating new app: $APP_NAME${NC}"
echo -e "Using template: ${YELLOW}$TEMPLATE${NC}"

# Copy template to apps directory
cp -r "$TEMPLATE_PATH" "$APP_PATH"

echo -e "${GREEN}✓ App created successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. cd apps/$APP_NAME"
echo "2. Install dependencies:"

if [ "$TEMPLATE" == "node-api" ] || [ "$TEMPLATE" == "nextjs-app" ]; then
    echo "   npm install"
elif [ "$TEMPLATE" == "python-api" ]; then
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
fi

echo "3. Test locally:"
if [ "$TEMPLATE" == "node-api" ]; then
    echo "   npm run dev"
elif [ "$TEMPLATE" == "python-api" ]; then
    echo "   python app.py"
elif [ "$TEMPLATE" == "nextjs-app" ]; then
    echo "   npm run dev"
fi

echo "4. Deploy to Railway:"
echo "   railway init"
echo "   railway up"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
