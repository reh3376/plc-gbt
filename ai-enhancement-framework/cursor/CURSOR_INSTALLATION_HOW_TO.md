# Cursor IDE Installation & Setup Guide - AI Enhancement Framework

## 📋 Overview

This guide provides comprehensive step-by-step instructions for installing and configuring the AI Enhancement Framework with Cursor IDE for optimal AI-assisted development.

## 🎯 Prerequisites

### System Requirements
- **Operating System**: macOS 10.15+, Ubuntu 18.04+, or Windows 10+
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 5GB free space
- **Internet Connection**: Required for initial setup and AI services

### Software Prerequisites
- **Cursor IDE**: Version 0.30.0 or later
- **Python**: 3.8 or later
- **Git**: For version control
- **Docker Desktop**: (Optional) For full service stack

## 🚀 Quick Installation (5 Minutes)

### Step 1: Install Cursor IDE
```bash
# macOS (via Homebrew)
brew install --cask cursor

# Linux (via AppImage)
curl -fsSL https://download.cursor.sh/linux/appimage/x64 -o cursor.appimage
chmod +x cursor.appimage
./cursor.appimage

# Windows (via Chocolatey)
choco install cursor
```

### Step 2: Install AI Enhancement Framework
```bash
# Navigate to the AI Enhancement Framework directory
cd ai-enhancement-framework

# Install framework in development mode (editable install)
pip install -e .

# Or install with full features (includes all optional dependencies)
pip install -e .[full]

# Verify installation
python -c "from ai_enhancement_framework.core import AITaskOrchestrator; print('Installation successful!')"
```

### Step 3: Initialize Framework in Your Project
```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize AI Enhancement Framework
python -m ai_enhancement_framework init

# Open in Cursor
cursor .
```

### Step 4: Verify Integration
1. Open Cursor IDE in your project
2. Create a new Python file: `test_ai_framework.py`
3. Add this code:
```python
from ai_enhancement_framework.core import AITaskOrchestrator

orchestrator = AITaskOrchestrator()
analysis = orchestrator.analyze_task("Create a simple function")
print(f"Task complexity: {analysis.complexity}")
```
4. Run the file - you should see the task complexity output

**🎉 Quick Setup Complete!** The framework is now active in your Cursor environment.

## 🔧 Detailed Installation & Configuration

### Platform-Specific Installation

#### macOS Installation
```bash
# 1. Install Cursor IDE
brew install --cask cursor

# 2. Install Python and dependencies
brew install python@3.11
python3 -m pip install --upgrade pip

# 3. Install AI Enhancement Framework
# Navigate to the AI Enhancement Framework directory
cd ai-enhancement-framework

# Install in development mode with full features
pip3 install -e .[full]

# 4. Optional: Install Docker for full services
brew install --cask docker

# 5. Start Docker services (if using full stack)
docker-compose -f ai-enhancement-framework/docker/docker-compose.yml up -d
```

#### Ubuntu/Linux Installation
```bash
# 1. Install Cursor IDE
curl -fsSL https://download.cursor.sh/linux/appimage/x64 -o cursor.appimage
chmod +x cursor.appimage
sudo mv cursor.appimage /usr/local/bin/cursor

# 2. Install Python and dependencies
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# 3. Install AI Enhancement Framework
# Navigate to the AI Enhancement Framework directory
cd ai-enhancement-framework

# Install in development mode with full features
pip3 install -e .[full]

# 4. Optional: Install Docker
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# 5. Start Docker services (if using full stack)
docker-compose -f ai-enhancement-framework/docker/docker-compose.yml up -d
```

#### Windows Installation
```powershell
# 1. Install Cursor IDE via Chocolatey
choco install cursor

# Alternative: Download and install from https://cursor.sh

# 2. Install Python
# Download from https://python.org and install Python 3.11+

# 3. Install AI Enhancement Framework
# Navigate to the AI Enhancement Framework directory
cd ai-enhancement-framework

# Install in development mode with full features
pip install -e .[full]

# 4. Optional: Install Docker Desktop
# Download from https://docker.com/products/docker-desktop

# 5. Start Docker services (if using full stack)
docker-compose -f ai-enhancement-framework/docker/docker-compose.yml up -d
```

### Framework Configuration

#### Automatic Configuration (Recommended)
```bash
# Run automatic setup wizard
python -m ai_enhancement_framework setup --cursor

# This will:
# 1. Detect your project type
# 2. Generate optimal .cursorrules configuration
# 3. Set up workspace settings
# 4. Configure memory persistence
# 5. Test all integrations
```

#### Manual Configuration

