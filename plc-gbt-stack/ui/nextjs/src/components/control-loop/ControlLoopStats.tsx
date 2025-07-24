/**
 * Control Loop Stats Component - Phase 31.7
 * AI Task Orchestrator Generated - Dashboard Statistics Display
 * 
 * Displays key performance metrics and statistics for control loops
 * Provides at-a-glance overview of system health and performance
 */

'use client'

import React from 'react'
import { Activity, AlertTriangle, CheckCircle, XCircle, TrendingUp, Clock } from 'lucide-react'

interface DashboardStats {
  totalLoops: number
  runningLoops: number
  errorLoops: number
  totalAlarms: number
  avgPerformance: number
}

interface ControlLoopStatsProps {
  stats: DashboardStats
  className?: string
}

/**
 * Dashboard Statistics Component
 * 
 * Displays key metrics in an attractive card layout:
 * - Total control loops
 * - Running loops vs errors
 * - Active alarms count
 * - Average performance score
 */
export function ControlLoopStats({ stats, className = "" }: ControlLoopStatsProps) {
  const { totalLoops, runningLoops, errorLoops, totalAlarms, avgPerformance } = stats

  // Calculate derived metrics
  const stoppedLoops = totalLoops - runningLoops - errorLoops
  const healthPercentage = totalLoops > 0 ? Math.round((runningLoops / totalLoops) * 100) : 0
  const performanceColor = 
    avgPerformance >= 90 ? 'text-green-400' :
    avgPerformance >= 70 ? 'text-yellow-400' : 'text-red-400'

  const performanceBgColor = 
    avgPerformance >= 90 ? 'bg-green-900/20 border-green-500' :
    avgPerformance >= 70 ? 'bg-yellow-900/20 border-yellow-500' : 'bg-red-900/20 border-red-500'

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 ${className}`}>
      {/* Total Loops */}
      <div className="bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Total Loops</p>
            <p className="text-2xl font-bold text-white">{totalLoops}</p>
          </div>
          <Activity className="w-8 h-8 text-blue-400" />
        </div>
        <div className="mt-2 text-xs text-gray-500">
          Industrial control points
        </div>
      </div>

      {/* Running Loops */}
      <div className="bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Running</p>
            <p className="text-2xl font-bold text-green-400">{runningLoops}</p>
          </div>
          <CheckCircle className="w-8 h-8 text-green-400" />
        </div>
        <div className="mt-2 text-xs text-gray-500">
          {healthPercentage}% system health
        </div>
      </div>

      {/* Error Loops */}
      <div className="bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Errors</p>
            <p className="text-2xl font-bold text-red-400">{errorLoops}</p>
          </div>
          <XCircle className="w-8 h-8 text-red-400" />
        </div>
        <div className="mt-2 text-xs text-gray-500">
          {stoppedLoops} stopped loops
        </div>
      </div>

      {/* Active Alarms */}
      <div className="bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Active Alarms</p>
            <p className={`text-2xl font-bold ${totalAlarms > 0 ? 'text-orange-400' : 'text-gray-400'}`}>
              {totalAlarms}
            </p>
          </div>
          <AlertTriangle className={`w-8 h-8 ${totalAlarms > 0 ? 'text-orange-400' : 'text-gray-500'}`} />
        </div>
        <div className="mt-2 text-xs text-gray-500">
          {totalAlarms > 0 ? 'Requires attention' : 'All clear'}
        </div>
      </div>

      {/* Average Performance */}
      <div className={`bg-[#2d2d2d] border rounded-lg p-4 ${performanceBgColor}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Avg Performance</p>
            <p className={`text-2xl font-bold ${performanceColor}`}>
              {avgPerformance.toFixed(1)}%
            </p>
          </div>
          <TrendingUp className={`w-8 h-8 ${performanceColor}`} />
        </div>
        <div className="mt-2">
          {/* Performance Bar */}
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                avgPerformance >= 90 ? 'bg-green-400' :
                avgPerformance >= 70 ? 'bg-yellow-400' : 'bg-red-400'
              }`}
              style={{ width: `${Math.min(avgPerformance, 100)}%` }}
            />
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Overall system efficiency
          </div>
        </div>
      </div>

      {/* Additional Quick Stats Row (spans full width on mobile) */}
      <div className="md:col-span-2 lg:col-span-5 bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-sm text-gray-400">Manual Mode</p>
            <p className="text-lg font-semibold text-yellow-400">{stoppedLoops}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Cascade Loops</p>
            <p className="text-lg font-semibold text-blue-400">0</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Tuning Sessions</p>
            <p className="text-lg font-semibold text-purple-400">0</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Last Update</p>
            <div className="flex items-center justify-center space-x-1 text-sm text-gray-400">
              <Clock className="w-3 h-3" />
              <span>Live</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ControlLoopStats 