#!/usr/bin/env python3
"""
Phase 22.1.4: Historical Tracking System
========================================

Comprehensive historical tracking and trend analysis for control loop analysis
results with performance monitoring and predictive analytics.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from .database_schema import AnalysisType, DatabaseSchemaManager
from .result_storage import AnalysisResultStorage, QueryFilter

logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    """Trend direction indicators"""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    UNKNOWN = "unknown"

@dataclass
class TrendAnalysis:
    """Analysis of performance trends"""
    metric_name: str
    trend_direction: TrendDirection
    trend_magnitude: float
    confidence: float
    period_days: int
    start_value: float
    end_value: float
    change_percentage: float
    r_squared: float
    recommendations: List[str] = field(default_factory=list)

@dataclass
class PerformanceMetrics:
    """Performance metrics for analysis tracking"""
    period_start: datetime
    period_end: datetime
    total_executions: int
    success_rate: float
    average_execution_time: float
    execution_time_trend: TrendDirection
    error_count: int
    most_common_algorithms: List[Tuple[str, int]]
    performance_by_type: Dict[str, Dict[str, float]]
    outliers: List[Dict[str, Any]]

class HistoricalTracker:
    """
    Comprehensive historical tracking and trend analysis system
    """

    def __init__(self, schema_manager: DatabaseSchemaManager,
                 result_storage: AnalysisResultStorage):
        self.schema_manager = schema_manager
        self.result_storage = result_storage
        self.Session = sessionmaker(bind=schema_manager.engine)

        self.logger = logging.getLogger(__name__ + '.HistoricalTracker')

    def analyze_performance_trends(self,
                                 analysis_type: Optional[AnalysisType] = None,
                                 algorithm_name: Optional[str] = None,
                                 days_back: int = 30) -> List[TrendAnalysis]:
        """Analyze performance trends over specified period"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)

            # Get daily performance data
            daily_data = self._get_daily_performance_data(
                start_date, end_date, analysis_type, algorithm_name
            )

            if len(daily_data) < 7:  # Need at least a week of data
                self.logger.warning("Insufficient data for trend analysis")
                return []

            trends = []

            # Analyze execution time trend
            exec_time_trend = self._analyze_metric_trend(
                daily_data, 'avg_execution_time', 'Execution Time', days_back
            )
            trends.append(exec_time_trend)

            # Analyze success rate trend
            success_rate_trend = self._analyze_metric_trend(
                daily_data, 'success_rate', 'Success Rate', days_back
            )
            trends.append(success_rate_trend)

            # Analyze volume trend
            volume_trend = self._analyze_metric_trend(
                daily_data, 'execution_count', 'Execution Volume', days_back
            )
            trends.append(volume_trend)

            return trends

        except Exception as e:
            self.logger.error(f"Failed to analyze performance trends: {e}")
            raise

    def _get_daily_performance_data(self, start_date: datetime, end_date: datetime,
                                   analysis_type: Optional[AnalysisType] = None,
                                   algorithm_name: Optional[str] = None) -> pd.DataFrame:
        """Get daily aggregated performance data"""
        try:
            with self.Session() as session:
                table = self.schema_manager.tables['analysis_results']

                # Build query for daily aggregation
                query = sa.select(
                    sa.func.date_trunc('day', table.c.created_at).label('date'),
                    sa.func.count().label('execution_count'),
                    sa.func.avg(table.c.execution_time).label('avg_execution_time'),
                    (sa.func.count(sa.case((table.c.success, 1))) /
                     sa.func.count().cast(sa.Float)).label('success_rate'),
                    sa.func.count(sa.case((not table.c.success, 1))).label('error_count')
                ).where(
                    table.c.created_at >= start_date,
                    table.c.created_at <= end_date
                )

                # Apply filters
                if analysis_type:
                    query = query.where(table.c.analysis_type == analysis_type.value)

                if algorithm_name:
                    query = query.where(table.c.algorithm_name == algorithm_name)

                query = query.group_by(
                    sa.func.date_trunc('day', table.c.created_at)
                ).order_by('date')

                results = session.execute(query).fetchall()

                # Convert to DataFrame
                data = []
                for row in results:
                    data.append({
                        'date': row.date,
                        'execution_count': row.execution_count,
                        'avg_execution_time': float(row.avg_execution_time or 0),
                        'success_rate': float(row.success_rate or 0),
                        'error_count': row.error_count
                    })

                return pd.DataFrame(data)

        except Exception as e:
            self.logger.error(f"Failed to get daily performance data: {e}")
            raise

    def _analyze_metric_trend(self, data: pd.DataFrame, metric_column: str,
                             metric_name: str, period_days: int) -> TrendAnalysis:
        """Analyze trend for a specific metric"""
        try:
            if len(data) < 2:
                return TrendAnalysis(
                    metric_name=metric_name,
                    trend_direction=TrendDirection.UNKNOWN,
                    trend_magnitude=0.0,
                    confidence=0.0,
                    period_days=period_days,
                    start_value=0.0,
                    end_value=0.0,
                    change_percentage=0.0,
                    r_squared=0.0
                )

            # Prepare data for linear regression
            x = np.arange(len(data))
            y = data[metric_column].values

            # Handle missing values
            valid_mask = ~np.isnan(y)
            if np.sum(valid_mask) < 2:
                return TrendAnalysis(
                    metric_name=metric_name,
                    trend_direction=TrendDirection.UNKNOWN,
                    trend_magnitude=0.0,
                    confidence=0.0,
                    period_days=period_days,
                    start_value=float(y[0]) if len(y) > 0 else 0.0,
                    end_value=float(y[-1]) if len(y) > 0 else 0.0,
                    change_percentage=0.0,
                    r_squared=0.0
                )

            x_valid = x[valid_mask]
            y_valid = y[valid_mask]

            # Linear regression
            coeffs = np.polyfit(x_valid, y_valid, 1)
            slope, intercept = coeffs

            # Calculate R-squared
            y_pred = slope * x_valid + intercept
            ss_res = np.sum((y_valid - y_pred) ** 2)
            ss_tot = np.sum((y_valid - np.mean(y_valid)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            # Determine trend direction
            start_value = float(y_valid[0])
            end_value = float(y_valid[-1])

            # Use slope and statistical significance
            trend_magnitude = abs(slope)

            if abs(slope) < np.std(y_valid) * 0.1:  # Less than 10% of std dev
                trend_direction = TrendDirection.STABLE
            elif slope > 0:
                trend_direction = TrendDirection.IMPROVING
            else:
                trend_direction = TrendDirection.DECLINING

            # Calculate confidence based on R-squared and data points
            confidence = min(1.0, r_squared * (len(y_valid) / 30))  # More data = higher confidence

            # Calculate percentage change
            if start_value != 0:
                change_percentage = ((end_value - start_value) / start_value) * 100
            else:
                change_percentage = 0.0

            # Generate recommendations
            recommendations = self._generate_trend_recommendations(
                metric_name, trend_direction, trend_magnitude, confidence
            )

            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction=trend_direction,
                trend_magnitude=trend_magnitude,
                confidence=confidence,
                period_days=period_days,
                start_value=start_value,
                end_value=end_value,
                change_percentage=change_percentage,
                r_squared=r_squared,
                recommendations=recommendations
            )

        except Exception as e:
            self.logger.error(f"Failed to analyze trend for {metric_name}: {e}")
            raise

    def _generate_trend_recommendations(self, metric_name: str,
                                       trend_direction: TrendDirection,
                                       magnitude: float,
                                       confidence: float) -> List[str]:
        """Generate recommendations based on trend analysis"""
        recommendations = []

        if confidence < 0.3:
            recommendations.append(f"Low confidence in {metric_name} trend - need more data")
            return recommendations

        if metric_name == "Execution Time":
            if trend_direction == TrendDirection.DECLINING:  # Getting worse (higher times)
                recommendations.append("Execution times are increasing - consider optimization")
                recommendations.append("Review algorithm performance and data preprocessing")
            elif trend_direction == TrendDirection.IMPROVING:
                recommendations.append("Execution times are improving - good performance trend")
            else:
                recommendations.append("Execution times are stable")

        elif metric_name == "Success Rate":
            if trend_direction == TrendDirection.DECLINING:
                recommendations.append("Success rate is declining - investigate failure causes")
                recommendations.append("Review input data quality and algorithm parameters")
            elif trend_direction == TrendDirection.IMPROVING:
                recommendations.append("Success rate is improving - positive trend")
            else:
                recommendations.append("Success rate is stable")

        elif metric_name == "Execution Volume":
            if trend_direction == TrendDirection.IMPROVING:
                recommendations.append("Analysis volume is increasing - monitor resource usage")
            elif trend_direction == TrendDirection.DECLINING:
                recommendations.append("Analysis volume is decreasing - check system utilization")

        return recommendations

    def get_performance_summary(self, days_back: int = 7,
                               analysis_type: Optional[AnalysisType] = None) -> PerformanceMetrics:
        """Get comprehensive performance summary"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)

            # Get basic metrics
            filters = QueryFilter(
                analysis_type=analysis_type,
                start_date=start_date,
                end_date=end_date,
                success_only=False,
                limit=10000  # Large limit to get all results
            )

            results, total_count = self.result_storage.retrieve_results(filters)

            if not results:
                return PerformanceMetrics(
                    period_start=start_date,
                    period_end=end_date,
                    total_executions=0,
                    success_rate=0.0,
                    average_execution_time=0.0,
                    execution_time_trend=TrendDirection.UNKNOWN,
                    error_count=0,
                    most_common_algorithms=[],
                    performance_by_type={},
                    outliers=[]
                )

            # Calculate basic metrics
            successful_results = [r for r in results if r['success']]
            success_rate = len(successful_results) / len(results)

            execution_times = [r['execution_time'] for r in results]
            average_execution_time = np.mean(execution_times)

            error_count = len(results) - len(successful_results)

            # Algorithm frequency
            algorithm_counts = {}
            for result in results:
                alg_name = result['algorithm_name']
                algorithm_counts[alg_name] = algorithm_counts.get(alg_name, 0) + 1

            most_common_algorithms = sorted(
                algorithm_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            # Performance by type
            performance_by_type = {}
            type_groups = {}
            for result in results:
                result_type = result['analysis_type']
                if result_type not in type_groups:
                    type_groups[result_type] = []
                type_groups[result_type].append(result)

            for result_type, type_results in type_groups.items():
                type_success_rate = len([r for r in type_results if r['success']]) / len(type_results)
                type_avg_time = np.mean([r['execution_time'] for r in type_results])

                performance_by_type[result_type] = {
                    'success_rate': type_success_rate,
                    'average_execution_time': type_avg_time,
                    'count': len(type_results)
                }

            # Detect outliers (execution times > 2 std devs from mean)
            outliers = []
            if len(execution_times) > 10:
                mean_time = np.mean(execution_times)
                std_time = np.std(execution_times)
                threshold = mean_time + 2 * std_time

                for result in results:
                    if result['execution_time'] > threshold:
                        outliers.append({
                            'result_id': result['result_id'],
                            'algorithm_name': result['algorithm_name'],
                            'execution_time': result['execution_time'],
                            'created_at': result['created_at']
                        })

            # Get execution time trend
            trends = self.analyze_performance_trends(analysis_type, None, days_back)
            execution_time_trend = TrendDirection.STABLE
            for trend in trends:
                if trend.metric_name == "Execution Time":
                    execution_time_trend = trend.trend_direction
                    break

            return PerformanceMetrics(
                period_start=start_date,
                period_end=end_date,
                total_executions=len(results),
                success_rate=success_rate,
                average_execution_time=average_execution_time,
                execution_time_trend=execution_time_trend,
                error_count=error_count,
                most_common_algorithms=most_common_algorithms,
                performance_by_type=performance_by_type,
                outliers=outliers[:10]  # Limit outliers
            )

        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            raise

    def detect_anomalies(self, days_back: int = 30,
                        analysis_type: Optional[AnalysisType] = None) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)

            # Get daily data for anomaly detection
            daily_data = self._get_daily_performance_data(
                start_date, end_date, analysis_type, None
            )

            if len(daily_data) < 7:
                return []

            anomalies = []

            # Check for execution time anomalies
            exec_times = daily_data['avg_execution_time'].values
            exec_mean = np.mean(exec_times)
            exec_std = np.std(exec_times)

            for i, (_, row) in enumerate(daily_data.iterrows()):
                if row['avg_execution_time'] > exec_mean + 3 * exec_std:
                    anomalies.append({
                        'type': 'execution_time_spike',
                        'date': row['date'],
                        'value': row['avg_execution_time'],
                        'threshold': exec_mean + 3 * exec_std,
                        'severity': 'high'
                    })

                # Check for success rate drops
                if row['success_rate'] < 0.8 and row['execution_count'] > 5:
                    anomalies.append({
                        'type': 'success_rate_drop',
                        'date': row['date'],
                        'value': row['success_rate'],
                        'threshold': 0.8,
                        'severity': 'medium'
                    })

                # Check for unusual volume spikes
                if i > 0:
                    prev_count = daily_data.iloc[i-1]['execution_count']
                    if row['execution_count'] > prev_count * 3 and prev_count > 0:
                        anomalies.append({
                            'type': 'volume_spike',
                            'date': row['date'],
                            'value': row['execution_count'],
                            'previous_value': prev_count,
                            'severity': 'low'
                        })

            return sorted(anomalies, key=lambda x: x['date'], reverse=True)

        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {e}")
            raise

    def generate_performance_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'period_days': days_back,
                'summary': {},
                'trends': {},
                'anomalies': [],
                'recommendations': []
            }

            # Get performance summary
            summary = self.get_performance_summary(days_back)
            report['summary'] = {
                'total_executions': summary.total_executions,
                'success_rate': summary.success_rate,
                'average_execution_time': summary.average_execution_time,
                'error_count': summary.error_count,
                'most_common_algorithms': summary.most_common_algorithms,
                'performance_by_type': summary.performance_by_type
            }

            # Get trend analysis
            trends = self.analyze_performance_trends(days_back=days_back)
            report['trends'] = {
                trend.metric_name: {
                    'direction': trend.trend_direction.value,
                    'magnitude': trend.trend_magnitude,
                    'confidence': trend.confidence,
                    'change_percentage': trend.change_percentage,
                    'recommendations': trend.recommendations
                }
                for trend in trends
            }

            # Get anomalies
            anomalies = self.detect_anomalies(days_back)
            report['anomalies'] = anomalies

            # Generate overall recommendations
            overall_recommendations = []

            if summary.success_rate < 0.9:
                overall_recommendations.append("Success rate below 90% - investigate failure causes")

            if summary.average_execution_time > 10.0:
                overall_recommendations.append("Average execution time high - consider optimization")

            if len(anomalies) > 5:
                overall_recommendations.append("Multiple anomalies detected - system monitoring recommended")

            if not overall_recommendations:
                overall_recommendations.append("System performance within normal parameters")

            report['recommendations'] = overall_recommendations

            return report

        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            raise

# Export main components
__all__ = [
    'HistoricalTracker',
    'TrendAnalysis',
    'PerformanceMetrics',
    'TrendDirection'
]
