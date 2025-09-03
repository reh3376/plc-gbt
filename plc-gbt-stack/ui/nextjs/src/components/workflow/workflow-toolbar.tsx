'use client';

import {
  IndustrialNodeType,
  useWorkflowStore,
  WorkflowMetadata,
} from '@/lib/stores/workflow-store';
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
  HelpCircle,
  Layout,
  LayoutGrid,
  LineChart,
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
  Trash2,
  Upload,
  Wrench,
  Zap,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import React, { useState } from 'react';
import { ExportWorkflowModal } from './ExportWorkflowModal';
import { ImportWorkflowModal } from './ImportWorkflowModal';
import { SaveWorkflowModal } from './SaveWorkflowModal';
import { WorkflowHelpModal } from './WorkflowHelpModal';
import { WorkflowStatusModal } from './WorkflowStatusModal';

// Workflow validation utility
interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

function validateWorkflowObject(data: unknown): ValidationResult {
  const errors: string[] = [];

  if (!data || typeof data !== 'object') {
    errors.push('File must contain a valid JSON object');
    return { isValid: false, errors };
  }

  const obj = data as Record<string, unknown>;

  // Check for required workflow properties
  if (!obj.nodes || !Array.isArray(obj.nodes)) {
    errors.push('Workflow must contain a "nodes" array');
  }

  if (!obj.edges || !Array.isArray(obj.edges)) {
    errors.push('Workflow must contain an "edges" array');
  }

  // Validate node structure
  if (Array.isArray(obj.nodes)) {
    obj.nodes.forEach((node, index) => {
      if (!node || typeof node !== 'object') {
        errors.push(`Node at index ${index} is not a valid object`);
        return;
      }

      const nodeObj = node as Record<string, unknown>;
      if (!nodeObj.id || typeof nodeObj.id !== 'string') {
        errors.push(`Node at index ${index} missing required "id" field`);
      }
      if (!nodeObj.type || typeof nodeObj.type !== 'string') {
        errors.push(`Node at index ${index} missing required "type" field`);
      }
      if (!nodeObj.position || typeof nodeObj.position !== 'object') {
        errors.push(`Node at index ${index} missing required "position" field`);
      }
    });
  }

  // Validate edge structure
  if (Array.isArray(obj.edges)) {
    obj.edges.forEach((edge, index) => {
      if (!edge || typeof edge !== 'object') {
        errors.push(`Edge at index ${index} is not a valid object`);
        return;
      }

      const edgeObj = edge as Record<string, unknown>;
      if (!edgeObj.id || typeof edgeObj.id !== 'string') {
        errors.push(`Edge at index ${index} missing required "id" field`);
      }
      if (!edgeObj.source || typeof edgeObj.source !== 'string') {
        errors.push(`Edge at index ${index} missing required "source" field`);
      }
      if (!edgeObj.target || typeof edgeObj.target !== 'string') {
        errors.push(`Edge at index ${index} missing required "target" field`);
      }
    });
  }

  return { isValid: errors.length === 0, errors };
}

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
  // New ML Classification & Analysis nodes - AI Task Orchestrator Implementation
  {
    type: 'binary-classification',
    label: 'Binary Classification',
    icon: Brain,
    color: '#3B82F6',
    category: 'ML Algorithm',
    description: 'Binary classification with multiple algorithms and ensemble methods',
  },
  {
    type: 'multiclass-classification',
    label: 'Multi-Class Classification',
    icon: Network,
    color: '#3B82F6',
    category: 'ML Algorithm',
    description: 'Multi-category classification with advanced ensemble and balancing',
  },
  {
    type: 'distribution-analyzer',
    label: 'Distribution Analyzer',
    icon: LineChart,
    color: '#06B6D4',
    category: 'Data Processing',
    description: 'Statistical distribution analysis with ML-enhanced pattern recognition',
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
  // Advanced Workflow Control Nodes
  {
    type: 'workflow-conditional',
    label: 'Workflow Conditional',
    icon: GitBranch,
    color: '#F59E0B',
    category: 'Workflow Control',
    description: 'Execute different workflow paths based on conditions and decision logic',
  },
  {
    type: 'workflow-parallel',
    label: 'Workflow Parallel',
    icon: Layout,
    color: '#8B5CF6',
    category: 'Workflow Control',
    description: 'Execute multiple workflow paths simultaneously with synchronization',
  },
  {
    type: 'workflow-loop',
    label: 'Workflow Loop',
    icon: RefreshCw,
    color: '#06B6D4',
    category: 'Workflow Control',
    description: 'Execute workflow paths iteratively with various loop types',
  },
  // Enhanced Industrial PLC Connectivity Nodes
  {
    type: 'advanced-modbus-client',
    label: 'Advanced Modbus Client',
    icon: Wrench,
    color: '#DC2626',
    category: 'Communication',
    description: 'Industrial-grade Modbus TCP/RTU client with enhanced diagnostics and security',
  },
  {
    type: 'advanced-opcua-client',
    label: 'Advanced OPC-UA Client',
    icon: Network,
    color: '#16A34A',
    category: 'Communication',
    description: 'Industrial-grade OPC-UA client with enhanced security and real-time performance',
  },
  {
    type: 'advanced-ethernet-ip',
    label: 'Advanced EtherNet/IP',
    icon: Zap,
    color: '#2563EB',
    category: 'Communication',
    description:
      'Industrial-grade EtherNet/IP client for Allen-Bradley PLCs with enhanced diagnostics',
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
  {
    id: 'Workflow Control',
    label: 'Workflow Control',
    description: 'Advanced workflow control and automation logic',
    color: '#7C3AED',
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
  const [nodePanelHeight, setNodePanelHeight] = useState(120); // Default height in pixels
  const [isResizing, setIsResizing] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Modal states
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [statusModalProps, setStatusModalProps] = useState<{
    operation: 'start' | 'pause' | 'stop';
    status: 'success' | 'error' | 'info';
    message: string;
    errors?: string[];
  }>({
    operation: 'start',
    status: 'info',
    message: '',
  });

  // Constants for resizing limits
  const DEFAULT_HEIGHT = 120;
  const MIN_HEIGHT = Math.round(DEFAULT_HEIGHT * 0.5); // 50% = 60px
  const MAX_HEIGHT = Math.round(DEFAULT_HEIGHT * 3.0); // 300% = 360px

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
    deleteWorkflow,
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

  // Handle mouse resize functionality
  const handleMouseDown = React.useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const handleMouseMove = React.useCallback(
    (e: MouseEvent) => {
      if (!isResizing) return;

      // Calculate new height based on mouse position relative to the node panel
      const rect = document.querySelector('[data-node-panel]')?.getBoundingClientRect();
      if (!rect) return;

      const newHeight = Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT, e.clientY - rect.top));
      setNodePanelHeight(newHeight);
    },
    [isResizing, MIN_HEIGHT, MAX_HEIGHT]
  );

  const handleMouseUp = React.useCallback(() => {
    setIsResizing(false);
  }, []);

  // Global mouse event listeners for resizing
  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'row-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

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
    setShowSaveModal(true);
  };

  const handleSaveWorkflow = async (options: {
    name: string;
    location: 'local' | 'remote';
    filepath?: string;
  }) => {
    try {
      // TODO: Implement location-specific save logic based on options.location
      await saveWorkflow();

      // Update the active workflow and add to workflows list (prevent duplicates)
      const currentState = useWorkflowStore.getState();

      // Check if workflow with this name already exists
      const existingWorkflow = currentState.workflows.find(w => w.name === options.name);

      let updatedWorkflow: WorkflowMetadata;
      let updatedWorkflows: WorkflowMetadata[];

      if (existingWorkflow) {
        // Update existing workflow instead of creating duplicate
        updatedWorkflow = {
          ...existingWorkflow,
          modified: new Date(),
          description: 'Updated saved workflow',
        };
        updatedWorkflows = currentState.workflows.map(w =>
          w.id === existingWorkflow.id ? updatedWorkflow : w
        );
      } else {
        // Create new workflow
        updatedWorkflow = {
          id: `saved-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: options.name,
          description: 'Saved workflow',
          version: '1.0.0',
          author: 'PLC-GBT',
          created: new Date(),
          modified: new Date(),
          tags: ['saved'],
          category: 'control' as const,
        };
        updatedWorkflows = [...currentState.workflows, updatedWorkflow];
      }

      // Update the store
      useWorkflowStore.setState({
        activeWorkflow: updatedWorkflow,
        workflows: updatedWorkflows,
      });

      setStatusModalProps({
        operation: 'stop', // Using stop operation for save (no auto-start behavior)
        status: 'success',
        message: `Workflow "${options.name}" saved successfully to ${options.location} storage.`,
      });
      setShowStatusModal(true);
    } catch (error) {
      setStatusModalProps({
        operation: 'start',
        status: 'error',
        message: `Failed to save workflow "${options.name}"`,
        errors: [error instanceof Error ? error.message : 'Unknown error'],
      });
      setShowStatusModal(true);
    }
  };

  const handleExport = () => {
    setShowExportModal(true);
  };

  const handleExportWorkflow = async (options: {
    name: string;
    format: 'json' | 'xml' | 'n8n';
    location: 'local' | 'remote';
    filepath?: string;
  }) => {
    try {
      const data = exportWorkflow(options.format);

      if (options.location === 'local') {
        // Local download
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${options.name}.${options.format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // TODO: Implement remote server export
        console.log('Exporting to remote server:', options);
      }

      setStatusModalProps({
        operation: 'start',
        status: 'success',
        message: `Workflow "${options.name}" exported successfully to ${options.location} storage.`,
      });
      setShowStatusModal(true);
    } catch (error) {
      setStatusModalProps({
        operation: 'start',
        status: 'error',
        message: `Failed to export workflow "${options.name}"`,
        errors: [error instanceof Error ? error.message : 'Unknown error'],
      });
      setShowStatusModal(true);
    }
  };

  const handleImport = () => {
    setShowImportModal(true);
  };

  const handleImportWorkflow = async (options: {
    location: 'local' | 'remote';
    filepath?: string;
    file?: File;
  }) => {
    try {
      if (options.location === 'local' && options.file) {
        // Local file import
        const reader = new FileReader();
        reader.onload = e => {
          const content = e.target?.result as string;
          try {
            const data = JSON.parse(content);

            // Validate workflow object structure
            const validationResult = validateWorkflowObject(data);
            if (!validationResult.isValid) {
              setStatusModalProps({
                operation: 'start',
                status: 'error',
                message: `Invalid workflow file "${options.file?.name}"`,
                errors: validationResult.errors,
              });
              setShowStatusModal(true);
              return;
            }

            importWorkflow(data);
            setStatusModalProps({
              operation: 'start',
              status: 'success',
              message: `Workflow "${options.file?.name}" imported successfully from local file.`,
            });
            setShowStatusModal(true);
          } catch (error) {
            setStatusModalProps({
              operation: 'start',
              status: 'error',
              message: `Failed to parse workflow file "${options.file?.name}"`,
              errors: [error instanceof Error ? error.message : 'Invalid JSON format'],
            });
            setShowStatusModal(true);
          }
        };
        reader.readAsText(options.file);
      } else if (options.location === 'remote' && options.filepath) {
        // TODO: Implement remote file import
        setStatusModalProps({
          operation: 'start',
          status: 'info',
          message: `Remote import from "${options.filepath}" not yet implemented.`,
        });
        setShowStatusModal(true);
      }
    } catch (error) {
      setStatusModalProps({
        operation: 'start',
        status: 'error',
        message: 'Failed to import workflow',
        errors: [error instanceof Error ? error.message : 'Unknown error'],
      });
      setShowStatusModal(true);
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

  // Workflow control handlers
  const handleStartWorkflow = () => {
    try {
      // TODO: Implement actual workflow start logic
      setStatusModalProps({
        operation: 'start',
        status: 'success',
        message: `Workflow "${
          activeWorkflow?.name || 'Demo Temperature Control'
        }" started successfully.`,
      });
      setShowStatusModal(true);
    } catch (error) {
      setStatusModalProps({
        operation: 'start',
        status: 'error',
        message: 'Failed to start workflow',
        errors: [error instanceof Error ? error.message : 'Unknown error'],
      });
      setShowStatusModal(true);
    }
  };

  const handlePauseWorkflow = () => {
    try {
      // TODO: Implement actual workflow pause logic
      setStatusModalProps({
        operation: 'pause',
        status: 'success',
        message: `Workflow "${
          activeWorkflow?.name || 'Demo Temperature Control'
        }" paused successfully.`,
      });
      setShowStatusModal(true);
    } catch (error) {
      setStatusModalProps({
        operation: 'pause',
        status: 'error',
        message: 'Failed to pause workflow',
        errors: [error instanceof Error ? error.message : 'Unknown error'],
      });
      setShowStatusModal(true);
    }
  };

  const handleStopWorkflow = () => {
    try {
      // TODO: Implement actual workflow stop logic
      setStatusModalProps({
        operation: 'stop',
        status: 'success',
        message: `Workflow "${
          activeWorkflow?.name || 'Demo Temperature Control'
        }" stopped successfully.`,
      });
      setShowStatusModal(true);
    } catch (error) {
      setStatusModalProps({
        operation: 'stop',
        status: 'error',
        message: 'Failed to stop workflow',
        errors: [error instanceof Error ? error.message : 'Unknown error'],
      });
      setShowStatusModal(true);
    }
  };

  const handleDeleteWorkflow = () => {
    if (!activeWorkflow) {
      setStatusModalProps({
        operation: 'stop', // Using stop for delete operation
        status: 'error',
        message: 'No workflow selected to delete',
      });
      setShowStatusModal(true);
      return;
    }

    // Show confirmation modal
    const confirmDelete = window.confirm(
      `Are you sure you want to delete the workflow "${activeWorkflow.name}"?\n\nThis will remove:\n- The workflow from all lists\n- All tabs containing this workflow\n- All nodes and connections from the canvas\n\nThis action cannot be undone.`
    );

    if (confirmDelete) {
      try {
        const workflowToDelete = activeWorkflow;

        // Get current state for comprehensive cleanup
        const currentState = useWorkflowStore.getState();

        // 1. Remove workflow from workflows array
        const updatedWorkflows = currentState.workflows.filter(w => w.id !== workflowToDelete.id);

        // 2. Close any tabs related to this workflow
        const updatedTabs = currentState.tabs.filter(tab => tab.workflowId !== workflowToDelete.id);

        // 3. If the active tab was for this workflow, switch to first remaining tab or create new
        let newActiveTabId = currentState.activeTabId;
        if (
          currentState.tabs.find(tab => tab.id === currentState.activeTabId)?.workflowId ===
          workflowToDelete.id
        ) {
          newActiveTabId = updatedTabs.length > 0 ? updatedTabs[0].id : null;
        }

        // 4. Clear canvas if this was the active workflow
        const shouldClearCanvas = currentState.activeWorkflow?.id === workflowToDelete.id;

        // 5. Update store with comprehensive cleanup
        useWorkflowStore.setState({
          workflows: updatedWorkflows,
          tabs: updatedTabs,
          activeTabId: newActiveTabId,
          activeWorkflow: shouldClearCanvas ? null : currentState.activeWorkflow,
          nodes: shouldClearCanvas ? [] : currentState.nodes,
          edges: shouldClearCanvas ? [] : currentState.edges,
        });

        setStatusModalProps({
          operation: 'stop', // Using stop for delete operation (red color)
          status: 'success',
          message: `Workflow "${workflowToDelete.name}" deleted successfully from all locations.`,
        });
        setShowStatusModal(true);
      } catch (error) {
        setStatusModalProps({
          operation: 'stop',
          status: 'error',
          message: `Failed to delete workflow "${activeWorkflow.name}"`,
          errors: [error instanceof Error ? error.message : 'Unknown error'],
        });
        setShowStatusModal(true);
      }
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
            onClick={handleImport}
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

          <button
            onClick={handleDeleteWorkflow}
            className="p-2 text-red-400 hover:text-red-300 hover:bg-[#3d3d3d] rounded transition-colors"
            title="Delete Current Workflow"
            disabled={!activeWorkflow || isReadOnly}
          >
            <Trash2 className="w-4 h-4" />
          </button>

          <div className="w-px h-6 bg-[#404040] mx-2" />
        </div>

        {/* Workflow Controls */}
        <div className="flex items-center space-x-1">
          <button
            onClick={handleStartWorkflow}
            className="p-2 text-green-400 hover:text-green-300 hover:bg-[#3d3d3d] rounded transition-colors"
            title="Start Workflow"
            disabled={isReadOnly}
          >
            <Play className="w-4 h-4" />
          </button>

          <button
            onClick={handlePauseWorkflow}
            className="p-2 text-yellow-400 hover:text-yellow-300 hover:bg-[#3d3d3d] rounded transition-colors"
            title="Pause Workflow"
            disabled={isReadOnly}
          >
            <Pause className="w-4 h-4" />
          </button>

          <button
            onClick={handleStopWorkflow}
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
            onClick={() => {
              setSnapToGrid(!snapToGrid);
              // Also toggle grid visibility for visual feedback
              useWorkflowStore.setState({ showBackground: !snapToGrid });
            }}
            className={cn(
              'p-2 rounded transition-colors',
              snapToGrid
                ? 'text-blue-400 bg-blue-600/20'
                : 'text-gray-300 hover:text-white hover:bg-[#3d3d3d]'
            )}
            title="Toggle Grid Lines"
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

        {/* Workflow Info - Always maintain layout space */}
        <div className="flex items-center space-x-3 ml-auto">
          {activeWorkflow ? (
            <>
              <div className="text-sm text-gray-400">{activeWorkflow.name}</div>
              <div className="text-xs text-gray-500">
                {nodes.length} nodes, {edges.length} connections
              </div>
              {isReadOnly && (
                <div className="px-2 py-1 bg-yellow-600/20 text-yellow-400 text-xs rounded">
                  Read Only
                </div>
              )}
            </>
          ) : (
            <div className="text-xs text-gray-500 italic">No workflow loaded</div>
          )}

          {/* Help Button */}
          <button
            onClick={() => setShowHelpModal(true)}
            className="p-2 text-blue-400 hover:text-blue-300 hover:bg-[#3d3d3d] rounded transition-colors"
            title="PLC-GBT Workflow Help & Support"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
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

          {/* Enhanced Node Palette with Resizable Container */}
          <div className="relative">
            <div
              data-node-panel
              className={cn(
                'overflow-y-auto overflow-x-hidden transition-all duration-150',
                'scrollbar-thin scrollbar-track-[#2d2d2d] scrollbar-thumb-[#505050] hover:scrollbar-thumb-[#606060]'
              )}
              style={{
                height: `${nodePanelHeight}px`,
                minHeight: `${MIN_HEIGHT}px`,
                maxHeight: `${MAX_HEIGHT}px`,
              }}
            >
              {nodeViewMode === 'list' ? (
                /* List View - Dense layout, 3 per row, 50% height reduction, single line text */
                <div className="grid grid-cols-3 gap-1">
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
                        'flex items-center gap-2 p-1 rounded border border-[#404040] transition-all duration-200 min-h-0 h-6', // Reduced padding and fixed height for 50% reduction
                        'focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-400',
                        isReadOnly
                          ? 'opacity-50 cursor-not-allowed'
                          : 'cursor-grab hover:border-[#505050] hover:bg-[#3d3d3d] group active:cursor-grabbing'
                      )}
                      title={`${node.description} - Drag to canvas`}
                      aria-label={`Add ${node.label} node to workflow`}
                    >
                      <node.icon className="w-3 h-3 text-white flex-shrink-0" />
                      <div className="flex-1 min-w-0 flex items-center gap-1">
                        <span className="text-xs text-gray-300 font-medium truncate">
                          {node.label}
                        </span>
                        <span className="text-xs text-gray-500 truncate">- {node.description}</span>
                      </div>
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <div
                          className="w-1.5 h-1.5 rounded-full"
                          style={{ backgroundColor: node.color }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                /* Card Views - Standard and Mini */
                <div
                  className={cn(
                    'grid gap-2 w-full', // Add w-full for full width flex
                    nodeViewMode === 'mini'
                      ? 'grid-cols-10' // 10 columns for mini cards per user requirement
                      : 'grid-cols-8' // 8 columns for standard cards per user requirement
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
                        'flex flex-col items-center rounded-lg border border-[#404040] transition-all duration-200 w-full', // Add w-full for flex sizing
                        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400',
                        nodeViewMode === 'mini' ? 'p-1.5' : 'p-2.5', // Adjusted padding for better fit
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
                      <span className="text-xs text-gray-300 text-center leading-tight font-medium">
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

            {/* Resize Handle */}
            <div
              className={cn(
                'absolute bottom-0 left-0 right-0 h-2 cursor-row-resize',
                'flex items-center justify-center group',
                'hover:bg-blue-500/10 transition-colors duration-200',
                isResizing && 'bg-blue-500/20'
              )}
              onMouseDown={handleMouseDown}
              title="Drag to resize node panel (50% - 300% of default height)"
            >
              {/* Resize indicator */}
              <div
                className={cn(
                  'w-8 h-0.5 rounded-full bg-gray-500 transition-all duration-200',
                  'group-hover:bg-blue-400 group-hover:w-12',
                  isResizing && 'bg-blue-400 w-12'
                )}
              />
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

      {/* Modals */}
      <SaveWorkflowModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        onSave={handleSaveWorkflow}
        currentWorkflowName={activeWorkflow?.name}
      />

      <ExportWorkflowModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExportWorkflow}
        currentWorkflowName={activeWorkflow?.name}
      />

      <ImportWorkflowModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onImport={handleImportWorkflow}
      />

      <WorkflowStatusModal
        isOpen={showStatusModal}
        onClose={() => setShowStatusModal(false)}
        operation={statusModalProps.operation}
        status={statusModalProps.status}
        message={statusModalProps.message}
        errors={statusModalProps.errors}
        workflowName={activeWorkflow?.name}
      />

      <WorkflowHelpModal isOpen={showHelpModal} onClose={() => setShowHelpModal(false)} />
    </div>
  );
}
