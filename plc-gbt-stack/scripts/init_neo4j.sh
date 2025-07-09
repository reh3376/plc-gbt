#!/bin/bash
# init_neo4j.sh - Initialize Neo4j with seed backup
# This script restores the initial knowledge graph from a backup file

set -e

echo "🚀 Neo4j Initialization Script"
echo "=============================="

# Configuration
NEO4J_CONTAINER="neo4j"
BACKUP_PATH="/seed/neo4j.backup"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-defaultpassword}"

# Check if backup file exists
if [ ! -f "../seed/neo4j.backup" ]; then
    echo "⚠️  Warning: No backup file found at ../seed/neo4j.backup"
    echo "   Skipping restore - Neo4j will start with empty database"
    echo "   Place your initial Neo4j backup in the seed directory to restore it"
    exit 0
fi

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
until docker exec $NEO4J_CONTAINER cypher-shell -u $NEO4J_USER -p $NEO4J_PASSWORD "RETURN 1" >/dev/null 2>&1; do
    sleep 2
done
echo "✅ Neo4j is ready"

# Stop Neo4j for restore
echo "🛑 Stopping Neo4j for backup restore..."
docker exec $NEO4J_CONTAINER neo4j stop

# Restore backup
echo "📦 Restoring backup..."
docker exec $NEO4J_CONTAINER neo4j-admin restore \
    --from=$BACKUP_PATH \
    --database=neo4j \
    --force

# Start Neo4j
echo "🚀 Starting Neo4j..."
docker exec $NEO4J_CONTAINER neo4j start

# Wait for Neo4j to be ready again
echo "⏳ Waiting for Neo4j to restart..."
sleep 10
until docker exec $NEO4J_CONTAINER cypher-shell -u $NEO4J_USER -p $NEO4J_PASSWORD "RETURN 1" >/dev/null 2>&1; do
    sleep 2
done

echo "✅ Neo4j initialization complete!"
echo ""
echo "You can now access Neo4j at http://localhost:7474"
echo "Username: $NEO4J_USER"
echo "Password: [from .env file]" 