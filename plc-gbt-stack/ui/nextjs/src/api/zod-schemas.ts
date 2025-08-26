/**
 * Generated Zod Schemas from OpenAPI - AI Task Orchestrator TypeScript Implementation
 *
 * @description Type-safe runtime validation schemas generated from OpenAPI specification
 * @compliance Strict TypeScript - zero `any` types policy
 * @integration OpenAPI Schema MCP for validation
 * @note DO NOT EDIT - Generated from openapi.json
 */

import { z } from 'zod';

// Industrial Node Type Enum Schema
export const IndustrialNodeTypeSchema = z.enum([
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
  'n8n-workflow',
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
  // Enhanced Industrial PLC Connectivity Nodes
  'advanced-modbus-client',
  'advanced-opcua-client',
  'advanced-ethernet-ip',
]);

// Property Field Type Schema
export const PropertyFieldTypeSchema = z.enum([
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
]);

// Validation Severity Schema
export const ValidationSeveritySchema = z.enum(['error', 'warning', 'info']);

// Property Field Width Schema
export const PropertyFieldWidthSchema = z.enum(['full', 'half', 'third', 'quarter']);

// Connection Test Type Schema
export const ConnectionTestTypeSchema = z.enum([
  'ping',
  'modbus',
  'opc',
  'http',
  'database',
  'custom',
]);

// Property Constraints Schema
export const PropertyConstraintsSchema = z
  .object({
    min: z.number().optional(),
    max: z.number().optional(),
    minLength: z.number().int().optional(),
    maxLength: z.number().int().optional(),
    pattern: z.string().optional(),
    step: z.number().optional(),
    enum: z.array(z.union([z.string(), z.number()])).optional(),
  })
  .strict();

// Property UI Hints Schema
export const PropertyUIHintsSchema = z
  .object({
    width: PropertyFieldWidthSchema.optional(),
    inline: z.boolean().optional(),
    collapsible: z.boolean().optional(),
    icon: z.string().optional(),
    helpText: z.string().optional(),
    units: z.string().optional(),
    format: z.string().optional(),
  })
  .strict();

// Property Option Schema
export const PropertyOptionSchema = z
  .object({
    value: z.union([z.string(), z.number(), z.boolean()]),
    label: z.string(),
    description: z.string().optional(),
    disabled: z.boolean().optional(),
    group: z.string().optional(),
  })
  .strict();

// Property Field Schema
export const PropertyFieldSchema = z
  .object({
    key: z.string(),
    label: z.string(),
    type: PropertyFieldTypeSchema,
    description: z.string().optional(),
    placeholder: z.string().optional(),
    defaultValue: z.unknown().optional(),
    required: z.boolean().optional(),
    readonly: z.boolean().optional(),
    hidden: z.boolean().optional(),
    group: z.string().optional(),
    order: z.number().int().optional(),
    dependsOn: z.array(z.string()).optional(),
    options: z.array(PropertyOptionSchema).optional(),
    constraints: PropertyConstraintsSchema.optional(),
    ui: PropertyUIHintsSchema.optional(),
  })
  .strict();

// Property Group Schema
export const PropertyGroupSchema = z
  .object({
    id: z.string(),
    label: z.string(),
    description: z.string().optional(),
    icon: z.string().optional(),
    collapsible: z.boolean().optional(),
    defaultCollapsed: z.boolean().optional(),
    order: z.number().int().optional(),
    fields: z.array(PropertyFieldSchema),
  })
  .strict();

// Connection Test Schema
export const ConnectionTestSchema = z
  .object({
    id: z.string(),
    label: z.string(),
    description: z.string(),
    type: ConnectionTestTypeSchema,
    requiredFields: z.array(z.string()),
    timeoutMs: z.number().int().min(100).max(30000),
  })
  .strict();

// Property Template Schema
export const PropertyTemplateSchema = z
  .object({
    id: z.string(),
    label: z.string(),
    description: z.string(),
    category: z.string(),
    config: z.record(z.string(), z.unknown()),
    tags: z.array(z.string()),
  })
  .strict();

