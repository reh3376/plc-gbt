/**
 * Enhanced Properties Panel - AI Task Orchestrator TypeScript Implementation
 *
 * @description Advanced workflow properties panel with dynamic forms and validation
 * @compliance Strict TypeScript - zero `any` types policy
 * @integration OpenAPI Schema MCP for validation
 * @features Dynamic forms, real-time validation, connection testing, templates
 */

'use client';

import {
  AlertCircle,
  CheckCircle,
  ChevronRight,
  Copy,
  Database,
  Loader,
  RotateCcw,
  Save,
  Settings,
  X,
  Zap,
} from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useState } from 'react';

import { nodeSchemaRegistry } from '@/lib/schemas/industrial-node-schemas';
import { useWorkflowStore } from '@/lib/stores/workflow-store';
import {
  ConnectionTestResult,
  EnhancedPropertiesPanelProps,
  NodePropertySchema,
  PropertiesTab,
  PropertyFieldChangeEvent,
  ValidationResult,
} from '@/lib/types/enhanced-properties-panel.types';
import { IndustrialNodeType } from '@/lib/types/workflow-management.types';
import { cn } from '@/lib/utils/cn';

// Tab configuration with icons and labels
const PANEL_TABS: ReadonlyArray<{
  readonly id: PropertiesTab;
  readonly label: string;
  readonly icon: React.ComponentType<{ className?: string }>;
  readonly description: string;
}> = [
  {
    id: 'properties',
    label: 'Properties',
    icon: Settings,
    description: 'Configure node parameters',
  },
  {
    id: 'connections',
    label: 'Connections',
    icon: Zap,
    description: 'Test connections and communication',
  },
  {
    id: 'validation',
    label: 'Validation',
    icon: CheckCircle,
    description: 'View validation results and errors',
  },
  {
    id: 'templates',
    label: 'Templates',
    icon: Copy,
    description: 'Apply or save configuration templates',
  },
  {
    id: 'advanced',
    label: 'Advanced',
    icon: Database,
    description: 'Advanced settings and raw configuration',
  },
] as const;

/**
 * Enhanced Properties Panel Component
 *
 * Provides comprehensive configuration interface for workflow nodes with:
 * - Dynamic form generation based on node type
 * - Real-time validation and error feedback
 * - Connection testing capabilities
 * - Template management
 * - Advanced configuration options
 */
