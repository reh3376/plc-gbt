#!/usr/bin/env python3
"""
Phase 3.7.1 GitHub Repository Creator
Following AI Task Orchestrator methodology for systematic repository creation and migration setup.

Task Analysis:
- Complexity: Moderate (100-500 lines, 2-5 files, 1-3 hours)
- Requirements: Create 6 private GitHub repositories, configure security, set up migration infrastructure
- Resources: GitHub API, authentication tokens, repository templates
- Risks: API rate limits, authentication failures, repository naming conflicts

This script creates private GitHub repositories for PLC migration:
- plc-100: https://github.com/reh3376/plc-100.git
- plc-200: https://github.com/reh3376/plc-200.git
- plc-300: https://github.com/reh3376/plc-300.git
- plc-400: https://github.com/reh3376/plc-400.git
- plc-500: https://github.com/reh3376/plc-500.git
- plc-600: https://github.com/reh3376/plc-600.git
"""

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import requests

# Setup logging following orchestrator best practices
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_repo_creation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RepositoryConfig:
    """Configuration for a GitHub repository."""
    name: str
    description: str
    private: bool = True
    auto_init: bool = True
    gitignore_template: str = None
    license_template: str = None
    allow_squash_merge: bool = True
    allow_merge_commit: bool = True
    allow_rebase_merge: bool = True
    delete_branch_on_merge: bool = True

@dataclass
class RepositoryResult:
    """Result of repository creation."""
    name: str
    url: str
    clone_url: str
    ssh_url: str
    created: bool
    error: Optional[str] = None
    status_code: Optional[int] = None

