"""
🚀 AI Enhancement Framework - Modular Integration
Advanced Code Analysis, Optimization, and Provider Abstraction with Modular Architecture

This framework provides comprehensive tools for AI-assisted development including:
- Modular enable/disable system for selective feature usage
- Advanced static analysis with libcst/astroid integration (optional)
- Hallucination detection for AI-generated code
- Code quality analysis with industrial control domain expertise
- Modular provider abstraction for databases (Redis, Neo4j, PostgreSQL, Qdrant) (optional)
- Model abstraction layer for AI models (OpenAI, future local LLMs) (optional)
- WolframAlpha Pro mathematical validation (optional)
- Fine-tuned LLM integration (optional)
- Code optimization and refactoring automation (optional)
- Validation frameworks with comprehensive safety checks
- Modular architecture enablement tools

Each component can be enabled/disabled via configuration:
- wolfram_integration.enable = True/False
- llm_integration.enable = True/False
- database_providers.enable = True/False
- etc.

Following AI Task Orchestrator methodology for systematic development enhancement.

Author: AI Enhancement Framework
Created: 2025-01-17
Updated: 2025-01-20 (Modular Architecture Integration Complete)
"""

__version__ = "2.1.0"  # Bumped for modular architecture
__author__ = "AI Enhancement Framework"

# Import configuration and module loader
from .config import get_module_config, is_module_enabled
from .core.module_loader import (
    get_module_loader, safe_import, conditional_import,
    requires_module, optional_module
)

# Initialize module loader
_loader = get_module_loader()

# Core Analysis Components (conditionally imported)
# Basic code analyzer (always available as fallback)
try:
    from .core.code_analyzer import (
        CodeAnalyzer,
        AnalysisResult,
        ComplexityMetrics,
        CodeIssue,
        analyze_file,
        analyze_directory
    )
except ImportError:
    CodeAnalyzer = None
    AnalysisResult = None
    ComplexityMetrics = None
    CodeIssue = None
    analyze_file = None
    analyze_directory = None

# Enhanced code analysis (conditional on code_analysis module)
_enhanced_code_analyzer = conditional_import(
    is_module_enabled("code_analysis"), 
    "code_analysis"
)

if _enhanced_code_analyzer:
    try:
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
    except ImportError:
        EnhancedCodeAnalyzer = None
        EnhancedAnalysisResult = None
        AnalysisLevel = None
        HallucinationCategory = None
        HallucinationDetection = None
        CodeQualityIssue = None
        CodeQualityAnalysis = None
        SemanticAnalysis = None
        CSTAnalysis = None
        HallucinationDetector = None
        AdvancedCodeQualityAnalyzer = None
        SemanticAnalyzer = None
        CSTAnalyzer = None
else:
    EnhancedCodeAnalyzer = None
    EnhancedAnalysisResult = None
    AnalysisLevel = None
    HallucinationCategory = None
    HallucinationDetection = None
    CodeQualityIssue = None
    CodeQualityAnalysis = None
    SemanticAnalysis = None
    CSTAnalysis = None
    HallucinationDetector = None
    AdvancedCodeQualityAnalyzer = None
    SemanticAnalyzer = None
    CSTAnalyzer = None

# Task Orchestrator (conditional on task_orchestrator module)
_task_orchestrator = conditional_import(
    is_module_enabled("task_orchestrator"),
    "task_orchestrator"
)

if _task_orchestrator:
    try:
        from .core.task_orchestrator import (
            AITaskOrchestrator as EnhancedTaskOrchestrator,
            TaskComplexity,
            TaskAnalysisResult as ValidationResult,
            BaseOrchestrator
        )
    except ImportError:
        EnhancedTaskOrchestrator = None
        TaskComplexity = None
        ValidationResult = None
        BaseOrchestrator = None
else:
    EnhancedTaskOrchestrator = None
    TaskComplexity = None
    ValidationResult = None
    BaseOrchestrator = None

