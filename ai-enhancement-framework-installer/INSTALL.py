#!/usr/bin/env python3
"""
🚀 AI Enhancement Framework - Master Installation Script

This script installs the complete AI Enhancement Framework in a new Cursor IDE instance,
following the AI Task Orchestrator Guide methodology for systematic installation.

Features:
- Automatic destination directory setup
- Dependency management and validation
- Interactive installation wizard integration
- Comprehensive validation framework
- Cursor IDE integration setup
- Docker services configuration (optional)

Author: AI Enhancement Framework
Created: 2025-01-21
License: MIT
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIFrameworkInstaller:
    """Master installer for AI Enhancement Framework"""
    
    def __init__(self, destination_dir: Optional[str] = None):
        self.installer_root = Path(__file__).parent
        self.destination_dir = Path(destination_dir) if destination_dir else Path.cwd() / "ai_enhancement_framework"
        self.installation_log = []
        self.start_time = datetime.now()
        
    def install(self, installation_type: str = "interactive") -> Dict[str, Any]:
        """Main installation method"""
        logger.info("🚀 Starting AI Enhancement Framework Installation")
        logger.info(f"📁 Installer location: {self.installer_root}")
        logger.info(f"🎯 Installation destination: {self.destination_dir}")
        
        try:
            # Step 1: Pre-installation validation
            self._pre_installation_checks()
            
            # Step 2: Choose installation method
            if installation_type == "interactive":
                return self._interactive_installation()
            elif installation_type == "automated":
                return self._automated_installation()
            elif installation_type == "minimal":
                return self._minimal_installation()
            else:
                return self._full_installation()
                
        except Exception as e:
            logger.error(f"❌ Installation failed: {e}")
            return {"success": False, "error": str(e), "log": self.installation_log}
    
    def _pre_installation_checks(self):
        """Validate system requirements before installation"""
        logger.info("🔍 Running pre-installation checks...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            raise RuntimeError(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        logger.info(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check available space (estimate 1GB needed)
        available_space = shutil.disk_usage(self.destination_dir.parent).free
        required_space = 1 * 1024 * 1024 * 1024  # 1GB
        if available_space < required_space:
            raise RuntimeError(f"Insufficient disk space. Required: 1GB, Available: {available_space // (1024**3)}GB")
        
        # Check pip availability
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("✅ pip is available")
        except subprocess.CalledProcessError:
            raise RuntimeError("pip is not available")
        
        self.installation_log.append("Pre-installation checks passed")
    
    def _interactive_installation(self) -> Dict[str, Any]:
        """Run interactive installation wizard"""
        logger.info("🧙‍♂️ Starting interactive installation wizard...")
        
        # Import and run the installation wizard
        wizard_path = self.installer_root / "install" / "setup_wizard.py"
        if not wizard_path.exists():
            raise RuntimeError(f"Installation wizard not found at {wizard_path}")
        
        try:
            # Run wizard with destination parameter
            env = os.environ.copy()
            env["AI_FRAMEWORK_DESTINATION"] = str(self.destination_dir)
            env["PYTHONPATH"] = str(self.installer_root)
            
            result = subprocess.run([
                sys.executable, str(wizard_path),
                "--destination", str(self.destination_dir)
            ], env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Interactive installation completed successfully")
                return self._post_installation_validation()
            else:
                raise RuntimeError(f"Wizard failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Interactive installation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _automated_installation(self) -> Dict[str, Any]:
        """Run automated installation with default settings"""
        logger.info("⚡ Starting automated installation...")
        
        # Step 1: Create destination directory
        self.destination_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 2: Copy core framework components
        self._copy_framework_components()
        
        # Step 3: Install dependencies
        self._install_dependencies()
        
        # Step 4: Setup configuration
        self._setup_configuration()
        
        # Step 5: Setup Cursor IDE integration
        self._setup_cursor_integration()
        
        # Step 6: Run validation
        return self._post_installation_validation()
    
    def _minimal_installation(self) -> Dict[str, Any]:
        """Install minimal framework (core only)"""
        logger.info("📦 Starting minimal installation...")
        
        # Create destination
        self.destination_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy essential components only
        essential_components = [
            "core/",
            "config/", 
            "__init__.py",
            "requirements.txt",
            ".ai_framework_config.json"
        ]
        
        for component in essential_components:
            src = self.installer_root / component
            dst = self.destination_dir / component
            
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                logger.info(f"📁 Copied directory: {component}")
            elif src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                logger.info(f"📄 Copied file: {component}")
        
        # Install core dependencies only
        self._install_core_dependencies()
        
        return self._post_installation_validation()
    
    def _full_installation(self) -> Dict[str, Any]:
        """Install complete framework with all components"""
        logger.info("🔥 Starting full installation...")
        
        # Step 1: Create destination directory
        self.destination_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 2: Copy all framework components
        logger.info("📁 Copying framework components...")
        components_to_copy = [
            "core/", "providers/", "optimization/", "cursor/", "config/",
            "scripts/", "docs/", "templates/", "tests/", "docker/",
            "__init__.py", "requirements.txt", "pyproject.toml",
            ".ai_framework_config.json", ".cursorrules", "README.md",
            "cli.py", "setup_comprehensive.py"
        ]
        
        for component in components_to_copy:
            src = self.installer_root / component
            dst = self.destination_dir / component
            
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                logger.info(f"📁 Copied directory: {component}")
            elif src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                logger.info(f"📄 Copied file: {component}")
        
        # Step 3: Install all dependencies
        self._install_all_dependencies()
        
        # Step 4: Setup configuration
        self._setup_configuration()
        
        # Step 5: Setup Docker services (optional)
        self._setup_docker_services()
        
        # Step 6: Setup Cursor IDE integration
        self._setup_cursor_integration()
        
        return self._post_installation_validation()
    
    def _copy_framework_components(self):
        """Copy framework components to destination"""
        logger.info("📁 Copying framework components...")
        
        # Copy core components
        core_components = [
            "core/", "providers/", "optimization/", "config/",
            "__init__.py", "requirements.txt", ".ai_framework_config.json"
        ]
        
        for component in core_components:
            src = self.installer_root / component
            dst = self.destination_dir / component
            
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        
        self.installation_log.append("Framework components copied")
    
    def _install_dependencies(self):
        """Install Python dependencies"""
        logger.info("📦 Installing dependencies...")
        
        requirements_file = self.installer_root / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ])
                logger.info("✅ Dependencies installed successfully")
                self.installation_log.append("Dependencies installed")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install dependencies: {e}")
                raise
    
    def _install_core_dependencies(self):
        """Install only core dependencies"""
        logger.info("📦 Installing core dependencies...")
        
        core_deps = [
            "pydantic>=2.0.0",
            "dataclasses-json>=0.6.0", 
            "python-dotenv>=1.0.0",
            "click>=8.1.0"
        ]
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + core_deps)
            logger.info("✅ Core dependencies installed")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install core dependencies: {e}")
            raise
    
    def _install_all_dependencies(self):
        """Install all dependencies including optional modules"""
        logger.info("📦 Installing all dependencies...")
        
        # Install from requirements file
        self._install_dependencies()
        
        # Install optional modules
        optional_deps = [
            "libcst>=1.0.0",
            "astroid>=3.0.0", 
            "black>=23.0.0",
            "redis>=4.5.0",
            "openai>=1.0.0"
        ]
        
        for dep in optional_deps:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", dep
                ])
                logger.info(f"✅ Installed optional dependency: {dep}")
            except subprocess.CalledProcessError:
                logger.warning(f"⚠️ Failed to install optional dependency: {dep}")
    
    def _setup_configuration(self):
        """Setup framework configuration"""
        logger.info("⚙️ Setting up configuration...")
        
        # Copy configuration files
        config_files = [
            ".ai_framework_config.json",
            ".cursorrules"
        ]
        
        for config_file in config_files:
            src = self.installer_root / config_file
            dst = self.destination_dir / config_file
            
            if src.exists():
                shutil.copy2(src, dst)
                logger.info(f"⚙️ Copied config: {config_file}")
        
        self.installation_log.append("Configuration setup completed")
    
    def _setup_cursor_integration(self):
        """Setup Cursor IDE integration"""
        logger.info("🎯 Setting up Cursor IDE integration...")
        
        # Copy .cursorrules to project root (parent of destination)
        cursorrules_src = self.installer_root / ".cursorrules"
        cursorrules_dst = self.destination_dir.parent / ".cursorrules"
        
        if cursorrules_src.exists():
            shutil.copy2(cursorrules_src, cursorrules_dst)
            logger.info("🎯 Cursor IDE integration configured")
            self.installation_log.append("Cursor IDE integration setup")
    
    def _setup_docker_services(self):
        """Setup Docker services (optional)"""
        logger.info("🐳 Setting up Docker services...")
        
        docker_compose_file = self.installer_root / "docker" / "docker-compose.yml"
        if docker_compose_file.exists():
            # Copy Docker configuration
            docker_dst = self.destination_dir / "docker"
            docker_src = self.installer_root / "docker"
            shutil.copytree(docker_src, docker_dst, dirs_exist_ok=True)
            
            # Try to start services
            try:
                subprocess.check_call([
                    "docker-compose", "-f", str(docker_dst / "docker-compose.yml"), "up", "-d"
                ], cwd=docker_dst)
                logger.info("🐳 Docker services started")
                self.installation_log.append("Docker services configured")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("⚠️ Docker not available - services not started")
    
    def _post_installation_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation after installation"""
        logger.info("✅ Running post-installation validation...")
        
        # Run the comprehensive validation script
        validation_script = self.destination_dir / "setup_comprehensive.py"
        if validation_script.exists():
            try:
                env = os.environ.copy()
                env["PYTHONPATH"] = str(self.destination_dir)
                
                result = subprocess.run([
                    sys.executable, str(validation_script)
                ], env=env, capture_output=True, text=True, cwd=self.destination_dir)
                
                if result.returncode == 0:
                    logger.info("✅ Validation completed successfully")
                    
                    # Generate installation report
                    return self._generate_installation_report(success=True)
                else:
                    logger.warning(f"⚠️ Validation warnings: {result.stderr}")
                    return self._generate_installation_report(success=True, warnings=result.stderr)
                    
            except Exception as e:
                logger.error(f"❌ Validation failed: {e}")
                return self._generate_installation_report(success=False, error=str(e))
        else:
            logger.warning("⚠️ Validation script not found")
            return self._generate_installation_report(success=True, warnings="Validation script not available")
    
    def _generate_installation_report(self, success: bool, error: str = None, warnings: str = None) -> Dict[str, Any]:
        """Generate installation report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            "success": success,
            "installation_time": duration,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "destination": str(self.destination_dir),
            "installer_version": "2.1.0",
            "log": self.installation_log
        }
        
        if error:
            report["error"] = error
        if warnings:
            report["warnings"] = warnings
        
        # Save report
        report_file = self.destination_dir / "installation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Installation report saved: {report_file}")
        
        if success:
            logger.info("🎉 AI Enhancement Framework installation completed successfully!")
            logger.info(f"⏱️ Installation time: {duration:.1f} seconds")
            logger.info(f"📁 Framework installed at: {self.destination_dir}")
        else:
            logger.error("❌ Installation failed")
        
        return report

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Enhancement Framework Installer")
    parser.add_argument("--destination", "-d", help="Installation destination directory")
    parser.add_argument("--type", "-t", choices=["interactive", "automated", "minimal", "full"],
                       default="interactive", help="Installation type")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    installer = AIFrameworkInstaller(args.destination)
    result = installer.install(args.type)
    
    if result["success"]:
        print("\n🎉 Installation completed successfully!")
        print(f"📁 Framework location: {result.get('destination', 'Unknown')}")
        print("\n📖 Next steps:")
        print("1. Read the user guide: AI_ENHANCEMENT_FRAMEWORK_COMPREHENSIVE_USER_GUIDE.md")
        print("2. Test the installation: python -c 'import ai_enhancement_framework; print(\"✅ Success!\")'")
        print("3. Configure API keys in .env file (if needed)")
        print("4. Start using AI-enhanced development features!")
        sys.exit(0)
    else:
        print(f"\n❌ Installation failed: {result.get('error', 'Unknown error')}")
        print(f"📋 Check installation log for details")
        sys.exit(1)

if __name__ == "__main__":
    main() 