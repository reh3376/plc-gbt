"""
Industrial Automation Workflow Templates Library
Phase 26.4.4: Pre-built templates for common industrial automation patterns

Provides comprehensive template library for industrial control loops, data collection,
batch processing, alarm management, and maintenance workflows.
"""

import copy
import json
import logging
import os

# Import workflow components
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), '../../llm'))


logger = logging.getLogger(__name__)

class TemplateCategory(Enum):
    """Categories of workflow templates"""
    CONTROL_LOOPS = "control_loops"
    DATA_COLLECTION = "data_collection"
    ALARM_MANAGEMENT = "alarm_management"
    BATCH_PROCESSING = "batch_processing"
    MAINTENANCE = "maintenance"
    SAFETY_SYSTEMS = "safety_systems"
    REPORTING = "reporting"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"

class IndustryType(Enum):
    """Industry types for specialized templates"""
    CHEMICAL = "chemical"
    PHARMACEUTICAL = "pharmaceutical"
    OIL_GAS = "oil_gas"
    FOOD_BEVERAGE = "food_beverage"
    WATER_TREATMENT = "water_treatment"
    POWER_GENERATION = "power_generation"
    MANUFACTURING = "manufacturing"
    PULP_PAPER = "pulp_paper"
    METALS_MINING = "metals_mining"
    GENERAL = "general"

