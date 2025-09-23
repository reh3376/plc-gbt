"""Enumerations and constants for the PLC Task Orchestrator."""

from enum import Enum


class TaskComplexity:
    """Task complexity levels for planning."""

    SIMPLE = "simple"  # < 100 lines, single file
    MODERATE = "moderate"  # 100-500 lines, few files
    COMPLEX = "complex"  # 500-1500 lines, multiple files
    EXTENSIVE = "extensive"  # > 1500 lines, major changes


class TaskStatus:
    """Task completion status constants."""

    COMPLETED = "✅ COMPLETED"
    IN_PROGRESS = "🔄 IN PROGRESS"
    FAILED = "❌ FAILED"
    PENDING = "⏳ PENDING"


class ExecutionSteps:
    """Execution step name constants."""

    TASK_EXECUTION = "Task Execution"
    SETUP = "Environment Setup"
    DISCOVERY = "Codebase Discovery"
    PLANNING = "Task Planning"
    CONTEXT = "Context Generation"
    IMPLEMENTATION = "Implementation"
    TESTING = "Testing"
    DOCUMENTATION = "Documentation"
    VALIDATION = "Validation"


class ControlSystemComplexity(Enum):
    """Control system specific complexity levels"""

    BASIC_PID = "basic_pid"  # Single loop tuning
    CASCADE_CONTROL = "cascade"  # Multi-loop coordination
    MPC_ADVANCED = "mpc"  # Model predictive control
    ML_ENHANCED = "ml_enhanced"  # ML-integrated control


class ValidationTier(Enum):
    """Multi-tier validation levels"""

    SYNTAX = "syntax"  # Basic syntax checking
    REQUIREMENTS = "requirements"  # Requirement coverage
    HALLUCINATION = "hallucination_detection"  # Enhanced hallucination detection
    BEST_PRACTICES = "best_practices"  # Code quality and best practices
    MATHEMATICAL = "mathematical"  # Mathematical accuracy
    PERFORMANCE = "performance"  # Performance benchmarks
    SAFETY = "safety"  # Safety compliance
    PRODUCTION = "production"  # Production readiness


class ValidationSeverity(Enum):
    """Validation issue severity levels for enhanced tracking"""

    CRITICAL = "critical"  # Blocks production deployment
    HIGH = "high"  # Must fix before release
    MEDIUM = "medium"  # Should fix for quality
    LOW = "low"  # Optional improvement
    INFO = "info"  # Informational only


class MemoryStrategy(Enum):
    """Memory system query strategies"""

    SPEED_OPTIMIZED = "speed"  # Redis-first for fast retrieval
    ACCURACY_OPTIMIZED = "accuracy"  # Neo4j for relationship accuracy
    COST_OPTIMIZED = "cost"  # PostgreSQL for cost efficiency
    BALANCED = "balanced"  # Adaptive routing


class DocumentationType(Enum):
    """Documentation types for generation"""

    API = "api"  # API documentation
    USER_GUIDE = "user_guide"  # User guide
    TECHNICAL = "technical"  # Technical documentation
    DEPLOYMENT = "deployment"  # Deployment guide
    ROADMAP = "roadmap"  # Roadmap updates
