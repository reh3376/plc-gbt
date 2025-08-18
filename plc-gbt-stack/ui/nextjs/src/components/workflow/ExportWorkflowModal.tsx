'use client';

import { cn } from '@/lib/utils/cn';
import { Download, FolderOpen, X } from 'lucide-react';
import React, { useState } from 'react';
import { createPortal } from 'react-dom';

interface ExportWorkflowModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly onExport: (options: ExportOptions) => Promise<void>;
  readonly currentWorkflowName?: string;
}

interface ExportOptions {
  readonly name: string;
  readonly format: 'json' | 'xml' | 'n8n';
  readonly location: 'local' | 'remote';
  readonly filepath?: string;
}

export function ExportWorkflowModal({
  isOpen,
  onClose,
  onExport,
  currentWorkflowName = 'Untitled Workflow',
}: Readonly<ExportWorkflowModalProps>): React.JSX.Element | null {
  const [filename, setFilename] = useState(currentWorkflowName);
  const [format, setFormat] = useState<'json' | 'xml' | 'n8n'>('json');
  const [exportLocation, setExportLocation] = useState<'local' | 'remote'>('local');
  const [customPath, setCustomPath] = useState('');
  const [isExporting, setIsExporting] = useState(false);

  if (!isOpen) return null;

  const handleExport = async () => {
    if (!filename.trim()) {
      alert('Please enter a filename');
      return;
    }

    setIsExporting(true);
    try {
      await onExport({
        name: filename.trim(),
        format,
        location: exportLocation,
        filepath: customPath.trim() || undefined,
      });
      onClose();
    } catch (error) {
      console.error('Export failed:', error);
      alert(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleBrowsePath = () => {
    // TODO: Implement file path browser
    alert('File path browser not yet implemented');
  };

  const formatOptions = [
    { value: 'json', label: 'JSON', description: 'Standard JSON format' },
    { value: 'xml', label: 'XML', description: 'XML format for legacy systems' },
    { value: 'n8n', label: 'N8N', description: 'N8N workflow format' },
  ] as const;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-[#2d2d2d] border border-[#404040] rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#404040]">
          <div className="flex items-center space-x-2">
            <Download className="w-5 h-5 text-green-400" />
            <h2 className="text-lg font-semibold text-white">Export Workflow</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            disabled={isExporting}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Filename */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Filename</label>
            <input
              type="text"
              value={filename}
              onChange={e => setFilename(e.target.value)}
              className="w-full px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter filename..."
              disabled={isExporting}
            />
          </div>

          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Export Format</label>
            <div className="space-y-2">
              {formatOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => setFormat(option.value)}
                  className={cn(
                    'w-full px-3 py-2 rounded border transition-colors text-left',
                    format === option.value
                      ? 'bg-green-600 border-green-500 text-white'
                      : 'bg-[#1e1e1e] border-[#404040] text-gray-300 hover:border-gray-300'
                  )}
                  disabled={isExporting}
                >
                  <div className="font-medium">{option.label}</div>
                  <div className="text-xs text-gray-400">{option.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Export Location */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Export Location</label>
            <div className="flex space-x-2">
              <button
                onClick={() => setExportLocation('local')}
                className={cn(
                  'flex-1 px-3 py-2 rounded border transition-colors',
                  exportLocation === 'local'
                    ? 'bg-green-600 border-green-500 text-white'
                    : 'bg-[#1e1e1e] border-[#404040] text-gray-300 hover:border-gray-300'
                )}
                disabled={isExporting}
              >
                Local Download
              </button>
              <button
                onClick={() => setExportLocation('remote')}
                className={cn(
                  'flex-1 px-3 py-2 rounded border transition-colors',
                  exportLocation === 'remote'
                    ? 'bg-green-600 border-green-500 text-white'
                    : 'bg-[#1e1e1e] border-[#404040] text-gray-300 hover:border-gray-300'
                )}
                disabled={isExporting}
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
                className="flex-1 px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Leave empty for default location..."
                disabled={isExporting}
              />
              <button
                onClick={handleBrowsePath}
                className="px-3 py-2 bg-[#1e1e1e] border border-[#404040] rounded text-gray-300 hover:text-white hover:border-gray-300 transition-colors"
                disabled={isExporting}
              >
                <FolderOpen className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Location Info */}
          <div className="text-xs text-gray-400 bg-[#1e1e1e] border border-[#404040] rounded p-2">
            {exportLocation === 'local' ? (
              <>
                <strong>Local Download:</strong> File will be downloaded to your browser&apos;s default
                download folder.
              </>
            ) : (
              <>
                <strong>Backend Server:</strong> File will be saved to the server&apos;s export
                directory.
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-2 p-4 border-t border-[#404040]">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
            disabled={isExporting}
          >
            Cancel
          </button>
          <button
            onClick={handleExport}
            disabled={isExporting || !filename.trim()}
            className={cn(
              'px-4 py-2 rounded transition-colors flex items-center space-x-2',
              isExporting || !filename.trim()
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            )}
          >
            <Download className="w-4 h-4" />
            <span>{isExporting ? 'Exporting...' : 'Export Workflow'}</span>
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
