#!/usr/bin/env python3
"""
Simple Task Workflow - Standalone Version

This version demonstrates the workflow without requiring the modular package imports.
Works with Python 3.9+
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for direct imports
sys.path.append(str(Path(__file__).parent.parent))

# Import the original monolithic orchestrator
from ai_task_orchestrator import get_task_guidance, validate_task_completion


def implement_solution(guidance: str) -> str:
    """
    Implement a solution based on the provided guidance.
    
    This is a demonstration function that creates a real L5X parser implementation.
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


def refine_implementation(code_content: str, issues: list) -> str:
    """
    Refine implementation based on validation issues.
    """
    # For this example, we'll just add better error handling
    refined_code = code_content

    # Add comprehensive error handling
    if "error handling" in str(issues).lower():
        refined_code = refined_code.replace(
            'def parse_l5x_tags(self, file_path: str)',
            '''def parse_l5x_tags(self, file_path: str)'''
        ).replace(
            'except ET.ParseError as e:',
            '''except ET.ParseError as e:
            logger.error(f"Invalid XML in L5X file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing L5X: {e}")
            raise'''
        )

    return refined_code


def run_simple_workflow_example():
    """
    Execute the complete simple task workflow example.
    """
    print("🚀 Simple Task Workflow Example (Standalone)")
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

    validation = validate_task_completion(code, requirements)
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
        validation2 = validate_task_completion(refined_code, requirements)
        print(f"New Validation Score: {validation2['overall_score']}%")
        print(f"Status: {validation2['overall_status']}")

    print("\n✨ Workflow completed!")

    # Generate example L5X file for testing
    example_l5x = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="32.02" TargetName="TestController" TargetType="Controller" ContainsContext="true" Owner="Test User" ExportDate="Mon Jan 18 2025 10:00:00" ExportOptions="References NoRawData L5KData DecoratedData Context Dependencies ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Target" Name="TestController">
<DataTypes>
    <DataType Name="MyUDT" Family="NoFamily" Class="User">
        <Members>
            <Member Name="Value" DataType="REAL" Dimension="0" Radix="Float" Hidden="false" ExternalAccess="Read/Write"/>
            <Member Name="Status" DataType="DINT" Dimension="0" Radix="Decimal" Hidden="false" ExternalAccess="Read/Write"/>
        </Members>
    </DataType>
</DataTypes>
<Tags>
    <Tag Name="TestTag1" TagType="Base" DataType="DINT" Radix="Decimal" Constant="false" ExternalAccess="Read/Write">
        <Data Format="L5K">
        <![CDATA[42]]>
        </Data>
    </Tag>
    <Tag Name="TestTag2" TagType="Base" DataType="REAL" Radix="Float" Constant="false" ExternalAccess="Read/Write">
        <Data Format="L5K">
        <![CDATA[3.14159]]>
        </Data>
    </Tag>
    <Tag Name="TestArray" TagType="Base" DataType="DINT" Dimensions="10" Radix="Decimal" Constant="false" ExternalAccess="Read/Write">
        <Description>
        <![CDATA[Test array of integers]]>
        </Description>
        <Data Format="L5K">
        <![CDATA[[0,1,2,3,4,5,6,7,8,9]]]>
        </Data>
    </Tag>
    <Tag Name="MyUDTTag" TagType="Base" DataType="MyUDT" Constant="false" ExternalAccess="Read/Write">
        <Data Format="L5K">
        <![CDATA[[100.5,1]]]>
        </Data>
    </Tag>
</Tags>
</Controller>
</RSLogix5000Content>'''

    # Save example L5X
    example_file = Path("example.L5X")
    with open(example_file, 'w') as f:
        f.write(example_l5x)
    print(f"\n📄 Created example L5X file: {example_file}")

    # Test the parser
    print("\n🧪 Testing the generated parser...")
    try:
        # Import and run the generated parser
        import subprocess
        result = subprocess.run([sys.executable, str(impl_file), str(example_file), "output.json"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Parser executed successfully!")
            print(result.stdout)

            # Show the output
            if Path("output.json").exists():
                with open("output.json") as f:
                    output_data = json.load(f)
                print(f"\n📊 Parsed {output_data['tag_count']} tags:")
                for tag in output_data['tags']:
                    print(f"  - {tag['name']} ({tag['data_type']})")
        else:
            print("❌ Parser failed:")
            print(result.stderr)
    except Exception as e:
        print(f"Error testing parser: {e}")

    # Clean up
    print("\n🧹 Cleaning up temporary files...")
    files_to_clean = [impl_file, example_file, Path("output.json")]
    refined_file = Path("l5x_parser_refined.py")
    if refined_file.exists():
        files_to_clean.append(refined_file)

    for file in files_to_clean:
        if file.exists():
            file.unlink()
            print(f"  - Removed {file}")


if __name__ == "__main__":
    run_simple_workflow_example()
