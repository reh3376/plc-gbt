#!/bin/bash

# Git Integration Enhanced - Automated Test Runner
# Following AI Task Orchestrator methodology

echo "🚀 Git Integration Enhanced - Automated Playwright Testing"
echo "========================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Playwright is installed
if ! npx playwright --version &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Playwright...${NC}"
    npm install -D @playwright/test
    npx playwright install
fi

# Ensure dev server is running
echo -e "${YELLOW}🔍 Checking if dev server is running...${NC}"
if ! curl -s http://localhost:3000 > /dev/null; then
    echo -e "${RED}❌ Dev server not running. Please run 'npm run dev' in another terminal.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dev server is running${NC}"
echo ""

# Run the tests
echo -e "${YELLOW}🧪 Running Git Integration tests...${NC}"
echo ""

# Run specific test file
npx playwright test git-integration-enhanced-playwright.test.ts --reporter=list

# Check test results
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "📊 Test Report available at: playwright-report/index.html"
    echo "📄 JSON results at: test-results/git-integration-results.json"
else
    echo ""
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "📊 View detailed report: npx playwright show-report"
fi

# Optional: Open report automatically
read -p "Open test report in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npx playwright show-report
fi
