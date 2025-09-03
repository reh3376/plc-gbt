#!/usr/bin/env python3
"""
check_fine_tuning_status.py - Check status of OpenAI fine-tuning job
=====================================================================

Monitors the progress of a fine-tuning job and displays key information.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

import openai

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))


def check_job_status(job_id: str = None):
    """Check the status of a fine-tuning job."""

    # Initialize OpenAI client
    client = openai.OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    # Use provided job ID or get from environment
    if not job_id:
        job_id = os.environ.get("OPENAI_FINETUNE_JOB_ID", "ftjob-FyqfDD3U8fRnNCUxmgojm4Yw")

    print(f"\n{'='*60}")
    print("🤖 OpenAI Fine-Tuning Job Status")
    print(f"{'='*60}")
    print(f"Job ID: {job_id}")
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    try:
        # Get job status
        job = client.fine_tuning.jobs.retrieve(job_id)

        print("📊 Job Information:")
        print(f"   Status: {job.status}")
        print(f"   Model: {job.model}")
        print(f"   Created: {datetime.fromtimestamp(job.created_at).strftime('%Y-%m-%d %H:%M:%S')}")

        if hasattr(job, 'finished_at') and job.finished_at:
            print(f"   Finished: {datetime.fromtimestamp(job.finished_at).strftime('%Y-%m-%d %H:%M:%S')}")
            duration = job.finished_at - job.created_at
            print(f"   Duration: {duration // 60} minutes {duration % 60} seconds")

        if hasattr(job, 'fine_tuned_model') and job.fine_tuned_model:
            print(f"\n✅ Fine-tuned Model ID: {job.fine_tuned_model}")

        if hasattr(job, 'trained_tokens') and job.trained_tokens:
            print("\n📈 Training Statistics:")
            print(f"   Trained Tokens: {job.trained_tokens:,}")

        # Get recent events
        print("\n📜 Recent Events:")
        events = client.fine_tuning.jobs.list_events(job_id, limit=10)
        for event in reversed(list(events.data)):
            timestamp = datetime.fromtimestamp(event.created_at).strftime('%H:%M:%S')
            print(f"   [{timestamp}] {event.message}")

        # Estimate completion if still running
        if job.status == "running":
            print("\n⏳ Job is still running...")
            print("   Tip: Fine-tuning typically takes 20-40 minutes for small datasets")

        elif job.status == "succeeded":
            print("\n🎉 Fine-tuning completed successfully!")
            print("\n📋 Next Steps:")
            print("   1. Update .env file:")
            print(f"      OPENAI_FINETUNE_MODEL={job.fine_tuned_model}")
            print("   2. Test the model:")
            print("      python3 test_fine_tuned_model.py")

        elif job.status == "failed":
            print("\n❌ Fine-tuning failed!")
            if hasattr(job, 'error') and job.error:
                print(f"   Error: {job.error}")

        return job

    except Exception as e:
        print(f"❌ Error checking job status: {e}")
        return None


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Check OpenAI fine-tuning job status')
    parser.add_argument('--job-id', type=str, help='Fine-tuning job ID')
    parser.add_argument('--watch', action='store_true', help='Continuously monitor job')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds (default: 30)')

    args = parser.parse_args()

    if args.watch:
        print("🔄 Monitoring job status (press Ctrl+C to stop)...")
        try:
            while True:
                job = check_job_status(args.job_id)
                if job and job.status in ["succeeded", "failed", "cancelled"]:
                    break
                time.sleep(args.interval)
                print("\n" * 3)  # Clear space between updates
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped.")
    else:
        check_job_status(args.job_id)


if __name__ == "__main__":
    main()
