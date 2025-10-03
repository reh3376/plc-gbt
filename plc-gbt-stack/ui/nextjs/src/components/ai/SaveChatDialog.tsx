'use client';

import { cn } from '@/lib/utils/cn';
import { X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface SaveChatDialogProps {
  onSave: (name: string) => void;
  onCancel: () => void;
  defaultName?: string;
}

export function SaveChatDialog({ onSave, onCancel, defaultName = '' }: SaveChatDialogProps) {
  const [chatName, setChatName] = useState(defaultName);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus();
    inputRef.current?.select();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatName.trim()) {
      onSave(chatName.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <div className="absolute inset-0 bg-black/50 z-20 flex items-center justify-center">
      <div
        className="bg-[#252526] border border-[#3c3c3c] rounded-lg shadow-xl w-full max-w-md mx-4"
        onKeyDown={handleKeyDown}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#3c3c3c]">
          <h3 className="text-sm font-medium text-[#cccccc]">Save Chat History</h3>
          <button
            onClick={onCancel}
            className="p-1 hover:bg-[#3c3c3c] rounded transition-colors"
            title="Cancel"
          >
            <X className="w-4 h-4 text-[#cccccc]" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-4">
          <label htmlFor="chat-name" className="block text-sm text-[#cccccc] mb-2">
            Enter a name for this chat history:
          </label>
          <input
            ref={inputRef}
            id="chat-name"
            type="text"
            value={chatName}
            onChange={e => setChatName(e.target.value)}
            className="w-full px-3 py-2 bg-[#1e1e1e] border border-[#3c3c3c] rounded text-[#cccccc] text-sm focus:outline-none focus:border-[#007acc]"
            placeholder="My Chat History"
          />

          {/* Buttons */}
          <div className="flex justify-end gap-2 mt-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm bg-[#3c3c3c] hover:bg-[#505050] text-[#cccccc] rounded transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!chatName.trim()}
              className={cn(
                'px-4 py-2 text-sm rounded transition-colors',
                chatName.trim()
                  ? 'bg-[#007acc] hover:bg-[#005a9e] text-white'
                  : 'bg-[#3c3c3c] text-[#6e6e6e] cursor-not-allowed'
              )}
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
