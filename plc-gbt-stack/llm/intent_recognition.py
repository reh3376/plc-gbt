"""
Intent Recognition Engine
Phase 23.2.1: Natural Language Intent Recognition

Provides comprehensive intent recognition including task classification,
entity extraction, multi-intent handling, and ambiguity resolution for
industrial control system interactions.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from . import (
    ApplicationContext,
    IntentType,
    TaskComplexity,
)

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Types of entities that can be extracted"""
    LOOP_NAME = "loop_name"
    PARAMETER = "parameter"
    VALUE = "value"
    FILE_PATH = "file_path"
    TIME_PERIOD = "time_period"
    CONTROLLER_TYPE = "controller_type"
    TUNING_METHOD = "tuning_method"
    OUTPUT_FORMAT = "output_format"
    OPERATION_TARGET = "operation_target"
    COMPARISON_METRIC = "comparison_metric"

class ConfidenceLevel(Enum):
    """Confidence levels for intent recognition"""
    VERY_LOW = "very_low"     # < 0.3
    LOW = "low"               # 0.3 - 0.5
    MEDIUM = "medium"         # 0.5 - 0.7
    HIGH = "high"             # 0.7 - 0.85
    VERY_HIGH = "very_high"   # > 0.85

class AmbiguityType(Enum):
    """Types of ambiguity in user input"""
    MULTIPLE_INTENTS = "multiple_intents"
    UNCLEAR_TARGET = "unclear_target"
    MISSING_PARAMETERS = "missing_parameters"
    CONFLICTING_ACTIONS = "conflicting_actions"
    VAGUE_SPECIFICATION = "vague_specification"

@dataclass
class ExtractedEntity:
    """Individual extracted entity"""
    entity_type: EntityType
    value: str
    confidence: float
    position: Tuple[int, int]  # Start and end position in text
    context: str = ""
    alternatives: List[str] = field(default_factory=list)

@dataclass
class IntentCandidate:
    """Candidate intent with confidence score"""
    intent_type: IntentType
    confidence: float
    entities: Dict[EntityType, List[ExtractedEntity]] = field(default_factory=dict)
    reasoning: str = ""
    required_clarification: List[str] = field(default_factory=list)

