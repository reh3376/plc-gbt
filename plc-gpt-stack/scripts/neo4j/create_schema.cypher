// PLC-GPT Neo4j Schema Definition
// Phase 3: Knowledge Graph Schema Implementation
// Version: 1.0.0
// Last Updated: 2025-01-01

// ============================================
// CONSTRAINTS - Ensure data integrity
// ============================================

// Core node type constraints (Day 1)
CREATE CONSTRAINT plc_program_id IF NOT EXISTS 
ON (p:PLCProgram) ASSERT p.id IS UNIQUE;

CREATE CONSTRAINT routine_id IF NOT EXISTS 
ON (r:Routine) ASSERT r.id IS UNIQUE;

CREATE CONSTRAINT aoi_id IF NOT EXISTS 
ON (a:AOI) ASSERT a.id IS UNIQUE;

// Additional node type constraints (Day 2)
CREATE CONSTRAINT udt_id IF NOT EXISTS 
ON (u:UDT) ASSERT u.id IS UNIQUE;

CREATE CONSTRAINT tag_id IF NOT EXISTS 
ON (t:Tag) ASSERT t.id IS UNIQUE;

CREATE CONSTRAINT device_id IF NOT EXISTS 
ON (d:Device) ASSERT d.id IS UNIQUE;

CREATE CONSTRAINT spec_doc_id IF NOT EXISTS 
ON (s:SpecDoc) ASSERT s.id IS UNIQUE;

CREATE CONSTRAINT question_answer_id IF NOT EXISTS 
ON (q:QuestionAnswer) ASSERT q.id IS UNIQUE;

// ============================================
// INDEXES - Optimize query performance
// ============================================

// Name-based lookups (common queries)
CREATE INDEX plc_program_name IF NOT EXISTS 
FOR (p:PLCProgram) ON (p.name);

CREATE INDEX routine_name IF NOT EXISTS 
FOR (r:Routine) ON (r.name);

CREATE INDEX aoi_name IF NOT EXISTS 
FOR (a:AOI) ON (a.name);

CREATE INDEX udt_name IF NOT EXISTS 
FOR (u:UDT) ON (u.name);

CREATE INDEX tag_name IF NOT EXISTS 
FOR (t:Tag) ON (t.name);

CREATE INDEX device_name IF NOT EXISTS 
FOR (d:Device) ON (d.name);

// Type-based lookups
CREATE INDEX routine_type IF NOT EXISTS 
FOR (r:Routine) ON (r.type);

CREATE INDEX spec_doc_type IF NOT EXISTS 
FOR (s:SpecDoc) ON (s.doc_type);

// Embedding lookups
CREATE INDEX question_embedding IF NOT EXISTS 
FOR (q:QuestionAnswer) ON (q.embedding_id);

// ============================================
// NODE TYPE DEFINITIONS & EXAMPLES
// ============================================

// PLCProgram - Top-level controller program
// Properties:
// - id: Unique identifier (UUID)
// - name: Program name (e.g., "TestController")
// - processor_type: Controller model (e.g., "1756-L85E")
// - firmware_version: Firmware revision
// - project_name: Studio 5000 project name
// - created_date: Creation timestamp
// - modified_date: Last modification timestamp
// - description: Optional description

// Routine - Program routines (Ladder, ST, FBD, SFC)
// Properties:
// - id: Unique identifier (UUID)
// - name: Routine name (e.g., "MainRoutine")
// - type: Routine type (RLL, ST, FBD, SFC)
// - language: Programming language
// - description: Optional description
// - rung_count: Number of rungs (for ladder logic)
// - file_path: Original file location

// AOI (Add-On Instruction) - Reusable instruction blocks
// Properties:
// - id: Unique identifier (UUID)
// - name: AOI name (e.g., "MotorControl_AOI")
// - revision: Version/revision number
// - description: AOI description
// - parameters: JSON array of parameters
// - created_by: Author
// - created_date: Creation date

// UDT (User Defined Type) - Custom data structures
// Properties:
// - id: Unique identifier (UUID)
// - name: UDT name (e.g., "MotorData_UDT")
// - size: Size in bytes
// - description: UDT description
// - members: JSON array of members
// - family: Optional type family

// Tag - Controller and program tags
// Properties:
// - id: Unique identifier (UUID)
// - name: Tag name
// - data_type: Data type (BOOL, INT, REAL, etc.)
// - scope: Tag scope (Controller, Program name)
// - value: Initial/default value
// - description: Tag description

