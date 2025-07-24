/**
 * Control Loop Panel - Phase 31.7 Tool Integration
 * AI Task Orchestrator Generated - Tool Panel Wrapper
 * 
 * Integrates the Control Loop Dashboard with the existing tool panel system
 * Provides proper layout constraints and integration with VS Code-style UI
 */

'use client'

import React from 'react'
import { ControlLoopDashboard } from '@/components/control-loop/ControlLoopDashboard'

/**
 * Control Loop Tool Panel
 * 
 * Wrapper component that integrates the Control Loop Dashboard
 * into the existing VS Code-style tool panel system
 */
export function ControlLoopPanel() {
  return (
    <div className="h-full w-full overflow-hidden">
      <ControlLoopDashboard 
        enableRealTime={true}
        refreshInterval={5000}
        className="h-full"
      />
    </div>
  )
}

export default ControlLoopPanel 