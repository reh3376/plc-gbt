/**
 * Connection Configuration Types
 * Shared across industrial protocol nodes
 */

export interface OPCUAConnection {
  serverUrl: string;
  securityMode: SecurityMode;
  securityPolicy: SecurityPolicy;
  userName?: string;
  password?: string;
  certificatePath?: string;
  privateKeyPath?: string;
  timeout: number;
}

export enum SecurityMode {
  NONE = 'None',
  SIGN = 'Sign',
  SIGN_AND_ENCRYPT = 'SignAndEncrypt'
}

export enum SecurityPolicy {
  NONE = 'None',
  BASIC128RSA15 = 'Basic128Rsa15',
  BASIC256 = 'Basic256',
  BASIC256SHA256 = 'Basic256Sha256'
}

export interface LLMConnection {
  modelId: string;
  temperature: number;
  maxTokens: number;
  timeout: number;
  apiKey?: string;
} 