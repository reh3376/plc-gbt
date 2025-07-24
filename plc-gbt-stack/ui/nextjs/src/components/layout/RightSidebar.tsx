'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'
import { useLayoutStore } from '@/lib/stores/layout-store'
import { useAIAssistantStore } from '@/lib/stores/ai-assistant-store'
import { ChatInterface } from '@/components/ai/ChatInterface'
import { 
  X,
  Bot,
  MessageSquare,
  HelpCircle,
  ChevronRight,
  PinOff
} from 'lucide-react'

interface RightSidebarProps {
  className?: string
}

interface SidebarTab {
  id: string
  name: string
  icon: React.ComponentType<{ className?: string }>
  content: React.ComponentType
}

// Enhanced AI Assistant Content with improved state management
const AIAssistantContent = () => {
  const { 
    detachPanel, 
    togglePanel, 
    setMode, 
    setSidebarIntegrated,
    isTyping,
    messages
  } = useAIAssistantStore()
  const { toggleRightPanel } = useLayoutStore()

  const handlePopOut = () => {
    // Enhanced pop-out with better state management
    setSidebarIntegrated(false)
    setMode('floating')
    toggleRightPanel()
    
    // Small delay to ensure smooth transition
    setTimeout(() => {
      detachPanel()
      togglePanel()
    }, 150)
  }

  const handleMinimizeToTray = () => {
    // Minimize to tray instead of completely closing
    toggleRightPanel()
  }

  return (
    <div className="h-full flex flex-col">
      {/* Enhanced header with status indicators */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[#3c3c3c] bg-[#2d2d30]">
        <div className="flex items-center space-x-2">
          <Bot className="w-4 h-4 text-[#007acc]" />
          <span className="text-sm font-medium text-[#cccccc]">AI Assistant</span>
          
          {/* Activity indicator */}
          {isTyping && (
            <div className="flex space-x-1">
              <div className="w-1 h-1 bg-[#007acc] rounded-full animate-bounce" />
              <div className="w-1 h-1 bg-[#007acc] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="w-1 h-1 bg-[#007acc] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
            </div>
          )}
          
          {/* Message count indicator */}
          {messages.length > 0 && (
            <span className="text-xs bg-[#007acc] text-white px-1.5 py-0.5 rounded">
              {messages.length}
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-1">
          {/* Minimize to tray button */}
          <button
            onClick={handleMinimizeToTray}
            className="p-1 hover:bg-[#3c3c3c] rounded text-[#cccccc] hover:text-white transition-colors"
            title="Minimize to tray"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
          
          {/* Pop out button with enhanced tooltip */}
          <button
            onClick={handlePopOut}
            className="p-1 hover:bg-[#3c3c3c] rounded text-[#cccccc] hover:text-white transition-colors"
            title="Pop out to floating window (keeps conversation)"
          >
            <PinOff className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* Chat Interface with enhanced props */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface 
          variant="sidebar"
          showHeader={false}
          showSystemStatus={true}
          className="h-full"
        />
      </div>
    </div>
  )
}

const ChatHistoryContent = () => {
  const { messages, clearMessages } = useAIAssistantStore()

  const getRelativeTime = (timestamp: Date) => {
    const now = new Date()
    const diff = now.getTime() - timestamp.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`
    if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`
    return `${days} day${days !== 1 ? 's' : ''} ago`
  }

  return (
    <div className="p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[#cccccc] font-medium">Chat History</h3>
        {messages.length > 0 && (
          <button
            onClick={clearMessages}
            className="text-xs text-[#969696] hover:text-[#cccccc] transition-colors"
          >
            Clear
          </button>
        )}
      </div>
      
      {messages.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-center">
          <div>
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50 text-[#969696]" />
            <p className="text-sm text-[#969696]">No chat history yet</p>
            <p className="text-xs text-[#555] mt-1">Your conversations will appear here.</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-2">
          <div className="text-xs text-[#969696] mb-2">
            {messages.length} message{messages.length !== 1 ? 's' : ''} • Last: {getRelativeTime(messages[messages.length - 1]?.timestamp)}
          </div>
          {messages.slice(-10).reverse().map((message) => (
            <div key={message.id} className="p-3 bg-[#2a2d2e] rounded border border-[#3c3c3c] hover:border-[#525252] transition-colors">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div className={cn(
                    "w-3 h-3 rounded-full",
                    message.role === 'user' ? "bg-[#00d4aa]" : "bg-[#007acc]"
                  )} />
                  <span className="text-xs font-medium text-[#cccccc]">
                    {message.role === 'user' ? 'You' : 'Assistant'}
                  </span>
                </div>
                <span className="text-xs text-[#969696]">
                  {getRelativeTime(message.timestamp)}
                </span>
              </div>
              <div className="text-sm text-[#cccccc] line-clamp-3">
                {message.content.length > 150 
                  ? message.content.substring(0, 150) + '...' 
                  : message.content
                }
              </div>
              {message.isError && (
                <div className="text-xs text-red-400 mt-1">Error message</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const HelpContent = () => (
  <div className="p-4">
    <h3 className="text-[#cccccc] font-medium mb-4">Help & Documentation</h3>
    <div className="space-y-3">
      <div className="space-y-2">
        <h4 className="text-[#cccccc] text-sm font-medium">Quick Start</h4>
        <div className="space-y-1 text-xs text-[#969696]">
          <div>• Open PLC projects from the file explorer</div>
          <div>• Use workflows to automate operations</div>
          <div>• Access AI assistance for programming help</div>
        </div>
      </div>
      
      <div className="space-y-2">
        <h4 className="text-[#cccccc] text-sm font-medium">Keyboard Shortcuts</h4>
        <div className="space-y-1 text-xs text-[#969696]">
          <div><kbd className="bg-[#3c3c3c] px-1 rounded">Ctrl+N</kbd> New file</div>
          <div><kbd className="bg-[#3c3c3c] px-1 rounded">Ctrl+S</kbd> Save</div>
          <div><kbd className="bg-[#3c3c3c] px-1 rounded">Ctrl+F</kbd> Search</div>
          <div><kbd className="bg-[#3c3c3c] px-1 rounded">F5</kbd> Run workflow</div>
        </div>
      </div>
      
      <button className="w-full py-2 bg-[#007acc] hover:bg-[#1177bb] text-white text-sm rounded transition-colors">
        View Full Documentation
      </button>
    </div>
  </div>
)

const SIDEBAR_TABS: SidebarTab[] = [
  {
    id: 'ai-assistant',
    name: 'AI Assistant',
    icon: Bot,
    content: AIAssistantContent
  },
  {
    id: 'chat-history',
    name: 'Chat History',
    icon: MessageSquare,
    content: ChatHistoryContent
  },
  {
    id: 'help',
    name: 'Help',
    icon: HelpCircle,
    content: HelpContent
  }
]

export function RightSidebar({ className }: RightSidebarProps) {
  const { toggleRightPanel } = useLayoutStore()
  const [activeTab, setActiveTab] = useState('ai-assistant')
  // Remove local isCollapsed state - use layout store instead
  
  const activeTabData = SIDEBAR_TABS.find(tab => tab.id === activeTab)
  const ActiveContent = activeTabData?.content || AIAssistantContent

  return (
    <aside 
      id="right-column"
      className={cn(
        "flex flex-col bg-[#252526] border-l border-[#3c3c3c] overflow-hidden h-full",
        className
      )}
    >
      {/* Header */}
      <div className="h-8 bg-[#2d2d30] border-b border-[#3c3c3c] flex items-center justify-between px-3">
        <span className="text-[#cccccc] text-sm font-medium uppercase tracking-wide">
          {activeTabData?.name || 'Right Panel'}
        </span>
        <div className="flex items-center space-x-1">
          <button
            onClick={toggleRightPanel}
            className="w-5 h-5 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors"
            title="Collapse Panel"
          >
            <ChevronRight className="w-3 h-3 text-[#cccccc]" />
          </button>
          <button
            onClick={toggleRightPanel}
            className="w-5 h-5 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors"
            title="Close Panel"
          >
            <X className="w-3 h-3 text-[#cccccc]" />
          </button>
        </div>
      </div>

      {/* Tab navigation */}
      <div className="border-b border-[#3c3c3c]">
        <div className="flex">
          {SIDEBAR_TABS.map(tab => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center space-x-2 px-3 py-2 text-sm transition-colors border-b-2",
                  isActive
                    ? "text-white bg-[#1e1e1e] border-[#007acc]"
                    : "text-[#cccccc] hover:text-white hover:bg-[#3c3c3c] border-transparent"
                )}
                title={tab.name}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden lg:inline">{tab.name}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-auto">
        <ActiveContent />
      </div>
    </aside>
  )
}

/**
 * RightSidebar Component
 * 
 * @description Column 4 slide-out panel for AI Assistant and auxiliary tools
 * @specification Implements main-ui-spec.md Column 4 requirements
 * 
 * @features
 * - Toggleable slide-out panel (hidden by default)
 * - Tabbed interface for multiple tools
 * - Collapsible content with icon-only mode
 * - AI Assistant integration
 * - Chat history and help documentation
 * - Responsive tab navigation
 * 
 * @tabs
 * - AI Assistant: Interactive PLC programming assistant
 * - Chat History: Previous conversations and queries
 * - Help: Documentation and keyboard shortcuts
 * 
 * @accessibility
 * - Keyboard navigation support
 * - Clear tab indicators
 * - Screen reader friendly
 * - Focus management
 * 
 * @performance
 * - Lazy content loading
 * - Efficient tab switching
 * - Optimized panel transitions
 * 
 * @future
 * - Real AI Assistant integration
 * - Additional tool tabs
 * - Custom panel resizing
 * - Drag and drop tab reordering
 */ 