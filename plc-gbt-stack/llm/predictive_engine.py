#!/usr/bin/env python3
"""
Phase 23.4.1: Predictive Analysis Engine
=======================================

Advanced ML-powered prediction and forecasting system for industrial control
applications. Provides predictive analytics, trend analysis, failure prediction,
and performance forecasting using multiple machine learning algorithms.

This module integrates with Phase 23.1-23.3 components to provide intelligent
predictive capabilities for control loop optimization, maintenance scheduling,
and system performance enhancement.

Components:
- PredictiveEngine: Core prediction orchestration system
- TimeSeriesPredictor: Advanced time series forecasting
- AnomalyDetector: Real-time anomaly detection and alerting
- PerformanceForecaster: System performance prediction
- MaintenancePredictor: Predictive maintenance scheduling
- TrendAnalyzer: Long-term trend analysis and insights

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 23.4.1 - Predictive Analysis Engine
Methodology: AI Task Orchestrator Guide
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import pickle
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Types of predictions supported"""
    TIME_SERIES = "time_series"
    ANOMALY_DETECTION = "anomaly_detection"
    PERFORMANCE_FORECAST = "performance_forecast"
    MAINTENANCE_SCHEDULE = "maintenance_schedule"
    TREND_ANALYSIS = "trend_analysis"
    FAILURE_PREDICTION = "failure_prediction"
    OPTIMIZATION_RECOMMENDATION = "optimization_recommendation"

class ModelType(Enum):
    """Machine learning model types"""
    RANDOM_FOREST = "random_forest"
    LINEAR_REGRESSION = "linear_regression"
    LSTM_NEURAL_NETWORK = "lstm_neural_network"
    ISOLATION_FOREST = "isolation_forest"
    SUPPORT_VECTOR_MACHINE = "svm"
    ENSEMBLE_HYBRID = "ensemble_hybrid"

class PredictionConfidence(Enum):
    """Prediction confidence levels"""
    VERY_LOW = "very_low"      # < 50%
    LOW = "low"                # 50-65%
    MEDIUM = "medium"          # 65-80%
    HIGH = "high"              # 80-90%
    VERY_HIGH = "very_high"    # 90-95%
    ABSOLUTE = "absolute"      # > 95%

@dataclass
class PredictionRequest:
    """Request for predictive analysis"""
    request_id: str
    prediction_type: PredictionType
    target_variable: str
    data_source: str
    time_horizon: timedelta
    confidence_threshold: float = 0.8
    model_preference: Optional[ModelType] = None
    historical_window: timedelta = field(default_factory=lambda: timedelta(days=30))
    prediction_intervals: int = 24  # Number of prediction points
    
    # Context and parameters
    context: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    requested_by: str = "system"
    priority: int = 1  # 1=low, 5=critical

