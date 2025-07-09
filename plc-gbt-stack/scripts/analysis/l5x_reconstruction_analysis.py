#!/usr/bin/env python3
"""
L5X to ACD Reconstruction Analysis

This script analyzes whether L5X files can fully reconstruct their original ACD files
by examining data preservation, conversion completeness, and identifying limitations.

Following AI Task Orchestrator methodology for systematic analysis.
"""

import sys
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import struct

# Add project paths
sys.path.append('/Users/reh3376/repos/PLC_GPT/plc-gpt-stack')

class L5XReconstructionAnalyzer:
    """Analyzes L5X files to determine ACD reconstruction capability"""
    
    def __init__(self):
        self.analysis_results = {}
        self.validation_criteria = [
            "Data completeness assessment",
            "Structure preservation analysis", 
            "Metadata preservation check",
            "Content comparison validation",
            "Reconstruction feasibility evaluation"
        ]
        
    def analyze_file_sizes_and_complexity(self, acd_file: Path, l5x_files: List[Path]) -> Dict[str, Any]:
        """Analyze file sizes and estimate complexity difference"""
        print("📊 Analyzing File Sizes and Complexity")
        print("=" * 50)
        
        analysis = {
            "acd_analysis": {},
            "l5x_analysis": {},
            "size_comparison": {},
            "complexity_assessment": {}
        }
        
        # ACD file analysis
        if acd_file.exists():
            acd_size = acd_file.stat().st_size
            analysis["acd_analysis"] = {
                "file_path": str(acd_file),
                "size_bytes": acd_size,
                "size_mb": round(acd_size / (1024 * 1024), 2),
                "file_hash": self._calculate_file_hash(acd_file),
                "is_binary": self._is_binary_file(acd_file),
                "estimated_complexity": self._estimate_acd_complexity(acd_file)
            }
            print(f"📁 ACD File: {acd_file.name}")
            print(f"   Size: {analysis['acd_analysis']['size_mb']} MB")
            print(f"   Hash: {analysis['acd_analysis']['file_hash'][:16]}...")
            print(f"   Binary: {analysis['acd_analysis']['is_binary']}")
        else:
            print(f"❌ ACD file not found: {acd_file}")
            return analysis
        
        # L5X files analysis
        analysis["l5x_analysis"] = []
        total_l5x_size = 0
        
        for l5x_file in l5x_files:
            if l5x_file.exists():
                l5x_size = l5x_file.stat().st_size
                l5x_analysis = {
                    "file_path": str(l5x_file),
                    "size_bytes": l5x_size,
                    "size_kb": round(l5x_size / 1024, 2),
                    "file_hash": self._calculate_file_hash(l5x_file),
                    "xml_structure": self._analyze_xml_structure(l5x_file),
                    "content_density": self._calculate_content_density(l5x_file)
                }
                analysis["l5x_analysis"].append(l5x_analysis)
                total_l5x_size += l5x_size
                
                print(f"📄 L5X File: {l5x_file.name}")
                print(f"   Size: {l5x_analysis['size_kb']} KB")
                print(f"   Elements: {l5x_analysis['xml_structure']['total_elements']}")
                print(f"   Density: {l5x_analysis['content_density']:.2f}%")
        
        # Size comparison
        if total_l5x_size > 0:
            size_ratio = (total_l5x_size / acd_size) * 100
            analysis["size_comparison"] = {
                "acd_size_mb": analysis["acd_analysis"]["size_mb"],
                "total_l5x_size_kb": round(total_l5x_size / 1024, 2),
                "size_ratio_percent": round(size_ratio, 3),
                "compression_ratio": f"1:{round(acd_size / total_l5x_size, 0)}",
                "data_reduction": f"{100 - size_ratio:.2f}%"
            }
            
            print(f"\n📈 Size Comparison:")
            print(f"   ACD: {analysis['size_comparison']['acd_size_mb']} MB")
            print(f"   L5X Total: {analysis['size_comparison']['total_l5x_size_kb']} KB")
            print(f"   Ratio: {analysis['size_comparison']['size_ratio_percent']}%")
            print(f"   Data Reduction: {analysis['size_comparison']['data_reduction']}")
        
        return analysis
    
    def analyze_l5x_content_completeness(self, l5x_files: List[Path]) -> Dict[str, Any]:
        """Analyze L5X content to determine completeness"""
        print("\n🔍 Analyzing L5X Content Completeness")
        print("=" * 50)
        
        completeness_analysis = {
            "files_analyzed": [],
            "content_summary": {},
            "missing_components": [],
            "preservation_assessment": {}
        }
        
        for l5x_file in l5x_files:
            if not l5x_file.exists():
                continue
                
            print(f"\n📄 Analyzing: {l5x_file.name}")
            
            try:
                tree = ET.parse(l5x_file)
                root = tree.getroot()
                
                file_analysis = {
                    "file_name": l5x_file.name,
                    "xml_valid": True,
                    "components_found": self._extract_plc_components(root),
                    "metadata_preserved": self._check_metadata_preservation(root),
                    "logic_content": self._analyze_logic_content(root),
                    "data_structures": self._analyze_data_structures(root)
                }
                
                completeness_analysis["files_analyzed"].append(file_analysis)
                
                # Print component summary
                components = file_analysis["components_found"]
                print(f"   Controllers: {components['controllers']}")
                print(f"   Programs: {components['programs']}")
                print(f"   Routines: {components['routines']}")
                print(f"   Tags: {components['tags']}")
                print(f"   Data Types: {components['data_types']}")
                print(f"   I/O Modules: {components['modules']}")
                
                # Print logic analysis
                logic = file_analysis["logic_content"]
                print(f"   Logic Rungs: {logic['rungs']}")
                print(f"   Instructions: {logic['instructions']}")
                print(f"   Logic Density: {logic['density']}%")
                
            except ET.ParseError as e:
                print(f"   ❌ XML Parse Error: {e}")
                file_analysis = {
                    "file_name": l5x_file.name,
                    "xml_valid": False,
                    "parse_error": str(e)
                }
                completeness_analysis["files_analyzed"].append(file_analysis)
        
        # Assess overall preservation
        completeness_analysis["preservation_assessment"] = self._assess_data_preservation(
            completeness_analysis["files_analyzed"]
        )
        
        return completeness_analysis
    
    def compare_with_acd_expectations(self, acd_file: Path, l5x_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare L5X content with expected ACD complexity"""
        print("\n⚖️  Comparing with ACD Expectations")
        print("=" * 50)
        
        comparison = {
            "acd_expected_components": {},
            "l5x_actual_components": {},
            "coverage_analysis": {},
            "missing_elements": [],
            "reconstruction_feasibility": {}
        }
        
        # Estimate expected components from ACD size and complexity
        acd_size_mb = acd_file.stat().st_size / (1024 * 1024)
        
        # Industry standard estimates for PLC projects
        expected_components = self._estimate_expected_components(acd_size_mb)
        comparison["acd_expected_components"] = expected_components
        
        print(f"📊 Expected Components (based on {acd_size_mb:.1f} MB ACD):")
        for component, count in expected_components.items():
            print(f"   {component}: ~{count}")
        
        # Extract actual components from L5X analysis
        actual_components = self._aggregate_l5x_components(l5x_analysis["files_analyzed"])
        comparison["l5x_actual_components"] = actual_components
        
        print(f"\n📋 Actual L5X Components:")
        for component, count in actual_components.items():
            print(f"   {component}: {count}")
        
        # Calculate coverage
        coverage = {}
        missing_elements = []
        
        for component, expected in expected_components.items():
            actual = actual_components.get(component, 0)
            if expected > 0:
                coverage_percent = min((actual / expected) * 100, 100)
                coverage[component] = {
                    "expected": expected,
                    "actual": actual,
                    "coverage_percent": round(coverage_percent, 1),
                    "status": "adequate" if coverage_percent >= 80 else "insufficient"
                }
                
                if coverage_percent < 50:
                    missing_elements.append(f"{component}: {expected - actual} missing")
        
        comparison["coverage_analysis"] = coverage
        comparison["missing_elements"] = missing_elements
        
        print(f"\n📈 Coverage Analysis:")
        for component, analysis in coverage.items():
            status_icon = "✅" if analysis["status"] == "adequate" else "⚠️"
            print(f"   {status_icon} {component}: {analysis['coverage_percent']}% coverage")
        
        if missing_elements:
            print(f"\n❌ Missing Elements:")
            for missing in missing_elements:
                print(f"   • {missing}")
        
        return comparison
    
    def assess_reconstruction_feasibility(self, size_analysis: Dict[str, Any], 
                                        content_analysis: Dict[str, Any],
                                        comparison_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess feasibility of reconstructing ACD from L5X"""
        print("\n🎯 Assessing Reconstruction Feasibility")
        print("=" * 50)
        
        feasibility = {
            "overall_score": 0.0,
            "factors": {},
            "limitations": [],
            "recommendations": [],
            "reconstruction_possible": False
        }
        
        # Factor 1: Size ratio (weight: 30%)
        size_ratio = size_analysis["size_comparison"]["size_ratio_percent"]
        if size_ratio >= 80:
            size_score = 100
        elif size_ratio >= 50:
            size_score = 70
        elif size_ratio >= 20:
            size_score = 40
        else:
            size_score = 10
            
        feasibility["factors"]["size_preservation"] = {
            "score": size_score,
            "weight": 0.3,
            "analysis": f"L5X contains {size_ratio:.2f}% of ACD data"
        }
        
        # Factor 2: Component coverage (weight: 40%)
        coverage_scores = []
        for component, analysis in comparison_analysis["coverage_analysis"].items():
            coverage_scores.append(analysis["coverage_percent"])
        
        avg_coverage = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0
        component_score = min(avg_coverage, 100)
        
        feasibility["factors"]["component_coverage"] = {
            "score": component_score,
            "weight": 0.4,
            "analysis": f"Average component coverage: {avg_coverage:.1f}%"
        }
        
        # Factor 3: Logic preservation (weight: 30%)
        logic_scores = []
        for file_analysis in content_analysis["files_analyzed"]:
            if "logic_content" in file_analysis:
                logic_scores.append(file_analysis["logic_content"]["density"])
        
        avg_logic = sum(logic_scores) / len(logic_scores) if logic_scores else 0
        logic_score = min(avg_logic, 100)
        
        feasibility["factors"]["logic_preservation"] = {
            "score": logic_score,
            "weight": 0.3,
            "analysis": f"Average logic density: {avg_logic:.1f}%"
        }
        
        # Calculate overall score
        overall_score = (
            feasibility["factors"]["size_preservation"]["score"] * 0.3 +
            feasibility["factors"]["component_coverage"]["score"] * 0.4 +
            feasibility["factors"]["logic_preservation"]["score"] * 0.3
        )
        
        feasibility["overall_score"] = round(overall_score, 1)
        
        # Determine reconstruction possibility
        if overall_score >= 80:
            feasibility["reconstruction_possible"] = True
            feasibility["confidence"] = "High"
        elif overall_score >= 60:
            feasibility["reconstruction_possible"] = True
            feasibility["confidence"] = "Medium"
        elif overall_score >= 40:
            feasibility["reconstruction_possible"] = False
            feasibility["confidence"] = "Low"
        else:
            feasibility["reconstruction_possible"] = False
            feasibility["confidence"] = "Very Low"
        
        # Generate limitations and recommendations
        if size_ratio < 20:
            feasibility["limitations"].append("Significant data loss during conversion")
            feasibility["recommendations"].append("Implement enhanced ACD parsing to preserve more data")
        
        if avg_coverage < 70:
            feasibility["limitations"].append("Incomplete component extraction")
            feasibility["recommendations"].append("Improve L5X generation to include all PLC components")
        
        if avg_logic < 50:
            feasibility["limitations"].append("Minimal logic content preserved")
            feasibility["recommendations"].append("Enhance logic extraction from ACD binary format")
        
        # Print results
        print(f"Overall Reconstruction Score: {feasibility['overall_score']:.1f}/100")
        print(f"Reconstruction Possible: {'✅ Yes' if feasibility['reconstruction_possible'] else '❌ No'}")
        print(f"Confidence Level: {feasibility['confidence']}")
        
        print(f"\n📊 Factor Breakdown:")
        for factor, details in feasibility["factors"].items():
            print(f"   {factor}: {details['score']:.1f}/100 (weight: {details['weight']*100:.0f}%)")
            print(f"      {details['analysis']}")
        
        if feasibility["limitations"]:
            print(f"\n⚠️ Limitations:")
            for limitation in feasibility["limitations"]:
                print(f"   • {limitation}")
        
        if feasibility["recommendations"]:
            print(f"\n💡 Recommendations:")
            for recommendation in feasibility["recommendations"]:
                print(f"   • {recommendation}")
        
        return feasibility
    
    def generate_comprehensive_report(self, acd_file: Path, l5x_files: List[Path]) -> Dict[str, Any]:
        """Generate comprehensive reconstruction analysis report"""
        print("🔄 L5X to ACD Reconstruction Analysis")
        print("=" * 70)
        
        report = {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "acd_file": str(acd_file),
                "l5x_files": [str(f) for f in l5x_files],
                "analyzer_version": "1.0.0"
            },
            "size_analysis": {},
            "content_analysis": {},
            "comparison_analysis": {},
            "feasibility_assessment": {},
            "conclusions": {}
        }
        
        # Perform analyses
        report["size_analysis"] = self.analyze_file_sizes_and_complexity(acd_file, l5x_files)
        report["content_analysis"] = self.analyze_l5x_content_completeness(l5x_files)
        report["comparison_analysis"] = self.compare_with_acd_expectations(
            acd_file, report["content_analysis"]
        )
        report["feasibility_assessment"] = self.assess_reconstruction_feasibility(
            report["size_analysis"], 
            report["content_analysis"],
            report["comparison_analysis"]
        )
        
        # Generate conclusions
        report["conclusions"] = self._generate_conclusions(report)
        
        return report
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True
    
    def _estimate_acd_complexity(self, acd_file: Path) -> Dict[str, Any]:
        """Estimate ACD file complexity based on size and structure"""
        size_mb = acd_file.stat().st_size / (1024 * 1024)
        
        if size_mb < 1:
            complexity = "Simple"
            estimated_components = {"programs": 1-3, "routines": 5-15, "tags": 50-200}
        elif size_mb < 5:
            complexity = "Medium"
            estimated_components = {"programs": 3-8, "routines": 15-50, "tags": 200-1000}
        elif size_mb < 20:
            complexity = "Complex"
            estimated_components = {"programs": 8-20, "routines": 50-200, "tags": 1000-5000}
        else:
            complexity = "Very Complex"
            estimated_components = {"programs": 20, "routines": 200, "tags": 5000}
        
        return {
            "complexity_level": complexity,
            "estimated_components": estimated_components,
            "size_category": f"{size_mb:.1f} MB"
        }
    
    def _analyze_xml_structure(self, l5x_file: Path) -> Dict[str, Any]:
        """Analyze XML structure of L5X file"""
        try:
            tree = ET.parse(l5x_file)
            root = tree.getroot()
            
            def count_elements(element):
                count = 1
                for child in element:
                    count += count_elements(child)
                return count
            
            return {
                "root_tag": root.tag,
                "total_elements": count_elements(root),
                "top_level_children": len(list(root)),
                "has_controller": root.find('.//Controller') is not None,
                "schema_version": root.get('SchemaRevision', 'Unknown')
            }
        except:
            return {"error": "Failed to parse XML"}
    
    def _calculate_content_density(self, l5x_file: Path) -> float:
        """Calculate content density as percentage of meaningful content"""
        try:
            with open(l5x_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove XML formatting to get actual content
            import re
            content_only = re.sub(r'<[^>]+>', '', content)
            content_only = re.sub(r'\s+', ' ', content_only).strip()
            
            if len(content) > 0:
                return (len(content_only) / len(content)) * 100
            return 0.0
        except:
            return 0.0
    
    def _extract_plc_components(self, root: ET.Element) -> Dict[str, int]:
        """Extract and count PLC components from L5X"""
        return {
            "controllers": len(root.findall('.//Controller')),
            "programs": len(root.findall('.//Program')),
            "routines": len(root.findall('.//Routine')),
            "tags": len(root.findall('.//Tag')),
            "data_types": len(root.findall('.//DataType')),
            "modules": len(root.findall('.//Module')),
            "tasks": len(root.findall('.//Task')),
            "aois": len(root.findall('.//AddOnInstructionDefinition'))
        }
    
    def _check_metadata_preservation(self, root: ET.Element) -> Dict[str, Any]:
        """Check what metadata is preserved in L5X"""
        controller = root.find('.//Controller')
        if controller is None:
            return {"preserved": False}
        
        return {
            "preserved": True,
            "controller_name": controller.get('Name', ''),
            "processor_type": controller.get('ProcessorType', ''),
            "software_revision": root.get('SoftwareRevision', ''),
            "creation_date": controller.get('ProjectCreationDate', ''),
            "last_modified": controller.get('LastModifiedDate', '')
        }
    
    def _analyze_logic_content(self, root: ET.Element) -> Dict[str, Any]:
        """Analyze logic content in L5X"""
        rungs = root.findall('.//Rung')
        instructions = []
        
        for rung in rungs:
            text_elem = rung.find('Text')
            if text_elem is not None and text_elem.text:
                # Count instructions in rung
                text = text_elem.text
                if 'NOP()' not in text:  # Exclude empty rungs
                    instructions.extend(text.split())
        
        return {
            "rungs": len(rungs),
            "instructions": len(instructions),
            "density": (len(instructions) / max(len(rungs), 1)) * 10  # Scaled density
        }
    
    def _analyze_data_structures(self, root: ET.Element) -> Dict[str, Any]:
        """Analyze data structures in L5X"""
        return {
            "user_defined_types": len(root.findall('.//DataType[@Class="User"]')),
            "predefined_types": len(root.findall('.//DataType[@Class="Predefined"]')),
            "controller_tags": len(root.findall('.//Controller/Tags/Tag')),
            "program_tags": len(root.findall('.//Program/Tags/Tag'))
        }
    
    def _assess_data_preservation(self, files_analyzed: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall data preservation across all L5X files"""
        total_components = {}
        valid_files = [f for f in files_analyzed if f.get("xml_valid", False)]
        
        for file_analysis in valid_files:
            components = file_analysis.get("components_found", {})
            for component, count in components.items():
                total_components[component] = total_components.get(component, 0) + count
        
        return {
            "valid_files": len(valid_files),
            "total_files": len(files_analyzed),
            "aggregated_components": total_components,
            "preservation_quality": "High" if len(valid_files) == len(files_analyzed) else "Partial"
        }
    
    def _estimate_expected_components(self, acd_size_mb: float) -> Dict[str, int]:
        """Estimate expected components based on ACD file size"""
        # Industry estimates based on typical PLC project sizes
        base_multiplier = max(1, acd_size_mb / 2)  # Scale with file size
        
        return {
            "controllers": 1,
            "programs": max(1, int(2 * base_multiplier)),
            "routines": max(3, int(10 * base_multiplier)),
            "tags": max(20, int(100 * base_multiplier)),
            "data_types": max(5, int(15 * base_multiplier)),
            "modules": max(2, int(5 * base_multiplier)),
            "tasks": max(1, int(3 * base_multiplier)),
            "aois": max(0, int(2 * base_multiplier))
        }
    
    def _aggregate_l5x_components(self, files_analyzed: List[Dict[str, Any]]) -> Dict[str, int]:
        """Aggregate components across all L5X files"""
        total = {}
        for file_analysis in files_analyzed:
            if file_analysis.get("xml_valid", False):
                components = file_analysis.get("components_found", {})
                for component, count in components.items():
                    total[component] = total.get(component, 0) + count
        return total
    
    def _generate_conclusions(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final conclusions from analysis"""
        feasibility = report["feasibility_assessment"]
        size_analysis = report["size_analysis"]
        
        conclusions = {
            "can_reconstruct_acd": feasibility["reconstruction_possible"],
            "confidence_level": feasibility.get("confidence", "Unknown"),
            "primary_limitations": feasibility["limitations"],
            "key_findings": [],
            "recommendations": feasibility["recommendations"]
        }
        
        # Key findings
        size_ratio = size_analysis["size_comparison"]["size_ratio_percent"]
        conclusions["key_findings"].append(
            f"L5X files contain only {size_ratio:.2f}% of original ACD data"
        )
        
        if feasibility["overall_score"] < 50:
            conclusions["key_findings"].append(
                "Current L5X conversion is insufficient for full ACD reconstruction"
            )
        
        if size_ratio < 10:
            conclusions["key_findings"].append(
                "Massive data loss indicates L5X files are metadata-only representations"
            )
        
        return conclusions


def main():
    """Main analysis function"""
    print("🔄 L5X to ACD Reconstruction Analysis")
    print("Following AI Task Orchestrator methodology")
    print("=" * 70)
    
    # File paths
    acd_file = Path("/Users/reh3376/repos/plc-100/plc-acd/PLC100_Mashing.ACD")
    l5x_files = [
        Path("/Users/reh3376/Downloads/PLC100_Mashing.L5X"),
        Path("/Users/reh3376/Downloads/PLC100_Mashing_converted.L5X")
    ]
    
    # Verify files exist
    if not acd_file.exists():
        print(f"❌ ACD file not found: {acd_file}")
        return 1
    
    existing_l5x = [f for f in l5x_files if f.exists()]
    if not existing_l5x:
        print(f"❌ No L5X files found")
        return 1
    
    print(f"📁 Analyzing ACD: {acd_file.name}")
    print(f"📄 Analyzing L5X files: {[f.name for f in existing_l5x]}")
    
    # Perform analysis
    analyzer = L5XReconstructionAnalyzer()
    report = analyzer.generate_comprehensive_report(acd_file, existing_l5x)
    
    # Save report
    report_file = Path("l5x_reconstruction_analysis_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print final conclusions
    print(f"\n{'='*70}")
    print("🎯 FINAL CONCLUSIONS")
    print(f"{'='*70}")
    
    conclusions = report["conclusions"]
    
    print(f"Can Reconstruct ACD: {'✅ Yes' if conclusions['can_reconstruct_acd'] else '❌ No'}")
    print(f"Confidence Level: {conclusions['confidence_level']}")
    print(f"Overall Score: {report['feasibility_assessment']['overall_score']:.1f}/100")
    
    print(f"\n🔍 Key Findings:")
    for finding in conclusions["key_findings"]:
        print(f"   • {finding}")
    
    if conclusions["primary_limitations"]:
        print(f"\n⚠️ Primary Limitations:")
        for limitation in conclusions["primary_limitations"]:
            print(f"   • {limitation}")
    
    if conclusions["recommendations"]:
        print(f"\n💡 Recommendations:")
        for recommendation in conclusions["recommendations"]:
            print(f"   • {recommendation}")
    
    print(f"\n📊 Detailed report saved to: {report_file}")
    
    return 0 if conclusions["can_reconstruct_acd"] else 1


if __name__ == "__main__":
    sys.exit(main()) 