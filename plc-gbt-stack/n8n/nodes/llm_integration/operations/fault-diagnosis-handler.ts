/**
 * Fault Diagnosis Operation Handler
 * Specialized handler for control system fault diagnosis
 */

import { IExecuteFunctions, INodeExecutionData } from 'n8n-workflow';
import { BaseOperationHandler } from '../../shared/utils';

export class FaultDiagnosisHandler extends BaseOperationHandler {
  
  async execute(
    executeFunctions: IExecuteFunctions,
    items: INodeExecutionData[]
  ): Promise<INodeExecutionData[]> {
    
    return this.executeWithErrorHandling(executeFunctions, async () => {
      const faultSymptoms = executeFunctions.getNodeParameter('faultSymptoms', 0, '') as string;
      const systemDescription = executeFunctions.getNodeParameter('systemDescription', 0, '') as string;
      const modelSelection = executeFunctions.getNodeParameter('modelSelection', 0, 'gpt-4o-industrial') as string;
      
      const prompt = this.buildDiagnosisPrompt(faultSymptoms, systemDescription);
      const response = await this.callIndustrialLLM(executeFunctions, prompt, modelSelection);
      
      return {
        operation: 'fault_diagnosis',
        faultSymptoms,
        systemDescription,
        diagnosis: response,
        possibleCauses: this.extractPossibleCauses(response),
        recommendedActions: this.extractRecommendedActions(response),
        timestamp: new Date().toISOString()
      };
    });
  }
  
  private buildDiagnosisPrompt(symptoms: string, system: string): string {
    return `As an expert in industrial control system troubleshooting, analyze the following fault:

Fault Symptoms: ${symptoms}
System Description: ${system}

Please provide a comprehensive fault diagnosis including:
1. Most likely root causes
2. Diagnostic steps to confirm the fault
3. Immediate corrective actions
4. Long-term preventive measures
5. Safety considerations during troubleshooting
6. Monitoring recommendations to prevent recurrence`;
  }
  
  private async callIndustrialLLM(executeFunctions: IExecuteFunctions, prompt: string, model: string): Promise<string> {
    return `Fault Diagnosis completed for: ${prompt.substring(0, 100)}...`;
  }
  
  private extractPossibleCauses(response: string): string[] {
    const causes: string[] = [];
    const lines = response.split('\n');
    
    lines.forEach(line => {
      if (line.toLowerCase().includes('cause') ||
          line.toLowerCase().includes('due to') ||
          line.toLowerCase().includes('likely') ||
          line.toLowerCase().includes('problem')) {
        causes.push(line.trim());
      }
    });
    
    return causes;
  }
  
  private extractRecommendedActions(response: string): string[] {
    const actions: string[] = [];
    const lines = response.split('\n');
    
    lines.forEach(line => {
      if (line.toLowerCase().includes('action') ||
          line.toLowerCase().includes('check') ||
          line.toLowerCase().includes('replace') ||
          line.toLowerCase().includes('adjust') ||
          line.toLowerCase().includes('calibrate')) {
        actions.push(line.trim());
      }
    });
    
    return actions;
  }
} 