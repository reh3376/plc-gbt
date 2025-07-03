# Repository and Article Processor

This script processes GitHub repositories and research articles, extracting metadata, content, and relationships for the Neo4j knowledge graph.

## Features

- **GitHub Repository Processing**: Extracts repository metadata, detects PLC-related content, creates Neo4j nodes
- **Research Article Processing**: Processes academic articles from Semantic Scholar and other sources
- **PLC Content Detection**: Automatically identifies PLC and industrial automation related content
- **Vector Embeddings**: Generates embeddings for content using OpenAI API
- **Batch Processing**: Processes multiple repositories and articles in a single run

## Prerequisites

1. **Database Services Running**:
   ```bash
   cd plc-gpt-stack
   docker-compose up -d
   ```

2. **Environment Variables**:
   ```bash
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USER="neo4j"
   export NEO4J_PASSWORD="your_password"
   export OPENAI_API_KEY="your_openai_key"
   export GITHUB_TOKEN="your_github_token"  # Optional, for higher rate limits
   ```

3. **Neo4j Schema**: Ensure the schema is initialized with the new node types:
   ```bash
   cd ../neo4j
   python3 init_neo4j_schema.py
   ```

## Usage

### Basic Usage
```bash
cd plc-gpt-stack/scripts/etl
python3 repo_article_processor.py
```

This will process all the predefined repositories and articles:

**Repositories:**
- hutcheb/acd - Rockwell ACD Tools
- jvalenzuela/l5x - RSLogix L5X Python module  
- anubrotoGhose/Rockwell-XML-File-Manipulation - L5X/L5K file manipulation
- cmseaton42/Allen-Bradley-Toolkit - Allen Bradley toolkit
- dmroeder/pylogix - PyLogix PLC communication
- Destination2Unknown/pytunelogix - PLC tuning tools
- ottowayi/pycomm3 - PLC communication library
- jlbcontrols/Flintium - Industrial automation framework
- pcwii/logixMQTTgateway - Logix MQTT gateway

**Articles:**
- Standard MPC research
- Distributionally Robust Model Predictive Control

### Testing
```bash
python3 test_repo_article_processor.py
```

## Output

The processor will:
1. Create `GitHubRepo` nodes in Neo4j with repository metadata
2. Create `ResearchArticle` nodes with article information
3. Generate vector embeddings stored in Qdrant
4. Create relationships based on PLC-related content detection
5. Provide detailed processing statistics

## Node Types Created

### GitHubRepo
- Repository metadata (name, owner, description, language, stars, etc.)
- PLC-related classification
- Topics and license information

### ResearchArticle  
- Article metadata (title, authors, abstract, journal, etc.)
- Publication information and source
- PLC/control systems relevance classification

### Concept
- Abstract concepts discussed in articles
- Linked to articles via `DISCUSSES` relationships

## Querying the Data

After processing, you can query the knowledge graph:

```cypher
// Find all PLC-related repositories
MATCH (r:GitHubRepo {plc_related: true})
RETURN r.name, r.description, r.stars
ORDER BY r.stars DESC

// Find Python repositories related to PLCs
MATCH (r:GitHubRepo {plc_related: true, language: "Python"})
RETURN r.full_name, r.description

// Find research articles about model predictive control
MATCH (a:ResearchArticle)
WHERE toLower(a.title) CONTAINS "predictive control"
RETURN a.title, a.authors, a.journal
```

## Configuration

You can modify the script to process additional repositories or articles by editing the lists in the `main()` function.

## Troubleshooting

- **Rate Limiting**: Set `GITHUB_TOKEN` for higher GitHub API limits
- **Network Issues**: The script includes retry logic and fallback mechanisms
- **Missing Dependencies**: Run `pip install neo4j qdrant-client structlog requests`
- **Database Connection**: Ensure Neo4j and Qdrant are running via docker-compose 