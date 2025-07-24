'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'
import { useLayoutStore, type ToolType, type IconConfig } from '@/lib/stores/layout-store'
import { 
  Folder,
  Search,
  PlayCircle,
  Settings,
  User,
  GripVertical,
  Activity
} from 'lucide-react'

// NEW: @dnd-kit imports for Phase 33.8
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
  defaultDropAnimationSideEffects,
  DropAnimation,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

// Icon mapping for dynamic rendering
const ICON_MAP = {
  explorer: Folder,
  search: Search,
  workflows: PlayCircle,
  'control-loops': Activity,
  settings: Settings,
  user: User,
}

const DEFAULT_ICONS: IconConfig[] = [
  {
    id: 'explorer',
    name: 'Explorer',
    icon: 'explorer',
    tooltip: 'File Explorer'
  },
  {
    id: 'search',
    name: 'Search',
    icon: 'search',
    tooltip: 'Search across files'
  },
  {
    id: 'workflows',
    name: 'Workflows',
    icon: 'workflows',
    tooltip: 'Workflow management'
  },
  {
    id: 'control-loops',
    name: 'Control Loops',
    icon: 'control-loops',
    tooltip: 'Industrial control loop management'
  },
  {
    id: 'settings',
    name: 'Settings',
    icon: 'settings',
    tooltip: 'Settings and preferences'
  }
]

const USER_ICON: IconConfig = {
  id: 'user',
  name: 'User',
  icon: 'user',
  tooltip: 'User profile and authentication'
}

// NEW: Sortable Icon Item Component for Phase 33.8
interface SortableIconItemProps {
  icon: IconConfig
  isActive: boolean
  onIconClick: (iconId: string) => void
  hoveredIcon: string | null
  setHoveredIcon: (iconId: string | null) => void
  isDragging?: boolean
}

function SortableIconItem({ 
  icon, 
  isActive, 
  onIconClick, 
  hoveredIcon, 
  setHoveredIcon, 
  isDragging = false 
}: SortableIconItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ 
    id: icon.id,
    data: {
      type: 'icon',
      icon: icon
    }
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const IconComponent = ICON_MAP[icon.icon as keyof typeof ICON_MAP] || User

  // Combine @dnd-kit attributes with our ARIA attributes
  const combinedAttributes = {
    ...attributes,
    // Ensure our ARIA attributes override @dnd-kit ones
    role: "tab",
    tabIndex: 0,
    "aria-selected": isActive,
    "aria-label": `${icon.tooltip}${isActive ? ' (active)' : ''}${isSortableDragging ? ' (being dragged)' : ''}`,
    "aria-describedby": `${icon.id}-instructions`,
    "aria-grabbed": isSortableDragging,
    "data-testid": `icon-${icon.id}` // For testing
  }

  return (
    <>
      {/* Hidden instructions for screen readers */}
      <div id={`${icon.id}-instructions`} className="sr-only">
        {icon.name} tool. Press Enter to activate. Press Space then arrow keys to reorder.
      </div>
      
      <div
        ref={setNodeRef}
        style={style}
        className={cn(
          "group relative w-8 h-8 rounded-sm flex items-center justify-center",
          "icon-strip-item transition-all duration-300 ease-in-out cursor-pointer",
          "hover:bg-[#2d2d30] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#333333]",
          isActive && "bg-[#094771] text-white",
          isSortableDragging && "dragging z-50 shadow-xl ring-2 ring-blue-400/75 scale-110",
          isDragging && "opacity-50"
        )}
        onMouseEnter={() => setHoveredIcon(icon.id)}
        onMouseLeave={() => setHoveredIcon(null)}
        onClick={() => onIconClick(icon.id)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onIconClick(icon.id)
          }
        }}
        {...combinedAttributes}
        {...listeners} // Apply drag listeners to entire icon for better UX
      >
        {/* Main Icon */}
        <IconComponent 
          className={cn(
            "w-5 h-5 transition-all duration-200",
            isActive ? "text-white" : "text-[#cccccc] group-hover:text-white"
          )}
          aria-hidden="true"
        />
        
        {/* Enhanced Drag Handle - Larger and Always Visible on Hover */}
        <div
          className={cn(
            "absolute -right-1 top-0 h-full w-3 flex items-center justify-center",
            "drag-handle opacity-0 group-hover:opacity-100 transition-all duration-300",
            "bg-[#094771]/80 backdrop-blur-sm rounded-r-sm",
            "hover:bg-[#094771] hover:w-4", // Expand on hover for easier grabbing
            isSortableDragging && "opacity-100 bg-[#094771]"
          )}
          aria-label={`Drag to reorder ${icon.name}`}
          role="button"
          aria-describedby={`${icon.id}-drag-instructions`}
        >
          <GripVertical 
            className="w-3 h-3 text-white/90" 
            aria-hidden="true"
          />
        </div>

        {/* Hidden drag instructions */}
        <div id={`${icon.id}-drag-instructions`} className="sr-only">
          Drag handle for {icon.name}. Use mouse or keyboard to reorder this tool.
        </div>

        {/* Tooltip */}
        {hoveredIcon === icon.id && !isSortableDragging && (
          <div 
            className="drag-tooltip left-10 top-1/2 -translate-y-1/2"
            role="tooltip"
            aria-hidden="true"
          >
            {icon.tooltip}
            <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-900 rotate-45"></div>
          </div>
        )}

        {/* Active Indicator */}
        {isActive && (
          <div 
            className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-white rounded-r-sm"
            aria-hidden="true"
          ></div>
        )}
      </div>
    </>
  )
}

