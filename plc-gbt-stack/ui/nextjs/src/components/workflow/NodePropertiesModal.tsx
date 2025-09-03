import {
  IndustrialNodeType,
  NodePropertySchema,
  PropertyField,
  ValidationResult,
} from '@/api/zod-schemas';
// Removed unused import: useNodePropertiesApi
import { useWorkflowStore } from '@/lib/stores/workflow-store';
import { cn } from '@/lib/utils/cn';
import { useModalManager } from '@/lib/utils/modal-manager';
// Removed unused imports: useModalPersistence, Node
import {
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Loader,
  Maximize2,
  Minimize2,
  Move,
  RotateCcw,
  Save,
  X,
} from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ModalResizeComponents } from './components/ModalResizeHandles';
import { useEnhancedModal } from './hooks/useEnhancedModal';
import { NodeHelpIcon } from './NodeHelpIcon';
import { CypherBuilder } from './specialized/CypherBuilder';
import { SQLBuilder } from './specialized/SQLBuilder';
import { AdvancedTab } from './tabs/AdvancedTab';
import { ConnectionsTab } from './tabs/ConnectionsTab';
import { TemplatesTab } from './tabs/TemplatesTab';
import { ValidationTab } from './tabs/ValidationTab';

interface NodePropertiesModalProps {
  readonly nodeId?: string;
  readonly onClose: () => void;
}

// Define the modal tabs
const MODAL_TABS = [
  { id: 'properties', label: 'Properties', shortcut: undefined }, // Removed number shortcut
  { id: 'connections', label: 'Connections', shortcut: undefined },
  { id: 'validation', label: 'Validation', shortcut: undefined },
  { id: 'templates', label: 'Templates', shortcut: undefined },
  { id: 'advanced', label: 'Advanced', shortcut: undefined },
] as const;

type ModalTab = (typeof MODAL_TABS)[number]['id'];

