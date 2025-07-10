#!/usr/bin/env python3
"""
🤖 Comprehensive Memory Management System - AI Task Orchestrator Implementation

Following AI Task Orchestrator Guide methodology for EXTENSIVE complexity task:
- Multi-database memory architecture design
- Comprehensive codebase ingestion system  
- Intelligent memory coordination layer
- CLI interface for repeatable operations
- Validation and testing framework

Author: AI Task Orchestrator
Created: 2025-01-09
Complexity: EXTENSIVE (>1500 lines, >15 files, >8 hours)
Context Management: Multi-step decomposition required
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Task complexity levels following AI Task Orchestrator Guide"""
    SIMPLE = "simple"      # < 100 lines, 1 file, < 1 hour
    MODERATE = "moderate"  # 100-500 lines, 2-5 files, 1-3 hours  
    COMPLEX = "complex"    # 500-1500 lines, 5-15 files, 3-8 hours
    EXTENSIVE = "extensive" # > 1500 lines, > 15 files, > 8 hours

class MemoryTier(Enum):
    """Memory tier classification for multi-database architecture"""
    SHORT_TERM = "short_term"      # Redis - Context window, real-time caching
    MEDIUM_TERM = "medium_term"    # Neo4j - Session memory, structured knowledge
    LONG_TERM = "long_term"        # PostgreSQL - Persistent storage, historical data
    PATTERN_MATCHING = "pattern"   # Qdrant - Vector embeddings, similarity search

@dataclass
class TaskAnalysis:
    """Comprehensive task analysis following AI Task Orchestrator methodology"""
    task_id: str
    complexity: TaskComplexity
    estimated_lines: int
    estimated_files: int
    estimated_hours: float
    requirements: List[str]
    dependencies: List[str]
    risks: List[str]
    resources_needed: Dict[str, Any]
    execution_plan: List[Dict[str, Any]]
    context_management: bool
    validation_criteria: List[str]

@dataclass
class MemoryArchitecture:
    """Multi-database memory architecture specification"""
    short_term_config: Dict[str, Any]   # Redis configuration
    medium_term_config: Dict[str, Any]  # Neo4j configuration  
    long_term_config: Dict[str, Any]    # PostgreSQL configuration
    pattern_config: Dict[str, Any]      # Qdrant configuration
    coordination_layer: Dict[str, Any]  # Memory coordination settings
    ingestion_pipelines: Dict[str, Any] # Codebase ingestion configuration

