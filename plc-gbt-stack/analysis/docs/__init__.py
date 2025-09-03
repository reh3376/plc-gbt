#!/usr/bin/env python3
"""
Phase 22.5: Task 22.5.4 - Documentation Generator Package
=========================================================

Documentation generation system including:
- Automatic analysis documentation
- Tuning recommendation reports
- Change impact assessments
- Compliance documentation

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.5.4 - Documentation Generator
Methodology: AI Task Orchestrator Guide
"""

__version__ = "1.0.0"
__author__ = "PLC-GPT Development Team"
__phase__ = "22.5.4"

# Documentation generator configuration
DOCUMENTATION_CONFIG = {
    "version": __version__,
    "supported_formats": [
        "markdown",
        "html",
        "pdf",
        "docx",
        "latex",
        "rst"
    ],
    "document_types": {
        "analysis_report": {
            "sections": ["summary", "methodology", "results", "conclusions", "appendices"],
            "templates": ["technical", "executive", "detailed"],
            "target_audience": "engineers"
        },
        "tuning_recommendations": {
            "sections": ["current_state", "recommendations", "implementation", "risks"],
            "templates": ["standard", "detailed", "quick_reference"],
            "target_audience": "operators"
        },
        "change_impact": {
            "sections": ["overview", "affected_systems", "risk_assessment", "mitigation"],
            "templates": ["formal", "summary", "technical"],
            "target_audience": "management"
        },
        "compliance_report": {
            "sections": ["requirements", "current_compliance", "gaps", "remediation"],
            "templates": ["regulatory", "audit", "certification"],
            "target_audience": "regulatory"
        }
    },
    "compliance_standards": {
        "isa_95": {
            "name": "ISA-95 Enterprise-Control System Integration",
            "requirements": ["data_integrity", "traceability", "security"],
            "documentation_level": "comprehensive"
        },
        "isa_88": {
            "name": "ISA-88 Batch Control",
            "requirements": ["recipe_management", "equipment_control", "batch_tracking"],
            "documentation_level": "detailed"
        },
        "fda_21cfr11": {
            "name": "FDA 21 CFR Part 11",
            "requirements": ["electronic_records", "electronic_signatures", "audit_trails"],
            "documentation_level": "comprehensive"
        },
        "iec_61511": {
            "name": "IEC 61511 Safety Instrumented Systems",
            "requirements": ["safety_integrity", "verification", "validation"],
            "documentation_level": "comprehensive"
        }
    },
    "auto_generation": {
        "analysis_docs": True,
        "change_tracking": True,
        "version_control": True,
        "cross_references": True,
        "index_generation": True
    },
    "template_settings": {
        "include_toc": True,
        "include_index": True,
        "include_glossary": True,
        "page_numbering": True,
        "header_footer": True,
        "watermark": False
    }
}

# Documentation types and enums
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


class DocumentType(Enum):
    """Document type enumeration"""
    ANALYSIS_REPORT = "analysis_report"
    TUNING_RECOMMENDATIONS = "tuning_recommendations"
    CHANGE_IMPACT = "change_impact"
    COMPLIANCE_REPORT = "compliance_report"
    TECHNICAL_MANUAL = "technical_manual"
    USER_GUIDE = "user_guide"

class DocumentFormat(Enum):
    """Document output formats"""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    LATEX = "latex"
    RST = "rst"

class TemplateStyle(Enum):
    """Document template styles"""
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    DETAILED = "detailed"
    SUMMARY = "summary"
    FORMAL = "formal"
    QUICK_REFERENCE = "quick_reference"

class ComplianceStandard(Enum):
    """Compliance standards"""
    ISA_95 = "isa_95"
    ISA_88 = "isa_88"
    FDA_21CFR11 = "fda_21cfr11"
    IEC_61511 = "iec_61511"
    ISO_9001 = "iso_9001"

