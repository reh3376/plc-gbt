"""
API Endpoints Package
Task 23.5.3: RESTful Chat API and WebSocket Implementation

Provides comprehensive API endpoints for LLM interaction including:
- RESTful chat API with authentication
- WebSocket for real-time interaction
- Batch processing endpoints
- Integration webhooks

Author: PLC-GPT Development Team
Date: June 18, 2025
Task: 23.5.3 - API Endpoints
"""

from .batch_processor import BatchProcessor
from .chat_api import ChatAPI, ChatRequest, ChatResponse
from .webhooks import WebhookManager
from .websocket_handler import WebSocketHandler, WebSocketManager

__all__ = [
    "ChatAPI",
    "ChatRequest",
    "ChatResponse",
    "WebSocketHandler",
    "WebSocketManager",
    "BatchProcessor",
    "WebhookManager"
]
