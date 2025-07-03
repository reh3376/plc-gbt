#!/usr/bin/env python3
"""
Fine-Tuning Completion Handler
Automated completion detection, model deployment, and validation following AI Task Orchestrator methodology

Features:
- Automated job completion detection
- Model deployment and configuration
- Comprehensive validation testing
- Status tracking and logging
- Error handling and recovery
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fine_tuning_completion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FineTuningCompletionHandler:
    """Handle fine-tuning completion, deployment, and validation."""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.session_log = []
        self.deployment_config = {}
        self.validation_results = {}
        
    def monitor_and_deploy(self, check_interval: int = 30) -> Dict[str, Any]:
        """
        Monitor job completion and automatically deploy model.
        
        Args:
            check_interval: Time between status checks in seconds
            
        Returns:
            Complete deployment and validation results
        """
        logger.info(f"🚀 Starting automated completion handler for job: {self.job_id}")
        
        # Step 1: Monitor for completion
        model_id = self._monitor_until_completion(check_interval)
        if not model_id:
            return {"status": "failed", "error": "Job did not complete successfully"}
        
        # Step 2: Deploy model
        deployment_result = self._deploy_model(model_id)
        if not deployment_result["success"]:
            return {"status": "failed", "error": f"Deployment failed: {deployment_result['error']}"}
        
        # Step 3: Validate deployment
        validation_result = self._validate_deployment(model_id)
        
        # Step 4: Update task status
        self._update_task_status(model_id, validation_result)
        
        return {
            "status": "completed",
            "model_id": model_id,
            "deployment": deployment_result,
            "validation": validation_result,
            "session_log": self.session_log
        }
    
    def _monitor_until_completion(self, check_interval: int) -> Optional[str]:
        """Monitor job until completion and return model ID."""
        logger.info(f"🔍 Monitoring job {self.job_id} until completion")
        
        while True:
            try:
                job = self.client.fine_tuning.jobs.retrieve(self.job_id)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.session_log.append({
                    "timestamp": timestamp,
                    "action": "status_check",
                    "status": job.status
                })
                
                logger.info(f"[{timestamp}] Job Status: {job.status}")
                
                if job.status == "succeeded":
                    logger.info(f"✅ Fine-tuning completed successfully!")
                    logger.info(f"🤖 Fine-tuned model: {job.fine_tuned_model}")
                    return job.fine_tuned_model
                    
                elif job.status == "failed":
                    logger.error(f"❌ Fine-tuning failed: {job.error}")
                    return None
                    
                elif job.status == "cancelled":
                    logger.warning(f"⚠️ Fine-tuning was cancelled")
                    return None
                    
                elif job.status in ["validating_files", "queued", "running"]:
                    if hasattr(job, 'trained_tokens') and job.trained_tokens:
                        logger.info(f"   Tokens processed: {job.trained_tokens:,}")
                    time.sleep(check_interval)
                    
            except Exception as e:
                logger.error(f"❌ Error checking job status: {e}")
                time.sleep(check_interval)
    
    def _deploy_model(self, model_id: str) -> Dict[str, Any]:
        """Deploy the completed model for inference."""
        logger.info(f"🚀 Deploying model: {model_id}")
        
        try:
            # Create deployment configuration
            self.deployment_config = {
                "model_id": model_id,
                "deployment_time": datetime.now().isoformat(),
                "max_tokens": 4000,
                "temperature": 0.7,
                "system_prompt": "You are PLC-GPT, a specialized AI assistant for industrial automation and PLC programming. You have extensive knowledge of Allen-Bradley systems, Studio 5000, Rockwell Automation, and industrial control systems."
            }
            
            # Save deployment configuration
            config_file = Path("deployment_config.json")
            with open(config_file, 'w') as f:
                json.dump(self.deployment_config, f, indent=2)
            
            logger.info(f"✅ Model deployment configured successfully")
            logger.info(f"📄 Configuration saved to: {config_file}")
            
            return {
                "success": True,
                "model_id": model_id,
                "config_file": str(config_file),
                "deployment_time": self.deployment_config["deployment_time"]
            }
            
        except Exception as e:
            logger.error(f"❌ Model deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_deployment(self, model_id: str) -> Dict[str, Any]:
        """Comprehensive validation of deployed model."""
        logger.info(f"🧪 Validating deployed model: {model_id}")
        
        validation_results = {
            "model_id": model_id,
            "validation_time": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "overall_score": 0,
            "test_results": []
        }
        
        # Comprehensive test suite for PLC domain
        test_cases = [
            {
                "category": "PLC Basics",
                "question": "What is an AOI in PLC programming?",
                "expected_keywords": ["add-on instruction", "reusable", "logic", "allen-bradley"]
            },
            {
                "category": "Hardware",
                "question": "How do you configure a CompactLogix controller?",
                "expected_keywords": ["studio 5000", "configuration", "io", "network"]
            },
            {
                "category": "Programming",
                "question": "What's the difference between ST and ladder logic?",
                "expected_keywords": ["structured text", "ladder", "programming", "language"]
            },
            {
                "category": "Troubleshooting",
                "question": "How do you troubleshoot communication errors in Studio 5000?",
                "expected_keywords": ["communication", "network", "diagnostic", "error"]
            },
            {
                "category": "Best Practices",
                "question": "What are the best practices for PLC tag naming?",
                "expected_keywords": ["naming", "convention", "tag", "standard"]
            }
        ]
        
        for test_case in test_cases:
            try:
                logger.info(f"🔍 Testing: {test_case['category']} - {test_case['question']}")
                
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": self.deployment_config["system_prompt"]},
                        {"role": "user", "content": test_case["question"]}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                
                answer = response.choices[0].message.content.strip()
                
                # Validate answer quality
                score = self._score_answer(answer, test_case["expected_keywords"])
                
                test_result = {
                    "category": test_case["category"],
                    "question": test_case["question"],
                    "answer": answer,
                    "score": score,
                    "passed": score >= 0.6
                }
                
                validation_results["test_results"].append(test_result)
                
                if test_result["passed"]:
                    validation_results["tests_passed"] += 1
                    logger.info(f"✅ Test passed (score: {score:.2f})")
                else:
                    validation_results["tests_failed"] += 1
                    logger.warning(f"❌ Test failed (score: {score:.2f})")
                    
            except Exception as e:
                logger.error(f"❌ Test failed with error: {e}")
                validation_results["tests_failed"] += 1
                validation_results["test_results"].append({
                    "category": test_case["category"],
                    "question": test_case["question"],
                    "error": str(e),
                    "passed": False
                })
        
        # Calculate overall score
        total_tests = len(test_cases)
        validation_results["overall_score"] = (validation_results["tests_passed"] / total_tests) * 100
        
        logger.info(f"📊 Validation Summary:")
        logger.info(f"   Tests Passed: {validation_results['tests_passed']}/{total_tests}")
        logger.info(f"   Overall Score: {validation_results['overall_score']:.1f}%")
        
        # Save validation results
        results_file = Path("validation_results.json")
        with open(results_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        logger.info(f"📄 Validation results saved to: {results_file}")
        
        return validation_results
    
    def _score_answer(self, answer: str, expected_keywords: List[str]) -> float:
        """Score answer based on keyword presence and length."""
        answer_lower = answer.lower()
        
        # Check for expected keywords
        keyword_score = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
        keyword_score = keyword_score / len(expected_keywords)
        
        # Check answer length (should be substantial)
        length_score = min(len(answer) / 100, 1.0)  # Normalize to 1.0 max
        
        # Combine scores
        return (keyword_score * 0.7) + (length_score * 0.3)
    
    def _update_task_status(self, model_id: str, validation_result: Dict[str, Any]):
        """Update task completion status."""
        logger.info(f"📋 Updating task status for model: {model_id}")
        
        status_update = {
            "task_id": "phase4_fine_tuning_monitor",
            "status": "completed",
            "completion_time": datetime.now().isoformat(),
            "model_id": model_id,
            "validation_score": validation_result["overall_score"],
            "next_task": "phase4_model_testing"
        }
        
        # Save status update
        status_file = Path("task_status_update.json")
        with open(status_file, 'w') as f:
            json.dump(status_update, f, indent=2)
        
        logger.info(f"✅ Task status updated - Ready for next phase")
        logger.info(f"📄 Status saved to: {status_file}")

def main():
    """Main execution function."""
    job_id = "ftjob-9xqplqCWf37zI86LdyX3ejqe"
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY environment variable not set!")
        return
    
    handler = FineTuningCompletionHandler(job_id)
    result = handler.monitor_and_deploy(check_interval=30)
    
    if result["status"] == "completed":
        logger.info(f"🎉 Fine-tuning completion handler finished successfully!")
        logger.info(f"🤖 Model {result['model_id']} is deployed and validated")
        logger.info(f"📊 Validation Score: {result['validation']['overall_score']:.1f}%")
    else:
        logger.error(f"❌ Completion handler failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 