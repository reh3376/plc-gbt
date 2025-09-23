# PLC Memory Database Backup Strategy

## 📦 Backup Overview

The PLC Memory System consists of 4 databases, each with specific backup requirements based on their data characteristics and criticality.

## 🗄️ Backup Directory Structure

```
/var/plc-gbt/backups/
├── redis/
│   ├── daily/
│   ├── hourly/
│   └── snapshots/
├── neo4j/
│   ├── weekly/
│   ├── daily/
│   └── graph-exports/
├── postgresql/
│   ├── daily/
│   ├── weekly/
│   ├── monthly/
│   └── wal-archives/
└── qdrant/
    ├── weekly/
    ├── collections/
    └── snapshots/
```

## 🔄 Backup Triggers & Schedules

### Redis (Real-time Cache)
```yaml
backup_triggers:
  - scheduled: "*/30 * * * *"  # Every 30 minutes
  - on_memory_threshold: 80%   # When memory usage exceeds 80%
  - before_maintenance: true    # Before any maintenance operation
  - on_critical_update: true    # After critical data changes

backup_types:
  - RDB snapshots: Hourly
  - AOF persistence: Continuous
  - Point-in-time: On-demand
```

### Neo4j (Knowledge Graph)
```yaml
backup_triggers:
  - scheduled: "0 2 * * *"     # Daily at 2 AM
  - after_bulk_import: true    # After importing new knowledge
  - before_schema_change: true # Before graph schema modifications
  - weekly_full: "0 3 * * 0"   # Weekly full backup on Sunday

backup_types:
  - Incremental: Daily
  - Full backup: Weekly
  - Graph export: On-demand
```

### PostgreSQL (Historical Data)
```yaml
backup_triggers:
  - scheduled: "0 1 * * *"     # Daily at 1 AM
  - continuous_archiving: true  # WAL archiving
  - before_migration: true      # Before schema migrations
  - monthly_full: "0 0 1 * *"  # Monthly full backup

backup_types:
  - Base backup: Daily
  - WAL archives: Continuous
  - Full dump: Weekly
  - Logical backup: Monthly
```

### Qdrant (Vector Embeddings)
```yaml
backup_triggers:
  - scheduled: "0 4 * * 1,4"   # Monday and Thursday at 4 AM
  - after_reindexing: true     # After vector index rebuilding
  - collection_size_change: 20% # When collection size changes >20%
  - before_version_upgrade: true

backup_types:
  - Collection snapshots: Bi-weekly
  - Full export: Weekly
  - Metadata backup: Daily
```

## 📅 Retention Policies

### Redis Retention
```python
redis_retention = {
    "hourly_snapshots": "24 hours",    # Keep last 24 hourly snapshots
    "daily_snapshots": "7 days",        # Keep last 7 daily snapshots
    "aof_files": "3 days",              # Keep AOF files for 3 days
    "emergency_dumps": "30 days"        # Keep emergency dumps for 30 days
}
```

### Neo4j Retention
```python
neo4j_retention = {
    "daily_incremental": "14 days",     # Keep 2 weeks of incremental
    "weekly_full": "90 days",           # Keep 3 months of weekly fulls
    "monthly_archive": "1 year",        # Keep yearly archives
    "graph_exports": "180 days"         # Keep exports for 6 months
}
```

### PostgreSQL Retention
```python
postgresql_retention = {
    "daily_base": "30 days",            # Keep 30 days of base backups
    "wal_archives": "7 days",           # Keep 7 days of WAL files
    "weekly_full": "90 days",           # Keep 3 months of weekly dumps
    "monthly_logical": "2 years",       # Keep 2 years of monthly backups
    "yearly_archive": "7 years"         # Keep 7 years for compliance
}
```

### Qdrant Retention
```python
qdrant_retention = {
    "collection_snapshots": "30 days",   # Keep 30 days of snapshots
    "weekly_exports": "60 days",         # Keep 2 months of exports
    "metadata_daily": "14 days",         # Keep 2 weeks of metadata
    "version_backups": "180 days"        # Keep 6 months for rollback
}
```

## 🔧 Configuration Integration

