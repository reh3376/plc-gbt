'use client'

import { useState, useEffect } from 'react'
import {
  Folder,
  FolderOpen,
  FileText,
  Plus,
  Copy,
  Scissors,
  Trash2,
  Edit3,
  Search,
  Upload,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  HardDrive,
  Cpu,
  Workflow,
  Settings,
  Clock
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useFileStore, FileNode } from '@/lib/stores/file-store'
import { ContextMenu, ContextMenuItem } from './context-menu'

// File type icons mapping
const getFileIcon = (fileType?: string, fileName?: string) => {
  if (!fileType && fileName) {
    const ext = fileName.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'acd': return HardDrive
      case 'l5x': return Cpu
      case 'json': return FileText
      case 'workflow': return Workflow
      default: return FileText
    }
  }
  
  switch (fileType) {
    case 'acd': return HardDrive
    case 'l5x': return Cpu
    case 'json': return FileText
    case 'ladder': return Settings
    default: return FileText
  }
}

// Get color for file type
const getFileColor = (fileType?: string, fileName?: string): string => {
  if (!fileType && fileName) {
    const ext = fileName.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'acd': return 'text-[#4fc3f7]'
      case 'l5x': return 'text-[#66bb6a]'
      case 'json': return 'text-[#ffb74d]'
      case 'workflow': return 'text-[#ba68c8]'
      default: return 'text-[#90a4ae]'
    }
  }
  
  switch (fileType) {
    case 'acd': return 'text-[#4fc3f7]'
    case 'l5x': return 'text-[#66bb6a]'
    case 'json': return 'text-[#ffb74d]'
    case 'ladder': return 'text-[#ff7043]'
    default: return 'text-[#90a4ae]'
  }
}

