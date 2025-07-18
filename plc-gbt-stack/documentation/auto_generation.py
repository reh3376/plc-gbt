#!/usr/bin/env python3
"""
📚 Phase 18.3: Intelligent Documentation System
==============================================

Comprehensive intelligent documentation and context management with:
- Context window management with token estimation and summarization
- Intelligent prompt optimization for large context scenarios
- Auto-generated Mermaid diagrams from orchestrator.describe()
- Comprehensive system visualization and documentation automation

Following AI Task Orchestrator Guide methodology for systematic documentation enhancement.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 18.3 - Intelligent Context & Documentation
Dependencies: AI Task Orchestrator, existing documentation systems
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import hashlib
import textwrap
from collections import defaultdict
import statistics

# Token counting and text processing
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("⚠️ tiktoken not available - using approximate token counting")

# AI and LLM integration
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("⚠️ OpenAI library not available")

# Import AI Task Orchestrator components
try:
    from ..ai.ai_task_orchestrator import AITaskOrchestrator, TaskComplexity, ControlSystemComplexity
    AI_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    AI_ORCHESTRATOR_AVAILABLE = False
    logging.warning("⚠️ AI Task Orchestrator not available")

# Mermaid and visualization libraries
try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    logging.warning("⚠️ Graphviz not available for advanced visualizations")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentationType(Enum):
    """Types of documentation to generate"""
    API_DOCUMENTATION = "api_docs"
    SYSTEM_ARCHITECTURE = "architecture"
    USER_GUIDE = "user_guide"
    TECHNICAL_REFERENCE = "technical_ref"
    TROUBLESHOOTING_GUIDE = "troubleshooting"
    INSTALLATION_GUIDE = "installation"
    MERMAID_DIAGRAM = "mermaid_diagram"
    FLOW_CHART = "flow_chart"
    SEQUENCE_DIAGRAM = "sequence_diagram"
    CLASS_DIAGRAM = "class_diagram"

class ContextOptimizationStrategy(Enum):
    """Strategies for context window optimization"""
    SUMMARIZATION = "summarization"
    CHUNKING = "chunking"
    PRIORITIZATION = "prioritization"
    HIERARCHICAL = "hierarchical"
    COMPRESSION = "compression"
    SELECTIVE_RETENTION = "selective_retention"

class MermaidDiagramType(Enum):
    """Types of Mermaid diagrams"""
    FLOWCHART = "flowchart"
    SEQUENCE_DIAGRAM = "sequenceDiagram"
    CLASS_DIAGRAM = "classDiagram"
    STATE_DIAGRAM = "stateDiagram"
    ENTITY_RELATIONSHIP = "erDiagram"
    USER_JOURNEY = "journey"
    GANTT_CHART = "gantt"
    PIE_CHART = "pie"
    GITGRAPH = "gitGraph"
    REQUIREMENT_DIAGRAM = "requirementDiagram"

@dataclass
class ContextWindow:
    """Context window configuration and state"""
    max_tokens: int = 16000  # Conservative default for GPT-4
    current_tokens: int = 0
    reserved_tokens: int = 1000  # Reserve for response
    
    # Content sections
    system_prompt_tokens: int = 0
    code_context_tokens: int = 0
    documentation_tokens: int = 0
    conversation_tokens: int = 0
    
    # Optimization settings
    optimization_strategy: ContextOptimizationStrategy = ContextOptimizationStrategy.SUMMARIZATION
    compression_ratio: float = 0.3  # Target compression ratio
    priority_weights: Dict[str, float] = field(default_factory=lambda: {
        'recent_conversation': 1.0,
        'current_task': 0.9,
        'code_context': 0.8,
        'documentation': 0.6,
        'historical_context': 0.3
    })

@dataclass
class DocumentationRequest:
    """Request for documentation generation"""
    request_id: str
    doc_type: DocumentationType
    target_system: str
    content_source: str  # File path, module name, or content
    output_path: Optional[str] = None
    
    # Generation parameters
    detail_level: str = "comprehensive"  # basic, standard, comprehensive
    include_examples: bool = True
    include_diagrams: bool = True
    target_audience: str = "developers"  # users, developers, administrators
    
    # Context optimization
    max_context_tokens: int = 12000
    optimization_strategy: ContextOptimizationStrategy = ContextOptimizationStrategy.SUMMARIZATION
    
    # Mermaid-specific settings
    mermaid_theme: str = "default"
    diagram_direction: str = "TD"  # Top-Down, Left-Right, etc.

@dataclass
class GeneratedDocumentation:
    """Generated documentation result"""
    request_id: str
    doc_type: DocumentationType
    content: str
    metadata: Dict[str, Any]
    
    # Quality metrics
    token_count: int = 0
    generation_time: float = 0.0
    completeness_score: float = 0.0
    readability_score: float = 0.0
    
    # Associated files
    diagrams: List[str] = field(default_factory=list)
    supplementary_files: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class TokenEstimator:
    """Token counting and estimation utilities"""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize token estimator"""
        self.model_name = model_name
        self.encoding = None
        
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.encoding_for_model(model_name)
            except KeyError:
                self.encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding
        
        # Fallback token estimation ratios
        self.char_to_token_ratio = 4.0  # Approximate characters per token
        self.word_to_token_ratio = 0.75  # Approximate tokens per word
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if not text:
            return 0
        
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Fallback estimation
            word_count = len(text.split())
            return int(word_count * self.word_to_token_ratio)
    
    def estimate_tokens_from_length(self, text_length: int) -> int:
        """Estimate tokens from character length"""
        return int(text_length / self.char_to_token_ratio)
    
    def truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit"""
        current_tokens = self.count_tokens(text)
        
        if current_tokens <= max_tokens:
            return text
        
        # Binary search for optimal truncation point
        lines = text.split('\n')
        left, right = 0, len(lines)
        best_text = ""
        
        while left <= right:
            mid = (left + right) // 2
            candidate_text = '\n'.join(lines[:mid])
            candidate_tokens = self.count_tokens(candidate_text)
            
            if candidate_tokens <= max_tokens:
                best_text = candidate_text
                left = mid + 1
            else:
                right = mid - 1
        
        return best_text

class ContextOptimizer:
    """Context window optimization and management"""
    
    def __init__(self, token_estimator: TokenEstimator):
        """Initialize context optimizer"""
        self.token_estimator = token_estimator
        self.logger = logging.getLogger(__name__)
    
    async def optimize_context(self, content_sections: Dict[str, str], 
                             context_window: ContextWindow) -> Dict[str, str]:
        """Optimize context to fit within token limits"""
        try:
            # Calculate current token usage
            total_tokens = sum(
                self.token_estimator.count_tokens(content) 
                for content in content_sections.values()
            )
            
            available_tokens = context_window.max_tokens - context_window.reserved_tokens
            
            if total_tokens <= available_tokens:
                self.logger.info(f"✅ Context fits within limits: {total_tokens}/{available_tokens} tokens")
                return content_sections
            
            self.logger.info(f"🔄 Optimizing context: {total_tokens} -> {available_tokens} tokens")
            
            # Apply optimization strategy
            if context_window.optimization_strategy == ContextOptimizationStrategy.SUMMARIZATION:
                return await self._optimize_by_summarization(content_sections, available_tokens)
            
            elif context_window.optimization_strategy == ContextOptimizationStrategy.CHUNKING:
                return await self._optimize_by_chunking(content_sections, available_tokens)
            
            elif context_window.optimization_strategy == ContextOptimizationStrategy.PRIORITIZATION:
                return await self._optimize_by_prioritization(content_sections, available_tokens, context_window.priority_weights)
            
            elif context_window.optimization_strategy == ContextOptimizationStrategy.HIERARCHICAL:
                return await self._optimize_hierarchically(content_sections, available_tokens)
            
            elif context_window.optimization_strategy == ContextOptimizationStrategy.COMPRESSION:
                return await self._optimize_by_compression(content_sections, available_tokens)
            
            else:
                # Default to truncation
                return await self._optimize_by_truncation(content_sections, available_tokens)
                
        except Exception as e:
            self.logger.error(f"❌ Context optimization error: {e}")
            return content_sections
    
    async def _optimize_by_summarization(self, content_sections: Dict[str, str], 
                                       target_tokens: int) -> Dict[str, str]:
        """Optimize context using AI summarization"""
        optimized = {}
        
        for section_name, content in content_sections.items():
            current_tokens = self.token_estimator.count_tokens(content)
            
            if current_tokens > target_tokens // len(content_sections):
                # Summarize this section
                summary = await self._summarize_content(content, target_tokens // len(content_sections))
                optimized[section_name] = summary
            else:
                optimized[section_name] = content
        
        return optimized
    
    async def _optimize_by_chunking(self, content_sections: Dict[str, str], 
                                  target_tokens: int) -> Dict[str, str]:
        """Optimize context by intelligent chunking"""
        optimized = {}
        tokens_per_section = target_tokens // len(content_sections)
        
        for section_name, content in content_sections.items():
            # Split content into logical chunks
            chunks = self._split_into_chunks(content)
            
            # Select most important chunks
            selected_chunks = self._select_important_chunks(chunks, tokens_per_section)
            optimized[section_name] = '\n\n'.join(selected_chunks)
        
        return optimized
    
    async def _optimize_by_prioritization(self, content_sections: Dict[str, str], 
                                        target_tokens: int,
                                        priority_weights: Dict[str, float]) -> Dict[str, str]:
        """Optimize context using priority-based allocation"""
        optimized = {}
        
        # Calculate weighted token allocation
        total_weight = sum(priority_weights.get(section, 0.5) for section in content_sections.keys())
        
        for section_name, content in content_sections.items():
            section_weight = priority_weights.get(section_name, 0.5)
            allocated_tokens = int((section_weight / total_weight) * target_tokens)
            
            if self.token_estimator.count_tokens(content) > allocated_tokens:
                optimized[section_name] = self.token_estimator.truncate_to_token_limit(content, allocated_tokens)
            else:
                optimized[section_name] = content
        
        return optimized
    
    async def _optimize_hierarchically(self, content_sections: Dict[str, str], 
                                     target_tokens: int) -> Dict[str, str]:
        """Optimize context using hierarchical importance"""
        # Extract headers, key information, and supporting details
        optimized = {}
        
        for section_name, content in content_sections.items():
            hierarchy = self._extract_content_hierarchy(content)
            compressed = self._compress_hierarchy(hierarchy, target_tokens // len(content_sections))
            optimized[section_name] = compressed
        
        return optimized
    
    async def _optimize_by_compression(self, content_sections: Dict[str, str], 
                                     target_tokens: int) -> Dict[str, str]:
        """Optimize context using compression techniques"""
        optimized = {}
        
        for section_name, content in content_sections.items():
            # Apply various compression techniques
            compressed = content
            
            # Remove excessive whitespace
            compressed = re.sub(r'\n\s*\n\s*\n', '\n\n', compressed)
            compressed = re.sub(r' +', ' ', compressed)
            
            # Compress code comments
            compressed = re.sub(r'#\s*.*?\n', '', compressed)  # Remove single-line comments
            compressed = re.sub(r'""".*?"""', '', compressed, flags=re.DOTALL)  # Remove docstrings
            
            # Abbreviate common patterns
            compressed = compressed.replace('function', 'fn')
            compressed = compressed.replace('variable', 'var')
            compressed = compressed.replace('parameter', 'param')
            
            optimized[section_name] = compressed
        
        return optimized
    
    async def _optimize_by_truncation(self, content_sections: Dict[str, str], 
                                    target_tokens: int) -> Dict[str, str]:
        """Optimize context by simple truncation"""
        optimized = {}
        tokens_per_section = target_tokens // len(content_sections)
        
        for section_name, content in content_sections.items():
            optimized[section_name] = self.token_estimator.truncate_to_token_limit(content, tokens_per_section)
        
        return optimized
    
    async def _summarize_content(self, content: str, target_tokens: int) -> str:
        """Summarize content using AI"""
        if not OPENAI_AVAILABLE:
            # Fallback to simple truncation
            return self.token_estimator.truncate_to_token_limit(content, target_tokens)
        
        try:
            client = AsyncOpenAI()
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Summarize the following content while preserving key technical information:"},
                    {"role": "user", "content": content}
                ],
                max_tokens=target_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.warning(f"⚠️ AI summarization failed: {e}")
            return self.token_estimator.truncate_to_token_limit(content, target_tokens)
    
    def _split_into_chunks(self, content: str) -> List[str]:
        """Split content into logical chunks"""
        # Split by paragraphs, functions, classes, etc.
        chunks = []
        
        # Split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > 500:  # Chunk size limit
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _select_important_chunks(self, chunks: List[str], target_tokens: int) -> List[str]:
        """Select most important chunks based on content analysis"""
        # Score chunks by importance
        scored_chunks = []
        
        for chunk in chunks:
            score = self._calculate_importance_score(chunk)
            tokens = self.token_estimator.count_tokens(chunk)
            scored_chunks.append((score, tokens, chunk))
        
        # Sort by importance score
        scored_chunks.sort(reverse=True)
        
        # Select chunks within token limit
        selected = []
        total_tokens = 0
        
        for score, tokens, chunk in scored_chunks:
            if total_tokens + tokens <= target_tokens:
                selected.append(chunk)
                total_tokens += tokens
            else:
                break
        
        return selected
    
    def _calculate_importance_score(self, chunk: str) -> float:
        """Calculate importance score for a content chunk"""
        score = 0.0
        
        # Keywords that indicate importance
        important_keywords = [
            'class', 'def', 'function', 'import', 'from', 'async', 'await',
            'try', 'except', 'error', 'warning', 'critical', 'TODO', 'FIXME',
            'API', 'endpoint', 'route', 'database', 'query', 'connection'
        ]
        
        for keyword in important_keywords:
            score += chunk.lower().count(keyword.lower()) * 0.1
        
        # Code blocks are important
        if '```' in chunk or '    ' in chunk:  # Indented code
            score += 0.5
        
        # Headers are important
        if chunk.startswith('#') or chunk.startswith('##'):
            score += 0.3
        
        # Length normalization
        score = score / max(1, len(chunk.split()) / 100)
        
        return score
    
    def _extract_content_hierarchy(self, content: str) -> Dict[str, List[str]]:
        """Extract hierarchical structure from content"""
        hierarchy = {
            'headers': [],
            'key_info': [],
            'details': []
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('#'):
                hierarchy['headers'].append(line)
            elif any(keyword in line.lower() for keyword in ['def ', 'class ', 'import ', 'from ']):
                hierarchy['key_info'].append(line)
            else:
                hierarchy['details'].append(line)
        
        return hierarchy
    
    def _compress_hierarchy(self, hierarchy: Dict[str, List[str]], target_tokens: int) -> str:
        """Compress hierarchical content"""
        result = []
        
        # Always include headers
        result.extend(hierarchy['headers'])
        
        # Include key info if space allows
        remaining_tokens = target_tokens - self.token_estimator.count_tokens('\n'.join(result))
        
        if remaining_tokens > 0:
            key_info_text = '\n'.join(hierarchy['key_info'])
            if self.token_estimator.count_tokens(key_info_text) <= remaining_tokens:
                result.extend(hierarchy['key_info'])
                remaining_tokens -= self.token_estimator.count_tokens(key_info_text)
        
        # Include details if space allows
        if remaining_tokens > 0:
            for detail in hierarchy['details']:
                if self.token_estimator.count_tokens(detail) <= remaining_tokens:
                    result.append(detail)
                    remaining_tokens -= self.token_estimator.count_tokens(detail)
                else:
                    break
        
        return '\n'.join(result)

class MermaidDiagramGenerator:
    """Generator for Mermaid diagrams from system descriptions"""
    
    def __init__(self):
        """Initialize Mermaid diagram generator"""
        self.logger = logging.getLogger(__name__)
        
        # Diagram templates
        self.templates = {
            MermaidDiagramType.FLOWCHART: self._generate_flowchart,
            MermaidDiagramType.SEQUENCE_DIAGRAM: self._generate_sequence_diagram,
            MermaidDiagramType.CLASS_DIAGRAM: self._generate_class_diagram,
            MermaidDiagramType.STATE_DIAGRAM: self._generate_state_diagram,
            MermaidDiagramType.ENTITY_RELATIONSHIP: self._generate_er_diagram
        }
    
    async def generate_diagram_from_description(self, description: str, 
                                              diagram_type: MermaidDiagramType,
                                              theme: str = "default",
                                              direction: str = "TD") -> str:
        """Generate Mermaid diagram from text description"""
        try:
            # Parse description to extract structure
            structure = await self._parse_system_structure(description)
            
            # Generate diagram based on type
            if diagram_type in self.templates:
                diagram_code = await self.templates[diagram_type](structure, direction)
            else:
                raise ValueError(f"Unsupported diagram type: {diagram_type}")
            
            # Apply theme if specified
            if theme != "default":
                diagram_code = f"%%{{init: {{'theme':'{theme}'}}}}%%\n{diagram_code}"
            
            return diagram_code
            
        except Exception as e:
            self.logger.error(f"❌ Mermaid diagram generation error: {e}")
            return self._generate_error_diagram(str(e))
    
    async def generate_orchestrator_diagram(self, orchestrator_description: Dict[str, Any]) -> str:
        """Generate Mermaid diagram from AI Task Orchestrator description"""
        try:
            # Extract orchestrator components
            components = orchestrator_description.get('components', {})
            workflows = orchestrator_description.get('workflows', [])
            dependencies = orchestrator_description.get('dependencies', [])
            
            # Generate flowchart showing orchestrator flow
            diagram = ["flowchart TD"]
            
            # Add components
            for comp_id, comp_info in components.items():
                comp_name = comp_info.get('name', comp_id)
                comp_type = comp_info.get('type', 'component')
                
                if comp_type == 'orchestrator':
                    diagram.append(f"    {comp_id}['{comp_name}']")
                    diagram.append(f"    {comp_id} --> {comp_id}_analysis['Task Analysis']")
                    diagram.append(f"    {comp_id}_analysis --> {comp_id}_planning['Planning']")
                    diagram.append(f"    {comp_id}_planning --> {comp_id}_execution['Execution']")
                    diagram.append(f"    {comp_id}_execution --> {comp_id}_validation['Validation']")
                elif comp_type == 'database':
                    diagram.append(f"    {comp_id}[({comp_name})]")
                elif comp_type == 'service':
                    diagram.append(f"    {comp_id}{{'{comp_name}'}}")
                else:
                    diagram.append(f"    {comp_id}['{comp_name}']")
            
            # Add dependencies
            for dep in dependencies:
                from_comp = dep.get('from')
                to_comp = dep.get('to')
                label = dep.get('label', '')
                
                if from_comp and to_comp:
                    if label:
                        diagram.append(f"    {from_comp} -->|{label}| {to_comp}")
                    else:
                        diagram.append(f"    {from_comp} --> {to_comp}")
            
            # Add styling
            diagram.extend([
                "",
                "    classDef orchestrator fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
                "    classDef database fill:#f3e5f5,stroke:#4a148c,stroke-width:2px", 
                "    classDef service fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px",
                "",
                "    class orchestrator orchestrator",
                "    class database database",
                "    class service service"
            ])
            
            return '\n'.join(diagram)
            
        except Exception as e:
            self.logger.error(f"❌ Orchestrator diagram generation error: {e}")
            return self._generate_error_diagram(str(e))
    
    async def generate_system_architecture_diagram(self, system_info: Dict[str, Any]) -> str:
        """Generate system architecture diagram"""
        try:
            diagram = ["flowchart TB"]
            
            # Add system layers
            layers = system_info.get('layers', {})
            for layer_id, layer_info in layers.items():
                layer_name = layer_info.get('name', layer_id)
                components = layer_info.get('components', [])
                
                # Create subgraph for layer
                diagram.append(f"    subgraph {layer_id}['{layer_name}']")
                
                for comp in components:
                    comp_id = comp.get('id', comp.get('name', '').replace(' ', '_'))
                    comp_name = comp.get('name', comp_id)
                    diagram.append(f"        {layer_id}_{comp_id}['{comp_name}']")
                
                diagram.append("    end")
            
            # Add connections between layers
            connections = system_info.get('connections', [])
            for conn in connections:
                from_comp = conn.get('from')
                to_comp = conn.get('to')
                protocol = conn.get('protocol', '')
                
                if from_comp and to_comp:
                    if protocol:
                        diagram.append(f"    {from_comp} -->|{protocol}| {to_comp}")
                    else:
                        diagram.append(f"    {from_comp} --> {to_comp}")
            
            return '\n'.join(diagram)
            
        except Exception as e:
            self.logger.error(f"❌ System architecture diagram error: {e}")
            return self._generate_error_diagram(str(e))
    
    async def _parse_system_structure(self, description: str) -> Dict[str, Any]:
        """Parse system structure from description"""
        structure = {
            'components': [],
            'connections': [],
            'processes': [],
            'data_flows': []
        }
        
        # Extract components (simplified keyword-based extraction)
        component_keywords = ['class', 'module', 'service', 'database', 'api', 'controller']
        for keyword in component_keywords:
            matches = re.findall(rf'{keyword}\s+(\w+)', description, re.IGNORECASE)
            for match in matches:
                structure['components'].append({
                    'name': match,
                    'type': keyword,
                    'id': f"{keyword}_{match}".lower()
                })
        
        # Extract processes (function definitions, method calls)
        function_matches = re.findall(r'def\s+(\w+)', description)
        for func in function_matches:
            structure['processes'].append({
                'name': func,
                'type': 'function',
                'id': f"func_{func}".lower()
            })
        
        # Extract connections (simplified - look for arrows, flow indicators)
        arrow_patterns = [r'(\w+)\s*->\s*(\w+)', r'(\w+)\s*→\s*(\w+)', r'(\w+)\s+calls?\s+(\w+)']
        for pattern in arrow_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for from_comp, to_comp in matches:
                structure['connections'].append({
                    'from': from_comp.lower(),
                    'to': to_comp.lower(),
                    'type': 'flow'
                })
        
        return structure
    
    async def _generate_flowchart(self, structure: Dict[str, Any], direction: str = "TD") -> str:
        """Generate Mermaid flowchart"""
        diagram = [f"flowchart {direction}"]
        
        # Add components
        for comp in structure.get('components', []):
            comp_id = comp['id']
            comp_name = comp['name']
            comp_type = comp.get('type', 'component')
            
            if comp_type == 'database':
                diagram.append(f"    {comp_id}[({comp_name})]")
            elif comp_type == 'service':
                diagram.append(f"    {comp_id}{{'{comp_name}'}}")
            elif comp_type == 'api':
                diagram.append(f"    {comp_id}[/{comp_name}/]")
            else:
                diagram.append(f"    {comp_id}['{comp_name}']")
        
        # Add processes
        for proc in structure.get('processes', []):
            proc_id = proc['id']
            proc_name = proc['name']
            diagram.append(f"    {proc_id}['{proc_name}()']")
        
        # Add connections
        for conn in structure.get('connections', []):
            from_comp = conn['from']
            to_comp = conn['to']
            diagram.append(f"    {from_comp} --> {to_comp}")
        
        return '\n'.join(diagram)
    
    async def _generate_sequence_diagram(self, structure: Dict[str, Any], direction: str = "TD") -> str:
        """Generate Mermaid sequence diagram"""
        diagram = ["sequenceDiagram"]
        
        # Add participants
        participants = set()
        for comp in structure.get('components', []):
            participants.add(comp['name'])
        for proc in structure.get('processes', []):
            participants.add(proc['name'])
        
        for participant in sorted(participants):
            diagram.append(f"    participant {participant}")
        
        # Add interactions (simplified)
        for i, conn in enumerate(structure.get('connections', [])):
            from_comp = conn['from'].replace('_', ' ').title()
            to_comp = conn['to'].replace('_', ' ').title()
            diagram.append(f"    {from_comp}->>+{to_comp}: Request {i+1}")
            diagram.append(f"    {to_comp}-->>-{from_comp}: Response {i+1}")
        
        return '\n'.join(diagram)
    
    async def _generate_class_diagram(self, structure: Dict[str, Any], direction: str = "TD") -> str:
        """Generate Mermaid class diagram"""
        diagram = ["classDiagram"]
        
        # Add classes
        for comp in structure.get('components', []):
            if comp.get('type') == 'class':
                class_name = comp['name']
                diagram.append(f"    class {class_name} {{")
                diagram.append(f"        +method1()")
                diagram.append(f"        +method2()")
                diagram.append(f"    }}")
        
        # Add relationships
        for conn in structure.get('connections', []):
            from_comp = conn['from'].replace('_', ' ').title()
            to_comp = conn['to'].replace('_', ' ').title()
            diagram.append(f"    {from_comp} --> {to_comp}")
        
        return '\n'.join(diagram)
    
    async def _generate_state_diagram(self, structure: Dict[str, Any], direction: str = "TD") -> str:
        """Generate Mermaid state diagram"""
        diagram = ["stateDiagram-v2"]
        
        # Add states
        states = []
        for proc in structure.get('processes', []):
            state_name = proc['name'].replace('_', ' ').title()
            states.append(state_name)
            diagram.append(f"    {proc['name']} : {state_name}")
        
        # Add transitions
        diagram.append("    [*] --> " + (states[0] if states else "Unknown"))
        for i in range(len(states) - 1):
            diagram.append(f"    {states[i].replace(' ', '')} --> {states[i+1].replace(' ', '')}")
        if states:
            diagram.append(f"    {states[-1].replace(' ', '')} --> [*]")
        
        return '\n'.join(diagram)
    
    async def _generate_er_diagram(self, structure: Dict[str, Any], direction: str = "TD") -> str:
        """Generate Mermaid ER diagram"""
        diagram = ["erDiagram"]
        
        # Add entities
        entities = []
        for comp in structure.get('components', []):
            if comp.get('type') in ['database', 'table', 'entity']:
                entity_name = comp['name'].upper()
                entities.append(entity_name)
                diagram.append(f"    {entity_name} {{")
                diagram.append(f"        int id PK")
                diagram.append(f"        string name")
                diagram.append(f"        datetime created_at")
                diagram.append(f"    }}")
        
        # Add relationships
        for i in range(len(entities) - 1):
            diagram.append(f"    {entities[i]} ||--o{{ {entities[i+1]} : has")
        
        return '\n'.join(diagram)
    
    def _generate_error_diagram(self, error_message: str) -> str:
        """Generate error diagram when generation fails"""
        return f"""flowchart TD
    Error["Diagram Generation Error"]
    Error --> Details["{error_message}"]
    
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    class Error,Details error"""

class IntelligentPromptOptimizer:
    """Optimizer for LLM prompts in large context scenarios"""
    
    def __init__(self, token_estimator: TokenEstimator, context_optimizer: ContextOptimizer):
        """Initialize prompt optimizer"""
        self.token_estimator = token_estimator
        self.context_optimizer = context_optimizer
        self.logger = logging.getLogger(__name__)
    
    async def optimize_prompt(self, base_prompt: str, context_data: Dict[str, str], 
                            max_context_tokens: int = 12000) -> str:
        """Optimize prompt for large context scenarios"""
        try:
            # Create context window
            context_window = ContextWindow(
                max_tokens=max_context_tokens,
                system_prompt_tokens=self.token_estimator.count_tokens(base_prompt)
            )
            
            # Optimize context data
            optimized_context = await self.context_optimizer.optimize_context(context_data, context_window)
            
            # Build optimized prompt
            sections = [base_prompt]
            
            for section_name, content in optimized_context.items():
                if content.strip():
                    sections.append(f"\n## {section_name.replace('_', ' ').title()}\n{content}")
            
            optimized_prompt = '\n'.join(sections)
            
            # Validate final token count
            final_tokens = self.token_estimator.count_tokens(optimized_prompt)
            self.logger.info(f"✅ Prompt optimized: {final_tokens}/{max_context_tokens} tokens")
            
            return optimized_prompt
            
        except Exception as e:
            self.logger.error(f"❌ Prompt optimization error: {e}")
            return base_prompt
    
    async def create_contextual_prompt(self, task_description: str, 
                                     system_info: Dict[str, Any],
                                     code_context: str = "",
                                     documentation_context: str = "") -> str:
        """Create contextually optimized prompt for documentation generation"""
        
        base_prompt = f"""You are an expert technical writer creating comprehensive documentation.

