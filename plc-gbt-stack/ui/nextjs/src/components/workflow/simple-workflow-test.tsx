'use client'

import { ReactFlow, ReactFlowProvider, Background, Controls } from '@xyflow/react'
import '@xyflow/react/dist/style.css'

// Ensure this component is completely standalone without API dependencies

const testNodes = [
  {
    id: '1',
    position: { x: 100, y: 100 },
    data: { label: 'Test Node 1' },
    type: 'default',
  },
  {
    id: '2',
    position: { x: 300, y: 100 },
    data: { label: 'Test Node 2' },
    type: 'default',
  },
]

const testEdges = [
  {
    id: 'e1-2',
    source: '1',
    target: '2',
  },
]

function SimpleWorkflowTestInner() {
  return (
    <div style={{ width: '800px', height: '600px', border: '2px solid red' }}>
      <ReactFlow
        nodes={testNodes}
        edges={testEdges}
        style={{ width: '100%', height: '100%' }}
        className="bg-gray-900"
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}

export function SimpleWorkflowTest() {
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ color: 'white', marginBottom: '20px' }}>Simple React Flow Test</h2>
      <ReactFlowProvider>
        <SimpleWorkflowTestInner />
      </ReactFlowProvider>
    </div>
  )
}

export default SimpleWorkflowTest 