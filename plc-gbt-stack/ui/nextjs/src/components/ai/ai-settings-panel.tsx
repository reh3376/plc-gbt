'use client'

import { useState } from 'react'
import { 
  Settings, 
  Palette, 
  Monitor, 
  Save, 
  RotateCcw,
  MousePointer,
  Download,
  Upload,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useAIAssistantStore, DockPosition } from '@/lib/stores/ai-assistant-store'

interface AISettingsPanelProps {
  isOpen: boolean
  onClose: () => void
}

export function AISettingsPanel({ isOpen, onClose }: AISettingsPanelProps) {
  const {
    userPreferences,
    dockPosition,
    size,
    position,
    setUserPreferences,
    setDockPosition,
    resetToDefaults,
    saveUserSession,
  } = useAIAssistantStore()

  const [activeTab, setActiveTab] = useState<'general' | 'appearance' | 'behavior' | 'advanced'>('general')
  const [tempUserId, setTempUserId] = useState(userPreferences.userId || '')

  if (!isOpen) return null

  const handleSaveUserSession = () => {
    if (tempUserId.trim()) {
      saveUserSession(tempUserId.trim())
    }
  }

  const handleExportSettings = () => {
    const settings = {
      userPreferences,
      dockPosition,
      size,
      position,
      exportDate: new Date().toISOString(),
    }
    const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `plc-gbt-ai-settings-${tempUserId || 'user'}-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleImportSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const settings = JSON.parse(e.target?.result as string)
        if (settings.userPreferences) {
          setUserPreferences(settings.userPreferences)
        }
        if (settings.dockPosition) {
          setDockPosition(settings.dockPosition)
        }
        alert('Settings imported successfully!')
      } catch {
        alert('Invalid settings file format!')
      }
    }
    reader.readAsText(file)
  }

  const tabs = [
    { id: 'general' as const, label: 'General', icon: Settings },
    { id: 'appearance' as const, label: 'Appearance', icon: Palette },
    { id: 'behavior' as const, label: 'Behavior', icon: MousePointer },
    { id: 'advanced' as const, label: 'Advanced', icon: Monitor },
  ]

  const dockOptions: { value: DockPosition; label: string }[] = [
    { value: 'right', label: 'Right Side (Traditional)' },
    { value: 'left', label: 'Left Side (After Sidebar)' },
    { value: 'center-left', label: '2nd Column (Center-Left)' },
    { value: 'center-right', label: '3rd Column (Center-Right)' },
    { value: 'top', label: 'Top Panel' },
    { value: 'bottom', label: 'Bottom Panel' },
    { value: 'floating', label: 'Free Floating' },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[#2d2d30] border border-[#3c3c3c] rounded-lg shadow-xl w-[600px] max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#3c3c3c]">
          <div className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-[#569cd6]" />
            <h2 className="text-lg font-medium text-[#cccccc]">AI Assistant Settings</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors"
          >
            <X className="w-4 h-4 text-[#cccccc]" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-[#3c3c3c]">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center space-x-2 px-4 py-3 text-sm transition-colors",
                  activeTab === tab.id 
                    ? "bg-[#3c3c3c] text-[#cccccc] border-b-2 border-[#007acc]" 
                    : "text-[#969696] hover:text-[#cccccc] hover:bg-[#2a2d2e]"
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-[#cccccc] mb-2">
                  User ID (for settings persistence)
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={tempUserId}
                    onChange={(e) => setTempUserId(e.target.value)}
                    placeholder="Enter your user ID"
                    className="flex-1 px-3 py-2 bg-[#3c3c3c] text-[#cccccc] rounded border border-[#525252] focus:border-[#007acc] focus:outline-none"
                  />
                  <button
                    onClick={handleSaveUserSession}
                    disabled={!tempUserId.trim()}
                    className="px-4 py-2 bg-[#007acc] text-white rounded hover:bg-[#005a9e] transition-colors disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-xs text-[#969696] mt-1">
                  Your UI preferences will be saved under this user ID
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#cccccc] mb-2">
                  Default Panel Position
                </label>
                <select
                  value={userPreferences.defaultDockPosition}
                  onChange={(e) => setUserPreferences({ defaultDockPosition: e.target.value as DockPosition })}
                  className="w-full px-3 py-2 bg-[#3c3c3c] text-[#cccccc] rounded border border-[#525252] focus:border-[#007acc] focus:outline-none"
                >
                  {dockOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-[#cccccc]">Show Timestamps</label>
                  <p className="text-xs text-[#969696]">Display message timestamps in chat</p>
                </div>
                <button
                  onClick={() => setUserPreferences({ showTimestamps: !userPreferences.showTimestamps })}
                  className={cn(
                    "w-12 h-6 rounded-full relative transition-colors",
                    userPreferences.showTimestamps ? "bg-[#007acc]" : "bg-[#525252]"
                  )}
                >
                  <div className={cn(
                    "w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform",
                    userPreferences.showTimestamps ? "translate-x-6" : "translate-x-0.5"
                  )} />
                </button>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-[#cccccc] mb-2">Theme</label>
                <div className="grid grid-cols-2 gap-3">
                  {(['dark', 'light'] as const).map((theme) => (
                    <button
                      key={theme}
                      onClick={() => setUserPreferences({ theme })}
                      className={cn(
                        "p-3 rounded border-2 transition-colors text-left",
                        userPreferences.theme === theme
                          ? "border-[#007acc] bg-[#0a3a5c]"
                          : "border-[#525252] bg-[#3c3c3c] hover:border-[#666666]"
                      )}
                    >
                      <div className="flex items-center space-x-2">
                        <div className={cn(
                          "w-4 h-4 rounded-full",
                          theme === 'dark' ? "bg-[#1e1e1e]" : "bg-[#ffffff]"
                        )} />
                        <span className="text-[#cccccc] capitalize">{theme}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'behavior' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-[#cccccc]">Snap to Edges</label>
                  <p className="text-xs text-[#969696]">Automatically snap panel to screen edges</p>
                </div>
                <button
                  onClick={() => setUserPreferences({ snapToEdges: !userPreferences.snapToEdges })}
                  className={cn(
                    "w-12 h-6 rounded-full relative transition-colors",
                    userPreferences.snapToEdges ? "bg-[#007acc]" : "bg-[#525252]"
                  )}
                >
                  <div className={cn(
                    "w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform",
                    userPreferences.snapToEdges ? "translate-x-6" : "translate-x-0.5"
                  )} />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-[#cccccc]">Auto Minimize</label>
                  <p className="text-xs text-[#969696]">Minimize panel when clicking outside</p>
                </div>
                <button
                  onClick={() => setUserPreferences({ autoMinimize: !userPreferences.autoMinimize })}
                  className={cn(
                    "w-12 h-6 rounded-full relative transition-colors",
                    userPreferences.autoMinimize ? "bg-[#007acc]" : "bg-[#525252]"
                  )}
                >
                  <div className={cn(
                    "w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform",
                    userPreferences.autoMinimize ? "translate-x-6" : "translate-x-0.5"
                  )} />
                </button>
              </div>
            </div>
          )}

          {activeTab === 'advanced' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-medium text-[#cccccc] mb-3">Settings Management</h3>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={handleExportSettings}
                    className="flex items-center space-x-2 px-3 py-2 bg-[#3c3c3c] text-[#cccccc] rounded hover:bg-[#525252] transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>Export Settings</span>
                  </button>
                  
                  <label className="flex items-center space-x-2 px-3 py-2 bg-[#3c3c3c] text-[#cccccc] rounded hover:bg-[#525252] transition-colors cursor-pointer">
                    <Upload className="w-4 h-4" />
                    <span>Import Settings</span>
                    <input
                      type="file"
                      accept=".json"
                      onChange={handleImportSettings}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-[#cccccc] mb-3">Reset Options</h3>
                <button
                  onClick={resetToDefaults}
                  className="flex items-center space-x-2 px-3 py-2 bg-[#e81123] text-white rounded hover:bg-[#c50e1f] transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Reset to Defaults</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-2 p-4 border-t border-[#3c3c3c]">
          <button
            onClick={onClose}
            className="px-4 py-2 text-[#cccccc] hover:bg-[#3c3c3c] rounded transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
} 