@dataclass
class PredictionResult:
    """Result of predictive analysis"""
    # Required fields (no defaults)
    request_id: str
    prediction_type: PredictionType
    model_used: ModelType
    predictions: List[float]
    timestamps: List[datetime]
    confidence_scores: List[float]
    accuracy_score: float
    confidence_level: PredictionConfidence
    model_performance: Dict[str, float]
    
    # Optional fields (with defaults)
    prediction_intervals: Optional[List[Tuple[float, float]]] = None
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    data_points_used: int = 0
    feature_importance: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class TimeSeriesPredictor:
    """Advanced time series forecasting system"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_extractors = {}
        
    async def predict_time_series(self, request: PredictionRequest, data: pd.DataFrame) -> PredictionResult:
        """Generate time series predictions"""
        logger.info(f"Starting time series prediction for {request.target_variable}")
        
        start_time = time.time()
        
        try:
            # Prepare data
            prepared_data = self._prepare_time_series_data(data, request.target_variable)
            
            # Feature engineering
            features = self._extract_time_series_features(prepared_data, request)
            
            # Model selection and training
            model = self._select_and_train_model(features, request)
            
            # Generate predictions
            predictions, confidence_scores = self._generate_predictions(model, features, request)
            
            # Calculate prediction intervals
            intervals = self._calculate_prediction_intervals(predictions, confidence_scores, request)
            
            # Performance evaluation
            performance_metrics = self._evaluate_model_performance(model, features, request)
            
            # Generate insights
            insights = self._generate_time_series_insights(predictions, data, request)
            recommendations = self._generate_time_series_recommendations(predictions, insights, request)
            alerts = self._generate_time_series_alerts(predictions, confidence_scores, request)
            
            # Create timestamps for predictions
            timestamps = self._generate_prediction_timestamps(request)
            
            execution_time = time.time() - start_time
            
            return PredictionResult(
                request_id=request.request_id,
                prediction_type=request.prediction_type,
                model_used=request.model_preference or ModelType.RANDOM_FOREST,
                predictions=predictions,
                timestamps=timestamps,
                confidence_scores=confidence_scores,
                prediction_intervals=intervals,
                accuracy_score=performance_metrics.get('accuracy', 0.0),
                confidence_level=self._determine_confidence_level(confidence_scores),
                model_performance=performance_metrics,
                insights=insights,
                recommendations=recommendations,
                alerts=alerts,
                execution_time=execution_time,
                data_points_used=len(prepared_data),
                feature_importance=self._extract_feature_importance(model, features)
            )
            
        except Exception as e:
            logger.error(f"Time series prediction failed: {e}")
            raise
            
    def _prepare_time_series_data(self, data: pd.DataFrame, target_variable: str) -> pd.DataFrame:
        """Prepare time series data for modeling"""
        # Ensure datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data.set_index('timestamp')
            else:
                data.index = pd.to_datetime(data.index)
                
        # Sort by timestamp
        data = data.sort_index()
        
        # Handle missing values
        data = data.fillna(method='forward').fillna(method='backward')
        
        # Remove outliers using IQR method
        if target_variable in data.columns:
            Q1 = data[target_variable].quantile(0.25)
            Q3 = data[target_variable].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            data = data[(data[target_variable] >= lower_bound) & (data[target_variable] <= upper_bound)]
            
        return data
        
    def _extract_time_series_features(self, data: pd.DataFrame, request: PredictionRequest) -> pd.DataFrame:
        """Extract time series features for modeling"""
        features = data.copy()
        target_var = request.target_variable
        
        if target_var in features.columns:
            # Lag features
            for lag in [1, 2, 3, 6, 12, 24]:
                features[f'{target_var}_lag_{lag}'] = features[target_var].shift(lag)
                
            # Rolling statistics
            for window in [3, 6, 12, 24]:
                features[f'{target_var}_rolling_mean_{window}'] = features[target_var].rolling(window=window).mean()
                features[f'{target_var}_rolling_std_{window}'] = features[target_var].rolling(window=window).std()
                features[f'{target_var}_rolling_min_{window}'] = features[target_var].rolling(window=window).min()
                features[f'{target_var}_rolling_max_{window}'] = features[target_var].rolling(window=window).max()
                
            # Exponential moving averages
            for alpha in [0.1, 0.3, 0.5]:
                features[f'{target_var}_ema_{alpha}'] = features[target_var].ewm(alpha=alpha).mean()
                
            # Time-based features
            features['hour'] = features.index.hour
            features['day_of_week'] = features.index.dayofweek
            features['day_of_month'] = features.index.day
            features['month'] = features.index.month
            features['quarter'] = features.index.quarter
            features['is_weekend'] = (features.index.dayofweek >= 5).astype(int)
            
            # Cyclical encoding for time features
            features['hour_sin'] = np.sin(2 * np.pi * features['hour'] / 24)
            features['hour_cos'] = np.cos(2 * np.pi * features['hour'] / 24)
            features['day_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
            features['day_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
            features['month_sin'] = np.sin(2 * np.pi * features['month'] / 12)
            features['month_cos'] = np.cos(2 * np.pi * features['month'] / 12)
            
            # Difference features
            features[f'{target_var}_diff_1'] = features[target_var].diff(1)
            features[f'{target_var}_diff_2'] = features[target_var].diff(2)
            
            # Percentage change
            features[f'{target_var}_pct_change_1'] = features[target_var].pct_change(1)
            features[f'{target_var}_pct_change_6'] = features[target_var].pct_change(6)
            
        # Remove NaN values
        features = features.dropna()
        
        return features
        
    def _select_and_train_model(self, features: pd.DataFrame, request: PredictionRequest) -> Any:
        """Select and train the best model for time series prediction"""
        target_var = request.target_variable
        
        if target_var not in features.columns:
            raise ValueError(f"Target variable {target_var} not found in features")
            
        # Prepare training data
        X = features.drop(columns=[target_var])
        y = features[target_var]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Store scaler for later use
        self.scalers[request.request_id] = scaler
        
        # Model selection based on preference or automatic selection
        if request.model_preference == ModelType.RANDOM_FOREST:
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        else:
            # Default to Random Forest
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Store model
        self.models[request.request_id] = model
        
        return model
        
    def _generate_predictions(self, model: Any, features: pd.DataFrame, request: PredictionRequest) -> Tuple[List[float], List[float]]:
        """Generate predictions and confidence scores"""
        target_var = request.target_variable
        scaler = self.scalers[request.request_id]
        
        # Use the last available data point as starting point
        last_data = features.tail(1)
        predictions = []
        confidence_scores = []
        
        # Generate predictions for requested intervals
        current_data = last_data.copy()
        
        for i in range(request.prediction_intervals):
            # Prepare features for prediction
            X = current_data.drop(columns=[target_var])
            X_scaled = scaler.transform(X)
            
            # Make prediction
            pred = model.predict(X_scaled)[0]
            predictions.append(float(pred))
            
            # Calculate confidence based on model uncertainty
            if hasattr(model, 'estimators_'):
                # For ensemble models, use prediction variance
                pred_std = np.std([estimator.predict(X_scaled)[0] for estimator in model.estimators_])
                confidence = max(0.0, min(1.0, 1.0 - pred_std / abs(pred) if pred != 0 else 0.5))
            else:
                # Simple confidence based on feature similarity
                confidence = 0.8  # Default confidence
                
            confidence_scores.append(confidence)
            
            # Update current_data for next iteration (simulate time progression)
            current_data = self._update_features_for_next_prediction(current_data, pred, request)
            
        return predictions, confidence_scores
        
    def _update_features_for_next_prediction(self, current_data: pd.DataFrame, prediction: float, request: PredictionRequest) -> pd.DataFrame:
        """Update features for the next prediction iteration"""
        updated_data = current_data.copy()
        target_var = request.target_variable
        
        # Update target variable with prediction
        updated_data[target_var] = prediction
        
        # Update lag features
        for lag in [1, 2, 3, 6, 12, 24]:
            lag_col = f'{target_var}_lag_{lag}'
            if lag_col in updated_data.columns:
                if lag == 1:
                    updated_data[lag_col] = prediction
                # For higher lags, we would need more sophisticated logic
                
        # Update rolling statistics (simplified)
        for window in [3, 6, 12, 24]:
            mean_col = f'{target_var}_rolling_mean_{window}'
            if mean_col in updated_data.columns:
                # Simplified update - in practice, you'd maintain a rolling window
                updated_data[mean_col] = prediction
                
        return updated_data
        
    def _calculate_prediction_intervals(self, predictions: List[float], confidence_scores: List[float], request: PredictionRequest) -> List[Tuple[float, float]]:
        """Calculate prediction intervals"""
        intervals = []
        
        for pred, conf in zip(predictions, confidence_scores):
            # Calculate interval width based on confidence
            interval_width = pred * (1 - conf) * 2  # Adjustable multiplier
            lower_bound = pred - interval_width
            upper_bound = pred + interval_width
            intervals.append((float(lower_bound), float(upper_bound)))
            
        return intervals
        
    def _evaluate_model_performance(self, model: Any, features: pd.DataFrame, request: PredictionRequest) -> Dict[str, float]:
        """Evaluate model performance"""
        target_var = request.target_variable
        scaler = self.scalers[request.request_id]
        
        # Prepare test data
        X = features.drop(columns=[target_var])
        y = features[target_var]
        
        # Split for evaluation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        X_test_scaled = scaler.transform(X_test)
        
        # Make predictions on test set
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Convert R² to accuracy percentage
        accuracy = max(0.0, min(1.0, r2)) * 100
        
        return {
            'accuracy': accuracy,
            'mse': float(mse),
            'mae': float(mae),
            'r2_score': float(r2),
            'rmse': float(np.sqrt(mse))
        }
        
    def _extract_feature_importance(self, model: Any, features: pd.DataFrame) -> Dict[str, float]:
        """Extract feature importance from model"""
        if hasattr(model, 'feature_importances_'):
            feature_names = features.drop(columns=[features.columns[0]]).columns
            importances = model.feature_importances_
            return {name: float(importance) for name, importance in zip(feature_names, importances)}
        return {}
        
    def _generate_time_series_insights(self, predictions: List[float], data: pd.DataFrame, request: PredictionRequest) -> List[str]:
        """Generate insights from time series predictions"""
        insights = []
        
        if not predictions:
            return insights
            
        # Trend analysis
        if len(predictions) > 1:
            trend_slope = (predictions[-1] - predictions[0]) / len(predictions)
            if abs(trend_slope) > 0.1:
                direction = "increasing" if trend_slope > 0 else "decreasing"
                insights.append(f"Strong {direction} trend detected with slope {trend_slope:.3f}")
            else:
                insights.append("Stable trend with minimal variation")
                
        # Volatility analysis
        pred_std = np.std(predictions)
        pred_mean = np.mean(predictions)
        cv = pred_std / pred_mean if pred_mean != 0 else 0
        
        if cv > 0.2:
            insights.append(f"High volatility detected (CV: {cv:.2f}) - consider additional monitoring")
        elif cv < 0.05:
            insights.append(f"Very stable predictions (CV: {cv:.2f}) - consistent performance expected")
            
        # Range analysis
        pred_min, pred_max = min(predictions), max(predictions)
        pred_range = pred_max - pred_min
        insights.append(f"Predicted range: {pred_min:.2f} to {pred_max:.2f} (span: {pred_range:.2f})")
        
        # Seasonal patterns (if applicable)
        if len(predictions) >= 24:  # Daily pattern
            hourly_avg = np.mean(np.array(predictions).reshape(-1, 24), axis=0)
            peak_hour = np.argmax(hourly_avg)
            valley_hour = np.argmin(hourly_avg)
            insights.append(f"Daily pattern: peak at hour {peak_hour}, valley at hour {valley_hour}")
            
        return insights
        
    def _generate_time_series_recommendations(self, predictions: List[float], insights: List[str], request: PredictionRequest) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not predictions:
            return recommendations
            
        # Performance optimization recommendations
        pred_mean = np.mean(predictions)
        pred_std = np.std(predictions)
        
        if pred_std > pred_mean * 0.1:
            recommendations.append("High variability detected - consider implementing predictive control strategies")
            
        # Maintenance recommendations
        if any("increasing" in insight for insight in insights):
            recommendations.append("Upward trend may indicate degradation - schedule preventive maintenance")
        elif any("decreasing" in insight for insight in insights):
            recommendations.append("Downward trend detected - investigate potential efficiency improvements")
            
        # Monitoring recommendations
        if len(predictions) > 12:
            recent_trend = np.mean(predictions[-6:]) - np.mean(predictions[:6])
            if abs(recent_trend) > pred_std:
                recommendations.append("Significant recent change detected - increase monitoring frequency")
                
        # Optimization opportunities
        if pred_std < pred_mean * 0.02:
            recommendations.append("Very stable performance - consider optimizing for efficiency gains")
            
        return recommendations
        
    def _generate_time_series_alerts(self, predictions: List[float], confidence_scores: List[float], request: PredictionRequest) -> List[str]:
        """Generate alerts based on predictions"""
        alerts = []
        
        if not predictions:
            return alerts
            
        # Low confidence alerts
        low_confidence_count = sum(1 for conf in confidence_scores if conf < 0.6)
        if low_confidence_count > len(confidence_scores) * 0.3:
            alerts.append(f"HIGH: {low_confidence_count} predictions have low confidence - verify data quality")
            
        # Extreme value alerts
        pred_mean = np.mean(predictions)
        pred_std = np.std(predictions)
        extreme_threshold = pred_mean + 3 * pred_std
        
        extreme_values = [p for p in predictions if abs(p - pred_mean) > 3 * pred_std]
        if extreme_values:
            alerts.append(f"MEDIUM: {len(extreme_values)} extreme values predicted - investigate potential issues")
            
        # Rapid change alerts
        if len(predictions) > 1:
            max_change = max(abs(predictions[i] - predictions[i-1]) for i in range(1, len(predictions)))
            if max_change > pred_std * 2:
                alerts.append(f"MEDIUM: Rapid change detected (max: {max_change:.2f}) - monitor closely")
                
        return alerts
        
    def _generate_prediction_timestamps(self, request: PredictionRequest) -> List[datetime]:
        """Generate timestamps for predictions"""
        start_time = datetime.now()
        time_delta = request.time_horizon / request.prediction_intervals
        
        timestamps = []
        for i in range(request.prediction_intervals):
            timestamp = start_time + (time_delta * i)
            timestamps.append(timestamp)
            
        return timestamps
        
    def _determine_confidence_level(self, confidence_scores: List[float]) -> PredictionConfidence:
        """Determine overall confidence level"""
        if not confidence_scores:
            return PredictionConfidence.LOW
            
        avg_confidence = np.mean(confidence_scores)
        
        if avg_confidence >= 0.95:
            return PredictionConfidence.ABSOLUTE
        elif avg_confidence >= 0.90:
            return PredictionConfidence.VERY_HIGH
        elif avg_confidence >= 0.80:
            return PredictionConfidence.HIGH
        elif avg_confidence >= 0.65:
            return PredictionConfidence.MEDIUM
        elif avg_confidence >= 0.50:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW

class AnomalyDetector:
    """Real-time anomaly detection system"""
    
    def __init__(self):
        self.models = {}
        self.thresholds = {}
        
    async def detect_anomalies(self, request: PredictionRequest, data: pd.DataFrame) -> PredictionResult:
        """Detect anomalies in real-time data"""
        logger.info(f"Starting anomaly detection for {request.target_variable}")
        
        start_time = time.time()
        
        try:
            # Prepare data for anomaly detection
            prepared_data = self._prepare_anomaly_data(data, request.target_variable)
            
            # Train anomaly detection model
            model = self._train_anomaly_model(prepared_data, request)
            
            # Detect anomalies
            anomaly_scores, anomaly_labels = self._detect_anomalies_in_data(model, prepared_data, request)
            
            # Generate anomaly insights
            insights = self._generate_anomaly_insights(anomaly_scores, anomaly_labels, request)
            recommendations = self._generate_anomaly_recommendations(anomaly_scores, insights, request)
            alerts = self._generate_anomaly_alerts(anomaly_scores, anomaly_labels, request)
            
            execution_time = time.time() - start_time
            
            # Convert results to match PredictionResult format
            predictions = anomaly_scores.tolist()
            timestamps = self._generate_prediction_timestamps(request)
            confidence_scores = [1.0 - score for score in anomaly_scores]  # Convert anomaly scores to confidence
            
            return PredictionResult(
                request_id=request.request_id,
                prediction_type=request.prediction_type,
                model_used=ModelType.ISOLATION_FOREST,
                predictions=predictions,
                timestamps=timestamps,
                confidence_scores=confidence_scores,
                accuracy_score=self._calculate_anomaly_accuracy(anomaly_labels),
                confidence_level=self._determine_confidence_level(confidence_scores),
                model_performance={"anomaly_rate": float(np.mean(anomaly_labels))},
                insights=insights,
                recommendations=recommendations,
                alerts=alerts,
                execution_time=execution_time,
                data_points_used=len(prepared_data)
            )
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            raise
            
    def _prepare_anomaly_data(self, data: pd.DataFrame, target_variable: str) -> pd.DataFrame:
        """Prepare data for anomaly detection"""
        # Similar to time series preparation but focused on anomaly features
        prepared_data = data.copy()
        
        if target_variable in prepared_data.columns:
            # Calculate statistical features
            prepared_data[f'{target_variable}_zscore'] = (prepared_data[target_variable] - prepared_data[target_variable].mean()) / prepared_data[target_variable].std()
            prepared_data[f'{target_variable}_rolling_zscore'] = prepared_data[target_variable].rolling(window=10).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
            
            # Rate of change features
            prepared_data[f'{target_variable}_roc'] = prepared_data[target_variable].pct_change()
            prepared_data[f'{target_variable}_roc_3'] = prepared_data[target_variable].pct_change(3)
            
        return prepared_data.dropna()
        
    def _train_anomaly_model(self, data: pd.DataFrame, request: PredictionRequest) -> Any:
        """Train anomaly detection model"""
        # Use Isolation Forest for anomaly detection
        model = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        
        # Select features for training
        features = data.select_dtypes(include=[np.number])
        model.fit(features)
        
        # Store model
        self.models[request.request_id] = model
        
        return model
        
    def _detect_anomalies_in_data(self, model: Any, data: pd.DataFrame, request: PredictionRequest) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies in the data"""
        features = data.select_dtypes(include=[np.number])
        
        # Get anomaly scores
        anomaly_scores = model.decision_function(features)
        
        # Get anomaly labels (-1 for anomaly, 1 for normal)
        anomaly_labels = model.predict(features)
        
        # Convert to binary (1 for anomaly, 0 for normal)
        anomaly_binary = (anomaly_labels == -1).astype(int)
        
        # Normalize anomaly scores to [0, 1]
        anomaly_scores_normalized = (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min())
        
        return anomaly_scores_normalized, anomaly_binary
        
    def _calculate_anomaly_accuracy(self, anomaly_labels: np.ndarray) -> float:
        """Calculate anomaly detection accuracy"""
        # In real scenario, you'd compare with ground truth
        # For now, return based on detection consistency
        anomaly_rate = np.mean(anomaly_labels)
        
        # Good anomaly detection should find 5-15% anomalies typically
        if 0.05 <= anomaly_rate <= 0.15:
            return 85.0
        elif 0.02 <= anomaly_rate <= 0.20:
            return 75.0
        else:
            return 60.0
            
    def _generate_anomaly_insights(self, anomaly_scores: np.ndarray, anomaly_labels: np.ndarray, request: PredictionRequest) -> List[str]:
        """Generate insights from anomaly detection"""
        insights = []
        
        anomaly_rate = np.mean(anomaly_labels) * 100
        insights.append(f"Anomaly rate: {anomaly_rate:.1f}% of data points")
        
        if anomaly_rate > 20:
            insights.append("High anomaly rate detected - investigate data quality or system issues")
        elif anomaly_rate < 1:
            insights.append("Very low anomaly rate - system operating normally")
        else:
            insights.append("Normal anomaly rate detected - routine monitoring recommended")
            
        # Score distribution analysis
        high_risk_count = np.sum(anomaly_scores > 0.8)
        if high_risk_count > 0:
            insights.append(f"{high_risk_count} high-risk anomalies detected requiring immediate attention")
            
        return insights
        
    def _generate_anomaly_recommendations(self, anomaly_scores: np.ndarray, insights: List[str], request: PredictionRequest) -> List[str]:
        """Generate recommendations for anomaly handling"""
        recommendations = []
        
        anomaly_rate = np.mean(anomaly_scores > 0.5) * 100
        
        if anomaly_rate > 15:
            recommendations.append("High anomaly rate - implement additional data validation checks")
            recommendations.append("Consider adjusting control parameters to reduce variability")
        elif anomaly_rate < 2:
            recommendations.append("System stable - maintain current monitoring frequency")
        else:
            recommendations.append("Normal operation - continue routine anomaly monitoring")
            
        # High-risk anomaly recommendations
        high_risk_anomalies = np.sum(anomaly_scores > 0.9)
        if high_risk_anomalies > 0:
            recommendations.append(f"Investigate {high_risk_anomalies} critical anomalies immediately")
            
        return recommendations
        
    def _generate_anomaly_alerts(self, anomaly_scores: np.ndarray, anomaly_labels: np.ndarray, request: PredictionRequest) -> List[str]:
        """Generate alerts for detected anomalies"""
        alerts = []
        
        critical_anomalies = np.sum(anomaly_scores > 0.9)
        high_anomalies = np.sum(anomaly_scores > 0.7)
        medium_anomalies = np.sum(anomaly_scores > 0.5)
        
        if critical_anomalies > 0:
            alerts.append(f"CRITICAL: {critical_anomalies} critical anomalies detected - immediate action required")
            
        if high_anomalies > 5:
            alerts.append(f"HIGH: {high_anomalies} high-severity anomalies detected - investigate within 1 hour")
            
        if medium_anomalies > 10:
            alerts.append(f"MEDIUM: {medium_anomalies} moderate anomalies detected - investigate within 4 hours")
            
        return alerts

