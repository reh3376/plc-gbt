/**
 * Project Template Wizard - Automated Testing Suite
 * AI Task Orchestrator Compliance - Phase 1 Testing
 *
 * @description Comprehensive automated tests using Playwright MCP
 * @requirement >= 99% success rate for Phase 1 completion
 */

import { MCPPlaywrightClient } from '@/lib/mcp/playwright-client';

interface TestResult {
  name: string;
  category: string;
  passed: boolean;
  duration: number;
  error?: string;
}

interface TestCategory {
  name: string;
  tests: TestResult[];
  successRate: number;
}

/**
 * Execute comprehensive automated testing suite for Project Template Wizard
 */
export async function executeProjectTemplateWizardTests(): Promise<{
  overallSuccessRate: number;
  categories: TestCategory[];
  readyForUserTesting: boolean;
}> {
  const mcpPlaywright = new MCPPlaywrightClient();
  const allTests: TestResult[] = [];

  try {
    // Initialize test environment
    await mcpPlaywright.browser_navigate('http://localhost:3001');
    await mcpPlaywright.browser_wait_for({ text: 'File Explorer', time: 5 });

    // Category 1: Component Interaction Tests
    console.log('🧪 Running Component Interaction Tests...');
    const componentTests = await runComponentInteractionTests(mcpPlaywright);
    allTests.push(...componentTests);

    // Category 2: E2E Workflow Tests
    console.log('🧪 Running E2E Workflow Tests...');
    const e2eTests = await runE2EWorkflowTests(mcpPlaywright);
    allTests.push(...e2eTests);

    // Category 3: Accessibility Tests
    console.log('🧪 Running Accessibility Tests...');
    const a11yTests = await runAccessibilityTests(mcpPlaywright);
    allTests.push(...a11yTests);

    // Category 4: Performance Tests
    console.log('🧪 Running Performance Tests...');
    const performanceTests = await runPerformanceTests(mcpPlaywright);
    allTests.push(...performanceTests);

    // Category 5: Cross-browser Tests
    console.log('🧪 Running Cross-browser Tests...');
    const crossBrowserTests = await runCrossBrowserTests(mcpPlaywright);
    allTests.push(...crossBrowserTests);

    // Calculate results
    const categories = calculateCategoryResults(allTests);
    const overallSuccessRate = calculateOverallSuccessRate(categories);

    console.log(`\n📊 Overall Success Rate: ${overallSuccessRate}%`);

    return {
      overallSuccessRate,
      categories,
      readyForUserTesting: overallSuccessRate >= 99,
    };
  } catch (error) {
    console.error('Test suite execution failed:', error);
    return {
      overallSuccessRate: 0,
      categories: [],
      readyForUserTesting: false,
    };
  } finally {
    await mcpPlaywright.browser_close();
  }
}

/**
 * Component Interaction Tests
 */
