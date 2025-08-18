'use client';

import { cn } from '@/lib/utils/cn';
import { HelpCircle } from 'lucide-react';
import { useState } from 'react';
import { WorkflowHelpModal } from '../workflow/WorkflowHelpModal';

interface HeaderProps {
  readonly className?: string;
}

export function Header({ className }: Readonly<HeaderProps>) {
  const [showHelpModal, setShowHelpModal] = useState(false);
  return (
    <header
      id="header-row"
      className={cn(
        'h-12 bg-[#3c3c3c] border-b border-[#3c3c3c]',
        'flex items-center justify-between px-4 select-none',
        'text-[#cccccc]',
        className
      )}
    >
      {/* Left side - Application title */}
      <div className="flex items-center space-x-2">
        <div className="relative w-7 h-5">
          {/* Background element for logo visibility - wider to show full logo */}
          <div className="absolute inset-0 bg-white/10 rounded-sm border border-white/20" />
          {/* Logo with higher z-index */}
          <img
            src="/whk-logo.png"
            alt="PLC-GBT Logo"
            className="relative w-7 h-5 object-contain z-10"
          />
        </div>
        <span className="text-sm font-medium">PLC-GBT Industrial Automation IDE</span>
      </div>

      {/* Center - Workspace title */}
      <div className="flex-1 text-center">
        <span className="text-[#969696] text-sm">Industrial Control Workspace</span>
      </div>

      {/* Right side - Help toolbar */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setShowHelpModal(true)}
          className="p-2 text-blue-400 hover:text-blue-300 hover:bg-[#505050] rounded transition-colors"
          title="PLC-GBT Help & Support"
        >
          <HelpCircle className="w-4 h-4" />
        </button>
      </div>

      {/* Help Modal */}
      <WorkflowHelpModal isOpen={showHelpModal} onClose={() => setShowHelpModal(false)} />
    </header>
  );
}

/**
 * Header Component
 *
 * @description Fixed 48px height title bar spanning full width
 * @specification Matches VS Code title bar design from main-ui-spec.md
 *
 * @features
 * - Fixed 48px height (h-12 = 3rem = 48px)
 * - App logo and title on left
 * - Workspace context in center
 * - Quick actions on right
 * - VS Code inspired styling
 *
 * @accessibility
 * - Semantic header element
 * - Keyboard focusable buttons
 * - ARIA labels for interactive elements
 */
