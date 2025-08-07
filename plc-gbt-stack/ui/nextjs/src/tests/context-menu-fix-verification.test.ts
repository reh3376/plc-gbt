/**
 * 🧪 Context Menu Fix Verification Test
 *
 * Specifically tests the context menu visibility fix for Control Loop Tuning Interface
 * Following AI Task Orchestrator TypeScript methodology
 */

import { expect, test } from '@playwright/test';

test.describe('Context Menu Visibility Fix', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the main page
    await page.goto('http://localhost:3000');

    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');

    // Click on Control Loop tool to open the tuning interface
    await page.click('[data-testid="icon-control-loops"]');

    // Wait for the Control Loop Tuning Interface to load
    await page.waitForSelector('[data-testid="context-menu-trigger"]', { timeout: 10000 });
  });

  test('Context menu should appear and remain visible when clicked', async ({ page }) => {
    // Click the context menu trigger (3-dot icon)
    await page.click('[data-testid="context-menu-trigger"]');

    // Wait for context popup to appear
    await page.waitForSelector('[data-testid="context-popup"]', { timeout: 5000 });

    // Verify the context popup is visible
    const contextPopup = page.locator('[data-testid="context-popup"]');
    await expect(contextPopup).toBeVisible();

    // Verify all expected context options are present
    await expect(page.locator('button:has-text("Change queID")')).toBeVisible();
    await expect(page.locator('button:has-text("Set to Active")')).toBeVisible();
    await expect(page.locator('button:has-text("Remove")')).toBeVisible();
    await expect(page.locator('button:has-text("Loop Analysis")')).toBeVisible();

    // Wait a moment to ensure it doesn't disappear immediately
    await page.waitForTimeout(1000);

    // Context popup should still be visible
    await expect(contextPopup).toBeVisible();
  });

  test('Context menu should remain visible when clicking inside it', async ({ page }) => {
    // Open context menu
    await page.click('[data-testid="context-menu-trigger"]');
    await page.waitForSelector('[data-testid="context-popup"]', { timeout: 5000 });

    const contextPopup = page.locator('[data-testid="context-popup"]');
    await expect(contextPopup).toBeVisible();

    // Click somewhere inside the context popup (but not on an action button)
    await contextPopup.click({ position: { x: 100, y: 50 } });

    // Wait a moment
    await page.waitForTimeout(500);

    // Context popup should still be visible
    await expect(contextPopup).toBeVisible();
  });

  test('Context menu should close when clicking outside', async ({ page }) => {
    // Open context menu
    await page.click('[data-testid="context-menu-trigger"]');
    await page.waitForSelector('[data-testid="context-popup"]', { timeout: 5000 });

    const contextPopup = page.locator('[data-testid="context-popup"]');
    await expect(contextPopup).toBeVisible();

    // Click outside the context popup (on the main content area)
    await page.click('body', { position: { x: 400, y: 300 } });

    // Wait for the popup to close
    await page.waitForTimeout(200);

    // Context popup should now be hidden
    await expect(contextPopup).not.toBeVisible();
  });

  test('Context menu should close when clicking an action', async ({ page }) => {
    // Open context menu
    await page.click('[data-testid="context-menu-trigger"]');
    await page.waitForSelector('[data-testid="context-popup"]', { timeout: 5000 });

    const contextPopup = page.locator('[data-testid="context-popup"]');
    await expect(contextPopup).toBeVisible();

    // Click on "Change queID" action (enabled action)
    await page.click('button:has-text("Change queID")');

    // Wait for the popup to close
    await page.waitForTimeout(200);

    // Context popup should now be hidden
    await expect(contextPopup).not.toBeVisible();
  });

  test('Context menu should be draggable', async ({ page }) => {
    // Open context menu
    await page.click('[data-testid="context-menu-trigger"]');
    await page.waitForSelector('[data-testid="context-popup"]', { timeout: 5000 });

    const contextPopup = page.locator('[data-testid="context-popup"]');
    await expect(contextPopup).toBeVisible();

    // Get initial position
    const initialBox = await contextPopup.boundingBox();

    // Drag the context popup by its header
    const dragHandle = contextPopup.locator('.bg-\\[\\#383838\\]').first();
    await dragHandle.dragTo(page.locator('body'), {
      targetPosition: { x: initialBox!.x + 100, y: initialBox!.y + 50 },
    });

    // Get new position
    const newBox = await contextPopup.boundingBox();

    // Verify the popup moved
    expect(Math.abs(newBox!.x - initialBox!.x)).toBeGreaterThan(50);

    // Context popup should still be visible after dragging
    await expect(contextPopup).toBeVisible();
  });

  test('Context menu close button should work', async ({ page }) => {
    // Open context menu
    await page.click('[data-testid="context-menu-trigger"]');
    await page.waitForSelector('[data-testid="context-popup"]', { timeout: 5000 });

    const contextPopup = page.locator('[data-testid="context-popup"]');
    await expect(contextPopup).toBeVisible();

    // Click the close button (✕)
    await page.click('[data-testid="context-popup"] button:has-text("✕")');

    // Wait for the popup to close
    await page.waitForTimeout(200);

    // Context popup should now be hidden
    await expect(contextPopup).not.toBeVisible();
  });
});
