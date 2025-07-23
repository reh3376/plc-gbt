/**
 * Session Management Types
 * Phase 31 - UI Testing Framework
 */

import { UserAgent } from './user-agent-types';
import { TestEnvironment } from './environment-types';
import { TestScenario } from './test-scenario-types';

export interface SessionConfig {
  testId: string;
  userAgent: UserAgent;
  environment: TestEnvironment;
  scenarioIds: string[];
  recordingEnabled: boolean;
  timeoutMinutes: number;
}

export interface SessionMetrics {
  totalDuration: number;
  averageStepTime: number;
  successRate: number;
  errorRate: number;
  retryCount: number;
} 