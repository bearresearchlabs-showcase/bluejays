#!/bin/bash

# Pre-commit hook script
# Run tests and linting before commits

set -e

echo "🔍 Running pre-commit checks..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found. Run this script from the project root.${NC}"
    exit 1
fi

# Run TypeScript check
echo "📝 Checking TypeScript..."
npx tsc --noEmit
print_status $? "TypeScript check passed"

# Run linter
echo "🔧 Running linter..."
npm run lint
print_status $? "Linter passed"

# Run tests
echo "🧪 Running tests..."
npm test -- --passWithNoTests
print_status $? "Tests passed"

# Check test coverage (warn if low, don't fail)
echo "📊 Checking test coverage..."
COVERAGE=$(npm test -- --coverage --coverageReporters=text-summary 2>&1 | grep -oP 'All files[^|]*\|\s*\K[0-9.]+' | head -1 || echo "0")
if (( $(echo "$COVERAGE < 60" | bc -l 2>/dev/null || echo "1") )); then
    echo -e "${YELLOW}⚠️  Warning: Test coverage is ${COVERAGE}% (target: 60%)${NC}"
else
    echo -e "${GREEN}✅ Test coverage: ${COVERAGE}%${NC}"
fi

echo -e "${GREEN}✨ All pre-commit checks passed!${NC}"
