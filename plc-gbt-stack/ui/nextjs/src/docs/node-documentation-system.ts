#!/usr/bin/env tsx

/**
 * 🏗️ Node Documentation System - AI Task Orchestrator TypeScript Implementation
 *
 * Compliance Requirements:
 * - Zero `any` types - strict TypeScript throughout
 * - Template-driven documentation generation
 * - OpenAPI Schema MCP integration for validation
 * - Comprehensive parameter coverage for all industrial nodes
 * - Production-ready documentation infrastructure
 */

export interface NodeCategory {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly iconClass: string;
  readonly templateExtensions: readonly string[];
}

export interface ParameterDefinition {
  readonly name: string;
  readonly type: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'enum';
  readonly required: boolean;
  readonly defaultValue: unknown;
  readonly description: string;
  readonly validation?: ParameterValidation;
  readonly enumValues?: readonly string[];
  readonly range?: {
    readonly min: number;
    readonly max: number;
    readonly step?: number;
  };
  readonly units?: string;
  readonly examples?: readonly string[];
}

export interface ParameterValidation {
  readonly pattern?: string;
  readonly minLength?: number;
  readonly maxLength?: number;
  readonly customRules?: readonly string[];
}

export interface ExampleConfiguration {
  readonly title: string;
  readonly description: string;
  readonly useCase: string;
  readonly configuration: Record<string, unknown>;
  readonly expectedOutput?: string;
  readonly notes?: readonly string[];
}

export interface ConnectionSpecification {
  readonly inputHandles: readonly HandleDefinition[];
  readonly outputHandles: readonly HandleDefinition[];
  readonly protocols?: readonly string[];
  readonly connectionTests?: readonly ConnectionTest[];
}

export interface HandleDefinition {
  readonly id: string;
  readonly label: string;
  readonly dataType: string;
  readonly required: boolean;
  readonly description: string;
}

export interface ConnectionTest {
  readonly name: string;
  readonly description: string;
  readonly procedure: readonly string[];
  readonly expectedResult: string;
  readonly troubleshooting: readonly string[];
}

export interface ValidationRule {
  readonly id: string;
  readonly severity: 'error' | 'warning' | 'info';
  readonly condition: string;
  readonly message: string;
  readonly suggestion?: string;
}

export interface NodeDocumentationSpec {
  readonly nodeType: string;
  readonly category: NodeCategory;
  readonly title: string;
  readonly description: string;
  readonly version: string;
  readonly lastUpdated: string;

  // Core configuration
  readonly parameters: readonly ParameterDefinition[];
  readonly examples: readonly ExampleConfiguration[];
  readonly connections: ConnectionSpecification;
  readonly validation: readonly ValidationRule[];

  // Documentation content
  readonly overview: NodeOverviewSection;
  readonly configurationGuide: ConfigurationGuideSection;
  readonly troubleshooting: TroubleshootingSection;
  readonly relatedNodes: readonly string[];
  readonly externalResources: readonly ExternalResource[];

  // Template metadata
  readonly templateCategory: string;
  readonly customSections?: readonly CustomDocSection[];
}

export interface NodeOverviewSection {
  readonly purpose: string;
  readonly keyFeatures: readonly string[];
  readonly useCases: readonly string[];
  readonly whenToUse: readonly string[];
  readonly industrialApplications?: readonly string[];
}

export interface ConfigurationGuideSection {
  readonly quickStart: readonly string[];
  readonly detailedSteps: readonly ConfigurationStep[];
  readonly bestPractices: readonly string[];
  readonly commonMistakes: readonly string[];
}

export interface ConfigurationStep {
  readonly step: number;
  readonly title: string;
  readonly description: string;
  readonly parameters: readonly string[];
  readonly screenshots?: readonly string[];
  readonly codeExamples?: readonly string[];
}

export interface TroubleshootingSection {
  readonly commonIssues: readonly TroubleshootingIssue[];
  readonly errorCodes: readonly ErrorCode[];
  readonly diagnosticProcedures: readonly string[];
  readonly supportContacts?: readonly string[];
}

export interface TroubleshootingIssue {
  readonly issue: string;
  readonly symptoms: readonly string[];
  readonly causes: readonly string[];
  readonly solutions: readonly string[];
  readonly prevention?: readonly string[];
}

