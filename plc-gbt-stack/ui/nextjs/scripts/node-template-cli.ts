#!/usr/bin/env npx tsx

/**
 * Node Template CLI - AI Task Orchestrator TypeScript Implementation
 *
 * @description Command-line interface for template-driven node creation
 * @compliance Strict TypeScript - zero `any` types policy
 * @features Interactive node creation, batch operations, validation
 */

import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

import { type IndustrialNodeType } from '../src/api/zod-schemas';
import {
  createBatchRegistration,
  nodeRegistrationAutomation,
  type NodeRegistrationConfig,
} from '../src/lib/schemas/node-registration-automation';
import {
  NODE_TEMPLATES,
  type NodeTemplateConfig,
} from '../src/lib/schemas/node-template-generator';

// CLI command interface
interface CLICommand {
  readonly name: string;
  readonly description: string;
  readonly execute: (args: string[]) => Promise<void>;
}

// Available CLI commands
const CLI_COMMANDS: ReadonlyArray<CLICommand> = [
  {
    name: 'create',
    description: 'Create a new node type using templates',
    execute: async args => {
      if (args.length < 4) {
        console.log('Usage: create <nodeType> <title> <description> <category> [template]');
        console.log(
          'Categories: control, data-integration, ml-ai, plc-integration, workflow, reporting, analysis'
        );
        console.log('Templates:', Object.keys(NODE_TEMPLATES).join(', '));
        return;
      }

      const [nodeType, title, description, category, templateName] = args;

      const config: NodeRegistrationConfig = {
        nodeType: nodeType as IndustrialNodeType,
        title,
        description,
        category: category as NodeTemplateConfig['category'],
        complexity: 'intermediate',
        templateName,
        generateDocumentation: true,
        registerInOpenAPI: true,
        addToWorkflowStore: true,
      };

      console.log(`🚀 Creating node: ${nodeType}`);
      console.log(`   Title: ${title}`);
      console.log(`   Category: ${category}`);
      console.log(`   Template: ${templateName || 'auto-generated'}`);

      const result = await nodeRegistrationAutomation.registerNode(config);

      if (result.success) {
        console.log(`✅ Node created successfully!`);
        console.log(`📁 Generated files: ${result.generatedFiles.length}`);
        result.generatedFiles.forEach(file => console.log(`   - ${file}`));
      } else {
        console.error(`❌ Failed to create node:`);
        result.errors.forEach(error => console.error(`   - ${error}`));
      }
    },
  },

  {
    name: 'batch',
    description: 'Create multiple nodes from a JSON configuration file',
    execute: async args => {
      if (args.length < 1) {
        console.log('Usage: batch <configFile.json>');
        console.log('Config file should contain an array of node configurations');
        return;
      }

      const configFile = args[0];

      try {
        const configPath = join(process.cwd(), configFile);
        const configContent = readFileSync(configPath, 'utf-8');
        const configs: NodeRegistrationConfig[] = JSON.parse(configContent);

        console.log(`🚀 Starting batch creation of ${configs.length} nodes...`);

        const batch = createBatchRegistration();
        configs.forEach(config => batch.addNode(config));

        const result = await batch.execute();

        console.log(`✅ Batch creation complete:`);
        console.log(`   Successful: ${result.successful.length}`);
        console.log(`   Failed: ${result.failed.length}`);
        console.log(`   Total files generated: ${result.totalGenerated * 3}`);

        if (result.failed.length > 0) {
          console.log(`❌ Failed nodes:`);
          result.failed.forEach(failure => {
            console.log(`   - ${failure.nodeType}: ${failure.error}`);
          });
        }
      } catch (error) {
        console.error(
          `❌ Failed to process batch file: ${
            error instanceof Error ? error.message : 'Unknown error'
          }`
        );
      }
    },
  },

  {
    name: 'templates',
    description: 'List available node templates',
    execute: async () => {
      console.log('📋 Available Node Templates:');
      console.log('');

      Object.entries(NODE_TEMPLATES).forEach(([templateName, template]) => {
        console.log(`🔧 ${templateName}`);
        console.log(`   Category: ${template.category}`);
        console.log(`   Complexity: ${template.complexity}`);
        console.log(`   Connection: ${template.hasConnection ? 'Yes' : 'No'}`);
        console.log(`   Fields: ${template.commonFields.length + template.specificFields.length}`);
        console.log('');
      });

      console.log(`Total templates: ${Object.keys(NODE_TEMPLATES).length}`);
    },
  },

  {
    name: 'validate',
    description: 'Validate a node configuration without creating it',
    execute: async args => {
      if (args.length < 4) {
        console.log('Usage: validate <nodeType> <title> <description> <category>');
        return;
      }

      const [nodeType, title, description, category] = args;

      const config: NodeRegistrationConfig = {
        nodeType: nodeType as IndustrialNodeType,
        title,
        description,
        category: category as NodeTemplateConfig['category'],
        complexity: 'intermediate',
        generateDocumentation: false,
        registerInOpenAPI: false,
        addToWorkflowStore: false,
      };

      const validation = nodeRegistrationAutomation.validateRegistrationConfig(config);

      console.log(`🔍 Validation Results for ${nodeType}:`);
      console.log(`   Valid: ${validation.isValid ? '✅' : '❌'}`);

      if (validation.errors.length > 0) {
        console.log(`   Errors:`);
        validation.errors.forEach(error => console.log(`     - ${error}`));
      }

      if (validation.warnings.length > 0) {
        console.log(`   Warnings:`);
        validation.warnings.forEach(warning => console.log(`     - ${warning}`));
      }

      if (validation.isValid) {
        console.log(`✅ Configuration is valid and ready for creation`);
      }
    },
  },

  {
    name: 'stats',
    description: 'Show template system statistics',
    execute: async () => {
      const stats = nodeRegistrationAutomation.getRegistrationStats();

      console.log('📊 Template System Statistics:');
      console.log('');
      console.log(`   Available Templates: ${stats.availableTemplates}`);
      console.log(`   Validation Rules: ${stats.validationRules}`);
      console.log(`   Connection Tests: ${stats.connectionTests}`);
      console.log(`   Generated Files: ${stats.generatedFiles}`);
      console.log('');

      console.log('🔧 Template Categories:');
      Object.entries(NODE_TEMPLATES).forEach(([name, template]) => {
        console.log(`   ${name}: ${template.category} (${template.complexity})`);
      });
    },
  },

  {
    name: 'help',
    description: 'Show help information',
    execute: async () => {
      console.log('🚀 Node Template CLI - AI Task Orchestrator TypeScript Implementation');
      console.log('');
      console.log('Available Commands:');
      console.log('');

      CLI_COMMANDS.forEach(command => {
        console.log(`   ${command.name.padEnd(12)} - ${command.description}`);
      });

      console.log('');
      console.log('Examples:');
      console.log(
        '   npx tsx scripts/node-template-cli.ts create my-sensor "My Sensor" "Custom sensor node" plc-integration'
      );
      console.log('   npx tsx scripts/node-template-cli.ts batch ./configs/new-nodes.json');
      console.log('   npx tsx scripts/node-template-cli.ts templates');
      console.log(
        '   npx tsx scripts/node-template-cli.ts validate my-node "My Node" "Description" control'
      );
      console.log('');
    },
  },
];

