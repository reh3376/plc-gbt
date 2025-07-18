#!/usr/bin/env python3
"""
Phase 22.2.4: ML-Enhanced Tuning Manager
========================================

Unified manager for coordinating all ML-enhanced PID tuning methods:
- Neural network tuning coordination
- Reinforcement learning orchestration
- Transfer learning management
- Ensemble method coordination
- Performance comparison and selection

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.4 - ML-Enhanced Tuning
Methodology: AI Task Orchestrator Guide
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
import logging
from enum import Enum
import time
from datetime import datetime
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import ML tuning modules
try:
    from .neural_tuning import NeuralNetworkTuner, NeuralNetworkConfig, NeuralTuningResults
    NEURAL_AVAILABLE = True
except ImportError:
    NEURAL_AVAILABLE = False

try:
    from .reinforcement_tuning import ReinforcementTuner, RLConfig, RLTuningResults
    RL_AVAILABLE = True
except ImportError:
    RL_AVAILABLE = False

try:
    from .transfer_tuning import TransferLearningTuner, TransferConfig, TransferResults
    TRANSFER_AVAILABLE = True
except ImportError:
    TRANSFER_AVAILABLE = False

try:
    from .ensemble_tuning import EnsembleTuner, EnsembleConfig, EnsembleResults
    ENSEMBLE_AVAILABLE = True
except ImportError:
    ENSEMBLE_AVAILABLE = False

# Import algorithm base class if available
try:
    from ...algorithms import (
        AlgorithmBase, AlgorithmMetadata, AlgorithmCategory, 
        AlgorithmComplexity, registry
    )
    ALGORITHM_REGISTRY_AVAILABLE = True
except ImportError:
    ALGORITHM_REGISTRY_AVAILABLE = False
    logging.warning("⚠️ Algorithm registry not available - using standalone implementation")

logger = logging.getLogger(__name__)

class MLMethodType(Enum):
    """ML method types"""
    NEURAL_NETWORK = "neural_network"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    TRANSFER_LEARNING = "transfer_learning"
    ENSEMBLE = "ensemble"
    AUTO_SELECT = "auto_select"

class SelectionCriteria(Enum):
    """Method selection criteria"""
    PERFORMANCE = "performance"
    SPEED = "speed"
    ROBUSTNESS = "robustness"
    DATA_EFFICIENCY = "data_efficiency"
    INTERPRETABILITY = "interpretability"
    UNCERTAINTY = "uncertainty"

@dataclass
class MLManagerConfig:
    """ML manager configuration"""
    # Method selection
    preferred_method: MLMethodType = MLMethodType.AUTO_SELECT
    selection_criteria: SelectionCriteria = SelectionCriteria.PERFORMANCE
    fallback_method: MLMethodType = MLMethodType.NEURAL_NETWORK
    
    # Parallel execution
    enable_parallel: bool = True
    max_workers: int = 4
    timeout_seconds: float = 300.0
    
    # Method configurations
    neural_config: Optional[NeuralNetworkConfig] = None
    rl_config: Optional[RLConfig] = None
    transfer_config: Optional[TransferConfig] = None
    ensemble_config: Optional[EnsembleConfig] = None
    
    # Performance thresholds
    min_performance_score: float = 0.7
    max_execution_time: float = 120.0
    confidence_threshold: float = 0.8
    
    # Data requirements
    min_data_points: int = 50
    data_quality_threshold: float = 0.8
    
    # Comparison and validation
    enable_cross_validation: bool = True
    validation_splits: int = 5
    enable_benchmarking: bool = True
    
    # Auto-selection parameters
    performance_weight: float = 0.4
    speed_weight: float = 0.2
    robustness_weight: float = 0.2
    efficiency_weight: float = 0.2

@dataclass
class MethodResult:
    """Individual method result"""
    method_type: MLMethodType
    success: bool
    parameters: Optional[Dict[str, float]]
    performance_metrics: Dict[str, float]
    execution_time: float
    confidence_scores: Dict[str, float]
    error_message: Optional[str] = None
    detailed_result: Optional[Any] = None

@dataclass
class MLManagerResults:
    """ML manager comprehensive results"""
    selected_method: MLMethodType
    selection_reasoning: str
    
    # Best result
    best_parameters: Dict[str, float]
    best_performance: Dict[str, float]
    best_confidence: Dict[str, float]
    
    # All method results
    method_results: Dict[str, MethodResult]
    
    # Comparison analysis
    performance_comparison: Dict[str, Dict[str, float]]
    method_rankings: Dict[SelectionCriteria, List[str]]
    
    # Execution statistics
    total_execution_time: float
    successful_methods: List[str]
    failed_methods: List[str]
    
    # Recommendations
    recommendations: Dict[str, str]
    uncertainty_analysis: Dict[str, float]
    
    status: str

class MLTuningManager:
    """Manager for all ML-enhanced tuning methods"""
    
    def __init__(self, configuration: Optional[MLManagerConfig] = None):
        self.config = configuration or MLManagerConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize available methods
        self.available_methods = self._check_available_methods()
        self.method_instances = {}
        
        # Performance history for auto-selection
        self.performance_history = {}
        
        # Initialize method instances
        self._initialize_methods()
        
        self.logger.info(f"Initialized ML manager with {len(self.available_methods)} methods")
    
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute ML-enhanced PID tuning with optimal method selection"""
        try:
            start_time = time.time()
            
            # Validate input data
            if not self._validate_input_data(data):
                return {
                    'success': False,
                    'error': 'Invalid input data for ML tuning',
                    'method': 'ml_enhanced_tuning'
                }
            
            # Determine which methods to run
            methods_to_run = self._determine_methods_to_run(data, kwargs)
            
            if not methods_to_run:
                return {
                    'success': False,
                    'error': 'No ML methods available or suitable',
                    'method': 'ml_enhanced_tuning'
                }
            
            # Execute methods
            if self.config.enable_parallel and len(methods_to_run) > 1:
                method_results = self._execute_methods_parallel(methods_to_run, data, kwargs)
            else:
                method_results = self._execute_methods_sequential(methods_to_run, data, kwargs)
            
            # Select best method and result
            best_method, selection_reasoning = self._select_best_method(method_results, data)
            
            # Perform comparison analysis
            comparison_analysis = self._perform_comparison_analysis(method_results)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(method_results, data)
            
            # Calculate uncertainty analysis
            uncertainty_analysis = self._analyze_uncertainty(method_results)
            
            total_time = time.time() - start_time
            
            # Get best result details
            best_result = method_results.get(best_method.value)
            if best_result and best_result.success:
                best_parameters = best_result.parameters
                best_performance = best_result.performance_metrics
                best_confidence = best_result.confidence_scores
            else:
                # Fallback to any successful result
                successful_results = [r for r in method_results.values() if r.success]
                if successful_results:
                    best_result = successful_results[0]
                    best_parameters = best_result.parameters
                    best_performance = best_result.performance_metrics
                    best_confidence = best_result.confidence_scores
                else:
                    best_parameters = {'Kp': 1.0, 'Ti': 10.0, 'Td': 0.0}
                    best_performance = {'score': 0.0}
                    best_confidence = {'Kp': 0.0, 'Ti': 0.0, 'Td': 0.0}
            
            # Create comprehensive results
            result = MLManagerResults(
                selected_method=best_method,
                selection_reasoning=selection_reasoning,
                best_parameters=best_parameters,
                best_performance=best_performance,
                best_confidence=best_confidence,
                method_results=method_results,
                performance_comparison=comparison_analysis['performance'],
                method_rankings=comparison_analysis['rankings'],
                total_execution_time=total_time,
                successful_methods=[name for name, result in method_results.items() if result.success],
                failed_methods=[name for name, result in method_results.items() if not result.success],
                recommendations=recommendations,
                uncertainty_analysis=uncertainty_analysis,
                status="success"
            )
            
            # Update performance history for future auto-selection
            self._update_performance_history(method_results, data)
            
            return {
                'success': True,
                'result': result,
                'method': 'ml_enhanced_tuning'
            }
            
        except Exception as e:
            self.logger.error(f"ML manager execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'ml_enhanced_tuning'
            }
    
    def _check_available_methods(self) -> List[MLMethodType]:
        """Check which ML methods are available"""
        
        available = []
        
        if NEURAL_AVAILABLE:
            available.append(MLMethodType.NEURAL_NETWORK)
            self.logger.info("✅ Neural network tuning available")
        else:
            self.logger.warning("❌ Neural network tuning not available")
        
        if RL_AVAILABLE:
            available.append(MLMethodType.REINFORCEMENT_LEARNING)
            self.logger.info("✅ Reinforcement learning tuning available")
        else:
            self.logger.warning("❌ Reinforcement learning tuning not available")
        
        if TRANSFER_AVAILABLE:
            available.append(MLMethodType.TRANSFER_LEARNING)
            self.logger.info("✅ Transfer learning tuning available")
        else:
            self.logger.warning("❌ Transfer learning tuning not available")
        
        if ENSEMBLE_AVAILABLE:
            available.append(MLMethodType.ENSEMBLE)
            self.logger.info("✅ Ensemble tuning available")
        else:
            self.logger.warning("❌ Ensemble tuning not available")
        
        return available
    
    def _initialize_methods(self):
        """Initialize method instances"""
        
        try:
            if MLMethodType.NEURAL_NETWORK in self.available_methods:
                self.method_instances[MLMethodType.NEURAL_NETWORK] = NeuralNetworkTuner(
                    self.config.neural_config
                )
        except Exception as e:
            self.logger.warning(f"Failed to initialize neural network tuner: {e}")
        
        try:
            if MLMethodType.REINFORCEMENT_LEARNING in self.available_methods:
                self.method_instances[MLMethodType.REINFORCEMENT_LEARNING] = ReinforcementTuner(
                    self.config.rl_config
                )
        except Exception as e:
            self.logger.warning(f"Failed to initialize RL tuner: {e}")
        
        try:
            if MLMethodType.TRANSFER_LEARNING in self.available_methods:
                self.method_instances[MLMethodType.TRANSFER_LEARNING] = TransferLearningTuner(
                    self.config.transfer_config
                )
        except Exception as e:
            self.logger.warning(f"Failed to initialize transfer learning tuner: {e}")
        
        try:
            if MLMethodType.ENSEMBLE in self.available_methods:
                self.method_instances[MLMethodType.ENSEMBLE] = EnsembleTuner(
                    self.config.ensemble_config
                )
        except Exception as e:
            self.logger.warning(f"Failed to initialize ensemble tuner: {e}")
    
    def _validate_input_data(self, data: Dict[str, Any]) -> bool:
        """Validate input data quality and completeness"""
        
        # Check required fields
        required_fields = ['process_gain', 'time_constant', 'dead_time']
        for field in required_fields:
            if field not in data:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Check data ranges
        if data.get('process_gain', 0) <= 0:
            self.logger.error("Process gain must be positive")
            return False
        
        if data.get('time_constant', 0) <= 0:
            self.logger.error("Time constant must be positive")
            return False
        
        if data.get('dead_time', 0) < 0:
            self.logger.error("Dead time must be non-negative")
            return False
        
        return True
    
    def _determine_methods_to_run(self, data: Dict[str, Any], kwargs: Dict[str, Any]) -> List[MLMethodType]:
        """Determine which methods to run based on configuration and data"""
        
        if self.config.preferred_method != MLMethodType.AUTO_SELECT:
            # Use specific method if available
            if self.config.preferred_method in self.available_methods:
                return [self.config.preferred_method]
            else:
                self.logger.warning(f"Preferred method {self.config.preferred_method} not available")
        
        # Auto-selection based on data characteristics and criteria
        suitable_methods = []
        
        # Check data requirements for each method
        data_size = data.get('data_points', 100)
        has_historical_data = 'historical_data' in data
        has_similar_processes = data.get('similar_processes_available', False)
        
        # Neural network: good for large datasets
        if (MLMethodType.NEURAL_NETWORK in self.available_methods and 
            data_size >= self.config.min_data_points):
            suitable_methods.append(MLMethodType.NEURAL_NETWORK)
        
        # Transfer learning: good when similar processes exist
        if (MLMethodType.TRANSFER_LEARNING in self.available_methods and 
            has_similar_processes):
            suitable_methods.append(MLMethodType.TRANSFER_LEARNING)
        
        # Reinforcement learning: good for online optimization
        if (MLMethodType.REINFORCEMENT_LEARNING in self.available_methods and 
            data.get('enable_online_learning', False)):
            suitable_methods.append(MLMethodType.REINFORCEMENT_LEARNING)
        
        # Ensemble: good when multiple methods are available
        if (MLMethodType.ENSEMBLE in self.available_methods and 
            len(self.available_methods) > 1):
            suitable_methods.append(MLMethodType.ENSEMBLE)
        
        # If no methods are suitable, use all available
        if not suitable_methods:
            suitable_methods = self.available_methods.copy()
        
        # Limit methods based on execution time constraints
        if self.config.max_execution_time < 60.0:
            # Prefer faster methods for tight time constraints
            fast_methods = [MLMethodType.NEURAL_NETWORK, MLMethodType.TRANSFER_LEARNING]
            suitable_methods = [m for m in suitable_methods if m in fast_methods]
        
        return suitable_methods
    
    def _execute_methods_parallel(self, methods: List[MLMethodType], 
                                 data: Dict[str, Any], kwargs: Dict[str, Any]) -> Dict[str, MethodResult]:
        """Execute methods in parallel"""
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all method executions
            future_to_method = {}
            for method in methods:
                if method in self.method_instances:
                    future = executor.submit(
                        self._execute_single_method, 
                        method, data, kwargs
                    )
                    future_to_method[future] = method
            
            # Collect results as they complete
            for future in as_completed(future_to_method, timeout=self.config.timeout_seconds):
                method = future_to_method[future]
                try:
                    result = future.result()
                    results[method.value] = result
                except Exception as e:
                    self.logger.error(f"Method {method} failed: {e}")
                    results[method.value] = MethodResult(
                        method_type=method,
                        success=False,
                        parameters=None,
                        performance_metrics={},
                        execution_time=0.0,
                        confidence_scores={},
                        error_message=str(e)
                    )
        
        return results
    
    def _execute_methods_sequential(self, methods: List[MLMethodType], 
                                   data: Dict[str, Any], kwargs: Dict[str, Any]) -> Dict[str, MethodResult]:
        """Execute methods sequentially"""
        
        results = {}
        
        for method in methods:
            if method in self.method_instances:
                try:
                    result = self._execute_single_method(method, data, kwargs)
                    results[method.value] = result
                except Exception as e:
                    self.logger.error(f"Method {method} failed: {e}")
                    results[method.value] = MethodResult(
                        method_type=method,
                        success=False,
                        parameters=None,
                        performance_metrics={},
                        execution_time=0.0,
                        confidence_scores={},
                        error_message=str(e)
                    )
        
        return results
    
    def _execute_single_method(self, method: MLMethodType, 
                              data: Dict[str, Any], kwargs: Dict[str, Any]) -> MethodResult:
        """Execute a single ML method"""
        
        start_time = time.time()
        
        try:
            tuner = self.method_instances[method]
            result = tuner.execute(data, **kwargs)
            execution_time = time.time() - start_time
            
            if result.get('success', False):
                # Extract results based on method type
                detailed_result = result.get('result')
                
                if hasattr(detailed_result, 'predicted_parameters'):
                    parameters = detailed_result.predicted_parameters
                elif hasattr(detailed_result, 'optimized_parameters'):
                    parameters = detailed_result.optimized_parameters
                elif hasattr(detailed_result, 'transferred_parameters'):
                    parameters = detailed_result.transferred_parameters
                elif hasattr(detailed_result, 'ensemble_parameters'):
                    parameters = detailed_result.ensemble_parameters
                else:
                    parameters = {'Kp': 1.0, 'Ti': 10.0, 'Td': 0.0}
                
                # Extract performance metrics
                if hasattr(detailed_result, 'model_performance'):
                    performance = detailed_result.model_performance
                elif hasattr(detailed_result, 'performance_metrics'):
                    performance = detailed_result.performance_metrics
                elif hasattr(detailed_result, 'eval_performance'):
                    performance = detailed_result.eval_performance
                elif hasattr(detailed_result, 'ensemble_performance'):
                    performance = detailed_result.ensemble_performance
                else:
                    performance = {'score': 0.8}
                
                # Extract confidence scores
                if hasattr(detailed_result, 'confidence_scores'):
                    confidence = detailed_result.confidence_scores
                elif hasattr(detailed_result, 'combination_confidence'):
                    confidence = detailed_result.combination_confidence
                else:
                    confidence = {param: 0.8 for param in parameters.keys()}
                
                return MethodResult(
                    method_type=method,
                    success=True,
                    parameters=parameters,
                    performance_metrics=performance,
                    execution_time=execution_time,
                    confidence_scores=confidence,
                    detailed_result=detailed_result
                )
            else:
                return MethodResult(
                    method_type=method,
                    success=False,
                    parameters=None,
                    performance_metrics={},
                    execution_time=execution_time,
                    confidence_scores={},
                    error_message=result.get('error', 'Unknown error')
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return MethodResult(
                method_type=method,
                success=False,
                parameters=None,
                performance_metrics={},
                execution_time=execution_time,
                confidence_scores={},
                error_message=str(e)
            )
    
    def _select_best_method(self, results: Dict[str, MethodResult], 
                           data: Dict[str, Any]) -> Tuple[MLMethodType, str]:
        """Select the best method based on configuration criteria"""
        
        successful_results = {name: result for name, result in results.items() if result.success}
        
        if not successful_results:
            # Return fallback method
            return self.config.fallback_method, "No successful methods - using fallback"
        
        if len(successful_results) == 1:
            # Only one successful method
            method_name = list(successful_results.keys())[0]
            return MLMethodType(method_name), "Only one successful method"
        
        # Score methods based on selection criteria
        method_scores = {}
        
        for method_name, result in successful_results.items():
            score = 0.0
            
            # Performance score
            performance = result.performance_metrics.get('score', 
                         result.performance_metrics.get('performance_score', 0.5))
            score += self.config.performance_weight * performance
            
            # Speed score (inverse of execution time)
            speed_score = 1.0 / (1.0 + result.execution_time / 60.0)  # Normalize to minutes
            score += self.config.speed_weight * speed_score
            
            # Robustness score (based on confidence)
            confidence_avg = np.mean(list(result.confidence_scores.values()))
            score += self.config.robustness_weight * confidence_avg
            
            # Efficiency score (performance per time)
            efficiency = performance / max(result.execution_time, 1.0)
            efficiency_norm = min(1.0, efficiency / 0.1)  # Normalize
            score += self.config.efficiency_weight * efficiency_norm
            
            method_scores[method_name] = score
        
        # Select method with highest score
        best_method_name = max(method_scores, key=method_scores.get)
        best_score = method_scores[best_method_name]
        
        reasoning = f"Selected {best_method_name} with score {best_score:.3f} based on weighted criteria"
        
        return MLMethodType(best_method_name), reasoning
    
    def _perform_comparison_analysis(self, results: Dict[str, MethodResult]) -> Dict[str, Any]:
        """Perform comprehensive comparison analysis"""
        
        # Performance comparison
        performance_comparison = {}
        for method_name, result in results.items():
            if result.success:
                performance_comparison[method_name] = {
                    'score': result.performance_metrics.get('score', 0.0),
                    'execution_time': result.execution_time,
                    'confidence': np.mean(list(result.confidence_scores.values())),
                    'parameters': result.parameters
                }
        
        # Method rankings by different criteria
        rankings = {}
        
        # Performance ranking
        perf_ranking = sorted(performance_comparison.items(), 
                             key=lambda x: x[1]['score'], reverse=True)
        rankings[SelectionCriteria.PERFORMANCE] = [item[0] for item in perf_ranking]
        
        # Speed ranking
        speed_ranking = sorted(performance_comparison.items(), 
                              key=lambda x: x[1]['execution_time'])
        rankings[SelectionCriteria.SPEED] = [item[0] for item in speed_ranking]
        
        # Robustness ranking
        robust_ranking = sorted(performance_comparison.items(), 
                               key=lambda x: x[1]['confidence'], reverse=True)
        rankings[SelectionCriteria.ROBUSTNESS] = [item[0] for item in robust_ranking]
        
        return {
            'performance': performance_comparison,
            'rankings': rankings
        }
    
    def _generate_recommendations(self, results: Dict[str, MethodResult], 
                                 data: Dict[str, Any]) -> Dict[str, str]:
        """Generate recommendations based on results"""
        
        recommendations = {}
        
        successful_methods = [name for name, result in results.items() if result.success]
        failed_methods = [name for name, result in results.items() if not result.success]
        
        # General recommendations
        if len(successful_methods) > 1:
            recommendations['ensemble'] = "Consider using ensemble methods to combine multiple successful approaches"
        
        if len(failed_methods) > 0:
            recommendations['troubleshooting'] = f"Methods {failed_methods} failed - check data quality and configuration"
        
        # Specific method recommendations
        for method_name, result in results.items():
            if result.success:
                if result.execution_time > 60.0:
                    recommendations[f'{method_name}_speed'] = "Consider reducing model complexity for faster execution"
                
                confidence_avg = np.mean(list(result.confidence_scores.values()))
                if confidence_avg < 0.7:
                    recommendations[f'{method_name}_confidence'] = "Low confidence - consider more training data or different approach"
        
        return recommendations
    
    def _analyze_uncertainty(self, results: Dict[str, MethodResult]) -> Dict[str, float]:
        """Analyze prediction uncertainty across methods"""
        
        uncertainty_analysis = {}
        
        # Collect parameter predictions
        param_predictions = {'Kp': [], 'Ti': [], 'Td': []}
        
        for result in results.values():
            if result.success and result.parameters:
                for param in param_predictions.keys():
                    if param in result.parameters:
                        param_predictions[param].append(result.parameters[param])
        
        # Calculate uncertainty metrics
        for param, values in param_predictions.items():
            if len(values) > 1:
                uncertainty_analysis[f'{param}_std'] = float(np.std(values))
                uncertainty_analysis[f'{param}_cv'] = float(np.std(values) / max(np.mean(values), 1e-6))
            else:
                uncertainty_analysis[f'{param}_std'] = 0.0
                uncertainty_analysis[f'{param}_cv'] = 0.0
        
        # Overall uncertainty
        all_stds = [uncertainty_analysis[k] for k in uncertainty_analysis.keys() if '_std' in k]
        uncertainty_analysis['overall_uncertainty'] = float(np.mean(all_stds)) if all_stds else 0.0
        
        return uncertainty_analysis
    
    def _update_performance_history(self, results: Dict[str, MethodResult], data: Dict[str, Any]):
        """Update performance history for future auto-selection"""
        
        process_type = data.get('process_type', 'general')
        
        if process_type not in self.performance_history:
            self.performance_history[process_type] = {}
        
        for method_name, result in results.items():
            if result.success:
                if method_name not in self.performance_history[process_type]:
                    self.performance_history[process_type][method_name] = []
                
                performance_record = {
                    'score': result.performance_metrics.get('score', 0.0),
                    'execution_time': result.execution_time,
                    'confidence': np.mean(list(result.confidence_scores.values())),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.performance_history[process_type][method_name].append(performance_record)
                
                # Keep only recent history
                max_history = 100
                if len(self.performance_history[process_type][method_name]) > max_history:
                    self.performance_history[process_type][method_name] = \
                        self.performance_history[process_type][method_name][-max_history:]

# Register algorithm if registry is available
if ALGORITHM_REGISTRY_AVAILABLE:
    
    @registry.register(
        category=AlgorithmCategory.TUNING_CALCULATION,
        complexity=AlgorithmComplexity.EXTENSIVE,
        metadata=AlgorithmMetadata(
            name="ML-Enhanced Tuning Manager",
            description="Unified manager for all ML-enhanced PID tuning methods",
            version="1.0.0",
            author="PLC-GPT Team",
            tags=["ml_manager", "auto_selection", "parallel_execution", "performance_comparison"]
        )
    )
    class RegisteredMLManager(MLTuningManager):
        pass

# Export classes and functions
__all__ = [
    'MLTuningManager',
    'MLManagerConfig',
    'MethodResult',
    'MLManagerResults',
    'MLMethodType',
    'SelectionCriteria'
] 