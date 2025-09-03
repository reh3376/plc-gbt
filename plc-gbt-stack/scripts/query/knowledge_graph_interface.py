#!/usr/bin/env python3
"""
Knowledge Graph Interface for LLM/Agent Access
Provides standardized methods for AI agents to query the PLC-GPT knowledge graph.

This module serves as the primary interface between LLMs/agents and the Neo4j
knowledge graph containing PLC repositories, research articles, and domain knowledge.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import structlog
from neo4j import GraphDatabase

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class PLCKnowledgeGraph:
    """
    Knowledge Graph Interface for LLM/Agent Access

    This class provides standardized methods for AI agents to access the PLC-GPT
    knowledge graph containing repositories, research articles, and domain expertise.

    Available Knowledge Types:
    - GitHub Repositories (PLC tools, libraries, examples)
    - Research Articles (control theory, automation research)
    - PLC Components (routines, AOIs, tags, devices)
    - Technical Documentation (specifications, manuals)
    - Question/Answer pairs from domain experts
    """

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = None
    ):
        """
        Initialize knowledge graph connection.

        Args:
            neo4j_uri: Neo4j database URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password (from environment if not provided)
        """
        if not neo4j_password:
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'your-secure-neo4j-password')

        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        logger.info("Knowledge graph interface initialized")

    def close(self):
        """Close database connection."""
        if self.driver:
            self.driver.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def get_available_knowledge_types(self) -> Dict[str, int]:
        """
        Get count of available knowledge types for LLM awareness.

        Returns:
            Dictionary with knowledge types and counts
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY type
            """)

            knowledge_types = {}
            for record in result:
                knowledge_types[record['type']] = record['count']

        logger.info(f"Available knowledge types: {knowledge_types}")
        return knowledge_types

    def find_plc_repositories(self,
                             language: Optional[str] = None,
                             min_stars: int = 0,
                             limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find PLC-related repositories for LLM context.

        Args:
            language: Programming language filter (e.g., "Python")
            min_stars: Minimum star count
            limit: Maximum results to return

        Returns:
            List of repository information
        """
        query = """
            MATCH (r:GitHubRepo {plc_related: true})
            WHERE r.stars >= $min_stars
        """

        params = {"min_stars": min_stars, "limit": limit}

        if language:
            query += " AND r.language = $language"
            params["language"] = language

        query += """
            RETURN r.name as name, r.full_name as full_name, r.description as description,
                   r.language as language, r.stars as stars, r.url as url,
                   r.topics as topics, r.license as license
            ORDER BY r.stars DESC
            LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, params)
            repositories = [dict(record) for record in result]

        logger.info(f"Found {len(repositories)} PLC repositories")
        return repositories

    def find_research_articles(self,
                              topic_keyword: Optional[str] = None,
                              limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find research articles for LLM knowledge augmentation.

        Args:
            topic_keyword: Search keyword (e.g., "control", "mpc", "automation")
            limit: Maximum results to return

        Returns:
            List of research article information
        """
        query = """
            MATCH (a:ResearchArticle)
            WHERE a.plc_related = true
        """

        params = {"limit": limit}

        if topic_keyword:
            query += " AND (toLower(a.title) CONTAINS toLower($keyword) OR toLower(a.abstract) CONTAINS toLower($keyword))"
            params["keyword"] = topic_keyword

        query += """
            RETURN a.title as title, a.authors as authors, a.abstract as abstract,
                   a.journal as journal, a.publication_date as publication_date,
                   a.url as url, a.source as source
            ORDER BY a.publication_date DESC
            LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, params)
            articles = [dict(record) for record in result]

        logger.info(f"Found {len(articles)} research articles")
        return articles

    def find_plc_components(self,
                           component_type: Optional[str] = None,
                           name_pattern: Optional[str] = None,
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        Find PLC components (AOIs, routines, tags) for technical assistance.

        Args:
            component_type: Type filter ("AOI", "Routine", "Tag", "Device")
            name_pattern: Name pattern to search for
            limit: Maximum results to return

        Returns:
            List of PLC component information
        """
        # Build dynamic query based on component type
        if component_type:
            query = f"MATCH (c:{component_type})"
        else:
            query = "MATCH (c) WHERE c:AOI OR c:Routine OR c:Tag OR c:Device"

        params = {"limit": limit}

        if name_pattern:
            query += " AND toLower(c.name) CONTAINS toLower($pattern)"
            params["pattern"] = name_pattern

        query += """
            RETURN labels(c)[0] as type, c.name as name,
                   c.description as description, properties(c) as properties
            ORDER BY c.name
            LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, params)
            components = [dict(record) for record in result]

        logger.info(f"Found {len(components)} PLC components")
        return components

    def find_domain_expertise(self,
                             question_keyword: Optional[str] = None,
                             min_confidence: float = 0.8,
                             limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find domain expertise from Q&A pairs for LLM knowledge enhancement.

        Args:
            question_keyword: Keyword to search in questions
            min_confidence: Minimum confidence threshold
            limit: Maximum results to return

        Returns:
            List of Q&A pairs with domain expertise
        """
        query = """
            MATCH (qa:QuestionAnswer)
            WHERE qa.confidence >= $min_confidence
        """

        params = {"min_confidence": min_confidence, "limit": limit}

        if question_keyword:
            query += " AND (toLower(qa.question) CONTAINS toLower($keyword) OR toLower(qa.answer) CONTAINS toLower($keyword))"
            params["keyword"] = question_keyword

        query += """
            RETURN qa.question as question, qa.answer as answer,
                   qa.confidence as confidence, qa.source_page as source_page
            ORDER BY qa.confidence DESC
            LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, params)
            expertise = [dict(record) for record in result]

        logger.info(f"Found {len(expertise)} domain expertise entries")
        return expertise

    def get_repository_ecosystem(self, focus_area: str = "communication") -> Dict[str, Any]:
        """
        Get repository ecosystem overview for LLM context building.

        Args:
            focus_area: Area of focus ("communication", "visualization", "control", etc.)

        Returns:
            Ecosystem overview with categorized repositories
        """
        with self.driver.session() as session:
            # Get repositories by language
            lang_result = session.run("""
                MATCH (r:GitHubRepo {plc_related: true})
                RETURN r.language as language, count(r) as count, avg(r.stars) as avg_stars
                ORDER BY count DESC
            """)

            languages = [dict(record) for record in lang_result]

            # Get repositories by focus area
            focus_result = session.run("""
                MATCH (r:GitHubRepo {plc_related: true})
                WHERE toLower(r.description) CONTAINS toLower($focus)
                RETURN r.name as name, r.description as description, r.stars as stars
                ORDER BY r.stars DESC
                LIMIT 10
            """, focus=focus_area)

            focus_repos = [dict(record) for record in focus_result]

            # Get most popular repositories
            popular_result = session.run("""
                MATCH (r:GitHubRepo {plc_related: true})
                RETURN r.name as name, r.stars as stars, r.description as description
                ORDER BY r.stars DESC
                LIMIT 5
            """)

            popular_repos = [dict(record) for record in popular_result]

        ecosystem = {
            "focus_area": focus_area,
            "languages": languages,
            "focus_repositories": focus_repos,
            "popular_repositories": popular_repos,
            "total_repositories": sum(lang['count'] for lang in languages)
        }

        logger.info(f"Retrieved ecosystem overview for {focus_area}")
        return ecosystem

    def search_knowledge_graph(self, search_term: str, limit: int = 15) -> Dict[str, List[Dict]]:
        """
        General search across all knowledge types for LLM queries.

        Args:
            search_term: Term to search for across all content
            limit: Maximum results per category

        Returns:
            Dictionary with categorized search results
        """
        results = {
            "repositories": [],
            "articles": [],
            "components": [],
            "expertise": []
        }

        with self.driver.session() as session:
            # Search repositories
            repo_result = session.run("""
                MATCH (r:GitHubRepo)
                WHERE toLower(r.name) CONTAINS toLower($term)
                   OR toLower(r.description) CONTAINS toLower($term)
                   OR any(topic IN r.topics WHERE toLower(topic) CONTAINS toLower($term))
                RETURN r.name as name, r.description as description, r.stars as stars
                ORDER BY r.stars DESC
                LIMIT $limit
            """, term=search_term, limit=limit)

            results["repositories"] = [dict(record) for record in repo_result]

            # Search articles
            article_result = session.run("""
                MATCH (a:ResearchArticle)
                WHERE toLower(a.title) CONTAINS toLower($term)
                   OR toLower(a.abstract) CONTAINS toLower($term)
                RETURN a.title as title, a.abstract as abstract, a.source as source
                LIMIT $limit
            """, term=search_term, limit=limit)

            results["articles"] = [dict(record) for record in article_result]

            # Search PLC components
            comp_result = session.run("""
                MATCH (c)
                WHERE (c:AOI OR c:Routine OR c:Tag OR c:Device)
                  AND (toLower(c.name) CONTAINS toLower($term)
                       OR toLower(coalesce(c.description, '')) CONTAINS toLower($term))
                RETURN labels(c)[0] as type, c.name as name, c.description as description
                LIMIT $limit
            """, term=search_term, limit=limit)

            results["components"] = [dict(record) for record in comp_result]

            # Search Q&A expertise
            qa_result = session.run("""
                MATCH (qa:QuestionAnswer)
                WHERE toLower(qa.question) CONTAINS toLower($term)
                   OR toLower(qa.answer) CONTAINS toLower($term)
                RETURN qa.question as question, qa.answer as answer, qa.confidence as confidence
                ORDER BY qa.confidence DESC
                LIMIT $limit
            """, term=search_term, limit=limit)

            results["expertise"] = [dict(record) for record in qa_result]

        total_results = sum(len(results[key]) for key in results)
        logger.info(f"Search for '{search_term}' returned {total_results} total results")
        return results


def get_knowledge_graph_summary() -> Dict[str, Any]:
    """
    Get summary of available knowledge for LLM/agent discovery.
    This function can be called by LLMs to understand available resources.

    Returns:
        Summary of available knowledge graph resources
    """
    try:
        with PLCKnowledgeGraph() as kg:
            knowledge_types = kg.get_available_knowledge_types()

            # Get sample data for each type
            sample_repos = kg.find_plc_repositories(limit=3)
            sample_articles = kg.find_research_articles(limit=2)
            ecosystem = kg.get_repository_ecosystem("communication")

            summary = {
                "knowledge_graph_available": True,
                "last_updated": datetime.now().isoformat(),
                "knowledge_types": knowledge_types,
                "capabilities": {
                    "repository_search": "Find PLC tools, libraries, and code examples",
                    "research_access": "Access control theory and automation research",
                    "component_lookup": "Find PLC components (AOIs, routines, tags)",
                    "domain_expertise": "Access Q&A pairs from domain experts",
                    "ecosystem_analysis": "Analyze PLC tool ecosystems"
                },
                "sample_data": {
                    "top_repositories": [r['name'] for r in sample_repos],
                    "research_topics": [a['title'] for a in sample_articles],
                    "programming_languages": [lang['language'] for lang in ecosystem['languages'][:3]]
                },
                "usage_instructions": {
                    "interface": "Use PLCKnowledgeGraph class in scripts/query/knowledge_graph_interface.py",
                    "connection": "bolt://localhost:7687 (Neo4j)",
                    "authentication": "Environment variable NEO4J_PASSWORD required"
                }
            }

        return summary

    except Exception as e:
        logger.error(f"Failed to get knowledge graph summary: {e}")
        return {
            "knowledge_graph_available": False,
            "error": str(e),
            "instructions": "Ensure Neo4j is running: cd plc-gpt-stack && docker-compose up -d"
        }


if __name__ == "__main__":
    # Demo usage for LLM reference
    print("=== PLC Knowledge Graph Interface Demo ===")

    try:
        with PLCKnowledgeGraph() as kg:
            print("\n1. Available Knowledge Types:")
            types = kg.get_available_knowledge_types()
            for ktype, count in types.items():
                print(f"   {ktype}: {count} entries")

            print("\n2. Top PLC Repositories:")
            repos = kg.find_plc_repositories(limit=5)
            for repo in repos:
                print(f"   • {repo['name']} ({repo['stars']}⭐): {repo['description'][:50]}...")

            print("\n3. Research Articles:")
            articles = kg.find_research_articles(limit=3)
            for article in articles:
                print(f"   • {article['title']} ({article['source']})")

            print("\n4. Search Example:")
            results = kg.search_knowledge_graph("communication", limit=3)
            print(f"   Found {len(results['repositories'])} repositories matching 'communication'")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Ensure Neo4j is running: cd plc-gpt-stack && docker-compose up -d")
