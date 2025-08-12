/**
 * Interactive File Tree Component - Phase 35 Enhancement
 *
 * Provides an interactive directory structure with:
 * - Expand/collapse folders
 * - Drag & drop file operations
 * - File move/rename/delete
 * - Visual file status indicators
 */

import { PLCProject } from '@/lib/types/plc-git';
import { cn } from '@/lib/utils/cn';
import {
  ChevronDown,
  ChevronRight,
  FileCode2,
  Folder,
  FolderOpen,
  GitBranch,
  MoreVertical,
  Pencil,
  Trash2,
} from 'lucide-react';
import React, { useCallback, useState } from 'react';

interface InteractiveFileTreeProps {
  project: PLCProject;
  selectedBranch: string;
  uploadedFiles: unknown[];
  onFileMove: (fileId: string, newPath: string) => void;
  onFileRename: (fileId: string, newName: string) => void;
  onFileDelete: (fileId: string) => void;
}

interface TreeNodeProps {
  name: string;
  path: string;
  type: 'folder' | 'file';
  children?: TreeNodeProps[];
  file?: unknown;
  onMove?: (fileId: string, targetPath: string) => void;
  onRename?: (fileId: string, newName: string) => void;
  onDelete?: (fileId: string) => void;
  level?: number;
}

const TreeNode: React.FC<TreeNodeProps> = ({
  name,
  path,
  type,
  children,
  file,
  onMove,
  onRename,
  onDelete,
  level = 0,
}) => {
  const [isExpanded, setIsExpanded] = useState(level < 2);
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState(name);
  const [isDragging, setIsDragging] = useState(false);
  const [isOver, setIsOver] = useState(false);

  // Handle drag start for files
  const handleDragStart = (e: React.DragEvent) => {
    if (type === 'file' && file && typeof file === 'object' && 'id' in file) {
      e.dataTransfer.setData('fileId', (file as { id: string }).id);
      e.dataTransfer.setData('sourcePath', path);
      setIsDragging(true);
    }
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  // Handle drop for folders
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (type === 'folder' && onMove) {
      const fileId = e.dataTransfer.getData('fileId');
      if (fileId) {
        onMove(fileId, path);
      }
    }
    setIsOver(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (type === 'folder') {
      setIsOver(true);
    }
  };

  const handleDragLeave = () => {
    setIsOver(false);
  };

  const handleRename = () => {
    if (file && onRename && newName !== name && typeof file === 'object' && 'id' in file) {
      onRename((file as { id: string }).id, newName);
    }
    setIsRenaming(false);
  };

  const nodeContent = (
    <div
      className={cn(
        'flex items-center gap-2 px-2 py-1 rounded cursor-pointer hover:bg-[#2d2d30] group relative',
        isDragging && 'opacity-50',
        isOver && 'bg-[#007acc]/20'
      )}
      style={{ paddingLeft: `${level * 16 + 8}px` }}
      onClick={e => {
        e.stopPropagation();
        if (type === 'folder') {
          setIsExpanded(!isExpanded);
        }
      }}
      draggable={type === 'file'}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onContextMenu={e => {
        e.preventDefault();
        e.stopPropagation();
        setShowContextMenu(true);
      }}
    >
      {type === 'folder' ? (
        <>
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-[#cccccc]/70" />
          ) : (
            <ChevronRight className="w-4 h-4 text-[#cccccc]/70" />
          )}
          {isExpanded ? (
            <FolderOpen className="w-4 h-4 text-[#cccccc]/70" />
          ) : (
            <Folder className="w-4 h-4 text-[#cccccc]/70" />
          )}
        </>
      ) : (
        <>
          <div className="w-4" />
          <FileCode2 className="w-4 h-4 text-[#cccccc]/70" />
        </>
      )}

      {isRenaming ? (
        <input
          className="flex-1 bg-[#3c3c3c] text-[#cccccc] text-sm px-1 rounded outline-none"
          value={newName}
          onChange={e => setNewName(e.target.value)}
          onBlur={handleRename}
          onKeyDown={e => {
            if (e.key === 'Enter') handleRename();
            if (e.key === 'Escape') {
              setNewName(name);
              setIsRenaming(false);
            }
          }}
          autoFocus
          onClick={e => e.stopPropagation()}
        />
      ) : (
        <span className="text-sm text-[#cccccc] flex-1">{name}</span>
      )}

      {file && typeof file === 'object' && file !== null && 'status' in file ? (
        <span
          className={cn(
            'text-xs px-1 rounded',
            (file as { status: string }).status === 'converted' && 'text-green-500',
            (file as { status: string }).status === 'converting' && 'text-yellow-500',
            (file as { status: string }).status === 'error' && 'text-red-500',
            (file as { status: string }).status === 'committed' && 'text-blue-500'
          )}
        >
          {(file as { status: string }).status}
        </span>
      ) : null}

      {/* Context menu trigger */}
      <button
        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-[#3c3c3c] rounded"
        onClick={e => {
          e.stopPropagation();
          setShowContextMenu(!showContextMenu);
        }}
      >
        <MoreVertical className="w-3 h-3 text-[#cccccc]/70" />
      </button>

      {/* Context menu */}
      {showContextMenu && (
        <div className="absolute right-2 mt-6 bg-[#2d2d30] border border-[#3c3c3c] rounded shadow-lg z-50">
          {type === 'file' && (
            <>
              <button
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-[#cccccc] hover:bg-[#3c3c3c] w-full"
                onClick={() => {
                  setIsRenaming(true);
                  setShowContextMenu(false);
                }}
              >
                <Pencil className="w-3 h-3" />
                Rename
              </button>
              <button
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-[#cccccc] hover:bg-[#3c3c3c] w-full"
                onClick={() => {
                  if (file && onDelete && typeof file === 'object' && 'id' in file) {
                    onDelete((file as { id: string }).id);
                  }
                  setShowContextMenu(false);
                }}
              >
                <Trash2 className="w-3 h-3" />
                Delete
              </button>
            </>
          )}
          {type === 'folder' && (
            <button
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-[#cccccc] hover:bg-[#3c3c3c] w-full"
              onClick={() => {
                // TODO: Implement new folder dialog
                setShowContextMenu(false);
              }}
            >
              <Folder className="w-3 h-3" />
              New Folder
            </button>
          )}
        </div>
      )}
    </div>
  );

  return (
    <div className="relative">
      {nodeContent}
      {isExpanded && children && (
        <div>
          {children.map((child, index) => (
            <TreeNode
              key={`${child.path}-${index}`}
              {...child}
              level={level + 1}
              onMove={onMove}
              onRename={onRename}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const InteractiveFileTree: React.FC<InteractiveFileTreeProps> = ({
  project,
  selectedBranch,
  uploadedFiles,
  onFileMove,
  onFileRename,
  onFileDelete,
}) => {
  // Build tree structure from project structure and uploaded files
  const buildTreeStructure = useCallback((): TreeNodeProps => {
    const root: TreeNodeProps = {
      name: project.name,
      path: project.path,
      type: 'folder',
      children: [],
    };

    // Add standard directories
    const directories = [
      {
        name: 'acd-current',
        path: `${project.path}/acd-current`,
        type: 'folder' as const,
        children: [
          {
            name: selectedBranch,
            path: `${project.path}/acd-current/${selectedBranch}`,
            type: 'folder' as const,
            children: (
              uploadedFiles as Array<{
                branch: string;
                type: string;
                path: string;
                name: string;
                id: string;
              }>
            )
              .filter(
                f =>
                  f.branch === selectedBranch && f.type === 'acd' && f.path.includes('acd-current')
              )
              .map(file => ({
                name: file.name,
                path: file.path,
                type: 'file' as const,
                file,
              })),
          },
        ],
      },
      {
        name: 'l5x-current',
        path: `${project.path}/l5x-current`,
        type: 'folder' as const,
        children: [
          {
            name: selectedBranch,
            path: `${project.path}/l5x-current/${selectedBranch}`,
            type: 'folder' as const,
            children: (
              uploadedFiles as Array<{
                branch: string;
                type: string;
                path: string;
                name: string;
                id: string;
              }>
            )
              .filter(
                f =>
                  f.branch === selectedBranch && f.type === 'l5x' && f.path.includes('l5x-current')
              )
              .map(file => ({
                name: file.name,
                path: file.path,
                type: 'file' as const,
                file,
              })),
          },
        ],
      },
      {
        name: 'acd-previous',
        path: `${project.path}/acd-previous`,
        type: 'folder' as const,
        children: [],
      },
      {
        name: 'plc',
        path: `${project.path}/plc`,
        type: 'folder' as const,
        children: [
          { name: 'routines', path: `${project.path}/plc/routines`, type: 'folder' as const },
          { name: 'tags', path: `${project.path}/plc/tags`, type: 'folder' as const },
          { name: 'dataTypes', path: `${project.path}/plc/dataTypes`, type: 'folder' as const },
        ],
      },
    ];

    root.children = directories;
    return root;
  }, [project, selectedBranch, uploadedFiles]);

  const treeStructure = buildTreeStructure();

  return (
    <div className="h-full overflow-auto">
      <div className="p-2">
        <div className="flex items-center gap-2 mb-2 text-sm text-[#cccccc]/70">
          <GitBranch className="w-4 h-4" />
          <span>Branch: {selectedBranch}</span>
        </div>
        <TreeNode
          {...treeStructure}
          onMove={onFileMove}
          onRename={onFileRename}
          onDelete={onFileDelete}
        />
      </div>
      <div className="p-2 border-t border-[#3c3c3c]">
        <p className="text-xs text-[#cccccc]/50">
          Drag files to move between folders. Right-click for more options.
        </p>
      </div>
    </div>
  );
};
