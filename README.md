# PLC-Savvy GPT

> A specialized GPT system for industrial automation and PLC programming expertise.

## 📚 Documentation

All project documentation has been organized into the following directories:

- **[Project Documentation](docs/)** - Contains all project documentation
  - [Full README](docs/README.md) - Detailed project overview and setup instructions
  - [Deployment Guide](docs/plc_gpt_full_guide.md) - Complete deployment handbook
  - [Implementation Roadmap](docs/roadmap.md) - Project timeline and task tracking

- **[Summaries](summaries/)** - Task completion summaries and progress reports

## 🚀 Quick Start

1. See the [Full README](docs/README.md) for detailed setup instructions
2. Check the [Roadmap](docs/roadmap.md) for current project status
3. Follow the [Deployment Guide](docs/plc_gpt_full_guide.md) for implementation details

## 🧠 Knowledge Graph for AI Agents

**For LLMs and AI Agents**: This project includes a comprehensive Neo4j knowledge graph containing PLC domain expertise that serves as persistent memory for AI systems.

**📊 Available Knowledge**:
- 9 GitHub repositories (PLC tools and libraries)
- 2 research articles (control theory and automation)
- PLC components (AOIs, routines, tags, devices)
- Domain expertise (Q&A pairs from professionals)

**🔌 Access Interface**: [`plc-gpt-stack/scripts/query/knowledge_graph_interface.py`](plc-gpt-stack/scripts/query/knowledge_graph_interface.py)

**📖 AI Agent Guide**: [`plc-gpt-stack/docs/AI_KNOWLEDGE_GRAPH_GUIDE.md`](plc-gpt-stack/docs/AI_KNOWLEDGE_GRAPH_GUIDE.md)

```python
# Quick availability check for AI systems
from scripts.query.knowledge_graph_interface import get_knowledge_graph_summary
summary = get_knowledge_graph_summary()
print(f"Knowledge graph available: {summary['knowledge_graph_available']}")
```

## 🤖 AI Task Orchestrator

**For AI Agents**: Structured framework for systematic coding task completion with built-in validation and hallucination prevention.

**🎯 Key Features**:
- Task analysis and complexity assessment
- Resource discovery and planning
- Context management for large tasks
- Syntax validation and hallucination detection
- Integration with knowledge graph and tools

**🔧 Task Orchestrator**: [`plc-gpt-stack/ai/ai_task_orchestrator.py`](plc-gpt-stack/ai/ai_task_orchestrator.py)

**📋 Usage Guide**: [`plc-gpt-stack/docs/AI_TASK_ORCHESTRATOR_GUIDE.md`](plc-gpt-stack/docs/AI_TASK_ORCHESTRATOR_GUIDE.md)

```python
# Quick task guidance for AI systems
from plc_gpt_stack.ai.ai_task_orchestrator import get_task_guidance, validate_task_completion

# Get structured guidance
guidance = get_task_guidance("Create a Python script to parse L5X files")

# Validate completed code
validation = validate_task_completion(code_content, requirements)
print(f"Validation Score: {validation['score']}%")
```

## 🔗 Repository

https://github.com/reh3376/plc-gpt_build

---

*For complete documentation, please see the [docs](docs/) directory.* 