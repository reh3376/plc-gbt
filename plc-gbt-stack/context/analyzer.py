#!/usr/bin/env python3
"""
🔍 Content Analyzer Module - Phase 24.1 Task 24.1.2

AI Task Orchestrator Implementation for deep content analysis.
Extracts patterns, relationships, and knowledge from scanned context files.

Author: AI Task Orchestrator
Created: 2025-07-15
Phase: 24.1 - Context Discovery & Analysis
"""

import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import the scanner module for data structures
from scanner import DataAnalysis, ScanResult

logger = logging.getLogger(__name__)

@dataclass
class SchemaPattern:
    """Represents a pattern found in control schemas"""
    pattern_type: str
    description: str
    occurrences: int
    schema_files: List[str]
    properties: List[str]
    example_values: Dict[str, Any]

@dataclass
class ControlRelationship:
    """Represents relationships between control elements"""
    source_schema: str
    target_schema: str
    relationship_type: str  # inheritance, composition, dependency
    shared_properties: List[str]
    differences: List[str]
    similarity_score: float

@dataclass
class AlgorithmPattern:
    """Represents algorithm patterns found in code"""
    algorithm_name: str
    function_names: List[str]
    implementation_approach: str
    complexity_level: str
    used_libraries: List[str]
    parameters: List[str]

@dataclass
class KnowledgeGraph:
    """Represents extracted knowledge relationships"""
    concepts: Dict[str, List[str]]  # concept -> related terms
    hierarchies: Dict[str, List[str]]  # parent -> children
    dependencies: Dict[str, List[str]]  # item -> depends on
    best_practices: Dict[str, List[str]]  # area -> practices

@dataclass
class ContentAnalysisResults:
    """Complete content analysis results"""
    schema_patterns: List[SchemaPattern]
    control_relationships: List[ControlRelationship]
    algorithm_patterns: List[AlgorithmPattern]
    knowledge_graph: KnowledgeGraph
    data_insights: Dict[str, Any]
    recommendations: List[str]

