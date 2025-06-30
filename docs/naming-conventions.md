# Naming Conventions

This document establishes naming conventions for the PLC-Savvy GPT project to ensure consistency across all components.

## General Principles

1. **Clarity**: Names should clearly indicate purpose and scope
2. **Consistency**: Follow established patterns throughout the project
3. **Brevity**: Use concise names while maintaining clarity
4. **Domain Alignment**: Use terminology familiar to PLC/automation professionals

## File and Directory Naming

### Directories
- Use `kebab-case` for directory names
- Keep names descriptive but concise
- Examples: `plc-gpt-stack`, `docs`, `summaries`

### Files
- **Python files**: Use `snake_case` (e.g., `etl_worker.py`)
- **Docker files**: Use `Dockerfile` or `servicename.Dockerfile`
- **Documentation**: Use `kebab-case` (e.g., `naming-conventions.md`)
- **Configuration**: Use `kebab-case` (e.g., `docker-compose.yml`)

## Code Naming Conventions

### Python

#### Variables and Functions
- Use `snake_case` for variables and functions
- Use descriptive names that indicate purpose
```python
# Good
plc_program_name = "Main_Program"
def extract_aoi_dependencies(l5x_content):
    pass

# Avoid
pn = "Main_Program"
def process(data):
    pass
```

#### Classes
- Use `PascalCase` for class names
- Prefix with domain context when appropriate
```python
class PLCProgram:
    pass

class EmbeddingGenerator:
    pass

class QdrantVectorStore:
    pass
```

#### Constants
- Use `UPPER_SNAKE_CASE` for constants
```python
DEFAULT_BATCH_SIZE = 100
MAX_RETRY_ATTEMPTS = 3
OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
```

#### Modules and Packages
- Use `snake_case` for module names
- Keep package names short and meaningful
```python
# Modules
etl_worker.py
vector_store.py
neo4j_client.py

# Packages
plc_parser/
knowledge_graph/
```

### Neo4j Graph Elements

#### Node Labels
- Use `PascalCase` for node labels
- Use singular nouns
- Examples: `PLCProgram`, `Routine`, `AOI`, `UDT`, `SpecDoc`

#### Relationship Types
- Use `UPPER_SNAKE_CASE` for relationship types
- Use descriptive verbs or prepositions
- Examples: `CONTAINS`, `USES`, `DERIVED_FROM`, `IN_PROGRAM`

#### Properties
- Use `camelCase` for property names
- Be consistent with property naming across similar nodes
```cypher
// Node properties
(:PLCProgram {
    name: "Main_Program",
    firmwareVersion: "35.011",
    createdAt: datetime(),
    projectPath: "/path/to/project"
})

// Relationship properties
(:Routine)-[:USES {frequency: 10, lastUsed: datetime()}]->(:AOI)
```

## Database and Service Naming

### Docker Services
- Use `kebab-case` for service names in docker-compose.yml
- Prefix with project identifier when needed
```yaml
services:
  neo4j:           # Core service
  plc-qdrant:      # Project-specific
  plc-gateway:     # Project-specific
  plc-etl-worker:  # Project-specific
```

### Database Names
- Use `snake_case` for database names
- Include purpose in the name
```
plc_knowledge_graph  # Neo4j database
plc_embeddings      # Qdrant collection
plc_metadata        # PostgreSQL database
```

### API Endpoints
- Use `kebab-case` for URL paths
- Use RESTful conventions
- Version APIs appropriately
```
GET  /api/v1/health
POST /api/v1/query
GET  /api/v1/plc-programs
POST /api/v1/documents/upload
```

## Environment Variables

- Use `UPPER_SNAKE_CASE` for environment variables
- Group related variables with prefixes
- Include service/component context

```bash
# OpenAI configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Neo4j configuration
NEO4J_PASSWORD=secure_password
NEO4J_BOLT_URL=bolt://neo4j:7687
NEO4J_USER=neo4j

# Gateway configuration
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
GATEWAY_BEARER_TOKEN=secure_token

# ETL configuration
ETL_BATCH_SIZE=100
ETL_WORKER_THREADS=4
ETL_LOG_LEVEL=INFO
```

## PLC-Specific Naming

### PLC Component Naming
Follow Allen-Bradley/Rockwell conventions when applicable:

- **Programs**: Use original PLC program names (e.g., `Main_Program`, `Safety_Program`)
- **Routines**: Preserve original routine names (e.g., `MainRoutine`, `FaultHandler`)
- **AOIs**: Use descriptive names reflecting functionality (e.g., `MotorControl`, `PIDController`)
- **UDTs**: Use meaningful type names (e.g., `Motor_Type`, `Valve_Status`)

### Document Types
```python
# Document classification
DOC_TYPE_MANUAL = "manual"
DOC_TYPE_SPECIFICATION = "specification"
DOC_TYPE_TROUBLESHOOTING = "troubleshooting"
DOC_TYPE_INSTALLATION = "installation"
DOC_TYPE_L5X = "l5x_export"
```

## Git and Version Control

### Branch Names
- Use `kebab-case` for branch names
- Include type prefix
```
feature/neo4j-schema
bugfix/health-check-fix
docs/naming-conventions
hotfix/security-patch
```

### Commit Messages
Follow Conventional Commits specification:
```
feat: add Neo4j schema implementation
fix: resolve Qdrant health check issue
docs: update naming conventions
refactor: restructure ETL worker modules
```

### Tags
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Prefix with 'v' for releases
```
v0.1.0  # Initial setup
v0.2.0  # Docker stack operational
v1.0.0  # First production release
```

## Logging and Monitoring

### Log Messages
- Use `snake_case` for structured logging keys
- Be consistent with field naming
```python
logger.info("document_processed", 
           file_path=str(file_path),
           processing_time_ms=elapsed_ms,
           document_type=doc_type)
```

### Metrics Names
- Use dot notation for metric hierarchies
- Include service context
```
plc_gpt.etl.documents_processed_total
plc_gpt.gateway.query_duration_seconds
plc_gpt.neo4j.nodes_created_total
```

## Examples Summary

| Component | Convention | Example |
|-----------|------------|---------|
| Python files | snake_case | `etl_worker.py` |
| Python classes | PascalCase | `PLCProgram` |
| Python variables | snake_case | `document_count` |
| Python constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Directories | kebab-case | `plc-gpt-stack` |
| Neo4j nodes | PascalCase | `PLCProgram` |
| Neo4j relationships | UPPER_SNAKE_CASE | `CONTAINS` |
| Neo4j properties | camelCase | `firmwareVersion` |
| Environment vars | UPPER_SNAKE_CASE | `OPENAI_API_KEY` |
| API endpoints | kebab-case | `/api/v1/plc-programs` |
| Docker services | kebab-case | `plc-gateway` |

---

*This document should be referenced when creating new components to ensure consistency across the project.* 