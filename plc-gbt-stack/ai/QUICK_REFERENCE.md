# AI Task Orchestrator - Quick Reference

## 🚀 Quick Start

```bash
# Setup environment
cd plc-gbt-stack/ai
./setup_environment.sh

# Run a workflow
python workflows/simple_task_workflow.py
```

## 📦 Core Components

### Python Orchestrator
```python
from plc_orchestrator.config import OrchestratorConfig
from ai_task_orchestrator import AITaskOrchestrator

# Initialize
config = OrchestratorConfig(environment="production")
orchestrator = AITaskOrchestrator(config=config)

# Analyze task
result = orchestrator.analyze_task("Build a PLC control system")
```

### TypeScript Orchestrator
```typescript
import { createConfig, AITaskOrchestratorTS } from './ai_task_orchestrator_ts';

// Initialize
const config = createConfig({ environment: 'production' });
const orchestrator = new AITaskOrchestratorTS(config);

// Analyze task
const result = await orchestrator.analyzeTask("Build a React component");
```

## 🔄 Workflows

### 1. Simple Task
```python
python workflows/simple_task_workflow.py
# Creates: output/generated_parser.py
```

### 2. Complex Control System
```python
python workflows/complex_control_workflow.py
# Creates: tank_control_system/
#   ├── TankControl_Logic.st
#   ├── SafetyInterlock_FB.st
#   ├── HMI_Config.json
#   ├── TankControl.L5X
#   └── TankControl_Documentation.md
```

### 3. Production Deployment
```python
python workflows/production_deployment_workflow.py
# Creates: deployments/{timestamp}/
#   ├── Dockerfile
#   ├── docker-compose.yml
#   ├── kubernetes.yaml
#   ├── rollback.sh
#   └── deployment_report.json
```

## 💾 Memory Adapters

### Redis (Caching)
```python
from plc_orchestrator.memory.adapters import RedisMemoryAdapter

adapter = RedisMemoryAdapter({
    'url': 'redis://localhost:6379',
    'ttl': 3600
})
```

### Neo4j (Relationships)
```python
from plc_orchestrator.memory.adapters import Neo4jMemoryAdapter

adapter = Neo4jMemoryAdapter({
    'uri': 'bolt://localhost:7687',
    'username': 'neo4j',
    'password': 'your-password'
})
```

### PostgreSQL (Structured)
```python
from plc_orchestrator.memory.adapters import PostgresMemoryAdapter

adapter = PostgresMemoryAdapter({
    'dsn': 'postgresql://user:pass@localhost/db'
})
```

### Qdrant (Vectors)
```python
from plc_orchestrator.memory.adapters import QdrantMemoryAdapter

adapter = QdrantMemoryAdapter({
    'url': 'http://localhost:6333',
    'vector_size': 1536
})
```

## 🛠️ Configuration

### Environment Variables
```bash
# Core
export ORCHESTRATOR_ENV=production
export ORCHESTRATOR_DEBUG=false

# Memory Systems
export REDIS_URL=redis://localhost:6379
export NEO4J_URI=bolt://localhost:7687
export POSTGRES_DSN=postgresql://user:pass@localhost/db
export QDRANT_URL=http://localhost:6333

# Features
export ENABLE_ALL_FEATURES=true
export ENABLE_PRODUCTION_CHECKS=true
export MIN_VALIDATION_SCORE=95.0
```

### Python Config
```python
config = OrchestratorConfig(
    environment="production",
    enable_production_checks=True,
    min_validation_score=95.0,
    max_retries=3,
    timeout_seconds=300
)
```

### TypeScript Config
```typescript
const config = createConfig({
    environment: 'production',
    enableProductionChecks: true,
    minValidationScore: 95,
    maxRetries: 3,
    timeoutSeconds: 300
});
```

## 🎯 Common Patterns

### Retry with Backoff
```python
@retry_with_backoff(max_attempts=3)
async def fetch_data():
    # Automatically retries on failure
    pass
```

### Circuit Breaker
```python
@CircuitBreaker(failure_threshold=5, recovery_timeout=60)
async def external_api_call():
    # Prevents cascading failures
    pass
```

### TTL Cache
```python
@TTLCache(ttl_seconds=3600, max_size=1000)
async def expensive_computation(param):
    # Results cached for 1 hour
    pass
```

## 📝 Task Types

- `SMALL_SCRIPT`: Utility scripts, helpers
- `API_ENDPOINT`: REST/GraphQL endpoints
- `DATA_PIPELINE`: ETL, data processing
- `UI_COMPONENT`: React/Vue components
- `CONTROL_SYSTEM`: PLC logic, automation
- `FULL_APPLICATION`: Complete systems

## 🔍 Validation Tiers

- `BASIC`: Syntax and structure
- `STANDARD`: + Logic and requirements
- `COMPREHENSIVE`: + Edge cases and errors
- `PRODUCTION`: + Performance and security

## 📊 Memory Entry Types

- `TASK`: Task descriptions
- `CODE`: Code snippets
- `ERROR`: Error records
- `SOLUTION`: Problem solutions
- `PATTERN`: Design patterns
- `CONTEXT`: Domain knowledge
- `RELATIONSHIP`: Entity connections

## 🚨 Error Handling

```python
from plc_orchestrator.validation import ValidationError

try:
    result = orchestrator.analyze_task(task)
except ValidationError as e:
    print(f"Validation failed: {e.details}")
```

## 📈 Performance Tips

1. **Use appropriate memory adapter**:
   - Redis: Session data, cache
   - Neo4j: Complex relationships
   - PostgreSQL: Structured queries
   - Qdrant: Semantic search

2. **Enable caching**:
   ```python
   config.cache_ttl = 3600  # 1 hour
   ```

3. **Batch operations**:
   ```python
   await adapter.batch_store(entries)
   ```

4. **Use connection pooling**:
   - Built-in for PostgreSQL
   - Redis connection pool
   - Neo4j driver pooling

## 🔗 Useful Links

- [Python Guide](../../docs/AI_TASK_ORCHESTRATOR_GUIDE.md)
- [TypeScript Guide](../../docs/AI_TASK_ORCHESTRATOR_TS_GUIDE.md)
- [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md)
- [Memory Adapters Demo](examples/memory_adapters_demo.py)

## 💡 Pro Tips

1. **Start simple**: Use `simple_task_workflow.py` as template
2. **Test locally**: All workflows work offline first
3. **Check logs**: Structured logging shows details
4. **Use right adapter**: Each has strengths
5. **Monitor performance**: Built-in metrics available

---
*Last updated: 2025-01-18*
