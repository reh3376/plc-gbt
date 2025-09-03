"""
Data Management Module
=====================

Modular data loading, validation, and preprocessing components.
Extracted from various files to eliminate code duplication.

Features:
- Standardized dataset loading
- Control variable extraction
- Data validation and cleaning
- Preprocessing pipelines
- Format conversion utilities
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class DatasetInfo:
    """Information about a loaded dataset"""
    file_path: str
    total_rows: int
    total_columns: int
    columns: List[str]
    memory_usage_mb: float
    load_timestamp: str
    file_size_mb: float
    data_types: Dict[str, str]

@dataclass
class ControlLoopData:
    """Structured control loop data"""
    pv_column: str
    sp_column: str
    cv_column: Optional[str]
    sp_method: str  # actual_column, synthetic_moving_average, etc.
    data_points: int
    pv_array: np.ndarray
    sp_array: np.ndarray
    error_array: np.ndarray
    cv_array: Optional[np.ndarray]
    process_statistics: Dict[str, float]
    data_quality: Dict[str, float]

class DataValidator:
    """Data validation utilities"""

    @staticmethod
    def validate_numeric_data(data: Union[pd.Series, np.ndarray],
                            column_name: str = "data") -> Dict[str, Any]:
        """
        Validate numeric data quality

        Args:
            data: Numeric data to validate
            column_name: Name for logging purposes

        Returns:
            Validation results dictionary
        """
        if isinstance(data, pd.Series):
            data_array = data.values
        else:
            data_array = np.array(data)

        validation = {
            "column_name": column_name,
            "total_points": len(data_array),
            "non_null_points": np.sum(~np.isnan(data_array)),
            "null_percentage": np.sum(np.isnan(data_array)) / len(data_array) * 100,
            "infinite_count": np.sum(np.isinf(data_array)),
            "min_value": np.nanmin(data_array),
            "max_value": np.nanmax(data_array),
            "mean_value": np.nanmean(data_array),
            "std_value": np.nanstd(data_array),
            "outlier_count": 0,
            "quality_score": 0.0
        }

        # Detect outliers using IQR method
        if validation["non_null_points"] > 0:
            q75, q25 = np.nanpercentile(data_array, [75, 25])
            iqr = q75 - q25
            if iqr > 0:
                lower_bound = q25 - (1.5 * iqr)
                upper_bound = q75 + (1.5 * iqr)
                validation["outlier_count"] = np.sum(
                    (data_array < lower_bound) | (data_array > upper_bound)
                )

        # Calculate quality score
        null_penalty = validation["null_percentage"] / 100
        infinite_penalty = min(validation["infinite_count"] / len(data_array), 0.5)
        outlier_penalty = min(validation["outlier_count"] / len(data_array), 0.3)

        validation["quality_score"] = max(0, 1.0 - null_penalty - infinite_penalty - outlier_penalty)

        return validation

    @staticmethod
    def validate_control_loop_data(pv_data: np.ndarray,
                                 sp_data: np.ndarray,
                                 cv_data: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Validate control loop data specifically"""
        validation = {
            "pv_validation": DataValidator.validate_numeric_data(pv_data, "PV"),
            "sp_validation": DataValidator.validate_numeric_data(sp_data, "SP"),
            "data_alignment": {
                "pv_length": len(pv_data),
                "sp_length": len(sp_data),
                "aligned": len(pv_data) == len(sp_data)
            },
            "control_quality": {}
        }

        if cv_data is not None:
            validation["cv_validation"] = DataValidator.validate_numeric_data(cv_data, "CV")
            validation["data_alignment"]["cv_length"] = len(cv_data)
            validation["data_alignment"]["cv_aligned"] = len(cv_data) == len(pv_data)

        # Control-specific quality metrics
        if validation["data_alignment"]["aligned"]:
            error_data = pv_data - sp_data

            # Control effectiveness
            pv_range = np.nanmax(pv_data) - np.nanmin(pv_data)
            error_range = np.nanmax(error_data) - np.nanmin(error_data)

            validation["control_quality"] = {
                "error_to_pv_ratio": error_range / pv_range if pv_range > 0 else float('inf'),
                "mean_absolute_error": np.nanmean(np.abs(error_data)),
                "error_std": np.nanstd(error_data),
                "setpoint_tracking": 1 - (np.nanstd(error_data) / np.nanstd(pv_data)) if np.nanstd(pv_data) > 0 else 0
            }

        return validation