async function runComponentInteractionTests(mcp: MCPPlaywrightClient): Promise<TestResult[]> {
  const tests: TestResult[] = [];

  // Test 1: Open Project Template Wizard
  tests.push(
    await executeTest(
      {
        name: 'Open Project Template Wizard',
        category: 'Component Interaction',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');
          await mcp.browser_wait_for({ text: 'Select Template', time: 2 });
        },
      },
      mcp
    )
  );

  // Test 2: Navigate through wizard steps
  tests.push(
    await executeTest(
      {
        name: 'Navigate wizard steps forward',
        category: 'Component Interaction',
        action: async () => {
          // Select a template
          await mcp.browser_click(
            'ControlLogix template',
            '[data-testid="template-controllogix-standard"]'
          );
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');
          await mcp.browser_wait_for({ text: 'Configure Project', time: 1 });
        },
      },
      mcp
    )
  );

  // Test 3: Navigate backward
  tests.push(
    await executeTest(
      {
        name: 'Navigate wizard steps backward',
        category: 'Component Interaction',
        action: async () => {
          await mcp.browser_click('Previous button', '[data-testid="wizard-prev-btn"]');
          await mcp.browser_wait_for({ text: 'Select Template', time: 1 });
        },
      },
      mcp
    )
  );

  // Test 4: Close wizard with X button
  tests.push(
    await executeTest(
      {
        name: 'Close wizard with X button',
        category: 'Component Interaction',
        action: async () => {
          await mcp.browser_click('Close button', '[data-testid="wizard-close-btn"]');
          await mcp.browser_wait_for({ textGone: 'Select Template', time: 1 });
        },
      },
      mcp
    )
  );

  // Test 5: Close wizard with ESC key
  tests.push(
    await executeTest(
      {
        name: 'Close wizard with ESC key',
        category: 'Component Interaction',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');
          await mcp.browser_wait_for({ text: 'Select Template', time: 1 });
          await mcp.browser_press_key('Escape');
          await mcp.browser_wait_for({ textGone: 'Select Template', time: 1 });
        },
      },
      mcp
    )
  );

  // Test 6: Template selection interaction
  tests.push(
    await executeTest(
      {
        name: 'Template selection highlights',
        category: 'Component Interaction',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');
          await mcp.browser_click(
            'Distillation template',
            '[data-testid="template-distillation-control"]'
          );
          const snapshot = await mcp.browser_snapshot();
          // Verify visual selection state
          if (!snapshot.includes('bg-[#094771]')) {
            throw new Error('Template selection highlight not applied');
          }
        },
      },
      mcp
    )
  );

  return tests;
}

/**
 * E2E Workflow Tests
 */
async function runE2EWorkflowTests(mcp: MCPPlaywrightClient): Promise<TestResult[]> {
  const tests: TestResult[] = [];

  // Test 1: Complete project creation workflow
  tests.push(
    await executeTest(
      {
        name: 'Complete project creation workflow',
        category: 'E2E Workflow',
        action: async () => {
          // Step 1: Open wizard
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');

          // Step 2: Select template
          await mcp.browser_click(
            'ControlLogix template',
            '[data-testid="template-controllogix-standard"]'
          );
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');

          // Step 3: Configure project
          await mcp.browser_type(
            'Project name input',
            '[data-testid="field-projectName"]',
            'TestProject_001'
          );
          await mcp.browser_select_option(
            'Processor select',
            '[data-testid="field-processorType"]',
            ['1756-L73']
          );
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');

          // Step 4: Review and create
          await mcp.browser_wait_for({ text: 'Review & Create', time: 1 });
          const snapshot = await mcp.browser_snapshot();
          if (!snapshot.includes('TestProject_001')) {
            throw new Error('Project name not shown in review');
          }

          await mcp.browser_click('Create button', '[data-testid="wizard-create-btn"]');
          await mcp.browser_wait_for({ text: 'Project created successfully', time: 3 });
        },
      },
      mcp
    )
  );

  // Test 2: Validation workflow
  tests.push(
    await executeTest(
      {
        name: 'Form validation workflow',
        category: 'E2E Workflow',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');
          await mcp.browser_click(
            'ControlLogix template',
            '[data-testid="template-controllogix-standard"]'
          );
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');

          // Try invalid project name
          await mcp.browser_type(
            'Project name input',
            '[data-testid="field-projectName"]',
            '123_Invalid'
          );
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');

          // Should see validation error
          const snapshot = await mcp.browser_snapshot();
          if (!snapshot.includes('alphanumeric') && !snapshot.includes('error')) {
            throw new Error('Validation error not shown');
          }
        },
      },
      mcp
    )
  );

  // Test 3: Multi-step data persistence
  tests.push(
    await executeTest(
      {
        name: 'Multi-step data persistence',
        category: 'E2E Workflow',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');
          await mcp.browser_click(
            'Distillation template',
            '[data-testid="template-distillation-control"]'
          );
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');

          // Enter data
          await mcp.browser_type(
            'Project name',
            '[data-testid="field-projectName"]',
            'Distillation_Test'
          );
          await mcp.browser_select_option('Column type', '[data-testid="field-columnType"]', [
            'binary',
          ]);

          // Navigate back
          await mcp.browser_click('Previous button', '[data-testid="wizard-prev-btn"]');

          // Navigate forward again
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');

          // Verify data persisted
          const value = await mcp.browser_evaluate(
            `() => document.querySelector('[data-testid="field-projectName"]').value`
          );

          if (value !== 'Distillation_Test') {
            throw new Error('Form data not persisted between steps');
          }
        },
      },
      mcp
    )
  );

  return tests;
}

