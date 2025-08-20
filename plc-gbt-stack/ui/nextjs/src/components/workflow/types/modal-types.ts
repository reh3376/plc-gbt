/**
 * Enhanced Modal Types - AI Task Orchestrator TypeScript Implementation
 *
 * @description Type-safe interfaces for modal positioning, dragging, and resizing
 * @compliance Strict TypeScript with zero `any` types
 * @integration OpenAPI Schema MCP validation
 */

// ========================================
// Core Modal Types
// ========================================

export interface ModalPosition {
  readonly x: number;
  readonly y: number;
}

export interface ModalSize {
  readonly width: number;
  readonly height: number;
}

export interface ModalConstraints {
  readonly minWidth: number;
  readonly minHeight: number;
  readonly maxWidth: number;
  readonly maxHeight: number;
}

export interface ViewportBounds {
  readonly width: number;
  readonly height: number;
  readonly scrollX: number;
  readonly scrollY: number;
}

// ========================================
// Resize Handle Types
// ========================================

export type ResizeHandle =
  | 'n' // North (top)
  | 'ne' // North-East (top-right)
  | 'e' // East (right)
  | 'se' // South-East (bottom-right)
  | 's' // South (bottom)
  | 'sw' // South-West (bottom-left)
  | 'w' // West (left)
  | 'nw'; // North-West (top-left)

export interface ResizeHandleConfig {
  readonly handle: ResizeHandle;
  readonly cursor: string;
  readonly className: string;
  readonly position: {
    readonly top?: string;
    readonly right?: string;
    readonly bottom?: string;
    readonly left?: string;
  };
}

// ========================================
// Modal State Management
// ========================================

export interface ModalDragState {
  readonly isDragging: boolean;
  readonly dragOffset: ModalPosition;
  readonly startPosition: ModalPosition;
}

export interface ModalResizeState {
  readonly isResizing: boolean;
  readonly resizeHandle: ResizeHandle | null;
  readonly startSize: ModalSize;
  readonly startPosition: ModalPosition;
  readonly startMousePosition: ModalPosition;
}

export interface ModalInteractionState extends ModalDragState, ModalResizeState {
  readonly isMaximized: boolean;
  readonly isMinimized: boolean;
  readonly zIndex: number;
  readonly isTopModal: boolean;
}

// ========================================
// Event Handler Types
// ========================================

export interface DragStartEvent {
  readonly clientX: number;
  readonly clientY: number;
  readonly target: EventTarget | null;
  readonly currentTarget: EventTarget | null;
}

export interface ResizeStartEvent extends DragStartEvent {
  readonly handle: ResizeHandle;
}

export interface MouseMoveEvent {
  readonly clientX: number;
  readonly clientY: number;
  readonly movementX: number;
  readonly movementY: number;
}

// ========================================
// Boundary Calculation Types
// ========================================

export interface CalculatedBounds {
  readonly position: ModalPosition;
  readonly size: ModalSize;
  readonly isWithinViewport: boolean;
  readonly adjustedForConstraints: boolean;
}

export interface BoundaryValidationResult {
  readonly isValid: boolean;
  readonly adjustedPosition: ModalPosition;
  readonly adjustedSize: ModalSize;
  readonly violations: ReadonlyArray<BoundaryViolation>;
}

export interface BoundaryViolation {
  readonly type: 'position' | 'size' | 'viewport';
  readonly axis: 'x' | 'y' | 'width' | 'height';
  readonly originalValue: number;
  readonly adjustedValue: number;
  readonly constraint: string;
}

// ========================================
// Snap and Grid Types
// ========================================

export interface SnapConfiguration {
  readonly enabled: boolean;
  readonly threshold: number;
  readonly snapToEdges: boolean;
  readonly snapToCenter: boolean;
  readonly snapToGrid: boolean;
  readonly gridSize: number;
}

export interface SnapResult {
  readonly snapped: boolean;
  readonly snapType: 'edge' | 'center' | 'grid' | 'none';
  readonly originalPosition: ModalPosition;
  readonly snappedPosition: ModalPosition;
  readonly snapDistance: number;
}

// ========================================
// Modal Manager Integration
// ========================================

export interface ModalManagerState {
  readonly modalId: string;
  readonly modalType: string;
  readonly zIndex: number;
  readonly isTopModal: boolean;
  readonly bringToFront: () => void;
  readonly sendToBack: () => void;
}

// ========================================
// Persistence Types
// ========================================

export interface ModalPersistentState {
  readonly position: ModalPosition;
  readonly size: ModalSize;
  readonly isMaximized: boolean;
  readonly isMinimized: boolean;
  readonly activeTab: string;
  readonly expandedGroups: ReadonlyArray<string>;
  readonly lastUpdated: string;
}

export interface PersistenceConfiguration {
  readonly enabled: boolean;
  readonly storageKey: string;
  readonly expirationDays: number;
  readonly autoSave: boolean;
  readonly saveDebounceMs: number;
}

// ========================================
// Configuration and Props
// ========================================

