'use client'

import { useState, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'

// Use static timestamps to avoid hydration mismatches
const STATIC_TIMESTAMP = '12:30 PM' // This will be replaced client-side

const mockMessages = [
  { id: '1', role: 'assistant' as const, content: 'Hello! I\'m your PLC-GBT AI assistant. How can I help you with your industrial automation tasks today?', timestamp: STATIC_TIMESTAMP },
  { id: '2', role: 'user' as const, content: 'Can you help me tune a PID controller?', timestamp: STATIC_TIMESTAMP },
  { id: '3', role: 'assistant' as const, content: 'I\'d be happy to help you tune your PID controller! Could you provide me with some details about your process? What are you trying to control (temperature, pressure, flow rate, etc.)?', timestamp: STATIC_TIMESTAMP },
]

export function ChatPanel() {
  const [messages, setMessages] = useState(mockMessages)

  // Update with real timestamps after hydration
  useEffect(() => {
    const now = new Date()
    setMessages(prev => prev.map((msg, index) => ({
      ...msg,
      timestamp: new Date(now.getTime() - (prev.length - index) * 60000).toLocaleTimeString()
    })))
  }, [])

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-2 border-b border-[#3c3c3c]">
        <div className="flex items-center space-x-2">
          <Bot className="w-4 h-4 text-[#569cd6]" />
          <span className="text-[#cccccc] text-sm font-medium">AI Assistant</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-2 space-y-3">
        {messages.map((message) => (
          <div key={message.id} className="flex space-x-2">
            <div className="w-6 h-6 rounded-full bg-[#3c3c3c] flex items-center justify-center flex-shrink-0">
              {message.role === 'assistant' ? (
                <Bot className="w-4 h-4 text-[#569cd6]" />
              ) : (
                <User className="w-4 h-4 text-[#cccccc]" />
              )}
            </div>
            <div className="flex-1">
              <div className="text-[#cccccc] text-sm leading-relaxed">
                {message.content}
              </div>
              <div className="text-[#969696] text-xs mt-1" suppressHydrationWarning>
                {message.timestamp}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="p-2 border-t border-[#3c3c3c]">
        <div className="flex space-x-2">
          <input
            type="text"
            placeholder="Ask about PID tuning, control loops, or industrial automation..."
            className="flex-1 px-3 py-2 bg-[#3c3c3c] text-[#cccccc] placeholder-[#969696] rounded border border-[#3c3c3c] focus:border-[#007acc] focus:outline-none text-sm"
          />
          <button className="w-8 h-8 flex items-center justify-center bg-[#007acc] text-white rounded hover:bg-[#005a9e] transition-colors">
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
} 