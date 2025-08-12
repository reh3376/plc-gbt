/**
 * 🏗️ Project Structure View Component - Phase 35
 *
 * Displays the governed PLC project directory structure with branch-specific folders
 * for ACD/L5X files and supporting directories.
 *
 * ✅ Follows: Governed file structure for Git workflows
 * ✅ Enforces: Strict TypeScript compliance
 * ✅ Features: Tree view of project structure with file counts
 */

'use client';

import { cn } from '@/lib/utils/cn';
import {
  ChevronDown,
  ChevronRight,
  File,
  FileCode2,
  FileText,
  Folder,
  FolderOpen,
  GitBranch,
} from 'lucide-react';
import React, { useState } from 'react';
import type { PLCProject } from '@/lib/types/plc-git';

interface ProjectStructureViewProps {
  project: PLCProject;
  selectedBranch: string;
  viewMode: 'tree' | 'list' | 'grid';
  onFileSelect?: (file: { path: string; type: string }) => void;
}

interface TreeNode {
  name: string;
  path: string;
  type: 'folder' | 'file';
  children?: TreeNode[];
  fileCount?: number;
  icon?: React.ReactNode;
}

export function ProjectStructureView({
  project,
  selectedBranch,
  viewMode,
  onFileSelect,
}: ProjectStructureViewProps) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(
    new Set([
      'root',
      'acd-current',
      'l5x-current',
      'plc',
    ])
  );

  // Build tree structure based on project structure
  const buildTreeStructure = (): TreeNode => {
    const root: TreeNode = {
      name: project.name,
      path: project.path,
      type: 'folder',
      children: [],
    };

    // ACD Current directory
    const acdCurrent: TreeNode = {
      name: 'acd-current',
      path: 'acd-current',
      type: 'folder',
      icon: <FileCode2 className="w-4 h-4" />,
      children: [
        { name: 'main', path: 'acd-current/main', type: 'folder', fileCount: 2 },
        { name: 'prod', path: 'acd-current/prod', type: 'folder', fileCount: 1 },
        { name: 'testing', path: 'acd-current/testing', type: 'folder', fileCount: 3 },
        { name: 'development', path: 'acd-current/development', type: 'folder', fileCount: 0 },
      ],
    };

    // Add feature branches if any
    Object.keys(project.structure.acdCurrent.feature).forEach(branch => {
      acdCurrent.children?.push({
        name: `feature/${branch}`,
        path: `acd-current/feature/${branch}`,
        type: 'folder',
        fileCount: 1,
        icon: <GitBranch className="w-3 h-3" />,
      });
    });

    // ACD Previous directory
    const acdPrevious: TreeNode = {
      name: 'acd-previous',
      path: 'acd-previous',
      type: 'folder',
      icon: <FileCode2 className="w-4 h-4 opacity-60" />,
      children: [
        { name: 'main', path: 'acd-previous/main', type: 'folder', fileCount: 5 },
        { name: 'prod', path: 'acd-previous/prod', type: 'folder', fileCount: 3 },
        { name: 'testing', path: 'acd-previous/testing', type: 'folder', fileCount: 2 },
        { name: 'development', path: 'acd-previous/development', type: 'folder', fileCount: 0 },
      ],
    };

    // L5X Current directory
    const l5xCurrent: TreeNode = {
      name: 'l5x-current',
      path: 'l5x-current',
      type: 'folder',
      icon: <FileText className="w-4 h-4" />,
      children: [
        { name: 'main', path: 'l5x-current/main', type: 'folder', fileCount: 2 },
        { name: 'prod', path: 'l5x-current/prod', type: 'folder', fileCount: 1 },
        { name: 'testing', path: 'l5x-current/testing', type: 'folder', fileCount: 3 },
        { name: 'development', path: 'l5x-current/development', type: 'folder', fileCount: 0 },
      ],
    };

    // L5X Previous directory
    const l5xPrevious: TreeNode = {
      name: 'l5x-previous',
      path: 'l5x-previous',
      type: 'folder',
      icon: <FileText className="w-4 h-4 opacity-60" />,
      children: [
        { name: 'main', path: 'l5x-previous/main', type: 'folder', fileCount: 5 },
        { name: 'prod', path: 'l5x-previous/prod', type: 'folder', fileCount: 3 },
        { name: 'testing', path: 'l5x-previous/testing', type: 'folder', fileCount: 2 },
        { name: 'development', path: 'l5x-previous/development', type: 'folder', fileCount: 0 },
      ],
    };

    // PLC subdirectories
    const plcDir: TreeNode = {
      name: 'plc',
      path: 'plc',
      type: 'folder',
      children: [
        { name: 'routines', path: 'plc/routines', type: 'folder', fileCount: 12 },
        { name: 'tags', path: 'plc/tags', type: 'folder', fileCount: 8 },
        { name: 'data-types', path: 'plc/data-types', type: 'folder', fileCount: 5 },
        { name: 'add-on-instructions', path: 'plc/add-on-instructions', type: 'folder', fileCount: 3 },
        { name: 'io', path: 'plc/io', type: 'folder', fileCount: 4 },
        { name: 'alarms', path: 'plc/alarms', type: 'folder', fileCount: 7 },
        { name: 'trends', path: 'plc/trends', type: 'folder', fileCount: 2 },
        { name: 'recipes', path: 'plc/recipes', type: 'folder', fileCount: 4 },
        { name: 'motion', path: 'plc/motion', type: 'folder', fileCount: 0 },
        { name: 'safety', path: 'plc/safety', type: 'folder', fileCount: 2 },
      ],
    };

    // Other directories
    const docsDir: TreeNode = {
      name: 'docs',
      path: 'docs',
      type: 'folder',
      fileCount: 15,
    };

    const pipelinesDir: TreeNode = {
      name: '.github/workflows',
      path: '.github/workflows',
      type: 'folder',
      fileCount: 3,
    };

    const testsDir: TreeNode = {
      name: 'tests',
      path: 'tests',
      type: 'folder',
      fileCount: 8,
    };

    const reportsDir: TreeNode = {
      name: 'reports',
      path: 'reports',
      type: 'folder',
      fileCount: 4,
    };

    root.children = [
      acdCurrent,
      acdPrevious,
      l5xCurrent,
      l5xPrevious,
      plcDir,
      docsDir,
      pipelinesDir,
      testsDir,
      reportsDir,
    ];

    return root;
  };

  const toggleNode = (path: string) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const renderTreeNode = (node: TreeNode, level: number = 0): React.ReactNode => {
    const isExpanded = expandedNodes.has(node.path);
    const hasChildren = node.children && node.children.length > 0;
    const paddingLeft = level * 16;

    return (
      <div key={node.path}>
        <div
          className={cn(
            'flex items-center py-1 px-2 hover:bg-[#2d2d30] cursor-pointer group',
            node.path.includes(selectedBranch) && 'bg-[#2d2d30]/50'
          )}
          style={{ paddingLeft: `${paddingLeft}px` }}
          onClick={() => {
            if (hasChildren) {
              toggleNode(node.path);
            } else if (node.type === 'file' && onFileSelect) {
              onFileSelect({ path: node.path, type: 'file' });
            }
          }}
        >
          {/* Expand/collapse icon */}
          {hasChildren && (
            <span className="mr-1">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3 text-[#cccccc]/70" />
              ) : (
                <ChevronRight className="w-3 h-3 text-[#cccccc]/70" />
              )}
            </span>
          )}
          {!hasChildren && <span className="w-4 mr-1" />}

          {/* Folder/file icon */}
          <span className="mr-2 text-[#cccccc]/70">
            {node.icon || (
              node.type === 'folder' ? (
                isExpanded ? (
                  <FolderOpen className="w-4 h-4" />
                ) : (
                  <Folder className="w-4 h-4" />
                )
              ) : (
                <File className="w-4 h-4" />
              )
            )}
          </span>

          {/* Node name */}
          <span className="text-sm text-[#cccccc] flex-1">{node.name}</span>

          {/* File count badge */}
          {node.type === 'folder' && node.fileCount !== undefined && (
            <span className="text-xs text-[#cccccc]/50 ml-2">
              {node.fileCount}
            </span>
          )}
        </div>

        {/* Render children */}
        {hasChildren && isExpanded && (
          <div>
            {node.children!.map(child => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  if (viewMode === 'tree') {
    const treeData = buildTreeStructure();
    return (
      <div className="h-full overflow-auto">
        <div className="py-2">
          {treeData.children?.map(child => renderTreeNode(child, 1))}
        </div>
      </div>
    );
  }

  // TODO: Implement list and grid views
  return (
    <div className="p-4 text-sm text-[#cccccc]/70">
      {viewMode} view not yet implemented
    </div>
  );
}
