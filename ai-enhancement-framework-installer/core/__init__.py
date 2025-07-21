"""
AI Enhancement Framework - Core Components

This module provides the foundational components for AI-assisted development:
- AITaskOrchestrator: Systematic task analysis and execution guidance
- UniversalMemoryManager: Multi-tier memory management system
- UniversalCodeAnalyzer: Comprehensive code quality analysis
"""

# Import core components
try:
    from .task_orchestrator import AITaskOrchestrator
except ImportError:
    AITaskOrchestrator = None

try:
    from .memory_manager import UniversalMemoryManager
except ImportError:
    UniversalMemoryManager = None

try:
    from .code_analyzer import UniversalCodeAnalyzer
except ImportError:
    UniversalCodeAnalyzer = None

# Export available components
__all__ = []

if AITaskOrchestrator:
    __all__.append('AITaskOrchestrator')

if UniversalMemoryManager:
    __all__.append('UniversalMemoryManager')
    
if UniversalCodeAnalyzer:
    __all__.append('UniversalCodeAnalyzer') 