# Math Function Creator - Industrial Control Node

**Node Type**: `math-function-creator`  
**Category**: Data Processing Nodes  
**Version**: 1.5.0  
**Last Updated**: 2025-01-15

---

Advanced mathematical function builder with scientific calculator, custom equation editor, and comprehensive mathematical operation support for process calculations

## 🎯 Overview

### Purpose
Advanced mathematical function creator enabling custom equation development with integrated scientific calculator, comprehensive validation, and industrial-grade numerical processing capabilities

### Key Features
- **Scientific Calculator**:  Integrated calculator with scientific, engineering, and programming modes
- **Custom Equations**:  Support for complex mathematical expressions with multiple variables
- **Function Validation**:  Comprehensive testing framework with domain checking and test cases
- **Unit Conversion**:  Automatic unit conversion and dimensional analysis capabilities
- **High Precision**:  Multiple precision modes including arbitrary precision arithmetic
- **Error Handling**:  Robust error handling with configurable responses to mathematical exceptions
- **Industrial Integration**:  Seamless integration with process control and data acquisition systems

### When to Use This Node
- **Complex Calculations**:  When standard math functions are insufficient
- **Custom Algorithms**:  Implementing proprietary or specialized mathematical models
- **Multi-variable Functions**:  When calculations involve multiple input parameters
- **Precision Requirements**:  When high numerical accuracy is critical
- **Unit Conversions**:  When automatic unit conversion is needed
- **Validation Needs**:  When mathematical accuracy must be verified with test cases

### Industrial Applications
- Chemical Engineering: Reaction kinetics, thermodynamic calculations, mass transfer
- Mechanical Systems: Stress analysis, vibration analysis, fluid dynamics
- Electrical Power: Load calculations, power factor correction, harmonics analysis
- Process Control: Advanced control algorithms, optimization functions
- Quality Assurance: Statistical process control, capability studies
- Environmental: Emissions calculations, environmental impact assessments

## ⚙️ Configuration Guide

### Quick Start
1. Drag Math Function Creator from data processing palette
2. Enter descriptive function name and mathematical equation
3. Define all variables used in the equation
4. Enable scientific calculator for equation development and testing
5. Configure domain limits to ensure safe input ranges
6. Add test cases to validate function accuracy
7. Connect input nodes providing variable values
8. Connect output to downstream calculation or control nodes

### Detailed Setup

#### Step 1: Function Definition
Define the mathematical function name and equation

**Required Parameters:**
- `functionName`
- `equation`
- `variables`

**Example Configuration:**
```json
{
  "functionName": "FlowCalculation",
  "equation": "Cv * sqrt(deltaP / SG)",
  "variables": ["Cv", "deltaP", "SG"]
}
```

#### Step 2: Calculator Integration
Configure the integrated scientific calculator

**Required Parameters:**
- `calculatorEnabled`
- `calculatorMode`
- `angleMode`

**Example Configuration:**
```json
{
  "calculatorEnabled": true,
  "calculatorMode": "scientific",
  "angleMode": "radians"
}
```

#### Step 3: Validation Setup
Configure domain limits and test cases for validation

**Required Parameters:**
- `domainLimits`
- `testCases`
- `rangeValidation`

**Example Configuration:**
```json
{
  "domainLimits": { "deltaP": { "min": 0, "max": 1000 } },
  "testCases": [{ "inputs": {"Cv": 1.0, "deltaP": 100, "SG": 1.0}, "expected": 10.0 }]
}
```

### Best Practices
- ✅ Use descriptive function names that indicate the calculation purpose
- ✅ Define comprehensive test cases covering normal and edge case scenarios
- ✅ Set appropriate domain limits to prevent invalid inputs
- ✅ Use the scientific calculator to validate equations before deployment
- ✅ Configure proper error handling for division by zero and overflow conditions
- ✅ Document equation sources and assumptions for future reference
- ✅ Test functions with real process data before production use

