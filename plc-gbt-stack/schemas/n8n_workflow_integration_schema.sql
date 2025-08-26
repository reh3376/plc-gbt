-- =====================================================================================
-- N8N Framework Integration - PostgreSQL Schema Extension
-- Phase 1.2: Workflow Storage Schema Implementation
-- 
-- Following AI Task Orchestrator TypeScript methodology with strict compliance
-- Date: December 22, 2024
-- =====================================================================================

-- Create dedicated schema for workflow management
CREATE SCHEMA IF NOT EXISTS plc_workflows;
SET search_path = plc_workflows, public;

-- =====================================================================================
-- CORE WORKFLOW TABLES
-- =====================================================================================

-- Workflow definitions table - stores n8n workflow JSON with industrial extensions
CREATE TABLE plc_workflows.workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workflow_data JSONB NOT NULL, -- N8N workflow format with industrial metadata
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived', 'error')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID, -- References users table if available
    
    -- Industrial workflow categorization
    industrial_tags TEXT[] DEFAULT '{}',
    industrial_category VARCHAR(100) DEFAULT 'general' CHECK (
        industrial_category IN (
            'control', 'monitoring', 'data_acquisition', 'safety', 
            'communication', 'analytics', 'maintenance', 'general'
        )
    ),
    
    -- Performance and compliance metadata
    performance_profile JSONB DEFAULT '{}', -- Expected execution time, resource usage
    compliance_level VARCHAR(20) DEFAULT 'standard' CHECK (
        compliance_level IN ('standard', 'industrial', 'safety_critical')
    ),
    
    -- Version control and audit
    schema_version VARCHAR(20) DEFAULT '1.106.0', -- N8N workflow schema version
    checksum VARCHAR(64), -- SHA-256 hash of workflow_data for integrity
    
    -- Indexes for performance
    UNIQUE(name, version)
);

-- Workflow execution history - comprehensive execution tracking
CREATE TABLE plc_workflows.workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES plc_workflows.workflow_definitions(id) ON DELETE CASCADE,
    
    -- Execution metadata
    execution_mode VARCHAR(20) DEFAULT 'manual' CHECK (
        execution_mode IN ('manual', 'scheduled', 'webhook', 'triggered', 'batch')
    ),
    execution_data JSONB NOT NULL, -- Input data and execution context
    
    -- Status tracking
    status VARCHAR(50) NOT NULL CHECK (
        status IN ('running', 'completed', 'failed', 'cancelled', 'timeout', 'waiting')
    ),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    
    -- Results and error handling
    output_data JSONB, -- Execution results
    error_message TEXT,
    error_code VARCHAR(50),
    error_details JSONB, -- Detailed error information including node-specific errors
    
    -- Performance metrics for industrial requirements
    performance_metrics JSONB DEFAULT '{}', -- Execution time, memory usage, throughput
    node_execution_stats JSONB DEFAULT '{}', -- Per-node execution statistics
    
    -- Industrial compliance tracking
    compliance_status VARCHAR(20) DEFAULT 'compliant' CHECK (
        compliance_status IN ('compliant', 'non_compliant', 'under_review')
    ),
    audit_log JSONB DEFAULT '{}', -- Compliance and audit trail
    
    -- Resource utilization
    resource_usage JSONB DEFAULT '{}', -- CPU, memory, network usage during execution
    
    -- Execution environment
    execution_environment JSONB DEFAULT '{}' -- Runtime context, variables, credentials used
);

