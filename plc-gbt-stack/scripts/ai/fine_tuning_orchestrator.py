#!/usr/bin/env python3
"""
Fine-Tuning Orchestrator for Phase 4 PLC-GPT Model Training
Handles the complete fine-tuning process with OpenAI API

This module:
- Manages training data upload and validation
- Orchestrates the fine-tuning process
- Monitors training progress and metrics
- Handles model deployment and testing
- Provides cost estimation and monitoring
"""

import asyncio
import json
import logging
import os

# Internal imports
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# OpenAI API
from openai import OpenAI

sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FineTuningOrchestrator:
    """Orchestrates the complete fine-tuning process for PLC domain expertise."""

    def __init__(self, openai_api_key: Optional[str] = None, organization: Optional[str] = None):
        """Initialize fine-tuning orchestrator."""

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
            organization=organization or os.getenv("OPENAI_ORGANIZATION")
        )

        # Training configuration
        self.training_config = {
            "model": os.getenv("OPENAI_FINETUNE_BASE_MODEL", "gpt-4o-mini-2024-07-18"),  # Use GPT-4o-mini as default (supports fine-tuning)
            "n_epochs": 3,           # Number of training epochs
            "batch_size": 1,         # Batch size for training
            "learning_rate_multiplier": 0.1,  # Learning rate multiplier
            "prompt_loss_weight": 0.01,       # Weight for prompt loss
            "suffix": "industrial-control"    # Model suffix for consistency
        }

        # Cost tracking (Updated for GPT-4o-mini)
        self.cost_estimates = {
            "training_cost_per_1k_tokens": 0.0030,  # GPT-4o-mini training cost
            "usage_cost_per_1k_tokens": 0.0001,     # GPT-4o-mini usage cost
            "estimated_tokens_per_example": 200      # Average tokens per training example
        }

        # Progress tracking
        self.training_jobs = {}
        self.model_deployments = {}

    async def orchestrate_complete_fine_tuning(self, training_data_dir: str) -> Dict[str, Any]:
        """Orchestrate the complete fine-tuning process."""
        logger.info("Starting complete fine-tuning orchestration")

        orchestration_result = {
            "start_time": datetime.now().isoformat(),
            "training_data_dir": training_data_dir,
            "steps_completed": [],
            "training_job_id": None,
            "model_id": None,
            "cost_estimate": 0.0,
            "status": "started"
        }

        try:
            # Step 1: Validate training data
            logger.info("Step 1: Validating training data")
            validation_result = await self.validate_training_data(training_data_dir)
            orchestration_result["steps_completed"].append({
                "step": "validation",
                "status": "completed",
                "result": validation_result
            })

            # Step 2: Upload training data
            logger.info("Step 2: Uploading training data to OpenAI")
            upload_result = await self.upload_training_data(training_data_dir)
            orchestration_result["steps_completed"].append({
                "step": "upload",
                "status": "completed",
                "result": upload_result
            })

            # Step 3: Estimate costs
            logger.info("Step 3: Estimating fine-tuning costs")
            cost_estimate = self.estimate_fine_tuning_costs(validation_result["training_examples"])
            orchestration_result["cost_estimate"] = cost_estimate
            orchestration_result["steps_completed"].append({
                "step": "cost_estimation",
                "status": "completed",
                "result": cost_estimate
            })

            # Step 4: Create fine-tuning job
            logger.info("Step 4: Creating fine-tuning job")
            job_result = await self.create_fine_tuning_job(upload_result["training_file_id"])
            orchestration_result["training_job_id"] = job_result["job_id"]
            orchestration_result["steps_completed"].append({
                "step": "job_creation",
                "status": "completed",
                "result": job_result
            })

            # Step 5: Monitor training progress
            logger.info("Step 5: Monitoring training progress")
            monitoring_result = await self.monitor_training_progress(job_result["job_id"])
            orchestration_result["steps_completed"].append({
                "step": "monitoring",
                "status": "completed",
                "result": monitoring_result
            })

            # Step 6: Deploy and test model
            if monitoring_result["status"] == "succeeded":
                logger.info("Step 6: Deploying and testing model")
                deployment_result = await self.deploy_and_test_model(monitoring_result["model_id"])
                orchestration_result["model_id"] = monitoring_result["model_id"]
                orchestration_result["steps_completed"].append({
                    "step": "deployment",
                    "status": "completed",
                    "result": deployment_result
                })
                orchestration_result["status"] = "completed"
            else:
                orchestration_result["status"] = "failed"
                orchestration_result["error"] = monitoring_result.get("error", "Training failed")

            # Step 7: Generate final report
            logger.info("Step 7: Generating final report")
            report = await self.generate_fine_tuning_report(orchestration_result)
            orchestration_result["final_report"] = report

        except Exception as e:
            logger.error(f"Fine-tuning orchestration failed: {e}")
            orchestration_result["status"] = "failed"
            orchestration_result["error"] = str(e)

        orchestration_result["end_time"] = datetime.now().isoformat()
        return orchestration_result

    async def validate_training_data(self, training_data_dir: str) -> Dict[str, Any]:
        """Validate training data format and quality."""
        training_dir = Path(training_data_dir)

        # Find training files
        training_files = list(training_dir.glob("*training*.jsonl"))
        validation_files = list(training_dir.glob("*validation*.jsonl"))

        if not training_files:
            raise ValueError("No training JSONL files found")

        training_file = training_files[0]
        validation_file = validation_files[0] if validation_files else None

        # Validate format
        training_examples = []
        validation_examples = []

        # Load and validate training data
        with open(training_file) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    example = json.loads(line.strip())
                    self.validate_training_example(example)
                    training_examples.append(example)
                except Exception as e:
                    logger.warning(f"Invalid training example at line {line_num}: {e}")

        # Load and validate validation data
        if validation_file:
            with open(validation_file) as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        example = json.loads(line.strip())
                        self.validate_training_example(example)
                        validation_examples.append(example)
                    except Exception as e:
                        logger.warning(f"Invalid validation example at line {line_num}: {e}")

        # Generate validation statistics
        validation_result = {
            "training_file": str(training_file),
            "validation_file": str(validation_file) if validation_file else None,
            "training_examples": len(training_examples),
            "validation_examples": len(validation_examples),
            "total_examples": len(training_examples) + len(validation_examples),
            "validation_passed": True,
            "statistics": self.generate_validation_statistics(training_examples, validation_examples)
        }

        logger.info(f"Validation completed: {validation_result['total_examples']} examples")
        return validation_result

    def validate_training_example(self, example: Dict[str, Any]) -> None:
        """Validate a single training example."""
        if "messages" not in example:
            raise ValueError("Missing 'messages' field")

        messages = example["messages"]
        if not isinstance(messages, list) or len(messages) < 2:
            raise ValueError("'messages' must be a list with at least 2 messages")

        # Check for required roles
        roles = [msg.get("role") for msg in messages]
        if "user" not in roles or "assistant" not in roles:
            raise ValueError("Must have at least 'user' and 'assistant' roles")

        # Check message structure
        for msg in messages:
            if "role" not in msg or "content" not in msg:
                raise ValueError("Each message must have 'role' and 'content' fields")

            if not isinstance(msg["content"], str) or len(msg["content"].strip()) == 0:
                raise ValueError("Message content must be non-empty string")

    def generate_validation_statistics(self, training_examples: List[Dict], validation_examples: List[Dict]) -> Dict[str, Any]:
        """Generate statistics for validation data."""
        all_examples = training_examples + validation_examples

        # Calculate token counts (approximate)
        total_tokens = 0
        user_message_lengths = []
        assistant_message_lengths = []

        for example in all_examples:
            example_tokens = 0
            for message in example["messages"]:
                content = message["content"]
                tokens = len(content.split()) * 1.3  # Rough token estimate
                example_tokens += tokens

                if message["role"] == "user":
                    user_message_lengths.append(len(content))
                elif message["role"] == "assistant":
                    assistant_message_lengths.append(len(content))

            total_tokens += example_tokens

        return {
            "total_examples": len(all_examples),
            "estimated_total_tokens": int(total_tokens),
            "avg_tokens_per_example": int(total_tokens / len(all_examples)) if all_examples else 0,
            "avg_user_message_length": int(sum(user_message_lengths) / len(user_message_lengths)) if user_message_lengths else 0,
            "avg_assistant_message_length": int(sum(assistant_message_lengths) / len(assistant_message_lengths)) if assistant_message_lengths else 0,
            "max_user_message_length": max(user_message_lengths) if user_message_lengths else 0,
            "max_assistant_message_length": max(assistant_message_lengths) if assistant_message_lengths else 0
        }

    async def upload_training_data(self, training_data_dir: str) -> Dict[str, Any]:
        """Upload training data to OpenAI."""
        training_dir = Path(training_data_dir)

        # Find training and validation files
        training_files = list(training_dir.glob("*training*.jsonl"))
        validation_files = list(training_dir.glob("*validation*.jsonl"))

        if not training_files:
            raise ValueError("No training JSONL files found")

        training_file = training_files[0]
        validation_file = validation_files[0] if validation_files else None

        # Upload training file
        logger.info(f"Uploading training file: {training_file}")
        with open(training_file, 'rb') as f:
            training_file_response = self.client.files.create(
                file=f,
                purpose="fine-tune"
            )

        upload_result = {
            "training_file_id": training_file_response.id,
            "training_file_name": training_file.name,
            "validation_file_id": None,
            "validation_file_name": None
        }

        # Upload validation file if exists
        if validation_file:
            logger.info(f"Uploading validation file: {validation_file}")
            with open(validation_file, 'rb') as f:
                validation_file_response = self.client.files.create(
                    file=f,
                    purpose="fine-tune"
                )

            upload_result["validation_file_id"] = validation_file_response.id
            upload_result["validation_file_name"] = validation_file.name

        logger.info(f"Upload completed: training_file_id={upload_result['training_file_id']}")
        return upload_result

    def estimate_fine_tuning_costs(self, num_examples: int) -> Dict[str, float]:
        """Estimate fine-tuning costs."""
        estimated_tokens = num_examples * self.cost_estimates["estimated_tokens_per_example"]
        training_cost = (estimated_tokens / 1000) * self.cost_estimates["training_cost_per_1k_tokens"]

        # Estimate usage costs (assuming 1000 queries per month)
        monthly_usage_tokens = 1000 * 150  # 150 tokens per query on average
        monthly_usage_cost = (monthly_usage_tokens / 1000) * self.cost_estimates["usage_cost_per_1k_tokens"]

        return {
            "estimated_training_tokens": estimated_tokens,
            "estimated_training_cost": training_cost,
            "estimated_monthly_usage_tokens": monthly_usage_tokens,
            "estimated_monthly_usage_cost": monthly_usage_cost,
            "total_estimated_first_month_cost": training_cost + monthly_usage_cost
        }

    async def create_fine_tuning_job(self, training_file_id: str, validation_file_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a fine-tuning job."""

        # Prepare job parameters
        job_params = {
            "training_file": training_file_id,
            "model": self.training_config["model"],
            "suffix": self.training_config["suffix"],
            "hyperparameters": {
                "n_epochs": self.training_config["n_epochs"],
                "batch_size": self.training_config["batch_size"],
                "learning_rate_multiplier": self.training_config["learning_rate_multiplier"]
            }
        }

        if validation_file_id:
            job_params["validation_file"] = validation_file_id

        # Create the fine-tuning job
        logger.info(f"Creating fine-tuning job with model: {self.training_config['model']}")
        job_response = self.client.fine_tuning.jobs.create(**job_params)

        job_result = {
            "job_id": job_response.id,
            "model": job_response.model,
            "status": job_response.status,
            "created_at": job_response.created_at,
            "training_file": job_response.training_file,
            "validation_file": getattr(job_response, 'validation_file', None),
            "hyperparameters": job_response.hyperparameters
        }

        # Store job info for monitoring
        self.training_jobs[job_response.id] = job_result

        logger.info(f"Fine-tuning job created: {job_response.id}")
        return job_result

    async def monitor_training_progress(self, job_id: str, check_interval: int = 30) -> Dict[str, Any]:
        """Monitor training progress until completion."""
        logger.info(f"Monitoring training progress for job: {job_id}")

        start_time = time.time()

        while True:
            try:
                # Get job status
                job = self.client.fine_tuning.jobs.retrieve(job_id)

                status = job.status
                logger.info(f"Job {job_id} status: {status}")

                if status in ["succeeded", "failed", "cancelled"]:
                    end_time = time.time()
                    duration = end_time - start_time

                    result = {
                        "job_id": job_id,
                        "status": status,
                        "duration_seconds": duration,
                        "model_id": getattr(job, 'fine_tuned_model', None),
                        "finished_at": getattr(job, 'finished_at', None),
                        "trained_tokens": getattr(job, 'trained_tokens', None),
                        "hyperparameters": job.hyperparameters
                    }

                    if status == "failed":
                        result["error"] = getattr(job, 'error', {}).get('message', 'Unknown error')

                    logger.info(f"Training {status} after {duration:.0f} seconds")
                    return result

                # Wait before next check
                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error monitoring job {job_id}: {e}")
                return {
                    "job_id": job_id,
                    "status": "error",
                    "error": str(e)
                }

    async def deploy_and_test_model(self, model_id: str) -> Dict[str, Any]:
        """Deploy and test the fine-tuned model."""
        logger.info(f"Deploying and testing model: {model_id}")

        # Test questions for model evaluation
        test_questions = [
            "What is the purpose of an AOI in PLC programming?",
            "How do you configure a motor control system?",
            "What are the safety requirements for emergency stop circuits?",
            "How do you troubleshoot communication errors in Ethernet/IP?",
            "What are best practices for tag naming conventions?"
        ]

        test_results = []

        for question in test_questions:
            try:
                # Test the fine-tuned model
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a PLC expert assistant. Provide accurate, detailed answers about PLC programming, configuration, and troubleshooting."
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ],
                    max_tokens=500,
                    temperature=0.1
                )

                test_results.append({
                    "question": question,
                    "answer": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens,
                    "status": "success"
                })

            except Exception as e:
                test_results.append({
                    "question": question,
                    "error": str(e),
                    "status": "error"
                })

        # Calculate success rate
        successful_tests = sum(1 for result in test_results if result["status"] == "success")
        success_rate = successful_tests / len(test_results) * 100

        deployment_result = {
            "model_id": model_id,
            "test_results": test_results,
            "success_rate": success_rate,
            "total_tests": len(test_results),
            "successful_tests": successful_tests,
            "deployment_status": "success" if success_rate >= 80 else "warning"
        }

        logger.info(f"Model testing completed: {success_rate:.1f}% success rate")
        return deployment_result

    async def generate_fine_tuning_report(self, orchestration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive fine-tuning report."""

        report = {
            "report_generated": datetime.now().isoformat(),
            "overall_status": orchestration_result["status"],
            "training_job_id": orchestration_result.get("training_job_id"),
            "model_id": orchestration_result.get("model_id"),
            "total_cost": orchestration_result.get("cost_estimate", {}).get("total_estimated_first_month_cost", 0),
            "summary": {},
            "recommendations": []
        }

        # Generate summary
        if orchestration_result["status"] == "completed":
            report["summary"]["message"] = "Fine-tuning completed successfully"
            report["summary"]["model_ready"] = True

            # Get deployment results
            deployment_step = next((s for s in orchestration_result["steps_completed"] if s["step"] == "deployment"), None)
            if deployment_step:
                success_rate = deployment_step["result"]["success_rate"]
                report["summary"]["test_success_rate"] = success_rate

                if success_rate >= 90:
                    report["recommendations"].append("Model performance is excellent. Ready for production use.")
                elif success_rate >= 80:
                    report["recommendations"].append("Model performance is good. Consider additional testing before full deployment.")
                else:
                    report["recommendations"].append("Model performance needs improvement. Consider retraining with more data.")

        else:
            report["summary"]["message"] = f"Fine-tuning failed: {orchestration_result.get('error', 'Unknown error')}"
            report["summary"]["model_ready"] = False
            report["recommendations"].append("Review training data quality and try again.")

        # Add general recommendations
        report["recommendations"].extend([
            "Monitor model performance in production",
            "Collect user feedback for continuous improvement",
            "Consider periodic retraining with new data",
            "Implement usage monitoring and cost tracking"
        ])

        return report


async def main():
    """Main execution for testing fine-tuning orchestrator."""

    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    orchestrator = FineTuningOrchestrator()

    # Example usage (requires actual training data)
    training_data_dir = "training_data"

    if not Path(training_data_dir).exists():
        print(f"Training data directory {training_data_dir} not found")
        print("Please run the training data generator first")
        return

    try:
        result = await orchestrator.orchestrate_complete_fine_tuning(training_data_dir)

        print("\n" + "="*60)
        print("FINE-TUNING ORCHESTRATION COMPLETE")
        print("="*60)
        print(f"Status: {result['status']}")
        print(f"Model ID: {result.get('model_id', 'N/A')}")
        print(f"Training Job ID: {result.get('training_job_id', 'N/A')}")
        print(f"Estimated Cost: ${result.get('cost_estimate', {}).get('total_estimated_first_month_cost', 0):.2f}")

        if result.get("final_report"):
            print(f"\nTest Success Rate: {result['final_report']['summary'].get('test_success_rate', 0):.1f}%")
            print("\nRecommendations:")
            for rec in result['final_report']['recommendations']:
                print(f"  - {rec}")

    except Exception as e:
        logger.error(f"Fine-tuning orchestration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
