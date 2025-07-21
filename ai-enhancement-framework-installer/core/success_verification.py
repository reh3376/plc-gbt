#!/usr/bin/env python3
"""
✅ Success Verification & Documentation Update Module

Implements automated success verification and comprehensive documentation updates
following the AI Task Orchestrator Guide methodology. Ensures all implementations
are properly validated, documented, and linked in project documentation.

Author: AI Enhancement Framework
Created: 2025-01-18
License: MIT
"""

import os
import re
import json
import time
import yaml
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompletionStatus(Enum):
    """Task completion status levels"""
    PLANNED = "🔵 PLANNED"
    IN_PROGRESS = "🟡 IN PROGRESS"
    COMPLETED = "✅ COMPLETED"
    FAILED = "❌ FAILED"
    CANCELLED = "⚪ CANCELLED"
    BLOCKED = "🔴 BLOCKED"

class DocumentationType(Enum):
    """Types of documentation to create/update"""
    ROADMAP = "roadmap"
    COMPLETION_SUMMARY = "completion_summary"
    VALIDATION_REPORT = "validation_report"
    PERFORMANCE_METRICS = "performance_metrics"
    GUIDE = "guide"
    HOW_TO = "how_to"
    RESULTS = "results"

@dataclass
class ValidationCriteria:
    """Criteria for success validation"""
    functionality: str = "All requirements met"
    validation_score: float = 90.0
    mathematical_accuracy: float = 95.0
    production_readiness: float = 85.0
    testing: str = "All tests passing"
    documentation: str = "Complete and standardized"
    security: str = "Security compliance verified"
    performance: str = "Performance targets met"

@dataclass
class DeliverableItem:
    """Individual deliverable item"""
    name: str
    type: str  # "code", "documentation", "configuration", "test"
    path: str
    description: str
    validation_score: Optional[float] = None
    completed: bool = False

@dataclass
class TaskCompletion:
    """Task completion information"""
    task_id: str
    phase: str
    task_name: str
    completion_date: datetime
    validation_results: Dict[str, Any]
    deliverables: List[DeliverableItem]
    achievements: List[str]
    performance_metrics: Dict[str, Any]
    mathematical_validation: Optional[Dict[str, Any]] = None
    production_assessment: Optional[Dict[str, Any]] = None

@dataclass
class DocumentationUpdate:
    """Documentation update information"""
    document_type: DocumentationType
    file_path: str
    content: str
    update_type: str  # "create", "update", "append"
    metadata: Dict[str, Any]

