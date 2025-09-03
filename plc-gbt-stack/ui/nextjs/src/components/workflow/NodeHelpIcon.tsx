/**
 * Node Help Icon Component - AI Task Orchestrator TypeScript Implementation
 *
 * @description CircleHelp icon system providing contextual help for all node types
 * @compliance Strict TypeScript - zero `any` types policy
 * @integration OpenAPI Schema MCP for help content validation
 * @features Tooltip display, documentation linking, contextual help
 */

'use client';

import { CircleHelp, ExternalLink } from 'lucide-react';
import React, { useCallback, useState } from 'react';

import { type IndustrialNodeType } from '@/api/zod-schemas';
import { cn } from '@/lib/utils/cn';

interface NodeHelpContent {
  readonly title: string;
  readonly description: string;
  readonly keyParameters: ReadonlyArray<string>;
  readonly useCases: ReadonlyArray<string>;
  readonly troubleshooting: ReadonlyArray<string>;
  readonly documentationUrl?: string;
  readonly isCustomPage: boolean;
}

interface NodeHelpIconProps {
  readonly nodeType: IndustrialNodeType;
  readonly className?: string;
  readonly size?: 'sm' | 'md' | 'lg';
  readonly showTooltip?: boolean;
  readonly onHelpClick?: (nodeType: IndustrialNodeType) => void;
}

