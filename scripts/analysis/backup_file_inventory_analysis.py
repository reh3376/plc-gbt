#!/usr/bin/env python3
"""
📁 Backup File Inventory Analysis
===================================

AI Task Orchestrator Implementation for Systematic File Reorganization

Comprehensive analysis of all backup files to plan database-specific reorganization:
- Inventory all plc_backup_* directories and contents
- Classify files by database type (Neo4j, PostgreSQL, Redis, Qdrant)
- Plan directory structure for organized storage
- Generate migration commands for systematic reorganization

Author: AI Task Orchestrator
Created: July 14, 2025
Version: 1.0.0 - Systematic File Organization
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class BackupFile:
    """Individual backup file specification"""
    filepath: str
    filename: str
    database_type: str
    file_type: str  # sql, rdb, json, directory
    size_bytes: int
    created_date: str
    source_directory: str


@dataclass
class BackupDirectory:
    """Backup directory analysis"""
    directory_name: str
    directory_path: str
    total_files: int
    total_size_bytes: int
    database_types: List[str]
    backup_files: List[BackupFile]
    target_organization: str


class BackupInventoryAnalyzer:
    """Comprehensive backup file inventory and organization planner"""
    
    def __init__(self):
        self.analysis_timestamp = datetime.now()
        self.session_id = f"backup_inventory_{self.analysis_timestamp.strftime('%Y%m%d_%H%M%S')}"
        self.inventory_results = []
        self.organization_plan = {}
        
        print("📁 Starting Backup File Inventory Analysis")
        print("=" * 50)
        print(f"📅 Analysis Date: {self.analysis_timestamp}")
        print(f"🎯 Objective: Plan database-specific backup file organization")
    
    def analyze_backup_directory(self, dir_path: Path) -> BackupDirectory:
        """Analyze individual backup directory"""
        
        backup_files = []
        database_types = set()
        total_size = 0
        
        if not dir_path.exists() or not dir_path.is_dir():
            return None
        
        print(f"\n🔍 Analyzing: {dir_path.name}")
        
        for item in dir_path.iterdir():
            if item.is_file():
                # Determine database type from filename
                database_type = self._classify_file_by_name(item.name)
                file_type = item.suffix.lstrip('.') if item.suffix else 'unknown'
                
                backup_file = BackupFile(
                    filepath=str(item),
                    filename=item.name,
                    database_type=database_type,
                    file_type=file_type,
                    size_bytes=item.stat().st_size,
                    created_date=datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                    source_directory=str(dir_path)
                )
                
                backup_files.append(backup_file)
                database_types.add(database_type)
                total_size += item.stat().st_size
                
                print(f"   📄 {item.name} -> {database_type} ({file_type})")
            
            elif item.is_dir():
                # Handle nested directories (like Neo4j backup dirs)
                database_type = self._classify_file_by_name(item.name)
                
                # Calculate directory size
                dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                
                backup_file = BackupFile(
                    filepath=str(item),
                    filename=item.name,
                    database_type=database_type,
                    file_type='directory',
                    size_bytes=dir_size,
                    created_date=datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                    source_directory=str(dir_path)
                )
                
                backup_files.append(backup_file)
                database_types.add(database_type)
                total_size += dir_size
                
                print(f"   📁 {item.name}/ -> {database_type} (directory)")
        
        # Determine target organization based on dominant database type
        target_org = self._determine_target_organization(database_types, backup_files)
        
        backup_dir = BackupDirectory(
            directory_name=dir_path.name,
            directory_path=str(dir_path),
            total_files=len(backup_files),
            total_size_bytes=total_size,
            database_types=list(database_types),
            backup_files=backup_files,
            target_organization=target_org
        )
        
        print(f"   📊 Summary: {len(backup_files)} files, {total_size/1024/1024:.2f} MB")
        print(f"   🎯 Target: {target_org}")
        
        return backup_dir
    
    def _classify_file_by_name(self, filename: str) -> str:
        """Classify file by database type based on filename patterns"""
        
        filename_lower = filename.lower()
        
        if 'neo4j' in filename_lower or filename_lower.endswith('.neo4j'):
            return 'neo4j'
        elif 'redis' in filename_lower or filename_lower.endswith('.rdb'):
            return 'redis'  
        elif 'postgresql' in filename_lower or 'postgres' in filename_lower or filename_lower.endswith('.sql'):
            return 'postgresql'
        elif 'qdrant' in filename_lower or (filename_lower.endswith('.json') and 'qdrant' in filename_lower):
            return 'qdrant'
        elif filename_lower.endswith('.json') and 'backup_summary' in filename_lower:
            return 'summary'
        else:
            return 'mixed'
    
    def _determine_target_organization(self, database_types: set, backup_files: List[BackupFile]) -> str:
        """Determine target organization directory based on contents"""
        
        # Remove 'summary' from consideration for organization
        db_types = {dt for dt in database_types if dt not in ['summary', 'mixed']}
        
        if len(db_types) == 0:
            return 'plc_backups/plc_backup_mixed'
        elif len(db_types) == 1:
            db_type = list(db_types)[0]
            return f'plc_backup_{db_type}'
        else:
            # Multi-database backup - determine primary type by file count or size
            type_counts = {}
            for bf in backup_files:
                if bf.database_type not in ['summary', 'mixed']:
                    type_counts[bf.database_type] = type_counts.get(bf.database_type, 0) + 1
            
            if type_counts:
                primary_type = max(type_counts.items(), key=lambda x: x[1])[0]
                return f'plc_backup_{primary_type}'
            else:
                return 'plc_backups/plc_backup_mixed'
    
    def run_comprehensive_inventory(self) -> Dict[str, Any]:
        """Run comprehensive inventory of all backup directories"""
        
        print(f"\n🚀 Starting comprehensive backup inventory")
        print("=" * 60)
        
        # Find all plc_backup_* directories
        current_dir = Path('.')
        backup_dirs = [d for d in current_dir.iterdir() 
                      if d.is_dir() and d.name.startswith('plc_backup_') and d.name != 'plc_backup_cli.py']
        
        print(f"📂 Found {len(backup_dirs)} backup directories to analyze")
        
        # Analyze each directory
        for backup_dir in backup_dirs:
            analysis = self.analyze_backup_directory(backup_dir)
            if analysis:
                self.inventory_results.append(analysis)
        
        # Generate organization plan
        self._generate_organization_plan()
        
        return self._generate_inventory_summary()
    
    def _generate_organization_plan(self):
        """Generate systematic organization plan"""
        
        self.organization_plan = {
            'target_directories': {
                'plc_backup_neo4j': [],
                'plc_backup_redis': [],
                'plc_backup_postgresql': [],
                'plc_backup_qdrant': [],
                'plc_backups/plc_backup_mixed': []
            },
            'migration_commands': [],
            'cli_updates_needed': []
        }
        
        # Group directories by target organization
        for analysis in self.inventory_results:
            target = analysis.target_organization
            
            if target in self.organization_plan['target_directories']:
                self.organization_plan['target_directories'][target].append(analysis)
            else:
                self.organization_plan['target_directories']['plc_backups/plc_backup_mixed'].append(analysis)
            
            # Generate migration command
            migration_cmd = f"mkdir -p {target} && mv {analysis.directory_path} {target}/"
            self.organization_plan['migration_commands'].append(migration_cmd)
        
        # Identify CLI updates needed
        cli_files = ['backup_cli_complete.py', 'plc_backup_cli.py', 'enterprise_backup_cli.py', 'enhanced_backup_cli.py']
        for cli_file in cli_files:
            if Path(cli_file).exists():
                self.organization_plan['cli_updates_needed'].append(cli_file)
    
    def _generate_inventory_summary(self) -> Dict[str, Any]:
        """Generate comprehensive inventory summary"""
        
        total_directories = len(self.inventory_results)
        total_files = sum(analysis.total_files for analysis in self.inventory_results)
        total_size_mb = sum(analysis.total_size_bytes for analysis in self.inventory_results) / (1024 * 1024)
        
        # Database type distribution
        db_distribution = {}
        for analysis in self.inventory_results:
            for db_type in analysis.database_types:
                if db_type not in ['summary', 'mixed']:
                    db_distribution[db_type] = db_distribution.get(db_type, 0) + 1
        
        summary = {
            'inventory_metadata': {
                'session_id': self.session_id,
                'timestamp': self.analysis_timestamp.isoformat(),
                'total_backup_directories': total_directories,
                'total_backup_files': total_files,
                'total_size_mb': round(total_size_mb, 2)
            },
            'database_distribution': db_distribution,
            'organization_plan': self.organization_plan,
            'detailed_analysis': [asdict(analysis) for analysis in self.inventory_results],
            'migration_recommendations': self._generate_migration_recommendations()
        }
        
        return summary
    
    def _generate_migration_recommendations(self) -> List[str]:
        """Generate migration recommendations"""
        
        recommendations = []
        
        # Analyze organization efficiency
        target_counts = {}
        for analysis in self.inventory_results:
            target = analysis.target_organization
            target_counts[target] = target_counts.get(target, 0) + 1
        
        recommendations.append(f"📁 Create {len(target_counts)} target directories for organized storage")
        
        if target_counts.get('plc_backups/plc_backup_mixed', 0) > 0:
            recommendations.append(f"⚠️ {target_counts['plc_backups/plc_backup_mixed']} directories contain mixed content")
        
        recommendations.append("🔧 Update CLI default paths to point to organized directories")
        recommendations.append("✅ Test all CLI commands after migration")
        recommendations.append("🗑️ Consider cleanup of empty directories after migration")
        
        return recommendations
    
    def print_inventory_summary(self, summary: Dict[str, Any]):
        """Print human-readable inventory summary"""
        
        print("\n" + "=" * 70)
        print("📁 BACKUP FILE INVENTORY SUMMARY")
        print("=" * 70)
        
        metadata = summary['inventory_metadata']
        print(f"🆔 Session: {metadata['session_id']}")
        print(f"📅 Timestamp: {metadata['timestamp']}")
        print(f"📂 Backup Directories: {metadata['total_backup_directories']}")
        print(f"📄 Total Files: {metadata['total_backup_files']}")
        print(f"💾 Total Size: {metadata['total_size_mb']} MB")
        
        print(f"\n📊 DATABASE TYPE DISTRIBUTION:")
        for db_type, count in summary['database_distribution'].items():
            print(f"   🔹 {db_type}: {count} directories")
        
        print(f"\n🎯 ORGANIZATION PLAN:")
        for target_dir, analyses in summary['organization_plan']['target_directories'].items():
            if analyses:
                print(f"   📁 {target_dir}: {len(analyses)} directories")
        
        print(f"\n🔧 MIGRATION COMMANDS:")
        for i, cmd in enumerate(summary['organization_plan']['migration_commands'][:5], 1):
            print(f"   {i}. {cmd}")
        
        remaining = len(summary['organization_plan']['migration_commands']) - 5
        if remaining > 0:
            print(f"   ... and {remaining} more commands")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(summary['migration_recommendations'], 1):
            print(f"   {i}. {rec}")


def main():
    """Execute backup file inventory analysis"""
    analyzer = BackupInventoryAnalyzer()
    
    # Run comprehensive inventory
    inventory_summary = analyzer.run_comprehensive_inventory()
    
    # Print summary
    analyzer.print_inventory_summary(inventory_summary)
    
    # Save detailed results
    results_file = f"{analyzer.session_id}_inventory.json"
    with open(results_file, 'w') as f:
        json.dump(inventory_summary, f, indent=2)
    
    print(f"\n📄 Detailed inventory saved: {results_file}")
    print(f"📁 Backup File Inventory Analysis Complete!")
    
    return inventory_summary


if __name__ == "__main__":
    main() 