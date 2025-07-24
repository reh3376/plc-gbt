/**
 * Control Loop Filters Component - Phase 31.7
 * AI Task Orchestrator Generated - Dashboard Filtering Interface
 * 
 * Provides comprehensive filtering capabilities for control loops:
 * - Status filtering (running, stopped, error, etc.)
 * - Type filtering (PID, PIDE variants)
 * - Performance threshold filtering
 * - Tag-based filtering
 */

'use client'

import React, { useState, useEffect } from 'react'
import { X, RotateCcw } from 'lucide-react'

import type { DashboardFilters, ControlLoopType } from '@/lib/types/control-loop.types'

// Define the status type for proper typing
type ControlLoopStatus = 'running' | 'stopped' | 'error' | 'tuning' | 'manual' | 'cascade'

interface ControlLoopFiltersProps {
  filters: DashboardFilters
  onFiltersChange: (filters: DashboardFilters) => void
  className?: string
}

/**
 * Comprehensive Filtering Component
 * 
 * Provides intuitive filtering interface with:
 * - Multi-select status filters
 * - Control loop type selection
 * - Performance threshold slider
 * - Tag filtering capabilities
 * - Reset functionality
 */
export function ControlLoopFilters({ 
  filters, 
  onFiltersChange, 
  className = "" 
}: ControlLoopFiltersProps) {
  // Local state for filters
  const [localFilters, setLocalFilters] = useState<DashboardFilters>(filters)

  // Sync with external filters
  useEffect(() => {
    setLocalFilters(filters)
  }, [filters])

  // Apply filters with debouncing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onFiltersChange(localFilters)
    }, 300) // 300ms debounce

    return () => clearTimeout(timeoutId)
  }, [localFilters, onFiltersChange])

  // Status options
  const statusOptions: Array<{
    value: ControlLoopStatus
    label: string
    color: string
  }> = [
    { value: 'running', label: 'Running', color: 'text-green-400' },
    { value: 'stopped', label: 'Stopped', color: 'text-gray-400' },
    { value: 'error', label: 'Error', color: 'text-red-400' },
    { value: 'tuning', label: 'Tuning', color: 'text-blue-400' },
    { value: 'manual', label: 'Manual', color: 'text-yellow-400' },
    { value: 'cascade', label: 'Cascade', color: 'text-purple-400' }
  ]

  // Control loop type options
  const typeOptions = [
    { 
      value: 'ladder_logic_standard_pid', 
      label: 'Ladder Logic Standard PID',
      shortLabel: 'LL Standard PID'
    },
    { 
      value: 'ladder_logic_advanced_pid', 
      label: 'Ladder Logic Advanced PID',
      shortLabel: 'LL Advanced PID'
    },
    { 
      value: 'function_block_standard_pide', 
      label: 'Function Block Standard PIDE',
      shortLabel: 'FB Standard PIDE'
    },
    { 
      value: 'function_block_advanced_pide', 
      label: 'Function Block Advanced PIDE',
      shortLabel: 'FB Advanced PIDE'
    }
  ] as const

  // Handle status toggle
  const handleStatusToggle = (status: ControlLoopStatus) => {
    const currentStatus = localFilters.status || []
    const newStatus = currentStatus.includes(status)
      ? currentStatus.filter(s => s !== status)
      : [...currentStatus, status]
    
    setLocalFilters(prev => ({
      ...prev,
      status: newStatus.length > 0 ? newStatus : undefined
    }))
  }

  // Handle type toggle
  const handleTypeToggle = (type: ControlLoopType) => {
    const currentTypes = localFilters.type || []
    const newTypes = currentTypes.includes(type)
      ? currentTypes.filter(t => t !== type)
      : [...currentTypes, type]
    
    setLocalFilters(prev => ({
      ...prev,
      type: newTypes.length > 0 ? newTypes : undefined
    }))
  }

  // Handle performance threshold change
  const handlePerformanceThresholdChange = (value: number) => {
    setLocalFilters(prev => ({
      ...prev,
      performance_threshold: value > 0 ? value : undefined
    }))
  }

  // Handle tags change
  const handleTagsChange = (tags: string) => {
    const tagArray = tags
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0)
    
    setLocalFilters(prev => ({
      ...prev,
      tags: tagArray.length > 0 ? tagArray : undefined
    }))
  }

  // Reset all filters
  const handleReset = () => {
    setLocalFilters({})
  }

  // Check if any filters are active
  const hasActiveFilters = 
    (localFilters.status && localFilters.status.length > 0) ||
    (localFilters.type && localFilters.type.length > 0) ||
    localFilters.performance_threshold !== undefined ||
    (localFilters.tags && localFilters.tags.length > 0)

  return (
    <div className={`bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-white">Filters</h3>
        <div className="flex items-center space-x-2">
          {hasActiveFilters && (
            <button
              onClick={handleReset}
              className="flex items-center space-x-1 px-2 py-1 text-sm text-gray-400 hover:text-white transition-colors"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Status
          </label>
          <div className="space-y-2">
            {statusOptions.map(option => (
              <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={localFilters.status?.includes(option.value) || false}
                  onChange={() => handleStatusToggle(option.value)}
                  className="w-4 h-4 rounded border-gray-600 bg-[#1e1e1e] text-blue-600 focus:ring-blue-500 focus:ring-2"
                />
                <span className={`text-sm ${option.color}`}>
                  {option.label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Type Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Control Loop Type
          </label>
          <div className="space-y-2">
            {typeOptions.map(option => (
              <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={localFilters.type?.includes(option.value) || false}
                  onChange={() => handleTypeToggle(option.value)}
                  className="w-4 h-4 rounded border-gray-600 bg-[#1e1e1e] text-blue-600 focus:ring-blue-500 focus:ring-2"
                />
                <span className="text-sm text-gray-300" title={option.label}>
                  {option.shortLabel}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Performance Threshold */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Min Performance Score
          </label>
          <div className="space-y-2">
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={localFilters.performance_threshold || 0}
              onChange={(e) => handlePerformanceThresholdChange(Number(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0%</span>
              <span className="text-white font-medium">
                {localFilters.performance_threshold || 0}%
              </span>
              <span>100%</span>
            </div>
            <div className="text-xs text-gray-400">
              Show loops with performance ≥ {localFilters.performance_threshold || 0}%
            </div>
          </div>
        </div>

        {/* Tags Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Tags
          </label>
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Enter tags separated by commas"
              value={localFilters.tags?.join(', ') || ''}
              onChange={(e) => handleTagsChange(e.target.value)}
              className="w-full px-3 py-2 bg-[#1e1e1e] border border-[#3c3c3c] rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
            <div className="text-xs text-gray-400">
              Filter by custom tags (e.g., reactor, critical, new)
            </div>
            {localFilters.tags && localFilters.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {localFilters.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 bg-blue-900/30 text-blue-300 text-xs rounded-md"
                  >
                    {tag}
                    <button
                      onClick={() => {
                        const newTags = localFilters.tags!.filter((_, i) => i !== index)
                        setLocalFilters(prev => ({
                          ...prev,
                          tags: newTags.length > 0 ? newTags : undefined
                        }))
                      }}
                      className="ml-1 text-blue-400 hover:text-blue-300"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="mt-4 pt-4 border-t border-[#3c3c3c]">
          <div className="text-sm text-gray-400">
            Active filters: 
            {(localFilters.status?.length || 0) > 0 && (
              <span className="ml-1 text-blue-300">
                {localFilters.status!.length} status{localFilters.status!.length !== 1 ? 'es' : ''}
              </span>
            )}
            {(localFilters.type?.length || 0) > 0 && (
              <span className="ml-1 text-blue-300">
                {localFilters.type!.length} type{localFilters.type!.length !== 1 ? 's' : ''}
              </span>
            )}
            {localFilters.performance_threshold !== undefined && (
              <span className="ml-1 text-blue-300">
                performance ≥ {localFilters.performance_threshold}%
              </span>
            )}
            {(localFilters.tags?.length || 0) > 0 && (
              <span className="ml-1 text-blue-300">
                {localFilters.tags!.length} tag{localFilters.tags!.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ControlLoopFilters 