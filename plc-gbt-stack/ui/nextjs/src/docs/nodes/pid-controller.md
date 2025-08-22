# PID Controller - Industrial Control Node

**Node Type**: `pid-controller`  
**Category**: PLC Control Nodes  
**Version**: 2.1.0  
**Last Updated**: 2025-01-15

---

Advanced Proportional-Integral-Derivative controller with auto-tuning, gain scheduling, and industrial safety features

## 🎯 Overview

### Purpose
Industrial-grade PID controller for precise automatic control of process variables in manufacturing and process industries

### Key Features
- **Classical PID Algorithm**:  Proportional, Integral, and Derivative control actions
- **Auto-Tuning**:  Multiple tuning algorithms including Ziegler-Nichols and Cohen-Coon
- **Safety Features**:  Anti-windup protection, output limiting, and process variable safety limits
- **Operating Modes**:  Automatic, manual, cascade, ratio, and override control modes
- **Industrial Integration**:  Direct PLC address connectivity with real-time communication
- **Advanced Features**:  Gain scheduling, bumpless transfer, and feed-forward compensation

### When to Use This Node
- **Continuous Process Control**:  When maintaining a variable at a constant setpoint
- **Disturbance Rejection**:  When process is subject to external disturbances
- **Precision Requirements**:  When tight control accuracy is required (<2% deviation)
- **Safety Critical Applications**:  When process upsets could cause safety issues
- **Cascade Control Systems**:  As inner or outer loop in multi-loop control strategies

### Industrial Applications
- Chemical Processing: Reactor temperature and pressure control
- Oil & Gas: Pipeline pressure and flow control
- Power Generation: Steam temperature and pressure regulation
- Food & Beverage: Pasteurization temperature control
- Pharmaceutical: Critical process parameter control
- Water Treatment: pH and chemical dosing control

## ⚙️ Configuration Guide

### Quick Start
1. Drag PID Controller node from the control palette to the workflow canvas
2. Connect the process variable input from sensor or measurement node
3. Connect the control output to actuator or final control element node
4. Double-click to open properties and configure PLC addresses
5. Set initial PID parameters (start with Kp=1, Ti=60s, Td=15s)
6. Configure output limits to match actuator range
7. Enable anti-windup protection and safety limits
8. Test in manual mode before switching to automatic

### Detailed Setup

#### Step 1: Process Variable Configuration
Configure the measurement input signal from the process

**Required Parameters:**
- `processVariable`
- `pvSignalType`
- `engineeringUnits`

**Example Configuration:**
```json
{
  "processVariable": "DB10.Temperature_PV",
  "pvSignalType": "analog",
  "engineeringUnits": "degC"
}
```

#### Step 2: Control Output Setup
Configure the output signal to the final control element

**Required Parameters:**
- `controlOutput`
- `outputLimits`
- `outputSignalType`

**Example Configuration:**
```json
{
  "controlOutput": "DB10.Valve_CV",
  "outputLimits": { "min": 0, "max": 100 },
  "outputSignalType": "analog"
}
```

#### Step 3: PID Parameter Tuning
Set initial PID parameters or enable auto-tuning

**Required Parameters:**
- `proportionalGain`
- `integralTime`
- `derivativeTime`
- `autoTuneEnabled`

**Example Configuration:**
```json
{
  "proportionalGain": 2.0,
  "integralTime": 120.0,
  "derivativeTime": 30.0,
  "autoTuneEnabled": false
}
```

### Best Practices
- ✅ Start with conservative tuning (low gain, long integral time) for safety
- ✅ Use auto-tuning only during planned maintenance windows
- ✅ Always configure safety limits and anti-windup protection
- ✅ Test manual mode operation before enabling automatic control
- ✅ Document tuning parameters and process conditions for future reference
- ✅ Monitor controller performance and retune periodically
- ✅ Use cascade control for improved performance in complex processes

### Common Mistakes to Avoid
- ❌ Setting derivative time too high - amplifies measurement noise
- ❌ Forgetting anti-windup protection - causes integral buildup during output saturation
- ❌ Incorrect control action (direct vs reverse) - causes positive feedback
- ❌ Inadequate output limits - can damage actuators or create unsafe conditions
- ❌ Poor signal quality - measurement noise degrades control performance
- ❌ Ignoring process dynamics - tuning without understanding the process response

