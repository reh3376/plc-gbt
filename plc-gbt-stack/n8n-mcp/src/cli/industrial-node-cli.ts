#!/usr/bin/env node

/**
 * Industrial N8N Custom Node Generator CLI
 * Command-line interface for rapid industrial node development
 * Part of PLC-GBT N8N Integration Framework
 */

import { program } from 'commander';
import * as fs from 'fs/promises';
import * as path from 'path';
import {
  IndustrialNodeGenerator,
  IndustrialNodeSpec,
} from '../templates/industrial-node-generator';

// Mock inquirer functionality for basic CLI
interface PromptQuestion {
  type: string;
  name: string;
  message: string;
  choices?: string[];
  default?: any;
  validate?: (input: string) => boolean | string;
}

const inquirer = {
  prompt: async (questions: PromptQuestion[]): Promise<any> => {
    console.log('Interactive mode not fully implemented in this version.');
    console.log('Please use --spec option with a JSON specification file.');
    return {};
  },
};

interface CLIOptions {
  output?: string;
  interactive?: boolean;
  template?: string;
  validate?: boolean;
  spec?: string;
}

class IndustrialNodeCLI {
  private readonly generator: IndustrialNodeGenerator;
  private readonly outputDir: string;

  constructor(outputDir: string = './generated-nodes') {
    this.generator = new IndustrialNodeGenerator();
    this.outputDir = outputDir;
  }

