#!/bin/bash
# Test database connectivity from within the development container

echo "==================================="
echo "PLC-GBT Database Connectivity Test"
echo "==================================="
echo ""

# Redis Test
echo "1. Testing Redis..."
redis-cli -h redis ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Redis connected successfully"
    echo "   Host: redis:6379"
else
    echo "   ❌ Redis connection failed"
fi
echo ""

# PostgreSQL Test
echo "2. Testing PostgreSQL..."
PGPASSWORD=${POSTGRES_PASSWORD:-password} psql -h postgres -U ${POSTGRES_USER:-plc_user} -d ${POSTGRES_DB:-plc_metadata} -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ PostgreSQL connected successfully"
    echo "   Host: postgres:5432"
    echo "   Database: ${POSTGRES_DB:-plc_metadata}"
else
    echo "   ❌ PostgreSQL connection failed"
fi
echo ""

# Neo4j Test
echo "3. Testing Neo4j..."
curl -s http://neo4j:7474 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Neo4j HTTP connected successfully"
    echo "   HTTP: http://neo4j:7474"
    echo "   Bolt: bolt://neo4j:7687"
else
    echo "   ❌ Neo4j connection failed"
fi
echo ""

# Qdrant Test
echo "4. Testing Qdrant..."
curl -s http://qdrant:6333/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Qdrant connected successfully"
    echo "   Host: http://qdrant:6333"
else
    echo "   ❌ Qdrant connection failed"
fi
echo ""

echo "==================================="
echo "Connection strings for development:"
echo "==================================="
echo "Redis:      redis://redis:6379"
echo "PostgreSQL: postgresql://plc_user:password@postgres:5432/plc_metadata"
echo "Neo4j:      bolt://neo4j:password@neo4j:7687"
echo "Qdrant:     http://qdrant:6333"
echo "====================================" 