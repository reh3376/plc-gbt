#!/usr/bin/env python3
"""
model_config_validator.py - Validate OpenAI model configuration
===============================================================

Ensures consistent model configuration across the PLC-GPT project.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class ModelConfigValidator:
    """Validate and manage OpenAI model configuration"""

    def __init__(self):
        self.env_path = Path(__file__).parent.parent.parent / '.env'
        self.required_vars = [
            'OPENAI_API_KEY',
            'OPENAI_FINETUNE_BASE_MODEL',
            'OPENAI_FINETUNE_MODEL',
            'OPENAI_MODEL',
            'OPENAI_EMBEDDING_MODEL'
        ]
        self.model_history_file = Path(__file__).parent / 'model_history.json'

    def load_env_vars(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}

        if self.env_path.exists():
            with open(self.env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value.strip()

        # Also check OS environment
        for var in self.required_vars:
            if var in os.environ:
                env_vars[var] = os.environ[var]

        return env_vars

    def validate_configuration(self) -> Dict[str, any]:
        """Validate current model configuration"""
        env_vars = self.load_env_vars()

        config = {
            'base_model': env_vars.get('OPENAI_FINETUNE_BASE_MODEL', 'gpt-4o'),
            'fine_tuned_model': env_vars.get('OPENAI_FINETUNE_MODEL'),
            'primary_model': env_vars.get('OPENAI_MODEL', 'gpt-4o'),
            'embedding_model': env_vars.get('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small'),
            'api_key_configured': bool(env_vars.get('OPENAI_API_KEY'))
        }

        # Validate configuration
        issues = []
        warnings = []

        # Check API key
        if not config['api_key_configured']:
            issues.append("OPENAI_API_KEY not configured")

        # Check fine-tuned model
        if not config['fine_tuned_model']:
            warnings.append("OPENAI_FINETUNE_MODEL not set - using base model")
        elif 'gpt-3.5-turbo' in config['fine_tuned_model']:
            warnings.append(f"Fine-tuned model uses GPT-3.5-turbo: {config['fine_tuned_model']}")
            warnings.append("Consider migrating to GPT-4o for better performance")

        # Check base model consistency
        if config['base_model'] != 'gpt-4o':
            issues.append(f"Base model is '{config['base_model']}', should be 'gpt-4o' for production")

        # Check primary model
        if config['primary_model'] != 'gpt-4o':
            warnings.append(f"Primary model is '{config['primary_model']}', consider using 'gpt-4o'")

        # Add validation results
        config['issues'] = issues
        config['warnings'] = warnings
        config['valid'] = len(issues) == 0

        return config

    def get_model_history(self) -> List[Dict]:
        """Load model training history"""
        if self.model_history_file.exists():
            with open(self.model_history_file) as f:
                return json.load(f)
        return []

    def add_model_to_history(self, model_id: str, base_model: str,
                           training_examples: int, validation_score: Optional[float] = None):
        """Add a model to the training history"""
        history = self.get_model_history()

        entry = {
            'model_id': model_id,
            'base_model': base_model,
            'date': datetime.now().isoformat(),
            'training_examples': training_examples,
            'validation_score': validation_score,
            'version': f"v{len(history) + 1}.0"
        }

        history.append(entry)

        with open(self.model_history_file, 'w') as f:
            json.dump(history, f, indent=2)

        return entry

    def print_report(self):
        """Print a formatted configuration report"""
        config = self.validate_configuration()

        print("\n" + "="*60)
        print("🤖 OpenAI Model Configuration Report")
        print("="*60)

        print("\n📋 Current Configuration:")
        print(f"   Base Model: {config['base_model']}")
        print(f"   Fine-tuned Model: {config['fine_tuned_model'] or 'Not configured'}")
        print(f"   Primary Model: {config['primary_model']}")
        print(f"   Embedding Model: {config['embedding_model']}")
        print(f"   API Key: {'✅ Configured' if config['api_key_configured'] else '❌ Not configured'}")

        if config['issues']:
            print("\n❌ Issues (Must Fix):")
            for issue in config['issues']:
                print(f"   - {issue}")

        if config['warnings']:
            print("\n⚠️  Warnings:")
            for warning in config['warnings']:
                print(f"   - {warning}")

        # Show model history
        history = self.get_model_history()
        if history:
            print("\n📊 Model Training History:")
            print("   Version | Model ID | Base | Examples | Score | Date")
            print("   " + "-"*55)
            for entry in history[-5:]:  # Show last 5 entries
                print(f"   {entry['version']:7} | {entry['model_id'][:20]:20} | "
                      f"{entry['base_model']:4} | {entry['training_examples']:8} | "
                      f"{entry['validation_score'] or 'N/A':5} | {entry['date'][:10]}")

        if config['valid'] and not config['warnings']:
            print("\n✅ Configuration is valid and optimized!")
        elif config['valid']:
            print("\n✅ Configuration is valid but has warnings")
        else:
            print("\n❌ Configuration has issues that need to be fixed")

        print("\n" + "="*60)

    def suggest_env_updates(self) -> List[str]:
        """Suggest .env file updates"""
        config = self.validate_configuration()
        suggestions = []

        if not config['fine_tuned_model']:
            suggestions.append("OPENAI_FINETUNE_MODEL=ft:gpt-4o-mini-2024-07-18:whiskey-house:industrial-control:But1jpnl")

        if config['base_model'] != 'gpt-4o':
            suggestions.append("OPENAI_FINETUNE_BASE_MODEL=gpt-4o")

        if config['primary_model'] != 'gpt-4o':
            suggestions.append("OPENAI_MODEL=gpt-4o")

        if suggestions:
            print("\n📝 Suggested .env updates:")
            for suggestion in suggestions:
                print(f"   {suggestion}")

        return suggestions


def main():
    """Main execution"""
    validator = ModelConfigValidator()

    # Print configuration report
    validator.print_report()

    # Suggest updates
    validator.suggest_env_updates()

    # Check if we need to update model history
    config = validator.validate_configuration()
    if config['fine_tuned_model'] and 'gpt-3.5-turbo' in config['fine_tuned_model']:
        print("\n🔄 GPT-3.5-turbo model detected")
        print("   To migrate to GPT-4o, run:")
        print("   python migrate_to_gpt4o.py")


if __name__ == "__main__":
    main()
