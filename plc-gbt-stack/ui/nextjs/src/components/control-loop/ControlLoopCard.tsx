/**
 * Control Loop Card Component - Phase 31.7
 * AI Task Orchestrator Generated - Individual Loop Display Card
 * 
 * Displays individual control loop information in a compact card:
 * - Status indicators and badges
 * - Real-time process values (SP, PV, CV)
 * - Performance metrics and alarms
 * - Quick action buttons
 */

'use client'

import React from 'react'
import { 
  Settings, 
  TrendingUp, 
  AlertTriangle, 
  Play, 
  Pause, 
  RotateCcw,
  Eye,
  Edit,
  Activity
} from 'lucide-react'

import type { ControlLoopSummary } from '@/lib/types/control-loop.types'

interface ControlLoopCardProps {
  loop: ControlLoopSummary
  className?: string
}

/**
 * Individual Control Loop Card
 * 
 * Compact display showing:
 * - Loop identification and status
 * - Current process values
 * - Performance indicators
 * - Quick actions
 */
export function ControlLoopCard({ loop, className = "" }: ControlLoopCardProps) {
  // Status styling
  const getStatusStyles = (status: string) => {
    switch (status) {
      case 'running':
        return {
          bg: 'bg-green-900/20',
          border: 'border-green-500',
          text: 'text-green-400',
          indicator: 'bg-green-400'
        }
      case 'stopped':
        return {
          bg: 'bg-gray-900/20',
          border: 'border-gray-500',
          text: 'text-gray-400',
          indicator: 'bg-gray-400'
        }
      case 'error':
        return {
          bg: 'bg-red-900/20',
          border: 'border-red-500',
          text: 'text-red-400',
          indicator: 'bg-red-400'
        }
      case 'tuning':
        return {
          bg: 'bg-blue-900/20',
          border: 'border-blue-500',
          text: 'text-blue-400',
          indicator: 'bg-blue-400'
        }
      case 'manual':
        return {
          bg: 'bg-yellow-900/20',
          border: 'border-yellow-500',
          text: 'text-yellow-400',
          indicator: 'bg-yellow-400'
        }
      case 'cascade':
        return {
          bg: 'bg-purple-900/20',
          border: 'border-purple-500',
          text: 'text-purple-400',
          indicator: 'bg-purple-400'
        }
      default:
        return {
          bg: 'bg-gray-900/20',
          border: 'border-gray-500',
          text: 'text-gray-400',
          indicator: 'bg-gray-400'
        }
    }
  }

  // Performance styling
  const getPerformanceStyles = (score: number) => {
    if (score >= 90) return 'text-green-400'
    if (score >= 70) return 'text-yellow-400'
    return 'text-red-400'
  }

  // Control loop type display name
  const getTypeDisplayName = (type: string) => {
    switch (type) {
      case 'ladder_logic_standard_pid':
        return 'LL Standard PID'
      case 'ladder_logic_advanced_pid':
        return 'LL Advanced PID'
      case 'function_block_standard_pide':
        return 'FB Standard PIDE'
      case 'function_block_advanced_pide':
        return 'FB Advanced PIDE'
      default:
        return type
    }
  }

  const statusStyles = getStatusStyles(loop.status)
  const performanceColor = getPerformanceStyles(loop.performance_score)
  const typeDisplayName = getTypeDisplayName(loop.type)

  // Calculate error (SP - PV)
  const error = loop.setpoint - loop.process_value
  const errorAbs = Math.abs(error)

  return (
    <div className={`bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-4 hover:border-[#4c4c4c] transition-colors ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            {/* Status indicator */}
            <div className={`w-2 h-2 rounded-full ${statusStyles.indicator} flex-shrink-0`} />
            <h3 className="text-sm font-medium text-white truncate" title={loop.name}>
              {loop.name}
            </h3>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 text-xs rounded ${statusStyles.bg} ${statusStyles.border} ${statusStyles.text} border`}>
              {loop.status.toUpperCase()}
            </span>
            <span className="text-xs text-gray-500">
              {typeDisplayName}
            </span>
          </div>
        </div>
        
        {/* Alarm indicator */}
        {loop.alarms_active > 0 && (
          <div className="flex items-center space-x-1 text-orange-400 ml-2">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-xs">{loop.alarms_active}</span>
          </div>
        )}
      </div>

      {/* Process Values */}
      <div className="grid grid-cols-3 gap-3 mb-3">
        {/* Setpoint */}
        <div className="text-center">
          <div className="text-xs text-gray-400 mb-1">SP</div>
          <div className="text-sm font-mono text-blue-300">
            {loop.setpoint.toFixed(1)}
          </div>
        </div>

        {/* Process Value */}
        <div className="text-center">
          <div className="text-xs text-gray-400 mb-1">PV</div>
          <div className="text-sm font-mono text-white">
            {loop.process_value.toFixed(1)}
          </div>
        </div>

        {/* Control Output */}
        <div className="text-center">
          <div className="text-xs text-gray-400 mb-1">CV</div>
          <div className="text-sm font-mono text-green-300">
            {loop.control_output.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Error and Performance */}
      <div className="flex items-center justify-between mb-3 text-xs">
        <div className="flex items-center space-x-2">
          <span className="text-gray-400">Error:</span>
          <span className={`font-mono ${errorAbs > 5 ? 'text-orange-400' : 'text-gray-300'}`}>
            {error >= 0 ? '+' : ''}{error.toFixed(1)}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-3 h-3 text-gray-400" />
          <span className={`font-medium ${performanceColor}`}>
            {loop.performance_score.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Progress Bar for Performance */}
      <div className="mb-3">
        <div className="w-full bg-gray-700 rounded-full h-1.5">
          <div 
            className={`h-1.5 rounded-full transition-all duration-300 ${
              loop.performance_score >= 90 ? 'bg-green-400' :
              loop.performance_score >= 70 ? 'bg-yellow-400' : 'bg-red-400'
            }`}
            style={{ width: `${Math.min(loop.performance_score, 100)}%` }}
          />
        </div>
      </div>

      {/* Mode and Last Updated */}
      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
        <span>Mode: {loop.mode}</span>
        <span>{loop.last_updated.toLocaleTimeString()}</span>
      </div>

      {/* Quick Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1">
          {/* View Details */}
          <button
            className="p-1.5 text-gray-400 hover:text-white hover:bg-[#3c3c3c] rounded transition-colors"
            title="View Details"
          >
            <Eye className="w-3.5 h-3.5" />
          </button>
          
          {/* Edit */}
          <button
            className="p-1.5 text-gray-400 hover:text-white hover:bg-[#3c3c3c] rounded transition-colors"
            title="Edit Settings"
          >
            <Edit className="w-3.5 h-3.5" />
          </button>
          
          {/* Tune */}
          <button
            className="p-1.5 text-gray-400 hover:text-white hover:bg-[#3c3c3c] rounded transition-colors"
            title="Tune Parameters"
          >
            <Settings className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex items-center space-x-1">
          {/* Start/Stop */}
          {loop.status === 'running' ? (
            <button
              className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-900/20 rounded transition-colors"
              title="Stop Loop"
            >
              <Pause className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              className="p-1.5 text-gray-400 hover:text-green-400 hover:bg-green-900/20 rounded transition-colors"
              title="Start Loop"
            >
              <Play className="w-3.5 h-3.5" />
            </button>
          )}
          
          {/* Reset */}
          <button
            className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-blue-900/20 rounded transition-colors"
            title="Reset Loop"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Additional Status Indicators */}
      <div className="mt-2 pt-2 border-t border-[#3c3c3c] flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <Activity className="w-3 h-3 text-gray-500" />
          <span className="text-gray-500">ID: {loop.id}</span>
        </div>
        
        {loop.status === 'error' && (
          <span className="text-red-400 font-medium">
            ACTION REQUIRED
          </span>
        )}
        
        {loop.alarms_active > 0 && (
          <span className="text-orange-400 font-medium">
            {loop.alarms_active} ALARM{loop.alarms_active !== 1 ? 'S' : ''}
          </span>
        )}
      </div>
    </div>
  )
}

export default ControlLoopCard 