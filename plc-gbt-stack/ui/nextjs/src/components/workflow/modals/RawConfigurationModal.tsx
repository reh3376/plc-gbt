/**
 * Raw Configuration Modal - AI Task Orchestrator TypeScript Implementation
 *
 * @description Modal for editing raw JSON configuration
 * @compliance Strict TypeScript with OpenAPI Schema MCP validation
 * @features JSON editor, validation, import/export functionality
 */

'use client';

import { Download, Save, Upload, X } from 'lucide-react';
import React, { useCallback, useState } from 'react';

import { cn } from '@/lib/utils/cn';

interface RawConfigurationModalProps {
  readonly isOpen: boolean;
  readonly config: Record<string, unknown>;
  readonly title?: string;
  readonly onSave: (config: Record<string, unknown>) => void;
  readonly onClose: () => void;
  readonly onExport?: () => void;
  readonly onImport?: (config: Record<string, unknown>) => void;
}

export function RawConfigurationModal({
  isOpen,
  config,
  title = 'Raw Configuration',
  onSave,
  onClose,
  onExport,
  onImport,
}: Readonly<RawConfigurationModalProps>): React.JSX.Element | null {
  const [editedConfig, setEditedConfig] = useState(JSON.stringify(config, null, 2));
  const [isValid, setIsValid] = useState(true);
  const [parseError, setParseError] = useState<string>('');

  // Validate JSON on change
  const handleConfigChange = useCallback((value: string) => {
    setEditedConfig(value);

    try {
      JSON.parse(value);
      setIsValid(true);
      setParseError('');
    } catch (error) {
      setIsValid(false);
      setParseError(error instanceof Error ? error.message : 'Invalid JSON');
    }
  }, []);

  // Save configuration
  const handleSave = useCallback(() => {
    if (!isValid) return;

    try {
      const parsedConfig = JSON.parse(editedConfig);
      onSave(parsedConfig);
      onClose();
    } catch (error) {
      setParseError(error instanceof Error ? error.message : 'Failed to save configuration');
    }
  }, [editedConfig, isValid, onSave, onClose]);

  // Handle file import
  const handleFileImport = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = e => {
        try {
          const content = e.target?.result as string;
          const parsedConfig = JSON.parse(content);
          setEditedConfig(JSON.stringify(parsedConfig, null, 2));
          setIsValid(true);
          setParseError('');

          if (onImport) {
            onImport(parsedConfig);
          }
        } catch (error) {
          setParseError(error instanceof Error ? error.message : 'Invalid JSON file');
        }
      };
      reader.readAsText(file);
    },
    [onImport]
  );

  // Export configuration
  const handleExport = useCallback(() => {
    if (!isValid) return;

    try {
      const dataStr = editedConfig;
      const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
      const exportFileDefaultName = 'node-configuration.json';

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();

      if (onExport) {
        onExport();
      }
    } catch (error) {
      setParseError(error instanceof Error ? error.message : 'Export failed');
    }
  }, [editedConfig, isValid, onExport]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[1200]">
      <div className="bg-[#2d2d2d] border border-[#404040] rounded-lg w-full max-w-4xl mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#404040]">
          <h3 className="text-lg font-medium text-white">{title}</h3>

          <div className="flex items-center gap-2">
            {/* Import Button */}
            <label className="flex items-center gap-2 px-3 py-1 text-sm text-gray-400 hover:text-white hover:bg-[#3d3d3d] rounded cursor-pointer transition-colors">
              <Upload className="w-4 h-4" />
              Import
              <input type="file" accept=".json" onChange={handleFileImport} className="hidden" />
            </label>

            {/* Export Button */}
            <button
              onClick={handleExport}
              disabled={!isValid}
              className={cn(
                'flex items-center gap-2 px-3 py-1 text-sm rounded transition-colors',
                isValid
                  ? 'text-gray-400 hover:text-white hover:bg-[#3d3d3d]'
                  : 'text-gray-600 cursor-not-allowed'
              )}
            >
              <Download className="w-4 h-4" />
              Export
            </button>

            {/* Close Button */}
            <button onClick={onClose} className="p-1 hover:bg-[#3d3d3d] rounded transition-colors">
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {/* JSON Editor */}
          <div className="flex-1 p-4">
            <textarea
              value={editedConfig}
              onChange={e => handleConfigChange(e.target.value)}
              className={cn(
                'w-full h-full resize-none font-mono text-sm',
                'bg-[#1e1e1e] border rounded-lg p-4',
                'text-white placeholder-gray-500',
                'focus:outline-none focus:ring-2',
                isValid
                  ? 'border-[#404040] focus:ring-blue-500/50'
                  : 'border-red-500 focus:ring-red-500/50'
              )}
              placeholder="Enter JSON configuration..."
              spellCheck={false}
            />
          </div>

          {/* Error Display */}
          {parseError && (
            <div className="mx-4 mb-4 p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
              <div className="flex items-center gap-2 text-red-400 text-sm">
                <X className="w-4 h-4" />
                <span className="font-medium">JSON Parse Error:</span>
              </div>
              <p className="text-red-300 text-sm mt-1">{parseError}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-[#404040]">
          <div className="text-sm text-gray-400">
            {isValid ? (
              <span className="text-green-400">✓ Valid JSON</span>
            ) : (
              <span className="text-red-400">✗ Invalid JSON</span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
            >
              Cancel
            </button>

            <button
              onClick={handleSave}
              disabled={!isValid}
              className={cn(
                'px-4 py-2 text-sm rounded transition-colors flex items-center gap-2',
                isValid
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-600 text-gray-400 cursor-not-allowed'
              )}
            >
              <Save className="w-4 h-4" />
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
