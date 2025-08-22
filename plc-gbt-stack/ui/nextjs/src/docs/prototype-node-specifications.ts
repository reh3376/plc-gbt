#!/usr/bin/env tsx

/**
 * 🔬 Prototype Node Specifications - AI Task Orchestrator Implementation
 *
 * Comprehensive specifications for the 3 prototype nodes:
 * 1. PID Controller - Complex control logic with tuning parameters
 * 2. PostgreSQL Connector - Database integration patterns
 * 3. Math Function Creator - Custom equations with scientific calculator
 */

import type { NodeDocumentationSpec } from './node-documentation-system';
import { NODE_CATEGORIES } from './node-documentation-system';

// 🎛️ PID Controller - Most Complex Control Logic
export const PID_CONTROLLER_SPEC: NodeDocumentationSpec = {
  nodeType: 'pid-controller',
  category: NODE_CATEGORIES.plc_control,
  title: 'PID Controller',
  description:
    'Advanced Proportional-Integral-Derivative controller with auto-tuning, gain scheduling, and industrial safety features',
  version: '2.1.0',
  lastUpdated: '2025-01-15',

  parameters: [
    // Essential PID Parameters
    {
      name: 'processVariable',
      type: 'string',
      required: true,
      defaultValue: '',
      description: 'PLC address or signal source for the process variable (measured value)',
      validation: {
        pattern: '^[A-Za-z0-9_]+\\.[A-Za-z0-9_]+$',
        customRules: ['Must be valid PLC address format', 'Signal must be analog type'],
      },
      examples: ['DB1.PV_Temperature', 'MW100', 'AI_Channel_1'],
    },
    {
      name: 'setPoint',
      type: 'number',
      required: true,
      defaultValue: 0,
      description: 'Desired target value for the controlled process variable',
      range: { min: -9999, max: 9999, step: 0.01 },
      units: 'Engineering Units',
    },
    {
      name: 'controlOutput',
      type: 'string',
      required: true,
      defaultValue: '',
      description: 'PLC address for the controller output signal to actuator/final control element',
      validation: {
        pattern: '^[A-Za-z0-9_]+\\.[A-Za-z0-9_]+$',
      },
      examples: ['DB1.CV_ValvePosition', 'QW200', 'AO_Channel_1'],
    },

    // PID Tuning Parameters
    {
      name: 'proportionalGain',
      type: 'number',
      required: true,
      defaultValue: 1.0,
      description: 'Proportional gain (Kp) - determines immediate response to error',
      range: { min: 0.001, max: 1000, step: 0.001 },
      units: 'Dimensionless',
    },
    {
      name: 'integralTime',
      type: 'number',
      required: true,
      defaultValue: 60.0,
      description: 'Integral time constant (Ti) in seconds - eliminates steady-state error',
      range: { min: 0.1, max: 86400, step: 0.1 },
      units: 'seconds',
    },
    {
      name: 'derivativeTime',
      type: 'number',
      required: true,
      defaultValue: 15.0,
      description: 'Derivative time constant (Td) in seconds - provides anticipatory action',
      range: { min: 0, max: 3600, step: 0.1 },
      units: 'seconds',
    },

    // Advanced Configuration
    {
      name: 'controllerMode',
      type: 'enum',
      required: true,
      defaultValue: 'automatic',
      description: 'Operating mode of the PID controller',
      enumValues: ['automatic', 'manual', 'cascade', 'ratio', 'override'],
      examples: ['automatic', 'manual'],
    },
    {
      name: 'controlAction',
      type: 'enum',
      required: true,
      defaultValue: 'direct',
      description: 'Controller action type - direct (heating) or reverse (cooling)',
      enumValues: ['direct', 'reverse'],
    },
    {
      name: 'outputLimits',
      type: 'object',
      required: true,
      defaultValue: { min: 0, max: 100 },
      description: 'Output signal limits to prevent actuator damage and ensure safe operation',
    },
    {
      name: 'scanTime',
      type: 'number',
      required: false,
      defaultValue: 1000,
      description: 'Controller execution interval in milliseconds',
      range: { min: 100, max: 60000, step: 100 },
      units: 'milliseconds',
    },

    // Anti-Windup and Safety
    {
      name: 'antiWindupEnabled',
      type: 'boolean',
      required: false,
      defaultValue: true,
      description: 'Enable integral windup protection when output reaches limits',
    },
    {
      name: 'bumplessTransfer',
      type: 'boolean',
      required: false,
      defaultValue: true,
      description: 'Enable smooth transitions between manual and automatic modes',
    },
    {
      name: 'safetyLimits',
      type: 'object',
      required: false,
      defaultValue: { pvHigh: 1000, pvLow: -1000 },
      description: 'Safety limits for process variable - triggers alarms and protective actions',
    },

    // Auto-Tuning Features
    {
      name: 'autoTuneEnabled',
      type: 'boolean',
      required: false,
      defaultValue: false,
      description: 'Enable automatic PID parameter tuning using relay feedback method',
    },
    {
      name: 'tuningMethod',
      type: 'enum',
      required: false,
      defaultValue: 'ziegler-nichols',
      description: 'Auto-tuning algorithm selection',
      enumValues: ['ziegler-nichols', 'cohen-coon', 'lambda-tuning', 'imc', 'relay-feedback'],
    },
  ],

  examples: [
    {
      title: 'Temperature Control Loop',
      description: 'Basic temperature control for a heating process with anti-windup protection',
      useCase: 'Maintaining reactor temperature at 250°C using electric heater',
      configuration: {
        processVariable: 'DB10.Temperature_PV',
        setPoint: 250.0,
        controlOutput: 'DB10.Heater_Output',
        proportionalGain: 2.5,
        integralTime: 120.0,
        derivativeTime: 30.0,
        controllerMode: 'automatic',
        controlAction: 'direct',
        outputLimits: { min: 0, max: 100 },
        antiWindupEnabled: true,
        safetyLimits: { pvHigh: 300, pvLow: 0 },
      },
      expectedOutput: 'Smooth temperature control with <2°C deviation from setpoint',
      notes: [
        'Tune conservatively for safety in heating applications',
        'Monitor for thermal lag and adjust derivative time accordingly',
        'Implement temperature ramp limiting for large setpoint changes',
      ],
    },
    {
      title: 'Flow Control with Cascade Configuration',
      description: 'Flow rate control as inner loop in cascade control system',
      useCase: 'Precise flow control for chemical dosing system',
      configuration: {
        processVariable: 'DB20.Flow_PV',
        setPoint: 'DB20.Flow_SP_Remote',
        controlOutput: 'DB20.Valve_Position',
        proportionalGain: 1.8,
        integralTime: 8.0,
        derivativeTime: 2.0,
        controllerMode: 'cascade',
        controlAction: 'direct',
        outputLimits: { min: 5, max: 95 },
        scanTime: 500,
        bumplessTransfer: true,
      },
      expectedOutput: 'Fast flow response with minimal overshoot',
      notes: [
        'Faster tuning appropriate for inner cascade loop',
        'Reserve 5% valve travel for safety margin',
        'Use faster scan time for improved performance',
      ],
    },
  ],

  connections: {
    inputHandles: [
      {
        id: 'pv_input',
        label: 'Process Variable',
        dataType: 'analog',
        required: true,
        description: 'Real-time process variable measurement from sensors or other nodes',
      },
      {
        id: 'sp_input',
        label: 'Setpoint',
        dataType: 'analog',
        required: false,
        description: 'External setpoint input (optional - can use internal setpoint parameter)',
      },
      {
        id: 'mode_input',
        label: 'Mode Control',
        dataType: 'digital',
        required: false,
        description: 'External mode switching (Auto/Manual)',
      },
    ],
    outputHandles: [
      {
        id: 'cv_output',
        label: 'Control Variable',
        dataType: 'analog',
        required: true,
        description: 'Controller output signal to final control element',
      },
      {
        id: 'error_output',
        label: 'Control Error',
        dataType: 'analog',
        required: false,
        description: 'Current error value (SP - PV) for monitoring and cascade control',
      },
      {
        id: 'status_output',
        label: 'Controller Status',
        dataType: 'digital',
        required: false,
        description: 'Controller health and operating status',
      },
    ],
    connectionTests: [
      {
        name: 'PV Signal Validation',
        description: 'Verify process variable signal is valid and within expected range',
        procedure: [
          'Check PLC address accessibility',
          'Validate signal data type (analog)',
          'Verify signal range matches process limits',
          'Test signal update rate meets scan time requirements',
        ],
        expectedResult: 'PV signal updates consistently with valid analog values',
        troubleshooting: [
          'Verify PLC connection and communication',
          'Check signal scaling and engineering units',
          'Validate analog input module configuration',
        ],
      },
      {
        name: 'Output Signal Test',
        description: 'Test controller output signal reaches final control element',
        procedure: [
          'Set controller to manual mode',
          'Apply test output values (25%, 50%, 75%)',
          'Verify actuator responds proportionally',
          'Check output limiting functionality',
        ],
        expectedResult: 'Actuator responds smoothly to output changes within configured limits',
        troubleshooting: [
          'Check actuator power supply and wiring',
          'Verify output signal scaling matches actuator input range',
          'Test actuator mechanical operation',
        ],
      },
    ],
  },

  validation: [
    {
      id: 'tuning_stability',
      severity: 'error',
      condition: 'proportionalGain * (1/integralTime) > 10',
      message: 'PID tuning may cause instability - reduce gain or increase integral time',
      suggestion: 'Use conservative tuning or enable auto-tune feature',
    },
    {
      id: 'derivative_noise',
      severity: 'warning',
      condition: 'derivativeTime > integralTime/4',
      message: 'High derivative time may amplify measurement noise',
      suggestion: 'Consider using derivative filtering or reducing derivative time',
    },
    {
      id: 'output_range',
      severity: 'error',
      condition: 'outputLimits.min >= outputLimits.max',
      message: 'Invalid output limits - minimum must be less than maximum',
      suggestion: 'Set minimum output limit below maximum output limit',
    },
  ],

  overview: {
    purpose:
      'Industrial-grade PID controller for precise automatic control of process variables in manufacturing and process industries',
    keyFeatures: [
      'Classical PID Algorithm: Proportional, Integral, and Derivative control actions',
      'Auto-Tuning: Multiple tuning algorithms including Ziegler-Nichols and Cohen-Coon',
      'Safety Features: Anti-windup protection, output limiting, and process variable safety limits',
      'Operating Modes: Automatic, manual, cascade, ratio, and override control modes',
      'Industrial Integration: Direct PLC address connectivity with real-time communication',
      'Advanced Features: Gain scheduling, bumpless transfer, and feed-forward compensation',
    ],
    useCases: [
      'Temperature Control: Reactor heating, oven control, HVAC systems',
      'Flow Control: Chemical dosing, liquid transfer, gas flow regulation',
      'Pressure Control: Steam systems, hydraulic control, pneumatic systems',
      'Level Control: Tank filling, inventory management, surge control',
      'Speed Control: Motor drives, conveyor systems, fan speed regulation',
      'Composition Control: pH control, concentration control, blending systems',
    ],
    whenToUse: [
      'Continuous Process Control: When maintaining a variable at a constant setpoint',
      'Disturbance Rejection: When process is subject to external disturbances',
      'Precision Requirements: When tight control accuracy is required (<2% deviation)',
      'Safety Critical Applications: When process upsets could cause safety issues',
      'Cascade Control Systems: As inner or outer loop in multi-loop control strategies',
    ],
    industrialApplications: [
      'Chemical Processing: Reactor temperature and pressure control',
      'Oil & Gas: Pipeline pressure and flow control',
      'Power Generation: Steam temperature and pressure regulation',
      'Food & Beverage: Pasteurization temperature control',
      'Pharmaceutical: Critical process parameter control',
      'Water Treatment: pH and chemical dosing control',
    ],
  },

  configurationGuide: {
    quickStart: [
      'Drag PID Controller node from the control palette to the workflow canvas',
      'Connect the process variable input from sensor or measurement node',
      'Connect the control output to actuator or final control element node',
      'Double-click to open properties and configure PLC addresses',
      'Set initial PID parameters (start with Kp=1, Ti=60s, Td=15s)',
      'Configure output limits to match actuator range',
      'Enable anti-windup protection and safety limits',
      'Test in manual mode before switching to automatic',
    ],
    detailedSteps: [
      {
        step: 1,
        title: 'Process Variable Configuration',
        description: 'Configure the measurement input signal from the process',
        parameters: ['processVariable', 'pvSignalType', 'engineeringUnits'],
        codeExamples: [
          '{\n  "processVariable": "DB10.Temperature_PV",\n  "pvSignalType": "analog",\n  "engineeringUnits": "degC"\n}',
        ],
      },
      {
        step: 2,
        title: 'Control Output Setup',
        description: 'Configure the output signal to the final control element',
        parameters: ['controlOutput', 'outputLimits', 'outputSignalType'],
        codeExamples: [
          '{\n  "controlOutput": "DB10.Valve_CV",\n  "outputLimits": { "min": 0, "max": 100 },\n  "outputSignalType": "analog"\n}',
        ],
      },
      {
        step: 3,
        title: 'PID Parameter Tuning',
        description: 'Set initial PID parameters or enable auto-tuning',
        parameters: ['proportionalGain', 'integralTime', 'derivativeTime', 'autoTuneEnabled'],
        codeExamples: [
          '{\n  "proportionalGain": 2.0,\n  "integralTime": 120.0,\n  "derivativeTime": 30.0,\n  "autoTuneEnabled": false\n}',
        ],
      },
    ],
    bestPractices: [
      'Start with conservative tuning (low gain, long integral time) for safety',
      'Use auto-tuning only during planned maintenance windows',
      'Always configure safety limits and anti-windup protection',
      'Test manual mode operation before enabling automatic control',
      'Document tuning parameters and process conditions for future reference',
      'Monitor controller performance and retune periodically',
      'Use cascade control for improved performance in complex processes',
    ],
    commonMistakes: [
      'Setting derivative time too high - amplifies measurement noise',
      'Forgetting anti-windup protection - causes integral buildup during output saturation',
      'Incorrect control action (direct vs reverse) - causes positive feedback',
      'Inadequate output limits - can damage actuators or create unsafe conditions',
      'Poor signal quality - measurement noise degrades control performance',
      'Ignoring process dynamics - tuning without understanding the process response',
    ],
  },

  troubleshooting: {
    commonIssues: [
      {
        issue: 'Controller Oscillation',
        symptoms: [
          'Process variable oscillates around setpoint',
          'Control output swings rapidly',
          'System unstable',
        ],
        causes: [
          'Proportional gain too high',
          'Integral time too short',
          'Derivative time inappropriate',
          'Measurement noise',
        ],
        solutions: [
          'Reduce proportional gain by 50%',
          'Increase integral time (slower integral action)',
          'Reduce or eliminate derivative action',
          'Add measurement filtering',
          'Check for mechanical backlash in actuator',
        ],
        prevention: [
          'Use conservative initial tuning',
          'Perform step testing before tuning',
          'Monitor control loop performance',
        ],
      },
      {
        issue: 'Slow Response to Setpoint Changes',
        symptoms: [
          'Long time to reach setpoint',
          'Sluggish response',
          'Poor disturbance rejection',
        ],
        causes: [
          'Proportional gain too low',
          'Integral time too long',
          'Output limits too restrictive',
        ],
        solutions: [
          'Increase proportional gain gradually',
          'Decrease integral time (faster integral action)',
          'Check and adjust output limits',
          'Verify actuator is not saturated',
          'Consider cascade control for faster response',
        ],
      },
      {
        issue: 'Integral Windup',
        symptoms: [
          'Large overshoot after manual mode',
          'Slow recovery from disturbances',
          'Control output stuck at limits',
        ],
        causes: ['Anti-windup disabled', 'Output limits reached', 'Manual mode operation'],
        solutions: [
          'Enable anti-windup protection',
          'Verify output limits are appropriate',
          'Use bumpless transfer for mode switching',
          'Reset integral term when switching to automatic',
        ],
      },
    ],
    errorCodes: [
      {
        code: 'PID_001',
        message: 'Process variable signal lost',
        severity: 'critical',
        solution: 'Check PLC communication and sensor wiring',
      },
      {
        code: 'PID_002',
        message: 'Control output failed to respond',
        severity: 'error',
        solution: 'Verify actuator power supply and control signal integrity',
      },
      {
        code: 'PID_003',
        message: 'PID parameters out of valid range',
        severity: 'warning',
        solution: 'Review and correct PID tuning parameters',
      },
    ],
    diagnosticProcedures: [
      'Monitor process variable signal for dropouts or noise',
      'Check control output signal reaches actuator correctly',
      'Verify PID parameters are within recommended ranges',
      'Test controller response to manual output changes',
      'Analyze control loop performance using trending data',
    ],
  },

  relatedNodes: [
    'pid-auto-tuner',
    'cascade-controller',
    'feedforward-controller',
    'analog-input-node',
    'analog-output-node',
    'plc-input',
    'plc-output',
    'alarm-handler',
    'data-logger',
  ],

  externalResources: [
    {
      title: 'ISA-5.1: Instrumentation Symbols and Identification',
      url: 'https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa51',
      type: 'specification',
      description: 'Standard symbols for process control and instrumentation',
    },
    {
      title: 'PID Control Theory and Practice',
      url: 'https://controlguru.com/pid-control-theory-and-practice/',
      type: 'documentation',
      description: 'Comprehensive guide to PID controller theory and implementation',
    },
    {
      title: 'Advanced PID Control by Karl Astrom',
      url: 'https://www.cds.caltech.edu/~murray/amwiki/index.php/PID_Control',
      type: 'documentation',
      description: 'Academic reference on advanced PID control techniques',
    },
  ],

  templateCategory: 'plc_control',
};

