import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeExecutionWithMetadata,
	NodeOperationError,
} from 'n8n-workflow';

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class PLCMemory implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'PLC Memory',
		name: 'plcMemory',
		group: ['industrial', 'database'],
		version: 1,
		subtitle: '={{$parameter["operation"]}}',
		description: 'PLC Memory Management System - Multi-database operations for industrial automation',
		defaults: {
			name: 'PLC Memory',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'plcMemoryCredentials',
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
						name: 'Status',
						value: 'status',
						description: 'Get PLC Memory system status and health metrics',
						action: 'Get system status',
					},
					{
						name: 'Query',
						value: 'query',
						description: 'Query memory system with intelligent routing',
						action: 'Query memory system',
					},
					{
						name: 'Ingest',
						value: 'ingest',
						description: 'Ingest codebase or files into memory system',
						action: 'Ingest data',
					},
					{
						name: 'Health Check',
						value: 'health',
						description: 'Run comprehensive health checks on all databases',
						action: 'Run health check',
					},
					{
						name: 'Backup',
						value: 'backup',
						description: 'Create backup of memory databases',
						action: 'Create backup',
					},
					{
						name: 'Optimize',
						value: 'optimize',
						description: 'Optimize memory tiers and performance',
						action: 'Optimize system',
					},
					{
						name: 'Clean',
						value: 'clean',
						description: 'Clean up unused data and optimize storage',
						action: 'Clean system',
					},
					{
						name: 'Version',
						value: 'version',
						description: 'Get system version information',
						action: 'Get version',
					},
				],
				default: 'status',
			},
			// Query operation parameters
			{
				displayName: 'Query Text',
				name: 'queryText',
				type: 'string',
				displayOptions: {
					show: {
						operation: ['query'],
					},
				},
				default: '',
				placeholder: 'e.g., authentication function',
				description: 'Text to search for in the memory system',
				required: true,
			},
			{
				displayName: 'Query Type',
				name: 'queryType',
				type: 'options',
				displayOptions: {
					show: {
						operation: ['query'],
					},
				},
				options: [
					{
						name: 'Code Function',
						value: 'code_function',
					},
					{
						name: 'Documentation',
						value: 'documentation',
					},
					{
						name: 'Configuration',
						value: 'configuration',
					},
					{
						name: 'Search Similarity',
						value: 'search_similarity',
					},
				],
				default: 'code_function',
				description: 'Type of data to search for',
			},
			{
				displayName: 'Query Strategy',
				name: 'queryStrategy',
				type: 'options',
				displayOptions: {
					show: {
						operation: ['query'],
					},
				},
				options: [
					{
						name: 'Speed',
						value: 'speed',
					},
					{
						name: 'Accuracy',
						value: 'accuracy',
					},
					{
						name: 'Cost',
						value: 'cost',
					},
					{
						name: 'Balanced',
						value: 'balanced',
					},
				],
				default: 'balanced',
				description: 'Query optimization strategy',
			},
			{
				displayName: 'Result Limit',
				name: 'queryLimit',
				type: 'number',
				displayOptions: {
					show: {
						operation: ['query'],
					},
				},
				default: 10,
				description: 'Maximum number of results to return',
			},
			// Ingest operation parameters
			{
				displayName: 'Ingest Path',
				name: 'ingestPath',
				type: 'string',
				displayOptions: {
					show: {
						operation: ['ingest'],
					},
				},
				default: '',
				placeholder: '/path/to/codebase or file.py',
				description: 'Path to ingest (file or directory)',
				required: true,
			},
			{
				displayName: 'Ingest Method',
				name: 'ingestMethod',
				type: 'options',
				displayOptions: {
					show: {
						operation: ['ingest'],
					},
				},
				options: [
					{
						name: 'Intelligent',
						value: 'intelligent',
					},
					{
						name: 'Legacy',
						value: 'legacy',
					},
				],
				default: 'intelligent',
				description: 'Ingestion method to use',
			},
			{
				displayName: 'Analysis Depth',
				name: 'ingestDepth',
				type: 'options',
				displayOptions: {
					show: {
						operation: ['ingest'],
					},
				},
				options: [
					{
						name: 'Surface',
						value: 'surface',
					},
					{
						name: 'Structural',
						value: 'structural',
					},
					{
						name: 'Semantic',
						value: 'semantic',
					},
					{
						name: 'Comprehensive',
						value: 'comprehensive',
					},
				],
				default: 'structural',
				description: 'Depth of analysis to perform',
			},
			{
				displayName: 'Dry Run',
				name: 'dryRun',
				type: 'boolean',
				displayOptions: {
					show: {
						operation: ['ingest', 'clean', 'optimize'],
					},
				},
				default: false,
				description: 'Preview operations without executing them',
			},
			// Backup operation parameters
			{
				displayName: 'Backup Database',
				name: 'backupDatabase',
				type: 'options',
				displayOptions: {
					show: {
						operation: ['backup'],
					},
				},
				options: [
					{
						name: 'All Databases',
						value: 'all',
					},
					{
						name: 'Redis',
						value: 'redis',
					},
					{
						name: 'Neo4j',
						value: 'neo4j',
					},
					{
						name: 'PostgreSQL',
						value: 'postgresql',
					},
					{
						name: 'Qdrant',
						value: 'qdrant',
					},
				],
				default: 'all',
				description: 'Database to backup',
			},
			// Output format
			{
				displayName: 'Output Format',
				name: 'outputFormat',
				type: 'options',
				options: [
					{
						name: 'Table',
						value: 'table',
					},
					{
						name: 'JSON',
						value: 'json',
					},
					{
						name: 'Detailed',
						value: 'detailed',
					},
				],
				default: 'json',
				description: 'Format for command output',
			},
			{
				displayName: 'Verbose Output',
				name: 'verbose',
				type: 'boolean',
				default: false,
				description: 'Enable verbose logging and detailed output',
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];

		for (let i = 0; i < items.length; i++) {
			const operation = this.getNodeParameter('operation', i) as string;
			const outputFormat = this.getNodeParameter('outputFormat', i) as string;
			const verbose = this.getNodeParameter('verbose', i) as boolean;

			try {
				let command = 'python3 ../scripts/ai/plc_memory_cli.py';
				let result: any;

				switch (operation) {
					case 'status':
						command += ' status';
						if (outputFormat !== 'table') {
							command += ` --format ${outputFormat}`;
						}
						if (verbose) {
							command += ' --detailed';
						}
						break;

					case 'query':
						const queryText = this.getNodeParameter('queryText', i) as string;
						const queryType = this.getNodeParameter('queryType', i) as string;
						const queryStrategy = this.getNodeParameter('queryStrategy', i) as string;
						const queryLimit = this.getNodeParameter('queryLimit', i) as number;

						command += ` query "${queryText}"`;
						command += ` --type ${queryType}`;
						command += ` --strategy ${queryStrategy}`;
						command += ` --limit ${queryLimit}`;
						command += ` --format ${outputFormat}`;
						break;

					case 'ingest':
						const ingestPath = this.getNodeParameter('ingestPath', i) as string;
						const ingestMethod = this.getNodeParameter('ingestMethod', i) as string;
						const ingestDepth = this.getNodeParameter('ingestDepth', i) as string;
						const dryRun = this.getNodeParameter('dryRun', i) as boolean;

						command += ` ingest "${ingestPath}"`;
						command += ` --method ${ingestMethod}`;
						command += ` --depth ${ingestDepth}`;
						if (dryRun) {
							command += ' --dry-run';
						}
						if (verbose) {
							command += ' --verbose';
						}
						break;

					case 'health':
						command += ' health';
						if (outputFormat !== 'table') {
							command += ` --format ${outputFormat}`;
						}
						break;

					case 'backup':
						const backupDatabase = this.getNodeParameter('backupDatabase', i) as string;
						command += ' backup';
						if (backupDatabase !== 'all') {
							command += ` --database ${backupDatabase}`;
						}
						if (verbose) {
							command += ' --verbose';
						}
						break;

					case 'optimize':
						const optimizeDryRun = this.getNodeParameter('dryRun', i) as boolean;
						command += ' optimize';
						if (optimizeDryRun) {
							command += ' --dry-run';
						}
						if (verbose) {
							command += ' --verbose';
						}
						break;

					case 'clean':
						const cleanDryRun = this.getNodeParameter('dryRun', i) as boolean;
						command += ' clean';
						if (cleanDryRun) {
							command += ' --dry-run';
						}
						if (verbose) {
							command += ' --verbose';
						}
						break;

					case 'version':
						command += ' version';
						break;

					default:
						throw new NodeOperationError(this.getNode(), `Unknown operation: ${operation}`);
				}

				// Execute the command
				const { stdout, stderr } = await execAsync(command, {
					cwd: '/app/n8n/nodes/plc_memory',
					timeout: 300000, // 5 minute timeout
				});

				// Process the result
				if (stderr && !stdout) {
					throw new NodeOperationError(this.getNode(), `PLC Memory CLI error: ${stderr}`);
				}

				// Parse JSON output if format is JSON
				if (outputFormat === 'json' && stdout.trim()) {
					try {
						result = JSON.parse(stdout);
					} catch (parseError) {
						// If JSON parsing fails, return raw stdout
						result = {
							operation,
							raw_output: stdout,
							stderr: stderr || null,
							format: 'raw'
						};
					}
				} else {
					result = {
						operation,
						output: stdout,
						stderr: stderr || null,
						format: outputFormat
					};
				}

				// Add execution metadata
				result.execution_metadata = {
					node_name: this.getNode().name,
					execution_time: new Date().toISOString(),
					command_executed: command,
					operation_type: operation,
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
					throw new NodeOperationError(this.getNode(), `PLC Memory operation failed: ${error.message}`);
				}
			}
		}

		return [returnData];
	}
} 