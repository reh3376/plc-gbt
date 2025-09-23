#!/usr/bin/env python3
"""
Performance optimization examples for the AI Task Orchestrator.

This example demonstrates:
1. Using performance monitoring
2. Caching strategies
3. Resource pooling
4. Profiling and optimization
5. Async performance patterns
"""

import asyncio
import time
from typing import Any

from plc_orchestrator import create_orchestrator
from plc_orchestrator.utils.performance import (
    PerformanceMonitor,
    ResourcePool,
    cache_result,
    global_monitor,
    profile,
)
from plc_orchestrator.utils.retry import retry


class PerformanceExamples:
    """Examples of performance optimization patterns."""

    def __init__(self):
        """Initialize with orchestrator and monitor."""
        self.orchestrator = create_orchestrator(
            enable_memory=False,  # Disable for consistent benchmarks
            max_workers=4,
        )
        self.monitor = PerformanceMonitor()

    def example_performance_monitoring(self):
        """Example: Monitor operation performance."""
        print("\n" + "=" * 60)
        print("Example 1: Performance Monitoring")
        print("=" * 60)

        # Monitor different operations
        tasks = [
            ("Simple task", "Create a hello world function"),
            ("Medium task", "Build REST API with authentication"),
            (
                "Complex task",
                "Design distributed system with microservices, message queues, and monitoring",
            ),
        ]

        print("\n1. Monitoring task analysis performance:")

        for name, description in tasks:
            with self.monitor.measure(f"analyze_{name}", {"length": len(description)}):
                analysis = self.orchestrator.analyze_task(description)
                print(f"  ✓ {name}: {analysis.complexity} ({analysis.estimated_effort['hours']}h)")

        # Get performance summary
        summary = self.monitor.get_summary()
        print("\n📊 Performance Summary:")
        for operation, metrics in summary.items():
            print(f"\n  {operation}:")
            print(f"    - Count: {metrics['count']}")
            print(f"    - Average: {metrics['average_time']:.3f}s")
            print(f"    - Min/Max: {metrics['min_time']:.3f}s / {metrics['max_time']:.3f}s")

    def example_caching_strategies(self):
        """Example: Implement caching for expensive operations."""
        print("\n" + "=" * 60)
        print("Example 2: Caching Strategies")
        print("=" * 60)

        # Create cached version of task analysis
        @cache_result(max_size=50, ttl=300)  # Cache 50 items for 5 minutes
        def cached_analyze_task(description: str) -> dict[str, Any]:
            """Cached task analysis."""
            analysis = self.orchestrator.analyze_task(description)
            return {
                "complexity": analysis.complexity,
                "hours": analysis.estimated_effort["hours"],
                "requirements": len(analysis.requirements),
            }

        # Test caching
        print("\n2. Testing cache performance:")
        test_task = "Create user authentication system with JWT"

        # First call - cache miss
        start = time.perf_counter()
        result1 = cached_analyze_task(test_task)
        time1 = time.perf_counter() - start
        print(f"  First call (cache miss): {time1:.3f}s")
        print(f"    Result: {result1}")

        # Second call - cache hit
        start = time.perf_counter()
        result2 = cached_analyze_task(test_task)
        time2 = time.perf_counter() - start
        print(f"\n  Second call (cache hit): {time2:.3f}s")
        print(f"    Speedup: {time1 / time2:.1f}x")

        # Cache statistics
        stats = cached_analyze_task.cache_stats()
        print("\n  Cache Statistics:")
        print(f"    - Hit rate: {stats['hit_rate']:.1%}")
        print(f"    - Size: {stats['size']}/{stats['max_size']}")

        # Example: Custom cache key
        @cache_result(key_func=lambda desc, tier: f"{desc[:20]}:{tier}")
        def cached_validate(description: str, tier: str = "basic") -> bool:
            """Cached validation with custom key."""
            # Simulate expensive validation
            time.sleep(0.1)
            return len(description) > 10

        print("\n2b. Custom cache key example:")
        cached_validate("Short", "basic")
        cached_validate("Short", "advanced")  # Different tier = different cache entry
        cached_validate("Short", "basic")  # Cache hit

        stats = cached_validate.cache_stats()
        print(f"  Custom cache entries: {stats['size']}")

    async def example_resource_pooling(self):
        """Example: Use resource pooling for expensive resources."""
        print("\n" + "=" * 60)
        print("Example 3: Resource Pooling")
        print("=" * 60)

        # Simulate expensive resource (e.g., database connection)
        class ExpensiveResource:
            """Simulated expensive resource."""

            def __init__(self, resource_id: int):
                self.id = resource_id
                self.created_at = time.time()
                print(f"  🔧 Creating expensive resource #{resource_id}")
                time.sleep(0.1)  # Simulate creation cost

            async def execute(self, query: str) -> str:
                """Execute operation on resource."""
                await asyncio.sleep(0.05)  # Simulate work
                return f"Result from resource #{self.id}: {query}"

        # Create resource pool
        resource_counter = 0

        def resource_factory():
            nonlocal resource_counter
            resource_counter += 1
            return ExpensiveResource(resource_counter)

        pool = ResourcePool(factory=resource_factory, max_size=3, timeout=5.0)

        print("\n3. Testing resource pool:")

        # Use resources concurrently
        async def use_resource(task_id: int):
            resource = await pool.acquire()
            try:
                result = await resource.execute(f"Task {task_id}")
                print(f"  ✓ {result}")
                await asyncio.sleep(0.1)  # Simulate work
            finally:
                await pool.release(resource)

        # Run concurrent tasks
        print("\n  Running 6 tasks with pool size 3:")
        tasks = [use_resource(i) for i in range(6)]
        await asyncio.gather(*tasks)

        print(f"\n  Resources created: {resource_counter} (pool reused resources)")

    def example_profiling(self):
        """Example: Profile function performance."""
        print("\n" + "=" * 60)
        print("Example 4: Profiling and Optimization")
        print("=" * 60)

        # Profile different implementations
        @profile
        def slow_implementation(data: list[int]) -> int:
            """Inefficient implementation."""
            result = 0
            for i in range(len(data)):
                for j in range(i):
                    result += data[i] * data[j]
            return result

        @profile
        def optimized_implementation(data: list[int]) -> int:
            """Optimized implementation."""
            # Use vectorized operations (simulated)
            import itertools

            pairs = itertools.combinations(enumerate(data), 2)
            return sum(data[i] * data[j] for i, j in pairs)

        # Test with data
        test_data = list(range(100))

        print("\n4. Profiling implementations:")
        print("\n  Slow implementation:")
        slow_result = slow_implementation(test_data)

        print("\n  Optimized implementation:")
        fast_result = optimized_implementation(test_data)

        print(f"\n  Results match: {slow_result == fast_result}")

    async def example_async_performance(self):
        """Example: Async performance patterns."""
        print("\n" + "=" * 60)
        print("Example 5: Async Performance Patterns")
        print("=" * 60)

        # Pattern 1: Concurrent execution
        print("\n5a. Concurrent vs Sequential:")

        async def analyze_task_async(description: str) -> str:
            """Simulate async task analysis."""
            await asyncio.sleep(0.5)  # Simulate work
            return f"Analyzed: {description[:20]}..."

        tasks = [
            "Create REST API",
            "Build authentication",
            "Design database schema",
            "Implement caching",
        ]

        # Sequential execution
        start = time.perf_counter()
        sequential_results = []
        for task in tasks:
            result = await analyze_task_async(task)
            sequential_results.append(result)
        sequential_time = time.perf_counter() - start
        print(f"  Sequential: {sequential_time:.2f}s")

        # Concurrent execution
        start = time.perf_counter()
        concurrent_results = await asyncio.gather(*[analyze_task_async(task) for task in tasks])
        concurrent_time = time.perf_counter() - start
        print(f"  Concurrent: {concurrent_time:.2f}s")
        print(f"  Speedup: {sequential_time / concurrent_time:.1f}x")

        # Pattern 2: Semaphore for rate limiting
        print("\n5b. Rate limiting with semaphore:")

        semaphore = asyncio.Semaphore(2)  # Max 2 concurrent

        async def rate_limited_task(task_id: int):
            async with semaphore:
                print(f"  → Task {task_id} started")
                await asyncio.sleep(0.5)
                print(f"  ← Task {task_id} completed")
                return f"Result {task_id}"

        # Run 6 tasks with max 2 concurrent
        await asyncio.gather(*[rate_limited_task(i) for i in range(6)])

        # Pattern 3: Timeout handling
        print("\n5c. Timeout handling:")

        @retry(max_attempts=2, initial_delay=0.1)
        async def flaky_operation():
            """Operation that might timeout."""
            await asyncio.sleep(0.3)
            return "Success"

        try:
            result = await asyncio.wait_for(flaky_operation(), timeout=1.0)
            print(f"  ✓ Operation completed: {result}")
        except TimeoutError:
            print("  ❌ Operation timed out")

    def example_optimization_techniques(self):
        """Example: Common optimization techniques."""
        print("\n" + "=" * 60)
        print("Example 6: Optimization Techniques")
        print("=" * 60)

        # Technique 1: Batch processing
        print("\n6a. Batch processing:")

        def process_single(item: str) -> str:
            """Process single item (slow)."""
            time.sleep(0.01)  # Simulate work
            return item.upper()

        def process_batch(items: list[str]) -> list[str]:
            """Process batch of items (fast)."""
            time.sleep(0.02)  # Simulate batch overhead
            return [item.upper() for item in items]

        test_items = [f"item{i}" for i in range(20)]

        # Single processing
        start = time.perf_counter()
        single_results = [process_single(item) for item in test_items]
        single_time = time.perf_counter() - start

        # Batch processing
        start = time.perf_counter()
        batch_results = process_batch(test_items)
        batch_time = time.perf_counter() - start

        print(f"  Single processing: {single_time:.3f}s")
        print(f"  Batch processing: {batch_time:.3f}s")
        print(f"  Speedup: {single_time / batch_time:.1f}x")

        # Technique 2: Early termination
        print("\n6b. Early termination optimization:")

        def find_complex_task(tasks: list[str]) -> str | None:
            """Find first complex task (with early termination)."""
            for task in tasks:
                with global_monitor.measure("task_check"):
                    analysis = self.orchestrator.analyze_task(task)
                    if analysis.complexity == "complex":
                        return task
            return None

        test_tasks = [
            "Simple function",
            "Add two numbers",
            "Build distributed microservices architecture with Kubernetes",
            "Create hello world",  # Won't be checked due to early termination
        ]

        found = find_complex_task(test_tasks)
        print(f"  Found complex task: {found[:40]}...")
        print(f"  Tasks checked: {global_monitor.metrics['task_check']['count']}")

    async def run_all_examples(self):
        """Run all performance examples."""
        self.example_performance_monitoring()
        self.example_caching_strategies()
        await self.example_resource_pooling()
        self.example_profiling()
        await self.example_async_performance()
        self.example_optimization_techniques()


async def main():
    """Run performance optimization examples."""
    print("\n⚡ AI Task Orchestrator - Performance Optimization")
    print("=================================================")

    examples = PerformanceExamples()
    await examples.run_all_examples()

    print("\n\n✅ Performance examples completed!")
    print("\nKey Techniques Demonstrated:")
    print("  - Performance monitoring and measurement")
    print("  - Result caching with TTL and custom keys")
    print("  - Resource pooling for expensive resources")
    print("  - Function profiling with timing and memory")
    print("  - Async concurrency patterns")
    print("  - Batch processing and early termination")
    print("\nBest Practices:")
    print("  - Measure before optimizing")
    print("  - Cache expensive computations")
    print("  - Pool reusable resources")
    print("  - Use async for I/O bound operations")
    print("  - Batch operations when possible")
    print("  - Implement early termination")


if __name__ == "__main__":
    asyncio.run(main())
