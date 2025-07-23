"""
Base Test Framework for N8N Integration Tests
Extracted common patterns to reduce complexity
"""

import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    duration: float
    details: str = ""
    error_message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ValidationMetrics:
    """Validation metrics for Phase 26.5"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    overall_score: float = 0.0
    execution_time: float = 0.0

class BaseTestExecutor(ABC):
    """Base class for all test executors"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.test_results: List[TestResult] = []
        
    def add_test_result(self, test_name: str, status: str, duration: float, 
                       details: str = "", error_message: str = ""):
        """Add test result to the collection"""
        result = TestResult(
            test_name=test_name,
            status=status,
            duration=duration,
            details=details,
            error_message=error_message
        )
        self.test_results.append(result)
        logger.info(f"✅ Test {test_name}: {status} ({duration:.2f}s)")
        
    @abstractmethod
    async def execute_tests(self) -> List[TestResult]:
        """Execute all tests in this executor"""
        pass
    
    def get_metrics(self) -> ValidationMetrics:
        """Calculate metrics for this executor"""
        metrics = ValidationMetrics()
        metrics.total_tests = len(self.test_results)
        
        for result in self.test_results:
            if result.status == "PASS":
                metrics.passed_tests += 1
            elif result.status == "FAIL":
                metrics.failed_tests += 1
            elif result.status == "SKIP":
                metrics.skipped_tests += 1
            else:
                metrics.error_tests += 1
                
        if metrics.total_tests > 0:
            metrics.overall_score = metrics.passed_tests / metrics.total_tests
            
        return metrics 