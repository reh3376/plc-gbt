#!/usr/bin/env python3
"""
Python Packaging Documentation Ingestor
Ingests scraped Python packaging documentation into Neo4j knowledge graph for long-term memory.

This script creates structured nodes and relationships for the Python packaging documentation
scraped from packaging.python.org to provide persistent knowledge for AI agents.
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

import structlog
from neo4j import GraphDatabase

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class PythonPackagingDocIngestor:
    """Ingest Python packaging documentation into Neo4j knowledge graph."""

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = None
    ):
        """Initialize the documentation ingestor."""
        if not neo4j_password:
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'plc-gpt-2024')

        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        # Python packaging documentation structure
        self.documentation_data = self._prepare_documentation_structure()

    def close(self):
        """Close connections."""
        if self.neo4j_driver:
            self.neo4j_driver.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def _prepare_documentation_structure(self) -> Dict[str, Any]:
        """Prepare the structured documentation data for ingestion."""
        return {
            "main_collection": {
                "id": str(uuid.uuid4()),
                "title": "Python Packaging User Guide",
                "source": "packaging.python.org",
                "base_url": "https://packaging.python.org/en/latest/",
                "category": "Technical Documentation",
                "language": "Python",
                "last_updated": "2025-01-25",
                "ingestion_date": datetime.now().isoformat(),
                "description": "Official Python Packaging Authority documentation for building and publishing Python packages"
            },
            "sections": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Building and Publishing",
                    "url": "https://packaging.python.org/en/latest/guides/section-build-and-publish/",
                    "section_type": "Guide Collection",
                    "description": "Comprehensive guides for packaging and distributing Python projects",
                    "key_topics": ["pyproject.toml", "packaging", "distributing", "binary extensions", "command-line tools"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Packaging and distributing projects",
                    "url": "https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/",
                    "section_type": "Detailed Guide",
                    "description": "Step-by-step guide for packaging and distributing Python projects with setuptools",
                    "key_topics": ["setup.py", "wheel", "PyPI", "twine", "source distributions", "binary distributions"],
                    "workflow_steps": [
                        "Install build tools (pip install build twine)",
                        "Configure project (pyproject.toml or setup.py)",
                        "Build packages (python -m build)",
                        "Validate packages (twine check dist/*)",
                        "Upload to PyPI (twine upload dist/*)"
                    ]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Overview of Python Packaging",
                    "url": "https://packaging.python.org/en/latest/overview/",
                    "section_type": "Overview",
                    "description": "High-level overview of Python packaging approaches and decision tree",
                    "key_topics": ["deployment", "libraries", "applications", "frameworks", "distribution formats"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Glossary",
                    "url": "https://packaging.python.org/en/latest/glossary/",
                    "section_type": "Reference",
                    "description": "Comprehensive glossary of Python packaging terminology",
                    "key_topics": ["distribution package", "wheel", "sdist", "build backend", "PyPI"]
                }
            ],
            "best_practices": [
                {
                    "id": str(uuid.uuid4()),
                    "practice": "Use pyproject.toml for modern packaging",
                    "description": "Modern Python packages should use pyproject.toml instead of setup.py",
                    "category": "Configuration",
                    "importance": "High"
                },
                {
                    "id": str(uuid.uuid4()),
                    "practice": "Build with python -m build",
                    "description": "Use the build package for creating distributions: python -m build",
                    "category": "Build Process",
                    "importance": "High"
                },
                {
                    "id": str(uuid.uuid4()),
                    "practice": "Validate with twine check",
                    "description": "Always validate packages before upload: twine check dist/*",
                    "category": "Quality Assurance",
                    "importance": "High"
                },
                {
                    "id": str(uuid.uuid4()),
                    "practice": "Create both wheel and sdist",
                    "description": "Publish both wheel (.whl) and source distribution (.tar.gz) for compatibility",
                    "category": "Distribution",
                    "importance": "Medium"
                }
            ],
            "tools": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "build",
                    "purpose": "Modern build frontend for creating source distributions and wheels",
                    "command": "python -m build",
                    "install": "pip install build"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "twine",
                    "purpose": "Utility for uploading packages to PyPI and validating distributions",
                    "command": "twine upload dist/*",
                    "install": "pip install twine"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "setuptools",
                    "purpose": "Build backend for Python packages",
                    "command": "Used automatically by build",
                    "install": "pip install setuptools"
                }
            ]
        }

    def ingest_documentation(self) -> Dict[str, Any]:
        """Ingest Python packaging documentation into Neo4j."""
        logger.info("Starting Python packaging documentation ingestion")

        results = {
            'status': 'started',
            'main_collection_id': None,
            'nodes_created': 0,
            'relationships_created': 0,
            'sections_processed': 0,
            'practices_processed': 0,
            'tools_processed': 0,
            'errors': []
        }

        try:
            with self.neo4j_driver.session() as session:

                # Create main documentation collection node
                main_id = self._create_main_collection_node(session)
                results['main_collection_id'] = main_id
                results['nodes_created'] += 1

                # Create section nodes
                for section in self.documentation_data['sections']:
                    self._create_section_node(session, section, main_id)
                    results['nodes_created'] += 1
                    results['relationships_created'] += 1
                    results['sections_processed'] += 1

                # Create best practice nodes
                for practice in self.documentation_data['best_practices']:
                    self._create_best_practice_node(session, practice, main_id)
                    results['nodes_created'] += 1
                    results['relationships_created'] += 1
                    results['practices_processed'] += 1

                # Create tool nodes
                for tool in self.documentation_data['tools']:
                    self._create_tool_node(session, tool, main_id)
                    results['nodes_created'] += 1
                    results['relationships_created'] += 1
                    results['tools_processed'] += 1

                # Create relationships between related concepts
                self._create_concept_relationships(session)
                results['relationships_created'] += 5  # Estimated additional relationships

                results['status'] = 'completed'
                logger.info("Python packaging documentation ingestion completed successfully", **results)

        except Exception as e:
            results['status'] = 'failed'
            results['errors'].append(str(e))
            logger.error("Python packaging documentation ingestion failed", error=str(e))
            raise

        return results

    def _create_main_collection_node(self, session) -> str:
        """Create the main documentation collection node."""
        main_data = self.documentation_data['main_collection']

        result = session.run("""
            MERGE (doc:Documentation {id: $id})
            SET doc += $properties
            SET doc.node_type = 'PythonPackagingGuide'
            RETURN doc.id as id
        """,
        id=main_data['id'],
        properties=main_data
        )

        doc_id = result.single()['id']
        logger.info(f"Created main documentation node: {doc_id}")
        return doc_id

    def _create_section_node(self, session, section_data: Dict, main_id: str) -> str:
        """Create a documentation section node."""

        result = session.run("""
            MERGE (section:DocumentationSection {id: $id})
            SET section += $properties
            WITH section
            MATCH (main:Documentation {id: $main_id})
            MERGE (main)-[:CONTAINS_SECTION]->(section)
            RETURN section.id as id
        """,
        id=section_data['id'],
        properties=section_data,
        main_id=main_id
        )

        section_id = result.single()['id']
        logger.info(f"Created documentation section: {section_data['title']}")
        return section_id

    def _create_best_practice_node(self, session, practice_data: Dict, main_id: str) -> str:
        """Create a best practice node."""

        result = session.run("""
            MERGE (practice:BestPractice {id: $id})
            SET practice += $properties
            WITH practice
            MATCH (main:Documentation {id: $main_id})
            MERGE (main)-[:DEFINES_PRACTICE]->(practice)
            RETURN practice.id as id
        """,
        id=practice_data['id'],
        properties=practice_data,
        main_id=main_id
        )

        practice_id = result.single()['id']
        logger.info(f"Created best practice: {practice_data['practice']}")
        return practice_id

    def _create_tool_node(self, session, tool_data: Dict, main_id: str) -> str:
        """Create a tool node."""

        result = session.run("""
            MERGE (tool:PackagingTool {id: $id})
            SET tool += $properties
            WITH tool
            MATCH (main:Documentation {id: $main_id})
            MERGE (main)-[:DESCRIBES_TOOL]->(tool)
            RETURN tool.id as id
        """,
        id=tool_data['id'],
        properties=tool_data,
        main_id=main_id
        )

        tool_id = result.single()['id']
        logger.info(f"Created packaging tool: {tool_data['name']}")
        return tool_id

    def _create_concept_relationships(self, session):
        """Create relationships between related concepts."""

        # Link tools to practices that use them
        session.run("""
            MATCH (tool:PackagingTool {name: 'build'})
            MATCH (practice:BestPractice {practice: 'Build with python -m build'})
            MERGE (practice)-[:USES_TOOL]->(tool)
        """)

        session.run("""
            MATCH (tool:PackagingTool {name: 'twine'})
            MATCH (practice:BestPractice {practice: 'Validate with twine check'})
            MERGE (practice)-[:USES_TOOL]->(tool)
        """)

        # Link sections to practices they contain
        session.run("""
            MATCH (section:DocumentationSection {title: 'Packaging and distributing projects'})
            MATCH (practice:BestPractice)
            WHERE practice.category IN ['Build Process', 'Quality Assurance', 'Distribution']
            MERGE (section)-[:EXPLAINS_PRACTICE]->(practice)
        """)

        logger.info("Created concept relationships")


def main():
    """Main execution function."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed, using environment variables directly")

    # Configuration
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'plc-gpt-2024')

    logger.info("Starting Python packaging documentation ingestion")

    try:
        with PythonPackagingDocIngestor(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password
        ) as ingestor:

            results = ingestor.ingest_documentation()

            print("\n" + "="*60)
            print("🐍 PYTHON PACKAGING DOCUMENTATION INGESTION COMPLETE")
            print("="*60)
            print(f"📊 Status: {results['status'].upper()}")
            print(f"📁 Main Collection ID: {results['main_collection_id']}")
            print(f"🔢 Nodes Created: {results['nodes_created']}")
            print(f"🔗 Relationships Created: {results['relationships_created']}")
            print(f"📚 Sections Processed: {results['sections_processed']}")
            print(f"✅ Best Practices: {results['practices_processed']}")
            print(f"🛠️ Tools Documented: {results['tools_processed']}")

            if results['errors']:
                print(f"❌ Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"   • {error}")
            else:
                print("✅ No errors encountered")

            print("\n📈 Knowledge Graph Enhanced:")
            print("   • Python packaging best practices")
            print("   • Modern packaging workflow")
            print("   • Tool usage and commands")
            print("   • Official documentation structure")
            print("   • Available for AI agent queries")

            print("\n🔍 Query examples:")
            print("   • MATCH (doc:Documentation {title: 'Python Packaging User Guide'}) RETURN doc")
            print("   • MATCH (practice:BestPractice) RETURN practice.practice, practice.importance")
            print("   • MATCH (tool:PackagingTool) RETURN tool.name, tool.command")

    except Exception as e:
        logger.error("Python packaging documentation ingestion failed", error=str(e))
        print(f"\n❌ Ingestion failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
