/**
 * 🌿 Branch Manager Component - Phase 35
 *
 * Manages Git branches for PLC projects with creation, merging, and switching.
 *
 * ✅ Follows: AI Task Orchestrator TypeScript methodology
 * ✅ Enforces: Strict TypeScript compliance
 * ✅ Features: Branch visualization, merge management, protection rules
 */

'use client';

import type { GitBranch as GitBranchType, PLCProject } from '@/lib/types/plc-git';
import { GitBranch, GitMerge, Lock, Plus } from 'lucide-react';
import React from 'react';

interface BranchManagerProps {
  project: PLCProject;
  branches: GitBranchType[];
  currentBranch: string;
  onBranchChange: (branch: string) => void;
  onCreateBranch: (name: string, from: string) => void;
  onMergeBranch: (source: string, target: string) => void;
}

export function BranchManager({
  project: _project,
  branches,
  currentBranch,
  onBranchChange,
  onCreateBranch,
  onMergeBranch,
}: BranchManagerProps) {
  return (
    <div className="h-full flex flex-col">
      {/* Branch actions */}
      <div className="p-3 border-b border-[#3c3c3c] flex items-center justify-between">
        <h4 className="text-sm font-medium text-[#cccccc]">Branches</h4>
        <button
          onClick={() => onCreateBranch('new-feature', currentBranch)}
          className="p-1 hover:bg-[#3c3c3c] rounded"
          title="Create new branch"
        >
          <Plus className="w-4 h-4 text-[#cccccc]" />
        </button>
      </div>

      {/* Branch list */}
      <div className="flex-1 overflow-auto">
        {branches.map(branch => (
          <div
            key={branch.name}
            className="p-4 border-b border-[#3c3c3c] hover:bg-[#2d2d30] cursor-pointer group"
            onClick={() => onBranchChange(branch.name)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <GitBranch className="w-4 h-4 text-[#cccccc]/70" />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-[#cccccc]">{branch.name}</span>
                    {branch.isCurrent && (
                      <span className="text-xs px-2 py-0.5 rounded bg-[#007acc] text-white">
                        current
                      </span>
                    )}
                    {branch.protected && (
                      <span title="Protected branch">
                        <Lock className="w-3 h-3 text-yellow-500" />
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[#cccccc]/70 mt-1">
                    {branch.lastCommit.message} • {branch.lastCommit.author}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                {branch.ahead > 0 && (
                  <span className="text-xs text-green-400">↑ {branch.ahead}</span>
                )}
                {branch.behind > 0 && (
                  <span className="text-xs text-red-400">↓ {branch.behind}</span>
                )}
                {!branch.isCurrent && !branch.protected && (
                  <button
                    onClick={e => {
                      e.stopPropagation();
                      onMergeBranch(branch.name, currentBranch);
                    }}
                    className="p-2 hover:bg-[#3c3c3c] rounded opacity-0 group-hover:opacity-100 transition-opacity"
                    title={`Merge ${branch.name} into ${currentBranch}`}
                  >
                    <GitMerge className="w-4 h-4 text-[#cccccc]" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
