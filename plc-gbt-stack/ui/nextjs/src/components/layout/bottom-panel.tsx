'use client';

import { Terminal } from '@/components/terminal/Terminal';
import { useLayoutStore } from '@/lib/stores/layout-store';
import { cn } from '@/lib/utils/cn';
import { Minus, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface BottomPanelProps {
  isOpen: boolean;
  height?: number;
}

interface PanelTab {
  id: string;
  title: string;
  content: React.ComponentType;
}

// Terminal component
const TerminalView = () => <Terminal />;

const OutputView = () => (
  <div className="flex-1 bg-[#1e1e1e] p-4 text-sm text-[#cccccc]">
    <div className="text-[#569cd6] mb-2">[Info] PLC-GBT UI Started</div>
    <div className="text-[#4ec9b0] mb-2">[Success] Connected to backend services</div>
    <div className="text-[#dcdcaa] mb-2">[Log] Ready for industrial automation tasks</div>
  </div>
);

const ProblemsView = () => (
  <div className="flex-1 bg-[#1e1e1e] p-4 text-sm text-[#cccccc]">
    <div className="text-[#569cd6]">No problems detected</div>
    <div className="text-[#6a9955] mt-2">All systems operational</div>
  </div>
);

const PANEL_TABS: PanelTab[] = [
  { id: 'terminal', title: 'Terminal', content: TerminalView },
  { id: 'output', title: 'Output', content: OutputView },
  { id: 'problems', title: 'Problems', content: ProblemsView },
];

export function BottomPanel({ isOpen, height = 200 }: BottomPanelProps) {
  const [activeTab, setActiveTab] = useState('terminal');
  const { toggleBottomPanel, bottomPanel, setBottomPanelHeight } = useLayoutStore();
  const [isResizing, setIsResizing] = useState(false);
  const [currentHeight, setCurrentHeight] = useState(height);
  const panelRef = useRef<HTMLDivElement>(null);

  // Sync local height with prop height
  useEffect(() => {
    setCurrentHeight(height);
  }, [height]);

  // When the panel opens, default to the terminal tab
  useEffect(() => {
    if (isOpen && bottomPanel.isOpen) {
      setActiveTab('terminal');
    }
  }, [isOpen, bottomPanel.isOpen]);

  // Handle resize drag
  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!panelRef.current) return;

      // Calculate new height based on mouse position from bottom of viewport
      const viewportHeight = window.innerHeight;
      const newHeight = viewportHeight - e.clientY;

      // Constrain height between 100px and 600px
      const constrainedHeight = Math.max(100, Math.min(600, newHeight));
      setCurrentHeight(constrainedHeight);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      // Save the final height to the store
      setBottomPanelHeight(currentHeight);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, currentHeight, setBottomPanelHeight]);

  if (!isOpen) {
    return null;
  }

  const ActiveComponent = PANEL_TABS.find(tab => tab.id === activeTab)?.content || TerminalView;

  return (
    <div
      ref={panelRef}
      className="bg-[#1e1e1e] border-t border-[#3c3c3c] flex flex-col"
      style={{ height: currentHeight }}
    >
      {/* Resize Handle */}
      <button
        type="button"
        aria-label="Resize panel (drag or use arrow keys)"
        onMouseDown={() => setIsResizing(true)}
        onKeyDown={e => {
          if (e.key === 'ArrowUp') {
            e.preventDefault();
            const newHeight = Math.min(600, currentHeight + 20);
            setCurrentHeight(newHeight);
            setBottomPanelHeight(newHeight);
          } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            const newHeight = Math.max(100, currentHeight - 20);
            setCurrentHeight(newHeight);
            setBottomPanelHeight(newHeight);
          }
        }}
        className={cn(
          'h-1 w-full cursor-ns-resize hover:bg-[#007acc] transition-colors focus:bg-[#007acc] focus:outline-none border-0 p-0',
          isResizing && 'bg-[#007acc]'
        )}
        title="Drag to resize (or use arrow keys)"
      />

      {/* Tab Bar */}
      <div className="h-8 bg-[#2d2d30] border-b border-[#3c3c3c] flex items-center justify-between">
        <div className="flex">
          {PANEL_TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'px-3 py-1 text-sm transition-colors',
                activeTab === tab.id
                  ? 'text-white bg-[#1e1e1e] border-t-2 border-blue-500'
                  : 'text-[#cccccc] hover:text-white hover:bg-[#3c3c3c]'
              )}
            >
              {tab.title}
            </button>
          ))}
        </div>

        {/* Panel Controls */}
        <div className="flex items-center">
          <button
            onClick={toggleBottomPanel}
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] transition-colors"
            title="Minimize Panel"
          >
            <Minus className="w-4 h-4 text-[#cccccc]" />
          </button>
          <button
            onClick={toggleBottomPanel}
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] transition-colors"
            title="Close Panel"
          >
            <X className="w-4 h-4 text-[#cccccc]" />
          </button>
        </div>
      </div>

      {/* Panel Content - Allow scrolling */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden">
        <ActiveComponent />
      </div>
    </div>
  );
}
