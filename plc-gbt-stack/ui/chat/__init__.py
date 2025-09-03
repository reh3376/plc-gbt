"""
Chat Interface Package
Task 23.5.1: Terminal-based Chat UI Implementation

Provides rich terminal-based chat interface with:
- Code syntax highlighting
- Progress indicators
- Multi-turn conversation support
- Industrial control system context

Author: PLC-GPT Development Team
Date: June 18, 2025
Task: 23.5.1 - Chat Interface
"""

from .chat_interface import ChatInterface
from .message_formatter import MessageFormatter
from .progress_indicator import ProgressIndicator
from .terminal_ui import TerminalChatUI

__all__ = [
    "ChatInterface",
    "TerminalChatUI",
    "MessageFormatter",
    "ProgressIndicator"
]
