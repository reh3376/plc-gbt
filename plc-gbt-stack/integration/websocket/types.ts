/**
 * WebSocket Type Definitions for PLC-GBT Real-time Communication
 * Phase 32.1 - Multi-System Integration
 *
 * CRITICAL: Strict TypeScript typing enforced - NO any types allowed
 * Following AI Task Orchestrator TypeScript Guide standards
 */

export enum WebSocketMessageType {
  // Connection lifecycle
  CONNECTION_INIT = 'connection_init',
  CONNECTION_ACK = 'connection_ack',
  CONNECTION_ERROR = 'connection_error',
  CONNECTION_CLOSE = 'connection_close',

  // PLC data streams
  PLC_DATA_SUBSCRIBE = 'plc_data_subscribe',
  PLC_DATA_UNSUBSCRIBE = 'plc_data_unsubscribe',
  PLC_DATA_UPDATE = 'plc_data_update',

  // Control loop monitoring
  CONTROL_LOOP_SUBSCRIBE = 'control_loop_subscribe',
  CONTROL_LOOP_UNSUBSCRIBE = 'control_loop_unsubscribe',
  CONTROL_LOOP_UPDATE = 'control_loop_update',

  // System events
  SYSTEM_EVENT = 'system_event',
  SYSTEM_ALERT = 'system_alert',
  SYSTEM_STATUS = 'system_status',

  // Commands
  EXECUTE_COMMAND = 'execute_command',
  COMMAND_RESULT = 'command_result',
  COMMAND_ERROR = 'command_error',
}

export enum SystemEventType {
  PLC_CONNECTED = 'plc_connected',
  PLC_DISCONNECTED = 'plc_disconnected',
  CONTROL_LOOP_STARTED = 'control_loop_started',
  CONTROL_LOOP_STOPPED = 'control_loop_stopped',
  ALARM_TRIGGERED = 'alarm_triggered',
  ALARM_CLEARED = 'alarm_cleared',
  CONFIGURATION_CHANGED = 'configuration_changed',
}

export enum AlertSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

export interface PLCDataPoint {
  timestamp: number;
  tagName: string;
  value: number | boolean | string;
  quality: 'good' | 'bad' | 'uncertain';
  unit?: string;
}

export interface ControlLoopData {
  loopId: string;
  name: string;
  setpoint: number;
  processVariable: number;
  controlVariable: number;
  mode: 'auto' | 'manual' | 'cascade';
  status: 'running' | 'stopped' | 'fault';
  performance: {
    overshoot: number;
    settlingTime: number;
    steadyStateError: number;
  };
}

export interface SystemAlert {
  id: string;
  timestamp: number;
  severity: AlertSeverity;
  source: string;
  message: string;
  details?: Record<string, unknown>;
  acknowledged: boolean;
}

export interface WebSocketMessage<T = unknown> {
  id: string;
  type: WebSocketMessageType;
  timestamp: number;
  payload: T;
}

export interface ConnectionConfig {
  clientId: string;
  authToken?: string;
  subscriptions?: string[];
  heartbeatInterval?: number;
}

export interface SubscriptionRequest {
  topics: string[];
  filters?: Record<string, unknown>;
  throttleMs?: number;
}

export interface CommandRequest {
  command: string;
  parameters: Record<string, unknown>;
  timeout?: number;
}

export interface CommandResult {
  success: boolean;
  result?: unknown;
  error?: string;
  executionTime: number;
}

// Type guards for runtime validation
export function isPLCDataPoint(data: unknown): data is PLCDataPoint {
  return (
    typeof data === 'object' &&
    data !== null &&
    'timestamp' in data &&
    'tagName' in data &&
    'value' in data &&
    'quality' in data
  );
}

export function isControlLoopData(data: unknown): data is ControlLoopData {
  return (
    typeof data === 'object' &&
    data !== null &&
    'loopId' in data &&
    'name' in data &&
    'setpoint' in data &&
    'processVariable' in data
  );
}

export function isSystemAlert(data: unknown): data is SystemAlert {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'severity' in data &&
    'message' in data
  );
}
