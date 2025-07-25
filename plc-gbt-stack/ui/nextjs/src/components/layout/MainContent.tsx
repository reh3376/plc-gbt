'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils/cn'
import { MainContentRouter } from './MainContentRouter'

interface MainContentProps {
  children?: ReactNode
  className?: string
}

export function MainContent({ children, className }: MainContentProps) {
  return (
    <main 
      id="main-column"
      className={cn(
        "flex-1 flex flex-col overflow-hidden bg-[#1e1e1e]",
        className
      )}
    >
      {/* Content area - now uses MainContentRouter for dynamic switching */}
      <div className="flex-1 overflow-hidden">
        {children || <MainContentRouter />}
      </div>
    </main>
  )
}

/**
 * MainContent Component
 * 
 * @description Column 3 container for the main editor/workspace area
 * @specification Implements main-ui-spec.md Column 3 requirements
 * 
 * @features
 * - Flexible container for editor content
 * - Welcome screen when no content is loaded
 * - Responsive to panel resizing
 * - Proper overflow handling
 * - VS Code editor area styling
 * 
 * @content
 * - Code editors with Monaco integration
 * - Workflow canvas with React Flow
 * - Tabbed editor interface
 * - Document viewers
 * - Split panel layouts
 * 
 * @accessibility
 * - Semantic main element
 * - Clear content hierarchy
 * - Keyboard navigation support
 * 
 * @performance
 * - Minimal overhead container
 * - Efficient content switching
 * - Proper overflow management
 */ 