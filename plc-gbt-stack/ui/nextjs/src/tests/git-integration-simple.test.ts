/**
 * Simple Git Integration Test to Debug Selectors
 */

import { expect, test } from '@playwright/test';

test('debug Git integration navigation', async ({ page }) => {
  // Navigate to the app
  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle');

  // Take a screenshot to see the current state
  await page.screenshot({ path: 'test-results/debug-initial.png' });

  // Try different selectors to find PLC Git icon
  console.log('Looking for icon strip...');
  const iconStrip = page.locator(
    '[data-testid="left-sidebar-icons"], .icon-strip, nav[role="navigation"]'
  );
  const iconStripVisible = await iconStrip.isVisible().catch(() => false);
  console.log('Icon strip visible:', iconStripVisible);

  // Try to find all icon items
  const iconItems = page.locator('.icon-strip-item, button[class*="icon"], [role="button"]');
  const iconCount = await iconItems.count();
  console.log('Found icon items:', iconCount);

  // Log all visible text
  const visibleText = await page.locator('body').textContent();
  console.log('Page contains PLC Git text:', visibleText?.includes('PLC Git'));

  // Find the actual clickable PLC Git icon (not the sr-only instructions)
  // The icon is a div with class icon-strip-item that contains the Git icon
  const plcGitIcon = page
    .locator('.icon-strip-item')
    .filter({ has: page.locator('svg.lucide-git-branch') });
  const plcGitIconCount = await plcGitIcon.count();
  console.log('Found PLC Git icons:', plcGitIconCount);

  if (plcGitIconCount > 0) {
    // Click the first matching icon
    await plcGitIcon.first().click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'test-results/debug-after-git-click.png' });
  } else {
    // Try alternative approach - find by position or other attributes
    const allIcons = page.locator('.icon-strip-item');
    const count = await allIcons.count();
    console.log('Total icon-strip-items:', count);

    // PLC Git is typically one of the last icons, try clicking each to find it
    for (let i = 0; i < count; i++) {
      const icon = allIcons.nth(i);
      const iconHtml = await icon.innerHTML();
      if (iconHtml.includes('git') || iconHtml.includes('GitBranch')) {
        console.log(`Found Git icon at position ${i}`);
        await icon.click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: 'test-results/debug-after-git-click.png' });
        break;
      }
    }
  }

  // Check if we're on the Git integration page
  const gitIntegrationTitle = page.locator(
    'h1:has-text("Git Integration"), [aria-label*="Git Integration"]'
  );
  const isOnGitPage = await gitIntegrationTitle.isVisible().catch(() => false);
  console.log('On Git Integration page:', isOnGitPage);

  // Log main content
  const mainContent = page.locator('#main-content, main');
  const mainContentText = await mainContent.textContent().catch(() => '');
  console.log('Main content preview:', mainContentText?.substring(0, 200));
});
