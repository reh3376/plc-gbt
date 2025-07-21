"""
AI Workflow Optimizer
Phase 26.4.2: AI-Enhanced Workflow Optimization

Provides intelligent workflow performance analysis, optimization suggestions,
automatic workflow improvement, and predictive maintenance recommendations.
"""

import json
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import re

# Import Phase 23 LLM components and workflow parser
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../llm'))

from nl_workflow_parser import (
    WorkflowDefinition, WorkflowNode, WorkflowConnection, WorkflowType, NodeType
)

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Types of workflow optimizations"""
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    COST = "cost"
    SAFETY = "safety"
    MAINTAINABILITY = "maintainability"
    SCALABILITY = "scalability"
    ENERGY_EFFICIENCY = "energy_efficiency"
    COMPLIANCE = "compliance"

class OptimizationPriority(Enum):
    """Priority levels for optimizations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NICE_TO_HAVE = "nice_to_have"

class PerformanceMetric(Enum):
    """Performance metrics for workflow analysis"""
    EXECUTION_TIME = "execution_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    LATENCY = "latency"
    SUCCESS_RATE = "success_rate"
    COST_PER_EXECUTION = "cost_per_execution"
    ENERGY_CONSUMPTION = "energy_consumption"

@dataclass
class WorkflowMetrics:
    """Performance metrics for a workflow"""
    execution_time_avg: float = 0.0
    execution_time_p95: float = 0.0
    execution_time_p99: float = 0.0
    throughput_per_hour: float = 0.0
    error_rate: float = 0.0
    success_rate: float = 100.0
    resource_usage_cpu: float = 0.0
    resource_usage_memory: float = 0.0
    cost_per_execution: float = 0.0
    total_executions: int = 0
    last_execution: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationRecommendation:
    """Individual optimization recommendation"""
    id: str
    optimization_type: OptimizationType
    priority: OptimizationPriority
    title: str
    description: str
    expected_improvement: str
    implementation_effort: str
    estimated_impact_score: float  # 0-100
    prerequisite_recommendations: List[str] = field(default_factory=list)
    implementation_steps: List[str] = field(default_factory=list)
    risk_assessment: str = ""
    cost_benefit_analysis: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowAnalysisResult:
    """Complete workflow analysis result"""
    workflow_id: str
    analysis_timestamp: datetime
    current_metrics: WorkflowMetrics
    performance_score: float  # 0-100
    reliability_score: float  # 0-100
    maintainability_score: float  # 0-100
    overall_health_score: float  # 0-100
    recommendations: List[OptimizationRecommendation] = field(default_factory=list)
    bottlenecks: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    compliance_issues: List[str] = field(default_factory=list)
    analysis_time_seconds: float = 0.0