@dataclass
class AmbiguityResolution:
    """Ambiguity detection and resolution suggestions"""
    ambiguity_type: AmbiguityType
    confidence: float
    description: str
    clarification_questions: List[str]
    suggested_actions: List[str] = field(default_factory=list)
    context_hints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntentRecognitionResult:
    """Complete intent recognition result"""
    primary_intent: IntentCandidate
    alternative_intents: List[IntentCandidate] = field(default_factory=list)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    entities: Dict[EntityType, List[ExtractedEntity]] = field(default_factory=dict)
    ambiguities: List[AmbiguityResolution] = field(default_factory=list)
    requires_clarification: bool = False
    clarification_message: Optional[str] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class EntityExtractor:
    """Extracts entities from natural language text"""

    def __init__(self):
        self.patterns = {
            EntityType.LOOP_NAME: [
                r'\b(?:loop|controller|system)\s+(?:named\s+)?["\']?([a-zA-Z_][a-zA-Z0-9_\-]*)["\']?',
                r'\b([a-zA-Z_][a-zA-Z0-9_\-]*)\s+(?:loop|controller|pid|system)',
                r'for\s+["\']?([a-zA-Z_][a-zA-Z0-9_\-]*)["\']?',
                r'called\s+["\']?([a-zA-Z_][a-zA-Z0-9_\-]*)["\']?'
            ],
            EntityType.PARAMETER: [
                r'\b(kp|ki|kd|proportional|integral|derivative)\b',
                r'\b(setpoint|sp|pv|process[\s_]?value|output|mv|manipulated[\s_]?variable)\b',
                r'\b(bias|offset|deadband|saturation)\b',
                r'\b(sample[\s_]?time|scan[\s_]?rate|update[\s_]?rate)\b'
            ],
            EntityType.VALUE: [
                r'\b(\d+\.?\d*)\s*(?:%|percent|degrees?|psi|bar|gpm|cfm|rpm)?\b',
                r'\b(true|false|on|off|enable|disable|auto|manual)\b'
            ],
            EntityType.FILE_PATH: [
                r'["\']?([a-zA-Z]:[\\\/][^"\']*)["\']?',  # Windows paths
                r'["\']?(\/[^"\']*)["\']?',                # Unix paths
                r'["\']?([^"\']*\.(?:json|xml|csv|txt|log))["\']?'  # Files with extensions
            ],
            EntityType.TIME_PERIOD: [
                r'\b(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?)\b',
                r'\blast\s+(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?)\b',
                r'\bpast\s+(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?)\b'
            ],
            EntityType.CONTROLLER_TYPE: [
                r'\b(pid|pi|pd|fuzzy|adaptive|cascade|feedforward|mpc|model[\s_]?predictive)\b'
            ],
            EntityType.TUNING_METHOD: [
                r'\b(ziegler[\s\-]?nichols|cohen[\s\-]?coon|lambda|imc|relay|step[\s_]?response)\b',
                r'\b(auto[\s_]?tun[eig]*|manual[\s_]?tun[eig]*|optimization)\b'
            ],
            EntityType.OUTPUT_FORMAT: [
                r'\b(csv|json|xml|excel|pdf|html|markdown|txt)\b',
                r'\bas\s+(csv|json|xml|excel|pdf|html|markdown|txt)\b'
            ]
        }

    def extract_entities(self, text: str, context: ApplicationContext) -> Dict[EntityType, List[ExtractedEntity]]:
        """Extract all entities from text"""
        entities = {}
        text_lower = text.lower()

        for entity_type, patterns in self.patterns.items():
            extracted = []

            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)

                    entity = ExtractedEntity(
                        entity_type=entity_type,
                        value=value.strip(),
                        confidence=self._calculate_entity_confidence(value, entity_type, context),
                        position=(match.start(), match.end()),
                        context=text[max(0, match.start()-20):min(len(text), match.end()+20)]
                    )
                    extracted.append(entity)

            if extracted:
                # Remove duplicates and sort by confidence
                unique_entities = {}
                for entity in extracted:
                    key = entity.value.lower()
                    if key not in unique_entities or entity.confidence > unique_entities[key].confidence:
                        unique_entities[key] = entity

                entities[entity_type] = sorted(unique_entities.values(),
                                             key=lambda x: x.confidence, reverse=True)

        # Context-based entity extraction
        self._extract_context_entities(text, context, entities)

        return entities

    def _calculate_entity_confidence(self, value: str, entity_type: EntityType, context: ApplicationContext) -> float:
        """Calculate confidence for extracted entity"""
        base_confidence = 0.7

        # Adjust based on entity type
        if entity_type == EntityType.LOOP_NAME:
            # Check if loop name exists in context
            if value in context.active_schemas or any(value in op.get('name', '') for op in context.recent_operations):
                base_confidence += 0.2

        elif entity_type == EntityType.PARAMETER:
            # PID parameters have high confidence
            if value.lower() in ['kp', 'ki', 'kd', 'proportional', 'integral', 'derivative']:
                base_confidence += 0.15

        elif entity_type == EntityType.CONTROLLER_TYPE:
            # Standard controller types have high confidence
            if value.lower() in ['pid', 'pi', 'pd', 'mpc']:
                base_confidence += 0.1

        elif entity_type == EntityType.FILE_PATH:
            # Check if file extension is reasonable
            if any(ext in value.lower() for ext in ['.json', '.xml', '.csv', '.txt']):
                base_confidence += 0.1

        # Length and format adjustments
        if len(value) < 2:
            base_confidence -= 0.2
        elif len(value) > 50:
            base_confidence -= 0.1

        return min(1.0, max(0.1, base_confidence))

    def _extract_context_entities(self, text: str, context: ApplicationContext, entities: Dict):
        """Extract entities based on application context"""
        # Extract loop names from active schemas
        for schema in context.active_schemas:
            if schema.lower() in text.lower():
                if EntityType.LOOP_NAME not in entities:
                    entities[EntityType.LOOP_NAME] = []

                entity = ExtractedEntity(
                    entity_type=EntityType.LOOP_NAME,
                    value=schema,
                    confidence=0.8,
                    position=(0, 0),  # Context-derived
                    context="from_application_context"
                )
                entities[EntityType.LOOP_NAME].append(entity)

