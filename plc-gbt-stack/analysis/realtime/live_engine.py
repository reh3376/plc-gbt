#!/usr/bin/env python3
"""
Phase 22.4: Task 22.4.2 - Live Analysis Engine
==============================================

Live analysis engine implementing:
- Streaming algorithm implementation
- Rolling window calculations
- Real-time model updating
- Performance degradation detection

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.4.2 - Live Analysis Engine
Methodology: AI Task Orchestrator Guide
"""

import logging
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from scipy import stats

# Import performance analysis from Phase 22.3
try:
    from ..performance.metrics import (
        PerformanceConfiguration,
        PerformanceMetricsCalculator,
        TimeDomainMetrics,
        TimeSeriesData,
    )
    PERFORMANCE_INTEGRATION_AVAILABLE = True
except ImportError:
    PERFORMANCE_INTEGRATION_AVAILABLE = False
    logging.warning("⚠️ Performance analysis integration not available")

# Import algorithm base class if available
try:
    from ..algorithms import (
        AlgorithmBase,
        AlgorithmCategory,
        AlgorithmComplexity,
        AlgorithmMetadata,
        registry,
    )
    ALGORITHM_REGISTRY_AVAILABLE = True
except ImportError:
    ALGORITHM_REGISTRY_AVAILABLE = False
    logging.warning("⚠️ Algorithm registry not available - using standalone implementation")

logger = logging.getLogger(__name__)

class StreamingMode(Enum):
    """Streaming analysis modes"""
    CONTINUOUS = "continuous"
    TRIGGERED = "triggered"
    BATCH = "batch"
    ADAPTIVE = "adaptive"

class DegradationSeverity(Enum):
    """Performance degradation severity levels"""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    CRITICAL = "critical"