-- Node execution details - granular tracking for industrial debugging
CREATE TABLE plc_workflows.node_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID NOT NULL REFERENCES plc_workflows.workflow_executions(id) ON DELETE CASCADE,
    
    -- Node identification
    node_id VARCHAR(255) NOT NULL, -- Node ID from workflow definition
    node_type VARCHAR(255) NOT NULL, -- Node type (e.g., 'n8n-nodes-base.httpRequest')
    node_name VARCHAR(255) NOT NULL, -- Display name of the node
    
    -- Execution timing
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    execution_duration_ms INTEGER,
    
    -- Status and results
    status VARCHAR(20) NOT NULL CHECK (
        status IN ('running', 'completed', 'failed', 'skipped', 'timeout')
    ),
    input_data JSONB, -- Data received by the node
    output_data JSONB, -- Data produced by the node
    
    -- Error handling
    error_message TEXT,
    error_type VARCHAR(100),
    error_details JSONB,
    
    -- Industrial-specific metrics
    industrial_metrics JSONB DEFAULT '{}', -- PLC values, sensor readings, control outputs
    safety_status VARCHAR(20) DEFAULT 'safe' CHECK (
        safety_status IN ('safe', 'warning', 'alarm', 'critical')
    ),
    
    -- Performance tracking
    resource_usage JSONB DEFAULT '{}', -- Node-specific resource consumption
    retry_count INTEGER DEFAULT 0,
    retry_details JSONB DEFAULT '{}' -- Retry attempts and results
);

-- Workflow templates - industrial workflow templates library
CREATE TABLE plc_workflows.workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_data JSONB NOT NULL, -- Template workflow structure
    
    -- Template categorization
    category VARCHAR(100) NOT NULL CHECK (
        category IN (
            'pid_control', 'data_acquisition', 'alarm_management', 'batch_processing',
            'safety_systems', 'communication', 'reporting', 'maintenance', 'custom'
        )
    ),
    subcategory VARCHAR(100),
    
    -- Industrial metadata
    industrial_standards TEXT[], -- Applicable industrial standards (IEC, ISA, etc.)
    equipment_compatibility TEXT[], -- Compatible equipment types
    process_types TEXT[], -- Compatible process types
    
    -- Template versioning
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    template_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(2,1) DEFAULT 0.0 CHECK (rating >= 0.0 AND rating <= 5.0),
    
    -- Template validation
    validation_status VARCHAR(20) DEFAULT 'pending' CHECK (
        validation_status IN ('pending', 'validated', 'deprecated', 'archived')
    ),
    validation_notes TEXT,
    
    UNIQUE(name, version)
);

-- Workflow schedules - advanced scheduling for industrial automation
CREATE TABLE plc_workflows.workflow_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES plc_workflows.workflow_definitions(id) ON DELETE CASCADE,
    
    -- Schedule configuration
    name VARCHAR(255) NOT NULL,
    description TEXT,
    schedule_type VARCHAR(20) NOT NULL CHECK (
        schedule_type IN ('cron', 'interval', 'event_driven', 'condition_based')
    ),
    
    -- Cron-based scheduling
    cron_expression VARCHAR(100), -- Standard cron expression
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Interval-based scheduling
    interval_seconds INTEGER, -- Interval in seconds
    
    -- Condition-based scheduling
    trigger_conditions JSONB DEFAULT '{}', -- Conditions that trigger execution
    
    -- Schedule status
    is_active BOOLEAN DEFAULT true,
    next_execution TIMESTAMP WITH TIME ZONE,
    last_execution TIMESTAMP WITH TIME ZONE,
    
    -- Execution constraints for industrial safety
    max_concurrent_executions INTEGER DEFAULT 1,
    execution_timeout_seconds INTEGER DEFAULT 3600, -- 1 hour default
    retry_policy JSONB DEFAULT '{"max_retries": 3, "retry_delay_seconds": 60}',
    
    -- Industrial scheduling features
    maintenance_windows JSONB DEFAULT '[]', -- Time windows when execution is prohibited
    priority_level INTEGER DEFAULT 5 CHECK (priority_level >= 1 AND priority_level <= 10),
    resource_requirements JSONB DEFAULT '{}', -- Required system resources
    
    -- Audit and compliance
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    schedule_audit_log JSONB DEFAULT '[]' -- Schedule change history
);

-- =====================================================================================
-- INDUSTRIAL EXTENSIONS
-- =====================================================================================

