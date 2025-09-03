#!/usr/bin/env python3
"""
Phase 14.1.2: Dependency Graph Builder
======================================

Advanced dependency graph analysis with import mapping, circular dependency detection,
and modular extraction suggestions. Following AI Task Orchestrator methodology.

Features:
- Comprehensive import graph mapping across entire codebase
- Advanced circular dependency detection with resolution strategies
- Modular extraction suggestions based on dependency patterns
- Cross-language dependency analysis (Python, TypeScript, JavaScript)
- Integration with CodebaseAnalyzer for enhanced insights

Target: ~500 lines
Author: AI Task Orchestrator
Date: 2025-01-18
"""

import ast
import re
import sys
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
from core import BaseOrchestrator, TaskAnalysis


@dataclass
class ImportNode:
    """Individual import node in dependency graph"""
    module_name: str
    file_path: str
    import_type: str  # absolute, relative, local
    import_statement: str
    line_number: int
    is_conditional: bool = False
    is_dynamic: bool = False

@dataclass
class DependencyEdge:
    """Edge representing dependency between modules"""
    source_file: str
    target_file: str
    import_nodes: List[ImportNode]
    strength: float  # 0-1 indicating coupling strength
    dependency_type: str  # direct, indirect, circular

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

@dataclass
class ModularExtractionOpportunity:
    """Opportunity for modular extraction based on dependencies"""
    opportunity_id: str
    target_files: List[str]
    common_dependencies: List[str]
    extraction_type: str  # utility_module, interface_extraction, shared_component
    estimated_benefit: str
    implementation_steps: List[str]
    risk_factors: List[str]

@dataclass
class DependencyGraphAnalysis:
    """Complete dependency graph analysis result"""
    total_modules: int
    total_dependencies: int
    graph_depth: int
    clustering_coefficient: float
    import_nodes: List[ImportNode]
    dependency_edges: List[DependencyEdge]
    circular_dependencies: List[CircularDependency]
    modular_opportunities: List[ModularExtractionOpportunity]
    architectural_insights: Dict[str, Any]
    optimization_recommendations: List[str]