@dataclass
class DocumentConfiguration:
    """Configuration for document generation"""
    document_id: str
    title: str
    document_type: DocumentType
    output_format: DocumentFormat
    template_style: TemplateStyle = TemplateStyle.TECHNICAL

    # Content settings
    sections: List[str] = field(default_factory=list)
    include_appendices: bool = True
    include_references: bool = True
    include_glossary: bool = False

    # Formatting settings
    page_size: str = "A4"
    font_family: str = "Arial"
    font_size: int = 11
    line_spacing: float = 1.15

    # Metadata
    author: str = "PLC-GPT Analysis System"
    company: str = "Industrial Control Systems"
    version: str = "1.0"
    classification: str = "Internal Use"

    # Generation options
    auto_numbering: bool = True
    cross_references: bool = True
    table_of_contents: bool = True

    # Output settings
    output_path: Optional[str] = None
    filename_template: str = "{document_type}_{timestamp}"

@dataclass
class AnalysisDocumentData:
    """Data for analysis documentation"""
    analysis_id: str
    analysis_type: str
    methodology: str

    # Analysis results
    key_findings: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    statistical_results: Dict[str, Any] = field(default_factory=dict)

    # Data sources and quality
    data_sources: List[str] = field(default_factory=list)
    data_quality_score: float = 1.0
    analysis_period: Optional[tuple] = None

    # Visualizations
    charts: List[str] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)

    # Conclusions and recommendations
    conclusions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

@dataclass
class TuningRecommendationData:
    """Data for tuning recommendation documentation"""
    loop_id: str
    current_tuning: Dict[str, float]
    recommended_tuning: Dict[str, float]

    # Performance analysis
    current_performance: Dict[str, float] = field(default_factory=dict)
    expected_improvement: Dict[str, float] = field(default_factory=dict)

    # Implementation details
    implementation_steps: List[str] = field(default_factory=list)
    implementation_time: str = "30 minutes"
    required_tools: List[str] = field(default_factory=list)

    # Risk assessment
    risk_level: str = "low"
    potential_issues: List[str] = field(default_factory=list)
    rollback_procedure: List[str] = field(default_factory=list)

    # Validation
    validation_criteria: List[str] = field(default_factory=list)
    success_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class ChangeImpactData:
    """Data for change impact assessment"""
    change_id: str
    change_description: str
    change_type: str  # "tuning", "configuration", "hardware", "software"

    # Impact analysis
    affected_loops: List[str] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    impact_severity: str = "medium"  # "low", "medium", "high", "critical"

    # Risk assessment
    identified_risks: List[Dict[str, Any]] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    contingency_plans: List[str] = field(default_factory=list)

    # Implementation plan
    implementation_phases: List[Dict[str, Any]] = field(default_factory=list)
    testing_requirements: List[str] = field(default_factory=list)
    rollback_plan: List[str] = field(default_factory=list)

    # Approval and tracking
    required_approvals: List[str] = field(default_factory=list)
    tracking_metrics: List[str] = field(default_factory=list)

@dataclass
class ComplianceDocumentData:
    """Data for compliance documentation"""
    audit_id: str
    standard: ComplianceStandard
    assessment_date: datetime

    # Compliance assessment
    requirements_checked: List[str] = field(default_factory=list)
    compliant_items: List[str] = field(default_factory=list)
    non_compliant_items: List[str] = field(default_factory=list)

    # Gap analysis
    identified_gaps: List[Dict[str, Any]] = field(default_factory=list)
    remediation_actions: List[Dict[str, Any]] = field(default_factory=list)

    # Evidence and documentation
    evidence_files: List[str] = field(default_factory=list)
    supporting_documents: List[str] = field(default_factory=list)

    # Action plan
    corrective_actions: List[Dict[str, Any]] = field(default_factory=list)
    target_completion: Optional[datetime] = None
    responsible_parties: List[str] = field(default_factory=list)

@dataclass
class DocumentGenerationResult:
    """Result of document generation"""
    success: bool
    document_id: str
    output_path: str

    # Document metadata
    format: str
    file_size: int
    page_count: int
    section_count: int

    # Generation metrics
    generation_time: float
    word_count: int
    image_count: int
    table_count: int

    # Quality metrics
    completeness_score: float
    readability_score: float
    compliance_score: float

    # Issues and warnings
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

# Import documentation modules
try:
    from .auto_formatter import AutoFormatter
    from .compliance_checker import ComplianceChecker
    from .doc_generator import DocumentGenerator
    from .template_engine import TemplateEngine
    DOCUMENTATION_MODULES_AVAILABLE = True
