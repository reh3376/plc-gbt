"""
PLC-GBT MCP (Model Context Protocol) Server
Following AI Task Orchestrator Guide Methodology

Provides structured interface between OpenAI fine-tuned LLM and PLC-GBT system.
Implements MCP protocol for tool discovery, execution, and resource management.

Author: AI Task Orchestrator
Created: 2025-07-21
Phase: 27.2 - MCP Server Implementation
Dependencies: Phase 23 (Fine-tuned LLM), Phase 21 (CLI), RESTful API
"""

import asyncio
import json
import logging
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

# MCP Protocol imports
from mcp import types
from mcp.server import Server
from mcp.types import (
    CallToolResult,
    GetPromptResult,
    ListPromptsResult,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# MCP SERVER CONFIGURATION AND CONSTANTS
# =============================================================================

SERVER_NAME = "plc-gbt-mcp-server"
SERVER_VERSION = "1.0.0"
API_BASE_URL = "http://localhost:8000/api/v1"
MAX_CONCURRENT_REQUESTS = 10
REQUEST_TIMEOUT = 30

class MCPCapability(str, Enum):
    """MCP server capabilities"""
    TOOLS = "tools"
    PROMPTS = "prompts"
    RESOURCES = "resources"

class OperationCategory(str, Enum):
    """Categories of operations for organization"""
    CONTROL_LOOPS = "control-loops"
    WORKFLOWS = "workflows"
    MEMORY = "memory"
    PLC = "plc"
    PLUGINS = "plugins"
    AUTOMATION = "automation"
    SYSTEM = "system"

# =============================================================================
# DATA MODELS FOR MCP OPERATIONS
# =============================================================================

@dataclass
class MCPToolDefinition:
    """Definition of an MCP tool"""
    name: str
    description: str
    category: OperationCategory
    endpoint: str
    method: str
    parameters: Dict[str, Any]
    cli_equivalent: str
    safety_level: str = "safe"  # safe, caution, restricted
    requires_confirmation: bool = False

@dataclass
class MCPPromptDefinition:
    """Definition of an MCP prompt template"""
    name: str
    description: str
    template: str
    parameters: List[str]
    category: OperationCategory
    examples: List[str] = field(default_factory=list)

@dataclass
class MCPResourceDefinition:
    """Definition of an MCP resource"""
    name: str
    description: str
    resource_type: str
    uri: str
    category: OperationCategory
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class APIResponse:
    """Response from REST API calls"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time_ms: Optional[float]
    status_code: int

# =============================================================================
# PLC-GBT MCP SERVER IMPLEMENTATION
# =============================================================================

class PLCGBTMCPServer:
    """Main MCP server implementation for PLC-GBT system"""

    def __init__(self, api_base_url: str = API_BASE_URL):
        self.api_base_url = api_base_url
        self.server = Server(SERVER_NAME)
        self.session: Optional[aiohttp.ClientSession] = None
        self.tools: Dict[str, MCPToolDefinition] = {}
        self.prompts: Dict[str, MCPPromptDefinition] = {}
        self.resources: Dict[str, MCPResourceDefinition] = {}

        # Initialize server capabilities
        self._register_tools()
        self._register_prompts()
        self._register_resources()

        # Register MCP handlers
        self._register_mcp_handlers()

        logger.info(f"Initialized PLC-GBT MCP Server v{SERVER_VERSION}")
        logger.info(f"API Base URL: {self.api_base_url}")
        logger.info(f"Registered {len(self.tools)} tools, {len(self.prompts)} prompts, {len(self.resources)} resources")

    async def start(self, transport_options: Dict[str, Any] = None):
        """Start the MCP server"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
        )

        logger.info("PLC-GBT MCP Server started successfully")
        logger.info(f"Available capabilities: {[cap.value for cap in MCPCapability]}")

        # Test API connectivity
        try:
            await self._test_api_connectivity()
            logger.info("✅ API connectivity verified")
        except Exception as e:
            logger.warning(f"⚠️ API connectivity test failed: {e}")

    async def stop(self):
        """Stop the MCP server"""
        if self.session:
            await self.session.close()
        logger.info("PLC-GBT MCP Server stopped")

    def _register_mcp_handlers(self):
        """Register all MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available tools"""
            tools = []
            for tool_def in self.tools.values():
                tools.append(Tool(
                    name=tool_def.name,
                    description=tool_def.description,
                    inputSchema={
                        "type": "object",
                        "properties": tool_def.parameters,
                        "required": list(tool_def.parameters.keys())
                    }
                ))
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> CallToolResult:
            """Execute a tool"""
            try:
                if name not in self.tools:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Error: Tool '{name}' not found"
                        )],
                        isError=True
                    )

                tool_def = self.tools[name]

                # Execute the tool via API call
                result = await self._execute_tool(tool_def, arguments)

                if result.success:
                    response_text = self._format_success_response(tool_def, result)
                else:
                    response_text = self._format_error_response(tool_def, result)

                return CallToolResult(
                    content=[TextContent(type="text", text=response_text)],
                    isError=not result.success
                )

            except Exception as e:
                error_text = f"Error executing tool '{name}': {str(e)}\n{traceback.format_exc()}"
                logger.error(error_text)
                return CallToolResult(
                    content=[TextContent(type="text", text=error_text)],
                    isError=True
                )

        @self.server.list_prompts()
        async def list_prompts() -> ListPromptsResult:
            """List all available prompts"""
            prompts = []
            for prompt_def in self.prompts.values():
                prompts.append(types.Prompt(
                    name=prompt_def.name,
                    description=prompt_def.description,
                    arguments=[
                        types.PromptArgument(name=param, description=f"Parameter: {param}")
                        for param in prompt_def.parameters
                    ]
                ))
            return ListPromptsResult(prompts=prompts)

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
            """Get a prompt template with filled parameters"""
            if name not in self.prompts:
                raise ValueError(f"Prompt '{name}' not found")

            prompt_def = self.prompts[name]
            filled_template = prompt_def.template

            # Fill in parameters
            for param, value in arguments.items():
                filled_template = filled_template.replace(f"{{{param}}}", str(value))

            return GetPromptResult(
                description=prompt_def.description,
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=filled_template)
                    )
                ]
            )

        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            """List all available resources"""
            resources = []
            for resource_def in self.resources.values():
                resources.append(types.Resource(
                    uri=resource_def.uri,
                    name=resource_def.name,
                    description=resource_def.description,
                    mimeType="application/json"
                ))
            return ListResourcesResult(resources=resources)

        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            """Read a resource"""
            resource_def = None
            for res in self.resources.values():
                if res.uri == uri:
                    resource_def = res
                    break

            if not resource_def:
                raise ValueError(f"Resource with URI '{uri}' not found")

            # Fetch resource content
            content = await self._fetch_resource_content(resource_def)

            return ReadResourceResult(
                contents=[TextContent(
                    type="text",
                    text=json.dumps(content, indent=2)
                )]
            )

    def _register_tools(self):
        """Register all available tools"""

        # Control Loop Schema Tools
        self.tools["list_schemas"] = MCPToolDefinition(
            name="list_schemas",
            description="List all available control loop schemas with filtering options",
            category=OperationCategory.CONTROL_LOOPS,
            endpoint="/schemas",
            method="GET",
            parameters={
                "page": {"type": "integer", "description": "Page number", "default": 1},
                "limit": {"type": "integer", "description": "Items per page", "default": 10},
                "schema_type": {"type": "string", "description": "Filter by schema type"},
                "search": {"type": "string", "description": "Search schema names"}
            },
            cli_equivalent="plc-cl schema list"
        )

        self.tools["create_schema"] = MCPToolDefinition(
            name="create_schema",
            description="Create a new control loop schema",
            category=OperationCategory.CONTROL_LOOPS,
            endpoint="/schemas",
            method="POST",
            parameters={
                "name": {"type": "string", "description": "Schema name"},
                "type": {"type": "string", "description": "Schema type"},
                "description": {"type": "string", "description": "Schema description"},
                "base_schema": {"type": "string", "description": "Base schema to extend"},
                "custom_fields": {"type": "object", "description": "Custom schema fields"}
            },
            cli_equivalent="plc-cl schema create --name {name} --type {type}",
            safety_level="caution",
            requires_confirmation=True
        )

        self.tools["get_schema"] = MCPToolDefinition(
            name="get_schema",
            description="Get detailed information about a specific schema",
            category=OperationCategory.CONTROL_LOOPS,
            endpoint="/schemas/{schema_id}",
            method="GET",
            parameters={
                "schema_id": {"type": "string", "description": "Schema ID"}
            },
            cli_equivalent="plc-cl schema info {schema_id}"
        )

        # Control Loop Instance Tools
        self.tools["list_instances"] = MCPToolDefinition(
            name="list_instances",
            description="List all control loop instances with filtering options",
            category=OperationCategory.CONTROL_LOOPS,
            endpoint="/instances",
            method="GET",
            parameters={
                "page": {"type": "integer", "description": "Page number", "default": 1},
                "limit": {"type": "integer", "description": "Items per page", "default": 10},
                "schema_id": {"type": "string", "description": "Filter by schema"},
                "status": {"type": "string", "description": "Filter by status"},
                "plc_host": {"type": "string", "description": "Filter by PLC host"}
            },
            cli_equivalent="plc-cl instance list"
        )

        self.tools["create_instance"] = MCPToolDefinition(
            name="create_instance",
            description="Create a new control loop instance",
            category=OperationCategory.CONTROL_LOOPS,
            endpoint="/instances",
            method="POST",
            parameters={
                "name": {"type": "string", "description": "Instance name"},
                "schema_id": {"type": "string", "description": "Base schema ID"},
                "configuration": {"type": "object", "description": "Instance configuration"},
                "plc_host": {"type": "string", "description": "PLC IP address"},
                "plc_slot": {"type": "integer", "description": "PLC slot number", "default": 0}
            },
            cli_equivalent="plc-cl instance create --schema {schema_id} --name {name}",
            safety_level="caution",
            requires_confirmation=True
        )

        # Natural Language Workflow Tools
        self.tools["create_workflow"] = MCPToolDefinition(
            name="create_workflow",
            description="Create a workflow from natural language description",
            category=OperationCategory.WORKFLOWS,
            endpoint="/workflows/create",
            method="POST",
            parameters={
                "description": {"type": "string", "description": "Natural language workflow description"},
                "analyze": {"type": "boolean", "description": "Analyze workflow after creation", "default": False},
                "optimize": {"type": "boolean", "description": "Optimize workflow after creation", "default": False},
                "deploy": {"type": "boolean", "description": "Deploy workflow after creation", "default": False},
                "template": {"type": "string", "description": "Base template to use"}
            },
            cli_equivalent="plc-cl workflow create {description}",
            safety_level="caution"
        )

        self.tools["list_workflows"] = MCPToolDefinition(
            name="list_workflows",
            description="List all available workflows",
            category=OperationCategory.WORKFLOWS,
            endpoint="/workflows",
            method="GET",
            parameters={
                "page": {"type": "integer", "description": "Page number", "default": 1},
                "limit": {"type": "integer", "description": "Items per page", "default": 10},
                "workflow_type": {"type": "string", "description": "Filter by workflow type"},
                "status": {"type": "string", "description": "Filter by status"}
            },
            cli_equivalent="plc-cl workflow list"
        )

        self.tools["analyze_workflow"] = MCPToolDefinition(
            name="analyze_workflow",
            description="Analyze workflow performance and generate recommendations",
            category=OperationCategory.WORKFLOWS,
            endpoint="/workflows/{workflow_id}/analyze",
            method="POST",
            parameters={
                "workflow_id": {"type": "string", "description": "Workflow ID"},
                "analysis_type": {"type": "string", "description": "Analysis type", "default": "standard"},
                "include_recommendations": {"type": "boolean", "description": "Include optimization recommendations", "default": True}
            },
            cli_equivalent="plc-cl workflow analyze {workflow_id}"
        )

        self.tools["optimize_workflow"] = MCPToolDefinition(
            name="optimize_workflow",
            description="Optimize workflow based on analysis",
            category=OperationCategory.WORKFLOWS,
            endpoint="/workflows/{workflow_id}/optimize",
            method="POST",
            parameters={
                "workflow_id": {"type": "string", "description": "Workflow ID"},
                "optimization_goals": {"type": "array", "items": {"type": "string"}, "description": "Optimization goals", "default": ["performance"]},
                "apply_automatically": {"type": "boolean", "description": "Apply optimizations automatically", "default": False}
            },
            cli_equivalent="plc-cl workflow optimize {workflow_id}",
            safety_level="caution"
        )

        self.tools["workflow_chat"] = MCPToolDefinition(
            name="workflow_chat",
            description="Interactive workflow management through conversation",
            category=OperationCategory.WORKFLOWS,
            endpoint="/workflows/chat",
            method="POST",
            parameters={
                "message": {"type": "string", "description": "User message"},
                "session_id": {"type": "string", "description": "Conversation session ID"},
                "user_id": {"type": "string", "description": "User identifier", "default": "api_user"},
                "context": {"type": "object", "description": "Additional context"}
            },
            cli_equivalent="plc-cl workflow chat"
        )

        # Memory System Tools
        self.tools["ingest_memory"] = MCPToolDefinition(
            name="ingest_memory",
            description="Ingest codebase files into the multi-database memory system",
            category=OperationCategory.MEMORY,
            endpoint="/memory/ingest",
            method="POST",
            parameters={
                "paths": {"type": "array", "items": {"type": "string"}, "description": "Paths to ingest"},
                "all_project": {"type": "boolean", "description": "Ingest entire project", "default": False},
                "analysis_depth": {"type": "string", "description": "Analysis depth", "default": "structural"},
                "method": {"type": "string", "description": "Ingestion method", "default": "intelligent"},
                "dry_run": {"type": "boolean", "description": "Preview without execution", "default": False}
            },
            cli_equivalent="plc-memory ingest {paths}",
            safety_level="caution"
        )

        self.tools["query_memory"] = MCPToolDefinition(
            name="query_memory",
            description="Query the memory system with intelligent routing",
            category=OperationCategory.MEMORY,
            endpoint="/memory/query",
            method="POST",
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "query_type": {"type": "string", "description": "Query type", "default": "code_function"},
                "strategy": {"type": "string", "description": "Query strategy", "default": "balanced"},
                "limit": {"type": "integer", "description": "Maximum results", "default": 10}
            },
            cli_equivalent="plc-memory query {query}"
        )

        self.tools["memory_status"] = MCPToolDefinition(
            name="memory_status",
            description="Get memory system status and performance metrics",
            category=OperationCategory.MEMORY,
            endpoint="/memory/status",
            method="GET",
            parameters={
                "detailed": {"type": "boolean", "description": "Include detailed metrics", "default": False},
                "database": {"type": "string", "description": "Specific database status"}
            },
            cli_equivalent="plc-memory status"
        )

        # PLC Integration Tools
        self.tools["connect_plc"] = MCPToolDefinition(
            name="connect_plc",
            description="Establish connection to ControlLogix PLC",
            category=OperationCategory.PLC,
            endpoint="/plc/connect",
            method="POST",
            parameters={
                "host": {"type": "string", "description": "PLC IP address"},
                "slot": {"type": "integer", "description": "PLC slot number", "default": 0},
                "timeout": {"type": "integer", "description": "Connection timeout in seconds", "default": 5},
                "read_only": {"type": "boolean", "description": "Read-only connection mode", "default": True}
            },
            cli_equivalent="plc-cl instance plc connect --host {host} --slot {slot}",
            safety_level="caution"
        )

        self.tools["read_plc_tags"] = MCPToolDefinition(
            name="read_plc_tags",
            description="Read values from PLC tags",
            category=OperationCategory.PLC,
            endpoint="/plc/read",
            method="POST",
            parameters={
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tag names to read"},
                "connection_id": {"type": "string", "description": "Existing connection ID"}
            },
            cli_equivalent="plc-cl instance plc read {tags}"
        )

        self.tools["discover_plcs"] = MCPToolDefinition(
            name="discover_plcs",
            description="Discover ControlLogix PLCs on the network",
            category=OperationCategory.PLC,
            endpoint="/plc/discover",
            method="GET",
            parameters={
                "network": {"type": "string", "description": "Network range to scan"},
                "timeout": {"type": "integer", "description": "Discovery timeout", "default": 5}
            },
            cli_equivalent="plc-cl instance plc discover"
        )

        # System and Monitoring Tools
        self.tools["system_status"] = MCPToolDefinition(
            name="system_status",
            description="Get overall system status and health",
            category=OperationCategory.SYSTEM,
            endpoint="/system/status",
            method="GET",
            parameters={},
            cli_equivalent="plc-cl status"
        )

        self.tools["system_config"] = MCPToolDefinition(
            name="system_config",
            description="Get system configuration settings",
            category=OperationCategory.SYSTEM,
            endpoint="/system/config",
            method="GET",
            parameters={},
            cli_equivalent="plc-cl config show"
        )

        self.tools["system_metrics"] = MCPToolDefinition(
            name="system_metrics",
            description="Get system performance metrics",
            category=OperationCategory.SYSTEM,
            endpoint="/system/metrics",
            method="GET",
            parameters={
                "metric_type": {"type": "string", "description": "Specific metric type"},
                "time_range": {"type": "string", "description": "Time range for metrics", "default": "1h"}
            },
            cli_equivalent="plc-cl metrics --type {metric_type} --range {time_range}"
        )

        logger.info(f"Registered {len(self.tools)} MCP tools")

    def _register_prompts(self):
        """Register prompt templates for common operations"""

        self.prompts["create_temperature_control"] = MCPPromptDefinition(
            name="create_temperature_control",
            description="Create a temperature control loop with PID controller",
            template="""Create a temperature control loop for {process_name} with the following specifications:
- Process Variable: {pv_tag}
- Setpoint: {setpoint_value}°C
- Output: {cv_tag}
- PID Parameters: Kp={kp}, Ki={ki}, Kd={kd}
- High Alarm: {high_alarm}°C
- Low Alarm: {low_alarm}°C
- Control action: {control_action}

Please use the create_instance tool with a standard-pid schema.""",
            parameters=["process_name", "pv_tag", "setpoint_value", "cv_tag", "kp", "ki", "kd", "high_alarm", "low_alarm", "control_action"],
            category=OperationCategory.CONTROL_LOOPS,
            examples=[
                "Create temperature control for reactor with TT_101 sensor, 85°C setpoint, and TIC_101 output"
            ]
        )

        self.prompts["create_data_logging_workflow"] = MCPPromptDefinition(
            name="create_data_logging_workflow",
            description="Create a data logging workflow for industrial processes",
            template="""Create a data logging workflow with the following requirements:
- Data sources: {data_sources}
- Logging interval: {interval} seconds
- Storage location: {storage_location}
- Data format: {data_format}
- Retention period: {retention_days} days
- Include alarms: {include_alarms}

Please use the create_workflow tool with appropriate natural language description.""",
            parameters=["data_sources", "interval", "storage_location", "data_format", "retention_days", "include_alarms"],
            category=OperationCategory.WORKFLOWS,
            examples=[
                "Create data logging for temperature and pressure sensors every 30 seconds to historian database"
            ]
        )

        self.prompts["troubleshoot_control_loop"] = MCPPromptDefinition(
            name="troubleshoot_control_loop",
            description="Troubleshoot control loop performance issues",
            template="""Troubleshoot control loop {loop_name} with the following symptoms:
- Issue description: {issue_description}
- Process variable behavior: {pv_behavior}
- Setpoint changes: {sp_changes}
- Output behavior: {cv_behavior}
- Error messages: {error_messages}

Please analyze the loop configuration and provide recommendations for tuning or fixes.""",
            parameters=["loop_name", "issue_description", "pv_behavior", "sp_changes", "cv_behavior", "error_messages"],
            category=OperationCategory.CONTROL_LOOPS,
            examples=[
                "Troubleshoot temperature control loop with oscillating behavior and slow response"
            ]
        )

        logger.info(f"Registered {len(self.prompts)} MCP prompts")

    def _register_resources(self):
        """Register available resources"""

        self.resources["schema_catalog"] = MCPResourceDefinition(
            name="schema_catalog",
            description="Complete catalog of available control loop schemas",
            resource_type="json",
            uri="plc-gbt://schemas/catalog",
            category=OperationCategory.CONTROL_LOOPS,
            metadata={"source": "schema_management_system"}
        )

        self.resources["workflow_templates"] = MCPResourceDefinition(
            name="workflow_templates",
            description="Library of industrial automation workflow templates",
            resource_type="json",
            uri="plc-gbt://workflows/templates",
            category=OperationCategory.WORKFLOWS,
            metadata={"source": "template_library"}
        )

        self.resources["system_documentation"] = MCPResourceDefinition(
            name="system_documentation",
            description="Complete system documentation and API reference",
            resource_type="json",
            uri="plc-gbt://system/documentation",
            category=OperationCategory.SYSTEM,
            metadata={"source": "documentation_system"}
        )

        self.resources["plc_tag_database"] = MCPResourceDefinition(
            name="plc_tag_database",
            description="Database of available PLC tags and their definitions",
            resource_type="json",
            uri="plc-gbt://plc/tags",
            category=OperationCategory.PLC,
            metadata={"source": "plc_integration_system"}
        )

        logger.info(f"Registered {len(self.resources)} MCP resources")

    async def _execute_tool(self, tool_def: MCPToolDefinition, arguments: Dict[str, Any]) -> APIResponse:
        """Execute a tool by calling the corresponding API endpoint"""
        try:
            # Build URL
            url = f"{self.api_base_url}{tool_def.endpoint}"

            # Replace path parameters
            for key, value in arguments.items():
                if f"{{{key}}}" in url:
                    url = url.replace(f"{{{key}}}", str(value))
                    # Remove from arguments so it's not sent in body
                    arguments = {k: v for k, v in arguments.items() if k != key}

            # Make API request
            start_time = datetime.now()

            if tool_def.method == "GET":
                response = await self.session.get(url, params=arguments)
            elif tool_def.method == "POST":
                response = await self.session.post(url, json=arguments)
            elif tool_def.method == "PUT":
                response = await self.session.put(url, json=arguments)
            elif tool_def.method == "DELETE":
                response = await self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {tool_def.method}")

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Parse response
            if response.content_type == "application/json":
                data = await response.json()
            else:
                data = {"response": await response.text()}

            return APIResponse(
                success=response.status < 400,
                data=data,
                error=None if response.status < 400 else f"HTTP {response.status}: {data}",
                execution_time_ms=execution_time,
                status_code=response.status
            )

        except Exception as e:
            logger.error(f"Error executing tool {tool_def.name}: {e}")
            return APIResponse(
                success=False,
                data=None,
                error=str(e),
                execution_time_ms=None,
                status_code=500
            )

    async def _fetch_resource_content(self, resource_def: MCPResourceDefinition) -> Dict[str, Any]:
        """Fetch content for a resource"""
        try:
            # Map resource URIs to API endpoints
            uri_mapping = {
                "plc-gbt://schemas/catalog": "/schemas",
                "plc-gbt://workflows/templates": "/workflows/templates",
                "plc-gbt://system/documentation": "/system/config",
                "plc-gbt://plc/tags": "/plc/connections"
            }

            endpoint = uri_mapping.get(resource_def.uri)
            if not endpoint:
                return {"error": f"Resource URI not mapped: {resource_def.uri}"}

            url = f"{self.api_base_url}{endpoint}"
            response = await self.session.get(url)

            if response.status < 400:
                return await response.json()
            else:
                return {"error": f"Failed to fetch resource: HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Error fetching resource {resource_def.name}: {e}")
            return {"error": str(e)}

    def _format_success_response(self, tool_def: MCPToolDefinition, result: APIResponse) -> str:
        """Format successful tool execution response"""
        response_parts = [
            f"✅ Successfully executed: {tool_def.name}",
            f"📊 Execution time: {result.execution_time_ms:.1f}ms",
            f"🔗 CLI equivalent: {tool_def.cli_equivalent}",
            "",
            "📋 Results:"
        ]

        if result.data:
            # Format the data nicely
            if isinstance(result.data, dict):
                if "message" in result.data:
                    response_parts.append(f"Message: {result.data['message']}")
                if "data" in result.data and result.data["data"]:
                    response_parts.append("Data:")
                    response_parts.append(json.dumps(result.data["data"], indent=2))
            else:
                response_parts.append(json.dumps(result.data, indent=2))

        return "\n".join(response_parts)

    def _format_error_response(self, tool_def: MCPToolDefinition, result: APIResponse) -> str:
        """Format error tool execution response"""
        response_parts = [
            f"❌ Error executing: {tool_def.name}",
            f"🔗 CLI equivalent: {tool_def.cli_equivalent}",
            f"Status code: {result.status_code}",
            "",
            "Error details:"
        ]

        if result.error:
            response_parts.append(result.error)

        if result.data and isinstance(result.data, dict) and "error" in result.data:
            response_parts.append(f"API Error: {result.data['error']}")

        return "\n".join(response_parts)

    async def _test_api_connectivity(self):
        """Test connectivity to the REST API"""
        try:
            url = f"{self.api_base_url}/system/status"
            response = await self.session.get(url)
            if response.status < 400:
                logger.info("API connectivity test successful")
            else:
                logger.warning(f"API connectivity test failed: HTTP {response.status}")
        except Exception as e:
            logger.error(f"API connectivity test error: {e}")
            raise