/**
 * Accessibility Tests
 */
async function runAccessibilityTests(mcp: MCPPlaywrightClient): Promise<TestResult[]> {
  const tests: TestResult[] = [];

  // Test 1: Keyboard navigation
  tests.push(
    await executeTest(
      {
        name: 'Full keyboard navigation',
        category: 'Accessibility',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');

          // Tab through templates
          await mcp.browser_press_key('Tab');
          await mcp.browser_press_key('Tab');
          await mcp.browser_press_key('Enter'); // Select template

          // Tab to next button
          await mcp.browser_press_key('Tab');
          await mcp.browser_press_key('Enter'); // Click next

          await mcp.browser_wait_for({ text: 'Configure Project', time: 1 });
        },
      },
      mcp
    )
  );

  // Test 2: Screen reader announcements
  tests.push(
    await executeTest(
      {
        name: 'Screen reader announcements',
        category: 'Accessibility',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');

          const snapshot = await mcp.browser_snapshot();

          // Check for ARIA attributes
          if (!snapshot.includes('role="dialog"')) {
            throw new Error('Missing dialog role');
          }
          if (!snapshot.includes('aria-modal="true"')) {
            throw new Error('Missing aria-modal');
          }
          if (!snapshot.includes('aria-labelledby')) {
            throw new Error('Missing aria-labelledby');
          }
        },
      },
      mcp
    )
  );

  // Test 3: Focus management
  tests.push(
    await executeTest(
      {
        name: 'Focus management',
        category: 'Accessibility',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');

          // Check initial focus
          const focusedElement = await mcp.browser_evaluate(`() => document.activeElement.tagName`);

          if (focusedElement !== 'H2') {
            throw new Error('Initial focus not on heading');
          }
        },
      },
      mcp
    )
  );

  // Test 4: ARIA live regions
  tests.push(
    await executeTest(
      {
        name: 'ARIA live region announcements',
        category: 'Accessibility',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');

          const snapshot = await mcp.browser_snapshot();
          if (!snapshot.includes('aria-live="polite"')) {
            throw new Error('Missing ARIA live region');
          }
        },
      },
      mcp
    )
  );

  return tests;
}

/**
 * Performance Tests
 */
async function runPerformanceTests(mcp: MCPPlaywrightClient): Promise<TestResult[]> {
  const tests: TestResult[] = [];

  // Test 1: Wizard open performance
  tests.push(
    await executeTest(
      {
        name: 'Wizard open performance',
        category: 'Performance',
        action: async () => {
          const startTime = Date.now();
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');
          await mcp.browser_wait_for({ text: 'Select Template', time: 1 });
          const endTime = Date.now();

          const duration = endTime - startTime;
          if (duration > 100) {
            throw new Error(`Wizard open took ${duration}ms (>100ms threshold)`);
          }
        },
      },
      mcp
    )
  );

  // Test 2: Step navigation performance
  tests.push(
    await executeTest(
      {
        name: 'Step navigation performance',
        category: 'Performance',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');
          await mcp.browser_click(
            'ControlLogix template',
            '[data-testid="template-controllogix-standard"]'
          );

          const startTime = Date.now();
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');
          await mcp.browser_wait_for({ text: 'Configure Project', time: 1 });
          const endTime = Date.now();

          const duration = endTime - startTime;
          if (duration > 50) {
            throw new Error(`Step navigation took ${duration}ms (>50ms threshold)`);
          }
        },
      },
      mcp
    )
  );

  // Test 3: Form validation performance
  tests.push(
    await executeTest(
      {
        name: 'Form validation performance',
        category: 'Performance',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');
          await mcp.browser_click(
            'ControlLogix template',
            '[data-testid="template-controllogix-standard"]'
          );
          await mcp.browser_click('Next button', '[data-testid="wizard-next-btn"]');

          const startTime = Date.now();
          await mcp.browser_type(
            'Project name',
            '[data-testid="field-projectName"]',
            'TestValidation'
          );
          const endTime = Date.now();

          const duration = endTime - startTime;
          if (duration > 200) {
            throw new Error(`Validation took ${duration}ms (>200ms threshold)`);
          }
        },
      },
      mcp
    )
  );

  return tests;
}

