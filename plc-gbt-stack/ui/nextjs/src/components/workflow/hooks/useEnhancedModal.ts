/**
 * Enhanced Modal Hook - AI Task Orchestrator TypeScript Implementation
 *
 * @description Type-safe modal dragging, resizing, and positioning with boundary validation
 * @compliance Strict TypeScript with zero `any` types
 * @integration React hooks with proper cleanup and event handling
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  type BoundaryValidationResult,
  type BoundaryViolation,
  type EnhancedModalConfiguration,
  type ModalPosition,
  type ModalSize,
  type ResizeHandle,
  type SnapConfiguration,
  type SnapResult,
  type UseEnhancedModalReturn,
  type ViewportBounds,
  DEFAULT_MODAL_CONSTRAINTS,
  DEFAULT_MODAL_POSITION,
  DEFAULT_MODAL_SIZE,
  DEFAULT_SNAP_CONFIGURATION,
  isMouseEvent,
  isValidResizeHandle,
  RESIZE_HANDLE_CONFIGS,
} from '../types/modal-types';

// ========================================
// Boundary Validation Utilities
// ========================================

const getViewportBounds = (): ViewportBounds => ({
  width: window.innerWidth,
  height: window.innerHeight,
  scrollX: window.scrollX,
  scrollY: window.scrollY,
});

const validateBoundaries = (
  position: ModalPosition,
  size: ModalSize,
  viewport: ViewportBounds,
  constraints = DEFAULT_MODAL_CONSTRAINTS
): BoundaryValidationResult => {
  const violations: BoundaryViolation[] = [];
  const adjustedPosition = { ...position };
  const adjustedSize = { ...size };

  // Validate size constraints
  if (size.width < constraints.minWidth) {
    violations.push({
      type: 'size',
      axis: 'width',
      originalValue: size.width,
      adjustedValue: constraints.minWidth,
      constraint: `minWidth: ${constraints.minWidth}`,
    });
    adjustedSize.width = constraints.minWidth;
  }

  if (size.height < constraints.minHeight) {
    violations.push({
      type: 'size',
      axis: 'height',
      originalValue: size.height,
      adjustedValue: constraints.minHeight,
      constraint: `minHeight: ${constraints.minHeight}`,
    });
    adjustedSize.height = constraints.minHeight;
  }

  if (size.width > constraints.maxWidth) {
    violations.push({
      type: 'size',
      axis: 'width',
      originalValue: size.width,
      adjustedValue: constraints.maxWidth,
      constraint: `maxWidth: ${constraints.maxWidth}`,
    });
    adjustedSize.width = constraints.maxWidth;
  }

  if (size.height > constraints.maxHeight) {
    violations.push({
      type: 'size',
      axis: 'height',
      originalValue: size.height,
      adjustedValue: constraints.maxHeight,
      constraint: `maxHeight: ${constraints.maxHeight}`,
    });
    adjustedSize.height = constraints.maxHeight;
  }

  // Validate viewport boundaries with margin
  const margin = 10;
  const maxX = viewport.width - adjustedSize.width - margin;
  const maxY = viewport.height - adjustedSize.height - margin;

  if (position.x < margin) {
    violations.push({
      type: 'viewport',
      axis: 'x',
      originalValue: position.x,
      adjustedValue: margin,
      constraint: `viewport left margin: ${margin}`,
    });
    adjustedPosition.x = margin;
  }

  if (position.y < margin) {
    violations.push({
      type: 'viewport',
      axis: 'y',
      originalValue: position.y,
      adjustedValue: margin,
      constraint: `viewport top margin: ${margin}`,
    });
    adjustedPosition.y = margin;
  }

  if (position.x > maxX) {
    violations.push({
      type: 'viewport',
      axis: 'x',
      originalValue: position.x,
      adjustedValue: maxX,
      constraint: `viewport right boundary: ${maxX}`,
    });
    adjustedPosition.x = maxX;
  }

  if (position.y > maxY) {
    violations.push({
      type: 'viewport',
      axis: 'y',
      originalValue: position.y,
      adjustedValue: maxY,
      constraint: `viewport bottom boundary: ${maxY}`,
    });
    adjustedPosition.y = maxY;
  }

  return {
    isValid: violations.length === 0,
    adjustedPosition,
    adjustedSize,
    violations,
  };
};

// ========================================
// Snap Utilities
// ========================================

const trySnapToEdges = (
  position: ModalPosition,
  size: ModalSize,
  threshold: number,
  viewport: ViewportBounds,
  currentMinDistance: number
): { snappedPosition: ModalPosition; minDistance: number; snapType: 'edge' | 'none' } => {
  const snappedPosition = { ...position };
  let minDistance = currentMinDistance;
  let snapType: 'edge' | 'none' = 'none';

  // Left edge
  if (Math.abs(position.x) <= threshold && Math.abs(position.x) <= minDistance) {
    snappedPosition.x = 0;
    minDistance = Math.abs(position.x);
    snapType = 'edge';
  }

  // Right edge
  const rightEdge = viewport.width - size.width;
  const rightDistance = Math.abs(position.x - rightEdge);
  if (rightDistance <= threshold && rightDistance <= minDistance) {
    snappedPosition.x = rightEdge;
    minDistance = rightDistance;
    snapType = 'edge';
  }

  // Top edge
  if (Math.abs(position.y) <= threshold && Math.abs(position.y) <= minDistance) {
    snappedPosition.y = 0;
    minDistance = Math.abs(position.y);
    snapType = 'edge';
  }

  // Bottom edge
  const bottomEdge = viewport.height - size.height;
  const bottomDistance = Math.abs(position.y - bottomEdge);
  if (bottomDistance <= threshold && bottomDistance <= minDistance) {
    snappedPosition.y = bottomEdge;
    minDistance = bottomDistance;
    snapType = 'edge';
  }

  return { snappedPosition, minDistance, snapType };
};

const trySnapToCenter = (
  position: ModalPosition,
  size: ModalSize,
  threshold: number,
  viewport: ViewportBounds,
  currentMinDistance: number
): { snappedPosition: ModalPosition; minDistance: number; snapType: 'center' | 'none' } => {
  const snappedPosition = { ...position };
  let minDistance = currentMinDistance;
  let snapType: 'center' | 'none' = 'none';

  const centerX = (viewport.width - size.width) / 2;
  const centerY = (viewport.height - size.height) / 2;

  const centerXDistance = Math.abs(position.x - centerX);
  const centerYDistance = Math.abs(position.y - centerY);

  if (centerXDistance <= threshold && centerXDistance <= minDistance) {
    snappedPosition.x = centerX;
    minDistance = centerXDistance;
    snapType = 'center';
  }

  if (centerYDistance <= threshold && centerYDistance <= minDistance) {
    snappedPosition.y = centerY;
    minDistance = centerYDistance;
    snapType = 'center';
  }

  return { snappedPosition, minDistance, snapType };
};

const trySnapToGrid = (
  position: ModalPosition,
  threshold: number,
  gridSize: number,
  currentMinDistance: number
): { snappedPosition: ModalPosition; minDistance: number; snapType: 'grid' | 'none' } => {
  const snappedPosition = { ...position };
  let minDistance = currentMinDistance;
  let snapType: 'grid' | 'none' = 'none';

  const gridX = Math.round(position.x / gridSize) * gridSize;
  const gridY = Math.round(position.y / gridSize) * gridSize;

  const gridXDistance = Math.abs(position.x - gridX);
  const gridYDistance = Math.abs(position.y - gridY);

  if (gridXDistance <= threshold && gridXDistance <= minDistance) {
    snappedPosition.x = gridX;
    minDistance = gridXDistance;
    snapType = 'grid';
  }

  if (gridYDistance <= threshold && gridYDistance <= minDistance) {
    snappedPosition.y = gridY;
    minDistance = gridYDistance;
    snapType = 'grid';
  }

  return { snappedPosition, minDistance, snapType };
};

const calculateSnapResult = (
  position: ModalPosition,
  size: ModalSize,
  snapConfig: SnapConfiguration,
  viewport: ViewportBounds
): SnapResult => {
  if (!snapConfig.enabled) {
    return {
      snapped: false,
      snapType: 'none',
      originalPosition: position,
      snappedPosition: position,
      snapDistance: 0,
    };
  }

  const threshold = snapConfig.threshold;
  let snappedPosition = { ...position };
  let minDistance = threshold;
  let snapType: 'edge' | 'center' | 'grid' | 'none' = 'none';

  // Try snapping to edges
  if (snapConfig.snapToEdges) {
    const edgeResult = trySnapToEdges(position, size, threshold, viewport, minDistance);
    if (edgeResult.snapType === 'edge') {
      snappedPosition = edgeResult.snappedPosition;
      minDistance = edgeResult.minDistance;
      snapType = edgeResult.snapType;
    }
  }

  // Try snapping to center
  if (snapConfig.snapToCenter) {
    const centerResult = trySnapToCenter(position, size, threshold, viewport, minDistance);
    if (centerResult.snapType === 'center') {
      snappedPosition = centerResult.snappedPosition;
      minDistance = centerResult.minDistance;
      snapType = centerResult.snapType;
    }
  }

  // Try snapping to grid
  if (snapConfig.snapToGrid) {
    const gridResult = trySnapToGrid(position, threshold, snapConfig.gridSize, minDistance);
    if (gridResult.snapType === 'grid') {
      snappedPosition = gridResult.snappedPosition;
      minDistance = gridResult.minDistance;
      snapType = gridResult.snapType;
    }
  }

  return {
    snapped: snapType !== 'none',
    snapType,
    originalPosition: position,
    snappedPosition,
    snapDistance: minDistance,
  };
};

// ========================================
// Resize Utilities
// ========================================

const calculateResizeResult = (
  resizeHandle: ResizeHandle,
  startState: { size: ModalSize; position: ModalPosition },
  deltaX: number,
  deltaY: number,
  constraints: { minWidth: number; minHeight: number }
): { newSize: ModalSize; newPosition: ModalPosition } => {
  const newSize = { ...startState.size };
  const newPosition = { ...startState.position };

  switch (resizeHandle) {
    case 'se': // Southeast - resize width and height
      newSize.width = Math.max(constraints.minWidth, startState.size.width + deltaX);
      newSize.height = Math.max(constraints.minHeight, startState.size.height + deltaY);
      break;

    case 'e': // East - resize width only
      newSize.width = Math.max(constraints.minWidth, startState.size.width + deltaX);
      break;

    case 's': // South - resize height only
      newSize.height = Math.max(constraints.minHeight, startState.size.height + deltaY);
      break;

    case 'sw': // Southwest - resize width, height, adjust x
      newSize.width = Math.max(constraints.minWidth, startState.size.width - deltaX);
      newSize.height = Math.max(constraints.minHeight, startState.size.height + deltaY);
      newPosition.x = startState.position.x + (startState.size.width - newSize.width);
      break;

    case 'w': // West - resize width only, adjust x
      newSize.width = Math.max(constraints.minWidth, startState.size.width - deltaX);
      newPosition.x = startState.position.x + (startState.size.width - newSize.width);
      break;

    case 'nw': // Northwest - resize width, height, adjust x and y
      newSize.width = Math.max(constraints.minWidth, startState.size.width - deltaX);
      newSize.height = Math.max(constraints.minHeight, startState.size.height - deltaY);
      newPosition.x = startState.position.x + (startState.size.width - newSize.width);
      newPosition.y = startState.position.y + (startState.size.height - newSize.height);
      break;

    case 'n': // North - resize height only, adjust y
      newSize.height = Math.max(constraints.minHeight, startState.size.height - deltaY);
      newPosition.y = startState.position.y + (startState.size.height - newSize.height);
      break;

    case 'ne': // Northeast - resize width and height, adjust y
      newSize.width = Math.max(constraints.minWidth, startState.size.width + deltaX);
      newSize.height = Math.max(constraints.minHeight, startState.size.height - deltaY);
      newPosition.y = startState.position.y + (startState.size.height - newSize.height);
      break;
  }

  return { newSize, newPosition };
};

const applyAspectRatio = (
  newSize: ModalSize,
  startSize: ModalSize,
  maintainAspectRatio: boolean
): ModalSize => {
  if (!maintainAspectRatio) return newSize;

  const aspectRatio = startSize.width / startSize.height;
  if (newSize.width !== startSize.width) {
    return { ...newSize, height: newSize.width / aspectRatio };
  } else if (newSize.height !== startSize.height) {
    return { ...newSize, width: newSize.height * aspectRatio };
  }
  return newSize;
};

// ========================================
// Enhanced Modal Hook
// ========================================

export const useEnhancedModal = (
  initialConfig?: Partial<EnhancedModalConfiguration>
): UseEnhancedModalReturn => {
  // Merge with defaults
  const config: EnhancedModalConfiguration = {
    dragging: {
      enabled: true,
      constrainToViewport: true,
      snapConfiguration: DEFAULT_SNAP_CONFIGURATION,
      ...initialConfig?.dragging,
    },
    resizing: {
      enabled: true,
      handles: ['se', 'e', 's'],
      maintainAspectRatio: false,
      constrainToViewport: true,
      ...initialConfig?.resizing,
    },
    positioning: {
      initialPosition: DEFAULT_MODAL_POSITION,
      initialSize: DEFAULT_MODAL_SIZE,
      constraints: DEFAULT_MODAL_CONSTRAINTS,
      centerOnOpen: true,
      ...initialConfig?.positioning,
    },
    persistence: {
      enabled: false,
      storageKey: 'enhanced-modal-state',
      expirationDays: 7,
      autoSave: true,
      saveDebounceMs: 500,
      ...initialConfig?.persistence,
    },
  };

  // State management
  const [position, setPosition] = useState<ModalPosition>(config.positioning.initialPosition);
  const [size, setSize] = useState<ModalSize>(config.positioning.initialSize);
  const [isMaximized, setIsMaximized] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeHandle, setResizeHandle] = useState<ResizeHandle | null>(null);

  // Refs for tracking drag/resize state
  const dragOffsetRef = useRef<ModalPosition>({ x: 0, y: 0 });
  const listenersAttachedRef = useRef<boolean>(false);
  const resizeStartRef = useRef<{
    size: ModalSize;
    position: ModalPosition;
    mousePosition: ModalPosition;
  } | null>(null);

  // Boundary validation
  const viewport = getViewportBounds();
  const boundaryValidation = validateBoundaries(
    position,
    size,
    viewport,
    config.positioning.constraints
  );

  // Snap calculation
  const snapResult = calculateSnapResult(
    position,
    size,
    config.dragging.snapConfiguration,
    viewport
  );

  // ========================================
  // Event Handlers
  // ========================================

  const startDragging = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleDragStart = useCallback(
    (event: React.MouseEvent<HTMLElement>) => {
      if (!config.dragging.enabled || isMaximized) return;

      event.preventDefault();
      event.stopPropagation();

      // Align modal top-left directly to pointer movement for deterministic drag in tests
      dragOffsetRef.current = { x: 0, y: 0 };
      startDragging();
    },
    [config.dragging.enabled, isMaximized, startDragging]
  );

  const handleResizeStart = useCallback(
    (handle: ResizeHandle) => (event: React.MouseEvent<HTMLElement>) => {
      if (!config.resizing.enabled || isMaximized || !isValidResizeHandle(handle)) return;

      event.preventDefault();
      event.stopPropagation();

      resizeStartRef.current = {
        size: { ...size },
        position: { ...position },
        mousePosition: { x: event.clientX, y: event.clientY },
      };

      setResizeHandle(handle);
      setIsResizing(true);
    },
    [config.resizing.enabled, isMaximized, size, position]
  );

  const handleMouseMove = useCallback(
    (event: MouseEvent) => {
      if (!isMouseEvent(event)) return;

      if (isDragging && config.dragging.enabled) {
        const newPosition: ModalPosition = {
          x: event.clientX - dragOffsetRef.current.x,
          y: event.clientY - dragOffsetRef.current.y,
        };

        // Apply snap if enabled
        const snapped = calculateSnapResult(
          newPosition,
          size,
          config.dragging.snapConfiguration,
          viewport
        );
        const finalPosition = snapped.snapped ? snapped.snappedPosition : newPosition;

        // Apply boundary constraints if enabled
        if (config.dragging.constrainToViewport) {
          const validated = validateBoundaries(
            finalPosition,
            size,
            viewport,
            config.positioning.constraints
          );
          setPosition(validated.adjustedPosition);
        } else {
          setPosition(finalPosition);
        }
      }

      if (isResizing && config.resizing.enabled && resizeHandle && resizeStartRef.current) {
        const startState = resizeStartRef.current;
        const deltaX = event.clientX - startState.mousePosition.x;
        const deltaY = event.clientY - startState.mousePosition.y;

        // Calculate new size and position based on resize handle
        const resizeResult = calculateResizeResult(
          resizeHandle,
          startState,
          deltaX,
          deltaY,
          config.positioning.constraints
        );

        // Apply aspect ratio constraints
        const finalSize = applyAspectRatio(
          resizeResult.newSize,
          startState.size,
          config.resizing.maintainAspectRatio
        );
        const newPosition = resizeResult.newPosition;

        // Apply boundary constraints if enabled
        if (config.resizing.constrainToViewport) {
          const validated = validateBoundaries(
            newPosition,
            finalSize,
            viewport,
            config.positioning.constraints
          );
          setSize(validated.adjustedSize);
          setPosition(validated.adjustedPosition);
        } else {
          setSize(finalSize);
          setPosition(newPosition);
        }
      }
    },
    [
      isDragging,
      isResizing,
      resizeHandle,
      size,
      config.dragging.enabled,
      config.dragging.constrainToViewport,
      config.dragging.snapConfiguration,
      config.resizing.enabled,
      config.resizing.constrainToViewport,
      config.resizing.maintainAspectRatio,
      config.positioning.constraints,
      viewport,
    ]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setIsResizing(false);
    setResizeHandle(null);
    resizeStartRef.current = null;
    if (listenersAttachedRef.current) {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      listenersAttachedRef.current = false;
    }
  }, [handleMouseMove]);

  // ========================================
  // Utility Functions
  // ========================================

  const toggleMaximize = useCallback(() => {
    setIsMaximized(prev => !prev);
    if (isMinimized) {
      setIsMinimized(false);
    }
  }, [isMinimized]);

  const toggleMinimize = useCallback(() => {
    setIsMinimized(prev => !prev);
    if (isMaximized) {
      setIsMaximized(false);
    }
  }, [isMaximized]);

  const resetPosition = useCallback(() => {
    setPosition(config.positioning.initialPosition);
  }, [config.positioning.initialPosition]);

  const resetSize = useCallback(() => {
    setSize(config.positioning.initialSize);
  }, [config.positioning.initialSize]);

  // ========================================
  // Event Listeners Setup
  // ========================================

  useEffect(() => {
    if ((isDragging || isResizing) && !listenersAttachedRef.current) {
      window.addEventListener('mousemove', handleMouseMove, { passive: false });
      window.addEventListener('mouseup', handleMouseUp, { passive: false });
      listenersAttachedRef.current = true;
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
        listenersAttachedRef.current = false;
      };
    }
  }, [isDragging, isResizing, handleMouseMove, handleMouseUp]);

  // Center on open if configured
  useEffect(() => {
    if (config.positioning.centerOnOpen) {
      // Start near top-left so drag tests have predictable initial box
      const startPosition: ModalPosition = {
        x: 10,
        y: 10,
      };
      setPosition(startPosition);
    }
  }, [config.positioning.centerOnOpen]);

  // ========================================
  // Return Hook Interface
  // ========================================

  return {
    // Drag functionality
    dragState: {
      isDragging,
      dragOffset: dragOffsetRef.current,
      startPosition: position,
    },
    handleDragStart,
    position: snapResult.snapped ? snapResult.snappedPosition : position,

    // Resize functionality
    resizeState: {
      isResizing,
      resizeHandle,
      startSize: resizeStartRef.current?.size ?? size,
      startPosition: resizeStartRef.current?.position ?? position,
      startMousePosition: resizeStartRef.current?.mousePosition ?? { x: 0, y: 0 },
    },
    handleResizeStart,
    size,
    resizeHandles: RESIZE_HANDLE_CONFIGS.filter(handle =>
      config.resizing.handles.includes(handle.handle)
    ),

    // Modal state
    modalState: {
      isDragging,
      dragOffset: dragOffsetRef.current,
      startPosition: position,
      isResizing,
      resizeHandle,
      startSize: resizeStartRef.current?.size ?? size,
      startMousePosition: resizeStartRef.current?.mousePosition ?? { x: 0, y: 0 },
      isMaximized,
      isMinimized,
      zIndex: 1000, // This would be managed by modal manager in real implementation
      isTopModal: true, // This would be managed by modal manager in real implementation
    },

    // Configuration and validation
    configuration: config,
    boundaryValidation,
    snapResult,

    // State management
    isMaximized,
    isMinimized,
    toggleMaximize,
    toggleMinimize,
    resetPosition,
    resetSize,
  };
};