##### 1. Create .cursorrules File
Create `.cursorrules` in your project root:
```yaml
# AI Enhancement Framework - Cursor Rules

# Core Framework Behavior
ai_agent:
  task_orchestrator: true
  memory_management: true
  code_analysis: true
  
# Development Context
project_type: "python"  # or "web_app", "data_science", "api_service", etc.
memory_tier_preference: "balanced"
analysis_level: "comprehensive"

# Code Quality Standards
quality_gates:
  type_hints: required
  docstrings: required
  test_coverage: 95%
  complexity_limit: 10

# AI Assistant Preferences
assistant_behavior:
  methodical_approach: true
  comprehensive_analysis: true
  production_ready_code: true
  documentation_focus: true

# Memory Persistence
memory:
  enabled: true
  project_id: "{{ project_name }}"
  context_auto_refresh: true
  
# Framework Integration
framework:
  ai_enhancement: true
  auto_analysis: true
  validation_on_save: true
```

##### 2. Create Workspace Settings
Create `.vscode/settings.json`:
```json
{
  "ai.framework.enabled": true,
  "ai.framework.mode": "development",
  "ai.framework.memory_persistence": true,
  "ai.framework.context_auto_load": true,
  
  "files.associations": {
    "*.cursorrules": "yaml",
    "*.ai-config": "json"
  },
  
  "extensions.recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter"
  ],
  
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.linting.enabled": true,
  
  "ai.framework.analysis": {
    "enableOnSave": true,
    "qualityThreshold": 80,
    "hallucinationDetection": true
  }
}
```

##### 3. Initialize Virtual Environment
```bash
# Create virtual environment
python -m venv ai-enhancement-env

# Activate environment
# On macOS/Linux:
source ai-enhancement-env/bin/activate
# On Windows:
ai-enhancement-env\Scripts\activate

# Navigate to the AI Enhancement Framework directory
cd ai-enhancement-framework

# Install framework in development mode with full features
pip install -e .[full]

# Update Cursor settings to use this environment
echo '{"python.defaultInterpreterPath": "./ai-enhancement-env/bin/python"}' > .vscode/settings.json
```

## 🛠 Advanced Setup Options

### Full Service Stack Installation

#### Docker Compose Setup (Recommended)
```bash
# 1. Download the complete stack
curl -o docker-compose.yml https://raw.githubusercontent.com/ai-framework/ai-enhancement-framework/main/docker/docker-compose.yml

# 2. Start all services
docker-compose up -d

# 3. Verify services are running
docker-compose ps

# 4. Check service health
curl http://localhost:6379/ping  # Redis
curl http://localhost:7474       # Neo4j
curl http://localhost:5432       # PostgreSQL (requires psql)
curl http://localhost:6333       # Qdrant
```

#### Individual Service Installation
```bash
# Redis (for fast caching)
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Neo4j (for knowledge graphs)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.15-community

# PostgreSQL (for persistent storage)
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_DB=ai_framework \
  -e POSTGRES_USER=ai_user \
  -e POSTGRES_PASSWORD=ai_password \
  postgres:15-alpine

# Qdrant (for vector search)
docker run -d --name qdrant \
  -p 6333:6333 \
  qdrant/qdrant:latest
```

### Environment Configuration

#### Production Configuration
```bash
# Set production environment variables
export AI_FRAMEWORK_ENV=production
export AI_FRAMEWORK_LOG_LEVEL=INFO
export AI_FRAMEWORK_MEMORY_ENABLED=true

# Database connections
export AI_FRAMEWORK_REDIS_URL="redis://localhost:6379"
export AI_FRAMEWORK_NEO4J_URI="bolt://localhost:7687"
export AI_FRAMEWORK_POSTGRES_URL="postgresql://ai_user:ai_password@localhost:5432/ai_framework"
export AI_FRAMEWORK_QDRANT_URL="http://localhost:6333"
```

#### Development Configuration
```bash
# Set development environment variables
export AI_FRAMEWORK_ENV=development
export AI_FRAMEWORK_LOG_LEVEL=DEBUG
export AI_FRAMEWORK_ANALYSIS_DEPTH=comprehensive
export AI_FRAMEWORK_VALIDATION_STRICT=true
```

## 🔍 Verification & Testing

