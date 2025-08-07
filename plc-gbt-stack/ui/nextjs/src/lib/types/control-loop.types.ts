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
  | 'Percent'
  | 'PSI'
  | 'Bar'
  | 'Celsius'
  | 'Fahrenheit'
  | 'Kelvin'
  | 'GPM'
  | 'M3/H'
  | 'LBS/H'
  | 'KG/H'
  | 'Volts'
  | 'mA';

// Control Loop Types
type ControlLoopType =
  | 'ladder_logic_standard_pid'
  | 'ladder_logic_advanced_pid'
  | 'function_block_standard_pide'
  | 'function_block_advanced_pide';

// Control Modes
type ControlMode = 'Manual' | 'Automatic' | 'Cascade' | 'Override' | 'Program' | 'Ratio';

// Algorithm Forms
type AlgorithmForm = 'dependent' | 'independent' | 'parallel' | 'series';

// Control Actions
type ControlAction = 'direct' | 'reverse';

// Process Variable Configuration
interface ProcessVariable {
  tag_name: string;
  engineering_units: EngineeringUnits;
  range_min: number;
  range_max: number;
  current_value?: number;
  quality?: 'good' | 'bad' | 'uncertain';
  timestamp?: Date;
}

// Setpoint Configuration
interface Setpoint {
  tag_name: string;
  engineering_units: EngineeringUnits;
  value: number;
  range_min: number;
  range_max: number;
  tracking_enabled?: boolean;
}

// Control Output Configuration
interface ControlOutput {
  tag_name: string;
  engineering_units: EngineeringUnits;
  range_min: number;
  range_max: number;
  initial_value: number;
  current_value?: number;
  manual_value?: number;
}

// PID Parameters
interface PIDParameters {
  proportional_gain: number; // Kp
  integral_time: number; // Ti (minutes)
  derivative_time: number; // Td (minutes)
  integral_hold?: boolean;
  derivative_hold?: boolean;
  proportional_bias?: number;
  integral_gain?: number; // Ki = Kp/Ti
  derivative_gain?: number; // Kd = Kp*Td
  feedforward_gain?: number;
  deadband?: number;
}

// Enhanced PID Parameters for PIDE
interface PIDEParameters extends PIDParameters {
  pgain?: number; // PIDE Proportional gain
  igain?: number; // PIDE Integral gain
  dgain?: number; // PIDE Derivative gain
  bias?: number; // Output bias
  maxcvpos?: number; // Maximum positive CV rate
  maxcvneg?: number; // Maximum negative CV rate
  pvtracking?: boolean; // PV tracking enable
  swtracking?: boolean; // SW tracking enable
}

// Scaling Configuration
interface ScalingConfiguration {
  pv_unscaled_min: number; // MINI
  pv_unscaled_max: number; // MAXI
  pv_engineering_min: number; // MINS
  pv_engineering_max: number; // MAXS
  cv_unscaled_min: number;
  cv_unscaled_max: number;
  cv_engineering_min: number;
  cv_engineering_max: number;
}

// Control Limits
interface ControlLimits {
  output_high_limit: number;
  output_low_limit: number;
  setpoint_high_limit: number;
  setpoint_low_limit: number;
  rate_limit?: number;
}

// Alarm Configuration
interface AlarmConfiguration {
  pv_high_alarm?: number; // PVH
  pv_low_alarm?: number; // PVL
  deviation_high_alarm?: number; // DVP
  deviation_low_alarm?: number; // DVN
  output_high_alarm?: number;
  output_low_alarm?: number;
  alarm_deadband?: number;
  alarm_enabled: boolean;
}

// Controller Options
interface ControllerOptions {
  auto_manual_station?: boolean;
  output_tracking?: boolean;
  setpoint_tracking?: boolean;
  zero_cross_time?: number;
  anti_windup_enabled?: boolean;
  feedforward_enabled?: boolean;
  cascade_enabled?: boolean;
  derivative_on_error?: boolean; // DOE
}

// Performance Metrics
interface PerformanceMetrics {
  performance_score: number;
  oscillation_index: number;
  cv_saturation_percent: number;
  integral_absolute_error?: number;
  settling_time?: number;
  overshoot_percent?: number;
  rise_time?: number;
  last_calculated: Date;
}

// Historical Data Point
interface HistoricalDataPoint {
  timestamp: Date;
  setpoint: number;
  process_value: number;
  control_output: number;
  error: number;
  mode: ControlMode;
}

// Tuning Session Information
interface TuningSession {
  id: string;
  started_at: Date;
  completed_at?: Date;
  method: 'manual' | 'auto' | 'ziegler_nichols' | 'cohen_coon' | 'internal_model_control';
  initial_parameters: PIDParameters | PIDEParameters;
  final_parameters?: PIDParameters | PIDEParameters;
  performance_improvement?: number;
  status: 'in_progress' | 'completed' | 'failed' | 'cancelled';
  notes?: string;
}

