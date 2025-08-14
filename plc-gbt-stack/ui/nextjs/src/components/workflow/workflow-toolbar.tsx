'use client';

import { IndustrialNodeType, useWorkflowStore } from '@/lib/stores/workflow-store';
import { cn } from '@/lib/utils/cn';
import {
  AlertTriangle,
  Brain,
  Code,
  Cpu,
  Database,
  Download,
  FileSpreadsheet,
  FileText,
  FolderOpen,
  GitBranch,
  Grid,
  Layout,
  LayoutGrid,
  List,
  Maximize2,
  Network,
  Pause,
  Play,
  RefreshCw,
  Save,
  Settings,
  Square,
  Target,
  TestTube,
  Upload,
  Wrench,
  Zap,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import React, { useState } from 'react';

interface NodePaletteItem {
  type: IndustrialNodeType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  category: string;
  description: string;
}

const nodePalette: NodePaletteItem[] = [
  {
    type: 'plc-input',
    label: 'PLC Input',
    icon: RefreshCw,
    color: '#10B981',
    category: 'I/O',
    description: 'Digital or analog input from PLC',
  },
  {
    type: 'plc-output',
    label: 'PLC Output',
    icon: GitBranch,
    color: '#EF4444',
    category: 'I/O',
    description: 'Digital or analog output to PLC',
  },
  {
    type: 'pid-controller',
    label: 'PID Controller',
    icon: Cpu,
    color: '#8B5CF6',
    category: 'Control',
    description: 'Proportional-Integral-Derivative controller',
  },
  {
    type: 'hmi-display',
    label: 'HMI Display',
    icon: AlertTriangle,
    color: '#8B5CF6',
    category: 'Interface',
    description: 'Human-machine interface display',
  },
  {
    type: 'data-logger',
    label: 'Data Logger',
    icon: GitBranch,
    color: '#06B6D4',
    category: 'Data',
    description: 'Historical data logging and storage',
  },
  {
    type: 'alarm-handler',
    label: 'Alarm Handler',
    icon: AlertTriangle,
    color: '#F59E0B',
    category: 'Safety',
    description: 'Process alarm management',
  },
  {
    type: 'modbus-client',
    label: 'Modbus Client',
    icon: Wrench,
    color: '#EC4899',
    category: 'Communication',
    description: 'Modbus TCP/RTU client connection',
  },
  {
    type: 'opc-server',
    label: 'OPC Server',
    icon: Code,
    color: '#84CC16',
    category: 'Communication',
    description: 'OPC-UA server interface',
  },
  {
    type: 'custom-logic',
    label: 'Custom Logic',
    icon: AlertTriangle,
    color: '#F97316',
    category: 'Logic',
    description: 'Custom logic block with scripting',
  },
  {
    type: 'n8n-workflow',
    label: 'N8N Workflow',
    icon: Layout,
    color: '#8B5CF6',
    category: 'Integration',
    description: 'N8N automation workflow',
  },
  // ML Algorithm nodes (based on MPC-overview.md)
  {
    type: 'narx-neural-network',
    label: 'NARX Neural Network',
    icon: Brain,
    color: '#3B82F6',
    category: 'ML Algorithm',
    description: 'Nonlinear AutoRegressive with eXogenous inputs for complex process dynamics',
  },
  {
    type: 'gaussian-process-regression',
    label: 'Gaussian Process Regression',
    icon: Target,
    color: '#3B82F6',
    category: 'ML Algorithm',
    description: 'GPR for uncertainty quantification and probabilistic predictions',
  },
  {
    type: 'lstm-model',
    label: 'LSTM Model',
    icon: RefreshCw,
    color: '#3B82F6',
    category: 'ML Algorithm',
    description: 'Long Short-Term Memory networks for time series prediction',
  },
  {
    type: 'sindy-identifier',
    label: 'SINDy Identifier',
    icon: Code,
    color: '#3B82F6',
    category: 'ML Algorithm',
    description: 'Sparse Identification of Nonlinear Dynamics for physics-ML fusion',
  },
  {
    type: 'reinforcement-learning',
    label: 'Reinforcement Learning',
    icon: Brain,
    color: '#3B82F6',
    category: 'ML Algorithm',
    description: 'DDPG, SAC, TD3 algorithms for adaptive control',
  },
  // MPC nodes (based on MPC-overview.md)
  {
    type: 'mpc-controller',
    label: 'MPC Controller',
    icon: Cpu,
    color: '#8B5CF6',
    category: 'MPC',
    description: 'Model Predictive Control with receding horizon optimization',
  },
  {
    type: 'kalman-filter',
    label: 'Kalman Filter',
    icon: Target,
    color: '#8B5CF6',
    category: 'MPC',
    description: 'State estimation with Riccati-solved gains for process variables',
  },
  {
    type: 'quadratic-programming',
    label: 'Quadratic Programming',
    icon: Zap,
    color: '#8B5CF6',
    category: 'MPC',
    description: 'QP solver for constrained optimization in real-time control',
  },
  {
    type: 'subspace-identification',
    label: 'Subspace ID (N4SID)',
    icon: Network,
    color: '#8B5CF6',
    category: 'MPC',
    description: 'N4SID/MOESP for MIMO system identification from data',
  },
  {
    type: 'imc-controller',
    label: 'IMC Controller',
    icon: Settings,
    color: '#8B5CF6',
    category: 'MPC',
    description: 'Internal Model Control for robust feedforward compensation',
  },
  // Model fine-tuning nodes (based on MPC-overview.md)
  {
    type: 'arx-armax-identifier',
    label: 'ARX/ARMAX Identifier',
    icon: RefreshCw,
    color: '#06B6D4',
    category: 'Model fine-tuning',
    description: 'AutoRegressive with eXogenous inputs for linear system ID',
  },
  {
    type: 'genetic-algorithm',
    label: 'Genetic Algorithm',
    icon: Code,
    color: '#06B6D4',
    category: 'Model fine-tuning',
    description: 'GA optimization for non-differentiable controller tuning',
  },
  {
    type: 'recursive-least-squares',
    label: 'Recursive Least Squares',
    icon: Target,
    color: '#06B6D4',
    category: 'Model fine-tuning',
    description: 'RLS for online parameter estimation and adaptation',
  },
  {
    type: 'model-validation',
    label: 'Model Validation',
    icon: TestTube,
    color: '#06B6D4',
    category: 'Model fine-tuning',
    description: 'FIT percentage and cross-validation for model quality',
  },
  {
    type: 'pilco-pets',
    label: 'PILCO/PETS',
    icon: Brain,
    color: '#06B6D4',
    category: 'Model fine-tuning',
    description: 'Probabilistic model-based RL for sample-efficient learning',
  },
  // Testing nodes (based on MPC-overview.md)
  {
    type: 'prbs-generator',
    label: 'PRBS Generator',
    icon: TestTube,
    color: '#10B981',
    category: 'Testing',
    description: 'Pseudo-Random Binary Sequence for system identification testing',
  },
  {
    type: 'relay-feedback-test',
    label: 'Relay Feedback Test',
    icon: RefreshCw,
    color: '#10B981',
    category: 'Testing',
    description: 'Auto-tuning PID via relay-induced limit cycles (Ku, Tu)',
  },
  {
    type: 'step-response-analyzer',
    label: 'Step Response Analyzer',
    icon: Target,
    color: '#10B981',
    category: 'Testing',
    description: 'Open-loop step testing for process characterization',
  },
  {
    type: 'distillation-simulator',
    label: 'Distillation Simulator',
    icon: Cpu,
    color: '#10B981',
    category: 'Testing',
    description: 'Process simulation for spirits manufacturing and validation',
  },
  {
    type: 'performance-metrics',
    label: 'Performance Metrics',
    icon: Network,
    color: '#10B981',
    category: 'Testing',
    description: 'ISE, MSE, MAE analysis for controller performance validation',
  },
  // Data Sources nodes
  {
    type: 'postgresql-connector',
    label: 'PostgreSQL Connector',
    icon: Database,
    color: '#9333EA',
    category: 'Data Sources',
    description: 'Connect to PostgreSQL databases for process data storage',
  },
  {
    type: 'redis-connector',
    label: 'Redis Connector',
    icon: Database,
    color: '#9333EA',
    category: 'Data Sources',
    description: 'High-speed Redis cache for real-time data operations',
  },
  {
    type: 'neo4j-connector',
    label: 'Neo4j Connector',
    icon: Network,
    color: '#9333EA',
    category: 'Data Sources',
    description: 'Graph database for knowledge representation and relationships',
  },
  {
    type: 'qdrant-connector',
    label: 'Qdrant Connector',
    icon: Brain,
    color: '#9333EA',
    category: 'Data Sources',
    description: 'Vector database for AI embeddings and similarity search',
  },
  {
    type: 'historian-connector',
    label: 'Historian Connector',
    icon: Database,
    color: '#9333EA',
    category: 'Data Sources',
    description: 'Industrial historian for time-series process data',
  },
  // Data Processing nodes
  {
    type: 'csv-dataset-creator',
    label: 'CSV Dataset Creator',
    icon: FileSpreadsheet,
    color: '#0EA5E9',
    category: 'Data Processing',
    description: 'Transform CSV files into clean pandas DataFrames',
  },
  {
    type: 'excel-dataset-creator',
    label: 'Excel Dataset Creator',
    icon: FileSpreadsheet,
    color: '#0EA5E9',
    category: 'Data Processing',
    description: 'Process Excel workbooks into structured datasets',
  },
  {
    type: 'data-cleaner',
    label: 'Data Cleaner',
    icon: RefreshCw,
    color: '#0EA5E9',
    category: 'Data Processing',
    description: 'Handle missing values, outliers, and data quality issues',
  },
  {
    type: 'feature-engineer',
    label: 'Feature Engineer',
    icon: Code,
    color: '#0EA5E9',
    category: 'Data Processing',
    description: 'Create derived features and transform variables for ML',
  },
  {
    type: 'time-series-processor',
    label: 'Time Series Processor',
    icon: Target,
    color: '#0EA5E9',
    category: 'Data Processing',
    description: 'Specialized processing for time-series industrial data',
  },
  // Reporting nodes
  {
    type: 'dashboard-generator',
    label: 'Dashboard Generator',
    icon: LayoutGrid,
    color: '#F59E0B',
    category: 'Reporting',
    description: 'Create interactive dashboards for process monitoring',
  },
  {
    type: 'pdf-report-generator',
    label: 'PDF Report Generator',
    icon: FileText,
    color: '#F59E0B',
    category: 'Reporting',
    description: 'Generate automated PDF reports with charts and analytics',
  },
  {
    type: 'email-notifier',
    label: 'Email Notifier',
    icon: AlertTriangle,
    color: '#F59E0B',
    category: 'Reporting',
    description: 'Send automated email alerts and reports',
  },
  {
    type: 'chart-generator',
    label: 'Chart Generator',
    icon: Target,
    color: '#F59E0B',
    category: 'Reporting',
    description: 'Create charts and visualizations for process data',
  },
  {
    type: 'kpi-calculator',
    label: 'KPI Calculator',
    icon: Network,
    color: '#F59E0B',
    category: 'Reporting',
    description: 'Calculate and track key performance indicators',
  },
];

// Enhanced category system with metadata
interface CategoryInfo {
  readonly id: string;
  readonly label: string;
  readonly description: string;
  readonly color: string;
}

const categoryInfo: ReadonlyArray<CategoryInfo> = [
  { id: 'All', label: 'All', description: 'Show all available nodes', color: '#6B7280' },
  { id: 'I/O', label: 'I/O', description: 'Input/Output operations', color: '#10B981' },
  { id: 'Control', label: 'Control', description: 'Process control systems', color: '#8B5CF6' },
  {
    id: 'Interface',
    label: 'Interface',
    description: 'User interface components',
    color: '#F59E0B',
  },
  { id: 'Data', label: 'Data', description: 'Data processing and storage', color: '#06B6D4' },
  { id: 'Safety', label: 'Safety', description: 'Safety and alarm systems', color: '#EF4444' },
  {
    id: 'Communication',
    label: 'Communication',
    description: 'Network and protocol handlers',
    color: '#EC4899',
  },
  { id: 'Logic', label: 'Logic', description: 'Custom logic and scripting', color: '#F97316' },
  {
    id: 'Integration',
    label: 'Integration',
    description: 'External system integration',
    color: '#84CC16',
  },
  {
    id: 'ML Algorithm',
    label: 'ML Algorithm',
    description: 'Machine learning algorithms and models',
    color: '#3B82F6',
  },
  { id: 'MPC', label: 'MPC', description: 'Model Predictive Control systems', color: '#8B5CF6' },
  {
    id: 'Model fine-tuning',
    label: 'Model fine-tuning',
    description: 'AI model training and optimization',
    color: '#06B6D4',
  },
  {
    id: 'Testing',
    label: 'Testing',
    description: 'Testing and validation tools',
    color: '#10B981',
  },
  {
    id: 'Data Sources',
    label: 'Data Sources',
    description: 'Database connectors and data input systems',
    color: '#9333EA',
  },
  {
    id: 'Data Processing',
    label: 'Data Processing',
    description: 'Dataset creation and data transformation tools',
    color: '#0EA5E9',
  },
  {
    id: 'Reporting',
    label: 'Reporting',
    description: 'Analytics and reporting output systems',
    color: '#F59E0B',
  },
] as const;

// Node view mode types following AI Task Orchestrator strict typing
type NodeViewMode = 'standard' | 'mini' | 'list';

interface ViewModeConfig {
  readonly id: NodeViewMode;
  readonly label: string;
  readonly icon: React.ComponentType<{ className?: string }>;
  readonly description: string;
}

const VIEW_MODES: ReadonlyArray<ViewModeConfig> = [
  {
    id: 'standard',
    label: 'Standard Cards',
    icon: LayoutGrid,
    description: 'Default card view with full details',
  },
  {
    id: 'mini',
    label: 'Mini Cards',
    icon: Grid,
    description: 'Compact card view with reduced details',
  },
  {
    id: 'list',
    label: 'List View',
    icon: List,
    description: 'Dense list view for many nodes',
  },
] as const;

export function WorkflowToolbar() {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showNodePalette, setShowNodePalette] = useState(true);
  const [nodeViewMode, setNodeViewMode] = useState<NodeViewMode>('standard');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

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
  } = useWorkflowStore();

  // Enhanced filtering with node count calculations and intelligent view mode defaults
  const filteredNodes =
    selectedCategory === 'All'
      ? nodePalette
      : nodePalette.filter(node => node.category === selectedCategory);

  // Intelligent default view mode based on AI Task Orchestrator methodology
  const getDefaultViewMode = (category: string, nodeCount: number): NodeViewMode => {
    if (category === 'All' || nodeCount > 10) {
      return 'list'; // Default to list for 'All' or categories with >10 nodes
    }
    return 'standard'; // Default to standard for smaller categories
  };

  // Auto-adjust view mode when category changes
  React.useEffect(() => {
    const nodeCount = getCategoryNodeCount(selectedCategory);
    const defaultMode = getDefaultViewMode(selectedCategory, nodeCount);
    setNodeViewMode(defaultMode);
  }, [selectedCategory]);

  // Calculate node count for each category for display badges
  const getCategoryNodeCount = (categoryId: string): number => {
    if (categoryId === 'All') return nodePalette.length;
    return nodePalette.filter(node => node.category === categoryId).length;
  };

  // Get category color for visual feedback
  const getCategoryColor = (categoryId: string): string => {
    const category = categoryInfo.find(cat => cat.id === categoryId);
    return category?.color || '#6B7280';
  };

  const handleDragStart = (event: React.DragEvent, nodeType: IndustrialNodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleSave = () => {
    saveWorkflow();
    // Success notification will be handled by the workflow store
  };

  const handleExport = () => {
    const data = exportWorkflow('json');
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeWorkflow?.name || 'workflow'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => {
        const content = e.target?.result as string;
        try {
          const data = JSON.parse(content);
          importWorkflow(data);
        } catch (error) {
          console.error('Failed to parse workflow file:', error);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleOpenWorkflowDirectory = async () => {
    try {
      // Call the API to get the workflows directory path and open it
      const response = await fetch('/api/v1/workflows?action=open-directory', {
        method: 'POST',
      });

      if (!response.ok) {
        console.error('Failed to open workflow directory');
      }
    } catch (error) {
      console.error('Error opening workflow directory:', error);
    }
  };

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
            <Upload className="w-4 h-4" />
          </button>

          <button
            onClick={handleExport}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Export Workflow"
          >
            <Download className="w-4 h-4" />
          </button>

          <button
            onClick={handleOpenWorkflowDirectory}
            className="p-2 text-gray-300 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            title="Open Workflows Folder"
          >
            <FolderOpen className="w-4 h-4" />
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
          <div className="text-sm text-gray-400">{activeWorkflow?.name || 'Untitled Workflow'}</div>

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
          {/* Enhanced Category Tabs with Visual Feedback */}
          <div className="overflow-x-auto mb-4 scrollbar-thin scrollbar-track-[#2d2d2d] scrollbar-thumb-[#505050] hover:scrollbar-thumb-[#606060] [&::-webkit-scrollbar]:h-1.5 [&::-webkit-scrollbar-track]:h-1.5 [&::-webkit-scrollbar-thumb]:h-1.5">
            <div className="flex items-center gap-2 min-w-fit">
              {categoryInfo.map(category => {
                const nodeCount = getCategoryNodeCount(category.id);
                const isSelected = selectedCategory === category.id;
                const categoryColor = getCategoryColor(category.id);

                return (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={cn(
                      'group relative flex items-center gap-2 px-3 py-2 text-xs rounded-lg transition-all duration-200 whitespace-nowrap',
                      'border border-transparent hover:border-[#505050] focus:outline-none focus:ring-2 focus:ring-blue-500',
                      isSelected
                        ? 'bg-[#404040] text-white border-[#505050] shadow-sm'
                        : 'text-gray-400 hover:text-white hover:bg-[#353535]'
                    )}
                    title={category.description}
                    style={{
                      borderLeftColor: isSelected ? categoryColor : 'transparent',
                      borderLeftWidth: isSelected ? '3px' : '0px',
                    }}
                  >
                    {/* Category label */}
                    <span className="font-medium">{category.label}</span>

                    {/* Node count badge */}
                    <span
                      className={cn(
                        'inline-flex items-center justify-center min-w-[18px] h-4 px-1.5 rounded-full text-[10px] font-medium transition-colors',
                        isSelected
                          ? 'bg-white/20 text-white'
                          : 'bg-gray-600/50 text-gray-300 group-hover:bg-gray-500/60 group-hover:text-white'
                      )}
                    >
                      {nodeCount}
                    </span>

                    {/* Active indicator dot */}
                    {isSelected && (
                      <div
                        className="absolute -top-1 -right-1 w-2 h-2 rounded-full"
                        style={{ backgroundColor: categoryColor }}
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* View Mode Selector */}
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-gray-400">
              Showing {filteredNodes.length} node{filteredNodes.length !== 1 ? 's' : ''}
            </div>
            <div className="flex items-center gap-1">
              {VIEW_MODES.map(mode => (
                <button
                  key={mode.id}
                  onClick={() => setNodeViewMode(mode.id)}
                  className={cn(
                    'p-1.5 rounded transition-colors text-xs flex items-center gap-1',
                    nodeViewMode === mode.id
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                      : 'text-gray-400 hover:text-white hover:bg-[#3d3d3d] border border-transparent'
                  )}
                  title={mode.description}
                  aria-label={`Switch to ${mode.label}`}
                >
                  <mode.icon className="w-3 h-3" />
                  <span className="hidden sm:inline">{mode.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Enhanced Node Palette with Scrollable Container */}
          <div className="relative">
            <div
              className={cn(
                'overflow-y-auto overflow-x-hidden',
                'max-h-[120px]', // Reduced by 70% from 400px to 120px for more canvas space
                'scrollbar-thin scrollbar-track-[#2d2d2d] scrollbar-thumb-[#505050] hover:scrollbar-thumb-[#606060]'
              )}
            >
              {nodeViewMode === 'list' ? (
                /* List View - Dense layout for many nodes */
                <div className="space-y-1">
                  {filteredNodes.map(node => (
                    <div
                      key={node.type}
                      role="button"
                      tabIndex={isReadOnly ? -1 : 0}
                      draggable={!isReadOnly}
                      onDragStart={e => handleDragStart(e, node.type)}
                      onKeyDown={e => {
                        if (!isReadOnly && (e.key === 'Enter' || e.key === ' ')) {
                          e.preventDefault();
                          handleDragStart(e as unknown as React.DragEvent, node.type);
                        }
                      }}
                      className={cn(
                        'flex items-center gap-3 p-2 rounded border border-[#404040] transition-all duration-200',
                        'focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-400',
                        isReadOnly
                          ? 'opacity-50 cursor-not-allowed'
                          : 'cursor-grab hover:border-[#505050] hover:bg-[#3d3d3d] group active:cursor-grabbing'
                      )}
                      title={`${node.description} - Drag to canvas`}
                      aria-label={`Add ${node.label} node to workflow`}
                    >
                      <node.icon className="w-4 h-4 text-white flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-gray-300 font-medium truncate">
                          {node.label}
                        </div>
                        <div className="text-xs text-gray-500 truncate">{node.description}</div>
                      </div>
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: node.color }}
                        />
                        <span className="text-xs text-gray-500">{node.category}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                /* Card Views - Standard and Mini */
                <div
                  className={cn(
                    'grid gap-2',
                    nodeViewMode === 'mini'
                      ? 'grid-cols-6' // More columns for mini cards
                      : 'grid-cols-4' // Reduced from 5 to 4 for better sizing
                  )}
                >
                  {filteredNodes.map(node => (
                    <div
                      key={node.type}
                      role="button"
                      tabIndex={isReadOnly ? -1 : 0}
                      draggable={!isReadOnly}
                      onDragStart={e => handleDragStart(e, node.type)}
                      onKeyDown={e => {
                        if (!isReadOnly && (e.key === 'Enter' || e.key === ' ')) {
                          e.preventDefault();
                          handleDragStart(e as unknown as React.DragEvent, node.type);
                        }
                      }}
                      className={cn(
                        'flex flex-col items-center rounded-lg border border-[#404040] transition-all duration-200',
                        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400',
                        nodeViewMode === 'mini' ? 'p-2' : 'p-3', // Smaller padding for mini
                        isReadOnly
                          ? 'opacity-50 cursor-not-allowed'
                          : 'cursor-grab hover:border-[#505050] hover:bg-[#3d3d3d] hover:shadow-sm group active:cursor-grabbing'
                      )}
                      title={`${node.description} - Drag to canvas or press Enter/Space to add`}
                      aria-label={`Add ${node.label} node to workflow`}
                    >
                      {/* Node icon with size adjusted for view mode */}
                      <node.icon
                        className={cn(
                          'transition-all duration-200 text-white',
                          nodeViewMode === 'mini'
                            ? 'w-4 h-4 mb-1' // Smaller icon for mini cards
                            : 'w-5 h-5 mb-2', // Reduced from w-6 h-6 for 50% smaller
                          !isReadOnly && 'group-hover:scale-110 group-hover:drop-shadow-sm'
                        )}
                      />

                      {/* Node label with adjusted text size */}
                      <span
                        className={cn(
                          'text-gray-300 text-center leading-tight font-medium',
                          nodeViewMode === 'mini'
                            ? 'text-xs' // Keep small text for mini
                            : 'text-xs' // Consistent text size
                        )}
                      >
                        {node.label}
                      </span>

                      {/* Category badge - hidden in mini mode for space */}
                      {nodeViewMode !== 'mini' && (
                        <div className="flex items-center mt-1 gap-1">
                          <div
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: node.color }}
                          />
                          <span className="text-xs text-gray-500">{node.category}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
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
  );
}
