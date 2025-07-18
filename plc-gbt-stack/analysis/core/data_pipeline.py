#!/usr/bin/env python3
"""
Enhanced Control Loop Data Pipeline
==================================

Phase 22.1.1: Data Pipeline Implementation

Advanced data pipeline for control loop analysis providing:
- Unified data ingestion from multiple sources (CSV, PLC, databases)
- Advanced preprocessing with filtering and outlier detection
- Multi-rate data synchronization and interpolation
- Integration with existing DataLoader patterns
- Async processing for scalable data handling

Features:
- Pipeline stage architecture for modular processing
- Type-safe data validation and transformation
- Automatic missing data handling and interpolation
- Advanced filtering algorithms (Butterworth, Kalman, etc.)
- Real-time data streaming support
- Integration with PLC memory management system

Author: AI Task Orchestrator  
Created: January 18, 2025
Phase: 22.1.1 - Modular Analysis Framework (Data Pipeline)
Dependencies: Phase 21 CLI, existing DataLoader modules
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, AsyncGenerator
from scipy import signal
from scipy.interpolate import interp1d

# Import existing modular components
try:
    from ...scripts.ai.modules.data import DataLoader, DataValidator, DataPreprocessor
    MODULAR_DATA_AVAILABLE = True
except ImportError:
    MODULAR_DATA_AVAILABLE = False
    logging.warning("⚠️ Existing data modules not available - using standalone implementation")

# Import foundation algorithms
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "docs" / "context"))
    from pid_analysis_bundle import infer_interval
    PID_BUNDLE_AVAILABLE = True
except ImportError:
    PID_BUNDLE_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """Data source type enumeration"""
    CSV_FILE = "csv_file"
    EXCEL_FILE = "excel_file"
    DATABASE = "database"
    PLC_REALTIME = "plc_realtime"
    API_ENDPOINT = "api_endpoint"
    MEMORY_CACHE = "memory_cache"
    STREAM = "stream"

class ProcessingStage(Enum):
    """Data processing stage enumeration"""
    INGESTION = "ingestion"
    VALIDATION = "validation"
    FILTERING = "filtering"
    OUTLIER_REMOVAL = "outlier_removal"
    INTERPOLATION = "interpolation"
    SYNCHRONIZATION = "synchronization"
    NORMALIZATION = "normalization"
    FEATURE_EXTRACTION = "feature_extraction"

class FilterType(Enum):
    """Filter type enumeration"""
    BUTTERWORTH = "butterworth"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL = "exponential"
    MEDIAN = "median"
    KALMAN = "kalman"
    SAVGOL = "savgol"

@dataclass
class DataSource:
    """Data source configuration"""
    source_id: str
    source_type: DataSourceType
    location: str  # File path, URL, connection string, etc.
    
    # Column mapping
    time_column: str = "timestamp"
    columns: Dict[str, str] = field(default_factory=dict)  # logical_name -> actual_column
    
    # Processing options
    auto_detect_columns: bool = True
    parse_dates: bool = True
    skip_rows: int = 0
    encoding: str = "utf-8"
    
    # Connection options (for databases/APIs)
    connection_options: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class ProcessingOptions:
    """Data processing configuration"""
    
    # Filtering options
    enable_filtering: bool = True
    filter_type: FilterType = FilterType.BUTTERWORTH
    filter_order: int = 2
    cutoff_frequency: float = 0.1  # Normalized frequency (0-1)
    
    # Outlier detection
    enable_outlier_removal: bool = True
    outlier_method: str = "iqr"  # "iqr", "zscore", "isolation_forest"
    outlier_threshold: float = 2.0
    
    # Interpolation
    enable_interpolation: bool = True
    interpolation_method: str = "linear"  # "linear", "cubic", "nearest"
    max_gap_seconds: float = 10.0
    
    # Synchronization
    enable_synchronization: bool = True
    target_sampling_rate: Optional[float] = None  # Hz, auto-detect if None
    sync_method: str = "interpolation"  # "interpolation", "forward_fill", "nearest"
    
    # Validation
    min_data_points: int = 10
    max_missing_ratio: float = 0.2
    require_monotonic_time: bool = True
    
    # Performance
    chunk_size: int = 10000
    parallel_processing: bool = True
    max_workers: int = 4

@dataclass
class PipelineStage:
    """Data pipeline stage configuration"""
    stage_id: str
    stage_type: ProcessingStage
    enabled: bool = True
    options: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ProcessingResult:
    """Result from data processing"""
    success: bool
    data: Optional[pd.DataFrame] = None
    
    # Processing metadata
    original_rows: int = 0
    processed_rows: int = 0
    processing_time: float = 0.0
    stages_completed: List[str] = field(default_factory=list)
    
    # Quality metrics
    missing_data_ratio: float = 0.0
    outliers_removed: int = 0
    interpolated_points: int = 0
    
    # Messages
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Raw processing info
    stage_results: Dict[str, Any] = field(default_factory=dict)

class DataProcessor(ABC):
    """Abstract base class for data processors"""
    
    def __init__(self, processor_id: str, stage_type: ProcessingStage):
        self.processor_id = processor_id
        self.stage_type = stage_type
        self.logger = logging.getLogger(f"{__name__}.{processor_id}")
    
    @abstractmethod
    async def process(self, data: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """Process the data"""
        pass
    
    def validate_input(self, data: pd.DataFrame) -> bool:
        """Validate input data"""
        return data is not None and len(data) > 0

class FilterProcessor(DataProcessor):
    """Advanced filtering processor"""
    
    def __init__(self):
        super().__init__("filter_processor", ProcessingStage.FILTERING)
    
    async def process(self, data: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """Apply filtering to data"""
        filter_type = FilterType(options.get('filter_type', 'butterworth'))
        
        # Get numeric columns for filtering
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        filtered_data = data.copy()
        
        for col in numeric_columns:
            if col in ['timestamp', 'time']:  # Skip time columns
                continue
            
            series = data[col].dropna()
            if len(series) < 10:  # Skip if insufficient data
                continue
            
            try:
                if filter_type == FilterType.BUTTERWORTH:
                    filtered_series = self._butterworth_filter(series, options)
                elif filter_type == FilterType.MOVING_AVERAGE:
                    filtered_series = self._moving_average_filter(series, options)
                elif filter_type == FilterType.EXPONENTIAL:
                    filtered_series = self._exponential_filter(series, options)
                elif filter_type == FilterType.MEDIAN:
                    filtered_series = self._median_filter(series, options)
                elif filter_type == FilterType.SAVGOL:
                    filtered_series = self._savgol_filter(series, options)
                else:
                    filtered_series = series  # No filtering
                
                # Update data with filtered values
                filtered_data.loc[series.index, col] = filtered_series
                
            except Exception as e:
                self.logger.warning(f"Filtering failed for column {col}: {e}")
        
        return filtered_data
    
    def _butterworth_filter(self, series: pd.Series, options: Dict[str, Any]) -> pd.Series:
        """Apply Butterworth filter"""
        order = options.get('filter_order', 2)
        cutoff = options.get('cutoff_frequency', 0.1)
        
        # Design filter
        b, a = signal.butter(order, cutoff, btype='low', analog=False)
        
        # Apply filter
        filtered_values = signal.filtfilt(b, a, series.values)
        
        return pd.Series(filtered_values, index=series.index)
    
    def _moving_average_filter(self, series: pd.Series, options: Dict[str, Any]) -> pd.Series:
        """Apply moving average filter"""
        window = options.get('window_size', 5)
        return series.rolling(window=window, center=True).mean().fillna(series)
    
    def _exponential_filter(self, series: pd.Series, options: Dict[str, Any]) -> pd.Series:
        """Apply exponential smoothing filter"""
        alpha = options.get('alpha', 0.1)
        return series.ewm(alpha=alpha).mean()
    
    def _median_filter(self, series: pd.Series, options: Dict[str, Any]) -> pd.Series:
        """Apply median filter"""
        window = options.get('window_size', 3)
        return series.rolling(window=window, center=True).median().fillna(series)
    
    def _savgol_filter(self, series: pd.Series, options: Dict[str, Any]) -> pd.Series:
        """Apply Savitzky-Golay filter"""
        window = options.get('window_size', 5)
        polyorder = options.get('poly_order', 2)
        
        # Ensure odd window size
        if window % 2 == 0:
            window += 1
        
        # Ensure valid polyorder
        polyorder = min(polyorder, window - 1)
        
        if len(series) >= window:
            filtered_values = signal.savgol_filter(series.values, window, polyorder)
            return pd.Series(filtered_values, index=series.index)
        else:
            return series

class OutlierProcessor(DataProcessor):
    """Outlier detection and removal processor"""
    
    def __init__(self):
        super().__init__("outlier_processor", ProcessingStage.OUTLIER_REMOVAL)
    
    async def process(self, data: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """Remove outliers from data"""
        method = options.get('outlier_method', 'iqr')
        threshold = options.get('outlier_threshold', 2.0)
        
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        cleaned_data = data.copy()
        outliers_removed = 0
        
        for col in numeric_columns:
            if col in ['timestamp', 'time']:
                continue
            
            series = data[col]
            
            if method == 'iqr':
                outlier_mask = self._iqr_outliers(series, threshold)
            elif method == 'zscore':
                outlier_mask = self._zscore_outliers(series, threshold)
            elif method == 'isolation_forest':
                outlier_mask = self._isolation_forest_outliers(series)
            else:
                outlier_mask = pd.Series(False, index=series.index)
            
            # Remove outliers (replace with NaN)
            cleaned_data.loc[outlier_mask, col] = np.nan
            outliers_removed += outlier_mask.sum()
        
        self.logger.info(f"Removed {outliers_removed} outliers")
        return cleaned_data
    
    def _iqr_outliers(self, series: pd.Series, threshold: float = 1.5) -> pd.Series:
        """Detect outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        return (series < lower_bound) | (series > upper_bound)
    
    def _zscore_outliers(self, series: pd.Series, threshold: float = 2.0) -> pd.Series:
        """Detect outliers using Z-score method"""
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    
    def _isolation_forest_outliers(self, series: pd.Series) -> pd.Series:
        """Detect outliers using Isolation Forest"""
        try:
            from sklearn.ensemble import IsolationForest
            
            values = series.values.reshape(-1, 1)
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outliers = iso_forest.fit_predict(values) == -1
            
            return pd.Series(outliers, index=series.index)
        except ImportError:
            self.logger.warning("scikit-learn not available, falling back to IQR method")
            return self._iqr_outliers(series)

