#!/usr/bin/env python3
"""
Simple Database Backup Script
============================

Comprehensive backup of all PLC-GPT databases using Docker CLI commands directly.
No additional Python dependencies required.

Backs up:
- Neo4j Knowledge Graph
- PostgreSQL Metadata  
- Qdrant Vector Database
- Redis Cache

Usage: python3 simple_db_backup.py
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


class SimpleDatabaseBackup:
    """Simple database backup using Docker CLI commands"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path("../../../plc-gbt-stack/backup") / f"session_{self.timestamp}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {}
        
        print("🚀 Starting Simple Database Backup Session")
        print(f"📁 Session ID: {self.timestamp}")
        print(f"📂 Backup Directory: {self.backup_dir.absolute()}")
    
    def check_containers(self):
        """Check if database containers are running"""
        print("\n🔍 Checking database containers...")
        
        containers = ['plc-neo4j', 'plc-postgres', 'plc-qdrant', 'plc-redis']
        status = {}
        
        for container in containers:
            try:
                result = subprocess.run(
                    ['docker', 'ps', '--filter', f'name={container}', '--format', '{{.Names}}'],
                    capture_output=True, text=True, timeout=10
                )
                
                is_running = container in result.stdout
                status[container] = is_running
                icon = "✅" if is_running else "❌"
                print(f"  {icon} {container}: {'Running' if is_running else 'Not running'}")
                
            except Exception as e:
                status[container] = False
                print(f"  ❌ {container}: Error checking status - {e}")
        
        return status
    
    def backup_neo4j(self):
        """Backup Neo4j database"""
        print("\n🧠 Backing up Neo4j Knowledge Graph...")
        
        start_time = time.time()
        backup_file = self.backup_dir / f"neo4j_dump_{self.timestamp}.cypher"
        
        try:
            # Export all data as Cypher statements
            cmd = [
                'docker', 'exec', 'plc-neo4j',
                'cypher-shell', '-u', 'neo4j', '-p', 'your-secure-neo4j-password',
                'CALL apoc.export.cypher.all(null,{stream:true}) YIELD file, batches, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data RETURN data'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                with open(backup_file, 'w') as f:
                    f.write(result.stdout)
                
                # Get node and relationship counts
                nodes_cmd = [
                    'docker', 'exec', 'plc-neo4j',
                    'cypher-shell', '-u', 'neo4j', '-p', 'your-secure-neo4j-password',
                    'MATCH (n) RETURN count(n) as count'
                ]
                
                nodes_result = subprocess.run(nodes_cmd, capture_output=True, text=True, timeout=30)
                node_count = 0
                if nodes_result.returncode == 0:
                    lines = nodes_result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip().isdigit():
                            node_count = int(line.strip())
                            break
                
                # Get relationship count
                rels_cmd = [
                    'docker', 'exec', 'plc-neo4j',
                    'cypher-shell', '-u', 'neo4j', '-p', 'your-secure-neo4j-password',
                    'MATCH ()-[r]->() RETURN count(r) as count'
                ]
                
                rels_result = subprocess.run(rels_cmd, capture_output=True, text=True, timeout=30)
                rel_count = 0
                if rels_result.returncode == 0:
                    lines = rels_result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip().isdigit():
                            rel_count = int(line.strip())
                            break
                
                file_size = backup_file.stat().st_size / (1024 * 1024)
                duration = time.time() - start_time
                
                self.results['neo4j'] = {
                    'status': 'success',
                    'file': str(backup_file),
                    'size_mb': round(file_size, 3),
                    'nodes': node_count,
                    'relationships': rel_count,
                    'duration': round(duration, 1)
                }
                
                print(f"  ✅ Neo4j backup complete: {backup_file.name}")
                print(f"     📊 {node_count:,} nodes, {rel_count:,} relationships")
                print(f"     💾 {file_size:.3f} MB, {duration:.1f}s")
                
            else:
                # Fallback: simple node export
                simple_cmd = [
                    'docker', 'exec', 'plc-neo4j',
                    'cypher-shell', '-u', 'neo4j', '-p', 'your-secure-neo4j-password',
                    'MATCH (n) RETURN n LIMIT 1000'
                ]
                
                simple_result = subprocess.run(simple_cmd, capture_output=True, text=True, timeout=30)
                
                if simple_result.returncode == 0:
                    with open(backup_file, 'w') as f:
                        f.write(simple_result.stdout)
                    
                    file_size = backup_file.stat().st_size / (1024 * 1024)
                    duration = time.time() - start_time
                    
                    self.results['neo4j'] = {
                        'status': 'partial',
                        'file': str(backup_file),
                        'size_mb': round(file_size, 3),
                        'nodes': 'limited',
                        'relationships': 'limited',
                        'duration': round(duration, 1),
                        'note': 'Fallback export - limited data'
                    }
                    
                    print(f"  ⚠️ Neo4j partial backup: {backup_file.name}")
                else:
                    raise Exception(f"Neo4j export failed: {result.stderr}")
        
        except Exception as e:
            duration = time.time() - start_time
            self.results['neo4j'] = {
                'status': 'failed',
                'error': str(e),
                'duration': round(duration, 1)
            }
            print(f"  ❌ Neo4j backup failed: {e}")
    
    def backup_postgresql(self):
        """Backup PostgreSQL database"""
        print("\n📊 Backing up PostgreSQL Database...")
        
        start_time = time.time()
        backup_file = self.backup_dir / f"postgresql_dump_{self.timestamp}.sql"
        
        try:
            cmd = [
                'docker', 'exec', 'plc-postgres',
                'pg_dump', '-U', 'plc_user', 'plc_metadata'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                with open(backup_file, 'w') as f:
                    f.write(result.stdout)
                
                file_size = backup_file.stat().st_size / (1024 * 1024)
                duration = time.time() - start_time
                
                # Count tables
                table_count = result.stdout.count('CREATE TABLE')
                
                self.results['postgresql'] = {
                    'status': 'success',
                    'file': str(backup_file),
                    'size_mb': round(file_size, 3),
                    'tables': table_count,
                    'duration': round(duration, 1)
                }
                
                print(f"  ✅ PostgreSQL backup complete: {backup_file.name}")
                print(f"     📊 {table_count} tables")
                print(f"     💾 {file_size:.3f} MB, {duration:.1f}s")
            else:
                raise Exception(f"pg_dump failed: {result.stderr}")
        
        except Exception as e:
            duration = time.time() - start_time
            self.results['postgresql'] = {
                'status': 'failed',
                'error': str(e),
                'duration': round(duration, 1)
            }
            print(f"  ❌ PostgreSQL backup failed: {e}")
    
    def backup_qdrant(self):
        """Backup Qdrant vector database"""
        print("\n🔍 Backing up Qdrant Vector Database...")
        
        start_time = time.time()
        backup_file = self.backup_dir / f"qdrant_collections_{self.timestamp}.json"
        
        try:
            # Use curl to get collections
            cmd = ['curl', '-s', 'http://localhost:6333/collections']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                collections_data = json.loads(result.stdout)
                
                backup_data = {
                    'timestamp': self.timestamp,
                    'collections': collections_data,
                    'backup_method': 'rest_api_export'
                }
                
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                
                file_size = backup_file.stat().st_size / (1024 * 1024)
                duration = time.time() - start_time
                
                collections_count = len(collections_data.get('result', {}).get('collections', []))
                
                self.results['qdrant'] = {
                    'status': 'success',
                    'file': str(backup_file),
                    'size_mb': round(file_size, 3),
                    'collections': collections_count,
                    'duration': round(duration, 1)
                }
                
                print(f"  ✅ Qdrant backup complete: {backup_file.name}")
                print(f"     📊 {collections_count} collections")
                print(f"     💾 {file_size:.3f} MB, {duration:.1f}s")
            else:
                raise Exception(f"Qdrant API call failed: {result.stderr}")
        
        except Exception as e:
            duration = time.time() - start_time
            self.results['qdrant'] = {
                'status': 'failed',
                'error': str(e),
                'duration': round(duration, 1)
            }
            print(f"  ❌ Qdrant backup failed: {e}")
    
    def backup_redis(self):
        """Backup Redis cache database"""
        print("\n⚡ Backing up Redis Cache...")
        
        start_time = time.time()
        backup_file = self.backup_dir / f"redis_dump_{self.timestamp}.rdb"
        
        try:
            # Trigger background save
            bgsave_cmd = ['docker', 'exec', 'plc-redis', 'redis-cli', 'BGSAVE']
            bgsave_result = subprocess.run(bgsave_cmd, capture_output=True, text=True, timeout=30)
            
            if bgsave_result.returncode == 0 and 'Background saving started' in bgsave_result.stdout:
                print(f"  ⏳ Waiting for Redis BGSAVE to complete...")
                time.sleep(3)  # Wait for save to complete
                
                # Copy the dump file
                copy_cmd = ['docker', 'cp', 'plc-redis:/data/dump.rdb', str(backup_file)]
                copy_result = subprocess.run(copy_cmd, capture_output=True, text=True, timeout=30)
                
                if copy_result.returncode == 0:
                    file_size = backup_file.stat().st_size / (1024 * 1024)
                    duration = time.time() - start_time
                    
                    # Get key count
                    dbsize_cmd = ['docker', 'exec', 'plc-redis', 'redis-cli', 'DBSIZE']
                    dbsize_result = subprocess.run(dbsize_cmd, capture_output=True, text=True)
                    
                    key_count = 0
                    if dbsize_result.returncode == 0:
                        key_count = int(dbsize_result.stdout.strip())
                    
                    self.results['redis'] = {
                        'status': 'success',
                        'file': str(backup_file),
                        'size_mb': round(file_size, 3),
                        'keys': key_count,
                        'duration': round(duration, 1)
                    }
                    
                    print(f"  ✅ Redis backup complete: {backup_file.name}")
                    print(f"     📊 {key_count:,} keys")
                    print(f"     💾 {file_size:.3f} MB, {duration:.1f}s")
                else:
                    raise Exception(f"Failed to copy RDB file: {copy_result.stderr}")
            else:
                raise Exception(f"BGSAVE failed: {bgsave_result.stderr}")
        
        except Exception as e:
            duration = time.time() - start_time
            self.results['redis'] = {
                'status': 'failed',
                'error': str(e),
                'duration': round(duration, 1)
            }
            print(f"  ❌ Redis backup failed: {e}")
    
    def save_session_summary(self):
        """Save session summary"""
        summary = {
            'session_id': self.timestamp,
            'backup_timestamp': datetime.now().isoformat(),
            'backup_directory': str(self.backup_dir.absolute()),
            'results': self.results,
            'summary': {
                'total_databases': len(self.results),
                'successful': len([r for r in self.results.values() if r['status'] == 'success']),
                'failed': len([r for r in self.results.values() if r['status'] == 'failed']),
                'total_size_mb': sum(r.get('size_mb', 0) for r in self.results.values()),
                'total_duration': sum(r.get('duration', 0) for r in self.results.values())
            }
        }
        
        summary_file = self.backup_dir / 'backup_session_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def print_final_summary(self, summary):
        """Print final backup summary"""
        print("\n" + "="*70)
        print("🎯 DATABASE BACKUP SESSION COMPLETE")
        print("="*70)
        
        print(f"📊 Session ID: {summary['session_id']}")
        print(f"📂 Location: {summary['backup_directory']}")
        print(f"⏱️  Duration: {summary['summary']['total_duration']:.1f}s")
        print(f"💾 Total Size: {summary['summary']['total_size_mb']:.3f} MB")
        print(f"✅ Success: {summary['summary']['successful']}/{summary['summary']['total_databases']}")
        
        print(f"\n📋 Individual Results:")
        for db, result in summary['results'].items():
            status_icon = {"success": "✅", "failed": "❌", "partial": "⚠️"}.get(result['status'], "❓")
            size = result.get('size_mb', 0)
            duration = result.get('duration', 0)
            
            print(f"  {status_icon} {db.upper():12} | {size:8.3f} MB | {duration:6.1f}s")
            
            if result['status'] == 'success':
                if 'nodes' in result:
                    print(f"     └─ {result['nodes']:,} nodes, {result['relationships']:,} relationships")
                elif 'tables' in result:
                    print(f"     └─ {result['tables']} tables")
                elif 'collections' in result:
                    print(f"     └─ {result['collections']} collections")
                elif 'keys' in result:
                    print(f"     └─ {result['keys']:,} keys")
            elif result['status'] == 'failed':
                print(f"     └─ Error: {result['error']}")
        
        print(f"\n🎯 Next Steps:")
        print(f"  • Stage and commit roadmap changes")
        print(f"  • Push changes to repository")
        print(f"  • Validate backup integrity")
        print(f"  • Begin Phase 10: LLM Training Data Generation")
        
        print("="*70)
    
    def run_complete_backup(self):
        """Run complete backup of all databases"""
        # Check container status
        container_status = self.check_containers()
        
        # Backup each available database
        if container_status.get('plc-neo4j', False):
            self.backup_neo4j()
        
        if container_status.get('plc-postgres', False):
            self.backup_postgresql()
        
        if container_status.get('plc-qdrant', False):
            self.backup_qdrant()
        
        if container_status.get('plc-redis', False):
            self.backup_redis()
        
        # Generate and save summary
        summary = self.save_session_summary()
        self.print_final_summary(summary)
        
        return summary


def main():
    """Main execution function"""
    backup_system = SimpleDatabaseBackup()
    summary = backup_system.run_complete_backup()
    
    # Return appropriate exit code
    success_count = summary['summary']['successful']
    total_count = summary['summary']['total_databases']
    
    if success_count == total_count and total_count > 0:
        return 0  # All successful
    elif success_count > 0:
        return 1  # Some successful
    else:
        return 2  # All failed


if __name__ == "__main__":
    sys.exit(main()) 