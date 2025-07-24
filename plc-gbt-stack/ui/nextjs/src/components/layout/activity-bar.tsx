'use client'

import { 
  Search, 
  MessageSquare, 
  Settings,
  Folder,
  PlayCircle,
  BarChart3
} from 'lucide-react'
import { useLayoutStore } from '@/lib/stores/layout-store'
import { cn } from '@/lib/utils/cn'

interface ActivityBarItem {
  id: string
  icon: React.ComponentType<{ className?: string }>
  title: string
  view: 'explorer' | 'search' | 'workflows' | 'chat' | 'settings'
}

const ACTIVITY_BAR_ITEMS: ActivityBarItem[] = [
  {
    id: 'explorer',
    icon: Folder,
    title: 'Explorer',
    view: 'explorer',
  },
  {
    id: 'search',
    icon: Search,
    title: 'Search',
    view: 'search',
  },
  {
    id: 'workflows',
    icon: PlayCircle,
    title: 'Workflows',
    view: 'workflows',
  },
  {
    id: 'chat',
    icon: MessageSquare,
    title: 'AI Assistant',
    view: 'chat',
  },
  {
    id: 'settings',
    icon: Settings,
    title: 'Settings',
    view: 'settings',
  },
]

export function ActivityBar() {
  const { activityBar, setActivityBarView, setSidebarOpen } = useLayoutStore()

  const handleItemClick = (view: ActivityBarItem['view']) => {
    if (activityBar.activeView === view) {
      // Toggle sidebar if clicking the same item
      setSidebarOpen(false)
    } else {
      // Change view and ensure sidebar is open
      setActivityBarView(view)
      setSidebarOpen(true)
    }
  }

  return (
    <div className="w-12 bg-[#333333] flex flex-col items-center py-2 border-r border-[#3c3c3c]">
      {/* Top items */}
      <div className="flex flex-col space-y-1">
        {ACTIVITY_BAR_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive = activityBar.activeView === item.view
          
          return (
            <button
              key={item.id}
              onClick={() => handleItemClick(item.view)}
              className={cn(
                "w-10 h-10 flex items-center justify-center rounded transition-colors group relative",
                isActive 
                  ? "text-white bg-[#094771]" 
                  : "text-[#cccccc] hover:text-white hover:bg-[#3c3c3c]"
              )}
              title={item.title}
            >
              <Icon className="w-6 h-6" />
              
              {/* Active indicator */}
              {isActive && (
                <div className="absolute -left-[1px] top-0 bottom-0 w-[2px] bg-white rounded-r" />
              )}
              
              {/* Tooltip */}
              <div className="absolute left-12 px-2 py-1 bg-[#2d2d30] text-white text-sm rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity delay-500 whitespace-nowrap z-50">
                {item.title}
              </div>
            </button>
          )
        })}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Bottom items - Additional controls */}
      <div className="flex flex-col space-y-1">
        <button
          className="w-10 h-10 flex items-center justify-center rounded transition-colors text-[#cccccc] hover:text-white hover:bg-[#3c3c3c] group relative"
          title="Analytics"
        >
          <BarChart3 className="w-6 h-6" />
          <div className="absolute left-12 px-2 py-1 bg-[#2d2d30] text-white text-sm rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity delay-500 whitespace-nowrap z-50">
            Analytics
          </div>
        </button>
      </div>
    </div>
  )
} 