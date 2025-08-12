/**
 * 📜 Commit History Component - Phase 35
 *
 * Displays Git commit history for PLC projects with diff viewing.
 *
 * ✅ Follows: AI Task Orchestrator TypeScript methodology
 * ✅ Enforces: Strict TypeScript compliance
 * ✅ Features: Commit timeline, file changes, semantic diffs
 */

'use client';

import { cn } from '@/lib/utils/cn';
import { GitCommit, FileText, Eye } from 'lucide-react';
import React from 'react';
import type { PLCProject, CommitEntry } from '@/lib/types/plc-git';

interface CommitHistoryProps {
  project: PLCProject;
  branch: string;
  commits: CommitEntry[];
  onViewDiff: (commitId: string) => void;
}

export function CommitHistory({
  project,
  branch,
  commits,
  onViewDiff,
}: CommitHistoryProps) {
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;

    return date.toLocaleDateString();
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-[#3c3c3c]">
        <h4 className="text-sm font-medium text-[#cccccc]">
          Commit History - {branch}
        </h4>
      </div>

      {/* Commit list */}
      <div className="flex-1 overflow-auto">
        {commits.map(commit => (
          <div
            key={commit.id}
            className="p-4 border-b border-[#3c3c3c] hover:bg-[#2d2d30] group"
          >
            <div className="flex items-start gap-3">
              <GitCommit className="w-4 h-4 text-[#cccccc]/70 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-[#cccccc] mb-2">{commit.message}</p>
                <div className="flex items-center gap-4 text-xs text-[#cccccc]/70">
                  <span>{commit.author}</span>
                  <span>{formatTimestamp(commit.timestamp)}</span>
                  <span className="flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    {commit.filesChanged} files
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#cccccc]/50 font-mono">
                  {commit.id.substring(0, 7)}
                </span>
                <button
                  onClick={() => onViewDiff(commit.id)}
                  className="p-1 hover:bg-[#3c3c3c] rounded opacity-0 group-hover:opacity-100 transition-opacity"
                  title="View changes"
                >
                  <Eye className="w-4 h-4 text-[#cccccc]" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
