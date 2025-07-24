/**
 * Comprehensive Control Loop Types for Phase 31.7
 * AI Task Orchestrator Generated - Matches Backend JSON Schema Infrastructure
 * 
 * Based on robust backend schemas from Phase 20 JSON Schema Framework:
 * - Ladder Logic Standard/Advanced PID
 * - Function Block Standard/Advanced PIDE  
 * - Enhanced with TypeScript type safety and validation
 */

// Engineering Units Enumeration
type EngineeringUnits = 
  | 'Percent' | 'PSI' | 'Bar' 
  | 'Celsius' | 'Fahrenheit' | 'Kelvin'
  | 'GPM' | 'M3/H' | 'LBS/H' | 'KG/H' 
  | 'Volts' | 'mA'

// Control Loop Types
type ControlLoopType = 
  | 'ladder_logic_standard_pid'
  | 'ladder_logic_advanced_pid' 
  | 'function_block_standard_pide'
  | 'function_block_advanced_pide'

// Control Modes
type ControlMode = 
  | 'Manual' | 'Automatic' | 'Cascade' 
  | 'Override' | 'Program' | 'Ratio'

// Algorithm Forms  
type AlgorithmForm = 
  | 'dependent' | 'independent' 
  | 'parallel' | 'series'

// Control Actions
type ControlAction = 'direct' | 'reverse'

// Process Variable Configuration
interface ProcessVariable {
  tag_name: string
  engineering_units: EngineeringUnits
  range_min: number
  range_max: number
  current_value?: number
  quality?: 'good' | 'bad' | 'uncertain'
  timestamp?: Date
}

// Setpoint Configuration
interface Setpoint {
  tag_name: string
  engineering_units: EngineeringUnits
  value: number
  range_min: number
  range_max: number
  tracking_enabled?: boolean
}

// Control Output Configuration  
interface ControlOutput {
  tag_name: string
  engineering_units: EngineeringUnits
  range_min: number
  range_max: number
  initial_value: number
  current_value?: number
  manual_value?: number
}

// PID Parameters
interface PIDParameters {
  proportional_gain: number    // Kp
  integral_time: number       // Ti (minutes)
  derivative_time: number     // Td (minutes)
  integral_hold?: boolean
  derivative_hold?: boolean
  proportional_bias?: number
  integral_gain?: number      // Ki = Kp/Ti
  derivative_gain?: number    // Kd = Kp*Td
  feedforward_gain?: number
  deadband?: number
}

// Enhanced PID Parameters for PIDE
interface PIDEParameters extends PIDParameters {
  pgain?: number             // PIDE Proportional gain
  igain?: number             // PIDE Integral gain  
  dgain?: number             // PIDE Derivative gain
  bias?: number              // Output bias
  maxcvpos?: number          // Maximum positive CV rate
  maxcvneg?: number          // Maximum negative CV rate
  pvtracking?: boolean       // PV tracking enable
  swtracking?: boolean       // SW tracking enable
}

// Scaling Configuration
interface ScalingConfiguration {
  pv_unscaled_min: number    // MINI
  pv_unscaled_max: number    // MAXI  
  pv_engineering_min: number // MINS
  pv_engineering_max: number // MAXS
  cv_unscaled_min: number
  cv_unscaled_max: number
  cv_engineering_min: number
  cv_engineering_max: number
}

// Control Limits
interface ControlLimits {
  output_high_limit: number
  output_low_limit: number
  setpoint_high_limit: number
  setpoint_low_limit: number
  rate_limit?: number
}

// Alarm Configuration
interface AlarmConfiguration {
  pv_high_alarm?: number     // PVH
  pv_low_alarm?: number      // PVL
  deviation_high_alarm?: number // DVP
  deviation_low_alarm?: number  // DVN
  output_high_alarm?: number
  output_low_alarm?: number
  alarm_deadband?: number
  alarm_enabled: boolean
}

// Controller Options
interface ControllerOptions {
  auto_manual_station?: boolean
  output_tracking?: boolean
  setpoint_tracking?: boolean
  zero_cross_time?: number
  anti_windup_enabled?: boolean
  feedforward_enabled?: boolean
  cascade_enabled?: boolean
  derivative_on_error?: boolean  // DOE
}

