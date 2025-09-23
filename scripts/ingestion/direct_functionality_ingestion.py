#!/usr/bin/env python3
"""
🧠 Direct Functionality Ingestion - AI Task Orchestrator Implementation

Direct file-based ingestion of new PLC-GBT functionality following
the AI Task Orchestrator methodology without database dependencies.

This script processes and structures the identified new functionality
for memory system ingestion, creating structured output files ready
for database import when connectivity is restored.

Author: AI Task Orchestrator
Created: July 22, 2025
Session: direct_ingestion_1753205820
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

class DirectFunctionalityIngestor:
    """Direct file-based functionality ingestion system"""
    
    def __init__(self, output_dir: str = "ingestion_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # New functionality files identified
        self.critical_files = [
            "docs/ENHANCED_MODEL_CONFIGURATION_CORRECTION_SUMMARY.md",
            "docs/CLI_API_BRIDGE_SOLUTION.md", 
            "ENHANCED_MODEL_CONFIGURATION_COMPLETION_SUMMARY.md",
            "ENHANCED_MODEL_DEPLOYMENT_READINESS_SUMMARY.md"
        ]
        
        self.high_priority_files = [
            "mcp/MCP_IMPLEMENTATION_COMPLETION_SUMMARY.md",
            "mcp/CURSOR_SETUP_INSTRUCTIONS.md",
            "mcp/cursor_integration_guide.md",
            "docs/PHASE26_4_NATURAL_LANGUAGE_WORKFLOW_ENGINE_COMPLETION.md",
            "docs/PHASE27_NATURAL_LANGUAGE_LLM_INTERFACE_COMPLETION.md",
            "docs/phase27_completion_appendix.md"
        ]
        
        self.medium_priority_files = [
            "scripts/results/phase27/PHASE27_ENHANCED_VALIDATION_REPORT_20250721_141621.md",
            "scripts/results/phase27/PHASE27_ULTRA_ENHANCED_VALIDATION_REPORT_20250721_142142.md",
            "mcp/MCP_DEBUGGING_RESOLUTION_SUMMARY.md",
            "mcp/MCP_SERVER_FIX_SUMMARY.md"
        ]
        
        # Structured data collections
        self.entities = []
        self.relationships = []
        self.vector_chunks = []
        self.metadata = {}
        
    def process_file(self, file_path: str, priority: str) -> Dict[str, Any]:
        """Process a single file and extract structured data"""
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return {}
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract metadata
            file_info = {
                "file_path": str(full_path),
                "file_name": full_path.name,
                "file_size": len(content),
                "priority": priority,
                "processed_at": datetime.now().isoformat(),
                "content_hash": hashlib.md5(content.encode()).hexdigest()
            }
            
            # Extract structured entities
            entities = self.extract_entities(content, file_info)
            
            # Create chunks for vector storage
            chunks = self.create_chunks(content, file_info)
            
            # Extract relationships
            relationships = self.extract_relationships(content, file_info)
            
            return {
                "file_info": file_info,
                "entities": entities,
                "chunks": chunks,
                "relationships": relationships
            }
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return {}
    
    def extract_entities(self, content: str, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract structured entities from content"""
        entities = []
        
        # Extract headers as entities
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        for i, header in enumerate(headers):
            entities.append({
                "type": "Header",
                "name": header.strip(),
                "properties": {
                    "level": len(re.match(r'^#+', header).group()),
                    "position": i,
                    "source_file": file_info["file_name"]
                }
            })
        
        # Extract code blocks as entities
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        for i, (lang, code) in enumerate(code_blocks):
            entities.append({
                "type": "CodeBlock",
                "name": f"CodeBlock_{i}",
                "properties": {
                    "language": lang or "text",
                    "code": code.strip(),
                    "source_file": file_info["file_name"]
                }
            })
        
        # Extract model references
        model_refs = re.findall(r'ft:gpt-[\w-]+:[\w-]+:[\w-]+:[\w-]+', content)
        for model_ref in set(model_refs):
            entities.append({
                "type": "ModelReference",
                "name": model_ref,
                "properties": {
                    "model_type": "fine_tuned",
                    "source_file": file_info["file_name"]
                }
            })
        
        # Extract file references
        file_refs = re.findall(r'`([^`]+\.(py|md|yml|yaml|json|ts|js))`', content)
        for file_ref, ext in file_refs:
            entities.append({
                "type": "FileReference",
                "name": file_ref,
                "properties": {
                    "extension": ext,
                    "source_file": file_info["file_name"]
                }
            })
        
        return entities
    
    def create_chunks(self, content: str, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create text chunks for vector storage"""
        chunks = []
        
        # Split content into sections
        sections = re.split(r'\n#+\s+', content)
        
        for i, section in enumerate(sections):
            if len(section.strip()) < 100:  # Skip very short sections
                continue
                
            # Create overlapping chunks of ~500 characters
            words = section.split()
            chunk_size = 100  # words
            overlap = 20      # words
            
            for j in range(0, len(words), chunk_size - overlap):
                chunk_words = words[j:j + chunk_size]
                chunk_text = ' '.join(chunk_words)
                
                if len(chunk_text) > 50:  # Only keep meaningful chunks
                    chunks.append({
                        "id": f"{file_info['file_name']}_chunk_{i}_{j}",
                        "text": chunk_text,
                        "metadata": {
                            "source_file": file_info["file_name"],
                            "section": i,
                            "position": j,
                            "priority": file_info["priority"]
                        }
                    })
        
        return chunks
    
    def extract_relationships(self, content: str, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Extract dependencies (file A imports/references file B)
        import_refs = re.findall(r'import\s+(\w+)', content)
        for ref in import_refs:
            relationships.append({
                "type": "IMPORTS",
                "source": file_info["file_name"],
                "target": ref,
                "properties": {"relationship_type": "import"}
            })
        
        # Extract links (file A links to file B)
        link_refs = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, url in link_refs:
            if not url.startswith('http'):  # Internal links
                relationships.append({
                    "type": "LINKS_TO",
                    "source": file_info["file_name"],
                    "target": url,
                    "properties": {"link_text": text}
                })
        
        return relationships
    
    def process_all_files(self) -> Dict[str, Any]:
        """Process all identified new functionality files"""
        print("🚀 Starting Direct Functionality Ingestion")
        print("="*60)
        
        all_results = {
            "critical": [],
            "high_priority": [],
            "medium_priority": []
        }
        
        # Process critical files
        print("\n📍 Processing CRITICAL functionality...")
        for file_path in self.critical_files:
            result = self.process_file(file_path, "critical")
            if result:
                all_results["critical"].append(result)
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
        
        # Process high priority files
        print("\n📍 Processing HIGH PRIORITY functionality...")
        for file_path in self.high_priority_files:
            result = self.process_file(file_path, "high_priority")
            if result:
                all_results["high_priority"].append(result)
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
        
        # Process medium priority files
        print("\n📍 Processing MEDIUM PRIORITY functionality...")
        for file_path in self.medium_priority_files:
            result = self.process_file(file_path, "medium_priority")
            if result:
                all_results["medium_priority"].append(result)
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
        
        return all_results
    
    def save_structured_output(self, results: Dict[str, Any]) -> None:
        """Save structured output for database import"""
        
        # Aggregate all data
        all_entities = []
        all_chunks = []
        all_relationships = []
        
        for priority_level in results.values():
            for file_result in priority_level:
                if file_result:
                    all_entities.extend(file_result.get("entities", []))
                    all_chunks.extend(file_result.get("chunks", []))
                    all_relationships.extend(file_result.get("relationships", []))
        
        # Save structured data for each database tier
        
        # Redis (short-term memory)
        redis_data = {
            "session_id": "direct_ingestion_1753205820",
            "timestamp": datetime.now().isoformat(),
            "active_configurations": [e for e in all_entities if e["type"] in ["ModelReference", "CodeBlock"]],
            "recent_files": [e for e in all_entities if e["type"] == "FileReference"]
        }
        
        with open(self.output_dir / "redis_data.json", 'w') as f:
            json.dump(redis_data, f, indent=2)
        
        # Neo4j (medium-term memory)
        neo4j_data = {
            "nodes": all_entities,
            "relationships": all_relationships
        }
        
        with open(self.output_dir / "neo4j_data.json", 'w') as f:
            json.dump(neo4j_data, f, indent=2)
        
        # PostgreSQL (long-term memory)
        postgresql_data = {
            "files_processed": len(self.critical_files + self.high_priority_files + self.medium_priority_files),
            "entities_extracted": len(all_entities),
            "ingestion_log": {
                "session_id": "direct_ingestion_1753205820",
                "timestamp": datetime.now().isoformat(),
                "method": "direct_file_ingestion",
                "status": "completed"
            }
        }
        
        with open(self.output_dir / "postgresql_data.json", 'w') as f:
            json.dump(postgresql_data, f, indent=2)
        
        # Qdrant (pattern matching)
        qdrant_data = {
            "collection": "new_functionality",
            "chunks": all_chunks
        }
        
        with open(self.output_dir / "qdrant_data.json", 'w') as f:
            json.dump(qdrant_data, f, indent=2)
        
        # Summary report
        summary = {
            "ingestion_summary": {
                "total_files_processed": len([item for sublist in results.values() for item in sublist if item]),
                "total_entities": len(all_entities),
                "total_chunks": len(all_chunks),
                "total_relationships": len(all_relationships),
                "completion_time": datetime.now().isoformat(),
                "status": "SUCCESS"
            },
            "breakdown": {
                "critical_files": len(results["critical"]),
                "high_priority_files": len(results["high_priority"]),
                "medium_priority_files": len(results["medium_priority"])
            }
        }
        
        with open(self.output_dir / "ingestion_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
    
    def run_complete_ingestion(self) -> None:
        """Run the complete direct ingestion process"""
        print("🧠 Direct Functionality Ingestion - AI Task Orchestrator")
        print(f"📁 Output Directory: {self.output_dir}")
        print(f"⏰ Start Time: {datetime.now().isoformat()}")
        
        # Process all files
        results = self.process_all_files()
        
        # Save structured output
        print("\n💾 Saving structured output for database import...")
        self.save_structured_output(results)
        
        print("\n🎉 Direct Functionality Ingestion COMPLETED")
        print("="*60)
        print(f"📊 Output files available in: {self.output_dir}")
        print("🚀 Ready for database import when connectivity is restored")

if __name__ == "__main__":
    ingestor = DirectFunctionalityIngestor()
    ingestor.run_complete_ingestion() 