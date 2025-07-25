'use client'

import React, { useState, useEffect } from 'react'
import { 
  Settings,
  X,
  ChevronDown,
  ChevronRight,
  Trash,
  Copy,
  Save,
  Undo,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useWorkflowStore } from '@/lib/stores/workflow-store'

interface PropertyField {
  key: string
  label: string
  type: 'text' | 'number' | 'boolean' | 'select' | 'textarea' | 'json'
  options?: string[]
  description?: string
  validation?: (value: unknown) => string | null
}

const commonProperties: PropertyField[] = [
  {
    key: 'label',
    label: 'Label',
    type: 'text',
    description: 'Display name for the node'
  },
  {
    key: 'description',
    label: 'Description',
    type: 'textarea',
    description: 'Detailed description of the node function'
  },
  {
    key: 'tags',
    label: 'Tags',
    type: 'text',
    description: 'Comma-separated tags for categorization'
  },
]

const nodeTypeProperties: Record<string, PropertyField[]> = {
  'pid-controller': [
    {
      key: 'kp',
      label: 'Proportional Gain (Kp)',
      type: 'number',
      description: 'Proportional gain coefficient',
      validation: (value) => (typeof value === 'number' && value < 0) ? 'Must be positive' : null
    },
    {
      key: 'ki',
      label: 'Integral Gain (Ki)',
      type: 'number',
      description: 'Integral gain coefficient',
      validation: (value) => (typeof value === 'number' && value < 0) ? 'Must be positive' : null
    },
    {
      key: 'kd',
      label: 'Derivative Gain (Kd)',
      type: 'number',
      description: 'Derivative gain coefficient',
      validation: (value) => (typeof value === 'number' && value < 0) ? 'Must be positive' : null
    },
    {
      key: 'setpoint',
      label: 'Setpoint',
      type: 'number',
      description: 'Target value for control'
    },
    {
      key: 'outputMin',
      label: 'Minimum Output',
      type: 'number',
      description: 'Minimum control output value'
    },
    {
      key: 'outputMax',
      label: 'Maximum Output',
      type: 'number',
      description: 'Maximum control output value'
    },
  ],
  'plc-input': [
    {
      key: 'address',
      label: 'PLC Address',
      type: 'text',
      description: 'PLC memory address (e.g., %I0.0)'
    },
    {
      key: 'dataType',
      label: 'Data Type',
      type: 'select',
      options: ['BOOL', 'INT', 'REAL', 'DINT'],
      description: 'PLC data type'
    },
    {
      key: 'scanRate',
      label: 'Scan Rate (ms)',
      type: 'number',
      description: 'Data acquisition rate in milliseconds'
    },
  ],
  'plc-output': [
    {
      key: 'address',
      label: 'PLC Address',
      type: 'text',
      description: 'PLC memory address (e.g., %Q0.0)'
    },
    {
      key: 'dataType',
      label: 'Data Type',
      type: 'select',
      options: ['BOOL', 'INT', 'REAL', 'DINT'],
      description: 'PLC data type'
    },
    {
      key: 'safeValue',
      label: 'Safe Value',
      type: 'text',
      description: 'Safe value when connection is lost'
    },
  ],
  'modbus-client': [
    {
      key: 'host',
      label: 'Host Address',
      type: 'text',
      description: 'Modbus server IP address'
    },
    {
      key: 'port',
      label: 'Port',
      type: 'number',
      description: 'Modbus server port (usually 502)'
    },
    {
      key: 'unitId',
      label: 'Unit ID',
      type: 'number',
      description: 'Modbus slave unit identifier'
    },
    {
      key: 'timeout',
      label: 'Timeout (ms)',
      type: 'number',
      description: 'Connection timeout in milliseconds'
    },
  ],
  'custom-logic': [
    {
      key: 'logic',
      label: 'Logic Code',
      type: 'textarea',
      description: 'Custom logic implementation'
    },
    {
      key: 'language',
      label: 'Language',
      type: 'select',
      options: ['JavaScript', 'Python', 'Structured Text'],
      description: 'Programming language for logic'
    },
  ],
  'n8n-workflow': [
    {
      key: 'workflowId',
      label: 'N8N Workflow ID',
      type: 'text',
      description: 'Unique N8N workflow identifier'
    },
    {
      key: 'apiUrl',
      label: 'N8N API URL',
      type: 'text',
      description: 'N8N instance API endpoint'
    },
    {
      key: 'apiKey',
      label: 'API Key',
      type: 'text',
      description: 'N8N API authentication key'
    },
  ],
}

