/**
 * Sortable File Item - AI Task Orchestrator TypeScript Implementation
 *
 * @description Draggable file item component for file explorer
 * @compliance Strict TypeScript - zero `any` types policy
 * @functionality Direct file/folder drag operations without grip handles
 */

'use client';

import type { FileItem } from '@/lib/types/file-explorer.types';
import { cn } from '@/lib/utils/cn';
import { useDroppable } from '@dnd-kit/core';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import React from 'react';

// File item wrapper props
interface FileItemWrapperProps {
  readonly file: FileItem;
  readonly depth: number;
  readonly isSelected: boolean;
  readonly onSelect: (fileId: string) => void;
  readonly onToggleFolder: (fileId: string) => void;
  readonly onDoubleClick?: (fileId: string) => void;
  readonly onContextMenu: (event: React.MouseEvent, file: FileItem) => void;
  readonly children: React.ReactNode;
  readonly className?: string;
}

/**
 * FileItemWrapper - Makes entire file item draggable without grip handles
 * Direct drag-and-drop on sustained click without requiring separate handles
 */
export function FileItemWrapper({
  file,
  depth,
  isSelected,
  onSelect,
  onToggleFolder,
  onDoubleClick,
  onContextMenu,
  children,
  className,
}: FileItemWrapperProps): React.ReactElement {
  // Folders are also droppable (can receive files)
  const droppable = useDroppable({
    id: file.id,
    data: {
      type: file.type,
      file,
      accepts: ['file', 'folder'], // Folders can accept both files and other folders
    },
    disabled: file.type !== 'folder', // Only enable for folders
  });

  // All items are draggable, but folders have reduced sortable sensitivity when acting as drop targets
  const sortable = useSortable({
    id: file.id,
    data: {
      type: file.type,
      file,
    },
    // Disable sortable behavior for folders when they're receiving drops
    disabled: file.type === 'folder' && droppable.isOver,
  });

  // Combine refs for folders (both draggable and droppable)
  const setNodeRef = (node: HTMLElement | null) => {
    sortable.setNodeRef(node);
    if (file.type === 'folder') {
      droppable.setNodeRef(node);
    }
  };

  // Use sortable properties for dragging behavior
  const { attributes, listeners, transform, transition, isDragging } = sortable;

  // Use droppable properties for drop zone behavior (folders only)
  const { isOver: isDropTarget } = droppable;

  // Debug: Log drag and drop states for folders
  React.useEffect(() => {
    if (file.type === 'folder') {
      if (isDropTarget) {
        console.log(`🎯 DROP TARGET - Folder "${file.name}" is receiving drop`);
      }
      if (isDragging) {
        console.log(`🖱️ DRAGGING - Folder "${file.name}" is being dragged`);
      }
    }
  }, [file.type, file.name, isDropTarget, isDragging]);

  // Apply transform styles for dragging
  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  // Handle click events (need to differentiate between select and drag)
  const handleClick = (event: React.MouseEvent) => {
    console.log(`🖱️ MOUSE CLICK - File: ${file.name}, Type: ${file.type}`);
    event.stopPropagation();

    // Always select the file/folder first for Location population
    onSelect(file.id);
    console.log(`🖱️ MOUSE CLICK - Selected file: ${file.id}`);

    // Focus the element to ensure it can receive keyboard events
    const target = event.currentTarget as HTMLElement;
    target.focus();
    console.log(`🖱️ MOUSE CLICK - Focused element for keyboard events`);

    // Then toggle folder if it's a folder
    if (file.type === 'folder') {
      onToggleFolder(file.id);
    }
  };

  // Handle double-click events to open files in editor
  const handleDoubleClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    if (file.type === 'file' && onDoubleClick) {
      onDoubleClick(file.id);
    }
  };

  // Handle keyboard events for accessibility
  const handleKeyDown = (event: React.KeyboardEvent) => {
    // ALWAYS log keyboard events to detect if handler is being called
    console.log(`🔥 KEYBOARD EVENT CAPTURED - Key: "${event.key}", Target:`, event.target);
    console.log(`🔥 KEYBOARD EVENT - File: ${file.name}, Type: ${file.type}`);
    console.log(`🔥 KEYBOARD EVENT - Event details:`, {
      key: event.key,
      code: event.code,
      ctrlKey: event.ctrlKey,
      metaKey: event.metaKey,
      defaultPrevented: event.defaultPrevented,
      bubbles: event.bubbles,
      target: event.target,
      currentTarget: event.currentTarget,
    });

    if (event.key === 'Enter' || event.key === ' ') {
      console.log(`🔥 KEYBOARD - ENTER/SPACE DETECTED! Processing...`);
      event.preventDefault();
      event.stopPropagation();

      // Always select the file/folder first for Location population
      onSelect(file.id);
      console.log(`🔥 KEYBOARD - Selected file: ${file.id}`);

      if (file.type === 'folder') {
        // Toggle folder expansion
        console.log(`🔥 KEYBOARD - Toggling folder: ${file.name}`);
        onToggleFolder(file.id);
      } else if (file.type === 'file' && onDoubleClick) {
        // Open file in editor (same as double-click behavior)
        console.log(`🔥 KEYBOARD - Opening file: ${file.name}`);
        onDoubleClick(file.id);
      } else {
        console.warn(
          `🔥 KEYBOARD - Cannot open file: type=${file.type}, onDoubleClick=${!!onDoubleClick}`
        );
      }
    } else {
      console.log(`🔥 KEYBOARD - Other key pressed: ${event.key}`);
    }
  };

  const handleContextMenu = (event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    onContextMenu(event, file);
  };

  // Dragging state - minimal overlay
  if (isDragging) {
    return (
      <div
        ref={setNodeRef}
        style={style}
        className={cn(
          'opacity-50 bg-[#252526] border border-[#007acc] rounded flex items-center py-1 px-2',
          className
        )}
        {...attributes}
      >
        {children}
      </div>
    );
  }

  // Normal state - entire file item is draggable
  return (
    <div className={cn('relative', className)} data-file-id={file.id} data-file-type={file.type}>
      <div
        ref={setNodeRef}
        className={cn(
          'flex items-center py-1 px-2 hover:bg-[#2a2d2e] cursor-pointer text-sm select-none transition-all duration-200',
          isSelected && 'bg-[#094771]',
          isDropTarget && 'bg-[#2a2d2e] border-l-2 border-[#007acc]',
          'focus:outline-none focus:ring-2 focus:ring-blue-500'
        )}
        style={{
          paddingLeft: `${depth * 16 + 8}px`,
          ...style,
        }}
        {...attributes}
        {...listeners}
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
        onKeyDown={handleKeyDown}
        onContextMenu={handleContextMenu}
        role="treeitem"
        tabIndex={0}
        aria-selected={isSelected}
        aria-expanded={file.type === 'folder' ? file.isExpanded : undefined}
        aria-label={`${file.type === 'folder' ? 'Folder' : 'File'}: ${file.name}`}
      >
        {/* File content - children are now direct flex children */}
        {children}
      </div>
    </div>
  );
}