### Common Mistakes to Avoid
- ❌ Forgetting to define all variables used in the equation
- ❌ Not setting domain limits leading to invalid calculations
- ❌ Using incorrect mathematical operator precedence
- ❌ Ignoring unit consistency in multi-variable equations
- ❌ Not testing edge cases like zero and negative inputs
- ❌ Overlooking numerical precision requirements for critical calculations

## 📊 Parameters Reference

### Essential Parameters

| Parameter | Type | Default | Range | Units | Description |
|-----------|------|---------|-------|-------|-------------|
| `functionName` | string | `"CustomFunction"` | - | - | Descriptive name for the mathematical function |
| `equation` | string | `"x"` | - | - | Mathematical equation using standard mathematical notation and functions |
| `variables` | array | `x` | - | - | List of input variables used in the equation |

### Advanced Parameters

| Parameter | Type | Default | Description | Notes |
|-----------|------|---------|-------------|-------|
| `calculatorEnabled` | boolean | `true` | Enable integrated scientific calculator for equation development and testing | Advanced parameter |
| `calculatorMode` | enum | `"scientific"` | Calculator operation mode | Options: basic, scientific, engineering, programmer |
| `angleMode` | enum | `"radians"` | Angle measurement mode for trigonometric functions | Options: radians, degrees, gradians |
| `domainLimits` | object | `[object Object]` | Input variable domain restrictions and validation limits | Advanced parameter |
| `rangeValidation` | object | `[object Object]` | Output range validation and limiting configuration | Advanced parameter |
| `testCases` | array | `` | Test cases for function validation with expected outputs | Advanced parameter |
| `precision` | enum | `"double"` | Numerical precision for calculations | Options: single, double, extended, arbitrary |
| `customConstants` | object | `[object Object]` | User-defined mathematical constants for use in equations | Advanced parameter |
| `unitConversion` | object | `[object Object]` | Automatic unit conversion and dimensional analysis | Advanced parameter |
| `errorHandling` | enum | `"strict"` | Error handling mode for mathematical operations | Options: strict, permissive, custom |
| `divisionByZeroAction` | enum | `"error"` | Action when division by zero is encountered | Options: error, infinity, nan, custom_value |
| `overflowProtection` | boolean | `true` | Enable protection against numerical overflow and underflow | Advanced parameter |

### Parameter Validation Rules
- **ERROR**: Mathematical equation contains syntax errors or undefined elements (Verify equation syntax and ensure all variables are defined)
- **ERROR**: Equation uses variables not defined in the variables list (Add all equation variables to the variables list)
- **WARNING**: Domain limits specified for undefined variables (Remove unused domain limits or add missing variables)
- **INFO**: No test cases defined for function validation (Add test cases to verify function correctness)

## 💡 Examples

### Example 1: Orifice Plate Flow Calculation

**Use Case**: Industrial flow measurement in process plants

Calculate volumetric flow rate through an orifice plate using differential pressure

```json
{
  "functionName": "OrificeFlowCalculation",
  "equation": "Cd * A * sqrt((2 * deltaP * gc) / (rho * (1 - beta^4)))",
  "variables": [
    "Cd",
    "A",
    "deltaP",
    "rho",
    "beta",
    "gc"
  ],
  "customConstants": {
    "gc": 32.174,
    "pi": 3.14159265359
  },
  "domainLimits": {
    "deltaP": {
      "min": 0,
      "max": 1000
    },
    "rho": {
      "min": 0.1,
      "max": 1000
    },
    "beta": {
      "min": 0.1,
      "max": 0.8
    },
    "Cd": {
      "min": 0.5,
      "max": 1
    }
  },
  "unitConversion": {
    "enabled": true,
    "inputUnits": {
      "deltaP": "psi",
      "rho": "lb/ft3"
    },
    "outputUnit": "ft3/min"
  },
  "testCases": [
    {
      "inputs": {
        "Cd": 0.61,
        "A": 0.785,
        "deltaP": 10,
        "rho": 62.4,
        "beta": 0.5
      },
      "expected": 156.2,
      "tolerance": 0.1
    }
  ]
}
```

