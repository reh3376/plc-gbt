'use client'

import { Settings, User, Shield, Palette, Monitor } from 'lucide-react'

const settingsCategories = [
  { id: 'user', name: 'User Settings', icon: User },
  { id: 'security', name: 'Security', icon: Shield },
  { id: 'appearance', name: 'Appearance', icon: Palette },
  { id: 'system', name: 'System', icon: Monitor },
]

export function SettingsPanel() {
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-2 border-b border-[#3c3c3c]">
        <div className="flex items-center space-x-2">
          <Settings className="w-4 h-4 text-[#cccccc]" />
          <span className="text-[#cccccc] text-sm font-medium">Settings</span>
        </div>
      </div>

      {/* Settings Categories */}
      <div className="flex-1 overflow-auto p-2">
        {settingsCategories.map((category) => {
          const Icon = category.icon
          return (
            <div 
              key={category.id} 
              className="flex items-center space-x-3 p-2 hover:bg-[#2a2d2e] rounded cursor-pointer transition-colors"
            >
              <Icon className="w-4 h-4 text-[#cccccc]" />
              <span className="text-[#cccccc] text-sm">{category.name}</span>
            </div>
          )
        })}
      </div>

      {/* Quick Settings */}
      <div className="p-2 border-t border-[#3c3c3c]">
        <div className="text-[#969696] text-xs mb-2">Quick Settings</div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[#cccccc] text-sm">Dark Theme</span>
            <div className="w-8 h-4 bg-[#007acc] rounded-full relative">
              <div className="w-3 h-3 bg-white rounded-full absolute right-0.5 top-0.5"></div>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[#cccccc] text-sm">Auto Save</span>
            <div className="w-8 h-4 bg-[#007acc] rounded-full relative">
              <div className="w-3 h-3 bg-white rounded-full absolute right-0.5 top-0.5"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 