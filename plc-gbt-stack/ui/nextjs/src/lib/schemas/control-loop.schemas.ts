/**
 * Comprehensive Control Loop Zod Schemas for Phase 31.7
 * AI Task Orchestrator Generated - Runtime Validation & Type Inference
 * 
 * Provides Zod schemas matching the enhanced TypeScript types
 * Follows user standards: Zod as de-facto validation library [[memory:4185841]]
 * Enables runtime validation with type inference for React components
 */

import { z } from "zod"

// Engineering Units Schema
const engineeringUnitsSchema = z.enum([
  'Percent', 'PSI', 'Bar', 
  'Celsius', 'Fahrenheit', 'Kelvin',
  'GPM', 'M3/H', 'LBS/H', 'KG/H', 
  'Volts', 'mA'
])

// Control Loop Type Schema
const controlLoopTypeSchema = z.enum([
  'ladder_logic_standard_pid',
  'ladder_logic_advanced_pid', 
  'function_block_standard_pide',
  'function_block_advanced_pide'
])

// Control Mode Schema
const controlModeSchema = z.enum([
  'Manual', 'Automatic', 'Cascade', 
  'Override', 'Program', 'Ratio'
])

// Algorithm Form Schema
const algorithmFormSchema = z.enum([
  'dependent', 'independent', 
  'parallel', 'series'
])

// Control Action Schema
const controlActionSchema = z.enum(['direct', 'reverse'])

// Process Variable Schema
const processVariableSchema = z.object({
  tag_name: z.string()
    .min(1, "Tag name is required")
    .max(40, "Tag name cannot exceed 40 characters")
    .regex(/^[A-Za-z][A-Za-z0-9_]*$/, "Tag name must start with letter and contain only alphanumeric characters and underscores"),
  engineering_units: engineeringUnitsSchema,
  range_min: z.number(),
  range_max: z.number(),
  current_value: z.number().optional(),
  quality: z.enum(['good', 'bad', 'uncertain']).default('good'),
  timestamp: z.date().optional()
}).refine((data) => data.range_max > data.range_min, {
  message: "Range max must be greater than range min",
  path: ["range_max"]
})

// Setpoint Schema
const setpointSchema = z.object({
  tag_name: z.string()
    .min(1, "Tag name is required")
    .max(40, "Tag name cannot exceed 40 characters")
    .regex(/^[A-Za-z][A-Za-z0-9_]*$/, "Tag name must follow PLC naming conventions"),
  engineering_units: engineeringUnitsSchema,
  value: z.number(),
  range_min: z.number(),
  range_max: z.number(),
  tracking_enabled: z.boolean().default(false)
}).refine((data) => data.range_max > data.range_min, {
  message: "Range max must be greater than range min",
  path: ["range_max"]
}).refine((data) => data.value >= data.range_min && data.value <= data.range_max, {
  message: "Setpoint value must be within specified range",
  path: ["value"]
})

// Control Output Schema
const controlOutputSchema = z.object({
  tag_name: z.string()
    .min(1, "Tag name is required")
    .max(40, "Tag name cannot exceed 40 characters")
    .regex(/^[A-Za-z][A-Za-z0-9_]*$/, "Tag name must follow PLC naming conventions"),
  engineering_units: engineeringUnitsSchema,
  range_min: z.number().min(0, "Output range minimum cannot be negative").max(100, "Output range minimum cannot exceed 100%"),
  range_max: z.number().min(0, "Output range maximum cannot be negative").max(100, "Output range maximum cannot exceed 100%"),
  initial_value: z.number().min(0, "Initial value cannot be negative").max(100, "Initial value cannot exceed 100%"),
  current_value: z.number().min(0).max(100).optional(),
  manual_value: z.number().min(0).max(100).optional()
}).refine((data) => data.range_max > data.range_min, {
  message: "Range max must be greater than range min",
  path: ["range_max"]
})

// PID Parameters Schema
const pidParametersSchema = z.object({
  proportional_gain: z.number()
    .min(0.001, "Proportional gain must be positive")
    .max(999.9, "Proportional gain cannot exceed 999.9"),
  integral_time: z.number()
    .min(0.01, "Integral time must be at least 0.01 minutes")
    .max(9999.0, "Integral time cannot exceed 9999 minutes"),
  derivative_time: z.number()
    .min(0.0, "Derivative time cannot be negative")
    .max(99.99, "Derivative time cannot exceed 99.99 minutes"),
  integral_hold: z.boolean().default(false),
  derivative_hold: z.boolean().default(false),
  proportional_bias: z.number().min(-100.0).max(100.0).optional(),
  integral_gain: z.number().min(0.0).max(999.9).optional(),
  derivative_gain: z.number().min(0.0).max(999.9).optional(),
  feedforward_gain: z.number().min(0.0).max(10.0).optional(),
  deadband: z.number().min(0.0).max(100.0).optional()
})

