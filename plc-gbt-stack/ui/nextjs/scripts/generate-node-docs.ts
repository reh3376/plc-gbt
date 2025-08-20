#!/usr/bin/env tsx

/**
 * Node Documentation Generation Script - AI Task Orchestrator TypeScript Implementation
 *
 * @description CLI script for generating comprehensive node documentation
 * @compliance Strict TypeScript - zero `any` types policy
 * @usage npm run docs:generate [options]
 */

import { resolve } from 'path';
import type { IndustrialNodeType } from '../src/api/zod-schemas';
import {
  runDocumentationCLI,
  type GenerationOptions,
  type GenerationResult,
} from '../src/lib/docs/generate-docs-cli';

interface CLIArgs {
  readonly outputDir?: string;
  readonly nodeTypes?: string;
  readonly validateOnly?: boolean;
  readonly verbose?: boolean;
  readonly help?: boolean;
}

/**
 * Parse command line arguments
 */
function parseArgs(): CLIArgs {
  const args: Record<string, string | boolean> = {};
  const argv = process.argv.slice(2);

  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];

    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const nextArg = argv[i + 1];

      if (nextArg && !nextArg.startsWith('--')) {
        args[key] = nextArg;
        i += 2; // Skip both current and next argument
      } else {
        args[key] = true;
        i += 1;
      }
    } else {
      i += 1;
    }
  }

  return args as CLIArgs;
}

/**
 * Display help information
 */
function showHelp(): void {
  console.log(`
🚀 Node Documentation Generator - AI Task Orchestrator

Generate comprehensive documentation for industrial node types.

Usage:
  npm run docs:generate [options]

Options:
  --output-dir <path>     Output directory for generated docs (default: src/app/docs)
  --node-types <types>    Comma-separated list of node types to generate
  --validate-only         Only validate documentation completeness, don't generate
  --verbose               Show detailed output during generation
  --help                  Show this help message

Examples:
  npm run docs:generate
  npm run docs:generate --verbose
  npm run docs:generate --node-types plc-input,pid-controller
  npm run docs:generate --validate-only
  npm run docs:generate --output-dir ./custom-docs --verbose

Node Types:
  Control & Optimization: pid-controller, mpc-controller, imc-controller, etc.
  PLC Integration: plc-input, plc-output, modbus-client, opc-server, etc.
  Data Integration: postgresql-connector, redis-connector, neo4j-connector, etc.
  Machine Learning: narx-neural-network, lstm-model, gaussian-process-regression, etc.
  System Components: data-logger, alarm-handler, hmi-display, custom-logic, etc.
  Workflow Management: workflow-reference, workflow-conditional, workflow-loop, etc.
  Analysis & Reporting: dashboard-generator, pdf-report-generator, kpi-calculator, etc.
`);
}

/**
 * Setup generation options from CLI arguments
 */
function setupOptions(args: CLIArgs): GenerationOptions {
  const outputDir = args.outputDir
    ? resolve(args.outputDir)
    : resolve(__dirname, '../src/app/docs');

  const nodeTypes = args.nodeTypes
    ? (args.nodeTypes.split(',').map(type => type.trim()) as IndustrialNodeType[])
    : undefined;

  return {
    outputDir,
    nodeTypes,
    validateOnly: Boolean(args.validateOnly),
    verbose: Boolean(args.verbose),
  };
}

/**
 * Display generation status
 */
function displayStatus(options: GenerationOptions): void {
  console.log('🚀 Starting Node Documentation Generation...');
  console.log(`📁 Output Directory: ${options.outputDir}`);

  if (options.nodeTypes) {
    console.log(`🎯 Target Node Types: ${options.nodeTypes.join(', ')}`);
  } else {
    console.log('🎯 Target: All configured node types');
  }

  if (options.validateOnly) {
    console.log('🔍 Mode: Validation only');
  }

  console.log('');
}

/**
 * Handle successful generation result
 */
function handleSuccess(result: GenerationResult, options: GenerationOptions): void {
  console.log('');
  console.log('✅ Documentation generation completed successfully!');

  if (!options.validateOnly) {
    console.log(`📝 Generated ${result.generated} documentation pages`);
  }

  if (result.warnings.length > 0) {
    console.log('');
    console.log('⚠️  Warnings:');
    result.warnings.forEach(warning => console.log(`   ${warning}`));
  }

  process.exit(0);
}

/**
 * Handle failed generation result
 */
function handleFailure(result: GenerationResult): void {
  console.log('');
  console.log('❌ Documentation generation failed!');

  if (result.errors.length > 0) {
    console.log('');
    console.log('🚨 Errors:');
    result.errors.forEach(error => console.log(`   ${error}`));
  }

  if (result.warnings.length > 0) {
    console.log('');
    console.log('⚠️  Warnings:');
    result.warnings.forEach(warning => console.log(`   ${warning}`));
  }

  process.exit(1);
}

/**
 * Main execution function
 */
function main(): void {
  const args = parseArgs();

  if (args.help) {
    showHelp();
    return;
  }

  const options = setupOptions(args);
  displayStatus(options);

  try {
    const result = runDocumentationCLI(options);

    if (result.success) {
      handleSuccess(result, options);
    } else {
      handleFailure(result);
    }
  } catch (error) {
    console.error('');
    console.error('💥 Fatal error during documentation generation:');
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

// Run the script
main();