@dataclass
class OptimizedWorkflow:
    """Optimized workflow with improvements applied"""
    original_workflow: WorkflowDefinition
    optimized_workflow: WorkflowDefinition
    applied_optimizations: List[OptimizationRecommendation]
    expected_improvements: Dict[str, float]
    validation_results: Dict[str, Any]
    optimization_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class WorkflowPerformanceAnalyzer:
    """Analyzes workflow performance and identifies bottlenecks"""
    
    def __init__(self):
        self.performance_patterns = {
            'serial_bottleneck': {
                'description': 'Sequential nodes causing performance bottleneck',
                'pattern': r'timer.*plc_read.*timer',
                'severity': 'medium'
            },
            'redundant_reads': {
                'description': 'Multiple reads of the same PLC tag',
                'pattern': r'plc_read.*plc_read',
                'severity': 'high'
            },
            'unoptimized_polling': {
                'description': 'High frequency polling without filtering',
                'pattern': r'polling_rate.*[0-9]{1,3}ms',
                'severity': 'medium'
            }
        }
    
    def analyze_workflow_performance(self, workflow: WorkflowDefinition, 
                                   metrics: Optional[WorkflowMetrics] = None) -> WorkflowAnalysisResult:
        """Perform comprehensive workflow performance analysis"""
        start_time = time.time()
        
        # Generate default metrics if not provided
        if metrics is None:
            metrics = self._generate_estimated_metrics(workflow)
        
        # Calculate performance scores
        performance_score = self._calculate_performance_score(workflow, metrics)
        reliability_score = self._calculate_reliability_score(workflow, metrics)
        maintainability_score = self._calculate_maintainability_score(workflow)
        overall_health_score = (performance_score + reliability_score + maintainability_score) / 3
        
        # Identify bottlenecks and issues
        bottlenecks = self._identify_bottlenecks(workflow, metrics)
        risk_factors = self._identify_risk_factors(workflow)
        compliance_issues = self._check_compliance(workflow)
        
        # Generate optimization recommendations
        recommendations = self._generate_recommendations(
            workflow, metrics, performance_score, reliability_score, maintainability_score
        )
        
        analysis_time = time.time() - start_time
        
        return WorkflowAnalysisResult(
            workflow_id=workflow.id,
            analysis_timestamp=datetime.now(timezone.utc),
            current_metrics=metrics,
            performance_score=performance_score,
            reliability_score=reliability_score,
            maintainability_score=maintainability_score,
            overall_health_score=overall_health_score,
            recommendations=recommendations,
            bottlenecks=bottlenecks,
            risk_factors=risk_factors,
            compliance_issues=compliance_issues,
            analysis_time_seconds=analysis_time
        )
    
    def _generate_estimated_metrics(self, workflow: WorkflowDefinition) -> WorkflowMetrics:
        """Generate estimated metrics based on workflow structure"""
        # Estimate execution time based on node count and types
        base_time = 1.0  # Base execution time in seconds
        time_per_node = 0.5
        
        # Different node types have different execution costs
        node_time_costs = {
            NodeType.PLC_READ: 0.1,
            NodeType.PLC_WRITE: 0.2,
            NodeType.DATABASE_QUERY: 0.3,
            NodeType.DATABASE_WRITE: 0.2,
            NodeType.PID_CONTROLLER: 0.05,
            NodeType.EMAIL: 1.0,
            NodeType.API_CALL: 0.5,
            NodeType.CONDITION: 0.01,
            NodeType.TIMER: 0.1
        }
        
        total_time = base_time
        for node in workflow.nodes:
            total_time += node_time_costs.get(node.type, time_per_node)
        
        # Add network latency for distributed operations
        plc_operations = len([n for n in workflow.nodes if 'plc' in n.type.value.lower()])
        if plc_operations > 0:
            total_time += plc_operations * 0.05  # 50ms per PLC operation
        
        # Estimate throughput and other metrics
        estimated_throughput = 3600 / total_time if total_time > 0 else 3600
        
        return WorkflowMetrics(
            execution_time_avg=total_time,
            execution_time_p95=total_time * 1.2,
            execution_time_p99=total_time * 1.5,
            throughput_per_hour=estimated_throughput,
            error_rate=2.0,  # Assume 2% error rate for new workflows
            success_rate=98.0,
            resource_usage_cpu=len(workflow.nodes) * 2.0,  # 2% CPU per node
            resource_usage_memory=len(workflow.nodes) * 10.0,  # 10MB per node
            cost_per_execution=total_time * 0.001,  # $0.001 per second
            total_executions=0,
            last_execution=None
        )
    
    def _calculate_performance_score(self, workflow: WorkflowDefinition, 
                                   metrics: WorkflowMetrics) -> float:
        """Calculate performance score (0-100)"""
        score = 100.0
        
        # Penalize slow execution times
        if metrics.execution_time_avg > 10.0:
            score -= min(30, (metrics.execution_time_avg - 10) * 2)
        
        # Penalize high error rates
        if metrics.error_rate > 1.0:
            score -= min(25, metrics.error_rate * 5)
        
        # Penalize high resource usage
        if metrics.resource_usage_cpu > 50.0:
            score -= min(20, (metrics.resource_usage_cpu - 50) * 0.4)
        
        # Reward good throughput
        if metrics.throughput_per_hour > 1000:
            score += min(10, (metrics.throughput_per_hour - 1000) / 100)
        
        # Penalize workflow complexity without optimization
        if len(workflow.nodes) > 10 and len(workflow.connections) < len(workflow.nodes):
            score -= 15  # Many nodes but few connections suggest poor structure
        
        return max(0, min(100, score))
    
    def _calculate_reliability_score(self, workflow: WorkflowDefinition, 
                                   metrics: WorkflowMetrics) -> float:
        """Calculate reliability score (0-100)"""
        score = 100.0
        
        # Success rate impact
        score = metrics.success_rate
        
        # Penalize single points of failure
        critical_nodes = [n for n in workflow.nodes if n.type in [
            NodeType.PLC_READ, NodeType.PLC_WRITE, NodeType.DATABASE_WRITE
        ]]
        if len(critical_nodes) > len(workflow.nodes) * 0.8:
            score -= 20  # Too many critical operations
        
        # Check for error handling
        error_handling_nodes = [n for n in workflow.nodes if 'error' in n.name.lower() or 
                               'retry' in n.name.lower() or n.type == NodeType.CONDITION]
        if len(error_handling_nodes) == 0 and len(workflow.nodes) > 3:
            score -= 25  # No error handling in complex workflow
        
        # Check for monitoring and alerting
        monitoring_nodes = [n for n in workflow.nodes if n.type in [
            NodeType.EMAIL, NodeType.SMS, NodeType.WEBHOOK
        ]]
        if len(monitoring_nodes) == 0 and workflow.workflow_type != WorkflowType.MONITORING:
            score -= 15  # No alerting capability
        
        return max(0, min(100, score))
    
    def _calculate_maintainability_score(self, workflow: WorkflowDefinition) -> float:
        """Calculate maintainability score (0-100)"""
        score = 100.0
        
        # Check node naming
        well_named_nodes = [n for n in workflow.nodes if len(n.name.split()) >= 2]
        if len(well_named_nodes) < len(workflow.nodes) * 0.8:
            score -= 20  # Poor naming
        
        # Check for documentation
        documented_nodes = [n for n in workflow.nodes if n.notes and len(n.notes) > 10]
        if len(documented_nodes) < len(workflow.nodes) * 0.3:
            score -= 25  # Poor documentation
        
        # Check workflow organization
        if len(workflow.nodes) > 15:
            score -= 15  # Very complex workflow
        elif len(workflow.nodes) > 10:
            score -= 5   # Moderately complex
        
        # Check for tags and categorization
        if len(workflow.tags) < 2:
            score -= 10  # Poor categorization
        
        # Check for consistent positioning (nodes not overlapping)
        positions = [n.position for n in workflow.nodes]
        unique_positions = set(positions)
        if len(unique_positions) < len(positions):
            score -= 15  # Overlapping nodes
        
        return max(0, min(100, score))
    
    def _identify_bottlenecks(self, workflow: WorkflowDefinition, 
                            metrics: WorkflowMetrics) -> List[str]:
        """Identify performance bottlenecks in the workflow"""
        bottlenecks = []
        
        # Check for sequential PLC operations
        plc_nodes = [n for n in workflow.nodes if 'plc' in n.type.value.lower()]
        if len(plc_nodes) > 3:
            bottlenecks.append(f"Multiple PLC operations ({len(plc_nodes)}) may cause sequential delays")
        
        # Check for polling-based operations
        timer_nodes = [n for n in workflow.nodes if n.type == NodeType.TIMER]
        fast_timers = [n for n in timer_nodes if 
                      n.parameters.get('interval', 1000) < 1000]  # Less than 1 second
        if fast_timers:
            bottlenecks.append(f"High-frequency polling detected ({len(fast_timers)} nodes)")
        
        # Check for database operations
        db_nodes = [n for n in workflow.nodes if 'database' in n.type.value.lower()]
        if len(db_nodes) > 2:
            bottlenecks.append(f"Multiple database operations ({len(db_nodes)}) may impact performance")
        
        # Check for external API calls
        api_nodes = [n for n in workflow.nodes if n.type in [NodeType.API_CALL, NodeType.EMAIL]]
        if len(api_nodes) > 1:
            bottlenecks.append(f"Multiple external API calls ({len(api_nodes)}) may cause latency")
        
        # Check for long execution chains
        if len(workflow.connections) > len(workflow.nodes) * 1.5:
            bottlenecks.append("Complex connection patterns may cause execution delays")
        
        return bottlenecks
    
    def _identify_risk_factors(self, workflow: WorkflowDefinition) -> List[str]:
        """Identify risk factors in the workflow"""
        risks = []
        
        # Check for missing error handling
        error_handlers = [n for n in workflow.nodes if 
                         'error' in n.name.lower() or n.type == NodeType.CONDITION]
        if not error_handlers and len(workflow.nodes) > 3:
            risks.append("No error handling mechanisms detected")
        
        # Check for safety-critical operations without monitoring
        safety_critical = [n for n in workflow.nodes if n.type in [
            NodeType.PLC_WRITE, NodeType.VALVE_CONTROL, NodeType.MOTOR_CONTROL
        ]]
        monitoring = [n for n in workflow.nodes if n.type in [
            NodeType.EMAIL, NodeType.SMS, NodeType.CONDITION
        ]]
        if safety_critical and not monitoring:
            risks.append("Safety-critical operations without monitoring")
        
        # Check for single points of failure
        if len(workflow.connections) < len(workflow.nodes) - 1:
            risks.append("Potential single points of failure detected")
        
        # Check for credentials exposure
        nodes_with_creds = [n for n in workflow.nodes if n.credentials]
        if len(nodes_with_creds) > len(workflow.nodes) * 0.5:
            risks.append("High number of nodes with credentials may increase security risk")
        
        return risks
    
    def _check_compliance(self, workflow: WorkflowDefinition) -> List[str]:
        """Check for compliance issues"""
        issues = []
        
        # Check for audit logging
        logging_nodes = [n for n in workflow.nodes if 
                        'log' in n.name.lower() or n.type == NodeType.DATABASE_WRITE]
        if not logging_nodes and workflow.workflow_type in [
            WorkflowType.SAFETY_INTERLOCK, WorkflowType.BATCH_PROCESSING
        ]:
            issues.append("Audit logging required for safety-critical workflows")
        
        # Check for approval workflows
        if workflow.workflow_type == WorkflowType.SAFETY_INTERLOCK:
            approval_nodes = [n for n in workflow.nodes if 
                            'approval' in n.name.lower() or 'confirm' in n.name.lower()]
            if not approval_nodes:
                issues.append("Safety interlocks require approval mechanisms")
        
        # Check for data retention
        if workflow.workflow_type == WorkflowType.DATA_COLLECTION:
            retention_info = any('retention' in str(n.parameters) for n in workflow.nodes)
            if not retention_info:
                issues.append("Data collection workflows should specify retention policies")
        
        return issues
    
    def _generate_recommendations(self, workflow: WorkflowDefinition, 
                                metrics: WorkflowMetrics,
                                performance_score: float,
                                reliability_score: float,
                                maintainability_score: float) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Performance recommendations
        if performance_score < 70:
            if metrics.execution_time_avg > 5.0:
                recommendations.append(OptimizationRecommendation(
                    id="perf_001",
                    optimization_type=OptimizationType.PERFORMANCE,
                    priority=OptimizationPriority.HIGH,
                    title="Reduce Execution Time",
                    description="Workflow execution time is high. Consider parallel execution and caching.",
                    expected_improvement="30-50% reduction in execution time",
                    implementation_effort="Medium",
                    estimated_impact_score=75.0,
                    implementation_steps=[
                        "Identify sequential operations that can be parallelized",
                        "Implement caching for frequently accessed data",
                        "Optimize database queries",
                        "Use batch operations where possible"
                    ],
                    risk_assessment="Low risk - performance optimizations typically safe"
                ))
            
            # PLC optimization
            plc_nodes = [n for n in workflow.nodes if 'plc' in n.type.value.lower()]
            if len(plc_nodes) > 3:
                recommendations.append(OptimizationRecommendation(
                    id="perf_002",
                    optimization_type=OptimizationType.PERFORMANCE,
                    priority=OptimizationPriority.MEDIUM,
                    title="Optimize PLC Communications",
                    description="Multiple PLC operations detected. Consider batching reads/writes.",
                    expected_improvement="20-40% reduction in PLC communication overhead",
                    implementation_effort="Medium",
                    estimated_impact_score=60.0,
                    implementation_steps=[
                        "Group PLC read operations into batch requests",
                        "Implement PLC tag change monitoring",
                        "Use OPC-UA subscriptions instead of polling where possible",
                        "Cache PLC values with appropriate refresh intervals"
                    ]
                ))
        
        # Reliability recommendations
        if reliability_score < 80:
            recommendations.append(OptimizationRecommendation(
                id="rel_001",
                optimization_type=OptimizationType.RELIABILITY,
                priority=OptimizationPriority.HIGH,
                title="Add Error Handling",
                description="Workflow lacks comprehensive error handling mechanisms.",
                expected_improvement="Reduce error-related downtime by 80%",
                implementation_effort="Medium",
                estimated_impact_score=85.0,
                implementation_steps=[
                    "Add try-catch error handling around critical operations",
                    "Implement retry logic with exponential backoff",
                    "Add failure notification alerts",
                    "Create fallback procedures for critical failures"
                ],
                risk_assessment="Low risk - improves system stability"
            ))
            
            # Monitoring recommendation
            monitoring_nodes = [n for n in workflow.nodes if n.type in [
                NodeType.EMAIL, NodeType.SMS, NodeType.WEBHOOK
            ]]
            if not monitoring_nodes:
                recommendations.append(OptimizationRecommendation(
                    id="rel_002",
                    optimization_type=OptimizationType.RELIABILITY,
                    priority=OptimizationPriority.MEDIUM,
                    title="Add Monitoring and Alerting",
                    description="No monitoring or alerting mechanisms detected.",
                    expected_improvement="Faster incident detection and response",
                    implementation_effort="Low",
                    estimated_impact_score=70.0,
                    implementation_steps=[
                        "Add email notifications for critical failures",
                        "Implement health check monitoring",
                        "Create dashboard for workflow status",
                        "Set up automated escalation procedures"
                    ]
                ))
        
        # Maintainability recommendations
        if maintainability_score < 75:
            documented_nodes = [n for n in workflow.nodes if n.notes]
            if len(documented_nodes) < len(workflow.nodes) * 0.5:
                recommendations.append(OptimizationRecommendation(
                    id="maint_001",
                    optimization_type=OptimizationType.MAINTAINABILITY,
                    priority=OptimizationPriority.MEDIUM,
                    title="Improve Documentation",
                    description="Many nodes lack proper documentation.",
                    expected_improvement="Easier maintenance and troubleshooting",
                    implementation_effort="Low",
                    estimated_impact_score=60.0,
                    implementation_steps=[
                        "Add descriptive notes to all nodes",
                        "Document node parameters and their purposes",
                        "Create workflow overview documentation",
                        "Add troubleshooting guides"
                    ]
                ))
            
            if len(workflow.nodes) > 12:
                recommendations.append(OptimizationRecommendation(
                    id="maint_002",
                    optimization_type=OptimizationType.MAINTAINABILITY,
                    priority=OptimizationPriority.LOW,
                    title="Consider Workflow Decomposition",
                    description="Large workflow may benefit from being split into smaller components.",
                    expected_improvement="Easier testing, debugging, and maintenance",
                    implementation_effort="High",
                    estimated_impact_score=50.0,
                    implementation_steps=[
                        "Identify logical workflow boundaries",
                        "Create sub-workflows for distinct functions",
                        "Implement workflow orchestration",
                        "Add inter-workflow communication mechanisms"
                    ]
                ))
        
        # Safety recommendations
        safety_critical = [n for n in workflow.nodes if n.type in [
            NodeType.PLC_WRITE, NodeType.VALVE_CONTROL, NodeType.MOTOR_CONTROL
        ]]
        if safety_critical:
            recommendations.append(OptimizationRecommendation(
                id="safety_001",
                optimization_type=OptimizationType.SAFETY,
                priority=OptimizationPriority.CRITICAL,
                title="Implement Safety Interlocks",
                description="Safety-critical operations require additional safeguards.",
                expected_improvement="Prevent unsafe operations and improve compliance",
                implementation_effort="High",
                estimated_impact_score=95.0,
                implementation_steps=[
                    "Add safety condition checks before critical operations",
                    "Implement operator approval for dangerous operations",
                    "Add emergency stop capabilities",
                    "Create safety audit logging",
                    "Implement limit checking and validation"
                ],
                risk_assessment="Critical for safety compliance"
            ))
        
        # Cost optimization
        expensive_nodes = [n for n in workflow.nodes if n.type in [
            NodeType.EMAIL, NodeType.SMS, NodeType.API_CALL
        ]]
        if len(expensive_nodes) > 2:
            recommendations.append(OptimizationRecommendation(
                id="cost_001",
                optimization_type=OptimizationType.COST,
                priority=OptimizationPriority.LOW,
                title="Optimize External Service Usage",
                description="Multiple external service calls may increase operational costs.",
                expected_improvement="10-30% reduction in operational costs",
                implementation_effort="Medium",
                estimated_impact_score=40.0,
                implementation_steps=[
                    "Consolidate multiple notifications into batches",
                    "Implement notification throttling",
                    "Use webhooks instead of polling where possible",
                    "Cache external API responses"
                ]
            ))
        
        return recommendations

