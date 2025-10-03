"""
OpenAI Service - AI Assistant Integration
Connects to OpenAI API with fine-tuned industrial control model

Fine-tuned Model: ft:gpt-4o:industrial-control:20250117
"""

import logging
import os
from datetime import UTC, datetime
from typing import Any

from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)

# Fine-tuned model ID - read from environment or use default
DEFAULT_MODEL = "ft:gpt-4o:industrial-control:20250117"
FINE_TUNED_MODEL = os.getenv("Model", DEFAULT_MODEL)
SEED = int(os.getenv("Seed", "1"))

class OpenAIService:
    """
    Service for interacting with OpenAI API
    Handles chat completions with fine-tuned industrial control model
    """

    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment - AI assistant will use fallback responses")
            self.client = None
            self.async_client = None
            self.model = None
            self.seed = None
        else:
            self.client = OpenAI(api_key=api_key)
            self.async_client = AsyncOpenAI(api_key=api_key)
            self.model = FINE_TUNED_MODEL
            self.seed = SEED
            logger.info("OpenAI client initialized")
            logger.info(f"  Model: {self.model}")
            logger.info(f"  Seed: {self.seed}")

    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return self.client is not None

    async def chat_completion(
        self,
        message: str,
        conversation_history: list[dict[str, str]] | None = None,
        context: dict[str, Any] | None = None,
        stream: bool = False
    ) -> dict[str, Any]:
        """
        Get chat completion from fine-tuned model

        Args:
            message: User's message
            conversation_history: Previous messages in conversation
            context: Additional context (current file, workspace info, etc.)
            stream: Whether to stream the response

        Returns:
            Dict with response message and metadata
        """
        if not self.is_available():
            return self._get_fallback_response(message)

        # Type guard: at this point we know client and model are not None
        assert self.async_client is not None
        assert self.model is not None
        assert self.seed is not None

        try:
            # Build messages array
            messages = []

            # System message with industrial control expertise
            system_message = {
                "role": "system",
                "content": (
                    "You are an expert industrial automation AI assistant specialized in "
                    "PLC programming, control systems, and industrial protocols. "
                    "You provide accurate, practical guidance on control theory, PID tuning, "
                    "ladder logic, function blocks, and industrial automation best practices. "
                    "Be concise, technical, and safety-conscious in your responses."
                )
            }

            # Add context if provided
            if context:
                context_str = self._format_context(context)
                system_message["content"] += f"\n\nCurrent context:\n{context_str}"

            messages.append(system_message)

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({
                "role": "user",
                "content": message
            })

            # Call OpenAI API with fine-tuned model
            logger.info(f"Calling OpenAI API with model: {self.model}, seed: {self.seed}")

            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                seed=self.seed,
                stream=stream
            )

            if stream:
                # Return stream object for streaming responses
                return {"stream": response}

            # Extract response (non-streaming)
            # Type narrowing: response is ChatCompletion when stream=False
            from openai.types.chat import ChatCompletion
            assert isinstance(response, ChatCompletion)
            assistant_message = response.choices[0].message.content

            return {
                "message": assistant_message,
                "model": self.model,
                "seed": self.seed,
                "timestamp": datetime.now(UTC).isoformat(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_response(message, error=str(e))

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context information for system message"""
        parts = []

        if "currentFile" in context:
            parts.append(f"Current file: {context['currentFile']}")

        if "fileType" in context:
            parts.append(f"File type: {context['fileType']}")

        if "selectedCode" in context:
            parts.append(f"Selected code:\n{context['selectedCode']}")

        if "workspace" in context:
            parts.append(f"Workspace: {context['workspace']}")

        return "\n".join(parts) if parts else "No specific context"

    def _get_fallback_response(self, message: str, error: str | None = None) -> dict[str, Any]:
        """
        Generate fallback response when OpenAI is unavailable

        Args:
            message: User's message
            error: Optional error message

        Returns:
            Fallback response dict
        """
        if error:
            fallback_message = (
                "⚠️ The AI assistant is temporarily unavailable due to an API error. "
                f"Error: {error}\n\n"
                "Please check your OPENAI_API_KEY environment variable and try again."
            )
        else:
            fallback_message = (
                "⚠️ The AI assistant requires an OpenAI API key to function. "
                "Please set the OPENAI_API_KEY environment variable and restart the server.\n\n"
                "To enable the AI assistant:\n"
                "1. Set OPENAI_API_KEY in your environment\n"
                "2. Restart the backend server\n"
                "3. The fine-tuned model will provide industrial control expertise"
            )

        return {
            "message": fallback_message,
            "model": "fallback",
            "timestamp": datetime.now(UTC).isoformat(),
            "fallback": True
        }


# Singleton instance
_openai_service: OpenAIService | None = None

def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service singleton"""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service

