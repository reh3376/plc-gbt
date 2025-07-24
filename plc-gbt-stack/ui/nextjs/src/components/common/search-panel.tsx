'use client'

import { Search, Filter } from 'lucide-react'

export function SearchPanel() {
  return (
    <div className="h-full flex flex-col p-4">
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#969696]" />
          <input
            type="text"
            placeholder="Search files, workflows, and control loops..."
            className="w-full pl-10 pr-4 py-2 bg-[#3c3c3c] text-[#cccccc] placeholder-[#969696] rounded border border-[#3c3c3c] focus:border-[#007acc] focus:outline-none"
          />
        </div>
      </div>
      
      <div className="flex items-center space-x-2 mb-4">
        <button className="flex items-center space-x-1 px-3 py-1 bg-[#3c3c3c] text-[#cccccc] rounded hover:bg-[#505050] transition-colors">
          <Filter className="w-4 h-4" />
          <span>Filters</span>
        </button>
      </div>

      <div className="text-[#969696] text-sm">
        Search across all PLC projects, workflows, and control loop configurations.
      </div>
    </div>
  )
} 