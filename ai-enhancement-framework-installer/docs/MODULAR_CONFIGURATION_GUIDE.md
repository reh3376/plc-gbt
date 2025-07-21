# 🔧 AI Enhancement Framework - Modular Configuration Guide

## 📋 Overview

The AI Enhancement Framework features a **modular architecture** that allows you to selectively enable or disable framework components based on your project needs. This guide explains how to configure and manage modules effectively.

## 🎯 Key Benefits

- **Lightweight Deployments**: Only load the components you need
- **Reduced Dependencies**: Avoid installing unnecessary packages
- **Flexible Configuration**: Enable/disable features without code changes  
- **Resource Optimization**: Lower memory usage and faster startup times
- **Development Focus**: Concentrate on specific framework capabilities

## 🏗️ Module Categories

### Core Modules
Always-available foundation components:
- **task_orchestrator**: AI Task Orchestrator for systematic task completion
- **memory_management**: Multi-database memory management system

### Analysis Modules
Code analysis and quality assessment:
- **code_analysis**: Advanced code analysis with hallucination detection
- **validation_framework**: 8-tier comprehensive validation framework

### Integration Modules
External service integrations:
- **wolfram_integration**: WolframAlpha Pro mathematical validation ⭐
- **llm_integration**: Fine-tuned LLM integration and domain expertise ⭐

### Provider Modules
Database and service abstractions:
- **database_providers**: Redis, Neo4j, PostgreSQL, Qdrant providers
- **model_providers**: AI model provider abstractions (OpenAI, local models)

### Optimization Modules
Code improvement and refactoring:
- **code_optimization**: Automated code optimization and refactoring
- **modular_extraction**: Function and class extraction to modules

### Utility Modules
Supporting functionality:
- **health_monitoring**: Health monitoring and metrics collection
- **docker_integration**: Docker containerization and orchestration

⭐ = Specifically mentioned in requirements

## 🚀 Quick Start

### 1. Check Current Configuration

```bash
# Show current module status
python -m ai_enhancement_framework.cli_modules status

# List all available modules
python -m ai_enhancement_framework.cli_modules list
```

### 2. Enable/Disable Modules

```bash
# Enable specific modules
python -m ai_enhancement_framework.cli_modules enable wolfram_integration llm_integration

# Disable modules you don't need
python -m ai_enhancement_framework.cli_modules disable database_providers docker_integration

# Validate configuration
python -m ai_enhancement_framework.cli_modules validate
```

### 3. Use in Python Code

```python
from ai_enhancement_framework import is_module_enabled, get_module_config

# Check if modules are enabled
if is_module_enabled("wolfram_integration"):
    from ai_enhancement_framework import MathematicalValidationOrchestrator
    # Use WolframAlpha features

if is_module_enabled("llm_integration"):
    from ai_enhancement_framework import LLMIntegration
    # Use fine-tuned LLM features

# Get full configuration
config = get_module_config()
print(f"Enabled modules: {list(config.get_enabled_modules().keys())}")
```

## 🛠️ Configuration Methods

### Method 1: CLI Tool (Recommended)

The easiest way to manage modules:

```bash
# Basic commands
python -m ai_enhancement_framework.cli_modules status
python -m ai_enhancement_framework.cli_modules enable wolfram_integration
python -m ai_enhancement_framework.cli_modules disable database_providers
python -m ai_enhancement_framework.cli_modules validate

# Advanced commands
python -m ai_enhancement_framework.cli_modules reset
python -m ai_enhancement_framework.cli_modules export my_config.json
python -m ai_enhancement_framework.cli_modules import my_config.json
```

### Method 2: Python API

Programmatic configuration:

```python
from ai_enhancement_framework import enable_features, disable_features, print_module_status

# Enable multiple features
enable_features("wolfram_integration", "llm_integration")

# Disable features  
disable_features("database_providers", "docker_integration")

# Show status
print_module_status()
```

### Method 3: Environment Variables

Override configuration with environment variables:

```bash
# Enable/disable specific modules
export AI_FRAMEWORK_WOLFRAM_ALPHA=true
export AI_FRAMEWORK_LLM_INTEGRATION=true
export AI_FRAMEWORK_DATABASE_PROVIDERS=false

# Run your application
python your_app.py
```

### Method 4: Configuration File

Direct JSON configuration (`.ai_framework_modules.json`):

```json
{
  "wolfram_integration": {
    "enabled": true,
    "description": "WolframAlpha Pro mathematical validation"
  },
  "llm_integration": {
    "enabled": true,
    "description": "Fine-tuned LLM integration and domain expertise"
  },
  "database_providers": {
    "enabled": false,
    "description": "Database provider abstractions"
  }
}
```

## 📊 Common Configuration Scenarios

### Scenario 1: Minimal AI Assistant

For basic AI assistance without external integrations:

