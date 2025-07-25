'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'
import { useLayoutStore } from '@/lib/stores/layout-store'
import { 
  Folder,
  FolderOpen,
  FileText,
  ChevronRight,
  ChevronDown,
  Plus,
  RefreshCw,
  GripVertical,
  BarChart3
} from 'lucide-react'

// NEW: @dnd-kit imports for Phase 33.8 Task 33.5.2
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
  DragOverEvent,
  DragOverlay,
  defaultDropAnimationSideEffects,
  DropAnimation,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import React from 'react' // Added for useEffect

interface FileItem {
  id: string
  name: string
  type: 'file' | 'folder'
  isExpanded?: boolean
  children?: FileItem[]
  path: string
  parentId?: string // NEW: For tracking parent relationships
}

const mockFiles: FileItem[] = [
  {
    id: '1',
    name: 'PLC Projects',
    type: 'folder',
    isExpanded: true,
    path: '/projects',
    children: [
      {
        id: '2',
        name: 'Distillation_Control.acd',
        type: 'file',
        path: '/projects/Distillation_Control.acd',
        parentId: '1'
      },
      {
        id: '3',
        name: 'Boiler_Safety.l5x',
        type: 'file',
        path: '/projects/Boiler_Safety.l5x',
        parentId: '1'
      },
      {
        id: '4',
        name: 'Control_Loops',
        type: 'folder',
        isExpanded: false,
        path: '/projects/Control_Loops',
        parentId: '1',
        children: [
          {
            id: '5',
            name: 'PID_Temperature.acd',
            type: 'file',
            path: '/projects/Control_Loops/PID_Temperature.acd',
            parentId: '4'
          },
          {
            id: '6',
            name: 'Flow_Control.acd',
            type: 'file',
            path: '/projects/Control_Loops/Flow_Control.acd',
            parentId: '4'
          }
        ]
      }
    ]
  },
  {
    id: '7',
    name: 'Workflows',
    type: 'folder',
    isExpanded: false,
    path: '/workflows',
    children: [
      {
        id: '8',
        name: 'Startup_Sequence.workflow',
        type: 'file',
        path: '/workflows/Startup_Sequence.workflow',
        parentId: '7'
      },
      {
        id: '9',
        name: 'Emergency_Shutdown.workflow',
        type: 'file',
        path: '/workflows/Emergency_Shutdown.workflow',
        parentId: '7'
      }
    ]
  },
  {
    id: '10',
    name: 'Templates',
    type: 'folder',
    isExpanded: false,
    path: '/templates',
    children: [
      {
        id: '11',
        name: 'Basic_PID_Template.acd',
        type: 'file',
        path: '/templates/Basic_PID_Template.acd',
        parentId: '10'
      }
    ]
  }
]

// NEW: Helper functions for drag-and-drop operations
const findFileById = (files: FileItem[], id: string): FileItem | null => {
  for (const file of files) {
    if (file.id === id) return file
    if (file.children) {
      const found = findFileById(file.children, id)
      if (found) return found
    }
  }
  return null
}

const removeFileFromTree = (files: FileItem[], id: string): FileItem[] => {
  return files.reduce<FileItem[]>((acc, file) => {
    if (file.id === id) {
      return acc // Remove this file
    }
    if (file.children) {
      return [...acc, { ...file, children: removeFileFromTree(file.children, id) }]
    }
    return [...acc, file]
  }, [])
}

const addFileToFolder = (files: FileItem[], fileToAdd: FileItem, targetFolderId: string): FileItem[] => {
  return files.map(file => {
    if (file.id === targetFolderId && file.type === 'folder') {
      const updatedFile = {
        ...fileToAdd,
        parentId: targetFolderId,
        path: `${file.path}/${fileToAdd.name}`
      }
      return {
        ...file,
        children: [...(file.children || []), updatedFile]
      }
    }
    if (file.children) {
      return { ...file, children: addFileToFolder(file.children, fileToAdd, targetFolderId) }
    }
    return file
  })
}

// NEW: Sortable File Item Component for drag-and-drop
interface SortableFileItemProps {
  item: FileItem
  depth: number
  isSelected: boolean
  onFileClick: (item: FileItem) => void
  isDragging?: boolean
  isOver?: boolean
  canDrop?: boolean
  focusedFileId?: string | null
  onKeyDown?: (e: React.KeyboardEvent, fileId: string) => void
}

