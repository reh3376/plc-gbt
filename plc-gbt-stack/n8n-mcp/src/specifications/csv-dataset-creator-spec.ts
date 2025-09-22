/**
 * CSV Dataset Creator N8N Node Specification
 *
 * Based on 7-Phase Collaborative Development Session
 * Implements hybrid architecture with base core + 4 specialized modes
 *
 * AI Task Orchestrator TypeScript Methodology Compliant
 */

import {
  IndustrialNodeSpec,
  IndustrialParameter,
  IndustrialPhaseSpec,
  SpecializedMode,
  ValidationRule,
} from '../templates/industrial-node-generator';

/**
 * CSV Dataset Creator Industrial Node Specification
 * Proof-of-concept for N8N migration approach
 */
export const csvDatasetCreatorSpec: IndustrialNodeSpec = {
  nodeId: 'csv-dataset-creator',
  displayName: 'CSV Dataset Creator',
  category: 'Data Processing',
  subCategory: 'Dataset Generation',
  description:
    'Transform and curate industrial data into high-quality CSV datasets with specialized templates for ML, MPC, dashboards, and reporting',
  icon: 'fa:database',

  // 4 Specialized Operation Modes from collaborative specification
  specializedModes: [
    {
      modeId: 'ml-dataset',
      modeName: 'ML Dataset Creator',
      description:
        'Machine learning training data preparation with feature engineering and train/validation splitting',
      targetApplication: 'Machine Learning Training',
      additionalParameters: [
        {
          name: 'trainTestSplit',
          displayName: 'Train/Test Split Ratio',
          type: 'number',
          required: true,
          default: 0.8,
          description: 'Ratio of data for training vs testing (0.5-0.95)',
          validation: { min: 0.5, max: 0.95 },
          tooltip: 'Standard ML practice: 0.8 means 80% training, 20% testing',
        },
        {
          name: 'featureEngineering',
          displayName: 'Feature Engineering',
          type: 'boolean',
          required: false,
          default: true,
          description: 'Enable automatic feature engineering and selection',
          tooltip: 'Creates derived features like moving averages, ratios, and lag variables',
        },
        {
          name: 'targetColumn',
          displayName: 'Target Column',
          type: 'string',
          required: true,
          description: 'Name of the column to predict (dependent variable)',
          placeholder: 'temperature_setpoint',
        },
      ],
    },
    {
      modeId: 'mpc-dataset',
      modeName: 'MPC Dataset Creator',
      description:
        'Model Predictive Control data formatting with process variables and control constraints',
      targetApplication: 'Model Predictive Control',
      additionalParameters: [
        {
          name: 'controlHorizon',
          displayName: 'Control Horizon',
          type: 'number',
          required: true,
          default: 10,
          description: 'MPC control horizon length (time steps)',
          validation: { min: 1, max: 100 },
          tooltip: 'Number of future control moves to optimize',
        },
        {
          name: 'predictionHorizon',
          displayName: 'Prediction Horizon',
          type: 'number',
          required: true,
          default: 20,
          description: 'MPC prediction horizon length (time steps)',
          validation: { min: 1, max: 200 },
          tooltip: 'How far into the future to predict system behavior',
        },
        {
          name: 'processVariables',
          displayName: 'Process Variables',
          type: 'json',
          required: true,
          description: 'JSON array of process variable definitions with min/max constraints',
          placeholder: '[{"name": "temperature", "min": 50, "max": 200, "units": "°C"}]',
        },
      ],
    },
    {
      modeId: 'dashboard-dataset',
      modeName: 'Dashboard Dataset Creator',
      description: 'Real-time dashboard data feeds with time-series optimization and aggregation',
      targetApplication: 'Real-time Dashboards',
      additionalParameters: [
        {
          name: 'aggregationInterval',
          displayName: 'Data Aggregation Interval',
          type: 'options',
          required: true,
          default: '1m',
          description: 'Time interval for data aggregation',
          options: [
            { name: '1 Second', value: '1s', description: 'Real-time data (high load)' },
            { name: '30 Seconds', value: '30s', description: 'Near real-time' },
            { name: '1 Minute', value: '1m', description: 'Standard dashboard refresh' },
            { name: '5 Minutes', value: '5m', description: 'Reduced load' },
            { name: '15 Minutes', value: '15m', description: 'Low frequency monitoring' },
          ],
          tooltip: 'Balance between data freshness and system performance',
        },
        {
          name: 'timeSeriesOptimization',
          displayName: 'Time Series Optimization',
          type: 'boolean',
          required: false,
          default: true,
          description: 'Optimize data structure for time-series queries',
          tooltip: 'Improves dashboard loading speed for time-based visualizations',
        },
      ],
    },
    {
      modeId: 'report-dataset',
      modeName: 'Report Dataset Creator',
      description:
        'Business and compliance reporting data with audit trails and regulatory formatting',
      targetApplication: 'Business & Compliance Reporting',
      additionalParameters: [
        {
          name: 'auditTrail',
          displayName: 'Enable Audit Trail',
          type: 'boolean',
          required: false,
          default: true,
          description: 'Include audit trail metadata for compliance',
          tooltip: 'Adds timestamps, user info, and change tracking for regulatory compliance',
        },
        {
          name: 'reportingStandard',
          displayName: 'Reporting Standard',
          type: 'options',
          required: true,
          default: 'iso21500',
          description: 'Compliance standard for data formatting',
          options: [
            { name: 'ISO 21500', value: 'iso21500', description: 'Project management standard' },
            { name: 'GMP', value: 'gmp', description: 'Good Manufacturing Practice' },
            {
              name: 'FDA 21 CFR Part 11',
              value: 'fda21cfr11',
              description: 'FDA electronic records',
            },
            {
              name: 'GAMP 5',
              value: 'gamp5',
              description: 'Good Automated Manufacturing Practice',
            },
            { name: 'Custom', value: 'custom', description: 'Custom reporting format' },
          ],
        },
      ],
    },
  ],

  // 7-Phase Implementation from collaborative specification
  phases: [
    {
      phaseNumber: 1,
      phaseName: 'Architecture & Input Configuration',
      description: 'Core input system and template management foundation',
      status: 'APPROVED', // Moving from AWAITING_REVIEW per specification
      parameters: [
        {
          name: 'datasetName',
          displayName: 'Dataset Name',
          type: 'string',
          required: true,
          description: 'Descriptive name for this dataset',
          placeholder: 'Process Temperature Analysis Dataset',
          tooltip: 'Used for file naming and documentation',
        },
        {
          name: 'inputSource',
          displayName: 'Input Source Type',
          type: 'options',
          required: true,
          default: 'json',
          description: 'Source format of input data',
          options: [
            {
              name: 'JSON Data',
              value: 'json',
              description: 'Structured JSON from upstream nodes',
            },
            { name: 'CSV File', value: 'csv', description: 'CSV file upload or URL' },
            { name: 'Database Query', value: 'sql', description: 'SQL query result' },
            { name: 'REST API', value: 'api', description: 'REST API endpoint' },
            { name: 'MQTT Stream', value: 'mqtt', description: 'MQTT message stream' },
            { name: 'GraphQL', value: 'graphql', description: 'GraphQL query result' },
          ],
        },
        {
          name: 'templateMode',
          displayName: 'Template Configuration',
          type: 'options',
          required: true,
          default: 'predefined',
          description: 'How to configure dataset parameters',
          options: [
            {
              name: 'Predefined Template',
              value: 'predefined',
              description: 'Use existing template',
            },
            {
              name: 'Custom Configuration',
              value: 'custom',
              description: 'Manual parameter configuration',
            },
            { name: 'LLM-Assisted', value: 'llm', description: 'AI-guided template creation' },
          ],
        },
      ],
      validation: [
        {
          ruleName: 'dataset_name_required',
          ruleType: 'required',
          configuration: { field: 'datasetName' },
          errorMessage: 'Dataset name is required for file organization',
        },
        {
          ruleName: 'valid_input_source',
          ruleType: 'custom',
          configuration: {
            field: 'inputSource',
            validValues: ['json', 'csv', 'sql', 'api', 'mqtt', 'graphql'],
          },
          errorMessage: 'Input source must be a supported data format',
        },
      ],
    },
    {
      phaseNumber: 2,
      phaseName: 'Data Processing & Parsing',
      description: 'CSV parsing, delimiter detection, and encoding configuration',
      status: 'APPROVED',
      parameters: [
        {
          name: 'delimiter',
          displayName: 'Field Delimiter',
          type: 'options',
          required: true,
          default: ',',
          description: 'CSV field separator character',
          options: [
            { name: 'Comma (,)', value: ',', description: 'Standard CSV format' },
            { name: 'Semicolon (;)', value: ';', description: 'European CSV format' },
            { name: 'Tab', value: '\t', description: 'Tab-separated values' },
            { name: 'Pipe (|)', value: '|', description: 'Pipe-separated values' },
            { name: 'Auto-detect', value: 'auto', description: 'Automatically detect delimiter' },
          ],
        },
        {
          name: 'encoding',
          displayName: 'Character Encoding',
          type: 'options',
          required: true,
          default: 'utf-8',
          description: 'Text encoding of the data source',
          options: [
            { name: 'UTF-8', value: 'utf-8', description: 'Universal encoding (recommended)' },
            { name: 'ASCII', value: 'ascii', description: 'Basic ASCII characters only' },
            { name: 'ISO-8859-1', value: 'iso-8859-1', description: 'Latin-1 encoding' },
            {
              name: 'Windows-1252',
              value: 'windows-1252',
              description: 'Windows default encoding',
            },
          ],
        },
        {
          name: 'hasHeader',
          displayName: 'Has Header Row',
          type: 'boolean',
          required: false,
          default: true,
          description: 'First row contains column names',
        },
        {
          name: 'skipRows',
          displayName: 'Skip Rows',
          type: 'number',
          required: false,
          default: 0,
          description: 'Number of rows to skip at beginning',
          validation: { min: 0, max: 100 },
        },
      ],
      validation: [
        {
          ruleName: 'valid_encoding',
          ruleType: 'custom',
          configuration: {
            field: 'encoding',
            validValues: ['utf-8', 'ascii', 'iso-8859-1', 'windows-1252'],
          },
          errorMessage: 'Character encoding must be supported',
        },
      ],
    },
    {
      phaseNumber: 3,
      phaseName: 'Data Cleaning & Quality',
      description: 'Data cleaning operations, null handling, and quality validation',
      status: 'APPROVED',
      parameters: [
        {
          name: 'nullHandling',
          displayName: 'Null Value Strategy',
          type: 'options',
          required: true,
          default: 'keep',
          description: 'How to handle missing/null values',
          options: [
            { name: 'Keep as NULL', value: 'keep', description: 'Preserve missing values' },
            {
              name: 'Drop Rows',
              value: 'drop_rows',
              description: 'Remove rows with any null values',
            },
            { name: 'Forward Fill', value: 'ffill', description: 'Use previous valid value' },
            { name: 'Backward Fill', value: 'bfill', description: 'Use next valid value' },
            { name: 'Mean Imputation', value: 'mean', description: 'Replace with column mean' },
            {
              name: 'Median Imputation',
              value: 'median',
              description: 'Replace with column median',
            },
            { name: 'Zero Fill', value: 'zero', description: 'Replace with zero' },
          ],
        },
        {
          name: 'outlierDetection',
          displayName: 'Outlier Detection',
          type: 'options',
          required: false,
          default: 'none',
          description: 'Method for detecting outliers',
          options: [
            { name: 'None', value: 'none', description: 'No outlier detection' },
            { name: 'IQR Method', value: 'iqr', description: 'Interquartile range method' },
            { name: 'Z-Score', value: 'zscore', description: 'Standard deviation method' },
            {
              name: 'Isolation Forest',
              value: 'isolation',
              description: 'ML-based outlier detection',
            },
          ],
        },
        {
          name: 'dataValidation',
          displayName: 'Enable Data Validation',
          type: 'boolean',
          required: false,
          default: true,
          description: 'Perform comprehensive data quality checks',
          tooltip: 'Validates data types, ranges, and consistency',
        },
      ],
      validation: [
        {
          ruleName: 'valid_null_strategy',
          ruleType: 'custom',
          configuration: { field: 'nullHandling' },
          errorMessage: 'Null handling strategy must be specified',
        },
      ],
    },
    {
      phaseNumber: 4,
      phaseName: 'Formula & Transformation Engine',
      description: 'Mathematical formulas, regex patterns, and data transformations',
      status: 'APPROVED',
      parameters: [
        {
          name: 'enableFormulas',
          displayName: 'Enable Formula Engine',
          type: 'boolean',
          required: false,
          default: false,
          description: 'Enable mathematical formula transformations',
          tooltip: 'Allows custom calculations and derived columns',
        },
        {
          name: 'formulas',
          displayName: 'Custom Formulas',
          type: 'json',
          required: false,
          description: 'JSON array of formula definitions',
          placeholder:
            '[{"name": "efficiency", "formula": "output / input * 100", "description": "Process efficiency percentage"}]',
          tooltip: 'Each formula creates a new calculated column',
        },
        {
          name: 'regexPatterns',
          displayName: 'RegEx Patterns',
          type: 'json',
          required: false,
          description: 'JSON array of regex pattern transformations',
          placeholder:
            '[{"field": "serial_number", "pattern": "^[A-Z]{2}\\\\d{6}$", "action": "validate"}]',
        },
        {
          name: 'normalization',
          displayName: 'Data Normalization',
          type: 'options',
          required: false,
          default: 'none',
          description: 'Normalization method for numerical columns',
          options: [
            { name: 'None', value: 'none', description: 'No normalization' },
            { name: 'Min-Max Scaling', value: 'minmax', description: 'Scale to 0-1 range' },
            { name: 'Z-Score Normalization', value: 'zscore', description: 'Mean=0, StdDev=1' },
            { name: 'Robust Scaling', value: 'robust', description: 'Uses median and IQR' },
          ],
        },
      ],
      validation: [
        {
          ruleName: 'formula_syntax_check',
          ruleType: 'custom',
          configuration: { field: 'formulas', syntaxValidation: true },
          errorMessage: 'Formula syntax must be valid mathematical expressions',
        },
      ],
    },
    {
      phaseNumber: 5,
      phaseName: 'Template Management System',
      description: 'Template storage, versioning, and LLM-assisted creation',
      status: 'APPROVED',
      parameters: [
        {
          name: 'saveAsTemplate',
          displayName: 'Save as Template',
          type: 'boolean',
          required: false,
          default: false,
          description: 'Save current configuration as reusable template',
        },
        {
          name: 'templateName',
          displayName: 'Template Name',
          type: 'string',
          required: false,
          description: 'Name for saved template',
          placeholder: 'Temperature Control Dataset Template',
        },
        {
          name: 'templateTags',
          displayName: 'Template Tags',
          type: 'string',
          required: false,
          description: 'Comma-separated tags for template categorization',
          placeholder: 'temperature, control, process, industrial',
        },
        {
          name: 'llmAssistance',
          displayName: 'Enable LLM Template Assistance',
          type: 'boolean',
          required: false,
          default: false,
          description: 'Use AI assistance for template optimization and suggestions',
          tooltip: 'Provides intelligent recommendations based on data patterns',
        },
      ],
      validation: [
        {
          ruleName: 'template_name_if_saving',
          ruleType: 'dependency',
          configuration: {
            if: { field: 'saveAsTemplate', value: true },
            then: { field: 'templateName', required: true },
          },
          errorMessage: 'Template name is required when saving as template',
        },
      ],
    },
    {
      phaseNumber: 6,
      phaseName: 'Output Format & Export',
      description: 'Multi-format output, metadata inclusion, and large dataset handling',
      status: 'APPROVED',
      parameters: [
        {
          name: 'outputFormat',
          displayName: 'Primary Output Format',
          type: 'options',
          required: true,
          default: 'csv',
          description: 'Main format for dataset output',
          options: [
            { name: 'CSV', value: 'csv', description: 'Comma-separated values' },
            { name: 'JSON', value: 'json', description: 'JavaScript Object Notation' },
            { name: 'Parquet', value: 'parquet', description: 'Compressed columnar format' },
            { name: 'Excel', value: 'xlsx', description: 'Microsoft Excel format' },
            { name: 'XML', value: 'xml', description: 'Extensible Markup Language' },
            { name: 'Markdown Table', value: 'markdown', description: 'Markdown table format' },
          ],
        },
        {
          name: 'includeMetadata',
          displayName: 'Include Metadata',
          type: 'boolean',
          required: false,
          default: true,
          description: 'Include processing metadata in output',
          tooltip: 'Adds creation time, processing steps, and data lineage information',
        },
        {
          name: 'compressionLevel',
          displayName: 'Compression Level',
          type: 'options',
          required: false,
          default: 'standard',
          description: 'Compression level for output files',
          options: [
            { name: 'None', value: 'none', description: 'No compression' },
            { name: 'Standard', value: 'standard', description: 'Balanced compression' },
            { name: 'High', value: 'high', description: 'Maximum compression' },
          ],
        },
        {
          name: 'chunkSize',
          displayName: 'Chunk Size (MB)',
          type: 'number',
          required: false,
          default: 100,
          description: 'Maximum size per output file chunk',
          validation: { min: 1, max: 1000 },
          tooltip: 'Large datasets will be split into multiple files of this size',
        },
      ],
      validation: [
        {
          ruleName: 'valid_chunk_size',
          ruleType: 'range',
          configuration: { field: 'chunkSize', min: 1, max: 1000 },
          errorMessage: 'Chunk size must be between 1 and 1000 MB',
        },
      ],
    },
    {
      phaseNumber: 7,
      phaseName: 'Advanced Validation & Quality Control',
      description: 'Comprehensive validation rules, conflict resolution, and quality scoring',
      status: 'APPROVED',
      parameters: [
        {
          name: 'validationLevel',
          displayName: 'Validation Level',
          type: 'options',
          required: true,
          default: 'standard',
          description: 'Depth of data validation to perform',
          options: [
            { name: 'Basic', value: 'basic', description: 'Essential validations only' },
            { name: 'Standard', value: 'standard', description: 'Comprehensive validation suite' },
            { name: 'Strict', value: 'strict', description: 'Maximum validation rigor' },
            { name: 'Custom', value: 'custom', description: 'User-defined validation rules' },
          ],
        },
        {
          name: 'qualityThreshold',
          displayName: 'Quality Score Threshold',
          type: 'number',
          required: false,
          default: 0.8,
          description: 'Minimum quality score to accept dataset (0.0-1.0)',
          validation: { min: 0.0, max: 1.0 },
          tooltip: 'Datasets below this score will trigger warnings or errors',
        },
        {
          name: 'conflictResolution',
          displayName: 'Conflict Resolution Strategy',
          type: 'options',
          required: false,
          default: 'prompt',
          description: 'How to handle data conflicts and inconsistencies',
          options: [
            { name: 'Prompt User', value: 'prompt', description: 'Ask user to resolve conflicts' },
            { name: 'Auto-resolve', value: 'auto', description: 'Use predefined resolution rules' },
            { name: 'Skip Conflicts', value: 'skip', description: 'Skip conflicting data' },
            {
              name: 'Fail on Conflict',
              value: 'fail',
              description: 'Stop processing on conflicts',
            },
          ],
        },
        {
          name: 'generateReport',
          displayName: 'Generate Quality Report',
          type: 'boolean',
          required: false,
          default: true,
          description: 'Create detailed data quality and processing report',
          tooltip: 'Includes statistics, validation results, and recommendations',
        },
      ],
      validation: [
        {
          ruleName: 'valid_quality_threshold',
          ruleType: 'range',
          configuration: { field: 'qualityThreshold', min: 0.0, max: 1.0 },
          errorMessage: 'Quality threshold must be between 0.0 and 1.0',
        },
      ],
    },
  ],
};
