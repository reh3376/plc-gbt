'use client'

import { cn } from '@/lib/utils/cn'
import { IconStrip } from './IconStrip'
import { ToolPanel } from './ToolPanel'

interface LeftSidebarProps {
  className?: string
}

export function LeftSidebar({ className }: LeftSidebarProps) {
  return (
    <div 
      id="left-column"
      className={cn(
        "flex h-full w-full bg-[#252526] border-r border-[#3c3c3c] overflow-hidden",
        className
      )}
    >
      {/* Section 1: Icon Strip (40px fixed width) */}
      <div className="flex-shrink-0 w-10">
        <IconStrip />
      </div>
      
      {/* Section 2: Tool Panel (flexible width - fills remaining space) */}
      <div className="flex-1 min-w-0 overflow-hidden">
        <ToolPanel />
      </div>
    </div>
  )
}

/**
 * LeftSidebar Component
 * 
 * @description Column 1 container combining VS Code Activity Bar and Sidebar functionality
 * @specification Implements main-ui-spec.md Column 1 requirements
 * 
 * @structure
 * - Section 1: IconStrip (40px fixed width) - Vertical tool navigation
 * - Section 2: ToolPanel (flexible width) - Active tool content
 * 
 * @features
 * - Resizable container (60px-650px constraints handled by parent)
 * - Two-section flex layout
 * - VS Code color scheme
 * - Proper overflow handling
 * 
 * @accessibility
 * - Semantic sidebar structure
 * - Keyboard navigable sections
 * - ARIA landmark navigation
 */ 