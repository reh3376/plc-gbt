#!/usr/bin/env python3
"""
Fine-Tuning Progress Monitor
Monitors the active fine-tuning job and deploys the model when complete

Usage:
    python3 monitor_fine_tuning.py [job_id]
"""

import os
import time
import json
from datetime import datetime
from openai import OpenAI
import argparse

def monitor_fine_tuning_job(job_id: str, check_interval: int = 30):
    """Monitor fine-tuning job progress with periodic updates."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print(f"🔍 Monitoring fine-tuning job: {job_id}")
    print(f"⏰ Check interval: {check_interval} seconds")
    print("=" * 60)
    
    while True:
        try:
            job = client.fine_tuning.jobs.retrieve(job_id)
            
            # Display current status
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Status: {job.status}")
            
            if job.status == "succeeded":
                print(f"✅ Fine-tuning completed successfully!")
                print(f"🤖 Fine-tuned model: {job.fine_tuned_model}")
                
                # Test the model
                test_model(job.fine_tuned_model)
                break
                
            elif job.status == "failed":
                print(f"❌ Fine-tuning failed!")
                if job.error:
                    print(f"Error: {job.error}")
                break
                
            elif job.status == "cancelled":
                print(f"⚠️ Fine-tuning was cancelled")
                break
                
            elif job.status in ["validating_files", "queued", "running"]:
                print(f"🔄 Fine-tuning in progress...")
                if hasattr(job, 'trained_tokens') and job.trained_tokens:
                    print(f"   Tokens processed: {job.trained_tokens:,}")
                    
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"❌ Error checking job status: {e}")
            time.sleep(check_interval)

def test_model(model_id: str):
    """Test the fine-tuned model with PLC-specific questions."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print(f"\n🧪 Testing fine-tuned model: {model_id}")
    print("=" * 60)
    
    # Test questions for PLC domain
    test_questions = [
        "What is an AOI in PLC programming?",
        "How do you configure a CompactLogix controller?",
        "What's the difference between ST and ladder logic?",
        "How do you troubleshoot communication errors in Studio 5000?",
        "What are the best practices for PLC tag naming?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}: {question}")
        print("-" * 40)
        
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are a PLC programming expert with extensive knowledge of Allen-Bradley systems, Studio 5000, and industrial automation."},
                    {"role": "user", "content": question}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"📝 Answer: {answer}")
            
        except Exception as e:
            print(f"❌ Error testing model: {e}")
    
    print(f"\n✅ Model testing complete!")
    print(f"🚀 Fine-tuned model {model_id} is ready for deployment!")

def get_latest_job_id():
    """Get the most recent fine-tuning job ID."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    jobs = client.fine_tuning.jobs.list(limit=1)
    if jobs.data:
        return jobs.data[0].id
    return None

def main():
    parser = argparse.ArgumentParser(description='Monitor fine-tuning job progress')
    parser.add_argument('job_id', nargs='?', help='Fine-tuning job ID (optional - will use latest)')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    # Get job ID
    job_id = args.job_id
    if not job_id:
        print("🔍 No job ID provided, finding latest job...")
        job_id = get_latest_job_id()
        if not job_id:
            print("❌ No fine-tuning jobs found!")
            return
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        return
    
    # Start monitoring
    monitor_fine_tuning_job(job_id, args.interval)

if __name__ == "__main__":
    main() 