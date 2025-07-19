This n8n-roadmap provides a general outline of adding n8n workflow functionality to the plc-gbt application.  Use our existing project infrastructure to implement this new functionality. The purpose of this new functionality is to allow users to create no-code workflows within the plc-gbt application which will pair with the fine-tuned openAI llm.  Allowing users to instantiate workflows using natural language.
 
Phase 0 – Baseline check
      1.         Update images and Docker Desktop to the latest stable (>= 4.31).
      2.         Verify port availability on host (5432, 7687, 6379, 6333, 5678).
      3.         Confirm memory & CPU headroom: n8n + worker in queue-mode adds ≈ 300 MiB RAM and ~1 vCPU under load.
 
⸻
 
Phase 0B – Schema / namespace isolation (NEW)
 
Goal: give n8n its own playground so it never collides with your existing “plc-memory” data.  Run these once before bringing the container up.
 
Engine
Command(s)
What it does
Tell n8n
Postgres 15
sql CREATE SCHEMA IF NOT EXISTS n8n AUTHORIZATION postgres;
Creates schema n8n in the existing DB
Set DB_POSTGRESDB_SCHEMA=n8n  &
Neo4j ≥ 5.x
Connect to the system DB over Cypher Shell and run:cypher CREATE DATABASE n8n IF NOT EXISTS WAIT;
Spins up an isolated Neo4j database called n8n
Provide the DB name in each Neo4j credential you create inside n8n.
Redis 7
In redis-cli  ➜  CONFIG SET databases 16 (if not already) then reserve DB 2:bash SELECT 2; FLUSHDB;
Keeps Bull queue keys out of DB 0
QUEUE_BULL_REDIS_DB=2 together with an optional QUEUE_BULL_PREFIX=n8n_
Qdrant 1.14
bash curl -X PUT localhost:6333/collections/n8n_memory \   -H 'Content-Type: application/json' \   -d '{ "vectors": { "size": 1024, "distance": "Cosine" } }'
Creates collection n8n_memory dedicated to n8n vector work
Point your Qdrant node credentials in n8n to n8n_memory.
 
Why bother? If someone truncates plc-memory tables or re-indexes Neo4j for AI-agent work, you won’t brick your automation platform.  
 
Phase 1 – Extend docker-compose.yml
 
version: '3.9'
 
services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      # --- Postgres ---
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres           # your existing service name
      DB_POSTGRESDB_PORT: 5432
      DB_POSTGRESDB_DATABASE: whk_data       # existing DB
      DB_POSTGRESDB_SCHEMA: n8n              # 👈 NEW
      DB_POSTGRESDB_USER: postgres
      DB_POSTGRESDB_PASSWORD: ${PG_PASSWORD}
      # --- Redis queue ---
      EXECUTIONS_MODE: queue
      QUEUE_BULL_REDIS_HOST: redis
      QUEUE_BULL_REDIS_PORT: 6379
      QUEUE_BULL_REDIS_DB: 2                 # 👈 NEW
      QUEUE_BULL_PREFIX: n8n_                # (optional)
      # --- Misc ---
      N8N_DISABLE_PRODUCTION_MAIN_PROCESS: "false"
      GENERIC_TIMEZONE: America/Kentucky/Louisville
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - ai_net
    depends_on:
      - postgres
      - redis
 
  # Existing services trimmed for brevity...
  postgres:
    # ...
  redis:
    # ...
  neo4j:
    # ...
  qdrant:
    # ...
 
networks:
  ai_net:
 
volumes:
  n8n_data:
 
Phase 2 – Wire n8n into the plc-memory stack
 
Create credentials inside n8n for Postgres, Neo4j, Redis, and Qdrant using the new namespaces above.
   2.         Expose the plc-memory workflow as an n8n Sub-Workflow or via Webhook so n8n can call it as needed.
   3.         Use variables not hard-coded connection strings. (Safe: process.env.PLC_PG_CONN etc.)
 
 
Phase 3 – Dry-run & smoke tests
Check
Pass criteria
n8n UI reachable
http://localhost:5678 loads, login works
Migrations
n8n schema in Postgres now contains ~25 tables
Queue mode
Worker logs show BullMQ connected to redis://…/2
Neo4j access
:use n8n returns empty graph (as expected)
Qdrant
GET /collections shows n8n_memory alongside existing ones
 
Phase 4 – Ops hardening
   •          Back-ups: include Postgres schema n8n, Neo4j DB n8n, Redis DB 2 RDB/AOF files, and Qdrant snapshots.
   •          Monitoring: hook n8n’s /metrics endpoint into Prometheus.
   •          Secrets: move database passwords out of compose into Docker secrets or Vault.
 
⸻
 
Phase 5 – Future upgrades
   •          Horizontal scaling: add more n8n workers; just share the same DBs & Redis DB 2.
   •          High-availability: promote Redis to a small cluster; mirror Postgres.
   •          Git-backed workflows: n8n 1.9+ supports native Git; store flows in version control.
 
⸻
 
Immediate next step
 
Run the Phase 0B commands, update your docker-compose.yml, and start the stack with docker compose up -d.  You’ll have n8n isolated, version-controlled, and ready to integrate with your AI coding agent without stepping on the plc-memory data.