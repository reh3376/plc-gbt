'use client';

import { cn } from '@/lib/utils/cn';
import { AlertTriangle, X } from 'lucide-react';

interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: 'danger' | 'warning' | 'info';
}

export function ConfirmDialog({
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  variant = 'warning',
}: ConfirmDialogProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
    if (e.key === 'Enter') {
      onConfirm();
    }
  };

  const variantStyles = {
    danger: 'text-red-400 bg-red-900/20',
    warning: 'text-yellow-400 bg-yellow-900/20',
    info: 'text-blue-400 bg-blue-900/20',
  };

  const buttonStyles = {
    danger: 'bg-red-600 hover:bg-red-700',
    warning: 'bg-yellow-600 hover:bg-yellow-700',
    info: 'bg-blue-600 hover:bg-blue-700',
  };

  return (
    <div className="absolute inset-0 bg-black/50 z-20 flex items-center justify-center">
      <div
        className="bg-[#252526] border border-[#3c3c3c] rounded-lg shadow-xl w-full max-w-md mx-4"
        onKeyDown={handleKeyDown}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#3c3c3c]">
          <h3 className="text-sm font-medium text-[#cccccc]">{title}</h3>
          <button
            onClick={onCancel}
            className="p-1 hover:bg-[#3c3c3c] rounded transition-colors"
            title="Close"
          >
            <X className="w-4 h-4 text-[#cccccc]" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          <div className={cn('flex items-start gap-3 p-3 rounded', variantStyles[variant])}>
            <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-[#cccccc]">{message}</p>
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-2 mt-4">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-sm bg-[#3c3c3c] hover:bg-[#505050] text-[#cccccc] rounded transition-colors"
            >
              {cancelText}
            </button>
            <button
              onClick={onConfirm}
              className={cn(
                'px-4 py-2 text-sm text-white rounded transition-colors',
                buttonStyles[variant]
              )}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
