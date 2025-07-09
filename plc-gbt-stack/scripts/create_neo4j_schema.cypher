// ============================================================================
// PLC-Savvy GPT Neo4j Schema Implementation
// Created: January 1, 2025
// Purpose: Define graph database structure for PLC knowledge representation
// ============================================================================

// Clear existing data (CAUTION: This removes all data)
// MATCH (n) DETACH DELETE n;

// ============================================================================
// NODE TYPE DEFINITIONS
// ============================================================================

// 1. PLCProgram Node
// Represents a complete PLC program/project
// Properties: name (string), firmware (string), project (string), created_at, updated_at
CREATE CONSTRAINT plc_program_name_unique IF NOT EXISTS FOR (p:PLCProgram) REQUIRE p.name IS UNIQUE;
CREATE INDEX plc_program_firmware IF NOT EXISTS FOR (p:PLCProgram) ON (p.firmware);
CREATE INDEX plc_program_project IF NOT EXISTS FOR (p:PLCProgram) ON (p.project);

// 2. Routine Node  
// Represents individual routines within PLC programs
// Properties: name (string), language (string), file_path (string), created_at, updated_at
CREATE CONSTRAINT routine_path_unique IF NOT EXISTS FOR (r:Routine) REQUIRE r.file_path IS UNIQUE;
CREATE INDEX routine_name IF NOT EXISTS FOR (r:Routine) ON (r.name);
CREATE INDEX routine_language IF NOT EXISTS FOR (r:Routine) ON (r.language);

// 3. AOI (Add-On Instruction) Node
// Represents reusable instruction blocks
// Properties: name (string), rev (string), desc (string), created_at, updated_at
CREATE CONSTRAINT aoi_name_unique IF NOT EXISTS FOR (a:AOI) REQUIRE a.name IS UNIQUE;
CREATE INDEX aoi_revision IF NOT EXISTS FOR (a:AOI) ON (a.rev);

// 4. UDT (User Defined Type) Node
// Represents custom data types
// Properties: name (string), size (integer), desc (string), created_at, updated_at
CREATE CONSTRAINT udt_name_unique IF NOT EXISTS FOR (u:UDT) REQUIRE u.name IS UNIQUE;
CREATE INDEX udt_size IF NOT EXISTS FOR (u:UDT) ON (u.size);

// 5. SpecDoc (Specification Document) Node
// Represents documentation and specification files
// Properties: title (string), doc_type (string), version (string), file_path (string), created_at, updated_at
CREATE CONSTRAINT specdoc_path_unique IF NOT EXISTS FOR (s:SpecDoc) REQUIRE s.file_path IS UNIQUE;
CREATE INDEX specdoc_type IF NOT EXISTS FOR (s:SpecDoc) ON (s.doc_type);
CREATE INDEX specdoc_version IF NOT EXISTS FOR (s:SpecDoc) ON (s.version);

// 6. QuestionAnswer Node
// Represents Q&A pairs derived from documentation
// Properties: question (string), answer (string), embedding_id (string), confidence (float), created_at, updated_at
CREATE CONSTRAINT qa_embedding_unique IF NOT EXISTS FOR (q:QuestionAnswer) REQUIRE q.embedding_id IS UNIQUE;
CREATE INDEX qa_confidence IF NOT EXISTS FOR (q:QuestionAnswer) ON (q.confidence);

// ============================================================================
// ADDITIONAL SUPPORTING NODE TYPES
// ============================================================================

// 7. Tag Node
// Represents PLC tags/variables
// Properties: name (string), data_type (string), scope (string), address (string)
CREATE CONSTRAINT tag_address_unique IF NOT EXISTS FOR (t:Tag) REQUIRE t.address IS UNIQUE;
CREATE INDEX tag_name IF NOT EXISTS FOR (t:Tag) ON (t.name);
CREATE INDEX tag_type IF NOT EXISTS FOR (t:Tag) ON (t.data_type);
CREATE INDEX tag_scope IF NOT EXISTS FOR (t:Tag) ON (t.scope);

