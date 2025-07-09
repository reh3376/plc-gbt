# 🧠 PLC-GPT Knowledge Graph - AI Agent Guide

**IMPORTANT FOR LLMs/AI AGENTS**: This project contains a comprehensive Neo4j knowledge graph with PLC domain expertise that you can access programmatically.

## 🎯 Purpose

The PLC-GPT knowledge graph serves as **persistent memory** for AI agents and LLMs operating within this codebase. It contains:

- **9 GitHub Repositories**: PLC tools, libraries, and frameworks (651-2 ⭐ range)
- **2 Research Articles**: Control theory and automation research
- **PLC Components**: AOIs, routines, tags, devices from actual systems
- **Domain Expertise**: Q&A pairs from PLC professionals
- **Technical Documentation**: Specifications and manuals

## 🔌 Access Interface

**Primary Interface**: `plc-gbt-stack/scripts/query/knowledge_graph_interface.py`

```python
from scripts.query.knowledge_graph_interface import PLCKnowledgeGraph, get_knowledge_graph_summary

# Quick availability check
summary = get_knowledge_graph_summary()
print(f"Knowledge graph available: {summary['knowledge_graph_available']}")

# Access the knowledge graph
with PLCKnowledgeGraph() as kg:
    # Find PLC repositories
    repos = kg.find_plc_repositories(language="Python", min_stars=50, limit=5)
    
    # Search for specific topics
    results = kg.search_knowledge_graph("Allen Bradley")
    
    # Get ecosystem overview
    ecosystem = kg.get_repository_ecosystem("communication")
```

## 📊 Available Knowledge Types

| Type | Count | Description |
|------|-------|-------------|
| **GitHubRepo** | 9 | PLC tools and libraries |
| **ResearchArticle** | 2 | Control systems research |
| **AOI** | Variable | Add-On Instructions |
| **Routine** | Variable | PLC program routines |
| **Tag** | Variable | Controller tags |
| **Device** | Variable | I/O modules |
| **QuestionAnswer** | Variable | Domain expertise |

## 🚀 Key Capabilities for AI Agents

### 1. Repository Discovery
```python
# Find the most popular PLC communication libraries
repos = kg.find_plc_repositories(language="Python", min_stars=100)
# Returns: pylogix (651⭐), pycomm3 (445⭐)
```

### 2. Research Access
```python
# Access control theory research
articles = kg.find_research_articles(topic_keyword="control")
# Returns: MPC research papers and control systems studies
```

### 3. Technical Component Lookup
```python
# Find specific PLC components
components = kg.find_plc_components(component_type="AOI", name_pattern="motor")
# Returns: Motor control AOIs and related components
```

### 4. Domain Expertise Queries
```python
# Access expert knowledge
expertise = kg.find_domain_expertise(question_keyword="communication")
# Returns: Q&A pairs about PLC communication protocols
```

### 5. Ecosystem Analysis
```python
# Understand the PLC tool landscape
ecosystem = kg.get_repository_ecosystem("visualization")
# Returns: Analysis of PLC visualization tools and frameworks
```

## 🔍 Search Capabilities

The knowledge graph supports comprehensive search across all data types:

```python
# Search everything for "Rockwell"
results = kg.search_knowledge_graph("Rockwell")
# Returns categorized results: repositories, articles, components, expertise
```

## 🌐 Connection Details

- **Neo4j URI**: `bolt://localhost:7687`
- **Authentication**: Environment variable `NEO4J_PASSWORD`
- **Status Check**: Use `get_knowledge_graph_summary()` to verify availability

## 📈 Repository Ecosystem Highlights

**Top PLC Tools by Popularity:**
1. **pylogix** (651⭐) - Allen Bradley PLC communication
2. **pycomm3** (445⭐) - Ethernet/IP library  
3. **acd** (54⭐) - Rockwell ACD tools
4. **l5x** (50⭐) - RSLogix L5X module
5. **Allen-Bradley-Toolkit** (49⭐) - XML processing toolkit

