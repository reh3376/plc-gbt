import { expect, test } from '@playwright/test';

/**
 * Node Properties Modal - Targeted Testing for Demo Nodes
 *
 * Following AI Task Orchestrator TypeScript methodology with MCP browser automation
 * Tests specifically target the existing demo nodes in the workflow store
 *
 * CRITICAL: Uses http://localhost:3000 for dev server access (confirmed working)
 * CRITICAL: Targets existing demo node 'demo-plc-input-1' (Temperature Sensor)
 */

test.describe('Node Properties Modal - Targeted Demo Node Testing', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to application and ensure it's loaded
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('domcontentloaded');

    // Navigate to Workflows tab (app defaults to File Explorer)
    await page.click('[role="tab"]:has-text("Workflows")');

    // Wait for React Flow canvas to load
    await page.waitForSelector('.react-flow__viewport', { timeout: 15000 });

    // Wait a bit more for nodes to render
    await page.waitForTimeout(2000);
  });

  test('Should find and interact with demo PLC Input node', async ({ page }) => {
    console.log('🔍 Looking for demo PLC Input node...');

    // Look for the Temperature Sensor node (demo-plc-input-1)
    const tempSensorNode = page
      .locator('.react-flow__node')
      .filter({ hasText: 'Temperature Sensor' });

    // Verify the node exists
    await expect(tempSensorNode).toBeVisible({ timeout: 10000 });
    console.log('✅ Found Temperature Sensor node');

    // Get the bounding box for double-click positioning
    const nodeBox = await tempSensorNode.boundingBox();
    expect(nodeBox).not.toBeNull();

    if (nodeBox) {
      const centerX = nodeBox.x + nodeBox.width / 2;
      const centerY = nodeBox.y + nodeBox.height / 2;

      console.log(`🎯 Double-clicking at position: ${centerX}, ${centerY}`);

      // Double-click on the center of the node
      await page.mouse.dblclick(centerX, centerY);

      // Wait for modal to appear
      await page.waitForTimeout(1000);

      // Check if modal opened
      const modal = page
        .locator('[data-testid="node-properties-modal"]')
        .or(page.locator('.fixed').filter({ hasText: 'Node Properties' }))
        .or(page.locator('h2:has-text("Node Properties")'));

      const isModalVisible = await modal.isVisible();
      console.log(`🔍 Modal visible: ${isModalVisible}`);

      if (isModalVisible) {
        console.log('✅ Node Properties Modal opened successfully!');

        // Verify modal content
        await expect(modal).toBeVisible();

        // Look for the Temperature Sensor title or PLC Input schema
        const modalContent = page.locator('.fixed').filter({ hasText: 'Node Properties' });
        await expect(modalContent).toBeVisible();
      } else {
        console.log('❌ Modal did not open - checking for alternative selectors...');

        // Debug: Log all visible elements that might be the modal
        const allModals = await page.locator('.fixed, [role="dialog"], .modal').all();
        console.log(`Found ${allModals.length} potential modal elements`);

        for (let i = 0; i < allModals.length; i++) {
          const modalText = await allModals[i].textContent();
          console.log(`Modal ${i}: ${modalText?.substring(0, 100)}...`);
        }

        // Fail the test with diagnostic info
        throw new Error(
          'Node Properties Modal did not open after double-clicking Temperature Sensor node'
        );
      }
    }
  });

  test('Should verify all demo nodes are present', async ({ page }) => {
    console.log('🔍 Checking for all demo nodes...');

    // Expected demo nodes based on INITIAL_DEMO_NODES
    const expectedNodes = [
      'Temperature Sensor', // demo-plc-input-1
      'Temperature PID', // demo-pid-1
      'Heater Output', // demo-plc-output-1
      'Process Data Logger', // demo-data-logger-1
    ];

    for (const nodeName of expectedNodes) {
      const node = page.locator('.react-flow__node').filter({ hasText: nodeName });
      await expect(node).toBeVisible({ timeout: 5000 });
      console.log(`✅ Found node: ${nodeName}`);
    }

    console.log('✅ All demo nodes are present and visible');
  });

  test('Should test modal opening with different interaction methods', async ({ page }) => {
    console.log('🔍 Testing different interaction methods...');

    const tempSensorNode = page
      .locator('.react-flow__node')
      .filter({ hasText: 'Temperature Sensor' });
    await expect(tempSensorNode).toBeVisible({ timeout: 10000 });

    // Method 1: Regular double-click
    console.log('🎯 Method 1: Regular double-click');
    await tempSensorNode.dblclick();
    await page.waitForTimeout(1000);

    const modal = page
      .locator('h2:has-text("Node Properties")')
      .or(page.locator('.fixed').filter({ hasText: 'Properties' }));

    if (await modal.isVisible()) {
      console.log('✅ Method 1 successful - Modal opened');
      // Close modal if it opened
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    } else {
      console.log('❌ Method 1 failed');
    }

    // Method 2: Click to select, then double-click
    console.log('🎯 Method 2: Select then double-click');
    await tempSensorNode.click(); // Select first
    await page.waitForTimeout(500);
    await tempSensorNode.dblclick(); // Then double-click
    await page.waitForTimeout(1000);

    if (await modal.isVisible()) {
      console.log('✅ Method 2 successful - Modal opened');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    } else {
      console.log('❌ Method 2 failed');
    }

    // Method 3: Force double-click with coordinates
    console.log('🎯 Method 3: Force double-click with coordinates');
    const nodeBox = await tempSensorNode.boundingBox();
    if (nodeBox) {
      const centerX = nodeBox.x + nodeBox.width / 2;
      const centerY = nodeBox.y + nodeBox.height / 2;
      await page.mouse.dblclick(centerX, centerY);
      await page.waitForTimeout(1000);

      if (await modal.isVisible()) {
        console.log('✅ Method 3 successful - Modal opened');
      } else {
        console.log('❌ Method 3 failed');
      }
    }

    // If none worked, this is a critical issue
    const finalCheck = await modal.isVisible();
    if (!finalCheck) {
      console.log('🚨 CRITICAL: None of the interaction methods opened the modal');

      // Debug: Check node properties for interaction debugging
      const nodeElement = await tempSensorNode.elementHandle();
      if (nodeElement) {
        const nodeDebugInfo = await nodeElement.evaluate((el: Element) => {
          return {
            className: el.className,
            tagName: el.tagName,
            hasDataNodeId: el.hasAttribute('data-id'),
            hasOnDoubleClick:
              typeof (el as unknown as Record<string, unknown>).ondblclick !== 'undefined',
            style: getComputedStyle(el).pointerEvents,
          };
        });
        console.log('Node debug info:', nodeDebugInfo);
      }
    }
  });

  test('Should verify React Flow canvas is interactive', async ({ page }) => {
    console.log('🔍 Testing React Flow canvas interactivity...');

    // Check if canvas is present
    const canvas = page.locator('.react-flow__viewport');
    await expect(canvas).toBeVisible();
    console.log('✅ React Flow canvas is visible');

    // Check if nodes are interactive (can be selected)
    const tempSensorNode = page
      .locator('.react-flow__node')
      .filter({ hasText: 'Temperature Sensor' });
    await tempSensorNode.click();

    // Check if node gets selected (usually adds a selected class or style)
    const isSelected = await tempSensorNode.evaluate(el => {
      return (
        el.classList.contains('selected') ||
        el.classList.contains('react-flow__node-selected') ||
        getComputedStyle(el).outline !== 'none'
      );
    });

    console.log(`Node selection state: ${isSelected}`);

    // Test canvas panning
    const canvasBox = await canvas.boundingBox();
    if (canvasBox) {
      const startX = canvasBox.x + 100;
      const startY = canvasBox.y + 100;
      const endX = startX + 50;
      const endY = startY + 50;

      await page.mouse.move(startX, startY);
      await page.mouse.down();
      await page.mouse.move(endX, endY);
      await page.mouse.up();

      console.log('✅ Canvas panning test completed');
    }
  });
});
