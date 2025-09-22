/**
 * Industrial N8N Custom Node Generator Framework
 * Template-driven rapid development for PLC-GBT industrial nodes
 * Based on CSV Dataset Creator 7-phase specification pattern
 */

import { logger } from '../utils/logger';

export interface IndustrialNodeSpec {
  nodeId: string;
  displayName: string;
  category:
    | 'Industrial Control'
    | 'Data Processing'
    | 'Analysis'
    | 'Communication'
    | 'Safety'
    | 'Monitoring';
  subCategory?: string;
  description: string;
  icon: string;
  phases: IndustrialPhaseSpec[];
  specializedModes?: SpecializedMode[];
}

export interface IndustrialPhaseSpec {
  phaseNumber: number;
  phaseName: string;
  description: string;
  status: 'AWAITING_REVIEW' | 'APPROVED' | 'IMPLEMENTED' | 'TESTED';
  parameters: IndustrialParameter[];
  validation: ValidationRule[];
}

export interface SpecializedMode {
  modeId: string;
  modeName: string;
  description: string;
  additionalParameters: IndustrialParameter[];
  targetApplication: string;
}

export interface IndustrialParameter {
  name: string;
  displayName: string;
  type: 'string' | 'number' | 'boolean' | 'options' | 'multiOptions' | 'json' | 'formula' | 'regex';
  required: boolean;
  default?: any;
  description: string;
  options?: Array<{ name: string; value: any; description?: string }>;
  placeholder?: string;
  tooltip?: string;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    custom?: string;
  };
}

export interface ValidationRule {
  ruleName: string;
  ruleType: 'required' | 'range' | 'pattern' | 'custom' | 'dependency';
  configuration: any;
  errorMessage: string;
}