// 8. Device Node  
// Represents hardware devices in the PLC system
// Properties: name (string), device_type (string), ip_address (string), slot (integer)
CREATE INDEX device_type IF NOT EXISTS FOR (d:Device) ON (d.device_type);
CREATE INDEX device_ip IF NOT EXISTS FOR (d:Device) ON (d.ip_address);

// 9. Network Node
// Represents network configurations
// Properties: name (string), network_type (string), subnet (string)
CREATE INDEX network_type IF NOT EXISTS FOR (n:Network) ON (n.network_type);

// ============================================================================
// RELATIONSHIP TYPE DEFINITIONS
// ============================================================================

// Primary PLC Program Relationships
// PLCProgram -CONTAINS-> Routine/UDT/AOI
CREATE INDEX contains_rel IF NOT EXISTS FOR ()-[r:CONTAINS]-() ON (r.created_at);

// Routine Relationships
// Routine -USES-> AOI
CREATE INDEX uses_rel IF NOT EXISTS FOR ()-[r:USES]-() ON (r.created_at);

// Routine -IN_PROGRAM-> PLCProgram  
CREATE INDEX in_program_rel IF NOT EXISTS FOR ()-[r:IN_PROGRAM]-() ON (r.created_at);

// AOI Relationships
// AOI -USES_UDT-> UDT
CREATE INDEX uses_udt_rel IF NOT EXISTS FOR ()-[r:USES_UDT]-() ON (r.created_at);

// Documentation Relationships
// SpecDoc -COVERS-> any (PLCProgram, Routine, AOI, UDT)
CREATE INDEX covers_rel IF NOT EXISTS FOR ()-[r:COVERS]-() ON (r.created_at);

// QuestionAnswer -DERIVED_FROM-> SpecDoc
CREATE INDEX derived_from_rel IF NOT EXISTS FOR ()-[r:DERIVED_FROM]-() ON (r.created_at);

// Additional Relationships
// Routine -USES-> Tag
// AOI -DEFINES-> Tag  
// Device -HOSTS-> PLCProgram
// PLCProgram -CONNECTS_TO-> Network
// Tag -MAPS_TO-> Device

// ============================================================================
// SAMPLE DATA CREATION (For Testing)
// ============================================================================

// Create sample PLC Program
CREATE (plc:PLCProgram {
    name: "MainProgram_v1.2",
    firmware: "v34.011",
    project: "LineControl_2025", 
    created_at: datetime(),
    updated_at: datetime(),
    description: "Main control program for production line"
});

// Create sample Routines
CREATE (r1:Routine {
    name: "MainRoutine",
    language: "Ladder Logic",
    file_path: "/programs/MainProgram_v1.2/MainRoutine.L5X",
    created_at: datetime(),
    updated_at: datetime(),
    description: "Primary control logic routine"
});

CREATE (r2:Routine {
    name: "SafetyRoutine", 
    language: "Function Block",
    file_path: "/programs/MainProgram_v1.2/SafetyRoutine.L5X",
    created_at: datetime(),
    updated_at: datetime(),
    description: "Safety interlocks and emergency stops"
});

// Create sample AOIs
CREATE (aoi1:AOI {
    name: "ConveyorControl_AOI",
    rev: "1.3",
    desc: "Standard conveyor control with speed and direction",
    created_at: datetime(),
    updated_at: datetime(),
    parameters: ["Speed", "Direction", "Enable", "Status"]
});

CREATE (aoi2:AOI {
    name: "MotorStarter_AOI",
    rev: "2.1", 
    desc: "Motor starter with overload protection",
    created_at: datetime(),
    updated_at: datetime(),
    parameters: ["Start", "Stop", "Overload", "Running"]
});

