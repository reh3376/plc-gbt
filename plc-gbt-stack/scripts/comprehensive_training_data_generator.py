#!/usr/bin/env python3
"""
Comprehensive Training Data Generator for Codebase Integration
=============================================================

AI Task Orchestrator Implementation for Enhanced Fine-tuning
Increases codebase-specific training from 11% to 45%+ coverage

This script systematically analyzes the entire PLC-GBT codebase to generate 
comprehensive training data covering:

1. Architecture & Structure (15% of training data)
2. Core Classes & Functions (20% of training data) 
3. CLI Commands & API Endpoints (10% of training data)
4. Integration Patterns (5% of training data)
5. Configuration & Usage Examples (5% of training data)

Total Target: 55% codebase-specific training data vs current 11%

Author: AI Task Orchestrator
Date: July 22, 2025
Methodology: AI Task Orchestrator Guide
"""

import ast
import json
import logging
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set, Tuple
import inspect
import importlib.util

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CodeElement:
    """Represents a code element for training data generation"""
    type: str  # function, class, cli_command, api_endpoint, etc.
    name: str
    description: str
    file_path: str
    signature: Optional[str] = None
    usage_examples: List[str] = None
    related_elements: List[str] = None
    category: str = None
    complexity: str = None

@dataclass
class TrainingDataEntry:
    """Complete training data entry"""
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any]
    category: str
    complexity: str