## 📊 Parameters Reference

### Essential Parameters

| Parameter | Type | Default | Range | Units | Description |
|-----------|------|---------|-------|-------|-------------|
| `processVariable` | string | `""` | - | - | PLC address or signal source for the process variable (measured value) |
| `setPoint` | number | `0` | -9999-9999 (step: 0.01) | Engineering Units | Desired target value for the controlled process variable |
| `controlOutput` | string | `""` | - | - | PLC address for the controller output signal to actuator/final control element |
| `proportionalGain` | number | `1` | 0.001-1000 (step: 0.001) | Dimensionless | Proportional gain (Kp) - determines immediate response to error |
| `integralTime` | number | `60` | 0.1-86400 (step: 0.1) | seconds | Integral time constant (Ti) in seconds - eliminates steady-state error |
| `derivativeTime` | number | `15` | 0-3600 (step: 0.1) | seconds | Derivative time constant (Td) in seconds - provides anticipatory action |
| `controllerMode` | enum | `"automatic"` | automatic | manual | cascade | ratio | override | - | Operating mode of the PID controller |
| `controlAction` | enum | `"direct"` | direct | reverse | - | Controller action type - direct (heating) or reverse (cooling) |
| `outputLimits` | object | `[object Object]` | - | - | Output signal limits to prevent actuator damage and ensure safe operation |

### Advanced Parameters

| Parameter | Type | Default | Description | Notes |
|-----------|------|---------|-------------|-------|
| `scanTime` | number | `1000` | Controller execution interval in milliseconds | Advanced parameter |
| `antiWindupEnabled` | boolean | `true` | Enable integral windup protection when output reaches limits | Advanced parameter |
| `bumplessTransfer` | boolean | `true` | Enable smooth transitions between manual and automatic modes | Advanced parameter |
| `safetyLimits` | object | `[object Object]` | Safety limits for process variable - triggers alarms and protective actions | Advanced parameter |
| `autoTuneEnabled` | boolean | `false` | Enable automatic PID parameter tuning using relay feedback method | Advanced parameter |
| `tuningMethod` | enum | `"ziegler-nichols"` | Auto-tuning algorithm selection | Options: ziegler-nichols, cohen-coon, lambda-tuning, imc, relay-feedback |

### Parameter Validation Rules
- **ERROR**: PID tuning may cause instability - reduce gain or increase integral time (Use conservative tuning or enable auto-tune feature)
- **WARNING**: High derivative time may amplify measurement noise (Consider using derivative filtering or reducing derivative time)
- **ERROR**: Invalid output limits - minimum must be less than maximum (Set minimum output limit below maximum output limit)

## 💡 Examples

### Example 1: Temperature Control Loop

**Use Case**: Maintaining reactor temperature at 250°C using electric heater

Basic temperature control for a heating process with anti-windup protection

```json
{
  "processVariable": "DB10.Temperature_PV",
  "setPoint": 250,
  "controlOutput": "DB10.Heater_Output",
  "proportionalGain": 2.5,
  "integralTime": 120,
  "derivativeTime": 30,
  "controllerMode": "automatic",
  "controlAction": "direct",
  "outputLimits": {
    "min": 0,
    "max": 100
  },
  "antiWindupEnabled": true,
  "safetyLimits": {
    "pvHigh": 300,
    "pvLow": 0
  }
}
```

**Expected Output:**
```
Smooth temperature control with <2°C deviation from setpoint
```

**Notes:**
- Tune conservatively for safety in heating applications
- Monitor for thermal lag and adjust derivative time accordingly
- Implement temperature ramp limiting for large setpoint changes

### Example 2: Flow Control with Cascade Configuration

**Use Case**: Precise flow control for chemical dosing system

Flow rate control as inner loop in cascade control system