class IntentClassifier:
    """Classifies user intent from natural language"""

    def __init__(self):
        self.intent_patterns = {
            IntentType.CREATE: [
                r'\b(create|make|build|generate|new|add)\b',
                r'\bset\s+up\b',
                r'\binitializ[eig]\b'
            ],
            IntentType.MODIFY: [
                r'\b(modify|change|update|edit|alter|adjust)\b',
                r'\btune\b',
                r'\bset\s+(?!up)\b'
            ],
            IntentType.ANALYZE: [
                r'\b(analyz[eig]|check|examine|inspect|review|assess)\b',
                r'\bhow\s+(?:is|does|well)\b',
                r'\bperformance\b'
            ],
            IntentType.DELETE: [
                r'\b(delete|remove|clear|clean|purge)\b',
                r'\bget\s+rid\s+of\b'
            ],
            IntentType.QUERY: [
                r'\b(show|display|list|what|which|where|when|who)\b',
                r'\btell\s+me\b',
                r'\bget\s+(?:me\s+)?(?:the\s+)?\b'
            ],
            IntentType.OPTIMIZE: [
                r'\b(optim[ization]*|improve|enhance|better|tune|adjust)\b',
                r'\bfind\s+best\b',
                r'\bminimiz[eig]\b|\bmaximiz[eig]\b'
            ],
            IntentType.VALIDATE: [
                r'\b(validate|verify|test|check|confirm)\b',
                r'\bis\s+(?:this|it|that)\s+(?:correct|right|valid)\b'
            ],
            IntentType.EXPLAIN: [
                r'\b(explain|describe|how|why|what\s+(?:is|does|means?))\b',
                r'\btell\s+me\s+(?:about|how)\b',
                r'\bhelp\s+me\s+understand\b'
            ],
            IntentType.HELP: [
                r'\b(help|assist|guide|support)\b',
                r'\bhow\s+(?:do|can)\s+i\b',
                r'\bwhat\s+(?:can|should)\s+i\b'
            ],
            IntentType.CONFIGURE: [
                r'\b(configur[eig]|setup|install|enable|disable)\b',
                r'\bset\s+up\b',
                r'\bturn\s+(?:on|off)\b'
            ]
        }

        self.complexity_indicators = {
            TaskComplexity.SIMPLE: [
                r'\b(show|list|display|get)\b',
                r'\bone\s+(?:loop|parameter|value)\b'
            ],
            TaskComplexity.MODERATE: [
                r'\b(multiple|several|few|some)\b',
                r'\band\b.*\band\b',  # Multiple actions
                r'\b(?:create|modify|analyze)\s+.*\s(?:and|then)\b'
            ],
            TaskComplexity.COMPLEX: [
                r'\boptimiz[eig]\b',
                r'\b(?:all|every|entire)\s+(?:system|loops?)\b',
                r'\bworkflow\b|\bpipeline\b|\bprocess\b'
            ],
            TaskComplexity.EXPERT: [
                r'\b(?:advanced|expert|complex|sophisticated)\b',
                r'\bmachine\s+learning\b|\bai\b|\balgorithm\b',
                r'\bcustom\b.*\bimplementation\b'
            ]
        }

    def classify_intent(self, text: str, entities: Dict[EntityType, List[ExtractedEntity]],
                       context: ApplicationContext) -> List[IntentCandidate]:
        """Classify user intent with confidence scores"""
        text_lower = text.lower()
        candidates = []

        # Score each intent type
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            matched_patterns = []

            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += 0.3 * len(matches)
                    matched_patterns.append(pattern)

            # Context-based scoring adjustments
            score += self._calculate_context_score(intent_type, entities, context)

            # Entity consistency scoring
            score += self._calculate_entity_consistency_score(intent_type, entities)

            if score > 0.1:  # Minimum threshold
                candidate = IntentCandidate(
                    intent_type=intent_type,
                    confidence=min(1.0, score),
                    entities=entities,
                    reasoning=f"Matched patterns: {matched_patterns[:3]}"
                )

                # Determine complexity
                self._determine_complexity(text_lower, entities)

                # Add required clarifications
                clarifications = self._identify_required_clarifications(intent_type, entities, context)
                candidate.required_clarification = clarifications

                candidates.append(candidate)

        # Sort by confidence and return top candidates
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        return candidates[:5]  # Top 5 candidates

    def _calculate_context_score(self, intent_type: IntentType, entities: Dict, context: ApplicationContext) -> float:
        """Calculate context-based score adjustments"""
        score = 0.0

        # Recent operations influence
        recent_intents = [op.get('intent', '') for op in context.recent_operations[-3:]]

        if intent_type.value in recent_intents:
            score += 0.1  # Bonus for recent similar operations

        # System state influence
        system_status = context.system_state.get('status', 'unknown')

        if intent_type == IntentType.CREATE and system_status == 'ready':
            score += 0.1
        elif intent_type == IntentType.ANALYZE and 'performance' in context.performance_metrics:
            score += 0.1
        elif intent_type == IntentType.QUERY and context.active_schemas:
            score += 0.05

        return score

    def _calculate_entity_consistency_score(self, intent_type: IntentType, entities: Dict) -> float:
        """Calculate score based on entity consistency with intent"""
        score = 0.0

        # Intent-entity consistency rules
        if intent_type == IntentType.CREATE and EntityType.LOOP_NAME in entities:
            score += 0.15
        elif intent_type == IntentType.MODIFY and EntityType.PARAMETER in entities:
            score += 0.15
        elif intent_type == IntentType.ANALYZE and EntityType.LOOP_NAME in entities:
            score += 0.1
        elif intent_type == IntentType.OPTIMIZE and EntityType.TUNING_METHOD in entities:
            score += 0.15
        elif intent_type == IntentType.QUERY and EntityType.OUTPUT_FORMAT in entities:
            score += 0.1

        return score

    def _determine_complexity(self, text: str, entities: Dict) -> TaskComplexity:
        """Determine task complexity based on text and entities"""
        for complexity, patterns in self.complexity_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return complexity

        # Entity-based complexity assessment
        entity_count = sum(len(entity_list) for entity_list in entities.values())

        if entity_count > 5:
            return TaskComplexity.COMPLEX
        elif entity_count > 2:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE

    def _identify_required_clarifications(self, intent_type: IntentType, entities: Dict,
                                        context: ApplicationContext) -> List[str]:
        """Identify what clarifications are needed"""
        clarifications = []

        # Intent-specific clarification rules
        if intent_type == IntentType.CREATE:
            if EntityType.LOOP_NAME not in entities:
                clarifications.append("What should the new loop be named?")
            if EntityType.CONTROLLER_TYPE not in entities:
                clarifications.append("What type of controller (PID, fuzzy, etc.)?")

        elif intent_type == IntentType.MODIFY:
            if EntityType.LOOP_NAME not in entities and not context.active_schemas:
                clarifications.append("Which loop should be modified?")
            if EntityType.PARAMETER not in entities:
                clarifications.append("Which parameters should be changed?")

        elif intent_type == IntentType.ANALYZE:
            if EntityType.LOOP_NAME not in entities and len(context.active_schemas) > 1:
                clarifications.append("Which loop should be analyzed?")

        elif intent_type == IntentType.OPTIMIZE:
            if EntityType.TUNING_METHOD not in entities:
                clarifications.append("What tuning method should be used?")

        return clarifications