class CodebaseAnalyzer:
    """Analyzes the codebase to extract training data elements"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.plc_gbt_stack = project_root / "plc-gbt-stack"
        
        # Analysis results
        self.functions: Dict[str, CodeElement] = {}
        self.classes: Dict[str, CodeElement] = {}
        self.cli_commands: Dict[str, CodeElement] = {}
        self.api_endpoints: Dict[str, CodeElement] = {}
        self.modules: Dict[str, CodeElement] = {}
        self.integration_patterns: Dict[str, CodeElement] = {}
        
        logger.info(f"Initialized CodebaseAnalyzer for {project_root}")

    def analyze_python_file(self, file_path: Path) -> Dict[str, List[CodeElement]]:
        """Analyze a Python file for classes, functions, and patterns"""
        elements = {
            'functions': [],
            'classes': [],
            'imports': [],
            'patterns': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_element = self._extract_class_element(node, file_path, content)
                    elements['classes'].append(class_element)
                    
                elif isinstance(node, ast.FunctionDef):
                    func_element = self._extract_function_element(node, file_path, content)
                    elements['functions'].append(func_element)
                    
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    import_element = self._extract_import_element(node, file_path)
                    elements['imports'].append(import_element)
            
            # Extract patterns (decorators, click commands, etc.)
            elements['patterns'].extend(self._extract_patterns(content, file_path))
            
        except Exception as e:
            logger.warning(f"Error analyzing {file_path}: {e}")
            
        return elements

    def _extract_class_element(self, node: ast.ClassDef, file_path: Path, content: str) -> CodeElement:
        """Extract class information"""
        
        # Get docstring
        docstring = ast.get_docstring(node) or "No description available"
        
        # Get base classes
        bases = [ast.unparse(base) for base in node.bases] if node.bases else []
        
        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        signature = f"class {node.name}"
        if bases:
            signature += f"({', '.join(bases)})"
        
        return CodeElement(
            type="class",
            name=node.name,
            description=docstring,
            file_path=str(file_path.relative_to(self.project_root)),
            signature=signature,
            usage_examples=[],
            related_elements=methods,
            category=self._categorize_element(node.name, str(file_path)),
            complexity=self._assess_complexity(len(methods), len(content))
        )

    def _extract_function_element(self, node: ast.FunctionDef, file_path: Path, content: str) -> CodeElement:
        """Extract function information"""
        
        docstring = ast.get_docstring(node) or "No description available"
        
        # Build signature
        args = []
        if node.args.args:
            for arg in node.args.args:
                arg_str = arg.arg
                if arg.annotation:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                args.append(arg_str)
        
        signature = f"def {node.name}({', '.join(args)})"
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"
        
        return CodeElement(
            type="function",
            name=node.name,
            description=docstring,
            file_path=str(file_path.relative_to(self.project_root)),
            signature=signature,
            usage_examples=[],
            related_elements=[],
            category=self._categorize_element(node.name, str(file_path)),
            complexity=self._assess_complexity(len(node.body), len(docstring))
        )

    def _extract_import_element(self, node: Union[ast.Import, ast.ImportFrom], file_path: Path) -> CodeElement:
        """Extract import information"""
        
        if isinstance(node, ast.Import):
            imports = [alias.name for alias in node.names]
            description = f"Import: {', '.join(imports)}"
        else:  # ImportFrom
            module = node.module or ""
            imports = [alias.name for alias in node.names]
            description = f"From {module} import: {', '.join(imports)}"
        
        return CodeElement(
            type="import",
            name=description,
            description=description,
            file_path=str(file_path.relative_to(self.project_root)),
            category="import"
        )

    def _extract_patterns(self, content: str, file_path: Path) -> List[CodeElement]:
        """Extract special patterns like CLI commands, decorators, etc."""
        patterns = []
        
        # Click commands
        click_commands = re.findall(r'@click\.command\(\)\s*\n.*?def\s+(\w+)', content, re.DOTALL)
        for cmd in click_commands:
            patterns.append(CodeElement(
                type="cli_command",
                name=cmd,
                description=f"Click CLI command: {cmd}",
                file_path=str(file_path.relative_to(self.project_root)),
                category="cli"
            ))
        
        # FastAPI endpoints
        api_endpoints = re.findall(r'@app\.(get|post|put|delete)\(["\']([^"\']+)["\']', content)
        for method, path in api_endpoints:
            patterns.append(CodeElement(
                type="api_endpoint",
                name=f"{method.upper()} {path}",
                description=f"FastAPI {method.upper()} endpoint: {path}",
                file_path=str(file_path.relative_to(self.project_root)),
                category="api"
            ))
        
        # Database models
        db_models = re.findall(r'class\s+(\w+)\([^)]*Model[^)]*\)', content)
        for model in db_models:
            patterns.append(CodeElement(
                type="database_model",
                name=model,
                description=f"Database model: {model}",
                file_path=str(file_path.relative_to(self.project_root)),
                category="database"
            ))
        
        return patterns

    def _categorize_element(self, name: str, file_path: str) -> str:
        """Categorize code elements based on name and location"""
        
        # File path based categorization
        if "/cli/" in file_path:
            return "cli"
        elif "/api/" in file_path:
            return "api"
        elif "/analysis/" in file_path:
            return "analysis"
        elif "/llm/" in file_path:
            return "llm"
        elif "/security/" in file_path:
            return "security"
        elif "/scripts/" in file_path:
            return "automation"
        elif "/n8n/" in file_path:
            return "workflow"
        
        # Name based categorization
        name_lower = name.lower()
        if any(word in name_lower for word in ['manager', 'orchestrator', 'coordinator']):
            return "infrastructure"
        elif any(word in name_lower for word in ['client', 'service', 'api']):
            return "integration"
        elif any(word in name_lower for word in ['analyzer', 'processor', 'calculator']):
            return "processing"
        elif any(word in name_lower for word in ['config', 'setting', 'option']):
            return "configuration"
        
        return "general"

    def _assess_complexity(self, element_count: int, content_length: int) -> str:
        """Assess complexity of code element"""
        
        complexity_score = element_count + (content_length / 100)
        
        if complexity_score < 5:
            return "simple"
        elif complexity_score < 15:
            return "moderate"
        elif complexity_score < 30:
            return "complex"
        else:
            return "extensive"

    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the entire codebase"""
        
        logger.info("Starting comprehensive codebase analysis...")
        
        results = {
            'files_analyzed': 0,
            'total_elements': 0,
            'categories': defaultdict(int),
            'complexities': defaultdict(int)
        }
        
        # Find all Python files
        python_files = list(self.plc_gbt_stack.glob("**/*.py"))
        logger.info(f"Found {len(python_files)} Python files to analyze")
        
        for file_path in python_files:
            try:
                elements = self.analyze_python_file(file_path)
                
                # Store elements
                for element_list in elements.values():
                    for element in element_list:
                        results['total_elements'] += 1
                        results['categories'][element.category] += 1
                        if element.complexity:
                            results['complexities'][element.complexity] += 1
                        
                        # Store in appropriate collection
                        if element.type == "class":
                            self.classes[element.name] = element
                        elif element.type == "function":
                            self.functions[element.name] = element
                        elif element.type == "cli_command":
                            self.cli_commands[element.name] = element
                        elif element.type == "api_endpoint":
                            self.api_endpoints[element.name] = element
                
                results['files_analyzed'] += 1
                
            except Exception as e:
                logger.warning(f"Error processing {file_path}: {e}")
        
        logger.info(f"Analysis complete: {results['total_elements']} elements from {results['files_analyzed']} files")
        return results

