/**
 * Control Loop Dashboard - Phase 31.7 Main Component
 * AI Task Orchestrator Generated - Uses Enhanced Backend Infrastructure
 * 
 * Primary dashboard container for industrial control loop management
 * Integrates with robust backend JSON schema framework from Phase 20
 * Follows user standards: React + TypeScript + Tailwind + Zod validation
 */

'use client'

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { AlertCircle, RefreshCw, Settings, Plus, Filter, Search, BarChart3 } from 'lucide-react'

// Enhanced types and schemas
import type { 
  ControlLoopSummary, 
  DashboardFilters, 
  ControlLoopType,
  ControlLoopUpdate 
} from '@/lib/types/control-loop.types'
import { dashboardFiltersSchema, controlLoopSummarySchema } from '@/lib/schemas/control-loop.schemas'

// Component imports (to be implemented)
import { ControlLoopGrid } from './ControlLoopGrid'
import { ControlLoopFilters } from './ControlLoopFilters'
import { ControlLoopStats } from './ControlLoopStats'
import { CreateControlLoopModal } from './CreateControlLoopModal'

// Mock data for development - will be replaced with API calls
const mockControlLoops: ControlLoopSummary[] = [
  {
    id: 'loop_001',
    name: 'Reactor Temperature Control',
    type: 'ladder_logic_advanced_pid',
    status: 'running',
    setpoint: 150.0,
    process_value: 149.8,
    control_output: 67.5,
    mode: 'Automatic',
    performance_score: 87.3,
    alarms_active: 0,
    last_updated: new Date('2025-01-17T10:30:00Z')
  },
  {
    id: 'loop_002', 
    name: 'Flow Rate Controller',
    type: 'function_block_standard_pide',
    status: 'running',
    setpoint: 250.0,
    process_value: 252.1,
    control_output: 42.8,
    mode: 'Automatic',
    performance_score: 94.1,
    alarms_active: 0,
    last_updated: new Date('2025-01-17T10:29:45Z')
  },
  {
    id: 'loop_003',
    name: 'Pressure Relief System',
    type: 'ladder_logic_standard_pid',
    status: 'manual',
    setpoint: 85.0,
    process_value: 83.2,
    control_output: 38.5,
    mode: 'Manual',
    performance_score: 72.6,
    alarms_active: 1,
    last_updated: new Date('2025-01-17T10:28:12Z')
  },
  {
    id: 'loop_004',
    name: 'Level Control Tank A',
    type: 'function_block_advanced_pide',
    status: 'error',
    setpoint: 75.0,
    process_value: 0.0,
    control_output: 0.0,
    mode: 'Override',
    performance_score: 0.0,
    alarms_active: 3,
    last_updated: new Date('2025-01-17T10:25:33Z')
  }
]

interface ControlLoopDashboardProps {
  /** Optional initial filters to apply */
  initialFilters?: Partial<DashboardFilters>
  /** Whether to enable real-time updates */
  enableRealTime?: boolean
  /** Refresh interval in milliseconds */
  refreshInterval?: number
  /** Custom CSS class name */
  className?: string
}

/**
 * Main Control Loop Dashboard Component
 * 
 * Provides comprehensive view of all control loops with:
 * - Real-time status updates
 * - Performance monitoring  
 * - Filtering and search capabilities
 * - Quick actions (create, edit, tune)
 * - Alarm management
 */
