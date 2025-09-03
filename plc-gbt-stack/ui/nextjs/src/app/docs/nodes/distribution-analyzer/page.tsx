import { NodeDocumentationTemplate } from '@/components/docs/NodeDocumentationTemplate';

const DISTRIBUTION_ANALYZER_DATA = {
  title: 'Distribution Analyzer Node',
  category: 'Data Processing',
  description: 'Advanced statistical distribution identification with ML-enhanced pattern recognition for industrial process data analysis.',
  
  overview: {
    purpose: 'Identify and analyze statistical distributions in industrial datasets, providing critical insights for process control, quality assurance, and predictive modeling applications.',
    keyFeatures: [
      '15+ Distribution Types: Normal, Log-Normal, Exponential, Weibull, Gamma, Beta, Uniform, Poisson, Binomial',
      'Goodness-of-Fit Testing: Kolmogorov-Smirnov, Anderson-Darling, Chi-Square, Shapiro-Wilk',
      'Parameter Estimation: Maximum Likelihood, Method of Moments, Bayesian estimation',
      'ML-Enhanced Detection: Neural network pattern recognition for complex distributions',
      'Mixture Models: Gaussian Mixture Models for multi-modal process data',
      'Advanced Visualization: Histograms, Q-Q plots, P-P plots, distribution overlays',
      'Process Monitoring: Statistical process control chart generation',
      'Confidence Intervals: Bootstrap and analytical confidence bounds'
    ],
    whenToUse: [
      'Process data characterization: Understanding natural process variation patterns',
      'Quality control setup: Establishing control limits based on data distribution',
      'Predictive model preparation: Selecting appropriate models based on data distribution',
      'Alarm threshold optimization: Setting statistically-based alarm limits',
      'Equipment wear analysis: Analyzing degradation patterns and failure distributions',
      'Batch consistency monitoring: Ensuring consistent product quality distributions'
    ]
  },

  quickStart: {
    steps: [
      'Drag Distribution Analyzer from Data Processing palette',
      'Connect 2D dataset input (univariate or bivariate data)',
      'Configure data column(s) for analysis',
      'Select distribution types to test (or use auto-detection)',
      'Set goodness-of-fit test confidence level',
      'Enable visualization outputs if needed',
      'Execute analysis and review distribution ranking results'
    ]
  },

  parameters: {
    essential: [
      {
        name: 'dataColumns',
        type: 'array',
        defaultValue: [],
        description: 'Column(s) to analyze (auto-detected if empty)',
        range: 'Valid numeric column names from input dataset'
      },
      {
        name: 'distributionTypes',
        type: 'multi-select',
        defaultValue: ['normal', 'log-normal', 'exponential', 'weibull', 'gamma'],
        options: ['normal', 'log-normal', 'exponential', 'weibull', 'gamma', 'beta', 'uniform', 'poisson', 'binomial', 'chi-square', 'student-t', 'f-distribution', 'pareto', 'laplace', 'logistic'],
        description: 'Distribution types to test and compare',
        range: 'One or more statistical distributions'
      },
      {
        name: 'confidenceLevel',
        type: 'number',
        defaultValue: 0.95,
        description: 'Confidence level for goodness-of-fit tests',
        range: '0.90-0.99'
      },
      {
        name: 'minimumSamples',
        type: 'number',
        defaultValue: 30,
        description: 'Minimum samples required for reliable analysis',
        range: '30-1000'
      },
      {
        name: 'outlierHandling',
        type: 'select',
        defaultValue: 'auto-detect',
        options: ['none', 'auto-detect', 'iqr-method', 'z-score', 'modified-z-score'],
        description: 'Outlier detection and handling strategy',
        range: 'Statistical outlier detection methods'
      }
    ],
    advanced: [
      {
        name: 'goodnessOfFitTests',
        type: 'object',
        defaultValue: { 
          ksTest: true, 
          andersonDarling: true, 
          chiSquare: false, 
          shapiroWilk: true,
          lilliefors: false 
        },
        description: 'Statistical tests for distribution fitting',
        notes: 'Multiple tests provide robust distribution identification'
      },
      {
        name: 'parameterEstimation',
        type: 'object',
        defaultValue: { method: 'mle', confidenceIntervals: true, bootstrapSamples: 1000 },
        description: 'Parameter estimation methods and confidence calculation',
        notes: 'MLE provides optimal parameter estimates'
      },
      {
        name: 'mixtureModeling',
        type: 'object',
        defaultValue: { enabled: false, maxComponents: 5, selectionCriterion: 'bic' },
        description: 'Gaussian Mixture Model for multi-modal distributions',
        notes: 'Identifies multiple overlapping distributions'
      },
      {
        name: 'visualization',
        type: 'object',
        defaultValue: { 
          generatePlots: true, 
          plotTypes: ['histogram', 'qq-plot', 'pp-plot'], 
          overlayBestFit: true,
          savePlots: false 
        },
        description: 'Visualization and plotting configuration',
        notes: 'Visual validation of distribution fits'
      },
      {
        name: 'processControl',
        type: 'object',
        defaultValue: { 
          generateControlLimits: false, 
          controlLimitSigma: 3, 
          spcChartType: 'x-bar',
          capability: false 
        },
        description: 'Statistical process control integration',
        notes: 'Generates control charts and capability indices'
      }
    ]
  },

  examples: [
    {
      title: 'Temperature Process Analysis',
      description: 'Analyze distillation column temperature distribution for process control optimization',
      config: {
        dataColumns: ['column_temperature'],
        distributionTypes: ['normal', 'log-normal', 'weibull'],
        outlierHandling: 'iqr-method',
        parameterEstimation: { method: 'mle', confidenceIntervals: true },
        processControl: { generateControlLimits: true, controlLimitSigma: 3 }
      }
    },
    {
      title: 'Multi-Modal Quality Data',
      description: 'Identify multiple quality distributions in batch production data',
      config: {
        dataColumns: ['batch_quality_score'],
        distributionTypes: ['normal', 'gamma', 'beta'],
        mixtureModeling: { enabled: true, maxComponents: 3, selectionCriterion: 'aic' },
        visualization: { generatePlots: true, plotTypes: ['histogram', 'qq-plot'], savePlots: true }
      }
    }
  ],

  bestPractices: {
    dos: [
      'Ensure sufficient sample size (100+ recommended) for reliable distribution fitting',
      'Handle outliers appropriately based on process knowledge',
      'Use multiple goodness-of-fit tests for robust identification',
      'Consider mixture models for complex multi-modal industrial data',
      'Validate distribution assumptions with domain expertise',
      'Generate confidence intervals for distribution parameters'
    ],
    donts: [
      "Don't rely on single goodness-of-fit test for critical applications",
      "Don't ignore outliers without investigating their process significance",
      "Don't assume normality without proper testing",
      "Don't apply distributions outside their valid parameter ranges",
      "Don't skip visual validation of distribution fits"
    ],
    performanceTips: [
      'Use Anderson-Darling test for detecting distribution tail behavior',
      'Apply Q-Q plots for visual validation of distribution fits',
      'Consider transformed distributions for non-standard process data',
      'Use mixture models when single distributions fail to fit adequately'
    ]
  },

  troubleshooting: {
    commonIssues: [
      {
        issue: 'No Distributions Pass Goodness-of-Fit Tests',
        symptoms: 'All tested distributions rejected by statistical tests',
        cause: 'Data may follow non-standard distribution or contain multiple populations',
        solution: [
          'Try mixture modeling with multiple components',
          'Check for outliers or data quality issues',
          'Consider non-parametric approaches',
          'Apply data transformations (log, Box-Cox, etc.)'
        ]
      },
      {
        issue: 'Parameter Estimation Convergence Failure',
        symptoms: 'Maximum likelihood estimation fails to converge',
        cause: 'Insufficient data, poor initial estimates, or distribution mismatch',
        solution: [
          'Increase sample size if possible',
          'Try method of moments for initial parameter estimates',
          'Check data preprocessing and outlier removal',
          'Consider alternative distribution types'
        ]
      },
      {
        issue: 'Mixture Model Overfitting',
        symptoms: 'Mixture model selects too many components',
        cause: 'Model complexity penalty insufficient or noise in data',
        solution: [
          'Use stricter information criteria (BIC vs AIC)',
          'Apply data smoothing or filtering',
          'Limit maximum number of mixture components',
          'Validate with holdout data for component selection'
        ]
      }
    ],
    errorCodes: [
      { code: 'DA001', message: 'Insufficient data points', solution: 'Provide at least 30 data points for analysis' },
      { code: 'DA002', message: 'Non-numeric data detected', solution: 'Ensure all analysis columns contain numeric data' },
      { code: 'DA003', message: 'Constant values detected', solution: 'Remove columns with zero variance' },
      { code: 'DA004', message: 'Distribution fitting failed', solution: 'Check data quality and try alternative distributions' }
    ]
  },

  relatedNodes: {
    inputNodes: [
      { name: 'Data Cleaner', description: 'Provides cleaned data for distribution analysis' },
      { name: 'Outlier Detector', description: 'Preprocesses data by removing outliers' },
      { name: 'Time Series Processor', description: 'Prepares temporal data for distribution analysis' }
    ],
    outputNodes: [
      { name: 'Process Control Chart', description: 'Uses distribution parameters for control limits' },
      { name: 'Statistical Report Generator', description: 'Creates detailed statistical analysis reports' },
      { name: 'Visualization Dashboard', description: 'Displays distribution analysis results' }
    ],
    complementaryNodes: [
      { name: 'Hypothesis Tester', description: 'Performs statistical hypothesis testing' },
      { name: 'Correlation Analyzer', description: 'Analyzes relationships between distributions' },
      { name: 'Process Capability Calculator', description: 'Calculates process capability indices' }
    ]
  },

  apiReference: {
    nodeClass: `class DistributionAnalyzerNode extends IndustrialNode {
  config: DistributionAnalyzerConfig;
  
  async analyzeDistribution(data: NumericDataset): Promise<DistributionAnalysis>
  async fitDistributions(): Promise<DistributionRanking>
  async generateVisualizations(): Promise<PlotCollection>
  async calculateParameters(): Promise<ParameterEstimates>
}`,
    configInterface: `interface DistributionAnalyzerConfig {
  dataColumns: string[];
  distributionTypes: DistributionType[];
  confidenceLevel: number;
  minimumSamples: number;
  outlierHandling: OutlierMethod;
  goodnessOfFitTests?: GoodnessOfFitConfig;
  parameterEstimation?: ParameterEstimationConfig;
  mixtureModeling?: MixtureModelingConfig;
  visualization?: VisualizationConfig;
}`,
    events: [
      'onDataValidation: Fired during initial data quality assessment',
      'onOutlierDetection: Fired when outliers are identified',
      'onDistributionFitting: Fired during distribution parameter estimation',
      'onGoodnessOfFitTesting: Fired during statistical hypothesis testing',
      'onVisualizationGeneration: Fired when creating diagnostic plots',
      'onAnalysisComplete: Fired when complete distribution analysis finishes'
    ]
  },

  additionalResources: {
    externalDocs: [
      { name: 'SciPy Statistical Distributions', url: 'https://docs.scipy.org/doc/scipy/reference/stats.html' },
      { name: 'Statistical Distribution Fitting Guide', url: 'https://en.wikipedia.org/wiki/Statistical_model_validation' },
      { name: 'Process Control Statistics', url: 'https://example.com/process-control-statistics' }
    ],
    communityResources: [
      { name: 'Statistical Process Control Forum', url: 'https://forum.plc-gbt.com/statistical-analysis' },
      { name: 'Distribution Analysis Examples', url: 'https://github.com/plc-gbt/distribution-examples' }
    ]
  },

  version: '1.0.0',
  lastUpdated: 'January 2025',
  appliesTo: 'PLC-GBT v3.1.0+'
};

export default function DistributionAnalyzerDocumentation() {
  return <NodeDocumentationTemplate {...DISTRIBUTION_ANALYZER_DATA} />;
}