  /**
   * Interactive node creation wizard
   */
  async createNodeInteractive(): Promise<void> {
    console.log('🏭 Industrial N8N Custom Node Generator');
    console.log('=====================================\n');

    try {
      // Basic node information
      const basicInfo = await inquirer.prompt([
        {
          type: 'input',
          name: 'nodeId',
          message: 'Node ID (camelCase):',
          validate: (input: string) => {
            return /^[a-z][a-zA-Z0-9]*$/.test(input) || 'Please enter a valid camelCase identifier';
          },
        },
        {
          type: 'input',
          name: 'displayName',
          message: 'Display Name:',
          validate: (input: string) => input.trim().length > 0 || 'Display name is required',
        },
        {
          type: 'list',
          name: 'category',
          message: 'Category:',
          choices: [
            'Industrial Control',
            'Data Processing',
            'Analysis',
            'Communication',
            'Safety',
            'Monitoring',
          ],
        },
        {
          type: 'input',
          name: 'description',
          message: 'Description:',
          validate: (input: string) => input.trim().length > 0 || 'Description is required',
        },
        {
          type: 'input',
          name: 'icon',
          message: 'Icon name (without extension):',
          default: 'industrial-node',
        },
      ]);

      // Specialized modes
      const { hasSpecializedModes } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'hasSpecializedModes',
          message: 'Does this node have specialized operation modes?',
          default: true,
        },
      ]);

      const specializedModes = [];
      if (hasSpecializedModes) {
        let addMoreModes = true;
        while (addMoreModes) {
          const mode = await inquirer.prompt([
            {
              type: 'input',
              name: 'modeId',
              message: 'Mode ID (camelCase):',
              validate: (input: string) =>
                /^[a-z][a-zA-Z0-9]*$/.test(input) || 'Valid camelCase required',
            },
            {
              type: 'input',
              name: 'modeName',
              message: 'Mode Display Name:',
              validate: (input: string) => input.trim().length > 0 || 'Mode name is required',
            },
            {
              type: 'input',
              name: 'description',
              message: 'Mode Description:',
              validate: (input: string) => input.trim().length > 0 || 'Description is required',
            },
            {
              type: 'input',
              name: 'targetApplication',
              message: 'Target Application:',
              validate: (input: string) =>
                input.trim().length > 0 || 'Target application is required',
            },
          ]);

          specializedModes.push({
            ...mode,
            additionalParameters: [], // TODO: Add parameter wizard
          });

          const { continueAdding } = await inquirer.prompt([
            {
              type: 'confirm',
              name: 'continueAdding',
              message: 'Add another specialized mode?',
              default: false,
            },
          ]);
          addMoreModes = continueAdding;
        }
      }

      // Create the node specification
      const spec: IndustrialNodeSpec = {
        ...basicInfo,
        specializedModes: specializedModes.length > 0 ? specializedModes : undefined,
        phases: [
          {
            phaseNumber: 1,
            phaseName: 'Basic Implementation',
            description: 'Core node functionality',
            status: 'APPROVED',
            parameters: [],
            validation: [],
          },
        ],
      };

      // Generate the node
      console.log('\n🔧 Generating N8N custom node...\n');
      await this.generateAndSaveNode(spec);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('❌ Error during interactive creation:', errorMessage);
      process.exit(1);
    }
  }

  /**
   * Generate node from JSON specification file
   */
  async createNodeFromSpec(specPath: string): Promise<void> {
    try {
      const specContent = await fs.readFile(specPath, 'utf-8');
      const spec: IndustrialNodeSpec = JSON.parse(specContent);

      console.log(`🏭 Generating node from specification: ${spec.displayName}`);
      await this.generateAndSaveNode(spec);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('❌ Error creating node from spec:', errorMessage);
      process.exit(1);
    }
  }

  /**
   * Generate CSV Dataset Creator proof-of-concept
   */
  async generateCSVDatasetCreatorPOC(): Promise<void> {
    console.log('📊 Generating CSV Dataset Creator Proof-of-Concept...\n');

    try {
      const result = await this.generator.generateCSVDatasetCreatorProofOfConcept();

      const nodeDir = path.join(this.outputDir, 'csv-dataset-creator');
      await fs.mkdir(nodeDir, { recursive: true });

      // Save all generated files
      await Promise.all([
        fs.writeFile(
          path.join(nodeDir, 'CsvDatasetCreator.node.json'),
          JSON.stringify(result.nodeDefinition, null, 2)
        ),
        fs.writeFile(path.join(nodeDir, 'CsvDatasetCreator.node.ts'), result.nodeImplementation),
        fs.writeFile(path.join(nodeDir, 'CsvDatasetCreator.node.test.ts'), result.nodeTest),
        fs.writeFile(path.join(nodeDir, 'README.md'), result.documentation),
      ]);

      console.log('✅ CSV Dataset Creator generated successfully!');
      console.log(`📁 Files saved to: ${nodeDir}`);
      console.log('\n📋 Generated files:');
      console.log('   • CsvDatasetCreator.node.json - Node definition');
      console.log('   • CsvDatasetCreator.node.ts - Implementation');
      console.log('   • CsvDatasetCreator.node.test.ts - Test suite');
      console.log('   • README.md - Documentation');
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('❌ Error generating CSV Dataset Creator:', errorMessage);
      process.exit(1);
    }
  }

  /**
   * List available templates and examples
   */
  async listTemplates(): Promise<void> {
    console.log('🏭 Available Industrial Node Templates:');
    console.log('=====================================\n');

    console.log('📊 Proof-of-Concept Templates:');
    console.log('   • csv-dataset-creator - Complete 7-phase dataset processing node');
    console.log('\n📋 Template Categories:');
    console.log('   • Industrial Control - PID controllers, valve controls');
    console.log('   • Data Processing - Dataset creators, data transformers');
    console.log('   • Analysis - Statistical analysis, trend detection');
    console.log('   • Communication - Protocol handlers, message brokers');
    console.log('   • Safety - Safety interlocks, alarm systems');
    console.log('   • Monitoring - KPI trackers, performance monitors');
    console.log('\n🚀 Usage:');
    console.log('   industrial-node generate --template csv-dataset-creator');
    console.log('   industrial-node create --interactive');
    console.log('   industrial-node create --spec path/to/spec.json');
  }

  /**
   * Validate node specification
   */
  async validateSpec(specPath: string): Promise<void> {
    try {
      const specContent = await fs.readFile(specPath, 'utf-8');
      const spec: IndustrialNodeSpec = JSON.parse(specContent);

      console.log(`🔍 Validating specification: ${spec.displayName}`);

      const validationResults = this.validateNodeSpec(spec);

      if (validationResults.valid) {
        console.log('✅ Specification is valid!');
        console.log(`   • Node ID: ${spec.nodeId}`);
        console.log(`   • Category: ${spec.category}`);
        console.log(`   • Phases: ${spec.phases.length}`);
        console.log(`   • Specialized Modes: ${spec.specializedModes?.length || 0}`);
      } else {
        console.log('❌ Specification validation failed:');
        validationResults.errors.forEach(error => {
          console.log(`   • ${error}`);
        });
        process.exit(1);
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('❌ Error validating specification:', errorMessage);
      process.exit(1);
    }
  }

  /**
   * Generate and save node files
   */
  private async generateAndSaveNode(spec: IndustrialNodeSpec): Promise<void> {
    try {
      const result = await this.generator.generateIndustrialNode(spec);

      const nodeDir = path.join(this.outputDir, spec.nodeId);
      await fs.mkdir(nodeDir, { recursive: true });

      const className = this.pascalCase(spec.nodeId);

      // Save all generated files
      const files = [
        {
          path: path.join(nodeDir, `${className}.node.json`),
          content: JSON.stringify(result.nodeDefinition, null, 2),
        },
        {
          path: path.join(nodeDir, `${className}.node.ts`),
          content: result.nodeImplementation,
        },
        {
          path: path.join(nodeDir, `${className}.node.test.ts`),
          content: result.nodeTest,
        },
        {
          path: path.join(nodeDir, 'README.md'),
          content: result.documentation,
        },
      ];

      if (result.nodeCredentials) {
        files.push({
          path: path.join(nodeDir, `${className}.credentials.ts`),
          content: JSON.stringify(result.nodeCredentials, null, 2),
        });
      }

      await Promise.all(files.map(file => fs.writeFile(file.path, file.content)));

      console.log(`✅ ${spec.displayName} generated successfully!`);
      console.log(`📁 Files saved to: ${nodeDir}`);
      console.log('\n📋 Generated files:');
      files.forEach(file => {
        console.log(`   • ${path.basename(file.path)}`);
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('❌ Generation failed:', errorMessage);
      throw error;
    }
  }

  /**
   * Validate node specification
   */
  private validateNodeSpec(spec: IndustrialNodeSpec): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Basic validation
    if (!spec.nodeId || !/^[a-z][a-zA-Z0-9]*$/.test(spec.nodeId)) {
      errors.push('Node ID must be a valid camelCase identifier');
    }

    if (!spec.displayName?.trim()) {
      errors.push('Display name is required');
    }

    if (!spec.description?.trim()) {
      errors.push('Description is required');
    }

    if (!spec.category) {
      errors.push('Category is required');
    }

    if (!Array.isArray(spec.phases) || spec.phases.length === 0) {
      errors.push('At least one phase is required');
    }

    // Phase validation
    spec.phases?.forEach((phase, index) => {
      if (!phase.phaseName?.trim()) {
        errors.push(`Phase ${index + 1}: Phase name is required`);
      }
      if (!phase.description?.trim()) {
        errors.push(`Phase ${index + 1}: Description is required`);
      }
    });

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  private pascalCase(str: string): string {
    return str
      .split(/[-_\s]+/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join('');
  }
}

// CLI Setup
program
  .name('industrial-node')
  .description('Industrial N8N Custom Node Generator for PLC-GBT')
  .version('1.0.0');

program
  .command('create')
  .description('Create a new industrial N8N custom node')
  .option('-i, --interactive', 'Use interactive mode', false)
  .option('-s, --spec <path>', 'Create from JSON specification file')
  .option('-o, --output <dir>', 'Output directory', './generated-nodes')
  .action(async (options: CLIOptions) => {
    const cli = new IndustrialNodeCLI(options.output);

    if (options.spec) {
      await cli.createNodeFromSpec(options.spec);
    } else {
      await cli.createNodeInteractive();
    }
  });

program
  .command('generate')
  .description('Generate from built-in templates')
  .option('-t, --template <name>', 'Template name')
  .option('-o, --output <dir>', 'Output directory', './generated-nodes')
  .action(async (options: CLIOptions) => {
    const cli = new IndustrialNodeCLI(options.output);

    if (options.template === 'csv-dataset-creator') {
      await cli.generateCSVDatasetCreatorPOC();
    } else {
      console.error(
        '❌ Unknown template. Run "industrial-node templates" to see available templates.'
      );
      process.exit(1);
    }
  });

program
  .command('templates')
  .description('List available templates and examples')
  .action(async () => {
    const cli = new IndustrialNodeCLI();
    await cli.listTemplates();
  });

program
  .command('validate')
  .description('Validate a node specification file')
  .argument('<spec>', 'Path to specification JSON file')
  .action(async (specPath: string) => {
    const cli = new IndustrialNodeCLI();
    await cli.validateSpec(specPath);
  });

// Handle unknown commands
program.on('command:*', () => {
  console.error('❌ Invalid command. See --help for available commands.');
  process.exit(1);
});

if (process.argv.length === 2) {
  program.help();
}

program.parse();

export { IndustrialNodeCLI };
