# AI Enhancement Framework - Multi-Environment Support Guide

**Version**: 1.0  
**Last Updated**: January 18, 2025  
**Audience**: DevOps Engineers, Team Leaders, Enterprise Users

## 📋 Overview

The AI Enhancement Framework supports multiple deployment environments to accommodate different development workflows, security requirements, and organizational needs. This guide covers setup, configuration, and best practices for development, testing, staging, and production environments.

## 🏗️ Environment Types

### Development Environment
**Purpose**: Local development with fast iteration and debugging capabilities

**Characteristics**:
- Full local Docker stack
- Debug logging enabled
- Hot-reload functionality
- Development-optimized configurations
- Local file system integration

**Resource Requirements**:
- **CPU**: 2+ cores recommended
- **Memory**: 4GB+ available RAM
- **Storage**: 10GB+ available space
- **Network**: Local network access

### Testing Environment
**Purpose**: Automated testing, CI/CD integration, and quality assurance

**Characteristics**:
- Isolated test data and configurations
- Automated test execution
- Performance profiling enabled
- Mock external services
- Disposable infrastructure

**Resource Requirements**:
- **CPU**: 4+ cores for parallel testing
- **Memory**: 8GB+ for test isolation
- **Storage**: 20GB+ for test artifacts
- **Network**: Limited external access

### Staging Environment
**Purpose**: Production-like environment for final validation and user acceptance testing

**Characteristics**:
- Production-mirrored configuration
- Real data volumes (anonymized)
- Performance monitoring
- Security hardening
- Backup and recovery testing

**Resource Requirements**:
- **CPU**: Production-equivalent
- **Memory**: Production-equivalent
- **Storage**: Production-equivalent
- **Network**: Restricted production access

### Production Environment
**Purpose**: Live deployment serving end users with maximum reliability and security

**Characteristics**:
- High availability and redundancy
- Comprehensive monitoring and alerting
- Security hardening and compliance
- Automated backup and disaster recovery
- Performance optimization

**Resource Requirements**:
- **CPU**: 8+ cores with auto-scaling
- **Memory**: 16GB+ with monitoring
- **Storage**: High-performance SSD with backup
- **Network**: Load balancing and CDN

## 🐳 Docker Configurations

### Development Configuration

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data
      - ./dev-configs/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    environment:
      - REDIS_LOG_LEVEL=debug

  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_dev_data:/data
      - ./dev-configs/neo4j:/conf
    environment:
      - NEO4J_AUTH=neo4j/dev-password
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_logs_debug_level=INFO
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=1G

  postgresql:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./dev-configs/init-dev.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      - POSTGRES_DB=ai_enhancement_dev
      - POSTGRES_USER=dev_user
      - POSTGRES_PASSWORD=dev-password
      - POSTGRES_LOG_STATEMENT=all

  qdrant:
    image: qdrant/qdrant:v1.7.4
    ports:
      - "6333:6333"
    volumes:
      - qdrant_dev_data:/qdrant/storage
      - ./dev-configs/qdrant:/qdrant/config
    environment:
      - QDRANT__LOG_LEVEL=DEBUG

volumes:
  redis_dev_data:
  neo4j_dev_data:
  postgres_dev_data:
  qdrant_dev_data:

networks:
  default:
    name: ai-enhancement-dev
