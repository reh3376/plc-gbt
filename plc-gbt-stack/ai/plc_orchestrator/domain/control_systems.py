"""Control systems domain handler for the PLC Task Orchestrator."""

from typing import Any

from plc_orchestrator.config.settings import OrchestratorConfig
from plc_orchestrator.utils.logging import get_logger


class ControlSystemsHandler:
    """Handles control system specific analysis and validation."""

    def __init__(self, config: OrchestratorConfig) -> None:
        """
        Initialize control systems handler.

        Args:
            config: Orchestrator configuration
        """
        self.config = config
        self.logger = get_logger(__name__, config.get_logging_config())

    def get_guidance(self, task_description: str) -> str:
        """
        Get control system specific guidance.

        Args:
            task_description: Task description

        Returns:
            Guidance text
        """
        control_type = self._identify_control_type(task_description)

        guidance = f"""
# Control System Implementation Guidance

## Control Type: {control_type}

### Key Considerations:

1. **Safety First**
   - Implement safety interlocks and limits
   - Add manual override capability
   - Include emergency shutdown logic
   - Validate all setpoints and commands

2. **Control Algorithm Selection**
   - For {control_type}: Consider PID, cascade, or feedforward control
   - Tune parameters based on process dynamics
   - Implement anti-windup for integral action
   - Add derivative filtering to reduce noise

3. **Performance Requirements**
   - Settling time: < 30 seconds (typical)
   - Overshoot: < 10%
   - Steady-state error: < 1%
   - Update rate: Match process dynamics

4. **Implementation Best Practices**
   - Use fixed-point arithmetic for PLC implementations
   - Implement bumpless transfer for mode changes
   - Add rate limiting for actuator protection
   - Include comprehensive alarming

5. **Testing and Validation**
   - Step response testing
   - Disturbance rejection validation
   - Stability margin verification
   - Failsafe mode testing

### Example PID Implementation Structure:

```python
class PIDController:
    def __init__(self, kp, ki, kd, dt, limits=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.limits = limits or (-100, 100)
        
        # State variables
        self.integral = 0
        self.prev_error = 0
        
    def update(self, setpoint, measurement):
        # Calculate error
        error = setpoint - measurement
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term with anti-windup
        self.integral += error * self.dt
        self.integral = self._apply_limits(self.integral, -100, 100)
        i_term = self.ki * self.integral
        
        # Derivative term with filtering
        d_term = self.kd * (error - self.prev_error) / self.dt
        self.prev_error = error
        
        # Calculate output
        output = p_term + i_term + d_term
        
        # Apply output limits
        output = self._apply_limits(output, *self.limits)
        
        return output
```

Remember: Always validate control implementations in simulation before deployment!
"""
        return guidance

    def validate_control_implementation(self, code_content: str) -> dict[str, Any]:
        """
        Validate control system implementation.

        Args:
            code_content: Implementation code

        Returns:
            Validation results
        """
        issues = []
        recommendations = []

        # Check for safety features
        safety_checks = {
            "limits": any(
                word in code_content.lower() for word in ["limit", "clamp", "bound", "max", "min"]
            ),
            "manual_override": "manual" in code_content.lower()
            or "override" in code_content.lower(),
            "error_handling": "try" in code_content and "except" in code_content,
            "alarming": any(word in code_content.lower() for word in ["alarm", "alert", "warning"]),
        }

        for check, passed in safety_checks.items():
            if not passed:
                issues.append(f"Missing safety feature: {check}")

        # Check for control features
        control_checks = {
            "anti_windup": "windup" in code_content.lower()
            or "integral_limit" in code_content.lower(),
            "bumpless_transfer": "bumpless" in code_content.lower(),
            "rate_limiting": "rate_limit" in code_content.lower()
            or "slew_rate" in code_content.lower(),
        }

        for check, passed in control_checks.items():
            if not passed:
                recommendations.append(f"Consider implementing: {check}")

        # Check for proper tuning parameters
        if "pid" in code_content.lower():
            if not all(param in code_content.lower() for param in ["kp", "ki", "kd"]):
                issues.append("PID controller missing tuning parameters")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "safety_score": sum(safety_checks.values()) / len(safety_checks) * 100,
            "control_score": sum(control_checks.values()) / len(control_checks) * 100,
        }

    def suggest_tuning_method(self, process_type: str) -> dict[str, Any]:
        """
        Suggest control tuning method based on process type.

        Args:
            process_type: Type of process (e.g., "temperature", "flow", "level")

        Returns:
            Tuning suggestions
        """
        tuning_methods = {
            "temperature": {
                "method": "Ziegler-Nichols Open Loop",
                "typical_gains": {"kp": 1.2, "ki": 0.5, "kd": 0.1},
                "notes": "Temperature processes are typically slow with significant dead time",
            },
            "flow": {
                "method": "Lambda Tuning",
                "typical_gains": {"kp": 0.5, "ki": 2.0, "kd": 0.0},
                "notes": "Flow loops are fast, often P-only or PI control is sufficient",
            },
            "pressure": {
                "method": "Cohen-Coon",
                "typical_gains": {"kp": 2.0, "ki": 1.0, "kd": 0.2},
                "notes": "Pressure loops are moderately fast, watch for noise",
            },
            "level": {
                "method": "Averaging Level Control",
                "typical_gains": {"kp": 1.0, "ki": 0.1, "kd": 0.0},
                "notes": "Level control often uses loose tuning to filter disturbances",
            },
        }

        return tuning_methods.get(
            process_type.lower(),
            {
                "method": "Ziegler-Nichols Closed Loop",
                "typical_gains": {"kp": 1.0, "ki": 0.5, "kd": 0.125},
                "notes": "Generic tuning - adjust based on process response",
            },
        )

    def _identify_control_type(self, task_description: str) -> str:
        """Identify type of control system from description."""
        desc_lower = task_description.lower()

        control_types = {
            "temperature": ["temperature", "thermal", "heat", "cooling"],
            "pressure": ["pressure", "psi", "bar", "vacuum"],
            "flow": ["flow", "flowrate", "gpm", "flow rate"],
            "level": ["level", "tank", "vessel", "height"],
            "position": ["position", "servo", "motion", "actuator"],
            "speed": ["speed", "velocity", "rpm", "frequency"],
        }

        for control_type, keywords in control_types.items():
            if any(keyword in desc_lower for keyword in keywords):
                return control_type.title() + " Control"

        return "Process Control"
