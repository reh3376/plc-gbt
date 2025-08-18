'use client';

import { cn } from '@/lib/utils/cn';
import { FolderOpen, Save, X } from 'lucide-react';
import React, { useState } from 'react';
import { createPortal } from 'react-dom';

interface SaveWorkflowModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly onSave: (options: SaveOptions) => Promise<void>;
  readonly currentWorkflowName?: string;
}

interface SaveOptions {
  readonly name: string;
  readonly location: 'local' | 'remote';
  readonly filepath?: string;
}

export function SaveWorkflowModal({
  isOpen,
  onClose,
  onSave,
  currentWorkflowName = 'Untitled Workflow',
}: Readonly<SaveWorkflowModalProps>): React.JSX.Element | null {
  const [workflowName, setWorkflowName] = useState(currentWorkflowName);
  const [saveLocation, setSaveLocation] = useState<'local' | 'remote'>('local');
  const [customPath, setCustomPath] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!workflowName.trim()) {
      alert('Please enter a workflow name');
      return;
    }

    setIsSaving(true);
    try {
      await onSave({
        name: workflowName.trim(),
        location: saveLocation,
        filepath: customPath.trim() || undefined,
      });
      onClose();
    } catch (error) {
      console.error('Save failed:', error);
      alert(`Save failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleBrowsePath = () => {
    // TODO: Implement file path browser
    alert('File path browser not yet implemented');
  };

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-[#2d2d2d] border border-[#404040] rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#404040]">
          <div className="flex items-center space-x-2">
            <Save className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">Save Workflow</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            disabled={isSaving}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Workflow Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Workflow Name</label>
            <input
              type="text"
              value={workflowName}
              onChange={e => setWorkflowName(e.target.value)}
              className="w-full px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter workflow name..."
              disabled={isSaving}
            />
          </div>

          {/* Save Location */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Save Location</label>
            <div className="flex space-x-2">
              <button
                onClick={() => setSaveLocation('local')}
                className={cn(
                  'flex-1 px-3 py-2 rounded border transition-colors',
                  saveLocation === 'local'
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-[#1e1e1e] border-[#404040] text-gray-300 hover:border-gray-300'
                )}
                disabled={isSaving}
              >
                Local Storage
              </button>
              <button
                onClick={() => setSaveLocation('remote')}
                className={cn(
                  'flex-1 px-3 py-2 rounded border transition-colors',
                  saveLocation === 'remote'
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-[#1e1e1e] border-[#404040] text-gray-300 hover:border-gray-300'
                )}
                disabled={isSaving}
              >
                Backend Server
              </button>
            </div>
          </div>

          {/* Custom Path (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Custom Path (Optional)
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={customPath}
                onChange={e => setCustomPath(e.target.value)}
                className="flex-1 px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Leave empty for default location..."
                disabled={isSaving}
              />
              <button
                onClick={handleBrowsePath}
                className="px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-gray-300 hover:text-white hover:border-gray-300 transition-colors"
                disabled={isSaving}
              >
                <FolderOpen className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Save Location Info */}
          <div className="text-xs text-gray-400 bg-[#1e1e1e] border border-[#404040] rounded p-2">
            {saveLocation === 'local' ? (
              <>
                <strong>Local Storage:</strong> Workflow will be saved to your browser&apos;s local
                storage and project-files/workflows/ directory.
              </>
            ) : (
              <>
                <strong>Backend Server:</strong> Workflow will be saved to the remote server
                database with API persistence.
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-2 p-4 border-t border-[#404040]">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
            disabled={isSaving}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || !workflowName.trim()}
            className={cn(
              'px-4 py-2 rounded transition-colors flex items-center space-x-2',
              isSaving || !workflowName.trim()
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            )}
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'Saving...' : 'Save Workflow'}</span>
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