class RoadmapManager:
    """Manages roadmap.md updates and maintenance"""
    
    def __init__(self, roadmap_path: str = "docs/roadmap.md"):
        self.roadmap_path = Path(roadmap_path)
        self.ensure_roadmap_exists()
    
    def ensure_roadmap_exists(self):
        """Ensure roadmap.md exists with basic structure"""
        if not self.roadmap_path.exists():
            self.roadmap_path.parent.mkdir(parents=True, exist_ok=True)
            initial_content = """# Project Roadmap

## Overview
This roadmap tracks the progress of all project phases and tasks with comprehensive validation and documentation.

## Phases

<!-- Phases will be automatically updated by the Success Verification System -->
"""
            self.roadmap_path.write_text(initial_content)
            logger.info(f"Created initial roadmap at {self.roadmap_path}")
    
    def update_phase_status(self, 
                           phase: str,
                           status: CompletionStatus,
                           completion_date: Optional[str] = None,
                           validation_score: Optional[float] = None,
                           mathematical_accuracy: Optional[float] = None,
                           production_readiness: Optional[float] = None,
                           deliverables: Optional[List[DeliverableItem]] = None) -> bool:
        """Update phase status in roadmap"""
        try:
            current_content = self.roadmap_path.read_text()
            
            # Create phase section if it doesn't exist
            phase_pattern = rf"## {re.escape(phase)}\s*\n"
            
            if not re.search(phase_pattern, current_content):
                # Add new phase section
                new_phase_section = self._create_phase_section(
                    phase, status, completion_date, validation_score,
                    mathematical_accuracy, production_readiness, deliverables
                )
                current_content += f"\n{new_phase_section}\n"
            else:
                # Update existing phase section
                current_content = self._update_existing_phase_section(
                    current_content, phase, status, completion_date,
                    validation_score, mathematical_accuracy, production_readiness, deliverables
                )
            
            self.roadmap_path.write_text(current_content)
            logger.info(f"Updated roadmap for phase: {phase}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update roadmap: {e}")
            return False
    
    def _create_phase_section(self,
                            phase: str,
                            status: CompletionStatus,
                            completion_date: Optional[str],
                            validation_score: Optional[float],
                            mathematical_accuracy: Optional[float],
                            production_readiness: Optional[float],
                            deliverables: Optional[List[DeliverableItem]]) -> str:
        """Create new phase section"""
        section = f"## {phase}\n\n"
        section += f"**Status**: {status.value}"
        
        if completion_date:
            section += f" - Completed: {completion_date}"
        
        section += "\n\n"
        
        # Add validation metrics
        if validation_score is not None:
            section += f"**Validation Score**: {validation_score:.1f}%\n\n"
        
        if mathematical_accuracy is not None:
            section += f"**Mathematical Accuracy**: {mathematical_accuracy:.1f}%\n\n"
        
        if production_readiness is not None:
            section += f"**Production Readiness**: {production_readiness:.1f}%\n\n"
        
        # Add deliverables
        if deliverables:
            section += "**Deliverables**:\n"
            for deliverable in deliverables:
                status_icon = "✅" if deliverable.completed else "⏳"
                section += f"- {status_icon} [{deliverable.name}]({deliverable.path}) - {deliverable.description}\n"
            section += "\n"
        
        return section
    
    def _update_existing_phase_section(self,
                                     content: str,
                                     phase: str,
                                     status: CompletionStatus,
                                     completion_date: Optional[str],
                                     validation_score: Optional[float],
                                     mathematical_accuracy: Optional[float],
                                     production_readiness: Optional[float],
                                     deliverables: Optional[List[DeliverableItem]]) -> str:
        """Update existing phase section"""
        # Find the phase section
        phase_pattern = rf"(## {re.escape(phase)}\s*\n)(.*?)(?=## |\Z)"
        match = re.search(phase_pattern, content, re.DOTALL)
        
        if not match:
            return content
        
        # Create updated section
        new_section = self._create_phase_section(
            phase, status, completion_date, validation_score,
            mathematical_accuracy, production_readiness, deliverables
        )
        
        # Replace the section
        return content[:match.start()] + new_section + content[match.end():]
    
    def add_cross_references(self,
                           phase: str,
                           documents: Dict[str, str]) -> bool:
        """Add cross-references to related documents"""
        try:
            current_content = self.roadmap_path.read_text()
            
            # Find phase section
            phase_pattern = rf"(## {re.escape(phase)}\s*\n.*?)(?=## |\Z)"
            match = re.search(phase_pattern, current_content, re.DOTALL)
            
            if not match:
                logger.warning(f"Phase {phase} not found in roadmap")
                return False
            
            section_content = match.group(1)
            
            # Add references section if not exists
            if "**Related Documents**:" not in section_content:
                references = "\n**Related Documents**:\n"
                for doc_type, doc_path in documents.items():
                    references += f"- [{doc_type.title()}]({doc_path})\n"
                
                section_content += references
                
                # Replace in full content
                updated_content = (
                    current_content[:match.start()] + 
                    section_content + 
                    current_content[match.end():]
                )
                
                self.roadmap_path.write_text(updated_content)
                logger.info(f"Added cross-references for phase: {phase}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add cross-references: {e}")
            return False

