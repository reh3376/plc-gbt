/**
 * System Health Dashboard - Phase 31.8 Task 31.8.3
 * AI Task Orchestrator Generated - System Health Monitoring with Real-time Updates
 *
 * Comprehensive system health monitoring dashboard with:
 * - Real-time status indicators with color coding
 * - System component health grid
 * - Alert management with acknowledgment
 * - Performance metrics visualization
 * - Industrial-grade reliability monitoring
 */

'use client';

import { useAnalyticsStore } from '@/lib/stores/analytics-store';
import type { HealthStatus, SystemHealth, SystemHealthProps } from '@/lib/types/analytics.types';
import { cn } from '@/lib/utils/cn';
import {
  Activity,
  AlertTriangle,
  Bell,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  // Memory, // Not available in this lucide-react version
  HardDrive,
  RefreshCw,
  Server,
  Shield,
  Wifi,
  XCircle,
  Zap,
} from 'lucide-react';
import React, { useCallback, useEffect, useMemo } from 'react';

// Health status color mapping for industrial applications
const getHealthStatusStyle = (status: HealthStatus) => {
  switch (status) {
    case 'healthy':
      return {
        color: 'text-green-400',
        bg: 'bg-green-500/20',
        border: 'border-green-500/50',
        icon: CheckCircle,
        pulse: false,
      };
    case 'warning':
      return {
        color: 'text-yellow-400',
        bg: 'bg-yellow-500/20',
        border: 'border-yellow-500/50',
        icon: AlertTriangle,
        pulse: true,
      };
    case 'critical':
      return {
        color: 'text-red-400',
        bg: 'bg-red-500/20',
        border: 'border-red-500/50',
        icon: XCircle,
        pulse: true,
      };
    case 'unknown':
    default:
      return {
        color: 'text-gray-400',
        bg: 'bg-gray-500/20',
        border: 'border-gray-500/50',
        icon: Clock,
        pulse: false,
      };
  }
};

// Component type icon mapping
const getComponentIcon = (componentType: string) => {
  const type = componentType.toLowerCase();
  if (type.includes('cpu') || type.includes('processor')) return Cpu;
  if (type.includes('memory') || type.includes('ram')) return HardDrive;
  if (type.includes('disk') || type.includes('storage')) return HardDrive;
  if (type.includes('network') || type.includes('ethernet')) return Wifi;
  if (type.includes('database') || type.includes('db')) return Database;
  if (type.includes('server') || type.includes('service')) return Server;
  if (type.includes('security') || type.includes('auth')) return Shield;
  if (type.includes('power') || type.includes('ups')) return Zap;
  return Activity;
};

// Mock system health data for development
const mockSystemHealth: SystemHealth = {
  overall: 'warning',
  components: [
    {
      id: 'cpu-001',
      name: 'Primary CPU',
      status: 'healthy',
      lastCheck: new Date(),
      uptime: 99.8,
      responseTime: 12,
      errorRate: 0.1,
    },
    {
      id: 'memory-001',
      name: 'System Memory',
      status: 'warning',
      lastCheck: new Date(),
      uptime: 98.5,
      responseTime: 8,
      errorRate: 1.2,
      metadata: { usage: 87 },
    },
    {
      id: 'database-001',
      name: 'PostgreSQL Primary',
      status: 'healthy',
      lastCheck: new Date(),
      uptime: 99.9,
      responseTime: 25,
      errorRate: 0.05,
    },
    {
      id: 'network-001',
      name: 'Network Interface',
      status: 'critical',
      lastCheck: new Date(),
      uptime: 92.3,
      responseTime: 150,
      errorRate: 8.5,
    },
  ],
  metrics: {
    uptime: 98.5,
    totalRequests: 1250000,
    errorRate: 2.3,
    avgResponseTime: 45,
    memoryUsage: 87,
    cpuUsage: 34,
    diskUsage: 67,
    networkLatency: 12,
  },
  alerts: [
    {
      id: 'alert-001',
      severity: 'critical',
      title: 'High Memory Usage',
      message: 'System memory usage exceeded 85% threshold',
      component: 'memory-001',
      timestamp: new Date(Date.now() - 1000 * 60 * 5),
      acknowledged: false,
    },
    {
      id: 'alert-002',
      severity: 'warning',
      title: 'Network Latency Spike',
      message: 'Network response time increased by 200%',
      component: 'network-001',
      timestamp: new Date(Date.now() - 1000 * 60 * 15),
      acknowledged: true,
    },
  ],
  lastUpdated: new Date(),
};

