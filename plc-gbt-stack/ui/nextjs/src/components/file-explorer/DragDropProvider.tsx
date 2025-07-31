/**
 * Drag and Drop Provider - AI Task Orchestrator TypeScript Implementation
 *
 * @description React component for drag-and-drop file operations
 * @compliance Strict TypeScript - zero `any` types policy
 * @functionality File reordering, moving, and upload via drag-drop
 */

'use client';

import type { FileItem } from '@/lib/types/file-explorer.types';
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragOverlay,
  DragStartEvent,
  DropAnimation,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  defaultDropAnimationSideEffects,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import React, { useCallback, useState } from 'react';

// Drag and drop provider props
interface DragDropProviderProps {
  children: React.ReactNode;
  files: FileItem[];
  onFileDrop: (draggedFile: FileItem, targetFolder: FileItem) => Promise<void>;
  onFileReorder: (draggedFile: FileItem, targetIndex: number) => Promise<void>;
  onExternalFileDrop: (files: FileList, targetFolder: FileItem) => Promise<void>;
  enabled?: boolean;
}

// Drag overlay component
interface DragOverlayContentProps {
  draggedFile: FileItem | null;
}

function DragOverlayContent({ draggedFile }: DragOverlayContentProps): React.ReactElement | null {
  if (!draggedFile) return null;

  return (
    <div className="bg-[#252526] border border-[#007acc] rounded px-2 py-1 text-[#cccccc] text-sm shadow-lg">
      <span className="flex items-center">
        {draggedFile.type === 'folder' ? '📁' : '📄'} {draggedFile.name}
      </span>
    </div>
  );
}

/**
 * DragDropProvider Component
 *
 * @description Provides drag-and-drop context for file operations
 * @features File moving, reordering, external file drops
 */
export function DragDropProvider({
  children,
  files,
  onFileDrop,
  onFileReorder,
  onExternalFileDrop,
  enabled = true,
}: DragDropProviderProps): React.ReactElement {
  const [, setActiveId] = useState<string | null>(null);
  const [draggedFile, setDraggedFile] = useState<FileItem | null>(null);

  // Configure sensors for drag operations
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Require 8px movement to start drag
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Find file by ID in the file tree
  const findFileById = useCallback(
    (fileId: string, fileList: FileItem[] = files): FileItem | null => {
      for (const file of fileList) {
        if (file.id === fileId) {
          return file;
        }
        if (file.children) {
          const found = findFileById(fileId, file.children);
          if (found) return found;
        }
      }
      return null;
    },
    [files]
  );

  // Handle drag start
  const handleDragStart = useCallback(
    (event: DragStartEvent) => {
      const { active } = event;
      const fileId = active.id as string;
      const file = findFileById(fileId);

      if (file) {
        setActiveId(fileId);
        setDraggedFile(file);
      }
    },
    [findFileById]
  );

  // Handle drag over
  const handleDragOver = useCallback(
    (event: DragOverEvent) => {
      // We can add visual feedback here for valid drop zones
      const { over } = event;

      if (over) {
        const overId = over.id as string;
        const overFile = findFileById(overId);

        // Add visual feedback for valid drop targets
        if (overFile && overFile.type === 'folder') {
          // Could add CSS class for drop zone highlighting
        }
      }
    },
    [findFileById]
  );

  // Handle drag end
  const handleDragEnd = useCallback(
    async (event: DragEndEvent) => {
      const { active, over } = event;

      setActiveId(null);
      setDraggedFile(null);

      if (!over || !draggedFile) return;

      const overId = over.id as string;
      const overFile = findFileById(overId);

      // Handle drop on folder
      if (overFile && overFile.type === 'folder' && overFile.id !== draggedFile.id) {
        try {
          await onFileDrop(draggedFile, overFile);
        } catch (error) {
          console.error('Drop operation failed:', error);
        }
        return;
      }

      // Handle reordering within the same level
      if (active.id !== over.id) {
        const activeIndex = files.findIndex(file => file.id === active.id);
        const overIndex = files.findIndex(file => file.id === over.id);

        if (activeIndex !== -1 && overIndex !== -1) {
          try {
            await onFileReorder(draggedFile, overIndex);
          } catch (error) {
            console.error('Reorder operation failed:', error);
          }
        }
      }
    },
    [draggedFile, findFileById, files, onFileDrop, onFileReorder]
  );

  // Handle external file drops (from OS file explorer)
  const handleExternalDrop = useCallback(
    async (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();

      const { dataTransfer } = event;
      const droppedFiles = dataTransfer.files;

      if (droppedFiles.length === 0) return;

      // Find the target folder (closest folder element)
      const targetElement = event.currentTarget;
      const folderId = targetElement.getAttribute('data-folder-id');

      let targetFolder: FileItem | null = null;

      if (folderId) {
        targetFolder = findFileById(folderId);
      }

      // Default to root if no specific folder found
      if (!targetFolder) {
        // Find root folder or create a default one
        targetFolder = files.find(f => f.type === 'folder') || {
          id: 'root',
          name: 'Root',
          type: 'folder',
          path: '/',
          isExpanded: true,
        };
      }

      try {
        await onExternalFileDrop(droppedFiles, targetFolder);
      } catch (error) {
        console.error('External file drop failed:', error);
      }
    },
    [files, findFileById, onExternalFileDrop]
  );

  // Handle drag over for external files
  const handleExternalDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    // Allow dropping files from external sources
    event.dataTransfer.dropEffect = 'copy';
  }, []);

  // Drop animation configuration
  const dropAnimation: DropAnimation = {
    sideEffects: defaultDropAnimationSideEffects({
      styles: {
        active: {
          opacity: '0.5',
        },
      },
    }),
  };

  // Get all file IDs for sortable context
  const getAllFileIds = useCallback((fileList: FileItem[]): string[] => {
    const ids: string[] = [];

    const extractIds = (files: FileItem[]): void => {
      for (const file of files) {
        ids.push(file.id);
        if (file.children) {
          extractIds(file.children);
        }
      }
    };

    extractIds(fileList);
    return ids;
  }, []);

  if (!enabled) {
    return <>{children}</>;
  }

  const fileIds = getAllFileIds(files);

  return (
    <div onDrop={handleExternalDrop} onDragOver={handleExternalDragOver} className="h-full w-full">
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <SortableContext items={fileIds} strategy={verticalListSortingStrategy}>
          {children}
        </SortableContext>

        <DragOverlay dropAnimation={dropAnimation}>
          <DragOverlayContent draggedFile={draggedFile} />
        </DragOverlay>
      </DndContext>
    </div>
  );
}

/**
 * Hook for drag and drop file operations
 */
export function useDragDropFileOperations() {
  const [isDragging, setIsDragging] = useState(false);
  const [dragOverTarget, setDragOverTarget] = useState<string | null>(null);

  const setDragState = useCallback((dragging: boolean, target?: string) => {
    setIsDragging(dragging);
    setDragOverTarget(target || null);
  }, []);

  const clearDragState = useCallback(() => {
    setIsDragging(false);
    setDragOverTarget(null);
  }, []);

  return {
    isDragging,
    dragOverTarget,
    setDragState,
    clearDragState,
  };
}
