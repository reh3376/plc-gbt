/**
 * Enhanced Industrial Node Types - AI Task Orchestrator TypeScript Implementation
 *
 * @description Comprehensive industrial automation node type definitions
 * @compliance Strict TypeScript - zero `any` types policy
 * @phase Phase 2.2 - Enhanced Node Library
 */

import type { IndustrialNodeData, IndustrialNodeType } from '@/lib/types/workflow-management.types';
import type { Node, NodeProps } from '@xyflow/react';

// Extended node data interface for enhanced nodes
export interface EnhancedIndustrialNodeData extends IndustrialNodeData {
  readonly category: NodeCategory;
  readonly subCategory?: string;
  readonly version: string;
  readonly documentation?: string;
  readonly examples?: ReadonlyArray<NodeExample>;
  readonly validation?: NodeValidationRules;
  readonly performance?: NodePerformanceMetrics;
  readonly security?: NodeSecurityConfig;
  readonly cost?: NodeCostConfig;
}

// Node categories for better organization
export type NodeCategory =
  | 'input_output' // I/O operations
  | 'control' // Control logic
  | 'communication' // Network/protocol
  | 'data_processing' // Data transformation
  | 'safety' // Safety systems
  | 'analytics' // Data analysis
  | 'integration' // System integration
  | 'testing' // Testing/simulation
  | 'maintenance' // Maintenance operations
  | 'custom'; // Custom/user-defined

// Detailed industrial node types with subcategories
export interface IndustrialNodeTypeDefinition {
  readonly type: IndustrialNodeType;
  readonly category: NodeCategory;
  readonly subCategory: string;
  readonly displayName: string;
  readonly description: string;
  readonly icon: string;
  readonly color: string;
  readonly inputPorts: ReadonlyArray<NodePortDefinition>;
  readonly outputPorts: ReadonlyArray<NodePortDefinition>;
  readonly configSchema: NodeConfigSchema;
  readonly examples: ReadonlyArray<NodeExample>;
  readonly documentation: string;
  readonly tags: ReadonlyArray<string>;
  readonly version: string;
  readonly vendor?: string;
  readonly license?: string;
  readonly deprecated?: boolean;
  readonly experimental?: boolean;
}

// Node port definitions
export interface NodePortDefinition {
  readonly id: string;
  readonly name: string;
  readonly type: PortDataType;
  readonly required: boolean;
  readonly description: string;
  readonly multiple?: boolean; // Can accept multiple connections
  readonly validation?: PortValidationRules;
}

// Port data types for type safety
export type PortDataType =
  | 'boolean'
  | 'integer'
  | 'float'
  | 'string'
  | 'object'
  | 'array'
  | 'binary'
  | 'timestamp'
  | 'plc_tag'
  | 'alarm'
  | 'trend'
  | 'recipe'
  | 'any';

// Configuration schema for nodes
export interface NodeConfigSchema {
  readonly properties: Record<string, SchemaProperty>;
  readonly required: ReadonlyArray<string>;
  readonly additionalProperties?: boolean;
}

export interface SchemaProperty {
  readonly type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  readonly description: string;
  readonly default?: unknown;
  readonly enum?: ReadonlyArray<unknown>;
  readonly minimum?: number;
  readonly maximum?: number;
  readonly pattern?: string;
  readonly format?: string;
  readonly items?: SchemaProperty;
  readonly properties?: Record<string, SchemaProperty>;
}

// Node examples for documentation
export interface NodeExample {
  readonly title: string;
  readonly description: string;
  readonly config: Record<string, unknown>;
  readonly inputs?: Record<string, unknown>;
  readonly expectedOutputs?: Record<string, unknown>;
  readonly useCase: string;
}

// Validation rules
export interface NodeValidationRules {
  readonly configValidation?: Array<ValidationRule>;
  readonly runtimeValidation?: Array<ValidationRule>;
  readonly dataValidation?: Array<ValidationRule>;
}

export interface PortValidationRules {
  readonly dataType?: PortDataType;
  readonly range?: { min?: number; max?: number };
  readonly pattern?: string;
  readonly required?: boolean;
  readonly customValidation?: string; // JavaScript expression
}

