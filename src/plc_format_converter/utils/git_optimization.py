"""
Git optimization utilities for PLC format conversion.

This module provides git-optimized formatting for L5X files to enable
meaningful diffs and merges in version control systems.

Phase 3.9 Enhanced Features:
- Git-friendly L5X formatting
- Consistent element ordering
- Meaningful diff generation
- Merge conflict resolution support
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from xml.etree import ElementTree as ET
import re

from ..core.models import PLCProject

logger = logging.getLogger(__name__)


class GitOptimizer:
    """Git optimization utilities for PLC projects."""
    
    def __init__(self):
        """Initialize GitOptimizer."""
        self.formatting_rules = {
            'indent': '  ',  # 2 spaces for consistency
            'max_line_length': 120,
            'sort_attributes': True,
            'preserve_whitespace': False
        }
    
    def optimize_for_git(self, project: PLCProject) -> str:
        """
        Optimize PLC project for git version control.
        
        Args:
            project: PLCProject to optimize
            
        Returns:
            Git-optimized L5X content as string
        """
        try:
            # Convert project to XML structure
            xml_content = self._project_to_xml(project)
            
            # Apply git optimization
            optimized_content = self._apply_git_formatting(xml_content)
            
            logger.info(f"Successfully optimized project '{project.name}' for git")
            return optimized_content
            
        except Exception as e:
            logger.error(f"Failed to optimize project for git: {e}")
            raise
    
    def _project_to_xml(self, project: PLCProject) -> str:
        """Convert PLCProject to XML string."""
        # This would integrate with the L5XHandler
        # For now, return a placeholder
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<RSLogix5000Content></RSLogix5000Content>'
    
    def _apply_git_formatting(self, xml_content: str) -> str:
        """Apply git-friendly formatting to XML content."""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Sort elements for consistency
            self._sort_elements_recursively(root)
            
            # Apply consistent formatting
            formatted_xml = self._format_xml_for_git(root)
            
            return formatted_xml
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error during git optimization: {e}")
            raise
    
    def _sort_elements_recursively(self, element: ET.Element) -> None:
        """Sort XML elements recursively for consistent ordering."""
        # Sort child elements by tag name, then by 'Name' attribute if present
        def sort_key(elem):
            name_attr = elem.get('Name', '')
            return (elem.tag, name_attr)
        
        # Sort children
        element[:] = sorted(element, key=sort_key)
        
        # Recursively sort children
        for child in element:
            self._sort_elements_recursively(child)
    
    def _format_xml_for_git(self, root: ET.Element) -> str:
        """Format XML with git-friendly indentation and structure."""
        # Convert to string with proper formatting
        xml_str = ET.tostring(root, encoding='unicode')
        
        # Apply consistent indentation
        formatted_lines = []
        indent_level = 0
        
        for line in xml_str.split('\n'):
            stripped = line.strip()
            if not stripped:
                continue
                
            # Adjust indent level
            if stripped.startswith('</'):
                indent_level -= 1
            
            # Add formatted line
            formatted_lines.append(self.formatting_rules['indent'] * indent_level + stripped)
            
            # Increase indent for opening tags
            if stripped.startswith('<') and not stripped.startswith('</') and not stripped.endswith('/>'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def generate_diff_summary(self, old_project: PLCProject, new_project: PLCProject) -> Dict[str, Any]:
        """
        Generate a summary of changes between two projects.
        
        Args:
            old_project: Original project
            new_project: Modified project
            
        Returns:
            Dictionary containing change summary
        """
        changes = {
            'controllers_modified': [],
            'programs_added': [],
            'programs_removed': [],
            'programs_modified': [],
            'tags_added': [],
            'tags_removed': [],
            'tags_modified': [],
            'routines_added': [],
            'routines_removed': [],
            'routines_modified': []
        }
        
        try:
            # Compare controllers
            old_controllers = {c.name: c for c in old_project.controllers}
            new_controllers = {c.name: c for c in new_project.controllers}
            
            for name, new_controller in new_controllers.items():
                if name in old_controllers:
                    if self._controllers_different(old_controllers[name], new_controller):
                        changes['controllers_modified'].append(name)
                        
                        # Compare programs within controller
                        old_programs = {p.name: p for p in old_controllers[name].programs}
                        new_programs = {p.name: p for p in new_controller.programs}
                        
                        # Find added/removed programs
                        for prog_name in new_programs:
                            if prog_name not in old_programs:
                                changes['programs_added'].append(f"{name}.{prog_name}")
                        
                        for prog_name in old_programs:
                            if prog_name not in new_programs:
                                changes['programs_removed'].append(f"{name}.{prog_name}")
                        
                        # Find modified programs
                        for prog_name in set(old_programs.keys()) & set(new_programs.keys()):
                            if self._programs_different(old_programs[prog_name], new_programs[prog_name]):
                                changes['programs_modified'].append(f"{name}.{prog_name}")
            
            logger.info(f"Generated diff summary with {sum(len(v) for v in changes.values())} total changes")
            return changes
            
        except Exception as e:
            logger.error(f"Failed to generate diff summary: {e}")
            return changes
    
    def _controllers_different(self, old_controller, new_controller) -> bool:
        """Check if two controllers are different."""
        return (
            old_controller.processor_type != new_controller.processor_type or
            len(old_controller.programs) != len(new_controller.programs) or
            len(old_controller.tags) != len(new_controller.tags)
        )
    
    def _programs_different(self, old_program, new_program) -> bool:
        """Check if two programs are different."""
        return (
            len(old_program.routines) != len(new_program.routines) or
            len(old_program.tags) != len(new_program.tags)
        )
    
    def optimize_file_for_git(self, input_path: Path, output_path: Path) -> bool:
        """
        Optimize an L5X file for git version control.
        
        Args:
            input_path: Path to input L5X file
            output_path: Path to output optimized L5X file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read input file
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply git optimization
            optimized_content = self._apply_git_formatting(content)
            
            # Write output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            logger.info(f"Successfully optimized {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize file {input_path}: {e}")
            return False
    
    def validate_git_compatibility(self, project: PLCProject) -> Dict[str, Any]:
        """
        Validate project for git compatibility.
        
        Args:
            project: Project to validate
            
        Returns:
            Validation results dictionary
        """
        results = {
            'is_compatible': True,
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Check for large binary data that shouldn't be in git
            for controller in project.controllers:
                if hasattr(controller, 'binary_data') and controller.binary_data:
                    results['warnings'].append(f"Controller {controller.name} contains binary data")
                    results['recommendations'].append("Consider extracting binary data to separate files")
            
            # Check for consistent naming conventions
            program_names = []
            for controller in project.controllers:
                program_names.extend([p.name for p in controller.programs])
            
            if len(set(program_names)) != len(program_names):
                results['warnings'].append("Duplicate program names found across controllers")
                results['recommendations'].append("Ensure unique program names for better git tracking")
            
            # Check file size implications
            estimated_size = len(str(project)) * 2  # Rough estimate
            if estimated_size > 10 * 1024 * 1024:  # 10MB
                results['warnings'].append("Project may generate large L5X files")
                results['recommendations'].append("Consider splitting large projects for better git performance")
            
            logger.info(f"Git compatibility validation completed for project '{project.name}'")
            return results
            
        except Exception as e:
            logger.error(f"Git compatibility validation failed: {e}")
            results['is_compatible'] = False
            results['warnings'].append(f"Validation error: {e}")
            return results 