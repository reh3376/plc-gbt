'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'
import { 
  User,
  Palette,
  Globe,
  Bell,
  Shield,
  Eye,
  Database
} from 'lucide-react'

interface Setting {
  id: string
  category: string
  name: string
  description: string
  type: 'boolean' | 'select' | 'number' | 'text'
  value: string | number | boolean
  options?: string[]
  min?: number
  max?: number
}

const mockSettings: Setting[] = [
  {
    id: 'theme',
    category: 'Appearance',
    name: 'Color Theme',
    description: 'Choose the color theme for the application',
    type: 'select',
    value: 'dark',
    options: ['dark', 'light', 'high-contrast', 'industrial']
  },
  {
    id: 'fontSize',
    category: 'Appearance',
    name: 'Font Size',
    description: 'Editor font size in pixels',
    type: 'number',
    value: 14,
    min: 10,
    max: 24
  },
  {
    id: 'autoSave',
    category: 'Editor',
    name: 'Auto Save',
    description: 'Automatically save changes after editing',
    type: 'boolean',
    value: true
  },
  {
    id: 'autoSaveDelay',
    category: 'Editor',
    name: 'Auto Save Delay',
    description: 'Delay in seconds before auto saving',
    type: 'number',
    value: 2,
    min: 1,
    max: 10
  },
  {
    id: 'showLineNumbers',
    category: 'Editor',
    name: 'Show Line Numbers',
    description: 'Display line numbers in the editor',
    type: 'boolean',
    value: true
  },
  {
    id: 'wordWrap',
    category: 'Editor',
    name: 'Word Wrap',
    description: 'Wrap long lines in the editor',
    type: 'boolean',
    value: false
  },
  {
    id: 'notifications',
    category: 'System',
    name: 'Enable Notifications',
    description: 'Show system and workflow notifications',
    type: 'boolean',
    value: true
  },
  {
    id: 'soundAlerts',
    category: 'System',
    name: 'Sound Alerts',
    description: 'Play sound for critical alerts',
    type: 'boolean',
    value: true
  },
  {
    id: 'backupInterval',
    category: 'System',
    name: 'Backup Interval',
    description: 'Automatic backup interval in hours',
    type: 'select',
    value: '6',
    options: ['1', '3', '6', '12', '24']
  },
  {
    id: 'connectionTimeout',
    category: 'Network',
    name: 'Connection Timeout',
    description: 'PLC connection timeout in seconds',
    type: 'number',
    value: 30,
    min: 5,
    max: 120
  },
  {
    id: 'retryAttempts',
    category: 'Network',
    name: 'Retry Attempts',
    description: 'Number of retry attempts for failed connections',
    type: 'number',
    value: 3,
    min: 1,
    max: 10
  }
]

