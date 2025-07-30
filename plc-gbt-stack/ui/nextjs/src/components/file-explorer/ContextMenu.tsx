/**
 * File Explorer Context Menu - AI Task Orchestrator TypeScript Implementation
 *
 * @description Right-click context menu for file and folder operations
 * @compliance Strict TypeScript - zero `any` types policy
 * @functionality Complete context menu with all file operations
 */

'use client';

import type { FileItem } from '@/lib/types/file-explorer.types';
import { cn } from '@/lib/utils/cn';
import { Copy, Edit3, File, Folder, Info, Scissors, Trash2, Upload } from 'lucide-react';
import React, { useCallback, useEffect, useRef, useState } from 'react';

// Context menu item definition
interface ContextMenuItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  action: () => void;
  disabled?: boolean;
  separator?: boolean;
  danger?: boolean;
}

// Context menu position
interface ContextMenuPosition {
  x: number;
  y: number;
}

// Context menu props
interface ContextMenuProps {
  isOpen: boolean;
  position: ContextMenuPosition;
  targetFile: FileItem | null;
  onClose: () => void;
  onRename: (file: FileItem) => void;
  onDelete: (file: FileItem) => void;
  onCopy: (file: FileItem) => void;
  onCut: (file: FileItem) => void;
  onPaste: (targetFolder: FileItem) => void;
  onCreateFile: (parentFolder: FileItem) => void;
  onCreateFolder: (parentFolder: FileItem) => void;
  onShowProperties: (file: FileItem) => void;
  canPaste: boolean;
  className?: string;
}

/**
 * ContextMenu Component
 *
 * @description Right-click context menu for file operations
 * @features Full file operations, keyboard navigation, proper positioning
 */
