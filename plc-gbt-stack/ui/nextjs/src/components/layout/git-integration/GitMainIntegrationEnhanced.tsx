/**
 * 🔧 Git Main Integration Enhanced Component - Phase 36.2 Implementation
 *
 * Enhanced Git integration with real Git operations connectivity
 * Following AI Task Orchestrator TypeScript methodology with strict typing.
 *
 * ✅ Uses: Real Git operations through API, React Query for state
 * ✅ Follows: AI Task Orchestrator TypeScript methodology
 * ✅ Implements: Phase 36.2 Enhanced Git Operations
 * ✅ Features: Real-time Git status, branch management, commit operations
 */

'use client';

import { useGitOperations } from '@/hooks/useGitOperations';
import { cn } from '@/lib/utils/cn';
import {
  AlertCircle,
  Check,
  FileCode2,
  GitBranch,
  GitCommit,
  GitFork,
  GitMerge,
  GitPullRequest,
  Loader2,
  Plus,
  RefreshCw,
  Upload,
  X,
} from 'lucide-react';
import React, { useCallback, useState } from 'react';
import { LadderLogicDiffViewer } from './LadderLogicDiffViewer';
import { PRManagementInterface } from './PRManagementInterface';

// Import Git types
import type { GitFileStatus } from '@/lib/git/git-operations';

interface GitMainIntegrationEnhancedProps {
  readonly className?: string;
  readonly initialProjects?: PLCProject[];
  readonly initialOperation?: GitMainOperation;
  readonly onOperationChange?: (operation: GitMainOperation) => void;
}

interface PLCProject {
  id: string;
  name: string;
  path: string;
  lastModified: string;
}

interface ProjectTab {
  id: string;
  projectId: string;
  projectName: string;
  path: string;
  isDirty: boolean;
  notifications: TabNotification[];
}

interface TabNotification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
}

type GitMainOperation =
  | 'git-management'
  | 'branches'
  | 'history'
  | 'pr-review'
  | 'diff-viewer'
  | 'merge-conflicts'
  | 'workflow-creation';

interface GitMainIntegrationState {
  openTabs: ProjectTab[];
  activeTabId: string;
  currentOperation: GitMainOperation;
  selectedFiles: string[];
  expandedFolders: Set<string>;
}

// Mock initial projects for development
const mockProjects: PLCProject[] = [
  {
    id: 'proj-1',
    name: 'Main Control System',
    path: '/projects/main-control',
    lastModified: '2025-01-20T10:30:00Z',
  },
  {
    id: 'proj-2',
    name: 'Backup System',
    path: '/projects/backup',
    lastModified: '2025-01-20T09:15:00Z',
  },
];

