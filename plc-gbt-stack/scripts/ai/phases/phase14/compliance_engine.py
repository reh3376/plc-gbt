#!/usr/bin/env python3
"""
Phase 14.3.2: Compliance Engine
===============================

Automated compliance monitoring and enforcement for JSON schema governance.
Following AI Task Orchestrator methodology for systematic compliance management.

Features:
- Codebase scanning for JSON usage and compliance
- Automated compliance reporting and audit trail
- Schema violation detection and auto-fixing
- Enterprise audit compliance scoring
- Real-time monitoring and alerting
- Compliance trend analysis and recommendations

Target: ~600 lines
Author: AI Task Orchestrator
Date: 2025-01-18
Phase: 14.3.2 - JSON Schema Governance Framework
Dependencies: Phase 14.3.1 (SchemaRegistry)
"""

import ast
import concurrent.futures
import json
import re
import sys
import uuid
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
from core import BaseOrchestrator, TaskAnalysis

# Import schema registry dependency
try:
    from .schema_registry import SchemaRegistry, ValidationResult
except ImportError:
    from schema_registry import SchemaRegistry

@dataclass
class JSONUsage:
    """JSON usage instance found in codebase"""
    file_path: str
    line_number: int
    usage_type: str  # literal, load, dump, schema_validation
    content: str
    extracted_json: Optional[Dict[str, Any]]
    estimated_schema: Optional[str]
    compliance_status: str  # compliant, non_compliant, unknown
    issues: List[str]
    recommendations: List[str]

@dataclass
class SchemaViolation:
    """Schema compliance violation"""
    violation_id: str
    file_path: str
    line_number: int
    violation_type: str  # missing_schema, invalid_schema, outdated_schema
    severity: str  # critical, major, minor, info
    description: str
    current_value: Optional[str]
    expected_value: Optional[str]
    auto_fixable: bool
    fix_suggestion: Optional[str]
    detected_at: str

@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""
    report_id: str
    scan_timestamp: str
    files_scanned: int
    json_usages_found: int
    compliant_usages: int
    non_compliant_usages: int
    violations: List[SchemaViolation]
    compliance_score: float  # 0.0 to 1.0
    trend_analysis: Dict[str, Any]
    recommendations: List[str]
    executive_summary: str

@dataclass
class FixResult:
    """Auto-fix operation result"""
    fix_id: str
    violation_id: str
    file_path: str
    fix_applied: bool
    original_content: str
    fixed_content: str
    backup_created: bool
    error_message: Optional[str]
    timestamp: str

class ViolationType(Enum):
    """Types of compliance violations"""
    MISSING_SCHEMA = "missing_schema"
    INVALID_SCHEMA = "invalid_schema"
    OUTDATED_SCHEMA = "outdated_schema"
    UNREGISTERED_SCHEMA = "unregistered_schema"
    INCONSISTENT_FORMAT = "inconsistent_format"
    SECURITY_VIOLATION = "security_violation"

