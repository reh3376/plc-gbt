"""
L5X to ACD Converter

This utility converts Logix Designer .L5X files to .ACD format.
The .L5X format is an XML-based export format, while .ACD is the native
Logix Designer project format.

Usage:
    python l5x_to_acd_converter.py input_file.l5x output_file.acd [--overwrite]

Arguments:
    input_file.l5x   - Path to the input .L5X file
    output_file.acd  - Path where the .ACD file should be saved
    --overwrite      - Optional flag to overwrite existing output file

Examples:
    python l5x_to_acd_converter.py "C:\\Projects\\MyProject.L5X" "C:\\Projects\\MyProject.ACD"
    python l5x_to_acd_converter.py "project.l5x" "project.acd" --overwrite
"""

import asyncio
import os
import sys

from logix_designer_sdk import StdOutEventLogger
from logix_designer_sdk.logix_project import LogixProject


def validate_input_file(file_path: str) -> bool:
    """
    Validate that the input file exists and has .l5x extension.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        True if valid, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' does not exist.")
        return False

    if not file_path.lower().endswith('.l5x'):
        print(f"Error: Input file '{file_path}' is not a .L5X file.")
        return False

    return True


def validate_output_file(file_path: str, overwrite: bool = False) -> bool:
    """
    Validate the output file path and handle overwrite logic.
    
    Args:
        file_path: Path where the output file should be saved
        overwrite: Whether to overwrite existing files
        
    Returns:
        True if valid, False otherwise
    """
    if not file_path.lower().endswith('.acd'):
        print(f"Error: Output file '{file_path}' must have .ACD extension.")
        return False

    if os.path.exists(file_path) and not overwrite:
        print(f"Error: Output file '{file_path}' already exists.")
        print("Use --overwrite flag to overwrite existing files.")
        return False

    # Check if the output directory exists
    output_dir = os.path.dirname(file_path)
    if output_dir and not os.path.exists(output_dir):
        print(f"Error: Output directory '{output_dir}' does not exist.")
        return False

    return True


async def convert_l5x_to_acd(input_path: str, output_path: str, overwrite: bool = False) -> bool:
    """
    Convert a .L5X file to .ACD format.
    
    Args:
        input_path: Path to the input .L5X file
        output_path: Path where the .ACD file should be saved
        overwrite: Whether to overwrite existing output file
        
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        print(f"Opening L5X file: {input_path}")

        # Open the L5X project
        project = await LogixProject.open_logix_project(input_path, StdOutEventLogger())

        print("Converting to ACD format...")

        # Save as ACD file
        # The third parameter (detailed_l5x) is not relevant for ACD output
        await project.save_as(output_path, overwrite, False)

        # Close the project
        project.close()

        print("✅ Conversion successful!")
        print(f"   Input:  {input_path}")
        print(f"   Output: {output_path}")

        # Display file sizes for reference
        input_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        print(f"   Input size:  {input_size:,} bytes")
        print(f"   Output size: {output_size:,} bytes")

        return True

    except Exception as e:
        print(f"❌ Conversion failed: {str(e)}")
        return False


def print_usage():
    """Print usage information."""
    print(__doc__)


async def main():
    """Main function."""
    # Parse command line arguments
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print_usage()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    overwrite = len(sys.argv) == 4 and sys.argv[3] == "--overwrite"

    # Handle help requests
    if input_file in ["-h", "--help", "help"]:
        print_usage()
        sys.exit(0)

    # Validate inputs
    if not validate_input_file(input_file):
        sys.exit(1)

    if not validate_output_file(output_file, overwrite):
        sys.exit(1)

    # Perform conversion
    success = await convert_l5x_to_acd(input_file, output_file, overwrite)

    if success:
        print("\n🎉 L5X to ACD conversion completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 L5X to ACD conversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
