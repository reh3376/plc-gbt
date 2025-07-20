"""
🚀 AI Enhancement Framework - Complete Integration
Advanced Code Analysis, Optimization, and Provider Abstraction

This framework provides comprehensive tools for AI-assisted development including:
- Advanced static analysis with libcst/astroid integration
- Hallucination detection for AI-generated code
- Code quality analysis with industrial control domain expertise
- Modular provider abstraction for databases (Redis, Neo4j, PostgreSQL, Qdrant)
- Model abstraction layer for AI models (OpenAI, future local LLMs)
- Code optimization and refactoring automation
- Validation frameworks with comprehensive safety checks
- Modular architecture enablement tools

Following AI Task Orchestrator methodology for systematic development enhancement.

Author: AI Enhancement Framework
Created: 2025-01-17
Updated: 2025-01-17 (Phase 17.3 & Phase 14 Integration Complete)
"""

__version__ = "2.0.0"
__author__ = "AI Enhancement Framework"

# Core Analysis Components
from .core.code_analyzer import (
    CodeAnalyzer,
    AnalysisResult,
    ComplexityMetrics,
    CodeIssue,
    analyze_file,
    analyze_directory
)

from .core.enhanced_code_analyzer import (
    EnhancedCodeAnalyzer,
    EnhancedAnalysisResult,
    AnalysisLevel,
    HallucinationCategory,
    HallucinationDetection,
    CodeQualityIssue,
    CodeQualityAnalysis,
    SemanticAnalysis,
    CSTAnalysis,
    HallucinationDetector,
    AdvancedCodeQualityAnalyzer,
    SemanticAnalyzer,
    CSTAnalyzer
)

from .core.enhanced_task_orchestrator import (
    EnhancedTaskOrchestrator,
    TaskComplexity,
    ValidationTier,
    ValidationResult
)

from .core.validation_framework import (
    ValidationFramework,
    ValidationRule,
    ValidationSeverity,
    ValidationReport
)

from .core.llm_integration import (
    LLMIntegration,
    ModelType,
    ModelResponse,
    validate_with_llm
)

from .core.memory_manager import (
    MemoryManager,
    MemoryTier,
    MemoryOperation,
    query_memory
)

# Optimization Components
from .optimization.codebase_analyzer import (
    CodebaseAnalyzer,
    FileAnalysisResult,
    DirectoryAnalysis,
    RefactoringPlan,
    ModularityMetrics
)

from .optimization.modular_extractor import (
    ModularExtractor,
    FunctionExtraction,
    UtilityModule,
    ExtractionResult,
    SafetyValidator,
    ImportManager
)

from .optimization.code_quality_optimizer import (
    CodeQualityOptimizer,
    ImportOptimization,
    FileRefactoring,
    PatternStandardization,
    OptimizationResult,
    QualityMetrics
)

# Provider Abstraction Components
from .providers.provider_framework import (
    BaseProvider,
    ProviderConfig,
    ProviderStatus,
    CircuitBreaker,
    HealthMonitor
)

from .providers.enhanced_provider_abstraction import (
    EnhancedDatabaseProvider,
    EnhancedProviderConfig,
    EnhancedProviderManager,
    EnhancedProviderFactory,
    ProviderType,
    OperationType,
    HealthStatus,
    OperationResult,
    ProviderMetrics,
    EnhancedRedisProvider,
    EnhancedNeo4jProvider,
    EnhancedPostgreSQLProvider,
    EnhancedQdrantProvider,
    create_enhanced_provider_manager_with_defaults,
    setup_default_providers
)

from .providers.enhanced_model_abstraction import (
    ModelProvider,
    ModelConfig,
    ModelMetrics,
    ModelRequest,
    ModelResponse,
    ModelType,
    ModelCapability,
    ModelStatus,
    OpenAIProvider,
    LocalModelProvider,
    EnhancedModelFactory,
    EnhancedModelManager,
    create_enhanced_model_manager_with_defaults,
    setup_default_openai_provider,
    create_model_request
)

from .providers.modular_provider_abstraction import (
    DatabaseProvider,
    ProviderManager,
    DatabaseOperationResult
)

from .providers.model_abstraction_layer import (
    ModelAbstractionLayer,
    ModelFactory,
    ModelManager
)

# Configuration and Utilities
from .config.settings import (
    FrameworkConfig,
    AnalysisConfig,
    OptimizationConfig,
    ProviderConfig as ConfigProviderConfig,
    load_config,
    save_config
)

from .utils.helpers import (
    setup_logging,
    validate_environment,
    check_dependencies,
    get_framework_info
)