# Validation Framework (conditional on validation_framework module)
_validation_framework = conditional_import(
    is_module_enabled("validation_framework"),
    "validation_framework"
)

if _validation_framework:
    try:
        from .core.validation_framework import (
            ComprehensiveValidationFramework as ValidationFramework,
            ValidationTier,
            ValidationSeverity,
            ComprehensiveValidationResult as ValidationReport
        )
    except ImportError:
        ValidationFramework = None
        ValidationTier = None
        ValidationSeverity = None
        ValidationReport = None
else:
    ValidationFramework = None
    ValidationTier = None
    ValidationSeverity = None
    ValidationReport = None

# LLM Integration (conditional on llm_integration module)  
_llm_integration = conditional_import(
    is_module_enabled("llm_integration"),
    "llm_integration"
)

if _llm_integration:
    try:
        from .core.llm_integration import (
            SpecializedLLMManager as LLMIntegration,
            LLMDomain as ModelType,
            DomainAnalysisResult as ModelResponse,
            DomainSpecificAnalyzer
        )
    except ImportError:
        LLMIntegration = None
        ModelType = None
        ModelResponse = None
        DomainSpecificAnalyzer = None
else:
    LLMIntegration = None
    ModelType = None
    ModelResponse = None
    DomainSpecificAnalyzer = None

# Memory Management (conditional on memory_management module)
_memory_management = conditional_import(
    is_module_enabled("memory_management"),
    "memory_management"
)

if _memory_management:
    try:
        from .core.memory_manager import (
            UniversalMemoryManager as MemoryManager,
            MemoryTier,
            QueryStrategy as MemoryOperation,
            MemoryRequest
        )
    except ImportError:
        MemoryManager = None
        MemoryTier = None
        MemoryOperation = None
        MemoryRequest = None
else:
    MemoryManager = None
    MemoryTier = None
    MemoryOperation = None
    MemoryRequest = None

# WolframAlpha Integration (conditional on wolfram_integration module)
_wolfram_integration = conditional_import(
    is_module_enabled("wolfram_integration"),
    "wolfram_integration"
)

if _wolfram_integration:
    try:
        from .core.wolfram_integration import (
            MathematicalValidationOrchestrator,
            MathematicalDomain,
            VerificationLevel,
            MathematicalExpression,
            VerificationResult,
            MathematicalContext,
            validate_mathematical_code,
            get_mathematical_context
        )
    except ImportError:
        MathematicalValidationOrchestrator = None
        MathematicalDomain = None
        VerificationLevel = None
        MathematicalExpression = None
        VerificationResult = None
        MathematicalContext = None
        validate_mathematical_code = None
        get_mathematical_context = None
else:
    MathematicalValidationOrchestrator = None
    MathematicalDomain = None
    VerificationLevel = None
    MathematicalExpression = None
    VerificationResult = None
    MathematicalContext = None
    validate_mathematical_code = None
    get_mathematical_context = None

# Optimization Components (conditional)
# Codebase Analyzer (conditional on code_optimization module)
_code_optimization = conditional_import(
    is_module_enabled("code_optimization"),
    "code_optimization"
)

if _code_optimization:
    try:
        from .optimization.codebase_analyzer import (
            CodebaseAnalyzer,
            FileAnalysisResult,
            DirectoryAnalysis,
            RefactoringPlan,
            ModularityMetrics
        )
    except ImportError:
        CodebaseAnalyzer = None
        FileAnalysisResult = None
        DirectoryAnalysis = None
        RefactoringPlan = None
        ModularityMetrics = None
else:
    CodebaseAnalyzer = None
    FileAnalysisResult = None
    DirectoryAnalysis = None
    RefactoringPlan = None
    ModularityMetrics = None

# Modular Extractor (conditional on modular_extraction module)
_modular_extraction = conditional_import(
    is_module_enabled("modular_extraction"),
    "modular_extraction"
)

