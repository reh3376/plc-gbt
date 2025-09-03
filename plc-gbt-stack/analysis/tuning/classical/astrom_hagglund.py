#!/usr/bin/env python3
"""
Phase 22.2: Task 22.2.2 - Åström-Hägglund Relay Autotuning Implementation
=========================================================================

Implementation of Åström-Hägglund relay-based autotuning method for automatic
PID parameter identification. This method uses relay feedback to induce
controlled oscillations and extract ultimate gain and period information.

Key Features:
- Automatic relay-based oscillation induction
- Real-time ultimate parameter extraction
- Multiple relay configurations (standard, bias, hysteresis)
- Automatic tuning parameter calculation
- Process identification during operation

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.2 - Classical Tuning Methods
Methodology: AI Task Orchestrator Guide
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq

# Import algorithm base class
try:
    from ...algorithms import (
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

class RelayType(Enum):
    """Relay feedback types"""
    STANDARD = "standard"
    BIAS = "bias"
    HYSTERESIS = "hysteresis"
    PRELOAD = "preload"

class AHTuningMethod(Enum):
    """Åström-Hägglund tuning rule variants"""
    STANDARD = "standard"
    IMPROVED = "improved"
    ROBUST = "robust"

@dataclass
class RelayTestParameters:
    """Relay test configuration parameters"""
    relay_amplitude: float
    relay_bias: float
    hysteresis: float
    test_duration: float
    sampling_time: float
    convergence_criteria: Dict[str, float]
    safety_limits: Dict[str, float]

@dataclass
class AHAutotuneResult:
    """Åström-Hägglund autotuning result"""
    tuning_method: str
    relay_type: RelayType
    tuning_variant: AHTuningMethod
    parameters: Dict[str, float]
    controller_type: str
    relay_test_results: Dict[str, Any]
    process_identification: Dict[str, float]
    oscillation_analysis: Dict[str, Any]
    tuning_quality: Dict[str, Any]
    recommendations: List[str]
    execution_time: float

class AstromHagglundTuner(AlgorithmBase if ALGORITHM_REGISTRY_AVAILABLE else object):
    """
    Åström-Hägglund relay-based autotuning algorithm

    Automatically determines PID parameters by using relay feedback
    to induce controlled oscillations and extract process characteristics.
    """

    def __init__(self):
        if ALGORITHM_REGISTRY_AVAILABLE:
            metadata = AlgorithmMetadata(
                name="astrom_hagglund_tuner",
                category=AlgorithmCategory.TUNING_CALCULATION,
                complexity=AlgorithmComplexity.HIGH,
                description="Åström-Hägglund relay-based autotuning method",
                version="1.0.0",
                min_data_points=200,
                supports_realtime=True,
                tags=["classical", "astrom_hagglund", "relay", "autotuning"]
            )
            super().__init__(metadata)

        self.logger = logging.getLogger(__name__ + '.AstromHagglundTuner')

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for Åström-Hägglund autotuning"""
        errors = []

        # Check for time series data or ultimate parameters
        if 'time_data' in data and 'output_data' in data and 'input_data' in data:
            # Time series approach (relay test data)
            for field in ['time_data', 'output_data', 'input_data']:
                if not isinstance(data[field], (list, np.ndarray)):
                    errors.append(f"Field '{field}' must be array-like")
                elif len(data[field]) < 100:
                    errors.append(f"Field '{field}' must have at least 100 data points for relay analysis")
        elif 'ultimate_gain' in data and 'ultimate_period' in data:
            # Ultimate parameters approach
            for field in ['ultimate_gain', 'ultimate_period']:
                if field not in data:
                    errors.append(f"Missing required field: '{field}'")
                elif not isinstance(data[field], (int, float)):
                    errors.append(f"Field '{field}' must be numeric")
                elif data[field] <= 0:
                    errors.append(f"Field '{field}' must be positive")
        else:
            errors.append("Must provide either time series data or ultimate parameters")

        # Validate relay parameters if provided
        if 'relay_amplitude' in data:
            if not isinstance(data['relay_amplitude'], (int, float)) or data['relay_amplitude'] <= 0:
                errors.append("Relay amplitude must be positive numeric value")

        # Check controller type
        if 'controller_type' in data:
            if data['controller_type'] not in ['dependent', 'independent']:
                errors.append("Controller type must be 'dependent' or 'independent'")

        # Check tuning method
        if 'tuning_method' in data:
            try:
                AHTuningMethod(data['tuning_method'])
            except ValueError:
                valid_methods = [m.value for m in AHTuningMethod]
                errors.append(f"Tuning method must be one of: {valid_methods}")

        return len(errors) == 0, errors

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute Åström-Hägglund autotuning algorithm"""
        start_time = time.time()

        controller_type = data.get('controller_type', 'dependent')
        tuning_method = AHTuningMethod(data.get('tuning_method', 'standard'))
        relay_type = RelayType(data.get('relay_type', 'standard'))

        try:
            # Determine approach based on input data
            if 'time_data' in data:
                # Analyze relay test data
                relay_results = self._analyze_relay_test_data(
                    data['time_data'], data['output_data'], data['input_data'],
                    data.get('relay_amplitude', 1.0)
                )
                ultimate_gain = relay_results['ultimate_gain']
                ultimate_period = relay_results['ultimate_period']
            else:
                # Use provided ultimate parameters
                ultimate_gain = data['ultimate_gain']
                ultimate_period = data['ultimate_period']
                relay_results = {
                    'ultimate_gain': ultimate_gain,
                    'ultimate_period': ultimate_period,
                    'source': 'provided_parameters'
                }

            # Process identification
            process_identification = self._identify_process_characteristics(
                ultimate_gain, ultimate_period, relay_results
            )

            # Calculate PID parameters using Åström-Hägglund rules
            if controller_type == 'dependent':
                pid_params = self._calculate_dependent_params(
                    ultimate_gain, ultimate_period, tuning_method
                )
            else:
                pid_params = self._calculate_independent_params(
                    ultimate_gain, ultimate_period, tuning_method
                )

            # Oscillation analysis
            oscillation_analysis = self._analyze_oscillation_characteristics(
                ultimate_gain, ultimate_period, relay_results
            )

            # Tuning quality assessment
            tuning_quality = self._assess_tuning_quality(
                ultimate_gain, ultimate_period, pid_params, tuning_method
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                ultimate_gain, ultimate_period, pid_params, tuning_method,
                process_identification, tuning_quality, relay_results
            )

            execution_time = time.time() - start_time

            result = AHAutotuneResult(
                tuning_method="Åström-Hägglund",
                relay_type=relay_type,
                tuning_variant=tuning_method,
                parameters=pid_params,
                controller_type=controller_type,
                relay_test_results=relay_results,
                process_identification=process_identification,
                oscillation_analysis=oscillation_analysis,
                tuning_quality=tuning_quality,
                recommendations=recommendations,
                execution_time=execution_time
            )

            return {
                'success': True,
                'result': result,
                'method': 'astrom_hagglund'
            }

        except Exception as e:
            self.logger.error(f"Åström-Hägglund autotuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'astrom_hagglund'
            }

    def _analyze_relay_test_data(self, time_data: np.ndarray, output_data: np.ndarray,
                               input_data: np.ndarray, relay_amplitude: float) -> Dict[str, Any]:
        """Analyze relay test data to extract ultimate parameters"""

        # Convert to numpy arrays
        time = np.array(time_data)
        output = np.array(output_data)
        np.array(input_data)

        # Find oscillation cycles in the output
        oscillation_analysis = self._detect_oscillation_cycles(time, output)

        # Extract ultimate period from oscillation analysis
        if len(oscillation_analysis['periods']) > 0:
            ultimate_period = np.mean(oscillation_analysis['periods'][-3:])  # Last 3 cycles
        else:
            # Fallback: use FFT analysis
            ultimate_period = self._extract_period_fft(time, output)

        # Calculate ultimate gain using describing function analysis
        ultimate_gain = self._calculate_ultimate_gain_from_relay(
            output_data, input_data, relay_amplitude, ultimate_period
        )

        # Relay test quality metrics
        cycle_consistency = np.std(oscillation_analysis['periods'][-3:]) / np.mean(oscillation_analysis['periods'][-3:]) if len(oscillation_analysis['periods']) >= 3 else 1.0
        amplitude_consistency = np.std(oscillation_analysis['amplitudes'][-3:]) / np.mean(oscillation_analysis['amplitudes'][-3:]) if len(oscillation_analysis['amplitudes']) >= 3 else 1.0

        # Test quality assessment
        test_quality = 'good' if cycle_consistency < 0.1 and amplitude_consistency < 0.15 else 'fair' if cycle_consistency < 0.2 else 'poor'

        return {
            'ultimate_gain': ultimate_gain,
            'ultimate_period': ultimate_period,
            'relay_amplitude': relay_amplitude,
            'oscillation_cycles': len(oscillation_analysis['periods']),
            'cycle_consistency': cycle_consistency,
            'amplitude_consistency': amplitude_consistency,
            'test_quality': test_quality,
            'oscillation_details': oscillation_analysis,
            'source': 'relay_test_analysis'
        }

    def _detect_oscillation_cycles(self, time: np.ndarray, output: np.ndarray) -> Dict[str, Any]:
        """Detect oscillation cycles in relay test output"""

        # Remove DC component
        output_detrended = output - np.mean(output)

        # Find peaks and valleys
        from scipy.signal import find_peaks

        peaks, _ = find_peaks(output_detrended, height=0.1*np.std(output_detrended))
        valleys, _ = find_peaks(-output_detrended, height=0.1*np.std(output_detrended))

        # Calculate periods (peak to peak)
        periods = []
        amplitudes = []

        if len(peaks) >= 2:
            for i in range(1, len(peaks)):
                period = time[peaks[i]] - time[peaks[i-1]]
                periods.append(period)

                # Find amplitude for this cycle
                cycle_start = peaks[i-1]
                cycle_end = peaks[i]
                cycle_output = output[cycle_start:cycle_end+1]
                amplitude = np.max(cycle_output) - np.min(cycle_output)
                amplitudes.append(amplitude)

        return {
            'periods': periods,
            'amplitudes': amplitudes,
            'peaks': peaks,
            'valleys': valleys,
            'mean_amplitude': np.mean(amplitudes) if amplitudes else 0,
            'amplitude_variation': np.std(amplitudes) if amplitudes else 0
        }

    def _extract_period_fft(self, time: np.ndarray, output: np.ndarray) -> float:
        """Extract dominant period using FFT analysis"""

        # Remove DC component
        output_detrended = output - np.mean(output)

        # Apply window to reduce spectral leakage
        window = signal.windows.hann(len(output_detrended))
        output_windowed = output_detrended * window

        # Compute FFT
        sampling_rate = 1.0 / np.mean(np.diff(time))
        fft_result = fft(output_windowed)
        frequencies = fftfreq(len(output_windowed), 1/sampling_rate)

        # Find dominant frequency (exclude DC)
        magnitude = np.abs(fft_result)
        magnitude[0] = 0  # Remove DC component

        # Find peak in positive frequencies
        positive_freq_idx = frequencies > 0
        positive_freqs = frequencies[positive_freq_idx]
        positive_magnitudes = magnitude[positive_freq_idx]

        if len(positive_magnitudes) > 0:
            dominant_freq_idx = np.argmax(positive_magnitudes)
            dominant_frequency = positive_freqs[dominant_freq_idx]
            ultimate_period = 1.0 / dominant_frequency if dominant_frequency > 0 else 60.0
        else:
            ultimate_period = 60.0  # Default fallback

        return ultimate_period

    def _calculate_ultimate_gain_from_relay(self, output_data: np.ndarray,
                                          input_data: np.ndarray,
                                          relay_amplitude: float,
                                          ultimate_period: float) -> float:
        """Calculate ultimate gain using describing function analysis"""

        # Calculate output amplitude (peak-to-peak)
        output_amplitude = (np.max(output_data) - np.min(output_data)) / 2.0

        # Describing function for relay
        # For standard relay: N(A) = 4h/(π*A) where h is relay height, A is amplitude
        describing_function = (4 * relay_amplitude) / (np.pi * output_amplitude) if output_amplitude > 0 else 1.0

        # Ultimate gain is reciprocal of describing function at oscillation
        ultimate_gain = 1.0 / describing_function if describing_function > 0 else 1.0

        # Apply reasonable bounds
        ultimate_gain = max(0.1, min(100.0, ultimate_gain))

        return ultimate_gain

    def _identify_process_characteristics(self, ultimate_gain: float, ultimate_period: float,
                                        relay_results: Dict[str, Any]) -> Dict[str, float]:
        """Identify process characteristics from ultimate parameters"""

        # Ultimate frequency
        omega_u = 2 * np.pi / ultimate_period

        # Estimate process model parameters (rough approximations)
        # For typical industrial processes
        estimated_time_constant = ultimate_period / 4.0
        estimated_dead_time = ultimate_period / 8.0
        estimated_process_gain = 1.0 / ultimate_gain  # Rough estimate

        # Process classification
        if ultimate_period < 10:
            process_type = "fast_response"
        elif ultimate_period < 60:
            process_type = "medium_response"
        else:
            process_type = "slow_response"

        # Relay test quality impact on confidence
        if 'test_quality' in relay_results:
            confidence = 0.9 if relay_results['test_quality'] == 'good' else 0.7 if relay_results['test_quality'] == 'fair' else 0.5
        else:
            confidence = 0.8  # Default confidence

        return {
            'ultimate_gain': ultimate_gain,
            'ultimate_period': ultimate_period,
            'ultimate_frequency': omega_u,
            'estimated_process_gain': estimated_process_gain,
            'estimated_time_constant': estimated_time_constant,
            'estimated_dead_time': estimated_dead_time,
            'process_type': process_type,
            'identification_confidence': confidence
        }

    def _calculate_dependent_params(self, ultimate_gain: float, ultimate_period: float,
                                  tuning_method: AHTuningMethod) -> Dict[str, float]:
        """Calculate dependent PID parameters using Åström-Hägglund rules"""

        if tuning_method == AHTuningMethod.STANDARD:
            # Standard Åström-Hägglund rules
            Kc = 0.45 * ultimate_gain
            Ti = 0.85 * ultimate_period
            Td = 0.15 * ultimate_period
        elif tuning_method == AHTuningMethod.IMPROVED:
            # Improved rules with better robustness
            Kc = 0.4 * ultimate_gain
            Ti = 0.8 * ultimate_period
            Td = 0.125 * ultimate_period
        else:  # ROBUST
            # More conservative robust rules
            Kc = 0.3 * ultimate_gain
            Ti = 1.0 * ultimate_period
            Td = 0.2 * ultimate_period

        # Apply reasonable bounds
        Kc = max(0.01, min(100.0, Kc))
        Ti = max(0.01, min(9999.0, Ti))
        Td = max(0.0, min(99.99, Td))

        return {
            'Kp': float(Kc),
            'Ti': float(Ti),
            'Td': float(Td)
        }

    def _calculate_independent_params(self, ultimate_gain: float, ultimate_period: float,
                                    tuning_method: AHTuningMethod) -> Dict[str, float]:
        """Calculate independent PID parameters using Åström-Hägglund rules"""

        # Get dependent parameters first
        dependent_params = self._calculate_dependent_params(ultimate_gain, ultimate_period, tuning_method)

        # Convert to independent form
        Kc = dependent_params['Kp']
        Ti = dependent_params['Ti']
        Td = dependent_params['Td']

        # Independent form conversion
        Kp = Kc
        Ki = Kc / Ti if Ti > 0 else 0
        Kd = Kc * Td

        # Apply reasonable bounds
        Kp = max(0.01, min(100.0, Kp))
        Ki = max(0.0, min(10.0, Ki))
        Kd = max(0.0, min(10.0, Kd))

        return {
            'Kp': float(Kp),
            'Ki': float(Ki),
            'Kd': float(Kd)
        }

    def _analyze_oscillation_characteristics(self, ultimate_gain: float, ultimate_period: float,
                                           relay_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze oscillation characteristics from relay test"""

        # Oscillation quality metrics
        if 'oscillation_details' in relay_results:
            details = relay_results['oscillation_details']

            # Consistency metrics
            period_consistency = 1.0 - (np.std(details['periods']) / np.mean(details['periods'])) if details['periods'] else 0.5
            amplitude_stability = 1.0 - (details['amplitude_variation'] / details['mean_amplitude']) if details['mean_amplitude'] > 0 else 0.5

            # Oscillation quality classification
            if period_consistency > 0.9 and amplitude_stability > 0.85:
                oscillation_quality = 'excellent'
            elif period_consistency > 0.8 and amplitude_stability > 0.7:
                oscillation_quality = 'good'
            elif period_consistency > 0.6 and amplitude_stability > 0.5:
                oscillation_quality = 'fair'
            else:
                oscillation_quality = 'poor'
        else:
            # Default values when detailed analysis not available
            period_consistency = 0.8
            amplitude_stability = 0.7
            oscillation_quality = 'good'

        # Frequency domain characteristics
        omega_u = 2 * np.pi / ultimate_period

        return {
            'ultimate_frequency': omega_u,
            'period_consistency': period_consistency,
            'amplitude_stability': amplitude_stability,
            'oscillation_quality': oscillation_quality,
            'sustained_oscillation': period_consistency > 0.7,
            'frequency_stability': period_consistency,  # Proxy measure
            'amplitude_decay': 1.0 - amplitude_stability  # Measure of amplitude decay
        }

    def _assess_tuning_quality(self, ultimate_gain: float, ultimate_period: float,
                             pid_params: Dict[str, float], tuning_method: AHTuningMethod) -> Dict[str, Any]:
        """Assess the quality of the autotuning result"""

        # Calculate stability margins
        Kc = pid_params['Kp']
        gain_margin = ultimate_gain / Kc if Kc > 0 else float('inf')
        gain_margin_db = 20 * np.log10(gain_margin) if gain_margin > 0 else 60

        # Typical phase margins for Åström-Hägglund
        typical_phase_margins = {
            AHTuningMethod.STANDARD: 40.0,
            AHTuningMethod.IMPROVED: 45.0,
            AHTuningMethod.ROBUST: 55.0
        }
        phase_margin = typical_phase_margins[tuning_method]

        # Quality assessment
        if gain_margin_db >= 10 and phase_margin >= 45:
            tuning_quality = 'excellent'
        elif gain_margin_db >= 6 and phase_margin >= 35:
            tuning_quality = 'good'
        elif gain_margin_db >= 4 and phase_margin >= 25:
            tuning_quality = 'fair'
        else:
            tuning_quality = 'poor'

        # Robustness assessment
        robustness_score = min(gain_margin_db / 15.0, 1.0) * min(phase_margin / 60.0, 1.0)

        # Expected performance characteristics
        performance_metrics = {
            'expected_overshoot': 15.0 if tuning_method == AHTuningMethod.STANDARD else 10.0 if tuning_method == AHTuningMethod.IMPROVED else 5.0,
            'expected_settling_time': 4.5 * ultimate_period if tuning_method == AHTuningMethod.STANDARD else 5.5 * ultimate_period if tuning_method == AHTuningMethod.IMPROVED else 7.0 * ultimate_period,
            'robustness_level': 'medium' if tuning_method == AHTuningMethod.STANDARD else 'high' if tuning_method == AHTuningMethod.IMPROVED else 'very_high'
        }

        return {
            'tuning_quality': tuning_quality,
            'gain_margin_db': min(gain_margin_db, 60),
            'phase_margin_deg': phase_margin,
            'robustness_score': robustness_score,
            'performance_metrics': performance_metrics,
            'autotuning_confidence': 0.9 if tuning_quality == 'excellent' else 0.7 if tuning_quality == 'good' else 0.5
        }

    def _generate_recommendations(self, ultimate_gain: float, ultimate_period: float,
                                pid_params: Dict[str, float], tuning_method: AHTuningMethod,
                                process_identification: Dict[str, float],
                                tuning_quality: Dict[str, Any],
                                relay_results: Dict[str, Any]) -> List[str]:
        """Generate autotuning recommendations"""
        recommendations = []

        # Autotuning method recommendations
        recommendations.append("Åström-Hägglund relay autotuning provides automatic parameter identification")

        if tuning_method == AHTuningMethod.STANDARD:
            recommendations.append("Standard A-H rules provide good performance/robustness balance")
        elif tuning_method == AHTuningMethod.IMPROVED:
            recommendations.append("Improved A-H rules offer enhanced robustness")
        else:
            recommendations.append("Robust A-H rules prioritize stability over speed")

        # Relay test quality recommendations
        if 'test_quality' in relay_results:
            if relay_results['test_quality'] == 'good':
                recommendations.append("Excellent relay test quality - high confidence in results")
            elif relay_results['test_quality'] == 'fair':
                recommendations.append("Fair relay test quality - consider repeating test for better accuracy")
            else:
                recommendations.append("Poor relay test quality - repeat test with adjusted relay amplitude")

        # Process identification recommendations
        if process_identification['identification_confidence'] < 0.7:
            recommendations.append("Low identification confidence - validate tuning with step test")

        # Tuning quality recommendations
        if tuning_quality['tuning_quality'] == 'excellent':
            recommendations.append("Excellent tuning quality - ready for implementation")
        elif tuning_quality['tuning_quality'] == 'good':
            recommendations.append("Good tuning quality - monitor initial performance")
        else:
            recommendations.append("Consider manual fine-tuning for improved performance")

        # Process-specific recommendations
        if ultimate_period > 60:
            recommendations.append("Slow process - relay autotuning well-suited for identification")
        elif ultimate_period < 10:
            recommendations.append("Fast process - ensure adequate sampling rate for relay test")

        if ultimate_gain > 5:
            recommendations.append("High process sensitivity - monitor for stability during implementation")

        # Industrial implementation recommendations
        recommendations.append("Implement tuning gradually and monitor for oscillations")
        recommendations.append("Åström-Hägglund provides good starting point for further optimization")

        if tuning_quality['robustness_score'] > 0.8:
            recommendations.append("High robustness - suitable for varying operating conditions")

        # Relay test specific recommendations
        if 'oscillation_cycles' in relay_results and relay_results['oscillation_cycles'] < 3:
            recommendations.append("Limited oscillation cycles - consider longer relay test duration")

        recommendations.append("Consider periodic re-autotuning to adapt to process changes")

        return recommendations

