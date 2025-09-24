"""
Natural Language UI Interface for PLC-GBT Industrial Automation
Following AI Task Orchestrator Guide Methodology

Provides conversational interface to all PLC-GBT capabilities via OpenAI fine-tuned LLM.
Integrates with MCP server for structured tool execution and maintains conversation context.

Author: AI Task Orchestrator
Created: 2025-07-21
Phase: 27.3 - Natural Language UI Implementation
Dependencies: Phase 23 (Fine-tuned LLM), MCP Server, RESTful API
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, cast

# OpenAI integration
import uvicorn

# FastAPI and web framework imports
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Local imports
from mcp.plc_gbt_mcp_server import MCPServerManager, PLCGBTMCPServer
from openai import AsyncOpenAI
from openai._types import NOT_GIVEN
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

UI_VERSION = "1.0.0"
FINE_TUNED_MODEL = "ft:gpt-4o-mini-2024-07-18:whiskey-house:industrial-control:But1jpnl"
MAX_CONVERSATION_HISTORY = 20
SESSION_TIMEOUT_MINUTES = 60

class ConversationRole(str, Enum):
    """Conversation roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class IntentType(str, Enum):
    """Types of user intents"""
    CONTROL_LOOP_MANAGEMENT = "control_loop_management"
    WORKFLOW_CREATION = "workflow_creation"
    MEMORY_OPERATIONS = "memory_operations"
    PLC_INTEGRATION = "plc_integration"
    SYSTEM_MONITORING = "system_monitoring"
    HELP_REQUEST = "help_request"
    GENERAL_INQUIRY = "general_inquiry"

class ContextType(str, Enum):
    """Types of conversation context"""
    NEW_SESSION = "new_session"
    CONTINUING_TASK = "continuing_task"
    FOLLOW_UP_QUESTION = "follow_up_question"
    ERROR_RECOVERY = "error_recovery"

# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class ConversationMessage:
    """Individual message in conversation"""
    id: str
    role: ConversationRole
    content: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] | None = None
    tool_results: list[dict[str, Any]] | None = None

@dataclass
class ConversationSession:
    """Complete conversation session"""
    session_id: str
    user_id: str
    messages: list[ConversationMessage]
    context: dict[str, Any]
    created_at: datetime
    last_activity: datetime
    intent_history: list[IntentType] = field(default_factory=list)
    active_task: str | None = None

@dataclass
class LLMResponse:
    """Response from OpenAI LLM"""
    content: str
    tool_calls: list[dict[str, Any]] | None
    usage: dict[str, Any]
    model: str
    finish_reason: str

@dataclass
class UIResponse:
    """Response from UI interface"""
    message: str
    suggestions: list[str]
    tool_results: list[dict[str, Any]] | None
    context_update: dict[str, Any] | None
    session_id: str
    timestamp: datetime

# =============================================================================
# OPENAI LLM INTEGRATION
# =============================================================================

class OpenAILLMManager:
    """Manages OpenAI fine-tuned LLM integration"""

    def __init__(self, api_key: str, model: str = FINE_TUNED_MODEL):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = self._get_system_prompt()

        logger.info(f"Initialized OpenAI LLM Manager with model: {model}")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the industrial automation LLM"""
        return """You are PLC-GBT, an expert AI assistant for industrial automation and control systems.
You have access to a comprehensive set of tools for managing control loops, creating workflows,
managing memory systems, integrating with PLCs, and monitoring industrial systems.

Your capabilities include:
1. Control Loop Management: Create, modify, and optimize PID controllers and advanced control loops
2. Workflow Creation: Design automation workflows using natural language descriptions
3. Memory Operations: Manage multi-database memory systems for knowledge storage and retrieval
4. PLC Integration: Connect to and interact with ControlLogix and other industrial PLCs
5. System Monitoring: Monitor system health, performance, and provide diagnostics

Key principles:
- Always prioritize safety in industrial environments
- Provide clear, actionable responses
- Use appropriate tools to execute user requests
- Explain complex technical concepts in accessible terms
- Confirm potentially dangerous operations before execution
- Maintain awareness of industrial control theory and best practices

