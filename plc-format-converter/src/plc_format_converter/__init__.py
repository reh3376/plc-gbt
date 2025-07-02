"""
PLC Format Converter

A Python library for bidirectional conversion between Rockwell .ACD and .L5X PLC file formats.
"""

__version__ = "0.1.0"
__author__ = "PLC-GPT Team"
__email__ = "dev@plc-gpt.com"

from .core.converter import PLCConverter
from .core.models import PLCProject, ConversionResult, ConversionError
from .formats.acd_handler import ACDHandler
from .formats.l5x_handler import L5XHandler
from .utils.validation import validate_conversion

__all__ = [
    "PLCConverter",
    "PLCProject", 
    "ConversionResult",
    "ConversionError",
    "ACDHandler",
    "L5XHandler",
    "validate_conversion",
] 