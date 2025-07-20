#!/usr/bin/env python3
"""
AI Enhancement Framework - Model Abstraction Layer
=================================================

Model abstraction layer for future local LLMs and model switching capabilities.
Extracted from Phase 17.3.4 implementation with enhanced framework integration.

Components:
1. Abstract Model Interface - Unified model access patterns
2. OpenAI Model Provider - Integration with OpenAI API
3. Local Model Provider - Support for local LLM deployments
4. Hugging Face Model Provider - Integration with HF models
5. Model Factory Pattern - Dynamic model instantiation
6. Model Configuration Management - Model-specific settings
7. Model Performance Monitoring - Response time and quality tracking
8. Model Switching Logic - Intelligent model selection
9. Fallback Mechanisms - Graceful degradation when models fail
10. Model Caching - Response caching for improved performance

Features:
- Unified interface across different model providers
- Automatic model switching based on availability and performance
- Response caching and performance optimization
- Token usage tracking and cost management
- Model health monitoring and circuit breaker patterns
- Configuration-driven model selection

Author: AI Enhancement Framework
Extracted from: Phase 17.3.4 PLC-GBT Implementation
Version: 1.0.0
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Protocol, TypeVar, AsyncGenerator
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor

# Model provider imports with availability checking
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Framework imports
from .provider_framework import (
    Provider, BaseProvider, ProviderConfig, ProviderType, OperationType,
    OperationRequest, OperationResult, HealthStatus, ProviderMetrics
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type definitions
ModelResponse = Dict[str, Any]
ModelInput = Union[str, List[str], Dict[str, Any]]

class ModelType(Enum):
    """Supported model types"""
    OPENAI_GPT = "openai_gpt"
    OPENAI_CHAT = "openai_chat"
    HUGGING_FACE = "hugging_face"
    LOCAL_LLM = "local_llm"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    CUSTOM_API = "custom_api"

class ModelTask(Enum):
    """Model task types"""
    TEXT_GENERATION = "text_generation"
    CHAT_COMPLETION = "chat_completion"
    CODE_GENERATION = "code_generation"
    TEXT_ANALYSIS = "text_analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    EMBEDDING = "embedding"

class ModelPriority(Enum):
    """Model priority levels"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    FALLBACK = "fallback"
    EXPERIMENTAL = "experimental"

@dataclass
class ModelConfig(ProviderConfig):
    """Extended configuration for AI models"""
    model_type: ModelType
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_path: Optional[str] = None  # For local models
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    supported_tasks: List[ModelTask] = field(default_factory=list)
    priority: ModelPriority = ModelPriority.SECONDARY
    cost_per_token: float = 0.0
    max_context_length: int = 4096
    supports_streaming: bool = False
    supports_function_calling: bool = False
    custom_headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class ModelMetrics(ProviderMetrics):
    """Extended metrics for AI models"""
    tokens_generated: int = 0
    tokens_consumed: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    quality_score: float = 0.0  # Based on user feedback
    cache_hit_rate: float = 0.0
    model_switches: int = 0
    fallback_usage: int = 0

@dataclass
class ModelRequest:
    """Model request structure"""
    task_type: ModelTask
    input_text: ModelInput
    parameters: Dict[str, Any] = field(default_factory=dict)
    system_prompt: Optional[str] = None
    context: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    functions: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelResponse:
    """Model response structure"""
    success: bool
    text: Optional[str] = None
    choices: List[str] = field(default_factory=list)
    tokens_used: int = 0
    cost: float = 0.0
    model_name: str = ""
    finish_reason: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[str] = None

