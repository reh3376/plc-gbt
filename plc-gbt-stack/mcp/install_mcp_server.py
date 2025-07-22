#!/usr/bin/env python3
"""
PLC-GBT MCP Server Installation Script for Cursor IDE
Following AI Task Orchestrator Guide Methodology

This script installs and configures the PLC-GBT MCP server for Cursor IDE integration.
Provides automated setup with minimal user intervention.

Author: AI Task Orchestrator
Created: 2025-07-21
Phase: 27.3 - MCP Server Installation
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerInstaller:
    """Installer for PLC-GBT MCP Server with Cursor IDE integration"""
    
    def __init__(self):
        self.system = platform.system()
        self.current_dir = Path(__file__).parent
        self.plc_gbt_root = self.current_dir.parent
        self.cursor_config_paths = self._get_cursor_config_paths()
        
    def _get_cursor_config_paths(self) -> Dict[str, Path]:
        """Get Cursor IDE configuration paths for different operating systems"""
        home = Path.home()
        
        if self.system == "Darwin":  # macOS
            return {
                "mcp_config": home / "Library/Application Support/Cursor/User/globalStorage",
                "settings": home / "Library/Application Support/Cursor/User",
                "mcp_file": "mcp-servers.json"
            }
        elif self.system == "Linux":
            return {
                "mcp_config": home / ".config/Cursor/User/globalStorage",
                "settings": home / ".config/Cursor/User",
                "mcp_file": "mcp-servers.json"
            }
        elif self.system == "Windows":
            appdata = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
            return {
                "mcp_config": appdata / "Cursor/User/globalStorage",
                "settings": appdata / "Cursor/User",
                "mcp_file": "mcp-servers.json"
            }
        else:
            raise OSError(f"Unsupported operating system: {self.system}")
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info("🔍 Checking dependencies...")
        
        # Check Python version
        if sys.version_info < (3, 9):
            logger.error(f"❌ Python 3.9+ required, found {sys.version}")
            return False
        logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")
        
        # Check required packages
        required_packages = ["aiohttp"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✅ {package} installed")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"⚠️  {package} not found")
        
        if missing_packages:
            logger.info("📦 Installing missing packages...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--user"
                ] + missing_packages)
                logger.info("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install dependencies: {e}")
                return False
        
        return True
    
    def test_mcp_server(self) -> bool:
        """Test the MCP server functionality"""
        logger.info("🧪 Testing MCP server...")
        
        try:
            # Test the simplified MCP server
            result = subprocess.run([
                sys.executable, 
                str(self.current_dir / "simple_mcp_server.py")
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "All tests passed" in result.stdout:
                logger.info("✅ MCP server test passed")
                return True
            else:
                logger.error(f"❌ MCP server test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ MCP server test timed out")
            return False
        except Exception as e:
            logger.error(f"❌ MCP server test error: {e}")
            return False
    
    def create_cursor_config(self) -> bool:
        """Create Cursor IDE MCP configuration"""
        logger.info("⚙️ Creating Cursor IDE MCP configuration...")
        
        try:
            # Ensure config directory exists
            self.cursor_config_paths["mcp_config"].mkdir(parents=True, exist_ok=True)
            
            # Load existing MCP configuration or create new
            mcp_config_file = self.cursor_config_paths["mcp_config"] / self.cursor_config_paths["mcp_file"]
            
            if mcp_config_file.exists():
                with open(mcp_config_file, 'r') as f:
                    mcp_config = json.load(f)
                logger.info("📄 Found existing MCP configuration")
            else:
                mcp_config = {"mcpServers": {}}
                logger.info("📄 Creating new MCP configuration")
            
            # Add PLC-GBT MCP server configuration
            plc_gbt_config = {
                "command": "python3",
                "args": ["__main__.py", "stdio"],
                "cwd": str(self.current_dir),
                "env": {
                    "PYTHONPATH": f"{str(self.plc_gbt_stack)}:{str(self.plc_gbt_root)}",
                    "PLC_GBT_API_URL": "http://localhost:8000/api/v1",
                    "MCP_SERVER_NAME": "plc-gbt-industrial-automation",
                    "MCP_LOG_LEVEL": "INFO"
                },
                "description": "PLC-GBT Industrial Automation MCP Server - Natural Language Interface to Industrial Control Systems",
                "capabilities": ["tools", "prompts", "resources"],
                "version": "1.0.0"
            }
            
            mcp_config["mcpServers"]["plc-gbt-industrial-automation"] = plc_gbt_config
            
            # Write updated configuration
            with open(mcp_config_file, 'w') as f:
                json.dump(mcp_config, f, indent=2)
            
            logger.info(f"✅ MCP configuration written to: {mcp_config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create Cursor configuration: {e}")
            return False
    
    def create_project_cursorrules(self) -> bool:
        """Create or update .cursorrules for the project"""
        logger.info("📝 Creating project .cursorrules configuration...")
        
        try:
            cursorrules_file = self.plc_gbt_root / ".cursorrules"
            
            cursorrules_content = """# PLC-GBT Industrial Automation Project - Cursor Rules
# AI Enhancement Framework Configuration

# Core Framework Configuration
ai_framework:
  enabled: true
  mode: "development"
  version: "1.0.0"

# Project Configuration
project:
  name: "plc-gbt-industrial-automation"
  type: "industrial_automation"
  complexity: "extensive"
  domain: "industrial_control"
  
