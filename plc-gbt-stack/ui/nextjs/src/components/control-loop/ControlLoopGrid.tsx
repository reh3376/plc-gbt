/**
 * Control Loop Grid Component - Phase 31.7
 * AI Task Orchestrator Generated - Grid Layout for Control Loops
 * 
 * Displays control loops in an organized grid layout with:
 * - Responsive design (1-4 columns based on screen size)
 * - Individual control loop cards
 * - Loading states and empty states
 * - Quick action buttons
 */

'use client'

import React from 'react'
import { RefreshCw, Loader2 } from 'lucide-react'

import type { ControlLoopSummary } from '@/lib/types/control-loop.types'
import { ControlLoopCard } from './ControlLoopCard'

interface ControlLoopGridProps {
  controlLoops: ControlLoopSummary[]
  isLoading: boolean
  onRefresh: () => void
  className?: string
}

/**
 * Grid Layout Component for Control Loops
 * 
 * Features:
 * - Responsive grid (1-4 columns)
 * - Loading and empty states
 * - Individual control loop cards
 * - Refresh functionality
 */
export function ControlLoopGrid({ 
  controlLoops, 
  isLoading, 
  onRefresh, 
  className = "" 
}: ControlLoopGridProps) {
  // Show loading state
  if (isLoading && controlLoops.length === 0) {
    return (
      <div className={`h-full flex items-center justify-center ${className}`}>
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-gray-400">Loading control loops...</p>
        </div>
      </div>
    )
  }

  // Show empty state
  if (!isLoading && controlLoops.length === 0) {
    return (
      <div className={`h-full flex items-center justify-center ${className}`}>
        <div className="text-center max-w-md">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-700 flex items-center justify-center">
            <RefreshCw className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-white mb-2">No Control Loops Found</h3>
          <p className="text-gray-400 mb-6">
            No control loops match your current filters. Try adjusting your search criteria or refresh the data.
          </p>
          <button
            onClick={onRefresh}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh Data</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`h-full ${className}`}>
      {/* Grid Container */}
      <div className="h-full overflow-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-1">
          {controlLoops.map((loop) => (
            <ControlLoopCard
              key={loop.id}
              loop={loop}
              className="h-fit"
            />
          ))}
        </div>

        {/* Loading overlay when refreshing */}
        {isLoading && controlLoops.length > 0 && (
          <div className="fixed bottom-4 right-4 bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg px-4 py-2 shadow-lg">
            <div className="flex items-center space-x-2 text-sm text-gray-300">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Refreshing...</span>
            </div>
          </div>
        )}
      </div>

      {/* Grid Statistics */}
      <div className="mt-4 px-1 py-2 border-t border-[#3c3c3c]">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>
            Showing {controlLoops.length} control loop{controlLoops.length !== 1 ? 's' : ''}
          </span>
          <div className="flex items-center space-x-4">
            <span>
              Running: {controlLoops.filter(loop => loop.status === 'running').length}
            </span>
            <span>
              Errors: {controlLoops.filter(loop => loop.status === 'error').length}
            </span>
            <span>
              Alarms: {controlLoops.reduce((total, loop) => total + loop.alarms_active, 0)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ControlLoopGrid 