class ContentAnalyzer:
    """
    Advanced content analyzer for Phase 24.1

    Performs deep analysis of scan results to extract patterns,
    relationships, and actionable knowledge for memory ingestion.
    """

    def __init__(self):
        self.scan_results: List[ScanResult] = []
        self.analysis_results: Optional[ContentAnalysisResults] = None

        # Pattern recognition templates
        self.control_property_patterns = {
            'pid_params': ['SP', 'PV', 'CV', 'KP', 'KI', 'KD', 'BIAS'],
            'pide_params': ['PGain', 'IGain', 'DGain', 'EGain', 'PVEUMax', 'PVEUMin'],
            'cascade_params': ['CascadeRatio', 'CascadePV', 'CascadeSP'],
            'feedforward_params': ['FFGain', 'FFInput', 'FFBias'],
            'tuning_params': ['TuningMethod', 'AutoTune', 'Manual'],
            'safety_params': ['HighLimit', 'LowLimit', 'AlarmH', 'AlarmL']
        }

        # Algorithm detection patterns
        self.algorithm_signatures = {
            'PID': ['proportional', 'integral', 'derivative', 'setpoint', 'error'],
            'Ziegler_Nichols': ['ultimate_gain', 'ultimate_period', 'oscillation'],
            'Cohen_Coon': ['process_reaction', 'step_response', 'delay_time'],
            'Lambda_Tuning': ['closed_loop_time_constant', 'lambda'],
            'IMC': ['internal_model', 'controller_design'],
            'MPC': ['model_predictive', 'optimization', 'constraints'],
            'Adaptive': ['parameter_estimation', 'self_tuning', 'recursive']
        }

        logger.info("ContentAnalyzer initialized")

    def analyze_content(self, scan_results: List[ScanResult]) -> ContentAnalysisResults:
        """
        Perform comprehensive content analysis on scan results

        Args:
            scan_results: List of scan results from ContextScanner

        Returns:
            Complete analysis results with patterns and relationships
        """
        logger.info(f"🔍 Starting content analysis on {len(scan_results)} scan results")

        self.scan_results = scan_results

        # Perform different types of analysis
        schema_patterns = self._analyze_schema_patterns()
        control_relationships = self._analyze_control_relationships()
        algorithm_patterns = self._analyze_algorithm_patterns()
        knowledge_graph = self._build_knowledge_graph()
        data_insights = self._analyze_data_insights()
        recommendations = self._generate_recommendations()

        self.analysis_results = ContentAnalysisResults(
            schema_patterns=schema_patterns,
            control_relationships=control_relationships,
            algorithm_patterns=algorithm_patterns,
            knowledge_graph=knowledge_graph,
            data_insights=data_insights,
            recommendations=recommendations
        )

        logger.info("✅ Content analysis complete")
        return self.analysis_results

    def _analyze_schema_patterns(self) -> List[SchemaPattern]:
        """Analyze patterns across JSON schemas"""
        logger.info("📋 Analyzing schema patterns")

        patterns = []
        schema_results = [r for r in self.scan_results if r.schema_analysis]

        if not schema_results:
            return patterns

        # Group schemas by control type and complexity
        type_groups = defaultdict(list)
        complexity_groups = defaultdict(list)

        for result in schema_results:
            schema = result.schema_analysis
            type_groups[schema.control_type].append(result)
            complexity_groups[schema.complexity_level].append(result)

        # Analyze property patterns
        property_patterns = self._find_property_patterns(schema_results)
        patterns.extend(property_patterns)

        # Analyze complexity evolution patterns
        complexity_patterns = self._find_complexity_patterns(complexity_groups)
        patterns.extend(complexity_patterns)

        # Analyze control type patterns
        type_patterns = self._find_type_patterns(type_groups)
        patterns.extend(type_patterns)

        logger.info(f"📊 Found {len(patterns)} schema patterns")
        return patterns

    def _find_property_patterns(self, schema_results: List[ScanResult]) -> List[SchemaPattern]:
        """Find common property patterns across schemas"""
        patterns = []

        # Load actual schema content to analyze properties
        all_properties = defaultdict(list)

        for result in schema_results:
            try:
                with open(result.metadata.path) as f:
                    schema_data = json.load(f)
                    properties = schema_data.get('properties', {})

                    for prop_name, prop_def in properties.items():
                        all_properties[prop_name].append({
                            'schema': result.metadata.name,
                            'definition': prop_def,
                            'type': prop_def.get('type', 'unknown'),
                            'description': prop_def.get('description', '')
                        })
            except Exception as e:
                logger.warning(f"Failed to load schema {result.metadata.path}: {e}")

        # Find common properties
        for prop_name, occurrences in all_properties.items():
            if len(occurrences) >= 2:  # Property appears in at least 2 schemas
                schema_files = [occ['schema'] for occ in occurrences]
                prop_types = [occ['type'] for occ in occurrences]

                # Determine pattern type
                pattern_type = "common_property"
                if len(set(prop_types)) == 1:
                    pattern_type = "consistent_property"

                patterns.append(SchemaPattern(
                    pattern_type=pattern_type,
                    description=f"Property '{prop_name}' appears across multiple schemas",
                    occurrences=len(occurrences),
                    schema_files=schema_files,
                    properties=[prop_name],
                    example_values={'types': list(set(prop_types))}
                ))

        return patterns

    def _find_complexity_patterns(self, complexity_groups: Dict[str, List[ScanResult]]) -> List[SchemaPattern]:
        """Find patterns in complexity evolution"""
        patterns = []

        # Analyze property count progression
        complexity_order = ['Standard', 'Advanced', 'Advanced_Feedforward', 'Advanced_Cascade', 'Advanced_Cascade_Feedforward']
        property_counts = {}

        for complexity in complexity_order:
            if complexity in complexity_groups:
                counts = [r.schema_analysis.property_count for r in complexity_groups[complexity]]
                property_counts[complexity] = {
                    'avg': sum(counts) / len(counts),
                    'min': min(counts),
                    'max': max(counts),
                    'count': len(counts)
                }

        if len(property_counts) >= 2:
            patterns.append(SchemaPattern(
                pattern_type="complexity_progression",
                description="Property count increases with complexity level",
                occurrences=sum(data['count'] for data in property_counts.values()),
                schema_files=[],
                properties=[],
                example_values=property_counts
            ))

        return patterns

    def _find_type_patterns(self, type_groups: Dict[str, List[ScanResult]]) -> List[SchemaPattern]:
        """Find patterns within control types"""
        patterns = []

        for control_type, results in type_groups.items():
            if len(results) >= 2:
                # Analyze common properties within type
                common_props = self._find_common_properties_in_group(results)

                if common_props:
                    patterns.append(SchemaPattern(
                        pattern_type=f"{control_type.lower()}_pattern",
                        description=f"Common properties in {control_type} controllers",
                        occurrences=len(results),
                        schema_files=[r.metadata.name for r in results],
                        properties=common_props,
                        example_values={'control_type': control_type}
                    ))

        return patterns

    def _find_common_properties_in_group(self, results: List[ScanResult]) -> List[str]:
        """Find properties common to all schemas in a group"""
        if not results:
            return []

        property_sets = []
        for result in results:
            try:
                with open(result.metadata.path) as f:
                    schema_data = json.load(f)
                    properties = set(schema_data.get('properties', {}).keys())
                    property_sets.append(properties)
            except Exception:
                continue

        if not property_sets:
            return []

        # Find intersection of all property sets
        common_props = property_sets[0]
        for prop_set in property_sets[1:]:
            common_props &= prop_set

        return list(common_props)

    def _analyze_control_relationships(self) -> List[ControlRelationship]:
        """Analyze relationships between different control configurations"""
        logger.info("🔗 Analyzing control relationships")

        relationships = []
        schema_results = [r for r in self.scan_results if r.schema_analysis]

        # Compare each pair of schemas
        for i, result1 in enumerate(schema_results):
            for result2 in schema_results[i+1:]:
                relationship = self._compare_schemas(result1, result2)
                if relationship:
                    relationships.append(relationship)

        logger.info(f"🔗 Found {len(relationships)} control relationships")
        return relationships

    def _compare_schemas(self, result1: ScanResult, result2: ScanResult) -> Optional[ControlRelationship]:
        """Compare two schemas and identify their relationship"""
        try:
            # Load both schemas
            with open(result1.metadata.path) as f:
                schema1 = json.load(f)
            with open(result2.metadata.path) as f:
                schema2 = json.load(f)

            props1 = set(schema1.get('properties', {}).keys())
            props2 = set(schema2.get('properties', {}).keys())

            # Calculate similarity
            intersection = props1 & props2
            union = props1 | props2
            similarity_score = len(intersection) / len(union) if union else 0

            # Determine relationship type
            relationship_type = "similarity"
            if props1.issubset(props2):
                relationship_type = "extends"  # result2 extends result1
            elif props2.issubset(props1):
                relationship_type = "extends"  # result1 extends result2
            elif similarity_score > 0.7:
                relationship_type = "variant"
            elif similarity_score > 0.3:
                relationship_type = "related"

            # Only create relationship if significant
            if similarity_score > 0.3:
                return ControlRelationship(
                    source_schema=result1.metadata.name,
                    target_schema=result2.metadata.name,
                    relationship_type=relationship_type,
                    shared_properties=list(intersection),
                    differences=list((props1 | props2) - intersection),
                    similarity_score=similarity_score
                )

        except Exception as e:
            logger.warning(f"Failed to compare schemas: {e}")

        return None

    def _analyze_algorithm_patterns(self) -> List[AlgorithmPattern]:
        """Analyze algorithm patterns in code files"""
        logger.info("🧮 Analyzing algorithm patterns")

        patterns = []
        code_results = [r for r in self.scan_results if r.code_analysis]

        for result in code_results:
            code_analysis = result.code_analysis

            # Analyze each identified algorithm
            for algorithm in code_analysis.control_algorithms:
                pattern = self._analyze_algorithm_implementation(result, algorithm)
                if pattern:
                    patterns.append(pattern)

        logger.info(f"🧮 Found {len(patterns)} algorithm patterns")
        return patterns

    def _analyze_algorithm_implementation(self, result: ScanResult, algorithm: str) -> Optional[AlgorithmPattern]:
        """Analyze how a specific algorithm is implemented"""
        try:
            with open(result.metadata.path) as f:
                content = f.read()

            # Find functions related to this algorithm
            related_functions = []
            for func_name in result.code_analysis.functions:
                if algorithm.lower().replace('-', '_') in func_name.lower():
                    related_functions.append(func_name)

            # Analyze implementation approach
            implementation_approach = self._determine_implementation_approach(content, algorithm)

            # Determine complexity
            complexity_level = "basic"
            if result.code_analysis.complexity_score > 50:
                complexity_level = "advanced"
            elif result.code_analysis.complexity_score > 20:
                complexity_level = "intermediate"

            # Extract parameters
            parameters = self._extract_algorithm_parameters(content, algorithm)

            return AlgorithmPattern(
                algorithm_name=algorithm,
                function_names=related_functions,
                implementation_approach=implementation_approach,
                complexity_level=complexity_level,
                used_libraries=result.code_analysis.imports[:5],  # Top 5 imports
                parameters=parameters
            )

        except Exception as e:
            logger.warning(f"Failed to analyze algorithm {algorithm}: {e}")

        return None

    def _determine_implementation_approach(self, content: str, algorithm: str) -> str:
        """Determine how an algorithm is implemented"""
        content_lower = content.lower()

        if 'numpy' in content_lower or 'scipy' in content_lower:
            return "numerical_library"
        elif 'class' in content_lower and algorithm.lower() in content_lower:
            return "object_oriented"
        elif 'def ' in content_lower:
            return "functional"
        else:
            return "procedural"

    def _extract_algorithm_parameters(self, content: str, algorithm: str) -> List[str]:
        """Extract parameters used by an algorithm"""
        parameters = []

        # Look for common parameter patterns in the content
        param_patterns = {
            'PID': ['kp', 'ki', 'kd', 'setpoint', 'process_variable', 'output'],
            'Ziegler-Nichols': ['ku', 'tu', 'ultimate_gain', 'ultimate_period'],
            'Cohen-Coon': ['k', 'tau', 'theta', 'gain', 'time_constant', 'delay']
        }

        if algorithm in param_patterns:
            for param in param_patterns[algorithm]:
                if param.lower() in content.lower():
                    parameters.append(param)

        return parameters

    def _build_knowledge_graph(self) -> KnowledgeGraph:
        """Build knowledge graph from all analyzed content"""
        logger.info("🕸️ Building knowledge graph")

        concepts = defaultdict(list)
        hierarchies = defaultdict(list)
        dependencies = defaultdict(list)
        best_practices = defaultdict(list)

        # Extract concepts from schemas
        schema_results = [r for r in self.scan_results if r.schema_analysis]
        for result in schema_results:
            schema = result.schema_analysis
            control_type = schema.control_type

            # Add to hierarchies
            if schema.complexity_level != 'Standard':
                hierarchies[control_type].append(schema.complexity_level)

            # Add concepts
            concepts[control_type].append(schema.title)

        # Extract concepts from documents
        doc_results = [r for r in self.scan_results if r.document_analysis]
        for result in doc_results:
            doc = result.document_analysis

            # Add control concepts
            for concept in doc.control_concepts:
                concepts['control_concepts'].append(concept)

            # Add best practices
            for practice in doc.best_practices:
                best_practices['general'].append(practice)

        # Extract dependencies from code
        code_results = [r for r in self.scan_results if r.code_analysis]
        for result in code_results:
            code = result.code_analysis

            # Add algorithm dependencies
            for algorithm in code.control_algorithms:
                dependencies[algorithm] = code.imports[:3]  # Top 3 dependencies

        return KnowledgeGraph(
            concepts=dict(concepts),
            hierarchies=dict(hierarchies),
            dependencies=dict(dependencies),
            best_practices=dict(best_practices)
        )

    def _analyze_data_insights(self) -> Dict[str, Any]:
        """Analyze insights from data files"""
        logger.info("📊 Analyzing data insights")

        insights = {}
        data_results = [r for r in self.scan_results if r.data_analysis]

        for result in data_results:
            data = result.data_analysis
            file_name = result.metadata.name

            insights[file_name] = {
                'size': f"{data.row_count} rows x {data.column_count} columns",
                'control_variables': data.control_variables,
                'data_types': data.data_types,
                'potential_use_cases': self._suggest_data_use_cases(data)
            }

        return insights

    def _suggest_data_use_cases(self, data: DataAnalysis) -> List[str]:
        """Suggest potential use cases for data"""
        use_cases = []

        if len(data.control_variables) > 0:
            use_cases.append("Control loop training data")
            use_cases.append("Process parameter analysis")

        if data.row_count > 1000:
            use_cases.append("Time series analysis")
            use_cases.append("Model training dataset")

        if any('temp' in col.lower() for col in data.columns):
            use_cases.append("Temperature control optimization")

        if any('pressure' in col.lower() for col in data.columns):
            use_cases.append("Pressure control tuning")

        return use_cases

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        logger.info("💡 Generating recommendations")

        recommendations = []

        if not self.scan_results:
            return recommendations

        # Count different types of content
        schema_count = len([r for r in self.scan_results if r.schema_analysis])
        code_count = len([r for r in self.scan_results if r.code_analysis])
        doc_count = len([r for r in self.scan_results if r.document_analysis])
        data_count = len([r for r in self.scan_results if r.data_analysis])

        # Schema recommendations
        if schema_count > 0:
            recommendations.append(f"Found {schema_count} control schemas - excellent foundation for Phase 20 JSON Schema Framework")

            # Check for schema completeness
            control_types = set()
            complexity_levels = set()
            for r in self.scan_results:
                if r.schema_analysis:
                    control_types.add(r.schema_analysis.control_type)
                    complexity_levels.add(r.schema_analysis.complexity_level)

            if len(control_types) >= 2:
                recommendations.append(f"Multiple control types ({', '.join(control_types)}) - good coverage for comprehensive system")

            if len(complexity_levels) >= 3:
                recommendations.append("Multiple complexity levels - enables progressive learning approach")

        # Code recommendations
        if code_count > 0:
            recommendations.append(f"Found {code_count} code files - valuable for Phase 22 Analysis Engine implementation")

            # Check for algorithm diversity
            all_algorithms = set()
            for r in self.scan_results:
                if r.code_analysis:
                    all_algorithms.update(r.code_analysis.control_algorithms)

            if len(all_algorithms) >= 3:
                recommendations.append(f"Multiple algorithms detected ({', '.join(all_algorithms)}) - rich foundation for analysis capabilities")

        # Documentation recommendations
        if doc_count > 0:
            recommendations.append(f"Found {doc_count} documentation files - excellent for Phase 24.3 training data generation")

            # Check for best practices
            total_practices = 0
            for r in self.scan_results:
                if r.document_analysis:
                    total_practices += len(r.document_analysis.best_practices)

            if total_practices >= 10:
                recommendations.append(f"Rich best practices content ({total_practices} practices) - ideal for Q&A dataset creation")

        # Data recommendations
        if data_count > 0:
            recommendations.append(f"Found {data_count} data files - valuable for model training and validation")

            for r in self.scan_results:
                if r.data_analysis and r.data_analysis.row_count > 10000:
                    recommendations.append(f"Large dataset detected ({r.metadata.name}) - suitable for advanced model training")

        # Integration recommendations
        if schema_count > 0 and code_count > 0:
            recommendations.append("Schema + Code combination - perfect for Phase 21 CLI implementation validation")

        if doc_count > 0 and data_count > 0:
            recommendations.append("Documentation + Data combination - excellent for Phase 23 LLM training enhancement")

        # Priority recommendations
        if len(recommendations) >= 5:
            recommendations.append("🚀 PRIORITY: This context directory is exceptionally rich - recommend immediate Phase 24.2 memory ingestion")

        return recommendations

    def export_analysis(self, output_path: str) -> str:
        """Export analysis results to JSON file"""
        if not self.analysis_results:
            raise ValueError("No analysis results available. Run analyze_content() first.")

        try:
            # Convert to serializable format
            export_data = {
                "analysis_timestamp": datetime.now().isoformat(),
                "total_scan_results": len(self.scan_results),
                "analysis_results": asdict(self.analysis_results)
            }

            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Analysis results exported to: {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to export analysis results: {e}")
            raise

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results"""
        if not self.analysis_results:
            return {"error": "No analysis results available"}

        results = self.analysis_results

        return {
            "schema_patterns": len(results.schema_patterns),
            "control_relationships": len(results.control_relationships),
            "algorithm_patterns": len(results.algorithm_patterns),
            "knowledge_concepts": len(results.knowledge_graph.concepts),
            "data_insights": len(results.data_insights),
            "recommendations": len(results.recommendations),
            "top_recommendations": results.recommendations[:3]
        }


def main():
    """CLI entry point for content analyzer"""
    import argparse

    from scanner import ContextScanner

    parser = argparse.ArgumentParser(description="Content Analyzer for Phase 24.1")
    parser.add_argument("context_path", help="Path to context directory")
    parser.add_argument("--output", "-o", help="Output file for analysis results")
    parser.add_argument("--scan-output", help="Output file from previous context scan")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Load scan results
    if args.scan_output:
        # Load from previous scan
        with open(args.scan_output) as f:
            json.load(f)

        # TODO: Convert back to ScanResult objects
        print("Loading from previous scan not yet implemented")
        return
    else:
        # Run scanner first
        scanner = ContextScanner(args.context_path)
        scan_results = scanner.scan_directory(recursive=True)

    # Run content analysis
    analyzer = ContentAnalyzer()
    analyzer.analyze_content(scan_results)

    # Print summary
    summary = analyzer.get_analysis_summary()
    print("\n📊 Content Analysis Complete!")
    print(f"📋 Schema patterns: {summary['schema_patterns']}")
    print(f"🔗 Control relationships: {summary['control_relationships']}")
    print(f"🧮 Algorithm patterns: {summary['algorithm_patterns']}")
    print(f"🕸️ Knowledge concepts: {summary['knowledge_concepts']}")
    print(f"📊 Data insights: {summary['data_insights']}")
    print(f"💡 Recommendations: {summary['recommendations']}")

    if summary['top_recommendations']:
        print("\n🚀 Top Recommendations:")
        for i, rec in enumerate(summary['top_recommendations'], 1):
            print(f"   {i}. {rec}")

    # Export results if requested
    if args.output:
        analyzer.export_analysis(args.output)


if __name__ == "__main__":
    main()