-- Industrial node registry - enhanced node metadata for industrial use
CREATE TABLE plc_workflows.industrial_node_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Node identification
    node_type VARCHAR(255) NOT NULL UNIQUE, -- Full node type identifier
    node_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Node classification
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    industrial_classification VARCHAR(100), -- Industrial-specific classification
    
    -- Capabilities and features
    capabilities JSONB DEFAULT '{}', -- Node capabilities and features
    supported_protocols TEXT[], -- Supported industrial protocols
    data_types TEXT[], -- Supported data types
    
    -- Performance characteristics
    average_execution_time_ms INTEGER,
    memory_usage_kb INTEGER,
    cpu_intensity VARCHAR(20) DEFAULT 'low' CHECK (cpu_intensity IN ('low', 'medium', 'high')),
    io_intensity VARCHAR(20) DEFAULT 'low' CHECK (io_intensity IN ('low', 'medium', 'high')),
    
    -- Industrial compliance
    safety_level VARCHAR(10) DEFAULT 'SIL0' CHECK (safety_level IN ('SIL0', 'SIL1', 'SIL2', 'SIL3')),
    certifications TEXT[], -- Industrial certifications (IEC 61131, IEC 62443, etc.)
    compliance_standards TEXT[], -- Applicable compliance standards
    
    -- Node configuration schema
    configuration_schema JSONB, -- JSON schema for node configuration
    validation_rules JSONB DEFAULT '{}', -- Validation rules for node parameters
    
    -- Documentation and support
    documentation_url VARCHAR(500),
    examples JSONB DEFAULT '[]', -- Usage examples
    troubleshooting_guide JSONB DEFAULT '{}',
    
    -- Version and lifecycle
    node_version VARCHAR(20),
    n8n_version_compatibility VARCHAR(50),
    lifecycle_status VARCHAR(20) DEFAULT 'active' CHECK (
        lifecycle_status IN ('active', 'deprecated', 'archived', 'experimental')
    ),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE
);

-- Industrial workflow connections - enhanced connection tracking
CREATE TABLE plc_workflows.workflow_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES plc_workflows.workflow_definitions(id) ON DELETE CASCADE,
    
    -- Connection details
    source_node_id VARCHAR(255) NOT NULL,
    target_node_id VARCHAR(255) NOT NULL,
    connection_type VARCHAR(50) DEFAULT 'main',
    
    -- Data flow characteristics
    data_schema JSONB, -- Schema of data flowing through connection
    expected_data_rate INTEGER, -- Expected data rate (items/second)
    data_validation_rules JSONB DEFAULT '{}',
    
    -- Performance monitoring
    throughput_stats JSONB DEFAULT '{}', -- Historical throughput statistics
    error_rate DECIMAL(5,4) DEFAULT 0.0, -- Connection error rate
    
    -- Industrial-specific connection properties
    signal_type VARCHAR(50), -- Type of industrial signal (analog, digital, etc.)
    safety_classification VARCHAR(20) DEFAULT 'non_safety' CHECK (
        safety_classification IN ('non_safety', 'safety_related', 'safety_critical')
    ),
    redundancy_level VARCHAR(20) DEFAULT 'none' CHECK (
        redundancy_level IN ('none', 'dual', 'triple', 'quad')
    ),
    
    -- Quality metrics for industrial reliability
    reliability_score DECIMAL(3,2) DEFAULT 1.00 CHECK (reliability_score >= 0.00 AND reliability_score <= 1.00),
    last_quality_check TIMESTAMP WITH TIME ZONE,
    quality_metrics JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================================================
-- PERFORMANCE AND MONITORING TABLES
-- =====================================================================================