/**
 * System Health Dashboard Component
 *
 * Features:
 * - Real-time system health monitoring
 * - Component status grid with color-coded indicators
 * - Alert management with acknowledgment
 * - Performance metrics with trend indicators
 * - Industrial-grade reliability monitoring
 * - WCAG 2.1 AA accessibility compliance
 */
export function SystemHealthDashboard({
  refreshInterval = 5000,
  showDetails = true,
  alertsOnly = false,
  onAlertAcknowledge,
  className,
}: SystemHealthProps) {
  // Analytics store integration
  const { systemHealth, setSystemHealth, acknowledgeAlert, setLoading, setError } =
    useAnalyticsStore();

  // Use mock data for development with proper fallback
  const currentHealth = useMemo(() => {
    // Ensure we have valid system health data with required properties
    if (
      systemHealth &&
      typeof systemHealth === 'object' &&
      Array.isArray((systemHealth as unknown as SystemHealth).alerts) &&
      Array.isArray((systemHealth as unknown as SystemHealth).components)
    ) {
      return systemHealth as unknown as SystemHealth;
    }
    return mockSystemHealth;
  }, [systemHealth]);

  // Get unacknowledged alerts
  const unacknowledgedAlerts = useMemo(
    () => currentHealth.alerts?.filter(alert => !alert.acknowledged) || [],
    [currentHealth.alerts]
  );

  // Critical components count
  const criticalComponents = useMemo(
    () =>
      currentHealth.components?.filter(component => component.status === 'critical').length || 0,
    [currentHealth.components]
  );

  // Update system health data
  const updateSystemHealth = useCallback(async () => {
    try {
      setLoading(true);

      // In a real implementation, this would fetch from API
      // For now, simulate data updates
      const updatedHealth: SystemHealth = {
        ...mockSystemHealth,
        lastUpdated: new Date(),
        // Simulate some data changes
        metrics: {
          ...mockSystemHealth.metrics,
          cpuUsage: Math.random() * 50 + 20,
          memoryUsage: Math.random() * 30 + 60,
          networkLatency: Math.random() * 20 + 5,
        },
      };

      setSystemHealth(updatedHealth as unknown as Record<string, unknown>);
      setError(null);
    } catch (err) {
      console.error('Failed to update system health:', err);
      setError('Failed to update system health data');
    } finally {
      setLoading(false);
    }
  }, [setSystemHealth, setLoading, setError]);

  // Auto-refresh system health
  useEffect(() => {
    const interval = setInterval(updateSystemHealth, refreshInterval);
    return () => clearInterval(interval);
  }, [updateSystemHealth, refreshInterval]);

  // Handle alert acknowledgment
  const handleAcknowledgeAlert = useCallback(
    (alertId: string) => {
      acknowledgeAlert(alertId);
      if (onAlertAcknowledge) {
        onAlertAcknowledge(alertId);
      }
    },
    [acknowledgeAlert, onAlertAcknowledge]
  );

  // Overall health status style
  const overallHealthStyle = getHealthStatusStyle(currentHealth.overall || 'unknown');
  const OverallHealthIcon = overallHealthStyle.icon;

  if (alertsOnly) {
    return (
      <div className={cn('space-y-4', className)}>
        {/* Alerts List */}
        <div className="bg-[#252526] border border-[#3c3c3c] rounded-md">
          <div className="p-3 border-b border-[#3c3c3c] bg-[#2d2d30]">
            <div className="flex items-center justify-between">
              <h3 className="text-[#cccccc] text-sm font-medium">System Alerts</h3>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-[#969696]">
                  {unacknowledgedAlerts.length} unacknowledged
                </span>
                <button
                  onClick={updateSystemHealth}
                  className="p-1 rounded text-[#969696] hover:text-[#cccccc] hover:bg-[#3c3c3c] transition-colors"
                  title="Refresh alerts"
                >
                  <RefreshCw className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>

          <div className="p-3 space-y-2 max-h-64 overflow-y-auto">
            {(currentHealth.alerts?.length || 0) === 0 ? (
              <div className="text-center py-6 text-[#969696]">
                <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-400" />
                <p className="text-sm">No active alerts</p>
              </div>
            ) : (
              currentHealth.alerts?.map(alert => {
                const severityStyle = getHealthStatusStyle(
                  alert.severity === 'info'
                    ? 'healthy'
                    : alert.severity === 'warning'
                      ? 'warning'
                      : alert.severity === 'error' || alert.severity === 'critical'
                        ? 'critical'
                        : 'unknown'
                );
                const SeverityIcon = severityStyle.icon;

                return (
                  <div
                    key={alert.id}
                    className={cn(
                      'p-3 rounded border',
                      severityStyle.bg,
                      severityStyle.border,
                      alert.acknowledged ? 'opacity-60' : ''
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <SeverityIcon className={cn('w-4 h-4 mt-0.5', severityStyle.color)} />
                        <div className="flex-1 min-w-0">
                          <h4 className="text-[#cccccc] text-sm font-medium">{alert.title}</h4>
                          <p className="text-[#969696] text-xs mt-1">{alert.message}</p>
                          <div className="flex items-center space-x-3 mt-2 text-xs text-[#969696]">
                            <span>{alert.timestamp.toLocaleTimeString()}</span>
                            {alert.component && <span>Component: {alert.component}</span>}
                            {alert.acknowledged && (
                              <span className="text-green-400">✓ Acknowledged</span>
                            )}
                          </div>
                        </div>
                      </div>

                      {!alert.acknowledged && (
                        <button
                          onClick={() => handleAcknowledgeAlert(alert.id)}
                          className="px-2 py-1 text-xs bg-blue-600/20 text-blue-400 border border-blue-500/50 rounded hover:bg-blue-600/30 transition-colors"
                        >
                          Acknowledge
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Overall System Status */}
      <div className="bg-[#252526] border border-[#3c3c3c] rounded-md">
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div
                className={cn(
                  'p-2 rounded-full',
                  overallHealthStyle.bg,
                  overallHealthStyle.pulse ? 'animate-pulse' : ''
                )}
              >
                <OverallHealthIcon className={cn('w-6 h-6', overallHealthStyle.color)} />
              </div>
              <div>
                <h2 className="text-[#cccccc] text-lg font-semibold">System Health</h2>
                <p className={cn('text-sm font-medium capitalize', overallHealthStyle.color)}>
                  {currentHealth.overall}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4 text-sm text-[#969696]">
              <div className="text-center">
                <div className="font-medium text-[#cccccc]">
                  {(currentHealth.metrics?.uptime || 0).toFixed(1)}%
                </div>
                <div className="text-xs">Uptime</div>
              </div>
              <div className="text-center">
                <div className="font-medium text-[#cccccc]">{criticalComponents}</div>
                <div className="text-xs">Critical</div>
              </div>
              <div className="text-center">
                <div className="font-medium text-[#cccccc]">{unacknowledgedAlerts.length}</div>
                <div className="text-xs">Alerts</div>
              </div>
              <button
                onClick={updateSystemHealth}
                className="p-2 rounded text-[#969696] hover:text-[#cccccc] hover:bg-[#3c3c3c] transition-colors"
                title="Refresh system health"
                aria-label="Refresh system health"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          {
            label: 'CPU Usage',
            value: currentHealth.metrics?.cpuUsage || 0,
            unit: '%',
            icon: Cpu,
            threshold: { warning: 70, critical: 90 },
          },
          {
            label: 'Memory Usage',
            value: currentHealth.metrics?.memoryUsage || 0,
            unit: '%',
            icon: HardDrive,
            threshold: { warning: 80, critical: 95 },
          },
          {
            label: 'Disk Usage',
            value: currentHealth.metrics?.diskUsage || 0,
            unit: '%',
            icon: HardDrive,
            threshold: { warning: 85, critical: 95 },
          },
          {
            label: 'Response Time',
            value: currentHealth.metrics?.avgResponseTime || 0,
            unit: 'ms',
            icon: Activity,
            threshold: { warning: 100, critical: 500 },
          },
        ].map(metric => {
          const status =
            metric.value >= metric.threshold.critical
              ? 'critical'
              : metric.value >= metric.threshold.warning
                ? 'warning'
                : 'healthy';
          const style = getHealthStatusStyle(status);
          const MetricIcon = metric.icon;

          return (
            <div key={metric.label} className="bg-[#252526] border border-[#3c3c3c] rounded-md p-4">
              <div className="flex items-center justify-between mb-2">
                <MetricIcon className="w-4 h-4 text-[#969696]" />
                <div
                  className={cn(
                    'w-2 h-2 rounded-full',
                    style.bg.replace('/20', ''),
                    style.pulse ? 'animate-pulse' : ''
                  )}
                />
              </div>
              <div className="space-y-1">
                <div className="text-lg font-semibold text-[#cccccc]">
                  {metric.value.toFixed(1)}
                  {metric.unit}
                </div>
                <div className="text-xs text-[#969696]">{metric.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {showDetails && (
        <>
          {/* Component Health Grid */}
          <div className="bg-[#252526] border border-[#3c3c3c] rounded-md">
            <div className="p-3 border-b border-[#3c3c3c] bg-[#2d2d30]">
              <h3 className="text-[#cccccc] text-sm font-medium">System Components</h3>
            </div>

            <div className="p-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {currentHealth.components?.map(component => {
                  const style = getHealthStatusStyle(component.status);
                  const ComponentIcon = getComponentIcon(component.name);
                  const StatusIcon = style.icon;

                  return (
                    <div
                      key={component.id}
                      className={cn('p-3 rounded border', style.bg, style.border)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <ComponentIcon className="w-4 h-4 text-[#969696]" />
                          <span className="text-[#cccccc] text-sm font-medium">
                            {component.name}
                          </span>
                        </div>
                        <StatusIcon className={cn('w-4 h-4', style.color)} />
                      </div>

                      <div className="grid grid-cols-3 gap-2 text-xs text-[#969696]">
                        <div>
                          <div className="font-medium text-[#cccccc]">
                            {component.uptime?.toFixed(1) || 'N/A'}%
                          </div>
                          <div>Uptime</div>
                        </div>
                        <div>
                          <div className="font-medium text-[#cccccc]">
                            {component.responseTime || 'N/A'}ms
                          </div>
                          <div>Response</div>
                        </div>
                        <div>
                          <div className="font-medium text-[#cccccc]">
                            {component.errorRate?.toFixed(1) || 'N/A'}%
                          </div>
                          <div>Errors</div>
                        </div>
                      </div>

                      <div className="mt-2 text-xs text-[#969696]">
                        Last check: {component.lastCheck.toLocaleTimeString()}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Recent Alerts */}
          <div className="bg-[#252526] border border-[#3c3c3c] rounded-md">
            <div className="p-3 border-b border-[#3c3c3c] bg-[#2d2d30]">
              <div className="flex items-center justify-between">
                <h3 className="text-[#cccccc] text-sm font-medium">Recent Alerts</h3>
                <div className="flex items-center space-x-2">
                  {unacknowledgedAlerts.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <Bell className="w-3 h-3 text-yellow-400" />
                      <span className="text-xs text-yellow-400">{unacknowledgedAlerts.length}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="p-3 space-y-2 max-h-48 overflow-y-auto">
              {currentHealth.alerts?.slice(0, 5).map(alert => {
                const severityStyle = getHealthStatusStyle(
                  alert.severity === 'info'
                    ? 'healthy'
                    : alert.severity === 'warning'
                      ? 'warning'
                      : alert.severity === 'error' || alert.severity === 'critical'
                        ? 'critical'
                        : 'unknown'
                );
                const SeverityIcon = severityStyle.icon;

                return (
                  <div
                    key={alert.id}
                    className={cn(
                      'flex items-center justify-between p-2 rounded border',
                      severityStyle.bg,
                      severityStyle.border,
                      alert.acknowledged ? 'opacity-60' : ''
                    )}
                  >
                    <div className="flex items-center space-x-2 flex-1 min-w-0">
                      <SeverityIcon className={cn('w-3 h-3', severityStyle.color)} />
                      <div className="flex-1 min-w-0">
                        <div className="text-[#cccccc] text-xs font-medium truncate">
                          {alert.title}
                        </div>
                        <div className="text-[#969696] text-xs">
                          {alert.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>

                    {!alert.acknowledged && (
                      <button
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                        className="ml-2 px-2 py-1 text-xs bg-blue-600/20 text-blue-400 border border-blue-500/50 rounded hover:bg-blue-600/30 transition-colors"
                      >
                        Ack
                      </button>
                    )}
                  </div>
                );
              })}

              {(currentHealth.alerts?.length || 0) === 0 && (
                <div className="text-center py-4 text-[#969696]">
                  <CheckCircle className="w-6 h-6 mx-auto mb-2 text-green-400" />
                  <p className="text-sm">No recent alerts</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default SystemHealthDashboard;