# =============================================================================
# MCP SERVER UTILITIES AND HELPERS
# =============================================================================

class MCPServerManager:
    """Manager for MCP server lifecycle and operations"""

    def __init__(self, api_base_url: str = API_BASE_URL):
        self.api_base_url = api_base_url
        self.server_instance: Optional[PLCGBTMCPServer] = None
        self.is_running = False

    async def start_server(self, **options) -> PLCGBTMCPServer:
        """Start the MCP server"""
        if self.is_running:
            raise RuntimeError("MCP server is already running")

        self.server_instance = PLCGBTMCPServer(self.api_base_url)
        await self.server_instance.start(options)
        self.is_running = True

        logger.info("MCP Server Manager: Server started successfully")
        return self.server_instance

    async def stop_server(self):
        """Stop the MCP server"""
        if not self.is_running or not self.server_instance:
            return

        await self.server_instance.stop()
        self.server_instance = None
        self.is_running = False

        logger.info("MCP Server Manager: Server stopped")

    def get_server_info(self) -> Dict[str, Any]:
        """Get information about the MCP server"""
        if not self.server_instance:
            return {"status": "stopped", "server": None}

        return {
            "status": "running" if self.is_running else "stopped",
            "server_name": SERVER_NAME,
            "server_version": SERVER_VERSION,
            "api_base_url": self.api_base_url,
            "capabilities": [cap.value for cap in MCPCapability],
            "tools_count": len(self.server_instance.tools),
            "prompts_count": len(self.server_instance.prompts),
            "resources_count": len(self.server_instance.resources)
        }

# =============================================================================
# CLI INTEGRATION FOR TESTING AND DEBUGGING
# =============================================================================

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing PLC-GBT MCP Server")
    print("=" * 50)

    manager = MCPServerManager()

    try:
        # Start server
        server = await manager.start_server()

        # Test server info
        info = manager.get_server_info()
        print(f"✅ Server Info: {json.dumps(info, indent=2)}")

        # Test tool discovery
        print(f"\n📋 Available Tools: {len(server.tools)}")
        for tool_name, tool_def in list(server.tools.items())[:5]:  # Show first 5
            print(f"  • {tool_name}: {tool_def.description}")

        # Test prompt discovery
        print(f"\n💬 Available Prompts: {len(server.prompts)}")
        for prompt_name, prompt_def in server.prompts.items():
            print(f"  • {prompt_name}: {prompt_def.description}")

        # Test resource discovery
        print(f"\n📄 Available Resources: {len(server.resources)}")
        for resource_name, resource_def in server.resources.items():
            print(f"  • {resource_name}: {resource_def.description}")

        print("\n✅ MCP Server test completed successfully!")

    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        traceback.print_exc()

    finally:
        await manager.stop_server()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