function SortableFileItem({ 
  item, 
  depth, 
  isSelected, 
  onFileClick, 
  isDragging = false, 
  isOver = false, 
  canDrop = false,
  focusedFileId,
  onKeyDown
}: SortableFileItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ 
    id: item.id,
    data: {
      type: item.type,
      item: item
    }
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const Icon = item.type === 'folder' 
    ? (item.isExpanded ? FolderOpen : Folder) 
    : FileText

  // Use roving tabindex pattern for better keyboard navigation
  const isFocused = focusedFileId === item.id
  const tabIndex = isFocused ? 0 : -1

  // Combine @dnd-kit attributes with our ARIA attributes
  const combinedAttributes = {
    ...attributes,
    // Ensure our ARIA attributes override @dnd-kit ones
    role: "treeitem" as const,
    tabIndex: tabIndex,
    "aria-expanded": item.type === 'folder' ? item.isExpanded : undefined,
    "aria-selected": isSelected,
    "aria-label": `${item.type === 'folder' ? 'Folder' : 'File'}: ${item.name}${isSelected ? ' (selected)' : ''}${isSortableDragging ? ' (being dragged)' : ''}`,
    "aria-describedby": `${item.id}-instructions`,
    "aria-grabbed": isSortableDragging,
    "aria-dropeffect": (item.type === 'folder' && isOver 
      ? (canDrop ? "move" as const : "none" as const) 
      : undefined) as "move" | "none" | undefined,
    "data-file-id": item.id, // For focus management
    "data-testid": `file-${item.id}` // For testing
  }

  return (
    <>
      {/* Hidden instructions for screen readers */}
      <div id={`${item.id}-instructions`} className="sr-only">
        {item.type === 'folder' ? 'Folder' : 'File'}: {item.name}. 
        {item.type === 'folder' ? ' Press Enter to expand/collapse.' : ' Press Enter to open.'}
        {item.type === 'file' ? ' Drag to move to a folder.' : ''}
        Use arrow keys to navigate.
      </div>
      
      <div
        ref={setNodeRef}
        className={cn(
          "group relative flex items-center py-1 px-2 text-sm min-w-0 rounded-sm",
          "file-item transition-all duration-250 ease-in-out cursor-pointer",
          "hover:bg-[#2d2d30] focus:outline-none focus:bg-[#094771] focus:text-white focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 focus:ring-offset-[#1e1e1e]",
          isSelected && "bg-[#094771] text-white",
          isFocused && "ring-2 ring-blue-500 ring-offset-1 ring-offset-[#1e1e1e]",
          isSortableDragging && "dragging shadow-xl ring-2 ring-blue-400/75 scale-105 z-50 rotate-2",
          isDragging && "opacity-50",
          isOver && canDrop && item.type === 'folder' && "drop-target bg-blue-900/25 ring-2 ring-blue-400/50",
          isOver && !canDrop && "drop-invalid bg-red-900/25 ring-2 ring-red-400/50"
        )}
        style={{ paddingLeft: `${depth * 12 + 8}px`, ...style }}
        onClick={() => onFileClick(item)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onFileClick(item)
          } else if (onKeyDown) {
            onKeyDown(e, item.id)
          }
        }}
        {...combinedAttributes}
        {...listeners} // Apply drag listeners to entire file item for better UX
      >
        {/* Folder toggle chevron */}
        {item.type === 'folder' && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onFileClick(item)
            }}
            className="flex-shrink-0 mr-1 p-0.5 rounded hover:bg-[#3c3c3c] focus:outline-none focus:bg-[#3c3c3c]"
            aria-label={`${item.isExpanded ? 'Collapse' : 'Expand'} folder ${item.name}`}
            tabIndex={-1} // Prevent tab navigation to this button
          >
            {item.isExpanded ? (
              <ChevronDown className="w-3 h-3 text-[#cccccc]" />
            ) : (
              <ChevronRight className="w-3 h-3 text-[#cccccc]" />
            )}
          </button>
        )}

        {/* File/Folder icon */}
        <Icon 
          className={cn(
            "file-icon w-4 h-4 mr-2 flex-shrink-0",
            item.type === 'folder' ? "text-[#dcb67a]" : "text-[#519aba]",
            isSelected && "text-white"
          )}
          aria-hidden="true"
        />

        {/* File/Folder name */}
        <span 
          className={cn(
            "truncate text-[#cccccc] transition-colors duration-200",
            isSelected && "text-white",
            "group-hover:text-white"
          )}
        >
          {item.name}
        </span>

        {/* Enhanced Drag Handle - Only for files, larger and more visible */}
        {item.type === 'file' && (
          <div
            className={cn(
              "absolute right-2 top-1/2 -translate-y-1/2",
              "drag-handle opacity-0 group-hover:opacity-100 transition-all duration-300",
              "bg-[#094771]/80 backdrop-blur-sm rounded p-1 hover:bg-[#094771]",
              isSortableDragging && "opacity-100 bg-[#094771]"
            )}
            aria-label={`Drag ${item.name} to move it`}
            role="button"
            aria-describedby={`${item.id}-drag-instructions`}
          >
            <GripVertical 
              className="w-3 h-3 text-white/90" 
              aria-hidden="true"
            />
          </div>
        )}

        {/* Hidden drag instructions */}
        {item.type === 'file' && (
          <div id={`${item.id}-drag-instructions`} className="sr-only">
            Drag handle for {item.name}. Use mouse or keyboard to move this file to a folder.
          </div>
        )}

        {/* Drag tooltip */}
        {isSortableDragging && (
          <div 
            className="drag-tooltip -top-8 left-1/2 -translate-x-1/2"
            role="tooltip"
            aria-hidden="true"
          >
            Moving {item.name}
          </div>
        )}

        {/* Drop indicator for folders */}
        {isOver && canDrop && item.type === 'folder' && (
          <div 
            className="absolute right-1 top-1/2 -translate-y-1/2"
            aria-hidden="true"
          >
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
          </div>
        )}
      </div>
    </>
  )
}

