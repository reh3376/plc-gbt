import { test } from '@playwright/test';

test('Debug - Find Workflow Tab', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(2000);

  // Debug: List all tabs
  const tabs = await page.locator('[role="tab"]').all();
  console.log(`Found ${tabs.length} tabs:`);

  for (let i = 0; i < tabs.length; i++) {
    const text = await tabs[i].textContent();
    const isVisible = await tabs[i].isVisible();
    console.log(`Tab ${i}: "${text?.trim()}" - Visible: ${isVisible}`);
  }

  // Try different selectors
  const selectors = [
    '[role="tab"]:has-text("Workflow")',
    'button:has-text("Workflow")',
    'text=Workflows',
    '[aria-label*="Workflow"]',
    '*:has-text("Workflow management")',
  ];

  for (const selector of selectors) {
    try {
      const element = page.locator(selector).first();
      const exists = (await element.count()) > 0;
      const visible = exists ? await element.isVisible() : false;
      console.log(`Selector "${selector}": Exists: ${exists}, Visible: ${visible}`);
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : String(e);
      console.log(`Selector "${selector}": Error - ${errorMessage}`);
    }
  }

  // Take screenshot
  await page.screenshot({ path: 'debug-workflow-tab.png', fullPage: true });
});