export interface ErrorCode {
  readonly code: string;
  readonly message: string;
  readonly severity: 'critical' | 'error' | 'warning' | 'info';
  readonly solution: string;
  readonly relatedParameters?: readonly string[];
}

export interface ExternalResource {
  readonly title: string;
  readonly url: string;
  readonly type: 'documentation' | 'tutorial' | 'video' | 'forum' | 'specification';
  readonly description: string;
}

export interface CustomDocSection {
  readonly id: string;
  readonly title: string;
  readonly content: string;
  readonly order: number;
}

// Node Categories as defined in the roadmap
export const NODE_CATEGORIES: Record<string, NodeCategory> = {
  plc_control: {
    id: 'plc_control',
    name: 'PLC Control Nodes',
    description: 'Industrial control and automation nodes',
    iconClass: 'lucide-settings',
    templateExtensions: ['control-theory', 'tuning-guidelines', 'stability-analysis'],
  },
  ml_algorithm: {
    id: 'ml_algorithm',
    name: 'ML Algorithm Nodes',
    description: 'Machine learning and AI algorithm nodes',
    iconClass: 'lucide-brain',
    templateExtensions: ['model-configuration', 'training-parameters', 'evaluation-metrics'],
  },
  mpc_control: {
    id: 'mpc_control',
    name: 'MPC Control Nodes',
    description: 'Model Predictive Control nodes',
    iconClass: 'lucide-target',
    templateExtensions: ['control-theory', 'constraint-handling', 'optimization'],
  },
  model_tuning: {
    id: 'model_tuning',
    name: 'Model Fine-Tuning Nodes',
    description: 'Model identification and tuning nodes',
    iconClass: 'lucide-sliders',
    templateExtensions: ['identification-methods', 'parameter-estimation', 'validation-metrics'],
  },
  testing_analysis: {
    id: 'testing_analysis',
    name: 'Testing & Analysis Nodes',
    description: 'Testing, validation, and analysis nodes',
    iconClass: 'lucide-flask',
    templateExtensions: ['test-procedures', 'analysis-methods', 'performance-metrics'],
  },
  data_sources: {
    id: 'data_sources',
    name: 'Data Source Nodes',
    description: 'Database and data connectivity nodes',
    iconClass: 'lucide-database',
    templateExtensions: ['database-specifics', 'connection-strings', 'query-optimization'],
  },
  data_processing: {
    id: 'data_processing',
    name: 'Data Processing Nodes',
    description: 'Data transformation and processing nodes',
    iconClass: 'lucide-shuffle',
    templateExtensions: [
      'data-transformation',
      'processing-algorithms',
      'performance-optimization',
    ],
  },
  reporting: {
    id: 'reporting',
    name: 'Reporting & Visualization Nodes',
    description: 'Report generation and visualization nodes',
    iconClass: 'lucide-bar-chart',
    templateExtensions: ['report-templates', 'visualization-options', 'export-formats'],
  },
  workflow: {
    id: 'workflow',
    name: 'Workflow Nodes',
    description: 'Nested and composite workflow nodes',
    iconClass: 'lucide-workflow',
    templateExtensions: ['workflow-orchestration', 'nesting-patterns', 'execution-control'],
  },
} as const;

