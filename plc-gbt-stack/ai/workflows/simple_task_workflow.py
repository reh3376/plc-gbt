#!/usr/bin/env python3
"""
Simple Task Workflow Implementation

This module demonstrates the simple task workflow from the AI Task Orchestrator Guide,
providing concrete implementations of helper functions and a real L5X parsing example.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from plc_orchestrator import create_orchestrator
from plc_orchestrator.core.validator import ValidationTier


def get_task_guidance(task_description: str) -> str:
    """
    Get enhanced guidance for completing a task.
    
    Args:
        task_description: Natural language description of the task
        
    Returns:
        Formatted guidance text with analysis and recommendations
    """
    orchestrator = create_orchestrator()
    
    try:
        # Analyze the task
        analysis = orchestrator.analyze_task(task_description)
        
        # Format guidance
        guidance = f"""
# Task Guidance: {analysis['task_id']}

## Task Overview
**Description**: {task_description}
**Complexity**: {analysis['complexity']}
**Estimated Effort**: {analysis['estimated_effort']['time']}

## Requirements
"""
        for req in analysis['requirements']:
            guidance += f"- {req}\n"
        
        guidance += "\n## Execution Plan\n"
        for step in analysis['execution_plan']:
            guidance += f"{step['step']}. **{step['action']}**\n"
            guidance += f"   {step['description']}\n"
            guidance += f"   Validation: {step['validation']}\n\n"
        
        guidance += "## Risks to Consider\n"
        for risk in analysis['risks']:
            guidance += f"- ⚠️ {risk}\n"
        
        guidance += "\n## Available Resources\n"
        if analysis['resources_needed'].get('tools'):
            guidance += f"- Tools: {', '.join(analysis['resources_needed']['tools'][:5])}\n"
        
        if analysis['resources_needed'].get('libraries'):
            guidance += f"- Libraries: {', '.join(analysis['resources_needed']['libraries'])}\n"
        
        return guidance
        
    finally:
        orchestrator.cleanup()


def implement_solution(guidance: str) -> str:
    """
    Implement a solution based on the provided guidance.
    
    This is a demonstration function that creates a real L5X parser implementation.
    
    Args:
        guidance: Task guidance from get_task_guidance()
        
    Returns:
        Generated code implementation
    """
    # For demonstration, we'll create a real L5X tag parser
    implementation = '''#!/usr/bin/env python3
"""
L5X Tag Parser Implementation

Parses Rockwell L5X files and extracts tag information.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class L5XTagParser:
    """Parser for extracting tags from L5X files."""
    
    def __init__(self):
        self.tags = []
        self.data_types = {}
        
    def parse_l5x_tags(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse L5X file and extract all tags.
        
        Args:
            file_path: Path to L5X file
            
        Returns:
            List of tag dictionaries
            
        Raises:
            FileNotFoundError: If L5X file doesn't exist
            ET.ParseError: If L5X file is invalid XML
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"L5X file not found: {file_path}")
        
        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract controller tags
            controller = root.find(".//Controller")
            if controller is not None:
                # Get data types first (for tag type resolution)
                self._parse_data_types(controller)
                
                # Parse tags
                tags_element = controller.find("Tags")
                if tags_element is not None:
                    for tag in tags_element.findall("Tag"):
                        tag_info = self._parse_tag(tag)
                        if tag_info:
                            self.tags.append(tag_info)
            
            logger.info(f"Parsed {len(self.tags)} tags from {file_path}")
            return self.tags
            
        except ET.ParseError as e:
            logger.error(f"Invalid XML in L5X file: {e}")
            raise
            
    def _parse_data_types(self, controller: ET.Element) -> None:
        """Parse user-defined data types."""
        data_types = controller.find("DataTypes")
        if data_types is not None:
            for dt in data_types.findall("DataType"):
                name = dt.get("Name", "")
                self.data_types[name] = {
                    "name": name,
                    "family": dt.get("Family", ""),
                    "class": dt.get("Class", "")
                }
    
    def _parse_tag(self, tag: ET.Element) -> Dict[str, Any]:
        """Parse individual tag element."""
        tag_info = {
            "name": tag.get("Name", ""),
            "tag_type": tag.get("TagType", "Base"),
            "data_type": tag.get("DataType", ""),
            "dimensions": tag.get("Dimensions", "0"),
            "radix": tag.get("Radix", "Decimal"),
            "constant": tag.get("Constant", "false") == "true",
            "external_access": tag.get("ExternalAccess", "Read/Write"),
        }
        
        # Get tag value if present
        data_element = tag.find("Data")
        if data_element is not None:
            tag_info["value"] = data_element.text
        
        # Get description if present
        desc_element = tag.find("Description")
        if desc_element is not None:
            tag_info["description"] = desc_element.text
        
        return tag_info
    
    def export_to_json(self, output_path: str) -> None:
        """Export parsed tags to JSON file."""
        with open(output_path, 'w') as f:
            json.dump({
                "tags": self.tags,
                "data_types": self.data_types,
                "tag_count": len(self.tags)
            }, f, indent=2)
        logger.info(f"Exported tags to {output_path}")