```

### Testing Configuration

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    environment:
      - REDIS_LOG_LEVEL=warn
    tmpfs:
      - /data:size=256m

  neo4j:
    image: neo4j:5.15-community
    environment:
      - NEO4J_AUTH=neo4j/test-password
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_memory_heap_max__size=512m
      - NEO4J_dbms_logs_debug_level=WARN
    tmpfs:
      - /data:size=1g

  postgresql:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_enhancement_test
      - POSTGRES_USER=test_user
      - POSTGRES_PASSWORD=test-password
      - POSTGRES_LOG_MIN_MESSAGES=WARNING
    tmpfs:
      - /var/lib/postgresql/data:size=1g

  qdrant:
    image: qdrant/qdrant:v1.7.4
    environment:
      - QDRANT__LOG_LEVEL=WARN
    tmpfs:
      - /qdrant/storage:size=512m

networks:
  default:
    name: ai-enhancement-test
```

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2GB
        reservations:
          memory: 1GB
    volumes:
      - redis_prod_data:/data
      - ./prod-configs/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    environment:
      - REDIS_LOG_LEVEL=notice
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  neo4j:
    image: neo4j:5.15-enterprise
    deploy:
      resources:
        limits:
          memory: 8GB
        reservations:
          memory: 4GB
    volumes:
      - neo4j_prod_data:/data
      - neo4j_prod_logs:/logs
      - ./prod-configs/neo4j:/conf
    environment:
      - NEO4J_AUTH=neo4j/$(cat /run/secrets/neo4j_password)
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_PLUGINS=["apoc", "graph-data-science"]
      - NEO4J_dbms_memory_heap_max__size=4G
    secrets:
      - neo4j_password
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "$(cat /run/secrets/neo4j_password)", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgresql:
    image: postgres:15
    deploy:
      resources:
        limits:
          memory: 4GB
        reservations:
          memory: 2GB
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - postgres_prod_backup:/backup
      - ./prod-configs/postgresql.conf:/etc/postgresql/postgresql.conf
    environment:
      - POSTGRES_DB=ai_enhancement_prod
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
    secrets:
      - postgres_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U prod_user -d ai_enhancement_prod"]
      interval: 30s
      timeout: 5s
      retries: 3

  qdrant:
    image: qdrant/qdrant:v1.7.4
    deploy:
      resources:
        limits:
          memory: 4GB
        reservations:
          memory: 2GB
    volumes:
      - qdrant_prod_data:/qdrant/storage
      - ./prod-configs/qdrant:/qdrant/config
    environment:
      - QDRANT__LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  redis_prod_data:
  neo4j_prod_data:
  neo4j_prod_logs:
  postgres_prod_data:
  postgres_prod_backup:
  qdrant_prod_data:

secrets:
  neo4j_password:
    external: true
  postgres_password:
    external: true

networks:
  default:
    name: ai-enhancement-prod
    driver: overlay
    encrypted: true
```

## ⚙️ Environment Configuration

### Environment Variables

```bash
# .env.development
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DEBUG=true
REDIS_URL=redis://localhost:6379/0
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dev-password
POSTGRES_URL=postgresql://dev_user:dev-password@localhost:5432/ai_enhancement_dev
QDRANT_URL=http://localhost:6333
AI_TASK_ORCHESTRATOR_COMPLEXITY=moderate
MEMORY_CACHE_TTL=300
PERFORMANCE_MONITORING=false
```

```bash
# .env.testing
ENVIRONMENT=testing
LOG_LEVEL=INFO
DEBUG=false
REDIS_URL=redis://localhost:6379/1
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=test-password
POSTGRES_URL=postgresql://test_user:test-password@localhost:5432/ai_enhancement_test
QDRANT_URL=http://localhost:6333
AI_TASK_ORCHESTRATOR_COMPLEXITY=simple
MEMORY_CACHE_TTL=60
PERFORMANCE_MONITORING=true
TESTING_MODE=true
```

```bash
# .env.production
ENVIRONMENT=production
LOG_LEVEL=WARN
DEBUG=false
REDIS_URL=redis://redis-cluster:6379/0
NEO4J_URL=bolt://neo4j-cluster:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD_FILE=/run/secrets/neo4j_password
POSTGRES_URL=postgresql://prod_user@postgres-cluster:5432/ai_enhancement_prod
QDRANT_URL=http://qdrant-cluster:6333
AI_TASK_ORCHESTRATOR_COMPLEXITY=complex
MEMORY_CACHE_TTL=3600
PERFORMANCE_MONITORING=true
SECURITY_HARDENING=true
BACKUP_ENABLED=true
```

### Configuration Management

```python
# config/environment_config.py
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    redis_url: str
    neo4j_url: str
    neo4j_user: str
    neo4j_password: str
    postgres_url: str
    qdrant_url: str

