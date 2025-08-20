/**
 * Node Configuration Validation API Route - AI Task Orchestrator TypeScript Implementation
 *
 * @description API endpoint for validating node configurations against schemas
 * @compliance Strict TypeScript with OpenAPI Schema MCP validation
 * @integration MCP_Docker OpenAPI validation for all requests/responses
 */

import {
  IndustrialNodeTypeSchema,
  NodeConfigurationValidationRequestSchema,
  NodeConfigurationValidationResponseSchema,
  type ErrorResponse,
  type IndustrialNodeType,
  type NodeConfigurationValidationRequest,
  type NodeConfigurationValidationResponse,
  type ValidationResult,
} from '@/api/zod-schemas';
import { openAPISchemaMCP } from '@/lib/mcp/openapi-schema-client';
import { nodeSchemaRegistry } from '@/lib/schemas/industrial-node-schemas';
import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/v1/node-properties/{nodeType}/validate
 * Validate node configuration against its property schema
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ nodeType: string }> }
): Promise<NextResponse<NodeConfigurationValidationResponse | ErrorResponse>> {
  try {
    const { nodeType } = await params;
    const body = await request.json();

    // Validate nodeType parameter
    const nodeTypeValidation = IndustrialNodeTypeSchema.safeParse(nodeType);
    if (!nodeTypeValidation.success) {
      const errorResponse: ErrorResponse = {
        error: `Invalid node type: ${nodeType}`,
        details: 'Must be a valid industrial node type',
        timestamp: new Date().toISOString(),
        code: 'INVALID_NODE_TYPE',
      };
      return NextResponse.json(errorResponse, { status: 400 });
    }

    // Validate request body using Zod schema
    const requestValidation = NodeConfigurationValidationRequestSchema.safeParse(body);
    if (!requestValidation.success) {
      const errorResponse: ErrorResponse = {
        error: 'Invalid request body',
        details: requestValidation.error.message,
        timestamp: new Date().toISOString(),
        code: 'INVALID_REQUEST',
      };
      return NextResponse.json(errorResponse, { status: 400 });
    }

    // Validate request against OpenAPI schema
    const openAPIValidation = await openAPISchemaMCP.validateRequest(
      'POST',
      `/api/v1/node-properties/${nodeType}/validate`,
      body
    );

    if (!openAPIValidation.success) {
      console.error('OpenAPI request validation failed:', openAPIValidation.errors);
    }

    // Get schema from registry
    const schema = nodeSchemaRegistry.getSchema(nodeTypeValidation.data as IndustrialNodeType);

    if (!schema) {
      const errorResponse: ErrorResponse = {
        error: `Schema not found for node type: ${nodeType}`,
        details: 'Node type is valid but no schema is registered',
        timestamp: new Date().toISOString(),
        code: 'SCHEMA_NOT_FOUND',
      };
      return NextResponse.json(errorResponse, { status: 404 });
    }

    // Perform validation
    const { configuration, context } = requestValidation.data;
    const validationResults: ValidationResult[] = [];
    let hasErrors = false;
    let hasWarnings = false;

    // Get the original schema with validation functions from the registry
    // For now, we'll only support the schemas that are actually registered
    const originalSchema = nodeSchemaRegistry.getSchema(
      nodeTypeValidation.data as 'pid-controller' | 'modbus-client' | 'opc-server' | 'hmi-display'
    );

    if (originalSchema) {
      // Validate each field in each group using the original schema with validation functions
      for (const group of originalSchema.groups) {
        for (const field of group.fields) {
          const value = configuration[field.key];

          // Check required fields
          if (field.required && (value === undefined || value === null || value === '')) {
            validationResults.push({
              isValid: false,
              severity: 'error',
              message: `${field.label} is required`,
              field: field.key,
              code: 'REQUIRED_FIELD',
            });
            hasErrors = true;
            continue;
          }

          // Run field-specific validation if value exists and validation function is available
          if (
            value !== undefined &&
            value !== null &&
            'validation' in field &&
            typeof field.validation === 'function'
          ) {
            try {
              const validationContext = {
                nodeType: schema.nodeType,
                allNodes: [],
                connectedNodes: [],
                workflowConfig: context || {},
              };

              const fieldValidation = field.validation(value, configuration, validationContext);
              if (fieldValidation) {
                validationResults.push(fieldValidation);
                if (fieldValidation.severity === 'error') hasErrors = true;
                if (fieldValidation.severity === 'warning') hasWarnings = true;
              }
            } catch (error) {
              validationResults.push({
                isValid: false,
                severity: 'error',
                message: `Validation error: ${
                  error instanceof Error ? error.message : 'Unknown error'
                }`,
                field: field.key,
                code: 'VALIDATION_EXCEPTION',
              });
              hasErrors = true;
            }
          }
        }
      }
    } else {
      // Fallback: Basic validation without functions
      for (const group of schema.groups) {
        for (const field of group.fields) {
          const value = configuration[field.key];

          // Check required fields
          if (field.required && (value === undefined || value === null || value === '')) {
            validationResults.push({
              isValid: false,
              severity: 'error',
              message: `${field.label} is required`,
              field: field.key,
              code: 'REQUIRED_FIELD',
            });
            hasErrors = true;
          }
        }
      }
    }

    // Create response
    const response: NodeConfigurationValidationResponse = {
      success: true,
      message: hasErrors
        ? 'Validation completed with errors'
        : hasWarnings
        ? 'Validation completed with warnings'
        : 'Validation passed',
      results: validationResults,
      isValid: !hasErrors,
      errors: validationResults.filter(r => r.severity === 'error'),
      warnings: validationResults.filter(r => r.severity === 'warning'),
    };

    // Validate response using Zod schema
    const zodValidation = NodeConfigurationValidationResponseSchema.safeParse(response);
    if (!zodValidation.success) {
      console.error('Zod validation failed:', zodValidation.error);
      const errorResponse: ErrorResponse = {
        error: 'Internal validation error',
        details: 'Response schema validation failed',
        timestamp: new Date().toISOString(),
        code: 'VALIDATION_ERROR',
      };
      return NextResponse.json(errorResponse, { status: 500 });
    }

    // Validate response against OpenAPI schema
    const responseValidation = await openAPISchemaMCP.validateResponse(
      'POST',
      `/api/v1/node-properties/${nodeType}/validate`,
      200,
      response
    );

    if (!responseValidation.success) {
      console.error('OpenAPI response validation failed:', responseValidation.errors);
    }

    return NextResponse.json(response);
  } catch (error) {
    console.error('Unexpected error in validation API:', error);

    const errorResponse: ErrorResponse = {
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error occurred',
      timestamp: new Date().toISOString(),
      code: 'INTERNAL_ERROR',
    };

    return NextResponse.json(errorResponse, { status: 500 });
  }
}