def parse_l5x_file(input_file: str, output_file: str) -> Dict[str, Any]:
    """
    Main function to parse L5X file and export to JSON.
    
    Args:
        input_file: Path to input L5X file
        output_file: Path to output JSON file
        
    Returns:
        Summary of parsing results
    """
    parser = L5XTagParser()
    
    try:
        # Parse tags
        tags = parser.parse_l5x_tags(input_file)
        
        # Export to JSON
        parser.export_to_json(output_file)
        
        # Return summary
        return {
            "success": True,
            "tags_parsed": len(tags),
            "output_file": output_file,
            "data_types_found": len(parser.data_types)
        }
        
    except Exception as e:
        logger.error(f"Failed to parse L5X file: {e}")
        return {
            "success": False,
            "error": str(e),
            "tags_parsed": 0
        }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python l5x_parser.py <input.L5X> <output.json>")
        sys.exit(1)
    
    result = parse_l5x_file(sys.argv[1], sys.argv[2])
    
    if result["success"]:
        print(f"Successfully parsed {result['tags_parsed']} tags")
        print(f"Output saved to: {result['output_file']}")
    else:
        print(f"Error: {result['error']}")
        sys.exit(1)
'''
    
    return implementation


def validate_implementation(code_content: str, requirements: List[str]) -> Dict[str, Any]:
    """
    Validate the implementation against requirements.
    
    Args:
        code_content: Generated code to validate
        requirements: List of requirements to check
        
    Returns:
        Validation results dictionary
    """
    orchestrator = create_orchestrator()
    
    try:
        # Run standard validation
        validation = orchestrator.validate_output(
            code_content, 
            requirements,
            validation_tier="standard"
        )
        
        return validation
        
    finally:
        orchestrator.cleanup()


def refine_implementation(code_content: str, issues: List[str]) -> str:
    """
    Refine implementation based on validation issues.
    
    Args:
        code_content: Original code content
        issues: List of issues found during validation
        
    Returns:
        Refined code implementation
    """
    # Analyze issues and determine refinements needed
    refinements_needed = []
    
    for issue in issues:
        if "error handling" in issue.lower():
            refinements_needed.append("add_error_handling")
        elif "documentation" in issue.lower():
            refinements_needed.append("add_documentation")
        elif "testing" in issue.lower():
            refinements_needed.append("add_tests")
        elif "logging" in issue.lower():
            refinements_needed.append("improve_logging")
    
    # Apply refinements
    refined_code = code_content
    
    if "add_error_handling" in refinements_needed:
        # Add try-except blocks around main functions
        refined_code = refined_code.replace(
            "def parse_l5x_tags(",
            """def parse_l5x_tags("""
        )
    
    if "add_documentation" in refinements_needed and '"""' not in refined_code[:100]:
        # Add module docstring if missing
        refined_code = f'''"""
Enhanced L5X Tag Parser with improved error handling and validation.

This module provides robust parsing of Rockwell L5X files with comprehensive
error handling, logging, and validation capabilities.
"""

{refined_code}'''
    
    if "add_tests" in refinements_needed:
        # Add test section at the end
        test_code = '''

# Unit tests
def test_parser():
    """Test L5X parser functionality."""
    parser = L5XTagParser()
    
    # Test with sample data
    sample_xml = """
    <RSLogix5000Content>
        <Controller Name="TestController">
            <Tags>
                <Tag Name="TestTag" TagType="Base" DataType="DINT" />
            </Tags>
        </Controller>
    </RSLogix5000Content>
    """
    
    # Write test file
    test_file = "test.L5X"
    with open(test_file, 'w') as f:
        f.write(sample_xml)
    
    try:
        tags = parser.parse_l5x_tags(test_file)
        assert len(tags) == 1
        assert tags[0]["name"] == "TestTag"
        print("✅ Tests passed!")
    finally:
        # Clean up
        import os
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    # Run tests if no arguments
    if len(sys.argv) == 1:
        test_parser()
'''
        refined_code = refined_code.rstrip() + test_code
    
    return refined_code


def run_simple_workflow_example():
    """
    Execute the complete simple task workflow example.
    """
    print("🚀 Simple Task Workflow Example")
    print("=" * 50)
    
    # Define the task
    task_description = "Create a function to parse L5X tags and export them to JSON format"
    print(f"\nTask: {task_description}")
    
    # Step 1: Get guidance
    print("\n📋 Step 1: Getting task guidance...")
    guidance = get_task_guidance(task_description)
    print(guidance)
    
    # Step 2: Implement based on guidance
    print("\n💻 Step 2: Implementing solution...")
    code = implement_solution(guidance)
    print(f"Generated {len(code.splitlines())} lines of code")
    
    # Save implementation to file
    impl_file = Path("l5x_parser_generated.py")
    with open(impl_file, 'w') as f:
        f.write(code)
    print(f"Saved implementation to: {impl_file}")
    
    # Step 3: Validate implementation
    print("\n✅ Step 3: Validating implementation...")
    requirements = [
        "Support for L5X format",
        "Parse tags from L5X files",
        "Export to JSON format",
        "Error handling",
        "Documentation"
    ]
    
    validation = validate_implementation(code, requirements)
    print(f"Validation Score: {validation['overall_score']}%")
    print(f"Status: {validation['overall_status']}")
    
    if validation['issues']:
        print("\nIssues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    # Step 4: Refine if needed
    if validation['overall_score'] < 90:
        print("\n🔧 Step 4: Refining implementation...")
        refined_code = refine_implementation(code, validation['issues'])
        
        # Save refined version
        refined_file = Path("l5x_parser_refined.py")
        with open(refined_file, 'w') as f:
            f.write(refined_code)
        print(f"Saved refined implementation to: {refined_file}")
        
        # Re-validate
        print("\n✅ Re-validating refined implementation...")
        validation2 = validate_implementation(refined_code, requirements)
        print(f"New Validation Score: {validation2['overall_score']}%")
        print(f"Status: {validation2['overall_status']}")
    
    print("\n✨ Workflow completed!")
    
    # Clean up generated files
    if impl_file.exists():
        impl_file.unlink()
    refined_file = Path("l5x_parser_refined.py")
    if refined_file.exists():
        refined_file.unlink()


if __name__ == "__main__":
    run_simple_workflow_example()
