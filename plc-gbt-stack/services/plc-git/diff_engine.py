"""
PLC-Aware Diff Engine - Phase 35.2.2
Intelligent diffing for L5X files understanding PLC structure
Following AI Task Orchestrator methodology
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple

from .models import (
    DataTypeDiff,
    DiffSummary,
    DiffType,
    PLCDiff,
    ProgramDiff,
    RoutineDiff,
    TagDiff,
)

logger = logging.getLogger(__name__)


class PLCDiffEngine:
    """
    PLC-aware diff engine that understands L5X structure
    Provides semantic diffing for ladder logic and control programs
    """
    
    def __init__(self):
        self.namespace = {'': 'http://www.rockwellautomation.com/schemas/2012/RSLogix5000'}
    
    async def generate_semantic_diff(
        self,
        original_l5x: str,
        modified_l5x: str
    ) -> PLCDiff:
        """
        Parse L5X structure for intelligent diffing
        
        Args:
            original_l5x: Original L5X content
            modified_l5x: Modified L5X content
            
        Returns:
            Semantic PLCDiff object
        """
        try:
            # Parse XML
            original_tree = ET.fromstring(original_l5x)
            modified_tree = ET.fromstring(modified_l5x)
            
            # Extract components
            original_routines = self._extract_routines(original_tree)
            modified_routines = self._extract_routines(modified_tree)
            
            original_tags = self._extract_tags(original_tree)
            modified_tags = self._extract_tags(modified_tree)
            
            original_datatypes = self._extract_datatypes(original_tree)
            modified_datatypes = self._extract_datatypes(modified_tree)
            
            original_programs = self._extract_programs(original_tree)
            modified_programs = self._extract_programs(modified_tree)
            
            # Calculate differences
            routine_diffs = self._diff_routines(original_routines, modified_routines)
            tag_diffs = self._diff_tags(original_tags, modified_tags)
            datatype_diffs = self._diff_datatypes(original_datatypes, modified_datatypes)
            program_diffs = self._diff_programs(original_programs, modified_programs)
            
            # Generate summary
            summary = self._generate_summary(
                routine_diffs,
                tag_diffs,
                datatype_diffs,
                program_diffs
            )
            
            return PLCDiff(
                file_a="original.l5x",
                file_b="modified.l5x",
                routines=routine_diffs,
                tags=tag_diffs,
                data_types=datatype_diffs,
                programs=program_diffs,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Failed to generate semantic diff: {str(e)}")
            # Return empty diff on error
            return PLCDiff(
                file_a="original.l5x",
                file_b="modified.l5x",
                routines=[],
                tags=[],
                data_types=[],
                programs=[],
                summary=DiffSummary(total_changes=0)
            )
    
    def format_diff_for_review(self, diff: PLCDiff) -> str:
        """
        Generate human-readable diff summary
        
        Args:
            diff: PLCDiff object
            
        Returns:
            Formatted diff summary string
        """
        lines = ["PLC Program Changes:", "=" * 50]
        
        # Routine changes
        if diff.routines:
            lines.append("\nRoutine Changes:")
            for routine in diff.routines:
                icon = self._get_diff_icon(routine.diff_type)
                lines.append(f"  {icon} {routine.name}")
                if routine.diff_type == DiffType.MODIFIED:
                    lines.append(f"      +{routine.line_changes_added} lines")
                    lines.append(f"      -{routine.line_changes_removed} lines")
        
        # Tag changes
        if diff.tags:
            lines.append("\nTag Changes:")
            for tag in diff.tags:
                icon = self._get_diff_icon(tag.diff_type)
                lines.append(f"  {icon} {tag.name} ({tag.data_type})")
                if tag.diff_type == DiffType.MODIFIED:
                    lines.append(f"      {tag.old_value} → {tag.new_value}")
        
        # Data type changes
        if diff.data_types:
            lines.append("\nData Type Changes:")
            for dt in diff.data_types:
                icon = self._get_diff_icon(dt.diff_type)
                lines.append(f"  {icon} {dt.name}")
                if dt.members_added:
                    lines.append(f"      + Members: {', '.join(dt.members_added)}")
                if dt.members_removed:
                    lines.append(f"      - Members: {', '.join(dt.members_removed)}")
        
        # Program changes
        if diff.programs:
            lines.append("\nProgram Changes:")
            for prog in diff.programs:
                icon = self._get_diff_icon(prog.diff_type)
                lines.append(f"  {icon} {prog.name}")
                if prog.routines_affected:
                    lines.append(f"      Routines: {', '.join(prog.routines_affected)}")
        
        # Summary
        lines.append("\nSummary:")
        lines.append(f"  Total Changes: {diff.summary.total_changes}")
        lines.append(f"  Routines: +{diff.summary.routines_added} "
                    f"~{diff.summary.routines_modified} "
                    f"-{diff.summary.routines_deleted}")
        lines.append(f"  Tags: +{diff.summary.tags_added} "
                    f"~{diff.summary.tags_modified} "
                    f"-{diff.summary.tags_deleted}")
        
        if diff.summary.has_safety_impact:
            lines.append("\n⚠️  WARNING: Changes may impact safety systems!")
        
        if diff.summary.requires_review:
            lines.append("\n🔍 Manual review required for these changes")
        
        return '\n'.join(lines)
    
    def _extract_routines(self, tree: ET.Element) -> Dict[str, Dict]:
        """Extract routines from L5X tree"""
        routines = {}
        
        # Find all routine elements
        for routine in tree.findall(".//Routine"):
            name = routine.get("Name", "Unknown")
            routine_type = routine.get("Type", "Unknown")
            
            # Extract routine content based on type
            content = ""
            if routine_type == "RLL":  # Ladder Logic
                rungs = routine.findall(".//Rung")
                content = f"{len(rungs)} rungs"
            elif routine_type == "ST":  # Structured Text
                text = routine.find(".//Text")
                if text is not None and text.text:
                    content = f"{len(text.text.splitlines())} lines"
            
            routines[name] = {
                "type": routine_type,
                "content": content,
                "element": routine
            }
        
        return routines
    
    def _extract_tags(self, tree: ET.Element) -> Dict[str, Dict]:
        """Extract tags from L5X tree"""
        tags = {}
        
        # Find all tag elements
        for tag in tree.findall(".//Tag"):
            name = tag.get("Name", "Unknown")
            data_type = tag.get("DataType", "Unknown")
            value = tag.get("Value", "")
            
            # Handle complex tag values
            if not value:
                data_element = tag.find(".//Data")
                if data_element is not None:
                    value = self._extract_tag_value(data_element)
            
            tags[name] = {
                "data_type": data_type,
                "value": value,
                "element": tag
            }
        
        return tags
    
    def _extract_datatypes(self, tree: ET.Element) -> Dict[str, Dict]:
        """Extract user-defined data types from L5X tree"""
        datatypes = {}
        
        for dt in tree.findall(".//DataType"):
            name = dt.get("Name", "Unknown")
            members = []
            
            for member in dt.findall(".//Member"):
                member_name = member.get("Name", "Unknown")
                member_type = member.get("DataType", "Unknown")
                members.append(f"{member_name}:{member_type}")
            
            datatypes[name] = {
                "members": members,
                "element": dt
            }
        
        return datatypes
    
    def _extract_programs(self, tree: ET.Element) -> Dict[str, Dict]:
        """Extract programs from L5X tree"""
        programs = {}
        
        for program in tree.findall(".//Program"):
            name = program.get("Name", "Unknown")
            
            # Extract routine names
            routines = []
            for routine in program.findall(".//Routine"):
                routines.append(routine.get("Name", "Unknown"))
            
            # Extract tag names
            tags = []
            for tag in program.findall(".//Tag"):
                tags.append(tag.get("Name", "Unknown"))
            
            programs[name] = {
                "routines": routines,
                "tags": tags,
                "element": program
            }
        
        return programs
    
    def _diff_routines(
        self,
        original: Dict[str, Dict],
        modified: Dict[str, Dict]
    ) -> List[RoutineDiff]:
        """Calculate routine differences"""
        diffs = []
        
        # Find added routines
        for name in set(modified.keys()) - set(original.keys()):
            diffs.append(RoutineDiff(
                name=name,
                diff_type=DiffType.ADDED,
                description=f"New {modified[name]['type']} routine"
            ))
        
        # Find deleted routines
        for name in set(original.keys()) - set(modified.keys()):
            diffs.append(RoutineDiff(
                name=name,
                diff_type=DiffType.DELETED,
                description=f"Removed {original[name]['type']} routine"
            ))
        
        # Find modified routines
        for name in set(original.keys()) & set(modified.keys()):
            if original[name]['content'] != modified[name]['content']:
                diffs.append(RoutineDiff(
                    name=name,
                    diff_type=DiffType.MODIFIED,
                    line_changes_added=10,  # TODO: Calculate actual changes
                    line_changes_removed=5,
                    description=f"Modified {original[name]['type']} routine"
                ))
        
        return diffs
    
    def _diff_tags(
        self,
        original: Dict[str, Dict],
        modified: Dict[str, Dict]
    ) -> List[TagDiff]:
        """Calculate tag differences"""
        diffs = []
        
        # Find added tags
        for name in set(modified.keys()) - set(original.keys()):
            diffs.append(TagDiff(
                name=name,
                diff_type=DiffType.ADDED,
                new_value=modified[name]['value'],
                data_type=modified[name]['data_type']
            ))
        
        # Find deleted tags
        for name in set(original.keys()) - set(modified.keys()):
            diffs.append(TagDiff(
                name=name,
                diff_type=DiffType.DELETED,
                old_value=original[name]['value'],
                data_type=original[name]['data_type']
            ))
        
        # Find modified tags
        for name in set(original.keys()) & set(modified.keys()):
            if original[name]['value'] != modified[name]['value']:
                diffs.append(TagDiff(
                    name=name,
                    diff_type=DiffType.MODIFIED,
                    old_value=original[name]['value'],
                    new_value=modified[name]['value'],
                    data_type=original[name]['data_type']
                ))
        
        return diffs
    
    def _diff_datatypes(
        self,
        original: Dict[str, Dict],
        modified: Dict[str, Dict]
    ) -> List[DataTypeDiff]:
        """Calculate data type differences"""
        diffs = []
        
        # Find added data types
        for name in set(modified.keys()) - set(original.keys()):
            diffs.append(DataTypeDiff(
                name=name,
                diff_type=DiffType.ADDED,
                members_added=modified[name]['members']
            ))
        
        # Find deleted data types
        for name in set(original.keys()) - set(modified.keys()):
            diffs.append(DataTypeDiff(
                name=name,
                diff_type=DiffType.DELETED,
                members_removed=original[name]['members']
            ))
        
        # Find modified data types
        for name in set(original.keys()) & set(modified.keys()):
            orig_members = set(original[name]['members'])
            mod_members = set(modified[name]['members'])
            
            added = list(mod_members - orig_members)
            removed = list(orig_members - mod_members)
            
            if added or removed:
                diffs.append(DataTypeDiff(
                    name=name,
                    diff_type=DiffType.MODIFIED,
                    members_added=added,
                    members_removed=removed
                ))
        
        return diffs
    
    def _diff_programs(
        self,
        original: Dict[str, Dict],
        modified: Dict[str, Dict]
    ) -> List[ProgramDiff]:
        """Calculate program differences"""
        diffs = []
        
        # Find added programs
        for name in set(modified.keys()) - set(original.keys()):
            diffs.append(ProgramDiff(
                name=name,
                diff_type=DiffType.ADDED,
                routines_affected=modified[name]['routines'],
                tags_affected=modified[name]['tags']
            ))
        
        # Find deleted programs
        for name in set(original.keys()) - set(modified.keys()):
            diffs.append(ProgramDiff(
                name=name,
                diff_type=DiffType.DELETED,
                routines_affected=original[name]['routines'],
                tags_affected=original[name]['tags']
            ))
        
        # Find modified programs
        for name in set(original.keys()) & set(modified.keys()):
            orig_routines = set(original[name]['routines'])
            mod_routines = set(modified[name]['routines'])
            
            orig_tags = set(original[name]['tags'])
            mod_tags = set(modified[name]['tags'])
            
            if orig_routines != mod_routines or orig_tags != mod_tags:
                diffs.append(ProgramDiff(
                    name=name,
                    diff_type=DiffType.MODIFIED,
                    routines_affected=list(mod_routines ^ orig_routines),
                    tags_affected=list(mod_tags ^ orig_tags)
                ))
        
        return diffs
    
    def _generate_summary(
        self,
        routine_diffs: List[RoutineDiff],
        tag_diffs: List[TagDiff],
        datatype_diffs: List[DataTypeDiff],
        program_diffs: List[ProgramDiff]
    ) -> DiffSummary:
        """Generate diff summary"""
        summary = DiffSummary(
            total_changes=len(routine_diffs) + len(tag_diffs) + 
                         len(datatype_diffs) + len(program_diffs)
        )
        
        # Count routine changes
        for diff in routine_diffs:
            if diff.diff_type == DiffType.ADDED:
                summary.routines_added += 1
            elif diff.diff_type == DiffType.MODIFIED:
                summary.routines_modified += 1
            elif diff.diff_type == DiffType.DELETED:
                summary.routines_deleted += 1
        
        # Count tag changes
        for diff in tag_diffs:
            if diff.diff_type == DiffType.ADDED:
                summary.tags_added += 1
            elif diff.diff_type == DiffType.MODIFIED:
                summary.tags_modified += 1
            elif diff.diff_type == DiffType.DELETED:
                summary.tags_deleted += 1
        
        # Check for safety impact
        safety_tags = ["E_Stop", "Safety", "Interlock", "Emergency"]
        for tag_diff in tag_diffs:
            if any(safety in tag_diff.name for safety in safety_tags):
                summary.has_safety_impact = True
                break
        
        # Require review for significant changes
        if (summary.total_changes > 10 or 
            summary.has_safety_impact or
            summary.routines_deleted > 0):
            summary.requires_review = True
        
        return summary
    
    def _extract_tag_value(self, data_element: ET.Element) -> str:
        """Extract tag value from Data element"""
        # Simple implementation - can be expanded for complex types
        if data_element.text:
            return data_element.text.strip()
        
        # Check for array values
        array_values = []
        for item in data_element.findall(".//Element"):
            if item.get("Value"):
                array_values.append(item.get("Value"))
        
        if array_values:
            return f"[{', '.join(array_values)}]"
        
        return ""
    
    def _get_diff_icon(self, diff_type: DiffType) -> str:
        """Get icon for diff type"""
        icons = {
            DiffType.ADDED: "+",
            DiffType.MODIFIED: "~",
            DiffType.DELETED: "-",
            DiffType.RENAMED: "→"
        }
        return icons.get(diff_type, "?")
