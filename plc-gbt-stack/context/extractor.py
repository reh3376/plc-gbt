#!/usr/bin/env python3
"""
🔍 Knowledge Extractor Module - Phase 24.1 Task 24.1.3

AI Task Orchestrator Implementation for extracting actionable knowledge.
Builds on content analysis to create structured knowledge for memory ingestion.

Author: AI Task Orchestrator
Created: 2025-07-15
Phase: 24.1 - Context Discovery & Analysis
"""

import json
import logging
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from analyzer import ContentAnalysisResults, ContentAnalyzer

# Import from previous modules
from scanner import ContextScanner, ScanResult

logger = logging.getLogger(__name__)

@dataclass
class KnowledgeEntity:
    """Represents a knowledge entity for memory storage"""
    entity_id: str
    entity_type: str  # concept, schema, algorithm, best_practice, data_pattern
    name: str
    description: str
    properties: Dict[str, Any]
    relationships: List[str]  # IDs of related entities
    source_files: List[str]
    confidence_score: float
    tags: List[str]

@dataclass
class KnowledgeRelationship:
    """Represents a relationship between knowledge entities"""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str  # depends_on, extends, implements, part_of, similar_to
    strength: float  # 0.0 to 1.0
    properties: Dict[str, Any]
    evidence: List[str]  # Supporting evidence for the relationship

@dataclass
class TrainingExample:
    """Represents a training example for model enhancement"""
    example_id: str
    question: str
    answer: str
    context: str
    example_type: str  # qa, instruction, conversation
    difficulty_level: str  # basic, intermediate, advanced
    tags: List[str]
    source_files: List[str]

@dataclass
class ExtractedKnowledge:
    """Complete extracted knowledge ready for memory ingestion"""
    entities: List[KnowledgeEntity]
    relationships: List[KnowledgeRelationship]
    training_examples: List[TrainingExample]
    knowledge_graph: Dict[str, Any]
    ingestion_metadata: Dict[str, Any]

