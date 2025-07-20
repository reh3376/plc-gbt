#!/usr/bin/env python3
"""
🛠️ AI Enhancement Framework - Module Management CLI

Command-line interface for managing framework modules and configuration.
Provides easy enable/disable functionality with validation and reporting.

Usage:
    python -m ai_enhancement_framework.cli_modules status
    python -m ai_enhancement_framework.cli_modules enable wolfram_integration llm_integration
    python -m ai_enhancement_framework.cli_modules disable database_providers
    python -m ai_enhancement_framework.cli_modules validate
    python -m ai_enhancement_framework.cli_modules reset

Author: AI Enhancement Framework
Created: 2025-01-20
License: MIT
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

try:
    from .config import get_module_config, is_module_enabled
    from .core.module_loader import get_module_loader
    from . import print_module_status, enable_features, disable_features
except ImportError:
    # Fallback for direct execution
    try:
        from config import get_module_config, is_module_enabled
        from core.module_loader import get_module_loader
        # Import functions directly from ai_enhancement_framework if available
        try:
            from ai_enhancement_framework import print_module_status, enable_features, disable_features
        except ImportError:
            print_module_status = None
            enable_features = None
            disable_features = None
    except ImportError:
        # Last fallback
        from ai_enhancement_framework.config import get_module_config, is_module_enabled
        from ai_enhancement_framework.core.module_loader import get_module_loader
        try:
            from ai_enhancement_framework import print_module_status, enable_features, disable_features
        except ImportError:
            print_module_status = None
            enable_features = None
            disable_features = None

# Local implementations for fallback
def _local_print_module_status():
    """Local implementation of print_module_status"""
    config = get_module_config()
    summary = config.get_configuration_summary()
    
    print(f"\n🚀 AI Enhancement Framework")
    print(f"📊 Modules: {summary['enabled_count']}/{summary['total_modules']} enabled")
    print(f"🔧 Configuration: {config.config_path}")
    
    print(f"\n✅ Enabled Modules ({summary['enabled_count']}):")
    for module in summary['enabled_modules']:
        module_info = config.get_module_info(module)
        print(f"  • {module}: {module_info['description']}")
    
    if summary['disabled_modules']:
        print(f"\n❌ Disabled Modules ({summary['disabled_count']}):")
        for module in summary['disabled_modules']:
            module_info = config.get_module_info(module)
            print(f"  • {module}: {module_info['description']}")
    
    if not summary['dependency_validation']['valid']:
        print(f"\n⚠️  Dependency Issues:")
        for issue in summary['dependency_validation']['issues']:
            print(f"  • {issue}")

# Use local implementation if import failed
if print_module_status is None:
    print_module_status = _local_print_module_status

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ModulesCLI:
    """CLI for managing framework modules"""
    
    def __init__(self):
        self.config = get_module_config()
        self.loader = get_module_loader()
    
    def print_status(self):
        """Print current module status"""
        try:
            print_module_status()
        except NameError:
            # Fallback implementation
            summary = self.config.get_configuration_summary()
            
            print(f"\n🚀 AI Enhancement Framework")
            print(f"📊 Modules: {summary['enabled_count']}/{summary['total_modules']} enabled")
            print(f"🔧 Configuration: {self.config.config_path}")
            
            print(f"\n✅ Enabled Modules ({summary['enabled_count']}):")
            for module in summary['enabled_modules']:
                module_info = self.config.get_module_info(module)
                print(f"  • {module}: {module_info['description']}")
            
            if summary['disabled_modules']:
                print(f"\n❌ Disabled Modules ({summary['disabled_count']}):")
                for module in summary['disabled_modules']:
                    module_info = self.config.get_module_info(module)
                    print(f"  • {module}: {module_info['description']}")
            
            if not summary['dependency_validation']['valid']:
                print(f"\n⚠️  Dependency Issues:")
                for issue in summary['dependency_validation']['issues']:
                    print(f"  • {issue}")
    
    def list_modules(self):
        """List all available modules by category"""
        summary = self.config.get_configuration_summary()
        
        print(f"\n📋 Available Modules ({summary['total_modules']} total)")
        print("=" * 50)
        
        for category, modules in summary['categories'].items():
            if modules:
                print(f"\n📂 {category.upper()}:")
                for module in modules:
                    module_info = self.config.get_module_info(module)
                    status = "✅" if module_info['enabled'] else "❌"
                    print(f"  {status} {module}")
                    print(f"      {module_info['description']}")
                    if module_info['dependencies']:
                        print(f"      Dependencies: {', '.join(module_info['dependencies'])}")
                    if module_info['requirements']:
                        print(f"      Requirements: {', '.join(module_info['requirements'])}")
    
    def enable_modules(self, modules: List[str]) -> bool:
        """Enable specified modules"""
        if not modules:
            print("❌ No modules specified")
            return False
        
        print(f"\n🔄 Enabling modules: {', '.join(modules)}")
        
        success = True
        for module in modules:
            if not hasattr(self.config.config, module):
                print(f"❌ Unknown module: {module}")
                success = False
                continue
            
            if self.config.is_module_enabled(module):
                print(f"⚠️  Module {module} is already enabled")
                continue
            
            try:
                self.config.enable_module(module)
                print(f"✅ Enabled: {module}")
            except Exception as e:
                print(f"❌ Failed to enable {module}: {e}")
                success = False
        
        if success:
            try:
                self.config.save_config()
                print(f"\n💾 Configuration saved")
                
                # Validate dependencies
                valid, issues = self.config.validate_dependencies()
                if not valid:
                    print(f"\n⚠️  Dependency warnings:")
                    for issue in issues:
                        print(f"  • {issue}")
                
            except Exception as e:
                print(f"❌ Failed to save configuration: {e}")
                return False
        
        return success
    
    def disable_modules(self, modules: List[str]) -> bool:
        """Disable specified modules"""
        if not modules:
            print("❌ No modules specified")
            return False
        
        print(f"\n🔄 Disabling modules: {', '.join(modules)}")
        
        success = True
        for module in modules:
            if not hasattr(self.config.config, module):
                print(f"❌ Unknown module: {module}")
                success = False
                continue
            
            if not self.config.is_module_enabled(module):
                print(f"⚠️  Module {module} is already disabled")
                continue
            
            try:
                self.config.disable_module(module)
                print(f"✅ Disabled: {module}")
            except Exception as e:
                print(f"❌ Failed to disable {module}: {e}")
                success = False
        
        if success:
            try:
                self.config.save_config()
                print(f"\n💾 Configuration saved")
                
                # Validate dependencies
                valid, issues = self.config.validate_dependencies()
                if not valid:
                    print(f"\n⚠️  Dependency warnings:")
                    for issue in issues:
                        print(f"  • {issue}")
                
            except Exception as e:
                print(f"❌ Failed to save configuration: {e}")
                return False
        
        return success
    
    def validate_configuration(self):
        """Validate current configuration"""
        print(f"\n🔍 Validating configuration...")
        
        # Check dependency validation
        valid_deps, dep_issues = self.config.validate_dependencies()
        if valid_deps:
            print("✅ Dependencies: All satisfied")
        else:
            print("❌ Dependencies: Issues found")
            for issue in dep_issues:
                print(f"  • {issue}")
        
        # Check module availability
        loader_valid, loader_issues = self.loader.validate_configuration()
        if loader_valid:
            print("✅ Module Loading: All enabled modules available")
        else:
            print("❌ Module Loading: Issues found")
            for issue in loader_issues:
                print(f"  • {issue}")
        
        # Test load enabled modules
        print(f"\n🧪 Testing module loading...")
        results = self.loader.preload_enabled_modules()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"📊 Load Test: {success_count}/{total_count} modules loaded successfully")
        
        for module, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {module}")
        
        overall_valid = valid_deps and loader_valid and success_count == total_count
        
        if overall_valid:
            print(f"\n🎉 Configuration is valid and ready!")
        else:
            print(f"\n⚠️  Configuration has issues that need attention")
        
        return overall_valid
    
    def reset_configuration(self):
        """Reset configuration to defaults"""
        print(f"\n⚠️  Resetting configuration to defaults...")
        
        # Enable all modules (default state)
        all_modules = self.config.get_all_module_names()
        for module in all_modules:
            self.config.enable_module(module)
        
        try:
            self.config.save_config()
            print(f"✅ Configuration reset complete")
            print(f"📄 All {len(all_modules)} modules enabled")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
            return False
        
        return True
    
    def export_configuration(self, output_file: str):
        """Export current configuration to file"""
        try:
            summary = self.config.get_configuration_summary()
            
            export_data = {
                "framework_version": "2.1.0",
                "export_timestamp": str(Path().cwd()),
                "configuration": summary,
                "module_details": {}
            }
            
            # Add detailed module information
            for module in self.config.get_all_module_names():
                export_data["module_details"][module] = self.config.get_module_info(module)
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Configuration exported to: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export configuration: {e}")
            return False
    
    def import_configuration(self, input_file: str):
        """Import configuration from file"""
        try:
            with open(input_file, 'r') as f:
                import_data = json.load(f)
            
            if 'configuration' not in import_data:
                print(f"❌ Invalid configuration file format")
                return False
            
            config_data = import_data['configuration']
            
            print(f"📥 Importing configuration...")
            print(f"   Enabling: {len(config_data['enabled_modules'])} modules")
            print(f"   Disabling: {len(config_data['disabled_modules'])} modules")
            
            # Apply configuration
            for module in config_data['enabled_modules']:
                self.config.enable_module(module)
            
            for module in config_data['disabled_modules']:
                self.config.disable_module(module)
            
            self.config.save_config()
            print(f"✅ Configuration imported successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to import configuration: {e}")
            return False

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Enhancement Framework - Module Management CLI",
        epilog="""
