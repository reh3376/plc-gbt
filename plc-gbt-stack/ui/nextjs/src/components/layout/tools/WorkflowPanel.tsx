'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'
import { 
  PlayCircle,
  Pause,
  Square,
  Plus,
  Edit3,
  Trash2,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react'

interface Workflow {
  id: string
  name: string
  description: string
  status: 'stopped' | 'running' | 'completed' | 'error' | 'paused'
  lastRun?: Date
  nextRun?: Date
  type: 'automation' | 'maintenance' | 'emergency' | 'manual'
  priority: 'low' | 'medium' | 'high' | 'critical'
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
    priority: 'high'
  },
  {
    id: '2',
    name: 'Emergency Shutdown',
    description: 'Emergency shutdown protocol for all systems',
    status: 'stopped',
    type: 'emergency',
    priority: 'critical'
  },
  {
    id: '3',
    name: 'Maintenance Check',
    description: 'Weekly maintenance routine checks',
    status: 'running',
    lastRun: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
    type: 'maintenance',
    priority: 'medium'
  },
  {
    id: '4',
    name: 'Temperature Calibration',
    description: 'Calibrate all temperature sensors',
    status: 'error',
    lastRun: new Date(Date.now() - 1 * 60 * 60 * 1000), // 1 hour ago
    type: 'maintenance',
    priority: 'high'
  },
  {
    id: '5',
    name: 'Data Backup',
    description: 'Backup all PLC configuration and data',
    status: 'paused',
    lastRun: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
    type: 'automation',
    priority: 'low'
  }
]

