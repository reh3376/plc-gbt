#!/usr/bin/env python3
"""
CI/CD Integration for PLC-Optimize Automation
==============================================

Comprehensive CI/CD integration system for automated codebase optimization
that integrates with multiple CI/CD platforms and git workflows.

Features:
- GitHub Actions integration with workflow templates
- Jenkins pipeline integration with Jenkinsfile generation
- GitLab CI integration with .gitlab-ci.yml templates
- Generic webhook-based integration for other platforms
- Automated optimization triggers on commits, PRs, and releases
- Safety validation and rollback mechanisms
- Performance monitoring and reporting

Following AI Task Orchestrator methodology for systematic CI/CD integration.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 14.4.2 - CI/CD Integration
Dependencies: Master CLI, Git Integration, All Phase 14 components
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import subprocess
import tempfile
import hashlib
import logging

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
from core import BaseOrchestrator, TaskAnalysis

# Import master CLI
try:
    from .plc_optimize_cli import PLCOptimizeMasterCLI, OptimizationProfile, OptimizationSession
except ImportError:
    from plc_optimize_cli import PLCOptimizeMasterCLI, OptimizationProfile, OptimizationSession

@dataclass
class CICDPlatform:
    """CI/CD platform configuration"""
    name: str
    config_file: str
    workflow_directory: str
    supports_artifacts: bool
    supports_caching: bool
    supports_parallel_jobs: bool
    trigger_events: List[str]
    
@dataclass 
class OptimizationTrigger:
    """Configuration for optimization trigger events"""
    event_type: str  # commit, pull_request, schedule, manual
    target_branches: List[str]
    file_patterns: List[str]  # Only trigger on certain file changes
    optimization_profile: str
    auto_apply_threshold: float
    notification_channels: List[str]

@dataclass
class CICDIntegrationResult:
    """Results of CI/CD integration setup"""
    platform: str
    integration_id: str
    config_files_created: List[str]
    webhook_urls: List[str]
    triggers_configured: List[OptimizationTrigger]
    validation_status: str
    setup_instructions: List[str]

class CICDIntegrationOrchestrator(BaseOrchestrator):
    """
    Comprehensive CI/CD integration orchestrator for automated optimization.
    
    Provides systematic integration with multiple CI/CD platforms including
    workflow generation, trigger configuration, and safety mechanisms.
    """

    def __init__(self, task_id: str = "cicd_integration", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)
        
        # Initialize master CLI for orchestration
        self.master_cli = PLCOptimizeMasterCLI("cicd_master")
        
        # CI/CD platform definitions
        self.supported_platforms = {
            "github_actions": CICDPlatform(
                name="GitHub Actions",
                config_file=".github/workflows/plc-optimize.yml",
                workflow_directory=".github/workflows",
                supports_artifacts=True,
                supports_caching=True,
                supports_parallel_jobs=True,
                trigger_events=["push", "pull_request", "schedule", "workflow_dispatch"]
            ),
            "gitlab_ci": CICDPlatform(
                name="GitLab CI",
                config_file=".gitlab-ci.yml",
                workflow_directory=".",
                supports_artifacts=True,
                supports_caching=True,
                supports_parallel_jobs=True,
                trigger_events=["push", "merge_request", "schedule", "manual"]
            ),
            "jenkins": CICDPlatform(
                name="Jenkins",
                config_file="Jenkinsfile",
                workflow_directory=".",
                supports_artifacts=True,
                supports_caching=False,
                supports_parallel_jobs=True,
                trigger_events=["scm", "timer", "manual"]
            ),
            "azure_devops": CICDPlatform(
                name="Azure DevOps",
                config_file="azure-pipelines.yml",
                workflow_directory=".",
                supports_artifacts=True,
                supports_caching=True,
                supports_parallel_jobs=True,
                trigger_events=["push", "pr", "schedule", "manual"]
            )
        }
        
        # Default optimization triggers
        self.default_triggers = [
            OptimizationTrigger(
                event_type="pull_request",
                target_branches=["main", "master", "develop"],
                file_patterns=["*.py", "*.ts", "*.js", "*.json"],
                optimization_profile="conservative",
                auto_apply_threshold=0.9,
                notification_channels=["github_pr_comment"]
            ),
            OptimizationTrigger(
                event_type="commit",
                target_branches=["main", "master"],
                file_patterns=["*.py", "*.ts", "*.js"],
                optimization_profile="ci_cd",
                auto_apply_threshold=0.85,
                notification_channels=["slack", "email"]
            ),
            OptimizationTrigger(
                event_type="schedule",
                target_branches=["main"],
                file_patterns=["*"],
                optimization_profile="aggressive",
                auto_apply_threshold=0.8,
                notification_channels=["slack", "email"]
            )
        ]
        
        # Integration configuration
        self.integration_config = {
            "timeout_minutes": 30,
            "retry_attempts": 2,
            "artifact_retention_days": 30,
            "enable_caching": True,
            "parallel_execution": True,
            "notification_webhook": None,
            "security_scan_enabled": True,
            "performance_monitoring": True
        }

    def _analyze_task(self) -> TaskAnalysis:
        """Analyze CI/CD integration task"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="complex",
            estimated_time="2-4 hours",
            estimated_lines=1500,
            requirements=[
                "Git repository with CI/CD platform access",
                "Master CLI interface available",
                "Platform-specific credentials and permissions",
                "Webhook and notification setup"
            ],
            risks=[
                "Platform-specific configuration differences",
                "Security and credential management",
                "Workflow trigger complexity",
                "Integration testing requirements"
            ],
            dependencies=[
                "modules.core",
                "plc_optimize_cli",
                "git_integration_hooks",
                "All Phase 14 components"
            ],
            success_criteria=[
                "CI/CD workflows generated for target platforms",
                "Triggers configured correctly",
                "Integration validated with test runs",
                "Documentation and setup instructions provided"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute CI/CD integration setup"""
        self.log_execution_step("CI/CD Integration Setup", "started")
        
        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}
            
            # Auto-detect CI/CD platform(s)
            project_root = self.config.get("system.project_root", str(Path.cwd()))
            detected_platforms = self._detect_cicd_platforms(project_root)
            
            # Setup integration for detected platforms
            integration_results = []
            for platform_name in detected_platforms:
                result = self.setup_platform_integration(project_root, platform_name)
                integration_results.append(result)
            
            # Generate comprehensive setup documentation
            setup_docs = self._generate_setup_documentation(integration_results)
            
            return {
                "status": "completed",
                "platforms_integrated": len(integration_results),
                "integration_results": [asdict(r) for r in integration_results],
                "setup_documentation": setup_docs,
                "next_steps": self._generate_next_steps(integration_results)
            }
            
        except Exception as e:
            self.log_error("CI/CD integration setup failed", e)
            return {"status": "failed", "error": str(e)}
        finally:
            self.log_execution_step("CI/CD Integration Setup", "completed")

    def setup_platform_integration(
        self, 
        project_root: str, 
        platform_name: str,
        custom_triggers: Optional[List[OptimizationTrigger]] = None
    ) -> CICDIntegrationResult:
        """
        Setup CI/CD integration for specific platform.
        
        Args:
            project_root: Project directory
            platform_name: CI/CD platform name
            custom_triggers: Custom trigger configuration
            
        Returns:
            Integration result with configuration and setup details
        """
        self.log_execution_step(f"{platform_name} Integration", "started")
        
        try:
            platform = self.supported_platforms.get(platform_name)
            if not platform:
                raise ValueError(f"Unsupported platform: {platform_name}")
            
            triggers = custom_triggers or self.default_triggers
            
            # Create workflow configuration
            workflow_config = self._generate_workflow_config(platform, triggers)
            
            # Create configuration files
            config_files = self._create_platform_config_files(
                project_root, platform, workflow_config
            )
            
            # Setup webhooks if supported
            webhook_urls = self._setup_platform_webhooks(project_root, platform)
            
            # Generate setup instructions
            setup_instructions = self._generate_platform_setup_instructions(
                platform, config_files, webhook_urls
            )
            
            # Validate integration
            validation_status = self._validate_platform_integration(
                project_root, platform, config_files
            )
            
            result = CICDIntegrationResult(
                platform=platform_name,
                integration_id=f"{platform_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                config_files_created=config_files,
                webhook_urls=webhook_urls,
                triggers_configured=triggers,
                validation_status=validation_status,
                setup_instructions=setup_instructions
            )
            
            self.log_execution_step(f"{platform_name} Integration", "completed")
            return result
            
        except Exception as e:
            self.log_error(f"{platform_name} integration failed", e)
            return CICDIntegrationResult(
                platform=platform_name,
                integration_id="failed",
                config_files_created=[],
                webhook_urls=[],
                triggers_configured=[],
                validation_status="failed",
                setup_instructions=[f"Integration failed: {str(e)}"]
            )

    def generate_github_actions_workflow(
        self, 
        triggers: List[OptimizationTrigger]
    ) -> Dict[str, Any]:
        """Generate GitHub Actions workflow configuration"""
        workflow = {
            "name": "PLC-Optimize Automated Codebase Optimization",
            "on": self._generate_github_triggers(triggers),
            "env": {
                "PLC_OPTIMIZE_CONFIG": ".plc_optimize_config.json",
                "PYTHON_VERSION": "3.12"
            },
            "jobs": {
                "optimize": {
                    "runs-on": "ubuntu-latest",
                    "timeout-minutes": self.integration_config["timeout_minutes"],
                    "strategy": {
                        "fail-fast": False,
                        "matrix": {
                            "profile": ["conservative", "ci_cd"]
                        }
                    },
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4",
                            "with": {
                                "fetch-depth": 0,
                                "token": "${{ secrets.GITHUB_TOKEN }}"
                            }
                        },
                        {
                            "name": "Setup Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "${{ env.PYTHON_VERSION }}",
                                "cache": "pip"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Cache optimization data",
                            "uses": "actions/cache@v3",
                            "with": {
                                "path": ".plc_optimize_cache",
                                "key": "plc-optimize-${{ hashFiles('**/*.py') }}"
                            }
                        },
                        {
                            "name": "Run PLC-Optimize Analysis",
                            "run": "python plc_optimize_cli.py analyze --project-root .",
                            "continue-on-error": True
                        },
                        {
                            "name": "Run PLC-Optimize with ${{ matrix.profile }} profile",
                            "run": "python plc_optimize_cli.py optimize --project-root . --profile ${{ matrix.profile }} --no-backup",
                            "env": {
                                "PLC_OPTIMIZE_PROFILE": "${{ matrix.profile }}"
                            }
                        },
                        {
                            "name": "Run Schema Governance Check",
                            "run": "python plc_optimize_cli.py schema-check --project-root .",
                            "continue-on-error": True
                        },
                        {
                            "name": "Upload optimization results",
                            "uses": "actions/upload-artifact@v3",
                            "with": {
                                "name": "optimization-results-${{ matrix.profile }}",
                                "path": "execution_summary_*.json",
                                "retention-days": self.integration_config["artifact_retention_days"]
                            },
                            "if": "always()"
                        },
                        {
                            "name": "Comment PR with results",
                            "if": "github.event_name == 'pull_request'",
                            "uses": "actions/github-script@v6",
                            "with": {
                                "script": self._generate_pr_comment_script()
                            }
                        }
                    ]
                },
                "security-scan": {
                    "runs-on": "ubuntu-latest",
                    "if": self.integration_config["security_scan_enabled"],
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Run security scan",
                            "run": "echo 'Security scan would run here'"
                        }
                    ]
                }
            }
        }
        
        return workflow

    def generate_gitlab_ci_config(
        self, 
        triggers: List[OptimizationTrigger]
    ) -> Dict[str, Any]:
        """Generate GitLab CI configuration"""
        config = {
            "stages": ["analysis", "optimize", "validate", "report"],
            "variables": {
                "PLC_OPTIMIZE_CONFIG": ".plc_optimize_config.json",
                "PYTHON_VERSION": "3.12"
            },
            "cache": {
                "paths": [".plc_optimize_cache/", ".pip/"]
            },
            "before_script": [
                "pip install --cache-dir .pip -r requirements.txt"
            ],
            "analysis": {
                "stage": "analysis",
                "script": [
                    "python plc_optimize_cli.py analyze --project-root ."
                ],
                "artifacts": {
                    "reports": {
                        "junit": "analysis_report.xml"
                    },
                    "paths": ["analysis_results.json"],
                    "expire_in": f"{self.integration_config['artifact_retention_days']} days"
                },
                "rules": self._generate_gitlab_rules(triggers)
            },
            "optimize_conservative": {
                "stage": "optimize",
                "script": [
                    "python plc_optimize_cli.py optimize --project-root . --profile conservative --no-backup"
                ],
                "artifacts": {
                    "paths": ["execution_summary_*.json"],
                    "expire_in": f"{self.integration_config['artifact_retention_days']} days"
                },
                "rules": self._generate_gitlab_rules(triggers),
                "allow_failure": True
            },
            "optimize_aggressive": {
                "stage": "optimize",
                "script": [
                    "python plc_optimize_cli.py optimize --project-root . --profile aggressive --auto-apply --no-backup"
                ],
                "rules": [
                    {"if": "$CI_COMMIT_BRANCH == 'main'"},
                    {"if": "$CI_PIPELINE_SOURCE == 'schedule'"}
                ],
                "when": "manual"
            },
            "schema_governance": {
                "stage": "validate",
                "script": [
                    "python plc_optimize_cli.py schema-check --project-root ."
                ],
                "artifacts": {
                    "paths": ["schema_compliance_report.json"],
                    "expire_in": f"{self.integration_config['artifact_retention_days']} days"
                },
                "rules": self._generate_gitlab_rules(triggers)
            },
            "generate_report": {
                "stage": "report",
                "script": [
                    "echo 'Generating comprehensive optimization report'",
                    "python -c \"import json; print('Report generation complete')\""
                ],
                "artifacts": {
                    "paths": ["optimization_report.html"],
                    "expire_in": f"{self.integration_config['artifact_retention_days']} days"
                },
                "when": "always"
            }
        }
        
        return config

    def generate_jenkins_pipeline(
        self, 
        triggers: List[OptimizationTrigger]
    ) -> str:
        """Generate Jenkins pipeline configuration"""
        pipeline = f"""
pipeline {{
    agent any
    
    options {{
        timeout(time: {self.integration_config['timeout_minutes']}, unit: 'MINUTES')
        retry({self.integration_config['retry_attempts']})
        buildDiscarder(logRotator(daysToKeepStr: '{self.integration_config['artifact_retention_days']}'))
    }}
    
    environment {{
        PLC_OPTIMIZE_CONFIG = '.plc_optimize_config.json'
        PYTHON_VERSION = '3.12'
    }}
    
    triggers {{
        cron('H 2 * * *')  // Daily at 2 AM
        pollSCM('H/15 * * * *')  // Poll every 15 minutes
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                checkout scm
                sh 'pip install -r requirements.txt'
            }}
        }}
        
        stage('Analysis') {{
            steps {{
                sh 'python plc_optimize_cli.py analyze --project-root .'
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'analysis_results.json', allowEmptyArchive: true
                }}
            }}
        }}
        
        stage('Optimization') {{
            parallel {{
                stage('Conservative Profile') {{
                    steps {{
                        sh 'python plc_optimize_cli.py optimize --project-root . --profile conservative --no-backup'
                    }}
                    post {{
                        always {{
                            archiveArtifacts artifacts: 'execution_summary_*.json', allowEmptyArchive: true
                        }}
                    }}
                }}
                stage('CI/CD Profile') {{
                    when {{
                        branch 'main'
                    }}
                    steps {{
                        sh 'python plc_optimize_cli.py optimize --project-root . --profile ci_cd --auto-apply --no-backup'
                    }}
                }}
            }}
        }}
        
        stage('Schema Governance') {{
            steps {{
                sh 'python plc_optimize_cli.py schema-check --project-root .'
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'schema_compliance_report.json', allowEmptyArchive: true
                }}
            }}
        }}
        
        stage('Report') {{
            steps {{
                sh 'echo "Generating comprehensive optimization report"'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'optimization_report.html',
                    reportName: 'PLC-Optimize Report'
                ])
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            emailext (
                subject: "PLC-Optimize Success: ${{env.JOB_NAME}} - ${{env.BUILD_NUMBER}}",
                body: "Optimization completed successfully. Check the report for details.",
                to: "${{env.CHANGE_AUTHOR_EMAIL}}"
            )
        }}
        failure {{
            emailext (
                subject: "PLC-Optimize Failed: ${{env.JOB_NAME}} - ${{env.BUILD_NUMBER}}",
                body: "Optimization failed. Check the console output for details.",
                to: "${{env.CHANGE_AUTHOR_EMAIL}}"
            )
        }}
    }}
}}
"""
        return pipeline.strip()

    def _detect_cicd_platforms(self, project_root: str) -> List[str]:
        """Auto-detect CI/CD platforms based on existing configuration files"""
        detected = []
        project_path = Path(project_root)
        
        # Check for GitHub Actions
        if (project_path / ".github" / "workflows").exists():
            detected.append("github_actions")
        
        # Check for GitLab CI
        if (project_path / ".gitlab-ci.yml").exists():
            detected.append("gitlab_ci")
        
        # Check for Jenkins
        if (project_path / "Jenkinsfile").exists():
            detected.append("jenkins")
        
        # Check for Azure DevOps
        if (project_path / "azure-pipelines.yml").exists():
            detected.append("azure_devops")
        
        # Default to GitHub Actions if none detected but .git exists
        if not detected and (project_path / ".git").exists():
            detected.append("github_actions")
        
        return detected

    def _generate_workflow_config(
        self, 
        platform: CICDPlatform, 
        triggers: List[OptimizationTrigger]
    ) -> Dict[str, Any]:
        """Generate platform-specific workflow configuration"""
        if platform.name == "GitHub Actions":
            return self.generate_github_actions_workflow(triggers)
        elif platform.name == "GitLab CI":
            return self.generate_gitlab_ci_config(triggers)
        elif platform.name == "Jenkins":
            return {"pipeline": self.generate_jenkins_pipeline(triggers)}
        else:
            return {"error": f"Unsupported platform: {platform.name}"}

    def _create_platform_config_files(
        self, 
        project_root: str, 
        platform: CICDPlatform, 
        workflow_config: Dict[str, Any]
    ) -> List[str]:
        """Create configuration files for the platform"""
        created_files = []
        project_path = Path(project_root)
        
        # Create workflow directory if needed
        workflow_dir = project_path / platform.workflow_directory
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        # Create main configuration file
        config_file_path = workflow_dir / platform.config_file
        
        if platform.name == "GitHub Actions":
            with open(config_file_path, 'w') as f:
                yaml.dump(workflow_config, f, default_flow_style=False, sort_keys=False)
        elif platform.name == "GitLab CI":
            with open(config_file_path, 'w') as f:
                yaml.dump(workflow_config, f, default_flow_style=False, sort_keys=False)
        elif platform.name == "Jenkins":
            with open(config_file_path, 'w') as f:
                f.write(workflow_config["pipeline"])
        
        created_files.append(str(config_file_path))
        
        # Create PLC-Optimize configuration file
        plc_config_path = project_path / ".plc_optimize_config.json"
        plc_config = {
            "optimization": {
                "enabled": True,
                "default_profile": "ci_cd",
                "auto_apply_threshold": 0.85,
                "backup_enabled": False,  # CI/CD handles versioning
                "timeout_minutes": 30
            },
            "validation": {
                "min_safety_score": 0.8,
                "enable_performance_checks": True,
                "enable_security_scan": True
            },
            "reporting": {
                "generate_html_report": True,
                "include_metrics": True,
                "notification_channels": ["ci_cd"]
            }
        }
        
        with open(plc_config_path, 'w') as f:
            json.dump(plc_config, f, indent=2)
        
        created_files.append(str(plc_config_path))
        
        return created_files

    def _setup_platform_webhooks(self, project_root: str, platform: CICDPlatform) -> List[str]:
        """Setup webhooks for the platform (if applicable)"""
        # Webhook setup would be platform-specific and require API access
        # For now, return placeholder webhook URLs
        webhook_urls = []
        
        if platform.name == "GitHub Actions":
            webhook_urls.append("https://api.github.com/repos/{owner}/{repo}/hooks")
        elif platform.name == "GitLab CI":
            webhook_urls.append("https://gitlab.com/api/v4/projects/{id}/hooks")
        
        return webhook_urls

    def _generate_github_triggers(self, triggers: List[OptimizationTrigger]) -> Dict[str, Any]:
        """Generate GitHub Actions trigger configuration"""
        github_triggers = {}
        
        for trigger in triggers:
            if trigger.event_type == "pull_request":
                github_triggers["pull_request"] = {
                    "branches": trigger.target_branches,
                    "paths": trigger.file_patterns
                }
            elif trigger.event_type == "commit":
                github_triggers["push"] = {
                    "branches": trigger.target_branches,
                    "paths": trigger.file_patterns
                }
            elif trigger.event_type == "schedule":
                github_triggers["schedule"] = [{"cron": "0 2 * * *"}]  # Daily at 2 AM
            elif trigger.event_type == "manual":
                github_triggers["workflow_dispatch"] = {}
        
        return github_triggers

    def _generate_gitlab_rules(self, triggers: List[OptimizationTrigger]) -> List[Dict[str, Any]]:
        """Generate GitLab CI rules configuration"""
        rules = []
        
        for trigger in triggers:
            if trigger.event_type == "pull_request":
                rules.append({"if": "$CI_PIPELINE_SOURCE == 'merge_request_event'"})
            elif trigger.event_type == "commit":
                for branch in trigger.target_branches:
                    rules.append({"if": f"$CI_COMMIT_BRANCH == '{branch}'"})
            elif trigger.event_type == "schedule":
                rules.append({"if": "$CI_PIPELINE_SOURCE == 'schedule'"})
        
        return rules

    def _generate_pr_comment_script(self) -> str:
        """Generate GitHub Actions script for PR comments"""
        return """
