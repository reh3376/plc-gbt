'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'
import { X, Minus } from 'lucide-react'
import { useLayoutStore } from '@/lib/stores/layout-store'

interface BottomPanelProps {
  isOpen: boolean
  height?: number
}

interface PanelTab {
  id: string
  title: string
  content: React.ComponentType
}

// Placeholder components for different tabs
const TerminalView = () => (
  <div className="flex-1 bg-[#0c0c0c] p-4 font-mono text-sm text-[#cccccc]">
    <div className="mb-2">
      <span className="text-green-400">plc-gbt@workspace:~$</span> 
      <span className="ml-2">Welcome to PLC-GBT Terminal</span>
    </div>
    <div className="mb-2">
      <span className="text-green-400">plc-gbt@workspace:~$</span> 
      <span className="ml-2 animate-pulse">_</span>
    </div>
  </div>
)

const OutputView = () => (
  <div className="flex-1 bg-[#1e1e1e] p-4 text-sm text-[#cccccc]">
    <div className="text-[#569cd6] mb-2">[Info] PLC-GBT UI Started</div>
    <div className="text-[#4ec9b0] mb-2">[Success] Connected to backend services</div>
    <div className="text-[#dcdcaa] mb-2">[Log] Ready for industrial automation tasks</div>
  </div>
)

const ProblemsView = () => (
  <div className="flex-1 bg-[#1e1e1e] p-4 text-sm text-[#cccccc]">
    <div className="text-[#569cd6]">No problems detected</div>
    <div className="text-[#6a9955] mt-2">All systems operational</div>
  </div>
)

const PANEL_TABS: PanelTab[] = [
  { id: 'terminal', title: 'Terminal', content: TerminalView },
  { id: 'output', title: 'Output', content: OutputView },
  { id: 'problems', title: 'Problems', content: ProblemsView },
]

export function BottomPanel({ isOpen, height = 200 }: BottomPanelProps) {
  const [activeTab, setActiveTab] = useState('terminal')
  const { toggleBottomPanel } = useLayoutStore()

  if (!isOpen) {
    return null
  }

  const ActiveComponent = PANEL_TABS.find(tab => tab.id === activeTab)?.content || TerminalView

  return (
    <div 
      className="bg-[#1e1e1e] border-t border-[#3c3c3c] flex flex-col"
      style={{ height }}
    >
      {/* Tab Bar */}
      <div className="h-8 bg-[#2d2d30] border-b border-[#3c3c3c] flex items-center justify-between">
        <div className="flex">
          {PANEL_TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "px-3 py-1 text-sm transition-colors",
                activeTab === tab.id
                  ? "text-white bg-[#1e1e1e] border-t-2 border-blue-500"
                  : "text-[#cccccc] hover:text-white hover:bg-[#3c3c3c]"
              )}
            >
              {tab.title}
            </button>
          ))}
        </div>

        {/* Panel Controls */}
        <div className="flex items-center">
          <button
            onClick={toggleBottomPanel}
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] transition-colors"
            title="Minimize Panel"
          >
            <Minus className="w-4 h-4 text-[#cccccc]" />
          </button>
          <button
            onClick={toggleBottomPanel}
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] transition-colors"
            title="Close Panel"
          >
            <X className="w-4 h-4 text-[#cccccc]" />
          </button>
        </div>
      </div>

      {/* Panel Content */}
      <div className="flex-1 overflow-hidden">
        <ActiveComponent />
      </div>
    </div>
  )
} 