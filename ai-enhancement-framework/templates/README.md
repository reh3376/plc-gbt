# AI Enhancement Framework - Environment Templates

## 📋 Overview

The Environment Templates provide pre-configured project scaffolding, configuration templates, and development workflows for quickly bootstrapping AI Enhancement Framework projects. These templates ensure consistent project structure, optimal configuration, and best practices across all framework implementations.

## 🏗️ Template Architecture

### Template Categories

#### 1. Project Templates (`project/`)
- **Purpose**: Complete project scaffolding for new AI Enhancement Framework projects
- **Components**:
  - Project structure layout
  - Base configuration files
  - Documentation templates
  - Development workflows
  - Testing frameworks

#### 2. Configuration Templates (`config/`)
- **Purpose**: Customizable configuration files for different project types and environments
- **Components**:
  - `.cursorrules` templates
  - Environment-specific configs
  - Docker configurations
  - IDE settings

#### 3. Development Templates (`development/`)
- **Purpose**: Development environment setup and workflow templates
- **Components**:
  - Git workflows
  - CI/CD pipelines
  - Code quality configurations
  - Testing setups

## 🚀 Quick Start

### Creating a New Project
```bash
# Navigate to your projects directory
cd /path/to/your/projects

# Create new project from template
python -m ai_enhancement_framework create-project my-ai-project

# Or manually copy template
cp -r ai-enhancement-framework/templates/project/ my-ai-project/
cd my-ai-project/

# Customize project settings
python customize_project.py
```

### Using Configuration Templates
```bash
# Copy base configuration template
cp ai-enhancement-framework/templates/config/.cursorrules .

# Copy environment-specific configuration
cp ai-enhancement-framework/templates/config/.env.development .env

# Copy Docker configuration
cp ai-enhancement-framework/templates/docker/* docker/
```

### IDE Setup Templates
```bash
# Copy VSCode/Cursor workspace settings
cp -r ai-enhancement-framework/templates/ide/.vscode/ .

# Copy editor configurations
cp ai-enhancement-framework/templates/ide/.editorconfig .
```

## 📁 Template Structure

```
templates/
├── project/                    # Complete project templates
│   ├── README.md              # Project documentation template
│   ├── src/                   # Source code structure
│   ├── tests/                 # Testing framework setup
│   ├── docs/                  # Documentation structure
│   ├── docker/                # Container configuration
│   └── scripts/               # Utility scripts
├── config/                    # Configuration templates
│   ├── .cursorrules           # AI assistant configuration
│   ├── .env.development       # Development environment
│   ├── .env.production        # Production environment
│   ├── docker-compose.yml     # Service orchestration
│   └── pyproject.toml         # Python project configuration
├── development/               # Development workflows
│   ├── .github/               # GitHub Actions workflows
│   ├── .pre-commit-config.yaml # Git hooks
│   ├── Makefile               # Build automation
│   └── scripts/               # Development scripts
└── README.md                  # This documentation
```

## 🎯 Project Templates

### Basic Python Project Template
**Location**: `templates/project/basic_python/`

Features:
- Clean project structure
- AI Enhancement Framework integration
- Basic testing setup
- Documentation templates
- Docker configuration

```
basic_python/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── utils/
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── conftest.py
├── docs/
│   ├── api.md
│   └── getting_started.md
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
└── scripts/
    ├── setup.sh
    └── test.sh
```

### Web API Project Template
**Location**: `templates/project/web_api/`

Features:
- FastAPI/Flask integration
- API documentation
- Authentication setup
- Database integration
- Production deployment

```
web_api/
├── README.md
├── requirements.txt
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   └── middleware/
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
│   ├── integration/
│   ├── unit/
│   └── fixtures/
├── docs/
│   ├── api_reference.md
│   └── deployment.md
└── config/
    ├── settings.py
    └── database.py
```

### Data Science Project Template
**Location**: `templates/project/data_science/`

Features:
- Jupyter notebook integration
- Data pipeline setup
- ML model templates
- Experiment tracking
- Visualization tools

```
data_science/
├── README.md
├── requirements.txt
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_training.ipynb
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── visualization/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── models/
└── reports/
    ├── figures/
    └── analysis/
```

### Machine Learning Project Template
**Location**: `templates/project/machine_learning/`

Features:
- MLOps integration
- Model versioning
- Training pipelines
- Deployment automation
- Monitoring setup

```
machine_learning/
├── README.md
├── requirements.txt
├── src/
│   ├── training/
│   ├── inference/
│   ├── evaluation/
│   └── deployment/
├── models/
│   ├── experiments/
│   └── production/
├── data/
│   ├── training/
│   ├── validation/
│   └── test/
├── pipelines/
│   ├── training.yaml
│   └── deployment.yaml
└── monitoring/
    ├── metrics.py
    └── alerts.py
```

## ⚙️ Configuration Templates

### .cursorrules Template
Customizable AI assistant configuration:

