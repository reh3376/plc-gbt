/**
 * 🧪 Advanced Settings Modal Test Suite
 *
 * Tests the newly implemented Advanced Settings Configuration Modal
 * Following AI Task Orchestrator TypeScript methodology
 */

import { expect, test } from '@playwright/test';

test.describe('Advanced Settings Modal', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the main page
    await page.goto('http://localhost:3000');

    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');

    // Click on Control Loop tool to open the tuning interface
    await page.click('[data-testid="icon-control-loops"]');

    // Wait for the Control Loop Tuning Interface to load
    await page.waitForSelector('text=Advanced Settings', { timeout: 10000 });
  });

  test('Advanced Settings button should open modal', async ({ page }) => {
    // Click the Advanced Settings button
    await page.click('text=Advanced Settings');

    // Wait for modal to appear
    await page.waitForSelector('text=Advanced Settings', { timeout: 5000 });

    // Verify modal sections are visible
    await expect(page.locator('text=Basic Settings')).toBeVisible();
    await expect(page.locator('text=Tuning Algorithm')).toBeVisible();
    await expect(page.locator('text=Safety Limits')).toBeVisible();
    await expect(page.locator('text=Data Retention')).toBeVisible();
  });

  test('Tuning Algorithm dropdown should have all options', async ({ page }) => {
    // Open Advanced Settings modal
    await page.click('text=Advanced Settings');
    await page.waitForSelector('#tuning-algorithm', { timeout: 5000 });

    // Check that all tuning algorithms are present
    const algorithmDropdown = page.locator('#tuning-algorithm');
    await expect(algorithmDropdown).toHaveValue('ziegler-nichols');

    // Verify all algorithm options exist
    await expect(page.locator('option[value="ziegler-nichols"]')).toBeVisible();
    await expect(page.locator('option[value="cohen-coon"]')).toBeVisible();
    await expect(page.locator('option[value="lambda-tuning"]')).toBeVisible();
    await expect(page.locator('option[value="imc"]')).toBeVisible();
    await expect(page.locator('option[value="relay-feedback"]')).toBeVisible();
    await expect(page.locator('option[value="genetic-algorithm"]')).toBeVisible();
  });

  test('Safety Limits inputs should be functional', async ({ page }) => {
    // Open Advanced Settings modal
    await page.click('text=Advanced Settings');
    await page.waitForSelector('#max-kp', { timeout: 5000 });

    // Test Max Kp input
    const maxKpInput = page.locator('#max-kp');
    await maxKpInput.fill('150');
    await expect(maxKpInput).toHaveValue('150');

    // Test Max Ki input
    const maxKiInput = page.locator('#max-ki');
    await maxKiInput.fill('75');
    await expect(maxKiInput).toHaveValue('75');

    // Test Max Kd input
    const maxKdInput = page.locator('#max-kd');
    await maxKdInput.fill('30');
    await expect(maxKdInput).toHaveValue('30');

    // Test Output Min/Max
    const outputMinInput = page.locator('#output-min');
    await outputMinInput.fill('5');
    await expect(outputMinInput).toHaveValue('5');

    const outputMaxInput = page.locator('#output-max');
    await outputMaxInput.fill('95');
    await expect(outputMaxInput).toHaveValue('95');
  });

  test('Data Retention section should toggle correctly', async ({ page }) => {
    // Open Advanced Settings modal
    await page.click('text=Advanced Settings');
    await page.waitForSelector('text=Enable Historical Data Retention', { timeout: 5000 });

    // Data retention should be enabled by default
    const dataRetentionCheckbox = page.locator(
      'input[type="checkbox"]:near(:text("Enable Historical Data Retention"))'
    );
    await expect(dataRetentionCheckbox).toBeChecked();

    // Retention Days and Max Data Points should be visible
    await expect(page.locator('#retention-days')).toBeVisible();
    await expect(page.locator('#max-data-points')).toBeVisible();

    // Disable data retention
    await dataRetentionCheckbox.uncheck();

    // Retention inputs should be hidden
    await expect(page.locator('#retention-days')).not.toBeVisible();
    await expect(page.locator('#max-data-points')).not.toBeVisible();
  });

  test('Save Settings should work', async ({ page }) => {
    // Open Advanced Settings modal
    await page.click('text=Advanced Settings');
    await page.waitForSelector('text=Save Settings', { timeout: 5000 });

    // Change some settings
    await page.selectOption('#tuning-algorithm', 'cohen-coon');
    await page.fill('#max-kp', '200');
    await page.fill('#analysis-time', '45');

    // Click Save Settings
    await page.click('text=Save Settings');

    // Modal should close
    await page.waitForTimeout(500);
    await expect(page.locator('text=Advanced Settings').nth(1)).not.toBeVisible(); // Modal title
  });

  test('Cancel should close modal without saving', async ({ page }) => {
    // Open Advanced Settings modal
    await page.click('text=Advanced Settings');
    await page.waitForSelector('text=Cancel', { timeout: 5000 });

    // Change some settings
    await page.selectOption('#tuning-algorithm', 'imc');
    await page.fill('#max-ki', '999');

    // Click Cancel
    await page.click('text=Cancel');

    // Modal should close
    await page.waitForTimeout(500);
    await expect(page.locator('text=Advanced Settings').nth(1)).not.toBeVisible(); // Modal title
  });

  test('Modal close button should work', async ({ page }) => {
    // Open Advanced Settings modal
    await page.click('text=Advanced Settings');
    await page.waitForSelector('text=✕', { timeout: 5000 });

    // Click the X close button
    await page.click('text=✕');

    // Modal should close
    await page.waitForTimeout(500);
    await expect(page.locator('text=Advanced Settings').nth(1)).not.toBeVisible(); // Modal title
  });
});
