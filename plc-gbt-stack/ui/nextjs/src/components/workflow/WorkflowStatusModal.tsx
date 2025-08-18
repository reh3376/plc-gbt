'use client';

import { cn } from '@/lib/utils/cn';
import { AlertCircle, CheckCircle, Pause, Play, Square, X, XCircle } from 'lucide-react';
import React from 'react';
import { createPortal } from 'react-dom';

interface WorkflowStatusModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly operation: 'start' | 'pause' | 'stop';
  readonly status: 'success' | 'error' | 'info';
  readonly message: string;
  readonly errors?: string[];
  readonly workflowName?: string;
}

export function WorkflowStatusModal({
  isOpen,
  onClose,
  operation,
  status,
  message,
  errors = [],
  workflowName = 'Workflow',
}: Readonly<WorkflowStatusModalProps>): React.JSX.Element | null {
  if (!isOpen) return null;

  const getOperationIcon = () => {
    switch (operation) {
      case 'start':
        return Play;
      case 'pause':
        return Pause;
      case 'stop':
        return Square;
      default:
        return Play;
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return CheckCircle;
      case 'error':
        return XCircle;
      case 'info':
        return AlertCircle;
      default:
        return AlertCircle;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      case 'info':
        return 'text-blue-400';
      default:
        return 'text-blue-400';
    }
  };

  const getHeaderColor = () => {
    // Use operation-specific colors for better UX
    if (status === 'success') {
      switch (operation) {
        case 'start':
          return 'border-green-500/20 bg-green-500/10';
        case 'pause':
          return 'border-yellow-500/20 bg-yellow-500/10';
        case 'stop':
          return 'border-red-500/20 bg-red-500/10';
        default:
          return 'border-green-500/20 bg-green-500/10';
      }
    }

    // For error/info status, use status-based colors
    switch (status) {
      case 'error':
        return 'border-red-500/20 bg-red-500/10';
      case 'info':
        return 'border-blue-500/20 bg-blue-500/10';
      default:
        return 'border-blue-500/20 bg-blue-500/10';
    }
  };

  const OperationIcon = getOperationIcon();
  const StatusIcon = getStatusIcon();

  const operationLabels = {
    start: 'Start Workflow',
    pause: 'Pause Workflow',
    stop: 'Stop Workflow',
  };

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-[#2d2d2d] border border-[#404040] rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div
          className={cn(
            'flex items-center justify-between p-4 border-b border-[#404040]',
            getHeaderColor()
          )}
        >
          <div className="flex items-center space-x-2">
            <OperationIcon className={cn('w-5 h-5', getStatusColor())} />
            <h2 className="text-lg font-semibold text-white">{operationLabels[operation]}</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Status Message */}
          <div className="flex items-start space-x-3">
            <StatusIcon className={cn('w-6 h-6 mt-0.5', getStatusColor())} />
            <div className="flex-1">
              <div className="text-white font-medium mb-1">{workflowName}</div>
              <div className="text-gray-300 text-sm">{message}</div>
            </div>
          </div>

          {/* Errors (if any) */}
          {errors.length > 0 && (
            <div className="bg-red-500/10 border border-red-500/20 rounded p-3">
              <div className="text-red-400 font-medium text-sm mb-2">Errors Encountered:</div>
              <ul className="space-y-1">
                {errors.map((error, index) => (
                  <li key={index} className="text-red-300 text-xs flex items-start space-x-2">
                    <span className="text-red-400 mt-0.5">•</span>
                    <span>{error}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Operation Details */}
          <div className="text-xs text-gray-400 bg-[#1e1e1e] border border-[#404040] rounded p-2">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="font-medium">Operation:</span> {operation.toUpperCase()}
              </div>
              <div>
                <span className="font-medium">Status:</span> {status.toUpperCase()}
              </div>
              <div>
                <span className="font-medium">Workflow:</span> {workflowName}
              </div>
              <div>
                <span className="font-medium">Time:</span> {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-2 p-4 border-t border-[#404040]">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded transition-colors flex items-center space-x-2"
          >
            <X className="w-4 h-4" />
            <span>Close</span>
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