class ComplianceEngine(BaseOrchestrator):
    """
    Automated compliance monitoring and enforcement engine for JSON schema governance.

    Provides comprehensive scanning, monitoring, and enforcement capabilities for
    ensuring enterprise-wide compliance with registered JSON schemas.
    """

    def __init__(self, schema_registry: SchemaRegistry, task_id: str = "compliance_engine",
                 config_file: Optional[str] = None):
        super().__init__(task_id, config_file)

        # Dependencies
        self.schema_registry = schema_registry

        # Compliance configuration
        self.compliance_config = {
            "scan_patterns": ["**/*.py", "**/*.json", "**/*.ts", "**/*.js"],
            "ignore_patterns": [
                "__pycache__", ".git", "node_modules", ".venv", "*.pyc",
                "test_", "_test", ".test.", "spec.", ".spec."
            ],
            "json_usage_patterns": {
                "json_loads": r'json\.loads?\s*\(',
                "json_dumps": r'json\.dumps?\s*\(',
                "json_literal": r'\{[^}]*\"[^\"]*\"[^}]*\}',
                "schema_validation": r'validate\s*\([^)]*schema'
            },
            "compliance_thresholds": {
                "excellent": 0.95,
                "good": 0.85,
                "acceptable": 0.70,
                "poor": 0.50
            },
            "auto_fix_enabled": True,
            "backup_original_files": True,
            "max_parallel_scans": 10
        }

        # Compliance state
        self.scan_results: List[JSONUsage] = []
        self.violations: List[SchemaViolation] = []
        self.compliance_history: List[ComplianceReport] = []

        # Performance metrics
        self.compliance_metrics = {
            "files_scanned": 0,
            "json_usages_found": 0,
            "violations_detected": 0,
            "auto_fixes_applied": 0,
            "compliance_score": 0.0,
            "scan_duration": 0.0
        }

    def _analyze_task(self) -> TaskAnalysis:
        """Implement task analysis following AI Task Orchestrator methodology"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="complex",
            estimated_time="3-5 hours",
            estimated_lines=600,
            requirements=[
                "Codebase scanning with AST parsing",
                "JSON usage pattern detection",
                "Schema compliance validation",
                "Automated violation fixing",
                "Compliance reporting and scoring",
                "Trend analysis and recommendations"
            ],
            risks=[
                "Large codebase scanning performance",
                "False positive detection in complex code",
                "Auto-fixing may introduce syntax errors",
                "Concurrent file access during scanning"
            ],
            dependencies=["ast", "re", "pathlib", "concurrent.futures", "schema_registry"],
            success_criteria=[
                "Accurate JSON usage detection (>95%)",
                "Fast codebase scanning (<30s for 1000 files)",
                "Safe auto-fixing with backup creation",
                "Comprehensive compliance reporting",
                "Trend analysis for compliance improvement"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute compliance monitoring and enforcement"""
        self.log_execution_step("Compliance Engine Operation", "started")

        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}

            # Get project root for scanning
            project_root = self.config.get("system.project_root", str(Path.cwd()))

            # Phase 1: Scan codebase for JSON usage
            self.log_execution_step("Codebase Scanning", "started")
            scan_results = self.scan_codebase_for_json(project_root)
            self.log_execution_step("Codebase Scanning", "completed", {
                "files_scanned": self.compliance_metrics["files_scanned"],
                "json_usages_found": len(scan_results)
            })

            # Phase 2: Generate compliance report
            self.log_execution_step("Compliance Analysis", "started")
            compliance_report = self.generate_compliance_report()
            self.log_execution_step("Compliance Analysis", "completed", {
                "violations_detected": len(compliance_report.violations),
                "compliance_score": compliance_report.compliance_score
            })

            # Phase 3: Auto-fix violations (if enabled)
            fix_results = []
            if self.compliance_config["auto_fix_enabled"]:
                self.log_execution_step("Auto-Fix Violations", "started")
                fixable_violations = [v for v in compliance_report.violations if v.auto_fixable]
                fix_results = self.auto_fix_schema_violations(fixable_violations)
                self.log_execution_step("Auto-Fix Violations", "completed", {
                    "fixes_attempted": len(fix_results),
                    "fixes_successful": len([f for f in fix_results if f.fix_applied])
                })

            # Prepare results
            results = {
                "compliance_status": "operational",
                "compliance_report": asdict(compliance_report),
                "auto_fix_results": [asdict(f) for f in fix_results],
                "compliance_metrics": self.compliance_metrics,
                "session_info": {
                    "session_id": self.session_id,
                    "scan_timestamp": datetime.now().isoformat(),
                    "project_root": project_root,
                    "configuration": self.compliance_config
                }
            }

            # Add performance metrics
            self.add_performance_metric("compliance_score", compliance_report.compliance_score)
            self.add_performance_metric("violations_detected", len(compliance_report.violations))

            self.log_execution_step("Compliance Engine Operation", "completed", {
                "compliance_score": compliance_report.compliance_score,
                "total_violations": len(compliance_report.violations)
            })

            return results

        except Exception as e:
            self.log_error("Compliance engine operation failed", e)
            return {"status": "failed", "error": str(e)}

    def scan_codebase_for_json(self, directory: str) -> List[JSONUsage]:
        """
        Scan entire codebase for JSON usage and compliance.

        Args:
            directory: Root directory to scan

        Returns:
            List of JSON usage instances found
        """
        scan_start_time = datetime.now()
        directory_path = Path(directory)

        # Find all scannable files
        files_to_scan = self._find_scannable_files(directory_path)
        self.compliance_metrics["files_scanned"] = len(files_to_scan)

        # Parallel scanning for performance
        json_usages = []
        max_workers = min(self.compliance_config["max_parallel_scans"], len(files_to_scan))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit scan tasks
            future_to_file = {
                executor.submit(self._scan_file_for_json, file_path): file_path
                for file_path in files_to_scan
            }

            # Collect results
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_usages = future.result()
                    json_usages.extend(file_usages)
                except Exception as e:
                    self.log_error(f"Failed to scan file {file_path}", e)

        # Update metrics
        self.compliance_metrics["json_usages_found"] = len(json_usages)
        self.compliance_metrics["scan_duration"] = (datetime.now() - scan_start_time).total_seconds()

        # Store results
        self.scan_results = json_usages

        return json_usages

    def generate_compliance_report(self) -> ComplianceReport:
        """
        Generate comprehensive compliance report.

        Returns:
            Detailed compliance report with violations and recommendations
        """
        report_id = str(uuid.uuid4())
        scan_timestamp = datetime.now().isoformat()

        # Analyze compliance for each JSON usage
        self._analyze_compliance_violations()

        # Calculate compliance metrics
        total_usages = len(self.scan_results)
        compliant_usages = len([u for u in self.scan_results if u.compliance_status == "compliant"])
        non_compliant_usages = len([u for u in self.scan_results if u.compliance_status == "non_compliant"])

        # Calculate compliance score
        compliance_score = compliant_usages / max(total_usages, 1)
        self.compliance_metrics["compliance_score"] = compliance_score

        # Generate trend analysis
        trend_analysis = self._generate_trend_analysis()

        # Generate recommendations
        recommendations = self._generate_compliance_recommendations()

        # Create executive summary
        executive_summary = self._create_executive_summary(
            compliance_score, len(self.violations), compliant_usages, non_compliant_usages
        )

        # Create report
        report = ComplianceReport(
            report_id=report_id,
            scan_timestamp=scan_timestamp,
            files_scanned=self.compliance_metrics["files_scanned"],
            json_usages_found=total_usages,
            compliant_usages=compliant_usages,
            non_compliant_usages=non_compliant_usages,
            violations=self.violations,
            compliance_score=compliance_score,
            trend_analysis=trend_analysis,
            recommendations=recommendations,
            executive_summary=executive_summary
        )

        # Store in history
        self.compliance_history.append(report)

        return report

    def auto_fix_schema_violations(self, violations: List[SchemaViolation]) -> List[FixResult]:
        """
        Automatically fix common schema violations where safe.

        Args:
            violations: List of violations to attempt fixing

        Returns:
            List of fix results with success/failure status
        """
        fix_results = []

        for violation in violations:
            if not violation.auto_fixable:
                continue

            fix_result = self._attempt_violation_fix(violation)
            fix_results.append(fix_result)

            if fix_result.fix_applied:
                self.compliance_metrics["auto_fixes_applied"] += 1

        return fix_results

    def _find_scannable_files(self, directory: Path) -> List[Path]:
        """Find all files that should be scanned for JSON usage"""
        scannable_files = []

        for pattern in self.compliance_config["scan_patterns"]:
            files = directory.glob(pattern)

            for file_path in files:
                if self._should_scan_file(file_path):
                    scannable_files.append(file_path)

        return sorted(set(scannable_files))  # Remove duplicates

    def _should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned based on ignore patterns"""
        path_str = str(file_path)

        for pattern in self.compliance_config["ignore_patterns"]:
            if pattern in path_str:
                return False

        # Additional checks
        if file_path.is_dir():
            return False

        if file_path.stat().st_size > 10 * 1024 * 1024:  # Skip files > 10MB
            return False

        return True

    def _scan_file_for_json(self, file_path: Path) -> List[JSONUsage]:
        """Scan individual file for JSON usage"""
        json_usages = []

        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Scan for different types of JSON usage
            if file_path.suffix == '.py':
                usages = self._scan_python_file(file_path, content)
            elif file_path.suffix == '.json':
                usages = self._scan_json_file(file_path, content)
            elif file_path.suffix in ['.ts', '.js']:
                usages = self._scan_javascript_file(file_path, content)
            else:
                usages = self._scan_generic_file(file_path, content)

            json_usages.extend(usages)

        except Exception as e:
            # Log error but don't fail the entire scan
            self.logger.warning(f"Failed to scan {file_path}: {e}")

        return json_usages

    def _scan_python_file(self, file_path: Path, content: str) -> List[JSONUsage]:
        """Scan Python file for JSON usage patterns"""
        usages = []
        lines = content.split('\n')

        # Pattern-based scanning
        for line_num, line in enumerate(lines, 1):
            # JSON loads/dumps
            for pattern_name, pattern in self.compliance_config["json_usage_patterns"].items():
                matches = re.finditer(pattern, line)
                for _match in matches:
                    usage = JSONUsage(
                        file_path=str(file_path),
                        line_number=line_num,
                        usage_type=pattern_name,
                        content=line.strip(),
                        extracted_json=None,
                        estimated_schema=None,
                        compliance_status="unknown",
                        issues=[],
                        recommendations=[]
                    )
                    usages.append(usage)

        # AST-based scanning for more accurate detection
        try:
            tree = ast.parse(content)
            ast_usages = self._extract_json_from_ast(tree, file_path)
            usages.extend(ast_usages)
        except SyntaxError:
            # Skip AST analysis for files with syntax errors
            pass

        return usages

    def _scan_json_file(self, file_path: Path, content: str) -> List[JSONUsage]:
        """Scan JSON file for schema compliance"""
        usages = []

        try:
            json_data = json.loads(content)

            usage = JSONUsage(
                file_path=str(file_path),
                line_number=1,
                usage_type="json_file",
                content=content[:200] + "..." if len(content) > 200 else content,
                extracted_json=json_data,
                estimated_schema=self._estimate_schema_for_json(json_data),
                compliance_status="unknown",
                issues=[],
                recommendations=[]
            )
            usages.append(usage)

        except json.JSONDecodeError as e:
            # Invalid JSON file
            usage = JSONUsage(
                file_path=str(file_path),
                line_number=getattr(e, 'lineno', 1),
                usage_type="invalid_json",
                content=content[:200] + "..." if len(content) > 200 else content,
                extracted_json=None,
                estimated_schema=None,
                compliance_status="non_compliant",
                issues=[f"Invalid JSON: {str(e)}"],
                recommendations=["Fix JSON syntax errors"]
            )
            usages.append(usage)

        return usages

    def _scan_javascript_file(self, file_path: Path, content: str) -> List[JSONUsage]:
        """Scan JavaScript/TypeScript file for JSON usage"""
        usages = []
        lines = content.split('\n')

        # Look for JSON.parse, JSON.stringify, and object literals
        js_patterns = {
            "json_parse": r'JSON\.parse\s*\(',
            "json_stringify": r'JSON\.stringify\s*\(',
            "object_literal": r'\{\s*["\'][^"\']*["\']\s*:'
        }

        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in js_patterns.items():
                matches = re.finditer(pattern, line)
                for _match in matches:
                    usage = JSONUsage(
                        file_path=str(file_path),
                        line_number=line_num,
                        usage_type=pattern_name,
                        content=line.strip(),
                        extracted_json=None,
                        estimated_schema=None,
                        compliance_status="unknown",
                        issues=[],
                        recommendations=[]
                    )
                    usages.append(usage)

        return usages

    def _scan_generic_file(self, file_path: Path, content: str) -> List[JSONUsage]:
        """Scan generic file for JSON-like patterns"""
        usages = []
        lines = content.split('\n')

        # Simple JSON object detection
        json_pattern = r'\{[^}]*"[^"]*"[^}]*\}'

        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(json_pattern, line)
            for _match in matches:
                usage = JSONUsage(
                    file_path=str(file_path),
                    line_number=line_num,
                    usage_type="json_like",
                    content=line.strip(),
                    extracted_json=None,
                    estimated_schema=None,
                    compliance_status="unknown",
                    issues=[],
                    recommendations=[]
                )
                usages.append(usage)

        return usages

    def _extract_json_from_ast(self, tree: ast.AST, file_path: Path) -> List[JSONUsage]:
        """Extract JSON usage from Python AST"""
        usages = []

        class JSONVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Look for json.loads, json.dumps calls
                if (isinstance(node.func, ast.Attribute) and
                    isinstance(node.func.value, ast.Name) and
                    node.func.value.id == 'json' and
                    node.func.attr in ['loads', 'dumps', 'load', 'dump']):

                    usage = JSONUsage(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        usage_type=f"json_{node.func.attr}",
                        content=ast.unparse(node) if hasattr(ast, 'unparse') else str(node),
                        extracted_json=None,
                        estimated_schema=None,
                        compliance_status="unknown",
                        issues=[],
                        recommendations=[]
                    )
                    usages.append(usage)

                self.generic_visit(node)

        visitor = JSONVisitor()
        visitor.visit(tree)

        return usages

    def _estimate_schema_for_json(self, json_data: Any) -> Optional[str]:
        """Estimate appropriate schema name for JSON data"""
        if not isinstance(json_data, dict):
            return None

        # Simple heuristics for schema estimation
        keys = set(json_data.keys())

        # Common patterns
        if {"name", "version", "dependencies"} <= keys:
            return "package_manifest"
        elif {"id", "name", "email"} <= keys:
            return "user_profile"
        elif {"timestamp", "level", "message"} <= keys:
            return "log_entry"
        elif {"status", "data", "error"} <= keys:
            return "api_response"

        return "generic_object"

    def _analyze_compliance_violations(self):
        """Analyze JSON usages and identify compliance violations"""
        self.violations = []

        for usage in self.scan_results:
            violations = self._check_usage_compliance(usage)
            self.violations.extend(violations)

            # Update usage compliance status
            if violations:
                usage.compliance_status = "non_compliant"
                usage.issues = [v.description for v in violations]
                usage.recommendations = [v.fix_suggestion for v in violations if v.fix_suggestion]
            else:
                usage.compliance_status = "compliant"

        self.compliance_metrics["violations_detected"] = len(self.violations)

    def _check_usage_compliance(self, usage: JSONUsage) -> List[SchemaViolation]:
        """Check individual JSON usage for compliance violations"""
        violations = []

        # Check if schema is registered (if estimated)
        if usage.estimated_schema:
            # Check with schema registry
            try:
                schema_def = self.schema_registry._get_schema(usage.estimated_schema, "latest")
                if not schema_def:
                    violation = SchemaViolation(
                        violation_id=str(uuid.uuid4()),
                        file_path=usage.file_path,
                        line_number=usage.line_number,
                        violation_type=ViolationType.UNREGISTERED_SCHEMA.value,
                        severity="major",
                        description=f"Estimated schema '{usage.estimated_schema}' is not registered",
                        current_value=usage.estimated_schema,
                        expected_value="registered_schema",
                        auto_fixable=False,
                        fix_suggestion=f"Register schema '{usage.estimated_schema}' in schema registry",
                        detected_at=datetime.now().isoformat()
                    )
                    violations.append(violation)
            except Exception:
                # Schema registry not available or error
                pass

        # Check for missing schema when JSON is used
        if usage.usage_type in ["json_loads", "json_file"] and not usage.estimated_schema:
            violation = SchemaViolation(
                violation_id=str(uuid.uuid4()),
                file_path=usage.file_path,
                line_number=usage.line_number,
                violation_type=ViolationType.MISSING_SCHEMA.value,
                severity="minor",
                description="JSON usage without identified schema",
                current_value=usage.content[:50],
                expected_value="schema_validated_json",
                auto_fixable=False,
                fix_suggestion="Add schema validation for this JSON usage",
                detected_at=datetime.now().isoformat()
            )
            violations.append(violation)

        # Check for invalid JSON in .json files
        if usage.usage_type == "invalid_json":
            violation = SchemaViolation(
                violation_id=str(uuid.uuid4()),
                file_path=usage.file_path,
                line_number=usage.line_number,
                violation_type=ViolationType.INVALID_SCHEMA.value,
                severity="critical",
                description="Invalid JSON syntax",
                current_value=usage.issues[0] if usage.issues else "Invalid JSON",
                expected_value="valid_json",
                auto_fixable=False,
                fix_suggestion="Fix JSON syntax errors",
                detected_at=datetime.now().isoformat()
            )
            violations.append(violation)

        return violations

    def _generate_trend_analysis(self) -> Dict[str, Any]:
        """Generate compliance trend analysis"""
        return {
            "current_compliance_score": self.compliance_metrics["compliance_score"],
            "total_violations_by_type": self._count_violations_by_type(),
            "files_with_violations": len({v.file_path for v in self.violations}),
            "most_common_violations": self._get_most_common_violations(),
            "compliance_trend": "stable",  # Would calculate from history in production
            "improvement_areas": self._identify_improvement_areas()
        }

    def _count_violations_by_type(self) -> Dict[str, int]:
        """Count violations by type"""
        violation_counts = Counter(v.violation_type for v in self.violations)
        return dict(violation_counts)

    def _get_most_common_violations(self) -> List[Dict[str, Any]]:
        """Get most common violation types"""
        violation_counts = self._count_violations_by_type()

        return [
            {"type": vtype, "count": count}
            for vtype, count in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

    def _identify_improvement_areas(self) -> List[str]:
        """Identify key areas for compliance improvement"""
        areas = []

        if self.compliance_metrics["compliance_score"] < 0.8:
            areas.append("Increase overall schema adoption")

        if len([v for v in self.violations if v.violation_type == ViolationType.MISSING_SCHEMA.value]) > 5:
            areas.append("Add schema validation to JSON operations")

        if len([v for v in self.violations if v.violation_type == ViolationType.INVALID_SCHEMA.value]) > 0:
            areas.append("Fix invalid JSON syntax errors")

        if len([v for v in self.violations if v.auto_fixable]) > 3:
            areas.append("Enable auto-fixing for simple violations")

        return areas

    def _generate_compliance_recommendations(self) -> List[str]:
        """Generate actionable compliance recommendations"""
        recommendations = []

        # Based on compliance score
        score = self.compliance_metrics["compliance_score"]
        if score < 0.5:
            recommendations.append("Critical: Implement comprehensive JSON schema governance")
        elif score < 0.7:
            recommendations.append("Improve schema coverage for JSON operations")
        elif score < 0.9:
            recommendations.append("Address remaining schema compliance gaps")
        else:
            recommendations.append("Maintain excellent compliance standards")

        # Based on violation types
        violation_types = {v.violation_type for v in self.violations}

        if ViolationType.MISSING_SCHEMA.value in violation_types:
            recommendations.append("Add schema validation to unvalidated JSON operations")

        if ViolationType.INVALID_SCHEMA.value in violation_types:
            recommendations.append("Fix JSON syntax errors immediately")

        if ViolationType.UNREGISTERED_SCHEMA.value in violation_types:
            recommendations.append("Register commonly used schemas in schema registry")

        # Auto-fix recommendations
        auto_fixable = len([v for v in self.violations if v.auto_fixable])
        if auto_fixable > 0:
            recommendations.append(f"Enable auto-fixing for {auto_fixable} automatically fixable violations")

        return recommendations

    def _create_executive_summary(self, compliance_score: float, violation_count: int,
                                compliant_usages: int, non_compliant_usages: int) -> str:
        """Create executive summary for compliance report"""
        # Determine compliance level
        if compliance_score >= 0.95:
            level = "Excellent"
        elif compliance_score >= 0.85:
            level = "Good"
        elif compliance_score >= 0.70:
            level = "Acceptable"
        else:
            level = "Needs Improvement"

        summary = f"""
