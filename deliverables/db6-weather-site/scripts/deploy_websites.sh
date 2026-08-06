#!/bin/bash
# Deploy database websites to Vercel
# This script deploys all complete website folders to Vercel

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Deploying database websites to Vercel..."
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}ERROR: Vercel CLI not found. Please install it with: npm i -g vercel${NC}"
    exit 1
fi

# Function to deploy a single website
deploy_website() {
    local db_num=$1
    local website_folder=$2
    
    echo -e "${GREEN}Deploying db-${db_num}...${NC}"
    echo "  Folder: $website_folder"
    
    cd "$website_folder"
    
    # Check if all required files exist
    if [ ! -f "db-${db_num}_documentation.html" ]; then
        echo -e "  ${YELLOW}⚠ Skipping: Missing db-${db_num}_documentation.html${NC}"
        cd "$BASE_DIR"
        return 1
    fi
    
    if [ ! -f "db-${db_num}_deliverable.json" ]; then
        echo -e "  ${YELLOW}⚠ Skipping: Missing db-${db_num}_deliverable.json${NC}"
        cd "$BASE_DIR"
        return 1
    fi
    
    if [ ! -f "vercel.json" ]; then
        echo -e "  ${YELLOW}⚠ Skipping: Missing vercel.json${NC}"
        cd "$BASE_DIR"
        return 1
    fi
    
    # Deploy to Vercel
    echo "  Deploying to Vercel..."
    if vercel --yes --prod 2>&1 | tee /tmp/vercel-deploy-${db_num}.log; then
        echo -e "  ${GREEN}✓ Successfully deployed db-${db_num}${NC}"
        # Extract deployment URL from log
        DEPLOY_URL=$(grep -o 'https://[^ ]*\.vercel\.app' /tmp/vercel-deploy-${db_num}.log | head -1)
        if [ -n "$DEPLOY_URL" ]; then
            echo "  Deployment URL: $DEPLOY_URL"
        fi
    else
        echo -e "  ${RED}✗ Failed to deploy db-${db_num}${NC}"
        cd "$BASE_DIR"
        return 1
    fi
    
    cd "$BASE_DIR"
    return 0
}

# Deploy websites for db-6 through db-15
SUCCESS_COUNT=0
SKIP_COUNT=0
FAIL_COUNT=0

for db_num in {6..15}; do
    # Find website folder
    website_folder=$(find "db-${db_num}/deliverable" -type d -name "db${db_num}-*" 2>/dev/null | head -1)
    
    if [ -z "$website_folder" ]; then
        echo -e "${YELLOW}Skipping db-${db_num}: No website folder found${NC}"
        ((SKIP_COUNT++))
        continue
    fi
    
    if deploy_website "$db_num" "$website_folder"; then
        ((SUCCESS_COUNT++))
    else
        ((FAIL_COUNT++))
    fi
    
    echo ""
done

# Summary
echo "=========================================="
echo "Deployment Summary:"
echo -e "${GREEN}Successfully deployed: ${SUCCESS_COUNT}${NC}"
echo -e "${YELLOW}Skipped: ${SKIP_COUNT}${NC}"
echo -e "${RED}Failed: ${FAIL_COUNT}${NC}"
echo "=========================================="

if [ $FAIL_COUNT -eq 0 ] && [ $SUCCESS_COUNT -gt 0 ]; then
    exit 0
else
    exit 1
fi
