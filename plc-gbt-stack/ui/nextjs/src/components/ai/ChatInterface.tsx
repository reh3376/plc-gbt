'use client';

import { useChat } from '@/lib/hooks/useApi';
import { useAIAssistantStore } from '@/lib/stores/ai-assistant-store';
import { cn } from '@/lib/utils/cn';
import { Bot, History, Save, Send, Trash2, User } from 'lucide-react';
import { useEffect, useState } from 'react';
import { ChatHistoryBrowser } from './ChatHistoryBrowser';
import { ConfirmDialog } from './ConfirmDialog';
import { SaveChatDialog } from './SaveChatDialog';

interface ChatInterfaceProps {
  className?: string;
  showHeader?: boolean;
  showSystemStatus?: boolean;
  variant?: 'floating' | 'sidebar';
}

export function ChatInterface({
  className,
  showHeader = false,
  showSystemStatus = true,
  variant = 'sidebar',
}: ChatInterfaceProps) {
  // Use selective subscription to prevent unnecessary re-renders
  const messages = useAIAssistantStore(state => state.messages);
  const isTyping = useAIAssistantStore(state => state.isTyping);
  const currentInput = useAIAssistantStore(state => state.currentInput);
  const userPreferences = useAIAssistantStore(state => state.userPreferences);
  const addMessage = useAIAssistantStore(state => state.addMessage);
  const updateMessage = useAIAssistantStore(state => state.updateMessage);
  const clearMessages = useAIAssistantStore(state => state.clearMessages);
  const setCurrentInput = useAIAssistantStore(state => state.setCurrentInput);
  const setTyping = useAIAssistantStore(state => state.setTyping);

  // API Integration
  const { sendMessage, streamMessage, loading: chatLoading, error: chatError } = useChat();

  // Chat history management state
  const [showHistoryBrowser, setShowHistoryBrowser] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Clear chat history with confirmation
  const handleClearHistory = () => {
    if (messages.length === 0) return;
    setShowClearConfirm(true);
  };

  const confirmClearHistory = () => {
    clearMessages();
    setCurrentInput('');
    setShowClearConfirm(false);
  };

  // Save chat history to filesystem
  const handleSaveHistory = () => {
    if (messages.length === 0) {
      return;
    }
    setShowSaveDialog(true);
  };

  const confirmSaveHistory = async (chatName: string) => {
    setShowSaveDialog(false);
    setIsSaving(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/ai/chat/history/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: chatName,
          messages: messages.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp,
          })),
          metadata: {
            savedAt: new Date().toISOString(),
            messageCount: messages.length,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to save chat history: ${response.statusText}`);
      }

      const result = await response.json();
      // Success - no need to alert, the save dialog is already closed
      console.log(
        `Chat history saved successfully to: ${result.data?.filePath || 'chat-histories/'}`
      );
    } catch (error) {
      console.error('Failed to save chat history:', error);
      // For errors, we could add a toast notification system later
    } finally {
      setIsSaving(false);
    }
  };

  // Toggle history browser
  const handleToggleHistoryBrowser = () => {
    setShowHistoryBrowser(!showHistoryBrowser);
  };

  // Load chat history from browser
  const handleLoadChatHistory = (messages: any[]) => {
    // Clear current messages
    clearMessages();

    // Add loaded messages to the store
    messages.forEach(msg => {
      addMessage({
        role: msg.role,
        content: msg.content,
      });
    });
  };

  // Handle message sending with real API
  const handleSendMessage = async () => {
    if (!currentInput.trim() || chatLoading) return;

    const userMessage = currentInput.trim();
    setCurrentInput('');

    // Add user message to local state
    addMessage({
      content: userMessage,
      role: 'user',
    });

    try {
      setTyping(true);

      if (userPreferences.enableStreaming) {
        // Use streaming for real-time responses
        const streamGenerator = streamMessage(userMessage);

        // Create a placeholder message and capture its ID
        addMessage({
          content: '',
          role: 'assistant',
          isStreaming: true,
        });

        // Get the messages from the store to find the newly added message ID
        // We need to use a timeout to let the store update
        await new Promise(resolve => setTimeout(resolve, 0));
        const currentMessages = useAIAssistantStore.getState().messages;
        const newMessage = currentMessages[currentMessages.length - 1];
        const assistantMessageId = newMessage?.id;

        if (!assistantMessageId) {
          throw new Error('Failed to create assistant message');
        }

        let accumulatedContent = '';

        try {
          // Properly handle AsyncGenerator from streamMessage
          for await (const chunk of streamGenerator) {
            if (chunk.done) {
              // Stream completed
              break;
            }

            // Accumulate the content
            accumulatedContent += chunk.content;

            // Update the existing message with accumulated content
            updateMessage(assistantMessageId, {
              content: accumulatedContent,
              isStreaming: true,
            });
          }

          // Mark streaming as complete
          updateMessage(assistantMessageId, {
            isStreaming: false,
          });
        } catch (streamError) {
          console.error('Streaming error:', streamError);
          // Update the placeholder message with error
          updateMessage(assistantMessageId, {
            content: `Streaming error: ${
              streamError instanceof Error ? streamError.message : 'Unknown streaming error'
            }`,
            isError: true,
            isStreaming: false,
          });
        }
      } else {
        // Use standard message sending
        const response = await sendMessage(userMessage);

        addMessage({
          content: response.message,
          role: 'assistant',
        });
      }
    } catch (error) {
      // Add error message
      addMessage({
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        role: 'assistant',
        isError: true,
      });
    } finally {
      setTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div
      className={cn(
        'flex flex-col h-full relative',
        variant === 'floating' ? 'bg-[#252526]' : 'bg-transparent',
        className
      )}
    >
      {/* Chat History Browser Overlay */}
      {showHistoryBrowser && (
        <ChatHistoryBrowser
          onClose={() => setShowHistoryBrowser(false)}
          onLoad={handleLoadChatHistory}
        />
      )}

      {/* Save Chat Dialog */}
      {showSaveDialog && (
        <SaveChatDialog
          defaultName={`Chat ${new Date().toLocaleString()}`}
          onSave={confirmSaveHistory}
          onCancel={() => setShowSaveDialog(false)}
        />
      )}

      {/* Clear Confirmation Dialog */}
      {showClearConfirm && (
        <ConfirmDialog
          title="Clear Chat History"
          message="Are you sure you want to clear the current chat history? This cannot be undone."
          confirmText="Clear"
          cancelText="Cancel"
          variant="danger"
          onConfirm={confirmClearHistory}
          onCancel={() => setShowClearConfirm(false)}
        />
      )}

      {/* Header - only shown if requested */}
      {showHeader && (
        <div className="flex items-center gap-2 p-3 border-b border-[#3c3c3c] bg-[#2d2d30]">
          <Bot className="w-4 h-4 text-[#007acc]" />
          <span className="text-sm font-medium text-[#cccccc]">PLC-GBT Assistant</span>
        </div>
      )}

      {/* Chat History Toolbar - Always visible */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[#3c3c3c] bg-[#252526]">
        <div className="flex items-center gap-1">
          <button
            onClick={handleClearHistory}
            disabled={messages.length === 0}
            className={cn(
              'p-1.5 rounded transition-colors text-xs flex items-center gap-1',
              messages.length === 0
                ? 'text-[#6e6e6e] cursor-not-allowed'
                : 'text-[#cccccc] hover:bg-[#3c3c3c] hover:text-white'
            )}
            title="Clear current chat history"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear</span>
          </button>

          <button
            onClick={handleSaveHistory}
            disabled={messages.length === 0 || isSaving}
            className={cn(
              'p-1.5 rounded transition-colors text-xs flex items-center gap-1',
              messages.length === 0 || isSaving
                ? 'text-[#6e6e6e] cursor-not-allowed'
                : 'text-[#cccccc] hover:bg-[#3c3c3c] hover:text-white'
            )}
            title="Save current chat history"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Saving...' : 'Save'}</span>
          </button>

          <button
            onClick={handleToggleHistoryBrowser}
            className="p-1.5 rounded transition-colors text-xs flex items-center gap-1 text-[#cccccc] hover:bg-[#3c3c3c] hover:text-white"
            title="Browse saved chat histories"
          >
            <History className="w-3.5 h-3.5" />
            <span>History</span>
          </button>
        </div>

        <div className="text-xs text-[#969696]">
          {messages.length} {messages.length === 1 ? 'message' : 'messages'}
        </div>
      </div>

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
            <p className="text-xs mt-1">
              Ask me about industrial automation, control loops, or PLC programming.
            </p>
          </div>
        ) : (
          messages.map(message => (
            <div
              key={message.id}
              className={cn(
                'flex gap-3 text-sm',
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
                  'max-w-[80%] p-3 rounded-lg',
                  message.role === 'user'
                    ? 'bg-[#007acc] text-white ml-auto'
                    : cn(
                        'bg-[#3c3c3c] text-[#cccccc]',
                        message.isError && 'bg-red-900/30 text-red-300'
                      )
                )}
              >
                <div className="whitespace-pre-wrap break-words">{message.content}</div>
                {userPreferences.showTimestamps && (
                  <div className="text-xs opacity-70 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                )}
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
                <div
                  className="w-2 h-2 rounded-full bg-[#007acc] animate-bounce"
                  style={{ animationDelay: '0.1s' }}
                />
                <div
                  className="w-2 h-2 rounded-full bg-[#007acc] animate-bounce"
                  style={{ animationDelay: '0.2s' }}
                />
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
            onChange={e => setCurrentInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about PLCs, control loops, or industrial automation..."
            className="flex-1 bg-[#3c3c3c] text-[#cccccc] border border-[#525252] rounded px-3 py-2 text-sm placeholder-[#969696] resize-none focus:outline-none focus:border-[#007acc] focus:ring-1 focus:ring-[#007acc]"
            rows={variant === 'floating' ? 2 : 1}
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

        {userPreferences.showTimestamps && variant === 'floating' && (
          <div className="text-xs text-[#969696] mt-1">
            Connected to PLC-GBT API at localhost:8000
          </div>
        )}
      </div>
    </div>
  );
}