class AbstractModelProvider(BaseProvider):
    """Abstract base class for AI model providers"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.model_config = config
        self.model_metrics = ModelMetrics()
        self.token_counter = 0
        self.cost_tracker = 0.0
        self.response_cache = {}
        self.cache_lock = threading.RLock()
        self.model_instance = None
        
    @abstractmethod
    async def _load_model(self) -> bool:
        """Load the AI model"""
        pass
    
    @abstractmethod
    async def _unload_model(self):
        """Unload the AI model"""
        pass
    
    @abstractmethod
    async def _generate_text(self, request: ModelRequest) -> ModelResponse:
        """Generate text using the model"""
        pass
    
    @abstractmethod
    async def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        pass
    
    async def _connect(self) -> bool:
        """Load and initialize the model"""
        return await self._load_model()
    
    async def _disconnect(self):
        """Unload the model"""
        await self._unload_model()
    
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        """Execute model operation"""
        start_time = time.time()
        
        try:
            # Convert operation request to model request
            model_request = self._convert_to_model_request(request)
            
            # Check cache first
            cache_key = self._generate_cache_key(model_request)
            cached_response = self._get_cached_response(cache_key)
            
            if cached_response:
                self.model_metrics.cache_hit_rate = (
                    self.model_metrics.cache_hit_rate * self.model_metrics.operation_count + 1
                ) / (self.model_metrics.operation_count + 1)
                
                duration_ms = (time.time() - start_time) * 1000
                return OperationResult(
                    success=True,
                    data=cached_response,
                    duration_ms=duration_ms,
                    operation_type=request.operation_type,
                    provider_name=self.config.provider_name,
                    metadata={"cached": True}
                )
            
            # Generate response
            response = await self._generate_text(model_request)
            
            # Cache successful responses
            if response.success:
                self._cache_response(cache_key, response)
            
            # Update metrics
            self._update_metrics(response, time.time() - start_time)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return OperationResult(
                success=response.success,
                data=response,
                error_message=response.error_message,
                error_code=response.error_code,
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return OperationResult(
                success=False,
                error_message=str(e),
                error_code="MODEL_ERROR",
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
    
    def _convert_to_model_request(self, request: OperationRequest) -> ModelRequest:
        """Convert operation request to model request"""
        task_type = ModelTask(request.parameters.get('task_type', ModelTask.TEXT_GENERATION.value))
        
        return ModelRequest(
            task_type=task_type,
            input_text=request.parameters.get('input_text', ''),
            parameters=request.parameters.get('parameters', {}),
            system_prompt=request.parameters.get('system_prompt'),
            context=request.parameters.get('context'),
            max_tokens=request.parameters.get('max_tokens'),
            temperature=request.parameters.get('temperature'),
            stream=request.parameters.get('stream', False),
            functions=request.parameters.get('functions'),
            metadata=request.metadata
        )
    
    def _generate_cache_key(self, request: ModelRequest) -> str:
        """Generate cache key for request"""
        key_data = {
            'task_type': request.task_type.value,
            'input_text': str(request.input_text),
            'system_prompt': request.system_prompt,
            'context': request.context,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature,
            'model_name': self.model_config.model_name
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[ModelResponse]:
        """Get cached response if available"""
        with self.cache_lock:
            return self.response_cache.get(cache_key)
    
    def _cache_response(self, cache_key: str, response: ModelResponse):
        """Cache model response"""
        with self.cache_lock:
            # Simple LRU cache implementation
            if len(self.response_cache) > 100:  # Max cache size
                # Remove oldest entries
                oldest_key = next(iter(self.response_cache))
                del self.response_cache[oldest_key]
            
            self.response_cache[cache_key] = response
    
    def _update_metrics(self, response: ModelResponse, duration: float):
        """Update model metrics"""
        self.model_metrics.operation_count += 1
        self.model_metrics.total_duration_ms += duration * 1000
        self.model_metrics.tokens_generated += response.tokens_used
        self.model_metrics.total_cost += response.cost
        self.model_metrics.last_operation_time = datetime.now()
        
        if not response.success:
            self.model_metrics.error_count += 1
            self.model_metrics.last_error_time = datetime.now()

class OpenAIProvider(AbstractModelProvider):
    """OpenAI model provider implementation"""
    
    def __init__(self, config: ModelConfig):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        super().__init__(config)
        self.client = None
        self.async_client = None
    
    async def _load_model(self) -> bool:
        """Initialize OpenAI client"""
        try:
            api_key = self.model_config.api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key required")
            
            self.async_client = AsyncOpenAI(
                api_key=api_key,
                base_url=self.model_config.api_base
            )
            
            # Test connection
            await self.async_client.models.list()
            
            logger.info(f"OpenAI provider {self.config.provider_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load OpenAI model: {e}")
            return False
    
    async def _unload_model(self):
        """Close OpenAI client"""
        if self.async_client:
            await self.async_client.close()
    
    async def _generate_text(self, request: ModelRequest) -> ModelResponse:
        """Generate text using OpenAI API"""
        try:
            if request.task_type == ModelTask.CHAT_COMPLETION:
                return await self._chat_completion(request)
            elif request.task_type == ModelTask.TEXT_GENERATION:
                return await self._text_completion(request)
            elif request.task_type == ModelTask.EMBEDDING:
                return await self._create_embedding(request)
            else:
                # Default to chat completion
                return await self._chat_completion(request)
                
        except Exception as e:
            return ModelResponse(
                success=False,
                error_message=str(e),
                error_code="OPENAI_ERROR",
                model_name=self.model_config.model_name
            )
    
    async def _chat_completion(self, request: ModelRequest) -> ModelResponse:
        """Create chat completion"""
        messages = []
        
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        
        if request.context:
            messages.append({"role": "user", "content": request.context})
        
        if isinstance(request.input_text, str):
            messages.append({"role": "user", "content": request.input_text})
        elif isinstance(request.input_text, list):
            for msg in request.input_text:
                if isinstance(msg, dict):
                    messages.append(msg)
                else:
                    messages.append({"role": "user", "content": str(msg)})
        
        response = await self.async_client.chat.completions.create(
            model=self.model_config.model_name,
            messages=messages,
            max_tokens=request.max_tokens or self.model_config.max_tokens,
            temperature=request.temperature or self.model_config.temperature,
            top_p=self.model_config.top_p,
            frequency_penalty=self.model_config.frequency_penalty,
            presence_penalty=self.model_config.presence_penalty,
            stop=self.model_config.stop_sequences or None,
            stream=request.stream,
            functions=request.functions
        )
        
        if request.stream:
            # Handle streaming response
            return await self._handle_streaming_response(response)
        else:
            # Handle regular response
            choice = response.choices[0]
            
            return ModelResponse(
                success=True,
                text=choice.message.content,
                choices=[choice.message.content],
                tokens_used=response.usage.total_tokens if response.usage else 0,
                cost=self._calculate_cost(response.usage.total_tokens if response.usage else 0),
                model_name=response.model,
                finish_reason=choice.finish_reason,
                function_call=choice.message.function_call.dict() if choice.message.function_call else None
            )
    
    async def _text_completion(self, request: ModelRequest) -> ModelResponse:
        """Create text completion (legacy)"""
        # Note: Text completion API is deprecated, convert to chat completion
        return await self._chat_completion(request)
    
    async def _create_embedding(self, request: ModelRequest) -> ModelResponse:
        """Create text embedding"""
        response = await self.async_client.embeddings.create(
            model=self.model_config.model_name,
            input=request.input_text
        )
        
        return ModelResponse(
            success=True,
            text=None,
            choices=[],
            tokens_used=response.usage.total_tokens,
            cost=self._calculate_cost(response.usage.total_tokens),
            model_name=response.model,
            metadata={"embedding": response.data[0].embedding}
        )
    
    async def _handle_streaming_response(self, response) -> ModelResponse:
        """Handle streaming response from OpenAI"""
        content_chunks = []
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content_chunks.append(chunk.choices[0].delta.content)
        
        full_content = ''.join(content_chunks)
        tokens_used = await self._estimate_tokens(full_content)
        
        return ModelResponse(
            success=True,
            text=full_content,
            choices=[full_content],
            tokens_used=tokens_used,
            cost=self._calculate_cost(tokens_used),
            model_name=self.model_config.model_name,
            metadata={"streamed": True}
        )
    
    async def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on token usage"""
        return tokens * self.model_config.cost_per_token
    
    async def _health_check_impl(self) -> HealthStatus:
        """OpenAI health check"""
        try:
            await self.async_client.models.list()
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.UNAVAILABLE
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get OpenAI provider capabilities"""
        return {
            "tasks": [task.value for task in self.model_config.supported_tasks],
            "streaming": self.model_config.supports_streaming,
            "function_calling": self.model_config.supports_function_calling,
            "max_context": self.model_config.max_context_length,
            "models": ["gpt-4", "gpt-3.5-turbo", "text-embedding-ada-002"],
            "features": ["chat", "completion", "embedding", "function_calling"]
        }

class LocalLLMProvider(AbstractModelProvider):
    """Local LLM provider for running models locally"""
    
    def __init__(self, config: ModelConfig):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers library not available. Install with: pip install transformers torch")
        
        super().__init__(config)
        self.tokenizer = None
        self.model = None
        self.pipeline = None
    
    async def _load_model(self) -> bool:
        """Load local LLM model"""
        try:
            model_path = self.model_config.model_path or self.model_config.model_name
            
            # Load in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def load_model_sync():
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForCausalLM.from_pretrained(model_path)
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device_map="auto" if self.model_config.connection_params.get("use_gpu") else None
                )
                return True
            
            with ThreadPoolExecutor() as executor:
                success = await loop.run_in_executor(executor, load_model_sync)
            
            if success:
                logger.info(f"Local LLM {self.config.provider_name} loaded successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            return False
    
    async def _unload_model(self):
        """Unload local model"""
        self.tokenizer = None
        self.model = None
        self.pipeline = None
    
    async def _generate_text(self, request: ModelRequest) -> ModelResponse:
        """Generate text using local LLM"""
        try:
            if not self.pipeline:
                raise RuntimeError("Model not loaded")
            
            # Prepare input
            if isinstance(request.input_text, str):
                input_text = request.input_text
            else:
                input_text = str(request.input_text)
            
            if request.system_prompt:
                input_text = f"{request.system_prompt}\n\n{input_text}"
            
            if request.context:
                input_text = f"{request.context}\n\n{input_text}"
            
            # Generate in thread pool
            loop = asyncio.get_event_loop()
            
            def generate_sync():
                return self.pipeline(
                    input_text,
                    max_length=request.max_tokens or self.model_config.max_tokens,
                    temperature=request.temperature or self.model_config.temperature,
                    top_p=self.model_config.top_p,
                    num_return_sequences=1,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            with ThreadPoolExecutor() as executor:
                results = await loop.run_in_executor(executor, generate_sync)
            
            if results and len(results) > 0:
                generated_text = results[0]['generated_text']
                # Remove input text from response
                if generated_text.startswith(input_text):
                    generated_text = generated_text[len(input_text):].strip()
                
                tokens_used = await self._estimate_tokens(generated_text)
                
                return ModelResponse(
                    success=True,
                    text=generated_text,
                    choices=[generated_text],
                    tokens_used=tokens_used,
                    cost=0.0,  # Local models have no API cost
                    model_name=self.model_config.model_name
                )
            else:
                return ModelResponse(
                    success=False,
                    error_message="No response generated",
                    error_code="NO_RESPONSE",
                    model_name=self.model_config.model_name
                )
                
        except Exception as e:
            return ModelResponse(
                success=False,
                error_message=str(e),
                error_code="LOCAL_LLM_ERROR",
                model_name=self.model_config.model_name
            )
    
    async def _estimate_tokens(self, text: str) -> int:
        """Estimate token count using tokenizer"""
        if self.tokenizer:
            tokens = self.tokenizer.encode(text)
            return len(tokens)
        else:
            return len(text) // 4  # Fallback estimation
    
    async def _health_check_impl(self) -> HealthStatus:
        """Local LLM health check"""
        return HealthStatus.HEALTHY if self.pipeline else HealthStatus.UNAVAILABLE
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get local LLM capabilities"""
        return {
            "tasks": [ModelTask.TEXT_GENERATION.value, ModelTask.CHAT_COMPLETION.value],
            "streaming": False,
            "function_calling": False,
            "max_context": self.model_config.max_context_length,
            "local": True,
            "cost": 0.0,
            "features": ["text_generation", "offline"]
        }