// Performance Metrics
interface PerformanceMetrics {
  performance_score: number
  oscillation_index: number
  cv_saturation_percent: number
  integral_absolute_error?: number
  settling_time?: number
  overshoot_percent?: number
  rise_time?: number
  last_calculated: Date
}

// Historical Data Point
interface HistoricalDataPoint {
  timestamp: Date
  setpoint: number
  process_value: number
  control_output: number
  error: number
  mode: ControlMode
}

// Tuning Session Information
interface TuningSession {
  id: string
  started_at: Date
  completed_at?: Date
  method: 'manual' | 'auto' | 'ziegler_nichols' | 'cohen_coon' | 'internal_model_control'
  initial_parameters: PIDParameters | PIDEParameters
  final_parameters?: PIDParameters | PIDEParameters
  performance_improvement?: number
  status: 'in_progress' | 'completed' | 'failed' | 'cancelled'
  notes?: string
}

// Cascade Configuration
interface CascadeConfiguration {
  is_cascade: boolean
  cascade_type?: 'master' | 'slave'
  master_loop_id?: string
  slave_loop_ids?: string[]
  cascade_ratio?: number
}

// Comprehensive Control Loop Interface
interface EnhancedControlLoop {
  // Identification
  id: string
  tag_name: string
  name: string
  description?: string
  
  // Classification
  type: ControlLoopType
  algorithm_form: AlgorithmForm
  control_mode: ControlMode
  control_action: ControlAction
  
  // Core Configuration
  process_variable: ProcessVariable
  setpoint: Setpoint
  control_output: ControlOutput
  
  // PID/PIDE Parameters
  pid_parameters: PIDParameters | PIDEParameters
  
  // Configuration
  scaling: ScalingConfiguration
  limits: ControlLimits
  alarms: AlarmConfiguration
  options: ControllerOptions
  
  // Status & Performance
  enabled: boolean
  status: 'running' | 'stopped' | 'error' | 'tuning' | 'manual' | 'cascade'
  scan_time: number // seconds
  performance_metrics: PerformanceMetrics
  
  // Advanced Features
  cascade_config?: CascadeConfiguration
  tuning_sessions: TuningSession[]
  
  // Metadata
  created_at: Date
  updated_at: Date
  last_tuned?: Date
  version: string
  schema_version: string
}

// Control Loop Summary for Dashboard Cards
interface ControlLoopSummary {
  id: string
  name: string
  type: ControlLoopType
  status: 'running' | 'stopped' | 'error' | 'tuning' | 'manual' | 'cascade'
  setpoint: number
  process_value: number
  control_output: number
  mode: ControlMode
  performance_score: number
  alarms_active: number
  last_updated: Date
}

// Dashboard Filter Options
interface DashboardFilters {
  status?: ('running' | 'stopped' | 'error' | 'tuning' | 'manual' | 'cascade')[]
  type?: ControlLoopType[]
  performance_threshold?: number
  search?: string
  tags?: string[]
}

// Real-time Update Event
interface ControlLoopUpdate {
  loop_id: string
  timestamp: Date
  updates: Partial<Pick<EnhancedControlLoop, 'process_variable' | 'control_output' | 'status' | 'performance_metrics'>>
}

// Tuning Request
interface TuningRequest {
  loop_id: string
  method: 'manual' | 'auto' | 'ziegler_nichols' | 'cohen_coon' | 'internal_model_control'
  target_performance?: number
  constraints?: {
    max_overshoot?: number
    max_settling_time?: number
    stability_margin?: number
  }
}

// Export all types
export type {
  EngineeringUnits,
  ControlLoopType,
  ControlMode,
  AlgorithmForm,
  ControlAction,
  ProcessVariable,
  Setpoint,
  ControlOutput,
  PIDParameters,
  PIDEParameters,
  ScalingConfiguration,
  ControlLimits,
  AlarmConfiguration,
  ControllerOptions,
  PerformanceMetrics,
  HistoricalDataPoint,
  TuningSession,
  CascadeConfiguration,
  EnhancedControlLoop,
  ControlLoopSummary,
  DashboardFilters,
  ControlLoopUpdate,
  TuningRequest
} 