// Enhanced PIDE Parameters Schema
const pideParametersSchema = pidParametersSchema.extend({
  pgain: z.number().min(0.0).max(999.9).optional(),
  igain: z.number().min(0.0).max(999.9).optional(),
  dgain: z.number().min(0.0).max(999.9).optional(),
  bias: z.number().min(-100.0).max(100.0).optional(),
  maxcvpos: z.number().min(0.0).max(100.0).optional(),
  maxcvneg: z.number().min(0.0).max(100.0).optional(),
  pvtracking: z.boolean().default(false),
  swtracking: z.boolean().default(false)
})

// Scaling Configuration Schema
const scalingConfigurationSchema = z.object({
  pv_unscaled_min: z.number().default(0),
  pv_unscaled_max: z.number().default(16383),
  pv_engineering_min: z.number(),
  pv_engineering_max: z.number(),
  cv_unscaled_min: z.number().default(0),
  cv_unscaled_max: z.number().default(16383),
  cv_engineering_min: z.number().min(0).max(100),
  cv_engineering_max: z.number().min(0).max(100)
}).refine((data) => data.pv_unscaled_max > data.pv_unscaled_min, {
  message: "PV unscaled max must be greater than min",
  path: ["pv_unscaled_max"]
}).refine((data) => data.pv_engineering_max > data.pv_engineering_min, {
  message: "PV engineering max must be greater than min", 
  path: ["pv_engineering_max"]
}).refine((data) => data.cv_engineering_max > data.cv_engineering_min, {
  message: "CV engineering max must be greater than min",
  path: ["cv_engineering_max"]
})

// Control Limits Schema
const controlLimitsSchema = z.object({
  output_high_limit: z.number().min(0).max(100),
  output_low_limit: z.number().min(0).max(100),
  setpoint_high_limit: z.number(),
  setpoint_low_limit: z.number(),
  rate_limit: z.number().min(0).optional()
}).refine((data) => data.output_high_limit > data.output_low_limit, {
  message: "Output high limit must be greater than low limit",
  path: ["output_high_limit"]
}).refine((data) => data.setpoint_high_limit > data.setpoint_low_limit, {
  message: "Setpoint high limit must be greater than low limit",
  path: ["setpoint_high_limit"]
})

// Alarm Configuration Schema
const alarmConfigurationSchema = z.object({
  pv_high_alarm: z.number().optional(),
  pv_low_alarm: z.number().optional(),
  deviation_high_alarm: z.number().min(0).optional(),
  deviation_low_alarm: z.number().min(0).optional(),
  output_high_alarm: z.number().min(0).max(100).optional(),
  output_low_alarm: z.number().min(0).max(100).optional(),
  alarm_deadband: z.number().min(0).optional(),
  alarm_enabled: z.boolean().default(true)
}).refine((data) => {
  if (data.pv_high_alarm !== undefined && data.pv_low_alarm !== undefined) {
    return data.pv_high_alarm > data.pv_low_alarm
  }
  return true
}, {
  message: "PV high alarm must be greater than low alarm",
  path: ["pv_high_alarm"]
}).refine((data) => {
  if (data.output_high_alarm !== undefined && data.output_low_alarm !== undefined) {
    return data.output_high_alarm > data.output_low_alarm
  }
  return true
}, {
  message: "Output high alarm must be greater than low alarm",
  path: ["output_high_alarm"]
})

// Controller Options Schema
const controllerOptionsSchema = z.object({
  auto_manual_station: z.boolean().default(true),
  output_tracking: z.boolean().default(true),
  setpoint_tracking: z.boolean().default(false),
  zero_cross_time: z.number().min(0).max(3600).default(0),
  anti_windup_enabled: z.boolean().default(true),
  feedforward_enabled: z.boolean().default(false),
  cascade_enabled: z.boolean().default(false),
  derivative_on_error: z.boolean().default(true)
})

// Performance Metrics Schema
const performanceMetricsSchema = z.object({
  performance_score: z.number().min(0).max(100),
  oscillation_index: z.number().min(0).max(1),
  cv_saturation_percent: z.number().min(0).max(100),
  integral_absolute_error: z.number().min(0).optional(),
  settling_time: z.number().min(0).optional(),
  overshoot_percent: z.number().min(0).optional(),
  rise_time: z.number().min(0).optional(),
  last_calculated: z.date()
})