### Python Configuration
```python
# config/backup_settings.py
from pydantic import BaseSettings, Field

class BackupConfig(BaseSettings):
    # Backup root directory
    backup_root: str = Field("/var/plc-gbt/backups", env="BACKUP_ROOT")
    
    # Redis backup settings
    redis_backup_interval: int = Field(30, env="REDIS_BACKUP_INTERVAL")  # minutes
    redis_retention_days: int = Field(7, env="REDIS_RETENTION_DAYS")
    
    # Neo4j backup settings
    neo4j_backup_hour: int = Field(2, env="NEO4J_BACKUP_HOUR")  # 2 AM
    neo4j_retention_days: int = Field(90, env="NEO4J_RETENTION_DAYS")
    
    # PostgreSQL backup settings
    postgres_backup_hour: int = Field(1, env="POSTGRES_BACKUP_HOUR")  # 1 AM
    postgres_wal_retention_days: int = Field(7, env="POSTGRES_WAL_RETENTION")
    postgres_full_retention_days: int = Field(90, env="POSTGRES_FULL_RETENTION")
    
    # Qdrant backup settings
    qdrant_backup_days: list = Field([1, 4], env="QDRANT_BACKUP_DAYS")  # Mon, Thu
    qdrant_retention_days: int = Field(60, env="QDRANT_RETENTION_DAYS")
    
    # Global settings
    enable_compression: bool = Field(True, env="BACKUP_COMPRESSION")
    enable_encryption: bool = Field(True, env="BACKUP_ENCRYPTION")
    alert_on_failure: bool = Field(True, env="BACKUP_ALERT_ON_FAILURE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### TypeScript Configuration
```typescript
// config/backupConfig.ts
import { z } from 'zod';

const BackupConfigSchema = z.object({
  // Backup root directory
  backupRoot: z.string().default('/var/plc-gbt/backups'),
  
  // Redis backup settings
  redis: z.object({
    backupInterval: z.number().default(30), // minutes
    retentionDays: z.number().default(7),
    enableSnapshots: z.boolean().default(true),
    enableAOF: z.boolean().default(true)
  }),
  
  // Neo4j backup settings
  neo4j: z.object({
    backupHour: z.number().default(2), // 2 AM
    retentionDays: z.number().default(90),
    incrementalEnabled: z.boolean().default(true),
    fullBackupDay: z.number().default(0) // Sunday
  }),
  
  // PostgreSQL backup settings
  postgresql: z.object({
    backupHour: z.number().default(1), // 1 AM
    walRetentionDays: z.number().default(7),
    fullRetentionDays: z.number().default(90),
    enableWAL: z.boolean().default(true),
    enableLogicalBackup: z.boolean().default(true)
  }),
  
  // Qdrant backup settings
  qdrant: z.object({
    backupDays: z.array(z.number()).default([1, 4]), // Monday, Thursday
    retentionDays: z.number().default(60),
    snapshotEnabled: z.boolean().default(true),
    exportEnabled: z.boolean().default(true)
  }),
  
  // Global settings
  global: z.object({
    enableCompression: z.boolean().default(true),
    enableEncryption: z.boolean().default(true),
    alertOnFailure: z.boolean().default(true),
    notificationEmail: z.string().email().optional()
  })
});

export type BackupConfig = z.infer<typeof BackupConfigSchema>;
```

## 🚀 Backup Implementation

### Automated Backup Manager
```python
# backup/backup_manager.py
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import subprocess

