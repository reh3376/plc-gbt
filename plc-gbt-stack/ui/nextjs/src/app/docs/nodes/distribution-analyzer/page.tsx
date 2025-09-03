import {
  NodeDocumentationTemplate,
  type NodeDocumentationData,
} from '@/components/docs/NodeDocumentationTemplate';

const DISTRIBUTION_ANALYZER_DATA: NodeDocumentationData = {
  nodeType: 'distribution-analyzer',
  title: 'Distribution Analyzer Node',
  description:
    'Advanced statistical distribution identification with ML-enhanced pattern recognition for industrial process data analysis.',
  overview:
    'Identify and analyze statistical distributions in industrial datasets, providing critical insights for process control, quality assurance, and predictive modeling applications.',

  features: [
    '15+ Distribution Types: Normal, Log-Normal, Exponential, Weibull, Gamma, Beta, Uniform, Poisson, Binomial',
    'Goodness-of-Fit Testing: Kolmogorov-Smirnov, Anderson-Darling, Chi-Square, Shapiro-Wilk',
    'Parameter Estimation: Maximum Likelihood, Method of Moments, Bayesian estimation',
    'ML-Enhanced Detection: Neural network pattern recognition for complex distributions',
    'Mixture Models: Gaussian Mixture Models for multi-modal process data',
    'Advanced Visualization: Histograms, Q-Q plots, P-P plots, distribution overlays',
    'Process Monitoring: Statistical process control chart generation',
    'Confidence Intervals: Bootstrap and analytical confidence bounds',
  ],

  useCases: [
    'Process data characterization: Understanding natural process variation patterns',
    'Quality control setup: Establishing control limits based on data distribution',
    'Predictive model preparation: Selecting appropriate models based on data distribution',
    'Alarm threshold optimization: Setting statistically-based alarm limits',
    'Equipment wear analysis: Analyzing degradation patterns and failure distributions',
    'Batch consistency monitoring: Ensuring consistent product quality distributions',
  ],

  parameters: [
    {
      name: 'dataColumns',
      type: 'text',
      defaultValue: '',
      description: 'Column(s) to analyze (comma-separated, auto-detected if empty)',
      range: 'Valid numeric column names from input dataset',
      required: false,
    },
    {
      name: 'distributionTypes',
      type: 'multiselect',
      defaultValue: 'normal,log-normal,exponential,weibull,gamma',
      description: 'Statistical distributions to test and compare',
      range: '15+ distribution types including normal, weibull, gamma, beta, etc.',
      required: false,
    },
    {
      name: 'confidenceLevel',
      type: 'number',
      defaultValue: '0.95',
      description: 'Confidence level for goodness-of-fit tests',
      range: '0.90-0.99',
      required: false,
    },
    {
      name: 'outlierHandling',
      type: 'select',
      defaultValue: 'auto-detect',
      description: 'Outlier detection and handling strategy',
      range: 'none, auto-detect, iqr-method, z-score, modified-z-score',
      required: false,
    },
    {
      name: 'goodnessOfFitTests',
      type: 'json',
      defaultValue: '{"ksTest": true, "andersonDarling": true, "shapiroWilk": true}',
      description: 'Statistical tests for distribution validation',
      required: false,
    },
    {
      name: 'mixtureModeling',
      type: 'json',
      defaultValue: '{"enabled": false, "maxComponents": 5, "selectionCriterion": "bic"}',
      description: 'Gaussian Mixture Models for multi-modal distributions',
      required: false,
    },
  ],

  examples: [
    {
      title: 'Temperature Process Analysis',
      description:
        'Analyze distillation column temperature distribution for process control optimization',
      code: `{
  "dataColumns": "column_temperature",
  "distributionTypes": ["normal", "log-normal", "weibull"],
  "outlierHandling": "iqr-method",
  "parameterEstimation": {
    "method": "mle",
    "confidenceIntervals": true
  }
}`,
      language: 'json' as const,
    },
    {
      title: 'Multi-Modal Quality Data',
      description: 'Identify multiple quality distributions in batch production data',
      code: `{
  "dataColumns": "batch_quality_score",
  "distributionTypes": ["normal", "gamma", "beta"],
  "mixtureModeling": {
    "enabled": true,
    "maxComponents": 3,
    "selectionCriterion": "aic"
  }
}`,
      language: 'json' as const,
    },
  ],

  troubleshooting: [
    {
      issue: 'No Distributions Pass Goodness-of-Fit Tests',
      symptoms: 'All tested distributions rejected by statistical tests',
      cause: 'Data may follow non-standard distribution or contain multiple populations',
      solution: 'Try mixture modeling, check for outliers, consider non-parametric approaches',
      severity: 'high' as const,
    },
    {
      issue: 'Parameter Estimation Convergence Failure',
      symptoms: 'Maximum likelihood estimation fails to converge',
      cause: 'Insufficient data, poor initial estimates, or distribution mismatch',
      solution:
        'Increase sample size, try method of moments for initial estimates, check preprocessing',
      severity: 'medium' as const,
    },
    {
      issue: 'Mixture Model Overfitting',
      symptoms: 'Mixture model selects too many components',
      cause: 'Model complexity penalty insufficient or noise in data',
      solution:
        'Use stricter information criteria (BIC vs AIC), apply data smoothing, limit components',
      severity: 'medium' as const,
    },
  ],

  bestPractices: {
    dos: [
      'Ensure sufficient sample size (100+ recommended) for reliable distribution fitting',
      'Handle outliers appropriately based on process knowledge',
      'Use multiple goodness-of-fit tests for robust identification',
      'Consider mixture models for complex multi-modal industrial data',
      'Validate distribution assumptions with domain expertise',
    ],
    donts: [
      "Don't rely on single goodness-of-fit test for critical applications",
      "Don't ignore outliers without investigating their process significance",
      "Don't assume normality without proper testing",
      "Don't apply distributions outside their valid parameter ranges",
    ],
    performanceTips: [
      'Use Anderson-Darling test for detecting distribution tail behavior',
      'Apply Q-Q plots for visual validation of distribution fits',
      'Consider transformed distributions for non-standard process data',
      'Use mixture models when single distributions fail to fit adequately',
    ],
  },

  relatedNodes: [
    'Data Cleaner',
    'Binary Classification',
    'Statistical Report Generator',
    'Process Control Chart',
    'Hypothesis Tester',
  ],

  externalLinks: [
    {
      title: 'SciPy Statistical Distributions',
      url: 'https://docs.scipy.org/doc/scipy/reference/stats.html',
      description: 'Complete reference for statistical distribution functions',
    },
    {
      title: 'Statistical Distribution Fitting Guide',
      url: 'https://en.wikipedia.org/wiki/Statistical_model_validation',
      description: 'Guide to statistical model validation and distribution fitting',
    },
    {
      title: 'Process Control Statistics',
      url: 'https://example.com/process-control-statistics',
      description: 'Statistical methods for process control and monitoring',
    },
  ],
};

export default function DistributionAnalyzerDocumentation() {
  return <NodeDocumentationTemplate data={DISTRIBUTION_ANALYZER_DATA} />;
}