class ComplexityLevel(Enum):
    """Complexity levels for templates"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class TemplateParameter:
    """Template parameter definition"""
    name: str
    description: str
    parameter_type: str  # string, number, boolean, select
    required: bool = True
    default_value: Any = None
    options: List[str] = field(default_factory=list)  # For select type
    validation_pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

@dataclass
class WorkflowTemplate:
    """Complete workflow template definition"""
    id: str
    name: str
    description: str
    category: TemplateCategory
    industry: IndustryType
    complexity: ComplexityLevel
    author: str = "PLC-GBT AI"
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    parameters: List[TemplateParameter] = field(default_factory=list)
    workflow_definition: Dict[str, Any] = field(default_factory=dict)
    usage_instructions: str = ""
    prerequisites: List[str] = field(default_factory=list)
    estimated_setup_time: str = "15-30 minutes"
    maintenance_notes: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class IndustrialTemplateLibrary:
    """Library of industrial automation workflow templates"""

    def __init__(self):
        self.templates = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize the template library with pre-built templates"""
        self._create_control_loop_templates()
        self._create_data_collection_templates()
        self._create_alarm_management_templates()
        self._create_batch_processing_templates()
        self._create_maintenance_templates()
        self._create_safety_system_templates()
        self._create_reporting_templates()
        self._create_integration_templates()

    def _create_control_loop_templates(self):
        """Create control loop templates"""

        # Basic Temperature Control Template
        temp_control_template = WorkflowTemplate(
            id="temp_control_basic",
            name="Basic Temperature Control Loop",
            description="Simple PID temperature control with alarm monitoring",
            category=TemplateCategory.CONTROL_LOOPS,
            industry=IndustryType.GENERAL,
            complexity=ComplexityLevel.BASIC,
            tags=["temperature", "PID", "control", "basic"],
            parameters=[
                TemplateParameter(
                    name="loop_name",
                    description="Name of the control loop",
                    parameter_type="string",
                    default_value="TIC_001"
                ),
                TemplateParameter(
                    name="pv_tag",
                    description="Process variable tag name",
                    parameter_type="string",
                    default_value="TT_001.PV"
                ),
                TemplateParameter(
                    name="sp_tag",
                    description="Setpoint tag name",
                    parameter_type="string",
                    default_value="TIC_001.SP"
                ),
                TemplateParameter(
                    name="cv_tag",
                    description="Control variable output tag",
                    parameter_type="string",
                    default_value="TIC_001.CV"
                ),
                TemplateParameter(
                    name="setpoint_value",
                    description="Default setpoint value",
                    parameter_type="number",
                    default_value=85.0,
                    min_value=0.0,
                    max_value=200.0
                ),
                TemplateParameter(
                    name="kp",
                    description="Proportional gain",
                    parameter_type="number",
                    default_value=1.0,
                    min_value=0.1,
                    max_value=10.0
                ),
                TemplateParameter(
                    name="ki",
                    description="Integral gain",
                    parameter_type="number",
                    default_value=0.1,
                    min_value=0.0,
                    max_value=5.0
                ),
                TemplateParameter(
                    name="kd",
                    description="Derivative gain",
                    parameter_type="number",
                    default_value=0.0,
                    min_value=0.0,
                    max_value=2.0
                ),
                TemplateParameter(
                    name="high_alarm",
                    description="High temperature alarm limit",
                    parameter_type="number",
                    default_value=95.0
                ),
                TemplateParameter(
                    name="low_alarm",
                    description="Low temperature alarm limit",
                    parameter_type="number",
                    default_value=75.0
                ),
                TemplateParameter(
                    name="alarm_email",
                    description="Email address for alarms",
                    parameter_type="string",
                    default_value="operator@plant.com"
                )
            ],
            workflow_definition=self._get_temperature_control_workflow(),
            usage_instructions="""
1. Configure PLC tags for temperature sensor and control valve
2. Set appropriate PID tuning parameters
3. Configure alarm limits based on process requirements
4. Test in manual mode before enabling automatic control
5. Monitor performance and adjust tuning as needed
            """,
            prerequisites=[
                "Temperature sensor calibrated and operational",
                "Control valve installed and tested",
                "PLC communication established",
                "Email SMTP server configured"
            ],
            maintenance_notes="Review PID performance monthly, recalibrate sensors quarterly"
        )

        # Advanced Cascade Control Template
        cascade_control_template = WorkflowTemplate(
            id="cascade_control_advanced",
            name="Cascade Temperature Control System",
            description="Advanced cascade control with primary and secondary loops",
            category=TemplateCategory.CONTROL_LOOPS,
            industry=IndustryType.CHEMICAL,
            complexity=ComplexityLevel.ADVANCED,
            tags=["cascade", "temperature", "flow", "advanced", "control"],
            parameters=[
                TemplateParameter(
                    name="primary_loop_name",
                    description="Primary loop name (temperature)",
                    parameter_type="string",
                    default_value="TIC_001"
                ),
                TemplateParameter(
                    name="secondary_loop_name",
                    description="Secondary loop name (flow)",
                    parameter_type="string",
                    default_value="FIC_001"
                ),
                TemplateParameter(
                    name="temp_pv_tag",
                    description="Temperature process variable",
                    parameter_type="string",
                    default_value="TT_001.PV"
                ),
                TemplateParameter(
                    name="flow_pv_tag",
                    description="Flow process variable",
                    parameter_type="string",
                    default_value="FT_001.PV"
                ),
                TemplateParameter(
                    name="temp_setpoint",
                    description="Temperature setpoint",
                    parameter_type="number",
                    default_value=120.0
                ),
                TemplateParameter(
                    name="cascade_ratio",
                    description="Cascade controller ratio",
                    parameter_type="number",
                    default_value=1.5,
                    min_value=0.5,
                    max_value=5.0
                )
            ],
            workflow_definition=self._get_cascade_control_workflow(),
            usage_instructions="""
1. Configure primary temperature control loop
2. Set up secondary flow control loop
3. Tune secondary loop first, then primary loop
4. Test cascade operation with setpoint changes
5. Implement feedforward compensation if needed
            """,
            prerequisites=[
                "Both temperature and flow sensors operational",
                "Control valve sized for cascade operation",
                "Advanced PLC with cascade control capability"
            ]
        )

        self.templates["temp_control_basic"] = temp_control_template
        self.templates["cascade_control_advanced"] = cascade_control_template

    def _create_data_collection_templates(self):
        """Create data collection templates"""

        # Historian Data Logger Template
        historian_template = WorkflowTemplate(
            id="data_historian_basic",
            name="Process Data Historian",
            description="Collect and store process data for historical trending",
            category=TemplateCategory.DATA_COLLECTION,
            industry=IndustryType.GENERAL,
            complexity=ComplexityLevel.BASIC,
            tags=["historian", "data logging", "trending"],
            parameters=[
                TemplateParameter(
                    name="collection_interval",
                    description="Data collection interval (seconds)",
                    parameter_type="number",
                    default_value=30,
                    min_value=1,
                    max_value=3600
                ),
                TemplateParameter(
                    name="tag_list",
                    description="Comma-separated list of tags to collect",
                    parameter_type="string",
                    default_value="TT_001,PT_001,FT_001,LT_001"
                ),
                TemplateParameter(
                    name="database_connection",
                    description="Database connection string",
                    parameter_type="string",
                    default_value="postgresql://user:pass@localhost:5432/process_data"
                ),
                TemplateParameter(
                    name="data_retention_days",
                    description="Data retention period in days",
                    parameter_type="number",
                    default_value=365,
                    min_value=1,
                    max_value=3650
                ),
                TemplateParameter(
                    name="compression_enabled",
                    description="Enable data compression",
                    parameter_type="boolean",
                    default_value=True
                )
            ],
            workflow_definition=self._get_historian_workflow(),
            usage_instructions="""
1. Configure tag list for data collection
2. Set appropriate collection interval based on process dynamics
3. Set up database connection and tables
4. Configure data retention policies
5. Enable compression to save storage space
            """,
            prerequisites=[
                "Database server configured and accessible",
                "PLC tags defined and accessible",
                "Adequate storage space allocated"
            ]
        )

        # Real-time Analytics Template
        analytics_template = WorkflowTemplate(
            id="realtime_analytics",
            name="Real-time Process Analytics",
            description="Continuous analysis of process data with trend detection",
            category=TemplateCategory.DATA_COLLECTION,
            industry=IndustryType.MANUFACTURING,
            complexity=ComplexityLevel.INTERMEDIATE,
            tags=["analytics", "real-time", "trending", "statistics"],
            parameters=[
                TemplateParameter(
                    name="analysis_window",
                    description="Analysis window size (minutes)",
                    parameter_type="number",
                    default_value=15,
                    min_value=1,
                    max_value=120
                ),
                TemplateParameter(
                    name="trend_sensitivity",
                    description="Trend detection sensitivity",
                    parameter_type="select",
                    options=["low", "medium", "high"],
                    default_value="medium"
                ),
                TemplateParameter(
                    name="statistical_metrics",
                    description="Statistical metrics to calculate",
                    parameter_type="string",
                    default_value="mean,std,min,max,trend"
                )
            ],
            workflow_definition=self._get_analytics_workflow()
        )

        self.templates["data_historian_basic"] = historian_template
        self.templates["realtime_analytics"] = analytics_template

    def _create_alarm_management_templates(self):
        """Create alarm management templates"""

        # Multi-level Alarm System Template
        alarm_system_template = WorkflowTemplate(
            id="alarm_system_multilevel",
            name="Multi-level Alarm Management System",
            description="Comprehensive alarm system with priority levels and escalation",
            category=TemplateCategory.ALARM_MANAGEMENT,
            industry=IndustryType.GENERAL,
            complexity=ComplexityLevel.INTERMEDIATE,
            tags=["alarms", "notifications", "escalation", "safety"],
            parameters=[
                TemplateParameter(
                    name="critical_alarm_tags",
                    description="Critical alarm tags (comma-separated)",
                    parameter_type="string",
                    default_value="PT_001_HH,TT_001_HH,LT_001_LL"
                ),
                TemplateParameter(
                    name="warning_alarm_tags",
                    description="Warning alarm tags (comma-separated)",
                    parameter_type="string",
                    default_value="PT_001_H,TT_001_H,LT_001_L"
                ),
                TemplateParameter(
                    name="primary_contacts",
                    description="Primary notification contacts",
                    parameter_type="string",
                    default_value="operator@plant.com,supervisor@plant.com"
                ),
                TemplateParameter(
                    name="escalation_contacts",
                    description="Escalation contacts",
                    parameter_type="string",
                    default_value="manager@plant.com,emergency@plant.com"
                ),
                TemplateParameter(
                    name="escalation_delay",
                    description="Escalation delay (minutes)",
                    parameter_type="number",
                    default_value=15,
                    min_value=1,
                    max_value=60
                ),
                TemplateParameter(
                    name="sms_enabled",
                    description="Enable SMS notifications",
                    parameter_type="boolean",
                    default_value=True
                )
            ],
            workflow_definition=self._get_alarm_system_workflow(),
            usage_instructions="""
1. Configure alarm tags and their priority levels
2. Set up notification contact lists
3. Configure escalation procedures and timings
4. Test all notification methods
5. Document alarm response procedures
            """,
            prerequisites=[
                "Alarm tags configured in PLC",
                "Email server configuration",
                "SMS gateway setup (if enabled)",
                "Alarm response procedures documented"
            ]
        )

        self.templates["alarm_system_multilevel"] = alarm_system_template

    def _create_batch_processing_templates(self):
        """Create batch processing templates"""

        # Recipe Management Template
        recipe_template = WorkflowTemplate(
            id="batch_recipe_management",
            name="Automated Batch Recipe Execution",
            description="Execute batch recipes with phase management and quality tracking",
            category=TemplateCategory.BATCH_PROCESSING,
            industry=IndustryType.CHEMICAL,
            complexity=ComplexityLevel.ADVANCED,
            tags=["batch", "recipe", "automation", "quality"],
            parameters=[
                TemplateParameter(
                    name="recipe_name",
                    description="Batch recipe name",
                    parameter_type="string",
                    default_value="Standard_Production_Recipe_v1.2"
                ),
                TemplateParameter(
                    name="batch_size",
                    description="Batch size (kg)",
                    parameter_type="number",
                    default_value=1000,
                    min_value=100,
                    max_value=5000
                ),
                TemplateParameter(
                    name="phases",
                    description="Recipe phases (comma-separated)",
                    parameter_type="string",
                    default_value="prep,heat,add_catalyst,react,cool,discharge"
                ),
                TemplateParameter(
                    name="quality_checks",
                    description="Quality check points",
                    parameter_type="string",
                    default_value="after_heat,after_react,final"
                ),
                TemplateParameter(
                    name="operator_approval",
                    description="Require operator approval for phase transitions",
                    parameter_type="boolean",
                    default_value=True
                )
            ],
            workflow_definition=self._get_batch_recipe_workflow(),
            usage_instructions="""
1. Define recipe phases and parameters
2. Configure quality check procedures
3. Set up operator approval workflows
4. Test recipe execution in simulation mode
5. Validate with actual production batch
            """,
            prerequisites=[
                "Batch equipment properly configured",
                "Recipe parameters validated",
                "Quality control procedures defined",
                "Operator training completed"
            ]
        )

        self.templates["batch_recipe_management"] = recipe_template

    def _create_maintenance_templates(self):
        """Create maintenance workflow templates"""

        # Predictive Maintenance Template
        predictive_maintenance_template = WorkflowTemplate(
            id="predictive_maintenance",
            name="Predictive Maintenance System",
            description="Monitor equipment health and predict maintenance needs",
            category=TemplateCategory.MAINTENANCE,
            industry=IndustryType.MANUFACTURING,
            complexity=ComplexityLevel.ADVANCED,
            tags=["maintenance", "predictive", "monitoring", "health"],
            parameters=[
                TemplateParameter(
                    name="equipment_tags",
                    description="Equipment monitoring tags",
                    parameter_type="string",
                    default_value="VIB_001,TEMP_001,CURR_001"
                ),
                TemplateParameter(
                    name="analysis_interval",
                    description="Health analysis interval (hours)",
                    parameter_type="number",
                    default_value=24,
                    min_value=1,
                    max_value=168
                ),
                TemplateParameter(
                    name="alert_threshold",
                    description="Maintenance alert threshold (0-100%)",
                    parameter_type="number",
                    default_value=80,
                    min_value=50,
                    max_value=95
                )
            ],
            workflow_definition=self._get_predictive_maintenance_workflow()
        )

        self.templates["predictive_maintenance"] = predictive_maintenance_template

    def _create_safety_system_templates(self):
        """Create safety system templates"""

        # Emergency Shutdown Template
        esd_template = WorkflowTemplate(
            id="emergency_shutdown",
            name="Emergency Shutdown System",
            description="Automated emergency shutdown with safety interlocks",
            category=TemplateCategory.SAFETY_SYSTEMS,
            industry=IndustryType.OIL_GAS,
            complexity=ComplexityLevel.EXPERT,
            tags=["safety", "emergency", "shutdown", "interlocks"],
            parameters=[
                TemplateParameter(
                    name="trigger_conditions",
                    description="Emergency trigger conditions",
                    parameter_type="string",
                    default_value="high_pressure,high_temperature,low_flow"
                ),
                TemplateParameter(
                    name="shutdown_sequence",
                    description="Shutdown sequence steps",
                    parameter_type="string",
                    default_value="close_valves,stop_pumps,vent_system,notify_emergency"
                )
            ],
            workflow_definition=self._get_emergency_shutdown_workflow()
        )

        self.templates["emergency_shutdown"] = esd_template

    def _create_reporting_templates(self):
        """Create reporting workflow templates"""

        # Production Report Template
        production_report_template = WorkflowTemplate(
            id="production_reporting",
            name="Automated Production Reporting",
            description="Generate daily, weekly, and monthly production reports",
            category=TemplateCategory.REPORTING,
            industry=IndustryType.MANUFACTURING,
            complexity=ComplexityLevel.INTERMEDIATE,
            tags=["reporting", "production", "KPI", "analytics"],
            parameters=[
                TemplateParameter(
                    name="report_frequency",
                    description="Report generation frequency",
                    parameter_type="select",
                    options=["daily", "weekly", "monthly"],
                    default_value="daily"
                ),
                TemplateParameter(
                    name="kpi_metrics",
                    description="KPI metrics to include",
                    parameter_type="string",
                    default_value="production_rate,efficiency,quality_score,downtime"
                )
            ],
            workflow_definition=self._get_production_report_workflow()
        )

        self.templates["production_reporting"] = production_report_template

    def _create_integration_templates(self):
        """Create system integration templates"""

        # MES Integration Template
        mes_integration_template = WorkflowTemplate(
            id="mes_integration",
            name="MES System Integration",
            description="Integrate PLC data with Manufacturing Execution System",
            category=TemplateCategory.INTEGRATION,
            industry=IndustryType.MANUFACTURING,
            complexity=ComplexityLevel.ADVANCED,
            tags=["MES", "integration", "data exchange"],
            parameters=[
                TemplateParameter(
                    name="mes_endpoint",
                    description="MES system API endpoint",
                    parameter_type="string",
                    default_value="https://mes.company.com/api/v1"
                ),
                TemplateParameter(
                    name="sync_interval",
                    description="Data synchronization interval (minutes)",
                    parameter_type="number",
                    default_value=5,
                    min_value=1,
                    max_value=60
                )
            ],
            workflow_definition=self._get_mes_integration_workflow()
        )

        self.templates["mes_integration"] = mes_integration_template

    # Workflow definition methods
    def _get_temperature_control_workflow(self) -> Dict[str, Any]:
        """Get temperature control workflow definition"""
        return {
            "name": "{{loop_name}} Temperature Control",
            "nodes": [
                {
                    "id": "read_pv",
                    "name": "Read Temperature",
                    "type": "plc_read",
                    "parameters": {
                        "tag_name": "{{pv_tag}}",
                        "polling_rate": 1000
                    },
                    "position": [100, 100]
                },
                {
                    "id": "read_sp",
                    "name": "Read Setpoint",
                    "type": "plc_read",
                    "parameters": {
                        "tag_name": "{{sp_tag}}",
                        "polling_rate": 5000
                    },
                    "position": [100, 200]
                },
                {
                    "id": "pid_controller",
                    "name": "PID Controller",
                    "type": "pid_controller",
                    "parameters": {
                        "kp": "{{kp}}",
                        "ki": "{{ki}}",
                        "kd": "{{kd}}",
                        "output_min": 0,
                        "output_max": 100
                    },
                    "position": [300, 150]
                },
                {
                    "id": "write_cv",
                    "name": "Write Control Output",
                    "type": "plc_write",
                    "parameters": {
                        "tag_name": "{{cv_tag}}"
                    },
                    "position": [500, 150]
                },
                {
                    "id": "high_alarm",
                    "name": "High Temperature Alarm",
                    "type": "condition",
                    "parameters": {
                        "condition": "value > {{high_alarm}}",
                        "alarm_priority": "high"
                    },
                    "position": [300, 50]
                },
                {
                    "id": "low_alarm",
                    "name": "Low Temperature Alarm",
                    "type": "condition",
                    "parameters": {
                        "condition": "value < {{low_alarm}}",
                        "alarm_priority": "medium"
                    },
                    "position": [300, 250]
                },
                {
                    "id": "email_alert",
                    "name": "Send Email Alert",
                    "type": "email",
                    "parameters": {
                        "recipients": ["{{alarm_email}}"],
                        "subject": "{{loop_name}} Temperature Alarm",
                        "body": "Temperature alarm triggered: {{alarm_message}}"
                    },
                    "position": [500, 50]
                }
            ],
            "connections": [
                {"source": "read_pv", "target": "pid_controller", "source_output": 0, "target_input": 0},
                {"source": "read_sp", "target": "pid_controller", "source_output": 0, "target_input": 1},
                {"source": "pid_controller", "target": "write_cv", "source_output": 0, "target_input": 0},
                {"source": "read_pv", "target": "high_alarm", "source_output": 0, "target_input": 0},
                {"source": "read_pv", "target": "low_alarm", "source_output": 0, "target_input": 0},
                {"source": "high_alarm", "target": "email_alert", "source_output": 0, "target_input": 0},
                {"source": "low_alarm", "target": "email_alert", "source_output": 0, "target_input": 0}
            ]
        }

    def _get_cascade_control_workflow(self) -> Dict[str, Any]:
        """Get cascade control workflow definition"""
        return {
            "name": "{{primary_loop_name}} Cascade Control",
            "nodes": [
                {
                    "id": "temp_pv",
                    "name": "Temperature PV",
                    "type": "plc_read",
                    "parameters": {"tag_name": "{{temp_pv_tag}}"},
                    "position": [100, 100]
                },
                {
                    "id": "flow_pv",
                    "name": "Flow PV",
                    "type": "plc_read",
                    "parameters": {"tag_name": "{{flow_pv_tag}}"},
                    "position": [100, 200]
                },
                {
                    "id": "primary_pid",
                    "name": "Primary Temperature PID",
                    "type": "pid_controller",
                    "parameters": {
                        "setpoint": "{{temp_setpoint}}",
                        "cascade_mode": True
                    },
                    "position": [300, 100]
                },
                {
                    "id": "secondary_pid",
                    "name": "Secondary Flow PID",
                    "type": "pid_controller",
                    "parameters": {
                        "cascade_ratio": "{{cascade_ratio}}"
                    },
                    "position": [500, 150]
                }
            ]
        }

    def _get_historian_workflow(self) -> Dict[str, Any]:
        """Get data historian workflow definition"""
        return {
            "name": "Process Data Historian",
            "nodes": [
                {
                    "id": "timer",
                    "name": "Collection Timer",
                    "type": "timer",
                    "parameters": {"interval": "{{collection_interval}}"},
                    "position": [100, 100]
                },
                {
                    "id": "collect_data",
                    "name": "Collect Process Data",
                    "type": "plc_read",
                    "parameters": {"tag_list": "{{tag_list}}"},
                    "position": [300, 100]
                },
                {
                    "id": "store_data",
                    "name": "Store to Database",
                    "type": "database_write",
                    "parameters": {
                        "connection": "{{database_connection}}",
                        "table": "process_history",
                        "compression": "{{compression_enabled}}"
                    },
                    "position": [500, 100]
                }
            ]
        }

    def _get_analytics_workflow(self) -> Dict[str, Any]:
        """Get real-time analytics workflow definition"""
        return {
            "name": "Real-time Process Analytics",
            "nodes": [
                {
                    "id": "data_buffer",
                    "name": "Data Buffer",
                    "type": "calculator",
                    "parameters": {"window_size": "{{analysis_window}}"},
                    "position": [100, 100]
                },
                {
                    "id": "trend_analysis",
                    "name": "Trend Analysis",
                    "type": "trend_analysis",
                    "parameters": {"sensitivity": "{{trend_sensitivity}}"},
                    "position": [300, 100]
                }
            ]
        }

    def _get_alarm_system_workflow(self) -> Dict[str, Any]:
        """Get alarm system workflow definition"""
        return {
            "name": "Multi-level Alarm System",
            "nodes": [
                {
                    "id": "monitor_critical",
                    "name": "Monitor Critical Alarms",
                    "type": "condition",
                    "parameters": {"alarm_tags": "{{critical_alarm_tags}}"},
                    "position": [100, 100]
                },
                {
                    "id": "immediate_notify",
                    "name": "Immediate Notification",
                    "type": "email",
                    "parameters": {"recipients": "{{primary_contacts}}"},
                    "position": [300, 100]
                },
                {
                    "id": "escalation_timer",
                    "name": "Escalation Timer",
                    "type": "timer",
                    "parameters": {"delay": "{{escalation_delay}}"},
                    "position": [300, 200]
                },
                {
                    "id": "escalate",
                    "name": "Escalate Alert",
                    "type": "email",
                    "parameters": {"recipients": "{{escalation_contacts}}"},
                    "position": [500, 200]
                }
            ]
        }

    def _get_batch_recipe_workflow(self) -> Dict[str, Any]:
        """Get batch recipe workflow definition"""
        return {
            "name": "{{recipe_name}} Execution",
            "nodes": [
                {
                    "id": "recipe_start",
                    "name": "Start Recipe",
                    "type": "timer",
                    "parameters": {"batch_id": "{{batch_id}}"},
                    "position": [100, 100]
                },
                {
                    "id": "phase_control",
                    "name": "Phase Controller",
                    "type": "calculator",
                    "parameters": {"phases": "{{phases}}"},
                    "position": [300, 100]
                },
                {
                    "id": "quality_check",
                    "name": "Quality Control",
                    "type": "condition",
                    "parameters": {"check_points": "{{quality_checks}}"},
                    "position": [500, 100]
                }
            ]
        }

    def _get_predictive_maintenance_workflow(self) -> Dict[str, Any]:
        """Get predictive maintenance workflow definition"""
        return {
            "name": "Predictive Maintenance Monitor",
            "nodes": [
                {
                    "id": "collect_health",
                    "name": "Collect Health Data",
                    "type": "plc_read",
                    "parameters": {"tags": "{{equipment_tags}}"},
                    "position": [100, 100]
                },
                {
                    "id": "analyze_health",
                    "name": "Health Analysis",
                    "type": "statistical_analysis",
                    "parameters": {"interval": "{{analysis_interval}}"},
                    "position": [300, 100]
                }
            ]
        }

    def _get_emergency_shutdown_workflow(self) -> Dict[str, Any]:
        """Get emergency shutdown workflow definition"""
        return {
            "name": "Emergency Shutdown System",
            "nodes": [
                {
                    "id": "safety_monitor",
                    "name": "Safety Monitoring",
                    "type": "condition",
                    "parameters": {"triggers": "{{trigger_conditions}}"},
                    "position": [100, 100]
                },
                {
                    "id": "emergency_action",
                    "name": "Emergency Actions",
                    "type": "plc_write",
                    "parameters": {"sequence": "{{shutdown_sequence}}"},
                    "position": [300, 100]
                }
            ]
        }

    def _get_production_report_workflow(self) -> Dict[str, Any]:
        """Get production report workflow definition"""
        return {
            "name": "Production Report Generator",
            "nodes": [
                {
                    "id": "report_timer",
                    "name": "Report Schedule",
                    "type": "timer",
                    "parameters": {"frequency": "{{report_frequency}}"},
                    "position": [100, 100]
                },
                {
                    "id": "collect_kpis",
                    "name": "Collect KPIs",
                    "type": "database_query",
                    "parameters": {"metrics": "{{kpi_metrics}}"},
                    "position": [300, 100]
                }
            ]
        }

    def _get_mes_integration_workflow(self) -> Dict[str, Any]:
        """Get MES integration workflow definition"""
        return {
            "name": "MES Data Integration",
            "nodes": [
                {
                    "id": "sync_timer",
                    "name": "Sync Timer",
                    "type": "timer",
                    "parameters": {"interval": "{{sync_interval}}"},
                    "position": [100, 100]
                },
                {
                    "id": "mes_sync",
                    "name": "MES Synchronization",
                    "type": "api_call",
                    "parameters": {"endpoint": "{{mes_endpoint}}"},
                    "position": [300, 100]
                }
            ]
        }

    # Public methods for template management
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)

    def get_templates_by_category(self, category: TemplateCategory) -> List[WorkflowTemplate]:
        """Get all templates in a category"""
        return [t for t in self.templates.values() if t.category == category]

    def get_templates_by_industry(self, industry: IndustryType) -> List[WorkflowTemplate]:
        """Get all templates for an industry"""
        return [t for t in self.templates.values() if t.industry == industry]

    def get_templates_by_complexity(self, complexity: ComplexityLevel) -> List[WorkflowTemplate]:
        """Get all templates by complexity level"""
        return [t for t in self.templates.values() if t.complexity == complexity]

    def search_templates(self, query: str) -> List[WorkflowTemplate]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for template in self.templates.values():
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)

        return results

    def instantiate_template(self, template_id: str,
                           parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create workflow instance from template with provided parameters"""
        template = self.get_template(template_id)
        if not template:
            return None

        # Start with template workflow definition
        workflow_def = copy.deepcopy(template.workflow_definition)

        # Replace parameter placeholders
        workflow_json = json.dumps(workflow_def)
        for param_name, param_value in parameters.items():
            placeholder = f"{{{{{param_name}}}}}"
            workflow_json = workflow_json.replace(placeholder, str(param_value))

        return json.loads(workflow_json)

    def validate_parameters(self, template_id: str,
                          parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate parameters against template requirements"""
        template = self.get_template(template_id)
        if not template:
            return False, ["Template not found"]

        errors = []

        # Check required parameters
        for param in template.parameters:
            if param.required and param.name not in parameters:
                errors.append(f"Required parameter '{param.name}' is missing")
                continue

            if param.name in parameters:
                value = parameters[param.name]

                # Type validation
                if param.parameter_type == "number":
                    if not isinstance(value, (int, float)):
                        errors.append(f"Parameter '{param.name}' must be a number")
                    elif param.min_value is not None and value < param.min_value:
                        errors.append(f"Parameter '{param.name}' must be >= {param.min_value}")
                    elif param.max_value is not None and value > param.max_value:
                        errors.append(f"Parameter '{param.name}' must be <= {param.max_value}")

                elif param.parameter_type == "boolean":
                    if not isinstance(value, bool):
                        errors.append(f"Parameter '{param.name}' must be a boolean")

                elif param.parameter_type == "select":
                    if param.options and value not in param.options:
                        errors.append(f"Parameter '{param.name}' must be one of: {', '.join(param.options)}")

        return len(errors) == 0, errors

    def get_template_catalog(self) -> Dict[str, Any]:
        """Get complete template catalog with metadata"""
        catalog = {
            "total_templates": len(self.templates),
            "categories": {},
            "industries": {},
            "complexity_levels": {},
            "templates": []
        }

        # Count by category
        for category in TemplateCategory:
            count = len(self.get_templates_by_category(category))
            if count > 0:
                catalog["categories"][category.value] = count

        # Count by industry
        for industry in IndustryType:
            count = len(self.get_templates_by_industry(industry))
            if count > 0:
                catalog["industries"][industry.value] = count

        # Count by complexity
        for complexity in ComplexityLevel:
            count = len(self.get_templates_by_complexity(complexity))
            if count > 0:
                catalog["complexity_levels"][complexity.value] = count

        # Template summaries
        for template in self.templates.values():
            catalog["templates"].append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category.value,
                "industry": template.industry.value,
                "complexity": template.complexity.value,
                "tags": template.tags,
                "parameter_count": len(template.parameters),
                "estimated_setup_time": template.estimated_setup_time
            })

        return catalog

