# Seed Directory

This directory is for storing initial Neo4j database backups that will be restored when the stack starts up.

## Usage

1. Place your Neo4j backup file here named `neo4j.backup`
2. The init script will automatically restore it when starting the stack
3. If no backup is found, Neo4j will start with an empty database

## Creating a Backup

To create a backup from an existing Neo4j instance:

```bash
docker exec plc-neo4j neo4j-admin backup \
  --database=neo4j \
  --to=/seed/neo4j.backup
```

## Note

The backup file should be compatible with Neo4j 5 Enterprise edition. 