```json
{
  "processVariable": "DB20.Flow_PV",
  "setPoint": "DB20.Flow_SP_Remote",
  "controlOutput": "DB20.Valve_Position",
  "proportionalGain": 1.8,
  "integralTime": 8,
  "derivativeTime": 2,
  "controllerMode": "cascade",
  "controlAction": "direct",
  "outputLimits": {
    "min": 5,
    "max": 95
  },
  "scanTime": 500,
  "bumplessTransfer": true
}
```

**Expected Output:**
```
Fast flow response with minimal overshoot
```

**Notes:**
- Faster tuning appropriate for inner cascade loop
- Reserve 5% valve travel for safety margin
- Use faster scan time for improved performance

## 🎯 Best Practices

### Configuration
- ✅ **Validate Input Data**: Always verify input data types and ranges before processing
- ✅ **Set Appropriate Timeouts**: Configure reasonable timeout values for industrial networks
- ✅ **Use Meaningful Names**: Give descriptive names to node instances for easy identification
- ✅ **Document Configuration**: Add comments explaining configuration choices
- ✅ **Test in Staging**: Validate configuration in non-production environment first

### Performance
- ✅ **Optimize Polling Intervals**: Balance data freshness with system performance
- ✅ **Monitor Resource Usage**: Track CPU, memory, and network utilization
- ✅ **Use Connection Pooling**: Reuse connections when possible to reduce overhead
- ✅ **Implement Caching**: Cache frequently accessed data to improve response times

### Security
- ✅ **Secure Credentials**: Use secure credential storage, never hardcode passwords
- ✅ **Enable Encryption**: Use encrypted connections when available (TLS/SSL)
- ✅ **Validate Certificates**: Verify SSL certificates in production environments
- ✅ **Implement Rate Limiting**: Protect against excessive requests and abuse

### Maintenance
- ✅ **Regular Updates**: Keep node configurations current with system changes
- ✅ **Monitor Logs**: Regularly review logs for warnings and errors
- ✅ **Backup Configuration**: Maintain backups of working configurations
- ✅ **Plan for Failure**: Implement graceful degradation and error recovery

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: Controller Oscillation

**Symptoms:**
- Process variable oscillates around setpoint
- Control output swings rapidly
- System unstable

**Possible Causes:**
- Proportional gain too high
- Integral time too short
- Derivative time inappropriate
- Measurement noise

**Solutions:**
1. Reduce proportional gain by 50%
2. Increase integral time (slower integral action)
3. Reduce or eliminate derivative action
4. Add measurement filtering
5. Check for mechanical backlash in actuator

**Prevention:**
- Use conservative initial tuning
- Perform step testing before tuning
- Monitor control loop performance

#### Issue 2: Slow Response to Setpoint Changes

**Symptoms:**
- Long time to reach setpoint
- Sluggish response
- Poor disturbance rejection

**Possible Causes:**
- Proportional gain too low
- Integral time too long
- Output limits too restrictive

**Solutions:**
1. Increase proportional gain gradually
2. Decrease integral time (faster integral action)
3. Check and adjust output limits
4. Verify actuator is not saturated
5. Consider cascade control for faster response



#### Issue 3: Integral Windup

**Symptoms:**
- Large overshoot after manual mode
- Slow recovery from disturbances
- Control output stuck at limits

**Possible Causes:**
- Anti-windup disabled
- Output limits reached
- Manual mode operation

**Solutions:**
1. Enable anti-windup protection
2. Verify output limits are appropriate
3. Use bumpless transfer for mode switching
4. Reset integral term when switching to automatic



### Error Codes

| Code | Severity | Message | Solution |
|------|----------|---------|----------|
| `PID_001` | critical | Process variable signal lost | Check PLC communication and sensor wiring |
| `PID_002` | error | Control output failed to respond | Verify actuator power supply and control signal integrity |
| `PID_003` | warning | PID parameters out of valid range | Review and correct PID tuning parameters |

### Diagnostic Procedures
1. Monitor process variable signal for dropouts or noise
2. Check control output signal reaches actuator correctly
3. Verify PID parameters are within recommended ranges
4. Test controller response to manual output changes
5. Analyze control loop performance using trending data

