'use client';

import { cn } from '@/lib/utils/cn';
import { FolderOpen, Upload, X } from 'lucide-react';
import React, { useState } from 'react';
import { createPortal } from 'react-dom';

interface ImportWorkflowModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly onImport: (options: ImportOptions) => Promise<void>;
}

interface ImportOptions {
  readonly location: 'local' | 'remote';
  readonly filepath?: string;
  readonly file?: File;
}

export function ImportWorkflowModal({
  isOpen,
  onClose,
  onImport,
}: Readonly<ImportWorkflowModalProps>): React.JSX.Element | null {
  const [importLocation, setImportLocation] = useState<'local' | 'remote'>('local');
  const [customPath, setCustomPath] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleBrowseFile = () => {
    fileInputRef.current?.click();
  };

  const handleBrowsePath = () => {
    // TODO: Implement file path browser for remote location
    alert('Remote file path browser not yet implemented');
  };

  const handleImport = async () => {
    if (importLocation === 'local' && !selectedFile) {
      alert('Please select a file to import');
      return;
    }

    if (importLocation === 'remote' && !customPath.trim()) {
      alert('Please enter a file path for remote import');
      return;
    }

    setIsImporting(true);
    try {
      await onImport({
        location: importLocation,
        filepath: customPath.trim() || undefined,
        file: selectedFile || undefined,
      });
      onClose();
      // Reset form
      setSelectedFile(null);
      setCustomPath('');
    } catch (error) {
      console.error('Import failed:', error);
      alert(`Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsImporting(false);
    }
  };

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        role="button"
        tabIndex={-1}
        onKeyDown={e => {
          if (e.key === 'Escape') onClose();
        }}
      />

      {/* Modal */}
      <div className="relative bg-[#2d2d2d] border border-[#404040] rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#404040]">
          <div className="flex items-center space-x-2">
            <Upload className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">Import Workflow</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            disabled={isImporting}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Import Location */}
          <div>
            <label htmlFor="import-location" className="block text-sm font-medium text-gray-300 mb-2">
              Import Location
            </label>
            <div className="flex space-x-2">
              <button
                onClick={() => setImportLocation('local')}
                className={cn(
                  'flex-1 px-3 py-2 rounded border transition-colors',
                  importLocation === 'local'
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-[#1e1e1e] border-[#404040] text-gray-300 hover:border-gray-300'
                )}
                disabled={isImporting}
              >
                Local File
              </button>
              <button
                onClick={() => setImportLocation('remote')}
                className={cn(
                  'flex-1 px-3 py-2 rounded border transition-colors',
                  importLocation === 'remote'
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-[#1e1e1e] border-[#404040] text-gray-300 hover:border-gray-300'
                )}
                disabled={isImporting}
              >
                Backend Server
              </button>
            </div>
          </div>

          {/* Local File Selection */}
          {importLocation === 'local' && (
            <div>
              <label htmlFor="file-select" className="block text-sm font-medium text-gray-300 mb-2">
                Select Workflow File
              </label>
              <div className="flex space-x-2">
                <div className="flex-1 px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-gray-300 text-sm">
                  {selectedFile ? selectedFile.name : 'No file selected'}
                </div>
                <button
                  onClick={handleBrowseFile}
                  className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors flex items-center space-x-1"
                  disabled={isImporting}
                >
                  <FolderOpen className="w-4 h-4" />
                  <span>Browse</span>
                </button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".json,.xml,.workflow"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
          )}

          {/* Remote Path Selection */}
          {importLocation === 'remote' && (
            <div>
              <label htmlFor="remote-path" className="block text-sm font-medium text-gray-300 mb-2">
                Remote File Path
              </label>
              <div className="flex space-x-2">
                <input
                  id="remote-path"
                  type="text"
                  value={customPath}
                  onChange={e => setCustomPath(e.target.value)}
                  className="flex-1 px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter remote file path..."
                  disabled={isImporting}
                />
                <button
                  onClick={handleBrowsePath}
                  className="px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-gray-300 hover:text-white hover:border-gray-300 transition-colors"
                  disabled={isImporting}
                >
                  <FolderOpen className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Import Info */}
          <div className="text-xs text-gray-400 bg-[#1e1e1e] border border-[#404040] rounded p-2">
            {importLocation === 'local' ? (
              <>
                <strong>Local File:</strong> Select a workflow file (.json, .xml, .workflow) from your computer.
              </>
            ) : (
              <>
                <strong>Backend Server:</strong> Import workflow from the remote server file system.
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-2 p-4 border-t border-[#404040]">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
            disabled={isImporting}
          >
            Cancel
          </button>
          <button
            onClick={handleImport}
            disabled={
              isImporting ||
              (importLocation === 'local' && !selectedFile) ||
              (importLocation === 'remote' && !customPath.trim())
            }
            className={cn(
              'px-4 py-2 rounded transition-colors flex items-center space-x-2',
              isImporting ||
                (importLocation === 'local' && !selectedFile) ||
                (importLocation === 'remote' && !customPath.trim())
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            )}
          >
            <Upload className="w-4 h-4" />
            <span>{isImporting ? 'Importing...' : 'Import Workflow'}</span>
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
