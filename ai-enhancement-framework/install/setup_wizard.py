#!/usr/bin/env python3
"""
🧙‍♂️ AI Enhancement Framework - Installation Wizard

Interactive installation wizard for the AI Enhancement Framework with modular component selection.
Guides users through the installation process, helping them choose only the components they need
for optimized performance and reduced dependencies.

Features:
- Interactive module selection
- Dependency checking and validation
- Configuration file generation
- Environment setup assistance
- Docker setup options
- Quick start templates

Author: AI Enhancement Framework
Created: 2025-01-20
License: MIT
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import shutil
import tempfile

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

@dataclass
class ModuleOption:
    """Module installation option"""
    name: str
    key: str
    description: str
    dependencies: List[str]
    optional: bool = True
    size_mb: float = 0.0
    requires_config: bool = False

@dataclass
class InstallationProfile:
    """Installation profile configuration"""
    name: str
    description: str
    modules: List[str]
    setup_docker: bool = False
    create_config: bool = True

class InstallationWizard:
    """AI Enhancement Framework Installation Wizard"""
    
    def __init__(self):
        self.modules = self._define_modules()
        self.profiles = self._define_profiles()
        self.selected_modules = set()
        self.installation_path = Path.cwd()
        self.config_data = {}
        
    def _define_modules(self) -> Dict[str, ModuleOption]:
        """Define available modules"""
        return {
            "code-analysis": ModuleOption(
                name="Code Analysis",
                key="code-analysis",
                description="Advanced code analysis with libcst/astroid integration for hallucination detection",
                dependencies=["libcst>=1.0.0", "astroid>=3.0.0", "black>=23.0.0"],
                size_mb=45.2,
                requires_config=False
            ),
            "database-providers": ModuleOption(
                name="Database Providers",
                key="database-providers", 
                description="Multi-database support (Redis, Neo4j, PostgreSQL, Qdrant)",
                dependencies=["redis>=4.5.0", "neo4j>=5.8.0", "psycopg2-binary>=2.9.0", "qdrant-client>=1.6.0"],
                size_mb=89.7,
                requires_config=True
            ),
            "llm-integration": ModuleOption(
                name="LLM Integration",
                key="llm-integration",
                description="Fine-tuned LLM integration with OpenAI and domain expertise",
                dependencies=["openai>=1.0.0", "anthropic>=0.7.0", "tiktoken>=0.5.0"],
                size_mb=156.3,
                requires_config=True
            ),
            "wolfram-alpha": ModuleOption(
                name="WolframAlpha Pro",
                key="wolfram-alpha",
                description="Mathematical validation and computational intelligence",
                dependencies=["requests>=2.31.0", "sympy>=1.12.0", "numpy>=1.24.0"],
                size_mb=78.9,
                requires_config=True
            ),
            "optimization": ModuleOption(
                name="Code Optimization",
                key="optimization",
                description="Automated code optimization and refactoring tools",
                dependencies=["libcst>=1.0.0", "astroid>=3.0.0"],
                size_mb=32.1,
                requires_config=False
            ),
            "monitoring": ModuleOption(
                name="Health Monitoring",
                key="monitoring",
                description="System health monitoring and performance metrics",
                dependencies=["aiohttp>=3.8.0", "psutil>=5.9.0", "structlog>=23.1.0"],
                size_mb=23.4,
                requires_config=False
            ),
            "docker": ModuleOption(
                name="Docker Integration",
                key="docker",
                description="Docker containerization and orchestration support",
                dependencies=["docker>=6.0.0"],
                size_mb=67.8,
                requires_config=True
            )
        }
    
    def _define_profiles(self) -> Dict[str, InstallationProfile]:
        """Define installation profiles"""
        return {
            "minimal": InstallationProfile(
                name="Minimal",
                description="Core framework only (task orchestrator, basic analysis)",
                modules=[],
                setup_docker=False,
                create_config=True
            ),
            "developer": InstallationProfile(
                name="Developer",
                description="Code analysis + optimization tools for development",
                modules=["code-analysis", "optimization", "monitoring"],
                setup_docker=False,
                create_config=True
            ),
            "ai-enhanced": InstallationProfile(
                name="AI Enhanced",
                description="LLM integration + WolframAlpha for AI-powered development",
                modules=["llm-integration", "wolfram-alpha", "code-analysis"],
                setup_docker=False,
                create_config=True
            ),
            "enterprise": InstallationProfile(
                name="Enterprise",
                description="Full database support + monitoring for production use",
                modules=["database-providers", "monitoring", "docker", "llm-integration"],
                setup_docker=True,
                create_config=True
            ),
            "full": InstallationProfile(
                name="Full Installation",
                description="All modules enabled for complete functionality",
                modules=list(self.modules.keys()),
                setup_docker=True,
                create_config=True
            )
        }
    
    def run(self) -> bool:
        """Run the installation wizard"""
        try:
            self._print_welcome()
            
            # Check system requirements
            if not self._check_system_requirements():
                return False
            
            # Choose installation mode
            installation_mode = self._choose_installation_mode()
            
            if installation_mode == "profile":
                # Use predefined profile
                profile = self._choose_profile()
                self.selected_modules = set(profile.modules)
                self.config_data["docker_setup"] = profile.setup_docker
            else:
                # Custom module selection
                self._select_custom_modules()
                self.config_data["docker_setup"] = self._ask_docker_setup()
            
            # Show installation summary
            if not self._show_installation_summary():
                return False
            
            # Perform installation
            return self._perform_installation()
            
        except KeyboardInterrupt:
            self._print_error("\n❌ Installation cancelled by user")
            return False
        except Exception as e:
            self._print_error(f"\n❌ Installation failed: {e}")
            return False
    
    def _print_welcome(self):
        """Print welcome message"""
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                "🤖 AI Enhancement Framework\n"
                "Installation Wizard\n\n"
                "Welcome! This wizard will help you install and configure\n"
                "the AI Enhancement Framework with only the components you need.",
                title="Welcome",
                border_style="blue"
            ))
        else:
            print("="*60)
            print("🤖 AI Enhancement Framework - Installation Wizard")
            print("="*60)
            print("Welcome! This wizard will help you install and configure")
            print("the AI Enhancement Framework with only the components you need.")
            print("="*60)
    
    def _check_system_requirements(self) -> bool:
        """Check system requirements"""
        if RICH_AVAILABLE:
            console.print("\n🔍 Checking system requirements...")
        else:
            print("\n🔍 Checking system requirements...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            self._print_error(f"❌ Python 3.8+ required (found {python_version.major}.{python_version.minor})")
            return False
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self._print_error("❌ pip not found - please install pip")
            return False
        
        if RICH_AVAILABLE:
            console.print("✅ System requirements satisfied")
        else:
            print("✅ System requirements satisfied")
        
        return True
    
    def _choose_installation_mode(self) -> str:
        """Choose installation mode"""
        if RICH_AVAILABLE:
            console.print("\n📦 Choose installation mode:")
            console.print("1. Quick Profile - Use predefined module combinations")
            console.print("2. Custom Selection - Choose individual modules")
            
            choice = Prompt.ask("Select mode", choices=["1", "2"], default="1")
        else:
            print("\n📦 Choose installation mode:")
            print("1. Quick Profile - Use predefined module combinations")
            print("2. Custom Selection - Choose individual modules")
            choice = input("Select mode [1]: ").strip() or "1"
        
        return "profile" if choice == "1" else "custom"
    
    def _choose_profile(self) -> InstallationProfile:
        """Choose installation profile"""
        if RICH_AVAILABLE:
            table = Table(title="Installation Profiles")
            table.add_column("Option", style="cyan", no_wrap=True)
            table.add_column("Name", style="green")
            table.add_column("Description", style="white")
            table.add_column("Modules", style="yellow")
            
            for i, (key, profile) in enumerate(self.profiles.items(), 1):
                modules_str = ", ".join(profile.modules) if profile.modules else "Core only"
                table.add_row(str(i), profile.name, profile.description, modules_str)
            
            console.print(table)
            choice = Prompt.ask("Select profile", choices=[str(i) for i in range(1, len(self.profiles)+1)], default="2")
        else:
            print("\n📋 Installation Profiles:")
            for i, (key, profile) in enumerate(self.profiles.items(), 1):
                modules_str = ", ".join(profile.modules) if profile.modules else "Core only"
                print(f"{i}. {profile.name}: {profile.description}")
                print(f"   Modules: {modules_str}")
            
            choice = input("Select profile [2]: ").strip() or "2"
        
        profile_keys = list(self.profiles.keys())
        selected_key = profile_keys[int(choice) - 1]
        return self.profiles[selected_key]
    
    def _select_custom_modules(self):
        """Select custom modules"""
        if RICH_AVAILABLE:
            console.print("\n🔧 Select modules to install:")
            
            table = Table(title="Available Modules")
            table.add_column("Option", style="cyan", no_wrap=True)
            table.add_column("Module", style="green")
            table.add_column("Description", style="white")
            table.add_column("Size", style="yellow")
            
            for i, (key, module) in enumerate(self.modules.items(), 1):
                table.add_row(str(i), module.name, module.description, f"{module.size_mb:.1f} MB")
            
            console.print(table)
            
            selections = Prompt.ask("Select modules (comma-separated, e.g., 1,3,5)").split(",")
        else:
            print("\n🔧 Select modules to install:")
            for i, (key, module) in enumerate(self.modules.items(), 1):
                print(f"{i}. {module.name}: {module.description} ({module.size_mb:.1f} MB)")
            
            selections = input("Select modules (comma-separated, e.g., 1,3,5): ").split(",")
        
        module_keys = list(self.modules.keys())
        for selection in selections:
            try:
                idx = int(selection.strip()) - 1
                if 0 <= idx < len(module_keys):
                    self.selected_modules.add(module_keys[idx])
            except ValueError:
                continue
    
    def _ask_docker_setup(self) -> bool:
        """Ask about Docker setup"""
        if RICH_AVAILABLE:
            return Confirm.ask("🐳 Set up Docker configuration?", default=False)
        else:
            response = input("🐳 Set up Docker configuration? [y/N]: ").strip().lower()
            return response in ['y', 'yes']
    
    def _show_installation_summary(self) -> bool:
        """Show installation summary and confirm"""
        total_size = sum(self.modules[module].size_mb for module in self.selected_modules)
        
        if RICH_AVAILABLE:
            table = Table(title="Installation Summary")
            table.add_column("Component", style="green")
            table.add_column("Status", style="cyan")
            table.add_column("Size", style="yellow")
            
            table.add_row("Core Framework", "✅ Included", "12.3 MB")
            
            for module_key in self.selected_modules:
                module = self.modules[module_key]
                table.add_row(module.name, "✅ Selected", f"{module.size_mb:.1f} MB")
            
            if self.config_data.get("docker_setup"):
                table.add_row("Docker Setup", "✅ Enabled", "~150 MB")
            
            table.add_row("Total Download", "", f"~{total_size + 12.3:.1f} MB")
            
            console.print(table)
            return Confirm.ask("\n🚀 Proceed with installation?", default=True)
        else:
            print("\n📋 Installation Summary:")
            print("Core Framework: ✅ Included (12.3 MB)")
            
            for module_key in self.selected_modules:
                module = self.modules[module_key]
                print(f"{module.name}: ✅ Selected ({module.size_mb:.1f} MB)")
            
            if self.config_data.get("docker_setup"):
                print("Docker Setup: ✅ Enabled (~150 MB)")
            
            print(f"Total Download: ~{total_size + 12.3:.1f} MB")
            
            response = input("\n🚀 Proceed with installation? [Y/n]: ").strip().lower()
            return response not in ['n', 'no']
    
    def _perform_installation(self) -> bool:
        """Perform the actual installation"""
        try:
            # Build pip install command
            install_cmd = [sys.executable, "-m", "pip", "install", "ai-enhancement-framework"]
            
            if self.selected_modules:
                modules_str = ",".join(self.selected_modules)
                install_cmd[-1] += f"[{modules_str}]"
            
            if RICH_AVAILABLE:
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Installing AI Enhancement Framework...", total=None)
                    
                    result = subprocess.run(install_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        progress.update(task, description="✅ Installation completed!")
                    else:
                        progress.update(task, description="❌ Installation failed!")
                        console.print(f"Error: {result.stderr}")
                        return False
            else:
                print("🔄 Installing AI Enhancement Framework...")
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Installation completed!")
                else:
                    print("❌ Installation failed!")
                    print(f"Error: {result.stderr}")
                    return False
            
            # Generate configuration
            self._generate_configuration()
            
            # Create project template
            self._create_project_template()
            
            # Show completion message
            self._show_completion_message()
            
            return True
            
        except Exception as e:
            self._print_error(f"Installation failed: {e}")
            return False
    
    def _generate_configuration(self):
        """Generate configuration files"""
        config = {
            "ai_enhancement_framework": {
                "version": "2.1.0",
                "modules": {
                    module: {"enabled": module in self.selected_modules}
                    for module in self.modules.keys()
                }
            }
        }
        
        # Add module-specific configurations
        if "database-providers" in self.selected_modules:
            config["database_providers"] = {
                "redis": {"host": "localhost", "port": 6379},
                "neo4j": {"uri": "bolt://localhost:7687", "user": "neo4j"},
                "postgresql": {"host": "localhost", "port": 5432},
                "qdrant": {"host": "localhost", "port": 6333}
            }
        
        if "llm-integration" in self.selected_modules:
            config["llm_integration"] = {
                "openai_api_key": "your-openai-api-key-here",
                "model": "gpt-4"
            }
        
        if "wolfram-alpha" in self.selected_modules:
            config["wolfram_integration"] = {
                "app_id": "your-wolfram-app-id-here"
            }
        
        # Save configuration
        config_path = self.installation_path / ".ai_framework_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        if RICH_AVAILABLE:
            console.print(f"📝 Configuration saved to: {config_path}")
        else:
            print(f"📝 Configuration saved to: {config_path}")
    
    def _create_project_template(self):
        """Create project template files"""
        # Create example usage script
        example_script = '''#!/usr/bin/env python3
"""
AI Enhancement Framework - Quick Start Example
"""

from ai_enhancement_framework import get_framework_capabilities
from ai_enhancement_framework.config import get_module_config

def main():
    print("🤖 AI Enhancement Framework - Quick Start")
    print("=" * 50)
    
    # Show framework capabilities
    capabilities = get_framework_capabilities()
    print(f"Available capabilities: {len([c for c in capabilities.values() if c])}")
    
    # Show module configuration
    config = get_module_config()
    summary = config.get_configuration_summary()
    print(f"Enabled modules: {summary['enabled_count']}/{summary['total_modules']}")
    
    print("\\n✅ Framework is ready to use!")
    print("📚 Check the documentation for more examples.")

if __name__ == "__main__":
    main()
'''
        
        example_path = self.installation_path / "ai_framework_example.py"
        with open(example_path, "w") as f:
            f.write(example_script)
        
        if RICH_AVAILABLE:
            console.print(f"📄 Example script created: {example_path}")
        else:
            print(f"📄 Example script created: {example_path}")
    
    def _show_completion_message(self):
        """Show installation completion message"""
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                "🎉 Installation Complete!\n\n"
                "Next steps:\n"
                "1. Review configuration: .ai_framework_config.json\n"
                "2. Run example: python ai_framework_example.py\n"
                "3. Check module status: ai-modules status\n"
                "4. Read documentation: https://ai-enhancement-framework.readthedocs.io\n\n"
                "Happy coding! 🚀",
                title="Success",
                border_style="green"
            ))
        else:
            print("\n" + "="*60)
            print("🎉 Installation Complete!")
            print("="*60)
            print("Next steps:")
            print("1. Review configuration: .ai_framework_config.json")
            print("2. Run example: python ai_framework_example.py")
            print("3. Check module status: ai-modules status")
            print("4. Read documentation: https://ai-enhancement-framework.readthedocs.io")
            print("\nHappy coding! 🚀")
            print("="*60)
    
    def _print_error(self, message: str):
        """Print error message"""
        if RICH_AVAILABLE:
            console.print(message, style="red")
        else:
            print(message)

def main():
    """Main entry point"""
    wizard = InstallationWizard()
    success = wizard.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