**Expected Output:**
```
Calculated volumetric flow rate with unit conversion
```

**Notes:**
- Discharge coefficient (Cd) typically ranges from 0.6-0.65 for sharp-edged orifices
- Beta ratio should be between 0.1-0.8 for accurate results
- Include gravitational constant (gc) for proper unit consistency

### Example 2: Temperature Compensation Formula

**Use Case**: Sensor calibration and temperature compensation in measurement systems

Compensate sensor readings for temperature effects using polynomial correction

```json
{
  "functionName": "TemperatureCompensation",
  "equation": "rawValue * (1 + a1*(T - Tref) + a2*(T - Tref)^2 + a3*(T - Tref)^3)",
  "variables": [
    "rawValue",
    "T",
    "Tref",
    "a1",
    "a2",
    "a3"
  ],
  "customConstants": {
    "Tref": 25
  },
  "domainLimits": {
    "T": {
      "min": -40,
      "max": 150
    },
    "rawValue": {
      "min": 0,
      "max": 10000
    }
  },
  "rangeValidation": {
    "enabled": true,
    "min": -99999,
    "max": 99999,
    "action": "clamp"
  },
  "precision": "double",
  "testCases": [
    {
      "inputs": {
        "rawValue": 100,
        "T": 50,
        "a1": 0.002,
        "a2": -0.00001,
        "a3": 0
      },
      "expected": 104.9875,
      "tolerance": 0.001
    }
  ]
}
```

**Expected Output:**
```
Temperature-compensated measurement value
```

**Notes:**
- Polynomial coefficients (a1, a2, a3) must be determined from calibration data
- Reference temperature (Tref) should match calibration conditions
- Higher-order terms may be needed for wide temperature ranges

### Example 3: PID Output Calculation with Feedforward

**Use Case**: Advanced process control with feedforward action

Custom PID controller output with feedforward compensation

```json
{
  "functionName": "PIDwithFeedforward",
  "equation": "Kp*error + Ki*integral + Kd*derivative + Kf*feedforward",
  "variables": [
    "error",
    "integral",
    "derivative",
    "feedforward",
    "Kp",
    "Ki",
    "Kd",
    "Kf"
  ],
  "domainLimits": {
    "Kp": {
      "min": 0,
      "max": 100
    },
    "Ki": {
      "min": 0,
      "max": 10
    },
    "Kd": {
      "min": 0,
      "max": 100
    },
    "Kf": {
      "min": 0,
      "max": 10
    }
  },
  "rangeValidation": {
    "enabled": true,
    "min": 0,
    "max": 100,
    "action": "clamp"
  },
  "calculatorEnabled": true,
  "calculatorMode": "engineering"
}
```

**Expected Output:**
```
Combined PID and feedforward control output
```

**Notes:**
- Feedforward gain (Kf) should be tuned based on process dynamics
- Output limiting prevents actuator damage and windup
- Consider derivative filtering for noisy process variables

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

#### Issue 1: Equation Parsing Error

**Symptoms:**
- Function fails to evaluate
- Syntax error messages
- Invalid operator errors

**Possible Causes:**
- Incorrect mathematical syntax
- Undefined variables
- Unsupported functions
- Mismatched parentheses

**Solutions:**
1. Verify equation syntax using the scientific calculator
2. Check that all variables are defined in the variables list
3. Review mathematical operator usage and precedence
4. Validate parentheses placement and matching
5. Test equation components individually



#### Issue 2: Numerical Overflow or Underflow

**Symptoms:**
- Results show infinity or NaN
- Unexpected very large or small numbers
- Calculation errors

**Possible Causes:**
- Input values too large or small
- Mathematical operations causing overflow
- Division by very small numbers