When users ask for help with industrial automation tasks, analyze their request and use the
available tools to provide comprehensive assistance. Always explain what you're doing and why."""

    async def generate_response(self, messages: list[ConversationMessage],
                              available_tools: list[ChatCompletionToolParam] | None) -> LLMResponse:
        """Generate response from OpenAI LLM with tool calling capability"""
        try:
            # Convert messages to OpenAI format
            openai_messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.system_prompt}]

            for msg in messages[-MAX_CONVERSATION_HISTORY:]:  # Limit context window
                openai_messages.append(cast(ChatCompletionMessageParam, {
                    "role": msg.role.value,
                    "content": msg.content
                }))

                # Add tool results if present
                if msg.tool_results:
                    for result in msg.tool_results:
                        openai_messages.append(cast(ChatCompletionMessageParam, {
                            "role": "tool",
                            "content": json.dumps(result),
                            "tool_call_id": result.get("tool_call_id", "unknown")
                        }))

            # Make API call with tools
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                tools=available_tools if available_tools else NOT_GIVEN,
                tool_choice="auto" if available_tools else NOT_GIVEN,
                temperature=0.3,  # Lower temperature for more consistent industrial advice
                max_tokens=1500
            )

            message = response.choices[0].message

            return LLMResponse(
                content=message.content or "",
                tool_calls=[tool_call.model_dump() for tool_call in message.tool_calls] if message.tool_calls else None,
                usage=response.usage.model_dump() if response.usage else {},
                model=response.model,
                finish_reason=response.choices[0].finish_reason
            )

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise

    def format_tools_for_openai(self, mcp_tools: dict[str, Any]) -> list[ChatCompletionToolParam]:
        """Convert MCP tools to OpenAI function calling format"""
        openai_tools: list[ChatCompletionToolParam] = []

        for tool_name, tool_def in mcp_tools.items():
            openai_tool = cast(ChatCompletionToolParam, {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_def.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool_def.parameters,
                        "required": list(tool_def.parameters.keys())
                    }
                }
            })
            openai_tools.append(openai_tool)

        return openai_tools

# =============================================================================
# CONVERSATION MANAGEMENT
# =============================================================================

