'use client';

import { cn } from '@/lib/utils/cn';
import { Clock, MessageSquare, Trash2, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { ConfirmDialog } from './ConfirmDialog';

interface ChatHistoryItem {
  fileId: string;
  filename: string;
  name: string;
  messageCount: number;
  savedAt: string;
  path: string;
}

interface ChatHistoryBrowserProps {
  readonly onClose: () => void;
  readonly onLoad: (messages: any[]) => void;
}

export function ChatHistoryBrowser({ onClose, onLoad }: ChatHistoryBrowserProps) {
  const [histories, setHistories] = useState<ChatHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ fileId: string; name: string } | null>(null);

  // Load chat histories on mount
  useEffect(() => {
    loadHistories();
  }, []);

  const loadHistories = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/ai/chat/history/list');
      if (!response.ok) {
        throw new Error(`Failed to load histories: ${response.statusText}`);
      }

      const result = await response.json();
      setHistories(result.data?.histories || []);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMsg);
      console.error('Failed to load chat histories:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadHistory = async (fileId: string) => {
    console.log('[ChatHistoryBrowser] Loading chat history:', fileId);
    try {
      const url = `http://localhost:8000/api/v1/ai/chat/history/${fileId}`;
      console.log('[ChatHistoryBrowser] Fetching from:', url);

      const response = await fetch(url);
      console.log('[ChatHistoryBrowser] Response status:', response.status);

      if (!response.ok) {
        throw new Error(`Failed to load history: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('[ChatHistoryBrowser] Response data:', result);

      const chatData = result.data;

      if (chatData?.messages) {
        console.log('[ChatHistoryBrowser] Found messages:', chatData.messages.length);

        // Convert timestamps back to Date objects
        const messages = chatData.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
          id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`,
        }));

        console.log('[ChatHistoryBrowser] Calling onLoad with messages:', messages);
        onLoad(messages);
        onClose();
      } else {
        console.warn('[ChatHistoryBrowser] No messages found in chat data');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      console.error('[ChatHistoryBrowser] Error loading chat history:', err);
      alert(`Failed to load chat history: ${errorMsg}`);
    }
  };

  const handleDeleteHistory = async (fileId: string, name: string, event: React.MouseEvent) => {
    event.stopPropagation();
    setDeleteConfirm({ fileId, name });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      const { fileId } = deleteConfirm;
      const response = await fetch(`http://localhost:8000/api/v1/ai/chat/history/${fileId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete history: ${response.statusText}`);
      }

      // Reload histories after deletion
      await loadHistories();
      setDeleteConfirm(null);
    } catch (err) {
      console.error('Failed to delete chat history:', err);
      // Could add toast notification here
      setDeleteConfirm(null);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Unknown date';
    }
  };

  return (
    <div className="absolute inset-0 bg-[#252526] z-10 flex flex-col">
      {/* Delete Confirmation Dialog */}
      {deleteConfirm && (
        <ConfirmDialog
          title="Delete Chat History"
          message={`Are you sure you want to delete "${deleteConfirm.name}"? This cannot be undone.`}
          confirmText="Delete"
          cancelText="Cancel"
          variant="danger"
          onConfirm={confirmDelete}
          onCancel={() => setDeleteConfirm(null)}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-[#3c3c3c] bg-[#2d2d30]">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-[#007acc]" />
          <span className="text-sm font-medium text-[#cccccc]">Chat History</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-[#3c3c3c] rounded transition-colors"
          title="Close history browser"
        >
          <X className="w-4 h-4 text-[#cccccc]" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3">
        {loading && (
          <div className="text-center text-[#969696] py-8">
            <div className="animate-spin w-8 h-8 border-2 border-[#007acc] border-t-transparent rounded-full mx-auto mb-2" />
            <p>Loading chat histories...</p>
          </div>
        )}

        {error && (
          <div className="text-center text-red-400 py-8">
            <p>Error: {error}</p>
            <button
              onClick={loadHistories}
              className="mt-2 px-3 py-1 bg-[#3c3c3c] hover:bg-[#505050] rounded text-sm transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && histories.length === 0 && (
          <div className="text-center text-[#969696] py-8">
            <Clock className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>No saved chat histories</p>
            <p className="text-xs mt-1">Save your conversations to access them later</p>
          </div>
        )}

        {!loading && !error && histories.length > 0 && (
          <div className="space-y-2">
            {histories.map(history => (
              <div
                key={history.fileId}
                onClick={() => setSelectedHistoryId(history.fileId)}
                onKeyDown={e => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setSelectedHistoryId(history.fileId);
                  }
                }}
                role="button"
                tabIndex={0}
                className={cn(
                  'p-3 rounded border cursor-pointer transition-all focus:outline-none focus:ring-2 focus:ring-[#007acc]',
                  selectedHistoryId === history.fileId
                    ? 'bg-[#094771] border-[#007acc]'
                    : 'bg-[#2d2d30] border-[#3c3c3c] hover:border-[#007acc] hover:bg-[#3c3c3c]'
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <MessageSquare className="w-3.5 h-3.5 text-[#007acc] flex-shrink-0" />
                      <span className="text-sm font-medium text-[#cccccc] truncate">
                        {history.name}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-[#969696]">
                      <span>{history.messageCount} messages</span>
                      <span>•</span>
                      <span>{formatDate(history.savedAt)}</span>
                    </div>
                  </div>
                  <button
                    onClick={e => handleDeleteHistory(history.fileId, history.name, e)}
                    className="p-1 hover:bg-red-900/30 rounded transition-colors flex-shrink-0"
                    title="Delete history"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer with Load Button */}
      <div className="p-3 border-t border-[#3c3c3c] bg-[#2d2d30] flex items-center justify-between gap-3">
        <div className="text-xs text-[#969696]">
          {histories.length} {histories.length === 1 ? 'history' : 'histories'}
          {selectedHistoryId && ' • 1 selected'}
        </div>
        <button
          onClick={() => selectedHistoryId && handleLoadHistory(selectedHistoryId)}
          disabled={!selectedHistoryId}
          className={cn(
            'px-4 py-1.5 rounded text-sm font-medium transition-colors',
            selectedHistoryId
              ? 'bg-[#007acc] hover:bg-[#005a9e] text-white'
              : 'bg-[#3c3c3c] text-[#696969] cursor-not-allowed'
          )}
        >
          Load Selected
        </button>
      </div>
    </div>
  );
}