except ImportError:
    DOCUMENTATION_MODULES_AVAILABLE = False

# Module availability status
AVAILABILITY_STATUS = {
    "doc_generator": DOCUMENTATION_MODULES_AVAILABLE,
    "template_engine": DOCUMENTATION_MODULES_AVAILABLE,
    "compliance_checker": DOCUMENTATION_MODULES_AVAILABLE,
    "auto_formatter": DOCUMENTATION_MODULES_AVAILABLE
}

def get_available_formats():
    """Get list of available document formats"""
    return DOCUMENTATION_CONFIG["supported_formats"]

def get_format_info(format_type: str):
    """Get detailed information about a document format"""
    info = {
        "markdown": {
            "name": "Markdown",
            "description": "Lightweight markup language for structured text",
            "pros": ["Human readable", "Version control friendly", "Platform independent"],
            "cons": ["Limited formatting", "No page layout", "Requires rendering"],
            "best_for": ["Technical documentation", "README files", "Wiki content"],
            "supports_images": True,
            "supports_tables": True
        },
        "html": {
            "name": "HyperText Markup Language",
            "description": "Web-based document format with rich formatting",
            "pros": ["Interactive content", "Rich formatting", "Cross-platform"],
            "cons": ["Requires browser", "Complex styling", "Not printable"],
            "best_for": ["Online documentation", "Interactive reports", "Dashboards"],
            "supports_images": True,
            "supports_tables": True
        },
        "pdf": {
            "name": "Portable Document Format",
            "description": "Professional document format for printing and distribution",
            "pros": ["Print ready", "Consistent layout", "Professional appearance"],
            "cons": ["Not editable", "Large file size", "Limited interactivity"],
            "best_for": ["Final reports", "Compliance documents", "Distribution"],
            "supports_images": True,
            "supports_tables": True
        },
        "docx": {
            "name": "Microsoft Word Document",
            "description": "Editable document format with advanced formatting",
            "pros": ["Fully editable", "Advanced formatting", "Comments and tracking"],
            "cons": ["Proprietary format", "Version compatibility", "Software dependency"],
            "best_for": ["Collaborative editing", "Complex formatting", "Review cycles"],
            "supports_images": True,
            "supports_tables": True
        }
    }
    return info.get(format_type, {"description": "Unknown format"})

def get_template_info(template_style: str):
    """Get information about document templates"""
    templates = {
        "technical": {
            "description": "Detailed technical documentation with code examples",
            "target_audience": "Engineers and technical staff",
            "sections": ["Introduction", "Methodology", "Technical Details", "Results", "Conclusions"],
            "formatting": "Monospace code blocks, technical diagrams, detailed appendices"
        },
        "executive": {
            "description": "High-level summary for decision makers",
            "target_audience": "Management and executives",
            "sections": ["Executive Summary", "Key Findings", "Recommendations", "Business Impact"],
            "formatting": "Large fonts, bullet points, charts and graphs"
        },
        "detailed": {
            "description": "Comprehensive documentation with full analysis",
            "target_audience": "Specialists and analysts",
            "sections": ["Background", "Analysis", "Detailed Results", "Discussion", "References"],
            "formatting": "Academic style, extensive references, detailed tables"
        },
        "summary": {
            "description": "Concise overview highlighting key points",
            "target_audience": "General audience",
            "sections": ["Overview", "Key Points", "Summary", "Next Steps"],
            "formatting": "Bullet points, short paragraphs, visual emphasis"
        }
    }
    return templates.get(template_style, {"description": "Unknown template"})

