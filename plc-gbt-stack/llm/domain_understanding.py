"""
Domain-Specific Understanding Module
Phase 23.2.4: Industrial Control Theory Domain Knowledge

Provides specialized understanding of control theory concepts, PID tuning interpretation,
performance goal understanding, and industry terminology handling for industrial control systems.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ControlConcept(Enum):
    """Core control theory concepts"""
    PID_CONTROLLER = "pid_controller"
    SETPOINT = "setpoint"
    PROCESS_VARIABLE = "process_variable"
    MANIPULATED_VARIABLE = "manipulated_variable"
    CONTROL_ERROR = "control_error"
    PROPORTIONAL_GAIN = "proportional_gain"
    INTEGRAL_TIME = "integral_time"
    DERIVATIVE_TIME = "derivative_time"
    DEADBAND = "deadband"
    SATURATION = "saturation"
    WINDUP = "windup"
    STABILITY = "stability"
    OSCILLATION = "oscillation"
    OVERSHOOT = "overshoot"
    SETTLING_TIME = "settling_time"
    RISE_TIME = "rise_time"
    STEADY_STATE_ERROR = "steady_state_error"

class TuningMethod(Enum):
    """PID tuning methodologies"""
    ZIEGLER_NICHOLS = "ziegler_nichols"
    COHEN_COON = "cohen_coon"
    LAMBDA_TUNING = "lambda_tuning"
    IMC_TUNING = "imc_tuning"
    RELAY_FEEDBACK = "relay_feedback"
    STEP_RESPONSE = "step_response"
    FREQUENCY_RESPONSE = "frequency_response"
    MANUAL_TUNING = "manual_tuning"
    AUTO_TUNING = "auto_tuning"

class PerformanceGoal(Enum):
    """Common performance optimization goals"""
    MINIMIZE_OVERSHOOT = "minimize_overshoot"
    MINIMIZE_SETTLING_TIME = "minimize_settling_time"
    MINIMIZE_STEADY_STATE_ERROR = "minimize_steady_state_error"
    MAXIMIZE_STABILITY = "maximize_stability"
    MINIMIZE_OSCILLATION = "minimize_oscillation"
    IMPROVE_DISTURBANCE_REJECTION = "improve_disturbance_rejection"
    REDUCE_ENERGY_CONSUMPTION = "reduce_energy_consumption"
    INCREASE_THROUGHPUT = "increase_throughput"
    MAINTAIN_CONSISTENCY = "maintain_consistency"

class IndustryDomain(Enum):
    """Industrial application domains"""
    CHEMICAL_PROCESS = "chemical_process"
    POWER_GENERATION = "power_generation"
    WATER_TREATMENT = "water_treatment"
    OIL_GAS = "oil_gas"
    MANUFACTURING = "manufacturing"
    FOOD_BEVERAGE = "food_beverage"
    PHARMACEUTICAL = "pharmaceutical"
    PULP_PAPER = "pulp_paper"
    METALS_MINING = "metals_mining"
    HVAC = "hvac"

@dataclass
class ConceptDefinition:
    """Definition of a control theory concept"""
    concept: ControlConcept
    name: str
    definition: str
    synonyms: List[str] = field(default_factory=list)
    units: List[str] = field(default_factory=list)
    typical_ranges: Dict[str, Any] = field(default_factory=dict)
    related_concepts: List[ControlConcept] = field(default_factory=list)
    industry_specific: Dict[IndustryDomain, str] = field(default_factory=dict)

@dataclass
class TuningMethodInfo:
    """Information about PID tuning methods"""
    method: TuningMethod
    name: str
    description: str
    advantages: List[str] = field(default_factory=list)
    disadvantages: List[str] = field(default_factory=list)
    best_for: List[str] = field(default_factory=list)
    parameters_needed: List[str] = field(default_factory=list)
    typical_applications: List[IndustryDomain] = field(default_factory=list)

@dataclass
class PerformanceGoalInfo:
    """Information about performance optimization goals"""
    goal: PerformanceGoal
    name: str
    description: str
    metrics: List[str] = field(default_factory=list)
    typical_constraints: List[str] = field(default_factory=list)
    tuning_emphasis: Dict[str, str] = field(default_factory=dict)  # parameter -> emphasis
    industry_relevance: Dict[IndustryDomain, float] = field(default_factory=dict)

@dataclass
class IndustryTerminology:
    """Industry-specific terminology"""
    domain: IndustryDomain
    terms: Dict[str, str] = field(default_factory=dict)  # term -> definition
    units: Dict[str, str] = field(default_factory=dict)  # parameter -> typical unit
    typical_processes: List[str] = field(default_factory=list)
    common_variables: List[str] = field(default_factory=list)
    regulatory_standards: List[str] = field(default_factory=list)

@dataclass
class DomainContext:
    """Context about the specific industrial domain"""
    primary_domain: IndustryDomain
    process_type: str
    key_variables: List[str] = field(default_factory=list)
    performance_priorities: List[PerformanceGoal] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    safety_considerations: List[str] = field(default_factory=list)

class ConceptRecognizer:
    """Recognizes control theory concepts in natural language"""

    def __init__(self):
        self.concept_definitions = self._initialize_concept_definitions()
        self.concept_patterns = self._build_concept_patterns()

    def _initialize_concept_definitions(self) -> Dict[ControlConcept, ConceptDefinition]:
        """Initialize comprehensive concept definitions"""
        return {
            ControlConcept.PID_CONTROLLER: ConceptDefinition(
                concept=ControlConcept.PID_CONTROLLER,
                name="PID Controller",
                definition="Proportional-Integral-Derivative controller that calculates control action based on error",
                synonyms=["pid", "proportional integral derivative", "three-term controller"],
                related_concepts=[ControlConcept.PROPORTIONAL_GAIN, ControlConcept.INTEGRAL_TIME, ControlConcept.DERIVATIVE_TIME]
            ),
            ControlConcept.SETPOINT: ConceptDefinition(
                concept=ControlConcept.SETPOINT,
                name="Setpoint",
                definition="Desired value for the process variable",
                synonyms=["sp", "target", "reference", "desired value", "set value"],
                units=["°C", "°F", "bar", "psi", "gpm", "lpm", "%"]
            ),
            ControlConcept.PROCESS_VARIABLE: ConceptDefinition(
                concept=ControlConcept.PROCESS_VARIABLE,
                name="Process Variable",
                definition="Measured value of the controlled process parameter",
                synonyms=["pv", "measured value", "actual value", "feedback"],
                units=["°C", "°F", "bar", "psi", "gpm", "lpm", "%"]
            ),
            ControlConcept.MANIPULATED_VARIABLE: ConceptDefinition(
                concept=ControlConcept.MANIPULATED_VARIABLE,
                name="Manipulated Variable",
                definition="Controller output that adjusts the process",
                synonyms=["mv", "control output", "output", "control signal"],
                units=["%", "mA", "V", "gpm", "cfm"],
                typical_ranges={"percentage": "0-100%", "current": "4-20mA", "voltage": "0-10V"}
            ),
            ControlConcept.PROPORTIONAL_GAIN: ConceptDefinition(
                concept=ControlConcept.PROPORTIONAL_GAIN,
                name="Proportional Gain",
                definition="Controller gain that determines response proportional to error",
                synonyms=["kp", "proportional constant", "p-gain", "gain"],
                typical_ranges={"low": "0.1-1.0", "medium": "1.0-10.0", "high": "10.0-100.0"}
            ),
            ControlConcept.INTEGRAL_TIME: ConceptDefinition(
                concept=ControlConcept.INTEGRAL_TIME,
                name="Integral Time",
                definition="Time constant for integral action to eliminate steady-state error",
                synonyms=["ti", "reset time", "integral constant", "i-time"],
                units=["seconds", "minutes"],
                typical_ranges={"fast": "1-60 seconds", "medium": "1-10 minutes", "slow": "10-60 minutes"}
            ),
            ControlConcept.DERIVATIVE_TIME: ConceptDefinition(
                concept=ControlConcept.DERIVATIVE_TIME,
                name="Derivative Time",
                definition="Time constant for derivative action to anticipate future error",
                synonyms=["td", "rate time", "derivative constant", "d-time"],
                units=["seconds", "minutes"],
                typical_ranges={"short": "0.1-1 second", "medium": "1-10 seconds", "long": "10-60 seconds"}
            ),
            ControlConcept.OVERSHOOT: ConceptDefinition(
                concept=ControlConcept.OVERSHOOT,
                name="Overshoot",
                definition="Maximum peak value above setpoint during transient response",
                synonyms=["peak overshoot", "maximum overshoot", "overshoot percentage"],
                units=["%", "absolute units"],
                typical_ranges={"acceptable": "0-10%", "moderate": "10-25%", "excessive": ">25%"}
            ),
            ControlConcept.SETTLING_TIME: ConceptDefinition(
                concept=ControlConcept.SETTLING_TIME,
                name="Settling Time",
                definition="Time for response to stay within specified band around setpoint",
                synonyms=["settling time", "stabilization time"],
                units=["seconds", "minutes"],
                typical_ranges={"fast": "<30 seconds", "medium": "30-300 seconds", "slow": ">300 seconds"}
            )
        }

    def _build_concept_patterns(self) -> Dict[ControlConcept, List[str]]:
        """Build regex patterns for concept recognition"""
        patterns = {}

        for concept, definition in self.concept_definitions.items():
            concept_patterns = []

            # Add main name pattern
            name_words = definition.name.lower().split()
            concept_patterns.append(r'\b' + r'\s*'.join(name_words) + r'\b')

            # Add synonym patterns
            for synonym in definition.synonyms:
                if len(synonym) > 2:  # Avoid very short patterns
                    concept_patterns.append(r'\b' + re.escape(synonym.lower()) + r'\b')

            patterns[concept] = concept_patterns

        return patterns

    def recognize_concepts(self, text: str) -> Dict[ControlConcept, float]:
        """Recognize control theory concepts in text"""
        text_lower = text.lower()
        recognized_concepts = {}

        for concept, patterns in self.concept_patterns.items():
            max_confidence = 0.0

            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    # Calculate confidence based on pattern specificity and frequency
                    confidence = min(1.0, len(matches) * 0.3 + 0.4)
                    if len(pattern) > 10:  # Longer patterns get bonus
                        confidence += 0.1
                    max_confidence = max(max_confidence, confidence)

            if max_confidence > 0.2:
                recognized_concepts[concept] = max_confidence

        return recognized_concepts

class TuningMethodInterpreter:
    """Interprets PID tuning methods and recommendations"""

    def __init__(self):
        self.tuning_methods = self._initialize_tuning_methods()
        self.method_patterns = self._build_method_patterns()

    def _initialize_tuning_methods(self) -> Dict[TuningMethod, TuningMethodInfo]:
        """Initialize tuning method information"""
        return {
            TuningMethod.ZIEGLER_NICHOLS: TuningMethodInfo(
                method=TuningMethod.ZIEGLER_NICHOLS,
                name="Ziegler-Nichols",
                description="Classic tuning method based on ultimate gain and period",
                advantages=["Well-established", "Works for many processes", "Simple to apply"],
                disadvantages=["Can be aggressive", "May cause overshoot", "Not optimal for all processes"],
                best_for=["General purpose", "Unknown processes", "Initial tuning"],
                parameters_needed=["Ultimate gain", "Ultimate period"],
                typical_applications=[IndustryDomain.CHEMICAL_PROCESS, IndustryDomain.MANUFACTURING]
            ),
            TuningMethod.COHEN_COON: TuningMethodInfo(
                method=TuningMethod.COHEN_COON,
                name="Cohen-Coon",
                description="Tuning method for processes with significant dead time",
                advantages=["Good for dead time processes", "Better stability", "Less oscillatory"],
                disadvantages=["Requires process model", "More complex", "Slower response"],
                best_for=["High dead time processes", "Temperature control", "Flow control"],
                parameters_needed=["Process gain", "Time constant", "Dead time"],
                typical_applications=[IndustryDomain.CHEMICAL_PROCESS, IndustryDomain.POWER_GENERATION]
            ),
            TuningMethod.LAMBDA_TUNING: TuningMethodInfo(
                method=TuningMethod.LAMBDA_TUNING,
                name="Lambda Tuning",
                description="Tuning based on desired closed-loop time constant",
                advantages=["Predictable response", "Good stability", "Adjustable aggressiveness"],
                disadvantages=["Requires process model", "May be conservative", "Complex calculation"],
                best_for=["Precise control", "Stable response", "Known processes"],
                parameters_needed=["Process model", "Desired time constant"],
                typical_applications=[IndustryDomain.PHARMACEUTICAL, IndustryDomain.FOOD_BEVERAGE]
            ),
            TuningMethod.AUTO_TUNING: TuningMethodInfo(
                method=TuningMethod.AUTO_TUNING,
                name="Auto-Tuning",
                description="Automated tuning using built-in algorithms",
                advantages=["Automatic", "No manual calculation", "Adaptive"],
                disadvantages=["May not be optimal", "Limited to built-in methods", "Process dependent"],
                best_for=["Quick setup", "Unknown processes", "Non-critical applications"],
                parameters_needed=["Process response"],
                typical_applications=[IndustryDomain.HVAC, IndustryDomain.MANUFACTURING]
            )
        }

    def _build_method_patterns(self) -> Dict[TuningMethod, List[str]]:
        """Build patterns for tuning method recognition"""
        patterns = {}

        for method, info in self.tuning_methods.items():
            method_patterns = []

            # Add method name patterns
            name_variations = [
                info.name.lower(),
                info.name.lower().replace('-', ' '),
                info.name.lower().replace(' ', ''),
                method.value.replace('_', ' '),
                method.value.replace('_', '-')
            ]

            for variation in name_variations:
                method_patterns.append(r'\b' + re.escape(variation) + r'\b')

            patterns[method] = method_patterns

        return patterns

    def identify_tuning_method(self, text: str) -> Dict[TuningMethod, float]:
        """Identify mentioned tuning methods"""
        text_lower = text.lower()
        identified_methods = {}

        for method, patterns in self.method_patterns.items():
            max_confidence = 0.0

            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.8
                    # Boost confidence if method is explicitly mentioned with tuning context
                    if any(word in text_lower for word in ['tuning', 'method', 'algorithm', 'approach']):
                        confidence += 0.1
                    max_confidence = max(max_confidence, confidence)

            if max_confidence > 0.3:
                identified_methods[method] = max_confidence

        return identified_methods

    def recommend_tuning_method(self, process_characteristics: Dict[str, Any],
                               domain: IndustryDomain) -> List[Tuple[TuningMethod, float, str]]:
        """Recommend tuning methods based on process characteristics"""
        recommendations = []

        # Analyze process characteristics
        has_dead_time = process_characteristics.get('dead_time', 0) > 0
        is_fast_process = process_characteristics.get('time_constant', 60) < 30
        requires_precision = process_characteristics.get('precision_required', False)
        is_stable_process = process_characteristics.get('stability', 'unknown') == 'stable'

        # Generate recommendations
        for method, info in self.tuning_methods.items():
            score = 0.5  # Base score
            reasons = []

            # Domain-specific scoring
            if domain in info.typical_applications:
                score += 0.2
                reasons.append(f"Well-suited for {domain.value} applications")

            # Process characteristic scoring
            if has_dead_time and method == TuningMethod.COHEN_COON:
                score += 0.3
                reasons.append("Excellent for processes with dead time")
            elif not has_dead_time and method == TuningMethod.ZIEGLER_NICHOLS:
                score += 0.2
                reasons.append("Good for general processes without significant dead time")

            if requires_precision and method == TuningMethod.LAMBDA_TUNING:
                score += 0.2
                reasons.append("Provides precise, predictable control")

            if not is_stable_process and method == TuningMethod.AUTO_TUNING:
                score += 0.1
                reasons.append("Safe option for unknown process behavior")

            if is_fast_process and method == TuningMethod.ZIEGLER_NICHOLS:
                score += 0.1
                reasons.append("Works well for fast-responding processes")

            recommendation_reason = "; ".join(reasons) if reasons else "General applicability"
            recommendations.append((method, min(1.0, score), recommendation_reason))

        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:3]

class PerformanceGoalInterpreter:
    """Interprets performance optimization goals"""

    def __init__(self):
        self.performance_goals = self._initialize_performance_goals()
        self.goal_patterns = self._build_goal_patterns()

    def _initialize_performance_goals(self) -> Dict[PerformanceGoal, PerformanceGoalInfo]:
        """Initialize performance goal information"""
        return {
            PerformanceGoal.MINIMIZE_OVERSHOOT: PerformanceGoalInfo(
                goal=PerformanceGoal.MINIMIZE_OVERSHOOT,
                name="Minimize Overshoot",
                description="Reduce or eliminate overshoot in system response",
                metrics=["Peak overshoot percentage", "Maximum deviation"],
                typical_constraints=["Settling time may increase", "Response may be slower"],
                tuning_emphasis={"kp": "reduce", "kd": "increase", "ki": "careful"}
            ),
            PerformanceGoal.MINIMIZE_SETTLING_TIME: PerformanceGoalInfo(
                goal=PerformanceGoal.MINIMIZE_SETTLING_TIME,
                name="Minimize Settling Time",
                description="Reduce time to reach and stay within setpoint tolerance",
                metrics=["Settling time", "2% settling time", "5% settling time"],
                typical_constraints=["May increase overshoot", "Can reduce stability margin"],
                tuning_emphasis={"kp": "increase", "ki": "increase", "kd": "optimize"}
            ),
            PerformanceGoal.MAXIMIZE_STABILITY: PerformanceGoalInfo(
                goal=PerformanceGoal.MAXIMIZE_STABILITY,
                name="Maximize Stability",
                description="Ensure robust, stable operation under varying conditions",
                metrics=["Gain margin", "Phase margin", "Stability index"],
                typical_constraints=["Response may be slower", "Less aggressive tuning"],
                tuning_emphasis={"kp": "conservative", "ki": "reduce", "kd": "careful"}
            ),
            PerformanceGoal.IMPROVE_DISTURBANCE_REJECTION: PerformanceGoalInfo(
                goal=PerformanceGoal.IMPROVE_DISTURBANCE_REJECTION,
                name="Improve Disturbance Rejection",
                description="Better response to external disturbances and load changes",
                metrics=["Disturbance recovery time", "Maximum deviation from setpoint"],
                typical_constraints=["May affect setpoint tracking", "Increased controller activity"],
                tuning_emphasis={"ki": "increase", "kp": "moderate", "kd": "increase"}
            )
        }

    def _build_goal_patterns(self) -> Dict[PerformanceGoal, List[str]]:
        """Build patterns for goal recognition"""
        patterns = {
            PerformanceGoal.MINIMIZE_OVERSHOOT: [
                r'\b(reduce|minimize|eliminate|avoid|prevent)\s+overshoot\b',
                r'\bno\s+overshoot\b',
                r'\bless\s+overshoot\b'
            ],
            PerformanceGoal.MINIMIZE_SETTLING_TIME: [
                r'\b(reduce|minimize|faster|quick|speed up)\s+(settling|stabilization)\s+time\b',
                r'\bfaster\s+(response|settling)\b',
                r'\bquick\s+settling\b'
            ],
            PerformanceGoal.MAXIMIZE_STABILITY: [
                r'\b(improve|increase|maximize|ensure)\s+stability\b',
                r'\bmore\s+stable\b',
                r'\bstable\s+(operation|response|behavior)\b'
            ],
            PerformanceGoal.IMPROVE_DISTURBANCE_REJECTION: [
                r'\b(improve|better)\s+(disturbance|load)\s+(rejection|response)\b',
                r'\bhandle\s+(disturbances|variations)\b',
                r'\breject\s+disturbances\b'
            ]
        }
        return patterns

    def identify_performance_goals(self, text: str) -> Dict[PerformanceGoal, float]:
        """Identify performance goals from text"""
        text_lower = text.lower()
        identified_goals = {}

        for goal, patterns in self.goal_patterns.items():
            max_confidence = 0.0

            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.8
                    # Boost confidence if explicitly mentioned with optimization context
                    if any(word in text_lower for word in ['optimize', 'improve', 'enhance', 'better']):
                        confidence += 0.1
                    max_confidence = max(max_confidence, confidence)

            if max_confidence > 0.3:
                identified_goals[goal] = max_confidence

        return identified_goals

class IndustryTerminologyManager:
    """Manages industry-specific terminology and context"""

    def __init__(self):
        self.industry_terminology = self._initialize_industry_terminology()

    def _initialize_industry_terminology(self) -> Dict[IndustryDomain, IndustryTerminology]:
        """Initialize industry-specific terminology"""
        return {
            IndustryDomain.CHEMICAL_PROCESS: IndustryTerminology(
                domain=IndustryDomain.CHEMICAL_PROCESS,
                terms={
                    "reactor": "Vessel where chemical reactions occur",
                    "distillation": "Separation process based on boiling points",
                    "reflux": "Return of condensed vapor to distillation column",
                    "reboiler": "Heat exchanger providing vapor for distillation",
                    "condenser": "Heat exchanger condensing vapor to liquid"
                },
                units={
                    "temperature": "°C",
                    "pressure": "bar",
                    "flow": "m³/h",
                    "level": "%"
                },
                typical_processes=["Distillation", "Reaction", "Separation", "Crystallization"],
                common_variables=["Temperature", "Pressure", "Flow rate", "Level", "Concentration"],
                regulatory_standards=["ASME", "API", "NFPA"]
            ),
            IndustryDomain.POWER_GENERATION: IndustryTerminology(
                domain=IndustryDomain.POWER_GENERATION,
                terms={
                    "turbine": "Rotating machine converting fluid energy to mechanical energy",
                    "boiler": "Pressure vessel generating steam",
                    "condenser": "Heat exchanger condensing steam back to water",
                    "feedwater": "Water supplied to boiler",
                    "load dispatch": "Distribution of power generation among units"
                },
                units={
                    "power": "MW",
                    "frequency": "Hz",
                    "voltage": "kV",
                    "temperature": "°C",
                    "pressure": "bar"
                },
                typical_processes=["Steam generation", "Power generation", "Load balancing"],
                common_variables=["Power output", "Steam temperature", "Steam pressure", "Frequency"],
                regulatory_standards=["IEEE", "NERC", "IEC"]
            ),
            IndustryDomain.WATER_TREATMENT: IndustryTerminology(
                domain=IndustryDomain.WATER_TREATMENT,
                terms={
                    "clarifier": "Tank for settling suspended solids",
                    "flocculation": "Process of forming flocs from fine particles",
                    "disinfection": "Process of killing pathogens",
                    "backwash": "Reverse flow cleaning of filters",
                    "sludge": "Semi-solid byproduct of treatment"
                },
                units={
                    "flow": "MGD",
                    "turbidity": "NTU",
                    "ph": "pH units",
                    "chlorine": "mg/L"
                },
                typical_processes=["Coagulation", "Sedimentation", "Filtration", "Disinfection"],
                common_variables=["Flow rate", "pH", "Turbidity", "Chlorine residual"],
                regulatory_standards=["EPA", "AWWA", "NSF"]
            )
        }

    def identify_industry_domain(self, text: str) -> Dict[IndustryDomain, float]:
        """Identify likely industry domain from text"""
        text_lower = text.lower()
        domain_scores = {}

        for domain, terminology in self.industry_terminology.items():
            score = 0.0

            # Check for domain-specific terms
            for term in terminology.terms.keys():
                if term in text_lower:
                    score += 0.3

            # Check for typical processes
            for process in terminology.typical_processes:
                if process.lower() in text_lower:
                    score += 0.2

            # Check for common variables
            for variable in terminology.common_variables:
                if variable.lower() in text_lower:
                    score += 0.1

            if score > 0.1:
                domain_scores[domain] = min(1.0, score)

        return domain_scores

    def get_domain_context(self, domain: IndustryDomain, specific_terms: List[str] = None) -> DomainContext:
        """Get comprehensive domain context"""
        terminology = self.industry_terminology.get(domain)
        if not terminology:
            return DomainContext(primary_domain=domain, process_type="unknown")

        # Determine process type based on specific terms
        process_type = "general"
        if specific_terms:
            for term in specific_terms:
                if term.lower() in terminology.typical_processes[0].lower():
                    process_type = terminology.typical_processes[0]
                    break

        return DomainContext(
            primary_domain=domain,
            process_type=process_type,
            key_variables=terminology.common_variables[:5],
            performance_priorities=[
                PerformanceGoal.MAXIMIZE_STABILITY,
                PerformanceGoal.MINIMIZE_SETTLING_TIME
            ],
            constraints=["Regulatory compliance", "Safety requirements", "Environmental limits"],
            safety_considerations=["Process safety", "Equipment protection", "Environmental protection"]
        )

class DomainUnderstandingEngine:
    """Main orchestrator for domain-specific understanding"""

    def __init__(self):
        self.concept_recognizer = ConceptRecognizer()
        self.tuning_interpreter = TuningMethodInterpreter()
        self.goal_interpreter = PerformanceGoalInterpreter()
        self.terminology_manager = IndustryTerminologyManager()

    def analyze_domain_content(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive domain analysis of text content"""
        # Recognize control concepts
        concepts = self.concept_recognizer.recognize_concepts(text)

        # Identify tuning methods
        tuning_methods = self.tuning_interpreter.identify_tuning_method(text)

        # Identify performance goals
        performance_goals = self.goal_interpreter.identify_performance_goals(text)

        # Identify industry domain
        industry_domains = self.terminology_manager.identify_industry_domain(text)

        # Get domain context if domain is identified
        domain_context = None
        if industry_domains:
            primary_domain = max(industry_domains.items(), key=lambda x: x[1])[0]
            domain_context = self.terminology_manager.get_domain_context(primary_domain)

        return {
            "control_concepts": {concept.value: confidence for concept, confidence in concepts.items()},
            "tuning_methods": {method.value: confidence for method, confidence in tuning_methods.items()},
            "performance_goals": {goal.value: confidence for goal, confidence in performance_goals.items()},
            "industry_domains": {domain.value: confidence for domain, confidence in industry_domains.items()},
            "domain_context": domain_context,
            "analysis_confidence": self._calculate_overall_confidence(concepts, tuning_methods, performance_goals, industry_domains)
        }

    def _calculate_overall_confidence(self, concepts: Dict, tuning_methods: Dict,
                                    performance_goals: Dict, industry_domains: Dict) -> float:
        """Calculate overall confidence in domain understanding"""
        total_items = len(concepts) + len(tuning_methods) + len(performance_goals) + len(industry_domains)

        if total_items == 0:
            return 0.0

        total_confidence = (
            sum(concepts.values()) +
            sum(tuning_methods.values()) +
            sum(performance_goals.values()) +
            sum(industry_domains.values())
        )

        return min(1.0, total_confidence / total_items)

    def provide_domain_guidance(self, concepts: List[ControlConcept],
                               domain: Optional[IndustryDomain] = None) -> Dict[str, Any]:
        """Provide educational guidance on domain concepts"""
        guidance = {
            "concept_explanations": {},
            "related_concepts": [],
            "industry_applications": {},
            "best_practices": []
        }

        for concept in concepts:
            if concept in self.concept_recognizer.concept_definitions:
                definition = self.concept_recognizer.concept_definitions[concept]
                guidance["concept_explanations"][concept.value] = {
                    "definition": definition.definition,
                    "synonyms": definition.synonyms,
                    "typical_ranges": definition.typical_ranges
                }

                # Add related concepts
                for related in definition.related_concepts:
                    if related not in concepts:
                        guidance["related_concepts"].append(related.value)

        if domain:
            terminology = self.terminology_manager.industry_terminology.get(domain)
            if terminology:
                guidance["industry_applications"] = terminology.terms
                guidance["best_practices"] = [
                    f"Follow {std} standards" for std in terminology.regulatory_standards
                ]

        return guidance

# Singleton engine instance
_domain_engine: Optional[DomainUnderstandingEngine] = None

def get_domain_engine() -> DomainUnderstandingEngine:
    """Get singleton domain understanding engine"""
    global _domain_engine
    if _domain_engine is None:
        _domain_engine = DomainUnderstandingEngine()
    return _domain_engine

def analyze_domain_content(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Quick function to analyze domain content"""
    engine = get_domain_engine()
    return engine.analyze_domain_content(text, context)

# Export main components
__all__ = [
    "ControlConcept",
    "TuningMethod",
    "PerformanceGoal",
    "IndustryDomain",
    "ConceptDefinition",
    "TuningMethodInfo",
    "PerformanceGoalInfo",
    "IndustryTerminology",
    "DomainContext",
    "ConceptRecognizer",
    "TuningMethodInterpreter",
    "PerformanceGoalInterpreter",
    "IndustryTerminologyManager",
    "DomainUnderstandingEngine",
    "get_domain_engine",
    "analyze_domain_content"
]
