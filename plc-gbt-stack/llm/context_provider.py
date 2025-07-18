"""
Application Context Provider
Phase 23.1.3: Dynamic Context Generation for LLM

Provides comprehensive application context including CLI commands, schemas,
performance metrics, and current system state for informed LLM interactions.
"""

import os
import json
import subprocess
import time
import glob
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict
from datetime import datetime, timezone
import logging

from . import ApplicationContext, ConversationMessage, ConversationRole

logger = logging.getLogger(__name__)

class ContextProvider:
    """Provides dynamic application context for LLM interactions"""
    
    def __init__(self, base_directory: str = None):
        self.base_directory = base_directory or os.getcwd()
        self.context_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_context_update = 0
        
    def get_application_context(self, force_refresh: bool = False) -> ApplicationContext:
        """Get comprehensive application context"""
        current_time = time.time()
        
        # Use cache if recent and not forcing refresh
        if (not force_refresh and 
            self.context_cache and 
            current_time - self.last_context_update < self.cache_ttl):
            return self._build_context_from_cache()
        
        # Generate fresh context
        context = ApplicationContext(
            current_directory=self._get_current_directory(),
            available_commands=self._get_available_commands(),
            active_schemas=self._get_active_schemas(),
            recent_operations=self._get_recent_operations(),
            performance_metrics=self._get_performance_metrics(),
            user_preferences=self._get_user_preferences(),
            session_history=[],  # Will be populated by conversation manager
            error_history=self._get_error_history(),
            system_state=self._get_system_state()
        )
        
        # Cache the context data
        self.context_cache = {
            "context": asdict(context),
            "timestamp": current_time
        }
        self.last_context_update = current_time
        
        return context
    
    def _get_current_directory(self) -> str:
        """Get current working directory with project context"""
        cwd = os.getcwd()
        
        # Determine project context
        if "plc-gbt-stack" in cwd:
            relative_path = cwd.split("plc-gbt-stack")[-1].lstrip("/")
            project_context = f"plc-gbt-stack/{relative_path}" if relative_path else "plc-gbt-stack"
        else:
            project_context = os.path.basename(cwd)
            
        return project_context
    
    def _get_available_commands(self) -> List[str]:
        """Get available CLI commands from the application"""
        commands = []
        
        try:
            # Check for plc-cl CLI
            cli_path = os.path.join(self.base_directory, "plc-cl")
            if os.path.exists(cli_path):
                commands.append("plc-cl")
                
                # Try to get help output for available commands
                try:
                    result = subprocess.run(
                        [cli_path, "--help"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        # Parse help output for commands
                        help_lines = result.stdout.split('\n')
                        for line in help_lines:
                            if line.strip().startswith('-') and ' ' in line:
                                cmd = line.strip().split()[0].lstrip('-')
                                if cmd and len(cmd) > 1:
                                    commands.append(f"plc-cl --{cmd}")
                except subprocess.TimeoutExpired:
                    logger.warning("CLI help command timed out")
                except Exception as e:
                    logger.warning(f"Failed to get CLI help: {str(e)}")
            
            # Check for Python scripts
            python_scripts = glob.glob(os.path.join(self.base_directory, "**/*.py"), recursive=True)
            for script in python_scripts[:10]:  # Limit to first 10
                relative_path = os.path.relpath(script, self.base_directory)
                if not relative_path.startswith('.') and 'test' not in relative_path.lower():
                    commands.append(f"python {relative_path}")
            
            # Common analysis commands
            commands.extend([
                "plc-cl create loop",
                "plc-cl analyze performance",
                "plc-cl optimize tuning",
                "plc-cl validate schema",
                "plc-cl export data",
                "plc-cl generate report"
            ])
            
        except Exception as e:
            logger.error(f"Error getting available commands: {str(e)}")
            commands = ["plc-cl", "python"]  # Fallback
            
        return commands
    
    def _get_active_schemas(self) -> List[str]:
        """Get list of active/available schemas"""
        schemas = []
        
        try:
            # Look for schema files
            schema_dirs = [
                os.path.join(self.base_directory, "schemas"),
                os.path.join(self.base_directory, "control"),
                os.path.join(self.base_directory, "instances")
            ]
            
            for schema_dir in schema_dirs:
                if os.path.exists(schema_dir):
                    schema_files = glob.glob(os.path.join(schema_dir, "*.json"))
                    for schema_file in schema_files:
                        schema_name = os.path.basename(schema_file).replace('.json', '')
                        schemas.append(schema_name)
            
            # If no schemas found, provide common ones
            if not schemas:
                schemas = [
                    "pid_controller_schema",
                    "control_loop_schema", 
                    "performance_metrics_schema",
                    "tuning_parameters_schema"
                ]
                
        except Exception as e:
            logger.error(f"Error getting active schemas: {str(e)}")
            schemas = ["basic_control_loop"]
            
        return schemas[:10]  # Limit to first 10
    
    def _get_recent_operations(self) -> List[Dict[str, Any]]:
        """Get recent operations from logs or history"""
        operations = []
        
        try:
            # Check for log files
            log_dirs = [
                os.path.join(self.base_directory, "logs"),
                os.path.join(self.base_directory, "results"),
                "/tmp"
            ]
            
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    log_files = glob.glob(os.path.join(log_dir, "*.log"))
                    log_files.extend(glob.glob(os.path.join(log_dir, "*.json")))
                    
                    # Get most recent files
                    log_files.sort(key=os.path.getmtime, reverse=True)
                    
                    for log_file in log_files[:3]:  # Check last 3 files
                        try:
                            mtime = os.path.getmtime(log_file)
                            # Only include recent files (last 24 hours)
                            if time.time() - mtime < 86400:
                                operations.append({
                                    "type": "file_operation",
                                    "file": os.path.basename(log_file),
                                    "timestamp": datetime.fromtimestamp(mtime).isoformat(),
                                    "size": os.path.getsize(log_file)
                                })
                        except Exception:
                            continue
                            
        except Exception as e:
            logger.error(f"Error getting recent operations: {str(e)}")
            
        # Add some default recent operations if none found
        if not operations:
            operations = [
                {
                    "type": "system_start",
                    "timestamp": datetime.now().isoformat(),
                    "description": "Application session started"
                }
            ]
            
        return operations[:10]  # Limit to 10 most recent
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        metrics = {}
        
        try:
            # Check for performance data files
            results_dir = os.path.join(self.base_directory, "results")
            if os.path.exists(results_dir):
                perf_files = glob.glob(os.path.join(results_dir, "**/*performance*.json"), recursive=True)
                perf_files.extend(glob.glob(os.path.join(results_dir, "**/*validation*.json"), recursive=True))
                
                if perf_files:
                    # Get most recent performance file
                    latest_file = max(perf_files, key=os.path.getmtime)
                    try:
                        with open(latest_file, 'r') as f:
                            perf_data = json.load(f)
                            metrics = {
                                "source": os.path.basename(latest_file),
                                "timestamp": datetime.fromtimestamp(os.path.getmtime(latest_file)).isoformat(),
                                "summary": self._extract_performance_summary(perf_data)
                            }
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in performance file: {latest_file}")
            
            # System performance metrics
            import psutil
            metrics.update({
                "system": {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            metrics = {
                "status": "metrics_unavailable",
                "timestamp": datetime.now().isoformat()
            }
            
        return metrics
    
    def _extract_performance_summary(self, perf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key performance indicators from performance data"""
        summary = {}
        
        # Look for common performance indicators
        if isinstance(perf_data, dict):
            # Check for validation scores
            if "validation_score" in perf_data:
                summary["validation_score"] = perf_data["validation_score"]
            if "overall_score" in perf_data:
                summary["overall_score"] = perf_data["overall_score"]
            
            # Check for completion status
            if "status" in perf_data:
                summary["status"] = perf_data["status"]
            if "completion_status" in perf_data:
                summary["completion_status"] = perf_data["completion_status"]
                
            # Check for capabilities count
            if "capabilities_implemented" in perf_data:
                summary["capabilities"] = perf_data["capabilities_implemented"]
            if "total_capabilities" in perf_data:
                summary["total_capabilities"] = perf_data["total_capabilities"]
                
            # Look for nested performance data
            for key, value in perf_data.items():
                if "performance" in key.lower() and isinstance(value, dict):
                    summary[key] = value
                    
        return summary
    
    def _get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences and settings"""
        preferences = {
            "output_format": "detailed",
            "explanation_level": "intermediate",
            "safety_confirmations": True,
            "auto_validation": True,
            "preferred_libraries": ["matplotlib", "pandas", "numpy"],
            "timezone": "UTC"
        }
        
        try:
            # Look for preferences file
            pref_files = [
                os.path.join(self.base_directory, "config", "preferences.json"),
                os.path.join(os.path.expanduser("~"), ".plc-gbt", "preferences.json")
            ]
            
            for pref_file in pref_files:
                if os.path.exists(pref_file):
                    with open(pref_file, 'r') as f:
                        user_prefs = json.load(f)
                        preferences.update(user_prefs)
                    break
                    
        except Exception as e:
            logger.warning(f"Could not load user preferences: {str(e)}")
            
        return preferences
    
    def _get_error_history(self) -> List[Dict[str, Any]]:
        """Get recent error history"""
        errors = []
        
        try:
            # Check for error logs
            log_dirs = [
                os.path.join(self.base_directory, "logs"),
                "/tmp"
            ]
            
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    error_files = glob.glob(os.path.join(log_dir, "*error*.log"))
                    error_files.extend(glob.glob(os.path.join(log_dir, "*.log")))
                    
                    for error_file in error_files[:3]:  # Check last 3 files
                        try:
                            with open(error_file, 'r') as f:
                                lines = f.readlines()[-50:]  # Last 50 lines
                                
                            for line in lines:
                                if "ERROR" in line or "Exception" in line:
                                    errors.append({
                                        "timestamp": datetime.now().isoformat(),
                                        "source": os.path.basename(error_file),
                                        "message": line.strip()[:200]  # Truncate long messages
                                    })
                                    
                        except Exception:
                            continue
                            
        except Exception as e:
            logger.warning(f"Error getting error history: {str(e)}")
            
        return errors[-5:]  # Return last 5 errors
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": f"session_{int(time.time())}",
            "version": "23.1.0",
            "status": "ready"
        }
        
        try:
            # Check if services are running
            state["services"] = {
                "cli_available": os.path.exists(os.path.join(self.base_directory, "plc-cl")),
                "python_environment": True,
                "analysis_engine": os.path.exists(os.path.join(self.base_directory, "analysis")),
                "llm_integration": True
            }
            
            # Check directory structure
            key_dirs = ["schemas", "instances", "analysis", "docs", "llm"]
            state["directory_structure"] = {
                d: os.path.exists(os.path.join(self.base_directory, d)) for d in key_dirs
            }
            
        except Exception as e:
            logger.error(f"Error getting system state: {str(e)}")
            state["status"] = "error"
            state["error"] = str(e)
            
        return state
    
    def _build_context_from_cache(self) -> ApplicationContext:
        """Build ApplicationContext from cached data"""
        cached_data = self.context_cache["context"]
        return ApplicationContext(**cached_data)
    
    def update_context_with_conversation(
        self, 
        context: ApplicationContext, 
        conversation_history: List[ConversationMessage]
    ) -> ApplicationContext:
        """Update context with conversation history"""
        context.session_history = conversation_history[-10:]  # Keep last 10 messages
        
        # Extract any new user preferences from conversation
        for msg in conversation_history[-3:]:  # Check last 3 messages
            if msg.role == ConversationRole.USER:
                content_lower = msg.content.lower()
                if "prefer" in content_lower or "like" in content_lower:
                    # Simple preference extraction
                    if "detailed" in content_lower:
                        context.user_preferences["explanation_level"] = "detailed"
                    elif "simple" in content_lower:
                        context.user_preferences["explanation_level"] = "simple"
                        
        return context
    
    def get_cli_documentation(self) -> Dict[str, Any]:
        """Get CLI command documentation for context"""
        docs = {
            "available_commands": self._get_available_commands(),
            "command_examples": {
                "create": "plc-cl create loop --name pump_control --type pid",
                "analyze": "plc-cl analyze performance --loop pump_control",
                "optimize": "plc-cl optimize tuning --loop pump_control --method ziegler-nichols",
                "validate": "plc-cl validate schema --file control_loop.json",
                "export": "plc-cl export data --format csv --output results.csv"
            },
            "common_parameters": {
                "--name": "Specify loop or component name",
                "--type": "Specify control loop type (pid, fuzzy, adaptive)",
                "--file": "Input file path",
                "--output": "Output file path",
                "--format": "Export format (csv, json, xml, excel)"
            }
        }
        return docs

# Singleton context provider
_context_provider: Optional[ContextProvider] = None

def get_context_provider(base_directory: str = None) -> ContextProvider:
    """Get singleton context provider instance"""
    global _context_provider
    if _context_provider is None:
        _context_provider = ContextProvider(base_directory)
    return _context_provider

def get_current_context(force_refresh: bool = False) -> ApplicationContext:
    """Quick function to get current application context"""
    provider = get_context_provider()
    return provider.get_application_context(force_refresh)

# Export main components
__all__ = [
    "ContextProvider",
    "get_context_provider",
    "get_current_context"
] 