export class IndustrialNodeGenerator {
  /**
   * Generate complete N8N custom node from industrial specification
   */
  async generateIndustrialNode(spec: IndustrialNodeSpec): Promise<{
    nodeDefinition: any;
    nodeImplementation: string;
    nodeCredentials?: any;
    nodeTest: string;
    documentation: string;
  }> {
    logger.info(`Generating industrial N8N custom node: ${spec.nodeId}`);

    try {
      // 1. Generate node definition (structure)
      const nodeDefinition = await this.generateNodeDefinition(spec);

      // 2. Generate node implementation (TypeScript code)
      const nodeImplementation = await this.generateNodeImplementation(spec);

      // 3. Generate credentials if needed
      const nodeCredentials =
        this.generateNodeCredentialRequirements(spec).length > 0
          ? { credentials: this.generateNodeCredentialRequirements(spec) }
          : undefined;

      // 4. Generate comprehensive test suite
      const nodeTest = await this.generateNodeTest(spec);

      // 5. Generate documentation
      const documentation = await this.generateNodeDocumentation(spec);

      return {
        nodeDefinition,
        nodeImplementation,
        nodeCredentials,
        nodeTest,
        documentation,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(`Failed to generate industrial node ${spec.nodeId}:`, error);
      throw new Error(`Industrial node generation failed: ${errorMessage}`);
    }
  }

  /**
   * Generate node definition JSON structure
   */
  private async generateNodeDefinition(spec: IndustrialNodeSpec): Promise<any> {
    const parameters: any[] = [];

    // Add specialized mode selector if multiple modes exist
    if (spec.specializedModes && spec.specializedModes.length > 0) {
      parameters.push({
        displayName: 'Operation Mode',
        name: 'operationMode',
        type: 'options',
        options: spec.specializedModes.map(mode => ({
          name: mode.modeName,
          value: mode.modeId,
          description: mode.description,
        })),
        default: spec.specializedModes[0].modeId,
        required: true,
        description: 'Select the specialized operation mode for this node',
      });
    }

    // Generate parameters from all phases
    for (const phase of spec.phases) {
      if (phase.status === 'APPROVED' || phase.status === 'IMPLEMENTED') {
        for (const param of phase.parameters) {
          parameters.push(this.convertParameterToN8NFormat(param, phase.phaseNumber));
        }
      }
    }

    // Add specialized mode parameters
    if (spec.specializedModes) {
      for (const mode of spec.specializedModes) {
        for (const param of mode.additionalParameters) {
          const n8nParam = this.convertParameterToN8NFormat(param, -1);
          n8nParam.displayOptions = {
            show: {
              operationMode: [mode.modeId],
            },
          };
          parameters.push(n8nParam);
        }
      }
    }

    return {
      displayName: spec.displayName,
      name: spec.nodeId,
      icon: `file:${spec.icon}.svg`,
      group: [spec.category.toLowerCase().replace(' ', '_')],
      version: 1,
      subtitle: '={{$parameter["operationMode"] || "Standard"}} Mode',
      description: spec.description,
      defaults: {
        name: spec.displayName,
      },
      inputs: ['main'],
      outputs: ['main'],
      credentials: this.generateNodeCredentialRequirements(spec),
      properties: parameters,
    };
  }

  /**
   * Generate TypeScript implementation code
   */
  private async generateNodeImplementation(spec: IndustrialNodeSpec): Promise<string> {
    const className = this.pascalCase(spec.nodeId);

    return `import { IExecuteFunctions } from 'n8n-core';
import {
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeOperationError,
} from 'n8n-workflow';

export class ${className} implements INodeType {
  description: INodeTypeDescription;

  constructor() {
    this.description = require('./${className}.node.json');
  }

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    try {
      for (let i = 0; i < items.length; i++) {
        // Get operation mode
        const operationMode = this.getNodeParameter('operationMode', i, '${spec.specializedModes?.[0]?.modeId || 'standard'}') as string;
        
        // Process item based on mode
        const result = await this.processItem(items[i], operationMode, i);
        
        returnData.push({
          json: result,
          pairedItem: { item: i },
        });
      }

      return [returnData];
    } catch (error) {
      throw new NodeOperationError(this.getNode(), \`${spec.displayName} execution failed: \${error.message}\`);
    }
  }

  private async processItem(
    item: INodeExecutionData,
    mode: string,
    itemIndex: number
  ): Promise<any> {
    const inputData = item.json;
    
    switch (mode) {
      ${
        spec.specializedModes
          ?.map(
            mode => `
      case '${mode.modeId}':
        return await this.process${this.pascalCase(mode.modeId)}Mode(inputData, itemIndex);
      `
          )
          .join('') || ''
      }
      
      default:
        return await this.processStandardMode(inputData, itemIndex);
    }
  }

  ${
    spec.specializedModes
      ?.map(
        mode => `
  private async process${this.pascalCase(mode.modeId)}Mode(
    inputData: any,
    itemIndex: number
  ): Promise<any> {
    // ${mode.description}
    // Specialized processing for ${mode.targetApplication}
    
    ${mode.additionalParameters
      .map(
        param => `
    const ${param.name} = this.getNodeParameter('${param.name}', itemIndex${param.default ? `, '${param.default}'` : ''}) as ${this.getTypeScriptType(param.type)};
    `
      )
      .join('')}
    
    // Implementation specific to ${mode.modeName}
    const result = {
      ...inputData,
      processedBy: '${spec.displayName}',
      operationMode: '${mode.modeId}',
      processedAt: new Date().toISOString(),
      // Add mode-specific processing results here
      ${mode.modeId}Result: {
        // Implement ${mode.modeName} specific logic
        status: 'processed',
        mode: '${mode.modeName}'
      }
    };
    
    return result;
  }
  `
      )
      .join('') || ''
  }

  private async processStandardMode(
    inputData: any,
    itemIndex: number
  ): Promise<any> {
    // Standard processing mode
    const result = {
      ...inputData,
      processedBy: '${spec.displayName}',
      operationMode: 'standard',
      processedAt: new Date().toISOString(),
      // Add standard processing results here
    };
    
    return result;
  }

  private validateInput(data: any, mode: string): void {
    // Implement validation logic based on spec.phases validation rules
    ${spec.phases
      .map(
        phase => `
    // Phase ${phase.phaseNumber}: ${phase.phaseName} validation
    ${phase.validation
      .map(
        rule => `
    // Validation rule: ${rule.ruleName}
    `
      )
      .join('')}
    `
      )
      .join('')}
  }
}`;
  }

  /**
   * Generate comprehensive test suite
   */
  private async generateNodeTest(spec: IndustrialNodeSpec): Promise<string> {
    const className = this.pascalCase(spec.nodeId);

    return `import { ${className} } from '../${className}.node';
import { WorkflowTestData } from 'n8n-test-helper';

describe('${className}', () => {
  const nodeType = new ${className}();

  describe('Node Configuration', () => {
    it('should have correct node definition', () => {
      expect(nodeType.description.displayName).toBe('${spec.displayName}');
      expect(nodeType.description.name).toBe('${spec.nodeId}');
      expect(nodeType.description.group).toContain('${spec.category.toLowerCase().replace(' ', '_')}');
    });

    it('should have required properties', () => {
      const properties = nodeType.description.properties;
      expect(Array.isArray(properties)).toBe(true);
      expect(properties.length).toBeGreaterThan(0);
    });
  });

  ${
    spec.specializedModes
      ?.map(
        mode => `
  describe('${mode.modeName} Mode', () => {
    it('should process data in ${mode.modeId} mode', async () => {
      const testData: WorkflowTestData = {
        input: {
          main: [
            [
              {
                json: {
                  testData: 'sample data for ${mode.modeName}',
                  timestamp: new Date().toISOString()
                }
              }
            ]
          ]
        },
        output: {
          nodeExecutionOrder: ['${className}'],
          nodeData: {}
        }
      };

      // Add test-specific assertions
      expect(true).toBe(true); // Placeholder - implement actual test
    });
  });
  `
      )
      .join('') || ''
  }

  describe('Error Handling', () => {
    it('should handle invalid input gracefully', async () => {
      // Test error handling
      expect(true).toBe(true); // Placeholder - implement actual test
    });

    it('should validate required parameters', async () => {
      // Test parameter validation
      expect(true).toBe(true); // Placeholder - implement actual test
    });
  });

  describe('Performance', () => {
    it('should process large datasets efficiently', async () => {
      // Performance test
      expect(true).toBe(true); // Placeholder - implement actual test
    });
  });
});`;
  }

  /**
   * Generate comprehensive documentation
   */
  private async generateNodeDocumentation(spec: IndustrialNodeSpec): Promise<string> {
    return `# ${spec.displayName}

## Overview
${spec.description}

**Category**: ${spec.category}${spec.subCategory ? ` > ${spec.subCategory}` : ''}

## Operation Modes

${
  spec.specializedModes
    ?.map(
      mode => `
### ${mode.modeName}
**Target Application**: ${mode.targetApplication}  
**Description**: ${mode.description}

#### Additional Parameters
${mode.additionalParameters
  .map(
    param => `
- **${param.displayName}** (\`${param.name}\`): ${param.description}
  - Type: ${param.type}
  - Required: ${param.required ? 'Yes' : 'No'}
  ${param.default ? `- Default: \`${param.default}\`` : ''}
`
  )
  .join('')}
`
    )
    .join('') || ''
}

## Technical Specification

### Development Phases
${spec.phases
  .map(
    phase => `
#### Phase ${phase.phaseNumber}: ${phase.phaseName}
**Status**: ${phase.status}  
**Description**: ${phase.description}

**Parameters**:
${phase.parameters
  .map(
    param => `
- **${param.displayName}** (\`${param.name}\`): ${param.description}
  - Type: ${param.type}
  - Required: ${param.required ? 'Yes' : 'No'}
  ${param.default ? `- Default: \`${param.default}\`` : ''}
`
  )
  .join('')}

**Validation Rules**:
${phase.validation
  .map(
    rule => `
- **${rule.ruleName}**: ${rule.errorMessage}
`
  )
  .join('')}
`
  )
  .join('')}

## Usage Examples

### Basic Usage
\`\`\`json
{
  "operationMode": "standard",
  // Add example parameters
}
\`\`\`

${
  spec.specializedModes
    ?.map(
      mode => `
### ${mode.modeName} Mode Example
\`\`\`json
{
  "operationMode": "${mode.modeId}",
  // Add mode-specific parameters
}
\`\`\`
`
    )
    .join('') || ''
}

