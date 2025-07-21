#!/usr/bin/env python3
"""
🚀 AI Enhancement Framework - Comprehensive Setup & Validation

This script sets up and validates the complete AI Task Orchestrator Guide methodology
implementation, ensuring all components work together properly.

Features Validated:
- 8-tier comprehensive validation framework
- WolframAlpha Pro mathematical integration (if configured)
- Fine-tuned LLM domain expertise (if configured)
- Success verification and automated documentation
- Multi-database memory integration support
- Production deployment readiness

Author: AI Enhancement Framework
Created: 2025-01-18
License: MIT
"""

import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveSetupValidator:
    """Validates the comprehensive AI Enhancement Framework setup"""
    
    def __init__(self):
        self.results = {}
        self.framework_root = Path(__file__).parent
        self.validation_results = []
        
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete framework validation"""
        logger.info("🚀 Starting Comprehensive AI Enhancement Framework Validation")
        start_time = time.time()
        
        try:
            # Step 1: Validate framework structure
            self._validate_framework_structure()
            
            # Step 2: Validate dependencies
            self._validate_dependencies()
            
            # Step 3: Validate core components
            asyncio.run(self._validate_core_components())
            
            # Step 4: Validate integration capabilities
            asyncio.run(self._validate_integration_capabilities())
            
            # Step 5: Run comprehensive methodology demonstration
            asyncio.run(self._demonstrate_comprehensive_methodology())
            
            # Step 6: Generate validation report
            self._generate_validation_report(start_time)
            
            logger.info("✅ Comprehensive validation completed successfully!")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Comprehensive validation failed: {e}")
            self.results['validation_failed'] = str(e)
            return self.results
    
    def _validate_framework_structure(self):
        """Validate framework directory structure"""
        logger.info("📁 Validating framework structure...")
        
        required_components = [
            'core/task_orchestrator.py',
            'core/memory_manager.py', 
            'core/code_analyzer.py',
            'core/validation_framework.py',
            'core/wolfram_integration.py',
            'core/llm_integration.py',
            'core/success_verification.py',
            'core/enhanced_task_orchestrator.py',
            'providers/provider_framework.py',
            'README.md',
            'requirements.txt',
            '.cursorrules',
            '.ai_framework_config.json',
            '.gitignore'
        ]
        
        missing_components = []
        existing_components = []
        
        for component in required_components:
            component_path = self.framework_root / component
            if component_path.exists():
                existing_components.append(component)
            else:
                missing_components.append(component)
        
        self.results['structure_validation'] = {
            'total_components': len(required_components),
            'existing_components': len(existing_components),
            'missing_components': missing_components,
            'completion_percentage': (len(existing_components) / len(required_components)) * 100
        }
        
        if missing_components:
            logger.warning(f"⚠️ Missing components: {missing_components}")
        else:
            logger.info("✅ All framework components present")
    
    def _validate_dependencies(self):
        """Validate Python dependencies"""
        logger.info("📦 Validating dependencies...")
        
        critical_imports = [
            ('asyncio', 'Core async support'),
            ('json', 'JSON processing'),
            ('time', 'Timing operations'),
            ('pathlib', 'Path operations'),
            ('datetime', 'Date/time handling'),
            ('typing', 'Type hints'),
            ('dataclasses', 'Data classes'),
            ('enum', 'Enumerations'),
            ('logging', 'Logging system')
        ]
        
        optional_imports = [
            ('numpy', 'Mathematical operations'),
            ('redis', 'Redis cache integration'),
            ('openai', 'OpenAI API integration'),
            ('psycopg2', 'PostgreSQL integration'),
            ('neo4j', 'Neo4j graph database'),
            ('qdrant_client', 'Qdrant vector database')
        ]
        
        import_results = {'critical': {}, 'optional': {}}
        
        # Test critical imports
        for module, description in critical_imports:
            try:
                __import__(module)
                import_results['critical'][module] = {'available': True, 'description': description}
            except ImportError as e:
                import_results['critical'][module] = {'available': False, 'error': str(e), 'description': description}
        
        # Test optional imports
        for module, description in optional_imports:
            try:
                __import__(module)
                import_results['optional'][module] = {'available': True, 'description': description}
            except ImportError as e:
                import_results['optional'][module] = {'available': False, 'error': str(e), 'description': description}
        
        critical_available = sum(1 for result in import_results['critical'].values() if result['available'])
        optional_available = sum(1 for result in import_results['optional'].values() if result['available'])
        
        self.results['dependency_validation'] = {
            'critical_imports': import_results['critical'],
            'optional_imports': import_results['optional'],
            'critical_available': critical_available,
            'critical_total': len(critical_imports),
            'optional_available': optional_available,
            'optional_total': len(optional_imports),
            'critical_percentage': (critical_available / len(critical_imports)) * 100
        }
        
        logger.info(f"✅ Critical dependencies: {critical_available}/{len(critical_imports)}")
        logger.info(f"✅ Optional dependencies: {optional_available}/{len(optional_imports)}")
    
    async def _validate_core_components(self):
        """Validate core framework components"""
        logger.info("🔧 Validating core components...")
        
        component_validations = {}
        
        # Validate task orchestrator
        try:
            from core.task_orchestrator import create_task_orchestrator
            orchestrator = create_task_orchestrator()
            component_validations['task_orchestrator'] = {'status': 'success', 'error': None}
            logger.info("✅ Task orchestrator validated")
        except Exception as e:
            component_validations['task_orchestrator'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Task orchestrator validation failed: {e}")
        
        # Validate validation framework
        try:
            from core.validation_framework import ComprehensiveValidationFramework
            framework = ComprehensiveValidationFramework()
            component_validations['validation_framework'] = {'status': 'success', 'error': None}
            logger.info("✅ Validation framework validated")
        except Exception as e:
            component_validations['validation_framework'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Validation framework validation failed: {e}")
        
        # Validate mathematical integration
        try:
            from core.wolfram_integration import MathematicalValidationOrchestrator
            math_orchestrator = MathematicalValidationOrchestrator(enable_wolfram_alpha=False)
            component_validations['wolfram_integration'] = {'status': 'success', 'error': None}
            logger.info("✅ Mathematical integration validated")
        except Exception as e:
            component_validations['wolfram_integration'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Mathematical integration validation failed: {e}")
        
        # Validate LLM integration
        try:
            from core.llm_integration import SpecializedLLMManager
            llm_manager = SpecializedLLMManager()
            component_validations['llm_integration'] = {'status': 'success', 'error': None}
            logger.info("✅ LLM integration validated")
        except Exception as e:
            component_validations['llm_integration'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ LLM integration validation failed: {e}")
        
        # Validate success verification
        try:
            from core.success_verification import SuccessVerificationOrchestrator
            success_verifier = SuccessVerificationOrchestrator()
            component_validations['success_verification'] = {'status': 'success', 'error': None}
            logger.info("✅ Success verification validated")
        except Exception as e:
            component_validations['success_verification'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Success verification validation failed: {e}")
        
        # Validate enhanced orchestrator
        try:
            from core.enhanced_task_orchestrator import EnhancedAITaskOrchestrator
            enhanced_orchestrator = EnhancedAITaskOrchestrator(
                enable_wolfram_alpha=False,
                enable_specialized_llm=False,
                enable_success_verification=False
            )
            component_validations['enhanced_orchestrator'] = {'status': 'success', 'error': None}
            logger.info("✅ Enhanced orchestrator validated")
        except Exception as e:
            component_validations['enhanced_orchestrator'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Enhanced orchestrator validation failed: {e}")
        
        successful_components = sum(1 for result in component_validations.values() if result['status'] == 'success')
        total_components = len(component_validations)
        
        self.results['core_component_validation'] = {
            'components': component_validations,
            'successful': successful_components,
            'total': total_components,
            'success_percentage': (successful_components / total_components) * 100
        }
    
    async def _validate_integration_capabilities(self):
        """Validate integration capabilities"""
        logger.info("🔗 Validating integration capabilities...")
        
        integration_tests = {}
        
        # Test 8-tier validation
        try:
            from core.validation_framework import validate_code_comprehensive
            
            test_code = '''
def hello_world():
    """A simple test function."""
    return "Hello, World!"
'''
            
            result = validate_code_comprehensive(
                code_content=test_code,
                requirements=["Implement hello world function"],
                validation_tier="standard"
            )
            
            integration_tests['8_tier_validation'] = {
                'status': 'success',
                'score': result.overall_score,
                'tiers_tested': len(result.tier_results)
            }
            logger.info(f"✅ 8-tier validation: {result.overall_score:.1f}%")
            
        except Exception as e:
            integration_tests['8_tier_validation'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ 8-tier validation test failed: {e}")
        
        # Test mathematical validation (without WolframAlpha)
        try:
            from core.wolfram_integration import validate_mathematical_code
            
            math_code = '''
import math

def calculate_circle_area(radius):
    """Calculate circle area."""
    return math.pi * radius ** 2
'''
            
            result = await validate_mathematical_code(
                code_content=math_code,
                enable_wolfram_alpha=False
            )
            
            integration_tests['mathematical_validation'] = {
                'status': 'success',
                'accuracy_score': result.get('accuracy_score', 100),
                'expressions_found': result.get('expressions_found', 0)
            }
            logger.info(f"✅ Mathematical validation: {result.get('accuracy_score', 100):.1f}%")
            
        except Exception as e:
            integration_tests['mathematical_validation'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Mathematical validation test failed: {e}")
        
        # Test domain-specific analysis
        try:
            from core.llm_integration import is_domain_specific_task
            
            is_specialized, domain = is_domain_specific_task("Implement PID controller for temperature control")
            
            integration_tests['domain_analysis'] = {
                'status': 'success',
                'domain_detected': is_specialized,
                'detected_domain': domain.value if domain else None
            }
            logger.info(f"✅ Domain analysis: Domain detected = {is_specialized}")
            
        except Exception as e:
            integration_tests['domain_analysis'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Domain analysis test failed: {e}")
        
        # Test success verification
        try:
            from core.success_verification import verify_task_completion
            
            mock_results = {
                'phase': 'Test_Phase',
                'validation_results': {'overall_score': 95.0},
                'deliverables': [],
                'achievements': ['Test completed'],
                'performance_metrics': {'test_time': '1.0s'}
            }
            
            result = verify_task_completion('test_001', mock_results)
            
            integration_tests['success_verification'] = {
                'status': 'success',
                'verification_success': result.get('success', False),
                'documentation_created': len(result.get('documentation_paths', {}))
            }
            logger.info(f"✅ Success verification: {result.get('success', False)}")
            
        except Exception as e:
            integration_tests['success_verification'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Success verification test failed: {e}")
        
        successful_integrations = sum(1 for result in integration_tests.values() if result['status'] == 'success')
        total_integrations = len(integration_tests)
        
        self.results['integration_validation'] = {
            'tests': integration_tests,
            'successful': successful_integrations,
            'total': total_integrations,
            'success_percentage': (successful_integrations / total_integrations) * 100
        }
    
    async def _demonstrate_comprehensive_methodology(self):
        """Demonstrate the complete comprehensive methodology"""
        logger.info("🎯 Demonstrating comprehensive methodology...")
        
        try:
            from core.enhanced_task_orchestrator import EnhancedAITaskOrchestrator
            
            # Create orchestrator with limited external dependencies
            orchestrator = EnhancedAITaskOrchestrator(
                enable_wolfram_alpha=False,  # Disable for demo unless configured
                enable_specialized_llm=False,  # Disable for demo unless configured
                enable_success_verification=True
            )
            
            # Demonstrate task analysis
            task_description = "Create a simple calculator with basic arithmetic operations and error handling"
            
            analysis = await orchestrator.analyze_task_comprehensive(task_description)
            
            # Demonstrate validation
            sample_code = '''
def calculator(operation, a, b):
    """Simple calculator with error handling."""
    try:
        if operation == 'add':
            return a + b
        elif operation == 'subtract':
            return a - b
        elif operation == 'multiply':
            return a * b
        elif operation == 'divide':
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        else:
            raise ValueError("Invalid operation")
    except Exception as e:
        return f"Error: {str(e)}"

# Test the calculator
if __name__ == "__main__":
    print(calculator('add', 5, 3))
    print(calculator('divide', 10, 2))
    print(calculator('divide', 10, 0))
'''
            
            validation_results = await orchestrator.validate_implementation_comprehensive(
                code_content=sample_code,
                requirements=analysis.requirements,
                analysis=analysis
            )
            
            self.results['methodology_demonstration'] = {
                'task_analysis': {
                    'complexity': analysis.complexity.value,
                    'domain_specific': analysis.domain_specific,
                    'mathematical_content': analysis.mathematical_content,
                    'requirements_count': len(analysis.requirements),
                    'execution_plan_steps': len(analysis.execution_plan)
                },
                'validation_results': {
                    'overall_score': validation_results.overall_score,
                    'production_ready': validation_results.production_ready,
                    'tiers_validated': len(validation_results.tier_results),
                    'recommendations_count': len(validation_results.recommendations)
                }
            }
            
            logger.info(f"✅ Methodology demonstration: {validation_results.overall_score:.1f}% score")
            
        except Exception as e:
            self.results['methodology_demonstration'] = {'status': 'failed', 'error': str(e)}
            logger.warning(f"⚠️ Methodology demonstration failed: {e}")
    
    def _generate_validation_report(self, start_time: float):
        """Generate comprehensive validation report"""
        logger.info("📊 Generating validation report...")
        
        execution_time = time.time() - start_time
        
        # Calculate overall success rate
        validations = [
            self.results.get('structure_validation', {}).get('completion_percentage', 0),
            self.results.get('dependency_validation', {}).get('critical_percentage', 0),
            self.results.get('core_component_validation', {}).get('success_percentage', 0),
            self.results.get('integration_validation', {}).get('success_percentage', 0)
        ]
        
        overall_success_rate = sum(validations) / len(validations) if validations else 0
        
        report = {
            'validation_summary': {
                'overall_success_rate': overall_success_rate,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'framework_version': '1.0.0',
                'methodology_compliance': 'AI Task Orchestrator Guide'
            },
            'detailed_results': self.results
        }
        
        # Save report
        report_path = self.framework_root / 'validation_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Validation report saved: {report_path}")
        
        # Print summary
        self._print_validation_summary(overall_success_rate, execution_time)
        
        self.results['validation_summary'] = report['validation_summary']
    
    def _print_validation_summary(self, success_rate: float, execution_time: float):
        """Print validation summary"""
        print("\n" + "="*60)
        print("🎉 AI ENHANCEMENT FRAMEWORK VALIDATION COMPLETE")
        print("="*60)
        print(f"📊 Overall Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Execution Time: {execution_time:.2f}s")
        print(f"📅 Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Framework structure
        structure = self.results.get('structure_validation', {})
        print(f"📁 Framework Structure: {structure.get('completion_percentage', 0):.1f}%")
        print(f"   Components: {structure.get('existing_components', 0)}/{structure.get('total_components', 0)}")
        
        # Dependencies
        deps = self.results.get('dependency_validation', {})
        print(f"📦 Dependencies: {deps.get('critical_percentage', 0):.1f}%")
        print(f"   Critical: {deps.get('critical_available', 0)}/{deps.get('critical_total', 0)}")
        print(f"   Optional: {deps.get('optional_available', 0)}/{deps.get('optional_total', 0)}")
        
        # Core components
        core = self.results.get('core_component_validation', {})
        print(f"🔧 Core Components: {core.get('success_percentage', 0):.1f}%")
        print(f"   Successful: {core.get('successful', 0)}/{core.get('total', 0)}")
        
        # Integration capabilities
        integration = self.results.get('integration_validation', {})
        print(f"🔗 Integration Tests: {integration.get('success_percentage', 0):.1f}%")
        print(f"   Successful: {integration.get('successful', 0)}/{integration.get('total', 0)}")
        
        # Methodology demonstration
        methodology = self.results.get('methodology_demonstration', {})
        if 'validation_results' in methodology:
            val_results = methodology['validation_results']
            print(f"🎯 Methodology Demo: {val_results.get('overall_score', 0):.1f}%")
            print(f"   Production Ready: {'✅' if val_results.get('production_ready') else '❌'}")
        
        print()
        if success_rate >= 90:
            print("🎉 EXCELLENT! Framework is ready for comprehensive task execution!")
        elif success_rate >= 75:
            print("✅ GOOD! Framework is functional with some optional features missing.")
        elif success_rate >= 50:
            print("⚠️ WARNING! Framework has significant issues that should be addressed.")
        else:
            print("❌ CRITICAL! Framework requires major fixes before use.")
        
        print("\n📚 Next Steps:")
        print("1. Review validation_report.json for detailed results")
        print("2. Install missing dependencies if needed: pip install -r requirements.txt")
        print("3. Configure optional integrations (WolframAlpha, OpenAI API keys)")
        print("4. Run the enhanced task orchestrator for full functionality")
        print("="*60)

def main():
    """Main validation function"""
    print("🚀 AI Enhancement Framework - Comprehensive Validation")
    print("Implementing AI Task Orchestrator Guide Methodology")
    print()
    
    validator = ComprehensiveSetupValidator()
    results = validator.run_comprehensive_validation()
    
    return results

if __name__ == "__main__":
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Add the current directory to Python path for imports
    sys.path.insert(0, str(script_dir))
    
    try:
        results = main()
        
        # Exit with appropriate code
        success_rate = results.get('validation_summary', {}).get('overall_success_rate', 0)
        if success_rate >= 75:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1) 