// Create sample UDTs
CREATE (udt1:UDT {
    name: "ConveyorData_UDT",
    size: 32,
    desc: "Data structure for conveyor status and control",
    created_at: datetime(),
    updated_at: datetime(),
    members: ["Speed", "Direction", "Running", "Fault"]
});

CREATE (udt2:UDT {
    name: "MotorData_UDT", 
    size: 16,
    desc: "Motor control and status data structure",
    created_at: datetime(),
    updated_at: datetime(),
    members: ["Command", "Status", "Current", "Temperature"]
});

// Create sample SpecDoc
CREATE (spec1:SpecDoc {
    title: "LineControl System Specification",
    doc_type: "System Specification",
    version: "2.1",
    file_path: "/docs/LineControl_SystemSpec_v2.1.pdf",
    created_at: datetime(),
    updated_at: datetime(),
    page_count: 45
});

CREATE (spec2:SpecDoc {
    title: "Safety Requirements Document",
    doc_type: "Safety Manual", 
    version: "1.4",
    file_path: "/docs/Safety_Requirements_v1.4.pdf",
    created_at: datetime(),
    updated_at: datetime(),
    page_count: 28
});

// Create sample QuestionAnswer
CREATE (qa1:QuestionAnswer {
    question: "How do you configure the conveyor speed control?",
    answer: "The conveyor speed is controlled through the ConveyorControl_AOI by setting the Speed parameter between 0-100%. The Direction parameter controls forward/reverse operation.",
    embedding_id: "emb_conv_speed_001",
    confidence: 0.95,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (qa2:QuestionAnswer {
    question: "What are the safety interlocks for motor operation?",
    answer: "Motor operation requires: 1) Safety circuit OK, 2) No overload condition, 3) Emergency stop not active, 4) Proper sequence from safety routine.",
    embedding_id: "emb_safety_motor_001", 
    confidence: 0.92,
    created_at: datetime(),
    updated_at: datetime()
});

// Create sample Tags
CREATE (tag1:Tag {
    name: "Conveyor_01_Speed",
    data_type: "REAL",
    scope: "Controller",
    address: "Conveyor_01.Speed",
    description: "Main conveyor speed setpoint"
});

CREATE (tag2:Tag {
    name: "Motor_01_Start",
    data_type: "BOOL", 
    scope: "Program",
    address: "Motor_01.Start",
    description: "Motor start command"
});

// Create sample Device
CREATE (dev1:Device {
    name: "CompactLogix_5380",
    device_type: "PLC",
    ip_address: "192.168.1.10",
    slot: 0,
    description: "Main control processor"
});

// ============================================================================
// RELATIONSHIP CREATION (Sample Data)
// ============================================================================

// Find the created nodes to create relationships
MATCH (plc:PLCProgram {name: "MainProgram_v1.2"})
MATCH (r1:Routine {name: "MainRoutine"})
MATCH (r2:Routine {name: "SafetyRoutine"})
MATCH (aoi1:AOI {name: "ConveyorControl_AOI"})
MATCH (aoi2:AOI {name: "MotorStarter_AOI"})
MATCH (udt1:UDT {name: "ConveyorData_UDT"})
MATCH (udt2:UDT {name: "MotorData_UDT"})
MATCH (spec1:SpecDoc {title: "LineControl System Specification"})
MATCH (spec2:SpecDoc {title: "Safety Requirements Document"})
MATCH (qa1:QuestionAnswer {embedding_id: "emb_conv_speed_001"})
MATCH (qa2:QuestionAnswer {embedding_id: "emb_safety_motor_001"})
MATCH (tag1:Tag {name: "Conveyor_01_Speed"})
MATCH (tag2:Tag {name: "Motor_01_Start"})
MATCH (dev1:Device {name: "CompactLogix_5380"})

// PLCProgram CONTAINS relationships
CREATE (plc)-[:CONTAINS {created_at: datetime()}]->(r1)
CREATE (plc)-[:CONTAINS {created_at: datetime()}]->(r2)
CREATE (plc)-[:CONTAINS {created_at: datetime()}]->(aoi1)
CREATE (plc)-[:CONTAINS {created_at: datetime()}]->(aoi2)
CREATE (plc)-[:CONTAINS {created_at: datetime()}]->(udt1)
CREATE (plc)-[:CONTAINS {created_at: datetime()}]->(udt2)

// Routine relationships
CREATE (r1)-[:IN_PROGRAM {created_at: datetime()}]->(plc)
CREATE (r2)-[:IN_PROGRAM {created_at: datetime()}]->(plc)
CREATE (r1)-[:USES {created_at: datetime(), usage_count: 3}]->(aoi1)
CREATE (r1)-[:USES {created_at: datetime(), usage_count: 2}]->(aoi2)
CREATE (r2)-[:USES {created_at: datetime(), usage_count: 1}]->(aoi2)

// AOI uses UDT relationships  
CREATE (aoi1)-[:USES_UDT {created_at: datetime()}]->(udt1)
CREATE (aoi2)-[:USES_UDT {created_at: datetime()}]->(udt2)

// Documentation relationships
CREATE (spec1)-[:COVERS {created_at: datetime(), relevance: 0.9}]->(plc)
CREATE (spec1)-[:COVERS {created_at: datetime(), relevance: 0.8}]->(aoi1)
CREATE (spec2)-[:COVERS {created_at: datetime(), relevance: 0.95}]->(r2)
CREATE (spec2)-[:COVERS {created_at: datetime(), relevance: 0.85}]->(aoi2)

// QuestionAnswer relationships
CREATE (qa1)-[:DERIVED_FROM {created_at: datetime(), page_reference: 15}]->(spec1)
CREATE (qa2)-[:DERIVED_FROM {created_at: datetime(), page_reference: 8}]->(spec2)

// Tag relationships
CREATE (r1)-[:USES {created_at: datetime(), access_type: "READ_WRITE"}]->(tag1)
CREATE (r1)-[:USES {created_at: datetime(), access_type: "WRITE"}]->(tag2)
CREATE (aoi1)-[:DEFINES {created_at: datetime()}]->(tag1)

// Device relationships
CREATE (dev1)-[:HOSTS {created_at: datetime()}]->(plc);

// ============================================================================
// VALIDATION QUERIES
// ============================================================================

// Query to validate schema creation
// MATCH (n) RETURN labels(n) as NodeType, count(n) as Count ORDER BY NodeType;

// Query to validate relationships
// MATCH ()-[r]->() RETURN type(r) as RelationType, count(r) as Count ORDER BY RelationType;

// Query to show complete program structure
// MATCH (plc:PLCProgram)-[r1:CONTAINS]->(component)
// OPTIONAL MATCH (component)-[r2]-(related)
// RETURN plc.name, type(r1), labels(component), component.name, type(r2), labels(related), related.name
// LIMIT 20;

// ============================================================================
// PERFORMANCE OPTIMIZATION
// ============================================================================

// Create composite indexes for common query patterns
CREATE INDEX plc_program_search IF NOT EXISTS FOR (p:PLCProgram) ON (p.name, p.project);
CREATE INDEX routine_program_search IF NOT EXISTS FOR (r:Routine) ON (r.name, r.language);
CREATE INDEX aoi_usage_search IF NOT EXISTS FOR (a:AOI) ON (a.name, a.rev);
CREATE INDEX qa_embedding_search IF NOT EXISTS FOR (q:QuestionAnswer) ON (q.embedding_id, q.confidence);

// ============================================================================
// SCHEMA VALIDATION COMPLETE
// ============================================================================

RETURN "PLC-Savvy GPT Neo4j Schema Implementation Complete" as Status,
       "Node types: PLCProgram, Routine, AOI, UDT, SpecDoc, QuestionAnswer, Tag, Device, Network" as NodeTypes,
       "Sample data created with full relationship graph" as SampleData,
       "Performance indexes and constraints applied" as Optimization; 