### Basic Functionality Test
```python
# test_framework_integration.py
import asyncio
from ai_enhancement_framework.core import (
    AITaskOrchestrator,
    UniversalMemoryManager,
    UniversalCodeAnalyzer
)

async def test_framework():
    print("🧪 Testing AI Enhancement Framework Integration...")
    
    # Test Task Orchestrator
    print("1. Testing Task Orchestrator...")
    orchestrator = AITaskOrchestrator()
    analysis = orchestrator.analyze_task("Create a simple web API")
    assert analysis.complexity in ['simple', 'moderate', 'complex', 'extensive']
    print(f"   ✅ Task analysis working: {analysis.complexity}")
    
    # Test Memory Manager (if services available)
    try:
        print("2. Testing Memory Manager...")
        memory = UniversalMemoryManager()
        await memory.initialize()
        
        # Test basic storage and retrieval
        await memory.store("test_key", {"test": "data"}, "test_data")
        result = await memory.retrieve("test_key")
        assert result is not None
        print(f"   ✅ Memory management working")
        
    except Exception as e:
        print(f"   ⚠️  Memory services not available: {e}")
        print("   ℹ️  This is normal if Docker services aren't running")
    
    # Test Code Analyzer
    print("3. Testing Code Analyzer...")
    analyzer = UniversalCodeAnalyzer()
    test_code = """
def hello_world():
    print("Hello, World!")
    return True
"""
    analysis = analyzer.analyze_content(test_code)
    assert analysis.quality_score > 0
    print(f"   ✅ Code analysis working: {analysis.quality_score}% quality")
    
    print("\n🎉 All tests passed! Framework is ready for use.")

if __name__ == "__main__":
    asyncio.run(test_framework())
```

Run the test:
```bash
python test_framework_integration.py
```

### Cursor IDE Integration Test
1. Open Cursor IDE in your project
2. Create a new Python file with intentionally poor code:
```python
# bad_code_example.py
def bad_function(x):
    # This function has issues
    import os  # unused import
    y = x + 1
    print(y)  # should use logging
    return y
```
3. Save the file
4. Check if Cursor provides AI-enhanced suggestions
5. Verify that the framework detects code quality issues

### Performance Verification
```python
# performance_test.py
import time
from ai_enhancement_framework.core import AITaskOrchestrator, UniversalCodeAnalyzer

def test_performance():
    print("⚡ Testing Framework Performance...")
    
    # Test task analysis speed
    orchestrator = AITaskOrchestrator()
    start_time = time.time()
    for i in range(10):
        analysis = orchestrator.analyze_task(f"Task {i}: Create a function")
    analysis_time = (time.time() - start_time) / 10
    print(f"Average task analysis time: {analysis_time:.3f}s")
    
    # Test code analysis speed
    analyzer = UniversalCodeAnalyzer()
    test_code = "def test(): pass\n" * 100  # 100 lines
    
    start_time = time.time()
    analysis = analyzer.analyze_content(test_code)
    code_analysis_time = time.time() - start_time
    lines_per_second = 100 / code_analysis_time
    print(f"Code analysis speed: {lines_per_second:.0f} lines/second")
    
    # Performance assertions
    assert analysis_time < 0.5, "Task analysis should be under 500ms"
    assert lines_per_second > 200, "Code analysis should be over 200 lines/second"
    
    print("✅ Performance tests passed!")

if __name__ == "__main__":
    test_performance()
```

## 🎛 Configuration Options

### Memory Configuration
```yaml
# ai_framework_config.yaml
memory:
  # Enable/disable memory system
  enabled: true
  
  # Memory tiers configuration
  tiers:
    redis:
      enabled: true
      url: "redis://localhost:6379"
      max_connections: 10
    
    neo4j:
      enabled: true
      uri: "bolt://localhost:7687"
      auth: ["neo4j", "password"]
    
    postgresql:
      enabled: true
      url: "postgresql://ai_user:ai_password@localhost:5432/ai_framework"
      pool_size: 5
    
    qdrant:
      enabled: true
      url: "http://localhost:6333"
      collection_name: "ai_framework"

  # Memory behavior
  auto_cleanup: true
  cleanup_interval: 3600  # seconds
  max_memory_usage: "1GB"
```

### Analysis Configuration
```yaml
analysis:
  # Quality thresholds
  quality_threshold: 80
  complexity_limit: 10
  
  # Analysis features
  syntax_validation: true
  hallucination_detection: true
  security_analysis: true
  performance_analysis: true
  
  # Output preferences
  detailed_reports: true
  suggestions_enabled: true
  auto_fix_suggestions: false
```

### Cursor-Specific Configuration
```yaml
cursor:
  # IDE integration
  auto_analysis: true
  validation_on_save: true
  context_auto_refresh: true
  
  # AI assistant behavior
  methodical_approach: true
  comprehensive_documentation: true
  production_ready_focus: true
  
  # Memory persistence
  session_memory: true
  project_memory: true
  cross_session_learning: true
```

