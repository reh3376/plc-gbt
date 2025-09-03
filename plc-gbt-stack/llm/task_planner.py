#!/usr/bin/env python3
"""
Phase 23.3: Task Planner
========================

Intelligent task planning system that converts natural language requests into
structured, executable task plans. Integrates with Phase 23.2 Natural Language
Understanding components to provide comprehensive task decomposition and planning.

This module analyzes natural language intents and generates detailed execution
plans with safety considerations, dependency management, and error recovery
strategies.

Components:
- TaskPlanner: Core planning engine with LLM integration
- PlanTemplate: Reusable templates for common task patterns
- DependencyAnalyzer: Intelligent dependency detection and ordering
- SafetyAnalyzer: Risk assessment and safety scoring
- PlanOptimizer: Task plan optimization and efficiency improvements

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 23.3 - Task Planner
Methodology: AI Task Orchestrator Guide
"""

import asyncio
import logging
import re
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Optional

# Import Phase 23.1 and 23.2 components
try:
    from . import ApplicationContext
    from .command_generator import CommandGenerator
    from .domain_understanding import DomainUnderstandingEngine
    from .intent_recognition import IntentRecognitionEngine, IntentRecognitionResult
    from .safety import SafetyValidator
    from .service import LLMService
    # Avoid circular import - import TaskExecutor classes locally where needed
except ImportError as e:
    # Fallback for testing
    logging.warning(f"Import error: {e}. Using mock implementations for testing.")

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class PlanTemplate:
    """Reusable template for common task patterns"""
    name: str
    description: str
    intent_patterns: List[str]
    step_templates: List[Dict[str, Any]]
    safety_level: int = 2
    estimated_duration_minutes: int = 5
    requires_approval: bool = False

    def matches_intent(self, intent: str, entities: Dict[str, Any]) -> float:
        """Calculate match score for this template against an intent"""
        match_score = 0.0

        for pattern in self.intent_patterns:
            if re.search(pattern.lower(), intent.lower()):
                match_score += 1.0

        # Normalize score
        return match_score / len(self.intent_patterns) if self.intent_patterns else 0.0

class DependencyAnalyzer:
    """Analyzes and orders task steps based on dependencies"""

    def __init__(self):
        self.dependency_rules = {
            "data_loading": ["validation", "safety_check"],
            "analysis": ["data_loading", "validation"],
            "reporting": ["analysis"],
            "schema_creation": ["validation"],
            "schema_deletion": ["safety_check", "user_confirmation"],
            "file_writing": ["validation", "safety_check"],
            "database_modification": ["safety_check", "user_confirmation"]
        }

    def analyze_dependencies(self, steps: List) -> List:
        """Analyze and reorder steps based on dependencies"""
        # Create dependency graph
        step_map = {step.step_id: step for step in steps}
        dependency_graph = {}

        for step in steps:
            dependencies = self._determine_dependencies(step, steps)
            dependency_graph[step.step_id] = dependencies
            step.dependencies = dependencies

        # Topological sort to determine execution order
        ordered_steps = self._topological_sort(dependency_graph, step_map)

        logger.debug(f"Reordered {len(steps)} steps based on dependencies")
        return ordered_steps

    def _determine_dependencies(self, step, all_steps: List) -> List[str]:
        """Determine dependencies for a single step"""
        dependencies = []
        step_category = self._categorize_step(step)

        # Check rule-based dependencies
        if step_category in self.dependency_rules:
            required_categories = self.dependency_rules[step_category]

            for other_step in all_steps:
                if other_step.step_id == step.step_id:
                    continue

                other_category = self._categorize_step(other_step)
                if other_category in required_categories:
                    dependencies.append(other_step.step_id)

        # Check data flow dependencies
        if "analyze" in step.description.lower():
            for other_step in all_steps:
                if "load" in other_step.description.lower() or "ingest" in other_step.description.lower():
                    dependencies.append(other_step.step_id)

        # Check validation dependencies
        if step.safety_level >= 3:
            for other_step in all_steps:
                if other_step.step_type == StepType.SAFETY_CHECK:
                    dependencies.append(other_step.step_id)

        return list(set(dependencies))  # Remove duplicates

    def _categorize_step(self, step) -> str:
        """Categorize a step for dependency analysis"""
        description = step.description.lower()
        command = step.command.lower()

        if "load" in description or "ingest" in description:
            return "data_loading"
        elif "analyze" in description or "analysis" in description:
            return "analysis"
        elif "report" in description or "generate" in description:
            return "reporting"
        elif "create" in description and "schema" in description:
            return "schema_creation"
        elif "delete" in description and "schema" in description:
            return "schema_deletion"
        elif "write" in description or "create" in description:
            return "file_writing"
        elif "database" in command or "db" in command:
            return "database_modification"
        elif step.step_type == StepType.VALIDATION:
            return "validation"
        elif step.step_type == StepType.SAFETY_CHECK:
            return "safety_check"
        else:
            return "generic"

    def _topological_sort(self, graph: Dict[str, List[str]], step_map: Dict[str, Any]) -> List:
        """Perform topological sort on dependency graph"""
        # Calculate in-degree for each node
        in_degree = dict.fromkeys(graph, 0)
        for node in graph:
            for dependency in graph[node]:
                if dependency in in_degree:
                    in_degree[dependency] += 1

        # Find nodes with no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(step_map[node])

            # Update in-degree for dependent nodes
            for dependent in graph:
                if node in graph[dependent]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        # Check for circular dependencies
        if len(result) != len(graph):
            logger.warning("Circular dependencies detected, using original order")
            return list(step_map.values())

        return result

