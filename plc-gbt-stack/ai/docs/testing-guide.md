# Testing Guide for AI Task Orchestrator

## Overview

This guide provides comprehensive testing strategies, patterns, and utilities for testing AI Task Orchestrator implementations. The orchestrator includes built-in testing utilities to facilitate unit testing, integration testing, and end-to-end testing.

## Testing Philosophy

The AI Task Orchestrator follows these testing principles:

1. **Test at Multiple Levels**: Unit, integration, and end-to-end
2. **Mock External Dependencies**: Isolate components for reliable testing
3. **Use Realistic Test Data**: Test with production-like scenarios
4. **Automate Everything**: CI/CD integration for continuous validation
5. **Performance Matters**: Include performance benchmarks in tests

## Testing Utilities

### Test Fixtures

The orchestrator provides pre-built fixtures for common testing scenarios:

```python
from plc_orchestrator.testing.fixtures import (
    create_test_orchestrator,
    create_test_task,
    create_test_analysis_result,
    create_test_validation_result,
    create_test_memory_adapter
)

# Create a test orchestrator with mock dependencies
orchestrator = create_test_orchestrator(
    enable_memory=True,
    mock_external_apis=True
)

# Create test data
task = create_test_task(
    description="Implement a REST API endpoint",
    complexity="moderate",
    technologies=["python", "fastapi"]
)
```

### Mock Objects

Pre-configured mocks for external services:

```python
from plc_orchestrator.testing.mocks import (
    MockWolframAlphaClient,
    MockOpenAIClient,
    MockMemoryAdapter,
    create_mock_response
)

# Mock WolframAlpha for mathematical validation
mock_wolfram = MockWolframAlphaClient()
mock_wolfram.add_response(
    query="solve x^2 + 2x + 1 = 0",
    response={"solutions": ["-1"], "steps": ["Factor", "Solve"]}
)

# Mock memory operations
mock_memory = MockMemoryAdapter()
await mock_memory.store("task:123", task_data)
```

### Test Helpers

Utility functions for common testing operations:

```python
from plc_orchestrator.testing.helpers import (
    assert_valid_analysis,
    assert_valid_guide,
    compare_implementations,
    generate_test_code,
    measure_performance
)

# Validate analysis result structure
assert_valid_analysis(analysis_result)

# Compare two implementations
differences = compare_implementations(
    original_code,
    optimized_code,
    check_behavior=True
)

# Measure performance
with measure_performance() as perf:
    result = orchestrator.analyze_task(task)
print(f"Analysis took {perf.duration}ms")
```

## Testing Patterns

### 1. Unit Testing

Test individual components in isolation:

```python
import pytest
from unittest.mock import Mock, patch

class TestTaskAnalyzer:
    def test_complexity_calculation(self):
        """Test complexity scoring algorithm"""
        from plc_orchestrator.core.analyzer import TaskAnalyzer
        
        analyzer = TaskAnalyzer()
        
        # Simple task
        simple_result = analyzer._calculate_complexity(
            description="Add two numbers",
            lines_of_code=10
        )
        assert simple_result == "simple"
        
        # Complex task
        complex_result = analyzer._calculate_complexity(
            description="Implement distributed cache with consensus",
            lines_of_code=5000
        )
        assert complex_result == "extensive"
    
    @patch('plc_orchestrator.core.analyzer.detect_technologies')
    def test_technology_detection(self, mock_detect):
        """Test technology detection with mocked NLP"""
        mock_detect.return_value = ["python", "redis", "docker"]
        
        analyzer = TaskAnalyzer()
        result = analyzer.analyze("Build a Redis cache in Python")
        
        assert "python" in result.technologies
        assert "redis" in result.technologies
```

### 2. Integration Testing

Test component interactions:

```python
@pytest.mark.integration
class TestOrchestratorIntegration:
    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator with real memory but mocked APIs"""
        return create_test_orchestrator(
            enable_memory=True,
            memory_backend="redis",
            mock_external_apis=True
        )
    
    async def test_full_task_lifecycle(self, orchestrator):
        """Test complete task flow from analysis to validation"""
        # Create task
        task = "Implement user authentication with JWT"
        
        # Analyze
        analysis = await orchestrator.analyze_task(task)
        assert analysis.status == "completed"
        
        # Generate guide
        guide = await orchestrator.generate_guide(analysis)
        assert len(guide.steps) > 0
        
        # Mock implementation
        implementation = generate_test_code("auth_jwt")
        
        # Validate
        validation = await orchestrator.validate_implementation(
            code=implementation,
            requirements=analysis.requirements
        )
        assert validation.passed
```

### 3. End-to-End Testing

Test complete workflows:

```python
@pytest.mark.e2e
class TestEndToEnd:
    async def test_plc_control_system_workflow(self):
        """Test PLC programming workflow end-to-end"""
        orchestrator = create_orchestrator()
        
        # Real-world PLC task
        task = """
        Create a PLC program for tank level control:
        - Monitor level with ultrasonic sensor
        - Control inlet valve to maintain setpoint
        - Implement high/low alarms
        - Add pump interlock logic
        """
        
        # Full workflow
        analysis = await orchestrator.analyze_task(task)
        guide = await orchestrator.generate_guide(analysis)
        
        # Verify PLC-specific elements
        assert any("ladder logic" in step.description.lower() 
                  for step in guide.steps)
        assert guide.hardware_requirements
        assert guide.safety_considerations
```

### 4. Property-Based Testing

Test with generated inputs:

```python
from hypothesis import given, strategies as st

class TestPropertyBased:
    @given(
        task_description=st.text(min_size=10, max_size=500),
        complexity=st.sampled_from(["simple", "moderate", "complex"]),
        technologies=st.lists(
            st.sampled_from(["python", "javascript", "go", "rust"]),
            min_size=1, max_size=3
        )
    )
    def test_orchestrator_handles_any_valid_input(
        self, task_description, complexity, technologies
    ):
        """Orchestrator should handle any valid task configuration"""
        orchestrator = create_test_orchestrator()
        
        # Should not raise exceptions
        analysis = orchestrator.analyze_task(task_description)
        assert analysis is not None
        assert hasattr(analysis, 'requirements')
```

### 5. Performance Testing

Ensure performance requirements are met:

```python
@pytest.mark.performance
class TestPerformance:
    def test_analysis_performance(self):
        """Analysis should complete within time limits"""
        orchestrator = create_test_orchestrator()
        
        # Test various task sizes
        tasks = [
            ("simple", "Add two numbers", 100),  # 100ms limit
            ("moderate", "Build REST API with 10 endpoints", 500),
            ("complex", "Implement distributed system", 1000),
        ]
        
        for name, task, time_limit in tasks:
            start = time.time()
            result = orchestrator.analyze_task(task)
            duration = (time.time() - start) * 1000
            
            assert duration < time_limit, \
                f"{name} task took {duration}ms (limit: {time_limit}ms)"
    
    def test_memory_usage(self):
        """Check memory usage stays within bounds"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        orchestrator = create_test_orchestrator()
        
        # Process many tasks
        for i in range(100):
            task = f"Implement feature {i}"
            orchestrator.analyze_task(task)
        
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 100, \
            f"Memory increased by {memory_increase}MB"
```

## Testing Memory Components

### Memory Adapter Testing

```python
from plc_orchestrator.testing.helpers import create_memory_test_suite

# Generate comprehensive test suite for custom adapter
class TestCustomMemoryAdapter:
    # Automatically generates standard tests
    test_store_and_retrieve = create_memory_test_suite.store_retrieve
    test_search_functionality = create_memory_test_suite.search
    test_delete_operations = create_memory_test_suite.delete
    test_concurrent_access = create_memory_test_suite.concurrency
    test_error_handling = create_memory_test_suite.errors
    
    @pytest.fixture
    async def adapter(self):
        """Create your custom adapter"""
        return CustomMemoryAdapter(connection_string="...")
```

### Memory Coordinator Testing

```python
class TestMemoryCoordinator:
    async def test_routing_strategy(self):
        """Test memory routing based on strategy"""
        coordinator = MemoryCoordinator(
            strategy="accuracy_optimized"
        )
        
        # Should route to appropriate adapters
        assert coordinator._select_adapter(
            data_type="relationship"
        ) == "neo4j"
        
        assert coordinator._select_adapter(
            data_type="vector"
        ) == "qdrant"
```

## Testing Validation Components

### Validation Testing Patterns

```python
class TestValidation:
    def test_security_validation(self):
        """Test security checks catch vulnerabilities"""
        validator = TaskValidator()
        
        vulnerable_code = """
        user_input = request.get('cmd')
        os.system(user_input)  # Command injection
        """
        
        result = validator.validate(
            vulnerable_code,
            tier=ValidationTier.SECURITY
        )
        
        assert not result.passed
        assert any("injection" in issue.message.lower() 
                  for issue in result.issues)
    
    def test_best_practices_validation(self):
        """Test code quality checks"""
        validator = TaskValidator()
        
        poor_quality_code = """
        def x(a,b,c,d,e,f,g,h,i,j,k):  # Too many parameters
            # No docstring
            if a:
                if b:
                    if c:
                        if d:  # Too deeply nested
                            return e
        """
        
        result = validator.validate(
            poor_quality_code,
            tier=ValidationTier.PRACTICES
        )
        
        assert len(result.issues) >= 3  # Multiple issues
```

## Testing Domain Components

### Control Systems Testing

```python
from plc_orchestrator.testing.helpers import (
    create_plc_test_program,
    simulate_plc_execution
)

class TestControlSystems:
    def test_plc_ladder_logic_generation(self):
        """Test ladder logic generation"""
        analyzer = ControlSystemsAnalyzer()
        
        task = "Create ladder logic for motor start/stop"
        result = analyzer.analyze(task)
        
        assert result.plc_language == "ladder_logic"
        assert "motor_start" in result.generated_tags
        assert "motor_stop" in result.generated_tags
    
    async def test_plc_simulation(self):
        """Test PLC program in simulation"""
        program = create_plc_test_program("motor_control")
        
        # Simulate execution
        simulation = await simulate_plc_execution(
            program,
            inputs={"start_button": True},
            duration_ms=1000
        )
        
        assert simulation.outputs["motor_running"] == True
        assert simulation.scan_time < 50  # ms
```

