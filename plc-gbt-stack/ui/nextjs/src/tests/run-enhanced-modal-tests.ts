/**
 * Enhanced Modal Test Runner - AI Task Orchestrator Implementation
 *
 * @description Script to run comprehensive modal drag/resize tests with MCP browser automation
 * @compliance Two-phase testing protocol with automated validation
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// ========================================
// Test Configuration
// ========================================

interface TestResult {
  readonly suiteName: string;
  readonly totalTests: number;
  readonly passedTests: number;
  readonly failedTests: number;
  readonly successRate: number;
  readonly duration: number;
}

interface AutomatedTestResults {
  readonly overallSuccessRate: number;
  readonly suiteResults: ReadonlyArray<TestResult>;
  readonly totalDuration: number;
  readonly readyForUserTesting: boolean;
}

// ========================================
// Test Execution
// ========================================

async function runEnhancedModalTests(): Promise<AutomatedTestResults> {
  console.log('🚀 Starting Enhanced Modal Automated Testing Suite');
  console.log('📋 Following AI Task Orchestrator Two-Phase Testing Protocol');

  const startTime = Date.now();

  try {
    // Run Playwright tests for enhanced modal functionality
    console.log('\n🤖 Phase 1: Automated Testing with Playwright MCP...');

    console.log('⚠️  Running tests in controlled mode (single browser, no parallel execution)');
    console.log('🌐 Using only Chromium browser to prevent browser explosion');

    const { stdout, stderr } = await execAsync(
      'npx playwright test src/tests/enhanced-modal-drag-resize.test.ts --reporter=json --project=chromium --workers=1',
      {
        cwd: process.cwd(),
        timeout: 180000, // 3 minutes timeout (reduced from 5 minutes)
        killSignal: 'SIGKILL' as const, // Ensure processes are killed if timeout
      }
    );

    // Parse test results
    const testOutput = JSON.parse(stdout);
    const suiteResults: TestResult[] = [];

    // Process test suites
    for (const suite of testOutput.suites || []) {
      const totalTests = suite.specs?.length || 0;
      const passedTests =
        suite.specs?.filter(
          (spec: Record<string, unknown>) =>
            Array.isArray(spec.tests) &&
            spec.tests.every((test: Record<string, unknown>) => test.status === 'passed')
        ).length || 0;

      suiteResults.push({
        suiteName: suite.title || 'Unknown Suite',
        totalTests,
        passedTests,
        failedTests: totalTests - passedTests,
        successRate: totalTests > 0 ? (passedTests / totalTests) * 100 : 0,
        duration: suite.duration || 0,
      });
    }

    const totalDuration = Date.now() - startTime;
    const overallSuccessRate =
      suiteResults.length > 0
        ? suiteResults.reduce((sum, suite) => sum + suite.successRate, 0) / suiteResults.length
        : 0;

    // Display results
    displayTestResults({
      overallSuccessRate,
      suiteResults,
      totalDuration,
      readyForUserTesting: overallSuccessRate >= 95,
    });

    return {
      overallSuccessRate,
      suiteResults,
      totalDuration,
      readyForUserTesting: overallSuccessRate >= 95,
    };
  } catch (error) {
    console.error('❌ Automated testing failed:', error);

    return {
      overallSuccessRate: 0,
      suiteResults: [],
      totalDuration: Date.now() - startTime,
      readyForUserTesting: false,
    };
  }
}

// ========================================
// Results Display
// ========================================

function displayTestResults(results: AutomatedTestResults): void {
  console.log('\n📊 AUTOMATED TEST RESULTS:');
  console.log('='.repeat(50));

  console.log(`🎯 Overall Success Rate: ${results.overallSuccessRate.toFixed(1)}%`);
  console.log(`⏱️  Total Duration: ${(results.totalDuration / 1000).toFixed(1)}s`);

  console.log('\n📋 Test Suite Breakdown:');
  results.suiteResults.forEach((suite, index) => {
    const status = suite.successRate >= 95 ? '✅' : '❌';
    console.log(`${status} ${suite.suiteName}:`);
    console.log(
      `   Success Rate: ${suite.successRate.toFixed(1)}% (${suite.passedTests}/${suite.totalTests})`
    );
    console.log(`   Duration: ${(suite.duration / 1000).toFixed(1)}s`);
  });

  if (results.readyForUserTesting) {
    console.log('\n🎉 AUTOMATED TESTING PASSED!');
    console.log('✅ Phase 1 Complete: >95% automated success rate achieved');
    console.log('🧑‍💻 Phase 2 Required: User Interactive Testing');
    displayUserTestingInstructions();
  } else {
    console.log('\n⚠️ AUTOMATED TESTING REQUIREMENTS NOT MET');
    console.log(
      `❌ Required: >95% success rate, Achieved: ${results.overallSuccessRate.toFixed(1)}%`
    );
    console.log('🔧 Fix automated test failures before user testing');
  }
}

// ========================================
// User Testing Preparation
// ========================================

function displayUserTestingInstructions(): void {
  console.log('\n🧪 USER INTERACTIVE TESTING REQUIRED:');
  console.log('='.repeat(50));
  console.log('📋 Automated validation complete - now requiring user validation:');
  console.log('📋 Please test the following functionality in your browser:');

  const testItems = [
    {
      category: 'Drag Functionality',
      tests: [
        'Click and drag modal header to move modal around screen',
        'Verify modal stays within viewport boundaries',
        'Test snap-to-edges functionality (drag near screen edges)',
        'Confirm smooth dragging performance without lag',
      ],
    },
    {
      category: 'Resize Functionality',
      tests: [
        'Hover over modal edges to see resize handles appear',
        'Resize modal horizontally using right edge handle',
        'Resize modal vertically using bottom edge handle',
        'Resize modal diagonally using corner handles',
        'Verify minimum size constraints are enforced',
        'Check resize indicator shows correct dimensions',
      ],
    },
    {
      category: 'State Management',
      tests: [
        'Click maximize button to fullscreen modal',
        'Click restore button to return to normal size',
        'Verify dragging is disabled when maximized',
        'Verify resize handles are hidden when maximized',
        'Test modal maintains content during all operations',
      ],
    },
    {
      category: 'Visual Quality',
      tests: [
        'Confirm all animations are smooth and responsive',
        'Verify no visual glitches during drag/resize operations',
        'Check modal content remains readable during operations',
        'Ensure professional appearance across all states',
      ],
    },
    {
      category: 'Accessibility',
      tests: [
        'Test keyboard navigation with Tab key',
        'Verify screen reader compatibility',
        'Check focus management during state changes',
        'Confirm ARIA labels are present and correct',
      ],
    },
  ];

  testItems.forEach((category, index) => {
    console.log(`\n${index + 1}. ${category.category}:`);
    category.tests.forEach((test, testIndex) => {
      console.log(`   ${String.fromCharCode(97 + testIndex)}. ${test}`);
    });
  });

  console.log('\n⚠️  CRITICAL: Even though automated tests passed, real user interaction');
  console.log('   may reveal issues that automation cannot detect:');
  console.log('   - Intuitive UX and user flow');
  console.log('   - Visual design and aesthetic issues');
  console.log('   - Real-world usage patterns');
  console.log('   - Subjective user experience quality');

  console.log('\n📝 Please complete ALL tests above and report:');
  console.log('   ✅ "All tests passed" - Ready to mark task complete');
  console.log('   ❌ "Test X failed: [description]" - Issues need fixing');
}

// ========================================
// Main Execution
// ========================================

if (require.main === module) {
  runEnhancedModalTests()
    .then(results => {
      process.exit(results.readyForUserTesting ? 0 : 1);
    })
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

export { runEnhancedModalTests, type AutomatedTestResults, type TestResult };