**Solutions:**
1. Enable overflow protection in configuration
2. Set appropriate domain limits for input variables
3. Review mathematical operations for potential overflow conditions
4. Consider using higher precision arithmetic mode
5. Implement result range validation and clamping



#### Issue 3: Inaccurate Results

**Symptoms:**
- Results differ from expected values
- Test cases fail
- Inconsistent calculations

**Possible Causes:**
- Incorrect equation formulation
- Precision limitations
- Unit conversion errors
- Input data quality issues

**Solutions:**
1. Verify equation against reference sources or documentation
2. Increase numerical precision setting if needed
3. Check unit conversion configuration and consistency
4. Validate input data quality and ranges
5. Add more comprehensive test cases to identify issues



### Error Codes

| Code | Severity | Message | Solution |
|------|----------|---------|----------|
| `MATH_001` | error | Equation syntax error | Review and correct mathematical equation syntax |
| `MATH_002` | error | Undefined variable in equation | Add missing variables to the variables list |
| `MATH_003` | warning | Division by zero detected | Check input values and configure division by zero handling |
| `MATH_004` | warning | Input value outside domain limits | Verify input values are within configured domain limits |

### Diagnostic Procedures
1. Test equation syntax using the integrated scientific calculator
2. Verify all variables are properly defined and connected
3. Check test cases execution and compare results with expected values
4. Monitor numerical precision and overflow protection settings
5. Validate input data ranges against configured domain limits

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

- **data-cleaner**: [Brief description of relationship]
- **feature-engineer**: [Brief description of relationship]
- **time-series-processor**: [Brief description of relationship]
- **pid-controller**: [Brief description of relationship]
- **performance-metrics**: [Brief description of relationship]
- **kpi-calculator**: [Brief description of relationship]
- **dashboard-generator**: [Brief description of relationship]

### Integration Patterns
- **Sequential Processing**: Connect output to input of compatible nodes
- **Parallel Processing**: Use multiple instances for load distribution
- **Conditional Logic**: Implement branching logic based on node outputs
- **Feedback Loops**: Create closed-loop control systems

## 🔌 API Reference