// 🗄️ PostgreSQL Connector - Database Integration Patterns
export const POSTGRESQL_CONNECTOR_SPEC: NodeDocumentationSpec = {
  nodeType: 'postgresql-connector',
  category: NODE_CATEGORIES.data_sources,
  title: 'PostgreSQL Connector',
  description:
    'Enterprise-grade PostgreSQL database connector with connection pooling, transaction management, and industrial-strength reliability features',
  version: '2.0.0',
  lastUpdated: '2025-01-15',

  parameters: [
    // Connection Configuration
    {
      name: 'connectionString',
      type: 'string',
      required: true,
      defaultValue: 'postgresql://username:password@localhost:5432/database',
      description: 'PostgreSQL connection string with credentials and database information',
      validation: {
        pattern: '^postgresql://[^:]+:[^@]+@[^:/]+:[0-9]+/[^\\s]+$',
        customRules: ['Must be valid PostgreSQL connection URI format'],
      },
      examples: [
        'postgresql://plc_user:${SECURE_PASSWORD}@192.168.1.100:5432/process_data',
        'postgresql://historian:${SECURE_PASSWORD}@db.company.com:5432/plant_historian',
      ],
    },
    {
      name: 'connectionPool',
      type: 'object',
      required: false,
      defaultValue: { min: 2, max: 10, idleTimeout: 30000 },
      description:
        'Connection pooling configuration for optimal performance and resource management',
    },
    {
      name: 'ssl',
      type: 'object',
      required: false,
      defaultValue: { enabled: false, rejectUnauthorized: true },
      description: 'SSL/TLS encryption settings for secure database connections',
    },

    // Query Configuration
    {
      name: 'defaultQuery',
      type: 'string',
      required: false,
      defaultValue: 'SELECT NOW() as current_time',
      description: 'Default SQL query to execute when node is triggered',
      validation: {
        customRules: ['Must be valid SQL syntax', 'Read-only queries recommended for safety'],
      },
    },
    {
      name: 'queryTimeout',
      type: 'number',
      required: false,
      defaultValue: 30000,
      description: 'Maximum query execution time in milliseconds',
      range: { min: 1000, max: 300000, step: 1000 },
      units: 'milliseconds',
    },
    {
      name: 'transactionMode',
      type: 'enum',
      required: false,
      defaultValue: 'auto-commit',
      description: 'Transaction handling mode for data consistency',
      enumValues: ['auto-commit', 'manual', 'read-only', 'serializable'],
    },

    // Data Processing
    {
      name: 'resultFormat',
      type: 'enum',
      required: false,
      defaultValue: 'json',
      description: 'Format for query result data output',
      enumValues: ['json', 'csv', 'raw'],
    },
    {
      name: 'parameterized',
      type: 'boolean',
      required: false,
      defaultValue: true,
      description: 'Enable parameterized queries for SQL injection protection',
    },
    {
      name: 'batchSize',
      type: 'number',
      required: false,
      defaultValue: 1000,
      description: 'Maximum number of rows to process in a single batch',
      range: { min: 1, max: 100000, step: 1 },
      units: 'rows',
    },

    // Monitoring and Reliability
    {
      name: 'healthCheck',
      type: 'object',
      required: false,
      defaultValue: { enabled: true, interval: 60000, query: 'SELECT 1' },
      description: 'Database connection health monitoring configuration',
    },
    {
      name: 'retryPolicy',
      type: 'object',
      required: false,
      defaultValue: { maxRetries: 3, backoffMultiplier: 2, initialDelay: 1000 },
      description: 'Automatic retry configuration for failed operations',
    },
    {
      name: 'logging',
      type: 'object',
      required: false,
      defaultValue: { level: 'info', logQueries: false, logPerformance: true },
      description: 'Database operation logging and audit trail configuration',
    },
  ],

  examples: [
    {
      title: 'Process Historian Data Retrieval',
      description: 'Retrieve time-series process data for trending and analysis',
      useCase: 'Historical data analysis for process optimization',
      configuration: {
        connectionString: 'postgresql://historian:${SECURE_PASSWORD}@192.168.1.100:5432/plant_data',
        defaultQuery: `
          SELECT timestamp, tag_name, value, quality 
          FROM process_data 
          WHERE timestamp >= $1 AND timestamp <= $2 
          ORDER BY timestamp DESC`,
        connectionPool: { min: 5, max: 20, idleTimeout: 60000 },
        transactionMode: 'read-only',
        resultFormat: 'json',
        parameterized: true,
        batchSize: 5000,
        healthCheck: { enabled: true, interval: 30000 },
      },
      expectedOutput: 'JSON array of time-series data records',
      notes: [
        'Use parameterized queries with timestamp range for security',
        'Configure larger connection pool for high-frequency data retrieval',
        'Enable performance logging to monitor query execution times',
      ],
    },
    {
      title: 'Real-time Alarm Logging',
      description: 'Log process alarms and events to PostgreSQL database',
      useCase: 'Industrial alarm and event management system',
      configuration: {
        connectionString: 'postgresql://alarm_user:${SECURE_PASSWORD}@db.plant.com:5432/alarms',
        defaultQuery: `
          INSERT INTO alarm_events (timestamp, alarm_id, severity, description, acknowledged) 
          VALUES ($1, $2, $3, $4, false)`,
        connectionPool: { min: 2, max: 8, idleTimeout: 30000 },
        transactionMode: 'auto-commit',
        parameterized: true,
        ssl: { enabled: true, rejectUnauthorized: true },
        retryPolicy: { maxRetries: 5, backoffMultiplier: 1.5, initialDelay: 500 },
        logging: { level: 'info', logQueries: true, logPerformance: false },
      },
      expectedOutput: 'Confirmation of successful alarm record insertion',
      notes: [
        'Use SSL encryption for sensitive alarm data',
        'Configure aggressive retry policy for critical alarm logging',
        'Enable query logging for audit trail compliance',
      ],
    },
  ],

  connections: {
    inputHandles: [
      {
        id: 'query_input',
        label: 'SQL Query',
        dataType: 'string',
        required: false,
        description: 'Dynamic SQL query input from other nodes',
      },
      {
        id: 'parameters_input',
        label: 'Query Parameters',
        dataType: 'object',
        required: false,
        description: 'Parameters for parameterized SQL queries',
      },
      {
        id: 'trigger_input',
        label: 'Execution Trigger',
        dataType: 'digital',
        required: false,
        description: 'Signal to trigger query execution',
      },
    ],
    outputHandles: [
      {
        id: 'result_output',
        label: 'Query Results',
        dataType: 'object',
        required: true,
        description: 'Query execution results in configured format',
      },
      {
        id: 'status_output',
        label: 'Connection Status',
        dataType: 'object',
        required: false,
        description: 'Database connection and operation status information',
      },
      {
        id: 'error_output',
        label: 'Error Information',
        dataType: 'string',
        required: false,
        description: 'Detailed error information for failed operations',
      },
    ],
    connectionTests: [
      {
        name: 'Database Connectivity Test',
        description: 'Verify PostgreSQL server connectivity and authentication',
        procedure: [
          'Parse and validate connection string format',
          'Attempt initial connection to PostgreSQL server',
          'Verify authentication credentials',
          'Test database access permissions',
          'Validate SSL configuration if enabled',
        ],
        expectedResult: 'Successful connection with valid authentication',
        troubleshooting: [
          'Verify PostgreSQL server is running and accessible',
          'Check network connectivity and firewall settings',
          'Validate credentials and database permissions',
          'Review SSL certificate configuration',
        ],
      },
      {
        name: 'Query Execution Test',
        description: 'Test SQL query execution and result retrieval',
        procedure: [
          'Execute simple test query (SELECT 1)',
          'Verify query results are returned correctly',
          'Test parameterized query functionality',
          'Validate result format conversion',
          'Check query timeout handling',
        ],
        expectedResult: 'Query executes successfully with expected results',
        troubleshooting: [
          'Check SQL syntax and database schema',
          'Verify table and column permissions',
          'Review query timeout settings',
          'Validate parameter binding',
        ],
      },
    ],
  },

  validation: [
    {
      id: 'connection_string_format',
      severity: 'error',
      condition: '!connectionString.startsWith("postgresql://")',
      message: 'Invalid connection string format - must use PostgreSQL URI scheme',
      suggestion: 'Use format: postgresql://username:password@host:port/database',
    },
    {
      id: 'pool_configuration',
      severity: 'warning',
      condition: 'connectionPool.max < connectionPool.min',
      message: 'Invalid connection pool configuration - maximum must be greater than minimum',
      suggestion: 'Set maximum pool size greater than minimum pool size',
    },
    {
      id: 'query_security',
      severity: 'warning',
      condition:
        'defaultQuery.toUpperCase().includes("DELETE") || defaultQuery.toUpperCase().includes("DROP")',
      message: 'Potentially dangerous SQL operation detected',
      suggestion: 'Use caution with destructive SQL operations - consider read-only mode',
    },
  ],

  overview: {
    purpose:
      'Enterprise-grade PostgreSQL database connector providing reliable, secure, and high-performance database integration for industrial process data management',
    keyFeatures: [
      'Connection Pooling: Efficient resource management with configurable pool sizes',
      'Transaction Management: ACID compliance with multiple transaction modes',
      'Security: SSL/TLS encryption, parameterized queries, and SQL injection protection',
      'Reliability: Automatic reconnection, health monitoring, and retry policies',
      'Performance: Query optimization, batch processing, and connection reuse',
      'Monitoring: Comprehensive logging, performance metrics, and health checks',
    ],
    useCases: [
      'Process Historian: Long-term storage of time-series process data',
      'Alarm Management: Logging and tracking of process alarms and events',
      'Recipe Management: Storage and retrieval of production recipes and procedures',
      'Quality Data: Laboratory results, test data, and quality measurements',
      'Asset Management: Equipment information, maintenance records, and inventory',
      'Reporting: Data source for reports, dashboards, and business intelligence',
    ],
    whenToUse: [
      'Large-scale Data Storage: When handling thousands or millions of data points',
      'Complex Queries: When advanced SQL capabilities are needed for data analysis',
      'ACID Compliance: When data integrity and consistency are critical',
      'Multi-user Access: When multiple systems need concurrent database access',
      'Enterprise Integration: When integrating with existing enterprise database systems',
    ],
    industrialApplications: [
      'Manufacturing Execution Systems (MES): Production data and tracking',
      'SCADA Systems: Real-time and historical data storage',
      'Laboratory Information Systems (LIMS): Test results and quality data',
      'Asset Performance Management: Equipment performance and maintenance data',
      'Energy Management: Power consumption, demand, and optimization data',
      'Environmental Monitoring: Emissions, waste, and compliance data',
    ],
  },

  configurationGuide: {
    quickStart: [
      'Drag PostgreSQL Connector from data sources palette',
      'Configure connection string with database credentials and server information',
      'Set up connection pooling for your expected load',
      'Define your SQL query or connect dynamic query input',
      'Configure SSL encryption if required by security policy',
      'Test database connectivity using the built-in connection test',
      'Set up health monitoring and retry policies for production use',
      'Connect output to downstream nodes for data processing',
    ],
    detailedSteps: [
      {
        step: 1,
        title: 'Database Connection Setup',
        description: 'Configure secure connection to PostgreSQL database server',
        parameters: ['connectionString', 'ssl', 'connectionPool'],
        codeExamples: [
          '{\n  "connectionString": "postgresql://plc_user:${SECURE_PASSWORD}@192.168.1.100:5432/process_db",\n  "ssl": { "enabled": true, "rejectUnauthorized": true },\n  "connectionPool": { "min": 5, "max": 20, "idleTimeout": 60000 }\n}',
        ],
      },
      {
        step: 2,
        title: 'Query Configuration',
        description: 'Define SQL queries and execution parameters',
        parameters: ['defaultQuery', 'parameterized', 'queryTimeout', 'transactionMode'],
        codeExamples: [
          '{\n  "defaultQuery": "SELECT * FROM process_data WHERE timestamp >= $1",\n  "parameterized": true,\n  "queryTimeout": 30000,\n  "transactionMode": "read-only"\n}',
        ],
      },
    ],
    bestPractices: [
      'Always use parameterized queries to prevent SQL injection attacks',
      'Configure appropriate connection pool sizes based on expected load',
      'Enable SSL encryption for production database connections',
      'Use read-only transaction mode when only querying data',
      'Implement proper error handling and retry policies',
      'Monitor connection pool usage and adjust sizes as needed',
      'Use database indexes on frequently queried columns',
    ],
    commonMistakes: [
      'Hardcoding credentials in connection strings - use secure credential storage',
      'Not using connection pooling - leads to performance problems',
      'Ignoring SQL injection risks - always use parameterized queries',
      'Setting query timeouts too low - may cause premature failures',
      'Not handling connection failures - implement proper retry logic',
      'Overlooking SSL requirements - may violate security policies',
    ],
  },

  troubleshooting: {
    commonIssues: [
      {
        issue: 'Connection Failed',
        symptoms: ['Unable to connect to database', 'Authentication errors', 'Network timeouts'],
        causes: [
          'Incorrect connection string',
          'Database server down',
          'Network connectivity issues',
          'Authentication failure',
        ],
        solutions: [
          'Verify PostgreSQL server is running and accepting connections',
          'Check connection string format and credentials',
          'Test network connectivity using ping or telnet',
          'Verify firewall and security group settings',
          'Check PostgreSQL pg_hba.conf authentication configuration',
        ],
      },
      {
        issue: 'Query Performance Issues',
        symptoms: ['Slow query execution', 'Query timeouts', 'High CPU usage'],
        causes: ['Missing indexes', 'Complex queries', 'Large result sets', 'Database locks'],
        solutions: [
          'Add indexes on frequently queried columns',
          'Optimize SQL queries and reduce complexity',
          'Implement result pagination for large datasets',
          'Monitor and resolve database lock contention',
          'Consider query plan analysis and optimization',
        ],
      },
    ],
    errorCodes: [
      {
        code: 'PG_001',
        message: 'Connection timeout',
        severity: 'error',
        solution: 'Check network connectivity and database server status',
      },
      {
        code: 'PG_002',
        message: 'Authentication failed',
        severity: 'error',
        solution: 'Verify database credentials and user permissions',
      },
      {
        code: 'PG_003',
        message: 'SQL syntax error',
        severity: 'error',
        solution: 'Review and correct SQL query syntax',
      },
    ],
    diagnosticProcedures: [
      'Test database connectivity using external tools (psql, pgAdmin)',
      'Monitor connection pool status and resource usage',
      'Analyze slow query logs for performance bottlenecks',
      'Check PostgreSQL server logs for error messages',
      'Verify database permissions and access rights',
    ],
  },

  relatedNodes: [
    'csv-dataset-creator',
    'data-cleaner',
    'dashboard-generator',
    'kpi-calculator',
    'alarm-handler',
    'redis-connector',
    'neo4j-connector',
  ],

  externalResources: [
    {
      title: 'PostgreSQL Official Documentation',
      url: 'https://www.postgresql.org/docs/',
      type: 'documentation',
      description: 'Comprehensive PostgreSQL documentation and reference',
    },
    {
      title: 'PostgreSQL Connection Pooling with pgbouncer',
      url: 'https://pgbouncer.github.io/',
      type: 'documentation',
      description: 'Connection pooling solution for PostgreSQL',
    },
    {
      title: 'PostgreSQL Performance Tuning',
      url: 'https://wiki.postgresql.org/wiki/Performance_Optimization',
      type: 'documentation',
      description: 'Performance optimization guides and best practices',
    },
  ],

  templateCategory: 'data_sources',
};