// Node Property Schema
export const NodePropertySchemaSchema = z
  .object({
    nodeType: IndustrialNodeTypeSchema,
    version: z.string().regex(/^\d+\.\d+\.\d+$/),
    title: z.string(),
    description: z.string(),
    groups: z.array(PropertyGroupSchema),
    connectionTests: z.array(ConnectionTestSchema).optional(),
    templates: z.array(PropertyTemplateSchema).optional(),
  })
  .strict();

// Validation Result Schema
export const ValidationResultSchema = z
  .object({
    isValid: z.boolean(),
    severity: ValidationSeveritySchema,
    message: z.string(),
    field: z.string(),
    code: z.string(),
  })
  .strict();

// Connection Test Result Schema
export const ConnectionTestResultSchema = z
  .object({
    success: z.boolean(),
    message: z.string(),
    details: z.record(z.string(), z.unknown()).optional(),
    latencyMs: z.number().optional(),
    timestamp: z.string().datetime(),
  })
  .strict();

// API Request/Response Schemas
export const NodeConfigurationValidationRequestSchema = z
  .object({
    configuration: z.record(z.string(), z.unknown()),
    context: z
      .object({
        workflowId: z.string().optional(),
        nodeId: z.string().optional(),
        connectedNodes: z.array(z.string()).optional(),
      })
      .optional(),
  })
  .strict();

export const NodeConfigurationValidationResponseSchema = z
  .object({
    success: z.boolean(),
    message: z.string(),
    results: z.array(ValidationResultSchema),
    isValid: z.boolean(),
    errors: z.array(ValidationResultSchema),
    warnings: z.array(ValidationResultSchema),
  })
  .strict();

export const NodeConnectionTestRequestSchema = z
  .object({
    testId: z.string(),
    configuration: z.record(z.string(), z.unknown()),
  })
  .strict();

export const NodeConnectionTestResponseSchema = z
  .object({
    success: z.boolean(),
    message: z.string(),
    result: ConnectionTestResultSchema,
  })
  .strict();

export const ErrorResponseSchema = z
  .object({
    error: z.string(),
    details: z.string().optional(),
    timestamp: z.string().datetime().optional(),
    code: z.string().optional(),
  })
  .strict();

// API Response Wrappers
export const NodePropertySchemaResponseSchema = z
  .object({
    success: z.boolean(),
    message: z.string(),
    data: NodePropertySchemaSchema,
  })
  .strict();

// Export types derived from Zod schemas
export type IndustrialNodeType = z.infer<typeof IndustrialNodeTypeSchema>;
export type PropertyFieldType = z.infer<typeof PropertyFieldTypeSchema>;
export type ValidationSeverity = z.infer<typeof ValidationSeveritySchema>;
export type PropertyFieldWidth = z.infer<typeof PropertyFieldWidthSchema>;
export type ConnectionTestType = z.infer<typeof ConnectionTestTypeSchema>;
export type PropertyConstraints = z.infer<typeof PropertyConstraintsSchema>;
export type PropertyUIHints = z.infer<typeof PropertyUIHintsSchema>;
export type PropertyOption = z.infer<typeof PropertyOptionSchema>;
export type PropertyField = z.infer<typeof PropertyFieldSchema>;
export type PropertyGroup = z.infer<typeof PropertyGroupSchema>;
export type ConnectionTest = z.infer<typeof ConnectionTestSchema>;
export type PropertyTemplate = z.infer<typeof PropertyTemplateSchema>;
export type NodePropertySchema = z.infer<typeof NodePropertySchemaSchema>;
export type ValidationResult = z.infer<typeof ValidationResultSchema>;
export type ConnectionTestResult = z.infer<typeof ConnectionTestResultSchema>;
export type NodeConfigurationValidationRequest = z.infer<
  typeof NodeConfigurationValidationRequestSchema
>;
export type NodeConfigurationValidationResponse = z.infer<
  typeof NodeConfigurationValidationResponseSchema
>;
export type NodeConnectionTestRequest = z.infer<typeof NodeConnectionTestRequestSchema>;
export type NodeConnectionTestResponse = z.infer<typeof NodeConnectionTestResponseSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
export type NodePropertySchemaResponse = z.infer<typeof NodePropertySchemaResponseSchema>;
