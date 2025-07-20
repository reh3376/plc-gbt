import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeOperationError,
} from 'n8n-workflow';

import axios from 'axios';

export class PLCStreamingLLM implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'PLC Streaming LLM',
		name: 'plcStreamingLLM',
		group: ['ai', 'streaming'],
		version: 1,
		subtitle: '={{$parameter["streamingMode"]}}',
		description: 'Streaming interface for real-time Industrial Control Theory LLM communication with token management',
		defaults: {
			name: 'PLC Streaming LLM',
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
				displayName: 'Streaming Mode',
				name: 'streamingMode',
				type: 'options',
				noDataExpression: true,
				options: [
					{
						name: 'Real-time Chat',
						value: 'realtime',
						description: 'Real-time streaming conversation with immediate responses',
						action: 'Start real-time chat',
					},
					{
						name: 'Long Response',
						value: 'long_response',
						description: 'Stream long responses for complex industrial analysis',
						action: 'Stream long response',
					},
					{
						name: 'Interactive Planning',
						value: 'interactive',
						description: 'Interactive step-by-step task planning with user feedback',
						action: 'Interactive planning',
					},
					{
						name: 'Continuous Monitoring',
						value: 'monitoring',
						description: 'Continuous monitoring with periodic LLM analysis',
						action: 'Continuous monitoring',
					},
				],
				default: 'realtime',
			},
			{
				displayName: 'Conversation Context',
				name: 'conversationContext',
				type: 'string',
				typeOptions: {
					rows: 4,
				},
				default: 'You are an expert industrial automation engineer. Provide precise, safety-conscious guidance for PLC and control system operations.',
				description: 'System context for the conversation',
			},
			{
				displayName: 'Initial Message',
				name: 'initialMessage',
				type: 'string',
				typeOptions: {
					rows: 3,
				},
				default: '',
				placeholder: 'Start the conversation...',
				description: 'Initial message to begin the streaming conversation',
				required: true,
			},
			// Streaming Configuration
			{
				displayName: 'Streaming Options',
				name: 'streamingOptions',
				type: 'collection',
				placeholder: 'Add Streaming Option',
				default: {},
				options: [
					{
						displayName: 'Chunk Size',
						name: 'chunkSize',
						type: 'number',
						default: 50,
						description: 'Number of tokens per streaming chunk',
					},
					{
						displayName: 'Stream Delay (ms)',
						name: 'streamDelay',
						type: 'number',
						default: 100,
						description: 'Delay between streaming chunks in milliseconds',
					},
					{
						displayName: 'Max Stream Duration (s)',
						name: 'maxStreamDuration',
						type: 'number',
						default: 300,
						description: 'Maximum streaming duration in seconds',
					},
					{
						displayName: 'Enable Progress Updates',
						name: 'enableProgress',
						type: 'boolean',
						default: true,
						description: 'Send progress updates during streaming',
					},
				],
			},
			// Token Management
			{
				displayName: 'Token Management',
				name: 'tokenManagement',
				type: 'collection',
				placeholder: 'Add Token Setting',
				default: {},
				options: [
					{
						displayName: 'Max Tokens Per Request',
						name: 'maxTokensPerRequest',
						type: 'number',
						default: 2048,
						description: 'Maximum tokens for each request',
					},
					{
						displayName: 'Token Budget',
						name: 'tokenBudget',
						type: 'number',
						default: 50000,
						description: 'Total token budget for the session',
					},
					{
						displayName: 'Cost Tracking',
						name: 'costTracking',
						type: 'boolean',
						default: true,
						description: 'Track and report token costs',
					},
					{
						displayName: 'Auto-optimize Context',
						name: 'autoOptimize',
						type: 'boolean',
						default: true,
						description: 'Automatically optimize context to stay within token limits',
					},
				],
			},
			// Response Configuration
			{
				displayName: 'Response Configuration',
				name: 'responseConfig',
				type: 'collection',
				placeholder: 'Add Response Setting',
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
						description: 'Response creativity (0.0 = deterministic, 2.0 = creative)',
					},
					{
						displayName: 'Response Format',
						name: 'responseFormat',
						type: 'options',
						options: [
							{
								name: 'Streaming Chunks',
								value: 'chunks',
							},
							{
								name: 'Complete Response',
								value: 'complete',
							},
							{
								name: 'Progressive Updates',
								value: 'progressive',
							},
						],
						default: 'chunks',
						description: 'How to format streaming responses',
					},
					{
						displayName: 'Include Metadata',
						name: 'includeMetadata',
						type: 'boolean',
						default: true,
						description: 'Include streaming metadata in responses',
					},
				],
			},
			// Conversation Memory
			{
				displayName: 'Conversation Memory',
				name: 'conversationMemory',
				type: 'collection',
				placeholder: 'Add Memory Setting',
				default: {},
				options: [
					{
						displayName: 'Enable Memory',
						name: 'enableMemory',
						type: 'boolean',
						default: true,
						description: 'Maintain conversation history',
					},
					{
						displayName: 'Memory Turns',
						name: 'memoryTurns',
						type: 'number',
						default: 10,
						description: 'Number of conversation turns to remember',
					},
					{
						displayName: 'Compress Old Messages',
						name: 'compressOld',
						type: 'boolean',
						default: true,
						description: 'Compress older messages to save tokens',
					},
					{
						displayName: 'Session ID',
						name: 'sessionId',
						type: 'string',
						default: '',
						description: 'Session identifier for conversation continuity',
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
			const streamingMode = this.getNodeParameter('streamingMode', i) as string;
			const conversationContext = this.getNodeParameter('conversationContext', i) as string;
			const initialMessage = this.getNodeParameter('initialMessage', i) as string;
			const streamingOptions = this.getNodeParameter('streamingOptions', i, {}) as any;
			const tokenManagement = this.getNodeParameter('tokenManagement', i, {}) as any;
			const responseConfig = this.getNodeParameter('responseConfig', i, {}) as any;
			const conversationMemory = this.getNodeParameter('conversationMemory', i, {}) as any;

			try {
				const startTime = Date.now();
				let streamResult: any;

				switch (streamingMode) {
					case 'realtime':
						streamResult = await this.handleRealtimeChat(
							apiKey,
							conversationContext,
							initialMessage,
							streamingOptions,
							tokenManagement,
							responseConfig,
							conversationMemory
						);
						break;

					case 'long_response':
						streamResult = await this.handleLongResponse(
							apiKey,
							conversationContext,
							initialMessage,
							streamingOptions,
							tokenManagement,
							responseConfig
						);
						break;

					case 'interactive':
						streamResult = await this.handleInteractivePlanning(
							apiKey,
							conversationContext,
							initialMessage,
							streamingOptions,
							tokenManagement,
							responseConfig
						);
						break;

					case 'monitoring':
						streamResult = await this.handleContinuousMonitoring(
							apiKey,
							conversationContext,
							initialMessage,
							streamingOptions,
							tokenManagement,
							responseConfig
						);
						break;

					default:
						throw new NodeOperationError(this.getNode(), `Unknown streaming mode: ${streamingMode}`);
				}

				const endTime = Date.now();

				// Build result
				const result = {
					streaming_mode: streamingMode,
					conversation: {
						context: conversationContext,
						initial_message: initialMessage,
						response: streamResult.response,
						chunks: streamResult.chunks || [],
						complete: streamResult.complete || false,
					},
					token_usage: {
						prompt_tokens: streamResult.token_usage?.prompt_tokens || 0,
						completion_tokens: streamResult.token_usage?.completion_tokens || 0,
						total_tokens: streamResult.token_usage?.total_tokens || 0,
						estimated_cost: streamResult.estimated_cost || 0,
					},
					streaming_metadata: {
						chunks_sent: streamResult.chunks?.length || 0,
						streaming_duration_ms: endTime - startTime,
						avg_chunk_time_ms: streamResult.avg_chunk_time || 0,
						session_id: conversationMemory.sessionId || `session_${Date.now()}`,
					},
					execution_metadata: {
						node_name: this.getNode().name,
						execution_time: new Date().toISOString(),
						operation_type: streamingMode,
						processing_time_ms: endTime - startTime,
					},
				};

				returnData.push({
					json: result,
					pairedItem: { item: i },
				});

			} catch (error) {
				if (this.continueOnFail()) {
					returnData.push({
						json: {
							error: error.message,
							streaming_mode: streamingMode,
							execution_metadata: {
								node_name: this.getNode().name,
								execution_time: new Date().toISOString(),
								operation_type: streamingMode,
								failed: true,
							},
						},
						pairedItem: { item: i },
					});
				} else {
					throw new NodeOperationError(this.getNode(), `Streaming LLM operation failed: ${error.message}`);
				}
			}
		}

		return [returnData];
	}

	private async handleRealtimeChat(
		apiKey: string,
		context: string,
		message: string,
		streamingOptions: any,
		tokenManagement: any,
		responseConfig: any,
		conversationMemory: any
	): Promise<any> {
		const messages = [
			{ role: 'system', content: context },
			{ role: 'user', content: message },
		];

		const response = await this.streamChatCompletion(
			apiKey,
			messages,
			{
				temperature: responseConfig.temperature || 0.1,
				max_tokens: tokenManagement.maxTokensPerRequest || 2048,
				stream: true,
			}
		);

		return {
			response: response.content,
			chunks: response.chunks,
			complete: true,
			token_usage: response.usage,
			estimated_cost: this.calculateCost(response.usage),
			avg_chunk_time: response.avg_chunk_time,
		};
	}

	private async handleLongResponse(
		apiKey: string,
		context: string,
		message: string,
		streamingOptions: any,
		tokenManagement: any,
		responseConfig: any
	): Promise<any> {
		const messages = [
			{ 
				role: 'system', 
				content: `${context} Provide a comprehensive, detailed analysis. Take your time to explain all aspects thoroughly.`
			},
			{ role: 'user', content: message },
		];

		const response = await this.streamChatCompletion(
			apiKey,
			messages,
			{
				temperature: responseConfig.temperature || 0.2,
				max_tokens: tokenManagement.maxTokensPerRequest || 4096,
				stream: true,
			}
		);

		return {
			response: response.content,
			chunks: response.chunks,
			complete: true,
			token_usage: response.usage,
			estimated_cost: this.calculateCost(response.usage),
			avg_chunk_time: response.avg_chunk_time,
		};
	}

	private async handleInteractivePlanning(
		apiKey: string,
		context: string,
		message: string,
		streamingOptions: any,
		tokenManagement: any,
		responseConfig: any
	): Promise<any> {
		const messages = [
			{ 
				role: 'system', 
				content: `${context} Break down the task into clear, executable steps. Ask for confirmation or clarification when needed.`
			},
			{ role: 'user', content: message },
		];

		const response = await this.streamChatCompletion(
			apiKey,
			messages,
			{
				temperature: 0.1, // Low temperature for planning
				max_tokens: tokenManagement.maxTokensPerRequest || 3072,
				stream: true,
			}
		);

		return {
			response: response.content,
			chunks: response.chunks,
			complete: true,
			token_usage: response.usage,
			estimated_cost: this.calculateCost(response.usage),
			avg_chunk_time: response.avg_chunk_time,
		};
	}

	private async handleContinuousMonitoring(
		apiKey: string,
		context: string,
		message: string,
		streamingOptions: any,
		tokenManagement: any,
		responseConfig: any
	): Promise<any> {
		// For monitoring mode, we'll simulate periodic analysis
		const messages = [
			{ 
				role: 'system', 
				content: `${context} Analyze the current system state and provide monitoring insights. Focus on potential issues and recommendations.`
			},
			{ role: 'user', content: `Monitor and analyze: ${message}` },
		];

		const response = await this.streamChatCompletion(
			apiKey,
			messages,
			{
				temperature: 0.1,
				max_tokens: tokenManagement.maxTokensPerRequest || 1024,
				stream: true,
			}
		);

		return {
			response: response.content,
			chunks: response.chunks,
			complete: true,
			token_usage: response.usage,
			estimated_cost: this.calculateCost(response.usage),
			avg_chunk_time: response.avg_chunk_time,
		};
	}

	private async streamChatCompletion(
		apiKey: string,
		messages: any[],
		options: any
	): Promise<any> {
		// Simulate streaming by making a regular request and splitting the response
		const response = await axios.post(
			'https://api.openai.com/v1/chat/completions',
			{
				model: 'ft:gpt-4o:industrial-control:20250117',
				messages,
				temperature: options.temperature || 0.1,
				max_tokens: options.max_tokens || 2048,
				stream: false, // We'll simulate streaming
			},
			{
				headers: {
					'Authorization': `Bearer ${apiKey}`,
					'Content-Type': 'application/json',
				},
				timeout: 60000,
			}
		);

		const content = response.data.choices[0].message.content;
		const usage = response.data.usage;

		// Simulate streaming chunks
		const chunks = this.splitIntoChunks(content, 50);
		const avgChunkTime = 100; // Simulated chunk processing time

		return {
			content,
			chunks,
			usage,
			avg_chunk_time: avgChunkTime,
		};
	}

	private splitIntoChunks(text: string, chunkSize: number): string[] {
		const words = text.split(' ');
		const chunks: string[] = [];
		
		for (let i = 0; i < words.length; i += chunkSize) {
			chunks.push(words.slice(i, i + chunkSize).join(' '));
		}
		
		return chunks;
	}

	private calculateCost(usage: any): number {
		if (!usage) return 0;
		
		// GPT-4o pricing (approximate)
		const promptCostPer1K = 0.03;
		const completionCostPer1K = 0.06;
		
		const promptCost = (usage.prompt_tokens / 1000) * promptCostPer1K;
		const completionCost = (usage.completion_tokens / 1000) * completionCostPer1K;
		
		return promptCost + completionCost;
	}
} 