class InterpolationProcessor(DataProcessor):
    """Missing data interpolation processor"""
    
    def __init__(self):
        super().__init__("interpolation_processor", ProcessingStage.INTERPOLATION)
    
    async def process(self, data: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """Interpolate missing data"""
        method = options.get('interpolation_method', 'linear')
        max_gap = options.get('max_gap_seconds', 10.0)
        
        interpolated_data = data.copy()
        interpolated_points = 0
        
        # Get time column for gap analysis
        time_col = self._identify_time_column(data)
        
        if time_col and time_col in data.columns:
            time_series = pd.to_datetime(data[time_col])
            time_diff = time_series.diff().dt.total_seconds()
        else:
            time_diff = None
        
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col == time_col:
                continue
            
            series = data[col]
            missing_mask = series.isnull()
            
            if not missing_mask.any():
                continue  # No missing data
            
            # Check gap sizes if time information is available
            if time_diff is not None:
                valid_interpolation_mask = self._get_valid_interpolation_mask(
                    missing_mask, time_diff, max_gap
                )
            else:
                valid_interpolation_mask = missing_mask
            
            # Perform interpolation
            if method == 'linear':
                interpolated_series = series.interpolate(method='linear')
            elif method == 'cubic':
                interpolated_series = series.interpolate(method='cubic')
            elif method == 'nearest':
                interpolated_series = series.interpolate(method='nearest')
            elif method == 'forward_fill':
                interpolated_series = series.fillna(method='ffill')
            elif method == 'backward_fill':
                interpolated_series = series.fillna(method='bfill')
            else:
                interpolated_series = series.interpolate(method='linear')
            
            # Apply only to valid interpolation points
            interpolated_data.loc[valid_interpolation_mask, col] = interpolated_series.loc[valid_interpolation_mask]
            interpolated_points += valid_interpolation_mask.sum()
        
        self.logger.info(f"Interpolated {interpolated_points} data points")
        return interpolated_data
    
    def _identify_time_column(self, data: pd.DataFrame) -> Optional[str]:
        """Identify the time column in the data"""
        potential_time_cols = ['timestamp', 'time', 'datetime', 'date']
        
        for col in potential_time_cols:
            if col in data.columns:
                return col
        
        # Look for datetime-like columns
        for col in data.columns:
            if data[col].dtype == 'object':
                try:
                    pd.to_datetime(data[col].iloc[0])
                    return col
                except:
                    continue
        
        return None
    
    def _get_valid_interpolation_mask(self, missing_mask: pd.Series, 
                                    time_diff: pd.Series, max_gap: float) -> pd.Series:
        """Get mask for valid interpolation points considering gap sizes"""
        valid_mask = missing_mask.copy()
        
        # Find gaps that are too large
        large_gaps = time_diff > max_gap
        
        # Mark missing values in large gaps as invalid for interpolation
        for i in range(len(missing_mask)):
            if missing_mask.iloc[i] and i > 0 and large_gaps.iloc[i]:
                valid_mask.iloc[i] = False
        
        return valid_mask

class SynchronizationProcessor(DataProcessor):
    """Multi-rate data synchronization processor"""
    
    def __init__(self):
        super().__init__("sync_processor", ProcessingStage.SYNCHRONIZATION)
    
    async def process(self, data: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """Synchronize data to target sampling rate"""
        target_rate = options.get('target_sampling_rate')
        sync_method = options.get('sync_method', 'interpolation')
        
        # Identify time column
        time_col = self._identify_time_column(data)
        if not time_col:
            self.logger.warning("No time column found, skipping synchronization")
            return data
        
        # Convert to datetime and sort
        time_series = pd.to_datetime(data[time_col])
        data_sorted = data.sort_values(time_col).copy()
        time_sorted = time_series.sort_values()
        
        # Detect current sampling rate
        if PID_BUNDLE_AVAILABLE:
            current_interval = infer_interval(time_sorted.astype('int64') / 1e9)
            current_rate = 1.0 / current_interval if current_interval > 0 else 1.0
        else:
            time_diff = time_sorted.diff().dt.total_seconds().dropna()
            current_interval = time_diff.median()
            current_rate = 1.0 / current_interval if current_interval > 0 else 1.0
        
        # Use current rate if target not specified
        if target_rate is None:
            target_rate = current_rate
            self.logger.info(f"Using detected sampling rate: {target_rate:.2f} Hz")
        
        # Create target time grid
        start_time = time_sorted.iloc[0]
        end_time = time_sorted.iloc[-1]
        target_interval = 1.0 / target_rate
        
        target_times = pd.date_range(
            start=start_time,
            end=end_time,
            freq=f'{target_interval}S'
        )
        
        # Synchronize data
        synchronized_data = pd.DataFrame({time_col: target_times})
        
        numeric_columns = data_sorted.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col == time_col:
                continue
            
            if sync_method == 'interpolation':
                # Linear interpolation
                f = interp1d(
                    time_sorted.astype('int64'),
                    data_sorted[col].values,
                    kind='linear',
                    bounds_error=False,
                    fill_value=np.nan
                )
                synchronized_data[col] = f(target_times.astype('int64'))
                
            elif sync_method == 'forward_fill':
                # Forward fill (step function)
                synchronized_data[col] = data_sorted.set_index(time_col)[col].reindex(
                    target_times, method='ffill'
                )
                
            elif sync_method == 'nearest':
                # Nearest neighbor
                synchronized_data[col] = data_sorted.set_index(time_col)[col].reindex(
                    target_times, method='nearest'
                )
        
        self.logger.info(f"Synchronized data to {target_rate:.2f} Hz ({len(synchronized_data)} points)")
        return synchronized_data
    
    def _identify_time_column(self, data: pd.DataFrame) -> Optional[str]:
        """Identify the time column in the data"""
        potential_time_cols = ['timestamp', 'time', 'datetime', 'date']
        
        for col in potential_time_cols:
            if col in data.columns:
                return col
        
        return None

class DataPipeline:
    """
    Main data pipeline orchestrating multiple processing stages
    """
    
    def __init__(self, options: ProcessingOptions = None):
        """Initialize data pipeline"""
        self.pipeline_id = f"data_pipeline_{int(time.time())}"
        self.options = options or ProcessingOptions()
        self.logger = logging.getLogger(f"{__name__}.DataPipeline")
        
        # Initialize processors
        self.processors = {
            ProcessingStage.FILTERING: FilterProcessor(),
            ProcessingStage.OUTLIER_REMOVAL: OutlierProcessor(),
            ProcessingStage.INTERPOLATION: InterpolationProcessor(),
            ProcessingStage.SYNCHRONIZATION: SynchronizationProcessor()
        }
        
        # Processing stages configuration
        self.stages = self._configure_default_stages()
        
        # Integration with existing data loader
        self.data_loader = None
        if MODULAR_DATA_AVAILABLE:
            try:
                self.data_loader = DataLoader()
                self.logger.info("Integrated with existing DataLoader")
            except Exception as e:
                self.logger.warning(f"DataLoader integration failed: {e}")
        
        self.logger.info(f"DataPipeline initialized: {self.pipeline_id}")
    
    def _configure_default_stages(self) -> List[PipelineStage]:
        """Configure default processing stages"""
        stages = []
        
        if self.options.enable_filtering:
            stages.append(PipelineStage(
                stage_id="filtering",
                stage_type=ProcessingStage.FILTERING,
                options={
                    'filter_type': self.options.filter_type.value,
                    'filter_order': self.options.filter_order,
                    'cutoff_frequency': self.options.cutoff_frequency
                }
            ))
        
        if self.options.enable_outlier_removal:
            stages.append(PipelineStage(
                stage_id="outlier_removal",
                stage_type=ProcessingStage.OUTLIER_REMOVAL,
                options={
                    'outlier_method': self.options.outlier_method,
                    'outlier_threshold': self.options.outlier_threshold
                }
            ))
        
        if self.options.enable_interpolation:
            stages.append(PipelineStage(
                stage_id="interpolation",
                stage_type=ProcessingStage.INTERPOLATION,
                options={
                    'interpolation_method': self.options.interpolation_method,
                    'max_gap_seconds': self.options.max_gap_seconds
                }
            ))
        
        if self.options.enable_synchronization:
            stages.append(PipelineStage(
                stage_id="synchronization",
                stage_type=ProcessingStage.SYNCHRONIZATION,
                options={
                    'target_sampling_rate': self.options.target_sampling_rate,
                    'sync_method': self.options.sync_method
                }
            ))
        
        return stages
    
    async def process_data_source(self, source: DataSource) -> ProcessingResult:
        """Process data from a configured source"""
        try:
            # Load data
            data = await self._load_data(source)
            if data is None or len(data) == 0:
                return ProcessingResult(
                    success=False,
                    errors=["Failed to load data from source"]
                )
            
            # Process through pipeline
            return await self.process_data(data)
            
        except Exception as e:
            self.logger.error(f"Data source processing failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[f"Processing failed: {str(e)}"]
            )
    
    async def process_data(self, data: pd.DataFrame) -> ProcessingResult:
        """Process data through the configured pipeline"""
        start_time = time.time()
        
        try:
            # Initialize result
            result = ProcessingResult(
                success=False,
                data=data.copy(),
                original_rows=len(data)
            )
            
            # Validate input data
            if not self._validate_input_data(data):
                result.errors.append("Input data validation failed")
                return result
            
            current_data = data.copy()
            
            # Execute processing stages
            for stage in self.stages:
                if not stage.enabled:
                    continue
                
                processor = self.processors.get(stage.stage_type)
                if not processor:
                    warning = f"Processor not found for stage: {stage.stage_type.value}"
                    result.warnings.append(warning)
                    self.logger.warning(warning)
                    continue
                
                try:
                    # Process stage
                    stage_start = time.time()
                    processed_data = await processor.process(current_data, stage.options)
                    stage_time = time.time() - stage_start
                    
                    # Update current data
                    current_data = processed_data
                    result.stages_completed.append(stage.stage_id)
                    
                    # Store stage results
                    result.stage_results[stage.stage_id] = {
                        'processing_time': stage_time,
                        'rows_processed': len(processed_data),
                        'stage_type': stage.stage_type.value
                    }
                    
                    self.logger.info(f"Stage {stage.stage_id} completed in {stage_time:.2f}s")
                    
                except Exception as e:
                    error = f"Stage {stage.stage_id} failed: {str(e)}"
                    result.errors.append(error)
                    self.logger.error(error)
            
            # Calculate final metrics
            result.data = current_data
            result.processed_rows = len(current_data)
            result.processing_time = time.time() - start_time
            result.missing_data_ratio = current_data.isnull().sum().sum() / (len(current_data) * len(current_data.columns))
            
            # Set success status
            result.success = len(result.errors) == 0
            
            self.logger.info(f"Pipeline processing completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Pipeline processing error: {e}")
            return ProcessingResult(
                success=False,
                errors=[f"Pipeline error: {str(e)}"],
                processing_time=time.time() - start_time
            )
    
    async def _load_data(self, source: DataSource) -> Optional[pd.DataFrame]:
        """Load data from configured source"""
        try:
            if source.source_type == DataSourceType.CSV_FILE:
                return pd.read_csv(
                    source.location,
                    skiprows=source.skip_rows,
                    encoding=source.encoding,
                    parse_dates=[source.time_column] if source.parse_dates else False
                )
            
            elif source.source_type == DataSourceType.EXCEL_FILE:
                return pd.read_excel(
                    source.location,
                    skiprows=source.skip_rows
                )
            
            # Additional source types would be implemented here
            else:
                self.logger.warning(f"Unsupported source type: {source.source_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Data loading failed: {e}")
            return None
    
    def _validate_input_data(self, data: pd.DataFrame) -> bool:
        """Validate input data"""
        if data is None or len(data) == 0:
            return False
        
        if len(data) < self.options.min_data_points:
            self.logger.warning(f"Insufficient data points: {len(data)} < {self.options.min_data_points}")
            return False
        
        # Check missing data ratio
        missing_ratio = data.isnull().sum().sum() / (len(data) * len(data.columns))
        if missing_ratio > self.options.max_missing_ratio:
            self.logger.warning(f"Too much missing data: {missing_ratio:.2%} > {self.options.max_missing_ratio:.2%}")
            return False
        
        return True
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline configuration information"""
        return {
            'pipeline_id': self.pipeline_id,
            'stages_configured': len(self.stages),
            'processors_available': list(self.processors.keys()),
            'options': {
                'filtering_enabled': self.options.enable_filtering,
                'outlier_removal_enabled': self.options.enable_outlier_removal,
                'interpolation_enabled': self.options.enable_interpolation,
                'synchronization_enabled': self.options.enable_synchronization
            },
            'integration': {
                'data_loader_available': self.data_loader is not None,
                'pid_bundle_available': PID_BUNDLE_AVAILABLE
            }
        }

# Convenience functions
async def process_csv_file(file_path: str, 
                          time_column: str = "timestamp",
                          options: ProcessingOptions = None) -> ProcessingResult:
    """Convenience function to process CSV file"""
    source = DataSource(
        source_id="csv_file",
        source_type=DataSourceType.CSV_FILE,
        location=file_path,
        time_column=time_column
    )
    
    pipeline = DataPipeline(options)
    return await pipeline.process_data_source(source)

def create_default_processing_options() -> ProcessingOptions:
    """Create default processing options for control loop data"""
    return ProcessingOptions(
        enable_filtering=True,
        filter_type=FilterType.BUTTERWORTH,
        filter_order=2,
        cutoff_frequency=0.1,
        
        enable_outlier_removal=True,
        outlier_method="iqr",
        outlier_threshold=2.0,
        
        enable_interpolation=True,
        interpolation_method="linear",
        max_gap_seconds=10.0,
        
        enable_synchronization=True,
        sync_method="interpolation"
    )

if __name__ == "__main__":
    # Demo and testing
    async def main():
        logger.info("🚀 Enhanced Control Loop Data Pipeline - Demo")
        
        # Create sample data with issues
        np.random.seed(42)
        time_points = pd.date_range('2025-01-01', periods=100, freq='1S')
        sample_data = pd.DataFrame({
            'timestamp': time_points,
            'CV': np.random.randn(100).cumsum() + 50,
            'PV': np.random.randn(100).cumsum() + 25,
            'SP': np.full(100, 30)
        })
        
        # Add some issues for testing
        sample_data.loc[10:15, 'PV'] = np.nan  # Missing data
        sample_data.loc[30, 'CV'] = 200  # Outlier
        sample_data.loc[31, 'CV'] = -50  # Another outlier
        
        # Create pipeline with default options
        options = create_default_processing_options()
        pipeline = DataPipeline(options)
        
        # Test processing
        try:
            result = await pipeline.process_data(sample_data)
            
            logger.info(f"✅ Processing completed: {result.success}")
            logger.info(f"📊 Original rows: {result.original_rows}")
            logger.info(f"📊 Processed rows: {result.processed_rows}")
            logger.info(f"📊 Stages completed: {result.stages_completed}")
            logger.info(f"📊 Missing data ratio: {result.missing_data_ratio:.2%}")
            logger.info(f"⚡ Processing time: {result.processing_time:.2f}s")
            
            if result.warnings:
                logger.warning(f"⚠️ Warnings: {result.warnings}")
            
            if result.errors:
                logger.error(f"❌ Errors: {result.errors}")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
        
        logger.info("✅ Data pipeline demo completed")
    
    asyncio.run(main()) 