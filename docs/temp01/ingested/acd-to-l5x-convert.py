"""
ACD to L5X Converter

This utility converts Logix Designer .ACD files to .L5X format.
The .ACD format is the native binary Logix Designer project format, while .L5X 
is an XML-based export format that's human-readable and suitable for version control.

Usage:
    python acd_to_l5x_converter.py input_file.acd output_file.l5x [--overwrite] [--detailed]

Arguments:
    input_file.acd   - Path to the input .ACD file
    output_file.l5x  - Path where the .L5X file should be saved
    --overwrite      - Optional flag to overwrite existing output file
    --detailed       - Optional flag to include detailed information in L5X export

Examples:
    python acd_to_l5x_converter.py "C:\\Projects\\MyProject.ACD" "C:\\Projects\\MyProject.L5X"
    python acd_to_l5x_converter.py "project.acd" "project.l5x" --overwrite --detailed
"""

import asyncio
import os
import sys

from logix_designer_sdk import StdOutEventLogger
from logix_designer_sdk.logix_project import LogixProject


def validate_input_file(file_path: str) -> bool:
    """
    Validate that the input file exists and has .acd extension.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        True if valid, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' does not exist.")
        return False

    if not file_path.lower().endswith('.acd'):
        print(f"Error: Input file '{file_path}' is not a .ACD file.")
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
    if not file_path.lower().endswith('.l5x'):
        print(f"Error: Output file '{file_path}' must have .L5X extension.")
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


async def convert_acd_to_l5x(input_path: str, output_path: str, overwrite: bool = False, detailed: bool = False) -> bool:
    """
    Convert a .ACD file to .L5X format.
    
    Args:
        input_path: Path to the input .ACD file
        output_path: Path where the .L5X file should be saved
        overwrite: Whether to overwrite existing output file
        detailed: Whether to include detailed information in L5X export
        
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        print(f"Opening ACD file: {input_path}")

        # Open the ACD project
        project = await LogixProject.open_logix_project(input_path, StdOutEventLogger())

        print("Converting to L5X format...")
        if detailed:
            print("  Using detailed export mode (includes additional metadata)")

        # Save as L5X file
        # The third parameter (detailed_l5x) controls the level of detail in the L5X export
        await project.save_as(output_path, overwrite, detailed)

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
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print_usage()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Parse optional flags
    overwrite = False
    detailed = False

    for arg in sys.argv[3:]:
        if arg == "--overwrite":
            overwrite = True
        elif arg == "--detailed":
            detailed = True
        elif arg in ["-h", "--help", "help"]:
            print_usage()
            sys.exit(0)
        else:
            print(f"Error: Unknown argument '{arg}'")
            print_usage()
            sys.exit(1)

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
    success = await convert_acd_to_l5x(input_file, output_file, overwrite, detailed)

    if success:
        print("\n🎉 ACD to L5X conversion completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 ACD to L5X conversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
