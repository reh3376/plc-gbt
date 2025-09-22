# PLC-GBT Main UI Layout Specification (VS Code–Style Interface)

This document provides a comprehensive specification for constructing the main UI page of the PLC-GBT application. The layout and functionality mirror the general structure of Visual Studio Code, with a top header, bottom footer, and a four-column content area (including collapsible side panels and a main editor region).

All decisions from prior discussions and clarifications have been merged here to ensure an implementation-ready guide. The design uses modern React libraries (like CSS Grid, flexbox, Zustand state, etc.) and common UI patterns (resizable panels, draggable icon lists, hover-reveal scrollbars) to achieve a VS Code–like experience.

## Overview of the VS Code–Style Layout

The application window is divided into a **4×3 CSS Grid**: four columns and three rows.

### Grid Structure

**Rows:**
- **Header Row** - Fixed header at the top (48px)
- **Main Row** - Stretchable middle content row (1fr)
- **Footer Row** - Fixed footer at the bottom (24px)

**Columns (in the middle row):**
1. **Column 1 – Left Sidebar**: Icon toolbar + primary sidebar content (Explorer, Search, etc.) - User-resizable horizontally
2. **Column 2 – Secondary Left Panel**: Reserved for future use or additional side panels
3. **Column 3 – Main Content**: Main editor/workspace area - Expands to fill remaining space
4. **Column 4 – Right Sidebar**: Slide-out panel for auxiliary tools (AI Assistant, inspectors) - Collapsed by default

### Dimensions

