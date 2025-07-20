import {
	IWebhookFunctions,
	IWebhookResponseData,
	INodeType,
	INodeTypeDescription,
	INodeExecutionData,
	NodeOperationError,
} from 'n8n-workflow';

import { Request, Response } from 'express';

export class PLCMemoryWebhook implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'PLC Memory Webhook',
		name: 'plcMemoryWebhook',
		group: ['webhook', 'industrial'],
		version: 1,
		description: 'Webhook interface for PLC Memory system integration with real-time data processing',
		defaults: {
			name: 'PLC Memory Webhook',
		},
		inputs: [],
		outputs: ['main'],
		webhooks: [
			{
				name: 'default',
				httpMethod: 'POST',
				responseMode: 'onReceived',
				path: 'plc-memory',
			},
		],
		properties: [
			{
				displayName: 'Authentication',
				name: 'authentication',
				type: 'options',
				options: [
					{
						name: 'None',
						value: 'none',
					},
					{
						name: 'Header Auth',
						value: 'headerAuth',
					},
					{
						name: 'Query Auth',
						value: 'queryAuth',
					},
				],
				default: 'none',
				description: 'Authentication method for webhook',
			},
			{
				displayName: 'Auth Header Name',
				name: 'authHeaderName',
				type: 'string',
				displayOptions: {
					show: {
						authentication: ['headerAuth'],
					},
				},
				default: 'X-PLC-Auth',
				description: 'Name of the authentication header',
			},
			{
				displayName: 'Auth Header Value',
				name: 'authHeaderValue',
				type: 'string',
				typeOptions: {
					password: true,
				},
				displayOptions: {
					show: {
						authentication: ['headerAuth'],
					},
				},
				default: '',
				description: 'Expected value of the authentication header',
			},
			{
				displayName: 'Auth Query Parameter',
				name: 'authQueryParameter',
				type: 'string',
				displayOptions: {
					show: {
						authentication: ['queryAuth'],
					},
				},
				default: 'token',
				description: 'Name of the authentication query parameter',
			},
			{
				displayName: 'Auth Query Value',
				name: 'authQueryValue',
				type: 'string',
				typeOptions: {
					password: true,
				},
				displayOptions: {
					show: {
						authentication: ['queryAuth'],
					},
				},
				default: '',
				description: 'Expected value of the authentication query parameter',
			},
			{
				displayName: 'Response Format',
				name: 'responseFormat',
				type: 'options',
				options: [
					{
						name: 'JSON',
						value: 'json',
					},
					{
						name: 'Text',
						value: 'text',
					},
				],
				default: 'json',
				description: 'Format for webhook response',
			},
			{
				displayName: 'Enable CORS',
				name: 'enableCors',
				type: 'boolean',
				default: true,
				description: 'Enable Cross-Origin Resource Sharing',
			},
		],
	};

	async webhook(this: IWebhookFunctions): Promise<IWebhookResponseData> {
		const req = this.getRequestObject() as Request;
		const res = this.getResponseObject() as Response;
		const authentication = this.getNodeParameter('authentication') as string;
		const responseFormat = this.getNodeParameter('responseFormat') as string;
		const enableCors = this.getNodeParameter('enableCors') as boolean;

		// Set CORS headers if enabled
		if (enableCors) {
			res.header('Access-Control-Allow-Origin', '*');
			res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
			res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-PLC-Auth');
		}

		// Handle OPTIONS request for CORS
		if (req.method === 'OPTIONS') {
			return {
				workflowData: [[]],
			};
		}

		// Authentication check
		try {
			if (authentication === 'headerAuth') {
				const authHeaderName = this.getNodeParameter('authHeaderName') as string;
				const authHeaderValue = this.getNodeParameter('authHeaderValue') as string;
				const providedValue = req.headers[authHeaderName.toLowerCase()];

				if (!providedValue || providedValue !== authHeaderValue) {
					res.status(401).json({ error: 'Authentication failed', code: 'AUTH_HEADER_INVALID' });
					return {
						workflowData: [[]],
					};
				}
			} else if (authentication === 'queryAuth') {
				const authQueryParameter = this.getNodeParameter('authQueryParameter') as string;
				const authQueryValue = this.getNodeParameter('authQueryValue') as string;
				const providedValue = req.query[authQueryParameter];

				if (!providedValue || providedValue !== authQueryValue) {
					res.status(401).json({ error: 'Authentication failed', code: 'AUTH_QUERY_INVALID' });
					return {
						workflowData: [[]],
					};
				}
			}

			// Parse request body
			const body = req.body || {};
			const operation = body.operation || 'status';
			const parameters = body.parameters || {};

			// Validate required operation
			const validOperations = ['status', 'query', 'ingest', 'health', 'backup', 'optimize', 'clean', 'version'];
			if (!validOperations.includes(operation)) {
				res.status(400).json({
					error: 'Invalid operation',
					code: 'INVALID_OPERATION',
					validOperations,
				});
				return {
					workflowData: [[]],
				};
			}

			// Process the webhook request
			const webhookData: INodeExecutionData = {
				json: {
					// Request metadata
					webhook_info: {
						method: req.method,
						url: req.url,
						headers: req.headers,
						timestamp: new Date().toISOString(),
						source_ip: req.ip || req.connection.remoteAddress,
					},
					// PLC Memory operation
					plc_memory_request: {
						operation,
						parameters,
						requested_format: parameters.format || 'json',
					},
					// Processing instructions for next node
					processing_instructions: {
						execute_operation: true,
						validate_parameters: true,
						track_performance: true,
					},
				},
			};

			// Prepare response based on format
			if (responseFormat === 'json') {
				const response = {
					status: 'received',
					operation,
					parameters,
					timestamp: new Date().toISOString(),
					webhook_id: this.getWebhookId(),
					message: `PLC Memory ${operation} operation queued for processing`,
				};

				res.status(200).json(response);
			} else {
				res.status(200).send(`PLC Memory ${operation} operation received and queued`);
			}

			return {
				workflowData: [[webhookData]],
			};

		} catch (error) {
			const errorResponse = {
				error: 'Webhook processing failed',
				code: 'WEBHOOK_ERROR',
				details: error.message,
				timestamp: new Date().toISOString(),
			};

			if (responseFormat === 'json') {
				res.status(500).json(errorResponse);
			} else {
				res.status(500).send(`Error: ${error.message}`);
			}

			return {
				workflowData: [[]],
			};
		}
	}
} 