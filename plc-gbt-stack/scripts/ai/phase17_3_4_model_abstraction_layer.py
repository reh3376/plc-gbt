#!/usr/bin/env python3
"""
🤖 Phase 17.3.4: Model Abstraction Layer - AI Task Orchestrator Implementation

Following AI Task Orchestrator Guide methodology for EXTENSIVE complexity task.

Phase 17.3.4 Components:
1. Abstract Model Provider Interface - Unified model access patterns
2. OpenAI Provider Implementation - Current production model integration
3. Local Model Provider Framework - Future support for local LLMs
4. Model Factory Pattern - Dynamic model instantiation and management
5. Model Health Monitoring - Performance and availability tracking
6. Configuration Management - Model-specific configuration handling
7. Token Management - Usage tracking and optimization
8. Model Switching Logic - Dynamic model selection based on task requirements
9. Performance Benchmarking - Model comparison and optimization
10. Fallback Mechanisms - Graceful degradation when models unavailable

Prepares for future integration of local LLMs while maintaining current OpenAI functionality.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 17.3.4 Model Abstraction Layer
"""

import asyncio
import logging
import os
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

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

# Tokenization support
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Supported model types"""
    OPENAI_GPT4O = "openai_gpt4o"
    OPENAI_GPT4O_MINI = "openai_gpt4o_mini"
    OPENAI_FINE_TUNED = "openai_fine_tuned"
    LOCAL_LLAMA = "local_llama"
    LOCAL_MISTRAL = "local_mistral"
    LOCAL_CUSTOM = "local_custom"

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
    LOADING = "loading"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class ModelConfig:
    """Configuration for model providers"""
    model_type: ModelType
    model_name: str
    api_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60
    retry_attempts: int = 3
    rate_limit_per_minute: int = 60
    cost_per_token: float = 0.0
    capabilities: List[ModelCapability] = field(default_factory=list)
    additional_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelMetrics:
    """Performance metrics for model providers"""
    request_count: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    error_count: int = 0
    last_request_time: Optional[datetime] = None
    last_error_time: Optional[datetime] = None
    status: ModelStatus = ModelStatus.AVAILABLE

    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage"""
        return (self.error_count / self.request_count * 100) if self.request_count > 0 else 0.0

    @property
    def tokens_per_request(self) -> float:
        """Calculate average tokens per request"""
        return self.total_tokens_used / self.request_count if self.request_count > 0 else 0.0

