/**
 * Workflow Execution Monitor - AI Task Orchestrator TypeScript Implementation
 *
 * @description Real-time workflow execution monitoring with live updates
 * @compliance Strict TypeScript - zero `any` types policy
 * @phase Phase 2.1 - N8N Real-time Integration
 */

'use client';

import { AlertCircle, CheckCircle2, Clock, Loader2, Pause, Play, Square, X } from 'lucide-react';
import React, { useCallback, useEffect, useState } from 'react';

import type { ExecutionMetrics, NodeExecutionState } from '@/lib/stores/workflow-execution-store';
import { useWorkflowExecutionStore } from '@/lib/stores/workflow-execution-store';
import { cn } from '@/lib/utils/cn';

interface WorkflowExecutionMonitorProps {
  readonly className?: string;
  readonly showAdvancedMetrics?: boolean;
  readonly compactMode?: boolean;
}

interface NodeExecutionCardProps {
  readonly nodeState: NodeExecutionState;
  readonly isActive?: boolean;
  readonly onClick?: () => void;
}

interface ExecutionControlsProps {
  readonly className?: string;
  readonly disabled?: boolean;
}

interface ExecutionMetricsProps {
  readonly metrics: ExecutionMetrics;
  readonly className?: string;
}

interface ExecutionProgressProps {
  readonly progress: number;
  readonly currentStep: string;
  readonly totalNodes: number;
  readonly completedNodes: number;
  readonly className?: string;
}

/**
 * Node Execution Card Component
 */