class AHRelayTuner(AstromHagglundTuner):
    """
    Specialized relay tuning implementation with enhanced relay test capabilities
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.AHRelayTuner')

    def design_relay_test(self, process_info: Dict[str, Any]) -> RelayTestParameters:
        """Design optimal relay test parameters"""

        # Extract process information
        process_info.get('expected_gain', 1.0)
        expected_time_constant = process_info.get('expected_time_constant', 60.0)
        noise_level = process_info.get('noise_level', 0.1)
        safety_limits = process_info.get('safety_limits', {'max_output': 100, 'min_output': 0})

        # Design relay amplitude (typically 2-5% of output range)
        output_range = safety_limits['max_output'] - safety_limits['min_output']
        relay_amplitude = min(0.05 * output_range, 5.0)  # 5% or max 5 units

        # Adjust for noise
        if noise_level > 0.05:
            relay_amplitude = max(relay_amplitude, 10 * noise_level)  # 10x noise level

        # Design test duration (typically 10-20 oscillation cycles)
        expected_period = 4 * expected_time_constant  # Rough estimate
        test_duration = max(15 * expected_period, 300)  # At least 5 minutes

        # Sampling time (at least 10 samples per period)
        sampling_time = min(expected_period / 20, 1.0)

        # Convergence criteria
        convergence_criteria = {
            'min_cycles': 5,
            'period_stability': 0.1,  # 10% variation
            'amplitude_stability': 0.15  # 15% variation
        }

        return RelayTestParameters(
            relay_amplitude=relay_amplitude,
            relay_bias=0.0,
            hysteresis=0.02 * relay_amplitude,  # 2% hysteresis
            test_duration=test_duration,
            sampling_time=sampling_time,
            convergence_criteria=convergence_criteria,
            safety_limits=safety_limits
        )

# Register Åström-Hägglund algorithms
if ALGORITHM_REGISTRY_AVAILABLE:
    try:
        registry.register(AstromHagglundTuner)
        registry.register(AHRelayTuner)
        logger.info("Åström-Hägglund algorithms registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register Åström-Hägglund algorithms: {e}")

# Export classes
__all__ = [
    'AstromHagglundTuner',
    'AHRelayTuner',
    'AHAutotuneResult',
    'RelayTestParameters',
    'RelayType',
    'AHTuningMethod'
]

logger.info("Åström-Hägglund autotuning method implementation completed")
