/**
 * Modal Resize Handles Component - AI Task Orchestrator TypeScript Implementation
 *
 * @description Type-safe resize handles for modal resizing functionality
 * @compliance Strict TypeScript with zero `any` types
 * @integration React components with proper event handling
 */

import { cn } from '@/lib/utils/cn';
import React from 'react';
import {
  type ResizeHandle,
  type ResizeHandleConfig,
  isValidResizeHandle,
} from '../types/modal-types';

// ========================================
// Individual Resize Handle Component
// ========================================

interface ResizeHandleProps {
  readonly handle: ResizeHandle;
  readonly config: ResizeHandleConfig;
  readonly onResizeStart: (event: React.MouseEvent<HTMLElement>) => void;
  readonly isResizing: boolean;
  readonly className?: string;
}

const ResizeHandleComponent: React.FC<ResizeHandleProps> = ({
  handle,
  config,
  onResizeStart,
  isResizing,
  className,
}) => {
  const handleMouseDown = (event: React.MouseEvent<HTMLElement>) => {
    event.preventDefault();
    event.stopPropagation();
    onResizeStart(event);
  };

  // Handle-specific styling
  const getHandleClasses = (): string => {
    const baseClasses = [
      'absolute',
      'z-50',
      'opacity-0',
      'hover:opacity-100',
      'transition-opacity',
      'duration-200',
      'bg-blue-500',
      'hover:bg-blue-400',
    ];

    if (isResizing) {
      baseClasses.push('opacity-100', 'bg-blue-400');
    }

    // Size and positioning classes based on handle type
    switch (handle) {
      case 'n':
      case 's':
        baseClasses.push('w-full', 'h-1', '-translate-x-1/2');
        break;
      case 'e':
      case 'w':
        baseClasses.push('w-1', 'h-full', '-translate-y-1/2');
        break;
      case 'ne':
      case 'nw':
      case 'se':
      case 'sw':
        baseClasses.push('w-3', 'h-3');
        break;
    }

    return baseClasses.join(' ');
  };

  const getHandleStyles = (): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      cursor: config.cursor,
      ...config.position,
    };

    // Corner handles need special positioning adjustments
    switch (handle) {
      case 'ne':
        return { ...baseStyle, transform: 'translate(50%, -50%)' };
      case 'nw':
        return { ...baseStyle, transform: 'translate(-50%, -50%)' };
      case 'se':
        return { ...baseStyle, transform: 'translate(50%, 50%)' };
      case 'sw':
        return { ...baseStyle, transform: 'translate(-50%, 50%)' };
      default:
        return baseStyle;
    }
  };

  return (
    <div
      className={cn(getHandleClasses(), className)}
      style={getHandleStyles()}
      onMouseDown={handleMouseDown}
      data-resize-handle={handle}
      data-testid={`resize-handle-${handle}`}
      role="button"
      tabIndex={-1}
      aria-label={`Resize modal ${handle}`}
    />
  );
};

// ========================================
// Modal Resize Handles Container
// ========================================

interface ModalResizeHandlesProps {
  readonly handles: ReadonlyArray<ResizeHandleConfig>;
  readonly onResizeStart: (handle: ResizeHandle) => (event: React.MouseEvent<HTMLElement>) => void;
  readonly currentResizeHandle: ResizeHandle | null;
  readonly enabled: boolean;
  readonly className?: string;
}

export const ModalResizeHandles: React.FC<ModalResizeHandlesProps> = ({
  handles,
  onResizeStart,
  currentResizeHandle,
  enabled,
  className,
}) => {
  if (!enabled) {
    return null;
  }

  return (
    <>
      {handles.map(handleConfig => {
        if (!isValidResizeHandle(handleConfig.handle)) {
          console.warn(`Invalid resize handle: ${handleConfig.handle}`);
          return null;
        }

        const isCurrentlyResizing = currentResizeHandle === handleConfig.handle;

        return (
          <ResizeHandleComponent
            key={handleConfig.handle}
            handle={handleConfig.handle}
            config={handleConfig}
            onResizeStart={onResizeStart(handleConfig.handle)}
            isResizing={isCurrentlyResizing}
            className={className}
          />
        );
      })}
    </>
  );
};

// ========================================
// Resize Overlay Component (Optional)
// ========================================

interface ResizeOverlayProps {
  readonly isResizing: boolean;
  readonly currentHandle: ResizeHandle | null;
  readonly className?: string;
}

export const ResizeOverlay: React.FC<ResizeOverlayProps> = ({
  isResizing,
  currentHandle,
  className,
}) => {
  if (!isResizing || !currentHandle) {
    return null;
  }

  const getOverlayCursor = (): string => {
    switch (currentHandle) {
      case 'n':
      case 's':
        return 'cursor-ns-resize';
      case 'e':
      case 'w':
        return 'cursor-ew-resize';
      case 'ne':
      case 'sw':
        return 'cursor-nesw-resize';
      case 'nw':
      case 'se':
        return 'cursor-nwse-resize';
      default:
        return 'cursor-default';
    }
  };

  return (
    <div
      className={cn(
        'fixed inset-0 z-[9999] bg-transparent select-none',
        getOverlayCursor(),
        className
      )}
      data-testid="resize-overlay"
      aria-hidden="true"
    />
  );
};

// ========================================
// Utility Components
// ========================================

interface ResizeIndicatorProps {
  readonly isResizing: boolean;
  readonly currentSize: { readonly width: number; readonly height: number };
  readonly className?: string;
}

export const ResizeIndicator: React.FC<ResizeIndicatorProps> = ({
  isResizing,
  currentSize,
  className,
}) => {
  if (!isResizing) {
    return null;
  }

  return (
    <div
      className={cn(
        'absolute top-0 right-0 bg-black/75 text-white text-xs px-2 py-1 rounded-bl',
        'pointer-events-none select-none z-50',
        className
      )}
      data-testid="resize-indicator"
      aria-live="polite"
    >
      {Math.round(currentSize.width)} × {Math.round(currentSize.height)}
    </div>
  );
};

// ========================================
// Compound Export
// ========================================

export const ModalResizeComponents = {
  Handles: ModalResizeHandles,
  Overlay: ResizeOverlay,
  Indicator: ResizeIndicator,
} as const;