```bash
# Disable optional integrations
python -m ai_enhancement_framework.cli_modules disable wolfram_integration llm_integration database_providers docker_integration

# Keep core functionality
python -m ai_enhancement_framework.cli_modules enable task_orchestrator code_analysis validation_framework
```

**Result**: Lightweight framework with core AI features only.

### Scenario 2: Full AI + Math Integration

For projects needing mathematical validation:

```bash
# Enable AI and mathematical features
python -m ai_enhancement_framework.cli_modules enable wolfram_integration llm_integration task_orchestrator

# Disable heavy database components if not needed
python -m ai_enhancement_framework.cli_modules disable database_providers
```

**Result**: AI + WolframAlpha Pro capabilities without database overhead.

### Scenario 3: Code Analysis Only

For pure code analysis and optimization:

```bash
# Enable analysis modules
python -m ai_enhancement_framework.cli_modules enable code_analysis validation_framework code_optimization modular_extraction

# Disable AI integrations
python -m ai_enhancement_framework.cli_modules disable wolfram_integration llm_integration database_providers model_providers
```

**Result**: Focus on code quality and refactoring tools.

### Scenario 4: Full Enterprise Setup

For comprehensive enterprise deployment:

```bash
# Enable everything
python -m ai_enhancement_framework.cli_modules reset

# Validate all components
python -m ai_enhancement_framework.cli_modules validate
```

**Result**: Complete framework with all capabilities.

## 🔍 Dependency Management

The framework automatically manages dependencies between modules:

### Dependency Rules

- **code_optimization** requires **code_analysis**
- **modular_extraction** requires **code_analysis**  
- **validation_framework** optionally uses **wolfram_integration**

### Dependency Validation

```bash
# Check for dependency issues
python -m ai_enhancement_framework.cli_modules validate

# Example output:
# ❌ Dependencies: Issues found
#   • Module 'code_optimization' requires 'code_analysis' but it's disabled
```

### Automatic Resolution

The framework will warn about dependency issues but won't automatically resolve them, giving you control over your configuration.

## 🌍 Environment-Specific Configurations

### Development Environment

```bash
# Enable debugging and development tools
export AI_FRAMEWORK_CODE_ANALYSIS=true
export AI_FRAMEWORK_VALIDATION_FRAMEWORK=true
export AI_FRAMEWORK_HEALTH_MONITORING=true
```

### Production Environment

```bash
# Minimal production setup
export AI_FRAMEWORK_TASK_ORCHESTRATOR=true
export AI_FRAMEWORK_WOLFRAM_ALPHA=true
export AI_FRAMEWORK_LLM_INTEGRATION=true
export AI_FRAMEWORK_DATABASE_PROVIDERS=false
export AI_FRAMEWORK_DOCKER=false
```

### Testing Environment

```bash
# Enable all modules for comprehensive testing
export AI_FRAMEWORK_CODE_ANALYSIS=true
export AI_FRAMEWORK_VALIDATION_FRAMEWORK=true
export AI_FRAMEWORK_WOLFRAM_ALPHA=true
export AI_FRAMEWORK_LLM_INTEGRATION=true
```

## 📦 Installation Considerations

### Package Dependencies

Different modules require different packages:

```python
# Core framework (always required)
pip install libcst astroid

# WolframAlpha integration (optional)
pip install requests

# LLM integration (optional)  
pip install openai transformers

# Database providers (optional)
pip install redis neo4j psycopg2 qdrant-client

# Docker integration (optional)
pip install docker

# Model providers (optional)
pip install torch
```

### Conditional Installation

Use the CLI to check what's needed:

```bash
# Validate configuration and see missing dependencies
python -m ai_enhancement_framework.cli_modules validate
```

## 🧪 Testing Module Configurations

### Test Individual Modules

```python
from ai_enhancement_framework.core.module_loader import get_module_loader

loader = get_module_loader()

# Test loading specific modules
wolfram = loader.load_module("wolfram_integration", required=False)
if wolfram:
    print("✅ WolframAlpha integration loaded successfully")
else:
    print("❌ WolframAlpha integration not available")
```

### Preload Testing

```bash
# Test all enabled modules
python -m ai_enhancement_framework.cli_modules validate

# Example output:
# 🧪 Testing module loading...
# 📊 Load Test: 8/10 modules loaded successfully
#   ✅ task_orchestrator
#   ✅ wolfram_integration
#   ❌ database_providers (missing dependencies)
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Module Import Errors

**Problem**: `ImportError: No module named 'wolfram_integration'`

**Solution**: 
```bash
# Check if module is enabled
python -m ai_enhancement_framework.cli_modules status

# Enable if needed
python -m ai_enhancement_framework.cli_modules enable wolfram_integration
```

#### 2. Dependency Conflicts

**Problem**: Dependency validation failures

**Solution**:
```bash
# Check dependencies
python -m ai_enhancement_framework.cli_modules validate

