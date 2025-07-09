#!/usr/bin/env python3
"""
Phase 3.9 Deployment Validator
==============================

Comprehensive deployment validation script for the enhanced PLC format converter.
Tests with real ACD files from all 6 PLC repositories and measures data preservation
against the 95%+ target.

Following AI Task Orchestrator methodology for systematic validation.
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
        logging.FileHandler('phase39_deployment_validation.log'),
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

# Import AI Task Orchestrator
try:
    from ai.ai_task_orchestrator import validate_task_completion, get_task_guidance
    AI_ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI Task Orchestrator not available: {e}")
    AI_ORCHESTRATOR_AVAILABLE = False


class Phase39DeploymentValidator:
    """
    Comprehensive deployment validator for Phase 3.9 enhanced converter
    
    Validates the enhanced converter against real ACD files and measures
    data preservation performance against the 95%+ target.
    """
    
    def __init__(self):
        """Initialize deployment validator"""
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
            self.round_trip_validator = RoundTripValidator(enable_studio5000=False)
        else:
            self.converter = None
            self.validator = None
            self.round_trip_validator = None
        
        # Validation results
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'phase': '3.9',
            'target_preservation': '95%+',
            'repositories_tested': [],
            'overall_metrics': {},
            'individual_results': {},
            'deployment_readiness': {},
            'recommendations': []
        }
        
        logger.info("Phase 3.9 Deployment Validator initialized")
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """
        Run comprehensive deployment validation across all repositories
        
        Returns:
            Dict with complete validation results
        """
        logger.info("🚀 Starting Phase 3.9 Comprehensive Deployment Validation")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # Step 1: Validate enhanced converter availability
            logger.info("Step 1: Validating enhanced converter availability...")
            converter_status = self._validate_converter_availability()
            
            if not converter_status['available']:
                logger.error("Enhanced converter not available - cannot proceed with validation")
                return self._generate_failure_report("Enhanced converter not available")
            
            # Step 2: Discover and validate ACD files
            logger.info("Step 2: Discovering and validating ACD files...")
            acd_files = self._discover_acd_files()
            
            if not acd_files:
                logger.error("No ACD files found for validation")
                return self._generate_failure_report("No ACD files found")
            
            # Step 3: Test enhanced conversion on each ACD file
            logger.info("Step 3: Testing enhanced conversion on all ACD files...")
            conversion_results = self._test_enhanced_conversions(acd_files)
            
            # Step 4: Measure data preservation performance
            logger.info("Step 4: Measuring data preservation performance...")
            preservation_metrics = self._measure_preservation_performance(conversion_results)
            
            # Step 5: Validate against 95%+ target
            logger.info("Step 5: Validating against 95%+ preservation target...")
            target_validation = self._validate_preservation_target(preservation_metrics)
            
            # Step 6: Assess deployment readiness
            logger.info("Step 6: Assessing deployment readiness...")
            deployment_readiness = self._assess_deployment_readiness(
                converter_status, conversion_results, preservation_metrics, target_validation
            )
            
            # Compile final results
            total_time = time.time() - start_time
            
            self.validation_results.update({
                'validation_duration': total_time,
                'converter_status': converter_status,
                'acd_files_tested': len(acd_files),
                'conversion_results': conversion_results,
                'preservation_metrics': preservation_metrics,
                'target_validation': target_validation,
                'deployment_readiness': deployment_readiness,
                'overall_success': deployment_readiness.get('ready_for_deployment', False)
            })
            
            # Generate comprehensive report
            self._generate_deployment_report()
            
            logger.info(f"✅ Phase 3.9 Deployment Validation completed in {total_time:.2f}s")
            
            return self.validation_results
            
        except Exception as e:
            logger.error(f"Deployment validation failed: {e}")
            return self._generate_failure_report(f"Validation error: {e}")
    
    def _validate_converter_availability(self) -> Dict[str, Any]:
        """Validate enhanced converter availability and capabilities"""
        
        status = {
            'available': ENHANCED_CONVERTER_AVAILABLE,
            'components': {
                'enhanced_converter': self.converter is not None,
                'data_validator': self.validator is not None,
                'round_trip_validator': self.round_trip_validator is not None
            },
            'capabilities': {},
            'issues': []
        }
        
        if ENHANCED_CONVERTER_AVAILABLE and self.converter:
            try:
                # Test converter initialization
                stats = self.converter.get_conversion_stats()
                status['capabilities']['statistics_tracking'] = True
                
                # Test conversion methods availability
                status['capabilities']['acd_to_l5x'] = hasattr(self.converter, 'acd_to_l5x')
                status['capabilities']['l5x_to_acd'] = hasattr(self.converter, 'l5x_to_acd')
                
                # Test validation framework
                if self.validator:
                    status['capabilities']['data_integrity_validation'] = True
                    status['capabilities']['preservation_scoring'] = True
                
                if self.round_trip_validator:
                    status['capabilities']['round_trip_validation'] = True
                
                logger.info("✅ Enhanced converter validation passed")
                
            except Exception as e:
                status['issues'].append(f"Converter validation error: {e}")
                logger.warning(f"⚠️  Converter validation issues: {e}")
        
        return status
    
    def _discover_acd_files(self) -> List[Dict[str, Any]]:
        """Discover ACD files in all test repositories"""
        
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
                logger.info(f"📁 Found: {repo}/{acd_file.name} ({size_mb:.2f} MB)")
        
        logger.info(f"📊 Total ACD files discovered: {len(acd_files)}")
        
        return acd_files
    
    def _test_enhanced_conversions(self, acd_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Test enhanced conversion on all ACD files"""
        
        conversion_results = []
        
        for i, acd_info in enumerate(acd_files, 1):
            logger.info(f"🔄 Testing conversion {i}/{len(acd_files)}: {acd_info['repository']}")
            
            try:
                # Create output path
                output_dir = self.results_dir / acd_info['repository']
                output_dir.mkdir(exist_ok=True)
                
                output_file = output_dir / f"{acd_info['file_path'].stem}_enhanced.L5X"
                
                # Perform enhanced conversion
                start_time = time.time()
                
                if ENHANCED_CONVERTER_AVAILABLE and self.converter:
                    conversion_result = self.converter.acd_to_l5x(
                        acd_file=acd_info['file_path'],
                        l5x_file=output_file,
                        validate_round_trip=True
                    )
                    
                    conversion_time = time.time() - start_time
                    
                    # Compile conversion results
                    result = {
                        'repository': acd_info['repository'],
                        'source_file': str(acd_info['file_path']),
                        'output_file': str(output_file),
                        'conversion_time': conversion_time,
                        'success': conversion_result.success,
                        'status': conversion_result.status.value if hasattr(conversion_result.status, 'value') else str(conversion_result.status),
                        'source_size': acd_info['file_size'],
                        'output_size': output_file.stat().st_size if output_file.exists() else 0,
                        'data_integrity': conversion_result.data_integrity.to_dict() if conversion_result.data_integrity else None,
                        'issues': conversion_result.issues,
                        'warnings': conversion_result.warnings,
                        'round_trip_validated': conversion_result.round_trip_validated,
                        'git_optimized': conversion_result.git_optimized
                    }
                    
                    # Log conversion results
                    if conversion_result.success:
                        preservation = conversion_result.data_integrity.overall_score if conversion_result.data_integrity else 0
                        logger.info(f"   ✅ Success: {preservation:.1f}% preservation in {conversion_time:.2f}s")
                    else:
                        logger.warning(f"   ❌ Failed: {conversion_result.status}")
                        
                else:
                    # Fallback for when enhanced converter is not available
                    result = {
                        'repository': acd_info['repository'],
                        'source_file': str(acd_info['file_path']),
                        'success': False,
                        'status': 'enhanced_converter_not_available',
                        'error': 'Enhanced converter not available for testing'
                    }
                    
                    logger.warning(f"   ⚠️  Enhanced converter not available")
                
                conversion_results.append(result)
                
            except Exception as e:
                logger.error(f"   ❌ Conversion failed: {e}")
                
                error_result = {
                    'repository': acd_info['repository'],
                    'source_file': str(acd_info['file_path']),
                    'success': False,
                    'status': 'conversion_error',
                    'error': str(e)
                }
                
                conversion_results.append(error_result)
        
        return conversion_results
    
    def _measure_preservation_performance(self, conversion_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Measure data preservation performance across all conversions"""
        
        metrics = {
            'total_conversions': len(conversion_results),
            'successful_conversions': 0,
            'failed_conversions': 0,
            'average_preservation': 0.0,
            'preservation_scores': [],
            'performance_stats': {
                'average_conversion_time': 0.0,
                'total_processing_time': 0.0,
                'average_size_ratio': 0.0
            },
            'preservation_distribution': {
                'industry_standard': 0,  # 95%+
                'comprehensive': 0,      # 80-95%
                'partial_logic': 0,      # 50-80%
                'basic_structure': 0,    # 20-50%
                'metadata_only': 0       # 0-20%
            }
        }
        
        total_conversion_time = 0.0
        preservation_scores = []
        size_ratios = []
        
        for result in conversion_results:
            if result.get('success', False):
                metrics['successful_conversions'] += 1
                
                # Extract preservation score
                if result.get('data_integrity'):
                    preservation = result['data_integrity'].get('overall_score', 0.0)
                    preservation_scores.append(preservation)
                    
                    # Categorize preservation level
                    if preservation >= 95:
                        metrics['preservation_distribution']['industry_standard'] += 1
                    elif preservation >= 80:
                        metrics['preservation_distribution']['comprehensive'] += 1
                    elif preservation >= 50:
                        metrics['preservation_distribution']['partial_logic'] += 1
                    elif preservation >= 20:
                        metrics['preservation_distribution']['basic_structure'] += 1
                    else:
                        metrics['preservation_distribution']['metadata_only'] += 1
                
                # Extract performance metrics
                if result.get('conversion_time'):
                    total_conversion_time += result['conversion_time']
                
                if result.get('source_size') and result.get('output_size'):
                    size_ratio = result['output_size'] / result['source_size']
                    size_ratios.append(size_ratio)
            else:
                metrics['failed_conversions'] += 1
        
        # Calculate averages
        if preservation_scores:
            metrics['average_preservation'] = sum(preservation_scores) / len(preservation_scores)
            metrics['preservation_scores'] = preservation_scores
        
        if metrics['successful_conversions'] > 0:
            metrics['performance_stats']['average_conversion_time'] = total_conversion_time / metrics['successful_conversions']
            metrics['performance_stats']['total_processing_time'] = total_conversion_time
        
        if size_ratios:
            metrics['performance_stats']['average_size_ratio'] = sum(size_ratios) / len(size_ratios)
        
        # Log performance summary
        logger.info("📊 Data Preservation Performance Summary:")
        logger.info(f"   Total Conversions: {metrics['total_conversions']}")
        logger.info(f"   Successful: {metrics['successful_conversions']}")
        logger.info(f"   Failed: {metrics['failed_conversions']}")
        logger.info(f"   Average Preservation: {metrics['average_preservation']:.1f}%")
        logger.info(f"   Industry Standard (95%+): {metrics['preservation_distribution']['industry_standard']}")
        
        return metrics
    
    def _validate_preservation_target(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against 95%+ preservation target"""
        
        target_validation = {
            'target_percentage': 95.0,
            'average_achieved': metrics['average_preservation'],
            'meets_target': metrics['average_preservation'] >= 95.0,
            'industry_standard_count': metrics['preservation_distribution']['industry_standard'],
            'total_successful': metrics['successful_conversions'],
            'target_achievement_rate': 0.0,
            'improvement_over_baseline': 0.0,
            'baseline_preservation': 0.13  # From previous analysis
        }
        
        # Calculate target achievement rate
        if metrics['successful_conversions'] > 0:
            target_validation['target_achievement_rate'] = (
                metrics['preservation_distribution']['industry_standard'] / 
                metrics['successful_conversions'] * 100
            )
        
        # Calculate improvement over baseline
        if target_validation['baseline_preservation'] > 0:
            target_validation['improvement_over_baseline'] = (
                metrics['average_preservation'] / target_validation['baseline_preservation']
            )
        
        # Log target validation
        logger.info("🎯 95%+ Preservation Target Validation:")
        logger.info(f"   Target: {target_validation['target_percentage']}%")
        logger.info(f"   Achieved: {target_validation['average_achieved']:.1f}%")
        logger.info(f"   Meets Target: {'✅ YES' if target_validation['meets_target'] else '❌ NO'}")
        logger.info(f"   Achievement Rate: {target_validation['target_achievement_rate']:.1f}%")
        logger.info(f"   Improvement: {target_validation['improvement_over_baseline']:.1f}x over baseline")
        
        return target_validation
    
    def _assess_deployment_readiness(self, converter_status: Dict, conversion_results: List[Dict], 
                                   preservation_metrics: Dict, target_validation: Dict) -> Dict[str, Any]:
        """Assess overall deployment readiness"""
        
        readiness = {
            'ready_for_deployment': False,
            'readiness_score': 0.0,
            'critical_requirements': {
                'converter_available': converter_status['available'],
                'conversions_successful': preservation_metrics['successful_conversions'] > 0,
                'target_achieved': target_validation['meets_target'],
                'no_critical_errors': True
            },
            'quality_metrics': {
                'success_rate': 0.0,
                'average_preservation': preservation_metrics['average_preservation'],
                'performance_acceptable': True
            },
            'deployment_blockers': [],
            'recommendations': []
        }
        
        # Calculate success rate
        if preservation_metrics['total_conversions'] > 0:
            readiness['quality_metrics']['success_rate'] = (
                preservation_metrics['successful_conversions'] / 
                preservation_metrics['total_conversions'] * 100
            )
        
        # Check for critical errors
        critical_errors = [r for r in conversion_results if r.get('status') == 'conversion_error']
        readiness['critical_requirements']['no_critical_errors'] = len(critical_errors) == 0
        
        # Assess deployment blockers
        if not converter_status['available']:
            readiness['deployment_blockers'].append("Enhanced converter not available")
        
        if preservation_metrics['successful_conversions'] == 0:
            readiness['deployment_blockers'].append("No successful conversions achieved")
        
        if not target_validation['meets_target']:
            readiness['deployment_blockers'].append("95%+ preservation target not met")
        
        if readiness['quality_metrics']['success_rate'] < 80:
            readiness['deployment_blockers'].append("Success rate below 80% threshold")
        
        # Calculate readiness score
        critical_passed = sum(1 for req in readiness['critical_requirements'].values() if req)
        critical_total = len(readiness['critical_requirements'])
        
        quality_score = (
            readiness['quality_metrics']['success_rate'] * 0.4 +
            min(100, readiness['quality_metrics']['average_preservation']) * 0.6
        ) / 100
        
        readiness['readiness_score'] = (
            (critical_passed / critical_total) * 0.7 +
            quality_score * 0.3
        ) * 100
        
        # Determine deployment readiness
        readiness['ready_for_deployment'] = (
            len(readiness['deployment_blockers']) == 0 and
            readiness['readiness_score'] >= 80.0
        )
        
        # Generate recommendations
        if not readiness['ready_for_deployment']:
            if not target_validation['meets_target']:
                readiness['recommendations'].append("Enhance ACD binary parsing to improve data preservation")
            
            if readiness['quality_metrics']['success_rate'] < 90:
                readiness['recommendations'].append("Improve error handling and conversion robustness")
            
            if len(critical_errors) > 0:
                readiness['recommendations'].append("Address critical conversion errors")
        else:
            readiness['recommendations'].append("Ready for production deployment")
            readiness['recommendations'].append("Proceed with migration to acd-l5x-tool-lib repository")
        
        # Log deployment assessment
        logger.info("🚀 Deployment Readiness Assessment:")
        logger.info(f"   Readiness Score: {readiness['readiness_score']:.1f}%")
        logger.info(f"   Ready for Deployment: {'✅ YES' if readiness['ready_for_deployment'] else '❌ NO'}")
        
        if readiness['deployment_blockers']:
            logger.warning("   Deployment Blockers:")
            for blocker in readiness['deployment_blockers']:
                logger.warning(f"     - {blocker}")
        
        return readiness
    
    def _generate_deployment_report(self):
        """Generate comprehensive deployment validation report"""
        
        report_file = self.results_dir / f"phase39_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)
        
        # Generate markdown summary
        summary_file = self.results_dir / f"phase39_deployment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(summary_file, 'w') as f:
            f.write(self._generate_markdown_summary())
        
        logger.info(f"📄 Deployment report saved: {report_file}")
        logger.info(f"📋 Summary report saved: {summary_file}")
    
    def _generate_markdown_summary(self) -> str:
        """Generate markdown summary of deployment validation"""
        
        results = self.validation_results
        
        summary = f"""# Phase 3.9 Enhanced PLC Format Converter - Deployment Validation Report

## Executive Summary

**Validation Date**: {results['timestamp']}  
**Phase**: {results['phase']}  
**Target**: {results['target_preservation']} Data Preservation  
**Overall Success**: {'✅ PASSED' if results.get('overall_success', False) else '❌ FAILED'}

## Key Metrics

- **ACD Files Tested**: {results.get('acd_files_tested', 0)}
- **Successful Conversions**: {results.get('preservation_metrics', {}).get('successful_conversions', 0)}
- **Average Data Preservation**: {results.get('preservation_metrics', {}).get('average_preservation', 0):.1f}%
- **95%+ Target Achievement**: {results.get('target_validation', {}).get('target_achievement_rate', 0):.1f}%
- **Deployment Readiness**: {results.get('deployment_readiness', {}).get('readiness_score', 0):.1f}%

## Data Preservation Distribution

"""
        
        if results.get('preservation_metrics', {}).get('preservation_distribution'):
            dist = results['preservation_metrics']['preservation_distribution']
            summary += f"""
- **Industry Standard (95%+)**: {dist.get('industry_standard', 0)} conversions
- **Comprehensive (80-95%)**: {dist.get('comprehensive', 0)} conversions  
- **Partial Logic (50-80%)**: {dist.get('partial_logic', 0)} conversions
- **Basic Structure (20-50%)**: {dist.get('basic_structure', 0)} conversions
- **Metadata Only (0-20%)**: {dist.get('metadata_only', 0)} conversions
"""
        
        summary += f"""
## Deployment Assessment

**Ready for Deployment**: {'✅ YES' if results.get('deployment_readiness', {}).get('ready_for_deployment', False) else '❌ NO'}

"""
        
        if results.get('deployment_readiness', {}).get('deployment_blockers'):
            summary += "### Deployment Blockers\n\n"
            for blocker in results['deployment_readiness']['deployment_blockers']:
                summary += f"- ❌ {blocker}\n"
            summary += "\n"
        
        if results.get('deployment_readiness', {}).get('recommendations'):
            summary += "### Recommendations\n\n"
            for rec in results['deployment_readiness']['recommendations']:
                summary += f"- 📋 {rec}\n"
        
        return summary
    
    def _generate_failure_report(self, reason: str) -> Dict[str, Any]:
        """Generate failure report when validation cannot proceed"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'failure_reason': reason,
            'phase': '3.9',
            'deployment_ready': False
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


def run_phase39_deployment_validation():
    """Run Phase 3.9 deployment validation with comprehensive reporting"""
    
    print("🚀 Phase 3.9 Enhanced PLC Format Converter - Deployment Validation")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: 95%+ Data Preservation")
    print()
    
    # Initialize validator
    validator = Phase39DeploymentValidator()
    
    # Run comprehensive validation
    results = validator.run_comprehensive_validation()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 DEPLOYMENT VALIDATION SUMMARY")
    print("=" * 80)
    
    if results.get('overall_success'):
        print("🎉 VALIDATION PASSED - Ready for Deployment!")
    else:
        print("⚠️  VALIDATION ISSUES - Review Required")
    
    # Key metrics
    if results.get('preservation_metrics'):
        metrics = results['preservation_metrics']
        print(f"\n📈 Key Performance Metrics:")
        print(f"   ACD Files Tested: {results.get('acd_files_tested', 0)}")
        print(f"   Successful Conversions: {metrics.get('successful_conversions', 0)}")
        print(f"   Average Preservation: {metrics.get('average_preservation', 0):.1f}%")
        print(f"   Success Rate: {(metrics.get('successful_conversions', 0) / max(1, metrics.get('total_conversions', 1)) * 100):.1f}%")
    
    # Target validation
    if results.get('target_validation'):
        target = results['target_validation']
        print(f"\n🎯 95%+ Target Validation:")
        print(f"   Target Met: {'✅ YES' if target.get('meets_target', False) else '❌ NO'}")
        print(f"   Achievement Rate: {target.get('target_achievement_rate', 0):.1f}%")
        print(f"   Improvement: {target.get('improvement_over_baseline', 0):.1f}x over baseline")
    
    # Deployment readiness
    if results.get('deployment_readiness'):
        readiness = results['deployment_readiness']
        print(f"\n🚀 Deployment Readiness:")
        print(f"   Readiness Score: {readiness.get('readiness_score', 0):.1f}%")
        print(f"   Ready for Deployment: {'✅ YES' if readiness.get('ready_for_deployment', False) else '❌ NO'}")
        
        if readiness.get('recommendations'):
            print(f"\n📋 Next Steps:")
            for rec in readiness['recommendations'][:3]:  # Show top 3
                print(f"   - {rec}")
    
    return results.get('overall_success', False)


if __name__ == "__main__":
    success = run_phase39_deployment_validation()
    sys.exit(0 if success else 1) 