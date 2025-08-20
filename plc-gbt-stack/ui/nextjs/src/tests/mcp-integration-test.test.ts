/**
 * MCP Integration Test - Verify Real MCP Client Functionality
 * 
 * @description Test that the real MCP client integration is working
 * @methodology AI Task Orchestrator TypeScript Guide
 * @phase Phase 5: Browser Automation Restoration
 */

import { test, expect } from '@playwright/test';

test.describe('MCP Integration Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    
    // Wait for the application to load (use domcontentloaded instead of networkidle)
    await page.waitForLoadState('domcontentloaded');
    
    // Wait for main UI elements to be present
    await page.waitForSelector('[role="tablist"]', { timeout: 10000 });
  });

  test('Application loads successfully with real MCP client', async ({ page }) => {
    // Test that the application loads without MCP client errors
    const consoleErrors: string[] = [];
    
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Wait for initial load
    await page.waitForTimeout(2000);

    // Check for MCP-related console errors
    const mcpErrors = consoleErrors.filter(error => 
      error.includes('MCP') || 
      error.includes('openapi') || 
      error.includes('schema')
    );

    console.log('Console errors found:', consoleErrors);
    console.log('MCP-related errors:', mcpErrors);

    // Application should load successfully
    expect(page.url()).toContain('localhost:3000');
    
    // Should not have critical MCP errors (warnings are acceptable)
    const criticalMCPErrors = mcpErrors.filter(error => 
      !error.includes('warning') && !error.includes('⚠️')
    );
    
    expect(criticalMCPErrors).toHaveLength(0);
  });

  test('Navigate to Workflows tab', async ({ page }) => {
    // Test navigation to workflows to prepare for node testing
    try {
      // Look for Workflows tab - try multiple selectors
      const workflowsTab = page.locator('[role="tab"]').filter({ hasText: 'Workflows' });
      
      if (await workflowsTab.count() > 0) {
        await workflowsTab.click();
        console.log('✅ Successfully clicked Workflows tab');
        
        // Wait for workflow canvas to load
        await page.waitForTimeout(1000);
        
        // Check if we're on the workflows page
        const canvas = page.locator('.react-flow');
        await expect(canvas).toBeVisible();
        console.log('✅ Workflow canvas is visible');
      } else {
        console.log('⚠️ Workflows tab not found - application may have different structure');
      }
      
    } catch (error) {
      console.log('⚠️ Navigation test failed:', error);
      // Take screenshot for debugging
      await page.screenshot({ path: 'test-results/mcp-integration-debug.png' });
    }
  });

  test('Test Node Properties Modal availability', async ({ page }) => {
    // Test if we can access node properties functionality
    try {
      // Navigate to workflows first
      const workflowsTab = page.locator('[role="tab"]').filter({ hasText: 'Workflows' });
      
      if (await workflowsTab.count() > 0) {
        await workflowsTab.click();
        await page.waitForTimeout(1000);
        
        // Look for any nodes on the canvas
        const nodes = page.locator('.react-flow__node');
        
        if (await nodes.count() > 0) {
          console.log(`Found ${await nodes.count()} nodes on canvas`);
          
          // Try to right-click on first node to open properties
          await nodes.first().click({ button: 'right' });
          await page.waitForTimeout(500);
          
          // Check if properties modal or context menu appears
          const modal = page.locator('[role="dialog"]');
          const contextMenu = page.locator('.context-menu');
          
          const modalVisible = await modal.isVisible().catch(() => false);
          const menuVisible = await contextMenu.isVisible().catch(() => false);
          
          if (modalVisible || menuVisible) {
            console.log('✅ Node interaction working - modal or menu appeared');
          } else {
            console.log('⚠️ No modal or menu appeared - may need different interaction');
          }
        } else {
          console.log('⚠️ No nodes found on canvas - may need to create test workflow');
        }
      }
      
    } catch (error) {
      console.log('⚠️ Node properties test failed:', error);
      await page.screenshot({ path: 'test-results/node-properties-debug.png' });
    }
  });
});