class UpdateStrategy(Enum):
    """Model update strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    FORGETTING_FACTOR = "forgetting_factor"
    CHANGE_DETECTION = "change_detection"
    ADAPTIVE_LEARNING = "adaptive_learning"

@dataclass
class StreamingConfiguration:
    """Configuration for streaming analysis"""
    stream_id: str
    window_size: int = 300  # seconds
    overlap_ratio: float = 0.5
    update_frequency: float = 1.0  # Hz
    buffer_size: int = 10000

    # Analysis settings
    enable_trend_detection: bool = True
    enable_anomaly_detection: bool = True
    enable_degradation_detection: bool = True
    enable_model_updating: bool = True

    # Performance thresholds
    max_processing_time: float = 0.1  # seconds
    max_memory_usage: float = 100.0  # MB
    alert_threshold: float = 0.8  # performance degradation threshold

@dataclass
class RollingWindowData:
    """Rolling window data container"""
    timestamps: deque
    values: deque
    statistics: Dict[str, float] = field(default_factory=dict)
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    last_update: Optional[datetime] = None

@dataclass
class StreamingResults:
    """Streaming analysis results"""
    stream_id: str
    timestamp: datetime
    window_data: RollingWindowData
    performance_metrics: Dict[str, float]
    trend_analysis: Dict[str, Any]
    anomaly_detection: Dict[str, Any]
    degradation_assessment: Dict[str, Any]
    model_updates: Dict[str, Any]
    processing_time: float
    next_update: datetime

class RollingWindowCalculator:
    """High-performance rolling window calculations"""

    def __init__(self, window_size: int, overlap_ratio: float = 0.5):
        self.window_size = window_size
        self.overlap_ratio = overlap_ratio
        self.overlap_samples = int(window_size * overlap_ratio)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Data storage
        self.windows = {}

    def add_data_point(self, stream_id: str, timestamp: datetime, value: float):
        """Add a new data point to the rolling window"""

        if stream_id not in self.windows:
            self.windows[stream_id] = RollingWindowData(
                timestamps=deque(maxlen=self.window_size),
                values=deque(maxlen=self.window_size)
            )

        window = self.windows[stream_id]
        window.timestamps.append(timestamp)
        window.values.append(value)
        window.last_update = timestamp

        # Update statistics if window is sufficient
        if len(window.values) >= 10:  # Minimum samples for statistics
            self._update_statistics(window)

    def _update_statistics(self, window: RollingWindowData):
        """Update rolling window statistics"""

        values = np.array(window.values)

        # Basic statistics
        window.statistics.update({
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'median': np.median(values),
            'range': np.max(values) - np.min(values),
            'skewness': stats.skew(values),
            'kurtosis': stats.kurtosis(values)
        })

        # Trend analysis
        if len(values) > 5:
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            window.statistics.update({
                'trend_slope': slope,
                'trend_r_squared': r_value**2,
                'trend_p_value': p_value
            })

        # Variability measures
        if len(values) > 2:
            window.statistics.update({
                'coefficient_variation': np.std(values) / np.mean(values) if np.mean(values) != 0 else 0,
                'interquartile_range': np.percentile(values, 75) - np.percentile(values, 25)
            })

    def get_window_data(self, stream_id: str) -> Optional[RollingWindowData]:
        """Get current window data for a stream"""
        return self.windows.get(stream_id)

    def is_window_ready(self, stream_id: str, min_samples: int = 10) -> bool:
        """Check if window has sufficient data for analysis"""
        window = self.windows.get(stream_id)
        return window is not None and len(window.values) >= min_samples

class StreamingAnalyzer:
    """Core streaming analysis engine"""

    def __init__(self, configuration: StreamingConfiguration):
        self.config = configuration
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Components
        self.window_calculator = RollingWindowCalculator(
            self.config.window_size,
            self.config.overlap_ratio
        )

        # Analysis modules
        if PERFORMANCE_INTEGRATION_AVAILABLE:
            self.performance_calculator = PerformanceMetricsCalculator()

        # Processing state
        self.is_running = False
        self.last_analysis = {}
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def process_data_stream(self, stream_id: str, data_point: Dict[str, Any]) -> Optional[StreamingResults]:
        """Process a single data point in the stream"""

        try:
            start_time = time.time()

            # Extract data
            timestamp = data_point.get('timestamp', datetime.now())
            value = data_point.get('value', 0.0)

            # Add to rolling window
            self.window_calculator.add_data_point(stream_id, timestamp, value)

            # Check if analysis should be performed
            if not self._should_analyze(stream_id, timestamp):
                return None

            # Get window data
            window_data = self.window_calculator.get_window_data(stream_id)
            if not window_data or len(window_data.values) < 10:
                return None

            # Perform analysis
            results = await self._perform_analysis(stream_id, window_data, data_point)

            # Calculate processing time
            processing_time = time.time() - start_time
            results.processing_time = processing_time

            # Update analysis tracking
            self.last_analysis[stream_id] = timestamp

            # Log performance
            if processing_time > self.config.max_processing_time:
                self.logger.warning(f"Analysis exceeded time limit: {processing_time:.3f}s")

            return results

        except Exception as e:
            self.logger.error(f"Error processing data stream {stream_id}: {e}")
            return None

    def _should_analyze(self, stream_id: str, timestamp: datetime) -> bool:
        """Determine if analysis should be performed"""

        last_analysis = self.last_analysis.get(stream_id)
        if last_analysis is None:
            return True

        time_since_last = (timestamp - last_analysis).total_seconds()
        analysis_interval = 1.0 / self.config.update_frequency

        return time_since_last >= analysis_interval

    async def _perform_analysis(self, stream_id: str, window_data: RollingWindowData,
                               current_data: Dict[str, Any]) -> StreamingResults:
        """Perform comprehensive streaming analysis"""

        timestamp = datetime.now()

        # Initialize results
        results = StreamingResults(
            stream_id=stream_id,
            timestamp=timestamp,
            window_data=window_data,
            performance_metrics={},
            trend_analysis={},
            anomaly_detection={},
            degradation_assessment={},
            model_updates={},
            processing_time=0.0,
            next_update=timestamp + timedelta(seconds=1.0/self.config.update_frequency)
        )

        # Performance metrics calculation
        if self.config.enable_trend_detection:
            results.performance_metrics = self._calculate_performance_metrics(window_data)

        # Trend detection
        if self.config.enable_trend_detection:
            results.trend_analysis = self._detect_trends(window_data)

        # Anomaly detection
        if self.config.enable_anomaly_detection:
            results.anomaly_detection = self._detect_anomalies(window_data, current_data)

        # Performance degradation detection
        if self.config.enable_degradation_detection:
            results.degradation_assessment = self._assess_degradation(window_data, results.performance_metrics)

        # Model updating
        if self.config.enable_model_updating:
            results.model_updates = self._update_models(stream_id, window_data)

        return results

    def _calculate_performance_metrics(self, window_data: RollingWindowData) -> Dict[str, float]:
        """Calculate real-time performance metrics"""

        metrics = {}

        # Use window statistics
        stats = window_data.statistics
        if stats:
            metrics.update({
                'mean': stats.get('mean', 0.0),
                'std_dev': stats.get('std', 0.0),
                'variability': stats.get('coefficient_variation', 0.0),
                'trend_strength': abs(stats.get('trend_slope', 0.0)),
                'trend_confidence': stats.get('trend_r_squared', 0.0)
            })

        # Additional real-time metrics
        values = np.array(window_data.values)
        if len(values) > 1:
            # Signal-to-noise ratio
            signal_power = np.mean(values**2)
            noise_power = np.var(np.diff(values))
            snr = signal_power / noise_power if noise_power > 0 else float('inf')
            metrics['signal_to_noise_ratio'] = min(snr, 1000.0)  # Cap at 1000

            # Stability index
            recent_std = np.std(values[-10:]) if len(values) >= 10 else np.std(values)
            overall_std = np.std(values)
            stability_index = 1.0 - (recent_std / overall_std) if overall_std > 0 else 1.0
            metrics['stability_index'] = max(0.0, min(1.0, stability_index))

        return metrics

    def _detect_trends(self, window_data: RollingWindowData) -> Dict[str, Any]:
        """Detect trends in the data stream"""

        trend_analysis = {
            'trend_detected': False,
            'direction': 'stable',
            'strength': 0.0,
            'confidence': 0.0,
            'change_points': []
        }

        values = np.array(window_data.values)
        if len(values) < 10:
            return trend_analysis

        # Linear trend analysis
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

        # Trend detection criteria
        trend_threshold = 0.01 * np.mean(values)  # 1% change threshold
        confidence_threshold = 0.3  # R² threshold

        if abs(slope) > trend_threshold and r_value**2 > confidence_threshold and p_value < 0.05:
            trend_analysis.update({
                'trend_detected': True,
                'direction': 'increasing' if slope > 0 else 'decreasing',
                'strength': abs(slope),
                'confidence': r_value**2,
                'slope': slope,
                'p_value': p_value
            })

        # Change point detection (simplified)
        if len(values) >= 20:
            # Split data in half and compare means
            mid_point = len(values) // 2
            first_half = values[:mid_point]
            second_half = values[mid_point:]

            # T-test for significant change
            t_stat, t_p_value = stats.ttest_ind(first_half, second_half)
            if t_p_value < 0.01:  # Significant change
                change_point = {
                    'location': mid_point,
                    'timestamp': window_data.timestamps[mid_point] if len(window_data.timestamps) > mid_point else None,
                    'magnitude': np.mean(second_half) - np.mean(first_half),
                    'confidence': 1.0 - t_p_value
                }
                trend_analysis['change_points'].append(change_point)

        return trend_analysis

    def _detect_anomalies(self, window_data: RollingWindowData, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in real-time data"""

        anomaly_detection = {
            'anomaly_detected': False,
            'anomaly_score': 0.0,
            'anomaly_type': 'none',
            'threshold_used': 3.0,
            'explanation': ''
        }

        values = np.array(window_data.values)
        current_value = current_data.get('value', 0.0)

        if len(values) < 10:
            return anomaly_detection

        # Statistical anomaly detection (Z-score)
        mean_val = np.mean(values)
        std_val = np.std(values)

        if std_val > 0:
            z_score = abs(current_value - mean_val) / std_val
            threshold = 3.0  # 3-sigma threshold

            if z_score > threshold:
                anomaly_detection.update({
                    'anomaly_detected': True,
                    'anomaly_score': z_score,
                    'anomaly_type': 'statistical_outlier',
                    'threshold_used': threshold,
                    'explanation': f'Value {current_value:.3f} is {z_score:.2f} standard deviations from mean {mean_val:.3f}'
                })

        # Rate of change anomaly
        if len(values) >= 2:
            recent_change = abs(values[-1] - values[-2])
            typical_change = np.mean(np.abs(np.diff(values)))

            if typical_change > 0 and recent_change > 5 * typical_change:
                anomaly_detection.update({
                    'anomaly_detected': True,
                    'anomaly_score': recent_change / typical_change,
                    'anomaly_type': 'rate_of_change',
                    'explanation': f'Rate of change {recent_change:.3f} exceeds typical {typical_change:.3f}'
                })

        return anomaly_detection

    def _assess_degradation(self, window_data: RollingWindowData, performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Assess performance degradation"""

        degradation_assessment = {
            'degradation_detected': False,
            'severity': DegradationSeverity.NONE.value,
            'degradation_score': 0.0,
            'affected_metrics': [],
            'trend_direction': 'stable',
            'recommendation': 'No action required'
        }

        # Define degradation thresholds
        thresholds = {
            'variability_increase': 2.0,  # 2x increase in variability
            'stability_decrease': 0.5,   # 50% decrease in stability
            'trend_strength_increase': 0.1  # Significant trend development
        }

        # Check individual metrics for degradation
        degradation_score = 0.0
        affected_metrics = []

        # Variability degradation
        variability = performance_metrics.get('variability', 0.0)
        if variability > thresholds['variability_increase']:
            degradation_score += min(variability / thresholds['variability_increase'], 3.0)
            affected_metrics.append('variability')

        # Stability degradation
        stability = performance_metrics.get('stability_index', 1.0)
        if stability < thresholds['stability_decrease']:
            degradation_score += (thresholds['stability_decrease'] - stability) * 2.0
            affected_metrics.append('stability')

        # Trend development (can indicate degradation)
        trend_strength = performance_metrics.get('trend_strength', 0.0)
        if trend_strength > thresholds['trend_strength_increase']:
            degradation_score += trend_strength * 10.0
            affected_metrics.append('trend_development')

        # Assess overall degradation
        if degradation_score > 0.1:
            degradation_assessment.update({
                'degradation_detected': True,
                'degradation_score': degradation_score,
                'affected_metrics': affected_metrics
            })

            # Determine severity
            if degradation_score >= 3.0:
                degradation_assessment['severity'] = DegradationSeverity.CRITICAL.value
                degradation_assessment['recommendation'] = 'Immediate action required - system performance critical'
            elif degradation_score >= 2.0:
                degradation_assessment['severity'] = DegradationSeverity.SIGNIFICANT.value
                degradation_assessment['recommendation'] = 'Performance degradation significant - investigate and correct'
            elif degradation_score >= 1.0:
                degradation_assessment['severity'] = DegradationSeverity.MODERATE.value
                degradation_assessment['recommendation'] = 'Monitor performance closely - consider tuning adjustments'
            else:
                degradation_assessment['severity'] = DegradationSeverity.MINOR.value
                degradation_assessment['recommendation'] = 'Minor performance changes detected - continue monitoring'

        return degradation_assessment

    def _update_models(self, stream_id: str, window_data: RollingWindowData) -> Dict[str, Any]:
        """Update process models in real-time"""

        model_updates = {
            'model_updated': False,
            'update_strategy': UpdateStrategy.SLIDING_WINDOW.value,
            'model_parameters': {},
            'model_quality': 0.0,
            'update_reason': 'No update needed'
        }

        values = np.array(window_data.values)
        if len(values) < 20:  # Need sufficient data for model updates
            return model_updates

        # Simple model update: moving average and variance
        try:
            # Calculate updated model parameters
            updated_parameters = {
                'mean': np.mean(values),
                'variance': np.var(values),
                'trend': window_data.statistics.get('trend_slope', 0.0),
                'autocorrelation': self._calculate_autocorrelation(values)
            }

            # Compare with existing model
            existing_params = window_data.model_parameters
            if self._should_update_model(existing_params, updated_parameters):
                window_data.model_parameters = updated_parameters

                # Calculate model quality (simplified)
                model_quality = self._calculate_model_quality(values, updated_parameters)

                model_updates.update({
                    'model_updated': True,
                    'model_parameters': updated_parameters,
                    'model_quality': model_quality,
                    'update_reason': 'Significant parameter change detected'
                })

        except Exception as e:
            self.logger.warning(f"Model update failed for {stream_id}: {e}")

        return model_updates

    def _calculate_autocorrelation(self, values: np.ndarray, max_lag: int = 10) -> float:
        """Calculate autocorrelation for time series"""

        if len(values) < max_lag * 2:
            return 0.0

        # Calculate autocorrelation at lag 1
        correlation = np.corrcoef(values[:-1], values[1:])[0, 1]
        return correlation if not np.isnan(correlation) else 0.0

    def _should_update_model(self, existing_params: Dict[str, Any],
                           new_params: Dict[str, Any]) -> bool:
        """Determine if model should be updated"""

        if not existing_params:
            return True

        # Check for significant parameter changes
        threshold = 0.1  # 10% change threshold

        for param, new_value in new_params.items():
            if param in existing_params:
                old_value = existing_params[param]
                if old_value != 0:
                    relative_change = abs(new_value - old_value) / abs(old_value)
                    if relative_change > threshold:
                        return True

        return False

    def _calculate_model_quality(self, values: np.ndarray,
                               parameters: Dict[str, Any]) -> float:
        """Calculate model quality score"""

        # Simplified model quality based on prediction accuracy
        try:
            predicted_mean = parameters['mean']
            actual_values = values[-10:]  # Last 10 values

            prediction_error = np.mean(np.abs(actual_values - predicted_mean))
            signal_magnitude = np.mean(np.abs(actual_values))

            if signal_magnitude > 0:
                quality_score = 1.0 - (prediction_error / signal_magnitude)
                return max(0.0, min(1.0, quality_score))

        except Exception:
            pass

        return 0.5  # Default moderate quality

class PerformanceDegradationDetector:
    """Advanced performance degradation detection"""

    def __init__(self, sensitivity: float = 0.8):
        self.sensitivity = sensitivity
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Historical baseline storage
        self.baselines = {}
        self.degradation_history = {}

    def establish_baseline(self, stream_id: str, baseline_data: np.ndarray):
        """Establish performance baseline for comparison"""

        if len(baseline_data) < 100:
            self.logger.warning(f"Insufficient baseline data for {stream_id}: {len(baseline_data)} samples")
            return

        baseline_stats = {
            'mean': np.mean(baseline_data),
            'std': np.std(baseline_data),
            'percentiles': {
                '5': np.percentile(baseline_data, 5),
                '25': np.percentile(baseline_data, 25),
                '75': np.percentile(baseline_data, 75),
                '95': np.percentile(baseline_data, 95)
            },
            'variability': np.std(baseline_data) / np.mean(baseline_data) if np.mean(baseline_data) != 0 else 0,
            'established': datetime.now()
        }

        self.baselines[stream_id] = baseline_stats
        self.logger.info(f"Baseline established for {stream_id}")

    def detect_degradation(self, stream_id: str, current_data: np.ndarray) -> Dict[str, Any]:
        """Detect performance degradation against baseline"""

        if stream_id not in self.baselines:
            return {
                'degradation_detected': False,
                'reason': 'No baseline established',
                'severity': DegradationSeverity.NONE.value
            }

        baseline = self.baselines[stream_id]

        # Calculate current statistics
        current_stats = {
            'mean': np.mean(current_data),
            'std': np.std(current_data),
            'variability': np.std(current_data) / np.mean(current_data) if np.mean(current_data) != 0 else 0
        }

        # Degradation detection logic
        degradation_indicators = []

        # Mean shift detection
        mean_shift = abs(current_stats['mean'] - baseline['mean']) / baseline['std']
        if mean_shift > 2.0 * self.sensitivity:
            degradation_indicators.append({
                'type': 'mean_shift',
                'severity': mean_shift,
                'description': f'Mean shifted by {mean_shift:.2f} standard deviations'
            })

        # Variability increase
        variability_ratio = current_stats['variability'] / baseline['variability'] if baseline['variability'] > 0 else 1.0
        if variability_ratio > (1.5 / self.sensitivity):
            degradation_indicators.append({
                'type': 'variability_increase',
                'severity': variability_ratio,
                'description': f'Variability increased by factor of {variability_ratio:.2f}'
            })

        # Distribution change (simplified KS test)
        try:
            baseline_sample = np.random.normal(baseline['mean'], baseline['std'], len(current_data))
            ks_stat, ks_p_value = stats.ks_2samp(baseline_sample, current_data)

            if ks_p_value < (0.05 * self.sensitivity):
                degradation_indicators.append({
                    'type': 'distribution_change',
                    'severity': ks_stat,
                    'description': f'Statistical distribution changed (p={ks_p_value:.4f})'
                })
        except Exception:
            pass

        # Overall assessment
        if degradation_indicators:
            max_severity = max(indicator['severity'] for indicator in degradation_indicators)

            if max_severity >= 4.0:
                severity = DegradationSeverity.CRITICAL
            elif max_severity >= 3.0:
                severity = DegradationSeverity.SIGNIFICANT
            elif max_severity >= 2.0:
                severity = DegradationSeverity.MODERATE
            else:
                severity = DegradationSeverity.MINOR

            return {
                'degradation_detected': True,
                'severity': severity.value,
                'indicators': degradation_indicators,
                'max_severity': max_severity,
                'baseline_age': (datetime.now() - baseline['established']).total_seconds() / 3600,  # hours
                'recommendation': self._get_degradation_recommendation(severity, degradation_indicators)
            }

        return {
            'degradation_detected': False,
            'severity': DegradationSeverity.NONE.value,
            'baseline_age': (datetime.now() - baseline['established']).total_seconds() / 3600
        }

    def _get_degradation_recommendation(self, severity: DegradationSeverity,
                                      indicators: List[Dict]) -> str:
        """Generate degradation response recommendations"""

        if severity == DegradationSeverity.CRITICAL:
            return "CRITICAL: Immediate intervention required - stop process if safe to do so"
        elif severity == DegradationSeverity.SIGNIFICANT:
            return "SIGNIFICANT: Investigate immediately and plan corrective action"
        elif severity == DegradationSeverity.MODERATE:
            return "MODERATE: Schedule maintenance and review control parameters"
        elif severity == DegradationSeverity.MINOR:
            return "MINOR: Monitor closely and document performance changes"
        else:
            return "Continue normal operation"

class LiveAnalysisEngine:
    """Main live analysis engine orchestrator"""

    def __init__(self, configurations: List[StreamingConfiguration]):
        self.configurations = {config.stream_id: config for config in configurations}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize analyzers
        self.analyzers = {}
        for config in configurations:
            self.analyzers[config.stream_id] = StreamingAnalyzer(config)

        # Performance degradation detector
        self.degradation_detector = PerformanceDegradationDetector()

        # Engine state
        self.is_running = False
        self.start_time = None
        self.statistics = {
            'total_data_points': 0,
            'total_analyses': 0,
            'average_processing_time': 0.0,
            'errors': 0
        }

    async def start_engine(self):
        """Start the live analysis engine"""
        self.is_running = True
        self.start_time = datetime.now()
        self.logger.info("Live Analysis Engine started")

    async def stop_engine(self):
        """Stop the live analysis engine"""
        self.is_running = False
        self.logger.info("Live Analysis Engine stopped")

    async def process_data_point(self, stream_id: str, data_point: Dict[str, Any]) -> Optional[StreamingResults]:
        """Process a data point through the live analysis engine"""

        if not self.is_running:
            return None

        if stream_id not in self.analyzers:
            self.logger.warning(f"Unknown stream ID: {stream_id}")
            return None

        try:
            # Update statistics
            self.statistics['total_data_points'] += 1

            # Process through analyzer
            analyzer = self.analyzers[stream_id]
            results = await analyzer.process_data_stream(stream_id, data_point)

            if results:
                self.statistics['total_analyses'] += 1

                # Update average processing time
                total_time = (self.statistics['average_processing_time'] *
                            (self.statistics['total_analyses'] - 1) + results.processing_time)
                self.statistics['average_processing_time'] = total_time / self.statistics['total_analyses']

            return results

        except Exception as e:
            self.statistics['errors'] += 1
            self.logger.error(f"Error processing data point for {stream_id}: {e}")
            return None

    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get engine performance statistics"""

        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        return {
            'uptime_seconds': uptime,
            'is_running': self.is_running,
            'total_streams': len(self.analyzers),
            'statistics': self.statistics.copy(),
            'throughput': self.statistics['total_data_points'] / uptime if uptime > 0 else 0,
            'analysis_rate': self.statistics['total_analyses'] / uptime if uptime > 0 else 0,
            'error_rate': self.statistics['errors'] / self.statistics['total_data_points'] if self.statistics['total_data_points'] > 0 else 0
        }

    def add_stream(self, configuration: StreamingConfiguration):
        """Add a new stream to the engine"""
        self.configurations[configuration.stream_id] = configuration
        self.analyzers[configuration.stream_id] = StreamingAnalyzer(configuration)
        self.logger.info(f"Added stream: {configuration.stream_id}")

    def remove_stream(self, stream_id: str):
        """Remove a stream from the engine"""
        if stream_id in self.analyzers:
            del self.analyzers[stream_id]
            del self.configurations[stream_id]
            self.logger.info(f"Removed stream: {stream_id}")

# Register with algorithm registry if available
if ALGORITHM_REGISTRY_AVAILABLE:
    @registry.register(
        category=AlgorithmCategory.REAL_TIME_ANALYSIS,
        complexity=AlgorithmComplexity.HIGH,
        metadata=AlgorithmMetadata(
            name="Live Analysis Engine",
            description="Real-time streaming analysis with degradation detection",
            version="1.0.0",
            author="PLC-GPT Team",
            tags=["real_time", "streaming", "degradation_detection", "performance_monitoring"]
        )
    )
    class RegisteredLiveAnalysisEngine(LiveAnalysisEngine):
        pass
