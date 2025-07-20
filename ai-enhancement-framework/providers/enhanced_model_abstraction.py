#!/usr/bin/env python3
"""
🤖 Enhanced Model Abstraction Layer - AI Enhancement Framework
Advanced Model Provider Abstraction with Multi-Model Support

This module implements comprehensive model abstraction layer including:
- Abstract Model Provider Interface with unified patterns for AI models
- OpenAI Provider Implementation with current production model integration
- Local Model Provider Framework for future support of local LLMs
- Model Factory Pattern for dynamic model instantiation and management
- Model Health Monitoring with performance and availability tracking
- Configuration Management with model-specific settings and capabilities
- Token Management with usage tracking and cost optimization
- Model Switching Logic with dynamic model selection based on requirements
- Performance Benchmarking for model comparison and optimization
- Fallback Mechanisms with graceful degradation when models unavailable

Following AI Task Orchestrator methodology for systematic model abstraction.

Author: AI Enhancement Framework
Created: 2025-01-17
Updated: 2025-01-17 (Phase 17.3.4 Integration)
Dependencies: openai, transformers (future), existing provider framework
"""

import os
import sys
import json
import time
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Protocol, AsyncGenerator
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import hashlib
from contextlib import asynccontextmanager
import weakref

# OpenAI imports with availability checking
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Local model imports (future support)
try:
    # Placeholder for future local model libraries
    # import transformers
    # import torch
    # import llama_cpp
    LOCAL_MODEL_LIBRARIES_AVAILABLE = False
except ImportError:
    LOCAL_MODEL_LIBRARIES_AVAILABLE = False

# Import existing framework components
try:
    from .provider_framework import BaseProvider, ProviderConfig, ProviderStatus
    EXISTING_PROVIDER_AVAILABLE = True
except ImportError:
    EXISTING_PROVIDER_AVAILABLE = False
    
    # Define minimal compatibility classes
    class ProviderStatus(Enum):
        HEALTHY = "healthy"
        DEGRADED = "degraded"
        UNAVAILABLE = "unavailable"
        UNKNOWN = "unknown"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Model Abstraction Core Types and Enums
# ============================================================================

class ModelType(Enum):
    """Supported model types"""
    OPENAI_GPT4O = "gpt-4o"
    OPENAI_GPT4O_MINI = "gpt-4o-mini"
    OPENAI_GPT35_TURBO = "gpt-3.5-turbo"
    OPENAI_FINE_TUNED = "fine-tuned"
    LOCAL_LLAMA = "local-llama"
    LOCAL_MISTRAL = "local-mistral"
    LOCAL_CUSTOM = "local-custom"

class ModelCapability(Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    MATHEMATICS = "mathematics"
    EMBEDDINGS = "embeddings"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    AUDIO = "audio"

class ModelStatus(Enum):
    """Model availability status"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"

class ModelProvider(Enum):
    """Model provider types"""
    OPENAI = "openai"
    LOCAL = "local"
    ANTHROPIC = "anthropic"  # Future support
    GOOGLE = "google"        # Future support

@dataclass
class ModelConfig:
    """Configuration for model providers"""
    model_type: ModelType
    model_name: str
    provider: ModelProvider
    
    # Authentication
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    organization: Optional[str] = None
    
    # Model settings
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Capabilities
    capabilities: List[ModelCapability] = field(default_factory=list)
    
    # Performance settings
    max_requests_per_minute: int = 60
    max_tokens_per_minute: int = 40000
    request_timeout: int = 60
    
    # Cost tracking
    cost_per_token_input: float = 0.0
    cost_per_token_output: float = 0.0
    
    # Fallback settings
    enable_fallback: bool = True
    fallback_model: Optional[str] = None
    
    # Local model settings (for future use)
    model_path: Optional[str] = None
    device: str = "cpu"
    quantization: Optional[str] = None

@dataclass
class ModelMetrics:
    """Metrics for model performance tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Token usage
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    
    # Performance
    average_response_time: float = 0.0
    last_response_time: float = 0.0
    peak_response_time: float = 0.0
    
    # Cost tracking
    total_cost: float = 0.0
    cost_per_request: float = 0.0
    
    # Error tracking
    error_rate: float = 0.0
    last_error: Optional[str] = None
    rate_limit_hits: int = 0
    
    # Status tracking
    uptime: timedelta = field(default_factory=lambda: timedelta(0))
    last_health_check: Optional[datetime] = None

@dataclass
class ModelRequest:
    """Request structure for model operations"""
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    stream: bool = False
    
    # Function calling (for supported models)
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Union[str, Dict[str, str]]] = None
    
    # Metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Context
    system_message: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

