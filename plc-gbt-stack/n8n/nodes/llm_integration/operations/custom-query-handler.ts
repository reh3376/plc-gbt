/**
 * Custom Query Operation Handler
 * Specialized handler for custom industrial control questions
 */

import { IExecuteFunctions, INodeExecutionData } from 'n8n-workflow';
import { BaseOperationHandler } from '../../shared/utils';

export class CustomQueryHandler extends BaseOperationHandler {
  
  async execute(
    executeFunctions: IExecuteFunctions,
    items: INodeExecutionData[]
  ): Promise<INodeExecutionData[]> {
    
    await this.validateParameters(executeFunctions, ['customQuery']);
    
    return this.executeWithErrorHandling(executeFunctions, async () => {
      const customQuery = executeFunctions.getNodeParameter('customQuery', 0) as string;
      const modelSelection = executeFunctions.getNodeParameter('modelSelection', 0, 'gpt-4o-industrial') as string;
      const temperature = executeFunctions.getNodeParameter('temperature', 0, 0.7) as number;
      const maxTokens = executeFunctions.getNodeParameter('maxTokens', 0, 2000) as number;
      
      const prompt = this.buildCustomQueryPrompt(customQuery);
      const response = await this.callIndustrialLLM(executeFunctions, prompt, modelSelection, temperature, maxTokens);
      
      return {
        operation: 'custom_query',
        query: customQuery,
        response,
        responseAnalysis: this.analyzeResponse(response),
        timestamp: new Date().toISOString()
      };
    });
  }
  
  private buildCustomQueryPrompt(query: string): string {
    return `As an expert in industrial control systems and automation, please answer the following question with detailed technical insight:

Question: ${query}

Please provide:
1. A comprehensive technical answer
2. Relevant examples or applications
3. Best practices and considerations
4. Any safety or implementation warnings
5. References to relevant standards or methodologies where applicable`;
  }
  
  private async callIndustrialLLM(
    executeFunctions: IExecuteFunctions, 
    prompt: string, 
    model: string, 
    temperature: number, 
    maxTokens: number
  ): Promise<string> {
    // Implementation would call the actual LLM API with custom parameters
    return `Custom Query Response for: ${prompt.substring(0, 100)}... (Temperature: ${temperature}, MaxTokens: ${maxTokens})`;
  }
  
  private analyzeResponse(response: string): {
    responseLength: number;
    technicalDepth: string;
    keyTopics: string[];
    containsWarnings: boolean;
  } {
    const responseLength = response.length;
    
    // Analyze technical depth
    const technicalKeywords = ['control', 'system', 'parameter', 'algorithm', 'process', 'safety'];
    const technicalScore = technicalKeywords.filter(keyword => 
      response.toLowerCase().includes(keyword)
    ).length;
    
    const technicalDepth = technicalScore > 4 ? 'high' : technicalScore > 2 ? 'medium' : 'low';
    
    // Extract key topics
    const keyTopics = this.extractKeyTopics(response);
    
    // Check for warnings
    const containsWarnings = response.toLowerCase().includes('warning') ||
                            response.toLowerCase().includes('caution') ||
                            response.toLowerCase().includes('danger') ||
                            response.toLowerCase().includes('risk');
    
    return {
      responseLength,
      technicalDepth,
      keyTopics,
      containsWarnings
    };
  }
  
  private extractKeyTopics(response: string): string[] {
    const topics: string[] = [];
    const sentences = response.split('.');
    
    sentences.forEach(sentence => {
      const words = sentence.toLowerCase().split(' ');
      const industrialTerms = [
        'pid', 'control', 'process', 'system', 'automation', 'safety',
        'sensor', 'actuator', 'plc', 'scada', 'hmi', 'temperature',
        'pressure', 'flow', 'level', 'valve', 'pump', 'motor'
      ];
      
      industrialTerms.forEach(term => {
        if (words.includes(term) && !topics.includes(term)) {
          topics.push(term);
        }
      });
    });
    
    return topics.slice(0, 10); // Limit to top 10 topics
  }
} 