export interface EnhancedModalConfiguration {
  readonly dragging: {
    readonly enabled: boolean;
    readonly constrainToViewport: boolean;
    readonly snapConfiguration: SnapConfiguration;
  };
  readonly resizing: {
    readonly enabled: boolean;
    readonly handles: ReadonlyArray<ResizeHandle>;
    readonly maintainAspectRatio: boolean;
    readonly constrainToViewport: boolean;
  };
  readonly positioning: {
    readonly initialPosition: ModalPosition;
    readonly initialSize: ModalSize;
    readonly constraints: ModalConstraints;
    readonly centerOnOpen: boolean;
  };
  readonly persistence: PersistenceConfiguration;
}

// ========================================
// Hook Return Types
// ========================================

export interface UseModalDragReturn {
  readonly dragState: ModalDragState;
  readonly handleDragStart: (event: React.MouseEvent<HTMLElement>) => void;
  readonly position: ModalPosition;
}

export interface UseModalResizeReturn {
  readonly resizeState: ModalResizeState;
  readonly handleResizeStart: (
    handle: ResizeHandle
  ) => (event: React.MouseEvent<HTMLElement>) => void;
  readonly size: ModalSize;
  readonly resizeHandles: ReadonlyArray<ResizeHandleConfig>;
}

export interface UseEnhancedModalReturn extends UseModalDragReturn, UseModalResizeReturn {
  readonly modalState: ModalInteractionState;
  readonly configuration: EnhancedModalConfiguration;
  readonly boundaryValidation: BoundaryValidationResult;
  readonly snapResult: SnapResult;
  readonly isMaximized: boolean;
  readonly isMinimized: boolean;
  readonly toggleMaximize: () => void;
  readonly toggleMinimize: () => void;
  readonly resetPosition: () => void;
  readonly resetSize: () => void;
}

// ========================================
// Utility Types
// ========================================

export type ModalEventType =
  | 'dragStart'
  | 'dragMove'
  | 'dragEnd'
  | 'resizeStart'
  | 'resizeMove'
  | 'resizeEnd'
  | 'maximize'
  | 'minimize'
  | 'restore'
  | 'close';

export interface ModalEvent<T = unknown> {
  readonly type: ModalEventType;
  readonly timestamp: number;
  readonly modalId: string;
  readonly data: T;
}

// ========================================
// Type Guards
// ========================================

export const isValidResizeHandle = (handle: unknown): handle is ResizeHandle => {
  return (
    typeof handle === 'string' && ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'].includes(handle)
  );
};

export const isModalPosition = (obj: unknown): obj is ModalPosition => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'x' in obj &&
    'y' in obj &&
    typeof (obj as Record<string, unknown>).x === 'number' &&
    typeof (obj as Record<string, unknown>).y === 'number'
  );
};

export const isModalSize = (obj: unknown): obj is ModalSize => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'width' in obj &&
    'height' in obj &&
    typeof (obj as Record<string, unknown>).width === 'number' &&
    typeof (obj as Record<string, unknown>).height === 'number'
  );
};

export const isMouseEvent = (event: unknown): event is MouseMoveEvent => {
  return (
    typeof event === 'object' &&
    event !== null &&
    'clientX' in event &&
    'clientY' in event &&
    typeof (event as Record<string, unknown>).clientX === 'number' &&
    typeof (event as Record<string, unknown>).clientY === 'number'
  );
};

// ========================================
// Constants
// ========================================

export const DEFAULT_MODAL_SIZE: ModalSize = {
  width: 800,
  height: 600,
} as const;

export const DEFAULT_MODAL_POSITION: ModalPosition = {
  x: 100,
  y: 100,
} as const;

export const DEFAULT_MODAL_CONSTRAINTS: ModalConstraints = {
  minWidth: 320,
  minHeight: 400,
  maxWidth: 1600,
  maxHeight: 1200,
} as const;

export const RESIZE_HANDLE_CONFIGS: ReadonlyArray<ResizeHandleConfig> = [
  {
    handle: 'n',
    cursor: 'n-resize',
    className: 'resize-handle-n',
    position: { top: '0px', left: '50%' },
  },
  {
    handle: 'ne',
    cursor: 'ne-resize',
    className: 'resize-handle-ne',
    position: { top: '0px', right: '0px' },
  },
  {
    handle: 'e',
    cursor: 'e-resize',
    className: 'resize-handle-e',
    position: { top: '50%', right: '0px' },
  },
  {
    handle: 'se',
    cursor: 'se-resize',
    className: 'resize-handle-se',
    position: { bottom: '0px', right: '0px' },
  },
  {
    handle: 's',
    cursor: 's-resize',
    className: 'resize-handle-s',
    position: { bottom: '0px', left: '50%' },
  },
  {
    handle: 'sw',
    cursor: 'sw-resize',
    className: 'resize-handle-sw',
    position: { bottom: '0px', left: '0px' },
  },
  {
    handle: 'w',
    cursor: 'w-resize',
    className: 'resize-handle-w',
    position: { top: '50%', left: '0px' },
  },
  {
    handle: 'nw',
    cursor: 'nw-resize',
    className: 'resize-handle-nw',
    position: { top: '0px', left: '0px' },
  },
] as const;

export const DEFAULT_SNAP_CONFIGURATION: SnapConfiguration = {
  enabled: true,
  threshold: 20,
  snapToEdges: true,
  snapToCenter: true,
  snapToGrid: false,
  gridSize: 20,
} as const;
