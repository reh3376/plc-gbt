#!/usr/bin/env python3
"""
Secure Configuration Manager for PLC-GPT
Phase 15.1: Enterprise Secrets Management

This module provides secure configuration management that integrates with
HashiCorp Vault and replaces hardcoded credentials throughout the system.

Features:
- Vault integration for secrets
- Environment variable fallback
- Configuration validation
- Automatic credential rotation
- Secure defaults and validation

Following AI Task Orchestrator methodology for systematic security enhancement.
"""

import asyncio
import logging
import os
import json
import time
from typing import Dict, List, Any, Optional, Union, Type
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import uuid

# Import our security components
from .vault_secrets_manager import (
    VaultSecretsManager, 
    get_vault_secrets_manager,
    DatabaseCredentials,
    APIKeyCredentials,
    SecretType
)

# Configuration validation
try:
    from pydantic import BaseModel, Field, validator
    from pydantic.env_settings import BaseSettings
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    logging.warning("pydantic not available for configuration validation")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigurationSource(Enum):
    """Sources for configuration values."""
    VAULT = "vault"
    ENVIRONMENT = "environment"
    DEFAULT = "default"
    FILE = "file"


@dataclass
class ConfigurationItem:
    """Configuration item with metadata."""
    key: str
    value: Any
    source: ConfigurationSource
    secret: bool = False
    required: bool = False
    description: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class DatabaseConfig:
    """Database configuration structure."""
    host: str
    port: int
    username: str
    password: str
    database: str
    ssl_mode: str = "require"
    connection_timeout: int = 30
    max_connections: int = 100
    pool_size: int = 10
    pool_timeout: int = 30
    
    def get_connection_string(self, database_type: str) -> str:
        """Get database connection string."""
        if database_type.lower() == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.ssl_mode}"
        elif database_type.lower() == "neo4j":
            return f"bolt://{self.host}:{self.port}"
        elif database_type.lower() == "redis":
            auth_part = f":{self.password}@" if self.password else ""
            return f"redis://{auth_part}{self.host}:{self.port}/{self.database}"
        else:
            return f"{database_type}://{self.host}:{self.port}"


@dataclass
class SecurityConfig:
    """Security configuration structure."""
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 7
    password_min_length: int = 12
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 120
    
    def validate_password_policy(self, password: str) -> bool:
        """Validate password against security policy."""
        if len(password) < self.password_min_length:
            return False
        
        if self.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        if self.password_require_numbers and not any(c.isdigit() for c in password):
            return False
        
        if self.password_require_uppercase and not any(c.isupper() for c in password):
            return False
        
        return True


@dataclass
class NetworkConfig:
    """Network configuration structure."""
    bind_host: str = "127.0.0.1"  # Secure default - no 0.0.0.0
    bind_port: int = 8000
    allowed_hosts: List[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    max_connections: int = 1000
    connection_timeout: int = 30
    read_timeout: int = 30
    write_timeout: int = 30
    
    def is_host_allowed(self, host: str) -> bool:
        """Check if host is allowed."""
        return host in self.allowed_hosts


@dataclass
class MonitoringConfig:
    """Monitoring configuration structure."""
    enabled: bool = True
    metrics_port: int = 8090
    health_check_interval: int = 30
    log_level: str = "INFO"
    audit_enabled: bool = True
    performance_tracking: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 80.0,
        "memory_usage": 85.0,
        "disk_usage": 90.0,
        "response_time": 1.0
    })


