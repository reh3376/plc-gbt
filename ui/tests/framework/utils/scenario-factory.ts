/**
 * Scenario Factory
 * Phase 31 - UI Testing Framework
 */

import {
  TestScenario,
  TestStep,
  InteractionType,
  ValidationType
} from '../types';

export class ScenarioFactory {
  
  createThemeWorkbenchScenario(): TestScenario {
    return {
      id: 'scenario-31.1-theia-workbench',
      subPhase: 'Phase 31.1',
      title: 'Theia Workbench Basic Functionality',
      description: 'Test basic Theia workbench functionality and user interface',
      prerequisiteKnowledge: ['Basic IDE usage', 'File management'],
      estimatedDuration: 30,
      criticalPath: true,
      steps: [
        this.createStep(1, 'Launch Theia workbench', 'Workbench loads successfully', InteractionType.NAVIGATE),
        this.createStep(2, 'Open file explorer', 'File explorer panel opens', InteractionType.CLICK),
        this.createStep(3, 'Create new file', 'New file is created and opened', InteractionType.CLICK),
        this.createStep(4, 'Save file', 'File is saved successfully', InteractionType.KEYBOARD_SHORTCUT)
      ],
      expectedOutcome: 'User can perform basic file operations in Theia workbench',
      successCriteria: [
        'All UI elements load correctly',
        'File operations complete without errors',
        'Response time < 2 seconds for each action'
      ],
      failureCriteria: [
        'UI elements fail to load',
        'File operations produce errors',
        'Response time > 5 seconds'
      ]
    };
  }
  
  createFileExplorerScenario(): TestScenario {
    return {
      id: 'scenario-31.2-file-explorer',
      subPhase: 'Phase 31.2',
      title: 'PLC File Explorer Extension',
      description: 'Test PLC-specific file explorer functionality',
      prerequisiteKnowledge: ['PLC file formats', 'Theia extension usage'],
      estimatedDuration: 45,
      criticalPath: true,
      steps: [
        this.createStep(1, 'Open PLC project', 'PLC project loads in explorer', InteractionType.CLICK),
        this.createStep(2, 'Navigate PLC file structure', 'File tree shows PLC organization', InteractionType.CLICK),
        this.createStep(3, 'Open ladder logic file', 'Ladder logic displays correctly', InteractionType.CLICK),
        this.createStep(4, 'Validate syntax highlighting', 'PLC syntax is highlighted', InteractionType.TYPE)
      ],
      expectedOutcome: 'PLC file explorer provides specialized PLC file management',
      successCriteria: [
        'PLC file types recognized',
        'Syntax highlighting functional',
        'File operations preserve PLC structure'
      ],
      failureCriteria: [
        'PLC files not recognized',
        'No syntax highlighting',
        'File corruption on operations'
      ]
    };
  }
  
  private createStep(
    stepNumber: number,
    instruction: string,
    expectedBehavior: string,
    interactionType: InteractionType
  ): TestStep {
    return {
      stepNumber,
      instruction,
      expectedBehavior,
      screenshot: true,
      videoCapture: stepNumber === 1, // Capture video for first step of each scenario
      interactionType,
      validation: [
        {
          type: ValidationType.ELEMENT_VISIBLE,
          target: 'main-content',
          expected: true,
          timeout: 5000
        },
        {
          type: ValidationType.RESPONSE_TIME,
          target: '',
          expected: 2000,
          timeout: 5000
        }
      ]
    };
  }
} 