// Node Type Registry - All 54+ nodes as defined in roadmap
export const NODE_REGISTRY: Record<string, Partial<NodeDocumentationSpec>> = {
  // 🔧 PLC Control Nodes (12 nodes)
  'plc-input': {
    nodeType: 'plc-input',
    category: NODE_CATEGORIES.plc_control,
    title: 'PLC Input Node',
    description: 'Digital and analog input configuration for PLC systems',
  },
  'plc-output': {
    nodeType: 'plc-output',
    category: NODE_CATEGORIES.plc_control,
    title: 'PLC Output Node',
    description: 'Digital and analog output configuration for PLC systems',
  },
  'pid-controller': {
    nodeType: 'pid-controller',
    category: NODE_CATEGORIES.plc_control,
    title: 'PID Controller',
    description: 'Proportional-Integral-Derivative control algorithm with tuning parameters',
  },
  'feedforward-controller': {
    nodeType: 'feedforward-controller',
    category: NODE_CATEGORIES.plc_control,
    title: 'Feedforward Controller',
    description: 'Feedforward control for disturbance rejection and performance enhancement',
  },
  'url-display': {
    nodeType: 'url-display',
    category: NODE_CATEGORIES.plc_control,
    title: 'URL Display Node',
    description: 'Display web content and URLs within workflow interface',
  },
  'data-logger': {
    nodeType: 'data-logger',
    category: NODE_CATEGORIES.plc_control,
    title: 'Data Logger',
    description: 'Time-series data logging with configurable storage options',
  },
  'alarm-handler': {
    nodeType: 'alarm-handler',
    category: NODE_CATEGORIES.plc_control,
    title: 'Alarm Handler',
    description: 'Industrial alarm management and notification system',
  },
  'modbus-client': {
    nodeType: 'modbus-client',
    category: NODE_CATEGORIES.plc_control,
    title: 'Modbus Client',
    description: 'Modbus protocol client for industrial device communication',
  },
  'opc-server': {
    nodeType: 'opc-server',
    category: NODE_CATEGORIES.plc_control,
    title: 'OPC UA Server',
    description: 'OPC UA server for industrial data publishing',
  },
  'opc-client': {
    nodeType: 'opc-client',
    category: NODE_CATEGORIES.plc_control,
    title: 'OPC UA Client',
    description: 'OPC UA client for industrial data subscription',
  },
  'custom-logic': {
    nodeType: 'custom-logic',
    category: NODE_CATEGORIES.plc_control,
    title: 'Custom Logic Node',
    description: 'User-defined scripting and custom control logic',
  },

  // 🤖 ML Algorithm Nodes (5 nodes)
  'narx-neural-network': {
    nodeType: 'narx-neural-network',
    category: NODE_CATEGORIES.ml_algorithm,
    title: 'NARX Neural Network',
    description: 'Nonlinear Auto-Regressive eXogenous neural network for system identification',
  },
  'gaussian-process-regression': {
    nodeType: 'gaussian-process-regression',
    category: NODE_CATEGORIES.ml_algorithm,
    title: 'Gaussian Process Regression',
    description: 'Bayesian regression with uncertainty quantification',
  },
  'lstm-model': {
    nodeType: 'lstm-model',
    category: NODE_CATEGORIES.ml_algorithm,
    title: 'LSTM Model',
    description: 'Long Short-Term Memory networks for sequence modeling',
  },
  'sindy-identifier': {
    nodeType: 'sindy-identifier',
    category: NODE_CATEGORIES.ml_algorithm,
    title: 'SINDy Identifier',
    description: 'Sparse Identification of Nonlinear Dynamics',
  },
  'reinforcement-learning': {
    nodeType: 'reinforcement-learning',
    category: NODE_CATEGORIES.ml_algorithm,
    title: 'Reinforcement Learning',
    description: 'RL algorithms for optimal control policy learning',
  },

  // 🎯 MPC Control Nodes (5 nodes)
  'mpc-controller': {
    nodeType: 'mpc-controller',
    category: NODE_CATEGORIES.mpc_control,
    title: 'MPC Controller',
    description: 'Model Predictive Control with constraints and optimization',
  },
  'kalman-filter': {
    nodeType: 'kalman-filter',
    category: NODE_CATEGORIES.mpc_control,
    title: 'Kalman Filter',
    description: 'State estimation and filtering for control systems',
  },
  'quadratic-programming': {
    nodeType: 'quadratic-programming',
    category: NODE_CATEGORIES.mpc_control,
    title: 'Quadratic Programming Solver',
    description: 'QP optimization solver for MPC applications',
  },
  'subspace-identification': {
    nodeType: 'subspace-identification',
    category: NODE_CATEGORIES.mpc_control,
    title: 'Subspace Identification',
    description: 'N4SID and MOESP algorithms for system identification',
  },
  'imc-controller': {
    nodeType: 'imc-controller',
    category: NODE_CATEGORIES.mpc_control,
    title: 'IMC Controller',
    description: 'Internal Model Control design and implementation',
  },

  // 🔬 Model Fine-Tuning Nodes (5 nodes)
  'arx-armax-identifier': {
    nodeType: 'arx-armax-identifier',
    category: NODE_CATEGORIES.model_tuning,
    title: 'ARX/ARMAX Identifier',
    description: 'Auto-regressive model identification with exogenous inputs',
  },
  'genetic-algorithm': {
    nodeType: 'genetic-algorithm',
    category: NODE_CATEGORIES.model_tuning,
    title: 'Genetic Algorithm Optimizer',
    description: 'Evolutionary optimization for parameter tuning',
  },
  'recursive-least-squares': {
    nodeType: 'recursive-least-squares',
    category: NODE_CATEGORIES.model_tuning,
    title: 'Recursive Least Squares',
    description: 'Adaptive parameter estimation with forgetting factor',
  },
  'model-validation': {
    nodeType: 'model-validation',
    category: NODE_CATEGORIES.model_tuning,
    title: 'Model Validation',
    description: 'Statistical validation and performance assessment',
  },
  'pilco-pets': {
    nodeType: 'pilco-pets',
    category: NODE_CATEGORIES.model_tuning,
    title: 'PILCO/PETS',
    description: 'Model-based reinforcement learning for control',
  },

  // 🧪 Testing & Analysis Nodes (5 nodes)
  'prbs-generator': {
    nodeType: 'prbs-generator',
    category: NODE_CATEGORIES.testing_analysis,
    title: 'PRBS Generator',
    description: 'Pseudo-Random Binary Sequence generation for system identification',
  },
  'relay-feedback-test': {
    nodeType: 'relay-feedback-test',
    category: NODE_CATEGORIES.testing_analysis,
    title: 'Relay Feedback Test',
    description: 'Relay auto-tuning for PID controller parameters',
  },
  'step-response-analyzer': {
    nodeType: 'step-response-analyzer',
    category: NODE_CATEGORIES.testing_analysis,
    title: 'Step Response Analyzer',
    description: 'Step response analysis and system characterization',
  },
  'distillation-simulator': {
    nodeType: 'distillation-simulator',
    category: NODE_CATEGORIES.testing_analysis,
    title: 'Distillation Simulator',
    description: 'Dynamic distillation column simulation and control',
  },
  'performance-metrics': {
    nodeType: 'performance-metrics',
    category: NODE_CATEGORIES.testing_analysis,
    title: 'Performance Metrics',
    description: 'KPI calculation and performance monitoring',
  },

  // 💾 Data Source Nodes (6 nodes)
  'postgresql-connector': {
    nodeType: 'postgresql-connector',
    category: NODE_CATEGORIES.data_sources,
    title: 'PostgreSQL Connector',
    description: 'PostgreSQL database connectivity and query execution',
  },
  'redis-connector': {
    nodeType: 'redis-connector',
    category: NODE_CATEGORIES.data_sources,
    title: 'Redis Connector',
    description: 'Redis key-value store integration',
  },
  'neo4j-connector': {
    nodeType: 'neo4j-connector',
    category: NODE_CATEGORIES.data_sources,
    title: 'Neo4j Connector',
    description: 'Graph database connectivity with Cypher query support',
  },
  'qdrant-connector': {
    nodeType: 'qdrant-connector',
    category: NODE_CATEGORIES.data_sources,
    title: 'Qdrant Connector',
    description: 'Vector database integration for similarity search',
  },
  'historian-connector': {
    nodeType: 'historian-connector',
    category: NODE_CATEGORIES.data_sources,
    title: 'Historian Connector',
    description: 'Process historian integration for time-series data',
  },
  'mqtt-client': {
    nodeType: 'mqtt-client',
    category: NODE_CATEGORIES.data_sources,
    title: 'MQTT 5 Client',
    description: 'MQTT client for IoT device communication',
  },

  // 🔄 Data Processing Nodes (6 nodes)
  'csv-dataset-creator': {
    nodeType: 'csv-dataset-creator',
    category: NODE_CATEGORIES.data_processing,
    title: 'CSV Dataset Creator',
    description: 'CSV data processing with schema validation',
  },
  'excel-dataset-creator': {
    nodeType: 'excel-dataset-creator',
    category: NODE_CATEGORIES.data_processing,
    title: 'Excel Dataset Creator',
    description: 'Excel spreadsheet data extraction and mapping',
  },
  'data-cleaner': {
    nodeType: 'data-cleaner',
    category: NODE_CATEGORIES.data_processing,
    title: 'Data Cleaner',
    description: 'Data quality assessment and cleaning operations',
  },
  'feature-engineer': {
    nodeType: 'feature-engineer',
    category: NODE_CATEGORIES.data_processing,
    title: 'Feature Engineer',
    description: 'Feature extraction and engineering for machine learning',
  },
  'time-series-processor': {
    nodeType: 'time-series-processor',
    category: NODE_CATEGORIES.data_processing,
    title: 'Time Series Processor',
    description: 'Time series analysis and preprocessing',
  },
  'math-function-creator': {
    nodeType: 'math-function-creator',
    category: NODE_CATEGORIES.data_processing,
    title: 'Math Function Creator',
    description: 'Custom mathematical functions and equations with scientific calculator',
  },

  // 📊 Reporting & Visualization Nodes (5 nodes)
  'dashboard-generator': {
    nodeType: 'dashboard-generator',
    category: NODE_CATEGORIES.reporting,
    title: 'Dashboard Generator',
    description: 'Interactive dashboard creation and configuration',
  },
  'pdf-report-generator': {
    nodeType: 'pdf-report-generator',
    category: NODE_CATEGORIES.reporting,
    title: 'PDF Report Generator',
    description: 'Automated PDF report generation with templates',
  },
  'email-notifier': {
    nodeType: 'email-notifier',
    category: NODE_CATEGORIES.reporting,
    title: 'Email Notifier',
    description: 'Email notification and alert system',
  },
  'chart-generator': {
    nodeType: 'chart-generator',
    category: NODE_CATEGORIES.reporting,
    title: 'Chart Generator',
    description: 'Dynamic chart and visualization generation',
  },
  'kpi-calculator': {
    nodeType: 'kpi-calculator',
    category: NODE_CATEGORIES.reporting,
    title: 'KPI Calculator',
    description: 'Key Performance Indicator calculation and monitoring',
  },

  // 🔗 Workflow Nodes will be added in future phase
} as const;

