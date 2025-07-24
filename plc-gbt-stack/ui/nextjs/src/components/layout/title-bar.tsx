'use client'

import { Minimize2, Square, X } from 'lucide-react'

export function TitleBar() {
  return (
    <div className="h-8 bg-[#3c3c3c] flex items-center justify-between px-4 select-none border-b border-[#3c3c3c]">
      {/* Left side - Application title */}
      <div className="flex items-center space-x-2">
        <div className="w-4 h-4 bg-gradient-to-br from-blue-500 to-blue-700 rounded-sm flex items-center justify-center">
          <span className="text-white text-xs font-bold">P</span>
        </div>
        <span className="text-[#cccccc] text-sm font-medium">
          PLC-GBT Industrial Automation IDE
        </span>
      </div>

      {/* Center - File path or project name (when available) */}
      <div className="flex-1 text-center">
        <span className="text-[#969696] text-sm">
          Welcome to PLC-GBT
        </span>
      </div>

      {/* Right side - Window controls */}
      <div className="flex items-center">
        <button 
          className="w-8 h-8 flex items-center justify-center hover:bg-[#505050] transition-colors"
          title="Minimize"
        >
          <Minimize2 className="w-4 h-4 text-[#cccccc]" />
        </button>
        <button 
          className="w-8 h-8 flex items-center justify-center hover:bg-[#505050] transition-colors"
          title="Maximize"
        >
          <Square className="w-4 h-4 text-[#cccccc]" />
        </button>
        <button 
          className="w-8 h-8 flex items-center justify-center hover:bg-red-600 transition-colors"
          title="Close"
        >
          <X className="w-4 h-4 text-[#cccccc]" />
        </button>
      </div>
    </div>
  )
} 