# Testing and example usage
def test_template_library():
    """Test the industrial template library"""
    library = IndustrialTemplateLibrary()

    print("=== Industrial Automation Template Library Test ===\n")

    # Get catalog
    catalog = library.get_template_catalog()
    print(f"Total Templates: {catalog['total_templates']}")
    print(f"Categories: {list(catalog['categories'].keys())}")
    print(f"Industries: {list(catalog['industries'].keys())}")
    print()

    # Test template retrieval
    temp_template = library.get_template("temp_control_basic")
    if temp_template:
        print(f"Template: {temp_template.name}")
        print(f"Description: {temp_template.description}")
        print(f"Parameters: {len(temp_template.parameters)}")
        print()

        # Test parameter validation
        test_params = {
            "loop_name": "TIC_101",
            "pv_tag": "TT_101.PV",
            "sp_tag": "TIC_101.SP",
            "cv_tag": "TIC_101.CV",
            "setpoint_value": 85.0,
            "kp": 1.2,
            "ki": 0.15,
            "kd": 0.0,
            "high_alarm": 95.0,
            "low_alarm": 75.0,
            "alarm_email": "operator@plant.com"
        }

        valid, errors = library.validate_parameters("temp_control_basic", test_params)
        print(f"Parameter Validation: {'✅ PASSED' if valid else '❌ FAILED'}")
        if errors:
            for error in errors:
                print(f"  - {error}")
        print()

        # Test template instantiation
        if valid:
            workflow_instance = library.instantiate_template("temp_control_basic", test_params)
            if workflow_instance:
                print(f"Template Instantiated: {workflow_instance['name']}")
                print(f"Nodes: {len(workflow_instance['nodes'])}")
                print(f"Connections: {len(workflow_instance.get('connections', []))}")

    # Test search
    search_results = library.search_templates("temperature")
    print(f"\nSearch Results for 'temperature': {len(search_results)} templates")
    for result in search_results:
        print(f"  - {result.name} ({result.complexity.value})")

    # Test category filtering
    control_templates = library.get_templates_by_category(TemplateCategory.CONTROL_LOOPS)
    print(f"\nControl Loop Templates: {len(control_templates)}")
    for template in control_templates:
        print(f"  - {template.name}")

if __name__ == "__main__":
    test_template_library()