## 🚨 Troubleshooting

### Common Installation Issues

#### Issue: "Module not found" error
```bash
# Solution: Ensure proper virtual environment
python -m venv ai-enhancement-env
source ai-enhancement-env/bin/activate  # On macOS/Linux

# Navigate to the AI Enhancement Framework directory
cd ai-enhancement-framework

# Install in development mode with full features
pip install -e .[full]
```

#### Issue: Cursor not recognizing framework
```bash
# Solution: Check Cursor settings
# 1. Open Cursor settings (Cmd/Ctrl + ,)
# 2. Search for "python interpreter"
# 3. Set to your virtual environment Python
# 4. Restart Cursor
```

#### Issue: Memory services connection failed
```bash
# Solution: Check Docker services
docker-compose ps

# Restart services if needed
docker-compose down
docker-compose up -d

# Verify connectivity
curl http://localhost:6379/ping
```

#### Issue: Performance is slow
```bash
# Solution: Optimize configuration
export AI_FRAMEWORK_ANALYSIS_DEPTH=standard  # Instead of comprehensive
export AI_FRAMEWORK_MEMORY_ENABLED=false     # Disable if not needed
```

### Docker Issues

#### Issue: Docker services won't start
```bash
# Check Docker is running
docker --version

# Check available resources
docker system df

# Clean up if needed
docker system prune

# Restart Docker Desktop (macOS/Windows)
```

#### Issue: Port conflicts
```bash
# Find what's using ports
lsof -i :6379  # Redis
lsof -i :7474  # Neo4j
lsof -i :5432  # PostgreSQL
lsof -i :6333  # Qdrant

# Modify docker-compose.yml to use different ports if needed
```

### Permission Issues

#### macOS/Linux Permission Issues
```bash
# Fix Python permissions
sudo chown -R $(whoami) /usr/local/lib/python3.*/site-packages

# Fix pip permissions
python -m pip install --user --upgrade pip
```

#### Windows Permission Issues
```powershell
# Navigate to the AI Enhancement Framework directory first
cd ai-enhancement-framework

# Run as Administrator or use:
pip install --user -e .[full]
```

## 📈 Performance Optimization

### Memory Optimization
```python
# Optimize memory usage
import os
os.environ['AI_FRAMEWORK_MEMORY_LIMIT'] = '512MB'
os.environ['AI_FRAMEWORK_CACHE_SIZE'] = '100MB'
```

### Analysis Optimization
```python
# Configure for your use case
from ai_enhancement_framework.core import configure_analysis

# Fast analysis for development
configure_analysis(
    depth='standard',
    hallucination_detection=True,
    security_analysis=False,  # Disable if not needed
    performance_analysis=False
)

# Comprehensive analysis for production
configure_analysis(
    depth='comprehensive',
    hallucination_detection=True,
    security_analysis=True,
    performance_analysis=True
)
```

## 🔄 Updates & Maintenance

### Updating the Framework
```bash
# Navigate to the AI Enhancement Framework directory
cd ai-enhancement-framework

# Update to latest version (reinstall in development mode)
pip install --upgrade -e .[full]

# Update Docker services
docker-compose pull
docker-compose up -d
```

### Health Checks
```python
# Regular health check script
from ai_enhancement_framework.core import health_check

async def daily_health_check():
    status = await health_check()
    print(f"Framework health: {status}")
    
    if not status.all_healthy:
        print("Issues detected:")
        for service, issue in status.issues.items():
            print(f"  {service}: {issue}")

# Run health check
import asyncio
asyncio.run(daily_health_check())
```

## 📚 Next Steps

### Getting Started
1. **Complete the verification tests** above
2. **Read the [Configuration Guide](CONFIGURATION_GUIDE.md)** for advanced setup
3. **Check the [Troubleshooting Guide](TROUBLESHOOTING.md)** if you encounter issues
4. **Explore the [Core Framework Documentation](../core/README.md)** for API details

### Learning Resources
- **[AI Task Orchestrator Guide](../docs/user_guide.md)** - Learn systematic AI-assisted development
- **[Memory Management Tutorial](../docs/memory_tutorial.md)** - Understand the multi-tier memory system
- **[Code Analysis Deep Dive](../docs/analysis_guide.md)** - Master code quality assessment

### Community & Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Complete guides and API reference
- **Examples**: Real-world integration patterns
- **Community Forum**: Get help from other users

---

**Installation Guide Version**: 1.0.0  
**Framework Version**: 1.0.0  
**Last Updated**: January 18, 2025  
**Status**: Production Ready ✅ 