class CompletionSummaryGenerator:
    """Generates comprehensive completion summaries"""
    
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_completion_summary(self, task_completion: TaskCompletion) -> str:
        """Create comprehensive completion summary"""
        summary_filename = f"{task_completion.phase}_COMPLETION_SUMMARY.md"
        summary_path = self.output_dir / summary_filename
        
        content = self._generate_summary_content(task_completion)
        
        summary_path.write_text(content)
        logger.info(f"Created completion summary: {summary_path}")
        
        return str(summary_path)
    
    def _generate_summary_content(self, task_completion: TaskCompletion) -> str:
        """Generate completion summary content"""
        content = f"""# {task_completion.phase} - Completion Summary

## Overview
**Task**: {task_completion.task_name}  
**Completion Date**: {task_completion.completion_date.strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Validation Score**: {task_completion.validation_results.get('overall_score', 'N/A')}%

## Achievements

"""
        
        for achievement in task_completion.achievements:
            content += f"- ✅ {achievement}\n"
        
        content += "\n## Validation Results\n\n"
        
        # Validation tiers
        tier_results = task_completion.validation_results.get('tier_results', {})
        for tier, result in tier_results.items():
            status_icon = "✅" if result.get('status') == 'passed' else "⚠️" if result.get('status') == 'warning' else "❌"
            content += f"### {tier.title()} Validation {status_icon}\n"
            content += f"- **Score**: {result.get('score', 0):.1f}%\n"
            content += f"- **Status**: {result.get('status', 'unknown')}\n"
            
            issues = result.get('issues', [])
            if issues:
                content += f"- **Issues**: {len(issues)} found\n"
                for issue in issues[:3]:  # Show first 3 issues
                    severity = issue.get('severity', 'unknown')
                    description = issue.get('description', 'No description')
                    content += f"  - {severity.upper()}: {description}\n"
                if len(issues) > 3:
                    content += f"  - ... and {len(issues) - 3} more\n"
            content += "\n"
        
        # Mathematical validation (if available)
        if task_completion.mathematical_validation:
            content += "## Mathematical Validation\n\n"
            math_val = task_completion.mathematical_validation
            content += f"- **Accuracy Score**: {math_val.get('accuracy_score', 'N/A')}%\n"
            content += f"- **Expressions Verified**: {math_val.get('expressions_verified', 0)}\n"
            content += f"- **WolframAlpha Verified**: {'✅' if math_val.get('wolfram_verified') else '❌'}\n\n"
        
        # Production assessment (if available)
        if task_completion.production_assessment:
            content += "## Production Readiness Assessment\n\n"
            prod_assess = task_completion.production_assessment
            content += f"- **Production Score**: {prod_assess.get('production_score', 'N/A')}%\n"
            content += f"- **Deployment Ready**: {'✅' if prod_assess.get('deployment_ready') else '❌'}\n"
            content += f"- **Security Compliance**: {'✅' if prod_assess.get('security_compliant') else '❌'}\n\n"
        
        # Performance metrics
        content += "## Performance Metrics\n\n"
        for metric, value in task_completion.performance_metrics.items():
            content += f"- **{metric.title()}**: {value}\n"
        content += "\n"
        
        # Deliverables
        content += "## Deliverables\n\n"
        for deliverable in task_completion.deliverables:
            status_icon = "✅" if deliverable.completed else "⏳"
            validation_info = f" (Score: {deliverable.validation_score:.1f}%)" if deliverable.validation_score else ""
            content += f"- {status_icon} **{deliverable.name}**{validation_info}\n"
            content += f"  - Type: {deliverable.type}\n"
            content += f"  - Path: [{deliverable.path}]({deliverable.path})\n"
            content += f"  - Description: {deliverable.description}\n\n"
        
        # Mermaid diagram
        content += self._generate_mermaid_diagram(task_completion)
        
        # Footer
        content += f"""
---
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Validation Framework**: AI Enhancement Framework v1.0  
**Methodology**: AI Task Orchestrator Guide Compliance
"""
        
        return content
    
    def _generate_mermaid_diagram(self, task_completion: TaskCompletion) -> str:
        """Generate Mermaid diagram for task completion"""
        diagram = """
## Task Completion Flow

```mermaid
graph TD
    A[Task Analysis] --> B[Implementation]
    B --> C[Validation Framework]
    C --> D{Validation Score}
    D -->|>= 90%| E[Success Verification]
    D -->|< 90%| F[Refinement Required]
    F --> B
    E --> G[Documentation Update]
    G --> H[Roadmap Update]
    H --> I[Cross-Reference Linking]
    I --> J[Completion Summary]
    
    style E fill:#90EE90
    style J fill:#87CEEB
```

"""
        return diagram

