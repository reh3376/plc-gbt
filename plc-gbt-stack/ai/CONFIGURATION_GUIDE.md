# ⚙️ Configuration Guide - AI Task Orchestrator

## Overview

The AI Task Orchestrator uses a flexible configuration system based on environment variables and Pydantic settings management. Configuration can be provided through environment variables, `.env` files, or programmatically.

## Quick Start

1. **Copy a template**:
   ```bash
   cp config_templates/env.development .env
   ```

2. **Edit `.env`** with your settings

3. **Run the orchestrator**:
   ```python
   from plc_orchestrator import create_orchestrator
   
   # Automatically loads from .env
   orchestrator = create_orchestrator()
   ```

## Configuration Methods

### 1. Environment Variables

Set variables in your shell:
```bash
export ENVIRONMENT=production
export ENABLE_MEMORY=true
export REDIS_URL=redis://localhost:6379
```

### 2. .env File

Create a `.env` file in your project root:
```env
ENVIRONMENT=development
DEBUG=true
REDIS_URL=redis://localhost:6379
```

### 3. Programmatic Configuration

Override settings in code:
```python
orchestrator = create_orchestrator(
    environment="production",
    enable_memory=True,
    redis_url="redis://localhost:6379"
)
```

### 4. Configuration Object

Use the `OrchestratorConfig` class directly:
```python
from plc_orchestrator.config.settings import OrchestratorConfig

config = OrchestratorConfig(
    environment="production",
    enable_memory=True,
    max_workers=8
)
orchestrator = AITaskOrchestrator(config=config)
```

## Configuration Options

### Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | "PLC Task Orchestrator" | Application name for logging |
| `ENVIRONMENT` | enum | "development" | Environment: development, staging, production, test |
| `DEBUG` | boolean | false | Enable debug mode |
| `VERSION` | string | "2.0.0" | Application version |

### Path Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PROJECT_ROOT` | path | (current dir) | Project root directory |
| `CONTEXT_DIR` | path | "context" | Directory for context documents |
| `GUIDES_DIR` | path | "guides" | Directory for implementation guides |
| `SUMMARIES_DIR` | path | "summaries" | Directory for task summaries |

### Memory System

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_MEMORY` | boolean | true | Enable memory system integration |
| `REDIS_URL` | url | None | Redis connection URL |
| `NEO4J_URI` | url | None | Neo4j bolt URI |
| `NEO4J_USER` | string | None | Neo4j username |
| `NEO4J_PASSWORD` | string | None | Neo4j password |
| `POSTGRES_DSN` | url | None | PostgreSQL connection string |
| `QDRANT_URL` | url | None | Qdrant vector database URL |

### Feature Flags

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_MATH_VALIDATION` | boolean | true | Enable WolframAlpha validation |
| `ENABLE_PRODUCTION_CHECKS` | boolean | false | Enable production readiness checks |
| `ENABLE_CONTROL_ANALYSIS` | boolean | true | Enable control system features |
| `ENABLE_LLM_INTEGRATION` | boolean | false | Enable LLM integration features |

### Performance Tuning

| Variable | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `MAX_WORKERS` | integer | 4 | 1-100 | Maximum worker threads |
| `TIMEOUT_SECONDS` | integer | 300 | 10-3600 | Operation timeout |
| `CACHE_TTL` | integer | 3600 | 0-86400 | Cache time-to-live |
| `MAX_RETRIES` | integer | 3 | 0-10 | Maximum retry attempts |

### Logging Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | enum | "INFO" | Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `USE_STRUCTLOG` | boolean | true | Use structured logging |
| `LOG_FILE` | path | None | Log file path (stdout if not set) |

### API Keys

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `WOLFRAM_ALPHA_API_KEY` | string | If math validation enabled | WolframAlpha API key |
| `OPENAI_API_KEY` | string | If LLM integration enabled | OpenAI API key |

## Environment-Specific Settings

### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
MAX_WORKERS=2
TIMEOUT_SECONDS=60
```

### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=8
ENABLE_PRODUCTION_CHECKS=true
```