### Getting Help
- **Documentation**: Check this guide and related node documentation
- **Connection Testing**: Use the built-in connection test feature
- **Log Analysis**: Review node execution logs for detailed error information
- **Community Support**: Search forums and community resources
- **Technical Support**: Contact technical support with error codes and logs

## 🔗 Related Nodes

### Input Nodes
*Nodes that commonly provide input to this node*

### Output Nodes  
*Nodes that commonly receive output from this node*

### Complementary Nodes
*Nodes that work well in combination with this node*

- **pid-auto-tuner**: [Brief description of relationship]
- **cascade-controller**: [Brief description of relationship]
- **feedforward-controller**: [Brief description of relationship]
- **analog-input-node**: [Brief description of relationship]
- **analog-output-node**: [Brief description of relationship]
- **plc-input**: [Brief description of relationship]
- **plc-output**: [Brief description of relationship]
- **alarm-handler**: [Brief description of relationship]
- **data-logger**: [Brief description of relationship]

### Integration Patterns
- **Sequential Processing**: Connect output to input of compatible nodes
- **Parallel Processing**: Use multiple instances for load distribution
- **Conditional Logic**: Implement branching logic based on node outputs
- **Feedback Loops**: Create closed-loop control systems

## 🔌 API Reference

### Node Interface
```typescript
interface PidControllerConfig {
  processVariable: string; // PLC address or signal source for the process variable (measured value)
  setPoint: number; // Desired target value for the controlled process variable
  controlOutput: string; // PLC address for the controller output signal to actuator/final control element
  proportionalGain: number; // Proportional gain (Kp) - determines immediate response to error
  integralTime: number; // Integral time constant (Ti) in seconds - eliminates steady-state error
  derivativeTime: number; // Derivative time constant (Td) in seconds - provides anticipatory action
  controllerMode: "automatic" | "manual" | "cascade" | "ratio" | "override"; // Operating mode of the PID controller
  controlAction: "direct" | "reverse"; // Controller action type - direct (heating) or reverse (cooling)
  outputLimits: Record<string, unknown>; // Output signal limits to prevent actuator damage and ensure safe operation
  scanTime?: number; // Controller execution interval in milliseconds
  antiWindupEnabled?: boolean; // Enable integral windup protection when output reaches limits
  bumplessTransfer?: boolean; // Enable smooth transitions between manual and automatic modes
  safetyLimits?: Record<string, unknown>; // Safety limits for process variable - triggers alarms and protective actions
  autoTuneEnabled?: boolean; // Enable automatic PID parameter tuning using relay feedback method
  tuningMethod?: "ziegler-nichols" | "cohen-coon" | "lambda-tuning" | "imc" | "relay-feedback"; // Auto-tuning algorithm selection
}

class PidControllerNode extends IndustrialControlNode {
  config: PidControllerConfig;
  
  async initialize(config: PidControllerConfig): Promise<void>;
  async process(input: NodeInput): Promise<NodeOutput>;
  async validate(): Promise<ValidationResult>;
  async cleanup(): Promise<void>;
}
```

