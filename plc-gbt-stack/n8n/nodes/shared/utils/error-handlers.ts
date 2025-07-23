/**
 * N8N Node Error Handlers
 * Standardized error handling across nodes
 */

import { IExecuteFunctions, NodeOperationError } from 'n8n-workflow';

export class NodeErrorHandler {
  
  static createOperationError(
    executeFunctions: IExecuteFunctions,
    message: string,
    context?: any
  ): NodeOperationError {
    const fullMessage = context 
      ? `${message}. Context: ${JSON.stringify(context)}`
      : message;
    
    return new NodeOperationError(executeFunctions.getNode(), fullMessage);
  }
  
  static handleConnectionError(
    executeFunctions: IExecuteFunctions,
    error: Error,
    connectionType: string
  ): NodeOperationError {
    return this.createOperationError(
      executeFunctions,
      `Failed to connect to ${connectionType}: ${error.message}`,
      { connectionType, originalError: error.message }
    );
  }
  
  static handleValidationError(
    executeFunctions: IExecuteFunctions,
    parameterName: string,
    value: any,
    expectedFormat?: string
  ): NodeOperationError {
    const message = expectedFormat
      ? `Invalid parameter '${parameterName}': expected ${expectedFormat}, got '${value}'`
      : `Invalid parameter '${parameterName}': '${value}'`;
    
    return this.createOperationError(
      executeFunctions,
      message,
      { parameterName, value, expectedFormat }
    );
  }
  
  static handleOperationError(
    executeFunctions: IExecuteFunctions,
    operation: string,
    error: Error
  ): NodeOperationError {
    return this.createOperationError(
      executeFunctions,
      `Operation '${operation}' failed: ${error.message}`,
      { operation, originalError: error.message }
    );
  }
} 