#!/usr/bin/env python3
"""
Example usage of the modularized AI Task Orchestrator.

This demonstrates how to use the new modular structure.
"""

# Import from the new modular structure
from plc_orchestrator import ValidationTier, create_orchestrator
from plc_orchestrator.core.progress import ProgressReporter


def main():
    """Main example function."""
    print("AI Task Orchestrator - Modular Example\n")

    # Create orchestrator with configuration
    orchestrator = create_orchestrator(
        enable_memory=False,  # Disable memory for this example
        enable_math_validation=True,
        log_level="INFO",
    )

    # Example task
    task_description = """
    Create a PID controller class for temperature control with the following requirements:
    - Must support tuning parameters (Kp, Ki, Kd)
    - Should implement anti-windup for integral term
    - Need manual/auto mode switching
    - Include safety limits for output
    - Add data logging capability
    """

    print(f"Task: {task_description}\n")

    # 1. Analyze the task
    print("1. Analyzing task...")
    analysis = orchestrator.analyze_task(task_description)

    print(f"   - Task ID: {analysis.task_id}")
    print(f"   - Complexity: {analysis.complexity}")
    print(f"   - Requirements: {len(analysis.requirements)}")
    print(f"   - Is Control Task: {analysis.is_control_system_task()}")
    print()

    # 2. Create implementation guide
    print("2. Creating implementation guide...")
    guide_path = orchestrator.create_implementation_guide(analysis)
    print(f"   - Guide created: {guide_path}")
    print()

    # 3. Simulate implementation
    print("3. Simulating implementation...")
    sample_implementation = """
import time
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

class ControlMode(Enum):
    MANUAL = "manual"
    AUTO = "auto"

@dataclass
class PIDController:
    '''PID Controller for temperature control with anti-windup and safety features.'''
    
    kp: float = 1.0  # Proportional gain
    ki: float = 0.5  # Integral gain
    kd: float = 0.1  # Derivative gain
    
    output_min: float = 0.0    # Minimum output limit
    output_max: float = 100.0  # Maximum output limit
    
    def __init__(self, kp: float, ki: float, kd: float, 
                 output_limits: Tuple[float, float] = (0, 100)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min, self.output_max = output_limits
        
        # State variables
        self.mode = ControlMode.MANUAL
        self.manual_output = 0.0
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = None
        
        # Anti-windup
        self.integral_min = -50.0
        self.integral_max = 50.0
        
        # Data logging
        self.log_data = []
        
    def set_mode(self, mode: ControlMode):
        '''Switch between manual and auto mode with bumpless transfer.'''
        if mode != self.mode:
            if mode == ControlMode.AUTO:
                # Reset integral for bumpless transfer
                self.integral = 0.0
                self.prev_error = 0.0
            self.mode = mode
            
    def update(self, setpoint: float, measurement: float) -> float:
        '''Update controller and return output.'''
        if self.mode == ControlMode.MANUAL:
            output = self.manual_output
        else:
            output = self._calculate_pid(setpoint, measurement)
            
        # Apply safety limits
        output = max(self.output_min, min(output, self.output_max))
        
        # Log data
        self._log_data(setpoint, measurement, output)
        
        return output
        
    def _calculate_pid(self, setpoint: float, measurement: float) -> float:
        '''Calculate PID output with anti-windup.'''
        current_time = time.time()
        
        if self.prev_time is None:
            dt = 0.1  # Default sample time
        else:
            dt = current_time - self.prev_time
            
        error = setpoint - measurement
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = max(self.integral_min, min(self.integral, self.integral_max))
        i_term = self.ki * self.integral
        
        # Derivative term
        if dt > 0:
            d_term = self.kd * (error - self.prev_error) / dt
        else:
            d_term = 0
            
        # Update state
        self.prev_error = error
        self.prev_time = current_time
        
        return p_term + i_term + d_term
        
    def _log_data(self, setpoint: float, measurement: float, output: float):
        '''Log control data for analysis.'''
        self.log_data.append({
            'timestamp': time.time(),
            'setpoint': setpoint,
            'measurement': measurement,
            'output': output,
            'mode': self.mode.value
        })
        
        # Keep only last 1000 samples
        if len(self.log_data) > 1000:
            self.log_data.pop(0)
    """

    # 4. Validate implementation
    print("4. Validating implementation...")
    validation_result = orchestrator.validate_implementation(
        sample_implementation, validation_tier=ValidationTier.PRODUCTION
    )

    print(f"   - Passed: {validation_result.passed}")
    print(f"   - Score: {validation_result.score:.1f}/100")
    print(f"   - Issues: {len(validation_result.issues)}")

    if validation_result.issues:
        print("\n   Issues found:")
        for issue in validation_result.issues[:3]:  # Show first 3
            print(f"   - [{issue['severity']}] {issue['message']}")

    if validation_result.recommendations:
        print("\n   Recommendations:")
        for rec in validation_result.recommendations[:3]:  # Show first 3
            print(f"   - {rec}")
    print()

    # 5. Get production checklist
    print("5. Generating production checklist...")
    checklist = orchestrator.get_production_checklist(sample_implementation)
    print(f"   - Overall ready: {checklist.overall_readiness}")
    print(f"   - Failed checks: {len(checklist.get_failed_checks())}")
    print()

    # 6. Create summary
    print("6. Creating task summary...")
    summary_path = orchestrator.create_summary_document()
    print(f"   - Summary created: {summary_path}")
    print()

    # Cleanup
    orchestrator.cleanup()
    print("Done!")


def advanced_example():
    """Advanced example with progress monitoring."""
    print("\nAdvanced Example - With Progress Monitoring\n")

    # Create orchestrator
    orchestrator = create_orchestrator()

    # Add progress callback
    def progress_callback(update):
        ProgressReporter.console_reporter(update)

    orchestrator.progress_monitor.add_progress_callback(progress_callback)

    # Set total steps
    orchestrator.progress_monitor.set_total_steps(5)

    # Execute steps
    steps = [
        {"name": "Setup", "type": "setup"},
        {"name": "Analysis", "type": "analysis"},
        {"name": "Implementation", "type": "implementation"},
        {"name": "Validation", "type": "validation"},
        {"name": "Documentation", "type": "documentation"},
    ]

    for i, step in enumerate(steps, 1):
        result = orchestrator.execute_task_step(i, step)
        time.sleep(0.5)  # Simulate work

    print("\n\nProgress Summary:")
    summary = orchestrator.progress_monitor.get_summary()
    print(f"- Completed: {summary['completed_steps']}/{summary['total_steps']}")
    print(f"- Duration: {summary['elapsed_time_formatted']}")


if __name__ == "__main__":
    import time

    # Run basic example
    main()

    # Uncomment to run advanced example
    # advanced_example()
