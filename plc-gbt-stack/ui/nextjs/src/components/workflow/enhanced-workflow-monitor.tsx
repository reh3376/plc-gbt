'use client';

import {
  Activity,
  BarChart3,
  CheckCircle,
  Clock,
  Eye,
  EyeOff,
  GitBranch,
  Pause,
  Play,
  RefreshCw,
  RotateCcw,
  Square,
  Timer,
  XCircle,
  Zap,
} from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useState } from 'react';

import {
  NodeExecutionState,
  useWorkflowOrchestrationStore,
  WorkflowExecutionContext,
  WorkflowExecutionState,
} from '@/lib/stores/workflow-orchestration-store';
import { cn } from '@/lib/utils/cn';

// Real-time execution monitoring component props
interface EnhancedWorkflowMonitorProps {
  className?: string;
  showAdvancedMetrics?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
  compactMode?: boolean;
}

// Node execution status component
interface NodeExecutionStatusProps {
  nodeId: string;
  state: NodeExecutionState;
  duration?: number;
  error?: string;
  retryCount?: number;
  maxRetries?: number;
  onClick?: () => void;
}

const NodeExecutionStatus: React.FC<NodeExecutionStatusProps> = ({
  nodeId,
  state,
  duration,
  error,
  retryCount = 0,
  maxRetries = 0,
  onClick,
}) => {
  const getStateIcon = () => {
    switch (state) {
      case NodeExecutionState.PENDING:
        return <Clock className="w-4 h-4 text-gray-400" />;
      case NodeExecutionState.RUNNING:
        return <Activity className="w-4 h-4 text-blue-500 animate-pulse" />;
      case NodeExecutionState.COMPLETED:
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case NodeExecutionState.FAILED:
        return <XCircle className="w-4 h-4 text-red-500" />;
      case NodeExecutionState.SKIPPED:
        return <Eye className="w-4 h-4 text-yellow-500" />;
      case NodeExecutionState.WAITING:
        return <Timer className="w-4 h-4 text-orange-500" />;
      case NodeExecutionState.RETRY:
        return <RotateCcw className="w-4 h-4 text-purple-500 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStateColor = () => {
    switch (state) {
      case NodeExecutionState.PENDING:
        return 'bg-gray-100 border-gray-200';
      case NodeExecutionState.RUNNING:
        return 'bg-blue-50 border-blue-200';
      case NodeExecutionState.COMPLETED:
        return 'bg-green-50 border-green-200';
      case NodeExecutionState.FAILED:
        return 'bg-red-50 border-red-200';
      case NodeExecutionState.SKIPPED:
        return 'bg-yellow-50 border-yellow-200';
      case NodeExecutionState.WAITING:
        return 'bg-orange-50 border-orange-200';
      case NodeExecutionState.RETRY:
        return 'bg-purple-50 border-purple-200';
      default:
        return 'bg-gray-100 border-gray-200';
    }
  };

  return (
    <button
      type="button"
      className={cn(
        'flex items-center gap-2 p-2 border rounded-lg cursor-pointer transition-all hover:shadow-sm w-full text-left',
        getStateColor()
      )}
      onClick={onClick}
      onKeyDown={e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
    >
      {getStateIcon()}
      <div className="flex-1 min-w-0">
        <div className="font-medium text-sm truncate">{nodeId}</div>
        <div className="flex items-center gap-2 text-xs text-gray-600">
          {duration && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {duration}ms
            </span>
          )}
          {retryCount > 0 && (
            <span className="flex items-center gap-1">
              <RotateCcw className="w-3 h-3" />
              {retryCount}/{maxRetries}
            </span>
          )}
        </div>
        {error && (
          <div className="text-xs text-red-600 truncate mt-1" title={error}>
            {error}
          </div>
        )}
      </div>
    </button>
  );
};

// Parallel execution monitor component
interface ParallelExecutionMonitorProps {
  branches: WorkflowExecutionContext['parallelBranches'];
}

const ParallelExecutionMonitor: React.FC<ParallelExecutionMonitorProps> = ({ branches }) => {
  if (branches.length === 0) return null;

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <GitBranch className="w-4 h-4 text-blue-600" />
        <span className="font-medium text-blue-900">Parallel Execution</span>
        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
          {branches.length} branches
        </span>
      </div>
      <div className="space-y-2">
        {branches.map(branch => (
          <div
            key={branch.branchId}
            className="flex items-center justify-between bg-white p-2 rounded border"
          >
            <div className="flex items-center gap-2">
              <div
                className={cn(
                  'w-2 h-2 rounded-full',
                  (() => {
                    if (branch.state === WorkflowExecutionState.COMPLETED) return 'bg-green-500';
                    if (branch.state === WorkflowExecutionState.FAILED) return 'bg-red-500';
                    if (branch.state === WorkflowExecutionState.RUNNING)
                      return 'bg-blue-500 animate-pulse';
                    return 'bg-gray-300';
                  })()
                )}
              />
              <span className="text-sm font-medium">Branch {branch.branchId.slice(-8)}</span>
            </div>
            <div className="text-xs text-gray-600">
              {branch.nodeIds.length} nodes
              {branch.endTime && branch.startTime && (
                <span className="ml-2">
                  ({branch.endTime.getTime() - branch.startTime.getTime()}ms)
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Loop execution monitor component
interface LoopExecutionMonitorProps {
  loops: WorkflowExecutionContext['loopContexts'];
}

const LoopExecutionMonitor: React.FC<LoopExecutionMonitorProps> = ({ loops }) => {
  if (loops.length === 0) return null;

  return (
    <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <RefreshCw className="w-4 h-4 text-purple-600" />
        <span className="font-medium text-purple-900">Loop Execution</span>
        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
          {loops.length} active
        </span>
      </div>
      <div className="space-y-2">
        {loops.map(loop => (
          <div key={loop.loopId} className="bg-white p-2 rounded border">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">Loop {loop.loopId.slice(-8)}</span>
              <span className="text-xs text-gray-600">
                {loop.currentIteration}/{loop.maxIterations}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(loop.currentIteration / loop.maxIterations) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Performance metrics component
interface PerformanceMetricsProps {
  executionContext: WorkflowExecutionContext;
  compact?: boolean;
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  executionContext,
  compact = false,
}) => {
  const totalExecutionTime = executionContext.endTime
    ? executionContext.endTime.getTime() - executionContext.startTime.getTime()
    : Date.now() - executionContext.startTime.getTime();

  const nodeExecutionTimes = Object.values(executionContext.performance.nodeExecutionTimes);
  const averageNodeTime =
    nodeExecutionTimes.length > 0
      ? nodeExecutionTimes.reduce((sum, time) => sum + time, 0) / nodeExecutionTimes.length
      : 0;

  const completionRate =
    executionContext.metadata.totalNodes > 0
      ? (executionContext.metadata.completedNodes / executionContext.metadata.totalNodes) * 100
      : 0;

  if (compact) {
    return (
      <div className="flex items-center gap-4 text-xs text-gray-600">
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {Math.round(totalExecutionTime / 1000)}s
        </span>
        <span className="flex items-center gap-1">
          <BarChart3 className="w-3 h-3" />
          {Math.round(completionRate)}%
        </span>
        <span className="flex items-center gap-1">
          <Zap className="w-3 h-3" />
          {Math.round(averageNodeTime)}ms avg
        </span>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <BarChart3 className="w-4 h-4 text-gray-600" />
        <span className="font-medium text-gray-900">Performance Metrics</span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-white p-2 rounded border">
          <div className="text-xs text-gray-600">Total Time</div>
          <div className="font-medium">{Math.round(totalExecutionTime / 1000)}s</div>
        </div>
        <div className="bg-white p-2 rounded border">
          <div className="text-xs text-gray-600">Completion</div>
          <div className="font-medium">{Math.round(completionRate)}%</div>
        </div>
        <div className="bg-white p-2 rounded border">
          <div className="text-xs text-gray-600">Avg Node Time</div>
          <div className="font-medium">{Math.round(averageNodeTime)}ms</div>
        </div>
        <div className="bg-white p-2 rounded border">
          <div className="text-xs text-gray-600">Parallel Efficiency</div>
          <div className="font-medium">
            {Math.round((executionContext.performance.parallelEfficiency || 0) * 100)}%
          </div>
        </div>
      </div>
    </div>
  );
};

// Main enhanced workflow monitor component
export const EnhancedWorkflowMonitor: React.FC<EnhancedWorkflowMonitorProps> = ({
  className,
  showAdvancedMetrics = true,
  autoRefresh = true,
  refreshInterval = 1000,
  compactMode = false,
}) => {
  const {
    currentExecution,
    nodeExecutionData,
    isExecuting,
    isPaused,
    executionProgress,
    currentStepDescription,
    startWorkflowExecution,
    pauseWorkflowExecution,
    resumeWorkflowExecution,
    cancelWorkflowExecution,
    retryFailedNodes,
  } = useWorkflowOrchestrationStore();

  const [isVisible, setIsVisible] = useState(true);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh || !isExecuting) return;

    const interval = setInterval(() => {
      // Force re-render to update real-time metrics
      // In a real implementation, this would trigger data refresh
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, isExecuting, refreshInterval]);

  // Execution control handlers
  const handleStart = useCallback(async () => {
    try {
      await startWorkflowExecution('demo-workflow', { startedBy: 'user' });
    } catch (error) {
      console.error('Failed to start workflow:', error);
    }
  }, [startWorkflowExecution]);

  const handlePause = useCallback(async () => {
    try {
      await pauseWorkflowExecution();
    } catch (error) {
      console.error('Failed to pause workflow:', error);
    }
  }, [pauseWorkflowExecution]);

  const handleResume = useCallback(async () => {
    try {
      await resumeWorkflowExecution();
    } catch (error) {
      console.error('Failed to resume workflow:', error);
    }
  }, [resumeWorkflowExecution]);

  const handleCancel = useCallback(async () => {
    try {
      await cancelWorkflowExecution();
    } catch (error) {
      console.error('Failed to cancel workflow:', error);
    }
  }, [cancelWorkflowExecution]);

  const handleRetry = useCallback(async () => {
    try {
      await retryFailedNodes();
    } catch (error) {
      console.error('Failed to retry failed nodes:', error);
    }
  }, [retryFailedNodes]);

  // Node execution data with statistics
  const nodeStats = useMemo(() => {
    const nodes = Object.values(nodeExecutionData);
    return {
      total: nodes.length,
      pending: nodes.filter(n => n.state === NodeExecutionState.PENDING).length,
      running: nodes.filter(n => n.state === NodeExecutionState.RUNNING).length,
      completed: nodes.filter(n => n.state === NodeExecutionState.COMPLETED).length,
      failed: nodes.filter(n => n.state === NodeExecutionState.FAILED).length,
      skipped: nodes.filter(n => n.state === NodeExecutionState.SKIPPED).length,
      waiting: nodes.filter(n => n.state === NodeExecutionState.WAITING).length,
      retry: nodes.filter(n => n.state === NodeExecutionState.RETRY).length,
    };
  }, [nodeExecutionData]);

  // Execution state indicator
  const getExecutionStateIndicator = () => {
    if (!currentExecution) {
      return (
        <div className="flex items-center gap-2 text-gray-500">
          <div className="w-2 h-2 rounded-full bg-gray-400" />
          <span className="text-sm">No active execution</span>
        </div>
      );
    }

    const stateConfig = {
      [WorkflowExecutionState.IDLE]: {
        color: 'bg-gray-400',
        text: 'Idle',
        icon: <Clock className="w-4 h-4" />,
      },
      [WorkflowExecutionState.RUNNING]: {
        color: 'bg-green-500 animate-pulse',
        text: 'Running',
        icon: <Play className="w-4 h-4" />,
      },
      [WorkflowExecutionState.PAUSED]: {
        color: 'bg-yellow-500',
        text: 'Paused',
        icon: <Pause className="w-4 h-4" />,
      },
      [WorkflowExecutionState.COMPLETED]: {
        color: 'bg-blue-500',
        text: 'Completed',
        icon: <CheckCircle className="w-4 h-4" />,
      },
      [WorkflowExecutionState.FAILED]: {
        color: 'bg-red-500',
        text: 'Failed',
        icon: <XCircle className="w-4 h-4" />,
      },
      [WorkflowExecutionState.CANCELLED]: {
        color: 'bg-orange-500',
        text: 'Cancelled',
        icon: <Square className="w-4 h-4" />,
      },
    };

    const config = stateConfig[currentExecution.state];

    return (
      <div className="flex items-center gap-2">
        <div className={cn('w-2 h-2 rounded-full', config.color)} />
        <span className="text-sm font-medium">{config.text}</span>
        {config.icon}
      </div>
    );
  };

  if (compactMode) {
    return (
      <div className={cn('bg-white border border-gray-200 rounded-lg p-3', className)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getExecutionStateIndicator()}
            {currentExecution && <PerformanceMetrics executionContext={currentExecution} compact />}
          </div>
          <div className="flex items-center gap-1">
            {!isExecuting && (
              <button
                onClick={handleStart}
                className="p-1 text-green-600 hover:bg-green-50 rounded"
                title="Start execution"
              >
                <Play className="w-4 h-4" />
              </button>
            )}
            {isExecuting && !isPaused && (
              <button
                onClick={handlePause}
                className="p-1 text-yellow-600 hover:bg-yellow-50 rounded"
                title="Pause execution"
              >
                <Pause className="w-4 h-4" />
              </button>
            )}
            {isPaused && (
              <button
                onClick={handleResume}
                className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                title="Resume execution"
              >
                <Play className="w-4 h-4" />
              </button>
            )}
            {isExecuting && (
              <button
                onClick={handleCancel}
                className="p-1 text-red-600 hover:bg-red-50 rounded"
                title="Cancel execution"
              >
                <Square className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={() => setIsVisible(!isVisible)}
              className="p-1 text-gray-600 hover:bg-gray-50 rounded"
              title={isVisible ? 'Hide details' : 'Show details'}
            >
              {isVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('bg-white border border-gray-200 rounded-lg', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">Workflow Monitor</h3>
          {getExecutionStateIndicator()}
        </div>

        {/* Control buttons */}
        <div className="flex items-center gap-2">
          {!isExecuting && (
            <button
              onClick={handleStart}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Play className="w-4 h-4" />
              Start
            </button>
          )}

          {isExecuting && !isPaused && (
            <button
              onClick={handlePause}
              className="flex items-center gap-2 px-3 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
            >
              <Pause className="w-4 h-4" />
              Pause
            </button>
          )}

          {isPaused && (
            <button
              onClick={handleResume}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Play className="w-4 h-4" />
              Resume
            </button>
          )}

          {isExecuting && (
            <button
              onClick={handleCancel}
              className="flex items-center gap-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <Square className="w-4 h-4" />
              Cancel
            </button>
          )}

          {nodeStats.failed > 0 && (
            <button
              onClick={handleRetry}
              className="flex items-center gap-2 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Retry
            </button>
          )}

          <button
            onClick={() => setIsVisible(!isVisible)}
            className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg"
            title={isVisible ? 'Hide details' : 'Show details'}
          >
            {isVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {isVisible && (
        <div className="p-4 space-y-4">
          {/* Progress and status */}
          {currentExecution && (
            <div className="space-y-3">
              {/* Progress bar */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-600">Execution Progress</span>
                  <span className="text-sm font-medium">{Math.round(executionProgress)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${executionProgress}%` }}
                  />
                </div>
              </div>

              {/* Current step */}
              {currentStepDescription && (
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Current Step: </span>
                  {currentStepDescription}
                </div>
              )}

              {/* Node statistics */}
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div className="bg-green-50 p-2 rounded text-center">
                  <div className="font-medium text-green-700">{nodeStats.completed}</div>
                  <div className="text-green-600">Completed</div>
                </div>
                <div className="bg-blue-50 p-2 rounded text-center">
                  <div className="font-medium text-blue-700">{nodeStats.running}</div>
                  <div className="text-blue-600">Running</div>
                </div>
                <div className="bg-red-50 p-2 rounded text-center">
                  <div className="font-medium text-red-700">{nodeStats.failed}</div>
                  <div className="text-red-600">Failed</div>
                </div>
                <div className="bg-gray-50 p-2 rounded text-center">
                  <div className="font-medium text-gray-700">{nodeStats.pending}</div>
                  <div className="text-gray-600">Pending</div>
                </div>
              </div>
            </div>
          )}

          {/* Advanced orchestration monitoring */}
          {currentExecution && showAdvancedMetrics && (
            <div className="space-y-3">
              <ParallelExecutionMonitor branches={currentExecution.parallelBranches} />
              <LoopExecutionMonitor loops={currentExecution.loopContexts} />
              <PerformanceMetrics executionContext={currentExecution} />
            </div>
          )}

          {/* Node execution details */}
          {Object.keys(nodeExecutionData).length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Node Execution Status</h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {Object.entries(nodeExecutionData).map(([nodeId, data]) => (
                  <NodeExecutionStatus
                    key={nodeId}
                    nodeId={nodeId}
                    state={data.state}
                    duration={data.duration}
                    error={data.error}
                    retryCount={data.retryCount}
                    maxRetries={data.maxRetries}
                    onClick={() => setSelectedNodeId(selectedNodeId === nodeId ? null : nodeId)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Selected node details */}
          {selectedNodeId && nodeExecutionData[selectedNodeId] && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <h5 className="font-medium text-gray-900 mb-2">Node Details: {selectedNodeId}</h5>
              <div className="text-sm space-y-1">
                <div>
                  <span className="font-medium">State:</span>{' '}
                  {nodeExecutionData[selectedNodeId].state}
                </div>
                {nodeExecutionData[selectedNodeId].startTime && (
                  <div>
                    <span className="font-medium">Started:</span>{' '}
                    {nodeExecutionData[selectedNodeId].startTime?.toLocaleTimeString()}
                  </div>
                )}
                {nodeExecutionData[selectedNodeId].endTime && (
                  <div>
                    <span className="font-medium">Completed:</span>{' '}
                    {nodeExecutionData[selectedNodeId].endTime?.toLocaleTimeString()}
                  </div>
                )}
                {nodeExecutionData[selectedNodeId].duration && (
                  <div>
                    <span className="font-medium">Duration:</span>{' '}
                    {nodeExecutionData[selectedNodeId].duration}ms
                  </div>
                )}
                {nodeExecutionData[selectedNodeId].output && (
                  <div>
                    <span className="font-medium">Output:</span>
                    <pre className="mt-1 p-2 bg-white border rounded text-xs overflow-x-auto">
                      {JSON.stringify(nodeExecutionData[selectedNodeId].output, null, 2)}
                    </pre>
                  </div>
                )}
                {nodeExecutionData[selectedNodeId].error && (
                  <div>
                    <span className="font-medium text-red-600">Error:</span>
                    <div className="mt-1 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                      {nodeExecutionData[selectedNodeId].error}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
