#!/usr/bin/env python3
"""
OpenAI Configuration Setup
=========================

Secure script to configure OpenAI API credentials for Phase 10 implementation.
"""

import getpass
import os
import re
from pathlib import Path


def update_env_file():
    """Update .env file with OpenAI API credentials"""

    print("🔐 OpenAI Configuration Setup")
    print("=" * 40)

    # Get current directory (should be plc-gbt-stack)
    env_path = Path('.env')

    if not env_path.exists():
        print("❌ .env file not found!")
        return False

    # Read current .env content
    with open(env_path) as f:
        content = f.read()

    # Check if OpenAI key is already set (not a placeholder)
    if 'OPENAI_API_KEY=' in content:
        current_key = re.search(r'OPENAI_API_KEY=(.+)', content)
        if current_key and not current_key.group(1).startswith('your-openai-api-key'):
            print("✅ OpenAI API key appears to be already configured")
            return True

    print("\n🔑 Please provide your OpenAI API key")
    print("   (This will be stored securely in your .env file)")
    print("   Format: sk-...")

    # Get API key securely
    api_key = getpass.getpass("OpenAI API Key: ").strip()

    if not api_key or not api_key.startswith('sk-'):
        print("❌ Invalid API key format. Should start with 'sk-'")
        return False

    # Get organization ID (optional)
    print("\n🏢 OpenAI Organization ID (optional, press Enter to skip)")
    org_id = input("Organization ID: ").strip()

    # Update .env file
    try:
        # Replace or add OpenAI configuration
        new_content = content

        # Update API key
        if 'OPENAI_API_KEY=' in content:
            new_content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={api_key}', new_content)
        else:
            new_content += f'\nOPENAI_API_KEY={api_key}'

        # Update organization ID
        if org_id:
            if 'OPENAI_ORG_ID=' in content:
                new_content = re.sub(r'OPENAI_ORG_ID=.*', f'OPENAI_ORG_ID={org_id}', new_content)
            else:
                new_content += f'\nOPENAI_ORG_ID={org_id}'

        # Write updated content
        with open(env_path, 'w') as f:
            f.write(new_content)

        print("✅ OpenAI configuration updated successfully!")
        return True

    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def test_openai_connection():
    """Test OpenAI connection"""
    try:
        from openai import OpenAI

        # Load environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        org_id = os.getenv('OPENAI_ORG_ID')

        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False

        # Test connection
        client = OpenAI(
            api_key=api_key,
            organization=org_id if org_id else None
        )

        # Test with a simple request
        response = client.models.list()
        print("✅ OpenAI connection successful!")
        print(f"   Available models: {len(response.data)}")
        return True

    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def main():
    """Main configuration flow"""
    print("🚀 Phase 10: OpenAI Configuration Setup")
    print("=" * 50)

    # Step 1: Update .env file
    if update_env_file():
        print("\n🔄 Loading environment variables...")

        # Load updated environment variables
        with open('.env') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

        # Step 2: Test connection
        print("\n🧪 Testing OpenAI connection...")
        if test_openai_connection():
            print("\n✅ Configuration complete! Ready for Phase 10 training data generation.")
            return True
        else:
            print("\n❌ Connection test failed. Please check your API key.")
            return False
    else:
        print("\n❌ Configuration failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
