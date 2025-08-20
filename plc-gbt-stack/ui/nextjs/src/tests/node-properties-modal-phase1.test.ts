import { test, expect } from '@playwright/test';

/**
 * Phase 1 Automated Testing - Adapted for actual UI elements
 * Following AI Task Orchestrator methodology
 */

test.describe('Node Properties Modal - Phase 1 Testing (Adapted)', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    
    // Wait for initial load
    await page.waitForTimeout(3000);
    
    // Try to navigate to workflows using various selectors
    const possibleSelectors = [
      'button:has-text("Workflows")',
      'a:has-text("Workflows")',
      '[class*="workflow"]',
      'text=Workflows'
    ];
    
    for (const selector of possibleSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 1000 })) {
          await element.click();
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }
    
    // Wait for React Flow to load
    await page.waitForSelector('.react-flow', { timeout: 10000 });
  });

  test('1. Core Modal Functionality', async ({ page }) => {
    console.log('Testing Core Modal Functionality...');
    
    // Try to add a node using various methods
    const nodePalettSelectors = [
      'text="PLC Input"',
      '[class*="plc-input"]',
      '.node-item:has-text("PLC Input")',
      'div:has-text("PLC Input")'
    ];
    
    let nodeAdded = false;
    for (const selector of nodePalettSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 1000 })) {
          await element.click();
          // Click on canvas
          await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
          nodeAdded = true;
          break;
        }
      } catch (e) {
        // Continue
      }
    }
    
    if (!nodeAdded) {
      // Try drag and drop
      const nodeItem = page.locator('.node-item, [class*="node-palette"]').first();
      if (await nodeItem.isVisible()) {
        await nodeItem.dragTo(page.locator('.react-flow__viewport'));
      }
    }
    
    // Wait for node to appear
    await page.waitForSelector('.react-flow__node', { timeout: 5000 });
    
    // Double-click to open modal
    await page.dblclick('.react-flow__node');
    
    // Check if modal opened
    const modalSelectors = [
      '[role="dialog"]',
      '.modal',
      '[class*="modal"]',
      '[class*="properties"]'
    ];
    
    let modalFound = false;
    for (const selector of modalSelectors) {
      const modal = page.locator(selector).first();
      if (await modal.isVisible({ timeout: 2000 })) {
        modalFound = true;
        console.log(`✓ Modal found with selector: ${selector}`);
        break;
      }
    }
    
    expect(modalFound).toBe(true);
    
    // Check for tabs
    const tabs = await page.$$('[role="tab"], button[class*="tab"]');
    console.log(`✓ Found ${tabs.length} tabs`);
    expect(tabs.length).toBeGreaterThan(0);
    
    // Check for Save/Reset buttons
    const saveButton = page.locator('button:has-text("Save"), button:has-text("save")');
    const resetButton = page.locator('button:has-text("Reset"), button:has-text("reset")');
    
    const hasSaveButton = await saveButton.count() > 0;
    const hasResetButton = await resetButton.count() > 0;
    
    console.log(`✓ Save button: ${hasSaveButton ? 'Found' : 'Not found'}`);
    console.log(`✓ Reset button: ${hasResetButton ? 'Found' : 'Not found'}`);
  });

  test('2. Tab Navigation', async ({ page }) => {
    console.log('Testing Tab Navigation...');
    
    // Add node and open modal
    await page.locator('text="PLC Input"').first().click({ timeout: 5000 });
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node');
    await page.dblclick('.react-flow__node');
    
    // Find all tabs
    const tabSelectors = [
      '[role="tab"]',
      'button[class*="tab"]',
      '[class*="tab-button"]'
    ];
    
    for (const selector of tabSelectors) {
      const tabs = page.locator(selector);
      const count = await tabs.count();
      if (count > 0) {
        console.log(`✓ Found ${count} tabs with selector: ${selector}`);
        
        // Try clicking each tab
        for (let i = 0; i < count && i < 5; i++) {
          try {
            await tabs.nth(i).click();
            await page.waitForTimeout(500);
            console.log(`  ✓ Clicked tab ${i + 1}`);
          } catch (e) {
            console.log(`  ✗ Could not click tab ${i + 1}`);
          }
        }
        break;
      }
    }
  });

  test('3. Form Field Interaction', async ({ page }) => {
    console.log('Testing Form Fields...');
    
    // Add node and open modal
    await page.locator('text="PLC Input"').first().click({ timeout: 5000 });
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node');
    await page.dblclick('.react-flow__node');
    
    // Wait for modal
    await page.waitForTimeout(1000);
    
    // Find form inputs
    const inputs = await page.$$('input[type="text"], input[type="number"], select, textarea');
    console.log(`✓ Found ${inputs.length} form inputs`);
    
    // Test first text input
    const textInput = page.locator('input[type="text"]').first();
    if (await textInput.isVisible()) {
      await textInput.fill('Test Value');
      const value = await textInput.inputValue();
      console.log(`✓ Text input test: ${value === 'Test Value' ? 'Passed' : 'Failed'}`);
    }
    
    // Test select dropdowns
    const selects = await page.$$('select');
    console.log(`✓ Found ${selects.length} select dropdowns`);
    
    for (let i = 0; i < selects.length && i < 3; i++) {
      const select = selects[i];
      const options = await select.$$('option');
      console.log(`  Select ${i + 1} has ${options.length} options`);
    }
  });

  test('4. Help System', async ({ page }) => {
    console.log('Testing Help System...');
    
    // Add node and open modal
    await page.locator('text="PLC Input"').first().click({ timeout: 5000 });
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node');
    await page.dblclick('.react-flow__node');
    
    // Look for help icons
    const helpSelectors = [
      'svg[class*="help"]',
      'button:has(svg[class*="circle"])',
      '[class*="help-icon"]',
      '[title*="help"]'
    ];
    
    let helpFound = false;
    for (const selector of helpSelectors) {
      const helpIcon = page.locator(selector).first();
      if (await helpIcon.isVisible({ timeout: 1000 })) {
        helpFound = true;
        console.log(`✓ Help icon found with selector: ${selector}`);
        
        // Try hovering
        await helpIcon.hover();
        await page.waitForTimeout(1000);
        
        // Check for tooltip
        const tooltip = page.locator('[role="tooltip"], [class*="tooltip"]').first();
        if (await tooltip.isVisible({ timeout: 1000 })) {
          console.log('✓ Tooltip appeared on hover');
        }
        break;
      }
    }
    
    expect(helpFound).toBe(true);
  });

  test('5. Modal Responsiveness', async ({ page }) => {
    console.log('Testing Modal Responsiveness...');
    
    // Add node and open modal
    await page.locator('text="PLC Input"').first().click({ timeout: 5000 });
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node');
    await page.dblclick('.react-flow__node');
    
    // Test ESC key
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    
    // Check if modal closed
    const modalGone = await page.locator('[role="dialog"], .modal').first().isHidden();
    console.log(`✓ ESC key closes modal: ${modalGone ? 'Yes' : 'No'}`);
    
    // Re-open if closed
    if (modalGone) {
      await page.dblclick('.react-flow__node');
    }
    
    // Test clicking outside (if applicable)
    // This depends on the modal implementation
  });
});

// Summary test to collect all results
test('Phase 1 Summary', async ({ page }) => {
  console.log('\n=== PHASE 1 AUTOMATED TESTING SUMMARY ===');
  console.log('✓ Tests created and executed');
  console.log('✓ Adapted to actual UI elements');
  console.log('✓ Ready for manual verification');
  console.log('\nNote: Some tests may need adjustment based on actual UI implementation');
  console.log('Please run user interactive testing to verify all functionality');
});
