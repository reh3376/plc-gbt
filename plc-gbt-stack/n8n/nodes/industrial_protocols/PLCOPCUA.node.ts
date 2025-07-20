import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeOperationError,
} from 'n8n-workflow';

import { OPCUAClient, MessageSecurityMode, SecurityPolicy, AttributeIds, ClientSubscription, ClientMonitoredItem } from 'node-opcua';

export class PLCOPCUA implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'PLC OPC-UA',
		name: 'plcOpcua',
		group: ['industrial', 'communication'],
		version: 1,
		subtitle: '={{$parameter["operation"]}}',
		description: 'OPC Unified Architecture client for industrial automation communication',
		defaults: {
			name: 'PLC OPC-UA',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'opcuaCredentials',
				required: false,
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
						name: 'Read Variables',
						value: 'read',
						description: 'Read values from OPC-UA server variables',
						action: 'Read OPC-UA variables',
					},
					{
						name: 'Write Variables',
						value: 'write',
						description: 'Write values to OPC-UA server variables',
						action: 'Write OPC-UA variables',
					},
					{
						name: 'Browse Server',
						value: 'browse',
						description: 'Browse OPC-UA server namespace and discover nodes',
						action: 'Browse OPC-UA server',
					},
					{
						name: 'Subscribe to Changes',
						value: 'subscribe',
						description: 'Subscribe to variable changes and receive notifications',
						action: 'Subscribe to OPC-UA changes',
					},
					{
						name: 'Call Methods',
						value: 'method',
						description: 'Call methods on OPC-UA server objects',
						action: 'Call OPC-UA methods',
					},
					{
						name: 'Server Discovery',
						value: 'discovery',
						description: 'Discover available OPC-UA servers on network',
						action: 'Discover OPC-UA servers',
					},
				],
				default: 'read',
			},
			// Connection settings
			{
				displayName: 'Server Endpoint',
				name: 'serverEndpoint',
				type: 'string',
				default: 'opc.tcp://localhost:4840',
				placeholder: 'opc.tcp://your-server:4840',
				description: 'OPC-UA server endpoint URL',
				required: true,
			},
			{
				displayName: 'Connection Settings',
				name: 'connectionSettings',
				type: 'collection',
				placeholder: 'Add Connection Setting',
				default: {},
				options: [
					{
						displayName: 'Connection Timeout (ms)',
						name: 'connectionTimeout',
						type: 'number',
						default: 10000,
						description: 'Connection timeout in milliseconds',
					},
					{
						displayName: 'Session Timeout (ms)',
						name: 'sessionTimeout',
						type: 'number',
						default: 60000,
						description: 'Session timeout in milliseconds',
					},
					{
						displayName: 'Keep Alive Interval (ms)',
						name: 'keepAliveInterval',
						type: 'number',
						default: 5000,
						description: 'Keep alive interval in milliseconds',
					},
					{
						displayName: 'Max Reconnect Attempts',
						name: 'maxReconnectAttempts',
						type: 'number',
						default: 5,
						description: 'Maximum number of reconnection attempts',
					},
				],
			},
			// Security settings
			{
				displayName: 'Security Settings',
				name: 'securitySettings',
				type: 'collection',
				placeholder: 'Add Security Setting',
				default: {},
				options: [
					{
						displayName: 'Security Mode',
						name: 'securityMode',
						type: 'options',
						options: [
							{
								name: 'None',
								value: 'None',
							},
							{
								name: 'Sign',
								value: 'Sign',
							},
							{
								name: 'Sign & Encrypt',
								value: 'SignAndEncrypt',
							},
						],
						default: 'None',
						description: 'Message security mode',
					},
					{
						displayName: 'Security Policy',
						name: 'securityPolicy',
						type: 'options',
						options: [
							{
								name: 'None',
								value: 'None',
							},
							{
								name: 'Basic128Rsa15',
								value: 'Basic128Rsa15',
							},
							{
								name: 'Basic256',
								value: 'Basic256',
							},
							{
								name: 'Basic256Sha256',
								value: 'Basic256Sha256',
							},
						],
						default: 'None',
						description: 'Security policy to use',
					},
					{
						displayName: 'Certificate File Path',
						name: 'certificatePath',
						type: 'string',
						default: '',
						description: 'Path to client certificate file',
					},
					{
						displayName: 'Private Key File Path',
						name: 'privateKeyPath',
						type: 'string',
						default: '',
						description: 'Path to private key file',
					},
				],
			},
			// Read operation parameters
			{
				displayName: 'Node IDs to Read',
				name: 'nodeIdsToRead',
				type: 'fixedCollection',
				displayOptions: {
					show: {
						operation: ['read'],
					},
				},
				default: {},
				typeOptions: {
					multipleValues: true,
				},
				options: [
					{
						name: 'nodeId',
						displayName: 'Node ID',
						values: [
							{
								displayName: 'Node ID',
								name: 'nodeId',
								type: 'string',
								default: '',
								placeholder: 'ns=2;s=Temperature',
								description: 'OPC-UA Node ID to read',
								required: true,
							},
							{
								displayName: 'Alias',
								name: 'alias',
								type: 'string',
								default: '',
								placeholder: 'temperature_sensor',
								description: 'Alias name for the result',
							},
							{
								displayName: 'Data Type',
								name: 'dataType',
								type: 'options',
								options: [
									{ name: 'Auto-detect', value: 'auto' },
									{ name: 'Boolean', value: 'boolean' },
									{ name: 'Number', value: 'number' },
									{ name: 'String', value: 'string' },
									{ name: 'DateTime', value: 'datetime' },
								],
								default: 'auto',
								description: 'Expected data type',
							},
						],
					},
				],
			},
			// Write operation parameters
			{
				displayName: 'Node IDs to Write',
				name: 'nodeIdsToWrite',
				type: 'fixedCollection',
				displayOptions: {
					show: {
						operation: ['write'],
					},
				},
				default: {},
				typeOptions: {
					multipleValues: true,
				},
				options: [
					{
						name: 'nodeId',
						displayName: 'Node ID',
						values: [
							{
								displayName: 'Node ID',
								name: 'nodeId',
								type: 'string',
								default: '',
								placeholder: 'ns=2;s=Setpoint',
								description: 'OPC-UA Node ID to write',
								required: true,
							},
							{
								displayName: 'Value',
								name: 'value',
								type: 'string',
								default: '',
								description: 'Value to write (will be converted to appropriate type)',
								required: true,
							},
							{
								displayName: 'Data Type',
								name: 'dataType',
								type: 'options',
								options: [
									{ name: 'Auto-detect', value: 'auto' },
									{ name: 'Boolean', value: 'boolean' },
									{ name: 'Number', value: 'number' },
									{ name: 'String', value: 'string' },
									{ name: 'DateTime', value: 'datetime' },
								],
								default: 'auto',
								description: 'Data type for the value',
							},
						],
					},
				],
			},
			// Browse operation parameters
			{
				displayName: 'Browse Root Node',
				name: 'browseRootNode',
				type: 'string',
				displayOptions: {
					show: {
						operation: ['browse'],
					},
				},
				default: 'RootFolder',
				description: 'Root node to start browsing from',
			},
			{
				displayName: 'Browse Depth',
				name: 'browseDepth',
				type: 'number',
				displayOptions: {
					show: {
						operation: ['browse'],
					},
				},
				default: 2,
				description: 'Maximum depth for browsing',
			},
			{
				displayName: 'Include References',
				name: 'includeReferences',
				type: 'boolean',
				displayOptions: {
					show: {
						operation: ['browse'],
					},
				},
				default: false,
				description: 'Include reference information in browse results',
			},
			// Subscription parameters
			{
				displayName: 'Subscription Settings',
				name: 'subscriptionSettings',
				type: 'collection',
				displayOptions: {
					show: {
						operation: ['subscribe'],
					},
				},
				placeholder: 'Add Subscription Setting',
				default: {},
				options: [
					{
						displayName: 'Publishing Interval (ms)',
						name: 'publishingInterval',
						type: 'number',
						default: 1000,
						description: 'Publishing interval in milliseconds',
					},
					{
						displayName: 'Max Notifications Per Publish',
						name: 'maxNotificationsPerPublish',
						type: 'number',
						default: 100,
						description: 'Maximum notifications per publish cycle',
					},
					{
						displayName: 'Priority',
						name: 'priority',
						type: 'number',
						default: 128,
						description: 'Subscription priority (0-255)',
					},
					{
						displayName: 'Lifetime Count',
						name: 'lifetimeCount',
						type: 'number',
						default: 60,
						description: 'Subscription lifetime count',
					},
				],
			},
			// Method call parameters
			{
				displayName: 'Method Details',
				name: 'methodDetails',
				type: 'collection',
				displayOptions: {
					show: {
						operation: ['method'],
					},
				},
				placeholder: 'Add Method Detail',
				default: {},
				options: [
					{
						displayName: 'Object Node ID',
						name: 'objectNodeId',
						type: 'string',
						default: '',
						description: 'Node ID of the object containing the method',
						required: true,
					},
					{
						displayName: 'Method Node ID',
						name: 'methodNodeId',
						type: 'string',
						default: '',
						description: 'Node ID of the method to call',
						required: true,
					},
					{
						displayName: 'Input Arguments',
						name: 'inputArguments',
						type: 'string',
						typeOptions: {
							rows: 3,
						},
						default: '[]',
						description: 'JSON array of input arguments for the method',
					},
				],
			},
			// Output options
			{
				displayName: 'Output Options',
				name: 'outputOptions',
				type: 'collection',
				placeholder: 'Add Output Option',
				default: {},
				options: [
					{
						displayName: 'Include Timestamps',
						name: 'includeTimestamps',
						type: 'boolean',
						default: true,
						description: 'Include server and source timestamps in results',
					},
					{
						displayName: 'Include Quality',
						name: 'includeQuality',
						type: 'boolean',
						default: true,
						description: 'Include quality status in results',
					},
					{
						displayName: 'Include Node Info',
						name: 'includeNodeInfo',
						type: 'boolean',
						default: false,
						description: 'Include additional node information',
					},
					{
						displayName: 'Raw Output',
						name: 'rawOutput',
						type: 'boolean',
						default: false,
						description: 'Return raw OPC-UA response without processing',
					},
				],
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];

		for (let i = 0; i < items.length; i++) {
			const operation = this.getNodeParameter('operation', i) as string;
			const serverEndpoint = this.getNodeParameter('serverEndpoint', i) as string;
			const connectionSettings = this.getNodeParameter('connectionSettings', i, {}) as any;
			const securitySettings = this.getNodeParameter('securitySettings', i, {}) as any;
			const outputOptions = this.getNodeParameter('outputOptions', i, {}) as any;

			try {
				const startTime = Date.now();
				let result: any;

				// Create OPC-UA client configuration
				const clientOptions = this.buildClientOptions(serverEndpoint, connectionSettings, securitySettings);
				const client = OPCUAClient.create(clientOptions);

				try {
					// Connect to server
					await client.connect(serverEndpoint);
					
					// Create session
					const session = await client.createSession();

					// Execute operation
					switch (operation) {
						case 'read':
							result = await this.executeReadOperation(session, i, outputOptions);
							break;

						case 'write':
							result = await this.executeWriteOperation(session, i, outputOptions);
							break;

						case 'browse':
							result = await this.executeBrowseOperation(session, i, outputOptions);
							break;

						case 'subscribe':
							result = await this.executeSubscribeOperation(session, i, outputOptions);
							break;

						case 'method':
							result = await this.executeMethodOperation(session, i, outputOptions);
							break;

						case 'discovery':
							result = await this.executeDiscoveryOperation(outputOptions);
							break;

						default:
							throw new NodeOperationError(this.getNode(), `Unknown operation: ${operation}`);
					}

					// Close session and disconnect
					await session.close();
					await client.disconnect();

				} catch (error) {
					// Ensure cleanup even on error
					try {
						await client.disconnect();
					} catch (disconnectError) {
						// Ignore disconnect errors during cleanup
					}
					throw error;
				}

				const endTime = Date.now();

				// Build response
				const response = {
					operation,
					server_endpoint: serverEndpoint,
					result,
					metadata: {
						node_name: this.getNode().name,
						execution_time: new Date().toISOString(),
						operation_type: operation,
						processing_time_ms: endTime - startTime,
						security_mode: securitySettings.securityMode || 'None',
						connection_timeout: connectionSettings.connectionTimeout || 10000,
					},
				};

				returnData.push({
					json: response,
					pairedItem: { item: i },
				});

			} catch (error) {
				if (this.continueOnFail()) {
					returnData.push({
						json: {
							error: error.message,
							operation,
							server_endpoint: serverEndpoint,
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
					throw new NodeOperationError(this.getNode(), `OPC-UA operation failed: ${error.message}`);
				}
			}
		}

		return [returnData];
	}

	private buildClientOptions(endpoint: string, connectionSettings: any, securitySettings: any): any {
		const options: any = {
			applicationName: 'N8N PLC OPC-UA Client',
			connectionStrategy: {
				initialDelay: 1000,
				maxRetry: connectionSettings.maxReconnectAttempts || 5,
			},
			securityMode: MessageSecurityMode[securitySettings.securityMode || 'None'],
			securityPolicy: SecurityPolicy[securitySettings.securityPolicy || 'None'],
			endpoint_must_exist: false,
			keepSessionAlive: true,
			timeout: connectionSettings.connectionTimeout || 10000,
		};

		// Add certificate configuration if specified
		if (securitySettings.certificatePath && securitySettings.privateKeyPath) {
			options.certificateFile = securitySettings.certificatePath;
			options.privateKeyFile = securitySettings.privateKeyPath;
		}

		return options;
	}

	private async executeReadOperation(session: any, itemIndex: number, outputOptions: any): Promise<any> {
		const nodeIdsToRead = this.getNodeParameter('nodeIdsToRead.nodeId', itemIndex, []) as any[];
		
		if (nodeIdsToRead.length === 0) {
			throw new NodeOperationError(this.getNode(), 'No node IDs specified for read operation');
		}

		const readRequest = nodeIdsToRead.map(node => ({
			nodeId: node.nodeId,
			attributeId: AttributeIds.Value,
		}));

		const dataValues = await session.read(readRequest);
		
		const results = dataValues.map((dataValue: any, index: number) => {
			const nodeConfig = nodeIdsToRead[index];
			const result: any = {
				nodeId: nodeConfig.nodeId,
				alias: nodeConfig.alias || `node_${index}`,
				value: dataValue.value?.value,
				statusCode: dataValue.statusCode.name,
			};

			if (outputOptions.includeTimestamps) {
				result.serverTimestamp = dataValue.serverTimestamp;
				result.sourceTimestamp = dataValue.sourceTimestamp;
			}

			if (outputOptions.includeQuality) {
				result.quality = {
					good: dataValue.statusCode.isGood(),
					bad: dataValue.statusCode.isBad(),
					uncertain: dataValue.statusCode.isUncertain(),
				};
			}

			return result;
		});

		return {
			success: true,
			values_read: results.length,
			results,
		};
	}

	private async executeWriteOperation(session: any, itemIndex: number, outputOptions: any): Promise<any> {
		const nodeIdsToWrite = this.getNodeParameter('nodeIdsToWrite.nodeId', itemIndex, []) as any[];
		
		if (nodeIdsToWrite.length === 0) {
			throw new NodeOperationError(this.getNode(), 'No node IDs specified for write operation');
		}

		const writeRequest = nodeIdsToWrite.map(node => ({
			nodeId: node.nodeId,
			attributeId: AttributeIds.Value,
			value: {
				value: this.convertValue(node.value, node.dataType),
			},
		}));

		const statusCodes = await session.write(writeRequest);
		
		const results = statusCodes.map((statusCode: any, index: number) => {
			const nodeConfig = nodeIdsToWrite[index];
			return {
				nodeId: nodeConfig.nodeId,
				value: nodeConfig.value,
				statusCode: statusCode.name,
				success: statusCode.isGood(),
			};
		});

		return {
			success: results.every(r => r.success),
			values_written: results.length,
			results,
		};
	}

	private async executeBrowseOperation(session: any, itemIndex: number, outputOptions: any): Promise<any> {
		const browseRootNode = this.getNodeParameter('browseRootNode', itemIndex) as string;
		const browseDepth = this.getNodeParameter('browseDepth', itemIndex) as number;
		const includeReferences = this.getNodeParameter('includeReferences', itemIndex) as boolean;

		const browseResult = await session.browse(browseRootNode);
		
		const nodes = browseResult.references?.map((ref: any) => ({
			nodeId: ref.nodeId.toString(),
			browseName: ref.browseName.toString(),
			displayName: ref.displayName?.text || '',
			nodeClass: ref.nodeClass,
			typeDefinition: ref.typeDefinition?.toString(),
			references: includeReferences ? ref.references : undefined,
		})) || [];

		return {
			success: true,
			root_node: browseRootNode,
			depth: browseDepth,
			nodes_found: nodes.length,
			nodes,
		};
	}

	private async executeSubscribeOperation(session: any, itemIndex: number, outputOptions: any): Promise<any> {
		const subscriptionSettings = this.getNodeParameter('subscriptionSettings', itemIndex, {}) as any;
		const nodeIdsToRead = this.getNodeParameter('nodeIdsToRead.nodeId', itemIndex, []) as any[];

		// Create subscription
		const subscription = await session.createSubscription2({
			requestedPublishingInterval: subscriptionSettings.publishingInterval || 1000,
			requestedLifetimeCount: subscriptionSettings.lifetimeCount || 60,
			requestedMaxKeepAliveCount: 10,
			maxNotificationsPerPublish: subscriptionSettings.maxNotificationsPerPublish || 100,
			publishingEnabled: true,
			priority: subscriptionSettings.priority || 128,
		});

		// Monitor items
		const monitoredItems = [];
		for (const nodeConfig of nodeIdsToRead) {
			const monitoredItem = await subscription.monitor(
				{
					nodeId: nodeConfig.nodeId,
					attributeId: AttributeIds.Value,
				},
				{
					samplingInterval: 1000,
					discardOldest: true,
					queueSize: 100,
				}
			);

			monitoredItems.push({
				nodeId: nodeConfig.nodeId,
				alias: nodeConfig.alias,
				monitoredItemId: monitoredItem.monitoredItemId,
			});
		}

		return {
			success: true,
			subscription_id: subscription.subscriptionId,
			publishing_interval: subscription.publishingInterval,
			monitored_items: monitoredItems.length,
			items: monitoredItems,
		};
	}

	private async executeMethodOperation(session: any, itemIndex: number, outputOptions: any): Promise<any> {
		const methodDetails = this.getNodeParameter('methodDetails', itemIndex, {}) as any;
		
		if (!methodDetails.objectNodeId || !methodDetails.methodNodeId) {
			throw new NodeOperationError(this.getNode(), 'Object Node ID and Method Node ID are required for method calls');
		}

		let inputArguments = [];
		if (methodDetails.inputArguments) {
			try {
				inputArguments = JSON.parse(methodDetails.inputArguments);
			} catch (error) {
				throw new NodeOperationError(this.getNode(), 'Invalid JSON format for input arguments');
			}
		}

		const callRequest = {
			objectId: methodDetails.objectNodeId,
			methodId: methodDetails.methodNodeId,
			inputArguments,
		};

		const callResult = await session.call(callRequest);

		return {
			success: callResult.statusCode.isGood(),
			statusCode: callResult.statusCode.name,
			outputArguments: callResult.outputArguments || [],
			methodNodeId: methodDetails.methodNodeId,
			objectNodeId: methodDetails.objectNodeId,
		};
	}

	private async executeDiscoveryOperation(outputOptions: any): Promise<any> {
		// This would implement OPC-UA server discovery
		// For now, return a placeholder
		return {
			success: true,
			discovery_method: 'network_scan',
			servers_found: 0,
			servers: [],
		};
	}

	private convertValue(value: string, dataType: string): any {
		switch (dataType) {
			case 'boolean':
				return value.toLowerCase() === 'true';
			case 'number':
				return parseFloat(value);
			case 'string':
				return value;
			case 'datetime':
				return new Date(value);
			default:
				// Auto-detect
				if (value.toLowerCase() === 'true' || value.toLowerCase() === 'false') {
					return value.toLowerCase() === 'true';
				}
				if (!isNaN(parseFloat(value))) {
					return parseFloat(value);
				}
				return value;
		}
	}
} 