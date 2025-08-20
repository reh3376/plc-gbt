'use client';

import {
  Background,
  BackgroundVariant,
  ConnectionMode,
  MarkerType,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Download, Grid, Maximize2, Save, X, ZoomIn, ZoomOut } from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { IndustrialNodeType, useWorkflowStore } from '@/lib/stores/workflow-store';
import { cn } from '@/lib/utils/cn';
import { industrialNodeTypes } from './industrial-nodes';
import { NodePropertiesModal } from './NodePropertiesModal';
import { WorkflowToolbar } from './workflow-toolbar';
import { WorkflowTabs } from './WorkflowTabs';

interface WorkflowCanvasProps {
  readonly className?: string;
  readonly isReadOnly?: boolean;
}

interface CanvasControlAction {
  readonly id: string;
  readonly label: string;
  readonly icon: React.ComponentType<{ className?: string }>;
  readonly onClick: () => void | Promise<void>;
  readonly disabled?: boolean;
  readonly variant?: 'primary' | 'secondary' | 'danger' | 'success';
  readonly tooltip?: string;
}

interface CanvasState {
  readonly nodesCount: number;
  readonly edgesCount: number;
  readonly selectedNodesCount: number;
  readonly selectedEdgesCount: number;
  readonly canUndo: boolean;
  readonly canRedo: boolean;
  readonly isConnected: boolean;
}

