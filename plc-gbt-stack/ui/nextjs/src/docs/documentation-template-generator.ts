#!/usr/bin/env tsx

/**
 * 📝 Documentation Template Generator - AI Task Orchestrator Implementation
 *
 * Generates comprehensive markdown documentation from NodeDocumentationSpec
 * following the master template structure defined in the roadmap
 */

import type {
  ConfigurationStep,
  ErrorCode,
  ExampleConfiguration,
  NodeDocumentationSpec,
  ParameterDefinition,
  TroubleshootingIssue,
} from './node-documentation-system';

export class DocumentationTemplateGenerator {
  /**
   * Generate complete markdown documentation from specification
   */
  public static generateMarkdownDocumentation(spec: NodeDocumentationSpec): string {
    const sections = [
      this.generateHeader(spec),
      this.generateOverview(spec),
      this.generateConfigurationGuide(spec),
      this.generateParametersReference(spec),
      this.generateExamples(spec),
      this.generateBestPractices(spec),
      this.generateTroubleshooting(spec),
      this.generateRelatedNodes(spec),
      this.generateAPIReference(spec),
      this.generateAdditionalResources(spec),
      this.generateFooter(spec),
    ];

    return sections.join('\n\n');
  }

  /**
   * Generate category-specific template extensions
   */
  public static generateCategoryExtensions(spec: NodeDocumentationSpec): string {
    const extensions: string[] = [];

    switch (spec.category.id) {
      case 'plc_control':
        extensions.push(this.generateControlTheorySection(spec));
        break;
      case 'data_sources':
        extensions.push(this.generateDatabaseSpecificsSection(spec));
        break;
      case 'ml_algorithm':
        extensions.push(this.generateMLModelSection(spec));
        break;
      case 'mpc_control':
        extensions.push(this.generateMPCSection(spec));
        break;
      case 'data_processing':
        extensions.push(this.generateDataProcessingSection(spec));
        break;
      case 'reporting':
        extensions.push(this.generateReportingSection(spec));
        break;
      default:
        // No specific extensions
        break;
    }

    return extensions.join('\n\n');
  }

  // Private helper methods for each section

  private static generateHeader(spec: NodeDocumentationSpec): string {
    return `# ${spec.title} - Industrial Control Node

**Node Type**: \`${spec.nodeType}\`  
**Category**: ${spec.category.name}  
**Version**: ${spec.version}  
**Last Updated**: ${spec.lastUpdated}

---

${spec.description}`;
  }

  private static generateOverview(spec: NodeDocumentationSpec): string {
    const { overview } = spec;

    return `## 🎯 Overview

### Purpose
${overview.purpose}

### Key Features
${overview.keyFeatures
  .map(feature => `- **${feature.split(':')[0]}**: ${feature.split(':')[1] || feature}`)
  .join('\n')}

### When to Use This Node
${overview.whenToUse
  .map(useCase => `- **${useCase.split(':')[0]}**: ${useCase.split(':')[1] || useCase}`)
  .join('\n')}

### Industrial Applications
${
  overview.industrialApplications?.map(app => `- ${app}`).join('\n') ||
  '- Process control and automation\n- Data acquisition and monitoring\n- System optimization and tuning'
}`;
  }

