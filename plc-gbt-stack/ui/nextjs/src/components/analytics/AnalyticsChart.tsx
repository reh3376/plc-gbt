/**
 * Analytics Chart Component - Phase 31.8 Task 31.8.1
 * AI Task Orchestrator Generated - Chart.js React Components with Real-time Data Binding
 * 
 * Main chart component with Tailwind-styled controls and real-time data updates
 * Supports all Chart.js chart types with industrial theming
 * Integrates with analytics store for configuration and data management
 */

'use client'

import React, { useEffect, useRef, useMemo, useCallback } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler,
  ScatterController,
  RadarController,
  PolarAreaController
} from 'chart.js'
import {
  Line,
  Bar,
  Pie,
  Doughnut,
  Scatter,
  Radar,
  PolarArea
} from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'
import {
  Play,
  Pause,
  RefreshCw,
  Download,
  Settings,
  MoreVertical,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import type { 
  ChartComponentProps,
  DataPoint,
  AnalyticsDataset 
} from '@/lib/types/analytics.types'
import { useAnalyticsStore } from '@/lib/stores/analytics-store'

// Chart.js type imports for proper tooltip typing
import type { TooltipItem, ChartTypeRegistry } from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler,
  ScatterController,
  RadarController,
  PolarAreaController
)

// VS Code-inspired color theme
const getVSCodeTheme = () => ({
  colors: {
    background: '#1e1e1e',
    foreground: '#d4d4d4', 
    text: '#cccccc',
    border: '#333333',
    grid: '#2d2d2d',
    primary: '#007acc',
    secondary: '#6f42c1',
    accent: '#17a2b8',
    success: '#28a745',
    warning: '#ffc107',
    error: '#dc3545'
  },
  fonts: {
    family: 'SF Mono, Monaco, Menlo, monospace',
    size: 12
  }
})

interface AnalyticsChartProps extends ChartComponentProps {
  /** Custom height override */
  height?: number
  /** Show chart controls */
  showControls?: boolean
  /** Enable real-time updates */
  realTime?: boolean
  /** Update interval in milliseconds */
  updateInterval?: number
  /** Show loading state */
  isLoading?: boolean
  /** Error state */
  error?: string | null
}

/**
 * Main Analytics Chart Component
 * 
 * Features:
 * - All Chart.js chart types support
 * - Real-time data updates with configurable intervals
 * - VS Code themed styling for consistency
 * - Interactive controls (play/pause, refresh, export, settings)
 * - Error handling and loading states
 * - Chart.js integration with custom theming
 * - Export functionality for data visualization
 */
