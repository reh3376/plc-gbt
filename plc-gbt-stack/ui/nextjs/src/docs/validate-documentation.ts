#!/usr/bin/env tsx

/**
 * 📋 Documentation Validation System - AI Task Orchestrator Implementation
 *
 * Validates generated node documentation for completeness, accuracy, and quality standards
 */

import fs from 'fs';
import path from 'path';

interface DocumentationValidationResult {
  readonly filePath: string;
  readonly nodeType: string;
  readonly valid: boolean;
  readonly score: number;
  readonly wordCount: number;
  readonly sectionCount: number;
  readonly issues: readonly ValidationIssue[];
  readonly recommendations: readonly string[];
}

interface ValidationIssue {
  readonly severity: 'error' | 'warning' | 'info';
  readonly category: string;
  readonly message: string;
  readonly section?: string;
}

interface ValidationCriteria {
  readonly minWordCount: number;
  readonly minSectionCount: number;
  readonly requiredSections: readonly string[];
  readonly requiredKeywords: readonly string[];
  readonly forbiddenPatterns: readonly RegExp[];
}

class DocumentationValidator {
  private readonly validationCriteria: ValidationCriteria = {
    minWordCount: 1000,
    minSectionCount: 30,
    requiredSections: [
      'Overview',
      'Configuration Guide',
      'Parameters Reference',
      'Examples',
      'Best Practices',
      'Troubleshooting',
      'Related Nodes',
      'API Reference',
    ],
    requiredKeywords: [
      'industrial',
      'configuration',
      'parameters',
      'example',
      'troubleshooting',
      'validation',
      'performance',
    ],
    forbiddenPatterns: [
      /\[TODO\]/gi,
      /\[PLACEHOLDER\]/gi,
      /\[TBD\]/gi,
      /lorem ipsum/gi,
      /undefined|null|NaN/g,
    ],
  };

  /**
   * Validate all documentation files in the nodes directory
   */
  public async validateAllDocumentation(
    docsDirectory: string = 'src/docs/nodes'
  ): Promise<readonly DocumentationValidationResult[]> {
    console.log('🔍 Starting Documentation Validation...\n');

    const results: DocumentationValidationResult[] = [];

    if (!fs.existsSync(docsDirectory)) {
      console.error(`❌ Documentation directory not found: ${docsDirectory}`);
      return results;
    }

    const files = fs
      .readdirSync(docsDirectory)
      .filter(file => file.endsWith('.md') && !file.startsWith('PROTOTYPE_DOCUMENTATION'))
      .sort();

    for (const file of files) {
      const filePath = path.join(docsDirectory, file);
      console.log(`📝 Validating: ${file}`);

      const result = await this.validateDocumentationFile(filePath);
      results.push(result);

      this.logValidationResult(result);
    }

    await this.generateValidationReport(results, docsDirectory);

    console.log('\n✅ Documentation Validation Complete!\n');
    return results;
  }

  /**
   * Validate a single documentation file
   */
  private async validateDocumentationFile(
    filePath: string
  ): Promise<DocumentationValidationResult> {
    const nodeType = path.basename(filePath, '.md');

    try {
      const content = await fs.promises.readFile(filePath, 'utf-8');
      const issues: ValidationIssue[] = [];
      const recommendations: string[] = [];

      // Count metrics
      const wordCount = this.countWords(content);
      const sectionCount = this.countSections(content);

      // Validate content structure
      this.validateContentStructure(content, issues);

      // Validate content quality
      this.validateContentQuality(content, issues, recommendations);

      // Validate technical accuracy
      this.validateTechnicalContent(content, issues, recommendations);

      // Calculate overall score
      const score = this.calculateValidationScore(wordCount, sectionCount, issues);
      const valid = issues.filter(i => i.severity === 'error').length === 0 && score >= 70;

      return {
        filePath,
        nodeType,
        valid,
        score,
        wordCount,
        sectionCount,
        issues,
        recommendations,
      };
    } catch (error) {
      return {
        filePath,
        nodeType,
        valid: false,
        score: 0,
        wordCount: 0,
        sectionCount: 0,
        issues: [
          {
            severity: 'error',
            category: 'file_access',
            message: `Failed to read file: ${
              error instanceof Error ? error.message : String(error)
            }`,
          },
        ],
        recommendations: ['Ensure file exists and is readable'],
      };
    }
  }

