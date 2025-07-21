"""
Natural Language Workflow Parser
Phase 26.4.1: Natural Language to N8N Workflow Translation

Converts natural language descriptions into executable N8N workflow definitions,
leveraging Phase 23 intent recognition infrastructure for industrial automation workflows.
"""

import re
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
import time

# Import Phase 23 LLM components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../llm'))

from intent_recognition import (
    EntityExtractor, IntentClassifier, AmbiguityResolver,
    IntentRecognitionEngine, IntentRecognitionResult, EntityType, IntentType
)
from domain_understanding import ConceptRecognizer, IndustryTerminologyManager
from context_provider import ContextProvider

logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Types of N8N workflows for industrial automation"""
    DATA_COLLECTION = "data_collection"
    PID_CONTROL = "pid_control"
    ALARM_MANAGEMENT = "alarm_management"
    MAINTENANCE_SCHEDULING = "maintenance_scheduling"
    BATCH_PROCESSING = "batch_processing"
    REPORTING = "reporting"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    SAFETY_INTERLOCK = "safety_interlock"
    OPTIMIZATION = "optimization"

class NodeType(Enum):
    """N8N node types for industrial workflows"""
    # Data nodes
    PLC_READ = "plc_read"
    PLC_WRITE = "plc_write"
    DATABASE_QUERY = "database_query"
    DATABASE_WRITE = "database_write"
    
    # Control nodes
    PID_CONTROLLER = "pid_controller"
    SETPOINT_ADJUSTMENT = "setpoint_adjustment"
    VALVE_CONTROL = "valve_control"
    MOTOR_CONTROL = "motor_control"
    
    # Logic nodes
    CONDITION = "condition"
    TIMER = "timer"
    COUNTER = "counter"
    CALCULATOR = "calculator"
    
    # Communication nodes
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    API_CALL = "api_call"
    
    # Industrial protocol nodes
    MODBUS = "modbus"
    OPC_UA = "opc_ua"
    ETHERNET_IP = "ethernet_ip"
    
    # Analysis nodes
    TREND_ANALYSIS = "trend_analysis"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    ALARM_ANALYSIS = "alarm_analysis"

@dataclass
class WorkflowNode:
    """Individual N8N workflow node definition"""
    id: str
    name: str
    type: NodeType
    position: Tuple[int, int] = (0, 0)
    parameters: Dict[str, Any] = field(default_factory=dict)
    credentials: Optional[str] = None
    notes: str = ""
    disabled: bool = False
    
@dataclass
class WorkflowConnection:
    """Connection between workflow nodes"""
    source_node: str
    source_output: int = 0
    target_node: str
    target_input: int = 0

@dataclass
class WorkflowDefinition:
    """Complete N8N workflow definition"""
    id: str
    name: str
    workflow_type: WorkflowType
    description: str
    nodes: List[WorkflowNode] = field(default_factory=list)
    connections: List[WorkflowConnection] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowTemplate:
    """Template for common workflow patterns"""
    name: str
    workflow_type: WorkflowType
    description: str
    required_parameters: List[str]
    optional_parameters: List[str] = field(default_factory=list)
    node_templates: List[Dict[str, Any]] = field(default_factory=list)
    example_usage: str = ""

@dataclass
class WorkflowParsingResult:
    """Result of natural language workflow parsing"""
    workflow_definition: Optional[WorkflowDefinition] = None
    confidence: float = 0.0
    parsing_success: bool = False
    error_message: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    clarification_needed: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class IndustrialWorkflowTemplates:
    """Industrial automation workflow templates"""
    
    @staticmethod
    def get_templates() -> Dict[str, WorkflowTemplate]:
        """Get all available workflow templates"""
        return {
            "temperature_control": WorkflowTemplate(
                name="Temperature Control Loop",
                workflow_type=WorkflowType.PID_CONTROL,
                description="Basic temperature control with PID controller",
                required_parameters=["temperature_sensor", "control_valve", "setpoint"],
                optional_parameters=["alarm_limits", "tuning_parameters"],
                node_templates=[
                    {"type": "plc_read", "purpose": "Read temperature sensor"},
                    {"type": "pid_controller", "purpose": "Calculate control output"},
                    {"type": "plc_write", "purpose": "Write to control valve"},
                    {"type": "condition", "purpose": "Check alarm conditions"}
                ],
                example_usage="Create temperature control for reactor tank with PID tuning"
            ),
            
            "data_logging": WorkflowTemplate(
                name="Data Collection and Logging",
                workflow_type=WorkflowType.DATA_COLLECTION,
                description="Collect data from multiple sources and log to database",
                required_parameters=["data_sources", "database_connection"],
                optional_parameters=["sampling_rate", "data_filtering"],
                node_templates=[
                    {"type": "plc_read", "purpose": "Read process data"},
                    {"type": "database_write", "purpose": "Store data"},
                    {"type": "timer", "purpose": "Control sampling rate"}
                ],
                example_usage="Log pressure, temperature, and flow data every 30 seconds"
            ),
            
            "alarm_monitoring": WorkflowTemplate(
                name="Alarm Monitoring and Notification",
                workflow_type=WorkflowType.ALARM_MANAGEMENT,
                description="Monitor process variables and send alerts",
                required_parameters=["monitored_variables", "alarm_limits"],
                optional_parameters=["notification_methods", "escalation_rules"],
                node_templates=[
                    {"type": "plc_read", "purpose": "Read process variables"},
                    {"type": "condition", "purpose": "Check alarm conditions"},
                    {"type": "email", "purpose": "Send alarm notifications"},
                    {"type": "database_write", "purpose": "Log alarm events"}
                ],
                example_usage="Monitor tank level and send email when high/low limits reached"
            ),
            
            "batch_recipe": WorkflowTemplate(
                name="Batch Processing Recipe",
                workflow_type=WorkflowType.BATCH_PROCESSING,
                description="Execute sequential batch recipe steps",
                required_parameters=["recipe_steps", "process_equipment"],
                optional_parameters=["step_timing", "quality_checks"],
                node_templates=[
                    {"type": "timer", "purpose": "Control step timing"},
                    {"type": "plc_write", "purpose": "Control equipment"},
                    {"type": "condition", "purpose": "Check step completion"},
                    {"type": "database_write", "purpose": "Log batch progress"}
                ],
                example_usage="Execute 5-step batch recipe for chemical processing"
            )
        }

class WorkflowEntityExtractor:
    """Extract workflow-specific entities from natural language"""
    
    def __init__(self):
        self.entity_patterns = {
            EntityType.LOOP_NAME: [
                r'\b(temperature|pressure|flow|level|pH|conductivity)\s+(?:control|loop)\b',
                r'\b(reactor|tank|vessel|column|exchanger)\s+(?:\w+\s+)?(?:control|loop)\b'
            ],
            EntityType.PARAMETER: [
                r'\b(setpoint|PV|CV|output)\b',
                r'\b(Kp|Ki|Kd|proportional|integral|derivative)\b',
                r'\b(high|low|alarm|limit)\b'
            ],
            EntityType.VALUE: [
                r'\b(\d+(?:\.\d+)?)\s*(?:°C|°F|psi|bar|gpm|lpm|%)\b',
                r'\b(\d+(?:\.\d+)?)\s*(?:seconds?|minutes?|hours?)\b'
            ],
            EntityType.CONTROLLER_TYPE: [
                r'\b(PID|PI|PD|cascade|feedforward|MPC)\b',
                r'\b(single|dual|triple)\s+loop\b'
            ],
            EntityType.OPERATION_TARGET: [
                r'\b(valve|pump|motor|heater|cooler|damper)\b',
                r'\b(inlet|outlet|supply|return|bypass)\s+(?:valve|pump)\b'
            ]
        }
    
    def extract_entities(self, text: str, context: Dict[str, Any] = None) -> Dict[EntityType, List[str]]:
        """Extract workflow-specific entities from text"""
        entities = {}
        text_lower = text.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities

class WorkflowIntentClassifier:
    """Classify workflow creation intents"""
    
    def __init__(self):
        self.intent_patterns = {
            WorkflowType.PID_CONTROL: [
                r'\b(?:create|build|make)\s+.*(?:PID|control|controller)\b',
                r'\b(?:temperature|pressure|flow|level)\s+control\b',
                r'\b(?:tune|tuning|adjust)\s+.*(?:PID|controller)\b'
            ],
            WorkflowType.DATA_COLLECTION: [
                r'\b(?:collect|log|record|store)\s+.*data\b',
                r'\b(?:data\s+logging|historian|trending)\b',
                r'\b(?:sample|monitor)\s+.*(?:every|interval)\b'
            ],
            WorkflowType.ALARM_MANAGEMENT: [
                r'\b(?:alarm|alert|notification|warning)\b',
                r'\b(?:monitor|watch|check)\s+.*(?:limit|threshold)\b',
                r'\b(?:send|notify|email)\s+.*(?:alarm|alert)\b'
            ],
            WorkflowType.BATCH_PROCESSING: [
                r'\b(?:batch|recipe|sequence|procedure)\b',
                r'\b(?:step|phase|stage)\s+.*(?:process|operation)\b',
                r'\b(?:execute|run|start)\s+.*(?:batch|recipe)\b'
            ]
        }
    
    def classify_intent(self, text: str) -> Tuple[WorkflowType, float]:
        """Classify the workflow intent with confidence score"""
        text_lower = text.lower()
        best_match = WorkflowType.MONITORING  # Default
        best_score = 0.0
        
        for workflow_type, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1.0
            
            # Normalize by number of patterns
            score = score / len(patterns)
            
            if score > best_score:
                best_score = score
                best_match = workflow_type
        
        return best_match, best_score

class WorkflowNodeGenerator:
    """Generate N8N nodes based on workflow requirements"""
    
    def __init__(self):
        self.node_counter = 0
    
    def generate_node_id(self) -> str:
        """Generate unique node ID"""
        self.node_counter += 1
        return f"node_{self.node_counter}_{uuid.uuid4().hex[:8]}"
    
    def create_plc_read_node(self, tag_name: str, connection: str = "default") -> WorkflowNode:
        """Create PLC read node"""
        return WorkflowNode(
            id=self.generate_node_id(),
            name=f"Read {tag_name}",
            type=NodeType.PLC_READ,
            parameters={
                "tag_name": tag_name,
                "connection": connection,
                "data_type": "real",
                "polling_rate": 1000
            }
        )
    
    def create_plc_write_node(self, tag_name: str, value_source: str = "previous_node") -> WorkflowNode:
        """Create PLC write node"""
        return WorkflowNode(
            id=self.generate_node_id(),
            name=f"Write {tag_name}",
            type=NodeType.PLC_WRITE,
            parameters={
                "tag_name": tag_name,
                "value_source": value_source,
                "data_type": "real"
            }
        )
    
    def create_pid_controller_node(self, process_variable: str, setpoint: str) -> WorkflowNode:
        """Create PID controller node"""
        return WorkflowNode(
            id=self.generate_node_id(),
            name="PID Controller",
            type=NodeType.PID_CONTROLLER,
            parameters={
                "process_variable": process_variable,
                "setpoint": setpoint,
                "kp": 1.0,
                "ki": 0.1,
                "kd": 0.0,
                "output_min": 0.0,
                "output_max": 100.0,
                "direction": "direct"
            }
        )
    
    def create_condition_node(self, condition: str, variable: str, threshold: float) -> WorkflowNode:
        """Create condition/alarm check node"""
        return WorkflowNode(
            id=self.generate_node_id(),
            name=f"Check {condition}",
            type=NodeType.CONDITION,
            parameters={
                "variable": variable,
                "operator": "greater_than",  # or less_than, equal, etc.
                "threshold": threshold,
                "condition_name": condition
            }
        )
    
    def create_email_node(self, recipients: List[str], subject: str) -> WorkflowNode:
        """Create email notification node"""
        return WorkflowNode(
            id=self.generate_node_id(),
            name="Send Email Alert",
            type=NodeType.EMAIL,
            parameters={
                "recipients": recipients,
                "subject": subject,
                "body_template": "Alert: {{$json.alarm_message}}",
                "smtp_config": "default"
            }
        )

class NaturalLanguageWorkflowParser:
    """Main class for parsing natural language into N8N workflows"""
    
    def __init__(self):
        self.intent_recognition_engine = IntentRecognitionEngine()
        self.workflow_entity_extractor = WorkflowEntityExtractor()
        self.workflow_intent_classifier = WorkflowIntentClassifier()
        self.node_generator = WorkflowNodeGenerator()
        self.concept_recognizer = ConceptRecognizer()
        self.terminology_manager = IndustryTerminologyManager()
        self.templates = IndustrialWorkflowTemplates.get_templates()
        
    def parse_workflow_request(self, natural_language_text: str, 
                              context: Optional[Dict[str, Any]] = None) -> WorkflowParsingResult:
        """Parse natural language text into N8N workflow definition"""
        start_time = time.time()
        
        try:
            # Step 1: Recognize intent and extract entities
            intent_result = self.intent_recognition_engine.recognize_intent(
                natural_language_text, context or {}
            )
            
            # Step 2: Classify workflow type
            workflow_type, type_confidence = self.workflow_intent_classifier.classify_intent(
                natural_language_text
            )
            
            # Step 3: Extract workflow-specific entities
            workflow_entities = self.workflow_entity_extractor.extract_entities(
                natural_language_text, context
            )
            
            # Step 4: Select appropriate template
            template = self._select_template(workflow_type, workflow_entities)
            
            # Step 5: Generate workflow definition
            workflow_def = self._generate_workflow_definition(
                natural_language_text, workflow_type, workflow_entities, template, context
            )
            
            # Step 6: Validate and optimize workflow
            validation_result = self._validate_workflow(workflow_def)
            
            processing_time = time.time() - start_time
            
            return WorkflowParsingResult(
                workflow_definition=workflow_def,
                confidence=min(intent_result.primary_intent.confidence, type_confidence),
                parsing_success=validation_result['valid'],
                error_message=validation_result.get('error'),
                suggestions=validation_result.get('suggestions', []),
                clarification_needed=intent_result.ambiguities and [
                    amb.description for amb in intent_result.ambiguities
                ] or [],
                processing_time=processing_time,
                metadata={
                    'workflow_type': workflow_type.value,
                    'template_used': template.name if template else None,
                    'entities_found': len(workflow_entities),
                    'intent_confidence': intent_result.primary_intent.confidence
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing workflow request: {str(e)}")
            return WorkflowParsingResult(
                parsing_success=False,
                error_message=f"Parsing failed: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _select_template(self, workflow_type: WorkflowType, 
                        entities: Dict[EntityType, List[str]]) -> Optional[WorkflowTemplate]:
        """Select the most appropriate template for the workflow"""
        # Simple template selection based on workflow type
        template_mapping = {
            WorkflowType.PID_CONTROL: "temperature_control",
            WorkflowType.DATA_COLLECTION: "data_logging",
            WorkflowType.ALARM_MANAGEMENT: "alarm_monitoring",
            WorkflowType.BATCH_PROCESSING: "batch_recipe"
        }
        
        template_name = template_mapping.get(workflow_type)
        return self.templates.get(template_name) if template_name else None
    
    def _generate_workflow_definition(self, text: str, workflow_type: WorkflowType,
                                    entities: Dict[EntityType, List[str]],
                                    template: Optional[WorkflowTemplate],
                                    context: Optional[Dict[str, Any]]) -> WorkflowDefinition:
        """Generate complete workflow definition"""
        workflow_id = str(uuid.uuid4())
        workflow_name = self._generate_workflow_name(text, workflow_type)
        
        workflow = WorkflowDefinition(
            id=workflow_id,
            name=workflow_name,
            workflow_type=workflow_type,
            description=f"Auto-generated workflow: {text[:100]}...",
            tags=["auto-generated", "industrial", workflow_type.value]
        )
        
        # Generate nodes based on workflow type and template
        if workflow_type == WorkflowType.PID_CONTROL:
            self._generate_pid_control_nodes(workflow, entities)
        elif workflow_type == WorkflowType.DATA_COLLECTION:
            self._generate_data_collection_nodes(workflow, entities)
        elif workflow_type == WorkflowType.ALARM_MANAGEMENT:
            self._generate_alarm_monitoring_nodes(workflow, entities)
        elif workflow_type == WorkflowType.BATCH_PROCESSING:
            self._generate_batch_processing_nodes(workflow, entities)
        else:
            # Default monitoring workflow
            self._generate_monitoring_nodes(workflow, entities)
        
        return workflow
    
    def _generate_workflow_name(self, text: str, workflow_type: WorkflowType) -> str:
        """Generate descriptive workflow name"""
        # Extract key terms from text
        words = re.findall(r'\b\w+\b', text.lower())
        key_words = [w for w in words if len(w) > 3 and w not in ['create', 'build', 'make', 'workflow']]
        
        if key_words:
            base_name = ' '.join(key_words[:3]).title()
        else:
            base_name = workflow_type.value.replace('_', ' ').title()
        
        return f"{base_name} Workflow"
    
    def _generate_pid_control_nodes(self, workflow: WorkflowDefinition, 
                                   entities: Dict[EntityType, List[str]]):
        """Generate nodes for PID control workflow"""
        # Extract relevant parameters
        loop_names = entities.get(EntityType.LOOP_NAME, ['temperature'])
        targets = entities.get(EntityType.OPERATION_TARGET, ['valve'])
        
        loop_name = loop_names[0] if loop_names else 'process_variable'
        target = targets[0] if targets else 'control_output'
        
        # Create nodes
        read_node = self.node_generator.create_plc_read_node(f"{loop_name}_PV")
        setpoint_node = self.node_generator.create_plc_read_node(f"{loop_name}_SP")
        pid_node = self.node_generator.create_pid_controller_node(
            f"{loop_name}_PV", f"{loop_name}_SP"
        )
        write_node = self.node_generator.create_plc_write_node(f"{target}_output")
        
        # Position nodes
        read_node.position = (100, 100)
        setpoint_node.position = (100, 200)
        pid_node.position = (300, 150)
        write_node.position = (500, 150)
        
        workflow.nodes.extend([read_node, setpoint_node, pid_node, write_node])
        
        # Create connections
        workflow.connections.extend([
            WorkflowConnection(read_node.id, 0, pid_node.id, 0),
            WorkflowConnection(setpoint_node.id, 0, pid_node.id, 1),
            WorkflowConnection(pid_node.id, 0, write_node.id, 0)
        ])
    
    def _generate_data_collection_nodes(self, workflow: WorkflowDefinition,
                                       entities: Dict[EntityType, List[str]]):
        """Generate nodes for data collection workflow"""
        # Create timer for periodic data collection
        timer_node = WorkflowNode(
            id=self.node_generator.generate_node_id(),
            name="Data Collection Timer",
            type=NodeType.TIMER,
            position=(100, 100),
            parameters={"interval": 30, "unit": "seconds"}
        )
        
        # Create data read nodes
        loop_names = entities.get(EntityType.LOOP_NAME, ['temperature', 'pressure'])
        read_nodes = []
        
        for i, loop_name in enumerate(loop_names[:5]):  # Limit to 5 variables
            read_node = self.node_generator.create_plc_read_node(f"{loop_name}_value")
            read_node.position = (300, 50 + i * 80)
            read_nodes.append(read_node)
        
        # Create database write node
        db_write_node = WorkflowNode(
            id=self.node_generator.generate_node_id(),
            name="Store Data",
            type=NodeType.DATABASE_WRITE,
            position=(500, 200),
            parameters={
                "table": "process_data",
                "batch_size": 100
            }
        )
        
        workflow.nodes.extend([timer_node] + read_nodes + [db_write_node])
        
        # Create connections
        for read_node in read_nodes:
            workflow.connections.append(
                WorkflowConnection(timer_node.id, 0, read_node.id, 0)
            )
            workflow.connections.append(
                WorkflowConnection(read_node.id, 0, db_write_node.id, 0)
            )
    
    def _generate_alarm_monitoring_nodes(self, workflow: WorkflowDefinition,
                                        entities: Dict[EntityType, List[str]]):
        """Generate nodes for alarm monitoring workflow"""
        loop_names = entities.get(EntityType.LOOP_NAME, ['temperature'])
        parameters = entities.get(EntityType.PARAMETER, ['high', 'low'])
        
        loop_name = loop_names[0] if loop_names else 'process_variable'
        
        # Create monitoring nodes
        read_node = self.node_generator.create_plc_read_node(f"{loop_name}_value")
        read_node.position = (100, 150)
        
        high_alarm_node = self.node_generator.create_condition_node(
            "High Alarm", f"{loop_name}_value", 100.0
        )
        high_alarm_node.position = (300, 100)
        
        low_alarm_node = self.node_generator.create_condition_node(
            "Low Alarm", f"{loop_name}_value", 0.0
        )
        low_alarm_node.position = (300, 200)
        
        email_node = self.node_generator.create_email_node(
            ["operator@plant.com"], f"{loop_name} Alarm"
        )
        email_node.position = (500, 150)
        
        workflow.nodes.extend([read_node, high_alarm_node, low_alarm_node, email_node])
        
        # Create connections
        workflow.connections.extend([
            WorkflowConnection(read_node.id, 0, high_alarm_node.id, 0),
            WorkflowConnection(read_node.id, 0, low_alarm_node.id, 0),
            WorkflowConnection(high_alarm_node.id, 0, email_node.id, 0),
            WorkflowConnection(low_alarm_node.id, 0, email_node.id, 0)
        ])
    
    def _generate_batch_processing_nodes(self, workflow: WorkflowDefinition,
                                        entities: Dict[EntityType, List[str]]):
        """Generate nodes for batch processing workflow"""
        # Create sequence of batch steps
        step_names = ["Initialize", "Heat", "Mix", "Cool", "Discharge"]
        
        for i, step_name in enumerate(step_names):
            step_node = WorkflowNode(
                id=self.node_generator.generate_node_id(),
                name=f"Step {i+1}: {step_name}",
                type=NodeType.TIMER,
                position=(100 + i * 150, 150),
                parameters={
                    "duration": 300,  # 5 minutes
                    "step_name": step_name
                }
            )
            workflow.nodes.append(step_node)
            
            # Connect sequential steps
            if i > 0:
                workflow.connections.append(
                    WorkflowConnection(workflow.nodes[i-1].id, 0, step_node.id, 0)
                )
    
    def _generate_monitoring_nodes(self, workflow: WorkflowDefinition,
                                  entities: Dict[EntityType, List[str]]):
        """Generate basic monitoring workflow nodes"""
        # Simple monitoring workflow
        read_node = self.node_generator.create_plc_read_node("status")
        read_node.position = (100, 150)
        
        db_write_node = WorkflowNode(
            id=self.node_generator.generate_node_id(),
            name="Log Status",
            type=NodeType.DATABASE_WRITE,
            position=(300, 150),
            parameters={"table": "system_status"}
        )
        
        workflow.nodes.extend([read_node, db_write_node])
        workflow.connections.append(
            WorkflowConnection(read_node.id, 0, db_write_node.id, 0)
        )
    
    def _validate_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Validate the generated workflow"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check if workflow has nodes
        if not workflow.nodes:
            validation_result['valid'] = False
            validation_result['errors'].append("Workflow has no nodes")
        
        # Check for orphaned nodes
        connected_nodes = set()
        for conn in workflow.connections:
            connected_nodes.add(conn.source_node)
            connected_nodes.add(conn.target_node)
        
        orphaned_nodes = [node.id for node in workflow.nodes if node.id not in connected_nodes]
        if orphaned_nodes and len(workflow.nodes) > 1:
            validation_result['warnings'].append(f"Orphaned nodes found: {len(orphaned_nodes)}")
        
        # Check for invalid connections
        node_ids = {node.id for node in workflow.nodes}
        for conn in workflow.connections:
            if conn.source_node not in node_ids or conn.target_node not in node_ids:
                validation_result['valid'] = False
                validation_result['errors'].append("Invalid connection found")
        
        # Add suggestions
        if len(workflow.nodes) < 3:
            validation_result['suggestions'].append("Consider adding more nodes for a complete workflow")
        
        if not validation_result['errors']:
            validation_result['valid'] = True
        
        return validation_result
    
    def get_workflow_json(self, workflow: WorkflowDefinition) -> str:
        """Convert workflow definition to N8N JSON format"""
        n8n_workflow = {
            "name": workflow.name,
            "nodes": [],
            "connections": {},
            "active": True,
            "settings": workflow.settings,
            "id": workflow.id,
            "tags": workflow.tags,
            "meta": {
                "created_by": "plc-gbt-nlp-parser",
                "created_at": workflow.created_at.isoformat(),
                "workflow_type": workflow.workflow_type.value
            }
        }
        
        # Convert nodes to N8N format
        for node in workflow.nodes:
            n8n_node = {
                "parameters": node.parameters,
                "name": node.name,
                "type": node.type.value,
                "typeVersion": 1,
                "position": list(node.position),
                "id": node.id
            }
            if node.credentials:
                n8n_node["credentials"] = {node.credentials: {"id": "1", "name": "Default"}}
            if node.disabled:
                n8n_node["disabled"] = True
            if node.notes:
                n8n_node["notes"] = node.notes
            
            n8n_workflow["nodes"].append(n8n_node)
        
        # Convert connections to N8N format
        connections_dict = {}
        for conn in workflow.connections:
            if conn.source_node not in connections_dict:
                connections_dict[conn.source_node] = {}
            if "main" not in connections_dict[conn.source_node]:
                connections_dict[conn.source_node]["main"] = []
            
            # Ensure list exists for output index
            while len(connections_dict[conn.source_node]["main"]) <= conn.source_output:
                connections_dict[conn.source_node]["main"].append([])
            
            connections_dict[conn.source_node]["main"][conn.source_output].append({
                "node": conn.target_node,
                "type": "main",
                "index": conn.target_input
            })
        
        n8n_workflow["connections"] = connections_dict
        
        return json.dumps(n8n_workflow, indent=2)

# Example usage and testing functions
def test_workflow_parser():
    """Test the natural language workflow parser"""
    parser = NaturalLanguageWorkflowParser()
    
    test_cases = [
        "Create a temperature control loop for the reactor with PID controller",
        "Set up data logging for pressure and flow every 30 seconds to database",
        "Monitor tank level and send email alert when high or low limits are reached",
        "Execute batch recipe with 5 steps: heat, mix, react, cool, discharge"
    ]
    
    for i, test_input in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Input: {test_input}")
        
        result = parser.parse_workflow_request(test_input)
        
        print(f"Success: {result.parsing_success}")
        print(f"Confidence: {result.confidence:.2f}")
        if result.workflow_definition:
            print(f"Workflow Type: {result.workflow_definition.workflow_type.value}")
            print(f"Nodes: {len(result.workflow_definition.nodes)}")
            print(f"Connections: {len(result.workflow_definition.connections)}")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
        
        if result.suggestions:
            print(f"Suggestions: {', '.join(result.suggestions)}")

if __name__ == "__main__":
    test_workflow_parser() 