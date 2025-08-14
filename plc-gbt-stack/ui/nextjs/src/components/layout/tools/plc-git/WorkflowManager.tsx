/**
 * 🔄 Workflow Manager Component - Phase 35
 *
 * Manages CI/CD workflows for PLC Git integration.
 *
 * ✅ Follows: AI Task Orchestrator TypeScript methodology
 * ✅ Enforces: Strict TypeScript compliance
 * ✅ Features: Pipeline visualization, workflow execution, status tracking
 */

'use client';

import type { PLCProject } from '@/lib/types/plc-git';
import { cn } from '@/lib/utils/cn';
import { CheckCircle, Clock, GitPullRequest, PlayCircle, XCircle } from 'lucide-react';
import React from 'react';

interface WorkflowManagerProps {
  project: PLCProject;
  onRunWorkflow: (workflow: string) => void;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'idle' | 'running' | 'success' | 'failed';
  lastRun?: string;
  duration?: string;
}

const mockWorkflows: Workflow[] = [
  {
    id: 'validate-plc',
    name: 'Validate PLC Program',
    description: 'Validate ACD/L5X files for syntax and safety compliance',
    status: 'success',
    lastRun: '2024-01-15T10:30:00Z',
    duration: '2m 15s',
  },
  {
    id: 'convert-acd',
    name: 'Convert ACD to L5X',
    description: 'Batch convert all ACD files to L5X format',
    status: 'idle',
  },
  {
    id: 'semantic-diff',
    name: 'Generate Semantic Diff',
    description: 'Compare PLC programs and generate semantic differences',
    status: 'idle',
  },
  {
    id: 'deploy-testing',
    name: 'Deploy to Testing',
    description: 'Deploy PLC program to testing environment',
    status: 'failed',
    lastRun: '2024-01-14T15:45:00Z',
    duration: '1m 30s',
  },
];

export function WorkflowManager({ project: _project, onRunWorkflow }: WorkflowManagerProps) {
  const getStatusIcon = (status: Workflow['status']) => {
    switch (status) {
      case 'running':
        return <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <GitPullRequest className="w-4 h-4 text-[#cccccc]/50" />;
    }
  };

  const formatTimestamp = (timestamp?: string): string => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-[#3c3c3c]">
        <h4 className="text-sm font-medium text-[#cccccc]">CI/CD Workflows</h4>
      </div>

      {/* Workflow list */}
      <div className="flex-1 overflow-auto p-4 space-y-3">
        {mockWorkflows.map(workflow => (
          <div
            key={workflow.id}
            className={cn(
              'p-4 rounded-lg border transition-colors',
              workflow.status === 'running'
                ? 'border-yellow-500/50 bg-yellow-500/10'
                : 'border-[#3c3c3c] bg-[#2d2d30] hover:bg-[#3c3c3c]'
            )}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                {getStatusIcon(workflow.status)}
                <div>
                  <h5 className="text-sm font-medium text-[#cccccc]">{workflow.name}</h5>
                  <p className="text-xs text-[#cccccc]/70 mt-1">{workflow.description}</p>
                  {workflow.lastRun && (
                    <div className="flex items-center gap-3 mt-2 text-xs text-[#cccccc]/50">
                      <span>Last run: {formatTimestamp(workflow.lastRun)}</span>
                      {workflow.duration && <span>Duration: {workflow.duration}</span>}
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={() => onRunWorkflow(workflow.id)}
                disabled={workflow.status === 'running'}
                className={cn(
                  'p-2 rounded transition-colors',
                  workflow.status === 'running'
                    ? 'bg-[#3c3c3c] text-[#cccccc]/30 cursor-not-allowed'
                    : 'hover:bg-[#3c3c3c] text-[#cccccc]'
                )}
                title={workflow.status === 'running' ? 'Workflow running' : 'Run workflow'}
              >
                <PlayCircle className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Workflow configuration hint */}
      <div className="p-3 border-t border-[#3c3c3c] bg-[#1e1e1e]/50">
        <p className="text-xs text-[#cccccc]/50">
          Workflows are defined in: <span className="font-mono">.github/workflows/</span>
        </p>
      </div>
    </div>
  );
}