class ConversationManager:
    """Manages conversation sessions and context"""

    def __init__(self):
        self.sessions: dict[str, ConversationSession] = {}
        self.llm_manager: OpenAILLMManager | None = None
        self.mcp_server: PLCGBTMCPServer | None = None

        logger.info("Initialized Conversation Manager")

    def set_llm_manager(self, llm_manager: OpenAILLMManager):
        """Set the LLM manager"""
        self.llm_manager = llm_manager
        logger.info("LLM manager set for conversation manager")

    def set_mcp_server(self, mcp_server: PLCGBTMCPServer):
        """Set the MCP server"""
        self.mcp_server = mcp_server
        logger.info("MCP server set for conversation manager")

    def create_session(self, user_id: str) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())

        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            messages=[],
            context={},
            created_at=datetime.now(UTC),
            last_activity=datetime.now(UTC)
        )

        self.sessions[session_id] = session
        logger.info(f"Created new conversation session: {session_id}")

        return session_id

    def get_session(self, session_id: str) -> ConversationSession | None:
        """Get a conversation session"""
        return self.sessions.get(session_id)

    def add_message(self, session_id: str, role: ConversationRole,
                   content: str, metadata: dict[str, Any] = None) -> str:
        """Add a message to conversation session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        message_id = str(uuid.uuid4())
        message = ConversationMessage(
            id=message_id,
            role=role,
            content=content,
            timestamp=datetime.now(UTC),
            metadata=metadata or {}
        )

        session.messages.append(message)
        session.last_activity = datetime.now(UTC)

        return message_id

    async def process_user_message(self, session_id: str, user_message: str) -> UIResponse:
        """Process user message and generate response"""
        try:
            session = self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # Add user message
            self.add_message(session_id, ConversationRole.USER, user_message)

            # Get available tools from MCP server
            available_tools = []
            if self.mcp_server and self.llm_manager:
                available_tools = self.llm_manager.format_tools_for_openai(self.mcp_server.tools)

            # Generate LLM response
            if not self.llm_manager:
                raise ValueError("LLM manager not initialized")

            llm_response = await self.llm_manager.generate_response(
                session.messages, available_tools
            )

            # Process tool calls if present
            tool_results = []
            if llm_response.tool_calls and self.mcp_server:
                tool_results = await self._execute_tool_calls(llm_response.tool_calls)

            # Add assistant message
            assistant_message_id = self.add_message(
                session_id,
                ConversationRole.ASSISTANT,
                llm_response.content
            )

            # Update message with tool information
            assistant_message = next(m for m in session.messages if m.id == assistant_message_id)
            assistant_message.tool_calls = llm_response.tool_calls
            assistant_message.tool_results = tool_results

            # Generate suggestions
            suggestions = self._generate_suggestions(session, llm_response)

            return UIResponse(
                message=llm_response.content,
                suggestions=suggestions,
                tool_results=tool_results,
                context_update=None,
                session_id=session_id,
                timestamp=datetime.now(UTC)
            )

        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            return UIResponse(
                message=f"I encountered an error processing your request: {str(e)}",
                suggestions=["Try rephrasing your request", "Check system status", "Ask for help"],
                tool_results=None,
                context_update=None,
                session_id=session_id,
                timestamp=datetime.now(UTC)
            )

    async def _execute_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute tool calls via MCP server"""
        results = []

        for tool_call in tool_calls:
            try:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                # Execute via MCP server
                result = await self.mcp_server.call_tool(function_name, function_args)

                results.append({
                    "tool_call_id": tool_call["id"],
                    "function_name": function_name,
                    "result": result.content[0].text if result.content else "No result",
                    "success": not result.isError
                })

            except Exception as e:
                logger.error(f"Error executing tool call {tool_call}: {e}")
                results.append({
                    "tool_call_id": tool_call.get("id", "unknown"),
                    "function_name": tool_call.get("function", {}).get("name", "unknown"),
                    "result": f"Error: {str(e)}",
                    "success": False
                })

        return results

    def _generate_suggestions(self, session: ConversationSession,
                            llm_response: LLMResponse) -> list[str]:
        """Generate contextual suggestions for next actions"""
        suggestions = []

        # Base suggestions
        if llm_response.tool_calls:
            suggestions.extend([
                "Show me the details of what was executed",
                "Explain the results",
                "What should I do next?"
            ])
        else:
            suggestions.extend([
                "Can you help me create a control loop?",
                "Show me system status",
                "Create a workflow for data logging"
            ])

        # Context-based suggestions
        recent_intents = session.intent_history[-3:] if session.intent_history else []

        if IntentType.CONTROL_LOOP_MANAGEMENT in recent_intents:
            suggestions.extend([
                "Optimize the control loop",
                "Check loop performance",
                "Connect to PLC"
            ])

        if IntentType.WORKFLOW_CREATION in recent_intents:
            suggestions.extend([
                "Analyze the workflow",
                "Deploy the workflow",
                "Create another workflow"
            ])

        # Limit suggestions
        return suggestions[:5]

# =============================================================================
# FASTAPI WEB APPLICATION
# =============================================================================

