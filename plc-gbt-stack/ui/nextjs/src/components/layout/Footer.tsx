'use client';

import { cn } from '@/lib/utils/cn';
import { Clock, Cpu, Database, MemoryStick, Wifi, WifiOff } from 'lucide-react';
import { useEffect, useState } from 'react';

interface FooterProps {
  className?: string;
}

interface SystemStatus {
  connected: boolean;
  activeConnections: number;
  memoryUsage: number;
  cpuUsage: number;
  uptime: string;
}

export function Footer({ className }: FooterProps) {
  const [status, setStatus] = useState<SystemStatus>({
    connected: true,
    activeConnections: 3,
    memoryUsage: 45,
    cpuUsage: 12,
    uptime: '2h 15m',
  });

  // Mock real-time status updates with proper cleanup and error handling
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    try {
      interval = setInterval(() => {
        setStatus(prev => ({
          ...prev,
          memoryUsage: Math.max(30, Math.min(80, prev.memoryUsage + (Math.random() - 0.5) * 5)),
          cpuUsage: Math.max(5, Math.min(50, prev.cpuUsage + (Math.random() - 0.5) * 10)),
        }));
      }, 5000);
    } catch (error) {
      console.error('Footer status update error:', error);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    };
  }, []);

  return (
    <footer
      id="footer-row"
      className={cn(
        'h-6 bg-[#007acc] border-t border-[#005a9e]',
        'flex items-center justify-between px-2 text-white text-xs select-none',
        className
      )}
    >
      {/* Left side - Connection and system status */}
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
          className="hover:bg-[#005a9e] px-2 py-1 rounded transition-colors"
          title="Toggle Terminal"
        >
          Terminal
        </button>
      </div>

      {/* Right side - System info */}
      <div className="flex items-center space-x-4">
        {/* Uptime */}
        <div className="flex items-center space-x-1">
          <Clock className="w-3 h-3" />
          <span>Uptime: {status.uptime}</span>
        </div>

        {/* Version */}
        <div className="text-[#cce7f0]">PLC-GBT v1.0.0</div>
      </div>
    </footer>
  );
}

/**
 * Footer Component
 *
 * @description Fixed 24px height status bar spanning full width
 * @specification Matches VS Code status bar design from main-ui-spec.md
 *
 * @features
 * - Fixed 24px height (h-6 = 1.5rem = 24px)
 * - System status indicators on left
 * - Quick actions in center
 * - Version info on right
 * - Real-time status updates
 * - VS Code inspired blue theme
 *
 * @accessibility
 * - Semantic footer element
 * - Clear status indicators
 * - Keyboard accessible buttons
 */
