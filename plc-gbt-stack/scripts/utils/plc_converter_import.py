#!/usr/bin/env python3
"""
PLC Format Converter Import Utility

This module provides a consistent way to import the plc_format_converter
library from the separate acd-l5x-tool-lib repository.
"""

import sys
import os
from pathlib import Path

def setup_plc_converter_import():
    """
    Set up the import path for plc_format_converter from the separate repository.
    
    Returns:
        bool: True if setup successful, False otherwise
    """
    # Path to the separate acd-l5x-tool-lib repository
    acd_l5x_repo_path = Path("/Users/reh3376/repos/acd-l5x-tool-lib/src")
    
    if acd_l5x_repo_path.exists():
        if str(acd_l5x_repo_path) not in sys.path:
            sys.path.insert(0, str(acd_l5x_repo_path))
        return True
    else:
        print(f"Warning: acd-l5x-tool-lib repository not found at {acd_l5x_repo_path}")
        return False

def import_plc_converter():
    """
    Import and return the PLCConverter class.
    
    Returns:
        PLCConverter class if successful, None otherwise
    """
    if setup_plc_converter_import():
        try:
            from plc_format_converter.core.converter import PLCConverter
            return PLCConverter
        except ImportError as e:
            print(f"Error importing PLCConverter: {e}")
            return None
    return None

def import_plc_models():
    """
    Import and return common PLC model classes.
    
    Returns:
        dict: Dictionary of model classes if successful, empty dict otherwise
    """
    if setup_plc_converter_import():
        try:
            from plc_format_converter.core.models import (
                PLCProject, PLCController, PLCProgram, PLCRoutine, 
                PLCTag, PLCDevice, ConversionResult, ConversionStatus
            )
            return {
                'PLCProject': PLCProject,
                'PLCController': PLCController,
                'PLCProgram': PLCProgram,
                'PLCRoutine': PLCRoutine,
                'PLCTag': PLCTag,
                'PLCDevice': PLCDevice,
                'ConversionResult': ConversionResult,
                'ConversionStatus': ConversionStatus
            }
        except ImportError as e:
            print(f"Error importing PLC models: {e}")
            return {}
    return {}

def import_format_handlers():
    """
    Import and return format handler classes.
    
    Returns:
        dict: Dictionary of handler classes if successful, empty dict otherwise
    """
    if setup_plc_converter_import():
        try:
            from plc_format_converter.formats.acd_handler import ACDHandler
            from plc_format_converter.formats.l5x_handler import L5XHandler
            return {
                'ACDHandler': ACDHandler,
                'L5XHandler': L5XHandler
            }
        except ImportError as e:
            print(f"Error importing format handlers: {e}")
            return {}
    return {}

# Convenience function for quick setup
def quick_setup():
    """
    Quick setup function that returns commonly used classes.
    
    Returns:
        tuple: (PLCConverter, models_dict, handlers_dict)
    """
    converter = import_plc_converter()
    models = import_plc_models()
    handlers = import_format_handlers()
    
    return converter, models, handlers

if __name__ == "__main__":
    # Test the import functionality
    print("Testing PLC Format Converter import utility...")
    
    PLCConverter, models, handlers = quick_setup()
    
    if PLCConverter:
        print("✅ PLCConverter imported successfully")
    else:
        print("❌ Failed to import PLCConverter")
    
    if models:
        print(f"✅ Imported {len(models)} model classes")
    else:
        print("❌ Failed to import model classes")
    
    if handlers:
        print(f"✅ Imported {len(handlers)} handler classes")
    else:
        print("❌ Failed to import handler classes") 