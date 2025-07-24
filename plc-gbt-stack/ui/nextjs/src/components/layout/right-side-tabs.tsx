'use client'

import { useState } from 'react'
import { 
  MessageSquare, 
  Bot, 
  Settings, 
  BarChart3, 
  Bell,
  HelpCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useAIAssistantStore } from '@/lib/stores/ai-assistant-store'
import { AISettingsPanel } from '../ai/ai-settings-panel'

interface TabItem {
  id: string
  icon: React.ComponentType<{ className?: string }>
  title: string
  badge?: number
  onClick: () => void
}

export function RightSideTabs() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const { togglePanel, isOpen: isAIOpen, isMinimized } = useAIAssistantStore()

  const tabs: TabItem[] = [
    {
      id: 'ai-assistant',
      icon: Bot,
      title: 'AI Assistant',
      onClick: togglePanel,
    },
    {
      id: 'notifications',
      icon: Bell,
      title: 'Notifications',
      badge: 3,
      onClick: () => console.log('Notifications clicked'),
    },
    {
      id: 'analytics',
      icon: BarChart3,
      title: 'System Analytics',
      onClick: () => console.log('Analytics clicked'),
    },
    {
      id: 'help',
      icon: HelpCircle,
      title: 'Help & Documentation',
      onClick: () => window.open('https://docs.plc-gbt.com', '_blank'),
    },
    {
      id: 'ai-settings',
      icon: Settings,
      title: 'AI Assistant Settings',
      onClick: () => setIsSettingsOpen(true),
    },
  ]

  return (
    <>
      <div 
        className={cn(
          "fixed right-0 top-1/2 transform -translate-y-1/2 z-40 transition-all duration-200",
          isCollapsed ? "translate-x-full" : "translate-x-0"
        )}
      >
        {/* Tab Container */}
        <div className="bg-[#2d2d30] border border-[#3c3c3c] rounded-l-lg shadow-lg flex flex-col">
          {/* Collapse/Expand Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="w-8 h-8 flex items-center justify-center border-b border-[#3c3c3c] hover:bg-[#3c3c3c] transition-colors text-[#cccccc]"
            title={isCollapsed ? "Expand tabs" : "Collapse tabs"}
          >
            {isCollapsed ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>

          {/* Tab Items */}
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = tab.id === 'ai-assistant' && (isAIOpen || isMinimized)
            
            return (
              <button
                key={tab.id}
                onClick={tab.onClick}
                className={cn(
                  "relative w-12 h-12 flex items-center justify-center hover:bg-[#3c3c3c] transition-colors group",
                  isActive && "bg-[#094771] text-white",
                  !isActive && "text-[#cccccc]"
                )}
                title={tab.title}
              >
                <Icon className="w-5 h-5" />
                
                {/* Badge */}
                {tab.badge && (
                  <div className="absolute -top-1 -right-1 w-5 h-5 bg-[#e81123] text-white text-xs rounded-full flex items-center justify-center">
                    {tab.badge}
                  </div>
                )}
                
                {/* Active Indicator */}
                {isActive && (
                  <div className="absolute right-0 top-2 bottom-2 w-[2px] bg-white rounded-l" />
                )}
                
                {/* Tooltip */}
                <div className="absolute right-14 px-2 py-1 bg-[#2d2d30] text-white text-sm rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity delay-500 whitespace-nowrap border border-[#3c3c3c]">
                  {tab.title}
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* AI Settings Panel */}
      <AISettingsPanel 
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </>
  )
} 