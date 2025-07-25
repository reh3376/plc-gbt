'use client';

import {
  AnalyticsChart,
  HistoricalDataAnalysis,
  SystemHealthDashboard,
} from '@/components/analytics';
import { useAnalyticsStore } from '@/lib/stores/analytics-store';
import type {
  AnalyticsChartConfig,
  DataPoint,
} from '@/lib/types/analytics.types';
import {
  Activity,
  BarChart3,
  Clock,
  Heart,
  Pause,
  Play,
  RotateCcw,
} from 'lucide-react';
import React, { useEffect, useState } from 'react';

// Generate mock real-time data for charts
const generateMockData = (count: number = 50): DataPoint[] => {
  const now = new Date();
  return Array.from({ length: count }, (_, i) => ({
    timestamp: new Date(now.getTime() - (count - i) * 60000), // 1 minute intervals
    value: Math.random() * 100 + Math.sin(i / 10) * 20 + 50,
    label: `Data Point ${i + 1}`,
  }));
};

// Mock chart configurations for testing
const mockChartConfigs: AnalyticsChartConfig[] = [
  {
    id: 'temperature-chart',
    title: 'Temperature Monitoring',
    type: 'line',
    datasets: [
      {
        id: 'temp-sensor-1',
        name: 'TT-001 Reactor Temp',
        label: 'TT-001 Reactor Temp',
        data: generateMockData(),
        unit: '°C',
        source: 'TT-001',
        tension: 0.4,
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
      },
      {
        id: 'temp-sensor-2',
        name: 'TT-002 Outlet Temp',
        label: 'TT-002 Outlet Temp',
        data: generateMockData().map((point) => ({
          ...point,
          value: point.value - 15 + Math.random() * 10, // Offset for different reading
        })),
        unit: '°C',
        source: 'TT-002',
        tension: 0.4,
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 2,
      },
    ],
    refreshInterval: 5000,
    autoRefresh: true,
    exportEnabled: true,
    timeRange: {
      start: new Date(Date.now() - 3600000), // 1 hour ago
      end: new Date(),
      preset: 'last-hour',
    },
  },
  {
    id: 'pressure-chart',
    title: 'Pressure Analysis',
    type: 'bar',
    datasets: [
      {
        id: 'pressure-sensor-1',
        name: 'PT-001 Main Pressure',
        label: 'PT-001 Main Pressure',
        data: generateMockData(20),
        unit: 'PSI',
        source: 'PT-001',
        backgroundColor: 'rgba(16, 185, 129, 0.7)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1,
      },
    ],
    refreshInterval: 10000,
    autoRefresh: true,
    exportEnabled: true,
    timeRange: {
      start: new Date(Date.now() - 1800000), // 30 minutes ago
      end: new Date(),
      preset: 'last-30min',
    },
  },
];

