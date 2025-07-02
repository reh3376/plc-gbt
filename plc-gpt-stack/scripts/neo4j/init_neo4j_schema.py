#!/usr/bin/env python3
"""
Neo4j Schema Initialization Script
Phase 3: Knowledge Graph Schema Implementation
Version: 1.0.0

This script initializes the Neo4j database schema for the PLC-GPT project.
It creates node types, relationships, constraints, and indexes.
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
import structlog

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


class Neo4jSchemaInitializer:
    """Handles Neo4j schema initialization and validation."""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection URI (e.g., bolt://localhost:7687)
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            logger.info("Connected to Neo4j", uri=self.uri, user=self.user)
        except Exception as e:
            logger.error("Failed to connect to Neo4j", error=str(e))
            raise
            
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")
            
    def execute_cypher_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Execute a Cypher script file.
        
        Args:
            file_path: Path to the Cypher script file
            
        Returns:
            Execution results and statistics
        """
        logger.info("Executing Cypher script", file=str(file_path))
        
        # Read the Cypher script
        with open(file_path, 'r') as f:
            cypher_script = f.read()
            
        # Split into individual statements (by semicolon)
        statements = [s.strip() for s in cypher_script.split(';') if s.strip()]
        
        results = {
            'total_statements': len(statements),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'execution_time': 0
        }
        
        start_time = time.time()
        
        with self.driver.session() as session:
            for i, statement in enumerate(statements):
                # Skip comments and empty lines
                if statement.startswith('//') or not statement:
                    continue
                    
                try:
                    # Execute statement
                    result = session.run(statement)
                    summary = result.consume()
                    
                    # Log statement execution
                    logger.debug(
                        "Executed statement",
                        index=i,
                        nodes_created=summary.counters.nodes_created,
                        relationships_created=summary.counters.relationships_created,
                        properties_set=summary.counters.properties_set
                    )
                    
                    results['successful'] += 1
                    
                except Neo4jError as e:
                    error_msg = f"Statement {i}: {str(e)}"
                    logger.error("Statement failed", index=i, error=str(e))
                    results['failed'] += 1
                    results['errors'].append(error_msg)
                    
        results['execution_time'] = time.time() - start_time
        
        logger.info(
            "Cypher script execution complete",
            successful=results['successful'],
            failed=results['failed'],
            time=f"{results['execution_time']:.2f}s"
        )
        
        return results
        
    def validate_schema(self) -> Dict[str, Any]:
        """
        Validate the created schema.
        
        Returns:
            Validation results
        """
        logger.info("Validating Neo4j schema")
        
        validation_queries = {
            'node_types': """
                MATCH (n) 
                RETURN DISTINCT labels(n) as NodeType, count(n) as Count 
                ORDER BY NodeType
            """,
            'constraints': """
                SHOW CONSTRAINTS
            """,
            'indexes': """
                SHOW INDEXES
            """,
            'relationships': """
                MATCH ()-[r]->()
                RETURN DISTINCT type(r) as RelationType, count(r) as Count
                ORDER BY RelationType
            """,
            'orphaned_nodes': """
                MATCH (n)
                WHERE NOT (n)--()
                RETURN labels(n)[0] as NodeType, count(n) as Count
            """
        }
        
        results = {}
        
        with self.driver.session() as session:
            for query_name, query in validation_queries.items():
                try:
                    result = session.run(query)
                    data = [record.data() for record in result]
                    results[query_name] = data
                    
                    # Log results
                    logger.info(f"Validation: {query_name}", count=len(data))
                    
                except Neo4jError as e:
                    logger.error(f"Validation query failed: {query_name}", error=str(e))
                    results[query_name] = {'error': str(e)}
                    
        return results
        
    def create_sample_data(self) -> Dict[str, int]:
        """
        Create sample data for testing.
        
        Returns:
            Count of created entities
        """
        logger.info("Creating sample data")
        
        # This is included in the Cypher script, but we can add more here if needed
        sample_queries = [
            # Additional sample data can be added here
        ]
        
        counts = {
            'nodes': 0,
            'relationships': 0
        }
        
        # Execute any additional sample data queries
        with self.driver.session() as session:
            for query in sample_queries:
                result = session.run(query)
                summary = result.consume()
                counts['nodes'] += summary.counters.nodes_created
                counts['relationships'] += summary.counters.relationships_created
                
        return counts
        
    def get_schema_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive schema statistics.
        
        Returns:
            Schema statistics
        """
        with self.driver.session() as session:
            # Node counts by type
            node_result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as Type, count(n) as Count
                ORDER BY Count DESC
            """)
            node_stats = {r['Type']: r['Count'] for r in node_result}
            
            # Relationship counts by type
            rel_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as Type, count(r) as Count
                ORDER BY Count DESC
            """)
            rel_stats = {r['Type']: r['Count'] for r in rel_result}
            
            # Total counts
            total_nodes = session.run("MATCH (n) RETURN count(n) as count").single()['count']
            total_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()['count']
            
            # Database size
            db_stats = session.run("CALL dbms.database.state('neo4j')").single()
            
            return {
                'node_types': node_stats,
                'relationship_types': rel_stats,
                'total_nodes': total_nodes,
                'total_relationships': total_rels,
                'database_state': db_stats.get('state', 'unknown')
            }


def main():
    """Main execution function."""
    # Configuration
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "your-password-here")
    
    # Schema file path
    script_dir = Path(__file__).parent
    schema_file = script_dir / "create_schema.cypher"
    
    # Check if schema file exists
    if not schema_file.exists():
        logger.error("Schema file not found", file=str(schema_file))
        sys.exit(1)
        
    logger.info(
        "Starting Neo4j schema initialization",
        uri=neo4j_uri,
        user=neo4j_user,
        schema_file=str(schema_file)
    )
    
    try:
        # Initialize schema
        with Neo4jSchemaInitializer(neo4j_uri, neo4j_user, neo4j_password) as initializer:
            # Execute schema creation
            logger.info("Creating schema...")
            execution_results = initializer.execute_cypher_file(schema_file)
            
            if execution_results['failed'] > 0:
                logger.error(
                    "Schema creation had errors",
                    failed=execution_results['failed'],
                    errors=execution_results['errors']
                )
            
            # Validate schema
            logger.info("Validating schema...")
            validation_results = initializer.validate_schema()
            
            # Get statistics
            logger.info("Getting schema statistics...")
            stats = initializer.get_schema_statistics()
            
            # Print summary
            print("\n" + "="*60)
            print("NEO4J SCHEMA INITIALIZATION COMPLETE")
            print("="*60)
            print(f"\nExecution Summary:")
            print(f"  - Statements executed: {execution_results['successful']}")
            print(f"  - Statements failed: {execution_results['failed']}")
            print(f"  - Execution time: {execution_results['execution_time']:.2f}s")
            
            print(f"\nSchema Statistics:")
            print(f"  - Total nodes: {stats['total_nodes']}")
            print(f"  - Total relationships: {stats['total_relationships']}")
            print(f"  - Node types: {len(stats['node_types'])}")
            print(f"  - Relationship types: {len(stats['relationship_types'])}")
            
            print(f"\nNode Type Counts:")
            for node_type, count in stats['node_types'].items():
                print(f"    - {node_type}: {count}")
                
            print(f"\nRelationship Type Counts:")
            for rel_type, count in stats['relationship_types'].items():
                print(f"    - {rel_type}: {count}")
                
            # Check for issues
            if validation_results.get('orphaned_nodes'):
                orphans = validation_results['orphaned_nodes']
                if orphans and any(o.get('Count', 0) > 0 for o in orphans):
                    print("\n⚠️  WARNING: Orphaned nodes detected!")
                    for orphan in orphans:
                        if orphan.get('Count', 0) > 0:
                            print(f"    - {orphan['NodeType']}: {orphan['Count']}")
                            
            print("\n✅ Schema initialization successful!")
            
    except Exception as e:
        logger.error("Schema initialization failed", error=str(e))
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 