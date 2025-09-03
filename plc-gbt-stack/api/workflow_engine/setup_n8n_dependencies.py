#!/usr/bin/env python3
"""
N8N Framework Integration - Dependency Setup Script
Phase 1.4: N8N Framework Dependencies Setup

This script ensures that the n8n framework dependencies are properly installed
and configured for the PLC-GBT integration.

Author: AI Task Orchestrator
Date: December 22, 2024
Phase: 1.4 - Basic Workflow Execution Integration
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
N8N_FRAMEWORK_PATH = PROJECT_ROOT / "n8n-framework"

# Constants
PACKAGE_JSON = "package.json"


class N8NDependencyManager:
    """
    Manages n8n framework dependencies for PLC-GBT integration.

    Ensures that the required Node.js packages are installed and
    properly configured for workflow execution.
    """

    def __init__(self, n8n_framework_path: Path):
        self.n8n_framework_path = n8n_framework_path
        self.node_executable = self._find_node_executable()
        self.npm_executable = self._find_npm_executable()

    def _find_node_executable(self) -> str:
        """Find Node.js executable."""
        node_candidates = ["node", "nodejs", "/usr/bin/node", "/usr/local/bin/node"]

        for candidate in node_candidates:
            try:
                result = subprocess.run(
                    [candidate, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"✅ Found Node.js: {candidate} ({result.stdout.strip()})")
                    return candidate
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        raise RuntimeError("Node.js not found - required for n8n workflow execution")

    def _find_npm_executable(self) -> str:
        """Find npm executable."""
        npm_candidates = ["npm", "/usr/bin/npm", "/usr/local/bin/npm"]

        for candidate in npm_candidates:
            try:
                result = subprocess.run(
                    [candidate, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"✅ Found npm: {candidate} ({result.stdout.strip()})")
                    return candidate
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        raise RuntimeError("npm not found - required for installing n8n dependencies")

    def validate_n8n_framework(self) -> bool:
        """Validate that n8n framework structure is correct."""
        logger.info("🔍 Validating N8N framework structure...")

        # Check essential directories and files
        required_paths = [
            self.n8n_framework_path / "packages" / "workflow",
            self.n8n_framework_path / "packages" / "core",
            self.n8n_framework_path / "packages" / "workflow" / PACKAGE_JSON,
            self.n8n_framework_path / "packages" / "core" / PACKAGE_JSON,
        ]

        for path in required_paths:
            if not path.exists():
                logger.error(f"❌ Required path not found: {path}")
                return False
            logger.debug(f"✅ Found: {path}")

        logger.info("✅ N8N framework structure validated")
        return True

    def check_dependencies_status(self) -> Dict[str, Any]:
        """Check the current status of n8n dependencies."""
        logger.info("📊 Checking N8N dependencies status...")

        status = {
            "workflow_package_installed": False,
            "core_package_installed": False,
            "node_modules_exists": False,
            "dependencies_installed": False
        }

        # Check if node_modules exists in framework root
        node_modules_path = self.n8n_framework_path / "node_modules"
        status["node_modules_exists"] = node_modules_path.exists()

        # Check specific package builds
        workflow_dist_path = self.n8n_framework_path / "packages" / "workflow" / "dist"
        status["workflow_package_installed"] = workflow_dist_path.exists()

        core_dist_path = self.n8n_framework_path / "packages" / "core" / "dist"
        status["core_package_installed"] = core_dist_path.exists()

        status["dependencies_installed"] = (
            status["node_modules_exists"] and
            status["workflow_package_installed"] and
            status["core_package_installed"]
        )

        return status

    async def install_dependencies(self) -> bool:
        """Install n8n framework dependencies."""
        logger.info("📦 Installing N8N framework dependencies...")

        try:
            # Change to n8n framework directory
            original_cwd = os.getcwd()
            os.chdir(self.n8n_framework_path)

            # Install dependencies using npm
            logger.info("🔧 Running npm install...")
            install_process = await asyncio.create_subprocess_exec(
                self.npm_executable,
                "install",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await install_process.communicate()

            if install_process.returncode == 0:
                logger.info("✅ npm install completed successfully")

                # Build the packages if needed
                await self._build_packages()

                return True
            else:
                logger.error("❌ npm install failed:")
                logger.error(f"STDOUT: {stdout.decode()}")
                logger.error(f"STDERR: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"❌ Dependency installation failed: {e}")
            return False
        finally:
            os.chdir(original_cwd)

    async def _build_packages(self) -> bool:
        """Build n8n packages if needed."""
        logger.info("🔨 Building N8N packages...")

        try:
            # Build workflow package
            workflow_path = self.n8n_framework_path / "packages" / "workflow"
            if (workflow_path / PACKAGE_JSON).exists():
                logger.info("📦 Building n8n-workflow package...")

                build_process = await asyncio.create_subprocess_exec(
                    self.npm_executable,
                    "run", "build",
                    cwd=str(workflow_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                _, stderr = await build_process.communicate()

                if build_process.returncode == 0:
                    logger.info("✅ n8n-workflow package built successfully")
                else:
                    logger.warning(f"⚠️ n8n-workflow build had issues: {stderr.decode()}")

            # Build core package
            core_path = self.n8n_framework_path / "packages" / "core"
            if (core_path / PACKAGE_JSON).exists():
                logger.info("📦 Building n8n-core package...")

                build_process = await asyncio.create_subprocess_exec(
                    self.npm_executable,
                    "run", "build",
                    cwd=str(core_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                _, stderr = await build_process.communicate()

                if build_process.returncode == 0:
                    logger.info("✅ n8n-core package built successfully")
                else:
                    logger.warning(f"⚠️ n8n-core build had issues: {stderr.decode()}")

            return True

        except Exception as e:
            logger.error(f"❌ Package build failed: {e}")
            return False

    async def setup_minimal_dependencies(self) -> bool:
        """Setup minimal dependencies required for workflow execution."""
        logger.info("🏗️ Setting up minimal N8N dependencies for integration...")

        try:
            # Create a minimal package.json for the integration if needed
            integration_package_path = self.n8n_framework_path / "integration_package.json"

            minimal_package = {
                "name": "n8n-plc-gbt-integration",
                "version": "1.0.0",
                "private": True,
                "dependencies": {
                    "n8n-workflow": "file:./packages/workflow",
                    "n8n-core": "file:./packages/core",
                    "lodash": "^4.17.21",
                    "luxon": "^3.0.0",
                    "zod": "^3.22.0"
                },
                "scripts": {
                    "test": "node test_integration.js"
                }
            }

            async with aiofiles.open(integration_package_path, 'w') as f:
                await f.write(json.dumps(minimal_package, indent=2))

            logger.info(f"✅ Created integration package.json: {integration_package_path}")

            # Create a simple test script to verify the integration
            test_script_path = self.n8n_framework_path / "test_integration.js"

            test_script_content = '''
// Test script to verify N8N framework integration
console.log("🧪 Testing N8N Framework Integration...");

try {
    // Test importing n8n-workflow
    const { Workflow } = require('./packages/workflow/dist/cjs/index.js');
    console.log("✅ n8n-workflow import successful");

    // Test creating a basic workflow
    const workflow = new Workflow({
        id: 'test-workflow',
        name: 'Test Workflow',
        nodes: [],
        connections: {},
        active: true,
        nodeTypes: null  // Will be provided at runtime
    });

    console.log(`✅ Workflow creation successful: ${workflow.name}`);
    console.log("🎉 N8N Framework Integration Test PASSED");

} catch (error) {
    console.error("❌ N8N Framework Integration Test FAILED:");
    console.error(error.message);
    process.exit(1);
}
'''

            async with aiofiles.open(test_script_path, 'w') as f:
                await f.write(test_script_content)

            logger.info(f"✅ Created integration test script: {test_script_path}")

            # Run the test script
            logger.info("🧪 Running integration test...")

            test_process = await asyncio.create_subprocess_exec(
                self.node_executable,
                str(test_script_path),
                cwd=str(self.n8n_framework_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await test_process.communicate()

            if test_process.returncode == 0:
                logger.info("✅ Integration test passed!")
                logger.info(f"Test output: {stdout.decode()}")
                return True
            else:
                logger.error("❌ Integration test failed!")
                logger.error(f"Error output: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"❌ Minimal dependency setup failed: {e}")
            return False

    async def setup_complete_environment(self) -> bool:
        """Setup complete n8n environment for PLC-GBT integration."""
        logger.info("🚀 Setting up complete N8N environment for PLC-GBT...")
        logger.info("=" * 60)

        try:
            # Step 1: Validate framework structure
            if not self.validate_n8n_framework():
                logger.error("❌ N8N framework validation failed")
                return False

            # Step 2: Check current dependency status
            status = self.check_dependencies_status()
            logger.info(f"📊 Dependencies status: {status}")

            # Step 3: Install dependencies if needed
            if not status["dependencies_installed"]:
                logger.info("📦 Dependencies not installed - installing now...")
                if not await self.install_dependencies():
                    logger.error("❌ Dependency installation failed")
                    return False
            else:
                logger.info("✅ Dependencies already installed")

            # Step 4: Setup minimal integration environment
            if not await self.setup_minimal_dependencies():
                logger.error("❌ Minimal dependency setup failed")
                return False

            # Step 5: Final validation
            final_status = self.check_dependencies_status()
            if final_status["dependencies_installed"]:
                logger.info("=" * 60)
                logger.info("✅ N8N Framework Environment Setup Complete!")
                logger.info("🎯 Ready for Phase 1.4 Integration Testing!")
                return True
            else:
                logger.error("❌ Final validation failed")
                return False

        except Exception as e:
            logger.error(f"❌ Environment setup failed: {e}")
            return False


async def main():
    """Main entry point for N8N dependency setup."""
    import argparse

    parser = argparse.ArgumentParser(
        description="N8N Framework Integration - Dependency Setup"
    )
    parser.add_argument(
        "--n8n-path",
        default=str(N8N_FRAMEWORK_PATH),
        help="Path to N8N framework directory"
    )
    parser.add_argument(
        "--force-reinstall",
        action="store_true",
        help="Force reinstall of all dependencies"
    )

    args = parser.parse_args()

    try:
        n8n_path = Path(args.n8n_path)

        if not n8n_path.exists():
            logger.error(f"❌ N8N framework path not found: {n8n_path}")
            logger.info("Please ensure the n8n framework is cloned to the correct location")
            sys.exit(1)

        # Initialize dependency manager
        dependency_manager = N8NDependencyManager(n8n_path)

        # Setup complete environment
        success = await dependency_manager.setup_complete_environment()

        if success:
            logger.info("🎉 N8N Framework setup completed successfully!")
            logger.info("Ready to run integration tests with:")
            logger.info("  python api/workflow_engine/integration_test.py")
            sys.exit(0)
        else:
            logger.error("❌ N8N Framework setup failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Setup script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
