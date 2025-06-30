# Coding Standards

This document establishes coding standards and best practices for the PLC-Savvy GPT project to ensure maintainable, readable, and reliable code.

## General Principles

1. **Readability First**: Code should be self-documenting and easy to understand
2. **Consistency**: Follow established patterns throughout the codebase
3. **Reliability**: Write defensive code with proper error handling
4. **Performance**: Consider performance implications but prioritize clarity
5. **Security**: Follow security best practices for data handling and API access

## Python Standards

### Code Style

Follow [PEP 8](https://pep8.org/) with specific project adaptations:

#### Line Length
- Maximum 88 characters per line (Black formatter default)
- Break long lines logically at natural breakpoints

```python
# Good
result = some_function_with_long_name(
    parameter_one="value",
    parameter_two="another_value",
    parameter_three="third_value"
)

# Avoid
result = some_function_with_long_name(parameter_one="value", parameter_two="another_value", parameter_three="third_value")
```

#### Imports
- Use absolute imports
- Group imports in this order: standard library, third-party, local
- Sort imports alphabetically within each group

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import neo4j
import structlog
from fastapi import FastAPI
from pydantic import BaseModel

# Local
from .models import PLCProgram
from .utils import load_config
```

#### Formatting Tools
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [ruff](https://docs.astral.sh/ruff/) for linting

### Type Hints

Use type hints for all function signatures and class attributes:

```python
from typing import Dict, List, Optional, Union
from pathlib import Path

def process_l5x_file(
    file_path: Path,
    batch_size: int = 100
) -> Dict[str, Union[str, int]]:
    """Process an L5X file and return metadata."""
    return {"status": "processed", "items_count": 42}

class PLCProgram:
    def __init__(self, name: str, firmware_version: str) -> None:
        self.name: str = name
        self.firmware_version: str = firmware_version
        self.routines: List[str] = []
```

### Documentation

#### Docstrings
Use Google-style docstrings for all public functions and classes:

```python
def extract_aoi_dependencies(l5x_content: str) -> List[Dict[str, str]]:
    """Extract AOI dependencies from L5X content.
    
    Args:
        l5x_content: Raw XML content from L5X file
        
    Returns:
        List of dictionaries containing AOI dependency information
        
    Raises:
        ValueError: If L5X content is invalid
        XMLParseError: If XML parsing fails
        
    Example:
        >>> content = load_l5x_file("program.l5x")
        >>> deps = extract_aoi_dependencies(content)
        >>> print(deps[0]["name"])
        "MotorControl"
    """
```

#### Comments
- Use comments to explain "why", not "what"
- Keep comments concise and up-to-date
- Use TODO comments for known improvements

```python
# TODO: Implement caching for frequently accessed AOIs
def get_aoi_definition(aoi_name: str) -> Optional[Dict]:
    # Use case-insensitive lookup because AOI names in L5X 
    # may not match the case used in documentation
    normalized_name = aoi_name.lower()
    return self.aoi_cache.get(normalized_name)
```

### Error Handling

#### Exception Handling
- Use specific exception types
- Log errors with context
- Handle exceptions at appropriate levels

```python
import structlog
from neo4j.exceptions import ServiceUnavailable

logger = structlog.get_logger()

def create_plc_program_node(program_data: Dict[str, str]) -> str:
    """Create a PLC program node in Neo4j."""
    try:
        with self.driver.session() as session:
            result = session.run(
                "CREATE (p:PLCProgram {name: $name, firmware: $firmware}) "
                "RETURN p.id",
                name=program_data["name"],
                firmware=program_data["firmware"]
            )
            return result.single()["p.id"]
            
    except ServiceUnavailable as e:
        logger.error(
            "neo4j_connection_failed",
            error=str(e),
            program_name=program_data.get("name")
        )
        raise
    except Exception as e:
        logger.error(
            "program_creation_failed",
            error=str(e),
            program_data=program_data
        )
        raise
```

#### Validation
- Validate inputs early
- Use Pydantic models for data validation
- Provide clear error messages

```python
from pydantic import BaseModel, validator

class PLCProgramModel(BaseModel):
    name: str
    firmware_version: str
    created_at: Optional[datetime] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Program name cannot be empty')
        return v.strip()
    
    @validator('firmware_version')
    def firmware_version_format(cls, v):
        if not re.match(r'^\d+\.\d+$', v):
            raise ValueError('Firmware version must be in format X.Y')
        return v
```

### Async Programming

When using async/await:
- Use proper async context managers
- Handle asyncio exceptions appropriately
- Use async libraries consistently

```python
import asyncio
import aiohttp
from typing import List

async def fetch_embeddings(texts: List[str]) -> List[List[float]]:
    """Fetch embeddings from OpenAI API."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_single_embedding(session, text) 
            for text in texts
        ]
        try:
            embeddings = await asyncio.gather(*tasks)
            return embeddings
        except asyncio.TimeoutError:
            logger.error("embedding_request_timeout")
            raise
```

## Database Standards

### Neo4j Cypher Queries

#### Query Structure
- Use proper indentation for readability
- Use parameter binding for security
- Include query comments for complex logic

```cypher
// Find all routines that use a specific AOI
MATCH (p:PLCProgram)-[:CONTAINS]->(r:Routine)
WHERE p.name = $program_name
  AND exists((r)-[:USES]->(:AOI {name: $aoi_name}))
RETURN r.name as routine_name,
       r.language as language,
       r.lastModified as last_modified
ORDER BY r.name
```

#### Performance Guidelines
- Use EXPLAIN and PROFILE for query optimization
- Create appropriate indexes
- Limit result sets when possible

```python
def get_related_routines(self, aoi_name: str, limit: int = 50) -> List[Dict]:
    """Get routines that use the specified AOI."""
    query = """
    MATCH (r:Routine)-[:USES]->(a:AOI {name: $aoi_name})
    RETURN r.name, r.language, r.lastModified
    ORDER BY r.lastModified DESC
    LIMIT $limit
    """
    
    with self.driver.session() as session:
        result = session.run(query, aoi_name=aoi_name, limit=limit)
        return [record.data() for record in result]
```

### Vector Database (Qdrant)

#### Collection Setup
- Use descriptive collection names
- Set appropriate vector dimensions
- Configure distance metrics correctly

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

def create_embedding_collection(self, collection_name: str) -> None:
    """Create a new collection for document embeddings."""
    self.client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=3072,  # text-embedding-3-large dimensions
            distance=Distance.COSINE
        )
    )
```

## API Standards

### FastAPI Best Practices

#### Request/Response Models
- Use Pydantic models for all API inputs/outputs
- Include proper validation and documentation

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=6, ge=1, le=20)
    include_context: bool = Field(default=True)
    
    class Config:
        schema_extra = {
            "example": {
                "question": "How do I configure a motor AOI?",
                "max_results": 6,
                "include_context": True
            }
        }

class QueryResponse(BaseModel):
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: List[str]
    processing_time_ms: int
```

#### Error Handling
- Use appropriate HTTP status codes
- Provide consistent error response format
- Log errors with request context

```python
from fastapi import HTTPException, Request
import structlog

logger = structlog.get_logger()

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(
        "validation_error",
        path=request.url.path,
        error=str(exc)
    )
    raise HTTPException(
        status_code=400,
        detail={"error": "Invalid input", "message": str(exc)}
    )
```

### Security

#### Authentication
- Use environment variables for secrets
- Implement proper token validation
- Log security events

```python
import os
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

def verify_token(token: str = Security(security)) -> str:
    """Verify API bearer token."""
    expected_token = os.getenv("GATEWAY_BEARER_TOKEN")
    
    if not expected_token:
        logger.error("missing_bearer_token_config")
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    if token.credentials != expected_token:
        logger.warning("invalid_token_attempt", token_prefix=token.credentials[:8])
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    
    return token.credentials
```

## Testing Standards

### Unit Tests
- Use pytest for testing framework
- Aim for 80%+ code coverage
- Follow AAA pattern (Arrange, Act, Assert)

```python
import pytest
from unittest.mock import Mock, patch
from myapp.etl_worker import DocumentProcessor

class TestDocumentProcessor:
    @pytest.fixture
    def processor(self):
        return DocumentProcessor(batch_size=10)
    
    def test_process_pdf_success(self, processor):
        # Arrange
        mock_pdf_path = "/path/to/test.pdf"
        expected_result = {"pages": 5, "text_length": 1000}
        
        # Act
        with patch('myapp.etl_worker.extract_pdf_content') as mock_extract:
            mock_extract.return_value = "Sample content"
            result = processor.process_pdf(mock_pdf_path)
        
        # Assert
        assert result["status"] == "success"
        assert "content" in result
        mock_extract.assert_called_once_with(mock_pdf_path)
```

### Integration Tests
- Test API endpoints end-to-end
- Use test databases (not production)
- Clean up test data after each test

```python
import pytest
from fastapi.testclient import TestClient
from myapp.main import app

client = TestClient(app)

def test_query_endpoint():
    """Test the main query endpoint."""
    response = client.post(
        "/api/v1/query",
        json={"question": "What is a PLC?", "max_results": 3},
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) <= 3
```

## Docker Standards

### Dockerfile Best Practices
- Use multi-stage builds when appropriate
- Run as non-root user
- Use specific base image versions
- Minimize layer count

```dockerfile
FROM python:3.12-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "-m", "myapp"]
```

## Configuration Management

### Environment Variables
- Use environment variables for configuration
- Provide sensible defaults
- Document all configuration options

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str
    
    # OpenAI configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo"
    
    # Application configuration
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Logging Standards

### Structured Logging
- Use structured logging with consistent fields
- Include correlation IDs for request tracking
- Log at appropriate levels

```python
import structlog
import uuid

logger = structlog.get_logger()

def process_document(file_path: str) -> None:
    """Process a document with proper logging."""
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "document_processing_started",
        correlation_id=correlation_id,
        file_path=file_path,
        file_size=os.path.getsize(file_path)
    )
    
    try:
        # Process document
        result = extract_content(file_path)
        
        logger.info(
            "document_processing_completed",
            correlation_id=correlation_id,
            file_path=file_path,
            pages_extracted=result.get("page_count", 0)
        )
        
    except Exception as e:
        logger.error(
            "document_processing_failed",
            correlation_id=correlation_id,
            file_path=file_path,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

## Code Review Guidelines

### Before Submitting
- [ ] Code follows established conventions
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No sensitive data in code
- [ ] Error handling is appropriate

### Review Checklist
- [ ] Code is readable and well-documented
- [ ] Business logic is correct
- [ ] Security considerations addressed
- [ ] Performance implications considered
- [ ] Test coverage is adequate

## Tools and Automation

### Pre-commit Hooks
Configure pre-commit hooks to enforce standards:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
```

### CI/CD Pipeline
- Run linting and formatting checks
- Execute all tests
- Check code coverage
- Build and test Docker images

---

*These standards should be followed by all contributors and regularly reviewed for updates.* 