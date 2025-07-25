'use client'

import React, { useState } from 'react'
import {
  Play,
  Pause,
  Square,
  Save,
  Download,
  RefreshCw,
  Layout,
  GitBranch,
  Code,
  Cpu,
  AlertTriangle,
  Settings,
  Wrench,
  ZoomIn,
  ZoomOut,
  Maximize2,
  LayoutGrid,
  Grid
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useWorkflowStore, IndustrialNodeType } from '@/lib/stores/workflow-store'

interface NodePaletteItem {
  type: IndustrialNodeType
  label: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  category: string
  description: string
}

const nodePalette: NodePaletteItem[] = [
  {
    type: 'plc-input',
    label: 'PLC Input',
    icon: RefreshCw,
    color: '#10B981',
    category: 'I/O',
    description: 'Digital or analog input from PLC'
  },
  {
    type: 'plc-output',
    label: 'PLC Output',
    icon: GitBranch,
    color: '#EF4444',
    category: 'I/O',
    description: 'Digital or analog output to PLC'
  },
  {
    type: 'pid-controller',
    label: 'PID Controller',
    icon: Cpu,
    color: '#8B5CF6',
    category: 'Control',
    description: 'Proportional-Integral-Derivative controller'
  },
  {
    type: 'hmi-display',
    label: 'HMI Display',
    icon: AlertTriangle,
    color: '#8B5CF6',
    category: 'Interface',
    description: 'Human-machine interface display'
  },
  {
    type: 'data-logger',
    label: 'Data Logger',
    icon: GitBranch,
    color: '#06B6D4',
    category: 'Data',
    description: 'Historical data logging and storage'
  },
  {
    type: 'alarm-handler',
    label: 'Alarm Handler',
    icon: AlertTriangle,
    color: '#F59E0B',
    category: 'Safety',
    description: 'Process alarm management'
  },
  {
    type: 'modbus-client',
    label: 'Modbus Client',
    icon: Wrench,
    color: '#EC4899',
    category: 'Communication',
    description: 'Modbus TCP/RTU client connection'
  },
  {
    type: 'opc-server',
    label: 'OPC Server',
    icon: Code,
    color: '#84CC16',
    category: 'Communication',
    description: 'OPC-UA server interface'
  },
  {
    type: 'custom-logic',
    label: 'Custom Logic',
    icon: AlertTriangle,
    color: '#F97316',
    category: 'Logic',
    description: 'Custom logic block with scripting'
  },
  {
    type: 'n8n-workflow',
    label: 'N8N Workflow',
    icon: Layout,
    color: '#8B5CF6',
    category: 'Integration',
    description: 'N8N automation workflow'
  },
]

const categories = ['All', 'I/O', 'Control', 'Interface', 'Data', 'Safety', 'Communication', 'Logic', 'Integration']

