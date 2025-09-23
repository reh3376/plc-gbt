#!/usr/bin/env python3
"""
Basic usage examples for the AI Task Orchestrator.

This example demonstrates the fundamental workflow:
1. Task analysis
2. Implementation guide creation
3. Code validation
4. Production readiness check
"""

import asyncio

from plc_orchestrator import ValidationTier, create_orchestrator


def example_simple_task():
    """Example: Analyze and validate a simple task."""
    print("\n" + "=" * 60)
    print("Example 1: Simple Task Analysis")
    print("=" * 60)

    # Create orchestrator
    orchestrator = create_orchestrator(enable_memory=False)

    # Define task
    task_description = """
    Create a Python function to parse CSV files with error handling.
    The function should:
    - Accept a file path as input
    - Handle missing files gracefully
    - Return a list of dictionaries
    - Include proper type hints
    """

    # Analyze task
    print("\n1. Analyzing task...")
    analysis = orchestrator.analyze_task(task_description)

    print("\nTask Analysis Results:")
    print(f"  - Task ID: {analysis.task_id}")
    print(f"  - Complexity: {analysis.complexity}")
    print(f"  - Estimated Time: {analysis.estimated_effort['hours']} hours")
    print(f"  - Requirements: {len(analysis.requirements)}")
    print(f"  - Identified Risks: {len(analysis.risks)}")

    # Create implementation guide
    print("\n2. Creating implementation guide...")
    guide_path = orchestrator.create_implementation_guide(analysis)
    print(f"  - Guide created at: {guide_path}")

    # Simulate implementation
    generated_code = '''
import csv
from pathlib import Path
from typing import List, Dict, Any

def parse_csv_file(file_path: str | Path) -> List[Dict[str, Any]]:
    """
    Parse a CSV file and return its contents as a list of dictionaries.
    Args:
        file_path: Path to the CSV file
    Returns:
        List of dictionaries representing CSV rows
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is not a valid CSV
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    if not file_path.suffix.lower() == '.csv':
        raise ValueError(f"File is not a CSV: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        raise ValueError(f"Error parsing CSV file: {e}") from e
'''

    # Validate implementation
    print("\n3. Validating implementation...")
    validation = orchestrator.validate_implementation(
        generated_code, analysis.requirements, validation_tier=ValidationTier.REQUIREMENTS
    )

    print("\nValidation Results:")
    print(f"  - Passed: {validation.passed}")
    print(f"  - Score: {validation.score}/100")
    print(f"  - Issues: {len(validation.issues)}")

    if validation.issues:
        print("\n  Issues found:")
        for issue in validation.issues[:3]:  # Show first 3 issues
            print(f"    - [{issue['severity']}] {issue['message']}")


def example_complex_task():
    """Example: Analyze a complex control system task."""
    print("\n" + "=" * 60)
    print("Example 2: Complex Control System Task")
    print("=" * 60)

    orchestrator = create_orchestrator(enable_memory=True, enable_control_analysis=True)

    task_description = """
    Implement a PID controller for temperature control in a distillation column.
    Requirements:
    - Support both manual and automatic modes
    - Include anti-windup protection
    - Implement bumpless transfer
    - Add cascade control capability
    - Include safety interlocks for high/low temperature
    - Log all control actions with timestamps
    - Provide real-time plotting capability
    """

    print("\n1. Analyzing complex task...")
    analysis = orchestrator.analyze_task(task_description)

    print("\nComplex Task Analysis:")
    print(f"  - Complexity: {analysis.complexity}")
    print(f"  - Is Control System: {analysis.is_control_system_task()}")
    print(f"  - Domain Tags: {', '.join(analysis.domain_tags)}")
    print(f"  - Estimated Hours: {analysis.estimated_effort['hours']}")

    # Show execution plan
    print(f"\n  Execution Plan ({len(analysis.execution_plan)} steps):")
    for i, step in enumerate(analysis.execution_plan[:5], 1):  # Show first 5 steps
        print(f"    {i}. {step['name']}")

    # Control system analysis
    if analysis.control_analysis:
        print("\n  Control System Analysis:")
        print(f"    - Type: {analysis.control_analysis['type']}")
        print(f"    - Complexity: {analysis.control_analysis['complexity']}")
        print(f"    - Safety Critical: {analysis.control_analysis['safety_critical']}")


async def example_with_memory():
    """Example: Using memory system for similar task lookup."""
    print("\n" + "=" * 60)
    print("Example 3: Task Analysis with Memory System")
    print("=" * 60)

    # This example assumes memory system is configured
    orchestrator = create_orchestrator(
        enable_memory=True,
        redis_url="redis://localhost:6379/0",  # Update with your Redis URL
    )

    task_description = """
    Create a data processing pipeline for industrial sensor data:
    - Read from multiple sensor sources
    - Apply signal filtering and smoothing
    - Detect anomalies using statistical methods
    - Store processed data in time-series database
    - Generate alerts for out-of-range values
    """

    print("\n1. Analyzing with memory insights...")
    analysis = orchestrator.analyze_task(task_description)

    print("\nAnalysis with Memory:")
    print(f"  - Task ID: {analysis.task_id}")
    print(f"  - Complexity: {analysis.complexity}")

    # Check memory insights
    if analysis.memory_insights:
        similar_tasks = analysis.memory_insights.get("similar_tasks", [])
        if similar_tasks:
            print(f"\n  Found {len(similar_tasks)} similar past tasks:")
            for task in similar_tasks[:3]:
                print(f"    - {task.get('description', 'N/A')[:60]}...")
                print(f"      Complexity: {task.get('complexity', 'N/A')}")
                print(f"      Success: {task.get('validation_passed', False)}")


