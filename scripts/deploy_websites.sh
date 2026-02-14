#!/bin/bash
# Deploy database websites to Vercel — 100% coverage (db-1 through db-16)
# Runs validation before deploy. Each db-N deliverable deploys as its own Vercel project.

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=== Database Websites Deploy (100% coverage) ==="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}ERROR: Vercel CLI not found. Please install it with: npm i -g vercel${NC}"
    exit 1
fi

# Parse args
SKIP_VALIDATE=false
STATIC_MODE=false
for arg in "$@"; do
  [ "$arg" = "--skip-validate" ] && SKIP_VALIDATE=true
  [ "$arg" = "--static" ] && STATIC_MODE=true
done

# --static: deploy single prepared public/ site (100% coverage, under 2GB, uses download links for large data)
if [ "$STATIC_MODE" = "true" ]; then
  echo "Static mode: preparing and deploying public/ (all 16 databases, schema + data or download links)"
  bash "$BASE_DIR/scripts/prepare_vercel_public.sh" || { echo -e "${RED}Prepare failed${NC}"; exit 1; }
  if [ ! -d "$BASE_DIR/public" ] || [ -z "$(ls -A $BASE_DIR/public 2>/dev/null)" ]; then
    echo -e "${RED}public/ is empty. Run prepare_vercel_public.sh first.${NC}"
    exit 1
  fi
  # Create minimal vercel.json in public for static deploy (framework: null = static)
  cat > "$BASE_DIR/public/vercel.json" << 'EOF'
{"framework":null,"rewrites":[{"source":"/","destination":"/index.html"}],"headers":[{"source":"/(.*\\.html)","headers":[{"key":"Content-Type","value":"text/html"}]},{"source":"/(.*\\.json)","headers":[{"key":"Content-Type","value":"application/json"}]}]}
EOF
  # Create index if missing
  if [ ! -f "$BASE_DIR/public/index.html" ]; then
    echo '<!DOCTYPE html><html><head><title>Database Documentation</title></head><body><h1>Database Documentation</h1><ul>' > "$BASE_DIR/public/index.html"
    for d in "$BASE_DIR"/public/db-*/; do [ -d "$d" ] && n=$(basename "$d") && echo "<li><a href=\"/${n}/${n}_documentation.html\">${n}</a></li>" >> "$BASE_DIR/public/index.html"; done
    echo '</ul></body></html>' >> "$BASE_DIR/public/index.html"
  fi
  cd "$BASE_DIR/public"
  vercel --yes --prod && echo -e "${GREEN}Static deploy complete.${NC}" || exit 1
  exit 0
fi

# Pre-deploy: validate all databases (optional, can skip with --skip-validate)

if [ "$SKIP_VALIDATE" = "false" ]; then
  echo "Validating all databases (db-1 through db-16)..."
  FAILED=0
  for n in $(seq 1 16); do
    if python3 scripts/db_check.py validate "$n" 2>/dev/null | grep -q "PASS"; then
      echo -e "  ${GREEN}db-${n}: PASS${NC}"
    else
      echo -e "  ${RED}db-${n}: FAIL${NC}"
      FAILED=$((FAILED + 1))
    fi
  done
  if [ "$FAILED" -gt 0 ]; then
    echo -e "${RED}Validation failed for $FAILED database(s). Fix before deploy or use --skip-validate${NC}"
    exit 1
  fi
  echo -e "${GREEN}All 16 databases validated.${NC}"
  echo ""
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

# Deploy websites for db-1 through db-16 (100% coverage)
SUCCESS_COUNT=0
SKIP_COUNT=0
FAIL_COUNT=0

for db_num in $(seq 1 16); do
    # Find website folder: source/db-N or db-N at root
    website_folder=""
    for base in "source/db-${db_num}" "db-${db_num}"; do
      [ -d "$base" ] || continue
      found=$(find "$base/deliverable" -type d -name "db${db_num}-*" 2>/dev/null | head -1)
      [ -n "$found" ] && website_folder="$found" && break
    done

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
