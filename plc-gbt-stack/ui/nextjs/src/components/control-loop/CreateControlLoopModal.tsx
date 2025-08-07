/**
 * Create Control Loop Modal Component - Phase 31.7
 * AI Task Orchestrator Generated - Placeholder Modal for Control Loop Creation
 *
 * Modal component for creating new control loops with form validation
 * This is a simplified placeholder - full implementation would include:
 * - Multi-step wizard for different loop types
 * - Comprehensive form validation
 * - Real-time parameter validation
 * - Template selection
 */

'use client';

import { Loader2, Move, Plus, X } from 'lucide-react';
import React, { useCallback, useEffect, useRef, useState } from 'react';

import { PLCGBTApiClient } from '@/lib/api/client';
import type { ControlLoopSummary, ControlLoopType } from '@/lib/types/control-loop.types';

interface CreateControlLoopModalProps {
  readonly onClose: () => void;
  readonly onCreated: (loop: ControlLoopSummary) => void;
}

/**
 * Placeholder Modal for Creating Control Loops
 *
 * Features to be implemented:
 * - Multi-step wizard
 * - Loop type selection
 * - Parameter configuration
 * - Validation and preview
 */
export function CreateControlLoopModal({ onClose, onCreated }: CreateControlLoopModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: 'ladder_logic_standard_pid' as ControlLoopType,
    description: '',
  });

  // Modal positioning and dragging state
  const [modalPosition, setModalPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [isPositioned, setIsPositioned] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);

  // Calculate optimal modal position to prevent edge obscuring
  const calculateOptimalPosition = useCallback(() => {
    if (!modalRef.current) return { x: 0, y: 0 };

    const modal = modalRef.current;
    const rect = modal.getBoundingClientRect();
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight,
    };

    // Calculate center position with padding from edges
    const padding = 20;
    let x = (viewport.width - rect.width) / 2;
    let y = (viewport.height - rect.height) / 2;

    // Ensure modal stays within viewport bounds
    x = Math.max(padding, Math.min(x, viewport.width - rect.width - padding));
    y = Math.max(padding, Math.min(y, viewport.height - rect.height - padding));

    return { x, y };
  }, []);

  // Initialize optimal positioning on mount
  useEffect(() => {
    if (!isPositioned) {
      const position = calculateOptimalPosition();
      setModalPosition(position);
      setIsPositioned(true);
    }
  }, [calculateOptimalPosition, isPositioned]);

  // Handle viewport resize to maintain optimal positioning
  useEffect(() => {
    const handleResize = () => {
      const position = calculateOptimalPosition();
      setModalPosition(position);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [calculateOptimalPosition]);

  // Handle drag start
  const handleDragStart = useCallback(
    (e: React.MouseEvent) => {
      if (!modalRef.current) return;

      setIsDragging(true);
      setDragStart({
        x: e.clientX - modalPosition.x,
        y: e.clientY - modalPosition.y,
      });
    },
    [modalPosition]
  );

  // Handle drag move
  const handleDragMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !modalRef.current) return;

      const modal = modalRef.current;
      const rect = modal.getBoundingClientRect();
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight,
      };

      const padding = 10;
      let newX = e.clientX - dragStart.x;
      let newY = e.clientY - dragStart.y;

      // Constrain to viewport with padding
      newX = Math.max(padding, Math.min(newX, viewport.width - rect.width - padding));
      newY = Math.max(padding, Math.min(newY, viewport.height - rect.height - padding));

      setModalPosition({ x: newX, y: newY });
    },
    [isDragging, dragStart]
  );

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Mouse event listeners for dragging
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleDragMove);
      document.addEventListener('mouseup', handleDragEnd);

      return () => {
        document.removeEventListener('mousemove', handleDragMove);
        document.removeEventListener('mouseup', handleDragEnd);
      };
    }
  }, [isDragging, handleDragMove, handleDragEnd]);

  // Keyboard event listener for Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Use API client to create control loop instance
      const apiClient = new PLCGBTApiClient();

      // Create the control loop instance using backend API
      const newInstance = await apiClient.createControlLoopInstance({
        schema_id: 'default_schema', // This would be selected from available schemas
        name: formData.name,
        parameters: {
          loop_type: formData.type,
          setpoint: 100.0,
          process_value: 98.5,
          control_output: 45.0,
          mode: 'Manual',
          performance_score: 75.0,
          alarms_active: 0,
        },
      });

      // Transform API response to UI format
      const newLoop: ControlLoopSummary = {
        id: newInstance.id,
        name: newInstance.name,
        type: formData.type,
        status: 'stopped', // New instances start stopped
        setpoint: 100.0,
        process_value: 98.5,
        control_output: 45.0,
        mode: 'Manual',
        performance_score: 75.0,
        alarms_active: 0,
        last_updated: new Date(newInstance.created_at),
      };

      onCreated(newLoop);
    } catch (error) {
      console.error('Failed to create control loop:', error);

      // Fallback to mock creation if API fails (offline mode)
      const mockLoop: ControlLoopSummary = {
        id: `loop_${Date.now()}`,
        name: formData.name,
        type: formData.type,
        status: 'stopped',
        setpoint: 100.0,
        process_value: 98.5,
        control_output: 45.0,
        mode: 'Manual',
        performance_score: 75.0,
        alarms_active: 0,
        last_updated: new Date(),
      };

      onCreated(mockLoop);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50">
      <div
        ref={modalRef}
        className={`absolute bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg shadow-xl w-full max-w-md transition-shadow duration-200 ${
          isDragging ? 'shadow-2xl scale-[1.02]' : 'shadow-xl'
        }`}
        style={{
          left: `${modalPosition.x}px`,
          top: `${modalPosition.y}px`,
          width: 'min(28rem, calc(100vw - 2rem))',
          maxHeight: 'calc(100vh - 2rem)',
          overflow: 'auto',
        }}
      >
        {/* Draggable Header */}
        <div
          className={`flex items-center justify-between p-4 border-b border-[#3c3c3c] cursor-move select-none ${
            isDragging ? 'bg-[#3c3c3c]' : 'hover:bg-[#333333]'
          } transition-colors`}
          onMouseDown={handleDragStart}
        >
          <div className="flex items-center space-x-2">
            <Move className="w-4 h-4 text-gray-400" />
            <h2 className="text-lg font-semibold text-white">Create Control Loop</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors z-10"
            onMouseDown={e => e.stopPropagation()} // Prevent drag when clicking close
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Loop Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 bg-[#1e1e1e] border border-[#3c3c3c] rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter loop name..."
            />
          </div>

          {/* Type */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Loop Type</label>
            <select
              value={formData.type}
              onChange={e =>
                setFormData(prev => ({ ...prev, type: e.target.value as ControlLoopType }))
              }
              className="w-full px-3 py-2 bg-[#1e1e1e] border border-[#3c3c3c] rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="ladder_logic_standard_pid">Ladder Logic Standard PID</option>
              <option value="ladder_logic_advanced_pid">Ladder Logic Advanced PID</option>
              <option value="function_block_standard_pide">Function Block Standard PIDE</option>
              <option value="function_block_advanced_pide">Function Block Advanced PIDE</option>
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Description (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full px-3 py-2 bg-[#1e1e1e] border border-[#3c3c3c] rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
              placeholder="Optional description..."
            />
          </div>

          {/* Notice */}
          <div className="bg-blue-900/20 border border-blue-500 rounded-md p-3">
            <p className="text-sm text-blue-300">
              <strong>Note:</strong> This is a simplified creation form. The full implementation
              will include comprehensive parameter configuration, validation, and a multi-step
              wizard.
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !formData.name.trim()}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-md transition-colors"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Creating...</span>
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Create Loop</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateControlLoopModal;