- **Header Height**: 48px (matches VS Code's TitleBar)
- **Footer Height**: 24px (matches VS Code's StatusBar)
- **Central Row**: 1fr height (stretches to fill remaining viewport)

## Global Grid Layout (HTML/CSS Structure)

The overall structure uses CSS Grid on a container spanning the full viewport:

```html
<div id="workspace"
     class="grid h-screen 
            grid-cols-[auto_auto_1fr_auto] 
            grid-rows-[48px_1fr_24px]">
  
  <!-- Row 1: Header -->
  <header id="header-row" class="col-span-4 row-start-1">
    <!-- Header content -->
  </header>

  <!-- Row 2: Main content area with four columns -->
  <aside id="left-column"     class="col-start-1 row-start-2 flex"></aside>
  <aside id="left-mid-column" class="col-start-2 row-start-2 flex"></aside>
  <main  id="main-column"     class="col-start-3 row-start-2 flex flex-col"></main>
  <aside id="right-column"    class="col-start-4 row-start-2 flex"></aside>

  <!-- Row 3: Footer -->
  <footer id="footer-row" class="col-span-4 row-start-3">
    <!-- Footer content -->
  </footer>
</div>
```

### Grid Template Explanation

**Columns**: `grid-cols-[auto_auto_1fr_auto]`
- Column 1 and Column 2: `auto` - Size to their content (with resizing constraints)
- Column 3: `1fr` - Takes remaining free space
- Column 4: `auto` - Size to content (when expanded)

**Rows**: `grid-rows-[48px_1fr_24px]`
- Header: Fixed 48px
- Main content: Flexible 1fr height
- Footer: Fixed 24px

The CSS Grid provides robust macro-layout with automatic RTL support when using logical properties.

## Column 1 – Left Sidebar (Icon Toolbar + Sidebar Content)

Column 1 combines VS Code's Activity Bar (icon rail) and Primary Sidebar into a single resizable panel with two sections:

### Section 1: Icon Rail (40px fixed width)
### Section 2: Tool Content (flexible width)

### Resizable Width Implementation

Using `react-resizable-panels` library for horizontal resizing:

```tsx
import { PanelGroup, Panel } from 'react-resizable-panels';

<PanelGroup direction="horizontal">
  {/* Column 1 as a resizable panel */}
  <Panel id="left-col" minSize={60} maxSize={650}>
    <div className="flex h-full">
      <IconStrip />   {/* Section 1: icon rail (40px fixed) */}
      <ToolPanel />   {/* Section 2: tool content (flexible) */}
    </div>
  </Panel>
  
  {/* Additional panels for Columns 2, 3 */}
  {/* Column 4 handled separately (toggleable) */}
</PanelGroup>
```

**Constraints:**
- **Minimum Width**: 60px (ensures icons aren't cut off)
- **Maximum Width**: 650px (prevents consuming too much workspace)
- **Resizing**: Drag handle between panels with smooth transitions
- **Persistence**: Width saved in Zustand store and localStorage

## Section 1 – Icon Strip (Vertical Tool Rail)

Vertical strip hosting icon buttons for quick navigation between tools.

### Specifications

**Dimensions:**
- **Width**: Fixed 40px (`w-10` in Tailwind)
- **Height**: 100% of Column 1
- **Icon Size**: 24-30px, centered in strip

**Default Icons:**
- 📁 File Explorer
- 🔍 Search  
- ⚙️ Workflows (custom PLC-GBT panel)
- ⚙️ Settings
- 👤 User Profile (always bottom-most, using `mt-auto`)

**Note**: AI Assistant icon removed from this section - accessible via right-side slide-out panel.

### Interactivity Features

**Active State Management:**
- Only one tool active at a time
- Highlighted background/border for active icon
- ARIA attributes: `role="tablist"`, `aria-selected="true/false"`

**Accessibility:**
- Keyboard navigation with Tab and Arrow keys
- Tooltip on hover showing tool name
- Screen reader friendly with proper ARIA roles

**Advanced Features (Future Phases):**

#### Dynamic Icon Management
- Right-click context menu for "Add Tool"
- Two-step selection process:
  1. **Icon Function**: Dropdown of available features/extensions
  2. **Icon Image**: Dropdown of icon choices
- Remove/hide icons via context menu

#### Drag-and-Drop Reordering
Using `react-beautiful-dnd` or `@dnd-kit`:

```tsx
<Droppable droppableId="icon-strip">
  {(provided) => (
    <div {...provided.droppableProps} ref={provided.innerRef}>
      {icons.map((icon, index) => (
        <Draggable key={icon.id} draggableId={icon.id} index={index}>
          {/* Icon component */}
        </Draggable>
      ))}
      {provided.placeholder}
    </div>
  )}
</Droppable>
```

#### Icon Scaling on Overflow
Auto-scale icons when count exceeds available space:

```css
.icon-btn img {
  width: clamp(10px, calc(30px - (var(--icon-count) - 10) * 1px), 30px);
  height: auto;
}
```

- **10+ icons**: Gradually shrink from 30px to 10px minimum
- **Variable**: `--icon-count` updated via JavaScript

#### Hover-Reveal Scrollbar
Smart scrolling behavior for overflow:

```css
/* Container */
.icon-strip {
  overflow-y: hidden;
  scrollbar-width: thin;
}

/* Hover region (5px wide) */
.icon-strip:hover {
  overflow-y: auto;
}

/* Custom scrollbar styling */
.icon-strip::-webkit-scrollbar {
  width: 5px;
  opacity: 0;
  transition: opacity 0.3s;
}

.icon-strip:hover::-webkit-scrollbar {
  opacity: 1;
}
```

**Behavior:**
- Hidden by default (`overflow-y: hidden`)
- 5px hover region on right edge
- Scrollbar appears on hover with fade transition
- 300ms visibility delay after hover ends

## Section 2 – Tool Panel (Sidebar Content Area)

Occupies remaining width of Column 1 after the 40px icon rail.

### Content Management

**Dynamic Rendering:**
- Shows content based on selected icon/tool
- **Explorer**: File Explorer tree
- **Search**: Search input and results  
- **Workflows**: Workflow list/management
- **Settings**: Settings UI or modal trigger

**Implementation Pattern:**
```tsx
const ToolPanel = () => {
  const { activeTool } = useLayoutStore();
  
  return (
    <div className="flex-1 h-full overflow-auto">
      {activeTool === 'explorer' && <FileExplorer />}
      {activeTool === 'search' && <SearchPanel />}
      {activeTool === 'workflows' && <WorkflowPanel />}
      {activeTool === 'settings' && <SettingsPanel />}
    </div>
  );
};
```

**Features:**
- **Responsive**: Adjusts to Column 1 width changes
- **Scrollable**: Internal scrolling for tall content
- **Lazy Loading**: Code-split large components
- **Default State**: Explorer active on load
- **State Management**: Global Zustand store for active tool

## Column 2 – Secondary Left Panel (Future Use)

Reserved placeholder for potential secondary sidebar functionality.

### Current Implementation
```tsx
<Panel id="left-mid-col" minSize={100} maxSize={800}>
  {/* Future content or empty for now */}
</Panel>
```

**Status**: 
- Currently unused/empty
- Maintains grid structure for future expansion
- Can be included in PanelGroup for consistent resizing
- May be collapsed or hidden in initial phases

## Column 3 – Main Content Area

Central panel occupying remaining space (`1fr` in grid).

### Primary Content Types
- **Code Editor**: Monaco editor with tab system
- **Workflow Canvas**: React Flow for visual workflows
- **Document Views**: Various content types
- **Split Panels**: Multiple editors side-by-side

### Layout Structure
```tsx
<main id="main-column" className="flex flex-col">
  {/* Tab bar for open editors */}
  <TabBar />
  
  {/* Main content area */}
  <div className="flex-1 overflow-hidden">
    <EditorGroup />
  </div>
  
  {/* Optional bottom panel for terminal/console */}
  <BottomPanel />
</main>
```

**Characteristics:**
- **Flexible Width**: Adjusts as sidebars resize
- **Minimum Width**: Preserved when sidebars hit max size
- **Complex Layout**: Internal grid/flex for sub-components
- **Responsive**: Adapts to available space

## Column 4 – Right Sidebar (Slide-Out Panel)

Special sidebar for AI Assistant and contextual tools.

### Behavior Specifications

**Visibility States:**
- **Hidden** (default): `width: 0`, `translateX(100%)`
- **Open**: Fixed width (~480px), slide-in transition

**Implementation:**
```tsx
<aside 
  id="right-column" 
  className={cn(
    "fixed right-0 top-0 h-full bg-sidebar border-l transition-transform duration-300",
    isRightPanelOpen ? "translate-x-0" : "translate-x-full"
  )}
  style={{ width: isRightPanelOpen ? '30rem' : '0' }}
>
  {/* AI Assistant UI */}
  <AssistantPanel />
</aside>
```

**Features:**
- **Toggle Control**: `layout.rightPanelOpen` boolean state
- **Fixed Width**: 480px when open (not user-resizable initially)
- **Smooth Transition**: CSS transforms for slide animation
- **Content**: AI Assistant, inspectors, context panels
- **Future**: May integrate into PanelGroup for drag-resizing

### Migration Strategy
- **Phase 1**: Implement slide-out structure (hidden by default)
- **Phase 2**: Migrate existing floating Assistant to this panel
- **Phase 3**: Remove floating panel, use only slide-out
- **Phase 4**: Add additional tools and features

## Header (Top Title Bar) and Footer (Status Bar)

### Header Specifications
- **Height**: Fixed 48px
- **Content**: App logo, workspace title, main menu
- **Styling**: VS Code-inspired title bar
- **Behavior**: Static, non-scrolling

### Footer Specifications  
- **Height**: Fixed 24px
- **Content**: Status messages, connection info, shortcuts
- **Styling**: VS Code-inspired status bar
- **Behavior**: Static, contextual indicators

```tsx
<header id="header-row" className="h-12 bg-titlebar border-b">
  <div className="flex items-center justify-between px-4 h-full">
    <div className="flex items-center space-x-2">
      <Logo />
      <span className="text-titlebar-foreground">PLC-GBT Industrial IDE</span>
    </div>
    <MainMenu />
  </div>
</header>

<footer id="footer-row" className="h-6 bg-statusbar border-t">
  <div className="flex items-center justify-between px-2 h-full text-xs">
    <StatusIndicators />
    <QuickActions />
  </div>
</footer>
```

## State Management and Persistence

### Zustand Store Structure
```tsx
interface LayoutState {
  // Active tool selection
  activeTool: 'explorer' | 'search' | 'workflows' | 'settings';
  
  // Panel dimensions
  leftColWidth: number;
  leftMidColWidth: number;
  rightPanelOpen: boolean;
  
  // UI preferences  
  headerVisible: boolean;
  footerVisible: boolean;
  
  // Icon customization
  iconOrder: string[];
  customIcons: IconConfig[];
}
```

### Persistence Strategy
```tsx
import { persist } from 'zustand/middleware';

export const useLayoutStore = create<LayoutStore>()(
  persist(
    (set, get) => ({
      // Store implementation
    }),
    {
      name: 'plc-gbt-layout',
      partialize: (state) => ({
        leftColWidth: state.leftColWidth,
        rightPanelOpen: state.rightPanelOpen,
        activeTool: state.activeTool,
        iconOrder: state.iconOrder,
      }),
    }
  )
);
```

**Persisted Data:**
- Panel widths and states
- Active tool selection  
- Icon order and customizations
- User preferences

**Session Data:**
- Temporary UI states
- Animation flags
- Loading states

## Accessibility and Internationalization

### Keyboard Navigation
```tsx
// Icon strip as tablist
<div role="tablist" onKeyDown={handleArrowNavigation}>
  {icons.map((icon) => (
    <button
      key={icon.id}
      role="tab"
      aria-selected={activeTool === icon.id}
      aria-controls={`panel-${icon.id}`}
      tabIndex={activeTool === icon.id ? 0 : -1}
    >
      <Icon name={icon.name} />
    </button>
  ))}
</div>
```

**Navigation Patterns:**
- **Tab**: Enter icon strip
- **Arrow Keys**: Move between icons (roving tabindex)
- **Enter/Space**: Activate tool
- **Escape**: Return to main content

### ARIA Implementation
```tsx
// Tool panel with proper labeling
<div
  id={`panel-${activeTool}`}
  role="tabpanel"
  aria-labelledby={`tab-${activeTool}`}
  className="flex-1 overflow-auto"
>
  {/* Panel content */}
</div>
```

### RTL Support
**CSS Grid RTL:**
```css
[dir="rtl"] .workspace-grid {
  grid-template-columns: auto 1fr auto auto; /* Flip column order */
}

/* Or use logical properties */
.sidebar {
  margin-inline-start: 0;
  border-inline-end: 1px solid var(--border-color);
}
```

**Dynamic Column Reordering:**
```tsx
const columnOrder = isRTL 
  ? ['right-column', 'main-column', 'left-mid-column', 'left-column']
  : ['left-column', 'left-mid-column', 'main-column', 'right-column'];
```

## Theme and Visual Design

### VS Code Color Scheme
```css
:root {
  /* Activity Bar */
  --activitybar-background: #333333;
  --activitybar-foreground: #ffffff;
  --activitybar-active-background: #094771;
  
  /* Sidebar */
  --sidebar-background: #252526;
  --sidebar-foreground: #cccccc;
  --sidebar-border: #3c3c3c;
  
  /* Title Bar */
  --titlebar-background: #3c3c3c;
  --titlebar-foreground: #cccccc;
  
  /* Status Bar */
  --statusbar-background: #007acc;
  --statusbar-foreground: #ffffff;
  
  /* Editor */
  --editor-background: #1e1e1e;
  --editor-foreground: #d4d4d4;
}
```

### Tailwind Configuration
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'activitybar': 'var(--activitybar-background)',
        'sidebar': 'var(--sidebar-background)',
        'titlebar': 'var(--titlebar-background)',
        'statusbar': 'var(--statusbar-background)',
        'editor': 'var(--editor-background)',
      },
      gridTemplateColumns: {
        'workspace': 'auto auto 1fr auto',
      },
      gridTemplateRows: {
        'workspace': '48px 1fr 24px',
      },
    },
  },
};
```

## Implementation Phases (Roadmap)

### Phase A – Base Layout and Resizing
**Objectives:**
- ✅ Set up CSS Grid structure (4×3 layout)
- ✅ Implement Column 1 with PanelGroup resizing
- ✅ Create static IconStrip with default icons
- ✅ Add placeholder ToolPanel
- ✅ Verify drag-resize functionality (60px-650px limits)
- ✅ Ensure header (48px) and footer (24px) are fixed

**Deliverables:**
- Working grid layout
- Resizable left sidebar
- Basic component structure

### Phase B – Core Interactivity and State
**Objectives:**
- 🔄 Implement Zustand state management
- 🔄 Make icon buttons switch ToolPanel content
- 🔄 Add User profile icon with mock avatar
- 🔄 Create toggleable right-column panel
- 🔄 Apply VS Code theme colors
- 🔄 Remove redundant old components

**Deliverables:**
- Functional tool switching
- Persistent layout preferences
- Styled VS Code-like interface

### Phase C – Advanced UX Enhancements
**Objectives:**
- ⏳ Add drag-and-drop icon reordering
- ⏳ Implement context menu for icon management
- ⏳ Create hover-reveal scrollbar
- ⏳ Add real avatar upload functionality
- ⏳ Integrate AI Assistant into right panel
- ⏳ Remove floating Assistant panel

**Deliverables:**
- Full customization capabilities
- Production-ready AI Assistant integration
- Polished user experience

## Component Architecture

### File Structure
```
src/
├── components/
│   ├── layout/
│   │   ├── WorkspaceGrid.tsx          # Main 4×3 grid container
│   │   ├── Header.tsx                 # Title bar (48px)
│   │   ├── Footer.tsx                 # Status bar (24px)
│   │   ├── LeftSidebar/
│   │   │   ├── index.tsx              # Column 1 container
│   │   │   ├── IconStrip.tsx          # Section 1: icon rail
│   │   │   ├── ToolPanel.tsx          # Section 2: content
│   │   │   └── tools/
│   │   │       ├── FileExplorer.tsx
│   │   │       ├── SearchPanel.tsx
│   │   │       ├── WorkflowPanel.tsx
│   │   │       └── SettingsPanel.tsx
│   │   ├── MainContent.tsx            # Column 3: editor area
│   │   └── RightSidebar.tsx           # Column 4: slide-out panel
│   └── ui/
│       ├── Icon.tsx                   # Reusable icon component
│       ├── Avatar.tsx                 # User profile avatar
│       └── ResizeHandle.tsx           # Custom resize handle
├── stores/
│   └── layoutStore.ts                 # Zustand layout state
└── styles/
    └── vscode-theme.css               # VS Code color variables