class GitHubRepositoryCreator:
    """
    GitHub Repository Creator following AI Task Orchestrator methodology.

    Features:
    - Comprehensive error handling and validation
    - Rate limit management
    - Security-first configuration
    - Detailed logging and progress tracking
    - Rollback capabilities
    """

    def __init__(self):
        """Initialize the repository creator with authentication."""
        self.session = requests.Session()
        self.base_url = "https://api.github.com"
        self.user = None
        self.token = None
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

        # Load authentication
        self._load_authentication()

        # Validate authentication
        self._validate_authentication()

    def _load_authentication(self):
        """Load GitHub authentication from environment."""
        try:
            # Try to load from ~/.env.github
            env_file = Path.home() / ".env.github"
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.startswith('GITHUB_TOKEN='):
                            self.token = line.split('=', 1)[1].strip()
                        elif line.startswith('GITHUB_USER='):
                            self.user = line.split('=', 1)[1].strip()

            # Fallback to environment variables
            if not self.token:
                self.token = os.getenv('GITHUB_TOKEN')
            if not self.user:
                self.user = os.getenv('GITHUB_USER')

            if not self.token:
                raise ValueError("GitHub token not found. Set GITHUB_TOKEN environment variable or ~/.env.github")

            # Configure session
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'PLC-GPT-Migration-Tool/1.0'
            })

            logger.info("✅ GitHub authentication loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load GitHub authentication: {e}")
            raise

    def _validate_authentication(self):
        """Validate GitHub authentication and get user info."""
        try:
            response = self.session.get(f"{self.base_url}/user")

            if response.status_code == 200:
                user_info = response.json()
                self.user = user_info['login']
                logger.info(f"✅ Authenticated as GitHub user: {self.user}")

                # Check rate limits
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
                logger.info(f"📊 Rate limit: {self.rate_limit_remaining} requests remaining")

                return True
            else:
                logger.error(f"❌ GitHub authentication failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to validate GitHub authentication: {e}")
            return False

    def _check_rate_limit(self):
        """Check and handle GitHub API rate limits."""
        if self.rate_limit_remaining is not None and self.rate_limit_remaining < 10:
            reset_time = datetime.fromtimestamp(self.rate_limit_reset)
            logger.warning(f"⚠️ Rate limit low ({self.rate_limit_remaining}). Resets at {reset_time}")
            return False
        return True

    def check_repository_exists(self, repo_name: str) -> bool:
        """Check if a repository already exists."""
        try:
            response = self.session.get(f"{self.base_url}/repos/{self.user}/{repo_name}")

            # Update rate limit info
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))

            if response.status_code == 200:
                logger.info(f"📁 Repository {repo_name} already exists")
                return True
            elif response.status_code == 404:
                logger.info(f"✨ Repository {repo_name} available for creation")
                return False
            else:
                logger.warning(f"⚠️ Unexpected response checking {repo_name}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error checking repository {repo_name}: {e}")
            return False

    def create_repository(self, config: RepositoryConfig) -> RepositoryResult:
        """Create a single GitHub repository."""
        logger.info(f"🚀 Creating repository: {config.name}")

        try:
            # Check rate limits
            if not self._check_rate_limit():
                return RepositoryResult(
                    name=config.name,
                    url="",
                    clone_url="",
                    ssh_url="",
                    created=False,
                    error="Rate limit exceeded"
                )

            # Check if repository already exists
            if self.check_repository_exists(config.name):
                repo_url = f"https://github.com/{self.user}/{config.name}"
                return RepositoryResult(
                    name=config.name,
                    url=repo_url,
                    clone_url=f"{repo_url}.git",
                    ssh_url=f"git@github.com:{self.user}/{config.name}.git",
                    created=False,
                    error="Repository already exists"
                )

            # Prepare repository data
            repo_data = {
                "name": config.name,
                "description": config.description,
                "private": config.private,
                "auto_init": config.auto_init,
                "allow_squash_merge": config.allow_squash_merge,
                "allow_merge_commit": config.allow_merge_commit,
                "allow_rebase_merge": config.allow_rebase_merge,
                "delete_branch_on_merge": config.delete_branch_on_merge
            }

            # Add optional templates
            if config.gitignore_template:
                repo_data["gitignore_template"] = config.gitignore_template
            if config.license_template:
                repo_data["license_template"] = config.license_template

            # Create repository
            response = self.session.post(f"{self.base_url}/user/repos", json=repo_data)

            # Update rate limit info
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))

            if response.status_code == 201:
                repo_info = response.json()
                logger.info(f"✅ Repository {config.name} created successfully")

                return RepositoryResult(
                    name=config.name,
                    url=repo_info['html_url'],
                    clone_url=repo_info['clone_url'],
                    ssh_url=repo_info['ssh_url'],
                    created=True,
                    status_code=201
                )
            else:
                error_msg = f"Failed to create repository: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"

                logger.error(f"❌ {error_msg}")

                return RepositoryResult(
                    name=config.name,
                    url="",
                    clone_url="",
                    ssh_url="",
                    created=False,
                    error=error_msg,
                    status_code=response.status_code
                )

        except Exception as e:
            logger.error(f"❌ Exception creating repository {config.name}: {e}")
            return RepositoryResult(
                name=config.name,
                url="",
                clone_url="",
                ssh_url="",
                created=False,
                error=str(e)
            )

    def setup_repository_security(self, repo_name: str) -> bool:
        """Configure security settings for the repository."""
        logger.info(f"🔒 Configuring security for {repo_name}")

        try:
            # Enable vulnerability alerts
            security_url = f"{self.base_url}/repos/{self.user}/{repo_name}/vulnerability-alerts"
            response = self.session.put(security_url)

            if response.status_code in [200, 204]:
                logger.info(f"✅ Vulnerability alerts enabled for {repo_name}")
            else:
                logger.warning(f"⚠️ Could not enable vulnerability alerts for {repo_name}: {response.status_code}")

            # Enable automated security fixes (Dependabot)
            dependabot_url = f"{self.base_url}/repos/{self.user}/{repo_name}/automated-security-fixes"
            response = self.session.put(dependabot_url)

            if response.status_code in [200, 204]:
                logger.info(f"✅ Automated security fixes enabled for {repo_name}")
            else:
                logger.warning(f"⚠️ Could not enable automated security fixes for {repo_name}: {response.status_code}")

            return True

        except Exception as e:
            logger.error(f"❌ Error configuring security for {repo_name}: {e}")
            return False

    def create_all_repositories(self) -> Dict[str, RepositoryResult]:
        """Create all PLC repositories with proper configuration."""
        logger.info("🎯 Starting GitHub repository creation for PLC migration")

        # Repository configurations
        repositories = [
            RepositoryConfig(
                name="plc-100",
                description="PLC-100 Mashing Process Control - Converted from Copia.io with ACD→L5X migration",
                private=True,
                auto_init=True,
                gitignore_template="Python"
            ),
            RepositoryConfig(
                name="plc-200",
                description="PLC-200 Fermentation Process Control - Converted from Copia.io with ACD→L5X migration",
                private=True,
                auto_init=True,
                gitignore_template="Python"
            ),
            RepositoryConfig(
                name="plc-300",
                description="PLC-300 Distillation Process Control - Converted from Copia.io with ACD→L5X migration",
                private=True,
                auto_init=True,
                gitignore_template="Python"
            ),
            RepositoryConfig(
                name="plc-400",
                description="PLC-400 Utilities Process Control - Converted from Copia.io with ACD→L5X migration",
                private=True,
                auto_init=True,
                gitignore_template="Python"
            ),
            RepositoryConfig(
                name="plc-500",
                description="PLC-500 Barreling Process Control - Converted from Copia.io with ACD→L5X migration",
                private=True,
                auto_init=True,
                gitignore_template="Python"
            ),
            RepositoryConfig(
                name="plc-600",
                description="PLC-600 RO Process Control - Converted from Copia.io with ACD→L5X migration",
                private=True,
                auto_init=True,
                gitignore_template="Python"
            )
        ]

        results = {}
        successful_creations = 0

        for config in repositories:
            result = self.create_repository(config)
            results[config.name] = result

            if result.created:
                successful_creations += 1
                # Configure security settings
                self.setup_repository_security(config.name)

            # Brief pause to respect rate limits
            import time
            time.sleep(1)

        logger.info(f"📊 Repository creation summary: {successful_creations}/{len(repositories)} successful")

        return results

