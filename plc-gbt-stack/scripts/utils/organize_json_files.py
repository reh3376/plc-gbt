#!/usr/bin/env python3
"""
JSON File Organization Utility
Systematically organizes all JSON files related to git-based functionality
into appropriate directory structures.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class JSONFileOrganizer:
    """Organizes JSON files into categorized directory structure"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.results_dir = base_path / "plc-gpt-stack" / "results"
        
        # Directory mapping for different file types
        self.category_mapping = {
            "phase37": "phase37",
            "phase38": "phase38", 
            "phase8": "phase8",
            "git": "git-operations",
            "repo": "repository-analysis",
            "validation": "validation-reports",
            "test": "testing-results",
            "etl": "etl-pipeline",
            "training": "training-data",
            "backup": "backups"
        }
        
        self.organization_results = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "files_moved": 0,
            "categories": {},
            "errors": []
        }
    
    def categorize_file(self, file_path: Path) -> str:
        """Determine the appropriate category for a JSON file"""
        filename = file_path.name.lower()
        
        # Phase-specific categorization
        if "phase37" in filename:
            return "phase37"
        elif "phase38" in filename:
            return "phase38"
        elif "phase8" in filename:
            return "phase8"
        elif any(keyword in filename for keyword in ["git", "remote", "sync", "deploy"]):
            return "git-operations"
        elif any(keyword in filename for keyword in ["repo", "repository", "migration"]):
            return "repository-analysis"
        elif any(keyword in filename for keyword in ["validation", "validate"]):
            return "validation-reports"
        elif any(keyword in filename for keyword in ["test", "testing"]):
            return "testing-results"
        elif "etl" in filename:
            return "etl-pipeline"
        elif "training" in filename:
            return "training-data"
        elif "backup" in filename:
            return "backups"
        else:
            return "miscellaneous"
    
    def create_directory_structure(self):
        """Create the organized directory structure"""
        print("📁 Creating directory structure...")
        
        # Create base results directory
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Create category directories
        for category in self.category_mapping.values():
            category_dir = self.results_dir / category
            category_dir.mkdir(exist_ok=True)
            print(f"   ✅ Created: {category_dir}")
        
        # Create miscellaneous directory
        misc_dir = self.results_dir / "miscellaneous"
        misc_dir.mkdir(exist_ok=True)
        print(f"   ✅ Created: {misc_dir}")
    
    def find_json_files(self) -> List[Path]:
        """Find all JSON files in the project"""
        json_files = []
        
        # Search for JSON files
        for json_file in self.base_path.rglob("*.json"):
            # Skip files already in results directory
            if "results" not in str(json_file):
                json_files.append(json_file)
        
        return json_files
    
    def move_file(self, source: Path, target_dir: str) -> bool:
        """Move a file to the target directory"""
        try:
            target_path = self.results_dir / target_dir / source.name
            
            # Handle duplicate names
            if target_path.exists():
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = source.name.split(".")
                new_name = f"{name_parts[0]}_duplicate_{timestamp}.{name_parts[1]}"
                target_path = self.results_dir / target_dir / new_name
            
            shutil.move(str(source), str(target_path))
            return True
            
        except Exception as e:
            self.organization_results["errors"].append({
                "file": str(source),
                "error": str(e)
            })
            return False
    
    def organize_files(self) -> Dict:
        """Main organization function"""
        print("🔍 Finding JSON files...")
        json_files = self.find_json_files()
        
        print(f"📊 Found {len(json_files)} JSON files to organize")
        
        # Create directory structure
        self.create_directory_structure()
        
        print("\n🔄 Organizing files...")
        
        for json_file in json_files:
            self.organization_results["files_processed"] += 1
            
            # Determine category
            category = self.categorize_file(json_file)
            
            # Initialize category in results
            if category not in self.organization_results["categories"]:
                self.organization_results["categories"][category] = []
            
            # Move file
            if self.move_file(json_file, category):
                self.organization_results["files_moved"] += 1
                self.organization_results["categories"][category].append(json_file.name)
                print(f"   ✅ Moved {json_file.name} → {category}/")
            else:
                print(f"   ❌ Failed to move {json_file.name}")
        
        return self.organization_results
    
    def create_category_indexes(self):
        """Create index files for each category"""
        print("\n📋 Creating category indexes...")
        
        for category, files in self.organization_results["categories"].items():
            if not files:
                continue
                
            index_content = {
                "category": category,
                "description": self.get_category_description(category),
                "file_count": len(files),
                "files": files,
                "last_updated": datetime.now().isoformat()
            }
            
            index_path = self.results_dir / category / "index.json"
            with open(index_path, 'w') as f:
                json.dump(index_content, f, indent=2)
            
            print(f"   ✅ Created index for {category} ({len(files)} files)")
    
    def get_category_description(self, category: str) -> str:
        """Get description for each category"""
        descriptions = {
            "phase37": "Phase 3.7 repository migration and ACD file processing results",
            "phase38": "Phase 3.8 automated PLC file management and GitHub Actions workflows",
            "phase8": "Phase 8 autonomous PID tuning integration results",
            "git-operations": "Git synchronization, deployment, and remote operations",
            "repository-analysis": "Repository discovery, analysis, and migration manifests",
            "validation-reports": "File validation, structure checks, and compliance reports",
            "testing-results": "Test execution results, comprehensive test suites, and validations",
            "etl-pipeline": "ETL pipeline processing and data transformation results",
            "training-data": "AI model training data and statistics",
            "backups": "Backup files and recovery data",
            "miscellaneous": "Uncategorized JSON files requiring manual review"
        }
        return descriptions.get(category, "Uncategorized files")
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the organization"""
        report_path = self.results_dir / "organization_summary.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.organization_results, f, indent=2)
        
        return str(report_path)

def main():
    """Main execution function"""
    base_path = Path("/Users/reh3376/repos/PLC_GPT")
    organizer = JSONFileOrganizer(base_path)
    
    print("🤖 AI Task Orchestrator: JSON File Organization")
    print("=" * 60)
    
    # Organize files
    results = organizer.organize_files()
    
    # Create category indexes
    organizer.create_category_indexes()
    
    # Generate summary report
    summary_path = organizer.generate_summary_report()
    
    print(f"\n📊 Organization Summary:")
    print(f"   📁 Files processed: {results['files_processed']}")
    print(f"   ✅ Files moved: {results['files_moved']}")
    print(f"   📂 Categories created: {len(results['categories'])}")
    print(f"   ❌ Errors: {len(results['errors'])}")
    
    if results['errors']:
        print(f"\n⚠️  Errors encountered:")
        for error in results['errors']:
            print(f"   - {error['file']}: {error['error']}")
    
    print(f"\n📄 Summary report saved: {summary_path}")
    
    return results

if __name__ == "__main__":
    main() 