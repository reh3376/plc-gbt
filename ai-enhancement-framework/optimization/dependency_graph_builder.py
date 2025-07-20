#!/usr/bin/env python3
"""
🔗 Dependency Graph Builder - AI Enhancement Framework
Advanced Dependency Analysis with Import Mapping and Circular Detection

This module implements comprehensive dependency graph analysis including:
- Comprehensive import graph mapping across entire codebase
- Advanced circular dependency detection with resolution strategies
- Modular extraction suggestions based on dependency patterns
- Cross-language dependency analysis (Python, TypeScript, JavaScript)
- Integration with CodebaseAnalyzer for enhanced insights
- Dependency strength analysis and coupling metrics
- Architectural pattern detection and recommendations

Following AI Task Orchestrator methodology for systematic dependency analysis.

Author: AI Enhancement Framework
Created: 2025-01-17
Updated: 2025-01-17 (Phase 14.1.2 Integration)
Dependencies: ast, networkx (optional), existing optimization framework
"""

import ast
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json
from collections import defaultdict, deque
import importlib.util
import logging
import hashlib

# Optional graph library for advanced analysis
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

# Import existing framework components
try:
    from .codebase_analyzer import CodebaseAnalyzer, FileAnalysisResult, DirectoryAnalysis
    CODEBASE_ANALYZER_AVAILABLE = True
except ImportError:
    CODEBASE_ANALYZER_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Data Structures for Dependency Analysis
# ============================================================================

@dataclass
class ImportNode:
    """Individual import node in dependency graph"""
    module_name: str
    file_path: str
    import_type: str  # absolute, relative, local, external
    import_statement: str
    line_number: int
    is_conditional: bool = False
    is_dynamic: bool = False
    namespace: Optional[str] = None
    alias: Optional[str] = None

@dataclass
class DependencyEdge:
    """Edge representing dependency between modules"""
    source_file: str
    target_file: str
    import_nodes: List[ImportNode]
    strength: float  # 0-1 indicating coupling strength
    dependency_type: str  # direct, indirect, circular
    coupling_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class CircularDependency:
    """Detailed circular dependency information"""
    cycle_id: str
    cycle_path: List[str]
    cycle_length: int
    total_imports: int
    resolution_complexity: str  # simple, moderate, complex
    suggested_resolution: List[str]
    impact_assessment: Dict[str, Any]
    breaking_points: List[Tuple[str, str]]  # Potential points to break cycle

@dataclass
class ModularExtractionOpportunity:
    """Opportunity for modular extraction based on dependencies"""
    opportunity_id: str
    target_files: List[str]
    common_dependencies: List[str]
    extraction_type: str  # utility_module, interface_extraction, shared_component
    estimated_benefit: float  # 0-1 score
    implementation_steps: List[str]
    risk_factors: List[str]
    affected_modules: List[str]

@dataclass
class ArchitecturalPattern:
    """Detected architectural pattern in dependency graph"""
    pattern_name: str
    pattern_type: str  # layered, mvc, microkernel, etc.
    confidence: float
    components: List[str]
    violations: List[str]
    recommendations: List[str]

@dataclass
class DependencyGraphAnalysis:
    """Complete dependency graph analysis result"""
    analysis_timestamp: datetime
    total_modules: int
    total_dependencies: int
    graph_depth: int
    clustering_coefficient: float
    
    # Core graph data
    import_nodes: List[ImportNode]
    dependency_edges: List[DependencyEdge]
    
    # Analysis results
    circular_dependencies: List[CircularDependency]
    modular_opportunities: List[ModularExtractionOpportunity]
    architectural_patterns: List[ArchitecturalPattern]
    
    # Metrics and insights
    dependency_metrics: Dict[str, float]
    coupling_analysis: Dict[str, Any]
    architectural_insights: Dict[str, Any]
    optimization_recommendations: List[str]
    
    # Graph statistics
    strongly_connected_components: List[List[str]] = field(default_factory=list)
    dependency_layers: List[List[str]] = field(default_factory=list)
    critical_modules: List[str] = field(default_factory=list)

# ============================================================================
# Dependency Graph Builder
# ============================================================================

