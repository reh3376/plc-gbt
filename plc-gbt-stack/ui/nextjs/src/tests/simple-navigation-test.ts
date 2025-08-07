/**
 * Simple Navigation Test - Debug Playwright Access
 * Test basic page navigation and element detection
 */

import { expect, test } from '@playwright/test';

test.describe('Simple Navigation Test', () => {
  test('Basic page access and navigation', async ({ page }) => {
    // Navigate to main page
    console.log('Navigating to http://localhost:3000');
    await page.goto('http://localhost:3000');

    // Wait for page to load
    await page.waitForLoadState('networkidle');
    console.log('Page loaded');

    // Take a screenshot for debugging
    await page.screenshot({ path: 'debug-page-load.png' });

    // Check if any control loops elements exist
    const controlLoopsIcon = page.locator('[data-testid="icon-control-loops"]');
    const isVisible = await controlLoopsIcon.isVisible();
    console.log(`Control loops icon visible: ${isVisible}`);

    if (isVisible) {
      console.log('Clicking control loops icon');
      await controlLoopsIcon.click();
      await page.waitForTimeout(1000);

      // Check if dashboard appears
      const dashboard = page.locator('text=Control Loop Dashboard');
      const dashboardVisible = await dashboard.isVisible();
      console.log(`Dashboard visible: ${dashboardVisible}`);
    } else {
      console.log('Control loops icon not found, listing all data-testids');
      const allTestIds = await page.locator('[data-testid]').all();
      for (const element of allTestIds) {
        const testId = await element.getAttribute('data-testid');
        console.log(`Found data-testid: ${testId}`);
      }
    }
  });
});
