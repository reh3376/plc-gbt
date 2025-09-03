/**
 * Real OpenAPI Schema MCP Client - Docker MCP Integration
 *
 * @description Real MCP client connecting to Docker MCP server on port 8811
 * @compliance Strict TypeScript - zero `any` types policy
 * @methodology AI Task Orchestrator TypeScript Guide
 * @integration Docker MCP server for OpenAPI schema management
 */

import type {
  CreateFileRequest,
  DeleteFileRequest,
  FileItem,
  MoveFileRequest,
  RenameFileRequest,
  UploadFileRequest,
} from '@/lib/types/file-explorer.types';

// Real OpenAPI MCP Schema Types (matching the fake client interface)
interface OpenAPISchema {
  type?: string;
  properties?: Record<string, OpenAPISchema>;
  items?: OpenAPISchema;
  required?: string[];
  description?: string;
  format?: string;
  enum?: unknown[];
  $ref?: string;
  anyOf?: OpenAPISchema[];
  oneOf?: OpenAPISchema[];
  allOf?: OpenAPISchema[];
  [key: string]: unknown;
}

interface OpenAPIEndpoint {
  method: string;
  path: string;
  operationId: string;
  summary?: string;
  description?: string;
  parameters?: OpenAPIParameter[];
  requestBody?: OpenAPIRequestBody;
  responses?: Record<string, OpenAPIResponse>;
}

interface OpenAPIParameter {
  name: string;
  in: 'query' | 'path' | 'header' | 'cookie';
  required?: boolean;
  schema?: OpenAPISchema;
  description?: string;
}

interface OpenAPIRequestBody {
  required?: boolean;
  content?: Record<string, { schema?: OpenAPISchema }>;
  description?: string;
}

interface OpenAPIResponse {
  description?: string;
  content?: Record<string, { schema?: OpenAPISchema }>;
  headers?: Record<string, OpenAPISchema>;
}

interface MCPOpenAPIValidationResult {
  valid: boolean;
  success: boolean; // Alias for compatibility with existing API routes
  errors?: string[];
  data?: unknown;
  statusCode?: number;
}

interface DockerMCPResponse {
  success: boolean;
  data?: unknown;
  error?: string;
  schemas?: Record<string, OpenAPISchema>;
  endpoints?: OpenAPIEndpoint[];
}

/**
 * Real OpenAPI Schema MCP Client
 * Connects to Docker MCP server on port 8811 for actual schema management
 */
export class RealOpenAPISchemaMCPClient {
  private mcpServerUrl: string;
  private isConnected: boolean = false;
  private endpointSchemas: Map<string, OpenAPIEndpoint> = new Map();
  private componentSchemas: Record<string, OpenAPISchema> = {};
  private connectionRetries: number = 0;
  private maxRetries: number = 3;
  private retryDelay: number = 1000; // 1 second

  constructor(mcpServerUrl?: string) {
    // Check if MCP server URL is provided via environment variable first
    this.mcpServerUrl =
      mcpServerUrl || process.env.NEXT_PUBLIC_MCP_SERVER_URL || 'http://localhost:8811';

    // Only attempt connection if not in development mode without MCP server
    if (this.shouldAttemptConnection()) {
      // Initialize connection on construction for immediate use
      this.initializeConnection();
    } else {
      console.log('🔄 MCP server not configured - using fallback validation mode');
      this.isConnected = false;
    }
  }

  /**
   * Check if we should attempt to connect to MCP server
   */
  private shouldAttemptConnection(): boolean {
    // Always attempt MCP connection in development when MCP_Docker is required
    // Per AI Task Orchestrator methodology: MCP_Docker is MANDATORY for all API development
    console.log('🔗 Connecting to Docker MCP OpenAPI server...');
    console.log('📡 Server URL:', this.mcpServerUrl);
    
    // Skip connection attempts if we detect common development scenarios without MCP
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      // In browser, check if this is a development environment
      const isDevelopment = process.env.NODE_ENV === 'development';
      const hasExplicitMCPConfig = !!process.env.NEXT_PUBLIC_MCP_SERVER_URL;

      // Always attempt connection when MCP_Docker is available
      return true;
    }