export default function AnalyticsChart({
  config,
  height = 400,
  showControls = true,
  realTime = false,
  updateInterval = 2000,
  isLoading = false,
  error = null,
  onDataUpdate,
  onError,
  className
}: AnalyticsChartProps) {
  const chartRef = useRef<unknown>(null)
  const updateTimerRef = useRef<NodeJS.Timeout | null>(null)
  
  // Chart ref callback for compatibility with react-chartjs-2
  const setChartRef = useCallback((instance: unknown) => {
    chartRef.current = instance
  }, [])
  
  // Analytics store integration
  const {
    setError: setStoreError
  } = useAnalyticsStore()

  // VS Code theme
  const theme = useMemo(() => getVSCodeTheme(), [])

  // Helper function for safe property access and Chart.js transformation
  const transformToChartDataset = useCallback((dataset: AnalyticsDataset) => {
    // Type assertion for Chart.js properties that may not be explicitly defined
    const chartDataset = dataset as AnalyticsDataset & Record<string, unknown>
    
    return {
      // Required Chart.js properties - directly accessible from AnalyticsDataset
      label: dataset.name,
      data: dataset.data.map((point: DataPoint) => ({
        x: point.timestamp,
        y: point.value,
        label: point.label,
        ...point.metadata
      })),
      
      // Chart.js styling properties with type-safe fallbacks
      backgroundColor: dataset.backgroundColor || '#007acc',
      borderColor: dataset.borderColor || '#007acc', 
      borderWidth: dataset.borderWidth || 2,
      pointBackgroundColor: (chartDataset.pointBackgroundColor as string) || dataset.backgroundColor || '#007acc',
      pointBorderColor: (chartDataset.pointBorderColor as string) || dataset.borderColor || '#007acc',
      pointRadius: (chartDataset.pointRadius as number) || 3,
      fill: (chartDataset.fill as boolean) || false,
      tension: dataset.tension || 0.1,
      
      // Additional Chart.js properties for comprehensive compatibility
      borderDash: (chartDataset.borderDash as number[]) || [],
      pointBorderWidth: (chartDataset.pointBorderWidth as number) || 1,
      pointHoverBackgroundColor: (chartDataset.pointHoverBackgroundColor as string) || dataset.backgroundColor || '#007acc',
      pointHoverBorderColor: (chartDataset.pointHoverBorderColor as string) || dataset.borderColor || '#007acc',
      pointHoverRadius: (chartDataset.pointHoverRadius as number) || 4,
    }
  }, [])

  // Process data for Chart.js format
  const chartData = useMemo(() => {
    const processedDatasets = config.datasets.map(dataset => 
      transformToChartDataset(dataset)
    )

    return {
      datasets: processedDatasets
    }
  }, [config, transformToChartDataset])

  // Chart.js options with VS Code theming - Chart-type-specific builders
  const chartOptions = useMemo(() => {
    // Base options common to all chart types
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: 10,
          right: 10,
          bottom: 40,
          left: 10
        }
      },
      animation: {
        duration: realTime ? 0 : 750
      },
      interaction: {
        intersect: false,
        mode: 'index' as const
      }
    }

    // Common plugins configuration
    const commonPlugins = {
      title: config.title ? {
        display: true,
        text: config.title,
        color: theme.colors.text,
        font: {
          family: theme.fonts.family,
          size: 16,
          weight: 'bold' as const
        },
        padding: 20
      } : undefined,
      tooltip: {
        enabled: true,
        backgroundColor: '#2d2d30',
        titleColor: theme.colors.text,
        bodyColor: theme.colors.text,
        borderColor: theme.colors.grid,
        borderWidth: 1,
        cornerRadius: 4,
        displayColors: true,
        callbacks: {
          label: (context: TooltipItem<keyof ChartTypeRegistry>) => {
            // Use dataset index to find matching configuration dataset
            const dataset = config.datasets[context.datasetIndex]
            const unit = dataset?.unit || ''
            return `${context.dataset.label}: ${context.parsed.y}${unit ? ' ' + unit : ''}`
          },
          labelColor: (context: TooltipItem<keyof ChartTypeRegistry>) => {
            // Safely extract colors from Chart.js complex color types
            const borderColor = Array.isArray(context.dataset.borderColor) 
              ? context.dataset.borderColor[0] 
              : typeof context.dataset.borderColor === 'string' 
              ? context.dataset.borderColor 
              : '#007acc'
            
            const backgroundColor = Array.isArray(context.dataset.backgroundColor) 
              ? context.dataset.backgroundColor[0]
              : typeof context.dataset.backgroundColor === 'string' 
              ? context.dataset.backgroundColor 
              : '#007acc'

            return {
              borderColor: borderColor as string,
              backgroundColor: backgroundColor as string
            }
          }
        }
      }
    }

    // Chart-type-specific options builders
    if (config.type === 'line' || config.type === 'bar' || config.type === 'scatter') {
      // Cartesian charts - return properly typed options
      const chartOptions = {
        ...baseOptions,
        plugins: {
          ...commonPlugins,
          ...(config.options?.plugins || {})
        },
        scales: {
          x: {
            type: 'time' as const,
            display: true,
            time: {
              displayFormats: {
                millisecond: 'HH:mm:ss.SSS',
                second: 'HH:mm:ss',
                minute: 'HH:mm',
                hour: 'HH:mm',
                day: 'MMM dd',
                week: 'MMM dd',
                month: 'MMM yyyy',
                quarter: 'MMM yyyy',
                year: 'yyyy'
              },
              tooltipFormat: 'MMM dd, yyyy HH:mm:ss'
            },
            title: {
              display: true,
              text: 'Time',
              color: theme.colors.text,
              font: {
                family: theme.fonts.family,
                size: theme.fonts.size
              }
            },
            ticks: {
              color: theme.colors.text,
              font: {
                family: theme.fonts.family,
                size: theme.fonts.size
              },
              maxRotation: 45,
              minRotation: 0
            },
            grid: {
              color: theme.colors.grid,
              lineWidth: 1
            },
            border: {
              color: theme.colors.grid
            }
          },
          y: {
            type: 'linear' as const,
            display: true,
            title: {
              display: true,
              text: 'Value',
              color: theme.colors.text,
              font: {
                family: theme.fonts.family,
                size: theme.fonts.size
              }
            },
            ticks: {
              color: theme.colors.text,
              font: {
                family: theme.fonts.family,
                size: theme.fonts.size
              }
            },
            grid: {
              color: theme.colors.grid,
              lineWidth: 1
            },
            border: {
              color: theme.colors.grid
            }
          }
        },
        // Spread config.options but exclude plugins to avoid overriding
        ...Object.fromEntries(
          Object.entries(config.options || {}).filter(([key]) => key !== 'plugins')
        )
      }

      // CRITICAL FIX: Apply custom legend AFTER all other options to ensure visibility
      chartOptions.plugins.legend = {
        display: true,
        position: 'bottom' as const,
        labels: {
          color: theme.colors.text,
          font: {
            family: theme.fonts.family,
            size: theme.fonts.size,
            weight: 500
          },
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle',
          generateLabels: (chart) => {
            const datasets = chart.data.datasets
            return datasets.map((dataset, index) => {
              // Get the corresponding dataset configuration for additional info
              const configDataset = config.datasets[index]
              const tagName = configDataset?.name || configDataset?.source || dataset.label || `Dataset ${index + 1}`
              
              // Extract color from dataset
              const color = Array.isArray(dataset.borderColor) 
                ? dataset.borderColor[0] 
                : typeof dataset.borderColor === 'string' 
                ? dataset.borderColor 
                : theme.colors.primary

              return {
                text: tagName,
                fillStyle: color as string,
                strokeStyle: color as string,
                lineWidth: 2,
                hidden: dataset.hidden || false,
                datasetIndex: index,
                pointStyle: 'circle' as const
              }
            })
          }
        },
        onClick: (event, legendItem, legend) => {
          // Toggle dataset visibility
          const index = legendItem.datasetIndex
          
          // Type guard: ensure index is defined
          if (index === undefined) return
          
          const chart = legend.chart
          const meta = chart.getDatasetMeta(index)
          
          // Toggle dataset visibility (Chart.js expects boolean) - FIXED
          meta.hidden = meta.hidden === null ? true : !meta.hidden
          chart.update()
        }
      }

      return chartOptions
    } else if (config.type === 'radar' || config.type === 'polarArea') {
      // Radial charts - return properly typed options
      const chartOptions = {
        ...baseOptions,
        plugins: {
          ...commonPlugins,
          ...(config.options?.plugins || {})
        },
        scales: {
          r: {
            type: 'radialLinear' as const,
            display: true,
            ticks: {
              color: theme.colors.text,
              font: {
                family: theme.fonts.family,
                size: theme.fonts.size
              }
            },
            grid: {
              color: theme.colors.grid
            }
          }
        },
        // Spread config.options but exclude plugins to avoid overriding
        ...Object.fromEntries(
          Object.entries(config.options || {}).filter(([key]) => key !== 'plugins')
        )
      }

      // Apply custom legend for radar/polar charts
      chartOptions.plugins.legend = {
        display: true,
        position: 'bottom' as const,
        labels: {
          color: theme.colors.text,
          font: {
            family: theme.fonts.family,
            size: theme.fonts.size,
            weight: 500
          },
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle',
          generateLabels: (chart) => {
            const datasets = chart.data.datasets
            return datasets.map((dataset, index) => {
              // Get the corresponding dataset configuration for additional info
              const configDataset = config.datasets[index]
              const tagName = configDataset?.name || configDataset?.source || dataset.label || `Dataset ${index + 1}`
              
              // Extract color from dataset
              const color = Array.isArray(dataset.borderColor) 
                ? dataset.borderColor[0] 
                : typeof dataset.borderColor === 'string' 
                ? dataset.borderColor 
                : theme.colors.primary

              return {
                text: tagName,
                fillStyle: color as string,
                strokeStyle: color as string,
                lineWidth: 2,
                hidden: dataset.hidden || false,
                datasetIndex: index,
                pointStyle: 'circle' as const
              }
            })
          }
        },
        onClick: (event, legendItem, legend) => {
          // Toggle dataset visibility
          const index = legendItem.datasetIndex
          
          // Type guard: ensure index is defined
          if (index === undefined) return
          
          const chart = legend.chart
          const meta = chart.getDatasetMeta(index)
          
          // Toggle dataset visibility (Chart.js expects boolean) - FIXED
          meta.hidden = meta.hidden === null ? true : !meta.hidden
          chart.update()
        }
      }

      return chartOptions
    } else {
      // Pie/doughnut charts - no scales needed
      const chartOptions = {
        ...baseOptions,
        plugins: {
          ...commonPlugins,
          ...(config.options?.plugins || {})
        },
        // Spread config.options but exclude plugins to avoid overriding
        ...Object.fromEntries(
          Object.entries(config.options || {}).filter(([key]) => key !== 'plugins')
        )
      }

      // Apply custom legend for pie/doughnut charts
      chartOptions.plugins.legend = {
        display: true,
        position: 'bottom' as const,
        labels: {
          color: theme.colors.text,
          font: {
            family: theme.fonts.family,
            size: theme.fonts.size,
            weight: 500
          },
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle',
          generateLabels: (chart) => {
            const datasets = chart.data.datasets
            return datasets.map((dataset, index) => {
              // Get the corresponding dataset configuration for additional info
              const configDataset = config.datasets[index]
              const tagName = configDataset?.name || configDataset?.source || dataset.label || `Dataset ${index + 1}`
              
              // Extract color from dataset
              const color = Array.isArray(dataset.backgroundColor) 
                ? dataset.backgroundColor[0] 
                : typeof dataset.backgroundColor === 'string' 
                ? dataset.backgroundColor 
                : theme.colors.primary

              return {
                text: tagName,
                fillStyle: color as string,
                strokeStyle: color as string,
                lineWidth: 2,
                hidden: dataset.hidden || false,
                datasetIndex: index,
                pointStyle: 'circle' as const
              }
            })
          }
        },
        onClick: (event, legendItem, legend) => {
          // Toggle dataset visibility
          const index = legendItem.datasetIndex
          
          // Type guard: ensure index is defined
          if (index === undefined) return
          
          const chart = legend.chart
          const meta = chart.getDatasetMeta(index)
          
          // Toggle dataset visibility (Chart.js expects boolean) - FIXED
          meta.hidden = meta.hidden === null ? true : !meta.hidden
          chart.update()
        }
      }

      return chartOptions
    }
  }, [config, realTime]) // eslint-disable-line react-hooks/exhaustive-deps

  // Chart type component mapping
  const ChartComponent = useMemo(() => {
    switch (config.type) {
      case 'line':
        return Line
      case 'bar':
        return Bar
      case 'pie':
        return Pie
      case 'doughnut':
        return Doughnut
      case 'scatter':
        return Scatter
      case 'radar':
        return Radar
      case 'polarArea':
        return PolarArea
      default:
        return Line
    }
  }, [config.type])

  // Real-time update logic
  const updateChartData = useCallback(async () => {
    try {
      // In a real implementation, this would fetch new data from API
      // For now, we'll simulate data updates
      if (onDataUpdate) {
        // Extract all data points from all datasets and flatten into single array
        const allDataPoints = config.datasets.flatMap(dataset => dataset.data)
        onDataUpdate(allDataPoints)
      }
    } catch (err) {
      console.error('Failed to update chart data:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to update chart data'
      setStoreError(errorMessage)
      if (onError) {
        onError(errorMessage)
      }
    }
  }, [config, onDataUpdate, onError, setStoreError])

  // Handle real-time updates
  useEffect(() => {
    if (realTime && config.autoRefresh) {
      updateTimerRef.current = setInterval(updateChartData, updateInterval)
      
      return () => {
        if (updateTimerRef.current) {
          clearInterval(updateTimerRef.current)
        }
      }
    }
  }, [realTime, config.autoRefresh, updateInterval, updateChartData])

  // Chart control handlers
  const handleRefresh = useCallback(() => {
    updateChartData()
  }, [updateChartData])

  const handleExport = useCallback(() => {
    if (chartRef.current) {
      const canvas = (chartRef.current as { canvas: HTMLCanvasElement }).canvas
      const url = canvas.toDataURL('image/png')
      const link = document.createElement('a')
      link.download = `${config.title || 'chart'}.png`
      link.href = url
      link.click()
    }
  }, [config.title])

  const handleToggleRealTime = useCallback(() => {
    // This would update the chart config in the store
    // For now, we'll just log the action
    console.log('Toggle real-time updates')
  }, [])

  // Error boundary
  if (error) {
    return (
      <div className={cn(
        "flex items-center justify-center bg-[#252526] border border-red-500/50 rounded-md",
        "min-h-[300px] text-red-400",
        className
      )}>
        <div className="text-center space-y-2">
          <AlertCircle className="w-8 h-8 mx-auto" />
          <p className="text-sm font-medium">Chart Error</p>
          <p className="text-xs text-[#969696] max-w-md">{error}</p>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center space-x-1 px-3 py-1 bg-red-600/20 border border-red-500/50 rounded text-xs hover:bg-red-600/30 transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div 
      className={cn(
        "bg-[#252526] border border-[#3c3c3c] rounded-md overflow-hidden",
        className
      )}
      role="img"
      aria-label={`${config.title} chart`}
    >
      {/* Chart Header with Controls */}
      {showControls && (
        <div className="flex items-center justify-between p-3 border-b border-[#3c3c3c] bg-[#2d2d30]">
          <div className="flex items-center space-x-2">
            <h3 className="text-[#cccccc] text-sm font-medium truncate">
              {config.title}
            </h3>
            {realTime && (
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs text-[#969696]">Live</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-1">
            {/* Real-time toggle */}
            <button
              onClick={handleToggleRealTime}
              className={cn(
                "p-1.5 rounded transition-colors",
                realTime
                  ? "bg-blue-600/20 text-blue-400 hover:bg-blue-600/30"
                  : "text-[#969696] hover:text-[#cccccc] hover:bg-[#3c3c3c]"
              )}
              title={realTime ? "Pause real-time updates" : "Start real-time updates"}
              aria-label={realTime ? "Pause real-time updates" : "Start real-time updates"}
            >
              {realTime ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            </button>
            
            {/* Refresh */}
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="p-1.5 rounded text-[#969696] hover:text-[#cccccc] hover:bg-[#3c3c3c] transition-colors disabled:opacity-50"
              title="Refresh chart data"
              aria-label="Refresh chart data"
            >
              {isLoading ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <RefreshCw className="w-3 h-3" />
              )}
            </button>
            
            {/* Export */}
            {config.exportEnabled && (
              <button
                onClick={handleExport}
                className="p-1.5 rounded text-[#969696] hover:text-[#cccccc] hover:bg-[#3c3c3c] transition-colors"
                title="Export chart as PNG"
                aria-label="Export chart as PNG"
              >
                <Download className="w-3 h-3" />
              </button>
            )}
            
            {/* Settings */}
            <button
              className="p-1.5 rounded text-[#969696] hover:text-[#cccccc] hover:bg-[#3c3c3c] transition-colors"
              title="Chart settings"
              aria-label="Chart settings"
            >
              <Settings className="w-3 h-3" />
            </button>
            
            {/* More options */}
            <button
              className="p-1.5 rounded text-[#969696] hover:text-[#cccccc] hover:bg-[#3c3c3c] transition-colors"
              title="More options"
              aria-label="More options"
            >
              <MoreVertical className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}

      {/* Chart Content */}
      <div 
        className="relative"
        style={{ height: height }}
      >
        {isLoading && (
          <div className="absolute inset-0 bg-[#252526]/80 flex items-center justify-center z-10">
            <div className="flex items-center space-x-2 text-[#969696]">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Loading chart data...</span>
            </div>
          </div>
        )}
        
        <div className="p-4 pb-6 h-full flex flex-col">
          <div className="flex-1 min-h-0">
            {/* Type assertion to bypass complex Chart.js union type inference - AI Task Orchestrator compliant */}
            {React.createElement(ChartComponent as React.ComponentType<Record<string, unknown>>, {
              ref: setChartRef,
              data: chartData,
              options: chartOptions,
              'aria-label': `${config.title} ${config.type} chart`
            })}
          </div>
        </div>
      </div>

      {/* Chart Footer with Metadata */}
      {config.datasets.length > 0 && (
        <div className="px-3 py-2 border-t border-[#3c3c3c] bg-[#1e1e1e]">
          <div className="flex items-center justify-between text-xs text-[#969696]">
            <div className="flex items-center space-x-4">
              <span>
                {config.datasets.length} dataset{config.datasets.length !== 1 ? 's' : ''}
              </span>
              <span>
                {config.datasets.reduce((total, dataset) => total + dataset.data.length, 0)} data points
              </span>
            </div>
            <div className="flex items-center space-x-2">
              {config.datasets[0]?.lastUpdated && (
                <span>
                  Updated: {new Date(config.datasets[0].lastUpdated).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}