class AIWorkflowOptimizer:
    """Main AI-powered workflow optimizer"""
    
    def __init__(self):
        self.performance_analyzer = WorkflowPerformanceAnalyzer()
        self.optimization_history = {}
        
    def optimize_workflow(self, workflow: WorkflowDefinition,
                         metrics: Optional[WorkflowMetrics] = None,
                         optimization_goals: List[OptimizationType] = None) -> OptimizedWorkflow:
        """Optimize workflow based on analysis and goals"""
        
        # Analyze current workflow
        analysis = self.performance_analyzer.analyze_workflow_performance(workflow, metrics)
        
        # Filter recommendations by goals if specified
        if optimization_goals:
            filtered_recommendations = [
                rec for rec in analysis.recommendations 
                if rec.optimization_type in optimization_goals
            ]
        else:
            # Apply high and critical priority recommendations by default
            filtered_recommendations = [
                rec for rec in analysis.recommendations 
                if rec.priority in [OptimizationPriority.CRITICAL, OptimizationPriority.HIGH]
            ]
        
        # Apply optimizations
        optimized_workflow = self._apply_optimizations(workflow, filtered_recommendations)
        
        # Calculate expected improvements
        expected_improvements = self._calculate_expected_improvements(
            analysis.current_metrics, filtered_recommendations
        )
        
        # Validate optimized workflow
        validation_results = self._validate_optimized_workflow(
            workflow, optimized_workflow, filtered_recommendations
        )
        
        return OptimizedWorkflow(
            original_workflow=workflow,
            optimized_workflow=optimized_workflow,
            applied_optimizations=filtered_recommendations,
            expected_improvements=expected_improvements,
            validation_results=validation_results
        )
    
    def _apply_optimizations(self, workflow: WorkflowDefinition,
                           recommendations: List[OptimizationRecommendation]) -> WorkflowDefinition:
        """Apply optimization recommendations to create improved workflow"""
        
        # Create a copy of the workflow
        optimized = WorkflowDefinition(
            id=workflow.id + "_optimized",
            name=workflow.name + " (Optimized)",
            workflow_type=workflow.workflow_type,
            description=workflow.description + " - AI Optimized",
            nodes=workflow.nodes.copy(),
            connections=workflow.connections.copy(),
            settings=workflow.settings.copy(),
            tags=workflow.tags + ["ai-optimized"],
            metadata=workflow.metadata.copy()
        )
        
        for rec in recommendations:
            if rec.optimization_type == OptimizationType.PERFORMANCE:
                self._apply_performance_optimizations(optimized, rec)
            elif rec.optimization_type == OptimizationType.RELIABILITY:
                self._apply_reliability_optimizations(optimized, rec)
            elif rec.optimization_type == OptimizationType.MAINTAINABILITY:
                self._apply_maintainability_optimizations(optimized, rec)
            elif rec.optimization_type == OptimizationType.SAFETY:
                self._apply_safety_optimizations(optimized, rec)
            elif rec.optimization_type == OptimizationType.COST:
                self._apply_cost_optimizations(optimized, rec)
        
        return optimized
    
    def _apply_performance_optimizations(self, workflow: WorkflowDefinition,
                                       recommendation: OptimizationRecommendation):
        """Apply performance optimization to workflow"""
        
        if "PLC" in recommendation.title:
            # Optimize PLC operations by adding caching
            plc_nodes = [n for n in workflow.nodes if 'plc' in n.type.value.lower()]
            for node in plc_nodes:
                if 'polling_rate' in node.parameters:
                    # Reduce polling frequency
                    current_rate = node.parameters.get('polling_rate', 1000)
                    node.parameters['polling_rate'] = max(1000, current_rate * 2)
                
                # Add caching
                node.parameters['enable_caching'] = True
                node.parameters['cache_duration'] = 5000  # 5 seconds
        
        elif "Execution Time" in recommendation.title:
            # Add parallel execution hints
            workflow.settings['execution_mode'] = 'parallel_optimized'
            workflow.settings['max_parallel_nodes'] = 5
    
    def _apply_reliability_optimizations(self, workflow: WorkflowDefinition,
                                       recommendation: OptimizationRecommendation):
        """Apply reliability optimization to workflow"""
        
        if "Error Handling" in recommendation.title:
            # Add error handling to critical nodes
            critical_nodes = [n for n in workflow.nodes if n.type in [
                NodeType.PLC_READ, NodeType.PLC_WRITE, NodeType.DATABASE_WRITE
            ]]
            
            for node in critical_nodes:
                node.parameters['retry_count'] = 3
                node.parameters['retry_delay'] = 1000
                node.parameters['error_handling'] = 'continue_on_fail'
        
        elif "Monitoring" in recommendation.title:
            # Add monitoring node
            monitor_node = WorkflowNode(
                id=f"monitor_{len(workflow.nodes)}",
                name="Workflow Health Monitor",
                type=NodeType.WEBHOOK,
                position=(600, 50),
                parameters={
                    'url': 'http://monitoring.internal/webhook',
                    'method': 'POST',
                    'payload': {'workflow_id': workflow.id, 'status': '{{$json.status}}'}
                }
            )
            workflow.nodes.append(monitor_node)
    
    def _apply_maintainability_optimizations(self, workflow: WorkflowDefinition,
                                           recommendation: OptimizationRecommendation):
        """Apply maintainability optimization to workflow"""
        
        if "Documentation" in recommendation.title:
            # Add documentation to nodes
            for node in workflow.nodes:
                if not node.notes:
                    node.notes = f"Auto-generated documentation for {node.name} ({node.type.value})"
        
        # Add workflow metadata
        workflow.metadata.update({
            'optimization_applied': True,
            'optimization_date': datetime.now(timezone.utc).isoformat(),
            'optimization_version': '1.0'
        })
    
    def _apply_safety_optimizations(self, workflow: WorkflowDefinition,
                                  recommendation: OptimizationRecommendation):
        """Apply safety optimization to workflow"""
        
        if "Safety Interlocks" in recommendation.title:
            # Add safety checks before critical operations
            safety_critical = [n for n in workflow.nodes if n.type in [
                NodeType.PLC_WRITE, NodeType.VALVE_CONTROL, NodeType.MOTOR_CONTROL
            ]]
            
            for node in safety_critical:
                # Add safety validation
                node.parameters['safety_check_required'] = True
                node.parameters['operator_approval'] = True
                node.parameters['safety_limits'] = {
                    'min_value': 0,
                    'max_value': 100,
                    'emergency_stop': True
                }
    
    def _apply_cost_optimizations(self, workflow: WorkflowDefinition,
                                recommendation: OptimizationRecommendation):
        """Apply cost optimization to workflow"""
        
        if "External Service" in recommendation.title:
            # Optimize external service usage
            external_nodes = [n for n in workflow.nodes if n.type in [
                NodeType.EMAIL, NodeType.SMS, NodeType.API_CALL
            ]]
            
            for node in external_nodes:
                # Add throttling
                node.parameters['rate_limit'] = 60  # Max 60 calls per minute
                node.parameters['batch_notifications'] = True
                node.parameters['priority_filtering'] = True
    
    def _calculate_expected_improvements(self, current_metrics: WorkflowMetrics,
                                       recommendations: List[OptimizationRecommendation]) -> Dict[str, float]:
        """Calculate expected performance improvements"""
        improvements = {
            'execution_time_reduction': 0.0,
            'error_rate_reduction': 0.0,
            'cost_reduction': 0.0,
            'reliability_improvement': 0.0
        }
        
        for rec in recommendations:
            if rec.optimization_type == OptimizationType.PERFORMANCE:
                improvements['execution_time_reduction'] += rec.estimated_impact_score * 0.01 * 0.3
            elif rec.optimization_type == OptimizationType.RELIABILITY:
                improvements['error_rate_reduction'] += rec.estimated_impact_score * 0.01 * 0.5
                improvements['reliability_improvement'] += rec.estimated_impact_score * 0.01 * 0.8
            elif rec.optimization_type == OptimizationType.COST:
                improvements['cost_reduction'] += rec.estimated_impact_score * 0.01 * 0.2
        
        # Cap improvements at reasonable levels
        for key in improvements:
            improvements[key] = min(improvements[key], 0.7)  # Max 70% improvement
        
        return improvements
    
    def _validate_optimized_workflow(self, original: WorkflowDefinition,
                                   optimized: WorkflowDefinition,
                                   recommendations: List[OptimizationRecommendation]) -> Dict[str, Any]:
        """Validate that optimizations don't break workflow functionality"""
        
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations_applied': len(recommendations),
            'nodes_modified': 0,
            'new_nodes_added': 0
        }
        
        # Check if core functionality is preserved
        original_critical_nodes = [n for n in original.nodes if n.type in [
            NodeType.PLC_READ, NodeType.PLC_WRITE, NodeType.PID_CONTROLLER
        ]]
        optimized_critical_nodes = [n for n in optimized.nodes if n.type in [
            NodeType.PLC_READ, NodeType.PLC_WRITE, NodeType.PID_CONTROLLER
        ]]
        
        if len(optimized_critical_nodes) < len(original_critical_nodes):
            validation['errors'].append("Critical nodes removed during optimization")
            validation['valid'] = False
        
        # Count modifications
        validation['nodes_modified'] = sum(1 for orig, opt in zip(original.nodes, optimized.nodes)
                                         if orig.parameters != opt.parameters)
        validation['new_nodes_added'] = len(optimized.nodes) - len(original.nodes)
        
        # Check for potential issues
        if validation['new_nodes_added'] > 3:
            validation['warnings'].append("Many new nodes added - may increase complexity")
        
        return validation
    
    def generate_optimization_report(self, analysis: WorkflowAnalysisResult,
                                   optimized: OptimizedWorkflow) -> str:
        """Generate comprehensive optimization report"""
        
        report = f"""
# Workflow Optimization Report

## Workflow: {optimized.original_workflow.name}
**Analysis Date**: {analysis.analysis_timestamp.isoformat()}
**Optimization Date**: {optimized.optimization_timestamp.isoformat()}

## Current Performance Scores
- **Overall Health**: {analysis.overall_health_score:.1f}/100
- **Performance**: {analysis.performance_score:.1f}/100  
- **Reliability**: {analysis.reliability_score:.1f}/100
- **Maintainability**: {analysis.maintainability_score:.1f}/100

## Key Metrics
- **Execution Time**: {analysis.current_metrics.execution_time_avg:.2f}s (avg)
- **Throughput**: {analysis.current_metrics.throughput_per_hour:.0f} executions/hour
- **Error Rate**: {analysis.current_metrics.error_rate:.1f}%
- **Success Rate**: {analysis.current_metrics.success_rate:.1f}%

## Optimizations Applied ({len(optimized.applied_optimizations)})
"""
        
        for i, rec in enumerate(optimized.applied_optimizations, 1):
            report += f"""
### {i}. {rec.title}
- **Type**: {rec.optimization_type.value.title()}
- **Priority**: {rec.priority.value.title()}
- **Expected Impact**: {rec.expected_improvement}
- **Implementation Effort**: {rec.implementation_effort}
- **Impact Score**: {rec.estimated_impact_score:.1f}/100
"""
        
        report += f"""
## Expected Improvements
- **Execution Time Reduction**: {optimized.expected_improvements.get('execution_time_reduction', 0)*100:.1f}%
- **Error Rate Reduction**: {optimized.expected_improvements.get('error_rate_reduction', 0)*100:.1f}%
- **Cost Reduction**: {optimized.expected_improvements.get('cost_reduction', 0)*100:.1f}%
- **Reliability Improvement**: {optimized.expected_improvements.get('reliability_improvement', 0)*100:.1f}%

## Implementation Status
- **Recommendations Applied**: {optimized.validation_results['recommendations_applied']}
- **Nodes Modified**: {optimized.validation_results['nodes_modified']}
- **New Nodes Added**: {optimized.validation_results['new_nodes_added']}
- **Validation Status**: {"✅ PASSED" if optimized.validation_results['valid'] else "❌ FAILED"}

## Next Steps
1. Deploy optimized workflow to staging environment
2. Monitor performance improvements
3. Apply remaining low-priority optimizations if needed
4. Schedule regular optimization reviews

---
*Report generated by PLC-GBT AI Workflow Optimizer*
"""
        
        return report

