"""Configuration settings for the PLC Task Orchestrator."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    from pydantic import BaseSettings, Field, validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback to dataclass if Pydantic not available
    BaseSettings = object  # type: ignore


# Pydantic-based configuration (preferred)
if PYDANTIC_AVAILABLE:

    class Settings(BaseSettings):
        """Application settings with environment variable support."""

        # Application
        app_name: str = Field("PLC Task Orchestrator", env="APP_NAME")
        environment: str = Field("development", env="ENVIRONMENT")
        debug: bool = Field(False, env="DEBUG")
        version: str = Field("2.0.0", env="VERSION")

        # Paths
        project_root: Path | None = Field(None, env="PROJECT_ROOT")
        context_dir: Path = Field(Path("context"), env="CONTEXT_DIR")
        guides_dir: Path = Field(Path("guides"), env="GUIDES_DIR")
        summaries_dir: Path = Field(Path("summaries"), env="SUMMARIES_DIR")

        # Memory System
        enable_memory: bool = Field(True, env="ENABLE_MEMORY")
        redis_url: str | None = Field(None, env="REDIS_URL")
        neo4j_uri: str | None = Field(None, env="NEO4J_URI")
        neo4j_user: str | None = Field(None, env="NEO4J_USER")
        neo4j_password: str | None = Field(None, env="NEO4J_PASSWORD")
        postgres_dsn: str | None = Field(None, env="POSTGRES_DSN")
        qdrant_url: str | None = Field(None, env="QDRANT_URL")

        # Features
        enable_math_validation: bool = Field(True, env="ENABLE_MATH_VALIDATION")
        enable_production_checks: bool = Field(False, env="ENABLE_PRODUCTION_CHECKS")
        enable_control_analysis: bool = Field(True, env="ENABLE_CONTROL_ANALYSIS")
        enable_llm_integration: bool = Field(False, env="ENABLE_LLM_INTEGRATION")

        # Performance
        max_workers: int = Field(4, env="MAX_WORKERS", ge=1, le=100)
        timeout_seconds: int = Field(300, env="TIMEOUT_SECONDS", ge=10)
        cache_ttl: int = Field(3600, env="CACHE_TTL", ge=0)
        max_retries: int = Field(3, env="MAX_RETRIES", ge=0, le=10)

        # Logging
        log_level: str = Field("INFO", env="LOG_LEVEL")
        use_structlog: bool = Field(True, env="USE_STRUCTLOG")
        log_file: Path | None = Field(None, env="LOG_FILE")

        # API Keys (for enhanced features)
        wolfram_alpha_api_key: str | None = Field(None, env="WOLFRAM_ALPHA_API_KEY")
        openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")

        @validator("environment")
        def validate_environment(cls, v: str) -> str:
            """Validate environment value."""
            allowed = ["development", "staging", "production", "test"]
            if v not in allowed:
                raise ValueError(f"environment must be one of {allowed}")
            return v

        @validator("log_level")
        def validate_log_level(cls, v: str) -> str:
            """Validate log level."""
            allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            v_upper = v.upper()
            if v_upper not in allowed:
                raise ValueError(f"log_level must be one of {allowed}")
            return v_upper

        @validator("project_root", pre=True, always=True)
        def set_project_root(cls, v: Path | None) -> Path:
            """Set project root if not provided."""
            if v is None:
                # Try to auto-detect project root
                current = Path.cwd()
                while current != current.parent:
                    if (current / ".git").exists() or (current / "pyproject.toml").exists():
                        return current
                    current = current.parent
                return Path.cwd()
            return Path(v)

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False

else:
    # Fallback dataclass-based configuration
    @dataclass
    class Settings:
        """Application settings (fallback without Pydantic)."""

        # Application
        app_name: str = "PLC Task Orchestrator"
        environment: str = "development"
        debug: bool = False
        version: str = "2.0.0"

        # Paths
        project_root: Path | None = None
        context_dir: Path = Path("context")
        guides_dir: Path = Path("guides")
        summaries_dir: Path = Path("summaries")

        # Memory System
        enable_memory: bool = True
        redis_url: str | None = None
        neo4j_uri: str | None = None
        neo4j_user: str | None = None
        neo4j_password: str | None = None
        postgres_dsn: str | None = None
        qdrant_url: str | None = None

        # Features
        enable_math_validation: bool = True
        enable_production_checks: bool = False
        enable_control_analysis: bool = True
        enable_llm_integration: bool = False

        # Performance
        max_workers: int = 4
        timeout_seconds: int = 300
        cache_ttl: int = 3600
        max_retries: int = 3

        # Logging
        log_level: str = "INFO"
        use_structlog: bool = True
        log_file: Path | None = None

        # API Keys
        wolfram_alpha_api_key: str | None = None
        openai_api_key: str | None = None

        def __post_init__(self) -> None:
            """Post-initialization validation and setup."""
            # Set project root if not provided
            if self.project_root is None:
                current = Path.cwd()
                while current != current.parent:
                    if (current / ".git").exists() or (current / "pyproject.toml").exists():
                        self.project_root = current
                        break
                    current = current.parent
                else:
                    self.project_root = Path.cwd()

            # Load from environment variables
            self._load_from_env()

        def _load_from_env(self) -> None:
            """Load settings from environment variables."""
            for field_name in self.__dataclass_fields__:
                env_name = field_name.upper()
                if env_name in os.environ:
                    value = os.environ[env_name]
                    # Convert to appropriate type
                    field_type = self.__dataclass_fields__[field_name].type
                    if field_type == bool:
                        value = value.lower() in ("true", "1", "yes")
                    elif field_type == int:
                        value = int(value)
                    elif field_type in (Path, Optional[Path]):
                        value = Path(value) if value else None
                    setattr(self, field_name, value)


class OrchestratorConfig:
    """Main configuration class for the orchestrator."""

    def __init__(self, config_file: str | None = None, **overrides: Any) -> None:
        """
        Initialize configuration.

        Args:
            config_file: Optional path to configuration file
            **overrides: Keyword arguments to override settings
        """
        # Load settings
        if PYDANTIC_AVAILABLE:
            if config_file:
                self.settings = Settings(_env_file=config_file)
            else:
                self.settings = Settings()
        else:
            self.settings = Settings()

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)

        # Create derived attributes
        self._setup_paths()
        self._setup_features()

    def _setup_paths(self) -> None:
        """Setup and validate paths."""
        if self.settings.project_root:
            # Make paths absolute relative to project root
            self.settings.context_dir = self.settings.project_root / self.settings.context_dir
            self.settings.guides_dir = self.settings.project_root / self.settings.guides_dir
            self.settings.summaries_dir = self.settings.project_root / self.settings.summaries_dir

            # Create directories if they don't exist
            for dir_path in [
                self.settings.context_dir,
                self.settings.guides_dir,
                self.settings.summaries_dir,
            ]:
                dir_path.mkdir(parents=True, exist_ok=True)

    def _setup_features(self) -> None:
        """Setup feature flags based on environment."""
        # Enable production checks in production environment
        if self.settings.environment == "production":
            self.settings.enable_production_checks = True

        # Disable debug in production
        if self.settings.environment == "production":
            self.settings.debug = False

    def get_memory_config(self) -> dict[str, Any]:
        """Get memory system configuration."""
        return {
            "enabled": self.settings.enable_memory,
            "redis": {
                "url": self.settings.redis_url or "redis://localhost:6379",
                "enabled": bool(self.settings.redis_url),
            },
            "neo4j": {
                "uri": self.settings.neo4j_uri or "bolt://localhost:7687",
                "user": self.settings.neo4j_user or "neo4j",
                "password": self.settings.neo4j_password or "password",
                "enabled": bool(self.settings.neo4j_uri),
            },
            "postgresql": {
                "dsn": self.settings.postgres_dsn,
                "enabled": bool(self.settings.postgres_dsn),
            },
            "qdrant": {
                "url": self.settings.qdrant_url or "http://localhost:6333",
                "enabled": bool(self.settings.qdrant_url),
            },
        }

    def get_logging_config(self) -> dict[str, Any]:
        """Get logging configuration."""
        return {
            "level": self.settings.log_level,
            "use_structlog": self.settings.use_structlog,
            "log_file": self.settings.log_file,
            "environment": self.settings.environment,
            "version": self.settings.version,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        if hasattr(self.settings, "dict"):
            return self.settings.dict()
        else:
            # Fallback for dataclass
            from dataclasses import asdict

            return asdict(self.settings)
