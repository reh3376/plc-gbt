/**
 * Connections Tab - AI Task Orchestrator TypeScript Implementation
 *
 * @description Configure node input/output connections and signal routing
 * @compliance Strict TypeScript with OpenAPI Schema MCP validation
 * @features Connection mapping, handle configuration, data type compatibility
 */

'use client';

import { ArrowDown, ArrowUp, Cable, CheckCircle, Info, Plus, Zap } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

import { type ConnectionTestResult, type NodePropertySchema } from '@/api/zod-schemas';
import { useNodePropertiesApi } from '@/lib/api/node-properties';
import { cn } from '@/lib/utils/cn';
import { RawConfigurationModal } from '../modals/RawConfigurationModal';

// Helper function to get handle border styling
const getHandleBorderStyle = (handle: ConnectionHandle): string => {
  if (handle.connected) {
    return 'border-green-500/30 bg-green-900/10';
  }
  if (handle.required) {
    return 'border-orange-500/30 bg-orange-900/10';
  }
  return 'border-[#404040] hover:border-[#505050]';
};

// Helper function to get handle status indicator color
const getHandleStatusColor = (handle: ConnectionHandle): string => {
  if (handle.connected) {
    return 'bg-green-400';
  }
  if (handle.required) {
    return 'bg-orange-400';
  }
  return 'bg-gray-400';
};

interface ConnectionHandle {
  readonly id: string;
  readonly type: 'input' | 'output';
  readonly dataType: 'boolean' | 'number' | 'string' | 'object' | 'any';
  readonly label: string;
  readonly description?: string;
  readonly required: boolean;
  readonly connected: boolean;
  readonly connectedTo?: string;
}

interface ConnectionsTabProps {
  readonly schema: NodePropertySchema;
  readonly config: Record<string, unknown>;
  readonly nodeId?: string;
  readonly onConfigChange: (key: string, value: unknown) => void;
}

