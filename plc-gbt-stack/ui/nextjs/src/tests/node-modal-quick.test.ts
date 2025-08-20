import { test, expect } from '@playwright/test';

test('Quick Node Modal Test', async ({ page }) => {
  console.log('Starting quick test...');
  
  // Go to the app
  await page.goto('http://localhost:3000');
  
  // Take screenshot of initial page
  await page.screenshot({ path: 'test-initial-page.png' });
  console.log('✓ Screenshot saved: test-initial-page.png');
  
  // Wait a bit for app to load
  await page.waitForTimeout(3000);
  
  // Look for any workflow-related elements
  const workflowElements = await page.$$('[class*="workflow"], [class*="Workflow"], text=Workflow');
  console.log(`Found ${workflowElements.length} workflow-related elements`);
  
  // Look for React Flow
  const reactFlow = await page.$('.react-flow');
  if (reactFlow) {
    console.log('✓ React Flow canvas found');
    
    // Take screenshot
    await page.screenshot({ path: 'test-react-flow.png' });
    
    // Try to find nodes in palette
    const nodeElements = await page.$$('[class*="node"], text="PLC"');
    console.log(`Found ${nodeElements.length} node-related elements`);
  } else {
    console.log('✗ React Flow canvas not found on initial page');
    
    // Try clicking on any visible buttons/links
    const buttons = await page.$$('button, a');
    console.log(`Found ${buttons.length} clickable elements`);
    
    // Click on first few buttons to see what happens
    for (let i = 0; i < Math.min(5, buttons.length); i++) {
      try {
        const text = await buttons[i].textContent();
        console.log(`Button ${i}: ${text}`);
      } catch (e) {
        // ignore
      }
    }
  }
  
  // Final screenshot
  await page.screenshot({ path: 'test-final-page.png', fullPage: true });
  console.log('✓ Final screenshot saved');
});
