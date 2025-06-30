# PLC‑Savvy GPT Deployment Handbook

> **Purpose**  
> This handbook merges the *Roadmap: Building a PLC‑Savvy GPT with Neo4j KG* and the *Implementation Guide: Deploying a PLC‑Savvy GPT in ChatGPT Enterprise* into one logically ordered reference.  It walks from high‑level concepts to concrete scripts, organized as **Phases** with actionable tasks.

---

## Phase 0 – Conceptual Overview

### 0.1 High‑Level Architecture
```
┌────────────┐     ingest          ┌─────────────┐
│  PDFs, L5X │ ───────────────▶   │ ETL + Embed │──┐
└────────────┘  (Python workers)  └─────────────┘  │
                                                   ▼
                                ┌────────────────────────────┐
     user prompt ───▶ Gateway ─▶│  Neo4j KG  +  Vector DB    │◀─┐ backups
                                └────────────────────────────┘  │
                                          ▲                     │
                                          │Cypher + similarity  │incremental
                     fine‑tuned GPT ◀─────┘                     │
                                          ▲                     │
                               master KG in data‑center ◀───────┘
```

**Key components**

| Layer | Role |
|-------|------|
| PDF/L5X corpus | Source of domain knowledge |
| ETL + Embed | Parse docs, extract entities, create embeddings |
| Neo4j Knowledge‑Graph | Structured relationships & incremental backups |
| Vector Store (Qdrant/LanceDB/pgvector) | Fast semantic search |
| Gateway (FastAPI) | Combines KG + vectors, exposes OpenAPI |
| Fine‑tuned GPT‑4‑turbo / o3 | Generates answers with RAG context |
| Master KG | Aggregates incremental backups from field nodes | fileciteturn2file1

---

## Phase 1 – Environment & Tooling

| Need | Recommended stack |
|------|-------------------|
| LLM | `gpt‑4‑turbo` or **o3‑turbo** |
| Graph DB | **Neo4j 5 Enterprise** in Docker |
| Vector store | Qdrant, LanceDB, or pgvector |
| Orchestrator | Docker Compose (local), Swarm/K8s optional |
| ETL | Python 3.12, `langchain‑community`, `neo4j‑python‑driver` |
| Backups | `neo4j-admin` (**--prefer-diff-as-parent**) | fileciteturn2file1

### Tasks
1. Install Docker & Docker Compose.
2. Clone/unpack `plc-gpt-stack`.
3. Copy initial Neo4j backup into `/seed`.
4. Populate `.env` with passwords & keys.

```bash
cd plc-gpt-stack
cp .env.example .env
docker compose pull          # or docker load -i images.tar
docker compose up -d         # spins neo4j, qdrant, etl, gateway
./scripts/init_neo4j.sh      # restores seed DB
```

Gateway boots at `https://gateway.local/api/v1/query`. fileciteturn2file0

---

## Phase 2 – OpenAI Enterprise Configuration

| Setting | Location | Action |
|---------|----------|--------|
| **Domain allow‑list** | Admin → Settings → GPTs & Plugins | Add `gateway.yourcorp.com` |
| **Model visibility** | Admin → Usage & Billing | Verify `ft:gpt‑4‑turbo:plc‑2025‑06` |
| **Secret storage** | Workspace Secrets Vault | Save `GATEWAY_BEARER` token | fileciteturn2file0

---

## Phase 3 – Knowledge‑Graph & Vector Pipeline

### 3.1 KG Schema (Cypher DL)

| Node | Properties | Relationships |
|------|------------|---------------|
| `PLCProgram` | `name, firmware, project` | **CONTAINS** → `Routine`, `UDT`, `AOI` |
| `Routine` | `name, language, file_path` | **USES** → `AOI`; **IN_PROGRAM** → `PLCProgram` |
| `AOI` | `name, rev, desc` | **USES_UDT** → `UDT` |
| `UDT` | `name, size, desc` | — |
| `SpecDoc` | `title, doc_type, version` | **COVERS** → any |
| `QuestionAnswer` | `question, answer, embedding_id` | **DERIVED_FROM** → `SpecDoc` | fileciteturn2file1