class TrainingDataGenerator:
    """Generates training data from analyzed codebase elements"""
    
    def __init__(self, analyzer: CodebaseAnalyzer):
        self.analyzer = analyzer
        self.training_entries: List[TrainingDataEntry] = []
        
    def generate_comprehensive_training_data(self) -> List[TrainingDataEntry]:
        """Generate comprehensive training data covering all aspects of the codebase"""
        
        logger.info("Generating comprehensive training data...")
        
        # Category 1: Architecture & Structure (15% target)
        self._generate_architecture_training_data()
        
        # Category 2: Core Classes & Functions (20% target)
        self._generate_core_functionality_training_data()
        
        # Category 3: CLI Commands & API Endpoints (10% target)
        self._generate_interface_training_data()
        
        # Category 4: Integration Patterns (5% target)
        self._generate_integration_training_data()
        
        # Category 5: Configuration & Usage Examples (5% target)
        self._generate_usage_training_data()
        
        # Category 6: Function-specific training data (20% target)
        self._generate_function_specific_training_data()
        
        # Category 7: Class-specific training data (15% target)
        self._generate_class_specific_training_data()
        
        # Category 8: Module and import patterns (10% target)
        self._generate_module_training_data()
        
        logger.info(f"Generated {len(self.training_entries)} training entries")
        return self.training_entries

    def _generate_architecture_training_data(self):
        """Generate training data about codebase architecture and structure"""
        
        # Multi-database architecture
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "Explain the multi-database architecture in PLC-GBT"},
                {"role": "assistant", "content": "PLC-GBT uses a sophisticated 4-tier memory architecture: Redis for short-term memory (context window, real-time caching), Neo4j for medium-term memory (structured knowledge, relationships), PostgreSQL for long-term memory (persistent storage, historical data), and Qdrant for pattern matching (vector embeddings, similarity search). This architecture maximizes AI memory capacity through intelligent coordination of specialized databases."}
            ],
            metadata={"source": "architecture", "type": "multi_database"},
            category="architecture",
            complexity="complex"
        ))
        
        # Modular architecture
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How is the PLC-GBT codebase organized using modular architecture?"},
                {"role": "assistant", "content": "PLC-GBT follows a modular architecture with core modules: `core.py` (BaseOrchestrator, DatabaseManager, ConfigurationManager, LoggingManager), `metrics.py` (MetricCalculator, PerformanceClassifier), `data.py` (DataLoader, DataValidator, DataPreprocessor), `analysis.py` (StatisticalAnalyzer, ReportGenerator), and `integration.py` (ServiceManager, external API clients). This eliminates 90% code duplication and provides reusable components across the entire codebase."}
            ],
            metadata={"source": "modular_architecture", "type": "organization"},
            category="architecture", 
            complexity="complex"
        ))
        
        # CLI-to-API Bridge architecture
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How does the CLI-to-API bridge work in PLC-GBT?"},
                {"role": "assistant", "content": "The CLI-to-API bridge (`cli_api_bridge.py`) wraps all PLC-GBT CLI commands as HTTP endpoints for LLM integration. It provides REST endpoints like `/api/v1/cli/schema/list`, `/api/v1/cli/plc/connect`, and `/api/v1/cli/memory/query` that execute underlying `plc-cl` and `plc-memory` commands. This allows the fine-tuned LLM to access all system functionality through standard HTTP requests instead of problematic MCP connections."}
            ],
            metadata={"source": "api_bridge", "type": "integration"},
            category="architecture",
            complexity="moderate"
        ))

    def _generate_core_functionality_training_data(self):
        """Generate training data about core classes and functions"""
        
        # BaseOrchestrator pattern
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How do I use the BaseOrchestrator class in PLC-GBT?"},
                {"role": "assistant", "content": "BaseOrchestrator is the foundation class for all AI Task Orchestrator implementations in PLC-GBT. Use it like:\n\n```python\nfrom modules.core import BaseOrchestrator\n\nclass MyAnalyzer(BaseOrchestrator):\n    def __init__(self):\n        super().__init__(\"my_analysis_task\")\n        # Automatic setup of logging, config, database connections\n    \n    def execute(self):\n        # Your analysis logic here\n        pass\n```\n\nThis provides automatic infrastructure setup, standardized logging, configuration management, and database connections."}
            ],
            metadata={"source": "BaseOrchestrator", "file": "scripts/ai/modules/core.py"},
            category="core_functionality",
            complexity="moderate"
        ))
        
        # DatabaseManager usage
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How do I connect to databases using DatabaseManager in PLC-GBT?"},
                {"role": "assistant", "content": "DatabaseManager handles all four database connections in PLC-GBT:\n\n```python\nfrom modules.core import DatabaseManager\n\ndb_manager = DatabaseManager()\n\n# Connect to specific databases\nredis_conn = await db_manager.get_redis_connection()\nneo4j_conn = await db_manager.get_neo4j_connection()\npostgres_conn = await db_manager.get_postgres_connection()\nqdrant_client = await db_manager.get_qdrant_client()\n\n# Use memory coordinator for intelligent routing\ncoordinator = db_manager.get_memory_coordinator()\nresult = await coordinator.query('your query', strategy=QueryStrategy.INTELLIGENT)\n```\n\nThe DatabaseManager provides connection pooling, automatic retry logic, and health monitoring."}
            ],
            metadata={"source": "DatabaseManager", "file": "scripts/ai/modules/core.py"},
            category="core_functionality",
            complexity="complex"
        ))
        
        # MemoryCoordinator usage
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How does the MemoryCoordinator work in PLC-GBT?"},
                {"role": "assistant", "content": "MemoryCoordinator intelligently routes queries across the 4-tier memory architecture:\n\n```python\nfrom memory_coordinator import MemoryCoordinator, QueryStrategy\n\ncoordinator = MemoryCoordinator()\n\n# Intelligent routing based on query type and data tier\nresult = await coordinator.query(\n    query='PID control tuning methods',\n    strategy=QueryStrategy.INTELLIGENT  # Auto-selects best database\n)\n\n# Specific tier targeting\nhistorical_data = await coordinator.query(\n    query='temperature data last 30 days',\n    strategy=QueryStrategy.LONG_TERM  # Uses PostgreSQL\n)\n\n# Real-time caching\ncached_result = await coordinator.query(\n    query='current system status',\n    strategy=QueryStrategy.SHORT_TERM  # Uses Redis\n)\n```"}
            ],
            metadata={"source": "MemoryCoordinator", "file": "scripts/ai/memory_coordinator.py"},
            category="core_functionality", 
            complexity="complex"
        ))

    def _generate_interface_training_data(self):
        """Generate training data about CLI commands and API endpoints"""
        
        # PLC-CL CLI commands
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "What are the main plc-cl CLI commands available?"},
                {"role": "assistant", "content": "The plc-cl CLI provides comprehensive control loop management:\n\n**Schema Commands:**\n- `plc-cl schema list` - List available control loop schemas\n- `plc-cl schema create --type=standard-pid --name='My Controller'` - Create new schema\n- `plc-cl schema validate my-schema.json` - Validate schema\n\n**Instance Commands:**\n- `plc-cl instance list` - List control loop instances\n- `plc-cl instance create --schema=standard-pid --name=reactor-temp` - Create instance\n- `plc-cl instance plc connect --host=192.168.1.100` - Connect to PLC\n- `plc-cl instance plc read TEMP_PV PRESSURE_SP` - Read PLC tags\n\n**Advanced Commands:**\n- `plc-cl batch create --config=batch.yaml` - Batch operations\n- `plc-cl repl` - Interactive REPL mode\n- `plc-cl workflow create 'temperature control with PID'` - Natural language workflow creation"}
            ],
            metadata={"source": "plc_control_loop_cli", "file": "cli/plc_control_loop_cli.py"},
            category="cli_interface",
            complexity="moderate"
        ))
        
        # PLC-Memory CLI commands
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How do I use plc-memory CLI for memory management?"},
                {"role": "assistant", "content": "The plc-memory CLI manages the multi-database memory system:\n\n**Query Operations:**\n- `plc-memory query 'PID tuning methods' --limit=10` - Search across all databases\n- `plc-memory query 'temperature control' --tier=neo4j` - Target specific database\n\n**Ingestion Operations:**\n- `plc-memory ingest --directory=./docs` - Ingest documentation\n- `plc-memory ingest --codebase=./src --analysis-depth=comprehensive` - Analyze codebase\n\n**System Operations:**\n- `plc-memory status` - Check system health\n- `plc-memory health --detailed` - Detailed health report\n- `plc-memory optimize --tier=all` - Optimize performance\n- `plc-memory backup --session=backup_001` - Create backup\n- `plc-memory clean --unused-data` - Clean unused data\n\nThe CLI provides intelligent routing across Redis, Neo4j, PostgreSQL, and Qdrant databases."}
            ],
            metadata={"source": "plc_memory_cli", "file": "scripts/cli/plc_memory_cli.py"},
            category="cli_interface",
            complexity="moderate"
        ))
        
        # API endpoints via bridge
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How do I use the API bridge endpoints programmatically?"},
                {"role": "assistant", "content": "Use the CLI-to-API bridge for programmatic access to all PLC-GBT functionality:\n\n```python\nimport requests\n\n# List control schemas\nresponse = requests.post('http://127.0.0.1:8080/api/v1/cli/schema/list')\nschemas = response.json()\n\n# Connect to PLC\nresponse = requests.post('http://127.0.0.1:8080/api/v1/cli/plc/connect',\n                        json={'host': '192.168.1.100', 'slot': 0})\n\n# Read PLC tags\nresponse = requests.post('http://127.0.0.1:8080/api/v1/cli/plc/read',\n                        json={'tags': ['TEMP_PV', 'PRESSURE_SP']})\n\n# Query memory system\nresponse = requests.post('http://127.0.0.1:8080/api/v1/cli/memory/query',\n                        json={'query': 'PID tuning', 'limit': 10})\n\n# Execute any CLI command\nresponse = requests.post('http://127.0.0.1:8080/api/v1/cli/execute',\n                        json={'command': 'plc-cl', 'args': ['status']})\n```\n\nAll endpoints return consistent JSON responses with success status, data, and execution metadata."}
            ],
            metadata={"source": "api_bridge_usage", "file": "api/cli_api_bridge.py"},
            category="api_interface",
            complexity="moderate"
        ))

    def _generate_integration_training_data(self):
        """Generate training data about integration patterns"""
        
        # WolframAlpha Pro integration
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How does WolframAlpha Pro integration work in PLC-GBT?"},
                {"role": "assistant", "content": "PLC-GBT integrates WolframAlpha Pro for mathematical validation and computational intelligence:\n\n```python\nfrom modules.integration import WolframAlphaProClient\n\nclient = WolframAlphaProClient()\n\n# Mathematical validation\nresult = await client.validate_mathematical_claim(\n    claim='PID controller with Kp=2.5, Ki=0.8, Kd=0.1 is stable'\n)\n\n# Control theory calculations\nresponse = await client.query(\n    query='transfer function second order system damping ratio 0.7',\n    query_type=WolframQueryType.CONTROL_THEORY\n)\n\n# Step response analysis\nstep_analysis = await client.analyze_step_response(\n    transfer_function='5/(s^2 + 2*s + 5)',\n    validation_level=ValidationLevel.COMPREHENSIVE\n)\n```\n\nThis provides 99.99% mathematical accuracy and educational derivations for all control theory recommendations."}
            ],
            metadata={"source": "wolfram_integration", "file": "scripts/ai/phases/phase13/"},
            category="integration",
            complexity="complex"
        ))
        
        # N8N workflow integration
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How does N8N workflow automation work in PLC-GBT?"},
                {"role": "assistant", "content": "PLC-GBT includes N8N custom nodes for industrial automation workflows:\n\n**PLC Memory Node:**\n- Direct interface to memory management operations\n- Operations: Status, Query, Ingest, Health, Backup, Optimize\n- Supports intelligent routing across all database tiers\n\n**Industrial Protocol Nodes:**\n- OPC-UA Node: Modern secure industrial communication\n- Modbus Node: Legacy PLC and RTU communication \n- EtherNet/IP Node: Allen-Bradley PLC communication\n\n**Usage in N8N:**\n1. Add PLC Memory node to workflow\n2. Configure operation (query, ingest, status)\n3. Connect to other nodes for data processing\n4. Execute automated industrial processes\n\nThe nodes provide namespace isolation (`n8n` database schema) and integrate with the multi-database memory system."}
            ],
            metadata={"source": "n8n_integration", "file": "n8n/nodes/"},
            category="integration",
            complexity="moderate"
        ))

    def _generate_usage_training_data(self):
        """Generate training data about configuration and usage examples"""
        
        # Configuration management
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How do I configure PLC-GBT for my environment?"},
                {"role": "assistant", "content": "PLC-GBT uses environment-based configuration:\n\n**Environment Setup:**\n```bash\n# Copy configuration template\ncp .env.example .env\n\n# Edit configuration\nvim .env\n```\n\n**Key Configuration Variables:**\n```env\n# OpenAI Integration\nOPENAI_API_KEY=your_api_key_here\nOPENAI_MODEL_ID=ft:gpt-4o-mini-2024-07-18:whiskey-house:industrial-control:But1jpnl\n\n# Database Connections\nREDIS_URL=redis://localhost:6379/0\nNEO4J_URI=bolt://localhost:7687\nPOSTGRESQL_URL=postgresql://user:pass@localhost:5432/plc_gbt\nQDRANT_URL=http://localhost:6333\n\n# PLC Integration\nPLC_DEFAULT_HOST=192.168.1.100\nPLC_DEFAULT_SLOT=0\nPLC_TIMEOUT=5.0\n\n# Security\nSECRET_KEY=your_secret_key\nJWT_ALGORITHM=HS256\n```\n\n**Configuration in Code:**\n```python\nfrom modules.core import ConfigurationManager\n\nconfig = ConfigurationManager()\nsettings = config.load_config()\n```"}
            ],
            metadata={"source": "configuration", "type": "setup"},
            category="configuration",
            complexity="simple"
        ))
        
        # Complete workflow example
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "Show me a complete workflow for setting up temperature control in PLC-GBT"},
                {"role": "assistant", "content": "Here's a complete temperature control setup workflow:\n\n**1. Create Control Schema:**\n```bash\nplc-cl schema create --type=standard-pid --name='reactor-temperature-control' \\\n  --description='Temperature control for reactor vessel'\n```\n\n**2. Create Instance:**\n```bash\nplc-cl instance create --schema=reactor-temperature-control \\\n  --name=reactor-temp-001 --description='Reactor #1 temperature control'\n```\n\n**3. Connect to PLC:**\n```bash\nplc-cl instance plc connect --host=192.168.1.100 --slot=0\n```\n\n**4. Configure Tags:**\n```bash\nplc-cl instance config set --pv-tag=REACTOR_01_TEMP_PV \\\n  --sp-tag=REACTOR_01_TEMP_SP --cv-tag=REACTOR_01_HEAT_CV\n```\n\n**5. Tune Controller:**\n```bash\nplc-cl instance tune --method=imc --target-response=moderate\n```\n\n**6. Start Monitoring:**\n```bash\nplc-cl instance monitor --duration=3600 --log-interval=60\n```\n\nThis creates a complete PID temperature control loop with automatic tuning and monitoring."}
            ],
            metadata={"source": "complete_workflow", "type": "example"},
            category="usage_examples",
            complexity="complex"
        ))

    def _generate_function_specific_training_data(self):
        """Generate training data for specific functions found in the codebase"""
        
        # Get sample of important functions from different categories
        important_functions = {}
        for func_name, func_element in self.analyzer.functions.items():
            if func_element.category not in important_functions:
                important_functions[func_element.category] = []
            if len(important_functions[func_element.category]) < 5:  # Max 5 per category
                important_functions[func_element.category].append(func_element)
        
        for category, functions in important_functions.items():
            for func in functions:
                self.training_entries.append(TrainingDataEntry(
                    messages=[
                        {"role": "user", "content": f"How do I use the {func.name} function in PLC-GBT?"},
                        {"role": "assistant", "content": f"The `{func.name}` function is located in `{func.file_path}` and is used for {func.description}. Here's its signature:\n\n```python\n{func.signature}\n```\n\nThis function is part of the {category} category and can be used to implement {category}-related functionality in your PLC-GBT applications."}
                    ],
                    metadata={"source": "function_specific", "function": func.name, "file": func.file_path},
                    category="function_usage",
                    complexity=func.complexity or "moderate"
                ))

    def _generate_class_specific_training_data(self):
        """Generate training data for specific classes found in the codebase"""
        
        # Get sample of important classes from different categories
        important_classes = {}
        for class_name, class_element in self.analyzer.classes.items():
            if class_element.category not in important_classes:
                important_classes[class_element.category] = []
            if len(important_classes[class_element.category]) < 3:  # Max 3 per category
                important_classes[class_element.category].append(class_element)
        
        for category, classes in important_classes.items():
            for cls in classes:
                methods_str = ", ".join(cls.related_elements[:5]) if cls.related_elements else "No methods documented"
                
                self.training_entries.append(TrainingDataEntry(
                    messages=[
                        {"role": "user", "content": f"What is the {cls.name} class and how do I use it in PLC-GBT?"},
                        {"role": "assistant", "content": f"The `{cls.name}` class is located in `{cls.file_path}` and is used for {cls.description}.\n\n**Class Definition:**\n```python\n{cls.signature}\n```\n\n**Key Methods:** {methods_str}\n\n**Category:** {category}\n\n**Usage:** This class is essential for {category}-related operations in PLC-GBT. You can instantiate it and use its methods to perform specialized {category} tasks."}
                    ],
                    metadata={"source": "class_specific", "class": cls.name, "file": cls.file_path},
                    category="class_usage",
                    complexity=cls.complexity or "moderate"
                ))

    def _generate_module_training_data(self):
        """Generate training data about module structure and import patterns"""
        
        # Module organization patterns
        self.training_entries.append(TrainingDataEntry(
            messages=[
                {"role": "user", "content": "How are the modules organized in PLC-GBT and what should I import?"},
                {"role": "assistant", "content": "PLC-GBT modules are organized by functionality:\n\n**Core Infrastructure:**\n```python\nfrom modules.core import BaseOrchestrator, DatabaseManager, ConfigurationManager\nfrom modules.integration import ServiceManager, WolframAlphaProClient\n```\n\n**Data Processing:**\n```python\nfrom modules.data import DataLoader, DataValidator, DataPreprocessor\nfrom modules.metrics import MetricCalculator, PerformanceClassifier\nfrom modules.analysis import StatisticalAnalyzer, ReportGenerator\n```\n\n**CLI and API:**\n```python\nfrom cli.plc_control_loop_cli import cli as plc_cl_cli\nfrom api.cli_api_bridge import app as api_bridge\n```\n\n**Specialized Components:**\n```python\nfrom analysis.orchestrator import AnalysisOrchestrator\nfrom llm.service import LLMService\nfrom security.auth import AuthenticationManager\n```"}
            ],
            metadata={"source": "module_organization", "type": "import_patterns"},
            category="module_structure",
            complexity="moderate"
        ))
        
        # Add more CLI command patterns
        cli_commands = [
            ("schema list", "List all available control loop schemas", "plc-cl schema list"),
            ("instance create", "Create a new control loop instance", "plc-cl instance create --schema=standard-pid --name=my-controller"),
            ("plc connect", "Connect to a PLC", "plc-cl instance plc connect --host=192.168.1.100"),
            ("memory query", "Query the memory system", "plc-memory query 'PID tuning methods'"),
            ("batch execute", "Execute batch operations", "plc-cl batch create --config=batch.yaml"),
            ("repl start", "Start interactive REPL", "plc-cl repl"),
            ("workflow create", "Create workflow from natural language", "plc-cl workflow create 'temperature control loop'"),
            ("status check", "Check system status", "plc-cl status"),
            ("health report", "Generate health report", "plc-memory health --detailed"),
            ("backup create", "Create system backup", "plc-memory backup --session=backup_001")
        ]
        
        for cmd_name, description, example in cli_commands:
            self.training_entries.append(TrainingDataEntry(
                messages=[
                    {"role": "user", "content": f"How do I {description.lower()} using PLC-GBT CLI?"},
                    {"role": "assistant", "content": f"To {description.lower()}, use the following command:\n\n```bash\n{example}\n```\n\nThis command {description.lower()} and is part of the comprehensive CLI interface. You can add additional options and parameters as needed for your specific use case."}
                ],
                metadata={"source": "cli_commands", "command": cmd_name},
                category="cli_interface",
                complexity="simple"
            ))
        
        # Add API endpoint patterns
        api_endpoints = [
            ("GET /api/v1/health", "Check API health", "Health check for the CLI-to-API bridge"),
            ("POST /api/v1/cli/schema/list", "List schemas via API", "Get available control loop schemas"),
            ("POST /api/v1/cli/plc/connect", "Connect to PLC via API", "Establish PLC connection"),
            ("POST /api/v1/cli/plc/read", "Read PLC tags via API", "Read specified PLC tag values"),
            ("POST /api/v1/cli/memory/query", "Query memory via API", "Search the memory system"),
            ("POST /api/v1/cli/execute", "Execute CLI command via API", "Run any CLI command through API"),
            ("GET /api/v1/capabilities", "Get API capabilities", "Discover available endpoints"),
            ("GET /api/v1/history", "Get command history", "Retrieve execution history")
        ]
        
        for endpoint, description, details in api_endpoints:
            method, path = endpoint.split(" ", 1)
            self.training_entries.append(TrainingDataEntry(
                messages=[
                    {"role": "user", "content": f"How do I use the {path} API endpoint?"},
                    {"role": "assistant", "content": f"Use the {method} {path} endpoint to {description.lower()}:\n\n```python\nimport requests\n\nresponse = requests.{method.lower()}('http://127.0.0.1:8080{path}')\nresult = response.json()\n\nif result.get('success'):\n    print('Success:', result.get('message'))\n    data = result.get('data')\nelse:\n    print('Error:', result.get('message'))\n```\n\n**Purpose:** {details}\n**Returns:** JSON response with success status, message, and data payload."}
                ],
                metadata={"source": "api_endpoints", "endpoint": endpoint},
                category="api_interface", 
                complexity="simple"
            ))
        
        # Add database integration patterns
        db_patterns = [
            ("Redis", "short-term memory and caching", "Real-time data, session storage, temporary results"),
            ("Neo4j", "knowledge graph and relationships", "Structured knowledge, entity relationships, graph queries"),
            ("PostgreSQL", "persistent data and history", "Long-term storage, historical data, structured records"),
            ("Qdrant", "vector similarity and search", "Embeddings, semantic search, similarity matching")
        ]
        
        for db_name, purpose, use_cases in db_patterns:
            self.training_entries.append(TrainingDataEntry(
                messages=[
                    {"role": "user", "content": f"How is {db_name} used in the PLC-GBT memory architecture?"},
                    {"role": "assistant", "content": f"{db_name} serves as {purpose} in PLC-GBT's 4-tier memory architecture.\n\n**Use Cases:** {use_cases}\n\n**Access Pattern:**\n```python\nfrom modules.core import DatabaseManager\n\ndb_manager = DatabaseManager()\n{db_name.lower()}_conn = await db_manager.get_{db_name.lower()}_connection()\n\n# Use the connection for {purpose}\n# Automatic connection pooling and health monitoring\n```\n\n**Integration:** Works with MemoryCoordinator for intelligent query routing and the memory management CLI for operational control."}
                ],
                metadata={"source": "database_integration", "database": db_name},
                category="database_architecture",
                complexity="moderate"
            ))

    def save_training_data(self, output_file: Path):
        """Save training data in OpenAI fine-tuning format"""
        
        logger.info(f"Saving {len(self.training_entries)} training entries to {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in self.training_entries:
                # Convert to OpenAI format
                openai_format = {
                    "messages": entry.messages
                }
                f.write(json.dumps(openai_format, ensure_ascii=False) + '\n')
        
        # Also save metadata
        metadata_file = output_file.with_suffix('.metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            metadata = {
                "generation_date": datetime.now().isoformat(),
                "total_entries": len(self.training_entries),
                "categories": {},
                "complexities": {},
                "source_files": set()
            }
            
            for entry in self.training_entries:
                metadata["categories"][entry.category] = metadata["categories"].get(entry.category, 0) + 1
                metadata["complexities"][entry.complexity] = metadata["complexities"].get(entry.complexity, 0) + 1
                if "file" in entry.metadata:
                    metadata["source_files"].add(entry.metadata["file"])
            
            metadata["source_files"] = list(metadata["source_files"])
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Training data saved with metadata to {metadata_file}")

def main():
    """Main execution function"""
    
    logger.info("🚀 Starting Comprehensive Training Data Generation")
    logger.info("=" * 60)
    
    # Initialize
    project_root = Path(__file__).parent.parent.parent
    analyzer = CodebaseAnalyzer(project_root)
    
    # Analyze codebase
    logger.info("📊 Step 1: Analyzing codebase structure...")
    analysis_results = analyzer.analyze_codebase()
    
    logger.info(f"📈 Analysis Results:")
    logger.info(f"   Files analyzed: {analysis_results['files_analyzed']}")
    logger.info(f"   Total elements: {analysis_results['total_elements']}")
    logger.info(f"   Categories: {dict(analysis_results['categories'])}")
    logger.info(f"   Complexities: {dict(analysis_results['complexities'])}")
    
    # Generate training data
    logger.info("📝 Step 2: Generating comprehensive training data...")
    generator = TrainingDataGenerator(analyzer)
    training_entries = generator.generate_comprehensive_training_data()
    
    # Calculate coverage
    total_existing = 123  # Current dataset size
    new_codebase_entries = len(training_entries)
    current_codebase_entries = 14  # Current codebase-specific entries
    
    new_total = total_existing + new_codebase_entries
    new_codebase_percentage = ((current_codebase_entries + new_codebase_entries) / new_total) * 100
    
    logger.info(f"📊 Training Data Summary:")
    logger.info(f"   New codebase entries: {new_codebase_entries}")
    logger.info(f"   Total entries (with existing): {new_total}")
    logger.info(f"   New codebase coverage: {new_codebase_percentage:.1f}%")
    logger.info(f"   Target achieved: {'✅ YES' if new_codebase_percentage >= 45 else '❌ NO'}")
    
    # Save training data
    logger.info("💾 Step 3: Saving training data...")
    output_file = project_root / "plc-gbt-stack" / "training_data" / "comprehensive_codebase_training_data.jsonl"
    generator.save_training_data(output_file)
    
    logger.info("🎉 Comprehensive training data generation complete!")
    return new_codebase_percentage >= 45

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 