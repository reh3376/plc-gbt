# Phase 3 Quick Reference Card

## 🚀 Day 1 Quick Start

```bash
# Start Docker services
cd /Users/reh3376/repos/PLC_GPT/plc-gpt-stack
docker-compose up -d neo4j qdrant

# Activate Python environment
source .venv/bin/activate

# Test connections
python -c "from neo4j import GraphDatabase; print('Neo4j OK')"
python -c "from qdrant_client import QdrantClient; print('Qdrant OK')"
```

## 📁 Key Files to Create/Modify

### New Files (Priority Order)
1. `scripts/neo4j/init_neo4j_schema.py` - Schema creation
2. `scripts/vector/init_vector_store.py` - Qdrant setup
3. `workers/etl_coordinator.py` - Pipeline orchestration
4. `scripts/etl/run_etl_pipeline.py` - Main ETL runner

### Existing Files to Enhance
1. `workers/etl_transformer.py` - Add Neo4j/Qdrant integration
2. `workers/etl_loader.py` - Add batch loading logic
3. `workers/document_parser.py` - Already good, minor tweaks

## 🔧 Core Neo4j Schema

```cypher
// Day 1: Create these first
CREATE CONSTRAINT plc_program_id ON (p:PLCProgram) ASSERT p.id IS UNIQUE;
CREATE CONSTRAINT routine_id ON (r:Routine) ASSERT r.id IS UNIQUE;
CREATE CONSTRAINT aoi_id ON (a:AOI) ASSERT a.id IS UNIQUE;

// Day 2: Add these
CREATE CONSTRAINT udt_id ON (u:UDT) ASSERT u.id IS UNIQUE;
CREATE CONSTRAINT tag_id ON (t:Tag) ASSERT t.id IS UNIQUE;
CREATE CONSTRAINT device_id ON (d:Device) ASSERT d.id IS UNIQUE;
```

## 🎯 Critical Decisions

### Day 1 Decisions
- **Embedding Model**: `text-embedding-3-large` (3072 dims) ✅
- **Vector Collection Name**: `plc_embeddings`
- **Neo4j Database**: Default `neo4j` database
- **Batch Size**: Start with 100, tune based on performance

### Day 2 Decisions  
- **UUID Strategy**: Use Python `uuid.uuid4()` for all IDs
- **Chunking Strategy**: 
  - Routines: One embedding per routine
  - AOIs: One embedding per AOI
  - Documents: Chunk at 1000 tokens
- **Relationship Creation**: Create during transform phase

## 📊 Test Commands

```bash
# Test Neo4j schema
python scripts/neo4j/validate_schema.py

# Test single file processing
python scripts/etl/run_etl_pipeline.py \
  --input plc-format-converter/tests/test_data/sample_controller.L5X \
  --test-mode

# Test vector search
python scripts/vector/test_similarity.py \
  --query "motor control AOI"

# Full integration test
python scripts/etl/validate_pipeline.py --comprehensive
```

## 🔗 Key Connection Strings

```python
# Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password-here")

# Qdrant
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# OpenAI (for embeddings)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

## ⚠️ Common Pitfalls to Avoid

1. **Don't forget indexes** - Create them BEFORE loading data
2. **Batch your operations** - Neo4j and Qdrant perform better with batches
3. **Handle duplicates** - Use MERGE instead of CREATE for idempotency
4. **Monitor memory** - Large files can OOM, implement streaming
5. **Test incrementally** - Don't wait until everything is built

## 📈 Performance Targets

- **Single L5X file**: < 10 seconds end-to-end
- **Neo4j query**: < 100ms for basic traversal
- **Vector search**: < 200ms for top-10 results
- **Memory usage**: < 1GB for typical file

## 🛠️ Debugging Tips

```bash
# Check Neo4j logs
docker logs plc-gpt-stack_neo4j_1

# Monitor Qdrant
curl http://localhost:6333/collections

# Test embeddings
python -c "import openai; openai.embeddings.create(
  model='text-embedding-3-large', 
  input='test'
)"

# Profile memory usage
pip install memory-profiler
python -m memory_profiler scripts/etl/run_etl_pipeline.py
```

## 📋 Daily Checklist

### Day 1 ✓
- [ ] Neo4j connection working
- [ ] Basic schema created (3 nodes)
- [ ] Qdrant collection created
- [ ] Sample embedding generated
- [ ] Basic ETL flow tested

### Day 2 ✓
- [ ] Process sample L5X successfully
- [ ] Verify nodes in Neo4j browser
- [ ] Verify vectors in Qdrant
- [ ] Basic query returns results

### Day 3 ✓
- [ ] All node types created
- [ ] All relationships working
- [ ] Multiple files processed
- [ ] No orphaned nodes

## 🎉 Success Indicators

- Neo4j browser shows connected graph
- Qdrant dashboard shows vectors
- Can answer: "What AOIs are in MainProgram?"
- No errors in Docker logs
- Tests passing with >90% coverage

---

**Remember**: Start simple, test often, iterate quickly! 