```yaml
# AI Enhancement Framework Configuration Template
ai_framework:
  version: "1.0.0"
  enabled: true
  mode: "{{MODE}}"  # development, testing, production

project:
  name: "{{PROJECT_NAME}}"
  type: "{{PROJECT_TYPE}}"  # python, web_api, data_science, ml_project
  complexity: "{{COMPLEXITY}}"  # simple, moderate, complex, extensive

assistant:
  task_orchestrator:
    enabled: true
    analysis_depth: "{{ANALYSIS_DEPTH}}"
    methodical_approach: true
  
  memory:
    enabled: true
    project_scoped: true
    cross_session_persistence: true
  
  code_analysis:
    enabled: true
    real_time: true
    validation_on_save: true
    hallucination_detection: true

standards:
  code_quality:
    type_hints: "required"
    docstrings: "required"
    test_coverage: {{TEST_COVERAGE}}
  
  documentation:
    auto_generate: true
    mermaid_diagrams: true
    api_documentation: true
```

### Environment Configuration Templates

#### Development Environment (`.env.development`)
```bash
# AI Enhancement Framework - Development Configuration
AI_FRAMEWORK_ENV=development
AI_FRAMEWORK_LOG_LEVEL=DEBUG
AI_FRAMEWORK_DEBUG=true

# Database Connections
AI_FRAMEWORK_REDIS_URL=redis://localhost:6379
AI_FRAMEWORK_NEO4J_URI=bolt://localhost:7687
AI_FRAMEWORK_POSTGRES_URL=postgresql://user:pass@localhost:5432/db_dev
AI_FRAMEWORK_QDRANT_URL=http://localhost:6333

# Development Settings
AI_FRAMEWORK_RELOAD=true
AI_FRAMEWORK_HOT_RELOAD=true
AI_FRAMEWORK_PROFILE=true

# OpenAI Configuration
OPENAI_API_KEY={{OPENAI_API_KEY}}
OPENAI_MODEL=gpt-4
```

#### Production Environment (`.env.production`)
```bash
# AI Enhancement Framework - Production Configuration
AI_FRAMEWORK_ENV=production
AI_FRAMEWORK_LOG_LEVEL=INFO
AI_FRAMEWORK_DEBUG=false

# Database Connections (use secrets management)
AI_FRAMEWORK_REDIS_URL=${REDIS_URL}
AI_FRAMEWORK_NEO4J_URI=${NEO4J_URI}
AI_FRAMEWORK_POSTGRES_URL=${POSTGRES_URL}
AI_FRAMEWORK_QDRANT_URL=${QDRANT_URL}

# Security Settings
AI_FRAMEWORK_JWT_SECRET=${JWT_SECRET}
AI_FRAMEWORK_API_RATE_LIMIT=100
AI_FRAMEWORK_CORS_ORIGINS=${ALLOWED_ORIGINS}

# Performance Settings
AI_FRAMEWORK_MAX_WORKERS=8
AI_FRAMEWORK_CACHE_SIZE=1GB
AI_FRAMEWORK_MEMORY_LIMIT=4GB
```

### Docker Configuration Templates

#### Development Docker Compose
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    volumes:
      - .:/app
      - /app/ai-enhancement-env
    ports:
      - "8000:8000"
    environment:
      - AI_FRAMEWORK_ENV=development
    depends_on:
      - redis
      - neo4j
      - postgresql
      - qdrant

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password

  postgresql:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=ai_framework_dev
      - POSTGRES_USER=dev_user
      - POSTGRES_PASSWORD=dev_password

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
```

## 🛠️ Development Templates

### GitHub Actions Workflow Template
```yaml
name: AI Enhancement Framework CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
      
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Configuration Template
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 🎨 Template Customization

