/**
 * Opc Client Documentation Page - AI Task Orchestrator TypeScript Implementation
 *
 * @description Comprehensive documentation for Opc Client node
 * @compliance Strict TypeScript - zero any types policy
 * @features Interactive examples, parameter guidance, troubleshooting
 * @generated Automatically generated from documentation-generator.ts
 */

'use client';

import React from 'react';

import { NodeDocumentationTemplate, type NodeDocumentationData } from '@/components/docs/NodeDocumentationTemplate';

const OPC_CLIENT_DATA: NodeDocumentationData = {
  "nodeType": "opc-client",
  "title": "Opc Client",
  "description": "Opc Client node for industrial automation applications",
  "overview": "The Opc Client node is part of the PLC Integration category and provides opc client node for industrial automation applications. \n\nThis node is classified as moderate complexity and is primarily used for real-time data exchange with industrial plcs. It integrates seamlessly with other nodes in the Control & Optimization, Data Integration categories to provide comprehensive industrial automation solutions.\n\nKey capabilities include advanced configuration options, real-time monitoring, robust error handling, and extensive integration possibilities with other system components.",
  "features": [
    "Industrial-grade reliability",
    "Real-time processing capabilities",
    "Configurable parameters",
    "Integration with other nodes"
  ],
  "useCases": [
    "Opc Client implementation in industrial processes",
    "Process automation and control",
    "System integration scenarios"
  ],
  "parameters": [
    {
      "name": "label",
      "type": "string",
      "defaultValue": "Opc Client 1",
      "description": "Human-readable name for this node instance",
      "required": true
    },
    {
      "name": "enabled",
      "type": "boolean",
      "defaultValue": "true",
      "description": "Enable or disable this node",
      "required": false
    }
  ],
  "examples": [
    {
      "title": "Basic Opc Client Configuration",
      "description": "Simple configuration example for Opc Client node",
      "language": "json",
      "code": "{\n  \"nodeType\": \"opc-client\",\n  \"config\": {\n    \"label\": \"Opc Client Example\",\n    \"enabled\": true\n  }\n}"
    }
  ],
  "troubleshooting": [
    {
      "issue": "Node Not Responding",
      "symptoms": "Node appears inactive or not processing data",
      "cause": "Configuration error or connection issue",
      "solution": "Check node configuration and verify all required parameters are set",
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
  "relatedNodes": [],
  "externalLinks": []
};

export default function OpcClientDocumentation(): React.JSX.Element {
  return <NodeDocumentationTemplate data={OPC_CLIENT_DATA} />;
}