def example_production_checklist():
    """Example: Generate production readiness checklist."""
    print("\n" + "=" * 60)
    print("Example 4: Production Readiness Check")
    print("=" * 60)

    orchestrator = create_orchestrator(enable_production_checks=True)

    # Example production-ready code
    production_code = '''
"""
Production-ready temperature monitoring service.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Protocol

import numpy as np
from prometheus_client import Counter, Gauge, Histogram

# Metrics
temperature_readings = Counter('temperature_readings_total', 'Total temperature readings')
current_temperature = Gauge('current_temperature_celsius', 'Current temperature')
reading_duration = Histogram('temperature_reading_duration_seconds', 'Time to read temperature')

# Configure logging
logger = logging.getLogger(__name__)


class TemperatureSensor(Protocol):
    """Protocol for temperature sensors."""
    def read_temperature(self) -> float: ...
    def get_status(self) -> str: ...


@dataclass
class TemperatureReading:
    """Temperature reading with metadata."""
    timestamp: datetime
    value: float
    sensor_id: str
    unit: str = "celsius"
class TemperatureMonitor:
    """Monitor temperature with safety checks and logging."""
    def __init__(
        self,
        sensor: TemperatureSensor,
        high_limit: float = 100.0,
        low_limit: float = 0.0,
        sensor_id: str = "default"
    ):
        self.sensor = sensor
        self.high_limit = high_limit
        self.low_limit = low_limit
        self.sensor_id = sensor_id
        self.readings: List[TemperatureReading] = []
        logger.info(
            f"Temperature monitor initialized: {sensor_id}",
            extra={"high_limit": high_limit, "low_limit": low_limit}
        )
    @reading_duration.time()
    def read_temperature(self) -> Optional[TemperatureReading]:
        """Read temperature with error handling."""
        try:
            # Read from sensor
            value = self.sensor.read_temperature()
            # Validate reading
            if not self._validate_reading(value):
                logger.warning(f"Invalid reading: {value}")
                return None
            # Create reading
            reading = TemperatureReading(
                timestamp=datetime.now(),
                value=value,
                sensor_id=self.sensor_id
            )
            # Update metrics
            temperature_readings.inc()
            current_temperature.set(value)
            # Store reading
            self.readings.append(reading)
            # Check limits
            if value > self.high_limit:
                logger.error(f"Temperature exceeded high limit: {value} > {self.high_limit}")
                self._trigger_high_alarm(value)
            elif value < self.low_limit:
                logger.error(f"Temperature below low limit: {value} < {self.low_limit}")
                self._trigger_low_alarm(value)
            return reading
        except Exception as e:
            logger.exception(f"Error reading temperature: {e}")
            return None
    def _validate_reading(self, value: float) -> bool:
        """Validate temperature reading."""
        # Check for sensor errors (common error values)
        if value in [-999.0, -9999.0, float('inf'), float('-inf')]:
            return False
        # Sanity check for reasonable values
        if not -273.15 <= value <= 1000.0:  # Absolute zero to 1000°C
            return False
        return True
    def _trigger_high_alarm(self, value: float) -> None:
        """Handle high temperature alarm."""
        logger.critical(f"HIGH TEMPERATURE ALARM: {value}°C")
        # In production: Send alerts, trigger safety systems, etc.
    def _trigger_low_alarm(self, value: float) -> None:
        """Handle low temperature alarm."""
        logger.critical(f"LOW TEMPERATURE ALARM: {value}°C")
        # In production: Send alerts, trigger safety systems, etc.
    def get_statistics(self) -> dict:
        """Calculate statistics from recent readings."""
        if not self.readings:
            return {"status": "no_data"}
        recent_values = [r.value for r in self.readings[-100:]]
        return {
            "count": len(self.readings),
            "current": recent_values[-1],
            "mean": np.mean(recent_values),
            "std": np.std(recent_values),
            "min": np.min(recent_values),
            "max": np.max(recent_values),
            "sensor_status": self.sensor.get_status()
        }
'''

    print("\n1. Checking production readiness...")
    checklist = orchestrator.get_production_checklist(production_code)

    print("\nProduction Checklist:")
    print(f"  - Overall Ready: {'✅' if checklist.overall_readiness else '❌'}")
    print(f"  - Passed Checks: {len(checklist.get_passed_checks())}/{len(checklist.checks)}")

    print("\n  Key Checks:")
    for category in ["error_handling", "logging", "monitoring", "documentation", "testing"]:
        checks = [c for c in checklist.checks if c["category"] == category]
        passed = [c for c in checks if c["passed"]]
        status = "✅" if len(passed) == len(checks) else "⚠️"
        print(f"    {status} {category.title()}: {len(passed)}/{len(checks)}")

    if checklist.blocking_issues:
        print("\n  ❌ Blocking Issues:")
        for issue in checklist.blocking_issues[:3]:
            print(f"    - {issue}")


def main():
    """Run all examples."""
    print("\n🚀 AI Task Orchestrator - Usage Examples")
    print("========================================")

    # Basic examples
    example_simple_task()
    example_complex_task()

    # Async example (if memory configured)
    try:
        asyncio.run(example_with_memory())
    except Exception as e:
        print(f"\n⚠️  Memory example skipped (Redis not configured): {e}")

    # Production checklist
    example_production_checklist()

    print("\n\n✅ All examples completed!")
    print("\nNext steps:")
    print("  1. Check the generated guide in the 'guides' directory")
    print("  2. Try modifying the task descriptions")
    print("  3. Experiment with different validation tiers")
    print("  4. Configure memory system for enhanced analysis")


if __name__ == "__main__":
    main()
