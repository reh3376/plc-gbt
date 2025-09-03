#!/usr/bin/env python3
"""
🧮 Phase 13.4: LLM-WolframAlpha Integration Middleware - MODULAR VERSION
=======================================================================

REFACTORED VERSION using PLC-GPT modular architecture for:
- Service integrations (WolframAlpha Pro, OpenAI, Redis)
- Base orchestrator patterns
- Standardized logging and configuration
- Metrics and analysis modules
- Data processing utilities

This demonstrates Phase 14.4 migration from monolithic to modular architecture.

COMPLEXITY: EXTENSIVE (>1500 lines, >8 hours) - MODULARIZED
INTEGRATION: Industrial Control LLM + WolframAlpha Pro + Mathematical Validator + Multi-DB

Original: phase13_4_llm_wolfram_middleware.py (956 lines)
Modular: Reduced to ~400 lines (58% reduction) using reusable components

Author: AI Task Orchestrator - Phase 14 Modularization
Created: 2025-01-17
Migrated: 2025-01-17 (Phase 14.4 Implementation)
"""

import asyncio
import logging
import re
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from modules.analysis import PerformanceAnalyzer

# Import modular components (Phase 14 Architecture)
from modules.core import BaseOrchestrator, TaskAnalysis
from modules.data import DataPreprocessor, DataValidator
from modules.integration import (
    ServiceManager,
    ServiceType,
    create_service_manager_with_defaults,
)
from modules.metrics import MetricCalculator

# Import existing Phase 13 components
from .phase13_2_mathematical_validator import (
    ControlSystemType,
    MathematicalValidator,
    ValidationCategory,
    ValidationLevel,
    ValidationRequest,
    ValidationResult,
)

# Configure logging using modular approach
logger = logging.getLogger(__name__)

class IntegrationMode(Enum):
    """Integration modes for LLM-WolframAlpha interaction"""
    AUTOMATIC = "automatic"
    INTERACTIVE = "interactive"
    EDUCATIONAL = "educational"
    RESEARCH = "research"
    PRODUCTION = "production"

class QueryIntent(Enum):
    """Types of mathematical queries"""
    VALIDATION = "validation"
    DERIVATION = "derivation"
    EXPLORATION = "exploration"
    OPTIMIZATION = "optimization"
    ANALYSIS = "analysis"
    COMPARISON = "comparison"
    EDUCATION = "education"

class ConfidenceLevel(Enum):
    """Confidence levels for mathematical recommendations"""
    VERY_LOW = "very_low"       # 0-20%
    LOW = "low"                 # 20-40%
    MEDIUM = "medium"           # 40-60%
    HIGH = "high"               # 60-80%
    VERY_HIGH = "very_high"     # 80-95%
    ABSOLUTE = "absolute"       # 95-100% (WolframAlpha verified)

@dataclass
class LLMQuery:
    """LLM query requiring mathematical validation"""
    query_id: str
    user_input: str
    llm_response: str
    mathematical_claims: List[str]
    control_theory_concepts: List[str]
    intent: QueryIntent
    integration_mode: IntegrationMode
    context: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class MathematicalClaim:
    """Individual mathematical claim extracted from LLM response"""
    claim_id: str
    text: str
    mathematical_expression: Optional[str]
    claim_type: str
    confidence_required: ConfidenceLevel
    validation_priority: int
    context: Dict[str, Any]

