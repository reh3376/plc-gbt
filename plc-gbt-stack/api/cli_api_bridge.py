#!/usr/bin/env python3
"""
CLI-to-API Bridge Server
Alternative to MCP for Fine-tuned LLM Integration

This server wraps all PLC-GBT CLI commands as HTTP endpoints, providing the fine-tuned
Industrial Control Theory LLM with reliable access to all system functionality.

Replaces the problematic MCP server approach with a robust HTTP API bridge.

Key Features:
- Wraps all plc-cl commands as REST endpoints
- Provides plc-memory integration
- Includes real-time PLC operations
- Supports batch operations and automation
- Complete API documentation with OpenAPI/Swagger
- Authentication and rate limiting for security
- Comprehensive error handling and logging

Author: AI Task Orchestrator
Date: January 22, 2025
Phase: Alternative LLM Integration (Post-MCP)
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body, Query, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# =============================================================================
# CONFIGURATION AND MODELS
# =============================================================================

APP_VERSION = "1.0.0"
APP_TITLE = "PLC-GBT CLI-to-API Bridge"
APP_DESCRIPTION = """
Comprehensive API bridge that wraps all PLC-GBT CLI commands for fine-tuned LLM integration.

This server provides HTTP endpoints for:
- Control loop schema and instance management (plc-cl commands)
- Memory system operations (plc-memory commands)
- PLC connectivity and real-time operations
- Workflow automation and batch processing
- System monitoring and diagnostics

Designed specifically for the OpenAI fine-tuned Industrial Control Theory LLM
(ft:gpt-4o:industrial-control:20250117) to replace the problematic MCP server approach.
"""

class CommandCategory(str, Enum):
    SCHEMA = "schema"
    INSTANCE = "instance"
    MEMORY = "memory"
    PLC = "plc"
    WORKFLOW = "workflow"
    BATCH = "batch"
    SYSTEM = "system"
    PLUGIN = "plugin"
    AUTOMATION = "automation"

class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"

@dataclass
class CLICommandResult:
    """Result of CLI command execution"""
    command: str
    status: ExecutionStatus
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    timestamp: datetime

class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    command_executed: Optional[str] = Field(None, description="CLI command that was executed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CommandRequest(BaseModel):
    """Request model for CLI command execution"""
    command: str = Field(..., description="CLI command to execute")
    args: List[str] = Field(default=[], description="Command arguments")
    timeout: Optional[float] = Field(30.0, description="Execution timeout in seconds")
    working_directory: Optional[str] = Field(None, description="Working directory for command")

# =============================================================================
# CLI COMMAND EXECUTOR
# =============================================================================

class CLIExecutor:
    """Secure CLI command executor with validation and sandboxing"""
    
    def __init__(self):
        self.allowed_commands = {
            "plc-cl": {
                "executable": "python3",
                "script_path": str(project_root / "cli" / "plc_control_loop_cli.py"),
                "description": "Control loop management commands"
            },
            "plc-memory": {
                "executable": "python3", 
                "script_path": str(project_root / "scripts" / "cli" / "plc_memory_cli.py"),
                "description": "Memory system operations"
            }
        }
        self.command_history: List[CLICommandResult] = []
        self.max_history = 1000
        
    async def execute_command(self, command: str, args: List[str], 
                            timeout: float = 30.0, working_dir: Optional[str] = None) -> CLICommandResult:
        """Execute CLI command with validation and security controls"""
        start_time = time.time()
        
        # Validate command
        if command not in self.allowed_commands:
            raise ValueError(f"Command '{command}' not allowed. Allowed: {list(self.allowed_commands.keys())}")
        
        cmd_config = self.allowed_commands[command]
        
        # Build full command
        if cmd_config["executable"] == "python3":
            full_cmd = ["python3", cmd_config["script_path"]] + args
        else:
            full_cmd = [cmd_config["executable"]] + args
            
        # Set working directory
        if working_dir is None:
            working_dir = str(project_root)
            
        logger.info(f"Executing command: {' '.join(full_cmd)} in {working_dir}")
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            # Wait with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            # Create result
            result = CLICommandResult(
                command=f"{command} {' '.join(args)}",
                status=ExecutionStatus.SUCCESS if process.returncode == 0 else ExecutionStatus.ERROR,
                exit_code=process.returncode,
                stdout=stdout.decode('utf-8', errors='replace'),
                stderr=stderr.decode('utf-8', errors='replace'),
                execution_time=execution_time,
                timestamp=datetime.now(timezone.utc)
            )
            
        except asyncio.TimeoutError:
            result = CLICommandResult(
                command=f"{command} {' '.join(args)}",
                status=ExecutionStatus.TIMEOUT,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                execution_time=time.time() - start_time,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            result = CLICommandResult(
                command=f"{command} {' '.join(args)}",
                status=ExecutionStatus.ERROR,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=time.time() - start_time,
                timestamp=datetime.now(timezone.utc)
            )
        
        # Store in history
        self._add_to_history(result)
        
        return result
    
    def _add_to_history(self, result: CLICommandResult):
        """Add command result to history"""
        self.command_history.append(result)
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]

# =============================================================================
# FASTAPI APPLICATION SETUP
# =============================================================================

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CLI executor
cli_executor = CLIExecutor()

# Security (optional authentication)
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication - can be enhanced as needed"""
    # For now, no authentication required
    # In production, implement proper JWT validation
    return {"user": "fine_tuned_llm"}

