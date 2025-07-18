#!/usr/bin/env python3
"""
Specialized Control Data Processors - Phase 22.1.2
==================================================

Advanced preprocessing algorithms specifically designed for industrial control
loop data analysis, building upon existing data pipeline capabilities.

Features:
- Control-specific signal processing (filtering, smoothing, differentiation)
- Process variable extraction and conditioning
- Time-series alignment and synchronization
- Control loop feature engineering
- Integration with existing DataPreprocessor patterns
- Real-time processing capabilities

Author: AI Task Orchestrator
Created: January 18, 2025
Phase: 22.1.2 - Enhanced Data Preprocessing (Processors)
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import warnings
from scipy import signal, interpolate, stats
from scipy.optimize import minimize_scalar
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
import time

# Import existing preprocessing modules
try:
    from ...scripts.ai.modules.data import DataPreprocessor
    MODULAR_DATA_AVAILABLE = True
except ImportError:
    MODULAR_DATA_AVAILABLE = False
    logging.warning("⚠️ Existing data modules not available - using standalone implementation")

# Import PID analysis for control-specific processing
try:
    from ...docs.context.pid_analysis_bundle import infer_interval, detect_steps
    PID_BUNDLE_AVAILABLE = True
except ImportError:
    PID_BUNDLE_AVAILABLE = False
    logging.warning("⚠️ PID analysis bundle not available")

# Setup logging
logger = logging.getLogger(__name__)

class ProcessingStrategy(Enum):
    """Processing strategy enumeration"""
    CONSERVATIVE = "conservative"  # Minimal processing, preserve original data
    STANDARD = "standard"         # Standard industrial preprocessing
    AGGRESSIVE = "aggressive"     # Maximum cleaning and conditioning
    CUSTOM = "custom"            # User-defined processing pipeline

class FilterType(Enum):
    """Signal filtering types"""
    NONE = "none"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL = "exponential"
    BUTTERWORTH = "butterworth"
    SAVITZKY_GOLAY = "savitzky_golay"
    MEDIAN = "median"
    KALMAN = "kalman"

class InterpolationMethod(Enum):
    """Interpolation methods for missing data"""
    NONE = "none"
    LINEAR = "linear"
    CUBIC = "cubic"
    SPLINE = "spline"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    MEAN = "mean"

@dataclass
class ProcessingOptions:
    """Configuration options for data processing"""
    strategy: ProcessingStrategy = ProcessingStrategy.STANDARD
    
    # Filtering options
    filter_type: FilterType = FilterType.MOVING_AVERAGE
    filter_window: int = 5
    filter_order: int = 2
    
    # Outlier handling
    outlier_detection: bool = True
    outlier_method: str = "iqr"  # "iqr", "zscore", "isolation_forest"
    outlier_threshold: float = 3.0
    outlier_action: str = "clip"  # "remove", "clip", "interpolate"
    
    # Missing data handling
    interpolation_method: InterpolationMethod = InterpolationMethod.LINEAR
    max_gap_size: int = 10  # Maximum consecutive missing values to interpolate
    
    # Scaling and normalization
    scaling_method: str = "none"  # "none", "standard", "robust", "minmax"
    scale_per_column: bool = True
    
    # Control-specific options
    detect_control_variables: bool = True
    extract_step_responses: bool = True
    calculate_derivatives: bool = True
    remove_steady_state_periods: bool = False
    
    # Time series options
    resample_frequency: Optional[str] = None  # e.g., "1S", "5T"
    align_timestamps: bool = True
    remove_duplicates: bool = True
    
    # Quality thresholds
    min_data_quality: float = 0.8
    min_signal_to_noise: float = 2.0
    
    # Performance options
    chunk_size: int = 10000
    parallel_processing: bool = True

@dataclass 
class ProcessingResult:
    """Result of data processing operation"""
    original_data: pd.DataFrame
    processed_data: pd.DataFrame
    processing_log: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    control_variables: Dict[str, str] = field(default_factory=dict)
    detected_features: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    success: bool = False
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class BaseProcessor(ABC):
    """Abstract base class for data processors"""
    
    def __init__(self, name: str, options: ProcessingOptions = None):
        self.name = name
        self.options = options or ProcessingOptions()
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def process(self, data: pd.DataFrame) -> ProcessingResult:
        """Process the input data"""
        pass
    
    def _log_step(self, result: ProcessingResult, message: str):
        """Log a processing step"""
        result.processing_log.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        self.logger.info(message)
    
    def _calculate_quality_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate data quality metrics"""
        if data.empty:
            return {}
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        metrics = {
            "completeness": 1.0 - (data.isnull().sum().sum() / data.size),
            "row_count": len(data),
            "column_count": len(data.columns),
            "numeric_columns": len(numeric_cols)
        }
        
        if len(numeric_cols) > 0:
            # Signal quality metrics
            for col in numeric_cols:
                col_data = data[col].dropna()
                if len(col_data) > 1:
                    # Signal-to-noise ratio estimation
                    signal_std = col_data.std()
                    noise_std = col_data.diff().std() / np.sqrt(2)
                    snr = signal_std / (noise_std + 1e-10)
                    metrics[f"{col}_snr"] = snr
                    
                    # Variability
                    metrics[f"{col}_range"] = col_data.max() - col_data.min()
                    metrics[f"{col}_cv"] = col_data.std() / (abs(col_data.mean()) + 1e-10)
        
        return metrics