  private static generateConfigurationGuide(spec: NodeDocumentationSpec): string {
    const { configurationGuide } = spec;

    return `## ⚙️ Configuration Guide

### Quick Start
${configurationGuide.quickStart.map((step, i) => `${i + 1}. ${step}`).join('\n')}

### Detailed Setup

${configurationGuide.detailedSteps
  .map(
    step =>
      `#### Step ${step.step}: ${step.title}
${step.description}

${
  step.parameters.length > 0
    ? `**Required Parameters:**
${step.parameters.map(param => `- \`${param}\``).join('\n')}`
    : ''
}

${
  step.codeExamples
    ? `**Example Configuration:**
\`\`\`json
${step.codeExamples.join('\n')}
\`\`\``
    : ''
}`
  )
  .join('\n\n')}

### Best Practices
${configurationGuide.bestPractices.map(practice => `- ✅ ${practice}`).join('\n')}

### Common Mistakes to Avoid
${configurationGuide.commonMistakes.map(mistake => `- ❌ ${mistake}`).join('\n')}`;
  }

  private static generateParametersReference(spec: NodeDocumentationSpec): string {
    if (spec.parameters.length === 0) {
      return `## 📊 Parameters Reference

*No configurable parameters for this node type.*`;
    }

    const requiredParams = spec.parameters.filter(p => p.required);
    const optionalParams = spec.parameters.filter(p => !p.required);

    return `## 📊 Parameters Reference

### Essential Parameters

| Parameter | Type | Default | Range | Units | Description |
|-----------|------|---------|-------|-------|-------------|
${requiredParams
  .map(
    param =>
      `| \`${param.name}\` | ${param.type} | \`${this.formatValue(
        param.defaultValue
      )}\` | ${this.formatRange(param)} | ${param.units || '-'} | ${param.description} |`
  )
  .join('\n')}

${
  optionalParams.length > 0
    ? `### Advanced Parameters

| Parameter | Type | Default | Description | Notes |
|-----------|------|---------|-------------|-------|
${optionalParams
  .map(
    param =>
      `| \`${param.name}\` | ${param.type} | \`${this.formatValue(param.defaultValue)}\` | ${
        param.description
      } | ${this.generateParameterNotes(param)} |`
  )
  .join('\n')}`
    : ''
}

### Parameter Validation Rules
${spec.validation
  .map(
    rule =>
      `- **${rule.severity.toUpperCase()}**: ${rule.message}${
        rule.suggestion ? ` (${rule.suggestion})` : ''
      }`
  )
  .join('\n')}`;
  }

  private static generateExamples(spec: NodeDocumentationSpec): string {
    if (spec.examples.length === 0) {
      return `## 💡 Examples

### Basic Configuration
\`\`\`json
{
  "nodeType": "${spec.nodeType}",
  "config": {
    "enabled": true,
    "name": "Example ${spec.title}"
  }
}
\`\`\`

*More detailed examples will be added as this node type is used in production workflows.*`;
    }

    return `## 💡 Examples

${spec.examples
  .map(
    (example, i) => `### Example ${i + 1}: ${example.title}

**Use Case**: ${example.useCase}

${example.description}

\`\`\`json
${JSON.stringify(example.configuration, null, 2)}
\`\`\`

${
  example.expectedOutput
    ? `**Expected Output:**
\`\`\`
${example.expectedOutput}
\`\`\``
    : ''
}