@dataclass
class ModelResponse:
    """Response structure for model operations"""
    content: str
    finish_reason: str
    
    # Token usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    # Metadata
    model_used: str = ""
    response_time: float = 0.0
    cost: float = 0.0
    request_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Function calling results
    function_calls: Optional[List[Dict[str, Any]]] = None
    
    # Quality metrics
    confidence_score: Optional[float] = None
    safety_score: Optional[float] = None

# ============================================================================
# Model Provider Interface
# ============================================================================

class ModelProvider(ABC):
    """Abstract base class for model providers"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.metrics = ModelMetrics()
        self.client = None
        self.lock = threading.RLock()
        self.health_check_task: Optional[asyncio.Task] = None
        self.shutdown_event = threading.Event()
        self.start_time = datetime.now()
        
        logger.info(f"{self.__class__.__name__} provider initialized for {config.model_name}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the model provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> ModelStatus:
        """Check model health and availability"""
        pass
    
    @abstractmethod
    async def generate_text(self, request: ModelRequest) -> ModelResponse:
        """Generate text using the model"""
        pass
    
    @abstractmethod
    async def generate_stream(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Generate text stream using the model"""
        pass
    
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        pass
    
    @abstractmethod
    async def close(self):
        """Close model provider and cleanup resources"""
        pass
    
    def has_capability(self, capability: ModelCapability) -> bool:
        """Check if model has specific capability"""
        return capability in self.config.capabilities
    
    async def get_metrics(self) -> ModelMetrics:
        """Get current model metrics"""
        with self.lock:
            self.metrics.uptime = datetime.now() - self.start_time
            return self.metrics
    
    def _update_metrics(self, success: bool, input_tokens: int, output_tokens: int,
                       response_time: float, cost: float = 0.0, error: Optional[str] = None):
        """Update model metrics"""
        with self.lock:
            self.metrics.total_requests += 1
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
                self.metrics.last_error = error
            
            # Update token metrics
            self.metrics.total_input_tokens += input_tokens
            self.metrics.total_output_tokens += output_tokens
            
            # Update performance metrics
            self.metrics.last_response_time = response_time
            if response_time > self.metrics.peak_response_time:
                self.metrics.peak_response_time = response_time
            
            # Calculate rolling average (simplified)
            total_time = self.metrics.average_response_time * (self.metrics.total_requests - 1)
            self.metrics.average_response_time = (total_time + response_time) / self.metrics.total_requests
            
            # Update cost metrics
            self.metrics.total_cost += cost
            if self.metrics.total_requests > 0:
                self.metrics.cost_per_request = self.metrics.total_cost / self.metrics.total_requests
            
            # Calculate error rate
            if self.metrics.total_requests > 0:
                self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests

    async def _perform_health_check(self):
        """Background health check task"""
        while not self.shutdown_event.is_set():
            try:
                status = await self.health_check()
                with self.lock:
                    self.metrics.last_health_check = datetime.now()
                
                logger.debug(f"{self.__class__.__name__} health check: {status.value}")
                
            except Exception as e:
                logger.warning(f"Health check failed for {self.__class__.__name__}: {str(e)}")
            
            await asyncio.sleep(60)  # Health check every minute

# ============================================================================
# OpenAI Provider Implementation
# ============================================================================

