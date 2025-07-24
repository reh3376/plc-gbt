'use client'

import { useState, useEffect } from 'react'
import { 
  Wifi, 
  WifiOff, 
  CheckCircle, 
  Clock,
  Database,
  Cpu,
  MemoryStick
} from 'lucide-react'
import { useLayoutStore } from '@/lib/stores/layout-store'

// Mock system status - in real app this would come from a store/API
interface SystemStatus {
  connected: boolean
  uptime: string
  activeConnections: number
  memoryUsage: number
  cpuUsage: number
  lastUpdate: Date | null
}

export function StatusBar() {
  const { toggleBottomPanel } = useLayoutStore()
  const [isClient, setIsClient] = useState(false)
  const [status, setStatus] = useState<SystemStatus>({
    connected: true,
    uptime: '2h 15m',
    activeConnections: 3,
    memoryUsage: 45,
    cpuUsage: 12,
    lastUpdate: null, // Initialize as null to avoid hydration mismatch
  })

  // Set client flag and initialize lastUpdate after hydration
  useEffect(() => {
    setIsClient(true)
    setStatus(prev => ({
      ...prev,
      lastUpdate: new Date(),
    }))
  }, [])

  // Mock real-time updates (only on client)
  useEffect(() => {
    if (!isClient) return

    const interval = setInterval(() => {
      setStatus(prev => ({
        ...prev,
        memoryUsage: Math.max(30, Math.min(80, prev.memoryUsage + (Math.random() - 0.5) * 5)),
        cpuUsage: Math.max(5, Math.min(50, prev.cpuUsage + (Math.random() - 0.5) * 10)),
        lastUpdate: new Date(),
      }))
    }, 5000)

    return () => clearInterval(interval)
  }, [isClient])

  return (
    <div className="h-6 bg-[#007acc] flex items-center justify-between px-2 text-white text-xs select-none">
      {/* Left side - Connection status and system info */}
      <div className="flex items-center space-x-4">
        {/* Connection Status */}
        <div className="flex items-center space-x-1">
          {status.connected ? (
            <>
              <Wifi className="w-3 h-3" />
              <span>Connected</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3 h-3" />
              <span>Disconnected</span>
            </>
          )}
        </div>

        {/* Active Connections */}
        <div className="flex items-center space-x-1">
          <Database className="w-3 h-3" />
          <span>{status.activeConnections} active</span>
        </div>

        {/* System Resources */}
        <div className="flex items-center space-x-1">
          <Cpu className="w-3 h-3" />
          <span>CPU: {Math.round(status.cpuUsage)}%</span>
        </div>

        <div className="flex items-center space-x-1">
          <MemoryStick className="w-3 h-3" />
          <span>RAM: {Math.round(status.memoryUsage)}%</span>
        </div>
      </div>

      {/* Center - Quick actions */}
      <div className="flex items-center space-x-2">
        <button
          onClick={toggleBottomPanel}
          className="hover:bg-[#005a9e] px-2 py-1 rounded transition-colors"
          title="Toggle Terminal"
        >
          Terminal
        </button>
      </div>

      {/* Right side - System status and info */}
      <div className="flex items-center space-x-4">
        {/* Uptime */}
        <div className="flex items-center space-x-1">
          <Clock className="w-3 h-3" />
          <span>Uptime: {status.uptime}</span>
        </div>

        {/* System Status */}
        <div className="flex items-center space-x-1">
          <CheckCircle className="w-3 h-3 text-green-300" />
          <span>Ready</span>
        </div>

        {/* Version */}
        <div className="text-[#cce7f0]">
          PLC-GBT v1.0.0
        </div>

        {/* Last Update Time - Only show when client-side */}
        <div className="text-[#cce7f0]" suppressHydrationWarning>
          {isClient && status.lastUpdate ? status.lastUpdate.toLocaleTimeString() : '--:--:--'}
        </div>
      </div>
    </div>
  )
} 