export function EnhancedPropertiesPanel({
  className,
  width = 320,
  resizable = true,
  collapsible = true,
  defaultTab = 'properties',
  onConfigChange,
  onValidationChange,
  onConnectionTest,
}: Readonly<EnhancedPropertiesPanelProps>): React.JSX.Element {
  // Component state with strict typing
  const [isVisible, setIsVisible] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<PropertiesTab>(defaultTab);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(
    new Set(['basic', 'connection'])
  );
  const [editingConfig, setEditingConfig] = useState<Record<string, unknown>>({});
  const [validationResults, setValidationResults] = useState<ReadonlyArray<ValidationResult>>([]);
  const [connectionTestResults, setConnectionTestResults] = useState<
    Record<string, ConnectionTestResult>
  >({});
  const [isDirty, setIsDirty] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [lastSavedConfig, setLastSavedConfig] = useState<Record<string, unknown>>({});

  // Workflow store integration
  const { nodes, selectedNodes, updateNodeData } = useWorkflowStore();

  // Get selected node and its schema
  const selectedNode = useMemo(() => {
    return selectedNodes.length === 1 ? (nodes.find(n => n.id === selectedNodes[0]) ?? null) : null;
  }, [nodes, selectedNodes]);

  const nodeSchema = useMemo((): NodePropertySchema | null => {
    if (!selectedNode || !selectedNode.type) return null;
    return nodeSchemaRegistry.getSchema(selectedNode.type as IndustrialNodeType);
  }, [selectedNode]);

  // Load node configuration when selection changes
  useEffect(() => {
    if (selectedNode?.data.config) {
      const config = selectedNode.data.config;
      setEditingConfig(config);
      setLastSavedConfig(config);
      setIsDirty(false);
      setValidationResults([]);
    } else {
      setEditingConfig({});
      setLastSavedConfig({});
      setIsDirty(false);
      setValidationResults([]);
    }
  }, [selectedNode]);

  // Validate configuration when it changes
  const validateConfiguration = useCallback(async (): Promise<ReadonlyArray<ValidationResult>> => {
    if (!nodeSchema || !selectedNode) return [];

    const results: ValidationResult[] = [];

    // Validate each group
    for (const group of nodeSchema.groups) {
      for (const field of group.fields) {
        if (field.validation) {
          const value = editingConfig[field.key];
          const validationResult = field.validation(value, editingConfig, {
            nodeType: selectedNode.type as IndustrialNodeType,
            allNodes: [],
            connectedNodes: [],
            workflowConfig: {},
          });

          if (validationResult) {
            results.push(validationResult);
          }
        }
      }
    }

    setValidationResults(results);
    onValidationChange?.(results);
    return results;
  }, [nodeSchema, selectedNode, editingConfig, nodes, onValidationChange]);

  // Handle configuration field changes
  const handleFieldChange = useCallback(
    (event: PropertyFieldChangeEvent): void => {
      const { field, newValue } = event;

      setEditingConfig(prev => ({
        ...prev,
        [field.key]: newValue,
      }));

      setIsDirty(true);
      onConfigChange?.({ ...editingConfig, [field.key]: newValue });

      // Trigger validation after a short delay
      setTimeout(() => {
        validateConfiguration();
      }, 300);
    },
    [editingConfig, onConfigChange, validateConfiguration]
  );

  // Save configuration to node
  const handleSaveConfig = useCallback(async (): Promise<void> => {
    if (!selectedNode) return;

    setIsLoading(true);
    try {
      // Validate before saving
      const results = await validateConfiguration();
      const hasErrors = results.some(r => r.severity === 'error');

      if (hasErrors) {
        throw new Error('Cannot save configuration with validation errors');
      }

      // Update node data
      updateNodeData(selectedNode.id, {
        ...selectedNode.data,
        config: editingConfig,
      });

      setLastSavedConfig(editingConfig);
      setIsDirty(false);
    } catch (error) {
      console.error('Failed to save configuration:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedNode, editingConfig, validateConfiguration, updateNodeData]);

  // Reset configuration to last saved
  const handleResetConfig = useCallback((): void => {
    setEditingConfig(lastSavedConfig);
    setIsDirty(false);
    setValidationResults([]);
  }, [lastSavedConfig]);

  // Test connection
  const handleTestConnection = useCallback(
    async (testId: string): Promise<void> => {
      if (!nodeSchema) return;

      const connectionTest = nodeSchema.connectionTests?.find(test => test.id === testId);
      if (!connectionTest) return;

      setIsLoading(true);
      try {
        const result = await connectionTest.validator(editingConfig);
        setConnectionTestResults(prev => ({
          ...prev,
          [testId]: result,
        }));
        onConnectionTest?.(result);
      } catch (error) {
        const errorResult: ConnectionTestResult = {
          success: false,
          message: `Test failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date(),
        };
        setConnectionTestResults(prev => ({
          ...prev,
          [testId]: errorResult,
        }));
        onConnectionTest?.(errorResult);
      } finally {
        setIsLoading(false);
      }
    },
    [nodeSchema, editingConfig, onConnectionTest]
  );

  // Toggle group expansion
  const handleToggleGroup = useCallback((groupId: string): void => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupId)) {
        newSet.delete(groupId);
      } else {
        newSet.add(groupId);
      }
      return newSet;
    });
  }, []);

  // Tab icons mapping helper (for future use)
  // const getTabIcon = useCallback((tabId: PropertiesTab): React.ComponentType<{ className?: string }> => {
  //   const tab = PANEL_TABS.find(t => t.id === tabId);
  //   return tab?.icon ?? Settings;
  // }, []);

  // Export configuration
  const handleExportConfig = useCallback((): void => {
    const configJson = JSON.stringify(editingConfig, null, 2);
    const blob = new Blob([configJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedNode?.data.label || 'node'}-config.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [editingConfig, selectedNode]);

  // Validation indicator helper (moved outside component for reuse)
  // Will be extracted to separate file in next iteration

  // Don't render if no node is selected
  if (!selectedNode || !nodeSchema) {
    return (
      <div
        className={cn('bg-[#2d2d2d] border-l border-[#404040] flex flex-col h-full', className)}
        style={{ width }}
      >
        <div className="p-4 text-center text-[#969696]">
          <Settings className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>Select a node to configure properties</p>
        </div>
      </div>
    );
  }

  if (!isVisible && collapsible) {
    return (
      <div className={cn('border-l border-[#404040] bg-[#2d2d2d]', className)}>
        <button
          onClick={() => setIsVisible(true)}
          className="w-6 h-full flex items-center justify-center text-[#969696] hover:text-white hover:bg-[#404040] transition-colors"
          aria-label="Show properties panel"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div
      className={cn('bg-[#2d2d2d] border-l border-[#404040] flex flex-col h-full', className)}
      style={{ width }}
    >
      {/* Panel Header */}
      <div className="flex items-center justify-between p-3 border-b border-[#404040]">
        <div className="flex items-center space-x-2">
          <Settings className="w-4 h-4 text-[#969696]" />
          <h3 className="text-sm font-medium text-white">Properties</h3>
          {isDirty && (
            <div className="w-2 h-2 bg-yellow-400 rounded-full" title="Unsaved changes" />
          )}
        </div>

        <div className="flex items-center space-x-1">
          {/* Save/Reset buttons */}
          <button
            onClick={handleSaveConfig}
            disabled={!isDirty || isLoading}
            className="p-1 text-[#969696] hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Save configuration"
          >
            {isLoading ? <Loader className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          </button>

          <button
            onClick={handleResetConfig}
            disabled={!isDirty}
            className="p-1 text-[#969696] hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Reset to last saved"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {collapsible && (
            <button
              onClick={() => setIsVisible(false)}
              className="p-1 text-[#969696] hover:text-white transition-colors"
              title="Hide properties panel"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Node Info */}
      <div className="p-3 border-b border-[#404040] bg-[#252525]">
        <div className="text-xs text-[#969696] mb-1">Selected Node</div>
        <div className="text-sm text-white font-medium">{selectedNode.data.label}</div>
        <div className="text-xs text-[#969696]">{nodeSchema.title}</div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-[#404040] bg-[#252525]">
        {PANEL_TABS.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex-1 flex items-center justify-center p-2 text-xs transition-colors border-b-2',
                isActive
                  ? 'border-blue-500 text-white bg-[#2d2d2d]'
                  : 'border-transparent text-[#969696] hover:text-white'
              )}
              title={tab.description}
            >
              <Icon className="w-3 h-3" />
            </button>
          );
        })}
      </div>

      {/* Validation Summary */}
      {validationResults.length > 0 && (
        <div className="p-3 border-b border-[#404040] bg-[#252525]">
          <div className="flex items-center space-x-2 text-xs">
            <div className="text-[#969696]">Validation:</div>
            {validationResults.some(r => r.severity === 'error') && (
              <div className="flex items-center space-x-1 text-red-400">
                <AlertCircle className="w-3 h-3" />
                <span>{validationResults.filter(r => r.severity === 'error').length} errors</span>
              </div>
            )}
            {validationResults.some(r => r.severity === 'warning') && (
              <div className="flex items-center space-x-1 text-yellow-400">
                <AlertCircle className="w-3 h-3" />
                <span>
                  {validationResults.filter(r => r.severity === 'warning').length} warnings
                </span>
              </div>
            )}
            {validationResults.every(r => r.severity === 'info') &&
              validationResults.length > 0 && (
                <div className="flex items-center space-x-1 text-green-400">
                  <CheckCircle className="w-3 h-3" />
                  <span>Valid</span>
                </div>
              )}
          </div>
        </div>
      )}

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'properties' && (
          <PropertiesTabContent
            schema={nodeSchema}
            config={editingConfig}
            validationResults={validationResults}
            expandedGroups={expandedGroups}
            onFieldChange={handleFieldChange}
            onGroupToggle={handleToggleGroup}
          />
        )}

        {activeTab === 'connections' && (
          <ConnectionsTabContent
            schema={nodeSchema}
            config={editingConfig}
            testResults={connectionTestResults}
            isLoading={isLoading}
            onTestConnection={handleTestConnection}
          />
        )}

        {activeTab === 'validation' && (
          <ValidationTabContent
            validationResults={validationResults}
            onRevalidate={validateConfiguration}
          />
        )}

        {activeTab === 'templates' && (
          <TemplatesTabContent
            schema={nodeSchema}
            config={editingConfig}
            onApplyTemplate={template => {
              setEditingConfig(template.config);
              setIsDirty(true);
            }}
          />
        )}

        {activeTab === 'advanced' && (
          <AdvancedTabContent
            config={editingConfig}
            onConfigChange={setEditingConfig}
            onExport={handleExportConfig}
          />
        )}
      </div>
    </div>
  );
}

// Temporary placeholder components for tab content
// These will be implemented in the next step
function PropertiesTabContent({
  schema,
  config,
  validationResults,
  expandedGroups,
  onFieldChange,
  onGroupToggle,
}: Readonly<{
  schema: NodePropertySchema;
  config: Record<string, unknown>;
  validationResults: ReadonlyArray<ValidationResult>;
  expandedGroups: Set<string>;
  onFieldChange: (event: PropertyFieldChangeEvent) => void;
  onGroupToggle: (groupId: string) => void;
}>): React.JSX.Element {
  return (
    <div className="p-4">
      <div className="text-sm text-[#969696]">Properties form will be implemented next</div>
      <div className="text-xs text-[#969696] mt-2">
        Schema: {schema.title} v{schema.version}
      </div>
    </div>
  );
}

function ConnectionsTabContent({
  schema,
  config,
  testResults,
  isLoading,
  onTestConnection,
}: Readonly<{
  schema: NodePropertySchema;
  config: Record<string, unknown>;
  testResults: Record<string, ConnectionTestResult>;
  isLoading: boolean;
  onTestConnection: (testId: string) => Promise<void>;
}>): React.JSX.Element {
  return (
    <div className="p-4">
      <div className="text-sm text-[#969696]">
        Connection testing panel will be implemented next
      </div>
    </div>
  );
}

function ValidationTabContent({
  validationResults,
  onRevalidate,
}: Readonly<{
  validationResults: ReadonlyArray<ValidationResult>;
  onRevalidate: () => Promise<ReadonlyArray<ValidationResult>>;
}>): React.JSX.Element {
  return (
    <div className="p-4">
      <div className="text-sm text-[#969696]">
        Validation details panel will be implemented next
      </div>
    </div>
  );
}

function TemplatesTabContent({
  schema,
  config,
  onApplyTemplate,
}: Readonly<{
  schema: NodePropertySchema;
  config: Record<string, unknown>;
  onApplyTemplate: (template: { config: Record<string, unknown> }) => void;
}>): React.JSX.Element {
  return (
    <div className="p-4">
      <div className="text-sm text-[#969696]">
        Template management panel will be implemented next
      </div>
    </div>
  );
}

function AdvancedTabContent({
  config,
  onConfigChange,
  onExport,
}: Readonly<{
  config: Record<string, unknown>;
  onConfigChange: (config: Record<string, unknown>) => void;
  onExport: () => void;
}>): React.JSX.Element {
  return (
    <div className="p-4">
      <div className="text-sm text-[#969696]">
        Advanced configuration panel will be implemented next
      </div>
    </div>
  );
}

export default EnhancedPropertiesPanel;
