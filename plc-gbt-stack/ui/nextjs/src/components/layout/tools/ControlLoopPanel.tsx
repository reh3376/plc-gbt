/**
 * Control Loop Panel - Configuration Interface
 * AI Task Orchestrator Generated - Control Loop Configuration Panel
 * 
 * Provides control loop configuration, parameter management, and control options
 * Designed to complement the main Control Loop Dashboard
 */

'use client'

import React, { useState } from 'react'
import { 
  Settings, 
  Play, 
  Pause, 
  Square, 
  Sliders, 
  Gauge, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  Zap
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'

interface ControlLoopConfig {
  id: string
  name: string
  type: 'PID' | 'PIDE' | 'Cascade' | 'Feedforward'
  status: 'running' | 'stopped' | 'error' | 'tuning'
  setpoint: number
  processVariable: number
  output: number
  parameters: {
    kp: number
    ki: number
    kd: number
  }
}

const mockControlLoops: ControlLoopConfig[] = [
  {
    id: 'temp-loop-01',
    name: 'Temperature Control',
    type: 'PID',
    status: 'running',
    setpoint: 75.0,
    processVariable: 74.8,
    output: 45.2,
    parameters: { kp: 1.2, ki: 0.8, kd: 0.1 }
  },
  {
    id: 'pressure-loop-02',
    name: 'Pressure Control',
    type: 'PIDE',
    status: 'running',
    setpoint: 150.0,
    processVariable: 149.5,
    output: 62.1,
    parameters: { kp: 2.1, ki: 1.2, kd: 0.05 }
  },
  {
    id: 'flow-loop-03',
    name: 'Flow Control',
    type: 'Cascade',
    status: 'stopped',
    setpoint: 500.0,
    processVariable: 0.0,
    output: 0.0,
    parameters: { kp: 0.8, ki: 0.5, kd: 0.2 }
  }
]

/**
 * Control Loop Configuration Panel
 * 
 * Provides configuration interface for control loops including:
 * - Loop selection and status
 * - Parameter tuning
 * - Setpoint adjustment
 * - Control operations
 */
export function ControlLoopPanel() {
  const [selectedLoop, setSelectedLoop] = useState<string>(mockControlLoops[0].id)
  const [isEditing, setIsEditing] = useState(false)
  
  const currentLoop = mockControlLoops.find(loop => loop.id === selectedLoop)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'stopped': return <Square className="w-4 h-4 text-gray-400" />
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-400" />
      case 'tuning': return <Clock className="w-4 h-4 text-yellow-400" />
      default: return <Square className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400'
      case 'stopped': return 'text-gray-400'
      case 'error': return 'text-red-400'
      case 'tuning': return 'text-yellow-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="h-full w-full flex flex-col bg-[#1e1e1e] text-[#cccccc] overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 bg-[#2d2d30] border-b border-[#3c3c3c] p-3">
        <div className="flex items-center space-x-2">
          <Sliders className="w-5 h-5 text-[#007acc]" />
          <h2 className="text-sm font-semibold">Control Loop Config</h2>
        </div>
      </div>

      {/* Control Loop List */}
      <div className="flex-shrink-0 border-b border-[#3c3c3c]">
        <div className="p-2">
          <h3 className="text-xs font-medium text-[#969696] mb-2">Active Loops</h3>
          <div className="space-y-1">
            {mockControlLoops.map((loop) => (
              <div
                key={loop.id}
                onClick={() => setSelectedLoop(loop.id)}
                className={cn(
                  'p-2 rounded cursor-pointer transition-colors text-xs',
                  selectedLoop === loop.id
                    ? 'bg-[#007acc] text-white'
                    : 'hover:bg-[#2d2d30] text-[#cccccc]'
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{loop.name}</span>
                  {getStatusIcon(loop.status)}
                </div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[#969696]">{loop.type}</span>
                  <span className={getStatusColor(loop.status)}>
                    {loop.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Configuration Panel */}
      {currentLoop && (
        <div className="flex-1 overflow-y-auto p-3 space-y-4">
          {/* Control Operations */}
          <div>
            <h3 className="text-xs font-medium text-[#969696] mb-2">Operations</h3>
            <div className="flex space-x-2">
              <button className="flex-1 flex items-center justify-center space-x-1 p-2 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors">
                <Play className="w-3 h-3" />
                <span>Start</span>
              </button>
              <button className="flex-1 flex items-center justify-center space-x-1 p-2 bg-yellow-600 hover:bg-yellow-700 text-white text-xs rounded transition-colors">
                <Pause className="w-3 h-3" />
                <span>Pause</span>
              </button>
              <button className="flex-1 flex items-center justify-center space-x-1 p-2 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors">
                <Square className="w-3 h-3" />
                <span>Stop</span>
              </button>
            </div>
          </div>

          {/* Current Values */}
          <div>
            <h3 className="text-xs font-medium text-[#969696] mb-2">Current Values</h3>
            <div className="grid grid-cols-1 gap-2">
              <div className="flex items-center justify-between p-2 bg-[#252526] rounded">
                <div className="flex items-center space-x-2">
                  <Target className="w-4 h-4 text-[#007acc]" />
                  <span className="text-xs">Setpoint</span>
                </div>
                <span className="text-xs font-mono">{currentLoop.setpoint.toFixed(1)}</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-[#252526] rounded">
                <div className="flex items-center space-x-2">
                  <Gauge className="w-4 h-4 text-green-400" />
                  <span className="text-xs">Process Variable</span>
                </div>
                <span className="text-xs font-mono">{currentLoop.processVariable.toFixed(1)}</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-[#252526] rounded">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 text-yellow-400" />
                  <span className="text-xs">Output</span>
                </div>
                <span className="text-xs font-mono">{currentLoop.output.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          {/* PID Parameters */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-medium text-[#969696]">PID Parameters</h3>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="text-xs text-[#007acc] hover:text-[#0099ff] transition-colors"
              >
                {isEditing ? 'Save' : 'Edit'}
              </button>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-[#252526] rounded">
                <span className="text-xs">Proportional (Kp)</span>
                {isEditing ? (
                  <input
                    type="number"
                    step="0.1"
                    defaultValue={currentLoop.parameters.kp}
                    className="w-16 px-1 py-0.5 text-xs bg-[#3c3c3c] border border-[#5c5c5c] rounded text-white"
                  />
                ) : (
                  <span className="text-xs font-mono">{currentLoop.parameters.kp}</span>
                )}
              </div>
              <div className="flex items-center justify-between p-2 bg-[#252526] rounded">
                <span className="text-xs">Integral (Ki)</span>
                {isEditing ? (
                  <input
                    type="number"
                    step="0.1"
                    defaultValue={currentLoop.parameters.ki}
                    className="w-16 px-1 py-0.5 text-xs bg-[#3c3c3c] border border-[#5c5c5c] rounded text-white"
                  />
                ) : (
                  <span className="text-xs font-mono">{currentLoop.parameters.ki}</span>
                )}
              </div>
              <div className="flex items-center justify-between p-2 bg-[#252526] rounded">
                <span className="text-xs">Derivative (Kd)</span>
                {isEditing ? (
                  <input
                    type="number"
                    step="0.01"
                    defaultValue={currentLoop.parameters.kd}
                    className="w-16 px-1 py-0.5 text-xs bg-[#3c3c3c] border border-[#5c5c5c] rounded text-white"
                  />
                ) : (
                  <span className="text-xs font-mono">{currentLoop.parameters.kd}</span>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <h3 className="text-xs font-medium text-[#969696] mb-2">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center justify-center space-x-2 p-2 bg-[#252526] hover:bg-[#2d2d30] text-white text-xs rounded transition-colors">
                <TrendingUp className="w-3 h-3" />
                <span>Auto Tune</span>
              </button>
              <button className="w-full flex items-center justify-center space-x-2 p-2 bg-[#252526] hover:bg-[#2d2d30] text-white text-xs rounded transition-colors">
                <Settings className="w-3 h-3" />
                <span>Advanced Settings</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ControlLoopPanel 