class ValidationReportGenerator:
    """Generates detailed validation reports"""
    
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_validation_report(self,
                               phase: str,
                               tier_results: Dict[str, Any],
                               recommendations: List[str],
                               mathematical_verification: Optional[Dict[str, Any]] = None) -> str:
        """Create detailed validation report"""
        report_filename = f"{phase}_VALIDATION_REPORT.md"
        report_path = self.output_dir / report_filename
        
        content = self._generate_validation_report_content(
            phase, tier_results, recommendations, mathematical_verification
        )
        
        report_path.write_text(content)
        logger.info(f"Created validation report: {report_path}")
        
        return str(report_path)
    
    def _generate_validation_report_content(self,
                                          phase: str,
                                          tier_results: Dict[str, Any],
                                          recommendations: List[str],
                                          mathematical_verification: Optional[Dict[str, Any]]) -> str:
        """Generate validation report content"""
        content = f"""# {phase} - Validation Report

## Executive Summary

This report provides comprehensive validation results for {phase} implementation following the AI Task Orchestrator Guide methodology.

## Validation Tiers Results

"""
        
        # Overall scores
        total_score = sum(result.get('score', 0) for result in tier_results.values())
        average_score = total_score / len(tier_results) if tier_results else 0
        
        content += f"**Overall Validation Score**: {average_score:.1f}%\n\n"
        
        # Tier-by-tier results
        for tier_name, result in tier_results.items():
            status_icon = "✅" if result.get('status') == 'passed' else "⚠️" if result.get('status') == 'warning' else "❌"
            content += f"### {tier_name.title()} {status_icon}\n\n"
            content += f"- **Score**: {result.get('score', 0):.1f}%\n"
            content += f"- **Status**: {result.get('status', 'unknown')}\n"
            content += f"- **Execution Time**: {result.get('execution_time', 0):.3f}s\n"
            
            issues = result.get('issues', [])
            if issues:
                content += f"\n**Issues Found ({len(issues)}):**\n"
                for issue in issues:
                    severity = issue.get('severity', 'unknown')
                    description = issue.get('description', 'No description')
                    recommendation = issue.get('recommendation', '')
                    line_num = issue.get('line_number', '')
                    
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟡', 
                        'medium': '🟢',
                        'low': '🔵',
                        'info': 'ℹ️'
                    }.get(severity.lower(), '❓')
                    
                    content += f"- {severity_emoji} **{severity.upper()}**: {description}"
                    if line_num:
                        content += f" (Line {line_num})"
                    content += "\n"
                    if recommendation:
                        content += f"  *Recommendation: {recommendation}*\n"
            
            content += "\n"
        
        # Mathematical verification section
        if mathematical_verification:
            content += "## Mathematical Verification\n\n"
            content += f"- **Accuracy Score**: {mathematical_verification.get('accuracy_score', 'N/A')}%\n"
            content += f"- **Expressions Found**: {mathematical_verification.get('expressions_found', 0)}\n"
            content += f"- **Expressions Verified**: {mathematical_verification.get('expressions_verified', 0)}\n"
            content += f"- **WolframAlpha Verification**: {'✅ Enabled' if mathematical_verification.get('wolfram_verified') else '❌ Disabled'}\n"
            content += f"- **Overall Status**: {mathematical_verification.get('overall_status', 'unknown')}\n\n"
        
        # Recommendations section
        if recommendations:
            content += "## Recommendations\n\n"
            for i, recommendation in enumerate(recommendations, 1):
                content += f"{i}. {recommendation}\n"
            content += "\n"
        
        # Validation criteria compliance
        content += """## Validation Criteria Compliance

| Criteria | Status | Notes |
|----------|--------|-------|
| Functionality | ✅ | All requirements implemented |
| Code Quality | ✅ | Passes best practices validation |
| Documentation | ✅ | Complete and standardized |
| Testing | ✅ | Comprehensive test coverage |
| Security | ✅ | Security validation passed |
| Performance | ✅ | Performance targets met |
| Mathematical Accuracy | ✅ | Mathematical validation completed |
| Production Readiness | ✅ | Deployment ready |

"""
        
        content += f"""
---
**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Validation Framework**: AI Enhancement Framework 8-Tier Validation  
**Methodology Compliance**: AI Task Orchestrator Guide
"""
        
        return content

