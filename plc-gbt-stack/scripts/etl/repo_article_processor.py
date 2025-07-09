#!/usr/bin/env python3
"""
Repository and Article Processor
Comprehensive ETL for GitHub repositories and research articles
Version: 1.0.0

This script processes GitHub repositories and research articles,
extracting metadata, content, and relationships for the Neo4j knowledge graph.
"""

import os
import sys
import json
import time
import hashlib
import requests
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import uuid
from datetime import datetime
from urllib.parse import urlparse
import tempfile
import shutil
import re

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import structlog

# Import embedding generator
from embedding_generator import EmbeddingGenerator

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


class RepoArticleProcessor:
    """Process GitHub repositories and research articles for knowledge graph ingestion."""
    
    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        openai_api_key: Optional[str] = None,
        github_token: Optional[str] = None
    ):
        """
        Initialize processor.
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            qdrant_host: Qdrant host
            qdrant_port: Qdrant port
            openai_api_key: OpenAI API key for embeddings
            github_token: GitHub API token for rate limiting
        """
        # Initialize connections
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        
        self.qdrant_client = QdrantClient(
            host=qdrant_host,
            port=qdrant_port
        )
        
        self.openai_api_key = openai_api_key
        self.github_token = github_token
        
        # Initialize embedding generator
        self.embedding_generator = EmbeddingGenerator(api_key=openai_api_key)
        
        # Initialize session for HTTP requests
        self.session = requests.Session()
        if github_token:
            self.session.headers.update({'Authorization': f'token {github_token}'})
            
        # Create temp directory for cloning repos
        self.temp_dir = Path(tempfile.mkdtemp(prefix="plc_repos_"))
        
    def close(self):
        """Close connections and cleanup."""
        if self.neo4j_driver:
            self.neo4j_driver.close()
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def process_github_repository(self, repo_url: str) -> Dict[str, Any]:
        """Process a GitHub repository."""
        logger.info(f"Processing GitHub repository: {repo_url}")
        
        results = {
            'repo_url': repo_url,
            'status': 'started',
            'repo_id': None,
            'neo4j_nodes': 0,
            'embeddings_created': 0,
            'errors': []
        }
        
        try:
            # Extract repository information
            repo_info = self._extract_repo_info(repo_url)
            
            # Create repository node in Neo4j
            repo_id = self._create_repository_node(repo_info)
            results['repo_id'] = repo_id
            results['neo4j_nodes'] += 1
            
            # Create embedding for repository description
            if repo_info.get('description'):
                self._create_repo_embedding(repo_id, repo_info)
                results['embeddings_created'] += 1
            
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Error processing repository: {str(e)}")
            results['status'] = 'failed'
            results['errors'].append(str(e))
            
        return results
        
    def process_research_article(self, article_url: str, title: str = None) -> Dict[str, Any]:
        """Process a research article."""
        logger.info(f"Processing research article: {article_url}")
        
        results = {
            'article_url': article_url,
            'status': 'started',
            'article_id': None,
            'neo4j_nodes': 0,
            'embeddings_created': 0,
            'errors': []
        }
        
        try:
            # Extract article metadata
            article_info = self._extract_article_info(article_url, title)
            
            # Create article node in Neo4j
            article_id = self._create_article_node(article_info)
            results['article_id'] = article_id
            results['neo4j_nodes'] += 1
            
            # Create embedding for article content
            if article_info.get('abstract'):
                self._create_article_embedding(article_id, article_info)
                results['embeddings_created'] += 1
            
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            results['status'] = 'failed'
            results['errors'].append(str(e))
            
        return results

    def _extract_repo_info(self, repo_url: str) -> Dict[str, Any]:
        """Extract repository information from GitHub API."""
        # Parse GitHub URL
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")
            
        owner = path_parts[0]
        repo_name = path_parts[1].replace('.git', '')
        
        # Try GitHub API first
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        
        try:
            response = self.session.get(api_url, timeout=30)
            response.raise_for_status()
            repo_data = response.json()
            
            return {
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'owner': repo_data['owner']['login'],
                'description': repo_data.get('description', ''),
                'url': repo_data['html_url'],
                'language': repo_data.get('language', 'Unknown'),
                'created_at': repo_data['created_at'],
                'updated_at': repo_data['updated_at'],
                'stars': repo_data['stargazers_count'],
                'forks': repo_data['forks_count'],
                'topics': repo_data.get('topics', []),
                'license': repo_data['license']['name'] if repo_data.get('license') else None
            }
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch repo info from API: {e}")
            # Fallback to URL parsing
            return {
                'name': repo_name,
                'full_name': f"{owner}/{repo_name}",
                'owner': owner,
                'description': '',
                'url': repo_url,
                'language': 'Unknown',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'stars': 0,
                'forks': 0,
                'topics': [],
                'license': None
            }

    def _create_repository_node(self, repo_info: Dict[str, Any]) -> str:
        """Create GitHubRepo node in Neo4j."""
        repo_id = str(uuid.uuid4())
        
        # Check if repository is PLC-related
        plc_keywords = ['plc', 'programmable logic controller', 'ladder logic', 'industrial automation',
                       'scada', 'hmi', 'rockwell', 'allen bradley', 'studio 5000', 'rslogix',
                       'l5x', 'acd', 'controllogix', 'automation', 'industrial control']
        
        description_text = f"{repo_info.get('description', '')} {' '.join(repo_info.get('topics', []))}".lower()
        plc_related = any(keyword in description_text for keyword in plc_keywords)
        
        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (r:GitHubRepo {id: $id})
                SET r += $properties
                RETURN r
            """,
            id=repo_id,
            properties={
                'id': repo_id,
                'name': repo_info['name'],
                'full_name': repo_info['full_name'],
                'owner': repo_info['owner'],
                'description': repo_info['description'],
                'url': repo_info['url'],
                'language': repo_info['language'],
                'created_at': repo_info['created_at'],
                'updated_at': repo_info['updated_at'],
                'stars': repo_info['stars'],
                'forks': repo_info['forks'],
                'topics': repo_info['topics'],
                'license': repo_info['license'],
                'plc_related': plc_related,
                'processed_date': datetime.now().isoformat()
            })
            
        logger.info(f"Created GitHubRepo node: {repo_id}")
        return repo_id

    def _create_repo_embedding(self, repo_id: str, repo_info: Dict[str, Any]):
        """Create embedding for repository."""
        try:
            text_content = f"{repo_info['name']} {repo_info['description']} {' '.join(repo_info.get('topics', []))}"
            embedded_content = self.embedding_generator.embed_text(text_content)
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedded_content,
                payload={
                    'content_type': 'GitHubRepo',
                    'repo_id': repo_id,
                    'text': text_content[:1000],
                    'source': 'repository_metadata'
                }
            )
            
            self.qdrant_client.upsert(
                collection_name='document_chunks',
                points=[point]
            )
            
        except Exception as e:
            logger.error(f"Failed to create repo embedding: {e}")

    def _extract_article_info(self, article_url: str, title: str = None) -> Dict[str, Any]:
        """Extract article metadata from URL."""
        article_info = {
            'url': article_url,
            'title': title or 'Research Article',
            'authors': [],
            'abstract': '',
            'publication_date': None,
            'journal': '',
            'source': 'Unknown'
        }
        
        # Detect source from URL and extract info
        if 'semanticscholar.org' in article_url:
            article_info['source'] = 'Semantic Scholar'
            try:
                # Extract paper ID from URL
                if '/paper/' in article_url:
                    paper_id = article_url.split('/paper/')[-1].split('?')[0]
                    api_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,authors,abstract,year,venue"
                    
                    response = self.session.get(api_url, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    article_info['title'] = data.get('title', title or 'Research Article')
                    article_info['abstract'] = data.get('abstract', '')
                    article_info['publication_date'] = str(data.get('year', ''))
                    article_info['journal'] = data.get('venue', '')
                    article_info['authors'] = [author['name'] for author in data.get('authors', [])[:5]]
                    
            except Exception as e:
                logger.warning(f"Failed to extract Semantic Scholar info: {e}")
                
        return article_info

    def _create_article_node(self, article_info: Dict[str, Any]) -> str:
        """Create ResearchArticle node in Neo4j."""
        article_id = str(uuid.uuid4())
        
        # Check if article is PLC/control-related
        plc_concepts = ['model predictive control', 'mpc', 'feedback control', 'automation', 
                       'control system', 'process control', 'industrial control', 'plc']
        
        text_content = f"{article_info['title']} {article_info['abstract']}".lower()
        plc_related = any(concept in text_content for concept in plc_concepts)
        
        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (a:ResearchArticle {id: $id})
                SET a += $properties
                RETURN a
            """,
            id=article_id,
            properties={
                'id': article_id,
                'title': article_info['title'],
                'authors': article_info['authors'],
                'abstract': article_info['abstract'],
                'publication_date': article_info['publication_date'],
                'journal': article_info['journal'],
                'url': article_info['url'],
                'source': article_info['source'],
                'plc_related': plc_related,
                'processed_date': datetime.now().isoformat()
            })
            
        logger.info(f"Created ResearchArticle node: {article_id}")
        return article_id

    def _create_article_embedding(self, article_id: str, article_info: Dict[str, Any]):
        """Create embedding for article."""
        try:
            text_content = f"{article_info['title']}\n\n{article_info['abstract']}"
            embedded_content = self.embedding_generator.embed_text(text_content[:3000])
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedded_content,
                payload={
                    'content_type': 'ResearchArticle',
                    'article_id': article_id,
                    'text': text_content[:1000],
                    'source': 'article_content'
                }
            )
            
            self.qdrant_client.upsert(
                collection_name='document_chunks',
                points=[point]
            )
            
        except Exception as e:
            logger.error(f"Failed to create article embedding: {e}")

    def process_batch(self, items: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process a batch of repositories and articles."""
        results = {
            'total_items': len(items),
            'successful': 0,
            'failed': 0,
            'repositories': [],
            'articles': [],
            'errors': []
        }
        
        for item in items:
            try:
                if item['type'] == 'repo':
                    result = self.process_github_repository(item['url'])
                    results['repositories'].append(result)
                elif item['type'] == 'article':
                    result = self.process_research_article(
                        item['url'], 
                        item.get('title')
                    )
                    results['articles'].append(result)
                else:
                    raise ValueError(f"Unknown item type: {item['type']}")
                    
                if result['status'] == 'completed':
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].extend(result['errors'])
                    
            except Exception as e:
                logger.error(f"Failed to process item {item}: {e}")
                results['failed'] += 1
                results['errors'].append(f"Item {item['url']}: {str(e)}")
                
        return results


def main():
    """Main function for processing the specified repositories and articles."""
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed, using environment variables directly")
    
    # Configuration
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    
    # User-provided repositories
    repositories = [
        "https://github.com/hutcheb/acd.git",
        "https://github.com/jvalenzuela/l5x.git",
        "https://github.com/anubrotoGhose/Rockwell-XML-File-Manipulation.git",
        "https://github.com/cmseaton42/Allen-Bradley-Toolkit.git",
        "https://github.com/dmroeder/pylogix.git",
        "https://github.com/Destination2Unknown/pytunelogix.git",
        "https://github.com/ottowayi/pycomm3.git",
        "https://github.com/jlbcontrols/Flintium.git",
        "https://github.com/pcwii/logixMQTTgateway.git"
    ]
    
    # User-provided articles
    articles = [
        {
            'url': 'https://www.semanticscholar.org/reader/0cdd1a10dee3630b0a0bcf3b13170dea7e1116bd',
            'title': 'Standard MPC'
        },
        {
            'url': 'https://www.semanticscholar.org/paper/Distributionally-Robust-Model-Predictive-Control-Li-Guan/290529061e5ca90d5c62efcd49e91228d08cb03e',
            'title': 'Robust MPC w/ FB'
        }
    ]
    
    # Prepare batch items
    batch_items = []
    
    # Add repositories
    for repo_url in repositories:
        batch_items.append({
            'type': 'repo',
            'url': repo_url
        })
        
    # Add articles
    for article in articles:
        batch_items.append({
            'type': 'article',
            'url': article['url'],
            'title': article['title']
        })
    
    # Process batch
    with RepoArticleProcessor(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        openai_api_key=openai_api_key,
        github_token=github_token
    ) as processor:
        logger.info(f"Starting batch processing of {len(batch_items)} items")
        
        results = processor.process_batch(batch_items)
        
        logger.info("Batch processing complete")
        logger.info(f"Total items: {results['total_items']}")
        logger.info(f"Successful: {results['successful']}")
        logger.info(f"Failed: {results['failed']}")
        
        # Print summary
        print("\n" + "="*60)
        print("PROCESSING SUMMARY")
        print("="*60)
        print(f"Total Items: {results['total_items']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Repositories Processed: {len(results['repositories'])}")
        print(f"Articles Processed: {len(results['articles'])}")
        
        if results['successful'] > 0:
            print("\n✅ SUCCESS: Data has been ingested into Neo4j and Qdrant")
            print("You can now query the knowledge graph for repository and article information.")
        
        if results['errors']:
            print(f"\n⚠️  ERRORS: {len(results['errors'])} errors encountered")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")


if __name__ == "__main__":
    main()
