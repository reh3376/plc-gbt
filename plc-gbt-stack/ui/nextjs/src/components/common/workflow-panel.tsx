'use client'

import { Play, Pause, Plus, MoreVertical, FileText, Settings, Trash2, Edit } from 'lucide-react'
import { useWorkflowStore } from '@/lib/stores/workflow-store'
import { cn } from '@/lib/utils/cn'

export function WorkflowPanel() {
  const {
    workflows,
    activeWorkflow,
    createWorkflow,
    loadWorkflow,
    deleteWorkflow,
  } = useWorkflowStore()

  const handleCreateWorkflow = () => {
    createWorkflow({
      name: `Workflow ${workflows.length + 1}`,
      description: 'New industrial automation workflow',
      version: '1.0.0',
      author: 'System User',
      tags: ['automation'],
      category: 'automation'
    })
  }

  const handleLoadWorkflow = (workflowId: string) => {
    loadWorkflow(workflowId)
  }

  const handleDeleteWorkflow = (workflowId: string) => {
    if (confirm('Are you sure you want to delete this workflow?')) {
      deleteWorkflow(workflowId)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'paused': return 'bg-yellow-500'
      case 'draft': return 'bg-gray-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'control': return '⚙️'
      case 'monitoring': return '📊'
      case 'automation': return '🔄'
      case 'integration': return '🔗'
      default: return '📄'
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-2 border-b border-[#3c3c3c]">
        <span className="text-[#cccccc] text-sm font-medium">Workflows</span>
        <button 
          onClick={handleCreateWorkflow}
          className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors"
          title="Create New Workflow"
        >
          <Plus className="w-4 h-4 text-[#cccccc]" />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-2 space-y-1">
        {workflows.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-gray-500">
            <FileText className="w-8 h-8 mb-2" />
            <p className="text-xs text-center">No workflows yet</p>
            <p className="text-xs text-center">Click + to create one</p>
          </div>
        ) : (
          workflows.map((workflow) => (
            <div 
              key={workflow.id} 
              className={cn(
                'flex items-center justify-between p-2 rounded cursor-pointer transition-colors group',
                'hover:bg-[#2a2d2e]',
                activeWorkflow?.id === workflow.id ? 'bg-blue-600/20 border border-blue-600/50' : ''
              )}
              onClick={() => handleLoadWorkflow(workflow.id)}
            >
              <div className="flex items-center space-x-2 flex-1 min-w-0">
                <div className="text-sm">{getCategoryIcon(workflow.category)}</div>
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${getStatusColor('draft')}`} />
                <div className="flex-1 min-w-0">
                  <div className="text-[#cccccc] text-sm truncate">{workflow.name}</div>
                  <div className="text-[#888] text-xs truncate">{workflow.description}</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    // TODO: Open edit dialog
                    console.log('Edit workflow:', workflow.id)
                  }}
                  className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded"
                  title="Edit Workflow"
                >
                  <Edit className="w-3 h-3 text-[#cccccc]" />
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteWorkflow(workflow.id)
                  }}
                  className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded"
                  title="Delete Workflow"
                >
                  <Trash2 className="w-3 h-3 text-red-400" />
                </button>
                
                <button
                  onClick={(e) => e.stopPropagation()}
                  className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded"
                  title="More Options"
                >
                  <MoreVertical className="w-3 h-3 text-[#cccccc]" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Workflow Actions */}
      {activeWorkflow && (
        <div className="border-t border-[#3c3c3c] p-2">
          <div className="text-xs text-gray-400 mb-2">Active: {activeWorkflow.name}</div>
          <div className="flex space-x-1">
            <button className="flex-1 flex items-center justify-center space-x-1 px-2 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-xs">
              <Play className="w-3 h-3" />
              <span>Run</span>
            </button>
            <button className="flex-1 flex items-center justify-center space-x-1 px-2 py-1 bg-yellow-600 hover:bg-yellow-700 text-white rounded text-xs">
              <Pause className="w-3 h-3" />
              <span>Pause</span>
            </button>
            <button className="px-2 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded text-xs">
              <Settings className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
} 