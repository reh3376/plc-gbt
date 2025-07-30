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
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import React from 'react';

// File item wrapper props
interface FileItemWrapperProps {
  file: FileItem;
  depth: number;
  isSelected: boolean;
  onSelect: (fileId: string) => void;
  onToggleFolder: (fileId: string) => void;
  onContextMenu: (event: React.MouseEvent, file: FileItem) => void;
  children: React.ReactNode;
  className?: string;
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
  onContextMenu,
  children,
  className,
}: FileItemWrapperProps): React.ReactElement {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging, isOver } =
    useSortable({
      id: file.id,
      data: {
        type: file.type,
        file,
      },
    });

  // Apply transform styles for dragging
  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  // Handle click events (need to differentiate between select and drag)
  const handleClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    if (file.type === 'folder') {
      onToggleFolder(file.id);
    } else {
      onSelect(file.id);
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
          isOver && 'bg-[#2a2d2e] border-l-2 border-[#007acc]',
          'focus:outline-none focus:ring-2 focus:ring-blue-500'
        )}
        style={{
          paddingLeft: `${depth * 16 + 8}px`,
          ...style,
        }}
        onClick={handleClick}
        onContextMenu={handleContextMenu}
        aria-selected={isSelected}
        aria-expanded={file.type === 'folder' ? file.isExpanded : undefined}
        {...attributes}
        {...listeners}
      >
        {/* File content - children are now direct flex children */}
        {children}
      </div>
    </div>
  );
}
