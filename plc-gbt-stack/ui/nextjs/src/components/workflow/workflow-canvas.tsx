'use client';

import {
  Background,
  BackgroundVariant,
  ConnectionMode,
  Controls,
  MarkerType,
  MiniMap,
  Panel,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import React, { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';

import { IndustrialNodeType, useWorkflowStore } from '@/lib/stores/workflow-store';
import { cn } from '@/lib/utils/cn';
import { EnhancedPropertiesPanel } from './EnhancedPropertiesPanel';
import { industrialNodeTypes } from './industrial-nodes';
import { WorkflowToolbar } from './workflow-toolbar';

interface WorkflowCanvasProps {
  className?: string;
  isReadOnly?: boolean;
}

function WorkflowCanvasInner({ className, isReadOnly = false }: WorkflowCanvasProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const { screenToFlowPosition, fitView, zoomIn, zoomOut } = useReactFlow();

  const {
    nodes,
    edges,
    viewport,
    snapToGrid,
    gridSize,
    showMinimap,
    showControls,
    showBackground,
    isReadOnly: storeReadOnly,
    selectedNodes,
    selectedEdges,

    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    setSelectedNodes,
    setSelectedEdges,
    clearSelection,
    setReadOnly,
  } = useWorkflowStore();

  // Set read-only mode
  useEffect(() => {
    setReadOnly(isReadOnly);
  }, [isReadOnly, setReadOnly]);

  // Track container dimensions for React Flow
  useLayoutEffect(() => {
    const resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setDimensions({ width, height });
      }
    });

    if (reactFlowWrapper.current) {
      resizeObserver.observe(reactFlowWrapper.current);
    }

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

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
    <div className={cn('flex h-full w-full min-h-0', className)} style={{ minHeight: '600px' }}>
      {/* Main Canvas */}
      <div
        className="flex-1 relative h-full min-h-0"
        ref={reactFlowWrapper}
        style={{ minHeight: '600px' }}
      >
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
          style={{
            width: dimensions.width,
            height: dimensions.height,
            minWidth: '800px',
            minHeight: '600px',
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

          {/* Controls */}
          {showControls && (
            <Controls
              position="bottom-left"
              className="!bg-[#2d2d2d] !border-[#404040] [&_button]:bg-[#2d2d2d] [&_button]:text-white [&_button]:border-[#404040]"
            />
          )}

          {/* Top Panel - Workflow Info */}
          <Panel position="top-left" className="m-2">
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
          </Panel>

          {/* Quick Actions Panel */}
          <Panel position="top-right" className="m-2">
            <div className="bg-[#2d2d2d] border border-[#404040] rounded-lg p-2 shadow-lg">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => fitView()}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
                >
                  Fit View
                </button>

                <button
                  onClick={() => clearSelection()}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors"
                  disabled={selectedNodes.length === 0 && selectedEdges.length === 0}
                >
                  Clear Selection
                </button>

                <button
                  onClick={() => {
                    /* TODO: Auto layout */
                  }}
                  className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded transition-colors"
                >
                  Auto Layout
                </button>
              </div>
            </div>
          </Panel>
        </ReactFlow>
      </div>

      {/* Enhanced Properties Panel */}
      <EnhancedPropertiesPanel
        className="min-w-0"
        width={320}
        resizable={true}
        collapsible={true}
        defaultTab="properties"
      />
    </div>
  );
}

// Main Workflow Canvas with Provider
export function WorkflowCanvas(props: WorkflowCanvasProps) {
  return (
    <div className="h-full w-full flex flex-col min-h-0" style={{ minHeight: '700px' }}>
      {/* Toolbar */}
      <WorkflowToolbar />

      {/* Canvas with React Flow Provider */}
      <div className="flex-1 min-h-0" style={{ minHeight: '650px' }}>
        <ReactFlowProvider>
          <WorkflowCanvasInner {...props} />
        </ReactFlowProvider>
      </div>
    </div>
  );
}

// Default export for React.lazy() compatibility
export default WorkflowCanvas;