class KnowledgeExtractor:
    """
    Advanced knowledge extractor for Phase 24.1

    Extracts structured, actionable knowledge from content analysis
    results and prepares it for ingestion into the PLC memory system.
    """

    def __init__(self):
        self.entities: List[KnowledgeEntity] = []
        self.relationships: List[KnowledgeRelationship] = []
        self.training_examples: List[TrainingExample] = []

        # Knowledge extraction templates
        self.entity_templates = {
            'control_schema': {
                'type': 'schema',
                'required_properties': ['title', 'control_type', 'complexity_level'],
                'tags': ['control', 'schema', 'configuration']
            },
            'control_algorithm': {
                'type': 'algorithm',
                'required_properties': ['algorithm_name', 'implementation_approach'],
                'tags': ['algorithm', 'control', 'implementation']
            },
            'best_practice': {
                'type': 'best_practice',
                'required_properties': ['practice_text', 'domain'],
                'tags': ['best_practice', 'guidance', 'recommendation']
            },
            'control_concept': {
                'type': 'concept',
                'required_properties': ['concept_name', 'definition'],
                'tags': ['concept', 'theory', 'control']
            }
        }

        # Training example templates
        self.qa_templates = {
            'schema_explanation': {
                'question_prefix': "What is the purpose of the {schema_name} schema?",
                'answer_template': "The {schema_name} schema is used for {description}. It has {property_count} properties and is classified as {complexity_level} complexity.",
                'tags': ['schema', 'explanation']
            },
            'property_usage': {
                'question_prefix': "How is the {property_name} property used in {schema_name}?",
                'answer_template': "In {schema_name}, the {property_name} property {description}. It is of type {type} and {constraints}.",
                'tags': ['property', 'usage']
            },
            'algorithm_comparison': {
                'question_prefix': "What's the difference between {algorithm1} and {algorithm2}?",
                'answer_template': "{algorithm1} uses {approach1} while {algorithm2} uses {approach2}. {algorithm1} is better for {use_case1} and {algorithm2} is better for {use_case2}.",
                'tags': ['algorithm', 'comparison']
            },
            'tuning_guidance': {
                'question_prefix': "How should I tune {control_type} parameters for {application}?",
                'answer_template': "For {control_type} in {application}, start with {initial_settings}. Monitor {key_metrics} and adjust {parameters} based on {criteria}.",
                'tags': ['tuning', 'guidance', 'parameters']
            }
        }

        logger.info("KnowledgeExtractor initialized")

    def extract_knowledge(self, scan_results: List[ScanResult],
                         analysis_results: ContentAnalysisResults) -> ExtractedKnowledge:
        """
        Extract comprehensive knowledge from scan and analysis results

        Args:
            scan_results: Original scan results from ContextScanner
            analysis_results: Analysis results from ContentAnalyzer

        Returns:
            Complete extracted knowledge ready for memory ingestion
        """
        logger.info(f"🔍 Starting knowledge extraction from {len(scan_results)} files")

        # Extract entities
        self._extract_entities(scan_results, analysis_results)

        # Extract relationships
        self._extract_relationships(analysis_results)

        # Generate training examples
        self._generate_training_examples(scan_results, analysis_results)

        # Build knowledge graph structure
        knowledge_graph = self._build_knowledge_graph_structure()

        # Create ingestion metadata
        ingestion_metadata = self._create_ingestion_metadata(scan_results)

        extracted_knowledge = ExtractedKnowledge(
            entities=self.entities,
            relationships=self.relationships,
            training_examples=self.training_examples,
            knowledge_graph=knowledge_graph,
            ingestion_metadata=ingestion_metadata
        )

        logger.info(f"✅ Knowledge extraction complete: {len(self.entities)} entities, "
                   f"{len(self.relationships)} relationships, {len(self.training_examples)} training examples")

        return extracted_knowledge

    def _extract_entities(self, scan_results: List[ScanResult],
                         analysis_results: ContentAnalysisResults):
        """Extract knowledge entities from scan and analysis results"""
        logger.info("📋 Extracting knowledge entities")

        # Extract schema entities
        self._extract_schema_entities(scan_results)

        # Extract algorithm entities
        self._extract_algorithm_entities(analysis_results.algorithm_patterns)

        # Extract concept entities
        self._extract_concept_entities(analysis_results.knowledge_graph)

        # Extract best practice entities
        self._extract_best_practice_entities(scan_results)

        # Extract data pattern entities
        self._extract_data_pattern_entities(analysis_results.data_insights)

        logger.info(f"📋 Extracted {len(self.entities)} knowledge entities")

    def _extract_schema_entities(self, scan_results: List[ScanResult]):
        """Extract entities from control schemas"""
        schema_results = [r for r in scan_results if r.schema_analysis]

        for result in schema_results:
            schema = result.schema_analysis

            entity = KnowledgeEntity(
                entity_id=f"schema_{result.metadata.name.replace('.json', '')}",
                entity_type="schema",
                name=schema.title,
                description=schema.description,
                properties={
                    "control_type": schema.control_type,
                    "complexity_level": schema.complexity_level,
                    "property_count": schema.property_count,
                    "required_fields": schema.required_fields,
                    "version": schema.version,
                    "file_path": result.metadata.path
                },
                relationships=[],  # Will be populated later
                source_files=[result.metadata.name],
                confidence_score=1.0,  # High confidence for structured schemas
                tags=["control", "schema", schema.control_type.lower(),
                      schema.complexity_level.lower()]
            )

            self.entities.append(entity)

    def _extract_algorithm_entities(self, algorithm_patterns):
        """Extract entities from algorithm patterns"""
        for pattern in algorithm_patterns:
            entity = KnowledgeEntity(
                entity_id=f"algorithm_{pattern.algorithm_name.lower().replace(' ', '_').replace('-', '_')}",
                entity_type="algorithm",
                name=pattern.algorithm_name,
                description=f"{pattern.algorithm_name} algorithm implementation",
                properties={
                    "implementation_approach": pattern.implementation_approach,
                    "complexity_level": pattern.complexity_level,
                    "function_names": pattern.function_names,
                    "used_libraries": pattern.used_libraries,
                    "parameters": pattern.parameters
                },
                relationships=[],
                source_files=[],  # Will be populated from pattern source
                confidence_score=0.8,  # Good confidence for detected algorithms
                tags=["algorithm", "control", pattern.algorithm_name.lower().replace(' ', '_')]
            )

            self.entities.append(entity)

    def _extract_concept_entities(self, knowledge_graph):
        """Extract entities from knowledge graph concepts"""
        for category, concepts in knowledge_graph.concepts.items():
            for concept in concepts:
                entity = KnowledgeEntity(
                    entity_id=f"concept_{category}_{concept.lower().replace(' ', '_')}",
                    entity_type="concept",
                    name=concept,
                    description=f"Control concept in category: {category}",
                    properties={
                        "category": category,
                        "domain": "control_systems"
                    },
                    relationships=[],
                    source_files=[],
                    confidence_score=0.7,  # Moderate confidence for extracted concepts
                    tags=["concept", "control", category.lower()]
                )

                self.entities.append(entity)

    def _extract_best_practice_entities(self, scan_results: List[ScanResult]):
        """Extract best practice entities from documentation"""
        doc_results = [r for r in scan_results if r.document_analysis]

        practice_id = 0
        for result in doc_results:
            doc = result.document_analysis

            for practice in doc.best_practices:
                practice_id += 1

                # Determine domain from practice content
                domain = self._determine_practice_domain(practice)

                entity = KnowledgeEntity(
                    entity_id=f"best_practice_{practice_id:03d}",
                    entity_type="best_practice",
                    name=f"Best Practice {practice_id}",
                    description=practice[:100] + "..." if len(practice) > 100 else practice,
                    properties={
                        "practice_text": practice,
                        "domain": domain,
                        "source_document": result.metadata.name
                    },
                    relationships=[],
                    source_files=[result.metadata.name],
                    confidence_score=0.6,  # Moderate confidence for extracted practices
                    tags=["best_practice", domain.lower(), "guidance"]
                )

                self.entities.append(entity)

    def _determine_practice_domain(self, practice_text: str) -> str:
        """Determine the domain of a best practice"""
        text_lower = practice_text.lower()

        if any(term in text_lower for term in ['pid', 'controller', 'tuning']):
            return "PID_Control"
        elif any(term in text_lower for term in ['cascade', 'feedforward']):
            return "Advanced_Control"
        elif any(term in text_lower for term in ['safety', 'interlock', 'alarm']):
            return "Safety"
        elif any(term in text_lower for term in ['commissioning', 'startup']):
            return "Commissioning"
        else:
            return "General"

    def _extract_data_pattern_entities(self, data_insights: Dict[str, Any]):
        """Extract entities from data patterns"""
        for file_name, insights in data_insights.items():
            entity = KnowledgeEntity(
                entity_id=f"data_pattern_{file_name.replace('.', '_')}",
                entity_type="data_pattern",
                name=f"Data Pattern: {file_name}",
                description=f"Data patterns found in {file_name}",
                properties={
                    "file_name": file_name,
                    "size": insights.get("size", "unknown"),
                    "control_variables": insights.get("control_variables", []),
                    "data_types": insights.get("data_types", {}),
                    "potential_use_cases": insights.get("potential_use_cases", [])
                },
                relationships=[],
                source_files=[file_name],
                confidence_score=0.9,  # High confidence for data analysis
                tags=["data", "pattern", "variables"]
            )

            self.entities.append(entity)

    def _extract_relationships(self, analysis_results: ContentAnalysisResults):
        """Extract relationships between entities"""
        logger.info("🔗 Extracting knowledge relationships")

        # Extract schema relationships
        self._extract_schema_relationships(analysis_results.control_relationships)

        # Extract hierarchical relationships
        self._extract_hierarchical_relationships(analysis_results.knowledge_graph)

        # Extract dependency relationships
        self._extract_dependency_relationships(analysis_results.knowledge_graph)

        # Extract similarity relationships
        self._extract_similarity_relationships(analysis_results.schema_patterns)

        logger.info(f"🔗 Extracted {len(self.relationships)} knowledge relationships")

    def _extract_schema_relationships(self, control_relationships):
        """Extract relationships from control analysis"""
        for rel in control_relationships:
            # Map source and target to entity IDs
            source_id = f"schema_{rel.source_schema.replace('.json', '')}"
            target_id = f"schema_{rel.target_schema.replace('.json', '')}"

            # Determine relationship type based on analysis
            rel_type = "similar_to"
            if rel.relationship_type == "extends":
                rel_type = "extends"
            elif rel.relationship_type == "variant":
                rel_type = "variant_of"

            relationship = KnowledgeRelationship(
                relationship_id=f"rel_{source_id}_{target_id}",
                source_entity_id=source_id,
                target_entity_id=target_id,
                relationship_type=rel_type,
                strength=rel.similarity_score,
                properties={
                    "shared_properties": rel.shared_properties,
                    "differences": rel.differences,
                    "similarity_score": rel.similarity_score
                },
                evidence=[f"Shared properties: {len(rel.shared_properties)}",
                          f"Similarity score: {rel.similarity_score:.2f}"]
            )

            self.relationships.append(relationship)

    def _extract_hierarchical_relationships(self, knowledge_graph):
        """Extract hierarchical relationships"""
        for parent, children in knowledge_graph.hierarchies.items():
            parent_id = f"concept_control_types_{parent.lower().replace(' ', '_')}"

            for child in children:
                child_id = f"concept_complexity_{child.lower().replace(' ', '_')}"

                relationship = KnowledgeRelationship(
                    relationship_id=f"hierarchy_{parent_id}_{child_id}",
                    source_entity_id=child_id,
                    target_entity_id=parent_id,
                    relationship_type="part_of",
                    strength=1.0,
                    properties={"hierarchy_type": "complexity"},
                    evidence=["Identified from schema complexity analysis"]
                )

                self.relationships.append(relationship)

    def _extract_dependency_relationships(self, knowledge_graph):
        """Extract dependency relationships"""
        for item, dependencies in knowledge_graph.dependencies.items():
            item_id = f"algorithm_{item.lower().replace(' ', '_').replace('-', '_')}"

            for dep in dependencies[:3]:  # Limit to top 3 dependencies
                # Create dependency entity if it doesn't exist
                dep_id = f"dependency_{dep.replace(' ', '_').replace('.', '_')}"

                relationship = KnowledgeRelationship(
                    relationship_id=f"depends_{item_id}_{dep_id}",
                    source_entity_id=item_id,
                    target_entity_id=dep_id,
                    relationship_type="depends_on",
                    strength=0.8,
                    properties={"dependency_type": "implementation"},
                    evidence=[f"Identified from import analysis: {dep}"]
                )

                self.relationships.append(relationship)

    def _extract_similarity_relationships(self, schema_patterns):
        """Extract similarity relationships from patterns"""
        for pattern in schema_patterns:
            if pattern.pattern_type == "common_property" and pattern.occurrences >= 2:
                # Create relationships between schemas that share this property
                schema_files = pattern.schema_files

                for i, schema1 in enumerate(schema_files):
                    for schema2 in schema_files[i+1:]:
                        source_id = f"schema_{schema1.replace('.json', '')}"
                        target_id = f"schema_{schema2.replace('.json', '')}"

                        relationship = KnowledgeRelationship(
                            relationship_id=f"similar_prop_{source_id}_{target_id}_{pattern.properties[0]}",
                            source_entity_id=source_id,
                            target_entity_id=target_id,
                            relationship_type="shares_property",
                            strength=0.6,
                            properties={
                                "shared_property": pattern.properties[0],
                                "pattern_type": pattern.pattern_type
                            },
                            evidence=[f"Both schemas have property: {pattern.properties[0]}"]
                        )

                        self.relationships.append(relationship)

    def _generate_training_examples(self, scan_results: List[ScanResult],
                                  analysis_results: ContentAnalysisResults):
        """Generate training examples for model enhancement"""
        logger.info("📚 Generating training examples")

        # Generate schema-based examples
        self._generate_schema_examples(scan_results)

        # Generate algorithm examples
        self._generate_algorithm_examples(analysis_results.algorithm_patterns)

        # Generate best practice examples
        self._generate_best_practice_examples(scan_results)

        # Generate comparison examples
        self._generate_comparison_examples(analysis_results.control_relationships)

        logger.info(f"📚 Generated {len(self.training_examples)} training examples")

    def _generate_schema_examples(self, scan_results: List[ScanResult]):
        """Generate training examples from schemas"""
        schema_results = [r for r in scan_results if r.schema_analysis]

        for result in schema_results:
            schema = result.schema_analysis

            # Schema explanation example
            question = f"What is the purpose of the {schema.title} schema?"
            answer = (f"The {schema.title} schema is used for {schema.description[:200]}... "
                     f"It has {schema.property_count} properties and is classified as "
                     f"{schema.complexity_level} complexity in the {schema.control_type} category.")

            example = TrainingExample(
                example_id=f"schema_explain_{result.metadata.name.replace('.json', '')}",
                question=question,
                answer=answer,
                context=f"Control schema: {schema.title}",
                example_type="qa",
                difficulty_level="intermediate",
                tags=["schema", "explanation", schema.control_type.lower()],
                source_files=[result.metadata.name]
            )

            self.training_examples.append(example)

            # Property usage examples
            if len(schema.required_fields) > 0:
                prop = schema.required_fields[0]  # Use first required field
                question = f"How is the {prop} property used in {schema.title}?"
                answer = f"In {schema.title}, the {prop} property is a required field that defines {prop.lower()} for the control loop configuration."

                example = TrainingExample(
                    example_id=f"prop_usage_{result.metadata.name.replace('.json', '')}_{prop}",
                    question=question,
                    answer=answer,
                    context=f"Property usage in {schema.title}",
                    example_type="qa",
                    difficulty_level="basic",
                    tags=["property", "usage", schema.control_type.lower()],
                    source_files=[result.metadata.name]
                )

                self.training_examples.append(example)

    def _generate_algorithm_examples(self, algorithm_patterns):
        """Generate training examples from algorithms"""
        for pattern in algorithm_patterns:
            # Algorithm explanation
            question = f"How is the {pattern.algorithm_name} algorithm implemented?"
            answer = (f"The {pattern.algorithm_name} algorithm is implemented using a "
                     f"{pattern.implementation_approach} approach with {pattern.complexity_level} "
                     f"complexity. It uses functions like {', '.join(pattern.function_names[:3])} "
                     f"and relies on libraries such as {', '.join(pattern.used_libraries[:2])}.")

            example = TrainingExample(
                example_id=f"algo_impl_{pattern.algorithm_name.lower().replace(' ', '_')}",
                question=question,
                answer=answer,
                context=f"Algorithm implementation: {pattern.algorithm_name}",
                example_type="qa",
                difficulty_level="advanced",
                tags=["algorithm", "implementation", pattern.algorithm_name.lower().replace(' ', '_')],
                source_files=[]
            )

            self.training_examples.append(example)

    def _generate_best_practice_examples(self, scan_results: List[ScanResult]):
        """Generate training examples from best practices"""
        doc_results = [r for r in scan_results if r.document_analysis]

        for result in doc_results:
            doc = result.document_analysis

            for i, practice in enumerate(doc.best_practices[:3]):  # Limit to first 3
                # Extract domain from practice
                domain = self._determine_practice_domain(practice)

                question = f"What is a best practice for {domain.lower().replace('_', ' ')}?"
                answer = practice

                example = TrainingExample(
                    example_id=f"best_practice_{result.metadata.name.replace('.', '_')}_{i}",
                    question=question,
                    answer=answer,
                    context=f"Best practices from {result.metadata.name}",
                    example_type="qa",
                    difficulty_level="intermediate",
                    tags=["best_practice", domain.lower(), "guidance"],
                    source_files=[result.metadata.name]
                )

                self.training_examples.append(example)

    def _generate_comparison_examples(self, control_relationships):
        """Generate comparison examples from relationships"""
        for rel in control_relationships[:5]:  # Limit to first 5
            if rel.similarity_score > 0.5:
                schema1 = rel.source_schema.replace('.json', '').replace('-', ' ').title()
                schema2 = rel.target_schema.replace('.json', '').replace('-', ' ').title()

                question = f"What's the difference between {schema1} and {schema2}?"
                answer = (f"{schema1} and {schema2} are similar control configurations with "
                         f"{len(rel.shared_properties)} shared properties. The main differences are "
                         f"in {', '.join(rel.differences[:3])}. They have a similarity score of "
                         f"{rel.similarity_score:.2f}.")

                example = TrainingExample(
                    example_id=f"compare_{rel.source_schema.replace('.json', '')}_{rel.target_schema.replace('.json', '')}",
                    question=question,
                    answer=answer,
                    context=f"Comparison between {schema1} and {schema2}",
                    example_type="qa",
                    difficulty_level="advanced",
                    tags=["comparison", "schema", "differences"],
                    source_files=[rel.source_schema, rel.target_schema]
                )

                self.training_examples.append(example)

    def _build_knowledge_graph_structure(self) -> Dict[str, Any]:
        """Build the knowledge graph structure for ingestion"""
        graph = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "total_entities": len(self.entities),
                "total_relationships": len(self.relationships),
                "entity_types": dict(Counter([e.entity_type for e in self.entities])),
                "relationship_types": dict(Counter([r.relationship_type for r in self.relationships]))
            }
        }

        # Add nodes
        for entity in self.entities:
            node = {
                "id": entity.entity_id,
                "type": entity.entity_type,
                "name": entity.name,
                "description": entity.description,
                "properties": entity.properties,
                "tags": entity.tags,
                "confidence": entity.confidence_score
            }
            graph["nodes"].append(node)

        # Add edges
        for relationship in self.relationships:
            edge = {
                "id": relationship.relationship_id,
                "source": relationship.source_entity_id,
                "target": relationship.target_entity_id,
                "type": relationship.relationship_type,
                "strength": relationship.strength,
                "properties": relationship.properties
            }
            graph["edges"].append(edge)

        return graph

    def _create_ingestion_metadata(self, scan_results: List[ScanResult]) -> Dict[str, Any]:
        """Create metadata for memory ingestion"""
        return {
            "extraction_timestamp": datetime.now().isoformat(),
            "source_files_count": len(scan_results),
            "source_files": [r.metadata.name for r in scan_results],
            "total_size_bytes": sum(r.metadata.size_bytes for r in scan_results),
            "file_types": dict(Counter([r.metadata.file_type for r in scan_results])),
            "extraction_stats": {
                "entities_extracted": len(self.entities),
                "relationships_extracted": len(self.relationships),
                "training_examples_generated": len(self.training_examples)
            },
            "confidence_distribution": {
                "high_confidence": len([e for e in self.entities if e.confidence_score >= 0.8]),
                "medium_confidence": len([e for e in self.entities if 0.5 <= e.confidence_score < 0.8]),
                "low_confidence": len([e for e in self.entities if e.confidence_score < 0.5])
            },
            "recommended_ingestion_order": [
                "schemas",  # High confidence, structured data
                "algorithms",  # Medium confidence, code-derived
                "concepts",  # Medium confidence, extracted
                "best_practices",  # Lower confidence, text-derived
                "data_patterns"  # High confidence, data-derived
            ]
        }

    def export_knowledge(self, output_path: str) -> str:
        """Export extracted knowledge to JSON file"""
        if not self.entities:
            raise ValueError("No knowledge extracted. Run extract_knowledge() first.")

        try:
            # Create extracted knowledge object
            knowledge = ExtractedKnowledge(
                entities=self.entities,
                relationships=self.relationships,
                training_examples=self.training_examples,
                knowledge_graph=self._build_knowledge_graph_structure(),
                ingestion_metadata=self._create_ingestion_metadata([])  # Basic metadata
            )

            # Convert to serializable format
            export_data = asdict(knowledge)

            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Knowledge exported to: {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to export knowledge: {e}")
            raise

    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get a summary of extracted knowledge"""
        if not self.entities:
            return {"error": "No knowledge extracted"}

        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "total_training_examples": len(self.training_examples),
            "entity_types": dict(Counter([e.entity_type for e in self.entities])),
            "relationship_types": dict(Counter([r.relationship_type for r in self.relationships])),
            "example_types": dict(Counter([ex.example_type for ex in self.training_examples])),
            "confidence_scores": {
                "average": sum(e.confidence_score for e in self.entities) / len(self.entities),
                "high_confidence_count": len([e for e in self.entities if e.confidence_score >= 0.8]),
                "medium_confidence_count": len([e for e in self.entities if 0.5 <= e.confidence_score < 0.8]),
                "low_confidence_count": len([e for e in self.entities if e.confidence_score < 0.5])
            }
        }


def main():
    """CLI entry point for knowledge extractor"""
    import argparse

    parser = argparse.ArgumentParser(description="Knowledge Extractor for Phase 24.1")
    parser.add_argument("context_path", help="Path to context directory")
    parser.add_argument("--output", "-o", help="Output file for extracted knowledge")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run complete pipeline: scan -> analyze -> extract
    scanner = ContextScanner(args.context_path)
    scan_results = scanner.scan_directory(recursive=True)

    analyzer = ContentAnalyzer()
    analysis_results = analyzer.analyze_content(scan_results)

    extractor = KnowledgeExtractor()
    extractor.extract_knowledge(scan_results, analysis_results)

    # Print summary
    summary = extractor.get_extraction_summary()
    print("\n📊 Knowledge Extraction Complete!")
    print(f"🎯 Total entities: {summary['total_entities']}")
    print(f"🔗 Total relationships: {summary['total_relationships']}")
    print(f"📚 Total training examples: {summary['total_training_examples']}")
    print(f"📋 Entity types: {summary['entity_types']}")
    print(f"🔗 Relationship types: {summary['relationship_types']}")
    print(f"📈 Average confidence: {summary['confidence_scores']['average']:.2f}")
    print(f"✅ High confidence entities: {summary['confidence_scores']['high_confidence_count']}")

    # Export if requested
    if args.output:
        extractor.export_knowledge(args.output)


if __name__ == "__main__":
    main()
