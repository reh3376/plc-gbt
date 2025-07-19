"""
Voice Interface Package
Task 23.5.2: Voice Interface Implementation (Architecture Ready)

Provides voice interaction capabilities for LLM integration including:
- Speech-to-text processing
- Text-to-speech output
- Voice command recognition
- Audio session management

Author: PLC-GPT Development Team
Date: June 18, 2025
Task: 23.5.2 - Voice Interface
Status: Architecture Ready - Implementation framework prepared
"""

from .voice_interface import VoiceInterface
from .speech_processor import SpeechProcessor

__all__ = [
    "VoiceInterface",
    "SpeechProcessor"
] 