```

### Key Component Interfaces
```tsx
// Layout Store
interface LayoutStore {
  activeTool: ToolType;
  leftColWidth: number;
  rightPanelOpen: boolean;
  iconOrder: string[];
  
  setActiveTool: (tool: ToolType) => void;
  setLeftColWidth: (width: number) => void;
  toggleRightPanel: () => void;
  reorderIcons: (newOrder: string[]) => void;
}

// Icon Configuration
interface IconConfig {
  id: string;
  name: string;
  icon: React.ComponentType;
  component: React.ComponentType;
  tooltip: string;
  isCustom?: boolean;
}

// Tool Panel Props
interface ToolPanelProps {
  activeTool: ToolType;
  width: number;
  onToolChange: (tool: ToolType) => void;
}
```

## Performance Considerations

### Code Splitting
```tsx
// Lazy load tool components
const FileExplorer = lazy(() => import('./tools/FileExplorer'));
const SearchPanel = lazy(() => import('./tools/SearchPanel'));
const WorkflowPanel = lazy(() => import('./tools/WorkflowPanel'));

// Tool panel with suspense
<Suspense fallback={<ToolPanelSkeleton />}>
  {activeTool === 'explorer' && <FileExplorer />}
  {activeTool === 'search' && <SearchPanel />}
  {activeTool === 'workflows' && <WorkflowPanel />}