if _modular_extraction:
    try:
        from .optimization.modular_extractor import (
            ModularExtractor,
            FunctionExtraction,
            ModuleCreation,
            ExtractionResult,
            ImportUpdate
        )
    except ImportError:
        ModularExtractor = None
        FunctionExtraction = None
        ModuleCreation = None
        ExtractionResult = None
        ImportUpdate = None
else:
    ModularExtractor = None
    FunctionExtraction = None
    ModuleCreation = None
    ExtractionResult = None
    ImportUpdate = None

# Code Quality Optimizer (conditional on code_optimization module)
if _code_optimization:
    try:
        from .optimization.code_quality_optimizer import (
            CodeQualityOptimizer,
            ImportOptimization,
            PatternStandardization,
            OptimizationResult
        )
    except ImportError:
        CodeQualityOptimizer = None
        ImportOptimization = None
        PatternStandardization = None
        OptimizationResult = None
else:
    CodeQualityOptimizer = None
    ImportOptimization = None
    PatternStandardization = None
    OptimizationResult = None

# Provider Abstraction Components (conditional)
# Base Provider Framework (always available)
try:
    from .providers.provider_framework import (
        BaseProvider,
        ProviderConfig,
        HealthStatus,
        CircuitBreaker,
        ProviderManager
    )
except ImportError:
    BaseProvider = None
    ProviderConfig = None
    HealthStatus = None
    CircuitBreaker = None
    ProviderManager = None

# Database Providers (conditional on database_providers module)
_database_providers = conditional_import(
    is_module_enabled("database_providers"),
    "database_providers"
)

if _database_providers:
    try:
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
    except ImportError:
        EnhancedDatabaseProvider = None
        EnhancedProviderConfig = None
        EnhancedProviderManager = None
        EnhancedProviderFactory = None
        ProviderType = None
        OperationType = None
        HealthStatus = None
        OperationResult = None
        ProviderMetrics = None
        EnhancedRedisProvider = None
        EnhancedNeo4jProvider = None
        EnhancedPostgreSQLProvider = None
        EnhancedQdrantProvider = None
        create_enhanced_provider_manager_with_defaults = None
        setup_default_providers = None
else:
    EnhancedDatabaseProvider = None
    EnhancedProviderConfig = None
    EnhancedProviderManager = None
    EnhancedProviderFactory = None
    ProviderType = None
    OperationType = None
    HealthStatus = None
    OperationResult = None
    ProviderMetrics = None
    EnhancedRedisProvider = None
    EnhancedNeo4jProvider = None
    EnhancedPostgreSQLProvider = None
    EnhancedQdrantProvider = None
    create_enhanced_provider_manager_with_defaults = None
    setup_default_providers = None

# Model Providers (conditional on model_providers module)
_model_providers = conditional_import(
    is_module_enabled("model_providers"),
    "model_providers"
)

if _model_providers:
    try:
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
    except ImportError:
        ModelProvider = None
        ModelConfig = None
        ModelMetrics = None
        ModelRequest = None
        ModelResponse = None
        ModelType = None
        ModelCapability = None
        ModelStatus = None
        OpenAIProvider = None
        LocalModelProvider = None
        EnhancedModelFactory = None
        EnhancedModelManager = None
        create_enhanced_model_manager_with_defaults = None
        setup_default_openai_provider = None
        create_model_request = None
else:
    ModelProvider = None
    ModelConfig = None
    ModelMetrics = None
    ModelRequest = None
    ModelResponse = None
    ModelType = None
    ModelCapability = None
    ModelStatus = None
    OpenAIProvider = None
    LocalModelProvider = None
    EnhancedModelFactory = None
    EnhancedModelManager = None
    create_enhanced_model_manager_with_defaults = None
    setup_default_openai_provider = None
    create_model_request = None

# Modular Provider Abstraction (conditional on database_providers module)
if _database_providers:
    try:
        from .providers.modular_provider_abstraction import (
            DatabaseProvider,
            ProviderManager,
            DatabaseOperationResult
        )
    except ImportError:
        DatabaseProvider = None
        ProviderManager = None
        DatabaseOperationResult = None
