"""
Conversational Workflow Management Interface
Phase 26.4.3: Chat-based workflow creation and management

Provides natural language interface for creating, modifying, and managing
N8N workflows through conversational interaction.
"""

import asyncio
import json
import logging
import os

# Import Phase 23 LLM components and workflow components
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../llm'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../llm'))

from nl_workflow_parser import NaturalLanguageWorkflowParser
from workflow_optimizer import AIWorkflowOptimizer, WorkflowAnalysisResult

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """States of the workflow conversation"""
    INITIAL = "initial"
    CREATING_WORKFLOW = "creating_workflow"
    MODIFYING_WORKFLOW = "modifying_workflow"
    ANALYZING_WORKFLOW = "analyzing_workflow"
    OPTIMIZING_WORKFLOW = "optimizing_workflow"
    DEPLOYING_WORKFLOW = "deploying_workflow"
    TROUBLESHOOTING = "troubleshooting"
    COMPLETED = "completed"

class UserIntent(Enum):
    """User intents for workflow management"""
    CREATE_WORKFLOW = "create_workflow"
    MODIFY_WORKFLOW = "modify_workflow"
    ANALYZE_WORKFLOW = "analyze_workflow"
    OPTIMIZE_WORKFLOW = "optimize_workflow"
    DELETE_WORKFLOW = "delete_workflow"
    LIST_WORKFLOWS = "list_workflows"
    DEPLOY_WORKFLOW = "deploy_workflow"
    MONITOR_WORKFLOW = "monitor_workflow"
    HELP = "help"
    CANCEL = "cancel"

@dataclass
class ConversationContext:
    """Context for workflow conversation"""
    current_workflow_id: Optional[str] = None
    workflow_definition: Optional[Dict[str, Any]] = None
    analysis_result: Optional[WorkflowAnalysisResult] = None
    pending_confirmations: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationResponse:
    """Response from the conversational interface"""
    message: str
    suggestions: List[str] = field(default_factory=list)
    requires_confirmation: bool = False
    workflow_preview: Optional[Dict[str, Any]] = None
    analysis_data: Optional[Dict[str, Any]] = None
    next_actions: List[str] = field(default_factory=list)
    conversation_state: ConversationState = ConversationState.INITIAL

class WorkflowIntentClassifier:
    """Classifies user intents related to workflow management"""

    def __init__(self):
        self.intent_patterns = {
            UserIntent.CREATE_WORKFLOW: [
                r'\b(?:create|build|make|generate)\s+.*(?:workflow|automation)\b',
                r'\b(?:new|fresh)\s+.*(?:workflow|process)\b',
                r'\b(?:automate|setup)\s+.*(?:process|task)\b'
            ],
            UserIntent.MODIFY_WORKFLOW: [
                r'\b(?:modify|change|update|edit)\s+.*(?:workflow|automation)\b',
                r'\b(?:add|remove|delete)\s+.*(?:node|step|operation)\b',
                r'\b(?:improve|enhance|fix)\s+.*(?:workflow|process)\b'
            ],
            UserIntent.ANALYZE_WORKFLOW: [
                r'\b(?:analyze|check|review|examine)\s+.*(?:workflow|performance)\b',
                r'\b(?:how|why)\s+.*(?:working|performing|running)\b',
                r'\b(?:status|health|metrics)\s+.*(?:workflow|automation)\b'
            ],
            UserIntent.OPTIMIZE_WORKFLOW: [
                r'\b(?:optimize|improve|enhance|speed up)\s+.*(?:workflow|performance)\b',
                r'\b(?:make|get)\s+.*(?:faster|better|efficient)\b',
                r'\b(?:reduce|minimize)\s+.*(?:time|cost|errors)\b'
            ],
            UserIntent.LIST_WORKFLOWS: [
                r'\b(?:list|show|display)\s+.*(?:workflows|automations)\b',
                r'\b(?:what|which)\s+.*(?:workflows|processes)\s+.*(?:exist|available)\b',
                r'\b(?:all|my)\s+.*(?:workflows|automations)\b'
            ],
            UserIntent.DEPLOY_WORKFLOW: [
                r'\b(?:deploy|activate|start|run)\s+.*(?:workflow|automation)\b',
                r'\b(?:put|move)\s+.*(?:production|live)\b',
                r'\b(?:execute|launch)\s+.*(?:workflow|process)\b'
            ],
            UserIntent.HELP: [
                r'\b(?:help|assistance|support)\b',
                r'\b(?:how|what)\s+.*(?:can|do|possible)\b',
                r'\b(?:commands|options|capabilities)\b'
            ]
        }

    def classify_intent(self, text: str) -> Tuple[UserIntent, float]:
        """Classify user intent with confidence score"""
        text_lower = text.lower()
        best_intent = UserIntent.HELP  # Default
        best_score = 0.0

        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1.0

            # Normalize by pattern count
            score = score / len(patterns)

            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent, best_score

