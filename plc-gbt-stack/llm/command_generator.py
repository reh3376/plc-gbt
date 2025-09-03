"""
Command Generation Engine
Phase 23.2.2: Natural Language to CLI Command Translation

Provides comprehensive command generation including natural language to CLI translation,
parameter extraction and validation, command sequence planning, and batch operation optimization.
"""

import logging
import re
import shlex
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from . import (
    ApplicationContext,
    EntityType,
    ExtractedEntity,
    IntentRecognitionResult,
    IntentType,
    TaskComplexity,
)

logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Types of CLI commands"""
    SIMPLE = "simple"           # Single command
    COMPOUND = "compound"       # Command with multiple flags
    SEQUENCE = "sequence"       # Multiple commands in order
    BATCH = "batch"            # Multiple parallel commands
    PIPELINE = "pipeline"      # Commands with data flow

class ValidationStatus(Enum):
    """Command validation status"""
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_CONFIRMATION = "needs_confirmation"
    MISSING_PARAMETERS = "missing_parameters"
    UNSAFE = "unsafe"

class ExecutionMode(Enum):
    """Command execution modes"""
    IMMEDIATE = "immediate"     # Execute right away
    PREVIEW = "preview"        # Show command without executing
    INTERACTIVE = "interactive" # Ask for confirmation
    BATCH = "batch"            # Queue for batch execution

@dataclass
class CommandParameter:
    """Individual command parameter"""
    name: str
    value: Any
    required: bool = True
    flag: str = ""
    description: str = ""
    validation_pattern: Optional[str] = None
    default_value: Any = None

@dataclass
class GeneratedCommand:
    """Generated CLI command with metadata"""
    command: str
    intent_type: IntentType
    command_type: CommandType
    parameters: List[CommandParameter] = field(default_factory=list)
    confidence: float = 0.0
    validation_status: ValidationStatus = ValidationStatus.VALID
    explanation: str = ""
    estimated_duration: int = 0  # seconds
    risk_level: str = "low"
    prerequisites: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CommandSequence:
    """Sequence of related commands"""
    commands: List[GeneratedCommand]
    sequence_type: CommandType
    total_duration: int = 0
    dependencies: List[Tuple[int, int]] = field(default_factory=list)  # (command_index, depends_on_index)
    parallel_groups: List[List[int]] = field(default_factory=list)     # Groups that can run in parallel
    explanation: str = ""
    rollback_commands: List[str] = field(default_factory=list)

@dataclass
class CommandGenerationResult:
    """Complete command generation result"""
    primary_command: GeneratedCommand
    alternative_commands: List[GeneratedCommand] = field(default_factory=list)
    command_sequence: Optional[CommandSequence] = None
    execution_mode: ExecutionMode = ExecutionMode.IMMEDIATE
    user_confirmation_required: bool = False
    confirmation_message: Optional[str] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class ParameterExtractor:
    """Extracts and validates command parameters"""

    def __init__(self):
        self.command_templates = {
            "plc-cl create loop": {
                "required": ["name"],
                "optional": ["type", "description", "setpoint", "output_min", "output_max"],
                "flags": {
                    "name": "--name",
                    "type": "--type",
                    "description": "--description",
                    "setpoint": "--setpoint",
                    "output_min": "--output-min",
                    "output_max": "--output-max"
                }
            },
            "plc-cl analyze performance": {
                "required": ["loop"],
                "optional": ["start_time", "end_time", "metrics", "output"],
                "flags": {
                    "loop": "--loop",
                    "start_time": "--start-time",
                    "end_time": "--end-time",
                    "metrics": "--metrics",
                    "output": "--output"
                }
            },
            "plc-cl optimize tuning": {
                "required": ["loop"],
                "optional": ["method", "target", "constraints", "output"],
                "flags": {
                    "loop": "--loop",
                    "method": "--method",
                    "target": "--target",
                    "constraints": "--constraints",
                    "output": "--output"
                }
            },
            "plc-cl validate schema": {
                "required": ["file"],
                "optional": ["schema_type", "strict", "output"],
                "flags": {
                    "file": "--file",
                    "schema_type": "--schema-type",
                    "strict": "--strict",
                    "output": "--output"
                }
            },
            "plc-cl export data": {
                "required": ["format"],
                "optional": ["loop", "start_time", "end_time", "output", "compression"],
                "flags": {
                    "format": "--format",
                    "loop": "--loop",
                    "start_time": "--start-time",
                    "end_time": "--end-time",
                    "output": "--output",
                    "compression": "--compression"
                }
            }
        }

    def extract_parameters(self, base_command: str, entities: Dict[EntityType, List[ExtractedEntity]],
                          context: ApplicationContext) -> List[CommandParameter]:
        """Extract command parameters from entities and context"""
        parameters = []

        if base_command not in self.command_templates:
            return parameters

        template = self.command_templates[base_command]

        # Extract parameters from entities
        entity_mappings = {
            EntityType.LOOP_NAME: ["loop", "name"],
            EntityType.FILE_PATH: ["file", "output"],
            EntityType.OUTPUT_FORMAT: ["format"],
            EntityType.TUNING_METHOD: ["method"],
            EntityType.TIME_PERIOD: ["start_time", "end_time"],
            EntityType.CONTROLLER_TYPE: ["type"],
            EntityType.VALUE: ["setpoint", "output_min", "output_max", "target"]
        }

        for entity_type, param_names in entity_mappings.items():
            if entity_type in entities:
                for entity in entities[entity_type]:
                    for param_name in param_names:
                        if param_name in template["flags"]:
                            param = CommandParameter(
                                name=param_name,
                                value=entity.value,
                                flag=template["flags"][param_name],
                                required=param_name in template["required"],
                                description=f"Extracted from {entity_type.value}"
                            )
                            parameters.append(param)
                            break  # Use first matching parameter

        # Fill in context-based parameters
        self._add_context_parameters(base_command, parameters, context, template)

        # Add default parameters for missing required ones
        self._add_default_parameters(parameters, template, context)

        return parameters

    def _add_context_parameters(self, base_command: str, parameters: List[CommandParameter],
                               context: ApplicationContext, template: Dict):
        """Add parameters based on application context"""
        existing_param_names = {p.name for p in parameters}

        # Add loop name from active schemas if not specified
        if "loop" in template["flags"] and "loop" not in existing_param_names:
            if len(context.active_schemas) == 1:
                param = CommandParameter(
                    name="loop",
                    value=context.active_schemas[0],
                    flag=template["flags"]["loop"],
                    required="loop" in template["required"],
                    description="Inferred from active schemas"
                )
                parameters.append(param)

        # Add output format based on user preferences
        if "format" in template["flags"] and "format" not in existing_param_names:
            preferred_format = context.user_preferences.get("output_format", "json")
            param = CommandParameter(
                name="format",
                value=preferred_format,
                flag=template["flags"]["format"],
                required="format" in template["required"],
                description="From user preferences"
            )
            parameters.append(param)

        # Add output file based on command type
        if "output" in template["flags"] and "output" not in existing_param_names:
            if "export" in base_command:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"export_{timestamp}.json"
                param = CommandParameter(
                    name="output",
                    value=output_file,
                    flag=template["flags"]["output"],
                    required=False,
                    description="Auto-generated output filename"
                )
                parameters.append(param)

    def _add_default_parameters(self, parameters: List[CommandParameter],
                               template: Dict, context: ApplicationContext):
        """Add default values for missing required parameters"""
        existing_param_names = {p.name for p in parameters}

        defaults = {
            "type": "pid",
            "method": "ziegler-nichols",
            "schema_type": "control_loop",
            "format": "json",
            "target": "optimization"
        }

        for required_param in template["required"]:
            if required_param not in existing_param_names and required_param in defaults:
                param = CommandParameter(
                    name=required_param,
                    value=defaults[required_param],
                    flag=template["flags"][required_param],
                    required=True,
                    description=f"Default value for {required_param}"
                )
                parameters.append(param)

class CommandBuilder:
    """Builds CLI commands from intents and parameters"""

    def __init__(self):
        self.parameter_extractor = ParameterExtractor()

        # Intent to command mappings
        self.intent_command_map = {
            IntentType.CREATE: [
                "plc-cl create loop",
                "plc-cl create schema",
                "plc-cl create instance"
            ],
            IntentType.ANALYZE: [
                "plc-cl analyze performance",
                "plc-cl analyze stability",
                "plc-cl analyze data"
            ],
            IntentType.OPTIMIZE: [
                "plc-cl optimize tuning",
                "plc-cl optimize performance",
                "plc-cl optimize parameters"
            ],
            IntentType.QUERY: [
                "plc-cl list loops",
                "plc-cl show status",
                "plc-cl get info"
            ],
            IntentType.VALIDATE: [
                "plc-cl validate schema",
                "plc-cl validate config",
                "plc-cl test connection"
            ],
            IntentType.MODIFY: [
                "plc-cl update loop",
                "plc-cl modify parameters",
                "plc-cl configure settings"
            ],
            IntentType.DELETE: [
                "plc-cl delete loop",
                "plc-cl remove instance",
                "plc-cl clean data"
            ],
            IntentType.HELP: [
                "plc-cl --help",
                "plc-cl help",
                "plc-cl docs"
            ],
            IntentType.CONFIGURE: [
                "plc-cl configure",
                "plc-cl setup",
                "plc-cl init"
            ]
        }

    def build_command(self, intent_result: IntentRecognitionResult,
                     context: ApplicationContext) -> GeneratedCommand:
        """Build a CLI command from intent recognition result"""
        intent_type = intent_result.primary_intent.intent_type
        entities = intent_result.entities

        # Select best command for intent
        base_command = self._select_base_command(intent_type, entities, context)

        # Extract parameters
        parameters = self.parameter_extractor.extract_parameters(base_command, entities, context)

        # Build full command
        full_command = self._build_full_command(base_command, parameters)

        # Validate command
        validation_status = self._validate_command(full_command, parameters, context)

        # Calculate confidence
        confidence = self._calculate_command_confidence(intent_result, parameters, validation_status)

        # Generate explanation
        explanation = self._generate_explanation(base_command, parameters, intent_type)

        # Determine command type
        command_type = self._determine_command_type(full_command, parameters)

        return GeneratedCommand(
            command=full_command,
            intent_type=intent_type,
            command_type=command_type,
            parameters=parameters,
            confidence=confidence,
            validation_status=validation_status,
            explanation=explanation,
            estimated_duration=self._estimate_duration(base_command),
            risk_level=self._assess_risk_level(base_command, parameters),
            alternatives=self._generate_alternatives(intent_type, entities, context)
        )

    def _select_base_command(self, intent_type: IntentType, entities: Dict,
                           context: ApplicationContext) -> str:
        """Select the most appropriate base command for the intent"""
        if intent_type not in self.intent_command_map:
            return "plc-cl --help"

        possible_commands = self.intent_command_map[intent_type]

        # Entity-based command selection
        if EntityType.LOOP_NAME in entities:
            # Prefer loop-specific commands
            loop_commands = [cmd for cmd in possible_commands if "loop" in cmd]
            if loop_commands:
                return loop_commands[0]

        if EntityType.FILE_PATH in entities:
            # Prefer file-based commands
            file_commands = [cmd for cmd in possible_commands if any(word in cmd for word in ["validate", "import", "export"])]
            if file_commands:
                return file_commands[0]

        if EntityType.TUNING_METHOD in entities:
            # Prefer tuning/optimization commands
            tuning_commands = [cmd for cmd in possible_commands if any(word in cmd for word in ["optimize", "tuning"])]
            if tuning_commands:
                return tuning_commands[0]

        # Default to first available command
        return possible_commands[0]

    def _build_full_command(self, base_command: str, parameters: List[CommandParameter]) -> str:
        """Build the complete command string"""
        command_parts = [base_command]

        for param in parameters:
            if param.flag and param.value is not None:
                # Handle boolean flags
                if isinstance(param.value, bool):
                    if param.value:
                        command_parts.append(param.flag)
                else:
                    # Quote values that might contain spaces
                    value_str = str(param.value)
                    if ' ' in value_str or '"' in value_str:
                        value_str = shlex.quote(value_str)
                    command_parts.extend([param.flag, value_str])

        return ' '.join(command_parts)

    def _validate_command(self, command: str, parameters: List[CommandParameter],
                         context: ApplicationContext) -> ValidationStatus:
        """Validate the generated command"""
        # Check for required parameters
        required_params = [p for p in parameters if p.required and p.value is None]
        if required_params:
            return ValidationStatus.MISSING_PARAMETERS

        # Check for dangerous operations
        dangerous_patterns = ['delete', 'remove', 'clean', 'reset', 'format']
        if any(pattern in command.lower() for pattern in dangerous_patterns):
            return ValidationStatus.NEEDS_CONFIRMATION

        # Validate parameter patterns
        for param in parameters:
            if param.validation_pattern and param.value:
                if not re.match(param.validation_pattern, str(param.value)):
                    return ValidationStatus.INVALID

        # Check if target files/loops exist
        if "--file" in command:
            file_params = [p for p in parameters if p.name == "file"]
            for _file_param in file_params:
                # In real implementation, check if file exists
                pass

        return ValidationStatus.VALID

    def _calculate_command_confidence(self, intent_result: IntentRecognitionResult,
                                    parameters: List[CommandParameter],
                                    validation_status: ValidationStatus) -> float:
        """Calculate confidence in the generated command"""
        base_confidence = intent_result.primary_intent.confidence

        # Adjust based on validation status
        validation_adjustments = {
            ValidationStatus.VALID: 0.0,
            ValidationStatus.NEEDS_CONFIRMATION: -0.1,
            ValidationStatus.MISSING_PARAMETERS: -0.3,
            ValidationStatus.INVALID: -0.5,
            ValidationStatus.UNSAFE: -0.7
        }

        base_confidence += validation_adjustments.get(validation_status, 0)

        # Adjust based on parameter completeness
        required_params = [p for p in parameters if p.required]
        filled_params = [p for p in required_params if p.value is not None]

        if required_params:
            completeness_bonus = (len(filled_params) / len(required_params)) * 0.2
            base_confidence += completeness_bonus

        return min(1.0, max(0.0, base_confidence))

    def _generate_explanation(self, base_command: str, parameters: List[CommandParameter],
                            intent_type: IntentType) -> str:
        """Generate human-readable explanation of the command"""
        action_descriptions = {
            "create": "creates a new",
            "analyze": "analyzes the",
            "optimize": "optimizes the",
            "validate": "validates the",
            "list": "lists all",
            "show": "displays information about",
            "delete": "removes the",
            "update": "modifies the",
            "export": "exports data from"
        }

        # Extract action from command
        action = None
        for cmd_action in action_descriptions.keys():
            if cmd_action in base_command:
                action = cmd_action
                break

        if not action:
            return f"This command executes: {base_command}"

        # Build explanation
        explanation = f"This command {action_descriptions[action]}"

        # Add target information
        loop_params = [p for p in parameters if p.name in ["loop", "name"]]
        if loop_params:
            explanation += f" '{loop_params[0].value}'"

        # Add object type
        if "loop" in base_command:
            explanation += " control loop"
        elif "schema" in base_command:
            explanation += " schema"
        elif "data" in base_command:
            explanation += " data"

        # Add additional details
        details = []
        for param in parameters[:3]:  # First 3 parameters
            if param.name not in ["loop", "name"] and param.value:
                details.append(f"{param.name}: {param.value}")

        if details:
            explanation += f" with {', '.join(details)}"

        return explanation

    def _determine_command_type(self, command: str, parameters: List[CommandParameter]) -> CommandType:
        """Determine the type of command"""
        if len(parameters) <= 2:
            return CommandType.SIMPLE
        elif any(param.name in ["batch", "multiple", "all"] for param in parameters):
            return CommandType.BATCH
        elif len(parameters) > 5:
            return CommandType.COMPOUND
        else:
            return CommandType.COMPOUND

    def _estimate_duration(self, base_command: str) -> int:
        """Estimate command execution duration in seconds"""
        duration_estimates = {
            "create": 5,
            "analyze": 30,
            "optimize": 120,
            "validate": 10,
            "list": 2,
            "show": 2,
            "delete": 3,
            "update": 10,
            "export": 60
        }

        for action, duration in duration_estimates.items():
            if action in base_command:
                return duration

        return 10  # Default

    def _assess_risk_level(self, base_command: str, parameters: List[CommandParameter]) -> str:
        """Assess risk level of command"""
        high_risk_actions = ["delete", "remove", "clean", "reset", "format"]
        medium_risk_actions = ["modify", "update", "configure"]

        command_lower = base_command.lower()

        if any(action in command_lower for action in high_risk_actions):
            return "high"
        elif any(action in command_lower for action in medium_risk_actions):
            return "medium"
        else:
            return "low"

    def _generate_alternatives(self, intent_type: IntentType, entities: Dict,
                             context: ApplicationContext) -> List[str]:
        """Generate alternative command options"""
        alternatives = []

        if intent_type in self.intent_command_map:
            all_commands = self.intent_command_map[intent_type]
            alternatives.extend(all_commands[1:3])  # Up to 2 alternatives

        return alternatives

class SequencePlanner:
    """Plans command sequences for complex tasks"""

    def plan_sequence(self, intent_result: IntentRecognitionResult,
                     context: ApplicationContext) -> Optional[CommandSequence]:
        """Plan a sequence of commands for complex intents"""
        intent = intent_result.primary_intent

        if intent.complexity == TaskComplexity.SIMPLE:
            return None  # Single command is sufficient

        # Multi-step task planning
        if intent.intent_type == IntentType.CREATE and EntityType.LOOP_NAME in intent_result.entities:
            return self._plan_create_loop_sequence(intent_result, context)
        elif intent.intent_type == IntentType.OPTIMIZE:
            return self._plan_optimization_sequence(intent_result, context)
        elif intent.intent_type == IntentType.ANALYZE:
            return self._plan_analysis_sequence(intent_result, context)

        return None

    def _plan_create_loop_sequence(self, intent_result: IntentRecognitionResult,
                                  context: ApplicationContext) -> CommandSequence:
        """Plan sequence for creating a control loop"""
        builder = CommandBuilder()
        commands = []

        # Step 1: Create the loop
        create_cmd = builder.build_command(intent_result, context)
        commands.append(create_cmd)

        # Step 2: Validate the created loop
        validate_intent = intent_result
        validate_intent.primary_intent.intent_type = IntentType.VALIDATE
        validate_cmd = builder.build_command(validate_intent, context)
        commands.append(validate_cmd)

        # Step 3: Analyze initial performance
        analyze_intent = intent_result
        analyze_intent.primary_intent.intent_type = IntentType.ANALYZE
        analyze_cmd = builder.build_command(analyze_intent, context)
        commands.append(analyze_cmd)

        return CommandSequence(
            commands=commands,
            sequence_type=CommandType.SEQUENCE,
            total_duration=sum(cmd.estimated_duration for cmd in commands),
            dependencies=[(1, 0), (2, 1)],  # Each step depends on previous
            explanation="Complete loop creation workflow: create → validate → analyze"
        )

    def _plan_optimization_sequence(self, intent_result: IntentRecognitionResult,
                                   context: ApplicationContext) -> CommandSequence:
        """Plan sequence for optimization tasks"""
        builder = CommandBuilder()
        commands = []

        # Step 1: Analyze current performance
        analyze_intent = intent_result
        analyze_intent.primary_intent.intent_type = IntentType.ANALYZE
        analyze_cmd = builder.build_command(analyze_intent, context)
        commands.append(analyze_cmd)

        # Step 2: Run optimization
        optimize_cmd = builder.build_command(intent_result, context)
        commands.append(optimize_cmd)

        # Step 3: Validate optimized parameters
        validate_intent = intent_result
        validate_intent.primary_intent.intent_type = IntentType.VALIDATE
        validate_cmd = builder.build_command(validate_intent, context)
        commands.append(validate_cmd)

        return CommandSequence(
            commands=commands,
            sequence_type=CommandType.SEQUENCE,
            total_duration=sum(cmd.estimated_duration for cmd in commands),
            dependencies=[(1, 0), (2, 1)],
            explanation="Optimization workflow: analyze → optimize → validate"
        )

    def _plan_analysis_sequence(self, intent_result: IntentRecognitionResult,
                               context: ApplicationContext) -> CommandSequence:
        """Plan sequence for comprehensive analysis"""
        builder = CommandBuilder()
        commands = []

        # Multiple analysis commands that can run in parallel
        analysis_types = ["performance", "stability", "efficiency"]

        for analysis_type in analysis_types:
            # Modify intent for each analysis type
            modified_intent = intent_result
            # In real implementation, would modify parameters for specific analysis
            cmd = builder.build_command(modified_intent, context)
            cmd.explanation = f"Analyze {analysis_type}"
            commands.append(cmd)

        return CommandSequence(
            commands=commands,
            sequence_type=CommandType.BATCH,
            total_duration=max(cmd.estimated_duration for cmd in commands),  # Parallel execution
            parallel_groups=[[0, 1, 2]],  # All can run in parallel
            explanation="Comprehensive analysis: performance, stability, and efficiency in parallel"
        )

class CommandGenerator:
    """Main command generation orchestrator"""

    def __init__(self):
        self.command_builder = CommandBuilder()
        self.sequence_planner = SequencePlanner()
        self.generation_history: List[CommandGenerationResult] = []

    def generate_command(self, intent_result: IntentRecognitionResult,
                        context: ApplicationContext) -> CommandGenerationResult:
        """Generate complete command(s) from intent recognition result"""
        start_time = time.time()

        # Generate primary command
        primary_command = self.command_builder.build_command(intent_result, context)

        # Generate alternative commands
        alternative_commands = self._generate_alternatives(intent_result, context)

        # Plan command sequence if needed
        command_sequence = self.sequence_planner.plan_sequence(intent_result, context)

        # Determine execution mode
        execution_mode = self._determine_execution_mode(primary_command, command_sequence)

        # Check if confirmation is required
        confirmation_required = self._requires_confirmation(primary_command, command_sequence)
        confirmation_message = None
        if confirmation_required:
            confirmation_message = self._generate_confirmation_message(primary_command, command_sequence)

        # Create result
        result = CommandGenerationResult(
            primary_command=primary_command,
            alternative_commands=alternative_commands,
            command_sequence=command_sequence,
            execution_mode=execution_mode,
            user_confirmation_required=confirmation_required,
            confirmation_message=confirmation_message,
            processing_time=time.time() - start_time,
            metadata={
                "intent_confidence": intent_result.primary_intent.confidence,
                "num_alternatives": len(alternative_commands),
                "has_sequence": command_sequence is not None
            }
        )

        # Store in history
        self.generation_history.append(result)
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-100:]

        return result

    def _generate_alternatives(self, intent_result: IntentRecognitionResult,
                             context: ApplicationContext) -> List[GeneratedCommand]:
        """Generate alternative command options"""
        alternatives = []

        # Use alternative intents if available
        for alt_intent in intent_result.alternative_intents[:2]:
            modified_result = intent_result
            modified_result.primary_intent = alt_intent
            alt_command = self.command_builder.build_command(modified_result, context)
            alternatives.append(alt_command)

        return alternatives

    def _determine_execution_mode(self, primary_command: GeneratedCommand,
                                 sequence: Optional[CommandSequence]) -> ExecutionMode:
        """Determine appropriate execution mode"""
        if primary_command.risk_level == "high" or primary_command.validation_status == ValidationStatus.NEEDS_CONFIRMATION:
            return ExecutionMode.INTERACTIVE
        elif sequence and len(sequence.commands) > 3:
            return ExecutionMode.BATCH
        elif primary_command.confidence < 0.7:
            return ExecutionMode.PREVIEW
        else:
            return ExecutionMode.IMMEDIATE

    def _requires_confirmation(self, primary_command: GeneratedCommand,
                             sequence: Optional[CommandSequence]) -> bool:
        """Check if user confirmation is required"""
        return (
            primary_command.risk_level in ["medium", "high"] or
            primary_command.validation_status == ValidationStatus.NEEDS_CONFIRMATION or
            (sequence and any(cmd.risk_level == "high" for cmd in sequence.commands))
        )

    def _generate_confirmation_message(self, primary_command: GeneratedCommand,
                                     sequence: Optional[CommandSequence]) -> str:
        """Generate confirmation message for risky operations"""
        if sequence:
            return f"⚠️ This will execute {len(sequence.commands)} commands:\n" + \
                   "\n".join(f"  {i+1}. {cmd.command}" for i, cmd in enumerate(sequence.commands[:3])) + \
                   f"\nEstimated duration: {sequence.total_duration} seconds. Continue?"
        else:
            return f"⚠️ About to execute: {primary_command.command}\n" + \
                   f"Risk level: {primary_command.risk_level}\n" + \
                   f"This will {primary_command.explanation}. Continue?"

# Singleton generator instance
_command_generator: Optional[CommandGenerator] = None

def get_command_generator() -> CommandGenerator:
    """Get singleton command generator"""
    global _command_generator
    if _command_generator is None:
        _command_generator = CommandGenerator()
    return _command_generator

def generate_command(intent_result: IntentRecognitionResult,
                    context: ApplicationContext) -> CommandGenerationResult:
    """Quick function to generate commands"""
    generator = get_command_generator()
    return generator.generate_command(intent_result, context)

# Export main components
__all__ = [
    "CommandType",
    "ValidationStatus",
    "ExecutionMode",
    "CommandParameter",
    "GeneratedCommand",
    "CommandSequence",
    "CommandGenerationResult",
    "ParameterExtractor",
    "CommandBuilder",
    "SequencePlanner",
    "CommandGenerator",
    "get_command_generator",
    "generate_command"
]