class PLCMemoryBackupManager:
    def __init__(self, config: BackupConfig):
        self.config = config
        self.backup_root = Path(config.backup_root)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create backup directory structure if not exists."""
        databases = ['redis', 'neo4j', 'postgresql', 'qdrant']
        subdirs = {
            'redis': ['daily', 'hourly', 'snapshots'],
            'neo4j': ['weekly', 'daily', 'graph-exports'],
            'postgresql': ['daily', 'weekly', 'monthly', 'wal-archives'],
            'qdrant': ['weekly', 'collections', 'snapshots']
        }
        
        for db in databases:
            for subdir in subdirs[db]:
                path = self.backup_root / db / subdir
                path.mkdir(parents=True, exist_ok=True)
    
    async def backup_redis(self):
        """Backup Redis with RDB snapshot."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_root / 'redis' / 'hourly' / f'redis_{timestamp}.rdb'
        
        # Trigger Redis BGSAVE
        await self._execute_redis_command('BGSAVE')
        
        # Wait for completion and copy RDB file
        await asyncio.sleep(5)  # Wait for BGSAVE to complete
        shutil.copy2('/var/lib/redis/dump.rdb', backup_path)
        
        # Apply retention policy
        await self._cleanup_old_backups('redis/hourly', hours=24)
        
        return backup_path
    
    async def backup_neo4j(self, incremental=True):
        """Backup Neo4j database."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_type = 'incremental' if incremental else 'full'
        backup_path = self.backup_root / 'neo4j' / 'daily' / f'neo4j_{backup_type}_{timestamp}'
        
        cmd = [
            'neo4j-admin', 'backup',
            '--backup-dir', str(backup_path),
            '--database', 'neo4j'
        ]
        
        if incremental:
            cmd.extend(['--incremental', 'true'])
        
        await self._execute_command(cmd)
        
        # Apply retention policy
        await self._cleanup_old_backups('neo4j/daily', days=14)
        
        return backup_path
    
    async def backup_postgresql(self):
        """Backup PostgreSQL with pg_basebackup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_root / 'postgresql' / 'daily' / f'pg_base_{timestamp}'
        
        cmd = [
            'pg_basebackup',
            '-D', str(backup_path),
            '-Ft',  # tar format
            '-z',   # compress
            '-P',   # progress
            '-X', 'stream'  # include WAL
        ]
        
        await self._execute_command(cmd)
        
        # Archive WAL files
        await self._archive_wal_files()
        
        # Apply retention policy
        await self._cleanup_old_backups('postgresql/daily', days=30)
        await self._cleanup_old_backups('postgresql/wal-archives', days=7)
        
        return backup_path
    
    async def backup_qdrant(self):
        """Backup Qdrant collections."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_root / 'qdrant' / 'collections' / f'qdrant_{timestamp}'
        
        # Create Qdrant snapshot via API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.config.qdrant_url}/collections/snapshot",
                json={"wait": True}
            ) as response:
                snapshot_info = await response.json()
        
        # Copy snapshot to backup location
        shutil.copytree(snapshot_info['path'], backup_path)
        
        # Apply retention policy
        await self._cleanup_old_backups('qdrant/collections', days=30)
        
        return backup_path
    
    async def _cleanup_old_backups(self, subpath: str, days: int = None, hours: int = None):
        """Remove backups older than retention period."""
        path = self.backup_root / subpath
        
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
        else:
            cutoff = datetime.now() - timedelta(days=days)
        
        for backup in path.iterdir():
            if backup.stat().st_mtime < cutoff.timestamp():
                if backup.is_dir():
                    shutil.rmtree(backup)
                else:
                    backup.unlink()
    
    async def run_scheduled_backups(self):
        """Run backups according to schedule."""
        while True:
            now = datetime.now()
            
            # Redis - every 30 minutes
            if now.minute % self.config.redis_backup_interval == 0:
                await self.backup_redis()
            
            # Neo4j - daily at 2 AM
            if now.hour == self.config.neo4j_backup_hour and now.minute == 0:
                await self.backup_neo4j()
            
            # PostgreSQL - daily at 1 AM
            if now.hour == self.config.postgres_backup_hour and now.minute == 0:
                await self.backup_postgresql()
            
            # Qdrant - Monday and Thursday at 4 AM
            if now.weekday() in self.config.qdrant_backup_days and now.hour == 4 and now.minute == 0:
                await self.backup_qdrant()
            
            # Sleep until next minute
            await asyncio.sleep(60)
```

## 📊 Monitoring & Alerts

### Backup Health Dashboard
```python
class BackupHealthMonitor:
    def __init__(self, backup_manager: PLCMemoryBackupManager):
        self.backup_manager = backup_manager
        self.metrics = {
            'last_backup': {},
            'backup_size': {},
            'success_rate': {},
            'retention_compliance': {}
        }
    
    async def check_backup_health(self) -> dict:
        """Check health of all backups."""
        health_status = {
            'redis': await self._check_redis_backups(),
            'neo4j': await self._check_neo4j_backups(),
            'postgresql': await self._check_postgresql_backups(),
            'qdrant': await self._check_qdrant_backups(),
            'overall': 'healthy'
        }
        
        # Determine overall health
        if any(db['status'] == 'critical' for db in health_status.values() if isinstance(db, dict)):
            health_status['overall'] = 'critical'
        elif any(db['status'] == 'warning' for db in health_status.values() if isinstance(db, dict)):
            health_status['overall'] = 'warning'
        
        return health_status
    
    async def send_alert(self, message: str, severity: str = 'warning'):
        """Send backup alert notification."""
        if self.backup_manager.config.alert_on_failure:
            # Send email, Slack, or other notification
            print(f"[{severity.upper()}] Backup Alert: {message}")
```

## 🔐 Security Considerations

### Backup Encryption
```python
import cryptography.fernet

class BackupEncryption:
    def __init__(self, key: bytes):
        self.cipher = cryptography.fernet.Fernet(key)
    
    def encrypt_backup(self, backup_path: Path) -> Path:
        """Encrypt backup file."""
        encrypted_path = backup_path.with_suffix('.enc')
        
        with open(backup_path, 'rb') as infile:
            with open(encrypted_path, 'wb') as outfile:
                outfile.write(self.cipher.encrypt(infile.read()))
        
        # Remove unencrypted file
        backup_path.unlink()
        
        return encrypted_path
```

## 📋 Best Practices

1. **Test Restores Regularly**: Schedule monthly restore tests
2. **Monitor Backup Sizes**: Alert on unusual size changes
3. **Verify Backup Integrity**: Use checksums and validation
4. **Document Recovery Procedures**: Maintain up-to-date runbooks

## 💻 PLC Memory CLI Commands

### Primary Backup Commands (plc_memory_cli.py)
```bash
# Working directory: plc-gbt-stack/scripts/ai/
cd plc-gbt-stack/scripts/ai/

# Full system backup (all databases)
python3 plc_memory_cli.py backup

# Individual database backups
python3 plc_memory_cli.py backup -d redis      # Redis only
python3 plc_memory_cli.py backup -d neo4j      # Neo4j only
python3 plc_memory_cli.py backup -d postgresql # PostgreSQL only
python3 plc_memory_cli.py backup -d qdrant     # Qdrant only

# Backup with custom output directory
python3 plc_memory_cli.py backup -o /var/plc-gbt/backups/manual/

# Backup with compression
python3 plc_memory_cli.py backup --compress

# Backup with validation
python3 plc_memory_cli.py backup --validate

# Combined options
python3 plc_memory_cli.py backup -d neo4j postgresql --compress --validate -o /backup/path

# Health check before backup
python3 plc_memory_cli.py health
python3 plc_memory_cli.py status --detailed
```

### Alternative Backup CLIs

#### plc_backup_cli.py
```bash
# Working directory: project root
cd /path/to/plc-gbt/

# Full system operations
python3 scripts/cli/plc_backup_cli.py backup all        # Full system backup
python3 scripts/cli/plc_backup_cli.py backup redis      # Redis only
python3 scripts/cli/plc_backup_cli.py backup neo4j      # Neo4j only
python3 scripts/cli/plc_backup_cli.py backup postgresql # PostgreSQL only
python3 scripts/cli/plc_backup_cli.py backup qdrant     # Qdrant only

# Management commands
python3 scripts/cli/plc_backup_cli.py list              # List all backups
python3 scripts/cli/plc_backup_cli.py validate <session_id>  # Validate backup
python3 scripts/cli/plc_backup_cli.py status            # System status
python3 scripts/cli/plc_backup_cli.py cleanup --older-than 30d  # Cleanup old backups
```

#### plc_backup_cli_final.py
```bash
# Working directory: plc-gbt-stack/scripts/ai/
cd plc-gbt-stack/scripts/ai/

# Backup operations
python3 plc_backup_cli_final.py backup all       # Full system backup
python3 plc_backup_cli_final.py backup redis     # Redis only
python3 plc_backup_cli_final.py backup neo4j     # Neo4j only
python3 plc_backup_cli_final.py backup postgresql # PostgreSQL only
python3 plc_backup_cli_final.py backup qdrant     # Qdrant only

# Management commands
python3 plc_backup_cli_final.py list             # List backups
python3 plc_backup_cli_final.py status           # System status
```

### Automated Backup Schedule (Cron)
```bash
# Add to crontab -e

# Redis - every 30 minutes
*/30 * * * * cd /path/to/plc-gbt-stack/scripts/ai && python3 plc_memory_cli.py backup -d redis

# Neo4j - daily at 2 AM
0 2 * * * cd /path/to/plc-gbt-stack/scripts/ai && python3 plc_memory_cli.py backup -d neo4j --compress

# PostgreSQL - daily at 1 AM  
0 1 * * * cd /path/to/plc-gbt-stack/scripts/ai && python3 plc_memory_cli.py backup -d postgresql --compress

# Qdrant - Monday and Thursday at 4 AM
0 4 * * 1,4 cd /path/to/plc-gbt-stack/scripts/ai && python3 plc_memory_cli.py backup -d qdrant

# Full system backup - Sunday at 3 AM
0 3 * * 0 cd /path/to/plc-gbt-stack/scripts/ai && python3 plc_memory_cli.py backup --compress --validate

# Health check - every 6 hours
0 */6 * * * cd /path/to/plc-gbt-stack/scripts/ai && python3 plc_memory_cli.py health
```
5. **Secure Backup Storage**: Encrypt and restrict access
6. **Offsite Replication**: Copy critical backups to remote storage
7. **Automate Monitoring**: Use health checks and alerts

## 🚨 Critical Backup Rules

- **Never skip scheduled backups** without documenting the reason
- **Always verify backup completion** before applying retention
- **Test restore procedures** at least monthly
- **Maintain 3-2-1 backup strategy**: 3 copies, 2 different media, 1 offsite
- **Document all backup failures** and remediation steps