# Main Framework Interface
from .framework import (
    AIEnhancementFramework,
    FrameworkMode,
    create_framework,
    initialize_framework
)

# Export all main components
__all__ = [
    # Core Analysis
    "CodeAnalyzer",
    "EnhancedCodeAnalyzer", 
    "AnalysisResult",
    "EnhancedAnalysisResult",
    "AnalysisLevel",
    "HallucinationDetector",
    "AdvancedCodeQualityAnalyzer",
    "SemanticAnalyzer",
    "CSTAnalyzer",
    "analyze_file",
    "analyze_directory",
    
    # Task Orchestration
    "EnhancedTaskOrchestrator",
    "TaskComplexity",
    "ValidationFramework",
    "ValidationRule",
    "ValidationSeverity",
    
    # LLM Integration
    "LLMIntegration",
    "ModelType",
    "ModelResponse",
    "validate_with_llm",
    
    # Memory Management
    "MemoryManager",
    "MemoryTier",
    "query_memory",
    
    # Optimization Tools
    "CodebaseAnalyzer",
    "ModularExtractor", 
    "CodeQualityOptimizer",
    "FileAnalysisResult",
    "DirectoryAnalysis",
    "RefactoringPlan",
    "ExtractionResult",
    "OptimizationResult",
    
    # Provider Abstraction
    "BaseProvider",
    "EnhancedDatabaseProvider",
    "EnhancedProviderManager",
    "EnhancedProviderFactory",
    "ProviderType",
    "OperationType",
    "HealthStatus",
    "EnhancedRedisProvider",
    "EnhancedNeo4jProvider", 
    "EnhancedPostgreSQLProvider",
    "EnhancedQdrantProvider",
    "create_enhanced_provider_manager_with_defaults",
    
    # Model Abstraction
    "ModelProvider",
    "ModelConfig",
    "ModelRequest",
    "ModelResponse",
    "ModelCapability",
    "ModelStatus",
    "OpenAIProvider",
    "LocalModelProvider",
    "EnhancedModelFactory",
    "EnhancedModelManager",
    "create_enhanced_model_manager_with_defaults",
    "setup_default_openai_provider",
    "create_model_request",
    
    # Configuration
    "FrameworkConfig",
    "AnalysisConfig",
    "OptimizationConfig",
    "load_config",
    "save_config",
    
    # Utilities
    "setup_logging",
    "validate_environment", 
    "check_dependencies",
    "get_framework_info",
    
    # Main Framework
    "AIEnhancementFramework",
    "FrameworkMode",
    "create_framework",
    "initialize_framework"
]

# Framework capabilities
FRAMEWORK_CAPABILITIES = {
    "advanced_static_analysis": True,
    "hallucination_detection": True,
    "libcst_integration": True,
    "astroid_integration": True,
    "code_quality_analysis": True,
    "modular_extraction": True,
    "code_optimization": True,
    "provider_abstraction": True,
    "model_abstraction": True,
    "redis_support": True,
    "neo4j_support": True,
    "postgresql_support": True,
    "qdrant_support": True,
    "openai_integration": True,
    "local_model_ready": True,
    "circuit_breaker_pattern": True,
    "health_monitoring": True,
    "metrics_tracking": True,
    "validation_framework": True,
    "industrial_control_patterns": True,
    "ai_task_orchestrator_integration": True
}

# Version information
VERSION_INFO = {
    "version": __version__,
    "phase_17_3_integration": "✅ Complete",
    "phase_14_integration": "✅ Complete", 
    "advanced_static_analysis": "✅ Integrated",
    "provider_abstraction": "✅ Integrated",
    "model_abstraction": "✅ Integrated",
    "optimization_tools": "✅ Integrated",
    "validation_framework": "✅ Enhanced",
    "capabilities": len(FRAMEWORK_CAPABILITIES),
    "components": len(__all__)
}

def get_framework_status():
    """Get comprehensive framework status"""
    return {
        "version": __version__,
        "capabilities": FRAMEWORK_CAPABILITIES,
        "version_info": VERSION_INFO,
        "components_available": len(__all__),
        "integration_status": {
            "phase_17_3_advanced_architecture": "Complete",
            "phase_14_optimization_tools": "Complete",
            "enhanced_static_analysis": "Complete",
            "provider_abstraction_layer": "Complete", 
            "model_abstraction_layer": "Complete",
            "validation_frameworks": "Enhanced"
        }
    }

# Initialize framework logging
import logging
logging.getLogger(__name__).info(f"AI Enhancement Framework v{__version__} loaded with {len(__all__)} components")
logging.getLogger(__name__).info(f"Capabilities: {list(FRAMEWORK_CAPABILITIES.keys())}") 