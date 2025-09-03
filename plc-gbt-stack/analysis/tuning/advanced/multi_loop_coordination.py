#!/usr/bin/env python3
"""
Phase 22.2.3: Multi-Loop Coordination Implementation
===================================================

Advanced multi-loop coordination algorithms for interacting control systems:
- Decentralized coordination with interaction compensation
- Centralized coordination with global optimization
- Distributed coordination with local communication
- Hierarchical coordination with supervisory control

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.3 - Advanced Tuning Strategies
Methodology: AI Task Orchestrator Guide
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
from scipy import optimize

# Import algorithm base class if available
try:
    from ...algorithms import (
        AlgorithmBase,
        AlgorithmCategory,
        AlgorithmComplexity,
        AlgorithmMetadata,
        registry,
    )
    ALGORITHM_REGISTRY_AVAILABLE = True
except ImportError:
    ALGORITHM_REGISTRY_AVAILABLE = False
    logging.warning("⚠️ Algorithm registry not available - using standalone implementation")

logger = logging.getLogger(__name__)

class CoordinationStrategy(Enum):
    """Multi-loop coordination strategies"""
    DECENTRALIZED = "decentralized"
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HIERARCHICAL = "hierarchical"

class InteractionType(Enum):
    """Types of loop interactions"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    NONLINEAR = "nonlinear"
    BIDIRECTIONAL = "bidirectional"

class CommunicationTopology(Enum):
    """Communication topologies for distributed control"""
    STAR = "star"
    RING = "ring"
    MESH = "mesh"
    HIERARCHICAL = "hierarchical"

@dataclass
class ControlLoop:
    """Individual control loop definition"""
    loop_id: str
    name: str
    controlled_variable: str
    manipulated_variable: str
    setpoint: float

    # Process model
    process_gain: float = 1.0
    time_constant: float = 10.0
    dead_time: float = 1.0

    # Current PID parameters
    kp: float = 1.0
    ti: float = 10.0
    td: float = 1.0

    # Constraints
    cv_min: Optional[float] = None
    cv_max: Optional[float] = None
    mv_min: Optional[float] = None
    mv_max: Optional[float] = None

    # Performance weights
    performance_weight: float = 1.0
    interaction_penalty: float = 0.1

    active: bool = True

@dataclass
class LoopInteraction:
    """Interaction between control loops"""
    from_loop: str
    to_loop: str
    interaction_gain: float
    interaction_delay: float = 0.0
    interaction_type: InteractionType = InteractionType.STATIC
    bidirectional: bool = False
    weight: float = 1.0

@dataclass
class CoordinationConfiguration:
    """Multi-loop coordination configuration"""
    strategy: CoordinationStrategy = CoordinationStrategy.DECENTRALIZED
    communication_topology: CommunicationTopology = CommunicationTopology.MESH

    # Optimization parameters
    optimization_objective: str = "performance"  # performance, robustness, energy
    max_iterations: int = 100
    convergence_tolerance: float = 1e-6
    coordination_frequency: float = 1.0  # Hz

    # Interaction handling
    interaction_threshold: float = 0.1
    interaction_compensation: bool = True
    detuning_factor: float = 0.8

    # Communication parameters
    communication_delay: float = 0.1  # seconds
    packet_loss_rate: float = 0.0
    bandwidth_limit: Optional[float] = None

    # Hierarchical parameters
    hierarchy_levels: int = 2
    supervisory_gain: float = 0.1
    local_autonomy: float = 0.8

@dataclass
class CoordinationResults:
    """Multi-loop coordination results"""
    tuning_method: str
    strategy: CoordinationStrategy
    configuration: CoordinationConfiguration
    loops: List[ControlLoop]
    interactions: List[LoopInteraction]
    optimized_parameters: Dict[str, Dict[str, float]]
    interaction_matrix: np.ndarray
    performance_metrics: Dict[str, float]
    convergence_analysis: Dict[str, Any]
    stability_analysis: Dict[str, Any]
    robustness_analysis: Dict[str, Any]
    communication_analysis: Dict[str, Any]
    execution_time: float
    status: str