${
  example.notes
    ? `**Notes:**
${example.notes.map(note => `- ${note}`).join('\n')}`
    : ''
}`
  )
  .join('\n\n')}`;
  }

  private static generateBestPractices(spec: NodeDocumentationSpec): string {
    return `## 🎯 Best Practices

### Configuration
- ✅ **Validate Input Data**: Always verify input data types and ranges before processing
- ✅ **Set Appropriate Timeouts**: Configure reasonable timeout values for industrial networks
- ✅ **Use Meaningful Names**: Give descriptive names to node instances for easy identification
- ✅ **Document Configuration**: Add comments explaining configuration choices
- ✅ **Test in Staging**: Validate configuration in non-production environment first

### Performance
- ✅ **Optimize Polling Intervals**: Balance data freshness with system performance
- ✅ **Monitor Resource Usage**: Track CPU, memory, and network utilization
- ✅ **Use Connection Pooling**: Reuse connections when possible to reduce overhead
- ✅ **Implement Caching**: Cache frequently accessed data to improve response times

### Security
- ✅ **Secure Credentials**: Use secure credential storage, never hardcode passwords
- ✅ **Enable Encryption**: Use encrypted connections when available (TLS/SSL)
- ✅ **Validate Certificates**: Verify SSL certificates in production environments
- ✅ **Implement Rate Limiting**: Protect against excessive requests and abuse

### Maintenance
- ✅ **Regular Updates**: Keep node configurations current with system changes
- ✅ **Monitor Logs**: Regularly review logs for warnings and errors
- ✅ **Backup Configuration**: Maintain backups of working configurations
- ✅ **Plan for Failure**: Implement graceful degradation and error recovery`;
  }

  private static generateTroubleshooting(spec: NodeDocumentationSpec): string {
    const { troubleshooting } = spec;

    return `## 🔧 Troubleshooting

### Common Issues

${troubleshooting.commonIssues
  .map(
    (issue, i) => `#### Issue ${i + 1}: ${issue.issue}

**Symptoms:**
${issue.symptoms.map(symptom => `- ${symptom}`).join('\n')}

**Possible Causes:**
${issue.causes.map(cause => `- ${cause}`).join('\n')}

**Solutions:**
${issue.solutions.map((solution, j) => `${j + 1}. ${solution}`).join('\n')}

${
  issue.prevention
    ? `**Prevention:**
${issue.prevention.map(prev => `- ${prev}`).join('\n')}`
    : ''
}`
  )
  .join('\n\n')}

${
  troubleshooting.errorCodes.length > 0
    ? `### Error Codes

| Code | Severity | Message | Solution |
|------|----------|---------|----------|
${troubleshooting.errorCodes
  .map(error => `| \`${error.code}\` | ${error.severity} | ${error.message} | ${error.solution} |`)
  .join('\n')}`
    : ''
}

### Diagnostic Procedures
${troubleshooting.diagnosticProcedures.map((procedure, i) => `${i + 1}. ${procedure}`).join('\n')}

### Getting Help
- **Documentation**: Check this guide and related node documentation
- **Connection Testing**: Use the built-in connection test feature
- **Log Analysis**: Review node execution logs for detailed error information
- **Community Support**: Search forums and community resources
- **Technical Support**: Contact technical support with error codes and logs`;
  }

  private static generateRelatedNodes(spec: NodeDocumentationSpec): string {
    if (spec.relatedNodes.length === 0) {
      return `## 🔗 Related Nodes

### Commonly Used Together
- Check the node palette for compatible nodes
- Review workflow examples for integration patterns
- Consider data flow requirements when selecting related nodes`;
    }

    return `## 🔗 Related Nodes

### Input Nodes
*Nodes that commonly provide input to this node*

### Output Nodes  
*Nodes that commonly receive output from this node*

### Complementary Nodes
*Nodes that work well in combination with this node*

${spec.relatedNodes
  .map(nodeId => `- **${nodeId}**: [Brief description of relationship]`)
  .join('\n')}

### Integration Patterns
- **Sequential Processing**: Connect output to input of compatible nodes
- **Parallel Processing**: Use multiple instances for load distribution
- **Conditional Logic**: Implement branching logic based on node outputs
- **Feedback Loops**: Create closed-loop control systems`;
  }

  private static generateAPIReference(spec: NodeDocumentationSpec): string {
    return `## 🔌 API Reference

### Node Interface
\`\`\`typescript
interface ${this.toPascalCase(spec.nodeType)}Config {
${spec.parameters
  .map(
    param =>
      `  ${param.name}${param.required ? '' : '?'}: ${this.getTypeScriptType(param)};${
        param.description ? ` // ${param.description}` : ''
      }`
  )
  .join('\n')}
}

class ${this.toPascalCase(spec.nodeType)}Node extends IndustrialControlNode {
  config: ${this.toPascalCase(spec.nodeType)}Config;
  
  async initialize(config: ${this.toPascalCase(spec.nodeType)}Config): Promise<void>;
  async process(input: NodeInput): Promise<NodeOutput>;
  async validate(): Promise<ValidationResult>;
  async cleanup(): Promise<void>;
}
\`\`\`

### Configuration Schema
\`\`\`json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
${spec.parameters
  .map(
    param => `    "${param.name}": {
      "type": "${param.type}",
      "description": "${param.description}"${
      param.defaultValue !== undefined
        ? `,\n      "default": ${JSON.stringify(param.defaultValue)}`
        : ''
    }${param.enumValues ? `,\n      "enum": ${JSON.stringify(param.enumValues)}` : ''}
    }`
  )
  .join(',\n')}
  },
  "required": [${spec.parameters
    .filter(p => p.required)
    .map(p => `"${p.name}"`)
    .join(', ')}]
}
\`\`\`

### Events
- **\`onInitialize\`**: Fired when node is initialized
- **\`onProcess\`**: Fired when node processes input data
- **\`onError\`**: Fired when an error occurs
- **\`onValidationChange\`**: Fired when validation status changes
- **\`onConfigurationChange\`**: Fired when configuration is modified`;
  }

  private static generateAdditionalResources(spec: NodeDocumentationSpec): string {
    return `## 📚 Additional Resources

### External Documentation
${spec.externalResources
  .map(resource => `- [${resource.title}](${resource.url}) - ${resource.description}`)
  .join('\n')}

### Standards and Specifications
- **Industry Standards**: Review applicable industry standards for this node type
- **Protocol Documentation**: Consult official protocol documentation where applicable
- **Safety Guidelines**: Follow industrial safety guidelines for control system implementation

### Training and Certification
- **Product Training**: Available through official training programs
- **Certification**: Professional certification programs for industrial automation
- **Continuing Education**: Stay current with industry developments and best practices

---

**Document Version**: ${spec.version}  
**Last Updated**: ${spec.lastUpdated}  
**Applies to PLC-GBT Version**: 2.0+  
**Template Category**: ${spec.templateCategory}

*This documentation is automatically generated from the node specification. For updates or corrections, please modify the source specification file.*`;
  }

  private static generateFooter(spec: NodeDocumentationSpec): string {
    return `---

## 📝 Documentation Metadata

- **Node Type ID**: \`${spec.nodeType}\`
- **Category**: ${spec.category.name} (\`${spec.category.id}\`)
- **Template Extensions**: ${spec.category.templateExtensions.join(', ')}
- **Generated**: ${new Date().toISOString()}
- **Documentation System**: PLC-GBT Node Documentation Generator v1.0

*This document follows the [PLC-GBT Documentation Standards](../documentation-standards.md) and is part of the comprehensive node documentation system.*`;
  }

  // Category-specific extension generators

  private static generateControlTheorySection(spec: NodeDocumentationSpec): string {
    return `## 🎛️ Control Theory

### Algorithm Description
*Mathematical description and theoretical foundation of the control algorithm*

### Tuning Guidelines
*Step-by-step tuning procedure for optimal performance*

1. **Initial Setup**: Configure basic parameters
2. **System Identification**: Characterize the process dynamics  
3. **Controller Design**: Apply appropriate tuning method
4. **Performance Validation**: Test and optimize performance
5. **Robustness Analysis**: Verify stability margins

### Stability Considerations
*Stability analysis and constraint guidelines*

- **Gain Margins**: Maintain adequate gain margins (>6dB recommended)
- **Phase Margins**: Ensure sufficient phase margins (>45° recommended)  
- **Bandwidth Limits**: Consider actuator and sensor bandwidth limitations
- **Nonlinear Effects**: Account for nonlinearities and saturation limits`;
  }

  private static generateDatabaseSpecificsSection(spec: NodeDocumentationSpec): string {
    return `## 🗄️ Database Integration

### Connection Configuration
\`\`\`
protocol://username:password@host:port/database?parameters
\`\`\`

### Query Optimization
*Database-specific optimization techniques and best practices*

### Performance Considerations
*Guidance for optimal database performance in industrial environments*

- **Connection Pooling**: Use connection pools for high-frequency operations
- **Query Optimization**: Index frequently queried columns
- **Batch Operations**: Group operations for better performance
- **Data Retention**: Implement appropriate data retention policies`;
  }

  private static generateMLModelSection(spec: NodeDocumentationSpec): string {
    return `## 🤖 Machine Learning Configuration

### Model Architecture
*Available model architectures and configuration options*

### Training Parameters
*Hyperparameter descriptions and tuning guidelines*

### Evaluation Metrics
*Performance metrics and interpretation guidelines*

- **Training Metrics**: Monitor loss convergence and overfitting
- **Validation Metrics**: Use appropriate validation techniques
- **Production Metrics**: Track model performance in deployment
- **Drift Detection**: Monitor for model degradation over time`;
  }

  private static generateMPCSection(spec: NodeDocumentationSpec): string {
    return `## 🎯 Model Predictive Control

### Constraint Handling
*Configuration and management of system constraints*

### Prediction Horizon
*Selection guidelines for prediction and control horizons*

### Optimization Parameters
*Economic optimization and performance tuning*

- **Objective Function**: Configure cost function weights
- **Constraint Priorities**: Set constraint violation penalties
- **Solver Settings**: Optimize solver parameters for real-time performance
- **Model Updates**: Implement adaptive model updating strategies`;
  }

  private static generateDataProcessingSection(spec: NodeDocumentationSpec): string {
    return `## 🔄 Data Processing Operations

### Data Transformation
*Available transformation operations and configurations*

### Processing Algorithms  
*Algorithm selection and parameter tuning*

### Performance Optimization
*Optimization strategies for large-scale data processing*

- **Memory Management**: Optimize memory usage for large datasets
- **Parallel Processing**: Utilize multi-core processing capabilities  
- **Streaming Processing**: Configure for real-time data streams
- **Batch Processing**: Optimize batch size for throughput`;
  }

  private static generateReportingSection(spec: NodeDocumentationSpec): string {
    return `## 📊 Reporting and Visualization

### Template Configuration
*Report template design and customization options*

### Output Formats
*Available output formats and configuration*

### Automation Settings
*Scheduling and automated report generation*

- **Report Scheduling**: Configure automated report generation
- **Distribution Lists**: Set up email distribution and notifications
- **Template Management**: Maintain and version report templates
- **Data Refresh**: Configure data refresh intervals and sources`;
  }

  // Helper methods

  private static formatValue(value: unknown): string {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'string') return `"${value}"`;
    return String(value);
  }

  private static formatRange(param: ParameterDefinition): string {
    if (param.range) {
      return `${param.range.min}-${param.range.max}${
        param.range.step ? ` (step: ${param.range.step})` : ''
      }`;
    }
    if (param.enumValues) {
      return param.enumValues.join(' | ');
    }
    return '-';
  }

  private static generateParameterNotes(param: ParameterDefinition): string {
    const notes: string[] = [];

    if (param.validation?.pattern) {
      notes.push(`Pattern: ${param.validation.pattern}`);
    }

    if (param.enumValues) {
      notes.push(`Options: ${param.enumValues.join(', ')}`);
    }

    if (param.examples) {
      notes.push(`Examples: ${param.examples.join(', ')}`);
    }

    return notes.join('; ') || 'Advanced parameter';
  }

  private static toPascalCase(str: string): string {
    return str
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');
  }

  private static getTypeScriptType(param: ParameterDefinition): string {
    switch (param.type) {
      case 'string':
        return 'string';
      case 'number':
        return 'number';
      case 'boolean':
        return 'boolean';
      case 'array':
        return 'unknown[]';
      case 'object':
        return 'Record<string, unknown>';
      case 'enum':
        return param.enumValues?.map(v => `"${v}"`).join(' | ') || 'string';
      default:
        return 'unknown';
    }
  }
}

export default DocumentationTemplateGenerator;
