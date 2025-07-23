/**
 * Test Scenario Types and Interfaces
 * Phase 31 - UI Testing Framework
 */

export interface ValidationCheck {
  type: ValidationType;
  target: string;
  expected: string | number | boolean;
  timeout: number;
}

export enum ValidationType {
  ELEMENT_VISIBLE = 'element_visible',
  ELEMENT_CLICKABLE = 'element_clickable',
  TEXT_CONTENT = 'text_content',
  ATTRIBUTE_VALUE = 'attribute_value',
  RESPONSE_TIME = 'response_time',
  ERROR_MESSAGE = 'error_message',
  DATA_ACCURACY = 'data_accuracy'
}

export interface TestScenario {
  id: string;
  subPhase: string;
  title: string;
  description: string;
  prerequisiteKnowledge: string[];
  estimatedDuration: number; // minutes
  criticalPath: boolean;
  steps: TestStep[];
  expectedOutcome: string;
  successCriteria: string[];
  failureCriteria: string[];
  accessibility?: AccessibilityRequirements;
}

export interface TestStep {
  stepNumber: number;
  instruction: string;
  expectedBehavior: string;
  screenshot?: boolean;
  videoCapture?: boolean;
  interactionType: InteractionType;
  validation: ValidationCheck[];
}

export enum InteractionType {
  CLICK = 'click',
  TYPE = 'type',
  DRAG_DROP = 'drag_drop',
  KEYBOARD_SHORTCUT = 'keyboard_shortcut',
  VOICE_COMMAND = 'voice_command',
  SCROLL = 'scroll',
  UPLOAD = 'upload',
  NAVIGATE = 'navigate'
}

export interface AccessibilityRequirements {
  screenReader: boolean;
  keyboardNavigation: boolean;
  highContrast: boolean;
  fontSize: number;
  colorBlindness: string[];
} 