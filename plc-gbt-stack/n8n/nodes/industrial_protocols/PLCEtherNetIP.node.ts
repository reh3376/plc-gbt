import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeOperationError,
} from 'n8n-workflow';

// Note: This would require an EtherNet/IP library like 'ethernet-ip' or similar
// For now, we'll create the interface structure

export class PLCEtherNetIP implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'PLC EtherNet/IP',
		name: 'plcEtherNetIp',
		group: ['industrial', 'communication'],
		version: 1,
		subtitle: '={{$parameter["operation"]}}',
		description: 'EtherNet/IP industrial Ethernet client for CIP communication with PLCs',
		defaults: {
			name: 'PLC EtherNet/IP',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'ethernetIpCredentials',
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
						name: 'Read Tags',
						value: 'readTags',
						description: 'Read tag values from PLC',
						action: 'Read EtherNet/IP tags',
					},
					{
						name: 'Write Tags',
						value: 'writeTags',
						description: 'Write tag values to PLC',
						action: 'Write EtherNet/IP tags',
					},
					{
						name: 'Read Tag List',
						value: 'readTagList',
						description: 'Get list of available tags from PLC',
						action: 'Read tag list',
					},
					{
						name: 'Read Program List',
						value: 'readProgramList',
						description: 'Get list of programs from PLC',
						action: 'Read program list',
					},
					{
						name: 'Get Controller Properties',
						value: 'getControllerProperties',
						description: 'Read controller information and properties',
						action: 'Get controller properties',
					},
					{
						name: 'Discover Devices',
						value: 'discoverDevices',
						description: 'Discover EtherNet/IP devices on network',
						action: 'Discover devices',
					},
					{
						name: 'Read Multiple Services',
						value: 'readMultipleServices',
						description: 'Execute multiple CIP services in one request',
						action: 'Read multiple services',
					},
					{
						name: 'Custom CIP Service',
						value: 'customCipService',
						description: 'Execute custom CIP service request',
						action: 'Execute custom CIP service',
					},
				],
				default: 'readTags',
			},
			// Connection settings
			{
				displayName: 'PLC Host/IP',
				name: 'plcHost',
				type: 'string',
				default: '192.168.1.100',
				description: 'IP address of the EtherNet/IP device',
				required: true,
			},
			{
				displayName: 'Port',
				name: 'port',
				type: 'number',
				default: 44818,
				description: 'EtherNet/IP port (default: 44818)',
			},
			{
				displayName: 'Slot',
				name: 'slot',
				type: 'number',
				default: 0,
				description: 'PLC slot number (default: 0 for integrated controllers)',
				typeOptions: {
					minValue: 0,
					maxValue: 30,
				},
			},
			// Connection configuration
			{
				displayName: 'Connection Settings',
				name: 'connectionSettings',
				type: 'collection',
				placeholder: 'Add Connection Setting',
				default: {},
				options: [
					{
						displayName: 'Timeout (ms)',
						name: 'timeout',
						type: 'number',
						default: 5000,
						description: 'Connection timeout in milliseconds',
					},
					{
						displayName: 'Allow Half Open',
						name: 'allowHalfOpen',
						type: 'boolean',
						default: false,
						description: 'Allow half-open connections',
					},
					{
						displayName: 'Connection Size',
						name: 'connectionSize',
						type: 'number',
						default: 508,
						description: 'Connection size in bytes',
					},
					{
						displayName: 'RPI (ms)',
						name: 'rpi',
						type: 'number',
						default: 100,
						description: 'Requested Packet Interval in milliseconds',
					},
				],
			},
			// Tag operations
			{
				displayName: 'Tags to Read',
				name: 'tagsToRead',
				type: 'fixedCollection',
				displayOptions: {
					show: {
						operation: ['readTags'],
					},
				},
				default: {},
				typeOptions: {
					multipleValues: true,
				},
				options: [
					{
						name: 'tag',
						displayName: 'Tag',
						values: [
							{
								displayName: 'Tag Name',
								name: 'tagName',
								type: 'string',
								default: '',
								placeholder: 'Program:MainProgram.Temperature',
								description: 'Full tag name including program scope',
								required: true,
							},
							{
								displayName: 'Alias',
								name: 'alias',
								type: 'string',
								default: '',
								placeholder: 'temp_sensor_1',
								description: 'Alias name for the result',
							},
							{
								displayName: 'Array Index',
								name: 'arrayIndex',
								type: 'string',
								default: '',
								placeholder: '0 or [5] or [2,3]',
								description: 'Array index if reading array element',
							},
							{
								displayName: 'Elements Count',
								name: 'elementsCount',
								type: 'number',
								default: 1,
								description: 'Number of array elements to read',
							},
						],
					},
				],
			},
			{
				displayName: 'Tags to Write',
				name: 'tagsToWrite',
				type: 'fixedCollection',
				displayOptions: {
					show: {
						operation: ['writeTags'],
					},
				},
				default: {},
				typeOptions: {
					multipleValues: true,
				},
				options: [
					{
						name: 'tag',
						displayName: 'Tag',
						values: [
							{
								displayName: 'Tag Name',
								name: 'tagName',
								type: 'string',
								default: '',
								placeholder: 'Program:MainProgram.Setpoint',
								description: 'Full tag name including program scope',
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
									{ name: 'BOOL', value: 'BOOL' },
									{ name: 'SINT', value: 'SINT' },
									{ name: 'INT', value: 'INT' },
									{ name: 'DINT', value: 'DINT' },
									{ name: 'LINT', value: 'LINT' },
									{ name: 'REAL', value: 'REAL' },
									{ name: 'LREAL', value: 'LREAL' },
									{ name: 'STRING', value: 'STRING' },
								],
								default: 'auto',
								description: 'Data type for the tag',
							},
							{
								displayName: 'Array Index',
								name: 'arrayIndex',
								type: 'string',
								default: '',
								placeholder: '0 or [5] or [2,3]',
								description: 'Array index if writing array element',
							},
						],
					},
				],
			},
			// List operations settings
			{
				displayName: 'List Options',
				name: 'listOptions',
				type: 'collection',
				displayOptions: {
					show: {
						operation: ['readTagList', 'readProgramList'],
					},
				},
				placeholder: 'Add List Option',
				default: {},
				options: [
					{
						displayName: 'Program Name',
						name: 'programName',
						type: 'string',
						default: '',
						placeholder: 'MainProgram',
						description: 'Specific program name to list tags from (leave empty for all)',
					},
					{
						displayName: 'Include Data Types',
						name: 'includeDataTypes',
						type: 'boolean',
						default: true,
						description: 'Include data type information',
					},
					{
						displayName: 'Include Dimensions',
						name: 'includeDimensions',
						type: 'boolean',
						default: true,
						description: 'Include array dimension information',
					},
					{
						displayName: 'Filter Pattern',
						name: 'filterPattern',
						type: 'string',
						default: '',
						placeholder: '*Temp* or Motor_*',
						description: 'Filter tags by name pattern (wildcards supported)',
					},
				],
			},
			// Controller properties
			{
				displayName: 'Controller Info Options',
				name: 'controllerInfoOptions',
				type: 'collection',
				displayOptions: {
					show: {
						operation: ['getControllerProperties'],
					},
				},
				placeholder: 'Add Controller Info Option',
				default: {},
				options: [
					{
						displayName: 'Include Device Info',
						name: 'includeDeviceInfo',
						type: 'boolean',
						default: true,
						description: 'Include device identification information',
					},
					{
						displayName: 'Include Status',
						name: 'includeStatus',
						type: 'boolean',
						default: true,
						description: 'Include controller status information',
					},
					{
						displayName: 'Include Timing',
						name: 'includeTiming',
						type: 'boolean',
						default: false,
						description: 'Include timing and performance information',
					},
				],
			},
			// Discovery settings
			{
				displayName: 'Discovery Settings',
				name: 'discoverySettings',
				type: 'collection',
				displayOptions: {
					show: {
						operation: ['discoverDevices'],
					},
				},
				placeholder: 'Add Discovery Setting',
				default: {},
				options: [
					{
						displayName: 'Network Range',
						name: 'networkRange',
						type: 'string',
						default: '192.168.1.0/24',
						description: 'Network range to scan (CIDR notation)',
					},
					{
						displayName: 'Scan Timeout (ms)',
						name: 'scanTimeout',
						type: 'number',
						default: 3000,
						description: 'Timeout for each device scan',
					},
					{
						displayName: 'Max Concurrent Scans',
						name: 'maxConcurrent',
						type: 'number',
						default: 10,
						description: 'Maximum concurrent device scans',
					},
					{
						displayName: 'Include Vendor Info',
						name: 'includeVendorInfo',
						type: 'boolean',
						default: true,
						description: 'Include vendor and device type information',
					},
				],
			},
			// Custom CIP service
			{
				displayName: 'CIP Service Details',
				name: 'cipServiceDetails',
				type: 'collection',
				displayOptions: {
					show: {
						operation: ['customCipService'],
					},
				},
				placeholder: 'Add CIP Service Detail',
				default: {},
				options: [
					{
						displayName: 'Service Code',
						name: 'serviceCode',
						type: 'string',
						default: '',
						placeholder: '0x0E (hex) or 14 (decimal)',
						description: 'CIP service code',
						required: true,
					},
					{
						displayName: 'Class ID',
						name: 'classId',
						type: 'string',
						default: '',
						placeholder: '0x6B',
						description: 'CIP class ID',
						required: true,
					},
					{
						displayName: 'Instance ID',
						name: 'instanceId',
						type: 'string',
						default: '1',
						description: 'CIP instance ID',
					},
					{
						displayName: 'Attribute ID',
						name: 'attributeId',
						type: 'string',
						default: '',
						description: 'CIP attribute ID (if applicable)',
					},
					{
						displayName: 'Request Data',
						name: 'requestData',
						type: 'string',
						typeOptions: {
							rows: 3,
						},
						default: '',
						placeholder: 'Hex bytes: 01 02 03 or JSON array: [1, 2, 3]',
						description: 'Request data as hex string or JSON byte array',
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
						displayName: 'Include Metadata',
						name: 'includeMetadata',
						type: 'boolean',
						default: true,
						description: 'Include operation metadata in response',
					},
					{
						displayName: 'Include Timing',
						name: 'includeTiming',
						type: 'boolean',
						default: true,
						description: 'Include timing information',
					},
					{
						displayName: 'Raw Response',
						name: 'rawResponse',
						type: 'boolean',
						default: false,
						description: 'Return raw EtherNet/IP response without processing',
					},
					{
						displayName: 'Verbose Logging',
						name: 'verboseLogging',
						type: 'boolean',
						default: false,
						description: 'Enable verbose logging for debugging',
					},
					{
						displayName: 'Quality Indicators',
						name: 'qualityIndicators',
						type: 'boolean',
						default: true,
						description: 'Include data quality indicators',
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
			const plcHost = this.getNodeParameter('plcHost', i) as string;
			const port = this.getNodeParameter('port', i) as number;
			const slot = this.getNodeParameter('slot', i) as number;
			const connectionSettings = this.getNodeParameter('connectionSettings', i, {}) as any;
			const outputOptions = this.getNodeParameter('outputOptions', i, {}) as any;

			try {
				const startTime = Date.now();
				let result: any;

				// Create EtherNet/IP client
				const client = await this.createEtherNetIpClient(plcHost, port, slot, connectionSettings);

				try {
					// Execute operation
					switch (operation) {
						case 'readTags':
							result = await this.executeReadTags(client, i, outputOptions);
							break;

						case 'writeTags':
							result = await this.executeWriteTags(client, i, outputOptions);
							break;

						case 'readTagList':
							result = await this.executeReadTagList(client, i, outputOptions);
							break;

						case 'readProgramList':
							result = await this.executeReadProgramList(client, i, outputOptions);
							break;

						case 'getControllerProperties':
							result = await this.executeGetControllerProperties(client, i, outputOptions);
							break;

						case 'discoverDevices':
							result = await this.executeDiscoverDevices(i, outputOptions);
							break;

						case 'readMultipleServices':
							result = await this.executeReadMultipleServices(client, i, outputOptions);
							break;

						case 'customCipService':
							result = await this.executeCustomCipService(client, i, outputOptions);
							break;

						default:
							throw new NodeOperationError(this.getNode(), `Unknown operation: ${operation}`);
					}

					// Close connection
					await this.closeEtherNetIpClient(client);

				} catch (error) {
					// Ensure cleanup
					await this.closeEtherNetIpClient(client);
					throw error;
				}

				const endTime = Date.now();

				// Build response
				const response = {
					operation,
					plc_host: plcHost,
					port,
					slot,
					result,
					metadata: {
						node_name: this.getNode().name,
						execution_time: new Date().toISOString(),
						operation_type: operation,
						processing_time_ms: endTime - startTime,
						timeout: connectionSettings.timeout || 5000,
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
							plc_host: plcHost,
							port,
							slot,
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
					throw new NodeOperationError(this.getNode(), `EtherNet/IP operation failed: ${error.message}`);
				}
			}
		}

		return [returnData];
	}

	private async createEtherNetIpClient(host: string, port: number, slot: number, connectionSettings: any): Promise<any> {
		// This would create an actual EtherNet/IP client
		// For now, return a mock client object
		return {
			host,
			port,
			slot,
			timeout: connectionSettings.timeout || 5000,
			connected: true,
			connectionSize: connectionSettings.connectionSize || 508,
			rpi: connectionSettings.rpi || 100,
		};
	}

	private async closeEtherNetIpClient(client: any): Promise<void> {
		// This would close the actual EtherNet/IP connection
		if (client) {
			client.connected = false;
		}
	}

	private async executeReadTags(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const tagsToRead = this.getNodeParameter('tagsToRead.tag', itemIndex, []) as any[];
		
		if (tagsToRead.length === 0) {
			throw new NodeOperationError(this.getNode(), 'No tags specified for read operation');
		}

		// Mock implementation - would use actual EtherNet/IP library
		const results = tagsToRead.map((tag, index) => {
			const mockValue = this.generateMockValue(tag.tagName);
			
			return {
				tag_name: tag.tagName,
				alias: tag.alias || `tag_${index}`,
				value: mockValue.value,
				data_type: mockValue.dataType,
				quality: 'Good',
				timestamp: new Date().toISOString(),
				array_index: tag.arrayIndex || null,
				elements_count: tag.elementsCount || 1,
			};
		});

		return {
			success: true,
			operation: 'read_tags',
			tags_read: results.length,
			results,
		};
	}

	private async executeWriteTags(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const tagsToWrite = this.getNodeParameter('tagsToWrite.tag', itemIndex, []) as any[];
		
		if (tagsToWrite.length === 0) {
			throw new NodeOperationError(this.getNode(), 'No tags specified for write operation');
		}

		// Mock implementation
		const results = tagsToWrite.map((tag) => ({
			tag_name: tag.tagName,
			value_written: this.convertValue(tag.value, tag.dataType),
			data_type: tag.dataType || 'auto',
			success: true,
			timestamp: new Date().toISOString(),
			array_index: tag.arrayIndex || null,
		}));

		return {
			success: true,
			operation: 'write_tags',
			tags_written: results.length,
			results,
		};
	}

	private async executeReadTagList(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const listOptions = this.getNodeParameter('listOptions', itemIndex, {}) as any;

		// Mock tag list
		const mockTags = [
			{
				name: 'Program:MainProgram.Temperature',
				data_type: 'REAL',
				dimensions: [],
				scope: 'Program',
				external_access: 'Read/Write',
			},
			{
				name: 'Program:MainProgram.Pressure',
				data_type: 'REAL',
				dimensions: [],
				scope: 'Program',
				external_access: 'Read/Write',
			},
			{
				name: 'Global.MotorSpeeds',
				data_type: 'REAL',
				dimensions: [10],
				scope: 'Global',
				external_access: 'Read/Write',
			},
		];

		let filteredTags = mockTags;
		if (listOptions.filterPattern) {
			const pattern = listOptions.filterPattern.replace(/\*/g, '.*');
			const regex = new RegExp(pattern, 'i');
			filteredTags = mockTags.filter(tag => regex.test(tag.name));
		}

		if (listOptions.programName) {
			filteredTags = filteredTags.filter(tag => 
				tag.name.startsWith(`Program:${listOptions.programName}.`)
			);
		}

		return {
			success: true,
			operation: 'read_tag_list',
			program_name: listOptions.programName || 'All',
			tags_found: filteredTags.length,
			tags: filteredTags,
		};
	}

	private async executeReadProgramList(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		// Mock program list
		const programs = [
			{
				name: 'MainProgram',
				type: 'Program',
				instance: 'MainProgram',
				disabled: false,
				use_as_folder: false,
			},
			{
				name: 'Safety_Program',
				type: 'Program',
				instance: 'Safety_Program',
				disabled: false,
				use_as_folder: false,
			},
		];

		return {
			success: true,
			operation: 'read_program_list',
			programs_found: programs.length,
			programs,
		};
	}

	private async executeGetControllerProperties(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const controllerInfoOptions = this.getNodeParameter('controllerInfoOptions', itemIndex, {}) as any;

		// Mock controller properties
		const properties: any = {
			success: true,
			operation: 'get_controller_properties',
		};

		if (controllerInfoOptions.includeDeviceInfo !== false) {
			properties.device_info = {
				vendor: 'Rockwell Automation/Allen-Bradley',
				product_type: 'Programmable Logic Controller',
				product_code: 55,
				major_revision: 20,
				minor_revision: 11,
				serial_number: '12345678',
				product_name: 'CompactLogix 5370 L3',
			};
		}

		if (controllerInfoOptions.includeStatus !== false) {
			properties.status = {
				mode: 'Run',
				keyswitch_position: 'Run',
				forces_enabled: false,
				forces_installed: false,
				safety_network_number: 0,
				last_keysw_state: 'Run',
			};
		}

		if (controllerInfoOptions.includeTiming) {
			properties.timing = {
				scan_time_last: 1.25,
				scan_time_max: 2.1,
				scan_time_average: 1.3,
				cpu_utilization: 15.2,
			};
		}

		return properties;
	}

	private async executeDiscoverDevices(itemIndex: number, outputOptions: any): Promise<any> {
		const discoverySettings = this.getNodeParameter('discoverySettings', itemIndex, {}) as any;

		// Mock device discovery
		const devices = [
			{
				ip_address: '192.168.1.100',
				device_type: 'CompactLogix',
				vendor: 'Rockwell Automation',
				product_name: 'CompactLogix 5370 L3',
				serial_number: '12345678',
				revision: '20.11',
				status: 'online',
				response_time_ms: 12,
			},
			{
				ip_address: '192.168.1.101',
				device_type: 'PowerFlex',
				vendor: 'Rockwell Automation',
				product_name: 'PowerFlex 525',
				serial_number: '87654321',
				revision: '5.001',
				status: 'online',
				response_time_ms: 8,
			},
		];

		return {
			success: true,
			operation: 'discover_devices',
			network_range: discoverySettings.networkRange || '192.168.1.0/24',
			devices_found: devices.length,
			scan_timeout: discoverySettings.scanTimeout || 3000,
			devices,
		};
	}

	private async executeReadMultipleServices(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		// Mock multiple services execution
		return {
			success: true,
			operation: 'read_multiple_services',
			services_executed: 3,
			results: [
				{ service: 'read_tag', tag: 'Temperature', value: 72.5, success: true },
				{ service: 'read_tag', tag: 'Pressure', value: 145.2, success: true },
				{ service: 'get_attribute', class_id: 1, instance_id: 1, attribute_id: 1, value: 'Online', success: true },
			],
		};
	}

	private async executeCustomCipService(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const cipServiceDetails = this.getNodeParameter('cipServiceDetails', itemIndex, {}) as any;

		if (!cipServiceDetails.serviceCode || !cipServiceDetails.classId) {
			throw new NodeOperationError(this.getNode(), 'Service Code and Class ID are required for custom CIP service');
		}

		// Mock CIP service execution
		return {
			success: true,
			operation: 'custom_cip_service',
			service_code: cipServiceDetails.serviceCode,
			class_id: cipServiceDetails.classId,
			instance_id: cipServiceDetails.instanceId || 1,
			attribute_id: cipServiceDetails.attributeId || null,
			response_data: [0x00, 0x01, 0x02], // Mock response
			general_status: 0x00, // Success
			extended_status: [],
		};
	}

	private generateMockValue(tagName: string): { value: any; dataType: string } {
		// Generate mock values based on tag name patterns
		if (tagName.toLowerCase().includes('temp')) {
			return { value: 72.5, dataType: 'REAL' };
		} else if (tagName.toLowerCase().includes('pressure')) {
			return { value: 145.2, dataType: 'REAL' };
		} else if (tagName.toLowerCase().includes('motor')) {
			return { value: true, dataType: 'BOOL' };
		} else if (tagName.toLowerCase().includes('count')) {
			return { value: 1250, dataType: 'DINT' };
		} else {
			return { value: 42, dataType: 'INT' };
		}
	}

	private convertValue(value: string, dataType: string): any {
		switch (dataType?.toUpperCase()) {
			case 'BOOL':
				return this.parseBoolean(value);
			case 'SINT':
			case 'INT':
			case 'DINT':
			case 'LINT':
				return parseInt(value);
			case 'REAL':
			case 'LREAL':
				return parseFloat(value);
			case 'STRING':
				return value;
			default:
				// Auto-detect
				if (value.toLowerCase() === 'true' || value.toLowerCase() === 'false') {
					return this.parseBoolean(value);
				}
				if (!isNaN(parseFloat(value))) {
					return parseFloat(value);
				}
				return value;
		}
	}

	private parseBoolean(value: string): boolean {
		const lowerValue = value.toLowerCase().trim();
		return lowerValue === 'true' || lowerValue === '1' || lowerValue === 'on';
	}
} 