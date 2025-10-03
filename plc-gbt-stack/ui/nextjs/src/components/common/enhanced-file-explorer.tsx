'use client';

import { fileApiService, FileUpdateEvent } from '@/lib/services/file-api-service';
import { FileNode } from '@/lib/stores/file-store';
import { cn } from '@/lib/utils/cn';
import {
  ChevronDown,
  ChevronRight,
  Clock,
  Copy,
  Cpu,
  Edit3,
  FileText,
  Folder,
  FolderOpen,
  HardDrive,
  Plus,
  RefreshCw,
  Scissors,
  Search,
  Settings,
  Trash2,
  Upload,
  Workflow,
} from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { ContextMenu, ContextMenuItem } from './context-menu';

// File type icons mapping
const getFileIcon = (fileType?: string, fileName?: string) => {
  if (!fileType && fileName) {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'acd':
        return HardDrive;
      case 'l5x':
        return Cpu;
      case 'json':
        return FileText;
      case 'workflow':
        return Workflow;
      default:
        return FileText;
    }
  }

  switch (fileType) {
    case 'acd':
      return HardDrive;
    case 'l5x':
      return Cpu;
    case 'json':
      return FileText;
    case 'ladder':
      return Settings;
    default:
      return FileText;
  }
};

// Get color for file type
const getFileColor = (fileType?: string, fileName?: string): string => {
  if (!fileType && fileName) {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'acd':
        return 'text-[#4fc3f7]';
      case 'l5x':
        return 'text-[#66bb6a]';
      case 'json':
        return 'text-[#ffb74d]';
      case 'workflow':
        return 'text-[#ba68c8]';
      default:
        return 'text-[#90a4ae]';
    }
  }

  switch (fileType) {
    case 'acd':
      return 'text-[#4fc3f7]';
    case 'l5x':
      return 'text-[#66bb6a]';
    case 'json':
      return 'text-[#ffb74d]';
    case 'ladder':
      return 'text-[#ff7043]';
    default:
      return 'text-[#90a4ae]';
  }
};