export function NodePropertiesModal({ nodeId, onClose }: NodePropertiesModalProps) {
  const { nodes, selectedNodes, updateNodeData } = useWorkflowStore();
  const isMountedRef = useRef(true);

  // Get the selected node - ensure it's always a Node object
  const selectedNode = useMemo(() => {
    if (nodeId) {
      return nodes.find(node => node.id === nodeId);
    }
    // selectedNodes contains string IDs, need to find the actual Node object
    if (selectedNodes.length === 1) {
      return nodes.find(node => node.id === selectedNodes[0]);
    }
    return undefined;
  }, [nodes, selectedNodes, nodeId]);

  // Enhanced modal with drag/resize functionality
  const enhancedModal = useEnhancedModal({
    positioning: {
      initialPosition: { x: 100, y: 100 },
      initialSize: { width: 800, height: 600 },
      constraints: {
        minWidth: 320,
        minHeight: 400,
        maxWidth: 1600,
        maxHeight: 1200,
      },
      centerOnOpen: true,
    },
    dragging: {
      enabled: true,
      constrainToViewport: true,
      snapConfiguration: {
        enabled: true,
        threshold: 15,
        snapToEdges: true,
        snapToCenter: true,
        snapToGrid: false,
        gridSize: 20,
      },
    },
    resizing: {
      enabled: true,
      handles: ['se', 'e', 's', 'ne', 'n', 'nw', 'w', 'sw'],
      maintainAspectRatio: false,
      constrainToViewport: true,
    },
  });

  // State management
  const [schema, setSchema] = useState<NodePropertySchema | null>(null);
  const [config, setConfig] = useState<Record<string, unknown>>({});
  const [savedConfig, setSavedConfig] = useState<Record<string, unknown>>({});
  const [isDirty, setIsDirty] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationResults, setValidationResults] = useState<ValidationResult[]>([
    {
      isValid: false,
      field: '',
      severity: 'info',
      message: 'Validation: Awaiting Configuration',
      code: 'AWAITING_CONFIG',
    },
  ]);
  const [activeTab, setActiveTab] = useState<ModalTab>('properties');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  // Modal manager for z-index and focus
  const { zIndex, isTopModal, bringToFront } = useModalManager('node-properties', 'properties');

  // Modal persistence - Enhanced modal handles this internally
  // Future: Re-enable persistence through enhanced modal configuration

  // Load node schema and configuration - simplified and debugged
  useEffect(() => {
    console.log('🔍 NodePropertiesModal useEffect triggered', {
      selectedNode: selectedNode?.id,
      nodeType: selectedNode?.type,
      isLoading,
    });

    if (!selectedNode || typeof selectedNode !== 'object') {
      console.log('❌ No selected node or invalid node type');
      return;
    }

    if (isLoading) {
      console.log('⏳ Already loading, skipping...');
      return;
    }

    const loadNodeData = async () => {
      console.log('🚀 Starting loadNodeData for:', selectedNode.type);
      setIsLoading(true);

      try {
        // Get schema for node type - use direct import
        const nodeType = selectedNode.type as IndustrialNodeType;
        console.log('📋 Loading schema for node type:', nodeType);

        // Direct import to avoid API call issues
        const { nodeSchemaRegistry } = await import('@/lib/schemas/industrial-node-schemas');
        const nodeSchema = nodeSchemaRegistry.getSchema(nodeType);

        console.log('📄 Schema loaded:', nodeSchema ? 'SUCCESS' : 'FAILED');

        if (!nodeSchema) {
          throw new Error(`No schema found for node type: ${nodeType}`);
        }

        setSchema(nodeSchema);
        console.log('✅ Schema set in state');

        // Load saved configuration from node data
        const savedNodeConfig = selectedNode.data?.config || {};
        setConfig(savedNodeConfig);
        setSavedConfig(savedNodeConfig);
        setIsDirty(false);
        console.log('💾 Configuration loaded:', savedNodeConfig);

        // Auto-expand first group
        if (nodeSchema.groups.length > 0) {
          setExpandedGroups(new Set([nodeSchema.groups[0].id]));
          console.log('📂 Expanded first group:', nodeSchema.groups[0].id);
        }

        // Initial validation with default state
        setValidationResults([
          {
            isValid: false,
            field: '',
            severity: 'info',
            message: 'Validation: Awaiting Configuration',
            code: 'AWAITING_CONFIG',
          },
        ]);
        console.log('✅ Validation state initialized');
      } catch (error) {
        console.error('❌ Failed to load node data:', error);
        setValidationResults([
          {
            isValid: false,
            field: '',
            severity: 'error',
            message: 'Failed to load node configuration: ' + (error as Error).message,
            code: 'LOAD_ERROR',
          },
        ]);
      } finally {
        console.log('🏁 Setting isLoading to false');
        setIsLoading(false);
      }
    };

    loadNodeData();
  }, [selectedNode?.id, selectedNode?.type]); // Trigger when node changes

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Validation with debouncing - simplified for development
  const validateConfiguration = useCallback(
    async (newConfig: Record<string, unknown>) => {
      if (!selectedNode || !schema) return;

      setIsValidating(true);
      try {
        // Simple client-side validation for now
        const hasRequiredFields = schema.groups.every(group =>
          group.fields.every(field => {
            if (field.required) {
              const value = newConfig[field.key];
              return value !== undefined && value !== null && value !== '';
            }
            return true;
          })
        );

        if (hasRequiredFields) {
          setValidationResults([
            {
              isValid: true,
              field: '',
              severity: 'info',
              message: 'Configuration is valid',
              code: 'VALID_CONFIG',
            },
          ]);
        } else {
          setValidationResults([
            {
              isValid: false,
              field: '',
              severity: 'warning',
              message: 'Some required fields are missing',
              code: 'MISSING_REQUIRED',
            },
          ]);
        }
      } catch (error) {
        console.error('Validation failed:', error);
        setValidationResults([
          {
            isValid: false,
            field: '',
            severity: 'error',
            message: 'Validation failed: ' + (error as Error).message,
            code: 'VALIDATION_ERROR',
          },
        ]);
      } finally {
        setIsValidating(false);
      }
    },
    [selectedNode?.id, selectedNode?.type, schema?.nodeType] // Only stable dependencies
  );

  // Handle field changes
  const handleFieldChange = useCallback(
    (fieldKey: string, value: unknown) => {
      setConfig(prev => {
        const newConfig = { ...prev, [fieldKey]: value };
        setIsDirty(JSON.stringify(newConfig) !== JSON.stringify(savedConfig));
        return newConfig;
      });
    },
    [savedConfig]
  );

  // Template operations
  const handleApplyTemplate = useCallback(
    (templateId: string) => {
      // Find template by ID and apply its configuration
      const template = schema?.templates?.find(t => t.id === templateId);
      if (template) {
        setConfig(template.config);
        setIsDirty(true);
      }
    },
    [schema]
  );

  const handleSaveAsTemplate = useCallback(() => {
    console.log('Save as template:', config);
    // Template saving functionality - Future enhancement for Phase 3
    // Will integrate with template management system when available
    const templateData = {
      id: `template-${Date.now()}`,
      label: `Custom Template - ${selectedNode?.type}`,
      description: 'User-created template',
      category: 'user-defined',
      config,
      tags: ['custom', selectedNode?.type || 'unknown'],
    };
    console.log('Template prepared for saving:', templateData);
    // Integration point: Connect to template management API when implemented
  }, [config, selectedNode?.type]);

  const handleExportConfig = useCallback(() => {
    const dataStr = JSON.stringify(config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const exportFileDefaultName = `${selectedNode?.type || 'node'}-config.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }, [config, selectedNode]);

  const handleImportConfig = useCallback((configJson: string) => {
    try {
      const importedConfig = JSON.parse(configJson);
      setConfig(importedConfig);
      setIsDirty(true);
    } catch (error) {
      console.error('Failed to import configuration:', error);
    }
  }, []);

  const handleRevalidate = useCallback(() => {
    validateConfiguration(config);
  }, [config, validateConfiguration]);

  // Group toggle
  const handleGroupToggle = useCallback((groupId: string) => {
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

  // Enhanced modal drag/resize handlers are provided by useEnhancedModal hook
  // All dragging and resizing logic is now handled by the enhanced modal system

  // Save configuration
  const handleSave = useCallback(() => {
    if (!selectedNode || !isDirty || validationResults.some(r => r.severity === 'error')) {
      return;
    }

    // Save configuration to the node data
    updateNodeData(selectedNode.id, { config });
    setSavedConfig(config);
    setIsDirty(false);

    console.log('Configuration saved:', config);
  }, [selectedNode, isDirty, validationResults, config, updateNodeData]);

  // Reset configuration
  const handleReset = useCallback(() => {
    setConfig(savedConfig);
    setIsDirty(false);
    setValidationResults([
      {
        isValid: false,
        field: '',
        severity: 'info',
        message: 'Validation: Awaiting Configuration',
        code: 'AWAITING_CONFIG',
      },
    ]);
  }, [savedConfig]);

  // Keyboard shortcuts - defined after handleSave/handleReset
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isTopModal) return;

      // ESC to close
      if (e.key === 'Escape') {
        onClose();
      }

      // Ctrl/Cmd + S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (isDirty && !validationResults.some(r => r.severity === 'error')) {
          handleSave();
        }
      }

      // Ctrl/Cmd + R to reset
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        if (isDirty) {
          handleReset();
        }
      }
    },
    [isTopModal, onClose, isDirty, validationResults, handleSave, handleReset]
  );

  // Toggle maximize - using enhanced modal
  const handleMaximizeToggle = useCallback(() => {
    enhancedModal.toggleMaximize();
  }, [enhancedModal]);

  // Setup keyboard event listeners
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  // Save state changes - TEMPORARILY DISABLED to fix infinite loop
  // useEffect(() => {
  //   const timeoutId = setTimeout(() => {
  //     saveState({
  //       position: modalPosition,
  //       size: modalSize,
  //       isMaximized,
  //       activeTab,
  //       expandedGroups: Array.from(expandedGroups),
  //     });
  //   }, 1000); // Increased debounce to prevent rapid updates

  //   return () => clearTimeout(timeoutId);
  // }, [modalPosition, modalSize, isMaximized, activeTab, expandedGroups]); // Removed saveState dependency

  // Helper function to render specialized components
  const renderSpecializedComponent = useCallback(
    (field: PropertyField, fieldValue: unknown) => {
      if (field.ui?.specialComponent === 'SQLBuilder') {
        const defaultSQLValue = [
          { name: 'Query1', sql: 'SELECT NOW() as current_time', enabled: true },
        ];
        const sqlValue = (() => {
          if (Array.isArray(fieldValue)) return fieldValue;
          if (Array.isArray(field.defaultValue)) return field.defaultValue;
          return defaultSQLValue;
        })();

        const connectionStringValue = (() => {
          if (
            !(config.host && config.port && config.database && config.username && config.password)
          ) {
            return '';
          }
          const host = typeof config.host === 'string' ? config.host : 'localhost';
          const port = typeof config.port === 'number' ? String(config.port) : '5432';
          const database = typeof config.database === 'string' ? config.database : 'postgres';
          const username = typeof config.username === 'string' ? config.username : 'user';
          const password = typeof config.password === 'string' ? config.password : 'password';
          return `postgresql://${username}:${password}@${host}:${port}/${database}`;
        })();

        return (
          <SQLBuilder
            value={sqlValue}
            onChange={statements => handleFieldChange(field.key, statements)}
            connectionString={connectionStringValue}
            className="mt-2"
          />
        );
      }

      if (field.ui?.specialComponent === 'CypherBuilder') {
        const defaultCypherValue = [
          {
            name: 'Query1',
            cypher: 'MATCH (n) RETURN COUNT(n) as nodeCount',
            enabled: true,
          },
        ];
        const cypherValue = (() => {
          if (Array.isArray(fieldValue)) return fieldValue;
          if (Array.isArray(field.defaultValue)) return field.defaultValue;
          return defaultCypherValue;
        })();

        return (
          <CypherBuilder
            value={cypherValue}
            onChange={statements => handleFieldChange(field.key, statements)}
            connectionUri={config.uri as string}
            username={config.username as string}
            password={config.password as string}
            database={'neo4j'}
            className="mt-2"
          />
        );
      }

      return null;
    },
    [config, handleFieldChange]
  );

  // Render property field
  const renderPropertyField = (field: PropertyField) => {
    const fieldValue = config[field.key];
    const fieldError = validationResults.find(r => r.field === field.key);

    // Special handling for PLC Input node
    const isPlcInput = selectedNode?.type === 'plc-input';

    // Hide signal scaling fields for boolean data type
    if (
      isPlcInput &&
      field.key &&
      ['rawMin', 'rawMax', 'scaledMin', 'scaledMax', 'units'].includes(field.key) &&
      config.dataType === 'BOOLEAN'
    ) {
      return null;
    }

    return (
      <div key={field.key} className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
          {field.label}
          {field.required && <span className="text-red-400">*</span>}
          {field.description && (
            <span className="text-xs text-gray-500">({field.description})</span>
          )}
        </label>

        {/* Render different field types */}
        {field.type === 'text' && (
          <input
            type="text"
            value={(fieldValue as string) || ''}
            onChange={e => handleFieldChange(field.key, e.target.value)}
            className={cn(
              'w-full px-3 py-2 bg-[#1e1e1e] border rounded-lg text-white',
              'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
              fieldError?.severity === 'error'
                ? 'border-red-500'
                : 'border-[#404040] hover:border-[#505050]'
            )}
            placeholder={field.defaultValue as string}
          />
        )}

        {field.type === 'number' && (
          <input
            type="number"
            value={(() => {
              if (typeof fieldValue === 'number') return String(fieldValue);
              if (typeof field.defaultValue === 'number') return String(field.defaultValue);
              return '';
            })()}
            onChange={e => handleFieldChange(field.key, parseFloat(e.target.value))}
            min={field.constraints?.min}
            max={field.constraints?.max}
            step={field.constraints?.step}
            className={cn(
              'w-full px-3 py-2 bg-[#1e1e1e] border rounded-lg text-white',
              'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
              fieldError?.severity === 'error'
                ? 'border-red-500'
                : 'border-[#404040] hover:border-[#505050]'
            )}
          />
        )}

        {field.type === 'boolean' && (
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={(fieldValue as boolean) || false}
              onChange={e => handleFieldChange(field.key, e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-400">Enable</span>
          </label>
        )}

        {field.type === 'select' && (
          <select
            value={(() => {
              if (typeof fieldValue === 'string') return fieldValue;
              if (typeof field.defaultValue === 'string') return field.defaultValue;
              return '';
            })()}
            onChange={e => handleFieldChange(field.key, e.target.value)}
            className={cn(
              'w-full px-3 py-2 bg-[#1e1e1e] border rounded-lg text-white',
              'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
              fieldError?.severity === 'error'
                ? 'border-red-500'
                : 'border-[#404040] hover:border-[#505050]'
            )}
          >
            <option value="">Select...</option>
            {field.options?.map(option => (
              <option key={String(option.value)} value={String(option.value)}>
                {option.label}
              </option>
            ))}
          </select>
        )}

        {/* Specialized Components */}
        {renderSpecializedComponent(field, fieldValue)}

        {/* Field validation message */}
        {fieldError && (
          <div
            className={cn(
              'flex items-center gap-2 text-sm',
              fieldError.severity === 'error' && 'text-red-400',
              fieldError.severity === 'warning' && 'text-yellow-400',
              fieldError.severity === 'info' && 'text-blue-400'
            )}
          >
            <AlertCircle className="w-4 h-4" />
            <span>{fieldError.message}</span>
          </div>
        )}
      </div>
    );
  };

  if (!selectedNode || typeof selectedNode !== 'object') {
    return null;
  }

  // Calculate responsive positioning and sizing
  const calculateModalStyle = () => {
    if (enhancedModal.isMaximized) {
      return {
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
      };
    }

    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const modalWidth = Math.min(enhancedModal.size.width, viewportWidth - 20);
    const modalHeight = Math.min(enhancedModal.size.height, viewportHeight - 20);

    // For narrow screens, let CSS handle centering (don't set left/top)
    const isNarrowScreen = viewportWidth <= 768; // Tailwind 'md' breakpoint

    if (isNarrowScreen) {
      // Let CSS handle positioning on narrow screens
      return {
        width: `${modalWidth}px`,
        height: `${modalHeight}px`,
        minWidth: '320px',
        maxWidth: '95vw',
        minHeight: '400px',
        maxHeight: '95vh',
      };
    } else {
      // Use positioned coordinates from enhanced modal
      return {
        top: `${enhancedModal.position.y}px`,
        left: `${enhancedModal.position.x}px`,
        width: `${modalWidth}px`,
        height: `${modalHeight}px`,
        minWidth: '320px',
        maxWidth: '95vw',
        minHeight: '400px',
        maxHeight: '95vh',
      };
    }
  };

  const modalStyle = calculateModalStyle();

  return (
    <>
      {/* Modal Backdrop */}
      <button
        type="button"
        className="fixed inset-0 bg-black/50 backdrop-blur-sm border-0 p-0"
        style={{ zIndex }}
        onClick={e => {
          if (isTopModal) {
            if (isDirty) {
              const confirmClose = window.confirm(
                'You have unsaved changes. Are you sure you want to close?'
              );
              if (confirmClose) {
                onClose();
              }
            } else {
              onClose();
            }
          } else {
            bringToFront();
          }
        }}
        aria-label="Close modal"
      />

      {/* Modal Content */}
      <dialog
        open
        aria-labelledby="modal-title"
        className={cn(
          'fixed bg-[#2d2d2d] rounded-lg shadow-2xl border border-[#404040]',
          'flex flex-col overflow-hidden',
          'sm:rounded-lg', // Only rounded on small screens and up
          'max-w-[95vw] max-h-[95vh]', // Ensure it never exceeds viewport
          // Auto-center on mobile/narrow screens using CSS
          'max-md:left-1/2 max-md:top-1/2 max-md:-translate-x-1/2 max-md:-translate-y-1/2', // Center on mobile
          enhancedModal.isMaximized && 'rounded-none'
        )}
        style={{
          ...modalStyle,
          zIndex: zIndex + 1,
        }}
      >
        {/* Modal Header */}
        <header className="flex items-center justify-between p-4 border-b border-[#404040] bg-[#252526]">
          <div className="flex items-center gap-3 flex-1">
            <button
              type="button"
              className="flex items-center gap-2 cursor-move bg-transparent border-0 p-1 rounded hover:bg-[#3d3d3d]"
              onMouseDown={enhancedModal.handleDragStart}
              aria-label="Drag to move modal"
              title="Drag to move modal"
            >
              <Move className="w-4 h-4 text-gray-500" />
            </button>
            <h2 id="modal-title" className="text-lg font-semibold text-white">
              {schema?.title || 'Node Properties'}
            </h2>
            {selectedNode && <NodeHelpIcon nodeType={selectedNode.type as IndustrialNodeType} />}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleMaximizeToggle}
              className="p-1 hover:bg-[#3d3d3d] rounded transition-colors"
              title={enhancedModal.isMaximized ? 'Restore' : 'Maximize'}
            >
              {enhancedModal.isMaximized ? (
                <Minimize2 className="w-4 h-4 text-gray-400" />
              ) : (
                <Maximize2 className="w-4 h-4 text-gray-400" />
              )}
            </button>
            <button
              onClick={onClose}
              className="p-1 hover:bg-[#3d3d3d] rounded transition-colors"
              title="Close"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </header>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 px-4 py-2 border-b border-[#404040] bg-[#2d2d2d]">
          {MODAL_TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
                activeTab === tab.id
                  ? 'bg-[#094771] text-white shadow-md transform scale-[1.02]'
                  : 'text-gray-400 hover:text-white hover:bg-[#3d3d3d] hover:transform hover:scale-[1.01]'
              )}
            >
              {tab.label}
              {tab.shortcut && <span className="ml-2 text-xs opacity-60">({tab.shortcut})</span>}
            </button>
          ))}
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-auto" style={{ height: 'calc(100% - 140px)' }}>
          <div className="p-4">
            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center justify-center py-8">
                <Loader className="w-8 h-8 animate-spin text-blue-400" />
              </div>
            )}

            {/* Properties Tab */}
            {activeTab === 'properties' && schema && !isLoading && (
              <div className="space-y-4">
                {/* Property Groups */}
                {schema.groups.map(group => {
                  const isExpanded = expandedGroups.has(group.id);
                  const groupFields = group.fields;

                  // Filter out fields based on conditions
                  const visibleFields = groupFields.filter(field => {
                    if (selectedNode?.type === 'plc-input' && config.dataType === 'BOOLEAN') {
                      // Hide signal scaling fields for boolean data type
                      if (
                        field.key &&
                        ['rawMin', 'rawMax', 'scaledMin', 'scaledMax', 'units'].includes(field.key)
                      ) {
                        return false;
                      }
                    }
                    return true;
                  });

                  if (visibleFields.length === 0) return null;

                  return (
                    <div
                      key={group.id}
                      className="border border-[#404040] rounded-lg overflow-hidden transition-all duration-200 hover:border-[#505050]"
                    >
                      <button
                        onClick={() => handleGroupToggle(group.id)}
                        className={cn(
                          'w-full flex items-center justify-between p-3 transition-all duration-200',
                          'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
                          isExpanded ? 'bg-[#3d3d3d] hover:bg-[#454545]' : 'hover:bg-[#3d3d3d]'
                        )}
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white">{group.label}</span>
                          {group.description && (
                            <span className="text-sm text-gray-400">({group.description})</span>
                          )}
                        </div>
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        )}
                      </button>

                      {isExpanded && (
                        <div className="p-3 pt-0 space-y-4 animate-in slide-in-from-top-2 duration-200">
                          {visibleFields.map(field => renderPropertyField(field))}
                        </div>
                      )}
                    </div>
                  );
                })}

                {/* Global Validation Messages */}
                {validationResults
                  .filter(result => !result.field)
                  .map((result, index) => (
                    <div
                      key={`${result.code}-${result.severity}-${index}`}
                      className={cn(
                        'flex items-center gap-2 p-3 rounded-lg transition-all duration-200',
                        'animate-in slide-in-from-left-2',
                        result.severity === 'error' &&
                          'bg-red-900/20 border border-red-500/30 shadow-red-500/10 shadow-lg',
                        result.severity === 'warning' &&
                          'bg-yellow-900/20 border border-yellow-500/30 shadow-yellow-500/10 shadow-lg',
                        result.severity === 'info' &&
                          'bg-blue-900/20 border border-blue-500/30 shadow-blue-500/10 shadow-lg'
                      )}
                    >
                      <AlertCircle
                        className={cn(
                          'w-4 h-4',
                          result.severity === 'error' && 'text-red-400',
                          result.severity === 'warning' && 'text-yellow-400',
                          result.severity === 'info' && 'text-blue-400'
                        )}
                      />
                      <span className="text-sm">{result.message}</span>
                    </div>
                  ))}
              </div>
            )}

            {/* Connections Tab */}
            {activeTab === 'connections' && schema && (
              <ConnectionsTab
                schema={schema}
                config={config}
                nodeId={nodeId}
                onConfigChange={(key, value) => {
                  setConfig(prev => ({ ...prev, [key]: value }));
                  setIsDirty(true);
                }}
              />
            )}

            {/* Validation Tab */}
            {activeTab === 'validation' && (
              <ValidationTab
                schema={schema || ({} as NodePropertySchema)}
                config={config}
                validationResults={validationResults}
                isValidating={isValidating}
                onRevalidate={handleRevalidate}
              />
            )}

            {/* Templates Tab */}
            {activeTab === 'templates' && schema && (
              <TemplatesTab
                schema={schema}
                config={config}
                onApplyTemplate={handleApplyTemplate}
                onSaveAsTemplate={handleSaveAsTemplate}
              />
            )}

            {/* Advanced Tab */}
            {activeTab === 'advanced' && schema && (
              <AdvancedTab
                schema={schema}
                config={config}
                onConfigChange={(key, value) => {
                  setConfig(prev => ({ ...prev, [key]: value }));
                  setIsDirty(true);
                }}
                onExport={handleExportConfig}
                onImport={handleImportConfig}
              />
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between p-4 border-t border-[#404040] bg-[#252526]">
          <div className="flex items-center gap-2">
            {(isLoading || isValidating) && (
              <Loader className="w-4 h-4 animate-spin text-blue-400" />
            )}
            <span className="text-sm text-gray-400">
              {(() => {
                if (isValidating) return 'Validating configuration...';
                if (selectedNode) {
                  const nodeLabel =
                    (typeof selectedNode === 'object' && selectedNode.data?.label) || 'Node';
                  return `Editing: ${nodeLabel}`;
                }
                return 'No node selected';
              })()}
            </span>
            {validationResults.length > 0 && (
              <div className="flex items-center gap-1 text-xs">
                {validationResults.some(r => r.severity === 'error') && (
                  <span className="text-red-400">
                    ❌ {validationResults.filter(r => r.severity === 'error').length} errors
                  </span>
                )}
                {validationResults.some(r => r.severity === 'warning') && (
                  <span className="text-yellow-400">
                    ⚠️ {validationResults.filter(r => r.severity === 'warning').length} warnings
                  </span>
                )}
                {!validationResults.some(r => r.severity === 'error' || r.severity === 'warning') &&
                  validationResults.some(
                    r => r.message === 'Validation: Awaiting Configuration'
                  ) && <span className="text-gray-400">Awaiting Configuration</span>}
                {!validationResults.some(r => r.severity === 'error' || r.severity === 'warning') &&
                  !validationResults.some(
                    r => r.message === 'Validation: Awaiting Configuration'
                  ) &&
                  validationResults.length > 0 && <span className="text-green-400">✅ Valid</span>}
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              disabled={!isDirty}
              className={cn(
                'px-4 py-2 text-sm rounded transition-all duration-200 flex items-center gap-2',
                'focus:outline-none focus:ring-2 focus:ring-gray-500/50',
                isDirty
                  ? 'text-gray-300 hover:text-white hover:bg-[#3d3d3d] border border-transparent hover:border-gray-500/30'
                  : 'text-gray-500 cursor-not-allowed border border-transparent'
              )}
              title="Reset all changes to saved values"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>

            <button
              onClick={handleSave}
              disabled={
                !isDirty || isValidating || validationResults.some(r => r.severity === 'error')
              }
              className={cn(
                'px-4 py-2 text-sm rounded transition-all duration-200 flex items-center gap-2',
                'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
                isDirty && !isValidating && !validationResults.some(r => r.severity === 'error')
                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-blue-500/20 transform hover:scale-105'
                  : 'bg-gray-600 text-gray-400 cursor-not-allowed'
              )}
              title={(() => {
                if (isValidating) return 'Validating configuration...';
                if (validationResults.some(r => r.severity === 'error'))
                  return 'Fix validation errors before saving';
                return 'Save changes to node configuration';
              })()}
            >
              <Save className="w-4 h-4" />
              Save Changes
            </button>
          </div>
        </div>

        {/* Enhanced Modal Resize Handles */}
        {!enhancedModal.isMaximized && (
          <>
            <ModalResizeComponents.Handles
              handles={enhancedModal.resizeHandles}
              onResizeStart={enhancedModal.handleResizeStart}
              currentResizeHandle={enhancedModal.resizeState.resizeHandle}
              enabled={enhancedModal.configuration.resizing.enabled}
            />
            <ModalResizeComponents.Indicator
              isResizing={enhancedModal.resizeState.isResizing}
              currentSize={enhancedModal.size}
            />
          </>
        )}
      </dialog>

      {/* Global Resize Overlay */}
      <ModalResizeComponents.Overlay
        isResizing={enhancedModal.resizeState.isResizing}
        currentHandle={enhancedModal.resizeState.resizeHandle}
      />
    </>
  );
}
