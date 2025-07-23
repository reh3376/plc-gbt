/**
 * Session Execution Logic
 * Phase 31 - UI Testing Framework
 */

import { EventEmitter } from 'events';
import {
  UserAgent,
  TestEnvironment,
  TestScenario,
  UserAgentTestSession,
  TestRecommendation,
  UserFeedback,
  TestScenarioResult
} from '../types';

export class SessionExecutor extends EventEmitter {
  
  async createSession(
    testId: string,
    userAgent: UserAgent,
    environment: TestEnvironment,
    scenarios: TestScenario[]
  ): Promise<UserAgentTestSession> {
    const sessionId = this.generateSessionId();
    
    const session: UserAgentTestSession = {
      sessionId,
      testId,
      userAgent,
      startTime: new Date(),
      environment,
      scenarios: scenarios.map(scenario => ({
        scenarioId: scenario.id,
        completed: false,
        duration: 0,
        stepResults: [],
        usabilityScore: 0,
        taskCompletion: false,
        errorCount: 0,
        feedback: '',
        issues: []
      })),
      overallScore: 0,
      feedback: this.getDefaultFeedback(),
      issues: [],
      recommendation: TestRecommendation.REJECTED_CRITICAL_ISSUES,
      approved: false
    };
    
    this.emit('sessionCreated', session);
    return session;
  }
  
  async finalizeSession(session: UserAgentTestSession): Promise<UserAgentTestSession> {
    session.endTime = new Date();
    session.overallScore = this.calculateOverallScore(session);
    session.recommendation = this.generateRecommendation(session);
    session.approved = this.isSessionApproved(session);
    
    this.emit('sessionCompleted', session);
    return session;
  }
  
  private generateSessionId(): string {
    return `uat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private getDefaultFeedback(): UserFeedback {
    return {
      overallSatisfaction: 0,
      easeOfUse: 0,
      visualDesign: 0,
      performance: 0,
      functionality: 0,
      wouldRecommend: false,
      mostLiked: [],
      mostDisliked: [],
      suggestions: [],
      additionalComments: ''
    };
  }
  
  private calculateOverallScore(session: UserAgentTestSession): number {
    const scenarioScores = session.scenarios.map(s => s.usabilityScore);
    const averageScore = scenarioScores.reduce((sum, score) => sum + score, 0) / scenarioScores.length;
    
    // Factor in user feedback
    const feedbackWeight = 0.3;
    const feedbackScore = (
      session.feedback.overallSatisfaction +
      session.feedback.easeOfUse +
      session.feedback.functionality
    ) / 3;
    
    return (averageScore * (1 - feedbackWeight)) + (feedbackScore * feedbackWeight);
  }
  
  private generateRecommendation(session: UserAgentTestSession): TestRecommendation {
    const criticalIssues = session.issues.filter(i => i.severity === 'critical').length;
    const blockingIssues = session.issues.filter(i => i.blocking).length;
    const overallScore = session.overallScore;
    
    if (criticalIssues > 0 || blockingIssues > 0) {
      return TestRecommendation.REJECTED_CRITICAL_ISSUES;
    }
    
    if (overallScore < 6) {
      return TestRecommendation.REJECTED_MAJOR_ISSUES;
    }
    
    if (overallScore < 8) {
      return TestRecommendation.APPROVED_WITH_MINOR_FIXES;
    }
    
    return TestRecommendation.APPROVED_PROCEED;
  }
  
  private isSessionApproved(session: UserAgentTestSession): boolean {
    return session.recommendation === TestRecommendation.APPROVED_PROCEED ||
           session.recommendation === TestRecommendation.APPROVED_WITH_MINOR_FIXES;
  }
} 