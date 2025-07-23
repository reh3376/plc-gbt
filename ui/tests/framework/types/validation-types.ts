/**
 * Validation and Issue Types
 * Phase 31 - UI Testing Framework
 */

import { TestEnvironment } from './environment-types';

export interface Issue {
  id: string;
  severity: IssueSeverity;
  category: IssueCategory;
  title: string;
  description: string;
  reproductionSteps: string[];
  expectedBehavior: string;
  actualBehavior: string;
  userAgent: string;
  environment: TestEnvironment;
  screenshot?: string;
  video?: string;
  priority: IssuePriority;
  blocking: boolean;
}

export enum IssueSeverity {
  CRITICAL = 'critical',   // Prevents task completion
  HIGH = 'high',          // Major usability issue
  MEDIUM = 'medium',      // Minor usability issue
  LOW = 'low'            // Cosmetic or enhancement
}

export enum IssueCategory {
  FUNCTIONALITY = 'functionality',
  USABILITY = 'usability',
  PERFORMANCE = 'performance',
  ACCESSIBILITY = 'accessibility',
  SECURITY = 'security',
  DESIGN = 'design'
}

export enum IssuePriority {
  P0 = 'p0', // Must fix before proceeding
  P1 = 'p1', // Should fix before proceeding
  P2 = 'p2', // Can fix in current iteration
  P3 = 'p3'  // Can defer to future iteration
} 