// Help content registry for all node types
const NODE_HELP_CONTENT: Record<IndustrialNodeType, NodeHelpContent> = {
  'pid-controller': {
    title: 'PID Controller',
    description: 'Proportional-Integral-Derivative controller for closed-loop process control',
    keyParameters: ['Kp (Proportional)', 'Ki (Integral)', 'Kd (Derivative)', 'Setpoint'],
    useCases: ['Temperature control', 'Flow rate regulation', 'Pressure control'],
    troubleshooting: ['Check tuning parameters', 'Verify sensor feedback', 'Review output limits'],
    documentationUrl: '/docs/nodes/pid-controller',
    isCustomPage: true,
  },
  'modbus-client': {
    title: 'Modbus Client',
    description: 'Industrial communication protocol client for reading/writing device data',
    keyParameters: ['Host Address', 'Port', 'Unit ID', 'Register Type'],
    useCases: ['PLC communication', 'Sensor data acquisition', 'Device control'],
    troubleshooting: [
      'Verify network connectivity',
      'Check device address',
      'Validate register mapping',
    ],
    documentationUrl: 'https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf',
    isCustomPage: false,
  },
  'opc-server': {
    title: 'OPC Server',
    description: 'OLE for Process Control server for industrial data exchange',
    keyParameters: ['Endpoint URL', 'Security Policy', 'Authentication'],
    useCases: ['SCADA integration', 'HMI data exchange', 'Process monitoring'],
    troubleshooting: ['Check server endpoint', 'Verify security settings', 'Test authentication'],
    documentationUrl:
      'https://opcfoundation.org/developer-tools/specifications-unified-architecture',
    isCustomPage: false,
  },
  'opc-client': {
    title: 'OPC Client',
    description: 'OPC client for connecting to industrial OPC servers',
    keyParameters: ['Server URL', 'Node ID', 'Subscription Rate'],
    useCases: [
      'Data collection from OPC servers',
      'Real-time monitoring',
      'Historical data access',
    ],
    troubleshooting: [
      'Verify server connection',
      'Check node identifiers',
      'Monitor subscription status',
    ],
    documentationUrl: '/docs/nodes/opc-client',
    isCustomPage: true,
  },
  'hmi-display': {
    title: 'HMI Display',
    description: 'Human Machine Interface display component for operator interaction',
    keyParameters: ['Display Type', 'Update Rate', 'Color Scheme'],
    useCases: ['Process visualization', 'Operator interface', 'Status monitoring'],
    troubleshooting: ['Check data binding', 'Verify update frequency', 'Test user interactions'],
    documentationUrl: '/docs/nodes/hmi-display',
    isCustomPage: true,
  },
  'plc-input': {
    title: 'PLC Input',
    description:
      'Programmable Logic Controller input for reading sensor data. Input Type: Digital, Analog. Data Type: BOOLEAN, SINT, INT, DINT, REAL, STRING, UDT, SINT[X], INT[X], DINT[X], REAL[X], STRING[X], UDT[X]',
    keyParameters: [
      'Input Type (Digital/Analog)',
      'Data Type (BOOLEAN, SINT, INT, DINT, REAL, STRING, UDT, Arrays)',
      'PLC Address',
      'Engineering Units',
    ],
    useCases: [
      'Digital sensor reading',
      'Analog signal processing',
      'Temperature monitoring',
      'Pressure sensing',
    ],
    troubleshooting: [
      'Verify PLC connection',
      'Check address format',
      'Validate data type compatibility',
      'Test signal scaling',
    ],
    documentationUrl: '/docs/nodes/plc-input',
    isCustomPage: true,
  },
  'plc-output': {
    title: 'PLC Output',
    description: 'PLC output for controlling actuators and devices',
    keyParameters: ['Address', 'Output Type', 'Initial Value'],
    useCases: ['Valve control', 'Motor control', 'Digital output control'],
    troubleshooting: ['Check output address', 'Verify actuator connection', 'Test output signals'],
    documentationUrl: '/docs/nodes/plc-output',
    isCustomPage: true,
  },
  'data-logger': {
    title: 'Data Logger',
    description: 'Historical data logging and storage system',
    keyParameters: ['Log Interval', 'Storage Location', 'Data Retention'],
    useCases: ['Process history', 'Trend analysis', 'Compliance reporting'],
    troubleshooting: ['Check storage space', 'Verify log intervals', 'Review data integrity'],
    documentationUrl: '/docs/nodes/data-logger',
    isCustomPage: true,
  },
  'alarm-handler': {
    title: 'Alarm Handler',
    description: 'Process alarm detection, notification, and management system',
    keyParameters: ['Alarm Type', 'Threshold Values', 'Notification Method'],
    useCases: ['Safety monitoring', 'Process alerts', 'Equipment protection'],
    troubleshooting: [
      'Review alarm conditions',
      'Test notification systems',
      'Check acknowledgment',
    ],
    documentationUrl: '/docs/nodes/alarm-handler',
    isCustomPage: true,
  },
  'custom-logic': {
    title: 'Custom Logic',
    description: 'User-defined logic block for custom process control algorithms',
    keyParameters: ['Logic Type', 'Input Variables', 'Output Variables'],
    useCases: ['Custom calculations', 'Business logic', 'Complex control strategies'],
    troubleshooting: ['Debug logic flow', 'Verify variable mapping', 'Test edge cases'],
    documentationUrl: '/docs/nodes/custom-logic',
    isCustomPage: true,
  },
  'feedforward-controller': {
    title: 'Feedforward Controller',
    description: 'Feedforward control system for disturbance compensation',
    keyParameters: ['Disturbance Input', 'Compensation Factor', 'Lead/Lag Time'],
    useCases: ['Load disturbance rejection', 'Process optimization', 'Advanced control'],
    troubleshooting: ['Tune compensation factor', 'Check disturbance measurement', 'Verify timing'],
    documentationUrl: '/docs/nodes/feedforward-controller',
    isCustomPage: true,
  },
  'url-display': {
    title: 'URL Display',
    description: 'Web content display component for embedding external resources',
    keyParameters: ['URL', 'Refresh Rate', 'Display Size'],
    useCases: ['Web dashboard embedding', 'External content display', 'Real-time web data'],
    troubleshooting: [
      'Check URL accessibility',
      'Verify network connectivity',
      'Test refresh functionality',
    ],
    documentationUrl: '/docs/nodes/url-display',
    isCustomPage: true,
  },
  'n8n-workflow': {
    title: 'N8N Workflow',
    description: 'Integration with N8N automation platform for workflow execution',
    keyParameters: ['Workflow ID', 'Execution Mode', 'Input Parameters'],
    useCases: ['Automation workflows', 'Data processing', 'Integration tasks'],
    troubleshooting: ['Check N8N connection', 'Verify workflow ID', 'Test execution parameters'],
    documentationUrl: '/docs/nodes/n8n-workflow',
    isCustomPage: true,
  },
  'math-function-creator': {
    title: 'Math Function Creator',
    description: 'Mathematical function builder with scientific calculator capabilities',
    keyParameters: ['Function Expression', 'Input Variables', 'Output Range'],
    useCases: ['Custom calculations', 'Mathematical modeling', 'Formula implementation'],
    troubleshooting: [
      'Validate function syntax',
      'Check variable definitions',
      'Test calculation results',
    ],
    documentationUrl: '/docs/nodes/math-function-creator',
    isCustomPage: true,
  },
  'data-distribution-analyzer': {
    title: 'Data Distribution Analyzer',
    description: 'Statistical analysis tool for data distribution and quality assessment',
    keyParameters: ['Analysis Type', 'Sample Size', 'Confidence Level'],
    useCases: ['Quality control', 'Statistical analysis', 'Process capability'],
    troubleshooting: ['Check sample size', 'Verify data quality', 'Review statistical parameters'],
    documentationUrl: '/docs/nodes/data-distribution-analyzer',
    isCustomPage: true,
  },
  'workflow-reference': {
    title: 'Workflow Reference',
    description: 'Reference to external workflow for modular design',
    keyParameters: ['Workflow Path', 'Input Mapping', 'Output Mapping'],
    useCases: ['Modular workflows', 'Reusable components', 'Workflow organization'],
    troubleshooting: [
      'Check workflow path',
      'Verify input/output mapping',
      'Test reference resolution',
    ],
    documentationUrl: '/docs/nodes/workflow-reference',
    isCustomPage: true,
  },
  'workflow-subset': {
    title: 'Workflow Subset',
    description: 'Subset execution of larger workflow for selective processing',
    keyParameters: ['Subset Definition', 'Execution Scope', 'Filter Criteria'],
    useCases: ['Selective execution', 'Conditional processing', 'Workflow optimization'],
    troubleshooting: ['Check subset criteria', 'Verify execution scope', 'Test filter conditions'],
    documentationUrl: '/docs/nodes/workflow-subset',
    isCustomPage: true,
  },
  'workflow-conditional': {
    title: 'Workflow Conditional',
    description: 'Conditional execution logic for workflow branching',
    keyParameters: ['Condition Expression', 'True Path', 'False Path'],
    useCases: ['Decision making', 'Conditional logic', 'Workflow branching'],
    troubleshooting: ['Validate condition logic', 'Check path execution', 'Test edge cases'],
    documentationUrl: '/docs/nodes/workflow-conditional',
    isCustomPage: true,
  },
  'workflow-parallel': {
    title: 'Workflow Parallel',
    description: 'Parallel execution of multiple workflow branches',
    keyParameters: ['Branch Count', 'Synchronization Mode', 'Timeout Settings'],
    useCases: ['Parallel processing', 'Performance optimization', 'Concurrent execution'],
    troubleshooting: [
      'Check branch execution',
      'Monitor synchronization',
      'Review timeout settings',
    ],
    documentationUrl: '/docs/nodes/workflow-parallel',
    isCustomPage: true,
  },
  'workflow-loop': {
    title: 'Workflow Loop',
    description: 'Iterative execution of workflow segments with loop control',
    keyParameters: ['Loop Type', 'Iteration Count', 'Exit Condition'],
    useCases: ['Batch processing', 'Iterative calculations', 'Data processing loops'],
    troubleshooting: ['Check loop conditions', 'Monitor iteration count', 'Verify exit criteria'],
    documentationUrl: '/docs/nodes/workflow-loop',
    isCustomPage: true,
  },
  'postgresql-connector': {
    title: 'PostgreSQL Connector',
    description: 'Database connector for PostgreSQL integration',
    keyParameters: ['Connection String', 'Query Type', 'Timeout Settings'],
    useCases: ['Data storage', 'Historical queries', 'Process data management'],
    troubleshooting: ['Check connection string', 'Verify database access', 'Test query syntax'],
    documentationUrl: '/docs/nodes/postgresql-connector',
    isCustomPage: true,
  },
  'redis-connector': {
    title: 'Redis Connector',
    description: 'In-memory data structure store connector for caching and real-time data',
    keyParameters: ['Redis Host', 'Port', 'Database Index'],
    useCases: ['Real-time caching', 'Session storage', 'Message queuing'],
    troubleshooting: ['Check Redis connection', 'Verify database index', 'Test key operations'],
    documentationUrl: '/docs/nodes/redis-connector',
    isCustomPage: true,
  },
  'neo4j-connector': {
    title: 'Neo4j Connector',
    description: 'Graph database connector for relationship-based data storage',
    keyParameters: ['Neo4j URI', 'Authentication', 'Cypher Query'],
    useCases: ['Relationship mapping', 'Graph analytics', 'Network analysis'],
    troubleshooting: ['Check database connection', 'Verify Cypher syntax', 'Test graph queries'],
    documentationUrl: '/docs/nodes/neo4j-connector',
    isCustomPage: true,
  },
  'qdrant-connector': {
    title: 'Qdrant Connector',
    description: 'Vector database connector for similarity search and AI applications',
    keyParameters: ['Qdrant URL', 'Collection Name', 'Vector Dimension'],
    useCases: ['Vector search', 'AI model integration', 'Similarity analysis'],
    troubleshooting: ['Check vector dimensions', 'Verify collection setup', 'Test search queries'],
    documentationUrl: '/docs/nodes/qdrant-connector',
    isCustomPage: true,
  },
  'historian-connector': {
    title: 'Historian Connector',
    description: 'Process historian database connector for time-series data',
    keyParameters: ['Historian Server', 'Tag Configuration', 'Time Range'],
    useCases: ['Historical analysis', 'Trend monitoring', 'Process optimization'],
    troubleshooting: ['Check historian connection', 'Verify tag names', 'Test time range queries'],
    documentationUrl: '/docs/nodes/historian-connector',
    isCustomPage: true,
  },
  'narx-neural-network': {
    title: 'NARX Neural Network',
    description:
      'Nonlinear AutoRegressive with eXogenous inputs neural network for system identification',
    keyParameters: ['Network Architecture', 'Training Data', 'Delay Parameters'],
    useCases: ['System modeling', 'Prediction', 'Nonlinear identification'],
    troubleshooting: [
      'Check training data quality',
      'Adjust network parameters',
      'Validate model accuracy',
    ],
    documentationUrl: '/docs/nodes/narx-neural-network',
    isCustomPage: true,
  },
  'gaussian-process-regression': {
    title: 'Gaussian Process Regression',
    description:
      'Probabilistic machine learning model for regression and uncertainty quantification',
    keyParameters: ['Kernel Function', 'Hyperparameters', 'Training Data'],
    useCases: ['Predictive modeling', 'Uncertainty quantification', 'Optimization'],
    troubleshooting: [
      'Select appropriate kernel',
      'Tune hyperparameters',
      'Check data preprocessing',
    ],
    documentationUrl: '/docs/nodes/gaussian-process-regression',
    isCustomPage: true,
  },
  'lstm-model': {
    title: 'LSTM Model',
    description: 'Long Short-Term Memory neural network for sequence prediction',
    keyParameters: ['LSTM Units', 'Sequence Length', 'Training Epochs'],
    useCases: ['Time series forecasting', 'Sequence prediction', 'Process modeling'],
    troubleshooting: [
      'Adjust sequence length',
      'Monitor training loss',
      'Check data normalization',
    ],
    documentationUrl: '/docs/nodes/lstm-model',
    isCustomPage: true,
  },
  'sindy-identifier': {
    title: 'SINDy Identifier',
    description: 'Sparse Identification of Nonlinear Dynamics for discovering governing equations',
    keyParameters: ['Library Functions', 'Sparsity Threshold', 'Regularization'],
    useCases: ['System identification', 'Equation discovery', 'Model reduction'],
    troubleshooting: [
      'Adjust sparsity threshold',
      'Select library functions',
      'Validate discovered equations',
    ],
    documentationUrl: '/docs/nodes/sindy-identifier',
    isCustomPage: true,
  },
  'reinforcement-learning': {
    title: 'Reinforcement Learning',
    description: 'RL agent for learning optimal control policies through interaction',
    keyParameters: ['Algorithm Type', 'Reward Function', 'Exploration Rate'],
    useCases: ['Optimal control', 'Adaptive control', 'Process optimization'],
    troubleshooting: [
      'Design reward function',
      'Tune exploration parameters',
      'Monitor learning progress',
    ],
    documentationUrl: '/docs/nodes/reinforcement-learning',
    isCustomPage: true,
  },
  'mpc-controller': {
    title: 'MPC Controller',
    description: 'Model Predictive Controller for advanced multivariable control',
    keyParameters: ['Prediction Horizon', 'Control Horizon', 'Constraints'],
    useCases: ['Multivariable control', 'Constraint handling', 'Optimal control'],
    troubleshooting: [
      'Tune horizon parameters',
      'Check constraint feasibility',
      'Validate model accuracy',
    ],
    documentationUrl: '/docs/nodes/mpc-controller',
    isCustomPage: true,
  },
  'kalman-filter': {
    title: 'Kalman Filter',
    description: 'State estimation filter for noisy measurements and system dynamics',
    keyParameters: ['State Model', 'Process Noise', 'Measurement Noise'],
    useCases: ['State estimation', 'Sensor fusion', 'Noise filtering'],
    troubleshooting: ['Tune noise parameters', 'Validate state model', 'Check filter convergence'],
    documentationUrl: '/docs/nodes/kalman-filter',
    isCustomPage: true,
  },
  'quadratic-programming': {
    title: 'Quadratic Programming',
    description: 'QP solver for optimization problems with quadratic objectives',
    keyParameters: ['Objective Function', 'Constraints', 'Solver Method'],
    useCases: ['Optimization problems', 'MPC implementation', 'Resource allocation'],
    troubleshooting: [
      'Check problem formulation',
      'Verify constraint feasibility',
      'Select appropriate solver',
    ],
    documentationUrl: '/docs/nodes/quadratic-programming',
    isCustomPage: true,
  },
  'subspace-identification': {
    title: 'Subspace Identification',
    description: 'System identification using subspace methods (N4SID, MOESP)',
    keyParameters: ['Model Order', 'Input-Output Data', 'Algorithm Type'],
    useCases: ['System identification', 'Model development', 'Process modeling'],
    troubleshooting: [
      'Select appropriate model order',
      'Check data quality',
      'Validate identified model',
    ],
    documentationUrl: '/docs/nodes/subspace-identification',
    isCustomPage: true,
  },
  'imc-controller': {
    title: 'IMC Controller',
    description: 'Internal Model Control for robust process control',
    keyParameters: ['Internal Model', 'Filter Parameter', 'Model Mismatch'],
    useCases: ['Robust control', 'Disturbance rejection', 'Model-based control'],
    troubleshooting: ['Validate internal model', 'Tune filter parameter', 'Check model accuracy'],
    documentationUrl: '/docs/nodes/imc-controller',
    isCustomPage: true,
  },
  'dashboard-generator': {
    title: 'Dashboard Generator',
    description: 'Automated dashboard creation for process visualization',
    keyParameters: ['Dashboard Template', 'Data Sources', 'Update Frequency'],
    useCases: ['Process monitoring', 'KPI visualization', 'Real-time dashboards'],
    troubleshooting: [
      'Check data source connections',
      'Verify template configuration',
      'Test update frequency',
    ],
    documentationUrl: '/docs/nodes/dashboard-generator',
    isCustomPage: true,
  },
  'pdf-report-generator': {
    title: 'PDF Report Generator',
    description: 'Automated PDF report generation from process data',
    keyParameters: ['Report Template', 'Data Query', 'Schedule'],
    useCases: ['Automated reporting', 'Compliance documents', 'Process summaries'],
    troubleshooting: ['Check template formatting', 'Verify data queries', 'Test report generation'],
    documentationUrl: '/docs/nodes/pdf-report-generator',
    isCustomPage: true,
  },
  'email-notifier': {
    title: 'Email Notifier',
    description: 'Email notification system for alerts and reports',
    keyParameters: ['SMTP Configuration', 'Recipients', 'Trigger Conditions'],
    useCases: ['Alert notifications', 'Report distribution', 'System notifications'],
    troubleshooting: ['Check SMTP settings', 'Verify recipient addresses', 'Test email delivery'],
    documentationUrl: '/docs/nodes/email-notifier',
    isCustomPage: true,
  },
  'chart-generator': {
    title: 'Chart Generator',
    description: 'Dynamic chart creation for data visualization',
    keyParameters: ['Chart Type', 'Data Source', 'Styling Options'],
    useCases: ['Data visualization', 'Trend analysis', 'Report graphics'],
    troubleshooting: ['Check data format', 'Verify chart configuration', 'Test rendering'],
    documentationUrl: '/docs/nodes/chart-generator',
    isCustomPage: true,
  },
  'kpi-calculator': {
    title: 'KPI Calculator',
    description: 'Key Performance Indicator calculation and monitoring',
    keyParameters: ['KPI Formula', 'Data Sources', 'Calculation Period'],
    useCases: ['Performance monitoring', 'Process optimization', 'Business metrics'],
    troubleshooting: [
      'Validate KPI formulas',
      'Check data availability',
      'Verify calculation periods',
    ],
    documentationUrl: '/docs/nodes/kpi-calculator',
    isCustomPage: true,
  },
  'arx-armax-identifier': {
    title: 'ARX/ARMAX Identifier',
    description: 'AutoRegressive with eXogenous inputs model identification',
    keyParameters: ['Model Order', 'Input Data', 'Estimation Method'],
    useCases: ['System identification', 'Model development', 'Parameter estimation'],
    troubleshooting: [
      'Check model order selection',
      'Verify data quality',
      'Validate estimation results',
    ],
    documentationUrl: '/docs/nodes/arx-armax-identifier',
    isCustomPage: true,
  },
  'genetic-algorithm': {
    title: 'Genetic Algorithm',
    description: 'Evolutionary optimization algorithm for parameter tuning',
    keyParameters: ['Population Size', 'Mutation Rate', 'Crossover Rate'],
    useCases: ['Parameter optimization', 'Controller tuning', 'Multi-objective optimization'],
    troubleshooting: [
      'Adjust population size',
      'Tune genetic operators',
      'Check convergence criteria',
    ],
    documentationUrl: '/docs/nodes/genetic-algorithm',
    isCustomPage: true,
  },
  'recursive-least-squares': {
    title: 'Recursive Least Squares',
    description: 'Adaptive parameter estimation using recursive least squares',
    keyParameters: ['Forgetting Factor', 'Initial Covariance', 'Regularization'],
    useCases: ['Adaptive control', 'Online parameter estimation', 'System adaptation'],
    troubleshooting: [
      'Tune forgetting factor',
      'Check numerical stability',
      'Monitor parameter drift',
    ],
    documentationUrl: '/docs/nodes/recursive-least-squares',
    isCustomPage: true,
  },
  'model-validation': {
    title: 'Model Validation',
    description: 'Model validation and performance assessment tools',
    keyParameters: ['Validation Method', 'Test Data', 'Performance Metrics'],
    useCases: ['Model verification', 'Performance assessment', 'Model selection'],
    troubleshooting: [
      'Check validation data quality',
      'Select appropriate metrics',
      'Interpret results',
    ],
    documentationUrl: '/docs/nodes/model-validation',
    isCustomPage: true,
  },
  'pilco-pets': {
    title: 'PILCO/PETS',
    description: 'Model-based reinforcement learning algorithms',
    keyParameters: ['Model Type', 'Planning Horizon', 'Uncertainty Propagation'],
    useCases: ['Model-based RL', 'Sample-efficient learning', 'Uncertainty-aware control'],
    troubleshooting: [
      'Check model accuracy',
      'Tune planning horizon',
      'Monitor uncertainty estimates',
    ],
    documentationUrl: '/docs/nodes/pilco-pets',
    isCustomPage: true,
  },
  'prbs-generator': {
    title: 'PRBS Generator',
    description: 'Pseudo-Random Binary Sequence generator for system identification',
    keyParameters: ['Sequence Length', 'Amplitude', 'Clock Period'],
    useCases: ['System identification', 'Process testing', 'Model validation'],
    troubleshooting: [
      'Check sequence properties',
      'Verify amplitude settings',
      'Monitor system response',
    ],
    documentationUrl: '/docs/nodes/prbs-generator',
    isCustomPage: true,
  },
  'relay-feedback-test': {
    title: 'Relay Feedback Test',
    description: 'Relay feedback tuning method for PID controller auto-tuning',
    keyParameters: ['Relay Amplitude', 'Hysteresis', 'Test Duration'],
    useCases: ['PID auto-tuning', 'Process characterization', 'Controller commissioning'],
    troubleshooting: [
      'Adjust relay amplitude',
      'Check oscillation quality',
      'Verify test completion',
    ],
    documentationUrl: '/docs/nodes/relay-feedback-test',
    isCustomPage: true,
  },
  'step-response-analyzer': {
    title: 'Step Response Analyzer',
    description: 'Step test analysis for process characterization',
    keyParameters: ['Step Size', 'Test Duration', 'Analysis Method'],
    useCases: ['Process identification', 'Controller tuning', 'System analysis'],
    troubleshooting: ['Check step size', 'Verify test duration', 'Analyze response quality'],
    documentationUrl: '/docs/nodes/step-response-analyzer',
    isCustomPage: true,
  },
  'distillation-simulator': {
    title: 'Distillation Simulator',
    description: 'Distillation column simulation and control',
    keyParameters: ['Column Configuration', 'Operating Conditions', 'Control Strategy'],
    useCases: ['Process simulation', 'Control design', 'Operator training'],
    troubleshooting: [
      'Check column parameters',
      'Verify operating conditions',
      'Validate control logic',
    ],
    documentationUrl: '/docs/nodes/distillation-simulator',
    isCustomPage: true,
  },
  'performance-metrics': {
    title: 'Performance Metrics',
    description: 'Process performance monitoring and KPI calculation',
    keyParameters: ['Metric Type', 'Calculation Window', 'Alarm Limits'],
    useCases: ['Performance monitoring', 'Process optimization', 'Quality control'],
    troubleshooting: ['Check calculation methods', 'Verify data sources', 'Review alarm settings'],
    documentationUrl: '/docs/nodes/performance-metrics',
    isCustomPage: true,
  },
  'csv-dataset-creator': {
    title: 'CSV Dataset Creator',
    description: 'CSV file generation and dataset creation tool',
    keyParameters: ['File Path', 'Column Mapping', 'Data Format'],
    useCases: ['Data export', 'Report generation', 'Dataset creation'],
    troubleshooting: ['Check file permissions', 'Verify column mapping', 'Test data format'],
    documentationUrl: '/docs/nodes/csv-dataset-creator',
    isCustomPage: true,
  },
  'excel-dataset-creator': {
    title: 'Excel Dataset Creator',
    description: 'Excel file generation and dataset creation tool',
    keyParameters: ['Workbook Template', 'Sheet Configuration', 'Data Mapping'],
    useCases: ['Excel reporting', 'Data analysis', 'Template-based exports'],
    troubleshooting: ['Check template format', 'Verify data mapping', 'Test Excel compatibility'],
    documentationUrl: '/docs/nodes/excel-dataset-creator',
    isCustomPage: true,
  },
  'data-cleaner': {
    title: 'Data Cleaner',
    description: 'Data quality assessment and cleaning operations',
    keyParameters: ['Cleaning Rules', 'Quality Thresholds', 'Output Format'],
    useCases: ['Data preprocessing', 'Quality control', 'Data validation'],
    troubleshooting: ['Review cleaning rules', 'Check quality metrics', 'Validate output data'],
    documentationUrl: '/docs/nodes/data-cleaner',
    isCustomPage: true,
  },
  'feature-engineer': {
    title: 'Feature Engineer',
    description: 'Feature engineering and transformation for machine learning',
    keyParameters: ['Feature Types', 'Transformation Methods', 'Selection Criteria'],
    useCases: ['ML preprocessing', 'Feature selection', 'Data transformation'],
    troubleshooting: [
      'Check feature definitions',
      'Verify transformations',
      'Test feature quality',
    ],
    documentationUrl: '/docs/nodes/feature-engineer',
    isCustomPage: true,
  },
  'time-series-processor': {
    title: 'Time Series Processor',
    description: 'Time series analysis and processing operations',
    keyParameters: ['Analysis Type', 'Window Size', 'Aggregation Method'],
    useCases: ['Trend analysis', 'Forecasting', 'Time series modeling'],
    troubleshooting: ['Check time alignment', 'Verify window parameters', 'Test analysis results'],
    documentationUrl: '/docs/nodes/time-series-processor',
    isCustomPage: true,
  },
  // Enhanced Industrial PLC Connectivity Nodes
  'advanced-modbus-client': {
    title: 'Advanced Modbus Client',
    description:
      'Industrial-grade Modbus TCP/RTU client with enhanced diagnostics, security, and performance optimization',
    keyParameters: [
      'Connection Type',
      'High-Performance Mode',
      'Security Level',
      'Data Buffering',
      'Diagnostics',
    ],
    useCases: [
      'Industrial PLC Communication',
      'SCADA Integration',
      'Real-time Data Acquisition',
      'Process Monitoring',
    ],
    troubleshooting: [
      'Verify network connectivity to Modbus device',
      'Check unit ID and addressing configuration',
      'Review security and encryption settings',
      'Monitor connection pool and performance metrics',
    ],
    documentationUrl: '/docs/nodes/communication/advanced-modbus-client',
    isCustomPage: false,
  },
  'advanced-opcua-client': {
    title: 'Advanced OPC-UA Client',
    description:
      'Industrial-grade OPC-UA client with enhanced security, subscription management, and real-time performance',
    keyParameters: [
      'Security Mode',
      'Subscription Settings',
      'Performance Mode',
      'Certificate Config',
      'Node Operations',
    ],
    useCases: [
      'Industrial Automation',
      'SCADA Systems',
      'Real-time Monitoring',
      'Secure Data Exchange',
    ],
    troubleshooting: [
      'Verify OPC-UA server endpoint and availability',
      'Check certificate configuration and security policies',
      'Review subscription and publishing interval settings',
      'Monitor connection pooling and performance metrics',
    ],
    documentationUrl: '/docs/nodes/communication/advanced-opcua-client',
    isCustomPage: false,
  },
  'advanced-ethernet-ip': {
    title: 'Advanced EtherNet/IP Client',
    description:
      'Industrial-grade EtherNet/IP client for Allen-Bradley PLCs with enhanced diagnostics and performance',
    keyParameters: [
      'PLC Model',
      'Performance Mode',
      'Tag Configuration',
      'Diagnostic Level',
      'Connection Settings',
    ],
    useCases: [
      'Allen-Bradley PLC Communication',
      'Factory Automation',
      'Process Control',
      'Data Acquisition',
    ],
    troubleshooting: [
      'Verify PLC host address and port configuration',
      'Check CPU slot number and connection path',
      'Review tag names and data type mappings',
      'Monitor diagnostic level and health checks',
    ],
    documentationUrl: '/docs/nodes/communication/advanced-ethernet-ip',
    isCustomPage: false,
  },
  // New ML Classification & Analysis nodes - AI Task Orchestrator Implementation
  'binary-classification': {
    title: 'Binary Classification',
    description: 'Advanced binary classification with multiple algorithms and ensemble methods',
    keyParameters: ['Algorithm Type', 'Target Column', 'Feature Columns', 'Validation Split', 'Hyperparameter Tuning'],
    useCases: ['Process fault detection', 'Quality control', 'Equipment monitoring', 'Safety classification'],
    troubleshooting: [
      'Check target column for binary values (0/1, True/False)',
      'Ensure sufficient training data (100+ samples)',
      'Verify feature-target correlation',
      'Enable class balancing for imbalanced data'
    ],
    documentationUrl: '/docs/nodes/binary-classification',
    isCustomPage: true,
  },
  'multiclass-classification': {
    title: 'Multi-Class Classification',
    description: 'Multi-category classification with advanced ensemble and balancing',
    keyParameters: ['Algorithm Types', 'Target Column', 'Class Names', 'Multi-Class Strategy', 'Ensemble Config'],
    useCases: ['Process state classification', 'Product categorization', 'Equipment health monitoring', 'Safety assessment'],
    troubleshooting: [
      'Ensure at least 3 classes in target column',
      'Enable class balancing for imbalanced classes',
      'Check for class confusion patterns in confusion matrix',
      'Use stratified validation for reliable performance'
    ],
    documentationUrl: '/docs/nodes/multiclass-classification',
    isCustomPage: true,
  },
  'distribution-analyzer': {
    title: 'Distribution Analyzer',
    description: 'Statistical distribution analysis with ML-enhanced pattern recognition',
    keyParameters: ['Data Columns', 'Distribution Types', 'Confidence Level', 'Outlier Handling', 'Goodness-of-Fit Tests'],
    useCases: ['Process characterization', 'Quality control setup', 'Alarm optimization', 'Equipment wear analysis'],
    troubleshooting: [
      'Ensure at least 30 data points for analysis',
      'Remove constant-value columns',
      'Check for outliers affecting distribution fits',
      'Try mixture modeling for multi-modal data'
    ],
    documentationUrl: '/docs/nodes/distribution-analyzer',
    isCustomPage: true,
  },
};