### Node Interface
```typescript
interface MathFunctionCreatorConfig {
  functionName: string; // Descriptive name for the mathematical function
  equation: string; // Mathematical equation using standard mathematical notation and functions
  variables: unknown[]; // List of input variables used in the equation
  calculatorEnabled?: boolean; // Enable integrated scientific calculator for equation development and testing
  calculatorMode?: "basic" | "scientific" | "engineering" | "programmer"; // Calculator operation mode
  angleMode?: "radians" | "degrees" | "gradians"; // Angle measurement mode for trigonometric functions
  domainLimits?: Record<string, unknown>; // Input variable domain restrictions and validation limits
  rangeValidation?: Record<string, unknown>; // Output range validation and limiting configuration
  testCases?: unknown[]; // Test cases for function validation with expected outputs
  precision?: "single" | "double" | "extended" | "arbitrary"; // Numerical precision for calculations
  customConstants?: Record<string, unknown>; // User-defined mathematical constants for use in equations
  unitConversion?: Record<string, unknown>; // Automatic unit conversion and dimensional analysis
  errorHandling?: "strict" | "permissive" | "custom"; // Error handling mode for mathematical operations
  divisionByZeroAction?: "error" | "infinity" | "nan" | "custom_value"; // Action when division by zero is encountered
  overflowProtection?: boolean; // Enable protection against numerical overflow and underflow
}

class MathFunctionCreatorNode extends IndustrialControlNode {
  config: MathFunctionCreatorConfig;
  
  async initialize(config: MathFunctionCreatorConfig): Promise<void>;
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
    "functionName": {
      "type": "string",
      "description": "Descriptive name for the mathematical function",
      "default": "CustomFunction"
    },
    "equation": {
      "type": "string",
      "description": "Mathematical equation using standard mathematical notation and functions",
      "default": "x"
    },
    "variables": {
      "type": "array",
      "description": "List of input variables used in the equation",
      "default": ["x"]
    },
    "calculatorEnabled": {
      "type": "boolean",
      "description": "Enable integrated scientific calculator for equation development and testing",
      "default": true
    },
    "calculatorMode": {
      "type": "enum",
      "description": "Calculator operation mode",
      "default": "scientific",
      "enum": ["basic","scientific","engineering","programmer"]
    },
    "angleMode": {
      "type": "enum",
      "description": "Angle measurement mode for trigonometric functions",
      "default": "radians",
      "enum": ["radians","degrees","gradians"]
    },
    "domainLimits": {
      "type": "object",
      "description": "Input variable domain restrictions and validation limits",
      "default": {}
    },
    "rangeValidation": {
      "type": "object",
      "description": "Output range validation and limiting configuration",
      "default": {"enabled":false}
    },
    "testCases": {
      "type": "array",
      "description": "Test cases for function validation with expected outputs",
      "default": []
    },
    "precision": {
      "type": "enum",
      "description": "Numerical precision for calculations",
      "default": "double",
      "enum": ["single","double","extended","arbitrary"]
    },
    "customConstants": {
      "type": "object",
      "description": "User-defined mathematical constants for use in equations",
      "default": {}
    },
    "unitConversion": {
      "type": "object",
      "description": "Automatic unit conversion and dimensional analysis",
      "default": {"enabled":false}
    },
    "errorHandling": {
      "type": "enum",
      "description": "Error handling mode for mathematical operations",
      "default": "strict",
      "enum": ["strict","permissive","custom"]
    },
    "divisionByZeroAction": {
      "type": "enum",
      "description": "Action when division by zero is encountered",
      "default": "error",
      "enum": ["error","infinity","nan","custom_value"]
    },
    "overflowProtection": {
      "type": "boolean",
      "description": "Enable protection against numerical overflow and underflow",
      "default": true
    }
  },
  "required": ["functionName", "equation", "variables"]
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
- [Mathematical Expression Evaluation](https://mathjs.org/docs/expressions/syntax.html) - Comprehensive guide to mathematical expression syntax
- [Engineering Mathematics Handbook](https://www.engineeringtoolbox.com/) - Reference for engineering calculations and formulas
- [Numerical Methods and Scientific Computing](https://numerical.recipes/) - Advanced numerical methods and computational techniques

### Standards and Specifications
- **Industry Standards**: Review applicable industry standards for this node type
- **Protocol Documentation**: Consult official protocol documentation where applicable
- **Safety Guidelines**: Follow industrial safety guidelines for control system implementation

### Training and Certification
- **Product Training**: Available through official training programs
- **Certification**: Professional certification programs for industrial automation
- **Continuing Education**: Stay current with industry developments and best practices

---

**Document Version**: 1.5.0  
**Last Updated**: 2025-01-15  
**Applies to PLC-GBT Version**: 2.0+  
**Template Category**: data_processing

*This documentation is automatically generated from the node specification. For updates or corrections, please modify the source specification file.*

---

## 📝 Documentation Metadata

- **Node Type ID**: `math-function-creator`
- **Category**: Data Processing Nodes (`data_processing`)
- **Template Extensions**: data-transformation, processing-algorithms, performance-optimization
- **Generated**: 2025-08-21T14:32:20.879Z
- **Documentation System**: PLC-GBT Node Documentation Generator v1.0

*This document follows the [PLC-GBT Documentation Standards](../documentation-standards.md) and is part of the comprehensive node documentation system.*

## 🔄 Data Processing Operations

### Data Transformation
*Available transformation operations and configurations*

### Processing Algorithms  
*Algorithm selection and parameter tuning*

### Performance Optimization
*Optimization strategies for large-scale data processing*

- **Memory Management**: Optimize memory usage for large datasets
- **Parallel Processing**: Utilize multi-core processing capabilities  
- **Streaming Processing**: Configure for real-time data streams
- **Batch Processing**: Optimize batch size for throughput