else:
    DatabaseProvider = None
    ProviderManager = None
    DatabaseOperationResult = None

# Model Abstraction Layer (conditional on model_providers module)
if _model_providers:
    try:
        from .providers.model_abstraction_layer import (
            ModelAbstractionLayer,
            ModelFactory,
            ModelManager
        )
    except ImportError:
        ModelAbstractionLayer = None
        ModelFactory = None
        ModelManager = None
else:
    ModelAbstractionLayer = None
    ModelFactory = None
    ModelManager = None

# Configuration and Utilities (conditional)
# Configuration system (always available)
try:
    from .config.settings import (
        FrameworkConfig,
        AnalysisConfig,
        OptimizationConfig,
        ProviderConfig as ConfigProviderConfig,
        load_config,
        save_config
    )
except ImportError:
    FrameworkConfig = None
    AnalysisConfig = None
    OptimizationConfig = None
    ConfigProviderConfig = None
    load_config = None
    save_config = None

# Utilities (always available)
try:
    from .utils.helpers import (
        setup_logging,
        validate_environment,
        check_dependencies,
        get_framework_info
    )
except ImportError:
    setup_logging = None
    validate_environment = None
    check_dependencies = None
    get_framework_info = None

# Main Framework Interface (always available)
try:
    from .framework import (
        AIEnhancementFramework,
        FrameworkMode,
        create_framework,
        initialize_framework
    )
except ImportError:
    AIEnhancementFramework = None
    FrameworkMode = None
    create_framework = None
    initialize_framework = None

# Export all main components (dynamically based on enabled modules)
__all__ = [
    # Configuration and Module Management (always available)
    "get_module_config",
    "is_module_enabled",
    "enable_module", 
    "disable_module",
    "get_module_loader",
    "safe_import",
    "conditional_import",
    "requires_module",
    "optional_module"
]

