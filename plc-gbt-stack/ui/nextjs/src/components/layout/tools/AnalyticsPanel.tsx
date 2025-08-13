'use client';

import { useLayoutStore } from '@/lib/stores/layout-store';
import { cn } from '@/lib/utils/cn';
import {
  Activity,
  BarChart3,
  ChevronRight,
  Clock,
  Eye,
  PlayCircle,
  TrendingUp,
} from 'lucide-react';
import { useState } from 'react';

type TrendDirection = 'up' | 'down' | 'stable';

interface AnalyticsMetric {
  id: string;
  name: string;
  value: string;
  trend: TrendDirection;
  change: string;
  icon: React.ComponentType<{ className?: string }>;
}

const mockMetrics: AnalyticsMetric[] = [
  {
    id: 'system-performance',
    name: 'System Performance',
    value: '87.3%',
    trend: 'up',
    change: '+2.1%',
    icon: Activity,
  },
  {
    id: 'active-loops',
    name: 'Active Control Loops',
    value: '12',
    trend: 'stable',
    change: '0',
    icon: PlayCircle,
  },
  {
    id: 'response-time',
    name: 'Avg Response Time',
    value: '45ms',
    trend: 'down',
    change: '-8ms',
    icon: Clock,
  },
  {
    id: 'throughput',
    name: 'Data Throughput',
    value: '2.4 MB/s',
    trend: 'up',
    change: '+0.3 MB/s',
    icon: TrendingUp,
  },
];

function AnalyticsPanel() {
  const { setMainContentMode } = useLayoutStore();
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);

  const handleMetricClick = (metricId: string) => {
    setSelectedMetric(metricId);
  };

  const handleViewFullDashboard = () => {
    setMainContentMode('analytics');
  };

  const getTrendIcon = (trend: TrendDirection) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-3 h-3 text-green-400" />;
      case 'down':
        return <TrendingUp className="w-3 h-3 text-red-400 rotate-180" />;
      case 'stable':
        return <div className="w-3 h-0.5 bg-yellow-400 rounded" />;
    }
  };

  const getTrendColor = (trend: TrendDirection) => {
    switch (trend) {
      case 'up':
        return 'text-green-400';
      case 'down':
        return 'text-red-400';
      case 'stable':
        return 'text-yellow-400';
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-[#252526] text-[#cccccc]">
      {/* Quick Metrics Overview */}
      <div className="p-3 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-[#cccccc]">System Overview</h3>
          <button
            onClick={handleViewFullDashboard}
            className="flex items-center text-xs text-[#007acc] hover:text-[#1a9fff] transition-colors"
            title="View Full Analytics Dashboard"
          >
            <Eye className="w-3 h-3 mr-1" />
            View All
          </button>
        </div>

        {/* Metrics Grid */}
        <div className="space-y-2">
          {mockMetrics.map(metric => {
            const IconComponent = metric.icon;
            const isSelected = selectedMetric === metric.id;

            return (
              <button
                key={metric.id}
                className={cn(
                  'w-full p-2 rounded border cursor-pointer transition-all text-left',
                  isSelected
                    ? 'bg-[#094771] border-[#007acc]'
                    : 'bg-[#2d2d30] border-[#3c3c3c] hover:bg-[#3c3c3c] hover:border-[#464647]'
                )}
                onClick={() => handleMetricClick(metric.id)}
                aria-expanded={isSelected}
                aria-controls={`metric-${metric.id}-details`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <IconComponent className="w-4 h-4 text-[#007acc]" />
                    <span className="text-xs font-medium">{metric.name}</span>
                  </div>
                  <ChevronRight
                    className={cn('w-3 h-3 transition-transform', isSelected ? 'rotate-90' : '')}
                  />
                </div>

                <div className="mt-1 flex items-center justify-between">
                  <span className="text-sm font-bold text-white">{metric.value}</span>
                  <div className="flex items-center space-x-1">
                    {getTrendIcon(metric.trend)}
                    <span className={cn('text-xs', getTrendColor(metric.trend))}>
                      {metric.change}
                    </span>
                  </div>
                </div>

                {/* Expanded Details */}
                {isSelected && (
                  <div
                    className="mt-2 pt-2 border-t border-[#3c3c3c]"
                    id={`metric-${metric.id}-details`}
                  >
                    <div className="text-xs text-[#969696]">
                      Last updated: {new Date().toLocaleTimeString()}
                    </div>
                    <div className="mt-1">
                      <button
                        onClick={e => {
                          e.stopPropagation();
                          handleViewFullDashboard();
                        }}
                        className="text-xs text-[#007acc] hover:text-[#1a9fff] transition-colors"
                      >
                        View detailed analytics →
                      </button>
                    </div>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-auto p-3 border-t border-[#3c3c3c]">
        <div className="space-y-2">
          <button
            onClick={handleViewFullDashboard}
            className="w-full py-2 px-3 bg-[#007acc] text-white text-xs font-medium rounded hover:bg-[#1a9fff] transition-colors flex items-center justify-center space-x-2"
          >
            <BarChart3 className="w-4 h-4" />
            <span>Open Analytics Dashboard</span>
          </button>

          <div className="text-xs text-[#969696] text-center">
            Real-time system analytics and performance monitoring
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPanel;

/**
 * AnalyticsPanel Component
 *
 * @description Tool panel for the Analytics dashboard in the left sidebar
 * @purpose Provides quick overview of system metrics and navigation to full analytics
 *
 * @features
 * - System performance overview
 * - Key metrics display with trends
 * - Quick navigation to full analytics dashboard
 * - Real-time data indicators
 * - Responsive metric cards
 *
 * @integration
 * - Connects to layout store for main content navigation
 * - Designed to fit left sidebar tool panel pattern
 * - Links to full AnalyticsDashboard component
 */
