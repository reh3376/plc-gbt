#!/usr/bin/env python3
"""
Phase 22.1.3: Step Detection Algorithms
======================================

Advanced step detection algorithms for control loop analysis, building upon
the proven detect_steps() methodology from pid_analysis_bundle.py with
enhanced capabilities:

- Enhanced natural step detection
- Machine learning-based step detection
- Multi-variable step detection
- Step validation and quality assessment
- Real-time step detection for streaming data

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import stats
from scipy.signal import find_peaks, savgol_filter
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from . import AlgorithmBase, AlgorithmCategory, AlgorithmComplexity, AlgorithmMetadata, registry

logger = logging.getLogger(__name__)

@dataclass
class StepDetectionResult:
    """Results from step detection analysis"""
    step_times: List[float]
    step_magnitudes: List[float]
    step_confidence: List[float]
    baseline_values: List[float]
    final_values: List[float]
    step_quality: float
    detection_method: str
    parameters_used: Dict[str, Any]
    diagnostics: Dict[str, Any]

class NaturalStepDetector(AlgorithmBase):
    """
    Enhanced natural step detection algorithm based on pid_analysis_bundle.py
    detect_steps() with improved sensitivity and validation
    """

    def __init__(self):
        metadata = AlgorithmMetadata(
            name="natural_step_detector",
            category=AlgorithmCategory.STEP_DETECTION,
            complexity=AlgorithmComplexity.LOW,
            description="Enhanced natural step detection based on statistical analysis",
            version="1.1.0",
            min_data_points=50,
            supports_realtime=True,
            tags=["step_detection", "statistical", "baseline", "pid_analysis"]
        )
        super().__init__(metadata)

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for step detection"""
        errors = []

        if 'time' not in data:
            errors.append("Missing 'time' array")
        if 'values' not in data:
            errors.append("Missing 'values' array")

        if not errors:
            time_data = np.array(data['time'])
            values_data = np.array(data['values'])

            if len(time_data) != len(values_data):
                errors.append("Time and values arrays must have same length")

            if len(time_data) < self.metadata.min_data_points:
                errors.append(f"Minimum {self.metadata.min_data_points} data points required")

            if np.any(np.isnan(time_data)) or np.any(np.isnan(values_data)):
                errors.append("Data contains NaN values")

        return len(errors) == 0, errors

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute natural step detection algorithm"""
        time_data = np.array(data['time'])
        values_data = np.array(data['values'])

        # Parameters
        min_step_size = kwargs.get('min_step_size', None)
        confidence_threshold = kwargs.get('confidence_threshold', 0.7)
        window_size = kwargs.get('window_size', min(20, len(values_data) // 10))

        # Auto-detect minimum step size if not provided
        if min_step_size is None:
            min_step_size = np.std(values_data) * 0.5

        # Step 1: Detect potential step locations using enhanced method
        step_candidates = self._detect_step_candidates(
            time_data, values_data, window_size, min_step_size
        )

        # Step 2: Validate and filter steps
        validated_steps = self._validate_steps(
            time_data, values_data, step_candidates,
            min_step_size, confidence_threshold
        )

        # Step 3: Calculate step characteristics
        step_results = self._calculate_step_characteristics(
            time_data, values_data, validated_steps
        )

        # Step 4: Quality assessment
        quality_score = self._assess_step_quality(step_results, values_data)

        return {
            'step_times': step_results['times'],
            'step_magnitudes': step_results['magnitudes'],
            'step_confidence': step_results['confidence'],
            'baseline_values': step_results['baselines'],
            'final_values': step_results['finals'],
            'step_quality': quality_score,
            'detection_method': 'natural_enhanced',
            'parameters_used': {
                'min_step_size': min_step_size,
                'confidence_threshold': confidence_threshold,
                'window_size': window_size
            },
            'diagnostics': {
                'total_candidates': len(step_candidates),
                'validated_steps': len(validated_steps),
                'data_points': len(values_data),
                'data_range': float(np.max(values_data) - np.min(values_data))
            }
        }

    def _detect_step_candidates(self, time_data: np.ndarray, values_data: np.ndarray,
                               window_size: int, min_step_size: float) -> List[int]:
        """Detect potential step locations using multiple methods"""
        candidates = set()

        # Method 1: Moving window variance analysis
        window_vars = []
        for i in range(len(values_data) - window_size):
            window = values_data[i:i + window_size]
            window_vars.append(np.var(window))

        # Find peaks in variance (potential step locations)
        variance_peaks, _ = find_peaks(window_vars, height=np.std(window_vars))
        candidates.update(variance_peaks + window_size // 2)

        # Method 2: Derivative analysis
        smoothed_data = savgol_filter(values_data,
                                     min(window_size, len(values_data) // 5 | 1), 2)
        derivative = np.diff(smoothed_data)
        derivative_peaks, _ = find_peaks(np.abs(derivative),
                                       height=min_step_size / np.diff(time_data).mean())
        candidates.update(derivative_peaks + 1)

        # Method 3: Statistical change point detection
        change_points = self._statistical_change_detection(values_data, window_size)
        candidates.update(change_points)

        # Filter candidates
        candidates = [c for c in candidates if window_size <= c <= len(values_data) - window_size]
        candidates.sort()

        return candidates

    def _statistical_change_detection(self, values_data: np.ndarray, window_size: int) -> List[int]:
        """Statistical change point detection using t-test"""
        change_points = []

        for i in range(window_size, len(values_data) - window_size):
            before = values_data[i - window_size:i]
            after = values_data[i:i + window_size]

            # Perform t-test
            try:
                t_stat, p_value = stats.ttest_ind(before, after)
                if p_value < 0.01 and abs(np.mean(after) - np.mean(before)) > np.std(values_data) * 0.3:
                    change_points.append(i)
            except:
                continue

        return change_points

    def _validate_steps(self, time_data: np.ndarray, values_data: np.ndarray,
                       candidates: List[int], min_step_size: float,
                       confidence_threshold: float) -> List[int]:
        """Validate step candidates and filter false positives"""
        validated = []

        for candidate in candidates:
            confidence = self._calculate_step_confidence(
                time_data, values_data, candidate, min_step_size
            )

            if confidence >= confidence_threshold:
                validated.append(candidate)

        # Remove closely spaced steps (keep highest confidence)
        min_separation = len(values_data) // 20  # Minimum 5% separation
        final_validated = []

        i = 0
        while i < len(validated):
            current = validated[i]
            current_conf = self._calculate_step_confidence(
                time_data, values_data, current, min_step_size
            )

            # Check for nearby steps
            j = i + 1
            while j < len(validated) and validated[j] - current < min_separation:
                competitor_conf = self._calculate_step_confidence(
                    time_data, values_data, validated[j], min_step_size
                )

                if competitor_conf > current_conf:
                    current = validated[j]
                    current_conf = competitor_conf
                j += 1

            final_validated.append(current)
            i = j

        return final_validated

    def _calculate_step_confidence(self, time_data: np.ndarray, values_data: np.ndarray,
                                  step_idx: int, min_step_size: float) -> float:
        """Calculate confidence score for a potential step"""
        window_size = min(20, len(values_data) // 10)

        # Get before and after windows
        before_start = max(0, step_idx - window_size)
        after_end = min(len(values_data), step_idx + window_size)

        before_values = values_data[before_start:step_idx]
        after_values = values_data[step_idx:after_end]

        if len(before_values) < 5 or len(after_values) < 5:
            return 0.0

        # Calculate step magnitude
        before_mean = np.mean(before_values)
        after_mean = np.mean(after_values)
        step_magnitude = abs(after_mean - before_mean)

        # Confidence factors
        magnitude_factor = min(1.0, step_magnitude / (min_step_size + 1e-10))

        # Statistical significance
        try:
            t_stat, p_value = stats.ttest_ind(before_values, after_values)
            significance_factor = max(0.0, 1.0 - p_value)
        except:
            significance_factor = 0.0

        # Stability factor (low variance in before/after regions)
        before_stability = 1.0 / (1.0 + np.var(before_values) / (np.var(values_data) + 1e-10))
        after_stability = 1.0 / (1.0 + np.var(after_values) / (np.var(values_data) + 1e-10))
        stability_factor = (before_stability + after_stability) / 2

        # Combined confidence
        confidence = (magnitude_factor * 0.4 +
                     significance_factor * 0.4 +
                     stability_factor * 0.2)

        return min(1.0, confidence)

    def _calculate_step_characteristics(self, time_data: np.ndarray,
                                      values_data: np.ndarray,
                                      step_indices: List[int]) -> Dict[str, List]:
        """Calculate detailed characteristics for validated steps"""
        window_size = min(20, len(values_data) // 10)

        results = {
            'times': [],
            'magnitudes': [],
            'confidence': [],
            'baselines': [],
            'finals': []
        }

        for step_idx in step_indices:
            # Calculate baseline and final values
            before_start = max(0, step_idx - window_size)
            after_end = min(len(values_data), step_idx + window_size)

            baseline = np.mean(values_data[before_start:step_idx])
            final = np.mean(values_data[step_idx:after_end])
            magnitude = final - baseline

            # Get step time
            step_time = time_data[step_idx]

            # Calculate confidence
            confidence = self._calculate_step_confidence(
                time_data, values_data, step_idx, abs(magnitude)
            )

            results['times'].append(float(step_time))
            results['magnitudes'].append(float(magnitude))
            results['confidence'].append(float(confidence))
            results['baselines'].append(float(baseline))
            results['finals'].append(float(final))

        return results

    def _assess_step_quality(self, step_results: Dict[str, List],
                           values_data: np.ndarray) -> float:
        """Assess overall quality of step detection"""
        if not step_results['times']:
            return 0.0

        # Quality factors
        confidence_score = np.mean(step_results['confidence'])

        # Check for reasonable step spacing
        if len(step_results['times']) > 1:
            spacings = np.diff(step_results['times'])
            min_spacing = np.min(spacings)
            data_duration = len(values_data)
            spacing_score = min(1.0, min_spacing / (data_duration * 0.1))
        else:
            spacing_score = 1.0

        # Check for magnitude consistency
        magnitudes = np.array(step_results['magnitudes'])
        if len(magnitudes) > 1:
            magnitude_consistency = 1.0 / (1.0 + np.std(magnitudes) / np.mean(np.abs(magnitudes)))
        else:
            magnitude_consistency = 1.0

        # Combined quality score
        quality = (confidence_score * 0.5 +
                  spacing_score * 0.3 +
                  magnitude_consistency * 0.2)

        return float(quality)

class MLStepDetector(AlgorithmBase):
    """
    Machine learning-based step detection using clustering and pattern recognition
    """

    def __init__(self):
        metadata = AlgorithmMetadata(
            name="ml_step_detector",
            category=AlgorithmCategory.STEP_DETECTION,
            complexity=AlgorithmComplexity.MEDIUM,
            description="Machine learning-based step detection using DBSCAN clustering",
            version="1.0.0",
            dependencies=["scikit-learn"],
            min_data_points=100,
            supports_realtime=False,
            tags=["step_detection", "machine_learning", "clustering", "DBSCAN"]
        )
        super().__init__(metadata)

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for ML step detection"""
        errors = []

        if 'time' not in data or 'values' not in data:
            errors.append("Missing 'time' or 'values' arrays")
            return False, errors

        time_data = np.array(data['time'])
        np.array(data['values'])

        if len(time_data) < self.metadata.min_data_points:
            errors.append(f"Minimum {self.metadata.min_data_points} data points required for ML detection")

        return len(errors) == 0, errors

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute ML-based step detection"""
        time_data = np.array(data['time'])
        values_data = np.array(data['values'])

        # Parameters
        eps = kwargs.get('eps', 0.1)
        min_samples = kwargs.get('min_samples', 5)

        # Feature extraction
        features = self._extract_features(time_data, values_data)

        # Clustering to find step regions
        clusterer = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = clusterer.fit_predict(features)

        # Identify step transitions
        step_indices = self._identify_step_transitions(clusters, values_data)

        # Calculate step characteristics
        step_results = self._calculate_ml_step_characteristics(
            time_data, values_data, step_indices
        )

        return {
            'step_times': step_results['times'],
            'step_magnitudes': step_results['magnitudes'],
            'step_confidence': step_results['confidence'],
            'baseline_values': step_results['baselines'],
            'final_values': step_results['finals'],
            'step_quality': step_results['quality'],
            'detection_method': 'ml_clustering',
            'parameters_used': {
                'eps': eps,
                'min_samples': min_samples,
                'n_clusters': len(np.unique(clusters[clusters != -1]))
            },
            'diagnostics': {
                'features_shape': features.shape,
                'n_noise_points': np.sum(clusters == -1),
                'n_clusters': len(np.unique(clusters[clusters != -1]))
            }
        }

    def _extract_features(self, time_data: np.ndarray, values_data: np.ndarray) -> np.ndarray:
        """Extract features for ML clustering"""
        window_size = min(10, len(values_data) // 20)
        features = []

        for i in range(window_size, len(values_data) - window_size):
            # Local statistics
            local_window = values_data[i-window_size:i+window_size]

            # Features
            local_mean = np.mean(local_window)
            local_std = np.std(local_window)
            local_trend = np.polyfit(range(len(local_window)), local_window, 1)[0]

            # Gradient features
            left_mean = np.mean(values_data[i-window_size:i])
            right_mean = np.mean(values_data[i:i+window_size])
            gradient = right_mean - left_mean

            features.append([
                local_mean,
                local_std,
                local_trend,
                gradient,
                values_data[i]
            ])

        features = np.array(features)

        # Standardize features
        scaler = StandardScaler()
        features = scaler.fit_transform(features)

        return features

    def _identify_step_transitions(self, clusters: np.ndarray, values_data: np.ndarray) -> List[int]:
        """Identify step transition points from cluster results"""
        window_size = min(10, len(values_data) // 20)
        step_indices = []

        # Find cluster transitions
        for i in range(1, len(clusters)):
            if clusters[i] != clusters[i-1] and clusters[i] != -1 and clusters[i-1] != -1:
                step_indices.append(i + window_size)  # Adjust for window offset

        return step_indices

    def _calculate_ml_step_characteristics(self, time_data: np.ndarray,
                                         values_data: np.ndarray,
                                         step_indices: List[int]) -> Dict[str, Any]:
        """Calculate characteristics for ML-detected steps"""
        window_size = min(20, len(values_data) // 10)

        results = {
            'times': [],
            'magnitudes': [],
            'confidence': [],
            'baselines': [],
            'finals': []
        }

        for step_idx in step_indices:
            if step_idx < window_size or step_idx >= len(values_data) - window_size:
                continue

            # Calculate baseline and final values
            baseline = np.mean(values_data[step_idx - window_size:step_idx])
            final = np.mean(values_data[step_idx:step_idx + window_size])
            magnitude = final - baseline

            # Calculate confidence based on cluster separation
            confidence = min(1.0, abs(magnitude) / (np.std(values_data) + 1e-10))

            results['times'].append(float(time_data[step_idx]))
            results['magnitudes'].append(float(magnitude))
            results['confidence'].append(float(confidence))
            results['baselines'].append(float(baseline))
            results['finals'].append(float(final))

        # Calculate overall quality
        if results['times']:
            results['quality'] = np.mean(results['confidence'])
        else:
            results['quality'] = 0.0

        return results

# Register algorithms
registry.register(NaturalStepDetector)
registry.register(MLStepDetector)

# Export algorithms
__all__ = [
    'NaturalStepDetector',
    'MLStepDetector',
    'StepDetectionResult'
]