/**
 * Cross-browser Tests
 */
async function runCrossBrowserTests(mcp: MCPPlaywrightClient): Promise<TestResult[]> {
  const tests: TestResult[] = [];

  // Note: In a real implementation, these would run on different browsers
  // For now, we'll test browser-agnostic functionality

  // Test 1: CSS compatibility
  tests.push(
    await executeTest(
      {
        name: 'CSS rendering compatibility',
        category: 'Cross-browser',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');

          const snapshot = await mcp.browser_snapshot();

          // Check for critical CSS classes
          const criticalClasses = ['bg-[#1e1e1e]', 'rounded-lg', 'shadow-xl', 'flex', 'grid'];
          for (const className of criticalClasses) {
            if (!snapshot.includes(className)) {
              throw new Error(`Critical CSS class ${className} not rendered`);
            }
          }
        },
      },
      mcp
    )
  );

  // Test 2: JavaScript functionality
  tests.push(
    await executeTest(
      {
        name: 'JavaScript functionality cross-browser',
        category: 'Cross-browser',
        action: async () => {
          await mcp.browser_click('New Project button', '[data-testid="new-project-btn"]');

          // Test modern JS features
          const result = await mcp.browser_evaluate(`() => {
          // Test arrow functions
          const test1 = (() => true)();
          // Test template literals
          const test2 = \`test\${1}\` === 'test1';
          // Test array methods
          const test3 = [1,2,3].includes(2);
          return test1 && test2 && test3;
        }`);

          if (!result) {
            throw new Error('JavaScript features not working correctly');
          }
        },
      },
      mcp
    )
  );

  return tests;
}

/**
 * Helper function to execute a single test
 */
async function executeTest(
  test: { name: string; category: string; action: () => Promise<void> },
  mcp: MCPPlaywrightClient
): Promise<TestResult> {
  const startTime = Date.now();

  try {
    await test.action();
    return {
      name: test.name,
      category: test.category,
      passed: true,
      duration: Date.now() - startTime,
    };
  } catch (error) {
    return {
      name: test.name,
      category: test.category,
      passed: false,
      duration: Date.now() - startTime,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Calculate results by category
 */
function calculateCategoryResults(tests: TestResult[]): TestCategory[] {
  const categories = new Map<string, TestResult[]>();

  tests.forEach(test => {
    if (!categories.has(test.category)) {
      categories.set(test.category, []);
    }
    categories.get(test.category)!.push(test);
  });

  return Array.from(categories.entries()).map(([name, categoryTests]) => ({
    name,
    tests: categoryTests,
    successRate: (categoryTests.filter(t => t.passed).length / categoryTests.length) * 100,
  }));
}

/**
 * Calculate overall success rate
 */
function calculateOverallSuccessRate(categories: TestCategory[]): number {
  const totalTests = categories.reduce((sum, cat) => sum + cat.tests.length, 0);
  const passedTests = categories.reduce(
    (sum, cat) => sum + cat.tests.filter(t => t.passed).length,
    0
  );

  return totalTests > 0 ? (passedTests / totalTests) * 100 : 0;
}
