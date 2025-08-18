'use client';

import { useLayoutStore } from '@/lib/stores/layout-store';
import { useWorkflowStore } from '@/lib/stores/workflow-store';
import { cn } from '@/lib/utils/cn';
import {
  CheckCircle,
  ChevronDown,
  Clock,
  Edit3,
  FolderPlus,
  Grid3X3,
  List,
  Minimize2,
  Pause,
  PlayCircle,
  Square,
  Trash2,
  XCircle,
} from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';

interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'stopped' | 'running' | 'completed' | 'error' | 'paused';
  lastRun?: Date;
  nextRun?: Date;
  type: 'automation' | 'maintenance' | 'emergency' | 'manual';
  priority: 'low' | 'medium' | 'high' | 'critical';
}

type ViewMode = 'icons' | 'mini' | 'list';

interface WorkflowMonitorState {
  monitoredWorkflows: Workflow[];
  availableWorkflows: Workflow[];
  viewMode: ViewMode;
  selectedWorkflow: string | null;
  filter: 'all' | 'running' | 'stopped' | 'error';
}

const mockWorkflows: Workflow[] = [
  {
    id: '1',
    name: 'Startup Sequence',
    description: 'Automated startup sequence for distillation column',
    status: 'completed',
    lastRun: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    nextRun: new Date(Date.now() + 6 * 60 * 60 * 1000), // 6 hours from now
    type: 'automation',
    priority: 'high',
  },
  {
    id: '2',
    name: 'Emergency Shutdown',
    description: 'Emergency shutdown protocol for all systems',
    status: 'stopped',
    type: 'emergency',
    priority: 'critical',
  },
  {
    id: '3',
    name: 'Maintenance Check',
    description: 'Weekly maintenance routine checks',
    status: 'running',
    lastRun: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
    type: 'maintenance',
    priority: 'medium',
  },
  {
    id: '4',
    name: 'Temperature Calibration',
    description: 'Calibrate all temperature sensors',
    status: 'error',
    lastRun: new Date(Date.now() - 1 * 60 * 60 * 1000), // 1 hour ago
    type: 'maintenance',
    priority: 'high',
  },
  {
    id: '5',
    name: 'Data Backup',
    description: 'Backup all PLC configuration and data',
    status: 'paused',
    lastRun: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
    type: 'automation',
    priority: 'low',
  },
];

// Available workflows that can be added to monitoring
const availableWorkflows: Workflow[] = [
  {
    id: '6',
    name: 'Pressure Relief Sequence',
    description: 'Automated pressure relief for reactor vessel',
    status: 'stopped',
    type: 'automation',
    priority: 'high',
  },
  {
    id: '7',
    name: 'Cooling System Startup',
    description: 'Cold startup sequence for cooling tower',
    status: 'stopped',
    type: 'automation',
    priority: 'medium',
  },
  {
    id: '8',
    name: 'Safety System Test',
    description: 'Comprehensive safety system validation',
    status: 'stopped',
    type: 'maintenance',
    priority: 'critical',
  },
];