class ModelFactory:
    """Factory for creating model providers"""
    
    _providers = {
        ModelType.OPENAI_GPT: OpenAIProvider,
        ModelType.OPENAI_CHAT: OpenAIProvider,
        ModelType.LOCAL_LLM: LocalLLMProvider,
        ModelType.HUGGING_FACE: LocalLLMProvider  # Use same implementation
    }
    
    @classmethod
    def create_provider(cls, config: ModelConfig) -> AbstractModelProvider:
        """Create model provider based on configuration"""
        provider_class = cls._providers.get(config.model_type)
        
        if not provider_class:
            raise ValueError(f"Unsupported model type: {config.model_type}")
        
        return provider_class(config)
    
    @classmethod
    def register_provider(cls, model_type: ModelType, provider_class: type):
        """Register custom model provider"""
        cls._providers[model_type] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> List[ModelType]:
        """Get list of available model provider types"""
        available = []
        
        if OPENAI_AVAILABLE:
            available.extend([ModelType.OPENAI_GPT, ModelType.OPENAI_CHAT])
        if TRANSFORMERS_AVAILABLE:
            available.extend([ModelType.LOCAL_LLM, ModelType.HUGGING_FACE])
            
        return available

class ModelManager:
    """Manager for multiple AI model providers with intelligent switching"""
    
    def __init__(self):
        self.providers: Dict[str, AbstractModelProvider] = {}
        self.configs: Dict[str, ModelConfig] = {}
        self.primary_models: Dict[ModelTask, str] = {}
        self.fallback_models: Dict[ModelTask, List[str]] = {}
        self.lock = threading.RLock()
        self.performance_tracker = {}
    
    async def add_model(self, name: str, config: ModelConfig) -> bool:
        """Add and initialize a model provider"""
        try:
            provider = ModelFactory.create_provider(config)
            
            if await provider.initialize():
                with self.lock:
                    self.providers[name] = provider
                    self.configs[name] = config
                    
                    # Set as primary for supported tasks if priority is high
                    if config.priority == ModelPriority.PRIMARY:
                        for task in config.supported_tasks:
                            self.primary_models[task] = name
                    
                    # Add to fallback lists
                    for task in config.supported_tasks:
                        if task not in self.fallback_models:
                            self.fallback_models[task] = []
                        if name not in self.fallback_models[task]:
                            self.fallback_models[task].append(name)
                
                logger.info(f"Model {name} added successfully")
                return True
            else:
                logger.error(f"Failed to initialize model {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding model {name}: {e}")
            return False
    
    async def remove_model(self, name: str) -> bool:
        """Remove a model provider"""
        try:
            with self.lock:
                provider = self.providers.get(name)
                if provider:
                    await provider.cleanup()
                    del self.providers[name]
                    del self.configs[name]
                    
                    # Remove from primary models
                    for task, model_name in list(self.primary_models.items()):
                        if model_name == name:
                            del self.primary_models[task]
                    
                    # Remove from fallback lists
                    for task, models in self.fallback_models.items():
                        if name in models:
                            models.remove(name)
                    
                    logger.info(f"Model {name} removed")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error removing model {name}: {e}")
            return False
    
    async def generate_text(self, request: ModelRequest, preferred_model: str = None) -> ModelResponse:
        """Generate text using best available model"""
        # Determine which models to try
        model_candidates = self._get_model_candidates(request.task_type, preferred_model)
        
        if not model_candidates:
            return ModelResponse(
                success=False,
                error_message=f"No models available for task {request.task_type}",
                error_code="NO_MODELS_AVAILABLE"
            )
        
        # Try models in order of preference
        last_error = None
        
        for model_name in model_candidates:
            provider = self.providers.get(model_name)
            if not provider:
                continue
            
            try:
                # Convert to operation request
                operation_request = OperationRequest(
                    operation_type=OperationType.EXECUTE,
                    parameters={
                        'task_type': request.task_type.value,
                        'input_text': request.input_text,
                        'parameters': request.parameters,
                        'system_prompt': request.system_prompt,
                        'context': request.context,
                        'max_tokens': request.max_tokens,
                        'temperature': request.temperature,
                        'stream': request.stream,
                        'functions': request.functions
                    },
                    metadata=request.metadata
                )
                
                result = await provider.execute_operation(operation_request)
                
                if result.success and result.data:
                    # Track successful usage
                    self._update_performance_tracker(model_name, True, result.duration_ms)
                    return result.data
                else:
                    last_error = result.error_message
                    self._update_performance_tracker(model_name, False, result.duration_ms)
                    continue
                    
            except Exception as e:
                last_error = str(e)
                self._update_performance_tracker(model_name, False, 0)
                continue
        
        # All models failed
        return ModelResponse(
            success=False,
            error_message=f"All models failed. Last error: {last_error}",
            error_code="ALL_MODELS_FAILED"
        )
    
    def _get_model_candidates(self, task: ModelTask, preferred_model: str = None) -> List[str]:
        """Get ordered list of model candidates for a task"""
        candidates = []
        
        # Add preferred model first if specified and supports task
        if preferred_model and preferred_model in self.providers:
            config = self.configs[preferred_model]
            if task in config.supported_tasks:
                candidates.append(preferred_model)
        
        # Add primary model for task
        primary = self.primary_models.get(task)
        if primary and primary not in candidates:
            candidates.append(primary)
        
        # Add fallback models sorted by performance
        fallbacks = self.fallback_models.get(task, [])
        for model in self._sort_by_performance(fallbacks):
            if model not in candidates:
                candidates.append(model)
        
        return candidates
    
    def _sort_by_performance(self, model_names: List[str]) -> List[str]:
        """Sort models by performance metrics"""
        def performance_score(name):
            tracker = self.performance_tracker.get(name, {})
            success_rate = tracker.get('success_rate', 0.0)
            avg_response_time = tracker.get('avg_response_time', float('inf'))
            
            # Higher success rate and lower response time is better
            return success_rate - (avg_response_time / 1000)  # Normalize response time
        
        return sorted(model_names, key=performance_score, reverse=True)
    
    def _update_performance_tracker(self, model_name: str, success: bool, response_time_ms: float):
        """Update performance tracking for model"""
        if model_name not in self.performance_tracker:
            self.performance_tracker[model_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_response_time': 0.0,
                'success_rate': 0.0,
                'avg_response_time': 0.0
            }
        
        tracker = self.performance_tracker[model_name]
        tracker['total_requests'] += 1
        tracker['total_response_time'] += response_time_ms
        
        if success:
            tracker['successful_requests'] += 1
        
        tracker['success_rate'] = tracker['successful_requests'] / tracker['total_requests']
        tracker['avg_response_time'] = tracker['total_response_time'] / tracker['total_requests']
    
    async def health_check_all(self) -> Dict[str, HealthStatus]:
        """Check health of all models"""
        results = {}
        
        for name, provider in self.providers.items():
            try:
                results[name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = HealthStatus.UNAVAILABLE
        
        return results
    
    def get_model_metrics(self) -> Dict[str, ModelMetrics]:
        """Get metrics for all models"""
        return {name: provider.get_metrics() for name, provider in self.providers.items()}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            "models": list(self.providers.keys()),
            "primary_models": self.primary_models,
            "fallback_models": self.fallback_models,
            "performance_tracker": self.performance_tracker,
            "health_status": asyncio.run(self.health_check_all())
        }
    
    async def cleanup_all(self):
        """Cleanup all model providers"""
        for provider in self.providers.values():
            try:
                await provider.cleanup()
            except Exception as e:
                logger.error(f"Error during model cleanup: {e}")
        
        self.providers.clear()
        self.configs.clear()
        self.primary_models.clear()
        self.fallback_models.clear()
        self.performance_tracker.clear()

