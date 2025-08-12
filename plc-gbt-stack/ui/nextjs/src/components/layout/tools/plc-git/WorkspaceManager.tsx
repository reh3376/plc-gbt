/**
 * 🏢 Workspace Manager Component - Phase 35
 *
 * Modal component for creating and managing PLC workspaces with customizable names.
 *
 * ✅ Follows: AI Task Orchestrator TypeScript methodology
 * ✅ Enforces: Strict TypeScript compliance
 * ✅ Features: Create, update, and configure workspace settings
 */

'use client';

import { cn } from '@/lib/utils/cn';
import { X } from 'lucide-react';
import React, { useState } from 'react';
import type { PLCWorkspace, CreateWorkspaceInput } from '@/lib/types/plc-git';

interface WorkspaceManagerProps {
  workspace?: PLCWorkspace | null;
  onClose: () => void;
  onCreate: (input: CreateWorkspaceInput) => Promise<void>;
  onUpdate?: (workspace: PLCWorkspace) => void;
}

export function WorkspaceManager({
  workspace,
  onClose,
  onCreate,
  onUpdate,
}: WorkspaceManagerProps) {
  const [formData, setFormData] = useState<CreateWorkspaceInput>({
    name: workspace?.name || '',
    description: workspace?.description || '',
    path: workspace?.path || '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (workspace) {
        // Update existing workspace
        onUpdate?.({
          ...workspace,
          name: formData.name,
          description: formData.description,
          lastModified: new Date().toISOString(),
        });
      } else {
        // Create new workspace
        await onCreate(formData);
      }
      onClose();
    } catch (error) {
      console.error('Error saving workspace:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#2d2d30] rounded-lg w-[480px] max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#3c3c3c]">
          <h3 className="text-lg font-semibold text-[#cccccc]">
            {workspace ? 'Workspace Settings' : 'Create New Workspace'}
          </h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-[#3c3c3c] rounded"
            aria-label="Close"
          >
            <X className="w-4 h-4 text-[#cccccc]" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-auto">
          <div className="p-6 space-y-6">
            {/* Workspace Name */}
            <div>
              <label className="block text-sm font-medium text-[#cccccc] mb-2">
                Workspace Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
                required
                className="w-full bg-[#1e1e1e] text-[#cccccc] px-3 py-2 rounded border border-[#3c3c3c] focus:border-[#007acc] focus:outline-none"
                placeholder="e.g., Main Plant Control"
              />
              <p className="text-xs text-[#cccccc]/70 mt-1">
                This will be the root folder name for all PLC projects
              </p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-[#cccccc] mb-2">
                Description
              </label>
              <textarea
                value={formData.description || ''}
                onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full bg-[#1e1e1e] text-[#cccccc] px-3 py-2 rounded border border-[#3c3c3c] focus:border-[#007acc] focus:outline-none h-24 resize-none"
                placeholder="Brief description of the workspace purpose"
              />
            </div>

            {/* Path (only for new workspaces) */}
            {!workspace && (
              <div>
                <label className="block text-sm font-medium text-[#cccccc] mb-2">
                  Workspace Path
                </label>
                <input
                  type="text"
                  value={formData.path || ''}
                  onChange={e => setFormData(prev => ({ ...prev, path: e.target.value }))}
                  className="w-full bg-[#1e1e1e] text-[#cccccc] px-3 py-2 rounded border border-[#3c3c3c] focus:border-[#007acc] focus:outline-none"
                  placeholder="Leave empty for default location"
                />
                <p className="text-xs text-[#cccccc]/70 mt-1">
                  Optional: Specify a custom path for the workspace
                </p>
              </div>
            )}

            {/* Workspace Info */}
            {workspace && (
              <div className="bg-[#1e1e1e] rounded p-4 space-y-2">
                <h4 className="text-sm font-medium text-[#cccccc]">Workspace Information</h4>
                <div className="space-y-1 text-xs text-[#cccccc]/70">
                  <div>ID: {workspace.id}</div>
                  <div>Created: {new Date(workspace.createdAt).toLocaleDateString()}</div>
                  <div>Projects: {workspace.projects.length}</div>
                  <div>Path: {workspace.path}</div>
                </div>
              </div>
            )}

            {/* Directory Structure Info */}
            <div className="bg-[#1e1e1e]/50 rounded p-4">
              <h4 className="text-sm font-medium text-[#cccccc] mb-2">
                Governed Directory Structure
              </h4>
              <div className="text-xs text-[#cccccc]/70 space-y-1">
                <div>• acd-current/ - Current ACD files by branch</div>
                <div>• acd-previous/ - Previous ACD file versions</div>
                <div>• l5x-current/ - Current L5X files by branch</div>
                <div>• l5x-previous/ - Previous L5X file versions</div>
                <div>• plc/ - PLC components (routines, tags, etc.)</div>
                <div>• docs/ - Documentation</div>
                <div>• .github/workflows/ - CI/CD pipelines</div>
                <div>• tests/ - Test scripts and data</div>
                <div>• reports/ - Analysis and diff reports</div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex gap-2 p-4 border-t border-[#3c3c3c]">
            <button
              type="submit"
              disabled={isSubmitting || !formData.name}
              className={cn(
                'flex-1 px-4 py-2 rounded font-medium transition-colors',
                isSubmitting || !formData.name
                  ? 'bg-[#3c3c3c] text-[#cccccc]/50 cursor-not-allowed'
                  : 'bg-[#007acc] text-white hover:bg-[#005a9e]'
              )}
            >
              {isSubmitting ? 'Saving...' : workspace ? 'Save Changes' : 'Create Workspace'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-[#3c3c3c] text-[#cccccc] px-4 py-2 rounded hover:bg-[#4c4c4c] font-medium"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
