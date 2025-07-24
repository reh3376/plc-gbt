'use client'

import { useLayoutStore } from '@/lib/stores/layout-store'
import { EnhancedFileExplorer } from '../common/enhanced-file-explorer'
import { SearchPanel } from '../common/search-panel'
import { WorkflowPanel } from '../common/workflow-panel'
import { ChatPanel } from '../chat/chat-panel'
import { SettingsPanel } from '../common/settings-panel'

interface SidebarProps {
  isOpen: boolean
  width?: number
}

export function Sidebar({ isOpen, width = 300 }: SidebarProps) {
  const { activityBar } = useLayoutStore()

  const renderContent = () => {
    switch (activityBar.activeView) {
      case 'explorer':
        return <EnhancedFileExplorer />
      case 'search':
        return <SearchPanel />
      case 'workflows':
        return <WorkflowPanel />
      case 'chat':
        return <ChatPanel />
      case 'settings':
        return <SettingsPanel />
      default:
        return <EnhancedFileExplorer />
    }
  }

  const getTitle = () => {
    switch (activityBar.activeView) {
      case 'explorer':
        return 'Explorer'
      case 'search':
        return 'Search'
      case 'workflows':
        return 'Workflows'
      case 'chat':
        return 'AI Assistant'
      case 'settings':
        return 'Settings'
      default:
        return 'Explorer'
    }
  }

  if (!isOpen) {
    return null
  }

  return (
    <div 
      className="bg-[#252526] border-r border-[#3c3c3c] flex flex-col overflow-hidden"
      style={{ width }}
    >
      {/* Sidebar Header */}
      <div className="h-8 bg-[#2d2d30] border-b border-[#3c3c3c] flex items-center px-3">
        <span className="text-[#cccccc] text-sm font-medium uppercase tracking-wide">
          {getTitle()}
        </span>
      </div>

      {/* Sidebar Content */}
      <div className="flex-1 overflow-hidden">
        {renderContent()}
      </div>
    </div>
  )
} 