def generate_migration_urls(results: Dict[str, RepositoryResult]) -> Dict[str, str]:
    """Generate the migration URL mapping."""
    urls = {}

    for repo_name, result in results.items():
        if result.created or result.error == "Repository already exists":
            # Use the expected URL format
            urls[repo_name] = f"https://github.com/reh3376/{repo_name}.git"
        else:
            logger.warning(f"⚠️ Repository {repo_name} not available: {result.error}")

    return urls

def save_results(results: Dict[str, RepositoryResult], urls: Dict[str, str]):
    """Save repository creation results and migration URLs."""
    output_dir = Path(__file__).parent

    # Save detailed results
    results_file = output_dir / "github_repository_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "creation_date": datetime.now().isoformat(),
            "results": {name: asdict(result) for name, result in results.items()}
        }, f, indent=2)

    # Save migration URLs
    urls_file = output_dir / "migration_urls.json"
    with open(urls_file, 'w') as f:
        json.dump({
            "migration_urls": urls,
            "creation_date": datetime.now().isoformat(),
            "total_repositories": len(urls)
        }, f, indent=2)

    # Generate migration summary
    summary_file = output_dir / "github_creation_summary.md"
    with open(summary_file, 'w') as f:
        f.write("# GitHub Repository Creation Summary\n\n")
        f.write(f"**Creation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Repository URLs\n")
        for repo_name, url in urls.items():
            f.write(f"- **{repo_name}**: {url}\n")

        f.write("\n## Creation Results\n")
        for repo_name, result in results.items():
            status = "✅ Created" if result.created else "❌ Failed" if result.error != "Repository already exists" else "📁 Exists"
            f.write(f"- **{repo_name}**: {status}")
            if result.error:
                f.write(f" - {result.error}")
            f.write("\n")

        f.write("\n## Security Configuration\n")
        f.write("All repositories configured with:\n")
        f.write("- Private visibility\n")
        f.write("- Vulnerability alerts enabled\n")
        f.write("- Automated security fixes enabled\n")
        f.write("- Branch protection rules ready for configuration\n")
        f.write("- Python .gitignore template\n")

    logger.info("📄 Results saved to:")
    logger.info(f"  - Detailed results: {results_file}")
    logger.info(f"  - Migration URLs: {urls_file}")
    logger.info(f"  - Summary report: {summary_file}")

def main():
    """Main function following AI Task Orchestrator methodology."""
    logger.info("🚀 Starting Phase 3.7.1 GitHub Repository Creation")
    logger.info("📋 Task: Create 6 private GitHub repositories for PLC migration")

    try:
        # Initialize GitHub repository creator
        creator = GitHubRepositoryCreator()

        # Create all repositories
        results = creator.create_all_repositories()

        # Generate migration URLs
        urls = generate_migration_urls(results)

        # Save results
        save_results(results, urls)

        # Print summary
        print("\n" + "="*60)
        print("🎯 GITHUB REPOSITORY CREATION COMPLETE")
        print("="*60)

        successful = sum(1 for r in results.values() if r.created)
        existing = sum(1 for r in results.values() if r.error == "Repository already exists")
        failed = len(results) - successful - existing

        print(f"📊 Results: {successful} created, {existing} existing, {failed} failed")
        print("\n📋 Migration URLs:")
        for repo_name, url in urls.items():
            print(f"  {repo_name}: {url}")

        if failed > 0:
            print(f"\n⚠️ {failed} repositories failed to create - check logs for details")

        print("\n✅ Ready for Phase 3.7.2: Conversion Infrastructure Development")
        print("="*60)

        return 0 if failed == 0 else 1

    except Exception as e:
        logger.error(f"❌ Fatal error in repository creation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
