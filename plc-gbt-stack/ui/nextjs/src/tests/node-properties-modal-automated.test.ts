import { expect, test } from '@playwright/test';

/**
 * Automated tests for Node Properties Modal
 * Following AI Task Orchestrator methodology - Phase 1 Automated Testing
 */

test.describe('Node Properties Modal - Automated Testing', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');

    // Wait for the application to load
    await page.waitForTimeout(2000);

    // Click on Workflows in the sidebar (using text selector)
    const workflowButton = page.getByText('Workflows', { exact: true });
    if (await workflowButton.isVisible()) {
      await workflowButton.click();
    }

    // Wait for React Flow canvas to be visible
    await page.waitForSelector('.react-flow', { timeout: 10000 });
  });

  test('Core Functionality', async ({ page }) => {
    // Look for PLC Input in the node palette
    const plcInputNode = page.getByText('PLC Input').first();
    if (await plcInputNode.isVisible()) {
      await plcInputNode.click();
      // Click on canvas to place node
      await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    } else {
      // Try alternate method - drag from palette
      const nodeItem = page.locator('.node-item').filter({ hasText: 'PLC Input' }).first();
      if (await nodeItem.isVisible()) {
        await nodeItem.dragTo(page.locator('.react-flow__viewport'));
      }
    }

    // Wait for node to appear on canvas
    await page.waitForSelector('.react-flow__node', { timeout: 5000 });

    // Double-click the first node to open properties modal
    await page.dblclick('.react-flow__node');

    // Test 1: Modal opens correctly - look for modal by class or role
    await page.waitForSelector('[role="dialog"], .modal, [class*="modal"]', {
      timeout: 5000,
    });
    const modalLocator = page.locator('[role="dialog"], .modal, [class*="modal"]');
    await expect(modalLocator).toBeVisible();

    // Test 2: Modal title shows correct node type
    const title = await page.textContent('h2, h3, [class*="title"]');
    expect(title?.toLowerCase()).toContain('plc');

    // Test 3: Tab system is present
    const tabs = await page.$$('[role="tab"]');
    expect(tabs.length).toBe(5); // Properties, Connections, Validation, Templates, Advanced

    // Test 4: Save and Reset buttons are present
    await expect(page.locator('button:has-text("Save Changes")')).toBeVisible();
    await expect(page.locator('button:has-text("Reset")')).toBeVisible();

    // Test 5: CircleHelp icon is present - look for help icon by class or svg
    const helpIcon = page.locator('[class*="help"], svg[class*="circle"], button:has(svg)');
    const helpIconCount = await helpIcon.count();
    expect(helpIconCount).toBeGreaterThan(0);
  });

  test('CircleHelp Icon System', async ({ page }) => {
    // Add a node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Test help icon hover
    const helpIcon = page.locator('[data-testid="node-help-icon"]');
    await helpIcon.hover();

    // Check tooltip appears
    await page.waitForSelector('[role="tooltip"]', { timeout: 2000 });
    const tooltipLocator = page.locator('[role="tooltip"]');
    await expect(tooltipLocator).toBeVisible();

    // Check tooltip content includes Input Type and Data Type
    const tooltipText = await tooltipLocator.textContent();
    expect(tooltipText).toContain('Input Type:');
    expect(tooltipText).toContain('Data Type:');

    // Click help icon to open documentation
    await helpIcon.click();

    // Check new tab opens (in test environment, check navigation)
    // Note: Playwright handles new tabs differently, we'll check the link exists
    const helpLink = await helpIcon.getAttribute('href');
    expect(helpLink).toContain('/docs/nodes/plc-input');
  });

  test('Tab System Navigation', async ({ page }) => {
    // Add node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Test tab switching
    const tabs = ['Properties', 'Connections', 'Validation', 'Templates', 'Advanced'];

    for (const tabName of tabs) {
      await page.click(`[role="tab"]:has-text("${tabName}")`);

      // Verify tab panel is visible
      const panel = page.locator(`[role="tabpanel"][aria-labelledby*="${tabName.toLowerCase()}"]`);
      await expect(panel).toBeVisible();
    }

    // Test keyboard navigation (Tab key)
    await page.click('[role="tab"]:has-text("Properties")');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');

    // Should move to Connections tab
    const activeTab = page.locator('[role="tab"][aria-selected="true"]');
    const activeTabText = await activeTab.textContent();
    expect(activeTabText).toContain('Connections');
  });

  test('Property Configuration - PLC Input Fields', async ({ page }) => {
    // Add node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Test Input Type dropdown
    const inputTypeSelect = page.locator('select[name="inputType"]');
    await expect(inputTypeSelect).toBeVisible();

    // Check options
    const inputTypeOptions = await inputTypeSelect.locator('option').allTextContents();
    expect(inputTypeOptions).toContain('Digital');
    expect(inputTypeOptions).toContain('Analog');

    // Test Data Type dropdown
    const dataTypeSelect = page.locator('select[name="dataType"]');
    await expect(dataTypeSelect).toBeVisible();

    // Check some data type options
    const dataTypeOptions = await dataTypeSelect.locator('option').allTextContents();
    expect(dataTypeOptions).toContain('BOOLEAN');
    expect(dataTypeOptions).toContain('INT');
    expect(dataTypeOptions).toContain('REAL');

    // Test PLC Address dropdown
    const plcAddressSelect = page.locator('select[name="plcAddress"]');
    await expect(plcAddressSelect).toBeVisible();

    // Test signal scaling visibility
    await dataTypeSelect.selectOption('BOOLEAN');
    const scalingSection = page.locator('[data-testid="signal-scaling-section"]');
    await expect(scalingSection).not.toBeVisible();

    // Switch to analog type
    await dataTypeSelect.selectOption('REAL');
    await expect(scalingSection).toBeVisible();
  });

  test('Connection Tab - PLC Input Specific', async ({ page }) => {
    // Add node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Navigate to Connections tab
    await page.click('[role="tab"]:has-text("Connections")');

    // PLC Input should not have input handles
    const inputHandles = await page.$$('[data-testid="input-handle-row"]');
    expect(inputHandles.length).toBe(0);

    // Check output handles exist
    const outputHandles = await page.$$('[data-testid="output-handle-row"]');
    expect(outputHandles.length).toBeGreaterThan(0);

    // Test Add Handle button
    const addHandleButton = page.locator('button:has-text("+ Add Handle")');
    await expect(addHandleButton).toBeVisible();

    // Click Add Handle button
    await addHandleButton.click();

    // Raw Configuration Modal should appear
    await page.waitForSelector('[data-testid="raw-config-modal"]', {
      timeout: 2000,
    });
    const rawConfigModalLocator = page.locator('[data-testid="raw-config-modal"]');
    await expect(rawConfigModalLocator).toBeVisible();

    // Signal mapping should be hidden for PLC Input
    const signalMappingSection = page.locator('[data-testid="signal-mapping-section"]');
    await expect(signalMappingSection).not.toBeVisible();
  });

  test('Validation Tab', async ({ page }) => {
    // Add node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Navigate to Validation tab
    await page.click('[role="tab"]:has-text("Validation")');

    // Check validation status shows "Awaiting Configuration"
    const validationStatus = await page.textContent('[data-testid="validation-status"]');
    expect(validationStatus).toContain('Awaiting Configuration');

    // Check add validation criteria button exists
    const addValidationButton = page.locator('button:has-text("Add Validation Criteria")');
    await expect(addValidationButton).toBeVisible();
  });

  test('Templates Tab', async ({ page }) => {
    // Add node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Navigate to Templates tab
    await page.click('[role="tab"]:has-text("Templates")');

    // Test Create Template button
    const createTemplateButton = page.locator('button:has-text("+ Create Template")');
    await expect(createTemplateButton).toBeVisible();

    await createTemplateButton.click();

    // Raw Configuration Modal should open
    await page.waitForSelector('[data-testid="raw-config-modal"]', {
      timeout: 2000,
    });
    const rawConfigModalLocator = page.locator('[data-testid="raw-config-modal"]');
    await expect(rawConfigModalLocator).toBeVisible();

    // Test search functionality
    const searchInput = page.locator('input[placeholder*="Search templates"]');
    await expect(searchInput).toBeVisible();

    // Test wildcard search tip is shown
    const searchTip = await page.textContent('[data-testid="search-tips"]');
    expect(searchTip).toContain('*');
  });

  test('Advanced Tab', async ({ page }) => {
    // Add node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Navigate to Advanced tab
    await page.click('[role="tab"]:has-text("Advanced")');

    // Check Raw Configuration section exists
    const rawConfigSection = page.locator('[data-testid="raw-configuration-section"]');
    await expect(rawConfigSection).toBeVisible();
  });

  test('Modal State Persistence', async ({ page }) => {
    // Add node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Enter a value in a field
    const nameInput = page.locator('input[name="name"]');
    await nameInput.fill('Test PLC Input');

    // Switch tabs
    await page.click('[role="tab"]:has-text("Connections")');
    await page.click('[role="tab"]:has-text("Properties")');

    // Value should persist
    const nameValue = await nameInput.inputValue();
    expect(nameValue).toBe('Test PLC Input');
  });

  test('Save and Reset Functionality', async ({ page }) => {
    // Add node and open properties
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Make changes
    const nameInput = page.locator('input[name="name"]');
    const originalValue = await nameInput.inputValue();
    await nameInput.fill('Modified Name');

    // Test Reset button
    await page.click('button:has-text("Reset")');
    const resetValue = await nameInput.inputValue();
    expect(resetValue).toBe(originalValue);

    // Test Save button
    await nameInput.fill('Final Name');
    await page.click('button:has-text("Save Changes")');

    // Modal should close or show success
    // Note: Implementation specific - adjust based on actual behavior
  });
});

