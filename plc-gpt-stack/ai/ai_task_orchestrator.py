#!/usr/bin/env python3
"""
AI Task Orchestrator - Structured Framework for Coding Task Completion
Provides AI agents and LLMs with systematic task analysis, planning, and execution.

This module ensures:
- Structured task decomposition and planning
- Resource discovery and utilization
- Context management for complex tasks
- Hallucination prevention and validation
- Progress tracking and documentation
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib
import re

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from . import ai_agent_resources as ai_resources
    AI_RESOURCES_AVAILABLE = True
except ImportError:
    AI_RESOURCES_AVAILABLE = False
    print("⚠️  ai_agent_resources not available - limited functionality")

try:
    import structlog
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class TaskComplexity:
    """Task complexity levels for planning."""
    SIMPLE = "simple"      # < 100 lines, single file
    MODERATE = "moderate"  # 100-500 lines, few files
    COMPLEX = "complex"    # 500-1500 lines, multiple files
    EXTENSIVE = "extensive" # > 1500 lines, major changes


class AITaskOrchestrator:
    """
    Comprehensive framework for AI agents to complete coding tasks systematically.
    
    Features:
    - Task analysis and decomposition
    - Resource discovery and review
    - Context management and planning
    - Validation and hallucination prevention
    - Progress tracking and documentation
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the task orchestrator.
        
        Args:
            project_root: Root directory of the project (auto-detected if None)
        """
        self.project_root = Path(project_root) if project_root else self._detect_project_root()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ai_task_"))
        self.task_id = self._generate_task_id()
        self.session_log = []
        self.validation_results = {}
        
        logger.info(f"Task orchestrator initialized: {self.task_id}")
        
    def _detect_project_root(self) -> Path:
        """Auto-detect project root directory."""
        current = Path.cwd()
        
        # Look for project markers
        markers = ['.git', 'README.md', 'pyproject.toml', 'package.json', 'docs/', 'plc-gpt-stack/']
        
        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent
            
        return Path.cwd()
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"task_{timestamp}_{random_suffix}"
    
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Comprehensive task analysis and planning.
        
        Args:
            task_description: Description of the task to complete
            
        Returns:
            Task analysis with complexity, requirements, and plan
        """
        logger.info("Starting task analysis")
        
        analysis = {
            "task_id": self.task_id,
            "description": task_description,
            "timestamp": datetime.now().isoformat(),
            "complexity": self._assess_complexity(task_description),
            "requirements": self._extract_requirements(task_description),
            "resources_needed": self._identify_resources(task_description),
            "risks": self._identify_risks(task_description),
            "validation_criteria": self._define_validation_criteria(task_description),
            "estimated_effort": self._estimate_effort(task_description),
            "dependencies": self._identify_dependencies(task_description)
        }
        
        # Create execution plan
        analysis["execution_plan"] = self._create_execution_plan(analysis)
        
        # Save analysis to temp file for context management
        analysis_file = self.temp_dir / f"{self.task_id}_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
            
        self.session_log.append({
            "action": "task_analysis",
            "timestamp": datetime.now().isoformat(),
            "result": "completed",
            "file": str(analysis_file)
        })
        
        return analysis
    
    def _assess_complexity(self, task_description: str) -> str:
        """Assess task complexity based on description."""
        desc_lower = task_description.lower()
        
        # Complexity indicators
        extensive_indicators = [
            "entire system", "full implementation", "complete rewrite",
            "comprehensive", "end-to-end", "multiple modules",
            "architecture", "framework", "major refactor"
        ]
        
        complex_indicators = [
            "multiple files", "integration", "database", "api",
            "complex logic", "algorithm", "optimization",
            "testing suite", "documentation"
        ]
        
        moderate_indicators = [
            "new feature", "modification", "enhancement",
            "class", "function", "module", "component"
        ]
        
        if any(indicator in desc_lower for indicator in extensive_indicators):
            return TaskComplexity.EXTENSIVE
        elif any(indicator in desc_lower for indicator in complex_indicators):
            return TaskComplexity.COMPLEX
        elif any(indicator in desc_lower for indicator in moderate_indicators):
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE
    
    def _extract_requirements(self, task_description: str) -> List[str]:
        """Extract technical requirements from task description."""
        requirements = []
        
        # File format requirements
        formats = re.findall(r'\b(L5X|ACD|JSON|CSV|XML|YAML|SQL)\b', task_description, re.IGNORECASE)
        requirements.extend([f"Support for {fmt} format" for fmt in formats])
        
        # Programming language requirements  
        languages = re.findall(r'\b(Python|TypeScript|JavaScript|Java|C\+\+|SQL|Cypher)\b', task_description, re.IGNORECASE)
        requirements.extend([f"Implementation in {lang}" for lang in languages])
        
        # Functionality requirements
        functions = re.findall(r'\b(convert|validate|parse|generate|analyze|process|integrate)\b', task_description, re.IGNORECASE)
        requirements.extend([f"Must {func} data/files" for func in functions])
        
        # Quality requirements
        if "test" in task_description.lower():
            requirements.append("Include comprehensive testing")
        if "document" in task_description.lower():
            requirements.append("Include documentation")
        if "error" in task_description.lower() or "exception" in task_description.lower():
            requirements.append("Robust error handling")
            
        return list(set(requirements)) or ["Basic functionality implementation"]
    
    def _identify_resources(self, task_description: str) -> Dict[str, List[str]]:
        """Identify available resources for the task."""
        resources = {
            "knowledge_graph": [],
            "tools": [],
            "documentation": [],
            "code_examples": [],
            "libraries": []
        }
        
        # Check AI resources if available
        if AI_RESOURCES_AVAILABLE:
            try:
                ai_resources_info = ai_resources.get_available_ai_resources()
                
                if ai_resources_info["knowledge_graph"]["available"]:
                    resources["knowledge_graph"] = ["Neo4j knowledge graph with PLC domain expertise"]
                    
                resources["tools"] = list(ai_resources_info["tools"].keys())
                resources["documentation"] = list(ai_resources_info["documentation"].values())
                
                # Get relevant repositories
                task_repos = ai_resources.get_tool_recommendations(task_description)
                resources["code_examples"] = [repo["name"] for repo in task_repos.get("repositories", [])]
                
            except Exception as e:
                logger.warning(f"Could not access AI resources: {e}")
        
        # Identify relevant libraries/tools from task description
        if "neo4j" in task_description.lower():
            resources["libraries"].append("neo4j-driver")
        if "qdrant" in task_description.lower():
            resources["libraries"].append("qdrant-client")
        if "plc" in task_description.lower() or "l5x" in task_description.lower():
            resources["libraries"].extend(["lxml", "xml.etree"])
            
        return resources
    
    def _identify_risks(self, task_description: str) -> List[str]:
        """Identify potential risks and challenges."""
        risks = []
        
        # Complexity risks
        if "multiple" in task_description.lower():
            risks.append("High complexity may lead to integration issues")
            
        # Data risks
        if any(fmt in task_description.lower() for fmt in ["xml", "json", "database"]):
            risks.append("Data parsing/validation errors possible")
            
        # Performance risks
        if any(word in task_description.lower() for word in ["large", "many", "bulk", "batch"]):
            risks.append("Performance optimization may be required")
            
        # Compatibility risks
        if "convert" in task_description.lower() or "format" in task_description.lower():
            risks.append("Format compatibility issues possible")
            
        # Context window risk
        if self._assess_complexity(task_description) in [TaskComplexity.COMPLEX, TaskComplexity.EXTENSIVE]:
            risks.append("May exceed context window - requires decomposition")
            
        return risks or ["Minimal risks identified"]
    
    def _define_validation_criteria(self, task_description: str) -> List[str]:
        """Define criteria for validating task completion."""
        criteria = [
            "Code compiles/runs without syntax errors",
            "Basic functionality works as described",
            "Error handling is implemented",
            "Code follows project conventions"
        ]
        
        # Add specific criteria based on task
        if "test" in task_description.lower():
            criteria.append("All tests pass")
        if "convert" in task_description.lower():
            criteria.append("Conversion produces valid output")
        if "api" in task_description.lower():
            criteria.append("API endpoints respond correctly")
        if "database" in task_description.lower():
            criteria.append("Database operations execute successfully")
            
        return criteria
    
    def _estimate_effort(self, task_description: str) -> Dict[str, Any]:
        """Estimate effort required for task completion."""
        complexity = self._assess_complexity(task_description)
        
        effort_mapping = {
            TaskComplexity.SIMPLE: {"lines": "< 100", "files": "1", "time": "< 1 hour"},
            TaskComplexity.MODERATE: {"lines": "100-500", "files": "2-5", "time": "1-3 hours"},
            TaskComplexity.COMPLEX: {"lines": "500-1500", "files": "5-15", "time": "3-8 hours"},
            TaskComplexity.EXTENSIVE: {"lines": "> 1500", "files": "> 15", "time": "> 8 hours"}
        }
        
        return effort_mapping[complexity]
    
    def _identify_dependencies(self, task_description: str) -> List[str]:
        """Identify task dependencies."""
        dependencies = []
        
        # Service dependencies
        if "neo4j" in task_description.lower():
            dependencies.append("Neo4j service running")
        if "qdrant" in task_description.lower():
            dependencies.append("Qdrant service running")
        if "database" in task_description.lower():
            dependencies.append("Database service accessible")
            
        # File dependencies
        if "config" in task_description.lower():
            dependencies.append("Configuration files present")
        if "input" in task_description.lower() or "file" in task_description.lower():
            dependencies.append("Input files available")
            
        return dependencies or ["No external dependencies identified"]
    
    def _create_execution_plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create step-by-step execution plan."""
        complexity = analysis["complexity"]
        
        base_steps = [
            {
                "step": 1,
                "action": "Environment Setup",
                "description": "Verify dependencies and setup development environment",
                "validation": "All required services and tools are available"
            },
            {
                "step": 2,
                "action": "Code Discovery",
                "description": "Analyze existing codebase and identify relevant files",
                "validation": "Relevant code patterns and structures identified"
            },
            {
                "step": 3,
                "action": "Implementation Planning",
                "description": "Create detailed implementation plan with file structure",
                "validation": "Clear implementation roadmap defined"
            }
        ]
        
        # Add complexity-specific steps
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXTENSIVE]:
            base_steps.extend([
                {
                    "step": 4,
                    "action": "Context Management",
                    "description": "Create detailed task documentation for context preservation",
                    "validation": "Task context properly documented and preserved"
                },
                {
                    "step": 5,
                    "action": "Incremental Implementation",
                    "description": "Implement solution in manageable chunks",
                    "validation": "Each chunk works independently"
                }
            ])
        else:
            base_steps.append({
                "step": 4,
                "action": "Direct Implementation",
                "description": "Implement solution according to requirements",
                "validation": "Implementation meets all requirements"
            })
        
        # Final steps
        base_steps.extend([
            {
                "step": len(base_steps) + 1,
                "action": "Testing & Validation",
                "description": "Test implementation and validate against criteria",
                "validation": "All validation criteria met"
            },
            {
                "step": len(base_steps) + 2,
                "action": "Documentation & Cleanup",
                "description": "Document solution and clean up temporary files",
                "validation": "Solution properly documented"
            }
        ])
        
        return base_steps
    
    def discover_codebase(self, task_description: str) -> Dict[str, Any]:
        """
        Discover and analyze relevant codebase components.
        
        Args:
            task_description: Task description for context
            
        Returns:
            Codebase analysis with relevant files and patterns
        """
        logger.info("Starting codebase discovery")
        
        discovery = {
            "relevant_files": [],
            "code_patterns": [],
            "documentation": [],
            "tools": [],
            "similar_implementations": []
        }
        
        # Extract keywords from task description
        keywords = self._extract_keywords(task_description)
        
        # Search for relevant files
        discovery["relevant_files"] = self._find_relevant_files(keywords)
        
        # Find code patterns
        discovery["code_patterns"] = self._analyze_code_patterns(keywords)
        
        # Find documentation
        discovery["documentation"] = self._find_documentation(keywords)
        
        # Find available tools
        discovery["tools"] = self._find_available_tools(keywords)
        
        # Save discovery results
        discovery_file = self.temp_dir / f"{self.task_id}_discovery.json"
        with open(discovery_file, 'w') as f:
            json.dump(discovery, f, indent=2)
            
        self.session_log.append({
            "action": "codebase_discovery",
            "timestamp": datetime.now().isoformat(),
            "result": "completed",
            "file": str(discovery_file)
        })
        
        return discovery
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Common PLC/automation keywords
        domain_keywords = [
            "plc", "aoi", "routine", "tag", "device", "l5x", "acd",
            "studio", "rockwell", "allen", "bradley", "automation",
            "control", "ethernet", "modbus", "scada", "hmi"
        ]
        
        # Technical keywords
        tech_keywords = [
            "convert", "parse", "validate", "generate", "process",
            "api", "database", "neo4j", "qdrant", "json", "xml"
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in domain_keywords + tech_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
                
        # Extract quoted terms
        quoted_terms = re.findall(r'"([^"]*)"', text)
        found_keywords.extend(quoted_terms)
        
        return list(set(found_keywords))
    
    def _find_relevant_files(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find files relevant to the task."""
        relevant_files = []
        
        # Search patterns
        search_patterns = []
        for keyword in keywords:
            search_patterns.extend([
                f"*{keyword}*",
                f"*{keyword.title()}*",
                f"*{keyword.upper()}*"
            ])
        
        # Search in project
        for pattern in search_patterns:
            try:
                files = list(self.project_root.rglob(pattern))
                for file_path in files[:10]:  # Limit results
                    if file_path.is_file() and file_path.suffix in ['.py', '.md', '.json', '.yaml', '.yml']:
                        relevant_files.append({
                            "path": str(file_path.relative_to(self.project_root)),
                            "type": file_path.suffix,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
            except Exception as e:
                logger.warning(f"Error searching for pattern {pattern}: {e}")
                
        return relevant_files[:20]  # Limit total results
    
    def _analyze_code_patterns(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Analyze code patterns in relevant files."""
        patterns = []
        
        # Look for common patterns in Python files
        python_files = list(self.project_root.rglob("*.py"))[:20]  # Limit search
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Find class definitions
                classes = re.findall(r'class\s+(\w+)', content)
                if classes:
                    patterns.append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "type": "class_definitions",
                        "items": classes[:5]  # Limit results
                    })
                
                # Find function definitions
                functions = re.findall(r'def\s+(\w+)', content)
                if functions:
                    patterns.append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "type": "function_definitions", 
                        "items": functions[:5]  # Limit results
                    })
                    
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
                
        return patterns[:15]  # Limit total patterns
    
    def _find_documentation(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find relevant documentation."""
        docs = []
        
        # Look for documentation files
        doc_patterns = ["*.md", "*.rst", "*.txt"]
        
        for pattern in doc_patterns:
            doc_files = list(self.project_root.rglob(pattern))
            
            for doc_file in doc_files[:10]:
                try:
                    content = doc_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Check if keywords appear in content
                    content_lower = content.lower()
                    matching_keywords = [kw for kw in keywords if kw in content_lower]
                    
                    if matching_keywords:
                        docs.append({
                            "path": str(doc_file.relative_to(self.project_root)),
                            "title": doc_file.stem,
                            "keywords_found": matching_keywords,
                            "size": len(content)
                        })
                        
                except Exception as e:
                    logger.warning(f"Error reading {doc_file}: {e}")
                    
        return docs[:10]
    
    def _find_available_tools(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find available tools and scripts."""
        tools = []
        
        # Look for executable Python files
        script_dirs = ["scripts", "tools", "bin", "utils"]
        
        for script_dir in script_dirs:
            script_path = self.project_root / script_dir
            if script_path.exists():
                python_scripts = list(script_path.rglob("*.py"))
                
                for script in python_scripts:
                    try:
                        content = script.read_text(encoding='utf-8', errors='ignore')
                        
                        # Check for main execution
                        if '__main__' in content:
                            tools.append({
                                "path": str(script.relative_to(self.project_root)),
                                "name": script.stem,
                                "type": "python_script",
                                "executable": True
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error analyzing script {script}: {e}")
                        
        return tools[:10]
    
    def create_context_document(self, task_analysis: Dict[str, Any], discovery: Dict[str, Any]) -> Path:
        """
        Create comprehensive context document for complex tasks.
        
        Args:
            task_analysis: Results from analyze_task()
            discovery: Results from discover_codebase()
            
        Returns:
            Path to context document
        """
        logger.info("Creating context document for task preservation")
        
        context_doc = {
            "task_overview": {
                "id": task_analysis["task_id"],
                "description": task_analysis["description"],
                "complexity": task_analysis["complexity"],
                "estimated_effort": task_analysis["estimated_effort"]
            },
            "requirements": task_analysis["requirements"],
            "execution_plan": task_analysis["execution_plan"],
            "resources": {
                "available_tools": task_analysis["resources_needed"]["tools"],
                "relevant_files": discovery["relevant_files"],
                "documentation": discovery["documentation"],
                "code_patterns": discovery["code_patterns"]
            },
            "validation_criteria": task_analysis["validation_criteria"],
            "risks_and_mitigations": task_analysis["risks"],
            "context_preservation": {
                "created_at": datetime.now().isoformat(),
                "purpose": "Preserve task context for complex implementation",
                "usage": "Reference this document if context window is exceeded"
            }
        }
        
        # Create detailed context document
        context_file = self.temp_dir / f"{self.task_id}_context.md"
        
        with open(context_file, 'w') as f:
            f.write(f"# Task Context Document: {task_analysis['task_id']}\n\n")
            f.write(f"**Created**: {datetime.now().isoformat()}\n")
            f.write(f"**Task**: {task_analysis['description']}\n")
            f.write(f"**Complexity**: {task_analysis['complexity']}\n\n")
            
            f.write("## Requirements\n")
            for req in task_analysis['requirements']:
                f.write(f"- {req}\n")
            f.write("\n")
            
            f.write("## Execution Plan\n")
            for step in task_analysis['execution_plan']:
                f.write(f"### Step {step['step']}: {step['action']}\n")
                f.write(f"{step['description']}\n")
                f.write(f"**Validation**: {step['validation']}\n\n")
                
            f.write("## Available Resources\n")
            f.write("### Tools\n")
            for tool in task_analysis['resources_needed']['tools']:
                f.write(f"- {tool}\n")
            f.write("\n")
            
            f.write("### Relevant Files\n")
            for file_info in discovery['relevant_files'][:10]:
                f.write(f"- `{file_info['path']}` ({file_info['type']})\n")
            f.write("\n")
            
            f.write("### Documentation\n")
            for doc in discovery['documentation'][:5]:
                f.write(f"- `{doc['path']}` - {doc.get('title', 'No title')}\n")
            f.write("\n")
            
            f.write("## Validation Criteria\n")
            for criteria in task_analysis['validation_criteria']:
                f.write(f"- [ ] {criteria}\n")
            f.write("\n")
            
            f.write("## Risks and Mitigations\n")
            for risk in task_analysis['risks']:
                f.write(f"- ⚠️ {risk}\n")
            f.write("\n")
        
        # Also save as JSON for programmatic access
        json_file = self.temp_dir / f"{self.task_id}_context.json"
        with open(json_file, 'w') as f:
            json.dump(context_doc, f, indent=2)
            
        self.session_log.append({
            "action": "context_document_creation",
            "timestamp": datetime.now().isoformat(),
            "result": "completed",
            "files": [str(context_file), str(json_file)]
        })
        
        logger.info(f"Context document created: {context_file}")
        return context_file
    
    def validate_output(self, code_content: str, requirements: List[str]) -> Dict[str, Any]:
        """
        Validate code output against requirements and check for hallucinations.
        
        Args:
            code_content: Generated code content
            requirements: List of requirements to validate against
            
        Returns:
            Validation results with pass/fail status and issues
        """
        logger.info("Starting output validation")
        
        validation = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "pass",
            "checks": {
                "syntax": {"status": "unknown", "details": []},
                "requirements": {"status": "unknown", "details": []},
                "hallucination": {"status": "unknown", "details": []},
                "best_practices": {"status": "unknown", "details": []}
            },
            "issues": [],
            "score": 0
        }
        
        # 1. Syntax validation
        syntax_result = self._validate_syntax(code_content)
        validation["checks"]["syntax"] = syntax_result
        
        # 2. Requirements validation
        req_result = self._validate_requirements(code_content, requirements)
        validation["checks"]["requirements"] = req_result
        
        # 3. Hallucination detection
        halluc_result = self._detect_hallucinations(code_content)
        validation["checks"]["hallucination"] = halluc_result
        
        # 4. Best practices validation
        practices_result = self._validate_best_practices(code_content)
        validation["checks"]["best_practices"] = practices_result
        
        # Calculate overall score and status
        passed_checks = sum(1 for check in validation["checks"].values() if check["status"] == "pass")
        total_checks = len(validation["checks"])
        validation["score"] = (passed_checks / total_checks) * 100
        
        if validation["score"] < 75:
            validation["overall_status"] = "fail"
        elif validation["score"] < 90:
            validation["overall_status"] = "warning"
        else:
            validation["overall_status"] = "pass"
            
        # Collect all issues
        for check_name, check_result in validation["checks"].items():
            if check_result["status"] != "pass":
                validation["issues"].extend([f"{check_name}: {detail}" for detail in check_result["details"]])
        
        # Save validation results
        validation_file = self.temp_dir / f"{self.task_id}_validation.json"
        with open(validation_file, 'w') as f:
            json.dump(validation, f, indent=2)
            
        self.validation_results = validation
        
        logger.info(f"Validation completed: {validation['score']}% score")
        return validation
    
    def _validate_syntax(self, code_content: str) -> Dict[str, Any]:
        """Validate Python syntax."""
        result = {"status": "pass", "details": []}
        
        try:
            # Try to compile the code
            compile(code_content, '<string>', 'exec')
            result["details"].append("Python syntax is valid")
        except SyntaxError as e:
            result["status"] = "fail"
            result["details"].append(f"Syntax error: {e.msg} at line {e.lineno}")
        except Exception as e:
            result["status"] = "warning"
            result["details"].append(f"Compilation warning: {str(e)}")
            
        return result
    
    def _validate_requirements(self, code_content: str, requirements: List[str]) -> Dict[str, Any]:
        """Validate code against requirements."""
        result = {"status": "pass", "details": []}
        
        code_lower = code_content.lower()
        missing_requirements = []
        
        for req in requirements:
            req_lower = req.lower()
            
            # Check for specific requirement patterns
            if "error handling" in req_lower:
                if not any(pattern in code_lower for pattern in ["try:", "except:", "raise", "error", "exception"]):
                    missing_requirements.append("Error handling not implemented")
                    
            elif "test" in req_lower:
                if not any(pattern in code_lower for pattern in ["test_", "assert", "unittest", "pytest"]):
                    missing_requirements.append("Testing not implemented")
                    
            elif "documentation" in req_lower:
                if not any(pattern in code_lower for pattern in ['"""', "'''", "# "]):
                    missing_requirements.append("Documentation not found")
                    
            elif "format" in req_lower:
                formats = re.findall(r'\b(L5X|ACD|JSON|XML|CSV)\b', req, re.IGNORECASE)
                for fmt in formats:
                    if fmt.lower() not in code_lower:
                        missing_requirements.append(f"Support for {fmt} format not found")
        
        if missing_requirements:
            result["status"] = "fail"
            result["details"] = missing_requirements
        else:
            result["details"].append("All requirements appear to be addressed")
            
        return result
    
    def _detect_hallucinations(self, code_content: str) -> Dict[str, Any]:
        """Detect potential hallucinations in code."""
        result = {"status": "pass", "details": []}
        
        # Common hallucination patterns
        suspicious_patterns = [
            # Non-existent modules
            (r'import\s+(?:fake_module|example_module|placeholder)', "Suspicious import of fake/placeholder module"),
            
            # Placeholder URLs/endpoints
            (r'https?://(?:example\.com|placeholder|fake)', "Placeholder URL detected"),
            
            # Fake API keys or credentials
            (r'(?:api_key|token|password)\s*=\s*["\'](?:fake|example|placeholder|your_)', "Placeholder credentials detected"),
            
            # Non-existent files with obvious placeholders
            (r'["\'](?:path/to/|/fake/|example\.)', "Placeholder file path detected"),
            
            # Obvious placeholder functions
            (r'def\s+(?:placeholder_|example_|fake_)', "Placeholder function name detected"),
            
            # TODO/FIXME comments indicating incomplete code
            (r'#\s*(?:TODO|FIXME|XXX|HACK)', "Incomplete code markers found")
        ]
        
        hallucinations = []
        
        for pattern, description in suspicious_patterns:
            matches = re.findall(pattern, code_content, re.IGNORECASE)
            if matches:
                hallucinations.append(f"{description}: {matches[:3]}")  # Show first 3 matches
        
        # Check for unrealistic/fake data
        fake_data_patterns = [
            r'john\.doe@example\.com',
            r'123-45-6789',  # Fake SSN pattern
            r'555-\d{4}',    # Fake phone numbers
        ]
        
        for pattern in fake_data_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                hallucinations.append(f"Fake/example data detected: {pattern}")
        
        if hallucinations:
            result["status"] = "warning"
            result["details"] = hallucinations
        else:
            result["details"].append("No obvious hallucinations detected")
            
        return result
    
    def _validate_best_practices(self, code_content: str) -> Dict[str, Any]:
        """Validate code against best practices."""
        result = {"status": "pass", "details": []}
        
        issues = []
        
        # Check for good practices
        if not re.search(r'""".*?"""', code_content, re.DOTALL):
            issues.append("Missing docstrings")
            
        if len(re.findall(r'\n', code_content)) > 100 and not re.search(r'def\s+\w+', code_content):
            issues.append("Long code without function decomposition")
            
        if 'print(' in code_content and 'logging' not in code_content:
            issues.append("Using print() instead of logging")
            
        # Check for security issues
        if re.search(r'eval\s*\(|exec\s*\(', code_content):
            issues.append("Dangerous use of eval() or exec()")
            
        # Check for proper imports
        if 'import *' in code_content:
            issues.append("Wildcard imports should be avoided")
            
        if issues:
            result["status"] = "warning"
            result["details"] = issues
        else:
            result["details"].append("Code follows good practices")
            
        return result
    
    def execute_task_step(self, step_number: int, execution_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a specific step from the execution plan.
        
        Args:
            step_number: Step number to execute
            execution_plan: Complete execution plan
            
        Returns:
            Step execution results
        """
        if step_number > len(execution_plan):
            raise ValueError(f"Step {step_number} does not exist in plan")
            
        step = execution_plan[step_number - 1]
        logger.info(f"Executing step {step_number}: {step['action']}")
        
        result = {
            "step_number": step_number,
            "action": step["action"],
            "status": "in_progress",
            "timestamp": datetime.now().isoformat(),
            "details": [],
            "validation_status": "pending"
        }
        
        try:
            # Execute step based on action type
            if "setup" in step["action"].lower():
                result.update(self._execute_setup_step())
            elif "discovery" in step["action"].lower():
                result.update(self._execute_discovery_step())
            elif "planning" in step["action"].lower():
                result.update(self._execute_planning_step())
            elif "context" in step["action"].lower():
                result.update(self._execute_context_step())
            elif "implementation" in step["action"].lower():
                result.update(self._execute_implementation_step())
            elif "testing" in step["action"].lower():
                result.update(self._execute_testing_step())
            elif "documentation" in step["action"].lower():
                result.update(self._execute_documentation_step())
            else:
                result["status"] = "completed"
                result["details"].append(f"Step guidance: {step['description']}")
                
        except Exception as e:
            result["status"] = "failed"
            result["details"].append(f"Error: {str(e)}")
            logger.error(f"Step {step_number} failed: {e}")
        
        # Log step completion
        self.session_log.append({
            "action": f"step_{step_number}_execution",
            "timestamp": datetime.now().isoformat(),
            "result": result["status"]
        })
        
        return result
    
    def _execute_setup_step(self) -> Dict[str, Any]:
        """Execute environment setup step."""
        details = []
        
        # Check Python environment
        details.append(f"Python version: {sys.version}")
        
        # Check for required tools
        tools_to_check = ["git", "docker", "pip"]
        for tool in tools_to_check:
            try:
                result = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    details.append(f"✅ {tool} available")
                else:
                    details.append(f"❌ {tool} not available")
            except Exception:
                details.append(f"❌ {tool} not available")
        
        # Check AI resources
        if AI_RESOURCES_AVAILABLE:
            details.append("✅ AI resources available")
        else:
            details.append("⚠️ AI resources not available")
            
        return {
            "status": "completed",
            "details": details
        }
    
    def _execute_discovery_step(self) -> Dict[str, Any]:
        """Execute code discovery step."""
        return {
            "status": "completed",
            "details": ["Code discovery should be performed using discover_codebase() method"]
        }
    
    def _execute_planning_step(self) -> Dict[str, Any]:
        """Execute implementation planning step."""
        return {
            "status": "completed",
            "details": ["Create detailed implementation plan based on analysis and discovery results"]
        }
    
    def _execute_context_step(self) -> Dict[str, Any]:
        """Execute context management step."""
        return {
            "status": "completed",
            "details": ["Context document should be created using create_context_document() method"]
        }
    
    def _execute_implementation_step(self) -> Dict[str, Any]:
        """Execute implementation step."""
        return {
            "status": "completed",
            "details": ["Implement solution according to plan and requirements"]
        }
    
    def _execute_testing_step(self) -> Dict[str, Any]:
        """Execute testing step."""
        return {
            "status": "completed",
            "details": ["Test implementation and validate using validate_output() method"]
        }
    
    def _execute_documentation_step(self) -> Dict[str, Any]:
        """Execute documentation step."""
        return {
            "status": "completed",
            "details": ["Document solution and clean up temporary files"]
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        return {
            "task_id": self.task_id,
            "session_start": self.session_log[0]["timestamp"] if self.session_log else None,
            "session_end": datetime.now().isoformat(),
            "actions_performed": len(self.session_log),
            "validation_score": self.validation_results.get("score", 0),
            "temp_directory": str(self.temp_dir),
            "log": self.session_log
        }
    
    def cleanup(self):
        """Clean up temporary files and close session."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            logger.info(f"Task orchestrator cleanup completed for {self.task_id}")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")


# Convenience functions for AI agents
def analyze_and_plan_task(task_description: str) -> Dict[str, Any]:
    """
    Quick task analysis and planning for AI agents.
    
    Args:
        task_description: Description of the task
        
    Returns:
        Task analysis with guidance
    """
    orchestrator = AITaskOrchestrator()
    
    try:
        analysis = orchestrator.analyze_task(task_description)
        
        # Create guidance text
        guidance = f"""
# Task Analysis: {analysis['task_id']}

## Overview
- **Complexity**: {analysis['complexity']}
- **Estimated Effort**: {analysis['estimated_effort']['time']}

## Requirements
"""
        for req in analysis['requirements']:
            guidance += f"- {req}\n"
        
        guidance += "\n## Available Resources\n"
        if AI_RESOURCES_AVAILABLE:
            guidance += "- ✅ Knowledge graph available\n"
            guidance += f"- Tools: {', '.join(analysis['resources_needed']['tools'][:3])}\n"
        else:
            guidance += "- ⚠️ Limited resources (AI resources not available)\n"
        
        guidance += "\n## Validation Criteria\n"
        for criteria in analysis['validation_criteria']:
            guidance += f"- [ ] {criteria}\n"
        
        if analysis['complexity'] in [TaskComplexity.COMPLEX, TaskComplexity.EXTENSIVE]:
            guidance += "\n⚠️ **Complex Task Warning**: May exceed context window - break into smaller steps\n"
        
        analysis['guidance'] = guidance
        return analysis
        
    finally:
        orchestrator.cleanup()


def validate_task_completion(code_content: str, requirements: List[str]) -> Dict[str, Any]:
    """
    Validate completed task against requirements and check for hallucinations.
    
    Args:
        code_content: Generated code content
        requirements: List of requirements
        
    Returns:
        Validation results
    """
    orchestrator = AITaskOrchestrator()
    
    try:
        return orchestrator.validate_output(code_content, requirements)
    finally:
        orchestrator.cleanup()


def get_task_guidance(task_description: str) -> str:
    """
    Get structured guidance for completing a task.
    
    Args:
        task_description: Description of the task
        
    Returns:
        Formatted guidance text
    """
    analysis = analyze_and_plan_task(task_description)
    return analysis.get('guidance', 'No guidance available')


if __name__ == "__main__":
    # Demo usage
    print("🤖 AI Task Orchestrator - Demo")
    print("=" * 50)
    
    # Example task
    task = "Create a Python script that converts L5X files to JSON format with validation and error handling"
    
    print(f"\nTask: {task}")
    print("\n📋 Getting task guidance...")
    
    guidance = get_task_guidance(task)
    print(guidance)
    
    print("\n✅ Task orchestrator ready for AI agent use!") 