// Cascade Configuration
interface CascadeConfiguration {
  is_cascade: boolean;
  cascade_type?: 'master' | 'slave';
  master_loop_id?: string;
  slave_loop_ids?: string[];
  cascade_ratio?: number;
}

// Comprehensive Control Loop Interface
interface EnhancedControlLoop {
  // Identification
  id: string;
  tag_name: string;
  name: string;
  description?: string;

  // Classification
  type: ControlLoopType;
  algorithm_form: AlgorithmForm;
  control_mode: ControlMode;
  control_action: ControlAction;

  // Core Configuration
  process_variable: ProcessVariable;
  setpoint: Setpoint;
  control_output: ControlOutput;

  // PID/PIDE Parameters
  pid_parameters: PIDParameters | PIDEParameters;

  // Configuration
  scaling: ScalingConfiguration;
  limits: ControlLimits;
  alarms: AlarmConfiguration;
  options: ControllerOptions;

  // Status & Performance
  enabled: boolean;
  status: 'running' | 'stopped' | 'error' | 'tuning' | 'manual' | 'cascade';
  scan_time: number; // seconds
  performance_metrics: PerformanceMetrics;

  // Advanced Features
  cascade_config?: CascadeConfiguration;
  tuning_sessions: TuningSession[];

  // Metadata
  created_at: Date;
  updated_at: Date;
  last_tuned?: Date;
  version: string;
  schema_version: string;
}

// Control Loop Summary for Dashboard Cards
interface ControlLoopSummary {
  id: string;
  name: string;
  type: ControlLoopType;
  status: 'running' | 'stopped' | 'error' | 'tuning' | 'manual' | 'cascade';
  setpoint: number;
  process_value: number;
  control_output: number;
  mode: ControlMode;
  performance_score: number;
  alarms_active: number;
  last_updated: Date;
}

// Dashboard Filter Options
interface DashboardFilters {
  status?: ('running' | 'stopped' | 'error' | 'tuning' | 'manual' | 'cascade')[];
  type?: ControlLoopType[];
  performance_threshold?: number;
  search?: string;
  tags?: string[];
}

// Real-time Update Event
interface ControlLoopUpdate {
  loop_id: string;
  timestamp: Date;
  updates: Partial<
    Pick<
      EnhancedControlLoop,
      'process_variable' | 'control_output' | 'status' | 'performance_metrics'
    >
  >;
}

// Tuning Request
interface TuningRequest {
  loop_id: string;
  method: 'manual' | 'auto' | 'ziegler_nichols' | 'cohen_coon' | 'internal_model_control';
  target_performance?: number;
  constraints?: {
    max_overshoot?: number;
    max_settling_time?: number;
    stability_margin?: number;
  };
}

// ===== SECTION 1: Control Loop Tuning Interface Types =====
// Following AI Task Orchestrator TypeScript methodology - Strict typing from start

// Tuning Queue Entry - Core data structure for tuning queue management
interface TuningQueueEntry {
  readonly loopId: string; // Unique identifier for the control loop
  readonly loopName: string; // Display name for the loop
  readonly queID: number; // Position in tuning queue (unique within queue)
  readonly isFocus: boolean; // Whether this loop is currently in focus
  readonly analysisOngoing: boolean; // Whether AI analysis is currently running
  readonly analysisTime?: number; // Duration of analysis in seconds (optional)
  readonly autotuneEnable: boolean; // Whether auto-tune functionality is enabled
  readonly queuedAt: Date; // When the loop was added to the queue
  readonly lastModified: Date; // Last time queue entry was modified
  readonly originalLoopData: ControlLoopSummary; // Reference to original loop data
}

// Tuning Queue Context Actions - Available actions in the context popup
type TuningQueueContextAction =
  | 'change_queue_id'
  | 'set_to_active'
  | 'remove_from_queue'
  | 'start_loop_analysis'
  | 'stop_loop_analysis';

// Tuning Queue Context Option - Individual option in the context popup
interface TuningQueueContextOption {
  readonly action: TuningQueueContextAction;
  readonly label: string;
  readonly description: string;
  readonly icon: string; // Lucide icon name
  readonly enabled: boolean; // Whether option is currently available
  readonly requiresConfirmation: boolean; // Whether action requires user confirmation
  readonly validationRules?: readonly string[]; // Additional validation requirements
}

// Focus Loop Editable Parameters - Parameters that can be edited for the focus loop
interface FocusLoopEditableParameters {
  readonly setpoint: number; // SP - Target process value
  readonly controlOutput: number; // CV - Control variable/output value
  readonly proportionalGain: number; // Kp or Kc - Proportional gain
  readonly integralGain: number; // Ki or Ti - Integral gain/time
  readonly derivativeGain: number; // Kd or Td - Derivative gain/time
  readonly lastUpdated: Date; // When parameters were last modified
  readonly modifiedBy: 'user' | 'ai' | 'auto'; // Source of last modification
}

