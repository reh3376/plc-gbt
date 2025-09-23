# 📚 AI Task Orchestrator - Examples

This directory contains comprehensive examples demonstrating various features and patterns of the AI Task Orchestrator.

## 🎯 Quick Start

Make sure you have the orchestrator installed:
```bash
cd plc-gbt-stack/ai/
pip install -e .
```

Then run any example:
```bash
python examples/01_basic_usage.py
```

## 📖 Available Examples

### 1. [Basic Usage](01_basic_usage.py)
**Learn the fundamentals** of the AI Task Orchestrator:
- Task analysis and complexity assessment
- Implementation guide generation
- Code validation with different tiers
- Production readiness checks
- Control system task handling

**Run it:**
```bash
python examples/01_basic_usage.py
```

### 2. [Memory CRUD Operations](02_memory_crud.py)
**Master the memory system** with CRUD patterns:
- Store task analysis results
- Query for similar tasks
- Update task outcomes
- Batch operations
- Memory routing strategies
- Cleanup patterns

**Requirements:** Redis, Neo4j, and/or PostgreSQL running

**Run it:**
```bash
python examples/02_memory_crud.py
```

### 3. [Error Handling Patterns](03_error_handling.py)
**Build robust applications** with proper error handling:
- Configuration error recovery
- Graceful degradation
- Validation error feedback
- Retry mechanisms with backoff
- Custom error handlers
- Error aggregation and reporting

**Run it:**
```bash
python examples/03_error_handling.py
```

### 4. [Testing Patterns](04_testing_patterns.py)
**Write effective tests** for orchestrator-based code:
- Unit testing with mocks
- Integration testing workflows
- Test factories and builders
- Property-based testing
- Performance testing
- Custom test helpers

**Run it:**
```bash
python examples/04_testing_patterns.py
```

### 5. [Performance Optimization](05_performance_optimization.py)
**Optimize for speed and efficiency**:
- Performance monitoring
- Caching strategies with TTL
- Resource pooling
- Function profiling
- Async concurrency patterns
- Batch processing techniques

**Run it:**
```bash
python examples/05_performance_optimization.py
```

## 🏃‍♂️ Running All Examples

To run all examples in sequence:
```bash
cd examples/
for example in *.py; do
    echo "Running $example..."
    python "$example"
    echo
done
```

## 🧩 Example Categories

### Getting Started
- **Start with:** `01_basic_usage.py`
- **Focus:** Core concepts and basic workflows

### Advanced Features
- **Memory System:** `02_memory_crud.py`
- **Error Handling:** `03_error_handling.py`
- **Performance:** `05_performance_optimization.py`

### Development Practices
- **Testing:** `04_testing_patterns.py`
- **Error Handling:** `03_error_handling.py`

## 💡 Tips for Using Examples

1. **Read the Code**: Each example is heavily commented to explain concepts
2. **Modify and Experiment**: Try changing task descriptions and parameters
3. **Check Output**: Examples print detailed information about what's happening
4. **Enable Debug Logging**: Set `LOG_LEVEL=DEBUG` for more details
5. **Use in Your Code**: Copy patterns from examples into your applications

## 🔧 Configuration

Examples use minimal configuration by default. To enable advanced features:

1. **Memory System**: Start Redis/Neo4j/PostgreSQL and update connection strings
2. **Math Validation**: Set `WOLFRAM_ALPHA_API_KEY` environment variable
3. **Production Checks**: Set `ENABLE_PRODUCTION_CHECKS=true`

Create a `.env` file in the `ai/` directory:
```env
# Memory system
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687
POSTGRES_DSN=postgresql://user:pass@localhost:5432/orchestrator

# Features
ENABLE_MEMORY=true
ENABLE_PRODUCTION_CHECKS=true
WOLFRAM_ALPHA_API_KEY=your_key_here

# Performance
MAX_WORKERS=4
CACHE_TTL=3600
```

## 📊 Example Complexity Guide

| Example | Complexity | Prerequisites | Key Concepts |
|---------|------------|---------------|---------------|
| 01_basic_usage | ⭐ Beginner | None | Task analysis, validation |
| 03_error_handling | ⭐⭐ Intermediate | None | Error recovery, retries |
| 04_testing_patterns | ⭐⭐ Intermediate | pytest knowledge | Mocking, fixtures |
| 02_memory_crud | ⭐⭐⭐ Advanced | Memory systems | Async, CRUD |
| 05_performance | ⭐⭐⭐ Advanced | Async Python | Caching, profiling |

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure orchestrator is installed
cd ../  # Go to ai/ directory
pip install -e .
```

### Memory System Not Available
```bash
# Start Redis (example)
docker run -d -p 6379:6379 redis:latest

# Or disable memory in examples
# Change: enable_memory=True
# To: enable_memory=False
```

### Performance Issues
- Disable memory system for faster execution
- Reduce task complexity in examples
- Use caching examples to speed up repeated operations

## 🚀 Next Steps

After exploring these examples:

1. **Read the Guides**: Check out the comprehensive guides in the docs
2. **Build Something**: Start with a simple task orchestration project
3. **Contribute**: Add your own examples for specific use cases
4. **Optimize**: Use performance patterns in production code

## 📝 Contributing Examples

To add a new example:

1. Follow the naming pattern: `XX_feature_name.py`
2. Include comprehensive docstrings
3. Add error handling
4. Print clear output
5. Update this README

Example template:
```python
#!/usr/bin/env python3
"""
Brief description of what this example demonstrates.

This example shows:
1. Feature one
2. Feature two
3. Feature three
"""

def main():
    """Run the example."""
    print("\n🎯 Example Title")
    print("=" * 50)
    
    # Your example code here
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()
```

---

Happy orchestrating! 🎭
