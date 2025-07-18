#!/usr/bin/env python3
"""
🧠 Phase 24.2: PLC Memory Integration - AI Task Orchestrator Implementation

Task 24.2.1: Prepare data for ingestion into PLC memory system
- Convert schemas to memory format
- Extract code documentation
- Process control data
- Structure relationships

Author: AI Task Orchestrator
Created: 2025-07-15
Phase: 24.2 - PLC Memory Integration
Dependencies: Phase 24.1 (Context Discovery & Analysis)
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Phase 24.1 imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "context"))
from scanner import ContextScanner, ScanResult
from analyzer import ContentAnalyzer
from extractor import KnowledgeExtractor
from validator import ValidationSystem

# PLC Memory imports
sys.path.append(str(Path(__file__).parent))
from memory_coordinator import MemoryCoordinator, MemoryRequest
from database_manager import DatabaseManager, DatabaseType, MemoryTier

logger = logging.getLogger(__name__)

@dataclass
class IngestionPackage:
    """Structured package ready for PLC memory ingestion"""
    package_id: str
    timestamp: datetime
    source_path: str
    
    # Structured data
    schemas: List[Dict[str, Any]]
    code_documentation: List[Dict[str, Any]]
    control_data: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    
    # Metadata
    entity_count: int
    relationship_count: int
    training_examples: List[Dict[str, Any]]
    
    # Quality metrics
    validation_score: float
    confidence_scores: Dict[str, float]
    
    # Memory routing strategy
    memory_distribution: Dict[str, List[str]]

class Phase24_2_MemoryIntegration:
    """
    Phase 24.2: PLC Memory Integration
    
    Integrates Phase 24.1 context analysis results into the PLC memory system
    with optimal data distribution across Redis, Neo4j, PostgreSQL, and Qdrant.
    """
    
    def __init__(self, context_path: str = "/Users/reh3376/repos/plc-gbt/plc-gbt-stack/docs/context"):
        self.context_path = Path(context_path)
        self.coordinator: Optional[MemoryCoordinator] = None
        self.db_manager: Optional[DatabaseManager] = None
        
        # Initialize Phase 24.1 components
        self.scanner = ContextScanner(str(self.context_path))
        self.analyzer = ContentAnalyzer()
        self.extractor = KnowledgeExtractor()
        self.validator = ValidationSystem()
        
        logger.info(f"Phase24_2_MemoryIntegration initialized for: {self.context_path}")
        
    async def initialize_memory_system(self):
        """Initialize PLC memory system connections"""
        try:
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize_all_connections()
            
            self.coordinator = MemoryCoordinator(self.db_manager)
            
            logger.info("✅ PLC memory system initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize memory system: {e}")
            return False
    
    async def execute_task_24_2_1(self) -> IngestionPackage:
        """
        Task 24.2.1: Prepare data for ingestion
        
        Converts Phase 24.1 analysis results into structured format
        optimized for PLC memory system ingestion.
        """
        logger.info("🔄 Starting Task 24.2.1: Prepare data for ingestion")
        
        # Step 1: Run Phase 24.1 pipeline if not already done
        scan_results = self.scanner.scan_directory(recursive=True)
        analysis_results = self.analyzer.analyze_content(scan_results)
        extracted_knowledge = self.extractor.extract_knowledge(scan_results, analysis_results)
        validation_report = self.validator.validate_all(scan_results, analysis_results, extracted_knowledge)
        
        logger.info(f"📊 Phase 24.1 results: {len(scan_results)} files scanned")
        
        # Step 2: Convert schemas to memory format
        schemas = self._convert_schemas_to_memory_format(scan_results, analysis_results)
        logger.info(f"🗂️ Converted {len(schemas)} schemas")
        
        # Step 3: Extract code documentation
        code_docs = self._extract_code_documentation(scan_results, analysis_results)
        logger.info(f"📚 Extracted {len(code_docs)} code documentation entries")
        
        # Step 4: Process control data
        control_data = self._process_control_data(scan_results, analysis_results)
        logger.info(f"🎛️ Processed {len(control_data)} control data entries")
        
        # Step 5: Structure relationships
        relationships = self._structure_relationships(extracted_knowledge)
        logger.info(f"🔗 Structured {len(relationships)} relationships")
        
        # Step 6: Prepare training examples
        training_examples = self._prepare_training_examples(extracted_knowledge)
        logger.info(f"📝 Prepared {len(training_examples)} training examples")
        
        # Step 7: Create memory distribution strategy
        memory_distribution = self._create_memory_distribution_strategy(
            schemas, code_docs, control_data, relationships
        )
        
        # Step 8: Create ingestion package
        package = IngestionPackage(
            package_id=f"phase24_2_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(),
            source_path=str(self.context_path),
            schemas=schemas,
            code_documentation=code_docs,
            control_data=control_data,
            relationships=relationships,
            entity_count=len(extracted_knowledge.entities),
            relationship_count=len(relationships),
            training_examples=training_examples,
            validation_score=validation_report.overall_score,
            confidence_scores=self._extract_confidence_scores(extracted_knowledge),
            memory_distribution=memory_distribution
        )
        
        logger.info(f"📦 Created ingestion package: {package.package_id}")
        logger.info(f"✅ Task 24.2.1 completed successfully")
        
        return package
    
    def _convert_schemas_to_memory_format(self, scan_results: List[ScanResult], 
                                        analysis_results) -> List[Dict[str, Any]]:
        """Convert JSON schemas to PLC memory format"""
        schemas = []
        
        # Access schema patterns from ContentAnalysisResults object
        schema_patterns = analysis_results.schema_patterns
        
        for pattern in schema_patterns:
            schema_entry = {
                'schema_id': f"schema_{len(schemas) + 1}",
                'name': pattern.pattern_type,  # Use pattern_type as name
                'type': 'control_loop_schema',
                'version': '1.0.0',
                'description': pattern.description,
                'properties': pattern.properties,
                'occurrences': pattern.occurrences,
                'schema_files': pattern.schema_files,
                'category': self._categorize_schema_pattern(pattern),
                'memory_tier': 'neo4j',  # Schemas go to Neo4j for relationship modeling
                'metadata': {
                    'source_files': pattern.schema_files,
                    'example_values': pattern.example_values,
                    'validated': True
                }
            }
            schemas.append(schema_entry)
        
        return schemas
    
    def _extract_code_documentation(self, scan_results: List[ScanResult], 
                                  analysis_results) -> List[Dict[str, Any]]:
        """Extract and structure code documentation"""
        code_docs = []
        
        # Find Python files with significant code
        for result in scan_results:
            if result.metadata.extension == '.py' and result.raw_content:
                doc_entry = {
                    'doc_id': f"code_doc_{len(code_docs) + 1}",
                    'file_path': result.metadata.path,
                    'file_name': result.metadata.name,
                    'type': 'python_code',
                    'functions': self._extract_function_info(result.raw_content),
                    'classes': self._extract_class_info(result.raw_content),
                    'imports': self._extract_import_info(result.raw_content),
                    'complexity': 'moderate',  # Default complexity
                    'memory_tier': 'postgresql',  # Code docs go to PostgreSQL for structured queries
                    'metadata': {
                        'size_bytes': result.metadata.size_bytes,
                        'file_hash': result.metadata.content_hash,
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                }
                code_docs.append(doc_entry)
        
        return code_docs
    
    def _process_control_data(self, scan_results: List[ScanResult], 
                            analysis_results) -> List[Dict[str, Any]]:
        """Process control system data files"""
        control_data = []
        
        # Find CSV and data files
        for result in scan_results:
            if result.metadata.extension in ['.csv', '.data']:
                data_entry = {
                    'data_id': f"control_data_{len(control_data) + 1}",
                    'file_path': result.metadata.path,
                    'file_name': result.metadata.name,
                    'type': 'control_system_data',
                    'format': result.metadata.extension,
                    'variables': self._extract_data_variables(result),
                    'time_series': self._is_time_series_data(result),
                    'memory_tier': 'qdrant',  # Data goes to Qdrant for similarity search
                    'metadata': {
                        'size_bytes': result.metadata.size_bytes,
                        'estimated_records': self._estimate_record_count(result),
                        'data_quality': 'validated'
                    }
                }
                control_data.append(data_entry)
        
        return control_data
    
    def _structure_relationships(self, extracted_knowledge) -> List[Dict[str, Any]]:
        """Structure relationships for knowledge graph"""
        relationships = []
        
        # Access relationships from ExtractedKnowledge object
        extracted_relationships = extracted_knowledge.relationships
        
        for rel in extracted_relationships:
            # Handle KnowledgeRelationship objects
            relationship = {
                'relationship_id': f"rel_{len(relationships) + 1}",
                'source_entity': rel.source_entity,
                'target_entity': rel.target_entity,
                'relationship_type': rel.relationship_type,
                'strength': rel.strength,
                'confidence': rel.confidence,
                'context': rel.context,
                'memory_tier': 'neo4j',  # Relationships go to Neo4j
                'metadata': {
                    'extracted_from': rel.source_files[0] if rel.source_files else 'unknown',
                    'validation_status': 'pending'
                }
            }
            relationships.append(relationship)
        
        return relationships
    
    def _prepare_training_examples(self, extracted_knowledge) -> List[Dict[str, Any]]:
        """Prepare training examples for model enhancement"""
        training_examples = []
        
        # Access training examples from ExtractedKnowledge object
        examples = extracted_knowledge.training_examples
        
        for example in examples:
            # Handle TrainingExample objects
            training_entry = {
                'example_id': f"train_{len(training_examples) + 1}",
                'question': example.question,
                'answer': example.answer,
                'category': example.category,
                'confidence': example.confidence,
                'source': example.source_files[0] if example.source_files else 'unknown',
                'memory_tier': 'redis',  # Training examples cached in Redis
                'metadata': {
                    'tokens_estimate': len(example.question + example.answer) // 4,
                    'difficulty_level': example.difficulty_level,
                    'tags': example.tags
                }
            }
            training_examples.append(training_entry)
        
        return training_examples
    
    def _create_memory_distribution_strategy(self, schemas: List[Dict], code_docs: List[Dict], 
                                           control_data: List[Dict], relationships: List[Dict]) -> Dict[str, List[str]]:
        """Create optimal memory distribution strategy"""
        return {
            'redis': [item['schema_id'] for item in schemas if item.get('access_frequency') == 'high'],
            'neo4j': [item['schema_id'] for item in schemas] + 
                    [item['relationship_id'] for item in relationships],
            'postgresql': [item['doc_id'] for item in code_docs],
            'qdrant': [item['data_id'] for item in control_data] + 
                     [item['schema_id'] for item in schemas]  # Schemas also in Qdrant for similarity
        }
    
    def _categorize_schema_pattern(self, pattern) -> str:
        """Categorize schema based on pattern analysis"""
        name = pattern.pattern_type.lower()
        description = pattern.description.lower()
        
        # Check both pattern type and description for categorization
        combined_text = f"{name} {description}"
        
        if 'cascade' in combined_text or 'cas' in combined_text:
            return 'cascade_control'
        elif 'feedforward' in combined_text or 'ff' in combined_text:
            return 'feedforward_control'
        elif 'pide' in combined_text:
            return 'pide_control'
        elif 'pid' in combined_text:
            return 'pid_control'
        else:
            return 'standard_control'
    
    def _extract_function_info(self, content: str) -> List[Dict[str, Any]]:
        """Extract function information from Python code"""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                func_name = line.split('def ')[1].split('(')[0].strip()
                functions.append({
                    'name': func_name,
                    'line_number': i + 1,
                    'signature': line.strip(),
                    'docstring': self._extract_docstring(lines, i + 1)
                })
        
        return functions
    
    def _extract_class_info(self, content: str) -> List[Dict[str, Any]]:
        """Extract class information from Python code"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip().startswith('class '):
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append({
                    'name': class_name,
                    'line_number': i + 1,
                    'definition': line.strip(),
                    'docstring': self._extract_docstring(lines, i + 1)
                })
        
        return classes
    
    def _extract_import_info(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(stripped)
        
        return imports
    
    def _extract_docstring(self, lines: List[str], start_line: int) -> Optional[str]:
        """Extract docstring for function or class"""
        if start_line < len(lines):
            next_line = lines[start_line].strip()
            if next_line.startswith('"""') or next_line.startswith("'''"):
                # Simple docstring extraction
                return next_line.replace('"""', '').replace("'''", '').strip()
        return None
    
    def _extract_data_variables(self, result: ScanResult) -> List[str]:
        """Extract variable names from data files"""
        if result.metadata.extension == '.csv' and result.raw_content:
            # First line typically contains headers
            first_line = result.raw_content.split('\n')[0]
            return [col.strip() for col in first_line.split(',')]
        return []
    
    def _is_time_series_data(self, result: ScanResult) -> bool:
        """Check if data appears to be time series"""
        if result.raw_content:
            # Look for time-related column names
            first_line = result.raw_content.split('\n')[0].lower()
            time_indicators = ['time', 'timestamp', 'date', 'datetime']
            return any(indicator in first_line for indicator in time_indicators)
        return False
    
    def _estimate_record_count(self, result: ScanResult) -> int:
        """Estimate number of records in data file"""
        if result.raw_content:
            return len(result.raw_content.split('\n')) - 1  # Subtract header
        return 0
    
    def _extract_confidence_scores(self, extracted_knowledge) -> Dict[str, float]:
        """Extract confidence scores from knowledge extraction"""
        # Access entities and relationships from ExtractedKnowledge object
        entities = extracted_knowledge.entities
        relationships = extracted_knowledge.relationships
        
        entity_confidences = [e.confidence for e in entities]
        relationship_confidences = [r.confidence for r in relationships]
        
        return {
            'average_entity_confidence': sum(entity_confidences) / len(entity_confidences) if entity_confidences else 0.0,
            'average_relationship_confidence': sum(relationship_confidences) / len(relationship_confidences) if relationship_confidences else 0.0,
            'overall_confidence': (sum(entity_confidences + relationship_confidences) / 
                                 len(entity_confidences + relationship_confidences)) if (entity_confidences + relationship_confidences) else 0.0
        }
    
    async def save_ingestion_package(self, package: IngestionPackage) -> str:
        """Save ingestion package for Task 24.2.2"""
        package_path = Path("../results/phase24") / f"{package.package_id}_ingestion_package.json"
        package_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        package_data = asdict(package)
        package_data['timestamp'] = package.timestamp.isoformat()
        
        with open(package_path, 'w') as f:
            json.dump(package_data, f, indent=2, default=str)
        
        logger.info(f"📦 Ingestion package saved: {package_path}")
        return str(package_path)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db_manager:
            await self.db_manager.close_all_connections()
        logger.info("🧹 Resources cleaned up")

async def main():
    """Main execution for Task 24.2.1"""
    logger.info("🚀 Starting Phase 24.2 Task 24.2.1: Prepare data for ingestion")
    
    integration = Phase24_2_MemoryIntegration()
    
    try:
        # Initialize memory system
        if not await integration.initialize_memory_system():
            logger.error("❌ Failed to initialize memory system")
            return
        
        # Execute Task 24.2.1
        package = await integration.execute_task_24_2_1()
        
        # Save package for Task 24.2.2
        package_path = await integration.save_ingestion_package(package)
        
        # Print summary
        print(f"\n✅ Task 24.2.1 Complete: Prepare data for ingestion")
        print(f"📦 Ingestion Package ID: {package.package_id}")
        print(f"🗂️ Schemas prepared: {len(package.schemas)}")
        print(f"📚 Code docs extracted: {len(package.code_documentation)}")
        print(f"🎛️ Control data processed: {len(package.control_data)}")
        print(f"🔗 Relationships structured: {len(package.relationships)}")
        print(f"📝 Training examples: {len(package.training_examples)}")
        print(f"🎯 Validation score: {package.validation_score:.2f}")
        print(f"💾 Package saved: {package_path}")
        
        # Memory distribution summary
        print(f"\n🧠 Memory Distribution Strategy:")
        for tier, items in package.memory_distribution.items():
            print(f"  {tier}: {len(items)} items")
            
    except Exception as e:
        logger.error(f"❌ Task 24.2.1 failed: {e}")
        raise
    finally:
        await integration.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main()) 