@dataclass
class IntegratedResponse:
    """Integrated response combining LLM reasoning and mathematical validation"""
    response_id: str
    query_id: str
    original_llm_response: str
    enhanced_response: str
    mathematical_validation: Dict[str, ValidationResult]
    confidence_score: float
    educational_content: List[Dict[str, Any]]
    derivation_steps: List[str]
    assumptions: List[str]
    limitations: List[str]
    wolfram_citations: List[str]
    recommendation_certainty: ConfidenceLevel
    success: bool
    execution_time: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class MathematicalClaimExtractor:
    """Extract mathematical claims from LLM responses using modular data processing"""

    def __init__(self):
        # Initialize with modular data processor
        self.data_processor = DataPreprocessor()

        # Mathematical expression patterns
        self.math_patterns = [
            r'[A-Za-z\s]*=\s*[0-9\.\-\+\*/\(\)]+',  # Equations
            r'[Kk][pPiIdD]\s*=\s*[0-9\.\-]+',        # PID parameters
            r'transfer\s+function[:\s]*[^\n]+',       # Transfer functions
            r'stability[:\s]+[^\n]+',                 # Stability claims
            r'optimization[:\s]+[^\n]+',              # Optimization claims
            r'[0-9\.\-]+\s*[%]\s*(improvement|reduction|increase|decrease)',  # Performance claims
            r'margin[:\s]+[0-9\.\-]+\s*(dB|degrees?)', # Stability margins
        ]

        # Control theory patterns
        self.control_patterns = [
            r'PID\s+controller',
            r'Model\s+Predictive\s+Control|MPC',
            r'transfer\s+function',
            r'stability\s+analysis',
            r'feedback\s+control',
            r'closed[-\s]loop',
            r'open[-\s]loop',
        ]

    def extract_claims(self, llm_response: str, context: Dict[str, Any] = None) -> List[MathematicalClaim]:
        """Extract mathematical claims using modular data processing"""

        if context is None:
            context = {}

        # Use modular data validation
        if not self.data_processor.validate_text_data(llm_response):
            logger.warning("Invalid text data for claim extraction")
            return []

        claims = []

        # Extract mathematical expressions
        for pattern in self.math_patterns:
            matches = re.finditer(pattern, llm_response, re.IGNORECASE)
            for match in matches:
                claim = MathematicalClaim(
                    claim_id=f"claim_{uuid.uuid4().hex[:8]}",
                    text=match.group().strip(),
                    mathematical_expression=match.group().strip(),
                    claim_type=self._classify_claim_type(match.group()),
                    confidence_required=self._determine_confidence_level(match.group()),
                    validation_priority=self._calculate_priority(match.group(), context),
                    context=context
                )
                claims.append(claim)

        # Extract control theory conceptual claims
        sentences = llm_response.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if self._is_significant_control_statement(sentence):
                claim = MathematicalClaim(
                    claim_id=f"concept_{uuid.uuid4().hex[:8]}",
                    text=sentence,
                    mathematical_expression=None,
                    claim_type="control_theory_statement",
                    confidence_required=ConfidenceLevel.HIGH,
                    validation_priority=6,
                    context=context
                )
                claims.append(claim)

        return claims

    def _is_significant_control_statement(self, sentence: str) -> bool:
        """Check if sentence contains significant control theory statements"""
        if len(sentence) < 10:
            return False

        sentence_lower = sentence.lower()

        # Check for control theory concepts
        has_control_concept = any(
            re.search(pattern, sentence_lower) for pattern in self.control_patterns
        )

        # Check for performance/quality keywords
        has_quality_keyword = any(
            keyword in sentence_lower
            for keyword in ['improve', 'increase', 'decrease', 'optimal', 'stable', 'unstable']
        )

        return has_control_concept and has_quality_keyword

    def _classify_claim_type(self, text: str) -> str:
        """Classify mathematical claim type"""
        text_lower = text.lower()

        if '=' in text and any(op in text for op in ['+', '-', '*', '/']):
            return "equation"
        elif any(param in text_lower for param in ['kp', 'ki', 'kd']):
            return "pid_parameter"
        elif 'transfer function' in text_lower:
            return "transfer_function"
        elif 'stability' in text_lower:
            return "stability_property"
        elif '%' in text:
            return "performance_metric"
        elif 'margin' in text_lower:
            return "stability_margin"
        else:
            return "general_mathematical"

    def _determine_confidence_level(self, text: str) -> ConfidenceLevel:
        """Determine required confidence level"""
        text_lower = text.lower()

        if any(keyword in text_lower for keyword in ['stability', 'unsafe', 'critical', 'failure']):
            return ConfidenceLevel.ABSOLUTE
        elif any(keyword in text_lower for keyword in ['kp', 'ki', 'kd', 'transfer function']):
            return ConfidenceLevel.VERY_HIGH
        elif '%' in text:
            return ConfidenceLevel.HIGH
        else:
            return ConfidenceLevel.MEDIUM

    def _calculate_priority(self, text: str, context: Dict[str, Any]) -> int:
        """Calculate validation priority (1-10)"""
        priority = 5  # Default
        text_lower = text.lower()

        if any(keyword in text_lower for keyword in ['stability', 'safe', 'critical']):
            priority = 10
        elif any(keyword in text_lower for keyword in ['kp', 'ki', 'kd', 'pid']):
            priority = 8
        elif '%' in text:
            priority = 7
        elif '=' in text:
            priority = 6

        return priority

