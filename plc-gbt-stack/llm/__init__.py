"""
PLC-GBT Fine-tuned LLM Integration Package
Phase 23: Fine-tuned LLM Application Integration

This package provides comprehensive integration with the fine-tuned Industrial Control Theory LLM
(ft:gpt-4o:industrial-control:20250117) for natural language application control.

Core capabilities:
- Natural language to action mapping
- Context-aware conversation management
- Task planning and execution
- Safety validation and error recovery
- Intelligent assistance and learning
"""

__version__ = "23.1.0"
__author__ = "PLC-GBT Development Team"
__description__ = "Fine-tuned LLM Integration for Industrial Control Systems"

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import os
import json
import logging
from datetime import datetime, timezone

# Configure logging for LLM operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM Integration Configuration
LLM_CONFIG = {
    "version": __version__,
    "model_id": "ft:gpt-4o:industrial-control:20250117",
    "base_model": "gpt-4o",
    "specialization": "industrial_control_theory",
    "max_tokens": 8192,
    "temperature": 0.1,  # Low temperature for precision
    "top_p": 0.95,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "request_timeout": 60,
    "max_retries": 3,
    "backoff_factor": 2.0,
    "rate_limits": {
        "requests_per_minute": 3500,
        "tokens_per_minute": 90000,
        "requests_per_day": 100000
    },
    "context_settings": {
        "max_context_length": 6000,
        "context_compression_threshold": 8000,
        "conversation_memory_turns": 10,
        "system_context_priority": "high"
    },
    "safety_settings": {
        "destructive_operation_confirmation": True,
        "hallucination_detection": True,
        "command_validation": True,
        "max_execution_time": 300,
        "allowed_cli_commands": [],  # Populated dynamically
        "restricted_operations": ["delete", "rm", "format", "reset"]
    }
}

class LLMRequestType(Enum):
    """Types of LLM requests"""
    CHAT = "chat"
    COMMAND_GENERATION = "command_generation"
    ANALYSIS = "analysis"
    EXPLANATION = "explanation"
    TASK_PLANNING = "task_planning"
    VALIDATION = "validation"
    LEARNING = "learning"

class LLMResponseStatus(Enum):
    """Status of LLM responses"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    VALIDATION_FAILED = "validation_failed"
    SAFETY_BLOCKED = "safety_blocked"

class ConversationRole(Enum):
    """Roles in LLM conversations"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class IntentType(Enum):
    """Types of user intents"""
    CREATE = "create"
    MODIFY = "modify"
    ANALYZE = "analyze"
    DELETE = "delete"
    QUERY = "query"
    OPTIMIZE = "optimize"
    VALIDATE = "validate"
    EXPLAIN = "explain"
    HELP = "help"
    CONFIGURE = "configure"

class TaskComplexity(Enum):
    """Complexity levels for task planning"""
    SIMPLE = "simple"           # Single command execution
    MODERATE = "moderate"       # Multiple related commands
    COMPLEX = "complex"         # Multi-step workflow
    EXPERT = "expert"          # Advanced optimization/analysis

@dataclass
class ConversationMessage:
    """Individual message in LLM conversation"""
    role: ConversationRole
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    function_call: Optional[Dict[str, Any]] = None
    function_response: Optional[str] = None

@dataclass
class LLMRequest:
    """LLM request configuration"""
    request_type: LLMRequestType
    messages: List[ConversationMessage]
    context: Dict[str, Any] = field(default_factory=dict)
    model_override: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    safety_checks: bool = True
    validate_response: bool = True

@dataclass
class LLMResponse:
    """LLM response with metadata"""
    status: LLMResponseStatus
    content: str
    request_id: str
    model_used: str
    usage: Dict[str, int] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    safety_checks: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0

@dataclass
class ApplicationContext:
    """Current application context for LLM"""
    current_directory: str
    available_commands: List[str]
    active_schemas: List[str]
    recent_operations: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    user_preferences: Dict[str, Any]
    session_history: List[ConversationMessage]
    error_history: List[Dict[str, Any]]
    system_state: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Intent:
    """Recognized user intent"""
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    context_required: List[str] = field(default_factory=list)
    complexity: TaskComplexity = TaskComplexity.SIMPLE
    estimated_steps: int = 1

@dataclass
class TaskPlan:
    """Planned task execution"""
    intent: Intent
    steps: List[Dict[str, Any]]
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: int = 0  # seconds
    risk_level: str = "low"
    validation_required: bool = False
    confirmation_required: bool = False
    resources_needed: List[str] = field(default_factory=list)

@dataclass
class ExecutionResult:
    """Result of task execution"""
    task_plan: TaskPlan
    status: str
    results: List[Dict[str, Any]]
    execution_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    performance_impact: Dict[str, Any] = field(default_factory=dict)

