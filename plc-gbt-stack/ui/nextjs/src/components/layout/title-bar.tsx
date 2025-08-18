'use client';

import { HelpCircle, Minimize2, Square, X } from 'lucide-react';
import { useState } from 'react';
import { WorkflowHelpModal } from '../workflow/WorkflowHelpModal';

export function TitleBar() {
  const [showHelpModal, setShowHelpModal] = useState(false);
  return (
    <div className="h-8 bg-[#3c3c3c] flex items-center justify-between px-4 select-none border-b border-[#3c3c3c]">
      {/* Left side - Application title */}
      <div className="flex items-center space-x-2">
        <div className="relative w-6 h-4">
          {/* Background element for logo visibility - wider to show full logo */}
          <div className="absolute inset-0 bg-white/10 rounded-sm border border-white/20" />
          {/* Logo with higher z-index */}
          <img
            src="/whk-logo.png"
            alt="PLC-GBT Logo"
            className="relative w-6 h-4 object-contain z-10"
          />
        </div>
        <span className="text-[#cccccc] text-sm font-medium">
          PLC-GBT Industrial Automation IDE
        </span>
      </div>

      {/* Center - File path or project name (when available) */}
      <div className="flex-1 text-center">
        <span className="text-[#969696] text-sm">Welcome to PLC-GBT</span>
      </div>

      {/* Right side - Help and Window controls */}
      <div className="flex items-center">
        {/* Help Button */}
        <button
          onClick={() => setShowHelpModal(true)}
          className="w-8 h-8 flex items-center justify-center hover:bg-[#505050] transition-colors mr-2"
          title="PLC-GBT Help & Support"
        >
          <HelpCircle className="w-4 h-4 text-blue-400" />
        </button>

        {/* Window Controls */}
        <button
          className="w-8 h-8 flex items-center justify-center hover:bg-[#505050] transition-colors"
          title="Minimize"
        >
          <Minimize2 className="w-4 h-4 text-[#cccccc]" />
        </button>
        <button
          className="w-8 h-8 flex items-center justify-center hover:bg-[#505050] transition-colors"
          title="Maximize"
        >
          <Square className="w-4 h-4 text-[#cccccc]" />
        </button>
        <button
          className="w-8 h-8 flex items-center justify-center hover:bg-red-600 transition-colors"
          title="Close"
        >
          <X className="w-4 h-4 text-[#cccccc]" />
        </button>
      </div>

      {/* Help Modal */}
      <WorkflowHelpModal isOpen={showHelpModal} onClose={() => setShowHelpModal(false)} />
    </div>
  );
}