### Mathematical Testing

```python
class TestMathematical:
    def test_expression_validation(self):
        """Test mathematical expression validation"""
        validator = MathematicalValidator()
        
        valid_expr = "integrate(x^2, x, 0, 1)"
        invalid_expr = "integrate(x^2, x, 0"  # Missing parenthesis
        
        assert validator.validate_expression(valid_expr).valid
        assert not validator.validate_expression(invalid_expr).valid
    
    @pytest.mark.skipif(
        not os.getenv("WOLFRAM_ALPHA_APP_ID"),
        reason="WolframAlpha API key not configured"
    )
    def test_wolfram_integration(self):
        """Test WolframAlpha integration"""
        validator = MathematicalValidator(
            wolfram_app_id=os.getenv("WOLFRAM_ALPHA_APP_ID")
        )
        
        result = validator.wolfram_validate(
            "derivative of sin(x) = cos(x)"
        )
        assert result["valid"] == True
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: AI Task Orchestrator Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
        pip install pytest-cov pytest-xdist
    
    - name: Run unit tests
      run: |
        pytest tests/unit -v --cov=plc_orchestrator
    
    - name: Run integration tests
      env:
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/integration -v
    
    - name: Run performance tests
      run: |
        pytest tests/performance -v --benchmark-only
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: orchestrator-tests
        name: Run orchestrator tests
        entry: pytest tests/unit -x
        language: system
        pass_filenames: false
        always_run: true
        
      - id: type-check
        name: Type checking
        entry: mypy plc_orchestrator
        language: system
        pass_filenames: false
```

## Test Organization

### Directory Structure

```
tests/
├── unit/
│   ├── test_analyzer.py
│   ├── test_validator.py
│   ├── test_orchestrator.py
│   └── test_utils.py
├── integration/
│   ├── test_memory_integration.py
│   ├── test_api_integration.py
│   └── test_workflow_integration.py
├── e2e/
│   ├── test_plc_workflows.py
│   ├── test_math_workflows.py
│   └── test_api_workflows.py
├── performance/
│   ├── test_benchmarks.py
│   └── test_load.py
├── fixtures/
│   ├── sample_tasks.json
│   ├── test_code_samples.py
│   └── mock_responses.json
└── conftest.py
```

### Test Naming Conventions

```python
# Test file naming
test_<module_name>.py

# Test class naming
class Test<ComponentName>:
    pass

# Test method naming
def test_<action>_<expected_result>():
    pass

# Examples:
def test_analyze_task_returns_valid_analysis():
    pass

def test_validate_code_detects_security_issues():
    pass

def test_memory_store_handles_concurrent_writes():
    pass
```

## Debugging Tests

### Using Test Fixtures

```python
# Save test data for debugging
from plc_orchestrator.testing.helpers import save_test_artifact

def test_complex_analysis():
    result = orchestrator.analyze_task(complex_task)
    
    # Save for inspection
    save_test_artifact("analysis_result.json", result)
    
    assert result.status == "completed"
```

### Verbose Logging in Tests

```python
import logging

# Enable debug logging for tests
logging.getLogger("plc_orchestrator").setLevel(logging.DEBUG)

# Or use pytest-logging
pytest -v --log-cli-level=DEBUG
```

### Interactive Debugging

```python
def test_debugging_example():
    # Use breakpoint() for debugging
    result = complex_operation()
    
    if result.unexpected:
        breakpoint()  # Drops into debugger
    
    assert result.valid
```

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Fixtures**: Share common setup code
3. **Mock External Services**: Don't depend on external APIs
4. **Test Edge Cases**: Empty inputs, large inputs, invalid data
5. **Keep Tests Fast**: Mock slow operations
6. **Test Error Paths**: Verify error handling
7. **Use Meaningful Assertions**: Be specific about what failed
8. **Document Complex Tests**: Explain the why, not just the what

## Troubleshooting

### Common Issues

1. **Flaky Tests**: Usually due to timing or external dependencies
   - Solution: Use proper mocking and deterministic test data

2. **Slow Tests**: Often from real I/O operations
   - Solution: Mock file/network operations

3. **Memory Leaks in Tests**: Objects not properly cleaned up
   - Solution: Use fixtures with proper teardown

4. **Import Errors**: Module path issues
   - Solution: Ensure proper PYTHONPATH or use `pip install -e .`

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock guide](https://docs.python.org/3/library/unittest.mock.html)
- [hypothesis for property-based testing](https://hypothesis.works/)
- [pytest-benchmark for performance testing](https://pytest-benchmark.readthedocs.io/)