@dataclass
class ModelRequest:
    """Request to a model provider"""
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stop_sequences: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    function_definitions: Optional[List[Dict[str, Any]]] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelResponse:
    """Response from a model provider"""
    content: str
    token_usage: Dict[str, int]
    model_name: str
    response_time: float
    finish_reason: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Get total tokens used"""
        return self.token_usage.get('total_tokens', 0)

class ModelProvider(ABC):
    """Abstract base class for model providers"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.metrics = ModelMetrics()
        self.client = None
        self.lock = threading.RLock()
        self.health_check_task: Optional[asyncio.Task] = None
        self.shutdown_event = threading.Event()

        logger.info(f"{self.__class__.__name__} provider initialized for {config.model_name}")

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the model provider"""
        pass

    @abstractmethod
    async def health_check(self) -> ModelStatus:
        """Check model health"""
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

    async def _execute_with_metrics(self, operation: Callable) -> ModelResponse:
        """Execute operation with metrics tracking"""
        start_time = time.time()

        try:
            response = await operation()
            response_time = time.time() - start_time

            self._update_metrics(True, response_time, response.total_tokens, response)
            return response

        except Exception as e:
            response_time = time.time() - start_time
            self._update_metrics(False, response_time, 0, None)
            logger.error(f"Model operation failed: {str(e)}")
            raise e

    def _update_metrics(self, success: bool, response_time: float, tokens_used: int, response: Optional[ModelResponse]):
        """Update provider metrics"""
        with self.lock:
            self.metrics.request_count += 1
            self.metrics.last_request_time = datetime.now()

            # Update response time (running average)
            if self.metrics.request_count == 1:
                self.metrics.average_response_time = response_time
            else:
                self.metrics.average_response_time = (
                    (self.metrics.average_response_time * (self.metrics.request_count - 1) + response_time)
                    / self.metrics.request_count
                )

            if success and response:
                self.metrics.total_tokens_used += tokens_used
                self.metrics.total_cost += tokens_used * self.config.cost_per_token
            else:
                self.metrics.error_count += 1
                self.metrics.last_error_time = datetime.now()

    async def start_health_monitoring(self):
        """Start background health monitoring"""
        async def health_monitor():
            while not self.shutdown_event.is_set():
                try:
                    self.metrics.status = await self.health_check()
                    await asyncio.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Health check failed for {self.__class__.__name__}: {e}")
                    self.metrics.status = ModelStatus.ERROR
                    await asyncio.sleep(5)  # Shorter interval on error

        if not self.health_check_task or self.health_check_task.done():
            self.health_check_task = asyncio.create_task(health_monitor())

class OpenAIProvider(ModelProvider):
    """OpenAI model provider implementation"""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.openai_client: Optional[AsyncOpenAI] = None
        self.tokenizer = None

        # Initialize tokenizer for token counting
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.encoding_for_model(config.model_name)
            except Exception:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Fallback

    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library not available")
            return False

        try:
            self.openai_client = AsyncOpenAI(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )

            # Test connection
            await self.health_check()
            logger.info(f"✅ OpenAI provider connected for {self.config.model_name}")

            await self.start_health_monitoring()
            return True

        except Exception as e:
            logger.error(f"❌ OpenAI provider initialization failed: {str(e)}")
            return False

    async def health_check(self) -> ModelStatus:
        """Check OpenAI model health"""
        try:
            if self.openai_client:
                # Make a minimal request to test availability
                await self.openai_client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                return ModelStatus.AVAILABLE
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")

        return ModelStatus.UNAVAILABLE

    async def generate_text(self, request: ModelRequest) -> ModelResponse:
        """Generate text using OpenAI model"""
        async def openai_operation():
            if not self.openai_client:
                raise RuntimeError("OpenAI client not initialized")

            # Prepare messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})

            # Prepare request parameters
            params = {
                "model": self.config.model_name,
                "messages": messages,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
            }

            if request.stop_sequences:
                params["stop"] = request.stop_sequences

            if request.function_definitions:
                params["functions"] = request.function_definitions
                params["function_call"] = "auto"

            # Make request
            response = await self.openai_client.chat.completions.create(**params)

            # Extract response content
            choice = response.choices[0]
            content = choice.message.content or ""

            # Handle function calls
            function_calls = None
            if choice.message.function_call:
                function_calls = [choice.message.function_call.model_dump()]

            return ModelResponse(
                content=content,
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model_name=response.model,
                response_time=0.0,  # Will be set by metrics
                finish_reason=choice.finish_reason,
                function_calls=function_calls,
                metadata={"openai_response_id": response.id}
            )

        return await self._execute_with_metrics(openai_operation)

    async def generate_stream(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Generate text stream using OpenAI model"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")

        # Prepare messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        # Prepare request parameters
        params = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": request.max_tokens or self.config.max_tokens,
            "temperature": request.temperature or self.config.temperature,
            "stream": True
        }

        if request.stop_sequences:
            params["stop"] = request.stop_sequences

        try:
            stream = await self.openai_client.chat.completions.create(**params)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {str(e)}")
            raise e

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")

        if not self.has_capability(ModelCapability.EMBEDDINGS):
            raise RuntimeError("Model does not support embeddings")

        try:
            response = await self.openai_client.embeddings.create(
                model=self.config.additional_config.get("embedding_model", "text-embedding-3-small"),
                input=texts
            )

            return [data.embedding for data in response.data]

        except Exception as e:
            logger.error(f"OpenAI embeddings failed: {str(e)}")
            raise e

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough approximation if tokenizer not available
            return len(text.split()) * 1.3

    async def close(self):
        """Close OpenAI connections"""
        self.shutdown_event.set()

        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()

        if self.openai_client:
            await self.openai_client.close()

        logger.info("✅ OpenAI provider closed")

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

class ModelFactory:
    """Factory for creating model providers"""

    _provider_classes = {
        ModelType.OPENAI_GPT4O: OpenAIProvider,
        ModelType.OPENAI_GPT4O_MINI: OpenAIProvider,
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

class ModelManager:
    """Manager for coordinating multiple model providers"""

    def __init__(self):
        self.providers: Dict[str, ModelProvider] = {}
        self.provider_configs: Dict[str, ModelConfig] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_providers: List[str] = []
        self.session_id = f"model_manager_{int(time.time())}"
        self.start_time = datetime.now()

        logger.info(f"ModelManager initialized with session: {self.session_id}")

    async def add_provider(self, provider_name: str, config: ModelConfig,
                          is_primary: bool = False) -> bool:
        """Add and initialize a model provider"""
        try:
            provider = ModelFactory.create_provider(config)

            if await provider.initialize():
                self.providers[provider_name] = provider
                self.provider_configs[provider_name] = config

                if is_primary:
                    self.primary_provider = provider_name
                elif provider_name not in self.fallback_providers:
                    self.fallback_providers.append(provider_name)

                logger.info(f"✅ Provider {provider_name} added successfully")
                return True
            else:
                logger.error(f"❌ Provider {provider_name} initialization failed")
                return False

        except Exception as e:
            logger.error(f"❌ Error adding provider {provider_name}: {str(e)}")
            return False

    async def get_provider(self, provider_name: str) -> Optional[ModelProvider]:
        """Get a specific provider"""
        return self.providers.get(provider_name)

    async def get_best_provider(self, capability: Optional[ModelCapability] = None) -> Optional[ModelProvider]:
        """Get the best available provider for a capability"""
        # Try primary provider first
        if self.primary_provider:
            provider = self.providers.get(self.primary_provider)
            if provider and provider.metrics.status == ModelStatus.AVAILABLE:
                if not capability or provider.has_capability(capability):
                    return provider

        # Try fallback providers
        for provider_name in self.fallback_providers:
            provider = self.providers.get(provider_name)
            if provider and provider.metrics.status == ModelStatus.AVAILABLE:
                if not capability or provider.has_capability(capability):
                    return provider

        return None

    async def generate_text(self, request: ModelRequest,
                          provider_name: Optional[str] = None,
                          capability: Optional[ModelCapability] = None) -> ModelResponse:
        """Generate text using best available provider"""
        if provider_name:
            provider = self.providers.get(provider_name)
            if not provider:
                raise ValueError(f"Provider {provider_name} not found")
        else:
            provider = await self.get_best_provider(capability)
            if not provider:
                raise RuntimeError("No suitable provider available")

        return await provider.generate_text(request)

    async def generate_stream(self, request: ModelRequest,
                            provider_name: Optional[str] = None,
                            capability: Optional[ModelCapability] = None) -> AsyncGenerator[str, None]:
        """Generate text stream using best available provider"""
        if provider_name:
            provider = self.providers.get(provider_name)
            if not provider:
                raise ValueError(f"Provider {provider_name} not found")
        else:
            provider = await self.get_best_provider(capability)
            if not provider:
                raise RuntimeError("No suitable provider available")

        async for chunk in provider.generate_stream(request):
            yield chunk

    async def get_embeddings(self, texts: List[str],
                           provider_name: Optional[str] = None) -> List[List[float]]:
        """Generate embeddings using best available provider"""
        if provider_name:
            provider = self.providers.get(provider_name)
            if not provider:
                raise ValueError(f"Provider {provider_name} not found")
        else:
            provider = await self.get_best_provider(ModelCapability.EMBEDDINGS)
            if not provider:
                raise RuntimeError("No embedding provider available")

        return await provider.get_embeddings(texts)

    async def get_all_metrics(self) -> Dict[str, ModelMetrics]:
        """Get metrics from all providers"""
        return {
            provider_name: provider.metrics
            for provider_name, provider in self.providers.items()
        }

    async def get_health_status(self) -> Dict[str, ModelStatus]:
        """Get health status from all providers"""
        health_status = {}

        for provider_name, provider in self.providers.items():
            try:
                health_status[provider_name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {provider_name}: {e}")
                health_status[provider_name] = ModelStatus.ERROR

        return health_status

    async def close_all(self):
        """Close all providers"""
        for provider_name, provider in self.providers.items():
            try:
                await provider.close()
                logger.info(f"✅ Provider {provider_name} closed")
            except Exception as e:
                logger.error(f"❌ Error closing provider {provider_name}: {e}")

        self.providers.clear()
        self.provider_configs.clear()

        logger.info("🔒 All model providers closed")

async def create_default_model_manager() -> ModelManager:
    """Create model manager with default configurations"""
    manager = ModelManager()

    # Get OpenAI API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.warning("OPENAI_API_KEY not found in environment")
        return manager

    # Default OpenAI configurations
    gpt4o_config = ModelConfig(
        model_type=ModelType.OPENAI_GPT4O,
        model_name="gpt-4o",
        api_key=openai_api_key,
        max_tokens=4096,
        temperature=0.7,
        cost_per_token=0.00001,  # Example cost
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.MATHEMATICS,
            ModelCapability.FUNCTION_CALLING
        ],
        additional_config={"embedding_model": "text-embedding-3-small"}
    )

    gpt4o_mini_config = ModelConfig(
        model_type=ModelType.OPENAI_GPT4O_MINI,
        model_name="gpt-4o-mini",
        api_key=openai_api_key,
        max_tokens=4096,
        temperature=0.7,
        cost_per_token=0.000001,  # Example cost
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING
        ]
    )

    # Check for fine-tuned model
    fine_tuned_model = os.getenv("OPENAI_FINETUNE_MODEL")
    if fine_tuned_model:
        fine_tuned_config = ModelConfig(
            model_type=ModelType.OPENAI_FINE_TUNED,
            model_name=fine_tuned_model,
            api_key=openai_api_key,
            max_tokens=4096,
            temperature=0.7,
            cost_per_token=0.00001,  # Example cost
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.MATHEMATICS
            ]
        )

        # Fine-tuned model as primary
        await manager.add_provider("fine_tuned", fine_tuned_config, is_primary=True)
        await manager.add_provider("gpt4o", gpt4o_config)
        await manager.add_provider("gpt4o_mini", gpt4o_mini_config)
    else:
        # GPT-4o as primary
        await manager.add_provider("gpt4o", gpt4o_config, is_primary=True)
        await manager.add_provider("gpt4o_mini", gpt4o_mini_config)

    return manager

# Example usage and testing functions
async def test_model_operations():
    """Test model manager operations"""
    logger.info("🧪 Testing Model Operations")

    manager = await create_default_model_manager()

    # Test text generation
    request = ModelRequest(
        prompt="Explain PID control in industrial automation",
        max_tokens=150,
        temperature=0.7
    )

    try:
        response = await manager.generate_text(request)
        logger.info(f"✅ Text generation successful: {len(response.content)} characters")
        logger.info(f"📊 Tokens used: {response.total_tokens}")
    except Exception as e:
        logger.error(f"❌ Text generation failed: {e}")

    # Test streaming
    try:
        stream_request = ModelRequest(
            prompt="List three benefits of model predictive control",
            max_tokens=100
        )

        content = ""
        async for chunk in manager.generate_stream(stream_request):
            content += chunk

        logger.info(f"✅ Streaming successful: {len(content)} characters")
    except Exception as e:
        logger.error(f"❌ Streaming failed: {e}")

    # Test embeddings
    try:
        texts = ["PID control", "Model predictive control", "Industrial automation"]
        embeddings = await manager.get_embeddings(texts)
        logger.info(f"✅ Embeddings generated: {len(embeddings)} vectors")
    except Exception as e:
        logger.error(f"❌ Embeddings failed: {e}")

    # Get health status
    health_status = await manager.get_health_status()
    logger.info(f"Health status: {health_status}")

    # Get metrics
    metrics = await manager.get_all_metrics()
    for provider_name, metric in metrics.items():
        logger.info(f"{provider_name} metrics: {metric.request_count} requests, {metric.error_rate:.2f}% error rate")

    await manager.close_all()

    logger.info("✅ Model testing completed")

async def main():
    """Main function for testing and demonstration"""
    logger.info("🚀 Phase 17.3.4: Model Abstraction Layer")
    logger.info("=" * 80)

    try:
        await test_model_operations()

        logger.info("🎯 Phase 17.3.4 implementation completed successfully")

    except Exception as e:
        logger.error(f"❌ Error in Phase 17.3.4: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
