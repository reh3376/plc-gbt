"""Setup script for PLC Task Orchestrator."""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text()
else:
    long_description = "PLC Task Orchestrator - Modular AI-assisted task completion framework"

setup(
    name="plc-orchestrator",
    version="2.0.0",
    author="PLC-GBT Team",
    description="Modular framework for AI-assisted task analysis, planning, and execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/plc-gbt/orchestrator",
    packages=find_packages(include=["plc_orchestrator", "plc_orchestrator.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        # Core dependencies (always required)
    ],
    extras_require={
        # Optional dependencies
        "memory": [
            "redis>=4.0",
            "neo4j>=5.0",
            "psycopg2-binary>=2.9",
            "qdrant-client>=1.0",
        ],
        "validation": [
            "pydantic>=2.0",
            "structlog>=23.0",
        ],
        "math": [
            "wolframalpha>=5.0",  # If available
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.20",
            "pytest-cov>=4.0",
            "black>=22.0",
            "mypy>=1.0",
            "ruff>=0.1",
        ],
        "all": [
            # Include all optional dependencies
            "redis>=4.0",
            "neo4j>=5.0",
            "psycopg2-binary>=2.9",
            "qdrant-client>=1.0",
            "pydantic>=2.0",
            "structlog>=23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "plc-orchestrator=plc_orchestrator.cli:main",
        ],
    },
)