class AmbiguityResolver:
    """Resolves ambiguities in user intent"""

    def detect_ambiguities(self, text: str, candidates: List[IntentCandidate],
                          entities: Dict, context: ApplicationContext) -> List[AmbiguityResolution]:
        """Detect and provide resolution strategies for ambiguities"""
        ambiguities = []

        # Multiple high-confidence intents
        high_confidence_intents = [c for c in candidates if c.confidence > 0.7]
        if len(high_confidence_intents) > 1:
            ambiguities.append(AmbiguityResolution(
                ambiguity_type=AmbiguityType.MULTIPLE_INTENTS,
                confidence=0.8,
                description=f"Multiple possible intents detected: {[c.intent_type.value for c in high_confidence_intents]}",
                clarification_questions=[
                    f"Do you want to {high_confidence_intents[0].intent_type.value} or {high_confidence_intents[1].intent_type.value}?",
                    "Could you be more specific about what you want to do?"
                ]
            ))

        # Unclear target when multiple loops available
        if EntityType.LOOP_NAME not in entities and len(context.active_schemas) > 1:
            ambiguities.append(AmbiguityResolution(
                ambiguity_type=AmbiguityType.UNCLEAR_TARGET,
                confidence=0.9,
                description="Multiple loops available but target not specified",
                clarification_questions=[
                    f"Which loop? Available options: {', '.join(context.active_schemas[:5])}",
                    "Please specify the loop name"
                ],
                context_hints={"available_loops": context.active_schemas}
            ))

        # Missing critical parameters
        if candidates and candidates[0].required_clarification:
            ambiguities.append(AmbiguityResolution(
                ambiguity_type=AmbiguityType.MISSING_PARAMETERS,
                confidence=0.7,
                description="Required parameters are missing",
                clarification_questions=candidates[0].required_clarification
            ))

        # Vague specifications
        if self._is_vague_specification(text):
            ambiguities.append(AmbiguityResolution(
                ambiguity_type=AmbiguityType.VAGUE_SPECIFICATION,
                confidence=0.6,
                description="Request is too vague for precise action",
                clarification_questions=[
                    "Could you provide more specific details?",
                    "What exactly would you like me to do?"
                ]
            ))

        return ambiguities

    def _is_vague_specification(self, text: str) -> bool:
        """Check if the specification is too vague"""
        vague_patterns = [
            r'^(?:help|assist)(?:\s+me)?\.?$',
            r'^(?:what|how)(?:\s+about)?(?:\s+this)?\.?$',
            r'^\w{1,3}\.?$',  # Very short requests
            r'^(?:do|make|fix|handle)\s+(?:something|anything|it|this|that)\.?$'
        ]

        text_clean = text.strip().lower()
        return any(re.match(pattern, text_clean) for pattern in vague_patterns)