function NodeExecutionCard({ nodeState, isActive = false, onClick }: NodeExecutionCardProps) {
  const getStatusIcon = () => {
    switch (nodeState.status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-gray-400" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'skipped':
        return <X className="w-4 h-4 text-gray-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (nodeState.status) {
      case 'pending':
        return 'border-gray-600 bg-gray-800/50';
      case 'running':
        return 'border-blue-500 bg-blue-900/20 shadow-blue-500/20 shadow-md';
      case 'completed':
        return 'border-green-600 bg-green-900/20';
      case 'error':
        return 'border-red-600 bg-red-900/20';
      case 'skipped':
        return 'border-gray-500 bg-gray-700/50';
      default:
        return 'border-gray-600 bg-gray-800/50';
    }
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return '--';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <button
      type="button"
      className={cn(
        'relative p-3 rounded-lg border-2 transition-all duration-200 hover:shadow-lg w-full text-left',
        getStatusColor(),
        isActive && 'ring-2 ring-blue-500/50'
      )}
      onClick={onClick}
      aria-label={`Node ${nodeState.nodeId} - Status: ${nodeState.status}`}
    >
      {/* Status indicator */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className="text-sm font-medium text-gray-200">{nodeState.nodeId}</span>
        </div>
        {nodeState.executionTime !== undefined && (
          <span className="text-xs text-gray-400">{formatDuration(nodeState.executionTime)}</span>
        )}
      </div>

      {/* Progress bar for running nodes */}
      {nodeState.status === 'running' && nodeState.progress !== undefined && (
        <div className="mb-2">
          <div className="w-full bg-gray-700 rounded-full h-1.5">
            <div
              className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${nodeState.progress}%` }}
            />
          </div>
          <span className="text-xs text-gray-400 mt-1">{nodeState.progress}% complete</span>
        </div>
      )}

      {/* Error message */}
      {nodeState.status === 'error' && nodeState.error && (
        <div className="mt-2 p-2 bg-red-900/30 border border-red-700 rounded text-xs text-red-300">
          {nodeState.error}
        </div>
      )}

      {/* Timestamps */}
      <div className="flex justify-between text-xs text-gray-500 mt-2">
        {nodeState.startedAt && <span>Started: {nodeState.startedAt.toLocaleTimeString()}</span>}
        {nodeState.finishedAt && <span>Finished: {nodeState.finishedAt.toLocaleTimeString()}</span>}
      </div>
    </button>
  );
}

/**
 * Execution Controls Component
 */
function ExecutionControls({ className, disabled = false }: ExecutionControlsProps) {
  const {
    isExecuting,
    isPaused,
    pauseWorkflowExecution,
    resumeWorkflowExecution,
    cancelWorkflowExecution,
  } = useWorkflowExecutionStore();

  const handlePause = useCallback(async () => {
    try {
      await pauseWorkflowExecution();
    } catch (error) {
      console.error('Failed to pause execution:', error);
    }
  }, [pauseWorkflowExecution]);

  const handleResume = useCallback(async () => {
    try {
      await resumeWorkflowExecution();
    } catch (error) {
      console.error('Failed to resume execution:', error);
    }
  }, [resumeWorkflowExecution]);

  const handleCancel = useCallback(async () => {
    try {
      await cancelWorkflowExecution();
    } catch (error) {
      console.error('Failed to cancel execution:', error);
    }
  }, [cancelWorkflowExecution]);

  return (
    <div className={cn('flex items-center space-x-2', className)}>
      {isExecuting && !isPaused && (
        <button
          onClick={handlePause}
          disabled={disabled}
          className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors"
        >
          <Pause className="w-4 h-4" />
          <span>Pause</span>
        </button>
      )}

      {isPaused && (
        <button
          onClick={handleResume}
          disabled={disabled}
          className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors"
        >
          <Play className="w-4 h-4" />
          <span>Resume</span>
        </button>
      )}

      {(isExecuting || isPaused) && (
        <button
          onClick={handleCancel}
          disabled={disabled}
          className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors"
        >
          <Square className="w-4 h-4" />
          <span>Cancel</span>
        </button>
      )}
    </div>
  );
}

/**
 * Execution Metrics Component
 */
function ExecutionMetrics({ metrics, className }: ExecutionMetricsProps) {
  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
  };

  return (
    <div className={cn('grid grid-cols-2 lg:grid-cols-4 gap-4', className)}>
      {/* Total execution time */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
        <div className="text-xs text-gray-400 mb-1">Total Time</div>
        <div className="text-lg font-semibold text-white">
          {formatTime(metrics.totalExecutionTime)}
        </div>
      </div>

      {/* Average node time */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
        <div className="text-xs text-gray-400 mb-1">Avg Node Time</div>
        <div className="text-lg font-semibold text-white">
          {formatTime(metrics.averageNodeTime)}
        </div>
      </div>

      {/* Success rate */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
        <div className="text-xs text-gray-400 mb-1">Success Rate</div>
        <div className="text-lg font-semibold text-white">{metrics.successRate.toFixed(1)}%</div>
      </div>

      {/* Error count */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
        <div className="text-xs text-gray-400 mb-1">Errors</div>
        <div className="text-lg font-semibold text-white">{metrics.errorCount}</div>
      </div>

      {/* Slowest node */}
      {metrics.slowestNode && (
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3 col-span-2">
          <div className="text-xs text-gray-400 mb-1">Slowest Node</div>
          <div className="text-sm font-semibold text-white">{metrics.slowestNode.nodeId}</div>
          <div className="text-xs text-gray-400">
            {formatTime(metrics.slowestNode.executionTime)}
          </div>
        </div>
      )}

      {/* Fastest node */}
      {metrics.fastestNode && (
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3 col-span-2">
          <div className="text-xs text-gray-400 mb-1">Fastest Node</div>
          <div className="text-sm font-semibold text-white">{metrics.fastestNode.nodeId}</div>
          <div className="text-xs text-gray-400">
            {formatTime(metrics.fastestNode.executionTime)}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Execution Progress Component
 */
function ExecutionProgress({
  progress,
  currentStep,
  totalNodes,
  completedNodes,
  className,
}: ExecutionProgressProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-sm text-gray-300 mb-2">
          <span>Execution Progress</span>
          <span>{progress.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2.5">
          <div
            className="bg-gradient-to-r from-blue-500 to-green-500 h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Current step */}
      <div className="text-sm text-gray-300">
        <span className="font-medium">Current Step:</span> {currentStep}
      </div>

      {/* Node statistics */}
      <div className="flex justify-between text-xs text-gray-400">
        <span>
          Nodes: {completedNodes} / {totalNodes}
        </span>
        <span>Remaining: {totalNodes - completedNodes}</span>
      </div>
    </div>
  );
}

/**
 * Main Workflow Execution Monitor Component
 */
export function WorkflowExecutionMonitor({
  className,
  showAdvancedMetrics = true,
  compactMode = false,
}: WorkflowExecutionMonitorProps) {
  const {
    currentExecution,
    nodeExecutionData,
    executionProgress,
    currentStepDescription,
    executionMetrics,
    connectionStatus,
    lastError,
    initializeWebSocket,
  } = useWorkflowExecutionStore();

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Initialize WebSocket connection on mount
  useEffect(() => {
    if (connectionStatus === 'disconnected') {
      initializeWebSocket().catch(console.error);
    }
  }, [connectionStatus, initializeWebSocket]);

  // Convert Map to Array for rendering
  const nodeStatesArray = Array.from(nodeExecutionData.entries()).map(([, state]) => state);

  // Connection status indicator
  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'bg-green-500';
      case 'connecting':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (compactMode) {
    return (
      <div className={cn('bg-gray-900 border border-gray-700 rounded-lg p-4', className)}>
        {currentExecution ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-white">Workflow Execution</h3>
              <div className={cn('w-2 h-2 rounded-full', getConnectionStatusColor())} />
            </div>

            <ExecutionProgress
              progress={executionProgress}
              currentStep={currentStepDescription}
              totalNodes={currentExecution.totalNodes}
              completedNodes={currentExecution.completedNodes}
            />

            <ExecutionControls />
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <Clock className="w-8 h-8 mx-auto mb-2" />
            <p>No active execution</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={cn('bg-gray-900 border border-gray-700 rounded-lg', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <h2 className="text-lg font-semibold text-white">Workflow Execution Monitor</h2>
          <div
            className={cn('w-3 h-3 rounded-full', getConnectionStatusColor())}
            title={`Connection: ${connectionStatus}`}
          />
        </div>

        {currentExecution && <ExecutionControls />}
      </div>

      {/* Content */}
      <div className="p-4">
        {lastError && (
          <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-red-300">{lastError}</div>
          </div>
        )}

        {currentExecution ? (
          <div className="space-y-6">
            {/* Execution info */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div>
                  <div className="text-xs text-gray-400 mb-1">Execution ID</div>
                  <div className="text-sm font-mono text-white">{currentExecution.executionId}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Workflow ID</div>
                  <div className="text-sm font-mono text-white">{currentExecution.workflowId}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Status</div>
                  <div className="text-sm font-semibold text-white capitalize">
                    {currentExecution.status}
                  </div>
                </div>
              </div>
            </div>

            {/* Progress */}
            <ExecutionProgress
              progress={executionProgress}
              currentStep={currentStepDescription}
              totalNodes={currentExecution.totalNodes}
              completedNodes={currentExecution.completedNodes}
            />

            {/* Node execution states */}
            {nodeStatesArray.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Node Execution States</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {nodeStatesArray.map(nodeState => (
                    <NodeExecutionCard
                      key={nodeState.nodeId}
                      nodeState={nodeState}
                      isActive={selectedNodeId === nodeState.nodeId}
                      onClick={() =>
                        setSelectedNodeId(
                          selectedNodeId === nodeState.nodeId ? null : nodeState.nodeId
                        )
                      }
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Advanced metrics */}
            {showAdvancedMetrics && executionMetrics && (
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Execution Metrics</h3>
                <ExecutionMetrics metrics={executionMetrics} />
              </div>
            )}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-12">
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-medium mb-2">No Active Execution</h3>
            <p className="text-sm">Start a workflow execution to see real-time monitoring data</p>
          </div>
        )}
      </div>
    </div>
  );
}