export interface ValidationRule {
  readonly rule: string;
  readonly message: string;
  readonly severity: 'error' | 'warning' | 'info';
}

// Performance metrics
export interface NodePerformanceMetrics {
  readonly expectedExecutionTime: number; // milliseconds
  readonly memoryUsage: number; // MB
  readonly cpuUsage: number; // percentage
  readonly networkBandwidth?: number; // Mbps
  readonly scalability: 'low' | 'medium' | 'high';
  readonly reliability: number; // 0-1 score
}

// Security configuration
export interface NodeSecurityConfig {
  readonly accessLevel: 'public' | 'internal' | 'restricted' | 'classified';
  readonly encryption?: boolean;
  readonly authentication?: boolean;
  readonly auditLogging?: boolean;
  readonly dataClassification?: string;
  readonly complianceStandards?: ReadonlyArray<string>;
}

// Cost configuration
export interface NodeCostConfig {
  readonly computeCost: number; // per execution
  readonly storageCost?: number; // per MB
  readonly networkCost?: number; // per MB transferred
  readonly licenseCost?: number; // per month
  readonly currency: string;
}

// Enhanced node type with all metadata
// React Flow Node<T> where T is the data property type
export type EnhancedIndustrialNode = Node<EnhancedIndustrialNodeData>;
// For NodeProps, we need to define it properly without generic, similar to existing pattern
export interface EnhancedNodeProps extends NodeProps {
  readonly data: EnhancedIndustrialNodeData;
}

