#!/usr/bin/env python3
"""
Comprehensive Model Tester for PLC-GPT
AI Task Orchestrator guided testing and validation framework

Features:
- Multi-domain PLC testing (hardware, programming, troubleshooting)
- Baseline comparison with standard GPT models
- Performance metrics and scoring
- Comprehensive validation reports
- Error analysis and improvement recommendations
"""

import os
import json
import time
import logging
import statistics
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from typing import Dict, List, Any, Optional, Tuple
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PLCGPTModelTester:
    """
    Comprehensive testing framework for PLC-GPT model validation.
    
    Following AI Task Orchestrator methodology:
    - Systematic test planning and execution
    - Multi-domain validation coverage
    - Performance benchmarking
    - Quality assessment and reporting
    """
    
    def __init__(self, fine_tuned_model_id: str = None):
        """
        Initialize the model tester.
        
        Args:
            fine_tuned_model_id: ID of the fine-tuned model to test
        """
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.fine_tuned_model_id = fine_tuned_model_id
        self.test_results = {}
        self.session_log = []
        self.test_categories = self._define_test_categories()
        
        # AI Task Orchestrator Analysis
        self.task_analysis = {
            "task_id": "phase4_model_testing",
            "complexity": "complex",  # 500-1500 lines, comprehensive testing
            "estimated_effort": "3-4 hours",
            "requirements": [
                "Comprehensive PLC domain testing",
                "Performance comparison with baseline models",
                "Quality metrics and scoring",
                "Detailed reporting and analysis",
                "Error detection and improvement recommendations"
            ],
            "validation_criteria": [
                "Test coverage across all PLC domains",
                "Performance metrics calculated accurately",
                "Baseline comparison completed",
                "Quality scores meet thresholds",
                "Comprehensive report generated"
            ]
        }
        
        logger.info(f"🧪 PLC-GPT Model Tester initialized")
        logger.info(f"📊 Task Complexity: {self.task_analysis['complexity']}")
        logger.info(f"⏱️ Estimated Effort: {self.task_analysis['estimated_effort']}")
    
    def _define_test_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Define comprehensive test categories and questions."""
        return {
            "plc_basics": [
                {
                    "question": "What is an AOI (Add-On Instruction) in PLC programming?",
                    "expected_keywords": ["add-on instruction", "reusable", "logic", "encapsulation", "parameters"],
                    "difficulty": "basic",
                    "max_score": 100
                },
                {
                    "question": "Explain the difference between NO (Normally Open) and NC (Normally Closed) contacts in ladder logic.",
                    "expected_keywords": ["normally open", "normally closed", "contact", "ladder", "logic"],
                    "difficulty": "basic",
                    "max_score": 100
                },
                {
                    "question": "What is the purpose of a PLC scan cycle?",
                    "expected_keywords": ["scan", "cycle", "input", "output", "program", "execution"],
                    "difficulty": "intermediate",
                    "max_score": 100
                }
            ],
            "hardware_configuration": [
                {
                    "question": "How do you configure a CompactLogix L32E controller for Ethernet communication?",
                    "expected_keywords": ["compactlogix", "ethernet", "configuration", "ip address", "studio 5000"],
                    "difficulty": "intermediate",
                    "max_score": 100
                },
                {
                    "question": "What are the key differences between ControlLogix and CompactLogix systems?",
                    "expected_keywords": ["controllogix", "compactlogix", "chassis", "modules", "scalability"],
                    "difficulty": "intermediate",
                    "max_score": 100
                },
                {
                    "question": "Explain the process of adding an I/O module to a Studio 5000 project.",
                    "expected_keywords": ["i/o module", "studio 5000", "configuration", "communication", "slot"],
                    "difficulty": "advanced",
                    "max_score": 100
                }
            ],
            "programming_languages": [
                {
                    "question": "Compare Ladder Logic, Function Block Diagram, and Structured Text programming languages.",
                    "expected_keywords": ["ladder logic", "function block", "structured text", "programming", "comparison"],
                    "difficulty": "intermediate",
                    "max_score": 100
                },
                {
                    "question": "Write a simple Structured Text program to control a conveyor belt with start/stop functionality.",
                    "expected_keywords": ["structured text", "conveyor", "start", "stop", "motor", "control"],
                    "difficulty": "advanced",
                    "max_score": 100
                },
                {
                    "question": "How do you implement a timer in ladder logic?",
                    "expected_keywords": ["timer", "ladder logic", "TON", "TOF", "preset", "accumulated"],
                    "difficulty": "basic",
                    "max_score": 100
                }
            ],
            "troubleshooting": [
                {
                    "question": "How do you troubleshoot a 'Connection Faulted' error in Studio 5000?",
                    "expected_keywords": ["connection faulted", "troubleshooting", "communication", "network", "diagnostic"],
                    "difficulty": "advanced",
                    "max_score": 100
                },
                {
                    "question": "What steps would you take to diagnose a PLC that's not responding?",
                    "expected_keywords": ["diagnosis", "not responding", "power", "communication", "fault", "led"],
                    "difficulty": "intermediate",
                    "max_score": 100
                },
                {
                    "question": "How do you use the Logic Analyzer in Studio 5000 for debugging?",
                    "expected_keywords": ["logic analyzer", "debugging", "studio 5000", "trend", "data collection"],
                    "difficulty": "advanced",
                    "max_score": 100
                }
            ],
            "safety_systems": [
                {
                    "question": "Explain the principles of Safety Instrumented Systems (SIS) in industrial automation.",
                    "expected_keywords": ["safety instrumented systems", "sis", "safety", "fail-safe", "integrity"],
                    "difficulty": "advanced",
                    "max_score": 100
                },
                {
                    "question": "What is the difference between Category 3 and Category 4 safety systems?",
                    "expected_keywords": ["category 3", "category 4", "safety", "redundancy", "monitoring"],
                    "difficulty": "expert",
                    "max_score": 100
                },
                {
                    "question": "How do you implement an Emergency Stop (E-Stop) circuit in a PLC system?",
                    "expected_keywords": ["emergency stop", "e-stop", "safety", "circuit", "normally closed"],
                    "difficulty": "intermediate",
                    "max_score": 100
                }
            ],
            "communication_protocols": [
                {
                    "question": "Compare Ethernet/IP, DeviceNet, and ControlNet communication protocols.",
                    "expected_keywords": ["ethernet/ip", "devicenet", "controlnet", "communication", "protocol"],
                    "difficulty": "advanced",
                    "max_score": 100
                },
                {
                    "question": "How do you configure a Modbus TCP communication in Studio 5000?",
                    "expected_keywords": ["modbus tcp", "configuration", "studio 5000", "communication", "slave"],
                    "difficulty": "advanced",
                    "max_score": 100
                },
                {
                    "question": "What is the Common Industrial Protocol (CIP) and how is it used?",
                    "expected_keywords": ["common industrial protocol", "cip", "communication", "objects", "services"],
                    "difficulty": "expert",
                    "max_score": 100
                }
            ]
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Run comprehensive model testing following AI Task Orchestrator methodology.
        
        Returns:
            Complete test results and analysis
        """
        logger.info("🚀 Starting comprehensive PLC-GPT model testing")
        logger.info("=" * 60)
        
        # Step 1: Validate setup
        if not self._validate_setup():
            return {"status": "failed", "error": "Setup validation failed"}
        
        # Step 2: Run baseline comparison
        baseline_results = self._run_baseline_comparison()
        
        # Step 3: Execute domain-specific tests
        domain_results = self._execute_domain_tests()
        
        # Step 4: Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(domain_results)
        
        # Step 5: Generate comprehensive report
        final_report = self._generate_comprehensive_report(
            baseline_results, domain_results, performance_metrics
        )
        
        # Step 6: Validate results against criteria
        validation_status = self._validate_test_results(final_report)
        
        return {
            "status": "completed",
            "validation_status": validation_status,
            "baseline_results": baseline_results,
            "domain_results": domain_results,
            "performance_metrics": performance_metrics,
            "final_report": final_report,
            "session_log": self.session_log
        }
    
    def _validate_setup(self) -> bool:
        """Validate testing environment setup."""
        logger.info("🔍 Validating testing environment setup")
        
        # Check API key
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("❌ OPENAI_API_KEY not found")
            return False
        
        # Check model availability
        if self.fine_tuned_model_id:
            try:
                # Test API call to verify model exists
                response = self.client.chat.completions.create(
                    model=self.fine_tuned_model_id,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                logger.info(f"✅ Fine-tuned model {self.fine_tuned_model_id} is accessible")
            except Exception as e:
                logger.error(f"❌ Fine-tuned model not accessible: {e}")
                return False
        else:
            logger.warning("⚠️ No fine-tuned model ID provided - will use latest available")
        
        logger.info("✅ Setup validation completed successfully")
        return True
    
    def _run_baseline_comparison(self) -> Dict[str, Any]:
        """Run baseline comparison with standard GPT models."""
        logger.info("📊 Running baseline comparison tests")
        
        # Models to compare against
        baseline_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            self.fine_tuned_model_id or "gpt-3.5-turbo"
        ]
        
        # Sample questions for comparison
        comparison_questions = [
            "What is an AOI in PLC programming?",
            "How do you configure a CompactLogix controller?",
            "What's the difference between Ladder Logic and Structured Text?"
        ]
        
        baseline_results = {}
        
        for model in baseline_models:
            if not model:
                continue
                
            model_results = []
            logger.info(f"🧪 Testing model: {model}")
            
            for question in comparison_questions:
                try:
                    start_time = time.time()
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a PLC programming expert."},
                            {"role": "user", "content": question}
                        ],
                        max_tokens=200,
                        temperature=0.7
                    )
                    response_time = time.time() - start_time
                    
                    answer = response.choices[0].message.content.strip()
                    
                    model_results.append({
                        "question": question,
                        "answer": answer,
                        "response_time": response_time,
                        "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Error testing {model}: {e}")
                    model_results.append({
                        "question": question,
                        "error": str(e),
                        "response_time": 0,
                        "tokens_used": 0
                    })
            
            baseline_results[model] = model_results
        
        logger.info("✅ Baseline comparison completed")
        return baseline_results
    
    def _execute_domain_tests(self) -> Dict[str, Any]:
        """Execute comprehensive domain-specific testing."""
        logger.info("🎯 Executing domain-specific tests")
        
        domain_results = {}
        
        for domain, questions in self.test_categories.items():
            logger.info(f"📝 Testing domain: {domain}")
            
            domain_results[domain] = {
                "questions_tested": len(questions),
                "results": [],
                "domain_score": 0
            }
            
            for question_data in questions:
                result = self._test_single_question(question_data, domain)
                domain_results[domain]["results"].append(result)
            
            # Calculate domain score
            total_score = sum(r["score"] for r in domain_results[domain]["results"])
            max_possible = len(questions) * 100
            domain_results[domain]["domain_score"] = (total_score / max_possible) * 100
            
            logger.info(f"✅ Domain {domain} completed - Score: {domain_results[domain]['domain_score']:.1f}%")
        
        return domain_results
    
    def _test_single_question(self, question_data: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Test a single question and return detailed results."""
        question = question_data["question"]
        expected_keywords = question_data["expected_keywords"]
        difficulty = question_data["difficulty"]
        max_score = question_data["max_score"]
        
        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.fine_tuned_model_id or "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are PLC-GPT, a specialized AI assistant for industrial automation and PLC programming. You have extensive knowledge of Allen-Bradley systems, Studio 5000, Rockwell Automation, and industrial control systems."},
                    {"role": "user", "content": question}
                ],
                max_tokens=300,
                temperature=0.7
            )
            response_time = time.time() - start_time
            
            answer = response.choices[0].message.content.strip()
            
            # Score the answer
            score = self._score_answer(answer, expected_keywords, difficulty)
            
            return {
                "question": question,
                "answer": answer,
                "expected_keywords": expected_keywords,
                "difficulty": difficulty,
                "score": score,
                "max_score": max_score,
                "response_time": response_time,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                "domain": domain
            }
            
        except Exception as e:
            logger.error(f"❌ Error testing question in {domain}: {e}")
            return {
                "question": question,
                "error": str(e),
                "score": 0,
                "max_score": max_score,
                "response_time": 0,
                "tokens_used": 0,
                "domain": domain
            }
    
    def _score_answer(self, answer: str, expected_keywords: List[str], difficulty: str) -> float:
        """Score answer based on keyword presence, quality, and difficulty."""
        answer_lower = answer.lower()
        
        # Keyword matching score (40%)
        keyword_score = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
        keyword_score = (keyword_score / len(expected_keywords)) * 40
        
        # Answer length and completeness score (30%)
        length_score = min(len(answer) / 150, 1.0) * 30
        
        # Technical accuracy indicators (20%)
        technical_indicators = [
            "studio 5000", "allen-bradley", "rockwell", "plc", "controller",
            "ladder logic", "structured text", "function block", "tag", "routine"
        ]
        technical_score = sum(1 for indicator in technical_indicators if indicator in answer_lower)
        technical_score = min(technical_score / 5, 1.0) * 20
        
        # Difficulty adjustment (10%)
        difficulty_multiplier = {
            "basic": 1.0,
            "intermediate": 0.9,
            "advanced": 0.8,
            "expert": 0.7
        }
        difficulty_score = difficulty_multiplier.get(difficulty, 1.0) * 10
        
        total_score = keyword_score + length_score + technical_score + difficulty_score
        return min(total_score, 100)  # Cap at 100
    
    def _calculate_performance_metrics(self, domain_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        logger.info("📊 Calculating performance metrics")
        
        all_scores = []
        all_response_times = []
        domain_scores = {}
        
        for domain, data in domain_results.items():
            domain_scores[domain] = data["domain_score"]
            for result in data["results"]:
                all_scores.append(result["score"])
                all_response_times.append(result["response_time"])
        
        metrics = {
            "overall_score": statistics.mean(all_scores) if all_scores else 0,
            "median_score": statistics.median(all_scores) if all_scores else 0,
            "score_std_dev": statistics.stdev(all_scores) if len(all_scores) > 1 else 0,
            "min_score": min(all_scores) if all_scores else 0,
            "max_score": max(all_scores) if all_scores else 0,
            "average_response_time": statistics.mean(all_response_times) if all_response_times else 0,
            "total_questions": len(all_scores),
            "questions_passed": sum(1 for score in all_scores if score >= 70),
            "pass_rate": (sum(1 for score in all_scores if score >= 70) / len(all_scores)) * 100 if all_scores else 0,
            "domain_scores": domain_scores
        }
        
        logger.info(f"📈 Performance Metrics Calculated:")
        logger.info(f"   Overall Score: {metrics['overall_score']:.1f}%")
        logger.info(f"   Pass Rate: {metrics['pass_rate']:.1f}%")
        logger.info(f"   Avg Response Time: {metrics['average_response_time']:.2f}s")
        
        return metrics
    
    def _generate_comprehensive_report(self, baseline_results: Dict[str, Any], 
                                     domain_results: Dict[str, Any], 
                                     performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive testing report."""
        logger.info("📋 Generating comprehensive test report")
        
        report = {
            "report_id": f"plc_gpt_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "model_tested": self.fine_tuned_model_id or "gpt-3.5-turbo",
            "test_summary": {
                "total_domains": len(domain_results),
                "total_questions": performance_metrics["total_questions"],
                "overall_score": performance_metrics["overall_score"],
                "pass_rate": performance_metrics["pass_rate"],
                "testing_duration": sum(
                    sum(r["response_time"] for r in data["results"]) 
                    for data in domain_results.values()
                )
            },
            "baseline_comparison": baseline_results,
            "domain_breakdown": domain_results,
            "performance_metrics": performance_metrics,
            "recommendations": self._generate_recommendations(performance_metrics, domain_results)
        }
        
        # Save report to file
        report_file = Path(f"plc_gpt_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate CSV summary
        self._generate_csv_summary(domain_results, report_file.with_suffix('.csv'))
        
        logger.info(f"📄 Comprehensive report saved to: {report_file}")
        return report
    
    def _generate_recommendations(self, performance_metrics: Dict[str, Any], 
                                domain_results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on test results."""
        recommendations = []
        
        # Overall performance recommendations
        if performance_metrics["overall_score"] < 70:
            recommendations.append("Overall performance below 70% - consider additional fine-tuning")
        
        if performance_metrics["pass_rate"] < 80:
            recommendations.append("Pass rate below 80% - review training data quality")
        
        # Domain-specific recommendations
        for domain, score in performance_metrics["domain_scores"].items():
            if score < 60:
                recommendations.append(f"Domain '{domain}' performing poorly ({score:.1f}%) - needs targeted improvement")
        
        # Response time recommendations
        if performance_metrics["average_response_time"] > 5:
            recommendations.append("Response time above 5 seconds - consider optimization")
        
        return recommendations
    
    def _generate_csv_summary(self, domain_results: Dict[str, Any], csv_file: Path):
        """Generate CSV summary of test results."""
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Domain', 'Question', 'Score', 'Difficulty', 'Response Time', 'Passed'])
            
            for domain, data in domain_results.items():
                for result in data["results"]:
                    writer.writerow([
                        domain,
                        result["question"],
                        result["score"],
                        result.get("difficulty", "unknown"),
                        result["response_time"],
                        result["score"] >= 70
                    ])
    
    def _validate_test_results(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Validate test results against AI Task Orchestrator criteria."""
        validation_results = {
            "criteria_met": 0,
            "criteria_total": len(self.task_analysis["validation_criteria"]),
            "validation_details": []
        }
        
        for criterion in self.task_analysis["validation_criteria"]:
            if "Test coverage across all PLC domains" in criterion:
                passed = len(report["domain_breakdown"]) >= 6
                validation_results["validation_details"].append({
                    "criterion": criterion,
                    "passed": passed,
                    "details": f"Tested {len(report['domain_breakdown'])} domains"
                })
                if passed:
                    validation_results["criteria_met"] += 1
            
            elif "Performance metrics calculated accurately" in criterion:
                passed = "performance_metrics" in report and report["performance_metrics"]["overall_score"] > 0
                validation_results["validation_details"].append({
                    "criterion": criterion,
                    "passed": passed,
                    "details": f"Overall score: {report['performance_metrics']['overall_score']:.1f}%"
                })
                if passed:
                    validation_results["criteria_met"] += 1
            
            elif "Baseline comparison completed" in criterion:
                passed = "baseline_comparison" in report and len(report["baseline_comparison"]) > 0
                validation_results["validation_details"].append({
                    "criterion": criterion,
                    "passed": passed,
                    "details": f"Compared against {len(report['baseline_comparison'])} models"
                })
                if passed:
                    validation_results["criteria_met"] += 1
            
            elif "Quality scores meet thresholds" in criterion:
                passed = report["performance_metrics"]["overall_score"] >= 70
                validation_results["validation_details"].append({
                    "criterion": criterion,
                    "passed": passed,
                    "details": f"Score {report['performance_metrics']['overall_score']:.1f}% (threshold: 70%)"
                })
                if passed:
                    validation_results["criteria_met"] += 1
            
            elif "Comprehensive report generated" in criterion:
                passed = "report_id" in report and len(report["recommendations"]) > 0
                validation_results["validation_details"].append({
                    "criterion": criterion,
                    "passed": passed,
                    "details": f"Report generated with {len(report['recommendations'])} recommendations"
                })
                if passed:
                    validation_results["criteria_met"] += 1
        
        validation_results["overall_validation_score"] = (
            validation_results["criteria_met"] / validation_results["criteria_total"]
        ) * 100
        
        return validation_results

def main():
    """Main execution function."""
    
    # Check for fine-tuned model ID
    fine_tuned_model = None
    
    # Try to find the latest fine-tuned model
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        jobs = client.fine_tuning.jobs.list(limit=10)
        
        for job in jobs.data:
            if job.status == "succeeded" and job.fine_tuned_model:
                fine_tuned_model = job.fine_tuned_model
                logger.info(f"🔍 Found fine-tuned model: {fine_tuned_model}")
                break
        
        if not fine_tuned_model:
            logger.warning("⚠️ No successful fine-tuned model found - using GPT-3.5-turbo")
            fine_tuned_model = "gpt-3.5-turbo"
            
    except Exception as e:
        logger.error(f"❌ Error finding fine-tuned model: {e}")
        return
    
    # Initialize tester
    tester = PLCGPTModelTester(fine_tuned_model)
    
    # Run comprehensive testing
    results = tester.run_comprehensive_test()
    
    if results["status"] == "completed":
        logger.info("🎉 Comprehensive model testing completed successfully!")
        logger.info(f"📊 Overall Score: {results['performance_metrics']['overall_score']:.1f}%")
        logger.info(f"✅ Pass Rate: {results['performance_metrics']['pass_rate']:.1f}%")
        logger.info(f"🔍 Validation Score: {results['validation_status']['overall_validation_score']:.1f}%")
        
        # Show top recommendations
        if results['final_report']['recommendations']:
            logger.info("💡 Top Recommendations:")
            for rec in results['final_report']['recommendations'][:3]:
                logger.info(f"   • {rec}")
    else:
        logger.error(f"❌ Model testing failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 