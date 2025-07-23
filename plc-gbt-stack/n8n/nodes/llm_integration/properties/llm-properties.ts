/**
 * PLC Industrial LLM Node Properties
 * Extracted property definitions for reduced complexity
 */

import { INodeProperties } from 'n8n-workflow';
import { PropertyBuilder } from '../../shared/utils';
import { LLMOperations, OperationConfig } from '../../shared/types';

export class LLMProperties {
  
  static getOperations(): OperationConfig[] {
    return [
      {
        name: 'Control Theory Analysis',
        value: LLMOperations.CONTROL_ANALYSIS,
        description: 'Analyze control system behavior and performance'
      },
      {
        name: 'PID Tuning Recommendation',
        value: LLMOperations.PID_TUNING,
        description: 'Get PID controller tuning recommendations'
      },
      {
        name: 'Safety Assessment',
        value: LLMOperations.SAFETY_ASSESSMENT,
        description: 'Assess safety implications of control strategies'
      },
      {
        name: 'Process Optimization',
        value: LLMOperations.PROCESS_OPTIMIZATION,
        description: 'Optimize industrial process parameters'
      },
      {
        name: 'Fault Diagnosis',
        value: LLMOperations.FAULT_DIAGNOSIS,
        description: 'Diagnose control system faults and issues'
      },
      {
        name: 'Custom Query',
        value: LLMOperations.CUSTOM_QUERY,
        description: 'Custom industrial control question'
      }
    ];
  }
  
  static getAllProperties(): INodeProperties[] {
    const operations = this.getOperations();
    
    return [
      PropertyBuilder.createOperationProperty(operations),
      
      // Process Description (for analysis operations)
      PropertyBuilder.createTextAreaProperty(
        'Process Description',
        'processDescription',
        {
          placeholder: 'Describe the industrial process (e.g., "Distillation column temperature control with cascade control scheme")',
          description: 'Detailed description of the industrial process to analyze',
          displayOptions: {
            show: {
              operation: [
                LLMOperations.CONTROL_ANALYSIS, 
                LLMOperations.SAFETY_ASSESSMENT, 
                LLMOperations.PROCESS_OPTIMIZATION
              ]
            }
          }
        }
      ),
      
      // PID Tuning Parameters
      PropertyBuilder.createStringProperty(
        'Process Variable',
        'processVariable',
        {
          placeholder: 'Temperature, Pressure, Flow, Level',
          description: 'Process variable being controlled',
          displayOptions: {
            show: {
              operation: [LLMOperations.PID_TUNING]
            }
          }
        }
      ),
      
      PropertyBuilder.createTextAreaProperty(
        'Process Characteristics',
        'processCharacteristics',
        {
          placeholder: 'Process gain, time constant, dead time, etc.',
          description: 'Known process characteristics for tuning',
          displayOptions: {
            show: {
              operation: [LLMOperations.PID_TUNING]
            }
          }
        }
      ),
      
      // Custom Query
      PropertyBuilder.createTextAreaProperty(
        'Custom Question',
        'customQuery',
        {
          placeholder: 'Ask any industrial control theory question...',
          description: 'Custom question about industrial control systems',
          displayOptions: {
            show: {
              operation: [LLMOperations.CUSTOM_QUERY]
            }
          }
        }
      ),
      
      // Model Configuration
      PropertyBuilder.createOptionsProperty(
        'Model Selection',
        'modelSelection',
        [
          {
            name: 'GPT-4o Industrial (Recommended)',
            value: 'gpt-4o-industrial',
            description: 'Fine-tuned model for industrial control'
          },
          {
            name: 'GPT-4o Base',
            value: 'gpt-4o',
            description: 'Base model with general knowledge'
          },
          {
            name: 'GPT-3.5 Turbo',
            value: 'gpt-3.5-turbo',
            description: 'Faster, lower-cost option'
          }
        ],
        'gpt-4o-industrial'
      ),
      
      PropertyBuilder.createOptionsProperty(
        'Analysis Depth',
        'analysisDepth',
        [
          {
            name: 'Standard',
            value: 'standard',
            description: 'Standard analysis depth'
          },
          {
            name: 'Detailed',
            value: 'detailed',
            description: 'In-depth technical analysis'
          },
          {
            name: 'Quick',
            value: 'quick',
            description: 'Fast overview analysis'
          }
        ],
        'standard'
      ),
      
      PropertyBuilder.createNumberProperty(
        'Temperature',
        'temperature',
        0.7,
        {
          min: 0,
          max: 2,
          description: 'Controls randomness of responses (0 = deterministic, 2 = very random)'
        }
      ),
      
      PropertyBuilder.createNumberProperty(
        'Max Tokens',
        'maxTokens',
        2000,
        {
          min: 100,
          max: 4000,
          description: 'Maximum tokens in the response'
        }
      )
    ];
  }
} 