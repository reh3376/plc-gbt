import {
  NodeDocumentationTemplate,
  type NodeDocumentationData,
} from '@/components/docs/NodeDocumentationTemplate';

const MULTICLASS_CLASSIFICATION_DATA: NodeDocumentationData = {
  nodeType: 'multiclass-classification',
  title: 'Multi-Category Classification Node',
  description:
    'Sophisticated multi-class classification supporting n-category problems with advanced ensemble methods and class balancing.',
  overview:
    'Perform multi-class classification on complex industrial datasets with automatic class balancing, ensemble methods, and advanced validation strategies for production control systems.',

  features: [
    'Algorithm Suite: Decision Trees, Random Forest, SVM (OvR/OvO), Neural Networks, Gradient Boosting',
    'Class Balancing: SMOTE, ADASYN, Random Oversampling, Class Weight Adjustment',
    'Multi-Class Strategies: One-vs-Rest, One-vs-One, Error-Correcting Output Codes',
    'Advanced Validation: Stratified K-Fold, temporal validation for time-series',
    'Feature Selection: Mutual Information, Chi-Square, Recursive Feature Elimination',
    'Ensemble Methods: Voting, Bagging, Boosting, Stacking with meta-learners',
    'Model Interpretability: SHAP values, LIME explanations, feature attribution',
  ],

  useCases: [
    'Process state classification: Multiple operating modes identification',
    'Product categorization: Quality grades (A, B, C, Reject classifications)',
    'Equipment health monitoring: Normal, Warning, Critical, Failure states',
    'Production line routing: Multi-path process decisions',
    'Safety level assessment: Low, Medium, High, Critical risk categories',
    'Batch quality control: Multiple quality classification levels',
  ],

  parameters: [
    {
      name: 'algorithmType',
      type: 'multiselect',
      defaultValue: 'random-forest,xgboost',
      description: 'Classification algorithms for ensemble comparison',
      range: 'decision-tree, random-forest, svm, neural-network, gradient-boosting, xgboost',
      required: true,
    },
    {
      name: 'targetColumn',
      type: 'string',
      defaultValue: 'class_label',
      description: 'Column containing multi-class target labels',
      range: 'Valid column name from input dataset',
      required: true,
    },
    {
      name: 'classNames',
      type: 'text',
      defaultValue: '',
      description: 'Explicit class names (comma-separated, auto-detected if empty)',
      range: 'String identifiers for each class',
      required: false,
    },
    {
      name: 'multiClassStrategy',
      type: 'select',
      defaultValue: 'ovr',
      description: 'Multi-class decomposition strategy',
      range: 'ovr (One-vs-Rest), ovo (One-vs-One), direct (Direct multi-class)',
      required: false,
    },
    {
      name: 'classBalancing',
      type: 'json',
      defaultValue:
        '{"enabled": true, "method": "auto", "strategy": "SMOTE", "oversampleRatio": 0.8}',
      description: 'Class imbalance correction methods',
      required: false,
    },
    {
      name: 'ensembleConfig',
      type: 'json',
      defaultValue:
        '{"votingType": "soft", "stackingEnabled": false, "metaLearner": "logistic-regression"}',
      description: 'Ensemble learning configuration',
      required: false,
    },
  ],

  examples: [
    {
      title: 'Production Quality Grading',
      description:
        'Classify whiskey batches into quality grades: Premium, Standard, Below-Grade, Reject',
      code: `{
  "algorithmType": ["random-forest", "xgboost", "gradient-boosting"],
  "targetColumn": "quality_grade",
  "classNames": "Premium,Standard,Below-Grade,Reject",
  "multiClassStrategy": "ovr",
  "ensembleConfig": {
    "votingType": "soft",
    "stackingEnabled": true
  }
}`,
      language: 'json' as const,
    },
    {
      title: 'Equipment State Monitoring',
      description:
        'Monitor distillation column states: Normal, Fouling, Flooding, Weeping, Critical',
      code: `{
  "algorithmType": ["svm", "neural-network"],
  "targetColumn": "column_state",
  "validationStrategy": "temporal-split",
  "interpretability": {
    "shapEnabled": true,
    "limeEnabled": true
  }
}`,
      language: 'json' as const,
    },
  ],

  troubleshooting: [
    {
      issue: 'Poor Performance on Minority Classes',
      symptoms: 'High overall accuracy but poor recall on important minority classes',
      cause: 'Class imbalance affecting model bias toward majority classes',
      solution:
        'Enable class balancing with SMOTE or ADASYN, adjust class weights, use stratified sampling',
      severity: 'high' as const,
    },
    {
      issue: 'High Inter-Class Confusion',
      symptoms: 'Model consistently confuses specific class pairs',
      cause: 'Similar feature patterns between classes or insufficient discriminative features',
      solution:
        'Add domain-specific features, apply feature selection, consider hierarchical classification',
      severity: 'medium' as const,
    },
  ],

  bestPractices: {
    dos: [
      'Use stratified validation to ensure all classes are represented',
      'Apply class balancing for imbalanced industrial datasets',
      'Monitor per-class performance metrics separately',
      'Use ensemble methods for critical classification decisions',
      'Validate temporal consistency for time-series industrial data',
    ],
    donts: [
      "Don't ignore rare but critical classes (safety events, equipment failures)",
      "Don't use accuracy alone for imbalanced multi-class problems",
      "Don't skip class probability calibration for decision support",
      "Don't deploy without per-class performance validation",
    ],
    performanceTips: [
      'Use macro-averaged F1 score for balanced class performance assessment',
      'Enable probability calibration for reliable confidence estimates',
      'Consider hierarchical classification for complex class structures',
      'Use confusion matrix analysis to identify class confusion patterns',
    ],
  },

  relatedNodes: [
    'Binary Classification',
    'Feature Engineer',
    'Data Cleaner',
    'Performance Dashboard',
    'Model Explainer',
  ],

  externalLinks: [
    {
      title: 'Multi-class Classification Guide',
      url: 'https://scikit-learn.org/stable/modules/multiclass.html',
      description: 'Comprehensive guide to multi-class classification methods',
    },
    {
      title: 'Ensemble Methods Documentation',
      url: 'https://scikit-learn.org/stable/modules/ensemble.html',
      description: 'Documentation on ensemble learning techniques',
    },
    {
      title: 'SHAP Model Explanations',
      url: 'https://shap.readthedocs.io/en/latest/',
      description: 'Model interpretability with SHAP explanations',
    },
  ],
};

export default function MulticlassClassificationDocumentation() {
  return <NodeDocumentationTemplate data={MULTICLASS_CLASSIFICATION_DATA} />;
}
