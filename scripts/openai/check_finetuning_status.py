#!/usr/bin/env python3
"""
Quick status check for OpenAI fine-tuning job
"""

import os
from openai import OpenAI

# Job ID from our submitted job
job_id = "ftjob-CtTZerCIsyT8Z1H9MbseAtmI"

# Get API key
api_key = input("Enter OpenAI API key: ").strip()
client = OpenAI(api_key=api_key)

try:
    # Get job status
    job = client.fine_tuning.jobs.retrieve(job_id)
    
    print(f"🔍 Fine-tuning Job Status Check")
    print("=" * 40)
    print(f"Job ID: {job.id}")
    print(f"Status: {job.status}")
    print(f"Model: {job.model}")
    print(f"Created: {job.created_at}")
    
    if job.fine_tuned_model:
        print(f"✅ Fine-tuned Model: {job.fine_tuned_model}")
    
    if job.estimated_finish:
        from datetime import datetime
        finish_time = datetime.fromtimestamp(job.estimated_finish)
        print(f"Estimated Finish: {finish_time}")
    
    if hasattr(job, 'trained_tokens') and job.trained_tokens:
        print(f"Trained Tokens: {job.trained_tokens}")
        
    if job.status == 'succeeded':
        print(f"\n🎉 SUCCESS! Fine-tuning completed!")
        print(f"New Model ID: {job.fine_tuned_model}")
    elif job.status == 'failed':
        print(f"\n❌ FAILED! Fine-tuning failed.")
        if hasattr(job, 'error'):
            print(f"Error: {job.error}")
    elif job.status in ['running', 'validating_files', 'queued']:
        print(f"\n⏳ IN PROGRESS: {job.status}")
    
except Exception as e:
    print(f"Error checking job status: {str(e)}") 