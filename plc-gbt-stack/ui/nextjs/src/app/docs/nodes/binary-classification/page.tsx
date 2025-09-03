import {
  NodeDocumentationTemplate,
  type NodeDocumentationData,
} from '@/components/docs/NodeDocumentationTemplate';

const BINARY_CLASSIFICATION_DATA: NodeDocumentationData = {
  nodeType: 'binary-classification',
  title: 'Binary Classification Node',
  description:
    'Advanced binary classification for industrial process data with multiple algorithm support and comprehensive model evaluation.',
  overview:
    'Perform binary classification on industrial datasets using state-of-the-art machine learning algorithms, designed for process control, fault detection, and decision support systems.',

  features: [
    'Multi-Algorithm Support: SVM, Random Forest, Logistic Regression, XGBoost, Neural Networks, Gradient Boosting',
    'Advanced Preprocessing: Feature scaling, encoding, missing value handling, outlier detection',
    'Comprehensive Validation: Cross-validation, time-series aware splits, holdout validation',
    'Hyperparameter Optimization: Grid search, random search, Bayesian optimization',
    'Performance Analytics: ROC-AUC, confusion matrix, feature importance, calibration plots',
    'Production Export: Multiple model formats (Pickle, ONNX, TensorFlow SavedModel)',
  ],

  useCases: [
    'Process fault detection: Classify normal vs abnormal operating conditions',
    'Quality control: Good vs defective product classification',
    'Equipment monitoring: Predictive maintenance classification (healthy vs faulty)',
    'Safety systems: Emergency vs normal condition detection',
    'Production optimization: High vs low yield classification',
  ],

  parameters: [
    {
      name: 'algorithmType',
      type: 'select',
      defaultValue: 'random-forest',
      description: 'Primary classification algorithm',
      range: 'svm, random-forest, logistic-regression, xgboost, neural-network, gradient-boosting',
      required: true,
    },
    {
      name: 'targetColumn',
      type: 'string',
      defaultValue: 'target',
      description: 'Column name containing binary target variable',
      range: 'Valid column name from input dataset',
      required: true,
    },
    {
      name: 'featureColumns',
      type: 'text',
      defaultValue: '',
      description:
        'Selected feature columns for training (comma-separated, auto-detected if empty)',
      range: 'Valid column names from input dataset',
      required: false,
    },
    {
      name: 'validationSplit',
      type: 'number',
      defaultValue: '0.2',
      description: 'Fraction of data reserved for validation',
      range: '0.1-0.5',
      required: false,
    },
    {
      name: 'hyperparameterTuning',
      type: 'json',
      defaultValue: '{"enabled": true, "method": "grid-search", "iterations": 50}',
      description: 'Hyperparameter optimization configuration',
      required: false,
    },
  ],

  examples: [
    {
      title: 'Process Fault Detection',
      description: 'Detect abnormal operating conditions in a distillation column',
      code: `{
  "algorithmType": "random-forest",
  "targetColumn": "fault_status",
  "featureColumns": "temperature,pressure,flow_rate,reflux_ratio",
  "validationSplit": 0.25,
  "hyperparameterTuning": {
    "enabled": true,
    "method": "random-search",
    "iterations": 100
  }
}`,
      language: 'json' as const,
    },
    {
      title: 'Quality Control Classification',
      description: 'Classify product quality as acceptable vs reject based on sensor data',
      code: `{
  "algorithmType": "xgboost",
  "targetColumn": "quality_pass",
  "featureColumns": "viscosity,color,ph_level,density",
  "ensembleMethods": {
    "enabled": true,
    "votingType": "soft",
    "algorithms": ["xgboost", "random-forest"]
  }
}`,
      language: 'json' as const,
    },
  ],

  troubleshooting: [
    {
      issue: 'Low Classification Accuracy',
      symptoms: 'Model accuracy below 70% on validation data',
      cause: 'Insufficient features, poor data quality, or algorithm mismatch',
      solution: 'Review feature engineering, check data quality, try ensemble methods',
      severity: 'high' as const,
    },
    {
      issue: 'Model Overfitting',
      symptoms: 'High training accuracy but poor validation performance',
      cause: 'Model too complex for available data',
      solution: 'Enable regularization, reduce complexity, use cross-validation',
      severity: 'medium' as const,
    },
    {
      issue: 'Training Memory Errors',
      symptoms: 'Out of memory errors during model training',
      cause: 'Dataset too large for available memory',
      solution: 'Enable data chunking, reduce features, use incremental learning',
      severity: 'medium' as const,
    },
  ],

  bestPractices: {
    dos: [
      'Always validate data quality before training',
      'Apply appropriate feature scaling for distance-based algorithms',
      'Monitor model performance with cross-validation',
      'Export trained models in production-ready formats',
      'Document feature engineering decisions for reproducibility',
    ],
    donts: [
      "Don't ignore class imbalance in industrial datasets",
      "Don't skip feature selection with high-dimensional data",
      "Don't use default hyperparameters for production models",
      "Don't deploy models without proper performance validation",
    ],
    performanceTips: [
      'Use ensemble methods for critical industrial applications',
      'Enable early stopping for large datasets to reduce training time',
      'Consider feature importance for model interpretability',
      'Use time-series aware validation for temporal industrial data',
    ],
  },

  relatedNodes: [
    'Feature Engineer',
    'Data Cleaner',
    'Performance Metrics',
    'Multiclass Classification',
    'Distribution Analyzer',
  ],

  externalLinks: [
    {
      title: 'Scikit-learn Classification Guide',
      url: 'https://scikit-learn.org/stable/supervised_learning.html#classification',
      description: 'Comprehensive guide to classification algorithms',
    },
    {
      title: 'XGBoost Documentation',
      url: 'https://xgboost.readthedocs.io/en/latest/',
      description: 'Official XGBoost documentation and tutorials',
    },
    {
      title: 'Industrial ML Best Practices',
      url: 'https://example.com/industrial-ml-guide',
      description: 'Best practices for machine learning in industrial applications',
    },
  ],
};

export default function BinaryClassificationDocumentation() {
  return <NodeDocumentationTemplate data={BINARY_CLASSIFICATION_DATA} />;
}
