#!/usr/bin/env python3
"""
Enhanced Model Validation Suite
==============================

Comprehensive testing framework to validate the enhanced fine-tuned model's
understanding of PLC-GBT codebase functionality.

Tests the model's ability to:
1. Understand codebase architecture and structure
2. Provide accurate CLI command guidance  
3. Explain API endpoint usage
4. Demonstrate function and class knowledge
5. Show integration pattern understanding
6. Provide configuration and usage examples

Author: AI Task Orchestrator
Date: July 22, 2025
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import requests
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestCategory(Enum):
    """Test categories for enhanced model validation"""
    ARCHITECTURE = "architecture"
    CLI_COMMANDS = "cli_commands" 
    API_ENDPOINTS = "api_endpoints"
    FUNCTIONS = "functions"
    CLASSES = "classes"
    INTEGRATIONS = "integrations"
    CONFIGURATION = "configuration"
    WORKFLOWS = "workflows"

class ValidationLevel(Enum):
    """Validation strictness levels"""
    BASIC = "basic"           # Keywords present, basic structure
    INTERMEDIATE = "intermediate"  # Accurate details, proper examples
    ADVANCED = "advanced"     # Complete accuracy, expert-level responses
    EXPERT = "expert"         # Perfect responses with deep insights

@dataclass
class TestCase:
    """Individual test case for model validation"""
    id: str
    category: TestCategory
    question: str
    expected_keywords: List[str]
    expected_elements: List[str]
    validation_level: ValidationLevel
    scoring_criteria: Dict[str, int]
    description: str

@dataclass
class TestResult:
    """Results from a single test case"""
    test_id: str
    question: str
    response: str
    score: float
    max_score: float
    passed: bool
    keywords_found: List[str]
    keywords_missing: List[str]
    elements_found: List[str]
    elements_missing: List[str]
    response_time: float
    validation_notes: str

class EnhancedModelValidator:
    """Main validation framework for enhanced model testing"""
    
    def __init__(self, model_id: str, api_key: Optional[str] = None):
        self.model_id = model_id
        self.api_key = api_key or self._load_api_key()
        self.client = OpenAI(api_key=self.api_key)
        
        # Test cases
        self.test_cases = self._initialize_test_cases()
        
        # Results tracking
        self.test_results: List[TestResult] = []
        self.category_scores: Dict[TestCategory, float] = {}
        
        logger.info(f"Initialized Enhanced Model Validator for: {model_id}")

    def _load_api_key(self) -> str:
        """Load API key from environment or .env file"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            # Try multiple possible .env locations
            env_paths = [
                Path(__file__).parent.parent.parent / '.env',
                Path(__file__).parent.parent / '.env',
                Path(__file__).parent / '.env',
                Path.cwd() / '.env'
            ]
            
            for env_file in env_paths:
                if env_file.exists():
                    with open(env_file, 'r') as f:
                        for line in f:
                            if line.startswith('OPENAI_API_KEY='):
                                api_key = line.split('=', 1)[1].strip().strip('"\'')
                                break
                    if api_key:
                        break
        
        if not api_key:
            # Fallback to prompting user
            print("OpenAI API key not found in environment variables or .env file.")
            api_key = input("Please enter your OpenAI API key: ").strip()
            
        if not api_key:
            raise ValueError("OpenAI API key is required to run model validation.")
        
        return api_key

    def _initialize_test_cases(self) -> List[TestCase]:
        """Initialize comprehensive test cases for validation"""
        
        test_cases = []
        
        # Architecture Tests
        test_cases.extend([
            TestCase(
                id="arch_001",
                category=TestCategory.ARCHITECTURE,
                question="Explain the multi-database architecture in PLC-GBT and how the four databases work together",
                expected_keywords=["Redis", "Neo4j", "PostgreSQL", "Qdrant", "memory", "architecture", "coordination"],
                expected_elements=["short-term memory", "medium-term memory", "long-term memory", "pattern matching"],
                validation_level=ValidationLevel.ADVANCED,
                scoring_criteria={"keywords": 30, "structure": 25, "accuracy": 25, "examples": 20},
                description="Test understanding of core multi-database architecture"
            ),
            TestCase(
                id="arch_002", 
                category=TestCategory.ARCHITECTURE,
                question="How does the modular architecture work in PLC-GBT? What are the main modules?",
                expected_keywords=["modular", "BaseOrchestrator", "DatabaseManager", "core.py", "metrics.py", "data.py"],
                expected_elements=["modules.core", "modules.metrics", "modules.data", "modules.analysis", "modules.integration"],
                validation_level=ValidationLevel.INTERMEDIATE,
                scoring_criteria={"keywords": 25, "modules": 30, "usage": 25, "benefits": 20},
                description="Test understanding of modular architecture design"
            )
        ])
        
        # CLI Command Tests
        test_cases.extend([
            TestCase(
                id="cli_001",
                category=TestCategory.CLI_COMMANDS,
                question="How do I create a new PID control loop instance using plc-cl CLI?",
                expected_keywords=["plc-cl", "instance", "create", "schema", "standard-pid", "--name"],
                expected_elements=["plc-cl instance create", "--schema=", "--name=", "PID", "control loop"],
                validation_level=ValidationLevel.INTERMEDIATE,
                scoring_criteria={"command": 40, "options": 30, "example": 20, "context": 10},
                description="Test CLI command knowledge for instance creation"
            ),
            TestCase(
                id="cli_002",
                category=TestCategory.CLI_COMMANDS, 
                question="What are the main plc-memory CLI commands for managing the memory system?",
                expected_keywords=["plc-memory", "query", "ingest", "status", "health", "backup", "optimize"],
                expected_elements=["plc-memory query", "plc-memory ingest", "plc-memory status", "multi-database"],
                validation_level=ValidationLevel.BASIC,
                scoring_criteria={"commands": 40, "descriptions": 30, "examples": 20, "context": 10},
                description="Test knowledge of memory management CLI commands"
            )
        ])
        
        # API Endpoint Tests  
        test_cases.extend([
            TestCase(
                id="api_001",
                category=TestCategory.API_ENDPOINTS,
                question="How do I use the API bridge to connect to a PLC programmatically?",
                expected_keywords=["API bridge", "requests.post", "/api/v1/cli/plc/connect", "host", "slot"],
                expected_elements=["http://127.0.0.1:8080", "json payload", "response.json()", "success"],
                validation_level=ValidationLevel.INTERMEDIATE,
                scoring_criteria={"endpoint": 30, "payload": 25, "example": 25, "response": 20},
                description="Test API endpoint usage knowledge"
            ),
            TestCase(
                id="api_002",
                category=TestCategory.API_ENDPOINTS,
                question="What's the difference between specific API endpoints and the generic execute endpoint?",
                expected_keywords=["specific endpoints", "generic execute", "/api/v1/cli/execute", "type safety", "flexibility"],
                expected_elements=["structured request", "parameter validation", "full flexibility", "CLI command"],
                validation_level=ValidationLevel.ADVANCED,
                scoring_criteria={"comparison": 30, "advantages": 25, "examples": 25, "use_cases": 20},
                description="Test understanding of API design patterns"
            )
        ])
        
        # Function Tests
        test_cases.extend([
            TestCase(
                id="func_001",
                category=TestCategory.FUNCTIONS,
                question="How do I use the BaseOrchestrator class in my PLC-GBT applications?",
                expected_keywords=["BaseOrchestrator", "modules.core", "super().__init__", "infrastructure", "logging"],
                expected_elements=["class inheritance", "automatic setup", "database connections", "configuration"],
                validation_level=ValidationLevel.INTERMEDIATE,
                scoring_criteria={"usage": 30, "benefits": 25, "example": 25, "inheritance": 20},
                description="Test understanding of core framework classes"
            ),
            TestCase(
                id="func_002",
                category=TestCategory.FUNCTIONS,
                question="How does the MemoryCoordinator work for intelligent query routing?",
                expected_keywords=["MemoryCoordinator", "query routing", "QueryStrategy", "INTELLIGENT", "memory tiers"],
                expected_elements=["query strategy", "database selection", "intelligent routing", "4-tier architecture"],
                validation_level=ValidationLevel.ADVANCED,
                scoring_criteria={"mechanism": 30, "strategies": 25, "examples": 25, "architecture": 20},
                description="Test understanding of memory coordination functionality"
            )
        ])
        
        # Integration Tests
        test_cases.extend([
            TestCase(
                id="integ_001",
                category=TestCategory.INTEGRATIONS,
                question="How does WolframAlpha Pro integration work in PLC-GBT for mathematical validation?",
                expected_keywords=["WolframAlpha Pro", "mathematical validation", "WolframAlphaProClient", "control theory"],
                expected_elements=["validate_mathematical_claim", "99.99% accuracy", "educational derivations"],
                validation_level=ValidationLevel.ADVANCED,
                scoring_criteria={"integration": 30, "features": 25, "accuracy": 25, "examples": 20},
                description="Test understanding of external service integrations"
            ),
            TestCase(
                id="integ_002",
                category=TestCategory.INTEGRATIONS,
                question="What N8N workflow automation capabilities are available in PLC-GBT?",
                expected_keywords=["N8N", "workflow automation", "custom nodes", "PLC Memory Node", "industrial protocols"],
                expected_elements=["PLC Memory Node", "OPC-UA", "Modbus", "EtherNet/IP", "namespace isolation"],
                validation_level=ValidationLevel.INTERMEDIATE,
                scoring_criteria={"nodes": 30, "protocols": 25, "capabilities": 25, "isolation": 20},
                description="Test knowledge of workflow automation integration"
            )
        ])
        
        # Configuration Tests
        test_cases.extend([
            TestCase(
                id="config_001",
                category=TestCategory.CONFIGURATION,
                question="How do I configure PLC-GBT for my environment? What are the key configuration variables?",
                expected_keywords=["configuration", ".env", "OPENAI_API_KEY", "DATABASE", "PLC_DEFAULT_HOST"],
                expected_elements=["environment variables", "database connections", "PLC integration", "security"],
                validation_level=ValidationLevel.BASIC,
                scoring_criteria={"setup": 30, "variables": 30, "examples": 25, "security": 15},
                description="Test understanding of system configuration"
            )
        ])
        
        # Workflow Tests
        test_cases.extend([
            TestCase(
                id="workflow_001",
                category=TestCategory.WORKFLOWS,
                question="Show me a complete workflow for setting up temperature control in PLC-GBT",
                expected_keywords=["temperature control", "schema create", "instance create", "PLC connect", "tune"],
                expected_elements=["plc-cl schema create", "plc-cl instance create", "plc-cl instance plc connect", "monitoring"],
                validation_level=ValidationLevel.EXPERT,
                scoring_criteria={"completeness": 30, "sequence": 25, "commands": 25, "practical": 20},
                description="Test ability to provide complete practical workflows"
            )
        ])
        
        return test_cases

    async def run_single_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case and evaluate the response"""
        
        logger.info(f"Running test {test_case.id}: {test_case.description}")
        
        start_time = time.time()
        
        try:
            # Get response from enhanced model
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": test_case.question}
                ],
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent responses
            )
            
            response_text = response.choices[0].message.content
            response_time = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Error running test {test_case.id}: {e}")
            return TestResult(
                test_id=test_case.id,
                question=test_case.question,
                response=f"ERROR: {str(e)}",
                score=0.0,
                max_score=100.0,
                passed=False,
                keywords_found=[],
                keywords_missing=test_case.expected_keywords,
                elements_found=[],
                elements_missing=test_case.expected_elements,
                response_time=0.0,
                validation_notes="API call failed"
            )
        
        # Evaluate response
        return self._evaluate_response(test_case, response_text, response_time)

    def _evaluate_response(self, test_case: TestCase, response: str, response_time: float) -> TestResult:
        """Evaluate the model response against test case criteria"""
        
        response_lower = response.lower()
        
        # Check keywords
        keywords_found = []
        keywords_missing = []
        for keyword in test_case.expected_keywords:
            if keyword.lower() in response_lower:
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)
        
        # Check expected elements
        elements_found = []
        elements_missing = []
        for element in test_case.expected_elements:
            if element.lower() in response_lower:
                elements_found.append(element)
            else:
                elements_missing.append(element)
        
        # Calculate score based on criteria
        total_score = 0.0
        max_score = sum(test_case.scoring_criteria.values())
        
        # Keyword scoring
        keyword_percentage = len(keywords_found) / len(test_case.expected_keywords) if test_case.expected_keywords else 1.0
        total_score += test_case.scoring_criteria.get("keywords", 0) * keyword_percentage
        
        # Element scoring
        element_percentage = len(elements_found) / len(test_case.expected_elements) if test_case.expected_elements else 1.0
        total_score += test_case.scoring_criteria.get("elements", 0) * element_percentage
        
        # Length and structure scoring
        if len(response) > 100:  # Adequate response length
            total_score += test_case.scoring_criteria.get("structure", 0) * 0.8
        if "```" in response:  # Contains code examples
            total_score += test_case.scoring_criteria.get("examples", 0) * 0.9
        
        # Accuracy assessment (industrial control standards - requires near-perfect performance)
        accuracy_score = 0.0
        if keyword_percentage >= 0.95 and element_percentage >= 0.95:
            accuracy_score = 1.0  # Perfect industrial control accuracy
        elif keyword_percentage >= 0.9 and element_percentage >= 0.9:
            accuracy_score = 0.95  # High industrial control accuracy
        elif keyword_percentage >= 0.8 and element_percentage >= 0.8:
            accuracy_score = 0.85  # Acceptable but below industrial standards
        else:
            accuracy_score = 0.5  # Below industrial control safety requirements
        
        total_score += test_case.scoring_criteria.get("accuracy", 0) * accuracy_score
        
        # Pass/fail determination - Industrial control systems require >99% accuracy
        score_percentage = total_score / max_score
        passed = score_percentage >= 0.99  # 99% threshold for passing (industrial control safety requirement)
        
        validation_notes = []
        if keyword_percentage < 0.95:
            validation_notes.append("Insufficient keyword coverage for industrial control standards")
        if element_percentage < 0.95:
            validation_notes.append("Missing critical expected elements")
        if len(response) < 100:
            validation_notes.append("Response too brief for comprehensive guidance")
        if score_percentage < 0.99:
            validation_notes.append("Below 99% industrial control safety threshold")
        if not validation_notes:
            validation_notes.append("Meets industrial control excellence standards")
        
        return TestResult(
            test_id=test_case.id,
            question=test_case.question,
            response=response,
            score=total_score,
            max_score=max_score,
            passed=passed,
            keywords_found=keywords_found,
            keywords_missing=keywords_missing,
            elements_found=elements_found,
            elements_missing=elements_missing,
            response_time=response_time,
            validation_notes="; ".join(validation_notes)
        )

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases and generate comprehensive report"""
        
        logger.info(f"Starting comprehensive validation of model: {self.model_id}")
        logger.info(f"Running {len(self.test_cases)} test cases across {len(TestCategory)} categories")
        
        start_time = time.time()
        
        # Run all tests
        for test_case in self.test_cases:
            result = await self.run_single_test(test_case)
            self.test_results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        total_time = time.time() - start_time
        
        # Calculate category scores
        self._calculate_category_scores()
        
        # Generate report
        report = self._generate_report(total_time)
        
        logger.info(f"Validation complete! Overall score: {report['overall_score']:.1f}%")
        return report

    def _calculate_category_scores(self):
        """Calculate average scores for each test category"""
        
        category_results = {}
        for result in self.test_results:
            test_case = next(tc for tc in self.test_cases if tc.id == result.test_id)
            category = test_case.category
            
            if category not in category_results:
                category_results[category] = []
            
            score_percentage = (result.score / result.max_score) * 100
            category_results[category].append(score_percentage)
        
        for category, scores in category_results.items():
            self.category_scores[category] = sum(scores) / len(scores) if scores else 0.0

    def _generate_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        overall_score = sum(r.score / r.max_score for r in self.test_results) / total_tests * 100
        
        report = {
            "model_id": self.model_id,
            "validation_date": datetime.now().isoformat(),
            "execution_time": total_time,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "pass_rate": (passed_tests / total_tests) * 100,
                "overall_score": overall_score
            },
            "category_scores": {cat.value: score for cat, score in self.category_scores.items()},
            "detailed_results": [asdict(result) for result in self.test_results],
            "recommendations": self._generate_recommendations()
        }
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        # Check category performance - Industrial control systems require >99% accuracy
        for category, score in self.category_scores.items():
            if score < 99:
                recommendations.append(f"CRITICAL: {category.value} below industrial control safety threshold - score: {score:.1f}% (Required: >99%)")
        
        # Check overall performance - Industrial control safety standards
        overall_score = sum(self.category_scores.values()) / len(self.category_scores)
        
        if overall_score >= 99.5:
            recommendations.append("✅ EXCELLENT: Exceeds industrial control safety standards!")
        elif overall_score >= 99:
            recommendations.append("✅ ACCEPTABLE: Meets minimum industrial control safety threshold.")
        elif overall_score >= 95:
            recommendations.append("⚠️ WARNING: Below industrial control safety standards - immediate improvement required.")
        elif overall_score >= 90:
            recommendations.append("❌ CRITICAL: Significant safety risk - model not suitable for industrial control.")
        else:
            recommendations.append("❌ FAILURE: Model completely unsuitable for industrial control applications.")
        
        return recommendations

    def save_report(self, report: Dict[str, Any], output_file: Optional[Path] = None):
        """Save validation report to file"""
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(f"enhanced_model_validation_report_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Validation report saved to: {output_file}")
        
        # Also create a summary file
        summary_file = output_file.with_suffix('.summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Enhanced Model Validation Summary\n")
            f.write(f"================================\n\n")
            f.write(f"Model: {report['model_id']}\n")
            f.write(f"Date: {report['validation_date']}\n")
            f.write(f"Execution Time: {report['execution_time']:.2f} seconds\n\n")
            
            f.write(f"Overall Results:\n")
            f.write(f"- Total Tests: {report['summary']['total_tests']}\n")
            f.write(f"- Passed: {report['summary']['passed_tests']}\n")
            f.write(f"- Failed: {report['summary']['failed_tests']}\n")
            f.write(f"- Pass Rate: {report['summary']['pass_rate']:.1f}%\n")
            f.write(f"- Overall Score: {report['summary']['overall_score']:.1f}%\n\n")
            
            f.write(f"Category Scores:\n")
            for category, score in report['category_scores'].items():
                f.write(f"- {category.replace('_', ' ').title()}: {score:.1f}%\n")
            
            f.write(f"\nRecommendations:\n")
            for i, rec in enumerate(report['recommendations'], 1):
                f.write(f"{i}. {rec}\n")
        
        logger.info(f"Summary report saved to: {summary_file}")

async def main():
    """Main execution function for standalone testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Model Validation Suite")
    parser.add_argument("--model-id", required=True, help="Fine-tuned model ID to validate")
    parser.add_argument("--output", help="Output file for validation report")
    parser.add_argument("--category", help="Run tests for specific category only")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = EnhancedModelValidator(model_id=args.model_id)
    
    # Filter tests by category if specified
    if args.category:
        try:
            category_filter = TestCategory(args.category)
            validator.test_cases = [tc for tc in validator.test_cases if tc.category == category_filter]
            logger.info(f"Running tests for category: {args.category}")
        except ValueError:
            logger.error(f"Invalid category: {args.category}")
            return
    
    # Run validation
    report = await validator.run_all_tests()
    
    # Save report
    output_file = Path(args.output) if args.output else None
    validator.save_report(report, output_file)
    
    # Print summary
    print(f"\n🎯 Enhanced Model Validation Complete!")
    print(f"Overall Score: {report['summary']['overall_score']:.1f}%")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    print(f"Tests: {report['summary']['passed_tests']}/{report['summary']['total_tests']} passed")

if __name__ == "__main__":
    asyncio.run(main()) 