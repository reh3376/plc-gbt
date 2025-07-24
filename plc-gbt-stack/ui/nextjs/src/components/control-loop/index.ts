/**
 * Control Loop Components Index - Phase 31.7
 * AI Task Orchestrator Generated - Component Exports
 * 
 * Centralized export for all control loop components
 * Provides clean imports for other parts of the application
 */

// Main dashboard component
export { default as ControlLoopDashboard } from './ControlLoopDashboard'

// Supporting components
export { default as ControlLoopStats } from './ControlLoopStats'

export { default as ControlLoopFilters } from './ControlLoopFilters'

export { default as ControlLoopGrid } from './ControlLoopGrid'

export { default as ControlLoopCard } from './ControlLoopCard'

export { default as CreateControlLoopModal } from './CreateControlLoopModal'

// Re-export types for convenience
export type {
  EnhancedControlLoop,
  ControlLoopSummary,
  DashboardFilters,
  ControlLoopType,
  ControlLoopUpdate,
  ProcessVariable,
  PIDParameters,
  PIDEParameters,
  PerformanceMetrics
} from '@/lib/types/control-loop.types' 