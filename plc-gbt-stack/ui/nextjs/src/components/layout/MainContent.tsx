'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils/cn'

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
      {/* Content area */}
      <div className="flex-1 overflow-hidden">
        {children || (
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center">
                <span className="text-white text-2xl font-bold">P</span>
              </div>
              <div>
                <h2 className="text-[#cccccc] text-xl font-medium mb-2">
                  Welcome to PLC-GBT
                </h2>
                <p className="text-[#969696] text-sm max-w-md">
                  Industrial Automation IDE for PLC programming, workflow management, and control system design.
                </p>
              </div>
              <div className="flex flex-col space-y-2 text-sm text-[#969696]">
                <div>📁 Open a project from the file explorer</div>
                <div>🔍 Search across your PLC files</div>
                <div>⚙️ Manage workflows and automation</div>
                <div>🤖 Access AI assistance from the right panel</div>
              </div>
            </div>
          </div>
        )}
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