-- Workflow performance metrics - detailed performance tracking
CREATE TABLE plc_workflows.workflow_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES plc_workflows.workflow_definitions(id) ON DELETE CASCADE,
    
    -- Time period for metrics
    measurement_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    measurement_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Execution statistics
    total_executions INTEGER NOT NULL DEFAULT 0,
    successful_executions INTEGER NOT NULL DEFAULT 0,
    failed_executions INTEGER NOT NULL DEFAULT 0,
    average_execution_time_ms DECIMAL(10,2),
    min_execution_time_ms INTEGER,
    max_execution_time_ms INTEGER,
    
    -- Resource utilization
    average_cpu_usage DECIMAL(5,2), -- Percentage
    peak_cpu_usage DECIMAL(5,2),
    average_memory_usage_mb DECIMAL(10,2),
    peak_memory_usage_mb DECIMAL(10,2),
    
    -- Throughput metrics
    data_points_processed BIGINT DEFAULT 0,
    average_throughput_per_second DECIMAL(10,2),
    peak_throughput_per_second DECIMAL(10,2),
    
    -- Error analysis
    error_breakdown JSONB DEFAULT '{}', -- Categorized error statistics
    most_common_errors JSONB DEFAULT '[]', -- Top error types and frequencies
    
    -- Industrial KPIs
    availability_percentage DECIMAL(5,2) DEFAULT 100.00, -- System availability
    reliability_score DECIMAL(3,2) DEFAULT 1.00, -- Overall reliability
    safety_incidents INTEGER DEFAULT 0, -- Safety-related incidents
    compliance_score DECIMAL(3,2) DEFAULT 1.00, -- Compliance adherence score
    
    -- Quality metrics
    data_quality_score DECIMAL(3,2) DEFAULT 1.00, -- Data quality assessment
    sla_compliance_percentage DECIMAL(5,2) DEFAULT 100.00, -- SLA compliance
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================================================

-- Workflow definitions indexes
CREATE INDEX idx_workflow_definitions_status ON plc_workflows.workflow_definitions(status);
CREATE INDEX idx_workflow_definitions_category ON plc_workflows.workflow_definitions(industrial_category);
CREATE INDEX idx_workflow_definitions_tags ON plc_workflows.workflow_definitions USING GIN(industrial_tags);
CREATE INDEX idx_workflow_definitions_created_at ON plc_workflows.workflow_definitions(created_at);
CREATE INDEX idx_workflow_definitions_updated_at ON plc_workflows.workflow_definitions(updated_at);

-- Workflow executions indexes
CREATE INDEX idx_workflow_executions_workflow_id ON plc_workflows.workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_status ON plc_workflows.workflow_executions(status);
CREATE INDEX idx_workflow_executions_started_at ON plc_workflows.workflow_executions(started_at);
CREATE INDEX idx_workflow_executions_finished_at ON plc_workflows.workflow_executions(finished_at);
CREATE INDEX idx_workflow_executions_execution_mode ON plc_workflows.workflow_executions(execution_mode);

-- Node executions indexes
CREATE INDEX idx_node_executions_workflow_execution_id ON plc_workflows.node_executions(workflow_execution_id);
CREATE INDEX idx_node_executions_node_type ON plc_workflows.node_executions(node_type);
CREATE INDEX idx_node_executions_status ON plc_workflows.node_executions(status);
CREATE INDEX idx_node_executions_started_at ON plc_workflows.node_executions(started_at);
CREATE INDEX idx_node_executions_safety_status ON plc_workflows.node_executions(safety_status);

-- Workflow schedules indexes
CREATE INDEX idx_workflow_schedules_workflow_id ON plc_workflows.workflow_schedules(workflow_id);
CREATE INDEX idx_workflow_schedules_active ON plc_workflows.workflow_schedules(is_active);
CREATE INDEX idx_workflow_schedules_next_execution ON plc_workflows.workflow_schedules(next_execution);
CREATE INDEX idx_workflow_schedules_schedule_type ON plc_workflows.workflow_schedules(schedule_type);

-- Industrial node registry indexes
CREATE INDEX idx_industrial_nodes_category ON plc_workflows.industrial_node_registry(category);
CREATE INDEX idx_industrial_nodes_safety_level ON plc_workflows.industrial_node_registry(safety_level);
CREATE INDEX idx_industrial_nodes_lifecycle ON plc_workflows.industrial_node_registry(lifecycle_status);
CREATE INDEX idx_industrial_nodes_protocols ON plc_workflows.industrial_node_registry USING GIN(supported_protocols);
CREATE INDEX idx_industrial_nodes_certifications ON plc_workflows.industrial_node_registry USING GIN(certifications);

-- =====================================================================================
-- FUNCTIONS AND TRIGGERS FOR INDUSTRIAL REQUIREMENTS
-- =====================================================================================