// NEW: Enhanced Drag Overlay Component with better visual feedback
function DragOverlayContent({ icon }: { icon: IconConfig | null }) {
  if (!icon) return null
  
  // Convert string icon name to React component
  const IconComponent = ICON_MAP[icon.icon as keyof typeof ICON_MAP] || User
  
  return (
    <div className="drag-overlay w-8 h-8 flex items-center justify-center rounded bg-[#094771] text-white">
      <IconComponent className="w-5 h-5" />
    </div>
  )
}

export function IconStrip() {
  const { activeTool, setActiveTool, iconOrder, reorderIcons, customIcons } = useLayoutStore()
  const [hoveredIcon, setHoveredIcon] = useState<string | null>(null)
  const [activeId, setActiveId] = useState<string | null>(null)
  // NEW: ARIA live region for screen reader announcements
  const [announcement, setAnnouncement] = useState<string>('')

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement required for better touch support
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // Create ordered list of main icons based on iconOrder
  const orderedIcons = iconOrder
    .map(iconId => DEFAULT_ICONS.find(icon => icon.id === iconId))
    .filter(Boolean) as IconConfig[]
  
  // Combine ordered icons with custom icons (excluding bottom positioned ones)
  const allMainIcons = [
    ...orderedIcons,
    ...customIcons.filter(icon => icon.position !== 'bottom')
  ]

  const handleIconClick = (iconId: string) => {
    setActiveTool(iconId as ToolType)
    // Announce tool change to screen readers
    const icon = [...DEFAULT_ICONS, ...customIcons].find(i => i.id === iconId)
    setAnnouncement(`${icon?.name || iconId} tool activated`)
  }

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string)
    setHoveredIcon(null)
    
    // Announce drag start to screen readers
    const draggedIcon = [...DEFAULT_ICONS, ...customIcons].find(i => i.id === event.active.id)
    setAnnouncement(`Started dragging ${draggedIcon?.name || event.active.id}`)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    
    if (active.id !== over?.id) {
      const oldIndex = iconOrder.indexOf(active.id as string)
      const newIndex = iconOrder.indexOf(over?.id as string)
      
      if (oldIndex !== -1 && newIndex !== -1) {
        reorderIcons(oldIndex, newIndex)
        
        // Announce successful reorder to screen readers
        const draggedIcon = DEFAULT_ICONS.find(i => i.id === active.id)
        const targetIcon = DEFAULT_ICONS.find(i => i.id === over?.id)
        setAnnouncement(`${draggedIcon?.name} moved ${oldIndex < newIndex ? 'down' : 'up'} in toolbar, now positioned ${newIndex < oldIndex ? 'before' : 'after'} ${targetIcon?.name}`)
      }
    } else {
      // Announce cancelled drag
      const draggedIcon = DEFAULT_ICONS.find(i => i.id === active.id)
      setAnnouncement(`Drag cancelled for ${draggedIcon?.name}`)
    }
    
    setActiveId(null)
  }

  // Find the currently dragged icon for overlay
  const draggedIcon = activeId 
    ? [...DEFAULT_ICONS, ...customIcons].find(icon => icon.id === activeId) || null
    : null

  // Enhanced drop animation configuration for better UX
  const dropAnimation: DropAnimation = {
    sideEffects: defaultDropAnimationSideEffects({
      styles: {
        active: {
          opacity: '0.8',
        },
      },
    }),
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      {/* ARIA live region for announcements */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        role="status"
      >
        {announcement}
      </div>

      <div 
        className="w-10 bg-[#333333] flex flex-col items-center py-2 border-r border-[#3c3c3c] relative" 
        role="tablist" 
        aria-label="Tool navigation"
        aria-describedby="icon-strip-instructions"
      >
        {/* Screen reader instructions */}
        <div id="icon-strip-instructions" className="sr-only">
          Use arrow keys to navigate between tools. Press Enter to activate a tool. 
          Use Space and arrow keys to reorder tools when drag mode is active.
        </div>

        <SortableContext items={iconOrder} strategy={verticalListSortingStrategy}>
          <div className="flex flex-col space-y-1" role="group" aria-label="Main tools">
            {allMainIcons.map((icon) => (
              <SortableIconItem
                key={icon.id}
                icon={icon}
                isActive={activeTool === icon.id}
                onIconClick={handleIconClick}
                hoveredIcon={hoveredIcon}
                setHoveredIcon={setHoveredIcon}
                isDragging={activeId === icon.id}
              />
            ))}
          </div>
        </SortableContext>

        {/* Spacer */}
        <div className="flex-1" />

        {/* User icon section */}
        <div className="mt-auto" role="group" aria-label="User tools">
          <SortableIconItem
            icon={USER_ICON}
            isActive={false} // User icon doesn't have active state currently
            onIconClick={handleIconClick}
            hoveredIcon={hoveredIcon}
            setHoveredIcon={setHoveredIcon}
          />
        </div>
      </div>

      {/* Enhanced Drag Overlay with better accessibility */}
      <DragOverlay dropAnimation={dropAnimation}>
        <DragOverlayContent icon={draggedIcon} />
      </DragOverlay>
    </DndContext>
  )
}

/**
 * IconStrip Component
 * 
 * @description Section 1 of Left Sidebar - Vertical icon rail for tool navigation
 * @specification Implements main-ui-spec.md Section 1 requirements
 * 
 * @features
 * - Fixed 40px width (w-10 = 2.5rem = 40px)
 * - Vertical icon layout with proper spacing
 * - Active state management with visual indicators
 * - Hover tooltips for accessibility
 * - User icon pinned to bottom
 * - VS Code Activity Bar styling
 * 
 * @icons
 * - File Explorer, Search, Workflows, Settings (main tools)
 * - User Profile (bottom-pinned for login/logout)
 * - AI Assistant removed (accessible via right slide-out)
 * 
 * @accessibility
 * - ARIA tablist pattern
 * - Keyboard navigation support
 * - Screen reader friendly
 * - Focus indicators
 * 
 * @future Phase C will add:
 * - Drag and drop reordering
 * - Custom icon management
 * - Context menu for icon operations
 * - Auto-scaling for overflow
 * - Hover-reveal scrollbar
 */ 