def generate_analysis_document(data: AnalysisDocumentData,
                             config: DocumentConfiguration) -> DocumentGenerationResult:
    """Generate analysis documentation"""

    start_time = datetime.now()

    # Validate inputs
    if not data.analysis_id:
        return DocumentGenerationResult(
            success=False,
            document_id=config.document_id,
            output_path="",
            format=config.output_format.value,
            file_size=0,
            page_count=0,
            section_count=0,
            generation_time=0.0,
            word_count=0,
            image_count=0,
            table_count=0,
            completeness_score=0.0,
            readability_score=0.0,
            compliance_score=0.0,
            errors=["Missing analysis_id in data"]
        )

    # Generate document content
    content = _generate_analysis_content(data, config)

    # Format document
    formatted_content = _format_document(content, config)

    # Write to file
    output_path = _write_document(formatted_content, config)

    # Calculate metrics
    generation_time = (datetime.now() - start_time).total_seconds()
    word_count = len(formatted_content.split())

    return DocumentGenerationResult(
        success=True,
        document_id=config.document_id,
        output_path=output_path,
        format=config.output_format.value,
        file_size=len(formatted_content.encode('utf-8')),
        page_count=max(1, word_count // 250),  # Estimate 250 words per page
        section_count=len(config.sections),
        generation_time=generation_time,
        word_count=word_count,
        image_count=len(data.charts),
        table_count=len(data.tables),
        completeness_score=_calculate_completeness(data),
        readability_score=_calculate_readability(formatted_content),
        compliance_score=1.0,  # Assume full compliance for analysis docs
        metadata={
            "analysis_type": data.analysis_type,
            "data_quality": data.data_quality_score,
            "generation_timestamp": datetime.now().isoformat()
        }
    )

def generate_tuning_recommendations(data: TuningRecommendationData,
                                  config: DocumentConfiguration) -> DocumentGenerationResult:
    """Generate tuning recommendation documentation"""

    start_time = datetime.now()

    # Generate content
    content = _generate_tuning_content(data, config)
    formatted_content = _format_document(content, config)
    output_path = _write_document(formatted_content, config)

    generation_time = (datetime.now() - start_time).total_seconds()
    word_count = len(formatted_content.split())

    return DocumentGenerationResult(
        success=True,
        document_id=config.document_id,
        output_path=output_path,
        format=config.output_format.value,
        file_size=len(formatted_content.encode('utf-8')),
        page_count=max(1, word_count // 250),
        section_count=len(config.sections),
        generation_time=generation_time,
        word_count=word_count,
        image_count=0,
        table_count=2,  # Current vs recommended tuning tables
        completeness_score=_calculate_tuning_completeness(data),
        readability_score=_calculate_readability(formatted_content),
        compliance_score=_assess_tuning_compliance(data),
        metadata={
            "loop_id": data.loop_id,
            "risk_level": data.risk_level,
            "implementation_time": data.implementation_time
        }
    )

def generate_change_impact_assessment(data: ChangeImpactData,
                                    config: DocumentConfiguration) -> DocumentGenerationResult:
    """Generate change impact assessment documentation"""

    start_time = datetime.now()

    # Generate content
    content = _generate_change_impact_content(data, config)
    formatted_content = _format_document(content, config)
    output_path = _write_document(formatted_content, config)

    generation_time = (datetime.now() - start_time).total_seconds()
    word_count = len(formatted_content.split())

    return DocumentGenerationResult(
        success=True,
        document_id=config.document_id,
        output_path=output_path,
        format=config.output_format.value,
        file_size=len(formatted_content.encode('utf-8')),
        page_count=max(1, word_count // 250),
        section_count=len(config.sections),
        generation_time=generation_time,
        word_count=word_count,
        image_count=0,
        table_count=len(data.implementation_phases) + 1,
        completeness_score=_calculate_change_completeness(data),
        readability_score=_calculate_readability(formatted_content),
        compliance_score=_assess_change_compliance(data),
        metadata={
            "change_id": data.change_id,
            "impact_severity": data.impact_severity,
            "affected_systems": len(data.affected_systems)
        }
    )

def generate_compliance_documentation(data: ComplianceDocumentData,
                                    config: DocumentConfiguration) -> DocumentGenerationResult:
    """Generate compliance documentation"""

    start_time = datetime.now()

    # Generate content
    content = _generate_compliance_content(data, config)
    formatted_content = _format_document(content, config)
    output_path = _write_document(formatted_content, config)

    generation_time = (datetime.now() - start_time).total_seconds()
    word_count = len(formatted_content.split())

    compliance_score = len(data.compliant_items) / len(data.requirements_checked) if data.requirements_checked else 0.0

    return DocumentGenerationResult(
        success=True,
        document_id=config.document_id,
        output_path=output_path,
        format=config.output_format.value,
        file_size=len(formatted_content.encode('utf-8')),
        page_count=max(1, word_count // 250),
        section_count=len(config.sections),
        generation_time=generation_time,
        word_count=word_count,
        image_count=0,
        table_count=len(data.identified_gaps) + 2,
        completeness_score=_calculate_compliance_completeness(data),
        readability_score=_calculate_readability(formatted_content),
        compliance_score=compliance_score,
        metadata={
            "audit_id": data.audit_id,
            "standard": data.standard.value,
            "assessment_date": data.assessment_date.isoformat(),
            "gaps_identified": len(data.identified_gaps)
        }
    )

def _generate_analysis_content(data: AnalysisDocumentData, config: DocumentConfiguration) -> str:
    """Generate content for analysis documentation"""

    content = f"""# {config.title}

## Executive Summary

Analysis ID: {data.analysis_id}
Analysis Type: {data.analysis_type}
Data Quality Score: {data.data_quality_score:.2f}

## Methodology

{data.methodology}

## Key Findings

"""

    for i, finding in enumerate(data.key_findings, 1):
        content += f"{i}. {finding}\n"

    content += "\n## Performance Metrics\n\n"

    for metric, value in data.performance_metrics.items():
        content += f"- **{metric.replace('_', ' ').title()}**: {value:.3f}\n"

    content += "\n## Conclusions\n\n"

    for i, conclusion in enumerate(data.conclusions, 1):
        content += f"{i}. {conclusion}\n"

    content += "\n## Recommendations\n\n"

    for i, recommendation in enumerate(data.recommendations, 1):
        content += f"{i}. {recommendation}\n"

    if data.next_steps:
        content += "\n## Next Steps\n\n"
        for i, step in enumerate(data.next_steps, 1):
            content += f"{i}. {step}\n"

    return content

def _generate_tuning_content(data: TuningRecommendationData, config: DocumentConfiguration) -> str:
    """Generate content for tuning recommendations"""

    content = f"""# {config.title}

## Loop Information

**Loop ID**: {data.loop_id}
**Risk Level**: {data.risk_level.upper()}
**Implementation Time**: {data.implementation_time}

## Current Tuning Parameters

"""

    for param, value in data.current_tuning.items():
        content += f"- **{param}**: {value}\n"

    content += "\n## Recommended Tuning Parameters\n\n"

    for param, value in data.recommended_tuning.items():
        content += f"- **{param}**: {value}\n"

    content += "\n## Expected Performance Improvement\n\n"

    for metric, improvement in data.expected_improvement.items():
        content += f"- **{metric.replace('_', ' ').title()}**: {improvement:+.1f}%\n"

    content += "\n## Implementation Steps\n\n"

    for i, step in enumerate(data.implementation_steps, 1):
        content += f"{i}. {step}\n"

    if data.potential_issues:
        content += "\n## Potential Issues and Risks\n\n"
        for issue in data.potential_issues:
            content += f"- {issue}\n"

    content += "\n## Rollback Procedure\n\n"

    for i, step in enumerate(data.rollback_procedure, 1):
        content += f"{i}. {step}\n"

    return content

def _generate_change_impact_content(data: ChangeImpactData, config: DocumentConfiguration) -> str:
    """Generate content for change impact assessment"""

    content = f"""# {config.title}

## Change Overview

**Change ID**: {data.change_id}
**Description**: {data.change_description}
**Type**: {data.change_type}
**Impact Severity**: {data.impact_severity.upper()}

## Affected Systems

"""

    for system in data.affected_systems:
        content += f"- {system}\n"

    content += "\n## Affected Control Loops\n\n"

    for loop in data.affected_loops:
        content += f"- {loop}\n"

    content += "\n## Risk Assessment\n\n"

    for risk in data.identified_risks:
        content += f"- **{risk.get('name', 'Unknown Risk')}** (Probability: {risk.get('probability', 'Unknown')}, Impact: {risk.get('impact', 'Unknown')})\n"
        content += f"  {risk.get('description', 'No description provided')}\n\n"

    content += "## Mitigation Strategies\n\n"

    for i, strategy in enumerate(data.mitigation_strategies, 1):
        content += f"{i}. {strategy}\n"

    content += "\n## Implementation Plan\n\n"

    for i, phase in enumerate(data.implementation_phases, 1):
        content += f"### Phase {i}: {phase.get('name', f'Phase {i}')}\n\n"
        content += f"- **Duration**: {phase.get('duration', 'TBD')}\n"
        content += f"- **Description**: {phase.get('description', 'No description')}\n\n"

    return content

def _generate_compliance_content(data: ComplianceDocumentData, config: DocumentConfiguration) -> str:
    """Generate content for compliance documentation"""

    standard_info = DOCUMENTATION_CONFIG["compliance_standards"].get(data.standard.value, {})

    content = f"""# {config.title}

## Compliance Assessment Overview

**Audit ID**: {data.audit_id}
**Standard**: {standard_info.get('name', data.standard.value)}
**Assessment Date**: {data.assessment_date.strftime('%Y-%m-%d')}
**Overall Compliance**: {len(data.compliant_items)}/{len(data.requirements_checked)} ({len(data.compliant_items)/len(data.requirements_checked)*100:.1f}%)

## Requirements Assessment

### Compliant Items

"""

    for item in data.compliant_items:
        content += f"✅ {item}\n"

    content += "\n### Non-Compliant Items\n\n"

    for item in data.non_compliant_items:
        content += f"❌ {item}\n"

    content += "\n## Gap Analysis\n\n"

    for gap in data.identified_gaps:
        content += f"### {gap.get('title', 'Identified Gap')}\n\n"
        content += f"**Severity**: {gap.get('severity', 'Unknown')}\n"
        content += f"**Description**: {gap.get('description', 'No description')}\n"
        content += f"**Impact**: {gap.get('impact', 'No impact assessment')}\n\n"

    content += "## Corrective Actions\n\n"

    for action in data.corrective_actions:
        content += f"- **{action.get('title', 'Action')}**\n"
        content += f"  - Responsible: {action.get('responsible', 'TBD')}\n"
        content += f"  - Due Date: {action.get('due_date', 'TBD')}\n"
        content += f"  - Priority: {action.get('priority', 'Medium')}\n\n"

    return content

def _format_document(content: str, config: DocumentConfiguration) -> str:
    """Format document based on output format"""

    if config.output_format == DocumentFormat.MARKDOWN:
        return content  # Already in markdown

    elif config.output_format == DocumentFormat.HTML:
        # Basic HTML conversion
        html_content = content.replace('\n', '<br>\n')
        html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n', 1)
        return f"<html><body>{html_content}</body></html>"

    else:
        # For other formats, return markdown (would need specialized libraries)
        return content

def _write_document(content: str, config: DocumentConfiguration) -> str:
    """Write document to file"""

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = config.filename_template.format(
        document_type=config.document_type.value,
        timestamp=timestamp
    )

    # Determine output path
    if config.output_path:
        output_path = Path(config.output_path) / f"{filename}.{config.output_format.value}"
    else:
        output_path = Path(f"{filename}.{config.output_format.value}")

    # Create directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return str(output_path)

def _calculate_completeness(data: AnalysisDocumentData) -> float:
    """Calculate document completeness score"""

    required_fields = ['analysis_id', 'analysis_type', 'methodology']
    optional_fields = ['key_findings', 'performance_metrics', 'conclusions', 'recommendations']

    required_score = sum(1 for field in required_fields if getattr(data, field, None))
    optional_score = sum(1 for field in optional_fields if getattr(data, field, None))

    total_possible = len(required_fields) + len(optional_fields)
    total_present = required_score + optional_score

    return total_present / total_possible

def _calculate_tuning_completeness(data: TuningRecommendationData) -> float:
    """Calculate tuning document completeness"""

    completeness = 0.0
    total_checks = 7

    if data.loop_id: completeness += 1
    if data.current_tuning: completeness += 1
    if data.recommended_tuning: completeness += 1
    if data.implementation_steps: completeness += 1
    if data.rollback_procedure: completeness += 1
    if data.validation_criteria: completeness += 1
    if data.risk_level: completeness += 1

    return completeness / total_checks

def _calculate_change_completeness(data: ChangeImpactData) -> float:
    """Calculate change impact document completeness"""

    completeness = 0.0
    total_checks = 6

    if data.change_id: completeness += 1
    if data.affected_systems: completeness += 1
    if data.identified_risks: completeness += 1
    if data.mitigation_strategies: completeness += 1
    if data.implementation_phases: completeness += 1
    if data.rollback_plan: completeness += 1

    return completeness / total_checks

def _calculate_compliance_completeness(data: ComplianceDocumentData) -> float:
    """Calculate compliance document completeness"""

    completeness = 0.0
    total_checks = 5

    if data.audit_id: completeness += 1
    if data.requirements_checked: completeness += 1
    if data.identified_gaps: completeness += 1
    if data.corrective_actions: completeness += 1
    if data.responsible_parties: completeness += 1

    return completeness / total_checks

def _calculate_readability(content: str) -> float:
    """Calculate document readability score (simplified)"""

    words = content.split()
    sentences = content.count('.') + content.count('!') + content.count('?')

    if sentences == 0:
        return 0.5

    avg_words_per_sentence = len(words) / sentences

    # Simple readability score (higher is better, max 1.0)
    if avg_words_per_sentence <= 15:
        return 1.0
    elif avg_words_per_sentence <= 20:
        return 0.8
    elif avg_words_per_sentence <= 25:
        return 0.6
    else:
        return 0.4

def _assess_tuning_compliance(data: TuningRecommendationData) -> float:
    """Assess compliance of tuning recommendations"""

    # Check if safety guidelines are followed
    compliance_score = 1.0

    # Check if risk assessment is provided
    if not data.risk_level:
        compliance_score -= 0.2

    # Check if rollback procedure exists
    if not data.rollback_procedure:
        compliance_score -= 0.3

    # Check if validation criteria are defined
    if not data.validation_criteria:
        compliance_score -= 0.2

    return max(0.0, compliance_score)

def _assess_change_compliance(data: ChangeImpactData) -> float:
    """Assess compliance of change impact assessment"""

    compliance_score = 1.0

    # Check required elements for change management
    if not data.identified_risks:
        compliance_score -= 0.3

    if not data.mitigation_strategies:
        compliance_score -= 0.3

    if not data.required_approvals:
        compliance_score -= 0.2

    if not data.rollback_plan:
        compliance_score -= 0.2

    return max(0.0, compliance_score)

# Export configuration for external use
__all__ = [
    # Configuration
    "DOCUMENTATION_CONFIG",
    "AVAILABILITY_STATUS",

    # Data classes
    "DocumentConfiguration",
    "AnalysisDocumentData",
    "TuningRecommendationData",
    "ChangeImpactData",
    "ComplianceDocumentData",
    "DocumentGenerationResult",

    # Enums
    "DocumentType",
    "DocumentFormat",
    "TemplateStyle",
    "ComplianceStandard",

    # Utility functions
    "get_available_formats",
    "get_format_info",
    "get_template_info",
    "generate_analysis_document",
    "generate_tuning_recommendations",
    "generate_change_impact_assessment",
    "generate_compliance_documentation",

    # Classes (if available)
]

# Add available classes to exports
if DOCUMENTATION_MODULES_AVAILABLE:
    __all__.extend([
        "DocumentGenerator",
        "TemplateEngine",
        "ComplianceChecker",
        "AutoFormatter"
    ])

# Package version and status information
def get_package_info():
    """Get comprehensive package information"""
    return {
        "version": __version__,
        "phase": __phase__,
        "author": __author__,
        "available_formats": get_available_formats(),
        "document_types": list(DOCUMENTATION_CONFIG["document_types"].keys()),
        "compliance_standards": list(DOCUMENTATION_CONFIG["compliance_standards"].keys()),
        "total_available": len([v for v in AVAILABILITY_STATUS.values() if v]),
        "total_modules": len(AVAILABILITY_STATUS),
        "completion_percentage": len([v for v in AVAILABILITY_STATUS.values() if v]) / len(AVAILABILITY_STATUS) * 100,
        "implementation_status": AVAILABILITY_STATUS
    }
