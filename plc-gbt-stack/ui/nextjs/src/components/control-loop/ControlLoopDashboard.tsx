/**
 * Control Loop Dashboard - Phase 31.7 Main Component
 * AI Task Orchestrator Generated - Uses Enhanced Backend Infrastructure
 *
 * Primary dashboard container for industrial control loop management
 * Integrates with robust backend JSON schema framework from Phase 20
 * Follows user standards: React + TypeScript + Tailwind + Zod validation
 */

'use client';

import { AlertCircle, Filter, Plus, RefreshCw, Search, Settings } from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';

// Enhanced types and schemas
import { dashboardFiltersSchema } from '@/lib/schemas/control-loop.schemas';
import type { ControlLoopSummary, DashboardFilters } from '@/lib/types/control-loop.types';

// API client for backend integration
import { PLCGBTApiClient } from '@/lib/api/client';

// WebSocket integration for real-time updates
import { useWebSocket, type ControlLoopUpdateEvent } from '@/lib/websocket/websocket-client';

// Component imports (to be implemented)
import { ControlLoopFilters } from './ControlLoopFilters';
import { ControlLoopGrid } from './ControlLoopGrid';
import { ControlLoopStats } from './ControlLoopStats';
import { CreateControlLoopModal } from './CreateControlLoopModal';

// Mock data for development - will be replaced with API calls
const mockControlLoops: ControlLoopSummary[] = [
  {
    id: 'loop-001',
    name: 'Reactor Temperature Control',
    type: 'ladder_logic_advanced_pid',
    status: 'running',
    setpoint: 150.0,
    process_value: 149.8,
    control_output: 67.5,
    mode: 'Automatic',
    performance_score: 87.3,
    alarms_active: 0,
    last_updated: new Date('2025-01-17T10:30:00Z'),
  },
  {
    id: 'loop-002',
    name: 'Flow Rate Controller',
    type: 'function_block_standard_pide',
    status: 'running',
    setpoint: 250.0,
    process_value: 252.1,
    control_output: 42.8,
    mode: 'Automatic',
    performance_score: 94.1,
    alarms_active: 0,
    last_updated: new Date('2025-01-17T10:29:45Z'),
  },
  {
    id: 'loop_003',
    name: 'Pressure Relief System',
    type: 'ladder_logic_standard_pid',
    status: 'manual',
    setpoint: 85.0,
    process_value: 83.2,
    control_output: 38.5,
    mode: 'Manual',
    performance_score: 72.6,
    alarms_active: 1,
    last_updated: new Date('2025-01-17T10:28:12Z'),
  },
  {
    id: 'loop_004',
    name: 'Level Control Tank A',
    type: 'function_block_advanced_pide',
    status: 'error',
    setpoint: 75.0,
    process_value: 0.0,
    control_output: 0.0,
    mode: 'Override',
    performance_score: 0.0,
    alarms_active: 3,
    last_updated: new Date('2025-01-17T10:25:33Z'),
  },
];

interface ControlLoopDashboardProps {
  /** Optional initial filters to apply */
  readonly initialFilters?: Partial<DashboardFilters>;
  /** Whether to enable real-time updates */
  readonly enableRealTime?: boolean;
  /** Refresh interval in milliseconds */
  readonly refreshInterval?: number;
  /** Custom CSS class name */
  readonly className?: string;
}

/**
 * Main Control Loop Dashboard Component
 *
 * Provides comprehensive view of all control loops with:
 * - Real-time status updates
 * - Performance monitoring
 * - Filtering and search capabilities
 * - Quick actions (create, edit, tune)
 * - Alarm management
 */
