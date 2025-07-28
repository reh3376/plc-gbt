# PLC-GBT Phase 32 Containerized Development Environment

This containerized development environment provides full access to all PLC-GBT databases and tools, bypassing Docker Desktop port forwarding issues on macOS.

## Quick Start

1. **Start the development container:**

   ```bash
   cd plc-gbt-stack/integration
   docker-compose -f docker-compose.dev.yml run --rm plc-dev
   ```

2. **Test database connectivity (inside container):**

   ```bash
   ./test-db-connectivity.sh
   # or simply:
   test-db
   ```

3. **Access databases directly:**

   ```bash
   # Redis
   redis-cli -h redis

   # PostgreSQL
   psql -h postgres -U plc_user -d plc_metadata

   # Neo4j via cypher-shell
   cypher-shell -a bolt://neo4j:7687 -u neo4j -p password

   # Qdrant via curl
   curl http://qdrant:6333/collections
   ```

## Database Connection Strings

Use these connection strings in your Phase 32 development:

- **Redis**: `redis://redis:6379`
- **PostgreSQL**: `postgresql://plc_user:password@postgres:5432/plc_metadata`
- **Neo4j**: `bolt://neo4j:password@neo4j:7687`
- **Qdrant**: `http://qdrant:6333`

## Available Tools

The container includes all necessary development tools:

### Python Development

- Python 3.11 with all PLC-GBT dependencies
- FastAPI, WebSockets, GraphQL libraries
- Database clients (redis, neo4j, psycopg2, qdrant-client)
- Testing tools (pytest, pytest-asyncio)
- Code quality tools (black, ruff)

### TypeScript Development

- Node.js 20.x
- TypeScript 5.3.3
- ts-node for direct execution
- nodemon for auto-reloading

### System Tools

- Git, vim, nano
- PostgreSQL client tools
- Redis CLI
- Network debugging tools (netcat, ping, dig)

## Helpful Aliases

Inside the container, these aliases are available:

- `ll` - List files with details
- `test-db` - Run database connectivity test
- `plc-memory` - Access PLC Memory CLI
- `plc-cl` - Access main PLC CLI

## Development Workflow

1. **Edit files on host**: Your entire project is mounted at `/workspace`
2. **Run services in container**: All database connections work seamlessly
3. **Test Phase 32 components**: WebSocket servers, GraphQL endpoints, etc.

## Running Phase 32 Services

### WebSocket Server (example)

```bash
cd /workspace/plc-gbt-stack/integration/websocket
python websocket_server.py
```

### GraphQL Server (example)

```bash
cd /workspace/plc-gbt-stack/integration/graphql
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Persisting Work

All changes made to files under `/workspace` are automatically persisted to your host machine. The container can be stopped and restarted without losing work.

## Troubleshooting

### Container won't start

Ensure database services are running:

```bash
cd ../  # Go to plc-gbt-stack directory
docker-compose ps
docker-compose up -d redis neo4j postgres qdrant
```

### Database connection errors

Run the connectivity test:

```bash
./test-db-connectivity.sh
```

### Port conflicts

The development container doesn't expose any ports by default. To expose a service port:

```bash
docker-compose -f docker-compose.dev.yml run --rm -p 8001:8001 plc-dev
```

## Next Steps for Phase 32.1

With the containerized environment ready, you can now:

1. Implement WebSocket real-time communication server
2. Create GraphQL schema and resolvers
3. Build data synchronization engine
4. Develop resilience patterns

All database connections work seamlessly within this environment!
