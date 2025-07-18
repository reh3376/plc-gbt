"""
LLM Service Layer
Phase 23.1.2: OpenAI API Integration with Fine-tuned Model

Provides robust service layer for interacting with the fine-tuned Industrial Control Theory LLM
with comprehensive error handling, retry logic, token management, and cost tracking.
"""

import asyncio
import aiohttp
import time
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import asdict
import openai
from openai import AsyncOpenAI

from . import (
    LLM_CONFIG, LLMRequest, LLMResponse, LLMRequestType, LLMResponseStatus,
    ConversationMessage, ConversationRole, ApplicationContext,
    validate_llm_response, estimate_token_count, optimize_context_for_model
)

logger = logging.getLogger(__name__)

class LLMServiceError(Exception):
    """Custom exception for LLM service errors"""
    def __init__(self, message: str, error_code: str = None, retry_after: int = None):
        super().__init__(message)
        self.error_code = error_code
        self.retry_after = retry_after

class TokenManager:
    """Manages token counting and limits"""
    
    def __init__(self):
        self.daily_tokens = 0
        self.minute_tokens = 0
        self.daily_requests = 0
        self.minute_requests = 0
        self.last_minute_reset = time.time()
        self.last_daily_reset = time.time()
        
    def check_limits(self, estimated_tokens: int) -> bool:
        """Check if request would exceed rate limits"""
        current_time = time.time()
        
        # Reset minute counters
        if current_time - self.last_minute_reset >= 60:
            self.minute_tokens = 0
            self.minute_requests = 0
            self.last_minute_reset = current_time
            
        # Reset daily counters  
        if current_time - self.last_daily_reset >= 86400:
            self.daily_tokens = 0
            self.daily_requests = 0
            self.last_daily_reset = current_time
            
        # Check limits
        if (self.minute_tokens + estimated_tokens > LLM_CONFIG["rate_limits"]["tokens_per_minute"] or
            self.minute_requests >= LLM_CONFIG["rate_limits"]["requests_per_minute"] or
            self.daily_requests >= LLM_CONFIG["rate_limits"]["requests_per_day"]):
            return False
            
        return True
    
    def update_usage(self, tokens_used: int):
        """Update token usage counters"""
        self.minute_tokens += tokens_used
        self.daily_tokens += tokens_used
        self.minute_requests += 1
        self.daily_requests += 1

class CostTracker:
    """Tracks API costs and usage"""
    
    def __init__(self):
        self.total_cost = 0.0
        self.total_tokens = 0
        self.total_requests = 0
        self.cost_per_token = 0.003 / 1000  # GPT-4 pricing per token
        self.session_start = datetime.now(timezone.utc)
        
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for a request"""
        # Fine-tuned model pricing (approximate)
        prompt_cost = prompt_tokens * 0.003 / 1000
        completion_cost = completion_tokens * 0.006 / 1000
        return prompt_cost + completion_cost
    
    def update_costs(self, prompt_tokens: int, completion_tokens: int):
        """Update cost tracking"""
        cost = self.calculate_cost(prompt_tokens, completion_tokens)
        self.total_cost += cost
        self.total_tokens += prompt_tokens + completion_tokens
        self.total_requests += 1
        
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage and cost summary"""
        session_duration = datetime.now(timezone.utc) - self.session_start
        return {
            "total_cost": round(self.total_cost, 4),
            "total_tokens": self.total_tokens,
            "total_requests": self.total_requests,
            "session_duration": str(session_duration),
            "average_cost_per_request": round(self.total_cost / max(1, self.total_requests), 4),
            "tokens_per_request": round(self.total_tokens / max(1, self.total_requests), 1)
        }