class NaturalLanguageUIApp:
    """Main FastAPI application for natural language interface"""

    def __init__(self, openai_api_key: str):
        self.app = FastAPI(
            title="PLC-GBT Natural Language Interface",
            description="Conversational interface for industrial automation control",
            version=UI_VERSION
        )

        # Initialize components
        self.conversation_manager = ConversationManager()
        self.llm_manager = OpenAILLMManager(openai_api_key)
        self.mcp_manager = MCPServerManager()

        # Set up templates and static files
        self.templates = Jinja2Templates(directory="templates")

        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Active WebSocket connections
        self.active_connections: dict[str, WebSocket] = {}

        # Register routes
        self._register_routes()

        logger.info("Initialized Natural Language UI App")

    async def startup(self):
        """Start up the application"""
        # Start MCP server
        mcp_server = await self.mcp_manager.start_server()

        # Set managers
        self.conversation_manager.set_llm_manager(self.llm_manager)
        self.conversation_manager.set_mcp_server(mcp_server)

        logger.info("Natural Language UI App started successfully")

    async def shutdown(self):
        """Shut down the application"""
        await self.mcp_manager.stop_server()
        logger.info("Natural Language UI App shut down")

    def _register_routes(self):
        """Register all FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """Serve the main chat interface"""
            return self.templates.TemplateResponse(
                "chat_interface.html",
                {"request": request, "title": "PLC-GBT Industrial Automation Assistant"}
            )

        @self.app.post("/api/sessions")
        async def create_session(user_id: str = "default_user"):
            """Create a new conversation session"""
            session_id = self.conversation_manager.create_session(user_id)
            return {"session_id": session_id, "status": "created"}

        @self.app.get("/api/sessions/{session_id}")
        async def get_session(session_id: str):
            """Get conversation session details"""
            session = self.conversation_manager.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

            return {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "message_count": len(session.messages),
                "active_task": session.active_task
            }

        @self.app.post("/api/sessions/{session_id}/messages")
        async def send_message(session_id: str, message: dict[str, str]):
            """Send a message and get response"""
            user_message = message.get("message", "")
            if not user_message:
                raise HTTPException(status_code=400, detail="Message content required")

            response = await self.conversation_manager.process_user_message(
                session_id, user_message
            )

            return {
                "response": response.message,
                "suggestions": response.suggestions,
                "tool_results": response.tool_results,
                "timestamp": response.timestamp.isoformat()
            }

        @self.app.get("/api/sessions/{session_id}/history")
        async def get_conversation_history(session_id: str, limit: int = 50):
            """Get conversation history"""
            session = self.conversation_manager.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

            messages = session.messages[-limit:] if limit else session.messages

            return {
                "session_id": session_id,
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "tool_calls": msg.tool_calls,
                        "tool_results": msg.tool_results
                    }
                    for msg in messages
                ]
            }

        @self.app.websocket("/ws/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str):
            """WebSocket endpoint for real-time chat"""
            await websocket.accept()
            self.active_connections[session_id] = websocket

            try:
                while True:
                    # Receive message from client
                    data = await websocket.receive_json()
                    user_message = data.get("message", "")

                    if user_message:
                        # Process message
                        response = await self.conversation_manager.process_user_message(
                            session_id, user_message
                        )

                        # Send response back
                        await websocket.send_json({
                            "type": "response",
                            "message": response.message,
                            "suggestions": response.suggestions,
                            "tool_results": response.tool_results,
                            "timestamp": response.timestamp.isoformat()
                        })

            except WebSocketDisconnect:
                del self.active_connections[session_id]
                logger.info(f"WebSocket disconnected for session: {session_id}")
            except Exception as e:
                logger.error(f"WebSocket error for session {session_id}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                })

        @self.app.get("/api/system/status")
        async def system_status():
            """Get system status"""
            mcp_info = self.mcp_manager.get_server_info()

            return {
                "ui_version": UI_VERSION,
                "llm_model": self.llm_manager.model,
                "mcp_server": mcp_info,
                "active_sessions": len(self.conversation_manager.sessions),
                "active_connections": len(self.active_connections),
                "timestamp": datetime.now(UTC).isoformat()
            }

        @self.app.get("/api/capabilities")
        async def get_capabilities():
            """Get available capabilities and tools"""
            if not self.mcp_manager.server_instance:
                return {"tools": [], "prompts": [], "resources": []}

            server = self.mcp_manager.server_instance

            return {
                "tools": [
                    {
                        "name": name,
                        "description": tool.description,
                        "category": tool.category.value,
                        "cli_equivalent": tool.cli_equivalent,
                        "safety_level": tool.safety_level
                    }
                    for name, tool in server.tools.items()
                ],
                "prompts": [
                    {
                        "name": name,
                        "description": prompt.description,
                        "category": prompt.category.value,
                        "parameters": prompt.parameters
                    }
                    for name, prompt in server.prompts.items()
                ],
                "resources": [
                    {
                        "name": name,
                        "description": resource.description,
                        "category": resource.category.value,
                        "uri": resource.uri
                    }
                    for name, resource in server.resources.items()
                ]
            }

# =============================================================================
# HTML TEMPLATE FOR CHAT INTERFACE
# =============================================================================

CHAT_INTERFACE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .chat-container {
            width: 90%;
            max-width: 1200px;
            height: 80vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(90deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .chat-header h1 {
            margin: 0;
            font-size: 24px;
        }

        .chat-header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 15px;
            max-width: 80%;
        }

        .message.user {
            margin-left: auto;
        }

        .message.assistant {
            margin-right: auto;
        }

        .message-content {
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }

        .message.user .message-content {
            background: #007bff;
            color: white;
        }

        .message.assistant .message-content {
            background: #e9ecef;
            color: #333;
            border: 1px solid #dee2e6;
        }

        .message-timestamp {
            font-size: 11px;
            opacity: 0.6;
            margin-top: 4px;
            text-align: right;
        }

        .message.assistant .message-timestamp {
            text-align: left;
        }

        .suggestions {
            padding: 10px 20px;
            background: #fff;
            border-top: 1px solid #dee2e6;
        }

        .suggestions h4 {
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #666;
        }

        .suggestion-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .suggestion-chip {
            padding: 6px 12px;
            background: #e9ecef;
            border: none;
            border-radius: 15px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .suggestion-chip:hover {
            background: #007bff;
            color: white;
        }

        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #dee2e6;
        }

        .chat-input-form {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #dee2e6;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .chat-input:focus {
            border-color: #007bff;
        }

        .send-button {
            padding: 12px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }

        .send-button:hover {
            background: #0056b3;
        }

        .send-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }

        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: #e9ecef;
            border-radius: 18px;
            max-width: 80px;
            margin-bottom: 15px;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: #666;
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }

        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        .typing-dot:nth-child(3) { animation-delay: 0s; }

        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }

        .tool-results {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 4px;
            font-size: 12px;
        }

        .tool-result {
            margin-bottom: 8px;
        }

        .tool-result.success {
            color: #28a745;
        }

        .tool-result.error {
            color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🏭 PLC-GBT Industrial Automation Assistant</h1>
            <p>Conversational interface for control loops, workflows, and industrial automation</p>
        </div>

        <div class="chat-messages" id="messages">
            <div class="message assistant">
                <div class="message-content">
                    Hello! I'm your PLC-GBT assistant. I can help you with:
                    <br><br>
                    🔧 <strong>Control Loop Management</strong> - Create and manage PID controllers<br>
                    🔄 <strong>Workflow Creation</strong> - Design automation workflows<br>
                    💾 <strong>Memory Operations</strong> - Manage knowledge storage<br>
                    🏭 <strong>PLC Integration</strong> - Connect to industrial systems<br>
                    📊 <strong>System Monitoring</strong> - Monitor performance and health<br>
                    <br>
                    What would you like to work on today?
                </div>
                <div class="message-timestamp">Just now</div>
            </div>
        </div>

        <div class="typing-indicator" id="typing">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>

        <div class="suggestions" id="suggestions">
            <h4>Suggestions:</h4>
            <div class="suggestion-chips">
                <button class="suggestion-chip" onclick="sendSuggestion('Create a temperature control loop')">Create a temperature control loop</button>
                <button class="suggestion-chip" onclick="sendSuggestion('Show system status')">Show system status</button>
                <button class="suggestion-chip" onclick="sendSuggestion('Create a data logging workflow')">Create a data logging workflow</button>
                <button class="suggestion-chip" onclick="sendSuggestion('Connect to PLC')">Connect to PLC</button>
                <button class="suggestion-chip" onclick="sendSuggestion('Help me get started')">Help me get started</button>
            </div>
        </div>

        <div class="chat-input-container">
            <form class="chat-input-form" onsubmit="sendMessage(event)">
                <input type="text" class="chat-input" id="messageInput"
                       placeholder="Ask me about industrial automation..." autocomplete="off">
                <button type="submit" class="send-button" id="sendButton">Send</button>
            </form>
        </div>
    </div>

    <script>
        let sessionId = null;
        let websocket = null;

        // Initialize session and WebSocket
        async function init() {
            try {
                // Create session
                const response = await fetch('/api/sessions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: 'web_user' })
                });
                const data = await response.json();
                sessionId = data.session_id;

                // Connect WebSocket
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                websocket = new WebSocket(`${protocol}//${window.location.host}/ws/${sessionId}`);

                websocket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'response') {
                        addMessage('assistant', data.message, data.tool_results);
                        updateSuggestions(data.suggestions);
                        hideTyping();
                        enableInput();
                    } else if (data.type === 'error') {
                        addMessage('assistant', data.message);
                        hideTyping();
                        enableInput();
                    }
                };

                websocket.onclose = function() {
                    console.log('WebSocket connection closed');
                };

            } catch (error) {
                console.error('Failed to initialize:', error);
            }
        }

        function sendMessage(event) {
            event.preventDefault();
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (message && websocket) {
                addMessage('user', message);
                input.value = '';
                showTyping();
                disableInput();

                websocket.send(JSON.stringify({ message: message }));
            }
        }

        function sendSuggestion(text) {
            document.getElementById('messageInput').value = text;
            sendMessage(new Event('submit'));
        }

        function addMessage(role, content, toolResults = null) {
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;

            let toolResultsHtml = '';
            if (toolResults && toolResults.length > 0) {
                toolResultsHtml = '<div class="tool-results">';
                toolResults.forEach(result => {
                    const resultClass = result.success ? 'success' : 'error';
                    toolResultsHtml += `<div class="tool-result ${resultClass}">🔧 ${result.function_name}: ${result.result}</div>`;
                });
                toolResultsHtml += '</div>';
            }

            messageDiv.innerHTML = `
                <div class="message-content">${content}${toolResultsHtml}</div>
                <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
            `;

            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function updateSuggestions(suggestions) {
            const suggestionsContainer = document.querySelector('.suggestion-chips');
            suggestionsContainer.innerHTML = '';

            suggestions.forEach(suggestion => {
                const chip = document.createElement('button');
                chip.className = 'suggestion-chip';
                chip.textContent = suggestion;
                chip.onclick = () => sendSuggestion(suggestion);
                suggestionsContainer.appendChild(chip);
            });
        }

        function showTyping() {
            document.getElementById('typing').style.display = 'block';
            const messagesContainer = document.getElementById('messages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function hideTyping() {
            document.getElementById('typing').style.display = 'none';
        }

        function disableInput() {
            document.getElementById('messageInput').disabled = true;
            document.getElementById('sendButton').disabled = true;
        }

        function enableInput() {
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendButton').disabled = false;
            document.getElementById('messageInput').focus();
        }

        // Handle Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(e);
            }
        });

        // Initialize on load
        window.addEventListener('load', init);
    </script>
</body>
</html>
"""

# =============================================================================
# APPLICATION FACTORY AND RUNNER
# =============================================================================

def create_app(openai_api_key: str) -> NaturalLanguageUIApp:
    """Create and configure the Natural Language UI application"""
    app = NaturalLanguageUIApp(openai_api_key)

    # Create templates directory and file
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)

    chat_template_file = templates_dir / "chat_interface.html"
    chat_template_file.write_text(CHAT_INTERFACE_TEMPLATE)

    return app

async def run_server(openai_api_key: str, host: str = "0.0.0.0", port: int = 8080):
    """Run the Natural Language UI server"""
    app_instance = create_app(openai_api_key)

    # Add startup and shutdown events
    @app_instance.app.on_event("startup")
    async def startup_event():
        await app_instance.startup()

    @app_instance.app.on_event("shutdown")
    async def shutdown_event():
        await app_instance.shutdown()

    # Run with uvicorn
    config = uvicorn.Config(
        app_instance.app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)

    logger.info(f"Starting Natural Language UI server on {host}:{port}")
    await server.serve()

if __name__ == "__main__":
    import os

    # Get OpenAI API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable required")

    # Run the server
    asyncio.run(run_server(openai_api_key))