export function WorkflowPropertiesPanel() {
  const [isVisible, setIsVisible] = useState(true)
  const [activeTab, setActiveTab] = useState<'properties' | 'config' | 'status'>('properties')
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['basic']))
  const [editingConfig, setEditingConfig] = useState<Record<string, unknown>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})

  const {
    nodes,
    edges,
    selectedNodes,
    selectedEdges,
    updateNodeData,
    deleteNode,
    duplicateNode,
  } = useWorkflowStore()

  const selectedNode = selectedNodes.length === 1 ? nodes.find(n => n.id === selectedNodes[0]) : null
  const selectedEdge = selectedEdges.length === 1 ? edges.find(e => e.id === selectedEdges[0]) : null

  useEffect(() => {
    if (selectedNode) {
      setEditingConfig(selectedNode.data.config || {})
      setErrors({})
    }
  }, [selectedNode])

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const validateField = (field: PropertyField, value: unknown): string | null => {
    if (field.validation) {
      return field.validation(value)
    }
    return null
  }

  const handleConfigChange = (key: string, value: unknown, field?: PropertyField) => {
    const newConfig = { ...editingConfig, [key]: value }
    setEditingConfig(newConfig)

    // Validate field
    if (field) {
      const error = validateField(field, value)
      setErrors(prev => ({
        ...prev,
        [key]: error || ''
      }))
    }
  }

  const handleSaveConfig = () => {
    if (!selectedNode) return

    // Check for validation errors
    const hasErrors = Object.values(errors).some(error => error !== '')
    if (hasErrors) return

    updateNodeData(selectedNode.id, {
      config: editingConfig,
      lastUpdate: new Date()
    })
  }

  const handleResetConfig = () => {
    if (selectedNode) {
      setEditingConfig(selectedNode.data.config || {})
      setErrors({})
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'offline': return <AlertCircle className="w-4 h-4 text-gray-500" />
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />
      case 'configuring': return <Clock className="w-4 h-4 text-yellow-500" />
      default: return <AlertCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const renderPropertyField = (field: PropertyField, value: unknown) => {
    const error = errors[field.key]
    const fieldId = `field-${field.key}-${selectedNode?.id || 'unknown'}`

    switch (field.type) {
      case 'text':
        return (
          <input
            id={fieldId}
            name={field.key}
            type="text"
            value={String(value) || ''}
            onChange={(e) => handleConfigChange(field.key, e.target.value, field)}
            className={cn(
              'w-full max-w-full px-3 py-2 bg-[#1e1e1e] border rounded text-white text-sm',
              'min-w-0 box-border',
              error ? 'border-red-500' : 'border-[#404040]'
            )}
            placeholder={`Enter ${field.label.toLowerCase()}`}
            aria-describedby={error ? `${fieldId}-error` : undefined}
          />
        )

      case 'number':
        return (
          <input
            id={fieldId}
            name={field.key}
            type="number"
            value={String(value) || ''}
            onChange={(e) => handleConfigChange(field.key, parseFloat(e.target.value) || 0, field)}
            className={cn(
              'w-full max-w-full px-3 py-2 bg-[#1e1e1e] border rounded text-white text-sm',
              'min-w-0 box-border',
              error ? 'border-red-500' : 'border-[#404040]'
            )}
            placeholder={`Enter ${field.label.toLowerCase()}`}
            aria-describedby={error ? `${fieldId}-error` : undefined}
          />
        )

      case 'boolean':
        return (
          <label htmlFor={fieldId} className="flex items-center space-x-2">
            <input
              id={fieldId}
              name={field.key}
              type="checkbox"
              checked={Boolean(value) || false}
              onChange={(e) => handleConfigChange(field.key, e.target.checked, field)}
              className="w-4 h-4 text-blue-600 bg-[#1e1e1e] border-[#404040] rounded"
            />
            <span className="text-sm text-gray-300">Enabled</span>
          </label>
        )

      case 'select':
        return (
          <select
            id={fieldId}
            name={field.key}
            value={String(value) || ''}
            onChange={(e) => handleConfigChange(field.key, e.target.value, field)}
            className={cn(
              'w-full max-w-full px-3 py-2 bg-[#1e1e1e] border rounded text-white text-sm',
              'min-w-0 box-border',
              error ? 'border-red-500' : 'border-[#404040]'
            )}
            aria-describedby={error ? `${fieldId}-error` : undefined}
          >
            <option value="">Select {field.label.toLowerCase()}</option>
            {field.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )

      case 'textarea':
        return (
          <textarea
            id={fieldId}
            name={field.key}
            value={String(value) || ''}
            onChange={(e) => handleConfigChange(field.key, e.target.value, field)}
            rows={4}
            className={cn(
              'w-full max-w-full px-3 py-2 bg-[#1e1e1e] border rounded text-white text-sm font-mono',
              'min-w-0 box-border resize-y',
              error ? 'border-red-500' : 'border-[#404040]'
            )}
            placeholder={`Enter ${field.label.toLowerCase()}`}
            aria-describedby={error ? `${fieldId}-error` : undefined}
          />
        )

      default:
        return null
    }
  }

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="absolute top-4 right-4 p-2 bg-[#2d2d2d] border border-[#404040] rounded text-white hover:bg-[#3d3d3d]"
      >
        <Settings className="w-4 h-4" />
      </button>
    )
  }

  if (!selectedNode && !selectedEdge) {
    return (
      <div className="w-80 bg-[#2d2d2d] border-l border-[#404040] flex flex-col">
        <div className="flex items-center justify-between p-3 border-b border-[#404040]">
          <span className="text-sm font-medium text-white">Properties</span>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <Settings className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-sm">
              Select a node or edge to view its properties
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-80 bg-[#2d2d2d] border-l border-[#404040] flex flex-col h-full max-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-[#404040] flex-shrink-0">
        <span className="text-sm font-medium text-white">
          {selectedNode ? 'Node Properties' : 'Edge Properties'}
        </span>
        <div className="flex items-center space-x-1">
          {selectedNode && (
            <>
              <button
                onClick={() => duplicateNode(selectedNode.id)}
                className="p-1 text-gray-400 hover:text-white"
                title="Duplicate Node"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                onClick={() => deleteNode(selectedNode.id)}
                className="p-1 text-gray-400 hover:text-red-400"
                title="Delete Node"
              >
                <Trash className="w-4 h-4" />
              </button>
            </>
          )}
          <button
            onClick={() => setIsVisible(false)}
            className="p-1 text-gray-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[#404040] flex-shrink-0">
        {['properties', 'config', 'status'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as 'properties' | 'config' | 'status')}
            className={cn(
              'flex-1 px-3 py-2 text-xs font-medium capitalize transition-colors',
              activeTab === tab
                ? 'text-blue-400 border-b border-blue-400'
                : 'text-gray-400 hover:text-white'
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden min-h-0">
        {activeTab === 'properties' && selectedNode && (
          <div className="p-3 space-y-4 max-w-full">
            {/* Basic Properties */}
            <div>
              <button
                onClick={() => toggleSection('basic')}
                className="flex items-center w-full text-left mb-2"
              >
                {expandedSections.has('basic') ? (
                  <ChevronDown className="w-4 h-4 mr-1 text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 mr-1 text-gray-400" />
                )}
                <span className="text-sm font-medium text-white">Basic Properties</span>
              </button>
              
              {expandedSections.has('basic') && (
                <div className="space-y-3 ml-5">
                  {commonProperties.map((field) => (
                    <div key={field.key}>
                      <label htmlFor={`field-${field.key}-${selectedNode?.id || 'unknown'}`} className="block text-xs text-gray-400 mb-1">
                        {field.label}
                      </label>
                      {renderPropertyField(field, selectedNode.data[field.key as keyof typeof selectedNode.data])}
                      {field.description && (
                        <p className="text-xs text-gray-500 mt-1">{field.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Node Type Specific Properties */}
            {nodeTypeProperties[selectedNode.type!] && (
              <div>
                <button
                  onClick={() => toggleSection('specific')}
                  className="flex items-center w-full text-left mb-2"
                >
                  {expandedSections.has('specific') ? (
                    <ChevronDown className="w-4 h-4 mr-1 text-gray-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 mr-1 text-gray-400" />
                  )}
                  <span className="text-sm font-medium text-white">
                    {selectedNode.type?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())} Settings
                  </span>
                </button>
                
                {expandedSections.has('specific') && (
                  <div className="space-y-3 ml-5">
                    {nodeTypeProperties[selectedNode.type!].map((field) => (
                      <div key={field.key}>
                        <label htmlFor={`field-${field.key}-${selectedNode?.id || 'unknown'}`} className="block text-xs text-gray-400 mb-1">
                          {field.label}
                        </label>
                        {renderPropertyField(field, editingConfig[field.key])}
                        {errors[field.key] && (
                          <p id={`${field.key}-error`} className="text-xs text-red-400 mt-1">{errors[field.key]}</p>
                        )}
                        {field.description && !errors[field.key] && (
                          <p className="text-xs text-gray-500 mt-1">{field.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'config' && selectedNode && (
          <div className="p-3">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium text-white">Configuration</span>
              <div className="flex space-x-2">
                <button
                  onClick={handleResetConfig}
                  className="px-2 py-1 text-xs bg-gray-600 hover:bg-gray-700 text-white rounded"
                >
                  <Undo className="w-3 h-3" />
                </button>
                <button
                  onClick={handleSaveConfig}
                  className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded"
                  disabled={Object.values(errors).some(error => error !== '')}
                >
                  <Save className="w-3 h-3" />
                </button>
              </div>
            </div>

            <textarea
              id="config-editor"
              name="config"
              value={JSON.stringify(editingConfig, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value)
                  setEditingConfig(parsed)
                  setErrors({})
                } catch {
                  setErrors({ json: 'Invalid JSON format' })
                }
              }}
              className="w-full max-w-full h-64 px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-white text-xs font-mono min-w-0 box-border resize-y"
              aria-label="Configuration JSON editor"
              aria-describedby={errors.json ? "config-error" : undefined}
            />
            
            {errors.json && (
              <p id="config-error" className="text-xs text-red-400 mt-2">{errors.json}</p>
            )}
          </div>
        )}

        {activeTab === 'status' && selectedNode && (
          <div className="p-3 space-y-4">
            <div className="flex items-center space-x-3">
              {getStatusIcon(selectedNode.data.status)}
              <div>
                <div className="text-sm font-medium text-white capitalize">
                  {selectedNode.data.status}
                </div>
                <div className="text-xs text-gray-400">
                  Current node status
                </div>
              </div>
            </div>

            {selectedNode.data.lastUpdate && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Last Updated</div>
                <div className="text-sm text-white">
                  {selectedNode.data.lastUpdate.toLocaleString()}
                </div>
              </div>
            )}

            <div>
              <div className="text-xs text-gray-400 mb-1">Node ID</div>
              <div className="text-sm text-white font-mono">{selectedNode.id}</div>
            </div>

            <div>
              <div className="text-xs text-gray-400 mb-1">Node Type</div>
              <div className="text-sm text-white">{selectedNode.type}</div>
            </div>

            <div>
              <div className="text-xs text-gray-400 mb-1">Position</div>
              <div className="text-sm text-white">
                x: {Math.round(selectedNode.position.x)}, y: {Math.round(selectedNode.position.y)}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 