# File Explorer Sorting Enhancement Test Plan

## Two-Phase Testing Protocol Implementation

### **Phase 1: Automated Testing with Playwright MCP** ⚡
**Required Success Rate: ≥95%**

### **Test Categories**

#### **1. Component Interaction Tests**
- **Sort Dropdown Functionality**
  - Click sort dropdown trigger button
  - Verify dropdown opens with correct options
  - Select each sort option (Files First, Folders First, A-Z, Z-A, Date)
  - Verify dropdown closes after selection
  - Verify selected option is highlighted

- **Keyboard Navigation**
  - Tab to sort dropdown
  - Use arrow keys to navigate options
  - Use Enter/Space to select options
  - Use Escape to close dropdown

#### **2. File Sorting Validation Tests**
- **Files First Sorting (Default)**
  - Verify files appear before folders
  - Verify files are alphabetically sorted
  - Verify folders are alphabetically sorted after files

- **Folders First Sorting**
  - Verify folders appear before files
  - Verify folders are alphabetically sorted
  - Verify files are alphabetically sorted after folders

- **A-Z Sorting**
  - Verify all items sorted alphabetically regardless of type
  - Verify proper case-insensitive sorting

- **Z-A Sorting**
  - Verify all items sorted reverse alphabetically
  - Verify proper case-insensitive reverse sorting

- **Date Sorting**
  - Verify items sorted by modification date (newest first)
  - Verify fallback to alphabetical for same dates

#### **3. Hierarchical Structure Tests**
- **Nested Folder Sorting**
  - Expand folders with children
  - Verify children are sorted according to selected option
  - Verify sort option applies recursively to all levels

- **Mixed Content Folders**
  - Test folders containing both files and subfolders
  - Verify correct sorting within each folder level

#### **4. UI State Management Tests**
- **Sort State Persistence**
  - Change sort option
  - Refresh file tree
  - Verify sort option is maintained

- **Sort Indicator Display**
  - Verify correct icon displays for selected sort option
  - Verify tooltip shows correct sort description

#### **5. Integration Tests**
- **File Operations Integration**
  - Create new file/folder
  - Verify new item appears in correct sorted position
  - Rename file/folder
  - Verify renamed item moves to correct position

- **Loading State Integration**
  - Verify sort dropdown is disabled during loading
  - Verify sort is applied after loading completes

### **Automated Test Implementation Plan**

#### **Component Tests** (Target: 99% success rate)
```typescript
// Test sort dropdown basic functionality
test('sort dropdown - basic interaction', async ({ page }) => {
  await page.click('[data-testid="sort-dropdown-trigger"]');
  await page.waitForSelector('[role="listbox"]');
  await page.click('[data-testid="sort-option-folders-first"]');
  await expect(page.locator('[data-testid="sort-dropdown-trigger"]')).toContainText('Folders First');
});
```

#### **E2E Workflow Tests** (Target: 95% success rate)
```typescript
// Test complete sorting workflow
test('file sorting - complete workflow', async ({ page }) => {
  // Test default files-first sorting
  await verifyFilesSortedAsFilesFirst(page);
  
  // Change to folders-first
  await page.click('[data-testid="sort-dropdown-trigger"]');
  await page.click('[data-testid="sort-option-folders-first"]');
  await verifyFilesSortedAsFoldersFirst(page);
  
  // Test alphabetical sorting
  await page.click('[data-testid="sort-dropdown-trigger"]');
  await page.click('[data-testid="sort-option-a-z"]');
  await verifyFilesSortedAlphabetically(page);
});
```

#### **Accessibility Tests** (Target: 95% success rate)
```typescript
// Test keyboard navigation
test('sort dropdown - keyboard accessibility', async ({ page }) => {
  await page.keyboard.press('Tab'); // Focus sort dropdown
  await page.keyboard.press('Enter'); // Open dropdown
  await page.keyboard.press('ArrowDown'); // Navigate to first option
  await page.keyboard.press('Enter'); // Select option
  await expect(page.locator('[role="listbox"]')).not.toBeVisible();
});
```

#### **Performance Tests** (Target: Core Web Vitals Green)
```typescript
// Test sorting performance with large file sets
test('sort performance - large file set', async ({ page }) => {
  const startTime = Date.now();
  await page.click('[data-testid="sort-dropdown-trigger"]');
  await page.click('[data-testid="sort-option-a-z"]');
  const endTime = Date.now();
  expect(endTime - startTime).toBeLessThan(100); // Should sort within 100ms
});
```

### **Expected Test Results**

| Test Category | Expected Success Rate | Key Metrics |
|---------------|----------------------|-------------|
| Component Tests | 99% | All dropdown interactions work |
| E2E Workflow Tests | 95% | Complete sorting workflows pass |
| Accessibility Tests | 95% | Keyboard navigation functional |
| Performance Tests | 95% | Sorting completes <100ms |
| Cross-browser Tests | 90% | Works in Chrome, Firefox, Safari |

### **Phase 2: User Interactive Testing** 👤
**Required Success Rate: 100%**

#### **User Testing Checklist**

1. **Basic Functionality**
   - [ ] Sort dropdown opens when clicked
   - [ ] All 5 sort options are available
   - [ ] Selected option is visually highlighted
   - [ ] Dropdown closes after selection

2. **Sorting Accuracy**
   - [ ] Files First: Files appear before folders, both alphabetical
   - [ ] Folders First: Folders appear before files, both alphabetical  
   - [ ] A-Z: All items sorted alphabetically regardless of type
   - [ ] Z-A: All items sorted reverse alphabetically
   - [ ] Date: Items sorted by modification date (newest first)

3. **Hierarchical Behavior**
   - [ ] Sorting applies to all folder levels
   - [ ] Expanding folders shows correctly sorted children
   - [ ] New files/folders appear in correct sorted position

4. **User Experience**
   - [ ] Sort icon is intuitive and recognizable
   - [ ] Dropdown feels responsive and smooth
   - [ ] Sort changes are immediate and visible
   - [ ] No performance lag with large file sets

5. **Accessibility**
   - [ ] Can navigate dropdown with keyboard only
   - [ ] Screen reader announces sort options correctly
   - [ ] Focus management works properly
   - [ ] Tooltips provide helpful information

### **Success Criteria**

**Automated Testing**: ≥95% overall success rate across all test categories
**User Testing**: 100% validation of all checklist items

**Only after BOTH phases pass successfully can the File Explorer sorting enhancement be marked as complete.**