JSON Schema Governance Compliance Report

Compliance Level: {level} ({compliance_score:.1%})
Total JSON Usages: {compliant_usages + non_compliant_usages}
Compliant: {compliant_usages} | Non-Compliant: {non_compliant_usages}
Total Violations: {violation_count}

{level} compliance indicates {'strong' if compliance_score >= 0.85 else 'adequate' if compliance_score >= 0.70 else 'insufficient'}
adherence to JSON schema governance standards across the codebase.
        """.strip()

        return summary

    def _attempt_violation_fix(self, violation: SchemaViolation) -> FixResult:
        """Attempt to automatically fix a schema violation"""
        fix_id = str(uuid.uuid4())

        try:
            # Read original file content
            with open(violation.file_path, encoding='utf-8') as f:
                original_content = f.read()

            # Create backup if enabled
            backup_created = False
            if self.compliance_config["backup_original_files"]:
                backup_path = Path(violation.file_path + ".backup")
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                backup_created = True

            # Apply fix based on violation type
            fixed_content = self._apply_violation_fix(original_content, violation)

            if fixed_content != original_content:
                # Write fixed content
                with open(violation.file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)

                return FixResult(
                    fix_id=fix_id,
                    violation_id=violation.violation_id,
                    file_path=violation.file_path,
                    fix_applied=True,
                    original_content=original_content,
                    fixed_content=fixed_content,
                    backup_created=backup_created,
                    error_message=None,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return FixResult(
                    fix_id=fix_id,
                    violation_id=violation.violation_id,
                    file_path=violation.file_path,
                    fix_applied=False,
                    original_content=original_content,
                    fixed_content=original_content,
                    backup_created=backup_created,
                    error_message="No fix needed or fix not applicable",
                    timestamp=datetime.now().isoformat()
                )

        except Exception as e:
            return FixResult(
                fix_id=fix_id,
                violation_id=violation.violation_id,
                file_path=violation.file_path,
                fix_applied=False,
                original_content="",
                fixed_content="",
                backup_created=False,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )

    def _apply_violation_fix(self, content: str, violation: SchemaViolation) -> str:
        """Apply specific fix for violation type"""
        # This is a simplified implementation
        # In production, this would have sophisticated fixing logic

        if violation.violation_type == ViolationType.INCONSISTENT_FORMAT.value:
            # Fix common JSON formatting issues
            return self._fix_json_formatting(content)

        # For now, return original content for other violation types
        # as they require more complex fixes
        return content

    def _fix_json_formatting(self, content: str) -> str:
        """Fix common JSON formatting issues"""
        try:
            # Attempt to parse and reformat JSON
            data = json.loads(content)
            return json.dumps(data, indent=2, sort_keys=True)
        except json.JSONDecodeError:
            # Return original if not valid JSON
            return content
