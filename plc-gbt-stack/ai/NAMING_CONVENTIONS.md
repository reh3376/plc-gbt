# 📏 AI Task Orchestrator - Naming Conventions Guide

## Overview

This guide establishes naming conventions for the AI Task Orchestrator across Python and TypeScript implementations. While maintaining consistency where possible, we respect each language's idioms and conventions.

## Core Principles

1. **Language Idioms First**: Follow PEP 8 for Python and TypeScript/JavaScript conventions
2. **Consistent Concepts**: Same concepts use equivalent names across languages
3. **Clear Mapping**: Document the naming transformation between languages
4. **No Confusion**: Avoid names that could be ambiguous across stacks

## Naming Standards

### Classes (✅ Already Aligned)
- **Both Languages**: PascalCase
- **No Suffixes**: Don't add `TS` or `Py` suffixes

```python
# Python
class AITaskOrchestrator:
class TaskAnalyzer:
class TaskValidator:
class MemoryCoordinator:
```

```typescript
// TypeScript
class AITaskOrchestrator {}
class TaskAnalyzer {}
class TaskValidator {}
class MemoryCoordinator {}
```

### Enums (✅ Already Aligned)
- **Both Languages**: PascalCase for enum names
- **Values**: Same string values across both

```python
# Python
class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXTENSIVE = "extensive"

class ValidationTier(Enum):
    SYNTAX = "syntax"
    REQUIREMENTS = "requirements"
    PRODUCTION = "production"
```

```typescript
// TypeScript
enum TaskComplexity {
  SIMPLE = 'simple',
  MODERATE = 'moderate',
  COMPLEX = 'complex',
  EXTENSIVE = 'extensive'
}

enum ValidationTier {
  SYNTAX = 'syntax',
  REQUIREMENTS = 'requirements',
  PRODUCTION = 'production'
}
```

### Methods (🔄 Language-Specific)
- **Python**: snake_case (PEP 8)
- **TypeScript**: camelCase
- **Mapping**: Document the conversion

```python
# Python (snake_case)
def analyze_task(self, description: str) -> TaskAnalysis:
def validate_implementation(self, code: str) -> ValidationResult:
def create_implementation_guide(self, analysis: TaskAnalysis) -> Path:
def get_production_checklist(self, implementation: str) -> DeploymentChecklist:
```

```typescript
// TypeScript (camelCase)
analyzeTask(description: string): Promise<TaskAnalysis>
validateImplementation(code: string): Promise<ValidationResult>
createImplementationGuide(analysis: TaskAnalysis): Promise<string>
getProductionChecklist(implementation: string): Promise<DeploymentChecklist>
```

### Method Mapping Table

| Python (snake_case) | TypeScript (camelCase) | Description |
|---------------------|------------------------|-------------|
| `analyze_task` | `analyzeTask` | Analyzes task complexity and requirements |
| `validate_implementation` | `validateImplementation` | Validates code against requirements |
| `create_implementation_guide` | `createImplementationGuide` | Creates implementation guide document |
| `get_production_checklist` | `getProductionChecklist` | Gets production readiness checklist |
| `execute_task_step` | `executeTaskStep` | Executes a specific task step |
| `create_summary_document` | `createSummaryDocument` | Creates task summary document |
| `add_progress_callback` | `addProgressCallback` | Adds progress monitoring callback |

### Interfaces/Protocols (✅ Already Aligned)
- **Both Languages**: PascalCase
- **Python**: Use `Protocol` from `typing`
- **TypeScript**: Use `interface`

```python
# Python
from typing import Protocol

class MemoryAdapter(Protocol):
    async def query(self, request: MemoryRequest) -> MemoryResponse: ...
    async def store(self, data: Any) -> bool: ...
```

```typescript
// TypeScript
interface MemoryAdapter {
  query(request: MemoryRequest): Promise<MemoryResponse>;
  store(data: any): Promise<boolean>;
}
```

### Data Classes/Types (✅ Already Aligned)
- **Both Languages**: PascalCase
- **Python**: Use `@dataclass` or Pydantic models
- **TypeScript**: Use `interface` or `type`

```python
# Python
@dataclass
class TaskAnalysis:
    task_id: str
    complexity: str
    requirements: list[str]
    risks: list[str]
```

```typescript
// TypeScript
interface TaskAnalysis {
  taskId: string;
  complexity: string;
  requirements: string[];
  risks: string[];
}
```

### File Names (✅ Already Aligned)
- **Both Languages**: snake_case
- **Extensions**: `.py` for Python, `.ts`/`.tsx` for TypeScript

```
# Python
ai_task_orchestrator.py
task_analyzer.py
task_validator.py
memory_coordinator.py

# TypeScript
ai_task_orchestrator.ts
task_analyzer.ts
task_validator.ts
memory_coordinator.ts
```

### Constants (✅ Already Aligned)
- **Python**: UPPER_SNAKE_CASE
- **TypeScript**: UPPER_SNAKE_CASE or camelCase

```python
# Python
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300
CACHE_TTL = 3600
```

```typescript
// TypeScript
const MAX_RETRIES = 3;
const DEFAULT_TIMEOUT = 300;
const CACHE_TTL = 3600;
```

## Migration Guide

### For Existing Code

1. **Classes, Enums, Interfaces**: Already aligned ✅
2. **Methods**: Keep language-specific conventions
3. **Documentation**: Update to show method mappings

### For New Code

1. **Follow this guide** for all new implementations
2. **Use migration script** for automated checking
3. **Update mapping table** when adding new methods

## Quick Reference Card

```yaml
# Universal (Same in Both Languages)
Classes: PascalCase          # AITaskOrchestrator
Enums: PascalCase           # TaskComplexity
Enum Values: lowercase      # "simple", "moderate"
Files: snake_case           # task_analyzer.py/.ts
Constants: UPPER_SNAKE      # MAX_RETRIES

# Language-Specific
Python Methods: snake_case   # analyze_task()
TypeScript Methods: camelCase # analyzeTask()

Python Privates: _leading    # _internal_method()
TypeScript Privates: private # private internalMethod()
```

## Automated Checking

Use the provided linting script to check naming conventions:

```bash
# Python
python check_naming_conventions.py

# TypeScript
npm run lint:naming
```

## Common Pitfalls

1. **Don't mix conventions**: `analyzeTask()` in Python or `analyze_task()` in TypeScript
2. **Don't add type suffixes**: `AITaskOrchestratorPy` or `ITaskAnalysis`
3. **Keep enum values consistent**: Same string values in both languages
4. **Document method mappings**: Update the mapping table for new methods

## Benefits

1. **Language Idioms**: Code feels natural in each language
2. **Easy Translation**: Clear mapping between implementations
3. **Tool Support**: IDEs and linters work correctly
4. **Developer Experience**: Familiar patterns for each community

---

**Remember**: Consistency within each language is more important than forcing identical names across languages. When in doubt, follow the language's standard conventions.
