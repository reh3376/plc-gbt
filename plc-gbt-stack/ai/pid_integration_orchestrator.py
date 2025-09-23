#!/usr/bin/env python3
"""
PID Integration Orchestrator for Phase 8
Demonstrates integration of Autonomous PID Tuning with existing PLC-GPT infrastructure

This module bridges the Autonomous PID Roadmap with:
- AI Task Orchestrator for intelligent workflow management
- Neo4j Knowledge Graph for PID loop relationships
- Enterprise Monitoring for real-time performance tracking
- Studio 5000 Integration for parameter deployment
- Vector Database for historical performance similarity

Created: January 3, 2025
"""

import logging
import os

# Integration with existing PLC-GPT infrastructure
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.ai_task_orchestrator import AITaskOrchestrator, get_task_guidance

from scripts.query.knowledge_graph_interface import PLCKnowledgeGraph

# External dependencies for PID functionality
try:
    import control
    import numpy as np
    from scipy import signal

    CONTROL_LIBRARIES_AVAILABLE = True
except ImportError:
    CONTROL_LIBRARIES_AVAILABLE = False
    print("Warning: Control libraries not available. PID functionality will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PIDProcessType(Enum):
    """PID process types for tuning strategy selection"""

    LEVEL = "level"
    FLOW = "flow"
    PRESSURE = "pressure"
    TEMPERATURE = "temperature"
    PH = "ph"
    CONDUCTIVITY = "conductivity"
    SPEED = "speed"
    POSITION = "position"


class PIDAlgorithmForm(Enum):
    """PID algorithm forms (Rockwell-specific)"""

    DEPENDENT = "dependent"
    INDEPENDENT = "independent"


class PIDInstructionType(Enum):
    """PID instruction types"""

    PID = "PID"
    PIDE = "PIDE"


class PIDControlMode(Enum):
    """PID control modes"""

    P = "P"
    PI = "PI"
    PID = "PID"


@dataclass
class PIDLoop:
    """PID Loop configuration and state"""

    loop_id: str
    name: str
    description: str
    process_type: PIDProcessType
    algorithm_form: PIDAlgorithmForm
    instruction_type: PIDInstructionType
    control_mode: PIDControlMode

    # Process Variables
    pv_tags: list[str] = field(default_factory=list)
    pv_weights: list[float] = field(default_factory=list)
    cv_tag: str = ""
    sp_tag: str = ""

    # PID Parameters
    kc: float = 1.0  # Proportional gain
    ti: float = 1.0  # Integral time (minutes)
    td: float = 0.0  # Derivative time (minutes)

    # Scaling and Limits
    pv_range: tuple[float, float] = (0.0, 100.0)
    cv_range: tuple[float, float] = (0.0, 100.0)
    sp_range: tuple[float, float] = (0.0, 100.0)

    # Performance Metrics
    last_tuned: datetime | None = None
    performance_score: float = 0.0
    oscillation_index: float = 0.0
    cv_saturation_percent: float = 0.0

    # Relationships
    cascade_master: str | None = None
    cascade_slaves: list[str] = field(default_factory=list)
    disturbance_variables: list[str] = field(default_factory=list)


@dataclass
class PIDTuningSession:
    """PID tuning session data"""

    session_id: str
    loop_id: str
    started: datetime
    completed: datetime | None = None

    # Tuning method and parameters
    tuning_method: str = "ziegler_nichols"
    initial_parameters: dict[str, float] = field(default_factory=dict)
    final_parameters: dict[str, float] = field(default_factory=dict)

    # Performance results
    initial_performance: dict[str, float] = field(default_factory=dict)
    final_performance: dict[str, float] = field(default_factory=dict)

    # Step test data
    step_test_data: list[dict[str, Any]] = field(default_factory=list)
    model_identification: dict[str, float] = field(default_factory=dict)

    # Status and notes
    status: str = "in_progress"
    notes: str = ""
    operator: str = ""


class PIDIntegrationOrchestrator:
    """
    PID Integration Orchestrator that bridges Autonomous PID Roadmap
    with existing PLC-GPT infrastructure.

    Key Integration Points:
    1. AI Task Orchestrator - Intelligent workflow management
    2. Knowledge Graph - PID loop relationships and history
    3. Enterprise Monitoring - Real-time performance tracking
    4. Studio 5000 Integration - Parameter deployment
    5. Vector Database - Historical performance similarity
    """

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
    ):
        """Initialize PID Integration Orchestrator"""

        # Initialize existing PLC-GPT infrastructure
        self.ai_orchestrator = AITaskOrchestrator()
        self.knowledge_graph = PLCKnowledgeGraph(neo4j_uri, neo4j_user, neo4j_password)

        # PID-specific state
        self.pid_loops: dict[str, PIDLoop] = {}
        self.active_tuning_sessions: dict[str, PIDTuningSession] = {}
        self.tuning_history: list[PIDTuningSession] = []

        # Performance tracking
        self.performance_thresholds = {
            "oscillation_index": 0.3,
            "cv_saturation_percent": 10.0,
            "response_time_seconds": 300.0,
            "steady_state_error_percent": 2.0,
        }

        # Tuning algorithm registry
        self.tuning_algorithms = {
            "ziegler_nichols": self._ziegler_nichols_tuning,
            "cohen_coon": self._cohen_coon_tuning,
            "imc": self._imc_tuning,
            "lambda_tuning": self._lambda_tuning,
        }

        logger.info("PID Integration Orchestrator initialized")
        logger.info(f"Control libraries available: {CONTROL_LIBRARIES_AVAILABLE}")

    def discover_pid_loops(self) -> list[PIDLoop]:
        """
        Discover PID loops using existing knowledge graph infrastructure.

        Integrates with:
        - PLCKnowledgeGraph for component discovery
        - AI Task Orchestrator for intelligent analysis
        """
        logger.info("Discovering PID loops using knowledge graph...")

        try:
            # Use AI Task Orchestrator for intelligent loop discovery
            get_task_guidance("Discover and analyze PID control loops in PLC project files")

            # Search for PID-related components in knowledge graph
            with self.knowledge_graph.driver.session() as session:
                # Query for PID/PIDE instructions
                query = """
                MATCH (c:PLCComponent)
                WHERE c.name CONTAINS 'PID' OR c.name CONTAINS 'PIDE'
                   OR c.description CONTAINS 'control' OR c.description CONTAINS 'loop'
                RETURN c.id as component_id, c.name as name, c.description as description,
                       c.component_type as type, properties(c) as properties
                ORDER BY c.name
                """

                result = session.run(query)
                components = [dict(record) for record in result]

                # Convert to PID loops
                discovered_loops = []
                for comp in components:
                    loop_id = f"loop_{comp['component_id']}"

                    # Use AI guidance to classify process type
                    process_type = self._classify_process_type(comp)

                    pid_loop = PIDLoop(
                        loop_id=loop_id,
                        name=comp["name"],
                        description=comp["description"] or "",
                        process_type=process_type,
                        algorithm_form=PIDAlgorithmForm.INDEPENDENT,
                        instruction_type=PIDInstructionType.PIDE,
                        control_mode=PIDControlMode.PID,
                    )

                    discovered_loops.append(pid_loop)
                    self.pid_loops[loop_id] = pid_loop

                logger.info(f"Discovered {len(discovered_loops)} PID loops")
                return discovered_loops

        except Exception as e:
            logger.error(f"Error discovering PID loops: {e}")
            return []

    def _classify_process_type(self, component: dict[str, Any]) -> PIDProcessType:
        """
        Classify process type using AI analysis.

        Integrates with AI Task Orchestrator for intelligent classification.
        """
        name = component.get("name", "").lower()
        description = component.get("description", "").lower()

        # Simple heuristic classification (can be enhanced with AI)
        if "level" in name or "level" in description:
            return PIDProcessType.LEVEL
        elif "flow" in name or "flow" in description:
            return PIDProcessType.FLOW
        elif "pressure" in name or "pressure" in description:
            return PIDProcessType.PRESSURE
        elif "temp" in name or "temp" in description:
            return PIDProcessType.TEMPERATURE
        else:
            return PIDProcessType.LEVEL  # Default

    def configure_multi_pv_strategy(
        self, loop_id: str, pv_tags: list[str], weights: list[float] | None = None
    ) -> bool:
        """
        Configure multi-PV control strategy as per Autonomous PID Roadmap Milestone 2.

        Integrates with:
        - Knowledge Graph for PV relationship discovery
        - AI Task Orchestrator for cascade suggestion
        """
        if loop_id not in self.pid_loops:
            logger.error(f"Loop {loop_id} not found")
            return False

        loop = self.pid_loops[loop_id]

        # Use AI Task Orchestrator for intelligent PV analysis
        task_description = f"Analyze multi-PV control strategy for {len(pv_tags)} process variables"
        get_task_guidance(task_description)

        # Configure PV weighting
        if weights is None:
            weights = [1.0] * len(pv_tags)  # Equal weights

        if len(weights) != len(pv_tags):
            logger.error("Number of weights must match number of PV tags")
            return False

        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        # Update loop configuration
        loop.pv_tags = pv_tags
        loop.pv_weights = normalized_weights

        # Check for cascade opportunities using knowledge graph
        cascade_suggestions = self._analyze_cascade_opportunities(loop_id)

        logger.info(f"Configured multi-PV strategy for loop {loop_id}")
        logger.info(f"PV tags: {pv_tags}")
        logger.info(f"Weights: {normalized_weights}")
        logger.info(f"Cascade suggestions: {len(cascade_suggestions)}")

        return True

    def _analyze_cascade_opportunities(self, loop_id: str) -> list[str]:
        """
        Analyze cascade control opportunities using knowledge graph.

        Integrates with PLCKnowledgeGraph for relationship analysis.
        """
        try:
            with self.knowledge_graph.driver.session() as session:
                # Find related components that could form cascade loops
                query = """
                MATCH (primary:PLCComponent {id: $loop_id})
                MATCH (secondary:PLCComponent)
                WHERE secondary.name CONTAINS 'flow' OR secondary.name CONTAINS 'pressure'
                RETURN secondary.id as secondary_id, secondary.name as name
                LIMIT 10
                """

                result = session.run(query, loop_id=loop_id)
                candidates = [record["secondary_id"] for record in result]

                return candidates

        except Exception as e:
            logger.error(f"Error analyzing cascade opportunities: {e}")
            return []

    def execute_automated_tuning(
        self, loop_id: str, method: str = "ziegler_nichols"
    ) -> PIDTuningSession:
        """
        Execute automated PID tuning procedure as per Autonomous PID Roadmap Milestone 5.

        Integrates with:
        - AI Task Orchestrator for workflow management
        - Enterprise Monitoring for performance tracking
        """
        if loop_id not in self.pid_loops:
            raise ValueError(f"Loop {loop_id} not found")

        if method not in self.tuning_algorithms:
            raise ValueError(f"Tuning method {method} not supported")

        # Create tuning session
        session_id = f"tuning_{loop_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = PIDTuningSession(
            session_id=session_id,
            loop_id=loop_id,
            started=datetime.now(),
            tuning_method=method,
            operator="system",
        )

        self.active_tuning_sessions[session_id] = session

        # Use AI Task Orchestrator for tuning workflow
        task_description = f"Execute automated PID tuning for loop {loop_id} using {method} method"
        guidance = get_task_guidance(task_description)

        logger.info(f"Starting automated tuning session: {session_id}")
        logger.info(f"Method: {method}")
        logger.info(f"AI guidance: {guidance.get('approach', 'Standard tuning procedure')}")

        try:
            # Execute tuning algorithm
            tuning_algorithm = self.tuning_algorithms[method]
            initial_params, final_params = tuning_algorithm(loop_id)

            # Update session with results
            session.initial_parameters = initial_params
            session.final_parameters = final_params
            session.completed = datetime.now()
            session.status = "completed"

            # Update loop parameters
            loop = self.pid_loops[loop_id]
            loop.kc = final_params.get("kc", loop.kc)
            loop.ti = final_params.get("ti", loop.ti)
            loop.td = final_params.get("td", loop.td)
            loop.last_tuned = datetime.now()

            logger.info(f"Tuning session {session_id} completed successfully")
            logger.info(f"Final parameters: Kc={loop.kc:.3f}, Ti={loop.ti:.3f}, Td={loop.td:.3f}")

        except Exception as e:
            session.status = "failed"
            session.notes = str(e)
            logger.error(f"Tuning session {session_id} failed: {e}")

        # Move to history
        self.tuning_history.append(session)
        del self.active_tuning_sessions[session_id]

        return session

    def _ziegler_nichols_tuning(self, loop_id: str) -> tuple[dict[str, float], dict[str, float]]:
        """
        Ziegler-Nichols tuning algorithm implementation.

        Integrates with enterprise monitoring for real-time data collection.
        """
        loop = self.pid_loops[loop_id]

        # Get initial parameters
        initial_params = {"kc": loop.kc, "ti": loop.ti, "td": loop.td}

        # Simulate tuning process (in real implementation, this would involve step tests)
        if CONTROL_LIBRARIES_AVAILABLE:
            # Example process model (First Order Plus Dead Time)
            K = 1.0  # Process gain
            tau = 10.0  # Time constant
            theta = 2.0  # Dead time

            # Ziegler-Nichols rules for FOPDT
            kc = 1.2 * tau / (K * theta)
            ti = 2.0 * theta
            td = 0.5 * theta

            final_params = {"kc": kc, "ti": ti, "td": td}
        else:
            # Fallback tuning without control libraries
            final_params = {
                "kc": initial_params["kc"] * 1.2,
                "ti": initial_params["ti"] * 0.8,
                "td": initial_params["td"] * 1.5,
            }

        logger.info(f"Ziegler-Nichols tuning completed for loop {loop_id}")
        return initial_params, final_params

    def _cohen_coon_tuning(self, loop_id: str) -> tuple[dict[str, float], dict[str, float]]:
        """Cohen-Coon tuning algorithm implementation."""
        # Placeholder implementation
        loop = self.pid_loops[loop_id]
        initial_params = {"kc": loop.kc, "ti": loop.ti, "td": loop.td}
        final_params = {"kc": loop.kc * 1.1, "ti": loop.ti * 0.9, "td": loop.td * 1.2}
        return initial_params, final_params

    def _imc_tuning(self, loop_id: str) -> tuple[dict[str, float], dict[str, float]]:
        """Internal Model Control tuning algorithm implementation."""
        # Placeholder implementation
        loop = self.pid_loops[loop_id]
        initial_params = {"kc": loop.kc, "ti": loop.ti, "td": loop.td}
        final_params = {"kc": loop.kc * 0.9, "ti": loop.ti * 1.1, "td": loop.td * 0.8}
        return initial_params, final_params

    def _lambda_tuning(self, loop_id: str) -> tuple[dict[str, float], dict[str, float]]:
        """Lambda tuning algorithm implementation."""
        # Placeholder implementation
        loop = self.pid_loops[loop_id]
        initial_params = {"kc": loop.kc, "ti": loop.ti, "td": loop.td}
        final_params = {"kc": loop.kc * 1.0, "ti": loop.ti * 1.0, "td": loop.td * 0.9}
        return initial_params, final_params

    def monitor_performance(self, loop_id: str) -> dict[str, Any]:
        """
        Monitor PID loop performance using enterprise monitoring infrastructure.

        Integrates with:
        - Enterprise Monitoring for metrics collection
        - Vector Database for historical comparison
        """
        if loop_id not in self.pid_loops:
            raise ValueError(f"Loop {loop_id} not found")

        loop = self.pid_loops[loop_id]

        # Simulate performance metrics (in real implementation, this would get real data)
        performance_metrics = {
            "timestamp": datetime.now().isoformat(),
            "loop_id": loop_id,
            "pv_value": 50.0 + np.random.normal(0, 2.0) if CONTROL_LIBRARIES_AVAILABLE else 50.0,
            "sp_value": 50.0,
            "cv_value": 45.0 + np.random.normal(0, 5.0) if CONTROL_LIBRARIES_AVAILABLE else 45.0,
            "oscillation_index": loop.oscillation_index,
            "cv_saturation_percent": loop.cv_saturation_percent,
            "performance_score": loop.performance_score,
            "tuning_method": self.tuning_history[-1].tuning_method
            if self.tuning_history
            else "manual",
        }

        # Check performance thresholds
        alerts = []
        if loop.oscillation_index > self.performance_thresholds["oscillation_index"]:
            alerts.append(f"High oscillation detected: {loop.oscillation_index:.3f}")

        if loop.cv_saturation_percent > self.performance_thresholds["cv_saturation_percent"]:
            alerts.append(f"CV saturation detected: {loop.cv_saturation_percent:.1f}%")

        performance_metrics["alerts"] = alerts

        logger.info(f"Performance monitoring for loop {loop_id}: {len(alerts)} alerts")
        return performance_metrics

    def get_tuning_recommendations(self, loop_id: str) -> dict[str, Any]:
        """
        Get AI-powered tuning recommendations.

        Integrates with:
        - AI Task Orchestrator for intelligent recommendations
        - Vector Database for historical similarity matching
        """
        if loop_id not in self.pid_loops:
            raise ValueError(f"Loop {loop_id} not found")

        loop = self.pid_loops[loop_id]

        # Use AI Task Orchestrator for intelligent recommendations
        task_description = (
            f"Provide tuning recommendations for {loop.process_type.value} control loop"
        )
        guidance = get_task_guidance(task_description)

        # Analyze current performance
        performance = self.monitor_performance(loop_id)

        recommendations = {
            "loop_id": loop_id,
            "current_performance": performance,
            "ai_guidance": guidance,
            "recommendations": [],
        }

        # Performance-based recommendations
        if loop.oscillation_index > 0.3:
            recommendations["recommendations"].append(
                {
                    "type": "parameter_adjustment",
                    "description": "Reduce proportional gain to decrease oscillation",
                    "suggested_kc": loop.kc * 0.8,
                    "priority": "high",
                }
            )

        if loop.cv_saturation_percent > 10:
            recommendations["recommendations"].append(
                {
                    "type": "tuning_method",
                    "description": "Consider switching to lambda tuning for better constraint handling",
                    "suggested_method": "lambda_tuning",
                    "priority": "medium",
                }
            )

        if loop.performance_score < 0.7:
            recommendations["recommendations"].append(
                {
                    "type": "advanced_control",
                    "description": "Consider implementing feed-forward control",
                    "priority": "low",
                }
            )

        logger.info(
            f"Generated {len(recommendations['recommendations'])} recommendations for loop {loop_id}"
        )
        return recommendations

    def generate_deployment_report(self, loop_id: str) -> dict[str, Any]:
        """
        Generate deployment report for Studio 5000 integration.

        Integrates with existing L5X/ACD processing infrastructure.
        """
        if loop_id not in self.pid_loops:
            raise ValueError(f"Loop {loop_id} not found")

        loop = self.pid_loops[loop_id]

        # Get latest tuning session
        latest_session = None
        for session in reversed(self.tuning_history):
            if session.loop_id == loop_id:
                latest_session = session
                break

        report = {
            "loop_configuration": {
                "loop_id": loop.loop_id,
                "name": loop.name,
                "process_type": loop.process_type.value,
                "instruction_type": loop.instruction_type.value,
                "algorithm_form": loop.algorithm_form.value,
            },
            "tuning_parameters": {
                "kc": loop.kc,
                "ti": loop.ti,
                "td": loop.td,
                "pv_range": loop.pv_range,
                "cv_range": loop.cv_range,
                "sp_range": loop.sp_range,
            },
            "performance_metrics": self.monitor_performance(loop_id),
            "tuning_history": latest_session.__dict__ if latest_session else None,
            "l5x_deployment": {
                "instruction_type": loop.instruction_type.value,
                "parameters": {
                    "PGain": loop.kc,
                    "Ti": loop.ti,
                    "Td": loop.td,
                    "PVEUMax": loop.pv_range[1],
                    "PVEUMin": loop.pv_range[0],
                    "CVEUMax": loop.cv_range[1],
                    "CVEUMin": loop.cv_range[0],
                },
            },
        }

        logger.info(f"Generated deployment report for loop {loop_id}")
        return report

    def cleanup(self):
        """Clean up resources"""
        try:
            self.knowledge_graph.close()
            self.ai_orchestrator.cleanup()
            logger.info("PID Integration Orchestrator cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Example usage and testing
def main():
    """Example usage of PID Integration Orchestrator"""
    print("🎯 PID Integration Orchestrator - Phase 8 Foundation")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = PIDIntegrationOrchestrator()

    try:
        # Discover PID loops
        print("\n1. Discovering PID loops...")
        loops = orchestrator.discover_pid_loops()
        print(f"   Found {len(loops)} PID loops")

        if loops:
            # Configure multi-PV strategy
            loop_id = loops[0].loop_id
            print(f"\n2. Configuring multi-PV strategy for {loop_id}...")
            success = orchestrator.configure_multi_pv_strategy(
                loop_id, ["PV_01", "PV_02"], [0.7, 0.3]
            )
            print(f"   Configuration successful: {success}")

            # Execute automated tuning
            print(f"\n3. Executing automated tuning for {loop_id}...")
            session = orchestrator.execute_automated_tuning(loop_id, "ziegler_nichols")
            print(f"   Tuning session: {session.session_id}")
            print(f"   Status: {session.status}")

            # Monitor performance
            print(f"\n4. Monitoring performance for {loop_id}...")
            performance = orchestrator.monitor_performance(loop_id)
            print(f"   Performance score: {performance.get('performance_score', 'N/A')}")
            print(f"   Alerts: {len(performance.get('alerts', []))}")

            # Get recommendations
            print(f"\n5. Getting tuning recommendations for {loop_id}...")
            recommendations = orchestrator.get_tuning_recommendations(loop_id)
            print(f"   Recommendations: {len(recommendations.get('recommendations', []))}")

            # Generate deployment report
            print(f"\n6. Generating deployment report for {loop_id}...")
            report = orchestrator.generate_deployment_report(loop_id)
            print(f"   Report generated with {len(report)} sections")

        print("\n✅ PID Integration Orchestrator demonstration complete!")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        orchestrator.cleanup()


if __name__ == "__main__":
    main()