export function ControlLoopDashboard({
  initialFilters = {},
  enableRealTime = true,
  refreshInterval = 5000,
  className = ""
}: ControlLoopDashboardProps) {
  // State management
  const [controlLoops, setControlLoops] = useState<ControlLoopSummary[]>(mockControlLoops)
  const [filters, setFilters] = useState<DashboardFilters>(initialFilters)
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // Filtered and searched control loops
  const filteredLoops = useMemo(() => {
    let filtered = controlLoops

    // Apply status filter
    if (filters.status && filters.status.length > 0) {
      filtered = filtered.filter(loop => filters.status!.includes(loop.status))
    }

    // Apply type filter
    if (filters.type && filters.type.length > 0) {
      filtered = filtered.filter(loop => filters.type!.includes(loop.type))
    }

    // Apply performance threshold filter
    if (filters.performance_threshold !== undefined) {
      filtered = filtered.filter(loop => loop.performance_score >= filters.performance_threshold!)
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(loop => 
        loop.name.toLowerCase().includes(query) ||
        loop.id.toLowerCase().includes(query) ||
        loop.type.toLowerCase().includes(query)
      )
    }

    return filtered
  }, [controlLoops, filters, searchQuery])

  // Dashboard statistics
  const dashboardStats = useMemo(() => {
    const totalLoops = controlLoops.length
    const runningLoops = controlLoops.filter(loop => loop.status === 'running').length
    const errorLoops = controlLoops.filter(loop => loop.status === 'error').length
    const totalAlarms = controlLoops.reduce((sum, loop) => sum + loop.alarms_active, 0)
    const avgPerformance = totalLoops > 0 
      ? controlLoops.reduce((sum, loop) => sum + loop.performance_score, 0) / totalLoops 
      : 0

    return {
      totalLoops,
      runningLoops,
      errorLoops,
      totalAlarms,
      avgPerformance: Math.round(avgPerformance * 10) / 10
    }
  }, [controlLoops])

  // Fetch control loops data
  const fetchControlLoops = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/control-loops/summary')
      // const data = await response.json()
      
      // Validate response with Zod schema
      // const validatedLoops = z.array(controlLoopSummarySchema).parse(data.loops)
      // setControlLoops(validatedLoops)
      
      // For now, simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      setControlLoops(mockControlLoops)
      setLastRefresh(new Date())
      
    } catch (err) {
      console.error('Failed to fetch control loops:', err)
      setError('Failed to load control loops. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Handle real-time updates
  const handleRealTimeUpdate = useCallback((update: ControlLoopUpdate) => {
    setControlLoops(prev => 
      prev.map(loop => 
        loop.id === update.loop_id
          ? { 
              ...loop,
              // Handle status update
              ...(update.updates.status && { status: update.updates.status }),
              // Handle process variable update - extract current_value
              ...(update.updates.process_variable && { 
                process_value: update.updates.process_variable.current_value ?? loop.process_value 
              }),
              // Handle control output update - extract current_value as number
              ...(update.updates.control_output && { 
                control_output: typeof update.updates.control_output === 'number' 
                  ? update.updates.control_output 
                  : update.updates.control_output.current_value ?? loop.control_output 
              }),
              // Handle performance metrics update - extract performance_score
              ...(update.updates.performance_metrics && { 
                performance_score: update.updates.performance_metrics.performance_score ?? loop.performance_score 
              }),
              last_updated: update.timestamp 
            }
          : loop
      )
    )
  }, [])

  // Setup real-time updates
  useEffect(() => {
    if (!enableRealTime) return

    const interval = setInterval(fetchControlLoops, refreshInterval)
    
    // TODO: Setup WebSocket connection for real-time updates
    // const ws = new WebSocket('/api/control-loops/ws')
    // ws.onmessage = (event) => {
    //   const update = JSON.parse(event.data)
    //   handleRealTimeUpdate(update)
    // }

    return () => {
      clearInterval(interval)
      // ws.close()
    }
  }, [enableRealTime, refreshInterval, fetchControlLoops, handleRealTimeUpdate])

  // Initial data load
  useEffect(() => {
    fetchControlLoops()
  }, [fetchControlLoops])

  // Handle filter changes
  const handleFiltersChange = useCallback((newFilters: DashboardFilters) => {
    try {
      const validatedFilters = dashboardFiltersSchema.parse(newFilters)
      setFilters(validatedFilters)
    } catch (err) {
      console.error('Invalid filters:', err)
      setError('Invalid filter configuration')
    }
  }, [])

  // Handle search change
  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query)
  }, [])

  // Handle manual refresh
  const handleRefresh = useCallback(() => {
    fetchControlLoops()
  }, [fetchControlLoops])

  return (
    <div className={`h-full w-full flex flex-col bg-[#1e1e1e] text-white ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[#3c3c3c]">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-white">Control Loop Dashboard</h1>
          <div className="flex items-center text-sm text-gray-400">
            <span>Last updated: {lastRefresh.toLocaleTimeString()}</span>
            {isLoading && <RefreshCw className="w-4 h-4 ml-2 animate-spin" />}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search loops..."
              value={searchQuery}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="pl-10 pr-4 py-2 bg-[#2d2d2d] border border-[#3c3c3c] rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
            />
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-md border transition-colors ${
              showFilters 
                ? 'bg-blue-600 border-blue-500 text-white' 
                : 'bg-[#2d2d2d] border-[#3c3c3c] text-gray-300 hover:bg-[#3c3c3c]'
            }`}
            title="Toggle Filters"
          >
            <Filter className="w-4 h-4" />
          </button>

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="p-2 bg-[#2d2d2d] border border-[#3c3c3c] rounded-md text-gray-300 hover:bg-[#3c3c3c] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          {/* Settings Button */}
          <button
            className="p-2 bg-[#2d2d2d] border border-[#3c3c3c] rounded-md text-gray-300 hover:bg-[#3c3c3c] transition-colors"
            title="Dashboard Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* Create New Loop Button */}
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Create Loop</span>
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-900/20 border border-red-500 rounded-md flex items-center space-x-2 text-red-400">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
          <button 
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-300"
          >
            ×
          </button>
        </div>
      )}

      {/* Dashboard Stats */}
      <ControlLoopStats 
        stats={dashboardStats}
        className="m-4"
      />

      {/* Filters Panel */}
      {showFilters && (
        <ControlLoopFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          className="mx-4 mb-4"
        />
      )}

      {/* Main Content */}
      <div className="flex-1 p-4 overflow-hidden">
        <ControlLoopGrid
          controlLoops={filteredLoops}
          isLoading={isLoading}
          onRefresh={handleRefresh}
          className="h-full"
        />
      </div>

      {/* Create Control Loop Modal */}
      {isCreateModalOpen && (
        <CreateControlLoopModal
          onClose={() => setIsCreateModalOpen(false)}
          onCreated={(newLoop) => {
            setControlLoops(prev => [...prev, newLoop])
            setIsCreateModalOpen(false)
          }}
        />
      )}
    </div>
  )
}

export default ControlLoopDashboard 