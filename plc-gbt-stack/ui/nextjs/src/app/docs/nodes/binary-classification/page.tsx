import { NodeDocumentationTemplate } from '@/components/docs/NodeDocumentationTemplate';

const BINARY_CLASSIFICATION_DATA = {
  title: 'Binary Classification Node',
  category: 'Machine Learning',
  description:
    'Advanced binary classification for industrial process data with multiple algorithm support and comprehensive model evaluation.',

  overview: {
    purpose:
      'Perform binary classification on industrial datasets using state-of-the-art machine learning algorithms, designed for process control, fault detection, and decision support systems.',
    keyFeatures: [
      'Multi-Algorithm Support: SVM, Random Forest, Logistic Regression, XGBoost, Neural Networks, Gradient Boosting',
      'Advanced Preprocessing: Feature scaling, encoding, missing value handling, outlier detection',
      'Comprehensive Validation: Cross-validation, time-series aware splits, holdout validation',
      'Hyperparameter Optimization: Grid search, random search, Bayesian optimization',
      'Performance Analytics: ROC-AUC, confusion matrix, feature importance, calibration plots',
      'Production Export: Multiple model formats (Pickle, ONNX, TensorFlow SavedModel)',
    ],
    whenToUse: [
      'Process fault detection: Classify normal vs abnormal operating conditions',
      'Quality control: Good vs defective product classification',
      'Equipment monitoring: Predictive maintenance classification (healthy vs faulty)',
      'Safety systems: Emergency vs normal condition detection',
      'Production optimization: High vs low yield classification',
    ],
  },

  quickStart: {
    steps: [
      'Drag Binary Classification node from ML Algorithm palette',
      'Connect input dataset (CSV/JSON with features and binary target)',
      'Configure feature columns and target variable',
      'Select classification algorithm(s) for comparison',
      'Set validation strategy and performance metrics',
      'Execute training and review performance results',
    ],
  },

  parameters: {
    essential: [
      {
        name: 'algorithmType',
        type: 'select',
        defaultValue: 'random-forest',
        options: [
          'svm',
          'random-forest',
          'logistic-regression',
          'xgboost',
          'neural-network',
          'gradient-boosting',
        ],
        description: 'Primary classification algorithm',
        range: 'Predefined algorithm options',
      },
      {
        name: 'targetColumn',
        type: 'string',
        defaultValue: 'target',
        description: 'Column name containing binary target variable',
        range: 'Valid column name from input dataset',
      },
      {
        name: 'featureColumns',
        type: 'array',
        defaultValue: [],
        description: 'Selected feature columns for training (auto-detected if empty)',
        range: 'Valid column names from input dataset',
      },
      {
        name: 'validationSplit',
        type: 'number',
        defaultValue: 0.2,
        description: 'Fraction of data reserved for validation',
        range: '0.1-0.5',
      },
      {
        name: 'crossValidationFolds',
        type: 'number',
        defaultValue: 5,
        description: 'Number of cross-validation folds',
        range: '2-10',
      },
    ],
    advanced: [
      {
        name: 'hyperparameterTuning',
        type: 'object',
        defaultValue: { enabled: true, method: 'grid-search', iterations: 50 },
        description: 'Hyperparameter optimization configuration',
        notes: 'Grid search, random search, or Bayesian optimization',
      },
      {
        name: 'ensembleMethods',
        type: 'object',
        defaultValue: {
          enabled: false,
          votingType: 'soft',
          algorithms: ['random-forest', 'xgboost'],
        },
        description: 'Ensemble learning configuration',
        notes: 'Combines multiple algorithms for improved performance',
      },
      {
        name: 'featureSelection',
        type: 'object',
        defaultValue: { enabled: false, method: 'mutual-info', kBest: 10 },
        description: 'Automatic feature selection',
        notes: 'Reduces dimensionality and improves model performance',
      },
      {
        name: 'classBalancing',
        type: 'object',
        defaultValue: { enabled: true, method: 'auto', strategy: 'SMOTE' },
        description: 'Handle imbalanced class distributions',
        notes: 'SMOTE, ADASYN, or resampling methods',
      },
    ],
  },

  examples: [
    {
      title: 'Process Fault Detection',
      description: 'Detect abnormal operating conditions in a distillation column',
      config: {
        algorithmType: 'random-forest',
        targetColumn: 'fault_status',
        featureColumns: ['temperature', 'pressure', 'flow_rate', 'reflux_ratio'],
        validationSplit: 0.25,
        crossValidationFolds: 5,
        hyperparameterTuning: { enabled: true, method: 'random-search', iterations: 100 },
        classBalancing: { enabled: true, method: 'auto', strategy: 'SMOTE' },
      },
    },
    {
      title: 'Quality Control Classification',
      description: 'Classify product quality as acceptable vs reject based on sensor data',
      config: {
        algorithmType: 'xgboost',
        targetColumn: 'quality_pass',
        featureColumns: ['viscosity', 'color', 'ph_level', 'density'],
        ensembleMethods: {
          enabled: true,
          votingType: 'soft',
          algorithms: ['xgboost', 'random-forest', 'svm'],
        },
        featureSelection: { enabled: true, method: 'mutual-info', kBest: 15 },
      },
    },
  ],

  bestPractices: {
    dos: [
      'Always validate data quality before training',
      'Use stratified sampling for imbalanced datasets',
      'Apply appropriate feature scaling for distance-based algorithms',
      'Monitor model performance with cross-validation',
      'Export trained models in production-ready formats',
      'Document feature engineering decisions for reproducibility',
    ],
    donts: [
      "Don't ignore class imbalance in industrial datasets",
      "Don't skip feature selection with high-dimensional data",
      "Don't use default hyperparameters for production models",
      "Don't forget to validate model calibration for probability outputs",
      "Don't deploy models without proper performance validation",
    ],
    performanceTips: [
      'Use ensemble methods for critical industrial applications',
      'Enable early stopping for large datasets to reduce training time',
      'Consider feature importance for model interpretability',
      'Use time-series aware validation for temporal industrial data',
    ],
  },

  troubleshooting: {
    commonIssues: [
      {
        issue: 'Low Classification Accuracy',
        symptoms: 'Model accuracy below 70% on validation data',
        cause: 'Insufficient features, poor data quality, or algorithm mismatch',
        solution: [
          'Review feature engineering and selection',
          'Check for missing values or outliers in training data',
          'Try ensemble methods or different algorithms',
          'Increase training dataset size if possible',
        ],
      },
      {
        issue: 'Model Overfitting',
        symptoms: 'High training accuracy but poor validation performance',
        cause: 'Model too complex for available data',
        solution: [
          'Enable regularization parameters',
          'Reduce model complexity (fewer trees, lower depth)',
          'Use more cross-validation folds',
          'Apply feature selection to reduce dimensionality',
        ],
      },
      {
        issue: 'Training Memory Errors',
        symptoms: 'Out of memory errors during model training',
        cause: 'Dataset too large for available memory',
        solution: [
          'Enable data chunking/batch processing',
          'Reduce feature dimensionality',
          'Use incremental learning algorithms',
          'Consider data sampling for extremely large datasets',
        ],
      },
    ],
    errorCodes: [
      {
        code: 'BC001',
        message: 'Invalid target column',
        solution: 'Verify target column exists and contains binary values',
      },
      {
        code: 'BC002',
        message: 'Insufficient training data',
        solution: 'Ensure minimum 100 samples for reliable training',
      },
      {
        code: 'BC003',
        message: 'Feature-target correlation too low',
        solution: 'Review feature selection and engineering',
      },
      {
        code: 'BC004',
        message: 'Cross-validation failed',
        solution: 'Check for data leakage or temporal dependencies',
      },
    ],
  },

  relatedNodes: {
    inputNodes: [
      { name: 'CSV Dataset Creator', description: 'Provides formatted training data' },
      { name: 'Feature Engineer', description: 'Preprocesses features before classification' },
      { name: 'Data Cleaner', description: 'Cleans and validates input data quality' },
    ],
    outputNodes: [
      { name: 'Performance Metrics', description: 'Analyzes classification results' },
      { name: 'Dashboard Generator', description: 'Visualizes model performance' },
      { name: 'PDF Report Generator', description: 'Creates model evaluation reports' },
    ],
    complementaryNodes: [
      { name: 'Multiclass Classification', description: 'For problems with >2 categories' },
      { name: 'Distribution Analyzer', description: 'Analyzes feature distributions' },
      { name: 'PCA Reducer', description: 'Reduces feature dimensionality' },
    ],
  },

  apiReference: {
    nodeClass: `class BinaryClassificationNode extends IndustrialNode {
  config: BinaryClassificationConfig;
  
  async trainModel(dataset: TrainingDataset): Promise<TrainedModel>
  async predict(features: FeatureVector): Promise<PredictionResult>
  async evaluateModel(): Promise<PerformanceMetrics>
  async exportModel(format: ModelFormat): Promise<ModelBlob>
}`,
    configInterface: `interface BinaryClassificationConfig {
  algorithmType: 'svm' | 'random-forest' | 'logistic-regression' | 'xgboost' | 'neural-network' | 'gradient-boosting';
  targetColumn: string;
  featureColumns: string[];
  validationSplit: number;
  crossValidationFolds: number;
  hyperparameterTuning?: HyperparameterConfig;
  ensembleMethods?: EnsembleConfig;
  featureSelection?: FeatureSelectionConfig;
  classBalancing?: ClassBalancingConfig;
}`,
    events: [
      'onTrainingStart: Fired when model training begins',
      'onTrainingProgress: Fired during training with progress updates',
      'onTrainingComplete: Fired when model training finishes',
      'onValidationComplete: Fired when cross-validation finishes',
      'onPrediction: Fired when making new predictions',
      'onError: Fired when training or prediction errors occur',
    ],
  },

  additionalResources: {
    externalDocs: [
      {
        name: 'Scikit-learn Classification Guide',
        url: 'https://scikit-learn.org/stable/supervised_learning.html#classification',
      },
      { name: 'XGBoost Documentation', url: 'https://xgboost.readthedocs.io/en/latest/' },
      { name: 'Industrial ML Best Practices', url: 'https://example.com/industrial-ml-guide' },
    ],
    communityResources: [
      { name: 'PLC-GBT ML Forum', url: 'https://forum.plc-gbt.com/ml' },
      {
        name: 'Classification Examples Repository',
        url: 'https://github.com/plc-gbt/classification-examples',
      },
      {
        name: 'Industrial Data Science Stack Overflow',
        url: 'https://stackoverflow.com/tags/industrial-ml',
      },
    ],
  },

  version: '1.0.0',
  lastUpdated: 'January 2025',
  appliesTo: 'PLC-GBT v3.1.0+',
};

export default function BinaryClassificationDocumentation() {
  return <NodeDocumentationTemplate {...BINARY_CLASSIFICATION_DATA} />;
}