class ComprehensiveMemoryOrchestrator:
    """
    🎯 EXTENSIVE Complexity Task Implementation
    
    Following AI Task Orchestrator Guide for comprehensive multi-database
    memory management system with intelligent codebase ingestion.
    
    Features:
    - Multi-database architecture coordination (Neo4j, PostgreSQL, Qdrant, Redis)
    - Comprehensive codebase ingestion and analysis
    - Intelligent memory tier management
    - CLI interface for repeatable operations
    - Validation and testing framework
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize comprehensive memory orchestrator"""
        self.session_id = session_id or f"memory_orchestrator_{int(time.time())}"
        self.start_time = datetime.now()
        
        # AI Task Orchestrator compliance
        self.task_analysis = None
        self.memory_architecture = None
        self.context_documents = {}
        self.validation_results = {}
        
        # Database connections (will be initialized)
        self.connections = {
            'neo4j': None,
            'postgresql': None, 
            'qdrant': None,
            'redis': None
        }
        
        # System state
        self.ingestion_stats = {}
        self.memory_usage = {}
        self.performance_metrics = {}
        
        logger.info(f"ComprehensiveMemoryOrchestrator initialized with session: {self.session_id}")

    def analyze_task(self, task_description: str) -> TaskAnalysis:
        """
        🔍 STEP 1: AI Task Orchestrator Methodology - Comprehensive Task Analysis
        
        Analyzes the memory management system task following AI Task Orchestrator Guide.
        This is an EXTENSIVE complexity task requiring multi-step decomposition.
        """
        logger.info("🤖 Starting AI Task Orchestrator analysis for memory management system")
        
        # Complexity assessment
        complexity = TaskComplexity.EXTENSIVE
        estimated_lines = 3000  # Multiple components, coordination layer, CLI tools
        estimated_files = 25    # Database adapters, CLI tools, coordination layer, tests
        estimated_hours = 12    # Multi-step implementation with validation
        
        # Requirements extraction
        requirements = [
            "Multi-database architecture (Neo4j, PostgreSQL, Qdrant, Redis)",
            "Comprehensive codebase ingestion system",
            "Intelligent memory tier management",
            "Short-term memory (Redis) for context window issues",
            "Medium-term memory (Neo4j) for structured knowledge",
            "Long-term memory (PostgreSQL) for persistent storage", 
            "Pattern matching (Qdrant) for similarity search",
            "Memory coordination layer for intelligent data flow",
            "CLI interface for repeatable operations",
            "Validation and testing framework",
            "Performance monitoring and optimization",
            "Error handling and recovery mechanisms"
        ]
        
        # Dependencies identification
        dependencies = [
            "Existing Neo4j knowledge graph schema",
            "Current Qdrant vector database setup",
            "Docker PostgreSQL and Redis services",
            "Python database connection libraries",
            "Current codebase structure and file organization",
            "AI Task Orchestrator methodology compliance"
        ]
        
        # Risk assessment
        risks = [
            "Data migration complexity across multiple databases",
            "Memory coordination layer performance overhead",
            "Context window limitations during large codebase ingestion",
            "Database connection pool management under load",
            "Potential data consistency issues across databases",
            "CLI command complexity and user experience",
            "Validation framework false positives/negatives"
        ]
        
        # Resource discovery
        resources_needed = {
            "databases": ["neo4j", "postgresql", "qdrant", "redis"],
            "libraries": ["neo4j-driver", "psycopg2", "qdrant-client", "redis-py"],
            "knowledge_graph": True,
            "vector_database": True,
            "ai_orchestrator": True,
            "cli_framework": "click",
            "validation_tools": ["pytest", "json-schema"]
        }
        
        # Execution plan (multi-step decomposition)
        execution_plan = [
            {
                "step": 1,
                "phase": "analysis_and_design",
                "action": "Complete task analysis and architecture design",
                "description": "Apply AI Task Orchestrator methodology, design memory architecture",
                "deliverables": ["task_analysis.json", "memory_architecture.json"],
                "validation": "Architecture design review and dependency validation",
                "estimated_hours": 2
            },
            {
                "step": 2, 
                "phase": "database_integration",
                "action": "Implement database connection and management layer",
                "description": "Create unified database interface and connection management",
                "deliverables": ["database_manager.py", "connection_pool.py"],
                "validation": "Database connectivity and connection pool testing",
                "estimated_hours": 2
            },
            {
                "step": 3,
                "phase": "codebase_ingestion",
                "action": "Build comprehensive codebase ingestion system",
                "description": "Create file analysis, parsing, and multi-database storage system",
                "deliverables": ["codebase_analyzer.py", "file_processors.py", "ingestion_pipeline.py"],
                "validation": "Test with actual codebase files and validate data integrity",
                "estimated_hours": 3
            },
            {
                "step": 4,
                "phase": "memory_coordination",
                "action": "Implement intelligent memory coordination layer",
                "description": "Create smart routing and data management across memory tiers",
                "deliverables": ["memory_coordinator.py", "tier_manager.py"],
                "validation": "Memory routing logic and performance testing",
                "estimated_hours": 2
            },
            {
                "step": 5,
                "phase": "cli_interface",
                "action": "Develop CLI commands for repeatable operations",
                "description": "Create user-friendly command-line interface for all operations",
                "deliverables": ["memory_cli.py", "cli_commands.py"],
                "validation": "CLI usability testing and command validation",
                "estimated_hours": 2
            },
            {
                "step": 6,
                "phase": "validation_testing",
                "action": "Implement comprehensive validation and testing framework",
                "description": "Create testing suite and validation mechanisms",
                "deliverables": ["test_suite.py", "validation_framework.py"],
                "validation": "Complete system validation and performance benchmarking", 
                "estimated_hours": 1
            }
        ]
        
        # Validation criteria
        validation_criteria = [
            "All four databases successfully connected and coordinated",
            "Codebase ingestion processes all file types correctly",
            "Memory tiers function according to specification",
            "CLI commands work reliably and handle errors gracefully",
            "System performance meets acceptable thresholds",
            "Data integrity maintained across all databases",
            "Comprehensive test coverage (>90%)",
            "Documentation complete and user-friendly"
        ]
        
        # Create task analysis
        task_analysis = TaskAnalysis(
            task_id=self.session_id,
            complexity=complexity,
            estimated_lines=estimated_lines,
            estimated_files=estimated_files,
            estimated_hours=estimated_hours,
            requirements=requirements,
            dependencies=dependencies,
            risks=risks,
            resources_needed=resources_needed,
            execution_plan=execution_plan,
            context_management=True,  # Required for EXTENSIVE tasks
            validation_criteria=validation_criteria
        )
        
        self.task_analysis = task_analysis
        logger.info(f"✅ Task analysis complete: {complexity.value} complexity with {estimated_hours}h estimate")
        
        return task_analysis

    def design_memory_architecture(self) -> MemoryArchitecture:
        """
        🏗️ STEP 2: Memory Architecture Design
        
        Designs the multi-database memory architecture based on user requirements:
        - Redis: Short-term memory for context window issues
        - Neo4j: Medium-term memory for structured knowledge
        - PostgreSQL: Long-term memory for persistent storage
        - Qdrant: Pattern matching for similarity search and AI training
        """
        logger.info("🏗️ Designing multi-database memory architecture")
        
        # Redis (Short-term Memory) Configuration
        short_term_config = {
            "purpose": "Short-term memory for context window issues and real-time caching",
            "data_types": [
                "Active conversation context",
                "Recent code analysis results", 
                "Temporary session data",
                "Real-time performance metrics",
                "Cache for frequently accessed data"
            ],
            "ttl_settings": {
                "conversation_context": 3600,  # 1 hour
                "analysis_cache": 1800,        # 30 minutes
                "session_data": 7200,          # 2 hours
                "performance_metrics": 300     # 5 minutes
            },
            "memory_limit": "1GB",
            "eviction_policy": "allkeys-lru"
        }
        
        # Neo4j (Medium-term Memory) Configuration  
        medium_term_config = {
            "purpose": "Medium-term structured knowledge and relationships",
            "data_types": [
                "Code structure relationships",
                "Function call graphs",
                "Class inheritance hierarchies", 
                "Module dependencies",
                "Knowledge graph entities and relationships",
                "Session history and patterns"
            ],
            "retention_policy": "90 days for session data, indefinite for core knowledge",
            "indexing_strategy": "Optimized for graph traversal and relationship queries",
            "backup_frequency": "Daily incremental, weekly full"
        }
        
        # PostgreSQL (Long-term Memory) Configuration
        long_term_config = {
            "purpose": "Long-term persistent storage and historical data",
            "data_types": [
                "Complete codebase metadata and history",
                "File content snapshots and versions",
                "System performance history", 
                "User interaction logs",
                "Configuration and settings",
                "Audit trails and compliance data"
            ],
            "schema_design": {
                "codebase_files": "Complete file metadata and content storage",
                "code_analysis": "Static analysis results and metrics",
                "interaction_history": "Long-term user interaction patterns",
                "system_metrics": "Historical performance and usage data"
            },
            "retention_policy": "7 years for compliance, configurable for other data",
            "backup_strategy": "Continuous replication with point-in-time recovery"
        }
        
        # Qdrant (Pattern Matching) Configuration
        pattern_config = {
            "purpose": "Vector embeddings for pattern matching and AI model training",
            "data_types": [
                "Code embeddings for similarity search",
                "Documentation embeddings",
                "Function and class embeddings",
                "Usage pattern embeddings",
                "AI model training vectors"
            ],
            "embedding_models": [
                "text-embedding-3-large for general code",
                "code-specific embeddings for technical content",
                "Custom embeddings for domain-specific patterns"
            ],
            "vector_dimensions": 3072,  # text-embedding-3-large
            "similarity_metrics": ["cosine", "euclidean", "dot"],
            "indexing_strategy": "HNSW for fast approximate nearest neighbor search"
        }
        
        # Memory Coordination Layer Configuration
        coordination_layer = {
            "routing_logic": {
                "real_time_queries": "Redis first, fallback to other databases",
                "structural_queries": "Neo4j primary, PostgreSQL for detailed data",
                "historical_queries": "PostgreSQL primary, Redis for recent cache",
                "similarity_queries": "Qdrant primary, Neo4j for relationships"
            },
            "data_flow": {
                "ingestion": "PostgreSQL → Neo4j → Qdrant → Redis (hot data)",
                "retrieval": "Redis → Neo4j → Qdrant → PostgreSQL (cold data)",
                "updates": "Real-time to Redis, async propagation to other databases"
            },
            "consistency_strategy": "Eventually consistent with conflict resolution",
            "performance_optimization": {
                "connection_pooling": "Optimized pool sizes per database",
                "query_caching": "Multi-tier caching strategy", 
                "batch_operations": "Bulk operations where possible"
            }
        }
        
        # Codebase Ingestion Pipeline Configuration
        ingestion_pipelines = {
            "file_processors": {
                "python_files": "AST parsing, dependency extraction, embedding generation",
                "markdown_files": "Documentation parsing and embedding",
                "json_files": "Schema validation and structured storage",
                "yaml_files": "Configuration parsing and validation",
                "sql_files": "Schema extraction and query analysis"
            },
            "analysis_types": [
                "Static code analysis (complexity, dependencies)",
                "Semantic analysis (function purpose, data flow)",
                "Quality metrics (test coverage, documentation)",
                "Security analysis (vulnerability scanning)"
            ],
            "storage_strategy": {
                "raw_files": "PostgreSQL with compression",
                "parsed_structure": "Neo4j as graph relationships",
                "embeddings": "Qdrant for similarity search",
                "active_context": "Redis for immediate access"
            }
        }
        
        # Create memory architecture
        memory_architecture = MemoryArchitecture(
            short_term_config=short_term_config,
            medium_term_config=medium_term_config,
            long_term_config=long_term_config,
            pattern_config=pattern_config,
            coordination_layer=coordination_layer,
            ingestion_pipelines=ingestion_pipelines
        )
        
        self.memory_architecture = memory_architecture
        logger.info("✅ Memory architecture design complete")
        
        return memory_architecture

    def create_context_document(self) -> str:
        """
        📋 STEP 3: Context Document Creation (Required for EXTENSIVE tasks)
        
        Creates comprehensive context document following AI Task Orchestrator Guide
        for tasks that may exceed context windows.
        """
        logger.info("📋 Creating context document for EXTENSIVE complexity task")
        
        if not self.task_analysis or not self.memory_architecture:
            raise ValueError("Task analysis and memory architecture must be completed first")
        
        context_doc = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.start_time.isoformat(),
                "complexity": self.task_analysis.complexity.value,
                "ai_orchestrator_compliance": True
            },
            "task_overview": {
                "description": "Comprehensive multi-database memory management system",
                "estimated_effort": f"{self.task_analysis.estimated_hours} hours",
                "estimated_scope": f"{self.task_analysis.estimated_lines} lines across {self.task_analysis.estimated_files} files"
            },
            "requirements_summary": self.task_analysis.requirements,
            "architecture_overview": {
                "memory_tiers": {
                    "short_term": "Redis - Context window and real-time caching",
                    "medium_term": "Neo4j - Structured knowledge and relationships", 
                    "long_term": "PostgreSQL - Persistent storage and historical data",
                    "pattern_matching": "Qdrant - Vector embeddings and similarity search"
                },
                "coordination_strategy": "Intelligent routing with eventually consistent updates"
            },
            "execution_plan": self.task_analysis.execution_plan,
            "validation_criteria": self.task_analysis.validation_criteria,
            "risk_mitigation": {
                risk: f"Monitor and address during implementation"
                for risk in self.task_analysis.risks
            }
        }
        
        # Save context document
        context_file = f"memory_orchestrator_context_{self.session_id}.json"
        context_path = Path(__file__).parent / context_file
        
        with open(context_path, 'w') as f:
            json.dump(context_doc, f, indent=2)
        
        self.context_documents['main'] = str(context_path)
        logger.info(f"✅ Context document created: {context_path}")
        
        return str(context_path)

    def validate_dependencies(self) -> Dict[str, Any]:
        """
        ✅ Validate system dependencies and prerequisites
        """
        logger.info("🔍 Validating system dependencies and prerequisites")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {},
            "issues": [],
            "recommendations": []
        }
        
        # Check database services
        database_checks = {
            "neo4j": self._check_neo4j_connection(),
            "postgresql": self._check_postgresql_connection(),
            "qdrant": self._check_qdrant_connection(), 
            "redis": self._check_redis_connection()
        }
        
        validation_results["checks"]["databases"] = database_checks
        
        # Check Python libraries
        library_checks = {}
        required_libraries = ["neo4j", "psycopg2", "qdrant-client", "redis", "click"]
        
        for lib in required_libraries:
            try:
                __import__(lib.replace('-', '_'))
                library_checks[lib] = "available"
            except ImportError:
                library_checks[lib] = "missing"
                validation_results["issues"].append(f"Missing required library: {lib}")
        
        validation_results["checks"]["libraries"] = library_checks
        
        # Check file system permissions
        fs_checks = self._check_filesystem_permissions()
        validation_results["checks"]["filesystem"] = fs_checks
        
        # Determine overall status
        if validation_results["issues"]:
            validation_results["overall_status"] = "issues_found"
        else:
            validation_results["overall_status"] = "ready"
        
        self.validation_results["dependencies"] = validation_results
        logger.info(f"✅ Dependency validation complete: {validation_results['overall_status']}")
        
        return validation_results

    def _check_neo4j_connection(self) -> str:
        """Check Neo4j database connection"""
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
            with driver.session() as session:
                result = session.run("RETURN 1")
                record = result.single()
                if record:
                    return "connected"
            return "connection_failed"
        except Exception as e:
            return f"error: {str(e)}"

    def _check_postgresql_connection(self) -> str:
        """Check PostgreSQL database connection"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="plc_metadata",
                user="plc_user",
                password="password"
            )
            conn.close()
            return "connected"
        except Exception as e:
            return f"error: {str(e)}"

    def _check_qdrant_connection(self) -> str:
        """Check Qdrant vector database connection"""
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(host="localhost", port=6333)
            info = client.get_cluster_info()
            return "connected"
        except Exception as e:
            return f"error: {str(e)}"

    def _check_redis_connection(self) -> str:
        """Check Redis connection"""
        try:
            import redis
            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
            return "connected"
        except Exception as e:
            return f"error: {str(e)}"

    def _check_filesystem_permissions(self) -> Dict[str, str]:
        """Check filesystem permissions for required directories"""
        checks = {}
        
        # Check write permissions for logs, cache, etc.
        test_dirs = [
            Path(__file__).parent,
            Path(__file__).parent.parent.parent / "logs",
            Path(__file__).parent.parent.parent / "cache"
        ]
        
        for test_dir in test_dirs:
            try:
                test_dir.mkdir(exist_ok=True)
                test_file = test_dir / f"permission_test_{int(time.time())}"
                test_file.touch()
                test_file.unlink()
                checks[str(test_dir)] = "writable"
            except Exception as e:
                checks[str(test_dir)] = f"permission_error: {str(e)}"
        
        return checks

    def get_session_summary(self) -> Dict[str, Any]:
        """
        📊 Get comprehensive session summary following AI Task Orchestrator Guide
        """
        duration = datetime.now() - self.start_time
        
        summary = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "ai_orchestrator_compliance": True,
            "task_complexity": self.task_analysis.complexity.value if self.task_analysis else "unknown",
            "phases_completed": [],
            "context_documents_created": len(self.context_documents),
            "validation_results": self.validation_results,
            "memory_architecture_designed": self.memory_architecture is not None,
            "recommendations": [
                "Follow systematic implementation approach",
                "Validate each phase before proceeding",
                "Monitor performance during implementation",
                "Maintain comprehensive documentation"
            ]
        }
        
        return summary

def main():
    """
    🚀 Main execution function demonstrating AI Task Orchestrator methodology
    """
    print("🤖 Comprehensive Memory Management System - AI Task Orchestrator")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = ComprehensiveMemoryOrchestrator()
    
    try:
        # Step 1: Comprehensive task analysis
        print("\n🔍 STEP 1: AI Task Orchestrator Analysis")
        task_description = """
        Create a comprehensive memory management system that ingests the entire codebase 
        into multiple databases to maximize AI memory capacity:
        - Neo4j (GraphDB) for medium-term structured memory
        - PostgreSQL for long-term persistent storage  
        - Redis for short-term context window management
        - Qdrant for vector pattern matching and AI fine-tuning
        - Intelligent memory coordination layer
        - CLI interface for repeatable operations
        """
        
        analysis = orchestrator.analyze_task(task_description)
        print(f"✅ Task classified as {analysis.complexity.value}")
        print(f"📊 Estimated effort: {analysis.estimated_hours} hours, {analysis.estimated_files} files")
        
        # Step 2: Memory architecture design
        print("\n🏗️ STEP 2: Memory Architecture Design")
        architecture = orchestrator.design_memory_architecture()
        print("✅ Multi-database memory architecture designed")
        
        # Step 3: Context document creation (required for EXTENSIVE tasks)
        print("\n📋 STEP 3: Context Document Creation")
        context_doc = orchestrator.create_context_document()
        print(f"✅ Context document created: {context_doc}")
        
        # Step 4: Dependency validation
        print("\n🔍 STEP 4: Dependency Validation")
        validation = orchestrator.validate_dependencies()
        print(f"✅ Dependency validation: {validation['overall_status']}")
        
        if validation["issues"]:
            print("⚠️ Issues found:")
            for issue in validation["issues"]:
                print(f"  - {issue}")
        
        # Step 5: Implementation guidance
        print("\n📋 STEP 5: Implementation Guidance")
        print("Following AI Task Orchestrator methodology for EXTENSIVE complexity:")
        
        for step in analysis.execution_plan:
            print(f"\nStep {step['step']}: {step['action']}")
            print(f"  📝 {step['description']}")
            print(f"  📦 Deliverables: {', '.join(step['deliverables'])}")
            print(f"  ⏱️ Estimated time: {step['estimated_hours']} hours")
            print(f"  ✅ Validation: {step['validation']}")
        
        # Step 6: Session summary
        print("\n📊 STEP 6: Session Summary")
        summary = orchestrator.get_session_summary()
        print(f"✅ Session {summary['session_id']} completed")
        print(f"⏱️ Duration: {summary['duration_seconds']:.1f} seconds")
        print(f"🏗️ Architecture designed: {summary['memory_architecture_designed']}")
        print(f"📋 Context documents: {summary['context_documents_created']}")
        
        # Next steps
        print("\n🎯 NEXT STEPS:")
        print("1. Address any dependency issues identified")
        print("2. Begin implementation following the 6-step execution plan")
        print("3. Validate each phase before proceeding to the next")
        print("4. Use the context document for complex implementation details")
        print("5. Follow AI Task Orchestrator methodology throughout")
        
        # Save comprehensive results
        results_file = f"memory_orchestrator_results_{orchestrator.session_id}.json"
        results_path = Path(__file__).parent / results_file
        
        results = {
            "task_analysis": asdict(analysis),
            "memory_architecture": asdict(architecture),
            "dependency_validation": validation,
            "session_summary": summary,
            "ai_orchestrator_compliance": True
        }
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Complete results saved to: {results_path}")
        
    except Exception as e:
        logger.error(f"Error during orchestration: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 