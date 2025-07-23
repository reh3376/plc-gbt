/**
 * Score Calculation Utilities
 * Phase 31 - UI Testing Framework
 */

import { TestStepResult } from '../types';

export class ScoreCalculator {
  
  calculateUsabilityScore(stepResults: TestStepResult[], errorCount: number): number {
    const totalSteps = stepResults.length;
    const successfulSteps = stepResults.filter(sr => sr.success).length;
    const baseScore = (successfulSteps / totalSteps) * 10;
    const errorPenalty = errorCount * 0.5;
    return Math.max(0, baseScore - errorPenalty);
  }
  
  calculateTaskCompletionRate(stepResults: TestStepResult[]): number {
    const completedSteps = stepResults.filter(sr => sr.completed).length;
    return completedSteps / stepResults.length;
  }
  
  calculateAverageStepTime(stepResults: TestStepResult[]): number {
    const totalTime = stepResults.reduce((sum, sr) => sum + sr.duration, 0);
    return totalTime / stepResults.length;
  }
  
  calculateEfficiencyScore(stepResults: TestStepResult[]): number {
    const avgAttempts = stepResults.reduce((sum, sr) => sum + sr.attempts, 0) / stepResults.length;
    // Lower attempts = higher efficiency
    return Math.max(0, 10 - (avgAttempts - 1) * 2);
  }
} 