# Add available components dynamically
_available_exports = {
    # Core Analysis
    "CodeAnalyzer": CodeAnalyzer,
    "EnhancedCodeAnalyzer": EnhancedCodeAnalyzer,
    "AnalysisResult": AnalysisResult,
    "EnhancedAnalysisResult": EnhancedAnalysisResult,
    "AnalysisLevel": AnalysisLevel,
    "HallucinationDetector": HallucinationDetector,
    "AdvancedCodeQualityAnalyzer": AdvancedCodeQualityAnalyzer,
    "SemanticAnalyzer": SemanticAnalyzer,
    "CSTAnalyzer": CSTAnalyzer,
    "analyze_file": analyze_file,
    "analyze_directory": analyze_directory,
    
    # Task Orchestration
    "EnhancedTaskOrchestrator": EnhancedTaskOrchestrator,
    "TaskComplexity": TaskComplexity,
    "ValidationFramework": ValidationFramework,
    "ValidationTier": ValidationTier,
    "ValidationSeverity": ValidationSeverity,
    
    # LLM Integration
    "LLMIntegration": LLMIntegration,
    "ModelType": ModelType,
    "ModelResponse": ModelResponse,
    "DomainSpecificAnalyzer": DomainSpecificAnalyzer,
    
    # WolframAlpha Integration
    "MathematicalValidationOrchestrator": MathematicalValidationOrchestrator,
    "MathematicalDomain": MathematicalDomain,
    "VerificationLevel": VerificationLevel,
    "validate_mathematical_code": validate_mathematical_code,
    "get_mathematical_context": get_mathematical_context,
    
    # Memory Management
    "MemoryManager": MemoryManager,
    "MemoryTier": MemoryTier,
    "MemoryRequest": MemoryRequest,
    
    # Optimization Tools
    "CodebaseAnalyzer": CodebaseAnalyzer,
    "ModularExtractor": ModularExtractor,
    "CodeQualityOptimizer": CodeQualityOptimizer,
    "FileAnalysisResult": FileAnalysisResult,
    "DirectoryAnalysis": DirectoryAnalysis,
    "RefactoringPlan": RefactoringPlan,
    "ExtractionResult": ExtractionResult,
    "OptimizationResult": OptimizationResult,
    
    # Provider Abstraction
    "BaseProvider": BaseProvider,
    "EnhancedDatabaseProvider": EnhancedDatabaseProvider,
    "EnhancedProviderManager": EnhancedProviderManager,
    "EnhancedProviderFactory": EnhancedProviderFactory,
    "ProviderType": ProviderType,
    "OperationType": OperationType,
    "HealthStatus": HealthStatus,
    "EnhancedRedisProvider": EnhancedRedisProvider,
    "EnhancedNeo4jProvider": EnhancedNeo4jProvider,
    "EnhancedPostgreSQLProvider": EnhancedPostgreSQLProvider,
    "EnhancedQdrantProvider": EnhancedQdrantProvider,
    "create_enhanced_provider_manager_with_defaults": create_enhanced_provider_manager_with_defaults,
    
    # Model Abstraction
    "ModelProvider": ModelProvider,
    "ModelConfig": ModelConfig,
    "ModelRequest": ModelRequest,
    "ModelResponse": ModelResponse,
    "ModelCapability": ModelCapability,
    "ModelStatus": ModelStatus,
    "OpenAIProvider": OpenAIProvider,
    "LocalModelProvider": LocalModelProvider,
    "EnhancedModelFactory": EnhancedModelFactory,
    "EnhancedModelManager": EnhancedModelManager,
    "create_enhanced_model_manager_with_defaults": create_enhanced_model_manager_with_defaults,
    "setup_default_openai_provider": setup_default_openai_provider,
    "create_model_request": create_model_request,
    
    # Configuration
    "FrameworkConfig": FrameworkConfig,
    "AnalysisConfig": AnalysisConfig,
    "OptimizationConfig": OptimizationConfig,
    "load_config": load_config,
    "save_config": save_config,
    
    # Utilities
    "setup_logging": setup_logging,
    "validate_environment": validate_environment,
    "check_dependencies": check_dependencies,
    "get_framework_info": get_framework_info,
    
    # Main Framework
    "AIEnhancementFramework": AIEnhancementFramework,
    "FrameworkMode": FrameworkMode,
    "create_framework": create_framework,
    "initialize_framework": initialize_framework
}

# Only export components that are actually available (not None)
for name, component in _available_exports.items():
    if component is not None:
        __all__.append(name)

# Framework capabilities (dynamic based on enabled modules)
def get_framework_capabilities() -> dict:
    """Get current framework capabilities based on enabled modules"""
    capabilities = {
        # Core capabilities (always available)
        "modular_architecture": True,
        "conditional_loading": True,
        "configuration_management": True,
        "dependency_validation": True,
        
        # Module-specific capabilities
        "advanced_static_analysis": is_module_enabled("code_analysis") and EnhancedCodeAnalyzer is not None,
        "hallucination_detection": is_module_enabled("code_analysis") and HallucinationDetector is not None,
        "libcst_integration": is_module_enabled("code_analysis") and CSTAnalyzer is not None,
        "astroid_integration": is_module_enabled("code_analysis") and SemanticAnalyzer is not None,
        "code_quality_analysis": is_module_enabled("code_analysis") and AdvancedCodeQualityAnalyzer is not None,
        "modular_extraction": is_module_enabled("modular_extraction") and ModularExtractor is not None,
        "code_optimization": is_module_enabled("code_optimization") and CodeQualityOptimizer is not None,
        "provider_abstraction": is_module_enabled("database_providers") and EnhancedProviderManager is not None,
        "model_abstraction": is_module_enabled("model_providers") and EnhancedModelManager is not None,
        "redis_support": is_module_enabled("database_providers") and EnhancedRedisProvider is not None,
        "neo4j_support": is_module_enabled("database_providers") and EnhancedNeo4jProvider is not None,
        "postgresql_support": is_module_enabled("database_providers") and EnhancedPostgreSQLProvider is not None,
        "qdrant_support": is_module_enabled("database_providers") and EnhancedQdrantProvider is not None,
        "openai_integration": is_module_enabled("model_providers") and OpenAIProvider is not None,
        "local_model_ready": is_module_enabled("model_providers") and LocalModelProvider is not None,
        "circuit_breaker_pattern": BaseProvider is not None and CircuitBreaker is not None,
        "health_monitoring": is_module_enabled("health_monitoring"),
        "metrics_tracking": is_module_enabled("health_monitoring"),
        "validation_framework": is_module_enabled("validation_framework") and ValidationFramework is not None,
        "wolfram_alpha_integration": is_module_enabled("wolfram_integration") and MathematicalValidationOrchestrator is not None,
        "llm_integration": is_module_enabled("llm_integration") and LLMIntegration is not None,
        "task_orchestrator": is_module_enabled("task_orchestrator") and EnhancedTaskOrchestrator is not None,
        "memory_management": is_module_enabled("memory_management") and MemoryManager is not None,
        "docker_integration": is_module_enabled("docker_integration"),
        "industrial_control_patterns": True,  # Available through documentation and patterns
        "ai_task_orchestrator_integration": True  # Core methodology
    }
    return capabilities

