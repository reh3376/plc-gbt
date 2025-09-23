# AI Task Orchestrator API Reference

## Table of Contents

1. [Core API](#core-api)
2. [Configuration API](#configuration-api)
3. [Memory API](#memory-api)
4. [Utils API](#utils-api)
5. [Domain API](#domain-api)
6. [Testing API](#testing-api)

## Core API

### AITaskOrchestrator

The main orchestrator class that coordinates all subsystems.

```python
from plc_orchestrator import AITaskOrchestrator

class AITaskOrchestrator:
    def __init__(self, config: OrchestratorConfig | None = None):
        """
        Initialize the AI Task Orchestrator.
        
        Args:
            config: Configuration object. If None, uses default settings.
        """
```

#### Methods

##### analyze_task

```python
def analyze_task(
    self,
    task_description: str,
    context: dict[str, Any] | None = None
) -> TaskAnalysis:
    """
    Analyze a task to extract requirements, complexity, and approach.
    
    Args:
        task_description: Natural language description of the task
        context: Additional context (e.g., existing code, constraints)
        
    Returns:
        TaskAnalysis object containing:
        - requirements: List of extracted requirements
        - complexity: Task complexity rating
        - technologies: Detected technologies
        - approach: Recommended implementation approach
        - risks: Identified risks and challenges
        
    Example:
        >>> orchestrator = AITaskOrchestrator()
        >>> analysis = orchestrator.analyze_task(
        ...     "Build a REST API for user management"
        ... )
        >>> print(analysis.complexity)
        'moderate'
    """
```

##### generate_guide

```python
def generate_guide(
    self,
    analysis: TaskAnalysis,
    format: str = "markdown"
) -> ImplementationGuide:
    """
    Generate a structured implementation guide.
    
    Args:
        analysis: Task analysis result
        format: Output format ('markdown', 'json', 'html')
        
    Returns:
        ImplementationGuide with step-by-step instructions
        
    Example:
        >>> guide = orchestrator.generate_guide(analysis)
        >>> for step in guide.steps:
        ...     print(f"{step.number}. {step.title}")
    """
```

##### validate_implementation

```python
def validate_implementation(
    self,
    code: str,
    requirements: list[str] | None = None,
    tier: ValidationTier | str = ValidationTier.STANDARD
) -> ValidationResult:
    """
    Validate code implementation against requirements.
    
    Args:
        code: Implementation code to validate
        requirements: List of requirements to check
        tier: Validation tier (BASIC, STANDARD, COMPREHENSIVE, SECURITY)
        
    Returns:
        ValidationResult containing:
        - passed: Overall validation status
        - score: Validation score (0-100)
        - issues: List of identified issues
        - suggestions: Improvement suggestions
    """
```

### TaskAnalyzer

Analyzes tasks to extract structured information.

```python
from plc_orchestrator.core import TaskAnalyzer

class TaskAnalyzer:
    def analyze(
        self,
        description: str,
        context: dict[str, Any] | None = None
    ) -> TaskAnalysis:
        """Analyze task description and extract metadata."""
```

### TaskValidator

Validates code implementations with multi-tier checking.

```python
from plc_orchestrator.core import TaskValidator

class TaskValidator:
    def validate(
        self,
        code: str,
        requirements: list[str] | None = None,
        tier: ValidationTier = ValidationTier.STANDARD
    ) -> ValidationResult:
        """Validate code against requirements and best practices."""
```

### ProgressMonitor

Tracks and reports task execution progress.

```python
from plc_orchestrator.core import ProgressMonitor

class ProgressMonitor:
    def start_task(self, task_id: str, total_steps: int) -> None:
        """Start tracking a new task."""
        
    def update_progress(
        self,
        task_id: str,
        completed_steps: int,
        message: str | None = None
    ) -> None:
        """Update task progress."""
        
    def get_status(self, task_id: str) -> TaskStatus:
        """Get current task status."""
```

## Configuration API

### OrchestratorConfig

Main configuration class using Pydantic.

```python
from plc_orchestrator.config import OrchestratorConfig

class OrchestratorConfig:
    def __init__(
        self,
        config_file: str | None = None,
        **kwargs
    ):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file
            **kwargs: Override specific settings
            
        Environment variables:
            - ORCHESTRATOR_ENVIRONMENT
            - OPENAI_API_KEY
            - WOLFRAM_ALPHA_APP_ID
            - ENABLE_MEMORY
            - MEMORY_STRATEGY
        """
```

#### Configuration Options

```python
# Core settings
app_name: str = "AI Task Orchestrator"
environment: str = "development"  # development, production, test
log_level: str = "INFO"

# API settings
openai_api_key: str | None = None
openai_model: str = "gpt-4"
wolfram_alpha_app_id: str | None = None
api_timeout: int = 30
max_retries: int = 3

# Memory settings
enable_memory: bool = True
memory_strategy: str = "balanced"  # speed, accuracy, cost, balanced
redis_url: str | None = None
neo4j_url: str | None = None
postgresql_url: str | None = None
qdrant_url: str | None = None

# Validation settings
validation_tier: str = "standard"
enable_security_checks: bool = True
max_code_complexity: int = 10

# Performance settings
cache_enabled: bool = True
cache_ttl: int = 3600
max_workers: int = 4
```

### Validators

Configuration validation utilities.

```python
from plc_orchestrator.config import validate_config

def validate_config(config: dict[str, Any]) -> None:
    """
    Validate configuration values.
    
    Raises:
        ConfigurationError: If configuration is invalid
    """
```

## Memory API

### MemoryCoordinator

Coordinates memory operations across different storage backends.

```python
from plc_orchestrator.memory import MemoryCoordinator

class MemoryCoordinator:
    def __init__(
        self,
        config: MemoryConfig,
        adapters: dict[str, BaseMemoryAdapter] | None = None
    ):
        """Initialize memory coordinator with adapters."""
```

#### Methods

##### store

```python
async def store(
    self,
    key: str,
    value: Any,
    ttl: int | None = None,
    adapter: str | None = None
) -> bool:
    """
    Store value in memory.
    
    Args:
        key: Storage key
        value: Value to store
        ttl: Time-to-live in seconds
        adapter: Force specific adapter
        
    Returns:
        Success status
    """
```

##### retrieve

```python
async def retrieve(
    self,
    key: str,
    adapter: str | None = None
) -> Any | None:
    """
    Retrieve value from memory.
    
    Args:
        key: Storage key
        adapter: Force specific adapter
        
    Returns:
        Stored value or None
    """
```

##### search

```python
async def search(
    self,
    query: MemoryQuery,
    adapter: str | None = None
) -> list[MemorySearchResult]:
    """
    Search memory with complex queries.
    
    Args:
        query: Search query object
        adapter: Force specific adapter
        
    Returns:
        List of matching results
    """
```

### Memory Adapters

Base protocol for memory adapters:

```python
from plc_orchestrator.memory.adapters import MemoryAdapterProtocol

class MemoryAdapterProtocol(Protocol):
    async def connect(self) -> None:
        """Establish connection to storage backend."""
        
    async def disconnect(self) -> None:
        """Close connection to storage backend."""
        
    async def store(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> bool:
        """Store value with optional TTL."""
        
    async def retrieve(self, key: str) -> Any | None:
        """Retrieve value by key."""
        
    async def delete(self, key: str) -> bool:
        """Delete value by key."""
        
    async def search(
        self,
        query: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Search with backend-specific query."""
```

### Query Builder

Build complex memory queries:

```python
from plc_orchestrator.memory import MemoryQuery

query = MemoryQuery()
    .filter("type", "task")
    .filter("status", "completed")
    .date_range("created_at", start="2024-01-01")
    .sort_by("score", descending=True)
    .limit(10)

results = await coordinator.search(query)
```

## Utils API

### Data Models

Common data structures used throughout the system.

```python
from plc_orchestrator.utils.data_models import (
    TaskAnalysis,
    ValidationResult,
    ExecutionStep,
    DeploymentChecklist,
    TestCase
)

@dataclass
class TaskAnalysis:
    task_description: str
    requirements: list[str]
    complexity: str
    estimated_time: str
    technologies: list[str]
    dependencies: list[str]
    approach: str
    risks: list[str]
    validation_criteria: list[str]
```

### Error Handling

Custom exception hierarchy:

```python
from plc_orchestrator.utils.errors import (
    OrchestratorError,
    ConfigurationError,
    ValidationError,
    AnalysisError,
    MemoryError
)

# Usage
try:
    result = orchestrator.analyze_task(task)
except AnalysisError as e:
    print(f"Analysis failed: {e.message}")
    print(f"Details: {e.details}")
```

### Retry Decorator

Automatic retry with exponential backoff:

```python
from plc_orchestrator.utils.retry import retry

@retry(
    attempts=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(ConnectionError, TimeoutError)
)
async def flaky_operation():
    """Operation that might fail transiently."""
    pass
```

### Performance Tools

#### Caching

```python
from plc_orchestrator.utils.performance import cache_result

@cache_result(max_size=100, ttl=3600)
def expensive_computation(param: str) -> dict:
    """Results will be cached for 1 hour."""
    return compute_result(param)
```

#### Performance Monitoring

```python
from plc_orchestrator.utils.performance import PerformanceMonitor

monitor = PerformanceMonitor()

with monitor.measure("api_call"):
    response = await make_api_call()
    
print(monitor.get_summary())
# {'api_call': {'count': 1, 'avg_time': 0.234, 'max_time': 0.234}}
```

#### Resource Pooling

```python
from plc_orchestrator.utils.performance import ResourcePool

# Create connection pool
pool = ResourcePool(
    factory=create_connection,
    max_size=10,
    timeout=30
)

async with pool.acquire() as conn:
    await conn.execute(query)
```

### Logging

Structured logging configuration:

```python
from plc_orchestrator.utils.logging import setup_logging

# Configure structured logging
logger = setup_logging(
    level="INFO",
    format="json",
    add_trace_id=True
)

# Use structured logging
logger.info(
    "Task completed",
    task_id="123",
    duration=1.5,
    status="success"
)
```

### Helpers

Utility functions:

```python
from plc_orchestrator.utils.helpers import (
    extract_code_blocks,
    clean_description,
    parse_technologies,
    estimate_complexity,
    calculate_complexity_score
)

# Extract code from markdown
code_blocks = extract_code_blocks(markdown_text)
for block in code_blocks:
    print(f"Language: {block.language}")
    print(f"Code: {block.code}")
```

## Domain API

### Control Systems

PLC and industrial control system utilities:

```python
from plc_orchestrator.domain.control_systems import (
    ControlSystemsAnalyzer,
    PLCLanguage,
    HardwareRequirement
)

analyzer = ControlSystemsAnalyzer()

# Analyze control system task
result = analyzer.analyze(
    task="Implement PID control for temperature",
    platform="allen_bradley"
)

# Validate PLC code
validation = analyzer.validate_plc_code(
    code=ladder_logic,
    platform="siemens",
    safety_level="SIL2"
)
```

### Mathematical

Mathematical validation and computation:

```python
from plc_orchestrator.domain.mathematical import (
    MathematicalValidator,
    ExpressionType
)

validator = MathematicalValidator()

# Validate mathematical expression
result = validator.validate_expression(
    "integrate(x^2 * sin(x), x, 0, pi)"
)

# Use WolframAlpha for validation
wolfram_result = validator.wolfram_validate(
    expression="d/dx (x^3 + 2x) = 3x^2 + 2"
)
```

## Testing API

### Test Fixtures

Pre-built test data generators:

```python
from plc_orchestrator.testing.fixtures import (
    create_test_orchestrator,
    create_test_task,
    create_test_analysis_result,
    create_test_validation_result
)

# Create test orchestrator
orchestrator = create_test_orchestrator(
    enable_memory=True,
    mock_external_apis=True
)

# Generate test data
task = create_test_task(
    complexity="moderate",
    technologies=["python", "fastapi"]
)
```

### Mock Objects

Mock implementations for testing:

```python
from plc_orchestrator.testing.mocks import (
    MockWolframAlphaClient,
    MockMemoryAdapter,
    MockOpenAIClient
)

# Mock WolframAlpha
mock_wolfram = MockWolframAlphaClient()
mock_wolfram.add_response(
    query="solve x^2 = 4",
    response={"solutions": ["2", "-2"]}
)
```

### Test Helpers

Testing utility functions:

```python
from plc_orchestrator.testing.helpers import (
    assert_valid_analysis,
    assert_valid_guide,
    compare_implementations,
    measure_performance,
    create_memory_test_suite
)

# Validate analysis structure
assert_valid_analysis(analysis_result)

# Compare code implementations
diff = compare_implementations(
    original_code,
    optimized_code,
    check_behavior=True
)
```

## Complete Example

Here's a complete example using multiple APIs:

```python
from plc_orchestrator import create_orchestrator
from plc_orchestrator.config import OrchestratorConfig
from plc_orchestrator.utils.performance import measure_execution_time
from plc_orchestrator.utils.retry import retry
import asyncio

@retry(attempts=3)
@measure_execution_time
async def process_task(task_description: str):
    """Process a task with full orchestration."""
    
    # Create configured orchestrator
    config = OrchestratorConfig(
        environment="production",
        enable_memory=True,
        memory_strategy="balanced",
        validation_tier="comprehensive"
    )
    
    orchestrator = create_orchestrator(config=config)
    
    # Analyze task
    analysis = await orchestrator.analyze_task(task_description)
    print(f"Complexity: {analysis.complexity}")
    print(f"Technologies: {', '.join(analysis.technologies)}")
    
    # Generate implementation guide
    guide = await orchestrator.generate_guide(analysis)
    print(f"Steps: {len(guide.steps)}")
    
    # Store in memory for later retrieval
    if orchestrator.memory_enabled:
        await orchestrator.memory.store(
            f"task:{analysis.task_id}",
            {
                "description": task_description,
                "analysis": analysis.to_dict(),
                "guide": guide.to_dict()
            },
            ttl=86400  # 24 hours
        )
    
    return analysis, guide

# Run the example
async def main():
    task = """
    Build a REST API for a library management system with:
    - Book CRUD operations
    - User authentication with JWT
    - Check-out/check-in functionality
    - Search with filters
    - PostgreSQL database
    """
    
    analysis, guide = await process_task(task)
    
    # Print the guide
    for step in guide.steps:
        print(f"\n{step.number}. {step.title}")
        print(f"   {step.description}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Codes

Common error codes and their meanings:

| Code | Error | Description |
|------|-------|-------------|
| E001 | ConfigurationError | Invalid configuration value |
| E002 | APIKeyMissing | Required API key not provided |
| E003 | ConnectionError | Cannot connect to external service |
| E004 | ValidationError | Code validation failed |
| E005 | AnalysisError | Task analysis failed |
| E006 | MemoryError | Memory operation failed |
| E007 | TimeoutError | Operation timed out |
| E008 | RateLimitError | API rate limit exceeded |
| E009 | AuthenticationError | Authentication failed |
| E010 | NotImplementedError | Feature not yet implemented |

## Version History

- **1.0.0**: Initial modular release
- **1.1.0**: Added performance optimization tools
- **1.2.0**: Enhanced error handling with retry mechanisms
- **1.3.0**: Added comprehensive testing utilities

## Additional Resources

- [Architecture Overview](architecture.md)
- [Configuration Guide](../CONFIGURATION_GUIDE.md)
- [Testing Guide](testing-guide.md)
- [Examples](../examples/)
