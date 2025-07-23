/**
 * Test Result and Session Types
 * Phase 31 - UI Testing Framework
 */

import { UserAgent, UserFeedback } from './user-agent-types';
import { TestEnvironment } from './environment-types';
import { Issue } from './validation-types';

export interface TestScenarioResult {
  scenarioId: string;
  completed: boolean;
  duration: number;
  stepResults: TestStepResult[];
  usabilityScore: number; // 1-10
  taskCompletion: boolean;
  errorCount: number;
  feedback: string;
  issues: Issue[];
}

export interface TestStepResult {
  stepNumber: number;
  completed: boolean;
  duration: number;
  attempts: number;
  success: boolean;
  feedback: string;
  screenshot?: string;
  videoSegment?: string;
  issues: Issue[];
}

export enum TestRecommendation {
  APPROVED_PROCEED = 'approved_proceed',
  APPROVED_WITH_MINOR_FIXES = 'approved_with_minor_fixes',
  REJECTED_MAJOR_ISSUES = 'rejected_major_issues',
  REJECTED_CRITICAL_ISSUES = 'rejected_critical_issues'
}

export interface UserAgentTestSession {
  sessionId: string;
  testId: string;
  userAgent: UserAgent;
  startTime: Date;
  endTime?: Date;
  environment: TestEnvironment;
  scenarios: TestScenarioResult[];
  overallScore: number;
  feedback: UserFeedback;
  issues: Issue[];
  recommendation: TestRecommendation;
  approved: boolean;
}

export interface SubPhaseValidationResult {
  subPhase: string;
  totalSessions: number;
  approvedSessions: number;
  approvalRate: number;
  averageScore: number;
  criticalIssues: number;
  blockingIssues: number;
  approved: boolean;
  recommendation: string;
  sessions: UserAgentTestSession[];
} 