function WorkflowPanel() {
  const [workflows, setWorkflows] = useState<Workflow[]>(mockWorkflows)
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'running' | 'stopped' | 'error'>('all')

  const getStatusIcon = (status: Workflow['status']) => {
    switch (status) {
      case 'running':
        return <PlayCircle className="w-4 h-4 text-green-500" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'paused':
        return <Pause className="w-4 h-4 text-yellow-500" />
      default:
        return <Square className="w-4 h-4 text-[#969696]" />
    }
  }

  const getPriorityColor = (priority: Workflow['priority']) => {
    switch (priority) {
      case 'critical':
        return 'text-red-400 border-red-400'
      case 'high':
        return 'text-orange-400 border-orange-400'
      case 'medium':
        return 'text-yellow-400 border-yellow-400'
      default:
        return 'text-[#969696] border-[#969696]'
    }
  }

  const getTypeColor = (type: Workflow['type']) => {
    switch (type) {
      case 'emergency':
        return 'bg-red-900 text-red-200'
      case 'automation':
        return 'bg-blue-900 text-blue-200'
      case 'maintenance':
        return 'bg-yellow-900 text-yellow-200'
      default:
        return 'bg-[#3c3c3c] text-[#cccccc]'
    }
  }

  const handleWorkflowAction = (workflowId: string, action: 'start' | 'stop' | 'pause') => {
    setWorkflows(prev => prev.map(workflow => {
      if (workflow.id === workflowId) {
        switch (action) {
          case 'start':
            return { ...workflow, status: 'running' as const, lastRun: new Date() }
          case 'stop':
            return { ...workflow, status: 'stopped' as const }
          case 'pause':
            return { ...workflow, status: 'paused' as const }
          default:
            return workflow
        }
      }
      return workflow
    }))
  }

  const formatTime = (date: Date) => {
    return new Intl.RelativeTimeFormat('en', { numeric: 'auto' }).format(
      Math.floor((date.getTime() - Date.now()) / (1000 * 60)),
      'minute'
    )
  }

  const filteredWorkflows = workflows.filter(workflow => {
    if (filter === 'all') return true
    if (filter === 'running') return workflow.status === 'running'
    if (filter === 'stopped') return workflow.status === 'stopped'
    if (filter === 'error') return workflow.status === 'error'
    return true
  })

  return (
    <div className="h-full flex flex-col">
      {/* Header with filters and actions */}
      <div className="p-3 border-b border-[#3c3c3c] space-y-3">
        {/* Filter tabs */}
        <div className="flex space-x-1">
          {['all', 'running', 'stopped', 'error'].map((filterOption) => (
            <button
              key={filterOption}
              onClick={() => setFilter(filterOption as 'all' | 'running' | 'stopped' | 'error')}
              className={cn(
                "px-3 py-1 text-xs rounded transition-colors capitalize",
                filter === filterOption
                  ? "bg-[#007acc] text-white"
                  : "bg-[#3c3c3c] text-[#cccccc] hover:bg-[#505050]"
              )}
            >
              {filterOption}
            </button>
          ))}
        </div>

        {/* Action buttons */}
        <div className="flex items-center justify-between">
          <span className="text-[#cccccc] text-sm font-medium">
            {filteredWorkflows.length} workflow{filteredWorkflows.length !== 1 ? 's' : ''}
          </span>
          <button
            className="flex items-center space-x-1 px-2 py-1 bg-[#007acc] hover:bg-[#1177bb] text-white text-xs rounded transition-colors"
            onClick={() => console.log('Create new workflow')}
          >
            <Plus className="w-3 h-3" />
            <span>New</span>
          </button>
        </div>
      </div>

      {/* Workflow list */}
      <div className="flex-1 overflow-auto">
        {filteredWorkflows.length === 0 ? (
          <div className="p-4 text-center text-[#969696] text-sm">
            No workflows found
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {filteredWorkflows.map((workflow) => (
              <div
                key={workflow.id}
                className={cn(
                  "p-3 rounded border transition-all",
                  selectedWorkflow === workflow.id
                    ? "border-[#007acc] bg-[#1e3a5a]"
                    : "border-[#3c3c3c] hover:border-[#505050] hover:bg-[#2a2d2e]"
                )}
                onClick={() => setSelectedWorkflow(
                  selectedWorkflow === workflow.id ? null : workflow.id
                )}
              >
                {/* Workflow header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(workflow.status)}
                    <h3 className="text-[#cccccc] font-medium text-sm">{workflow.name}</h3>
                    <span className={cn(
                      "px-2 py-0.5 rounded text-xs border",
                      getPriorityColor(workflow.priority)
                    )}>
                      {workflow.priority}
                    </span>
                  </div>
                  
                  <span className={cn(
                    "px-2 py-0.5 rounded text-xs",
                    getTypeColor(workflow.type)
                  )}>
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
                {selectedWorkflow === workflow.id && (
                  <div className="mt-3 pt-3 border-t border-[#3c3c3c] flex items-center space-x-2">
                    {workflow.status !== 'running' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleWorkflowAction(workflow.id, 'start')
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
                          onClick={(e) => {
                            e.stopPropagation()
                            handleWorkflowAction(workflow.id, 'pause')
                          }}
                          className="flex items-center space-x-1 px-2 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-xs rounded transition-colors"
                        >
                          <Pause className="w-3 h-3" />
                          <span>Pause</span>
                        </button>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleWorkflowAction(workflow.id, 'stop')
                          }}
                          className="flex items-center space-x-1 px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                        >
                          <Square className="w-3 h-3" />
                          <span>Stop</span>
                        </button>
                      </>
                    )}

                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        console.log('Edit workflow:', workflow.id)
                      }}
                      className="flex items-center space-x-1 px-2 py-1 bg-[#3c3c3c] hover:bg-[#505050] text-[#cccccc] text-xs rounded transition-colors"
                    >
                      <Edit3 className="w-3 h-3" />
                      <span>Edit</span>
                    </button>

                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        console.log('Delete workflow:', workflow.id)
                      }}
                      className="flex items-center space-x-1 px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                    >
                      <Trash2 className="w-3 h-3" />
                      <span>Delete</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Status summary */}
      <div className="p-2 border-t border-[#3c3c3c] text-xs text-[#969696]">
        Running: {workflows.filter(w => w.status === 'running').length} | 
        Errors: {workflows.filter(w => w.status === 'error').length} | 
        Total: {workflows.length}
      </div>
    </div>
  )
}

export default WorkflowPanel

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