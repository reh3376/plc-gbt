#!/usr/bin/env python3
"""
Phase 22.3: Task 22.3.1 - Performance Metrics Implementation
===========================================================

Comprehensive performance metrics calculator including:
- IAE, ISE, ITAE calculations
- Settling time and overshoot analysis
- Robustness metrics (GM, PM)
- Control effort quantification

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.3.1 - Performance Metrics
Methodology: AI Task Orchestrator Guide
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

import numpy as np
from scipy import integrate, signal

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

class MetricType(Enum):
    """Performance metric calculation types"""
    TIME_DOMAIN = "time_domain"
    FREQUENCY_DOMAIN = "frequency_domain"
    STABILITY = "stability"
    CONTROL_EFFORT = "control_effort"

@dataclass
class PerformanceConfiguration:
    """Performance metrics calculation configuration"""
    settling_criteria: float = 0.02  # 2% settling band
    overshoot_threshold: float = 0.05  # 5% overshoot warning
    steady_state_window: float = 0.1  # 10% of total time for steady state
    min_settling_samples: int = 10  # Minimum samples in settling band

    # Time domain settings
    time_weighting: bool = True  # Use time weighting for ITAE
    integration_method: str = "trapz"  # Integration method

    # Frequency domain settings
    frequency_points: int = 1000  # Number of frequency points
    gain_margin_crossover: bool = True  # Use -180° crossover for GM

    # Control effort settings
    effort_normalization: bool = True  # Normalize by signal range
    effort_penalty_factor: float = 1.0  # Penalty for excessive control effort

    # Robustness settings
    uncertainty_bounds: float = 0.1  # 10% model uncertainty
    robustness_samples: int = 100  # Monte Carlo samples

@dataclass
class TimeSeriesData:
    """Time series data container"""
    time: np.ndarray
    setpoint: np.ndarray
    process_variable: np.ndarray
    control_output: np.ndarray
    error: Optional[np.ndarray] = None
    disturbance: Optional[np.ndarray] = None
    sample_time: Optional[float] = None

@dataclass
class PerformanceResults:
    """Performance analysis results"""
    # Time domain metrics
    iae: float  # Integral Absolute Error
    ise: float  # Integral Squared Error
    itae: float  # Integral Time Absolute Error
    itse: float  # Integral Time Squared Error

    # Step response characteristics
    settling_time: float  # Time to settle within criteria
    overshoot: float  # Maximum overshoot percentage
    undershoot: float  # Maximum undershoot percentage
    rise_time: float  # 10% to 90% rise time
    peak_time: float  # Time to peak value

    # Control effort metrics
    control_effort: float  # Total control effort
    control_variation: float  # Control signal variation

    # Frequency domain metrics
    gain_margin: float  # Gain margin in dB
    phase_margin: float  # Phase margin in degrees
    gain_crossover_freq: float  # Gain crossover frequency
    phase_crossover_freq: float  # Phase crossover frequency

    # Overall performance
    performance_index: float  # Combined performance metric
    robustness_index: float  # Robustness metric
    efficiency_index: float  # Control efficiency metric

    # Analysis metadata
    analysis_time: float
    data_quality: float
    configuration: PerformanceConfiguration

class TimeDomainMetrics:
    """Time domain performance metrics calculator"""

    def __init__(self, configuration: Optional[PerformanceConfiguration] = None):
        self.config = configuration or PerformanceConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calculate_error_metrics(self, data: TimeSeriesData) -> Dict[str, float]:
        """Calculate IAE, ISE, ITAE, ITSE metrics"""

        if data.error is None:
            data.error = data.setpoint - data.process_variable

        time_vec = data.time
        error = data.error
        np.mean(np.diff(time_vec))

        # Integral Absolute Error
        iae = integrate.trapz(np.abs(error), time_vec)

        # Integral Squared Error
        ise = integrate.trapz(error**2, time_vec)

        # Integral Time Absolute Error
        itae = integrate.trapz(time_vec * np.abs(error), time_vec)

        # Integral Time Squared Error
        itse = integrate.trapz(time_vec * error**2, time_vec)

        return {
            'iae': iae,
            'ise': ise,
            'itae': itae,
            'itse': itse
        }

    def calculate_step_response_metrics(self, data: TimeSeriesData) -> Dict[str, float]:
        """Calculate step response characteristics"""

        pv = data.process_variable
        time_vec = data.time

        # Find steady state value (last 10% of data)
        steady_start = int(len(pv) * (1 - self.config.steady_state_window))
        steady_state = np.mean(pv[steady_start:])
        initial_value = pv[0]

        # Step change magnitude
        step_magnitude = np.abs(steady_state - initial_value)

        if step_magnitude < 1e-6:
            # No significant step change
            return {
                'settling_time': 0.0,
                'overshoot': 0.0,
                'undershoot': 0.0,
                'rise_time': 0.0,
                'peak_time': 0.0
            }

        # Calculate overshoot/undershoot
        if steady_state > initial_value:
            # Positive step
            peak_value = np.max(pv)
            valley_value = np.min(pv)
            overshoot = max(0, (peak_value - steady_state) / step_magnitude)
            undershoot = max(0, (initial_value - valley_value) / step_magnitude)
            peak_idx = np.argmax(pv)
        else:
            # Negative step
            peak_value = np.min(pv)
            valley_value = np.max(pv)
            overshoot = max(0, (steady_state - peak_value) / step_magnitude)
            undershoot = max(0, (valley_value - initial_value) / step_magnitude)
            peak_idx = np.argmin(pv)

        peak_time = time_vec[peak_idx]

        # Calculate rise time (10% to 90% of final value)
        value_10 = initial_value + 0.1 * (steady_state - initial_value)
        value_90 = initial_value + 0.9 * (steady_state - initial_value)

        if steady_state > initial_value:
            idx_10 = np.where(pv >= value_10)[0]
            idx_90 = np.where(pv >= value_90)[0]
        else:
            idx_10 = np.where(pv <= value_10)[0]
            idx_90 = np.where(pv <= value_90)[0]

        rise_time = 0.0
        if len(idx_10) > 0 and len(idx_90) > 0:
            rise_time = time_vec[idx_90[0]] - time_vec[idx_10[0]]

        # Calculate settling time
        settling_band = self.config.settling_criteria * step_magnitude
        settling_time = self._calculate_settling_time(
            time_vec, pv, steady_state, settling_band
        )

        return {
            'settling_time': settling_time,
            'overshoot': overshoot,
            'undershoot': undershoot,
            'rise_time': rise_time,
            'peak_time': peak_time
        }

    def _calculate_settling_time(self, time_vec: np.ndarray, pv: np.ndarray,
                                steady_state: float, settling_band: float) -> float:
        """Calculate settling time within specified band"""

        # Find last time point outside settling band
        outside_band = np.abs(pv - steady_state) > settling_band

        if not np.any(outside_band):
            return 0.0  # Already settled

        # Find last index outside band
        last_outside_idx = np.where(outside_band)[0][-1]

        # Check for sustained settling (minimum samples in band)
        settling_start = last_outside_idx + 1
        if settling_start >= len(time_vec):
            return time_vec[-1]

        # Verify sustained settling
        remaining_samples = len(time_vec) - settling_start
        if remaining_samples >= self.config.min_settling_samples:
            return time_vec[settling_start]
        else:
            return time_vec[-1]  # Not enough samples to confirm settling

class FrequencyDomainMetrics:
    """Frequency domain performance metrics calculator"""

    def __init__(self, configuration: Optional[PerformanceConfiguration] = None):
        self.config = configuration or PerformanceConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calculate_margins(self, num: np.ndarray, den: np.ndarray,
                         sample_time: Optional[float] = None) -> Dict[str, float]:
        """Calculate gain and phase margins from transfer function"""

        try:
            # Create transfer function
            if sample_time is not None:
                # Discrete system
                sys = signal.TransferFunction(num, den, dt=sample_time)
            else:
                # Continuous system
                sys = signal.TransferFunction(num, den)

            # Calculate frequency response
            if sample_time is not None:
                # For discrete systems, use appropriate frequency range
                w = np.logspace(-3, np.log10(np.pi/sample_time), self.config.frequency_points)
            else:
                w = np.logspace(-3, 3, self.config.frequency_points)

            w, h = signal.freqresp(sys, w)
            magnitude_db = 20 * np.log10(np.abs(h))
            phase_deg = np.angle(h) * 180 / np.pi

            # Unwrap phase for better analysis
            phase_deg = np.unwrap(phase_deg * np.pi / 180) * 180 / np.pi

            # Find gain crossover frequency (|H| = 1, or 0 dB)
            gain_crossover_idx = self._find_crossover(magnitude_db, 0.0)
            if gain_crossover_idx is not None:
                gain_crossover_freq = w[gain_crossover_idx]
                phase_margin = 180 + phase_deg[gain_crossover_idx]
            else:
                gain_crossover_freq = 0.0
                phase_margin = 0.0

            # Find phase crossover frequency (phase = -180°)
            phase_crossover_idx = self._find_crossover(phase_deg, -180.0)
            if phase_crossover_idx is not None:
                phase_crossover_freq = w[phase_crossover_idx]
                gain_margin_db = -magnitude_db[phase_crossover_idx]
            else:
                phase_crossover_freq = 0.0
                gain_margin_db = float('inf')

            return {
                'gain_margin': gain_margin_db,
                'phase_margin': phase_margin,
                'gain_crossover_freq': gain_crossover_freq,
                'phase_crossover_freq': phase_crossover_freq
            }

        except Exception as e:
            self.logger.warning(f"Frequency domain analysis failed: {e}")
            return {
                'gain_margin': 0.0,
                'phase_margin': 0.0,
                'gain_crossover_freq': 0.0,
                'phase_crossover_freq': 0.0
            }

    def _find_crossover(self, data: np.ndarray, target: float) -> Optional[int]:
        """Find index where data crosses target value"""

        diff = data - target
        sign_changes = np.diff(np.sign(diff))
        crossover_indices = np.where(sign_changes != 0)[0]

        if len(crossover_indices) > 0:
            return crossover_indices[0]
        return None

class ControlEffortAnalyzer:
    """Control effort and efficiency analyzer"""

    def __init__(self, configuration: Optional[PerformanceConfiguration] = None):
        self.config = configuration or PerformanceConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calculate_control_effort(self, data: TimeSeriesData) -> Dict[str, float]:
        """Calculate control effort metrics"""

        control_signal = data.control_output
        time_vec = data.time

        # Total control effort (integral of squared control signal)
        control_effort = integrate.trapz(control_signal**2, time_vec)

        # Control signal variation (total variation)
        control_variation = np.sum(np.abs(np.diff(control_signal)))

        # Normalized control effort
        if self.config.effort_normalization:
            signal_range = np.max(control_signal) - np.min(control_signal)
            if signal_range > 1e-6:
                control_effort_normalized = control_effort / (signal_range**2)
                control_variation_normalized = control_variation / signal_range
            else:
                control_effort_normalized = 0.0
                control_variation_normalized = 0.0
        else:
            control_effort_normalized = control_effort
            control_variation_normalized = control_variation

        # Control efficiency (performance per unit effort)
        error_magnitude = np.mean(np.abs(data.error)) if data.error is not None else 1.0
        if control_effort > 1e-6:
            efficiency = 1.0 / (error_magnitude * control_effort_normalized + 1e-6)
        else:
            efficiency = 1.0

        return {
            'control_effort': control_effort_normalized,
            'control_variation': control_variation_normalized,
            'efficiency_index': efficiency
        }

class RobustnessAnalyzer:
    """Robustness and stability analyzer"""

    def __init__(self, configuration: Optional[PerformanceConfiguration] = None):
        self.config = configuration or PerformanceConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calculate_robustness_index(self, gain_margin: float, phase_margin: float,
                                  sensitivity_peak: Optional[float] = None) -> float:
        """Calculate combined robustness index"""

        # Normalize margins to 0-1 scale
        gm_normalized = min(1.0, max(0.0, (gain_margin - 3.0) / 15.0))  # 3-18 dB range
        pm_normalized = min(1.0, max(0.0, (phase_margin - 30.0) / 60.0))  # 30-90 deg range

        # Weight gain and phase margins
        robustness_base = 0.6 * gm_normalized + 0.4 * pm_normalized

        # Include sensitivity peak if available
        if sensitivity_peak is not None:
            # Lower sensitivity peak is better (typical range 1-6)
            sens_normalized = min(1.0, max(0.0, (6.0 - sensitivity_peak) / 5.0))
            robustness_index = 0.7 * robustness_base + 0.3 * sens_normalized
        else:
            robustness_index = robustness_base

        return robustness_index

class PerformanceMetricsCalculator:
    """Main performance metrics calculator orchestrator"""

    def __init__(self, configuration: Optional[PerformanceConfiguration] = None):
        self.config = configuration or PerformanceConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Component analyzers
        self.time_domain = TimeDomainMetrics(self.config)
        self.frequency_domain = FrequencyDomainMetrics(self.config)
        self.control_effort = ControlEffortAnalyzer(self.config)
        self.robustness = RobustnessAnalyzer(self.config)

    def analyze_performance(self, data: TimeSeriesData,
                          transfer_function: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> PerformanceResults:
        """Comprehensive performance analysis"""

        try:
            start_time = time.time()

            # Validate and prepare data
            validated_data = self._validate_data(data)
            data_quality = self._assess_data_quality(validated_data)

            # Calculate time domain metrics
            error_metrics = self.time_domain.calculate_error_metrics(validated_data)
            step_metrics = self.time_domain.calculate_step_response_metrics(validated_data)

            # Calculate control effort metrics
            effort_metrics = self.control_effort.calculate_control_effort(validated_data)

            # Calculate frequency domain metrics if transfer function provided
            if transfer_function is not None:
                freq_metrics = self.frequency_domain.calculate_margins(
                    transfer_function[0], transfer_function[1], validated_data.sample_time
                )
            else:
                freq_metrics = {
                    'gain_margin': 0.0,
                    'phase_margin': 0.0,
                    'gain_crossover_freq': 0.0,
                    'phase_crossover_freq': 0.0
                }

            # Calculate robustness index
            robustness_index = self.robustness.calculate_robustness_index(
                freq_metrics['gain_margin'], freq_metrics['phase_margin']
            )

            # Calculate overall performance index
            performance_index = self._calculate_performance_index(
                error_metrics, step_metrics, effort_metrics, freq_metrics
            )

            analysis_time = time.time() - start_time

            # Create results
            results = PerformanceResults(
                # Time domain metrics
                iae=error_metrics['iae'],
                ise=error_metrics['ise'],
                itae=error_metrics['itae'],
                itse=error_metrics['itse'],

                # Step response metrics
                settling_time=step_metrics['settling_time'],
                overshoot=step_metrics['overshoot'],
                undershoot=step_metrics['undershoot'],
                rise_time=step_metrics['rise_time'],
                peak_time=step_metrics['peak_time'],

                # Control effort metrics
                control_effort=effort_metrics['control_effort'],
                control_variation=effort_metrics['control_variation'],

                # Frequency domain metrics
                gain_margin=freq_metrics['gain_margin'],
                phase_margin=freq_metrics['phase_margin'],
                gain_crossover_freq=freq_metrics['gain_crossover_freq'],
                phase_crossover_freq=freq_metrics['phase_crossover_freq'],

                # Overall metrics
                performance_index=performance_index,
                robustness_index=robustness_index,
                efficiency_index=effort_metrics['efficiency_index'],

                # Metadata
                analysis_time=analysis_time,
                data_quality=data_quality,
                configuration=self.config
            )

            return results

        except Exception as e:
            self.logger.error(f"Performance analysis failed: {e}")
            raise

    def _validate_data(self, data: TimeSeriesData) -> TimeSeriesData:
        """Validate and clean time series data"""

        # Ensure all arrays have same length
        min_length = min(len(data.time), len(data.setpoint), len(data.process_variable), len(data.control_output))

        validated_data = TimeSeriesData(
            time=data.time[:min_length],
            setpoint=data.setpoint[:min_length],
            process_variable=data.process_variable[:min_length],
            control_output=data.control_output[:min_length],
            sample_time=data.sample_time
        )

        # Calculate error if not provided
        if data.error is None:
            validated_data.error = validated_data.setpoint - validated_data.process_variable
        else:
            validated_data.error = data.error[:min_length]

        # Estimate sample time if not provided
        if validated_data.sample_time is None:
            validated_data.sample_time = np.mean(np.diff(validated_data.time))

        return validated_data

    def _assess_data_quality(self, data: TimeSeriesData) -> float:
        """Assess quality of time series data"""

        quality_score = 1.0

        # Check for missing data
        if np.any(np.isnan(data.process_variable)) or np.any(np.isnan(data.control_output)):
            quality_score *= 0.8

        # Check time vector consistency
        time_diffs = np.diff(data.time)
        time_consistency = np.std(time_diffs) / np.mean(time_diffs) if np.mean(time_diffs) > 0 else 1.0
        if time_consistency > 0.1:  # >10% variation in sampling
            quality_score *= 0.9

        # Check for data range
        pv_range = np.max(data.process_variable) - np.min(data.process_variable)
        if pv_range < 1e-6:  # Very small signal range
            quality_score *= 0.7

        # Check for sufficient data length
        if len(data.time) < 100:  # Less than 100 samples
            quality_score *= 0.8

        return max(0.0, min(1.0, quality_score))

    def _calculate_performance_index(self, error_metrics: dict, step_metrics: dict,
                                   effort_metrics: dict, freq_metrics: dict) -> float:
        """Calculate overall performance index"""

        # Normalize individual metrics (lower is better for most)
        iae_score = min(1.0, max(0.0, 1.0 - error_metrics['iae'] / 100.0))
        settling_score = min(1.0, max(0.0, 1.0 - step_metrics['settling_time'] / 120.0))
        overshoot_score = min(1.0, max(0.0, 1.0 - step_metrics['overshoot'] / 0.3))
        effort_score = min(1.0, max(0.0, 1.0 - effort_metrics['control_effort'] / 1000.0))

        # Frequency domain scores (higher is better)
        gm_score = min(1.0, max(0.0, (freq_metrics['gain_margin'] - 3.0) / 15.0))
        pm_score = min(1.0, max(0.0, (freq_metrics['phase_margin'] - 30.0) / 60.0))

        # Weighted combination
        performance_index = (
            0.25 * iae_score +
            0.2 * settling_score +
            0.15 * overshoot_score +
            0.15 * effort_score +
            0.15 * gm_score +
            0.1 * pm_score
        )

        return performance_index