// Historical Data Point Schema
const historicalDataPointSchema = z.object({
  timestamp: z.date(),
  setpoint: z.number(),
  process_value: z.number(),
  control_output: z.number().min(0).max(100),
  error: z.number(),
  mode: controlModeSchema
})

// Tuning Session Schema
const tuningSessionSchema = z.object({
  id: z.string().min(1),
  started_at: z.date(),
  completed_at: z.date().optional(),
  method: z.enum(['manual', 'auto', 'ziegler_nichols', 'cohen_coon', 'internal_model_control']),
  initial_parameters: z.union([pidParametersSchema, pideParametersSchema]),
  final_parameters: z.union([pidParametersSchema, pideParametersSchema]).optional(),
  performance_improvement: z.number().min(-100).max(100).optional(),
  status: z.enum(['in_progress', 'completed', 'failed', 'cancelled']),
  notes: z.string().max(1000).optional()
})

// Cascade Configuration Schema
const cascadeConfigurationSchema = z.object({
  is_cascade: z.boolean(),
  cascade_type: z.enum(['master', 'slave']).optional(),
  master_loop_id: z.string().optional(),
  slave_loop_ids: z.array(z.string()).default([]),
  cascade_ratio: z.number().min(0).optional()
}).refine((data) => {
  if (data.is_cascade && data.cascade_type === 'slave') {
    return data.master_loop_id !== undefined
  }
  return true
}, {
  message: "Slave loops must specify a master loop ID",
  path: ["master_loop_id"]
})

// Enhanced Control Loop Schema
const enhancedControlLoopSchema = z.object({
  // Identification
  id: z.string().min(1),
  tag_name: z.string()
    .min(1, "Tag name is required")
    .max(40, "Tag name cannot exceed 40 characters")
    .regex(/^[A-Za-z][A-Za-z0-9_]*$/, "Tag name must follow PLC naming conventions"),
  name: z.string().min(1).max(200),
  description: z.string().max(500).optional(),
  
  // Classification
  type: controlLoopTypeSchema,
  algorithm_form: algorithmFormSchema,
  control_mode: controlModeSchema,
  control_action: controlActionSchema,
  
  // Core Configuration
  process_variable: processVariableSchema,
  setpoint: setpointSchema,
  control_output: controlOutputSchema,
  
  // PID/PIDE Parameters
  pid_parameters: z.union([pidParametersSchema, pideParametersSchema]),
  
  // Configuration
  scaling: scalingConfigurationSchema,
  limits: controlLimitsSchema,
  alarms: alarmConfigurationSchema,
  options: controllerOptionsSchema,
  
  // Status & Performance
  enabled: z.boolean(),
  status: z.enum(['running', 'stopped', 'error', 'tuning', 'manual', 'cascade']),
  scan_time: z.number().min(0.001).max(60.0),
  performance_metrics: performanceMetricsSchema,
  
  // Advanced Features
  cascade_config: cascadeConfigurationSchema.optional(),
  tuning_sessions: z.array(tuningSessionSchema).default([]),
  
  // Metadata
  created_at: z.date(),
  updated_at: z.date(),
  last_tuned: z.date().optional(),
  version: z.string().regex(/^\d+\.\d+\.\d+$/, "Version must follow semantic versioning"),
  schema_version: z.string().regex(/^\d{2}\.\d{2}\.\d{3}$/, "Schema version must follow XX.YY.ZZZ format")
})

// Control Loop Summary Schema
const controlLoopSummarySchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  type: controlLoopTypeSchema,
  status: z.enum(['running', 'stopped', 'error', 'tuning', 'manual', 'cascade']),
  setpoint: z.number(),
  process_value: z.number(),
  control_output: z.number().min(0).max(100),
  mode: controlModeSchema,
  performance_score: z.number().min(0).max(100),
  alarms_active: z.number().min(0),
  last_updated: z.date()
})

// Dashboard Filters Schema
const dashboardFiltersSchema = z.object({
  status: z.array(z.enum(['running', 'stopped', 'error', 'tuning', 'manual', 'cascade'])).optional(),
  type: z.array(controlLoopTypeSchema).optional(),
  performance_threshold: z.number().min(0).max(100).optional(),
  search: z.string().max(100).optional(),
  tags: z.array(z.string()).optional()
})

