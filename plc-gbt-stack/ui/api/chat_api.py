#!/usr/bin/env python3
"""
Task 23.5.3: Chat API Implementation
===================================

RESTful chat API with authentication, rate limiting, and comprehensive
integration with Phase 23.1-23.4 LLM components.

Features:
- RESTful endpoints for chat interaction
- JWT authentication and authorization
- Rate limiting and request validation
- Streaming responses for real-time interaction
- Comprehensive error handling
- OpenAPI documentation generation

Author: PLC-GPT Development Team
Date: June 18, 2025
Task: 23.5.3 - API Endpoints
Methodology: AI Task Orchestrator Guide
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.responses import StreamingResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from pydantic import BaseModel, Field, validator
    from starlette.middleware.base import BaseHTTPMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logging.warning("FastAPI not available - chat API will not be functional")

# Import Phase 23 components
try:
    from ...llm.service import LLMService, get_llm_service
    from ...llm.conversation import ConversationManager
    from ...llm.task_executor import TaskExecutor
    from ...llm.task_planner import TaskPlanner
    from ...llm import LLMRequest, LLMRequestType, ConversationRole, ApplicationContext, LLMResponse
    from ...auth.jwt_manager import JWTManager, get_jwt_manager
    from ...auth.rbac import Permission, get_rbac_manager
except ImportError as e:
    logging.warning(f"Phase 23 components not available: {e}")

# Configure logging
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer() if FASTAPI_AVAILABLE else None

class MessageRole(str, Enum):
    """Message roles for API"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatRequestType(str, Enum):
    """Types of chat requests"""
    SIMPLE = "simple"
    TASK_EXECUTION = "task_execution"
    ANALYSIS = "analysis"
    CONFIGURATION = "configuration"

# Pydantic models for API
if FASTAPI_AVAILABLE:
    class Message(BaseModel):
        """Individual message in chat"""
        role: MessageRole
        content: str
        timestamp: Optional[datetime] = Field(default_factory=datetime.now)
        metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
        
    class ChatRequest(BaseModel):
        """Chat request model"""
        message: str = Field(..., min_length=1, max_length=10000, description="User message")
        conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn chat")
        request_type: ChatRequestType = Field(ChatRequestType.SIMPLE, description="Type of chat request")
        context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
        stream: bool = Field(False, description="Enable streaming response")
        max_tokens: Optional[int] = Field(None, ge=1, le=4000, description="Maximum tokens in response")
        temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
        
        class Config:
            schema_extra = {
                "example": {
                    "message": "Analyze the temperature control loop TIC-101",
                    "request_type": "analysis",
                    "context": {
                        "system": "distillation_column",
                        "priority": "high"
                    },
                    "stream": False
                }
            }
    
    class ChatResponse(BaseModel):
        """Chat response model"""
        response: str = Field(..., description="AI assistant response")
        conversation_id: str = Field(..., description="Conversation ID")
        message_id: str = Field(..., description="Unique message ID")
        request_type: ChatRequestType = Field(..., description="Type of request processed")
        processing_time: float = Field(..., description="Processing time in seconds")
        token_usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")
        metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response metadata")
        
        class Config:
            schema_extra = {
                "example": {
                    "response": "I've analyzed temperature control loop TIC-101. The current tuning shows...",
                    "conversation_id": "conv_123456789",
                    "message_id": "msg_987654321",
                    "request_type": "analysis",
                    "processing_time": 1.25,
                    "token_usage": {
                        "prompt_tokens": 150,
                        "completion_tokens": 300,
                        "total_tokens": 450
                    }
                }
            }
    
    class ConversationHistory(BaseModel):
        """Conversation history model"""
        conversation_id: str
        messages: List[Message]
        created_at: datetime
        updated_at: datetime
        metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class ErrorDetail(BaseModel):
        """Error detail model"""
        error_code: str
        message: str
        details: Optional[Dict[str, Any]] = None
        timestamp: datetime = Field(default_factory=datetime.now)
    
    class HealthResponse(BaseModel):
        """Health check response"""
        status: str
        timestamp: datetime
        version: str
        components: Dict[str, str]
        uptime_seconds: float

