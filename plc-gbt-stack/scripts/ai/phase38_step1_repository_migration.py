#!/usr/bin/env python3
"""
Phase 3.8.1: Repository Structure Migration & Setup
AI Task Orchestrator Guided Implementation

This script implements the repository structure migration for the automated PLC file 
management workflow. It creates the new directory structure, migrates existing files,
and implements validation and enforcement mechanisms.

New Structure:
- /plc-acd/          # Current running .acd file (single file)
- /plc-l5x/          # Current .l5x file (single file)  
- /plc-acd-previous/ # Previous .acd versions (timestamped)
- /plc-l5x-previous/ # Previous .l5x versions (timestamped)
- /plc/ (DEPRECATED) # Legacy directory to be migrated and removed
"""

import os
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import subprocess

# Add the plc-gbt-stack to the path for imports
sys.path.append('/Users/reh3376/repos/plc-gbt/plc-gbt-stack')

@dataclass
class RepositoryStatus:
    """Repository migration status tracking"""
    repo_name: str
    exists: bool
    legacy_plc_dir: bool
    legacy_files: List[str]
    new_structure_created: bool
    migration_completed: bool
    validation_passed: bool
    errors: List[str]

@dataclass
class MigrationPlan:
    """File migration plan for a repository"""
    repo_name: str
    legacy_files: List[Dict[str, Any]]
    migration_actions: List[Dict[str, Any]]
    backup_created: bool
    rollback_available: bool