  /**
   * Validate document structure and required sections
   */
  private validateContentStructure(content: string, issues: ValidationIssue[]): void {
    const sections = this.extractSections(content);

    // Check for required sections
    for (const requiredSection of this.validationCriteria.requiredSections) {
      const hasSection = sections.some(section =>
        section.toLowerCase().includes(requiredSection.toLowerCase())
      );

      if (!hasSection) {
        issues.push({
          severity: 'error',
          category: 'structure',
          message: `Missing required section: ${requiredSection}`,
        });
      }
    }

    // Check minimum section count
    if (sections.length < this.validationCriteria.minSectionCount) {
      issues.push({
        severity: 'warning',
        category: 'completeness',
        message: `Insufficient section count: ${sections.length} (minimum: ${this.validationCriteria.minSectionCount})`,
      });
    }

    // Check for empty sections
    const emptySections = sections.filter(section => {
      const sectionRegex = new RegExp(`## ${section}([\\s\\S]*?)(?=## |$)`, 'i');
      const match = content.match(sectionRegex);
      return !match || match[1].trim().length < 50;
    });

    if (emptySections.length > 0) {
      issues.push({
        severity: 'warning',
        category: 'completeness',
        message: `Empty or minimal sections detected: ${emptySections.join(', ')}`,
      });
    }
  }

  /**
   * Validate content quality and completeness
   */
  private validateContentQuality(
    content: string,
    issues: ValidationIssue[],
    recommendations: string[]
  ): void {
    const wordCount = this.countWords(content);

    // Check minimum word count
    if (wordCount < this.validationCriteria.minWordCount) {
      issues.push({
        severity: 'warning',
        category: 'completeness',
        message: `Insufficient content length: ${wordCount} words (minimum: ${this.validationCriteria.minWordCount})`,
      });
    }

    // Check for forbidden patterns
    for (const pattern of this.validationCriteria.forbiddenPatterns) {
      const matches = content.match(pattern);
      if (matches) {
        issues.push({
          severity: 'error',
          category: 'quality',
          message: `Forbidden content detected: ${matches[0]} (${matches.length} occurrences)`,
        });
      }
    }

    // Check for required keywords
    const missingKeywords = this.validationCriteria.requiredKeywords.filter(
      keyword => !content.toLowerCase().includes(keyword.toLowerCase())
    );

    if (missingKeywords.length > 0) {
      recommendations.push(`Consider adding missing keywords: ${missingKeywords.join(', ')}`);
    }

    // Check for code examples
    const codeBlocks = (content.match(/```[\s\S]*?```/g) || []).length;
    if (codeBlocks < 3) {
      recommendations.push('Add more code examples to improve technical documentation');
    }

    // Check for external links
    const externalLinks = (content.match(/\[.*?\]\(https?:\/\/.*?\)/g) || []).length;
    if (externalLinks < 2) {
      recommendations.push('Add external references and documentation links');
    }
  }

  /**
   * Validate technical content accuracy
   */
  private validateTechnicalContent(
    content: string,
    issues: ValidationIssue[],
    recommendations: string[]
  ): void {
    // Check for parameter documentation
    if (!content.includes('Parameters Reference') && !content.includes('parameters')) {
      issues.push({
        severity: 'warning',
        category: 'technical',
        message: 'Missing parameter documentation',
      });
    }

    // Check for examples
    if (!content.includes('Examples') && !content.includes('example')) {
      issues.push({
        severity: 'warning',
        category: 'technical',
        message: 'Missing usage examples',
      });
    }

    // Check for troubleshooting
    if (!content.includes('Troubleshooting') && !content.includes('troubleshooting')) {
      issues.push({
        severity: 'warning',
        category: 'technical',
        message: 'Missing troubleshooting information',
      });
    }

    // Technical accuracy checks
    const technicalIndicators = [
      'configuration',
      'validation',
      'error handling',
      'performance',
      'security',
      'best practices',
    ];

    const missingIndicators = technicalIndicators.filter(
      indicator => !content.toLowerCase().includes(indicator)
    );

    if (missingIndicators.length > 2) {
      recommendations.push(
        `Enhance technical coverage: ${missingIndicators.slice(0, 3).join(', ')}`
      );
    }
  }