@dataclass
class AIConfig:
    default_complexity: str
    memory_cache_ttl: int
    performance_monitoring: bool
    debugging_enabled: bool

@dataclass
class SecurityConfig:
    security_hardening: bool
    encryption_enabled: bool
    audit_logging: bool
    backup_enabled: bool

@dataclass
class EnvironmentConfig:
    environment: Environment
    log_level: str
    debug: bool
    database: DatabaseConfig
    ai: AIConfig
    security: SecurityConfig

def load_environment_config() -> EnvironmentConfig:
    """Load configuration based on current environment"""
    env = Environment(os.getenv('ENVIRONMENT', 'development'))
    
    database_config = DatabaseConfig(
        redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        neo4j_url=os.getenv('NEO4J_URL', 'bolt://localhost:7687'),
        neo4j_user=os.getenv('NEO4J_USER', 'neo4j'),
        neo4j_password=os.getenv('NEO4J_PASSWORD', 'ai-enhancement'),
        postgres_url=os.getenv('POSTGRES_URL', 'postgresql://ai_user:ai_enhancement@localhost:5432/ai_enhancement'),
        qdrant_url=os.getenv('QDRANT_URL', 'http://localhost:6333')
    )
    
    ai_config = AIConfig(
        default_complexity=os.getenv('AI_TASK_ORCHESTRATOR_COMPLEXITY', 'moderate'),
        memory_cache_ttl=int(os.getenv('MEMORY_CACHE_TTL', '1800')),
        performance_monitoring=os.getenv('PERFORMANCE_MONITORING', 'false').lower() == 'true',
        debugging_enabled=os.getenv('DEBUG', 'false').lower() == 'true'
    )
    
    security_config = SecurityConfig(
        security_hardening=os.getenv('SECURITY_HARDENING', 'false').lower() == 'true',
        encryption_enabled=os.getenv('ENCRYPTION_ENABLED', 'true').lower() == 'true',
        audit_logging=os.getenv('AUDIT_LOGGING', 'false').lower() == 'true',
        backup_enabled=os.getenv('BACKUP_ENABLED', 'false').lower() == 'true'
    )
    
    return EnvironmentConfig(
        environment=env,
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        debug=os.getenv('DEBUG', 'false').lower() == 'true',
        database=database_config,
        ai=ai_config,
        security=security_config
    )
```

## 🚀 Deployment Strategies

### Development Deployment

```bash
# Development setup script
#!/bin/bash
set -e

echo "Setting up AI Enhancement Framework for development..."

# Create development directories
mkdir -p dev-configs/{redis,neo4j,postgresql,qdrant}
mkdir -p dev-data/{logs,backups}