</Suspense>
```

### Render Optimization
```tsx
// Memoize expensive components
const IconStrip = memo(({ icons, activeTool, onToolChange }) => {
  return (
    <div className="icon-strip">
      {icons.map((icon) => (
        <IconButton 
          key={icon.id}
          icon={icon}
          isActive={activeTool === icon.id}
          onClick={() => onToolChange(icon.id)}
        />
      ))}
    </div>
  );
});

// Optimize resize handlers
const debouncedResize = useCallback(
  debounce((width: number) => {
    setLeftColWidth(width);
  }, 100),
  []
);
```

### Bundle Size Management
- **Tree Shaking**: Import only used components
- **Dynamic Imports**: Load tools on demand
- **Icon Optimization**: Use SVG icons with proper bundling
- **CSS Purging**: Remove unused Tailwind classes

## Testing Strategy

### Unit Tests
```tsx
// Icon strip functionality
describe('IconStrip', () => {
  it('should highlight active tool', () => {
    render(<IconStrip activeTool="explorer" />);
    expect(screen.getByRole('tab', { selected: true })).toHaveTextContent('Explorer');
  });
  
  it('should handle keyboard navigation', () => {
    render(<IconStrip />);
    const iconStrip = screen.getByRole('tablist');
    fireEvent.keyDown(iconStrip, { key: 'ArrowDown' });
    // Assert focus moved to next icon
  });
});
```

### Integration Tests
```tsx
// Layout resizing
describe('LayoutResizing', () => {
  it('should persist panel width', async () => {
    const { rerender } = render(<WorkspaceGrid />);
    
    // Resize panel
    fireEvent.dragEnd(screen.getByTestId('resize-handle'), { clientX: 300 });
    
    // Rerender component
    rerender(<WorkspaceGrid />);
    
    // Assert width is restored
    expect(screen.getByTestId('left-sidebar')).toHaveStyle('width: 300px');
  });
});
```

### E2E Tests
```typescript
// Playwright tests
test('should navigate between tools', async ({ page }) => {
  await page.goto('/');
  
  // Click search icon
  await page.click('[data-testid="tool-search"]');
  
  // Verify search panel is visible
  await expect(page.locator('[data-testid="search-panel"]')).toBeVisible();
  
  // Verify URL or state change
  await expect(page.locator('[aria-selected="true"]')).toHaveAttribute('data-tool', 'search');
});
```

## External Dependencies

### Required Libraries
```json
{
  "react-resizable-panels": "^2.0.0",
  "react-beautiful-dnd": "^13.1.1",
  "@dnd-kit/core": "^6.1.0",
  "zustand": "^4.4.0",
  "react-flow-renderer": "^11.10.0",
  "clsx": "^2.0.0",
  "tailwindcss": "^3.3.0"
}
```

### Optional Enhancements
```json
{
  "@mui/material": "^5.14.0",
  "react-hotkeys-hook": "^4.4.0",
  "framer-motion": "^10.16.0",
  "react-virtual": "^2.10.0"
}
```

## References and Citations

### Layout and Grid Systems
- [CSS Grid 4-column Layout Examples](https://stackoverflow.com/questions/49145552/how-is-grid-template-rows-auto-auto-1fr-auto-interpreted) - Understanding CSS Grid track sizing
- [VS Code Activity Bar Width Discussion](https://stackoverflow.com/questions/45048214/activity-bar-width-in-visual-studio-code) - User feedback on VS Code UI metrics

### React Panel Libraries  
- [React Resizable Panels Documentation](https://blog.logrocket.com/essential-tools-implementing-react-panel-layouts/) - Implementation guide for panel layouts
- [Essential Panel Layout Tools](https://blog.logrocket.com/essential-tools-implementing-react-panel-layouts/) - Comprehensive overview of React panel libraries

### Drag and Drop Implementation
- [React Beautiful DND GitHub](https://github.com/atlassian/react-beautiful-dnd) - Official documentation and examples
- [Accessible Drag and Drop Lists](https://github.com/atlassian/react-beautiful-dnd) - Accessibility best practices

### UI/UX Patterns
- [Scrollbars on Hover](https://css-tricks.com/scrollbars-on-hover/) - CSS techniques for hover-reveal scrollbars  
- [Hover Scrollbar Implementation](https://stackoverflow.com/questions/8631799/make-scrollbars-only-visible-when-a-div-is-hovered-over) - Stack Overflow solutions

### State Management
- [Zustand Persistence Guide](https://zustand.docs.pmnd.rs/integrations/persisting-store-data) - Official documentation for state persistence
- [React Flow State Management](https://reactflow.dev/learn/advanced-use/state-management) - Integration with Zustand

### Component Libraries
- [Material-UI Avatar Component](https://mui.com/material-ui/react-avatar/) - User profile avatar implementation
- [React Flow Documentation](https://www.vibestack.io/product/react-flow) - Workflow canvas integration

---

**Document Status**: ✅ Comprehensive specification ready for implementation  
**Last Updated**: January 17, 2025  
**Version**: 2.0 (Reformatted and Enhanced)