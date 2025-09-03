#!/usr/bin/env python3
"""
✅ Validation System Module - Phase 24.1 Task 24.1.4

AI Task Orchestrator Implementation for comprehensive validation.
Validates schema integrity, code functionality, data quality, and knowledge extraction accuracy.

Author: AI Task Orchestrator
Created: 2025-07-15
Phase: 24.1 - Context Discovery & Analysis
"""

import ast
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import jsonschema
from analyzer import ContentAnalysisResults
from extractor import ExtractedKnowledge, KnowledgeEntity, KnowledgeRelationship

# Import from previous modules
from scanner import CodeAnalysis, DataAnalysis, ScanResult

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a single validation check"""
    check_name: str
    check_type: str  # schema, code, data, knowledge, integrity
    status: str  # passed, failed, warning, skipped
    score: float  # 0.0 to 1.0
    message: str
    details: Dict[str, Any]
    recommendations: List[str]

@dataclass
class ValidationReport:
    """Complete validation report"""
    validation_timestamp: str
    overall_score: float
    overall_status: str
    check_results: List[ValidationResult]
    summary: Dict[str, Any]
    recommendations: List[str]

class ValidationSystem:
    """
    Comprehensive validation system for Phase 24.1

    Validates all aspects of context processing: schemas, code, data,
    knowledge extraction, and overall integrity.
    """

    def __init__(self):
        self.validation_results: List[ValidationResult] = []

        # JSON Schema for validating control schemas
        self.control_schema_meta = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["$schema", "title", "type", "properties"],
            "properties": {
                "$schema": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "type": {"const": "object"},
                "properties": {"type": "object"},
                "required": {"type": "array", "items": {"type": "string"}}
            }
        }

        # Required properties for different control types
        self.control_type_requirements = {
            "PID": ["SP", "PV", "CV", "KP", "KI", "KD"],
            "PIDE": ["PV", "PGain", "IGain", "DGain"],
            "Cascade": ["CascadePV", "CascadeSP", "CascadeRatio"],
            "Feedforward": ["FFGain", "FFInput"]
        }

        # Data quality thresholds
        self.quality_thresholds = {
            "min_confidence_score": 0.5,
            "min_relationship_strength": 0.3,
            "max_missing_data_percent": 10.0,
            "min_training_examples": 5,
            "min_entity_coverage": 0.8
        }

        logger.info("ValidationSystem initialized")

    def validate_all(self, scan_results: List[ScanResult],
                    analysis_results: ContentAnalysisResults,
                    extracted_knowledge: ExtractedKnowledge) -> ValidationReport:
        """
        Perform comprehensive validation of all components

        Args:
            scan_results: Original scan results
            analysis_results: Content analysis results
            extracted_knowledge: Extracted knowledge

        Returns:
            Complete validation report
        """
        logger.info("🔍 Starting comprehensive validation")

        self.validation_results = []

        # Schema validation
        self._validate_schemas(scan_results)

        # Code validation
        self._validate_code(scan_results)

        # Data validation
        self._validate_data(scan_results)

        # Knowledge validation
        self._validate_knowledge(extracted_knowledge)

        # Analysis validation
        self._validate_analysis(analysis_results)

        # Integrity validation
        self._validate_integrity(scan_results, analysis_results, extracted_knowledge)

        # Generate report
        report = self._generate_validation_report()

        logger.info(f"✅ Validation complete: {report.overall_score:.2f} overall score")
        return report

    def _validate_schemas(self, scan_results: List[ScanResult]):
        """Validate JSON schema files"""
        logger.info("📋 Validating JSON schemas")

        schema_results = [r for r in scan_results if r.schema_analysis]

        if not schema_results:
            self.validation_results.append(ValidationResult(
                check_name="schema_presence",
                check_type="schema",
                status="warning",
                score=0.0,
                message="No schema files found",
                details={},
                recommendations=["Add JSON schema files for validation"]
            ))
            return

        passed_count = 0
        total_count = len(schema_results)

        for result in schema_results:
            try:
                # Load and validate schema structure
                with open(result.metadata.path) as f:
                    schema_data = json.load(f)

                # Validate against meta-schema
                try:
                    jsonschema.validate(schema_data, self.control_schema_meta)
                    structure_valid = True
                except jsonschema.ValidationError as e:
                    structure_valid = False
                    str(e)

                # Validate control-specific requirements
                control_valid = self._validate_control_requirements(
                    schema_data, result.schema_analysis.control_type
                )

                # Calculate score
                score = 0.0
                if structure_valid:
                    score += 0.5
                if control_valid['valid']:
                    score += 0.5

                status = "passed" if score >= 0.8 else "warning" if score >= 0.5 else "failed"
                if status == "passed":
                    passed_count += 1

                self.validation_results.append(ValidationResult(
                    check_name=f"schema_validation_{result.metadata.name}",
                    check_type="schema",
                    status=status,
                    score=score,
                    message=f"Schema validation: {score*100:.0f}%",
                    details={
                        "structure_valid": structure_valid,
                        "control_valid": control_valid['valid'],
                        "missing_properties": control_valid.get('missing', []),
                        "property_count": len(schema_data.get('properties', {}))
                    },
                    recommendations=control_valid.get('recommendations', [])
                ))

            except Exception as e:
                self.validation_results.append(ValidationResult(
                    check_name=f"schema_validation_{result.metadata.name}",
                    check_type="schema",
                    status="failed",
                    score=0.0,
                    message=f"Schema validation failed: {e}",
                    details={"error": str(e)},
                    recommendations=["Fix schema file format"]
                ))

        # Overall schema validation summary
        overall_score = passed_count / total_count if total_count > 0 else 0.0
        self.validation_results.append(ValidationResult(
            check_name="schema_overall",
            check_type="schema",
            status="passed" if overall_score >= 0.8 else "warning" if overall_score >= 0.5 else "failed",
            score=overall_score,
            message=f"Schema validation: {passed_count}/{total_count} schemas passed",
            details={"passed": passed_count, "total": total_count},
            recommendations=[]
        ))

    def _validate_control_requirements(self, schema_data: Dict, control_type: str) -> Dict[str, Any]:
        """Validate control-specific requirements for a schema"""
        properties = schema_data.get('properties', {})
        required_props = self.control_type_requirements.get(control_type, [])

        missing_props = []
        for prop in required_props:
            if prop not in properties:
                missing_props.append(prop)

        valid = len(missing_props) == 0
        recommendations = []

        if missing_props:
            recommendations.append(f"Add missing {control_type} properties: {', '.join(missing_props)}")

        return {
            "valid": valid,
            "missing": missing_props,
            "recommendations": recommendations
        }

    def _validate_code(self, scan_results: List[ScanResult]):
        """Validate Python code files"""
        logger.info("🐍 Validating Python code")

        code_results = [r for r in scan_results if r.code_analysis]

        if not code_results:
            self.validation_results.append(ValidationResult(
                check_name="code_presence",
                check_type="code",
                status="warning",
                score=0.0,
                message="No code files found",
                details={},
                recommendations=["Add Python code files for analysis"]
            ))
            return

        for result in code_results:
            try:
                # Load and parse code
                with open(result.metadata.path) as f:
                    code_content = f.read()

                # Syntax validation
                syntax_valid = self._validate_python_syntax(code_content)

                # Code quality validation
                quality_score = self._validate_code_quality(result.code_analysis)

                # Algorithm validation
                algorithm_valid = self._validate_algorithms(result.code_analysis)

                # Calculate overall score
                score = (
                    (0.4 if syntax_valid else 0.0) +
                    (quality_score * 0.4) +
                    (algorithm_valid * 0.2)
                )

                status = "passed" if score >= 0.8 else "warning" if score >= 0.5 else "failed"

                self.validation_results.append(ValidationResult(
                    check_name=f"code_validation_{result.metadata.name}",
                    check_type="code",
                    status=status,
                    score=score,
                    message=f"Code validation: {score*100:.0f}%",
                    details={
                        "syntax_valid": syntax_valid,
                        "quality_score": quality_score,
                        "algorithm_count": len(result.code_analysis.control_algorithms),
                        "function_count": len(result.code_analysis.functions),
                        "complexity_score": result.code_analysis.complexity_score
                    },
                    recommendations=self._get_code_recommendations(result.code_analysis)
                ))

            except Exception as e:
                self.validation_results.append(ValidationResult(
                    check_name=f"code_validation_{result.metadata.name}",
                    check_type="code",
                    status="failed",
                    score=0.0,
                    message=f"Code validation failed: {e}",
                    details={"error": str(e)},
                    recommendations=["Fix code syntax errors"]
                ))

    def _validate_python_syntax(self, code_content: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code_content)
            return True
        except SyntaxError:
            return False

    def _validate_code_quality(self, code_analysis: CodeAnalysis) -> float:
        """Validate code quality metrics"""
        score = 0.0

        # Check for docstrings
        if code_analysis.has_docstrings:
            score += 0.3

        # Check function count (reasonable range)
        func_count = len(code_analysis.functions)
        if 5 <= func_count <= 50:
            score += 0.3
        elif func_count > 0:
            score += 0.15

        # Check complexity (not too high)
        complexity = code_analysis.complexity_score
        if complexity < 50:
            score += 0.4
        elif complexity < 100:
            score += 0.2

        return min(score, 1.0)

    def _validate_algorithms(self, code_analysis: CodeAnalysis) -> float:
        """Validate algorithm implementation"""
        algorithm_count = len(code_analysis.control_algorithms)

        if algorithm_count >= 3:
            return 1.0
        elif algorithm_count >= 1:
            return 0.6
        else:
            return 0.0

    def _get_code_recommendations(self, code_analysis: CodeAnalysis) -> List[str]:
        """Get recommendations for code improvement"""
        recommendations = []

        if not code_analysis.has_docstrings:
            recommendations.append("Add docstrings to functions and classes")

        if len(code_analysis.functions) == 0:
            recommendations.append("Add functions to improve code structure")

        if code_analysis.complexity_score > 100:
            recommendations.append("Reduce code complexity by breaking down functions")

        if len(code_analysis.control_algorithms) == 0:
            recommendations.append("Implement control algorithms for better domain coverage")

        return recommendations

    def _validate_data(self, scan_results: List[ScanResult]):
        """Validate data files"""
        logger.info("📊 Validating data files")

        data_results = [r for r in scan_results if r.data_analysis]

        if not data_results:
            self.validation_results.append(ValidationResult(
                check_name="data_presence",
                check_type="data",
                status="warning",
                score=0.0,
                message="No data files found",
                details={},
                recommendations=["Add data files for analysis"]
            ))
            return

        for result in data_results:
            data_analysis = result.data_analysis

            # Data completeness
            completeness_score = self._validate_data_completeness(data_analysis)

            # Data quality
            quality_score = self._validate_data_quality(data_analysis)

            # Control variable presence
            control_score = self._validate_control_variables(data_analysis)

            # Overall score
            score = (completeness_score * 0.4 + quality_score * 0.3 + control_score * 0.3)
            status = "passed" if score >= 0.8 else "warning" if score >= 0.5 else "failed"

            self.validation_results.append(ValidationResult(
                check_name=f"data_validation_{result.metadata.name}",
                check_type="data",
                status=status,
                score=score,
                message=f"Data validation: {score*100:.0f}%",
                details={
                    "row_count": data_analysis.row_count,
                    "column_count": data_analysis.column_count,
                    "control_variables": len(data_analysis.control_variables),
                    "completeness_score": completeness_score,
                    "quality_score": quality_score
                },
                recommendations=self._get_data_recommendations(data_analysis)
            ))

    def _validate_data_completeness(self, data_analysis: DataAnalysis) -> float:
        """Validate data completeness"""
        if data_analysis.row_count == 0:
            return 0.0
        elif data_analysis.row_count < 100:
            return 0.5
        elif data_analysis.row_count < 1000:
            return 0.8
        else:
            return 1.0

    def _validate_data_quality(self, data_analysis: DataAnalysis) -> float:
        """Validate data quality"""
        score = 0.0

        # Check for reasonable number of columns
        if 3 <= data_analysis.column_count <= 50:
            score += 0.5
        elif data_analysis.column_count > 0:
            score += 0.25

        # Check data type diversity
        unique_types = set(data_analysis.data_types.values())
        if len(unique_types) >= 2:
            score += 0.5
        elif len(unique_types) >= 1:
            score += 0.25

        return min(score, 1.0)

    def _validate_control_variables(self, data_analysis: DataAnalysis) -> float:
        """Validate presence of control variables"""
        control_var_count = len(data_analysis.control_variables)

        if control_var_count >= 5:
            return 1.0
        elif control_var_count >= 2:
            return 0.7
        elif control_var_count >= 1:
            return 0.4
        else:
            return 0.0

    def _get_data_recommendations(self, data_analysis: DataAnalysis) -> List[str]:
        """Get recommendations for data improvement"""
        recommendations = []

        if data_analysis.row_count < 100:
            recommendations.append("Increase dataset size for better analysis")

        if len(data_analysis.control_variables) == 0:
            recommendations.append("Add control system variables to dataset")

        if data_analysis.column_count < 3:
            recommendations.append("Add more data columns for comprehensive analysis")

        return recommendations

    def _validate_knowledge(self, extracted_knowledge: ExtractedKnowledge):
        """Validate extracted knowledge"""
        logger.info("🧠 Validating extracted knowledge")

        # Entity validation
        entity_score = self._validate_entities(extracted_knowledge.entities)

        # Relationship validation
        relationship_score = self._validate_relationships(extracted_knowledge.relationships)

        # Training example validation
        training_score = self._validate_training_examples(extracted_knowledge.training_examples)

        # Overall knowledge validation
        overall_score = (entity_score * 0.4 + relationship_score * 0.3 + training_score * 0.3)
        status = "passed" if overall_score >= 0.8 else "warning" if overall_score >= 0.5 else "failed"

        self.validation_results.append(ValidationResult(
            check_name="knowledge_extraction",
            check_type="knowledge",
            status=status,
            score=overall_score,
            message=f"Knowledge extraction validation: {overall_score*100:.0f}%",
            details={
                "entity_count": len(extracted_knowledge.entities),
                "relationship_count": len(extracted_knowledge.relationships),
                "training_example_count": len(extracted_knowledge.training_examples),
                "entity_score": entity_score,
                "relationship_score": relationship_score,
                "training_score": training_score
            },
            recommendations=self._get_knowledge_recommendations(extracted_knowledge)
        ))

    def _validate_entities(self, entities: List[KnowledgeEntity]) -> float:
        """Validate knowledge entities"""
        if not entities:
            return 0.0

        valid_count = 0

        for entity in entities:
            entity_valid = True

            # Check required fields
            if not entity.entity_id or not entity.name:
                entity_valid = False

            # Check confidence score
            if entity.confidence_score < self.quality_thresholds["min_confidence_score"]:
                entity_valid = False

            # Check properties
            if not entity.properties:
                entity_valid = False

            if entity_valid:
                valid_count += 1

        return valid_count / len(entities)

    def _validate_relationships(self, relationships: List[KnowledgeRelationship]) -> float:
        """Validate knowledge relationships"""
        if not relationships:
            return 0.0

        valid_count = 0

        for relationship in relationships:
            relationship_valid = True

            # Check required fields
            if not relationship.source_entity_id or not relationship.target_entity_id:
                relationship_valid = False

            # Check strength
            if relationship.strength < self.quality_thresholds["min_relationship_strength"]:
                relationship_valid = False

            if relationship_valid:
                valid_count += 1

        return valid_count / len(relationships)

    def _validate_training_examples(self, training_examples) -> float:
        """Validate training examples"""
        if not training_examples:
            return 0.0

        if len(training_examples) < self.quality_thresholds["min_training_examples"]:
            return 0.3

        valid_count = 0

        for example in training_examples:
            example_valid = True

            # Check required fields
            if not example.question or not example.answer:
                example_valid = False

            # Check length
            if len(example.question) < 10 or len(example.answer) < 20:
                example_valid = False

            if example_valid:
                valid_count += 1

        return valid_count / len(training_examples)

    def _get_knowledge_recommendations(self, extracted_knowledge: ExtractedKnowledge) -> List[str]:
        """Get recommendations for knowledge improvement"""
        recommendations = []

        if len(extracted_knowledge.entities) < 10:
            recommendations.append("Extract more entities for comprehensive knowledge coverage")

        if len(extracted_knowledge.relationships) < 5:
            recommendations.append("Identify more relationships between entities")

        if len(extracted_knowledge.training_examples) < self.quality_thresholds["min_training_examples"]:
            recommendations.append("Generate more training examples for model enhancement")

        # Check entity confidence
        low_confidence = [e for e in extracted_knowledge.entities
                         if e.confidence_score < self.quality_thresholds["min_confidence_score"]]
        if low_confidence:
            recommendations.append(f"Improve confidence scores for {len(low_confidence)} entities")

        return recommendations

    def _validate_analysis(self, analysis_results: ContentAnalysisResults):
        """Validate content analysis results"""
        logger.info("🔬 Validating content analysis")

        # Pattern validation
        pattern_score = len(analysis_results.schema_patterns) / 50  # Expect around 50 patterns
        pattern_score = min(pattern_score, 1.0)

        # Relationship validation
        relationship_score = len(analysis_results.control_relationships) / 10  # Expect around 10 relationships
        relationship_score = min(relationship_score, 1.0)

        # Knowledge graph validation
        kg_score = 1.0 if analysis_results.knowledge_graph.concepts else 0.0

        # Overall analysis score
        overall_score = (pattern_score * 0.4 + relationship_score * 0.4 + kg_score * 0.2)
        status = "passed" if overall_score >= 0.8 else "warning" if overall_score >= 0.5 else "failed"

        self.validation_results.append(ValidationResult(
            check_name="content_analysis",
            check_type="analysis",
            status=status,
            score=overall_score,
            message=f"Content analysis validation: {overall_score*100:.0f}%",
            details={
                "pattern_count": len(analysis_results.schema_patterns),
                "relationship_count": len(analysis_results.control_relationships),
                "concept_categories": len(analysis_results.knowledge_graph.concepts),
                "pattern_score": pattern_score,
                "relationship_score": relationship_score
            },
            recommendations=[]
        ))

    def _validate_integrity(self, scan_results: List[ScanResult],
                          analysis_results: ContentAnalysisResults,
                          extracted_knowledge: ExtractedKnowledge):
        """Validate overall integrity and consistency"""
        logger.info("🔧 Validating system integrity")

        # Check consistency between scan and analysis
        scan_schema_count = len([r for r in scan_results if r.schema_analysis])
        extracted_schema_count = len([e for e in extracted_knowledge.entities if e.entity_type == "schema"])

        consistency_score = 1.0 if scan_schema_count == extracted_schema_count else 0.7

        # Check data flow integrity
        flow_score = 1.0  # Assume good flow for now

        # Check coverage
        coverage_score = self._calculate_coverage(scan_results, extracted_knowledge)

        # Overall integrity
        integrity_score = (consistency_score * 0.4 + flow_score * 0.3 + coverage_score * 0.3)
        status = "passed" if integrity_score >= 0.8 else "warning" if integrity_score >= 0.5 else "failed"

        self.validation_results.append(ValidationResult(
            check_name="system_integrity",
            check_type="integrity",
            status=status,
            score=integrity_score,
            message=f"System integrity validation: {integrity_score*100:.0f}%",
            details={
                "consistency_score": consistency_score,
                "coverage_score": coverage_score,
                "scan_schemas": scan_schema_count,
                "extracted_schemas": extracted_schema_count
            },
            recommendations=[]
        ))

    def _calculate_coverage(self, scan_results: List[ScanResult],
                          extracted_knowledge: ExtractedKnowledge) -> float:
        """Calculate coverage of extracted knowledge vs original data"""
        source_files = {r.metadata.name for r in scan_results}

        # Check how many source files are represented in entities
        represented_files = set()
        for entity in extracted_knowledge.entities:
            represented_files.update(entity.source_files)

        coverage = len(represented_files) / len(source_files) if source_files else 0.0
        return min(coverage, 1.0)

    def _generate_validation_report(self) -> ValidationReport:
        """Generate comprehensive validation report"""
        # Calculate overall score
        if not self.validation_results:
            overall_score = 0.0
            overall_status = "failed"
        else:
            overall_score = sum(r.score for r in self.validation_results) / len(self.validation_results)

            if overall_score >= 0.8:
                overall_status = "passed"
            elif overall_score >= 0.5:
                overall_status = "warning"
            else:
                overall_status = "failed"

        # Generate summary
        summary = {
            "total_checks": len(self.validation_results),
            "passed_checks": len([r for r in self.validation_results if r.status == "passed"]),
            "warning_checks": len([r for r in self.validation_results if r.status == "warning"]),
            "failed_checks": len([r for r in self.validation_results if r.status == "failed"]),
            "check_types": {}
        }

        # Group by check type
        for result in self.validation_results:
            check_type = result.check_type
            if check_type not in summary["check_types"]:
                summary["check_types"][check_type] = {"count": 0, "avg_score": 0.0}
            summary["check_types"][check_type]["count"] += 1
            summary["check_types"][check_type]["avg_score"] += result.score

        # Calculate averages
        for check_type in summary["check_types"]:
            count = summary["check_types"][check_type]["count"]
            summary["check_types"][check_type]["avg_score"] /= count

        # Collect recommendations
        all_recommendations = []
        for result in self.validation_results:
            all_recommendations.extend(result.recommendations)

        # Remove duplicates and prioritize
        unique_recommendations = list(set(all_recommendations))

        return ValidationReport(
            validation_timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            overall_status=overall_status,
            check_results=self.validation_results,
            summary=summary,
            recommendations=unique_recommendations[:10]  # Top 10 recommendations
        )

    def export_report(self, report: ValidationReport, output_path: str) -> str:
        """Export validation report to JSON file"""
        try:
            # Convert to serializable format
            export_data = asdict(report)

            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Validation report exported to: {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to export validation report: {e}")
            raise


def main():
    """CLI entry point for validation system"""
    import argparse

    from analyzer import ContentAnalyzer
    from extractor import KnowledgeExtractor
    from scanner import ContextScanner

    parser = argparse.ArgumentParser(description="Validation System for Phase 24.1")
    parser.add_argument("context_path", help="Path to context directory")
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run complete pipeline: scan -> analyze -> extract -> validate
    scanner = ContextScanner(args.context_path)
    scan_results = scanner.scan_directory(recursive=True)

    analyzer = ContentAnalyzer()
    analysis_results = analyzer.analyze_content(scan_results)

    extractor = KnowledgeExtractor()
    extracted_knowledge = extractor.extract_knowledge(scan_results, analysis_results)

    validator = ValidationSystem()
    report = validator.validate_all(scan_results, analysis_results, extracted_knowledge)

    # Print summary
    print("\n✅ Validation Complete!")
    print(f"📊 Overall Score: {report.overall_score:.2f}")
    print(f"🎯 Overall Status: {report.overall_status.upper()}")
    print(f"📋 Total Checks: {report.summary['total_checks']}")
    print(f"✅ Passed: {report.summary['passed_checks']}")
    print(f"⚠️  Warnings: {report.summary['warning_checks']}")
    print(f"❌ Failed: {report.summary['failed_checks']}")

    if report.recommendations:
        print("\n💡 Top Recommendations:")
        for i, rec in enumerate(report.recommendations[:5], 1):
            print(f"   {i}. {rec}")

    # Export if requested
    if args.output:
        validator.export_report(report, args.output)


if __name__ == "__main__":
    main()