// Comprehensive node library definitions
export const ENHANCED_INDUSTRIAL_NODE_LIBRARY: ReadonlyArray<IndustrialNodeTypeDefinition> = [
  // ===== INPUT/OUTPUT NODES =====
  {
    type: 'plc-input',
    category: 'input_output',
    subCategory: 'Digital Input',
    displayName: 'PLC Digital Input',
    description: 'Reads digital signals from PLC input modules',
    icon: 'input-circle',
    color: '#3B82F6',
    inputPorts: [],
    outputPorts: [
      {
        id: 'digital_value',
        name: 'Digital Value',
        type: 'boolean',
        required: true,
        description: 'Current digital input state (true/false)',
      },
      {
        id: 'timestamp',
        name: 'Timestamp',
        type: 'timestamp',
        required: false,
        description: 'Time when value was read',
      },
    ],
    configSchema: {
      properties: {
        plcAddress: {
          type: 'string',
          description: 'PLC address or tag name',
          pattern: '^[A-Za-z][A-Za-z0-9_]*$',
        },
        scanRate: {
          type: 'number',
          description: 'Scan rate in milliseconds',
          minimum: 10,
          maximum: 10000,
          default: 100,
        },
        debounceTime: {
          type: 'number',
          description: 'Debounce time in milliseconds',
          minimum: 0,
          maximum: 1000,
          default: 50,
        },
        invertLogic: {
          type: 'boolean',
          description: 'Invert the input logic',
          default: false,
        },
      },
      required: ['plcAddress'],
    },
    examples: [
      {
        title: 'Emergency Stop Button',
        description: 'Monitor emergency stop button state',
        config: {
          plcAddress: 'EmergencyStop_PB',
          scanRate: 50,
          debounceTime: 100,
          invertLogic: true,
        },
        expectedOutputs: {
          digital_value: false,
          timestamp: '2025-01-01T00:00:00Z',
        },
        useCase: 'Safety system monitoring',
      },
    ],
    documentation:
      'Monitors digital input points from PLC hardware. Supports configurable scan rates and debouncing.',
    tags: ['plc', 'input', 'digital', 'hardware'],
    version: '2.1.0',
    vendor: 'Industrial Automation Inc.',
    license: 'MIT',
  },

  {
    type: 'plc-output',
    category: 'input_output',
    subCategory: 'Digital Output',
    displayName: 'PLC Digital Output',
    description: 'Controls digital outputs to PLC output modules',
    icon: 'output-circle',
    color: '#EF4444',
    inputPorts: [
      {
        id: 'control_signal',
        name: 'Control Signal',
        type: 'boolean',
        required: true,
        description: 'Digital control signal to output',
      },
      {
        id: 'enable',
        name: 'Enable',
        type: 'boolean',
        required: false,
        description: 'Enable/disable output control',
      },
    ],
    outputPorts: [
      {
        id: 'status',
        name: 'Status',
        type: 'boolean',
        required: true,
        description: 'Current output status',
      },
      {
        id: 'error',
        name: 'Error',
        type: 'string',
        required: false,
        description: 'Error message if operation fails',
      },
    ],
    configSchema: {
      properties: {
        plcAddress: {
          type: 'string',
          description: 'PLC output address or tag name',
          pattern: '^[A-Za-z][A-Za-z0-9_]*$',
        },
        safeState: {
          type: 'boolean',
          description: 'Safe state value when disabled',
          default: false,
        },
        pulseMode: {
          type: 'boolean',
          description: 'Enable pulse mode operation',
          default: false,
        },
        pulseDuration: {
          type: 'number',
          description: 'Pulse duration in milliseconds',
          minimum: 10,
          maximum: 10000,
          default: 500,
        },
      },
      required: ['plcAddress'],
    },
    examples: [
      {
        title: 'Motor Starter Control',
        description: 'Control a motor starter contactor',
        config: {
          plcAddress: 'Motor_Start_01',
          safeState: false,
          pulseMode: false,
        },
        inputs: {
          control_signal: true,
          enable: true,
        },
        expectedOutputs: {
          status: true,
        },
        useCase: 'Motor control system',
      },
    ],
    documentation:
      'Controls digital output points to PLC hardware. Supports safe states and pulse mode operation.',
    tags: ['plc', 'output', 'digital', 'control'],
    version: '2.1.0',
    vendor: 'Industrial Automation Inc.',
    license: 'MIT',
  },

  // ===== CONTROL NODES =====
  {
    type: 'pid-controller',
    category: 'control',
    subCategory: 'Process Control',
    displayName: 'PID Controller',
    description: 'Proportional-Integral-Derivative controller for process control',
    icon: 'trending-up',
    color: '#10B981',
    inputPorts: [
      {
        id: 'process_variable',
        name: 'Process Variable',
        type: 'float',
        required: true,
        description: 'Current process value to control',
      },
      {
        id: 'setpoint',
        name: 'Setpoint',
        type: 'float',
        required: true,
        description: 'Desired process value',
      },
      {
        id: 'enable',
        name: 'Enable',
        type: 'boolean',
        required: false,
        description: 'Enable/disable PID control',
      },
      {
        id: 'manual_output',
        name: 'Manual Output',
        type: 'float',
        required: false,
        description: 'Manual output value when not in auto mode',
      },
    ],
    outputPorts: [
      {
        id: 'control_output',
        name: 'Control Output',
        type: 'float',
        required: true,
        description: 'PID controller output value',
      },
      {
        id: 'error',
        name: 'Error',
        type: 'float',
        required: true,
        description: 'Current error (setpoint - process variable)',
      },
      {
        id: 'integral',
        name: 'Integral',
        type: 'float',
        required: false,
        description: 'Integral term value',
      },
      {
        id: 'derivative',
        name: 'Derivative',
        type: 'float',
        required: false,
        description: 'Derivative term value',
      },
    ],
    configSchema: {
      properties: {
        kp: {
          type: 'number',
          description: 'Proportional gain',
          minimum: 0,
          default: 1.0,
        },
        ki: {
          type: 'number',
          description: 'Integral gain',
          minimum: 0,
          default: 0.1,
        },
        kd: {
          type: 'number',
          description: 'Derivative gain',
          minimum: 0,
          default: 0.01,
        },
        outputMin: {
          type: 'number',
          description: 'Minimum output value',
          default: 0,
        },
        outputMax: {
          type: 'number',
          description: 'Maximum output value',
          default: 100,
        },
        integralLimit: {
          type: 'number',
          description: 'Integral windup limit',
          default: 100,
        },
        derivativeFilterTime: {
          type: 'number',
          description: 'Derivative filter time constant',
          minimum: 0,
          default: 0.1,
        },
        controlMode: {
          type: 'string',
          description: 'Control mode',
          enum: ['auto', 'manual', 'cascade'],
          default: 'auto',
        },
      },
      required: ['kp'],
    },
    examples: [
      {
        title: 'Temperature Control',
        description: 'Control temperature in a heating system',
        config: {
          kp: 2.0,
          ki: 0.5,
          kd: 0.1,
          outputMin: 0,
          outputMax: 100,
          controlMode: 'auto',
        },
        inputs: {
          process_variable: 75.2,
          setpoint: 80.0,
          enable: true,
        },
        expectedOutputs: {
          control_output: 65.3,
          error: 4.8,
        },
        useCase: 'HVAC temperature control',
      },
    ],
    documentation:
      'Advanced PID controller with anti-windup, derivative filtering, and multiple control modes.',
    tags: ['control', 'pid', 'process', 'automation'],
    version: '3.0.0',
    vendor: 'Process Control Systems',
    license: 'Commercial',
  },

  // ===== COMMUNICATION NODES =====
  {
    type: 'modbus-client',
    category: 'communication',
    subCategory: 'Industrial Protocols',
    displayName: 'Modbus TCP Client',
    description: 'Communicates with Modbus TCP/IP devices',
    icon: 'network',
    color: '#8B5CF6',
    inputPorts: [
      {
        id: 'trigger',
        name: 'Trigger',
        type: 'boolean',
        required: false,
        description: 'Trigger read/write operation',
      },
      {
        id: 'write_data',
        name: 'Write Data',
        type: 'array',
        required: false,
        description: 'Data to write to Modbus device',
      },
    ],
    outputPorts: [
      {
        id: 'read_data',
        name: 'Read Data',
        type: 'array',
        required: true,
        description: 'Data read from Modbus device',
      },
      {
        id: 'connection_status',
        name: 'Connection Status',
        type: 'boolean',
        required: true,
        description: 'Current connection status',
      },
      {
        id: 'error',
        name: 'Error',
        type: 'string',
        required: false,
        description: 'Communication error message',
      },
    ],
    configSchema: {
      properties: {
        ipAddress: {
          type: 'string',
          description: 'Modbus device IP address',
          pattern: '^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$',
        },
        port: {
          type: 'number',
          description: 'TCP port number',
          minimum: 1,
          maximum: 65535,
          default: 502,
        },
        unitId: {
          type: 'number',
          description: 'Modbus unit ID',
          minimum: 1,
          maximum: 255,
          default: 1,
        },
        functionCode: {
          type: 'number',
          description: 'Modbus function code',
          enum: [1, 2, 3, 4, 5, 6, 15, 16],
          default: 3,
        },
        startAddress: {
          type: 'number',
          description: 'Starting register address',
          minimum: 0,
          maximum: 65535,
          default: 0,
        },
        quantity: {
          type: 'number',
          description: 'Number of registers to read/write',
          minimum: 1,
          maximum: 125,
          default: 1,
        },
        pollInterval: {
          type: 'number',
          description: 'Polling interval in milliseconds',
          minimum: 100,
          maximum: 60000,
          default: 1000,
        },
        timeout: {
          type: 'number',
          description: 'Communication timeout in milliseconds',
          minimum: 100,
          maximum: 10000,
          default: 3000,
        },
      },
      required: ['ipAddress', 'functionCode', 'startAddress'],
    },
    examples: [
      {
        title: 'Read Holding Registers',
        description: 'Read temperature values from a Modbus temperature transmitter',
        config: {
          ipAddress: '192.168.1.100',
          port: 502,
          unitId: 1,
          functionCode: 3,
          startAddress: 40001,
          quantity: 4,
          pollInterval: 2000,
        },
        expectedOutputs: {
          read_data: [23.5, 24.1, 22.8, 25.0],
          connection_status: true,
        },
        useCase: 'Temperature monitoring system',
      },
    ],
    documentation:
      'Full-featured Modbus TCP client supporting all major function codes with automatic reconnection.',
    tags: ['modbus', 'communication', 'industrial', 'tcp'],
    version: '2.3.0',
    vendor: 'Industrial Communication Inc.',
    license: 'Apache-2.0',
  },

  // ===== DATA PROCESSING NODES =====
  {
    type: 'data-logger',
    category: 'data_processing',
    subCategory: 'Data Storage',
    displayName: 'Industrial Data Logger',
    description: 'Logs process data to various storage backends',
    icon: 'database',
    color: '#F59E0B',
    inputPorts: [
      {
        id: 'data',
        name: 'Data',
        type: 'object',
        required: true,
        description: 'Data object to log',
      },
      {
        id: 'timestamp',
        name: 'Timestamp',
        type: 'timestamp',
        required: false,
        description: 'Custom timestamp (uses current time if not provided)',
      },
      {
        id: 'tags',
        name: 'Tags',
        type: 'object',
        required: false,
        description: 'Metadata tags for the data',
      },
    ],
    outputPorts: [
      {
        id: 'success',
        name: 'Success',
        type: 'boolean',
        required: true,
        description: 'Whether logging was successful',
      },
      {
        id: 'record_id',
        name: 'Record ID',
        type: 'string',
        required: false,
        description: 'Unique ID of the logged record',
      },
      {
        id: 'error',
        name: 'Error',
        type: 'string',
        required: false,
        description: 'Error message if logging fails',
      },
    ],
    configSchema: {
      properties: {
        storageType: {
          type: 'string',
          description: 'Storage backend type',
          enum: ['postgresql', 'influxdb', 'timescaledb', 'csv', 'json'],
          default: 'postgresql',
        },
        connectionString: {
          type: 'string',
          description: 'Database connection string',
        },
        tableName: {
          type: 'string',
          description: 'Table or measurement name',
          default: 'process_data',
        },
        batchSize: {
          type: 'number',
          description: 'Batch size for bulk inserts',
          minimum: 1,
          maximum: 10000,
          default: 100,
        },
        flushInterval: {
          type: 'number',
          description: 'Flush interval in milliseconds',
          minimum: 1000,
          maximum: 300000,
          default: 10000,
        },
        retentionPeriod: {
          type: 'string',
          description: 'Data retention period (e.g., "30d", "1y")',
          default: '1y',
        },
        compression: {
          type: 'boolean',
          description: 'Enable data compression',
          default: true,
        },
        encryption: {
          type: 'boolean',
          description: 'Enable data encryption',
          default: false,
        },
      },
      required: ['storageType', 'connectionString'],
    },
    examples: [
      {
        title: 'Process Data Logging',
        description: 'Log temperature and pressure data to PostgreSQL',
        config: {
          storageType: 'postgresql',
          connectionString: 'postgresql://user:pass@localhost:5432/factory',
          tableName: 'process_measurements',
          batchSize: 50,
          flushInterval: 5000,
        },
        inputs: {
          data: {
            temperature: 75.2,
            pressure: 14.7,
            flow_rate: 125.5,
          },
          tags: {
            unit: 'reactor_01',
            shift: 'day',
          },
        },
        expectedOutputs: {
          success: true,
          record_id: 'log_12345',
        },
        useCase: 'Manufacturing data collection',
      },
    ],
    documentation:
      'High-performance data logger supporting multiple storage backends with batching and compression.',
    tags: ['data', 'logging', 'storage', 'historian'],
    version: '2.5.0',
    vendor: 'Data Systems Corp.',
    license: 'Commercial',
  },

  // ===== SAFETY NODES =====
  {
    type: 'safety-interlock',
    category: 'safety',
    subCategory: 'Safety Logic',
    displayName: 'Safety Interlock',
    description: 'Implements safety interlock logic with fail-safe operation',
    icon: 'shield-check',
    color: '#DC2626',
    inputPorts: [
      {
        id: 'conditions',
        name: 'Safety Conditions',
        type: 'array',
        required: true,
        description: 'Array of safety condition states',
        multiple: true,
      },
      {
        id: 'reset',
        name: 'Reset',
        type: 'boolean',
        required: false,
        description: 'Reset interlock (requires manual intervention)',
      },
      {
        id: 'bypass',
        name: 'Bypass',
        type: 'boolean',
        required: false,
        description: 'Bypass interlock (requires authorization)',
      },
    ],
    outputPorts: [
      {
        id: 'safe_to_operate',
        name: 'Safe to Operate',
        type: 'boolean',
        required: true,
        description: 'True when all safety conditions are met',
      },
      {
        id: 'alarm',
        name: 'Alarm',
        type: 'object',
        required: false,
        description: 'Safety alarm information',
      },
      {
        id: 'trip_reason',
        name: 'Trip Reason',
        type: 'string',
        required: false,
        description: 'Reason for safety trip',
      },
    ],
    configSchema: {
      properties: {
        interlockMode: {
          type: 'string',
          description: 'Interlock operation mode',
          enum: ['fail_safe', 'fail_secure', 'voting_2oo3'],
          default: 'fail_safe',
        },
        requireManualReset: {
          type: 'boolean',
          description: 'Require manual reset after trip',
          default: true,
        },
        bypassEnabled: {
          type: 'boolean',
          description: 'Allow bypass operation',
          default: false,
        },
        bypassTimeout: {
          type: 'number',
          description: 'Bypass timeout in seconds',
          minimum: 60,
          maximum: 3600,
          default: 300,
        },
        alarmPriority: {
          type: 'string',
          description: 'Alarm priority level',
          enum: ['low', 'medium', 'high', 'critical'],
          default: 'critical',
        },
        logEvents: {
          type: 'boolean',
          description: 'Log all interlock events',
          default: true,
        },
      },
      required: ['interlockMode'],
    },
    examples: [
      {
        title: 'Emergency Stop System',
        description: 'Implement emergency stop safety interlock',
        config: {
          interlockMode: 'fail_safe',
          requireManualReset: true,
          bypassEnabled: false,
          alarmPriority: 'critical',
        },
        inputs: {
          conditions: [true, true, false, true], // One condition is false
          reset: false,
          bypass: false,
        },
        expectedOutputs: {
          safe_to_operate: false,
          alarm: {
            type: 'safety_trip',
            priority: 'critical',
            message: 'Safety condition violation detected',
          },
          trip_reason: 'Emergency stop activated',
        },
        useCase: 'Machine safety system',
      },
    ],
    documentation: 'Certified safety interlock with SIL-rated logic and comprehensive audit trail.',
    tags: ['safety', 'interlock', 'fail-safe', 'sil-rated'],
    version: '1.2.0',
    vendor: 'Safety Systems International',
    license: 'Commercial',
  },
];

// Helper functions for node management
export const getNodesByCategory = (
  category: NodeCategory
): ReadonlyArray<IndustrialNodeTypeDefinition> => {
  return ENHANCED_INDUSTRIAL_NODE_LIBRARY.filter(node => node.category === category);
};

export const getNodeByType = (
  type: IndustrialNodeType
): IndustrialNodeTypeDefinition | undefined => {
  return ENHANCED_INDUSTRIAL_NODE_LIBRARY.find(node => node.type === type);
};

export const getNodeCategories = (): ReadonlyArray<NodeCategory> => {
  const categories = new Set(ENHANCED_INDUSTRIAL_NODE_LIBRARY.map(node => node.category));
  return Array.from(categories);
};

export const searchNodes = (query: string): ReadonlyArray<IndustrialNodeTypeDefinition> => {
  const lowerQuery = query.toLowerCase();
  return ENHANCED_INDUSTRIAL_NODE_LIBRARY.filter(
    node =>
      node.displayName.toLowerCase().includes(lowerQuery) ||
      node.description.toLowerCase().includes(lowerQuery) ||
      node.tags.some(tag => tag.toLowerCase().includes(lowerQuery)) ||
      node.category.toLowerCase().includes(lowerQuery)
  );
};
