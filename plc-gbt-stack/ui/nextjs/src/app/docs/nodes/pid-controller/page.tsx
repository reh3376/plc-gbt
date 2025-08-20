/**
 * PID Controller Documentation Page - AI Task Orchestrator TypeScript Implementation
 *
 * @description Comprehensive documentation for PID Controller node
 * @compliance Strict TypeScript - zero any types policy
 * @features Interactive examples, parameter guidance, troubleshooting
 * @generated Automatically generated from documentation-generator.ts
 */

'use client';

import React from 'react';

import { NodeDocumentationTemplate, type NodeDocumentationData } from '@/components/docs/NodeDocumentationTemplate';

const PID_CONTROLLER_DATA: NodeDocumentationData = {
  "nodeType": "pid-controller",
  "title": "PID Controller",
  "description": "Proportional-Integral-Derivative controller for process control applications",
  "overview": "The PID Controller node is part of the Control & Optimization category and provides proportional-integral-derivative controller for process control applications. \n\nThis node is classified as complex complexity and is primarily used for process control and optimization in industrial systems. It integrates seamlessly with other nodes in the PLC Integration, Machine Learning categories to provide comprehensive industrial automation solutions.\n\nKey capabilities include advanced configuration options, real-time monitoring, robust error handling, and extensive integration possibilities with other system components.",
  "features": [
    "Classic PID control algorithm implementation",
    "Auto-tuning capabilities with multiple methods",
    "Setpoint tracking and disturbance rejection",
    "Anti-windup protection for integral term",
    "Derivative filtering for noise reduction",
    "Manual/Auto mode switching",
    "Cascade control support",
    "Feedforward integration"
  ],
  "useCases": [
    "Temperature control in chemical reactors",
    "Flow control in pipeline systems",
    "Pressure control in vessels and tanks",
    "Level control in storage tanks",
    "pH control in water treatment",
    "Speed control of rotating equipment"
  ],
  "parameters": [
    {
      "name": "label",
      "type": "string",
      "defaultValue": "PID Controller 1",
      "description": "Human-readable name for this controller instance",
      "required": true
    },
    {
      "name": "kp",
      "type": "number",
      "defaultValue": "1.0",
      "range": "0.001-1000",
      "description": "Proportional gain coefficient",
      "required": true
    },
    {
      "name": "ki",
      "type": "number",
      "defaultValue": "0.1",
      "range": "0-100",
      "description": "Integral gain coefficient",
      "required": true
    },
    {
      "name": "kd",
      "type": "number",
      "defaultValue": "0.01",
      "range": "0-10",
      "description": "Derivative gain coefficient",
      "required": true
    },
    {
      "name": "setpoint",
      "type": "number",
      "defaultValue": "0",
      "description": "Target value for the controlled variable",
      "required": true
    },
    {
      "name": "outputMin",
      "type": "number",
      "defaultValue": "0",
      "description": "Minimum controller output value",
      "required": true
    },
    {
      "name": "outputMax",
      "type": "number",
      "defaultValue": "100",
      "description": "Maximum controller output value",
      "required": true
    }
  ],
  "examples": [
    {
      "title": "Temperature Control Loop",
      "description": "PID controller for reactor temperature control",
      "language": "json",
      "code": "{\n  \"nodeType\": \"pid-controller\",\n  \"config\": {\n    \"label\": \"Reactor Temperature Control\",\n    \"kp\": 2.5,\n    \"ki\": 0.8,\n    \"kd\": 0.15,\n    \"setpoint\": 85.0,\n    \"outputMin\": 0,\n    \"outputMax\": 100,\n    \"units\": \"°C\",\n    \"mode\": \"auto\",\n    \"enabled\": true\n  }\n}"
    }
  ],
  "troubleshooting": [
    {
      "issue": "Oscillating Control",
      "symptoms": "Process variable oscillates around setpoint",
      "cause": "Aggressive tuning parameters, typically high Kp or Kd",
      "solution": "Reduce proportional gain (Kp) and derivative gain (Kd). Consider using auto-tuning.",
      "severity": "medium"
    },
    {
      "issue": "Slow Response",
      "symptoms": "Controller takes too long to reach setpoint",
      "cause": "Conservative tuning parameters or integral windup",
      "solution": "Increase proportional gain (Kp) and integral gain (Ki). Check for output saturation.",
      "severity": "medium"
    }
  ],
  "bestPractices": {
    "dos": [
      "Always provide meaningful labels for node instances",
      "Test configuration in development environment first",
      "Monitor node performance in production",
      "Document configuration choices for maintenance",
      "Use appropriate data types for your application",
      "Implement proper error handling and recovery",
      "Tune control parameters systematically using proven methods",
      "Implement safety limits and interlocks",
      "Monitor control loop performance continuously"
    ],
    "donts": [
      "Don't use default values in production without review",
      "Don't ignore validation warnings or errors",
      "Don't exceed recommended parameter ranges",
      "Don't skip connection testing before deployment"
    ],
    "performanceTips": [
      "Optimize scan rates and polling intervals for your use case",
      "Monitor resource usage and network bandwidth",
      "Use connection pooling when available",
      "Implement appropriate caching strategies",
      "Use appropriate control loop timing (typically 4-10x process time constant)",
      "Implement anti-windup protection for integral terms",
      "Consider feedforward control for measurable disturbances"
    ]
  },
  "relatedNodes": [
    "plc-input",
    "plc-output",
    "feedforward-controller"
  ],
  "externalLinks": [
    {
      "title": "PID Control Theory and Practice",
      "url": "https://www.ni.com/en-us/innovations/white-papers/06/pid-theory-explained.html",
      "description": "Comprehensive guide to PID control theory and implementation"
    }
  ]
};

export default function PidControllerDocumentation(): React.JSX.Element {
  return <NodeDocumentationTemplate data={PID_CONTROLLER_DATA} />;
}