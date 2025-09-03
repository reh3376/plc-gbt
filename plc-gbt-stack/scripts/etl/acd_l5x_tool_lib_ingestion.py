#!/usr/bin/env python3
"""
ACD-L5X Tool Library Repository Ingestion Script
Specialized ingestion for the acd-l5x-tool-lib repository context
Version: 1.0.0

This script ingests comprehensive context from the acd-l5x-tool-lib repository
into the Neo4j knowledge graph, including repository metadata, code structure,
capabilities, and relationships to the main PLC-GPT project.
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

import structlog
from embedding_generator import EmbeddingGenerator
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Import existing processors

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


class ACDToolLibIngestion:
    """Specialized ingestion for acd-l5x-tool-lib repository."""

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "plc-gpt-2024",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        openai_api_key: Optional[str] = None,
        github_token: Optional[str] = None
    ):
        """Initialize the ingestion system."""
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        self.qdrant_client = QdrantClient(
            host=qdrant_host,
            port=qdrant_port
        )

        self.embedding_generator = EmbeddingGenerator(api_key=openai_api_key)

        # Session for HTTP requests
        self.session = requests.Session()
        if github_token:
            self.session.headers.update({'Authorization': f'token {github_token}'})

        # Repository context data
        self.repo_context = self._build_comprehensive_context()

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

    def _build_comprehensive_context(self) -> Dict[str, Any]:
        """Build comprehensive context for the acd-l5x-tool-lib repository."""
        return {
            'repository': {
                'name': 'acd-l5x-tool-lib',
                'full_name': 'reh3376/acd-l5x-tool-lib',
                'owner': 'reh3376',
                'url': 'https://github.com/reh3376/acd-l5x-tool-lib',
                'description': 'This library allows for the conversion of .acd files to .l5x and .l5x back to .acd with validation testing. This will allow an enterprise to use standard github repos to manage versioning and development in a manner similar to more standard IT type CI/CD.',
                'language': 'Python',
                'license': 'MIT',
                'stars': 13,
                'forks': 2,
                'topics': ['plc', 'automation', 'l5x', 'acd', 'rockwell', 'allen-bradley', 'industrial-automation'],
                'is_template': True,
                'plc_related': True,
                'category': 'PLC File Format Converter'
            },
            'capabilities': {
                'file_formats': {
                    'acd': {
                        'description': 'Rockwell Automation Archive files',
                        'operations': ['read', 'parse', 'convert_to_l5x'],
                        'validation': True
                    },
                    'l5x': {
                        'description': 'Logix Designer Export format',
                        'operations': ['read', 'parse', 'convert_to_acd', 'save'],
                        'validation': True
                    }
                },
                'supported_controllers': [
                    {
                        'name': 'ControlLogix',
                        'programs': 1000,
                        'tags': 250000,
                        'motion': True,
                        'safety': False,
                        'io_modules': 128
                    },
                    {
                        'name': 'CompactLogix',
                        'programs': 100,
                        'tags': 32000,
                        'motion': True,
                        'safety': False,
                        'io_modules': 30
                    },
                    {
                        'name': 'GuardLogix',
                        'programs': 1000,
                        'tags': 250000,
                        'motion': True,
                        'safety': True,
                        'io_modules': 128
                    }
                ],
                'validation_features': [
                    'Controller capability validation',
                    'Data consistency checks',
                    'Motion instruction validation',
                    'Safety instruction validation',
                    'Naming convention validation',
                    'Component dependency analysis'
                ],
                'integration_features': [
                    'Batch processing',
                    'CI/CD pipeline integration',
                    'Version control compatibility',
                    'Docker containerization',
                    'API access via CLI'
                ]
            },
            'code_structure': {
                'src/plc_format_converter/': {
                    '__init__.py': 'Package initialization and main exports',
                    'cli.py': 'Command-line interface for format conversion',
                    'core/': {
                        'converter.py': 'Main converter logic and orchestration',
                        'models.py': 'Pydantic data models for PLC components'
                    },
                    'formats/': {
                        '__init__.py': 'Format handler exports',
                        'acd_handler.py': 'ACD file format handler and parser',
                        'l5x_handler.py': 'L5X file format handler and parser'
                    },
                    'utils/': {
                        '__init__.py': 'Utility function exports',
                        'validation.py': 'Validation framework and rules engine'
                    }
                },
                'tests/': {
                    'test_data/': 'Sample PLC files for testing',
                    'test_library_integration.py': 'Integration test suite'
                },
                'docs/': {
                    'plc-file-conversion-howto.md': 'Comprehensive usage guide'
                }
            },
            'usage_patterns': {
                'basic_conversion': {
                    'acd_to_l5x': 'handler = ACDHandler(); project = handler.load("file.acd"); L5XHandler().save(project, "output.l5x")',
                    'l5x_to_acd': 'handler = L5XHandler(); project = handler.load("file.l5x"); ACDHandler().save(project, "output.acd")'
                },
                'validation': {
                    'comprehensive': 'validator = PLCValidator(); result = validator.validate_project(project, options)',
                    'custom_rules': 'class CustomValidator(PLCValidator): def validate_naming_conventions(self, project, result): ...'
                },
                'batch_processing': {
                    'multiple_files': 'def batch_convert_l5x_files(input_dir, output_dir): ...',
                    'validation_pipeline': 'for l5x_file in Path(input_dir).glob("*.L5X"): ...'
                }
            },
            'relationships': {
                'plc_gpt_integration': {
                    'role': 'Core file format conversion library',
                    'dependency_type': 'External PyPI package',
                    'integration_points': [
                        'ETL pipeline for L5X file processing',
                        'Format validation in knowledge graph ingestion',
                        'PLC component extraction and analysis',
                        'CI/CD automation for PLC development workflows'
                    ]
                },
                'ecosystem_position': {
                    'category': 'PLC Development Tools',
                    'related_libraries': [
                        'hutcheb/acd - Core ACD parsing',
                        'jvalenzuela/l5x - L5X XML processing',
                        'dmroeder/pylogix - PLC communication',
                        'ottowayi/pycomm3 - Communication protocols'
                    ],
                    'enterprise_value': [
                        'Version control for PLC programs',
                        'Automated testing and validation',
                        'CI/CD pipeline integration',
                        'Format standardization across teams'
                    ]
                }
            },
            'technical_specifications': {
                'python_version': '3.8+',
                'dependencies': [
                    'pydantic - Data validation and settings management',
                    'lxml - XML processing for L5X files',
                    'click - CLI framework',
                    'pathlib - Path handling',
                    'typing - Type hints and annotations'
                ],
                'performance': {
                    'file_size_limits': 'Up to 100MB L5X files tested',
                    'processing_speed': 'Typical conversion: 1-5 seconds per file',
                    'memory_usage': 'Peak usage: 2-3x file size during processing'
                },
                'deployment': {
                    'docker_support': True,
                    'pypi_package': True,
                    'github_actions': True,
                    'container_registry': 'GitHub Container Registry'
                }
            }
        }

    def ingest_repository(self) -> Dict[str, Any]:
        """Ingest the acd-l5x-tool-lib repository into the knowledge graph."""
        logger.info("Starting acd-l5x-tool-lib repository ingestion")

        results = {
            'status': 'started',
            'repository_id': None,
            'nodes_created': 0,
            'relationships_created': 0,
            'embeddings_created': 0,
            'components_processed': 0,
            'errors': []
        }

        try:
            # Step 1: Create main repository node
            repo_id = self._create_repository_node()
            results['repository_id'] = repo_id
            results['nodes_created'] += 1

            # Step 2: Create capability nodes
            capability_results = self._create_capability_nodes(repo_id)
            results['nodes_created'] += capability_results['nodes_created']
            results['relationships_created'] += capability_results['relationships_created']

            # Step 3: Create code structure nodes
            structure_results = self._create_code_structure_nodes(repo_id)
            results['nodes_created'] += structure_results['nodes_created']
            results['relationships_created'] += structure_results['relationships_created']

            # Step 4: Create controller support nodes
            controller_results = self._create_controller_support_nodes(repo_id)
            results['nodes_created'] += controller_results['nodes_created']
            results['relationships_created'] += controller_results['relationships_created']

            # Step 5: Create integration relationship with PLC-GPT
            integration_results = self._create_plc_gpt_integration(repo_id)
            results['relationships_created'] += integration_results['relationships_created']

            # Step 6: Generate embeddings
            embedding_results = self._generate_comprehensive_embeddings(repo_id)
            results['embeddings_created'] = embedding_results['embeddings_created']

            # Step 7: Create ecosystem relationships
            ecosystem_results = self._create_ecosystem_relationships(repo_id)
            results['relationships_created'] += ecosystem_results['relationships_created']

            results['status'] = 'completed'
            results['components_processed'] = (
                len(self.repo_context['capabilities']['file_formats']) +
                len(self.repo_context['capabilities']['supported_controllers']) +
                len(self.repo_context['code_structure'])
            )

        except Exception as e:
            logger.error(f"Error during ingestion: {str(e)}")
            results['status'] = 'failed'
            results['errors'].append(str(e))

        return results

    def _create_repository_node(self) -> str:
        """Create the main GitHubRepo node."""
        repo_id = str(uuid.uuid4())
        repo_data = self.repo_context['repository']

        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (r:GitHubRepo {id: $id})
                SET r += $properties
                RETURN r
            """,
            id=repo_id,
            properties={
                'id': repo_id,
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'owner': repo_data['owner'],
                'description': repo_data['description'],
                'url': repo_data['url'],
                'language': repo_data['language'],
                'license': repo_data['license'],
                'stars': repo_data['stars'],
                'forks': repo_data['forks'],
                'topics': repo_data['topics'],
                'is_template': repo_data['is_template'],
                'plc_related': repo_data['plc_related'],
                'category': repo_data['category'],
                'processed_date': datetime.now().isoformat(),
                'ingestion_source': 'specialized_acd_l5x_ingestion'
            })

        logger.info(f"Created GitHubRepo node: {repo_id}")
        return repo_id

    def _create_capability_nodes(self, repo_id: str) -> Dict[str, int]:
        """Create nodes for repository capabilities."""
        stats = {'nodes_created': 0, 'relationships_created': 0}

        with self.neo4j_driver.session() as session:
            # Create file format capability nodes
            for format_name, format_data in self.repo_context['capabilities']['file_formats'].items():
                capability_id = str(uuid.uuid4())

                session.run("""
                    CREATE (c:Capability {
                        id: $id,
                        name: $name,
                        type: 'FileFormat',
                        description: $description,
                        operations: $operations,
                        validation_supported: $validation,
                        created_date: datetime($created_date)
                    })
                    WITH c
                    MATCH (r:GitHubRepo {id: $repo_id})
                    CREATE (r)-[:HAS_CAPABILITY]->(c)
                    RETURN c
                """,
                id=capability_id,
                name=format_name.upper(),
                description=format_data['description'],
                operations=format_data['operations'],
                validation=format_data['validation'],
                created_date=datetime.now().isoformat(),
                repo_id=repo_id
                )

                stats['nodes_created'] += 1
                stats['relationships_created'] += 1

            # Create validation capability nodes
            for validation_feature in self.repo_context['capabilities']['validation_features']:
                capability_id = str(uuid.uuid4())

                session.run("""
                    CREATE (c:Capability {
                        id: $id,
                        name: $name,
                        type: 'Validation',
                        description: $description,
                        created_date: datetime($created_date)
                    })
                    WITH c
                    MATCH (r:GitHubRepo {id: $repo_id})
                    CREATE (r)-[:HAS_CAPABILITY]->(c)
                    RETURN c
                """,
                id=capability_id,
                name=validation_feature.replace(' ', '_').upper(),
                description=validation_feature,
                created_date=datetime.now().isoformat(),
                repo_id=repo_id
                )

                stats['nodes_created'] += 1
                stats['relationships_created'] += 1

        return stats

    def _create_code_structure_nodes(self, repo_id: str) -> Dict[str, int]:
        """Create nodes for code structure components."""
        stats = {'nodes_created': 0, 'relationships_created': 0}

        def create_module_nodes(path_dict: Dict, parent_path: str = "", parent_id: str = None):
            for name, content in path_dict.items():
                if isinstance(content, dict):
                    # Directory
                    module_id = str(uuid.uuid4())
                    current_path = f"{parent_path}/{name}" if parent_path else name

                    with self.neo4j_driver.session() as session:
                        session.run("""
                            CREATE (m:CodeModule {
                                id: $id,
                                name: $name,
                                path: $path,
                                type: 'Directory',
                                created_date: datetime($created_date)
                            })
                            WITH m
                            MATCH (r:GitHubRepo {id: $repo_id})
                            CREATE (r)-[:CONTAINS_MODULE]->(m)
                            RETURN m
                        """,
                        id=module_id,
                        name=name,
                        path=current_path,
                        created_date=datetime.now().isoformat(),
                        repo_id=repo_id
                        )

                    stats['nodes_created'] += 1
                    stats['relationships_created'] += 1

                    # Create parent-child relationship if exists
                    if parent_id:
                        with self.neo4j_driver.session() as session:
                            session.run("""
                                MATCH (parent:CodeModule {id: $parent_id})
                                MATCH (child:CodeModule {id: $child_id})
                                CREATE (parent)-[:CONTAINS]->(child)
                                RETURN parent, child
                            """,
                            parent_id=parent_id,
                            child_id=module_id
                            )

                        stats['relationships_created'] += 1

                    # Recursively process subdirectories
                    create_module_nodes(content, current_path, module_id)

                else:
                    # File
                    module_id = str(uuid.uuid4())
                    current_path = f"{parent_path}/{name}" if parent_path else name

                    with self.neo4j_driver.session() as session:
                        session.run("""
                            CREATE (m:CodeModule {
                                id: $id,
                                name: $name,
                                path: $path,
                                type: 'File',
                                description: $description,
                                created_date: datetime($created_date)
                            })
                            WITH m
                            MATCH (r:GitHubRepo {id: $repo_id})
                            CREATE (r)-[:CONTAINS_MODULE]->(m)
                            RETURN m
                        """,
                        id=module_id,
                        name=name,
                        path=current_path,
                        description=content,
                        created_date=datetime.now().isoformat(),
                        repo_id=repo_id
                        )

                    stats['nodes_created'] += 1
                    stats['relationships_created'] += 1

                    # Create parent-child relationship if exists
                    if parent_id:
                        with self.neo4j_driver.session() as session:
                            session.run("""
                                MATCH (parent:CodeModule {id: $parent_id})
                                MATCH (child:CodeModule {id: $child_id})
                                CREATE (parent)-[:CONTAINS]->(child)
                                RETURN parent, child
                            """,
                            parent_id=parent_id,
                            child_id=module_id
                            )

                        stats['relationships_created'] += 1

        create_module_nodes(self.repo_context['code_structure'])
        return stats

    def _create_controller_support_nodes(self, repo_id: str) -> Dict[str, int]:
        """Create nodes for supported PLC controllers."""
        stats = {'nodes_created': 0, 'relationships_created': 0}

        with self.neo4j_driver.session() as session:
            for controller in self.repo_context['capabilities']['supported_controllers']:
                controller_id = str(uuid.uuid4())

                session.run("""
                    CREATE (c:PLCController {
                        id: $id,
                        name: $name,
                        max_programs: $programs,
                        max_tags: $tags,
                        motion_support: $motion,
                        safety_support: $safety,
                        max_io_modules: $io_modules,
                        created_date: datetime($created_date)
                    })
                    WITH c
                    MATCH (r:GitHubRepo {id: $repo_id})
                    CREATE (r)-[:SUPPORTS_CONTROLLER]->(c)
                    RETURN c
                """,
                id=controller_id,
                name=controller['name'],
                programs=controller['programs'],
                tags=controller['tags'],
                motion=controller['motion'],
                safety=controller['safety'],
                io_modules=controller['io_modules'],
                created_date=datetime.now().isoformat(),
                repo_id=repo_id
                )

                stats['nodes_created'] += 1
                stats['relationships_created'] += 1

        return stats

    def _create_plc_gpt_integration(self, repo_id: str) -> Dict[str, int]:
        """Create relationship with PLC-GPT project."""
        stats = {'relationships_created': 0}

        with self.neo4j_driver.session() as session:
            # Try to find existing PLC-GPT project node
            result = session.run("""
                MATCH (p:PLCProgram)
                WHERE p.name CONTAINS 'PLC-GPT' OR p.project_name CONTAINS 'PLC-GPT'
                RETURN p
                LIMIT 1
            """)

            plc_gpt_node = result.single()

            if plc_gpt_node:
                # Create integration relationship
                session.run("""
                    MATCH (r:GitHubRepo {id: $repo_id})
                    MATCH (p:PLCProgram {id: $plc_gpt_id})
                    CREATE (r)-[:INTEGRATES_WITH {
                        integration_type: 'External Library',
                        role: 'File Format Converter',
                        dependency_type: 'PyPI Package',
                        created_date: datetime($created_date)
                    }]->(p)
                    RETURN r, p
                """,
                repo_id=repo_id,
                plc_gpt_id=plc_gpt_node['p']['id'],
                created_date=datetime.now().isoformat()
                )

                stats['relationships_created'] += 1
            else:
                # Create a placeholder PLC-GPT project node
                plc_gpt_id = str(uuid.uuid4())

                session.run("""
                    CREATE (p:PLCProgram {
                        id: $id,
                        name: 'PLC-GPT',
                        project_name: 'PLC-GPT Enterprise System',
                        description: 'AI-powered PLC programming assistant with knowledge graph',
                        processor_type: 'Enterprise System',
                        created_date: datetime($created_date)
                    })
                    WITH p
                    MATCH (r:GitHubRepo {id: $repo_id})
                    CREATE (r)-[:INTEGRATES_WITH {
                        integration_type: 'External Library',
                        role: 'File Format Converter',
                        dependency_type: 'PyPI Package',
                        created_date: datetime($created_date)
                    }]->(p)
                    RETURN r, p
                """,
                id=plc_gpt_id,
                created_date=datetime.now().isoformat(),
                repo_id=repo_id
                )

                stats['relationships_created'] += 1

        return stats

    def _generate_comprehensive_embeddings(self, repo_id: str) -> Dict[str, int]:
        """Generate embeddings for repository content."""
        stats = {'embeddings_created': 0}

        try:
            # Repository overview embedding
            overview_text = f"""
            Repository: {self.repo_context['repository']['name']}
            Description: {self.repo_context['repository']['description']}
            Category: {self.repo_context['repository']['category']}
            Language: {self.repo_context['repository']['language']}
            Topics: {', '.join(self.repo_context['repository']['topics'])}
            """

            overview_embedding = self.embedding_generator.embed_text(overview_text)

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=overview_embedding,
                payload={
                    'content_type': 'GitHubRepo',
                    'repo_id': repo_id,
                    'text': overview_text[:1000],
                    'source': 'repository_overview',
                    'embedding_type': 'comprehensive_overview'
                }
            )

            self.qdrant_client.upsert(
                collection_name='document_chunks',
                points=[point]
            )

            stats['embeddings_created'] += 1

            # Capabilities embedding
            capabilities_text = f"""
            File Format Capabilities:
            {json.dumps(self.repo_context['capabilities']['file_formats'], indent=2)}

            Validation Features:
            {', '.join(self.repo_context['capabilities']['validation_features'])}

            Integration Features:
            {', '.join(self.repo_context['capabilities']['integration_features'])}
            """

            capabilities_embedding = self.embedding_generator.embed_text(capabilities_text)

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=capabilities_embedding,
                payload={
                    'content_type': 'GitHubRepo',
                    'repo_id': repo_id,
                    'text': capabilities_text[:1000],
                    'source': 'repository_capabilities',
                    'embedding_type': 'technical_capabilities'
                }
            )

            self.qdrant_client.upsert(
                collection_name='document_chunks',
                points=[point]
            )

            stats['embeddings_created'] += 1

            # Usage patterns embedding
            usage_text = f"""
            Usage Patterns and Examples:
            {json.dumps(self.repo_context['usage_patterns'], indent=2)}

            Technical Specifications:
            {json.dumps(self.repo_context['technical_specifications'], indent=2)}
            """

            usage_embedding = self.embedding_generator.embed_text(usage_text)

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=usage_embedding,
                payload={
                    'content_type': 'GitHubRepo',
                    'repo_id': repo_id,
                    'text': usage_text[:1000],
                    'source': 'repository_usage',
                    'embedding_type': 'usage_examples'
                }
            )

            self.qdrant_client.upsert(
                collection_name='document_chunks',
                points=[point]
            )

            stats['embeddings_created'] += 1

        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")

        return stats

    def _create_ecosystem_relationships(self, repo_id: str) -> Dict[str, int]:
        """Create relationships with ecosystem libraries."""
        stats = {'relationships_created': 0}

        ecosystem_libs = self.repo_context['relationships']['ecosystem_position']['related_libraries']

        with self.neo4j_driver.session() as session:
            for lib_description in ecosystem_libs:
                # Parse library name from description
                lib_name = lib_description.split(' - ')[0].split('/')[-1]

                # Try to find existing repository node
                result = session.run("""
                    MATCH (r:GitHubRepo)
                    WHERE r.name = $lib_name OR r.full_name CONTAINS $lib_name
                    RETURN r
                    LIMIT 1
                """, lib_name=lib_name)

                existing_repo = result.single()

                if existing_repo:
                    # Create ecosystem relationship
                    session.run("""
                        MATCH (r1:GitHubRepo {id: $repo_id})
                        MATCH (r2:GitHubRepo {id: $related_id})
                        CREATE (r1)-[:RELATED_TO {
                            relationship_type: 'Ecosystem Library',
                            description: $description,
                            created_date: datetime($created_date)
                        }]->(r2)
                        RETURN r1, r2
                    """,
                    repo_id=repo_id,
                    related_id=existing_repo['r']['id'],
                    description=lib_description,
                    created_date=datetime.now().isoformat()
                    )

                    stats['relationships_created'] += 1

        return stats


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
    openai_api_key = os.getenv('OPENAI_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')

    logger.info("Starting acd-l5x-tool-lib repository ingestion")

    try:
        with ACDToolLibIngestion(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            openai_api_key=openai_api_key,
            github_token=github_token
        ) as ingestion:

            results = ingestion.ingest_repository()

            # Print results
            print("\n" + "="*60)
            print("ACD-L5X TOOL LIB INGESTION RESULTS")
            print("="*60)
            print(f"Status: {results['status']}")
            print(f"Repository ID: {results['repository_id']}")
            print(f"Nodes Created: {results['nodes_created']}")
            print(f"Relationships Created: {results['relationships_created']}")
            print(f"Embeddings Created: {results['embeddings_created']}")
            print(f"Components Processed: {results['components_processed']}")

            if results['status'] == 'completed':
                print("\n✅ SUCCESS: acd-l5x-tool-lib repository has been successfully ingested!")
                print("The knowledge graph now contains comprehensive context about:")
                print("  • Repository metadata and capabilities")
                print("  • File format conversion features")
                print("  • Supported PLC controllers")
                print("  • Code structure and modules")
                print("  • Integration with PLC-GPT ecosystem")
                print("  • Usage patterns and technical specifications")
                print("\nYou can now query this information through the knowledge graph interface.")
            else:
                print(f"\n❌ FAILED: {len(results['errors'])} errors occurred")
                for error in results['errors']:
                    print(f"  - {error}")

    except Exception as e:
        logger.error(f"Fatal error during ingestion: {str(e)}")
        print(f"\n❌ FATAL ERROR: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
