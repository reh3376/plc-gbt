/**
 * Workflow Tabs Component - AI Task Orchestrator TypeScript Implementation
 *
 * @description Tab management for multiple workflow canvases
 * @compliance Strict TypeScript - zero `any` types policy
 */

'use client';

import { useWorkflowStore } from '@/lib/stores/workflow-store';
import { cn } from '@/lib/utils/cn';
import { X } from 'lucide-react';
import React from 'react';

export function WorkflowTabs(): React.JSX.Element {
  const { tabs, activeTabId, switchTab, closeTab } = useWorkflowStore();

  if (tabs.length === 0) {
    return <div className="h-8 bg-[#252526] border-b border-[#404040]" />;
  }

  return (
    <div className="flex bg-[#252526] border-b border-[#404040] overflow-x-auto">
      {tabs.map(tab => (
        <div
          key={tab.id}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 border-r border-[#404040] group min-w-0',
            'hover:bg-[#2d2d2d] transition-colors',
            activeTabId === tab.id && 'bg-[#1e1e1e] border-b-2 border-b-blue-500'
          )}
        >
          <button
            onClick={() => switchTab(tab.id)}
            type="button"
            className="flex items-center gap-1 min-w-0 bg-transparent border-0 p-0 cursor-pointer"
          >
            <span className="text-xs text-gray-300 truncate max-w-[150px]">
              {tab.name}
              {tab.isDirty && <span className="text-orange-400 ml-1">●</span>}
            </span>
          </button>
          <button
            onClick={e => {
              e.stopPropagation();
              closeTab(tab.id);
            }}
            type="button"
            className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:bg-[#3c3c3c] rounded"
            aria-label={`Close ${tab.name}`}
          >
            <X className="w-3 h-3 text-gray-400 hover:text-white" />
          </button>
        </div>
      ))}
    </div>
  );
}
