"""Configuration validation for the PLC Task Orchestrator."""

from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from plc_orchestrator.utils.errors import ConfigurationError


class ConfigValidator:
    """Validator for orchestrator configuration."""

    @staticmethod
    def validate_url(url: str, scheme: str | None = None) -> None:
        """
        Validate URL format.

        This method validates URLs and raises an exception if invalid.
        It does not return a value on success (None return).

        Args:
            url: URL to validate
            scheme: Expected URL scheme

        Raises:
            ConfigurationError: If URL is invalid
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ConfigurationError(f"Invalid URL format: {url}")

            if scheme and parsed.scheme != scheme:
                raise ConfigurationError(
                    f"Invalid URL scheme: expected {scheme}, got {parsed.scheme}"
                )

        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Invalid URL: {url}") from e

    @staticmethod
    def validate_path(path: Path | str, must_exist: bool = False) -> Path:
        """
        Validate filesystem path.

        Args:
            path: Path to validate
            must_exist: Whether path must exist

        Returns:
            Validated Path object

        Raises:
            ConfigurationError: If path is invalid
        """
        try:
            path_obj = Path(path)

            if must_exist and not path_obj.exists():
                raise ConfigurationError(f"Path does not exist: {path}")

            return path_obj

        except Exception as e:
            raise ConfigurationError(f"Invalid path: {path}") from e

    @staticmethod
    def validate_port(port: int) -> None:
        """
        Validate network port number.

        Raises:
            ConfigurationError: If port is invalid
        """
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ConfigurationError(f"Invalid port: {port}. Must be between 1 and 65535")

    @staticmethod
    def validate_api_key(key: str | None, service: str) -> None:
        """
        Validate API key format.

        This method validates API keys and raises an exception if invalid.
        None values are considered valid (optional keys).

        Args:
            key: API key to validate
            service: Service name for error messages

        Raises:
            ConfigurationError: If key format is invalid
        """
        if key is None:
            return  # None is valid (optional key)

        if not isinstance(key, str) or len(key) < 10:
            raise ConfigurationError(f"Invalid {service} API key: must be at least 10 characters")

        # Basic format checks
        if service.lower() == "openai" and not key.startswith("sk-"):
            raise ConfigurationError("Invalid OpenAI API key format: must start with 'sk-'")


# Validation helper functions to reduce complexity
def _validate_environment(config: dict[str, Any], errors: list[str]) -> None:
    """Validate environment setting."""
    if "environment" in config:
        allowed_envs = ["development", "staging", "production", "test"]
        if config["environment"] not in allowed_envs:
            errors.append(
                f"Invalid environment: {config['environment']}. Must be one of {allowed_envs}"
            )


def _validate_paths(config: dict[str, Any], errors: list[str], validator: ConfigValidator) -> None:
    """Validate all path configurations."""
    path_keys = ["project_root", "context_dir", "guides_dir", "summaries_dir"]
    for path_key in path_keys:
        if path_key in config and config[path_key]:
            try:
                validator.validate_path(config[path_key])
            except ConfigurationError as e:
                errors.append(f"{path_key}: {e}")


def _validate_urls(config: dict[str, Any], errors: list[str], validator: ConfigValidator) -> None:
    """Validate all URL configurations."""
    url_configs = [
        ("redis_url", "redis"),
        ("neo4j_uri", "bolt"),
        ("postgres_dsn", "postgresql"),
        ("qdrant_url", "http"),
    ]

    for key, scheme in url_configs:
        if key in config and config[key]:
            try:
                validator.validate_url(config[key], scheme)
            except ConfigurationError as e:
                errors.append(f"{key}: {e}")


def _validate_api_keys(
    config: dict[str, Any], errors: list[str], validator: ConfigValidator
) -> None:
    """Validate all API key configurations."""
    api_keys = [
        ("wolfram_alpha_api_key", "WolframAlpha"),
        ("openai_api_key", "OpenAI"),
    ]

    for key, service in api_keys:
        if key in config:
            try:
                validator.validate_api_key(config.get(key), service)
            except ConfigurationError as e:
                errors.append(f"{key}: {e}")


def _validate_numeric_ranges(config: dict[str, Any], errors: list[str]) -> None:
    """Validate all numeric range configurations."""
    numeric_validations = [
        ("max_workers", 1, 100),
        ("timeout_seconds", 10, 3600),
        ("cache_ttl", 0, 86400),
        ("max_retries", 0, 10),
    ]

    for key, min_val, max_val in numeric_validations:
        if key in config:
            value = config[key]
            if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                errors.append(
                    f"{key}: Invalid value {value}. Must be between {min_val} and {max_val}"
                )


def _validate_log_level(config: dict[str, Any], errors: list[str]) -> None:
    """Validate log level configuration."""
    if "log_level" in config:
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config["log_level"].upper() not in allowed_levels:
            errors.append(
                f"Invalid log_level: {config['log_level']}. Must be one of {allowed_levels}"
            )


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Validate complete configuration dictionary.

    Args:
        config: Configuration dictionary

    Returns:
        Validated configuration

    Raises:
        ConfigurationError: If any validation fails
    """
    validator = ConfigValidator()
    errors: list[str] = []

    # Run all validation steps
    validation_steps: list[Callable[[dict[str, Any], list[str]], None]] = [
        lambda c, e: _validate_environment(c, e),
        lambda c, e: _validate_paths(c, e, validator),
        lambda c, e: _validate_urls(c, e, validator),
        lambda c, e: _validate_api_keys(c, e, validator),
        lambda c, e: _validate_numeric_ranges(c, e),
        lambda c, e: _validate_log_level(c, e),
    ]

    for step in validation_steps:
        step(config, errors)

    # Check for any errors
    if errors:
        raise ConfigurationError("Configuration validation failed", details={"errors": errors})

    return config


