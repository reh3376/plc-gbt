#!/usr/bin/env python3

"""
AI Enhancement Framework - Health Check Monitor
Comprehensive health monitoring for all framework services
"""

import asyncio
import logging
import time
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import aiohttp
import asyncpg
import redis.asyncio as redis
from neo4j import AsyncGraphDatabase
import qdrant_client
from qdrant_client.http import models as qdrant_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceHealth:
    """Service health status data structure"""
    name: str
    status: str  # 'healthy', 'unhealthy', 'degraded', 'unknown'
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class SystemHealth:
    """Overall system health data structure"""
    overall_status: str
    last_check: datetime
    services: Dict[str, ServiceHealth]
    summary: Dict[str, Any]

class HealthMonitor:
    """Comprehensive health monitoring for AI Enhancement Framework"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize health monitor with configuration"""
        self.config = config or self._load_default_config()
        self.session: Optional[aiohttp.ClientSession] = None
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'redis': {
                'url': 'redis://localhost:6379',
                'timeout': 5.0
            },
            'neo4j': {
                'uri': 'bolt://localhost:7687',
                'auth': ('neo4j', 'ai_framework_password'),
                'timeout': 10.0
            },
            'postgresql': {
                'host': 'localhost',
                'port': 5432,
                'database': 'ai_framework',
                'user': 'ai_framework_user',
                'password': 'ai_framework_password',
                'timeout': 10.0
            },
            'qdrant': {
                'url': 'http://localhost:6333',
                'timeout': 10.0
            },
            'framework_api': {
                'url': 'http://localhost:8000',
                'timeout': 15.0
            },
            'thresholds': {
                'response_time_warning': 1000,  # ms
                'response_time_critical': 5000,  # ms
                'error_rate_warning': 5,  # %
                'error_rate_critical': 15  # %
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def check_redis(self) -> ServiceHealth:
        """Check Redis service health"""
        start_time = time.time()
        
        try:
            redis_client = redis.from_url(
                self.config['redis']['url'],
                socket_connect_timeout=self.config['redis']['timeout']
            )
            
            # Test basic connectivity
            await redis_client.ping()
            
            # Test read/write operations
            test_key = f"health_check_{int(time.time())}"
            await redis_client.set(test_key, "test_value", ex=10)
            value = await redis_client.get(test_key)
            await redis_client.delete(test_key)
            
            # Get Redis info
            info = await redis_client.info()
            
            response_time = (time.time() - start_time) * 1000
            
            details = {
                'version': info.get('redis_version'),
                'uptime': info.get('uptime_in_seconds'),
                'connected_clients': info.get('connected_clients'),
                'used_memory': info.get('used_memory_human'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
            
            await redis_client.close()
            
            status = 'healthy'
            if response_time > self.config['thresholds']['response_time_warning']:
                status = 'degraded'
            
            return ServiceHealth(
                name='Redis',
                status=status,
                response_time=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Redis health check failed: {e}")
            
            return ServiceHealth(
                name='Redis',
                status='unhealthy',
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_neo4j(self) -> ServiceHealth:
        """Check Neo4j service health"""
        start_time = time.time()
        
        try:
            driver = AsyncGraphDatabase.driver(
                self.config['neo4j']['uri'],
                auth=self.config['neo4j']['auth']
            )
            
            async with driver.session() as session:
                # Test basic connectivity and query
                result = await session.run("RETURN 1 as test, datetime() as timestamp")
                record = await result.single()
                
                # Get database info
                db_info = await session.run("CALL dbms.components() YIELD name, versions, edition")
                components = [record async for record in db_info]
                
            response_time = (time.time() - start_time) * 1000
            
            details = {
                'test_query': record['test'],
                'timestamp': str(record['timestamp']),
                'components': [dict(component) for component in components]
            }
            
            await driver.close()
            
            status = 'healthy'
            if response_time > self.config['thresholds']['response_time_warning']:
                status = 'degraded'
            
            return ServiceHealth(
                name='Neo4j',
                status=status,
                response_time=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Neo4j health check failed: {e}")
            
            return ServiceHealth(
                name='Neo4j',
                status='unhealthy',
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_postgresql(self) -> ServiceHealth:
        """Check PostgreSQL service health"""
        start_time = time.time()
        
        try:
            dsn = f"postgresql://{self.config['postgresql']['user']}:{self.config['postgresql']['password']}@{self.config['postgresql']['host']}:{self.config['postgresql']['port']}/{self.config['postgresql']['database']}"
            
            conn = await asyncpg.connect(dsn)
            
            # Test basic connectivity
            result = await conn.fetchrow("SELECT version(), current_timestamp as timestamp")
            
            # Get database statistics
            stats = await conn.fetchrow("""
                SELECT 
                    pg_database_size(current_database()) as db_size,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT setting FROM pg_settings WHERE name = 'max_connections') as max_connections
            """)
            
            await conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            details = {
                'version': result['version'],
                'timestamp': str(result['timestamp']),
                'database_size': stats['db_size'],
                'active_connections': stats['active_connections'],
                'max_connections': stats['max_connections']
            }
            
            status = 'healthy'
            if response_time > self.config['thresholds']['response_time_warning']:
                status = 'degraded'
            
            return ServiceHealth(
                name='PostgreSQL',
                status=status,
                response_time=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"PostgreSQL health check failed: {e}")
            
            return ServiceHealth(
                name='PostgreSQL',
                status='unhealthy',
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_qdrant(self) -> ServiceHealth:
        """Check Qdrant service health"""
        start_time = time.time()
        
        try:
            client = qdrant_client.QdrantClient(
                url=self.config['qdrant']['url'],
                timeout=self.config['qdrant']['timeout']
            )
            
            # Test basic connectivity
            health = client.get_cluster_info()
            collections = client.get_collections()
            
            response_time = (time.time() - start_time) * 1000
            
            details = {
                'cluster_info': health.dict() if hasattr(health, 'dict') else str(health),
                'collections_count': len(collections.collections) if collections else 0,
                'collections': [col.name for col in collections.collections] if collections else []
            }
            
            status = 'healthy'
            if response_time > self.config['thresholds']['response_time_warning']:
                status = 'degraded'
            
            return ServiceHealth(
                name='Qdrant',
                status=status,
                response_time=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Qdrant health check failed: {e}")
            
            return ServiceHealth(
                name='Qdrant',
                status='unhealthy',
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_framework_api(self) -> ServiceHealth:
        """Check AI Framework API health"""
        start_time = time.time()
        
        try:
            if not self.session:
                raise RuntimeError("HTTP session not initialized")
            
            timeout = aiohttp.ClientTimeout(total=self.config['framework_api']['timeout'])
            
            # Check health endpoint
            async with self.session.get(
                f"{self.config['framework_api']['url']}/health",
                timeout=timeout
            ) as response:
                health_data = await response.json()
                response.raise_for_status()
            
            # Check API info endpoint
            async with self.session.get(
                f"{self.config['framework_api']['url']}/info",
                timeout=timeout
            ) as response:
                api_info = await response.json() if response.status == 200 else {}
            
            response_time = (time.time() - start_time) * 1000
            
            details = {
                'health_endpoint': health_data,
                'api_info': api_info,
                'status_code': response.status
            }
            
            status = 'healthy'
            if response_time > self.config['thresholds']['response_time_warning']:
                status = 'degraded'
            
            return ServiceHealth(
                name='Framework API',
                status=status,
                response_time=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Framework API health check failed: {e}")
            
            return ServiceHealth(
                name='Framework API',
                status='unhealthy',
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_all_services(self) -> SystemHealth:
        """Check all services and return system health"""
        logger.info("Starting comprehensive health check...")
        
        # Run all health checks concurrently
        health_checks = await asyncio.gather(
            self.check_redis(),
            self.check_neo4j(),
            self.check_postgresql(),
            self.check_qdrant(),
            self.check_framework_api(),
            return_exceptions=True
        )
        
        services = {}
        healthy_count = 0
        total_count = 0
        total_response_time = 0
        
        for health in health_checks:
            if isinstance(health, ServiceHealth):
                services[health.name] = health
                total_count += 1
                total_response_time += health.response_time
                
                if health.status == 'healthy':
                    healthy_count += 1
            else:
                logger.error(f"Health check failed with exception: {health}")
        
        # Determine overall status
        if healthy_count == total_count:
            overall_status = 'healthy'
        elif healthy_count >= total_count * 0.7:  # 70% or more healthy
            overall_status = 'degraded'
        else:
            overall_status = 'unhealthy'
        
        # Calculate summary statistics
        avg_response_time = total_response_time / max(total_count, 1)
        summary = {
            'healthy_services': healthy_count,
            'total_services': total_count,
            'health_percentage': (healthy_count / max(total_count, 1)) * 100,
            'average_response_time': avg_response_time,
            'check_duration': total_response_time
        }
        
        return SystemHealth(
            overall_status=overall_status,
            last_check=datetime.now(),
            services=services,
            summary=summary
        )
    
    def save_health_report(self, health: SystemHealth, filepath: str = None):
        """Save health report to file"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"health_report_{timestamp}.json"
        
        # Convert to serializable format
        report = {
            'overall_status': health.overall_status,
            'last_check': health.last_check.isoformat(),
            'services': {
                name: {
                    'name': service.name,
                    'status': service.status,
                    'response_time': service.response_time,
                    'last_check': service.last_check.isoformat(),
                    'error_message': service.error_message,
                    'details': service.details
                }
                for name, service in health.services.items()
            },
            'summary': health.summary
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Health report saved to {filepath}")
    
    def print_health_report(self, health: SystemHealth):
        """Print formatted health report to console"""
        print("\n" + "="*50)
        print("AI Enhancement Framework - Health Check Report")
        print("="*50)
        print(f"Overall Status: {health.overall_status.upper()}")
        print(f"Check Time: {health.last_check}")
        print(f"Health Score: {health.summary['health_percentage']:.1f}%")
        print(f"Average Response Time: {health.summary['average_response_time']:.2f}ms")
        print()
        
        # Service details
        print("Service Status:")
        print("-" * 30)
        
        for name, service in health.services.items():
            status_symbol = {
                'healthy': '✅',
                'degraded': '⚠️',
                'unhealthy': '❌',
                'unknown': '❓'
            }.get(service.status, '❓')
            
            print(f"{status_symbol} {service.name}")
            print(f"   Status: {service.status}")
            print(f"   Response Time: {service.response_time:.2f}ms")
            
            if service.error_message:
                print(f"   Error: {service.error_message}")
            
            if service.details:
                for key, value in service.details.items():
                    if isinstance(value, (str, int, float)):
                        print(f"   {key}: {value}")
            print()
        
        # Recommendations
        unhealthy_services = [s for s in health.services.values() if s.status in ['unhealthy', 'degraded']]
        if unhealthy_services:
            print("Recommendations:")
            print("-" * 20)
            for service in unhealthy_services:
                if service.status == 'unhealthy':
                    print(f"• Restart {service.name} service")
                elif service.status == 'degraded':
                    print(f"• Check {service.name} performance and resources")
        
        print("="*50)

async def main():
    """Main health check execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Enhancement Framework Health Check')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--output', help='Output file path for health report')
    parser.add_argument('--quiet', action='store_true', help='Suppress console output')
    parser.add_argument('--continuous', type=int, help='Run continuously with interval in seconds')
    
    args = parser.parse_args()
    
    # Load configuration if provided
    config = None
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    async with HealthMonitor(config) as monitor:
        if args.continuous:
            logger.info(f"Starting continuous health monitoring (interval: {args.continuous}s)")
            
            while True:
                try:
                    health = await monitor.check_all_services()
                    
                    if not args.quiet:
                        monitor.print_health_report(health)
                    
                    if args.output:
                        monitor.save_health_report(health, args.output)
                    
                    await asyncio.sleep(args.continuous)
                    
                except KeyboardInterrupt:
                    logger.info("Health monitoring stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Health check failed: {e}")
                    await asyncio.sleep(args.continuous)
        else:
            # Single health check
            health = await monitor.check_all_services()
            
            if not args.quiet:
                monitor.print_health_report(health)
            
            if args.output:
                monitor.save_health_report(health, args.output)
            
            # Exit with appropriate code
            if health.overall_status == 'healthy':
                sys.exit(0)
            elif health.overall_status == 'degraded':
                sys.exit(1)
            else:
                sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main()) 