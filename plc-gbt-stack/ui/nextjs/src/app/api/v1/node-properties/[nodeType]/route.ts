/**
 * Node Properties API Route - AI Task Orchestrator TypeScript Implementation
 *
 * @description API endpoints for retrieving node property schemas
 * @compliance Strict TypeScript with OpenAPI Schema MCP validation
 * @integration MCP_Docker OpenAPI validation for all requests/responses
 */

import {
  IndustrialNodeTypeSchema,
  NodePropertySchemaResponseSchema,
  type ErrorResponse,
  type IndustrialNodeType,
} from '@/api/zod-schemas';
import { openAPISchemaMCP } from '@/lib/mcp/openapi-schema-client';
import { nodeSchemaRegistry } from '@/lib/schemas/industrial-node-schemas';
import { NextRequest, NextResponse } from 'next/server';

type NodePropertySchemaResponse = {
  success: boolean;
  message: string;
  data: import('@/api/zod-schemas').NodePropertySchema;
};

/**
 * GET /api/v1/node-properties/{nodeType}
 * Retrieve property schema for a specific industrial node type
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ nodeType: string }> }
): Promise<NextResponse<NodePropertySchemaResponse | ErrorResponse>> {
  try {
    const { nodeType } = await params;

    // Validate nodeType parameter using Zod schema
    const nodeTypeValidation = IndustrialNodeTypeSchema.safeParse(nodeType);
    if (!nodeTypeValidation.success) {
      const errorResponse: ErrorResponse = {
        error: `Invalid node type: ${nodeType}`,
        details: 'Must be a valid industrial node type',
        timestamp: new Date().toISOString(),
        code: 'INVALID_NODE_TYPE',
      };

      // Validate error response against OpenAPI schema
      const validationResult = await openAPISchemaMCP.validateResponse(
        'GET',
        `/api/v1/node-properties/${nodeType}`,
        400,
        errorResponse
      );

      if (!validationResult.success) {
        console.error('OpenAPI validation failed for error response:', validationResult.errors);
      }

      return NextResponse.json(errorResponse, { status: 400 });
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

      // Validate error response against OpenAPI schema
      const validationResult = await openAPISchemaMCP.validateResponse(
        'GET',
        `/api/v1/node-properties/${nodeType}`,
        404,
        errorResponse
      );

      if (!validationResult.success) {
        console.error('OpenAPI validation failed for 404 response:', validationResult.errors);
      }

      return NextResponse.json(errorResponse, { status: 404 });
    }

    // Create successful response
    const response: NodePropertySchemaResponse = {
      success: true,
      message: `Schema retrieved for ${nodeType}`,
      data: schema,
    };

    // Validate response using Zod schema
    const zodValidation = NodePropertySchemaResponseSchema.safeParse(response);
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
    const validationResult = await openAPISchemaMCP.validateResponse(
      'GET',
      `/api/v1/node-properties/${nodeType}`,
      200,
      response
    );

    if (!validationResult.success) {
      console.error('OpenAPI validation failed for success response:', validationResult.errors);
    }

    return NextResponse.json(response);
  } catch (error) {
    console.error('Unexpected error in node properties API:', error);

    const errorResponse: ErrorResponse = {
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error occurred',
      timestamp: new Date().toISOString(),
      code: 'INTERNAL_ERROR',
    };

    // Validate error response
    const validationResult = await openAPISchemaMCP.validateResponse(
      'GET',
      `/api/v1/node-properties/error`,
      500,
      errorResponse
    );

    if (!validationResult.success) {
      console.error('OpenAPI validation failed for error response:', validationResult.errors);
    }

    return NextResponse.json(errorResponse, { status: 500 });
  }
}
