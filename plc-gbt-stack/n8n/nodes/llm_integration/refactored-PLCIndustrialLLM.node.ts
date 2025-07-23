/**
 * Refactored PLC Industrial LLM Node for N8N Workflow Automation
 * Phase 26.3: PLC Memory Stack Integration - LLM Integration
 * 
 * Simplified node using modular components.
 * Reduced from 638 lines to ~80 lines (87% reduction).
 */

import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
} from 'n8n-workflow';

import { LLMProperties } from './properties/llm-properties';
import { LLMOperations } from '../shared/types';
import { NodeErrorHandler } from '../shared/utils';
import {
    ControlAnalysisHandler,
    PidTuningHandler,
    SafetyAssessmentHandler,
    ProcessOptimizationHandler,
    FaultDiagnosisHandler,
    CustomQueryHandler
} from './operations';

export class PLCIndustrialLLM implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'PLC Industrial LLM',
        name: 'plcIndustrialLLM',
        group: ['transform'],
        version: 1,
        description: 'Interact with fine-tuned Industrial Control Theory LLM for specialized automation tasks',
        defaults: {
            name: 'PLC Industrial LLM',
            color: '#FF9500',
        },
        inputs: ['main'],
        outputs: ['main'],
        credentials: [
            {
                name: 'openAIApi',
                required: true,
            }
        ],
        properties: LLMProperties.getAllProperties()
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const operation = this.getNodeParameter('operation', 0) as LLMOperations;
        
        try {
            const handler = this.getOperationHandler(operation);
            const result = await handler.execute(this, items);
            return [result];
            
        } catch (error) {
            throw NodeErrorHandler.handleOperationError(this, operation, error as Error);
        }
    }
    
    private getOperationHandler(operation: LLMOperations) {
        switch (operation) {
            case LLMOperations.CONTROL_ANALYSIS:
                return new ControlAnalysisHandler();
            case LLMOperations.PID_TUNING:
                return new PidTuningHandler();
            case LLMOperations.SAFETY_ASSESSMENT:
                return new SafetyAssessmentHandler();
            case LLMOperations.PROCESS_OPTIMIZATION:
                return new ProcessOptimizationHandler();
            case LLMOperations.FAULT_DIAGNOSIS:
                return new FaultDiagnosisHandler();
            case LLMOperations.CUSTOM_QUERY:
                return new CustomQueryHandler();
            default:
                throw NodeErrorHandler.createOperationError(
                    this,
                    `Unknown operation: ${operation}`
                );
        }
    }
} 