# CSV Dataset Creator

## Overview
Transform and curate industrial data into high-quality CSV datasets with specialized templates for ML, MPC, dashboards, and reporting

**Category**: Data Processing > Dataset Generation

## Operation Modes


### ML Dataset Creator
**Target Application**: Machine Learning Training  
**Description**: Machine learning training data preparation with feature engineering and train/validation splitting

#### Additional Parameters

- **Train/Test Split Ratio** (`trainTestSplit`): Ratio of data for training vs testing (0.5-0.95)
  - Type: number
  - Required: Yes
  - Default: `0.8`

- **Feature Engineering** (`featureEngineering`): Enable automatic feature engineering and selection
  - Type: boolean
  - Required: No
  - Default: `true`

- **Target Column** (`targetColumn`): Name of the column to predict (dependent variable)
  - Type: string
  - Required: Yes
  


### MPC Dataset Creator
**Target Application**: Model Predictive Control  
**Description**: Model Predictive Control data formatting with process variables and control constraints

#### Additional Parameters

- **Control Horizon** (`controlHorizon`): MPC control horizon length (time steps)
  - Type: number
  - Required: Yes
  - Default: `10`

- **Prediction Horizon** (`predictionHorizon`): MPC prediction horizon length (time steps)
  - Type: number
  - Required: Yes
  - Default: `20`

- **Process Variables** (`processVariables`): JSON array of process variable definitions with min/max constraints
  - Type: json
  - Required: Yes
  


### Dashboard Dataset Creator
**Target Application**: Real-time Dashboards  
**Description**: Real-time dashboard data feeds with time-series optimization and aggregation

#### Additional Parameters

- **Data Aggregation Interval** (`aggregationInterval`): Time interval for data aggregation
  - Type: options
  - Required: Yes
  - Default: `1m`

- **Time Series Optimization** (`timeSeriesOptimization`): Optimize data structure for time-series queries
  - Type: boolean
  - Required: No
  - Default: `true`


### Report Dataset Creator
**Target Application**: Business & Compliance Reporting  
**Description**: Business and compliance reporting data with audit trails and regulatory formatting

#### Additional Parameters

- **Enable Audit Trail** (`auditTrail`): Include audit trail metadata for compliance
  - Type: boolean
  - Required: No
  - Default: `true`

- **Reporting Standard** (`reportingStandard`): Compliance standard for data formatting
  - Type: options
  - Required: Yes
  - Default: `iso21500`



## Technical Specification

### Development Phases

#### Phase 1: Architecture & Input Configuration
**Status**: APPROVED  
**Description**: Core input system and template management foundation

**Parameters**:

- **Dataset Name** (`datasetName`): Descriptive name for this dataset
  - Type: string
  - Required: Yes
  

- **Input Source Type** (`inputSource`): Source format of input data
  - Type: options
  - Required: Yes
  - Default: `json`

- **Template Configuration** (`templateMode`): How to configure dataset parameters
  - Type: options
  - Required: Yes
  - Default: `predefined`


**Validation Rules**:

- **dataset_name_required**: Dataset name is required for file organization

- **valid_input_source**: Input source must be a supported data format


#### Phase 2: Data Processing & Parsing
**Status**: APPROVED  
**Description**: CSV parsing, delimiter detection, and encoding configuration

**Parameters**:

- **Field Delimiter** (`delimiter`): CSV field separator character
  - Type: options
  - Required: Yes
  - Default: `,`

- **Character Encoding** (`encoding`): Text encoding of the data source
  - Type: options
  - Required: Yes
  - Default: `utf-8`

- **Has Header Row** (`hasHeader`): First row contains column names
  - Type: boolean
  - Required: No
  - Default: `true`

- **Skip Rows** (`skipRows`): Number of rows to skip at beginning
  - Type: number
  - Required: No
  


**Validation Rules**:

- **valid_encoding**: Character encoding must be supported


#### Phase 3: Data Cleaning & Quality
**Status**: APPROVED  
**Description**: Data cleaning operations, null handling, and quality validation

**Parameters**:

- **Null Value Strategy** (`nullHandling`): How to handle missing/null values
  - Type: options
  - Required: Yes
  - Default: `keep`

- **Outlier Detection** (`outlierDetection`): Method for detecting outliers
  - Type: options
  - Required: No
  - Default: `none`

- **Enable Data Validation** (`dataValidation`): Perform comprehensive data quality checks
  - Type: boolean
  - Required: No
  - Default: `true`