function WorkflowCanvasInner({ className, isReadOnly = false }: Readonly<WorkflowCanvasProps>) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [_isAutoLayouting, setIsAutoLayouting] = useState(false);
  const [isPropertiesModalOpen, setIsPropertiesModalOpen] = useState(false);
  const { screenToFlowPosition, fitView, zoomIn, zoomOut } = useReactFlow();

  const {
    nodes,
    edges,
    viewport,
    snapToGrid,
    gridSize,
    showMinimap,
    showBackground,
    isReadOnly: storeReadOnly,
    zoomCommand,

    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    setSelectedNodes,
    setSelectedEdges,
    setReadOnly,
    autoLayoutNodes,
    saveWorkflow,
    exportWorkflow,
    clearZoomCommand,
  } = useWorkflowStore();

  // Debug logging for workflow data and auto-fit view
  useEffect(() => {
    console.log('[WorkflowCanvas] Component mounted/updated:', {
      nodeCount: nodes.length,
      edgeCount: edges.length,
      hasNodes: nodes.length > 0,
      firstNode: nodes[0],
      viewport,
    });

    // Auto-fit view when nodes are loaded
    if (nodes.length > 0) {
      // Small delay to ensure React Flow has rendered the nodes
      setTimeout(() => {
        fitView({
          padding: 0.1,
          duration: 500,
        });
      }, 100);
    }
  }, [nodes.length, fitView]);

  // Listen for zoom commands from toolbar
  useEffect(() => {
    if (zoomCommand) {
      console.log('[WorkflowCanvas] Executing zoom command:', zoomCommand);
      switch (zoomCommand) {
        case 'zoom-in':
          zoomIn({ duration: 200 });
          break;
        case 'zoom-out':
          zoomOut({ duration: 200 });
          break;
        case 'fit-view':
          fitView({
            padding: 0.15,
            duration: 800,
            includeHiddenNodes: false,
            maxZoom: 1.2,
            minZoom: 0.1,
          });
          break;
        case 'reset-zoom':
          // Reset to 1x zoom centered
          fitView({ padding: 0.15, duration: 800, maxZoom: 1, minZoom: 1 });
          break;
      }
      // Clear the command after execution
      clearZoomCommand();
    }
  }, [zoomCommand, zoomIn, zoomOut, fitView, clearZoomCommand]);

  // Handle container resize
  useEffect(() => {
    const handleResize = () => {
      if (nodes.length > 0) {
        // Re-fit view on resize with a debounce
        setTimeout(() => {
          fitView({
            padding: 0.1,
            duration: 200,
          });
        }, 100);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [nodes.length, fitView]);

  // Enhanced Canvas State (unused for now, prepared for future features)
  // const canvasState: CanvasState = {
  //   nodesCount: nodes.length,
  //   edgesCount: edges.length,
  //   selectedNodesCount: selectedNodes.length,
  //   selectedEdgesCount: selectedEdges.length,
  //   canUndo: false, // Future: Implement undo/redo
  //   canRedo: false, // Future: Implement undo/redo
  //   isConnected: true, // Future: Check backend connection
  // };

  // Enhanced Auto Layout Handler
  const _handleAutoLayout = useCallback(async () => {
    if (nodes.length === 0) return;

    try {
      setIsAutoLayouting(true);
      await autoLayoutNodes('horizontal');

      // Fit view after layout with animation
      setTimeout(() => {
        fitView({
          padding: 0.1,
          duration: 800,
          includeHiddenNodes: false,
        });
      }, 100);
    } catch (error) {
      console.error('Auto layout failed:', error);
    } finally {
      setIsAutoLayouting(false);
    }
  }, [nodes.length, autoLayoutNodes, fitView]);

  // Enhanced Fit View Handler - Fixed to prevent UI panel disappearance
  const _handleFitView = useCallback(() => {
    fitView({
      padding: 0.15, // Increased padding to avoid panel overlap
      duration: 800,
      includeHiddenNodes: false,
      maxZoom: 1.2, // Reduced max zoom to prevent panel hiding
      minZoom: 0.1,
    });
  }, [fitView]);

  // Save Workflow Handler
  const _handleSaveWorkflow = useCallback(async () => {
    try {
      await saveWorkflow();
      // Future: Show success notification
    } catch (error) {
      console.error('Save workflow failed:', error);
      // Future: Show error notification
    }
  }, [saveWorkflow]);

  // Export Workflow Handler
  const _handleExportWorkflow = useCallback(() => {
    try {
      const data = exportWorkflow('json');
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `workflow-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export workflow failed:', error);
    }
  }, [exportWorkflow]);

  // Canvas Control Actions moved to WorkflowCanvasOverlays

  // Set read-only mode
  useEffect(() => {
    setReadOnly(isReadOnly);
  }, [isReadOnly, setReadOnly]);

  // Handle viewport changes
  // const onMoveEnd = useCallback(() => {
  //   const newViewport = getViewport()
  //   setViewport(newViewport)
  // }, [getViewport, setViewport])

  // Handle drag over for adding nodes
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // Handle drop for adding nodes
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      if (typeof type === 'undefined' || !type) return;

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      addNode(type as IndustrialNodeType, position);
    },
    [screenToFlowPosition, addNode]
  );

  // Handle node double-click to open properties modal
  const onNodeDoubleClick = useCallback(
    (event: React.MouseEvent) => {
      event.stopPropagation();
      if (!isReadOnly) {
        setIsPropertiesModalOpen(true);
      }
    },
    [isReadOnly]
  );

  // Handle selection changes
  const onSelectionChange = useCallback(
    ({
      nodes: selectedNodes,
      edges: selectedEdges,
    }: {
      nodes: Array<{ id: string }>;
      edges: Array<{ id: string }>;
    }) => {
      setSelectedNodes(selectedNodes.map(node => node.id));
      setSelectedEdges(selectedEdges.map(edge => edge.id));
    },
    [setSelectedNodes, setSelectedEdges]
  );

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.target !== document.body) return;

      // Delete selected elements
      if (event.key === 'Delete' || event.key === 'Backspace') {
        // TODO: Implement delete functionality
        console.log('Delete selected elements');
      }

      // Select all
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'a':
            event.preventDefault();
            // TODO: Implement select all
            console.log('Select all');
            break;
          case 'c':
            event.preventDefault();
            // TODO: Implement copy
            console.log('Copy selected');
            break;
          case 'v':
            event.preventDefault();
            // TODO: Implement paste
            console.log('Paste');
            break;
          case 'z':
            event.preventDefault();
            // TODO: Implement undo
            console.log('Undo');
            break;
          case 'y':
            event.preventDefault();
            // TODO: Implement redo
            console.log('Redo');
            break;
          case '=':
          case '+':
            event.preventDefault();
            zoomIn();
            break;
          case '-':
            event.preventDefault();
            zoomOut();
            break;
          case '0':
            event.preventDefault();
            fitView();
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [zoomIn, zoomOut, fitView]);

  return (
    <div className={cn('flex h-full w-full min-h-0', className)}>
      {/* Main Canvas */}
      <div className="flex-1 relative h-full w-full" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={industrialNodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onSelectionChange={onSelectionChange}
          onNodeDoubleClick={onNodeDoubleClick}
          connectionMode={ConnectionMode.Loose}
          defaultViewport={viewport}
          snapToGrid={snapToGrid}
          snapGrid={[gridSize, gridSize]}
          deleteKeyCode={['Delete', 'Backspace']}
          multiSelectionKeyCode={['Meta', 'Ctrl']}
          selectionKeyCode={['Shift']}
          panOnDrag={!storeReadOnly}
          elementsSelectable={!storeReadOnly}
          nodesConnectable={!storeReadOnly}
          nodesDraggable={!storeReadOnly}
          edgesFocusable={!storeReadOnly}
          nodesFocusable={!storeReadOnly}
          proOptions={{ hideAttribution: true }}
          className="bg-[#1e1e1e]"
          fitView
          fitViewOptions={{
            padding: 0.1,
            includeHiddenNodes: false,
          }}
          defaultEdgeOptions={{
            type: 'default',
            style: {
              stroke: '#6B7280',
              strokeWidth: 2,
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#6B7280',
            },
            focusable: true,
            selectable: true,
          }}
        >
          {/* Background Pattern */}
          {showBackground && (
            <Background color="#404040" gap={gridSize} size={2} variant={BackgroundVariant.Lines} />
          )}

          {/* Minimap */}
          {showMinimap && (
            <MiniMap
              nodeColor={node => {
                switch (node.type) {
                  case 'plc-input':
                    return '#10B981';
                  case 'plc-output':
                    return '#EF4444';
                  case 'pid-controller':
                    return '#8B5CF6';
                  case 'hmi-display':
                    return '#8B5CF6';
                  case 'data-logger':
                    return '#06B6D4';
                  case 'alarm-handler':
                    return '#F59E0B';
                  case 'modbus-client':
                    return '#EC4899';
                  case 'opc-server':
                    return '#84CC16';
                  case 'custom-logic':
                    return '#F97316';
                  case 'n8n-workflow':
                    return '#8B5CF6';
                  default:
                    return '#6B7280';
                }
              }}
              nodeStrokeColor="#fff"
              nodeStrokeWidth={2}
              maskColor="rgba(0, 0, 0, 0.8)"
              position="bottom-right"
              className="!bg-[#2d2d2d] !border-[#404040]"
              style={{
                backgroundColor: '#2d2d2d',
                border: '1px solid #404040',
              }}
            />
          )}

          {/* Controls - COMPLETELY DISABLED to prevent UI panel interference */}
          {/* All zoom and fit controls are now provided by WorkflowCanvasOverlays */}
        </ReactFlow>
      </div>

      {/* Node Properties Modal */}
      {isPropertiesModalOpen && (
        <NodePropertiesModal onClose={() => setIsPropertiesModalOpen(false)} />
      )}
    </div>
  );
}

// External Canvas Overlays - Outside React Flow Transform Context
function WorkflowCanvasOverlays() {
  const {
    nodes,
    edges,
    selectedNodes,
    selectedEdges,
    isReadOnly: storeReadOnly,
  } = useWorkflowStore();
  const { clearSelection, autoLayoutNodes, saveWorkflow } = useWorkflowStore();

  // Get React Flow instance for direct control access
  const { fitView, zoomIn, zoomOut } = useReactFlow();

  // Canvas state for Enhanced Canvas Controls
  const canvasState = useMemo(
    () => ({
      selectedNodesCount: selectedNodes.length,
      selectedEdgesCount: selectedEdges.length,
    }),
    [selectedNodes.length, selectedEdges.length]
  );

  // Enhanced Fit View Handler
  const handleFitView = useCallback(() => {
    fitView({
      padding: 0.15,
      duration: 800,
      includeHiddenNodes: false,
      maxZoom: 1.2,
      minZoom: 0.1,
    });
  }, [fitView]);

  // Zoom In Handler
  const handleZoomIn = useCallback(() => {
    zoomIn({ duration: 200 });
  }, [zoomIn]);

  // Zoom Out Handler
  const handleZoomOut = useCallback(() => {
    zoomOut({ duration: 200 });
  }, [zoomOut]);

  // Save Workflow Handler
  const handleSaveWorkflow = useCallback(async () => {
    try {
      await saveWorkflow();
    } catch (error) {
      console.error('Failed to save workflow:', error);
    }
  }, [saveWorkflow]);

  // Auto Layout Handler
  const [isAutoLayouting, setIsAutoLayouting] = useState<boolean>(false);
  const handleAutoLayout = useCallback(async () => {
    if (isAutoLayouting) return;

    setIsAutoLayouting(true);
    try {
      autoLayoutNodes('horizontal');
      // Fit view after layout with a small delay
      setTimeout(() => {
        fitView({
          padding: 0.15,
          duration: 800,
          includeHiddenNodes: false,
          maxZoom: 1.2,
          minZoom: 0.1,
        });
      }, 100);
    } finally {
      setIsAutoLayouting(false);
    }
  }, [isAutoLayouting, autoLayoutNodes, fitView]);

  // Export Workflow Handler
  const handleExportWorkflow = useCallback(() => {
    const workflowData = { nodes, edges: [] }; // Replace with actual edges if available
    const blob = new Blob([JSON.stringify(workflowData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'workflow.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [nodes]);

  // Canvas Control Actions
  const canvasControlActions = [
    {
      id: 'zoom-in',
      label: 'Zoom In',
      icon: ZoomIn,
      onClick: handleZoomIn,
      variant: 'secondary' as const,
      tooltip: 'Zoom in (+)',
    },
    {
      id: 'zoom-out',
      label: 'Zoom Out',
      icon: ZoomOut,
      onClick: handleZoomOut,
      variant: 'secondary' as const,
      tooltip: 'Zoom out (-)',
    },
    {
      id: 'fit-view',
      label: 'Fit View',
      icon: Maximize2,
      onClick: handleFitView,
      variant: 'primary' as const,
      tooltip: 'Fit all nodes in view (Ctrl+Shift+F)',
    },
    {
      id: 'clear-selection',
      label: 'Clear Selection',
      icon: X,
      onClick: clearSelection,
      disabled: canvasState.selectedNodesCount === 0 && canvasState.selectedEdgesCount === 0,
      variant: 'secondary' as const,
      tooltip: 'Clear all selected nodes and edges (Escape)',
    },
    {
      id: 'auto-layout',
      label: isAutoLayouting ? 'Layouting...' : 'Auto Layout',
      icon: Grid,
      onClick: handleAutoLayout,
      disabled: isAutoLayouting,
      variant: 'success' as const,
      tooltip: 'Auto-arrange nodes using force-directed layout',
    },
    {
      id: 'save-workflow',
      label: 'Save',
      icon: Save,
      onClick: handleSaveWorkflow,
      variant: 'success' as const,
      tooltip: 'Save the current workflow',
    },
    {
      id: 'export-workflow',
      label: 'Export',
      icon: Download,
      onClick: handleExportWorkflow,
      variant: 'secondary' as const,
      tooltip: 'Export workflow as JSON file',
    },
  ];

  return (
    <>
      {/* Top Left Panel - Workflow Info */}
      <div className="absolute top-2 left-2 z-50 pointer-events-auto">
        <div className="bg-[#2d2d2d] border border-[#404040] rounded-lg p-3 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="text-sm font-medium text-white">Industrial Workflow Canvas</div>

            <div className="text-xs text-gray-400">
              Nodes: {nodes.length} | Edges: {edges.length}
            </div>

            {selectedNodes.length > 0 && (
              <div className="text-xs text-blue-400">
                Selected: {selectedNodes.length} nodes, {selectedEdges.length} edges
              </div>
            )}

            {storeReadOnly && (
              <div className="px-2 py-1 bg-yellow-600/20 text-yellow-400 text-xs rounded">
                Read Only
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Top Right Panel - Enhanced Canvas Controls */}
      <div className="absolute top-2 right-2 z-50 pointer-events-auto">
        <div className="bg-[#2d2d2d] border border-[#404040] rounded-lg p-2 shadow-lg">
          <div className="flex items-center space-x-2">
            {canvasControlActions.map(action => {
              const getVariantStyles = (variant: CanvasControlAction['variant']) => {
                switch (variant) {
                  case 'primary':
                    return 'bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50';
                  case 'secondary':
                    return 'bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 disabled:opacity-50';
                  case 'success':
                    return 'bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50';
                  case 'danger':
                    return 'bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:opacity-50';
                  default:
                    return 'bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 disabled:opacity-50';
                }
              };

              return (
                <button
                  key={action.id}
                  onClick={action.onClick}
                  disabled={action.disabled}
                  className={cn(
                    'flex items-center gap-1.5 px-3 py-1 text-white text-xs rounded transition-all duration-200',
                    'disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500',
                    getVariantStyles(action.variant)
                  )}
                  title={action.tooltip}
                  data-testid={`canvas-control-${action.id}`}
                >
                  <action.icon className="w-3 h-3" />
                  <span className="font-medium">{action.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}

// Main Workflow Canvas with Provider
export function WorkflowCanvas(props: WorkflowCanvasProps) {
  return (
    <div className="h-full w-full flex flex-col min-h-0">
      {/* Tabs */}
      <WorkflowTabs />

      {/* Toolbar */}
      <WorkflowToolbar />

      {/* Canvas with React Flow Provider - Positioned Relative Container */}
      <div className="flex-1 min-h-0 relative">
        <ReactFlowProvider>
          <WorkflowCanvasInner {...props} />
          {/* External UI Panels - Inside Provider but Outside React Flow Transform Context */}
          <WorkflowCanvasOverlays />
        </ReactFlowProvider>
      </div>
    </div>
  );
}

// Default export for React.lazy() compatibility
export default WorkflowCanvas;