class SignalProcessor(BaseProcessor):
    """Processor for signal conditioning and filtering"""
    
    def __init__(self, options: ProcessingOptions = None):
        super().__init__("SignalProcessor", options)
    
    def process(self, data: pd.DataFrame) -> ProcessingResult:
        """Apply signal processing to data"""
        start_time = time.time()
        result = ProcessingResult(original_data=data.copy(), processed_data=data.copy())
        
        try:
            self._log_step(result, f"Starting signal processing with {self.options.filter_type.value} filter")
            
            # Apply filtering to numeric columns
            numeric_cols = result.processed_data.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                col_data = result.processed_data[col].dropna()
                if len(col_data) > self.options.filter_window:
                    filtered_data = self._apply_filter(col_data, self.options.filter_type)
                    
                    # Update only non-null values
                    mask = result.processed_data[col].notna()
                    result.processed_data.loc[mask, col] = filtered_data
                    
                    self._log_step(result, f"Applied {self.options.filter_type.value} filter to {col}")
            
            # Calculate quality metrics
            result.quality_metrics = self._calculate_quality_metrics(result.processed_data)
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Signal processing failed: {str(e)}")
            self.logger.error(f"Signal processing failed: {e}")
        
        result.processing_time = time.time() - start_time
        return result
    
    def _apply_filter(self, data: pd.Series, filter_type: FilterType) -> pd.Series:
        """Apply specified filter to data series"""
        if filter_type == FilterType.NONE:
            return data
        
        elif filter_type == FilterType.MOVING_AVERAGE:
            return data.rolling(window=self.options.filter_window, center=True).mean().fillna(data)
        
        elif filter_type == FilterType.EXPONENTIAL:
            # Exponential smoothing
            alpha = 2.0 / (self.options.filter_window + 1)
            return data.ewm(alpha=alpha).mean()
        
        elif filter_type == FilterType.MEDIAN:
            return data.rolling(window=self.options.filter_window, center=True).median().fillna(data)
        
        elif filter_type == FilterType.BUTTERWORTH:
            # Butterworth low-pass filter
            try:
                nyquist = 0.5  # Normalized frequency (assuming unit sampling rate)
                cutoff = 1.0 / self.options.filter_window
                normal_cutoff = cutoff / nyquist
                
                if normal_cutoff >= 1.0:
                    return data  # Cannot filter with this frequency
                
                b, a = signal.butter(self.options.filter_order, normal_cutoff, btype='low')
                filtered = signal.filtfilt(b, a, data.values)
                return pd.Series(filtered, index=data.index)
            except Exception:
                # Fallback to moving average
                return data.rolling(window=self.options.filter_window, center=True).mean().fillna(data)
        
        elif filter_type == FilterType.SAVITZKY_GOLAY:
            # Savitzky-Golay filter
            try:
                window_length = min(self.options.filter_window, len(data))
                if window_length % 2 == 0:
                    window_length -= 1
                if window_length < 3:
                    return data
                
                polyorder = min(self.options.filter_order, window_length - 1)
                filtered = signal.savgol_filter(data.values, window_length, polyorder)
                return pd.Series(filtered, index=data.index)
            except Exception:
                # Fallback to moving average
                return data.rolling(window=self.options.filter_window, center=True).mean().fillna(data)
        
        else:
            return data