export function ControlLoopDashboard({
  initialFilters = {},
  enableRealTime = true,
  refreshInterval = 5000,
  className = '',
}: ControlLoopDashboardProps) {
  // State management
  const [controlLoops, setControlLoops] = useState<ControlLoopSummary[]>(mockControlLoops);
  const [filters, setFilters] = useState<DashboardFilters>(initialFilters);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);

  // WebSocket integration for real-time updates
  const { connect: connectWS, subscribeToControlLoops, stopReconnection } = useWebSocket();

  // Ref to avoid dependency issues with fetchControlLoops in useEffect
  const fetchControlLoopsRef = useRef<(() => Promise<void>) | undefined>(undefined);

  // Filtered and searched control loops
  const filteredLoops = useMemo(() => {
    let filtered = controlLoops;

    // Apply status filter
    if (filters.status && filters.status.length > 0) {
      filtered = filtered.filter(loop => filters.status!.includes(loop.status));
    }

    // Apply type filter
    if (filters.type && filters.type.length > 0) {
      filtered = filtered.filter(loop => filters.type!.includes(loop.type));
    }

    // Apply performance threshold filter
    if (filters.performance_threshold !== undefined) {
      filtered = filtered.filter(loop => loop.performance_score >= filters.performance_threshold!);
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        loop =>
          loop.name.toLowerCase().includes(query) ||
          loop.id.toLowerCase().includes(query) ||
          loop.type.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [controlLoops, filters, searchQuery]);

  // Dashboard statistics
  const dashboardStats = useMemo(() => {
    const totalLoops = controlLoops.length;
    const runningLoops = controlLoops.filter(loop => loop.status === 'running').length;
    const errorLoops = controlLoops.filter(loop => loop.status === 'error').length;
    const totalAlarms = controlLoops.reduce((sum, loop) => sum + loop.alarms_active, 0);
    const avgPerformance =
      totalLoops > 0
        ? controlLoops.reduce((sum, loop) => sum + loop.performance_score, 0) / totalLoops
        : 0;

    return {
      totalLoops,
      runningLoops,
      errorLoops,
      totalAlarms,
      avgPerformance: Math.round(avgPerformance * 10) / 10,
    };
  }, [controlLoops]);

  // Quick connectivity check to avoid unnecessary API calls
  const checkBackendConnectivity = useCallback(async (): Promise<boolean> => {
    try {
      // Quick ping to backend health endpoint with short timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000); // 1 second timeout

      const response = await fetch('http://localhost:8000/api/v1/health', {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const isConnected = response.ok;
      setIsBackendConnected(isConnected);
      return isConnected;
    } catch {
      setIsBackendConnected(false);
      return false;
    }
  }, []);

  // Fetch control loops data
  const fetchControlLoops = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Use API client to fetch control loop instances
      const apiClient = new PLCGBTApiClient();
      const controlLoopInstances = await apiClient.getControlLoopInstances();

      // Transform instances to summary format (mapping API response to UI format)
      const summaryData: ControlLoopSummary[] = controlLoopInstances.map(instance => {
        // Extract parameters from the instance
        const params = instance.parameters || {};

        // Map API status to UI status - Fixed: Map active to running but prevent WebSocket flicker
        let mappedStatus: ControlLoopSummary['status'] = 'stopped';
        if (instance.status === 'active') {
          mappedStatus = 'running'; // Backend sends 'active', UI shows 'running'
        } else if (instance.status === 'error') {
          mappedStatus = 'error';
        } else if (instance.status === 'inactive') {
          mappedStatus = 'stopped';
        }

        // Map mode to ControlMode
        const validModes: ControlLoopSummary['mode'][] = [
          'Manual',
          'Automatic',
          'Cascade',
          'Override',
          'Program',
          'Ratio',
        ];
        const mappedMode = validModes.includes(params.mode as ControlLoopSummary['mode'])
          ? (params.mode as ControlLoopSummary['mode'])
          : 'Manual';

        return {
          id: instance.id,
          name: instance.name,
          type: (params.loop_type as ControlLoopSummary['type']) || 'ladder_logic_standard_pid',
          status: mappedStatus,
          setpoint: Number(params.setpoint) || 0,
          process_value: Number(params.process_value) || 0,
          control_output: Number(params.control_output) || 0,
          mode: mappedMode,
          performance_score: Number(params.performance_score) || 0,
          alarms_active: Number(params.alarms_active) || 0,
          last_updated: new Date(instance.updated_at),
        };
      });

      setControlLoops(summaryData);
      setLastRefresh(new Date());
    } catch (catchError) {
      // Suppress console error spam - only show user-friendly error once
      const errorMessage = 'Backend offline - using demo data';
      console.warn(
        '🔴 Backend connection failed:',
        catchError instanceof Error ? catchError.message : 'Unknown error'
      );
      // Fallback to mock data if API fails (offline mode)
      setControlLoops(mockControlLoops);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []); // Remove error dependency to prevent infinite loop

  // Update ref when fetchControlLoops changes
  fetchControlLoopsRef.current = fetchControlLoops;

  // Handle real-time updates - Fixed: Only update values, not status to prevent flicker
  const handleRealTimeUpdate = useCallback((event: ControlLoopUpdateEvent) => {
    console.log('🔄 Processing real-time update:', event); // Debug log

    setControlLoops(prev =>
      prev.map(loop =>
        loop.id === event.data.loop_id
          ? {
              ...loop,
              // REMOVED: Status updates that cause Active→Running flicker
              // Status should only change through explicit user actions, not value updates

              // Handle process value update - direct number from WebSocket
              ...(typeof event.data.updates.process_value === 'number' && {
                process_value: event.data.updates.process_value,
              }),
              // Handle control output update - direct number from WebSocket
              ...(typeof event.data.updates.control_output === 'number' && {
                control_output: event.data.updates.control_output,
              }),
              // Handle performance score if provided
              ...(typeof event.data.updates.performance_score === 'number' && {
                performance_score: event.data.updates.performance_score,
              }),
              // Update timestamp
              last_updated: new Date(event.timestamp),
            }
          : loop
      )
    );
  }, []);

  // Refs for other functions to avoid dependency issues
  const handleRealTimeUpdateRef = useRef(handleRealTimeUpdate);
  const connectWSRef = useRef(connectWS);
  const subscribeToControlLoopsRef = useRef(subscribeToControlLoops);
  const stopReconnectionRef = useRef(stopReconnection);
  const checkBackendConnectivityRef = useRef(checkBackendConnectivity);

  // Update other refs when functions change
  handleRealTimeUpdateRef.current = handleRealTimeUpdate;
  connectWSRef.current = connectWS;
  subscribeToControlLoopsRef.current = subscribeToControlLoops;
  stopReconnectionRef.current = stopReconnection;
  checkBackendConnectivityRef.current = checkBackendConnectivity;

  // Setup real-time updates with WebSocket integration
  useEffect(() => {
    console.log('🔧 Starting WebSocket setup...', { enableRealTime, error });

    if (!enableRealTime) {
      console.log('❌ WebSocket setup skipped - enableRealTime is false');
      return;
    }

    // Don't set up polling if we know the backend is offline
    if (error?.includes('offline') || error?.includes('Backend offline')) {
      console.info('⏸️ Skipping real-time setup - backend is offline');
      // Stop any ongoing WebSocket reconnection attempts
      stopReconnectionRef.current?.();
      return;
    }

    // Quick connectivity check before setting up WebSocket
    const setupRealTime = async () => {
      console.log('🔍 Checking backend connectivity...');
      const isBackendAvailable = await checkBackendConnectivityRef.current?.();
      console.log('🔍 Backend available:', isBackendAvailable);

      if (!isBackendAvailable) {
        console.info('⏸️ Skipping WebSocket setup - backend not reachable');
        stopReconnectionRef.current?.();
        return () => {}; // Return empty cleanup function
      }

      // Backend is available, proceed with WebSocket setup
      console.log('🚀 Backend available, setting up WebSocket connection...');
      return setupWebSocketConnection();
    };

    const setupWebSocketConnection = () => {
      console.log('⚙️ Setting up WebSocket connection...');

      // Track WebSocket connection state to avoid polling conflicts
      let isWebSocketConnected = false;
      let interval: NodeJS.Timeout | null = null;

      // Start with polling fallback - will be disabled if WebSocket connects
      const startPolling = () => {
        if (!isWebSocketConnected && !interval) {
          console.log('🔄 Starting polling fallback...');
          interval = setInterval(() => {
            fetchControlLoopsRef.current?.();
          }, refreshInterval);
        }
      };

      const stopPolling = () => {
        if (interval) {
          console.log('⏹️ Stopping polling (WebSocket connected)');
          clearInterval(interval);
          interval = null;
        }
      };

      // Start with polling as fallback
      startPolling();

      // Establish WebSocket connection for real-time updates
      console.log('🔌 Attempting WebSocket connection...');
      connectWSRef
        .current?.()
        .then(() => {
          console.log('✅ WebSocket connected - disabling polling to prevent data conflicts');
          isWebSocketConnected = true;
          stopPolling(); // Stop polling to prevent value oscillation
        })
        .catch(err => {
          console.info('ℹ️ WebSocket failed - continuing with polling fallback:', err);
          isWebSocketConnected = false;
          startPolling(); // Ensure polling continues if WebSocket fails
        });

      // Subscribe to control loop updates via WebSocket
      console.log('📡 Setting up WebSocket subscription...');
      const unsubscribe =
        subscribeToControlLoopsRef.current?.((event: ControlLoopUpdateEvent) => {
          console.log('📡 Real-time control loop update received:', event);

          // Track WebSocket activity for health monitoring
          (window as Window & { lastWebSocketUpdate?: number }).lastWebSocketUpdate = Date.now();

          // Ensure WebSocket is still considered connected when receiving data
          if (!isWebSocketConnected) {
            console.log('🔄 WebSocket data received - stopping polling to prevent conflicts');
            isWebSocketConnected = true;
            stopPolling();
          }

          // Pass WebSocket event directly to update handler
          handleRealTimeUpdateRef.current?.(event);
        }) ||
        (() => {
          console.log('❌ Failed to set up WebSocket subscription');
        });

      // Monitor for WebSocket disconnections to restart polling
      const monitorWebSocketHealth = () => {
        // Initialize timestamp
        (window as Window & { lastWebSocketUpdate?: number }).lastWebSocketUpdate = Date.now();

        const healthInterval = setInterval(() => {
          // If we haven't received data for a while and WebSocket was connected, restart polling
          // This is a fallback mechanism in case WebSocket silently fails
          const now = Date.now();
          const lastUpdate =
            (window as Window & { lastWebSocketUpdate?: number }).lastWebSocketUpdate || now;
          const timeSinceLastUpdate = now - lastUpdate;

          if (isWebSocketConnected && timeSinceLastUpdate > refreshInterval * 2) {
            console.log('⚠️ WebSocket appears stale - restarting polling as backup');
            isWebSocketConnected = false;
            startPolling();
          }
        }, refreshInterval);

        return () => clearInterval(healthInterval);
      };

      const stopHealthMonitoring = monitorWebSocketHealth();

      return () => {
        // Cleanup function to handle polling, WebSocket, and health monitoring
        if (interval) {
          clearInterval(interval);
        }
        if (unsubscribe) {
          unsubscribe();
        }
        if (stopHealthMonitoring) {
          stopHealthMonitoring();
        }
        console.log('🧹 WebSocket, polling, and health monitoring cleanup completed');
      };
    };

    // Setup real-time with cleanup handling
    let cleanup: (() => void) | null = null;

    setupRealTime()
      .then(cleanupFn => {
        cleanup = cleanupFn;
      })
      .catch(err => {
        console.warn('Real-time setup failed:', err);
      });

    return () => {
      if (cleanup) {
        cleanup();
      }
    };
  }, [enableRealTime, refreshInterval, error]); // Only include primitive values, not functions

  // Separate effect to stop WebSocket reconnection when backend goes offline
  useEffect(() => {
    if (error?.includes('offline') || error?.includes('Backend offline')) {
      console.info('🛑 Stopping WebSocket reconnection - backend is offline');
      stopReconnectionRef.current?.();
    }
  }, [error]);

  // Initial data load with connectivity check
  useEffect(() => {
    const initializeData = async () => {
      console.log('🔍 Checking backend connectivity...');
      const isBackendAvailable = await checkBackendConnectivityRef.current?.();

      if (isBackendAvailable) {
        console.log('✅ Backend available - loading data');
        fetchControlLoops();
      } else {
        console.log('⚠️ Backend offline - using demo data immediately');
        setControlLoops(mockControlLoops);
        setError('Backend offline - using demo data');
        setIsLoading(false);
        // Prevent WebSocket connection attempts
        stopReconnectionRef.current?.();
      }
    };

    initializeData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only once on mount

  // Handle filter changes
  const handleFiltersChange = useCallback((newFilters: DashboardFilters) => {
    try {
      const validatedFilters = dashboardFiltersSchema.parse(newFilters);
      setFilters(validatedFilters);
    } catch (err) {
      console.error('Invalid filters:', err);
      setError('Invalid filter configuration');
    }
  }, []);

  // Handle search change
  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  // Handle manual refresh
  const handleRefresh = useCallback(() => {
    fetchControlLoopsRef.current?.();
  }, []);

  // Control loop action handlers
  const handleStartLoop = useCallback(async (loopId: string) => {
    console.log(`🟢 Starting control loop: ${loopId}`);
    try {
      const apiClient = new PLCGBTApiClient();
      await apiClient.updateControlLoopInstance(loopId, { status: 'active' });
      // Refresh data to show updated status
      fetchControlLoopsRef.current?.();
    } catch (error) {
      console.error('Failed to start loop:', error);
    }
  }, []);

  const handleStopLoop = useCallback(async (loopId: string) => {
    console.log(`🔴 Stopping control loop: ${loopId}`);
    try {
      const apiClient = new PLCGBTApiClient();
      await apiClient.updateControlLoopInstance(loopId, { status: 'inactive' });
      // Refresh data to show updated status
      fetchControlLoopsRef.current?.();
    } catch (error) {
      console.error('Failed to stop loop:', error);
    }
  }, []);

  const handleEditLoop = useCallback((loopId: string) => {
    console.log(`✏️ Editing control loop: ${loopId}`);
    // TODO: Open edit modal or navigate to edit page
    alert(`Edit loop ${loopId} - Modal to be implemented`);
  }, []);

  const handleTuneLoop = useCallback(
    (loopId: string) => {
      console.log(`🔧 Adding control loop to tuning queue: ${loopId}`);

      // Find the loop to add to tuning queue
      const loopToTune = controlLoops.find(loop => loop.id === loopId);
      if (!loopToTune) {
        console.error('Loop not found:', loopId);
        return;
      }

      // TODO: Integrate with Control Loop Panel tuning queue
      // This should:
      // 1. Add the loop to the tuning queue in ControlLoopPanel state
      // 2. Switch to the Control Loop tool in the left sidebar
      // 3. Set the added loop as the focus loop

      // For now, provide user feedback about the action
      console.log('Loop added to tuning queue:', {
        id: loopToTune.id,
        name: loopToTune.name,
        type: loopToTune.type,
        currentStatus: loopToTune.status,
      });

      // Placeholder notification - replace with proper tuning queue integration
      alert(
        `Added "${loopToTune.name}" to tuning queue.\n\nNext steps:\n1. Switch to Control Loop panel in sidebar\n2. Loop will appear in Active Loops dropdown\n3. Use keyboard arrows or dropdown to focus\n4. Adjust PID parameters as needed\n\n[Integration with ControlLoopPanel pending]`
      );
    },
    [controlLoops]
  );

  const handleSetpointChange = useCallback(async (loopId: string, value: number) => {
    console.log(`📈 Updating setpoint for ${loopId}: ${value}`);
    try {
      const apiClient = new PLCGBTApiClient();
      await apiClient.updateControlLoopInstance(loopId, { parameters: { setpoint: value } });
      // Update local state immediately for responsive UI
      setControlLoops(prev =>
        prev.map(loop => (loop.id === loopId ? { ...loop, setpoint: value } : loop))
      );
    } catch (error) {
      console.error('Failed to update setpoint:', error);
      // Revert local change on error
      fetchControlLoopsRef.current?.();
    }
  }, []);

  return (
    <div className={`h-full w-full flex flex-col bg-[#1e1e1e] text-white ${className}`}>
      {/* Header - Dynamic Responsive Design with Flex Scaling */}
      <div className="flex items-stretch justify-between min-h-[4rem] max-h-[6rem] p-4 border-b border-[#3c3c3c] gap-4">
        {/* Left Section - Dynamic Title and Status */}
        <div className="flex items-center min-w-0 flex-1 space-x-3 overflow-hidden pr-4">
          <h1
            className="font-semibold text-white flex-shrink-0 leading-tight"
            style={{
              fontSize: 'clamp(1rem, 2.5vw, 1.5rem)',
              maxWidth: 'min(50vw, 20rem)',
              lineHeight: '1.2',
            }}
          >
            Control Loop Dashboard
          </h1>

          {/* Status Indicators - Dynamic Responsive Layout */}
          <div className="flex items-center gap-1 sm:gap-2 lg:gap-3 min-w-0 overflow-hidden flex-shrink">
            {/* Backend Connectivity Indicator */}
            <div className="flex items-center space-x-1 sm:space-x-1.5 lg:space-x-2 flex-shrink-0">
              <div
                className={`w-2 h-2 lg:w-2.5 lg:h-2.5 rounded-full transition-colors ${
                  isBackendConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span
                className={`font-medium transition-colors whitespace-nowrap ${
                  isBackendConnected ? 'text-green-400' : 'text-red-400'
                }`}
                style={{
                  fontSize: 'clamp(0.75rem, 1.5vw, 0.875rem)',
                }}
              >
                {isBackendConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Last Updated - Responsive visibility and sizing */}
            <div className="hidden lg:flex items-center space-x-1.5 lg:space-x-2 text-gray-400 flex-shrink min-w-0">
              <span
                className="font-medium whitespace-nowrap"
                style={{ fontSize: 'clamp(0.7rem, 1.2vw, 0.875rem)' }}
              >
                Last updated:
              </span>
              <span
                className="text-gray-300 whitespace-nowrap truncate"
                style={{ fontSize: 'clamp(0.7rem, 1.2vw, 0.875rem)' }}
              >
                {lastRefresh.toLocaleTimeString()}
              </span>
              {isLoading && (
                <RefreshCw className="w-3 h-3 lg:w-4 lg:h-4 animate-spin text-blue-400 flex-shrink-0" />
              )}
            </div>

            {/* Compact Last Updated for medium screens */}
            <div className="hidden md:flex lg:hidden items-center space-x-1.5 text-gray-400 flex-shrink-0">
              <span
                className="text-gray-300 whitespace-nowrap"
                style={{ fontSize: 'clamp(0.7rem, 1.2vw, 0.8rem)' }}
              >
                {lastRefresh.toLocaleTimeString()}
              </span>
              {isLoading && <RefreshCw className="w-3 h-3 animate-spin text-blue-400" />}
            </div>
          </div>
        </div>

        {/* Right Section - Dynamic Actions and Controls */}
        <div className="flex items-center gap-1 sm:gap-2 lg:gap-3 flex-shrink-0 min-w-fit">
          {/* Search - Dynamic Responsive Width */}
          <div className="relative hidden lg:block flex-shrink-0">
            <Search
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              style={{
                width: 'clamp(0.875rem, 1.2vw, 1rem)',
                height: 'clamp(0.875rem, 1.2vw, 1rem)',
              }}
            />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={e => handleSearchChange(e.target.value)}
              className="pl-10 pr-4 py-2 bg-[#2d2d2d] border border-[#3c3c3c] rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              style={{
                width: 'clamp(7rem, 12vw, 14rem)',
                minWidth: '7rem',
                fontSize: 'clamp(0.75rem, 1.1vw, 0.875rem)',
              }}
            />
          </div>

          {/* Mobile Search Button */}
          <button
            className="md:hidden p-2 bg-[#2d2d2d] border border-[#3c3c3c] rounded-md text-gray-300 hover:bg-[#3c3c3c] transition-colors"
            title="Search"
          >
            <Search className="w-4 h-4" />
          </button>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-md border transition-all duration-200 ${
              showFilters
                ? 'bg-blue-600 border-blue-500 text-white shadow-md'
                : 'bg-[#2d2d2d] border-[#3c3c3c] text-gray-300 hover:bg-[#3c3c3c] hover:border-[#4c4c4c]'
            }`}
            title="Toggle Filters"
          >
            <Filter className="w-4 h-4" />
          </button>

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="p-2 bg-[#2d2d2d] border border-[#3c3c3c] rounded-md text-gray-300 hover:bg-[#3c3c3c] hover:border-[#4c4c4c] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            title="Refresh Data"
          >
            <RefreshCw
              className={`w-4 h-4 transition-transform ${isLoading ? 'animate-spin' : ''}`}
            />
          </button>

          {/* Settings Button - Hidden on small screens */}
          <button
            className="hidden lg:block p-2 bg-[#2d2d2d] border border-[#3c3c3c] rounded-md text-gray-300 hover:bg-[#3c3c3c] hover:border-[#4c4c4c] transition-all duration-200"
            title="Dashboard Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* Create New Loop Button - Dynamic Responsive */}
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-3 lg:px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-all duration-200 hover:shadow-lg flex-shrink-0"
          >
            <Plus className="w-4 h-4 flex-shrink-0" />
            <span
              className="hidden sm:inline font-medium"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 1rem)' }}
            >
              Create Loop
            </span>
            <span
              className="sm:hidden font-medium"
              style={{ fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)' }}
            >
              Add
            </span>
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-900/20 border border-red-500 rounded-md flex items-center space-x-2 text-red-400">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-300"
          >
            ×
          </button>
        </div>
      )}

      {/* Dashboard Stats */}
      <ControlLoopStats stats={dashboardStats} className="m-4" />

      {/* Filters Panel */}
      {showFilters && (
        <ControlLoopFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          className="mx-4 mb-4"
        />
      )}

      {/* Main Content */}
      <div className="flex-1 p-4 overflow-hidden">
        <ControlLoopGrid
          controlLoops={filteredLoops}
          isLoading={isLoading}
          onRefresh={handleRefresh}
          onStart={handleStartLoop}
          onStop={handleStopLoop}
          onEdit={handleEditLoop}
          onTune={handleTuneLoop}
          onSetpointChange={handleSetpointChange}
          className="h-full"
        />
      </div>

      {/* Create Control Loop Modal */}
      {isCreateModalOpen && (
        <CreateControlLoopModal
          onClose={() => setIsCreateModalOpen(false)}
          onCreated={newLoop => {
            setControlLoops(prev => [...prev, newLoop]);
            setIsCreateModalOpen(false);
          }}
        />
      )}
    </div>
  );
}

export default ControlLoopDashboard;