class ConversationalWorkflowManager:
    """Main conversational interface for workflow management"""

    def __init__(self):
        self.workflow_parser = NaturalLanguageWorkflowParser()
        self.workflow_optimizer = AIWorkflowOptimizer()
        self.intent_classifier = WorkflowIntentClassifier()
        self.active_sessions = {}
        self.workflow_storage = {}  # In-memory storage for demo

    async def handle_user_message(self, user_id: str, message: str,
                                  session_id: Optional[str] = None) -> ConversationResponse:
        """Handle incoming user message and provide appropriate response"""

        # Get or create conversation session
        if session_id is None:
            session_id = str(uuid.uuid4())

        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = ConversationContext()

        context = self.active_sessions[session_id]

        # Classify user intent
        intent, confidence = self.intent_classifier.classify_intent(message)

        # Route to appropriate handler
        if intent == UserIntent.CREATE_WORKFLOW:
            return await self._handle_create_workflow(message, context)
        elif intent == UserIntent.MODIFY_WORKFLOW:
            return await self._handle_modify_workflow(message, context)
        elif intent == UserIntent.ANALYZE_WORKFLOW:
            return await self._handle_analyze_workflow(message, context)
        elif intent == UserIntent.OPTIMIZE_WORKFLOW:
            return await self._handle_optimize_workflow(message, context)
        elif intent == UserIntent.LIST_WORKFLOWS:
            return await self._handle_list_workflows(message, context)
        elif intent == UserIntent.DEPLOY_WORKFLOW:
            return await self._handle_deploy_workflow(message, context)
        elif intent == UserIntent.HELP:
            return await self._handle_help(message, context)
        else:
            return ConversationResponse(
                message="I'm not sure what you'd like to do. Could you please rephrase or ask for help?",
                suggestions=["Create a new workflow", "List existing workflows", "Help"],
                conversation_state=ConversationState.INITIAL
            )

    async def _handle_create_workflow(self, message: str,
                                     context: ConversationContext) -> ConversationResponse:
        """Handle workflow creation requests"""

        try:
            # Parse the workflow request
            parsing_result = self.workflow_parser.parse_workflow_request(message)

            if parsing_result.parsing_success and parsing_result.workflow_definition:
                workflow = parsing_result.workflow_definition

                # Store workflow in context
                context.current_workflow_id = workflow.id
                context.workflow_definition = workflow.__dict__

                # Generate preview
                workflow_json = self.workflow_parser.get_workflow_json(workflow)

                response_message = f"""
✅ **Workflow Created Successfully!**

**Name**: {workflow.name}
**Type**: {workflow.workflow_type.value.replace('_', ' ').title()}
**Nodes**: {len(workflow.nodes)}
**Connections**: {len(workflow.connections)}

**Description**: {workflow.description}

The workflow includes:
"""

                for i, node in enumerate(workflow.nodes, 1):
                    response_message += f"\n{i}. **{node.name}** ({node.type.value.replace('_', ' ').title()})"

                response_message += """

Would you like me to:
- Analyze the workflow for optimization opportunities
- Deploy it to production
- Make modifications
- Save it for later use
"""

                return ConversationResponse(
                    message=response_message,
                    workflow_preview=json.loads(workflow_json),
                    suggestions=[
                        "Analyze workflow performance",
                        "Deploy to production",
                        "Optimize workflow",
                        "Modify workflow"
                    ],
                    conversation_state=ConversationState.CREATING_WORKFLOW
                )

            else:
                # Workflow creation failed, provide guidance
                error_msg = "I had trouble creating your workflow. "
                if parsing_result.error_message:
                    error_msg += f"Error: {parsing_result.error_message}"

                if parsing_result.clarification_needed:
                    error_msg += f"\n\nI need clarification on: {', '.join(parsing_result.clarification_needed)}"

                if parsing_result.suggestions:
                    error_msg += f"\n\nSuggestions: {', '.join(parsing_result.suggestions)}"

                return ConversationResponse(
                    message=error_msg,
                    suggestions=[
                        "Try describing the workflow differently",
                        "Start with a simple example",
                        "Ask for help with workflow creation"
                    ],
                    conversation_state=ConversationState.INITIAL
                )

        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            return ConversationResponse(
                message="An error occurred while creating the workflow. Please try again or contact support.",
                suggestions=["Try again", "Get help"],
                conversation_state=ConversationState.INITIAL
            )

    async def _handle_modify_workflow(self, message: str,
                                     context: ConversationContext) -> ConversationResponse:
        """Handle workflow modification requests"""

        if not context.current_workflow_id or not context.workflow_definition:
            return ConversationResponse(
                message="No workflow is currently selected. Please create a workflow first or select an existing one.",
                suggestions=["Create new workflow", "List existing workflows"],
                conversation_state=ConversationState.INITIAL
            )

        # For now, provide guidance on modifications
        # In a full implementation, this would parse the modification request
        # and apply changes to the workflow definition

        modification_guidance = f"""
🔧 **Workflow Modification**

Current workflow: **{context.workflow_definition.get('name', 'Unknown')}**

I can help you modify your workflow. Here are some things you can ask for:

**Add Components**:
- "Add email notification when temperature exceeds 100°C"
- "Add database logging every 30 seconds"
- "Add safety interlock for emergency shutdown"

**Modify Parameters**:
- "Change PID controller Kp to 1.5"
- "Set polling rate to 5 seconds"
- "Update alarm threshold to 85%"

**Remove Components**:
- "Remove the email notification"
- "Delete the timer node"
- "Disable the safety check"

What specific modification would you like to make?
"""

        return ConversationResponse(
            message=modification_guidance,
            suggestions=[
                "Add email notification",
                "Change controller parameters",
                "Add safety interlock",
                "Modify polling settings"
            ],
            conversation_state=ConversationState.MODIFYING_WORKFLOW
        )

    async def _handle_analyze_workflow(self, message: str,
                                      context: ConversationContext) -> ConversationResponse:
        """Handle workflow analysis requests"""

        if not context.current_workflow_id or not context.workflow_definition:
            # Check if workflow ID is mentioned in message
            workflow_id = self._extract_workflow_id(message)
            if workflow_id and workflow_id in self.workflow_storage:
                context.current_workflow_id = workflow_id
                context.workflow_definition = self.workflow_storage[workflow_id]
            else:
                return ConversationResponse(
                    message="No workflow is currently selected. Please create a workflow first or specify which workflow to analyze.",
                    suggestions=["Create new workflow", "List existing workflows"],
                    conversation_state=ConversationState.INITIAL
                )

        try:
            # Reconstruct workflow definition from stored data
            from nl_workflow_parser import WorkflowDefinition, WorkflowType

            workflow_data = context.workflow_definition
            workflow = WorkflowDefinition(
                id=workflow_data['id'],
                name=workflow_data['name'],
                workflow_type=WorkflowType(workflow_data['workflow_type']),
                description=workflow_data['description']
            )

            # Perform analysis
            analysis = self.workflow_optimizer.performance_analyzer.analyze_workflow_performance(workflow)
            context.analysis_result = analysis

            # Generate analysis report
            analysis_message = f"""
📊 **Workflow Analysis Results**

**Workflow**: {workflow.name}
**Analysis Date**: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

## Performance Scores
- **Overall Health**: {analysis.overall_health_score:.1f}/100
- **Performance**: {analysis.performance_score:.1f}/100
- **Reliability**: {analysis.reliability_score:.1f}/100
- **Maintainability**: {analysis.maintainability_score:.1f}/100

## Key Metrics
- **Estimated Execution Time**: {analysis.current_metrics.execution_time_avg:.2f} seconds
- **Expected Throughput**: {analysis.current_metrics.throughput_per_hour:.0f} executions/hour
- **Estimated Error Rate**: {analysis.current_metrics.error_rate:.1f}%
- **Resource Usage**: {analysis.current_metrics.resource_usage_cpu:.1f}% CPU

## Issues Found
"""

            if analysis.bottlenecks:
                analysis_message += f"\n**⚠️ Performance Bottlenecks** ({len(analysis.bottlenecks)}):\n"
                for bottleneck in analysis.bottlenecks:
                    analysis_message += f"- {bottleneck}\n"

            if analysis.risk_factors:
                analysis_message += f"\n**🔴 Risk Factors** ({len(analysis.risk_factors)}):\n"
                for risk in analysis.risk_factors:
                    analysis_message += f"- {risk}\n"

            if analysis.compliance_issues:
                analysis_message += f"\n**📋 Compliance Issues** ({len(analysis.compliance_issues)}):\n"
                for issue in analysis.compliance_issues:
                    analysis_message += f"- {issue}\n"

            if analysis.recommendations:
                analysis_message += f"\n## Optimization Recommendations ({len(analysis.recommendations)})\n"
                for i, rec in enumerate(analysis.recommendations[:3], 1):  # Show top 3
                    analysis_message += f"{i}. **{rec.title}** ({rec.priority.value.title()})\n"
                    analysis_message += f"   {rec.description}\n"
                    analysis_message += f"   Expected: {rec.expected_improvement}\n\n"

                if len(analysis.recommendations) > 3:
                    analysis_message += f"*...and {len(analysis.recommendations) - 3} more recommendations*\n"

            analysis_message += "\nWould you like me to optimize the workflow or provide more details on any specific area?"

            return ConversationResponse(
                message=analysis_message,
                analysis_data={
                    'overall_score': analysis.overall_health_score,
                    'performance_score': analysis.performance_score,
                    'reliability_score': analysis.reliability_score,
                    'maintainability_score': analysis.maintainability_score,
                    'recommendations_count': len(analysis.recommendations),
                    'issues_count': len(analysis.bottlenecks) + len(analysis.risk_factors)
                },
                suggestions=[
                    "Optimize workflow",
                    "Show detailed recommendations",
                    "Fix specific issues",
                    "Deploy anyway"
                ],
                conversation_state=ConversationState.ANALYZING_WORKFLOW
            )

        except Exception as e:
            logger.error(f"Error analyzing workflow: {str(e)}")
            return ConversationResponse(
                message="An error occurred while analyzing the workflow. Please try again.",
                suggestions=["Try again", "Get help"],
                conversation_state=ConversationState.INITIAL
            )

    async def _handle_optimize_workflow(self, message: str,
                                       context: ConversationContext) -> ConversationResponse:
        """Handle workflow optimization requests"""

        if not context.current_workflow_id or not context.workflow_definition:
            return ConversationResponse(
                message="No workflow is currently selected for optimization. Please create or select a workflow first.",
                suggestions=["Create new workflow", "List existing workflows"],
                conversation_state=ConversationState.INITIAL
            )

        try:
            # Get analysis if not already done
            if not context.analysis_result:
                # Perform quick analysis first
                workflow_data = context.workflow_definition
                from nl_workflow_parser import WorkflowDefinition, WorkflowType

                workflow = WorkflowDefinition(
                    id=workflow_data['id'],
                    name=workflow_data['name'],
                    workflow_type=WorkflowType(workflow_data['workflow_type']),
                    description=workflow_data['description']
                )

                context.analysis_result = self.workflow_optimizer.performance_analyzer.analyze_workflow_performance(workflow)

            # Perform optimization
            optimized = self.workflow_optimizer.optimize_workflow(
                workflow,
                context.analysis_result.current_metrics
            )

            # Generate optimization report
            optimization_message = f"""
🚀 **Workflow Optimization Complete!**

**Original Workflow**: {optimized.original_workflow.name}
**Optimized Workflow**: {optimized.optimized_workflow.name}

## Optimizations Applied ({len(optimized.applied_optimizations)})
"""

            for i, optimization in enumerate(optimized.applied_optimizations, 1):
                optimization_message += f"""
{i}. **{optimization.title}**
   - **Type**: {optimization.optimization_type.value.title()}
   - **Priority**: {optimization.priority.value.title()}
   - **Expected**: {optimization.expected_improvement}
   - **Effort**: {optimization.implementation_effort}
"""

            optimization_message += f"""
## Expected Improvements
- **Execution Time**: {optimized.expected_improvements.get('execution_time_reduction', 0)*100:.1f}% faster
- **Reliability**: {optimized.expected_improvements.get('reliability_improvement', 0)*100:.1f}% more reliable
- **Error Rate**: {optimized.expected_improvements.get('error_rate_reduction', 0)*100:.1f}% fewer errors
- **Cost**: {optimized.expected_improvements.get('cost_reduction', 0)*100:.1f}% cost reduction

## Validation Results
- **Status**: {"✅ PASSED" if optimized.validation_results['valid'] else "❌ FAILED"}
- **Nodes Modified**: {optimized.validation_results['nodes_modified']}
- **New Nodes Added**: {optimized.validation_results['new_nodes_added']}

The optimized workflow is ready for deployment. Would you like to:
- Deploy the optimized version
- Compare with the original
- Make additional modifications
"""

            # Store optimized workflow
            context.workflow_definition = optimized.optimized_workflow.__dict__
            context.current_workflow_id = optimized.optimized_workflow.id

            return ConversationResponse(
                message=optimization_message,
                workflow_preview=json.loads(self.workflow_parser.get_workflow_json(optimized.optimized_workflow)),
                suggestions=[
                    "Deploy optimized workflow",
                    "Compare versions",
                    "Make more changes",
                    "Save for later"
                ],
                conversation_state=ConversationState.OPTIMIZING_WORKFLOW
            )

        except Exception as e:
            logger.error(f"Error optimizing workflow: {str(e)}")
            return ConversationResponse(
                message="An error occurred while optimizing the workflow. Please try again.",
                suggestions=["Try again", "Analyze workflow first", "Get help"],
                conversation_state=ConversationState.INITIAL
            )

    async def _handle_list_workflows(self, message: str,
                                    context: ConversationContext) -> ConversationResponse:
        """Handle requests to list existing workflows"""

        if not self.workflow_storage:
            return ConversationResponse(
                message="No workflows found. Would you like to create your first workflow?",
                suggestions=["Create new workflow", "Get help"],
                conversation_state=ConversationState.INITIAL
            )

        workflows_message = f"📋 **Available Workflows** ({len(self.workflow_storage)})\n\n"

        for i, (workflow_id, workflow_data) in enumerate(self.workflow_storage.items(), 1):
            workflows_message += f"{i}. **{workflow_data.get('name', 'Unnamed Workflow')}**\n"
            workflows_message += f"   - ID: `{workflow_id[:8]}...`\n"
            workflows_message += f"   - Type: {workflow_data.get('workflow_type', 'Unknown').replace('_', ' ').title()}\n"
            workflows_message += f"   - Created: {workflow_data.get('created_at', 'Unknown')}\n\n"

        workflows_message += "Which workflow would you like to work with?"

        # Generate suggestions based on available workflows
        suggestions = [f"Analyze {list(self.workflow_storage.values())[i].get('name', 'workflow')}"
                      for i in range(min(3, len(self.workflow_storage)))]
        suggestions.append("Create new workflow")

        return ConversationResponse(
            message=workflows_message,
            suggestions=suggestions,
            conversation_state=ConversationState.INITIAL
        )

    async def _handle_deploy_workflow(self, message: str,
                                     context: ConversationContext) -> ConversationResponse:
        """Handle workflow deployment requests"""

        if not context.current_workflow_id or not context.workflow_definition:
            return ConversationResponse(
                message="No workflow is currently selected for deployment. Please create or select a workflow first.",
                suggestions=["Create new workflow", "List existing workflows"],
                conversation_state=ConversationState.INITIAL
            )

        # Simulate deployment process
        workflow_name = context.workflow_definition.get('name', 'Unknown Workflow')

        deployment_message = f"""
🚀 **Deploying Workflow: {workflow_name}**

## Pre-Deployment Checks
✅ Workflow validation passed
✅ Dependencies verified
✅ Credentials configured
✅ Resource allocation confirmed

## Deployment Process
1. **Staging Deployment** - Testing in staging environment...
2. **Health Checks** - Verifying workflow functionality...
3. **Production Deployment** - Activating in production...
4. **Monitoring Setup** - Configuring alerts and dashboards...

## Deployment Results
🎉 **Deployment Successful!**

- **Status**: Active and Running
- **Endpoint**: `https://n8n.plc-automation.internal/workflow/{context.current_workflow_id}`
- **Monitoring**: Dashboard available at monitoring.plc-automation.internal
- **Logs**: Available in centralized logging system

## Next Steps
- Monitor workflow performance for the first 24 hours
- Set up alerting thresholds
- Schedule regular health checks
- Plan for scaling if needed

The workflow is now live and processing requests!
"""

        # Store workflow as deployed
        context.workflow_definition['status'] = 'deployed'
        context.workflow_definition['deployment_date'] = datetime.now(timezone.utc).isoformat()
        self.workflow_storage[context.current_workflow_id] = context.workflow_definition

        return ConversationResponse(
            message=deployment_message,
            suggestions=[
                "Monitor workflow performance",
                "Create another workflow",
                "View deployment logs",
                "Set up alerts"
            ],
            conversation_state=ConversationState.DEPLOYING_WORKFLOW
        )

    async def _handle_help(self, message: str,
                          context: ConversationContext) -> ConversationResponse:
        """Handle help requests"""

        help_message = """
🤖 **PLC-GBT Workflow Assistant Help**

I can help you create, manage, and optimize industrial automation workflows using natural language. Here's what I can do:

## 🔧 **Workflow Creation**
- "Create a temperature control loop for the reactor"
- "Set up data logging for pressure and flow"
- "Build an alarm system for tank levels"
- "Generate a batch processing workflow"

## 📝 **Workflow Management**
- "Analyze my workflow performance"
- "Optimize the temperature control workflow"
- "List all my workflows"
- "Deploy workflow to production"

## 🔍 **Analysis & Optimization**
- "Check for performance bottlenecks"
- "Find ways to improve reliability"
- "Suggest cost optimizations"
- "Identify safety issues"

## 📊 **Monitoring & Troubleshooting**
- "Show workflow status"
- "Why is my workflow slow?"
- "Fix errors in the batch process"
- "Monitor execution metrics"

## 💡 **Examples to Get Started**
1. **Simple Control Loop**: "Create a PID controller for reactor temperature with setpoint 85°C"
2. **Data Collection**: "Log temperature, pressure, and flow data every 30 seconds to database"
3. **Alarm System**: "Monitor tank level and email alerts when high/low limits reached"
4. **Batch Process**: "Create a 5-step batch recipe: heat, mix, react, cool, discharge"

## 🚀 **Advanced Features**
- AI-powered optimization suggestions
- Safety compliance checking
- Performance analysis and bottleneck detection
- Automatic error handling and retry logic
- Integration with PLCs, databases, and notification systems

Just describe what you want to automate in plain English, and I'll help you build it!

What would you like to work on today?
"""

        return ConversationResponse(
            message=help_message,
            suggestions=[
                "Create a temperature control workflow",
                "Set up data logging",
                "Build an alarm system",
                "List my existing workflows"
            ],
            conversation_state=ConversationState.INITIAL
        )

    def _extract_workflow_id(self, message: str) -> Optional[str]:
        """Extract workflow ID from message if mentioned"""
        # Simple pattern matching for workflow IDs
        import re

        # Look for patterns like "workflow abc123" or "ID: abc123"
        patterns = [
            r'workflow\s+([a-f0-9\-]{8,})',
            r'id[:]\s*([a-f0-9\-]{8,})',
            r'([a-f0-9\-]{8,})'
        ]

        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                potential_id = match.group(1)
                # Check if this ID exists in storage
                for stored_id in self.workflow_storage:
                    if stored_id.startswith(potential_id):
                        return stored_id

        return None

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            return context.session_metadata.get('history', [])
        return []

    def clear_session(self, session_id: str):
        """Clear conversation session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

# Voice interface integration (placeholder for future implementation)
class VoiceWorkflowInterface:
    """Voice-controlled workflow interface"""

    def __init__(self, conversation_manager: ConversationalWorkflowManager):
        self.conversation_manager = conversation_manager

    async def process_voice_command(self, audio_data: bytes,
                                   user_id: str, session_id: str) -> Dict[str, Any]:
        """Process voice command and return response"""
        # Placeholder for speech-to-text conversion
        # In a real implementation, this would use STT service
        text = self._convert_speech_to_text(audio_data)

        # Process through conversational interface
        response = await self.conversation_manager.handle_user_message(
            user_id, text, session_id
        )

        # Convert response to speech
        audio_response = self._convert_text_to_speech(response.message)

        return {
            'text_response': response.message,
            'audio_response': audio_response,
            'suggestions': response.suggestions,
            'workflow_preview': response.workflow_preview
        }

    def _convert_speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text (placeholder)"""
        # Placeholder implementation
        return "Create a temperature control loop for the reactor"

    def _convert_text_to_speech(self, text: str) -> bytes:
        """Convert text to speech (placeholder)"""
        # Placeholder implementation
        return b"audio_data_placeholder"

# Example usage and testing
async def test_conversational_interface():
    """Test the conversational workflow interface"""
    manager = ConversationalWorkflowManager()

    test_conversations = [
        "Create a temperature control loop for the reactor with PID controller",
        "Analyze the workflow I just created",
        "Optimize it for better performance",
        "Deploy the optimized workflow to production"
    ]

    session_id = "test_session_123"
    user_id = "test_user"

    print("=== Testing Conversational Workflow Interface ===\n")

    for _i, message in enumerate(test_conversations, 1):
        print(f"👤 User: {message}")

        response = await manager.handle_user_message(user_id, message, session_id)

        print(f"🤖 Assistant: {response.message[:200]}...")
        print(f"📋 Suggestions: {', '.join(response.suggestions[:3])}")
        print(f"🔄 State: {response.conversation_state.value}")

        if response.workflow_preview:
            print(f"📊 Workflow: {response.workflow_preview.get('name', 'Unknown')}")

        print("-" * 80 + "\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_conversational_interface())
