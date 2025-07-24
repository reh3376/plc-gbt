'use client'

import { ReactNode } from 'react'
import { useLayoutStore } from '@/lib/stores/layout-store'
import { useAIAssistantStore } from '@/lib/stores/ai-assistant-store'
import { cn } from '@/lib/utils/cn'
import { TitleBar } from './title-bar'
import { ActivityBar } from './activity-bar'
import { Sidebar } from './sidebar'
import { BottomPanel } from './bottom-panel'
import { StatusBar } from './status-bar'
import { RightSideTabs } from './right-side-tabs'
import { FloatingAIPanel } from '../ai/floating-ai-panel'

interface WorkspaceLayoutProps {
  children: ReactNode // Main editor area content
}

export function WorkspaceLayout({ children }: WorkspaceLayoutProps) {
  const {
    sidebar,
    bottomPanel,
    rightPanel,
  } = useLayoutStore()

  const { 
    isOpen: isAIOpen, 
    isDetached: isAIDetached,
    dockPosition 
  } = useAIAssistantStore()

  return (
    <div className="h-screen flex flex-col bg-[#1e1e1e] text-[#cccccc] overflow-hidden">
      {/* Title Bar */}
      <TitleBar />
      
      {/* Top Panel - AI Assistant when docked top */}
      {isAIOpen && !isAIDetached && dockPosition === 'top' && (
        <div className="h-64 border-b border-[#3c3c3c]">
          <FloatingAIPanel />
        </div>
      )}
      
      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Activity Bar - Always leftmost */}
        <ActivityBar />
        
        {/* Sidebar - Always after activity bar when open */}
        <Sidebar 
          isOpen={sidebar.isOpen}
          width={sidebar.width}
        />
        
        {/* Left Panel - AI Assistant when docked left (after sidebar) */}
        {isAIOpen && !isAIDetached && dockPosition === 'left' && (
          <div className="w-96 border-r border-[#3c3c3c] flex-shrink-0">
            <FloatingAIPanel />
          </div>
        )}
        
        {/* Center-Left Panel - AI Assistant in 2nd column */}
        {isAIOpen && !isAIDetached && dockPosition === 'center-left' && (
          <div className="w-80 border-r border-[#3c3c3c] flex-shrink-0 bg-[#252526]">
            <FloatingAIPanel />
          </div>
        )}
        
        {/* Main Editor Area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Editor Content */}
          <div 
            className={cn(
              "flex-1 overflow-hidden",
              bottomPanel.isOpen && "border-b border-[#3c3c3c]"
            )}
          >
            <div className="flex h-full">
              {/* Main content area */}
              <div className="flex-1">
                {children}
              </div>
              
              {/* Center-Right Panel - AI Assistant in 3rd column */}
              {isAIOpen && !isAIDetached && dockPosition === 'center-right' && (
                <div className="w-80 border-l border-[#3c3c3c] flex-shrink-0 bg-[#252526]">
                  <FloatingAIPanel />
                </div>
              )}
            </div>
          </div>
          
          {/* Bottom Panel */}
          <BottomPanel 
            isOpen={bottomPanel.isOpen}
            height={bottomPanel.height}
          />
          
          {/* Bottom Panel - AI Assistant when docked bottom */}
          {isAIOpen && !isAIDetached && dockPosition === 'bottom' && (
            <div className="h-64 border-t border-[#3c3c3c]">
              <FloatingAIPanel />
            </div>
          )}
        </div>
        
        {/* Right Panel - AI Assistant when docked right (2nd/3rd column option) */}
        {isAIOpen && !isAIDetached && dockPosition === 'right' && (
          <div className="w-96 border-l border-[#3c3c3c] flex-shrink-0">
            <FloatingAIPanel />
          </div>
        )}
        
        {/* Additional Right Panel - System panels */}
        {rightPanel.isOpen && (
          <div 
            className="bg-[#252526] border-l border-[#3c3c3c] overflow-hidden flex flex-col flex-shrink-0"
            style={{ width: rightPanel.width }}
          >
            <div className="flex-1 p-4">
              <div className="text-[#969696] text-center">
                Right panel content will go here
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Status Bar */}
      <StatusBar />
      
      {/* Right Side Tabs */}
      <RightSideTabs />
      
      {/* Floating AI Panel (when detached) */}
      {isAIOpen && isAIDetached && (
        <FloatingAIPanel />
      )}
    </div>
  )
} 