#!/usr/bin/env python3
"""
Quick script to check available OpenAI models for fine-tuning
"""

import os
from openai import OpenAI

# Get API key from user input
api_key = input("Enter OpenAI API key: ").strip()
client = OpenAI(api_key=api_key)

try:
    # List available models
    models = client.models.list()
    
    print("Available models for fine-tuning:")
    print("=" * 40)
    
    fine_tunable_models = []
    for model in models.data:
        # Check if model can be fine-tuned
        try:
            # Models that are typically fine-tunable
            if any(name in model.id for name in ['gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-4o-2024']):
                fine_tunable_models.append(model.id)
                print(f"✅ {model.id}")
        except:
            pass
    
    if not fine_tunable_models:
        print("❌ No fine-tunable models found")
        print("\nAll available models:")
        for model in models.data:
            print(f"   {model.id}")
    
    print(f"\nRecommended model for fine-tuning: gpt-4o-mini")
    
except Exception as e:
    print(f"Error: {str(e)}") 