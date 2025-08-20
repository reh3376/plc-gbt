/**
 * Advanced Tab - AI Task Orchestrator TypeScript Implementation
 *
 * @description Access advanced settings, debugging, and raw configuration
 * @compliance Strict TypeScript with OpenAPI Schema MCP validation
 * @features Performance settings, debug logging, raw JSON editor, advanced features
 */

'use client';

import {
  Bug,
  Code,
  Cog,
  Copy,
  Download,
  FileText,
  Monitor,
  Settings,
  Upload,
  Zap,
} from 'lucide-react';
import React, { useCallback, useState } from 'react';

import { type NodePropertySchema } from '@/api/zod-schemas';
import { cn } from '@/lib/utils/cn';

interface AdvancedTabProps {
  readonly schema: NodePropertySchema;
  readonly config: Record<string, unknown>;
  readonly onConfigChange: (key: string, value: unknown) => void;
  readonly onExport: () => void;
  readonly onImport: (config: string) => void;
}

export function AdvancedTab({
  schema,
  config,
  onConfigChange,
  onExport,
  onImport,
}: Readonly<AdvancedTabProps>): React.JSX.Element {
  const [activeSection, setActiveSection] = useState<'performance' | 'debug' | 'raw' | 'features'>(
    'performance'
  );
  const [rawConfigText, setRawConfigText] = useState(() => JSON.stringify(config, null, 2));
  const [isRawEditing, setIsRawEditing] = useState(false);

  // Handle raw configuration changes
  const handleRawConfigSave = useCallback(() => {
    try {
      const parsedConfig = JSON.parse(rawConfigText);

      // Apply all changes from parsed config
      Object.entries(parsedConfig).forEach(([key, value]) => {
        onConfigChange(key, value);
      });

      setIsRawEditing(false);
    } catch (error) {
      console.error('Invalid JSON configuration:', error);
      alert('Invalid JSON format. Please check your configuration and try again.');
    }
  }, [rawConfigText, onConfigChange]);

  // Handle configuration import
  const handleImportConfig = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = event => {
      const file = (event.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = e => {
          const content = e.target?.result as string;
          onImport(content);
        };
        reader.readAsText(file);
      }
    };
    input.click();
  }, [onImport]);

  return (
    <div className="p-4 space-y-6">
      {/* Section Navigation */}
      <div className="flex items-center gap-2 border-b border-[#404040] pb-4">
        {[
          { id: 'performance', label: 'Performance', icon: Monitor },
          { id: 'debug', label: 'Debug & Logging', icon: Bug },
          { id: 'raw', label: 'Raw Configuration', icon: Code },
          { id: 'features', label: 'Node Features', icon: Zap },
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

      {/* Performance Settings */}
      {activeSection === 'performance' && (
        <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
          <h3 className="text-lg font-medium text-white">Performance Optimization</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Polling Settings */}
            <div className="border border-[#404040] rounded-lg p-4">
              <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                <Settings className="w-4 h-4 text-blue-400" />
                Polling & Updates
              </h4>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Update Interval (ms)</label>
                  <input
                    type="number"
                    value={(config.updateInterval as number) || 1000}
                    onChange={e =>
                      onConfigChange('updateInterval', parseInt(e.target.value) || 1000)
                    }
                    min="100"
                    max="60000"
                    step="100"
                    className="w-full px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={(config.enableBatching as boolean) || false}
                      onChange={e => onConfigChange('enableBatching', e.target.checked)}
                      className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-white">Enable Batch Processing</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Memory Settings */}
            <div className="border border-[#404040] rounded-lg p-4">
              <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                <Monitor className="w-4 h-4 text-green-400" />
                Memory & Caching
              </h4>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Cache Size (entries)</label>
                  <input
                    type="number"
                    value={(config.cacheSize as number) || 100}
                    onChange={e => onConfigChange('cacheSize', parseInt(e.target.value) || 100)}
                    min="10"
                    max="10000"
                    className="w-full px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={(config.enablePersistence as boolean) || true}
                      onChange={e => onConfigChange('enablePersistence', e.target.checked)}
                      className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-white">Persist Data</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Debug & Logging */}
      {activeSection === 'debug' && (
        <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
          <h3 className="text-lg font-medium text-white">Debug & Logging Configuration</h3>

          <div className="border border-[#404040] rounded-lg p-4">
            <h4 className="font-medium text-white mb-3 flex items-center gap-2">
              <Bug className="w-4 h-4 text-orange-400" />
              Logging Settings
            </h4>

            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-300 mb-1">Log Level</label>
                <select
                  value={(config.logLevel as string) || 'info'}
                  onChange={e => onConfigChange('logLevel', e.target.value)}
                  className="w-full px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="error">Error</option>
                  <option value="warn">Warning</option>
                  <option value="info">Info</option>
                  <option value="debug">Debug</option>
                  <option value="trace">Trace</option>
                </select>
              </div>

              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={(config.enableDetailedLogging as boolean) || false}
                    onChange={e => onConfigChange('enableDetailedLogging', e.target.checked)}
                    className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-white">Enable Detailed Logging</span>
                </label>
              </div>

              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={(config.enablePerformanceMetrics as boolean) || false}
                    onChange={e => onConfigChange('enablePerformanceMetrics', e.target.checked)}
                    className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-white">Track Performance Metrics</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Raw Configuration Editor */}
      {activeSection === 'raw' && (
        <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-white">Raw Configuration Editor</h3>

            <div className="flex items-center gap-2">
              <button
                onClick={handleImportConfig}
                className="flex items-center gap-2 px-3 py-1 text-sm text-gray-400 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
              >
                <Upload className="w-4 h-4" />
                Import
              </button>

              <button
                onClick={onExport}
                className="flex items-center gap-2 px-3 py-1 text-sm text-gray-400 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
              >
                <Download className="w-4 h-4" />
                Export
              </button>

              <button
                onClick={() => {
                  navigator.clipboard.writeText(rawConfigText);
                }}
                className="flex items-center gap-2 px-3 py-1 text-sm text-gray-400 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
              >
                <Copy className="w-4 h-4" />
                Copy
              </button>
            </div>
          </div>

          <div className="border border-[#404040] rounded-lg overflow-hidden">
            <div className="flex items-center justify-between p-3 bg-[#252526] border-b border-[#404040]">
              <span className="text-sm font-medium text-gray-300">JSON Configuration</span>

              <div className="flex items-center gap-2">
                {isRawEditing && (
                  <>
                    <button
                      onClick={() => {
                        setRawConfigText(JSON.stringify(config, null, 2));
                        setIsRawEditing(false);
                      }}
                      className="px-3 py-1 text-xs text-gray-400 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
                    >
                      Cancel
                    </button>

                    <button
                      onClick={handleRawConfigSave}
                      className="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                    >
                      Apply Changes
                    </button>
                  </>
                )}

                <button
                  onClick={() => setIsRawEditing(!isRawEditing)}
                  className={cn(
                    'px-3 py-1 text-xs rounded transition-colors',
                    isRawEditing
                      ? 'bg-orange-600 hover:bg-orange-700 text-white'
                      : 'bg-[#3d3d3d] text-gray-400 hover:text-white'
                  )}
                >
                  {isRawEditing ? 'Exit Edit' : 'Edit JSON'}
                </button>
              </div>
            </div>

            <div className="p-4">
              {isRawEditing ? (
                <textarea
                  value={rawConfigText}
                  onChange={e => setRawConfigText(e.target.value)}
                  className="w-full h-64 bg-[#1e1e1e] border border-[#404040] rounded text-gray-300 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  placeholder="Enter JSON configuration..."
                />
              ) : (
                <pre className="text-gray-300 text-sm font-mono whitespace-pre-wrap max-h-64 overflow-y-auto">
                  {JSON.stringify(config, null, 2)}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Node-Specific Features */}
      {activeSection === 'features' && (
        <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
          <h3 className="text-lg font-medium text-white">Node-Specific Features</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Integration Settings */}
            <div className="border border-[#404040] rounded-lg p-4">
              <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                <Cog className="w-4 h-4 text-purple-400" />
                Integration Settings
              </h4>

              <div className="space-y-3">
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={(config.enableAutoReconnect as boolean) || false}
                      onChange={e => onConfigChange('enableAutoReconnect', e.target.checked)}
                      className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-white">Auto-Reconnect</span>
                  </label>
                </div>

                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={(config.enableErrorRecovery as boolean) || true}
                      onChange={e => onConfigChange('enableErrorRecovery', e.target.checked)}
                      className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-white">Error Recovery</span>
                  </label>
                </div>

                <div>
                  <label className="block text-sm text-gray-300 mb-1">Retry Attempts</label>
                  <input
                    type="number"
                    value={(config.retryAttempts as number) || 3}
                    onChange={e => onConfigChange('retryAttempts', parseInt(e.target.value) || 3)}
                    min="0"
                    max="10"
                    className="w-full px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Node-Specific Options */}
            <div className="border border-[#404040] rounded-lg p-4">
              <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4 text-yellow-400" />
                {schema.title} Features
              </h4>

              <div className="space-y-3">
                {schema.nodeType === 'pid-controller' && (
                  <>
                    <div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={(config.enableAntiWindup as boolean) || true}
                          onChange={e => onConfigChange('enableAntiWindup', e.target.checked)}
                          className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-white">Anti-Windup Protection</span>
                      </label>
                    </div>

                    <div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={(config.enableDerivativeFiltering as boolean) || false}
                          onChange={e =>
                            onConfigChange('enableDerivativeFiltering', e.target.checked)
                          }
                          className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-white">Derivative Filtering</span>
                      </label>
                    </div>
                  </>
                )}

                {(schema.nodeType === 'modbus-client' || schema.nodeType === 'opc-server') && (
                  <>
                    <div>
                      <label className="block text-sm text-gray-300 mb-1">
                        Connection Pool Size
                      </label>
                      <input
                        type="number"
                        value={(config.connectionPoolSize as number) || 5}
                        onChange={e =>
                          onConfigChange('connectionPoolSize', parseInt(e.target.value) || 5)
                        }
                        min="1"
                        max="50"
                        className="w-full px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={(config.enableKeepAlive as boolean) || true}
                          onChange={e => onConfigChange('enableKeepAlive', e.target.checked)}
                          className="w-4 h-4 rounded border-[#505050] bg-[#3d3d3d] text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-white">Keep-Alive Connections</span>
                      </label>
                    </div>
                  </>
                )}

                {/* Generic options for other node types */}
                {!['pid-controller', 'modbus-client', 'opc-server'].includes(schema.nodeType) && (
                  <div className="text-center text-gray-400 py-4">
                    <FileText className="w-8 h-8 mx-auto mb-2 text-gray-500" />
                    <p className="text-sm">No advanced features available for {schema.title}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
