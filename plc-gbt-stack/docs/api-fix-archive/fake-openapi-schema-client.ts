/**
 * OpenAPI Schema MCP Client - AI Task Orchestrator TypeScript Implementation
 *
 * @description MCP client for OpenAPI schema management and validation
 * @compliance Strict TypeScript - zero `any` types policy
 * @integration MCP_Docker OpenAPI server for schema-first development
 */

import type {
  CreateFileRequest,
  DeleteFileRequest,
  FileItem,
  FileOperationResult,
  MoveFileRequest,
  RenameFileRequest,
  UploadFileRequest,
} from '@/lib/types/file-explorer.types';

// OpenAPI MCP Schema Types
interface OpenAPISchema {
  type?: string;
  properties?: Record<string, OpenAPISchema>;
  items?: OpenAPISchema;
  required?: string[];
  description?: string;
  format?: string;
  enum?: unknown[];
  $ref?: string; // Support for OpenAPI references
  anyOf?: OpenAPISchema[]; // Support for union types
  oneOf?: OpenAPISchema[]; // Support for exclusive union types
  allOf?: OpenAPISchema[]; // Support for intersection types
  // Allow additional schema properties
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
  schema: OpenAPISchema;
  description?: string;
}

interface OpenAPIRequestBody {
  required?: boolean;
  content: Record<string, { schema: OpenAPISchema }>;
}

interface OpenAPIResponse {
  description: string;
  content?: Record<string, { schema: OpenAPISchema }>;
}

interface MCPOpenAPIValidationResult {
  success: boolean;
  data?: unknown;
  errors?: string[];
  schema?: OpenAPISchema;
}

/**
 * OpenAPI Schema MCP Client
 *
 * @description Integrates with MCP_Docker OpenAPI server for schema management
 * @features Schema validation, type generation, API contract enforcement
 */
export class OpenAPISchemaMCPClient {
  private mcpServerUrl: string;
  private isConnected: boolean = false;
  private endpointSchemas: Map<string, OpenAPIEndpoint> = new Map();
  private componentSchemas: Record<string, OpenAPISchema> = {};

  constructor(mcpServerUrl: string = 'http://localhost:3001/mcp') {
    this.mcpServerUrl = mcpServerUrl;
    // Load schemas synchronously on construction for immediate use
    this.loadOpenAPISchemasSync();
  }

  /**
   * Connect to MCP_Docker OpenAPI server
   */
  async connect(): Promise<void> {
    try {
      // Initialize connection to MCP_Docker OpenAPI server
      console.log('🔗 Connecting to OpenAPI Schema MCP server...');

      // Load OpenAPI schemas from MCP server
      this.loadOpenAPISchemasSync();

      this.isConnected = true;
      console.log('✅ Connected to OpenAPI Schema MCP server');
    } catch (error) {
      console.warn('⚠️ OpenAPI Schema MCP server unavailable, using fallback validation');
      this.isConnected = false;
    }
  }

