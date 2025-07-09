# Phase 8: PID Tuning Integration - Complete API Documentation

## 🎯 Overview

This document provides comprehensive API documentation for all Phase 8 PID Tuning Integration components, following AI Task Orchestrator Guide methodology for systematic documentation. This covers all 10 days of Phase 8 implementation with complete endpoint reference, integration examples, and usage patterns.

## 📋 Table of Contents

1. [Schema Definitions](#schema-definitions)
2. [Core PID API Endpoints](#core-pid-api-endpoints)
3. [Advanced Control Features API](#advanced-control-features-api) 
4. [Enterprise Security API](#enterprise-security-api)
5. [Performance Monitoring API](#performance-monitoring-api)
6. [Training & Validation API](#training--validation-api)
7. [Integration Examples](#integration-examples)
8. [Authentication & Security](#authentication--security)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)
11. [SDK & Client Libraries](#sdk--client-libraries)

---

## Schema Definitions

### Multi-Variable Scaling Configuration Schema

The Phase 8 system supports multiple process variables and disturbance variables for comprehensive control. Each scaling configuration includes tagname identification and complete raw-to-engineering unit conversion.

#### Variable Types:
- **pv01_scaling, pv02_scaling**: Primary and secondary process variables
- **dv01_scaling, dv02_scaling**: Disturbance variables for feed-forward control
- **cv_limits**: Control variable limits with tagname identification

#### Scaling Schema Structure:
```json
{
  "pv01_scaling": {
    "tagname": "string",      // PLC tag identifier (required)
    "raw_min": "integer",     // Raw ADC minimum value
    "raw_max": "integer",     // Raw ADC maximum value  
    "eng_min": "number",      // Engineering unit minimum
    "eng_max": "number",      // Engineering unit maximum
    "units": "string"         // Engineering units (°C, °F, psi, GPM, Hz, etc.)
  },
  "pv02_scaling": {
    "tagname": "string",
    "raw_min": "integer", 
    "raw_max": "integer",
    "eng_min": "number",
    "eng_max": "number", 
    "units": "string"
  },
  "dv01_scaling": {
    "tagname": "string",
    "raw_min": "integer",
    "raw_max": "integer", 
    "eng_min": "number",
    "eng_max": "number",
    "units": "string"
  },
  "dv02_scaling": {
    "tagname": "string",
    "raw_min": "integer",
    "raw_max": "integer",
    "eng_min": "number", 
    "eng_max": "number",
    "units": "string"
  },
  "cv_limits": {
    "tagname": "string",      // Control output tag identifier
    "min": "number",          // Minimum control output
    "max": "number",          // Maximum control output
    "units": "string"         // Output units (%, Hz, mA, etc.)
  }
}
```

#### Common Unit Types:
- **Temperature**: °C, °F, K, °R
- **Pressure**: psi, bar, kPa, MPa, inHg, mmHg
- **Flow**: GPM, LPM, CFM, m³/h, kg/h
- **Level**: %, ft, m, inches
- **Frequency**: Hz, RPM
- **Electrical**: mA, V, %, Hz

#### Example Standardized Multi-Variable Configuration:
```json
{
  "instance_name": "REACTOR_TEMP_CONTROL_001",
  "schema_version": "1.0.0",
  
  "metadata": {
    "created_timestamp": "2025-07-09T12:30:00Z",
    "updated_timestamp": "2025-07-09T12:30:00Z", 
    "schema_type": "phase8_pid_control",
    "created_by": "api_configuration_system",
    "description": "Production reactor temperature control with advanced multi-variable strategy",
    "tags": ["production", "reactor", "temperature", "cascade"],
    "process_information": {
      "process_type": "temperature",
      "industry_sector": "chemical",
      "safety_level": "SIL2",
      "environmental_conditions": {
        "temperature_range": {"value": 22, "units": "°C"},
        "humidity_range": "35-65%",
        "vibration_level": "medium",
        "hazardous_area": true
      }
    },
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T12:30:00Z",
      "validation_score": 1.0,
      "issues": []
    }
  },
  
  "variable_counts": {
    "total_variables": 5,
    "process_variables_count": 2,
    "disturbance_variables_count": 2,
    "control_variables_count": 1
  },
  
  "data": {
    "control_configuration": {
      "loop_id": "REACTOR_TEMP_001",
      "algorithm_form": "dependent",
      "instruction_type": "PIDE", 
      "control_mode": "CASCADE"
    },
    
    "variable_definitions": {
      "process_variables": [
        {
          "variable_id": "pv01",
          "tagname": {
            "tagname": "TIT_2035",
            "data_type": "REAL",
            "description": "Primary reactor temperature measurement"
          },
          "scaling": {
            "raw_min": 0,
            "raw_max": 4095,
            "eng_min": 0.0,
            "eng_max": 100.0,
            "units": "°C",
            "linearization": "linear"
          },
          "alarm_limits": {
            "high_high": 95.0,
            "high": 90.0,
            "low": 10.0,
            "low_low": 5.0,
            "rate_of_change": 5.0
          }
        },
        {
          "variable_id": "pv02",
          "tagname": {
            "tagname": "TIT_2045",
            "data_type": "REAL", 
            "description": "Secondary reactor temperature for redundancy"
          },
          "scaling": {
            "raw_min": 0,
            "raw_max": 4095,
            "eng_min": 0.0,
            "eng_max": 100.0,
            "units": "°C",
            "linearization": "linear"
          },
          "alarm_limits": {
            "high_high": 95.0,
            "high": 90.0,
            "low": 10.0,
            "low_low": 5.0,
            "rate_of_change": 5.0
          }
        }
      ],
      
      "disturbance_variables": [
        {
          "variable_id": "dv01",
          "tagname": {
            "tagname": "PIT_2055",
            "data_type": "REAL",
            "description": "Feed stream pressure for feed-forward control"
          },
          "scaling": {
            "raw_min": 0,
            "raw_max": 4095,
            "eng_min": 0.0,
            "eng_max": 50.0,
            "units": "psi"
          },
          "feedforward_config": {
            "enabled": true,
            "gain": 0.85,
            "lead_time": 8.0,
            "lag_time": 3.0
          }
        },
        {
          "variable_id": "dv02",
          "tagname": {
            "tagname": "TIT_2055",
            "data_type": "REAL",
            "description": "Feed stream temperature for anticipatory control"
          },
          "scaling": {
            "raw_min": 0,
            "raw_max": 4095,
            "eng_min": 32.0,
            "eng_max": 212.0,
            "units": "°F"
          },
          "feedforward_config": {
            "enabled": true,
            "gain": 1.15,
            "lead_time": 5.0,
            "lag_time": 2.0
          }
        }
      ],
      
      "control_variables": [
        {
          "variable_id": "cv01",
          "tagname": {
            "tagname": "PMP_2055.Hz",
            "data_type": "REAL",
            "description": "Cooling system pump frequency control output"
          },
          "limits": {
            "min": 0.0,
            "max": 60.0,
            "units": "Hz",
            "rate_limit": 3.0
          },
          "actuator_characteristics": {
            "type": "pump",
            "action": "reverse",
            "response_time": 3.2
          }
        }
      ]
    },
    
    "tuning_parameters": {
      "current_parameters": {
        "kc": 1.8,
        "ti": 12.0,
        "td": 3.0,
        "bias": 45.0,
        "setpoint": 85.0
      },
      "tuning_history": [
        {
          "timestamp": "2025-07-09T08:00:00Z",
          "method": "imc",
          "parameters": {
            "kc": 1.8,
            "ti": 12.0,
            "td": 3.0
          },
          "performance_before": {
            "excellent": 2.5,
            "good": 5.0,
            "acceptable": 10.0
          },
          "performance_after": {
            "excellent": 1.2,
            "good": 2.8,
            "acceptable": 6.5
          }
        }
      ]
    }
  }
}
```

---

## Core PID API Endpoints

### 1. PID Loop Management

#### `POST /api/v1/pid/loops`
**Create new PID loop configuration**

```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "temperature",
      "pressure",
      "flow",
      "control",
      "api"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "temperature",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 41,
    "process_variables_count": 3,
    "disturbance_variables_count": 2,
    "control_variables_count": 2,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 34
  },
  "data": {
    "loop_id": "LOOP_001",
    "process_type": "temperature",
    "algorithm_form": "dependent",
    "instruction_type": "PIDE",
    "control_mode": "PID",
    "kc": 1.5,
    "ti": 10.0,
    "td": 2.5,
    "pv01_scaling": {
      "tagname": "TIT_2035",
      "raw_min": 0,
      "raw_max": 4095,
      "eng_min": 0.0,
      "eng_max": 150.0,
      "units": "\u00b0C"
    },
    "pv02_scaling": {
      "tagname": "TIT_2045",
      "raw_min": 0,
      "raw_max": 4095,
      "eng_min": 0.0,
      "eng_max": 150.0,
      "units": "\u00b0C"
    },
    "dv01_scaling": {
      "tagname": "PIT_2055",
      "raw_min": 0,
      "raw_max": 4095,
      "eng_min": 0.0,
      "eng_max": 50.0,
      "units": "psi"
    },
    "dv02_scaling": {
      "tagname": "FIT_2065",
      "raw_min": 0,
      "raw_max": 4095,
      "eng_min": 0.0,
      "eng_max": 1000.0,
      "units": "GPM"
    },
    "cv_limits": {
      "tagname": "VLV_2055.Position",
      "min": 0.0,
      "max": 100.0,
      "units": "%"
    }
  }
}
```

**Response:**
```json
{
  "instance_name": "VALIDATION_FRAMEWORK_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api",
      "validation"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 5,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 1,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 4
  },
  "data": {
    "success": true,
    "loop_id": "LOOP_001",
    "status": "created",
    "validation_score": 0.95,
    "created_timestamp": "2025-01-10T10:00:00Z"
  }
}
```

#### `GET /api/v1/pid/loops/{loop_id}`
**Retrieve PID loop configuration and status**

**Response:**
```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api",
      "performance"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 13,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 1,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 2,
    "configuration_items_count": 10
  },
  "data": {
    "loop_id": "LOOP_001",
    "status": "active",
    "current_performance": {
      "mae": 2.1,
      "iae": 15.3,
      "oscillation_index": 0.12,
      "cv_saturation": 0.05
    },
    "tuning_parameters": {
      "kc": 1.5,
      "ti": 10.0,
      "td": 2.5
    },
    "last_tuned": "2025-01-10T09:30:00Z",
    "performance_trend": "improving"
  }
}
```

#### `PUT /api/v1/pid/loops/{loop_id}/tune`
**Execute automated tuning procedure**

```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "api",
      "validation",
      "safety"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 8,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 1,
    "validation_checks_count": 2,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 5
  },
  "data": {
    "tuning_method": "ziegler_nichols",
    "test_type": "step_test",
    "test_parameters": {
      "step_size": 5.0,
      "duration": 300
    },
    "safety_limits": {
      "max_cv_change": 10.0,
      "abort_conditions": [
        "cv_saturation",
        "pv_deviation"
      ]
    }
  }
}
```

### 2. Multi-PV Control Strategy

#### `POST /api/v1/pid/multi-pv`
**Configure multi-PV averaging and control strategy**

```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "temperature",
      "flow",
      "control",
      "api"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "temperature",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 9,
    "process_variables_count": 2,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 7
  },
  "data": {
    "strategy_id": "MULTI_PV_001",
    "primary_pv": "TT_001",
    "secondary_pvs": [
      "TT_002",
      "TT_003"
    ],
    "weighting_method": "distance_based",
    "weights": [
      0.6,
      0.25,
      0.15
    ],
    "cascade_configuration": {
      "enabled": true,
      "primary_loop": "TEMP_PRIMARY",
      "secondary_loop": "FLOW_SECONDARY"
    }
  }
}
```

### 3. Advanced Control Features

#### `POST /api/v1/pid/advanced/feedforward`
**Configure feed-forward control**

```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "flow",
      "control",
      "api"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "flow",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 7,
    "process_variables_count": 0,
    "disturbance_variables_count": 1,
    "control_variables_count": 0,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 6
  },
  "data": {
    "loop_id": "LOOP_001",
    "disturbance_variable": "FLOW_DIST",
    "ff_gain": 0.8,
    "lead_compensation": {
      "enabled": true,
      "lead_time": 5.0
    },
    "ff_limits": [
      -50.0,
      50.0
    ]
  }
}
```

#### `POST /api/v1/pid/advanced/smith-predictor`
**Configure Smith predictor for dead-time compensation**

```json
{
  "instance_name": "VALIDATION_FRAMEWORK_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api",
      "validation",
      "training"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 8,
    "process_variables_count": 1,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 2,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 5
  },
  "data": {
    "loop_id": "LOOP_001",
    "process_model": {
      "gain": 1.2,
      "time_constant": 30.0,
      "dead_time": 45.0
    },
    "model_validation": {
      "r_squared": 0.92,
      "validation_date": "2025-01-10T08:00:00Z"
    }
  }
}
```

---

## Advanced Control Features API

### 1. Model Predictive Control (MPC)

#### `POST /api/v1/pid/mpc/controller`
**Create MPC controller configuration**

```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 10,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 6,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 4
  },
  "data": {
    "controller_id": "MPC_001",
    "prediction_horizon": 20,
    "control_horizon": 5,
    "constraints": {
      "cv_min": [
        0.0,
        0.0
      ],
      "cv_max": [
        100.0,
        100.0
      ],
      "delta_cv_max": [
        5.0,
        5.0
      ]
    },
    "objective_weights": {
      "tracking": [
        1.0,
        1.0
      ],
      "cv_penalty": [
        0.1,
        0.1
      ]
    }
  }
}
```

### 2. Adaptive Control

#### `POST /api/v1/pid/adaptive/estimator`
**Configure real-time parameter estimation**

```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 7,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 7
  },
  "data": {
    "loop_id": "LOOP_001",
    "estimation_method": "recursive_least_squares",
    "adaptation_rate": 0.95,
    "parameter_bounds": {
      "kc": [
        0.1,
        10.0
      ],
      "ti": [
        1.0,
        100.0
      ],
      "td": [
        0.0,
        20.0
      ]
    }
  }
}
```

---

## Enterprise Security API

### 1. Authentication & Authorization

#### `POST /api/v1/auth/login`
**Authenticate user with enterprise credentials**

```json
{
  "instance_name": "AUTH_CONFIGURATION_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "api_configuration",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized api configuration configuration",
    "tags": [
      "api"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    }
  },
  "variable_counts": {
    "total_variables": 4,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 4
  },
  "data": {
    "username": "engineer@company.com",
    "password": "secure_password",
    "authentication_method": "ldap",
    "domain": "company.local"
  }
}
```

**Response:**
```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api",
      "performance"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 5,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 5
  },
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user_roles": [
      "pid_engineer",
      "system_operator"
    ],
    "permissions": [
      "tune_loops",
      "view_performance",
      "modify_parameters"
    ]
  }
}
```

#### `GET /api/v1/auth/permissions`
**Get user permissions and role-based access**

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. Audit Logging

#### `GET /api/v1/audit/logs`
**Retrieve audit logs with filtering**

**Query Parameters:**
- `start_date`: ISO 8601 timestamp
- `end_date`: ISO 8601 timestamp  
- `user_id`: Filter by user
- `action_type`: Filter by action type
- `loop_id`: Filter by PID loop

**Response:**
```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 13,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 13
  },
  "data": {
    "logs": [
      {
        "timestamp": "2025-01-10T10:15:30Z",
        "user_id": "engineer@company.com",
        "action": "parameter_change",
        "resource": "LOOP_001",
        "details": {
          "parameter": "kc",
          "old_value": 1.2,
          "new_value": 1.5
        },
        "ip_address": "192.168.1.100"
      }
    ],
    "total_count": 1,
    "page": 1,
    "page_size": 50
  }
}
```

---

## Performance Monitoring API

### 1. Real-time Metrics

#### `GET /api/v1/monitoring/loops/{loop_id}/metrics`
**Get real-time performance metrics**

**Response:**
```json
{
  "instance_name": "PERFORMANCE_METRICS_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "performance_metrics",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized performance metrics configuration",
    "tags": [
      "control",
      "api",
      "performance"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    }
  },
  "variable_counts": {
    "total_variables": 13,
    "process_variables_count": 0,
    "disturbance_variables_count": 1,
    "control_variables_count": 2,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 1,
    "configuration_items_count": 9
  },
  "data": {
    "loop_id": "LOOP_001",
    "timestamp": "2025-01-10T10:20:00Z",
    "performance_metrics": {
      "mae": 2.1,
      "iae": 15.3,
      "ise": 45.7,
      "itae": 89.2,
      "oscillation_index": 0.12,
      "cv_saturation_percentage": 5.2
    },
    "control_quality": {
      "stability_margin": 0.8,
      "disturbance_rejection": 0.85,
      "setpoint_tracking": 0.92
    }
  }
}
```

### 2. Historical Analytics

#### `GET /api/v1/analytics/performance/trends`
**Get performance trend analysis**

**Query Parameters:**
- `loop_ids`: Comma-separated list of loop IDs
- `time_range`: Time range (1h, 24h, 7d, 30d)
- `metrics`: Comma-separated metrics to include

---

## Training & Validation API

### 1. Simulation & Testing

#### `POST /api/v1/testing/simulation`
**Run PID controller simulation**

```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api",
      "training"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 15,
    "process_variables_count": 1,
    "disturbance_variables_count": 1,
    "control_variables_count": 1,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 12
  },
  "data": {
    "simulation_id": "SIM_001",
    "process_model": {
      "type": "fopdt",
      "gain": 1.5,
      "time_constant": 25.0,
      "dead_time": 8.0
    },
    "controller_parameters": {
      "kc": 1.2,
      "ti": 15.0,
      "td": 3.0
    },
    "simulation_time": 600,
    "disturbances": [
      {
        "time": 300,
        "type": "step",
        "magnitude": 10.0
      }
    ]
  }
}
```

### 2. Validation Framework

#### `POST /api/v1/validation/controller`
**Validate controller against industry standards**

```json
{
  "instance_name": "VALIDATION_FRAMEWORK_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "validation_framework",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized validation framework configuration",
    "tags": [
      "control",
      "api",
      "validation"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    }
  },
  "variable_counts": {
    "total_variables": 3,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 2,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 1
  },
  "data": {
    "loop_id": "LOOP_001",
    "validation_standards": [
      "isa_95",
      "iec_61131_3"
    ],
    "test_scenarios": [
      "setpoint_tracking",
      "disturbance_rejection",
      "noise_immunity"
    ]
  }
}
```

---

## Integration Examples

### 1. Complete PID Loop Setup

```python
import requests

# Step 1: Authenticate
auth_response = requests.post('/api/v1/auth/login', json={
    'username': 'engineer@company.com',
    'password': 'secure_password',
    'authentication_method': 'ldap'
})
token = auth_response.json()['access_token']

headers = {'Authorization': f'Bearer {token}'}

# Step 2: Create PID loop with complete scaling configuration
loop_config = {
    'loop_id': 'REACTOR_TEMP_001',
    'process_type': 'temperature',
    'algorithm_form': 'dependent',
    'instruction_type': 'PIDE',
    'control_mode': 'PID',
    'pv01_scaling': {
        'tagname': 'TIT_R101_MAIN',
        'raw_min': 0,
        'raw_max': 4095,
        'eng_min': 0.0,
        'eng_max': 250.0,
        'units': '°C'
    },
    'pv02_scaling': {
        'tagname': 'TIT_R101_BACKUP',
        'raw_min': 0,
        'raw_max': 4095,
        'eng_min': 0.0,
        'eng_max': 250.0,
        'units': '°C'
    },
    'dv01_scaling': {
        'tagname': 'PIT_R101_JACKET',
        'raw_min': 0,
        'raw_max': 4095,
        'eng_min': 0.0,
        'eng_max': 100.0,
        'units': 'psi'
    },
    'dv02_scaling': {
        'tagname': 'FIT_COOLING_WATER',
        'raw_min': 0,
        'raw_max': 4095,
        'eng_min': 0.0,
        'eng_max': 500.0,
        'units': 'GPM'
    },
    'cv_limits': {
        'tagname': 'VLV_COOLING.Position',
        'min': 0.0,
        'max': 100.0,
        'units': '%'
    }
}

loop_response = requests.post('/api/v1/pid/loops', 
                            json=loop_config, headers=headers)

# Step 3: Execute auto-tuning
tuning_config = {
    'tuning_method': 'cohen_coon',
    'test_type': 'step_test',
    'test_parameters': {'step_size': 5.0, 'duration': 300}
}

tune_response = requests.put(f'/api/v1/pid/loops/REACTOR_TEMP_001/tune',
                           json=tuning_config, headers=headers)

# Step 4: Monitor performance
metrics = requests.get('/api/v1/monitoring/loops/REACTOR_TEMP_001/metrics',
                      headers=headers)
print(f"Current MAE: {metrics.json()['performance_metrics']['mae']}")
```

### 2. Enterprise Deployment Pattern

```python
# Multi-loop cascade configuration with enterprise security
cascade_config = {
    'strategy_id': 'CASCADE_REACTOR_001',
    'primary_loop': {
        'loop_id': 'TEMP_PRIMARY',
        'process_type': 'temperature',
        'control_mode': 'PI'
    },
    'secondary_loop': {
        'loop_id': 'FLOW_SECONDARY', 
        'process_type': 'flow',
        'control_mode': 'P'
    },
    'cascade_ratio': 0.8,
    'security_validation': True
}

# Deploy with audit logging
deployment = requests.post('/api/v1/pid/cascade/deploy',
                         json=cascade_config, headers=headers)
```

---

## Authentication & Security

### JWT Token Structure
```json
{
  "instance_name": "PID_CONTROL_LOOP_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "phase8_pid_control",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized phase8 pid control configuration",
    "tags": [
      "control",
      "api",
      "performance"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    },
    "process_information": {
      "process_type": "mixed",
      "industry_sector": "general_manufacturing",
      "safety_level": "SIL1",
      "environmental_conditions": {
        "temperature_range": {
          "value": 25,
          "units": "\u00b0C"
        },
        "humidity_range": "40-60%",
        "vibration_level": "low",
        "hazardous_area": false
      }
    }
  },
  "variable_counts": {
    "total_variables": 9,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 9
  },
  "data": {
    "header": {
      "alg": "RS256",
      "typ": "JWT"
    },
    "payload": {
      "sub": "engineer@company.com",
      "roles": [
        "pid_engineer",
        "system_operator"
      ],
      "permissions": [
        "tune_loops",
        "view_performance"
      ],
      "exp": 1641811200,
      "iat": 1641807600
    }
  }
}
```

### Required Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-API-Version: v1
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "instance_name": "API_CONFIG_001",
  "schema_version": "1.0.0",
  "metadata": {
    "created_timestamp": "2025-07-09T13:45:59Z",
    "updated_timestamp": "2025-07-09T13:45:59Z",
    "schema_type": "api_configuration",
    "created_by": "documentation_standardization_orchestrator",
    "description": "Standardized api configuration configuration",
    "tags": [
      "control",
      "api"
    ],
    "validation_status": {
      "validated": true,
      "validation_timestamp": "2025-07-09T13:45:59Z",
      "validation_score": 1.0,
      "issues": []
    }
  },
  "variable_counts": {
    "total_variables": 9,
    "process_variables_count": 0,
    "disturbance_variables_count": 0,
    "control_variables_count": 0,
    "validation_checks_count": 0,
    "endpoints_count": 0,
    "metrics_count": 0,
    "configuration_items_count": 9
  },
  "data": {
    "error": {
      "code": "INVALID_PARAMETERS",
      "message": "PID parameters outside acceptable range",
      "details": {
        "field": "kc",
        "value": 150.0,
        "max_allowed": 100.0
      },
      "request_id": "req_12345",
      "timestamp": "2025-01-10T10:30:00Z"
    }
  }
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED`: 401 - Valid token required
- `INSUFFICIENT_PERMISSIONS`: 403 - User lacks required permissions
- `LOOP_NOT_FOUND`: 404 - Specified loop ID does not exist
- `INVALID_PARAMETERS`: 400 - Request parameters invalid or out of range
- `TUNING_IN_PROGRESS`: 409 - Loop currently being tuned
- `SAFETY_VIOLATION`: 422 - Operation would violate safety constraints
- `RATE_LIMIT_EXCEEDED`: 429 - Too many requests

---

## Rate Limiting

### Default Limits
- **Standard Users**: 100 requests/minute
- **Enterprise Users**: 1000 requests/minute  
- **System APIs**: 10000 requests/minute

### Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641811200
```

---

## SDK & Client Libraries

### Python SDK
```python
from plc_gpt_pid import PIDClient

client = PIDClient(
    base_url='https://api.plc-gbt.com',
    auth_method='jwt',
    token='your_jwt_token'
)

# Create and tune loop
loop = client.loops.create('REACTOR_001', process_type='temperature')
tuning_result = loop.auto_tune(method='ziegler_nichols')
performance = loop.get_performance_metrics()
```

### JavaScript SDK
```javascript
import { PIDClient } from '@plc-gbt/pid-sdk';

const client = new PIDClient({
  baseURL: 'https://api.plc-gbt.com',
  authToken: 'your_jwt_token'
});

// Monitor multiple loops
const loops = await client.loops.getAll();
const metrics = await Promise.all(
  loops.map(loop => loop.getMetrics())
);
```

---

## Support & Resources

### Technical Support
- **Email**: api-support@plc-gbt.com
- **Documentation**: https://docs.plc-gbt.com/phase8
- **GitHub Issues**: https://github.com/plc-gbt/pid-integration/issues

### Additional Resources
- [Phase 8 Integration Guide](PHASE8_INTEGRATION_GUIDE.md)
- [Training Materials](PHASE8_TRAINING_MODULE_1_BASICS.md)
- [Best Practices](PHASE8_BEST_PRACTICES_MANUFACTURING.md)
- [Troubleshooting Guide](PHASE8_TROUBLESHOOTING_GUIDE.md)

---

*This documentation follows AI Task Orchestrator Guide methodology for comprehensive technical documentation.*  
*Last Updated: January 10, 2025*  
*Version: 1.0.0* 