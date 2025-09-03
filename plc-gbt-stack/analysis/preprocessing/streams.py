#!/usr/bin/env python3
"""
Real-Time Stream Processing - Phase 22.1.2
==========================================

Real-time data stream processing capabilities for industrial control systems
with advanced buffering, synchronization, and real-time analysis features.

Features:
- Real-time data stream processing
- Multi-stream synchronization
- Intelligent data buffering with windowing
- Stream quality monitoring
- Integration with existing data pipeline
- Performance optimization for real-time systems

Author: AI Task Orchestrator
Created: January 18, 2025
Phase: 22.1.2 - Enhanced Data Preprocessing (Streams)
"""

import asyncio
import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Setup logging
logger = logging.getLogger(__name__)

class StreamType(Enum):
    """Types of data streams"""
    CONTINUOUS = "continuous"    # Continuous real-time data
    PERIODIC = "periodic"       # Regular interval data
    EVENT_DRIVEN = "event_driven"  # Event-triggered data
    BATCH = "batch"            # Periodic batch updates

class SynchronizationStrategy(Enum):
    """Stream synchronization strategies"""
    EXACT_MATCH = "exact_match"          # Require exact timestamp match
    NEAREST_NEIGHBOR = "nearest_neighbor"  # Use nearest timestamp
    INTERPOLATION = "interpolation"       # Interpolate between points
    WINDOW_BASED = "window_based"        # Synchronize within time windows

class BufferStrategy(Enum):
    """Data buffering strategies"""
    FIFO = "fifo"              # First In, First Out
    LIFO = "lifo"              # Last In, First Out
    TIME_WINDOW = "time_window"    # Time-based window
    SIZE_LIMIT = "size_limit"      # Size-based limit
    QUALITY_BASED = "quality_based"  # Quality-based retention

@dataclass
class StreamingOptions:
    """Configuration for stream processing"""
    buffer_size: int = 10000           # Maximum buffer size
    time_window_seconds: int = 300     # 5-minute time window
    sync_tolerance_ms: int = 100       # 100ms synchronization tolerance
    quality_threshold: float = 0.8     # Minimum quality for retention
    processing_interval_ms: int = 1000  # 1-second processing interval
    max_latency_ms: int = 5000         # Maximum acceptable latency
    enable_compression: bool = False    # Enable data compression
    enable_persistence: bool = True     # Enable data persistence
    real_time_validation: bool = True   # Enable real-time validation

@dataclass
class StreamData:
    """Individual stream data point"""
    timestamp: datetime
    values: Dict[str, Any]
    source_id: str
    quality_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'timestamp': self.timestamp,
            'source_id': self.source_id,
            'quality_score': self.quality_score,
            'metadata': self.metadata,
            **self.values
        }

@dataclass
class StreamBuffer:
    """Buffer for streaming data"""
    stream_id: str
    data: deque = field(default_factory=deque)
    strategy: BufferStrategy = BufferStrategy.TIME_WINDOW
    max_size: int = 10000
    time_window: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def add_data(self, stream_data: StreamData):
        """Add data to buffer"""
        self.data.append(stream_data)
        self.last_updated = datetime.now()
        self._maintain_buffer()

    def _maintain_buffer(self):
        """Maintain buffer according to strategy"""
        if self.strategy == BufferStrategy.SIZE_LIMIT:
            while len(self.data) > self.max_size:
                self.data.popleft()

        elif self.strategy == BufferStrategy.TIME_WINDOW:
            cutoff_time = datetime.now() - self.time_window
            while self.data and self.data[0].timestamp < cutoff_time:
                self.data.popleft()

        elif self.strategy == BufferStrategy.QUALITY_BASED:
            # Remove low-quality data when buffer is full
            if len(self.data) > self.max_size:
                # Sort by quality and remove lowest quality data
                sorted_data = sorted(self.data, key=lambda x: x.quality_score, reverse=True)
                self.data = deque(sorted_data[:self.max_size])

    def get_recent_data(self, count: Optional[int] = None) -> List[StreamData]:
        """Get recent data from buffer"""
        if count is None:
            return list(self.data)
        else:
            return list(self.data)[-count:]

    def to_dataframe(self) -> pd.DataFrame:
        """Convert buffer data to DataFrame"""
        if not self.data:
            return pd.DataFrame()

        records = [data.to_dict() for data in self.data]
        df = pd.DataFrame(records)

        # Set timestamp as index if present
        if 'timestamp' in df.columns:
            df.set_index('timestamp', inplace=True)

        return df

