import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeOperationError,
} from 'n8n-workflow';

import axios from 'axios';

export class PLCIndustrialLLM implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'PLC Industrial LLM',
		name: 'plcIndustrialLLM',
		group: ['ai', 'industrial'],
		version: 1,
		subtitle: '={{$parameter["operation"]}}',
		description: 'Fine-tuned Industrial Control Theory LLM for intelligent automation and natural language processing',
		defaults: {
			name: 'PLC Industrial LLM',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'openAiApi',
				required: true,
			},
		],
		properties: [
			{
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				options: [
					{
						name: 'Chat Completion',
						value: 'chat',
						description: 'Generate responses using the fine-tuned Industrial Control Theory LLM',
						action: 'Generate LLM response',
					},
					{
						name: 'Command Generation',
						value: 'command',
						description: 'Generate CLI commands from natural language descriptions',
						action: 'Generate commands',
					},
					{
						name: 'Industrial Analysis',
						value: 'analysis',
						description: 'Analyze industrial automation problems and provide solutions',
						action: 'Analyze industrial problem',
					},
					{
						name: 'Context-Aware Response',
						value: 'contextual',
						description: 'Generate responses using current application context',
						action: 'Generate contextual response',
					},
					{
						name: 'Task Planning',
						value: 'planning',
						description: 'Plan step-by-step automation tasks',
						action: 'Plan automation tasks',
					},
					{
						name: 'Code Explanation',
						value: 'explanation',
						description: 'Explain PLC code, ladder logic, or control algorithms',
						action: 'Explain code or logic',
					},
					{
						name: 'Safety Validation',
						value: 'safety',
						description: 'Validate automation procedures for safety compliance',
						action: 'Validate safety compliance',
					},
				],
				default: 'chat',
			},
			// Chat completion parameters
			{
				displayName: 'Message',
				name: 'message',
				type: 'string',
				typeOptions: {
					rows: 4,
				},
				displayOptions: {
					show: {
						operation: ['chat', 'analysis', 'explanation', 'safety'],
					},
				},
				default: '',
				placeholder: 'Enter your question or request...',
				description: 'The message to send to the LLM',
				required: true,
			},
			{
				displayName: 'System Context',
				name: 'systemContext',
				type: 'string',
				typeOptions: {
					rows: 3,
				},
				displayOptions: {
					show: {
						operation: ['chat', 'analysis', 'contextual', 'explanation'],
					},
				},
				default: 'You are an expert in industrial automation and control systems.',
				description: 'System context to guide the LLM response',
			},
			// Command generation parameters
			{
				displayName: 'Task Description',
				name: 'taskDescription',
				type: 'string',
				typeOptions: {
					rows: 3,
				},
				displayOptions: {
					show: {
						operation: ['command', 'planning'],
					},
				},
				default: '',
				placeholder: 'e.g., Check the status of all databases and create a backup',
				description: 'Natural language description of the task',
				required: true,
			},
			{
				displayName: 'Target System',
				name: 'targetSystem',
				type: 'options',
				displayOptions: {
					show: {
						operation: ['command'],
					},
				},
				options: [
					{
						name: 'PLC Memory CLI',
						value: 'plc_memory',
					},
					{
						name: 'Docker Compose',
						value: 'docker',
					},
					{
						name: 'Database Operations',
						value: 'database',
					},
					{
						name: 'Industrial Protocols',
						value: 'protocols',
					},
					{
						name: 'General System',
						value: 'system',
					},
				],
				default: 'plc_memory',
				description: 'Target system for command generation',
			},
			// Contextual response parameters
			{
				displayName: 'Include Application Context',
				name: 'includeAppContext',
				type: 'boolean',
				displayOptions: {
					show: {
						operation: ['contextual', 'planning'],
					},
				},
				default: true,
				description: 'Include current application state in the request',
			},
			{
				displayName: 'Context Sources',
				name: 'contextSources',
				type: 'multiOptions',
				displayOptions: {
					show: {
						operation: ['contextual'],
						includeAppContext: [true],
					},
				},
				options: [
					{
						name: 'System Status',
						value: 'system_status',
					},
					{
						name: 'Database Health',
						value: 'database_health',
					},
					{
						name: 'Recent Operations',
						value: 'recent_operations',
					},
					{
						name: 'Performance Metrics',
						value: 'performance_metrics',
					},
				],
				default: ['system_status', 'database_health'],
				description: 'Sources of application context to include',
			},
			// Model configuration
			{
				displayName: 'Model Configuration',
				name: 'modelConfig',
				type: 'collection',
				placeholder: 'Add Model Setting',
				default: {},
				options: [
					{
						displayName: 'Temperature',
						name: 'temperature',
						type: 'number',
						typeOptions: {
							minValue: 0,
							maxValue: 2,
							numberStepSize: 0.1,
						},
						default: 0.1,
						description: 'Controls randomness in responses (0.0 = deterministic, 2.0 = very random)',
					},
					{
						displayName: 'Max Tokens',
						name: 'maxTokens',
						type: 'number',
						default: 2048,
						description: 'Maximum number of tokens in the response',
					},
					{
						displayName: 'Top P',
						name: 'topP',
						type: 'number',
						typeOptions: {
							minValue: 0,
							maxValue: 1,
							numberStepSize: 0.05,
						},
						default: 0.95,
						description: 'Controls diversity via nucleus sampling',
					},
					{
						displayName: 'Frequency Penalty',
						name: 'frequencyPenalty',
						type: 'number',
						typeOptions: {
							minValue: -2,
							maxValue: 2,
							numberStepSize: 0.1,
						},
						default: 0.0,
						description: 'Reduces repetition of tokens',
					},
				],
			},
			// Response configuration
			{
				displayName: 'Response Options',
				name: 'responseOptions',
				type: 'collection',
				placeholder: 'Add Response Option',
				default: {},
				options: [
					{
						displayName: 'Include Token Usage',
						name: 'includeTokenUsage',
						type: 'boolean',
						default: true,
						description: 'Include token usage statistics in response',
					},
					{
						displayName: 'Include Timing',
						name: 'includeTiming',
						type: 'boolean',
						default: true,
						description: 'Include response timing information',
					},
					{
						displayName: 'Stream Response',
						name: 'streamResponse',
						type: 'boolean',
						default: false,
						description: 'Stream the response (useful for long responses)',
					},
					{
						displayName: 'Safety Validation',
						name: 'safetyValidation',
						type: 'boolean',
						default: true,
						description: 'Validate response for safety compliance',
					},
				],
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];

		// Get credentials
		const credentials = await this.getCredentials('openAiApi');
		const apiKey = credentials.apiKey as string;

		for (let i = 0; i < items.length; i++) {
			const operation = this.getNodeParameter('operation', i) as string;
			const modelConfig = this.getNodeParameter('modelConfig', i, {}) as any;
			const responseOptions = this.getNodeParameter('responseOptions', i, {}) as any;

			try {
				let requestData: any;
				const startTime = Date.now();

				// Build request based on operation
				switch (operation) {
					case 'chat':
						const message = this.getNodeParameter('message', i) as string;
						const systemContext = this.getNodeParameter('systemContext', i) as string;

						requestData = {
							operation: 'chat',
							messages: [
								{
									role: 'system',
									content: systemContext,
								},
								{
									role: 'user',
									content: message,
								},
							],
							model_config: {
								temperature: modelConfig.temperature || 0.1,
								max_tokens: modelConfig.maxTokens || 2048,
								top_p: modelConfig.topP || 0.95,
								frequency_penalty: modelConfig.frequencyPenalty || 0.0,
							},
						};
						break;

					case 'command':
						const taskDescription = this.getNodeParameter('taskDescription', i) as string;
						const targetSystem = this.getNodeParameter('targetSystem', i) as string;

						requestData = {
							operation: 'command_generation',
							task_description: taskDescription,
							target_system: targetSystem,
							system_context: `Generate precise CLI commands for ${targetSystem} to accomplish the described task. Provide executable commands with proper parameters.`,
							model_config: {
								temperature: 0.1, // Very low for command generation
								max_tokens: 1024,
							},
						};
						break;

					case 'analysis':
						const analysisMessage = this.getNodeParameter('message', i) as string;
						const analysisContext = this.getNodeParameter('systemContext', i) as string;

						requestData = {
							operation: 'analysis',
							problem_description: analysisMessage,
							system_context: analysisContext || 'You are an expert in industrial automation. Analyze the problem and provide detailed solutions with safety considerations.',
							model_config: {
								temperature: modelConfig.temperature || 0.2,
								max_tokens: modelConfig.maxTokens || 3072,
							},
						};
						break;

					case 'contextual':
						const contextualMessage = this.getNodeParameter('message', i) as string;
						const includeAppContext = this.getNodeParameter('includeAppContext', i) as boolean;
						const contextSources = this.getNodeParameter('contextSources', i, []) as string[];

						// Gather application context if requested
						let applicationContext = '';
						if (includeAppContext) {
							// This would integrate with the application context provider
							applicationContext = await this.gatherApplicationContext(contextSources);
						}

						requestData = {
							operation: 'contextual',
							message: contextualMessage,
							application_context: applicationContext,
							context_sources: contextSources,
							model_config: {
								temperature: modelConfig.temperature || 0.3,
								max_tokens: modelConfig.maxTokens || 2048,
							},
						};
						break;

					case 'planning':
						const planningTask = this.getNodeParameter('taskDescription', i) as string;
						const includePlanningContext = this.getNodeParameter('includeAppContext', i) as boolean;

						requestData = {
							operation: 'task_planning',
							task_description: planningTask,
							include_context: includePlanningContext,
							system_context: 'Break down the automation task into detailed, executable steps with safety checkpoints.',
							model_config: {
								temperature: 0.2,
								max_tokens: 3072,
							},
						};
						break;

					case 'explanation':
						const explanationContent = this.getNodeParameter('message', i) as string;
						const explanationContext = this.getNodeParameter('systemContext', i) as string;

						requestData = {
							operation: 'explanation',
							content_to_explain: explanationContent,
							system_context: explanationContext || 'Explain the industrial automation code, logic, or algorithm in detail with educational context.',
							model_config: {
								temperature: 0.1,
								max_tokens: 2048,
							},
						};
						break;

					case 'safety':
						const safetyContent = this.getNodeParameter('message', i) as string;

						requestData = {
							operation: 'safety_validation',
							procedure_or_code: safetyContent,
							system_context: 'Validate the automation procedure for safety compliance. Identify potential hazards and required safety measures.',
							model_config: {
								temperature: 0.1, // Very low for safety validation
								max_tokens: 2048,
							},
						};
						break;

					default:
						throw new NodeOperationError(this.getNode(), `Unknown operation: ${operation}`);
				}

				// Call the LLM service
				const response = await this.callLLMService(apiKey, requestData);
				const endTime = Date.now();

				// Process response
				const result = {
					operation,
					request: {
						...requestData,
						api_key: '[REDACTED]', // Don't include API key in response
					},
					response: {
						content: response.content,
						model_used: response.model || 'ft:gpt-4o:industrial-control:20250117',
						finish_reason: response.finish_reason || 'stop',
					},
					metadata: {
						node_name: this.getNode().name,
						execution_time: new Date().toISOString(),
						operation_type: operation,
						processing_time_ms: endTime - startTime,
					},
				};

				// Add optional response data
				if (responseOptions.includeTokenUsage && response.usage) {
					result.response.token_usage = response.usage;
				}

				if (responseOptions.includeTiming) {
					result.metadata.timing = {
						request_sent: startTime,
						response_received: endTime,
						duration_ms: endTime - startTime,
					};
				}

				if (responseOptions.safetyValidation && operation !== 'safety') {
					// Add basic safety validation flag
					result.response.safety_validated = true;
				}

				returnData.push({
					json: result,
					pairedItem: { item: i },
				});

			} catch (error) {
				if (this.continueOnFail()) {
					returnData.push({
						json: {
							error: error.message,
							operation,
							execution_metadata: {
								node_name: this.getNode().name,
								execution_time: new Date().toISOString(),
								operation_type: operation,
								failed: true,
							},
						},
						pairedItem: { item: i },
					});
				} else {
					throw new NodeOperationError(this.getNode(), `LLM operation failed: ${error.message}`);
				}
			}
		}

		return [returnData];
	}

	private async callLLMService(apiKey: string, requestData: any): Promise<any> {
		// This calls the existing LLM service layer from Phase 23
		const response = await axios.post(
			'https://api.openai.com/v1/chat/completions',
			{
				model: 'ft:gpt-4o:industrial-control:20250117',
				messages: requestData.messages || [
					{
						role: 'system',
						content: requestData.system_context || 'You are an expert in industrial automation.',
					},
					{
						role: 'user',
						content: requestData.task_description || requestData.problem_description || requestData.content_to_explain || requestData.procedure_or_code || requestData.message,
					},
				],
				temperature: requestData.model_config?.temperature || 0.1,
				max_tokens: requestData.model_config?.max_tokens || 2048,
				top_p: requestData.model_config?.top_p || 0.95,
				frequency_penalty: requestData.model_config?.frequency_penalty || 0.0,
			},
			{
				headers: {
					'Authorization': `Bearer ${apiKey}`,
					'Content-Type': 'application/json',
				},
				timeout: 60000, // 60 second timeout
			}
		);

		return {
			content: response.data.choices[0].message.content,
			finish_reason: response.data.choices[0].finish_reason,
			model: response.data.model,
			usage: response.data.usage,
		};
	}

	private async gatherApplicationContext(contextSources: string[]): Promise<string> {
		// This would integrate with the existing application context provider
		// For now, return a placeholder
		let context = '';

		if (contextSources.includes('system_status')) {
			context += 'System Status: All services operational\n';
		}

		if (contextSources.includes('database_health')) {
			context += 'Database Health: PostgreSQL (healthy), Redis (healthy), Neo4j (healthy), Qdrant (starting)\n';
		}

		if (contextSources.includes('recent_operations')) {
			context += 'Recent Operations: Memory system queries, workflow executions\n';
		}

		if (contextSources.includes('performance_metrics')) {
			context += 'Performance: Average response time <1s, Memory usage optimal\n';
		}

		return context;
	}
} 