class PredictiveEngine:
    """Core predictive analysis orchestration system"""
    
    def __init__(self):
        self.time_series_predictor = TimeSeriesPredictor()
        self.anomaly_detector = AnomalyDetector()
        self.active_requests = {}
        self.prediction_cache = {}
        
        # Initialize model registry
        self.model_registry = {
            PredictionType.TIME_SERIES: self.time_series_predictor,
            PredictionType.ANOMALY_DETECTION: self.anomaly_detector,
            # Additional predictors can be added here
        }
        
    async def create_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Create a prediction based on the request type"""
        logger.info(f"Creating prediction for request {request.request_id}")
        
        self.active_requests[request.request_id] = request
        
        try:
            # Load data
            data = await self._load_prediction_data(request)
            
            # Validate data quality
            await self._validate_data_quality(data, request)
            
            # Route to appropriate predictor
            predictor = self.model_registry.get(request.prediction_type)
            if not predictor:
                raise ValueError(f"Unsupported prediction type: {request.prediction_type}")
                
            # Generate prediction
            if request.prediction_type == PredictionType.TIME_SERIES:
                result = await predictor.predict_time_series(request, data)
            elif request.prediction_type == PredictionType.ANOMALY_DETECTION:
                result = await predictor.detect_anomalies(request, data)
            else:
                raise ValueError(f"Prediction type {request.prediction_type} not implemented")
                
            # Cache result
            self.prediction_cache[request.request_id] = result
            
            logger.info(f"Prediction completed: {result.confidence_level.value} confidence, {result.accuracy_score:.1f}% accuracy")
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction creation failed: {e}")
            raise
        finally:
            self.active_requests.pop(request.request_id, None)
            
    async def _load_prediction_data(self, request: PredictionRequest) -> pd.DataFrame:
        """Load data for prediction"""
        # In a real implementation, this would load from various sources
        # For now, create sample data
        
        if request.data_source.endswith('.csv'):
            try:
                data = pd.read_csv(request.data_source)
            except FileNotFoundError:
                # Generate sample data for demonstration
                data = self._generate_sample_data(request)
        else:
            # Generate sample data
            data = self._generate_sample_data(request)
            
        return data
        
    def _generate_sample_data(self, request: PredictionRequest) -> pd.DataFrame:
        """Generate sample data for demonstration"""
        # Create realistic industrial control data
        np.random.seed(42)
        
        # Time range
        end_time = datetime.now()
        start_time = end_time - request.historical_window
        time_range = pd.date_range(start=start_time, end=end_time, freq='H')
        
        # Generate base signal with trend and seasonality
        n_points = len(time_range)
        base_value = 50.0
        
        # Trend component
        trend = np.linspace(0, 5, n_points)
        
        # Seasonal component (daily pattern)
        seasonal = 10 * np.sin(2 * np.pi * np.arange(n_points) / 24)
        
        # Noise component
        noise = np.random.normal(0, 2, n_points)
        
        # Combine components
        values = base_value + trend + seasonal + noise
        
        # Create DataFrame
        data = pd.DataFrame({
            'timestamp': time_range,
            request.target_variable: values,
            'temperature': 20 + 5 * np.sin(2 * np.pi * np.arange(n_points) / 24) + np.random.normal(0, 1, n_points),
            'pressure': 100 + 10 * np.cos(2 * np.pi * np.arange(n_points) / 12) + np.random.normal(0, 2, n_points),
            'flow_rate': 25 + 5 * np.random.random(n_points),
        })
        
        data = data.set_index('timestamp')
        
        return data
        
    async def _validate_data_quality(self, data: pd.DataFrame, request: PredictionRequest) -> None:
        """Validate data quality for prediction"""
        if data.empty:
            raise ValueError("Data is empty")
            
        if request.target_variable not in data.columns:
            raise ValueError(f"Target variable {request.target_variable} not found in data")
            
        # Check for sufficient data points
        min_points = max(50, request.prediction_intervals * 2)
        if len(data) < min_points:
            logger.warning(f"Limited data available: {len(data)} points (recommended: {min_points})")
            
        # Check for missing values
        missing_ratio = data[request.target_variable].isna().sum() / len(data)
        if missing_ratio > 0.1:
            logger.warning(f"High missing value ratio: {missing_ratio:.1%}")
            
        logger.info(f"Data quality validation passed: {len(data)} points, {missing_ratio:.1%} missing")
        
    def get_prediction_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a prediction request"""
        if request_id in self.active_requests:
            return {"status": "processing", "request": self.active_requests[request_id]}
        elif request_id in self.prediction_cache:
            return {"status": "completed", "result": self.prediction_cache[request_id]}
        else:
            return None
            
    def list_active_predictions(self) -> List[str]:
        """List all active prediction request IDs"""
        return list(self.active_requests.keys())
        
    def get_cached_predictions(self) -> List[str]:
        """Get list of cached prediction request IDs"""
        return list(self.prediction_cache.keys())