**Validation Rules**:

- **valid_null_strategy**: Null handling strategy must be specified


#### Phase 4: Formula & Transformation Engine
**Status**: APPROVED  
**Description**: Mathematical formulas, regex patterns, and data transformations

**Parameters**:

- **Enable Formula Engine** (`enableFormulas`): Enable mathematical formula transformations
  - Type: boolean
  - Required: No
  

- **Custom Formulas** (`formulas`): JSON array of formula definitions
  - Type: json
  - Required: No
  

- **RegEx Patterns** (`regexPatterns`): JSON array of regex pattern transformations
  - Type: json
  - Required: No
  

- **Data Normalization** (`normalization`): Normalization method for numerical columns
  - Type: options
  - Required: No
  - Default: `none`


**Validation Rules**:

- **formula_syntax_check**: Formula syntax must be valid mathematical expressions


#### Phase 5: Template Management System
**Status**: APPROVED  
**Description**: Template storage, versioning, and LLM-assisted creation

**Parameters**:

- **Save as Template** (`saveAsTemplate`): Save current configuration as reusable template
  - Type: boolean
  - Required: No
  

- **Template Name** (`templateName`): Name for saved template
  - Type: string
  - Required: No
  

- **Template Tags** (`templateTags`): Comma-separated tags for template categorization
  - Type: string
  - Required: No
  

- **Enable LLM Template Assistance** (`llmAssistance`): Use AI assistance for template optimization and suggestions
  - Type: boolean
  - Required: No
  


**Validation Rules**:

- **template_name_if_saving**: Template name is required when saving as template


#### Phase 6: Output Format & Export
**Status**: APPROVED  
**Description**: Multi-format output, metadata inclusion, and large dataset handling

**Parameters**:

- **Primary Output Format** (`outputFormat`): Main format for dataset output
  - Type: options
  - Required: Yes
  - Default: `csv`

- **Include Metadata** (`includeMetadata`): Include processing metadata in output
  - Type: boolean
  - Required: No
  - Default: `true`

- **Compression Level** (`compressionLevel`): Compression level for output files
  - Type: options
  - Required: No
  - Default: `standard`

- **Chunk Size (MB)** (`chunkSize`): Maximum size per output file chunk
  - Type: number
  - Required: No
  - Default: `100`


**Validation Rules**:

- **valid_chunk_size**: Chunk size must be between 1 and 1000 MB


#### Phase 7: Advanced Validation & Quality Control
**Status**: APPROVED  
**Description**: Comprehensive validation rules, conflict resolution, and quality scoring

**Parameters**:

- **Validation Level** (`validationLevel`): Depth of data validation to perform
  - Type: options
  - Required: Yes
  - Default: `standard`

- **Quality Score Threshold** (`qualityThreshold`): Minimum quality score to accept dataset (0.0-1.0)
  - Type: number
  - Required: No
  - Default: `0.8`

- **Conflict Resolution Strategy** (`conflictResolution`): How to handle data conflicts and inconsistencies
  - Type: options
  - Required: No
  - Default: `prompt`

- **Generate Quality Report** (`generateReport`): Create detailed data quality and processing report
  - Type: boolean
  - Required: No
  - Default: `true`


**Validation Rules**:

- **valid_quality_threshold**: Quality threshold must be between 0.0 and 1.0



## Usage Examples

### Basic Usage
```json
{
  "operationMode": "standard",
  // Add example parameters
}
```


### ML Dataset Creator Mode Example
```json
{
  "operationMode": "ml-dataset",
  // Add mode-specific parameters
}
```

### MPC Dataset Creator Mode Example
```json
{
  "operationMode": "mpc-dataset",
  // Add mode-specific parameters
}
```

### Dashboard Dataset Creator Mode Example
```json
{
  "operationMode": "dashboard-dataset",
  // Add mode-specific parameters
}
```

### Report Dataset Creator Mode Example
```json
{
  "operationMode": "report-dataset",
  // Add mode-specific parameters
}
```


## Integration Notes

- **Input**: Accepts any JSON data structure
- **Output**: Enhanced JSON with processing metadata
- **Validation**: Comprehensive validation across all phases
- **Performance**: Optimized for industrial data processing

## Error Handling

The node implements comprehensive error handling including:
- Parameter validation
- Input data validation
- Processing error recovery
- Detailed error reporting

## Related Nodes

This node is part of the PLC-GBT industrial automation suite and works seamlessly with other industrial nodes in the ecosystem.