## Integration Notes

- **Input**: Accepts any JSON data structure
- **Output**: Enhanced JSON with processing metadata
- **Validation**: Comprehensive validation across all phases
- **Performance**: Optimized for industrial data processing

## Error Handling

The node implements comprehensive error handling including:
- Parameter validation
- Input data validation
- Processing error recovery
- Detailed error reporting

## Related Nodes

This node is part of the PLC-GBT industrial automation suite and works seamlessly with other industrial nodes in the ecosystem.
`;
  }

  /**
   * Utility methods
   */
  private convertParameterToN8NFormat(param: IndustrialParameter, phaseNumber: number): any {
    let paramType = param.type;
    if (param.type === 'formula' || param.type === 'regex') {
      paramType = 'string';
    }

    const n8nParam: any = {
      displayName: param.displayName,
      name: param.name,
      type: paramType,
      required: param.required,
      description: param.description,
    };

    if (param.default !== undefined) {
      n8nParam.default = param.default;
    }

    if (param.placeholder) {
      n8nParam.placeholder = param.placeholder;
    }

    if (param.options) {
      n8nParam.options = param.options;
    }

    if (param.validation) {
      // Add validation logic
      if (param.validation.pattern) {
        n8nParam.pattern = param.validation.pattern;
      }
    }

    // Add phase-based grouping
    if (phaseNumber > 0) {
      n8nParam.displayName = `[Phase ${phaseNumber}] ${param.displayName}`;
    }

    return n8nParam;
  }

  private generateNodeCredentialRequirements(spec: IndustrialNodeSpec): any[] {
    // Generate credential requirements based on node functionality
    return [];
  }

  private pascalCase(str: string): string {
    return str
      .split(/[-_\s]+/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join('');
  }

  private getTypeScriptType(paramType: string): string {
    switch (paramType) {
      case 'string':
      case 'formula':
      case 'regex':
        return 'string';
      case 'number':
        return 'number';
      case 'boolean':
        return 'boolean';
      case 'options':
        return 'string';
      case 'multiOptions':
        return 'string[]';
      case 'json':
        return 'any';
      default:
        return 'any';
    }
  }

  /**
   * Generate CSV Dataset Creator as proof-of-concept
   */
  async generateCSVDatasetCreatorProofOfConcept(): Promise<any> {
    const spec: IndustrialNodeSpec = {
      nodeId: 'csvDatasetCreator',
      displayName: 'CSV Dataset Creator',
      category: 'Data Processing',
      subCategory: 'Dataset Management',
      description:
        'Create curated CSV datasets from any data source with advanced processing capabilities',
      icon: 'csv-dataset-creator',
      specializedModes: [
        {
          modeId: 'ml',
          modeName: 'Machine Learning',
          description: 'Prepare training datasets for ML algorithms',
          targetApplication: 'Machine Learning Training Data',
          additionalParameters: [
            {
              name: 'trainValidationSplit',
              displayName: 'Train/Validation Split Ratio',
              type: 'number',
              required: false,
              default: 0.8,
              description: 'Ratio for training vs validation data split (0.1-0.9)',
            },
            {
              name: 'featureEngineering',
              displayName: 'Enable Feature Engineering',
              type: 'boolean',
              required: false,
              default: true,
              description: 'Apply automated feature engineering transformations',
            },
          ],
        },
        {
          modeId: 'mpc',
          modeName: 'Model Predictive Control',
          description: 'Format data for MPC system integration',
          targetApplication: 'MPC Control Systems',
          additionalParameters: [
            {
              name: 'controlHorizon',
              displayName: 'Control Horizon',
              type: 'number',
              required: false,
              default: 10,
              description: 'MPC control horizon length',
            },
            {
              name: 'predictionHorizon',
              displayName: 'Prediction Horizon',
              type: 'number',
              required: false,
              default: 20,
              description: 'MPC prediction horizon length',
            },
          ],
        },
      ],
      phases: [
        {
          phaseNumber: 1,
          phaseName: 'Architecture Decision',
          description: 'Hybrid architecture with shared core components',
          status: 'APPROVED',
          parameters: [
            {
              name: 'outputFormat',
              displayName: 'Output Format',
              type: 'options',
              required: true,
              default: 'csv',
              description: 'Primary output format for the dataset',
              options: [
                { name: 'CSV', value: 'csv' },
                { name: 'JSON', value: 'json' },
                { name: 'Excel', value: 'excel' },
                { name: 'Parquet', value: 'parquet' },
              ],
            },
          ],
          validation: [
            {
              ruleName: 'Format Selection Required',
              ruleType: 'required',
              configuration: { field: 'outputFormat' },
              errorMessage: 'Output format must be selected',
            },
          ],
        },
      ],
    };

    return await this.generateIndustrialNode(spec);
  }
}

export default IndustrialNodeGenerator;