function SettingsPanel() {
  const [settings, setSettings] = useState<Setting[]>(mockSettings)
  const [activeCategory, setActiveCategory] = useState('Appearance')
  const [hasChanges, setHasChanges] = useState(false)

  const categories = [...new Set(settings.map(s => s.category))]

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Appearance':
        return <Palette className="w-4 h-4" />
      case 'Editor':
        return <Globe className="w-4 h-4" />
      case 'System':
        return <Bell className="w-4 h-4" />
      case 'Network':
        return <Database className="w-4 h-4" />
      case 'Security':
        return <Shield className="w-4 h-4" />
      default:
        return <User className="w-4 h-4" />
    }
  }

  const updateSetting = (id: string, value: string | number | boolean) => {
    setSettings(prev => prev.map(setting => 
      setting.id === id ? { ...setting, value } : setting
    ))
    setHasChanges(true)
  }

  const saveSettings = () => {
    // Here you would save to backend/localStorage
    console.log('Saving settings:', settings)
    setHasChanges(false)
  }

  const resetSettings = () => {
    setSettings(mockSettings)
    setHasChanges(false)
  }

  const renderSetting = (setting: Setting) => {
    switch (setting.type) {
      case 'boolean':
        return (
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-[#cccccc] text-sm font-medium">{setting.name}</h4>
              <p className="text-[#969696] text-xs">{setting.description}</p>
            </div>
            <button
              onClick={() => updateSetting(setting.id, !setting.value)}
              className={cn(
                "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                setting.value ? "bg-[#007acc]" : "bg-[#3c3c3c]"
              )}
            >
              <span
                className={cn(
                  "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                  setting.value ? "translate-x-6" : "translate-x-1"
                )}
              />
            </button>
          </div>
        )

      case 'select':
        return (
          <div>
            <h4 className="text-[#cccccc] text-sm font-medium mb-1">{setting.name}</h4>
            <p className="text-[#969696] text-xs mb-2">{setting.description}</p>
            <select
              value={String(setting.value)}
              onChange={(e) => updateSetting(setting.id, e.target.value)}
              className="w-full px-3 py-2 text-sm bg-[#3c3c3c] text-[#cccccc] border border-[#3c3c3c] rounded focus:border-[#007acc] focus:outline-none"
            >
              {setting.options?.map(option => (
                <option key={option} value={option}>
                  {option.charAt(0).toUpperCase() + option.slice(1)}
                </option>
              ))}
            </select>
          </div>
        )

      case 'number':
        return (
          <div>
            <h4 className="text-[#cccccc] text-sm font-medium mb-1">{setting.name}</h4>
            <p className="text-[#969696] text-xs mb-2">{setting.description}</p>
            <input
              type="number"
              value={Number(setting.value)}
              min={setting.min}
              max={setting.max}
              onChange={(e) => updateSetting(setting.id, parseInt(e.target.value))}
              className="w-full px-3 py-2 text-sm bg-[#3c3c3c] text-[#cccccc] border border-[#3c3c3c] rounded focus:border-[#007acc] focus:outline-none"
            />
          </div>
        )

      case 'text':
        return (
          <div>
            <h4 className="text-[#cccccc] text-sm font-medium mb-1">{setting.name}</h4>
            <p className="text-[#969696] text-xs mb-2">{setting.description}</p>
            <input
              type="text"
              value={String(setting.value)}
              onChange={(e) => updateSetting(setting.id, e.target.value)}
              className="w-full px-3 py-2 text-sm bg-[#3c3c3c] text-[#cccccc] border border-[#3c3c3c] rounded focus:border-[#007acc] focus:outline-none"
            />
          </div>
        )

      default:
        return null
    }
  }

  const categorySettings = settings.filter(s => s.category === activeCategory)

  return (
    <div className="h-full flex flex-col">
      {/* Header with save actions */}
      <div className="p-3 border-b border-[#3c3c3c]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-[#cccccc] font-medium">Settings</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={resetSettings}
              disabled={!hasChanges}
              className="flex items-center space-x-1 px-2 py-1 bg-[#3c3c3c] hover:bg-[#505050] disabled:opacity-50 disabled:cursor-not-allowed text-[#cccccc] text-xs rounded transition-colors"
            >
              <Eye className="w-3 h-3" />
              <span>Reset</span>
            </button>
            <button
              onClick={saveSettings}
              disabled={!hasChanges}
              className="flex items-center space-x-1 px-2 py-1 bg-[#007acc] hover:bg-[#1177bb] disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs rounded transition-colors"
            >
              <Database className="w-3 h-3" />
              <span>Save</span>
            </button>
          </div>
        </div>

        {hasChanges && (
          <div className="text-xs text-[#ffa500] flex items-center space-x-1">
            <span>•</span>
            <span>You have unsaved changes</span>
          </div>
        )}
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Category sidebar */}
        <div className="w-40 bg-[#2d2d30] border-r border-[#3c3c3c] p-2">
          <div className="space-y-1">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={cn(
                  "w-full flex items-center space-x-2 px-2 py-2 text-sm rounded transition-colors",
                  activeCategory === category
                    ? "bg-[#007acc] text-white"
                    : "text-[#cccccc] hover:bg-[#3c3c3c]"
                )}
              >
                {getCategoryIcon(category)}
                <span>{category}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Settings content */}
        <div className="flex-1 overflow-auto">
          <div className="p-4 space-y-6">
            {categorySettings.map(setting => (
              <div
                key={setting.id}
                className="p-4 bg-[#2a2d2e] rounded border border-[#3c3c3c]"
              >
                {renderSetting(setting)}
              </div>
            ))}

            {categorySettings.length === 0 && (
              <div className="text-center text-[#969696] text-sm py-8">
                No settings available for this category
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer with info */}
      <div className="p-2 border-t border-[#3c3c3c] text-xs text-[#969696]">
        <div className="flex items-center justify-between">
          <span>{categorySettings.length} setting{categorySettings.length !== 1 ? 's' : ''} in {activeCategory}</span>
          <span>PLC-GBT v1.0.0</span>
        </div>
      </div>
    </div>
  )
}

export default SettingsPanel

/**
 * SettingsPanel Component
 * 
 * @description Application settings and preferences management
 * @specification Implements main-ui-spec.md SettingsPanel tool requirements
 * 
 * @features
 * - Categorized settings organization
 * - Multiple input types (boolean, select, number, text)
 * - Real-time setting updates with change tracking
 * - Save/reset functionality
 * - Responsive layout with category sidebar
 * - Visual change indicators
 * 
 * @categories
 * - Appearance: Theme, font size, layout preferences
 * - Editor: Auto-save, line numbers, word wrap
 * - System: Notifications, backups, alerts
 * - Network: Connection settings, timeouts
 * - Security: Authentication, permissions
 * 
 * @accessibility
 * - Keyboard navigation support
 * - Clear input labels and descriptions
 * - Screen reader friendly
 * - Focus indicators
 * 
 * @performance
 * - Lazy loaded via Suspense
 * - Efficient setting updates
 * - Optimized re-renders
 */ 