class LLMService:
    """Main LLM service for API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise LLMServiceError("OpenAI API key not found")
            
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.token_manager = TokenManager()
        self.cost_tracker = CostTracker()
        self.request_history: List[Dict[str, Any]] = []
        
    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """Send request to LLM with retry logic"""
        request_id = f"req_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            # Prepare messages for API
            api_messages = self._prepare_messages(request.messages)
            
            # Estimate tokens
            estimated_tokens = sum(estimate_token_count(msg["content"]) for msg in api_messages)
            estimated_tokens += request.max_tokens or LLM_CONFIG["max_tokens"]
            
            # Check rate limits
            if not self.token_manager.check_limits(estimated_tokens):
                return LLMResponse(
                    status=LLMResponseStatus.RATE_LIMITED,
                    content="Rate limit exceeded",
                    request_id=request_id,
                    model_used=request.model_override or LLM_CONFIG["model_id"]
                )
            
            # Make API request with retries
            response_data = await self._make_api_request_with_retry(
                messages=api_messages,
                model=request.model_override or LLM_CONFIG["model_id"],
                temperature=request.temperature or LLM_CONFIG["temperature"],
                max_tokens=request.max_tokens or LLM_CONFIG["max_tokens"],
                timeout=request.timeout or LLM_CONFIG["request_timeout"]
            )
            
            # Process response
            response_content = response_data.choices[0].message.content
            usage = response_data.usage
            
            # Update tracking
            self.token_manager.update_usage(usage.total_tokens)
            self.cost_tracker.update_costs(usage.prompt_tokens, usage.completion_tokens)
            
            # Validate response if requested
            validation_results = {}
            if request.validate_response:
                validation_results = validate_llm_response(response_content, request.request_type)
            
            # Create response object
            response = LLMResponse(
                status=LLMResponseStatus.SUCCESS,
                content=response_content,
                request_id=request_id,
                model_used=response_data.model,
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                processing_time=time.time() - start_time,
                metadata=request.metadata,
                validation_results=validation_results,
                confidence_score=validation_results.get("confidence", 1.0)
            )
            
            # Log request
            self._log_request(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM request failed: {str(e)}")
            return LLMResponse(
                status=LLMResponseStatus.ERROR,
                content=f"Request failed: {str(e)}",
                request_id=request_id,
                model_used=request.model_override or LLM_CONFIG["model_id"],
                processing_time=time.time() - start_time
            )
    
    async def _make_api_request_with_retry(self, **kwargs) -> Any:
        """Make API request with exponential backoff retry"""
        max_retries = LLM_CONFIG["max_retries"]
        backoff_factor = LLM_CONFIG["backoff_factor"]
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.chat.completions.create(**kwargs)
                return response
                
            except openai.RateLimitError as e:
                if attempt == max_retries:
                    raise LLMServiceError("Rate limit exceeded after all retries", "rate_limit")
                
                wait_time = backoff_factor ** attempt
                logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}")
                await asyncio.sleep(wait_time)
                
            except openai.APITimeoutError as e:
                if attempt == max_retries:
                    raise LLMServiceError("Request timeout after all retries", "timeout")
                
                wait_time = backoff_factor ** attempt
                logger.warning(f"Timeout, retrying in {wait_time}s (attempt {attempt + 1})")
                await asyncio.sleep(wait_time)
                
            except openai.APIError as e:
                if attempt == max_retries:
                    raise LLMServiceError(f"API error: {str(e)}", "api_error")
                
                wait_time = backoff_factor ** attempt
                logger.warning(f"API error, retrying in {wait_time}s: {str(e)}")
                await asyncio.sleep(wait_time)
                
    def _prepare_messages(self, messages: List[ConversationMessage]) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI API format"""
        api_messages = []
        for msg in messages:
            api_msg = {
                "role": msg.role.value,
                "content": msg.content
            }
            if msg.function_call:
                api_msg["function_call"] = msg.function_call
            api_messages.append(api_msg)
        return api_messages
    
    def _log_request(self, request: LLMRequest, response: LLMResponse):
        """Log request and response for debugging"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": response.request_id,
            "request_type": request.request_type.value,
            "model": response.model_used,
            "status": response.status.value,
            "processing_time": response.processing_time,
            "usage": response.usage,
            "validation_score": response.confidence_score
        }
        
        self.request_history.append(log_entry)
        
        # Keep only last 100 requests in memory
        if len(self.request_history) > 100:
            self.request_history = self.request_history[-100:]
    
    async def chat_completion(
        self,
        messages: List[ConversationMessage],
        context: Optional[ApplicationContext] = None,
        **kwargs
    ) -> LLMResponse:
        """Simplified chat completion interface"""
        request = LLMRequest(
            request_type=LLMRequestType.CHAT,
            messages=messages,
            context=asdict(context) if context else {},
            **kwargs
        )
        return await self.send_request(request)
    
    async def generate_command(
        self,
        user_input: str,
        context: ApplicationContext,
        **kwargs
    ) -> LLMResponse:
        """Generate CLI command from natural language"""
        system_msg = ConversationMessage(
            role=ConversationRole.SYSTEM,
            content=f"""You are an expert CLI command generator for the PLC-GBT application.
            