# Utility functions for LLM integration
def get_model_info() -> Dict[str, Any]:
    """Get information about the fine-tuned model"""
    return {
        "model_id": LLM_CONFIG["model_id"],
        "base_model": LLM_CONFIG["base_model"],
        "specialization": LLM_CONFIG["specialization"],
        "version": __version__,
        "capabilities": [
            "Industrial control theory expertise",
            "PID tuning optimization",
            "CLI command generation",
            "Natural language understanding",
            "Task planning and execution",
            "Safety validation",
            "Educational explanations"
        ]
    }

def create_system_message(context: ApplicationContext) -> ConversationMessage:
    """Create system message with current application context"""
    system_content = f"""You are an expert Industrial Control Theory assistant with specialized knowledge in:
- PID control systems and tuning strategies
- Industrial automation and PLC programming
- The PLC-GBT application CLI and schemas
- Control loop optimization and analysis

Current Context:
- Working Directory: {context.current_directory}
- Available Commands: {len(context.available_commands)} commands
- Active Schemas: {context.active_schemas}
- System State: {context.system_state.get('status', 'ready')}

Guidelines:
1. Always validate commands before suggesting execution
2. Explain the reasoning behind recommendations
3. Consider safety implications of all actions
4. Provide educational context when appropriate
5. Ask for clarification when intent is ambiguous

You can execute CLI commands, analyze control systems, and provide expert guidance on industrial control theory."""

    return ConversationMessage(
        role=ConversationRole.SYSTEM,
        content=system_content,
        metadata={"context_version": context.system_state.get("version", "unknown")}
    )

def validate_llm_response(response: str, request_type: LLMRequestType) -> Dict[str, Any]:
    """Validate LLM response based on request type"""
    validation_results = {
        "is_valid": True,
        "issues": [],
        "confidence": 1.0,
        "safety_score": 1.0
    }
    
    if not response or len(response.strip()) == 0:
        validation_results["is_valid"] = False
        validation_results["issues"].append("Empty response")
        return validation_results
    
    # Request-type specific validation
    if request_type == LLMRequestType.COMMAND_GENERATION:
        # Check if response contains valid CLI commands
        if "plc-cl" not in response and "python" not in response:
            validation_results["confidence"] *= 0.8
            validation_results["issues"].append("Response may not contain valid commands")
    
    elif request_type == LLMRequestType.ANALYSIS:
        # Check if response contains analytical content
        analysis_keywords = ["analysis", "performance", "tuning", "optimization", "recommendation"]
        if not any(keyword in response.lower() for keyword in analysis_keywords):
            validation_results["confidence"] *= 0.7
            validation_results["issues"].append("Response may lack analytical content")
    
    # Safety checks
    dangerous_patterns = ["rm -rf", "delete all", "format", "reset everything"]
    for pattern in dangerous_patterns:
        if pattern.lower() in response.lower():
            validation_results["safety_score"] *= 0.3
            validation_results["issues"].append(f"Potentially dangerous operation detected: {pattern}")
    
    return validation_results

def estimate_token_count(text: str) -> int:
    """Estimate token count for text (rough approximation)"""
    # Rough estimation: ~4 characters per token for English text
    return len(text) // 4

def optimize_context_for_model(context: ApplicationContext, max_tokens: int = 6000) -> ApplicationContext:
    """Optimize context to fit within token limits"""
    optimized_context = context
    
    # Prioritize recent operations and current state
    if len(context.recent_operations) > 10:
        optimized_context.recent_operations = context.recent_operations[-10:]
    
    if len(context.session_history) > 10:
        optimized_context.session_history = context.session_history[-10:]
    
    if len(context.error_history) > 5:
        optimized_context.error_history = context.error_history[-5:]
    
    return optimized_context

# Import additional classes for Phase 23.2/23.3 integration
from .intent_recognition import ExtractedEntity, EntityType, IntentRecognitionResult
from .command_generator import CommandGenerationResult

# Export main components
__all__ = [
    "LLM_CONFIG",
    "LLMRequestType",
    "LLMResponseStatus", 
    "ConversationRole",
    "IntentType",
    "TaskComplexity",
    "ConversationMessage",
    "LLMRequest",
    "LLMResponse",
    "ApplicationContext",
    "Intent",
    "TaskPlan",
    "ExecutionResult",
    "ExtractedEntity",
    "EntityType", 
    "IntentRecognitionResult",
    "CommandGenerationResult",
    "get_model_info",
    "create_system_message",
    "validate_llm_response",
    "estimate_token_count",
    "optimize_context_for_model"
] 