export function WorkflowToolbar() {
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [showNodePalette, setShowNodePalette] = useState(true)
  const fileInputRef = React.useRef<HTMLInputElement>(null)

  const {
    nodes,
    edges,
    selectedNodes,
    activeWorkflow,
    snapToGrid,
    showMinimap,
    isReadOnly,
    
    saveWorkflow,
    exportWorkflow,
    importWorkflow,
    fitView,
    zoomIn,
    zoomOut,
    resetZoom,
    autoLayoutNodes,
    alignNodes,
    distributeNodes,
    setSnapToGrid,
    toggleMinimap,
  } = useWorkflowStore()

  const filteredNodes = selectedCategory === 'All' 
    ? nodePalette 
    : nodePalette.filter(node => node.category === selectedCategory)

  const handleDragStart = (event: React.DragEvent, nodeType: IndustrialNodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }

  const handleSave = () => {
    saveWorkflow()
    // TODO: Show success notification
  }

  const handleExport = () => {
    const data = exportWorkflow('json')
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${activeWorkflow?.name || 'workflow'}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        try {
          const data = JSON.parse(content)
          importWorkflow(data)
        } catch (error) {
          console.error('Failed to parse workflow file:', error)
        }
      }
      reader.readAsText(file)
    }
  }

  return (
    <div className="bg-[#2d2d2d] border-b border-[#404040] flex flex-col">
      {/* Main Toolbar */}
      <div className="flex items-center justify-between p-2 space-x-2">
        {/* File Operations */}
        <div className="flex items-center space-x-1">
          <button
            onClick={handleSave}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Save Workflow"
            disabled={isReadOnly}
          >
            <Save className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Import Workflow"
            disabled={isReadOnly}
          >
            <Settings className="w-4 h-4" />
          </button>
          
          <button
            onClick={handleExport}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Export Workflow"
          >
            <Download className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-[#404040] mx-2" />
        </div>

        {/* Workflow Controls */}
        <div className="flex items-center space-x-1">
          <button
            className="p-2 text-green-400 hover:text-green-300 hover:bg-[#3d3d3d] rounded transition-colors"
            title="Start Workflow"
            disabled={isReadOnly}
          >
            <Play className="w-4 h-4" />
          </button>
          
          <button
            className="p-2 text-yellow-400 hover:text-yellow-300 hover:bg-[#3d3d3d] rounded transition-colors"
            title="Pause Workflow"
            disabled={isReadOnly}
          >
            <Pause className="w-4 h-4" />
          </button>
          
          <button
            className="p-2 text-red-400 hover:text-red-300 hover:bg-[#3d3d3d] rounded transition-colors"
            title="Stop Workflow"
            disabled={isReadOnly}
          >
            <Square className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-[#404040] mx-2" />
        </div>

        {/* View Controls */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => zoomIn()}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => zoomOut()}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => fitView()}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Fit View"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => resetZoom()}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Reset Zoom"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-[#404040] mx-2" />
        </div>

        {/* Layout Controls */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => autoLayoutNodes('horizontal')}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Auto Layout Horizontal"
            disabled={nodes.length === 0 || isReadOnly}
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => alignNodes('left')}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Align Left"
            disabled={selectedNodes.length < 2 || isReadOnly}
          >
            {/* AlignLeft removed */}
          </button>
          
          <button
            onClick={() => alignNodes('center')}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Align Center"
            disabled={selectedNodes.length < 2 || isReadOnly}
          >
            {/* AlignCenter removed */}
          </button>
          
          <button
            onClick={() => distributeNodes('horizontal')}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Distribute Horizontally"
            disabled={selectedNodes.length < 3 || isReadOnly}
          >
            {/* ArrowRightLeft removed */}
          </button>
          
          <div className="w-px h-6 bg-[#404040] mx-2" />
        </div>

        {/* View Options */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setSnapToGrid(!snapToGrid)}
            className={cn(
              'p-2 rounded transition-colors',
              snapToGrid 
                ? 'text-blue-400 bg-blue-600/20' 
                : 'text-gray-300 hover:text-white hover:bg-[#3d3d3d]'
            )}
            title="Snap to Grid"
          >
            <Grid className="w-4 h-4" />
          </button>
          
          <button
            onClick={toggleMinimap}
            className={cn(
              'p-2 rounded transition-colors',
              showMinimap 
                ? 'text-blue-400 bg-blue-600/20' 
                : 'text-gray-300 hover:text-white hover:bg-[#3d3d3d]'
            )}
            title="Toggle Minimap"
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => setShowNodePalette(!showNodePalette)}
            className={cn(
              'p-2 rounded transition-colors',
              showNodePalette 
                ? 'text-blue-400 bg-blue-600/20' 
                : 'text-gray-300 hover:text-white hover:bg-[#3d3d3d]'
            )}
            title="Toggle Node Palette"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>

        {/* Workflow Info */}
        <div className="flex items-center space-x-3 ml-auto">
          <div className="text-sm text-gray-400">
            {activeWorkflow?.name || 'Untitled Workflow'}
          </div>
          
          <div className="text-xs text-gray-500">
            {nodes.length} nodes, {edges.length} connections
          </div>
          
          {isReadOnly && (
            <div className="px-2 py-1 bg-yellow-600/20 text-yellow-400 text-xs rounded">
              Read Only
            </div>
          )}
        </div>
      </div>

      {/* Node Palette */}
      {showNodePalette && (
        <div className="border-t border-[#404040] p-3">
          {/* Category Tabs */}
          <div className="flex items-center space-x-1 mb-3">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={cn(
                  'px-3 py-1 text-xs rounded transition-colors',
                  selectedCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-[#3d3d3d]'
                )}
              >
                {category}
              </button>
            ))}
          </div>

          {/* Node Palette Grid */}
          <div className="grid grid-cols-5 gap-2">
            {filteredNodes.map((node) => (
              <div
                key={node.type}
                draggable={!isReadOnly}
                onDragStart={(e) => handleDragStart(e, node.type)}
                className={cn(
                  'flex flex-col items-center p-3 rounded-lg border border-[#404040] cursor-grab',
                  'hover:border-[#505050] hover:bg-[#3d3d3d] transition-colors group',
                  isReadOnly && 'opacity-50 cursor-not-allowed'
                )}
                title={node.description}
              >
                <node.icon 
                  className="w-6 h-6 mb-2 group-hover:scale-110 transition-transform text-white" 
                />
                <span className="text-xs text-gray-300 text-center leading-tight">
                  {node.label}
                </span>
                <span className="text-xs text-gray-500 mt-1">
                  {node.category}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".json,.xml"
        onChange={handleImport}
        className="hidden"
      />
    </div>
  )
} 