export function ContextMenu({
  isOpen,
  position,
  targetFile,
  onClose,
  onRename,
  onDelete,
  onCopy,
  onCut,
  onPaste,
  onCreateFile,
  onCreateFolder,
  onShowProperties,
  canPaste,
  className,
}: ContextMenuProps): React.ReactElement | null {
  const menuRef = useRef<HTMLDivElement>(null);
  const [adjustedPosition, setAdjustedPosition] = useState(position);

  // Adjust menu position to prevent overflow
  useEffect(() => {
    if (isOpen && menuRef.current) {
      const menuRect = menuRef.current.getBoundingClientRect();
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight,
      };

      let adjustedX = position.x;
      let adjustedY = position.y;

      // Adjust horizontal position
      if (position.x + menuRect.width > viewport.width) {
        adjustedX = viewport.width - menuRect.width - 10;
      }

      // Adjust vertical position
      if (position.y + menuRect.height > viewport.height) {
        adjustedY = viewport.height - menuRect.height - 10;
      }

      // Ensure minimum margins
      adjustedX = Math.max(10, adjustedX);
      adjustedY = Math.max(10, adjustedY);

      setAdjustedPosition({ x: adjustedX, y: adjustedY });
    }
  }, [isOpen, position]);

  // Handle click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);

      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [isOpen, onClose]);

  // Generate context menu items based on target file
  const getMenuItems = useCallback((): ContextMenuItem[] => {
    if (!targetFile) return [];

    const isFolder = targetFile.type === 'folder';
    const items: ContextMenuItem[] = [];

    // File/Folder specific operations
    if (isFolder) {
      items.push(
        {
          id: 'new-file',
          label: 'New File',
          icon: File,
          action: () => {
            onCreateFile(targetFile);
            onClose();
          },
        },
        {
          id: 'new-folder',
          label: 'New Folder',
          icon: Folder,
          action: () => {
            onCreateFolder(targetFile);
            onClose();
          },
        },
        {
          id: 'separator-1',
          label: '',
          icon: File,
          action: () => {},
          separator: true,
        }
      );

      // Paste option for folders
      if (canPaste) {
        items.push({
          id: 'paste',
          label: 'Paste',
          icon: Upload,
          action: () => {
            onPaste(targetFile);
            onClose();
          },
        });
      }
    }

    // Common operations for both files and folders
    items.push(
      {
        id: 'copy',
        label: 'Copy',
        icon: Copy,
        action: () => {
          onCopy(targetFile);
          onClose();
        },
      },
      {
        id: 'cut',
        label: 'Cut',
        icon: Scissors,
        action: () => {
          onCut(targetFile);
          onClose();
        },
      },
      {
        id: 'separator-2',
        label: '',
        icon: File,
        action: () => {},
        separator: true,
      },
      {
        id: 'rename',
        label: 'Rename',
        icon: Edit3,
        action: () => {
          onRename(targetFile);
          onClose();
        },
      },
      {
        id: 'delete',
        label: 'Delete',
        icon: Trash2,
        action: () => {
          onDelete(targetFile);
          onClose();
        },
        danger: true,
      },
      {
        id: 'separator-3',
        label: '',
        icon: File,
        action: () => {},
        separator: true,
      },
      {
        id: 'properties',
        label: 'Properties',
        icon: Info,
        action: () => {
          onShowProperties(targetFile);
          onClose();
        },
      }
    );

    return items;
  }, [
    targetFile,
    canPaste,
    onCreateFile,
    onCreateFolder,
    onPaste,
    onCopy,
    onCut,
    onRename,
    onDelete,
    onShowProperties,
    onClose,
  ]);

  // Handle menu item click
  const handleItemClick = useCallback((item: ContextMenuItem, event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();

    if (!item.disabled && !item.separator) {
      item.action();
    }
  }, []);

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      const menuItems = getMenuItems().filter(item => !item.separator && !item.disabled);
      const currentFocus = document.activeElement as HTMLElement;
      const focusedIndex = menuItems.findIndex(
        item => currentFocus?.getAttribute('data-item-id') === item.id
      );

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          const nextIndex = (focusedIndex + 1) % menuItems.length;
          const nextElement = menuRef.current?.querySelector(
            `[data-item-id="${menuItems[nextIndex].id}"]`
          ) as HTMLElement;
          nextElement?.focus();
          break;

        case 'ArrowUp':
          event.preventDefault();
          const prevIndex = focusedIndex <= 0 ? menuItems.length - 1 : focusedIndex - 1;
          const prevElement = menuRef.current?.querySelector(
            `[data-item-id="${menuItems[prevIndex].id}"]`
          ) as HTMLElement;
          prevElement?.focus();
          break;

        case 'Enter':
        case ' ':
          event.preventDefault();
          if (focusedIndex >= 0) {
            menuItems[focusedIndex].action();
          }
          break;

        case 'Escape':
          event.preventDefault();
          onClose();
          break;
      }
    },
    [getMenuItems, onClose]
  );

  if (!isOpen || !targetFile) {
    return null;
  }

  const menuItems = getMenuItems();

  return (
    <div
      ref={menuRef}
      className={cn(
        'fixed z-50 min-w-[180px] bg-[#2d2d30] border border-[#5a5a5a] rounded-md shadow-lg py-1',
        'focus:outline-none',
        className
      )}
      style={{
        left: adjustedPosition.x,
        top: adjustedPosition.y,
      }}
      role="menu"
      aria-label="File context menu"
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      {menuItems.map((item, index) => {
        if (item.separator) {
          return (
            <div key={`separator-${index}`} className="h-px bg-[#5a5a5a] my-1" role="separator" />
          );
        }

        const IconComponent = item.icon;

        return (
          <button
            key={item.id}
            data-item-id={item.id}
            className={cn(
              'w-full px-3 py-2 flex items-center text-left text-sm transition-colors',
              'hover:bg-[#094771] focus:bg-[#094771] focus:outline-none',
              item.disabled && 'opacity-50 cursor-not-allowed',
              item.danger
                ? 'text-[#f14c4c] hover:text-white focus:text-white'
                : 'text-[#cccccc] hover:text-white focus:text-white'
            )}
            onClick={event => handleItemClick(item, event)}
            disabled={item.disabled}
            role="menuitem"
            tabIndex={-1}
          >
            <IconComponent className="w-4 h-4 mr-3 flex-shrink-0" />
            <span className="truncate">{item.label}</span>
          </button>
        );
      })}
    </div>
  );
}

/**
 * Context Menu Hook
 *
 * @description Custom hook for managing context menu state
 */
export function useContextMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState<ContextMenuPosition>({ x: 0, y: 0 });
  const [targetFile, setTargetFile] = useState<FileItem | null>(null);

  const openContextMenu = useCallback((event: React.MouseEvent, file: FileItem) => {
    event.preventDefault();
    event.stopPropagation();

    setPosition({ x: event.clientX, y: event.clientY });
    setTargetFile(file);
    setIsOpen(true);
  }, []);

  const closeContextMenu = useCallback(() => {
    setIsOpen(false);
    setTargetFile(null);
  }, []);

  return {
    isOpen,
    position,
    targetFile,
    openContextMenu,
    closeContextMenu,
  };
}
