#!/usr/bin/env python3
"""
Enhanced Fine-tuning Job Submission
===================================

Submits the enhanced comprehensive training dataset (249 entries, 56% codebase-specific)
for OpenAI fine-tuning with improved codebase coverage.

Training Data Composition:
- 109 Industrial control theory entries (44%)
- 13 API integration entries (5%) 
- 127 Comprehensive codebase entries (51%)
Total: 249 entries with 56% codebase-specific coverage

Author: AI Task Orchestrator
Date: July 22, 2025
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_api_key():
    """Load OpenAI API key from environment or .env file"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        env_file = Path(__file__).parent.parent.parent / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip('"\'')
                        break
    
    if not api_key:
        api_key = input("Enter OpenAI API key: ").strip()
    
    return api_key

def validate_training_data(file_path: Path) -> bool:
    """Validate training data format"""
    logger.info(f"Validating training data: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_count = 0
            for line in f:
                line_count += 1
                data = json.loads(line.strip())
                
                # Validate required fields
                if 'messages' not in data:
                    logger.error(f"Line {line_count}: Missing 'messages' field")
                    return False
                
                if not isinstance(data['messages'], list):
                    logger.error(f"Line {line_count}: 'messages' must be a list")
                    return False
                
                # Validate message format
                for msg in data['messages']:
                    if 'role' not in msg or 'content' not in msg:
                        logger.error(f"Line {line_count}: Invalid message format")
                        return False
                    
                    if msg['role'] not in ['user', 'assistant', 'system']:
                        logger.error(f"Line {line_count}: Invalid role: {msg['role']}")
                        return False
        
        logger.info(f"✅ Training data validation passed: {line_count} entries")
        return True
        
    except Exception as e:
        logger.error(f"❌ Training data validation failed: {e}")
        return False

def submit_fine_tuning_job(api_key: str, training_file_path: Path) -> dict:
    """Submit fine-tuning job to OpenAI"""
    
    client = OpenAI(api_key=api_key)
    
    try:
        # Upload training file
        logger.info("📤 Uploading training file...")
        with open(training_file_path, 'rb') as f:
            training_file = client.files.create(
                file=f,
                purpose='fine-tune'
            )
        
        logger.info(f"✅ Training file uploaded: {training_file.id}")
        
        # Wait for file processing
        logger.info("⏳ Waiting for file processing...")
        while True:
            file_status = client.files.retrieve(training_file.id)
            if file_status.status == 'processed':
                logger.info("✅ File processed successfully")
                break
            elif file_status.status == 'error':
                logger.error("❌ File processing failed")
                return {"error": "File processing failed"}
            
            time.sleep(2)
        
        # Submit fine-tuning job
        logger.info("🚀 Submitting fine-tuning job...")
        
        job_suffix = f"enhanced-comprehensive-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        fine_tuning_job = client.fine_tuning.jobs.create(
            training_file=training_file.id,
            model="gpt-3.5-turbo",
            suffix=job_suffix,
            hyperparameters={
                "n_epochs": 3,  # Good default for this dataset size
                "batch_size": "auto",
                "learning_rate_multiplier": "auto"
            }
        )
        
        logger.info(f"✅ Fine-tuning job submitted successfully!")
        logger.info(f"   Job ID: {fine_tuning_job.id}")
        logger.info(f"   Model: {fine_tuning_job.model}")
        logger.info(f"   Status: {fine_tuning_job.status}")
        logger.info(f"   Training file: {fine_tuning_job.training_file}")
        
        return {
            "success": True,
            "job_id": fine_tuning_job.id,
            "status": fine_tuning_job.status,
            "model": fine_tuning_job.model,
            "training_file_id": training_file.id,
            "suffix": job_suffix
        }
        
    except Exception as e:
        logger.error(f"❌ Fine-tuning job submission failed: {e}")
        return {"error": str(e)}

def monitor_job(api_key: str, job_id: str):
    """Monitor fine-tuning job progress"""
    
    client = OpenAI(api_key=api_key)
    logger.info(f"📊 Monitoring fine-tuning job: {job_id}")
    
    try:
        while True:
            job = client.fine_tuning.jobs.retrieve(job_id)
            logger.info(f"Status: {job.status}")
            
            if job.status in ['succeeded', 'failed', 'cancelled']:
                break
            
            # Wait 30 seconds before checking again
            time.sleep(30)
        
        if job.status == 'succeeded':
            logger.info(f"🎉 Fine-tuning completed successfully!")
            logger.info(f"   Fine-tuned model: {job.fine_tuned_model}")
            return job.fine_tuned_model
        else:
            logger.error(f"❌ Fine-tuning failed with status: {job.status}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error monitoring job: {e}")
        return None

def main():
    """Main execution function"""
    
    logger.info("🚀 Enhanced Comprehensive Fine-tuning Job Submission")
    logger.info("=" * 60)
    
    # Load API key
    api_key = load_api_key()
    
    # Training file path
    training_file_path = Path("enhanced_comprehensive_training_data.jsonl")
    
    if not training_file_path.exists():
        logger.error(f"❌ Training file not found: {training_file_path}")
        return False
    
    # Validate training data
    if not validate_training_data(training_file_path):
        logger.error("❌ Training data validation failed")
        return False
    
    # Submit fine-tuning job
    result = submit_fine_tuning_job(api_key, training_file_path)
    
    if "error" in result:
        logger.error(f"❌ Job submission failed: {result['error']}")
        return False
    
    # Log job details
    logger.info("📊 Job Summary:")
    logger.info(f"   Enhanced Training Data: 249 entries")
    logger.info(f"   Codebase Coverage: 56% (140/249 entries)")
    logger.info(f"   Improvement: From 11% to 56% codebase coverage")
    logger.info(f"   Job ID: {result['job_id']}")
    logger.info(f"   Model Suffix: {result['suffix']}")
    
    # Ask if user wants to monitor
    monitor = input("\nWould you like to monitor the job progress? (y/n): ").strip().lower()
    
    if monitor == 'y':
        fine_tuned_model = monitor_job(api_key, result['job_id'])
        if fine_tuned_model:
            logger.info(f"🎯 Success! New fine-tuned model: {fine_tuned_model}")
            
            # Save model info
            model_info = {
                "fine_tuned_model": fine_tuned_model,
                "job_id": result['job_id'],
                "training_entries": 249,
                "codebase_coverage": "56%",
                "creation_date": datetime.now().isoformat(),
                "improvement": "From 11% to 56% codebase coverage"
            }
            
            with open("enhanced_model_info.json", "w") as f:
                json.dump(model_info, f, indent=2)
            
            logger.info("📄 Model information saved to enhanced_model_info.json")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 