class ControlDataProcessor(BaseProcessor):
    """Specialized processor for control loop data"""
    
    def __init__(self, options: ProcessingOptions = None):
        super().__init__("ControlDataProcessor", options)
    
    def process(self, data: pd.DataFrame) -> ProcessingResult:
        """Process control loop data"""
        start_time = time.time()
        result = ProcessingResult(original_data=data.copy(), processed_data=data.copy())
        
        try:
            self._log_step(result, "Starting control data processing")
            
            # Detect control variables
            if self.options.detect_control_variables:
                control_vars = self._detect_control_variables(result.processed_data)
                result.control_variables = control_vars
                self._log_step(result, f"Detected control variables: {control_vars}")
            
            # Handle missing data
            if self.options.interpolation_method != InterpolationMethod.NONE:
                result.processed_data = self._handle_missing_data(result.processed_data)
                self._log_step(result, f"Applied {self.options.interpolation_method.value} interpolation")
            
            # Remove outliers
            if self.options.outlier_detection:
                result.processed_data = self._handle_outliers(result.processed_data)
                self._log_step(result, f"Handled outliers using {self.options.outlier_method}")
            
            # Extract step responses if requested
            if self.options.extract_step_responses:
                step_features = self._extract_step_responses(result.processed_data, result.control_variables)
                result.detected_features["step_responses"] = step_features
                self._log_step(result, f"Extracted {len(step_features)} step responses")
            
            # Calculate derivatives if requested
            if self.options.calculate_derivatives:
                result.processed_data = self._calculate_derivatives(result.processed_data)
                self._log_step(result, "Calculated derivatives for process variables")
            
            # Apply scaling if requested
            if self.options.scaling_method != "none":
                result.processed_data = self._apply_scaling(result.processed_data)
                self._log_step(result, f"Applied {self.options.scaling_method} scaling")
            
            # Calculate quality metrics
            result.quality_metrics = self._calculate_quality_metrics(result.processed_data)
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Control data processing failed: {str(e)}")
            self.logger.error(f"Control data processing failed: {e}")
        
        result.processing_time = time.time() - start_time
        return result
    
    def _detect_control_variables(self, data: pd.DataFrame) -> Dict[str, str]:
        """Detect control variables (PV, SP, CV) in the data"""
        control_vars = {}
        
        # Use existing DataPreprocessor if available
        if MODULAR_DATA_AVAILABLE:
            try:
                # Try to use existing control variable detection
                control_data = DataPreprocessor.extract_control_loop_data(data)
                if hasattr(control_data, 'pv_column'):
                    control_vars['PV'] = control_data.pv_column
                if hasattr(control_data, 'sp_column'):
                    control_vars['SP'] = control_data.sp_column
                if hasattr(control_data, 'cv_column'):
                    control_vars['CV'] = control_data.cv_column
                return control_vars
            except Exception as e:
                self.logger.warning(f"DataPreprocessor detection failed: {e}")
        
        # Fallback to pattern matching
        columns_lower = {col.lower(): col for col in data.columns}
        
        # Pattern matching for common control variable names
        pv_patterns = ['pv', 'process_variable', 'measurement', 'sensor', 'actual']
        sp_patterns = ['sp', 'setpoint', 'set_point', 'target', 'reference']
        cv_patterns = ['cv', 'control_variable', 'output', 'manipulated', 'valve']
        
        for pattern in pv_patterns:
            matches = [col for col_lower, col in columns_lower.items() if pattern in col_lower]
            if matches:
                control_vars['PV'] = matches[0]
                break
        
        for pattern in sp_patterns:
            matches = [col for col_lower, col in columns_lower.items() if pattern in col_lower]
            if matches:
                control_vars['SP'] = matches[0]
                break
        
        for pattern in cv_patterns:
            matches = [col for col_lower, col in columns_lower.items() if pattern in col_lower]
            if matches:
                control_vars['CV'] = matches[0]
                break
        
        return control_vars
    
    def _handle_missing_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing data using specified interpolation method"""
        processed_data = data.copy()
        numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = processed_data[col]
            
            if col_data.isnull().sum() == 0:
                continue  # No missing data
            
            # Check gap sizes
            null_groups = col_data.isnull().astype(int).groupby(col_data.notna().cumsum()).sum()
            max_gap = null_groups.max() if len(null_groups) > 0 else 0
            
            if max_gap > self.options.max_gap_size:
                self.logger.warning(f"Column {col} has gaps larger than {self.options.max_gap_size}")
                continue
            
            # Apply interpolation
            if self.options.interpolation_method == InterpolationMethod.LINEAR:
                processed_data[col] = col_data.interpolate(method='linear')
            elif self.options.interpolation_method == InterpolationMethod.CUBIC:
                processed_data[col] = col_data.interpolate(method='cubic')
            elif self.options.interpolation_method == InterpolationMethod.SPLINE:
                processed_data[col] = col_data.interpolate(method='spline', order=3)
            elif self.options.interpolation_method == InterpolationMethod.FORWARD_FILL:
                processed_data[col] = col_data.fillna(method='ffill')
            elif self.options.interpolation_method == InterpolationMethod.BACKWARD_FILL:
                processed_data[col] = col_data.fillna(method='bfill')
            elif self.options.interpolation_method == InterpolationMethod.MEAN:
                processed_data[col] = col_data.fillna(col_data.mean())
        
        return processed_data
    
    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers using specified method"""
        processed_data = data.copy()
        numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = processed_data[col].dropna()
            
            if len(col_data) < 10:
                continue  # Too few points for outlier detection
            
            # Detect outliers
            if self.options.outlier_method == "iqr":
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)
                
            elif self.options.outlier_method == "zscore":
                z_scores = np.abs(stats.zscore(col_data))
                outlier_mask = z_scores > self.options.outlier_threshold
                
            else:
                continue  # Unknown method
            
            if outlier_mask.sum() == 0:
                continue  # No outliers found
            
            # Handle outliers
            if self.options.outlier_action == "remove":
                # Mark outliers as NaN for later interpolation
                processed_data.loc[outlier_mask, col] = np.nan
                
            elif self.options.outlier_action == "clip":
                if self.options.outlier_method == "iqr":
                    processed_data.loc[col_data < lower_bound, col] = lower_bound
                    processed_data.loc[col_data > upper_bound, col] = upper_bound
                elif self.options.outlier_method == "zscore":
                    median_val = col_data.median()
                    mad = np.median(np.abs(col_data - median_val))
                    lower_clip = median_val - self.options.outlier_threshold * mad
                    upper_clip = median_val + self.options.outlier_threshold * mad
                    processed_data[col] = processed_data[col].clip(lower_clip, upper_clip)
            
            elif self.options.outlier_action == "interpolate":
                # Mark outliers as NaN and interpolate
                processed_data.loc[outlier_mask, col] = np.nan
                processed_data[col] = processed_data[col].interpolate(method='linear')
        
        return processed_data
    
    def _extract_step_responses(self, data: pd.DataFrame, control_vars: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract step response features from control data"""
        step_responses = []
        
        if 'CV' not in control_vars or control_vars['CV'] not in data.columns:
            return step_responses
        
        cv_col = control_vars['CV']
        cv_data = data[cv_col].dropna()
        
        if len(cv_data) < 10:
            return step_responses
        
        # Use PID bundle if available for step detection
        if PID_BUNDLE_AVAILABLE:
            try:
                step_indices = detect_steps(cv_data, threshold=cv_data.std() * 0.5)
                
                for idx in step_indices:
                    if idx + 50 < len(cv_data):  # Ensure enough data after step
                        step_info = {
                            'index': idx,
                            'timestamp': data.index[idx] if hasattr(data.index, 'to_pydatetime') else idx,
                            'cv_before': cv_data.iloc[idx],
                            'cv_after': cv_data.iloc[idx + 1],
                            'magnitude': cv_data.iloc[idx + 1] - cv_data.iloc[idx]
                        }
                        step_responses.append(step_info)
            except Exception as e:
                self.logger.warning(f"PID bundle step detection failed: {e}")
        
        return step_responses
    
    def _calculate_derivatives(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate derivatives for process variables"""
        processed_data = data.copy()
        numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = processed_data[col].dropna()
            
            if len(col_data) > 1:
                # Calculate first derivative (rate of change)
                derivative = col_data.diff()
                derivative_col = f"{col}_derivative"
                processed_data[derivative_col] = derivative
        
        return processed_data
    
    def _apply_scaling(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply scaling/normalization to numeric columns"""
        processed_data = data.copy()
        numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return processed_data
        
        # Select scaler
        if self.options.scaling_method == "standard":
            scaler = StandardScaler()
        elif self.options.scaling_method == "robust":
            scaler = RobustScaler()
        elif self.options.scaling_method == "minmax":
            scaler = MinMaxScaler()
        else:
            return processed_data
        
        if self.options.scale_per_column:
            # Scale each column independently
            for col in numeric_cols:
                col_data = processed_data[[col]].dropna()
                if len(col_data) > 1:
                    scaled_data = scaler.fit_transform(col_data)
                    processed_data.loc[col_data.index, col] = scaled_data.flatten()
        else:
            # Scale all columns together
            numeric_data = processed_data[numeric_cols].dropna()
            if len(numeric_data) > 1:
                scaled_data = scaler.fit_transform(numeric_data)
                processed_data.loc[numeric_data.index, numeric_cols] = scaled_data
        
        return processed_data

class TimeSeriesProcessor(BaseProcessor):
    """Processor for time-series specific operations"""
    
    def __init__(self, options: ProcessingOptions = None):
        super().__init__("TimeSeriesProcessor", options)
    
    def process(self, data: pd.DataFrame) -> ProcessingResult:
        """Process time-series data"""
        start_time = time.time()
        result = ProcessingResult(original_data=data.copy(), processed_data=data.copy())
        
        try:
            self._log_step(result, "Starting time-series processing")
            
            # Align timestamps if requested
            if self.options.align_timestamps:
                result.processed_data = self._align_timestamps(result.processed_data)
                self._log_step(result, "Aligned timestamps")
            
            # Remove duplicates if requested
            if self.options.remove_duplicates:
                before_count = len(result.processed_data)
                result.processed_data = result.processed_data.drop_duplicates()
                after_count = len(result.processed_data)
                if before_count != after_count:
                    self._log_step(result, f"Removed {before_count - after_count} duplicate records")
            
            # Resample if requested
            if self.options.resample_frequency:
                result.processed_data = self._resample_data(result.processed_data)
                self._log_step(result, f"Resampled to {self.options.resample_frequency}")
            
            # Calculate time-series features
            ts_features = self._calculate_timeseries_features(result.processed_data)
            result.detected_features["timeseries"] = ts_features
            
            result.quality_metrics = self._calculate_quality_metrics(result.processed_data)
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Time-series processing failed: {str(e)}")
            self.logger.error(f"Time-series processing failed: {e}")
        
        result.processing_time = time.time() - start_time
        return result
    
    def _align_timestamps(self, data: pd.DataFrame) -> pd.DataFrame:
        """Align timestamps to regular intervals"""
        # Find time columns
        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]
        
        if not time_columns:
            return data
        
        time_col = time_columns[0]
        processed_data = data.copy()
        
        try:
            # Convert to datetime if not already
            processed_data[time_col] = pd.to_datetime(processed_data[time_col])
            
            # Sort by time
            processed_data = processed_data.sort_values(time_col)
            
            # Set as index for easier resampling
            processed_data = processed_data.set_index(time_col)
            
        except Exception as e:
            self.logger.warning(f"Timestamp alignment failed: {e}")
        
        return processed_data
    
    def _resample_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Resample data to specified frequency"""
        if not isinstance(data.index, pd.DatetimeIndex):
            return data
        
        try:
            # Resample numeric columns with mean, others with forward fill
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
            
            resampled_data = pd.DataFrame()
            
            if len(numeric_cols) > 0:
                resampled_numeric = data[numeric_cols].resample(self.options.resample_frequency).mean()
                resampled_data = pd.concat([resampled_data, resampled_numeric], axis=1)
            
            if len(non_numeric_cols) > 0:
                resampled_non_numeric = data[non_numeric_cols].resample(self.options.resample_frequency).first()
                resampled_data = pd.concat([resampled_data, resampled_non_numeric], axis=1)
            
            return resampled_data
            
        except Exception as e:
            self.logger.warning(f"Resampling failed: {e}")
            return data
    
    def _calculate_timeseries_features(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate time-series specific features"""
        features = {}
        
        if isinstance(data.index, pd.DatetimeIndex):
            # Time span
            features['time_span'] = (data.index.max() - data.index.min()).total_seconds()
            features['sampling_frequency'] = len(data) / features['time_span'] if features['time_span'] > 0 else 0
            
            # Gaps in time series
            time_diffs = data.index.to_series().diff().dropna()
            if len(time_diffs) > 0:
                features['median_interval'] = time_diffs.median().total_seconds()
                features['max_gap'] = time_diffs.max().total_seconds()
                features['irregular_intervals'] = (time_diffs > time_diffs.median() * 2).sum()
        
        # Data characteristics
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            features['numeric_columns'] = len(numeric_cols)
            features['total_data_points'] = len(data) * len(numeric_cols)
            features['missing_ratio'] = data[numeric_cols].isnull().sum().sum() / (len(data) * len(numeric_cols))
        
        return features 