Task: {task_description}

Please generate clear, well-structured documentation that includes:
1. Overview and purpose
2. Technical details with examples
3. Usage instructions
4. API references (if applicable)
5. Troubleshooting information
6. Visual diagrams using Mermaid syntax where helpful

Follow these guidelines:
- Use clear, professional language
- Include practical examples
- Structure content with appropriate headings
- Add code examples with syntax highlighting
- Create Mermaid diagrams for complex concepts
- Ensure accuracy and completeness"""

        context_data = {
            'system_information': json.dumps(system_info, indent=2) if system_info else "",
            'code_context': code_context,
            'documentation_context': documentation_context
        }
        
        return await self.optimize_prompt(base_prompt, context_data)

class DocumentationGenerator:
    """Main documentation generation orchestrator"""
    
    def __init__(self):
        """Initialize documentation generator"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.token_estimator = TokenEstimator()
        self.context_optimizer = ContextOptimizer(self.token_estimator)
        self.mermaid_generator = MermaidDiagramGenerator()
        self.prompt_optimizer = IntelligentPromptOptimizer(self.token_estimator, self.context_optimizer)
        
        # Documentation cache
        self.documentation_cache: Dict[str, GeneratedDocumentation] = {}
        self.generation_history: List[DocumentationRequest] = []
        
        # Performance metrics
        self.generation_metrics = {
            'total_requests': 0,
            'successful_generations': 0,
            'cache_hits': 0,
            'average_generation_time': 0.0,
            'total_tokens_processed': 0
        }
        
        self.logger.info("📚 Intelligent Documentation System initialized")
    
    async def generate_documentation(self, request: DocumentationRequest) -> GeneratedDocumentation:
        """Generate documentation based on request"""
        start_time = time.time()
        self.generation_metrics['total_requests'] += 1
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.documentation_cache:
                self.generation_metrics['cache_hits'] += 1
                self.logger.info(f"📋 Cache hit for documentation request: {request.request_id}")
                return self.documentation_cache[cache_key]
            
            self.logger.info(f"📝 Generating documentation: {request.doc_type.value} for {request.target_system}")
            
            # Load content source
            source_content = await self._load_content_source(request.content_source)
            
            # Generate based on documentation type
            if request.doc_type == DocumentationType.MERMAID_DIAGRAM:
                content = await self._generate_mermaid_documentation(request, source_content)
            elif request.doc_type == DocumentationType.API_DOCUMENTATION:
                content = await self._generate_api_documentation(request, source_content)
            elif request.doc_type == DocumentationType.SYSTEM_ARCHITECTURE:
                content = await self._generate_architecture_documentation(request, source_content)
            elif request.doc_type == DocumentationType.USER_GUIDE:
                content = await self._generate_user_guide(request, source_content)
            elif request.doc_type == DocumentationType.TECHNICAL_REFERENCE:
                content = await self._generate_technical_reference(request, source_content)
            else:
                content = await self._generate_generic_documentation(request, source_content)
            
            # Create result
            generation_time = time.time() - start_time
            
            result = GeneratedDocumentation(
                request_id=request.request_id,
                doc_type=request.doc_type,
                content=content,
                metadata={
                    'target_system': request.target_system,
                    'source': request.content_source,
                    'detail_level': request.detail_level,
                    'target_audience': request.target_audience
                },
                token_count=self.token_estimator.count_tokens(content),
                generation_time=generation_time,
                completeness_score=self._calculate_completeness_score(content, request),
                readability_score=self._calculate_readability_score(content)
            )
            
            # Save to cache
            self.documentation_cache[cache_key] = result
            
            # Update metrics
            self.generation_metrics['successful_generations'] += 1
            self.generation_metrics['total_tokens_processed'] += result.token_count
            self._update_average_generation_time(generation_time)
            
            # Save to file if output path specified
            if request.output_path:
                await self._save_documentation_to_file(result, request.output_path)
            
            self.logger.info(f"✅ Documentation generated successfully: {result.token_count} tokens in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Documentation generation failed: {e}")
            generation_time = time.time() - start_time
            
            return GeneratedDocumentation(
                request_id=request.request_id,
                doc_type=request.doc_type,
                content=f"# Documentation Generation Error\n\n**Error**: {str(e)}\n\nPlease check the request parameters and try again.",
                metadata={'error': str(e)},
                generation_time=generation_time
            )
    
    async def generate_orchestrator_documentation(self, orchestrator_instance) -> GeneratedDocumentation:
        """Generate comprehensive documentation for AI Task Orchestrator"""
        try:
            if not AI_ORCHESTRATOR_AVAILABLE:
                raise RuntimeError("AI Task Orchestrator not available")
            
            # Get orchestrator description
            orchestrator_description = await self._describe_orchestrator(orchestrator_instance)
            
            # Generate documentation request
            request = DocumentationRequest(
                request_id=f"orchestrator_docs_{uuid.uuid4().hex[:8]}",
                doc_type=DocumentationType.SYSTEM_ARCHITECTURE,
                target_system="AI Task Orchestrator",
                content_source="orchestrator_instance",
                detail_level="comprehensive",
                include_diagrams=True,
                target_audience="developers"
            )
            
            # Generate comprehensive documentation
            documentation_sections = await self._generate_orchestrator_sections(orchestrator_description)
            
            # Generate Mermaid diagram
            mermaid_diagram = await self.mermaid_generator.generate_orchestrator_diagram(orchestrator_description)
            
            # Combine all sections
            content_parts = [
                "# AI Task Orchestrator Documentation",
                "",
                "## System Overview",
                documentation_sections.get('overview', ''),
                "",
                "## Architecture Diagram",
                "```mermaid",
                mermaid_diagram,
                "```",
                "",
                "## Components",
                documentation_sections.get('components', ''),
                "",
                "## Workflows",
                documentation_sections.get('workflows', ''),
                "",
                "## API Reference",
                documentation_sections.get('api_reference', ''),
                "",
                "## Usage Examples",
                documentation_sections.get('examples', ''),
                "",
                "## Configuration",
                documentation_sections.get('configuration', ''),
                "",
                "## Troubleshooting",
                documentation_sections.get('troubleshooting', '')
            ]
            
            content = '\n'.join(content_parts)
            
            result = GeneratedDocumentation(
                request_id=request.request_id,
                doc_type=request.doc_type,
                content=content,
                metadata={
                    'target_system': 'AI Task Orchestrator',
                    'components_documented': len(orchestrator_description.get('components', {})),
                    'workflows_documented': len(orchestrator_description.get('workflows', [])),
                    'includes_diagram': True
                },
                token_count=self.token_estimator.count_tokens(content),
                diagrams=[mermaid_diagram],
                completeness_score=0.95,
                readability_score=0.90
            )
            
            self.logger.info("✅ AI Task Orchestrator documentation generated")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Orchestrator documentation generation failed: {e}")
            raise
    
    async def _load_content_source(self, content_source: str) -> str:
        """Load content from various sources"""
        try:
            if content_source.startswith('/') or content_source.endswith('.py') or content_source.endswith('.md'):
                # File path
                file_path = Path(content_source)
                if file_path.exists():
                    return file_path.read_text(encoding='utf-8')
                else:
                    return f"File not found: {content_source}"
            
            elif content_source.startswith('http'):
                # URL (not implemented for security)
                return "URL sources not supported"
            
            else:
                # Direct content or module name
                return content_source
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load content source: {e}")
            return content_source
    
    async def _generate_mermaid_documentation(self, request: DocumentationRequest, source_content: str) -> str:
        """Generate Mermaid diagram documentation"""
        diagram_type = MermaidDiagramType.FLOWCHART  # Default
        
        # Determine diagram type from request or content
        if 'sequence' in request.target_system.lower():
            diagram_type = MermaidDiagramType.SEQUENCE_DIAGRAM
        elif 'class' in request.target_system.lower():
            diagram_type = MermaidDiagramType.CLASS_DIAGRAM
        elif 'state' in request.target_system.lower():
            diagram_type = MermaidDiagramType.STATE_DIAGRAM
        elif 'entity' in request.target_system.lower() or 'database' in request.target_system.lower():
            diagram_type = MermaidDiagramType.ENTITY_RELATIONSHIP
        
        # Generate diagram
        diagram_code = await self.mermaid_generator.generate_diagram_from_description(
            source_content, diagram_type, request.mermaid_theme, request.diagram_direction
        )
        
        # Create documentation with diagram
        content = f"""# {request.target_system} - {diagram_type.value.title()}

## Overview
This diagram represents the {request.target_system} system architecture and component relationships.

## Diagram
```mermaid
{diagram_code}
```

## Description
{source_content[:500]}...

## Usage
To use this diagram:
1. Copy the Mermaid code above
2. Paste it into any Mermaid-compatible editor
3. Customize colors and styling as needed

## Generated Information
- **Diagram Type**: {diagram_type.value}
- **Theme**: {request.mermaid_theme}
- **Direction**: {request.diagram_direction}
- **Generated**: {datetime.now().isoformat()}
"""
        
        return content
    
    async def _generate_api_documentation(self, request: DocumentationRequest, source_content: str) -> str:
        """Generate API documentation"""
        # Parse API endpoints, methods, parameters from source
        api_info = await self._parse_api_information(source_content)
        
        content_parts = [
            f"# {request.target_system} API Documentation",
            "",
            "## Overview",
            f"This document provides comprehensive API documentation for {request.target_system}.",
            "",
            "## Base URL",
            f"`{api_info.get('base_url', 'https://api.example.com')}`",
            "",
            "## Authentication",
            api_info.get('authentication', 'Authentication information not available.'),
            "",
            "## Endpoints"
        ]
        
        # Add endpoint documentation
        for endpoint in api_info.get('endpoints', []):
            content_parts.extend([
                f"### {endpoint.get('method', 'GET').upper()} {endpoint.get('path', '/unknown')}",
                "",
                endpoint.get('description', 'No description available.'),
                "",
                "#### Parameters",
                "| Name | Type | Required | Description |",
                "|------|------|----------|-------------|",
            ])
            
            for param in endpoint.get('parameters', []):
                required = "Yes" if param.get('required', False) else "No"
                content_parts.append(f"| {param.get('name', '')} | {param.get('type', '')} | {required} | {param.get('description', '')} |")
            
            content_parts.extend([
                "",
                "#### Response",
                "```json",
                json.dumps(endpoint.get('response_example', {}), indent=2),
                "```",
                ""
            ])
        
        return '\n'.join(content_parts)
    
    async def _generate_architecture_documentation(self, request: DocumentationRequest, source_content: str) -> str:
        """Generate system architecture documentation"""
        # Parse system architecture information
        arch_info = await self._parse_architecture_information(source_content)
        
        # Generate architecture diagram
        architecture_diagram = await self.mermaid_generator.generate_system_architecture_diagram(arch_info)
        
        content_parts = [
            f"# {request.target_system} - System Architecture",
            "",
            "## Overview",
            f"This document describes the architecture of {request.target_system}.",
            "",
            "## Architecture Diagram",
            "```mermaid",
            architecture_diagram,
            "```",
            "",
            "## System Components"
        ]
        
        # Add component documentation
        for layer_name, layer_info in arch_info.get('layers', {}).items():
            content_parts.extend([
                f"### {layer_info.get('name', layer_name)}",
                "",
                layer_info.get('description', 'No description available.'),
                "",
                "#### Components:"
            ])
            
            for component in layer_info.get('components', []):
                content_parts.append(f"- **{component.get('name', 'Unknown')}**: {component.get('description', 'No description')}")
            
            content_parts.append("")
        
        # Add data flow section
        content_parts.extend([
            "## Data Flow",
            "",
            "The following describes how data flows through the system:",
            ""
        ])
        
        for connection in arch_info.get('connections', []):
            from_comp = connection.get('from', 'Unknown')
            to_comp = connection.get('to', 'Unknown')
            protocol = connection.get('protocol', 'Unknown protocol')
            content_parts.append(f"- {from_comp} → {to_comp} via {protocol}")
        
        return '\n'.join(content_parts)
    
    async def _generate_user_guide(self, request: DocumentationRequest, source_content: str) -> str:
        """Generate user guide documentation"""
        content = f"""# {request.target_system} - User Guide

## Getting Started

Welcome to {request.target_system}! This guide will help you get up and running quickly.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps
1. Install the package:
   ```bash
   pip install {request.target_system.lower().replace(' ', '-')}
   ```

2. Verify installation:
   ```bash
   python -c "import {request.target_system.lower().replace(' ', '_')}; print('Installation successful!')"
   ```

## Quick Start

### Basic Usage
```python
from {request.target_system.lower().replace(' ', '_')} import main_function

# Initialize the system
system = main_function()

# Basic operation
result = system.process()
print(result)
```

## Common Tasks

### Task 1: Basic Operation
Description of how to perform basic operations.

### Task 2: Advanced Configuration
Description of advanced configuration options.

## Troubleshooting

### Common Issues

#### Issue 1: Installation Problems
**Problem**: Package fails to install
**Solution**: Ensure you have the latest pip version

#### Issue 2: Import Errors
**Problem**: Cannot import modules
**Solution**: Check Python path and installation

## Support

For additional help:
- Check the documentation: [link]
- Submit issues: [link]
- Community forum: [link]

## Generated Information
- **Generated**: {datetime.now().isoformat()}
- **Target Audience**: {request.target_audience}
- **Detail Level**: {request.detail_level}
"""
        
        return content
    
    async def _generate_technical_reference(self, request: DocumentationRequest, source_content: str) -> str:
        """Generate technical reference documentation"""
        # Parse technical information from source
        tech_info = await self._parse_technical_information(source_content)
        
        content_parts = [
            f"# {request.target_system} - Technical Reference",
            "",
            "## Overview",
            f"Technical reference documentation for {request.target_system}.",
            "",
            "## Architecture",
            tech_info.get('architecture', 'Architecture information not available.'),
            "",
            "## Modules and Classes"
        ]
        
        # Add class/module documentation
        for module in tech_info.get('modules', []):
            content_parts.extend([
                f"### {module.get('name', 'Unknown Module')}",
                "",
                module.get('description', 'No description available.'),
                "",
                "#### Classes:"
            ])
            
            for cls in module.get('classes', []):
                content_parts.extend([
                    f"##### {cls.get('name', 'Unknown Class')}",
                    "",
                    cls.get('description', 'No description available.'),
                    "",
                    "**Methods:**"
                ])
                
                for method in cls.get('methods', []):
                    content_parts.append(f"- `{method.get('name', 'unknown')}({method.get('parameters', '')})`: {method.get('description', 'No description')}")
                
                content_parts.append("")
        
        return '\n'.join(content_parts)
    
    async def _generate_generic_documentation(self, request: DocumentationRequest, source_content: str) -> str:
        """Generate generic documentation"""
        return f"""# {request.target_system} Documentation

## Overview
This document provides information about {request.target_system}.

## Content Analysis
Based on the source content provided, here is the extracted information:

{source_content[:2000]}...

## Generated Information
- **Documentation Type**: {request.doc_type.value}
- **Target System**: {request.target_system}
- **Detail Level**: {request.detail_level}
- **Target Audience**: {request.target_audience}
- **Generated**: {datetime.now().isoformat()}

## Additional Information
For more detailed information, please refer to the source materials or contact the development team.
"""
    
    async def _describe_orchestrator(self, orchestrator_instance) -> Dict[str, Any]:
        """Generate description of AI Task Orchestrator"""
        description = {
            'components': {
                'orchestrator': {
                    'name': 'AI Task Orchestrator',
                    'type': 'orchestrator',
                    'description': 'Main coordination and workflow management system'
                },
                'neo4j': {
                    'name': 'Neo4j Knowledge Graph',
                    'type': 'database',
                    'description': 'Graph database for storing relationships and knowledge'
                },
                'redis': {
                    'name': 'Redis Cache',
                    'type': 'database',
                    'description': 'High-performance caching layer'
                },
                'postgresql': {
                    'name': 'PostgreSQL',
                    'type': 'database',
                    'description': 'Relational database for structured data'
                },
                'qdrant': {
                    'name': 'Qdrant Vector DB',
                    'type': 'database',
                    'description': 'Vector database for semantic search'
                },
                'wolfram': {
                    'name': 'WolframAlpha Pro',
                    'type': 'service',
                    'description': 'Mathematical computation and validation service'
                }
            },
            'workflows': [
                {
                    'name': 'Task Analysis',
                    'description': 'Analyze task complexity and requirements',
                    'steps': ['complexity_assessment', 'requirement_extraction', 'resource_discovery']
                },
                {
                    'name': 'Implementation Planning',
                    'description': 'Create systematic implementation plan',
                    'steps': ['strategy_selection', 'milestone_definition', 'risk_assessment']
                },
                {
                    'name': 'Execution Management',
                    'description': 'Coordinate task execution and monitoring',
                    'steps': ['resource_allocation', 'progress_tracking', 'quality_assurance']
                },
                {
                    'name': 'Validation & Documentation',
                    'description': 'Validate results and generate documentation',
                    'steps': ['result_validation', 'documentation_generation', 'completion_reporting']
                }
            ],
            'dependencies': [
                {'from': 'orchestrator', 'to': 'neo4j', 'label': 'Knowledge Queries'},
                {'from': 'orchestrator', 'to': 'redis', 'label': 'Caching'},
                {'from': 'orchestrator', 'to': 'postgresql', 'label': 'Data Storage'},
                {'from': 'orchestrator', 'to': 'qdrant', 'label': 'Vector Search'},
                {'from': 'orchestrator', 'to': 'wolfram', 'label': 'Mathematical Validation'}
            ]
        }
        
        return description
    
    async def _generate_orchestrator_sections(self, orchestrator_description: Dict[str, Any]) -> Dict[str, str]:
        """Generate detailed sections for orchestrator documentation"""
        sections = {}
        
        # Overview section
        sections['overview'] = """The AI Task Orchestrator is a comprehensive framework for systematic problem-solving and task completion. It provides structured guidance for complex coding tasks through intelligent analysis, planning, and execution coordination.

Key capabilities:
- Automatic complexity assessment and requirement extraction
- Intelligent resource discovery and utilization
- Multi-database memory integration
- Real-time progress monitoring and validation
- Comprehensive documentation generation"""
        
        # Components section
        components_text = []
        for comp_id, comp_info in orchestrator_description.get('components', {}).items():
            components_text.append(f"### {comp_info['name']}")
            components_text.append(f"**Type**: {comp_info['type']}")
            components_text.append(f"**Description**: {comp_info['description']}")
            components_text.append("")
        
        sections['components'] = '\n'.join(components_text)
        
        # Workflows section
        workflows_text = []
        for workflow in orchestrator_description.get('workflows', []):
            workflows_text.append(f"### {workflow['name']}")
            workflows_text.append(f"{workflow['description']}")
            workflows_text.append("**Steps:**")
            for step in workflow.get('steps', []):
                workflows_text.append(f"1. {step.replace('_', ' ').title()}")
            workflows_text.append("")
        
        sections['workflows'] = '\n'.join(workflows_text)
        
        # API Reference section
        sections['api_reference'] = """### Core Methods

#### `analyze_task(task_description: str) -> TaskAnalysis`
Analyze task complexity and extract requirements.

#### `create_implementation_plan(analysis: TaskAnalysis) -> ImplementationPlan`
Create systematic implementation plan based on analysis.

#### `execute_task(plan: ImplementationPlan) -> ExecutionResult`
Execute task according to implementation plan.

#### `validate_result(result: ExecutionResult) -> ValidationReport`
Validate execution results and generate quality metrics."""
        
        # Examples section
        sections['examples'] = """### Basic Usage

```python
from ai_task_orchestrator import AITaskOrchestrator

# Initialize orchestrator
orchestrator = AITaskOrchestrator()

# Analyze task
task_desc = "Create a REST API for user management"
analysis = await orchestrator.analyze_task(task_desc)

# Create implementation plan
plan = await orchestrator.create_implementation_plan(analysis)

# Execute task
result = await orchestrator.execute_task(plan)

# Validate result
validation = await orchestrator.validate_result(result)
```

### Advanced Configuration

```python
# Configure with custom settings
config = {
    'complexity_threshold': 'EXTENSIVE',
    'validation_level': 'COMPREHENSIVE',
    'memory_integration': True
}

orchestrator = AITaskOrchestrator(config)
```"""
        
        # Configuration section
        sections['configuration'] = """### Environment Variables

- `NEO4J_URI`: Neo4j database connection URI
- `REDIS_URL`: Redis cache connection URL
- `POSTGRESQL_URL`: PostgreSQL database URL
- `QDRANT_URL`: Qdrant vector database URL
- `WOLFRAM_APP_ID`: WolframAlpha Pro API key

### Configuration File

```yaml
orchestrator:
  complexity_assessment:
    enabled: true
    detailed_analysis: true
  
  memory_integration:
    neo4j_enabled: true
    redis_enabled: true
    postgresql_enabled: true
    qdrant_enabled: true
  
  validation:
    wolfram_enabled: true
    comprehensive_testing: true
```"""
        
        # Troubleshooting section
        sections['troubleshooting'] = """### Common Issues

#### Database Connection Errors
**Problem**: Cannot connect to databases
**Solution**: 
1. Check connection URLs in environment variables
2. Verify database services are running
3. Check network connectivity and firewall settings

#### Performance Issues
**Problem**: Slow task execution
**Solution**:
1. Enable Redis caching
2. Optimize database queries
3. Increase resource allocation

#### Memory Integration Problems
**Problem**: Memory system not responding
**Solution**:
1. Verify all database services are operational
2. Check memory coordinator configuration
3. Review database connection pooling settings"""
        
        return sections
    
    async def _parse_api_information(self, source_content: str) -> Dict[str, Any]:
        """Parse API information from source content"""
        api_info = {
            'base_url': 'https://api.example.com',
            'authentication': 'Bearer token authentication required.',
            'endpoints': []
        }
        
        # Simple regex-based parsing (in production, use AST parsing)
        endpoint_pattern = r'@app\.(get|post|put|delete)\(["\']([^"\']+)["\']'
        matches = re.findall(endpoint_pattern, source_content, re.IGNORECASE)
        
        for method, path in matches:
            endpoint = {
                'method': method.upper(),
                'path': path,
                'description': f'{method.upper()} operation for {path}',
                'parameters': [
                    {'name': 'id', 'type': 'integer', 'required': True, 'description': 'Resource ID'}
                ],
                'response_example': {'status': 'success', 'data': {}}
            }
            api_info['endpoints'].append(endpoint)
        
        return api_info
    
    async def _parse_architecture_information(self, source_content: str) -> Dict[str, Any]:
        """Parse architecture information from source content"""
        arch_info = {
            'layers': {
                'presentation': {
                    'name': 'Presentation Layer',
                    'description': 'User interface and API endpoints',
                    'components': [
                        {'name': 'Web Interface', 'description': 'Frontend web application'},
                        {'name': 'REST API', 'description': 'RESTful API endpoints'}
                    ]
                },
                'business': {
                    'name': 'Business Logic Layer',
                    'description': 'Core business logic and processing',
                    'components': [
                        {'name': 'Service Layer', 'description': 'Business services'},
                        {'name': 'Domain Models', 'description': 'Domain objects and logic'}
                    ]
                },
                'data': {
                    'name': 'Data Layer',
                    'description': 'Data persistence and storage',
                    'components': [
                        {'name': 'Database', 'description': 'Primary data storage'},
                        {'name': 'Cache', 'description': 'Caching layer'}
                    ]
                }
            },
            'connections': [
                {'from': 'presentation_web', 'to': 'business_service', 'protocol': 'HTTP/REST'},
                {'from': 'business_service', 'to': 'data_database', 'protocol': 'SQL'},
                {'from': 'business_service', 'to': 'data_cache', 'protocol': 'Redis'}
            ]
        }
        
        return arch_info
    
    async def _parse_technical_information(self, source_content: str) -> Dict[str, Any]:
        """Parse technical information from source content"""
        tech_info = {
            'architecture': 'Modular Python application with clean architecture principles.',
            'modules': [
                {
                    'name': 'Core Module',
                    'description': 'Core functionality and base classes',
                    'classes': [
                        {
                            'name': 'BaseClass',
                            'description': 'Base class for all components',
                            'methods': [
                                {'name': 'initialize', 'parameters': 'config: Dict', 'description': 'Initialize component'},
                                {'name': 'process', 'parameters': 'data: Any', 'description': 'Process data'}
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Extract class and function definitions
        class_pattern = r'class\s+(\w+)'
        function_pattern = r'def\s+(\w+)\s*\([^)]*\)'
        
        classes = re.findall(class_pattern, source_content)
        functions = re.findall(function_pattern, source_content)
        
        if classes or functions:
            module = {
                'name': 'Extracted Module',
                'description': 'Module extracted from source content',
                'classes': []
            }
            
            for cls_name in classes:
                module['classes'].append({
                    'name': cls_name,
                    'description': f'Class {cls_name} extracted from source',
                    'methods': [{'name': func, 'parameters': '', 'description': f'Method {func}'} for func in functions[:3]]
                })
            
            tech_info['modules'] = [module]
        
        return tech_info
    
    def _generate_cache_key(self, request: DocumentationRequest) -> str:
        """Generate cache key for documentation request"""
        key_data = f"{request.doc_type.value}_{request.target_system}_{request.detail_level}_{request.target_audience}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _calculate_completeness_score(self, content: str, request: DocumentationRequest) -> float:
        """Calculate completeness score for generated documentation"""
        score = 0.0
        
        # Check for essential sections
        if "# " in content:  # Has main heading
            score += 0.2
        if "## " in content:  # Has subheadings
            score += 0.2
        if "```" in content:  # Has code examples
            score += 0.2
        if "mermaid" in content.lower():  # Has diagrams
            score += 0.2
        if len(content) > 1000:  # Substantial content
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score for generated documentation"""
        # Simple readability metrics
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if not non_empty_lines:
            return 0.0
        
        # Average line length (shorter is generally more readable)
        avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
        line_length_score = max(0, 1 - (avg_line_length - 80) / 200)  # Penalty for very long lines
        
        # Structure score (headers, lists, code blocks)
        structure_elements = content.count('#') + content.count('- ') + content.count('```')
        structure_score = min(1.0, structure_elements / len(non_empty_lines) * 10)
        
        return (line_length_score + structure_score) / 2
    
    def _update_average_generation_time(self, generation_time: float):
        """Update average generation time metric"""
        total_generations = self.generation_metrics['successful_generations']
        if total_generations > 0:
            current_avg = self.generation_metrics['average_generation_time']
            self.generation_metrics['average_generation_time'] = (
                (current_avg * (total_generations - 1) + generation_time) / total_generations
            )
    
    async def _save_documentation_to_file(self, documentation: GeneratedDocumentation, output_path: str):
        """Save generated documentation to file"""
        try:
            file_path = Path(output_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata header
            metadata_header = f"""<!--
Generated Documentation
========================
Request ID: {documentation.request_id}
Type: {documentation.doc_type.value}
Generated: {documentation.created_at.isoformat()}
Token Count: {documentation.token_count}
Generation Time: {documentation.generation_time:.2f}s
Completeness Score: {documentation.completeness_score:.2f}
Readability Score: {documentation.readability_score:.2f}
-->

"""
            
            full_content = metadata_header + documentation.content
            file_path.write_text(full_content, encoding='utf-8')
            
            self.logger.info(f"✅ Documentation saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save documentation: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of documentation system"""
        return {
            'system_status': 'operational',
            'metrics': self.generation_metrics,
            'capabilities': {
                'token_estimation': TIKTOKEN_AVAILABLE,
                'ai_optimization': OPENAI_AVAILABLE,
                'orchestrator_integration': AI_ORCHESTRATOR_AVAILABLE,
                'advanced_visualizations': GRAPHVIZ_AVAILABLE
            },
            'cache_stats': {
                'cached_documents': len(self.documentation_cache),
                'cache_hit_rate': self.generation_metrics['cache_hits'] / max(1, self.generation_metrics['total_requests'])
            },
            'supported_doc_types': [doc_type.value for doc_type in DocumentationType],
            'supported_diagram_types': [diagram_type.value for diagram_type in MermaidDiagramType],
            'timestamp': datetime.now().isoformat()
        }

# Global instance
intelligent_documentation_system = DocumentationGenerator()

# Alias classes for test compatibility
MermaidGenerator = MermaidDiagramGenerator
DocumentationFramework = DocumentationGenerator

async def main():
    """
    Demonstration of the Intelligent Documentation System
    """
    logger.info("📚 Intelligent Documentation System Demo")
    
    # Initialize components
    token_estimator = TokenEstimator()
    context_optimizer = ContextOptimizer(token_estimator)
    mermaid_generator = MermaidDiagramGenerator()
    prompt_optimizer = IntelligentPromptOptimizer(token_estimator, context_optimizer)
    doc_generator = DocumentationGenerator()
    
    # Example system structure for documentation
    example_system = {
        "name": "PLC Control System",
        "description": "Industrial control system with PID controllers",
        "components": [
            {
                "name": "PIDController",
                "type": "class",
                "description": "Main PID controller implementation",
                "methods": ["calculate", "tune", "reset"],
                "relationships": ["uses DataLogger", "extends BaseController"]
            },
            {
                "name": "DataLogger", 
                "type": "service",
                "description": "Logs process data to database",
                "methods": ["log", "retrieve", "archive"],
                "relationships": ["stores ProcessData"]
            },
            {
                "name": "HMI",
                "type": "interface",
                "description": "Human-machine interface",
                "methods": ["display", "update", "alert"],
                "relationships": ["monitors PIDController"]
            }
        ]
    }
    
    # Test token estimation
    example_text = """
    This is an example documentation text that we want to estimate tokens for.
    It contains multiple sentences and technical content about PID controllers,
    process variables, and control algorithms.
    """
    
    tokens = token_estimator.count_tokens(example_text)
    logger.info(f"📊 Token estimation: {tokens} tokens")
    
    # Test context optimization
    large_content = example_text * 10  # Simulate large content
    context_window = ContextWindow(
        max_tokens=1000,
        current_tokens=token_estimator.count_tokens(large_content),
        priority_weights={
            'recent_conversation': 1.0,
            'current_task': 0.9,
            'code_context': 0.8,
            'documentation': 0.6,
            'historical_context': 0.3
        },
        optimization_strategy=ContextOptimizationStrategy.PRIORITIZATION
    )
    
    optimized_content = await context_optimizer.optimize_context({
        'system_information': json.dumps(example_system, indent=2),
        'code_context': example_text,
        'documentation_context': ""
    }, context_window)
    logger.info(f"🔧 Context optimization: {token_estimator.count_tokens(large_content)} tokens (was {token_estimator.count_tokens(large_content)})")
    
    # Test Mermaid diagram generation
    flowchart = await mermaid_generator.generate_diagram_from_description(
        "System with user authentication, database storage, and API endpoints",
        MermaidDiagramType.FLOWCHART,
        direction="TD"
    )
    logger.info(f"📊 Generated Mermaid flowchart:\n{flowchart}")
    
    # Test documentation generation
    doc_request = DocumentationRequest(
        request_id=f"demo_doc_{uuid.uuid4().hex[:8]}",
        doc_type=DocumentationType.SYSTEM_ARCHITECTURE,
        target_system="PLC Control System",
        content_source=json.dumps(example_system, indent=2),
        detail_level="comprehensive",
        target_audience="developers",
        max_context_tokens=1000,
        optimization_strategy=ContextOptimizationStrategy.PRIORITIZATION,
        mermaid_theme="default",
        diagram_direction="TD"
    )
    
    documentation = await doc_generator.generate_documentation(doc_request)
    logger.info(f"📖 Generated documentation: {len(documentation.content)} characters")
    logger.info(f"📊 Documentation quality score: {documentation.completeness_score:.2f}")
    
    # Test prompt optimization
    example_prompt = "Generate comprehensive documentation for a PID control system including algorithms, tuning methods, and implementation details."
    
    optimized_prompt = await prompt_optimizer.optimize_prompt(
        example_prompt,
        {
            'system_information': json.dumps(example_system, indent=2),
            'code_context': example_text,
            'documentation_context': ""
        },
        max_context_tokens=500
    )
    logger.info(f"✨ Optimized prompt: {optimized_prompt}")
    
    logger.info("✅ Intelligent Documentation System Demo Completed")

if __name__ == "__main__":
    asyncio.run(main()) 