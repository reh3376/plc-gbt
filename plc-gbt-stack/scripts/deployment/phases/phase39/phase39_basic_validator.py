#!/usr/bin/env python3
"""
Phase 3.9 Basic Deployment Validator
====================================

Basic deployment validation script that tests infrastructure and validates
the deployment framework without requiring all enhanced components to be
fully functional.

Following AI Task Orchestrator methodology for systematic validation.
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

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
        logging.FileHandler('phase39_basic_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import AI Task Orchestrator
try:
    from ai.ai_task_orchestrator import get_task_guidance, validate_task_completion
    AI_ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI Task Orchestrator not available: {e}")
    AI_ORCHESTRATOR_AVAILABLE = False


class Phase39BasicValidator:
    """
    Basic deployment validator for Phase 3.9 infrastructure

    Tests deployment readiness without requiring all enhanced components
    to be fully functional.
    """

    def __init__(self):
        """Initialize basic validator"""
        self.repo_base = Path("/Users/reh3376/repos")
        self.test_repos = ["plc-100", "plc-200", "plc-300", "plc-400", "plc-500", "plc-600"]
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)

        # Validation results
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'phase': '3.9',
            'validation_type': 'basic_infrastructure',
            'target_preservation': '95%+',
            'infrastructure_tests': {},
            'acd_file_discovery': {},
            'baseline_analysis': {},
            'deployment_readiness': {},
            'recommendations': []
        }

        logger.info("Phase 3.9 Basic Deployment Validator initialized")

    def run_basic_validation(self) -> Dict[str, Any]:
        """
        Run basic deployment validation focusing on infrastructure

        Returns:
            Dict with validation results
        """
        logger.info("🚀 Starting Phase 3.9 Basic Deployment Validation")
        logger.info("=" * 80)

        start_time = time.time()

        try:
            # Step 1: Test infrastructure components
            logger.info("Step 1: Testing infrastructure components...")
            infrastructure_status = self._test_infrastructure_components()

            # Step 2: Discover and analyze ACD files
            logger.info("Step 2: Discovering and analyzing ACD files...")
            acd_analysis = self._discover_and_analyze_acd_files()

            # Step 3: Analyze baseline preservation
            logger.info("Step 3: Analyzing baseline data preservation...")
            baseline_analysis = self._analyze_baseline_preservation()

            # Step 4: Test enhanced component availability
            logger.info("Step 4: Testing enhanced component availability...")
            component_availability = self._test_enhanced_components()

            # Step 5: Assess deployment readiness
            logger.info("Step 5: Assessing deployment readiness...")
            deployment_readiness = self._assess_basic_deployment_readiness(
                infrastructure_status, acd_analysis, baseline_analysis, component_availability
            )

            # Compile final results
            total_time = time.time() - start_time

            self.validation_results.update({
                'validation_duration': total_time,
                'infrastructure_status': infrastructure_status,
                'acd_file_discovery': acd_analysis,
                'baseline_analysis': baseline_analysis,
                'component_availability': component_availability,
                'deployment_readiness': deployment_readiness,
                'overall_success': deployment_readiness.get('infrastructure_ready', False)
            })

            # Generate basic report
            self._generate_basic_report()

            logger.info(f"✅ Phase 3.9 Basic Validation completed in {total_time:.2f}s")

            return self.validation_results

        except Exception as e:
            logger.error(f"Basic validation failed: {e}")
            return self._generate_failure_report(f"Validation error: {e}")

    def _test_infrastructure_components(self) -> Dict[str, Any]:
        """Test basic infrastructure components"""

        status = {
            'python_environment': False,
            'project_structure': False,
            'ai_orchestrator': AI_ORCHESTRATOR_AVAILABLE,
            'enhanced_models': False,
            'validation_framework': False,
            'git_optimization': False,
            'issues': []
        }

        # Test Python environment
        try:
            import sys
            python_version = sys.version_info
            if python_version.major >= 3 and python_version.minor >= 8:
                status['python_environment'] = True
            else:
                status['issues'].append(f"Python version {python_version} may be too old")
        except Exception as e:
            status['issues'].append(f"Python environment test failed: {e}")

        # Test project structure
        try:
            required_paths = [
                project_root / "plc-gpt-stack",
                project_root / "plc-gpt-stack" / "plc-format-converter",
                project_root / "plc-gpt-stack" / "plc-format-converter" / "src"
            ]

            if all(path.exists() for path in required_paths):
                status['project_structure'] = True
            else:
                missing = [str(p) for p in required_paths if not p.exists()]
                status['issues'].append(f"Missing project paths: {missing}")
        except Exception as e:
            status['issues'].append(f"Project structure test failed: {e}")

        # Test enhanced models
        try:
            sys.path.insert(0, str(project_root / "plc-gpt-stack" / "plc-format-converter" / "src"))
            from plc_format_converter.core.models import (
                ConversionResult,
                ConversionStatus,
                DataIntegrityScore,
                PLCProject,
            )
            status['enhanced_models'] = True
        except ImportError as e:
            status['issues'].append(f"Enhanced models import failed: {e}")

        # Test validation framework
        try:
            from plc_format_converter.utils.validation import DataIntegrityValidator
            status['validation_framework'] = True
        except ImportError as e:
            status['issues'].append(f"Validation framework import failed: {e}")

        # Test git optimization
        try:
            from plc_format_converter.utils.git_optimization import GitOptimizer
            status['git_optimization'] = True
        except ImportError as e:
            status['issues'].append(f"Git optimization import failed: {e}")

        # Log infrastructure status
        passed_tests = sum(1 for k, v in status.items() if k != 'issues' and v)
        total_tests = len([k for k in status.keys() if k != 'issues'])

        logger.info(f"📊 Infrastructure Tests: {passed_tests}/{total_tests} passed")

        return status

    def _discover_and_analyze_acd_files(self) -> Dict[str, Any]:
        """Discover and analyze ACD files in test repositories"""

        analysis = {
            'repositories_scanned': len(self.test_repos),
            'acd_files_found': 0,
            'total_size_mb': 0.0,
            'files_by_repo': {},
            'size_distribution': {},
            'issues': []
        }

        for repo in self.test_repos:
            repo_path = self.repo_base / repo
            acd_dir = repo_path / "plc-acd"

            repo_files = []

            if acd_dir.exists():
                for acd_file in acd_dir.glob("*.ACD"):
                    file_size = acd_file.stat().st_size
                    size_mb = file_size / (1024 * 1024)

                    file_info = {
                        'name': acd_file.name,
                        'size_bytes': file_size,
                        'size_mb': round(size_mb, 2),
                        'last_modified': datetime.fromtimestamp(acd_file.stat().st_mtime).isoformat()
                    }

                    repo_files.append(file_info)
                    analysis['total_size_mb'] += size_mb

                    # Categorize by size
                    if size_mb < 1:
                        category = 'small'
                    elif size_mb < 5:
                        category = 'medium'
                    else:
                        category = 'large'

                    analysis['size_distribution'][category] = analysis['size_distribution'].get(category, 0) + 1

                    logger.info(f"📁 Found: {repo}/{acd_file.name} ({size_mb:.2f} MB)")
            else:
                analysis['issues'].append(f"ACD directory not found for {repo}")

            analysis['files_by_repo'][repo] = repo_files
            analysis['acd_files_found'] += len(repo_files)

        analysis['total_size_mb'] = round(analysis['total_size_mb'], 2)

        logger.info(f"📊 ACD File Discovery: {analysis['acd_files_found']} files, {analysis['total_size_mb']} MB total")

        return analysis

    def _analyze_baseline_preservation(self) -> Dict[str, Any]:
        """Analyze baseline data preservation from existing L5X files"""

        analysis = {
            'baseline_preservation_percent': 0.13,  # From previous analysis
            'l5x_files_found': 0,
            'total_l5x_size_mb': 0.0,
            'preservation_ratios': [],
            'improvement_potential': 0.0,
            'target_achievement': {}
        }

        # Scan for existing L5X files
        for repo in self.test_repos:
            repo_path = self.repo_base / repo
            l5x_dir = repo_path / "plc-l5x"

            if l5x_dir.exists():
                for l5x_file in l5x_dir.glob("*.L5X"):
                    file_size = l5x_file.stat().st_size
                    size_mb = file_size / (1024 * 1024)
                    analysis['total_l5x_size_mb'] += size_mb
                    analysis['l5x_files_found'] += 1

        analysis['total_l5x_size_mb'] = round(analysis['total_l5x_size_mb'], 2)

        # Calculate improvement potential
        target_preservation = 95.0
        current_preservation = analysis['baseline_preservation_percent']
        analysis['improvement_potential'] = target_preservation / current_preservation

        # Target achievement analysis
        analysis['target_achievement'] = {
            'current_preservation': current_preservation,
            'target_preservation': target_preservation,
            'improvement_factor': round(analysis['improvement_potential'], 1),
            'gap_to_close': target_preservation - current_preservation
        }

        logger.info(f"📊 Baseline Analysis: {current_preservation}% → {target_preservation}% ({analysis['improvement_potential']:.1f}x improvement needed)")

        return analysis

    def _test_enhanced_components(self) -> Dict[str, Any]:
        """Test availability of enhanced components"""

        components = {
            'enhanced_models': False,
            'enhanced_converter': False,
            'enhanced_handlers': False,
            'validation_framework': False,
            'git_optimization': False,
            'ai_orchestrator': AI_ORCHESTRATOR_AVAILABLE,
            'issues': []
        }

        # Test enhanced models
        try:
            sys.path.insert(0, str(project_root / "plc-gpt-stack" / "plc-format-converter" / "src"))
            from plc_format_converter.core.models import (
                DataIntegrityScore,
                PLCController,
                PLCDevice,
                PLCProject,
            )
            components['enhanced_models'] = True
        except ImportError as e:
            components['issues'].append(f"Enhanced models: {e}")

        # Test enhanced converter
        try:
            from plc_format_converter.core.converter import EnhancedPLCConverter
            # Try to instantiate
            EnhancedPLCConverter(enable_studio5000=False)
            components['enhanced_converter'] = True
        except Exception as e:
            components['issues'].append(f"Enhanced converter: {e}")

        # Test validation framework
        try:
            from plc_format_converter.utils.validation import (
                DataIntegrityValidator,
                RoundTripValidator,
            )
            components['validation_framework'] = True
        except ImportError as e:
            components['issues'].append(f"Validation framework: {e}")

        # Test git optimization
        try:
            from plc_format_converter.utils.git_optimization import GitOptimizer
            components['git_optimization'] = True
        except ImportError as e:
            components['issues'].append(f"Git optimization: {e}")

        # Calculate availability percentage
        available_count = sum(1 for k, v in components.items() if k != 'issues' and v)
        total_count = len([k for k in components.keys() if k != 'issues'])
        availability_percentage = (available_count / total_count) * 100

        components['availability_percentage'] = round(availability_percentage, 1)

        logger.info(f"📊 Component Availability: {available_count}/{total_count} ({availability_percentage:.1f}%)")

        return components

    def _assess_basic_deployment_readiness(self, infrastructure_status: Dict, acd_analysis: Dict,
                                         baseline_analysis: Dict, component_availability: Dict) -> Dict[str, Any]:
        """Assess basic deployment readiness"""

        readiness = {
            'infrastructure_ready': False,
            'data_available': False,
            'components_available': False,
            'readiness_score': 0.0,
            'deployment_blockers': [],
            'recommendations': [],
            'next_steps': []
        }

        # Check infrastructure readiness
        infra_passed = sum(1 for k, v in infrastructure_status.items() if k != 'issues' and v)
        infra_total = len([k for k in infrastructure_status.keys() if k != 'issues'])
        infra_percentage = (infra_passed / infra_total) * 100

        readiness['infrastructure_ready'] = infra_percentage >= 70

        # Check data availability
        readiness['data_available'] = acd_analysis['acd_files_found'] > 0

        # Check component availability
        readiness['components_available'] = component_availability['availability_percentage'] >= 50

        # Calculate overall readiness score
        readiness['readiness_score'] = (
            (infra_percentage * 0.4) +
            (100 if readiness['data_available'] else 0) * 0.3 +
            (component_availability['availability_percentage'] * 0.3)
        )

        # Identify deployment blockers
        if not readiness['infrastructure_ready']:
            readiness['deployment_blockers'].append("Infrastructure not ready (< 70% pass rate)")

        if not readiness['data_available']:
            readiness['deployment_blockers'].append("No ACD files found for testing")

        if not readiness['components_available']:
            readiness['deployment_blockers'].append("Enhanced components not available (< 50%)")

        # Generate recommendations
        if infrastructure_status.get('issues'):
            readiness['recommendations'].append("Resolve infrastructure issues")

        if component_availability['availability_percentage'] < 80:
            readiness['recommendations'].append("Complete enhanced component implementation")

        if acd_analysis['acd_files_found'] == 0:
            readiness['recommendations'].append("Ensure ACD test files are available")

        # Generate next steps
        if readiness['readiness_score'] >= 80:
            readiness['next_steps'].append("Proceed with full enhanced converter testing")
            readiness['next_steps'].append("Implement remaining enhanced components")
        elif readiness['readiness_score'] >= 60:
            readiness['next_steps'].append("Address component availability issues")
            readiness['next_steps'].append("Test basic conversion workflows")
        else:
            readiness['next_steps'].append("Fix infrastructure issues")
            readiness['next_steps'].append("Complete basic component implementation")

        # Log deployment assessment
        logger.info("🚀 Basic Deployment Readiness Assessment:")
        logger.info(f"   Infrastructure Ready: {'✅ YES' if readiness['infrastructure_ready'] else '❌ NO'}")
        logger.info(f"   Data Available: {'✅ YES' if readiness['data_available'] else '❌ NO'}")
        logger.info(f"   Components Available: {'✅ YES' if readiness['components_available'] else '❌ NO'}")
        logger.info(f"   Readiness Score: {readiness['readiness_score']:.1f}%")

        return readiness

    def _generate_basic_report(self):
        """Generate basic deployment validation report"""

        report_file = self.results_dir / f"phase39_basic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)

        # Generate markdown summary
        summary_file = self.results_dir / f"phase39_basic_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(summary_file, 'w') as f:
            f.write(self._generate_basic_markdown_summary())

        logger.info(f"📄 Basic report saved: {report_file}")
        logger.info(f"📋 Summary saved: {summary_file}")

    def _generate_basic_markdown_summary(self) -> str:
        """Generate markdown summary of basic validation"""

        results = self.validation_results

        summary = f"""# Phase 3.9 Enhanced PLC Format Converter - Basic Validation Report

