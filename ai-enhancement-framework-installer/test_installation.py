#!/usr/bin/env python3
"""
🧪 AI Enhancement Framework - Installation Test Script

This script tests the AI Enhancement Framework installation package to ensure
all components work correctly in an isolated environment.

Author: AI Enhancement Framework
Created: 2025-01-21
License: MIT
"""

import os
import sys
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstallationTester:
    """Tests the AI Enhancement Framework installation package"""
    
    def __init__(self):
        self.installer_root = Path(__file__).parent
        self.test_results = {}
        self.temp_dir = None
    
    def run_tests(self) -> Dict[str, Any]:
        """Run comprehensive installation tests"""
        logger.info("🧪 Starting AI Enhancement Framework Installation Tests")
        
        try:
            # Create temporary test environment
            self._setup_test_environment()
            
            # Test different installation types
            self._test_minimal_installation()
            self._test_automated_installation()
            self._test_framework_import()
            self._test_core_functionality()
            
            # Generate test report
            return self._generate_test_report(success=True)
            
        except Exception as e:
            logger.error(f"❌ Tests failed: {e}")
            return self._generate_test_report(success=False, error=str(e))
            
        finally:
            self._cleanup_test_environment()
    
    def _setup_test_environment(self):
        """Setup isolated test environment"""
        logger.info("🔧 Setting up test environment...")
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ai_framework_test_"))
        logger.info(f"📁 Test directory: {self.temp_dir}")
        
        # Copy installer package to test directory
        test_installer = self.temp_dir / "ai-enhancement-framework-installer"
        shutil.copytree(self.installer_root, test_installer)
        
        self.test_installer_path = test_installer
        self.test_results["test_environment"] = "PASSED"
    
    def _test_minimal_installation(self):
        """Test minimal installation"""
        logger.info("📦 Testing minimal installation...")
        
        test_destination = self.temp_dir / "minimal_test"
        
        try:
            # Run minimal installation
            result = subprocess.run([
                sys.executable, 
                str(self.test_installer_path / "INSTALL.py"),
                "--type", "minimal",
                "--destination", str(test_destination),
                "--quiet"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Verify minimal components exist
                required_files = [
                    "core/__init__.py",
                    "config/__init__.py",
                    "__init__.py",
                    "requirements.txt",
                    ".ai_framework_config.json"
                ]
                
                missing_files = []
                for file_path in required_files:
                    if not (test_destination / file_path).exists():
                        missing_files.append(file_path)
                
                if not missing_files:
                    logger.info("✅ Minimal installation test passed")
                    self.test_results["minimal_installation"] = "PASSED"
                else:
                    logger.error(f"❌ Missing files in minimal installation: {missing_files}")
                    self.test_results["minimal_installation"] = f"FAILED - Missing: {missing_files}"
            else:
                logger.error(f"❌ Minimal installation failed: {result.stderr}")
                self.test_results["minimal_installation"] = f"FAILED - {result.stderr}"
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Minimal installation timed out")
            self.test_results["minimal_installation"] = "FAILED - Timeout"
        except Exception as e:
            logger.error(f"❌ Minimal installation error: {e}")
            self.test_results["minimal_installation"] = f"FAILED - {str(e)}"
    
    def _test_automated_installation(self):
        """Test automated installation"""
        logger.info("⚡ Testing automated installation...")
        
        test_destination = self.temp_dir / "automated_test"
        
        try:
            # Run automated installation
            result = subprocess.run([
                sys.executable,
                str(self.test_installer_path / "INSTALL.py"), 
                "--type", "automated",
                "--destination", str(test_destination),
                "--quiet"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # Verify installation report exists
                report_file = test_destination / "installation_report.json"
                if report_file.exists():
                    with open(report_file) as f:
                        report = json.load(f)
                    
                    if report.get("success", False):
                        logger.info("✅ Automated installation test passed")
                        self.test_results["automated_installation"] = "PASSED"
                    else:
                        logger.error(f"❌ Installation report shows failure: {report}")
                        self.test_results["automated_installation"] = f"FAILED - Report: {report}"
                else:
                    logger.error("❌ Installation report not found")
                    self.test_results["automated_installation"] = "FAILED - No report"
            else:
                logger.error(f"❌ Automated installation failed: {result.stderr}")
                self.test_results["automated_installation"] = f"FAILED - {result.stderr}"
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Automated installation timed out")
            self.test_results["automated_installation"] = "FAILED - Timeout"
        except Exception as e:
            logger.error(f"❌ Automated installation error: {e}")
            self.test_results["automated_installation"] = f"FAILED - {str(e)}"
    
    def _test_framework_import(self):
        """Test framework import functionality"""
        logger.info("🔍 Testing framework import...")
        
        test_destination = self.temp_dir / "automated_test"
        
        if not test_destination.exists():
            logger.warning("⚠️ Skipping import test - no installation found")
            self.test_results["framework_import"] = "SKIPPED"
            return
        
        try:
            # Test import in isolated Python environment
            test_script = f"""
import sys
sys.path.insert(0, '{test_destination}')

try:
    import ai_enhancement_framework
    print(f"Framework version: {{ai_enhancement_framework.__version__}}")
    
    # Test core imports
    from ai_enhancement_framework.core import CodeAnalyzer
    from ai_enhancement_framework.config import get_module_config
    
    print("✅ Core imports successful")
    exit(0)
except Exception as e:
    print(f"❌ Import failed: {{e}}")
    exit(1)
"""
            
            result = subprocess.run([
                sys.executable, "-c", test_script
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ Framework import test passed")
                self.test_results["framework_import"] = "PASSED"
            else:
                logger.error(f"❌ Framework import failed: {result.stderr}")
                self.test_results["framework_import"] = f"FAILED - {result.stderr}"
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Import test timed out")
            self.test_results["framework_import"] = "FAILED - Timeout"
        except Exception as e:
            logger.error(f"❌ Import test error: {e}")
            self.test_results["framework_import"] = f"FAILED - {str(e)}"
    
    def _test_core_functionality(self):
        """Test core framework functionality"""
        logger.info("🎯 Testing core functionality...")
        
        test_destination = self.temp_dir / "automated_test"
        
        if not test_destination.exists():
            logger.warning("⚠️ Skipping functionality test - no installation found")
            self.test_results["core_functionality"] = "SKIPPED"
            return
        
        try:
            # Test core functionality
            test_script = f"""
import sys
sys.path.insert(0, '{test_destination}')

try:
    import ai_enhancement_framework
    from ai_enhancement_framework.config import get_module_config
    
    # Test configuration
    config = get_module_config()
    print(f"Configuration modules: {{len(config)}}")
    
    # Test basic code analysis
    from ai_enhancement_framework.core import CodeAnalyzer
    
    analyzer = CodeAnalyzer()
    test_code = "def test_function(): return True"
    result = analyzer.analyze_code(test_code)
    
    print(f"Analysis result: {{type(result)}}")
    print("✅ Core functionality test successful")
    exit(0)
    
except Exception as e:
    print(f"❌ Functionality test failed: {{e}}")
    import traceback
    traceback.print_exc()
    exit(1)
"""
            
            result = subprocess.run([
                sys.executable, "-c", test_script
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info("✅ Core functionality test passed")
                self.test_results["core_functionality"] = "PASSED"
            else:
                logger.error(f"❌ Core functionality test failed: {result.stderr}")
                self.test_results["core_functionality"] = f"FAILED - {result.stderr}"
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Functionality test timed out")
            self.test_results["core_functionality"] = "FAILED - Timeout"
        except Exception as e:
            logger.error(f"❌ Functionality test error: {e}")
            self.test_results["core_functionality"] = f"FAILED - {str(e)}"
    
    def _cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info("🧹 Test environment cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup test environment: {e}")
    
    def _generate_test_report(self, success: bool, error: str = None) -> Dict[str, Any]:
        """Generate test report"""
        passed_tests = sum(1 for result in self.test_results.values() if result == "PASSED")
        total_tests = len(self.test_results)
        
        report = {
            "success": success,
            "tests_passed": passed_tests,
            "tests_total": total_tests,
            "pass_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
            "test_results": self.test_results
        }
        
        if error:
            report["error"] = error
        
        # Save test report
        report_file = self.installer_root / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Test report saved: {report_file}")
        logger.info(f"🎯 Test Results: {passed_tests}/{total_tests} passed ({report['pass_rate']})")
        
        return report

def main():
    """Main entry point"""
    logger.info("🧪 AI Enhancement Framework Installation Tester")
    
    tester = InstallationTester()
    results = tester.run_tests()
    
    if results["success"] and results["tests_passed"] == results["tests_total"]:
        print("\n🎉 All installation tests passed!")
        print(f"✅ {results['tests_passed']}/{results['tests_total']} tests successful")
        print("📦 Installation package is ready for deployment")
        sys.exit(0)
    else:
        print(f"\n❌ Installation tests failed")
        print(f"📊 {results['tests_passed']}/{results['tests_total']} tests passed")
        print("🔍 Check test_report.json for details")
        sys.exit(1)

if __name__ == "__main__":
    main() 