class OpenAIProvider(ModelProvider):
    """OpenAI model provider implementation"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.openai_client = None
        
    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            if not OPENAI_AVAILABLE:
                logger.error("OpenAI library not available")
                return False
            
            if not self.config.api_key:
                logger.error("OpenAI API key not provided")
                return False
            
            # Initialize OpenAI client
            self.openai_client = AsyncOpenAI(
                api_key=self.config.api_key,
                organization=self.config.organization,
                base_url=self.config.api_base,
                timeout=self.config.request_timeout
            )
            
            # Test connection with a simple request
            test_response = await self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            
            # Start health monitoring
            self.health_check_task = asyncio.create_task(self._perform_health_check())
            
            logger.info(f"✅ OpenAI provider initialized successfully for {self.config.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenAI provider initialization failed: {str(e)}")
            return False
    
    async def health_check(self) -> ModelStatus:
        """Check OpenAI model health"""
        try:
            if not self.openai_client:
                return ModelStatus.UNAVAILABLE
            
            start_time = time.time()
            
            # Simple health check request
            response = await self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": "health check"}],
                max_tokens=1
            )
            
            response_time = time.time() - start_time
            
            if response_time > 5.0:  # Slow response
                return ModelStatus.DEGRADED
            
            return ModelStatus.AVAILABLE
            
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str:
                return ModelStatus.RATE_LIMITED
            else:
                return ModelStatus.UNAVAILABLE
    
    async def generate_text(self, request: ModelRequest) -> ModelResponse:
        """Generate text using OpenAI model"""
        start_time = time.time()
        
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            # Prepare messages
            messages = []
            
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            
            if request.conversation_history:
                messages.extend(request.conversation_history)
            
            messages.append({"role": "user", "content": request.prompt})
            
            # Prepare request parameters
            params = {
                "model": self.config.model_name,
                "messages": messages,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "top_p": request.top_p or self.config.top_p,
                "frequency_penalty": request.frequency_penalty or self.config.frequency_penalty,
                "presence_penalty": request.presence_penalty or self.config.presence_penalty,
            }
            
            if request.stop:
                params["stop"] = request.stop
            
            if request.functions:
                params["functions"] = request.functions
                if request.function_call:
                    params["function_call"] = request.function_call
            
            # Make API request
            response = await self.openai_client.chat.completions.create(**params)
            
            response_time = time.time() - start_time
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content or ""
            finish_reason = choice.finish_reason
            
            # Calculate cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            cost = (input_tokens * self.config.cost_per_token_input + 
                   output_tokens * self.config.cost_per_token_output)
            
            # Update metrics
            self._update_metrics(True, input_tokens, output_tokens, response_time, cost)
            
            # Handle function calls
            function_calls = None
            if hasattr(choice.message, 'function_call') and choice.message.function_call:
                function_calls = [choice.message.function_call]
            
            return ModelResponse(
                content=content,
                finish_reason=finish_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                model_used=self.config.model_name,
                response_time=response_time,
                cost=cost,
                request_id=request.request_id,
                function_calls=function_calls
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            
            # Update metrics for failure
            self._update_metrics(False, 0, 0, response_time, 0.0, error_msg)
            
            # Check for rate limiting
            if "rate limit" in error_msg.lower():
                with self.lock:
                    self.metrics.rate_limit_hits += 1
            
            return ModelResponse(
                content="",
                finish_reason="error",
                model_used=self.config.model_name,
                response_time=response_time,
                request_id=request.request_id
            )
    
    async def generate_stream(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Generate text stream using OpenAI model"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            # Prepare messages (similar to generate_text)
            messages = []
            
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            
            if request.conversation_history:
                messages.extend(request.conversation_history)
            
            messages.append({"role": "user", "content": request.prompt})
            
            # Prepare streaming request
            params = {
                "model": self.config.model_name,
                "messages": messages,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "stream": True
            }
            
            # Stream response
            stream = await self.openai_client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Streaming failed: {str(e)}")
            yield f"Error: {str(e)}"
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",  # Default embedding model
                input=texts
            )
            
            return [embedding.embedding for embedding in response.data]
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return []
    
    async def close(self):
        """Close OpenAI provider"""
        self.shutdown_event.set()
        
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
        
        if self.openai_client:
            await self.openai_client.close()
        
        logger.info("✅ OpenAI provider closed")

# ============================================================================
# Local Model Provider (Future Implementation)
# ============================================================================

class LocalModelProvider(ModelProvider):
    """Local model provider implementation (future support)"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.model = None
        self.tokenizer = None
    
    async def initialize(self) -> bool:
        """Initialize local model"""
        logger.warning("Local model support not yet implemented")
        return False
    
    async def health_check(self) -> ModelStatus:
        """Check local model health"""
        if self.model is None:
            return ModelStatus.UNAVAILABLE
        return ModelStatus.AVAILABLE
    
    async def generate_text(self, request: ModelRequest) -> ModelResponse:
        """Generate text using local model"""
        raise NotImplementedError("Local model support not yet implemented")
    
    async def generate_stream(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Generate text stream using local model"""
        raise NotImplementedError("Local model support not yet implemented")
        yield ""  # Make it a proper generator
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model"""
        raise NotImplementedError("Local model embeddings not yet implemented")
    
    async def close(self):
        """Close local model"""
        self.shutdown_event.set()
        
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
        
        logger.info("✅ Local model provider closed")

# ============================================================================
# Model Factory
# ============================================================================

class EnhancedModelFactory:
    """Factory for creating model providers"""
    
    _provider_classes = {
        ModelType.OPENAI_GPT4O: OpenAIProvider,
        ModelType.OPENAI_GPT4O_MINI: OpenAIProvider,
        ModelType.OPENAI_GPT35_TURBO: OpenAIProvider,
        ModelType.OPENAI_FINE_TUNED: OpenAIProvider,
        ModelType.LOCAL_LLAMA: LocalModelProvider,
        ModelType.LOCAL_MISTRAL: LocalModelProvider,
        ModelType.LOCAL_CUSTOM: LocalModelProvider
    }
    
    @classmethod
    def create_provider(cls, config: ModelConfig) -> ModelProvider:
        """Create a model provider instance"""
        provider_class = cls._provider_classes.get(config.model_type)
        
        if not provider_class:
            raise ValueError(f"Unsupported model type: {config.model_type}")
        
        return provider_class(config)
    
    @classmethod
    def get_supported_models(cls) -> List[ModelType]:
        """Get list of supported model types"""
        return list(cls._provider_classes.keys())
    
    @classmethod
    def get_available_models(cls) -> Dict[ModelType, bool]:
        """Get availability status of all model types"""
        return {
            ModelType.OPENAI_GPT4O: OPENAI_AVAILABLE,
            ModelType.OPENAI_GPT4O_MINI: OPENAI_AVAILABLE,
            ModelType.OPENAI_GPT35_TURBO: OPENAI_AVAILABLE,
            ModelType.OPENAI_FINE_TUNED: OPENAI_AVAILABLE,
            ModelType.LOCAL_LLAMA: LOCAL_MODEL_LIBRARIES_AVAILABLE,
            ModelType.LOCAL_MISTRAL: LOCAL_MODEL_LIBRARIES_AVAILABLE,
            ModelType.LOCAL_CUSTOM: LOCAL_MODEL_LIBRARIES_AVAILABLE
        }

# ============================================================================
# Model Manager
# ============================================================================

class EnhancedModelManager:
    """Manager for coordinating multiple model providers with intelligent routing"""
    
    def __init__(self):
        self.providers: Dict[str, ModelProvider] = {}
        self.provider_configs: Dict[str, ModelConfig] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_providers: List[str] = []
        self.session_id = f"enhanced_model_manager_{int(time.time())}"
        self.start_time = datetime.now()
        
        logger.info(f"EnhancedModelManager initialized with session: {self.session_id}")
    
    async def add_provider(self, provider_name: str, config: ModelConfig, 
                          is_primary: bool = False) -> bool:
        """Add and initialize a model provider"""
        try:
            provider = EnhancedModelFactory.create_provider(config)
            
            if await provider.initialize():
                self.providers[provider_name] = provider
                self.provider_configs[provider_name] = config
                
                if is_primary:
                    self.primary_provider = provider_name
                elif provider_name not in self.fallback_providers:
                    self.fallback_providers.append(provider_name)
                
                logger.info(f"✅ Model provider {provider_name} added successfully")
                return True
            else:
                logger.error(f"❌ Model provider {provider_name} initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding model provider {provider_name}: {str(e)}")
            return False
    
    async def get_provider(self, provider_name: str) -> Optional[ModelProvider]:
        """Get a specific provider"""
        return self.providers.get(provider_name)
    
    async def generate_text(self, request: ModelRequest, 
                           provider_name: Optional[str] = None) -> ModelResponse:
        """Generate text with intelligent provider selection"""
        # Select provider
        if provider_name:
            provider = self.providers.get(provider_name)
            if not provider:
                return ModelResponse(
                    content="",
                    finish_reason="error",
                    request_id=request.request_id
                )
        else:
            provider = await self._select_best_provider(request)
            if not provider:
                return ModelResponse(
                    content="",
                    finish_reason="error",
                    request_id=request.request_id
                )
        
        # Try primary provider first
        try:
            response = await provider.generate_text(request)
            if response.finish_reason != "error":
                return response
        except Exception as e:
            logger.warning(f"Primary provider failed: {str(e)}")
        
        # Try fallback providers
        for fallback_name in self.fallback_providers:
            fallback_provider = self.providers.get(fallback_name)
            if fallback_provider:
                try:
                    logger.info(f"Trying fallback provider: {fallback_name}")
                    response = await fallback_provider.generate_text(request)
                    if response.finish_reason != "error":
                        return response
                except Exception as e:
                    logger.warning(f"Fallback provider {fallback_name} failed: {str(e)}")
                    continue
        
        # All providers failed
        return ModelResponse(
            content="",
            finish_reason="error",
            request_id=request.request_id
        )
    
    async def generate_stream(self, request: ModelRequest, 
                             provider_name: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Generate text stream with provider selection"""
        provider = None
        
        if provider_name:
            provider = self.providers.get(provider_name)
        else:
            provider = await self._select_best_provider(request)
        
        if provider:
            async for chunk in provider.generate_stream(request):
                yield chunk
        else:
            yield "Error: No available providers"
    
    async def _select_best_provider(self, request: ModelRequest) -> Optional[ModelProvider]:
        """Select the best available provider for the request"""
        # Check primary provider first
        if self.primary_provider:
            primary = self.providers.get(self.primary_provider)
            if primary:
                status = await primary.health_check()
                if status == ModelStatus.AVAILABLE:
                    return primary
        
        # Check fallback providers
        for fallback_name in self.fallback_providers:
            fallback = self.providers.get(fallback_name)
            if fallback:
                status = await fallback.health_check()
                if status == ModelStatus.AVAILABLE:
                    return fallback
        
        return None
    
    async def get_all_metrics(self) -> Dict[str, ModelMetrics]:
        """Get metrics from all providers"""
        metrics = {}
        
        for provider_name, provider in self.providers.items():
            try:
                metrics[provider_name] = await provider.get_metrics()
            except Exception as e:
                logger.error(f"Failed to get metrics from {provider_name}: {str(e)}")
        
        return metrics
    
    async def check_all_health(self) -> Dict[str, ModelStatus]:
        """Check health of all providers"""
        health_status = {}
        
        for provider_name, provider in self.providers.items():
            try:
                health_status[provider_name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {provider_name}: {str(e)}")
                health_status[provider_name] = ModelStatus.UNAVAILABLE
        
        return health_status
    
    async def close_all(self):
        """Close all model providers"""
        for provider_name, provider in self.providers.items():
            try:
                await provider.close()
                logger.info(f"✅ Model provider {provider_name} closed")
            except Exception as e:
                logger.error(f"❌ Error closing model provider {provider_name}: {str(e)}")
        
        self.providers.clear()
        self.provider_configs.clear()
        
        logger.info("✅ All model providers closed successfully")

# ============================================================================
# Helper Functions
# ============================================================================

def create_enhanced_model_manager_with_defaults() -> EnhancedModelManager:
    """Create model manager with default configurations"""
    return EnhancedModelManager()

async def setup_default_openai_provider(manager: EnhancedModelManager, 
                                       api_key: str,
                                       model_name: str = "gpt-4o-mini",
                                       is_primary: bool = True) -> bool:
    """Setup default OpenAI provider"""
    config = ModelConfig(
        model_type=ModelType.OPENAI_GPT4O_MINI,
        model_name=model_name,
        provider=ModelProvider.OPENAI,
        api_key=api_key,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.FUNCTION_CALLING
        ],
        cost_per_token_input=0.00015,  # Example pricing
        cost_per_token_output=0.0006   # Example pricing
    )
    
    return await manager.add_provider("openai_primary", config, is_primary)

def create_model_request(prompt: str, 
                        max_tokens: int = 1000,
                        temperature: float = 0.7,
                        system_message: Optional[str] = None) -> ModelRequest:
    """Create a standard model request"""
    return ModelRequest(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        system_message=system_message
    ) 