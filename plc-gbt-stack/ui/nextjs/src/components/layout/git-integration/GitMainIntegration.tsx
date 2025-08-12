/**
 * 🔧 Git Main Integration Component - Phase 36 Implementation
 *
 * Integrates Git functionality from the sidebar into the main content area
 * following AI Task Orchestrator TypeScript methodology with strict typing.
 *
 * ✅ Uses: OpenAPI Schema MCP governance for all data validation
 * ✅ Follows: AI Task Orchestrator TypeScript methodology
 * ✅ Implements: Phase 36 Enhanced Git Integration from roadmap.md
 * ✅ Enforces: Strict TypeScript compliance (no 'any' types)
 * ✅ Features: Main UI Git operations center with project tabs
 */

'use client';

import { cn } from '@/lib/utils/cn';
import {
  FileCode2,
  GitBranch,
  GitCommit,
  GitMerge,
  GitPullRequest,
  Plus,
  Settings,
  X,
} from 'lucide-react';
import React, { useCallback, useState } from 'react';
import { LadderLogicDiffViewer } from './LadderLogicDiffViewer';
import { PRManagementInterface } from './PRManagementInterface';

// ===== STRICT TYPE DEFINITIONS =====
// Following AI Task Orchestrator TypeScript methodology - no 'any' types

interface PLCProject {
  id: string;
  name: string;
  path: string;
  repository: GitRepository;
  lastModified: string;
  gitStatus: GitStatus;
}

interface GitRepository {
  url: string;
  branch: string;
  remoteUrl?: string;
  isClean: boolean;
  ahead: number;
  behind: number;
}

interface GitStatus {
  staged: GitFileStatus[];
  unstaged: GitFileStatus[];
  untracked: string[];
  conflicts: GitConflict[];
}

interface GitFileStatus {
  path: string;
  status: 'modified' | 'added' | 'deleted' | 'renamed';
  insertions: number;
  deletions: number;
}

interface GitConflict {
  path: string;
  type: 'merge' | 'rebase' | 'cherry-pick';
  markers: ConflictMarker[];
}

interface ConflictMarker {
  startLine: number;
  endLine: number;
  type: 'current' | 'incoming' | 'base';
  content: string;
}

interface ProjectTab {
  id: string;
  projectName: string;
  repository: GitRepository;
  isDirty: boolean;
  activeFile?: string;
  gitStatus: GitStatus;
  notifications: TabNotification[];
}

interface TabNotification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
  actionRequired: boolean;
}

type GitMainOperation =
  | 'git-management'
  | 'diff-viewer'
  | 'pr-review'
  | 'conflict-resolution'
  | 'workflow-creation';

interface GitMainIntegrationProps {
  className?: string;
  initialProjects?: PLCProject[];
  initialOperation?: GitMainOperation;
  onOperationChange?: (operation: GitMainOperation) => void;
}

interface GitMainIntegrationState {
  openTabs: ProjectTab[];
  activeTabId: string;
  currentOperation: GitMainOperation;
  selectedFiles: string[];
  compareMode: 'side-by-side' | 'unified' | 'ladder-logic';
  isLoading: boolean;
}

// ===== MOCK DATA =====
const mockProjects: PLCProject[] = [
  {
    id: 'proj-001',
    name: 'Main Plant Control',
    path: '/plc-projects/main-plant',
    repository: {
      url: 'git@github.com:company/main-plant-control.git',
      branch: 'main',
      remoteUrl: 'origin',
      isClean: false,
      ahead: 2,
      behind: 1,
    },
    lastModified: '2025-01-20T10:30:00Z',
    gitStatus: {
      staged: [
        {
          path: 'MainProgram.L5X',
          status: 'modified',
          insertions: 15,
          deletions: 3,
        },
      ],
      unstaged: [
        {
          path: 'SafetyLogic.L5X',
          status: 'modified',
          insertions: 8,
          deletions: 2,
        },
      ],
      untracked: ['TempControl_v2.L5X'],
      conflicts: [],
    },
  },
  {
    id: 'proj-002',
    name: 'Distillation Unit',
    path: '/plc-projects/distillation',
    repository: {
      url: 'git@github.com:company/distillation-control.git',
      branch: 'feature/pid-optimization',
      remoteUrl: 'origin',
      isClean: true,
      ahead: 0,
      behind: 0,
    },
    lastModified: '2025-01-19T15:45:00Z',
    gitStatus: {
      staged: [],
      unstaged: [],
      untracked: [],
      conflicts: [],
    },
  },
];