export function ConnectionsTab({
  schema,
  config,
  nodeId,
  onConfigChange,
}: Readonly<ConnectionsTabProps>): React.JSX.Element {
  const [activeSection, setActiveSection] = useState<'handles' | 'mappings' | 'testing'>('handles');
  const [testResults, setTestResults] = useState<Record<string, ConnectionTestResult>>({});
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [customHandles, setCustomHandles] = useState<ConnectionHandle[]>([]);
  const [showHandleConfigModal, setShowHandleConfigModal] = useState(false);

  const nodePropertiesApi = useNodePropertiesApi();

  // Handle adding custom handles - open Raw Configuration modal
  const handleAddHandle = useCallback(() => {
    setShowHandleConfigModal(true);
  }, []);

  // Handle saving new handle configuration
  const handleSaveHandleConfig = useCallback((handleConfig: Record<string, unknown>) => {
    const newHandle: ConnectionHandle = {
      id: `custom-handle-${Date.now()}`,
      type: (handleConfig.type as 'input' | 'output') || 'output',
      dataType:
        (handleConfig.dataType as 'boolean' | 'number' | 'string' | 'object' | 'any') || 'any',
      label: (handleConfig.label as string) || 'Custom Handle',
      description: (handleConfig.description as string) || 'User-defined connection handle',
      required: (handleConfig.required as boolean) || false,
      connected: false,
    };
    setCustomHandles(prev => [...prev, newHandle]);
    setShowHandleConfigModal(false);
  }, []);

  // Mock connection handles based on node type
  const connectionHandles = useMemo((): ReadonlyArray<ConnectionHandle> => {
    const handles: ConnectionHandle[] = [];

    // Input handles based on node type
    switch (schema.nodeType) {
      case 'plc-input': {
        // PLC Input nodes do not have input handles - they are data sources
        // For analog inputs, provide multiple output handles with different scaling
        const inputType = config.inputType as string;

        if (inputType === 'Analog') {
          handles.push(
            {
              id: 'raw-value',
              type: 'output',
              dataType: 'number',
              label: 'Raw Value',
              description: 'Unscaled raw input value from PLC',
              required: false,
              connected: false,
            },
            {
              id: 'scaled-value',
              type: 'output',
              dataType: 'number',
              label: 'Scaled Value',
              description: 'Engineering units scaled value',
              required: false,
              connected: false,
            },
            {
              id: 'percentage',
              type: 'output',
              dataType: 'number',
              label: 'Percentage',
              description: 'Value as percentage (0-100%)',
              required: false,
              connected: false,
            }
          );
        } else {
          // Digital input - single boolean output
          handles.push({
            id: 'digital-value',
            type: 'output',
            dataType: 'boolean',
            label: 'Digital Value',
            description: 'Boolean state of digital input',
            required: false,
            connected: false,
          });
        }
        break;
      }

      case 'pid-controller':
        handles.push(
          {
            id: 'process-value',
            type: 'input',
            dataType: 'number',
            label: 'Process Value',
            description: 'Current process variable measurement',
            required: true,
            connected: false,
          },
          {
            id: 'setpoint',
            type: 'input',
            dataType: 'number',
            label: 'Setpoint',
            description: 'Target value for the process variable',
            required: true,
            connected: false,
          },
          {
            id: 'control-output',
            type: 'output',
            dataType: 'number',
            label: 'Control Output',
            description: 'PID controller output signal',
            required: false,
            connected: false,
          }
        );
        break;

      case 'modbus-client':
        handles.push(
          {
            id: 'trigger',
            type: 'input',
            dataType: 'boolean',
            label: 'Read Trigger',
            description: 'Trigger signal to read Modbus registers',
            required: false,
            connected: false,
          },
          {
            id: 'data-output',
            type: 'output',
            dataType: 'object',
            label: 'Register Data',
            description: 'Read register values',
            required: false,
            connected: false,
          }
        );
        break;

      case 'data-logger':
        handles.push(
          {
            id: 'data-input',
            type: 'input',
            dataType: 'any',
            label: 'Data Input',
            description: 'Data to be logged',
            required: true,
            connected: false,
          },
          {
            id: 'timestamp',
            type: 'input',
            dataType: 'string',
            label: 'Timestamp',
            description: 'Optional timestamp for data',
            required: false,
            connected: false,
          }
        );
        break;

      default:
        // Generic input/output for unknown node types
        handles.push(
          {
            id: 'generic-input',
            type: 'input',
            dataType: 'any',
            label: 'Input',
            description: 'Generic input connection',
            required: false,
            connected: false,
          },
          {
            id: 'generic-output',
            type: 'output',
            dataType: 'any',
            label: 'Output',
            description: 'Generic output connection',
            required: false,
            connected: false,
          }
        );
    }

    // Include custom handles
    return [...handles, ...customHandles];
  }, [schema.nodeType, config.inputType, customHandles]);

  // Test connection for nodes that support it
  const handleConnectionTest = useCallback(
    async (testId: string) => {
      if (!schema.connectionTests?.length) return;

      setIsTestingConnection(true);
      try {
        const response = await nodePropertiesApi.testConnection(schema.nodeType, {
          testId,
          configuration: config,
        });

        setTestResults(prev => ({
          ...prev,
          [testId]: response.result,
        }));
      } catch (error) {
        console.error('Connection test failed:', error);
        setTestResults(prev => ({
          ...prev,
          [testId]: {
            success: false,
            message: error instanceof Error ? error.message : 'Connection test failed',
            timestamp: new Date().toISOString(),
          },
        }));
      } finally {
        setIsTestingConnection(false);
      }
    },
    [schema.nodeType, schema.connectionTests, config, nodePropertiesApi]
  );

  return (
    <div className="p-4 space-y-6">
      {/* Section Navigation */}
      <div className="flex items-center gap-2 border-b border-[#404040] pb-4">
        {[
          { id: 'handles', label: 'Connection Handles', icon: Cable },
          { id: 'mappings', label: 'Signal Mappings', icon: ArrowDown },
          { id: 'testing', label: 'Connection Testing', icon: Zap },
        ].map(section => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id as typeof activeSection)}
            className={cn(
              'flex items-center gap-2 px-3 py-2 text-sm rounded transition-all duration-200',
              'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
              activeSection === section.id
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#3d3d3d]'
            )}
          >
            <section.icon className="w-4 h-4" />
            {section.label}
          </button>
        ))}
      </div>

      {/* Connection Handles Section */}
      {activeSection === 'handles' && (
        <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-white">Connection Handles</h3>
            <button
              className="flex items-center gap-2 px-3 py-1 text-sm text-blue-400 hover:text-blue-300 hover:bg-blue-600/10 rounded transition-colors"
              onClick={handleAddHandle}
            >
              <Plus className="w-4 h-4" />
              Add Handle
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Input Handles */}
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2">
                <ArrowDown className="w-4 h-4 text-green-400" />
                Input Handles
              </h4>
              {connectionHandles
                .filter(handle => handle.type === 'input')
                .map(handle => (
                  <div
                    key={handle.id}
                    className={cn(
                      'p-3 border rounded-lg transition-all duration-200',
                      getHandleBorderStyle(handle)
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={cn('w-3 h-3 rounded-full', getHandleStatusColor(handle))} />
                        <span className="font-medium text-white">{handle.label}</span>
                        {handle.required && <span className="text-red-400 text-xs">*</span>}
                      </div>
                      <span className="text-xs text-gray-400 bg-[#3d3d3d] px-2 py-1 rounded">
                        {handle.dataType}
                      </span>
                    </div>
                    {handle.description && (
                      <p className="text-xs text-gray-400 mt-1">{handle.description}</p>
                    )}
                    {handle.connected && handle.connectedTo && (
                      <div className="flex items-center gap-1 mt-2 text-xs text-green-400">
                        <CheckCircle className="w-3 h-3" />
                        Connected to: {handle.connectedTo}
                      </div>
                    )}
                  </div>
                ))}
            </div>

            {/* Output Handles */}
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2">
                <ArrowUp className="w-4 h-4 text-blue-400" />
                Output Handles
              </h4>
              {connectionHandles
                .filter(handle => handle.type === 'output')
                .map(handle => (
                  <div
                    key={handle.id}
                    className={cn(
                      'p-3 border rounded-lg transition-all duration-200',
                      handle.connected
                        ? 'border-blue-500/30 bg-blue-900/10'
                        : 'border-[#404040] hover:border-[#505050]'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div
                          className={cn(
                            'w-3 h-3 rounded-full',
                            handle.connected ? 'bg-blue-400' : 'bg-gray-400'
                          )}
                        />
                        <span className="font-medium text-white">{handle.label}</span>
                      </div>
                      <span className="text-xs text-gray-400 bg-[#3d3d3d] px-2 py-1 rounded">
                        {handle.dataType}
                      </span>
                    </div>
                    {handle.description && (
                      <p className="text-xs text-gray-400 mt-1">{handle.description}</p>
                    )}
                    {handle.connected && handle.connectedTo && (
                      <div className="flex items-center gap-1 mt-2 text-xs text-blue-400">
                        <CheckCircle className="w-3 h-3" />
                        Connected to: {handle.connectedTo}
                      </div>
                    )}
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* Signal Mappings Section */}
      {activeSection === 'mappings' && (
        <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
          {schema.nodeType === 'plc-input' ? (
            <div className="text-center text-gray-400 py-8">
              <Info className="w-12 h-12 mx-auto mb-4 text-gray-500" />
              <p className="text-lg font-medium mb-2">Signal Mapping Not Required</p>
              <p className="text-sm max-w-md mx-auto">
                PLC Input nodes are data sources and do not require signal mapping configuration.
                Configure the input properties in the Properties tab.
              </p>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-white">Signal Mappings</h3>
                <button
                  className="flex items-center gap-2 px-3 py-1 text-sm text-blue-400 hover:text-blue-300 hover:bg-blue-600/10 rounded transition-colors"
                  onClick={() => {
                    // Custom mapping functionality (placeholder for future implementation)
                    console.log('Add custom mapping');
                  }}
                >
                  <Plus className="w-4 h-4" />
                  Add Mapping
                </button>
              </div>

              <div className="text-center text-gray-400 py-8">
                <Cable className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                <p className="text-lg font-medium mb-2">Signal Mapping Configuration</p>
                <p className="text-sm max-w-md mx-auto">
                  Configure how data flows between connected nodes. Define transformations, data
                  type conversions, and signal routing rules.
                </p>
                <div className="text-xs text-gray-500 bg-[#1e1e1e] px-3 py-1 rounded-full mt-4 inline-block">
                  Advanced feature - Coming in Phase 3
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Connection Testing Section */}
      {activeSection === 'testing' && (
        <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
          <h3 className="text-lg font-medium text-white">Connection Testing</h3>

          {schema.connectionTests && schema.connectionTests.length > 0 ? (
            <div className="space-y-3">
              {schema.connectionTests.map(test => {
                const result = testResults[test.id];
                const isTestRunning = isTestingConnection;

                return (
                  <div
                    key={test.id}
                    className={cn(
                      'p-4 border rounded-lg transition-all duration-200',
                      result?.success
                        ? 'border-green-500/30 bg-green-900/10'
                        : result?.success === false
                        ? 'border-red-500/30 bg-red-900/10'
                        : 'border-[#404040] hover:border-[#505050]'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-white">{test.label}</h4>
                        <p className="text-sm text-gray-400">{test.description}</p>
                      </div>

                      <button
                        onClick={() => handleConnectionTest(test.id)}
                        disabled={isTestRunning}
                        className={cn(
                          'px-4 py-2 text-sm rounded transition-all duration-200 flex items-center gap-2',
                          'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
                          isTestRunning
                            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                        )}
                      >
                        <Zap className="w-4 h-4" />
                        {isTestRunning ? 'Testing...' : 'Test Connection'}
                      </button>
                    </div>

                    {/* Test Results */}
                    {result && (
                      <div className="mt-3 pt-3 border-t border-[#404040]">
                        <div className="flex items-center gap-2 mb-2">
                          <div
                            className={cn(
                              'w-2 h-2 rounded-full',
                              result.success ? 'bg-green-400' : 'bg-red-400'
                            )}
                          />
                          <span
                            className={cn(
                              'text-sm font-medium',
                              result.success ? 'text-green-400' : 'text-red-400'
                            )}
                          >
                            {result.success ? 'Connection Successful' : 'Connection Failed'}
                          </span>
                          {result.latencyMs && (
                            <span className="text-xs text-gray-400">({result.latencyMs}ms)</span>
                          )}
                        </div>

                        <p className="text-sm text-gray-300">{result.message}</p>

                        {result.details && Object.keys(result.details).length > 0 && (
                          <div className="mt-2 p-2 bg-[#1e1e1e] rounded text-xs">
                            <div className="text-gray-400 mb-1">Connection Details:</div>
                            <pre className="text-gray-300 whitespace-pre-wrap">
                              {JSON.stringify(result.details, null, 2)}
                            </pre>
                          </div>
                        )}

                        <div className="text-xs text-gray-500 mt-2">
                          Tested: {new Date(result.timestamp).toLocaleString()}
                        </div>
                      </div>
                    )}

                    {/* Required Fields Info */}
                    <div className="mt-3 pt-3 border-t border-[#404040]">
                      <div className="flex items-center gap-2 mb-2">
                        <Info className="w-4 h-4 text-blue-400" />
                        <span className="text-sm text-gray-300">Required Configuration:</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {test.requiredFields.map(field => {
                          const hasValue =
                            field in config && config[field] !== undefined && config[field] !== '';
                          return (
                            <span
                              key={field}
                              className={cn(
                                'text-xs px-2 py-1 rounded',
                                hasValue
                                  ? 'bg-green-600/20 text-green-400 border border-green-500/30'
                                  : 'bg-red-600/20 text-red-400 border border-red-500/30'
                              )}
                            >
                              {field}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center text-gray-400 py-8">
              <Zap className="w-12 h-12 mx-auto mb-4 text-gray-500" />
              <p className="text-lg font-medium mb-2">No Connection Tests Available</p>
              <p className="text-sm max-w-md mx-auto">
                This node type does not have built-in connection tests. Connection validation will
                be performed during workflow execution.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Handle Configuration Modal */}
      <RawConfigurationModal
        isOpen={showHandleConfigModal}
        config={{
          type: 'output',
          dataType: 'any',
          label: 'New Handle',
          description: 'Custom connection handle',
          required: false,
        }}
        title="Configure Connection Handle"
        onSave={handleSaveHandleConfig}
        onClose={() => setShowHandleConfigModal(false)}
      />
    </div>
  );
}
