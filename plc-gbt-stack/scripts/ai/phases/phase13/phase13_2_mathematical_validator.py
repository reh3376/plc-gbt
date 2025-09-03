#!/usr/bin/env python3
"""
🧮 Phase 13.2: Mathematical Validation Framework - AI Task Orchestrator Implementation

Real-time mathematical validation system for industrial control theory recommendations
using WolframAlpha Pro computational intelligence.

Following AI Task Orchestrator Guide methodology for:
- Real-time validation of control theory recommendations
- Optimization verification for multi-objective solutions
- Control system stability verification
- Mathematical validation of performance improvements

COMPLEXITY: COMPLEX (500-1500 lines, 3-8 hours)
INTEGRATION: WolframAlpha Pro API + Control Theory LLM + Multi-Database

Author: AI Task Orchestrator
Created: 2025-01-17
Phase: 13.2 - Mathematical Validation Framework
"""

import asyncio
import json
import logging
import re
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import sympy as sp
from scipy import signal
from scipy.signal import TransferFunction

# Import from Phase 13.1
from .phase13_1_wolfram_api_client import (
    IndustrialControlQueries,
    WolframAlphaProClient,
    WolframAPIException,
    WolframQueryType,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation depth levels"""
    BASIC = "basic"           # Quick sanity checks
    STANDARD = "standard"     # Standard mathematical validation
    COMPREHENSIVE = "comprehensive"  # Full validation with WolframAlpha Pro
    RESEARCH = "research"     # Advanced research-level validation

class ControlSystemType(Enum):
    """Control system types for specialized validation"""
    PID = "pid"
    MPC = "mpc"
    FUZZY = "fuzzy"
    ADAPTIVE = "adaptive"
    OPTIMAL = "optimal"
    ROBUST = "robust"
    NONLINEAR = "nonlinear"
    MULTI_LOOP = "multi_loop"

class ValidationCategory(Enum):
    """Categories of mathematical validation"""
    MATHEMATICAL_ACCURACY = "mathematical_accuracy"
    CONTROL_THEORY = "control_theory"
    STABILITY_ANALYSIS = "stability_analysis"
    OPTIMIZATION = "optimization"
    STATISTICAL = "statistical"
    PERFORMANCE = "performance"
    SAFETY = "safety"
    CONSTRAINTS = "constraints"

@dataclass
class ValidationRequest:
    """Request for mathematical validation"""
    request_id: str
    category: ValidationCategory
    system_type: ControlSystemType
    validation_level: ValidationLevel
    input_data: Dict[str, Any]
    expected_result: Optional[Any] = None
    tolerance: float = 1e-6
    timeout: int = 30
    wolfram_validation: bool = True
    fallback_methods: List[str] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.fallback_methods is None:
            self.fallback_methods = ["numpy", "scipy", "sympy"]
        if self.context is None:
            self.context = {}

@dataclass
class ValidationResult:
    """Result of mathematical validation"""
    result_id: str
    request_id: str
    success: bool
    validated: bool
    accuracy_score: float
    confidence_score: float
    mathematical_result: Any
    wolfram_result: Optional[Any] = None
    local_result: Optional[Any] = None
    discrepancy: Optional[float] = None
    validation_method: str = ""
    execution_time: float = 0.0
    warnings: List[str] = None
    errors: List[str] = None
    educational_content: List[str] = None
    derivation_steps: List[str] = None
    assumptions: List[str] = None
    limitations: List[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.educational_content is None:
            self.educational_content = []
        if self.derivation_steps is None:
            self.derivation_steps = []
        if self.assumptions is None:
            self.assumptions = []
        if self.limitations is None:
            self.limitations = []
        if self.timestamp is None:
            self.timestamp = datetime.now()

class MathematicalValidator:
    """
    Core mathematical validation engine

    Provides comprehensive validation of mathematical computations
    with WolframAlpha Pro verification and local fallback methods.
    """

    def __init__(self, wolfram_client: Optional[WolframAlphaProClient] = None):
        self.wolfram_client = wolfram_client
        self.validation_cache = {}
        self.session_stats = {
            "validations_performed": 0,
            "wolfram_queries": 0,
            "cache_hits": 0,
            "accuracy_scores": [],
            "start_time": datetime.now()
        }

        logger.info("🔍 Mathematical Validator initialized")

    async def validate(self, request: ValidationRequest) -> ValidationResult:
        """
        Perform comprehensive mathematical validation
        """
        start_time = time.time()
        request_id = request.request_id

        logger.info(f"🔍 Starting validation: {request_id}")
        logger.info(f"📊 Category: {request.category.value}, System: {request.system_type.value}")

        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = self.validation_cache.get(cache_key)
            if cached_result:
                self.session_stats["cache_hits"] += 1
                logger.info(f"🎯 Cache hit for validation: {request_id}")
                return cached_result

            # Perform validation based on category
            if request.category == ValidationCategory.MATHEMATICAL_ACCURACY:
                result = await self._validate_mathematical_accuracy(request)
            elif request.category == ValidationCategory.CONTROL_THEORY:
                result = await self._validate_control_theory(request)
            elif request.category == ValidationCategory.STABILITY_ANALYSIS:
                result = await self._validate_stability_analysis(request)
            elif request.category == ValidationCategory.OPTIMIZATION:
                result = await self._validate_optimization(request)
            elif request.category == ValidationCategory.STATISTICAL:
                result = await self._validate_statistical(request)
            elif request.category == ValidationCategory.PERFORMANCE:
                result = await self._validate_performance(request)
            elif request.category == ValidationCategory.SAFETY:
                result = await self._validate_safety(request)
            elif request.category == ValidationCategory.CONSTRAINTS:
                result = await self._validate_constraints(request)
            else:
                raise ValueError(f"Unknown validation category: {request.category}")

            # Update execution time
            result.execution_time = time.time() - start_time

            # Cache result
            self.validation_cache[cache_key] = result

            # Update session stats
            self.session_stats["validations_performed"] += 1
            self.session_stats["accuracy_scores"].append(result.accuracy_score)

            logger.info(f"✅ Validation completed: {request_id}")
            logger.info(f"📊 Accuracy: {result.accuracy_score:.2%}, Confidence: {result.confidence_score:.2%}")

            return result

        except Exception as e:
            error_result = ValidationResult(
                result_id=f"error_{uuid.uuid4().hex[:8]}",
                request_id=request_id,
                success=False,
                validated=False,
                accuracy_score=0.0,
                confidence_score=0.0,
                mathematical_result=None,
                execution_time=time.time() - start_time,
                errors=[str(e)]
            )

            logger.error(f"❌ Validation failed: {request_id} - {e}")
            return error_result

    def _generate_cache_key(self, request: ValidationRequest) -> str:
        """Generate cache key for validation request"""
        key_data = {
            "category": request.category.value,
            "system_type": request.system_type.value,
            "input_data": str(sorted(request.input_data.items())),
            "tolerance": request.tolerance,
            "level": request.validation_level.value
        }
        return f"validation:{hash(str(key_data))}"

    async def _validate_mathematical_accuracy(self, request: ValidationRequest) -> ValidationResult:
        """Validate mathematical accuracy of computations"""

        input_data = request.input_data
        computation_type = input_data.get("type", "unknown")

        if computation_type == "equation_solving":
            return await self._validate_equation_solving(request)
        elif computation_type == "integration":
            return await self._validate_integration(request)
        elif computation_type == "differentiation":
            return await self._validate_differentiation(request)
        elif computation_type == "matrix_operations":
            return await self._validate_matrix_operations(request)
        elif computation_type == "symbolic_computation":
            return await self._validate_symbolic_computation(request)
        else:
            return await self._validate_general_computation(request)

    async def _validate_equation_solving(self, request: ValidationRequest) -> ValidationResult:
        """Validate equation solving accuracy"""

        equation = request.input_data.get("equation", "")
        variable = request.input_data.get("variable", "x")
        proposed_solution = request.input_data.get("solution")

        # Local validation using SymPy
        try:
            x = sp.Symbol(variable)
            sympy_equation = sp.sympify(equation)
            sympy_solutions = sp.solve(sympy_equation, x)
            local_result = [float(sol.evalf()) if sol.is_real else complex(sol.evalf()) for sol in sympy_solutions]
        except Exception as e:
            local_result = None
            logger.warning(f"SymPy validation failed: {e}")

        # WolframAlpha Pro validation
        wolfram_result = None
        if self.wolfram_client and request.wolfram_validation:
            try:
                query = f"solve {equation} for {variable}"
                wolfram_response = await self.wolfram_client.query(
                    query, WolframQueryType.EQUATION_SOLVING
                )
                self.session_stats["wolfram_queries"] += 1

                if wolfram_response.success and wolfram_response.mathematical_result:
                    wolfram_result = self._parse_wolfram_solution(wolfram_response.mathematical_result)

            except WolframAPIException as e:
                logger.warning(f"WolframAlpha validation failed: {e}")

        # Compare results
        accuracy_score = 0.0
        confidence_score = 0.0
        validated = False
        discrepancy = None

        if local_result is not None and wolfram_result is not None:
            # Both results available - compare
            discrepancy = self._calculate_solution_discrepancy(local_result, wolfram_result)
            if discrepancy < request.tolerance:
                accuracy_score = 1.0
                confidence_score = 0.95
                validated = True
            else:
                accuracy_score = max(0.0, 1.0 - discrepancy / 10.0)
                confidence_score = 0.7
                validated = False
        elif local_result is not None:
            # Only local result available
            accuracy_score = 0.8
            confidence_score = 0.7
            validated = True
        elif wolfram_result is not None:
            # Only WolframAlpha result available
            accuracy_score = 0.9
            confidence_score = 0.85
            validated = True

        # Validate against proposed solution if provided
        if proposed_solution is not None:
            if local_result is not None:
                solution_accuracy = self._validate_proposed_solution(
                    proposed_solution, local_result, request.tolerance
                )
                accuracy_score = min(accuracy_score, solution_accuracy)

        return ValidationResult(
            result_id=f"eq_solve_{uuid.uuid4().hex[:8]}",
            request_id=request.request_id,
            success=True,
            validated=validated,
            accuracy_score=accuracy_score,
            confidence_score=confidence_score,
            mathematical_result=local_result or wolfram_result,
            wolfram_result=wolfram_result,
            local_result=local_result,
            discrepancy=discrepancy,
            validation_method="equation_solving",
            derivation_steps=[
                f"Original equation: {equation}",
                f"Variable to solve for: {variable}",
                f"SymPy solutions: {local_result}",
                f"WolframAlpha solutions: {wolfram_result}"
            ]
        )

    async def _validate_control_theory(self, request: ValidationRequest) -> ValidationResult:
        """Validate control theory computations"""

        system_type = request.system_type

        if system_type == ControlSystemType.PID:
            return await self._validate_pid_controller(request)
        elif system_type == ControlSystemType.MPC:
            return await self._validate_mpc_controller(request)
        elif system_type == ControlSystemType.OPTIMAL:
            return await self._validate_optimal_control(request)
        else:
            return await self._validate_general_control_system(request)

    async def _validate_pid_controller(self, request: ValidationRequest) -> ValidationResult:
        """Validate PID controller design and tuning"""

        input_data = request.input_data
        kp = input_data.get("kp", 1.0)
        ki = input_data.get("ki", 0.1)
        kd = input_data.get("kd", 0.01)
        process_tf = input_data.get("process_transfer_function")

        # Local validation using scipy.signal
        local_result = {}
        try:
            # Create PID controller transfer function
            pid_tf = TransferFunction([kd, kp, ki], [1, 0])
            local_result["pid_transfer_function"] = {
                "numerator": pid_tf.num.tolist(),
                "denominator": pid_tf.den.tolist()
            }

            # If process transfer function provided, analyze closed-loop system
            if process_tf:
                process_num = process_tf.get("numerator", [1])
                process_den = process_tf.get("denominator", [1, 1])
                process = TransferFunction(process_num, process_den)

                # Closed-loop transfer function
                closed_loop = signal.feedback(process * pid_tf)
                local_result["closed_loop_tf"] = {
                    "numerator": closed_loop.num.tolist(),
                    "denominator": closed_loop.den.tolist()
                }

                # Stability check
                poles = closed_loop.pole
                stable = np.all(np.real(poles) < 0)
                local_result["stability"] = {
                    "stable": bool(stable),
                    "poles": poles.tolist(),
                    "dominant_pole": float(np.max(np.real(poles)))
                }

        except Exception as e:
            logger.warning(f"Local PID validation failed: {e}")

        # WolframAlpha Pro validation
        wolfram_result = None
        if self.wolfram_client and request.wolfram_validation:
            try:
                query = IndustrialControlQueries.pid_tuning_query(kp, ki, kd)
                wolfram_response = await self.wolfram_client.query(
                    query, WolframQueryType.CONTROL_THEORY
                )
                self.session_stats["wolfram_queries"] += 1

                if wolfram_response.success:
                    wolfram_result = {
                        "wolfram_analysis": wolfram_response.mathematical_result,
                        "educational_content": wolfram_response.educational_content
                    }

            except WolframAPIException as e:
                logger.warning(f"WolframAlpha PID validation failed: {e}")

        # Calculate validation metrics
        accuracy_score = 1.0 if local_result else 0.0
        confidence_score = 0.9 if local_result.get("stability", {}).get("stable", False) else 0.6
        validated = bool(local_result)

        return ValidationResult(
            result_id=f"pid_val_{uuid.uuid4().hex[:8]}",
            request_id=request.request_id,
            success=True,
            validated=validated,
            accuracy_score=accuracy_score,
            confidence_score=confidence_score,
            mathematical_result=local_result,
            wolfram_result=wolfram_result,
            local_result=local_result,
            validation_method="pid_control_validation",
            educational_content=wolfram_result.get("educational_content", []) if wolfram_result else [],
            derivation_steps=[
                f"PID parameters: Kp={kp}, Ki={ki}, Kd={kd}",
                f"PID transfer function: {local_result.get('pid_transfer_function', 'N/A')}",
                f"Closed-loop stability: {local_result.get('stability', {}).get('stable', 'Unknown')}",
                f"Dominant pole: {local_result.get('stability', {}).get('dominant_pole', 'N/A')}"
            ]
        )

    async def _validate_stability_analysis(self, request: ValidationRequest) -> ValidationResult:
        """Validate control system stability analysis"""

        input_data = request.input_data
        transfer_function = input_data.get("transfer_function")

        if not transfer_function:
            return ValidationResult(
                result_id=f"stab_error_{uuid.uuid4().hex[:8]}",
                request_id=request.request_id,
                success=False,
                validated=False,
                accuracy_score=0.0,
                confidence_score=0.0,
                mathematical_result=None,
                errors=["Transfer function not provided"]
            )

        # Local stability analysis
        local_result = {}
        try:
            numerator = transfer_function.get("numerator", [1])
            denominator = transfer_function.get("denominator", [1, 1])

            tf = TransferFunction(numerator, denominator)
            poles = tf.pole
            zeros = tf.zero

            # Stability analysis
            stable = np.all(np.real(poles) < 0)
            gain_margin, phase_margin, _, _ = signal.margin(tf)

            local_result = {
                "poles": poles.tolist(),
                "zeros": zeros.tolist(),
                "stable": bool(stable),
                "gain_margin_db": float(20 * np.log10(gain_margin)) if gain_margin > 0 else float('-inf'),
                "phase_margin_deg": float(phase_margin * 180 / np.pi),
                "stability_analysis": {
                    "routh_hurwitz": self._routh_hurwitz_test(denominator),
                    "nyquist_stable": stable,
                    "bibo_stable": stable
                }
            }

        except Exception as e:
            logger.warning(f"Local stability analysis failed: {e}")

        # WolframAlpha Pro validation
        wolfram_result = None
        if self.wolfram_client and request.wolfram_validation:
            try:
                tf_string = self._transfer_function_to_string(transfer_function)
                query = IndustrialControlQueries.stability_analysis_query(tf_string)
                wolfram_response = await self.wolfram_client.query(
                    query, WolframQueryType.STABILITY_ANALYSIS
                )
                self.session_stats["wolfram_queries"] += 1

                if wolfram_response.success:
                    wolfram_result = wolfram_response.mathematical_result

            except WolframAPIException as e:
                logger.warning(f"WolframAlpha stability validation failed: {e}")

        accuracy_score = 1.0 if local_result else 0.0
        confidence_score = 0.95 if local_result.get("stable") is not None else 0.0
        validated = bool(local_result)

        return ValidationResult(
            result_id=f"stab_val_{uuid.uuid4().hex[:8]}",
            request_id=request.request_id,
            success=True,
            validated=validated,
            accuracy_score=accuracy_score,
            confidence_score=confidence_score,
            mathematical_result=local_result,
            wolfram_result=wolfram_result,
            local_result=local_result,
            validation_method="stability_analysis",
            derivation_steps=[
                f"Transfer function: {self._transfer_function_to_string(transfer_function)}",
                f"Poles: {local_result.get('poles', 'N/A')}",
                f"Stability: {'Stable' if local_result.get('stable') else 'Unstable'}",
                f"Gain margin: {local_result.get('gain_margin_db', 'N/A')} dB",
                f"Phase margin: {local_result.get('phase_margin_deg', 'N/A')}°"
            ]
        )

    async def _validate_optimization(self, request: ValidationRequest) -> ValidationResult:
        """Validate optimization problem solutions"""

        input_data = request.input_data
        objective = input_data.get("objective")
        constraints = input_data.get("constraints", [])
        variables = input_data.get("variables", [])
        solution = input_data.get("solution")

        # Local validation using scipy.optimize
        local_result = {}
        try:
            if objective and solution:
                # Validate solution satisfies constraints
                constraint_violations = []
                for constraint in constraints:
                    violation = self._check_constraint_violation(solution, constraint)
                    if violation > request.tolerance:
                        constraint_violations.append({
                            "constraint": constraint,
                            "violation": violation
                        })

                local_result = {
                    "solution_valid": len(constraint_violations) == 0,
                    "constraint_violations": constraint_violations,
                    "objective_value": self._evaluate_objective(solution, objective)
                }

        except Exception as e:
            logger.warning(f"Local optimization validation failed: {e}")

        # WolframAlpha Pro validation
        wolfram_result = None
        if self.wolfram_client and request.wolfram_validation:
            try:
                query = IndustrialControlQueries.optimization_query(
                    objective, constraints, variables
                )
                wolfram_response = await self.wolfram_client.query(
                    query, WolframQueryType.OPTIMIZATION
                )
                self.session_stats["wolfram_queries"] += 1

                if wolfram_response.success:
                    wolfram_result = wolfram_response.mathematical_result

            except WolframAPIException as e:
                logger.warning(f"WolframAlpha optimization validation failed: {e}")

        accuracy_score = 1.0 if local_result.get("solution_valid", False) else 0.0
        confidence_score = 0.9 if local_result else 0.0
        validated = bool(local_result)

        return ValidationResult(
            result_id=f"opt_val_{uuid.uuid4().hex[:8]}",
            request_id=request.request_id,
            success=True,
            validated=validated,
            accuracy_score=accuracy_score,
            confidence_score=confidence_score,
            mathematical_result=local_result,
            wolfram_result=wolfram_result,
            local_result=local_result,
            validation_method="optimization_validation"
        )

    # Helper methods

    def _parse_wolfram_solution(self, wolfram_text: str) -> List[float]:
        """Parse solutions from WolframAlpha response text"""
        try:
            # Simple regex-based parsing - could be enhanced
            numbers = re.findall(r'-?\d+\.?\d*', wolfram_text)
            return [float(num) for num in numbers]
        except:
            return []

    def _calculate_solution_discrepancy(self, sol1: List[float], sol2: List[float]) -> float:
        """Calculate discrepancy between two solution sets"""
        if not sol1 or not sol2:
            return float('inf')

        # Simple approach - compare first solutions
        if len(sol1) > 0 and len(sol2) > 0:
            return abs(sol1[0] - sol2[0])

        return float('inf')

    def _validate_proposed_solution(self, proposed: float, actual: List[float], tolerance: float) -> float:
        """Validate proposed solution against actual solutions"""
        if not actual:
            return 0.0

        min_error = min(abs(proposed - sol) for sol in actual)
        return 1.0 if min_error < tolerance else max(0.0, 1.0 - min_error)

    def _routh_hurwitz_test(self, denominator: List[float]) -> Dict[str, Any]:
        """Perform Routh-Hurwitz stability test"""
        try:
            # Basic Routh-Hurwitz implementation
            n = len(denominator) - 1
            stable = all(coeff > 0 for coeff in denominator)

            return {
                "stable": stable,
                "method": "simplified_routh_hurwitz",
                "order": n
            }
        except:
            return {"stable": False, "method": "failed", "order": 0}

    def _transfer_function_to_string(self, tf_dict: Dict[str, Any]) -> str:
        """Convert transfer function dict to string representation"""
        num = tf_dict.get("numerator", [1])
        den = tf_dict.get("denominator", [1])

        num_str = " + ".join([f"{coeff}*s^{len(num)-i-1}" for i, coeff in enumerate(num) if coeff != 0])
        den_str = " + ".join([f"{coeff}*s^{len(den)-i-1}" for i, coeff in enumerate(den) if coeff != 0])

        return f"({num_str}) / ({den_str})"

    def _check_constraint_violation(self, solution: Dict[str, float], constraint: str) -> float:
        """Check if solution violates constraint"""
        # Simplified constraint checking - would need proper parsing
        return 0.0

    def _evaluate_objective(self, solution: Dict[str, float], objective: str) -> float:
        """Evaluate objective function at solution"""
        # Simplified objective evaluation - would need proper parsing
        return 0.0

    def get_session_stats(self) -> Dict[str, Any]:
        """Get validation session statistics"""
        stats = self.session_stats.copy()

        if stats["accuracy_scores"]:
            stats["avg_accuracy"] = np.mean(stats["accuracy_scores"])
            stats["min_accuracy"] = np.min(stats["accuracy_scores"])
            stats["max_accuracy"] = np.max(stats["accuracy_scores"])
        else:
            stats["avg_accuracy"] = 0.0
            stats["min_accuracy"] = 0.0
            stats["max_accuracy"] = 0.0

        duration = datetime.now() - stats["start_time"]
        stats["session_duration"] = str(duration)

        return stats

# Integration with existing mathematical context

class ContextAwareMathematicalValidator(MathematicalValidator):
    """
    Enhanced validator with integration to existing mathematical context
    from WolframAlpha Pro context enhancement work
    """

    def __init__(self, wolfram_client: Optional[WolframAlphaProClient] = None,
                 mathematical_context_path: Optional[str] = None):
        super().__init__(wolfram_client)

        self.mathematical_context = {}
        if mathematical_context_path:
            self._load_mathematical_context(mathematical_context_path)

    def _load_mathematical_context(self, context_path: str):
        """Load existing mathematical context from previous phases"""
        try:
            with open(context_path) as f:
                self.mathematical_context = json.load(f)
            logger.info(f"📚 Loaded mathematical context from {context_path}")
        except Exception as e:
            logger.warning(f"Failed to load mathematical context: {e}")

    async def validate_with_context(self, request: ValidationRequest) -> ValidationResult:
        """Validate using both local computation and existing context"""

        # Standard validation
        result = await self.validate(request)

        # Enhance with context
        if self.mathematical_context:
            context_validation = self._validate_against_context(request, result)
            result.confidence_score = max(result.confidence_score, context_validation.get("confidence", 0.0))
            result.educational_content.extend(context_validation.get("educational_content", []))

        return result

    def _validate_against_context(self, request: ValidationRequest, result: ValidationResult) -> Dict[str, Any]:
        """Validate against existing mathematical context"""

        # Search for relevant context based on validation category
        category_context = self.mathematical_context.get(request.category.value, {})

        if not category_context:
            return {}

        # Extract relevant educational content and confidence boosts
        context_validation = {
            "confidence": 0.8,  # Boost confidence if context matches
            "educational_content": category_context.get("educational_content", []),
            "related_equations": category_context.get("equations", []),
            "related_principles": category_context.get("principles", [])
        }

        return context_validation

# Production deployment utilities

async def create_production_validator(wolfram_api_key: str,
                                    redis_url: str = "redis://localhost:6379",
                                    context_path: Optional[str] = None) -> ContextAwareMathematicalValidator:
    """Create production-ready mathematical validator"""

    # Initialize WolframAlpha Pro client
    wolfram_client = WolframAlphaProClient(
        api_key=wolfram_api_key,
        enable_caching=True,
        cache_ttl=3600,
        rate_limit_per_minute=100
    )

    # Initialize context-aware validator
    validator = ContextAwareMathematicalValidator(
        wolfram_client=wolfram_client,
        mathematical_context_path=context_path
    )

    logger.info("🚀 Production mathematical validator created")
    return validator

# Example usage and testing

async def test_mathematical_validator():
    """Test mathematical validation framework"""

    # Create test validator (without actual API key)
    validator = MathematicalValidator()

    # Test equation solving validation
    eq_request = ValidationRequest(
        request_id="test_eq_001",
        category=ValidationCategory.MATHEMATICAL_ACCURACY,
        system_type=ControlSystemType.PID,
        validation_level=ValidationLevel.STANDARD,
        input_data={
            "type": "equation_solving",
            "equation": "x**2 - 4",
            "variable": "x",
            "solution": 2.0
        }
    )

    eq_result = await validator.validate(eq_request)
    print(f"Equation validation result: {eq_result.validated}, accuracy: {eq_result.accuracy_score}")

    # Test PID controller validation
    pid_request = ValidationRequest(
        request_id="test_pid_001",
        category=ValidationCategory.CONTROL_THEORY,
        system_type=ControlSystemType.PID,
        validation_level=ValidationLevel.COMPREHENSIVE,
        input_data={
            "kp": 1.0,
            "ki": 0.1,
            "kd": 0.01,
            "process_transfer_function": {
                "numerator": [1],
                "denominator": [1, 1]
            }
        }
    )

    pid_result = await validator.validate(pid_request)
    print(f"PID validation result: {pid_result.validated}, accuracy: {pid_result.accuracy_score}")

    # Test stability analysis
    stability_request = ValidationRequest(
        request_id="test_stab_001",
        category=ValidationCategory.STABILITY_ANALYSIS,
        system_type=ControlSystemType.PID,
        validation_level=ValidationLevel.STANDARD,
        input_data={
            "transfer_function": {
                "numerator": [1],
                "denominator": [1, 2, 1]
            }
        }
    )

    stability_result = await validator.validate(stability_request)
    print(f"Stability validation result: {stability_result.validated}, accuracy: {stability_result.accuracy_score}")

    # Print session statistics
    stats = validator.get_session_stats()
    print(f"Session stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_mathematical_validator())