  /**
   * Calculate validation score based on various factors
   */
  private calculateValidationScore(
    wordCount: number,
    sectionCount: number,
    issues: ValidationIssue[]
  ): number {
    let score = 100;

    // Deduct points for issues
    issues.forEach(issue => {
      switch (issue.severity) {
        case 'error':
          score -= 20;
          break;
        case 'warning':
          score -= 10;
          break;
        case 'info':
          score -= 2;
          break;
      }
    });

    // Bonus points for exceeding minimums
    if (wordCount > this.validationCriteria.minWordCount * 1.5) {
      score += 5;
    }

    if (sectionCount > this.validationCriteria.minSectionCount * 1.2) {
      score += 5;
    }

    return Math.max(0, Math.min(100, score));
  }

  /**
   * Extract section headers from markdown content
   */
  private extractSections(content: string): readonly string[] {
    const matches = content.match(/^#{2,6}\s+(.+)$/gm);
    return matches ? matches.map(match => match.replace(/^#{2,6}\s+/, '').trim()) : [];
  }

  /**
   * Count words in content
   */
  private countWords(content: string): number {
    return content
      .replace(/```[\s\S]*?```/g, '') // Remove code blocks
      .replace(/#{1,6}\s/g, '') // Remove headers
      .replace(/[^\w\s]/g, ' ') // Replace non-word chars with spaces
      .split(/\s+/)
      .filter(word => word.length > 0).length;
  }

  /**
   * Count sections in content
   */
  private countSections(content: string): number {
    return (content.match(/^#{1,6}\s/gm) || []).length;
  }

  /**
   * Log validation result summary
   */
  private logValidationResult(result: DocumentationValidationResult): void {
    const status = result.valid ? '✅' : '❌';
    const scoreColor = result.score >= 80 ? '🟢' : result.score >= 60 ? '🟡' : '🔴';

    console.log(
      `  ${status} Score: ${result.score}/100 ${scoreColor} | ${result.wordCount} words, ${result.sectionCount} sections`
    );

    if (result.issues.length > 0) {
      const errorCount = result.issues.filter(i => i.severity === 'error').length;
      const warningCount = result.issues.filter(i => i.severity === 'warning').length;
      console.log(`     Issues: ${errorCount} errors, ${warningCount} warnings`);
    }
  }

  /**
   * Generate comprehensive validation report
   */
  private async generateValidationReport(
    results: readonly DocumentationValidationResult[],
    outputDir: string
  ): Promise<void> {
    const validCount = results.filter(r => r.valid).length;
    const avgScore = results.reduce((sum, r) => sum + r.score, 0) / results.length;
    const totalWords = results.reduce((sum, r) => sum + r.wordCount, 0);
    const totalSections = results.reduce((sum, r) => sum + r.sectionCount, 0);

    const report = `# 📋 Documentation Validation Report

## 🎯 Validation Summary

**Validation Date**: ${new Date().toISOString().split('T')[0]}  
**Total Documents**: ${results.length}  
**Valid Documents**: ${validCount}  
**Invalid Documents**: ${results.length - validCount}  
**Average Score**: ${avgScore.toFixed(1)}/100  
**Total Word Count**: ${totalWords.toLocaleString()}  
**Total Sections**: ${totalSections}  

---

## 📊 Individual Document Results

| Document | Status | Score | Word Count | Sections | Issues |
|----------|--------|-------|------------|----------|--------|
${results
  .map(r => {
    const status = r.valid ? '✅ Valid' : '❌ Invalid';
    const errorCount = r.issues.filter(i => i.severity === 'error').length;
    const warningCount = r.issues.filter(i => i.severity === 'warning').length;
    const issueText = `${errorCount}E, ${warningCount}W`;

    return `| \`${r.nodeType}\` | ${status} | ${r.score}/100 | ${r.wordCount.toLocaleString()} | ${
      r.sectionCount
    } | ${issueText} |`;
  })
  .join('\n')}

## 🔍 Quality Analysis

### **✅ High Quality Documents** (Score ≥ 80)
${
  results
    .filter(r => r.score >= 80)
    .map(r => `- **${r.nodeType}**: ${r.score}/100 (${r.wordCount.toLocaleString()} words)`)
    .join('\n') || '- None'
}

### **⚠️ Documents Needing Improvement** (Score < 80)
${
  results
    .filter(r => r.score < 80)
    .map(
      r =>
        `- **${r.nodeType}**: ${r.score}/100 - ${r.issues
          .slice(0, 2)
          .map(i => i.message)
          .join(', ')}`
    )
    .join('\n') || '- None'
}

## 🚨 Issues Summary

### **Critical Errors** (Must Fix)
${
  results
    .flatMap(r => r.issues.filter(i => i.severity === 'error'))
    .slice(0, 10)
    .map(issue => `- **${issue.category}**: ${issue.message}`)
    .join('\n') || '- None detected'
}

### **Warnings** (Should Fix)
${
  results
    .flatMap(r => r.issues.filter(i => i.severity === 'warning'))
    .slice(0, 10)
    .map(issue => `- **${issue.category}**: ${issue.message}`)
    .join('\n') || '- None detected'
}

## 💡 Recommendations

### **Content Improvement**
${
  results
    .flatMap(r => r.recommendations)
    .slice(0, 8)
    .map(rec => `- ${rec}`)
    .join('\n') || '- Documentation meets quality standards'
}

### **Next Steps**
1. **Address Critical Errors**: Fix all error-level issues before deployment
2. **Improve Low-Scoring Documents**: Focus on documents with scores < 70
3. **Enhance Technical Coverage**: Add more examples and troubleshooting content
4. **User Testing**: Validate documentation with actual users
5. **Continuous Improvement**: Regular reviews and updates

## 🎉 **Validation Results: ${validCount}/${results.length} Documents Pass**

${
  validCount === results.length
    ? '✅ **ALL DOCUMENTATION VALIDATED SUCCESSFULLY!**\n\nThe prototype node documentation meets production quality standards and is ready for integration with the Node Properties Modal system.'
    : `⚠️ **${
        results.length - validCount
      } documents need attention before production deployment.**\n\nFocus on addressing critical errors and improving low-scoring documents.`
}

---

**Validation System**: PLC-GBT Documentation Validator v1.0  
**AI Task Orchestrator**: TypeScript Implementation  
**Quality Standards**: Industrial Documentation Requirements  

*This validation ensures all node documentation meets professional standards for technical accuracy, completeness, and user experience.*`;

    const reportPath = path.join(outputDir, 'DOCUMENTATION_VALIDATION_REPORT.md');
    await fs.promises.writeFile(reportPath, report, 'utf-8');

    console.log(`\n📊 Validation report generated: ${reportPath}`);
  }
}

// Execute validation if run directly
if (require.main === module) {
  const validator = new DocumentationValidator();
  validator
    .validateAllDocumentation()
    .then(results => {
      const validCount = results.filter(r => r.valid).length;
      const avgScore = results.reduce((sum, r) => sum + r.score, 0) / results.length;

      console.log(`\n🎉 Validation completed: ${validCount}/${results.length} documents valid`);
      console.log(`📊 Average quality score: ${avgScore.toFixed(1)}/100`);

      if (validCount < results.length || avgScore < 70) {
        console.warn('⚠️  Some documentation needs improvement - check validation report');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('💥 Fatal error during validation:', error);
      process.exit(1);
    });
}

export default DocumentationValidator;