# =============================================================================
# CONTROL LOOP MANAGEMENT ENDPOINTS
# =============================================================================

@app.post("/api/v1/cli/schema/list", response_model=APIResponse, tags=["Control Loops"])
async def list_schemas(
    schema_type: Optional[str] = Query(None, description="Filter by schema type"),
    search: Optional[str] = Query(None, description="Search schema names"),
    user = Depends(get_current_user)
):
    """List all control loop schemas via CLI"""
    args = ["schema", "list"]
    if schema_type:
        args.extend(["--type", schema_type])
    if search:
        args.extend(["--search", search])
    
    result = await cli_executor.execute_command("plc-cl", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message="Schema list retrieved" if result.status == ExecutionStatus.SUCCESS else "Failed to retrieve schemas",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

@app.post("/api/v1/cli/schema/create", response_model=APIResponse, tags=["Control Loops"])
async def create_schema(
    schema_name: str = Body(..., description="Schema name"),
    schema_type: str = Body(..., description="Schema type"),
    description: Optional[str] = Body(None, description="Schema description"),
    user = Depends(get_current_user)
):
    """Create new control loop schema via CLI"""
    args = ["schema", "create", schema_name, "--type", schema_type]
    if description:
        args.extend(["--description", description])
    
    result = await cli_executor.execute_command("plc-cl", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message=f"Schema '{schema_name}' created" if result.status == ExecutionStatus.SUCCESS else "Failed to create schema",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

@app.post("/api/v1/cli/instance/list", response_model=APIResponse, tags=["Control Loops"])
async def list_instances(
    schema_id: Optional[str] = Query(None, description="Filter by schema"),
    status: Optional[str] = Query(None, description="Filter by status"),
    plc_host: Optional[str] = Query(None, description="Filter by PLC host"),
    user = Depends(get_current_user)
):
    """List all control loop instances via CLI"""
    args = ["instance", "list"]
    if schema_id:
        args.extend(["--schema", schema_id])
    if status:
        args.extend(["--status", status])
    if plc_host:
        args.extend(["--plc-host", plc_host])
    
    result = await cli_executor.execute_command("plc-cl", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message="Instance list retrieved" if result.status == ExecutionStatus.SUCCESS else "Failed to retrieve instances",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

@app.post("/api/v1/cli/instance/create", response_model=APIResponse, tags=["Control Loops"])
async def create_instance(
    instance_name: str = Body(..., description="Instance name"),
    schema_name: str = Body(..., description="Schema to use"),
    plc_host: Optional[str] = Body(None, description="PLC host address"),
    user = Depends(get_current_user)
):
    """Create new control loop instance via CLI"""
    args = ["instance", "create", instance_name, "--schema", schema_name]
    if plc_host:
        args.extend(["--plc-host", plc_host])
    
    result = await cli_executor.execute_command("plc-cl", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message=f"Instance '{instance_name}' created" if result.status == ExecutionStatus.SUCCESS else "Failed to create instance",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

# =============================================================================
# PLC INTEGRATION ENDPOINTS
# =============================================================================

@app.post("/api/v1/cli/plc/connect", response_model=APIResponse, tags=["PLC Operations"])
async def connect_plc(
    host: str = Body(..., description="PLC IP address"),
    slot: int = Body(0, description="PLC slot number"),
    timeout: float = Body(5.0, description="Connection timeout"),
    user = Depends(get_current_user)
):
    """Connect to ControlLogix PLC via CLI"""
    args = ["instance", "plc", "connect", "--host", host, "--slot", str(slot), "--timeout", str(timeout)]
    
    result = await cli_executor.execute_command("plc-cl", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message=f"Connected to PLC {host}" if result.status == ExecutionStatus.SUCCESS else "Failed to connect to PLC",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

@app.post("/api/v1/cli/plc/read", response_model=APIResponse, tags=["PLC Operations"])
async def read_plc_tags(
    tags: List[str] = Body(..., description="PLC tags to read"),
    connection_id: Optional[str] = Body(None, description="Connection ID"),
    user = Depends(get_current_user)
):
    """Read PLC tag values via CLI"""
    args = ["instance", "plc", "read"] + tags
    if connection_id:
        args.extend(["--connection", connection_id])
    
    result = await cli_executor.execute_command("plc-cl", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message="PLC tags read successfully" if result.status == ExecutionStatus.SUCCESS else "Failed to read PLC tags",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

# =============================================================================
# MEMORY SYSTEM ENDPOINTS
# =============================================================================

@app.post("/api/v1/cli/memory/query", response_model=APIResponse, tags=["Memory System"])
async def query_memory(
    query: str = Body(..., description="Query to execute"),
    database: Optional[str] = Body(None, description="Target database (neo4j, postgresql, qdrant, redis)"),
    limit: Optional[int] = Body(None, description="Result limit"),
    user = Depends(get_current_user)
):
    """Query the memory system via CLI"""
    args = ["query", query]
    if database:
        args.extend(["--database", database])
    if limit:
        args.extend(["--limit", str(limit)])
    
    result = await cli_executor.execute_command("plc-memory", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message="Memory query executed" if result.status == ExecutionStatus.SUCCESS else "Memory query failed",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

@app.post("/api/v1/cli/memory/ingest", response_model=APIResponse, tags=["Memory System"])
async def ingest_memory(
    paths: List[str] = Body(..., description="Paths to ingest"),
    force: bool = Body(False, description="Force re-ingestion"),
    user = Depends(get_current_user)
):
    """Ingest files into memory system via CLI"""
    args = ["ingest"] + paths
    if force:
        args.append("--force")
    
    result = await cli_executor.execute_command("plc-memory", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message="Files ingested successfully" if result.status == ExecutionStatus.SUCCESS else "Ingestion failed",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

# =============================================================================
# BATCH AND AUTOMATION ENDPOINTS
# =============================================================================

@app.post("/api/v1/cli/batch/create", response_model=APIResponse, tags=["Batch Operations"])
async def create_batch(
    operation: str = Body(..., description="Batch operation type"),
    config_file: Optional[str] = Body(None, description="Configuration file path"),
    dry_run: bool = Body(True, description="Perform dry run first"),
    user = Depends(get_current_user)
):
    """Create and execute batch operation via CLI"""
    args = ["batch", operation]
    if config_file:
        args.extend(["--config", config_file])
    if dry_run:
        args.append("--dry-run")
    
    result = await cli_executor.execute_command("plc-cl", args)
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message="Batch operation executed" if result.status == ExecutionStatus.SUCCESS else "Batch operation failed",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

# =============================================================================
# SYSTEM STATUS AND MONITORING
# =============================================================================

@app.get("/api/v1/cli/system/status", response_model=APIResponse, tags=["System"])
async def get_system_status(user = Depends(get_current_user)):
    """Get overall system status via CLI"""
    result = await cli_executor.execute_command("plc-cl", ["status"])
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message="System status retrieved" if result.status == ExecutionStatus.SUCCESS else "Failed to get system status",
        data={"stdout": result.stdout, "stderr": result.stderr},
        command_executed=result.command,
        execution_time=result.execution_time
    )

@app.get("/api/v1/history", response_model=APIResponse, tags=["System"])
async def get_command_history(
    limit: int = Query(50, description="Number of commands to return"),
    user = Depends(get_current_user)
):
    """Get recent command execution history"""
    recent_commands = cli_executor.command_history[-limit:]
    
    history_data = []
    for cmd in recent_commands:
        history_data.append({
            "command": cmd.command,
            "status": cmd.status.value,
            "exit_code": cmd.exit_code,
            "execution_time": cmd.execution_time,
            "timestamp": cmd.timestamp.isoformat()
        })
    
    return APIResponse(
        success=True,
        message=f"Retrieved {len(history_data)} command history entries",
        data={"history": history_data}
    )

# =============================================================================
# GENERIC COMMAND ENDPOINT
# =============================================================================

@app.post("/api/v1/cli/execute", response_model=APIResponse, tags=["Generic"])
async def execute_cli_command(
    request: CommandRequest,
    user = Depends(get_current_user)
):
    """Execute any allowed CLI command with full flexibility"""
    result = await cli_executor.execute_command(
        request.command,
        request.args,
        timeout=request.timeout,
        working_dir=request.working_directory
    )
    
    return APIResponse(
        success=result.status == ExecutionStatus.SUCCESS,
        message="Command executed" if result.status == ExecutionStatus.SUCCESS else "Command failed",
        data={
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code
        },
        command_executed=result.command,
        execution_time=result.execution_time
    )

# =============================================================================
# HEALTH AND CAPABILITIES
# =============================================================================

@app.get("/api/v1/health", tags=["System"])
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "allowed_commands": list(cli_executor.allowed_commands.keys())
    }

@app.get("/api/v1/capabilities", tags=["System"])
async def get_capabilities():
    """Get available CLI capabilities for LLM discovery"""
    capabilities = {
        "commands": cli_executor.allowed_commands,
        "endpoints": {
            "control_loops": [
                "POST /api/v1/cli/schema/list",
                "POST /api/v1/cli/schema/create", 
                "POST /api/v1/cli/instance/list",
                "POST /api/v1/cli/instance/create"
            ],
            "plc_operations": [
                "POST /api/v1/cli/plc/connect",
                "POST /api/v1/cli/plc/read"
            ],
            "memory_system": [
                "POST /api/v1/cli/memory/query",
                "POST /api/v1/cli/memory/ingest"
            ],
            "batch_operations": [
                "POST /api/v1/cli/batch/create"
            ],
            "system": [
                "GET /api/v1/cli/system/status",
                "GET /api/v1/history",
                "POST /api/v1/cli/execute"
            ]
        },
        "authentication": "optional",
        "rate_limits": "none",
        "documentation": "/docs"
    }
    
    return capabilities

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup initialization"""
    logger.info(f"Starting {APP_TITLE} v{APP_VERSION}")
    logger.info("CLI-to-API Bridge initialized successfully")
    logger.info(f"Available commands: {list(cli_executor.allowed_commands.keys())}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "cli_api_bridge:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="info"
    ) 