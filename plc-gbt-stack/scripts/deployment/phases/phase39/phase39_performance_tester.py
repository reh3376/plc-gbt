#!/usr/bin/env python3
"""
Phase 3.9 Performance Tester
============================

Performance testing script that measures data preservation with the enhanced
converter and validates against the 95%+ target using real ACD files.

Following AI Task Orchestrator methodology for comprehensive performance evaluation.
"""

import os
import sys
import json
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "plc-gpt-stack"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase39_performance_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import enhanced converter components
try:
    sys.path.insert(0, str(project_root / "plc-gpt-stack" / "plc-format-converter" / "src"))
    from plc_format_converter.core.converter import EnhancedPLCConverter
    from plc_format_converter.core.models import (
        ConversionResult, ConversionStatus, DataIntegrityScore, DataPreservationLevel
    )
    from plc_format_converter.utils.validation import DataIntegrityValidator, RoundTripValidator
    ENHANCED_CONVERTER_AVAILABLE = True
    logger.info("Enhanced converter components imported successfully")
except ImportError as e:
    logger.error(f"Enhanced converter not available: {e}")
    ENHANCED_CONVERTER_AVAILABLE = False


class Phase39PerformanceTester:
    """
    Performance tester for Phase 3.9 enhanced converter
    
    Tests data preservation performance against the 95%+ target using
    real ACD files from all 6 PLC repositories.
    """
    
    def __init__(self):
        """Initialize performance tester"""
        self.repo_base = Path("/Users/reh3376/repos")
        self.test_repos = ["plc-100", "plc-200", "plc-300", "plc-400", "plc-500", "plc-600"]
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize enhanced converter if available
        if ENHANCED_CONVERTER_AVAILABLE:
            self.converter = EnhancedPLCConverter(
                enable_studio5000=False,  # Disable for testing
                enable_git_optimization=True
            )
            self.validator = DataIntegrityValidator()
        else:
            self.converter = None
            self.validator = None
        
        # Performance results
        self.performance_results = {
            'timestamp': datetime.now().isoformat(),
            'phase': '3.9',
            'test_type': 'performance_evaluation',
            'target_preservation': '95%+',
            'converter_available': ENHANCED_CONVERTER_AVAILABLE,
            'test_results': [],
            'performance_metrics': {},
            'preservation_analysis': {},
            'target_validation': {},
            'recommendations': []
        }
        
        logger.info("Phase 3.9 Performance Tester initialized")
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive performance tests across all ACD files
        
        Returns:
            Dict with complete performance results
        """
        logger.info("🚀 Starting Phase 3.9 Performance Testing")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # Step 1: Validate converter availability
            if not ENHANCED_CONVERTER_AVAILABLE or not self.converter:
                logger.error("Enhanced converter not available - cannot run performance tests")
                return self._generate_failure_report("Enhanced converter not available")
            
            # Step 2: Discover ACD files
            logger.info("Step 1: Discovering ACD files for testing...")
            acd_files = self._discover_acd_files()
            
            if not acd_files:
                logger.error("No ACD files found for performance testing")
                return self._generate_failure_report("No ACD files found")
            
            # Step 3: Run performance tests on each ACD file
            logger.info("Step 2: Running performance tests on all ACD files...")
            test_results = self._run_conversion_tests(acd_files)
            
            # Step 4: Analyze performance metrics
            logger.info("Step 3: Analyzing performance metrics...")
            performance_metrics = self._analyze_performance_metrics(test_results)
            
            # Step 5: Analyze data preservation
            logger.info("Step 4: Analyzing data preservation performance...")
            preservation_analysis = self._analyze_preservation_performance(test_results)
            
            # Step 6: Validate against 95%+ target
            logger.info("Step 5: Validating against 95%+ preservation target...")
            target_validation = self._validate_preservation_target(preservation_analysis)
            
            # Step 7: Generate recommendations
            logger.info("Step 6: Generating performance recommendations...")
            recommendations = self._generate_performance_recommendations(
                performance_metrics, preservation_analysis, target_validation
            )
            
            # Compile final results
            total_time = time.time() - start_time
            
            self.performance_results.update({
                'test_duration': total_time,
                'acd_files_tested': len(acd_files),
                'test_results': test_results,
                'performance_metrics': performance_metrics,
                'preservation_analysis': preservation_analysis,
                'target_validation': target_validation,
                'recommendations': recommendations,
                'overall_success': target_validation.get('meets_target', False)
            })
            
            # Generate performance report
            self._generate_performance_report()
            
            logger.info(f"✅ Phase 3.9 Performance Testing completed in {total_time:.2f}s")
            
            return self.performance_results
            
        except Exception as e:
            logger.error(f"Performance testing failed: {e}")
            return self._generate_failure_report(f"Testing error: {e}")
    
    def _discover_acd_files(self) -> List[Dict[str, Any]]:
        """Discover ACD files for performance testing"""
        
        acd_files = []
        
        for repo in self.test_repos:
            repo_path = self.repo_base / repo
            acd_dir = repo_path / "plc-acd"
            
            if not acd_dir.exists():
                logger.warning(f"⚠️  ACD directory not found: {acd_dir}")
                continue
            
            for acd_file in acd_dir.glob("*.ACD"):
                file_info = {
                    'repository': repo,
                    'file_path': acd_file,
                    'file_name': acd_file.name,
                    'file_size': acd_file.stat().st_size,
                    'file_hash': self._calculate_file_hash(acd_file),
                    'last_modified': datetime.fromtimestamp(acd_file.stat().st_mtime)
                }
                
                acd_files.append(file_info)
                
                size_mb = file_info['file_size'] / (1024 * 1024)
                logger.info(f"📁 Testing: {repo}/{acd_file.name} ({size_mb:.2f} MB)")
        
        logger.info(f"📊 Total ACD files for testing: {len(acd_files)}")
        
        return acd_files
    
    def _run_conversion_tests(self, acd_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run conversion tests on all ACD files"""
        
        test_results = []
        
        for i, acd_info in enumerate(acd_files, 1):
            logger.info(f"🔄 Testing conversion {i}/{len(acd_files)}: {acd_info['repository']}")
            
            try:
                # Create output directory
                output_dir = self.results_dir / acd_info['repository']
                output_dir.mkdir(exist_ok=True)
                
                output_file = output_dir / f"{acd_info['file_path'].stem}_enhanced.L5X"
                
                # Perform enhanced conversion with timing
                start_time = time.time()
                
                conversion_result = self.converter.acd_to_l5x(
                    acd_file=acd_info['file_path'],
                    l5x_file=output_file,
                    validate_round_trip=True
                )
                
                conversion_time = time.time() - start_time
                
                # Analyze the conversion result
                test_result = {
                    'repository': acd_info['repository'],
                    'source_file': str(acd_info['file_path']),
                    'output_file': str(output_file),
                    'conversion_time': conversion_time,
                    'success': conversion_result.success,
                    'status': conversion_result.status.value if hasattr(conversion_result.status, 'value') else str(conversion_result.status),
                    'source_size': acd_info['file_size'],
                    'output_size': output_file.stat().st_size if output_file.exists() else 0,
                    'size_ratio': 0.0,
                    'throughput_mb_per_sec': 0.0,
                    'data_integrity': None,
                    'preservation_score': 0.0,
                    'preservation_level': 'metadata_only',
                    'issues': conversion_result.issues,
                    'warnings': conversion_result.warnings,
                    'round_trip_validated': conversion_result.round_trip_validated,
                    'git_optimized': conversion_result.git_optimized
                }
                
                # Calculate performance metrics
                if test_result['source_size'] > 0:
                    test_result['size_ratio'] = test_result['output_size'] / test_result['source_size']
                
                if conversion_time > 0:
                    source_mb = test_result['source_size'] / (1024 * 1024)
                    test_result['throughput_mb_per_sec'] = source_mb / conversion_time
                
                # Extract data integrity information
                if conversion_result.data_integrity:
                    test_result['data_integrity'] = conversion_result.data_integrity.to_dict() if hasattr(conversion_result.data_integrity, 'to_dict') else {
                        'overall_score': conversion_result.data_integrity.overall_score,
                        'preservation_level': conversion_result.data_integrity.preservation_level.value,
                        'logic_preservation': conversion_result.data_integrity.logic_preservation,
                        'tag_preservation': conversion_result.data_integrity.tag_preservation,
                        'io_preservation': conversion_result.data_integrity.io_preservation,
                        'motion_preservation': conversion_result.data_integrity.motion_preservation,
                        'safety_preservation': conversion_result.data_integrity.safety_preservation
                    }
                    
                    test_result['preservation_score'] = conversion_result.data_integrity.overall_score
                    test_result['preservation_level'] = conversion_result.data_integrity.preservation_level.value
                
                # Log test results
                if conversion_result.success:
                    logger.info(f"   ✅ Success: {test_result['preservation_score']:.1f}% preservation in {conversion_time:.2f}s")
                else:
                    logger.warning(f"   ❌ Failed: {conversion_result.status}")
                
                test_results.append(test_result)
                
            except Exception as e:
                logger.error(f"   ❌ Test failed: {e}")
                
                error_result = {
                    'repository': acd_info['repository'],
                    'source_file': str(acd_info['file_path']),
                    'success': False,
                    'status': 'test_error',
                    'error': str(e),
                    'conversion_time': 0.0,
                    'preservation_score': 0.0
                }
                
                test_results.append(error_result)
        
        return test_results
    
    def _analyze_performance_metrics(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversion performance metrics"""
        
        metrics = {
            'total_tests': len(test_results),
            'successful_tests': 0,
            'failed_tests': 0,
            'average_conversion_time': 0.0,
            'total_processing_time': 0.0,
            'average_throughput': 0.0,
            'throughput_range': {'min': float('inf'), 'max': 0.0},
            'size_analysis': {
                'average_size_ratio': 0.0,
                'total_source_mb': 0.0,
                'total_output_mb': 0.0
            },
            'performance_distribution': {
                'fast': 0,      # < 5 seconds
                'normal': 0,    # 5-30 seconds
                'slow': 0       # > 30 seconds
            }
        }
        
        conversion_times = []
        throughputs = []
        size_ratios = []
        total_source_size = 0
        total_output_size = 0
        
        for result in test_results:
            if result.get('success', False):
                metrics['successful_tests'] += 1
                
                # Conversion time analysis
                conv_time = result.get('conversion_time', 0.0)
                if conv_time > 0:
                    conversion_times.append(conv_time)
                    
                    # Performance categorization
                    if conv_time < 5:
                        metrics['performance_distribution']['fast'] += 1
                    elif conv_time <= 30:
                        metrics['performance_distribution']['normal'] += 1
                    else:
                        metrics['performance_distribution']['slow'] += 1
                
                # Throughput analysis
                throughput = result.get('throughput_mb_per_sec', 0.0)
                if throughput > 0:
                    throughputs.append(throughput)
                    
                    # Update throughput range
                    metrics['throughput_range']['min'] = min(metrics['throughput_range']['min'], throughput)
                    metrics['throughput_range']['max'] = max(metrics['throughput_range']['max'], throughput)
                
                # Size analysis
                size_ratio = result.get('size_ratio', 0.0)
                if size_ratio > 0:
                    size_ratios.append(size_ratio)
                
                total_source_size += result.get('source_size', 0)
                total_output_size += result.get('output_size', 0)
            else:
                metrics['failed_tests'] += 1
        
        # Calculate averages
        if conversion_times:
            metrics['average_conversion_time'] = sum(conversion_times) / len(conversion_times)
            metrics['total_processing_time'] = sum(conversion_times)
        
        if throughputs:
            metrics['average_throughput'] = sum(throughputs) / len(throughputs)
        
        if size_ratios:
            metrics['size_analysis']['average_size_ratio'] = sum(size_ratios) / len(size_ratios)
        
        metrics['size_analysis']['total_source_mb'] = total_source_size / (1024 * 1024)
        metrics['size_analysis']['total_output_mb'] = total_output_size / (1024 * 1024)
        
        # Fix throughput range if no valid throughputs
        if metrics['throughput_range']['min'] == float('inf'):
            metrics['throughput_range']['min'] = 0.0
        
        # Log performance summary
        logger.info("📊 Performance Metrics Summary:")
        logger.info(f"   Successful Tests: {metrics['successful_tests']}/{metrics['total_tests']}")
        logger.info(f"   Average Conversion Time: {metrics['average_conversion_time']:.2f}s")
        logger.info(f"   Average Throughput: {metrics['average_throughput']:.2f} MB/s")
        
        return metrics
    
    def _analyze_preservation_performance(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze data preservation performance"""
        
        analysis = {
            'total_tests': len(test_results),
            'successful_tests': 0,
            'preservation_scores': [],
            'average_preservation': 0.0,
            'preservation_range': {'min': 100.0, 'max': 0.0},
            'preservation_distribution': {
                'industry_standard': 0,  # 95%+
                'comprehensive': 0,      # 80-95%
                'partial_logic': 0,      # 50-80%
                'basic_structure': 0,    # 20-50%
                'metadata_only': 0       # 0-20%
            },
            'component_preservation': {
                'logic_avg': 0.0,
                'tags_avg': 0.0,
                'io_avg': 0.0,
                'motion_avg': 0.0,
                'safety_avg': 0.0
            },
            'baseline_comparison': {
                'baseline_preservation': 0.13,
                'improvement_factor': 0.0,
                'improvement_achieved': False
            }
        }
        
        preservation_scores = []
        component_scores = {
            'logic': [],
            'tags': [],
            'io': [],
            'motion': [],
            'safety': []
        }
        
        for result in test_results:
            if result.get('success', False):
                analysis['successful_tests'] += 1
                
                # Overall preservation score
                preservation = result.get('preservation_score', 0.0)
                preservation_scores.append(preservation)
                
                # Update preservation range
                analysis['preservation_range']['min'] = min(analysis['preservation_range']['min'], preservation)
                analysis['preservation_range']['max'] = max(analysis['preservation_range']['max'], preservation)
                
                # Categorize preservation level
                if preservation >= 95:
                    analysis['preservation_distribution']['industry_standard'] += 1
                elif preservation >= 80:
                    analysis['preservation_distribution']['comprehensive'] += 1
                elif preservation >= 50:
                    analysis['preservation_distribution']['partial_logic'] += 1
                elif preservation >= 20:
                    analysis['preservation_distribution']['basic_structure'] += 1
                else:
                    analysis['preservation_distribution']['metadata_only'] += 1
                
                # Component-level preservation
                if result.get('data_integrity'):
                    integrity = result['data_integrity']
                    component_scores['logic'].append(integrity.get('logic_preservation', 0.0))
                    component_scores['tags'].append(integrity.get('tag_preservation', 0.0))
                    component_scores['io'].append(integrity.get('io_preservation', 0.0))
                    component_scores['motion'].append(integrity.get('motion_preservation', 0.0))
                    component_scores['safety'].append(integrity.get('safety_preservation', 0.0))
        
        # Calculate averages
        if preservation_scores:
            analysis['average_preservation'] = sum(preservation_scores) / len(preservation_scores)
            analysis['preservation_scores'] = preservation_scores
        
        # Component averages
        for component, scores in component_scores.items():
            if scores:
                analysis['component_preservation'][f'{component}_avg'] = sum(scores) / len(scores)
        
        # Baseline comparison
        if analysis['average_preservation'] > 0:
            analysis['baseline_comparison']['improvement_factor'] = (
                analysis['average_preservation'] / analysis['baseline_comparison']['baseline_preservation']
            )
            analysis['baseline_comparison']['improvement_achieved'] = (
                analysis['baseline_comparison']['improvement_factor'] > 1.0
            )
        
        # Fix preservation range if no valid scores
        if analysis['preservation_range']['min'] == 100.0:
            analysis['preservation_range']['min'] = 0.0
        
        # Log preservation summary
        logger.info("📊 Data Preservation Analysis:")
        logger.info(f"   Average Preservation: {analysis['average_preservation']:.1f}%")
        logger.info(f"   Industry Standard (95%+): {analysis['preservation_distribution']['industry_standard']}")
        logger.info(f"   Improvement Factor: {analysis['baseline_comparison']['improvement_factor']:.1f}x")
        
        return analysis
    
    def _validate_preservation_target(self, preservation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against 95%+ preservation target"""
        
        validation = {
            'target_percentage': 95.0,
            'average_achieved': preservation_analysis['average_preservation'],
            'meets_target': preservation_analysis['average_preservation'] >= 95.0,
            'target_achievement_rate': 0.0,
            'successful_tests': preservation_analysis['successful_tests'],
            'industry_standard_count': preservation_analysis['preservation_distribution']['industry_standard'],
            'gap_to_target': 0.0,
            'improvement_needed': 0.0
        }
        
        # Calculate target achievement rate
        if preservation_analysis['successful_tests'] > 0:
            validation['target_achievement_rate'] = (
                preservation_analysis['preservation_distribution']['industry_standard'] / 
                preservation_analysis['successful_tests'] * 100
            )
        
        # Calculate gap to target
        validation['gap_to_target'] = max(0, validation['target_percentage'] - validation['average_achieved'])
        
        # Calculate improvement needed
        if validation['average_achieved'] > 0:
            validation['improvement_needed'] = validation['target_percentage'] / validation['average_achieved']
        
        # Log target validation
        logger.info("🎯 95%+ Target Validation:")
        logger.info(f"   Target: {validation['target_percentage']}%")
        logger.info(f"   Achieved: {validation['average_achieved']:.1f}%")
        logger.info(f"   Meets Target: {'✅ YES' if validation['meets_target'] else '❌ NO'}")
        logger.info(f"   Achievement Rate: {validation['target_achievement_rate']:.1f}%")
        
        return validation
    
    def _generate_performance_recommendations(self, performance_metrics: Dict, 
                                           preservation_analysis: Dict, 
                                           target_validation: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        
        recommendations = []
        
        # Performance recommendations
        if performance_metrics['average_conversion_time'] > 30:
            recommendations.append("Optimize conversion algorithms for better performance")
        
        if performance_metrics['failed_tests'] > 0:
            recommendations.append("Improve error handling and conversion robustness")
        
        # Preservation recommendations
        if not target_validation['meets_target']:
            gap = target_validation['gap_to_target']
            recommendations.append(f"Enhance data preservation by {gap:.1f}% to meet 95%+ target")
        
        if preservation_analysis['component_preservation']['logic_avg'] < 90:
            recommendations.append("Improve ladder logic parsing and preservation")
        
        if preservation_analysis['component_preservation']['tags_avg'] < 90:
            recommendations.append("Enhance tag database extraction and preservation")
        
        if preservation_analysis['preservation_distribution']['industry_standard'] == 0:
            recommendations.append("Critical: No conversions achieved industry standard (95%+)")
        
        # Success recommendations
        if target_validation['meets_target']:
            recommendations.append("Excellent: Target preservation achieved - ready for production")
            recommendations.append("Proceed with migration to acd-l5x-tool-lib repository")
        
        return recommendations
    
    def _generate_performance_report(self):
        """Generate comprehensive performance report"""
        
        report_file = self.results_dir / f"phase39_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.performance_results, f, indent=2, default=str)
        
        # Generate markdown summary
        summary_file = self.results_dir / f"phase39_performance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(summary_file, 'w') as f:
            f.write(self._generate_performance_markdown_summary())
        
        logger.info(f"📄 Performance report saved: {report_file}")
        logger.info(f"📋 Summary saved: {summary_file}")
    
    def _generate_performance_markdown_summary(self) -> str:
        """Generate markdown summary of performance testing"""
        
        results = self.performance_results
        
        summary = f"""# Phase 3.9 Enhanced PLC Format Converter - Performance Test Report

## Executive Summary

**Test Date**: {results['timestamp']}  
**Phase**: {results['phase']}  
**Test Type**: {results['test_type']}  
**Target**: {results['target_preservation']} Data Preservation  
**Target Achieved**: {'✅ YES' if results.get('target_validation', {}).get('meets_target', False) else '❌ NO'}

## Performance Metrics

- **ACD Files Tested**: {results.get('acd_files_tested', 0)}
- **Successful Tests**: {results.get('performance_metrics', {}).get('successful_tests', 0)}
- **Average Conversion Time**: {results.get('performance_metrics', {}).get('average_conversion_time', 0):.2f}s
- **Average Throughput**: {results.get('performance_metrics', {}).get('average_throughput', 0):.2f} MB/s

## Data Preservation Results

- **Average Preservation**: {results.get('preservation_analysis', {}).get('average_preservation', 0):.1f}%
- **Industry Standard (95%+)**: {results.get('preservation_analysis', {}).get('preservation_distribution', {}).get('industry_standard', 0)} tests
- **Improvement Factor**: {results.get('preservation_analysis', {}).get('baseline_comparison', {}).get('improvement_factor', 0):.1f}x over baseline

## Target Validation

- **95%+ Target Met**: {'✅ YES' if results.get('target_validation', {}).get('meets_target', False) else '❌ NO'}
- **Achievement Rate**: {results.get('target_validation', {}).get('target_achievement_rate', 0):.1f}%
- **Gap to Target**: {results.get('target_validation', {}).get('gap_to_target', 0):.1f}%

"""
        
        if results.get('recommendations'):
            summary += "## Recommendations\n\n"
            for rec in results['recommendations']:
                summary += f"- 📋 {rec}\n"
        
        return summary
    
    def _generate_failure_report(self, reason: str) -> Dict[str, Any]:
        """Generate failure report when testing cannot proceed"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'failure_reason': reason,
            'phase': '3.9',
            'test_type': 'performance_evaluation',
            'target_achieved': False
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""


def run_phase39_performance_tests():
    """Run Phase 3.9 performance tests with comprehensive evaluation"""
    
    print("🚀 Phase 3.9 Enhanced PLC Format Converter - Performance Testing")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: 95%+ Data Preservation")
    print()
    
    # Initialize tester
    tester = Phase39PerformanceTester()
    
    # Run performance tests
    results = tester.run_performance_tests()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 80)
    
    if results.get('overall_success'):
        print("🎉 TARGET ACHIEVED - 95%+ Data Preservation!")
    else:
        print("⚠️  TARGET NOT MET - Improvement Required")
    
    # Performance metrics
    if results.get('performance_metrics'):
        metrics = results['performance_metrics']
        print(f"\n📈 Performance Metrics:")
        print(f"   Tests Run: {metrics.get('total_tests', 0)}")
        print(f"   Successful: {metrics.get('successful_tests', 0)}")
        print(f"   Average Time: {metrics.get('average_conversion_time', 0):.2f}s")
        print(f"   Throughput: {metrics.get('average_throughput', 0):.2f} MB/s")
    
    # Preservation results
    if results.get('preservation_analysis'):
        preservation = results['preservation_analysis']
        print(f"\n🎯 Data Preservation:")
        print(f"   Average: {preservation.get('average_preservation', 0):.1f}%")
        print(f"   Industry Standard: {preservation.get('preservation_distribution', {}).get('industry_standard', 0)}")
        print(f"   Improvement: {preservation.get('baseline_comparison', {}).get('improvement_factor', 0):.1f}x")
    
    # Target validation
    if results.get('target_validation'):
        target = results['target_validation']
        print(f"\n✅ Target Validation:")
        print(f"   95%+ Target: {'✅ MET' if target.get('meets_target', False) else '❌ NOT MET'}")
        print(f"   Achievement Rate: {target.get('target_achievement_rate', 0):.1f}%")
        
        if target.get('gap_to_target', 0) > 0:
            print(f"   Gap to Close: {target['gap_to_target']:.1f}%")
    
    # Recommendations
    if results.get('recommendations'):
        print(f"\n📋 Key Recommendations:")
        for rec in results['recommendations'][:3]:  # Show top 3
            print(f"   - {rec}")
    
    return results.get('overall_success', False)


if __name__ == "__main__":
    success = run_phase39_performance_tests()
    sys.exit(0 if success else 1) 