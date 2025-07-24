#!/bin/bash

# Efficient Build Error Analysis Script
# Usage: ./scripts/analyze-build-errors.sh
# Purpose: Systematically analyze and categorize build errors

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p logs

# Timestamp for log files
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BUILD_LOG="logs/build-errors-$TIMESTAMP.log"
ANALYSIS_LOG="logs/error-analysis-$TIMESTAMP.log"

echo -e "${BLUE}🔍 Starting Comprehensive Build Error Analysis${NC}"
echo "=================================================="

# Step 1: Capture ALL build errors
echo -e "${YELLOW}📝 Step 1: Capturing all build errors...${NC}"
npm run build 2>&1 | tee "$BUILD_LOG"
BUILD_EXIT_CODE=${PIPESTATUS[0]}

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful! No errors to analyze.${NC}"
    exit 0
fi

echo -e "${RED}❌ Build failed. Analyzing errors...${NC}"

# Step 2: Error Pattern Analysis
echo -e "${YELLOW}📊 Step 2: Analyzing error patterns...${NC}"

{
    echo "Build Error Analysis Report"
    echo "=========================="
    echo "Timestamp: $(date)"
    echo "Build Log: $BUILD_LOG"
    echo ""

    # Count different error types
    echo "ERROR PATTERN SUMMARY:"
    echo "====================="
    
    # Type incompatibility errors
    TYPE_ERRORS=$(grep -c "is not assignable to type" "$BUILD_LOG" 2>/dev/null || echo "0")
    echo "Type Assignment Errors: $TYPE_ERRORS"
    
    # Import/Export errors  
    IMPORT_ERRORS=$(grep -c "is not exported from\|Cannot find module" "$BUILD_LOG" 2>/dev/null || echo "0")
    echo "Import/Export Errors: $IMPORT_ERRORS"
    
    # Property errors
    PROP_ERRORS=$(grep -c "Property.*does not exist" "$BUILD_LOG" 2>/dev/null || echo "0")
    echo "Property/Prop Errors: $PROP_ERRORS"
    
    # Hydration errors
    HYDRATION_ERRORS=$(grep -c "hydrated but.*didn't match" "$BUILD_LOG" 2>/dev/null || echo "0")
    echo "Hydration Errors: $HYDRATION_ERRORS"
    
    # Generic TypeScript errors
    TS_ERRORS=$(grep -c "error TS[0-9]" "$BUILD_LOG" 2>/dev/null || echo "0")
    echo "Other TypeScript Errors: $TS_ERRORS"
    
    echo ""
    echo "DETAILED ERROR BREAKDOWN:"
    echo "========================"
    
    # Extract unique error patterns
    echo ""
    echo "Type Assignment Patterns:"
    grep "is not assignable to type" "$BUILD_LOG" | sed 's/^.*src\///' | sort | uniq -c | sort -nr
    
    echo ""
    echo "Import/Export Issues:"
    grep -E "is not exported from|Cannot find module" "$BUILD_LOG" | sed 's/^.*src\///' | sort | uniq
    
    echo ""
    echo "Property Issues:"
    grep "Property.*does not exist" "$BUILD_LOG" | sed 's/^.*src\///' | sort | uniq
    
    echo ""
    echo "RECOMMENDED FIX STRATEGY:"
    echo "========================"
    
    if [ "$TYPE_ERRORS" -gt "0" ]; then
        echo "1. Fix Type Assignment Errors ($TYPE_ERRORS found):"
        echo "   - Pattern: Use String(), Boolean(), Number() conversions"
        echo "   - Files: Use parallel edit_file calls for similar patterns"
        echo "   - Example: {value || ''} → {String(value) || ''}"
        echo ""
    fi
    
    if [ "$IMPORT_ERRORS" -gt "0" ]; then
        echo "2. Fix Import/Export Errors ($IMPORT_ERRORS found):"
        echo "   - Add missing imports in single edit"
        echo "   - Install missing type definitions"
        echo "   - Check package.json dependencies"
        echo ""
    fi
    
    if [ "$PROP_ERRORS" -gt "0" ]; then
        echo "3. Fix Property Errors ($PROP_ERRORS found):"
        echo "   - Remove invalid props (style, etc.)"
        echo "   - Use className instead of style for icons"
        echo "   - Check component prop interfaces"
        echo ""
    fi
    
    if [ "$HYDRATION_ERRORS" -gt "0" ]; then
        echo "4. Fix Hydration Errors ($HYDRATION_ERRORS found) - CRITICAL:"
        echo "   - Implement useEffect + isMounted pattern"
        echo "   - Ensure SSR/client rendering consistency"
        echo "   - Priority: Fix immediately"
        echo ""
    fi
    
    echo "EXECUTION PLAN:"
    echo "==============="
    echo "1. Categorize errors by pattern (done above)"
    echo "2. Create parallel fix strategy"
    echo "3. Execute multiple edit_file calls simultaneously"
    echo "4. Run single verification build"
    echo "5. Target: Resolve in 2-3 build iterations maximum"
    
} > "$ANALYSIS_LOG"

# Display analysis
cat "$ANALYSIS_LOG"

echo ""
echo -e "${BLUE}📋 Analysis complete!${NC}"
echo -e "${GREEN}📄 Full analysis saved to: $ANALYSIS_LOG${NC}"
echo -e "${YELLOW}📄 Build log saved to: $BUILD_LOG${NC}"

echo ""
echo -e "${BLUE}🎯 Next Steps:${NC}"
echo "1. Review the error patterns above"
echo "2. Plan parallel fixes for each category"
echo "3. Execute multiple edit_file calls simultaneously"
echo "4. Run 'npm run build' to verify fixes"

# Optional: Open analysis in editor
if command -v code &> /dev/null; then
    echo ""
    echo -e "${BLUE}💡 Tip: Opening analysis in VS Code...${NC}"
    code "$ANALYSIS_LOG"
fi

exit $BUILD_EXIT_CODE 