// Advanced Settings Configuration - Settings accessible through Advanced Settings modal
interface AdvancedSettingsConfiguration {
  readonly autotuneEnable: boolean; // Enable/disable auto-tune functionality
  readonly analysisTime: number; // Default analysis duration in seconds
  readonly tuningAlgorithm: TuningMethod; // Selected tuning algorithm
  readonly safetyLimits: SafetyLimitsConfig; // Safety configuration
  readonly historicalDataRetention: number; // Days to retain historical data
  readonly autoSaveInterval: number; // Auto-save interval in milliseconds
}

// Safety Limits Configuration
interface SafetyLimitsConfig {
  readonly maxSetpointChange: number; // Maximum allowed setpoint change per operation
  readonly maxOutputChange: number; // Maximum allowed output change per operation
  readonly emergencyShutdownThreshold: number; // Threshold for emergency shutdown
  readonly parameterChangeRateLimit: number; // Rate limit for parameter changes
}

// Tuning Method - Available tuning algorithms
type TuningMethod =
  | 'manual'
  | 'ziegler_nichols'
  | 'cohen_coon'
  | 'internal_model_control'
  | 'lambda_tuning'
  | 'pid_autotune';

// Control Loop Mode for Quick Actions - Enhanced with additional modes
type ControlLoopOperatingMode = 'Auto' | 'Manual' | 'Software Manual' | 'Off';

// Tuning Queue State - Complete state management interface
interface TuningQueueState {
  readonly entries: readonly TuningQueueEntry[]; // All entries in the tuning queue
  readonly focusLoopId: string | null; // ID of currently focused loop
  readonly maxQueueSize: number; // Maximum allowed queue size
  readonly nextAvailableQueID: number; // Next available queue ID
  readonly lastUpdated: Date; // When queue was last modified
}

// Tuning Queue Action - State management actions
interface TuningQueueAction {
  readonly type: TuningQueueActionType;
  readonly payload: Record<string, unknown>;
  readonly timestamp: Date;
  readonly userId?: string; // Optional user ID for audit trail
}

// Tuning Queue Action Types
type TuningQueueActionType =
  | 'ADD_TO_QUEUE'
  | 'REMOVE_FROM_QUEUE'
  | 'UPDATE_QUEUE_ID'
  | 'SET_FOCUS_LOOP'
  | 'START_ANALYSIS'
  | 'STOP_ANALYSIS'
  | 'UPDATE_PARAMETERS'
  | 'CLEAR_QUEUE'
  | 'REORDER_QUEUE';

// Keyboard Navigation State - Navigation management
interface KeyboardNavigationState {
  readonly isNavigationActive: boolean; // Whether keyboard navigation is enabled
  readonly currentIndex: number; // Current navigation index
  readonly totalEntries: number; // Total number of navigable entries
  readonly navigationMode: 'queue' | 'parameters'; // Current navigation context
}

// Parameter Validation Result - Validation feedback for parameter changes
interface ParameterValidationResult {
  readonly isValid: boolean; // Whether validation passed
  readonly errors: readonly string[]; // Validation error messages
  readonly warnings: readonly string[]; // Validation warnings
  readonly fieldErrors: Record<string, string>; // Field-specific error messages
  readonly suggestedValues?: Partial<FocusLoopEditableParameters>; // AI-suggested corrections
}

// Tuning Interface Event - Events for real-time updates
interface TuningInterfaceEvent {
  readonly type: TuningInterfaceEventType;
  readonly loopId: string;
  readonly timestamp: Date;
  readonly data: Record<string, unknown>;
  readonly source: 'user' | 'ai' | 'websocket' | 'system';
}

// Tuning Interface Event Types
type TuningInterfaceEventType =
  | 'PARAMETER_CHANGED'
  | 'QUEUE_UPDATED'
  | 'FOCUS_CHANGED'
  | 'ANALYSIS_STARTED'
  | 'ANALYSIS_COMPLETED'
  | 'MODE_CHANGED'
  | 'ERROR_OCCURRED';

// Export all types
export type {
  AdvancedSettingsConfiguration,
  AlarmConfiguration,
  AlgorithmForm,
  CascadeConfiguration,
  ControlAction,
  ControlLimits,
  ControlLoopOperatingMode,
  ControlLoopSummary,
  ControlLoopType,
  ControlLoopUpdate,
  ControlMode,
  ControlOutput,
  ControllerOptions,
  DashboardFilters,
  EngineeringUnits,
  EnhancedControlLoop,
  FocusLoopEditableParameters,
  HistoricalDataPoint,
  KeyboardNavigationState,
  PIDEParameters,
  PIDParameters,
  ParameterValidationResult,
  PerformanceMetrics,
  ProcessVariable,
  SafetyLimitsConfig,
  ScalingConfiguration,
  Setpoint,
  TuningInterfaceEvent,
  TuningInterfaceEventType,
  TuningMethod,
  TuningQueueAction,
  TuningQueueActionType,
  TuningQueueContextAction,
  TuningQueueContextOption,
  // Section 1: Control Loop Tuning Interface Types
  TuningQueueEntry,
  TuningQueueState,
  TuningRequest,
  TuningSession,
};
