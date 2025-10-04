-- =====================================================================
-- PLC-GBT File Storage System - Production Schema
-- =====================================================================
-- This schema provides enterprise-grade file storage with:
-- - Metadata management in PostgreSQL
-- - Hierarchical folder structure
-- - Version control and soft deletes
-- - Access control and permissions
-- - Full-text search capabilities
-- - Audit logging
-- =====================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- =====================================================================
-- FILE CATEGORIES & TYPES
-- =====================================================================

CREATE TABLE IF NOT EXISTS file_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default categories
INSERT INTO file_categories (name, description, icon, color) VALUES
    ('plc-programs', 'PLC program files (.acd, .l5x)', 'cpu', '#4fc3f7'),
    ('workflows', 'Automation workflow definitions', 'workflow', '#ba68c8'),
    ('chat-histories', 'AI Assistant conversation histories', 'message-square', '#ffb74d'),
    ('documentation', 'Documentation and guides', 'file-text', '#66bb6a'),
    ('configurations', 'System configuration files', 'settings', '#ff7043'),
    ('exports', 'Exported data and reports', 'download', '#90a4ae'),
    ('uploads', 'User uploaded files', 'upload', '#ffa726'),
    ('projects', 'Project files and archives', 'folder', '#42a5f5')
ON CONFLICT (name) DO NOTHING;

-- =====================================================================
-- FOLDERS (Hierarchical Structure)
-- =====================================================================

CREATE TABLE IF NOT EXISTS folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES folders(id) ON DELETE CASCADE,
    path TEXT NOT NULL, -- Full path for quick lookups
    category_id INTEGER REFERENCES file_categories(id),
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE, -- System folders can't be deleted
    permissions JSONB DEFAULT '{"read": ["*"], "write": ["admin"], "delete": ["admin"]}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE, -- Soft delete
    
    CONSTRAINT unique_folder_path UNIQUE(path),
    CONSTRAINT no_self_reference CHECK (id != parent_id)
);

-- Create index for hierarchical queries
CREATE INDEX IF NOT EXISTS idx_folders_parent_id ON folders(parent_id);
CREATE INDEX IF NOT EXISTS idx_folders_path ON folders USING gin(path gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_folders_deleted_at ON folders(deleted_at);

-- =====================================================================
-- FILES (Main File Metadata Table)
-- =====================================================================

CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    folder_id UUID REFERENCES folders(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES file_categories(id),
    
    -- File storage information
    storage_path TEXT NOT NULL, -- Relative path in filesystem
    storage_type VARCHAR(50) DEFAULT 'local', -- local, s3, azure, etc.
    file_size BIGINT NOT NULL, -- Size in bytes
    mime_type VARCHAR(255),
    file_extension VARCHAR(50),
    checksum VARCHAR(64), -- SHA-256 hash for integrity
    
    -- Content and metadata
    description TEXT,
    tags TEXT[], -- Array of tags for categorization
    metadata JSONB DEFAULT '{}'::jsonb, -- Custom metadata
    
    -- Version control
    version INTEGER DEFAULT 1,
    is_latest_version BOOLEAN DEFAULT TRUE,
    parent_version_id UUID REFERENCES files(id) ON DELETE SET NULL,
    
    -- Access control
    permissions JSONB DEFAULT '{"read": ["*"], "write": ["owner"], "delete": ["owner"]}'::jsonb,
    is_public BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    locked_by VARCHAR(255),
    locked_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    
    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by VARCHAR(255),
    
    CONSTRAINT positive_file_size CHECK (file_size >= 0),
    CONSTRAINT positive_version CHECK (version > 0)
);

-- Create comprehensive indexes
CREATE INDEX IF NOT EXISTS idx_files_folder_id ON files(folder_id);
CREATE INDEX IF NOT EXISTS idx_files_category_id ON files(category_id);
CREATE INDEX IF NOT EXISTS idx_files_name ON files USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_files_tags ON files USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_files_checksum ON files(checksum);
CREATE INDEX IF NOT EXISTS idx_files_created_by ON files(created_by);
CREATE INDEX IF NOT EXISTS idx_files_deleted_at ON files(deleted_at);
CREATE INDEX IF NOT EXISTS idx_files_version ON files(parent_version_id, version);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_files_search ON files USING gin(
    to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, ''))
);

-- =====================================================================
-- FILE VERSIONS (Version History)
-- =====================================================================

