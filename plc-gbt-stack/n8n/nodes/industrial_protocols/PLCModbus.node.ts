import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeOperationError,
} from 'n8n-workflow';

import ModbusRTU from 'modbus-serial';

export class PLCModbus implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'PLC Modbus',
		name: 'plcModbus',
		group: ['industrial', 'communication'],
		version: 1,
		subtitle: '={{$parameter["operation"]}}',
		description: 'Modbus TCP/RTU client for industrial automation communication',
		defaults: {
			name: 'PLC Modbus',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'modbusCredentials',
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
						name: 'Read Coils',
						value: 'readCoils',
						description: 'Read coil status (function code 1)',
						action: 'Read Modbus coils',
					},
					{
						name: 'Read Discrete Inputs',
						value: 'readDiscreteInputs',
						description: 'Read discrete input status (function code 2)',
						action: 'Read discrete inputs',
					},
					{
						name: 'Read Holding Registers',
						value: 'readHoldingRegisters',
						description: 'Read holding register values (function code 3)',
						action: 'Read holding registers',
					},
					{
						name: 'Read Input Registers',
						value: 'readInputRegisters',
						description: 'Read input register values (function code 4)',
						action: 'Read input registers',
					},
					{
						name: 'Write Single Coil',
						value: 'writeSingleCoil',
						description: 'Write single coil (function code 5)',
						action: 'Write single coil',
					},
					{
						name: 'Write Single Register',
						value: 'writeSingleRegister',
						description: 'Write single holding register (function code 6)',
						action: 'Write single register',
					},
					{
						name: 'Write Multiple Coils',
						value: 'writeMultipleCoils',
						description: 'Write multiple coils (function code 15)',
						action: 'Write multiple coils',
					},
					{
						name: 'Write Multiple Registers',
						value: 'writeMultipleRegisters',
						description: 'Write multiple holding registers (function code 16)',
						action: 'Write multiple registers',
					},
				],
				default: 'readHoldingRegisters',
			},
			// Connection settings
			{
				displayName: 'Connection Type',
				name: 'connectionType',
				type: 'options',
				options: [
					{
						name: 'Modbus TCP',
						value: 'tcp',
					},
					{
						name: 'Modbus RTU over TCP',
						value: 'rtu-tcp',
					},
					{
						name: 'Modbus RTU (Serial)',
						value: 'rtu-serial',
					},
				],
				default: 'tcp',
				description: 'Type of Modbus connection',
			},
			{
				displayName: 'Host/IP Address',
				name: 'host',
				type: 'string',
				displayOptions: {
					show: {
						connectionType: ['tcp', 'rtu-tcp'],
					},
				},
				default: 'localhost',
				description: 'Modbus server host or IP address',
				required: true,
			},
			{
				displayName: 'Port',
				name: 'port',
				type: 'number',
				displayOptions: {
					show: {
						connectionType: ['tcp', 'rtu-tcp'],
					},
				},
				default: 502,
				description: 'Modbus server port number',
			},
			{
				displayName: 'Serial Port',
				name: 'serialPort',
				type: 'string',
				displayOptions: {
					show: {
						connectionType: ['rtu-serial'],
					},
				},
				default: '/dev/ttyUSB0',
				placeholder: '/dev/ttyUSB0 or COM1',
				description: 'Serial port device path',
				required: true,
			},
			{
				displayName: 'Unit ID',
				name: 'unitId',
				type: 'number',
				default: 1,
				description: 'Modbus unit/slave ID (1-247)',
				typeOptions: {
					minValue: 1,
					maxValue: 247,
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
						displayName: 'Retry Count',
						name: 'retryCount',
						type: 'number',
						default: 3,
						description: 'Number of retry attempts',
					},
					{
						displayName: 'Delay Between Retries (ms)',
						name: 'retryDelay',
						type: 'number',
						default: 1000,
						description: 'Delay between retry attempts',
					},
				],
			},
			// Serial settings (for RTU)
			{
				displayName: 'Serial Settings',
				name: 'serialSettings',
				type: 'collection',
				displayOptions: {
					show: {
						connectionType: ['rtu-serial'],
					},
				},
				placeholder: 'Add Serial Setting',
				default: {},
				options: [
					{
						displayName: 'Baud Rate',
						name: 'baudRate',
						type: 'options',
						options: [
							{ name: '9600', value: 9600 },
							{ name: '19200', value: 19200 },
							{ name: '38400', value: 38400 },
							{ name: '57600', value: 57600 },
							{ name: '115200', value: 115200 },
						],
						default: 9600,
						description: 'Serial baud rate',
					},
					{
						displayName: 'Data Bits',
						name: 'dataBits',
						type: 'options',
						options: [
							{ name: '7', value: 7 },
							{ name: '8', value: 8 },
						],
						default: 8,
						description: 'Number of data bits',
					},
					{
						displayName: 'Stop Bits',
						name: 'stopBits',
						type: 'options',
						options: [
							{ name: '1', value: 1 },
							{ name: '2', value: 2 },
						],
						default: 1,
						description: 'Number of stop bits',
					},
					{
						displayName: 'Parity',
						name: 'parity',
						type: 'options',
						options: [
							{ name: 'None', value: 'none' },
							{ name: 'Even', value: 'even' },
							{ name: 'Odd', value: 'odd' },
						],
						default: 'none',
						description: 'Parity setting',
					},
				],
			},
			// Read operation parameters
			{
				displayName: 'Start Address',
				name: 'startAddress',
				type: 'number',
				displayOptions: {
					show: {
						operation: ['readCoils', 'readDiscreteInputs', 'readHoldingRegisters', 'readInputRegisters'],
					},
				},
				default: 0,
				description: 'Starting address to read from (0-based)',
				typeOptions: {
					minValue: 0,
					maxValue: 65535,
				},
			},
			{
				displayName: 'Quantity',
				name: 'quantity',
				type: 'number',
				displayOptions: {
					show: {
						operation: ['readCoils', 'readDiscreteInputs', 'readHoldingRegisters', 'readInputRegisters'],
					},
				},
				default: 1,
				description: 'Number of values to read',
				typeOptions: {
					minValue: 1,
					maxValue: 2000,
				},
			},
			// Write single value parameters
			{
				displayName: 'Address',
				name: 'address',
				type: 'number',
				displayOptions: {
					show: {
						operation: ['writeSingleCoil', 'writeSingleRegister'],
					},
				},
				default: 0,
				description: 'Address to write to (0-based)',
				typeOptions: {
					minValue: 0,
					maxValue: 65535,
				},
			},
			{
				displayName: 'Value',
				name: 'value',
				type: 'string',
				displayOptions: {
					show: {
						operation: ['writeSingleCoil', 'writeSingleRegister'],
					},
				},
				default: '',
				description: 'Value to write (boolean for coils, number for registers)',
				required: true,
			},
			// Write multiple values parameters
			{
				displayName: 'Start Address',
				name: 'writeStartAddress',
				type: 'number',
				displayOptions: {
					show: {
						operation: ['writeMultipleCoils', 'writeMultipleRegisters'],
					},
				},
				default: 0,
				description: 'Starting address to write to (0-based)',
				typeOptions: {
					minValue: 0,
					maxValue: 65535,
				},
			},
			{
				displayName: 'Values',
				name: 'values',
				type: 'string',
				typeOptions: {
					rows: 3,
				},
				displayOptions: {
					show: {
						operation: ['writeMultipleCoils', 'writeMultipleRegisters'],
					},
				},
				default: '',
				placeholder: 'JSON array: [true, false, true] or [100, 200, 300]',
				description: 'JSON array of values to write',
				required: true,
			},
			// Data processing options
			{
				displayName: 'Data Processing',
				name: 'dataProcessing',
				type: 'collection',
				placeholder: 'Add Data Processing Option',
				default: {},
				options: [
					{
						displayName: 'Register Format',
						name: 'registerFormat',
						type: 'options',
						displayOptions: {
							show: {
								'/operation': ['readHoldingRegisters', 'readInputRegisters', 'writeSingleRegister', 'writeMultipleRegisters'],
							},
						},
						options: [
							{ name: 'Raw 16-bit', value: 'raw' },
							{ name: 'Signed Int16', value: 'int16' },
							{ name: 'Unsigned Int16', value: 'uint16' },
							{ name: 'Float32 (2 registers)', value: 'float32' },
							{ name: 'Int32 (2 registers)', value: 'int32' },
						],
						default: 'uint16',
						description: 'How to interpret register data',
					},
					{
						displayName: 'Byte Order',
						name: 'byteOrder',
						type: 'options',
						displayOptions: {
							show: {
								'/operation': ['readHoldingRegisters', 'readInputRegisters'],
								'registerFormat': ['float32', 'int32'],
							},
						},
						options: [
							{ name: 'Big Endian', value: 'BE' },
							{ name: 'Little Endian', value: 'LE' },
							{ name: 'Big Endian Word Swap', value: 'BEW' },
							{ name: 'Little Endian Word Swap', value: 'LEW' },
						],
						default: 'BE',
						description: 'Byte order for multi-register values',
					},
					{
						displayName: 'Scale Factor',
						name: 'scaleFactor',
						type: 'number',
						default: 1,
						description: 'Scale factor to apply to register values',
					},
					{
						displayName: 'Offset',
						name: 'offset',
						type: 'number',
						default: 0,
						description: 'Offset to add to register values',
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
						description: 'Return raw Modbus response without processing',
					},
					{
						displayName: 'Address Labels',
						name: 'addressLabels',
						type: 'string',
						typeOptions: {
							rows: 3,
						},
						default: '',
						placeholder: '{"0": "Temperature", "1": "Pressure"}',
						description: 'JSON object mapping addresses to descriptive labels',
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
			const connectionType = this.getNodeParameter('connectionType', i) as string;
			const unitId = this.getNodeParameter('unitId', i) as number;
			const connectionSettings = this.getNodeParameter('connectionSettings', i, {}) as any;
			const dataProcessing = this.getNodeParameter('dataProcessing', i, {}) as any;
			const outputOptions = this.getNodeParameter('outputOptions', i, {}) as any;

			try {
				const startTime = Date.now();
				let result: any;

				// Create and configure Modbus client
				const client = new ModbusRTU();
				
				// Configure connection based on type
				await this.setupConnection(client, connectionType, i, connectionSettings);

				// Set unit ID
				client.setID(unitId);

				// Set timeout
				client.setTimeout(connectionSettings.timeout || 5000);

				try {
					// Execute operation
					switch (operation) {
						case 'readCoils':
							result = await this.executeReadCoils(client, i, dataProcessing, outputOptions);
							break;

						case 'readDiscreteInputs':
							result = await this.executeReadDiscreteInputs(client, i, dataProcessing, outputOptions);
							break;

						case 'readHoldingRegisters':
							result = await this.executeReadHoldingRegisters(client, i, dataProcessing, outputOptions);
							break;

						case 'readInputRegisters':
							result = await this.executeReadInputRegisters(client, i, dataProcessing, outputOptions);
							break;

						case 'writeSingleCoil':
							result = await this.executeWriteSingleCoil(client, i, outputOptions);
							break;

						case 'writeSingleRegister':
							result = await this.executeWriteSingleRegister(client, i, outputOptions);
							break;

						case 'writeMultipleCoils':
							result = await this.executeWriteMultipleCoils(client, i, outputOptions);
							break;

						case 'writeMultipleRegisters':
							result = await this.executeWriteMultipleRegisters(client, i, outputOptions);
							break;

						default:
							throw new NodeOperationError(this.getNode(), `Unknown operation: ${operation}`);
					}

					// Close connection
					client.close(() => {});

				} catch (error) {
					// Ensure cleanup
					client.close(() => {});
					throw error;
				}

				const endTime = Date.now();

				// Build response
				const response = {
					operation,
					connection_type: connectionType,
					unit_id: unitId,
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
							connection_type: connectionType,
							unit_id: unitId,
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
					throw new NodeOperationError(this.getNode(), `Modbus operation failed: ${error.message}`);
				}
			}
		}

		return [returnData];
	}

	private async setupConnection(client: any, connectionType: string, itemIndex: number, connectionSettings: any): Promise<void> {
		switch (connectionType) {
			case 'tcp':
				const host = this.getNodeParameter('host', itemIndex) as string;
				const port = this.getNodeParameter('port', itemIndex) as number;
				await client.connectTCP(host, { port });
				break;

			case 'rtu-tcp':
				const rtudHost = this.getNodeParameter('host', itemIndex) as string;
				const rtudPort = this.getNodeParameter('port', itemIndex) as number;
				await client.connectRTUBuffered(rtudHost, { port: rtudPort });
				break;

			case 'rtu-serial':
				const serialPort = this.getNodeParameter('serialPort', itemIndex) as string;
				const serialSettings = this.getNodeParameter('serialSettings', itemIndex, {}) as any;
				
				const serialOptions = {
					baudRate: serialSettings.baudRate || 9600,
					dataBits: serialSettings.dataBits || 8,
					stopBits: serialSettings.stopBits || 1,
					parity: serialSettings.parity || 'none',
				};
				
				await client.connectRTUBuffered(serialPort, serialOptions);
				break;

			default:
				throw new NodeOperationError(this.getNode(), `Unknown connection type: ${connectionType}`);
		}
	}

	private async executeReadCoils(client: any, itemIndex: number, dataProcessing: any, outputOptions: any): Promise<any> {
		const startAddress = this.getNodeParameter('startAddress', itemIndex) as number;
		const quantity = this.getNodeParameter('quantity', itemIndex) as number;

		const response = await client.readCoils(startAddress, quantity);
		
		const results = response.data.map((value: boolean, index: number) => ({
			address: startAddress + index,
			value,
			label: this.getAddressLabel(startAddress + index, outputOptions.addressLabels),
		}));

		return {
			success: true,
			function_code: 1,
			start_address: startAddress,
			quantity,
			values_read: results.length,
			results,
		};
	}

	private async executeReadDiscreteInputs(client: any, itemIndex: number, dataProcessing: any, outputOptions: any): Promise<any> {
		const startAddress = this.getNodeParameter('startAddress', itemIndex) as number;
		const quantity = this.getNodeParameter('quantity', itemIndex) as number;

		const response = await client.readDiscreteInputs(startAddress, quantity);
		
		const results = response.data.map((value: boolean, index: number) => ({
			address: startAddress + index,
			value,
			label: this.getAddressLabel(startAddress + index, outputOptions.addressLabels),
		}));

		return {
			success: true,
			function_code: 2,
			start_address: startAddress,
			quantity,
			values_read: results.length,
			results,
		};
	}

	private async executeReadHoldingRegisters(client: any, itemIndex: number, dataProcessing: any, outputOptions: any): Promise<any> {
		const startAddress = this.getNodeParameter('startAddress', itemIndex) as number;
		const quantity = this.getNodeParameter('quantity', itemIndex) as number;

		const response = await client.readHoldingRegisters(startAddress, quantity);
		
		const results = this.processRegisterData(
			response.data,
			startAddress,
			dataProcessing,
			outputOptions.addressLabels
		);

		return {
			success: true,
			function_code: 3,
			start_address: startAddress,
			quantity,
			values_read: results.length,
			register_format: dataProcessing.registerFormat || 'uint16',
			results,
		};
	}

	private async executeReadInputRegisters(client: any, itemIndex: number, dataProcessing: any, outputOptions: any): Promise<any> {
		const startAddress = this.getNodeParameter('startAddress', itemIndex) as number;
		const quantity = this.getNodeParameter('quantity', itemIndex) as number;

		const response = await client.readInputRegisters(startAddress, quantity);
		
		const results = this.processRegisterData(
			response.data,
			startAddress,
			dataProcessing,
			outputOptions.addressLabels
		);

		return {
			success: true,
			function_code: 4,
			start_address: startAddress,
			quantity,
			values_read: results.length,
			register_format: dataProcessing.registerFormat || 'uint16',
			results,
		};
	}

	private async executeWriteSingleCoil(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const address = this.getNodeParameter('address', itemIndex) as number;
		const value = this.getNodeParameter('value', itemIndex) as string;
		
		const boolValue = this.parseBoolean(value);
		const response = await client.writeCoil(address, boolValue);

		return {
			success: true,
			function_code: 5,
			address,
			value: boolValue,
			response_value: response.state,
		};
	}

	private async executeWriteSingleRegister(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const address = this.getNodeParameter('address', itemIndex) as number;
		const value = this.getNodeParameter('value', itemIndex) as string;
		
		const numValue = parseInt(value);
		if (isNaN(numValue)) {
			throw new NodeOperationError(this.getNode(), `Invalid register value: ${value}`);
		}

		const response = await client.writeRegister(address, numValue);

		return {
			success: true,
			function_code: 6,
			address,
			value: numValue,
			response_value: response.value,
		};
	}

	private async executeWriteMultipleCoils(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const startAddress = this.getNodeParameter('writeStartAddress', itemIndex) as number;
		const valuesString = this.getNodeParameter('values', itemIndex) as string;
		
		let values: boolean[];
		try {
			values = JSON.parse(valuesString);
			if (!Array.isArray(values)) {
				throw new Error('Values must be an array');
			}
		} catch (error) {
			throw new NodeOperationError(this.getNode(), `Invalid values JSON: ${error.message}`);
		}

		const response = await client.writeCoils(startAddress, values);

		return {
			success: true,
			function_code: 15,
			start_address: startAddress,
			quantity: values.length,
			values_written: values,
		};
	}

	private async executeWriteMultipleRegisters(client: any, itemIndex: number, outputOptions: any): Promise<any> {
		const startAddress = this.getNodeParameter('writeStartAddress', itemIndex) as number;
		const valuesString = this.getNodeParameter('values', itemIndex) as string;
		
		let values: number[];
		try {
			values = JSON.parse(valuesString);
			if (!Array.isArray(values)) {
				throw new Error('Values must be an array');
			}
		} catch (error) {
			throw new NodeOperationError(this.getNode(), `Invalid values JSON: ${error.message}`);
		}

		const response = await client.writeRegisters(startAddress, values);

		return {
			success: true,
			function_code: 16,
			start_address: startAddress,
			quantity: values.length,
			values_written: values,
		};
	}

	private processRegisterData(data: number[], startAddress: number, dataProcessing: any, addressLabels?: string): any[] {
		const format = dataProcessing.registerFormat || 'uint16';
		const scaleFactor = dataProcessing.scaleFactor || 1;
		const offset = dataProcessing.offset || 0;
		const byteOrder = dataProcessing.byteOrder || 'BE';

		const results: any[] = [];

		switch (format) {
			case 'raw':
			case 'uint16':
				data.forEach((value, index) => {
					results.push({
						address: startAddress + index,
						raw_value: value,
						value: (value * scaleFactor) + offset,
						label: this.getAddressLabel(startAddress + index, addressLabels),
					});
				});
				break;

			case 'int16':
				data.forEach((value, index) => {
					// Convert unsigned to signed 16-bit
					const signedValue = value > 32767 ? value - 65536 : value;
					results.push({
						address: startAddress + index,
						raw_value: value,
						value: (signedValue * scaleFactor) + offset,
						label: this.getAddressLabel(startAddress + index, addressLabels),
					});
				});
				break;

			case 'float32':
			case 'int32':
				// Process pairs of registers
				for (let i = 0; i < data.length; i += 2) {
					if (i + 1 < data.length) {
						const value = this.combineRegisters(data[i], data[i + 1], format, byteOrder);
						results.push({
							address: startAddress + i,
							address_span: [startAddress + i, startAddress + i + 1],
							raw_values: [data[i], data[i + 1]],
							value: (value * scaleFactor) + offset,
							label: this.getAddressLabel(startAddress + i, addressLabels),
						});
					}
				}
				break;
		}

		return results;
	}

	private combineRegisters(reg1: number, reg2: number, format: string, byteOrder: string): number {
		let combined: number;

		// Combine registers based on byte order
		switch (byteOrder) {
			case 'BE': // Big Endian
				combined = (reg1 << 16) | reg2;
				break;
			case 'LE': // Little Endian
				combined = (reg2 << 16) | reg1;
				break;
			case 'BEW': // Big Endian Word Swap
				combined = (reg2 << 16) | reg1;
				break;
			case 'LEW': // Little Endian Word Swap
				combined = (reg1 << 16) | reg2;
				break;
			default:
				combined = (reg1 << 16) | reg2;
		}

		if (format === 'float32') {
			// Convert to float32
			const buffer = Buffer.allocUnsafe(4);
			buffer.writeUInt32BE(combined, 0);
			return buffer.readFloatBE(0);
		} else {
			// int32 - convert to signed
			return combined > 2147483647 ? combined - 4294967296 : combined;
		}
	}

	private parseBoolean(value: string): boolean {
		const lowerValue = value.toLowerCase().trim();
		return lowerValue === 'true' || lowerValue === '1' || lowerValue === 'on';
	}

	private getAddressLabel(address: number, addressLabels?: string): string | undefined {
		if (!addressLabels) return undefined;
		
		try {
			const labels = JSON.parse(addressLabels);
			return labels[address.toString()];
		} catch (error) {
			return undefined;
		}
	}
} 