class SafetyAnalyzer:
    """Analyzes task plans for safety risks and assigns safety scores"""

    def __init__(self):
        self.high_risk_patterns = [
            r'delete|remove|drop|truncate',
            r'format|wipe|clear',
            r'shutdown|restart|reboot',
            r'modify.*production',
            r'change.*safety.*setting',
            r'disable.*alarm',
            r'override.*interlock'
        ]

        self.medium_risk_patterns = [
            r'create|add|insert',
            r'update|modify|change',
            r'start|stop|enable|disable',
            r'configure|setup|install'
        ]

    def analyze_safety(self, task_plan) -> float:
        """Analyze overall safety score for a task plan"""
        # Local import to avoid circular import
        from .task_executor import StepType

        total_risk = 0.0
        step_count = len(task_plan.steps)

        if step_count == 0:
            return 1.0

        for step in task_plan.steps:
            step_risk = self._analyze_step_safety(step)
            total_risk += step_risk
            step.safety_level = int(step_risk)

        # Calculate weighted average safety score
        average_risk = total_risk / step_count

        # Apply additional risk factors
        if any(step.step_type == StepType.DATABASE_QUERY for step in task_plan.steps):
            average_risk += 0.5

        if any("production" in step.description.lower() for step in task_plan.steps):
            average_risk += 1.0

        # Cap at maximum risk level
        safety_score = min(average_risk, 5.0)

        # Set approval requirement for high-risk tasks
        if safety_score >= 4.0:
            task_plan.requires_approval = True

        logger.debug(f"Task safety analysis: {safety_score}/5.0 (requires_approval: {task_plan.requires_approval})")
        return safety_score

    def _analyze_step_safety(self, step) -> float:
        """Analyze safety risk for a single step"""
        risk_score = 1.0  # Base risk

        text_to_analyze = f"{step.description} {step.command}".lower()

        # Check high-risk patterns
        for pattern in self.high_risk_patterns:
            if re.search(pattern, text_to_analyze):
                risk_score += 2.0
                break

        # Check medium-risk patterns
        for pattern in self.medium_risk_patterns:
            if re.search(pattern, text_to_analyze):
                risk_score += 1.0
                break

        # Additional risk factors
        if step.step_type in [StepType.DATABASE_QUERY, StepType.FILE_OPERATION]:
            risk_score += 0.5

        if "force" in step.command.lower():
            risk_score += 1.0

        if step.timeout_seconds > 300:  # > 5 minutes
            risk_score += 0.5

        return min(risk_score, 5.0)

