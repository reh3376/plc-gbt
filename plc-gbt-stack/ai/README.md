# PLC Task Orchestrator - Modular Edition

A modular framework for AI-assisted task analysis, planning, and execution with multi-database memory integration and specialized domain support.

## 📚 Documentation

- **[Documentation Index](docs/index.md)** - Complete documentation overview
- **[Architecture Guide](docs/architecture.md)** - System design and components
- **[API Reference](docs/api-reference.md)** - Comprehensive API documentation
- **[Quick Start Guide](QUICK_START_GUIDE.md)** - Detailed getting started guide
- **[Testing Guide](docs/testing-guide.md)** - Testing strategies and utilities

## 🚀 Quick Start (60 seconds)

```python
from plc_orchestrator import create_orchestrator

# 1. Create orchestrator
orchestrator = create_orchestrator()

# 2. Analyze task
analysis = orchestrator.analyze_task("Create a PLC data parser")

# 3. Validate implementation
result = orchestrator.validate_implementation(code, analysis.requirements)

# 4. Generate documentation
orchestrator.create_summary_document()
```

## 📦 Installation

### Basic Installation
```bash
pip install -e .
```

### With Optional Features
```bash
# With memory system support
pip install -e ".[memory]"

# With all features
pip install -e ".[all]"

# For development
pip install -e ".[dev]"
```

## 🏗️ New Modular Architecture

The orchestrator has been refactored from a single 3000+ line file into a clean modular structure:

```
plc_orchestrator/
├── core/               # Core orchestration logic
│   ├── orchestrator.py # Main orchestrator (~500 lines)
│   ├── analyzer.py     # Task analysis
│   ├── validator.py    # Multi-tier validation
│   └── progress.py     # Progress monitoring
├── memory/             # Memory system integration
│   ├── coordinator.py  # Multi-DB coordination
│   └── adapters/       # Database adapters
├── domain/             # Domain-specific handlers
│   ├── control_systems.py
│   └── mathematical.py
├── config/             # Configuration management
│   ├── settings.py     # Pydantic-based config
│   └── validators.py
└── utils/              # Utilities
    ├── enums.py        # Enumerations
    ├── data_models.py  # Data structures
    ├── errors.py       # Custom exceptions
    └── helpers.py      # Helper functions
```

## 🔄 Migration from Monolithic Version

If you're upgrading from the old `ai_task_orchestrator.py`:

```bash
# Run migration helper
python migrate_to_modular.py your_code.py
```

### Key Changes:
```python
# Old
from ai_task_orchestrator import AITaskOrchestrator
orchestrator = AITaskOrchestrator(task_id="123")

# New
from plc_orchestrator import create_orchestrator
orchestrator = create_orchestrator(task_id="123")
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Application
ENVIRONMENT=development
LOG_LEVEL=INFO

# Memory System (optional)
ENABLE_MEMORY=true
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
POSTGRES_DSN=postgresql://user:pass@localhost/db
QDRANT_URL=http://localhost:6333

# Features
ENABLE_MATH_VALIDATION=true
ENABLE_CONTROL_ANALYSIS=true

# API Keys (optional)
WOLFRAM_ALPHA_API_KEY=your_key
OPENAI_API_KEY=your_key
```

### Programmatic Configuration
```python
orchestrator = create_orchestrator(
    enable_memory=True,
    enable_math_validation=True,
    log_level="DEBUG",
    timeout_seconds=600
)
```

## 🎯 Core Features

### 1. Task Analysis
```python
analysis = orchestrator.analyze_task(
    "Build a temperature control system with PID"
)

print(f"Complexity: {analysis.complexity}")
print(f"Requirements: {len(analysis.requirements)}")
print(f"Risks: {analysis.risks}")
```

### 2. Multi-Tier Validation
```python
from plc_orchestrator import ValidationTier

result = orchestrator.validate_implementation(
    code_content=implementation,
    validation_tier=ValidationTier.PRODUCTION
)

if not result.passed:
    for issue in result.get_critical_issues():
        print(f"CRITICAL: {issue['message']}")
```

### 3. Progress Monitoring
```python
# Add progress callback
def on_progress(update):
    print(f"[{update.percentage:.1f}%] {update.status}")

orchestrator.progress_monitor.add_progress_callback(on_progress)
```

### 4. Memory System Integration (Optional)
```python
# Memory system automatically enhances analysis if enabled
analysis = orchestrator.analyze_task("Create data pipeline")
# analysis.memory_insights contains similar implementations
```

### 5. Domain-Specific Support
```python
# Automatic control system analysis
if analysis.is_control_system_task():
    guidance = orchestrator.control_handler.get_guidance(task)
    print(guidance)
```

**Domain Guides:**
- [Control Systems Integration](docs/domain/control-systems.md) - PLC, SCADA, industrial automation
- [Mathematical Validation](docs/domain/mathematical.md) - Symbolic computation, numerical validation

## 📊 Validation Tiers

The orchestrator supports multiple validation tiers:

- **SYNTAX**: Basic syntax checking
- **REQUIREMENTS**: Requirement coverage
- **HALLUCINATION**: AI hallucination detection
- **BEST_PRACTICES**: Code quality checks
- **MATHEMATICAL**: Math validation (with WolframAlpha)
- **PERFORMANCE**: Performance analysis
- **SAFETY**: Safety compliance
- **PRODUCTION**: Production readiness

## 🔧 Advanced Usage

### Custom Configuration
```python
from plc_orchestrator.config import OrchestratorConfig

config = OrchestratorConfig(
    config_file="custom_config.yml",
    enable_memory=True,
    max_workers=8
)
orchestrator = AITaskOrchestrator(config=config)
```

### Direct Component Usage
```python
from plc_orchestrator.core import TaskAnalyzer, TaskValidator

# Use components independently
analyzer = TaskAnalyzer(config)
analysis = analyzer.analyze("Build REST API")

validator = TaskValidator(config)
result = validator.validate(code, requirements)
```

### Memory System Queries
```python
from plc_orchestrator.memory import QueryBuilder

# Find similar implementations
query = QueryBuilder.build_task_query(
    "implement caching layer",
    limit=5
)
response = await orchestrator.memory_coordinator.query(query)
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=plc_orchestrator tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **[Documentation Hub](docs/index.md)** - Complete documentation index
- **[Configuration Guide](CONFIGURATION_GUIDE.md)** - All configuration options
- **[Examples](examples/)** - Working code examples
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Migration Guide](TYPESCRIPT_MIGRATION_GUIDE.md)** - For TypeScript users
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## 🎉 Benefits of Modular Architecture

- **Maintainability**: Each module is focused and <500 lines
- **Testability**: Easy to test individual components
- **Flexibility**: Enable/disable features as needed
- **Performance**: Load only what you need
- **Extensibility**: Easy to add new domains/validators
- **Configuration**: Environment-based with validation

---

**Version 2.0.0** - Complete modular rewrite for better maintainability and extensibility.
