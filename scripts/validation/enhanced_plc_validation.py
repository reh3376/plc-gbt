#!/usr/bin/env python3
"""
Enhanced PLC Validation Framework
Comprehensive integrity checking and data validation
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import xml.etree.ElementTree as ET

class EnhancedPLCValidator:
    """Enhanced validation framework for PLC files and conversions"""
    
    def __init__(self):
        self.validation_rules = {
            "l5x": {
                "required_elements": ["RSLogix5000Content", "Controller"],
                "min_file_size": 1024,
                "max_file_size": 100 * 1024 * 1024  # 100MB
            },
            "acd": {
                "min_file_size": 1024,
                "max_file_size": 50 * 1024 * 1024   # 50MB
            }
        }
    
    def validate_round_trip_conversion(self, original_file, converted_file, reconverted_file):
        """Validate ACD → L5X → ACD round-trip conversion"""
        validation_result = {
            "round_trip_validation": {
                "original": str(original_file),
                "converted": str(converted_file),
                "reconverted": str(reconverted_file),
                "integrity_score": 0.0,
                "data_preservation": {},
                "issues": []
            }
        }
        
        try:
            # Calculate file hashes for comparison
            original_hash = self._calculate_file_hash(original_file)
            reconverted_hash = self._calculate_file_hash(reconverted_file)
            
            # Compare file sizes
            original_size = original_file.stat().st_size
            reconverted_size = reconverted_file.stat().st_size
            size_difference = abs(original_size - reconverted_size) / original_size * 100
            
            validation_result["round_trip_validation"]["data_preservation"] = {
                "original_hash": original_hash,
                "reconverted_hash": reconverted_hash,
                "hash_match": original_hash == reconverted_hash,
                "original_size": original_size,
                "reconverted_size": reconverted_size,
                "size_difference_percent": size_difference
            }
            
            # Calculate integrity score
            integrity_score = 100.0
            if not validation_result["round_trip_validation"]["data_preservation"]["hash_match"]:
                integrity_score -= 50.0
                validation_result["round_trip_validation"]["issues"].append("File hash mismatch")
            
            if size_difference > 5.0:  # More than 5% size difference
                integrity_score -= 25.0
                validation_result["round_trip_validation"]["issues"].append(f"Significant size difference: {size_difference:.1f}%")
            
            validation_result["round_trip_validation"]["integrity_score"] = integrity_score
            
        except Exception as e:
            validation_result["round_trip_validation"]["issues"].append(f"Round-trip validation error: {e}")
            validation_result["round_trip_validation"]["integrity_score"] = 0.0
        
        return validation_result
    
    def validate_component_preservation(self, l5x_file):
        """Validate component preservation in L5X file"""
        component_validation = {
            "component_analysis": {
                "file": str(l5x_file),
                "components_found": {},
                "validation_score": 0.0,
                "issues": []
            }
        }
        
        try:
            tree = ET.parse(l5x_file)
            root = tree.getroot()
            
            # Count different component types
            components = {
                "programs": len(root.findall(".//Program")),
                "routines": len(root.findall(".//Routine")),
                "aois": len(root.findall(".//AddOnInstructionDefinition")),
                "udts": len(root.findall(".//DataType")),
                "tags": len(root.findall(".//Tag")),
                "devices": len(root.findall(".//Module"))
            }
            
            component_validation["component_analysis"]["components_found"] = components
            
            # Calculate validation score based on component presence
            score = 100.0
            if components["programs"] == 0:
                score -= 30.0
                component_validation["component_analysis"]["issues"].append("No programs found")
            
            if components["routines"] == 0:
                score -= 20.0
                component_validation["component_analysis"]["issues"].append("No routines found")
            
            if components["tags"] == 0:
                score -= 15.0
                component_validation["component_analysis"]["issues"].append("No tags found")
            
            component_validation["component_analysis"]["validation_score"] = max(0.0, score)
            
        except Exception as e:
            component_validation["component_analysis"]["issues"].append(f"Component analysis error: {e}")
            component_validation["component_analysis"]["validation_score"] = 0.0
        
        return component_validation
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

def main():
    """Main validation execution"""
    validator = EnhancedPLCValidator()
    
    print("🔍 Enhanced PLC Validation Framework")
    print("=" * 50)
    print("✅ Validation framework initialized")
    print("📋 Available validation methods:")
    print("   • Round-trip conversion validation")
    print("   • Component preservation analysis")
    print("   • Data integrity scoring")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