class PlanOptimizer:
    """Optimizes task plans for efficiency and performance"""

    def __init__(self):
        self.optimization_strategies = [
            self._parallel_optimization,
            self._cache_optimization,
            self._batch_optimization,
            self._timeout_optimization
        ]

    def optimize_plan(self, task_plan):
        """Apply optimization strategies to a task plan"""
        logger.debug(f"Optimizing task plan: {task_plan.name}")

        for strategy in self.optimization_strategies:
            task_plan = strategy(task_plan)

        return task_plan

    def _parallel_optimization(self, task_plan):
        """Identify steps that can be executed in parallel"""
        independent_steps = []

        for step in task_plan.steps:
            if not step.dependencies and step.safety_level <= 2:
                independent_steps.append(step)

        if len(independent_steps) > 1:
            logger.debug(f"Found {len(independent_steps)} steps that can be parallelized")

        return task_plan

    def _cache_optimization(self, task_plan):
        """Optimize for caching opportunities"""
        data_loading_steps = [s for s in task_plan.steps
                            if "load" in s.description.lower() or "ingest" in s.description.lower()]

        for step in data_loading_steps:
            # Add caching parameters
            if "cache" not in step.parameters:
                step.parameters["cache"] = True
                step.parameters["cache_ttl"] = 3600  # 1 hour

        return task_plan

    def _batch_optimization(self, task_plan):
        """Combine similar operations into batches"""
        similar_steps = {}

        for step in task_plan.steps:
            key = (step.step_type, step.command.split()[0] if step.command else "")
            if key not in similar_steps:
                similar_steps[key] = []
            similar_steps[key].append(step)

        # For groups with multiple similar steps, consider batching
        for key, steps in similar_steps.items():
            if len(steps) > 1 and steps[0].safety_level <= 2:
                logger.debug(f"Found {len(steps)} similar steps that could be batched: {key}")

        return task_plan

    def _timeout_optimization(self, task_plan):
        """Optimize step timeouts based on operation type"""
        for step in task_plan.steps:
            if step.step_type == StepType.CLI_COMMAND:
                if "analyze" in step.description.lower():
                    step.timeout_seconds = max(step.timeout_seconds, 120)  # Analysis needs more time
                elif "validate" in step.description.lower():
                    step.timeout_seconds = min(step.timeout_seconds, 30)   # Validation should be quick

        return task_plan