// Device - I/O modules and communication devices
// Properties:
// - id: Unique identifier (UUID)
// - name: Device name
// - catalog_number: Product catalog number
// - slot: Slot number
// - ip_address: IP address (if applicable)
// - parent_module: Parent module name

// SpecDoc - Specification documents
// Properties:
// - id: Unique identifier (UUID)
// - title: Document title
// - doc_type: Document type (Specification, Manual, etc.)
// - version: Document version
// - file_path: Original file location
// - page_count: Number of pages

// QuestionAnswer - Q&A pairs from documents
// Properties:
// - id: Unique identifier (UUID)
// - question: Question text
// - answer: Answer text
// - embedding_id: Vector embedding reference
// - confidence: Confidence score
// - source_page: Source page number

// ============================================
// RELATIONSHIP DEFINITIONS
// ============================================

// PLCProgram -[CONTAINS]-> Routine
// PLCProgram -[CONTAINS]-> AOI
// PLCProgram -[CONTAINS]-> UDT
// PLCProgram -[HAS_TAG]-> Tag
// PLCProgram -[HAS_DEVICE]-> Device

// Routine -[USES]-> AOI
// Routine -[IN_PROGRAM]-> PLCProgram
// Routine -[HAS_TAG]-> Tag

// AOI -[USES_UDT]-> UDT
// AOI -[HAS_PARAMETER]-> Tag

// Tag -[USES_TYPE]-> UDT
// Tag -[DEFINES]-> Device

// Device -[HOSTS]-> Tag

// SpecDoc -[COVERS]-> PLCProgram
// SpecDoc -[COVERS]-> AOI
// SpecDoc -[COVERS]-> UDT

// QuestionAnswer -[DERIVED_FROM]-> SpecDoc
// QuestionAnswer -[RELATES_TO]-> PLCProgram
// QuestionAnswer -[RELATES_TO]-> AOI

// ============================================
// SAMPLE DATA - Using our test L5X file
// ============================================

// Create sample PLCProgram
MERGE (p:PLCProgram {
  id: 'plc_001',
  name: 'TestController',
  processor_type: '1756-L85E',
  firmware_version: '35.00',
  project_name: 'SampleProject',
  created_date: datetime('2024-12-31T12:00:00'),
  modified_date: datetime('2025-01-01T12:00:00'),
  description: 'Sample motor control system'
});

// Create sample Routines
MERGE (r1:Routine {
  id: 'routine_001',
  name: 'MainRoutine',
  type: 'RLL',
  language: 'Ladder Logic',
  description: 'Main program routine',
  rung_count: 2,
  file_path: 'MainProgram/MainRoutine'
});

MERGE (r2:Routine {
  id: 'routine_002',
  name: 'SafetyRoutine',
  type: 'RLL',
  language: 'Ladder Logic',
  description: 'Safety monitoring routine',
  rung_count: 1,
  file_path: 'MainProgram/SafetyRoutine'
});

// Create sample AOI
MERGE (a:AOI {
  id: 'aoi_001',
  name: 'MotorControl_AOI',
  revision: '1.0',
  description: 'Motor control Add-On Instruction for speed control and monitoring',
  parameters: '[{"name":"Start","type":"BOOL","usage":"Input"},{"name":"Stop","type":"BOOL","usage":"Input"},{"name":"SpeedSetpoint","type":"REAL","usage":"Input"},{"name":"MotorData","type":"MotorData_UDT","usage":"InOut"}]',
  created_by: 'Engineer',
  created_date: datetime('2024-12-31T12:00:00')
});

// Create sample UDT
MERGE (u:UDT {
  id: 'udt_001',
  name: 'MotorData_UDT',
  size: 20,
  description: 'Motor data structure',
  members: '[{"name":"Speed","type":"REAL"},{"name":"Current","type":"REAL"},{"name":"Temperature","type":"REAL"},{"name":"Running","type":"BOOL"},{"name":"Fault","type":"BOOL"}]',
  family: 'Motor'
});

// Create sample Tags
MERGE (t1:Tag {
  id: 'tag_001',
  name: 'Motor1_Data',
  data_type: 'MotorData_UDT',
  scope: 'Controller',
  description: 'Motor 1 data structure'
});

MERGE (t2:Tag {
  id: 'tag_002',
  name: 'SystemEnable',
  data_type: 'BOOL',
  scope: 'Controller',
  value: '0',
  description: 'System enable signal'
});