# Copy development configurations
cp configs/dev/* dev-configs/

# Set development environment
export ENVIRONMENT=development
cp .env.development .env

# Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for services to be ready
./scripts/wait-for-services.sh

# Initialize development data
python scripts/init-dev-data.py

echo "Development environment ready!"
echo "Access services at:"
echo "  Redis: localhost:6379"
echo "  Neo4j: http://localhost:7474"
echo "  PostgreSQL: localhost:5432"
echo "  Qdrant: http://localhost:6333"
```

### Production Deployment

```bash
# Production deployment script
#!/bin/bash
set -e

echo "Deploying AI Enhancement Framework to production..."

# Validate production environment
./scripts/validate-production-env.sh

# Create production secrets
docker secret create neo4j_password neo4j_password.txt
docker secret create postgres_password postgres_password.txt

# Deploy production stack
docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml ai-enhancement

# Wait for stack to be ready
./scripts/wait-for-stack.sh ai-enhancement

# Run health checks
./scripts/production-health-check.sh

# Initialize production monitoring
./scripts/setup-monitoring.sh

echo "Production deployment complete!"
```

## 📊 Environment Monitoring

### Health Check Scripts

```python
# scripts/health_check.py
import asyncio
import aiohttp
import asyncpg
import redis.asyncio as redis
from neo4j import AsyncGraphDatabase
import sys

async def check_redis_health(redis_url: str) -> bool:
    """Check Redis service health"""
    try:
        r = redis.from_url(redis_url, decode_responses=True)
        await r.ping()
        await r.close()
        return True
    except Exception as e:
        print(f"Redis health check failed: {e}")
        return False

async def check_neo4j_health(neo4j_url: str, user: str, password: str) -> bool:
    """Check Neo4j service health"""
    try:
        driver = AsyncGraphDatabase.driver(neo4j_url, auth=(user, password))
        async with driver.session() as session:
            result = await session.run("RETURN 1 as test")
            await result.single()
        await driver.close()
        return True
    except Exception as e:
        print(f"Neo4j health check failed: {e}")
        return False

async def check_postgresql_health(postgres_url: str) -> bool:
    """Check PostgreSQL service health"""
    try:
        conn = await asyncpg.connect(postgres_url)
        await conn.execute('SELECT 1')
        await conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL health check failed: {e}")
        return False

async def check_qdrant_health(qdrant_url: str) -> bool:
    """Check Qdrant service health"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{qdrant_url}/health') as response:
                return response.status == 200
    except Exception as e:
        print(f"Qdrant health check failed: {e}")
        return False

async def main():
    """Run comprehensive health checks"""
    config = load_environment_config()
    
    health_checks = [
        ("Redis", check_redis_health(config.database.redis_url)),
        ("Neo4j", check_neo4j_health(config.database.neo4j_url, config.database.neo4j_user, config.database.neo4j_password)),
        ("PostgreSQL", check_postgresql_health(config.database.postgres_url)),
        ("Qdrant", check_qdrant_health(config.database.qdrant_url))
    ]
    
    results = await asyncio.gather(*[check for _, check in health_checks], return_exceptions=True)
    
    all_healthy = True
    for (service, _), result in zip(health_checks, results):
        if isinstance(result, Exception) or not result:
            print(f"❌ {service}: UNHEALTHY")
            all_healthy = False
        else:
            print(f"✅ {service}: HEALTHY")
    
    if all_healthy:
        print("\n🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("\n⚠️  Some services are unhealthy!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### Performance Monitoring

```python
# monitoring/environment_monitor.py
import asyncio
import psutil
import docker
from dataclasses import dataclass
from typing import Dict, List
import json
import time

@dataclass
class ServiceMetrics:
    cpu_percent: float
    memory_usage_mb: float
    memory_percent: float
    network_io: Dict[str, int]
    disk_io: Dict[str, int]
    uptime_seconds: float

class EnvironmentMonitor:
    """Monitor environment-specific performance metrics"""
    
    def __init__(self, environment: Environment):
        self.environment = environment
        self.client = docker.from_env()
        self.service_names = {
            'redis': f'ai-enhancement-redis-{environment.value}',
            'neo4j': f'ai-enhancement-neo4j-{environment.value}',
            'postgresql': f'ai-enhancement-postgres-{environment.value}',
            'qdrant': f'ai-enhancement-qdrant-{environment.value}'
        }
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get overall system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        }
    
    def get_service_metrics(self, service: str) -> ServiceMetrics:
        """Get metrics for a specific service"""
        try:
            container = self.client.containers.get(self.service_names[service])
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_percent = self._calculate_cpu_percent(stats)
            
            # Calculate memory usage
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100
            
            # Get uptime
            uptime = time.time() - container.attrs['State']['StartedAt']
            
            return ServiceMetrics(
                cpu_percent=cpu_percent,
                memory_usage_mb=memory_usage / (1024 * 1024),
                memory_percent=memory_percent,
                network_io=stats['networks'],
                disk_io=stats['blkio_stats'],
                uptime_seconds=uptime
            )
            
        except Exception as e:
            raise Exception(f"Failed to get metrics for {service}: {str(e)}")
    
    def _calculate_cpu_percent(self, stats: dict) -> float:
        """Calculate CPU percentage from Docker stats"""
        cpu_stats = stats['cpu_stats']
        precpu_stats = stats['precpu_stats']
        
        cpu_delta = cpu_stats['cpu_usage']['total_usage'] - precpu_stats['cpu_usage']['total_usage']
        system_delta = cpu_stats['system_cpu_usage'] - precpu_stats['system_cpu_usage']
        
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * len(cpu_stats['cpu_usage']['percpu_usage']) * 100.0
            return round(cpu_percent, 2)
        return 0.0
    
    def generate_environment_report(self) -> Dict:
        """Generate comprehensive environment report"""
        report = {
            'environment': self.environment.value,
            'timestamp': time.time(),
            'system_metrics': self.get_system_metrics(),
            'service_metrics': {}
        }
        
        for service in self.service_names.keys():
            try:
                report['service_metrics'][service] = self.get_service_metrics(service).__dict__
            except Exception as e:
                report['service_metrics'][service] = {'error': str(e)}
        
        return report
```

## 🔧 Environment Switching

### Automated Environment Scripts

```bash
# scripts/switch-environment.sh
#!/bin/bash

ENVIRONMENT=$1
BACKUP_CURRENT=${2:-true}

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 <environment> [backup_current]"
    echo "Environments: development, testing, staging, production"
    exit 1
fi

echo "Switching to $ENVIRONMENT environment..."

# Backup current environment if requested
if [ "$BACKUP_CURRENT" = "true" ]; then
    echo "Backing up current environment..."
    ./scripts/backup-environment.sh
fi

# Stop current services
echo "Stopping current services..."
docker-compose down

# Switch configuration
echo "Switching configuration..."
cp .env.$ENVIRONMENT .env
cp docker-compose.$ENVIRONMENT.yml docker-compose.override.yml

# Start new environment
echo "Starting $ENVIRONMENT services..."
docker-compose up -d

# Wait for services
echo "Waiting for services to be ready..."
./scripts/wait-for-services.sh

# Run environment-specific initialization
if [ -f "scripts/init-$ENVIRONMENT.sh" ]; then
    echo "Running $ENVIRONMENT initialization..."
    ./scripts/init-$ENVIRONMENT.sh
fi

# Validate environment
echo "Validating $ENVIRONMENT environment..."
python scripts/health_check.py

echo "Successfully switched to $ENVIRONMENT environment!"
```

## 📚 Best Practices

### Development Best Practices
1. **Use development-specific databases** to avoid data conflicts
2. **Enable debug logging** for detailed troubleshooting
3. **Use file watchers** for automatic service restart during development
4. **Maintain development data fixtures** for consistent testing
5. **Document environment-specific configurations** for team sharing

### Production Best Practices
1. **Implement comprehensive monitoring** and alerting
2. **Use secrets management** for sensitive configuration
3. **Enable automated backups** with tested restore procedures
4. **Implement blue-green deployments** for zero-downtime updates
5. **Maintain disaster recovery plans** with regular testing

### Security Best Practices
1. **Use environment-specific credentials** that are never shared
2. **Implement network isolation** between environments
3. **Enable encryption in transit and at rest** for production
4. **Regular security audits** and vulnerability assessments
5. **Access control and audit logging** for all environments

## 🎯 Conclusion

Multi-environment support ensures the AI Enhancement Framework can scale from individual development to enterprise production deployments. By following this guide, teams can maintain consistent, secure, and reliable deployments across all stages of the development lifecycle.

---

**For Support**: Create an issue in the [AI Enhancement Framework repository](https://github.com/ai-enhancement/framework/issues)  
**For Updates**: Check the [Environment Configuration Wiki](https://github.com/ai-enhancement/framework/wiki/environment-configuration)  
**For Enterprise**: Contact enterprise@ai-enhancement.dev 