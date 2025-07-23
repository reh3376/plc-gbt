/**
 * N8N Node Property Builders
 * Reusable property configuration builders
 */

import { INodeProperties } from 'n8n-workflow';
import { OperationConfig } from '../types';

export class PropertyBuilder {
  
  static createOperationProperty(
    operations: OperationConfig[], 
    defaultOperation: string = operations[0]?.value
  ): INodeProperties {
    return {
      displayName: 'Operation',
      name: 'operation',
      type: 'options',
      options: operations,
      default: defaultOperation,
      description: 'Operation to perform'
    };
  }
  
  static createStringProperty(
    displayName: string,
    name: string,
    options: {
      placeholder?: string;
      description?: string;
      required?: boolean;
      displayOptions?: any;
      typeOptions?: any;
    } = {}
  ): INodeProperties {
    return {
      displayName,
      name,
      type: 'string',
      default: '',
      placeholder: options.placeholder || '',
      description: options.description || '',
      required: options.required || false,
      displayOptions: options.displayOptions,
      typeOptions: options.typeOptions
    };
  }
  
  static createNumberProperty(
    displayName: string,
    name: string,
    defaultValue: number = 0,
    options: {
      min?: number;
      max?: number;
      description?: string;
      displayOptions?: any;
    } = {}
  ): INodeProperties {
    return {
      displayName,
      name,
      type: 'number',
      default: defaultValue,
      typeOptions: {
        minValue: options.min,
        maxValue: options.max
      },
      description: options.description || '',
      displayOptions: options.displayOptions
    };
  }
  
  static createOptionsProperty(
    displayName: string,
    name: string,
    options: OperationConfig[],
    defaultValue?: string
  ): INodeProperties {
    return {
      displayName,
      name,
      type: 'options',
      options,
      default: defaultValue || options[0]?.value,
      description: `Select ${displayName.toLowerCase()}`
    };
  }
  
  static createTextAreaProperty(
    displayName: string,
    name: string,
    options: {
      placeholder?: string;
      description?: string;
      displayOptions?: any;
    } = {}
  ): INodeProperties {
    return {
      displayName,
      name,
      type: 'string',
      typeOptions: {
        alwaysOpenEditWindow: true,
        editor: 'plainText'
      },
      default: '',
      placeholder: options.placeholder || '',
      description: options.description || '',
      displayOptions: options.displayOptions
    };
  }
} 