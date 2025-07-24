'use client'

import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels'
import { Header } from './Header'
import { Footer } from './Footer'
import { LeftSidebar } from './LeftSidebar'
import { MainContent } from './MainContent'
import { useLayoutStore } from '@/lib/stores/layout-store'
import { useAIAssistantStore } from '@/lib/stores/ai-assistant-store'
import { ChatInterface } from '@/components/ai/ChatInterface'
import { useEffect } from 'react'
// import { cn } from '@/lib/utils/cn' // Unused
import { ChevronRight, ChevronLeft, X } from 'lucide-react'

export function WorkspaceGrid() {
  const { 
    leftColWidth, 
    setLeftColWidth,
    aiAssistant,
    toggleAIAssistant,
    setAIAssistantOpen,
    setAIAssistantPosition,
    toggleAIAssistantMinimized,
    setAIAssistantWidth
  } = useLayoutStore()
  
  // Remove dependency on old AI assistant store mode system
  const { setSidebarIntegrated } = useAIAssistantStore()

  // Set AI assistant to always be in sidebar integrated mode
  useEffect(() => {
    setSidebarIntegrated(true)
  }, [setSidebarIntegrated])

  // Defensive state management: Ensure AI Assistant state consistency
  useEffect(() => {
    // If AI Assistant is closed, ensure it's not in any visible state
    if (!aiAssistant.isOpen) {
      // Reset to default position when closed
      if (aiAssistant.position !== 'right-edge') {
        console.warn('Resetting AI Assistant position from', aiAssistant.position, 'to right-edge')
        setAIAssistantPosition('right-edge')
      }
    }
  }, [aiAssistant.isOpen, aiAssistant.position, setAIAssistantPosition])

  // SUPER AGGRESSIVE: Monitor left panel width and reset if it exceeds safe limits
  useEffect(() => {
    const checkPanelWidth = () => {
      if (leftColWidth > 80) {
        console.warn('DEFENSIVE: Left panel width exceeded 80%, resetting from', leftColWidth, 'to 80%')
        setLeftColWidth(80)
      }
    }
    
    // Check immediately and set up frequent interval
    checkPanelWidth()
    const interval = setInterval(checkPanelWidth, 250) // Check every 250ms
    
    return () => clearInterval(interval)
  }, [leftColWidth, setLeftColWidth])

  // EMERGENCY: Prevent Column 2 from appearing when it shouldn't - IMMEDIATE CORRECTION
  useEffect(() => {
    const emergencyCorrection = () => {
      // Check if Column 2 DOM element exists when it shouldn't
      const column2Element = document.querySelector('#ai-column-2')
      const column2Handle = document.querySelector('#column2-handle')
      
      if (column2Element || column2Handle) {
        if (!aiAssistant.isOpen || aiAssistant.position !== 'column-2') {
          console.error('EMERGENCY: Column 2 DOM elements found when they should not exist!')
          console.error('Current AI state:', { isOpen: aiAssistant.isOpen, position: aiAssistant.position })
          
          // IMMEDIATE CORRECTION
          setAIAssistantOpen(false)
          setAIAssistantPosition('right-edge')
          
          // FORCE localStorage clear
          localStorage.removeItem('plc-gbt-layout-storage')
          localStorage.setItem('plc-layout-force-clear', Date.now().toString())
          
          // Force page reload if DOM elements persist
          setTimeout(() => {
            const stillExists = document.querySelector('#ai-column-2') || document.querySelector('#column2-handle')
            if (stillExists) {
              console.error('EMERGENCY: Column 2 still exists after correction, forcing reload')
              window.location.reload()
            }
          }, 1000)
        }
      }
      
      // Check for invalid AI state combinations
      if (aiAssistant.position === 'column-2' && !aiAssistant.isOpen) {
        console.error('EMERGENCY: AI in column-2 position but not open!')
        setAIAssistantOpen(false)
        setAIAssistantPosition('right-edge')
        localStorage.removeItem('plc-gbt-layout-storage')
      }
    }
    
    // Run immediately and every 1 second
    emergencyCorrection()
    const interval = setInterval(emergencyCorrection, 1000)
    
    return () => clearInterval(interval)
  }, [aiAssistant, setAIAssistantOpen, setAIAssistantPosition])

  // FORCE localStorage clear on mount if any Column 2 corruption detected
  useEffect(() => {
    const forceCleanup = () => {
      const layoutStorage = localStorage.getItem('plc-gbt-layout-storage')
      if (layoutStorage) {
        try {
          const parsed = JSON.parse(layoutStorage)
          if (parsed.state?.aiAssistant?.position === 'column-2') {
            console.error('EMERGENCY: Found Column 2 in localStorage on mount, clearing immediately')
            localStorage.removeItem('plc-gbt-layout-storage')
            localStorage.setItem('plc-layout-emergency-clear', Date.now().toString())
          }
        } catch (_e) {
          console.error('EMERGENCY: Corrupted localStorage detected, clearing')
          localStorage.removeItem('plc-gbt-layout-storage')
        }
      }
    }
    
    forceCleanup()
  }, []) // Only run on mount

  // Enhanced keyboard shortcuts for AI Assistant
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl+Shift+A to toggle AI Assistant
      if (event.ctrlKey && event.shiftKey && event.key === 'A') {
        event.preventDefault()
        toggleAIAssistant()
      }
      
      // Escape to close AI Assistant
      if (event.key === 'Escape' && aiAssistant.isOpen) {
        event.preventDefault()
        setAIAssistantOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [aiAssistant.isOpen, toggleAIAssistant, setAIAssistantOpen])

  // Handler functions for AI Assistant positioning
  const handleMoveToColumn2 = () => {
    setAIAssistantPosition('column-2')
  }

  const handleMoveToRightEdge = () => {
    setAIAssistantPosition('right-edge')
  }

  const handleCompleteCollapse = () => {
    // Add closing animation before actually closing
    const aiAssistantElement = document.querySelector('.ai-assistant-panel')
    if (aiAssistantElement) {
      aiAssistantElement.classList.add('exiting')
      
      // Wait for animation to complete before actually closing
      setTimeout(() => {
        setAIAssistantOpen(false)
      }, 1000) // Match the CSS animation duration
    } else {
      // Fallback: close immediately if element not found
      setAIAssistantOpen(false)
    }
  }

  // AI Assistant Panel Content Component
  const AIAssistantPanel = ({ position }: { position: 'column-2' | 'right-edge' }) => {
    if (aiAssistant.isMinimized) {
      return (
        <div className="w-full h-full flex flex-col items-center justify-start pt-4">
          <button
            onClick={toggleAIAssistantMinimized}
            className="p-2 hover:bg-[#3c3c3c] rounded transition-all duration-1500 text-[#cccccc] hover:text-white"
            title="Expand AI Assistant"
          >
            {position === 'column-2' ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      )
    }

    return (
      <div className="w-full flex flex-col h-full">
        {/* AI Assistant Header with dual chevron system */}
        <div className="h-8 bg-[#2d2d30] border-b border-[#3c3c3c] flex items-center justify-between px-3">
          <span className="text-[#cccccc] text-sm font-medium">AI Assistant</span>
          <div className="flex items-center space-x-1">
            <button
              onClick={position === 'column-2' ? handleMoveToRightEdge : handleMoveToColumn2}
              className="w-5 h-5 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-all duration-1500"
              title={position === 'column-2' ? 'Move to right edge' : 'Move to Column 2'}
            >
              {position === 'column-2' ? 
                <ChevronRight className="w-3 h-3 text-[#cccccc]" /> : 
                <ChevronLeft className="w-3 h-3 text-[#cccccc]" />
              }
            </button>
            <button
              onClick={handleCompleteCollapse}
              className="w-5 h-5 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-all duration-1500"
              title="Close AI Assistant"
            >
              <X className="w-3 h-3 text-[#cccccc]" />
            </button>
          </div>
        </div>
        
        {/* AI Assistant Content */}
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

  return (
    <div className="h-screen w-screen flex flex-col bg-[#1e1e1e] overflow-hidden">
      {/* Header Row - Fixed 48px */}
      <Header />
      
      {/* Main Row - Flexible height */}
      <div className="flex-1 overflow-hidden w-full">
        <PanelGroup 
          direction="horizontal" 
          className="w-full h-full transition-all duration-1500 ease-in-out"
          key={`panel-layout-${aiAssistant.isOpen}-${aiAssistant.position}-${aiAssistant.isMinimized}`}
          autoSaveId="workspace-layout"
        >
          {/* Column 1: Left Sidebar (Icon Strip + Tool Panel) - ALWAYS RESIZABLE */}
          <Panel
            id="left-sidebar"
            defaultSize={leftColWidth}
            minSize={6}
            maxSize={80}
            onResize={(size) => {
              // Aggressive constraint enforcement to prevent Column 2 bugs
              const constrainedSize = Math.max(6, Math.min(80, size))
              setLeftColWidth(constrainedSize)
              
              // Defensive: If somehow the size exceeds 80%, reset it
              if (size > 80) {
                console.warn('DEFENSIVE: Left panel exceeded 80%, resetting to 80%')
                setTimeout(() => setLeftColWidth(80), 100)
              }
            }}
            className="flex transition-all duration-1500 ease-in-out"
          >
            <LeftSidebar />
          </Panel>

          {/* DEDICATED Left Panel Resize Handle - ALWAYS PRESENT */}
          <PanelResizeHandle 
            id="left-panel-handle"
            className="w-1 bg-[#3c3c3c] hover:bg-[#007acc] transition-all duration-1500" 
          />

          {/* Column 2: AI Assistant - ONLY when AI is in column-2 mode */}
          {aiAssistant.isOpen && aiAssistant.position === 'column-2' && (
            <>
              <Panel
                id="ai-column-2"
                defaultSize={aiAssistant.isMinimized ? 3 : 25}
                minSize={aiAssistant.isMinimized ? 3 : 15}
                maxSize={aiAssistant.isMinimized ? 3 : 40}
                onResize={(size) => {
                  // Only allow resizing when not minimized
                  if (!aiAssistant.isMinimized) {
                    setAIAssistantWidth(size)
                  }
                }}
                className="flex transition-all duration-1500 ease-in-out bg-[#252526] border-r border-[#3c3c3c]"
              >
                <div className="ai-assistant-panel w-full h-full">
                  <AIAssistantPanel position="column-2" />
                </div>
              </Panel>
              
              {/* Column 2 Right Edge Resize Handle */}
              <PanelResizeHandle 
                id="column2-handle"
                className="w-1 bg-[#3c3c3c] hover:bg-[#007acc] transition-all duration-1500"
              />
            </>
          )}

          {/* Column 3: Main Content - FLEXIBLE */}
          <Panel
            id="main-content"
            defaultSize={
              // Calculate main content size properly to avoid negative values
              (() => {
                const leftPanelSize = leftColWidth
                const aiPanelSize = aiAssistant.isOpen ? (aiAssistant.isMinimized ? 3 : 25) : 0
                const remainingSize = 100 - leftPanelSize - aiPanelSize
                
                // Ensure minimum size is respected
                const minMainContentSize = 30
                return Math.max(remainingSize, minMainContentSize)
              })()
            }
            minSize={30}
            className="flex transition-all duration-1000 ease-in-out"
          >
            <MainContent />
          </Panel>

          {/* Column 4: AI Assistant at Right Edge - ONLY when position is 'right-edge' */}
          {aiAssistant.isOpen && aiAssistant.position === 'right-edge' && (
            <>
              {/* Right Edge Resize Handle */}
              <PanelResizeHandle 
                id="right-edge-handle"
                className="w-1 bg-[#3c3c3c] hover:bg-[#007acc] transition-all duration-1500" 
              />
              
              <Panel
                id="ai-right-edge"
                defaultSize={aiAssistant.isMinimized ? 3 : 25}
                minSize={aiAssistant.isMinimized ? 3 : 15}
                maxSize={aiAssistant.isMinimized ? 3 : 40}
                onResize={(size) => !aiAssistant.isMinimized && setAIAssistantWidth(size)}
                className="flex transition-all duration-1500 ease-in-out bg-[#252526] border-l border-[#3c3c3c]"
              >
                <div className="ai-assistant-panel w-full h-full">
                  <AIAssistantPanel position="right-edge" />
                </div>
              </Panel>
            </>
          )}
        </PanelGroup>
        
        {/* Floating chevron when AI Assistant is completely closed */}
        {!aiAssistant.isOpen && (
          <div className="fixed right-0 top-1/2 transform -translate-y-1/2 z-10">
            <button
              onClick={() => {
                setAIAssistantOpen(true)
                setAIAssistantPosition('right-edge')
              }}
              className="p-2 bg-[#252526] border border-[#3c3c3c] rounded-l-md hover:bg-[#3c3c3c] transition-all duration-1500 text-[#cccccc] hover:text-white shadow-lg transform hover:scale-105"
              title="Open AI Assistant (Ctrl+Shift+A)"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
      
      {/* Footer Row - Fixed 24px */}
      <Footer />
    </div>
  )
} 