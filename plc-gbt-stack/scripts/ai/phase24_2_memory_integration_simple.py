#!/usr/bin/env python3
"""
🧠 Phase 24.2: PLC Memory Integration - Simplified Implementation

Task 24.2.1: Prepare data for ingestion into PLC memory system

Author: AI Task Orchestrator
Created: 2025-07-15
Phase: 24.2 - PLC Memory Integration
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Phase 24.1 imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "context"))
from scanner import ContextScanner
from analyzer import ContentAnalyzer
from extractor import KnowledgeExtractor
from validator import ValidationSystem

# PLC Memory imports
sys.path.append(str(Path(__file__).parent))
from memory_coordinator import MemoryCoordinator
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class IngestionPackage:
    """Structured package ready for PLC memory ingestion"""
    package_id: str
    timestamp: datetime
    source_path: str
    
    # Summary statistics
    files_processed: int
    schemas_found: int
    entities_extracted: int
    relationships_extracted: int
    training_examples_generated: int
    
    # Quality metrics
    validation_score: float
    overall_confidence: float
    
    # Memory routing strategy
    memory_distribution: Dict[str, int]

class Phase24_2_MemoryIntegrationSimple:
    """
    Simplified Phase 24.2: PLC Memory Integration
    
    Runs Phase 24.1 pipeline and prepares summary for Task 24.2.2
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
        
        logger.info(f"Phase24_2_MemoryIntegrationSimple initialized for: {self.context_path}")
        
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
        
        Runs Phase 24.1 pipeline and creates ingestion package summary.
        """
        logger.info("🔄 Starting Task 24.2.1: Prepare data for ingestion")
        
        # Step 1: Run Phase 24.1 pipeline
        scan_results = self.scanner.scan_directory(recursive=True)
        analysis_results = self.analyzer.analyze_content(scan_results)
        extracted_knowledge = self.extractor.extract_knowledge(scan_results, analysis_results)
        validation_report = self.validator.validate_all(scan_results, analysis_results, extracted_knowledge)
        
        logger.info(f"📊 Phase 24.1 results: {len(scan_results)} files scanned")
        
        # Step 2: Extract summary statistics
        files_processed = len(scan_results)
        schemas_found = len(analysis_results.schema_patterns)
        entities_extracted = len(extracted_knowledge.entities)
        relationships_extracted = len(extracted_knowledge.relationships)
        training_examples_generated = len(extracted_knowledge.training_examples)
        
        # Step 3: Calculate confidence scores
        entity_confidences = [e.confidence_score for e in extracted_knowledge.entities]
        overall_confidence = sum(entity_confidences) / len(entity_confidences) if entity_confidences else 0.0
        
        # Step 4: Create memory distribution strategy
        memory_distribution = {
            'redis': min(100, schemas_found),  # High-frequency access schemas
            'neo4j': schemas_found + relationships_extracted,  # All schemas and relationships
            'postgresql': len([r for r in scan_results if r.metadata.extension == '.py']),  # Code documentation
            'qdrant': len([r for r in scan_results if r.metadata.extension in ['.csv', '.data']])  # Data files
        }
        
        # Step 5: Create ingestion package
        package = IngestionPackage(
            package_id=f"phase24_2_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(),
            source_path=str(self.context_path),
            files_processed=files_processed,
            schemas_found=schemas_found,
            entities_extracted=entities_extracted,
            relationships_extracted=relationships_extracted,
            training_examples_generated=training_examples_generated,
            validation_score=validation_report.overall_score,
            overall_confidence=overall_confidence,
            memory_distribution=memory_distribution
        )
        
        logger.info(f"📦 Created ingestion package: {package.package_id}")
        logger.info(f"✅ Task 24.2.1 completed successfully")
        
        return package
    
    async def save_ingestion_package(self, package: IngestionPackage) -> str:
        """Save ingestion package for Task 24.2.2"""
        package_path = Path("results/phase24") / f"{package.package_id}_ingestion_package.json"
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
    
    integration = Phase24_2_MemoryIntegrationSimple()
    
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
        print(f"📁 Files processed: {package.files_processed}")
        print(f"🗂️ Schemas found: {package.schemas_found}")
        print(f"🧠 Entities extracted: {package.entities_extracted}")
        print(f"🔗 Relationships extracted: {package.relationships_extracted}")
        print(f"📝 Training examples generated: {package.training_examples_generated}")
        print(f"🎯 Validation score: {package.validation_score:.2f}")
        print(f"🔮 Overall confidence: {package.overall_confidence:.2f}")
        print(f"💾 Package saved: {package_path}")
        
        # Memory distribution summary
        print(f"\n🧠 Memory Distribution Strategy:")
        for tier, count in package.memory_distribution.items():
            print(f"  {tier}: {count} items")
            
    except Exception as e:
        logger.error(f"❌ Task 24.2.1 failed: {e}")
        raise
    finally:
        await integration.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main()) 