class DependencyGraphBuilder(BaseOrchestrator):
    """
    Advanced dependency graph builder for comprehensive codebase analysis.

    Builds detailed import graphs, detects circular dependencies, and suggests
    modular extraction opportunities based on dependency patterns.
    """

    def __init__(self, task_id: str = "dependency_graph_analysis", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)

        # Analysis configuration
        self.graph_config = {
            "supported_languages": ["python", "typescript", "javascript"],
            "max_dependency_depth": 50,
            "circular_dependency_threshold": 3,
            "clustering_threshold": 0.3,
            "extraction_opportunity_threshold": 5,
            "ignore_patterns": [
                "__pycache__", ".git", "node_modules", ".venv", "*.pyc",
                "test_", "_test", ".test.", "spec.", ".spec."
            ]
        }

        # Graph storage
        self.import_graph = defaultdict(list)
        self.reverse_graph = defaultdict(list)
        self.module_registry = {}  # file_path -> module_info

        # Analysis results
        self.import_nodes = []
        self.dependency_edges = []
        self.circular_dependencies = []
        self.modular_opportunities = []

        # Performance tracking
        self.analysis_metrics = {
            "files_processed": 0,
            "imports_analyzed": 0,
            "circular_deps_found": 0,
            "extraction_opportunities": 0
        }

    def _analyze_task(self) -> TaskAnalysis:
        """Implement task analysis following AI Task Orchestrator methodology"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="complex",
            estimated_time="2-3 hours",
            estimated_lines=500,
            requirements=[
                "AST parsing for import analysis",
                "Graph algorithms for cycle detection",
                "Dependency strength calculation",
                "Modular extraction pattern recognition",
                "Cross-language import analysis"
            ],
            risks=[
                "Complex circular dependency resolution",
                "Large graph traversal performance",
                "Cross-language import parsing complexity"
            ],
            dependencies=["ast", "collections", "core.BaseOrchestrator"],
            success_criteria=[
                "Complete dependency graph construction",
                "Accurate circular dependency detection",
                "Actionable modular extraction suggestions",
                "Performance under 60 seconds for 500+ files"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute comprehensive dependency graph analysis"""
        self.log_execution_step("Dependency Graph Analysis", "started")

        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}

            # Get target directory
            project_root = self.config.get("system.project_root", str(Path.cwd()))

            # Build comprehensive dependency graph
            graph_analysis = self.build_import_graph(project_root)

            # Save results
            results = {
                "graph_analysis": asdict(graph_analysis),
                "metrics": self.analysis_metrics,
                "session_info": {
                    "session_id": self.session_id,
                    "analysis_date": datetime.now().isoformat(),
                    "total_execution_time": self.results.get("execution_duration", 0)
                }
            }

            # Add performance metrics
            self.add_performance_metric("files_processed", self.analysis_metrics["files_processed"])
            self.add_performance_metric("circular_deps_found", self.analysis_metrics["circular_deps_found"])

            self.log_execution_step("Dependency Graph Analysis", "completed", {
                "total_modules": graph_analysis.total_modules,
                "circular_dependencies": len(graph_analysis.circular_dependencies),
                "modular_opportunities": len(graph_analysis.modular_opportunities)
            })

            return results

        except Exception as e:
            self.log_error("Dependency graph analysis failed", e)
            return {"status": "failed", "error": str(e)}

    def build_import_graph(self, codebase_path: str) -> DependencyGraphAnalysis:
        """
        Build comprehensive import graph for entire codebase.

        Args:
            codebase_path: Root path of codebase to analyze

        Returns:
            Complete dependency graph analysis
        """
        codebase_path = Path(codebase_path)

        self.log_execution_step("Import Graph Construction", "started", {"path": str(codebase_path)})

        # Step 1: Discover all analyzable files
        analyzable_files = self._discover_files(codebase_path)

        # Step 2: Extract imports from each file
        for file_path in analyzable_files:
            self._extract_file_imports(file_path)

        # Step 3: Build dependency edges
        self._build_dependency_edges()

        # Step 4: Detect circular dependencies
        self.circular_dependencies = self.identify_circular_dependencies()

        # Step 5: Find modular extraction opportunities
        self.modular_opportunities = self.suggest_modular_extraction()

        # Step 6: Calculate graph metrics
        architectural_insights = self._calculate_architectural_insights()

        # Step 7: Generate optimization recommendations
        optimization_recommendations = self._generate_optimization_recommendations()

        self.log_execution_step("Import Graph Construction", "completed")

        return DependencyGraphAnalysis(
            total_modules=len(self.module_registry),
            total_dependencies=len(self.dependency_edges),
            graph_depth=self._calculate_graph_depth(),
            clustering_coefficient=architectural_insights.get("clustering_coefficient", 0.0),
            import_nodes=self.import_nodes,
            dependency_edges=self.dependency_edges,
            circular_dependencies=self.circular_dependencies,
            modular_opportunities=self.modular_opportunities,
            architectural_insights=architectural_insights,
            optimization_recommendations=optimization_recommendations
        )

    def _discover_files(self, codebase_path: Path) -> List[Path]:
        """Discover all analyzable files in codebase"""
        analyzable_files = []

        # Python files
        python_files = list(codebase_path.rglob("*.py"))
        analyzable_files.extend(python_files)

        # TypeScript/JavaScript files (basic support)
        ts_files = list(codebase_path.rglob("*.ts"))
        js_files = list(codebase_path.rglob("*.js"))
        analyzable_files.extend(ts_files)
        analyzable_files.extend(js_files)

        # Filter out ignored patterns
        filtered_files = []
        for file_path in analyzable_files:
            if not self._should_ignore_file(file_path):
                filtered_files.append(file_path)

        return filtered_files

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        path_str = str(file_path)

        for pattern in self.graph_config["ignore_patterns"]:
            if pattern in path_str:
                return True

        return False

    def _extract_file_imports(self, file_path: Path) -> None:
        """Extract import information from a single file"""
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Register module
            self.module_registry[str(file_path)] = {
                "name": file_path.stem,
                "path": str(file_path),
                "language": self._detect_language(file_path),
                "size": len(content),
                "imports": []
            }

            # Extract imports based on language
            if file_path.suffix == '.py':
                self._extract_python_imports(file_path, content)
            elif file_path.suffix in ['.ts', '.js']:
                self._extract_typescript_imports(file_path, content)

            self.analysis_metrics["files_processed"] += 1

        except Exception as e:
            self.logger.warning(f"Failed to extract imports from {file_path}: {e}")

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        if file_path.suffix == '.py':
            return 'python'
        elif file_path.suffix == '.ts':
            return 'typescript'
        elif file_path.suffix == '.js':
            return 'javascript'
        else:
            return 'unknown'

    def _extract_python_imports(self, file_path: Path, content: str) -> None:
        """Extract Python imports using AST"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_nodes = self._process_python_import_node(node, file_path)
                    self.import_nodes.extend(import_nodes)
                    self.module_registry[str(file_path)]["imports"].extend(import_nodes)

        except SyntaxError as e:
            self.logger.warning(f"Syntax error in {file_path}: {e}")

    def _process_python_import_node(self, node: ast.AST, file_path: Path) -> List[ImportNode]:
        """Process individual Python import AST node"""
        import_nodes = []

        if isinstance(node, ast.Import):
            for alias in node.names:
                import_nodes.append(ImportNode(
                    module_name=alias.name,
                    file_path=str(file_path),
                    import_type="absolute",
                    import_statement=f"import {alias.name}",
                    line_number=node.lineno,
                    is_conditional=self._is_conditional_import(node),
                    is_dynamic=False
                ))

        elif isinstance(node, ast.ImportFrom):
            module_name = node.module if node.module else ""
            level = node.level

            import_type = "relative" if level > 0 else "absolute"

            for alias in node.names:
                import_statement = f"from {module_name} import {alias.name}"
                if level > 0:
                    import_statement = f"from {'.' * level}{module_name} import {alias.name}"

                import_nodes.append(ImportNode(
                    module_name=f"{module_name}.{alias.name}" if module_name else alias.name,
                    file_path=str(file_path),
                    import_type=import_type,
                    import_statement=import_statement,
                    line_number=node.lineno,
                    is_conditional=self._is_conditional_import(node),
                    is_dynamic=False
                ))

        self.analysis_metrics["imports_analyzed"] += len(import_nodes)
        return import_nodes

    def _is_conditional_import(self, node: ast.AST) -> bool:
        """Check if import is inside conditional block"""
        # Simple heuristic: check if import is not at module level
        return hasattr(node, 'col_offset') and node.col_offset > 0

    def _extract_typescript_imports(self, file_path: Path, content: str) -> None:
        """Extract TypeScript/JavaScript imports using regex patterns"""
        # Basic regex patterns for import statements
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',  # import ... from '...'
            r'import\s+[\'"]([^\'"]+)[\'"]',               # import '...'
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',   # require('...')
        ]

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern in import_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    module_name = match.group(1)

                    import_node = ImportNode(
                        module_name=module_name,
                        file_path=str(file_path),
                        import_type="absolute" if not module_name.startswith('.') else "relative",
                        import_statement=line.strip(),
                        line_number=line_num,
                        is_conditional=False,
                        is_dynamic="require" in line
                    )

                    self.import_nodes.append(import_node)
                    self.module_registry[str(file_path)]["imports"].append(import_node)
                    self.analysis_metrics["imports_analyzed"] += 1

    def _build_dependency_edges(self) -> None:
        """Build dependency edges from import nodes"""
        # Group imports by source-target pairs
        edge_map = defaultdict(list)

        for import_node in self.import_nodes:
            target_file = self._resolve_import_target(import_node)
            if target_file:
                key = (import_node.file_path, target_file)
                edge_map[key].append(import_node)

        # Create dependency edges
        for (source_file, target_file), imports in edge_map.items():
            strength = self._calculate_dependency_strength(imports)
            dependency_type = self._classify_dependency_type(source_file, target_file)

            edge = DependencyEdge(
                source_file=source_file,
                target_file=target_file,
                import_nodes=imports,
                strength=strength,
                dependency_type=dependency_type
            )

            self.dependency_edges.append(edge)

            # Build adjacency lists
            self.import_graph[source_file].append(target_file)
            self.reverse_graph[target_file].append(source_file)

    def _resolve_import_target(self, import_node: ImportNode) -> Optional[str]:
        """Resolve import module name to actual file path"""
        # Simple resolution for local modules
        source_path = Path(import_node.file_path)

        # For relative imports
        if import_node.import_type == "relative":
            # Basic relative resolution
            module_parts = import_node.module_name.split('.')
            target_path = source_path.parent

            for part in module_parts:
                if part:  # Skip empty parts from leading dots
                    target_path = target_path / part

            # Try with .py extension
            py_file = target_path.with_suffix('.py')
            if py_file.exists() and str(py_file) in self.module_registry:
                return str(py_file)

        # For absolute imports, check if module exists in registry
        for file_path, module_info in self.module_registry.items():
            if module_info["name"] in import_node.module_name:
                return file_path

        return None

    def _calculate_dependency_strength(self, imports: List[ImportNode]) -> float:
        """Calculate dependency strength based on import characteristics"""
        if not imports:
            return 0.0

        base_strength = len(imports) * 0.2  # Base on number of imports

        # Adjust for import types
        for import_node in imports:
            if import_node.is_conditional:
                base_strength *= 0.8  # Conditional imports are weaker
            if import_node.is_dynamic:
                base_strength *= 0.9  # Dynamic imports are slightly weaker

        return min(base_strength, 1.0)

    def _classify_dependency_type(self, source_file: str, target_file: str) -> str:
        """Classify dependency type"""
        # Check if it's part of a circular dependency
        if self._has_path(target_file, source_file):
            return "circular"
        elif self._has_path(source_file, target_file, max_depth=2):
            return "direct"
        else:
            return "indirect"

    def _has_path(self, source: str, target: str, max_depth: int = 10) -> bool:
        """Check if there's a path from source to target"""
        if source == target:
            return True

        visited = set()
        queue = deque([(source, 0)])

        while queue:
            current, depth = queue.popleft()

            if depth >= max_depth:
                continue

            if current in visited:
                continue

            visited.add(current)

            for neighbor in self.import_graph.get(current, []):
                if neighbor == target:
                    return True
                queue.append((neighbor, depth + 1))

        return False

    def identify_circular_dependencies(self) -> List[CircularDependency]:
        """
        Detect circular dependencies using advanced algorithms.

        Returns:
            List of detailed circular dependency information
        """
        self.log_execution_step("Circular Dependency Detection", "started")

        circular_deps = []
        visited = set()
        rec_stack = set()

        def dfs_cycle_detection(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle_path = path[cycle_start:]

                circular_dep = self._create_circular_dependency_info(cycle_path)
                circular_deps.append(circular_dep)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.import_graph.get(node, []):
                dfs_cycle_detection(neighbor, path + [neighbor])

            rec_stack.remove(node)

        # Run DFS from each unvisited node
        for node in self.module_registry:
            if node not in visited:
                dfs_cycle_detection(node, [node])

        self.analysis_metrics["circular_deps_found"] = len(circular_deps)

        self.log_execution_step("Circular Dependency Detection", "completed", {
            "cycles_found": len(circular_deps)
        })

        return circular_deps

    def _create_circular_dependency_info(self, cycle_path: List[str]) -> CircularDependency:
        """Create detailed circular dependency information"""
        cycle_id = f"cycle_{len(self.circular_dependencies) + 1}"

        # Calculate total imports in cycle
        total_imports = 0
        for i in range(len(cycle_path)):
            source = cycle_path[i]
            target = cycle_path[(i + 1) % len(cycle_path)]

            # Count imports between source and target
            for edge in self.dependency_edges:
                if edge.source_file == source and edge.target_file == target:
                    total_imports += len(edge.import_nodes)

        # Assess resolution complexity
        resolution_complexity = "simple"
        if len(cycle_path) > 3:
            resolution_complexity = "moderate"
        if len(cycle_path) > 5 or total_imports > 10:
            resolution_complexity = "complex"

        # Generate resolution suggestions
        suggested_resolution = self._generate_cycle_resolution_suggestions(cycle_path)

        # Impact assessment
        impact_assessment = {
            "maintainability": "high" if resolution_complexity == "complex" else "medium",
            "testability": "medium",
            "deployment_risk": "medium"
        }

        return CircularDependency(
            cycle_id=cycle_id,
            cycle_path=cycle_path,
            cycle_length=len(cycle_path),
            total_imports=total_imports,
            resolution_complexity=resolution_complexity,
            suggested_resolution=suggested_resolution,
            impact_assessment=impact_assessment
        )

    def _generate_cycle_resolution_suggestions(self, cycle_path: List[str]) -> List[str]:
        """Generate suggestions for resolving circular dependencies"""
        suggestions = []

        if len(cycle_path) <= 3:
            suggestions.extend([
                "Extract common interfaces or base classes",
                "Move shared utilities to separate module",
                "Use dependency injection pattern"
            ])
        else:
            suggestions.extend([
                "Identify core module and make others depend on it",
                "Extract shared components to utility modules",
                "Consider architectural restructuring",
                "Implement mediator or observer patterns"
            ])

        return suggestions

    def suggest_modular_extraction(self) -> List[ModularExtractionOpportunity]:
        """
        Suggest modular extraction opportunities based on dependency patterns.

        Returns:
            List of modular extraction opportunities
        """
        self.log_execution_step("Modular Extraction Analysis", "started")

        opportunities = []

        # Find files with common dependency patterns
        dependency_clusters = self._find_dependency_clusters()

        for cluster_id, cluster_files in dependency_clusters.items():
            if len(cluster_files) >= 3:  # Minimum cluster size
                opportunity = self._create_extraction_opportunity(cluster_id, cluster_files)
                opportunities.append(opportunity)

        self.analysis_metrics["extraction_opportunities"] = len(opportunities)

        self.log_execution_step("Modular Extraction Analysis", "completed", {
            "opportunities_found": len(opportunities)
        })

        return opportunities

    def _find_dependency_clusters(self) -> Dict[str, List[str]]:
        """Find clusters of files with similar dependency patterns"""
        clusters = defaultdict(list)

        # Group files by their dependencies
        dependency_signatures = {}

        for file_path in self.module_registry:
            dependencies = set(self.import_graph.get(file_path, []))
            signature = frozenset(dependencies)
            dependency_signatures[file_path] = signature

        # Find files with similar dependency signatures
        signature_groups = defaultdict(list)
        for file_path, signature in dependency_signatures.items():
            signature_groups[signature].append(file_path)

        # Create clusters from groups with multiple files
        cluster_id = 0
        for signature, files in signature_groups.items():
            if len(files) >= 2:
                clusters[f"cluster_{cluster_id}"] = files
                cluster_id += 1

        return clusters

    def _create_extraction_opportunity(self, cluster_id: str, cluster_files: List[str]) -> ModularExtractionOpportunity:
        """Create modular extraction opportunity from cluster"""
        # Find common dependencies
        common_deps = set()
        if cluster_files:
            common_deps = set(self.import_graph.get(cluster_files[0], []))
            for file_path in cluster_files[1:]:
                file_deps = set(self.import_graph.get(file_path, []))
                common_deps &= file_deps

        # Determine extraction type
        extraction_type = "utility_module"
        if len(common_deps) > 5:
            extraction_type = "shared_component"
        elif any("interface" in dep.lower() or "base" in dep.lower() for dep in common_deps):
            extraction_type = "interface_extraction"

        return ModularExtractionOpportunity(
            opportunity_id=f"extract_{cluster_id}",
            target_files=cluster_files,
            common_dependencies=list(common_deps),
            extraction_type=extraction_type,
            estimated_benefit="Medium",
            implementation_steps=[
                "Identify shared functionality patterns",
                "Create new utility module",
                "Extract common code",
                "Update import statements",
                "Validate functionality"
            ],
            risk_factors=[
                "Potential breaking changes",
                "Import statement updates required",
                "Testing complexity"
            ]
        )

    def _calculate_graph_depth(self) -> int:
        """Calculate maximum depth of dependency graph"""
        max_depth = 0

        for root in self.module_registry:
            if not self.reverse_graph.get(root):  # Root node (no incoming dependencies)
                depth = self._calculate_depth_from_node(root)
                max_depth = max(max_depth, depth)

        return max_depth

    def _calculate_depth_from_node(self, node: str, visited: Optional[Set[str]] = None) -> int:
        """Calculate depth from a specific node"""
        if visited is None:
            visited = set()

        if node in visited:
            return 0  # Avoid infinite recursion in cycles

        visited.add(node)

        children = self.import_graph.get(node, [])
        if not children:
            return 1

        max_child_depth = 0
        for child in children:
            child_depth = self._calculate_depth_from_node(child, visited.copy())
            max_child_depth = max(max_child_depth, child_depth)

        return 1 + max_child_depth

    def _calculate_architectural_insights(self) -> Dict[str, Any]:
        """Calculate architectural insights from dependency graph"""
        insights = {}

        # Clustering coefficient
        total_nodes = len(self.module_registry)
        if total_nodes > 2:
            insights["clustering_coefficient"] = self._calculate_clustering_coefficient()
        else:
            insights["clustering_coefficient"] = 0.0

        # Module coupling metrics
        insights["average_dependencies"] = len(self.dependency_edges) / max(total_nodes, 1)
        insights["highly_coupled_modules"] = self._identify_highly_coupled_modules()
        insights["dependency_distribution"] = self._analyze_dependency_distribution()

        return insights

    def _calculate_clustering_coefficient(self) -> float:
        """Calculate clustering coefficient of the dependency graph"""
        total_coefficient = 0.0
        node_count = 0

        for node in self.module_registry:
            neighbors = set(self.import_graph.get(node, []))
            if len(neighbors) < 2:
                continue

            # Count edges between neighbors
            neighbor_edges = 0
            for neighbor1 in neighbors:
                for neighbor2 in neighbors:
                    if neighbor1 != neighbor2 and neighbor2 in self.import_graph.get(neighbor1, []):
                        neighbor_edges += 1

            # Calculate clustering coefficient for this node
            possible_edges = len(neighbors) * (len(neighbors) - 1)
            if possible_edges > 0:
                node_coefficient = neighbor_edges / possible_edges
                total_coefficient += node_coefficient
                node_count += 1

        return total_coefficient / max(node_count, 1)

    def _identify_highly_coupled_modules(self) -> List[str]:
        """Identify modules with high coupling"""
        coupling_scores = {}

        for file_path in self.module_registry:
            outgoing = len(self.import_graph.get(file_path, []))
            incoming = len(self.reverse_graph.get(file_path, []))
            coupling_scores[file_path] = outgoing + incoming

        # Find modules with coupling above threshold
        avg_coupling = sum(coupling_scores.values()) / len(coupling_scores)
        threshold = avg_coupling * 1.5

        highly_coupled = [
            file_path for file_path, score in coupling_scores.items()
            if score > threshold
        ]

        return highly_coupled

    def _analyze_dependency_distribution(self) -> Dict[str, int]:
        """Analyze distribution of dependencies"""
        distribution = {
            "no_dependencies": 0,
            "low_dependencies": 0,  # 1-3
            "medium_dependencies": 0,  # 4-7
            "high_dependencies": 0  # 8+
        }

        for file_path in self.module_registry:
            dep_count = len(self.import_graph.get(file_path, []))

            if dep_count == 0:
                distribution["no_dependencies"] += 1
            elif dep_count <= 3:
                distribution["low_dependencies"] += 1
            elif dep_count <= 7:
                distribution["medium_dependencies"] += 1
            else:
                distribution["high_dependencies"] += 1

        return distribution

    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []

        # Circular dependency recommendations
        if self.circular_dependencies:
            recommendations.append(f"Resolve {len(self.circular_dependencies)} circular dependencies")

        # High coupling recommendations
        architectural_insights = self._calculate_architectural_insights()
        highly_coupled = architectural_insights.get("highly_coupled_modules", [])
        if highly_coupled:
            recommendations.append(f"Reduce coupling in {len(highly_coupled)} modules")

        # Modular extraction recommendations
        if self.modular_opportunities:
            recommendations.append(f"Consider {len(self.modular_opportunities)} modular extraction opportunities")

        # Graph structure recommendations
        if architectural_insights.get("clustering_coefficient", 0) < 0.3:
            recommendations.append("Improve module organization to increase cohesion")

        return recommendations
