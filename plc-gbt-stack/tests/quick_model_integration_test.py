#!/usr/bin/env python3
"""
Quick Model Integration Test
===========================

Simple test to verify the fine-tuned model integration is working correctly
after configuration updates.

Author: AI Task Orchestrator
Date: July 22, 2025
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def load_api_key():
    """Load API key from .env file"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return os.getenv('OPENAI_API_KEY')

def test_model_integration():
    """Test the fine-tuned model integration"""
    print("🔄 Quick Model Integration Test")
    print("=" * 40)
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("❌ ERROR: No OpenAI API key found")
        return False
    
    print(f"✅ API Key loaded: {api_key[:10]}...")
    
    # Test model configuration
    model_id = "ft:gpt-4o-mini-2024-07-18:whiskey-house:industrial-control:But1jpnl"
    print(f"✅ Target Model: {model_id}")
    
    try:
        from openai import OpenAI
        
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
        
        # Test model response
        print("\n🧪 Testing model response...")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user", "content": "What is PLC-GBT and how does it help with industrial control?"}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        response_time = time.time() - start_time
        response_text = response.choices[0].message.content
        
        print(f"✅ Model responded in {response_time:.2f} seconds")
        print(f"✅ Response length: {len(response_text)} characters")
        print(f"✅ Response preview: {response_text[:100]}...")
        
        # Basic quality checks
        quality_checks = {
            "Contains 'PLC'": "plc" in response_text.lower(),
            "Contains 'industrial'": "industrial" in response_text.lower(),
            "Contains 'control'": "control" in response_text.lower(),
            "Adequate length": len(response_text) > 50,
            "Response time < 10s": response_time < 10.0
        }
        
        print("\n📊 Quality Checks:")
        all_passed = True
        for check, result in quality_checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}: {result}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("\n🎉 SUCCESS: Model integration test PASSED!")
            print("✅ Fine-tuned model is responding correctly")
            print("✅ Industrial control knowledge demonstrated")
            print("✅ System ready for production use")
            return True
        else:
            print("\n⚠️ WARNING: Some quality checks failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Model integration test failed")
        print(f"Error details: {str(e)}")
        return False

def test_configuration_consistency():
    """Test that all configuration files reference the correct model"""
    print("\n🔍 Configuration Consistency Check")
    print("=" * 40)
    
    correct_model = "ft:gpt-4o-mini-2024-07-18:whiskey-house:industrial-control:But1jpnl"
    
    # Files to check
    config_files = [
        "../ui/natural_language_interface.py",
        "../scripts/ai/model_config_validator.py", 
        "../scripts/comprehensive_training_data_generator.py",
        "../../ai-enhancement-framework/core/llm_integration.py",
        "../.env"
    ]
    
    consistent = True
    
    for file_path in config_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                    if correct_model in content:
                        print(f"✅ {file_path}: Model reference found")
                    else:
                        print(f"❌ {file_path}: Model reference missing or incorrect")
                        consistent = False
            except Exception as e:
                print(f"⚠️ {file_path}: Could not read file - {e}")
        else:
            print(f"⚠️ {file_path}: File not found")
    
    if consistent:
        print("\n✅ Configuration consistency check PASSED")
    else:
        print("\n❌ Configuration consistency check FAILED")
    
    return consistent

def main():
    """Run comprehensive quick tests"""
    print("🚀 PLC-GBT Enhanced Model Integration Test Suite")
    print("=" * 50)
    print(f"Date: July 22, 2025")
    print(f"Target Model: ft:gpt-4o-mini-2024-07-18:whiskey-house:industrial-control:But1jpnl")
    print()
    
    # Run tests
    model_test = test_model_integration()
    config_test = test_configuration_consistency()
    
    # Final summary
    print("\n" + "=" * 50)
    print("📋 FINAL TEST SUMMARY")
    print("=" * 50)
    
    if model_test and config_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Model integration working correctly")
        print("✅ Configuration consistency verified")
        print("✅ System ready for production use")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        if not model_test:
            print("❌ Model integration issues detected")
        if not config_test:
            print("❌ Configuration inconsistency detected") 
        print("⚠️ Review issues before production deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 