function FileExplorer() {
  const [files, setFiles] = useState<FileItem[]>(mockFiles)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [overId, setOverId] = useState<string | null>(null)
  // NEW: Focus management for keyboard navigation
  const [focusedFileId, setFocusedFileId] = useState<string | null>(null)
  // NEW: ARIA live region for screen reader announcements
  const [announcement, setAnnouncement] = useState<string>('')
  const { setMainContentMode } = useLayoutStore()

  // NEW: @dnd-kit sensors configuration for Phase 33.8
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement required to start drag
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const toggleFolder = (id: string) => {
    const updateFiles = (items: FileItem[]): FileItem[] => {
      return items.map(item => {
        if (item.id === id && item.type === 'folder') {
          const newExpanded = !item.isExpanded
          // Announce folder state change
          setAnnouncement(`Folder ${item.name} ${newExpanded ? 'expanded' : 'collapsed'}`)
          return { ...item, isExpanded: newExpanded }
        }
        if (item.children) {
          return { ...item, children: updateFiles(item.children) }
        }
        return item
      })
    }
    
    setFiles(updateFiles(files))
  }

  const handleFileClick = (file: FileItem) => {
    if (file.type === 'folder') {
      toggleFolder(file.id)
    } else {
      setSelectedFile(file.id)
      setAnnouncement(`File ${file.name} selected`)
      // Here you would typically open the file in the editor
      console.log('Opening file:', file.path)
    }
    // Set focus for keyboard navigation
    setFocusedFileId(file.id)
  }

  // NEW: Keyboard navigation handlers for better accessibility
  const handleKeyDown = (e: React.KeyboardEvent, fileId: string) => {
    const allFiles = getAllFileIds(files)
    const currentIndex = allFiles.indexOf(fileId)
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        if (currentIndex < allFiles.length - 1) {
          const nextFileId = allFiles[currentIndex + 1]
          setFocusedFileId(nextFileId)
          setAnnouncement(`Navigated to ${findFileById(files, nextFileId)?.name}`)
          // Focus the next element
          setTimeout(() => {
            const nextElement = document.querySelector(`[data-file-id="${nextFileId}"]`) as HTMLElement
            nextElement?.focus()
          }, 0)
        }
        break
      case 'ArrowUp':
        e.preventDefault()
        if (currentIndex > 0) {
          const prevFileId = allFiles[currentIndex - 1]
          setFocusedFileId(prevFileId)
          setAnnouncement(`Navigated to ${findFileById(files, prevFileId)?.name}`)
          // Focus the previous element
          setTimeout(() => {
            const prevElement = document.querySelector(`[data-file-id="${prevFileId}"]`) as HTMLElement
            prevElement?.focus()
          }, 0)
        }
        break
      case 'ArrowRight':
        e.preventDefault()
        const file = findFileById(files, fileId)
        if (file?.type === 'folder' && !file.isExpanded) {
          toggleFolder(fileId)
        }
        break
      case 'ArrowLeft':
        e.preventDefault()
        const folderFile = findFileById(files, fileId)
        if (folderFile?.type === 'folder' && folderFile.isExpanded) {
          toggleFolder(fileId)
        }
        break
    }
  }

  // NEW: Drag-and-drop event handlers for Phase 33.8
  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string)
    const draggedFile = findFileById(files, event.active.id as string)
    setAnnouncement(`Started dragging ${draggedFile?.name}`)
  }

  const handleDragOver = (event: DragOverEvent) => {
    const { over } = event
    setOverId(over?.id as string | null)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    
    if (!over || active.id === over.id) {
      setActiveId(null)
      setOverId(null)
      if (active.id !== over?.id) {
        const draggedFile = findFileById(files, active.id as string)
        setAnnouncement(`Drag cancelled for ${draggedFile?.name}`)
      }
      return
    }

    const draggedFile = findFileById(files, active.id as string)
    const targetItem = findFileById(files, over.id as string)
    
    if (draggedFile && targetItem && targetItem.type === 'folder') {
      // Move file to folder
      const updatedFiles = removeFileFromTree(files, active.id as string)
      const finalFiles = addFileToFolder(updatedFiles, draggedFile, over.id as string)
      setFiles(finalFiles)
      
      // Announce successful move
      setAnnouncement(`${draggedFile.name} moved to folder ${targetItem.name}`)
      
      // Show success feedback
      const targetElement = document.querySelector(`[data-file-id="${over.id}"]`)
      if (targetElement) {
        targetElement.classList.add('drop-success')
        setTimeout(() => targetElement.classList.remove('drop-success'), 600)
      }
    } else {
      // Show error feedback
      setAnnouncement(`Cannot move ${draggedFile?.name} to ${targetItem?.name}. Only files can be moved to folders.`)
      const targetElement = document.querySelector(`[data-file-id="${over.id}"]`)
      if (targetElement) {
        targetElement.classList.add('drop-error')
        setTimeout(() => targetElement.classList.remove('drop-error'), 600)
      }
    }
    
    setActiveId(null)
    setOverId(null)
  }

  // Helper to collect all file IDs for sortable context
  const getAllFileIds = (items: FileItem[]): string[] => {
    let ids: string[] = []
    items.forEach(item => {
      ids.push(item.id)
      if (item.children) {
        ids = ids.concat(getAllFileIds(item.children))
      }
    })
    return ids
  }

  const renderFileItem = (item: FileItem, depth: number = 0): React.ReactNode => {
    const isOver = overId === item.id
    const isDragging = activeId === item.id
    const canDrop = item.type === 'folder' && !isDragging

    return (
      <div key={item.id}>
        <SortableFileItem 
          item={item}
          depth={depth}
          isSelected={selectedFile === item.id}
          onFileClick={handleFileClick}
          isDragging={isDragging}
          isOver={isOver}
          canDrop={canDrop}
          focusedFileId={focusedFileId}
          onKeyDown={handleKeyDown}
        />
        
        {item.type === 'folder' && item.isExpanded && item.children && (
          <div role="group" aria-label={`Contents of ${item.name}`}>
            {item.children.map(child => renderFileItem(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  // Initialize focus on first file if none selected
  React.useEffect(() => {
    if (!focusedFileId && files.length > 0) {
      setFocusedFileId(files[0].id)
    }
  }, [files, focusedFileId])

  // Find the currently dragged file for overlay
  const draggedFile = activeId ? findFileById(files, activeId) : null

  // NEW: Enhanced drop animation for better UX
  const dropAnimation: DropAnimation = {
    sideEffects: defaultDropAnimationSideEffects({
      styles: {
        active: {
          opacity: '0.5',
        },
      },
    }),
  }

  return (
    <DndContext 
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      {/* ARIA live region for announcements */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        role="status"
      >
        {announcement}
      </div>

      <div 
        className="h-full w-full flex flex-col"
        role="application"
        aria-label="File Explorer"
        aria-describedby="file-explorer-instructions"
      >
        {/* Screen reader instructions */}
        <div id="file-explorer-instructions" className="sr-only">
          File explorer with drag and drop support. Use Tab to navigate to files, arrow keys to move between files, 
          Enter to open files or expand folders, and drag files to move them between folders.
        </div>

        {/* Action buttons */}
        <div 
          className="flex items-center justify-end p-2 space-x-1 border-b border-[#3c3c3c]"
          role="toolbar"
          aria-label="File operations"
        >
          <button
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            title="New File"
            aria-label="Create new file"
          >
            <Plus className="w-4 h-4 text-[#cccccc]" />
          </button>
          <button
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            title="Refresh"
            aria-label="Refresh file explorer"
          >
            <RefreshCw className="w-4 h-4 text-[#cccccc]" />
          </button>
          <button
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            title="Analytics"
            aria-label="Switch to analytics view"
            onClick={() => setMainContentMode('analytics')}
          >
            <BarChart3 className="w-4 h-4 text-[#cccccc]" />
          </button>
        </div>

        {/* File tree with drag-and-drop and improved keyboard navigation */}
        <div 
          className="flex-1 w-full overflow-auto"
          role="tree"
          aria-label="File and folder tree"
          aria-multiselectable="false"
          aria-describedby="file-tree-instructions"
        >
          {/* Hidden tree instructions */}
          <div id="file-tree-instructions" className="sr-only">
            File tree. Use arrow keys to navigate, Enter to open items, 
            Right arrow to expand folders, Left arrow to collapse folders.
            Files can be dragged to folders to move them.
          </div>

          <SortableContext 
            items={getAllFileIds(files)} 
            strategy={verticalListSortingStrategy}
          >
            {files.map(item => renderFileItem(item))}
          </SortableContext>
        </div>

        {/* Footer with file count */}
        <div 
          className="p-2 border-t border-[#3c3c3c] text-xs text-[#969696]"
          role="status"
          aria-live="polite"
          aria-label="File count status"
        >
          {files.reduce((count, f) => count + (f.children?.length || 0) + 1, 0)} items
        </div>
      </div>

      {/* Enhanced Drag Overlay with better visual feedback */}
      <DragOverlay dropAnimation={dropAnimation}>
        {draggedFile && (
          <div 
            className="drag-overlay flex items-center py-1 px-2 bg-[#094771] text-white rounded min-w-0"
            role="img"
            aria-label={`Dragging ${draggedFile.name}`}
          >
            {draggedFile.type === 'folder' ? (
              <Folder className="file-icon w-4 h-4 mr-2 text-[#dcb67a] flex-shrink-0" />
            ) : (
              <FileText className="file-icon w-4 h-4 mr-2 text-[#519aba] flex-shrink-0" />
            )}
            <span className="text-sm truncate">{draggedFile.name}</span>
          </div>
        )}
      </DragOverlay>
    </DndContext>
  )
}

export default FileExplorer

/**
 * FileExplorer Component
 * 
 * @description File tree explorer for PLC projects and workflows
 * @specification Implements main-ui-spec.md FileExplorer tool requirements
 * 
 * @features
 * - Hierarchical file tree with expand/collapse
 * - File type icons and proper visual hierarchy
 * - Selection state management
 * - Action buttons for file operations
 * - Responsive to panel resizing
 * - PLC-specific file types (.acd, .l5x, .workflow)
 * 
 * @accessibility
 * - Keyboard navigation support
 * - ARIA tree structure
 * - Clear visual indicators
 * - Screen reader friendly
 * 
 * @performance
 * - Lazy loaded via Suspense
 * - Optimized tree rendering
 * - Efficient state updates
 */ 