// Control Loop Update Schema
const controlLoopUpdateSchema = z.object({
  loop_id: z.string().min(1),
  timestamp: z.date(),
  updates: z.object({
    process_variable: processVariableSchema.partial(),
    control_output: controlOutputSchema.partial(),
    status: z.enum(['running', 'stopped', 'error', 'tuning', 'manual', 'cascade']),
    performance_metrics: performanceMetricsSchema.partial()
  }).partial()
})

// Tuning Request Schema
const tuningRequestSchema = z.object({
  loop_id: z.string().min(1),
  method: z.enum(['manual', 'auto', 'ziegler_nichols', 'cohen_coon', 'internal_model_control']),
  target_performance: z.number().min(0).max(100).optional(),
  constraints: z.object({
    max_overshoot: z.number().min(0).max(100).optional(),
    max_settling_time: z.number().min(0).optional(),
    stability_margin: z.number().min(0).max(1).optional()
  }).optional()
})

// Form schemas for creating/updating control loops
const createControlLoopSchema = enhancedControlLoopSchema.omit({ 
  id: true, 
  created_at: true, 
  updated_at: true,
  performance_metrics: true,
  tuning_sessions: true
})

const updateControlLoopSchema = enhancedControlLoopSchema.partial().required({ id: true })

// API Response Schemas
const controlLoopApiResponseSchema = z.object({
  success: z.boolean(),
  data: z.union([
    enhancedControlLoopSchema,
    z.array(enhancedControlLoopSchema),
    controlLoopSummarySchema,
    z.array(controlLoopSummarySchema)
  ]).optional(),
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.any().optional()
  }).optional(),
  timestamp: z.date(),
  pagination: z.object({
    page: z.number().min(1),
    limit: z.number().min(1).max(100),
    total: z.number().min(0),
    hasNext: z.boolean(),
    hasPrev: z.boolean()
  }).optional()
})

// Export all schemas
export {
  engineeringUnitsSchema,
  controlLoopTypeSchema,
  controlModeSchema,
  algorithmFormSchema,
  controlActionSchema,
  processVariableSchema,
  setpointSchema,
  controlOutputSchema,
  pidParametersSchema,
  pideParametersSchema,
  scalingConfigurationSchema,
  controlLimitsSchema,
  alarmConfigurationSchema,
  controllerOptionsSchema,
  performanceMetricsSchema,
  historicalDataPointSchema,
  tuningSessionSchema,
  cascadeConfigurationSchema,
  enhancedControlLoopSchema,
  controlLoopSummarySchema,
  dashboardFiltersSchema,
  controlLoopUpdateSchema,
  tuningRequestSchema,
  createControlLoopSchema,
  updateControlLoopSchema,
  controlLoopApiResponseSchema
}

// Type exports inferred from schemas
export type EngineeringUnits = z.infer<typeof engineeringUnitsSchema>
export type ControlLoopType = z.infer<typeof controlLoopTypeSchema>
export type ControlMode = z.infer<typeof controlModeSchema>
export type AlgorithmForm = z.infer<typeof algorithmFormSchema>
export type ControlAction = z.infer<typeof controlActionSchema>
export type ProcessVariable = z.infer<typeof processVariableSchema>
export type Setpoint = z.infer<typeof setpointSchema>
export type ControlOutput = z.infer<typeof controlOutputSchema>
export type PIDParameters = z.infer<typeof pidParametersSchema>
export type PIDEParameters = z.infer<typeof pideParametersSchema>
export type ScalingConfiguration = z.infer<typeof scalingConfigurationSchema>
export type ControlLimits = z.infer<typeof controlLimitsSchema>
export type AlarmConfiguration = z.infer<typeof alarmConfigurationSchema>
export type ControllerOptions = z.infer<typeof controllerOptionsSchema>
export type PerformanceMetrics = z.infer<typeof performanceMetricsSchema>
export type HistoricalDataPoint = z.infer<typeof historicalDataPointSchema>
export type TuningSession = z.infer<typeof tuningSessionSchema>
export type CascadeConfiguration = z.infer<typeof cascadeConfigurationSchema>
export type EnhancedControlLoop = z.infer<typeof enhancedControlLoopSchema>
export type ControlLoopSummary = z.infer<typeof controlLoopSummarySchema>
export type DashboardFilters = z.infer<typeof dashboardFiltersSchema>
export type ControlLoopUpdate = z.infer<typeof controlLoopUpdateSchema>
export type TuningRequest = z.infer<typeof tuningRequestSchema>
export type CreateControlLoop = z.infer<typeof createControlLoopSchema>
export type UpdateControlLoop = z.infer<typeof updateControlLoopSchema>
export type ControlLoopApiResponse = z.infer<typeof controlLoopApiResponseSchema> 