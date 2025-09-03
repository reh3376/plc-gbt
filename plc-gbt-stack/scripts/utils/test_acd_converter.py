#!/usr/bin/env python3
"""
Test script for ACD to L5X converter functionality
"""

import sys
from pathlib import Path

# Add the acd-l5x-tool-lib to Python path
sys.path.insert(0, '/Users/reh3376/repos/acd-l5x-tool-lib/src')

def test_converter_imports():
    """Test if we can import the converter components"""
    try:
        from plc_format_converter.core.converter import PLCConverter
        from plc_format_converter.formats.acd_handler import ACDHandler
        from plc_format_converter.formats.l5x_handler import L5XHandler
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_converter_capabilities():
    """Test converter capabilities"""
    try:
        from plc_format_converter.formats.acd_handler import ACDHandler
        from plc_format_converter.formats.l5x_handler import L5XHandler

        # Test ACD handler
        acd_handler = ACDHandler()
        acd_caps = acd_handler.get_capabilities()
        print(f"ACD Handler - Read: {acd_caps.get('read_support', False)}, Write: {acd_caps.get('write_support', False)}")

        # Test L5X handler
        l5x_handler = L5XHandler()
        l5x_caps = l5x_handler.get_capabilities()
        print(f"L5X Handler - Read: {l5x_caps.get('read_support', False)}, Write: {l5x_caps.get('write_support', False)}")

        return True
    except Exception as e:
        print(f"❌ Capability test failed: {e}")
        return False

def test_single_conversion():
    """Test conversion of a single ACD file"""
    try:
        from plc_format_converter.core.converter import PLCConverter

        # Test with plc-100 ACD file
        acd_file = Path("/Users/reh3376/repos/plc-100/plc-acd/PLC100_Mashing.ACD")
        test_l5x_file = Path("/tmp/test_conversion.L5X")

        if not acd_file.exists():
            print(f"❌ Test ACD file not found: {acd_file}")
            return False

        print(f"🔄 Testing conversion: {acd_file} -> {test_l5x_file}")

        # Initialize converter
        converter = PLCConverter()

        # Perform conversion
        result = converter.acd_to_l5x(acd_file, test_l5x_file)

        print(f"Conversion result: Success={result.success}, Status={result.status}")

        if test_l5x_file.exists():
            size = test_l5x_file.stat().st_size
            print(f"✅ Output file created: {size} bytes")

            # Clean up test file
            test_l5x_file.unlink()

            return result.success
        else:
            print("❌ Output file not created")
            return False

    except Exception as e:
        print(f"❌ Conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Testing ACD to L5X Converter")
    print("=" * 40)

    # Test 1: Imports
    print("\n1. Testing imports...")
    if not test_converter_imports():
        return 1

    # Test 2: Capabilities
    print("\n2. Testing capabilities...")
    if not test_converter_capabilities():
        return 1

    # Test 3: Single conversion
    print("\n3. Testing single conversion...")
    if not test_single_conversion():
        return 1

    print("\n✅ All tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
