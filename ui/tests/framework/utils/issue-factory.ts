/**
 * Issue Factory
 * Phase 31 - UI Testing Framework
 */

import {
  Issue,
  TestStep,
  IssueSeverity,
  IssueCategory,
  IssuePriority,
  TestEnvironment
} from '../types';

export class IssueFactory {
  
  createFromValidationError(error: Error, step: TestStep): Issue {
    return {
      id: this.generateIssueId(),
      severity: IssueSeverity.HIGH,
      category: IssueCategory.FUNCTIONALITY,
      title: `Validation failed for step ${step.stepNumber}`,
      description: error.message,
      reproductionSteps: [step.instruction],
      expectedBehavior: step.expectedBehavior,
      actualBehavior: error.message,
      userAgent: '',
      environment: {} as TestEnvironment,
      priority: IssuePriority.P1,
      blocking: true
    };
  }
  
  createFromExecutionError(error: Error, step: TestStep): Issue {
    return {
      id: this.generateIssueId(),
      severity: IssueSeverity.CRITICAL,
      category: IssueCategory.FUNCTIONALITY,
      title: `Step execution failed: ${step.stepNumber}`,
      description: error.message,
      reproductionSteps: [step.instruction],
      expectedBehavior: step.expectedBehavior,
      actualBehavior: error.message,
      userAgent: '',
      environment: {} as TestEnvironment,
      priority: IssuePriority.P0,
      blocking: true
    };
  }
  
  createUsabilityIssue(
    title: string,
    description: string,
    step: TestStep,
    severity: IssueSeverity = IssueSeverity.MEDIUM
  ): Issue {
    return {
      id: this.generateIssueId(),
      severity,
      category: IssueCategory.USABILITY,
      title,
      description,
      reproductionSteps: [step.instruction],
      expectedBehavior: step.expectedBehavior,
      actualBehavior: description,
      userAgent: '',
      environment: {} as TestEnvironment,
      priority: this.getPriorityFromSeverity(severity),
      blocking: severity === IssueSeverity.CRITICAL
    };
  }
  
  private generateIssueId(): string {
    return `issue-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
  }
  
  private getPriorityFromSeverity(severity: IssueSeverity): IssuePriority {
    switch (severity) {
      case IssueSeverity.CRITICAL:
        return IssuePriority.P0;
      case IssueSeverity.HIGH:
        return IssuePriority.P1;
      case IssueSeverity.MEDIUM:
        return IssuePriority.P2;
      case IssueSeverity.LOW:
        return IssuePriority.P3;
      default:
        return IssuePriority.P2;
    }
  }
} 