CREATE TABLE IF NOT EXISTS file_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    checksum VARCHAR(64),
    change_description TEXT,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_file_version UNIQUE(file_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_file_versions_file_id ON file_versions(file_id);

-- =====================================================================
-- FILE ACCESS LOG (Audit Trail)
-- =====================================================================

CREATE TABLE IF NOT EXISTS file_access_log (
    id BIGSERIAL PRIMARY KEY,
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL, -- read, write, delete, download, upload
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_access_log_file_id ON file_access_log(file_id);
CREATE INDEX IF NOT EXISTS idx_file_access_log_user_id ON file_access_log(user_id);
CREATE INDEX IF NOT EXISTS idx_file_access_log_created_at ON file_access_log(created_at);

-- =====================================================================
-- FILE SHARES (Sharing & Collaboration)
-- =====================================================================

CREATE TABLE IF NOT EXISTS file_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    share_token VARCHAR(64) UNIQUE NOT NULL,
    shared_by VARCHAR(255) NOT NULL,
    shared_with VARCHAR(255), -- NULL for public shares
    permissions JSONB DEFAULT '{"read": true, "write": false, "delete": false}'::jsonb,
    expires_at TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    max_access_count INTEGER, -- Limit number of accesses
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_file_shares_file_id ON file_shares(file_id);
CREATE INDEX IF NOT EXISTS idx_file_shares_token ON file_shares(share_token);
CREATE INDEX IF NOT EXISTS idx_file_shares_expires_at ON file_shares(expires_at);

-- =====================================================================
-- FILE TAGS (Separate table for better management)
-- =====================================================================

CREATE TABLE IF NOT EXISTS file_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_tags_name ON file_tags USING gin(name gin_trgm_ops);

-- =====================================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================================

-- View: Active files (not deleted) with category info
CREATE OR REPLACE VIEW active_files AS
SELECT 
    f.*,
    fc.name as category_name,
    fc.icon as category_icon,
    fc.color as category_color,
    fol.path as folder_path,
    fol.name as folder_name
FROM files f
LEFT JOIN file_categories fc ON f.category_id = fc.id
LEFT JOIN folders fol ON f.folder_id = fol.id
WHERE f.deleted_at IS NULL;

-- View: File storage statistics
CREATE OR REPLACE VIEW file_storage_stats AS
SELECT 
    fc.name as category,
    COUNT(f.id)::BIGINT as file_count,
    COALESCE(SUM(f.file_size), 0)::BIGINT as total_size,
    COALESCE(AVG(f.file_size), 0)::BIGINT as avg_size,
    COALESCE(MAX(f.file_size), 0)::BIGINT as max_size
FROM files f
LEFT JOIN file_categories fc ON f.category_id = fc.id
WHERE f.deleted_at IS NULL
GROUP BY fc.name;

-- =====================================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at on files
CREATE TRIGGER update_files_updated_at 
    BEFORE UPDATE ON files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Auto-update updated_at on folders
CREATE TRIGGER update_folders_updated_at 
    BEFORE UPDATE ON folders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Get folder hierarchy
CREATE OR REPLACE FUNCTION get_folder_hierarchy(folder_uuid UUID)
RETURNS TABLE (
    id UUID,
    name VARCHAR(255),
    level INTEGER
) AS $$
WITH RECURSIVE folder_tree AS (
    -- Base case
    SELECT id, name, parent_id, 0 as level
    FROM folders
    WHERE id = folder_uuid
    
    UNION ALL
    
    -- Recursive case
    SELECT f.id, f.name, f.parent_id, ft.level + 1
    FROM folders f
    INNER JOIN folder_tree ft ON f.parent_id = ft.id
)
SELECT id, name, level
FROM folder_tree
ORDER BY level;
$$ LANGUAGE SQL;

-- Function: Calculate folder size (including subfolders)
CREATE OR REPLACE FUNCTION calculate_folder_size(folder_uuid UUID)
RETURNS BIGINT AS $$
WITH RECURSIVE folder_tree AS (
    SELECT id FROM folders WHERE id = folder_uuid
    UNION ALL
    SELECT f.id FROM folders f
    INNER JOIN folder_tree ft ON f.parent_id = ft.id
)
SELECT COALESCE(SUM(file_size), 0)
FROM files
WHERE folder_id IN (SELECT id FROM folder_tree)
  AND deleted_at IS NULL;
$$ LANGUAGE SQL;

-- Function: Search files with full-text search
CREATE OR REPLACE FUNCTION search_files(
    search_query TEXT,
    category_filter INTEGER DEFAULT NULL,
    tag_filter TEXT[] DEFAULT NULL,
    limit_results INTEGER DEFAULT 100
)
RETURNS TABLE (
    id UUID,
    name VARCHAR(255),
    description TEXT,
    folder_path TEXT,
    file_size BIGINT,
    created_at TIMESTAMP WITH TIME ZONE,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.name,
        f.description,
        fol.path as folder_path,
        f.file_size,
        f.created_at,
        ts_rank(
            to_tsvector('english', coalesce(f.name, '') || ' ' || coalesce(f.description, '')),
            plainto_tsquery('english', search_query)
        ) as rank
    FROM files f
    LEFT JOIN folders fol ON f.folder_id = fol.id
    WHERE f.deleted_at IS NULL
      AND to_tsvector('english', coalesce(f.name, '') || ' ' || coalesce(f.description, ''))
          @@ plainto_tsquery('english', search_query)
      AND (category_filter IS NULL OR f.category_id = category_filter)
      AND (tag_filter IS NULL OR f.tags && tag_filter)
    ORDER BY rank DESC
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- INITIAL DATA: Create default folder structure
-- =====================================================================

-- Root folder
INSERT INTO folders (id, name, parent_id, path, is_system, created_by) VALUES
    ('00000000-0000-0000-0000-000000000001', 'Root', NULL, '/', TRUE, 'system')
ON CONFLICT (path) DO NOTHING;

-- System folders
INSERT INTO folders (name, parent_id, path, category_id, is_system, created_by)
SELECT 
    fc.name,
    '00000000-0000-0000-0000-000000000001',
    '/' || fc.name,
    fc.id,
    TRUE,
    'system'
FROM file_categories fc
ON CONFLICT (path) DO NOTHING;

-- =====================================================================
-- GRANTS (Adjust based on your user roles)
-- =====================================================================

-- Grant access to application user (adjust username as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO plc_gbt_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO plc_gbt_app;

-- =====================================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================================

COMMENT ON TABLE files IS 'Main file metadata table with version control and soft delete';
COMMENT ON TABLE folders IS 'Hierarchical folder structure for organizing files';
COMMENT ON TABLE file_versions IS 'Version history for files';
COMMENT ON TABLE file_access_log IS 'Audit log of all file operations';
COMMENT ON TABLE file_shares IS 'File sharing and collaboration tokens';
COMMENT ON COLUMN files.checksum IS 'SHA-256 hash for file integrity verification';
COMMENT ON COLUMN files.storage_path IS 'Relative path to file in storage backend';
COMMENT ON COLUMN files.is_latest_version IS 'Indicates if this is the current version';