### Configuration Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "processVariable": {
      "type": "string",
      "description": "PLC address or signal source for the process variable (measured value)",
      "default": ""
    },
    "setPoint": {
      "type": "number",
      "description": "Desired target value for the controlled process variable",
      "default": 0
    },
    "controlOutput": {
      "type": "string",
      "description": "PLC address for the controller output signal to actuator/final control element",
      "default": ""
    },
    "proportionalGain": {
      "type": "number",
      "description": "Proportional gain (Kp) - determines immediate response to error",
      "default": 1
    },
    "integralTime": {
      "type": "number",
      "description": "Integral time constant (Ti) in seconds - eliminates steady-state error",
      "default": 60
    },
    "derivativeTime": {
      "type": "number",
      "description": "Derivative time constant (Td) in seconds - provides anticipatory action",
      "default": 15
    },
    "controllerMode": {
      "type": "enum",
      "description": "Operating mode of the PID controller",
      "default": "automatic",
      "enum": ["automatic","manual","cascade","ratio","override"]
    },
    "controlAction": {
      "type": "enum",
      "description": "Controller action type - direct (heating) or reverse (cooling)",
      "default": "direct",
      "enum": ["direct","reverse"]
    },
    "outputLimits": {
      "type": "object",
      "description": "Output signal limits to prevent actuator damage and ensure safe operation",
      "default": {"min":0,"max":100}
    },
    "scanTime": {
      "type": "number",
      "description": "Controller execution interval in milliseconds",
      "default": 1000
    },
    "antiWindupEnabled": {
      "type": "boolean",
      "description": "Enable integral windup protection when output reaches limits",
      "default": true
    },
    "bumplessTransfer": {
      "type": "boolean",
      "description": "Enable smooth transitions between manual and automatic modes",
      "default": true
    },
    "safetyLimits": {
      "type": "object",
      "description": "Safety limits for process variable - triggers alarms and protective actions",
      "default": {"pvHigh":1000,"pvLow":-1000}
    },
    "autoTuneEnabled": {
      "type": "boolean",
      "description": "Enable automatic PID parameter tuning using relay feedback method",
      "default": false
    },
    "tuningMethod": {
      "type": "enum",
      "description": "Auto-tuning algorithm selection",
      "default": "ziegler-nichols",
      "enum": ["ziegler-nichols","cohen-coon","lambda-tuning","imc","relay-feedback"]
    }
  },
  "required": ["processVariable", "setPoint", "controlOutput", "proportionalGain", "integralTime", "derivativeTime", "controllerMode", "controlAction", "outputLimits"]
}
```

### Events
- **`onInitialize`**: Fired when node is initialized
- **`onProcess`**: Fired when node processes input data
- **`onError`**: Fired when an error occurs
- **`onValidationChange`**: Fired when validation status changes
- **`onConfigurationChange`**: Fired when configuration is modified

## 📚 Additional Resources

### External Documentation
- [ISA-5.1: Instrumentation Symbols and Identification](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa51) - Standard symbols for process control and instrumentation
- [PID Control Theory and Practice](https://controlguru.com/pid-control-theory-and-practice/) - Comprehensive guide to PID controller theory and implementation
- [Advanced PID Control by Karl Astrom](https://www.cds.caltech.edu/~murray/amwiki/index.php/PID_Control) - Academic reference on advanced PID control techniques

### Standards and Specifications
- **Industry Standards**: Review applicable industry standards for this node type
- **Protocol Documentation**: Consult official protocol documentation where applicable
- **Safety Guidelines**: Follow industrial safety guidelines for control system implementation

### Training and Certification
- **Product Training**: Available through official training programs
- **Certification**: Professional certification programs for industrial automation
- **Continuing Education**: Stay current with industry developments and best practices

---

**Document Version**: 2.1.0  
**Last Updated**: 2025-01-15  
**Applies to PLC-GBT Version**: 2.0+  
**Template Category**: plc_control

*This documentation is automatically generated from the node specification. For updates or corrections, please modify the source specification file.*

---

## 📝 Documentation Metadata

- **Node Type ID**: `pid-controller`
- **Category**: PLC Control Nodes (`plc_control`)
- **Template Extensions**: control-theory, tuning-guidelines, stability-analysis
- **Generated**: 2025-08-21T14:32:20.876Z
- **Documentation System**: PLC-GBT Node Documentation Generator v1.0

*This document follows the [PLC-GBT Documentation Standards](../documentation-standards.md) and is part of the comprehensive node documentation system.*

## 🎛️ Control Theory

### Algorithm Description
*Mathematical description and theoretical foundation of the control algorithm*

### Tuning Guidelines
*Step-by-step tuning procedure for optimal performance*

1. **Initial Setup**: Configure basic parameters
2. **System Identification**: Characterize the process dynamics  
3. **Controller Design**: Apply appropriate tuning method
4. **Performance Validation**: Test and optimize performance
5. **Robustness Analysis**: Verify stability margins

### Stability Considerations
*Stability analysis and constraint guidelines*

- **Gain Margins**: Maintain adequate gain margins (>6dB recommended)
- **Phase Margins**: Ensure sufficient phase margins (>45° recommended)  
- **Bandwidth Limits**: Consider actuator and sensor bandwidth limitations
- **Nonlinear Effects**: Account for nonlinearities and saturation limits