export default function GitMainIntegrationEnhanced({
  className,
  initialProjects = mockProjects,
  initialOperation = 'git-management',
  onOperationChange,
}: GitMainIntegrationEnhancedProps) {
  // State management
  const [state, setState] = useState<GitMainIntegrationState>({
    openTabs: initialProjects.map(proj => ({
      id: `tab-${proj.id}`,
      projectId: proj.id,
      projectName: proj.name,
      path: proj.path,
      isDirty: false,
      notifications: [],
    })),
    activeTabId: `tab-${initialProjects[0]?.id || 'default'}`,
    currentOperation: initialOperation,
    selectedFiles: [],
    expandedFolders: new Set(),
  });

  // Branch management state
  const [newBranchName, setNewBranchName] = useState('');
  const [showCreateBranch, setShowCreateBranch] = useState(false);

  // Get active tab
  const activeTab = state.openTabs.find(tab => tab.id === state.activeTabId);

  // Add notification to tab
  const addNotification = useCallback(
    (tabId: string, notification: Omit<TabNotification, 'id' | 'timestamp'>) => {
      setState(prev => ({
        ...prev,
        openTabs: prev.openTabs.map(tab =>
          tab.id === tabId
            ? {
                ...tab,
                notifications: [
                  ...tab.notifications,
                  {
                    ...notification,
                    id: `notif-${Date.now()}`,
                    timestamp: new Date().toISOString(),
                  },
                ].slice(-5), // Keep only last 5 notifications
              }
            : tab
        ),
      }));
    },
    []
  );

  // Git operations hook
  const {
    status,
    branches,
    isLoading,
    stageFiles,
    unstageFiles,
    stageAll,
    unstageAll,
    commit,
    createBranch,
    switchBranch,
    push,
    pull,
    refresh,
    isStaging,
    isCommitting,
    isPushing,
    isPulling,
  } = useGitOperations({
    repoPath: activeTab?.path || '',
    onError: error => {
      console.error('Git operation error:', error);
      // Add error notification
      if (activeTab) {
        addNotification(activeTab.id, {
          type: 'error',
          message: error.message,
        });
      }
    },
    onSuccess: message => {
      // Add success notification
      if (activeTab) {
        addNotification(activeTab.id, {
          type: 'success',
          message,
        });
      }
    },
  });

  // Handle stage/unstage
  const handleStageToggle = useCallback(
    (file: GitFileStatus) => {
      if (file.staged) {
        unstageFiles([file.path]);
      } else {
        stageFiles([file.path]);
      }
    },
    [stageFiles, unstageFiles]
  );

  // Handle commit
  const [commitMessage, setCommitMessage] = useState('');
  const handleCommit = useCallback(() => {
    if (!commitMessage.trim()) {
      addNotification(state.activeTabId, {
        type: 'error',
        message: 'Please enter a commit message',
      });
      return;
    }

    commit({
      message: commitMessage,
      author: {
        name: 'Current User', // Would come from user settings
        email: 'user@example.com',
      },
    });
    setCommitMessage('');
  }, [commit, commitMessage, state.activeTabId, addNotification]);

  // Render Git status for files
  const renderGitStatus = () => {
    if (!status) return null;

    const stagedFiles = status.files?.filter((f: GitFileStatus) => f.staged) || [];
    const unstagedFiles = status.files?.filter((f: GitFileStatus) => !f.staged) || [];

    return (
      <div className="space-y-4">
        {/* Branch info */}
        <div className="flex items-center justify-between p-3 bg-[#1e1e1e] rounded border border-[#3c3c3c]">
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-[#4ec9b0]" />
            <span className="text-sm font-medium">{status.branch || 'main'}</span>
            {status.upstream && (
              <span className="text-xs text-[#969696]">
                ({status.ahead || 0} ahead, {status.behind || 0} behind)
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => pull({})}
              disabled={isPulling}
              className="px-2 py-1 text-xs bg-[#0e639c] text-white rounded hover:bg-[#1177bb] disabled:opacity-50 flex items-center gap-1"
            >
              {isPulling ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <GitPullRequest className="w-3 h-3" />
              )}
              Pull
            </button>
            <button
              onClick={() => push({})}
              disabled={isPushing || (status.behind || 0) > 0}
              className="px-2 py-1 text-xs bg-[#0e639c] text-white rounded hover:bg-[#1177bb] disabled:opacity-50 flex items-center gap-1"
            >
              {isPushing ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Upload className="w-3 h-3" />
              )}
              Push
            </button>
          </div>
        </div>

        {/* Staged files */}
        {stagedFiles.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-[#4ec9b0]">
                Staged Changes ({stagedFiles.length})
              </h4>
              <button
                onClick={unstageAll}
                disabled={isStaging}
                className="text-xs text-[#969696] hover:text-[#cccccc]"
              >
                Unstage All
              </button>
            </div>
            <div className="space-y-1">
              {stagedFiles.map((file: GitFileStatus) => (
                <button
                  key={file.path}
                  className="w-full flex items-center justify-between p-2 bg-[#1e1e1e] rounded hover:bg-[#2d2d30] cursor-pointer text-left"
                  onClick={() => handleStageToggle(file)}
                  type="button"
                >
                  <div className="flex items-center gap-2">
                    <FileCode2 className="w-4 h-4 text-[#4ec9b0]" />
                    <span className="text-sm">{file.path}</span>
                    <span className="text-xs text-[#969696]">({file.status})</span>
                  </div>
                  <Check className="w-4 h-4 text-[#4ec9b0]" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Unstaged files */}
        {unstagedFiles.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-[#f48771]">
                Changes ({unstagedFiles.length})
              </h4>
              <button
                onClick={stageAll}
                disabled={isStaging}
                className="text-xs text-[#969696] hover:text-[#cccccc]"
              >
                Stage All
              </button>
            </div>
            <div className="space-y-1">
              {unstagedFiles.map((file: GitFileStatus) => (
                <button
                  key={file.path}
                  className="w-full flex items-center justify-between p-2 bg-[#1e1e1e] rounded hover:bg-[#2d2d30] cursor-pointer text-left"
                  onClick={() => handleStageToggle(file)}
                  type="button"
                >
                  <div className="flex items-center gap-2">
                    <FileCode2 className="w-4 h-4 text-[#f48771]" />
                    <span className="text-sm">{file.path}</span>
                    <span className="text-xs text-[#969696]">({file.status})</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Commit section */}
        {stagedFiles.length > 0 && (
          <div className="p-3 bg-[#1e1e1e] rounded border border-[#3c3c3c]">
            <textarea
              value={commitMessage}
              onChange={e => setCommitMessage(e.target.value)}
              placeholder="Commit message..."
              className="w-full h-20 p-2 bg-[#3c3c3c] text-[#cccccc] rounded resize-none focus:outline-none focus:ring-1 focus:ring-[#0e639c]"
            />
            <button
              onClick={handleCommit}
              disabled={isCommitting || !commitMessage.trim()}
              className="mt-2 px-4 py-2 bg-[#0e639c] text-white rounded hover:bg-[#1177bb] disabled:opacity-50 flex items-center gap-2"
            >
              {isCommitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Committing...
                </>
              ) : (
                <>
                  <GitCommit className="w-4 h-4" />
                  Commit
                </>
              )}
            </button>
          </div>
        )}

        {/* Conflicts */}
        {status.conflicts && status.conflicts.length > 0 && (
          <div className="p-3 bg-[#5a1e1e] rounded border border-[#f48771]">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-[#f48771]" />
              <h4 className="text-sm font-medium text-[#f48771]">
                Merge Conflicts ({status.conflicts.length})
              </h4>
            </div>
            <div className="space-y-1">
              {status.conflicts.map((conflict: string) => (
                <div key={conflict} className="text-sm text-[#cccccc]">
                  {conflict}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render branch management
  const renderBranchManagement = () => {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-md font-medium">Branches</h3>
          <button
            onClick={() => setShowCreateBranch(!showCreateBranch)}
            className="px-3 py-1 text-sm bg-[#0e639c] text-white rounded hover:bg-[#1177bb] flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Branch
          </button>
        </div>

        {showCreateBranch && (
          <div className="p-3 bg-[#1e1e1e] rounded border border-[#3c3c3c]">
            <input
              type="text"
              value={newBranchName}
              onChange={e => setNewBranchName(e.target.value)}
              placeholder="Branch name..."
              className="w-full p-2 bg-[#3c3c3c] text-[#cccccc] rounded focus:outline-none focus:ring-1 focus:ring-[#0e639c]"
            />
            <div className="flex gap-2 mt-2">
              <button
                onClick={() => {
                  if (newBranchName.trim()) {
                    createBranch({ name: newBranchName });
                    setNewBranchName('');
                    setShowCreateBranch(false);
                  }
                }}
                className="px-3 py-1 text-sm bg-[#0e639c] text-white rounded hover:bg-[#1177bb]"
              >
                Create
              </button>
              <button
                onClick={() => {
                  setNewBranchName('');
                  setShowCreateBranch(false);
                }}
                className="px-3 py-1 text-sm bg-[#3c3c3c] text-[#cccccc] rounded hover:bg-[#464647]"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="space-y-2">
          {branches?.map(branch => (
            <button
              key={branch.name}
              className={cn(
                'w-full flex items-center justify-between p-3 rounded border cursor-pointer text-left',
                branch.current
                  ? 'bg-[#0e639c]/20 border-[#0e639c]'
                  : 'bg-[#1e1e1e] border-[#3c3c3c] hover:bg-[#2d2d30]'
              )}
              onClick={() => !branch.current && switchBranch(branch.name)}
              type="button"
              disabled={branch.current}
            >
              <div className="flex items-center gap-2">
                <GitBranch
                  className={cn('w-4 h-4', branch.current ? 'text-[#0e639c]' : 'text-[#969696]')}
                />
                <span className={cn('text-sm font-medium', branch.current && 'text-[#0e639c]')}>
                  {branch.name}
                </span>
                {branch.current && (
                  <span className="text-xs text-[#0e639c] font-medium">(current)</span>
                )}
              </div>
              {branch.remote && (
                <div className="text-xs text-[#969696]">
                  {branch.ahead > 0 && `↑${branch.ahead}`}
                  {branch.ahead > 0 && branch.behind > 0 && ' '}
                  {branch.behind > 0 && `↓${branch.behind}`}
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={cn('h-full flex flex-col bg-[#252526] text-[#cccccc]', className)}>
      {/* Project Tabs */}
      <div className="bg-[#2d2d30] border-b border-[#3c3c3c]">
        <div className="flex items-center">
          {state.openTabs.map(tab => (
            <div
              key={tab.id}
              className={cn(
                'flex items-center gap-2 px-4 py-2 border-r border-[#3c3c3c] cursor-pointer',
                state.activeTabId === tab.id
                  ? 'bg-[#1e1e1e] text-white'
                  : 'hover:bg-[#383838] text-[#969696]'
              )}
              onClick={() => setState(prev => ({ ...prev, activeTabId: tab.id }))}
              role="tab"
              tabIndex={0}
              onKeyDown={e => {
                if (e.key === 'Enter' || e.key === ' ') {
                  setState(prev => ({ ...prev, activeTabId: tab.id }));
                }
              }}
            >
              <span className="text-sm">{tab.projectName}</span>
              {tab.isDirty && <span className="w-2 h-2 bg-[#f48771] rounded-full" />}
              <button
                onClick={e => {
                  e.stopPropagation();
                  setState(prev => ({
                    ...prev,
                    openTabs: prev.openTabs.filter(t => t.id !== tab.id),
                    activeTabId:
                      prev.activeTabId === tab.id ? prev.openTabs[0]?.id || '' : prev.activeTabId,
                  }));
                }}
                className="ml-2 hover:bg-[#464647] rounded p-0.5"
                type="button"
                aria-label={`Close ${tab.projectName}`}
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
          <button
            onClick={() => {
              const projectName = prompt('Enter project name:') || 'New Project';
              const newProject: PLCProject = {
                id: `proj-${Date.now()}`,
                name: projectName,
                path: `/projects/${projectName.toLowerCase().replace(/\s+/g, '-')}`,
                lastModified: new Date().toISOString(),
              };

              const newTab: ProjectTab = {
                id: `tab-${newProject.id}`,
                projectId: newProject.id,
                projectName: newProject.name,
                path: newProject.path,
                isDirty: false,
                notifications: [],
              };

              setState(prev => ({
                ...prev,
                openTabs: [...prev.openTabs, newTab],
                activeTabId: newTab.id,
              }));

              initialProjects.push(newProject);
            }}
            className="p-2 hover:bg-[#383838]"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full flex">
          {/* Operation Controls */}
          <div className="w-48 bg-[#1e1e1e] border-r border-[#3c3c3c] p-4">
            <h3 className="text-sm font-semibold mb-4">Git Operations</h3>
            <div className="space-y-2">
              {[
                { id: 'git-management', label: 'Files & Changes', icon: FileCode2 },
                { id: 'branches', label: 'Branches', icon: GitBranch },
                { id: 'history', label: 'History', icon: GitCommit },
                { id: 'pr-review', label: 'Pull Requests', icon: GitPullRequest },
                { id: 'diff-viewer', label: 'Diff Viewer', icon: GitMerge },
                { id: 'merge-conflicts', label: 'Conflicts', icon: GitFork },
              ].map(op => {
                const Icon = op.icon;
                return (
                  <button
                    key={op.id}
                    onClick={() => {
                      setState(prev => ({ ...prev, currentOperation: op.id as GitMainOperation }));
                      onOperationChange?.(op.id as GitMainOperation);
                    }}
                    className={cn(
                      'w-full flex items-center gap-2 px-3 py-2 rounded text-sm',
                      state.currentOperation === op.id
                        ? 'bg-[#094771] text-white'
                        : 'hover:bg-[#2d2d30] text-[#cccccc]'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {op.label}
                  </button>
                );
              })}
            </div>

            <div className="mt-6">
              <button
                onClick={refresh}
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-[#3c3c3c] text-[#cccccc] rounded hover:bg-[#464647] disabled:opacity-50"
              >
                <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
                Refresh
              </button>
            </div>
          </div>

          {/* Operation Content */}
          <div className="flex-1 p-6 overflow-auto">
            {isLoading && !status && !branches ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-8 h-8 animate-spin text-[#0e639c]" />
              </div>
            ) : (
              <>
                {state.currentOperation === 'git-management' && renderGitStatus()}
                {state.currentOperation === 'branches' && renderBranchManagement()}
                {state.currentOperation === 'history' && (
                  <div>
                    <h3 className="text-md font-medium mb-3">Commit History</h3>
                    <p className="text-[#969696]">
                      View commit history with visual timeline and change tracking.
                    </p>
                  </div>
                )}
                {state.currentOperation === 'pr-review' && (
                  <PRManagementInterface
                    onPRCreate={() => {
                      console.log('Creating new PR...');
                    }}
                  />
                )}
                {state.currentOperation === 'diff-viewer' && (
                  <LadderLogicDiffViewer
                    className="h-full"
                    projectId={activeTab?.id}
                    onFileSelect={files => {
                      setState(prev => ({
                        ...prev,
                        selectedFiles: files,
                      }));
                    }}
                  />
                )}
                {state.currentOperation === 'merge-conflicts' && (
                  <div>
                    <h3 className="text-md font-medium mb-3">Merge Conflicts</h3>
                    {status?.conflicts && status.conflicts.length > 0 ? (
                      <div className="space-y-4">
                        <p className="text-[#f48771]">
                          {status.conflicts.length} conflict(s) need to be resolved
                        </p>
                        {/* Conflict resolution UI would go here */}
                      </div>
                    ) : (
                      <p className="text-[#969696]">No merge conflicts detected.</p>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Notifications */}
      {activeTab && activeTab.notifications.length > 0 && (
        <div className="absolute bottom-4 right-4 space-y-2 max-w-sm">
          {activeTab.notifications.slice(-3).map(notif => (
            <div
              key={notif.id}
              className={cn(
                'p-3 rounded shadow-lg',
                notif.type === 'error' && 'bg-[#5a1e1e] text-[#f48771]',
                notif.type === 'warning' && 'bg-[#5a4a1e] text-[#d7ba7d]',
                notif.type === 'success' && 'bg-[#1e5a1e] text-[#4ec9b0]',
                notif.type === 'info' && 'bg-[#1e3a5a] text-[#3794ff]'
              )}
            >
              <p className="text-sm">{notif.message}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
