'use client';

import type { MainContentMode, ToolType } from '@/lib/stores/layout-store';
import { useLayoutStore } from '@/lib/stores/layout-store';
import { cn } from '@/lib/utils/cn';
import { Loader2 } from 'lucide-react';
import { Suspense, lazy, useEffect } from 'react';

// Lazy load tool components for performance
const EnhancedFileExplorer = lazy(() => import('../../file-explorer/EnhancedFileExplorer'));
const SearchPanel = lazy(() => import('../tools/SearchPanel'));
const WorkflowPanel = lazy(() => import('../tools/WorkflowPanel'));
const ControlLoopPanel = lazy(() => import('../tools/ControlLoopPanel'));
const SettingsPanel = lazy(() => import('../tools/SettingsPanel'));
const PLCGitPanelEnhanced = lazy(() => import('../tools/PLCGitPanelEnhanced'));

interface ToolPanelProps {
  className?: string;
}

function ToolPanelSkeleton() {
  return (
    <div className="flex items-center justify-center h-32">
      <Loader2 className="w-6 h-6 animate-spin text-[#007acc]" />
    </div>
  );
}

// Map tools to their corresponding MainContent modes
const getMainContentModeForTool = (tool: ToolType): MainContentMode => {
  switch (tool) {
    case 'explorer':
      return 'welcome'; // Will switch to 'editor' when a file is opened
    case 'search':
      return 'welcome'; // Could switch to 'editor' when search results are opened
    case 'analytics':
      return 'analytics';
    case 'workflows':
      return 'workflow';
    case 'control-loops':
      return 'control-loop';
    case 'settings':
      return 'settings-config';
    case 'plc-git':
      return 'plc-git';
    default:
      return 'welcome';
  }
};

export function ToolPanel({ className }: ToolPanelProps) {
  const { activeTool, setMainContentMode } = useLayoutStore();

  // Update MainContent mode when active tool changes
  useEffect(() => {
    const newMode = getMainContentModeForTool(activeTool);
    setMainContentMode(newMode);
  }, [activeTool, setMainContentMode]);

  const getTitle = () => {
    switch (activeTool) {
      case 'explorer':
        return 'Explorer';
      case 'search':
        return 'Search';
      case 'workflows':
        return 'Workflows';
      case 'control-loops':
        return 'Control Loops';
      case 'settings':
        return 'Settings';
      case 'plc-git':
        return 'PLC Git';
      default:
        return 'Explorer';
    }
  };

  const renderContent = () => {
    switch (activeTool) {
      case 'explorer':
        return <EnhancedFileExplorer />;
      case 'search':
        return <SearchPanel />;
      case 'workflows':
        return <WorkflowPanel />;
      case 'control-loops':
        return <ControlLoopPanel />;
      case 'settings':
        return <SettingsPanel />;
      case 'plc-git':
        return <PLCGitPanelEnhanced />;
      default:
        return <EnhancedFileExplorer />;
    }
  };

  return (
    <div
      id={`panel-${activeTool}`}
      role="tabpanel"
      aria-labelledby={`tab-${activeTool}`}
      className={cn('flex-1 flex flex-col w-full h-full overflow-hidden bg-[#252526]', className)}
    >
      {/* Panel Header */}
      <div className="h-8 bg-[#2d2d30] border-b border-[#3c3c3c] flex items-center px-3 flex-shrink-0">
        <span className="text-[#cccccc] text-sm font-medium uppercase tracking-wide">
          {getTitle()}
        </span>
      </div>

      {/* Panel Content */}
      <div className="flex-1 w-full overflow-hidden">
        <Suspense fallback={<ToolPanelSkeleton />}>{renderContent()}</Suspense>
      </div>
    </div>
  );
}

/**
 * ToolPanel Component
 *
 * @description Section 2 of Left Sidebar - Active tool content area
 * @specification Implements main-ui-spec.md Section 2 requirements
 *
 * @features
 * - Flexible width (takes remaining space after 40px icon strip)
 * - Dynamic content rendering based on active tool
 * - Lazy loading for performance optimization
 * - Proper header with tool title
 * - Responsive to panel resizing
 * - Loading states with skeleton UI
 *
 * @tools
 * - FileExplorer: File tree and project navigation
 * - SearchPanel: Search across files and content
 * - WorkflowPanel: Workflow management and automation
 * - SettingsPanel: Application settings and preferences
 *
 * @accessibility
 * - ARIA tabpanel pattern
 * - Proper labeling and relationships
 * - Keyboard navigation support
 * - Screen reader friendly content
 *
 * @performance
 * - Code splitting with lazy loading
 * - Suspense boundaries for smooth loading
 * - Optimized re-renders with proper state management
 */
