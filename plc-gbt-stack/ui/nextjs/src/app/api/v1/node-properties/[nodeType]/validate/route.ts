/**
 * Node Properties Validation API Route - AI Task Orchestrator TypeScript Implementation
 *
 * @description Validates node configuration against property schemas with OpenAPI MCP integration
 * @compliance Strict TypeScript with OpenAPI Schema MCP validation
 * @route POST /api/v1/node-properties/{nodeType}/validate
 */

import {
  IndustrialNodeTypeSchema,
  NodeConfigurationValidationRequestSchema,
  NodeConfigurationValidationResponseSchema,
  type ErrorResponse,
  type IndustrialNodeType,
  type NodeConfigurationValidationRequest,
  type NodeConfigurationValidationResponse,
  type NodePropertySchema,
  type ValidationResult,
} from '@/api/zod-schemas';
import { openAPISchemaMCP } from '@/lib/mcp/openapi-schema-client';
import { nodeSchemaRegistry } from '@/lib/schemas/industrial-node-schemas';
import { NextRequest, NextResponse } from 'next/server';

// Helper function to validate node type parameter
async function validateNodeTypeParameter(nodeType: string): Promise<ErrorResponse | null> {
  const nodeTypeValidation = IndustrialNodeTypeSchema.safeParse(nodeType);
  if (!nodeTypeValidation.success) {
    return {
      error: `Invalid node type: ${nodeType}`,
      details: 'Must be a valid industrial node type',
      timestamp: new Date().toISOString(),
      code: 'INVALID_NODE_TYPE',
    };
  }
  return null;
}

// Helper function to get node schema
async function getNodeSchema(
  nodeType: string
): Promise<{ schema: NodePropertySchema | null; error: ErrorResponse | null }> {
  const schema = nodeSchemaRegistry.getSchema(nodeType as IndustrialNodeType);
  if (!schema) {
    return {
      schema: null,
      error: {
        error: `Schema not found for node type: ${nodeType}`,
        details: 'Node type is valid but no schema is registered',
        timestamp: new Date().toISOString(),
        code: 'SCHEMA_NOT_FOUND',
      },
    };
  }
  return { schema, error: null };
}

// Helper function to validate request body
async function validateRequestBody(
  body: unknown
): Promise<{ request: NodeConfigurationValidationRequest | null; error: ErrorResponse | null }> {
  const requestValidation = NodeConfigurationValidationRequestSchema.safeParse(body);
  if (!requestValidation.success) {
    return {
      request: null,
      error: {
        error: 'Invalid request format',
        details: requestValidation.error.message,
        timestamp: new Date().toISOString(),
        code: 'INVALID_REQUEST_FORMAT',
      },
    };
  }
  return { request: requestValidation.data, error: null };
}

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

    // Validate nodeType parameter using helper function
    const nodeTypeError = await validateNodeTypeParameter(nodeType);
    if (nodeTypeError) {
      return NextResponse.json(nodeTypeError, { status: 400 });
    }

    // Validate request body using helper function
    const { request: validatedRequest, error: requestError } = await validateRequestBody(body);
    if (requestError) {
      return NextResponse.json(requestError, { status: 400 });
    }

    // Get node schema using helper function
    const { schema: nodeSchema, error: schemaError } = await getNodeSchema(nodeType);
    if (schemaError) {
      return NextResponse.json(schemaError, { status: 404 });
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

    // Continue with validation logic using validated data
    const { configuration } = validatedRequest!;
    const validationResults: ValidationResult[] = [];
    let hasErrors = false;
    const hasWarnings = false;

    // Validate each field in each group using the schema
    if (nodeSchema) {
      for (const group of nodeSchema.groups) {
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

          // Type validation
          if (value !== undefined && value !== null && value !== '') {
            // Basic type checking based on field type
            let typeValid = true;
            let typeMessage = '';

            switch (field.type) {
              case 'number':
                if (typeof value !== 'number' && isNaN(Number(value))) {
                  typeValid = false;
                  typeMessage = `${field.label} must be a number`;
                }
                break;
              case 'boolean':
                if (typeof value !== 'boolean') {
                  typeValid = false;
                  typeMessage = `${field.label} must be a boolean`;
                }
                break;
              case 'text':
              case 'textarea':
              case 'select':
                if (typeof value !== 'string') {
                  typeValid = false;
                  typeMessage = `${field.label} must be a string`;
                }
                break;
            }

            if (!typeValid) {
              validationResults.push({
                isValid: false,
                severity: 'error',
                message: typeMessage,
                field: field.key,
                code: 'TYPE_MISMATCH',
              });
              hasErrors = true;
            }
          }
        }
      }
    }

    // Create response
    const response: NodeConfigurationValidationResponse = {
      success: !hasErrors,
      message: hasErrors
        ? 'Validation failed'
        : hasWarnings
        ? 'Validation passed with warnings'
        : 'Validation passed',
      results: validationResults,
      isValid: !hasErrors,
      errors: validationResults.filter(r => r.severity === 'error'),
      warnings: validationResults.filter(r => r.severity === 'warning'),
    };

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
