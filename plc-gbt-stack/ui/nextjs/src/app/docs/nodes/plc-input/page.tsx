/**
 * PLC Input Documentation Page - AI Task Orchestrator TypeScript Implementation
 *
 * @description Comprehensive documentation for PLC Input node
 * @compliance Strict TypeScript - zero any types policy
 * @features Interactive examples, parameter guidance, troubleshooting
 * @generated Automatically generated from documentation-generator.ts
 */

'use client';

import React from 'react';

import { NodeDocumentationTemplate, type NodeDocumentationData } from '@/components/docs/NodeDocumentationTemplate';

const PLC_INPUT_DATA: NodeDocumentationData = {
  "nodeType": "plc-input",
  "title": "PLC Input",
  "description": "Programmable Logic Controller input for reading sensor data and digital/analog signals",
  "overview": "The PLC Input node is part of the PLC Integration category and provides programmable logic controller input for reading sensor data and digital/analog signals. \n\nThis node is classified as moderate complexity and is primarily used for real-time data exchange with industrial plcs. It integrates seamlessly with other nodes in the Control & Optimization, Data Integration categories to provide comprehensive industrial automation solutions.\n\nKey capabilities include advanced configuration options, real-time monitoring, robust error handling, and extensive integration possibilities with other system components.",
  "features": [
    "Digital and analog input support",
    "Multiple data type handling (BOOLEAN, SINT, INT, DINT, REAL, STRING, UDT)",
    "Array data type support for bulk operations",
    "Real-time data acquisition from PLCs",
    "Connection testing and validation",
    "Multiple output handles for analog scaling",
    "Engineering units conversion",
    "Signal conditioning and filtering"
  ],
  "useCases": [
    "Reading temperature sensors from process equipment",
    "Monitoring pressure transmitters in pipelines",
    "Collecting flow meter data for batch processes",
    "Digital status monitoring of pumps and valves",
    "Multi-point temperature monitoring in distillation columns",
    "Vibration monitoring for predictive maintenance"
  ],
  "parameters": [
    {
      "name": "label",
      "type": "string",
      "defaultValue": "PLC Input 1",
      "description": "Human-readable name for this node instance",
      "required": true
    },
    {
      "name": "inputType",
      "type": "select",
      "defaultValue": "Digital",
      "range": "Digital, Analog",
      "description": "Type of input signal being read",
      "required": true
    },
    {
      "name": "dataType",
      "type": "select",
      "defaultValue": "BOOLEAN",
      "range": "BOOLEAN, SINT, INT, DINT, REAL, STRING, UDT, Arrays",
      "description": "PLC data type for the input signal",
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
      "name": "scanRate",
      "type": "number",
      "defaultValue": "1000",
      "range": "100-10000",
      "description": "Data acquisition rate in milliseconds",
      "required": false
    },
    {
      "name": "units",
      "type": "select",
      "defaultValue": "None",
      "description": "Engineering units for the input value",
      "required": false
    },
    {
      "name": "enabled",
      "type": "boolean",
      "defaultValue": "true",
      "description": "Enable or disable this input node",
      "required": false
    }
  ],
  "examples": [
    {
      "title": "Digital Input - Pump Status",
      "description": "Monitor a pump running status from PLC digital output",
      "language": "json",
      "code": "{\n  \"nodeType\": \"plc-input\",\n  \"config\": {\n    \"label\": \"Pump P-101 Status\",\n    \"inputType\": \"Digital\",\n    \"dataType\": \"BOOLEAN\",\n    \"plcAddress\": \"DB1.DBX0.0\",\n    \"scanRate\": 500,\n    \"enabled\": true\n  }\n}"
    },
    {
      "title": "Analog Input - Temperature Sensor",
      "description": "Read temperature from a 4-20mA transmitter",
      "language": "json",
      "code": "{\n  \"nodeType\": \"plc-input\",\n  \"config\": {\n    \"label\": \"Reactor Temperature\",\n    \"inputType\": \"Analog\",\n    \"dataType\": \"REAL\",\n    \"plcAddress\": \"IW100\",\n    \"scanRate\": 1000,\n    \"units\": \"°C\",\n    \"scaling\": {\n      \"inputMin\": 0,\n      \"inputMax\": 27648,\n      \"outputMin\": 0,\n      \"outputMax\": 500\n    },\n    \"enabled\": true\n  }\n}"
    }
  ],
  "troubleshooting": [
    {
      "issue": "Connection Timeout",
      "symptoms": "Node shows red status, no data updates",
      "cause": "PLC connection lost or network issues",
      "solution": "Check PLC connection settings and network connectivity. Verify PLC is responding to ping.",
      "severity": "high"
    },
    {
      "issue": "Invalid Data Type",
      "symptoms": "Data appears corrupted or unexpected values",
      "cause": "Mismatch between configured data type and actual PLC data type",
      "solution": "Verify the PLC address data type matches the configured data type in the node properties.",
      "severity": "medium"
    },
    {
      "issue": "Slow Data Updates",
      "symptoms": "Data updates slower than expected",
      "cause": "Scan rate too high or PLC communication overloaded",
      "solution": "Increase scan rate interval or optimize PLC communication load.",
      "severity": "low"
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
    "plc-output",
    "data-logger",
    "alarm-handler"
  ],
  "externalLinks": [
    {
      "title": "Siemens S7 Communication Protocol",
      "url": "https://support.industry.siemens.com/cs/document/26483647",
      "description": "Official documentation for S7 PLC communication"
    },
    {
      "title": "Allen-Bradley EtherNet/IP Guide",
      "url": "https://literature.rockwellautomation.com/idc/groups/literature/documents/um/enet-um001_-en-p.pdf",
      "description": "EtherNet/IP communication implementation guide"
    }
  ]
};

export default function PlcInputDocumentation(): React.JSX.Element {
  return <NodeDocumentationTemplate data={PLC_INPUT_DATA} />;
}