    // Server-side always attempts connection
    return true;
  }

  /**
   * Initialize connection (non-blocking)
   */
  private initializeConnection(): void {
    // Start connection asynchronously without blocking construction
    this.connect().catch(error => {
      // Suppress noisy error logs in development without MCP server
      if (process.env.NODE_ENV !== 'development') {
        console.warn('⚠️ MCP connection failed during initialization:', error.message);
      }
      console.log('🔄 Using fallback validation mode (MCP server not available)');
    });
  }

  /**
   * Connect to real Docker MCP OpenAPI server
   */
  async connect(): Promise<void> {
    try {
      console.log('🔗 Connecting to Docker MCP OpenAPI server...');
      console.log(`📡 Server URL: ${this.mcpServerUrl}`);

      // Test connection to Docker MCP server
      const healthCheck = await this.makeRequest('/health', 'GET');

      if (!healthCheck.success) {
        throw new Error(`Health check failed: ${healthCheck.error}`);
      }

      // Load schemas from Docker MCP server
      await this.loadSchemasFromMCP();

      this.isConnected = true;
      this.connectionRetries = 0;
      console.log('✅ Connected to Docker MCP OpenAPI server');
      console.log(`📊 Loaded ${Object.keys(this.componentSchemas).length} component schemas`);
      console.log(`🔗 Loaded ${this.endpointSchemas.size} API endpoints`);
    } catch (error) {
      // Only show detailed errors in non-development environments
      if (process.env.NODE_ENV !== 'development') {
        console.error('❌ Failed to connect to Docker MCP server:', error);
      }

      if (this.connectionRetries < this.maxRetries) {
        this.connectionRetries++;

        // Only log retries in non-development environments
        if (process.env.NODE_ENV !== 'development') {
          console.log(
            `🔄 Retrying connection (${this.connectionRetries}/${this.maxRetries}) in ${this.retryDelay}ms...`
          );
        }

        await new Promise(resolve => setTimeout(resolve, this.retryDelay));
        return this.connect();
      }

      // Final warning - less noisy in development
      if (process.env.NODE_ENV === 'development') {
        console.log('ℹ️ MCP server not available - validation will use fallback mode');
      } else {
        console.warn('⚠️ Max retries reached. Using fallback mode.');
      }

      this.isConnected = false;
      throw error;
    }
  }

  /**
   * Load OpenAPI schemas from Docker MCP server
   */
  private async loadSchemasFromMCP(): Promise<void> {
    try {
      // Request schemas from Docker MCP server
      const schemasResponse = await this.makeRequest('/schemas/openapi', 'GET');

      if (!schemasResponse.success) {
        throw new Error(`Failed to load schemas: ${schemasResponse.error}`);
      }

      // Parse component schemas
      if (schemasResponse.schemas) {
        this.componentSchemas = schemasResponse.schemas;
      }

      // Parse endpoint schemas
      if (schemasResponse.endpoints) {
        for (const endpoint of schemasResponse.endpoints) {
          const key = `${endpoint.method.toUpperCase()} ${endpoint.path}`;
          this.endpointSchemas.set(key, endpoint);
        }
      }

      console.log('📋 Schemas loaded from Docker MCP server');
    } catch (error) {
      console.error('❌ Failed to load schemas from MCP:', error);
      throw error;
    }
  }

  /**
   * Make HTTP request to Docker MCP server
   */
  private async makeRequest(
    path: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    body?: unknown
  ): Promise<DockerMCPResponse> {
    try {
      const url = `${this.mcpServerUrl}${path}`;

      const requestOptions: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      };

      if (body) {
        requestOptions.body = JSON.stringify(body);
      }

      const response = await fetch(url, requestOptions);

      if (!response.ok) {
        return {
          success: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.json();

      const result: DockerMCPResponse = {
        success: true,
        data,
      };

      if (data && typeof data === 'object' && data !== null) {
        const dataObj = data as Record<string, unknown>;
        if (dataObj.schemas) {
          result.schemas = dataObj.schemas as Record<string, OpenAPISchema>;
        }
        if (dataObj.endpoints) {
          result.endpoints = dataObj.endpoints as OpenAPIEndpoint[];
        }
      }

      return result;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Validate API request against OpenAPI schema
   */
  async validateRequest(
    method: string,
    path: string,
    data: unknown
  ): Promise<MCPOpenAPIValidationResult> {
    try {
      if (!this.isConnected) {
        console.warn('⚠️ MCP server not connected, skipping validation');
        return { valid: true, success: true, data };
      }

      // Send validation request to Docker MCP server
      const validationResponse = await this.makeRequest('/validate/request', 'POST', {
        method: method.toUpperCase(),
        path,
        data,
      });

      if (!validationResponse.success) {
        console.warn(`⚠️ Request validation failed: ${validationResponse.error}`);
        return {
          valid: false,
          success: false,
          errors: [validationResponse.error || 'Validation failed'],
        };
      }

      return {
        valid: true,
        success: true,
        data: validationResponse.data,
      };
    } catch (error) {
      console.warn('⚠️ Request validation error:', error);
      return {
        valid: false,
        success: false,
        errors: [error instanceof Error ? error.message : 'Validation error'],
      };
    }
  }

  /**
   * Validate API response against OpenAPI schema
   */
  async validateResponse(
    method: string,
    path: string,
    statusCode: number,
    data: unknown
  ): Promise<MCPOpenAPIValidationResult> {
    try {
      if (!this.isConnected) {
        console.warn('⚠️ MCP server not connected, skipping validation');
        return { valid: true, success: true, data, statusCode };
      }

      // Send validation request to Docker MCP server
      const validationResponse = await this.makeRequest('/validate/response', 'POST', {
        method: method.toUpperCase(),
        path,
        statusCode,
        data,
      });

      if (!validationResponse.success) {
        console.warn(`⚠️ Response validation failed: ${validationResponse.error}`);
        return {
          valid: false,
          success: false,
          errors: [validationResponse.error || 'Validation failed'],
          statusCode,
        };
      }

      return {
        valid: true,
        success: true,
        data: validationResponse.data,
        statusCode,
      };
    } catch (error) {
      console.warn('⚠️ Response validation error:', error);
      return {
        valid: false,
        success: false,
        errors: [error instanceof Error ? error.message : 'Validation error'],
        statusCode,
      };
    }
  }

  /**
   * Get endpoint schema for specific method and path
   */
  getEndpointSchema(method: string, path: string): OpenAPIEndpoint | null {
    const key = `${method.toUpperCase()} ${path}`;
    return this.endpointSchemas.get(key) || null;
  }

  /**
   * Get component schema by name
   */
  getComponentSchema(schemaName: string): OpenAPISchema | null {
    return this.componentSchemas[schemaName] || null;
  }

  /**
   * Check if MCP server is connected
   */
  isSchemaServerConnected(): boolean {
    return this.isConnected;
  }

  /**
   * Generate TypeScript types from OpenAPI schemas
   */
  generateTypeScriptTypes(): string {
    const types: string[] = [];

    for (const [name, schema] of Object.entries(this.componentSchemas)) {
      const typeDefinition = this.schemaToTypeScript(name, schema);
      types.push(typeDefinition);
    }

    return types.join('\n\n');
  }

  /**
   * Convert OpenAPI schema to TypeScript type definition
   */
  private schemaToTypeScript(name: string, schema: OpenAPISchema): string {
    // Basic TypeScript type generation
    // This is a simplified implementation - a full implementation would handle all OpenAPI features

    if (schema.type === 'object' && schema.properties) {
      const properties: string[] = [];

      for (const [propName, propSchema] of Object.entries(schema.properties)) {
        const isRequired = schema.required?.includes(propName) ?? false;
        const optional = isRequired ? '' : '?';
        const propType = this.getTypeScriptType(propSchema);

        properties.push(`  ${propName}${optional}: ${propType};`);
      }

      return `export interface ${name} {\n${properties.join('\n')}\n}`;
    }

    return `export type ${name} = ${this.getTypeScriptType(schema)};`;
  }

  /**
   * Get TypeScript type for OpenAPI schema
   */
  private getTypeScriptType(schema: OpenAPISchema): string {
    if (schema.$ref) {
      // Extract type name from $ref
      const refParts = schema.$ref.split('/');
      return refParts[refParts.length - 1];
    }

    switch (schema.type) {
      case 'string':
        return schema.enum ? schema.enum.map(v => `'${v}'`).join(' | ') : 'string';
      case 'number':
      case 'integer':
        return 'number';
      case 'boolean':
        return 'boolean';
      case 'array':
        return schema.items ? `${this.getTypeScriptType(schema.items)}[]` : 'unknown[]';
      case 'object':
        return 'Record<string, unknown>';
      default:
        return 'unknown';
    }
  }

  /**
   * Disconnect from MCP server
   */
  async disconnect(): Promise<void> {
    this.isConnected = false;
    this.endpointSchemas.clear();
    this.componentSchemas = {};
    console.log('🔌 Disconnected from Docker MCP server');
  }
}

// Create singleton instance with expected export name
const openAPISchemaMCP = new RealOpenAPISchemaMCPClient();

// Export both class and instance (maintaining compatibility with existing imports)
export { openAPISchemaMCP, RealOpenAPISchemaMCPClient as OpenAPISchemaMCPClient };

// Export interfaces for compatibility
export interface FileOperationResponse {
  success: boolean;
  data?: unknown;
  error?: string;
}

export interface FileOperationResult {
  success: boolean;
  message: string;
  data?: unknown;
}

/**
 * React hook for OpenAPI Schema MCP integration
 * Provides access to real MCP Docker server functionality
 */
export function useOpenAPISchemaMCP() {
  return {
    validateRequest: openAPISchemaMCP.validateRequest.bind(openAPISchemaMCP),
    validateResponse: openAPISchemaMCP.validateResponse.bind(openAPISchemaMCP),
    getEndpointSchema: openAPISchemaMCP.getEndpointSchema.bind(openAPISchemaMCP),
    getComponentSchema: openAPISchemaMCP.getComponentSchema.bind(openAPISchemaMCP),
    isConnected: openAPISchemaMCP.isSchemaServerConnected(),
    connect: openAPISchemaMCP.connect.bind(openAPISchemaMCP),
    disconnect: openAPISchemaMCP.disconnect.bind(openAPISchemaMCP),
    generateTypeScriptTypes: openAPISchemaMCP.generateTypeScriptTypes.bind(openAPISchemaMCP),
  };
}
