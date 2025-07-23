/**
 * N8N Node Operation Types
 * Shared across multiple node implementations
 */

export enum LLMOperations {
  CONTROL_ANALYSIS = 'control_analysis',
  PID_TUNING = 'pid_tuning',
  SAFETY_ASSESSMENT = 'safety_assessment',
  PROCESS_OPTIMIZATION = 'process_optimization',
  FAULT_DIAGNOSIS = 'fault_diagnosis',
  CUSTOM_QUERY = 'custom_query'
}

export enum OPCUAOperations {
  READ = 'read',
  WRITE = 'write',
  BROWSE = 'browse',
  SUBSCRIBE = 'subscribe',
  METHOD = 'method',
  INFO = 'info'
}

export enum MemoryOperations {
  QUERY = 'query',
  SEARCH = 'search',
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  BACKUP = 'backup'
}

export interface OperationConfig {
  name: string;
  value: string;
  description: string;
} 