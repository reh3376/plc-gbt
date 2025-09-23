#!/usr/bin/env python3
"""
Complex Control System Workflow
================================

This workflow demonstrates implementing a complex industrial control system:
1. Tank level control with PID
2. Safety interlocks and alarms
3. HMI interface generation
4. Compliance validation

Requirements:
- Python 3.10+
- plc_orchestrator package
- lxml for L5X generation
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_task_orchestrator import AITaskOrchestrator, get_task_guidance, validate_task_completion
from plc_orchestrator.config import OrchestratorConfig
from plc_orchestrator.core.enums import DomainType, TaskComplexity, ValidationTier
from plc_orchestrator.domain.control_systems import (
    ControlSystemAnalyzer,
    SafetyValidator,
    generate_l5x_template,
)


def create_tank_control_system():
    """Create a complete tank level control system with safety features."""

    print("=== Complex Control System Workflow ===")
    print("Creating tank level control with safety interlocks...\n")

    # Initialize orchestrator with production settings
    config = OrchestratorConfig(
        environment="production",
        enable_production_checks=True,
        enable_industrial_llm=True,
        require_documentation=True,
        min_validation_score=95.0
    )

    orchestrator = AITaskOrchestrator(config=config)

    # Define complex control task
    task_description = """
    Implement a tank level control system with the following requirements:
    
    1. PID Control:
       - Maintain tank level at 75% setpoint
       - Input: Level transmitter (0-100%)
       - Output: Control valve (0-100%)
       - Tuning: P=2.5, I=0.5, D=0.1
    
    2. Safety Interlocks:
       - High level alarm at 90%
       - High-high level shutdown at 95%
       - Low level alarm at 20%
       - Low-low level shutdown at 10%
       
    3. Operating Modes:
       - Manual: Direct valve control
       - Auto: PID control active
       - Maintenance: All outputs disabled
       
    4. HMI Requirements:
       - Tank visualization with level indicator
       - Trend display for level and valve position
       - Alarm banner with acknowledgment
       - Mode selection buttons
       
    5. Data Logging:
       - Log level, valve position, and alarms every 1 second
       - Maintain 24-hour circular buffer
       - Export capability to CSV
    
    Generate complete ladder logic, function blocks, HMI screens, and documentation.
    """

    # Analyze the complex task
    print("1. Analyzing control system requirements...")
    analysis = orchestrator.analyze_task(task_description)

    print(f"   - Complexity: {analysis['complexity']}")
    print(f"   - Domain: {analysis['domain']}")
    print(f"   - Estimated effort: {analysis.get('estimated_hours', 'N/A')} hours")
    print(f"   - Risk level: {analysis.get('risk_level', 'Medium')}")

    # Get implementation guidance
    print("\n2. Getting implementation guidance...")
    guidance = get_task_guidance(
        task_type=DomainType.CONTROL_SYSTEMS,
        complexity=TaskComplexity.COMPLEX,
        context={
            "system_type": "tank_control",
            "safety_critical": True,
            "requires_hmi": True,
            "requires_logging": True
        }
    )

    print(f"   - Recommended patterns: {len(guidance.get('patterns', []))}")
    print(f"   - Safety considerations: {len(guidance.get('safety_checks', []))}")

    # Generate PLC code components
    print("\n3. Generating PLC code components...")

    # 3.1 Generate main ladder logic
    ladder_logic = f"""
    // Tank Level Control System
    // Generated: {datetime.now().isoformat()}
    // Safety Rating: SIL-2 Capable
    
    PROGRAM TankLevelControl
    VAR
        // Process Variables
        TankLevel : REAL := 0.0;        // Current tank level (0-100%)
        ValvePosition : REAL := 0.0;    // Control valve position (0-100%)
        LevelSetpoint : REAL := 75.0;   // Level setpoint (%)
        
        // PID Controller
        PID_Controller : PID;
        PID_Error : REAL;
        PID_Output : REAL;
        
        // Operating Modes
        Mode_Manual : BOOL := FALSE;
        Mode_Auto : BOOL := TRUE;
        Mode_Maintenance : BOOL := FALSE;
        ManualValvePosition : REAL := 0.0;
        
        // Alarms and Interlocks
        Alarm_HighLevel : BOOL := FALSE;
        Alarm_HighHighLevel : BOOL := FALSE;
        Alarm_LowLevel : BOOL := FALSE;
        Alarm_LowLowLevel : BOOL := FALSE;
        
        // Safety Shutdown
        SafetyShutdown : BOOL := FALSE;
        
        // Data Logging
        LogTimer : TON;
        LogTrigger : BOOL := FALSE;
        LogBuffer : ARRAY[1..86400] OF TankLogEntry;  // 24-hour buffer
        LogIndex : DINT := 1;
    END_VAR
    
    // Main Control Logic
    
    // Read Level Transmitter
    TankLevel := ScaleAnalogInput(AI_TankLevel, 0.0, 100.0);
    
    // Check Alarm Conditions
    Alarm_HighLevel := TankLevel >= 90.0;
    Alarm_HighHighLevel := TankLevel >= 95.0;
    Alarm_LowLevel := TankLevel <= 20.0;
    Alarm_LowLowLevel := TankLevel <= 10.0;
    
    // Safety Shutdown Logic
    SafetyShutdown := Alarm_HighHighLevel OR Alarm_LowLowLevel OR Mode_Maintenance;
    
    // Mode Selection (Mutually Exclusive)
    IF Mode_Manual THEN
        Mode_Auto := FALSE;
        Mode_Maintenance := FALSE;
    ELSIF Mode_Auto THEN
        Mode_Manual := FALSE;
        Mode_Maintenance := FALSE;
    ELSIF Mode_Maintenance THEN
        Mode_Manual := FALSE;
        Mode_Auto := FALSE;
    END_IF;
    
    // Control Logic
    IF SafetyShutdown THEN
        // Emergency shutdown - close valve
        ValvePosition := 0.0;
    ELSIF Mode_Manual THEN
        // Manual mode - use operator input
        ValvePosition := LIMIT(0.0, ManualValvePosition, 100.0);
    ELSIF Mode_Auto THEN
        // Auto mode - PID control
        PID_Error := LevelSetpoint - TankLevel;
        
        PID_Controller(
            EN := TRUE,
            SP := LevelSetpoint,
            PV := TankLevel,
            KP := 2.5,
            KI := 0.5,
            KD := 0.1,
            OUT_MIN := 0.0,
            OUT_MAX := 100.0
        );
        
        ValvePosition := PID_Controller.OUT;
    ELSE
        // Default safe state
        ValvePosition := 0.0;
    END_IF;
    
    // Write to Control Valve
    AO_ControlValve := ScaleAnalogOutput(ValvePosition, 0.0, 100.0);
    
    // Data Logging (1 second interval)
    LogTimer(IN := TRUE, PT := T#1S);
    IF LogTimer.Q THEN
        LogTrigger := TRUE;
        LogTimer(IN := FALSE);  // Reset timer
        LogTimer(IN := TRUE);   // Restart timer
    END_IF;
    
    IF LogTrigger THEN
        LogBuffer[LogIndex].Timestamp := CurrentTime();
        LogBuffer[LogIndex].Level := TankLevel;
        LogBuffer[LogIndex].ValvePosition := ValvePosition;
        LogBuffer[LogIndex].HighAlarm := Alarm_HighLevel;
        LogBuffer[LogIndex].LowAlarm := Alarm_LowLevel;
        LogBuffer[LogIndex].Mode := GetCurrentMode();
        
        LogIndex := LogIndex + 1;
        IF LogIndex > 86400 THEN
            LogIndex := 1;  // Circular buffer
        END_IF;
        
        LogTrigger := FALSE;
    END_IF;
    
    END_PROGRAM
    """

    # 3.2 Generate safety function block
    safety_fb = """
    FUNCTION_BLOCK FB_SafetyInterlock
    VAR_INPUT
        ProcessValue : REAL;
        HighAlarmLimit : REAL;
        HighHighLimit : REAL;
        LowAlarmLimit : REAL;
        LowLowLimit : REAL;
        AlarmDelay : TIME := T#2S;
        ResetRequest : BOOL;
    END_VAR
    
    VAR_OUTPUT
        HighAlarm : BOOL;
        HighHighAlarm : BOOL;
        LowAlarm : BOOL;
        LowLowAlarm : BOOL;
        SafetyTrip : BOOL;
        AlarmActive : BOOL;
    END_VAR
    
    VAR
        HighTimer : TON;
        HighHighTimer : TON;
        LowTimer : TON;
        LowLowTimer : TON;
        TripLatch : BOOL;
    END_VAR
    
    // Alarm detection with time delay
    HighTimer(IN := (ProcessValue >= HighAlarmLimit), PT := AlarmDelay);
    HighAlarm := HighTimer.Q;
    
    HighHighTimer(IN := (ProcessValue >= HighHighLimit), PT := T#0S);  // No delay for safety
    HighHighAlarm := HighHighTimer.Q;
    
    LowTimer(IN := (ProcessValue <= LowAlarmLimit), PT := AlarmDelay);
    LowAlarm := LowTimer.Q;
    
    LowLowTimer(IN := (ProcessValue <= LowLowLimit), PT := T#0S);  // No delay for safety
    LowLowAlarm := LowLowTimer.Q;
    
    // Safety trip logic with latch
    IF HighHighAlarm OR LowLowAlarm THEN
        TripLatch := TRUE;
    END_IF;
    
    // Reset logic (requires alarms cleared)
    IF ResetRequest AND NOT HighHighAlarm AND NOT LowLowAlarm THEN
        TripLatch := FALSE;
    END_IF;
    
    SafetyTrip := TripLatch;
    AlarmActive := HighAlarm OR HighHighAlarm OR LowAlarm OR LowLowAlarm;
    
    END_FUNCTION_BLOCK
    """

    # 3.3 Generate HMI configuration
    hmi_config = {
        "screens": [
            {
                "name": "Main",
                "elements": [
                    {
                        "type": "tank",
                        "id": "TankDisplay",
                        "position": {"x": 100, "y": 50},
                        "size": {"width": 200, "height": 300},
                        "bindings": {
                            "level": "TankLevel",
                            "fillColor": {
                                "normal": "#3498db",
                                "alarm": "#e74c3c"
                            }
                        }
                    },
                    {
                        "type": "numeric_display",
                        "id": "LevelDisplay",
                        "position": {"x": 320, "y": 100},
                        "label": "Level",
                        "units": "%",
                        "binding": "TankLevel",
                        "format": "##0.0"
                    },
                    {
                        "type": "numeric_entry",
                        "id": "SetpointEntry",
                        "position": {"x": 320, "y": 150},
                        "label": "Setpoint",
                        "units": "%",
                        "binding": "LevelSetpoint",
                        "min": 0,
                        "max": 100
                    },
                    {
                        "type": "valve",
                        "id": "ControlValve",
                        "position": {"x": 150, "y": 360},
                        "binding": "ValvePosition",
                        "orientation": "horizontal"
                    },
                    {
                        "type": "mode_selector",
                        "id": "ModeSelect",
                        "position": {"x": 450, "y": 50},
                        "options": [
                            {"text": "Manual", "value": "Mode_Manual"},
                            {"text": "Auto", "value": "Mode_Auto"},
                            {"text": "Maintenance", "value": "Mode_Maintenance"}
                        ]
                    },
                    {
                        "type": "alarm_banner",
                        "id": "AlarmBanner",
                        "position": {"x": 0, "y": 0},
                        "width": "100%",
                        "height": 40,
                        "alarmGroups": ["TankAlarms"]
                    }
                ]
            },
            {
                "name": "Trends",
                "elements": [
                    {
                        "type": "trend",
                        "id": "LevelTrend",
                        "position": {"x": 10, "y": 50},
                        "size": {"width": 780, "height": 400},
                        "pens": [
                            {
                                "name": "Tank Level",
                                "tag": "TankLevel",
                                "color": "#3498db",
                                "min": 0,
                                "max": 100
                            },
                            {
                                "name": "Valve Position",
                                "tag": "ValvePosition",
                                "color": "#2ecc71",
                                "min": 0,
                                "max": 100
                            },
                            {
                                "name": "Setpoint",
                                "tag": "LevelSetpoint",
                                "color": "#e74c3c",
                                "min": 0,
                                "max": 100,
                                "style": "dashed"
                            }
                        ],
                        "timeSpan": "1h",
                        "updateRate": "1s"
                    }
                ]
            }
        ],
        "alarms": [
            {
                "tag": "Alarm_HighLevel",
                "group": "TankAlarms",
                "priority": 2,
                "message": "Tank level high (>90%)",
                "requiresAck": True
            },
            {
                "tag": "Alarm_HighHighLevel",
                "group": "TankAlarms",
                "priority": 1,
                "message": "Tank level critical - Safety shutdown (>95%)",
                "requiresAck": True
            },
            {
                "tag": "Alarm_LowLevel",
                "group": "TankAlarms",
                "priority": 2,
                "message": "Tank level low (<20%)",
                "requiresAck": True
            },
            {
                "tag": "Alarm_LowLowLevel",
                "group": "TankAlarms",
                "priority": 1,
                "message": "Tank level critical - Safety shutdown (<10%)",
                "requiresAck": True
            }
        ]
    }

    # Save generated files
    output_dir = Path("tank_control_system")
    output_dir.mkdir(exist_ok=True)

    # Save ladder logic
    ladder_file = output_dir / "TankControl_Logic.st"
    with open(ladder_file, 'w') as f:
        f.write(ladder_logic)
    print(f"   ✓ Generated ladder logic: {ladder_file}")

    # Save safety function block
    safety_file = output_dir / "SafetyInterlock_FB.st"
    with open(safety_file, 'w') as f:
        f.write(safety_fb)
    print(f"   ✓ Generated safety function block: {safety_file}")

    # Save HMI configuration
    hmi_file = output_dir / "HMI_Config.json"
    with open(hmi_file, 'w') as f:
        json.dump(hmi_config, f, indent=2)
    print(f"   ✓ Generated HMI configuration: {hmi_file}")

    # Generate L5X export
    print("\n4. Generating L5X export file...")
    l5x_content = generate_l5x_template(
        program_name="TankLevelControl",
        controller_type="ControlLogix",
        tags=[
            {"name": "TankLevel", "type": "REAL", "description": "Current tank level (%)"},
            {"name": "ValvePosition", "type": "REAL", "description": "Control valve position (%)"},
            {"name": "LevelSetpoint", "type": "REAL", "description": "Level setpoint (%)"},
            {"name": "Mode_Manual", "type": "BOOL", "description": "Manual mode selection"},
            {"name": "Mode_Auto", "type": "BOOL", "description": "Auto mode selection"},
            {"name": "Mode_Maintenance", "type": "BOOL", "description": "Maintenance mode"},
            {"name": "Alarm_HighLevel", "type": "BOOL", "description": "High level alarm"},
            {"name": "Alarm_HighHighLevel", "type": "BOOL", "description": "High-high level alarm"},
            {"name": "Alarm_LowLevel", "type": "BOOL", "description": "Low level alarm"},
            {"name": "Alarm_LowLowLevel", "type": "BOOL", "description": "Low-low level alarm"},
            {"name": "SafetyShutdown", "type": "BOOL", "description": "Safety shutdown active"}
        ],
        routines=[
            {"name": "Main", "type": "Ladder", "content": ladder_logic},
            {"name": "SafetyInterlock", "type": "FunctionBlock", "content": safety_fb}
        ]
    )

    l5x_file = output_dir / "TankControl.L5X"
    with open(l5x_file, 'w') as f:
        f.write(l5x_content)
    print(f"   ✓ Generated L5X export: {l5x_file}")

    # Perform safety validation
    print("\n5. Performing safety validation...")
    analyzer = ControlSystemAnalyzer()
    safety_validator = SafetyValidator()

    safety_analysis = analyzer.analyze_control_logic(ladder_logic)
    print(f"   - Safety functions identified: {safety_analysis.get('safety_functions', 0)}")
    print(f"   - Interlocks present: {safety_analysis.get('interlocks_found', False)}")
    print(f"   - Emergency shutdown: {safety_analysis.get('emergency_shutdown', False)}")

    validation_results = safety_validator.validate_safety_logic(
        ladder_logic,
        required_sil_level=2
    )
    print(f"   - SIL-2 compliance: {'PASS' if validation_results['sil_compliant'] else 'FAIL'}")

    # Generate documentation
    print("\n6. Generating documentation...")
    doc_content = f"""
# Tank Level Control System Documentation

## System Overview
This control system implements a tank level control with safety interlocks and HMI interface.

### Key Features:
- PID control for automatic level maintenance
- Multiple operating modes (Manual/Auto/Maintenance)
- Safety interlocks with high/low level alarms
- Emergency shutdown on critical conditions
- Real-time data logging with 24-hour buffer
- Comprehensive HMI with trending

## Control Strategy

### PID Control
- **Setpoint**: 75% (adjustable)
- **Proportional Gain (Kp)**: 2.5
- **Integral Time (Ki)**: 0.5
- **Derivative Time (Kd)**: 0.1
- **Output Range**: 0-100% valve position

### Safety Interlocks
| Condition | Threshold | Action | Priority |
|-----------|----------|--------|----------|
| High Level | 90% | Alarm | Warning |
| High-High Level | 95% | Shutdown | Critical |
| Low Level | 20% | Alarm | Warning |
| Low-Low Level | 10% | Shutdown | Critical |

### Operating Modes
1. **Manual Mode**: Direct operator control of valve position
2. **Auto Mode**: PID control active based on setpoint
3. **Maintenance Mode**: All outputs disabled for safety

## Implementation Details

### Hardware Requirements
- PLC: Allen-Bradley ControlLogix or equivalent
- Level Transmitter: 4-20mA, 0-100% range
- Control Valve: 4-20mA actuator, fail-closed
- HMI: PanelView Plus or equivalent

### Software Components
1. Main control program (TankLevelControl)
2. Safety interlock function block (FB_SafetyInterlock)
3. HMI screens (Main view and Trending)
4. Alarm management system

## Testing Procedures

### Functional Tests
1. Verify PID control maintains setpoint ±2%
2. Test all alarm conditions and acknowledgments
3. Verify mode transitions and interlocks
4. Test emergency shutdown scenarios

### Safety Tests
1. Simulate high-high level condition → Verify shutdown
2. Simulate low-low level condition → Verify shutdown
3. Test manual reset after safety trip
4. Verify maintenance mode disables all outputs

## Maintenance

### Regular Checks (Monthly)
- Calibrate level transmitter
- Test valve stroke and response
- Verify alarm setpoints
- Review data logs for anomalies

### Annual Inspection
- Full functional test of safety interlocks
- PID tuning verification
- HMI touch calibration
- Backup configuration files

---
Generated: {datetime.now().isoformat()}
Version: 1.0
Safety Rating: SIL-2 Capable
"""

    doc_file = output_dir / "TankControl_Documentation.md"
    with open(doc_file, 'w') as f:
        f.write(doc_content)
    print(f"   ✓ Generated documentation: {doc_file}")

    # Validate the complete implementation
    print("\n7. Validating complete implementation...")
    validation = validate_task_completion(
        task_description=task_description,
        generated_code={
            "ladder_logic": ladder_logic,
            "safety_fb": safety_fb,
            "hmi_config": json.dumps(hmi_config),
            "documentation": doc_content
        },
        validation_tier=ValidationTier.PRODUCTION,
        domain_type=DomainType.CONTROL_SYSTEMS
    )

    print("\n=== Validation Results ===")
    print(f"Status: {validation['status'].upper()}")
    print(f"Score: {validation['score']}/100")
    print(f"Safety Compliance: {'PASS' if validation.get('safety_compliant', False) else 'FAIL'}")

    if validation.get('issues'):
        print("\nIssues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")

    if validation.get('recommendations'):
        print("\nRecommendations:")
        for rec in validation['recommendations']:
            print(f"  - {rec}")

    print("\n✓ Complex control system workflow completed!")
    print(f"  Output directory: {output_dir.absolute()}")

    return {
        "status": "success",
        "output_dir": str(output_dir.absolute()),
        "files_generated": [
            str(ladder_file),
            str(safety_file),
            str(hmi_file),
            str(l5x_file),
            str(doc_file)
        ],
        "validation_score": validation['score'],
        "safety_compliant": validation.get('safety_compliant', False)
    }


if __name__ == "__main__":
    result = create_tank_control_system()
    print(f"\nWorkflow result: {json.dumps(result, indent=2)}")
