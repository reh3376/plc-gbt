#!/usr/bin/env python3
"""
🧮 Phase 13.4: LLM-WolframAlpha Integration Middleware - AI Task Orchestrator Implementation

Seamless integration between the Industrial Control Theory LLM and WolframAlpha Pro
for mathematical validation, educational derivations, and confidence scoring.

Following AI Task Orchestrator Guide methodology for:
- Seamless integration where LLM calls WolframAlpha Pro
- Mathematical query generation from natural language
- Result synthesis between AI reasoning and computation
- Educational mode with step-by-step derivations
- Mathematical certainty metrics for recommendations

COMPLEXITY: EXTENSIVE (>1500 lines, >8 hours)
INTEGRATION: Industrial Control LLM + WolframAlpha Pro + Mathematical Validator + Multi-DB

Author: AI Task Orchestrator
Created: 2025-01-17
Phase: 13.4 - LLM-WolframAlpha Integration
"""

import asyncio
import logging
import re
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from openai import AsyncOpenAI

# Import from previous Phase 13 components
from .phase13_1_wolfram_api_client import (
    WolframAlphaProClient,
)
from .phase13_2_mathematical_validator import (
    ContextAwareMathematicalValidator,
    ControlSystemType,
    MathematicalValidator,
    ValidationCategory,
    ValidationLevel,
    ValidationRequest,
    ValidationResult,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationMode(Enum):
    """Integration modes for LLM-WolframAlpha interaction"""
    AUTOMATIC = "automatic"         # Automatic mathematical validation
    INTERACTIVE = "interactive"     # User-guided validation
    EDUCATIONAL = "educational"     # Step-by-step educational mode
    RESEARCH = "research"           # Advanced research mode
    PRODUCTION = "production"       # Production deployment mode

class QueryIntent(Enum):
    """Types of mathematical queries the LLM might generate"""
    VALIDATION = "validation"                   # Validate a calculation
    DERIVATION = "derivation"                  # Show mathematical derivation
    EXPLORATION = "exploration"                # Explore mathematical concepts
    OPTIMIZATION = "optimization"              # Solve optimization problems
    ANALYSIS = "analysis"                      # Analyze control systems
    COMPARISON = "comparison"                  # Compare different approaches
    EDUCATION = "education"                    # Educational explanation

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
    claim_type: str  # equation, calculation, property, theorem, etc.
    confidence_required: ConfidenceLevel
    validation_priority: int  # 1-10 scale
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
    """Extract mathematical claims from LLM responses"""

    def __init__(self):
        # Patterns for detecting mathematical claims
        self.math_patterns = [
            r'[A-Za-z\s]*=\s*[0-9\.\-\+\*/\(\)]+',  # Equations
            r'[Kk][pPiIdD]\s*=\s*[0-9\.\-]+',        # PID parameters
            r'transfer\s+function[:\s]*[^\n]+',       # Transfer functions
            r'stability[:\s]+[^\n]+',                 # Stability claims
            r'optimization[:\s]+[^\n]+',              # Optimization claims
            r'[0-9\.\-]+\s*[%]\s*(improvement|reduction|increase|decrease)',  # Performance claims
            r'margin[:\s]+[0-9\.\-]+\s*(dB|degrees?)', # Stability margins
        ]

        # Control theory concept patterns
        self.control_patterns = [
            r'PID\s+controller',
            r'Model\s+Predictive\s+Control|MPC',
            r'transfer\s+function',
            r'stability\s+analysis',
            r'root\s+locus',
            r'Bode\s+plot',
            r'Nyquist\s+plot',
            r'feedback\s+control',
            r'closed[-\s]loop',
            r'open[-\s]loop',
        ]

    def extract_claims(self, llm_response: str, context: Dict[str, Any] = None) -> List[MathematicalClaim]:
        """Extract mathematical claims from LLM response"""

        if context is None:
            context = {}

        claims = []

        # Extract mathematical expressions
        for _i, pattern in enumerate(self.math_patterns):
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

        # Extract control theory concepts
        control_concepts = []
        for pattern in self.control_patterns:
            matches = re.finditer(pattern, llm_response, re.IGNORECASE)
            for match in matches:
                control_concepts.append(match.group().strip())

        # Create conceptual claims for important control theory statements
        sentences = llm_response.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and any(concept.lower() in sentence.lower() for concept in control_concepts):
                if any(keyword in sentence.lower() for keyword in ['improve', 'increase', 'decrease', 'optimal', 'stable', 'unstable']):
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

    def _classify_claim_type(self, text: str) -> str:
        """Classify the type of mathematical claim"""
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
        """Determine required confidence level for validation"""
        text_lower = text.lower()

        # Critical safety and stability claims need highest confidence
        if any(keyword in text_lower for keyword in ['stability', 'unsafe', 'critical', 'failure']):
            return ConfidenceLevel.ABSOLUTE

        # PID parameters and transfer functions need high confidence
        elif any(keyword in text_lower for keyword in ['kp', 'ki', 'kd', 'transfer function']):
            return ConfidenceLevel.VERY_HIGH

        # Performance claims need high confidence
        elif '%' in text:
            return ConfidenceLevel.HIGH

        # General mathematical claims need medium confidence
        else:
            return ConfidenceLevel.MEDIUM

    def _calculate_priority(self, text: str, context: Dict[str, Any]) -> int:
        """Calculate validation priority (1-10)"""
        priority = 5  # Default medium priority

        text_lower = text.lower()

        # Safety-critical claims get highest priority
        if any(keyword in text_lower for keyword in ['stability', 'safe', 'critical']):
            priority = 10

        # Control parameters get high priority
        elif any(keyword in text_lower for keyword in ['kp', 'ki', 'kd', 'pid']):
            priority = 8

        # Performance claims get medium-high priority
        elif '%' in text:
            priority = 7

        # Mathematical equations get medium priority
        elif '=' in text:
            priority = 6

        return priority

class QueryIntentClassifier:
    """Classify the intent of mathematical queries"""

    def __init__(self):
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
        """Classify the intent of the query"""

        combined_text = f"{user_input} {llm_response}".lower()

        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            intent_scores[intent] = score

        # Return intent with highest score, default to ANALYSIS
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        else:
            return QueryIntent.ANALYSIS

class WolframQueryGenerator:
    """Generate WolframAlpha queries from mathematical claims"""

    def __init__(self):
        self.query_templates = {
            "equation": "solve {expression}",
            "pid_parameter": "analyze PID controller with {parameters} for stability and performance",
            "transfer_function": "analyze transfer function {expression} for poles, zeros, and stability",
            "stability_property": "stability analysis of {expression}",
            "performance_metric": "calculate {expression} and verify result",
            "stability_margin": "gain margin and phase margin of {expression}",
            "optimization": "optimize {objective} subject to {constraints}",
            "control_theory_statement": "verify control theory statement: {statement}"
        }

    def generate_query(self, claim: MathematicalClaim) -> str:
        """Generate WolframAlpha query for mathematical claim"""

        claim_type = claim.claim_type
        template = self.query_templates.get(claim_type, "analyze {expression}")

        if claim.mathematical_expression:
            query = template.format(expression=claim.mathematical_expression)
        else:
            query = template.format(
                expression=claim.text,
                statement=claim.text,
                parameters=claim.text,
                objective=claim.text,
                constraints=claim.text
            )

        return query

class EducationalContentGenerator:
    """Generate educational content from mathematical validations"""

    def __init__(self):
        self.education_templates = {
            "equation_solving": [
                "Let's solve this equation step by step:",
                "1. Starting with: {equation}",
                "2. Mathematical analysis: {analysis}",
                "3. Solution: {solution}",
                "4. Verification: {verification}"
            ],
            "pid_tuning": [
                "PID Controller Analysis:",
                "1. Controller parameters: Kp={kp}, Ki={ki}, Kd={kd}",
                "2. Transfer function: {transfer_function}",
                "3. Stability analysis: {stability}",
                "4. Performance characteristics: {performance}",
                "5. Recommendations: {recommendations}"
            ],
            "stability_analysis": [
                "Control System Stability Analysis:",
                "1. System transfer function: {transfer_function}",
                "2. Pole locations: {poles}",
                "3. Stability assessment: {stability}",
                "4. Stability margins: {margins}",
                "5. Design implications: {implications}"
            ]
        }

    def generate_educational_content(self,
                                   validation_results: Dict[str, ValidationResult],
                                   claims: List[MathematicalClaim]) -> List[Dict[str, Any]]:
        """Generate educational content from validation results"""

        educational_content = []

        for claim in claims:
            claim_id = claim.claim_id
            if claim_id in validation_results:
                result = validation_results[claim_id]

                content = {
                    "claim_id": claim_id,
                    "title": f"Mathematical Analysis: {claim.claim_type.replace('_', ' ').title()}",
                    "content": self._generate_content_for_claim(claim, result),
                    "confidence": result.confidence_score,
                    "validation_method": result.validation_method,
                    "wolfram_verified": result.wolfram_result is not None
                }

                educational_content.append(content)

        return educational_content

    def _generate_content_for_claim(self, claim: MathematicalClaim, result: ValidationResult) -> List[str]:
        """Generate specific educational content for a claim"""

        content = []

        # Add claim description
        content.append(f"Mathematical Claim: {claim.text}")

        # Add validation result
        if result.validated:
            content.append(f"✅ Validation: PASSED (Accuracy: {result.accuracy_score:.1%})")
        else:
            content.append(f"⚠️ Validation: REQUIRES ATTENTION (Accuracy: {result.accuracy_score:.1%})")

        # Add mathematical result
        if result.mathematical_result:
            content.append(f"Mathematical Result: {result.mathematical_result}")

        # Add derivation steps
        if result.derivation_steps:
            content.append("Step-by-step Analysis:")
            content.extend([f"  {step}" for step in result.derivation_steps])

        # Add WolframAlpha insights
        if result.wolfram_result:
            content.append(f"WolframAlpha Pro Verification: {result.wolfram_result}")

        # Add educational insights
        if result.educational_content:
            content.append("Educational Insights:")
            content.extend([f"  • {insight}" for insight in result.educational_content])

        return content

class LLMWolframMiddleware:
    """
    Main middleware class for seamless LLM-WolframAlpha integration

    Provides comprehensive integration between Industrial Control Theory LLM
    and WolframAlpha Pro for mathematical validation and educational enhancement.
    """

    def __init__(self,
                 openai_client: AsyncOpenAI,
                 wolfram_client: WolframAlphaProClient,
                 validator: MathematicalValidator,
                 redis_client: Optional[redis.Redis] = None,
                 integration_mode: IntegrationMode = IntegrationMode.PRODUCTION):

        self.openai_client = openai_client
        self.wolfram_client = wolfram_client
        self.validator = validator
        self.redis_client = redis_client
        self.integration_mode = integration_mode

        # Initialize components
        self.claim_extractor = MathematicalClaimExtractor()
        self.intent_classifier = QueryIntentClassifier()
        self.query_generator = WolframQueryGenerator()
        self.education_generator = EducationalContentGenerator()

        # Session statistics
        self.session_stats = {
            "queries_processed": 0,
            "claims_validated": 0,
            "wolfram_queries": 0,
            "high_confidence_results": 0,
            "educational_responses": 0,
            "start_time": datetime.now()
        }

        logger.info("🤖 LLM-WolframAlpha Middleware initialized")
        logger.info(f"🔧 Integration mode: {integration_mode.value}")

    async def process_llm_query(self,
                               user_input: str,
                               llm_response: str,
                               context: Dict[str, Any] = None) -> IntegratedResponse:
        """
        Process LLM query with mathematical validation and enhancement
        """
        start_time = time.time()
        query_id = f"llm_query_{uuid.uuid4().hex[:8]}"

        if context is None:
            context = {}

        logger.info(f"🔍 Processing LLM query: {query_id}")

        try:
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

            # Extract mathematical claims
            claims = self.claim_extractor.extract_claims(llm_response, context)
            llm_query.mathematical_claims = [claim.text for claim in claims]

            logger.info(f"📊 Extracted {len(claims)} mathematical claims")

            # Validate claims
            validation_results = await self._validate_claims(claims)

            # Generate educational content
            educational_content = self.education_generator.generate_educational_content(
                validation_results, claims
            )

            # Enhance LLM response
            enhanced_response = await self._enhance_llm_response(
                llm_response, claims, validation_results, educational_content
            )

            # Calculate overall confidence
            confidence_score = self._calculate_overall_confidence(validation_results)
            recommendation_certainty = self._determine_recommendation_certainty(confidence_score)

            # Collect derivation steps and other metadata
            derivation_steps = []
            assumptions = []
            limitations = []
            wolfram_citations = []

            for result in validation_results.values():
                derivation_steps.extend(result.derivation_steps)
                assumptions.extend(result.assumptions)
                limitations.extend(result.limitations)
                if result.wolfram_result:
                    wolfram_citations.append(f"WolframAlpha Pro validation for: {result.validation_method}")

            # Create integrated response
            integrated_response = IntegratedResponse(
                response_id=f"integrated_{uuid.uuid4().hex[:8]}",
                query_id=query_id,
                original_llm_response=llm_response,
                enhanced_response=enhanced_response,
                mathematical_validation=validation_results,
                confidence_score=confidence_score,
                educational_content=educational_content,
                derivation_steps=list(set(derivation_steps)),  # Remove duplicates
                assumptions=list(set(assumptions)),
                limitations=list(set(limitations)),
                wolfram_citations=wolfram_citations,
                recommendation_certainty=recommendation_certainty,
                success=True,
                execution_time=time.time() - start_time
            )

            # Update session statistics
            self.session_stats["queries_processed"] += 1
            self.session_stats["claims_validated"] += len(claims)
            self.session_stats["wolfram_queries"] += len([r for r in validation_results.values() if r.wolfram_result])
            if confidence_score >= 0.8:
                self.session_stats["high_confidence_results"] += 1
            if educational_content:
                self.session_stats["educational_responses"] += 1

            logger.info(f"✅ LLM query processing completed: {query_id}")
            logger.info(f"📊 Confidence: {confidence_score:.1%}, Certainty: {recommendation_certainty.value}")

            return integrated_response

        except Exception as e:
            error_response = IntegratedResponse(
                response_id=f"error_{uuid.uuid4().hex[:8]}",
                query_id=query_id,
                original_llm_response=llm_response,
                enhanced_response=llm_response,  # Fallback to original
                mathematical_validation={},
                confidence_score=0.0,
                educational_content=[],
                derivation_steps=[],
                assumptions=[],
                limitations=[f"Error during processing: {str(e)}"],
                wolfram_citations=[],
                recommendation_certainty=ConfidenceLevel.VERY_LOW,
                success=False,
                execution_time=time.time() - start_time
            )

            logger.error(f"❌ LLM query processing failed: {query_id} - {e}")
            return error_response

    async def _validate_claims(self, claims: List[MathematicalClaim]) -> Dict[str, ValidationResult]:
        """Validate mathematical claims using the validation framework"""

        validation_results = {}

        # Sort claims by priority
        sorted_claims = sorted(claims, key=lambda c: c.validation_priority, reverse=True)

        for claim in sorted_claims:
            try:
                # Create validation request
                validation_request = ValidationRequest(
                    request_id=f"val_{claim.claim_id}",
                    category=self._map_claim_to_validation_category(claim),
                    system_type=self._infer_system_type(claim),
                    validation_level=self._map_confidence_to_validation_level(claim.confidence_required),
                    input_data=self._prepare_validation_input(claim),
                    tolerance=1e-6,
                    wolfram_validation=True,
                    context=claim.context
                )

                # Perform validation
                result = await self.validator.validate(validation_request)
                validation_results[claim.claim_id] = result

                logger.info(f"✓ Validated claim: {claim.claim_id} (Accuracy: {result.accuracy_score:.1%})")

            except Exception as e:
                logger.warning(f"Failed to validate claim {claim.claim_id}: {e}")
                # Create minimal error result
                error_result = ValidationResult(
                    result_id=f"error_{claim.claim_id}",
                    request_id=f"val_{claim.claim_id}",
                    success=False,
                    validated=False,
                    accuracy_score=0.0,
                    confidence_score=0.0,
                    mathematical_result=None,
                    errors=[str(e)]
                )
                validation_results[claim.claim_id] = error_result

        return validation_results

    async def _enhance_llm_response(self,
                                  original_response: str,
                                  claims: List[MathematicalClaim],
                                  validation_results: Dict[str, ValidationResult],
                                  educational_content: List[Dict[str, Any]]) -> str:
        """Enhance LLM response with mathematical validation and educational content"""

        enhanced_response = original_response

        # Add validation indicators
        if self.integration_mode in [IntegrationMode.EDUCATIONAL, IntegrationMode.INTERACTIVE]:
            enhanced_response += "\n\n## Mathematical Validation\n"

            for claim in claims:
                if claim.claim_id in validation_results:
                    result = validation_results[claim.claim_id]
                    status = "✅ VERIFIED" if result.validated and result.accuracy_score > 0.8 else "⚠️ NEEDS REVIEW"
                    enhanced_response += f"\n**{claim.text}** - {status} (Confidence: {result.confidence_score:.1%})"

        # Add educational content
        if educational_content and self.integration_mode == IntegrationMode.EDUCATIONAL:
            enhanced_response += "\n\n## Mathematical Analysis & Education\n"

            for content in educational_content:
                enhanced_response += f"\n### {content['title']}\n"
                for line in content['content']:
                    enhanced_response += f"{line}\n"

        # Add WolframAlpha citations
        wolfram_validations = [r for r in validation_results.values() if r.wolfram_result]
        if wolfram_validations:
            enhanced_response += "\n\n*Mathematical validation powered by WolframAlpha Pro computational intelligence.*"

        return enhanced_response

    def _map_claim_to_validation_category(self, claim: MathematicalClaim) -> ValidationCategory:
        """Map claim type to validation category"""

        claim_type = claim.claim_type

        if claim_type in ["equation", "general_mathematical"]:
            return ValidationCategory.MATHEMATICAL_ACCURACY
        elif claim_type in ["pid_parameter", "transfer_function", "control_theory_statement"]:
            return ValidationCategory.CONTROL_THEORY
        elif claim_type in ["stability_property", "stability_margin"]:
            return ValidationCategory.STABILITY_ANALYSIS
        elif claim_type == "performance_metric":
            return ValidationCategory.PERFORMANCE
        else:
            return ValidationCategory.MATHEMATICAL_ACCURACY

    def _infer_system_type(self, claim: MathematicalClaim) -> ControlSystemType:
        """Infer control system type from claim"""

        text_lower = claim.text.lower()

        if any(keyword in text_lower for keyword in ['pid', 'kp', 'ki', 'kd']):
            return ControlSystemType.PID
        elif any(keyword in text_lower for keyword in ['mpc', 'model predictive', 'optimization']):
            return ControlSystemType.MPC
        elif 'optimal' in text_lower:
            return ControlSystemType.OPTIMAL
        elif 'adaptive' in text_lower:
            return ControlSystemType.ADAPTIVE
        else:
            return ControlSystemType.PID  # Default

    def _map_confidence_to_validation_level(self, confidence: ConfidenceLevel) -> ValidationLevel:
        """Map confidence requirement to validation level"""

        if confidence in [ConfidenceLevel.ABSOLUTE, ConfidenceLevel.VERY_HIGH]:
            return ValidationLevel.COMPREHENSIVE
        elif confidence == ConfidenceLevel.HIGH:
            return ValidationLevel.STANDARD
        else:
            return ValidationLevel.BASIC

    def _prepare_validation_input(self, claim: MathematicalClaim) -> Dict[str, Any]:
        """Prepare input data for validation"""

        input_data = {
            "type": claim.claim_type,
            "text": claim.text,
            "mathematical_expression": claim.mathematical_expression,
            "context": claim.context
        }

        # Parse specific types of claims
        if claim.claim_type == "equation" and claim.mathematical_expression:
            if '=' in claim.mathematical_expression:
                parts = claim.mathematical_expression.split('=')
                if len(parts) == 2:
                    input_data["equation"] = f"{parts[0].strip()} - ({parts[1].strip()})"
                    input_data["variable"] = "x"  # Default variable

        elif claim.claim_type == "pid_parameter":
            # Extract PID parameters
            kp_match = re.search(r'[Kk][pP]\s*=\s*([\d\.\-]+)', claim.text)
            ki_match = re.search(r'[Kk][iI]\s*=\s*([\d\.\-]+)', claim.text)
            kd_match = re.search(r'[Kk][dD]\s*=\s*([\d\.\-]+)', claim.text)

            if kp_match:
                input_data["kp"] = float(kp_match.group(1))
            if ki_match:
                input_data["ki"] = float(ki_match.group(1))
            if kd_match:
                input_data["kd"] = float(kd_match.group(1))

        return input_data

    def _calculate_overall_confidence(self, validation_results: Dict[str, ValidationResult]) -> float:
        """Calculate overall confidence score from validation results"""

        if not validation_results:
            return 0.0

        # Weight confidence scores by validation priority and accuracy
        total_weighted_confidence = 0.0
        total_weight = 0.0

        for result in validation_results.values():
            weight = result.accuracy_score * result.confidence_score
            total_weighted_confidence += result.confidence_score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_weighted_confidence / total_weight

    def _determine_recommendation_certainty(self, confidence_score: float) -> ConfidenceLevel:
        """Determine recommendation certainty level"""

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

    async def create_educational_response(self,
                                        user_question: str,
                                        topic: str = "control_theory") -> IntegratedResponse:
        """Create comprehensive educational response with mathematical derivations"""

        # Generate educational LLM response
        educational_prompt = f"""
        Provide a comprehensive educational explanation for: {user_question}

        Focus on {topic} and include:
        1. Fundamental concepts and principles
        2. Mathematical foundations and equations
        3. Practical applications in industrial control
        4. Step-by-step derivations where applicable
        5. Common misconceptions and clarifications

        Make the explanation suitable for both learning and reference.
        """

        try:
            llm_response = await self.openai_client.chat.completions.create(
                model="ft:gpt-4o:industrial-control:20250117",  # Use fine-tuned model
                messages=[
                    {"role": "system", "content": "You are an expert in industrial control theory and automation. Provide detailed, educational explanations with mathematical rigor."},
                    {"role": "user", "content": educational_prompt}
                ],
                temperature=0.1  # Low temperature for consistent educational content
            )

            response_text = llm_response.choices[0].message.content

            # Process with educational mode
            original_mode = self.integration_mode
            self.integration_mode = IntegrationMode.EDUCATIONAL

            integrated_response = await self.process_llm_query(
                user_input=user_question,
                llm_response=response_text,
                context={"mode": "educational", "topic": topic}
            )

            # Restore original mode
            self.integration_mode = original_mode

            return integrated_response

        except Exception as e:
            logger.error(f"Failed to create educational response: {e}")
            # Return minimal error response
            return IntegratedResponse(
                response_id=f"edu_error_{uuid.uuid4().hex[:8]}",
                query_id=f"edu_{uuid.uuid4().hex[:8]}",
                original_llm_response="",
                enhanced_response=f"Error creating educational response: {str(e)}",
                mathematical_validation={},
                confidence_score=0.0,
                educational_content=[],
                derivation_steps=[],
                assumptions=[],
                limitations=["Educational response generation failed"],
                wolfram_citations=[],
                recommendation_certainty=ConfidenceLevel.VERY_LOW,
                success=False,
                execution_time=0.0
            )

    def get_session_stats(self) -> Dict[str, Any]:
        """Get integration session statistics"""

        stats = self.session_stats.copy()

        duration = datetime.now() - stats["start_time"]
        stats["session_duration"] = str(duration)

        if stats["queries_processed"] > 0:
            stats["claims_per_query"] = stats["claims_validated"] / stats["queries_processed"]
            stats["wolfram_usage_rate"] = stats["wolfram_queries"] / stats["claims_validated"] if stats["claims_validated"] > 0 else 0
            stats["high_confidence_rate"] = stats["high_confidence_results"] / stats["queries_processed"]
            stats["educational_response_rate"] = stats["educational_responses"] / stats["queries_processed"]
        else:
            stats["claims_per_query"] = 0
            stats["wolfram_usage_rate"] = 0
            stats["high_confidence_rate"] = 0
            stats["educational_response_rate"] = 0

        return stats

# Production deployment utilities

async def create_production_middleware(
    openai_api_key: str,
    wolfram_api_key: str,
    redis_url: str = "redis://localhost:6379",
    context_path: Optional[str] = None
) -> LLMWolframMiddleware:
    """Create production-ready LLM-WolframAlpha middleware"""

    # Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=openai_api_key)

    # Initialize WolframAlpha Pro client
    wolfram_client = WolframAlphaProClient(
        api_key=wolfram_api_key,
        enable_caching=True,
        cache_ttl=3600,
        rate_limit_per_minute=100
    )

    # Initialize mathematical validator
    validator = ContextAwareMathematicalValidator(
        wolfram_client=wolfram_client,
        mathematical_context_path=context_path
    )

    # Initialize Redis client
    redis_client = redis.from_url(redis_url, decode_responses=True)

    # Create middleware
    middleware = LLMWolframMiddleware(
        openai_client=openai_client,
        wolfram_client=wolfram_client,
        validator=validator,
        redis_client=redis_client,
        integration_mode=IntegrationMode.PRODUCTION
    )

    logger.info("🚀 Production LLM-WolframAlpha middleware created")
    return middleware

# Example usage and testing

async def test_llm_wolfram_integration():
    """Test LLM-WolframAlpha integration middleware"""

    # Mock clients for testing
    openai_client = None  # Would need actual API key
    wolfram_client = None  # Would need actual API key
    validator = MathematicalValidator()

    if not openai_client or not wolfram_client:
        logger.warning("Demo mode - mocking integration responses")
        return

    middleware = LLMWolframMiddleware(
        openai_client=openai_client,
        wolfram_client=wolfram_client,
        validator=validator,
        integration_mode=IntegrationMode.EDUCATIONAL
    )

    # Test mathematical claim extraction
    test_llm_response = """
    For a PID controller with Kp=1.0, Ki=0.1, and Kd=0.01, the system will be stable.
    The transfer function is G(s) = 1/(s+1), and this gives a gain margin of 20 dB.
    Performance will improve by 15% with this tuning.
    """

    # Test claim extraction
    claims = middleware.claim_extractor.extract_claims(test_llm_response)
    print(f"Extracted {len(claims)} claims:")
    for claim in claims:
        print(f"  - {claim.text} (Type: {claim.claim_type}, Priority: {claim.validation_priority})")

    # Test full integration
    integrated_response = await middleware.process_llm_query(
        user_input="How should I tune my PID controller?",
        llm_response=test_llm_response
    )

    print("\nIntegration results:")
    print(f"  Confidence: {integrated_response.confidence_score:.1%}")
    print(f"  Certainty: {integrated_response.recommendation_certainty.value}")
    print(f"  Educational content items: {len(integrated_response.educational_content)}")
    print(f"  WolframAlpha citations: {len(integrated_response.wolfram_citations)}")

    # Print session statistics
    stats = middleware.get_session_stats()
    print(f"\nSession stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_llm_wolfram_integration())