class DataBuffer:
    """
    Advanced data buffer with multiple streams and synchronization
    """

    def __init__(self, options: StreamingOptions = None):
        self.options = options or StreamingOptions()
        self.buffers: Dict[str, StreamBuffer] = {}
        self.logger = logging.getLogger(f"{__name__}.DataBuffer")
        self._lock = threading.RLock()

    def add_stream(self, stream_id: str, buffer_strategy: BufferStrategy = BufferStrategy.TIME_WINDOW):
        """Add a new stream buffer"""
        with self._lock:
            self.buffers[stream_id] = StreamBuffer(
                stream_id=stream_id,
                strategy=buffer_strategy,
                max_size=self.options.buffer_size,
                time_window=timedelta(seconds=self.options.time_window_seconds)
            )
            self.logger.info(f"Added stream buffer: {stream_id}")

    def add_data(self, stream_id: str, timestamp: datetime, values: Dict[str, Any],
                source_id: str = None, quality_score: float = 1.0, metadata: Dict[str, Any] = None):
        """Add data to a stream buffer"""
        if stream_id not in self.buffers:
            self.add_stream(stream_id)

        stream_data = StreamData(
            timestamp=timestamp,
            values=values,
            source_id=source_id or stream_id,
            quality_score=quality_score,
            metadata=metadata or {}
        )

        with self._lock:
            self.buffers[stream_id].add_data(stream_data)

    def get_synchronized_data(self, stream_ids: List[str],
                            strategy: SynchronizationStrategy = SynchronizationStrategy.NEAREST_NEIGHBOR) -> pd.DataFrame:
        """Get synchronized data from multiple streams"""
        if not stream_ids or not any(sid in self.buffers for sid in stream_ids):
            return pd.DataFrame()

        with self._lock:
            # Get data from all requested streams
            stream_dataframes = {}
            for stream_id in stream_ids:
                if stream_id in self.buffers:
                    df = self.buffers[stream_id].to_dataframe()
                    if not df.empty:
                        stream_dataframes[stream_id] = df

            if not stream_dataframes:
                return pd.DataFrame()

            # Synchronize based on strategy
            return self._synchronize_dataframes(stream_dataframes, strategy)

    def _synchronize_dataframes(self, stream_dataframes: Dict[str, pd.DataFrame],
                              strategy: SynchronizationStrategy) -> pd.DataFrame:
        """Synchronize multiple dataframes"""
        if not stream_dataframes:
            return pd.DataFrame()

        if strategy == SynchronizationStrategy.EXACT_MATCH:
            # Find common timestamps
            common_index = None
            for df in stream_dataframes.values():
                if common_index is None:
                    common_index = df.index
                else:
                    common_index = common_index.intersection(df.index)

            if common_index.empty:
                return pd.DataFrame()

            # Combine data with common timestamps
            result_df = pd.DataFrame(index=common_index)
            for stream_id, df in stream_dataframes.items():
                for col in df.columns:
                    result_df[f"{stream_id}_{col}"] = df.loc[common_index, col]

            return result_df

        elif strategy == SynchronizationStrategy.NEAREST_NEIGHBOR:
            # Use one stream as reference and align others
            reference_stream = list(stream_dataframes.keys())[0]
            reference_df = stream_dataframes[reference_stream]

            result_df = reference_df.copy()

            for stream_id, df in stream_dataframes.items():
                if stream_id == reference_stream:
                    continue

                # Reindex to match reference timestamps
                aligned_df = df.reindex(reference_df.index, method='nearest',
                                      tolerance=pd.Timedelta(milliseconds=self.options.sync_tolerance_ms))

                for col in aligned_df.columns:
                    result_df[f"{stream_id}_{col}"] = aligned_df[col]

            return result_df

        elif strategy == SynchronizationStrategy.WINDOW_BASED:
            # Combine all data and group by time windows
            all_data = []
            for stream_id, df in stream_dataframes.items():
                df_copy = df.copy()
                df_copy['stream_id'] = stream_id
                all_data.append(df_copy)

            if not all_data:
                return pd.DataFrame()

            combined_df = pd.concat(all_data)

            # Group by time windows (e.g., 1-second windows)
            window_size = f"{self.options.sync_tolerance_ms}ms"
            grouped = combined_df.groupby([pd.Grouper(freq=window_size), 'stream_id']).mean()

            # Pivot to get streams as columns
            result_df = grouped.unstack('stream_id')

            return result_df

        else:
            # Default: just concatenate all data
            return pd.concat(stream_dataframes.values(), axis=1, keys=stream_dataframes.keys())