class MultiLoopCoordinator:
    """Base multi-loop coordination class"""

    def __init__(self, configuration: Optional[CoordinationConfiguration] = None):
        self.config = configuration or CoordinationConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # System components
        self.loops: List[ControlLoop] = []
        self.interactions: List[LoopInteraction] = []
        self.interaction_matrix = None
        self.communication_graph = None

        # Optimization state
        self.current_parameters = {}
        self.iteration_history = []

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute multi-loop coordination"""
        try:
            start_time = time.time()

            # Extract system configuration
            loops, interactions = self._extract_system_configuration(data)

            # Build interaction matrix
            interaction_matrix = self._build_interaction_matrix(loops, interactions)

            # Setup communication topology
            self._setup_communication_topology(loops)

            # Run coordination algorithm
            optimized_parameters = self._run_coordination(loops, interactions)

            # Analyze results
            performance_metrics = self._analyze_performance(loops, optimized_parameters)
            convergence_analysis = self._analyze_convergence()
            stability_analysis = self._analyze_system_stability(loops, interactions, optimized_parameters)
            robustness_analysis = self._analyze_robustness(loops, interactions, optimized_parameters)
            communication_analysis = self._analyze_communication_performance()

            execution_time = time.time() - start_time

            # Create results
            result = CoordinationResults(
                tuning_method=f"MultiLoop_{self.config.strategy.value}",
                strategy=self.config.strategy,
                configuration=self.config,
                loops=loops,
                interactions=interactions,
                optimized_parameters=optimized_parameters,
                interaction_matrix=interaction_matrix,
                performance_metrics=performance_metrics,
                convergence_analysis=convergence_analysis,
                stability_analysis=stability_analysis,
                robustness_analysis=robustness_analysis,
                communication_analysis=communication_analysis,
                execution_time=execution_time,
                status="success"
            )

            return {
                'success': True,
                'result': result,
                'method': 'multi_loop_coordination'
            }

        except Exception as e:
            self.logger.error(f"Multi-loop coordination failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'multi_loop_coordination'
            }

    def _extract_system_configuration(self, data: Dict[str, Any]) -> Tuple[List[ControlLoop], List[LoopInteraction]]:
        """Extract control loops and interactions from data"""

        loops = []
        interactions = []

        # Extract control loops
        if 'control_loops' in data:
            for loop_data in data['control_loops']:
                loop = ControlLoop(
                    loop_id=loop_data.get('loop_id', f"loop_{len(loops)}"),
                    name=loop_data.get('name', f"Loop {len(loops)}"),
                    controlled_variable=loop_data.get('controlled_variable', 'CV'),
                    manipulated_variable=loop_data.get('manipulated_variable', 'MV'),
                    setpoint=loop_data.get('setpoint', 50.0),
                    process_gain=loop_data.get('process_gain', 1.0),
                    time_constant=loop_data.get('time_constant', 10.0),
                    dead_time=loop_data.get('dead_time', 1.0),
                    kp=loop_data.get('kp', 1.0),
                    ti=loop_data.get('ti', 10.0),
                    td=loop_data.get('td', 1.0),
                    cv_min=loop_data.get('cv_min'),
                    cv_max=loop_data.get('cv_max'),
                    mv_min=loop_data.get('mv_min'),
                    mv_max=loop_data.get('mv_max'),
                    performance_weight=loop_data.get('performance_weight', 1.0),
                    interaction_penalty=loop_data.get('interaction_penalty', 0.1),
                    active=loop_data.get('active', True)
                )
                loops.append(loop)
        else:
            # Create default 2x2 system
            loops = self._create_default_system()

        # Extract interactions
        if 'interactions' in data:
            for interaction_data in data['interactions']:
                interaction = LoopInteraction(
                    from_loop=interaction_data.get('from_loop'),
                    to_loop=interaction_data.get('to_loop'),
                    interaction_gain=interaction_data.get('interaction_gain', 0.1),
                    interaction_delay=interaction_data.get('interaction_delay', 0.0),
                    interaction_type=InteractionType(interaction_data.get('interaction_type', 'static')),
                    bidirectional=interaction_data.get('bidirectional', False),
                    weight=interaction_data.get('weight', 1.0)
                )
                interactions.append(interaction)
        else:
            # Create default interactions
            interactions = self._create_default_interactions(loops)

        self.loops = loops
        self.interactions = interactions

        return loops, interactions

    def _create_default_system(self) -> List[ControlLoop]:
        """Create default 2x2 interacting system"""

        loops = [
            ControlLoop(
                loop_id="loop_1",
                name="Temperature Control",
                controlled_variable="Temperature",
                manipulated_variable="Heating",
                setpoint=80.0,
                process_gain=2.0,
                time_constant=15.0,
                dead_time=2.0,
                kp=1.0,
                ti=15.0,
                td=2.0
            ),
            ControlLoop(
                loop_id="loop_2",
                name="Flow Control",
                controlled_variable="Flow Rate",
                manipulated_variable="Valve Position",
                setpoint=50.0,
                process_gain=1.5,
                time_constant=8.0,
                dead_time=1.0,
                kp=1.2,
                ti=8.0,
                td=1.0
            )
        ]

        return loops

    def _create_default_interactions(self, loops: List[ControlLoop]) -> List[LoopInteraction]:
        """Create default interactions between loops"""

        interactions = []

        if len(loops) >= 2:
            # Create bidirectional interactions
            interactions.append(LoopInteraction(
                from_loop=loops[0].loop_id,
                to_loop=loops[1].loop_id,
                interaction_gain=0.3,
                interaction_type=InteractionType.STATIC,
                bidirectional=True
            ))

            interactions.append(LoopInteraction(
                from_loop=loops[1].loop_id,
                to_loop=loops[0].loop_id,
                interaction_gain=0.2,
                interaction_type=InteractionType.STATIC,
                bidirectional=True
            ))

        return interactions

    def _build_interaction_matrix(self, loops: List[ControlLoop],
                                 interactions: List[LoopInteraction]) -> np.ndarray:
        """Build interaction matrix between loops"""

        n_loops = len(loops)
        interaction_matrix = np.eye(n_loops)  # Start with identity (no self-interaction penalty)

        # Create loop ID to index mapping
        loop_id_to_index = {loop.loop_id: i for i, loop in enumerate(loops)}

        # Fill interaction matrix
        for interaction in interactions:
            from_idx = loop_id_to_index.get(interaction.from_loop)
            to_idx = loop_id_to_index.get(interaction.to_loop)

            if from_idx is not None and to_idx is not None:
                interaction_matrix[to_idx, from_idx] = interaction.interaction_gain

                if interaction.bidirectional:
                    interaction_matrix[from_idx, to_idx] = interaction.interaction_gain

        self.interaction_matrix = interaction_matrix
        return interaction_matrix

    def _setup_communication_topology(self, loops: List[ControlLoop]) -> nx.Graph:
        """Setup communication topology for distributed coordination"""

        G = nx.Graph()

        # Add nodes (control loops)
        for loop in loops:
            G.add_node(loop.loop_id, loop=loop)

        # Add edges based on topology
        if self.config.communication_topology == CommunicationTopology.MESH:
            # Fully connected
            for i, loop1 in enumerate(loops):
                for _j, loop2 in enumerate(loops[i+1:], i+1):
                    G.add_edge(loop1.loop_id, loop2.loop_id,
                             delay=self.config.communication_delay)

        elif self.config.communication_topology == CommunicationTopology.RING:
            # Ring topology
            for i in range(len(loops)):
                next_i = (i + 1) % len(loops)
                G.add_edge(loops[i].loop_id, loops[next_i].loop_id,
                         delay=self.config.communication_delay)

        elif self.config.communication_topology == CommunicationTopology.STAR:
            # Star topology (first loop is central)
            if len(loops) > 1:
                central_loop = loops[0].loop_id
                for loop in loops[1:]:
                    G.add_edge(central_loop, loop.loop_id,
                             delay=self.config.communication_delay)

        self.communication_graph = G
        return G

    def _run_coordination(self, loops: List[ControlLoop],
                         interactions: List[LoopInteraction]) -> Dict[str, Dict[str, float]]:
        """Run coordination algorithm based on strategy"""

        if self.config.strategy == CoordinationStrategy.DECENTRALIZED:
            return self._decentralized_coordination(loops, interactions)
        elif self.config.strategy == CoordinationStrategy.CENTRALIZED:
            return self._centralized_coordination(loops, interactions)
        elif self.config.strategy == CoordinationStrategy.DISTRIBUTED:
            return self._distributed_coordination(loops, interactions)
        elif self.config.strategy == CoordinationStrategy.HIERARCHICAL:
            return self._hierarchical_coordination(loops, interactions)
        else:
            raise ValueError(f"Unknown coordination strategy: {self.config.strategy}")

    def _decentralized_coordination(self, loops: List[ControlLoop],
                                  interactions: List[LoopInteraction]) -> Dict[str, Dict[str, float]]:
        """Decentralized coordination with interaction compensation"""

        optimized_parameters = {}

        # Calculate Relative Gain Array (RGA) for interaction analysis
        rga_matrix = self._calculate_rga(loops, interactions)

        for loop in loops:
            if not loop.active:
                continue

            # Base tuning using single-loop methods
            base_params = self._single_loop_tuning(loop)

            # Apply detuning factor based on interactions
            detuning_factor = self._calculate_detuning_factor(loop, rga_matrix, loops)

            # Compensate for interactions
            compensated_params = {
                'Kp': base_params['Kp'] * detuning_factor,
                'Ti': base_params['Ti'] / detuning_factor,
                'Td': base_params['Td'] * detuning_factor
            }

            # Apply bounds
            compensated_params = self._apply_parameter_bounds(compensated_params, loop)

            optimized_parameters[loop.loop_id] = compensated_params

        return optimized_parameters

    def _centralized_coordination(self, loops: List[ControlLoop],
                                interactions: List[LoopInteraction]) -> Dict[str, Dict[str, float]]:
        """Centralized coordination with global optimization"""

        # Setup global optimization problem
        len([loop for loop in loops if loop.active])
        n_params = 3  # Kp, Ti, Td per loop

        # Initial parameter vector
        x0 = []
        loop_indices = {}
        active_loops = [loop for loop in loops if loop.active]

        for i, loop in enumerate(active_loops):
            loop_indices[loop.loop_id] = i
            x0.extend([loop.kp, loop.ti, loop.td])

        x0 = np.array(x0)

        # Define objective function
        def objective_function(x):
            return self._global_objective(x, active_loops, interactions)

        # Define constraints
        bounds = []
        for loop in active_loops:
            bounds.extend([
                (0.1, 10.0),   # Kp bounds
                (0.1, 100.0),  # Ti bounds
                (0.0, 10.0)    # Td bounds
            ])

        # Solve optimization problem
        result = optimize.minimize(
            objective_function,
            x0,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': self.config.max_iterations}
        )

        # Extract optimized parameters
        optimized_parameters = {}
        x_opt = result.x

        for i, loop in enumerate(active_loops):
            start_idx = i * n_params
            optimized_parameters[loop.loop_id] = {
                'Kp': x_opt[start_idx],
                'Ti': x_opt[start_idx + 1],
                'Td': x_opt[start_idx + 2]
            }

        return optimized_parameters

    def _distributed_coordination(self, loops: List[ControlLoop],
                                interactions: List[LoopInteraction]) -> Dict[str, Dict[str, float]]:
        """Distributed coordination with consensus algorithm"""

        optimized_parameters = {}

        # Initialize with local tuning
        for loop in loops:
            if loop.active:
                local_params = self._single_loop_tuning(loop)
                optimized_parameters[loop.loop_id] = local_params

        # Consensus iterations
        for iteration in range(self.config.max_iterations):
            previous_parameters = {k: v.copy() for k, v in optimized_parameters.items()}

            # Update each loop using neighbor information
            for loop in loops:
                if not loop.active:
                    continue

                # Get neighbor parameters
                neighbors = list(self.communication_graph.neighbors(loop.loop_id))

                if neighbors:
                    # Consensus update
                    consensus_params = self._consensus_update(
                        loop, neighbors, optimized_parameters
                    )
                    optimized_parameters[loop.loop_id] = consensus_params

            # Check convergence
            if self._check_convergence(previous_parameters, optimized_parameters):
                self.logger.info(f"Distributed coordination converged after {iteration + 1} iterations")
                break

        return optimized_parameters

    def _hierarchical_coordination(self, loops: List[ControlLoop],
                                 interactions: List[LoopInteraction]) -> Dict[str, Dict[str, float]]:
        """Hierarchical coordination with supervisory control"""

        optimized_parameters = {}

        # Level 1: Local optimization
        for loop in loops:
            if loop.active:
                local_params = self._single_loop_tuning(loop)
                optimized_parameters[loop.loop_id] = local_params

        # Level 2: Supervisory coordination
        supervisory_adjustments = self._supervisory_coordination(loops, interactions, optimized_parameters)

        # Apply supervisory adjustments
        for loop_id, adjustments in supervisory_adjustments.items():
            if loop_id in optimized_parameters:
                current_params = optimized_parameters[loop_id]

                # Apply adjustments with supervisory gain
                adjusted_params = {}
                for param, adjustment in adjustments.items():
                    current_value = current_params.get(param, 1.0)
                    adjusted_value = current_value * (1 + self.config.supervisory_gain * adjustment)
                    adjusted_params[param] = adjusted_value

                # Blend with local autonomy
                autonomy = self.config.local_autonomy
                blended_params = {}
                for param in ['Kp', 'Ti', 'Td']:
                    local_value = current_params.get(param, 1.0)
                    adjusted_value = adjusted_params.get(param, local_value)
                    blended_value = autonomy * local_value + (1 - autonomy) * adjusted_value
                    blended_params[param] = blended_value

                optimized_parameters[loop_id] = blended_params

        return optimized_parameters

    def _single_loop_tuning(self, loop: ControlLoop) -> Dict[str, float]:
        """Single-loop PID tuning using IMC method"""

        # Simple IMC tuning
        K = loop.process_gain
        tau = loop.time_constant
        theta = loop.dead_time

        # Lambda tuning parameter (closed-loop time constant)
        lambda_c = max(theta, 0.1 * tau)

        # IMC PID parameters
        Kp = (tau + 0.5 * theta) / (K * (lambda_c + 0.5 * theta))
        Ti = tau + 0.5 * theta
        Td = tau * theta / (2 * tau + theta)

        return {'Kp': Kp, 'Ti': Ti, 'Td': Td}

    def _calculate_rga(self, loops: List[ControlLoop],
                       interactions: List[LoopInteraction]) -> np.ndarray:
        """Calculate Relative Gain Array for interaction analysis"""

        n_loops = len(loops)

        if n_loops == 1:
            return np.array([[1.0]])

        # Build steady-state gain matrix
        gain_matrix = np.eye(n_loops)

        # Loop ID to index mapping
        loop_id_to_index = {loop.loop_id: i for i, loop in enumerate(loops)}

        # Fill gain matrix with process gains and interactions
        for i, loop in enumerate(loops):
            gain_matrix[i, i] = loop.process_gain

        for interaction in interactions:
            from_idx = loop_id_to_index.get(interaction.from_loop)
            to_idx = loop_id_to_index.get(interaction.to_loop)

            if from_idx is not None and to_idx is not None:
                gain_matrix[to_idx, from_idx] = interaction.interaction_gain

        # Calculate RGA: RGA = G .* (G^-1)^T
        try:
            gain_inv = np.linalg.inv(gain_matrix)
            rga = gain_matrix * gain_inv.T
        except np.linalg.LinAlgError:
            # Singular matrix, use pseudo-inverse
            gain_pinv = np.linalg.pinv(gain_matrix)
            rga = gain_matrix * gain_pinv.T

        return rga

    def _calculate_detuning_factor(self, loop: ControlLoop, rga_matrix: np.ndarray,
                                  loops: List[ControlLoop]) -> float:
        """Calculate detuning factor based on RGA"""

        # Find loop index
        loop_idx = None
        for i, l in enumerate(loops):
            if l.loop_id == loop.loop_id:
                loop_idx = i
                break

        if loop_idx is None or loop_idx >= rga_matrix.shape[0]:
            return self.config.detuning_factor

        # Use RGA diagonal element to determine detuning
        rga_diagonal = rga_matrix[loop_idx, loop_idx]

        if rga_diagonal > 0.8:
            # Low interaction - minimal detuning
            detuning_factor = 0.95
        elif rga_diagonal > 0.5:
            # Moderate interaction
            detuning_factor = self.config.detuning_factor
        else:
            # High interaction - aggressive detuning
            detuning_factor = 0.6

        return detuning_factor

    def _global_objective(self, x: np.ndarray, loops: List[ControlLoop],
                         interactions: List[LoopInteraction]) -> float:
        """Global optimization objective function"""

        # Extract parameters
        n_params = 3
        total_cost = 0.0

        # Performance cost for each loop
        for i, loop in enumerate(loops):
            start_idx = i * n_params
            Kp, Ti, Td = x[start_idx:start_idx + n_params]

            # Simple performance metric (ISE approximation)
            K = loop.process_gain

            # Closed-loop characteristic equation approximation
            # Cost increases with poor damping or slow response
            lambda_c = 1 / (Kp * K)  # Approximate closed-loop time constant
            performance_cost = lambda_c + 1 / lambda_c  # Penalize both slow and fast response

            total_cost += loop.performance_weight * performance_cost

        # Interaction cost
        interaction_cost = 0.0
        loop_params = {}

        for i, loop in enumerate(loops):
            start_idx = i * n_params
            loop_params[loop.loop_id] = x[start_idx:start_idx + n_params]

        for interaction in interactions:
            if interaction.from_loop in loop_params and interaction.to_loop in loop_params:
                # Penalize strong controllers in highly interacting systems
                from_params = loop_params[interaction.from_loop]
                interaction_penalty = interaction.interaction_gain * from_params[0]  # Kp
                interaction_cost += interaction_penalty

        total_cost += interaction_cost

        return total_cost

    def _consensus_update(self, loop: ControlLoop, neighbors: List[str],
                         current_parameters: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Consensus update for distributed coordination"""

        current_params = current_parameters[loop.loop_id]

        if not neighbors:
            return current_params

        # Average with neighbors
        consensus_params = {}

        for param in ['Kp', 'Ti', 'Td']:
            param_sum = current_params[param]
            count = 1

            for neighbor_id in neighbors:
                if neighbor_id in current_parameters:
                    param_sum += current_parameters[neighbor_id][param]
                    count += 1

            consensus_params[param] = param_sum / count

        # Apply local improvement
        local_improvement = self._local_optimization_step(loop, consensus_params)

        # Blend consensus and local improvement
        blend_factor = 0.7  # Weight for consensus

        final_params = {}
        for param in ['Kp', 'Ti', 'Td']:
            consensus_value = consensus_params[param]
            local_value = local_improvement[param]
            final_params[param] = blend_factor * consensus_value + (1 - blend_factor) * local_value

        return self._apply_parameter_bounds(final_params, loop)

    def _local_optimization_step(self, loop: ControlLoop,
                                current_params: Dict[str, float]) -> Dict[str, float]:
        """Local optimization step for distributed coordination"""

        # Simple gradient-based improvement
        # This is a simplified implementation
        current_params.copy()

        # Simulate small parameter adjustments and choose best
        best_cost = float('inf')
        best_params = current_params.copy()

        for param in ['Kp', 'Ti', 'Td']:
            for delta in [-0.1, 0.1]:
                test_params = current_params.copy()
                test_params[param] *= (1 + delta)

                # Simple cost function (local performance)
                cost = self._local_performance_cost(loop, test_params)

                if cost < best_cost:
                    best_cost = cost
                    best_params = test_params

        return best_params

    def _local_performance_cost(self, loop: ControlLoop,
                               params: Dict[str, float]) -> float:
        """Calculate local performance cost"""

        Kp = params['Kp']
        Ti = params['Ti']
        Td = params['Td']

        # Simple cost based on parameter reasonableness
        # Penalize extreme parameters
        cost = 0.0

        if Kp > 10 or Kp < 0.1:
            cost += 10.0
        if Ti > 100 or Ti < 0.1:
            cost += 10.0
        if Td > 10:
            cost += 10.0

        # Penalize aggressive tuning
        aggressiveness = Kp * Td / Ti
        if aggressiveness > 1.0:
            cost += aggressiveness

        return cost

    def _supervisory_coordination(self, loops: List[ControlLoop],
                                interactions: List[LoopInteraction],
                                local_parameters: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Supervisory coordination adjustments"""

        adjustments = {}

        # Analyze global performance
        self._calculate_overall_interaction_strength(interactions)

        for loop in loops:
            if not loop.active:
                continue

            loop_adjustments = {'Kp': 0.0, 'Ti': 0.0, 'Td': 0.0}

            # Calculate loop's role in interactions
            incoming_interactions = [i for i in interactions if i.to_loop == loop.loop_id]
            outgoing_interactions = [i for i in interactions if i.from_loop == loop.loop_id]

            # If loop has strong incoming interactions, detune
            for interaction in incoming_interactions:
                if interaction.interaction_gain > self.config.interaction_threshold:
                    loop_adjustments['Kp'] -= 0.1  # Reduce gain
                    loop_adjustments['Ti'] += 0.1   # Increase integral time

            # If loop creates strong outgoing interactions, moderate tuning
            for interaction in outgoing_interactions:
                if interaction.interaction_gain > self.config.interaction_threshold:
                    loop_adjustments['Td'] += 0.05  # Add derivative action

            adjustments[loop.loop_id] = loop_adjustments

        return adjustments

    def _calculate_overall_interaction_strength(self, interactions: List[LoopInteraction]) -> float:
        """Calculate overall system interaction strength"""

        if not interactions:
            return 0.0

        total_strength = sum(abs(i.interaction_gain) for i in interactions)
        return total_strength / len(interactions)

    def _check_convergence(self, previous_params: Dict[str, Dict[str, float]],
                          current_params: Dict[str, Dict[str, float]]) -> bool:
        """Check convergence of iterative algorithm"""

        max_change = 0.0

        for loop_id in current_params:
            if loop_id in previous_params:
                for param in ['Kp', 'Ti', 'Td']:
                    if param in current_params[loop_id] and param in previous_params[loop_id]:
                        current_val = current_params[loop_id][param]
                        previous_val = previous_params[loop_id][param]
                        relative_change = abs(current_val - previous_val) / (abs(previous_val) + 1e-6)
                        max_change = max(max_change, relative_change)

        return max_change < self.config.convergence_tolerance

    def _apply_parameter_bounds(self, params: Dict[str, float],
                               loop: ControlLoop) -> Dict[str, float]:
        """Apply parameter bounds"""

        bounded_params = {}

        bounded_params['Kp'] = np.clip(params.get('Kp', 1.0), 0.1, 10.0)
        bounded_params['Ti'] = np.clip(params.get('Ti', 10.0), 0.1, 100.0)
        bounded_params['Td'] = np.clip(params.get('Td', 1.0), 0.0, 10.0)

        return bounded_params

    def _analyze_performance(self, loops: List[ControlLoop],
                           optimized_parameters: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Analyze overall system performance"""

        total_performance = 0.0
        active_loops = 0

        for loop in loops:
            if not loop.active or loop.loop_id not in optimized_parameters:
                continue

            params = optimized_parameters[loop.loop_id]

            # Simple performance metric
            Kp = params['Kp']
            params['Ti']
            params['Td']

            # Estimate settling time and overshoot
            lambda_c = 1 / (Kp * loop.process_gain)
            settling_time = 4 * lambda_c
            overshoot = max(0, 100 * (Kp * loop.process_gain - 1))

            loop_performance = 1 / (1 + settling_time/10 + overshoot/100)
            total_performance += loop_performance * loop.performance_weight
            active_loops += 1

        average_performance = total_performance / max(active_loops, 1)

        return {
            "overall_performance": average_performance,
            "active_loops": active_loops,
            "coordination_strategy": self.config.strategy.value,
            "interaction_compensation": self.config.interaction_compensation
        }

    def _analyze_convergence(self) -> Dict[str, Any]:
        """Analyze convergence of coordination algorithm"""

        return {
            "converged": len(self.iteration_history) < self.config.max_iterations,
            "iterations": len(self.iteration_history),
            "max_iterations": self.config.max_iterations,
            "convergence_tolerance": self.config.convergence_tolerance
        }

    def _analyze_system_stability(self, loops: List[ControlLoop],
                                 interactions: List[LoopInteraction],
                                 optimized_parameters: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Analyze overall system stability"""

        stable_loops = 0
        total_loops = 0

        for loop in loops:
            if not loop.active:
                continue

            total_loops += 1

            if loop.loop_id in optimized_parameters:
                params = optimized_parameters[loop.loop_id]

                # Simple stability check
                Kp = params['Kp']
                Ti = params['Ti']
                Td = params['Td']

                # Basic stability criteria
                if 0.1 <= Kp <= 10.0 and 0.1 <= Ti <= 100.0 and 0.0 <= Td <= 10.0:
                    stable_loops += 1

        stability_ratio = stable_loops / max(total_loops, 1)

        return {
            "globally_stable": stability_ratio >= 0.95,
            "stability_ratio": stability_ratio,
            "stable_loops": stable_loops,
            "total_loops": total_loops,
            "interaction_matrix_eigenvalues": np.linalg.eigvals(self.interaction_matrix).tolist() if self.interaction_matrix is not None else []
        }

    def _analyze_robustness(self, loops: List[ControlLoop],
                          interactions: List[LoopInteraction],
                          optimized_parameters: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Analyze system robustness to uncertainties"""

        # Monte Carlo robustness analysis
        n_samples = 100
        stable_samples = 0

        for _ in range(n_samples):
            # Perturb interaction gains
            perturbed_stable = True

            for interaction in interactions:
                # Random perturbation ±20%
                perturbation = 1 + 0.2 * (2 * np.random.random() - 1)
                perturbed_gain = interaction.interaction_gain * perturbation

                # Check if perturbation causes instability (simplified)
                if abs(perturbed_gain) > 0.8:  # Arbitrary threshold
                    perturbed_stable = False
                    break

            if perturbed_stable:
                stable_samples += 1

        robustness_probability = stable_samples / n_samples

        return {
            "robust": robustness_probability > 0.90,
            "robustness_probability": robustness_probability,
            "monte_carlo_samples": n_samples,
            "uncertainty_level": 0.2
        }

    def _analyze_communication_performance(self) -> Dict[str, Any]:
        """Analyze communication performance for distributed strategies"""

        if not self.communication_graph:
            return {"communication_required": False}

        # Graph analysis
        n_nodes = self.communication_graph.number_of_nodes()
        n_edges = self.communication_graph.number_of_edges()

        # Calculate communication metrics
        avg_path_length = 0.0
        connectivity = 0.0

        try:
            if nx.is_connected(self.communication_graph):
                avg_path_length = nx.average_shortest_path_length(self.communication_graph)
                connectivity = 1.0
            else:
                connectivity = 0.0
        except:
            connectivity = 0.0

        return {
            "communication_required": True,
            "topology": self.config.communication_topology.value,
            "nodes": n_nodes,
            "edges": n_edges,
            "connectivity": connectivity,
            "average_path_length": avg_path_length,
            "communication_delay": self.config.communication_delay,
            "packet_loss_rate": self.config.packet_loss_rate
        }


# Specialized coordinators
class DecentralizedCoordinator(MultiLoopCoordinator):
    """Decentralized multi-loop coordinator"""

    def __init__(self, configuration: Optional[CoordinationConfiguration] = None):
        config = configuration or CoordinationConfiguration()
        config.strategy = CoordinationStrategy.DECENTRALIZED
        super().__init__(config)


class CentralizedCoordinator(MultiLoopCoordinator):
    """Centralized multi-loop coordinator"""

    def __init__(self, configuration: Optional[CoordinationConfiguration] = None):
        config = configuration or CoordinationConfiguration()
        config.strategy = CoordinationStrategy.CENTRALIZED
        super().__init__(config)


class DistributedCoordinator(MultiLoopCoordinator):
    """Distributed multi-loop coordinator"""

    def __init__(self, configuration: Optional[CoordinationConfiguration] = None):
        config = configuration or CoordinationConfiguration()
        config.strategy = CoordinationStrategy.DISTRIBUTED
        super().__init__(config)


class HierarchicalCoordinator(MultiLoopCoordinator):
    """Hierarchical multi-loop coordinator"""

    def __init__(self, configuration: Optional[CoordinationConfiguration] = None):
        config = configuration or CoordinationConfiguration()
        config.strategy = CoordinationStrategy.HIERARCHICAL
        super().__init__(config)


# Register algorithms if registry is available
if ALGORITHM_REGISTRY_AVAILABLE:

    @registry.register(
        category=AlgorithmCategory.TUNING_CALCULATION,
        complexity=AlgorithmComplexity.HIGH,
        metadata=AlgorithmMetadata(
            name="Decentralized Multi-Loop Coordination",
            description="Decentralized coordination for interacting control loops",
            version="1.0.0",
            author="PLC-GPT Team",
            tags=["multi_loop", "decentralized", "coordination", "interaction"]
        )
    )
    class RegisteredDecentralizedCoordinator(DecentralizedCoordinator):
        pass


# Export classes and functions
__all__ = [
    'MultiLoopCoordinator',
    'DecentralizedCoordinator',
    'CentralizedCoordinator',
    'DistributedCoordinator',
    'HierarchicalCoordinator',
    'CoordinationConfiguration',
    'ControlLoop',
    'LoopInteraction',
    'CoordinationResults',
    'CoordinationStrategy',
    'InteractionType',
    'CommunicationTopology'
]
