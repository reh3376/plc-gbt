/**
 * Control Loop Stats Component - Phase 31.7
 * AI Task Orchestrator Generated - Dashboard Statistics Display
 *
 * Displays key performance metrics and statistics for control loops
 * Provides at-a-glance overview of system health and performance
 */

'use client';

import { Activity, AlertTriangle, CheckCircle, Clock, TrendingUp, XCircle } from 'lucide-react';
import React from 'react';

interface DashboardStats {
  totalLoops: number;
  runningLoops: number;
  errorLoops: number;
  totalAlarms: number;
  avgPerformance: number;
}

interface ControlLoopStatsProps {
  stats: DashboardStats;
  className?: string;
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
export function ControlLoopStats({ stats, className = '' }: ControlLoopStatsProps) {
  const { totalLoops, runningLoops, errorLoops, totalAlarms, avgPerformance } = stats;

  // Calculate derived metrics
  const stoppedLoops = totalLoops - runningLoops - errorLoops;
  const healthPercentage = totalLoops > 0 ? Math.round((runningLoops / totalLoops) * 100) : 0;
  const performanceColor =
    avgPerformance >= 90
      ? 'text-green-400'
      : avgPerformance >= 70
        ? 'text-yellow-400'
        : 'text-red-400';

  const performanceBgColor =
    avgPerformance >= 90
      ? 'bg-green-900/20 border-green-500'
      : avgPerformance >= 70
        ? 'bg-yellow-900/20 border-yellow-500'
        : 'bg-red-900/20 border-red-500';

  return (
    <div
      className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-2 sm:gap-3 lg:gap-4 ${className}`}
    >
      {/* Total Loops */}
      <div className="bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-3 lg:p-4 min-w-0 overflow-hidden flex flex-col min-h-[6rem] max-h-[8rem]">
        <div className="flex items-center justify-between min-w-0">
          <div className="min-w-0 flex-1">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Total Loops
            </p>
            <p className="font-bold text-white" style={{ fontSize: 'clamp(1.25rem, 3vw, 2rem)' }}>
              {totalLoops}
            </p>
          </div>
          <Activity className="w-6 h-6 lg:w-8 lg:h-8 text-blue-400 flex-shrink-0" />
        </div>
        <div
          className="mt-2 text-gray-500 truncate"
          style={{ fontSize: 'clamp(0.7rem, 1vw, 0.75rem)' }}
        >
          Industrial control points
        </div>
      </div>

      {/* Running Loops */}
      <div className="bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-3 lg:p-4 min-w-0 overflow-hidden flex flex-col min-h-[6rem] max-h-[8rem]">
        <div className="flex items-center justify-between min-w-0">
          <div className="min-w-0 flex-1">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Running
            </p>
            <p
              className="font-bold text-green-400"
              style={{ fontSize: 'clamp(1.25rem, 3vw, 2rem)' }}
            >
              {runningLoops}
            </p>
          </div>
          <CheckCircle className="w-6 h-6 lg:w-8 lg:h-8 text-green-400 flex-shrink-0" />
        </div>
        <div
          className="mt-2 text-gray-500 truncate"
          style={{ fontSize: 'clamp(0.7rem, 1vw, 0.75rem)' }}
        >
          {healthPercentage}% system health
        </div>
      </div>

      {/* Error Loops */}
      <div className="bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-3 lg:p-4 min-w-0 overflow-hidden flex flex-col min-h-[6rem] max-h-[8rem]">
        <div className="flex items-center justify-between min-w-0">
          <div className="min-w-0 flex-1">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Errors
            </p>
            <p className="font-bold text-red-400" style={{ fontSize: 'clamp(1.25rem, 3vw, 2rem)' }}>
              {errorLoops}
            </p>
          </div>
          <XCircle className="w-6 h-6 lg:w-8 lg:h-8 text-red-400 flex-shrink-0" />
        </div>
        <div
          className="mt-2 text-gray-500 truncate"
          style={{ fontSize: 'clamp(0.7rem, 1vw, 0.75rem)' }}
        >
          {stoppedLoops} stopped loops
        </div>
      </div>

      {/* Active Alarms */}
      <div className="bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-3 lg:p-4 min-w-0 overflow-hidden flex flex-col min-h-[6rem] max-h-[8rem]">
        <div className="flex items-center justify-between min-w-0">
          <div className="min-w-0 flex-1">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Active Alarms
            </p>
            <p
              className={`font-bold ${totalAlarms > 0 ? 'text-orange-400' : 'text-gray-400'}`}
              style={{ fontSize: 'clamp(1.25rem, 3vw, 2rem)' }}
            >
              {totalAlarms}
            </p>
          </div>
          <AlertTriangle
            className={`w-6 h-6 lg:w-8 lg:h-8 flex-shrink-0 ${totalAlarms > 0 ? 'text-orange-400' : 'text-gray-500'}`}
          />
        </div>
        <div
          className="mt-2 text-gray-500 truncate"
          style={{ fontSize: 'clamp(0.7rem, 1vw, 0.75rem)' }}
        >
          {totalAlarms > 0 ? 'Requires attention' : 'All clear'}
        </div>
      </div>

      {/* Average Performance */}
      <div
        className={`bg-[#2d2d2d] border rounded-lg p-3 lg:p-4 min-w-0 overflow-hidden flex flex-col min-h-[6rem] max-h-[8rem] ${performanceBgColor}`}
      >
        <div className="flex items-center justify-between min-w-0">
          <div className="min-w-0 flex-1">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Avg Performance
            </p>
            <p
              className={`font-bold ${performanceColor}`}
              style={{ fontSize: 'clamp(1.25rem, 3vw, 2rem)' }}
            >
              {avgPerformance.toFixed(1)}%
            </p>
          </div>
          <TrendingUp className={`w-6 h-6 lg:w-8 lg:h-8 flex-shrink-0 ${performanceColor}`} />
        </div>
        <div className="mt-2 min-w-0">
          {/* Performance Bar */}
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                avgPerformance >= 90
                  ? 'bg-green-400'
                  : avgPerformance >= 70
                    ? 'bg-yellow-400'
                    : 'bg-red-400'
              }`}
              style={{ width: `${Math.min(avgPerformance, 100)}%` }}
            />
          </div>
          <div
            className="mt-1 text-gray-500 truncate"
            style={{ fontSize: 'clamp(0.7rem, 1vw, 0.75rem)' }}
          >
            Overall system efficiency
          </div>
        </div>
      </div>

      {/* Additional Quick Stats Row (spans full width on mobile) */}
      <div className="md:col-span-2 lg:col-span-5 bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg p-3 lg:p-4 min-w-0 overflow-hidden">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 sm:gap-3 lg:gap-4 text-center">
          <div className="min-w-0">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Manual Mode
            </p>
            <p
              className="font-semibold text-yellow-400"
              style={{ fontSize: 'clamp(1rem, 2vw, 1.125rem)' }}
            >
              {stoppedLoops}
            </p>
          </div>
          <div className="min-w-0">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Cascade Loops
            </p>
            <p
              className="font-semibold text-blue-400"
              style={{ fontSize: 'clamp(1rem, 2vw, 1.125rem)' }}
            >
              0
            </p>
          </div>
          <div className="min-w-0">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Tuning Sessions
            </p>
            <p
              className="font-semibold text-purple-400"
              style={{ fontSize: 'clamp(1rem, 2vw, 1.125rem)' }}
            >
              0
            </p>
          </div>
          <div className="min-w-0">
            <p
              className="text-gray-400 truncate"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Last Update
            </p>
            <div className="flex items-center justify-center space-x-1 text-gray-400">
              <Clock className="w-3 h-3 flex-shrink-0" />
              <span style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}>Live</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ControlLoopStats;
