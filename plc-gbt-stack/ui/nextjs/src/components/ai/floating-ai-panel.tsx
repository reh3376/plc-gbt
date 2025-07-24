'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { 
  X, 
  Minimize2, 
  Pin,
  PinOff,
  Send,
  Bot,
  User,
  Sidebar  // Added for dock-to-sidebar button
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useAIAssistantStore } from '@/lib/stores/ai-assistant-store'
import { useLayoutStore } from '@/lib/stores/layout-store'  // Added for sidebar integration
import { useChat, useHealth } from '@/lib/hooks/useApi'

interface FloatingAIPanelProps {
  className?: string
}

export function FloatingAIPanel({ className }: FloatingAIPanelProps) {
  const {
    isOpen,
    isDetached,
    isDragging,
    isResizing,
    isMinimized,
    position,
    size,
    messages,
    isTyping,
    currentInput,
    userPreferences,
    
    togglePanel,
    detachPanel,
    attachPanel,
    minimizePanel,
    maximizePanel,
    setPosition,
    setSize,
    startDragging,
    stopDragging,
    startResizing,
    stopResizing,
    addMessage,
    setCurrentInput,
    setTyping,
    setMode,
    setSidebarIntegrated,
  } = useAIAssistantStore()

  // Enhanced layout store integration
  const { setRightPanelOpen } = useLayoutStore()

  // API Integration
  const { 
    sendMessage, 
    streamMessage, 
    loading: chatLoading, 
    error: chatError 
  } = useChat()
  
  const { 
    data: healthData, 
    loading: healthLoading, 
    error: healthError,
    execute: executeHealthCheck
  } = useHealth()

  const panelRef = useRef<HTMLDivElement>(null)
  const dragHandleRef = useRef<HTMLDivElement>(null)
  const resizeHandleRef = useRef<HTMLDivElement>(null)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 })

  // Drag functionality
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!panelRef.current) return
    
    const rect = panelRef.current.getBoundingClientRect()
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
    
    startDragging()
  }, [startDragging])

  // Global mouse move and up handlers
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging && isDetached) {
        const newX = e.clientX - dragOffset.x
        const newY = e.clientY - dragOffset.y
        
        // Keep panel within viewport bounds
        const maxX = window.innerWidth - size.width
        const maxY = window.innerHeight - size.height
        
        setPosition({
          x: Math.max(0, Math.min(maxX, newX)),
          y: Math.max(0, Math.min(maxY, newY))
        })
      }
      
      if (isResizing) {
        const deltaX = e.clientX - resizeStart.x
        const deltaY = e.clientY - resizeStart.y
        
        setSize({
          width: Math.max(300, resizeStart.width + deltaX),
          height: Math.max(200, resizeStart.height + deltaY)
        })
      }
    }

    // Auto-docking logic with enhanced zones
    const handleMouseUp = (_e: MouseEvent) => {
      if (isDragging) {
        // Enhanced docking zones for better UX
        const dockThreshold = 80  // Increased threshold
        const columnThreshold = 150  // Zone for column detection
        const windowWidth = window.innerWidth
        const windowHeight = window.innerHeight
        const centerX = windowWidth / 2
        
        // Determine dock position based on mouse position
        if (position.x < dockThreshold) {
          // Left edge - dock to sidebar-adjacent (2nd column)
          attachPanel('left')
        } else if (position.x + size.width > windowWidth - dockThreshold) {
          // Right edge - dock to right column
          attachPanel('right')
        } else if (position.y < dockThreshold) {
          // Top edge
          attachPanel('top')
        } else if (position.y + size.height > windowHeight - dockThreshold) {
          // Bottom edge
          attachPanel('bottom')
        } else if (Math.abs(position.x - centerX + size.width/2) < columnThreshold) {
          // Center column detection
          attachPanel('center-left')
        } else if (position.x > centerX) {
          // Right half of screen
          attachPanel('center-right')
        }
        // If none of the above, stay floating
        
        stopDragging()
      }
      
      if (isResizing) {
        stopResizing()
      }
    }

    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, isResizing, dragOffset, resizeStart, position, size, isDetached, attachPanel, stopDragging, stopResizing, setPosition, setSize])

  // Execute health check on mount - Remove dependency to prevent infinite loop
  useEffect(() => {
    executeHealthCheck();
  }, []);  // Empty dependency array - only run on mount

  // Enhanced dock-to-sidebar function
  const handleDockToSidebar = useCallback(() => {
    setMode('sidebar')
    setSidebarIntegrated(true)
    setRightPanelOpen(true)
    togglePanel() // Close floating panel
  }, [setMode, setSidebarIntegrated, setRightPanelOpen, togglePanel])

  // Handle message sending with real API
  const handleSendMessage = async () => {
    if (!currentInput.trim() || chatLoading) return

    const userMessage = currentInput.trim()
    setCurrentInput('')

    // Add user message to local state
    addMessage({
      content: userMessage,
      role: 'user'
    })

    try {
      setTyping(true)
      
      if (userPreferences.enableStreaming) {
        // Use streaming for real-time responses
        const streamGenerator = streamMessage(userMessage)
        
        // Add initial assistant message
        addMessage({
          content: '',
          role: 'assistant'
        })

        for await (const chunk of streamGenerator) {
          // TODO: Update the assistant message with accumulated content
          // This would require updating the store to handle message updates
          console.log('Stream chunk:', chunk.content)
        }
      } else {
        // Use standard message sending
        const response = await sendMessage(userMessage)
        
        addMessage({
          content: response.message,
          role: 'assistant'
        })
      }
    } catch (error) {
      // Add error message
      addMessage({
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        role: 'assistant',
        isError: true
      })
    } finally {
      setTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (!isOpen) return null

  const showHealthStatus = healthData && !healthLoading

  return (
    <div
      ref={panelRef}
      className={cn(
        "fixed bg-[#252526] border border-[#3c3c3c] rounded-lg shadow-2xl z-50 flex flex-col",
        "transition-all duration-200 ease-in-out",
        isDetached && !isDragging && "shadow-2xl",
        isDragging && "cursor-move",
        className
      )}
      style={{
        left: isDetached ? position.x : undefined,
        top: isDetached ? position.y : undefined,
        width: size.width,
        height: isMinimized ? 'auto' : size.height,
        right: !isDetached ? 20 : undefined,
        bottom: !isDetached ? 20 : undefined,
        cursor: isDetached ? "move" : undefined
      }}
    >
      {/* Header */}
      <div
        ref={dragHandleRef}
        className={cn(
          "flex items-center justify-between p-3 border-b border-[#3c3c3c] bg-[#2d2d30]",
          "rounded-t-lg cursor-move select-none"
        )}
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-[#007acc]" />
          <span className="text-sm font-medium text-[#cccccc]">
            PLC-GBT Assistant
          </span>
          {showHealthStatus && (
            <div className={cn(
              "w-2 h-2 rounded-full",
              healthData.status === 'healthy' ? 'bg-green-500' :
              healthData.status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
            )} />
          )}
        </div>
        
        <div className="flex items-center gap-1">
          {/* Dock to sidebar button (only when detached) */}
          {isDetached && (
            <button
              onClick={handleDockToSidebar}
              className="p-1 hover:bg-[#3c3c3c] rounded text-[#cccccc] hover:text-white transition-colors"
              title="Dock to sidebar (Ctrl+Shift+A)"
            >
              <Sidebar className="w-4 h-4" />
            </button>
          )}
          
          {/* Traditional dock/detach button */}
          <button
            onClick={() => isDetached ? attachPanel('right') : detachPanel()}
            className="p-1 hover:bg-[#3c3c3c] rounded text-[#cccccc] hover:text-white transition-colors"
            title={isDetached ? "Dock to right edge" : "Detach Panel"}
          >
            {isDetached ? <Pin className="w-4 h-4" /> : <PinOff className="w-4 h-4" />}
          </button>
          
          {/* Minimize button */}
          <button
            onClick={() => isMinimized ? maximizePanel() : minimizePanel()}
            className="p-1 hover:bg-[#3c3c3c] rounded text-[#cccccc] hover:text-white transition-colors"
            title={isMinimized ? "Maximize" : "Minimize"}
          >
            <Minimize2 className="w-4 h-4" />
          </button>
          
          {/* Close button */}
          <button
            onClick={togglePanel}
            className="p-1 hover:bg-[#3c3c3c] rounded text-[#cccccc] hover:text-white transition-colors"
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* System Status Banner */}
          {showHealthStatus && healthData.status !== 'healthy' && (
            <div className={cn(
              "px-3 py-2 text-xs border-b border-[#3c3c3c]",
              healthData.status === 'degraded' ? 'bg-yellow-900/20 text-yellow-300' : 'bg-red-900/20 text-red-300'
            )}>
              System Status: {healthData.status.toUpperCase()}
              {healthError && ` - ${healthError.message}`}
            </div>
          )}

          {/* Error Banner */}
          {chatError && (
            <div className="px-3 py-2 text-xs bg-red-900/20 text-red-300 border-b border-[#3c3c3c]">
              Connection Error: {chatError.message}
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
            {messages.length === 0 ? (
              <div className="text-center text-[#969696] text-sm py-8">
                <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Hello! I&apos;m your PLC-GBT Assistant.</p>
                <p className="text-xs mt-1">Ask me about industrial automation, control loops, or PLC programming.</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex gap-3 text-sm",
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <div className="w-6 h-6 rounded-full bg-[#007acc] flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Bot className="w-3 h-3 text-white" />
                    </div>
                  )}
                  
                  <div
                    className={cn(
                      "max-w-[80%] p-3 rounded-lg",
                      message.role === 'user'
                        ? "bg-[#007acc] text-white ml-auto"
                        : cn(
                            "bg-[#3c3c3c] text-[#cccccc]",
                            message.isError && "bg-red-900/30 text-red-300"
                          )
                    )}
                  >
                    <div className="whitespace-pre-wrap break-words">
                      {message.content}
                    </div>
                    <div className="text-xs opacity-70 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  
                  {message.role === 'user' && (
                    <div className="w-6 h-6 rounded-full bg-[#00d4aa] flex items-center justify-center flex-shrink-0 mt-0.5">
                      <User className="w-3 h-3 text-white" />
                    </div>
                  )}
                </div>
              ))
            )}
            
            {isTyping && (
              <div className="flex gap-3 text-sm">
                <div className="w-6 h-6 rounded-full bg-[#007acc] flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot className="w-3 h-3 text-white" />
                </div>
                <div className="bg-[#3c3c3c] text-[#cccccc] p-3 rounded-lg">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-[#007acc] animate-bounce" />
                    <div className="w-2 h-2 rounded-full bg-[#007acc] animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 rounded-full bg-[#007acc] animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-[#3c3c3c] p-3">
            <div className="flex gap-2">
              <textarea
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about PLCs, control loops, or industrial automation..."
                className="flex-1 bg-[#3c3c3c] text-[#cccccc] border border-[#525252] rounded px-3 py-2 text-sm placeholder-[#969696] resize-none focus:outline-none focus:border-[#007acc] focus:ring-1 focus:ring-[#007acc]"
                rows={2}
                disabled={chatLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!currentInput.trim() || chatLoading}
                className="px-3 py-2 bg-[#007acc] text-white rounded hover:bg-[#005a9e] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                title="Send Message"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            
            {userPreferences.showTimestamps && (
              <div className="text-xs text-[#969696] mt-1">
                Connected to PLC-GBT API at localhost:8000
              </div>
            )}
          </div>
        </>
      )}

      {/* Resize Handle */}
      {isDetached && !isMinimized && (
        <div
          ref={resizeHandleRef}
          className="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize bg-[#525252] hover:bg-[#007acc] transition-colors"
          style={{
            clipPath: 'polygon(100% 0%, 0% 100%, 100% 100%)'
          }}
          onMouseDown={(e) => {
            e.stopPropagation()
            setResizeStart({
              x: e.clientX,
              y: e.clientY,
              width: size.width,
              height: size.height
            })
            startResizing()
          }}
        />
      )}
    </div>
  )
} 