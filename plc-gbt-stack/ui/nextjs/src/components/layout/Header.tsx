'use client'

import { cn } from '@/lib/utils/cn'

interface HeaderProps {
  className?: string
}

export function Header({ className }: HeaderProps) {
  return (
    <header 
      id="header-row" 
      className={cn(
        "h-12 bg-[#3c3c3c] border-b border-[#3c3c3c]",
        "flex items-center justify-between px-4 select-none",
        "text-[#cccccc]",
        className
      )}
    >
      {/* Left side - Application title */}
      <div className="flex items-center space-x-2">
        <div className="w-4 h-4 bg-gradient-to-br from-blue-500 to-blue-700 rounded-sm flex items-center justify-center">
          <span className="text-white text-xs font-bold">P</span>
        </div>
        <span className="text-sm font-medium">
          PLC-GBT Industrial Automation IDE
        </span>
      </div>

      {/* Center - Workspace title */}
      <div className="flex-1 text-center">
        <span className="text-[#969696] text-sm">
          Industrial Control Workspace
        </span>
      </div>

      {/* Right side - Quick actions */}
      <div className="flex items-center space-x-2">
        <button 
          className="px-2 py-1 text-xs hover:bg-[#505050] rounded transition-colors"
          title="Settings"
        >
          Settings
        </button>
        <button 
          className="px-2 py-1 text-xs hover:bg-[#505050] rounded transition-colors"
          title="Help"
        >
          Help
        </button>
      </div>
    </header>
  )
}

/**
 * Header Component
 * 
 * @description Fixed 48px height title bar spanning full width
 * @specification Matches VS Code title bar design from main-ui-spec.md
 * 
 * @features
 * - Fixed 48px height (h-12 = 3rem = 48px)
 * - App logo and title on left
 * - Workspace context in center
 * - Quick actions on right
 * - VS Code inspired styling
 * 
 * @accessibility
 * - Semantic header element
 * - Keyboard focusable buttons
 * - ARIA labels for interactive elements
 */ 