**Research Areas:**
- Model Predictive Control (MPC)
- Robust control with feedback
- Industrial automation systems

## 🛠 Usage Patterns for AI Agents

### Contextual Repository Recommendations
```python
def recommend_plc_tools(task_description: str):
    with PLCKnowledgeGraph() as kg:
        # Search for relevant tools
        results = kg.search_knowledge_graph(task_description)
        
        # Return top repositories with context
        return {
            'repositories': results['repositories'][:3],
            'research': results['articles'],
            'expertise': results['expertise'][:2]
        }
```

### Technical Problem Solving
```python
def solve_plc_problem(problem_statement: str):
    with PLCKnowledgeGraph() as kg:
        # Find relevant components
        components = kg.find_plc_components(name_pattern=extract_keywords(problem_statement))
        
        # Find similar solved problems
        expertise = kg.find_domain_expertise(question_keyword=extract_keywords(problem_statement))
        
        # Find relevant tools
        tools = kg.find_plc_repositories(limit=5)
        
        return combine_knowledge(components, expertise, tools)
```

### Learning and Research
```python
def research_topic(topic: str):
    with PLCKnowledgeGraph() as kg:
        # Academic research
        articles = kg.find_research_articles(topic_keyword=topic)
        
        # Practical implementations
        repos = kg.search_knowledge_graph(topic)['repositories']
        
        # Expert insights
        qa_pairs = kg.find_domain_expertise(question_keyword=topic)
        
        return create_learning_path(articles, repos, qa_pairs)
```

## ⚡ Quick Start for LLMs

```python
# 1. Check if knowledge graph is available
from scripts.query.knowledge_graph_interface import get_knowledge_graph_summary
summary = get_knowledge_graph_summary()

if summary['knowledge_graph_available']:
    # 2. Access the knowledge graph
    from scripts.query.knowledge_graph_interface import PLCKnowledgeGraph
    
    with PLCKnowledgeGraph() as kg:
        # 3. Query for relevant information
        repos = kg.find_plc_repositories(limit=5)
        articles = kg.find_research_articles(limit=3)
        
        # 4. Use the knowledge in your responses
        print(f"Available PLC tools: {[r['name'] for r in repos]}")
        print(f"Research topics: {[a['title'] for a in articles]}")
```

## 🔄 Data Freshness

- **Last Updated**: Dynamic (check `get_knowledge_graph_summary()`)
- **Repository Data**: Live GitHub API data with stars, descriptions, topics
- **Research Articles**: Semantic Scholar API integration
- **Update Frequency**: On-demand via ETL pipeline

## 🎯 AI Agent Integration Examples

**For Code Generation Tasks**:
- Query repositories for relevant libraries before suggesting implementations
- Reference actual PLC components when generating automation code
- Incorporate research findings for advanced control algorithms

**For Technical Support**:
- Search domain expertise for similar problems
- Recommend specific tools based on user requirements
- Provide context-aware solutions using repository examples

**For Learning and Training**:
- Build comprehensive knowledge from repositories + research + expertise
- Create learning paths that combine theory (articles) with practice (repositories)
- Validate recommendations against actual PLC professional knowledge

## 🚨 Error Handling

Always check availability before use:

```python
try:
    summary = get_knowledge_graph_summary()
    if not summary['knowledge_graph_available']:
        # Fallback to non-graph knowledge
        return use_traditional_knowledge_sources()
except Exception as e:
    # Handle gracefully - knowledge graph is enhancement, not requirement
    logger.warning(f"Knowledge graph unavailable: {e}")
    return provide_basic_response()
```

## 📝 Notes for AI Systems

- **Purpose**: Persistent memory and domain expertise for PLC/automation tasks
- **Scope**: Industrial automation, PLC programming, control systems
- **Reliability**: Local Neo4j instance (requires Docker services)
- **Performance**: Sub-second query response times for most operations
- **Scalability**: Designed for thousands of components and relationships

**Use this knowledge graph to provide more accurate, contextual, and expert-level responses for PLC and industrial automation queries.** 