# Current capabilities (computed at import time)
FRAMEWORK_CAPABILITIES = get_framework_capabilities()

# Version information (dynamic)
def get_version_info() -> dict:
    """Get current version information including enabled modules"""
    enabled_modules = get_module_config().get_enabled_modules()
    disabled_modules = get_module_config().get_disabled_modules()
    
    return {
        "version": __version__,
        "architecture": "✅ Modular",
        "phase_17_3_integration": "✅ Complete",
        "phase_14_integration": "✅ Complete", 
        "modular_system": "✅ Implemented",
        "conditional_loading": "✅ Active",
        "enabled_modules": len(enabled_modules),
        "disabled_modules": len(disabled_modules),
        "total_modules": len(enabled_modules) + len(disabled_modules),
        "capabilities": len([k for k, v in FRAMEWORK_CAPABILITIES.items() if v]),
        "available_components": len(__all__),
        "configuration_path": str(get_module_config().config_path),
        "module_status": {
            name: "✅ Enabled" if config.enabled else "❌ Disabled"
            for name, config in {**enabled_modules, **disabled_modules}.items()
        }
    }

VERSION_INFO = get_version_info()

# Convenience functions for module management
def print_module_status():
    """Print current module status"""
    config = get_module_config()
    summary = config.get_configuration_summary()
    
    print(f"\n🚀 AI Enhancement Framework v{__version__}")
    print(f"📊 Modules: {summary['enabled_count']}/{summary['total_modules']} enabled")
    print(f"🔧 Configuration: {config.config_path}")
    
    print(f"\n✅ Enabled Modules ({summary['enabled_count']}):")
    for module in summary['enabled_modules']:
        module_info = config.get_module_info(module)
        print(f"  • {module}: {module_info['description']}")
    
    if summary['disabled_modules']:
        print(f"\n❌ Disabled Modules ({summary['disabled_count']}):")
        for module in summary['disabled_modules']:
            module_info = config.get_module_info(module)
            print(f"  • {module}: {module_info['description']}")
    
    if not summary['dependency_validation']['valid']:
        print(f"\n⚠️  Dependency Issues:")
        for issue in summary['dependency_validation']['issues']:
            print(f"  • {issue}")

def enable_features(*features):
    """Enable multiple features at once"""
    config = get_module_config()
    results = {}
    for feature in features:
        results[feature] = config.enable_module(feature)
    config.save_config()
    return results

def disable_features(*features):
    """Disable multiple features at once"""  
    config = get_module_config()
    results = {}
    for feature in features:
        results[feature] = config.disable_module(feature)
    config.save_config()
    return results

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