/**
 * Test Environment Types and Interfaces
 * Phase 31 - UI Testing Framework
 */

export interface TestEnvironment {
  url: string;
  browser: string;
  browserVersion: string;
  os: string;
  screenResolution: string;
  networkCondition: NetworkCondition;
  deviceType: DeviceType;
}

export enum NetworkCondition {
  FAST = 'fast',      // > 10 Mbps
  GOOD = 'good',      // 1-10 Mbps
  SLOW = 'slow',      // 0.1-1 Mbps
  OFFLINE = 'offline'
}

export enum DeviceType {
  DESKTOP = 'desktop',
  TABLET = 'tablet',
  MOBILE = 'mobile',
  INDUSTRIAL_TERMINAL = 'industrial_terminal'
} 