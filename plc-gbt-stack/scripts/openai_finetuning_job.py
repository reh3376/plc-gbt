#!/usr/bin/env python3
"""
OpenAI Fine-tuning Job Submission Script
Phase 23: LLM Fine-tuning Integration

Uploads combined training data and submits fine-tuning job to OpenAI.
Combines industrial control theory knowledge with API integration capabilities.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openai_finetuning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OpenAIFineTuner:
    """OpenAI Fine-tuning Job Manager"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Try to load from .env file if not found
        if not self.api_key:
            env_file = Path(__file__).parent.parent.parent / '.env'
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.startswith('OPENAI_API_KEY='):
                            self.api_key = line.split('=', 1)[1].strip().strip('"\'')
                            break

        # Prompt for API key if still not found
        if not self.api_key:
            print("OpenAI API key not found in environment or .env file.")
            print("Please provide your OpenAI API key for fine-tuning:")
            self.api_key = input("API Key: ").strip()

            if not self.api_key:
                raise ValueError("OpenAI API key is required for fine-tuning.")

        self.client = OpenAI(api_key=self.api_key)
        self.project_root = Path(__file__).parent.parent

    def validate_training_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate JSONL training file format"""
        logger.info(f"Validating training file: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"Training file not found: {file_path}")

        validation_results = {
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'total_lines': 0,
            'valid_lines': 0,
            'errors': [],
            'sample_entries': []
        }

        with open(file_path, encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                validation_results['total_lines'] = line_num

                if not line.strip():
                    continue

                try:
                    # Parse JSON
                    entry = json.loads(line.strip())

                    # Validate structure
                    if 'messages' not in entry:
                        validation_results['errors'].append(f"Line {line_num}: Missing 'messages' key")
                        continue

                    if not isinstance(entry['messages'], list):
                        validation_results['errors'].append(f"Line {line_num}: 'messages' must be a list")
                        continue

                    if len(entry['messages']) < 2:
                        validation_results['errors'].append(f"Line {line_num}: Need at least user and assistant messages")
                        continue

                    # Validate message structure
                    for msg_idx, message in enumerate(entry['messages']):
                        if not isinstance(message, dict):
                            validation_results['errors'].append(f"Line {line_num}, message {msg_idx}: Must be dict")
                            continue

                        if 'role' not in message or 'content' not in message:
                            validation_results['errors'].append(f"Line {line_num}, message {msg_idx}: Missing role or content")
                            continue

                        if message['role'] not in ['user', 'assistant', 'system']:
                            validation_results['errors'].append(f"Line {line_num}, message {msg_idx}: Invalid role")
                            continue

                    validation_results['valid_lines'] += 1

                    # Store sample entries
                    if len(validation_results['sample_entries']) < 3:
                        validation_results['sample_entries'].append({
                            'line': line_num,
                            'user_content': entry['messages'][0]['content'][:100] + "..." if len(entry['messages'][0]['content']) > 100 else entry['messages'][0]['content'],
                            'assistant_content': entry['messages'][1]['content'][:100] + "..." if len(entry['messages'][1]['content']) > 100 else entry['messages'][1]['content']
                        })

                except json.JSONDecodeError as e:
                    validation_results['errors'].append(f"Line {line_num}: JSON decode error - {str(e)}")
                except Exception as e:
                    validation_results['errors'].append(f"Line {line_num}: Validation error - {str(e)}")

        validation_results['success'] = len(validation_results['errors']) == 0
        validation_results['error_rate'] = len(validation_results['errors']) / validation_results['total_lines'] if validation_results['total_lines'] > 0 else 0

        logger.info(f"Validation complete: {validation_results['valid_lines']}/{validation_results['total_lines']} valid entries")
        if validation_results['errors']:
            logger.warning(f"Found {len(validation_results['errors'])} validation errors")
            for error in validation_results['errors'][:5]:  # Show first 5 errors
                logger.warning(f"  {error}")

        return validation_results

    def upload_training_file(self, file_path: Path) -> str:
        """Upload training file to OpenAI"""
        logger.info(f"Uploading training file: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose='fine-tune'
                )

            file_id = response.id
            logger.info(f"Training file uploaded successfully. File ID: {file_id}")

            # Wait for file to be processed
            logger.info("Waiting for file processing...")
            while True:
                file_info = self.client.files.retrieve(file_id)
                if file_info.status == 'processed':
                    logger.info("File processed successfully")
                    break
                elif file_info.status == 'error':
                    raise Exception(f"File processing failed: {file_info}")
                else:
                    logger.info(f"File status: {file_info.status}")
                    time.sleep(5)

            return file_id

        except Exception as e:
            logger.error(f"Failed to upload training file: {str(e)}")
            raise

    def submit_fine_tuning_job(self, training_file_id: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """Submit fine-tuning job to OpenAI"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"industrial-control-api-bridge-{timestamp}"

        logger.info(f"Submitting fine-tuning job for model: {model}")
        logger.info(f"Training file ID: {training_file_id}")
        logger.info(f"Model suffix: {suffix}")

        try:
            job = self.client.fine_tuning.jobs.create(
                training_file=training_file_id,
                model=model,
                suffix=suffix,
                hyperparameters={
                    "n_epochs": 3,  # Conservative number of epochs
                    "batch_size": "auto",
                    "learning_rate_multiplier": "auto"
                }
            )

            job_info = {
                'job_id': job.id,
                'model': model,
                'training_file': training_file_id,
                'suffix': suffix,
                'status': job.status,
                'created_at': job.created_at,
                'estimated_finish': job.estimated_finish,
                'fine_tuned_model': job.fine_tuned_model,
                'hyperparameters': job.hyperparameters
            }

            logger.info("Fine-tuning job submitted successfully!")
            logger.info(f"Job ID: {job.id}")
            logger.info(f"Status: {job.status}")
            if job.estimated_finish:
                finish_time = datetime.fromtimestamp(job.estimated_finish)
                logger.info(f"Estimated completion: {finish_time}")

            return job_info

        except Exception as e:
            logger.error(f"Failed to submit fine-tuning job: {str(e)}")
            raise

    def monitor_job_progress(self, job_id: str) -> Dict[str, Any]:
        """Monitor fine-tuning job progress"""
        logger.info(f"Monitoring fine-tuning job: {job_id}")

        start_time = time.time()

        while True:
            try:
                job = self.client.fine_tuning.jobs.retrieve(job_id)

                elapsed_time = time.time() - start_time
                logger.info(f"Job status: {job.status} (elapsed: {elapsed_time/60:.1f} min)")

                if job.status == 'succeeded':
                    logger.info("✅ Fine-tuning completed successfully!")
                    logger.info(f"Fine-tuned model ID: {job.fine_tuned_model}")

                    return {
                        'success': True,
                        'model_id': job.fine_tuned_model,
                        'status': job.status,
                        'elapsed_time': elapsed_time,
                        'training_file': job.training_file,
                        'result_files': job.result_files
                    }

                elif job.status == 'failed':
                    logger.error("❌ Fine-tuning failed!")
                    logger.error(f"Error: {job}")

                    return {
                        'success': False,
                        'status': job.status,
                        'error': str(job),
                        'elapsed_time': elapsed_time
                    }

                elif job.status in ['cancelled', 'cancelling']:
                    logger.warning("⚠️ Fine-tuning was cancelled")

                    return {
                        'success': False,
                        'status': job.status,
                        'elapsed_time': elapsed_time
                    }

                else:
                    # Job still running
                    if job.estimated_finish:
                        finish_time = datetime.fromtimestamp(job.estimated_finish)
                        logger.info(f"Estimated completion: {finish_time}")

                    # Check for progress updates
                    if hasattr(job, 'trained_tokens') and job.trained_tokens:
                        logger.info(f"Trained tokens: {job.trained_tokens}")

                    time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error monitoring job: {str(e)}")
                time.sleep(60)  # Wait longer on error

    def run_complete_fine_tuning(self, training_file_path: str) -> Dict[str, Any]:
        """Execute complete fine-tuning workflow"""
        logger.info("🚀 Starting OpenAI Fine-tuning Workflow")
        logger.info("=" * 50)

        try:
            # Convert to Path object
            file_path = Path(training_file_path)

            # Step 1: Validate training file
            logger.info("📋 Step 1: Validating training file...")
            validation = self.validate_training_file(file_path)

            if not validation['success']:
                logger.error("❌ Training file validation failed!")
                logger.error(f"Errors found: {len(validation['errors'])}")
                return {'success': False, 'error': 'Validation failed', 'validation': validation}

            logger.info(f"✅ Training file valid: {validation['valid_lines']} samples")
            logger.info(f"File size: {validation['file_size_mb']:.2f} MB")

            # Step 2: Upload training file
            logger.info("📤 Step 2: Uploading training file...")
            file_id = self.upload_training_file(file_path)

            # Step 3: Submit fine-tuning job
            logger.info("🎯 Step 3: Submitting fine-tuning job...")
            job_info = self.submit_fine_tuning_job(file_id)

            # Step 4: Monitor progress
            logger.info("⏱️ Step 4: Monitoring job progress...")
            result = self.monitor_job_progress(job_info['job_id'])

            # Combine all information
            final_result = {
                'success': result['success'],
                'validation': validation,
                'file_id': file_id,
                'job_info': job_info,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }

            if result['success']:
                logger.info("🎉 Fine-tuning completed successfully!")
                logger.info(f"New model ID: {result['model_id']}")

                # Save result to file
                result_file = self.project_root / 'plc-gbt-stack' / 'results' / f"fine_tuning_result_{int(time.time())}.json"
                result_file.parent.mkdir(exist_ok=True)

                with open(result_file, 'w') as f:
                    json.dump(final_result, f, indent=2)

                logger.info(f"Results saved to: {result_file}")

            return final_result

        except Exception as e:
            logger.error(f"❌ Fine-tuning workflow failed: {str(e)}")
            return {'success': False, 'error': str(e)}

def main():
    """Main execution function"""
    try:
        # Initialize fine-tuner
        fine_tuner = OpenAIFineTuner()

        # Set training file path
        training_file_path = "plc-gbt-stack/training_data/combined_industrial_api_training_data.jsonl"

        # Run complete fine-tuning workflow
        result = fine_tuner.run_complete_fine_tuning(training_file_path)

        if result['success']:
            print("\n" + "="*60)
            print("🎉 FINE-TUNING COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"New Model ID: {result['result']['model_id']}")
            print(f"Training Samples: {result['validation']['valid_lines']}")
            print(f"Training Time: {result['result']['elapsed_time']/60:.1f} minutes")
            print("\nNext Steps:")
            print("1. Update LLM_CONFIG with new model ID")
            print("2. Test integration with CLI-to-API bridge")
            print("3. Validate end-to-end functionality")
            return 0
        else:
            print("\n" + "="*60)
            print("❌ FINE-TUNING FAILED!")
            print("="*60)
            print(f"Error: {result.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        logger.error(f"Script execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