// Format file size
const formatFileSize = (bytes?: number): string => {
  if (!bytes) return '';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`;
};

// Format last modified date
const formatLastModified = (date?: Date | string): string => {
  if (!date) return '';

  // Handle both Date objects and date strings (for hydration compatibility)
  const dateObj = date instanceof Date ? date : new Date(date);

  // Check if the date is valid
  if (isNaN(dateObj.getTime())) return '';

  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return dateObj.toLocaleDateString();
};

interface FileItemProps {
  file: FileNode;
  depth: number;
  onSelect: (fileId: string) => void;
  isSelected: boolean;
  selectedFileId?: string | null;
  onToggleFolder: (folderId: string) => void;
  onDeleteFile: (fileId: string) => void;
  onRenameFile: (fileId: string, newName: string) => void;
  onCopyFile: (fileId: string) => void;
  onCutFile: (fileId: string) => void;
  onPasteFile: (parentId: string | null) => void;
  onCreateFile: (name: string, parentPath: string) => void;
  onCreateFolder: (name: string, parentPath: string) => void;
  clipboardFile: { id: string; operation: 'copy' | 'cut' } | null;
}

function FileItem({
  file,
  depth,
  onSelect,
  isSelected,
  selectedFileId,
  onToggleFolder,
  onDeleteFile,
  onRenameFile,
  onCopyFile,
  onCutFile,
  onPasteFile,
  onCreateFile,
  onCreateFolder,
  clipboardFile,
}: FileItemProps) {
  const isExpanded = file.isExpanded;
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState(file.name);
  const [isMounted, setIsMounted] = useState(false);

  // Prevent hydration mismatch by ensuring consistent rendering
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const isFolder = file.type === 'folder';
  const Icon = isFolder
    ? isExpanded
      ? FolderOpen
      : Folder
    : getFileIcon(file.fileType, file.name);

  const handleClick = () => {
    if (isFolder) {
      onToggleFolder(file.id);
    } else {
      onSelect(file.id);
    }
  };

  const handleRename = () => {
    if (newName.trim() && newName !== file.name) {
      onRenameFile(file.id, newName.trim());
    }
    setIsRenaming(false);
    setNewName(file.name);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setIsRenaming(false);
      setNewName(file.name);
    }
  };

  // Context menu items
  // Debug: Log the file's immutable status
  console.log(
    '[ContextMenu] Creating menu for:',
    file.name,
    'isImmutable:',
    file.isImmutable,
    'isSystem:',
    file.isSystem
  );

  const contextMenuItems: ContextMenuItem[] = [
    {
      id: 'open',
      label: 'Open',
      icon: <FileText className="w-4 h-4" />,
      onClick: () => onSelect(file.id),
      disabled: isFolder,
    },
    { id: 'separator1', separator: true },
    {
      id: 'newFile',
      label: 'New File',
      icon: <Plus className="w-4 h-4" />,
      shortcut: 'Ctrl+N',
      onClick: () => {
        const parentId = isFolder ? file.id : file.parentId;
        if (parentId) {
          onCreateFile('Untitled.json', parentId);
        }
      },
      disabled: !isFolder && !file.parentId,
    },
    {
      id: 'newFolder',
      label: 'New Folder',
      icon: <Folder className="w-4 h-4" />,
      onClick: () => {
        const parentId = isFolder ? file.id : file.parentId;
        if (parentId) {
          onCreateFolder('New Folder', parentId);
        }
      },
      disabled: !isFolder && !file.parentId,
    },
    { id: 'separator2', separator: true },
    {
      id: 'copy',
      label: 'Copy',
      icon: <Copy className="w-4 h-4" />,
      shortcut: 'Ctrl+C',
      onClick: () => onCopyFile(file.id),
      disabled: file.isImmutable, // Disable copy for immutable items
    },
    {
      id: 'cut',
      label: 'Cut',
      icon: <Scissors className="w-4 h-4" />,
      shortcut: 'Ctrl+X',
      onClick: () => onCutFile(file.id),
      disabled: isFolder || file.isImmutable, // Disable cut for folders and immutable items
    },
    {
      id: 'paste',
      label: 'Paste',
      icon: <Copy className="w-4 h-4" />,
      shortcut: 'Ctrl+V',
      onClick: () => onPasteFile(isFolder ? file.id : file.parentId ?? null),
      disabled: !clipboardFile || (!isFolder && !file.parentId),
    },
    { id: 'separator3', separator: true },
    {
      id: 'rename',
      label: 'Rename',
      icon: <Edit3 className="w-4 h-4" />,
      shortcut: 'F2',
      onClick: () => setIsRenaming(true),
      disabled: file.isImmutable, // Disable rename for immutable items
    },
    {
      id: 'delete',
      label: 'Delete',
      icon: <Trash2 className="w-4 h-4" />,
      shortcut: 'Del',
      onClick: () => onDeleteFile(file.id),
      danger: true,
      disabled: file.isImmutable, // Disable delete for immutable items
    },
  ];

  return (
    <div>
      <ContextMenu items={contextMenuItems}>
        <div
          className={cn(
            'flex items-center py-1 px-2 hover:bg-[#2a2d2e] cursor-pointer text-sm select-none group',
            isSelected && 'bg-[#3c3c3c]',
            file.hasUnsavedChanges && 'bg-[#1a472a]'
          )}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={handleClick}
        >
          {/* Folder toggle indicator */}
          {isFolder && (
            <div className="w-4 h-4 flex items-center justify-center mr-1">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3 text-[#cccccc]" />
              ) : (
                <ChevronRight className="w-3 h-3 text-[#cccccc]" />
              )}
            </div>
          )}

          {/* File/Folder icon */}
          <div className="mr-2 flex-shrink-0">
            <Icon
              className={cn(
                'w-4 h-4',
                isFolder ? 'text-[#cccccc]' : getFileColor(file.fileType, file.name)
              )}
            />
          </div>

          {/* File name (editable when renaming) */}
          {isRenaming ? (
            <input
              type="text"
              value={newName}
              onChange={e => setNewName(e.target.value)}
              onBlur={handleRename}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-[#3c3c3c] text-[#cccccc] px-1 rounded border border-[#007acc] focus:outline-none"
              autoFocus
            />
          ) : (
            <span
              className={cn(
                'flex-1 truncate text-[#cccccc]',
                file.hasUnsavedChanges && 'text-[#4fc3f7]'
              )}
            >
              {file.name}
              {file.hasUnsavedChanges && <span className="ml-1">•</span>}
            </span>
          )}

          {/* File metadata (shown on hover for files) */}
          {!isFolder && !isRenaming && (
            <div className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 text-xs text-[#969696] flex items-center space-x-2">
              {file.size && <span>{formatFileSize(file.size)}</span>}
              {file.lastModified && <span>{formatLastModified(file.lastModified)}</span>}
            </div>
          )}

          {/* Loading indicator */}
          {file.isLoading && (
            <div className="ml-2 animate-spin">
              <Clock className="w-3 h-3 text-[#007acc]" />
            </div>
          )}
        </div>
      </ContextMenu>

      {/* Render children for expanded folders */}
      {isFolder && isExpanded && file.children && isMounted && (
        <div>
          {file.children.map(child => (
            <FileItem
              key={child.id}
              file={child}
              depth={depth + 1}
              onSelect={onSelect}
              isSelected={child.id === selectedFileId}
              selectedFileId={selectedFileId}
              onToggleFolder={onToggleFolder}
              onDeleteFile={onDeleteFile}
              onRenameFile={onRenameFile}
              onCopyFile={onCopyFile}
              onCutFile={onCutFile}
              onPasteFile={onPasteFile}
              onCreateFile={onCreateFile}
              onCreateFolder={onCreateFolder}
              clipboardFile={clipboardFile}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function EnhancedFileExplorer() {
  const [files, setFiles] = useState<FileNode[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [clipboardFile, setClipboardFile] = useState<{
    id: string;
    operation: 'copy' | 'cut';
  } | null>(null);

  const [, setShowCreateMenu] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const getFilteredFiles = useCallback((): FileNode[] => {
    if (!searchQuery) return files;
    const query = searchQuery.toLowerCase();

    const filterNode = (node: FileNode): FileNode | null => {
      const matches =
        node.name.toLowerCase().includes(query) ||
        node.path.toLowerCase().includes(query) ||
        node.fileType?.toLowerCase().includes(query);

      let filteredChildren: FileNode[] = [];
      if (node.children) {
        filteredChildren = node.children
          .map(child => filterNode(child))
          .filter((child): child is FileNode => child !== null);
      }

      if (matches || filteredChildren.length > 0) {
        return {
          ...node,
          children: filteredChildren.length > 0 ? filteredChildren : node.children,
          isExpanded: filteredChildren.length > 0 ? true : node.isExpanded,
        };
      }

      return null;
    };

    return files.map(file => filterNode(file)).filter((file): file is FileNode => file !== null);
  }, [files, searchQuery]);

  const fetchFiles = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const fetchedFiles = await fileApiService.getFileTree();
      setFiles(fetchedFiles);
    } catch (error) {
      console.error('Failed to fetch files:', error);
      setError('Failed to load files. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadFiles = event.target.files;
    if (!uploadFiles) return;

    setIsLoading(true);
    try {
      for (const file of Array.from(uploadFiles)) {
        await fileApiService.uploadFile(file, '/uploads'); // Upload to uploads folder
      }
      await fetchFiles(); // Refresh file tree
    } catch (error) {
      console.error('Failed to upload files:', error);
      setError('Failed to upload files. Please try again.');
    } finally {
      setIsLoading(false);
    }

    event.target.value = ''; // Reset input
  };

  const handleCreateFile = async (name: string, parentPath: string) => {
    setIsLoading(true);
    try {
      // Create a temporary file object for upload
      const blob = new Blob([''], { type: 'application/json' });
      const file = new File([blob], name, { type: 'application/json' });
      await fileApiService.uploadFile(file, parentPath);
      await fetchFiles();
    } catch (error) {
      console.error('Failed to create file:', error);
      setError(`Failed to create ${name}. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateFolder = async (name: string, parentPath: string) => {
    setIsLoading(true);
    try {
      await fileApiService.createFolder(parentPath, name);
      await fetchFiles();
    } catch (error) {
      console.error('Failed to create folder:', error);
      setError(`Failed to create folder ${name}. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleFolder = useCallback(
    (folderId: string) => {
      // Find and toggle the folder in current state without API call (UI only)
      const toggleInTree = (nodes: FileNode[]): FileNode[] => {
        return nodes.map(node => {
          if (node.id === folderId && node.type === 'folder') {
            return { ...node, isExpanded: !node.isExpanded };
          }
          if (node.children) {
            return { ...node, children: toggleInTree(node.children) };
          }
          return node;
        });
      };
      setFiles(toggleInTree(files));
    },
    [files]
  );

  const handleDeleteFile = useCallback(
    async (fileId: string) => {
      setIsLoading(true);
      try {
        await fileApiService.deleteFile(fileId);
        await fetchFiles();
      } catch (error) {
        console.error('Failed to delete file:', error);
        setError('Failed to delete file. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [fetchFiles]
  );

  const handleRenameFile = useCallback(
    async (fileId: string, newName: string) => {
      setIsLoading(true);
      try {
        await fileApiService.renameFile(fileId, newName);
        await fetchFiles();
      } catch (error) {
        console.error('Failed to rename file:', error);
        setError(`Failed to rename to ${newName}. Please try again.`);
      } finally {
        setIsLoading(false);
      }
    },
    [fetchFiles]
  );

  const handleCopyFile = useCallback((fileId: string) => {
    setClipboardFile({ id: fileId, operation: 'copy' });
  }, []);

  const handleCutFile = useCallback((fileId: string) => {
    setClipboardFile({ id: fileId, operation: 'cut' });
  }, []);

  const handlePasteFile = useCallback(
    async (parentId: string | null) => {
      if (!clipboardFile || !parentId) return;

      setIsLoading(true);
      try {
        if (clipboardFile.operation === 'copy') {
          await fileApiService.copyFile(clipboardFile.id, parentId);
        } else {
          await fileApiService.moveFile(clipboardFile.id, parentId);
        }
        setClipboardFile(null);
        await fetchFiles();
      } catch (error) {
        console.error('Failed to paste file:', error);
        setError('Failed to paste file. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [clipboardFile, fetchFiles]
  );

  // Initialize file tree and WebSocket updates
  useEffect(() => {
    fetchFiles();

    // Subscribe to real-time file updates
    const unsubscribe = fileApiService.subscribeToFileUpdates((event: FileUpdateEvent) => {
      console.log('File update received:', event);
      // Refresh the file tree when files change
      fetchFiles();
    });

    return unsubscribe;
  }, [fetchFiles]);

  const displayFiles = getFilteredFiles();

  const createMenuItems: ContextMenuItem[] = [
    {
      id: 'newFile',
      label: 'New PLC File',
      icon: <FileText className="w-4 h-4" />,
      onClick: async () => {
        await handleCreateFile('Untitled.json', '/projects');
        setShowCreateMenu(false);
      },
    },
    {
      id: 'newFolder',
      label: 'New Folder',
      icon: <Folder className="w-4 h-4" />,
      onClick: async () => {
        await handleCreateFolder('New Folder', '/projects');
        setShowCreateMenu(false);
      },
    },
    { id: 'separator', separator: true },
    {
      id: 'upload',
      label: 'Upload Files',
      icon: <Upload className="w-4 h-4" />,
      onClick: () => {
        document.getElementById('file-upload')?.click();
        setShowCreateMenu(false);
      },
    },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header with search and actions */}
      <div className="p-2 border-b border-[#3c3c3c] space-y-2">
        {/* Search input */}
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-[#969696]" />
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-7 pr-3 py-1 text-xs bg-[#3c3c3c] text-[#cccccc] placeholder-[#969696] rounded border border-[#3c3c3c] focus:border-[#007acc] focus:outline-none"
          />
        </div>

        {/* Action buttons */}
        <div className="flex items-center justify-between">
          <span className="text-[#cccccc] text-sm font-medium">Files</span>
          <div className="flex space-x-1">
            <ContextMenu items={createMenuItems}>
              <button
                className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors"
                title="New File/Folder"
              >
                <Plus className="w-4 h-4 text-[#cccccc]" />
              </button>
            </ContextMenu>
            <button
              className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors"
              title="Refresh"
              onClick={fetchFiles}
              disabled={isLoading}
            >
              <RefreshCw className={cn('w-4 h-4 text-[#cccccc]', isLoading && 'animate-spin')} />
            </button>
          </div>
        </div>
      </div>

      {/* File tree */}
      <div className="flex-1 overflow-auto">
        {!isMounted ? (
          <div className="p-4 text-center text-[#969696] text-sm">Loading...</div>
        ) : error ? (
          <div className="p-4 text-center text-[#969696] text-sm">{error}</div>
        ) : displayFiles.length === 0 ? (
          <div className="p-4 text-center text-[#969696] text-sm">
            {searchQuery ? 'No files match your search' : 'No files in workspace'}
          </div>
        ) : (
          displayFiles.map(file => (
            <FileItem
              key={file.id}
              file={file}
              depth={0}
              onSelect={setSelectedFileId}
              isSelected={file.id === selectedFileId}
              selectedFileId={selectedFileId}
              onToggleFolder={handleToggleFolder}
              onDeleteFile={handleDeleteFile}
              onRenameFile={handleRenameFile}
              onCopyFile={handleCopyFile}
              onCutFile={handleCutFile}
              onPasteFile={handlePasteFile}
              onCreateFile={handleCreateFile}
              onCreateFolder={handleCreateFolder}
              clipboardFile={clipboardFile}
            />
          ))
        )}
      </div>

      {/* Status footer */}
      <div className="p-2 border-t border-[#3c3c3c] text-xs text-[#969696]">
        {searchQuery ? (
          <span>{displayFiles.length} results found</span>
        ) : (
          <span>{files.reduce((count, f) => count + (f.children?.length || 0) + 1, 0)} items</span>
        )}
      </div>

      {/* Hidden file upload input */}
      <input
        id="file-upload"
        type="file"
        multiple
        accept=".acd,.l5x,.json,.txt"
        onChange={handleFileUpload}
        className="hidden"
      />
    </div>
  );
}
