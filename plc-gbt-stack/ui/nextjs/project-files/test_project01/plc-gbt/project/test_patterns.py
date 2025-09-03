#!/usr/bin/env python3
"""
Test script to verify regex patterns work correctly
"""

import re

# Test samples from the actual file
test_cases = [
    # tagGroup test
    '                                  "tagGroup": "Perspective Default",',

    # OPC path tests
    '                                  "opcItemPath": "ns\\u003d1;s\\u003d[WHK01_PLC400_Utility]Neutralization.SP_HMI[5]",',
    '                                  "opcItemPath": "ns\\u003d1;s\\u003d[WHK01_PLC300_Still]Temperature.PV",',
    '                                  "opcItemPath": "ns\\u003d1;s\\u003d[WHK01_PLC100_Mashing]Level.SP_HMI[10]",',
    '                                  "opcItemPath": "ns\\u003d1;s\\u003d[WHK01_PLC200_Fermenters]Pressure.PV_Raw",',
]

def test_patterns():
    """Test all replacement patterns."""

    print("🧪 Testing Replacement Patterns\n")

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case}")
        modified = test_case

        # Apply all patterns
        # 1. tagGroup pattern
        pattern1 = r'"tagGroup":\s*"Perspective Default"'
        replacement1 = '"tagGroup": "Default"'
        modified = re.sub(pattern1, replacement1, modified)

        # 2-5. PLC patterns
        patterns = [
            (r'"opcItemPath":\s*"([^"]*)\[WHK01_PLC400_Utility\]', r'"opcItemPath": "\1[plc400]'),
            (r'"opcItemPath":\s*"([^"]*)\[WHK01_PLC300_Still\]', r'"opcItemPath": "\1[plc300]'),
            (r'"opcItemPath":\s*"([^"]*)\[WHK01_PLC100_Mashing\]', r'"opcItemPath": "\1[plc100]'),
            (r'"opcItemPath":\s*"([^"]*)\[WHK01_PLC200_Fermenters\]', r'"opcItemPath": "\1[plc200]'),
        ]

        for pattern, replacement in patterns:
            modified = re.sub(pattern, replacement, modified)

        if modified != test_case:
            print(f"   ✅ Modified: {modified}")
        else:
            print("   ➡️  No change")
        print()

if __name__ == "__main__":
    test_patterns()