class IntentRecognitionEngine:
    """Main intent recognition orchestrator"""

    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()
        self.ambiguity_resolver = AmbiguityResolver()
        self.recognition_history: List[IntentRecognitionResult] = []

    def recognize_intent(self, text: str, context: ApplicationContext) -> IntentRecognitionResult:
        """Complete intent recognition pipeline"""
        start_time = time.time()

        # Extract entities
        entities = self.entity_extractor.extract_entities(text, context)

        # Classify intents
        candidates = self.intent_classifier.classify_intent(text, entities, context)

        # Detect ambiguities
        ambiguities = self.ambiguity_resolver.detect_ambiguities(text, candidates, entities, context)

        # Determine primary intent
        primary_intent = candidates[0] if candidates else IntentCandidate(
            intent_type=IntentType.HELP,
            confidence=0.3,
            reasoning="No clear intent detected, defaulting to help"
        )

        # Determine confidence level
        confidence_level = self._determine_confidence_level(primary_intent.confidence, ambiguities)

        # Check if clarification is required
        requires_clarification = (
            confidence_level in [ConfidenceLevel.VERY_LOW, ConfidenceLevel.LOW] or
            len(ambiguities) > 0 or
            len(primary_intent.required_clarification) > 0
        )

        # Generate clarification message
        clarification_message = None
        if requires_clarification:
            clarification_message = self._generate_clarification_message(
                primary_intent, ambiguities, entities, context
            )

        # Create result
        result = IntentRecognitionResult(
            primary_intent=primary_intent,
            alternative_intents=candidates[1:4] if len(candidates) > 1 else [],
            confidence_level=confidence_level,
            entities=entities,
            ambiguities=ambiguities,
            requires_clarification=requires_clarification,
            clarification_message=clarification_message,
            processing_time=time.time() - start_time,
            metadata={
                "original_text": text,
                "num_candidates": len(candidates),
                "num_entities": sum(len(e) for e in entities.values()),
                "num_ambiguities": len(ambiguities)
            }
        )

        # Store in history
        self.recognition_history.append(result)
        if len(self.recognition_history) > 100:
            self.recognition_history = self.recognition_history[-100:]

        return result

    def _determine_confidence_level(self, confidence: float, ambiguities: List) -> ConfidenceLevel:
        """Determine overall confidence level"""
        # Reduce confidence based on ambiguities
        adjusted_confidence = confidence - (len(ambiguities) * 0.1)

        if adjusted_confidence >= 0.85:
            return ConfidenceLevel.VERY_HIGH
        elif adjusted_confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif adjusted_confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif adjusted_confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _generate_clarification_message(self, primary_intent: IntentCandidate,
                                      ambiguities: List, entities: Dict,
                                      context: ApplicationContext) -> str:
        """Generate appropriate clarification message"""
        messages = []

        # Add ambiguity-specific questions
        for ambiguity in ambiguities:
            messages.extend(ambiguity.clarification_questions[:2])  # Max 2 per ambiguity

        # Add intent-specific clarifications
        messages.extend(primary_intent.required_clarification[:2])

        if not messages:
            messages = [
                "I'm not completely sure what you want to do. Could you provide more details?",
                f"I think you want to {primary_intent.intent_type.value}, but I need more information."
            ]

        # Format as a helpful response
        if len(messages) == 1:
            return f"🤔 {messages[0]}"
        else:
            return "🤔 I need some clarification:\n" + "\n".join(f"• {msg}" for msg in messages[:3])

    def get_recognition_summary(self) -> Dict[str, Any]:
        """Get summary of recognition activities"""
        if not self.recognition_history:
            return {"total_recognitions": 0}

        total = len(self.recognition_history)
        confidence_counts = {}
        for level in ConfidenceLevel:
            confidence_counts[level.value] = sum(
                1 for r in self.recognition_history if r.confidence_level == level
            )

        intent_counts = {}
        for intent_type in IntentType:
            intent_counts[intent_type.value] = sum(
                1 for r in self.recognition_history if r.primary_intent.intent_type == intent_type
            )

        avg_processing_time = sum(r.processing_time for r in self.recognition_history) / total
        clarification_rate = sum(1 for r in self.recognition_history if r.requires_clarification) / total * 100

        return {
            "total_recognitions": total,
            "confidence_distribution": confidence_counts,
            "intent_distribution": intent_counts,
            "average_processing_time": round(avg_processing_time, 3),
            "clarification_rate": round(clarification_rate, 1),
            "recent_activity": [
                {
                    "intent": r.primary_intent.intent_type.value,
                    "confidence": r.confidence_level.value,
                    "clarification_needed": r.requires_clarification
                }
                for r in self.recognition_history[-10:]
            ]
        }

# Singleton engine instance
_intent_engine: Optional[IntentRecognitionEngine] = None

def get_intent_engine() -> IntentRecognitionEngine:
    """Get singleton intent recognition engine"""
    global _intent_engine
    if _intent_engine is None:
        _intent_engine = IntentRecognitionEngine()
    return _intent_engine

def recognize_intent(text: str, context: ApplicationContext) -> IntentRecognitionResult:
    """Quick function to recognize intent"""
    engine = get_intent_engine()
    return engine.recognize_intent(text, context)

# Export main components
__all__ = [
    "EntityType",
    "ConfidenceLevel",
    "AmbiguityType",
    "ExtractedEntity",
    "IntentCandidate",
    "AmbiguityResolution",
    "IntentRecognitionResult",
    "EntityExtractor",
    "IntentClassifier",
    "AmbiguityResolver",
    "IntentRecognitionEngine",
    "get_intent_engine",
    "recognize_intent"
]