export default function AnalyticsDashboard() {
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);
  const [selectedChart, setSelectedChart] = useState<string>(
    mockChartConfigs[0].id
  );

  const {
    addDashboard,
    updatePreferences,
    setChartConfig,
    dashboards,
    setActiveDashboard,
    preferences,
  } = useAnalyticsStore();

  // Initialize dashboard if not set
  useEffect(() => {
    if (dashboards.length > 0 && dashboards[0]) {
      setActiveDashboard(dashboards[0].id);
    }
  }, [dashboards, setActiveDashboard]);

  // Initialize analytics store with mock data
  useEffect(() => {
    // Add mock dashboard
    addDashboard({
      id: 'main-dashboard',
      name: 'Main Analytics Dashboard',
      description: 'Primary dashboard for analytics monitoring and visualization',
      widgets: mockChartConfigs.map((config, index) => ({
        id: config.id,
        type: 'chart' as const,
        config: config as unknown as Record<string, unknown>,
        position: {
          x: (index % 2) * 6,
          y: Math.floor(index / 2) * 4,
          w: 6,
          h: 4,
        },
      })),
      layout: {
        columns: 12,
        rows: 8,
        gap: 10,
      },
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    // Set chart configurations
    mockChartConfigs.forEach((config) => {
      setChartConfig(config.id, config);
    });
  }, [addDashboard, setChartConfig]);

  const handleChartUpdate = (data: DataPoint[]) => {
    console.log('Chart data updated:', data.length, 'points');
  };

  const handleChartError = (error: string) => {
    console.error('Chart error:', error);
  };

  const toggleRealTime = () => {
    setIsRealTimeEnabled(!isRealTimeEnabled);
    updatePreferences({
      ...preferences,
      autoRefresh: !isRealTimeEnabled,
    });
  };

  const selectedChartConfig = mockChartConfigs.find(
    (config) => config.id === selectedChart
  );

  return (
    <div className='h-full flex flex-col bg-[#1e1e1e] text-[#cccccc] overflow-hidden'>
      {/* Dashboard Header */}
      <div className='flex-shrink-0 bg-[#2d2d30] border-b border-[#3c3c3c] p-4'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center space-x-3'>
            <BarChart3 className='w-6 h-6 text-[#007acc]' />
            <h1 className='text-xl font-semibold'>Analytics Dashboard</h1>
          </div>

          <div className='flex items-center space-x-3'>
            <button
              onClick={toggleRealTime}
              className='flex items-center space-x-2 px-3 py-1.5 bg-[#007acc] hover:bg-[#005a9e] rounded text-sm transition-colors'
            >
              {isRealTimeEnabled ? (
                <Pause className='w-4 h-4' />
              ) : (
                <Play className='w-4 h-4' />
              )}
              <span>{isRealTimeEnabled ? 'Pause' : 'Resume'} Real-time</span>
            </button>

            <button className='flex items-center space-x-2 px-3 py-1.5 bg-[#2d2d30] hover:bg-[#3c3c3c] border border-[#3c3c3c] rounded text-sm transition-colors'>
              <RotateCcw className='w-4 h-4' />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className='flex-1 overflow-hidden'>
        <div className='h-full grid grid-cols-1 lg:grid-cols-3 gap-4 p-4'>
          {/* Main Chart Area - 2/3 width */}
          <div className='lg:col-span-2 bg-[#252526] border border-[#3c3c3c] rounded-lg overflow-hidden'>
            <div className='p-4 border-b border-[#3c3c3c]'>
              <div className='flex items-center justify-between'>
                <h2 className='text-lg font-medium'>Real-time Analytics</h2>
                <select
                  value={selectedChart}
                  onChange={(e) => setSelectedChart(e.target.value)}
                  className='bg-[#2d2d30] border border-[#3c3c3c] rounded px-3 py-1 text-sm'
                >
                  {mockChartConfigs.map((config) => (
                    <option key={config.id} value={config.id}>
                      {config.title}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className='p-4 h-96'>
              {selectedChartConfig && (
                <AnalyticsChart
                  config={selectedChartConfig}
                  onDataUpdate={handleChartUpdate}
                  onError={handleChartError}
                  className='h-full'
                />
              )}
            </div>
          </div>

          {/* Right Sidebar - System Health */}
          <div className='space-y-4'>
            {/* System Health */}
            <div className='bg-[#252526] border border-[#3c3c3c] rounded-lg p-4'>
              <div className='flex items-center space-x-2 mb-4'>
                <Heart className='w-5 h-5 text-[#007acc]' />
                <h3 className='font-medium'>System Health</h3>
              </div>

              <SystemHealthDashboard />
            </div>

            {/* Quick Stats */}
            <div className='bg-[#252526] border border-[#3c3c3c] rounded-lg p-4'>
              <div className='flex items-center space-x-2 mb-4'>
                <Activity className='w-5 h-5 text-[#007acc]' />
                <h3 className='font-medium'>Live Metrics</h3>
              </div>

              <div className='space-y-3'>
                <div className='flex justify-between'>
                  <span className='text-[#969696]'>Active Sensors:</span>
                  <span className='text-[#cccccc]'>24</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-[#969696]'>Data Points/min:</span>
                  <span className='text-[#cccccc]'>1,247</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-[#969696]'>Alerts:</span>
                  <span className='text-yellow-400'>3</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-[#969696]'>Uptime:</span>
                  <span className='text-green-400'>99.8%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Historical Data Analysis Section */}
        <div className='border-t border-[#3c3c3c] bg-[#252526] p-4'>
          <div className='flex items-center space-x-2 mb-4'>
            <Clock className='w-5 h-5 text-[#007acc]' />
            <h3 className='font-medium'>Historical Data Analysis</h3>
          </div>

          <HistoricalDataAnalysis />
        </div>
      </div>
    </div>
  );
}

/**
 * AnalyticsDashboard Component
 *
 * @description Integrated analytics dashboard for MainContent router
 * @specification Adapts existing analytics-demo page for production use
 *
 * @features
 * - Real-time chart visualization with multiple data sources
 * - System health monitoring and status indicators
 * - Historical data analysis with filtering capabilities
 * - Interactive controls for real-time data management
 * - Responsive grid layout optimized for VS Code layout
 *
 * @integration
 * - Uses existing AnalyticsChart, SystemHealthDashboard, HistoricalDataAnalysis components
 * - Leverages existing analytics store for state management
 * - Maintains compatibility with existing 18KB analytics-demo implementation
 * - Optimized for MainContent router lazy loading
 *
 * @performance
 * - Mock data generation for development and testing
 * - Configurable refresh intervals for real-time updates
 * - Efficient state management with Zustand store
 * - Optimized re-renders with proper React patterns
 */
