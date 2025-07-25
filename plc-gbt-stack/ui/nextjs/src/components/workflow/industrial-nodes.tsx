'use client'

import React, { useState, memo } from 'react'
import { Handle, Position, NodeProps } from '@xyflow/react'
import {
  Zap,
  Activity,
  Gauge,
  Monitor,
  Database,
  AlertTriangle,
  Network,
  Server,
  Cpu,
  Wifi,
  Play,
  Square,
  Settings,
  RotateCw
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { IndustrialNodeData } from '@/lib/stores/workflow-store'

// Base Industrial Node Component
interface BaseNodeProps extends NodeProps {
  data: IndustrialNodeData
  icon: React.ComponentType<{ className?: string }>
  color: string
  handles?: {
    inputs?: number
    outputs?: number
  }
}

function BaseIndustrialNode({ 
  data, 
  selected, 
  icon: Icon,
  color,
  handles = { inputs: 1, outputs: 1 }
}: BaseNodeProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getStatusColor = (status: IndustrialNodeData['status']) => {
    switch (status) {
      case 'online': return 'bg-green-500'
      case 'offline': return 'bg-gray-500'
      case 'error': return 'bg-red-500'
      case 'configuring': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusText = (status: IndustrialNodeData['status']) => {
    switch (status) {
      case 'online': return 'Online'
      case 'offline': return 'Offline'
      case 'error': return 'Error'
      case 'configuring': return 'Config'
      default: return 'Unknown'
    }
  }

  return (
    <div 
      className={cn(
        'bg-[#2d2d2d] border rounded-lg shadow-lg min-w-[160px]',
        selected ? 'border-blue-500 ring-2 ring-blue-500/50' : 'border-[#404040]',
        'hover:border-[#505050] transition-colors'
      )}
    >
      {/* Input Handles */}
      {Array.from({ length: handles.inputs || 0 }, (_, i) => (
        <Handle
          key={`input-${i}`}
          type="target"
          position={Position.Left}
          id={`input-${i}`}
          style={{ 
            top: `${((i + 1) * 100) / (handles.inputs! + 1)}%`,
            background: color,
            border: '2px solid #fff'
          }}
          className="w-3 h-3"
        />
      ))}

      {/* Node Header */}
      <div 
        className={cn(
          'drag-handle flex items-center justify-between p-3 cursor-move',
          'border-b border-[#404040]'
        )}
        style={{ borderTopColor: color }}
      >
        <div className="flex items-center space-x-2">
          <Icon className="w-5 h-5 text-white" />
          <span className="text-sm font-medium text-white truncate">
            {data.label}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <div 
            className={cn(
              'w-2 h-2 rounded-full',
              getStatusColor(data.status)
            )}
            title={getStatusText(data.status)}
          />
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Node Content */}
      <div className="p-3">
        <div className="text-xs text-gray-400 mb-1">
          Status: <span className="text-white">{getStatusText(data.status)}</span>
        </div>
        
        {data.description && (
          <div className="text-xs text-gray-400 mb-2 line-clamp-2">
            {data.description}
          </div>
        )}

        {/* Expanded Configuration */}
        {isExpanded && (
          <div className="mt-3 pt-3 border-t border-[#404040]">
            <div className="space-y-2">
              <div className="text-xs">
                <span className="text-gray-400">Tags: </span>
                <span className="text-white">{data.tags.join(', ')}</span>
              </div>
              
              {data.lastUpdate && (
                <div className="text-xs">
                  <span className="text-gray-400">Updated: </span>
                  <span className="text-white">
                    {data.lastUpdate.toLocaleTimeString()}
                  </span>
                </div>
              )}

              {Object.keys(data.config).length > 0 && (
                <div className="text-xs">
                  <span className="text-gray-400">Config: </span>
                  <span className="text-white">
                    {Object.keys(data.config).length} parameters
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Output Handles */}
      {Array.from({ length: handles.outputs || 0 }, (_, i) => (
        <Handle
          key={`output-${i}`}
          type="source"
          position={Position.Right}
          id={`output-${i}`}
          style={{ 
            top: `${((i + 1) * 100) / (handles.outputs! + 1)}%`,
            background: color,
            border: '2px solid #fff'
          }}
          className="w-3 h-3"
        />
      ))}
    </div>
  )
}

// PLC Input Node
export const PLCInputNode = memo((props: NodeProps & { data: IndustrialNodeData }) => (
  <BaseIndustrialNode
    {...props}
    icon={Zap}
    color="#10B981"
    handles={{ inputs: 0, outputs: 2 }}
  />
))
PLCInputNode.displayName = 'PLCInputNode'

// PLC Output Node
export const PLCOutputNode = memo((props: NodeProps & { data: IndustrialNodeData }) => (
  <BaseIndustrialNode
    {...props}
    icon={Activity}
    color="#EF4444"
    handles={{ inputs: 2, outputs: 0 }}
  />
))
PLCOutputNode.displayName = 'PLCOutputNode'

// PID Controller Node
export const PIDControllerNode = memo((props: NodeProps & { data: IndustrialNodeData }) => {
  const [showTuning, setShowTuning] = useState(false)

  return (
    <div 
      className={cn(
        'bg-[#2d2d2d] border rounded-lg shadow-lg min-w-[180px]',
        props.selected ? 'border-blue-500 ring-2 ring-blue-500/50' : 'border-[#404040]'
      )}
    >
      {/* Input Handles */}
      <Handle
        type="target"
        position={Position.Left}
        id="setpoint"
        style={{ top: '25%', background: '#3B82F6', border: '2px solid #fff' }}
        className="w-3 h-3"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="process-variable"
        style={{ top: '75%', background: '#10B981', border: '2px solid #fff' }}
        className="w-3 h-3"
      />

      {/* Header */}
      <div className="drag-handle flex items-center justify-between p-3 border-b border-[#404040] bg-gradient-to-r from-purple-900/20 to-blue-900/20">
        <div className="flex items-center space-x-2">
          <RotateCw className="w-5 h-5 text-purple-400" />
          <span className="text-sm font-medium text-white">
            {props.data.label}
          </span>
        </div>
        <button
          onClick={() => setShowTuning(!showTuning)}
          className="text-purple-400 hover:text-purple-300"
        >
          <Gauge className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="p-3">
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="text-center">
            <div className="text-gray-400">P</div>
            <div className="text-white font-mono">
              {String(props.data.config.kp) || '1.0'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-gray-400">I</div>
            <div className="text-white font-mono">
              {String(props.data.config.ki) || '0.1'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-gray-400">D</div>
            <div className="text-white font-mono">
              {String(props.data.config.kd) || '0.01'}
            </div>
          </div>
        </div>

        {showTuning && (
          <div className="mt-3 pt-3 border-t border-[#404040]">
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-400">Setpoint:</span>
                <span className="text-white">{String(props.data.config.setpoint) || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Output:</span>
                <span className="text-white">{String(props.data.config.output) || '0'}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Error:</span>
                <span className="text-white">{String(props.data.config.error) || '0'}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="control-output"
        style={{ top: '50%', background: '#F59E0B', border: '2px solid #fff' }}
        className="w-3 h-3"
      />
    </div>
  )
})
PIDControllerNode.displayName = 'PIDControllerNode'

// HMI Display Node
export const HMIDisplayNode = memo((props: NodeProps & { data: IndustrialNodeData }) => (
  <BaseIndustrialNode
    {...props}
    icon={Monitor}
    color="#8B5CF6"
    handles={{ inputs: 3, outputs: 1 }}
  />
))
HMIDisplayNode.displayName = 'HMIDisplayNode'

// Data Logger Node
export const DataLoggerNode = memo((props: NodeProps & { data: IndustrialNodeData }) => (
  <BaseIndustrialNode
    {...props}
    icon={Database}
    color="#06B6D4"
    handles={{ inputs: 4, outputs: 1 }}
  />
))
DataLoggerNode.displayName = 'DataLoggerNode'

// Alarm Handler Node
export const AlarmHandlerNode = memo((props: NodeProps & { data: IndustrialNodeData }) => (
  <BaseIndustrialNode
    {...props}
    icon={AlertTriangle}
    color="#F59E0B"
    handles={{ inputs: 2, outputs: 2 }}
  />
))
AlarmHandlerNode.displayName = 'AlarmHandlerNode'

// Modbus Client Node
export const ModbusClientNode = memo((props: NodeProps & { data: IndustrialNodeData }) => (
  <BaseIndustrialNode
    {...props}
    icon={Network}
    color="#EC4899"
    handles={{ inputs: 1, outputs: 3 }}
  />
))
ModbusClientNode.displayName = 'ModbusClientNode'

// OPC Server Node
export const OPCServerNode = memo((props: NodeProps & { data: IndustrialNodeData }) => (
  <BaseIndustrialNode
    {...props}
    icon={Server}
    color="#84CC16"
    handles={{ inputs: 3, outputs: 1 }}
  />
))
OPCServerNode.displayName = 'OPCServerNode'

// Custom Logic Node
export const CustomLogicNode = memo((props: NodeProps & { data: IndustrialNodeData }) => {
  const [isEditing, setIsEditing] = useState(false)

  return (
    <div 
      className={cn(
        'bg-[#2d2d2d] border rounded-lg shadow-lg min-w-[200px]',
        props.selected ? 'border-blue-500 ring-2 ring-blue-500/50' : 'border-[#404040]'
      )}
    >
      {/* Input Handles */}
      <Handle
        type="target"
        position={Position.Left}
        id="input-1"
        style={{ top: '30%', background: '#10B981', border: '2px solid #fff' }}
        className="w-3 h-3"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="input-2"
        style={{ top: '70%', background: '#10B981', border: '2px solid #fff' }}
        className="w-3 h-3"
      />

      {/* Header */}
      <div className="drag-handle flex items-center justify-between p-3 border-b border-[#404040] bg-gradient-to-r from-orange-900/20 to-red-900/20">
        <div className="flex items-center space-x-2">
          <Cpu className="w-5 h-5 text-orange-400" />
          <span className="text-sm font-medium text-white">
            {props.data.label}
          </span>
        </div>
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="text-orange-400 hover:text-orange-300"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="p-3">
        <div className="text-xs text-gray-400 mb-2">
          Logic Function
        </div>
        
        {isEditing ? (
          <textarea
            className="w-full h-20 text-xs bg-[#1e1e1e] text-white border border-[#404040] rounded p-2 font-mono"
            placeholder="// Enter custom logic here..."
            value={String(props.data.config.logic) || ''}
            onChange={(e) => {
              // TODO: Update node config
              console.log('Logic updated:', e.target.value)
            }}
          />
        ) : (
          <div className="text-xs text-white font-mono bg-[#1e1e1e] p-2 rounded min-h-[60px] border border-[#404040]">
            {String(props.data.config.logic) || '// Click edit to add logic...'}
          </div>
        )}

        <div className="mt-2 flex justify-between text-xs">
          <span className="text-gray-400">
            Runtime: {String(props.data.config.runtime) || '0ms'}
          </span>
          <span className="text-gray-400">
            Cycles: {String(props.data.config.cycles) || '0'}
          </span>
        </div>
      </div>

      {/* Output Handles */}
      <Handle
        type="source"
        position={Position.Right}
        id="output-1"
        style={{ top: '30%', background: '#EF4444', border: '2px solid #fff' }}
        className="w-3 h-3"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="output-2"
        style={{ top: '70%', background: '#EF4444', border: '2px solid #fff' }}
        className="w-3 h-3"
      />
    </div>
  )
})
CustomLogicNode.displayName = 'CustomLogicNode'

// N8N Workflow Node
export const N8NWorkflowNode = memo((props: NodeProps & { data: IndustrialNodeData }) => {
  const [isConnected] = useState(false)

  return (
    <div 
      className={cn(
        'bg-[#2d2d2d] border rounded-lg shadow-lg min-w-[180px]',
        props.selected ? 'border-blue-500 ring-2 ring-blue-500/50' : 'border-[#404040]'
      )}
    >
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="trigger"
        style={{ top: '50%', background: '#8B5CF6', border: '2px solid #fff' }}
        className="w-3 h-3"
      />

      {/* Header */}
      <div className="drag-handle flex items-center justify-between p-3 border-b border-[#404040] bg-gradient-to-r from-purple-900/20 to-pink-900/20">
        <div className="flex items-center space-x-2">
          <Wifi className="w-5 h-5 text-purple-400" />
          <span className="text-sm font-medium text-white">
            {props.data.label}
          </span>
        </div>
        <div className={cn(
          'w-2 h-2 rounded-full',
          isConnected ? 'bg-green-500' : 'bg-gray-500'
        )} />
      </div>

      {/* Content */}
      <div className="p-3">
        <div className="text-xs space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-400">Workflow ID:</span>
            <span className="text-white font-mono text-xs">
              {String(props.data.config.workflowId) || 'N/A'}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-gray-400">Executions:</span>
            <span className="text-white">
              {String(props.data.config.executions) || '0'}
            </span>
          </div>

          <div className="flex justify-between">
            <span className="text-gray-400">Last Run:</span>
            <span className="text-white text-xs">
              {String(props.data.config.lastRun) || 'Never'}
            </span>
          </div>
        </div>

        <div className="mt-3 flex space-x-2">
          <button 
            className="flex-1 bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs flex items-center justify-center space-x-1"
            onClick={() => console.log('Start N8N workflow')}
          >
            <Play className="w-3 h-3" />
            <span>Start</span>
          </button>
          
          <button 
            className="flex-1 bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs flex items-center justify-center space-x-1"
            onClick={() => console.log('Stop N8N workflow')}
          >
            <Square className="w-3 h-3" />
            <span>Stop</span>
          </button>
        </div>
      </div>

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="result"
        style={{ top: '50%', background: '#8B5CF6', border: '2px solid #fff' }}
        className="w-3 h-3"
      />
    </div>
  )
})
N8NWorkflowNode.displayName = 'N8NWorkflowNode'

// Export all node types for React Flow
export const industrialNodeTypes = {
  'plc-input': PLCInputNode,
  'plc-output': PLCOutputNode,
  'pid-controller': PIDControllerNode,
  'hmi-display': HMIDisplayNode,
  'data-logger': DataLoggerNode,
  'alarm-handler': AlarmHandlerNode,
  'modbus-client': ModbusClientNode,
  'opc-server': OPCServerNode,
  'custom-logic': CustomLogicNode,
  'n8n-workflow': N8NWorkflowNode,
} 