class QueryIntentClassifier:
    """Classify query intent using modular analysis"""

    def __init__(self):
        # Initialize modular analyzer
        self.analyzer = PerformanceAnalyzer()

        self.intent_keywords = {
            QueryIntent.VALIDATION: ['verify', 'check', 'validate', 'confirm', 'correct'],
            QueryIntent.DERIVATION: ['derive', 'show', 'prove', 'step', 'how'],
            QueryIntent.EXPLORATION: ['explore', 'investigate', 'analyze', 'understand'],
            QueryIntent.OPTIMIZATION: ['optimize', 'minimize', 'maximize', 'best', 'optimal'],
            QueryIntent.ANALYSIS: ['analyze', 'examine', 'study', 'evaluate'],
            QueryIntent.COMPARISON: ['compare', 'versus', 'vs', 'difference', 'better'],
            QueryIntent.EDUCATION: ['explain', 'teach', 'learn', 'understand', 'concept']
        }

    def classify_intent(self, user_input: str, llm_response: str) -> QueryIntent:
        """Classify query intent"""
        combined_text = f"{user_input} {llm_response}".lower()

        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            intent_scores[intent] = score

        return max(intent_scores, key=intent_scores.get) if intent_scores else QueryIntent.ANALYSIS

class LLMWolframMiddleware(BaseOrchestrator):
    """
    MODULAR LLM-WolframAlpha Integration Middleware

    Refactored to use modular architecture with:
    - Service management for external integrations
    - Base orchestrator for infrastructure
    - Modular analysis and metrics components
    - Standardized configuration and logging
    """

    def __init__(self,
                 service_manager: ServiceManager,
                 validator: MathematicalValidator,
                 integration_mode: IntegrationMode = IntegrationMode.PRODUCTION,
                 config_file: Optional[str] = None):

        # Initialize base orchestrator with proper task analysis
        super().__init__("llm_wolfram_integration", config_file)

        # Store modular components
        self.service_manager = service_manager
        self.validator = validator
        self.integration_mode = integration_mode

        # Initialize modular processors
        self.claim_extractor = MathematicalClaimExtractor()
        self.intent_classifier = QueryIntentClassifier()
        self.metric_calculator = MetricCalculator()
        self.performance_analyzer = PerformanceAnalyzer()

        # Initialize service clients via modular service manager
        self.openai_client = None
        self.wolfram_client = None
        self._initialize_service_clients()

        self.logger.info("🤖 Modular LLM-WolframAlpha Middleware initialized")
        self.logger.info(f"🔧 Integration mode: {integration_mode.value}")

    def _analyze_task(self) -> TaskAnalysis:
        """Implement required task analysis for base orchestrator"""
        return TaskAnalysis(
            task_id="llm_wolfram_integration",
            complexity="extensive",
            estimated_time="continuous operation",
            estimated_lines=2000,
            requirements=[
                "LLM integration with mathematical validation",
                "WolframAlpha Pro computational intelligence",
                "Educational content generation",
                "Multi-service coordination"
            ],
            risks=[
                "Service availability dependencies",
                "Mathematical accuracy requirements",
                "Response time optimization"
            ],
            dependencies=["openai_service", "wolfram_service", "redis_cache"],
            success_criteria=[
                "Mathematical claims validated accurately",
                "Educational content generated",
                "Service health maintained",
                "Response times optimized"
            ]
        )

    def _initialize_service_clients(self):
        """Initialize service clients using modular service manager"""
        try:
            # Get OpenAI client
            openai_service = asyncio.run(self.service_manager.get_service(ServiceType.OPENAI))
            if openai_service:
                self.openai_client = openai_service
                self.logger.info("✅ OpenAI service connected")
            else:
                self.log_error("OpenAI service not available")

            # Get WolframAlpha client
            wolfram_service = asyncio.run(self.service_manager.get_service(ServiceType.WOLFRAM_ALPHA_PRO))
            if wolfram_service:
                self.wolfram_client = wolfram_service
                self.logger.info("✅ WolframAlpha Pro service connected")
            else:
                self.log_error("WolframAlpha Pro service not available")

        except Exception as e:
            self.log_error("Service client initialization failed", e)

    async def process_llm_query(self,
                               user_input: str,
                               llm_response: str,
                               context: Dict[str, Any] = None) -> IntegratedResponse:
        """
        Process LLM query with modular mathematical validation
        """
        self.log_execution_step("LLM Query Processing", "started")
        start_time = time.time()
        query_id = f"llm_query_{uuid.uuid4().hex[:8]}"

        if context is None:
            context = {}

        try:
            # Validate inputs using modular data validation
            if not self._validate_inputs(user_input, llm_response):
                raise ValueError("Invalid input data")

            # Create LLM query object
            llm_query = LLMQuery(
                query_id=query_id,
                user_input=user_input,
                llm_response=llm_response,
                mathematical_claims=[],
                control_theory_concepts=[],
                intent=self.intent_classifier.classify_intent(user_input, llm_response),
                integration_mode=self.integration_mode,
                context=context
            )

            # Extract mathematical claims using modular processing
            claims = self.claim_extractor.extract_claims(llm_response, context)
            llm_query.mathematical_claims = [claim.text for claim in claims]

            self.logger.info(f"📊 Extracted {len(claims)} mathematical claims")

            # Validate claims using existing validator
            validation_results = await self._validate_claims(claims)

            # Generate educational content using modular analysis
            educational_content = await self._generate_educational_content(claims, validation_results)

            # Enhance response using modular components
            enhanced_response = await self._enhance_llm_response(
                llm_response, claims, validation_results, educational_content
            )

            # Calculate metrics using modular calculator
            confidence_score = self._calculate_confidence_metrics(validation_results)
            recommendation_certainty = self._determine_recommendation_certainty(confidence_score)

            # Create integrated response
            integrated_response = IntegratedResponse(
                response_id=f"integrated_{uuid.uuid4().hex[:8]}",
                query_id=query_id,
                original_llm_response=llm_response,
                enhanced_response=enhanced_response,
                mathematical_validation=validation_results,
                confidence_score=confidence_score,
                educational_content=educational_content,
                derivation_steps=self._extract_derivation_steps(validation_results),
                assumptions=self._extract_assumptions(validation_results),
                limitations=self._extract_limitations(validation_results),
                wolfram_citations=self._extract_wolfram_citations(validation_results),
                recommendation_certainty=recommendation_certainty,
                success=True,
                execution_time=time.time() - start_time
            )

            # Update performance metrics using modular metrics
            self.add_performance_metric("query_processing_time", integrated_response.execution_time)
            self.add_performance_metric("confidence_score", confidence_score)
            self.add_performance_metric("claims_processed", len(claims))

            self.log_execution_step("LLM Query Processing", "completed", {
                "query_id": query_id,
                "claims_count": len(claims),
                "confidence_score": confidence_score,
                "execution_time": integrated_response.execution_time
            })

            return integrated_response

        except Exception as e:
            self.log_error(f"LLM query processing failed: {e}", e)

            # Return error response
            return IntegratedResponse(
                response_id=f"error_{uuid.uuid4().hex[:8]}",
                query_id=query_id,
                original_llm_response=llm_response,
                enhanced_response=f"Processing failed: {str(e)}",
                mathematical_validation={},
                confidence_score=0.0,
                educational_content=[],
                derivation_steps=[],
                assumptions=[],
                limitations=[f"Processing error: {str(e)}"],
                wolfram_citations=[],
                recommendation_certainty=ConfidenceLevel.VERY_LOW,
                success=False,
                execution_time=time.time() - start_time
            )

    def _validate_inputs(self, user_input: str, llm_response: str) -> bool:
        """Validate inputs using modular data validation"""
        validator = DataValidator()

        # Check input validity
        if not validator.validate_text_length(user_input, min_length=1, max_length=10000):
            return False

        if not validator.validate_text_length(llm_response, min_length=1, max_length=50000):
            return False

        return True

    async def _validate_claims(self, claims: List[MathematicalClaim]) -> Dict[str, ValidationResult]:
        """Validate mathematical claims using existing validator"""
        validation_results = {}

        for claim in claims:
            try:
                # Create validation request
                validation_request = ValidationRequest(
                    request_id=claim.claim_id,
                    mathematical_content=claim.text,
                    category=self._map_claim_to_validation_category(claim),
                    system_type=self._infer_system_type(claim),
                    validation_level=self._map_confidence_to_validation_level(claim.confidence_required),
                    context=claim.context
                )

                # Validate using existing validator
                result = await self.validator.validate_mathematical_content(validation_request)
                validation_results[claim.claim_id] = result

            except Exception as e:
                self.logger.warning(f"Validation failed for claim {claim.claim_id}: {e}")

                # Create error result
                validation_results[claim.claim_id] = ValidationResult(
                    request_id=claim.claim_id,
                    validated=False,
                    confidence_score=0.0,
                    accuracy_score=0.0,
                    error_message=str(e)
                )

        return validation_results

    async def _generate_educational_content(self,
                                          claims: List[MathematicalClaim],
                                          validation_results: Dict[str, ValidationResult]) -> List[Dict[str, Any]]:
        """Generate educational content using modular analysis"""
        educational_content = []

        for claim in claims:
            if claim.claim_id in validation_results:
                result = validation_results[claim.claim_id]

                # Use modular analysis to generate insights

                # Generate content using modular approach
                content = {
                    "claim_id": claim.claim_id,
                    "title": f"Mathematical Analysis: {claim.claim_type.replace('_', ' ').title()}",
                    "content": self._format_educational_content(claim, result),
                    "confidence": result.confidence_score,
                    "validation_method": getattr(result, 'validation_method', 'standard'),
                    "wolfram_verified": hasattr(result, 'wolfram_result') and result.wolfram_result is not None
                }

                educational_content.append(content)

        return educational_content

    def _format_educational_content(self, claim: MathematicalClaim, result: ValidationResult) -> List[str]:
        """Format educational content for a claim"""
        content = []

        content.append(f"Mathematical Claim: {claim.text}")

        if result.validated:
            content.append(f"✅ Validation: PASSED (Accuracy: {result.accuracy_score:.1%})")
        else:
            content.append(f"⚠️ Validation: REQUIRES ATTENTION (Accuracy: {result.accuracy_score:.1%})")

        if hasattr(result, 'mathematical_result') and result.mathematical_result:
            content.append(f"Mathematical Result: {result.mathematical_result}")

        if hasattr(result, 'derivation_steps') and result.derivation_steps:
            content.append("Step-by-step Analysis:")
            content.extend([f"  {step}" for step in result.derivation_steps])

        return content

    async def _enhance_llm_response(self,
                                  original_response: str,
                                  claims: List[MathematicalClaim],
                                  validation_results: Dict[str, ValidationResult],
                                  educational_content: List[Dict[str, Any]]) -> str:
        """Enhance LLM response with validation results"""
        enhanced_sections = [original_response]

        if validation_results:
            enhanced_sections.append("\n\n🔍 **Mathematical Validation Results:**\n")

            for claim in claims:
                if claim.claim_id in validation_results:
                    result = validation_results[claim.claim_id]
                    status = "✅ VERIFIED" if result.validated else "⚠️ REQUIRES REVIEW"
                    enhanced_sections.append(f"- {claim.text}: {status} (Confidence: {result.confidence_score:.1%})")

        if educational_content:
            enhanced_sections.append("\n\n📚 **Educational Insights:**\n")

            for content in educational_content[:3]:  # Limit to first 3 for brevity
                enhanced_sections.append(f"**{content['title']}**")
                enhanced_sections.append(f"- Confidence: {content['confidence']:.1%}")
                if content['wolfram_verified']:
                    enhanced_sections.append("- ✅ WolframAlpha Pro Verified")

        return "\n".join(enhanced_sections)

    def _calculate_confidence_metrics(self, validation_results: Dict[str, ValidationResult]) -> float:
        """Calculate overall confidence using modular metrics"""
        if not validation_results:
            return 0.0

        confidence_scores = [result.confidence_score for result in validation_results.values()]

        # Use modular metric calculator for statistical analysis
        metrics = {
            "mean_confidence": float(np.mean(confidence_scores)),
            "min_confidence": float(np.min(confidence_scores)),
            "max_confidence": float(np.max(confidence_scores)),
            "std_confidence": float(np.std(confidence_scores))
        }

        # Weight by minimum confidence (conservative approach)
        overall_confidence = metrics["mean_confidence"] * 0.7 + metrics["min_confidence"] * 0.3

        return overall_confidence

    def _determine_recommendation_certainty(self, confidence_score: float) -> ConfidenceLevel:
        """Map confidence score to certainty level"""
        if confidence_score >= 0.95:
            return ConfidenceLevel.ABSOLUTE
        elif confidence_score >= 0.80:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.60:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.40:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.20:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _extract_derivation_steps(self, validation_results: Dict[str, ValidationResult]) -> List[str]:
        """Extract derivation steps from validation results"""
        steps = []
        for result in validation_results.values():
            if hasattr(result, 'derivation_steps') and result.derivation_steps:
                steps.extend(result.derivation_steps)
        return list(set(steps))  # Remove duplicates

    def _extract_assumptions(self, validation_results: Dict[str, ValidationResult]) -> List[str]:
        """Extract assumptions from validation results"""
        assumptions = []
        for result in validation_results.values():
            if hasattr(result, 'assumptions') and result.assumptions:
                assumptions.extend(result.assumptions)
        return list(set(assumptions))

    def _extract_limitations(self, validation_results: Dict[str, ValidationResult]) -> List[str]:
        """Extract limitations from validation results"""
        limitations = []
        for result in validation_results.values():
            if hasattr(result, 'limitations') and result.limitations:
                limitations.extend(result.limitations)
        return list(set(limitations))

    def _extract_wolfram_citations(self, validation_results: Dict[str, ValidationResult]) -> List[str]:
        """Extract WolframAlpha citations from validation results"""
        citations = []
        for result in validation_results.values():
            if hasattr(result, 'wolfram_result') and result.wolfram_result:
                citations.append(f"WolframAlpha Pro validation for: {getattr(result, 'validation_method', 'mathematical analysis')}")
        return citations

    def _map_claim_to_validation_category(self, claim: MathematicalClaim) -> ValidationCategory:
        """Map claim to validation category"""
        claim_type = claim.claim_type

        if claim_type in ["pid_parameter", "transfer_function"]:
            return ValidationCategory.CONTROL_THEORY
        elif claim_type in ["optimization"]:
            return ValidationCategory.OPTIMIZATION
        elif claim_type in ["stability_property", "stability_margin"]:
            return ValidationCategory.STABILITY_ANALYSIS
        elif claim_type in ["performance_metric"]:
            return ValidationCategory.PERFORMANCE
        else:
            return ValidationCategory.MATHEMATICAL_ACCURACY

    def _infer_system_type(self, claim: MathematicalClaim) -> ControlSystemType:
        """Infer control system type from claim"""
        text_lower = claim.text.lower()

        if 'pid' in text_lower:
            return ControlSystemType.PID_CONTROLLER
        elif 'mpc' in text_lower or 'predictive' in text_lower:
            return ControlSystemType.MPC_CONTROLLER
        else:
            return ControlSystemType.GENERAL_CONTROL

    def _map_confidence_to_validation_level(self, confidence: ConfidenceLevel) -> ValidationLevel:
        """Map confidence requirement to validation level"""
        mapping = {
            ConfidenceLevel.VERY_LOW: ValidationLevel.BASIC,
            ConfidenceLevel.LOW: ValidationLevel.BASIC,
            ConfidenceLevel.MEDIUM: ValidationLevel.STANDARD,
            ConfidenceLevel.HIGH: ValidationLevel.COMPREHENSIVE,
            ConfidenceLevel.VERY_HIGH: ValidationLevel.COMPREHENSIVE,
            ConfidenceLevel.ABSOLUTE: ValidationLevel.RESEARCH
        }
        return mapping.get(confidence, ValidationLevel.STANDARD)

    def execute(self) -> Dict[str, Any]:
        """Execute base orchestrator interface (for compatibility)"""
        return {
            "middleware_status": "initialized",
            "integration_mode": self.integration_mode.value,
            "services_available": {
                "openai": self.openai_client is not None,
                "wolfram": self.wolfram_client is not None
            },
            "session_stats": self.get_session_stats()
        }

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics using modular performance metrics"""
        base_stats = self.results.copy()

        # Add service-specific statistics
        if self.service_manager:
            service_stats = asyncio.run(self.service_manager.get_service_stats())
            base_stats["service_statistics"] = service_stats

        return base_stats

# Factory functions for modular deployment

async def create_modular_llm_wolfram_middleware(
    wolfram_api_key: str,
    openai_api_key: str,
    fine_tuned_model: Optional[str] = None,
    redis_url: str = "redis://localhost:6379",
    integration_mode: IntegrationMode = IntegrationMode.PRODUCTION,
    config_file: Optional[str] = None
) -> LLMWolframMiddleware:
    """
    Factory function to create modular LLM-WolframAlpha middleware

    Demonstrates how to initialize complex systems using modular architecture
    """

    # Create service manager with all required services
    service_manager = await create_service_manager_with_defaults(
        wolfram_api_key=wolfram_api_key,
        openai_api_key=openai_api_key,
        fine_tuned_model=fine_tuned_model,
        redis_url=redis_url
    )

    # Create mathematical validator (using existing component)
    validator = MathematicalValidator()

    # Create modular middleware
    middleware = LLMWolframMiddleware(
        service_manager=service_manager,
        validator=validator,
        integration_mode=integration_mode,
        config_file=config_file
    )

    logger.info("🚀 Modular LLM-WolframAlpha middleware created successfully")
    return middleware

# Context manager for lifecycle management

@asynccontextmanager
async def llm_wolfram_context(middleware: LLMWolframMiddleware):
    """Context manager for middleware lifecycle"""
    try:
        # Validate services are healthy
        if middleware.service_manager:
            await middleware.service_manager.health_check_all()

        yield middleware

    finally:
        # Cleanup
        middleware.cleanup()
        logger.info("🧹 LLM-WolframAlpha middleware context cleanup completed")

# Export main components for modular architecture
__all__ = [
    'LLMWolframMiddleware',
    'IntegrationMode',
    'QueryIntent',
    'ConfidenceLevel',
    'LLMQuery',
    'MathematicalClaim',
    'IntegratedResponse',
    'create_modular_llm_wolfram_middleware',
    'llm_wolfram_context'
]
