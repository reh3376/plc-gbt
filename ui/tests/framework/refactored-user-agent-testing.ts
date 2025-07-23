/**
 * Refactored User Agent Testing Framework - Phase 31
 * 
 * Simplified framework using modular components.
 * Reduced from 802 lines to ~150 lines (81% reduction).
 * 
 * @author PLC-GBT Development Team
 * @version 2.0.0-refactored
 * @since Phase 31.1
 */

import { EventEmitter } from 'events';
import {
  UserAgent,
  TestEnvironment,
  TestScenario,
  UserAgentTestSession,
  TestRecommendation,
  SubPhaseValidationResult,
  NetworkCondition,
  DeviceType
} from './types';
import {
  SessionExecutor,
  ScenarioExecutor,
  RecordingManager
} from './executors';
import {
  ScenarioFactory,
  UserAgentRegistry
} from './utils';

// ==================== Refactored Framework Implementation ====================

export class UserAgentTestingFramework extends EventEmitter {
  private sessions: Map<string, UserAgentTestSession> = new Map();
  private scenarios: Map<string, TestScenario> = new Map();
  
  // Extracted components
  private sessionExecutor: SessionExecutor;
  private scenarioExecutor: ScenarioExecutor;
  private recordingManager: RecordingManager;
  private scenarioFactory: ScenarioFactory;
  private userAgentRegistry: UserAgentRegistry;
  
  constructor() {
    super();
    this.initializeComponents();
    this.initializeFramework();
  }
  
  // ==================== Public API ====================
  
  async createTestSession(
    testId: string,
    userAgent: UserAgent,
    environment: TestEnvironment,
    scenarioIds: string[]
  ): Promise<UserAgentTestSession> {
    const scenarios = scenarioIds.map(id => this.scenarios.get(id)).filter(Boolean) as TestScenario[];
    const session = await this.sessionExecutor.createSession(testId, userAgent, environment, scenarios);
    
    this.sessions.set(session.sessionId, session);
    return session;
  }
  
  async startTestSession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }
    
    await this.validateTestEnvironment(session.environment);
    await this.recordingManager.startRecording(sessionId);
    
    this.emit('sessionStarted', session);
  }
  
  async executeScenario(sessionId: string, scenarioId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    const scenario = this.scenarios.get(scenarioId);
    
    if (!session || !scenario) {
      throw new Error('Session or scenario not found');
    }
    
    const result = await this.scenarioExecutor.executeScenario(sessionId, scenario);
    
    // Update session with results
    const scenarioIndex = session.scenarios.findIndex(s => s.scenarioId === scenarioId);
    if (scenarioIndex >= 0) {
      session.scenarios[scenarioIndex] = result;
    }
  }
  
  async completeTestSession(sessionId: string): Promise<UserAgentTestSession> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }
    
    await this.recordingManager.stopRecording(sessionId);
    const finalizedSession = await this.sessionExecutor.finalizeSession(session);
    
    this.sessions.set(sessionId, finalizedSession);
    return finalizedSession;
  }
  
  async validateSubPhase(subPhase: string): Promise<SubPhaseValidationResult> {
    const subPhaseSessions = Array.from(this.sessions.values())
      .filter(session => session.scenarios.some(s => s.scenarioId.includes(subPhase)));
    
    const totalSessions = subPhaseSessions.length;
    const approvedSessions = subPhaseSessions.filter(s => s.approved).length;
    const averageScore = subPhaseSessions.reduce((sum, s) => sum + s.overallScore, 0) / totalSessions;
    const criticalIssues = subPhaseSessions.reduce((sum, s) => 
      sum + s.issues.filter(i => i.severity === 'critical').length, 0);
    const blockingIssues = subPhaseSessions.reduce((sum, s) => 
      sum + s.issues.filter(i => i.blocking).length, 0);
    
    const approved = approvedSessions >= Math.ceil(totalSessions * 0.8) && criticalIssues === 0;
    
    return {
      subPhase,
      totalSessions,
      approvedSessions,
      approvalRate: approvedSessions / totalSessions,
      averageScore,
      criticalIssues,
      blockingIssues,
      approved,
      recommendation: approved ? 'Proceed to next sub-phase' : 'Address critical issues before proceeding',
      sessions: subPhaseSessions
    };
  }
  
  // ==================== Registry Management ====================
  
  registerUserAgent(userAgent: UserAgent): void {
    this.userAgentRegistry.registerUserAgent(userAgent);
  }
  
  registerScenario(scenario: TestScenario): void {
    this.scenarios.set(scenario.id, scenario);
  }
  
  getAvailableUserAgents(): UserAgent[] {
    return this.userAgentRegistry.getAvailableUserAgents();
  }
  
  getRequiredUserRoles(subPhase: string) {
    return this.userAgentRegistry.getRequiredUserRoles(subPhase);
  }
  
  // ==================== Initialization ====================
  
  private initializeComponents(): void {
    this.sessionExecutor = new SessionExecutor();
    this.scenarioExecutor = new ScenarioExecutor();
    this.recordingManager = new RecordingManager();
    this.scenarioFactory = new ScenarioFactory();
    this.userAgentRegistry = new UserAgentRegistry();
    
    // Forward events from components
    this.sessionExecutor.on('sessionCreated', (session) => this.emit('sessionCreated', session));
    this.sessionExecutor.on('sessionCompleted', (session) => this.emit('sessionCompleted', session));
    this.scenarioExecutor.on('scenarioCompleted', (sessionId, result) => 
      this.emit('scenarioCompleted', sessionId, result));
  }
  
  private initializeFramework(): void {
    this.registerDefaultScenarios();
  }
  
  private registerDefaultScenarios(): void {
    // Register scenarios using the factory
    this.registerScenario(this.scenarioFactory.createThemeWorkbenchScenario());
    this.registerScenario(this.scenarioFactory.createFileExplorerScenario());
  }
  
  private async validateTestEnvironment(environment: TestEnvironment): Promise<void> {
    // Simplified environment validation
    if (!environment.url || !environment.browser) {
      throw new Error('Invalid test environment configuration');
    }
  }
  
  private getDefaultTestEnvironment(): TestEnvironment {
    return {
      url: 'http://localhost:3001',
      browser: 'Chrome',
      browserVersion: '120.0',
      os: 'macOS',
      screenResolution: '1920x1080',
      networkCondition: NetworkCondition.FAST,
      deviceType: DeviceType.DESKTOP
    };
  }
}

// ==================== Export Framework ====================

export default UserAgentTestingFramework;

// Re-export types for convenience
export * from './types';
export * from './executors';
export * from './utils'; 