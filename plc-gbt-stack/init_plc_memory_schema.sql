-- PLC Memory Database Schema Initialization
-- Creates all required tables for the plc-memory system

-- Python files table
CREATE TABLE IF NOT EXISTS python_files (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL UNIQUE,
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes INTEGER NOT NULL DEFAULT 0,
    functions_count INTEGER DEFAULT 0,
    classes_count INTEGER DEFAULT 0,
    lines_of_code INTEGER DEFAULT 0,
    complexity_score REAL DEFAULT 0.0,
    data JSONB NOT NULL,
    metadata JSONB,
    embedding_generated BOOLEAN DEFAULT FALSE,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documentation table
CREATE TABLE IF NOT EXISTS documentation (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL UNIQUE,
    file_name VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    doc_type VARCHAR(50) DEFAULT 'markdown',
    file_size_bytes INTEGER NOT NULL DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    section_count INTEGER DEFAULT 0,
    data JSONB NOT NULL,
    metadata JSONB,
    embedding_generated BOOLEAN DEFAULT FALSE,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Configuration files table
CREATE TABLE IF NOT EXISTS configuration_files (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL UNIQUE,
    file_name VARCHAR(255) NOT NULL,
    config_type VARCHAR(50) DEFAULT 'json',
    file_size_bytes INTEGER NOT NULL DEFAULT 0,
    key_count INTEGER DEFAULT 0,
    validation_status VARCHAR(20) DEFAULT 'pending',
    data JSONB NOT NULL,
    metadata JSONB,
    embedding_generated BOOLEAN DEFAULT FALSE,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Experiment models table (for MPC functionality)
CREATE TABLE IF NOT EXISTS experiment_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    kind TEXT NOT NULL,
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(name, version)
);

-- Experiment runs table
CREATE TABLE IF NOT EXISTS experiment_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES experiment_models(id),
    run_name TEXT NOT NULL,
    status TEXT NOT NULL,
    results JSONB,
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    UNIQUE(model_id, run_name)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_python_files_path ON python_files(file_path);
CREATE INDEX IF NOT EXISTS idx_python_files_embedding ON python_files(embedding_generated);
CREATE INDEX IF NOT EXISTS idx_documentation_path ON documentation(file_path);
CREATE INDEX IF NOT EXISTS idx_documentation_embedding ON documentation(embedding_generated);
CREATE INDEX IF NOT EXISTS idx_configuration_files_path ON configuration_files(file_path);
CREATE INDEX IF NOT EXISTS idx_configuration_files_type ON configuration_files(config_type);
CREATE INDEX IF NOT EXISTS idx_experiment_models_name ON experiment_models(name);
CREATE INDEX IF NOT EXISTS idx_experiment_runs_model ON experiment_runs(model_id);
CREATE INDEX IF NOT EXISTS idx_experiment_runs_status ON experiment_runs(status);