# AI Assistant Behavior
assistant:
  task_orchestrator:
    enabled: true
    analysis_depth: "comprehensive"
    methodical_approach: true
    domain_expertise: "industrial_automation"
  
  memory:
    enabled: true
    project_scoped: true
    cross_session_persistence: true
    auto_cleanup: true
  
  code_analysis:
    enabled: true
    real_time: true
    validation_on_save: true
    hallucination_detection: true
    safety_analysis: true
    performance_analysis: true

# Industrial Automation Standards
standards:
  code_quality:
    type_hints: "required"
    docstrings: "required"
    test_coverage: 95
    complexity_limit: 10
  
  industrial_compliance:
    safety_standards: ["IEC 61511", "ISA 84"]
    control_standards: ["IEC 61131", "ISA 88"]
    cybersecurity: ["IEC 62443"]
  
  documentation:
    auto_generate: true
    mermaid_diagrams: true
    api_documentation: true
    safety_documentation: true

# MCP Integration
mcp_integration:
  enabled: true
  server_name: "plc-gbt-industrial-automation"
  natural_language_interface: true
  real_time_monitoring: true
  
# Industrial Features
industrial_features:
  control_loop_management: true
  plc_integration: true
  safety_systems: true
  process_optimization: true
  predictive_maintenance: true
  
# Framework Integration
framework:
  ai_enhancement: true
  auto_analysis: true
  validation_on_save: true
  memory_persistence: true
  context_awareness: true
  industrial_expertise: true
"""
            
            with open(cursorrules_file, 'w') as f:
                f.write(cursorrules_content)
            
            logger.info(f"✅ Created .cursorrules: {cursorrules_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create .cursorrules: {e}")
            return False
    
    def create_vscode_settings(self) -> bool:
        """Create VSCode/Cursor workspace settings"""
        logger.info("⚙️ Creating workspace settings...")
        
        try:
            vscode_dir = self.plc_gbt_root / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            settings_file = vscode_dir / "settings.json"
            
            settings = {
                "ai.framework.enabled": True,
                "ai.framework.config_file": ".cursorrules",
                "ai.framework.auto_init": True,
                "ai.framework.project_type": "industrial_automation",
                "mcp.enabled": True,
                "mcp.server.plc_gbt": {
                    "enabled": True,
                    "auto_start": True
                },
                "files.associations": {
                    "*.cursorrules": "yaml",
                    "*.ai-config": "json"
                },
                "python.defaultInterpreterPath": f"{sys.executable}",
                "python.testing.pytestEnabled": True,
                "python.linting.enabled": True,
                "python.linting.flake8Enabled": True,
                "python.formatting.provider": "black",
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": True,
                    "source.fixAll": True
                }
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info(f"✅ Created workspace settings: {settings_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create workspace settings: {e}")
            return False
    
    def run_installation(self) -> bool:
        """Run the complete installation process"""
        logger.info("🚀 Starting PLC-GBT MCP Server Installation for Cursor IDE")
        logger.info("=" * 60)
        
        steps = [
            ("Checking dependencies", self.check_dependencies),
            ("Testing MCP server", self.test_mcp_server),
            ("Creating Cursor MCP configuration", self.create_cursor_config),
            ("Creating project .cursorrules", self.create_project_cursorrules),
            ("Creating workspace settings", self.create_vscode_settings)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            if not step_func():
                logger.error(f"❌ Installation failed at: {step_name}")
                return False
            logger.info(f"✅ {step_name} completed")
        
        return True
    
    def print_installation_summary(self):
        """Print installation summary and next steps"""
        logger.info("\n" + "=" * 60)
        logger.info("🎉 PLC-GBT MCP Server Installation Complete!")
        logger.info("=" * 60)
        
        print(f"""
📋 Installation Summary:
   • MCP Server: ✅ Installed and tested
   • Dependencies: ✅ All requirements met
   • Cursor Config: ✅ MCP server registered
   • Project Config: ✅ .cursorrules created
   • Workspace: ✅ VSCode settings configured

🚀 Next Steps:
   1. Restart Cursor IDE completely
   2. Open this project in Cursor
   3. Look for "MCP Tools" in the sidebar or command palette
   4. Verify "plc-gbt-industrial-automation" appears in MCP servers
   5. Test with: "Create a temperature control loop"

📁 Configuration Files:
   • MCP Config: {self.cursor_config_paths['mcp_config']}/{self.cursor_config_paths['mcp_file']}
   • Project Rules: {self.plc_gbt_root}/.cursorrules
   • Workspace: {self.plc_gbt_root}/.vscode/settings.json

🛠️ Available Capabilities:
   • 8 Industrial Automation Tools
   • 4 Expert Assistance Prompts
   • 5 Knowledge Resources
   • Natural Language Control Loop Creation
   • Real-time PLC Integration
   • AI-Powered PID Tuning
   • Safety System Validation

📚 Documentation:
   • Integration Guide: {self.current_dir}/cursor_integration_guide.md
   • API Reference: http://localhost:8000/api/v1/docs
   • Project Docs: {self.plc_gbt_root}/docs/

💡 Tips:
   • Use natural language: "Create a cascade control loop"
   • Ask for help: "How do I tune a PID controller?"
   • Get status: "What's the current system status?"
   • Browse resources: "Show me control loop schemas"

🔧 Troubleshooting:
   • If MCP server doesn't appear, check Cursor logs
   • Ensure Python 3.9+ is available in PATH
   • Verify all files are in correct locations
   • Restart Cursor IDE after installation
""")

def main():
    """Main installation function"""
    try:
        installer = MCPServerInstaller()
        
        if installer.run_installation():
            installer.print_installation_summary()
            return 0
        else:
            logger.error("❌ Installation failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Installation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Installation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 