-- Function to update workflow modification timestamp
CREATE OR REPLACE FUNCTION plc_workflows.update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
CREATE TRIGGER trigger_workflow_definitions_updated_at
    BEFORE UPDATE ON plc_workflows.workflow_definitions
    FOR EACH ROW EXECUTE FUNCTION plc_workflows.update_modified_timestamp();

CREATE TRIGGER trigger_workflow_templates_updated_at
    BEFORE UPDATE ON plc_workflows.workflow_templates
    FOR EACH ROW EXECUTE FUNCTION plc_workflows.update_modified_timestamp();

CREATE TRIGGER trigger_workflow_schedules_updated_at
    BEFORE UPDATE ON plc_workflows.workflow_schedules
    FOR EACH ROW EXECUTE FUNCTION plc_workflows.update_modified_timestamp();

CREATE TRIGGER trigger_industrial_node_registry_updated_at
    BEFORE UPDATE ON plc_workflows.industrial_node_registry
    FOR EACH ROW EXECUTE FUNCTION plc_workflows.update_modified_timestamp();

-- Function to calculate workflow checksum for integrity verification
CREATE OR REPLACE FUNCTION plc_workflows.calculate_workflow_checksum(workflow_data JSONB)
RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(sha256(workflow_data::text::bytea), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically calculate checksum on workflow updates
CREATE OR REPLACE FUNCTION plc_workflows.update_workflow_checksum()
RETURNS TRIGGER AS $$
BEGIN
    NEW.checksum = plc_workflows.calculate_workflow_checksum(NEW.workflow_data);
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_workflow_checksum
    BEFORE INSERT OR UPDATE ON plc_workflows.workflow_definitions
    FOR EACH ROW EXECUTE FUNCTION plc_workflows.update_workflow_checksum();

-- Function to update execution duration automatically
CREATE OR REPLACE FUNCTION plc_workflows.update_execution_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.finished_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.execution_duration_ms = EXTRACT(EPOCH FROM (NEW.finished_at - NEW.started_at)) * 1000;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_node_execution_duration
    BEFORE UPDATE ON plc_workflows.node_executions
    FOR EACH ROW EXECUTE FUNCTION plc_workflows.update_execution_duration();

-- =====================================================================================
-- VIEWS FOR CONVENIENT DATA ACCESS
-- =====================================================================================

-- Active workflows with latest execution status
CREATE VIEW plc_workflows.active_workflows_summary AS
SELECT 
    wd.id,
    wd.name,
    wd.description,
    wd.industrial_category,
    wd.compliance_level,
    wd.created_at,
    wd.updated_at,
    we.status as last_execution_status,
    we.started_at as last_execution_start,
    we.finished_at as last_execution_finish,
    we.performance_metrics as last_execution_metrics
FROM plc_workflows.workflow_definitions wd
LEFT JOIN plc_workflows.workflow_executions we ON wd.id = we.workflow_id
WHERE wd.status = 'active'
AND (we.started_at IS NULL OR we.started_at = (
    SELECT MAX(started_at) 
    FROM plc_workflows.workflow_executions 
    WHERE workflow_id = wd.id
));

-- Workflow execution summary with statistics
CREATE VIEW plc_workflows.workflow_execution_summary AS
SELECT 
    wd.id as workflow_id,
    wd.name as workflow_name,
    wd.industrial_category,
    COUNT(we.id) as total_executions,
    COUNT(CASE WHEN we.status = 'completed' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN we.status = 'failed' THEN 1 END) as failed_executions,
    AVG(EXTRACT(EPOCH FROM (we.finished_at - we.started_at)) * 1000) as avg_execution_time_ms,
    MAX(we.started_at) as last_execution,
    wd.performance_profile
FROM plc_workflows.workflow_definitions wd
LEFT JOIN plc_workflows.workflow_executions we ON wd.id = we.workflow_id
GROUP BY wd.id, wd.name, wd.industrial_category, wd.performance_profile;

-- Industrial node usage statistics
CREATE VIEW plc_workflows.node_usage_statistics AS
SELECT 
    inr.node_type,
    inr.display_name,
    inr.category,
    inr.safety_level,
    COUNT(ne.id) as total_executions,
    COUNT(CASE WHEN ne.status = 'completed' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN ne.status = 'failed' THEN 1 END) as failed_executions,
    AVG(ne.execution_duration_ms) as avg_execution_time_ms,
    MAX(ne.started_at) as last_used
FROM plc_workflows.industrial_node_registry inr
LEFT JOIN plc_workflows.node_executions ne ON inr.node_type = ne.node_type
GROUP BY inr.node_type, inr.display_name, inr.category, inr.safety_level;

-- =====================================================================================
-- SECURITY AND PERMISSIONS
-- =====================================================================================

-- Grant appropriate permissions (adjust based on your user management system)
-- Note: Replace 'plc_workflow_user' with actual application user/role
-- GRANT USAGE ON SCHEMA plc_workflows TO plc_workflow_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA plc_workflows TO plc_workflow_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA plc_workflows TO plc_workflow_user;

-- =====================================================================================
-- INITIAL DATA AND CONFIGURATION
-- =====================================================================================

-- Insert default industrial node registry entries for common n8n nodes
INSERT INTO plc_workflows.industrial_node_registry (
    node_type, node_name, display_name, description, category, subcategory,
    industrial_classification, capabilities, supported_protocols, safety_level,
    average_execution_time_ms, memory_usage_kb, cpu_intensity, io_intensity
) VALUES
    ('n8n-nodes-base.httpRequest', 'HTTP Request', 'HTTP Request', 
     'Make HTTP requests to REST APIs and web services', 'communication', 'http',
     'data_acquisition', '{"methods": ["GET", "POST", "PUT", "DELETE"], "auth": ["basic", "oauth"], "ssl": true}',
     ARRAY['HTTP', 'HTTPS', 'REST'], 'SIL0', 150, 512, 'low', 'medium'),
    
    ('n8n-nodes-base.postgres', 'PostgreSQL', 'PostgreSQL Database', 
     'Execute SQL queries against PostgreSQL databases', 'database', 'sql',
     'data_storage', '{"operations": ["select", "insert", "update", "delete"], "transactions": true}',
     ARRAY['PostgreSQL', 'SQL'], 'SIL1', 200, 1024, 'medium', 'high'),
    
    ('n8n-nodes-base.redis', 'Redis', 'Redis Cache', 
     'Store and retrieve data from Redis cache', 'database', 'cache',
     'data_caching', '{"operations": ["get", "set", "delete", "expire"], "pub_sub": true}',
     ARRAY['Redis', 'TCP'], 'SIL0', 50, 256, 'low', 'medium'),
    
    ('n8n-nodes-base.mqtt', 'MQTT', 'MQTT Broker', 
     'Publish and subscribe to MQTT topics', 'communication', 'mqtt',
     'industrial_communication', '{"qos_levels": [0, 1, 2], "retain": true, "last_will": true}',
     ARRAY['MQTT', 'TCP', 'Websockets'], 'SIL1', 100, 512, 'low', 'medium'),
    
    ('n8n-nodes-base.schedule', 'Schedule', 'Schedule Trigger', 
     'Trigger workflows on a schedule using cron expressions', 'trigger', 'time',
     'automation', '{"cron": true, "interval": true, "timezone_support": true}',
     ARRAY[], 'SIL0', 10, 128, 'low', 'low');

-- Insert sample workflow templates for common industrial scenarios
INSERT INTO plc_workflows.workflow_templates (
    name, description, template_data, category, subcategory,
    industrial_standards, equipment_compatibility, process_types, version
) VALUES
    ('PID Control Loop Monitor', 
     'Template for monitoring PID control loops with alarm management',
     '{"nodes": [], "connections": {}, "template_type": "pid_monitoring"}',
     'pid_control', 'monitoring', 
     ARRAY['IEC 61131-3', 'ISA-88'], 
     ARRAY['PLC', 'DCS', 'SCADA'], 
     ARRAY['continuous', 'batch'], '1.0.0'),
    
    ('Data Acquisition Template', 
     'Template for collecting data from industrial sensors and equipment',
     '{"nodes": [], "connections": {}, "template_type": "data_acquisition"}',
     'data_acquisition', 'sensors', 
     ARRAY['IEC 61850', 'Modbus'], 
     ARRAY['sensors', 'transmitters', 'analyzers'], 
     ARRAY['continuous', 'discrete'], '1.0.0'),
    
    ('Alarm Management System', 
     'Template for industrial alarm management and notification',
     '{"nodes": [], "connections": {}, "template_type": "alarm_management"}',
     'alarm_management', 'notifications', 
     ARRAY['IEC 62682', 'ISA-18.2'], 
     ARRAY['alarm_servers', 'HMI', 'SCADA'], 
     ARRAY['all'], '1.0.0');

-- =====================================================================================
-- SCHEMA VALIDATION AND HEALTH CHECK FUNCTIONS
-- =====================================================================================

-- Function to validate workflow JSON schema
CREATE OR REPLACE FUNCTION plc_workflows.validate_workflow_schema(workflow_data JSONB)
RETURNS BOOLEAN AS $$
BEGIN
    -- Basic schema validation for n8n workflow format
    IF NOT (workflow_data ? 'nodes' AND workflow_data ? 'connections') THEN
        RETURN FALSE;
    END IF;
    
    -- Validate nodes array
    IF NOT (jsonb_typeof(workflow_data->'nodes') = 'array') THEN
        RETURN FALSE;
    END IF;
    
    -- Validate connections object
    IF NOT (jsonb_typeof(workflow_data->'connections') = 'object') THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get schema health status
CREATE OR REPLACE FUNCTION plc_workflows.get_schema_health()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    total_workflows INTEGER;
    active_workflows INTEGER;
    total_executions INTEGER;
    avg_execution_time DECIMAL(10,2);
    error_rate DECIMAL(5,4);
BEGIN
    -- Collect health metrics
    SELECT COUNT(*) INTO total_workflows FROM plc_workflows.workflow_definitions;
    SELECT COUNT(*) INTO active_workflows FROM plc_workflows.workflow_definitions WHERE status = 'active';
    SELECT COUNT(*) INTO total_executions FROM plc_workflows.workflow_executions;
    
    SELECT AVG(EXTRACT(EPOCH FROM (finished_at - started_at)) * 1000)
    INTO avg_execution_time
    FROM plc_workflows.workflow_executions
    WHERE finished_at IS NOT NULL;
    
    SELECT 
        COALESCE(
            (COUNT(CASE WHEN status = 'failed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0)) * 100,
            0
        )
    INTO error_rate
    FROM plc_workflows.workflow_executions;
    
    -- Build result
    result := jsonb_build_object(
        'schema_version', '1.106.0',
        'total_workflows', total_workflows,
        'active_workflows', active_workflows,
        'total_executions', total_executions,
        'avg_execution_time_ms', avg_execution_time,
        'error_rate_percentage', error_rate,
        'last_updated', NOW(),
        'status', CASE 
            WHEN error_rate > 10 THEN 'degraded'
            WHEN error_rate > 5 THEN 'warning'
            ELSE 'healthy'
        END
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================================
-- COMPLETION MARKER
-- =====================================================================================

-- Insert schema version and completion marker
INSERT INTO plc_workflows.workflow_definitions (
    name, description, workflow_data, version, status, 
    industrial_category, compliance_level, schema_version
) VALUES (
    '__schema_validation__', 
    'N8N Framework Integration Schema - Phase 1.2 Completion Marker',
    '{"nodes": [], "connections": {}, "schema_initialized": true, "phase": "1.2"}',
    1, 'active', 'general', 'standard', '1.106.0'
) ON CONFLICT (name, version) DO NOTHING;

-- Reset search path
SET search_path = public;

-- =====================================================================================
-- SCHEMA CREATION COMPLETED SUCCESSFULLY
-- Phase 1.2: PostgreSQL Schema Extension for N8N Workflow Storage
-- Industrial-Grade Schema with Performance, Security, and Compliance Features
-- =====================================================================================