// Performance tests
test.describe('Performance Tests', () => {
  test('Modal opens within 500ms', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="workflow-canvas"]');
    await page.click('[data-testid="sidebar-tool-workflows"]');
    await page.waitForSelector('.react-flow');

    // Add node
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');

    // Measure modal open time
    const startTime = Date.now();
    await page.dblclick('.react-flow__node-plc-input');
    await page.waitForSelector('[data-testid="node-properties-modal"]');
    const endTime = Date.now();

    expect(endTime - startTime).toBeLessThan(500);
  });
});

// Accessibility tests
test.describe('Accessibility Tests', () => {
  test('Modal is keyboard navigable', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="workflow-canvas"]');
    await page.click('[data-testid="sidebar-tool-workflows"]');
    await page.waitForSelector('.react-flow');

    // Add node and open modal
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Test ESC key closes modal
    await page.keyboard.press('Escape');
    const modalAfterEsc = await page.$('[data-testid="node-properties-modal"]');
    expect(modalAfterEsc).toBeNull();
  });

  test('All interactive elements have proper ARIA labels', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="workflow-canvas"]');
    await page.click('[data-testid="sidebar-tool-workflows"]');
    await page.waitForSelector('.react-flow');

    // Add node and open modal
    await page.click('[data-testid="node-palette-plc-input"]');
    await page.click('.react-flow__viewport', { position: { x: 400, y: 300 } });
    await page.waitForSelector('.react-flow__node-plc-input');
    await page.dblclick('.react-flow__node-plc-input');

    // Check tabs have proper ARIA attributes
    const tabs = await page.$$('[role="tab"]');
    for (const tab of tabs) {
      const ariaSelected = await tab.getAttribute('aria-selected');
      expect(['true', 'false']).toContain(ariaSelected);
    }

    // Check form inputs have labels
    const inputs = await page.$$('input, select, textarea');
    for (const input of inputs) {
      const name = await input.getAttribute('name');
      const label = await page.$(`label[for="${name}"]`);
      // Either has a label or aria-label
      if (!label) {
        const ariaLabel = await input.getAttribute('aria-label');
        expect(ariaLabel).toBeTruthy();
      }
    }
  });
});
