"""Task analysis module for the PLC Task Orchestrator."""

import re
from typing import Any

from plc_orchestrator.config.settings import OrchestratorConfig
from plc_orchestrator.utils.data_models import TaskAnalysis
from plc_orchestrator.utils.enums import ControlSystemComplexity, TaskComplexity
from plc_orchestrator.utils.errors import TaskAnalysisError
from plc_orchestrator.utils.helpers import (
    calculate_complexity_score,
    extract_keywords,
    generate_task_id,
)
from plc_orchestrator.utils.logging import get_logger


class TaskAnalyzer:
    """Analyzes tasks to determine complexity, requirements, and execution plans."""

    # Constants
    ML_KEYWORD = "machine learning"

    def __init__(self, config: OrchestratorConfig) -> None:
        """
        Initialize task analyzer.

        Args:
            config: Orchestrator configuration
        """
        self.config = config
        self.logger = get_logger(__name__, config.get_logging_config())

    def analyze(self, task_description: str) -> TaskAnalysis:
        """
        Analyze a task description to create a comprehensive task analysis.

        Args:
            task_description: Natural language task description

        Returns:
            Complete task analysis

        Raises:
            TaskAnalysisError: If analysis fails
        """
        try:
            task_id = generate_task_id()
            self.logger.info(f"Analyzing task: {task_id}")

            # Basic analysis
            complexity = self._assess_complexity(task_description)
            requirements = self._extract_requirements(task_description)
            risks = self._identify_risks(task_description)
            dependencies = self._identify_dependencies(task_description)

            # Effort estimation
            estimated_effort = self._estimate_effort(task_description)

            # Create execution plan
            execution_plan = self._create_execution_plan(task_description, complexity, requirements)

            # Define validation criteria
            validation_criteria = self._define_validation_criteria(task_description)

            # Resources identification
            resources = self._identify_resources(task_description)

            # Check for control system task
            control_analysis = None
            if self.config.settings.enable_control_analysis and self._is_control_system_task(
                task_description
            ):
                control_analysis = self._analyze_control_task(task_description)

            # Create task analysis
            analysis = TaskAnalysis(
                task_id=task_id,
                description=task_description,
                complexity=complexity,
                requirements=requirements,
                risks=risks,
                dependencies=dependencies,
                estimated_effort=estimated_effort,
                execution_plan=execution_plan,
                validation_criteria=validation_criteria,
                resources=resources,
                control_analysis=control_analysis,
                metadata={
                    "analyzer_version": "2.0.0",
                    "analysis_timestamp": None,  # Will be set by dataclass
                },
            )

            self.logger.info(
                "Task analysis completed",
                extra={
                    "task_id": task_id,
                    "complexity": complexity,
                    "requirements_count": len(requirements),
                },
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Task analysis failed: {e}")
            raise TaskAnalysisError(
                f"Failed to analyze task: {e}", task_description=task_description
            )

    def _assess_complexity(self, task_description: str) -> str:
        """
        Assess task complexity based on various factors.

        Args:
            task_description: Task description

        Returns:
            Complexity level
        """
        # Extract indicators
        lines_indicator = self._estimate_lines_of_code(task_description)
        files_indicator = self._estimate_file_count(task_description)
        deps_indicator = len(self._identify_dependencies(task_description))
        has_tests = "test" in task_description.lower()

        # Calculate complexity
        return calculate_complexity_score(
            lines_of_code=lines_indicator,
            num_files=files_indicator,
            num_dependencies=deps_indicator,
            has_tests=has_tests,
        )

    def _estimate_lines_of_code(self, task_description: str) -> int:
        """Estimate lines of code from task description."""
        desc_lower = task_description.lower()

        # Look for explicit mentions
        loc_match = re.search(r"(\d+)\s*lines?\s*of\s*code", desc_lower)
        if loc_match:
            return int(loc_match.group(1))

        # Estimate based on keywords
        if any(word in desc_lower for word in ["simple", "basic", "small", "quick"]):
            return 50
        elif any(word in desc_lower for word in ["complex", "large", "comprehensive", "full"]):
            return 1000
        elif any(word in desc_lower for word in ["entire", "system", "framework", "platform"]):
            return 2000
        else:
            return 300  # Default moderate

    def _estimate_file_count(self, task_description: str) -> int:
        """Estimate number of files from task description."""
        desc_lower = task_description.lower()

        # Look for explicit mentions
        file_match = re.search(r"(\d+)\s*files?", desc_lower)
        if file_match:
            return int(file_match.group(1))

        # Estimate based on scope
        if "single file" in desc_lower or "one file" in desc_lower:
            return 1
        elif any(word in desc_lower for word in ["module", "package", "library"]):
            return 5
        elif any(word in desc_lower for word in ["application", "system", "framework"]):
            return 20
        else:
            return 3  # Default few files

    def _extract_requirements(self, task_description: str) -> list[str]:
        """
        Extract functional and non-functional requirements.

        Args:
            task_description: Task description

        Returns:
            List of requirements
        """
        requirements = []
        desc_lower = task_description.lower()

        # Functional requirements patterns
        patterns = [
            (r"must\s+(\w+[\w\s]+)", "Must {}"),
            (r"should\s+(\w+[\w\s]+)", "Should {}"),
            (r"need(?:s)?\s+to\s+(\w+[\w\s]+)", "Need to {}"),
            (r"require(?:s)?\s+(\w+[\w\s]+)", "Requires {}"),
            (r"implement\s+(\w+[\w\s]+)", "Implement {}"),
            (r"create\s+(\w+[\w\s]+)", "Create {}"),
            (r"build\s+(\w+[\w\s]+)", "Build {}"),
            (r"support\s+(\w+[\w\s]+)", "Support {}"),
        ]

        for pattern, template in patterns:
            matches = re.finditer(pattern, desc_lower)
            for match in matches:
                req = template.format(match.group(1).strip())
                if len(req) > 10:  # Filter out very short matches
                    requirements.append(req)

        # Add specific technical requirements
        tech_requirements = {
            "error handling": ["Implement comprehensive error handling", "Handle edge cases"],
            "logging": ["Add logging functionality", "Include debug logging"],
            "testing": ["Write unit tests", "Include integration tests"],
            "documentation": ["Document code with docstrings", "Create user documentation"],
            "performance": ["Optimize for performance", "Handle large datasets efficiently"],
            "security": ["Implement security best practices", "Validate all inputs"],
            "async": ["Implement asynchronous operations", "Handle concurrent requests"],
            "api": ["Create REST API endpoints", "Follow RESTful principles"],
            "database": ["Implement database operations", "Handle database transactions"],
            "validation": ["Validate input data", "Implement data validation"],
        }

        for keyword, reqs in tech_requirements.items():
            if keyword in desc_lower:
                requirements.extend(reqs)

        # Remove duplicates while preserving order
        seen = set()
        unique_requirements = []
        for req in requirements:
            if req not in seen:
                seen.add(req)
                unique_requirements.append(req)

        return (
            unique_requirements
            if unique_requirements
            else ["Implement the requested functionality"]
        )

    def _identify_risks(self, task_description: str) -> list[str]:
        """Identify potential risks and challenges."""
        risks = []
        desc_lower = task_description.lower()

        # Technical risks
        risk_indicators = {
            "performance": "Performance degradation with large datasets",
            "scale": "Scalability issues under high load",
            "security": "Security vulnerabilities if not properly implemented",
            "compatibility": "Compatibility issues with existing systems",
            "migration": "Data migration risks",
            "integration": "Integration complexity with external systems",
            "real-time": "Real-time processing constraints",
            "concurrent": "Concurrency and race condition risks",
            "memory": "Memory usage concerns",
            "network": "Network reliability dependencies",
            "legacy": "Legacy system compatibility issues",
            "third-party": "Third-party dependency risks",
        }

        for indicator, risk in risk_indicators.items():
            if indicator in desc_lower:
                risks.append(risk)

        # Add general risks based on complexity
        complexity = self._assess_complexity(task_description)
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXTENSIVE]:
            risks.extend(
                [
                    "Increased complexity may lead to bugs",
                    "Longer development time required",
                    "Higher maintenance burden",
                ]
            )

        return risks if risks else ["Standard implementation risks"]

    def _identify_dependencies(self, task_description: str) -> list[str]:
        """Identify external dependencies and libraries."""
        dependencies = []
        desc_lower = task_description.lower()

        # Common Python dependencies
        dep_patterns = {
            "fastapi": ["FastAPI", "uvicorn", "pydantic"],
            "flask": ["Flask", "werkzeug"],
            "django": ["Django"],
            "requests": ["requests"],
            "async": ["asyncio", "aiohttp"],
            "database": ["sqlalchemy", "psycopg2"],
            "mongodb": ["pymongo"],
            "redis": ["redis"],
            "numpy": ["numpy"],
            "pandas": ["pandas"],
            self.ML_KEYWORD: ["scikit-learn", "tensorflow", "pytorch"],
            "plotting": ["matplotlib", "seaborn"],
            "testing": ["pytest", "unittest"],
            "logging": ["structlog"],
            "validation": ["pydantic", "marshmallow"],
            "cli": ["click", "typer"],
            "scheduling": ["celery", "apscheduler"],
            "websocket": ["websockets"],
            "graphql": ["graphene"],
            "grpc": ["grpcio"],
        }

        for keyword, deps in dep_patterns.items():
            if keyword in desc_lower:
                dependencies.extend(deps)

        # Remove duplicates
        return list(set(dependencies))

    def _estimate_effort(self, task_description: str) -> dict[str, Any]:
        """Estimate development effort."""
        complexity = self._assess_complexity(task_description)

        # Base estimates
        effort_map = {
            TaskComplexity.SIMPLE: {"hours": 2, "days": 0.25, "confidence": "high"},
            TaskComplexity.MODERATE: {"hours": 8, "days": 1, "confidence": "medium"},
            TaskComplexity.COMPLEX: {"hours": 24, "days": 3, "confidence": "medium"},
            TaskComplexity.EXTENSIVE: {"hours": 40, "days": 5, "confidence": "low"},
        }

        base_effort = effort_map.get(complexity, effort_map[TaskComplexity.MODERATE])

        # Adjust for specific factors
        multiplier = 1.0

        if "test" in task_description.lower():
            multiplier *= 1.3
        if "documentation" in task_description.lower():
            multiplier *= 1.2
        if "refactor" in task_description.lower():
            multiplier *= 1.5
        if "optimize" in task_description.lower():
            multiplier *= 1.4

        return {
            "hours": int(base_effort["hours"] * multiplier),
            "days": round(base_effort["days"] * multiplier, 1),
            "confidence": base_effort["confidence"],
            "factors": {"base_complexity": complexity, "multiplier": multiplier},
        }

    def _create_execution_plan(
        self, _task_description: str, complexity: str, requirements: list[str]
    ) -> list[dict[str, Any]]:
        """Create step-by-step execution plan."""
        plan = []

        # Always start with setup
        plan.append(
            {
                "step": 1,
                "name": "Environment Setup",
                "description": "Set up development environment and dependencies",
                "estimated_time": "15 minutes",
            }
        )

        # Add discovery for non-simple tasks
        if complexity != TaskComplexity.SIMPLE:
            plan.append(
                {
                    "step": 2,
                    "name": "Codebase Discovery",
                    "description": "Analyze existing code and identify integration points",
                    "estimated_time": "30 minutes",
                }
            )

        # Core implementation steps
        base_step = len(plan) + 1

        plan.append(
            {
                "step": base_step,
                "name": "Implementation Planning",
                "description": "Create detailed implementation plan",
                "estimated_time": "20 minutes",
            }
        )

        plan.append(
            {
                "step": base_step + 1,
                "name": "Core Implementation",
                "description": "Implement main functionality",
                "estimated_time": "2-4 hours",
            }
        )

        # Add testing if mentioned
        if any("test" in req.lower() for req in requirements):
            plan.append(
                {
                    "step": base_step + 2,
                    "name": "Testing",
                    "description": "Write and run tests",
                    "estimated_time": "1 hour",
                }
            )

        # Add documentation
        plan.append(
            {
                "step": len(plan) + 1,
                "name": "Documentation",
                "description": "Document code and update project docs",
                "estimated_time": "30 minutes",
            }
        )

        # Add validation
        plan.append(
            {
                "step": len(plan) + 1,
                "name": "Validation",
                "description": "Validate implementation against requirements",
                "estimated_time": "20 minutes",
            }
        )

        return plan

    def _define_validation_criteria(self, task_description: str) -> list[str]:
        """Define criteria for validating task completion."""
        criteria = [
            "Code compiles/runs without errors",
            "All requirements are implemented",
            "Code follows project conventions",
            "Error handling is implemented",
            "Code is properly documented",
        ]

        desc_lower = task_description.lower()

        # Add specific criteria based on task
        if "test" in desc_lower:
            criteria.append("All tests pass with >80% coverage")
        if "api" in desc_lower:
            criteria.append("API endpoints respond correctly")
        if "performance" in desc_lower:
            criteria.append("Performance benchmarks are met")
        if "security" in desc_lower:
            criteria.append("Security best practices are followed")
        if "database" in desc_lower:
            criteria.append("Database operations are transactional")
        if "async" in desc_lower:
            criteria.append("Async operations handle errors properly")

        return criteria

    def _identify_resources(self, task_description: str) -> dict[str, Any]:
        """Identify required resources and references."""
        keywords = extract_keywords(task_description)

        return {
            "keywords": keywords,
            "domains": self._identify_domains(task_description),
            "technologies": self._identify_technologies(task_description),
            "references": self._suggest_references(task_description),
        }

    def _identify_domains(self, task_description: str) -> list[str]:
        """Identify technical domains."""
        domains = []
        desc_lower = task_description.lower()

        domain_keywords = {
            "web": ["api", "rest", "http", "web", "endpoint"],
            "data": ["data", "database", "sql", "query", "etl"],
            "ml": [self.ML_KEYWORD, "ml", "ai", "model", "training"],
            "control": ["control", "pid", "plc", "scada", "automation"],
            "security": ["security", "auth", "encryption", "secure"],
            "networking": ["network", "socket", "tcp", "udp", "protocol"],
            "devops": ["deploy", "ci/cd", "docker", "kubernetes"],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                domains.append(domain)

        return domains if domains else ["general"]

    def _identify_technologies(self, task_description: str) -> list[str]:
        """Identify specific technologies mentioned."""
        technologies = []
        desc_lower = task_description.lower()

        # Common technology patterns
        tech_patterns = [
            r"using\s+(\w+)",
            r"with\s+(\w+)",
            r"(\w+)\s+framework",
            r"(\w+)\s+library",
            r"(\w+)\s+api",
            r"(\w+)\s+database",
        ]

        for pattern in tech_patterns:
            matches = re.finditer(pattern, desc_lower)
            for match in matches:
                tech = match.group(1)
                if len(tech) > 2:  # Filter out short matches
                    technologies.append(tech)

        return list(set(technologies))

    def _suggest_references(self, task_description: str) -> list[str]:
        """Suggest documentation references."""
        references = []
        desc_lower = task_description.lower()

        # Add relevant documentation
        if "fastapi" in desc_lower:
            references.append("https://fastapi.tiangolo.com/")
        if "pydantic" in desc_lower:
            references.append("https://pydantic-docs.helpmanual.io/")
        if "async" in desc_lower:
            references.append("https://docs.python.org/3/library/asyncio.html")
        if "test" in desc_lower:
            references.append("https://docs.pytest.org/")

        return references

    def _is_control_system_task(self, task_description: str) -> bool:
        """Check if task is control system related."""
        control_keywords = [
            "control",
            "pid",
            "plc",
            "scada",
            "hmi",
            "automation",
            "controller",
            "tuning",
            "loop",
            "setpoint",
            "process",
            "feedback",
            "feedforward",
            "cascade",
            "mpc",
            "dcs",
        ]

        desc_lower = task_description.lower()
        return any(keyword in desc_lower for keyword in control_keywords)

    def _analyze_control_task(self, task_description: str) -> dict[str, Any]:
        """Analyze control system specific aspects."""
        complexity = self._assess_control_complexity(task_description)

        return {
            "complexity": complexity.value,
            "control_type": self._identify_control_type(task_description),
            "safety_requirements": self._identify_safety_requirements(task_description),
            "performance_targets": self._identify_performance_targets(task_description),
            "recommended_algorithms": self._recommend_control_algorithms(task_description),
            "validation_methods": [
                "Step response analysis",
                "Stability margin verification",
                "Disturbance rejection testing",
                "Setpoint tracking validation",
            ],
        }

    def _assess_control_complexity(self, task_description: str) -> ControlSystemComplexity:
        """Assess control system complexity."""
        desc_lower = task_description.lower()

        if any(word in desc_lower for word in ["mpc", "model predictive", "advanced"]):
            return ControlSystemComplexity.MPC_ADVANCED
        elif any(word in desc_lower for word in ["cascade", "feedforward", "multi-loop"]):
            return ControlSystemComplexity.CASCADE_CONTROL
        elif any(word in desc_lower for word in ["ml", self.ML_KEYWORD, "neural"]):
            return ControlSystemComplexity.ML_ENHANCED
        else:
            return ControlSystemComplexity.BASIC_PID

    def _identify_control_type(self, task_description: str) -> str:
        """Identify type of control system."""
        desc_lower = task_description.lower()

        if "temperature" in desc_lower:
            return "Temperature Control"
        elif "pressure" in desc_lower:
            return "Pressure Control"
        elif "flow" in desc_lower:
            return "Flow Control"
        elif "level" in desc_lower:
            return "Level Control"
        elif "position" in desc_lower or "motion" in desc_lower:
            return "Motion Control"
        else:
            return "Process Control"

    def _identify_safety_requirements(self, task_description: str) -> list[str]:
        """Identify safety requirements for control systems."""
        requirements = [
            "Implement safety interlocks",
            "Add alarm and trip logic",
            "Include manual override capability",
            "Implement bumpless transfer",
            "Add rate limiting for actuator commands",
        ]

        desc_lower = task_description.lower()

        if "critical" in desc_lower or "safety" in desc_lower:
            requirements.extend(
                [
                    "Implement redundant safety checks",
                    "Add SIL-rated safety functions",
                    "Include emergency shutdown logic",
                ]
            )

        return requirements

    def _identify_performance_targets(self, task_description: str) -> dict[str, Any]:
        """Identify performance targets for control systems."""
        # Default targets
        targets = {
            "settling_time": "< 30 seconds",
            "overshoot": "< 10%",
            "steady_state_error": "< 1%",
            "rise_time": "< 10 seconds",
        }

        desc_lower = task_description.lower()

        # Adjust based on application
        if "fast" in desc_lower or "rapid" in desc_lower:
            targets["settling_time"] = "< 10 seconds"
            targets["rise_time"] = "< 3 seconds"
        elif "precise" in desc_lower or "accurate" in desc_lower:
            targets["overshoot"] = "< 5%"
            targets["steady_state_error"] = "< 0.5%"

        return targets

    def _recommend_control_algorithms(self, task_description: str) -> list[str]:
        """Recommend control algorithms based on task."""
        algorithms = ["PID Control"]
        desc_lower = task_description.lower()

        if "cascade" in desc_lower:
            algorithms.append("Cascade Control")
        if "feedforward" in desc_lower:
            algorithms.append("Feedforward Control")
        if "adaptive" in desc_lower:
            algorithms.append("Adaptive Control")
        if "predictive" in desc_lower or "mpc" in desc_lower:
            algorithms.append("Model Predictive Control")
        if "optimal" in desc_lower:
            algorithms.append("Optimal Control")
        if "robust" in desc_lower:
            algorithms.append("Robust Control")

        return algorithms