### Testing
```env
ENVIRONMENT=test
ENABLE_MEMORY=false
LOG_LEVEL=WARNING
TIMEOUT_SECONDS=10
CACHE_TTL=0
```

## Configuration Validation

The orchestrator validates configuration on startup:

```python
from plc_orchestrator.config.validators import validate_config

# This happens automatically
config = OrchestratorConfig()
validated_config = validate_config(config.dict())
```

### Validation Rules

1. **Environment**: Must be one of: development, staging, production, test
2. **URLs**: Must have valid format and correct scheme
3. **Numeric Values**: Must be within allowed ranges
4. **API Keys**: Must be at least 10 characters (if provided)
5. **Memory System**: If enabled, at least one adapter URL must be provided

## Best Practices

### 1. Use Environment Templates

Start with a template for your environment:
```bash
cp config_templates/env.production .env
# Edit .env with your specific values
```

### 2. Secure Sensitive Values

Never commit sensitive values to version control:
```env
# Use environment variable references
NEO4J_PASSWORD=${NEO4J_PROD_PASSWORD}
OPENAI_API_KEY=${OPENAI_API_KEY}
```

### 3. Override for Testing

Override specific settings for tests:
```python
test_orchestrator = create_orchestrator(
    environment="test",
    enable_memory=False,
    timeout_seconds=10
)
```

### 4. Validate Early

Check configuration at startup:
```python
try:
    orchestrator = create_orchestrator()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
```

## Common Patterns

### Minimal Development Setup
```env
ENVIRONMENT=development
DEBUG=true
```

### Full Production Setup
```env
ENVIRONMENT=production
ENABLE_MEMORY=true
REDIS_URL=redis://prod-redis:6379
NEO4J_URI=bolt://prod-neo4j:7687
POSTGRES_DSN=postgresql://user:pass@prod-db:5432/db
ENABLE_PRODUCTION_CHECKS=true
LOG_FILE=/var/log/orchestrator/app.log
```

### Memory-Only Development
```env
ENABLE_MEMORY=true
REDIS_URL=redis://localhost:6379
# Disable features not needed
ENABLE_MATH_VALIDATION=false
ENABLE_CONTROL_ANALYSIS=false
```

## Troubleshooting

### Configuration Not Loading

1. Check file location: `.env` should be in project root
2. Verify environment variable names (case-sensitive)
3. Check for syntax errors in `.env` file

### Validation Errors

```python
# Enable debug logging to see validation details
import logging
logging.basicConfig(level=logging.DEBUG)

orchestrator = create_orchestrator()
```

### Memory System Issues

If memory system fails to initialize:
1. Check connection URLs are correct
2. Verify services are running
3. Check network connectivity
4. Review credentials

## Configuration API Reference

### OrchestratorConfig Methods

```python
config = OrchestratorConfig()

# Get configuration as dictionary
config_dict = config.to_dict()

# Get specific sub-configurations
memory_config = config.get_memory_config()
logging_config = config.get_logging_config()

# Access settings directly
print(config.settings.environment)
print(config.settings.enable_memory)
```

### Environment Variable Mapping

The system automatically maps environment variables to settings:
- `ENABLE_MEMORY` → `config.settings.enable_memory`
- `REDIS_URL` → `config.settings.redis_url`
- `LOG_LEVEL` → `config.settings.log_level`

## Advanced Configuration

### Custom Validators

Add custom validation logic:
```python
from plc_orchestrator.config.validators import ConfigValidator

class CustomValidator(ConfigValidator):
    @staticmethod
    def validate_custom_setting(value: str) -> None:
        if not value.startswith("custom_"):
            raise ConfigurationError("Custom setting must start with 'custom_'")
```

### Dynamic Configuration

Load configuration from external sources:
```python
import json

# Load from JSON
with open("config.json") as f:
    config_data = json.load(f)

orchestrator = create_orchestrator(**config_data)
```

---

**Remember**: Configuration is loaded once at startup. Changes to environment variables or `.env` files require restarting the application.