Available commands: {context.available_commands[:20]}  # Show first 20
Current directory: {context.current_directory}
Active schemas: {context.active_schemas}

Generate precise CLI commands for the user's request. Always explain what the command does."""
        )
        
        user_msg = ConversationMessage(
            role=ConversationRole.USER,
            content=user_input
        )
        
        request = LLMRequest(
            request_type=LLMRequestType.COMMAND_GENERATION,
            messages=[system_msg, user_msg],
            context=asdict(context),
            **kwargs
        )
        
        return await self.send_request(request)
    
    async def analyze_performance(
        self,
        data: Dict[str, Any],
        context: ApplicationContext,
        **kwargs
    ) -> LLMResponse:
        """Analyze control loop performance"""
        system_msg = ConversationMessage(
            role=ConversationRole.SYSTEM,
            content="""You are an expert in industrial control theory and PID tuning.
            Analyze the provided control loop data and provide detailed insights on:
            - Performance metrics and trends
            - Tuning recommendations
            - Optimization opportunities
            - Potential issues or concerns"""
        )
        
        data_msg = ConversationMessage(
            role=ConversationRole.USER,
            content=f"Please analyze this control loop data: {json.dumps(data, indent=2)}"
        )
        
        request = LLMRequest(
            request_type=LLMRequestType.ANALYSIS,
            messages=[system_msg, data_msg],
            context=asdict(context),
            **kwargs
        )
        
        return await self.send_request(request)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and statistics"""
        return {
            "service_status": "running",
            "model_id": LLM_CONFIG["model_id"],
            "api_key_configured": bool(self.api_key),
            "usage_summary": self.cost_tracker.get_usage_summary(),
            "rate_limits": {
                "minute_tokens": self.token_manager.minute_tokens,
                "daily_tokens": self.token_manager.daily_tokens,
                "minute_requests": self.token_manager.minute_requests,
                "daily_requests": self.token_manager.daily_requests
            },
            "recent_requests": len(self.request_history),
            "configuration": {
                "max_tokens": LLM_CONFIG["max_tokens"],
                "temperature": LLM_CONFIG["temperature"],
                "timeout": LLM_CONFIG["request_timeout"],
                "max_retries": LLM_CONFIG["max_retries"]
            }
        }
    
    async def health_check(self) -> bool:
        """Check if LLM service is healthy"""
        try:
            test_msg = ConversationMessage(
                role=ConversationRole.USER,
                content="Hello, can you confirm you're working?"
            )
            
            request = LLMRequest(
                request_type=LLMRequestType.CHAT,
                messages=[test_msg],
                max_tokens=50
            )
            
            response = await self.send_request(request)
            return response.status == LLMResponseStatus.SUCCESS
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

# Singleton service instance
_llm_service: Optional[LLMService] = None

def get_llm_service(api_key: Optional[str] = None) -> LLMService:
    """Get singleton LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService(api_key)
    return _llm_service

async def quick_chat(message: str, context: Optional[ApplicationContext] = None) -> str:
    """Quick chat interface for simple interactions"""
    service = get_llm_service()
    
    msg = ConversationMessage(
        role=ConversationRole.USER,
        content=message
    )
    
    response = await service.chat_completion([msg], context)
    return response.content if response.status == LLMResponseStatus.SUCCESS else "Error in response"

# Export main components
__all__ = [
    "LLMService",
    "LLMServiceError", 
    "TokenManager",
    "CostTracker",
    "get_llm_service",
    "quick_chat"
] 