// Type-safe node type extraction
export type NodeTypeId = keyof typeof NODE_REGISTRY;
export type NodeCategoryId = keyof typeof NODE_CATEGORIES;

// Documentation generation utilities
export class NodeDocumentationGenerator {
  /**
   * Generate complete documentation specification for a node
   */
  public static generateDocumentationSpec(
    nodeTypeId: NodeTypeId,
    customOverrides?: Partial<NodeDocumentationSpec>
  ): NodeDocumentationSpec {
    const baseSpec = NODE_REGISTRY[nodeTypeId];
    if (!baseSpec) {
      throw new Error(`Node type ${nodeTypeId} not found in registry`);
    }

    // Create default complete specification
    const defaultSpec: NodeDocumentationSpec = {
      nodeType: baseSpec.nodeType || nodeTypeId,
      category: baseSpec.category || NODE_CATEGORIES.plc_control,
      title: baseSpec.title || 'Untitled Node',
      description: baseSpec.description || 'No description provided',
      version: '1.0.0',
      lastUpdated: new Date().toISOString().split('T')[0],

      parameters: [],
      examples: [],
      connections: {
        inputHandles: [],
        outputHandles: [],
      },
      validation: [],

      overview: {
        purpose: baseSpec.description || 'Industrial control node',
        keyFeatures: [],
        useCases: [],
        whenToUse: [],
      },

      configurationGuide: {
        quickStart: [],
        detailedSteps: [],
        bestPractices: [],
        commonMistakes: [],
      },

      troubleshooting: {
        commonIssues: [],
        errorCodes: [],
        diagnosticProcedures: [],
      },

      relatedNodes: [],
      externalResources: [],
      templateCategory: baseSpec.category?.id || 'plc_control',
    };

    // Merge with custom overrides
    return {
      ...defaultSpec,
      ...customOverrides,
    };
  }

  /**
   * Get all node types for a specific category
   */
  public static getNodesByCategory(categoryId: NodeCategoryId): readonly NodeTypeId[] {
    return Object.keys(NODE_REGISTRY).filter(
      nodeType => NODE_REGISTRY[nodeType as NodeTypeId]?.category?.id === categoryId
    ) as readonly NodeTypeId[];
  }

  /**
   * Generate markdown documentation from specification
   */
  public static generateMarkdownDocumentation(spec: NodeDocumentationSpec): string {
    // This will be implemented in the next file
    return `# ${spec.title} - Documentation\n\n[Template will be implemented in documentation template generator]`;
  }
}

export default NodeDocumentationGenerator;