Examples:
  %(prog)s status                     # Show current module status
  %(prog)s list                       # List all available modules
  %(prog)s enable wolfram_integration # Enable WolframAlpha integration
  %(prog)s disable database_providers # Disable database providers
  %(prog)s validate                   # Validate current configuration
  %(prog)s reset                      # Reset to default configuration
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show current module status')
    
    # List command
    subparsers.add_parser('list', help='List all available modules')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable modules')
    enable_parser.add_argument('modules', nargs='+', help='Module names to enable')
    
    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable modules')
    disable_parser.add_argument('modules', nargs='+', help='Module names to disable')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate current configuration')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset configuration to defaults')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export configuration to file')
    export_parser.add_argument('file', help='Output file path')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import configuration from file')
    import_parser.add_argument('file', help='Input file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = ModulesCLI()
    
    try:
        if args.command == 'status':
            cli.print_status()
        elif args.command == 'list':
            cli.list_modules()
        elif args.command == 'enable':
            success = cli.enable_modules(args.modules)
            return 0 if success else 1
        elif args.command == 'disable':
            success = cli.disable_modules(args.modules)
            return 0 if success else 1
        elif args.command == 'validate':
            valid = cli.validate_configuration()
            return 0 if valid else 1
        elif args.command == 'reset':
            success = cli.reset_configuration()
            return 0 if success else 1
        elif args.command == 'export':
            success = cli.export_configuration(args.file)
            return 0 if success else 1
        elif args.command == 'import':
            success = cli.import_configuration(args.file)
            return 0 if success else 1
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 