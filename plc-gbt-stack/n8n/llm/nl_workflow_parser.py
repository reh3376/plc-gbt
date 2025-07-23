"""
Natural Language Workflow Parser for N8N Integration
Phase 26.4: Natural Language Workflow Engine

This module provides natural language processing capabilities to convert
human-readable descriptions into structured N8N workflow configurations.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowRequest:
    """Structured representation of a natural language workflow request"""
    workflow_type: str
    intent: str
    entities: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class NodeTemplate:
    """Template for N8N node generation"""
    node_type: str
    display_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    position: Tuple[int, int] = (0, 0)

class NaturalLanguageWorkflowParser:
    """
    Parser for converting natural language descriptions into N8N workflows
    """
    
    def __init__(self):
        self.workflow_patterns = self._initialize_patterns()
        self.node_templates = self._initialize_node_templates()
        
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for workflow intent recognition"""
        return {
            'plc_memory_query': [
                r'(query|search|find|get|retrieve)\s+(plc|memory|data|entities)',
                r'(select|fetch)\s+.*\s+(from|in)\s+(database|memory|plc)',
                r'(show|display|list)\s+(control|loops|entities|data)'
            ],
            'control_analysis': [
                r'(analyze|assess|evaluate|examine)\s+(control|process|system)',
                r'(control|pid|loop)\s+(analysis|assessment|evaluation)',
                r'(performance|stability|tuning)\s+(analysis|check|review)'
            ],
            'data_monitoring': [
                r'(monitor|watch|track|observe)\s+(temperature|pressure|flow|level)',
                r'(real.?time|continuous|live)\s+(monitoring|tracking|data)',
                r'(subscribe|listen)\s+to\s+(changes|updates|values)'
            ],
            'safety_validation': [
                r'(safety|security|compliance)\s+(check|validation|assessment)',
                r'(validate|verify|ensure)\s+(safety|security|compliance)',
                r'(interlock|alarm|trip|emergency)\s+(system|check)'
            ],
            'process_optimization': [
                r'(optimize|improve|enhance|tune)\s+(process|performance|efficiency)',
                r'(energy|cost|efficiency)\s+(optimization|improvement)',
                r'(minimize|maximize|reduce)\s+(energy|cost|waste|time)'
            ],
            'automation_workflow': [
                r'(automate|schedule|trigger)\s+(process|task|operation)',
                r'(when|if)\s+.*\s+(then|do|execute|run)',
                r'(workflow|automation|sequence)\s+(creation|setup|configuration)'
            ]
        }
    
    def _initialize_node_templates(self) -> Dict[str, NodeTemplate]:
        """Initialize N8N node templates"""
        return {
            'plc_memory': NodeTemplate(
                node_type='plc-gbt-stack.plcMemory',
                display_name='PLC Memory Operation',
                parameters={
                    'database': 'postgresql',
                    'operation': 'query'
                }
            ),
            'industrial_llm': NodeTemplate(
                node_type='plc-gbt-stack.plcIndustrialLLM',
                display_name='Industrial LLM Analysis',
                parameters={
                    'operation': 'control_analysis',
                    'modelSelection': 'ft:gpt-4o-mini-2024-07-18:whiskey-house:industrial-control:But1jpnl',
                    'temperature': 0.3,
                    'enableSafetyValidation': True
                }
            ),
            'opcua_read': NodeTemplate(
                node_type='plc-gbt-stack.plcOPCUA',
                display_name='Read PLC Data',
                parameters={
                    'operation': 'read',
                    'serverUrl': 'opc.tcp://localhost:4840',
                    'securityMode': 'None'
                }
            ),
            'manual_trigger': NodeTemplate(
                node_type='n8n-nodes-base.manualTrigger',
                display_name='Manual Trigger',
                parameters={}
            ),
            'cron_trigger': NodeTemplate(
                node_type='n8n-nodes-base.cron',
                display_name='Schedule Trigger',
                parameters={
                    'triggerTimes': {
                        'item': [{'mode': 'everyMinute'}]
                    }
                }
            ),
            'webhook_trigger': NodeTemplate(
                node_type='n8n-nodes-base.webhook',
                display_name='Webhook Trigger',
                parameters={
                    'httpMethod': 'POST',
                    'path': 'workflow-trigger'
                }
            )
        }
    
    def parse_workflow_request(self, natural_language_input: str) -> WorkflowRequest:
        """
        Parse natural language input and return structured workflow request
        
        Args:
            natural_language_input: Human-readable workflow description
            
        Returns:
            WorkflowRequest object with parsed intent and parameters
        """
        logger.info(f"Parsing workflow request: {natural_language_input}")
        
        # Clean and normalize input
        normalized_input = self._normalize_input(natural_language_input)
        
        # Identify workflow intent
        workflow_type, confidence = self._identify_workflow_type(normalized_input)
        
        # Extract entities and parameters
        entities = self._extract_entities(normalized_input)
        parameters = self._extract_parameters(normalized_input, workflow_type)
        
        # Generate node structure
        nodes = self._generate_workflow_nodes(workflow_type, entities, parameters)
        
        return WorkflowRequest(
            workflow_type=workflow_type,
            intent=normalized_input,
            entities=entities,
            parameters=parameters,
            nodes=nodes,
            confidence=confidence
        )
    
    def _normalize_input(self, text: str) -> str:
        """Normalize input text for processing"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Handle common variations
        text = re.sub(r'\bplcs?\b', 'plc', text)
        text = re.sub(r'\btemps?\b', 'temperature', text)
        text = re.sub(r'\bpressures?\b', 'pressure', text)
        text = re.sub(r'\bflows?\b', 'flow', text)
        
        return text
    
    def _identify_workflow_type(self, text: str) -> Tuple[str, float]:
        """
        Identify the workflow type based on pattern matching
        
        Returns:
            Tuple of (workflow_type, confidence_score)
        """
        best_match = ('automation_workflow', 0.0)  # Default fallback
        
        for workflow_type, patterns in self.workflow_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Calculate confidence based on match quality
                    match_length = len(match.group())
                    text_length = len(text)
                    confidence = min(0.9, (match_length / text_length) * 2)
                    
                    if confidence > best_match[1]:
                        best_match = (workflow_type, confidence)
        
        logger.info(f"Identified workflow type: {best_match[0]} (confidence: {best_match[1]:.2f})")
        return best_match
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from the input text"""
        entities = {}
        
        # Process variables
        process_vars = ['temperature', 'pressure', 'flow', 'level', 'ph', 'conductivity']
        for var in process_vars:
            if var in text:
                entities.setdefault('process_variables', []).append(var)
        
        # Control types
        control_types = ['pid', 'cascade', 'feedforward', 'mpc', 'fuzzy']
        for ctrl in control_types:
            if ctrl in text:
                entities.setdefault('control_types', []).append(ctrl)
        
        # Equipment
        equipment = ['reactor', 'pump', 'valve', 'sensor', 'motor', 'heater', 'cooler']
        for equip in equipment:
            if equip in text:
                entities.setdefault('equipment', []).append(equip)
        
        # Time-related entities
        time_patterns = [
            (r'every\s+(\d+)\s+(minutes?|hours?|days?)', 'schedule_interval'),
            (r'(\d+)\s+(seconds?|minutes?|hours?)', 'time_duration'),
            (r'(hourly|daily|weekly|monthly)', 'schedule_frequency')
        ]
        
        for pattern, entity_type in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        # Numerical values
        number_patterns = [
            (r'(\d+(?:\.\d+)?)\s*(°c|celsius|°f|fahrenheit)', 'temperature_values'),
            (r'(\d+(?:\.\d+)?)\s*(bar|psi|pa|kpa)', 'pressure_values'),
            (r'(\d+(?:\.\d+)?)\s*(l/min|gpm|m3/h)', 'flow_values')
        ]
        
        for pattern, entity_type in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def _extract_parameters(self, text: str, workflow_type: str) -> Dict[str, Any]:
        """Extract workflow-specific parameters"""
        parameters = {}
        
        if workflow_type == 'plc_memory_query':
            # Extract query parameters
            if 'where' in text or 'filter' in text:
                parameters['use_filters'] = True
            
            limit_match = re.search(r'(\d+)\s+(records?|results?|rows?)', text)
            if limit_match:
                parameters['limit'] = int(limit_match.group(1))
            else:
                parameters['limit'] = 10  # Default
                
        elif workflow_type == 'control_analysis':
            # Extract analysis parameters
            if 'stability' in text:
                parameters['include_stability_analysis'] = True
            if 'performance' in text:
                parameters['include_performance_metrics'] = True
            if 'tuning' in text:
                parameters['include_tuning_recommendations'] = True
                
        elif workflow_type == 'data_monitoring':
            # Extract monitoring parameters
            if 'real-time' in text or 'continuous' in text:
                parameters['monitoring_mode'] = 'real_time'
            else:
                parameters['monitoring_mode'] = 'periodic'
                
            interval_match = re.search(r'every\s+(\d+)\s+(seconds?|minutes?)', text)
            if interval_match:
                unit = interval_match.group(2).rstrip('s')
                value = int(interval_match.group(1))
                if unit == 'minute':
                    value *= 60
                parameters['monitoring_interval'] = value * 1000  # Convert to milliseconds
            else:
                parameters['monitoring_interval'] = 5000  # Default 5 seconds
                
        elif workflow_type == 'automation_workflow':
            # Extract automation parameters
            if 'when' in text or 'if' in text:
                parameters['trigger_type'] = 'conditional'
            elif 'schedule' in text or 'every' in text:
                parameters['trigger_type'] = 'scheduled'
            else:
                parameters['trigger_type'] = 'manual'
        
        return parameters
    
    def _generate_workflow_nodes(self, workflow_type: str, entities: Dict[str, Any], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate N8N workflow nodes based on parsed input"""
        nodes = []
        position_x = 120
        position_y = 300
        
        # Start with appropriate trigger
        trigger_type = parameters.get('trigger_type', 'manual')
        if trigger_type == 'scheduled':
            trigger_node = self._create_node('cron_trigger', position_x, position_y)
        elif trigger_type == 'conditional':
            trigger_node = self._create_node('webhook_trigger', position_x, position_y)
        else:
            trigger_node = self._create_node('manual_trigger', position_x, position_y)
        
        nodes.append(trigger_node)
        position_x += 200
        
        # Add workflow-specific nodes
        if workflow_type == 'plc_memory_query':
            memory_node = self._create_node('plc_memory', position_x, position_y)
            memory_node['parameters'].update({
                'database': 'postgresql',
                'operation': 'query',
                'query': self._generate_sql_query(entities, parameters)
            })
            nodes.append(memory_node)
            
        elif workflow_type == 'control_analysis':
            # Add memory query first
            memory_node = self._create_node('plc_memory', position_x, position_y)
            memory_node['parameters'].update({
                'database': 'postgresql',
                'operation': 'query',
                'query': "SELECT * FROM plc_memory_entities WHERE entity_type = 'control_loop' LIMIT 5;"
            })
            nodes.append(memory_node)
            position_x += 200
            
            # Add LLM analysis
            llm_node = self._create_node('industrial_llm', position_x, position_y)
            llm_node['parameters'].update({
                'operation': 'control_analysis',
                'processDescription': "{{$json['result']['rows'][0]['description']}}",
                'responseFormat': 'structured'
            })
            nodes.append(llm_node)
            
        elif workflow_type == 'data_monitoring':
            # Add OPC-UA read node
            opcua_node = self._create_node('opcua_read', position_x, position_y)
            
            # Configure node IDs based on entities
            node_ids = []
            if 'process_variables' in entities:
                for var in entities['process_variables']:
                    node_ids.append(f"ns=2;s={var.capitalize()}")
            
            if not node_ids:
                node_ids = ["ns=2;s=Temperature", "ns=2;s=Pressure", "ns=2;s=FlowRate"]
            
            opcua_node['parameters'].update({
                'nodeIds': '\n'.join(node_ids),
                'includeTimestamps': True
            })
            nodes.append(opcua_node)
            
        elif workflow_type == 'safety_validation':
            # Add safety assessment
            llm_node = self._create_node('industrial_llm', position_x, position_y)
            llm_node['parameters'].update({
                'operation': 'safety_assessment',
                'processDescription': "Safety validation for industrial process",
                'enableSafetyValidation': True,
                'responseFormat': 'report'
            })
            nodes.append(llm_node)
            
        elif workflow_type == 'process_optimization':
            # Add optimization analysis
            llm_node = self._create_node('industrial_llm', position_x, position_y)
            llm_node['parameters'].update({
                'operation': 'process_optimization',
                'processDescription': "Process optimization analysis",
                'responseFormat': 'structured'
            })
            nodes.append(llm_node)
        
        return nodes
    
    def _create_node(self, template_name: str, x: int, y: int) -> Dict[str, Any]:
        """Create a node from template"""
        template = self.node_templates[template_name]
        
        return {
            'id': f"{template_name}-{int(datetime.now().timestamp())}",
            'name': template.display_name,
            'type': template.node_type,
            'typeVersion': 1,
            'position': [x, y],
            'parameters': template.parameters.copy()
        }
    
    def _generate_sql_query(self, entities: Dict[str, Any], parameters: Dict[str, Any]) -> str:
        """Generate SQL query based on extracted entities and parameters"""
        base_query = "SELECT * FROM plc_memory_entities"
        conditions = []
        
        # Add entity-based conditions
        if 'process_variables' in entities:
            var_conditions = [f"entity_name ILIKE '%{var}%'" for var in entities['process_variables']]
            conditions.append(f"({' OR '.join(var_conditions)})")
        
        if 'control_types' in entities:
            ctrl_conditions = [f"entity_type ILIKE '%{ctrl}%'" for ctrl in entities['control_types']]
            conditions.append(f"({' OR '.join(ctrl_conditions)})")
        
        if 'equipment' in entities:
            equip_conditions = [f"description ILIKE '%{equip}%'" for equip in entities['equipment']]
            conditions.append(f"({' OR '.join(equip_conditions)})")
        
        # Build final query
        if conditions:
            base_query += f" WHERE {' AND '.join(conditions)}"
        
        # Add limit
        limit = parameters.get('limit', 10)
        base_query += f" LIMIT {limit};"
        
        return base_query
    
    def generate_n8n_workflow(self, workflow_request: WorkflowRequest) -> Dict[str, Any]:
        """
        Generate complete N8N workflow JSON from parsed request
        
        Args:
            workflow_request: Parsed workflow request
            
        Returns:
            Complete N8N workflow JSON
        """
        workflow = {
            "name": f"Generated Workflow - {workflow_request.workflow_type.replace('_', ' ').title()}",
            "nodes": workflow_request.nodes,
            "connections": self._generate_connections(workflow_request.nodes),
            "active": False,
            "settings": {},
            "versionId": "1.0.0",
            "meta": {
                "templateCredsSetupCompleted": True,
                "instanceId": "plc-gbt-n8n-instance",
                "generatedFrom": "natural_language",
                "originalRequest": workflow_request.intent,
                "confidence": workflow_request.confidence,
                "timestamp": workflow_request.timestamp
            },
            "id": f"generated-{workflow_request.workflow_type}-{int(datetime.now().timestamp())}",
            "tags": [
                {
                    "id": "generated",
                    "name": "AI Generated"
                },
                {
                    "id": workflow_request.workflow_type.replace('_', '-'),
                    "name": workflow_request.workflow_type.replace('_', ' ').title()
                }
            ]
        }
        
        return workflow
    
    def _generate_connections(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate connections between nodes"""
        connections = {}
        
        for i, node in enumerate(nodes[:-1]):
            next_node = nodes[i + 1]
            connections[node['name']] = {
                "main": [
                    [
                        {
                            "node": next_node['name'],
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        
        return connections


# Example usage and testing
def main():
    """Example usage of the Natural Language Workflow Parser"""
    parser = NaturalLanguageWorkflowParser()
    
    # Test cases
    test_cases = [
        "Analyze the temperature control system for stability",
        "Monitor pressure and flow rate every 30 seconds",
        "Query PLC memory for all control loops with temperature",
        "Validate safety interlocks for the reactor system",
        "Optimize the process efficiency for energy consumption",
        "Create a workflow that runs every hour to check system health"
    ]
    
    for test_input in test_cases:
        print(f"\n{'='*60}")
        print(f"Input: {test_input}")
        print(f"{'='*60}")
        
        workflow_request = parser.parse_workflow_request(test_input)
        
        print(f"Workflow Type: {workflow_request.workflow_type}")
        print(f"Confidence: {workflow_request.confidence:.2f}")
        print(f"Entities: {workflow_request.entities}")
        print(f"Parameters: {workflow_request.parameters}")
        print(f"Nodes: {len(workflow_request.nodes)} nodes generated")
        
        # Generate full workflow
        workflow_json = parser.generate_n8n_workflow(workflow_request)
        print(f"Generated workflow: {workflow_json['name']}")


if __name__ == "__main__":
    main() 