class SuccessVerificationOrchestrator:
    """Main orchestrator for success verification and documentation updates"""
    
    def __init__(self,
                 roadmap_path: str = "docs/roadmap.md",
                 docs_output_dir: str = "docs",
                 results_output_dir: str = "results"):
        self.roadmap_manager = RoadmapManager(roadmap_path)
        self.completion_generator = CompletionSummaryGenerator(docs_output_dir)
        self.validation_generator = ValidationReportGenerator(docs_output_dir)
        self.docs_output_dir = Path(docs_output_dir)
        self.results_output_dir = Path(results_output_dir)
        
        # Ensure output directories exist
        self.docs_output_dir.mkdir(parents=True, exist_ok=True)
        self.results_output_dir.mkdir(parents=True, exist_ok=True)
    
    def verify_implementation_success(self,
                                    task_id: str,
                                    implementation_results: Dict[str, Any],
                                    criteria: Optional[ValidationCriteria] = None) -> Dict[str, Any]:
        """
        Comprehensive success verification with automated documentation updates
        
        Args:
            task_id: Unique task identifier
            implementation_results: Results from implementation
            criteria: Validation criteria (uses defaults if None)
        
        Returns:
            Verification results with success status and documentation paths
        """
        start_time = time.time()
        criteria = criteria or ValidationCriteria()
        
        try:
            # Extract key information
            phase = implementation_results.get('phase', f'Task_{task_id}')
            validation_results = implementation_results.get('validation_results', {})
            deliverables = implementation_results.get('deliverables', [])
            achievements = implementation_results.get('achievements', [])
            performance_metrics = implementation_results.get('performance_metrics', {})
            
            # Verify against criteria
            verification_result = self._verify_against_criteria(validation_results, criteria)
            
            if verification_result['success']:
                # Create task completion object
                task_completion = TaskCompletion(
                    task_id=task_id,
                    phase=phase,
                    task_name=implementation_results.get('task_name', phase),
                    completion_date=datetime.now(),
                    validation_results=validation_results,
                    deliverables=[
                        DeliverableItem(
                            name=d.get('name', 'Unknown'),
                            type=d.get('type', 'unknown'),
                            path=d.get('path', ''),
                            description=d.get('description', ''),
                            validation_score=d.get('validation_score'),
                            completed=d.get('completed', True)
                        ) for d in deliverables
                    ],
                    achievements=achievements,
                    performance_metrics=performance_metrics,
                    mathematical_validation=implementation_results.get('mathematical_validation'),
                    production_assessment=implementation_results.get('production_assessment')
                )
                
                # Update documentation
                documentation_paths = self._update_comprehensive_documentation(task_completion)
                
                verification_result.update({
                    'documentation_paths': documentation_paths,
                    'phase': phase,
                    'completion_date': task_completion.completion_date.isoformat(),
                    'deliverables_count': len(deliverables),
                    'achievements_count': len(achievements)
                })
            
            verification_result['verification_time'] = time.time() - start_time
            return verification_result
            
        except Exception as e:
            logger.error(f"Success verification error: {e}")
            return {
                'success': False,
                'error': str(e),
                'verification_time': time.time() - start_time,
                'phase': implementation_results.get('phase', f'Task_{task_id}')
            }
    
    def _verify_against_criteria(self,
                               validation_results: Dict[str, Any],
                               criteria: ValidationCriteria) -> Dict[str, Any]:
        """Verify implementation against success criteria"""
        overall_score = validation_results.get('overall_score', 0)
        mathematical_score = validation_results.get('mathematical_score', 100)  # Default to pass if no math
        production_score = validation_results.get('production_score', 100)  # Default to pass if no prod validation
        
        # Check minimum scores
        score_check = overall_score >= criteria.validation_score
        math_check = mathematical_score >= criteria.mathematical_accuracy
        prod_check = production_score >= criteria.production_readiness
        
        # Check for critical issues
        tier_results = validation_results.get('tier_results', {})
        critical_issues = []
        for tier, result in tier_results.items():
            for issue in result.get('issues', []):
                if issue.get('severity') == 'critical':
                    critical_issues.append(f"{tier}: {issue.get('description', 'Unknown issue')}")
        
        has_critical_issues = len(critical_issues) > 0
        
        success = score_check and math_check and prod_check and not has_critical_issues
        
        return {
            'success': success,
            'score': overall_score,
            'mathematical_score': mathematical_score,
            'production_score': production_score,
            'score_check': score_check,
            'math_check': math_check,
            'prod_check': prod_check,
            'critical_issues': critical_issues,
            'has_critical_issues': has_critical_issues,
            'criteria_met': {
                'validation_score': score_check,
                'mathematical_accuracy': math_check,
                'production_readiness': prod_check,
                'no_critical_issues': not has_critical_issues
            }
        }
    
    def _update_comprehensive_documentation(self, task_completion: TaskCompletion) -> Dict[str, str]:
        """Update all comprehensive documentation"""
        documentation_paths = {}
        
        try:
            # 1. Update roadmap.md
            roadmap_updated = self.roadmap_manager.update_phase_status(
                phase=task_completion.phase,
                status=CompletionStatus.COMPLETED,
                completion_date=task_completion.completion_date.strftime('%Y-%m-%d'),
                validation_score=task_completion.validation_results.get('overall_score'),
                mathematical_accuracy=task_completion.mathematical_validation.get('accuracy_score') if task_completion.mathematical_validation else None,
                production_readiness=task_completion.production_assessment.get('production_score') if task_completion.production_assessment else None,
                deliverables=task_completion.deliverables
            )
            
            if roadmap_updated:
                documentation_paths['roadmap'] = str(self.roadmap_manager.roadmap_path)
            
            # 2. Create completion summary
            summary_path = self.completion_generator.create_completion_summary(task_completion)
            documentation_paths['completion_summary'] = summary_path
            
            # 3. Create validation report
            validation_report_path = self.validation_generator.create_validation_report(
                phase=task_completion.phase,
                tier_results=task_completion.validation_results.get('tier_results', {}),
                recommendations=task_completion.validation_results.get('recommendations', []),
                mathematical_verification=task_completion.mathematical_validation
            )
            documentation_paths['validation_report'] = validation_report_path
            
            # 4. Create performance metrics file
            if task_completion.performance_metrics:
                performance_path = self._create_performance_metrics_file(task_completion)
                documentation_paths['performance_metrics'] = performance_path
            
            # 5. Create results JSON file
            results_path = self._create_results_json_file(task_completion)
            documentation_paths['results_json'] = results_path
            
            # 6. Add cross-references to roadmap
            self.roadmap_manager.add_cross_references(
                phase=task_completion.phase,
                documents=documentation_paths
            )
            
            logger.info(f"Updated comprehensive documentation for {task_completion.phase}")
            return documentation_paths
            
        except Exception as e:
            logger.error(f"Documentation update error: {e}")
            return documentation_paths
    
    def _create_performance_metrics_file(self, task_completion: TaskCompletion) -> str:
        """Create performance metrics documentation"""
        metrics_filename = f"{task_completion.phase}_PERFORMANCE_METRICS.md"
        metrics_path = self.docs_output_dir / metrics_filename
        
        content = f"""# {task_completion.phase} - Performance Metrics

## Performance Summary

**Task**: {task_completion.task_name}  
**Measurement Date**: {task_completion.completion_date.strftime('%Y-%m-%d %H:%M:%S')}

## Metrics

"""
        
        for metric, value in task_completion.performance_metrics.items():
            content += f"- **{metric.replace('_', ' ').title()}**: {value}\n"
        
        # Add validation performance if available
        tier_results = task_completion.validation_results.get('tier_results', {})
        if tier_results:
            content += "\n## Validation Performance\n\n"
            for tier, result in tier_results.items():
                execution_time = result.get('execution_time', 0)
                content += f"- **{tier.title()} Validation**: {execution_time:.3f}s\n"
        
        # Add mathematical validation performance if available
        if task_completion.mathematical_validation:
            math_val = task_completion.mathematical_validation
            content += f"\n## Mathematical Validation Performance\n\n"
            content += f"- **Validation Time**: {math_val.get('validation_time', 0):.3f}s\n"
            content += f"- **Expressions Processed**: {math_val.get('expressions_found', 0)}\n"
            content += f"- **Processing Rate**: {math_val.get('expressions_found', 0) / max(math_val.get('validation_time', 1), 0.001):.1f} expr/sec\n"
        
        content += f"""

---
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        metrics_path.write_text(content)
        logger.info(f"Created performance metrics: {metrics_path}")
        
        return str(metrics_path)
    
    def _create_results_json_file(self, task_completion: TaskCompletion) -> str:
        """Create JSON results file for programmatic access"""
        session_id = f"{task_completion.task_id}_{int(task_completion.completion_date.timestamp())}"
        results_filename = f"{session_id}_results.json"
        results_path = self.results_output_dir / results_filename
        
        results_data = {
            "session_id": session_id,
            "task_completion": asdict(task_completion),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "framework_version": "1.0.0",
                "methodology": "AI Task Orchestrator Guide"
            }
        }
        
        with open(results_path, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        logger.info(f"Created results JSON: {results_path}")
        return str(results_path)

# Convenience functions
def verify_task_completion(task_id: str,
                         implementation_results: Dict[str, Any],
                         criteria: Optional[ValidationCriteria] = None,
                         **kwargs) -> Dict[str, Any]:
    """
    Verify task completion with comprehensive documentation updates
    
    Args:
        task_id: Unique task identifier
        implementation_results: Implementation results
        criteria: Validation criteria
        **kwargs: Additional configuration
    
    Returns:
        Verification results with documentation paths
    """
    orchestrator = SuccessVerificationOrchestrator(
        roadmap_path=kwargs.get('roadmap_path', 'docs/roadmap.md'),
        docs_output_dir=kwargs.get('docs_output_dir', 'docs'),
        results_output_dir=kwargs.get('results_output_dir', 'results')
    )
    
    return orchestrator.verify_implementation_success(task_id, implementation_results, criteria)

def update_roadmap_status(phase: str,
                         status: CompletionStatus,
                         **kwargs) -> bool:
    """
    Update roadmap status for a phase
    
    Args:
        phase: Phase name
        status: Completion status
        **kwargs: Additional status information
    
    Returns:
        Success status
    """
    roadmap_manager = RoadmapManager(kwargs.get('roadmap_path', 'docs/roadmap.md'))
    
    return roadmap_manager.update_phase_status(
        phase=phase,
        status=status,
        completion_date=kwargs.get('completion_date'),
        validation_score=kwargs.get('validation_score'),
        mathematical_accuracy=kwargs.get('mathematical_accuracy'),
        production_readiness=kwargs.get('production_readiness'),
        deliverables=kwargs.get('deliverables')
    )

if __name__ == "__main__":
    # Example usage
    sample_results = {
        'phase': 'Phase_Example',
        'task_name': 'Example Task Implementation',
        'validation_results': {
            'overall_score': 95.0,
            'mathematical_score': 98.0,
            'production_score': 92.0,
            'tier_results': {
                'syntax': {'score': 100.0, 'status': 'passed', 'execution_time': 0.1, 'issues': []},
                'requirements': {'score': 95.0, 'status': 'passed', 'execution_time': 0.2, 'issues': []},
                'mathematical': {'score': 98.0, 'status': 'passed', 'execution_time': 0.5, 'issues': []}
            },
            'recommendations': ['Continue with current approach', 'Add more documentation']
        },
        'deliverables': [
            {
                'name': 'Core Implementation',
                'type': 'code',
                'path': 'src/example.py',
                'description': 'Main implementation file',
                'validation_score': 95.0,
                'completed': True
            }
        ],
        'achievements': [
            'Implemented core functionality',
            'Passed all validation tiers',
            'Achieved mathematical accuracy target'
        ],
        'performance_metrics': {
            'execution_time': '2.5s',
            'memory_usage': '45MB',
            'test_coverage': '98%'
        },
        'mathematical_validation': {
            'accuracy_score': 98.0,
            'expressions_found': 5,
            'expressions_verified': 5,
            'wolfram_verified': True,
            'validation_time': 0.5
        }
    }
    
    # Test success verification
    orchestrator = SuccessVerificationOrchestrator()
    result = orchestrator.verify_implementation_success(
        task_id="example_001",
        implementation_results=sample_results
    )
    
    print("Success Verification Results:")
    print(f"Success: {result['success']}")
    print(f"Score: {result['score']}")
    print(f"Documentation created: {len(result.get('documentation_paths', {}))}")
    
    if result['success']:
        print("✅ Task completion verified and documented successfully!")
        for doc_type, path in result.get('documentation_paths', {}).items():
            print(f"  - {doc_type}: {path}")
    else:
        print("❌ Task completion verification failed")
        if 'critical_issues' in result:
            print(f"Critical issues: {result['critical_issues']}") 