# Configuration helpers
def create_openai_config(model_name: str = "gpt-3.5-turbo", api_key: str = None,
                        max_tokens: int = 1000, temperature: float = 0.7) -> ModelConfig:
    """Create OpenAI model configuration"""
    return ModelConfig(
        provider_type=ProviderType.AI_SERVICE,
        provider_name=f"openai_{model_name}",
        model_type=ModelType.OPENAI_CHAT,
        model_name=model_name,
        api_key=api_key,
        max_tokens=max_tokens,
        temperature=temperature,
        supported_tasks=[
            ModelTask.CHAT_COMPLETION,
            ModelTask.TEXT_GENERATION,
            ModelTask.CODE_GENERATION
        ],
        supports_streaming=True,
        supports_function_calling=True,
        cost_per_token=0.0015 if "gpt-4" in model_name else 0.0005
    )

def create_local_llm_config(model_path: str, model_name: str = None) -> ModelConfig:
    """Create local LLM configuration"""
    return ModelConfig(
        provider_type=ProviderType.AI_SERVICE,
        provider_name=f"local_{model_name or Path(model_path).name}",
        model_type=ModelType.LOCAL_LLM,
        model_name=model_name or model_path,
        model_path=model_path,
        supported_tasks=[
            ModelTask.TEXT_GENERATION,
            ModelTask.CHAT_COMPLETION
        ],
        cost_per_token=0.0,  # No API cost for local models
        priority=ModelPriority.FALLBACK
    ) 