class StreamSynchronizer:
    """
    Advanced stream synchronization with multiple strategies
    """

    def __init__(self, options: StreamingOptions = None):
        self.options = options or StreamingOptions()
        self.logger = logging.getLogger(f"{__name__}.StreamSynchronizer")

    async def synchronize_streams(self, streams: Dict[str, AsyncGenerator],
                                strategy: SynchronizationStrategy = SynchronizationStrategy.NEAREST_NEIGHBOR) -> AsyncGenerator[pd.DataFrame, None]:
        """Synchronize multiple async data streams"""
        buffer = DataBuffer(self.options)

        # Add all streams to buffer
        for stream_id in streams.keys():
            buffer.add_stream(stream_id)

        # Start collecting data from all streams
        async def collect_stream_data(stream_id: str, stream_gen: AsyncGenerator):
            async for data_point in stream_gen:
                if isinstance(data_point, dict):
                    timestamp = data_point.get('timestamp', datetime.now())
                    values = {k: v for k, v in data_point.items() if k != 'timestamp'}
                    buffer.add_data(stream_id, timestamp, values)

        # Start collection tasks
        collection_tasks = [
            asyncio.create_task(collect_stream_data(stream_id, stream_gen))
            for stream_id, stream_gen in streams.items()
        ]

        try:
            # Periodically yield synchronized data
            while True:
                await asyncio.sleep(self.options.processing_interval_ms / 1000.0)

                synchronized_data = buffer.get_synchronized_data(list(streams.keys()), strategy)
                if not synchronized_data.empty:
                    yield synchronized_data

        finally:
            # Cancel collection tasks
            for task in collection_tasks:
                task.cancel()

    def synchronize_dataframes(self, dataframes: Dict[str, pd.DataFrame],
                             strategy: SynchronizationStrategy = SynchronizationStrategy.NEAREST_NEIGHBOR) -> pd.DataFrame:
        """Synchronize static dataframes"""
        buffer = DataBuffer(self.options)
        return buffer._synchronize_dataframes(dataframes, strategy)