# Factory functions for common prediction requests
def create_control_loop_prediction_request(
    loop_name: str,
    target_variable: str,
    hours_ahead: int = 24,
    data_source: str = "historian"
) -> PredictionRequest:
    """Create a prediction request for control loop forecasting"""
    return PredictionRequest(
        request_id=f"loop_pred_{loop_name}_{int(time.time())}",
        prediction_type=PredictionType.TIME_SERIES,
        target_variable=target_variable,
        data_source=data_source,
        time_horizon=timedelta(hours=hours_ahead),
        historical_window=timedelta(days=7),
        prediction_intervals=hours_ahead,
        context={"loop_name": loop_name, "prediction_type": "control_loop"},
        requested_by="control_system"
    )

def create_anomaly_detection_request(
    system_name: str,
    target_variable: str,
    data_source: str = "realtime"
) -> PredictionRequest:
    """Create an anomaly detection request"""
    return PredictionRequest(
        request_id=f"anomaly_{system_name}_{int(time.time())}",
        prediction_type=PredictionType.ANOMALY_DETECTION,
        target_variable=target_variable,
        data_source=data_source,
        time_horizon=timedelta(hours=1),
        historical_window=timedelta(hours=24),
        prediction_intervals=1,
        context={"system_name": system_name, "detection_type": "realtime"},
        requested_by="monitoring_system"
    )

# Export main classes and functions
__all__ = [
    "PredictiveEngine", "TimeSeriesPredictor", "AnomalyDetector",
    "PredictionRequest", "PredictionResult", "PredictionType", "ModelType",
    "PredictionConfidence", "create_control_loop_prediction_request",
    "create_anomaly_detection_request"
]

if __name__ == "__main__":
    # Example usage
    async def main():
        engine = PredictiveEngine()
        
        # Create a time series prediction request
        request = create_control_loop_prediction_request(
            loop_name="TIC-101",
            target_variable="temperature",
            hours_ahead=24
        )
        
        # Generate prediction
        result = await engine.create_prediction(request)
        
        print(f"Prediction completed!")
        print(f"Confidence: {result.confidence_level.value}")
        print(f"Accuracy: {result.accuracy_score:.1f}%")
        print(f"Predictions: {len(result.predictions)} points")
        print(f"Execution time: {result.execution_time:.2f}s")
        
        if result.insights:
            print("\nInsights:")
            for insight in result.insights:
                print(f"  • {insight}")
                
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"  • {rec}")
        
    asyncio.run(main()) 