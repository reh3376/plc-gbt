#!/usr/bin/env python3
"""
AI Enhancement Framework - Command Line Interface

Simple CLI for framework management and utilities.
"""

import sys
import argparse
from typing import List, Optional

def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    if argv is None:
        argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        prog="ai-framework",
        description="AI Enhancement Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-framework --version    Show framework version
  ai-framework init         Initialize framework in current directory
  ai-framework check        Check framework installation
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="AI Enhancement Framework 1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize framework")
    init_parser.add_argument(
        "--project-type",
        choices=["python", "web_api", "data_science", "ml_project"],
        default="python",
        help="Project type for initialization"
    )
    
    # Check command  
    check_parser = subparsers.add_parser("check", help="Check installation")
    check_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args(argv)
    
    if args.command == "init":
        return cmd_init(args)
    elif args.command == "check":
        return cmd_check(args)
    else:
        parser.print_help()
        return 1

def cmd_init(args) -> int:
    """Initialize framework in current directory."""
    print(f"🎯 Initializing AI Enhancement Framework ({args.project_type} project)...")
    
    try:
        # Import here to avoid startup overhead
        from .core import AITaskOrchestrator
        
        print("✅ Core components available")
        print("📁 Creating .cursorrules configuration...")
        
        # Create basic .cursorrules file
        cursorrules_content = f"""# AI Enhancement Framework Configuration
ai_framework:
  enabled: true
  mode: "development"

project:
  type: "{args.project_type}"
  
assistant:
  task_orchestrator: true
  memory_management: true
  code_analysis: true
"""
        
        with open(".cursorrules", "w") as f:
            f.write(cursorrules_content)
        
        print("✅ Framework initialized successfully!")
        print("\nNext steps:")
        print("1. Open project in Cursor IDE")
        print("2. Start development with AI assistance")
        
        return 0
        
    except ImportError as e:
        print(f"❌ Framework not properly installed: {e}")
        print("Please run: pip install -e .[full]")
        return 1

def cmd_check(args) -> int:
    """Check framework installation."""
    print("🔍 Checking AI Enhancement Framework installation...")
    
    errors = []
    
    # Check core imports
    try:
        from .core import AITaskOrchestrator
        print("✅ AITaskOrchestrator available")
    except ImportError as e:
        errors.append(f"AITaskOrchestrator: {e}")
    
    try:
        from .core import UniversalCodeAnalyzer  
        print("✅ UniversalCodeAnalyzer available")
    except ImportError as e:
        errors.append(f"UniversalCodeAnalyzer: {e}")
        
    try:
        from .core import UniversalMemoryManager
        print("✅ UniversalMemoryManager available")
    except ImportError as e:
        errors.append(f"UniversalMemoryManager: {e}")
    
    # Check optional dependencies
    optional_deps = {
        "redis": "Redis support",
        "neo4j": "Neo4j support", 
        "psycopg2": "PostgreSQL support",
        "qdrant_client": "Qdrant support",
        "aiohttp": "Async HTTP support"
    }
    
    if args.verbose:
        print("\n📦 Optional dependencies:")
        for dep, desc in optional_deps.items():
            try:
                __import__(dep)
                print(f"✅ {desc}")
            except ImportError:
                print(f"⚠️  {desc} (optional)")
    
    if errors:
        print(f"\n❌ {len(errors)} issue(s) found:")
        for error in errors:
            print(f"  - {error}")
        print("\nTry reinstalling: pip install -e .[full]")
        return 1
    else:
        print("\n🎉 Framework installation looks good!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 