class SecureConfigManager:
    """
    Secure configuration manager with Vault integration.
    
    This class provides secure configuration management that:
    - Integrates with HashiCorp Vault for secrets
    - Validates configuration against security policies
    - Provides secure defaults
    - Supports automatic credential rotation
    - Logs all configuration access for audit
    """
    
    def __init__(
        self,
        vault_manager: VaultSecretsManager = None,
        config_file: str = None,
        environment_prefix: str = "PLC_GPT"
    ):
        """
        Initialize secure configuration manager.
        
        Args:
            vault_manager: Vault secrets manager instance
            config_file: Optional configuration file path
            environment_prefix: Prefix for environment variables
        """
        self.vault_manager = vault_manager or get_vault_secrets_manager()
        self.config_file = Path(config_file) if config_file else None
        self.environment_prefix = environment_prefix
        
        # Configuration storage
        self.config_items: Dict[str, ConfigurationItem] = {}
        self.database_configs: Dict[str, DatabaseConfig] = {}
        self.security_config: Optional[SecurityConfig] = None
        self.network_config: Optional[NetworkConfig] = None
        self.monitoring_config: Optional[MonitoringConfig] = None
        
        # Configuration cache
        self.cache_ttl = 300  # 5 minutes
        self.last_refresh = 0
        
        # Audit logging
        self.audit_log_path = Path("logs/config_audit.log")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("SecureConfigManager initialized")
    
    def _audit_log(self, operation: str, key: str, source: ConfigurationSource, success: bool, details: Dict[str, Any] = None):
        """Log configuration access for audit."""
        audit_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "key": key,
            "source": source.value,
            "success": success,
            "details": details or {},
            "user": os.getenv("USER", "system"),
            "session_id": str(uuid.uuid4())
        }
        
        try:
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(audit_event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write config audit log: {e}")
    
    async def initialize_configuration(self):
        """Initialize all configuration from various sources."""
        try:
            logger.info("🔧 Initializing secure configuration...")
            
            # Load database configurations
            await self._load_database_configs()
            
            # Load security configuration
            await self._load_security_config()
            
            # Load network configuration
            await self._load_network_config()
            
            # Load monitoring configuration
            await self._load_monitoring_config()
            
            # Load additional configuration items
            await self._load_additional_configs()
            
            logger.info("✅ Secure configuration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize configuration: {e}")
            raise
    
    async def _load_database_configs(self):
        """Load database configurations from Vault."""
        database_names = ["postgresql", "neo4j", "redis", "qdrant"]
        
        for db_name in database_names:
            try:
                # Try to get from Vault first
                db_creds = await self.vault_manager.get_database_credentials(db_name)
                
                if db_creds:
                    self.database_configs[db_name] = DatabaseConfig(
                        host=db_creds.host,
                        port=db_creds.port,
                        username=db_creds.username,
                        password=db_creds.password,
                        database=db_creds.database,
                        ssl_mode=db_creds.ssl_mode,
                        connection_timeout=db_creds.connection_timeout,
                        max_connections=db_creds.max_connections
                    )
                    
                    self._audit_log("load_database_config", db_name, ConfigurationSource.VAULT, True)
                    logger.info(f"✅ Loaded {db_name} config from Vault")
                else:
                    # Fallback to environment variables
                    config = self._load_database_config_from_env(db_name)
                    if config:
                        self.database_configs[db_name] = config
                        self._audit_log("load_database_config", db_name, ConfigurationSource.ENVIRONMENT, True)
                        logger.info(f"✅ Loaded {db_name} config from environment")
                    else:
                        logger.warning(f"❌ No configuration found for {db_name}")
                        
            except Exception as e:
                logger.error(f"Failed to load {db_name} configuration: {e}")
                self._audit_log("load_database_config", db_name, ConfigurationSource.VAULT, False, {"error": str(e)})
    
    def _load_database_config_from_env(self, db_name: str) -> Optional[DatabaseConfig]:
        """Load database configuration from environment variables."""
        prefix = f"{self.environment_prefix}_{db_name.upper()}"
        
        host = os.getenv(f"{prefix}_HOST")
        port = os.getenv(f"{prefix}_PORT")
        username = os.getenv(f"{prefix}_USERNAME")
        password = os.getenv(f"{prefix}_PASSWORD")
        database = os.getenv(f"{prefix}_DATABASE")
        
        if not all([host, port, username, database]):
            return None
        
        return DatabaseConfig(
            host=host,
            port=int(port),
            username=username,
            password=password or "",
            database=database,
            ssl_mode=os.getenv(f"{prefix}_SSL_MODE", "require"),
            connection_timeout=int(os.getenv(f"{prefix}_CONNECTION_TIMEOUT", "30")),
            max_connections=int(os.getenv(f"{prefix}_MAX_CONNECTIONS", "100"))
        )
    
    async def _load_security_config(self):
        """Load security configuration."""
        try:
            # Try to get JWT secret from Vault
            jwt_secret_data = await self.vault_manager.get_secret("jwt_secret/main")
            
            if jwt_secret_data:
                jwt_secret = jwt_secret_data.get("secret")
                jwt_algorithm = jwt_secret_data.get("algorithm", "HS256")
                jwt_expiration_hours = jwt_secret_data.get("expiration_hours", 24)
                source = ConfigurationSource.VAULT
            else:
                # Fallback to environment
                jwt_secret = os.getenv(f"{self.environment_prefix}_JWT_SECRET")
                jwt_algorithm = os.getenv(f"{self.environment_prefix}_JWT_ALGORITHM", "HS256")
                jwt_expiration_hours = int(os.getenv(f"{self.environment_prefix}_JWT_EXPIRATION_HOURS", "24"))
                source = ConfigurationSource.ENVIRONMENT
                
                if not jwt_secret:
                    # Generate a secure default
                    jwt_secret = f"phase15-generated-jwt-secret-{uuid.uuid4().hex[:32]}"
                    source = ConfigurationSource.DEFAULT
                    logger.warning("Generated default JWT secret - set in Vault for production")
            
            self.security_config = SecurityConfig(
                jwt_secret=jwt_secret,
                jwt_algorithm=jwt_algorithm,
                jwt_expiration_hours=jwt_expiration_hours,
                jwt_refresh_expiration_days=int(os.getenv(f"{self.environment_prefix}_JWT_REFRESH_DAYS", "7")),
                password_min_length=int(os.getenv(f"{self.environment_prefix}_PASSWORD_MIN_LENGTH", "12")),
                password_require_special=os.getenv(f"{self.environment_prefix}_PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true",
                password_require_numbers=os.getenv(f"{self.environment_prefix}_PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true",
                password_require_uppercase=os.getenv(f"{self.environment_prefix}_PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
                max_login_attempts=int(os.getenv(f"{self.environment_prefix}_MAX_LOGIN_ATTEMPTS", "5")),
                lockout_duration_minutes=int(os.getenv(f"{self.environment_prefix}_LOCKOUT_DURATION_MINUTES", "30")),
                session_timeout_minutes=int(os.getenv(f"{self.environment_prefix}_SESSION_TIMEOUT_MINUTES", "120"))
            )
            
            self._audit_log("load_security_config", "jwt_secret", source, True)
            logger.info("✅ Security configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load security configuration: {e}")
            self._audit_log("load_security_config", "jwt_secret", ConfigurationSource.VAULT, False, {"error": str(e)})
            raise
    
    async def _load_network_config(self):
        """Load network configuration with secure defaults."""
        try:
            self.network_config = NetworkConfig(
                bind_host=os.getenv(f"{self.environment_prefix}_BIND_HOST", "127.0.0.1"),  # Secure default
                bind_port=int(os.getenv(f"{self.environment_prefix}_BIND_PORT", "8000")),
                allowed_hosts=os.getenv(f"{self.environment_prefix}_ALLOWED_HOSTS", "localhost,127.0.0.1").split(","),
                cors_origins=os.getenv(f"{self.environment_prefix}_CORS_ORIGINS", "http://localhost:3000").split(","),
                max_connections=int(os.getenv(f"{self.environment_prefix}_MAX_CONNECTIONS", "1000")),
                connection_timeout=int(os.getenv(f"{self.environment_prefix}_CONNECTION_TIMEOUT", "30")),
                read_timeout=int(os.getenv(f"{self.environment_prefix}_READ_TIMEOUT", "30")),
                write_timeout=int(os.getenv(f"{self.environment_prefix}_WRITE_TIMEOUT", "30"))
            )
            
            # Validate network configuration
            if self.network_config.bind_host == "0.0.0.0":
                logger.warning("⚠️ Binding to 0.0.0.0 is not secure - consider using 127.0.0.1 or specific IP")
            
            self._audit_log("load_network_config", "network", ConfigurationSource.ENVIRONMENT, True)
            logger.info("✅ Network configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load network configuration: {e}")
            raise
    
    async def _load_monitoring_config(self):
        """Load monitoring configuration."""
        try:
            self.monitoring_config = MonitoringConfig(
                enabled=os.getenv(f"{self.environment_prefix}_MONITORING_ENABLED", "true").lower() == "true",
                metrics_port=int(os.getenv(f"{self.environment_prefix}_METRICS_PORT", "8090")),
                health_check_interval=int(os.getenv(f"{self.environment_prefix}_HEALTH_CHECK_INTERVAL", "30")),
                log_level=os.getenv(f"{self.environment_prefix}_LOG_LEVEL", "INFO"),
                audit_enabled=os.getenv(f"{self.environment_prefix}_AUDIT_ENABLED", "true").lower() == "true",
                performance_tracking=os.getenv(f"{self.environment_prefix}_PERFORMANCE_TRACKING", "true").lower() == "true"
            )
            
            self._audit_log("load_monitoring_config", "monitoring", ConfigurationSource.ENVIRONMENT, True)
            logger.info("✅ Monitoring configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load monitoring configuration: {e}")
            raise
    
    async def _load_additional_configs(self):
        """Load additional configuration items."""
        try:
            # OpenAI API configuration
            openai_creds = await self.vault_manager.get_api_key("openai")
            if openai_creds:
                self.config_items["openai_api_key"] = ConfigurationItem(
                    key="openai_api_key",
                    value=openai_creds.api_key,
                    source=ConfigurationSource.VAULT,
                    secret=True,
                    required=True,
                    description="OpenAI API key for AI model access"
                )
                self._audit_log("load_config", "openai_api_key", ConfigurationSource.VAULT, True)
            else:
                # Fallback to environment
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.config_items["openai_api_key"] = ConfigurationItem(
                        key="openai_api_key",
                        value=api_key,
                        source=ConfigurationSource.ENVIRONMENT,
                        secret=True,
                        required=True,
                        description="OpenAI API key for AI model access"
                    )
                    self._audit_log("load_config", "openai_api_key", ConfigurationSource.ENVIRONMENT, True)
            
            # Additional configuration items can be added here
            
        except Exception as e:
            logger.error(f"Failed to load additional configurations: {e}")
    
    def get_database_config(self, database_name: str) -> Optional[DatabaseConfig]:
        """
        Get database configuration.
        
        Args:
            database_name: Database name (postgresql, neo4j, redis, qdrant)
            
        Returns:
            DatabaseConfig object or None if not found
        """
        config = self.database_configs.get(database_name)
        if config:
            self._audit_log("get_database_config", database_name, ConfigurationSource.VAULT, True)
        else:
            self._audit_log("get_database_config", database_name, ConfigurationSource.VAULT, False, {"error": "not_found"})
        
        return config
    
    def get_security_config(self) -> Optional[SecurityConfig]:
        """Get security configuration."""
        if self.security_config:
            self._audit_log("get_security_config", "security", ConfigurationSource.VAULT, True)
        
        return self.security_config
    
    def get_network_config(self) -> Optional[NetworkConfig]:
        """Get network configuration."""
        if self.network_config:
            self._audit_log("get_network_config", "network", ConfigurationSource.ENVIRONMENT, True)
        
        return self.network_config
    
    def get_monitoring_config(self) -> Optional[MonitoringConfig]:
        """Get monitoring configuration."""
        if self.monitoring_config:
            self._audit_log("get_monitoring_config", "monitoring", ConfigurationSource.ENVIRONMENT, True)
        
        return self.monitoring_config
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        config_item = self.config_items.get(key)
        if config_item:
            self._audit_log("get_config_value", key, config_item.source, True)
            return config_item.value
        
        # Try environment variable
        env_key = f"{self.environment_prefix}_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value:
            self._audit_log("get_config_value", key, ConfigurationSource.ENVIRONMENT, True)
            return env_value
        
        self._audit_log("get_config_value", key, ConfigurationSource.DEFAULT, True)
        return default
    
    async def refresh_configuration(self):
        """Refresh configuration from all sources."""
        try:
            logger.info("🔄 Refreshing configuration...")
            
            # Clear existing configuration
            self.config_items.clear()
            self.database_configs.clear()
            
            # Reload all configuration
            await self.initialize_configuration()
            
            self.last_refresh = time.time()
            logger.info("✅ Configuration refreshed successfully")
            
        except Exception as e:
            logger.error(f"Failed to refresh configuration: {e}")
            raise
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate current configuration.
        
        Returns:
            Validation results dictionary
        """
        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "valid",
            "issues": [],
            "warnings": [],
            "database_configs": {},
            "security_config": {},
            "network_config": {},
            "monitoring_config": {}
        }
        
        try:
            # Validate database configurations
            for db_name, config in self.database_configs.items():
                db_validation = {
                    "status": "valid",
                    "issues": []
                }
                
                # Check required fields
                if not config.host:
                    db_validation["issues"].append("Missing host")
                if not config.username:
                    db_validation["issues"].append("Missing username")
                if not config.password and db_name != "qdrant":
                    db_validation["issues"].append("Missing password")
                
                # Check security settings
                if config.ssl_mode == "disable":
                    validation_results["warnings"].append(f"{db_name}: SSL disabled")
                
                if db_validation["issues"]:
                    db_validation["status"] = "invalid"
                    validation_results["overall_status"] = "invalid"
                
                validation_results["database_configs"][db_name] = db_validation
            
            # Validate security configuration
            if self.security_config:
                security_validation = {
                    "status": "valid",
                    "issues": []
                }
                
                # Check JWT secret strength
                if len(self.security_config.jwt_secret) < 32:
                    security_validation["issues"].append("JWT secret too short (< 32 characters)")
                
                # Check password policy
                if self.security_config.password_min_length < 8:
                    security_validation["issues"].append("Password minimum length too low (< 8)")
                
                if security_validation["issues"]:
                    security_validation["status"] = "invalid"
                    validation_results["overall_status"] = "invalid"
                
                validation_results["security_config"] = security_validation
            
            # Validate network configuration
            if self.network_config:
                network_validation = {
                    "status": "valid",
                    "issues": []
                }
                
                # Check bind address
                if self.network_config.bind_host == "0.0.0.0":
                    validation_results["warnings"].append("Binding to 0.0.0.0 is not secure")
                
                # Check allowed hosts
                if not self.network_config.allowed_hosts:
                    network_validation["issues"].append("No allowed hosts configured")
                
                if network_validation["issues"]:
                    network_validation["status"] = "invalid"
                    validation_results["overall_status"] = "invalid"
                
                validation_results["network_config"] = network_validation
            
            # Set overall status
            if validation_results["issues"] or any(
                db_config.get("status") == "invalid" 
                for db_config in validation_results["database_configs"].values()
            ):
                validation_results["overall_status"] = "invalid"
            elif validation_results["warnings"]:
                validation_results["overall_status"] = "warning"
            
            logger.info(f"Configuration validation: {validation_results['overall_status']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            validation_results["overall_status"] = "error"
            validation_results["issues"].append(f"Validation error: {str(e)}")
            return validation_results
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "last_refresh": datetime.fromtimestamp(self.last_refresh).isoformat() if self.last_refresh else None,
            "database_configs": len(self.database_configs),
            "config_items": len(self.config_items),
            "security_config_loaded": self.security_config is not None,
            "network_config_loaded": self.network_config is not None,
            "monitoring_config_loaded": self.monitoring_config is not None,
            "vault_available": self.vault_manager.vault_available,
            "configuration_sources": {}
        }
        
        # Count configuration sources
        for item in self.config_items.values():
            source = item.source.value
            summary["configuration_sources"][source] = summary["configuration_sources"].get(source, 0) + 1
        
        return summary


# Global instance for easy access
_secure_config_manager = None


def get_secure_config_manager() -> SecureConfigManager:
    """Get global SecureConfigManager instance."""
    global _secure_config_manager
    
    if _secure_config_manager is None:
        _secure_config_manager = SecureConfigManager()
    
    return _secure_config_manager


async def initialize_secure_configuration():
    """Initialize secure configuration system."""
    config_manager = get_secure_config_manager()
    await config_manager.initialize_configuration()
    return config_manager


if __name__ == "__main__":
    # Test the SecureConfigManager
    async def test_secure_config():
        print("🔧 Testing SecureConfigManager...")
        
        # Initialize configuration
        config_manager = await initialize_secure_configuration()
        
        # Get configuration summary
        summary = config_manager.get_configuration_summary()
        print(f"📊 Configuration Summary: {json.dumps(summary, indent=2)}")
        
        # Validate configuration
        validation = config_manager.validate_configuration()
        print(f"✅ Validation Results: {json.dumps(validation, indent=2)}")
        
        # Test database configuration
        pg_config = config_manager.get_database_config("postgresql")
        if pg_config:
            print(f"🗄️ PostgreSQL Config: {pg_config.host}:{pg_config.port}")
        
        # Test security configuration
        security_config = config_manager.get_security_config()
        if security_config:
            print(f"🔐 Security Config: JWT algorithm={security_config.jwt_algorithm}")
        
        print("🎉 SecureConfigManager test completed!")
    
    # Run test
    asyncio.run(test_secure_config()) 