### 3.2 ETL Workflow
1. **Extract** – `pdfplumber`, `lxml` parse PDFs/L5X.
2. **Transform** – detect entities, tag UUIDs, generate embeddings with `text-embedding-3-large`.
3. **Load** – bulk import via `cypher-shell`.

---

## Phase 4 – Fine‑Tuning & Retrieval‑Augmented Generation

### 4.1 Fine‑Tune
```bash
openai tools fine_tunes.create   -m o3-turbo   -t plc_train.jsonl
```
*Target*: 300–1 000 gold Q‑A pairs.

### 4.2 Query Flow
1. Vector similarity search (`k=6`).
2. Cypher neighborhood query for related nodes.
3. Assemble prompt sections:
   *Vector context* + *Graph context* + *User question*.
4. Call fine‑tuned model.

---

## Phase 5 – GPT Construction with Actions

### 5.1 OpenAPI Spec (excerpt)
```yaml
openapi: 3.1.0
info: { title: PLC-KG Gateway, version: "1.0.0" }
paths:
  /query:
    post:
      operationId: queryKnowledge
      security: [{ bearerAuth: [] }]
      ...
```

### 5.2 Build Steps
1. **Explore → Create a GPT**.  
2. **Instructions** – define persona; instruct GPT to call `queryKnowledge` when internal data required.  
3. **Model** – select your fine‑tuned ID.  
4. **Knowledge** – upload seed docs.  
5. **Actions** – paste OpenAPI spec; attach `GATEWAY_BEARER`.  
6. **Publish** – scope to workspace or group. fileciteturn2file0

---

## Phase 6 – Maintenance & Governance

| Task | Frequency | Tool |
|------|-----------|------|
| Fine‑tune refresh | Weekly | CI pipeline calling `openai fine_tunes.create` |
| Vector re‑embed | Nightly | `etl_worker --reindex` |
| Neo4j diff backup | Nightly | `neo4j-admin backup` |
| Push diff to master | Nightly | `rclone` or `rsync` |
| Field pull/restore | 4 h | Gateway auto‑restore script | fileciteturn2file0

### Governance Guard‑Rails
* Mask customer tags during ETL.  
* Neo4j **RBAC** – read‑only user `gpt_kg_ro`.  
* Enforce HTTPS + JWT/Bearer on gateway.  
* Enable ChatGPT Enterprise audit logs. fileciteturn2file0

---

## Phase 7 – Milestone Checklist

| Week | Deliverable |
|------|-------------|
| 1 | KG schema & Docker skeleton finalized |
| 2 | ETL imports seed into Neo4j |
| 3 | Vector DB populated; gateway prototype |
| 4 | First fine‑tune complete |
| 5 | Backup scripts verified |
| 6 | Security hardening & offline installer |
| 7 | Alpha test with Emulate 5570 PLC |
| 8 | Master KG deployed; first field rollout | fileciteturn2file1

---

## Appendix A – Package Structure

```
plc-gpt-stack/
├── docker-compose.yml
├── .env.example
├── /seed/neo4j.backup
├── /scripts/init_neo4j.sh
└── /workers/etl_worker.Dockerfile
```

## Appendix B – Gateway Query Example
```http
POST /api/v1/query
Content-Type: application/json
Authorization: Bearer $GATEWAY_BEARER

{ "question": "Why does Routine REFILL_VALVE use AOI FTR?" }
```
Returns JSON with `vector_context`, `graph_context`, and `citations`.

---

### Next Actions for You

1. Review KG schema names and adjust if needed.  
2. Place project documents into the `incoming` folder for ETL ingestion.  
3. Decide hosting location for master KG (on‑prem vs private cloud).
