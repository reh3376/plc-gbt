"""
Conversation Management System
Phase 23.2.3: Multi-turn Conversation Support

Provides comprehensive conversation management including multi-turn support,
context preservation across turns, clarification request generation, and task progress tracking.
"""

import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from . import (
    ConversationMessage, ConversationRole, ApplicationContext,
    IntentRecognitionResult, CommandGenerationResult, LLMResponse
)

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """States of conversation flow"""
    ACTIVE = "active"               # Normal conversation
    WAITING_CLARIFICATION = "waiting_clarification"  # Waiting for user clarification
    WAITING_CONFIRMATION = "waiting_confirmation"    # Waiting for user confirmation
    EXECUTING_TASK = "executing_task"                # Task in progress
    COMPLETED = "completed"         # Task completed successfully
    ERROR = "error"                # Error state
    PAUSED = "paused"              # Conversation paused

class TaskStatus(Enum):
    """Status of tasks within conversation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_INPUT = "waiting_input"

class ConversationTopic(Enum):
    """Topics/domains of conversation"""
    CONTROL_LOOP_MANAGEMENT = "control_loop_management"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SYSTEM_OPTIMIZATION = "system_optimization"
    TROUBLESHOOTING = "troubleshooting"
    CONFIGURATION = "configuration"
    LEARNING = "learning"
    GENERAL_HELP = "general_help"

@dataclass
class ConversationTask:
    """Individual task within a conversation"""
    task_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    intent_result: Optional[IntentRecognitionResult] = None
    command_result: Optional[CommandGenerationResult] = None
    execution_result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress_percentage: int = 0
    subtasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ClarificationRequest:
    """Request for clarification from user"""
    request_id: str
    question: str
    context: str
    options: List[str] = field(default_factory=list)
    required: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationContext:
    """Context maintained across conversation turns"""
    topic: ConversationTopic
    user_goals: List[str] = field(default_factory=list)
    active_entities: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[ConversationMessage] = field(default_factory=list)
    task_history: List[ConversationTask] = field(default_factory=list)
    clarification_history: List[ClarificationRequest] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ConversationTurn:
    """Individual turn in conversation"""
    turn_id: str
    user_input: str
    assistant_response: str
    intent_result: Optional[IntentRecognitionResult] = None
    command_result: Optional[CommandGenerationResult] = None
    clarification_request: Optional[ClarificationRequest] = None
    task_updates: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationSession:
    """Complete conversation session"""
    session_id: str
    user_id: str
    state: ConversationState = ConversationState.ACTIVE
    context: ConversationContext = field(default_factory=lambda: ConversationContext(topic=ConversationTopic.GENERAL_HELP))
    turns: List[ConversationTurn] = field(default_factory=list)
    active_tasks: List[ConversationTask] = field(default_factory=list)
    pending_clarifications: List[ClarificationRequest] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_minutes: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContextManager:
    """Manages conversation context and memory"""
    
    def __init__(self, max_history_turns: int = 20):
        self.max_history_turns = max_history_turns
    
    def update_context(self, context: ConversationContext, 
                      new_turn: ConversationTurn, 
                      app_context: ApplicationContext) -> ConversationContext:
        """Update conversation context with new turn"""
        # Add new turn to history
        context.conversation_history.extend([
            ConversationMessage(
                role=ConversationRole.USER,
                content=new_turn.user_input,
                timestamp=new_turn.timestamp
            ),
            ConversationMessage(
                role=ConversationRole.ASSISTANT,
                content=new_turn.assistant_response,
                timestamp=new_turn.timestamp
            )
        ])
        
        # Trim history if too long
        if len(context.conversation_history) > self.max_history_turns * 2:
            context.conversation_history = context.conversation_history[-self.max_history_turns * 2:]
        
        # Update active entities from intent result
        if new_turn.intent_result:
            self._update_entities_from_intent(context, new_turn.intent_result)
        
        # Update topic classification
        context.topic = self._classify_conversation_topic(context)
        
        # Update user preferences
        self._extract_user_preferences(context, new_turn)
        
        # Update goals if mentioned
        self._extract_user_goals(context, new_turn)
        
        context.last_updated = datetime.now(timezone.utc)
        return context
    
    def _update_entities_from_intent(self, context: ConversationContext, 
                                   intent_result: IntentRecognitionResult):
        """Update active entities from intent recognition"""
        for entity_type, entities in intent_result.entities.items():
            for entity in entities:
                key = f"{entity_type.value}_{entity.value}"
                context.active_entities[key] = {
                    "type": entity_type.value,
                    "value": entity.value,
                    "confidence": entity.confidence,
                    "last_mentioned": datetime.now(timezone.utc).isoformat(),
                    "mention_count": context.active_entities.get(key, {}).get("mention_count", 0) + 1
                }
    
    def _classify_conversation_topic(self, context: ConversationContext) -> ConversationTopic:
        """Classify the main topic of conversation"""
        recent_messages = context.conversation_history[-10:]  # Last 10 messages
        
        topic_keywords = {
            ConversationTopic.CONTROL_LOOP_MANAGEMENT: [
                "loop", "controller", "pid", "create", "modify", "configure"
            ],
            ConversationTopic.PERFORMANCE_ANALYSIS: [
                "performance", "analyze", "metrics", "efficiency", "stability"
            ],
            ConversationTopic.SYSTEM_OPTIMIZATION: [
                "optimize", "tuning", "improve", "enhance", "better"
            ],
            ConversationTopic.TROUBLESHOOTING: [
                "problem", "issue", "error", "fix", "debug", "troubleshoot"
            ],
            ConversationTopic.CONFIGURATION: [
                "configure", "setup", "settings", "parameters", "options"
            ],
            ConversationTopic.LEARNING: [
                "how", "what", "why", "explain", "learn", "understand", "help"
            ]
        }
        
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = 0
            for message in recent_messages:
                content_lower = message.content.lower()
                for keyword in keywords:
                    score += content_lower.count(keyword)
            topic_scores[topic] = score
        
        # Return topic with highest score, or current topic if tied
        max_score = max(topic_scores.values()) if topic_scores.values() else 0
        if max_score == 0:
            return context.topic
        
        return max(topic_scores.items(), key=lambda x: x[1])[0]
    
    def _extract_user_preferences(self, context: ConversationContext, turn: ConversationTurn):
        """Extract user preferences from conversation"""
        user_input_lower = turn.user_input.lower()
        
        # Output format preferences
        if "prefer" in user_input_lower:
            if "json" in user_input_lower:
                context.user_preferences["output_format"] = "json"
            elif "csv" in user_input_lower:
                context.user_preferences["output_format"] = "csv"
            elif "detailed" in user_input_lower:
                context.user_preferences["explanation_level"] = "detailed"
            elif "simple" in user_input_lower:
                context.user_preferences["explanation_level"] = "simple"
        
        # Confirmation preferences
        if "always ask" in user_input_lower or "confirm" in user_input_lower:
            context.user_preferences["require_confirmation"] = True
        elif "don't ask" in user_input_lower or "auto" in user_input_lower:
            context.user_preferences["require_confirmation"] = False
    
    def _extract_user_goals(self, context: ConversationContext, turn: ConversationTurn):
        """Extract user goals from conversation"""
        goal_patterns = [
            r"i want to (.+)",
            r"i need to (.+)",
            r"my goal is to (.+)",
            r"i'm trying to (.+)",
            r"help me (.+)"
        ]
        
        import re
        user_input_lower = turn.user_input.lower()
        
        for pattern in goal_patterns:
            matches = re.findall(pattern, user_input_lower)
            for match in matches:
                goal = match.strip()
                if goal not in context.user_goals and len(goal) > 5:
                    context.user_goals.append(goal)
        
        # Limit to 5 most recent goals
        context.user_goals = context.user_goals[-5:]

class TaskTracker:
    """Tracks and manages conversation tasks"""
    
    def create_task(self, description: str, intent_result: IntentRecognitionResult) -> ConversationTask:
        """Create a new conversation task"""
        return ConversationTask(
            task_id=str(uuid.uuid4()),
            description=description,
            intent_result=intent_result,
            metadata={
                "intent_type": intent_result.primary_intent.intent_type.value,
                "confidence": intent_result.primary_intent.confidence,
                "requires_clarification": intent_result.requires_clarification
            }
        )
    
    def update_task_status(self, task: ConversationTask, new_status: TaskStatus, 
                          progress: Optional[int] = None, error_message: Optional[str] = None):
        """Update task status and progress"""
        old_status = task.status
        task.status = new_status
        
        if progress is not None:
            task.progress_percentage = min(100, max(0, progress))
        
        if error_message:
            task.error_message = error_message
        
        # Update timestamps
        if new_status == TaskStatus.IN_PROGRESS and old_status == TaskStatus.PENDING:
            task.started_at = datetime.now(timezone.utc)
        elif new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task.completed_at = datetime.now(timezone.utc)
    
    def decompose_complex_task(self, task: ConversationTask) -> List[ConversationTask]:
        """Break down complex task into subtasks"""
        if not task.intent_result:
            return [task]
        
        intent_type = task.intent_result.primary_intent.intent_type
        subtasks = []
        
        # Task decomposition based on intent type
        if intent_type.value == "create" and "loop" in task.description.lower():
            subtasks = [
                ConversationTask(
                    task_id=str(uuid.uuid4()),
                    description="Validate loop parameters",
                    dependencies=[task.task_id]
                ),
                ConversationTask(
                    task_id=str(uuid.uuid4()),
                    description="Create control loop configuration",
                    dependencies=[task.task_id]
                ),
                ConversationTask(
                    task_id=str(uuid.uuid4()),
                    description="Initialize loop monitoring",
                    dependencies=[task.task_id]
                )
            ]
        elif intent_type.value == "optimize":
            subtasks = [
                ConversationTask(
                    task_id=str(uuid.uuid4()),
                    description="Analyze current performance",
                    dependencies=[task.task_id]
                ),
                ConversationTask(
                    task_id=str(uuid.uuid4()),
                    description="Calculate optimal parameters",
                    dependencies=[task.task_id]
                ),
                ConversationTask(
                    task_id=str(uuid.uuid4()),
                    description="Apply optimization results",
                    dependencies=[task.task_id]
                )
            ]
        
        return subtasks if subtasks else [task]
    
    def get_task_progress_summary(self, tasks: List[ConversationTask]) -> Dict[str, Any]:
        """Get overall progress summary for tasks"""
        if not tasks:
            return {"total_tasks": 0, "overall_progress": 0}
        
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(1 for task in tasks if task.status == status)
        
        completed_tasks = status_counts.get("completed", 0)
        total_tasks = len(tasks)
        overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overall_progress": round(overall_progress, 1),
            "status_distribution": status_counts,
            "active_tasks": [task.task_id for task in tasks if task.status == TaskStatus.IN_PROGRESS]
        }

class ClarificationManager:
    """Manages clarification requests and responses"""
    
    def create_clarification_request(self, question: str, context: str, 
                                   options: List[str] = None) -> ClarificationRequest:
        """Create a new clarification request"""
        return ClarificationRequest(
            request_id=str(uuid.uuid4()),
            question=question,
            context=context,
            options=options or [],
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)  # 10 minute timeout
        )
    
    def process_clarification_response(self, request: ClarificationRequest, 
                                     user_response: str) -> Dict[str, Any]:
        """Process user's response to clarification request"""
        response_lower = user_response.lower().strip()
        
        # Handle common response patterns
        if request.options:
            # Multiple choice clarification
            for i, option in enumerate(request.options):
                if (str(i+1) in response_lower or 
                    option.lower() in response_lower or
                    any(word in response_lower for word in option.lower().split()[:2])):
                    return {
                        "resolved": True,
                        "selected_option": option,
                        "option_index": i,
                        "confidence": 0.9
                    }
        
        # Yes/No questions
        if any(word in response_lower for word in ["yes", "y", "ok", "okay", "sure", "proceed"]):
            return {"resolved": True, "answer": "yes", "confidence": 0.9}
        elif any(word in response_lower for word in ["no", "n", "cancel", "stop", "abort"]):
            return {"resolved": True, "answer": "no", "confidence": 0.9}
        
        # Extract specific values
        import re
        numbers = re.findall(r'\d+\.?\d*', user_response)
        if numbers:
            return {"resolved": True, "value": numbers[0], "confidence": 0.8}
        
        # Partial understanding
        return {
            "resolved": False,
            "partial_response": user_response,
            "confidence": 0.3,
            "needs_follow_up": True
        }
    
    def generate_follow_up_question(self, request: ClarificationRequest, 
                                   partial_response: str) -> str:
        """Generate follow-up question for unclear responses"""
        return f"I didn't quite understand '{partial_response}'. {request.question}\n" + \
               (f"Please choose from: {', '.join(request.options)}" if request.options else 
                "Could you please be more specific?")

