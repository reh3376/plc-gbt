/**
 * N8N Node Operation Handlers
 * Common operation execution patterns
 */

import { IExecuteFunctions, INodeExecutionData, NodeOperationError } from 'n8n-workflow';

export abstract class BaseOperationHandler {
  
  protected async validateParameters(
    executeFunctions: IExecuteFunctions,
    requiredParams: string[]
  ): Promise<void> {
    for (const param of requiredParams) {
      const value = executeFunctions.getNodeParameter(param, 0) as string;
      if (!value || value.trim() === '') {
        throw new NodeOperationError(
          executeFunctions.getNode(),
          `Parameter '${param}' is required but not provided`
        );
      }
    }
  }
  
  protected createSuccessResponse(data: any): INodeExecutionData {
    return {
      json: {
        success: true,
        timestamp: new Date().toISOString(),
        data
      }
    };
  }
  
  protected createErrorResponse(error: Error | string): INodeExecutionData {
    const errorMessage = error instanceof Error ? error.message : error;
    return {
      json: {
        success: false,
        timestamp: new Date().toISOString(),
        error: errorMessage
      }
    };
  }
  
  protected async executeWithErrorHandling<T>(
    executeFunctions: IExecuteFunctions,
    operation: () => Promise<T>
  ): Promise<INodeExecutionData[]> {
    try {
      const result = await operation();
      return [this.createSuccessResponse(result)];
    } catch (error) {
      throw new NodeOperationError(
        executeFunctions.getNode(),
        error instanceof Error ? error.message : String(error)
      );
    }
  }
  
  abstract execute(
    executeFunctions: IExecuteFunctions,
    items: INodeExecutionData[]
  ): Promise<INodeExecutionData[]>;
} 