// 🧮 Math Function Creator - Custom Equations with Scientific Calculator
export const MATH_FUNCTION_CREATOR_SPEC: NodeDocumentationSpec = {
  nodeType: 'math-function-creator',
  category: NODE_CATEGORIES.data_processing,
  title: 'Math Function Creator',
  description:
    'Advanced mathematical function builder with scientific calculator, custom equation editor, and comprehensive mathematical operation support for process calculations',
  version: '1.5.0',
  lastUpdated: '2025-01-15',

  parameters: [
    // Function Definition
    {
      name: 'functionName',
      type: 'string',
      required: true,
      defaultValue: 'CustomFunction',
      description: 'Descriptive name for the mathematical function',
      validation: {
        pattern: '^[A-Za-z][A-Za-z0-9_]*$',
        customRules: ['Must start with letter', 'No spaces or special characters'],
      },
      examples: ['TemperatureCompensation', 'FlowCalculation', 'PressureDrop'],
    },
    {
      name: 'equation',
      type: 'string',
      required: true,
      defaultValue: 'x',
      description: 'Mathematical equation using standard mathematical notation and functions',
      validation: {
        customRules: [
          'Must be valid mathematical expression',
          'Variables must be defined in inputs',
        ],
      },
      examples: [
        'sqrt(x^2 + y^2)',
        'exp(-t/tau) * sin(2*pi*f*t)',
        '(P1 - P2) * K * sqrt(1 - (d/D)^4)',
      ],
    },
    {
      name: 'variables',
      type: 'array',
      required: true,
      defaultValue: ['x'],
      description: 'List of input variables used in the equation',
      examples: ['["x"]', '["x", "y", "z"]', '["pressure", "temperature", "flow"]'],
    },

    // Scientific Calculator Integration
    {
      name: 'calculatorEnabled',
      type: 'boolean',
      required: false,
      defaultValue: true,
      description: 'Enable integrated scientific calculator for equation development and testing',
    },
    {
      name: 'calculatorMode',
      type: 'enum',
      required: false,
      defaultValue: 'scientific',
      description: 'Calculator operation mode',
      enumValues: ['basic', 'scientific', 'engineering', 'programmer'],
    },
    {
      name: 'angleMode',
      type: 'enum',
      required: false,
      defaultValue: 'radians',
      description: 'Angle measurement mode for trigonometric functions',
      enumValues: ['radians', 'degrees', 'gradians'],
    },

    // Function Validation and Testing
    {
      name: 'domainLimits',
      type: 'object',
      required: false,
      defaultValue: {},
      description: 'Input variable domain restrictions and validation limits',
    },
    {
      name: 'rangeValidation',
      type: 'object',
      required: false,
      defaultValue: { enabled: false },
      description: 'Output range validation and limiting configuration',
    },
    {
      name: 'testCases',
      type: 'array',
      required: false,
      defaultValue: [],
      description: 'Test cases for function validation with expected outputs',
    },

    // Advanced Mathematical Features
    {
      name: 'precision',
      type: 'enum',
      required: false,
      defaultValue: 'double',
      description: 'Numerical precision for calculations',
      enumValues: ['single', 'double', 'extended', 'arbitrary'],
    },
    {
      name: 'customConstants',
      type: 'object',
      required: false,
      defaultValue: {},
      description: 'User-defined mathematical constants for use in equations',
    },
    {
      name: 'unitConversion',
      type: 'object',
      required: false,
      defaultValue: { enabled: false },
      description: 'Automatic unit conversion and dimensional analysis',
    },

    // Error Handling and Safety
    {
      name: 'errorHandling',
      type: 'enum',
      required: false,
      defaultValue: 'strict',
      description: 'Error handling mode for mathematical operations',
      enumValues: ['strict', 'permissive', 'custom'],
    },
    {
      name: 'divisionByZeroAction',
      type: 'enum',
      required: false,
      defaultValue: 'error',
      description: 'Action when division by zero is encountered',
      enumValues: ['error', 'infinity', 'nan', 'custom_value'],
    },
    {
      name: 'overflowProtection',
      type: 'boolean',
      required: false,
      defaultValue: true,
      description: 'Enable protection against numerical overflow and underflow',
    },
  ],

  examples: [
    {
      title: 'Orifice Plate Flow Calculation',
      description:
        'Calculate volumetric flow rate through an orifice plate using differential pressure',
      useCase: 'Industrial flow measurement in process plants',
      configuration: {
        functionName: 'OrificeFlowCalculation',
        equation: 'Cd * A * sqrt((2 * deltaP * gc) / (rho * (1 - beta^4)))',
        variables: ['Cd', 'A', 'deltaP', 'rho', 'beta', 'gc'],
        customConstants: {
          gc: 32.174, // gravitational constant
          pi: 3.14159265359,
        },
        domainLimits: {
          deltaP: { min: 0, max: 1000 },
          rho: { min: 0.1, max: 1000 },
          beta: { min: 0.1, max: 0.8 },
          Cd: { min: 0.5, max: 1.0 },
        },
        unitConversion: {
          enabled: true,
          inputUnits: { deltaP: 'psi', rho: 'lb/ft3' },
          outputUnit: 'ft3/min',
        },
        testCases: [
          {
            inputs: { Cd: 0.61, A: 0.785, deltaP: 10, rho: 62.4, beta: 0.5 },
            expected: 156.2,
            tolerance: 0.1,
          },
        ],
      },
      expectedOutput: 'Calculated volumetric flow rate with unit conversion',
      notes: [
        'Discharge coefficient (Cd) typically ranges from 0.6-0.65 for sharp-edged orifices',
        'Beta ratio should be between 0.1-0.8 for accurate results',
        'Include gravitational constant (gc) for proper unit consistency',
      ],
    },
    {
      title: 'Temperature Compensation Formula',
      description: 'Compensate sensor readings for temperature effects using polynomial correction',
      useCase: 'Sensor calibration and temperature compensation in measurement systems',
      configuration: {
        functionName: 'TemperatureCompensation',
        equation: 'rawValue * (1 + a1*(T - Tref) + a2*(T - Tref)^2 + a3*(T - Tref)^3)',
        variables: ['rawValue', 'T', 'Tref', 'a1', 'a2', 'a3'],
        customConstants: {
          Tref: 25.0, // Reference temperature in Celsius
        },
        domainLimits: {
          T: { min: -40, max: 150 },
          rawValue: { min: 0, max: 10000 },
        },
        rangeValidation: {
          enabled: true,
          min: -99999,
          max: 99999,
          action: 'clamp',
        },
        precision: 'double',
        testCases: [
          {
            inputs: { rawValue: 100, T: 50, a1: 0.002, a2: -0.00001, a3: 0 },
            expected: 104.9875,
            tolerance: 0.001,
          },
        ],
      },
      expectedOutput: 'Temperature-compensated measurement value',
      notes: [
        'Polynomial coefficients (a1, a2, a3) must be determined from calibration data',
        'Reference temperature (Tref) should match calibration conditions',
        'Higher-order terms may be needed for wide temperature ranges',
      ],
    },
    {
      title: 'PID Output Calculation with Feedforward',
      description: 'Custom PID controller output with feedforward compensation',
      useCase: 'Advanced process control with feedforward action',
      configuration: {
        functionName: 'PIDwithFeedforward',
        equation: 'Kp*error + Ki*integral + Kd*derivative + Kf*feedforward',
        variables: ['error', 'integral', 'derivative', 'feedforward', 'Kp', 'Ki', 'Kd', 'Kf'],
        domainLimits: {
          Kp: { min: 0, max: 100 },
          Ki: { min: 0, max: 10 },
          Kd: { min: 0, max: 100 },
          Kf: { min: 0, max: 10 },
        },
        rangeValidation: {
          enabled: true,
          min: 0,
          max: 100,
          action: 'clamp',
        },
        calculatorEnabled: true,
        calculatorMode: 'engineering',
      },
      expectedOutput: 'Combined PID and feedforward control output',
      notes: [
        'Feedforward gain (Kf) should be tuned based on process dynamics',
        'Output limiting prevents actuator damage and windup',
        'Consider derivative filtering for noisy process variables',
      ],
    },
  ],

  connections: {
    inputHandles: [
      {
        id: 'variable_inputs',
        label: 'Function Variables',
        dataType: 'object',
        required: true,
        description: 'Input values for all variables defined in the mathematical equation',
      },
      {
        id: 'parameter_inputs',
        label: 'Function Parameters',
        dataType: 'object',
        required: false,
        description: 'Optional parameter values that override default constants',
      },
      {
        id: 'trigger_input',
        label: 'Calculate Trigger',
        dataType: 'digital',
        required: false,
        description: 'Signal to trigger function calculation',
      },
    ],
    outputHandles: [
      {
        id: 'result_output',
        label: 'Function Result',
        dataType: 'number',
        required: true,
        description: 'Calculated result of the mathematical function',
      },
      {
        id: 'intermediate_outputs',
        label: 'Intermediate Values',
        dataType: 'object',
        required: false,
        description: 'Intermediate calculation values for debugging and analysis',
      },
      {
        id: 'validation_output',
        label: 'Validation Status',
        dataType: 'object',
        required: false,
        description: 'Input validation and domain checking results',
      },
    ],
    connectionTests: [
      {
        name: 'Equation Syntax Validation',
        description: 'Verify mathematical equation syntax and variable definitions',
        procedure: [
          'Parse equation syntax using mathematical expression parser',
          'Validate all variables are defined in the variables list',
          'Check for undefined functions or operators',
          'Verify parentheses and operator precedence',
          'Test with sample input values',
        ],
        expectedResult: 'Equation parses successfully and evaluates without errors',
        troubleshooting: [
          'Check equation syntax for mathematical operators and functions',
          'Verify all variables used in equation are defined in variables list',
          'Review parentheses placement and operator precedence',
          'Test equation with known input values',
        ],
      },
      {
        name: 'Numerical Accuracy Test',
        description: 'Validate calculation accuracy against known test cases',
        procedure: [
          'Execute function with predefined test cases',
          'Compare results against expected values',
          'Check numerical precision and rounding',
          'Verify handling of edge cases (zero, infinity, NaN)',
          'Test domain validation and range limiting',
        ],
        expectedResult: 'All test cases pass within specified tolerance',
        troubleshooting: [
          'Review test case expected values and tolerance settings',
          'Check precision settings for numerical calculations',
          'Verify domain limits and range validation configuration',
          'Test with simpler equations to isolate issues',
        ],
      },
    ],
  },

  validation: [
    {
      id: 'equation_syntax',
      severity: 'error',
      condition: 'equation contains undefined variables or functions',
      message: 'Mathematical equation contains syntax errors or undefined elements',
      suggestion: 'Verify equation syntax and ensure all variables are defined',
    },
    {
      id: 'variable_definition',
      severity: 'error',
      condition: 'equation variables not in variables array',
      message: 'Equation uses variables not defined in the variables list',
      suggestion: 'Add all equation variables to the variables list',
    },
    {
      id: 'domain_consistency',
      severity: 'warning',
      condition: 'domainLimits defined for non-existent variables',
      message: 'Domain limits specified for undefined variables',
      suggestion: 'Remove unused domain limits or add missing variables',
    },
    {
      id: 'test_case_coverage',
      severity: 'info',
      condition: 'testCases.length === 0',
      message: 'No test cases defined for function validation',
      suggestion: 'Add test cases to verify function correctness',
    },
  ],

  overview: {
    purpose:
      'Advanced mathematical function creator enabling custom equation development with integrated scientific calculator, comprehensive validation, and industrial-grade numerical processing capabilities',
    keyFeatures: [
      'Scientific Calculator: Integrated calculator with scientific, engineering, and programming modes',
      'Custom Equations: Support for complex mathematical expressions with multiple variables',
      'Function Validation: Comprehensive testing framework with domain checking and test cases',
      'Unit Conversion: Automatic unit conversion and dimensional analysis capabilities',
      'High Precision: Multiple precision modes including arbitrary precision arithmetic',
      'Error Handling: Robust error handling with configurable responses to mathematical exceptions',
      'Industrial Integration: Seamless integration with process control and data acquisition systems',
    ],
    useCases: [
      'Process Calculations: Custom engineering calculations for process optimization',
      'Sensor Compensation: Temperature, pressure, and linearity compensation formulas',
      'Control Algorithms: Custom control law implementation and advanced control strategies',
      'Data Processing: Mathematical transformations and signal processing functions',
      'Performance Metrics: Custom KPI and efficiency calculations',
      'Quality Control: Statistical calculations and quality metrics computation',
    ],
    whenToUse: [
      'Complex Calculations: When standard math functions are insufficient',
      'Custom Algorithms: Implementing proprietary or specialized mathematical models',
      'Multi-variable Functions: When calculations involve multiple input parameters',
      'Precision Requirements: When high numerical accuracy is critical',
      'Unit Conversions: When automatic unit conversion is needed',
      'Validation Needs: When mathematical accuracy must be verified with test cases',
    ],
    industrialApplications: [
      'Chemical Engineering: Reaction kinetics, thermodynamic calculations, mass transfer',
      'Mechanical Systems: Stress analysis, vibration analysis, fluid dynamics',
      'Electrical Power: Load calculations, power factor correction, harmonics analysis',
      'Process Control: Advanced control algorithms, optimization functions',
      'Quality Assurance: Statistical process control, capability studies',
      'Environmental: Emissions calculations, environmental impact assessments',
    ],
  },

  configurationGuide: {
    quickStart: [
      'Drag Math Function Creator from data processing palette',
      'Enter descriptive function name and mathematical equation',
      'Define all variables used in the equation',
      'Enable scientific calculator for equation development and testing',
      'Configure domain limits to ensure safe input ranges',
      'Add test cases to validate function accuracy',
      'Connect input nodes providing variable values',
      'Connect output to downstream calculation or control nodes',
    ],
    detailedSteps: [
      {
        step: 1,
        title: 'Function Definition',
        description: 'Define the mathematical function name and equation',
        parameters: ['functionName', 'equation', 'variables'],
        codeExamples: [
          '{\n  "functionName": "FlowCalculation",\n  "equation": "Cv * sqrt(deltaP / SG)",\n  "variables": ["Cv", "deltaP", "SG"]\n}',
        ],
      },
      {
        step: 2,
        title: 'Calculator Integration',
        description: 'Configure the integrated scientific calculator',
        parameters: ['calculatorEnabled', 'calculatorMode', 'angleMode'],
        codeExamples: [
          '{\n  "calculatorEnabled": true,\n  "calculatorMode": "scientific",\n  "angleMode": "radians"\n}',
        ],
      },
      {
        step: 3,
        title: 'Validation Setup',
        description: 'Configure domain limits and test cases for validation',
        parameters: ['domainLimits', 'testCases', 'rangeValidation'],
        codeExamples: [
          '{\n  "domainLimits": { "deltaP": { "min": 0, "max": 1000 } },\n  "testCases": [{ "inputs": {"Cv": 1.0, "deltaP": 100, "SG": 1.0}, "expected": 10.0 }]\n}',
        ],
      },
    ],
    bestPractices: [
      'Use descriptive function names that indicate the calculation purpose',
      'Define comprehensive test cases covering normal and edge case scenarios',
      'Set appropriate domain limits to prevent invalid inputs',
      'Use the scientific calculator to validate equations before deployment',
      'Configure proper error handling for division by zero and overflow conditions',
      'Document equation sources and assumptions for future reference',
      'Test functions with real process data before production use',
    ],
    commonMistakes: [
      'Forgetting to define all variables used in the equation',
      'Not setting domain limits leading to invalid calculations',
      'Using incorrect mathematical operator precedence',
      'Ignoring unit consistency in multi-variable equations',
      'Not testing edge cases like zero and negative inputs',
      'Overlooking numerical precision requirements for critical calculations',
    ],
  },

  troubleshooting: {
    commonIssues: [
      {
        issue: 'Equation Parsing Error',
        symptoms: [
          'Function fails to evaluate',
          'Syntax error messages',
          'Invalid operator errors',
        ],
        causes: [
          'Incorrect mathematical syntax',
          'Undefined variables',
          'Unsupported functions',
          'Mismatched parentheses',
        ],
        solutions: [
          'Verify equation syntax using the scientific calculator',
          'Check that all variables are defined in the variables list',
          'Review mathematical operator usage and precedence',
          'Validate parentheses placement and matching',
          'Test equation components individually',
        ],
      },
      {
        issue: 'Numerical Overflow or Underflow',
        symptoms: [
          'Results show infinity or NaN',
          'Unexpected very large or small numbers',
          'Calculation errors',
        ],
        causes: [
          'Input values too large or small',
          'Mathematical operations causing overflow',
          'Division by very small numbers',
        ],
        solutions: [
          'Enable overflow protection in configuration',
          'Set appropriate domain limits for input variables',
          'Review mathematical operations for potential overflow conditions',
          'Consider using higher precision arithmetic mode',
          'Implement result range validation and clamping',
        ],
      },
      {
        issue: 'Inaccurate Results',
        symptoms: [
          'Results differ from expected values',
          'Test cases fail',
          'Inconsistent calculations',
        ],
        causes: [
          'Incorrect equation formulation',
          'Precision limitations',
          'Unit conversion errors',
          'Input data quality issues',
        ],
        solutions: [
          'Verify equation against reference sources or documentation',
          'Increase numerical precision setting if needed',
          'Check unit conversion configuration and consistency',
          'Validate input data quality and ranges',
          'Add more comprehensive test cases to identify issues',
        ],
      },
    ],
    errorCodes: [
      {
        code: 'MATH_001',
        message: 'Equation syntax error',
        severity: 'error',
        solution: 'Review and correct mathematical equation syntax',
      },
      {
        code: 'MATH_002',
        message: 'Undefined variable in equation',
        severity: 'error',
        solution: 'Add missing variables to the variables list',
      },
      {
        code: 'MATH_003',
        message: 'Division by zero detected',
        severity: 'warning',
        solution: 'Check input values and configure division by zero handling',
      },
      {
        code: 'MATH_004',
        message: 'Input value outside domain limits',
        severity: 'warning',
        solution: 'Verify input values are within configured domain limits',
      },
    ],
    diagnosticProcedures: [
      'Test equation syntax using the integrated scientific calculator',
      'Verify all variables are properly defined and connected',
      'Check test cases execution and compare results with expected values',
      'Monitor numerical precision and overflow protection settings',
      'Validate input data ranges against configured domain limits',
    ],
  },

  relatedNodes: [
    'data-cleaner',
    'feature-engineer',
    'time-series-processor',
    'pid-controller',
    'performance-metrics',
    'kpi-calculator',
    'dashboard-generator',
  ],

  externalResources: [
    {
      title: 'Mathematical Expression Evaluation',
      url: 'https://mathjs.org/docs/expressions/syntax.html',
      type: 'documentation',
      description: 'Comprehensive guide to mathematical expression syntax',
    },
    {
      title: 'Engineering Mathematics Handbook',
      url: 'https://www.engineeringtoolbox.com/',
      type: 'documentation',
      description: 'Reference for engineering calculations and formulas',
    },
    {
      title: 'Numerical Methods and Scientific Computing',
      url: 'https://numerical.recipes/',
      type: 'documentation',
      description: 'Advanced numerical methods and computational techniques',
    },
  ],

  templateCategory: 'data_processing',
  customSections: [
    {
      id: 'scientific_calculator_integration',
      title: 'Scientific Calculator Integration',
      content: `The integrated scientific calculator provides comprehensive mathematical computation capabilities directly within the node configuration interface. This powerful tool enables equation development, testing, and validation without external software.

### Calculator Features

**Scientific Mode:**
- Basic arithmetic operations (+, -, *, /, ^)
- Trigonometric functions (sin, cos, tan, asin, acos, atan)
- Logarithmic and exponential functions (log, ln, exp, pow)
- Statistical functions (mean, std, var, min, max)
- Constants (pi, e, golden ratio, etc.)

**Engineering Mode:**
- Engineering notation display (1.23E+6)
- Unit conversion capabilities
- Complex number operations
- Matrix and vector operations
- Statistical analysis functions

**Advanced Features:**
- Custom constant definition
- Function graphing and visualization
- Equation solving and root finding
- Numerical integration and differentiation
- Matrix operations and linear algebra

### Equation Development Workflow

1. **Define Variables**: Start by identifying all input variables
2. **Build Equation**: Use calculator to develop and test equation components
3. **Validate Syntax**: Verify equation syntax and mathematical correctness
4. **Test with Data**: Execute with sample data to verify expected results
5. **Configure Validation**: Set up domain limits and test cases
6. **Deploy Function**: Connect to workflow and begin production use

### Calculator Interface

The scientific calculator modal provides:
- **Expression Input**: Multi-line equation editor with syntax highlighting
- **Variable Panel**: Define and test with different variable values
- **Function Library**: Browse available mathematical functions and operators
- **Graph Visualization**: Plot functions to verify mathematical behavior
- **Test Execution**: Run calculations with different input combinations
- **Result Analysis**: Analyze numerical accuracy and precision

This integration eliminates the need for external mathematical software and provides a seamless development experience within the PLC-GBT environment.`,
      order: 1,
    },
  ],
};

export const PROTOTYPE_SPECIFICATIONS = {
  PID_CONTROLLER_SPEC,
  POSTGRESQL_CONNECTOR_SPEC,
  MATH_FUNCTION_CREATOR_SPEC,
} as const;
