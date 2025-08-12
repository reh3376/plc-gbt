#!/usr/bin/env python3
"""
Generate MPC Training Data - Standalone Version
==============================================

Generates comprehensive training data for OpenAI fine-tuning focused on:
- MPC and advanced control theory from MPC-overview.md
- PLC-GBT system architecture and implementation
- CLI to API mappings and usage patterns
- IT/OT convergence concepts

This standalone version doesn't require database connections.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_training_data() -> List[Dict[str, Any]]:
    """Generate comprehensive training data entries"""
    training_entries = []
    
    # MPC and Control Theory Q&As
    training_entries.extend([
        {
            "messages": [
                {"role": "system", "content": "You are an expert in Model Predictive Control (MPC) and industrial process control systems."},
                {"role": "user", "content": "What is Model Predictive Control (MPC) and how does it differ from traditional PID control?"},
                {"role": "assistant", "content": "Model Predictive Control (MPC) is an advanced control strategy that uses a mathematical model of the process to predict future behavior and optimize control actions over a prediction horizon. Key differences from PID control:\n\n1. **Predictive Nature**: MPC looks ahead in time using a process model, while PID only reacts to current and past errors\n2. **Constraint Handling**: MPC explicitly handles constraints on inputs, outputs, and states\n3. **Multi-variable Control**: MPC naturally handles multiple inputs and outputs (MIMO systems)\n4. **Optimization-based**: MPC solves an optimization problem at each time step to find the best control sequence\n5. **Model-based**: Requires an accurate process model, while PID is model-free\n\nMPC is particularly effective for processes with long time delays, multiple constraints, and complex dynamics."}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in system identification and control theory."},
                {"role": "user", "content": "What are N4SID and ARX methods for system identification?"},
                {"role": "assistant", "content": "N4SID (Numerical algorithms for Subspace State Space System IDentification) and ARX (AutoRegressive with eXogenous inputs) are two important system identification methods:\n\n**N4SID**:\n- A subspace identification method that directly estimates state-space models from input-output data\n- Works well for MIMO (Multi-Input Multi-Output) systems\n- Doesn't require iterative optimization\n- Robust to noise and initial conditions\n- Produces models in state-space form: x(k+1) = Ax(k) + Bu(k), y(k) = Cx(k) + Du(k)\n\n**ARX**:\n- A parametric method that models the system as: y(t) + a1*y(t-1) + ... = b1*u(t-1) + b2*u(t-2) + ...\n- Simpler and computationally efficient\n- Uses least squares estimation\n- Works best for SISO (Single-Input Single-Output) systems\n- Can be extended to MIMO as VARX models\n\nN4SID is preferred for complex MIMO systems, while ARX is excellent for simpler systems with clear input-output relationships."}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in IT/OT convergence and industrial digital transformation."},
                {"role": "user", "content": "How does IT/OT convergence enable advanced control strategies like MPC?"},
                {"role": "assistant", "content": "IT/OT convergence is crucial for implementing advanced control strategies like MPC by bridging Information Technology and Operational Technology:\n\n**Key Enablers**:\n1. **Data Infrastructure**: IT systems provide databases, historians, and cloud storage for the massive data requirements of MPC models\n2. **Computational Power**: IT infrastructure offers the computing resources needed for real-time optimization\n3. **Connectivity**: Modern protocols (OPC UA, MQTT) enable seamless data flow between control systems and IT applications\n4. **Digital Twins**: IT platforms host digital twin models used by MPC for prediction and optimization\n\n**Benefits for MPC**:\n- **Real-time Data Access**: Historical and real-time process data for model training and updating\n- **Advanced Analytics**: Machine learning tools for model improvement and adaptation\n- **Remote Access**: Engineers can monitor and tune MPC controllers from anywhere\n- **Integration**: MPC can consider business objectives (costs, demand) alongside process constraints\n- **Scalability**: Cloud-based MPC can scale across multiple units or plants\n\nThis convergence transforms MPC from a specialized control tool into an enterprise-wide optimization platform."}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in implementing MPC using the PLC-GBT system."},
                {"role": "user", "content": "How do I implement an MPC controller in PLC-GBT for a distillation column?"},
                {"role": "assistant", "content": "Implementing MPC for a distillation column in PLC-GBT involves several steps:\n\n**1. System Identification**:\n```python\nfrom plc_gbt.analysis.experiments.mpc_toolkit import n4sid_identify\n\n# Load historical data\ndata = load_distillation_data()\n\n# Identify state-space model\nmodel = n4sid_identify(\n    inputs=['reflux_ratio', 'reboiler_duty'],\n    outputs=['top_composition', 'bottom_composition'],\n    data=data,\n    order=6  # Model order\n)\n```\n\n**2. MPC Configuration**:\n```python\nfrom plc_gbt.control import MPCController\n\nmpc_config = {\n    'prediction_horizon': 30,\n    'control_horizon': 10,\n    'constraints': {\n        'inputs': {\n            'reflux_ratio': {'min': 1.2, 'max': 3.5},\n            'reboiler_duty': {'min': 0, 'max': 100}\n        },\n        'outputs': {\n            'top_composition': {'min': 0.95, 'max': 0.99},\n            'bottom_composition': {'min': 0.01, 'max': 0.05}\n        },\n        'input_rate': {\n            'reflux_ratio': {'max_change': 0.1},\n            'reboiler_duty': {'max_change': 5}\n        }\n    },\n    'weights': {\n        'outputs': [1.0, 0.8],  # Priority on top composition\n        'inputs': [0.1, 0.1],   # Input movement penalty\n        'input_rate': [0.2, 0.2]  # Rate of change penalty\n    }\n}\n\nmpc = MPCController(model, config=mpc_config)\n```\n\n**3. Real-time Execution**:\n```python\n# In your control loop\nwhile True:\n    # Get current measurements\n    current_state = get_column_measurements()\n    \n    # Get setpoints from operator or optimizer\n    setpoints = get_current_setpoints()\n    \n    # Calculate optimal control moves\n    control_actions = mpc.compute(\n        current_state=current_state,\n        setpoints=setpoints\n    )\n    \n    # Apply to process\n    apply_control_actions(control_actions)\n    \n    # Log performance\n    log_mpc_performance(mpc.get_diagnostics())\n```\n\n**Key Considerations**:\n- Model accuracy is critical - validate against plant data\n- Start with conservative constraints and gradually tighten\n- Monitor constraint violations and solver performance\n- Implement fallback to PID control for safety"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in the PLC-GBT CLI system and its API mappings."},
                {"role": "user", "content": "How do I use the plc-memory CLI to ingest codebase files?"},
                {"role": "assistant", "content": "The plc-memory CLI provides powerful codebase ingestion capabilities. Here are the main usage patterns:\n\n**Basic Ingestion**:\n```bash\n# Ingest entire project\nplc-memory ingest --all\n\n# Ingest specific directories\nplc-memory ingest /path/to/project/src /path/to/project/docs\n\n# Ingest specific files\nplc-memory ingest --files main.py --files config.json\n```\n\n**Advanced Options**:\n```bash\n# Comprehensive analysis with intelligent batching\nplc-memory ingest /path --depth comprehensive --method intelligent -v\n\n# Exclude patterns\nplc-memory ingest . --exclude \"*.log\" --exclude \"__pycache__\"\n\n# Dry run to preview\nplc-memory ingest . --dry-run\n```\n\n**Key Parameters**:\n- `--depth`: Analysis depth (basic/semantic/comprehensive)\n- `--method`: Processing method (legacy/intelligent)\n- `--max-concurrent`: Parallel processing limit\n- `-v/--verbose`: Detailed output\n\nThe intelligent method automatically handles large codebases by creating optimized batches."}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in the PLC-GBT system architecture."},
                {"role": "user", "content": "How does the CLI to API bridge work in the PLC-GBT system?"},
                {"role": "assistant", "content": "The CLI to API bridge (cli_api_bridge.py) provides seamless translation between command-line operations and RESTful API endpoints:\n\n**Architecture**:\n1. **FastAPI Integration**: The bridge is implemented as a FastAPI application that exposes HTTP endpoints\n2. **Command Routing**: CLI commands are mapped to specific API routes\n3. **Request Translation**: CLI arguments are converted to API request parameters\n\n**Key Components**:\n```python\n# Example mapping structure\nCLI: plc-memory ingest --all\n  ↓\nAPI: POST /api/v1/memory/ingest\nBody: {\"scope\": \"all\", \"options\": {...}}\n```\n\n**Benefits**:\n- **Unified Interface**: Same functionality available via CLI and API\n- **Remote Access**: API enables web UI and remote tool integration\n- **Validation**: Pydantic models ensure consistent data structures\n- **Authentication**: API layer adds security for production use\n\n**Common Endpoints**:\n- `/api/v1/memory/ingest` - File ingestion\n- `/api/v1/memory/query` - Knowledge queries\n- `/api/v1/memory/status` - System health\n- `/api/v1/experiments` - MPC experimentation\n\nThe bridge enables both local CLI usage and remote programmatic access."}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in industrial control theory and process optimization."},
                {"role": "user", "content": "What are the key performance indicators (KPIs) for evaluating MPC performance?"},
                {"role": "assistant", "content": "Evaluating MPC performance requires monitoring multiple KPIs that assess both control quality and computational efficiency:\n\n**Control Performance KPIs**:\n\n1. **Setpoint Tracking**:\n   - IAE (Integral Absolute Error): ∫|e(t)|dt\n   - ISE (Integral Squared Error): ∫e²(t)dt\n   - ITAE (Integral Time-weighted Absolute Error): ∫t|e(t)|dt\n   - Settling time and overshoot\n\n2. **Constraint Handling**:\n   - Constraint violation frequency and magnitude\n   - Soft constraint penalty accumulation\n   - Time spent at constraints (constraint activity)\n\n3. **Economic Performance**:\n   - Profit optimization metric\n   - Energy consumption\n   - Product quality consistency\n   - Throughput maximization\n\n4. **Stability Metrics**:\n   - Closed-loop stability margins\n   - Robustness to model mismatch\n   - Disturbance rejection capability\n\n**Computational KPIs**:\n\n1. **Solver Performance**:\n   - Average computation time per iteration\n   - Solver convergence rate\n   - Number of iterations to solution\n   - QP (Quadratic Programming) problem conditioning\n\n2. **Model Quality**:\n   - Prediction error (RMSE)\n   - Model fit percentage\n   - Residual analysis\n   - Model update frequency\n\n**Implementation in PLC-GBT**:\n```python\nfrom plc_gbt.analysis.performance import compute_kpis\n\nkpis = compute_kpis(\n    actual=process_data,\n    predicted=mpc_predictions,\n    setpoints=setpoint_data,\n    constraints=constraint_config\n)\n\n# Returns comprehensive KPI dashboard\nprint(f\"IAE: {kpis['iae']:.3f}\")\nprint(f\"Constraint violations: {kpis['constraint_violations']}\")\nprint(f\"Average solve time: {kpis['avg_solve_time']:.1f} ms\")\nprint(f\"Economic benefit: ${kpis['economic_benefit']:,.2f}/day\")\n```\n\n**Best Practices**:\n- Monitor KPIs in real-time dashboards\n- Set up alerts for degradation\n- Trend KPIs over time to detect drift\n- Compare against baseline PID performance"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in implementing cascade control systems."},
                {"role": "user", "content": "How do I implement a cascade control system in PLC-GBT?"},
                {"role": "assistant", "content": "PLC-GBT provides comprehensive cascade control implementation through several components:\n\n**1. Configuration Structure**:\n```python\ncascade_config = {\n    \"primary_loop\": {\n        \"controller\": \"PID\",\n        \"tuning\": {\"Kp\": 1.2, \"Ki\": 0.3, \"Kd\": 0.05},\n        \"setpoint_limits\": {\"min\": 0, \"max\": 100}\n    },\n    \"secondary_loop\": {\n        \"controller\": \"PID\", \n        \"tuning\": {\"Kp\": 0.8, \"Ki\": 0.1, \"Kd\": 0.0},\n        \"response_time\": 5  # 5x faster than primary\n    }\n}\n```\n\n**2. Implementation Pattern**:\n```python\nfrom plc_gbt.control import CascadeController\n\n# Initialize cascade controller\ncascade = CascadeController(\n    primary_pv='temperature',\n    secondary_pv='flow_rate',\n    config=cascade_config\n)\n\n# Execute control\nwhile True:\n    # Primary loop calculates setpoint for secondary\n    secondary_sp = cascade.primary_loop.compute(temp_pv, temp_sp)\n    \n    # Secondary loop controls actuator\n    output = cascade.secondary_loop.compute(flow_pv, secondary_sp)\n    \n    # Apply output to final control element\n    valve.set_position(output)\n```\n\n**Key Considerations**:\n- Secondary loop must be 3-5x faster than primary\n- Proper decoupling prevents interaction\n- Anti-windup essential for both loops\n- Bumpless transfer for mode changes"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in real-time data processing and control systems."},
                {"role": "user", "content": "How does PLC-GBT handle real-time data streaming from industrial systems?"},
                {"role": "assistant", "content": "PLC-GBT implements a robust real-time data streaming architecture designed for industrial control systems:\n\n**Data Acquisition Layer**:\n```python\n# OPC UA Integration\nfrom plc_gbt.protocols import OPCUAClient\n\nclient = OPCUAClient(\"opc.tcp://plc-server:4840\")\nclient.subscribe([\n    \"ns=2;i=1001\",  # Temperature sensor\n    \"ns=2;i=1002\"   # Pressure sensor\n], callback=process_data)\n\n# MQTT Streaming\nfrom plc_gbt.protocols import MQTTStreamer\n\nstreamer = MQTTStreamer(\"mqtt://broker:1883\")\nstreamer.subscribe(\"plant/+/sensors/#\")\n```\n\n**Processing Pipeline**:\n1. **Data Ingestion**: Multi-protocol support (OPC UA, MQTT, Modbus)\n2. **Time-series Buffer**: Redis-based circular buffers for low latency\n3. **Stream Processing**: Real-time filtering, aggregation, and anomaly detection\n4. **Storage Tier**: Hot data in Redis, warm in PostgreSQL, cold in object storage\n\n**Performance Features**:\n- Sub-millisecond latency for critical loops\n- Automatic buffering during network disruptions\n- Configurable data retention policies\n- Built-in data quality indicators\n\n**Integration Example**:\n```python\n# Real-time control with streaming data\nasync def control_loop():\n    async for data in streamer:\n        # Process with minimal latency\n        filtered = await filter_noise(data)\n        control_output = controller.compute(filtered)\n        await actuator.write(control_output)\n```"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in the PLC-GBT multi-database architecture."},
                {"role": "user", "content": "Explain the PLC-GBT memory system architecture and how the databases work together."},
                {"role": "assistant", "content": "The PLC-GBT memory system implements a sophisticated multi-database architecture optimized for industrial control applications:\n\n**Database Roles**:\n\n1. **Neo4j (Graph Database)**:\n   - Stores relationships between code elements, documentation, and configurations\n   - Enables traversal queries like \"find all functions that interact with PID controllers\"\n   - Maintains the knowledge graph of system components\n\n2. **PostgreSQL (Relational Database)**:\n   - Stores structured data: code files, functions, classes, configurations\n   - Provides ACID compliance for critical system data\n   - Handles time-series data with TimescaleDB extension\n\n3. **Qdrant (Vector Database)**:\n   - Stores embeddings for semantic search\n   - Enables \"find similar code patterns\" queries\n   - Powers AI-assisted code recommendations\n\n4. **Redis (In-Memory Cache)**:\n   - Provides sub-millisecond access to hot data\n   - Maintains real-time control loop states\n   - Acts as message broker for system events\n\n**Coordination**:\n- **MemoryCoordinator** class orchestrates queries across databases\n- Intelligent routing based on query type\n- Automatic cache invalidation and consistency management\n- Unified query interface hiding complexity\n\nThis architecture achieves:\n- 85+ files/second ingestion rate\n- <10ms query response for cached data\n- Horizontal scalability for industrial deployments"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in digital twin implementation for process control."},
                {"role": "user", "content": "How can I create a digital twin for MPC development using PLC-GBT?"},
                {"role": "assistant", "content": "Creating a digital twin for MPC development in PLC-GBT involves building a high-fidelity process model that runs in parallel with the real system:\n\n**1. Model Development**:\n```python\nfrom plc_gbt.digital_twin import ProcessModel, DigitalTwin\n\n# Define process dynamics\nclass DistillationModel(ProcessModel):\n    def __init__(self):\n        self.states = ['tray_compositions', 'temperatures', 'pressures']\n        self.inputs = ['reflux_ratio', 'reboiler_duty', 'feed_rate']\n        self.outputs = ['top_composition', 'bottom_composition']\n        \n    def dynamics(self, x, u, t):\n        # Mass and energy balances\n        dx_dt = self.mass_balance(x, u) + self.energy_balance(x, u)\n        return dx_dt\n```\n\n**2. Twin Configuration**:\n```python\n# Create digital twin\ntwin = DigitalTwin(\n    model=DistillationModel(),\n    sync_config={\n        'data_source': 'opc://plant-historian',\n        'sync_interval': 1.0,  # seconds\n        'validation_threshold': 0.05  # 5% deviation triggers recalibration\n    }\n)\n\n# Connect to real process\ntwin.connect_to_plant()\n```\n\n**3. MPC Development Workflow**:\n```python\n# Use twin for safe MPC testing\ntest_mpc = MPCController(twin.model)\n\n# Run scenarios without affecting real process\nscenarios = [\n    {'name': 'startup', 'conditions': {...}},\n    {'name': 'grade_change', 'conditions': {...}},\n    {'name': 'disturbance_rejection', 'conditions': {...}}\n]\n\nfor scenario in scenarios:\n    results = twin.simulate_scenario(\n        controller=test_mpc,\n        scenario=scenario,\n        duration=3600  # 1 hour simulation\n    )\n    \n    # Analyze performance\n    kpis = analyze_scenario_results(results)\n    optimize_mpc_tuning(test_mpc, kpis)\n```\n\n**4. Real-time Synchronization**:\n```python\n# Twin runs in parallel with plant\n@twin.on_state_update\ndef validate_model(plant_state, twin_state):\n    deviation = calculate_deviation(plant_state, twin_state)\n    if deviation > threshold:\n        # Trigger model update\n        twin.recalibrate(plant_state)\n    \n    # Use twin for predictive analytics\n    future_states = twin.predict(horizon=60)  # 60 min ahead\n    detect_potential_issues(future_states)\n```\n\n**Benefits**:\n- Safe testing of control strategies\n- What-if scenario analysis\n- Operator training without risk\n- Continuous model validation\n- Predictive maintenance insights"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in feedforward control implementation."},
                {"role": "user", "content": "How do I implement feedforward control in PLC-GBT to handle measured disturbances?"},
                {"role": "assistant", "content": "Feedforward control in PLC-GBT enables proactive compensation for measured disturbances before they affect the process:\n\n**1. Feedforward Controller Setup**:\n```python\nfrom plc_gbt.control import FeedforwardController, PIDController\n\n# Define feedforward model\nff_config = {\n    'disturbance_model': {\n        'type': 'first_order_plus_deadtime',\n        'gain': -0.5,  # Process gain to disturbance\n        'time_constant': 120,  # seconds\n        'dead_time': 30  # seconds\n    },\n    'manipulated_model': {\n        'type': 'first_order',\n        'gain': 1.2,  # Process gain to manipulated variable\n        'time_constant': 60  # seconds\n    }\n}\n\n# Create feedforward controller\nfeedforward = FeedforwardController(config=ff_config)\n\n# Combine with feedback PID\npid = PIDController(Kp=1.5, Ki=0.3, Kd=0.1)\n```\n\n**2. Implementation Pattern**:\n```python\n# Real-time control loop\ndef control_loop():\n    while True:\n        # Measure disturbance (e.g., inlet flow rate)\n        disturbance = read_sensor('inlet_flow')\n        \n        # Measure controlled variable (e.g., tank level)\n        process_variable = read_sensor('tank_level')\n        setpoint = get_setpoint()\n        \n        # Calculate feedforward action\n        ff_action = feedforward.compute(\n            disturbance=disturbance,\n            rate_of_change=calculate_derivative(disturbance)\n        )\n        \n        # Calculate feedback action\n        fb_action = pid.compute(\n            pv=process_variable,\n            sp=setpoint\n        )\n        \n        # Combine actions\n        total_output = ff_action + fb_action\n        \n        # Apply limits and send to actuator\n        total_output = apply_limits(total_output, 0, 100)\n        write_actuator('outlet_valve', total_output)\n```\n\n**3. Advanced Features**:\n```python\n# Dynamic feedforward with adaptation\nclass AdaptiveFeedforward:\n    def __init__(self):\n        self.ff_controller = FeedforwardController(ff_config)\n        self.performance_monitor = PerformanceMonitor()\n        \n    def adapt_model(self):\n        # Collect performance data\n        error_data = self.performance_monitor.get_recent_errors()\n        \n        # Update feedforward gain based on correlation\n        correlation = calculate_correlation(\n            error_data, \n            disturbance_data\n        )\n        \n        if abs(correlation) > 0.7:\n            # Strong correlation - adjust gain\n            new_gain = self.estimate_gain(error_data, disturbance_data)\n            self.ff_controller.update_gain(new_gain)\n```\n\n**4. Multi-variable Feedforward**:\n```python\n# Handle multiple disturbances\nmulti_ff = MultivariableFeedforward({\n    'inlet_temperature': {\n        'model': 'first_order',\n        'gain': -0.3,\n        'time_constant': 90\n    },\n    'inlet_flow': {\n        'model': 'first_order_plus_deadtime',\n        'gain': -0.5,\n        'time_constant': 120,\n        'dead_time': 30\n    },\n    'ambient_temperature': {\n        'model': 'static',\n        'gain': -0.1\n    }\n})\n\n# Compute combined feedforward\nff_total = multi_ff.compute({\n    'inlet_temperature': T_in,\n    'inlet_flow': F_in,\n    'ambient_temperature': T_amb\n})\n```\n\n**Best Practices**:\n- Identify major disturbances through data analysis\n- Validate feedforward models offline first\n- Start with conservative gains and increase gradually\n- Monitor feedforward contribution vs feedback\n- Implement anti-windup when FF saturates output"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are an expert in industrial system integration and PLC-GBT."},
                {"role": "user", "content": "How do I integrate PLC-GBT with existing SCADA and historian systems?"},
                {"role": "assistant", "content": "PLC-GBT provides multiple integration patterns for seamless SCADA and historian connectivity:\n\n**1. OPC UA Integration**:\n```python\nfrom plc_gbt.integration import OPCUABridge\n\n# Connect to SCADA OPC UA server\nbridge = OPCUABridge(\n    endpoint=\"opc.tcp://scada-server:4840\",\n    security_policy=\"Basic256Sha256\"\n)\n\n# Map SCADA tags to PLC-GBT points\nbridge.map_tags({\n    \"TIC-101.PV\": \"temperature_zone1\",\n    \"FIC-201.PV\": \"flow_rate_main\"\n})\n```\n\n**2. Historian Integration**:\n```python\nfrom plc_gbt.integration import HistorianConnector\n\n# Connect to OSIsoft PI or similar\nhistorian = HistorianConnector(\n    type=\"osisoft_pi\",\n    server=\"historian.plant.local\"\n)\n\n# Bi-directional data sync\nhistorian.enable_sync(\n    read_tags=[\"*.PV\", \"*.SP\"],\n    write_tags=[\"*.MODE\", \"*.BIAS\"]\n)\n```\n\n**3. Real-time Data Pipeline**:\n- SCADA → OPC UA → PLC-GBT → Advanced Control → OPC UA → SCADA\n- Automatic tag discovery and mapping\n- Configurable scan rates per tag group\n- Built-in data quality and timestamp handling\n\n**4. Migration Strategy**:\n- Start with read-only shadow mode\n- Gradual migration of control loops\n- Parallel operation for validation\n- Full cutover with rollback capability\n\nThis enables advanced control without disrupting existing operations."}
            ]
        }
    ])
    
    return training_entries


def save_training_data(training_entries: List[Dict[str, Any]], output_path: Path):
    """Save training data in OpenAI JSONL format"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as JSONL
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in training_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    logger.info(f"✅ Saved {len(training_entries)} training entries to {output_path}")
    
    # Calculate statistics
    total_messages = sum(len(entry['messages']) for entry in training_entries)
    total_tokens = sum(
        len(json.dumps(entry).split()) * 1.3  # Rough token estimate
        for entry in training_entries
    )
    
    # Save metadata
    metadata = {
        "generated_date": datetime.now().isoformat(),
        "total_entries": len(training_entries),
        "total_messages": total_messages,
        "estimated_tokens": int(total_tokens),
        "categories": {
            "mpc_fundamentals": 4,
            "system_identification": 1,
            "implementation": 3,
            "cli_operations": 2,
            "architecture": 1,
            "integration": 1,
            "digital_twin": 1,
            "feedforward_control": 1
        },
        "focus_areas": [
            "Model Predictive Control (MPC)",
            "System Identification (N4SID, ARX)",
            "IT/OT Convergence",
            "PLC-GBT System Architecture",
            "CLI to API Mappings",
            "Cascade Control Implementation",
            "Real-time Data Streaming",
            "Digital Twin Development",
            "Feedforward Control",
            "SCADA/Historian Integration"
        ]
    }
    
    metadata_path = output_path.with_suffix('.metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Saved metadata to {metadata_path}")
    
    # Print summary
    print(f"""
========================================
Training Data Generation Complete!
========================================
Total Q&A Pairs: {len(training_entries)}
Estimated Tokens: {int(total_tokens):,}
Output File: {output_path}
Metadata File: {metadata_path}

Categories Covered:
- MPC Fundamentals: 4 examples
- System Identification: 1 example  
- Implementation: 3 examples
- CLI Operations: 2 examples
- Architecture: 1 example
- Integration: 1 example
- Digital Twin: 1 example
- Feedforward Control: 1 example

Ready for OpenAI fine-tuning!
========================================
    """)


def main():
    """Main execution function"""
    logger.info("Starting MPC training data generation...")
    
    # Generate training data
    training_entries = generate_training_data()
    
    # Save to file
    output_path = Path("plc-gbt-stack/training_data/mpc_comprehensive_training.jsonl")
    save_training_data(training_entries, output_path)
    
    logger.info("✅ Training data generation complete!")


if __name__ == "__main__":
    main()