/**
 * NodeHelpIcon Component
 *
 * Provides contextual help for industrial nodes with tooltip and documentation linking
 */
export function NodeHelpIcon({
  nodeType,
  className,
  size = 'md',
  showTooltip = true,
  onHelpClick,
}: Readonly<NodeHelpIconProps>): React.JSX.Element {
  const [showTooltipContent, setShowTooltipContent] = useState(false);

  const helpContent = NODE_HELP_CONTENT[nodeType];

  const handleIconClick = useCallback(() => {
    onHelpClick?.(nodeType);

    // Open documentation in new tab if available
    if (helpContent.documentationUrl) {
      window.open(helpContent.documentationUrl, '_blank', 'noopener,noreferrer');
    }
  }, [nodeType, onHelpClick, helpContent.documentationUrl]);

  const handleMouseEnter = useCallback(() => {
    if (showTooltip) {
      setShowTooltipContent(true);
    }
  }, [showTooltip]);

  const handleMouseLeave = useCallback(() => {
    setShowTooltipContent(false);
  }, []);

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  return (
    <div className="relative inline-block">
      <button
        type="button"
        className={cn(
          'inline-flex items-center justify-center rounded-full',
          'text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400',
          'transition-colors duration-200',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1',
          className
        )}
        onClick={handleIconClick}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        aria-label={`Help for ${helpContent.title}`}
        title={`Get help for ${helpContent.title}`}
      >
        <CircleHelp className={cn(sizeClasses[size])} />
        {helpContent.documentationUrl && <ExternalLink className="w-2 h-2 ml-1 opacity-60" />}
      </button>

      {/* Tooltip Content */}
      {showTooltip && showTooltipContent && (
        <div
          className={cn(
            'absolute z-50 w-80 p-4 mt-2 bg-white dark:bg-gray-800',
            'border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg',
            'text-sm text-gray-900 dark:text-gray-100',
            'transform -translate-x-1/2 left-1/2',
            'animate-in fade-in-0 slide-in-from-top-2 duration-200'
          )}
          role="tooltip"
        >
          {/* Title */}
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-blue-600 dark:text-blue-400">{helpContent.title}</h4>
            {helpContent.isCustomPage && (
              <span className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                Custom
              </span>
            )}
          </div>

          {/* Description */}
          <p className="mb-3 text-gray-700 dark:text-gray-300">{helpContent.description}</p>

          {/* Key Parameters */}
          <div className="mb-3">
            <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-1">Key Parameters:</h5>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              {helpContent.keyParameters.slice(0, 3).map(param => (
                <li key={param} className="flex items-center">
                  <span className="w-1 h-1 bg-blue-500 rounded-full mr-2" />
                  {param}
                </li>
              ))}
              {helpContent.keyParameters.length > 3 && (
                <li className="text-gray-500 dark:text-gray-500">
                  +{helpContent.keyParameters.length - 3} more...
                </li>
              )}
            </ul>
          </div>

          {/* Use Cases */}
          <div className="mb-3">
            <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-1">Common Uses:</h5>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              {helpContent.useCases.slice(0, 2).map(useCase => (
                <li key={useCase} className="flex items-center">
                  <span className="w-1 h-1 bg-green-500 rounded-full mr-2" />
                  {useCase}
                </li>
              ))}
            </ul>
          </div>

          {/* Documentation Link */}
          {helpContent.documentationUrl && (
            <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                className="flex items-center text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors"
                onClick={handleIconClick}
              >
                <ExternalLink className="w-3 h-3 mr-1" />
                View Full Documentation
              </button>
            </div>
          )}

          {/* Tooltip Arrow */}
          <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
            <div className="w-4 h-4 bg-white dark:bg-gray-800 border-l border-t border-gray-200 dark:border-gray-700 rotate-45" />
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Hook for managing help content
 */
export function useNodeHelp(nodeType: IndustrialNodeType) {
  const helpContent = NODE_HELP_CONTENT[nodeType];

  const openDocumentation = useCallback(() => {
    if (helpContent.documentationUrl) {
      window.open(helpContent.documentationUrl, '_blank', 'noopener,noreferrer');
    }
  }, [helpContent.documentationUrl]);

  return {
    helpContent,
    openDocumentation,
    hasDocumentation: Boolean(helpContent.documentationUrl),
    isCustomPage: helpContent.isCustomPage,
  };
}

export type { NodeHelpContent, NodeHelpIconProps };