class DataLoader:
    """Standardized data loading utilities"""

    @staticmethod
    def load_csv_dataset(file_path: str, **kwargs) -> Tuple[pd.DataFrame, DatasetInfo]:
        """
        Load CSV dataset with comprehensive metadata

        Args:
            file_path: Path to CSV file
            **kwargs: Additional pandas read_csv arguments

        Returns:
            Tuple of (DataFrame, DatasetInfo)
        """
        logger.info(f"📁 Loading dataset: {Path(file_path).name}")

        # Default pandas arguments
        load_args = {
            "low_memory": False,
            "encoding": "utf-8"
        }
        load_args.update(kwargs)

        try:
            # Load dataset
            df = pd.read_csv(file_path, **load_args)

            # Calculate file size
            file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)

            # Get data types
            data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

            # Create dataset info
            dataset_info = DatasetInfo(
                file_path=file_path,
                total_rows=len(df),
                total_columns=len(df.columns),
                columns=list(df.columns),
                memory_usage_mb=df.memory_usage(deep=True).sum() / (1024 * 1024),
                load_timestamp=datetime.now().isoformat(),
                file_size_mb=file_size_mb,
                data_types=data_types
            )

            logger.info(f"✅ Dataset loaded: {len(df):,} rows, {len(df.columns)} columns")
            logger.info(f"   Memory usage: {dataset_info.memory_usage_mb:.1f} MB")
            logger.info(f"   File size: {dataset_info.file_size_mb:.1f} MB")

            return df, dataset_info

        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            raise

    @staticmethod
    def detect_control_variables(df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """
        Auto-detect control loop variables in DataFrame

        Args:
            df: DataFrame to analyze

        Returns:
            Dictionary with detected column names
        """
        columns = df.columns.tolist()
        detected = {
            "pv_candidates": [],
            "sp_candidates": [],
            "cv_candidates": [],
            "recommended_pv": None,
            "recommended_sp": None,
            "recommended_cv": None
        }

        # Common patterns for control variables
        pv_patterns = [r'pv\d*', r'process.?var', r'measured', r'actual', r'feedback']
        sp_patterns = [r'sp\d*', r'set.?point', r'target', r'reference', r'desired']
        cv_patterns = [r'cv\d*', r'control.?var', r'output', r'manipulated', r'valve']

        # Search for matches
        for col in columns:
            col_lower = col.lower()

            # Check PV patterns
            for pattern in pv_patterns:
                if re.search(pattern, col_lower):
                    detected["pv_candidates"].append(col)
                    break

            # Check SP patterns
            for pattern in sp_patterns:
                if re.search(pattern, col_lower):
                    detected["sp_candidates"].append(col)
                    break

            # Check CV patterns
            for pattern in cv_patterns:
                if re.search(pattern, col_lower):
                    detected["cv_candidates"].append(col)
                    break

        # Select best candidates (first match or most likely)
        if detected["pv_candidates"]:
            detected["recommended_pv"] = detected["pv_candidates"][0]
        elif df.select_dtypes(include=[np.number]).columns.any():
            # Fallback to first numeric column
            detected["recommended_pv"] = df.select_dtypes(include=[np.number]).columns[0]

        if detected["sp_candidates"]:
            detected["recommended_sp"] = detected["sp_candidates"][0]

        if detected["cv_candidates"]:
            detected["recommended_cv"] = detected["cv_candidates"][0]

        logger.info("🔍 Control variable detection:")
        logger.info(f"   PV candidates: {detected['pv_candidates']}")
        logger.info(f"   SP candidates: {detected['sp_candidates']}")
        logger.info(f"   CV candidates: {detected['cv_candidates']}")

        return detected

class DataPreprocessor:
    """Data preprocessing utilities"""

    @staticmethod
    def clean_numeric_data(data: pd.Series) -> pd.Series:
        """
        Clean numeric data by handling common issues

        Args:
            data: Pandas Series to clean

        Returns:
            Cleaned Series
        """
        cleaned = data.copy()

        # Convert object types to numeric if possible
        if cleaned.dtype == 'object':
            cleaned = pd.to_numeric(cleaned, errors='coerce')

        # Remove infinite values
        cleaned = cleaned.replace([np.inf, -np.inf], np.nan)

        # Log cleaning results
        original_count = len(data)
        valid_count = cleaned.notna().sum()
        logger.debug(f"   Cleaned data: {valid_count}/{original_count} valid points")

        return cleaned

    @staticmethod
    def create_synthetic_setpoint(pv_data: np.ndarray,
                                method: str = "moving_average",
                                window_size: Optional[int] = None) -> Tuple[np.ndarray, str]:
        """
        Create synthetic setpoint from process variable data

        Args:
            pv_data: Process variable array
            method: Method to use ('moving_average', 'median_filter', 'trend_line')
            window_size: Window size for filtering methods

        Returns:
            Tuple of (synthetic_setpoint, method_description)
        """
        if window_size is None:
            window_size = min(100, len(pv_data) // 10)

        if method == "moving_average":
            # Create moving average setpoint
            df_pv = pd.Series(pv_data)
            sp_data = df_pv.rolling(window=window_size, center=True).mean()
            sp_data = sp_data.fillna(method='bfill').fillna(method='ffill')
            description = f"moving_average_window_{window_size}"

        elif method == "median_filter":
            # Use median filter for noise resistance
            from scipy.signal import medfilt
            kernel_size = min(window_size, len(pv_data) // 2)
            if kernel_size % 2 == 0:
                kernel_size += 1  # Ensure odd kernel size
            sp_data = medfilt(pv_data, kernel_size=kernel_size)
            description = f"median_filter_kernel_{kernel_size}"

        elif method == "trend_line":
            # Linear trend line
            time_points = np.arange(len(pv_data))
            coeffs = np.polyfit(time_points, pv_data, 1)
            sp_data = np.polyval(coeffs, time_points)
            description = "linear_trend"

        else:
            raise ValueError(f"Unknown setpoint method: {method}")

        logger.info(f"   Created synthetic setpoint using {description}")
        return np.array(sp_data), description

    @staticmethod
    def extract_control_loop_data(df: pd.DataFrame,
                                pv_column: Optional[str] = None,
                                sp_column: Optional[str] = None,
                                cv_column: Optional[str] = None,
                                auto_detect: bool = True) -> ControlLoopData:
        """
        Extract and structure control loop data from DataFrame

        Args:
            df: Input DataFrame
            pv_column: Process variable column name
            sp_column: Setpoint column name
            cv_column: Control variable column name
            auto_detect: Whether to auto-detect columns if not specified

        Returns:
            ControlLoopData object
        """
        logger.info("🔍 Extracting control loop variables...")

        # Auto-detect columns if not specified
        if auto_detect:
            detected = DataLoader.detect_control_variables(df)

            if not pv_column:
                pv_column = detected["recommended_pv"]
            if not sp_column:
                sp_column = detected["recommended_sp"]
            if not cv_column:
                cv_column = detected["recommended_cv"]

        if not pv_column:
            raise ValueError("No process variable column specified or detected")

        # Extract and clean PV data
        pv_data = DataPreprocessor.clean_numeric_data(df[pv_column]).dropna()

        # Handle setpoint
        if sp_column and sp_column in df.columns:
            sp_data = DataPreprocessor.clean_numeric_data(df[sp_column]).dropna()
            sp_method = "actual_column"
        else:
            # Create synthetic setpoint
            sp_data_array, sp_method = DataPreprocessor.create_synthetic_setpoint(pv_data.values)
            sp_data = pd.Series(sp_data_array, index=pv_data.index[:len(sp_data_array)])
            sp_column = "synthetic"

        # Align data lengths
        min_length = min(len(pv_data), len(sp_data))
        pv_array = pv_data.iloc[:min_length].values
        sp_array = sp_data.iloc[:min_length].values
        error_array = pv_array - sp_array

        # Extract control variable if available
        cv_array = None
        if cv_column and cv_column in df.columns:
            cv_data = DataPreprocessor.clean_numeric_data(df[cv_column]).dropna()
            cv_array = cv_data.iloc[:min_length].values

        # Calculate process statistics
        process_statistics = {
            "pv_mean": float(np.mean(pv_array)),
            "pv_std": float(np.std(pv_array)),
            "pv_range": float(np.max(pv_array) - np.min(pv_array)),
            "pv_min": float(np.min(pv_array)),
            "pv_max": float(np.max(pv_array)),
            "sp_mean": float(np.mean(sp_array)),
            "sp_std": float(np.std(sp_array)),
            "sp_range": float(np.max(sp_array) - np.min(sp_array)),
            "error_mean": float(np.mean(error_array)),
            "error_std": float(np.std(error_array)),
            "error_abs_mean": float(np.mean(np.abs(error_array))),
            "error_range": float(np.max(error_array) - np.min(error_array))
        }

        # Calculate data quality metrics
        pv_validation = DataValidator.validate_numeric_data(pv_array, "PV")
        sp_validation = DataValidator.validate_numeric_data(sp_array, "SP")

        data_quality = {
            "pv_quality_score": pv_validation["quality_score"],
            "sp_quality_score": sp_validation["quality_score"],
            "overall_quality": (pv_validation["quality_score"] + sp_validation["quality_score"]) / 2,
            "data_completeness": min_length / len(df),
            "signal_to_noise_ratio": float(np.std(pv_array) / (np.std(error_array) + 1e-10))
        }

        if cv_array is not None:
            cv_validation = DataValidator.validate_numeric_data(cv_array, "CV")
            data_quality["cv_quality_score"] = cv_validation["quality_score"]
            data_quality["overall_quality"] = (
                pv_validation["quality_score"] +
                sp_validation["quality_score"] +
                cv_validation["quality_score"]
            ) / 3

        control_data = ControlLoopData(
            pv_column=pv_column,
            sp_column=sp_column,
            cv_column=cv_column,
            sp_method=sp_method,
            data_points=min_length,
            pv_array=pv_array,
            sp_array=sp_array,
            error_array=error_array,
            cv_array=cv_array,
            process_statistics=process_statistics,
            data_quality=data_quality
        )

        logger.info("✅ Control variables extracted")
        logger.info(f"   PV: {pv_column}, SP: {sp_column} ({sp_method}), CV: {cv_column}")
        logger.info(f"   Data points: {min_length:,}")
        logger.info(f"   Data quality: {data_quality['overall_quality']:.1%}")

        return control_data

class DatasetRegistry:
    """Registry for managing dataset metadata and access patterns"""

    def __init__(self):
        self.datasets = {}
        self.access_log = []

    def register_dataset(self, dataset_id: str,
                        dataset_info: DatasetInfo,
                        tags: Optional[List[str]] = None):
        """Register a dataset in the registry"""
        self.datasets[dataset_id] = {
            "info": dataset_info,
            "tags": tags or [],
            "registered_at": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None
        }

        logger.info(f"📋 Dataset registered: {dataset_id}")

    def get_dataset_info(self, dataset_id: str) -> Optional[DatasetInfo]:
        """Get dataset information"""
        if dataset_id in self.datasets:
            self.datasets[dataset_id]["access_count"] += 1
            self.datasets[dataset_id]["last_accessed"] = datetime.now().isoformat()
            return self.datasets[dataset_id]["info"]
        return None

    def find_datasets_by_tags(self, tags: List[str]) -> List[str]:
        """Find datasets matching any of the specified tags"""
        matching_datasets = []

        for dataset_id, metadata in self.datasets.items():
            if any(tag in metadata["tags"] for tag in tags):
                matching_datasets.append(dataset_id)

        return matching_datasets

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get registry usage statistics"""
        total_datasets = len(self.datasets)
        total_accesses = sum(ds["access_count"] for ds in self.datasets.values())

        most_accessed = max(
            self.datasets.items(),
            key=lambda x: x[1]["access_count"],
            default=(None, {"access_count": 0})
        )

        return {
            "total_datasets": total_datasets,
            "total_accesses": total_accesses,
            "most_accessed_dataset": most_accessed[0],
            "most_accessed_count": most_accessed[1]["access_count"],
            "average_accesses": total_accesses / total_datasets if total_datasets > 0 else 0
        }

# Utility functions for common data operations
def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to standard format"""
    df_normalized = df.copy()

    # Convert to lowercase and replace spaces/special chars with underscores
    df_normalized.columns = [
        re.sub(r'[^\w]', '_', col.lower().strip())
        for col in df_normalized.columns
    ]

    # Remove duplicate underscores
    df_normalized.columns = [
        re.sub(r'_+', '_', col).strip('_')
        for col in df_normalized.columns
    ]

    return df_normalized

def detect_time_column(df: pd.DataFrame) -> Optional[str]:
    """Detect time/timestamp column in DataFrame"""
    time_patterns = [r'time', r'timestamp', r'date', r'datetime', r'ts']

    for col in df.columns:
        col_lower = col.lower()
        for pattern in time_patterns:
            if re.search(pattern, col_lower):
                return col

    # Check for datetime dtypes
    datetime_cols = df.select_dtypes(include=['datetime64']).columns
    if len(datetime_cols) > 0:
        return datetime_cols[0]

    return None

def create_time_features(df: pd.DataFrame, time_column: str) -> pd.DataFrame:
    """Create time-based features from timestamp column"""
    df_features = df.copy()

    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df_features[time_column]):
        df_features[time_column] = pd.to_datetime(df_features[time_column])

    dt = df_features[time_column].dt

    # Create time features
    df_features['hour'] = dt.hour
    df_features['day_of_week'] = dt.dayofweek
    df_features['day_of_month'] = dt.day
    df_features['month'] = dt.month
    df_features['quarter'] = dt.quarter
    df_features['is_weekend'] = dt.dayofweek.isin([5, 6]).astype(int)
    df_features['is_business_hour'] = ((dt.hour >= 8) & (dt.hour <= 17)).astype(int)

    return df_features