# Testing and example usage
def test_workflow_optimizer():
    """Test the AI workflow optimizer"""
    from nl_workflow_parser import NaturalLanguageWorkflowParser
    
    # Create a test workflow
    parser = NaturalLanguageWorkflowParser()
    result = parser.parse_workflow_request(
        "Create a temperature control loop for the reactor with PID controller and email alerts"
    )
    
    if result.parsing_success and result.workflow_definition:
        optimizer = AIWorkflowOptimizer()
        
        # Generate sample metrics
        metrics = WorkflowMetrics(
            execution_time_avg=8.5,
            error_rate=5.0,
            success_rate=95.0,
            resource_usage_cpu=25.0,
            throughput_per_hour=400
        )
        
        # Analyze workflow
        analysis = optimizer.performance_analyzer.analyze_workflow_performance(
            result.workflow_definition, metrics
        )
        
        print(f"Analysis completed:")
        print(f"- Overall Health Score: {analysis.overall_health_score:.1f}/100")
        print(f"- Recommendations: {len(analysis.recommendations)}")
        print(f"- Bottlenecks: {len(analysis.bottlenecks)}")
        
        # Optimize workflow
        optimized = optimizer.optimize_workflow(
            result.workflow_definition, metrics,
            [OptimizationType.PERFORMANCE, OptimizationType.RELIABILITY]
        )
        
        print(f"\nOptimization completed:")
        print(f"- Optimizations Applied: {len(optimized.applied_optimizations)}")
        print(f"- Nodes Modified: {optimized.validation_results['nodes_modified']}")
        print(f"- Expected Execution Time Reduction: {optimized.expected_improvements.get('execution_time_reduction', 0)*100:.1f}%")
        
        # Generate report
        report = optimizer.generate_optimization_report(analysis, optimized)
        print(f"\nGenerated optimization report ({len(report)} characters)")
        
        return True
    else:
        print("Failed to create test workflow")
        return False

if __name__ == "__main__":
    test_workflow_optimizer() 