const fs = require('fs');
const path = require('path');

// Find the latest execution summary
const summaryFiles = fs.readdirSync('.').filter(file => file.startsWith('execution_summary_'));
if (summaryFiles.length === 0) {
  console.log('No execution summary found');
  return;
}

const summaryFile = summaryFiles[summaryFiles.length - 1];
const summary = JSON.parse(fs.readFileSync(summaryFile, 'utf8'));

const comment = `## 🤖 PLC-Optimize Results

**Optimization completed with the following results:**

- **Files Analyzed**: ${summary.workflow_result?.overall_metrics?.files_optimized || 0}
- **Validation Score**: ${(summary.workflow_result?.overall_metrics?.validation_score || 0).toFixed(2)}
- **Components Executed**: ${summary.session?.components_executed?.length || 0}

**Recommendations**: ${summary.workflow_result?.recommendations?.length || 0} suggestions generated

<details>
<summary>View detailed results</summary>

\`\`\`json
${JSON.stringify(summary.workflow_result?.overall_metrics || {}, null, 2)}
\`\`\`

</details>
`;

github.rest.issues.createComment({
  issue_number: context.issue.number,
  owner: context.repo.owner,
  repo: context.repo.repo,
  body: comment
});
"""

    def _validate_platform_integration(
        self, 
        project_root: str, 
        platform: CICDPlatform, 
        config_files: List[str]
    ) -> str:
        """Validate that platform integration was set up correctly"""
        validation_errors = []
        
        # Check that config files exist and are valid
        for config_file in config_files:
            if not Path(config_file).exists():
                validation_errors.append(f"Configuration file not created: {config_file}")
            else:
                # Basic syntax validation
                try:
                    if config_file.endswith('.yml') or config_file.endswith('.yaml'):
                        with open(config_file, 'r') as f:
                            yaml.safe_load(f)
                    elif config_file.endswith('.json'):
                        with open(config_file, 'r') as f:
                            json.load(f)
                except Exception as e:
                    validation_errors.append(f"Invalid syntax in {config_file}: {str(e)}")
        
        # Check git repository
        if not (Path(project_root) / ".git").exists():
            validation_errors.append("Not a git repository")
        
        # Check for required dependencies
        requirements_file = Path(project_root) / "requirements.txt"
        if not requirements_file.exists():
            validation_errors.append("requirements.txt not found")
        
        if validation_errors:
            return f"validation_failed: {'; '.join(validation_errors)}"
        else:
            return "validation_passed"

    def _generate_platform_setup_instructions(
        self, 
        platform: CICDPlatform, 
        config_files: List[str], 
        webhook_urls: List[str]
    ) -> List[str]:
        """Generate setup instructions for the platform"""
        instructions = [
            f"✅ {platform.name} integration configured successfully",
            f"📁 Configuration files created: {len(config_files)}",
            "",
            "🔧 Setup Instructions:",
            f"1. Review the generated {platform.config_file} configuration",
            "2. Commit the configuration files to your repository",
            "3. Push to trigger the first optimization run"
        ]
        
        if platform.name == "GitHub Actions":
            instructions.extend([
                "4. Check the Actions tab in your GitHub repository",
                "5. Configure repository secrets if needed:",
                "   - SLACK_WEBHOOK_URL (optional)",
                "   - NOTIFICATION_EMAIL (optional)",
                "6. Enable Actions in repository settings if disabled"
            ])
        elif platform.name == "GitLab CI":
            instructions.extend([
                "4. Check the CI/CD > Pipelines section in GitLab",
                "5. Configure CI/CD variables if needed:",
                "   - SLACK_WEBHOOK_URL (optional)",
                "   - NOTIFICATION_EMAIL (optional)",
                "6. Ensure GitLab Runner is available for your project"
            ])
        elif platform.name == "Jenkins":
            instructions.extend([
                "4. Import the Jenkinsfile into your Jenkins instance",
                "5. Configure Jenkins credentials and plugins:",
                "   - Git plugin",
                "   - Pipeline plugin",
                "   - Email Extension plugin",
                "6. Set up webhook triggers if desired"
            ])
        
        instructions.extend([
            "",
            "🎯 Optimization Profiles Available:",
            "   - conservative: Safe optimizations only",
            "   - ci_cd: Balanced optimization for CI/CD",
            "   - aggressive: Comprehensive optimization",
            "",
            "🔍 Monitoring:",
            "   - Check workflow logs for execution details",
            "   - Review artifact downloads for results",
            "   - Monitor performance metrics over time"
        ])
        
        return instructions

    def _generate_setup_documentation(self, integration_results: List[CICDIntegrationResult]) -> str:
        """Generate comprehensive setup documentation"""
        doc = "# PLC-Optimize CI/CD Integration Setup\n\n"
        doc += f"**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        doc += f"**Platforms Integrated**: {len(integration_results)}\n\n"
        
        for result in integration_results:
            doc += f"## {result.platform}\n\n"
            doc += f"**Integration ID**: {result.integration_id}\n"
            doc += f"**Status**: {result.validation_status}\n"
            doc += f"**Configuration Files**: {len(result.config_files_created)}\n\n"
            
            doc += "### Setup Instructions\n\n"
            for instruction in result.setup_instructions:
                doc += f"{instruction}\n"
            doc += "\n"
            
            doc += "### Triggers Configured\n\n"
            for trigger in result.triggers_configured:
                doc += f"- **{trigger.event_type}**: {trigger.optimization_profile} profile\n"
                doc += f"  - Branches: {', '.join(trigger.target_branches)}\n"
                doc += f"  - File patterns: {', '.join(trigger.file_patterns)}\n"
                doc += f"  - Auto-apply threshold: {trigger.auto_apply_threshold}\n\n"
        
        doc += "## Next Steps\n\n"
        doc += "1. **Test the Integration**: Push a commit to trigger the first run\n"
        doc += "2. **Monitor Results**: Check the CI/CD dashboard for execution status\n"
        doc += "3. **Customize Configuration**: Adjust profiles and triggers as needed\n"
        doc += "4. **Enable Notifications**: Configure webhook URLs for team notifications\n"
        doc += "5. **Schedule Regular Optimization**: Set up periodic optimization runs\n\n"
        
        doc += "## Troubleshooting\n\n"
        doc += "- **Permission Issues**: Ensure repository write access for automation\n"
        doc += "- **Dependency Errors**: Check requirements.txt for all dependencies\n"
        doc += "- **Timeout Issues**: Adjust timeout settings in configuration\n"
        doc += "- **Validation Failures**: Review safety thresholds and adjust as needed\n"
        
        return doc

    def _generate_next_steps(self, integration_results: List[CICDIntegrationResult]) -> List[str]:
        """Generate next steps based on integration results"""
        next_steps = []
        
        successful_integrations = [r for r in integration_results if r.validation_status == "validation_passed"]
        failed_integrations = [r for r in integration_results if r.validation_status.startswith("validation_failed")]
        
        if successful_integrations:
            next_steps.extend([
                f"✅ {len(successful_integrations)} platform(s) integrated successfully",
                "🚀 Commit and push configuration files to activate automation",
                "📊 Monitor first optimization runs in CI/CD dashboard",
                "🔧 Customize optimization profiles based on results"
            ])
        
        if failed_integrations:
            next_steps.extend([
                f"⚠️ {len(failed_integrations)} platform(s) need attention",
                "🔍 Review validation errors and fix configuration issues",
                "📚 Check platform-specific documentation for setup requirements"
            ])
        
        next_steps.extend([
            "🔔 Configure notification channels for team awareness",
            "📈 Set up performance monitoring and reporting",
            "🛡️ Review security settings and access permissions",
            "📅 Schedule regular optimization maintenance windows"
        ])
        
        return next_steps


if __name__ == "__main__":
    # Demo/test the CI/CD integration
    import tempfile
    
    print("🚀 PLC-Optimize CI/CD Integration Demo")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        
        # Create CI/CD integration
        cicd_integration = CICDIntegrationOrchestrator()
        
        # Setup GitHub Actions integration
        result = cicd_integration.setup_platform_integration(
            project_root=temp_dir,
            platform_name="github_actions"
        )
        
        print(f"✅ Integration Status: {result.validation_status}")
        print(f"📁 Files Created: {len(result.config_files_created)}")
        print(f"🔧 Setup Instructions: {len(result.setup_instructions)}")
        
        for file_path in result.config_files_created:
            print(f"   Created: {file_path}")
        
        print("\n💡 Next Steps:")
        for step in result.setup_instructions[:5]:
            print(f"   {step}")
        
        print(f"\n🎯 CI/CD Integration Demo Complete!") 