function WorkflowPanel() {
  // ===== INTEGRATION WITH WORKFLOW STORE =====
  const { workflows: savedWorkflows, openWorkflowInNewTab } = useWorkflowStore();

  // ===== PERSISTENT STATE MANAGEMENT WITH LOCALSTORAGE =====
  const [monitorState, setMonitorState] = useState<WorkflowMonitorState>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('workflowMonitorState');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);

          // Convert date strings back to Date objects
          const parseWorkflowDates = (workflows: Workflow[]) => {
            return workflows.map(workflow => ({
              ...workflow,
              lastRun: workflow.lastRun ? new Date(workflow.lastRun) : undefined,
              nextRun: workflow.nextRun ? new Date(workflow.nextRun) : undefined,
            }));
          };

          return {
            monitoredWorkflows: parsed.monitoredWorkflows
              ? parseWorkflowDates(parsed.monitoredWorkflows)
              : mockWorkflows,
            availableWorkflows: parsed.availableWorkflows
              ? parseWorkflowDates(parsed.availableWorkflows)
              : availableWorkflows,
            viewMode: parsed.viewMode || 'icons',
            selectedWorkflow: parsed.selectedWorkflow || null,
            filter: parsed.filter || 'all',
          };
        } catch (error) {
          console.warn('Failed to parse saved workflow monitor state:', error);
        }
      }
    }
    return {
      monitoredWorkflows: mockWorkflows,
      availableWorkflows: availableWorkflows,
      viewMode: 'icons' as ViewMode,
      selectedWorkflow: null,
      filter: 'all' as const,
    };
  });

  // ===== COMBINE SAVED WORKFLOWS WITH AVAILABLE WORKFLOWS =====
  const combinedAvailableWorkflows = [
    ...availableWorkflows,
    // Convert saved workflows from store to Workflow format
    ...savedWorkflows.map(wf => ({
      id: wf.id,
      name: wf.name,
      description: wf.description,
      status: 'stopped' as const,
      type: wf.category as 'automation' | 'maintenance' | 'emergency' | 'manual',
      priority: 'medium' as const,
    })),
  ];

  const [showDropdown, setShowDropdown] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalWorkflow, setModalWorkflow] = useState<Workflow | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // ===== PERSISTENCE EFFECT =====
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('workflowMonitorState', JSON.stringify(monitorState));
    }
  }, [monitorState]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getStatusIcon = (status: Workflow['status']) => {
    switch (status) {
      case 'running':
        return <PlayCircle className="w-4 h-4 text-green-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'paused':
        return <Pause className="w-4 h-4 text-yellow-500" />;
      default:
        return <Square className="w-4 h-4 text-[#969696]" />;
    }
  };

  const getPriorityColor = (priority: Workflow['priority']) => {
    switch (priority) {
      case 'critical':
        return 'text-red-400 border-red-400';
      case 'high':
        return 'text-orange-400 border-orange-400';
      case 'medium':
        return 'text-yellow-400 border-yellow-400';
      default:
        return 'text-[#969696] border-[#969696]';
    }
  };

  const getTypeColor = (type: Workflow['type']) => {
    switch (type) {
      case 'emergency':
        return 'bg-red-900 text-red-200';
      case 'automation':
        return 'bg-blue-900 text-blue-200';
      case 'maintenance':
        return 'bg-yellow-900 text-yellow-200';
      default:
        return 'bg-[#3c3c3c] text-[#cccccc]';
    }
  };

  // ===== WORKFLOW ACTION HANDLERS =====
  const handleWorkflowAction = (workflowId: string, action: 'start' | 'stop' | 'pause') => {
    const now = new Date();
    setMonitorState(prev => ({
      ...prev,
      monitoredWorkflows: prev.monitoredWorkflows.map(workflow => {
        if (workflow.id === workflowId) {
          switch (action) {
            case 'start':
              return { ...workflow, status: 'running' as const, lastRun: now };
            case 'stop':
              return { ...workflow, status: 'stopped' as const };
            case 'pause':
              return { ...workflow, status: 'paused' as const };
            default:
              return workflow;
          }
        }
        return workflow;
      }),
    }));
  };

  const handleAddToMonitoring = (workflowToAdd: Workflow) => {
    // Check if workflow is already being monitored
    if (!monitorState.monitoredWorkflows.find(w => w.id === workflowToAdd.id)) {
      // Ensure dates are proper Date objects
      const normalizedWorkflow = {
        ...workflowToAdd,
        lastRun: workflowToAdd.lastRun ? new Date(workflowToAdd.lastRun) : undefined,
        nextRun: workflowToAdd.nextRun ? new Date(workflowToAdd.nextRun) : undefined,
      };

      setMonitorState(prev => ({
        ...prev,
        monitoredWorkflows: [...prev.monitoredWorkflows, normalizedWorkflow],
        // Remove from available workflows temporarily (until refresh)
        availableWorkflows: prev.availableWorkflows.filter(w => w.id !== workflowToAdd.id),
      }));
    }
    setShowDropdown(false);
  };

  const handleRemoveFromMonitoring = (workflowId: string) => {
    const removedWorkflow = monitorState.monitoredWorkflows.find(w => w.id === workflowId);
    setMonitorState(prev => ({
      ...prev,
      monitoredWorkflows: prev.monitoredWorkflows.filter(w => w.id !== workflowId),
      // Add back to available workflows with normalized dates
      availableWorkflows: removedWorkflow
        ? [
            ...prev.availableWorkflows,
            {
              ...removedWorkflow,
              lastRun: removedWorkflow.lastRun ? new Date(removedWorkflow.lastRun) : undefined,
              nextRun: removedWorkflow.nextRun ? new Date(removedWorkflow.nextRun) : undefined,
            },
          ].sort((a, b) => a.name.localeCompare(b.name))
        : prev.availableWorkflows,
    }));
  };

  const { setActiveTool, setMainContentMode } = useLayoutStore();

  const handleEditWorkflow = async (workflowId: string) => {
    // COMPREHENSIVE FIX: Complete workflow edit implementation with proper sequencing
    try {
      console.log(`[WorkflowPanel] Starting edit workflow: ${workflowId}`);

      // Step 1: Set the active tool to workflows (left sidebar)
      setActiveTool('workflows');
      console.log('[WorkflowPanel] Set active tool to workflows');

      // Step 2: Set main content mode to workflow (main area)
      setMainContentMode('workflow');
      console.log('[WorkflowPanel] Set main content mode to workflow');

      // Step 3: Small delay to ensure WorkflowCanvas component is mounted
      // This prevents race conditions with component mounting
      await new Promise(resolve => setTimeout(resolve, 100));
      console.log('[WorkflowPanel] Waited for WorkflowCanvas mount');

      // Step 4: Load the workflow data and create tab
      // This will fetch data from API and update the workflow store
      await openWorkflowInNewTab(workflowId);
      console.log(`[WorkflowPanel] Called openWorkflowInNewTab for workflow ${workflowId}`);

      // Step 5: Close any open modals (for mini/list views)
      setModalWorkflow(null);
      console.log('[WorkflowPanel] Closed workflow modal if open');

      // Success log
      console.log(`[WorkflowPanel] Successfully initiated workflow edit for: ${workflowId}`);
    } catch (error) {
      console.error('[WorkflowPanel] Failed to open workflow:', error);
      alert(
        `Failed to open workflow ${workflowId}: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  };

  const handleViewModeChange = (newMode: ViewMode) => {
    setMonitorState(prev => ({ ...prev, viewMode: newMode }));
  };

  const handleFilterChange = (newFilter: 'all' | 'running' | 'stopped' | 'error') => {
    setMonitorState(prev => ({ ...prev, filter: newFilter }));
  };

  // FIXED: Separate selection handler that only manages selection state
  const handleWorkflowSelection = (workflowId: string | null) => {
    setMonitorState(prev => ({
      ...prev,
      selectedWorkflow: prev.selectedWorkflow === workflowId ? null : workflowId,
    }));
  };

  // FIXED: Modal handler that includes selection state management
  const handleModalOpen = (workflow: Workflow) => {
    // Update selection state when opening modal
    setMonitorState(prev => ({
      ...prev,
      selectedWorkflow: workflow.id,
    }));
    setModalWorkflow(workflow);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setModalWorkflow(null);
    // FIXED: Don't clear selection state when modal closes - preserve blue overlay
    // Selection state should persist until user clicks another workflow
  };

  const formatTime = (date: Date | string | undefined) => {
    if (!date) return 'Never';

    let dateObj: Date;
    if (typeof date === 'string') {
      dateObj = new Date(date);
    } else if (date instanceof Date) {
      dateObj = date;
    } else {
      return 'Invalid date';
    }

    // Check if date is valid
    if (isNaN(dateObj.getTime())) {
      return 'Invalid date';
    }

    return new Intl.RelativeTimeFormat('en', { numeric: 'auto' }).format(
      Math.floor((dateObj.getTime() - Date.now()) / (1000 * 60)),
      'minute'
    );
  };

  // ===== COMPUTED VALUES =====
  const filteredWorkflows = monitorState.monitoredWorkflows.filter(workflow => {
    if (monitorState.filter === 'all') return true;
    if (monitorState.filter === 'running') return workflow.status === 'running';
    if (monitorState.filter === 'stopped') return workflow.status === 'stopped';
    if (monitorState.filter === 'error') return workflow.status === 'error';
    return true;
  });

  // Count workflows by status for filter badges
  const statusCounts = {
    all: monitorState.monitoredWorkflows.length,
    running: monitorState.monitoredWorkflows.filter(w => w.status === 'running').length,
    stopped: monitorState.monitoredWorkflows.filter(w => w.status === 'stopped').length,
    error: monitorState.monitoredWorkflows.filter(w => w.status === 'error').length,
  };

  // Available workflows that aren't currently monitored (includes saved workflows from store)
  const availableForMonitoring = combinedAvailableWorkflows.filter(
    aw => !monitorState.monitoredWorkflows.find(mw => mw.id === aw.id)
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header with filters and actions */}
      <div className="p-3 border-b border-[#3c3c3c] space-y-3">
        {/* Filter tabs with counts */}
        <div className="flex space-x-1">
          {(['all', 'running', 'stopped', 'error'] as const).map(filterOption => (
            <button
              key={filterOption}
              onClick={() => handleFilterChange(filterOption)}
              className={cn(
                'px-3 py-1 text-xs rounded transition-colors capitalize flex items-center space-x-1',
                monitorState.filter === filterOption
                  ? 'bg-[#007acc] text-white'
                  : 'bg-[#3c3c3c] text-[#cccccc] hover:bg-[#505050]'
              )}
            >
              <span>{filterOption}</span>
              <span
                className={cn(
                  'px-1.5 py-0.5 rounded text-xs font-bold',
                  monitorState.filter === filterOption
                    ? 'bg-white/20 text-white'
                    : 'bg-[#555555] text-[#cccccc]'
                )}
              >
                {statusCounts[filterOption]}
              </span>
            </button>
          ))}
        </div>

        {/* View mode selector */}
        <div className="flex items-center space-x-1">
          <span className="text-[#969696] text-xs">View:</span>
          <div className="flex space-x-1">
            {[
              { mode: 'icons' as const, icon: Grid3X3, label: 'Icons' },
              { mode: 'mini' as const, icon: Minimize2, label: 'Mini' },
              { mode: 'list' as const, icon: List, label: 'List' },
            ].map(({ mode, icon: Icon, label }) => (
              <button
                key={mode}
                onClick={() => handleViewModeChange(mode)}
                className={cn(
                  'p-1.5 rounded transition-colors',
                  monitorState.viewMode === mode
                    ? 'bg-[#007acc] text-white'
                    : 'bg-[#3c3c3c] text-[#cccccc] hover:bg-[#505050]'
                )}
                title={label}
              >
                <Icon className="w-3 h-3" />
              </button>
            ))}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center justify-between">
          <span className="text-[#cccccc] text-sm font-medium">
            {filteredWorkflows.length} workflow{filteredWorkflows.length !== 1 ? 's' : ''}
          </span>
          <div className="relative" ref={dropdownRef}>
            <button
              className="flex items-center space-x-1 px-2 py-1 bg-[#007acc] hover:bg-[#1177bb] text-white text-xs rounded transition-colors"
              onClick={() => setShowDropdown(!showDropdown)}
            >
              <FolderPlus className="w-3 h-3" />
              <span>Add Workflow</span>
              <ChevronDown className="w-3 h-3" />
            </button>

            {/* Dropdown menu */}
            {showDropdown && (
              <div className="absolute top-full mt-1 right-0 w-64 bg-[#2d2d30] border border-[#3c3c3c] rounded shadow-lg z-50">
                <div className="p-2 border-b border-[#3c3c3c]">
                  <p className="text-xs text-[#cccccc] font-medium">Available Workflows</p>
                </div>
                <div className="max-h-40 overflow-auto">
                  {availableForMonitoring.map(workflow => (
                    <button
                      key={workflow.id}
                      onClick={() => handleAddToMonitoring(workflow)}
                      className="w-full text-left px-3 py-2 hover:bg-[#3c3c3c] transition-colors"
                    >
                      <div className="flex items-center space-x-2">
                        <span
                          className={cn(
                            'px-1.5 py-0.5 rounded text-xs',
                            getPriorityColor(workflow.priority)
                          )}
                        >
                          {workflow.priority}
                        </span>
                        <span className="text-[#cccccc] text-xs font-medium">{workflow.name}</span>
                      </div>
                      <p className="text-[#969696] text-xs mt-1">{workflow.description}</p>
                    </button>
                  ))}
                  {availableForMonitoring.length === 0 && (
                    <div className="px-3 py-2 text-xs text-[#969696]">
                      All available workflows are already being monitored
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Workflow list with scrolling */}
      <div className="flex-1 overflow-y-auto">
        {filteredWorkflows.length === 0 ? (
          <div className="p-4 text-center text-[#969696] text-sm">No workflows found</div>
        ) : (
          <div className={cn('p-2', monitorState.viewMode === 'list' ? 'space-y-1' : 'space-y-2')}>
            {filteredWorkflows.map(workflow => {
              const isSelected = monitorState.selectedWorkflow === workflow.id;

              if (monitorState.viewMode === 'mini') {
                return (
                  <div
                    key={workflow.id}
                    className={cn(
                      'p-2 rounded border transition-all cursor-pointer',
                      isSelected
                        ? 'border-[#007acc] bg-[#1e3a5a]'
                        : 'border-[#3c3c3c] hover:border-[#505050] hover:bg-[#2a2d2e]'
                    )}
                    onClick={() => handleModalOpen(workflow)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={e => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleModalOpen(workflow);
                      }
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(workflow.status)}
                        <span className="text-[#cccccc] text-sm font-medium truncate">
                          {workflow.name}
                        </span>
                      </div>
                      <span
                        className={cn(
                          'px-1.5 py-0.5 rounded text-xs',
                          getPriorityColor(workflow.priority)
                        )}
                      >
                        {workflow.priority}
                      </span>
                    </div>
                  </div>
                );
              }

              if (monitorState.viewMode === 'list') {
                return (
                  <div
                    key={workflow.id}
                    className={cn(
                      'px-3 py-2 rounded border transition-all cursor-pointer flex items-center justify-between',
                      isSelected
                        ? 'border-[#007acc] bg-[#1e3a5a]'
                        : 'border-[#3c3c3c] hover:border-[#505050] hover:bg-[#2a2d2e]'
                    )}
                    onClick={() => handleModalOpen(workflow)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={e => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleModalOpen(workflow);
                      }
                    }}
                  >
                    <div className="flex items-center space-x-3 flex-1">
                      {getStatusIcon(workflow.status)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <h3 className="text-[#cccccc] font-medium text-sm truncate">
                            {workflow.name}
                          </h3>
                          <span
                            className={cn(
                              'px-2 py-0.5 rounded text-xs',
                              getTypeColor(workflow.type)
                            )}
                          >
                            {workflow.type}
                          </span>
                        </div>
                        <p className="text-[#969696] text-xs truncate">{workflow.description}</p>
                      </div>
                    </div>
                    <span
                      className={cn(
                        'px-1.5 py-0.5 rounded text-xs',
                        getPriorityColor(workflow.priority)
                      )}
                    >
                      {workflow.priority}
                    </span>
                  </div>
                );
              }

              // Default standard view
              return (
                <div
                  key={workflow.id}
                  className={cn(
                    'p-3 rounded border transition-all',
                    isSelected
                      ? 'border-[#007acc] bg-[#1e3a5a]'
                      : 'border-[#3c3c3c] hover:border-[#505050] hover:bg-[#2a2d2e]'
                  )}
                  onClick={() => handleWorkflowSelection(workflow.id)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleWorkflowSelection(workflow.id);
                    }
                  }}
                  role="button"
                  tabIndex={0}
                >
                  {/* Workflow header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(workflow.status)}
                      <h3 className="text-[#cccccc] font-medium text-sm">{workflow.name}</h3>
                      <span
                        className={cn(
                          'px-2 py-0.5 rounded text-xs border',
                          getPriorityColor(workflow.priority)
                        )}
                      >
                        {workflow.priority}
                      </span>
                    </div>

                    <span
                      className={cn('px-2 py-0.5 rounded text-xs', getTypeColor(workflow.type))}
                    >
                      {workflow.type}
                    </span>
                  </div>

                  {/* Workflow description */}
                  <p className="text-[#969696] text-xs mb-2">{workflow.description}</p>

                  {/* Workflow timing */}
                  <div className="flex items-center justify-between text-xs text-[#969696]">
                    <div className="flex items-center space-x-4">
                      {workflow.lastRun && (
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>Last: {formatTime(workflow.lastRun)}</span>
                        </div>
                      )}
                      {workflow.nextRun && (
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>Next: {formatTime(workflow.nextRun)}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Workflow actions */}
                  {isSelected && (
                    <div className="mt-3 pt-3 border-t border-[#3c3c3c] flex items-center space-x-2">
                      {workflow.status !== 'running' && (
                        <button
                          onClick={e => {
                            e.stopPropagation();
                            handleWorkflowAction(workflow.id, 'start');
                          }}
                          className="flex items-center space-x-1 px-2 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors"
                        >
                          <PlayCircle className="w-3 h-3" />
                          <span>Start</span>
                        </button>
                      )}

                      {workflow.status === 'running' && (
                        <>
                          <button
                            onClick={e => {
                              e.stopPropagation();
                              handleWorkflowAction(workflow.id, 'pause');
                            }}
                            className="flex items-center space-x-1 px-2 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-xs rounded transition-colors"
                          >
                            <Pause className="w-3 h-3" />
                            <span>Pause</span>
                          </button>

                          <button
                            onClick={e => {
                              e.stopPropagation();
                              handleWorkflowAction(workflow.id, 'stop');
                            }}
                            className="flex items-center space-x-1 px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                          >
                            <Square className="w-3 h-3" />
                            <span>Stop</span>
                          </button>
                        </>
                      )}

                      <button
                        onClick={async e => {
                          e.stopPropagation();
                          await handleEditWorkflow(workflow.id);
                        }}
                        className="flex items-center space-x-1 px-2 py-1 bg-[#3c3c3c] hover:bg-[#505050] text-[#cccccc] text-xs rounded transition-colors"
                      >
                        <Edit3 className="w-3 h-3" />
                        <span>Edit</span>
                      </button>

                      <button
                        onClick={e => {
                          e.stopPropagation();
                          handleRemoveFromMonitoring(workflow.id);
                        }}
                        className="flex items-center space-x-1 px-2 py-1 bg-orange-600 hover:bg-orange-700 text-white text-xs rounded transition-colors"
                        title="Remove from monitoring (workflow will not be deleted)"
                      >
                        <Trash2 className="w-3 h-3" />
                        <span>Remove</span>
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Status summary */}
      <div className="p-2 border-t border-[#3c3c3c] text-xs text-[#969696]">
        Running: {statusCounts.running} | Errors: {statusCounts.error} | Total: {statusCounts.all}
      </div>

      {/* Modal for mini and list view */}
      {showModal && modalWorkflow && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#2d2d30] border border-[#3c3c3c] rounded-lg p-4 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[#cccccc] font-medium text-lg">{modalWorkflow.name}</h3>
              <button
                onClick={handleModalClose}
                className="text-[#969696] hover:text-[#cccccc] transition-colors"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                {getStatusIcon(modalWorkflow.status)}
                <span className="text-[#cccccc] text-sm">Status: {modalWorkflow.status}</span>
                <span
                  className={cn('px-2 py-0.5 rounded text-xs', getTypeColor(modalWorkflow.type))}
                >
                  {modalWorkflow.type}
                </span>
                <span
                  className={cn(
                    'px-2 py-0.5 rounded text-xs border',
                    getPriorityColor(modalWorkflow.priority)
                  )}
                >
                  {modalWorkflow.priority}
                </span>
              </div>

              <p className="text-[#969696] text-sm">{modalWorkflow.description}</p>

              {modalWorkflow.lastRun && (
                <div className="flex items-center space-x-2 text-sm text-[#969696]">
                  <Clock className="w-4 h-4" />
                  <span>Last run: {formatTime(modalWorkflow.lastRun)}</span>
                </div>
              )}

              {modalWorkflow.nextRun && (
                <div className="flex items-center space-x-2 text-sm text-[#969696]">
                  <Clock className="w-4 h-4" />
                  <span>Next run: {formatTime(modalWorkflow.nextRun)}</span>
                </div>
              )}

              <div className="flex items-center space-x-2 pt-3 border-t border-[#3c3c3c]">
                {modalWorkflow.status !== 'running' && (
                  <button
                    onClick={() => {
                      handleWorkflowAction(modalWorkflow.id, 'start');
                      handleModalClose();
                    }}
                    className="flex items-center space-x-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                  >
                    <PlayCircle className="w-4 h-4" />
                    <span>Start</span>
                  </button>
                )}

                {modalWorkflow.status === 'running' && (
                  <>
                    <button
                      onClick={() => {
                        handleWorkflowAction(modalWorkflow.id, 'pause');
                        handleModalClose();
                      }}
                      className="flex items-center space-x-1 px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded transition-colors"
                    >
                      <Pause className="w-4 h-4" />
                      <span>Pause</span>
                    </button>

                    <button
                      onClick={() => {
                        handleWorkflowAction(modalWorkflow.id, 'stop');
                        handleModalClose();
                      }}
                      className="flex items-center space-x-1 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                    >
                      <Square className="w-4 h-4" />
                      <span>Stop</span>
                    </button>
                  </>
                )}

                <button
                  onClick={async () => {
                    await handleEditWorkflow(modalWorkflow.id);
                    handleModalClose();
                  }}
                  className="flex items-center space-x-1 px-3 py-1.5 bg-[#3c3c3c] hover:bg-[#505050] text-[#cccccc] text-sm rounded transition-colors"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>Edit</span>
                </button>

                <button
                  onClick={() => {
                    handleRemoveFromMonitoring(modalWorkflow.id);
                    handleModalClose();
                  }}
                  className="flex items-center space-x-1 px-3 py-1.5 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded transition-colors"
                  title="Remove from monitoring (workflow will not be deleted)"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Remove</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default WorkflowPanel;

/**
 * WorkflowPanel Component
 *
 * @description Workflow management and automation for PLC operations
 * @specification Implements main-ui-spec.md WorkflowPanel tool requirements
 *
 * @features
 * - Workflow status monitoring and control
 * - Priority-based workflow organization
 * - Real-time status updates with visual indicators
 * - Workflow type categorization (automation, maintenance, emergency)
 * - Quick actions for start/stop/pause operations
 * - Filtering and search capabilities
 *
 * @workflowTypes
 * - Automation: Scheduled automated sequences
 * - Maintenance: Routine maintenance procedures
 * - Emergency: Critical safety protocols
 * - Manual: User-initiated workflows
 *
 * @accessibility
 * - Keyboard navigation support
 * - Clear status indicators
 * - Screen reader friendly
 * - Color-coded priority system
 *
 * @performance
 * - Lazy loaded via Suspense
 * - Efficient filtering and state management
 * - Optimized re-renders
 */
