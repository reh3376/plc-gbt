# Database Backups

This directory contains backups of all databases used in the PLC-Savvy GPT system.

## Directory Structure

```
backup/
├── neo4j/          # Neo4j Knowledge Graph backups
├── postgres/       # PostgreSQL metadata database backups
├── qdrant/         # Qdrant vector database backups
└── README.md       # This file
```

## Backup Details

### Neo4j Backups (`neo4j/`)
- **Location**: `backup/neo4j/dumps/`
- **Format**: `.backup` files created by `neo4j-admin database backup`
- **Current Backup**: `neo4j-2025-07-01T15-26-41.backup`
- **Content**: Complete Neo4j knowledge graph including all nodes and relationships
- **Size**: ~5KB (initial empty database)

### PostgreSQL Backups (`postgres/`)
- **Location**: `backup/postgres/`
- **Format**: SQL dump files created by `pg_dump`
- **Current Backup**: `plc_metadata_backup_2025-07-01_11-27-27.sql`
- **Content**: Complete metadata database dump including schema and data
- **Database**: `plc_metadata`
- **User**: `plc_user`
- **Size**: ~491 bytes (initial empty database)

### Qdrant Backups (`qdrant/`)
- **Location**: `backup/qdrant/`
- **Format**: JSON collection listings and configuration exports
- **Current Backup**: `collections_empty_2025-07-01_11-27-36.txt`
- **Content**: Vector database collections (currently empty)
- **Status**: No collections created yet

## Backup Creation Commands

### Neo4j
```bash
# Create backup directory inside container
docker exec plc-neo4j mkdir -p /var/lib/neo4j/dumps

# Create backup
docker exec plc-neo4j neo4j-admin database backup --to-path=/var/lib/neo4j/dumps/ neo4j

# Copy to local backup directory
docker cp plc-neo4j:/var/lib/neo4j/dumps/ ./backup/neo4j/
```

### PostgreSQL
```bash
# Create backup
docker exec plc-postgres pg_dump -U plc_user plc_metadata > ./backup/postgres/plc_metadata_backup_$(date +%Y-%m-%d_%H-%M-%S).sql
```

### Qdrant
```bash
# List collections (currently empty)
curl -X POST "http://localhost:6333/collections" | jq . > ./backup/qdrant/collections_list_$(date +%Y-%m-%d_%H-%M-%S).json
```

## Restore Procedures

### Neo4j Restore
```bash
# Stop Neo4j service
docker-compose stop neo4j

# Copy backup to container
docker cp ./backup/neo4j/dumps/neo4j-[timestamp].backup plc-neo4j:/var/lib/neo4j/dumps/

# Restore database (requires stopped service)
docker exec plc-neo4j neo4j-admin database load --from-path=/var/lib/neo4j/dumps/ neo4j

# Start Neo4j service
docker-compose start neo4j
```

### PostgreSQL Restore
```bash
# Restore database
docker exec -i plc-postgres psql -U plc_user plc_metadata < ./backup/postgres/plc_metadata_backup_[timestamp].sql
```

### Qdrant Restore
```bash
# Qdrant collections will be restored when ETL pipeline creates and populates them
# Current backup serves as a baseline configuration snapshot
```

## Backup Schedule Recommendations

- **Neo4j**: Daily incremental backups, weekly full backups
- **PostgreSQL**: Daily backups of metadata
- **Qdrant**: Backup after significant vector data updates

## Notes

- All databases are currently in their initial state (empty/minimal data)
- Backup sizes will grow significantly as the system processes PLC documentation
- Consider implementing automated backup scripts for production use
- Backup files include timestamps for version tracking

---

**Created**: July 1, 2025  
**Last Updated**: July 1, 2025  
**System Status**: Phase 1 Complete - Infrastructure Setup 