class DependencyGraphBuilder:
    """
    Advanced dependency graph builder for comprehensive codebase analysis.
    
    Builds detailed import graphs, detects circular dependencies, and suggests
    modular extraction opportunities based on dependency patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dependency graph builder"""
        self.config = config or {}
        self.session_id = f"dep_graph_{int(datetime.now().timestamp())}"
        
        # Analysis configuration
        self.analysis_config = {
            "supported_extensions": [".py", ".ts", ".js", ".tsx", ".jsx"],
            "ignore_patterns": ["__pycache__", "node_modules", ".git", "*.pyc"],
            "max_graph_depth": 10,
            "circular_dependency_threshold": 3,
            "coupling_strength_threshold": 0.7,
            "external_dependencies": ["standard_library", "third_party"]
        }
        
        # Graph storage
        self.import_graph = defaultdict(list)
        self.dependency_graph = defaultdict(set)
        self.reverse_graph = defaultdict(set)
        
        # Analysis cache
        self.file_imports_cache = {}
        self.module_resolution_cache = {}
        
        # Integration with codebase analyzer
        if CODEBASE_ANALYZER_AVAILABLE:
            self.codebase_analyzer = CodebaseAnalyzer()
        else:
            self.codebase_analyzer = None
        
        logger.info(f"DependencyGraphBuilder initialized with session: {self.session_id}")
    
    def analyze_dependencies(self, root_path: str, 
                           file_patterns: List[str] = None) -> DependencyGraphAnalysis:
        """Perform comprehensive dependency analysis"""
        logger.info(f"Starting dependency analysis for: {root_path}")
        
        if file_patterns is None:
            file_patterns = ["*.py"]
        
        start_time = datetime.now()
        
        # Phase 1: Discover all files
        files_to_analyze = self._discover_files(root_path, file_patterns)
        logger.info(f"Discovered {len(files_to_analyze)} files for analysis")
        
        # Phase 2: Extract imports from all files
        import_nodes = self._extract_all_imports(files_to_analyze)
        logger.info(f"Extracted {len(import_nodes)} import statements")
        
        # Phase 3: Build dependency graph
        dependency_edges = self._build_dependency_graph(import_nodes, files_to_analyze)
        logger.info(f"Built dependency graph with {len(dependency_edges)} edges")
        
        # Phase 4: Detect circular dependencies
        circular_dependencies = self._detect_circular_dependencies()
        logger.info(f"Detected {len(circular_dependencies)} circular dependencies")
        
        # Phase 5: Identify modular extraction opportunities
        modular_opportunities = self._identify_modular_opportunities()
        logger.info(f"Identified {len(modular_opportunities)} modular extraction opportunities")
        
        # Phase 6: Detect architectural patterns
        architectural_patterns = self._detect_architectural_patterns()
        logger.info(f"Detected {len(architectural_patterns)} architectural patterns")
        
        # Phase 7: Calculate metrics and insights
        dependency_metrics = self._calculate_dependency_metrics()
        coupling_analysis = self._analyze_coupling_patterns()
        architectural_insights = self._generate_architectural_insights()
        
        # Phase 8: Generate recommendations
        optimization_recommendations = self._generate_optimization_recommendations(
            circular_dependencies, modular_opportunities, dependency_metrics
        )
        
        # Build comprehensive analysis result
        analysis = DependencyGraphAnalysis(
            analysis_timestamp=start_time,
            total_modules=len(files_to_analyze),
            total_dependencies=len(dependency_edges),
            graph_depth=self._calculate_graph_depth(),
            clustering_coefficient=self._calculate_clustering_coefficient(),
            import_nodes=import_nodes,
            dependency_edges=dependency_edges,
            circular_dependencies=circular_dependencies,
            modular_opportunities=modular_opportunities,
            architectural_patterns=architectural_patterns,
            dependency_metrics=dependency_metrics,
            coupling_analysis=coupling_analysis,
            architectural_insights=architectural_insights,
            optimization_recommendations=optimization_recommendations
        )
        
        # Advanced graph analysis if NetworkX available
        if NETWORKX_AVAILABLE:
            self._enhance_with_networkx_analysis(analysis)
        
        execution_time = datetime.now() - start_time
        logger.info(f"Dependency analysis completed in {execution_time.total_seconds():.2f} seconds")
        
        return analysis
    
    def _discover_files(self, root_path: str, patterns: List[str]) -> List[str]:
        """Discover all files matching patterns"""
        files = []
        root = Path(root_path)
        
        for pattern in patterns:
            files.extend(str(f) for f in root.rglob(pattern) 
                        if not any(ignore in str(f) for ignore in self.analysis_config["ignore_patterns"]))
        
        return sorted(set(files))
    
    def _extract_all_imports(self, files: List[str]) -> List[ImportNode]:
        """Extract import statements from all files"""
        all_imports = []
        
        for file_path in files:
            try:
                file_imports = self._extract_file_imports(file_path)
                all_imports.extend(file_imports)
                self.file_imports_cache[file_path] = file_imports
            except Exception as e:
                logger.warning(f"Failed to extract imports from {file_path}: {str(e)}")
        
        return all_imports
    
    def _extract_file_imports(self, file_path: str) -> List[ImportNode]:
        """Extract imports from a single file"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle different file types
            if file_path.endswith('.py'):
                imports = self._extract_python_imports(file_path, content)
            elif file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                imports = self._extract_typescript_imports(file_path, content)
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
        
        return imports
    
    def _extract_python_imports(self, file_path: str, content: str) -> List[ImportNode]:
        """Extract Python imports using AST"""
        imports = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_node = ImportNode(
                            module_name=alias.name,
                            file_path=file_path,
                            import_type=self._classify_import_type(alias.name),
                            import_statement=f"import {alias.name}",
                            line_number=node.lineno,
                            alias=alias.asname,
                            is_conditional=self._is_conditional_import(node, tree),
                            is_dynamic=False
                        )
                        imports.append(import_node)
                
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module or ""
                    for alias in node.names:
                        import_node = ImportNode(
                            module_name=module_name,
                            file_path=file_path,
                            import_type=self._classify_import_type(module_name),
                            import_statement=f"from {module_name} import {alias.name}",
                            line_number=node.lineno,
                            alias=alias.asname,
                            is_conditional=self._is_conditional_import(node, tree),
                            is_dynamic=False
                        )
                        imports.append(import_node)
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {str(e)}")
        
        return imports
    
    def _extract_typescript_imports(self, file_path: str, content: str) -> List[ImportNode]:
        """Extract TypeScript/JavaScript imports using regex patterns"""
        imports = []
        lines = content.split('\n')
        
        # Patterns for different import styles
        import_patterns = [
            r'import\s+(.+?)\s+from\s+["\'](.+?)["\']',  # import ... from "..."
            r'import\s+["\'](.+?)["\']',                   # import "..."
            r'const\s+(.+?)\s*=\s*require\(["\'](.+?)["\']\)',  # const ... = require("...")
            r'import\s*\(\s*["\'](.+?)["\']\s*\)'         # import("...") dynamic
        ]
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            for pattern in import_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if len(match.groups()) == 2:
                        imported_items, module_name = match.groups()
                    else:
                        module_name = match.group(1)
                        imported_items = ""
                    
                    import_node = ImportNode(
                        module_name=module_name,
                        file_path=file_path,
                        import_type=self._classify_import_type(module_name),
                        import_statement=line,
                        line_number=line_num,
                        is_conditional=False,  # TODO: Add conditional detection for TS
                        is_dynamic="import(" in line
                    )
                    imports.append(import_node)
        
        return imports
    
    def _classify_import_type(self, module_name: str) -> str:
        """Classify import type (absolute, relative, local, external)"""
        if not module_name:
            return "unknown"
        
        if module_name.startswith('.'):
            return "relative"
        elif module_name in self._get_standard_library_modules():
            return "standard_library"
        elif self._is_third_party_module(module_name):
            return "third_party"
        else:
            return "local"
    
    def _get_standard_library_modules(self) -> Set[str]:
        """Get set of standard library module names"""
        # Simplified - in production would use more comprehensive list
        return {
            "os", "sys", "json", "re", "datetime", "time", "pathlib", "typing",
            "collections", "itertools", "functools", "asyncio", "threading",
            "logging", "unittest", "math", "random", "string", "io"
        }
    
    def _is_third_party_module(self, module_name: str) -> bool:
        """Check if module is third-party"""
        # Simplified check - could be enhanced with package database
        common_third_party = {
            "numpy", "pandas", "matplotlib", "scipy", "sklearn", "tensorflow",
            "torch", "requests", "flask", "django", "fastapi", "pytest",
            "click", "pydantic", "sqlalchemy", "redis", "psycopg2"
        }
        
        root_module = module_name.split('.')[0]
        return root_module in common_third_party
    
    def _is_conditional_import(self, import_node: ast.AST, tree: ast.AST) -> bool:
        """Check if import is inside conditional block"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.Try, ast.ExceptHandler)):
                for child in ast.walk(node):
                    if child is import_node:
                        return True
        return False
    
    def _build_dependency_graph(self, import_nodes: List[ImportNode], 
                               all_files: List[str]) -> List[DependencyEdge]:
        """Build dependency graph from import nodes"""
        edges = []
        file_set = set(all_files)
        
        # Group imports by source file
        imports_by_file = defaultdict(list)
        for import_node in import_nodes:
            imports_by_file[import_node.file_path].append(import_node)
        
        # Build edges
        for source_file, imports in imports_by_file.items():
            for import_node in imports:
                target_file = self._resolve_import_to_file(import_node, all_files)
                
                if target_file and target_file in file_set and target_file != source_file:
                    # Find or create edge
                    edge = self._find_or_create_edge(edges, source_file, target_file)
                    edge.import_nodes.append(import_node)
                    
                    # Update dependency graph structures
                    self.dependency_graph[source_file].add(target_file)
                    self.reverse_graph[target_file].add(source_file)
        
        # Calculate edge strengths and coupling metrics
        for edge in edges:
            edge.strength = self._calculate_edge_strength(edge)
            edge.coupling_metrics = self._calculate_coupling_metrics(edge)
            edge.dependency_type = self._classify_dependency_type(edge)
        
        return edges
    
    def _resolve_import_to_file(self, import_node: ImportNode, all_files: List[str]) -> Optional[str]:
        """Resolve import statement to actual file path"""
        module_name = import_node.module_name
        source_file = import_node.file_path
        
        # Check cache first
        cache_key = f"{source_file}:{module_name}"
        if cache_key in self.module_resolution_cache:
            return self.module_resolution_cache[cache_key]
        
        resolved_file = None
        
        if import_node.import_type == "relative":
            resolved_file = self._resolve_relative_import(source_file, module_name, all_files)
        elif import_node.import_type == "local":
            resolved_file = self._resolve_local_import(module_name, all_files)
        
        # Cache result
        self.module_resolution_cache[cache_key] = resolved_file
        return resolved_file
    
    def _resolve_relative_import(self, source_file: str, module_name: str, 
                                all_files: List[str]) -> Optional[str]:
        """Resolve relative import to file path"""
        source_dir = Path(source_file).parent
        
        # Handle different levels of relative imports
        level = 0
        clean_module = module_name
        while clean_module.startswith('.'):
            level += 1
            clean_module = clean_module[1:]
        
        # Go up directories based on level
        target_dir = source_dir
        for _ in range(level - 1):
            target_dir = target_dir.parent
        
        # Build potential file paths
        if clean_module:
            module_path = target_dir / clean_module.replace('.', '/')
        else:
            module_path = target_dir
        
        # Try different file extensions
        for ext in ['.py', '.ts', '.js', '.tsx', '.jsx']:
            candidate = f"{module_path}{ext}"
            if candidate in all_files:
                return candidate
            
            # Try __init__ files
            init_candidate = f"{module_path}/__init__{ext}"
            if init_candidate in all_files:
                return init_candidate
        
        return None
    
    def _resolve_local_import(self, module_name: str, all_files: List[str]) -> Optional[str]:
        """Resolve local import to file path"""
        # Convert module name to file path
        module_path = module_name.replace('.', '/')
        
        # Try different extensions and locations
        for file_path in all_files:
            path_obj = Path(file_path)
            
            # Check if file matches module name
            if path_obj.stem == module_name or module_path in file_path:
                return file_path
        
        return None
    
    def _find_or_create_edge(self, edges: List[DependencyEdge], 
                           source: str, target: str) -> DependencyEdge:
        """Find existing edge or create new one"""
        for edge in edges:
            if edge.source_file == source and edge.target_file == target:
                return edge
        
        # Create new edge
        new_edge = DependencyEdge(
            source_file=source,
            target_file=target,
            import_nodes=[],
            strength=0.0,
            dependency_type="direct"
        )
        edges.append(new_edge)
        return new_edge
    
    def _calculate_edge_strength(self, edge: DependencyEdge) -> float:
        """Calculate coupling strength of dependency edge"""
        # Simple calculation based on number of imports
        base_strength = min(len(edge.import_nodes) / 10.0, 1.0)
        
        # Adjust based on import types
        adjustment = 0.0
        for import_node in edge.import_nodes:
            if import_node.import_type == "relative":
                adjustment += 0.2  # Relative imports indicate stronger coupling
            elif import_node.is_dynamic:
                adjustment -= 0.1  # Dynamic imports are weaker
        
        return min(max(base_strength + adjustment, 0.0), 1.0)
    
    def _calculate_coupling_metrics(self, edge: DependencyEdge) -> Dict[str, float]:
        """Calculate detailed coupling metrics"""
        return {
            "import_count": len(edge.import_nodes),
            "relative_import_ratio": sum(1 for node in edge.import_nodes 
                                       if node.import_type == "relative") / max(len(edge.import_nodes), 1),
            "dynamic_import_ratio": sum(1 for node in edge.import_nodes 
                                      if node.is_dynamic) / max(len(edge.import_nodes), 1),
            "conditional_import_ratio": sum(1 for node in edge.import_nodes 
                                          if node.is_conditional) / max(len(edge.import_nodes), 1)
        }
    
    def _classify_dependency_type(self, edge: DependencyEdge) -> str:
        """Classify the type of dependency"""
        source, target = edge.source_file, edge.target_file
        
        # Check for circular dependency
        if target in self.dependency_graph and source in self.dependency_graph[target]:
            return "circular"
        
        # Check for indirect dependency
        if self._has_indirect_path(source, target):
            return "indirect"
        
        return "direct"
    
    def _has_indirect_path(self, source: str, target: str, visited: Set[str] = None) -> bool:
        """Check if there's an indirect path between source and target"""
        if visited is None:
            visited = set()
        
        if source in visited:
            return False
        
        visited.add(source)
        
        for intermediate in self.dependency_graph.get(source, []):
            if intermediate == target:
                continue  # Skip direct connection
            
            if intermediate in self.dependency_graph:
                if target in self.dependency_graph[intermediate]:
                    return True
                
                if self._has_indirect_path(intermediate, target, visited.copy()):
                    return True
        
        return False
    
    def _detect_circular_dependencies(self) -> List[CircularDependency]:
        """Detect circular dependencies using DFS"""
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> List[List[str]]:
            """DFS to find cycles"""
            cycles = []
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    cycles.extend(dfs(neighbor, path.copy()))
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
            return cycles
        
        # Find all cycles
        all_cycles = []
        for node in self.dependency_graph:
            if node not in visited:
                all_cycles.extend(dfs(node, []))
        
        # Convert to CircularDependency objects
        for i, cycle in enumerate(all_cycles):
            if len(cycle) >= 3:  # Actual cycle (not just back-and-forth)
                circular_dep = CircularDependency(
                    cycle_id=f"cycle_{i:03d}",
                    cycle_path=cycle,
                    cycle_length=len(cycle) - 1,  # Exclude duplicate node
                    total_imports=self._count_cycle_imports(cycle),
                    resolution_complexity=self._assess_resolution_complexity(cycle),
                    suggested_resolution=self._suggest_cycle_resolution(cycle),
                    impact_assessment=self._assess_cycle_impact(cycle),
                    breaking_points=self._identify_breaking_points(cycle)
                )
                circular_deps.append(circular_dep)
        
        return circular_deps
    
    def _count_cycle_imports(self, cycle: List[str]) -> int:
        """Count total imports in cycle"""
        total = 0
        for i in range(len(cycle) - 1):
            source, target = cycle[i], cycle[i + 1]
            total += len(self.dependency_graph.get(source, []))
        return total
    
    def _assess_resolution_complexity(self, cycle: List[str]) -> str:
        """Assess complexity of resolving circular dependency"""
        cycle_length = len(cycle) - 1
        
        if cycle_length <= 2:
            return "simple"
        elif cycle_length <= 4:
            return "moderate"
        else:
            return "complex"
    
    def _suggest_cycle_resolution(self, cycle: List[str]) -> List[str]:
        """Suggest strategies to resolve circular dependency"""
        suggestions = []
        
        if len(cycle) == 3:  # Simple A->B->A cycle
            suggestions.append("Extract common interface or abstract base class")
            suggestions.append("Use dependency injection pattern")
            suggestions.append("Merge modules if they are tightly coupled")
        else:
            suggestions.append("Introduce mediator pattern")
            suggestions.append("Break cycle by extracting shared utilities")
            suggestions.append("Use observer pattern for loose coupling")
            suggestions.append("Consider architectural refactoring")
        
        return suggestions
    
    def _assess_cycle_impact(self, cycle: List[str]) -> Dict[str, Any]:
        """Assess the impact of circular dependency"""
        return {
            "affected_modules": len(cycle) - 1,
            "import_complexity": self._count_cycle_imports(cycle),
            "maintenance_risk": "high" if len(cycle) > 3 else "medium",
            "testing_difficulty": "high" if len(cycle) > 2 else "medium"
        }
    
    def _identify_breaking_points(self, cycle: List[str]) -> List[Tuple[str, str]]:
        """Identify potential points to break the cycle"""
        breaking_points = []
        
        for i in range(len(cycle) - 1):
            source, target = cycle[i], cycle[i + 1]
            
            # Analyze the dependency strength
            edge_strength = 0.0
            for edge in self.dependency_edges:
                if edge.source_file == source and edge.target_file == target:
                    edge_strength = edge.strength
                    break
            
            # Lower strength edges are better breaking points
            if edge_strength < 0.5:
                breaking_points.append((source, target))
        
        return breaking_points
    
    def _identify_modular_opportunities(self) -> List[ModularExtractionOpportunity]:
        """Identify opportunities for modular extraction"""
        opportunities = []
        
        # Find modules with high fan-out (many dependencies)
        high_fanout_modules = []
        for module, deps in self.dependency_graph.items():
            if len(deps) > 5:  # Threshold for high fan-out
                high_fanout_modules.append((module, len(deps)))
        
        # Find modules with high fan-in (many dependents)
        high_fanin_modules = []
        for module, deps in self.reverse_graph.items():
            if len(deps) > 3:  # Threshold for high fan-in
                high_fanin_modules.append((module, len(deps)))
        
        # Generate extraction opportunities
        opportunity_id = 0
        
        # Utility module opportunities (high fan-in)
        for module, fan_in_count in high_fanin_modules:
            opportunity = ModularExtractionOpportunity(
                opportunity_id=f"utility_{opportunity_id:03d}",
                target_files=[module],
                common_dependencies=list(self.reverse_graph[module]),
                extraction_type="utility_module",
                estimated_benefit=min(fan_in_count / 10.0, 1.0),
                implementation_steps=[
                    f"Extract commonly used functions from {Path(module).name}",
                    "Create dedicated utility module",
                    "Update import statements in dependent modules",
                    "Add comprehensive tests for extracted utilities"
                ],
                risk_factors=[
                    "Breaking changes if interface modified",
                    "Potential circular dependencies"
                ],
                affected_modules=list(self.reverse_graph[module])
            )
            opportunities.append(opportunity)
            opportunity_id += 1
        
        # Interface extraction opportunities (high fan-out)
        for module, fan_out_count in high_fanout_modules:
            opportunity = ModularExtractionOpportunity(
                opportunity_id=f"interface_{opportunity_id:03d}",
                target_files=[module],
                common_dependencies=list(self.dependency_graph[module]),
                extraction_type="interface_extraction",
                estimated_benefit=min(fan_out_count / 15.0, 1.0),
                implementation_steps=[
                    f"Analyze dependencies in {Path(module).name}",
                    "Extract common interfaces or abstract classes",
                    "Implement dependency injection",
                    "Reduce direct dependencies"
                ],
                risk_factors=[
                    "Increased complexity",
                    "Performance overhead"
                ],
                affected_modules=list(self.dependency_graph[module])
            )
            opportunities.append(opportunity)
            opportunity_id += 1
        
        return opportunities
    
    def _detect_architectural_patterns(self) -> List[ArchitecturalPattern]:
        """Detect architectural patterns in the dependency graph"""
        patterns = []
        
        # Detect layered architecture
        layers = self._detect_layered_architecture()
        if layers:
            patterns.append(ArchitecturalPattern(
                pattern_name="Layered Architecture",
                pattern_type="layered",
                confidence=0.8,
                components=layers,
                violations=[],
                recommendations=["Ensure dependencies only flow downward between layers"]
            ))
        
        # Detect hub-and-spoke pattern
        hubs = self._detect_hub_pattern()
        if hubs:
            patterns.append(ArchitecturalPattern(
                pattern_name="Hub and Spoke",
                pattern_type="hub_spoke",
                confidence=0.7,
                components=hubs,
                violations=[],
                recommendations=["Consider breaking down central hubs to reduce coupling"]
            ))
        
        return patterns
    
    def _detect_layered_architecture(self) -> List[str]:
        """Detect if codebase follows layered architecture"""
        # Simple heuristic based on directory structure and dependency flow
        layers = []
        
        # Group modules by directory level
        directory_groups = defaultdict(list)
        for module in self.dependency_graph.keys():
            depth = len(Path(module).parts) - 1
            directory_groups[depth].append(module)
        
        # Check if dependencies flow predominantly in one direction
        if len(directory_groups) >= 3:
            sorted_depths = sorted(directory_groups.keys())
            layers = [f"Layer {i}: {len(directory_groups[depth])} modules" 
                     for i, depth in enumerate(sorted_depths)]
        
        return layers
    
    def _detect_hub_pattern(self) -> List[str]:
        """Detect hub-and-spoke pattern"""
        hubs = []
        
        # Find modules with high centrality (high fan-in and fan-out)
        for module in self.dependency_graph.keys():
            fan_out = len(self.dependency_graph.get(module, []))
            fan_in = len(self.reverse_graph.get(module, []))
            
            if fan_out > 5 and fan_in > 3:  # Thresholds for hub detection
                hubs.append(f"{Path(module).name} (out: {fan_out}, in: {fan_in})")
        
        return hubs
    
    def _calculate_dependency_metrics(self) -> Dict[str, float]:
        """Calculate various dependency metrics"""
        total_modules = len(self.dependency_graph)
        total_edges = sum(len(deps) for deps in self.dependency_graph.values())
        
        return {
            "total_modules": total_modules,
            "total_dependencies": total_edges,
            "average_fan_out": total_edges / max(total_modules, 1),
            "max_fan_out": max(len(deps) for deps in self.dependency_graph.values()) if self.dependency_graph else 0,
            "max_fan_in": max(len(deps) for deps in self.reverse_graph.values()) if self.reverse_graph else 0,
            "graph_density": total_edges / max(total_modules * (total_modules - 1), 1),
            "cyclic_complexity": len(self._detect_circular_dependencies())
        }
    
    def _analyze_coupling_patterns(self) -> Dict[str, Any]:
        """Analyze coupling patterns in the codebase"""
        coupling_analysis = {
            "tight_coupling_pairs": [],
            "loose_coupling_pairs": [],
            "average_coupling_strength": 0.0,
            "coupling_distribution": {"tight": 0, "medium": 0, "loose": 0}
        }
        
        if hasattr(self, 'dependency_edges'):
            total_strength = 0.0
            for edge in self.dependency_edges:
                total_strength += edge.strength
                
                if edge.strength > 0.7:
                    coupling_analysis["tight_coupling_pairs"].append(
                        (edge.source_file, edge.target_file, edge.strength)
                    )
                    coupling_analysis["coupling_distribution"]["tight"] += 1
                elif edge.strength > 0.4:
                    coupling_analysis["coupling_distribution"]["medium"] += 1
                else:
                    coupling_analysis["loose_coupling_pairs"].append(
                        (edge.source_file, edge.target_file, edge.strength)
                    )
                    coupling_analysis["coupling_distribution"]["loose"] += 1
            
            if self.dependency_edges:
                coupling_analysis["average_coupling_strength"] = total_strength / len(self.dependency_edges)
        
        return coupling_analysis
    
    def _generate_architectural_insights(self) -> Dict[str, Any]:
        """Generate architectural insights from dependency analysis"""
        insights = {
            "modularity_score": self._calculate_modularity_score(),
            "maintainability_index": self._calculate_maintainability_index(),
            "technical_debt_indicators": self._identify_technical_debt(),
            "refactoring_priorities": self._identify_refactoring_priorities()
        }
        
        return insights
    
    def _calculate_modularity_score(self) -> float:
        """Calculate overall modularity score"""
        if not self.dependency_graph:
            return 0.0
        
        # Simple modularity calculation based on coupling and cohesion
        total_modules = len(self.dependency_graph)
        total_dependencies = sum(len(deps) for deps in self.dependency_graph.values())
        
        # Lower dependency ratio indicates better modularity
        dependency_ratio = total_dependencies / max(total_modules * (total_modules - 1), 1)
        modularity_score = max(0.0, 1.0 - dependency_ratio * 10)
        
        return min(modularity_score, 1.0)
    
    def _calculate_maintainability_index(self) -> float:
        """Calculate maintainability index based on dependencies"""
        # Simplified calculation - could be enhanced with more sophisticated metrics
        circular_penalty = len(self._detect_circular_dependencies()) * 0.1
        complexity_penalty = self._calculate_dependency_metrics()["average_fan_out"] * 0.05
        
        base_score = 1.0
        maintainability_index = max(0.0, base_score - circular_penalty - complexity_penalty)
        
        return min(maintainability_index, 1.0)
    
    def _identify_technical_debt(self) -> List[str]:
        """Identify technical debt indicators"""
        debt_indicators = []
        
        # Circular dependencies
        circular_count = len(self._detect_circular_dependencies())
        if circular_count > 0:
            debt_indicators.append(f"{circular_count} circular dependencies detected")
        
        # High coupling
        metrics = self._calculate_dependency_metrics()
        if metrics["average_fan_out"] > 8:
            debt_indicators.append("High average fan-out indicates tight coupling")
        
        # Complex modules
        complex_modules = [module for module, deps in self.dependency_graph.items() 
                          if len(deps) > 10]
        if complex_modules:
            debt_indicators.append(f"{len(complex_modules)} modules with high complexity")
        
        return debt_indicators
    
    def _identify_refactoring_priorities(self) -> List[str]:
        """Identify refactoring priorities"""
        priorities = []
        
        # Prioritize circular dependency resolution
        circular_deps = self._detect_circular_dependencies()
        if circular_deps:
            priorities.append(f"Resolve {len(circular_deps)} circular dependencies")
        
        # Prioritize high-coupling modules
        high_coupling = [(module, len(deps)) for module, deps in self.dependency_graph.items() 
                        if len(deps) > 8]
        if high_coupling:
            priorities.append(f"Refactor {len(high_coupling)} high-coupling modules")
        
        # Prioritize modular extraction opportunities
        opportunities = self._identify_modular_opportunities()
        high_benefit_ops = [op for op in opportunities if op.estimated_benefit > 0.7]
        if high_benefit_ops:
            priorities.append(f"Implement {len(high_benefit_ops)} high-benefit modular extractions")
        
        return priorities
    
    def _generate_optimization_recommendations(self, circular_deps: List[CircularDependency],
                                             modular_ops: List[ModularExtractionOpportunity],
                                             metrics: Dict[str, float]) -> List[str]:
        """Generate comprehensive optimization recommendations"""
        recommendations = []
        
        # Circular dependency recommendations
        if circular_deps:
            recommendations.append(f"CRITICAL: Resolve {len(circular_deps)} circular dependencies")
            for dep in circular_deps[:3]:  # Top 3 most critical
                recommendations.extend(dep.suggested_resolution)
        
        # Modular extraction recommendations
        high_benefit_ops = [op for op in modular_ops if op.estimated_benefit > 0.6]
        if high_benefit_ops:
            recommendations.append(f"Implement {len(high_benefit_ops)} high-benefit modular extractions")
        
        # General architecture recommendations
        if metrics["average_fan_out"] > 6:
            recommendations.append("Reduce module coupling through dependency injection")
        
        if metrics["graph_density"] > 0.3:
            recommendations.append("Implement layered architecture to reduce complexity")
        
        # Specific actionable recommendations
        recommendations.extend([
            "Establish clear module boundaries and interfaces",
            "Implement unit testing for all modules",
            "Add dependency injection container",
            "Create architectural documentation",
            "Set up dependency monitoring and alerts"
        ])
        
        return recommendations
    
    def _calculate_graph_depth(self) -> int:
        """Calculate maximum depth of dependency graph"""
        max_depth = 0
        
        def dfs_depth(node: str, visited: Set[str], depth: int) -> int:
            if node in visited:
                return depth
            
            visited.add(node)
            current_max = depth
            
            for neighbor in self.dependency_graph.get(node, []):
                neighbor_depth = dfs_depth(neighbor, visited.copy(), depth + 1)
                current_max = max(current_max, neighbor_depth)
            
            return current_max
        
        for node in self.dependency_graph:
            depth = dfs_depth(node, set(), 0)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _calculate_clustering_coefficient(self) -> float:
        """Calculate clustering coefficient of dependency graph"""
        if not NETWORKX_AVAILABLE:
            return 0.0
        
        # Convert to NetworkX graph for advanced analysis
        G = nx.DiGraph()
        for source, targets in self.dependency_graph.items():
            for target in targets:
                G.add_edge(source, target)
        
        return nx.average_clustering(G.to_undirected())
    
    def _enhance_with_networkx_analysis(self, analysis: DependencyGraphAnalysis):
        """Enhance analysis with NetworkX graph algorithms"""
        if not NETWORKX_AVAILABLE:
            return
        
        # Create NetworkX graph
        G = nx.DiGraph()
        for source, targets in self.dependency_graph.items():
            for target in targets:
                G.add_edge(source, target)
        
        # Calculate strongly connected components
        sccs = list(nx.strongly_connected_components(G))
        analysis.strongly_connected_components = [list(scc) for scc in sccs if len(scc) > 1]
        
        # Calculate topological layers (if DAG)
        try:
            if nx.is_directed_acyclic_graph(G):
                layers = []
                remaining_nodes = set(G.nodes())
                
                while remaining_nodes:
                    # Find nodes with no incoming edges from remaining nodes
                    current_layer = []
                    for node in remaining_nodes:
                        has_incoming = any(pred in remaining_nodes for pred in G.predecessors(node))
                        if not has_incoming:
                            current_layer.append(node)
                    
                    if not current_layer:
                        break
                    
                    layers.append(current_layer)
                    remaining_nodes -= set(current_layer)
                
                analysis.dependency_layers = layers
        except:
            pass  # Not a DAG, skip layer analysis
        
        # Identify critical modules (high centrality)
        try:
            centrality = nx.betweenness_centrality(G)
            threshold = sum(centrality.values()) / len(centrality) * 2
            analysis.critical_modules = [node for node, cent in centrality.items() 
                                       if cent > threshold]
        except:
            pass
    
    def export_graph(self, analysis: DependencyGraphAnalysis, 
                    output_path: str, format: str = "json"):
        """Export dependency graph to various formats"""
        if format == "json":
            self._export_to_json(analysis, output_path)
        elif format == "dot" and NETWORKX_AVAILABLE:
            self._export_to_dot(analysis, output_path)
        elif format == "gml" and NETWORKX_AVAILABLE:
            self._export_to_gml(analysis, output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_json(self, analysis: DependencyGraphAnalysis, output_path: str):
        """Export analysis to JSON format"""
        export_data = asdict(analysis)
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def _export_to_dot(self, analysis: DependencyGraphAnalysis, output_path: str):
        """Export dependency graph to DOT format for visualization"""
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX required for DOT export")
        
        G = nx.DiGraph()
        for edge in analysis.dependency_edges:
            G.add_edge(edge.source_file, edge.target_file, 
                      weight=edge.strength, label=f"{len(edge.import_nodes)} imports")
        
        nx.drawing.nx_pydot.write_dot(G, output_path)
    
    def _export_to_gml(self, analysis: DependencyGraphAnalysis, output_path: str):
        """Export dependency graph to GML format"""
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX required for GML export")
        
        G = nx.DiGraph()
        for edge in analysis.dependency_edges:
            G.add_edge(edge.source_file, edge.target_file, 
                      weight=edge.strength, imports=len(edge.import_nodes))
        
        nx.write_gml(G, output_path) 