class ConversationManager:
    """Main conversation management orchestrator"""
    
    def __init__(self):
        self.context_manager = ContextManager()
        self.task_tracker = TaskTracker()
        self.clarification_manager = ClarificationManager()
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.session_timeout_minutes = 30
    
    def start_session(self, user_id: str, initial_message: str = None) -> ConversationSession:
        """Start a new conversation session"""
        session = ConversationSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            metadata={"initial_message": initial_message or ""}
        )
        
        self.active_sessions[session.session_id] = session
        return session
    
    def process_turn(self, session_id: str, user_input: str, 
                    intent_result: IntentRecognitionResult,
                    command_result: Optional[CommandGenerationResult] = None,
                    app_context: Optional[ApplicationContext] = None) -> ConversationTurn:
        """Process a single conversation turn"""
        start_time = time.time()
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Create new turn
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            user_input=user_input,
            assistant_response="",  # Will be filled by response generation
            intent_result=intent_result,
            command_result=command_result
        )
        
        # Process pending clarifications first
        clarification_response = self._process_pending_clarifications(session, user_input)
        if clarification_response:
            turn.assistant_response = clarification_response
            turn.metadata["clarification_processed"] = True
        else:
            # Normal turn processing
            turn.assistant_response = self._generate_turn_response(session, turn, app_context)
        
        # Update conversation context
        if app_context:
            session.context = self.context_manager.update_context(
                session.context, turn, app_context
            )
        
        # Update tasks if needed
        self._update_tasks_from_turn(session, turn)
        
        # Check for new clarification needs
        if intent_result.requires_clarification and not clarification_response:
            clarification = self.clarification_manager.create_clarification_request(
                question=intent_result.clarification_message or "I need more information.",
                context=user_input,
                options=[]
            )
            session.pending_clarifications.append(clarification)
            turn.clarification_request = clarification
            session.state = ConversationState.WAITING_CLARIFICATION
        
        # Add turn to session
        turn.processing_time = time.time() - start_time
        session.turns.append(turn)
        session.last_activity = datetime.now(timezone.utc)
        
        return turn
    
    def _process_pending_clarifications(self, session: ConversationSession, 
                                      user_input: str) -> Optional[str]:
        """Process any pending clarification requests"""
        if not session.pending_clarifications:
            return None
        
        latest_clarification = session.pending_clarifications[-1]
        response_data = self.clarification_manager.process_clarification_response(
            latest_clarification, user_input
        )
        
        if response_data.get("resolved"):
            # Remove resolved clarification
            session.pending_clarifications.remove(latest_clarification)
            session.context.clarification_history.append(latest_clarification)
            
            # Update session state
            if not session.pending_clarifications:
                session.state = ConversationState.ACTIVE
            
            return f"✅ Thank you for the clarification. " + \
                   f"I understand you selected: {response_data.get('selected_option', response_data.get('answer', 'your response'))}"
        
        elif response_data.get("needs_follow_up"):
            follow_up = self.clarification_manager.generate_follow_up_question(
                latest_clarification, response_data.get("partial_response", "")
            )
            return f"🤔 {follow_up}"
        
        return None
    
    def _generate_turn_response(self, session: ConversationSession, 
                               turn: ConversationTurn,
                               app_context: Optional[ApplicationContext]) -> str:
        """Generate response for a normal conversation turn"""
        if not turn.intent_result:
            return "I didn't understand that. Could you please rephrase your request?"
        
        intent = turn.intent_result.primary_intent
        response_parts = []
        
        # Acknowledge intent
        intent_acknowledgments = {
            "create": "I'll help you create",
            "analyze": "I'll analyze",
            "optimize": "I'll optimize",
            "modify": "I'll modify",
            "query": "Let me show you",
            "validate": "I'll validate",
            "delete": "I'll remove",
            "explain": "Let me explain",
            "help": "I'm here to help with",
            "configure": "I'll configure"
        }
        
        ack = intent_acknowledgments.get(intent.intent_type.value, "I'll help you with")
        
        # Add entity information if available
        if turn.intent_result.entities:
            entity_info = []
            for entity_type, entities in turn.intent_result.entities.items():
                if entities:
                    entity_info.append(f"{entity_type.value}: {entities[0].value}")
            
            if entity_info:
                response_parts.append(f"{ack} {' and '.join(entity_info[:2])}")
            else:
                response_parts.append(f"{ack} your request")
        else:
            response_parts.append(f"{ack} your request")
        
        # Add command information if available
        if turn.command_result:
            cmd = turn.command_result.primary_command
            response_parts.append(f"\n\n💻 Command: `{cmd.command}`")
            response_parts.append(f"📝 This will: {cmd.explanation}")
            
            if cmd.risk_level != "low":
                response_parts.append(f"⚠️ Risk level: {cmd.risk_level}")
            
            if turn.command_result.user_confirmation_required:
                response_parts.append(f"\n{turn.command_result.confirmation_message}")
                session.state = ConversationState.WAITING_CONFIRMATION
        
        # Add task progress if relevant
        if session.active_tasks:
            progress = self.task_tracker.get_task_progress_summary(session.active_tasks)
            if progress["total_tasks"] > 0:
                response_parts.append(f"\n📊 Task Progress: {progress['overall_progress']:.1f}% complete")
        
        # Add helpful context
        if turn.intent_result.confidence_level.value in ["low", "very_low"]:
            response_parts.append("\n💡 If this isn't what you meant, please provide more details.")
        
        return "".join(response_parts)
    
    def _update_tasks_from_turn(self, session: ConversationSession, turn: ConversationTurn):
        """Update active tasks based on conversation turn"""
        if not turn.intent_result:
            return
        
        # Create new task if this is a new request
        if turn.intent_result.primary_intent.confidence > 0.6:
            task = self.task_tracker.create_task(
                description=f"{turn.intent_result.primary_intent.intent_type.value} task",
                intent_result=turn.intent_result
            )
            
            # Start task if command is ready
            if turn.command_result and not turn.command_result.user_confirmation_required:
                self.task_tracker.update_task_status(task, TaskStatus.IN_PROGRESS)
            
            session.active_tasks.append(task)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        task_progress = self.task_tracker.get_task_progress_summary(session.active_tasks)
        
        return {
            "session_id": session_id,
            "state": session.state.value,
            "duration_minutes": (datetime.now(timezone.utc) - session.started_at).total_seconds() / 60,
            "turns_count": len(session.turns),
            "topic": session.context.topic.value,
            "active_entities": len(session.context.active_entities),
            "user_goals": session.context.user_goals,
            "task_progress": task_progress,
            "pending_clarifications": len(session.pending_clarifications),
            "last_activity": session.last_activity.isoformat()
        }
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now(timezone.utc)
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            time_since_activity = (current_time - session.last_activity).total_seconds() / 60
            if time_since_activity > session.timeout_minutes:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Expired session {session_id}")

# Singleton manager instance
_conversation_manager: Optional[ConversationManager] = None

def get_conversation_manager() -> ConversationManager:
    """Get singleton conversation manager"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager

# Export main components
__all__ = [
    "ConversationState",
    "TaskStatus",
    "ConversationTopic",
    "ConversationTask",
    "ClarificationRequest",
    "ConversationContext",
    "ConversationTurn",
    "ConversationSession",
    "ContextManager",
    "TaskTracker",
    "ClarificationManager",
    "ConversationManager",
    "get_conversation_manager"
] 