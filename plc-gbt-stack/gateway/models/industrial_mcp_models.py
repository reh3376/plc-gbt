"""
Industrial MCP Pydantic Models
Extracted from industrial_automation_mcp_proxy.py to reduce complexity
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ControlLoopRequest(BaseModel):
    name: str = Field(..., description="Control loop name")
    loop_type: str = Field("PID", description="Control loop type (PID, PI, PD, etc.)")
    setpoint: float = Field(..., description="Desired setpoint value")
    process_variable: str = Field(..., description="Process variable to control")
    output_variable: str = Field(..., description="Control output variable")
    tuning_params: Optional[Dict[str, float]] = Field(None, description="PID tuning parameters")
    safety_limits: Optional[Dict[str, float]] = Field(None, description="Safety limits")

class ControlLoopResponse(BaseModel):
    success: bool = Field(..., description="Whether control loop was created successfully")
    control_loop_id: str = Field(..., description="Unique control loop identifier")
    schema_used: str = Field(..., description="Control loop schema applied")
    parameters: Dict[str, Any] = Field(..., description="Applied control parameters")
    validation_score: float = Field(..., description="Validation score (0-100)")
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")

class PIDTuningRequest(BaseModel):
    control_loop_id: str = Field(..., description="Control loop to tune")
    tuning_method: str = Field("auto", description="Tuning method (auto, ziegler-nichols, cohen-coon)")
    process_data: Optional[List[Dict[str, float]]] = Field(None, description="Historical process data")
    performance_criteria: str = Field("balanced", description="Performance criteria (fast, balanced, stable)")

class PIDTuningResponse(BaseModel):
    success: bool = Field(..., description="Whether tuning was successful")
    tuned_parameters: Dict[str, float] = Field(..., description="Optimized PID parameters")
    performance_prediction: Dict[str, float] = Field(..., description="Predicted performance metrics")
    tuning_method_used: str = Field(..., description="Tuning method applied")
    recommendations: List[str] = Field(default_factory=list, description="Implementation recommendations")

class PLCConnectionRequest(BaseModel):
    plc_address: str = Field(..., description="PLC IP address or hostname")
    plc_type: str = Field("ControlLogix", description="PLC type (ControlLogix, CompactLogix, etc.)")
    slot: int = Field(0, description="PLC slot number")
    timeout: float = Field(5.0, description="Connection timeout in seconds")
    protocol: str = Field("EtherNet/IP", description="Communication protocol")

class PLCConnectionResponse(BaseModel):
    success: bool = Field(..., description="Whether connection was successful")
    connection_id: str = Field(..., description="Connection identifier")
    plc_info: Dict[str, Any] = Field(..., description="PLC system information")
    available_tags: List[str] = Field(default_factory=list, description="Available PLC tags")
    connection_status: str = Field(..., description="Connection status details")

class SafetySystemRequest(BaseModel):
    safety_system_name: str = Field(..., description="Safety system name")
    safety_function: str = Field(..., description="Safety function to validate")
    interlocks: List[Dict[str, Any]] = Field(..., description="Safety interlock definitions")
    fail_safe_actions: List[str] = Field(..., description="Fail-safe actions")
    sil_level: int = Field(1, ge=1, le=4, description="Safety Integrity Level (1-4)")

class SafetySystemResponse(BaseModel):
    validation_passed: bool = Field(..., description="Whether safety validation passed")
    sil_compliance: bool = Field(..., description="SIL level compliance")
    safety_score: float = Field(..., description="Overall safety score (0-100)")
    compliance_issues: List[str] = Field(default_factory=list, description="Compliance issues found")
    recommendations: List[str] = Field(default_factory=list, description="Safety recommendations")

class SystemStatusResponse(BaseModel):
    system_healthy: bool = Field(..., description="Overall system health")
    active_control_loops: int = Field(..., description="Number of active control loops")
    plc_connections: int = Field(..., description="Number of active PLC connections")
    memory_usage: Dict[str, float] = Field(..., description="Memory usage statistics")
    performance_metrics: Dict[str, float] = Field(..., description="System performance metrics")
    alerts: List[str] = Field(default_factory=list, description="Active system alerts")

class IndustrialKnowledgeRequest(BaseModel):
    query: str = Field(..., description="Search query for industrial knowledge")
    domain: Optional[str] = Field(None, description="Knowledge domain filter")
    limit: int = Field(10, ge=1, le=50, description="Maximum results to return")

class IndustrialKnowledgeResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Knowledge search results")
    total_found: int = Field(..., description="Total results found")
    search_time_ms: float = Field(..., description="Search execution time")
    knowledge_domains: List[str] = Field(default_factory=list, description="Available knowledge domains")
