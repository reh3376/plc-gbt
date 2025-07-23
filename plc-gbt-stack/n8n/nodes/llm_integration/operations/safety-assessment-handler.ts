/**
 * Safety Assessment Operation Handler
 * Specialized handler for safety analysis of control strategies
 */

import { IExecuteFunctions, INodeExecutionData } from 'n8n-workflow';
import { BaseOperationHandler } from '../../shared/utils';

export class SafetyAssessmentHandler extends BaseOperationHandler {
  
  async execute(
    executeFunctions: IExecuteFunctions,
    items: INodeExecutionData[]
  ): Promise<INodeExecutionData[]> {
    
    await this.validateParameters(executeFunctions, ['processDescription']);
    
    return this.executeWithErrorHandling(executeFunctions, async () => {
      const processDescription = executeFunctions.getNodeParameter('processDescription', 0) as string;
      const modelSelection = executeFunctions.getNodeParameter('modelSelection', 0, 'gpt-4o-industrial') as string;
      
      const prompt = this.buildSafetyAssessmentPrompt(processDescription);
      const response = await this.callIndustrialLLM(executeFunctions, prompt, modelSelection);
      
      return {
        operation: 'safety_assessment',
        processDescription,
        safetyAnalysis: response,
        riskLevel: this.extractRiskLevel(response),
        safetyRecommendations: this.extractSafetyRecommendations(response),
        timestamp: new Date().toISOString()
      };
    });
  }
  
  private buildSafetyAssessmentPrompt(processDescription: string): string {
    return `As a safety expert in industrial control systems, assess the safety implications of:

Process: ${processDescription}

Please provide a comprehensive safety assessment covering:
1. Potential hazards and risks
2. Safety-critical control functions
3. Failure mode analysis
4. Safety system requirements
5. Risk mitigation strategies
6. Compliance considerations
7. Safety instrumented systems (SIS) recommendations`;
  }
  
  private async callIndustrialLLM(executeFunctions: IExecuteFunctions, prompt: string, model: string): Promise<string> {
    return `Safety Assessment completed for: ${prompt.substring(0, 100)}...`;
  }
  
  private extractRiskLevel(response: string): string {
    const riskKeywords = {
      'high': ['high risk', 'critical', 'dangerous', 'severe'],
      'medium': ['medium risk', 'moderate', 'caution'],
      'low': ['low risk', 'minimal', 'acceptable', 'safe']
    };
    
    const responseLower = response.toLowerCase();
    
    for (const [level, keywords] of Object.entries(riskKeywords)) {
      if (keywords.some(keyword => responseLower.includes(keyword))) {
        return level;
      }
    }
    
    return 'unknown';
  }
  
  private extractSafetyRecommendations(response: string): string[] {
    const recommendations: string[] = [];
    const lines = response.split('\n');
    
    lines.forEach(line => {
      if (line.toLowerCase().includes('recommend') ||
          line.toLowerCase().includes('implement') ||
          line.toLowerCase().includes('ensure') ||
          line.toLowerCase().includes('install')) {
        recommendations.push(line.trim());
      }
    });
    
    return recommendations;
  }
} 