class Phase38RepositoryMigrator:
    """
    Repository Structure Migration & Setup for Phase 3.8
    Implements AI Task Orchestrator methodology for systematic migration
    """
    
    def __init__(self):
        self.base_path = Path("/Users/reh3376/repos")
        self.plc_gbt_path = Path("/Users/reh3376/repos/plc-gbt")
        self.plc_repos = [f"plc-{i}00" for i in range(1, 7)]
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define new directory structure
        self.new_directories = [
            "plc-acd",           # Current .acd file (single)
            "plc-l5x",           # Current .l5x file (single)
            "plc-acd-previous",  # Previous .acd versions (multiple, timestamped)
            "plc-l5x-previous"   # Previous .l5x versions (multiple, timestamped)
        ]
        
        # File type mappings
        self.file_mappings = {
            ".acd": "plc-acd",
            ".ACD": "plc-acd", 
            ".l5x": "plc-l5x",
            ".L5X": "plc-l5x"
        }
        
        self.results = {
            "migration_timestamp": self.timestamp,
            "repositories_processed": [],
            "migration_summary": {},
            "errors": [],
            "rollback_procedures": []
        }
    
    def discover_repositories(self) -> List[RepositoryStatus]:
        """
        Discover and analyze all PLC repositories
        """
        print("🔍 Phase 3.8.1: Repository Discovery & Analysis")
        print("=" * 60)
        
        repo_statuses = []
        
        for repo_name in self.plc_repos:
            repo_path = self.base_path / repo_name
            status = RepositoryStatus(
                repo_name=repo_name,
                exists=repo_path.exists(),
                legacy_plc_dir=False,
                legacy_files=[],
                new_structure_created=False,
                migration_completed=False,
                validation_passed=False,
                errors=[]
            )
            
            if status.exists:
                # Check for legacy /plc/ directory
                legacy_plc_path = repo_path / "plc"
                if legacy_plc_path.exists():
                    status.legacy_plc_dir = True
                    
                    # Discover legacy files
                    try:
                        for file_path in legacy_plc_path.rglob("*"):
                            if file_path.is_file():
                                status.legacy_files.append(str(file_path.relative_to(repo_path)))
                    except Exception as e:
                        status.errors.append(f"Error discovering legacy files: {str(e)}")
                
                print(f"✅ {repo_name}: Found repository")
                print(f"   📁 Legacy /plc/ directory: {'Yes' if status.legacy_plc_dir else 'No'}")
                print(f"   📄 Legacy files: {len(status.legacy_files)}")
            else:
                print(f"❌ {repo_name}: Repository not found")
                status.errors.append("Repository not found")
            
            repo_statuses.append(status)
        
        return repo_statuses
    
    def create_migration_plan(self, repo_status: RepositoryStatus) -> MigrationPlan:
        """
        Create detailed migration plan for a repository
        """
        repo_path = self.base_path / repo_status.repo_name
        legacy_plc_path = repo_path / "plc"
        
        plan = MigrationPlan(
            repo_name=repo_status.repo_name,
            legacy_files=[],
            migration_actions=[],
            backup_created=False,
            rollback_available=False
        )
        
        if not repo_status.legacy_plc_dir:
            return plan
        
        # Analyze legacy files
        for file_rel_path in repo_status.legacy_files:
            file_path = repo_path / file_rel_path
            file_info = {
                "relative_path": file_rel_path,
                "absolute_path": str(file_path),
                "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
                "modified_time": file_path.stat().st_mtime if file_path.exists() else 0,
                "file_extension": file_path.suffix.lower(),
                "target_directory": None,
                "migration_type": "unknown"
            }
            
            # Determine target directory based on file extension
            if file_info["file_extension"] in self.file_mappings:
                file_info["target_directory"] = self.file_mappings[file_info["file_extension"]]
                file_info["migration_type"] = "move_to_current"
            else:
                file_info["migration_type"] = "archive"
            
            plan.legacy_files.append(file_info)
        
        # Create migration actions
        for file_info in plan.legacy_files:
            if file_info["migration_type"] == "move_to_current":
                action = {
                    "action_type": "move_file",
                    "source": file_info["absolute_path"],
                    "target": str(repo_path / file_info["target_directory"] / Path(file_info["relative_path"]).name),
                    "backup_source": str(repo_path / "migration_backup" / file_info["relative_path"]),
                    "file_type": file_info["file_extension"]
                }
                plan.migration_actions.append(action)
            elif file_info["migration_type"] == "archive":
                action = {
                    "action_type": "archive_file", 
                    "source": file_info["absolute_path"],
                    "target": str(repo_path / "plc-archive" / f"legacy_{self.timestamp}" / file_info["relative_path"]),
                    "backup_source": str(repo_path / "migration_backup" / file_info["relative_path"]),
                    "file_type": file_info["file_extension"]
                }
                plan.migration_actions.append(action)
        
        return plan
    
    def create_backup(self, repo_status: RepositoryStatus, migration_plan: MigrationPlan) -> bool:
        """
        Create comprehensive backup before migration
        """
        repo_path = self.base_path / repo_status.repo_name
        backup_path = repo_path / "migration_backup" / self.timestamp
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup entire /plc/ directory if it exists
            legacy_plc_path = repo_path / "plc"
            if legacy_plc_path.exists():
                backup_plc_path = backup_path / "plc"
                shutil.copytree(legacy_plc_path, backup_plc_path)
                
            # Create backup metadata
            backup_metadata = {
                "backup_timestamp": self.timestamp,
                "repository": repo_status.repo_name,
                "legacy_files_count": len(migration_plan.legacy_files),
                "migration_actions_count": len(migration_plan.migration_actions),
                "backup_path": str(backup_path),
                "original_structure": {
                    "plc_directory": str(legacy_plc_path) if legacy_plc_path.exists() else None,
                    "files": [f["relative_path"] for f in migration_plan.legacy_files]
                }
            }
            
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            migration_plan.backup_created = True
            migration_plan.rollback_available = True
            
            print(f"✅ {repo_status.repo_name}: Backup created at {backup_path}")
            return True
            
        except Exception as e:
            error_msg = f"Backup creation failed: {str(e)}"
            repo_status.errors.append(error_msg)
            print(f"❌ {repo_status.repo_name}: {error_msg}")
            return False
    
    def create_new_directory_structure(self, repo_status: RepositoryStatus) -> bool:
        """
        Create new directory structure in repository
        """
        repo_path = self.base_path / repo_status.repo_name
        
        try:
            for directory in self.new_directories:
                dir_path = repo_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Create README.md for each directory
                readme_content = self.generate_directory_readme(directory)
                readme_path = dir_path / "README.md"
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
            
            # Create .gitkeep files for empty directories
            for directory in self.new_directories:
                dir_path = repo_path / directory
                gitkeep_path = dir_path / ".gitkeep"
                if not any(dir_path.iterdir()):  # If directory is empty
                    gitkeep_path.touch()
            
            repo_status.new_structure_created = True
            print(f"✅ {repo_status.repo_name}: New directory structure created")
            return True
            
        except Exception as e:
            error_msg = f"Directory structure creation failed: {str(e)}"
            repo_status.errors.append(error_msg)
            print(f"❌ {repo_status.repo_name}: {error_msg}")
            return False
    
    def generate_directory_readme(self, directory: str) -> str:
        """
        Generate README.md content for directory
        """
        readme_templates = {
            "plc-acd": """# PLC ACD Files (Current)

This directory contains the **current active** ACD file for this PLC.

## Rules:
- ✅ **SINGLE FILE ONLY** - Only one .acd file should exist in this directory
- 🔄 **Current Version** - This is the production-ready ACD file
- 📝 **Studio 5000** - Engineers work with this file in Studio 5000
- 🚀 **Automated Management** - File management handled by GitHub Actions

## Workflow:
1. Engineers clone repository and work with the .acd file in Studio 5000
2. Changes are committed to feature branches
3. Pull requests trigger validation and conversion workflows
4. Successful merges update this directory automatically

## Previous Versions:
Previous versions are automatically archived in `/plc-acd-previous/` with timestamps.
""",
            "plc-l5x": """# PLC L5X Files (Current)

This directory contains the **current active** L5X file for this PLC.

## Rules:
- ✅ **SINGLE FILE ONLY** - Only one .l5x file should exist in this directory
- 🔄 **Auto-Generated** - Created automatically from ACD files via GitHub Actions
- 📊 **Version Sync** - Synchronized with corresponding ACD file
- 🔒 **Read-Only** - Do not manually edit these files

## Workflow:
1. L5X files are automatically generated when ACD files are merged
2. Conversion uses plc-format-converter for bidirectional compatibility
3. Validation ensures data integrity between ACD and L5X formats
4. Previous versions are automatically archived

## Previous Versions:
Previous versions are automatically archived in `/plc-l5x-previous/` with timestamps.
""",
            "plc-acd-previous": """# PLC ACD Files (Previous Versions)

This directory contains **previous versions** of ACD files with timestamp-based naming.

## Naming Convention:
```
{original_filename}_{YYYYMMDD_HHMMSS}.acd
```

## Rules:
- 📚 **Multiple Files** - Contains historical versions with timestamps
- 🔄 **Auto-Archive** - Files moved here automatically on new merges
- 📊 **Version History** - Complete history of ACD file changes
- 🔍 **Comparison** - Use for diff analysis and rollback procedures

## Retention Policy:
- Files are retained based on configured retention policies
- Automatic cleanup of old versions (configurable)
- Critical versions can be tagged for permanent retention

## Usage:
- Compare current version with previous versions
- Rollback to previous version if needed
- Analyze change history and evolution
""",
            "plc-l5x-previous": """# PLC L5X Files (Previous Versions)

This directory contains **previous versions** of L5X files with timestamp-based naming.

## Naming Convention:
```
{original_filename}_{YYYYMMDD_HHMMSS}.l5x
```

## Rules:
- 📚 **Multiple Files** - Contains historical versions with timestamps
- 🔄 **Auto-Archive** - Files moved here automatically on new conversions
- 📊 **Version History** - Complete history of L5X file changes
- 🔗 **ACD Sync** - Corresponds to ACD file versions

## Retention Policy:
- Files are retained based on configured retention policies
- Automatic cleanup of old versions (configurable)
- Critical versions can be tagged for permanent retention

## Usage:
- Compare current version with previous versions
- Analyze conversion history and quality
- Validate bidirectional conversion accuracy
"""
        }
        
        return readme_templates.get(directory, f"# {directory.title()}\n\nAutomatically managed directory for PLC files.\n")
    
    def execute_migration(self, repo_status: RepositoryStatus, migration_plan: MigrationPlan) -> bool:
        """
        Execute the migration plan
        """
        if not migration_plan.migration_actions:
            print(f"ℹ️  {repo_status.repo_name}: No migration actions required")
            repo_status.migration_completed = True
            return True
        
        try:
            repo_path = self.base_path / repo_status.repo_name
            
            for action in migration_plan.migration_actions:
                source_path = Path(action["source"])
                target_path = Path(action["target"])
                
                if action["action_type"] == "move_file":
                    # Ensure target directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file to new location
                    shutil.move(str(source_path), str(target_path))
                    print(f"   📁 Moved: {source_path.name} → {target_path.parent.name}/")
                    
                elif action["action_type"] == "archive_file":
                    # Ensure archive directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file to archive
                    shutil.move(str(source_path), str(target_path))
                    print(f"   📦 Archived: {source_path.name} → {target_path.parent.name}/")
            
            repo_status.migration_completed = True
            print(f"✅ {repo_status.repo_name}: Migration completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Migration execution failed: {str(e)}"
            repo_status.errors.append(error_msg)
            print(f"❌ {repo_status.repo_name}: {error_msg}")
            return False
    
    def cleanup_legacy_directory(self, repo_status: RepositoryStatus) -> bool:
        """
        Clean up legacy /plc/ directory after successful migration
        """
        if not repo_status.migration_completed:
            return False
        
        try:
            repo_path = self.base_path / repo_status.repo_name
            legacy_plc_path = repo_path / "plc"
            
            if legacy_plc_path.exists():
                # Create deprecation notice
                deprecation_notice = legacy_plc_path / "DEPRECATED_DIRECTORY.md"
                notice_content = f"""# DEPRECATED DIRECTORY

This directory has been **DEPRECATED** as of {self.timestamp}.

## Migration Complete
All files have been migrated to the new directory structure:
- `/plc-acd/` - Current ACD files
- `/plc-l5x/` - Current L5X files  
- `/plc-acd-previous/` - Previous ACD versions
- `/plc-l5x-previous/` - Previous L5X versions

## Backup Available
Complete backup available at: `/migration_backup/{self.timestamp}/`

## Removal Schedule
This directory will be removed in the next maintenance cycle.
Contact repository administrator if you need to access legacy files.
"""
                with open(deprecation_notice, 'w') as f:
                    f.write(notice_content)
                
                print(f"⚠️  {repo_status.repo_name}: Legacy /plc/ directory marked as deprecated")
                
                # Optionally remove the directory (commented out for safety)
                # shutil.rmtree(legacy_plc_path)
                # print(f"🗑️  {repo_status.repo_name}: Legacy /plc/ directory removed")
            
            return True
            
        except Exception as e:
            error_msg = f"Legacy cleanup failed: {str(e)}"
            repo_status.errors.append(error_msg)
            print(f"❌ {repo_status.repo_name}: {error_msg}")
            return False
    
    def validate_migration(self, repo_status: RepositoryStatus, migration_plan: MigrationPlan) -> bool:
        """
        Validate migration was successful
        """
        try:
            repo_path = self.base_path / repo_status.repo_name
            validation_results = {
                "new_directories_exist": True,
                "files_migrated_correctly": True,
                "backup_intact": True,
                "structure_compliant": True
            }
            
            # Check new directories exist
            for directory in self.new_directories:
                dir_path = repo_path / directory
                if not dir_path.exists():
                    validation_results["new_directories_exist"] = False
                    repo_status.errors.append(f"New directory missing: {directory}")
            
            # Check migrated files exist in correct locations
            for action in migration_plan.migration_actions:
                target_path = Path(action["target"])
                if not target_path.exists():
                    validation_results["files_migrated_correctly"] = False
                    repo_status.errors.append(f"Migrated file missing: {target_path}")
            
            # Check backup integrity
            backup_path = repo_path / "migration_backup" / self.timestamp
            if migration_plan.backup_created and not backup_path.exists():
                validation_results["backup_intact"] = False
                repo_status.errors.append("Migration backup missing")
            
            # Overall validation
            repo_status.validation_passed = all(validation_results.values())
            
            if repo_status.validation_passed:
                print(f"✅ {repo_status.repo_name}: Validation passed")
            else:
                print(f"❌ {repo_status.repo_name}: Validation failed")
                for key, value in validation_results.items():
                    if not value:
                        print(f"   ❌ {key}")
            
            return repo_status.validation_passed
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            repo_status.errors.append(error_msg)
            print(f"❌ {repo_status.repo_name}: {error_msg}")
            return False
    
    def migrate_repository(self, repo_status: RepositoryStatus) -> bool:
        """
        Complete migration process for a single repository
        """
        print(f"\n🔄 Processing {repo_status.repo_name}")
        print("-" * 40)
        
        if not repo_status.exists:
            print(f"⏭️  Skipping {repo_status.repo_name}: Repository not found")
            return False
        
        # Step 1: Create migration plan
        migration_plan = self.create_migration_plan(repo_status)
        
        # Step 2: Create backup
        if not self.create_backup(repo_status, migration_plan):
            return False
        
        # Step 3: Create new directory structure
        if not self.create_new_directory_structure(repo_status):
            return False
        
        # Step 4: Execute migration
        if not self.execute_migration(repo_status, migration_plan):
            return False
        
        # Step 5: Cleanup legacy directory
        if not self.cleanup_legacy_directory(repo_status):
            return False
        
        # Step 6: Validate migration
        if not self.validate_migration(repo_status, migration_plan):
            return False
        
        # Store results
        self.results["repositories_processed"].append({
            "repository": repo_status.repo_name,
            "status": "success" if repo_status.validation_passed else "failed",
            "legacy_files_migrated": len(migration_plan.legacy_files),
            "migration_actions": len(migration_plan.migration_actions),
            "errors": repo_status.errors
        })
        
        return repo_status.validation_passed
    
    def execute_full_migration(self) -> Dict[str, Any]:
        """
        Execute complete migration across all repositories
        """
        print("🚀 Phase 3.8.1: Repository Structure Migration & Setup")
        print("=" * 80)
        
        # Discover repositories
        repo_statuses = self.discover_repositories()
        
        # Migrate each repository
        successful_migrations = 0
        failed_migrations = 0
        
        for repo_status in repo_statuses:
            if self.migrate_repository(repo_status):
                successful_migrations += 1
            else:
                failed_migrations += 1
        
        # Generate summary
        self.results["migration_summary"] = {
            "total_repositories": len(repo_statuses),
            "successful_migrations": successful_migrations,
            "failed_migrations": failed_migrations,
            "success_rate": (successful_migrations / len(repo_statuses)) * 100 if repo_statuses else 0
        }
        
        print(f"\n📊 Migration Summary:")
        print(f"   📁 Total Repositories: {self.results['migration_summary']['total_repositories']}")
        print(f"   ✅ Successful: {successful_migrations}")
        print(f"   ❌ Failed: {failed_migrations}")
        print(f"   📈 Success Rate: {self.results['migration_summary']['success_rate']:.1f}%")
        
        return self.results
    
    def save_results(self, results: Dict[str, Any]) -> str:
        """
        Save migration results to file
        """
        output_file = f"phase38_step1_migration_results_{self.timestamp}.json"
        output_path = self.plc_gpt_path / "plc-gpt-stack" / "scripts" / "ai" / output_file
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")
        return str(output_path)

def main():
    """
    Main execution function for Phase 3.8.1 repository migration
    """
    migrator = Phase38RepositoryMigrator()
    
    try:
        # Execute full migration
        results = migrator.execute_full_migration()
        
        # Save results
        results_file = migrator.save_results(results)
        
        print("\n" + "=" * 80)
        print("✅ PHASE 3.8.1: REPOSITORY MIGRATION COMPLETE")
        print("=" * 80)
        print(f"📊 Success Rate: {results['migration_summary']['success_rate']:.1f}%")
        print(f"📁 Results File: {results_file}")
        
        if results['migration_summary']['success_rate'] == 100.0:
            print("\n🎯 NEXT STEPS:")
            print("1. Review migration results and validate new structure")
            print("2. Begin Phase 3.8.2: Automated Conversion Pipeline Development")
            print("3. Test new directory structure with sample files")
            print("4. Update documentation and engineer guidelines")
            
            return True
        else:
            print("\n⚠️  MIGRATION ISSUES DETECTED:")
            print("1. Review failed migrations and error messages")
            print("2. Fix issues before proceeding to next phase")
            print("3. Re-run migration for failed repositories")
            
            return False
        
    except Exception as e:
        print(f"❌ Error in Phase 3.8.1 migration: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 