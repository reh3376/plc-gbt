#!/usr/bin/env python3
"""
🖥️ CLI Configuration Manager

Comprehensive configuration management for the PLC Control Loop CLI with
environment variable support, validation, and persistence.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.1 - Core CLI Infrastructure
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION SCHEMA AND VALIDATION
# =============================================================================

class ConfigurationCategory(Enum):
    """Configuration categories for organization"""
    GENERAL = "general"
    AUTHENTICATION = "authentication"
    PERFORMANCE = "performance"
    LOGGING = "logging"
    ADVANCED = "advanced"
    PATHS = "paths"

@dataclass
class ConfigurationField:
    """Configuration field metadata"""
    name: str
    category: ConfigurationCategory
    data_type: type
    default_value: Any
    description: str
    env_var: Optional[str] = None
    validation_fn: Optional[callable] = None
    choices: Optional[List[str]] = None
    sensitive: bool = False

# =============================================================================
# CONFIGURATION DEFINITIONS
# =============================================================================

CONFIG_SCHEMA = [
    # General settings
    ConfigurationField(
        name="default_output_format",
        category=ConfigurationCategory.GENERAL,
        data_type=str,
        default_value="table",
        description="Default output format for CLI commands",
        env_var="PLC_CL_OUTPUT_FORMAT",
        choices=["table", "json", "yaml", "csv"]
    ),
    ConfigurationField(
        name="color_output",
        category=ConfigurationCategory.GENERAL,
        data_type=bool,
        default_value=True,
        description="Enable colored output",
        env_var="PLC_CL_COLOR"
    ),
    ConfigurationField(
        name="editor",
        category=ConfigurationCategory.GENERAL,
        data_type=str,
        default_value=os.environ.get("EDITOR", "nano"),
        description="Default text editor for editing files",
        env_var="PLC_CL_EDITOR"
    ),
    ConfigurationField(
        name="pager",
        category=ConfigurationCategory.GENERAL,
        data_type=str,
        default_value=os.environ.get("PAGER", "less"),
        description="Default pager for viewing long output",
        env_var="PLC_CL_PAGER"
    ),
    
    # Path settings
    ConfigurationField(
        name="default_schema_registry",
        category=ConfigurationCategory.PATHS,
        data_type=str,
        default_value="plc-gbt-stack/schemas",
        description="Default path to schema registry",
        env_var="PLC_CL_SCHEMA_REGISTRY"
    ),
    ConfigurationField(
        name="default_instances_dir",
        category=ConfigurationCategory.PATHS,
        data_type=str,
        default_value="plc-gbt-stack/instances",
        description="Default directory for control loop instances",
        env_var="PLC_CL_INSTANCES_DIR"
    ),
    ConfigurationField(
        name="templates_dir",
        category=ConfigurationCategory.PATHS,
        data_type=str,
        default_value="plc-gbt-stack/templates",
        description="Directory containing instance templates",
        env_var="PLC_CL_TEMPLATES_DIR"
    ),
    ConfigurationField(
        name="scripts_dir",
        category=ConfigurationCategory.PATHS,
        data_type=str,
        default_value="plc-gbt-stack/scripts/cli",
        description="Directory for CLI scripts",
        env_var="PLC_CL_SCRIPTS_DIR"
    ),
    
    # Authentication settings
    ConfigurationField(
        name="auth_enabled",
        category=ConfigurationCategory.AUTHENTICATION,
        data_type=bool,
        default_value=True,
        description="Enable authentication for CLI operations",
        env_var="PLC_CL_AUTH_ENABLED"
    ),
    ConfigurationField(
        name="api_base_url",
        category=ConfigurationCategory.AUTHENTICATION,
        data_type=str,
        default_value="http://localhost:8000",
        description="Base URL for API authentication",
        env_var="PLC_CL_API_URL"
    ),
    ConfigurationField(
        name="session_timeout",
        category=ConfigurationCategory.AUTHENTICATION,
        data_type=int,
        default_value=3600,
        description="Session timeout in seconds",
        env_var="PLC_CL_SESSION_TIMEOUT",
        validation_fn=lambda x: x > 0
    ),
    ConfigurationField(
        name="auto_login",
        category=ConfigurationCategory.AUTHENTICATION,
        data_type=bool,
        default_value=False,
        description="Automatically login when authentication is required",
        env_var="PLC_CL_AUTO_LOGIN"
    ),
    
    # Performance settings
    ConfigurationField(
        name="max_concurrent_operations",
        category=ConfigurationCategory.PERFORMANCE,
        data_type=int,
        default_value=5,
        description="Maximum concurrent operations for batch commands",
        env_var="PLC_CL_MAX_CONCURRENT",
        validation_fn=lambda x: 1 <= x <= 20
    ),
    ConfigurationField(
        name="cache_enabled",
        category=ConfigurationCategory.PERFORMANCE,
        data_type=bool,
        default_value=True,
        description="Enable caching for improved performance",
        env_var="PLC_CL_CACHE_ENABLED"
    ),
    ConfigurationField(
        name="cache_ttl",
        category=ConfigurationCategory.PERFORMANCE,
        data_type=int,
        default_value=300,
        description="Cache time-to-live in seconds",
        env_var="PLC_CL_CACHE_TTL",
        validation_fn=lambda x: x > 0
    ),
    ConfigurationField(
        name="request_timeout",
        category=ConfigurationCategory.PERFORMANCE,
        data_type=int,
        default_value=30,
        description="Request timeout in seconds",
        env_var="PLC_CL_REQUEST_TIMEOUT",
        validation_fn=lambda x: x > 0
    ),
    
    # Logging settings
    ConfigurationField(
        name="log_level",
        category=ConfigurationCategory.LOGGING,
        data_type=str,
        default_value="info",
        description="Logging level",
        env_var="PLC_CL_LOG_LEVEL",
        choices=["debug", "info", "warning", "error"]
    ),
    ConfigurationField(
        name="log_file",
        category=ConfigurationCategory.LOGGING,
        data_type=str,
        default_value="",
        description="Log file path (empty for no file logging)",
        env_var="PLC_CL_LOG_FILE"
    ),
    ConfigurationField(
        name="verbose",
        category=ConfigurationCategory.LOGGING,
        data_type=bool,
        default_value=False,
        description="Enable verbose output",
        env_var="PLC_CL_VERBOSE"
    ),
    ConfigurationField(
        name="audit_logging",
        category=ConfigurationCategory.LOGGING,
        data_type=bool,
        default_value=True,
        description="Enable audit logging for operations",
        env_var="PLC_CL_AUDIT_LOGGING"
    ),
    
    # Advanced settings
    ConfigurationField(
        name="confirm_destructive",
        category=ConfigurationCategory.ADVANCED,
        data_type=bool,
        default_value=True,
        description="Require confirmation for destructive operations",
        env_var="PLC_CL_CONFIRM_DESTRUCTIVE"
    ),
    ConfigurationField(
        name="dry_run_default",
        category=ConfigurationCategory.ADVANCED,
        data_type=bool,
        default_value=False,
        description="Enable dry-run mode by default",
        env_var="PLC_CL_DRY_RUN"
    ),
    ConfigurationField(
        name="plugin_dirs",
        category=ConfigurationCategory.ADVANCED,
        data_type=str,
        default_value="plc-gbt-stack/cli/plugins",
        description="Directories to search for plugins (colon-separated)",
        env_var="PLC_CL_PLUGIN_DIRS"
    ),
    ConfigurationField(
        name="auto_update_check",
        category=ConfigurationCategory.ADVANCED,
        data_type=bool,
        default_value=True,
        description="Automatically check for updates",
        env_var="PLC_CL_AUTO_UPDATE"
    )
]

# =============================================================================
# CONFIGURATION MANAGER
# =============================================================================

class AdvancedConfigurationManager:
    """Advanced configuration manager with validation and environment support"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".plc-control-loop"
        self.config_file = self.config_dir / ".plc-cl-config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create configuration mapping
        self.config_schema = {field.name: field for field in CONFIG_SCHEMA}
        self._config_data: Dict[str, Any] = {}
        self._loaded = False
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from file and environment variables"""
        if self._loaded:
            return self._config_data
        
        # Start with defaults
        config = {}
        for field in CONFIG_SCHEMA:
            config[field.name] = field.default_value
        
        # Load from file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                config.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Override with environment variables
        for field in CONFIG_SCHEMA:
            if field.env_var and field.env_var in os.environ:
                env_value = os.environ[field.env_var]
                try:
                    config[field.name] = self._convert_value(env_value, field.data_type)
                except ValueError as e:
                    logger.warning(f"Invalid environment variable {field.env_var}: {e}")
        
        # Validate configuration
        validated_config = self._validate_configuration(config)
        
        self._config_data = validated_config
        self._loaded = True
        
        return self._config_data
    
    def save_configuration(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to file"""
        try:
            config_to_save = config or self._config_data
            
            # Organize by category for better readability
            organized_config = {}
            for category in ConfigurationCategory:
                category_config = {}
                for field in CONFIG_SCHEMA:
                    if field.category == category and field.name in config_to_save:
                        if not field.sensitive:  # Don't save sensitive values
                            category_config[field.name] = config_to_save[field.name]
                
                if category_config:
                    organized_config[category.value] = category_config
            
            with open(self.config_file, 'w') as f:
                yaml.dump(organized_config, f, default_flow_style=False, sort_keys=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        config = self.load_configuration()
        return config.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a configuration setting"""
        if key not in self.config_schema:
            return False
        
        field = self.config_schema[key]
        
        try:
            # Type conversion and validation
            converted_value = self._convert_value(value, field.data_type)
            
            if field.validation_fn and not field.validation_fn(converted_value):
                raise ValueError(f"Validation failed for {key}")
            
            if field.choices and converted_value not in field.choices:
                raise ValueError(f"Value must be one of: {field.choices}")
            
            self._config_data[key] = converted_value
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to set {key}: {e}")
            return False
    
    def reset_configuration(self) -> bool:
        """Reset configuration to defaults"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            
            self._config_data = {}
            self._loaded = False
            
            # Reload defaults
            self.load_configuration()
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def get_configuration_by_category(self, category: ConfigurationCategory) -> Dict[str, Any]:
        """Get configuration settings by category"""
        config = self.load_configuration()
        result = {}
        
        for field in CONFIG_SCHEMA:
            if field.category == category and field.name in config:
                result[field.name] = config[field.name]
        
        return result
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any errors"""
        config = self.load_configuration()
        return self._validate_configuration(config, return_errors=True)
    
    def get_field_info(self, field_name: str) -> Optional[ConfigurationField]:
        """Get metadata for a configuration field"""
        return self.config_schema.get(field_name)
    
    def list_all_fields(self) -> List[ConfigurationField]:
        """List all available configuration fields"""
        return CONFIG_SCHEMA
    
    def export_configuration(self, format_type: str = "yaml") -> str:
        """Export configuration in specified format"""
        config = self.load_configuration()
        
        if format_type == "json":
            return json.dumps(config, indent=2)
        elif format_type == "yaml":
            return yaml.dump(config, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def import_configuration(self, config_data: str, format_type: str = "yaml") -> bool:
        """Import configuration from string"""
        try:
            if format_type == "json":
                imported_config = json.loads(config_data)
            elif format_type == "yaml":
                imported_config = yaml.safe_load(config_data)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            # Flatten if organized by category
            if any(category.value in imported_config for category in ConfigurationCategory):
                flattened_config = {}
                for category_data in imported_config.values():
                    if isinstance(category_data, dict):
                        flattened_config.update(category_data)
                imported_config = flattened_config
            
            # Validate and save
            validated_config = self._validate_configuration(imported_config)
            self._config_data = validated_config
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False
    
    # =============================================================================
    # PRIVATE METHODS
    # =============================================================================
    
    def _convert_value(self, value: Any, target_type: type) -> Any:
        """Convert value to target type"""
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return str(value)
        else:
            return value
    
    def _validate_configuration(self, config: Dict[str, Any], return_errors: bool = False) -> Union[Dict[str, Any], List[str]]:
        """Validate configuration values"""
        errors = []
        validated_config = config.copy()
        
        for field in CONFIG_SCHEMA:
            value = config.get(field.name, field.default_value)
            
            try:
                # Type validation
                converted_value = self._convert_value(value, field.data_type)
                
                # Custom validation
                if field.validation_fn and not field.validation_fn(converted_value):
                    errors.append(f"Validation failed for {field.name}: {value}")
                    continue
                
                # Choice validation
                if field.choices and converted_value not in field.choices:
                    errors.append(f"{field.name} must be one of {field.choices}, got: {converted_value}")
                    continue
                
                validated_config[field.name] = converted_value
                
            except (ValueError, TypeError) as e:
                errors.append(f"Invalid value for {field.name}: {value} ({e})")
        
        if return_errors:
            return errors
        
        if errors:
            logger.warning(f"Configuration validation warnings: {errors}")
        
        return validated_config 