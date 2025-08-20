/**
 * PLC Output Documentation Page - AI Task Orchestrator TypeScript Implementation
 *
 * @description Comprehensive documentation for PLC Output node
 * @compliance Strict TypeScript - zero any types policy
 * @features Interactive examples, parameter guidance, troubleshooting
 * @generated Automatically generated from documentation-generator.ts
 */

'use client';

import React from 'react';

import { NodeDocumentationTemplate, type NodeDocumentationData } from '@/components/docs/NodeDocumentationTemplate';

const PLC_OUTPUT_DATA: NodeDocumentationData = {
  "nodeType": "plc-output",
  "title": "PLC Output",
  "description": "Programmable Logic Controller output for controlling actuators and devices",
  "overview": "The PLC Output node is part of the PLC Integration category and provides programmable logic controller output for controlling actuators and devices. \n\nThis node is classified as moderate complexity and is primarily used for real-time data exchange with industrial plcs. It integrates seamlessly with other nodes in the Control & Optimization, Data Integration categories to provide comprehensive industrial automation solutions.\n\nKey capabilities include advanced configuration options, real-time monitoring, robust error handling, and extensive integration possibilities with other system components.",
  "features": [
    "Digital and analog output control",
    "Multiple data type support (BOOLEAN, SINT, INT, DINT, REAL)",
    "Real-time control signal output to PLCs",
    "Output value validation and limiting",
    "Connection testing and verification",
    "Safety interlocks and emergency stops",
    "Output scaling and engineering units"
  ],
  "useCases": [
    "Controlling valve positions in process systems",
    "Setting pump speed via variable frequency drives",
    "Digital control of solenoid valves",
    "Analog control of heating elements",
    "Motor start/stop control",
    "Process setpoint adjustment"
  ],
  "parameters": [
    {
      "name": "label",
      "type": "string",
      "defaultValue": "PLC Output 1",
      "description": "Human-readable name for this node instance",
      "required": true
    },
    {
      "name": "outputType",
      "type": "select",
      "defaultValue": "Digital",
      "range": "Digital, Analog",
      "description": "Type of output signal being sent",
      "required": true
    },
    {
      "name": "dataType",
      "type": "select",
      "defaultValue": "BOOLEAN",
      "range": "BOOLEAN, SINT, INT, DINT, REAL",
      "description": "PLC data type for the output signal",
      "required": true
    },
    {
      "name": "plcAddress",
      "type": "select",
      "defaultValue": "",
      "description": "PLC address constructed from selected connection",
      "required": true
    },
    {
      "name": "safetyValue",
      "type": "number",
      "defaultValue": "0",
      "description": "Safe value to output on communication failure",
      "required": true
    }
  ],
  "examples": [
    {
      "title": "Digital Output - Valve Control",
      "description": "Control a solenoid valve open/close state",
      "language": "json",
      "code": "{\n  \"nodeType\": \"plc-output\",\n  \"config\": {\n    \"label\": \"Inlet Valve V-101\",\n    \"outputType\": \"Digital\",\n    \"dataType\": \"BOOLEAN\",\n    \"plcAddress\": \"Q0.0\",\n    \"safetyValue\": false,\n    \"enabled\": true\n  }\n}"
    }
  ],
  "troubleshooting": [
    {
      "issue": "Output Not Responding",
      "symptoms": "PLC output does not change when node value changes",
      "cause": "Incorrect PLC address or communication failure",
      "solution": "Verify PLC address is correct and PLC is in RUN mode.",
      "severity": "high"
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
      "Verify PLC address formats match your PLC system",
      "Test communication thoroughly before production",
      "Implement proper safety values for communication failures"
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
      "Optimize PLC communication by grouping related tags",
      "Use appropriate scan rates to balance performance and network load",
      "Monitor PLC CPU utilization and communication statistics"
    ]
  },
  "relatedNodes": [
    "plc-input",
    "pid-controller",
    "alarm-handler"
  ],
  "externalLinks": []
};

export default function PlcOutputDocumentation(): React.JSX.Element {
  return <NodeDocumentationTemplate data={PLC_OUTPUT_DATA} />;
}