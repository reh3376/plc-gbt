import { NodeDocumentationTemplate } from '@/components/docs/NodeDocumentationTemplate';

const MULTICLASS_CLASSIFICATION_DATA = {
  title: 'Multi-Category Classification Node',
  category: 'Machine Learning',
  description:
    'Sophisticated multi-class classification supporting n-category problems with advanced ensemble methods and class balancing.',

  overview: {
    purpose:
      'Perform multi-class classification on complex industrial datasets with automatic class balancing, ensemble methods, and advanced validation strategies for production control systems.',
    keyFeatures: [
      'Algorithm Suite: Decision Trees, Random Forest, SVM (OvR/OvO), Neural Networks, Gradient Boosting',
      'Class Balancing: SMOTE, ADASYN, Random Oversampling, Class Weight Adjustment',
      'Multi-Class Strategies: One-vs-Rest, One-vs-One, Error-Correcting Output Codes',
      'Advanced Validation: Stratified K-Fold, temporal validation for time-series',
      'Feature Selection: Mutual Information, Chi-Square, Recursive Feature Elimination',
      'Ensemble Methods: Voting, Bagging, Boosting, Stacking with meta-learners',
      'Model Interpretability: SHAP values, LIME explanations, feature attribution',
    ],
    whenToUse: [
      'Process state classification: Multiple operating modes identification',
      'Product categorization: Quality grades (A, B, C, Reject classifications)',
      'Equipment health monitoring: Normal, Warning, Critical, Failure states',
      'Production line routing: Multi-path process decisions',
      'Safety level assessment: Low, Medium, High, Critical risk categories',
      'Batch quality control: Multiple quality classification levels',
    ],
  },

  quickStart: {
    steps: [
      'Drag Multi-Category Classification node from ML Algorithm palette',
      'Connect multi-class labeled dataset with categorical features',
      'Configure feature matrix and class label column',
      'Select classification strategy (OvR, OvO, or direct multi-class)',
      'Configure class balancing if dataset is imbalanced',
      'Choose ensemble methods for improved performance',
      'Execute training with cross-validation',
      'Analyze confusion matrix and per-class performance metrics',
    ],
  },

  parameters: {
    essential: [
      {
        name: 'algorithmType',
        type: 'multi-select',
        defaultValue: ['random-forest', 'xgboost'],
        options: [
          'decision-tree',
          'random-forest',
          'svm',
          'neural-network',
          'gradient-boosting',
          'xgboost',
        ],
        description: 'Classification algorithms for ensemble comparison',
        range: 'One or more algorithm types',
      },
      {
        name: 'targetColumn',
        type: 'string',
        defaultValue: 'class_label',
        description: 'Column containing multi-class target labels',
        range: 'Valid column name from input dataset',
      },
      {
        name: 'classNames',
        type: 'array',
        defaultValue: [],
        description: 'Explicit class names (auto-detected if empty)',
        range: 'String identifiers for each class',
      },
      {
        name: 'multiClassStrategy',
        type: 'select',
        defaultValue: 'ovr',
        options: ['ovr', 'ovo', 'direct'],
        description: 'Multi-class decomposition strategy',
        range: 'One-vs-Rest, One-vs-One, or Direct multi-class',
      },
      {
        name: 'validationStrategy',
        type: 'select',
        defaultValue: 'stratified-kfold',
        options: ['stratified-kfold', 'kfold', 'leave-one-out', 'temporal-split'],
        description: 'Cross-validation strategy for model evaluation',
        range: 'Validation method appropriate for data structure',
      },
    ],
    advanced: [
      {
        name: 'classBalancing',
        type: 'object',
        defaultValue: { enabled: true, method: 'auto', strategy: 'SMOTE', oversampleRatio: 0.8 },
        description: 'Class imbalance correction methods',
        notes: 'Automatically detects and corrects class imbalances',
      },
      {
        name: 'ensembleConfig',
        type: 'object',
        defaultValue: {
          votingType: 'soft',
          stackingEnabled: false,
          metaLearner: 'logistic-regression',
        },
        description: 'Ensemble learning configuration',
        notes: 'Combines predictions from multiple algorithms',
      },
      {
        name: 'featureSelection',
        type: 'object',
        defaultValue: { enabled: false, method: 'mutual-info', kBest: 20, threshold: 0.1 },
        description: 'Feature selection and dimensionality reduction',
        notes: 'Improves performance and interpretability',
      },
      {
        name: 'interpretability',
        type: 'object',
        defaultValue: { shapEnabled: true, limeEnabled: false, featureImportance: true },
        description: 'Model interpretability and explanation methods',
        notes: 'Provides insights into model decision-making',
      },
      {
        name: 'performanceOptimization',
        type: 'object',
        defaultValue: { parallelProcessing: true, nJobs: -1, memoryOptimization: true },
        description: 'Training and inference optimization',
        notes: 'Improves training speed and memory usage',
      },
    ],
  },

  examples: [
    {
      title: 'Production Quality Grading',
      description:
        'Classify whiskey batches into quality grades: Premium, Standard, Below-Grade, Reject',
      config: {
        algorithmType: ['random-forest', 'xgboost', 'gradient-boosting'],
        targetColumn: 'quality_grade',
        classNames: ['Premium', 'Standard', 'Below-Grade', 'Reject'],
        multiClassStrategy: 'ovr',
        ensembleConfig: { votingType: 'soft', stackingEnabled: true },
        classBalancing: { enabled: true, method: 'adaptive', strategy: 'ADASYN' },
      },
    },
    {
      title: 'Equipment State Monitoring',
      description:
        'Monitor distillation column states: Normal, Fouling, Flooding, Weeping, Critical',
      config: {
        algorithmType: ['svm', 'neural-network'],
        targetColumn: 'column_state',
        validationStrategy: 'temporal-split',
        featureSelection: { enabled: true, method: 'chi-square', kBest: 12 },
        interpretability: { shapEnabled: true, limeEnabled: true },
      },
    },
  ],

  bestPractices: {
    dos: [
      'Use stratified validation to ensure all classes are represented',
      'Apply class balancing for imbalanced industrial datasets',
      'Monitor per-class performance metrics separately',
      'Use ensemble methods for critical classification decisions',
      'Validate temporal consistency for time-series industrial data',
      'Apply feature selection to improve model interpretability',
    ],
    donts: [
      "Don't ignore rare but critical classes (safety events, equipment failures)",
      "Don't use accuracy alone for imbalanced multi-class problems",
      "Don't skip class probability calibration for decision support",
      "Don't deploy without per-class performance validation",
      "Don't forget to handle new/unseen classes in production",
    ],
    performanceTips: [
      'Use macro-averaged F1 score for balanced class performance assessment',
      'Enable probability calibration for reliable confidence estimates',
      'Consider hierarchical classification for complex class structures',
      'Use confusion matrix analysis to identify class confusion patterns',
    ],
  },

  troubleshooting: {
    commonIssues: [
      {
        issue: 'Poor Performance on Minority Classes',
        symptoms: 'High overall accuracy but poor recall on important minority classes',
        cause: 'Class imbalance affecting model bias toward majority classes',
        solution: [
          'Enable class balancing with SMOTE or ADASYN',
          'Adjust class weights to penalize minority class errors',
          'Use stratified sampling in cross-validation',
          'Consider cost-sensitive learning approaches',
        ],
      },
      {
        issue: 'High Inter-Class Confusion',
        symptoms: 'Model consistently confuses specific class pairs',
        cause: 'Similar feature patterns between classes or insufficient discriminative features',
        solution: [
          'Add domain-specific features that distinguish confused classes',
          'Apply feature selection focused on class discrimination',
          'Use hierarchical classification to separate similar classes',
          'Consider ensemble methods with class-specific expertise',
        ],
      },
      {
        issue: 'Inconsistent Temporal Performance',
        symptoms: 'Model performance varies significantly across time periods',
        cause: 'Concept drift or temporal dependencies in industrial processes',
        solution: [
          'Use temporal validation splits instead of random splits',
          'Enable incremental learning for adapting to process changes',
          'Add time-based features to capture temporal patterns',
          'Implement model retraining schedules for production deployment',
        ],
      },
    ],
    errorCodes: [
      {
        code: 'MC001',
        message: 'Insufficient classes detected',
        solution: 'Ensure at least 3 classes in target column',
      },
      {
        code: 'MC002',
        message: 'Class imbalance too severe',
        solution: 'Enable aggressive class balancing strategies',
      },
      {
        code: 'MC003',
        message: 'Feature matrix rank deficient',
        solution: 'Remove collinear features or apply PCA',
      },
      {
        code: 'MC004',
        message: 'Ensemble training failed',
        solution: 'Verify individual algorithm compatibility',
      },
    ],
  },

  relatedNodes: {
    inputNodes: [
      { name: 'Data Cleaner', description: 'Preprocesses multi-class datasets' },
      { name: 'Feature Engineer', description: 'Creates discriminative features' },
      { name: 'CSV Dataset Creator', description: 'Formats multi-class training data' },
    ],
    outputNodes: [
      { name: 'Confusion Matrix Visualizer', description: 'Analyzes class prediction patterns' },
      { name: 'Performance Dashboard', description: 'Monitors per-class performance' },
      { name: 'Model Explainer', description: 'Provides SHAP/LIME explanations' },
    ],
    complementaryNodes: [
      { name: 'Binary Classification', description: 'For simplified 2-class problems' },
      { name: 'Clustering Analysis', description: 'For unsupervised class discovery' },
      { name: 'Anomaly Detection', description: 'Identifies outlier classes' },
    ],
  },

  apiReference: {
    nodeClass: `class MulticlassClassificationNode extends IndustrialNode {
  config: MulticlassClassificationConfig;
  
  async trainModel(dataset: MulticlassDataset): Promise<MulticlassModel>
  async predict(features: FeatureVector): Promise<ClassPrediction>
  async evaluatePerformance(): Promise<MulticlassMetrics>
  async explainPrediction(instance: FeatureVector): Promise<ExplanationResult>
}`,
    configInterface: `interface MulticlassClassificationConfig {
  algorithmType: AlgorithmType[];
  targetColumn: string;
  classNames: string[];
  multiClassStrategy: 'ovr' | 'ovo' | 'direct';
  validationStrategy: ValidationStrategy;
  classBalancing?: ClassBalancingConfig;
  ensembleConfig?: EnsembleConfig;
  featureSelection?: FeatureSelectionConfig;
  interpretability?: InterpretabilityConfig;
}`,
    events: [
      'onClassBalancing: Fired during class imbalance correction',
      'onFeatureSelection: Fired during feature selection process',
      'onEnsembleTraining: Fired during ensemble model training',
      'onValidationComplete: Fired when k-fold validation completes',
      'onConfusionMatrix: Fired when confusion matrix is generated',
      'onSHAPAnalysis: Fired when SHAP explanations are computed',
    ],
  },

  additionalResources: {
    externalDocs: [
      {
        name: 'Multi-class Classification Guide',
        url: 'https://scikit-learn.org/stable/modules/multiclass.html',
      },
      {
        name: 'Ensemble Methods Documentation',
        url: 'https://scikit-learn.org/stable/modules/ensemble.html',
      },
      { name: 'SHAP Model Explanations', url: 'https://shap.readthedocs.io/en/latest/' },
    ],
    communityResources: [
      {
        name: 'Industrial Classification Examples',
        url: 'https://github.com/plc-gbt/multiclass-examples',
      },
      { name: 'Process Control ML Community', url: 'https://forum.plc-gbt.com/process-ml' },
    ],
  },

  version: '1.0.0',
  lastUpdated: 'January 2025',
  appliesTo: 'PLC-GBT v3.1.0+',
};

export default function MulticlassClassificationDocumentation() {
  return <NodeDocumentationTemplate {...MULTICLASS_CLASSIFICATION_DATA} />;
}