// Create sample Device
MERGE (d:Device {
  id: 'device_001',
  name: 'ENBT_Module',
  catalog_number: '1756-ENBT/A',
  slot: 1,
  ip_address: '192.168.1.100',
  parent_module: 'Local'
});

// Create sample SpecDoc
MERGE (s:SpecDoc {
  id: 'spec_001',
  title: 'Motor Control System Specification',
  doc_type: 'Specification',
  version: '2.1',
  file_path: 'docs/motor_control_spec.pdf',
  page_count: 45
});

// Create sample QuestionAnswer pairs
MERGE (qa1:QuestionAnswer {
  id: 'qa_001',
  question: 'What is the purpose of the MotorControl_AOI?',
  answer: 'The MotorControl_AOI is an Add-On Instruction designed for speed control and monitoring of motors. It provides Start/Stop functionality and monitors motor parameters.',
  embedding_id: 'emb_qa_001',
  confidence: 0.95,
  source_page: 12
});

MERGE (qa2:QuestionAnswer {
  id: 'qa_002',
  question: 'How do I configure the ENBT module for Ethernet communication?',
  answer: 'The ENBT module should be installed in slot 1 with IP address 192.168.1.100. Configure it through RSLogix 5000 using the I/O Configuration tree.',
  embedding_id: 'emb_qa_002',
  confidence: 0.92,
  source_page: 23
});

// Create relationships
MATCH (p:PLCProgram {id: 'plc_001'})
MATCH (r1:Routine {id: 'routine_001'})
MATCH (r2:Routine {id: 'routine_002'})
MATCH (a:AOI {id: 'aoi_001'})
MATCH (u:UDT {id: 'udt_001'})
MERGE (p)-[:CONTAINS]->(r1)
MERGE (p)-[:CONTAINS]->(r2)
MERGE (p)-[:CONTAINS]->(a)
MERGE (p)-[:CONTAINS]->(u);

MATCH (r1:Routine {id: 'routine_001'})
MATCH (a:AOI {id: 'aoi_001'})
MERGE (r1)-[:USES]->(a);

MATCH (a:AOI {id: 'aoi_001'})
MATCH (u:UDT {id: 'udt_001'})
MERGE (a)-[:USES_UDT]->(u);

MATCH (p:PLCProgram {id: 'plc_001'})
MATCH (t1:Tag {id: 'tag_001'})
MATCH (t2:Tag {id: 'tag_002'})
MERGE (p)-[:HAS_TAG]->(t1)
MERGE (p)-[:HAS_TAG]->(t2);

MATCH (p:PLCProgram {id: 'plc_001'})
MATCH (d:Device {id: 'device_001'})
MERGE (p)-[:HAS_DEVICE]->(d);

// Create SpecDoc relationships
MATCH (s:SpecDoc {id: 'spec_001'})
MATCH (p:PLCProgram {id: 'plc_001'})
MATCH (a:AOI {id: 'aoi_001'})
MATCH (u:UDT {id: 'udt_001'})
MERGE (s)-[:COVERS]->(p)
MERGE (s)-[:COVERS]->(a)
MERGE (s)-[:COVERS]->(u);

// Create QuestionAnswer relationships
MATCH (qa1:QuestionAnswer {id: 'qa_001'})
MATCH (qa2:QuestionAnswer {id: 'qa_002'})
MATCH (s:SpecDoc {id: 'spec_001'})
MATCH (a:AOI {id: 'aoi_001'})
MATCH (d:Device {id: 'device_001'})
MERGE (qa1)-[:DERIVED_FROM]->(s)
MERGE (qa1)-[:RELATES_TO]->(a)
MERGE (qa2)-[:DERIVED_FROM]->(s)
MERGE (qa2)-[:RELATES_TO]->(d);

// ============================================
// VERIFICATION QUERIES
// ============================================

// Count nodes by type
MATCH (n) 
RETURN labels(n)[0] as NodeType, count(n) as Count 
ORDER BY NodeType;

// Show relationships
MATCH (p:PLCProgram)-[r]->(n)
RETURN p.name as Program, type(r) as Relationship, labels(n)[0] as TargetType, n.name as TargetName;

// Find all AOIs used by routines
MATCH (r:Routine)-[:USES]->(a:AOI)
RETURN r.name as Routine, a.name as AOI, a.description as Description; 