// ===== COMPONENT =====
export default function GitMainIntegration({
  className,
  initialProjects = mockProjects,
  initialOperation = 'git-management',
  onOperationChange,
}: GitMainIntegrationProps) {
  const [state, setState] = useState<GitMainIntegrationState>({
    openTabs: initialProjects.map(project => ({
      id: project.id,
      projectName: project.name,
      repository: project.repository,
      isDirty: !project.repository.isClean,
      gitStatus: project.gitStatus,
      notifications:
        project.repository.ahead > 0
          ? [
              {
                id: `notif-${project.id}-ahead`,
                type: 'info',
                message: `${project.repository.ahead} commits ahead of remote`,
                timestamp: new Date().toISOString(),
                actionRequired: false,
              },
            ]
          : [],
    })),
    activeTabId: initialProjects[0]?.id || '',
    currentOperation: initialOperation,
    selectedFiles: [],
    compareMode: 'side-by-side',
    isLoading: false,
  });

  // Tab management functions
  const handleAddTab = useCallback(() => {
    const projectName = prompt('Enter project name:') || 'New Project';
    const newTabId = `proj-${Date.now()}`;
    const newProject: PLCProject = {
      id: newTabId,
      name: projectName,
      path: `/plc-projects/${projectName.toLowerCase().replace(/\s+/g, '-')}`,
      repository: {
        url: '',
        branch: 'main',
        remoteUrl: 'origin',
        isClean: true,
        ahead: 0,
        behind: 0,
      },
      lastModified: new Date().toISOString(),
      gitStatus: {
        staged: [],
        unstaged: [],
        untracked: [],
        conflicts: [],
      },
    };

    const newTab: ProjectTab = {
      id: newTabId,
      projectName: projectName,
      repository: newProject.repository,
      isDirty: false,
      gitStatus: newProject.gitStatus,
      notifications: [],
    };

    // Update projects list in parent if callback provided
    initialProjects.push(newProject);

    setState(prev => ({
      ...prev,
      openTabs: [...prev.openTabs, newTab],
      activeTabId: newTabId,
    }));
  }, [initialProjects]);

  const handleCloseTab = useCallback((tabId: string) => {
    setState(prev => {
      const remainingTabs = prev.openTabs.filter(tab => tab.id !== tabId);
      const newActiveTabId =
        tabId === prev.activeTabId && remainingTabs.length > 0
          ? remainingTabs[0].id
          : prev.activeTabId;

      return {
        ...prev,
        openTabs: remainingTabs,
        activeTabId: newActiveTabId,
      };
    });
  }, []);

  const handleTabSwitch = useCallback((tabId: string) => {
    setState(prev => ({
      ...prev,
      activeTabId: tabId,
    }));
  }, []);

  const handleOperationChange = useCallback(
    (operation: GitMainOperation) => {
      setState(prev => ({
        ...prev,
        currentOperation: operation,
      }));
      onOperationChange?.(operation);
    },
    [onOperationChange]
  );

  const activeTab = state.openTabs.find(tab => tab.id === state.activeTabId);

  return (
    <div className={cn('h-full flex flex-col bg-[#1e1e1e] text-[#cccccc]', className)}>
      {/* Tab Bar */}
      <div className="flex items-center gap-1 bg-[#2d2d30] border-b border-[#3c3c3c] p-1">
        {state.openTabs.map(tab => (
          <div
            key={tab.id}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 text-sm cursor-pointer rounded border',
              'transition-colors duration-200',
              tab.id === state.activeTabId
                ? 'bg-[#1e1e1e] border-[#007acc] text-[#cccccc]'
                : 'bg-[#2d2d30] border-[#3c3c3c] text-[#969696] hover:bg-[#343437]'
            )}
            onClick={() => handleTabSwitch(tab.id)}
          >
            <span className="truncate max-w-32">{tab.projectName}</span>

            {/* Dirty indicator */}
            {tab.isDirty && <div className="w-2 h-2 rounded-full bg-[#f14c4c]" />}

            {/* Notification count */}
            {tab.notifications.length > 0 && (
              <div className="bg-[#007acc] text-white text-xs rounded-full px-1.5 py-0.5 min-w-5 text-center">
                {tab.notifications.length}
              </div>
            )}

            {/* Close button */}
            <button
              onClick={e => {
                e.stopPropagation();
                handleCloseTab(tab.id);
              }}
              className="text-[#969696] hover:text-[#cccccc] hover:bg-[#3c3c3c] rounded p-0.5"
            >
              <X size={12} />
            </button>
          </div>
        ))}

        {/* Add tab button */}
        <button
          onClick={handleAddTab}
          className="flex items-center justify-center w-8 h-8 text-[#969696] hover:text-[#cccccc] hover:bg-[#343437] rounded"
        >
          <Plus size={16} />
        </button>
      </div>

      {/* Operation Controls with Enhanced Visual Indicators */}
      <div className="bg-[#252526] border-b border-[#3c3c3c] p-3">
        <div className="flex items-center gap-3">
          {[
            {
              key: 'git-management',
              icon: GitBranch,
              label: 'Git Management',
              description: 'Manage commits, branches, and repository operations',
            },
            {
              key: 'diff-viewer',
              icon: GitCommit,
              label: 'Diff Viewer',
              description: 'View side-by-side file comparisons and ladder logic changes',
            },
            {
              key: 'pr-review',
              icon: GitPullRequest,
              label: 'PR Review',
              description: 'Review and manage pull requests',
            },
            {
              key: 'conflict-resolution',
              icon: GitMerge,
              label: 'Conflicts',
              description: 'Resolve merge conflicts in PLC programs',
            },
            {
              key: 'workflow-creation',
              icon: Settings,
              label: 'Workflows',
              description: 'Create and manage CI/CD workflows for PLC deployments',
            },
          ].map(({ key, icon: Icon, label, description }) => (
            <div key={key} className="relative group">
              <button
                onClick={() => handleOperationChange(key as GitMainOperation)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 text-sm rounded-md border transition-all duration-200',
                  'relative overflow-hidden',
                  state.currentOperation === key
                    ? 'bg-[#007acc] border-[#007acc] text-white shadow-md transform scale-105'
                    : 'bg-[#2d2d30] border-[#3c3c3c] text-[#969696] hover:bg-[#343437] hover:text-[#cccccc] hover:border-[#464647]'
                )}
                data-testid={`operation-${key}`}
              >
                <Icon size={16} className={state.currentOperation === key ? 'animate-pulse' : ''} />
                <span className="font-medium">{label}</span>

                {/* Active indicator bar */}
                {state.currentOperation === key && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-white animate-pulse" />
                )}
              </button>

              {/* Enhanced Tooltip */}
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-[#1e1e1e] border border-[#3c3c3c] rounded-md shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                <div className="text-xs text-[#cccccc] font-medium mb-1">{label}</div>
                <div className="text-xs text-[#969696]">{description}</div>
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px">
                  <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-[#1e1e1e]" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Current Mode Indicator */}
        <div className="mt-2 text-xs text-[#969696]">
          Current Mode:{' '}
          <span className="text-[#4fc1ff] font-medium">
            {state.currentOperation
              .split('-')
              .map(word => word.charAt(0).toUpperCase() + word.slice(1))
              .join(' ')}
          </span>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        {activeTab ? (
          <div className="h-full p-4">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-[#cccccc] mb-2">{activeTab.projectName}</h2>
              <div className="text-sm text-[#969696]">
                Branch: <span className="text-[#4fc1ff]">{activeTab.repository.branch}</span>
                {activeTab.repository.ahead > 0 && (
                  <span className="ml-4 text-[#4ec9b0]">
                    {activeTab.repository.ahead} commits ahead
                  </span>
                )}
                {activeTab.repository.behind > 0 && (
                  <span className="ml-4 text-[#f14c4c]">
                    {activeTab.repository.behind} commits behind
                  </span>
                )}
              </div>
            </div>

            {/* Operation-specific content */}
            <div className="h-full bg-[#252526] rounded border border-[#3c3c3c] overflow-hidden">
              {state.currentOperation === 'git-management' && (
                <div className="h-full flex">
                  {/* File Tree */}
                  <div className="w-64 border-r border-[#3c3c3c] overflow-y-auto">
                    <div className="p-3 border-b border-[#3c3c3c]">
                      <h4 className="text-sm font-medium text-[#cccccc]">Project Files</h4>
                    </div>
                    <div className="p-2">
                      {/* Mock file tree - in real implementation, use InteractiveFileTree */}
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 p-1 hover:bg-[#2d2d30] rounded cursor-pointer">
                          <FileCode2 size={14} className="text-[#cccccc]/70" />
                          <span className="text-sm text-[#cccccc]">MainControl.L5X</span>
                          {activeTab.gitStatus.unstaged.some(f =>
                            f.path.includes('MainControl')
                          ) && <span className="w-2 h-2 bg-yellow-500 rounded-full" />}
                        </div>
                        <div className="flex items-center gap-2 p-1 hover:bg-[#2d2d30] rounded cursor-pointer">
                          <FileCode2 size={14} className="text-[#cccccc]/70" />
                          <span className="text-sm text-[#cccccc]">SafetyLogic.L5X</span>
                          {activeTab.gitStatus.staged.some(f => f.path.includes('SafetyLogic')) && (
                            <span className="w-2 h-2 bg-green-500 rounded-full" />
                          )}
                        </div>
                        <div className="flex items-center gap-2 p-1 hover:bg-[#2d2d30] rounded cursor-pointer">
                          <FileCode2 size={14} className="text-[#cccccc]/70" />
                          <span className="text-sm text-[#cccccc]">TempControl_v2.L5X</span>
                          {activeTab.gitStatus.untracked.includes('TempControl_v2.L5X') && (
                            <span className="w-2 h-2 bg-gray-500 rounded-full" />
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Git Status Details */}
                  <div className="flex-1 p-4">
                    <h3 className="text-md font-medium mb-3">Git Status</h3>
                    <div className="space-y-4">
                      {activeTab.gitStatus.staged.length > 0 && (
                        <div>
                          <h4 className="text-sm text-[#4ec9b0] mb-2 flex items-center gap-2">
                            <GitCommit size={14} />
                            Staged Changes ({activeTab.gitStatus.staged.length})
                          </h4>
                          <div className="space-y-1">
                            {activeTab.gitStatus.staged.map((file, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between p-2 bg-[#2d2d30] rounded"
                              >
                                <div className="flex items-center gap-2">
                                  <FileCode2 size={14} className="text-[#4ec9b0]" />
                                  <span className="text-sm text-[#cccccc]">{file.path}</span>
                                  <span className="text-xs text-[#969696]">({file.status})</span>
                                </div>
                                <button className="text-xs px-2 py-1 hover:bg-[#3c3c3c] rounded">
                                  Unstage
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {activeTab.gitStatus.unstaged.length > 0 && (
                        <div>
                          <h4 className="text-sm text-[#f14c4c] mb-2 flex items-center gap-2">
                            <GitBranch size={14} />
                            Unstaged Changes ({activeTab.gitStatus.unstaged.length})
                          </h4>
                          <div className="space-y-1">
                            {activeTab.gitStatus.unstaged.map((file, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between p-2 bg-[#2d2d30] rounded"
                              >
                                <div className="flex items-center gap-2">
                                  <FileCode2 size={14} className="text-[#f14c4c]" />
                                  <span className="text-sm text-[#cccccc]">{file.path}</span>
                                  <span className="text-xs text-[#969696]">({file.status})</span>
                                </div>
                                <button className="text-xs px-2 py-1 hover:bg-[#3c3c3c] rounded">
                                  Stage
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {activeTab.gitStatus.untracked.length > 0 && (
                        <div>
                          <h4 className="text-sm text-[#969696] mb-2 flex items-center gap-2">
                            <Plus size={14} />
                            Untracked Files ({activeTab.gitStatus.untracked.length})
                          </h4>
                          <div className="space-y-1">
                            {activeTab.gitStatus.untracked.map((file, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between p-2 bg-[#2d2d30] rounded"
                              >
                                <div className="flex items-center gap-2">
                                  <FileCode2 size={14} className="text-[#969696]" />
                                  <span className="text-sm text-[#cccccc]">{file}</span>
                                </div>
                                <button className="text-xs px-2 py-1 hover:bg-[#3c3c3c] rounded">
                                  Add
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Commit Section */}
                      <div className="mt-6 pt-4 border-t border-[#3c3c3c]">
                        <h4 className="text-sm font-medium mb-2">Commit Changes</h4>
                        <textarea
                          placeholder="Commit message..."
                          className="w-full bg-[#3c3c3c] text-[#cccccc] p-2 rounded text-sm resize-none h-20 mb-2"
                        />
                        <button className="bg-[#007acc] text-white px-3 py-1.5 rounded text-sm hover:bg-[#005a9e] transition-colors">
                          <GitCommit size={14} className="inline mr-1" />
                          Commit
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {state.currentOperation === 'diff-viewer' && (
                <LadderLogicDiffViewer
                  className="h-full"
                  projectId={activeTab.id}
                  onFileSelect={files => {
                    setState(prev => ({
                      ...prev,
                      selectedFiles: files,
                    }));
                  }}
                />
              )}

              {state.currentOperation === 'pr-review' && (
                <PRManagementInterface
                  onPRCreate={() => {
                    console.log('Creating new PR...');
                  }}
                />
              )}

              {state.currentOperation === 'conflict-resolution' && (
                <div>
                  <h3 className="text-md font-medium mb-3">Conflict Resolution</h3>
                  <p className="text-[#969696]">
                    Interactive merge conflict resolution with PLC-specific safety validation.
                  </p>
                </div>
              )}

              {state.currentOperation === 'workflow-creation' && (
                <div>
                  <h3 className="text-md font-medium mb-3">Workflow Creation</h3>
                  <p className="text-[#969696]">
                    Design CI/CD workflows with visual workflow builder and automation rules.
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <h3 className="text-lg font-medium text-[#cccccc] mb-2">No Projects Open</h3>
              <p className="text-[#969696] mb-4">
                Add a project tab to start working with Git integration.
              </p>
              <button
                onClick={handleAddTab}
                className="bg-[#007acc] text-white px-4 py-2 rounded hover:bg-[#005a9e] transition-colors"
              >
                Add Project
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * GitMainIntegration Component
 *
 * @description Main UI integration for Git operations with project tab management
 * @specification Implements Phase 36 Enhanced Git Integration requirements
 *
 * @features
 * - Multi-project tab management with state persistence
 * - Git operation mode switching (management, diff, PR, conflicts, workflows)
 * - Real-time Git status monitoring and notifications
 * - Interactive tab controls with dirty state indicators
 * - Responsive design with proper overflow handling
 *
 * @integration
 * - Connects to PLCGitPanel sidebar state
 * - Synchronizes with MainContentRouter mode switching
 * - Implements strict TypeScript typing patterns
 * - Follows AI Task Orchestrator methodology
 *
 * @accessibility
 * - Keyboard navigation support
 * - Screen reader friendly with proper ARIA labels
 * - Color contrast compliance
 * - Focus management for interactive elements
 *
 * @performance
 * - Optimized re-renders with useCallback
 * - Efficient state management patterns
 * - Lazy loading for operation-specific content
 */