# Rate limiting middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for API endpoints"""
    
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        cutoff_time = current_time - 60  # 1 minute ago
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if req_time > cutoff_time
            ]
        
        # Check rate limit
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        if len(self.requests[client_ip]) >= self.calls_per_minute:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response

class ChatAPI:
    """
    Main Chat API class providing RESTful endpoints for LLM interaction
    """
    
    def __init__(self):
        """Initialize Chat API"""
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for Chat API")
            
        self.app = FastAPI(
            title="PLC-GBT Chat API",
            description="RESTful API for Industrial Control System AI Assistant",
            version="23.5.0",
            docs_url="/api/v1/docs",
            redoc_url="/api/v1/redoc"
        )
        
        # Initialize components
        try:
            self.llm_service = get_llm_service()
            self.conversation_manager = ConversationManager()
            self.task_executor = TaskExecutor()
            self.task_planner = TaskPlanner()
            self.jwt_manager = get_jwt_manager()
            self.rbac_manager = get_rbac_manager()
        except Exception as e:
            logger.warning(f"Some components not available: {e}")
            self.llm_service = None
        
        # Conversation storage (in production, use database)
        self.conversations: Dict[str, List[Message]] = {}
        self.start_time = time.time()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_middleware(self):
        """Setup API middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://localhost:8080"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Rate limiting
        self.app.add_middleware(RateLimitMiddleware, calls_per_minute=100)
        
        # Trusted hosts
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.plc-gbt.com"]
        )
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/api/v1/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now(),
                version="23.5.0",
                components={
                    "llm_service": "available" if self.llm_service else "unavailable",
                    "conversation_manager": "available",
                    "task_executor": "available",
                    "task_planner": "available"
                },
                uptime_seconds=time.time() - self.start_time
            )
        
        @self.app.post("/api/v1/chat", response_model=ChatResponse)
        async def chat(
            request: ChatRequest,
            background_tasks: BackgroundTasks,
            current_user: Dict[str, Any] = Depends(self._get_current_user)
        ):
            """Main chat endpoint"""
            start_time = time.time()
            
            try:
                # Generate conversation ID if not provided
                conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:12]}"
                message_id = f"msg_{uuid.uuid4().hex[:12]}"
                
                # Process message
                if request.stream:
                    return StreamingResponse(
                        self._stream_chat_response(request, conversation_id, message_id, current_user),
                        media_type="text/plain"
                    )
                else:
                    response_text = await self._process_chat_message(
                        request, conversation_id, current_user
                    )
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Create response
                response = ChatResponse(
                    response=response_text,
                    conversation_id=conversation_id,
                    message_id=message_id,
                    request_type=request.request_type,
                    processing_time=processing_time,
                    token_usage={
                        "prompt_tokens": len(request.message.split()) * 1.3,  # Approximate
                        "completion_tokens": len(response_text.split()) * 1.3,
                        "total_tokens": len((request.message + response_text).split()) * 1.3
                    },
                    metadata={
                        "user_id": current_user.get("user_id"),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                # Store conversation
                background_tasks.add_task(self._store_conversation, conversation_id, request, response)
                
                return response
                
            except Exception as e:
                logger.error(f"Error in chat endpoint: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing chat request: {str(e)}"
                )
        
        @self.app.get("/api/v1/conversations/{conversation_id}", response_model=ConversationHistory)
        async def get_conversation(
            conversation_id: str,
            current_user: Dict[str, Any] = Depends(self._get_current_user)
        ):
            """Get conversation history"""
            if conversation_id not in self.conversations:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            messages = self.conversations[conversation_id]
            return ConversationHistory(
                conversation_id=conversation_id,
                messages=messages,
                created_at=messages[0].timestamp if messages else datetime.now(),
                updated_at=messages[-1].timestamp if messages else datetime.now(),
                metadata={"user_id": current_user.get("user_id")}
            )
        
        @self.app.delete("/api/v1/conversations/{conversation_id}")
        async def delete_conversation(
            conversation_id: str,
            current_user: Dict[str, Any] = Depends(self._get_current_user)
        ):
            """Delete conversation"""
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
                return {"message": "Conversation deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        
        @self.app.get("/api/v1/conversations")
        async def list_conversations(
            current_user: Dict[str, Any] = Depends(self._get_current_user)
        ):
            """List user conversations"""
            user_conversations = []
            for conv_id, messages in self.conversations.items():
                if messages:
                    user_conversations.append({
                        "conversation_id": conv_id,
                        "message_count": len(messages),
                        "last_message": messages[-1].timestamp,
                        "preview": messages[-1].content[:100] + "..." if len(messages[-1].content) > 100 else messages[-1].content
                    })
            
            return {"conversations": user_conversations}
    
    async def _get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Get current authenticated user"""
        try:
            if not self.jwt_manager:
                # For development - allow access without authentication
                return {"user_id": "dev_user", "role": "admin"}
                
            token = credentials.credentials
            payload = self.jwt_manager.decode_token(token)
            return payload
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def _process_chat_message(
        self, 
        request: ChatRequest, 
        conversation_id: str, 
        user: Dict[str, Any]
    ) -> str:
        """Process chat message and return response"""
        try:
            if not self.llm_service:
                return "LLM service not available - using mock response for API testing"
            
            # Create application context
            app_context = ApplicationContext(
                user_input=request.message,
                conversation_history=self._get_conversation_context(conversation_id),
                system_state=request.context,
                metadata={
                    "conversation_id": conversation_id,
                    "user_id": user.get("user_id"),
                    "request_type": request.request_type.value
                }
            )
            
            # Create LLM request
            llm_request = LLMRequest(
                request_type=LLMRequestType.CHAT,
                prompt=request.message,
                context=app_context,
                metadata={
                    "api_request": True,
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature
                }
            )
            
            # Send to LLM service
            response = await self.llm_service.send_request(llm_request)
            
            if response and response.content:
                return response.content
            else:
                return "No response received from AI assistant"
                
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return f"Error processing request: {str(e)}"
    
    async def _stream_chat_response(
        self,
        request: ChatRequest,
        conversation_id: str,
        message_id: str,
        user: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Stream chat response for real-time interaction"""
        try:
            # Simulate streaming response (in production, integrate with streaming LLM API)
            response_text = await self._process_chat_message(request, conversation_id, user)
            
            # Stream response word by word
            words = response_text.split()
            for i, word in enumerate(words):
                if i == 0:
                    yield word
                else:
                    yield f" {word}"
                
                # Small delay for streaming effect
                await asyncio.sleep(0.05)
                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def _get_conversation_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation context for LLM"""
        if conversation_id not in self.conversations:
            return []
        
        messages = self.conversations[conversation_id]
        context = []
        
        # Get last 10 messages for context
        for msg in messages[-10:]:
            context.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            })
        
        return context
    
    async def _store_conversation(
        self,
        conversation_id: str,
        request: ChatRequest,
        response: ChatResponse
    ):
        """Store conversation message (background task)"""
        try:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            
            # Add user message
            user_message = Message(
                role=MessageRole.USER,
                content=request.message,
                metadata={"request_type": request.request_type.value}
            )
            
            # Add assistant response
            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content=response.response,
                metadata={
                    "message_id": response.message_id,
                    "processing_time": response.processing_time,
                    "token_usage": response.token_usage
                }
            )
            
            self.conversations[conversation_id].extend([user_message, assistant_message])
            
            # Limit conversation history (keep last 100 messages)
            if len(self.conversations[conversation_id]) > 100:
                self.conversations[conversation_id] = self.conversations[conversation_id][-100:]
                
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")

# Factory function
def create_chat_api() -> ChatAPI:
    """Create and return Chat API instance"""
    return ChatAPI()

# Global app instance for ASGI
chat_api = create_chat_api() if FASTAPI_AVAILABLE else None
app = chat_api.app if chat_api else None

if __name__ == "__main__":
    # Development server
    if FASTAPI_AVAILABLE:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    else:
        print("FastAPI not available - cannot start server") 