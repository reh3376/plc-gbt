#!/usr/bin/env python3
"""
OpenAI Enterprise Configuration Test Script
Phase 2 Implementation - PLC-Savvy GPT

This script tests OpenAI Enterprise API access and configuration.
Run this script to verify your OpenAI Enterprise setup is working correctly.
"""

import json
import os
import sys
import time
from datetime import datetime

try:
    import openai
    import requests
except ImportError:
    print("❌ Missing required packages. Install with:")
    print("pip install openai requests")
    sys.exit(1)


class OpenAIConfigTester:
    """Test OpenAI Enterprise configuration and API access."""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.org_id = os.getenv('OPENAI_ORG_ID')
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

        # Configure OpenAI client
        if self.api_key:
            openai.api_key = self.api_key
            if self.org_id:
                openai.organization = self.org_id

        self.test_results = {}
        # Use models from environment configuration
        self.required_models = [
            os.getenv('OPENAI_PRIMARY_MODEL', 'gpt-4o'),
            os.getenv('OPENAI_FALLBACK_MODEL', 'gpt-4o-mini'),
            os.getenv('OPENAI_REASONING_MODEL', 'o1-mini'),
            os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large'),
            'text-embedding-ada-002'  # Keep as backup
        ]

    def print_header(self):
        """Print test header."""
        print("=" * 70)
        print("🧪 OpenAI Enterprise Configuration Test")
        print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 70)

    def test_environment_variables(self) -> bool:
        """Test if required environment variables are set."""
        print("\n🔧 Testing Environment Variables...")

        required_vars = ['OPENAI_API_KEY', 'OPENAI_ORG_ID']
        optional_vars = ['OPENAI_BASE_URL', 'GATEWAY_BEARER']

        success = True

        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if 'KEY' in var or 'TOKEN' in var:
                    display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    display_value = value
                print(f"  ✅ {var}: {display_value}")
            else:
                print(f"  ❌ {var}: Not set")
                success = False

        for var in optional_vars:
            value = os.getenv(var)
            if value:
                if 'KEY' in var or 'TOKEN' in var:
                    display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    display_value = value
                print(f"  ℹ️  {var}: {display_value}")
            else:
                print(f"  ⚠️  {var}: Not set (optional)")

        self.test_results['environment_variables'] = success
        return success

    def test_api_connectivity(self) -> bool:
        """Test basic API connectivity."""
        print("\n🌐 Testing API Connectivity...")

        if not self.api_key:
            print("  ❌ No API key configured")
            self.test_results['api_connectivity'] = False
            return False

        try:
            # Test basic API call
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            if self.org_id:
                headers['OpenAI-Organization'] = self.org_id

            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                print("  ✅ API connectivity: Success")
                print(f"  ✅ Response time: {response.elapsed.total_seconds():.2f}s")
                self.test_results['api_connectivity'] = True
                return True
            else:
                print(f"  ❌ API Error: {response.status_code} - {response.text}")
                self.test_results['api_connectivity'] = False
                return False

        except requests.RequestException as e:
            print(f"  ❌ Connection Error: {e}")
            self.test_results['api_connectivity'] = False
            return False

    def test_model_access(self) -> bool:
        """Test access to required models."""
        print("\n🤖 Testing Model Access...")

        if not self.api_key:
            print("  ❌ No API key configured")
            self.test_results['model_access'] = False
            return False

        try:
            # Get available models
            response = openai.models.list()
            available_models = [model.id for model in response.data]

            print(f"  ℹ️  Total models available: {len(available_models)}")

            # Check for required models
            model_results = {}
            for model in self.required_models:
                if model in available_models:
                    print(f"  ✅ {model}: Available")
                    model_results[model] = True
                else:
                    print(f"  ❌ {model}: Not available")
                    model_results[model] = False

            # Check for fine-tuned models
            fine_tuned_models = [m for m in available_models if m.startswith('ft:')]
            if fine_tuned_models:
                print(f"  ℹ️  Fine-tuned models found: {len(fine_tuned_models)}")
                for model in fine_tuned_models[:3]:  # Show first 3
                    print(f"    - {model}")
            else:
                print("  ℹ️  No fine-tuned models found")

            success = all(model_results.values())
            self.test_results['model_access'] = {
                'success': success,
                'models': model_results,
                'available_count': sum(model_results.values()),
                'total_count': len(model_results)
            }
            return success

        except Exception as e:
            print(f"  ❌ Error retrieving models: {e}")
            self.test_results['model_access'] = False
            return False

    def test_chat_completion(self) -> bool:
        """Test chat completion functionality."""
        print("\n💬 Testing Chat Completion...")

        if not self.api_key:
            print("  ❌ No API key configured")
            self.test_results['chat_completion'] = False
            return False

        try:
            # Use configured primary model
            model = os.getenv('OPENAI_PRIMARY_MODEL', 'gpt-4o')

            start_time = time.time()
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is a PLC in industrial automation? (One sentence answer)"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            end_time = time.time()

            response_time = end_time - start_time
            response_text = response.choices[0].message.content.strip()

            print(f"  ✅ Model: {model}")
            print(f"  ✅ Response time: {response_time:.2f}s")
            print(f"  ✅ Token usage: {response.usage.total_tokens}")
            print(f"  ✅ Response: {response_text[:100]}{'...' if len(response_text) > 100 else ''}")

            self.test_results['chat_completion'] = {
                'success': True,
                'model': model,
                'response_time': response_time,
                'tokens': response.usage.total_tokens
            }
            return True

        except Exception as e:
            print(f"  ❌ Chat completion error: {e}")
            self.test_results['chat_completion'] = False
            return False

    def test_embedding_generation(self) -> bool:
        """Test embedding generation."""
        print("\n🧠 Testing Embedding Generation...")

        if not self.api_key:
            print("  ❌ No API key configured")
            self.test_results['embedding_generation'] = False
            return False

        try:
            model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
            text = "This is a test document for PLC programming and industrial automation."

            start_time = time.time()
            response = openai.embeddings.create(
                model=model,
                input=text
            )
            end_time = time.time()

            response_time = end_time - start_time
            embedding = response.data[0].embedding

            print(f"  ✅ Model: {model}")
            print(f"  ✅ Response time: {response_time:.2f}s")
            print(f"  ✅ Embedding dimensions: {len(embedding)}")
            print(f"  ✅ Token usage: {response.usage.total_tokens}")

            # Verify expected dimensions for text-embedding-3-large
            expected_dims = 3072
            if len(embedding) == expected_dims:
                print(f"  ✅ Dimensions match expected ({expected_dims})")
            else:
                print(f"  ⚠️  Unexpected dimensions: got {len(embedding)}, expected {expected_dims}")

            self.test_results['embedding_generation'] = {
                'success': True,
                'model': model,
                'response_time': response_time,
                'dimensions': len(embedding),
                'tokens': response.usage.total_tokens
            }
            return True

        except Exception as e:
            print(f"  ❌ Embedding generation error: {e}")
            self.test_results['embedding_generation'] = False
            return False

    def test_rate_limits(self) -> bool:
        """Test API rate limits (basic check)."""
        print("\n⏱️  Testing Rate Limits...")

        if not self.api_key:
            print("  ❌ No API key configured")
            self.test_results['rate_limits'] = False
            return False

        try:
            # Make several quick requests to test rate limiting
            request_times = []
            test_model = os.getenv('OPENAI_FALLBACK_MODEL', 'gpt-4o-mini')
            for i in range(3):
                start_time = time.time()
                openai.chat.completions.create(
                    model=test_model,
                    messages=[{"role": "user", "content": f"Test message {i+1}"}],
                    max_tokens=10
                )
                end_time = time.time()
                request_times.append(end_time - start_time)
                time.sleep(0.5)  # Small delay between requests

            avg_response_time = sum(request_times) / len(request_times)
            print(f"  ✅ Average response time: {avg_response_time:.2f}s")
            print("  ✅ No rate limiting detected in test")

            # Check response headers for rate limit info
            print("  ℹ️  Rate limit info available in API headers")

            self.test_results['rate_limits'] = {
                'success': True,
                'avg_response_time': avg_response_time
            }
            return True

        except Exception as e:
            if "rate_limit" in str(e).lower():
                print(f"  ⚠️  Rate limit encountered: {e}")
                self.test_results['rate_limits'] = {'rate_limited': True}
                return True  # This is expected behavior
            else:
                print(f"  ❌ Rate limit test error: {e}")
                self.test_results['rate_limits'] = False
                return False

    def test_organization_access(self) -> bool:
        """Test organization-specific access."""
        print("\n🏢 Testing Organization Access...")

        if not self.org_id:
            print("  ⚠️  No organization ID configured")
            self.test_results['organization_access'] = 'not_configured'
            return True

        try:
            # This would require additional API endpoints
            print(f"  ℹ️  Organization ID: {self.org_id}")
            print("  ✅ Organization ID configured")

            # Basic test with org header
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'OpenAI-Organization': self.org_id,
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                print("  ✅ Organization access: Success")
                self.test_results['organization_access'] = True
                return True
            else:
                print(f"  ❌ Organization access error: {response.status_code}")
                self.test_results['organization_access'] = False
                return False

        except Exception as e:
            print(f"  ❌ Organization access test error: {e}")
            self.test_results['organization_access'] = False
            return False

    def generate_report(self):
        """Generate final test report."""
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)

        total_tests = 0
        passed_tests = 0

        test_status = {
            'environment_variables': 'Environment Variables',
            'api_connectivity': 'API Connectivity',
            'model_access': 'Model Access',
            'chat_completion': 'Chat Completion',
            'embedding_generation': 'Embedding Generation',
            'rate_limits': 'Rate Limits',
            'organization_access': 'Organization Access'
        }

        for test_key, test_name in test_status.items():
            total_tests += 1
            result = self.test_results.get(test_key, False)

            if result is True or (isinstance(result, dict) and result.get('success')):
                print(f"✅ {test_name}: PASS")
                passed_tests += 1
            elif result == 'not_configured':
                print(f"⚠️  {test_name}: NOT CONFIGURED")
                passed_tests += 0.5  # Partial credit
            else:
                print(f"❌ {test_name}: FAIL")

        print("-" * 70)
        print(f"📈 Overall Score: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")

        if passed_tests == total_tests:
            print("🎉 All tests passed! OpenAI Enterprise is ready.")
        elif passed_tests >= total_tests * 0.8:
            print("✅ Most tests passed. Review failed tests above.")
        else:
            print("⚠️  Several tests failed. Check configuration and credentials.")

        # Save detailed results
        report_file = f"openai_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'detailed_results': self.test_results
            }, f, indent=2)

        print(f"📄 Detailed report saved to: {report_file}")

    def run_all_tests(self):
        """Run all configuration tests."""
        self.print_header()

        # Run tests in order
        tests = [
            self.test_environment_variables,
            self.test_api_connectivity,
            self.test_model_access,
            self.test_chat_completion,
            self.test_embedding_generation,
            self.test_rate_limits,
            self.test_organization_access
        ]

        for test in tests:
            try:
                test()
            except KeyboardInterrupt:
                print("\n⏹️  Tests interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error in test: {e}")

        self.generate_report()


def main():
    """Main function to run OpenAI configuration tests."""
    print("🚀 Starting OpenAI Enterprise Configuration Tests...\n")

    # Check if .env file exists and load it
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"📁 Loading environment from {env_file}")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Environment variables loaded successfully")
        except ImportError:
            print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
        except Exception as e:
            print(f"⚠️  Error loading .env file: {e}")
    else:
        print("⚠️  No .env file found. Using system environment variables.")
        print("💡 Tip: Create a .env file with your OpenAI credentials for easier testing.")

    tester = OpenAIConfigTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