/**
 * Main CLI function
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('🚀 Node Template CLI');
    console.log('Use "help" command for usage information');
    return;
  }

  const commandName = args[0];
  const commandArgs = args.slice(1);

  const command = CLI_COMMANDS.find(cmd => cmd.name === commandName);

  if (!command) {
    console.error(`❌ Unknown command: ${commandName}`);
    console.log('Available commands:', CLI_COMMANDS.map(cmd => cmd.name).join(', '));
    console.log('Use "help" for more information');
    process.exit(1);
  }

  try {
    await command.execute(commandArgs);
  } catch (error) {
    console.error(`❌ Command failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    process.exit(1);
  }
}

// Example configuration file for batch operations
const EXAMPLE_BATCH_CONFIG = [
  {
    nodeType: 'custom-sensor',
    title: 'Custom Sensor',
    description: 'User-defined sensor for specialized measurements',
    category: 'plc-integration',
    complexity: 'basic',
    templateName: 'basic-control',
    generateDocumentation: true,
    registerInOpenAPI: true,
    addToWorkflowStore: true,
  },
  {
    nodeType: 'advanced-optimizer',
    title: 'Advanced Optimizer',
    description: 'Multi-objective optimization algorithm',
    category: 'ml-ai',
    complexity: 'advanced',
    templateName: 'ml-algorithm',
    generateDocumentation: true,
    registerInOpenAPI: true,
    addToWorkflowStore: true,
  },
];

/**
 * Generate example configuration file
 */
function generateExampleConfig(): void {
  const configPath = join(process.cwd(), 'example-batch-config.json');
  writeFileSync(configPath, JSON.stringify(EXAMPLE_BATCH_CONFIG, null, 2), 'utf-8');
  console.log(`📄 Generated example configuration: ${configPath}`);
}

// Run CLI if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('CLI Error:', error);
    process.exit(1);
  });
}

export { generateExampleConfig, main as runNodeTemplateCLI };