### Project Customization Script
```python
#!/usr/bin/env python3
"""
AI Enhancement Framework - Project Template Customizer
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

class ProjectCustomizer:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.placeholders = {}
    
    def collect_project_info(self):
        """Collect project information from user"""
        print("🎯 AI Enhancement Framework Project Setup")
        print("=" * 50)
        
        self.placeholders = {
            'PROJECT_NAME': input("Project name: "),
            'PROJECT_TYPE': self.select_project_type(),
            'PROJECT_COMPLEXITY': self.select_complexity(),
            'ANALYSIS_DEPTH': self.select_analysis_depth(),
            'TEST_COVERAGE': input("Target test coverage (default 95): ") or "95",
            'OPENAI_API_KEY': input("OpenAI API Key (optional): ") or "your_api_key_here"
        }
    
    def select_project_type(self) -> str:
        """Select project type"""
        types = [
            "python",
            "web_api", 
            "data_science",
            "machine_learning",
            "desktop_app"
        ]
        
        print("\nSelect project type:")
        for i, ptype in enumerate(types, 1):
            print(f"  {i}. {ptype}")
        
        choice = int(input("Choice (1-5): ")) - 1
        return types[choice]
    
    def select_complexity(self) -> str:
        """Select project complexity"""
        complexities = ["simple", "moderate", "complex", "extensive"]
        
        print("\nSelect project complexity:")
        for i, complexity in enumerate(complexities, 1):
            print(f"  {i}. {complexity}")
        
        choice = int(input("Choice (1-4): ")) - 1
        return complexities[choice]
    
    def select_analysis_depth(self) -> str:
        """Select AI analysis depth"""
        depths = ["basic", "standard", "comprehensive"]
        
        print("\nSelect AI analysis depth:")
        for i, depth in enumerate(depths, 1):
            print(f"  {i}. {depth}")
        
        choice = int(input("Choice (1-3): ")) - 1
        return depths[choice]
    
    def customize_files(self):
        """Customize template files with user input"""
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(('.md', '.py', '.yml', '.yaml', '.json', '.env')):
                    file_path = Path(root) / file
                    self.customize_file(file_path)
    
    def customize_file(self, file_path: Path):
        """Customize individual file"""
        try:
            content = file_path.read_text()
            
            for placeholder, value in self.placeholders.items():
                content = content.replace(f"{{{{{placeholder}}}}}", str(value))
            
            file_path.write_text(content)
            print(f"✅ Customized {file_path}")
            
        except Exception as e:
            print(f"❌ Error customizing {file_path}: {e}")
    
    def run(self):
        """Run the customization process"""
        self.collect_project_info()
        self.customize_files()
        
        print("\n🎉 Project customization complete!")
        print("\nNext steps:")
        print("1. Review and edit configuration files")
        print("2. Run: ./scripts/setup.sh")
        print("3. Start development: cursor .")

if __name__ == "__main__":
    project_path = Path.cwd()
    customizer = ProjectCustomizer(project_path)
    customizer.run()
```

## 📊 Template Usage Analytics

### Template Selection Guidelines

#### Choose **Basic Python** for:
- Simple scripts and utilities
- Learning and experimentation
- Quick prototypes
- Small automation tasks

#### Choose **Web API** for:
- REST API services
- Microservices architecture
- Web application backends
- API-first applications

#### Choose **Data Science** for:
- Data analysis projects
- Research and exploration
- Report generation
- Statistical analysis

#### Choose **Machine Learning** for:
- Model training and deployment
- MLOps pipelines
- Production ML systems
- AI-powered applications

## 🔧 Extending Templates

### Creating Custom Templates
```bash
# Create new template directory
mkdir templates/custom_template/

# Copy base template
cp -r templates/project/basic_python/* templates/custom_template/

# Customize template files
# Add your specific configurations
# Update placeholder values

# Test template
python -m ai_enhancement_framework test-template templates/custom_template/
```

### Template Validation
```python
from pathlib import Path
from ai_enhancement_framework.templates import TemplateValidator

def validate_template(template_path: Path) -> bool:
    """Validate template structure and content"""
    validator = TemplateValidator(template_path)
    
    results = validator.validate()
    
    if results.is_valid:
        print("✅ Template is valid")
        return True
    else:
        print("❌ Template validation failed:")
        for error in results.errors:
            print(f"  - {error}")
        return False
```

## 🚀 Production Deployment Templates

### Kubernetes Deployment Template
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-framework-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-framework
  template:
    metadata:
      labels:
        app: ai-framework
    spec:
      containers:
      - name: app
        image: ai-framework:latest
        ports:
        - containerPort: 8000
        env:
        - name: AI_FRAMEWORK_ENV
          value: "production"
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
          requests:
            memory: "1Gi"
            cpu: "500m"
```

### Docker Production Template
```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as runtime

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8000

USER 1000

CMD ["python", "-m", "src.main"]
```

## 📚 Template Documentation

### Template Structure Guidelines
1. **Consistent Naming**: Use descriptive, standardized names
2. **Clear Organization**: Logical directory structure
3. **Documentation**: Comprehensive README files
4. **Configurability**: Placeholder-based customization
5. **Best Practices**: Follow framework conventions

### Template Maintenance
- Regular updates for framework changes
- Version compatibility testing
- Security vulnerability patches
- Performance optimizations
- User feedback integration

## 🔗 Related Documentation

- **[Project Template README](project/README.md)** - Project template documentation
- **[Configuration Guide](../cursor/CONFIGURATION_GUIDE.md)** - Advanced configuration
- **[Installation Guide](../cursor/CURSOR_INSTALLATION_HOW_TO.md)** - Setup instructions
- **[Docker Configuration](../docker/docker-compose.yml)** - Container orchestration
- **[Monitoring Framework](../monitoring/README.md)** - Health monitoring

---

**Environment Templates Version**: 1.0.0  
**AI Enhancement Framework**: 1.0.0  
**Last Updated**: January 18, 2025  
**Status**: Production Ready ✅ 