# Enable required dependencies
python -m ai_enhancement_framework.cli_modules enable code_analysis
```

#### 3. Configuration File Issues

**Problem**: Configuration not persisting

**Solution**:
```bash
# Reset to defaults
python -m ai_enhancement_framework.cli_modules reset

# Reconfigure
python -m ai_enhancement_framework.cli_modules enable wolfram_integration llm_integration
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from ai_enhancement_framework import get_module_loader
loader = get_module_loader()
# Detailed logs will show module loading process
```

## 📚 Advanced Usage

### Custom Module Configurations

```python
from ai_enhancement_framework.config import get_module_config

config = get_module_config()

# Get detailed module information
wolfram_info = config.get_module_info("wolfram_integration")
print(f"Dependencies: {wolfram_info['dependencies']}")
print(f"Requirements: {wolfram_info['requirements']}")

# Check availability
available = config.get_module_loader().check_module_availability("wolfram_integration")
print(f"Available: {available}")
```

### Conditional Feature Implementation

```python
from ai_enhancement_framework import is_module_enabled
from ai_enhancement_framework.core.module_loader import optional_module, requires_module

@optional_module("wolfram_integration")
def mathematical_validation(equation):
    """This function only runs if WolframAlpha is enabled"""
    from ai_enhancement_framework import validate_mathematical_code
    return validate_mathematical_code(equation)

@requires_module("llm_integration")  
def ai_analysis(code):
    """This function requires LLM integration to be enabled"""
    from ai_enhancement_framework import LLMIntegration
    llm = LLMIntegration()
    return llm.analyze_code(code)

# Usage
result = mathematical_validation("x^2 + 2x + 1")  # Returns None if disabled
ai_result = ai_analysis("def hello(): pass")  # Raises error if disabled
```

## 📋 Configuration Reference

### All Available Modules

| Module | Category | Default | Description |
|--------|----------|---------|-------------|
| `task_orchestrator` | Core | ✅ | AI Task Orchestrator for systematic task completion |
| `memory_management` | Core | ✅ | Multi-database memory management system |
| `code_analysis` | Analysis | ✅ | Advanced code analysis with hallucination detection |
| `wolfram_integration` | Integration | ✅ | WolframAlpha Pro mathematical validation |
| `llm_integration` | Integration | ✅ | Fine-tuned LLM integration and domain expertise |
| `database_providers` | Providers | ✅ | Database provider abstractions (Redis, Neo4j, PostgreSQL, Qdrant) |
| `model_providers` | Providers | ✅ | AI model provider abstractions |
| `code_optimization` | Optimization | ✅ | Automated code optimization and refactoring |
| `modular_extraction` | Optimization | ✅ | Automated function and class extraction to modules |
| `validation_framework` | Validation | ✅ | 8-tier comprehensive validation framework |
| `health_monitoring` | Utilities | ✅ | Health monitoring and metrics collection |
| `docker_integration` | Utilities | ✅ | Docker containerization and orchestration |

### Environment Variables

| Variable | Module | Description |
|----------|--------|-------------|
| `AI_FRAMEWORK_TASK_ORCHESTRATOR` | task_orchestrator | Enable/disable task orchestrator |
| `AI_FRAMEWORK_MEMORY_MANAGEMENT` | memory_management | Enable/disable memory management |
| `AI_FRAMEWORK_CODE_ANALYSIS` | code_analysis | Enable/disable code analysis |
| `AI_FRAMEWORK_WOLFRAM_ALPHA` | wolfram_integration | Enable/disable WolframAlpha integration |
| `AI_FRAMEWORK_LLM_INTEGRATION` | llm_integration | Enable/disable LLM integration |
| `AI_FRAMEWORK_DATABASE_PROVIDERS` | database_providers | Enable/disable database providers |
| `AI_FRAMEWORK_MODEL_PROVIDERS` | model_providers | Enable/disable model providers |
| `AI_FRAMEWORK_CODE_OPTIMIZATION` | code_optimization | Enable/disable code optimization |
| `AI_FRAMEWORK_MODULAR_EXTRACTION` | modular_extraction | Enable/disable modular extraction |
| `AI_FRAMEWORK_VALIDATION` | validation_framework | Enable/disable validation framework |
| `AI_FRAMEWORK_HEALTH_MONITORING` | health_monitoring | Enable/disable health monitoring |
| `AI_FRAMEWORK_DOCKER` | docker_integration | Enable/disable docker integration |

## 🎉 Summary

The AI Enhancement Framework's modular architecture provides:

✅ **Simple Configuration**: Easy enable/disable with CLI or Python API  
✅ **Flexible Deployment**: Choose only the features you need  
✅ **Environment Support**: Different configs for dev/test/prod  
✅ **Dependency Management**: Automatic validation and warnings  
✅ **Backward Compatibility**: Graceful fallbacks when modules unavailable  

Use the modular system to create lightweight, focused deployments that meet your specific project requirements while maintaining the full power of the AI Enhancement Framework when needed. 