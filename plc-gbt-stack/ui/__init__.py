"""
PLC-GBT User Interface Package
Phase 23.5: User Interface & Experience

This package provides comprehensive user interfaces for LLM interaction including:
- Terminal-based chat UI with rich formatting
- Voice interface with speech-to-text/text-to-speech
- API endpoints for REST and WebSocket integration
- Interactive documentation and help system

Author: PLC-GPT Development Team
Date: June 18, 2025
Phase: 23.5 - User Interface & Experience
Methodology: AI Task Orchestrator Guide
"""

__version__ = "23.5.0"
__author__ = "PLC-GPT Development Team"
__description__ = "User Interface & Experience for Fine-tuned LLM Integration"

# Import main components
from .api import ChatAPI, WebSocketHandler
from .chat import ChatInterface, TerminalChatUI
from .docs import InteractiveDocumentation
from .voice import SpeechProcessor, VoiceInterface

__all__ = [
    "ChatInterface",
    "TerminalChatUI",
    "VoiceInterface",
    "SpeechProcessor",
    "ChatAPI",
    "WebSocketHandler",
    "InteractiveDocumentation"
]
