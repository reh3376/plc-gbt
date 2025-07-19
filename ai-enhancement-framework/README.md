# 🤖 AI Enhancement Framework

**Universal AI-powered development tools extracted from plc-gbt project**

The AI Enhancement Framework is a generalized, production-ready toolkit that transforms specialized PLC-GPT capabilities into universal tools for any Python project. It provides systematic AI task orchestration, multi-database memory management, comprehensive code analysis, and modular provider abstraction.

## 🚀 Features

### Core Components

- **🧠 Universal Task Orchestrator** - Systematic AI task analysis and execution
- **💾 Memory Management System** - Multi-tier memory architecture with intelligent routing
- **🔍 Code Analysis Framework** - AI hallucination detection and quality assessment  
- **🔌 Provider Framework** - Universal service integration with health monitoring

### Key Capabilities

- **Domain-Agnostic Design** - Works with any Python project
- **Extensible Architecture** - Easy to add custom analyzers and providers
- **Production-Ready** - Comprehensive error handling and monitoring
- **AI-First Approach** - Built specifically for AI-assisted development
- **Methodical Processing** - Follows AI Task Orchestrator Guide methodology

## 📁 Project Structure

```
ai-enhancement-framework/
├── core/
│   ├── task_orchestrator.py    # Universal AI task orchestration
│   ├── memory_manager.py       # Multi-database memory management
│   └── code_analyzer.py        # Universal code analysis
├── providers/
│   └── provider_framework.py   # Modular provider abstraction
├── cursor/                     # Cursor IDE extensions (future)
├── cli/                        # Command-line interfaces (future)
├── docker/                     # Docker configurations (future)
├── docs/                       # Documentation (future)
├── tests/                      # Test suites (future)
└── README.md                   # This file
```

## 🏗️ Architecture

### Memory Tier Strategy
- **Short-term** - Fast access cache (Redis, in-memory)
- **Medium-term** - Structured knowledge (Neo4j, graph databases)  
- **Long-term** - Persistent storage (PostgreSQL, file systems)
- **Pattern Matching** - Vector/similarity search (Qdrant, Pinecone)

### Provider Architecture
- **Universal Interface** - Consistent API across all provider types
- **Health Monitoring** - Automatic health checks and circuit breakers
- **Intelligent Routing** - Performance-based provider selection
- **Extensible Design** - Easy integration of new services

## 🚀 Quick Start

### 1. AI Task Orchestrator

```python
from ai_enhancement_framework.core.task_orchestrator import create_task_orchestrator

# Create orchestrator
orchestrator = create_task_orchestrator()

# Analyze a task
task = "Create a Python utility to parse JSON files with error handling"
result = orchestrator.analyze_task(task)

print(f"Complexity: {result.complexity.value}")
print(f"Estimated effort: {result.estimated_effort}")
print(f"Execution plan: {len(result.execution_plan)} steps")

# Cleanup
orchestrator.cleanup()
```

### 2. Memory Management

```python
import asyncio
from ai_enhancement_framework.core.memory_manager import create_default_memory_manager, MemoryRequest, OperationType

async def memory_example():
    # Create memory manager
    manager = await create_default_memory_manager()
    
    # Store data
    set_request = MemoryRequest(
        operation="set",
        data_type="string", 
        context={"key": "example", "value": "Hello World"}
    )
    
    # Retrieve data
    get_request = MemoryRequest(
        operation="get",
        data_type="string",
        context={"key": "example"}
    )
    
    # Execute operations
    await manager.execute_request(set_request)
    result = await manager.execute_request(get_request)
    
    print(f"Retrieved: {result.data}")
    
    # Cleanup
    await manager.cleanup()

asyncio.run(memory_example())
```

### 3. Code Analysis

```python
from ai_enhancement_framework.core.code_analyzer import analyze_file, AnalysisLevel

# Analyze a Python file
result = analyze_file("example.py", AnalysisLevel.COMPREHENSIVE)

print(f"Quality Score: {result.quality_score}")
print(f"Issues Found: {len(result.issues)}")

# Show critical issues
for issue in result.issues:
    if issue.severity.value == "critical":
        print(f"CRITICAL: {issue.description} (Line {issue.line_number})")

# Show recommendations
for rec in result.recommendations:
    print(f"💡 {rec}")
```

### 4. Provider Framework

```python
import asyncio
from ai_enhancement_framework.providers.provider_framework import (
    create_provider_manager, ProviderConfig, ProviderType, OperationRequest, OperationType
)

async def provider_example():
    # Create provider manager
    manager = create_provider_manager()
    
    # Add file system provider
    config = ProviderConfig(
        provider_type=ProviderType.FILE_SYSTEM,
        provider_name="local_files",
        endpoint="./data",
        metadata={"factory_type": "file_system"}
    )
    
    await manager.add_provider(config)
    
    # Write file
    write_request = OperationRequest(
        operation_type=OperationType.WRITE,
        parameters={"path": "test.txt", "content": "Hello Framework!"}
    )
    
    result = await manager.execute_operation("local_files", write_request)
    print(f"Write success: {result.success}")
    
    # Cleanup
    await manager.cleanup_all()

asyncio.run(provider_example())
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Optional dependencies based on providers used:
  - `redis` for Redis memory provider
  - `aiohttp` for HTTP API providers  
  - `psycopg2` for PostgreSQL providers
  - `neo4j` for Neo4j providers
  - `qdrant-client` for Qdrant providers

### Basic Installation
```bash
# Clone the framework
git clone <repository-url>
cd ai-enhancement-framework

# Install core dependencies
pip install -r requirements.txt  # (when available)