## Executive Summary

**Validation Date**: {results['timestamp']}
**Phase**: {results['phase']}
**Validation Type**: {results['validation_type']}
**Target**: {results['target_preservation']} Data Preservation
**Infrastructure Ready**: {'✅ PASSED' if results.get('deployment_readiness', {}).get('infrastructure_ready', False) else '❌ NEEDS WORK'}

## Key Metrics

- **ACD Files Available**: {results.get('acd_file_discovery', {}).get('acd_files_found', 0)}
- **Total ACD Data**: {results.get('acd_file_discovery', {}).get('total_size_mb', 0)} MB
- **Component Availability**: {results.get('component_availability', {}).get('availability_percentage', 0):.1f}%
- **Infrastructure Readiness**: {results.get('deployment_readiness', {}).get('readiness_score', 0):.1f}%

## Baseline Analysis

- **Current Preservation**: {results.get('baseline_analysis', {}).get('baseline_preservation_percent', 0)}%
- **Target Preservation**: 95%+
- **Improvement Factor**: {results.get('baseline_analysis', {}).get('target_achievement', {}).get('improvement_factor', 0)}x

## Infrastructure Status

"""

        if results.get('infrastructure_status'):
            infra = results['infrastructure_status']
            for component, status in infra.items():
                if component != 'issues':
                    summary += f"- **{component.replace('_', ' ').title()}**: {'✅ PASS' if status else '❌ FAIL'}\n"

        summary += "\n## Deployment Assessment\n\n"

        if results.get('deployment_readiness', {}).get('deployment_blockers'):
            summary += "### Deployment Blockers\n\n"
            for blocker in results['deployment_readiness']['deployment_blockers']:
                summary += f"- ❌ {blocker}\n"
            summary += "\n"

        if results.get('deployment_readiness', {}).get('next_steps'):
            summary += "### Next Steps\n\n"
            for step in results['deployment_readiness']['next_steps']:
                summary += f"- 📋 {step}\n"

        return summary

    def _generate_failure_report(self, reason: str) -> Dict[str, Any]:
        """Generate failure report when validation cannot proceed"""

        return {
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'failure_reason': reason,
            'phase': '3.9',
            'validation_type': 'basic_infrastructure',
            'deployment_ready': False
        }


def run_phase39_basic_validation():
    """Run Phase 3.9 basic deployment validation"""

    print("🚀 Phase 3.9 Enhanced PLC Format Converter - Basic Validation")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("Focus: Infrastructure and Component Availability")
    print()

    # Initialize validator
    validator = Phase39BasicValidator()

    # Run basic validation
    results = validator.run_basic_validation()

    # Print summary
    print("\n" + "=" * 80)
    print("📊 BASIC VALIDATION SUMMARY")
    print("=" * 80)

    if results.get('overall_success'):
        print("🎉 INFRASTRUCTURE VALIDATION PASSED!")
    else:
        print("⚠️  INFRASTRUCTURE NEEDS ATTENTION")

    # Key metrics
    if results.get('acd_file_discovery'):
        discovery = results['acd_file_discovery']
        print("\n📈 Data Availability:")
        print(f"   ACD Files Found: {discovery.get('acd_files_found', 0)}")
        print(f"   Total Size: {discovery.get('total_size_mb', 0)} MB")
        print(f"   Repositories: {discovery.get('repositories_scanned', 0)}")

    # Component availability
    if results.get('component_availability'):
        components = results['component_availability']
        print("\n🔧 Component Availability:")
        print(f"   Overall: {components.get('availability_percentage', 0):.1f}%")
        print(f"   Enhanced Models: {'✅' if components.get('enhanced_models') else '❌'}")
        print(f"   Validation Framework: {'✅' if components.get('validation_framework') else '❌'}")
        print(f"   Git Optimization: {'✅' if components.get('git_optimization') else '❌'}")

    # Deployment readiness
    if results.get('deployment_readiness'):
        readiness = results['deployment_readiness']
        print("\n🚀 Deployment Readiness:")
        print(f"   Readiness Score: {readiness.get('readiness_score', 0):.1f}%")
        print(f"   Infrastructure Ready: {'✅ YES' if readiness.get('infrastructure_ready', False) else '❌ NO'}")

        if readiness.get('next_steps'):
            print("\n📋 Next Steps:")
            for step in readiness['next_steps'][:3]:  # Show top 3
                print(f"   - {step}")

    return results.get('overall_success', False)


if __name__ == "__main__":
    success = run_phase39_basic_validation()
    sys.exit(0 if success else 1)
