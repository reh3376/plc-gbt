#!/usr/bin/env python3
"""
AI Agent Resource Discovery Module
Simple interface for AI agents to discover available PLC-GPT resources.

Import this module to quickly check what knowledge resources are available
for AI agents operating within the PLC-GPT codebase.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Add scripts to path
sys.path.append(str(Path(__file__).parent / "scripts"))

def get_available_ai_resources() -> Dict[str, Any]:
    """
    Discover all AI resources available in the PLC-GPT project.

    This function provides a complete overview of knowledge and tools
    available to AI agents, including the knowledge graph, documentation,
    and specialized tools.

    Returns:
        Dictionary containing all available AI resources
    """
    resources = {
        "knowledge_graph": {
            "available": False,
            "interface": "scripts/query/knowledge_graph_interface.py",
            "guide": "../docs/AI_KNOWLEDGE_GRAPH_GUIDE.md",
            "connection": "bolt://localhost:7687",
            "description": "Neo4j knowledge graph with PLC domain expertise",
            "types": []
        },
        "documentation": {
            "main_docs": "docs/",
            "roadmap": "docs/roadmap.md",
            "deployment_guide": "docs/plc_gpt_full_guide.md",
            "file_conversion_guide": "docs/plc-file-conversion-howto.md",
            "summaries": "summaries/"
        },
        "tools": {
            "studio5000_integration": "plc-gpt-stack/scripts/etl/studio5000_integration.py",
            "format_compatibility_checker": "plc-gpt-stack/scripts/etl/format_compatibility_checker.py",
            "repo_article_processor": "plc-gpt-stack/scripts/etl/repo_article_processor.py",
            "embedding_generator": "plc-gpt-stack/scripts/etl/embedding_generator.py"
        },
        "services": {
            "neo4j": {"port": 7687, "http_port": 7474, "status": "unknown"},
            "qdrant": {"port": 6333, "status": "unknown"},
            "postgres": {"port": 5432, "status": "unknown"},
            "gateway": {"port": 8000, "status": "unknown"}
        },
        "formats_supported": ["L5X", "ACD", "L5K", "RSS", "APA"],
        "programming_languages": ["Python", "TypeScript", "Cypher"],
        "ai_capabilities": [
            "PLC repository search and analysis",
            "Research article access and synthesis",
            "Technical component lookup",
            "Domain expertise queries",
            "File format conversion",
            "Compatibility validation",
            "Ecosystem analysis"
        ]
    }

    # Check knowledge graph availability
    try:
        from scripts.query.knowledge_graph_interface import get_knowledge_graph_summary
        kg_summary = get_knowledge_graph_summary()

        if kg_summary.get('knowledge_graph_available'):
            resources["knowledge_graph"]["available"] = True
            resources["knowledge_graph"]["types"] = list(kg_summary.get('knowledge_types', {}).keys())
            resources["knowledge_graph"]["last_updated"] = kg_summary.get('last_updated')
            resources["knowledge_graph"]["capabilities"] = kg_summary.get('capabilities', {})
            resources["knowledge_graph"]["sample_data"] = kg_summary.get('sample_data', {})

    except Exception as e:
        resources["knowledge_graph"]["error"] = str(e)
        resources["knowledge_graph"]["instructions"] = "Run: cd plc-gpt-stack && docker-compose up -d"

    return resources


def check_plc_knowledge_available() -> bool:
    """
    Quick check if PLC knowledge graph is available.

    Returns:
        True if knowledge graph is accessible, False otherwise
    """
    try:
        from scripts.query.knowledge_graph_interface import get_knowledge_graph_summary
        summary = get_knowledge_graph_summary()
        return summary.get('knowledge_graph_available', False)
    except Exception:
        return False


def get_plc_repositories(language: str = None, min_stars: int = 0) -> List[Dict[str, Any]]:
    """
    Get PLC repositories from knowledge graph.

    Args:
        language: Programming language filter
        min_stars: Minimum star count

    Returns:
        List of repository information
    """
    try:
        from scripts.query.knowledge_graph_interface import PLCKnowledgeGraph

        with PLCKnowledgeGraph() as kg:
            return kg.find_plc_repositories(language=language, min_stars=min_stars)
    except Exception as e:
        return [{"error": f"Knowledge graph unavailable: {e}"}]


def search_plc_knowledge(query: str) -> Dict[str, List[Dict]]:
    """
    Search across all PLC knowledge.

    Args:
        query: Search term

    Returns:
        Categorized search results
    """
    try:
        from scripts.query.knowledge_graph_interface import PLCKnowledgeGraph

        with PLCKnowledgeGraph() as kg:
            return kg.search_knowledge_graph(query)
    except Exception as e:
        return {"error": [{"message": f"Knowledge graph unavailable: {e}"}]}


def get_tool_recommendations(task_description: str) -> Dict[str, Any]:
    """
    Get tool recommendations for a specific PLC task.

    Args:
        task_description: Description of the task

    Returns:
        Recommended tools and resources
    """
    recommendations = {
        "repositories": [],
        "tools": [],
        "documentation": [],
        "research": []
    }

    task_lower = task_description.lower()

    # Repository recommendations based on task
    try:
        repos = get_plc_repositories()
        for repo in repos:
            if any(keyword in repo.get('description', '').lower() for keyword in task_lower.split()):
                recommendations["repositories"].append({
                    "name": repo.get('name'),
                    "description": repo.get('description'),
                    "stars": repo.get('stars', 0),
                    "url": repo.get('url')
                })
    except Exception:
        pass

    # Tool recommendations
    if "conversion" in task_lower or "format" in task_lower:
        recommendations["tools"].append({
            "name": "Studio 5000 Integration",
            "path": "plc-gpt-stack/scripts/etl/studio5000_integration.py",
            "description": "Convert between ACD and L5X formats"
        })
        recommendations["tools"].append({
            "name": "Format Compatibility Checker",
            "path": "plc-gpt-stack/scripts/etl/format_compatibility_checker.py",
            "description": "Validate format conversions and compatibility"
        })

    # Documentation recommendations
    if "setup" in task_lower or "install" in task_lower:
        recommendations["documentation"].append({
            "name": "Deployment Guide",
            "path": "docs/plc_gpt_full_guide.md",
            "description": "Complete setup and deployment instructions"
        })

    if "conversion" in task_lower:
        recommendations["documentation"].append({
            "name": "File Conversion Guide",
            "path": "docs/plc-file-conversion-howto.md",
            "description": "How to use file conversion tools"
        })

    return recommendations


# Constants for AI agents
PLC_KNOWLEDGE_GRAPH_INTERFACE = "scripts/query/knowledge_graph_interface.py"
AI_AGENT_GUIDE = "../docs/AI_KNOWLEDGE_GRAPH_GUIDE.md"
NEO4J_CONNECTION = "bolt://localhost:7687"

# Quick access functions
def kg_available() -> bool:
    """Alias for check_plc_knowledge_available()"""
    return check_plc_knowledge_available()

def get_kg_summary():
    """Get knowledge graph summary if available"""
    try:
        from scripts.query.knowledge_graph_interface import get_knowledge_graph_summary
        return get_knowledge_graph_summary()
    except Exception:
        return {"knowledge_graph_available": False, "error": "Interface not accessible"}


if __name__ == "__main__":
    # Demo for AI agents
    print("🤖 PLC-GPT AI Agent Resources")
    print("=" * 40)

    resources = get_available_ai_resources()

    print(f"\n📊 Knowledge Graph Available: {resources['knowledge_graph']['available']}")
    if resources['knowledge_graph']['available']:
        print(f"   Types: {len(resources['knowledge_graph']['types'])} knowledge types")
        print(f"   Interface: {resources['knowledge_graph']['interface']}")

    print(f"\n🛠 Tools Available: {len(resources['tools'])} specialized tools")
    for tool_name in resources['tools']:
        print(f"   • {tool_name}")

    print("\n🎯 AI Capabilities:")
    for capability in resources['ai_capabilities']:
        print(f"   • {capability}")

    print("\n💡 Quick Start for AI Agents:")
    print("   import plc-gpt-stack.ai_agent_resources as ai_resources")
    print("   resources = ai_resources.get_available_ai_resources()")
    print("   if ai_resources.kg_available():")
    print("       repos = ai_resources.get_plc_repositories(language='Python')")
    print("       results = ai_resources.search_plc_knowledge('Allen Bradley')")