# For development
pip install -e .
```

## 📚 Detailed Usage

### Task Orchestrator Customization

```python
from ai_enhancement_framework.core.task_orchestrator import AITaskOrchestrator

# Custom project markers
custom_markers = ['.git', 'pyproject.toml', 'custom_marker.txt']

# Domain-specific configuration  
domain_config = {
    "domain": "web_development",
    "complexity_adjustments": {
        "database": 1.2,  # Increase complexity for DB tasks
        "frontend": 0.8   # Decrease for frontend tasks
    }
}

orchestrator = AITaskOrchestrator(
    project_markers=custom_markers,
    domain_config=domain_config
)
```

### Memory Manager Configuration

```python
# Create memory manager with configuration file
manager = UniversalMemoryManager("memory_config.json")

# Example config file format:
config = {
    "providers": {
        "redis_cache": {
            "type": "redis",
            "tier": "short_term", 
            "connection": {"host": "localhost", "port": 6379},
            "enabled": True
        }
    }
}
```

### Custom Code Analyzers

```python
from ai_enhancement_framework.core.code_analyzer import UniversalCodeAnalyzer, CodeAnalyzer

class CustomAnalyzer(CodeAnalyzer):
    def analyze(self, content: str, file_path: Path) -> AnalysisResult:
        # Custom analysis logic
        pass
    
    def get_supported_languages(self) -> List[str]:
        return ["python", "custom_lang"]
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {"custom_feature": True}

# Add to analyzer
analyzer = UniversalCodeAnalyzer()
analyzer.add_custom_analyzer("custom", CustomAnalyzer())
```

### Custom Providers

```python
from ai_enhancement_framework.providers.provider_framework import BaseProvider

class CustomProvider(BaseProvider):
    async def _connect(self) -> bool:
        # Initialize custom service connection
        return True
    
    async def _disconnect(self):
        # Cleanup custom service connection
        pass
    
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        # Execute custom operations
        return OperationResult(success=True, data="custom_result")
    
    async def _health_check_impl(self) -> HealthStatus:
        # Check custom service health
        return HealthStatus.HEALTHY

# Register with manager
manager.register_provider_factory("custom_service", CustomProvider)
```

## 🎯 Use Cases

### 1. AI-Assisted Development
- Systematic task breakdown and analysis
- Intelligent code quality assessment  
- AI hallucination detection in generated code
- Memory-efficient context management

### 2. Large Codebase Management
- Multi-database knowledge storage
- Intelligent query routing
- Performance monitoring and optimization
- Automated code analysis at scale

### 3. Service Integration
- Universal provider interface
- Health monitoring and failover
- Performance metrics and monitoring
- Circuit breaker patterns for resilience

### 4. Development Workflow Enhancement
- Cursor IDE integration (planned)
- CLI tools for automation (planned)
- Docker containerization (planned)
- CI/CD pipeline integration (planned)

## 🔧 Configuration

### Environment Variables
```bash
# Memory providers
REDIS_HOST=localhost
REDIS_PORT=6379
NEO4J_URI=bolt://localhost:7687
POSTGRES_HOST=localhost

# Framework settings
AI_FRAMEWORK_LOG_LEVEL=INFO
AI_FRAMEWORK_TIMEOUT=30
```

### Configuration Files
The framework supports JSON configuration files for all components:

```json
{
  "memory": {
    "providers": {
      "redis_cache": {
        "type": "redis",
        "tier": "short_term",
        "connection": {"host": "localhost", "port": 6379}
      }
    }
  },
  "providers": {
    "web_api": {
      "type": "api", 
      "endpoint": "https://api.example.com",
      "timeout_seconds": 30
    }
  }
}
```

## 🧪 Testing

```bash
# Run core tests
python -m pytest tests/core/

# Run provider tests  
python -m pytest tests/providers/

# Run integration tests
python -m pytest tests/integration/

# Run example scripts
python ai-enhancement-framework/core/task_orchestrator.py
python ai-enhancement-framework/core/memory_manager.py
python ai-enhancement-framework/core/code_analyzer.py
python ai-enhancement-framework/providers/provider_framework.py
```

## 📈 Performance

### Memory Management
- **Sub-millisecond** short-term memory access
- **Multi-tier** routing optimization
- **Intelligent caching** with automatic warming
- **Connection pooling** for all providers

### Code Analysis
- **Multi-language** support with extensible architecture
- **Parallel processing** for large codebases
- **Incremental analysis** for performance
- **AI hallucination detection** with high accuracy

### Provider Framework
- **Circuit breaker** patterns for resilience
- **Health monitoring** with automatic failover
- **Performance metrics** collection
- **Retry logic** with exponential backoff

## 🛣️ Roadmap

### Phase 25.2: CLI & Automation Tools
- Command-line interfaces for all components
- Automation scripts and workflows
- Integration with popular development tools

### Phase 25.3: Cursor IDE Integration  
- VSCode/Cursor extension development
- Real-time code analysis and suggestions
- AI task orchestration within the IDE

### Phase 25.4: Docker & Deployment
- Docker containers for all services
- Kubernetes deployment configurations
- Cloud provider integrations

### Phase 25.5: Advanced Features
- Machine learning model integrations
- Advanced analytics and reporting
- Performance optimization tools

## 🤝 Contributing

The AI Enhancement Framework is extracted from the plc-gbt project and is designed to be universally applicable. Contributions are welcome for:

- Additional provider implementations
- Custom analyzer modules
- Performance optimizations
- Documentation improvements
- Test coverage expansion

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

This framework is extracted and generalized from the plc-gbt project, which pioneered many of the AI task orchestration and memory management patterns implemented here. Special thanks to the AI Task Orchestrator methodology that guides the systematic approach to complex task execution.

---

**Built with ❤️ for the AI development community** 