class TaskPlanner:
    """Core task planning engine with LLM integration"""

    def __init__(self, llm_service: Optional['LLMService'] = None):
        self.llm_service = llm_service
        self.intent_recognizer = IntentRecognitionEngine() if 'IntentRecognitionEngine' in globals() else None
        self.command_generator = CommandGenerator() if 'CommandGenerator' in globals() else None
        self.domain_expert = DomainUnderstandingEngine() if 'DomainUnderstandingEngine' in globals() else None
        self.safety_validator = SafetyValidator() if 'SafetyValidator' in globals() else None

        self.dependency_analyzer = DependencyAnalyzer()
        self.safety_analyzer = SafetyAnalyzer()
        self.plan_optimizer = PlanOptimizer()

        # Load task templates
        self.templates = self._load_templates()

    def _load_templates(self) -> List[PlanTemplate]:
        """Load predefined task templates"""
        templates = [
            PlanTemplate(
                name="control_loop_analysis",
                description="Analyze a control loop performance and generate report",
                intent_patterns=[
                    r"analyze.*control.*loop",
                    r"check.*loop.*performance",
                    r"evaluate.*pid.*controller",
                    r"study.*control.*system"
                ],
                step_templates=[
                    {
                        "type": "validation",
                        "description": "Validate input parameters",
                        "safety_level": 1
                    },
                    {
                        "type": "data_loading",
                        "description": "Load control loop data",
                        "safety_level": 2
                    },
                    {
                        "type": "analysis",
                        "description": "Perform control loop analysis",
                        "safety_level": 2
                    },
                    {
                        "type": "reporting",
                        "description": "Generate analysis report",
                        "safety_level": 1
                    }
                ],
                safety_level=2,
                estimated_duration_minutes=10
            ),

            PlanTemplate(
                name="schema_management",
                description="Create, modify, or delete control loop schemas",
                intent_patterns=[
                    r"create.*schema",
                    r"delete.*schema",
                    r"modify.*schema",
                    r"manage.*schema"
                ],
                step_templates=[
                    {
                        "type": "validation",
                        "description": "Validate schema parameters",
                        "safety_level": 1
                    },
                    {
                        "type": "safety_check",
                        "description": "Perform safety checks",
                        "safety_level": 3
                    },
                    {
                        "type": "schema_operation",
                        "description": "Execute schema operation",
                        "safety_level": 3
                    },
                    {
                        "type": "verification",
                        "description": "Verify operation result",
                        "safety_level": 1
                    }
                ],
                safety_level=3,
                estimated_duration_minutes=5,
                requires_approval=True
            ),

            PlanTemplate(
                name="data_ingestion",
                description="Ingest data from various sources into the system",
                intent_patterns=[
                    r"ingest.*data",
                    r"load.*data",
                    r"import.*data",
                    r"add.*data.*source"
                ],
                step_templates=[
                    {
                        "type": "validation",
                        "description": "Validate data source",
                        "safety_level": 1
                    },
                    {
                        "type": "data_loading",
                        "description": "Load data from source",
                        "safety_level": 2
                    },
                    {
                        "type": "data_validation",
                        "description": "Validate loaded data",
                        "safety_level": 1
                    },
                    {
                        "type": "storage",
                        "description": "Store data in system",
                        "safety_level": 2
                    }
                ],
                safety_level=2,
                estimated_duration_minutes=8
            ),

            PlanTemplate(
                name="system_optimization",
                description="Optimize system performance and configuration",
                intent_patterns=[
                    r"optimize.*system",
                    r"improve.*performance",
                    r"tune.*parameters",
                    r"enhance.*efficiency"
                ],
                step_templates=[
                    {
                        "type": "performance_analysis",
                        "description": "Analyze current performance",
                        "safety_level": 1
                    },
                    {
                        "type": "optimization_planning",
                        "description": "Plan optimization strategy",
                        "safety_level": 2
                    },
                    {
                        "type": "safety_check",
                        "description": "Verify optimization safety",
                        "safety_level": 3
                    },
                    {
                        "type": "optimization_execution",
                        "description": "Apply optimizations",
                        "safety_level": 4
                    },
                    {
                        "type": "verification",
                        "description": "Verify optimization results",
                        "safety_level": 2
                    }
                ],
                safety_level=4,
                estimated_duration_minutes=20,
                requires_approval=True
            )
        ]

        logger.info(f"Loaded {len(templates)} task templates")
        return templates

    async def create_task_plan(self, natural_language_request: str, user_context: Optional[Dict[str, Any]] = None):
        """
        Create a comprehensive task plan from a natural language request

        Args:
            natural_language_request: User's request in natural language
            user_context: Additional context about the user and environment

        Returns:
            TaskPlan: Complete executable task plan
        """
        logger.info(f"Creating task plan for request: {natural_language_request}")

        # Step 1: Understand the intent and extract entities
        intent_data = await self._analyze_intent(natural_language_request)

        # Step 2: Find matching template or create custom plan
        template = self._find_best_template(intent_data)

        # Step 3: Generate detailed task plan
        if template:
            task_plan = await self._create_plan_from_template(template, intent_data, user_context)
        else:
            task_plan = await self._create_custom_plan(intent_data, user_context)

        # Step 4: Analyze dependencies and reorder steps
        task_plan.steps = self.dependency_analyzer.analyze_dependencies(task_plan.steps)

        # Step 5: Perform safety analysis
        task_plan.safety_score = self.safety_analyzer.analyze_safety(task_plan)

        # Step 6: Optimize the plan
        task_plan = self.plan_optimizer.optimize_plan(task_plan)

        # Step 7: Final validation
        await self._validate_plan(task_plan)

        logger.info(f"Created task plan '{task_plan.name}' with {len(task_plan.steps)} steps (safety: {task_plan.safety_score:.1f}/5.0)")
        return task_plan

    async def _analyze_intent(self, request: str) -> Dict[str, Any]:
        """Analyze natural language request to extract intent and entities"""
        if self.intent_recognizer:
            try:
                # Create application context for intent recognition
                context = ApplicationContext()
                intent_result = self.intent_recognizer.recognize_intent(request, context)
                entities = intent_result.entities if intent_result else []

                return {
                    "intent": intent_result.primary_intent.intent_type.value if intent_result and intent_result.primary_intent else "general_task",
                    "confidence": intent_result.primary_intent.confidence if intent_result and intent_result.primary_intent else 0.5,
                    "entities": {e.entity_type.value: e.value for e in entities} if entities else {},
                    "original_request": request
                }
            except Exception as e:
                logger.warning(f"Intent recognition failed: {e}")

        # Fallback: simple pattern matching
        return self._simple_intent_analysis(request)

    def _simple_intent_analysis(self, request: str) -> Dict[str, Any]:
        """Simple pattern-based intent analysis as fallback"""
        request_lower = request.lower()

        # Common intent patterns
        if any(word in request_lower for word in ["analyze", "analysis", "check", "study"]):
            intent_type = "analyze"
        elif any(word in request_lower for word in ["create", "make", "generate", "new"]):
            intent_type = "create"
        elif any(word in request_lower for word in ["delete", "remove", "drop"]):
            intent_type = "delete"
        elif any(word in request_lower for word in ["load", "ingest", "import"]):
            intent_type = "ingest"
        elif any(word in request_lower for word in ["optimize", "improve", "tune"]):
            intent_type = "optimize"
        else:
            intent_type = "general_task"

        # Extract simple entities
        entities = {}

        # Look for schema names
        schema_match = re.search(r'schema\s+([a-zA-Z_][a-zA-Z0-9_]*)', request_lower)
        if schema_match:
            entities["schema_name"] = schema_match.group(1)

        # Look for loop names
        loop_match = re.search(r'loop\s+([a-zA-Z0-9_-]+)', request_lower)
        if loop_match:
            entities["loop_name"] = loop_match.group(1)

        # Look for file paths
        file_match = re.search(r'([a-zA-Z0-9_./\\-]+\.(csv|json|yaml|xml))', request)
        if file_match:
            entities["file_path"] = file_match.group(1)

        return {
            "intent": intent_type,
            "confidence": 0.7,
            "entities": entities,
            "original_request": request
        }

    def _find_best_template(self, intent_data: Dict[str, Any]) -> Optional[PlanTemplate]:
        """Find the best matching template for the given intent"""
        best_template = None
        best_score = 0.0

        intent = intent_data.get("intent", "")
        entities = intent_data.get("entities", {})

        for template in self.templates:
            score = template.matches_intent(intent, entities)
            if score > best_score:
                best_score = score
                best_template = template

        # Only use template if match score is reasonable
        if best_score >= 0.5:
            logger.debug(f"Selected template '{best_template.name}' with score {best_score:.2f}")
            return best_template
        else:
            logger.debug("No suitable template found, will create custom plan")
            return None

    async def _create_plan_from_template(self, template: PlanTemplate, intent_data: Dict[str, Any], user_context: Optional[Dict[str, Any]]):
        """Create a task plan from a template"""
        # Local import to avoid circular import
        from .task_executor import TaskPlan, TaskPriority, TaskStep

        task_id = f"task_{int(time.time())}_{len(template.name)}"
        entities = intent_data.get("entities", {})

        # Create task plan
        task_plan = TaskPlan(
            task_id=task_id,
            name=f"{template.description}",
            description=template.description,
            original_request=intent_data["original_request"],
            priority=TaskPriority.NORMAL,
            estimated_duration=timedelta(minutes=template.estimated_duration_minutes),
            safety_score=float(template.safety_level),
            requires_approval=template.requires_approval
        )

        # Generate steps from template
        for i, step_template in enumerate(template.step_templates):
            step_id = f"{task_id}_step_{i}"

            # Generate specific command based on intent and entities
            command = await self._generate_command_for_step(step_template, intent_data, entities)

            step = TaskStep(
                step_id=step_id,
                step_type=self._map_step_type(step_template.get("type", "generic")),
                description=step_template["description"],
                command=command,
                safety_level=step_template.get("safety_level", 2),
                timeout_seconds=step_template.get("timeout", 30),
                confirmation_required=step_template.get("confirmation_required", False)
            )

            task_plan.steps.append(step)

        return task_plan

    async def _create_custom_plan(self, intent_data: Dict[str, Any], user_context: Optional[Dict[str, Any]]):
        """Create a custom task plan using LLM assistance"""
        # Local import to avoid circular import
        from .task_executor import TaskPlan, TaskPriority

        task_id = f"custom_{int(time.time())}"
        intent = intent_data.get("intent", "general_task")
        request = intent_data["original_request"]

        # Create basic task plan
        task_plan = TaskPlan(
            task_id=task_id,
            name=f"Custom Task: {intent.title()}",
            description=f"Custom task based on: {request}",
            original_request=request,
            priority=TaskPriority.NORMAL,
            estimated_duration=timedelta(minutes=10)
        )

        # Generate steps using LLM if available
        if self.llm_service:
            try:
                steps = await self._generate_steps_with_llm(intent_data)
                task_plan.steps.extend(steps)
            except Exception as e:
                logger.warning(f"LLM step generation failed: {e}")

        # Fallback: create basic steps
        if not task_plan.steps:
            task_plan.steps = self._create_fallback_steps(intent_data)

        return task_plan

    async def _generate_steps_with_llm(self, intent_data: Dict[str, Any]) -> List:
        """Generate task steps using LLM assistance"""
        f"""
        Create a detailed task plan for the following request:
        "{intent_data['original_request']}"

        Intent: {intent_data['intent']}
        Entities: {intent_data['entities']}

        Generate 3-7 specific steps that would accomplish this task.
        Each step should include:
        - A clear description
        - A specific command or action
        - A safety level (1-5, where 1 is safe and 5 is dangerous)

        Format as JSON array of steps.
        """

        # This would use the LLM service to generate steps
        # For now, return empty list as fallback
        return []

    def _create_fallback_steps(self, intent_data: Dict[str, Any]) -> List:
        """Create basic fallback steps when LLM is not available"""
        # Local import to avoid circular import
        from .task_executor import StepType, TaskStep

        intent = intent_data.get("intent", "general_task")
        entities = intent_data.get("entities", {})
        task_id = f"fallback_{int(time.time())}"

        steps = []

        if intent == "analyze":
            if "loop_name" in entities:
                loop_name = entities["loop_name"]
                steps = [
                    TaskStep(
                        step_id=f"{task_id}_validate",
                        step_type=StepType.VALIDATION,
                        description=f"Validate loop name: {loop_name}",
                        command="validate_loop_name",
                        parameters={"loop_name": loop_name},
                        safety_level=1
                    ),
                    TaskStep(
                        step_id=f"{task_id}_analyze",
                        step_type=StepType.CLI_COMMAND,
                        description=f"Analyze control loop: {loop_name}",
                        command=f"plc-control-loop analyze --loop {loop_name}",
                        safety_level=2
                    )
                ]
        elif intent == "create":
            if "schema_name" in entities:
                schema_name = entities["schema_name"]
                steps = [
                    TaskStep(
                        step_id=f"{task_id}_create",
                        step_type=StepType.CLI_COMMAND,
                        description=f"Create schema: {schema_name}",
                        command=f"plc-control-loop schema create --name {schema_name}",
                        safety_level=2
                    )
                ]

        # Generic fallback
        if not steps:
            steps = [
                TaskStep(
                    step_id=f"{task_id}_generic",
                    step_type=StepType.CLI_COMMAND,
                    description="Execute generic task",
                    command="echo 'Task execution placeholder'",
                    safety_level=1
                )
            ]

        return steps

    async def _generate_command_for_step(self, step_template: Dict[str, Any], intent_data: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Generate specific command for a step based on template and entities"""
        step_type = step_template.get("type", "generic")
        intent = intent_data.get("intent", "general_task")

        if self.command_generator:
            try:
                return await self.command_generator.generate_command(intent, entities, step_type)
            except Exception as e:
                logger.warning(f"Command generation failed: {e}")

        # Fallback command generation
        return self._generate_fallback_command(step_type, intent, entities)

    def _generate_fallback_command(self, step_type: str, intent: str, entities: Dict[str, Any]) -> str:
        """Generate fallback commands using simple templates"""
        if step_type == "validation":
            return "validate_input"
        elif step_type == "data_loading":
            if "file_path" in entities:
                return f"plc-memory ingest --source {entities['file_path']}"
            else:
                return "plc-memory ingest --source /default/path"
        elif step_type == "analysis":
            if "loop_name" in entities:
                return f"plc-control-loop analyze --loop {entities['loop_name']}"
            else:
                return "plc-control-loop analyze"
        elif step_type == "schema_operation":
            if "schema_name" in entities:
                if intent == "create":
                    return f"plc-control-loop schema create --name {entities['schema_name']}"
                elif intent == "delete":
                    return f"plc-control-loop schema delete --name {entities['schema_name']}"
            return "plc-control-loop schema list"
        else:
            return f"echo 'Executing {step_type} step'"

    def _map_step_type(self, template_type: str):
        """Map template step type to StepType enum"""
        # Local import to avoid circular import
        from .task_executor import StepType

        mapping = {
            "validation": StepType.VALIDATION,
            "data_loading": StepType.CLI_COMMAND,
            "analysis": StepType.CLI_COMMAND,
            "reporting": StepType.CLI_COMMAND,
            "safety_check": StepType.SAFETY_CHECK,
            "schema_operation": StepType.CLI_COMMAND,
            "verification": StepType.VALIDATION,
            "user_confirmation": StepType.USER_CONFIRMATION,
            "file_operation": StepType.FILE_OPERATION,
            "database_query": StepType.DATABASE_QUERY
        }
        return mapping.get(template_type, StepType.CLI_COMMAND)

    async def _validate_plan(self, task_plan) -> None:
        """Perform final validation of the task plan"""
        if not task_plan.steps:
            raise ValueError("Task plan must have at least one step")

        # Check for circular dependencies
        step_ids = {step.step_id for step in task_plan.steps}
        for step in task_plan.steps:
            for dep_id in step.dependencies:
                if dep_id not in step_ids:
                    logger.warning(f"Step {step.step_id} has invalid dependency: {dep_id}")
                    step.dependencies.remove(dep_id)

        # Validate safety requirements
        if self.safety_validator:
            try:
                is_safe = await self.safety_validator.validate_task_plan(task_plan)
                if not is_safe:
                    task_plan.requires_approval = True
                    logger.warning("Task plan requires approval due to safety concerns")
            except Exception as e:
                logger.warning(f"Safety validation failed: {e}")

        task_plan.status = TaskStatus.PLANNED
        logger.debug(f"Task plan validation completed: {task_plan.name}")

# Export main classes
__all__ = [
    "TaskPlanner", "PlanTemplate", "DependencyAnalyzer",
    "SafetyAnalyzer", "PlanOptimizer"
]

if __name__ == "__main__":
    # Example usage
    async def main():
        planner = TaskPlanner()

        # Create task plan from natural language
        request = "Analyze the temperature control loop TIC-101 using data from /data/tic101.csv"
        task_plan = await planner.create_task_plan(request)

        print(f"Created task plan: {task_plan.name}")
        print(f"Steps: {len(task_plan.steps)}")
        print(f"Safety score: {task_plan.safety_score}")

        for step in task_plan.steps:
            print(f"  - {step.description}")

    asyncio.run(main())