class RealTimeProcessor:
    """
    Real-time data processor with streaming capabilities
    """

    def __init__(self, options: StreamingOptions = None):
        self.options = options or StreamingOptions()
        self.logger = logging.getLogger(f"{__name__}.RealTimeProcessor")
        self.buffer = DataBuffer(options)
        self.synchronizer = StreamSynchronizer(options)
        self.is_running = False
        self._processing_task = None
        self._callbacks: List[Callable] = []

    def add_callback(self, callback: Callable[[pd.DataFrame], None]):
        """Add callback for processed data"""
        self._callbacks.append(callback)

    def add_stream_data(self, stream_id: str, timestamp: datetime, values: Dict[str, Any],
                       quality_score: float = 1.0):
        """Add data to a stream"""
        self.buffer.add_data(stream_id, timestamp, values, quality_score=quality_score)

    async def start_processing(self, stream_ids: List[str]):
        """Start real-time processing"""
        if self.is_running:
            self.logger.warning("Processor is already running")
            return

        self.is_running = True
        self.logger.info(f"Starting real-time processing for streams: {stream_ids}")

        # Ensure all streams exist
        for stream_id in stream_ids:
            if stream_id not in self.buffer.buffers:
                self.buffer.add_stream(stream_id)

        # Start processing loop
        self._processing_task = asyncio.create_task(self._processing_loop(stream_ids))

    async def stop_processing(self):
        """Stop real-time processing"""
        if not self.is_running:
            return

        self.is_running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Real-time processing stopped")

    async def _processing_loop(self, stream_ids: List[str]):
        """Main processing loop"""
        try:
            while self.is_running:
                # Get synchronized data
                synchronized_data = self.buffer.get_synchronized_data(
                    stream_ids, SynchronizationStrategy.NEAREST_NEIGHBOR)

                if not synchronized_data.empty and len(synchronized_data) > 0:
                    # Apply real-time validation if enabled
                    if self.options.real_time_validation:
                        validated_data = self._validate_real_time_data(synchronized_data)
                    else:
                        validated_data = synchronized_data

                    # Call all registered callbacks
                    for callback in self._callbacks:
                        try:
                            callback(validated_data)
                        except Exception as e:
                            self.logger.error(f"Callback error: {e}")

                # Wait for next processing interval
                await asyncio.sleep(self.options.processing_interval_ms / 1000.0)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Processing loop error: {e}")

    def _validate_real_time_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate real-time data"""
        validated_data = data.copy()

        # Check data freshness
        if isinstance(data.index, pd.DatetimeIndex):
            latest_time = data.index.max()
            current_time = datetime.now()

            # Handle timezone-naive datetime
            if latest_time.tz is None:
                current_time = current_time.replace(tzinfo=None)

            age_ms = (current_time - latest_time).total_seconds() * 1000

            if age_ms > self.options.max_latency_ms:
                self.logger.warning(f"Data latency ({age_ms:.0f}ms) exceeds threshold ({self.options.max_latency_ms}ms)")

        # Check for NaN values
        numeric_cols = validated_data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            nan_count = validated_data[col].isna().sum()
            if nan_count > 0:
                self.logger.warning(f"Column {col} has {nan_count} NaN values")

        return validated_data

    def get_stream_status(self) -> Dict[str, Any]:
        """Get status of all streams"""
        status = {
            'is_running': self.is_running,
            'stream_count': len(self.buffer.buffers),
            'streams': {}
        }

        for stream_id, buffer in self.buffer.buffers.items():
            status['streams'][stream_id] = {
                'data_points': len(buffer.data),
                'last_updated': buffer.last_updated,
                'age_seconds': (datetime.now() - buffer.last_updated).total_seconds() if buffer.data else None
            }

        return status

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for real-time processing"""
        metrics = {
            'processing_interval_ms': self.options.processing_interval_ms,
            'buffer_utilization': {},
            'average_latency_ms': 0.0,
            'throughput_points_per_second': 0.0
        }

        # Calculate buffer utilization
        for stream_id, buffer in self.buffer.buffers.items():
            utilization = len(buffer.data) / buffer.max_size
            metrics['buffer_utilization'][stream_id] = utilization

        # Calculate average latency
        if self.buffer.buffers:
            total_latency = 0
            count = 0
            current_time = datetime.now()

            for buffer in self.buffer.buffers.values():
                if buffer.data:
                    latest_data = buffer.data[-1]
                    latency = (current_time - latest_data.timestamp).total_seconds() * 1000
                    total_latency += latency
                    count += 1

            if count > 0:
                metrics['average_latency_ms'] = total_latency / count

        return metrics

# Utility functions for stream processing
async def create_mock_stream(stream_id: str, interval_ms: int = 1000,
                           value_range: Tuple[float, float] = (0.0, 100.0)) -> AsyncGenerator[Dict[str, Any], None]:
    """Create a mock data stream for testing"""
    while True:
        timestamp = datetime.now()
        value = np.random.uniform(value_range[0], value_range[1])

        yield {
            'timestamp': timestamp,
            'value': value,
            'stream_id': stream_id
        }

        await asyncio.sleep(interval_ms / 1000.0)

def merge_stream_data(stream_data_list: List[pd.DataFrame]) -> pd.DataFrame:
    """Merge multiple stream dataframes into one"""
    if not stream_data_list:
        return pd.DataFrame()

    # Filter out empty dataframes
    non_empty_streams = [df for df in stream_data_list if not df.empty]

    if not non_empty_streams:
        return pd.DataFrame()

    # Concatenate all streams
    merged_data = pd.concat(non_empty_streams, axis=0, ignore_index=True)

    # Sort by timestamp if available
    if 'timestamp' in merged_data.columns:
        merged_data = merged_data.sort_values('timestamp')

    return merged_data
