/**
 * OpenAPI Schema Store
 * Manages storage and retrieval of OpenAPI schemas
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export interface OpenAPISchema {
  openapi: string;
  info: {
    title: string;
    version: string;
    description?: string;
  };
  servers?: Array<{
    url: string;
    description?: string;
  }>;
  paths: Record<string, any>;
  components?: {
    schemas?: Record<string, any>;
    responses?: Record<string, any>;
    parameters?: Record<string, any>;
    securitySchemes?: Record<string, any>;
  };
}

export class SchemaStore {
  private schemas: Map<string, OpenAPISchema> = new Map();
  private schemaDir: string;

  constructor() {
    // Store schemas in a data directory
    this.schemaDir = join(__dirname, '../../data/schemas');
    this.ensureDirectoryExists();
    this.loadExistingSchemas();
  }

  private ensureDirectoryExists(): void {
    if (!existsSync(this.schemaDir)) {
      mkdirSync(this.schemaDir, { recursive: true });
    }
  }

  private loadExistingSchemas(): void {
    // Load the default PLC-GBT OpenAPI schema
    const defaultSchemaPath = join(this.schemaDir, 'plc-gbt-api.json');
    if (existsSync(defaultSchemaPath)) {
      try {
        const schema = JSON.parse(readFileSync(defaultSchemaPath, 'utf-8'));
        this.schemas.set('plc-gbt-api', schema);
        console.log('Loaded existing PLC-GBT API schema');
      } catch (error) {
        console.error('Failed to load default schema:', error);
      }
    } else {
      // Initialize with the schemas from the fake client
      this.initializeDefaultSchemas();
    }
  }

  private initializeDefaultSchemas(): void {
    // Create the default PLC-GBT OpenAPI schema based on the fake implementation
    const defaultSchema: OpenAPISchema = {
      openapi: '3.0.3',
      info: {
        title: 'PLC-GBT API',
        version: '1.0.0',
        description: 'Industrial automation workflow management API'
      },
      servers: [
        {
          url: 'http://localhost:3000/api/v1',
          description: 'Development server'
        }
      ],
      paths: this.getDefaultPaths(),
      components: {
        schemas: this.getDefaultSchemas()
      }
    };

    this.registerSchema('plc-gbt-api', defaultSchema);
  }

  private getDefaultPaths(): Record<string, any> {
    // These match the endpoints from the fake client
    return {
      '/files': {
        get: {
          operationId: 'getFiles',
          summary: 'Get file tree',
          responses: {
            '200': {
              description: 'File tree retrieved successfully',
              content: {
                'application/json': {
                  schema: {
                    $ref: '#/components/schemas/FileOperationResponse'
                  }
                }
              }
            }
          }
        }
      },
      '/workflows': {
        get: {
          operationId: 'getWorkflows',
          summary: 'Get all workflows',
          responses: {
            '200': {
              description: 'Workflows retrieved successfully',
              content: {
                'application/json': {
                  schema: {
                    $ref: '#/components/schemas/WorkflowListResponse'
                  }
                }
              }
            }
          }
        },
        post: {
          operationId: 'createWorkflow',
          summary: 'Create new workflow',
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/CreateWorkflowRequest'
                }
              }
            }
          },
          responses: {
            '201': {
              description: 'Workflow created successfully',
              content: {
                'application/json': {
                  schema: {
                    $ref: '#/components/schemas/WorkflowOperationResult'
                  }
                }
              }
            }
          }
        }
      },
      '/node-properties/{nodeType}': {
        get: {
          operationId: 'getNodePropertySchema',
          summary: 'Get node property schema',
          parameters: [
            {
              name: 'nodeType',
              in: 'path',
              required: true,
              schema: {
                $ref: '#/components/schemas/IndustrialNodeType'
              }
            }
          ],
          responses: {
            '200': {
              description: 'Node property schema retrieved successfully',
              content: {
                'application/json': {
                  schema: {
                    $ref: '#/components/schemas/NodePropertySchemaResponse'
                  }
                }
              }
            }
          }
        }
      }
    };
  }

  private getDefaultSchemas(): Record<string, any> {
    // Import schemas from the fake client implementation
    return {
      // Base response schemas
      FileOperationResponse: {
        type: 'object',
        required: ['success', 'message', 'data'],
        properties: {
          success: { type: 'boolean' },
          message: { type: 'string' },
          data: {
            type: 'array',
            items: { $ref: '#/components/schemas/FileItem' }
          }
        }
      },
      FileItem: {
        type: 'object',
        required: ['id', 'name', 'type'],
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          type: { type: 'string', enum: ['file', 'folder'] },
          path: { type: 'string' },
          size: { type: 'integer' },
          modified: { type: 'string', format: 'date-time' }
        }
      },
      // Workflow schemas
      WorkflowNode: {
        type: 'object',
        required: ['id', 'type', 'position', 'data'],
        properties: {
          id: { type: 'string' },
          type: { type: 'string' },
          position: {
            type: 'object',
            properties: {
              x: { type: 'number' },
              y: { type: 'number' }
            },
            required: ['x', 'y']
          },
          data: {
            type: 'object',
            properties: {
              label: { type: 'string' },
              description: { type: 'string' },
              status: { type: 'string' }
            },
            required: ['label']
          }
        }
      },
      WorkflowEdge: {
        type: 'object',
        required: ['id', 'source', 'target'],
        properties: {
          id: { type: 'string' },
          source: { type: 'string' },
          target: { type: 'string' },
          sourceHandle: { type: 'string' },
          targetHandle: { type: 'string' },
          type: { type: 'string' }
        }
      },
      WorkflowMetadata: {
        type: 'object',
        required: ['id', 'name', 'created', 'modified', 'nodes', 'edges'],
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
            items: { type: 'string' }
          },
          nodes: {
            type: 'array',
            items: { $ref: '#/components/schemas/WorkflowNode' }
          },
          edges: {
            type: 'array',
            items: { $ref: '#/components/schemas/WorkflowEdge' }
          }
        }
      },
      // Industrial node type enum
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
          'custom-logic'
          // ... add all 54 types
        ]
      },
      // Node property schemas
      NodePropertySchema: {
        type: 'object',
        required: ['nodeType', 'version', 'title', 'description', 'groups'],
        properties: {
          nodeType: { $ref: '#/components/schemas/IndustrialNodeType' },
          version: { type: 'string', pattern: '^\\d+\\.\\d+\\.\\d+$' },
          title: { type: 'string' },
          description: { type: 'string' },
          groups: {
            type: 'array',
            items: { $ref: '#/components/schemas/PropertyGroup' }
          }
        }
      },
      PropertyGroup: {
        type: 'object',
        required: ['id', 'label', 'fields'],
        properties: {
          id: { type: 'string' },
          label: { type: 'string' },
          description: { type: 'string' },
          collapsible: { type: 'boolean' },
          fields: {
            type: 'array',
            items: { $ref: '#/components/schemas/PropertyField' }
          }
        }
      },
      PropertyField: {
        type: 'object',
        required: ['key', 'label', 'type'],
        properties: {
          key: { type: 'string' },
          label: { type: 'string' },
          type: { type: 'string' },
          description: { type: 'string' },
          required: { type: 'boolean' },
          defaultValue: {}
        }
      }
    };
  }

  public registerSchema(name: string, schema: OpenAPISchema): void {
    this.schemas.set(name, schema);
    
    // Persist to disk
    const schemaPath = join(this.schemaDir, `${name}.json`);
    writeFileSync(schemaPath, JSON.stringify(schema, null, 2));
    
    console.log(`Registered OpenAPI schema: ${name}`);
  }

  public getSchema(name: string): OpenAPISchema | undefined {
    return this.schemas.get(name);
  }

  public getAllSchemas(): Map<string, OpenAPISchema> {
    return this.schemas;
  }

  public getComponentSchema(schemaName: string, componentName: string): any {
    const schema = this.schemas.get(schemaName);
    if (!schema || !schema.components?.schemas) {
      return undefined;
    }
    return schema.components.schemas[componentName];
  }
}