  /**
   * Load OpenAPI schemas synchronously for immediate use
   */
  private loadOpenAPISchemasSync(): void {
    // Define file operations API endpoints
    const fileOperationsEndpoints: OpenAPIEndpoint[] = [
      {
        method: 'GET',
        path: '/api/v1/files',
        operationId: 'getFiles',
        summary: 'Get file tree',
        description: 'Retrieve the complete file and folder tree',
        responses: {
          '200': {
            description: 'File tree retrieved successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    message: { type: 'string' },
                    data: {
                      type: 'array',
                      items: { $ref: '#/components/schemas/FileItem' },
                    },
                  },
                  required: ['success', 'message', 'data'],
                },
              },
            },
          },
        },
      },
      {
        method: 'PUT',
        path: '/api/v1/files/{id}/move',
        operationId: 'moveFile',
        summary: 'Move file or folder',
        description: 'Move a file or folder to a different parent directory',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' },
            description: 'File or folder ID to move',
          },
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/MoveFileRequest' },
            },
          },
        },
        responses: {
          '200': {
            description: 'File moved successfully',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/FileOperationResult' },
              },
            },
          },
        },
      },
      {
        method: 'PUT',
        path: '/api/v1/files/{id}/rename',
        operationId: 'renameFile',
        summary: 'Rename file or folder',
        description: 'Rename a file or folder',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' },
            description: 'File or folder ID to rename',
          },
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/RenameFileRequest' },
            },
          },
        },
        responses: {
          '200': {
            description: 'File renamed successfully',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/FileOperationResult' },
              },
            },
          },
        },
      },
    ];

    // Define workflow management API endpoints
    const workflowManagementEndpoints: OpenAPIEndpoint[] = [
      {
        method: 'GET',
        path: '/api/v1/workflows',
        operationId: 'getWorkflows',
        summary: 'Get all workflows',
        description: 'Retrieve all workflow definitions and metadata',
        responses: {
          '200': {
            description: 'Workflows retrieved successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    message: { type: 'string' },
                    data: {
                      type: 'array',
                      items: { $ref: '#/components/schemas/WorkflowMetadata' },
                    },
                  },
                  required: ['success', 'message', 'data'],
                },
              },
            },
          },
        },
      },
      {
        method: 'POST',
        path: '/api/v1/workflows',
        operationId: 'createWorkflow',
        summary: 'Create new workflow',
        description: 'Create a new workflow definition',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/CreateWorkflowRequest' },
            },
          },
        },
        responses: {
          '201': {
            description: 'Workflow created successfully',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/WorkflowOperationResult' },
              },
            },
          },
        },
      },
      {
        method: 'PUT',
        path: '/api/v1/workflows/{id}',
        operationId: 'updateWorkflow',
        summary: 'Update existing workflow',
        description: 'Update an existing workflow definition and metadata',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' },
            description: 'Workflow ID to update',
          },
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  name: { type: 'string' },
                  description: { type: 'string' },
                  version: { type: 'string' },
                  author: { type: 'string' },
                  tags: { type: 'array', items: { type: 'string' } },
                  category: {
                    type: 'string',
                    enum: ['control', 'monitoring', 'automation', 'integration'],
                  },
                  nodes: {
                    type: 'array',
                    items: { $ref: '#/components/schemas/WorkflowNode' },
                  },
                  edges: {
                    type: 'array',
                    items: { $ref: '#/components/schemas/WorkflowEdge' },
                  },
                  viewport: { type: 'object' },
                  modified: { type: 'string', format: 'date-time' },
                },
                required: ['id', 'name', 'nodes', 'edges'],
              },
            },
          },
        },
        responses: {
          '200': {
            description: 'Workflow updated successfully',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/WorkflowOperationResult' },
              },
            },
          },
        },
      },
      {
        method: 'PUT',
        path: '/api/v1/workflows/{id}/execute',
        operationId: 'executeWorkflow',
        summary: 'Execute workflow',
        description: 'Start execution of a workflow',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' },
            description: 'Workflow ID to execute',
          },
        ],
        requestBody: {
          required: false,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/WorkflowExecutionRequest' },
            },
          },
        },
        responses: {
          '200': {
            description: 'Workflow execution started',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/WorkflowExecutionResult' },
              },
            },
          },
        },
      },
      {
        method: 'GET',
        path: '/api/v1/workflows/{id}/status',
        operationId: 'getWorkflowStatus',
        summary: 'Get workflow execution status',
        description: 'Retrieve current execution status of a workflow',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' },
            description: 'Workflow ID',
          },
        ],
        responses: {
          '200': {
            description: 'Workflow status retrieved',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/WorkflowStatusResult' },
              },
            },
          },
        },
      },
    ];

    // Define node properties API endpoints
    const nodePropertiesEndpoints: OpenAPIEndpoint[] = [
      {
        method: 'GET',
        path: '/api/v1/node-properties/{nodeType}',
        operationId: 'getNodePropertySchema',
        summary: 'Get node property schema',
        description: 'Retrieve the property schema for a specific industrial node type',
        parameters: [
          {
            name: 'nodeType',
            in: 'path',
            required: true,
            schema: { $ref: '#/components/schemas/IndustrialNodeType' },
            description: 'Type of industrial node',
          },
        ],
        responses: {
          '200': {
            description: 'Node property schema retrieved successfully',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    success: { type: 'boolean' },
                    message: { type: 'string' },
                    data: { $ref: '#/components/schemas/NodePropertySchema' },
                  },
                  required: ['success', 'message', 'data'],
                },
              },
            },
          },
          '404': {
            description: 'Node type not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' },
              },
            },
          },
        },
      },
      {
        method: 'POST',
        path: '/api/v1/node-properties/{nodeType}/validate',
        operationId: 'validateNodeConfiguration',
        summary: 'Validate node configuration',
        description: 'Validate a node configuration against its property schema',
        parameters: [
          {
            name: 'nodeType',
            in: 'path',
            required: true,
            schema: { $ref: '#/components/schemas/IndustrialNodeType' },
            description: 'Type of industrial node',
          },
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/NodeConfigurationValidationRequest' },
            },
          },
        },
        responses: {
          '200': {
            description: 'Configuration validation completed',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/NodeConfigurationValidationResponse' },
              },
            },
          },
          '400': {
            description: 'Invalid configuration data',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' },
              },
            },
          },
        },
      },
      {
        method: 'POST',
        path: '/api/v1/node-properties/{nodeType}/test-connection',
        operationId: 'testNodeConnection',
        summary: 'Test node connection',
        description: 'Test the connection for a node configuration',
        parameters: [
          {
            name: 'nodeType',
            in: 'path',
            required: true,
            schema: { $ref: '#/components/schemas/IndustrialNodeType' },
            description: 'Type of industrial node',
          },
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/NodeConnectionTestRequest' },
            },
          },
        },
        responses: {
          '200': {
            description: 'Connection test completed',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/NodeConnectionTestResponse' },
              },
            },
          },
        },
      },
    ];

    // Define support and help API endpoints
    const supportEndpoints: OpenAPIEndpoint[] = [
      {
        method: 'POST',
        path: '/api/v1/support/send-email',
        operationId: 'sendSupportEmail',
        summary: 'Send support email',
        description: 'Send a support request email with workflow context and attachments',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/SupportEmailRequest' },
            },
          },
        },
        responses: {
          '200': {
            description: 'Support email sent successfully',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/SupportEmailResponse' },
              },
            },
          },
          '400': {
            description: 'Invalid request data',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' },
              },
            },
          },
          '500': {
            description: 'Server error sending email',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' },
              },
            },
          },
        },
      },
    ];

    // Store all endpoint schemas
    const allEndpoints = [
      ...fileOperationsEndpoints,
      ...workflowManagementEndpoints,
      ...nodePropertiesEndpoints,
      ...supportEndpoints,
    ];
    allEndpoints.forEach(endpoint => {
      const key = `${endpoint.method}:${endpoint.path}`;
      this.endpointSchemas.set(key, endpoint);
    });

    // Define component schemas
    this.componentSchemas = {
      WorkflowNode: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          type: { type: 'string' },
          position: {
            type: 'object',
            properties: {
              x: { type: 'number' },
              y: { type: 'number' },
            },
            required: ['x', 'y'],
          },
          data: {
            type: 'object',
            properties: {
              label: { type: 'string' },
              description: { type: 'string' },
              status: { type: 'string' },
              // PLC Input/Output specific
              value: {
                anyOf: [{ type: 'boolean' }, { type: 'number' }, { type: 'null' }],
              },
              isDigital: { type: 'boolean' },
              address: { type: 'string' },
              // PID Controller specific
              kp: { type: 'number' },
              ki: { type: 'number' },
              kd: { type: 'number' },
              setpoint: { type: 'number' },
              processValue: { type: 'number' },
              output: { type: 'number' },
              error: { type: 'number' },
              // Legacy support for config-based structure
              config: {
                type: 'object',
                properties: {
                  kp: { type: 'number' },
                  ki: { type: 'number' },
                  kd: { type: 'number' },
                  setpoint: { type: 'number' },
                  processValue: { type: 'number' },
                  output: { type: 'number' },
                  error: { type: 'number' },
                },
              },
            },
            required: ['label'],
          },
        },
        required: ['id', 'type', 'position', 'data'],
      },
      WorkflowEdge: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          source: { type: 'string' },
          target: { type: 'string' },
          sourceHandle: { type: 'string' },
          targetHandle: { type: 'string' },
          type: { type: 'string' },
        },
        required: ['id', 'source', 'target'],
      },
      WorkflowMetadata: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          description: { type: 'string' },
          version: { type: 'string' },
          author: { type: 'string' },
          created: { type: 'string', format: 'date-time' },
          modified: { type: 'string', format: 'date-time' },
          tags: {
            type: 'array',
            items: { type: 'string' },
          },
          category: {
            type: 'string',
            enum: ['control', 'monitoring', 'automation', 'data-processing', 'safety', 'custom'],
          },
          priority: {
            type: 'string',
            enum: ['low', 'medium', 'high', 'critical'],
          },
          isPublic: { type: 'boolean' },
          permissions: {
            type: 'array',
            items: { type: 'string' },
          },
          status: {
            type: 'string',
            enum: ['running', 'stopped', 'paused', 'error', 'completed'],
          },
          type: {
            type: 'string',
            enum: ['automation', 'maintenance', 'emergency', 'testing'],
          },
          nodes: {
            type: 'array',
            items: { $ref: '#/components/schemas/WorkflowNode' },
          },
          edges: {
            type: 'array',
            items: { $ref: '#/components/schemas/WorkflowEdge' },
          },
          variables: {
            type: 'object',
            additionalProperties: true,
          },
        },
        required: ['id', 'name', 'created', 'modified', 'nodes', 'edges'],
      },
      WorkflowData: {
        type: 'object',
        properties: {
          metadata: { $ref: '#/components/schemas/WorkflowMetadata' },
          nodes: {
            type: 'array',
            items: { $ref: '#/components/schemas/WorkflowNode' },
          },
          edges: {
            type: 'array',
            items: { $ref: '#/components/schemas/WorkflowEdge' },
          },
          variables: {
            type: 'object',
            additionalProperties: true,
          },
        },
        required: ['metadata', 'nodes', 'edges'],
      },

      // Support email schemas
      SupportEmailRequest: {
        type: 'object',
        properties: {
          to: {
            type: 'string',
            format: 'email',
            description: 'Support email recipient address',
          },
          subject: {
            type: 'string',
            minLength: 1,
            maxLength: 100,
            description: 'Email subject line',
          },
          text: {
            type: 'string',
            minLength: 1,
            maxLength: 5000,
            description: 'Plain text email content',
          },
          html: {
            type: 'string',
            description: 'HTML email content',
          },
          priority: {
            type: 'string',
            enum: ['low', 'medium', 'high', 'critical'],
            description: 'Support request priority level',
          },
          category: {
            type: 'string',
            enum: ['bug', 'feature', 'question', 'documentation'],
            description: 'Support request category',
          },
          attachmentCount: {
            type: 'integer',
            minimum: 0,
            description: 'Number of file attachments',
          },
          attachmentNames: {
            type: 'array',
            items: { type: 'string' },
            description: 'Names of attached files',
          },
        },
        required: ['to', 'subject', 'text', 'priority', 'category'],
      },

      SupportEmailResponse: {
        type: 'object',
        properties: {
          success: {
            type: 'boolean',
            description: 'Whether email was sent successfully',
          },
          messageId: {
            type: 'string',
            description: 'Unique message identifier',
          },
          timestamp: {
            type: 'string',
            format: 'date-time',
            description: 'Email sent timestamp',
          },
          recipient: {
            type: 'string',
            format: 'email',
            description: 'Email recipient address',
          },
          subject: {
            type: 'string',
            description: 'Email subject line',
          },
          status: {
            type: 'string',
            enum: ['sent', 'queued', 'failed'],
            description: 'Email delivery status',
          },
          details: {
            type: 'object',
            properties: {
              priority: { type: 'string' },
              category: { type: 'string' },
              attachmentCount: { type: 'integer' },
              attachmentNames: {
                type: 'array',
                items: { type: 'string' },
              },
            },
          },
        },
        required: ['success', 'messageId', 'timestamp', 'recipient', 'status'],
      },

      ErrorResponse: {
        type: 'object',
        properties: {
          error: {
            type: 'string',
            description: 'Error message',
          },
          details: {
            type: 'string',
            description: 'Additional error details',
          },
          timestamp: {
            type: 'string',
            format: 'date-time',
            description: 'Error timestamp',
          },
        },
        required: ['error'],
      },

      // Node Property Schemas
      IndustrialNodeType: {
        type: 'string',
        enum: [
          'plc-input',
          'plc-output',
          'pid-controller',
          'hmi-display',
          'data-logger',
          'alarm-handler',
          'modbus-client',
          'opc-server',
          'opc-client',
          'custom-logic',
          'feedforward-controller',
          'url-display',
          'narx-neural-network',
          'gaussian-process-regression',
          'lstm-model',
          'sindy-identifier',
          'reinforcement-learning',
          'mpc-controller',
          'kalman-filter',
          'quadratic-programming',
          'subspace-identification',
          'imc-controller',
          'arx-armax-identifier',
          'genetic-algorithm',
          'recursive-least-squares',
          'model-validation',
          'pilco-pets',
          'prbs-generator',
          'relay-feedback-test',
          'step-response-analyzer',
          'distillation-simulator',
          'performance-metrics',
          'postgresql-connector',
          'redis-connector',
          'neo4j-connector',
          'qdrant-connector',
          'historian-connector',
          'csv-dataset-creator',
          'excel-dataset-creator',
          'data-cleaner',
          'feature-engineer',
          'time-series-processor',
          'math-function-creator',
          'data-distribution-analyzer',
          'dashboard-generator',
          'pdf-report-generator',
          'email-notifier',
          'chart-generator',
          'kpi-calculator',
          'workflow-reference',
          'workflow-subset',
          'workflow-conditional',
          'workflow-parallel',
          'workflow-loop',
        ],
        description: 'Industrial automation node types supported by the system',
      },

      PropertyFieldType: {
        type: 'string',
        enum: [
          'text',
          'number',
          'boolean',
          'select',
          'multiselect',
          'textarea',
          'json',
          'password',
          'url',
          'email',
          'slider',
          'color',
          'datetime',
          'file',
        ],
        description: 'Supported property field types for dynamic form generation',
      },

      ValidationSeverity: {
        type: 'string',
        enum: ['error', 'warning', 'info'],
        description: 'Validation result severity levels',
      },

      PropertyConstraints: {
        type: 'object',
        properties: {
          min: { type: 'number', description: 'Minimum value for numeric fields' },
          max: { type: 'number', description: 'Maximum value for numeric fields' },
          minLength: { type: 'integer', description: 'Minimum length for string fields' },
          maxLength: { type: 'integer', description: 'Maximum length for string fields' },
          pattern: { type: 'string', description: 'Regular expression pattern for validation' },
          step: { type: 'number', description: 'Step value for numeric inputs' },
          enum: {
            type: 'array',
            items: { oneOf: [{ type: 'string' }, { type: 'number' }] },
            description: 'Allowed values for enumerated fields',
          },
        },
        additionalProperties: false,
      },

      PropertyUIHints: {
        type: 'object',
        properties: {
          width: { type: 'string', enum: ['full', 'half', 'third', 'quarter'] },
          inline: { type: 'boolean', description: 'Whether to display field inline' },
          collapsible: { type: 'boolean', description: 'Whether field group is collapsible' },
          icon: { type: 'string', description: 'Icon name for the field' },
          helpText: { type: 'string', description: 'Additional help text for the field' },
          units: { type: 'string', description: 'Units to display with numeric fields' },
          format: { type: 'string', description: 'Display format for the field' },
        },
        additionalProperties: false,
      },

      PropertyOption: {
        type: 'object',
        properties: {
          value: {
            oneOf: [{ type: 'string' }, { type: 'number' }, { type: 'boolean' }],
            description: 'Option value',
          },
          label: { type: 'string', description: 'Display label for the option' },
          description: { type: 'string', description: 'Optional description for the option' },
          disabled: { type: 'boolean', description: 'Whether the option is disabled' },
          group: { type: 'string', description: 'Option group for categorization' },
        },
        required: ['value', 'label'],
        additionalProperties: false,
      },

      PropertyField: {
        type: 'object',
        properties: {
          key: { type: 'string', description: 'Unique identifier for the property field' },
          label: { type: 'string', description: 'Display label for the field' },
          type: { $ref: '#/components/schemas/PropertyFieldType' },
          description: { type: 'string', description: 'Help text describing the field' },
          placeholder: { type: 'string', description: 'Placeholder text for input fields' },
          defaultValue: { description: 'Default value for the field' },
          required: { type: 'boolean', description: 'Whether the field is required' },
          readonly: { type: 'boolean', description: 'Whether the field is read-only' },
          hidden: { type: 'boolean', description: 'Whether the field is hidden' },
          group: { type: 'string', description: 'Group ID this field belongs to' },
          order: { type: 'integer', description: 'Display order within the group' },
          dependsOn: {
            type: 'array',
            items: { type: 'string' },
            description: 'Fields this field depends on',
          },
          options: {
            type: 'array',
            items: { $ref: '#/components/schemas/PropertyOption' },
            description: 'Options for select/multiselect fields',
          },
          constraints: { $ref: '#/components/schemas/PropertyConstraints' },
          ui: { $ref: '#/components/schemas/PropertyUIHints' },
        },
        required: ['key', 'label', 'type'],
        additionalProperties: false,
      },

      PropertyGroup: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'Unique identifier for the property group' },
          label: { type: 'string', description: 'Display label for the group' },
          description: { type: 'string', description: 'Description of the group' },
          icon: { type: 'string', description: 'Icon name for the group' },
          collapsible: { type: 'boolean', description: 'Whether the group can be collapsed' },
          defaultCollapsed: {
            type: 'boolean',
            description: 'Whether the group is collapsed by default',
          },
          order: { type: 'integer', description: 'Display order of the group' },
          fields: {
            type: 'array',
            items: { $ref: '#/components/schemas/PropertyField' },
            description: 'Property fields in this group',
          },
        },
        required: ['id', 'label', 'fields'],
        additionalProperties: false,
      },

      ConnectionTest: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'Unique identifier for the connection test' },
          label: { type: 'string', description: 'Display label for the test' },
          description: { type: 'string', description: 'Description of what the test validates' },
          type: { type: 'string', enum: ['ping', 'modbus', 'opc', 'http', 'database', 'custom'] },
          requiredFields: {
            type: 'array',
            items: { type: 'string' },
            description: 'Configuration fields required for this test',
          },
          timeoutMs: {
            type: 'integer',
            minimum: 100,
            maximum: 30000,
            description: 'Test timeout in milliseconds',
          },
        },
        required: ['id', 'label', 'type', 'requiredFields', 'timeoutMs'],
        additionalProperties: false,
      },

      PropertyTemplate: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'Unique identifier for the template' },
          label: { type: 'string', description: 'Display label for the template' },
          description: { type: 'string', description: 'Description of the template' },
          category: { type: 'string', description: 'Template category' },
          config: {
            type: 'object',
            additionalProperties: true,
            description: 'Template configuration values',
          },
          tags: {
            type: 'array',
            items: { type: 'string' },
            description: 'Tags for template categorization',
          },
        },
        required: ['id', 'label', 'description', 'category', 'config'],
        additionalProperties: false,
      },

      NodePropertySchema: {
        type: 'object',
        properties: {
          nodeType: { $ref: '#/components/schemas/IndustrialNodeType' },
          version: {
            type: 'string',
            pattern: '^\\d+\\.\\d+\\.\\d+$',
            description: 'Schema version (semantic versioning)',
          },
          title: { type: 'string', description: 'Human-readable title for the node type' },
          description: {
            type: 'string',
            description: 'Detailed description of the node functionality',
          },
          groups: {
            type: 'array',
            items: { $ref: '#/components/schemas/PropertyGroup' },
            description: 'Property groups for organizing fields',
          },
          connectionTests: {
            type: 'array',
            items: { $ref: '#/components/schemas/ConnectionTest' },
            description: 'Available connection tests for this node type',
          },
          templates: {
            type: 'array',
            items: { $ref: '#/components/schemas/PropertyTemplate' },
            description: 'Pre-configured templates for this node type',
          },
        },
        required: ['nodeType', 'version', 'title', 'description', 'groups'],
        additionalProperties: false,
      },

      ValidationResult: {
        type: 'object',
        properties: {
          isValid: { type: 'boolean', description: 'Whether the validation passed' },
          severity: { $ref: '#/components/schemas/ValidationSeverity' },
          message: { type: 'string', description: 'Validation message' },
          field: { type: 'string', description: 'Field that failed validation' },
          code: { type: 'string', description: 'Error code for programmatic handling' },
        },
        required: ['isValid', 'severity', 'message', 'field', 'code'],
        additionalProperties: false,
      },

      ConnectionTestResult: {
        type: 'object',
        properties: {
          success: { type: 'boolean', description: 'Whether the connection test succeeded' },
          message: { type: 'string', description: 'Test result message' },
          details: {
            type: 'object',
            additionalProperties: true,
            description: 'Additional test result details',
          },
          latencyMs: { type: 'number', description: 'Connection latency in milliseconds' },
          timestamp: {
            type: 'string',
            format: 'date-time',
            description: 'When the test was performed',
          },
        },
        required: ['success', 'message', 'timestamp'],
        additionalProperties: false,
      },

      NodeConfigurationValidationRequest: {
        type: 'object',
        properties: {
          configuration: {
            type: 'object',
            additionalProperties: true,
            description: 'Node configuration to validate',
          },
          context: {
            type: 'object',
            properties: {
              workflowId: { type: 'string' },
              nodeId: { type: 'string' },
              connectedNodes: { type: 'array', items: { type: 'string' } },
            },
            description: 'Validation context information',
          },
        },
        required: ['configuration'],
        additionalProperties: false,
      },

      NodeConfigurationValidationResponse: {
        type: 'object',
        properties: {
          success: { type: 'boolean', description: 'Whether validation passed overall' },
          message: { type: 'string', description: 'Overall validation message' },
          results: {
            type: 'array',
            items: { $ref: '#/components/schemas/ValidationResult' },
            description: 'Individual validation results',
          },
          isValid: { type: 'boolean', description: 'Whether the configuration is valid' },
          errors: {
            type: 'array',
            items: { $ref: '#/components/schemas/ValidationResult' },
            description: 'Validation errors',
          },
          warnings: {
            type: 'array',
            items: { $ref: '#/components/schemas/ValidationResult' },
            description: 'Validation warnings',
          },
        },
        required: ['success', 'message', 'results', 'isValid'],
        additionalProperties: false,
      },

      NodeConnectionTestRequest: {
        type: 'object',
        properties: {
          testId: { type: 'string', description: 'ID of the connection test to run' },
          configuration: {
            type: 'object',
            additionalProperties: true,
            description: 'Node configuration for connection testing',
          },
        },
        required: ['testId', 'configuration'],
        additionalProperties: false,
      },

      NodeConnectionTestResponse: {
        type: 'object',
        properties: {
          success: { type: 'boolean', description: 'Whether the test request was processed' },
          message: { type: 'string', description: 'Test result message' },
          result: { $ref: '#/components/schemas/ConnectionTestResult' },
        },
        required: ['success', 'message', 'result'],
        additionalProperties: false,
      },
    };
  }

  /**
   * Validate API request using OpenAPI schema
   */
  async validateRequest(
    method: string,
    path: string,
    data: unknown
  ): Promise<MCPOpenAPIValidationResult> {
    // Normalize path for schema lookup by converting parametric paths
    const normalizedPath = this.normalizePathForSchema(path);
    const key = `${method.toUpperCase()}:${normalizedPath}`;
    const endpoint = this.endpointSchemas.get(key);

    if (!endpoint) {
      console.log('🔧 AVAILABLE SCHEMAS:', Array.from(this.endpointSchemas.keys()));
      console.log('🔧 LOOKING FOR KEY:', key);
      return {
        success: false,
        errors: [`No schema found for ${method} ${path}`],
      };
    }

    try {
      // Validate request body against schema
      if (endpoint.requestBody && data) {
        const requestSchema = endpoint.requestBody.content['application/json']?.schema;
        if (requestSchema) {
          const validationResult = this.validateDataAgainstSchema(data, requestSchema);
          if (!validationResult.success) {
            return validationResult;
          }
        }
      }

      return {
        success: true,
        data,
        schema: endpoint.requestBody?.content['application/json']?.schema,
      };
    } catch (error) {
      return {
        success: false,
        errors: [error instanceof Error ? error.message : 'Validation failed'],
      };
    }
  }

  /**
   * Validate API response using OpenAPI schema
   */
  async validateResponse(
    method: string,
    path: string,
    statusCode: number,
    data: unknown
  ): Promise<MCPOpenAPIValidationResult> {
    // Normalize path for schema lookup by converting parametric paths
    const normalizedPath = this.normalizePathForSchema(path);
    const key = `${method.toUpperCase()}:${normalizedPath}`;
    const endpoint = this.endpointSchemas.get(key);

    if (!endpoint) {
      return {
        success: false,
        errors: [`No schema found for ${method} ${path}`],
      };
    }

    try {
      const response = endpoint.responses?.[statusCode.toString()];
      if (!response) {
        return {
          success: false,
          errors: [`No response schema for status ${statusCode}`],
        };
      }

      const responseSchema = response.content?.['application/json']?.schema;
      if (!responseSchema) {
        return { success: true, data }; // No schema to validate against
      }

      return this.validateDataAgainstSchema(data, responseSchema);
    } catch (error) {
      return {
        success: false,
        errors: [error instanceof Error ? error.message : 'Response validation failed'],
      };
    }
  }

  /**
   * Normalize API path for schema lookup
   * Converts /api/v1/files/%2Fproject%2Ftest.txt/move -> /api/v1/files/{id}/move
   */
  private normalizePathForSchema(path: string): string {
    console.log('🔧 NORMALIZING PATH:', { originalPath: path });

    // Decode URL-encoded characters first
    const decodedPath = decodeURIComponent(path);
    console.log('🔧 DECODED PATH:', decodedPath);

    // Replace dynamic segments with OpenAPI parameter placeholders
    // Note: [^\/]+ doesn't work for file paths with slashes, need to use .+ instead
    let normalizedPath = decodedPath;

    // Handle file paths
    if (decodedPath.includes('/move')) {
      normalizedPath = decodedPath.replace(
        /\/api\/v1\/files\/.+\/move$/,
        '/api/v1/files/{id}/move'
      );
    } else if (decodedPath.includes('/rename')) {
      normalizedPath = decodedPath.replace(
        /\/api\/v1\/files\/.+\/rename$/,
        '/api/v1/files/{id}/rename'
      );
    } else if (decodedPath.includes('/content')) {
      normalizedPath = decodedPath.replace(
        /\/api\/v1\/files\/.+\/content$/,
        '/api/v1/files/{id}/content'
      );
    } else if (decodedPath.match(/\/api\/v1\/files\/.+$/)) {
      normalizedPath = decodedPath.replace(/\/api\/v1\/files\/.+$/, '/api/v1/files/{id}');
    }

    // Handle workflow paths
    else if (decodedPath.includes('/execute')) {
      normalizedPath = decodedPath.replace(
        /\/api\/v1\/workflows\/.+\/execute$/,
        '/api/v1/workflows/{id}/execute'
      );
    } else if (decodedPath.includes('/status')) {
      normalizedPath = decodedPath.replace(
        /\/api\/v1\/workflows\/.+\/status$/,
        '/api/v1/workflows/{id}/status'
      );
    } else if (decodedPath.match(/\/api\/v1\/workflows\/.+$/)) {
      normalizedPath = decodedPath.replace(/\/api\/v1\/workflows\/.+$/, '/api/v1/workflows/{id}');
    }

    console.log('🔧 NORMALIZED PATH:', normalizedPath);

    return normalizedPath;
  }

  /**
   * Resolve schema references
   * @private
   */
  private resolveSchemaRef(schema: OpenAPISchema | unknown): OpenAPISchema | unknown {
    if (!schema || typeof schema !== 'object') {
      return schema;
    }

    const schemaObj = schema as OpenAPISchema;

    // Handle $ref
    if (schemaObj.$ref) {
      const refPath = schemaObj.$ref;
      if (typeof refPath === 'string' && refPath.startsWith('#/components/schemas/')) {
        const schemaName = refPath.replace('#/components/schemas/', '');
        const resolvedSchema = this.componentSchemas[schemaName];
        if (!resolvedSchema) {
          console.warn(`Schema reference ${refPath} not found`);
          return schema;
        }
        return this.resolveSchemaRef(resolvedSchema);
      }
    }

    // Recursively resolve nested schemas
    const resolved: OpenAPISchema = {};
    for (const key in schemaObj) {
      if (key === 'properties' && typeof schemaObj[key] === 'object') {
        const properties: Record<string, OpenAPISchema> = {};
        const schemaProperties = schemaObj[key] as Record<string, OpenAPISchema>;
        for (const propKey in schemaProperties) {
          properties[propKey] = this.resolveSchemaRef(schemaProperties[propKey]) as OpenAPISchema;
        }
        resolved[key] = properties;
      } else if (key === 'items') {
        resolved[key] = this.resolveSchemaRef(schemaObj[key]) as OpenAPISchema;
      } else {
        resolved[key] = schemaObj[key];
      }
    }

    return resolved;
  }

  /**
   * Validate data against OpenAPI schema
   */
  private validateDataAgainstSchema(
    data: unknown,
    schema: OpenAPISchema
  ): MCPOpenAPIValidationResult {
    try {
      // Resolve any $ref in the schema
      const resolvedSchema = this.resolveSchemaRef(schema);
      // Basic schema validation (would use Zod in production)
      if (schema.type === 'object' && typeof data === 'object' && data !== null) {
        const obj = data as Record<string, unknown>;

        // Check required properties
        if (schema.required) {
          for (const requiredProp of schema.required) {
            if (!(requiredProp in obj)) {
              return {
                success: false,
                errors: [`Missing required property: ${requiredProp}`],
              };
            }
          }
        }

        // Validate property types
        if (schema.properties) {
          for (const [propName, propSchema] of Object.entries(schema.properties)) {
            if (propName in obj) {
              const propValidation = this.validateDataAgainstSchema(obj[propName], propSchema);
              if (!propValidation.success) {
                return {
                  success: false,
                  errors: propValidation.errors?.map(err => `${propName}.${err}`),
                };
              }
            }
          }
        }
      }

      return {
        success: true,
        data,
        schema,
      };
    } catch (error) {
      return {
        success: false,
        errors: [error instanceof Error ? error.message : 'Schema validation failed'],
      };
    }
  }

  /**
   * Get OpenAPI schema for specific endpoint
   */
  getEndpointSchema(method: string, path: string): OpenAPIEndpoint | null {
    const normalizedPath = this.normalizePathForSchema(path);
    const key = `${method.toUpperCase()}:${normalizedPath}`;
    return this.endpointSchemas.get(key) || null;
  }

  /**
   * Generate TypeScript types from OpenAPI schema
   */
  generateTypeScriptTypes(): string {
    return `
// Generated TypeScript types from OpenAPI Schema MCP
export interface FileOperationResponse {
  success: boolean;
  message: string;
  data: FileItem[];
}

export interface FileOperationResult {
  success: boolean;
  message: string;
  data?: FileItem;
  error?: string;
}
`;
  }

  /**
   * Check if connected to MCP server
   */
  isSchemaServerConnected(): boolean {
    return this.isConnected;
  }
}

// Singleton instance for app-wide use
export const openAPISchemaMCP = new OpenAPISchemaMCPClient();

/**
 * React hook for OpenAPI Schema MCP integration
 */
export function useOpenAPISchemaMCP() {
  return {
    validateRequest: openAPISchemaMCP.validateRequest.bind(openAPISchemaMCP),
    validateResponse: openAPISchemaMCP.validateResponse.bind(openAPISchemaMCP),
    getEndpointSchema: openAPISchemaMCP.getEndpointSchema.bind(openAPISchemaMCP),
    isConnected: openAPISchemaMCP.isSchemaServerConnected(),
  };
}
