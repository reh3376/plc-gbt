'use client';

import { cn } from '@/lib/utils/cn';
import { ReactNode, useEffect, useRef, useState } from 'react';

export interface ContextMenuItem {
  id: string;
  label?: string;
  icon?: ReactNode;
  shortcut?: string;
  disabled?: boolean;
  separator?: boolean;
  submenu?: ContextMenuItem[];
  onClick?: () => void;
  danger?: boolean;
}

interface ContextMenuProps {
  items: ContextMenuItem[];
  children: ReactNode;
  disabled?: boolean;
}

export function ContextMenu({ items, children, disabled = false }: ContextMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const menuRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscapeKey);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [isOpen]);

  const handleContextMenu = (event: React.MouseEvent) => {
    if (disabled) return;

    event.preventDefault();
    event.stopPropagation();

    const menuWidth = 200; // Estimated menu width
    const menuHeight = items.length * 32; // Estimated menu height

    let x = event.clientX;
    let y = event.clientY;

    // Adjust position if menu would go off screen
    if (x + menuWidth > window.innerWidth) {
      x = window.innerWidth - menuWidth - 10;
    }
    if (y + menuHeight > window.innerHeight) {
      y = window.innerHeight - menuHeight - 10;
    }

    setPosition({ x, y });
    setIsOpen(true);
  };

  const handleItemClick = (item: ContextMenuItem) => {
    if (item.disabled) return;

    if (item.onClick) {
      item.onClick();
    }
    setIsOpen(false);
  };

  const renderMenuItem = (item: ContextMenuItem, index: number) => {
    if (item.separator) {
      return <div key={`separator-${index}`} className="h-[1px] bg-[#3c3c3c] mx-1 my-1" />;
    }

    return (
      <button
        key={item.id}
        onClick={() => handleItemClick(item)}
        disabled={item.disabled}
        className={cn(
          'w-full flex items-center justify-between px-3 py-2 text-sm text-left transition-colors',
          item.disabled && 'opacity-40 cursor-not-allowed text-[#505050] pointer-events-none',
          !item.disabled && 'hover:bg-[#3c3c3c] focus:bg-[#3c3c3c] focus:outline-none',
          !item.disabled && item.danger && 'text-red-400 hover:text-red-300',
          !item.disabled && !item.danger && 'text-[#cccccc] hover:text-white'
        )}
      >
        <div className="flex items-center space-x-2">
          {item.icon && (
            <span className="w-4 h-4 flex items-center justify-center">{item.icon}</span>
          )}
          {item.label && <span>{item.label}</span>}
        </div>
        {item.shortcut && <span className="text-xs text-[#969696]">{item.shortcut}</span>}
      </button>
    );
  };

  return (
    <>
      <div ref={triggerRef} onContextMenu={handleContextMenu} className="w-full">
        {children}
      </div>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />

          {/* Context Menu */}
          <div
            ref={menuRef}
            className="fixed z-50 bg-[#2d2d30] border border-[#3c3c3c] rounded shadow-lg py-1 min-w-[180px]"
            style={{
              left: position.x,
              top: position.y,
            }}
          >
            {items.map((item, index) => renderMenuItem(item, index))}
          </div>
        </>
      )}
    </>
  );
}