# Memory validation helper functions
def _validate_redis_config(
    memory_config: dict[str, Any], errors: list[str], validator: ConfigValidator
) -> None:
    """Validate Redis configuration."""
    if memory_config.get("redis", {}).get("enabled"):
        redis_url = memory_config["redis"].get("url")
        if redis_url:
            try:
                validator.validate_url(redis_url, "redis")
            except ConfigurationError as e:
                errors.append(f"Redis: {e}")


def _validate_neo4j_config(
    memory_config: dict[str, Any], errors: list[str], validator: ConfigValidator
) -> None:
    """Validate Neo4j configuration."""
    if memory_config.get("neo4j", {}).get("enabled"):
        neo4j_config = memory_config["neo4j"]
        if neo4j_config.get("uri"):
            try:
                validator.validate_url(neo4j_config["uri"], "bolt")
            except ConfigurationError as e:
                errors.append(f"Neo4j: {e}")

        if not neo4j_config.get("user") or not neo4j_config.get("password"):
            errors.append("Neo4j: user and password are required")


def _validate_postgresql_config(
    memory_config: dict[str, Any], errors: list[str], validator: ConfigValidator
) -> None:
    """Validate PostgreSQL configuration."""
    if memory_config.get("postgresql", {}).get("enabled"):
        postgres_dsn = memory_config["postgresql"].get("dsn")
        if postgres_dsn:
            try:
                validator.validate_url(postgres_dsn, "postgresql")
            except ConfigurationError as e:
                errors.append(f"PostgreSQL: {e}")


def _validate_qdrant_config(
    memory_config: dict[str, Any], errors: list[str], validator: ConfigValidator
) -> None:
    """Validate Qdrant configuration."""
    if memory_config.get("qdrant", {}).get("enabled"):
        qdrant_url = memory_config["qdrant"].get("url")
        if qdrant_url:
            try:
                validator.validate_url(qdrant_url, "http")
            except ConfigurationError as e:
                errors.append(f"Qdrant: {e}")


def validate_memory_config(memory_config: dict[str, Any]) -> dict[str, Any]:
    """
    Validate memory system configuration.

    Args:
        memory_config: Memory configuration dictionary

    Returns:
        Validated configuration

    Raises:
        ConfigurationError: If validation fails
    """
    if not memory_config.get("enabled", True):
        return memory_config

    validator = ConfigValidator()
    errors: list[str] = []

    # Run all memory validation steps
    memory_validation_steps = [
        lambda c, e: _validate_redis_config(c, e, validator),
        lambda c, e: _validate_neo4j_config(c, e, validator),
        lambda c, e: _validate_postgresql_config(c, e, validator),
        lambda c, e: _validate_qdrant_config(c, e, validator),
    ]

    for step in memory_validation_steps:
        step(memory_config, errors)

    if errors:
        raise ConfigurationError(
            "Memory configuration validation failed", details={"errors": errors}
        )

    return memory_config


def validate_all_configs(config: Any) -> None:
    """
    Validate all configuration settings for the orchestrator.

    Args:
        config: OrchestratorConfig instance

    Raises:
        ConfigurationError: If any validation fails
    """
    # Get configuration as dictionary
    if hasattr(config, "to_dict"):
        config_dict = config.to_dict()
    elif hasattr(config, "settings"):
        # Handle OrchestratorConfig object
        if hasattr(config.settings, "__dict__"):
            config_dict = config.settings.__dict__.copy()
        else:
            # For Pydantic models
            config_dict = (
                config.settings.dict()
                if hasattr(config.settings, "dict")
                else vars(config.settings)
            )
    else:
        config_dict = config if isinstance(config, dict) else vars(config)

    # Validate main configuration
    validate_config(config_dict)

    # Validate memory configuration if available
    if hasattr(config, "get_memory_config"):
        memory_config = config.get_memory_config()
        validate_memory_config(memory_config)
