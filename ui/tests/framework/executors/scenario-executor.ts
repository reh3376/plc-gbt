/**
 * Scenario Execution Logic
 * Phase 31 - UI Testing Framework
 */

import { EventEmitter } from 'events';
import {
  TestScenario,
  TestScenarioResult,
  TestStepResult
} from '../types';
import { StepExecutor } from './step-executor';
import { ScoreCalculator } from '../utils/score-calculator';

export class ScenarioExecutor extends EventEmitter {
  private stepExecutor: StepExecutor;
  private scoreCalculator: ScoreCalculator;
  
  constructor() {
    super();
    this.stepExecutor = new StepExecutor();
    this.scoreCalculator = new ScoreCalculator();
  }
  
  async executeScenario(
    sessionId: string,
    scenario: TestScenario
  ): Promise<TestScenarioResult> {
    const startTime = Date.now();
    const stepResults: TestStepResult[] = [];
    let errorCount = 0;
    let taskCompletion = true;
    
    this.emit('scenarioStarted', sessionId, scenario.id);
    
    // Execute each step
    for (const step of scenario.steps) {
      const stepResult = await this.stepExecutor.executeStep(sessionId, step);
      stepResults.push(stepResult);
      
      if (!stepResult.success) {
        errorCount++;
        if (scenario.criticalPath) {
          taskCompletion = false;
          break;
        }
      }
    }
    
    const duration = Date.now() - startTime;
    const usabilityScore = this.scoreCalculator.calculateUsabilityScore(stepResults, errorCount);
    
    const result: TestScenarioResult = {
      scenarioId: scenario.id,
      completed: true,
      duration,
      stepResults,
      usabilityScore,
      taskCompletion,
      errorCount,
      feedback: '',
      issues: stepResults.flatMap(sr => sr.issues)
    };
    
    this.emit('scenarioCompleted', sessionId, result);
    return result;
  }
} 