// Format file size
const formatFileSize = (bytes?: number): string => {
  if (!bytes) return ''
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// Format last modified date
const formatLastModified = (date?: Date | string): string => {
  if (!date) return ''
  
  // Handle both Date objects and date strings (for hydration compatibility)
  const dateObj = date instanceof Date ? date : new Date(date)
  
  // Check if the date is valid
  if (isNaN(dateObj.getTime())) return ''
  
  const now = new Date()
  const diffMs = now.getTime() - dateObj.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return dateObj.toLocaleDateString()
}

interface FileItemProps {
  file: FileNode
  depth: number
  onSelect: (fileId: string) => void
  isSelected: boolean
  selectedFileId?: string | null
}

function FileItem({ file, depth, onSelect, isSelected, selectedFileId }: FileItemProps) {
  const isExpanded = file.isExpanded
  const [isRenaming, setIsRenaming] = useState(false)
  const [newName, setNewName] = useState(file.name)
  const [isMounted, setIsMounted] = useState(false)
  
  // Prevent hydration mismatch by ensuring consistent rendering
  useEffect(() => {
    setIsMounted(true)
  }, [])
  
  const {
    toggleFolder,
    deleteFile,
    renameFile,
    copyFile,
    cutFile,
    pasteFile,
    clipboardFile,
    addFile,
    addFolder,
  } = useFileStore()

  const isFolder = file.type === 'folder'
  const Icon = isFolder 
    ? (isExpanded ? FolderOpen : Folder)
    : getFileIcon(file.fileType, file.name)

  const handleClick = () => {
    if (isFolder) {
      toggleFolder(file.id)
    } else {
      onSelect(file.id)
    }
  }

  const handleRename = () => {
    if (newName.trim() && newName !== file.name) {
      renameFile(file.id, newName.trim())
    }
    setIsRenaming(false)
    setNewName(file.name)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRename()
    } else if (e.key === 'Escape') {
      setIsRenaming(false)
      setNewName(file.name)
    }
  }

  // Context menu items
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
        const parentId = isFolder ? file.id : file.parentId
        if (parentId) {
          addFile({
            name: 'Untitled.json',
            type: 'file',
            path: `${file.path}/Untitled.json`,
            parentId,
            fileType: 'json',
            size: 0,
          })
        }
      },
      disabled: !isFolder && !file.parentId,
    },
    {
      id: 'newFolder',
      label: 'New Folder',
      icon: <Folder className="w-4 h-4" />,
      onClick: () => {
        const parentId = isFolder ? file.id : file.parentId
        if (parentId) {
          addFolder({
            name: 'New Folder',
            type: 'folder',
            path: `${file.path}/New Folder`,
            parentId,
          })
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
      onClick: () => copyFile(file.id),
    },
    {
      id: 'cut',
      label: 'Cut',
      icon: <Scissors className="w-4 h-4" />,
      shortcut: 'Ctrl+X',
      onClick: () => cutFile(file.id),
      disabled: isFolder,
    },
    {
      id: 'paste',
      label: 'Paste',
      icon: <Copy className="w-4 h-4" />,
      shortcut: 'Ctrl+V',
      onClick: () => pasteFile(isFolder ? file.id : file.parentId),
      disabled: !clipboardFile || (!isFolder && !file.parentId),
    },
    { id: 'separator3', separator: true },
    {
      id: 'rename',
      label: 'Rename',
      icon: <Edit3 className="w-4 h-4" />,
      shortcut: 'F2',
      onClick: () => setIsRenaming(true),
    },
    {
      id: 'delete',
      label: 'Delete',
      icon: <Trash2 className="w-4 h-4" />,
      shortcut: 'Del',
      onClick: () => deleteFile(file.id),
      danger: true,
    },
  ]

  return (
    <div>
      <ContextMenu items={contextMenuItems}>
        <div
          className={cn(
            "flex items-center py-1 px-2 hover:bg-[#2a2d2e] cursor-pointer text-sm select-none group",
            isSelected && "bg-[#3c3c3c]",
            file.hasUnsavedChanges && "bg-[#1a472a]"
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
            <Icon className={cn(
              "w-4 h-4",
              isFolder ? "text-[#cccccc]" : getFileColor(file.fileType, file.name)
            )} />
          </div>
          
          {/* File name (editable when renaming) */}
          {isRenaming ? (
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onBlur={handleRename}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-[#3c3c3c] text-[#cccccc] px-1 rounded border border-[#007acc] focus:outline-none"
              autoFocus
            />
          ) : (
            <span className={cn(
              "flex-1 truncate text-[#cccccc]",
              file.hasUnsavedChanges && "text-[#4fc3f7]"
            )}>
              {file.name}
              {file.hasUnsavedChanges && <span className="ml-1">•</span>}
            </span>
          )}

          {/* File metadata (shown on hover for files) */}
          {!isFolder && !isRenaming && (
            <div className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 text-xs text-[#969696] flex items-center space-x-2">
              {file.size && (
                <span>{formatFileSize(file.size)}</span>
              )}
              {file.lastModified && (
                <span>{formatLastModified(file.lastModified)}</span>
              )}
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
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function EnhancedFileExplorer() {
  const {
    files,
    selectedFileId,
    selectFile,
    searchQuery,
    setSearchQuery,
    getFilteredFiles,
    isLoading,
    setLoading,
    addFile,
    addFolder,
  } = useFileStore()

  const [_showCreateMenu, setShowCreateMenu] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  
  // Prevent hydration mismatch
  useEffect(() => {
    setIsMounted(true)
  }, [])

  const displayFiles = searchQuery ? getFilteredFiles() : files

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    Array.from(files).forEach(file => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const _content = e.target?.result as string
        addFile({
          name: file.name,
          type: 'file',
          path: `/uploads/${file.name}`,
          parentId: '1', // Add to PLC Projects folder
          fileType: file.name.endsWith('.json') ? 'json' : 
                   file.name.endsWith('.acd') ? 'acd' :
                   file.name.endsWith('.l5x') ? 'l5x' : 'json',
          size: file.size,
        })
      }
      reader.readAsText(file)
    })

    event.target.value = '' // Reset input
  }

  const createMenuItems: ContextMenuItem[] = [
    {
      id: 'newFile',
      label: 'New PLC File',
      icon: <FileText className="w-4 h-4" />,
      onClick: () => {
        addFile({
          name: 'Untitled.json',
          type: 'file',
          path: '/projects/Untitled.json',
          parentId: '1',
          fileType: 'json',
          size: 0,
        })
        setShowCreateMenu(false)
      },
    },
    {
      id: 'newFolder',
      label: 'New Folder',
      icon: <Folder className="w-4 h-4" />,
      onClick: () => {
        addFolder({
          name: 'New Folder',
          type: 'folder',
          path: '/projects/New Folder',
          parentId: '1',
        })
        setShowCreateMenu(false)
      },
    },
    { id: 'separator', separator: true },
    {
      id: 'upload',
      label: 'Upload Files',
      icon: <Upload className="w-4 h-4" />,
      onClick: () => {
        document.getElementById('file-upload')?.click()
        setShowCreateMenu(false)
      },
    },
  ]

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
            onChange={(e) => setSearchQuery(e.target.value)}
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
              onClick={() => {
                setLoading(true)
                setTimeout(() => setLoading(false), 500) // Mock refresh
              }}
            >
              <RefreshCw className={cn(
                "w-4 h-4 text-[#cccccc]",
                isLoading && "animate-spin"
              )} />
            </button>
          </div>
        </div>
      </div>

      {/* File tree */}
      <div className="flex-1 overflow-auto">
        {!isMounted ? (
          <div className="p-4 text-center text-[#969696] text-sm">
            Loading...
          </div>
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
              onSelect={selectFile}
              isSelected={file.id === selectedFileId}
              selectedFileId={selectedFileId}
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
  )
} 