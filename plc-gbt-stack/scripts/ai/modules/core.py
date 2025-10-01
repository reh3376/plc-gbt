"""
Core Infrastructure Module
==========================

Base infrastructure components for the PLC-GPT system including:
- Database connections (PostgreSQL, Redis)
- Logging configuration
- Configuration management
- Base orchestrator patterns
- Common utilities

This module eliminates code duplication across the codebase.
"""

import json
import logging
import os
import sys
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# Database imports
try:
    import psycopg2
    import redis
    from psycopg2.extras import RealDictCursor
    DATABASE_LIBRARIES_AVAILABLE = True
except ImportError:
    DATABASE_LIBRARIES_AVAILABLE = False
    if TYPE_CHECKING:
        import redis  # For type hints only

@dataclass
class TaskAnalysis:
    """Standard task analysis structure for AI Task Orchestrator"""
    task_id: str
    complexity: str  # simple, moderate, complex
    estimated_time: str
    estimated_lines: int
    requirements: list[str]
    risks: list[str]
    dependencies: list[str]
    success_criteria: list[str]

class LoggingManager:
    """Centralized logging configuration"""

    @staticmethod
    def setup_logging(
        level: str = "INFO",
        log_file: str | None = None,
        format_string: str | None = None
    ) -> logging.Logger:
        """
        Setup standardized logging configuration

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
            format_string: Custom format string

        Returns:
            Configured logger instance
        """
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format=format_string,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )

        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(logging.Formatter(format_string))
            logging.getLogger().addHandler(file_handler)

        return logging.getLogger()

class ConfigurationManager:
    """Centralized configuration management"""

    def __init__(self, config_file: str | None = None):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file or environment"""
        config = {
            # Database configuration
            "database": {
                "postgresql": {
                    "host": os.getenv("POSTGRES_HOST", "localhost"),
                    "port": int(os.getenv("POSTGRES_PORT", "5432")),
                    "database": os.getenv("POSTGRES_DB", "plc_metadata"),
                    "user": os.getenv("POSTGRES_USER", "plc_user"),
                    "password": os.getenv("POSTGRES_PASSWORD", "plc_password")
                },
                "redis": {
                    "host": os.getenv("REDIS_HOST", "localhost"),
                    "port": int(os.getenv("REDIS_PORT", "6379")),
                    "db": int(os.getenv("REDIS_DB", "0"))
                }
            },

            # AI configuration
            "ai": {
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "fine_tuned_model": os.getenv("FINE_TUNED_MODEL_ID"),
                "wolfram_api_key": os.getenv("WOLFRAM_API_KEY")
            },

            # Performance thresholds
            "performance": {
                "default_mae_ranges": {"excellent": 0.5, "good": 1.5, "acceptable": 3.0},
                "default_mse_ranges": {"excellent": 1.0, "good": 5.0, "acceptable": 15.0},
                "default_oscillation_ranges": {"excellent": 5.0, "good": 15.0, "acceptable": 30.0}
            },

            # System configuration
            "system": {
                "max_concurrent_tasks": int(os.getenv("MAX_CONCURRENT_TASKS", "10")),
                "default_timeout": int(os.getenv("DEFAULT_TIMEOUT", "300")),
                "results_directory": os.getenv("RESULTS_DIR", "results")
            }
        }

        # Load from file if specified
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file) as f:
                file_config = json.load(f)
                config.update(file_config)

        return config

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'database.postgresql.host')"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

class DatabaseManager:
    """Centralized database connection management"""

    def __init__(self, config: ConfigurationManager):
        self.config = config
        self._postgres_conn = None
        self._redis_client = None
        self.logger = logging.getLogger(__name__)

    def get_postgres_connection(self) -> Optional["psycopg2.extensions.connection"]:
        """Get PostgreSQL connection with retry logic"""
        if not DATABASE_LIBRARIES_AVAILABLE:
            self.logger.warning("Database libraries not available")
            return None

        if self._postgres_conn is None or self._postgres_conn.closed:
            try:
                pg_config = self.config.get("database.postgresql")
                self._postgres_conn = psycopg2.connect(
                    host=pg_config["host"],
                    port=pg_config["port"],
                    database=pg_config["database"],
                    user=pg_config["user"],
                    password=pg_config["password"],
                    cursor_factory=RealDictCursor
                )
                self.logger.info("PostgreSQL connection established")
            except Exception as e:
                self.logger.error(f"Failed to connect to PostgreSQL: {e}")
                return None

        return self._postgres_conn

    def get_redis_client(self) -> Optional["redis.Redis"]:
        """Get Redis client with retry logic"""
        if not DATABASE_LIBRARIES_AVAILABLE:
            self.logger.warning("Database libraries not available")
            return None

        if self._redis_client is None:
            try:
                redis_config = self.config.get("database.redis")
                self._redis_client = redis.Redis(
                    host=redis_config["host"],
                    port=redis_config["port"],
                    db=redis_config["db"],
                    decode_responses=True
                )
                # Test connection
                self._redis_client.ping()
                self.logger.info("Redis connection established")
            except Exception as e:
                self.logger.error(f"Failed to connect to Redis: {e}")
                return None

        return self._redis_client

    def execute_postgres_query(self, query: str, params: tuple | None = None) -> list[dict] | None:
        """Execute PostgreSQL query with error handling"""
        conn = self.get_postgres_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall()
                conn.commit()
                return []
        except Exception as e:
            self.logger.error(f"PostgreSQL query failed: {e}")
            conn.rollback()
            return None

    def set_redis_value(self, key: str, value: str | dict, expiry: int | None = None) -> bool:
        """Set Redis value with error handling"""
        client = self.get_redis_client()
        if not client:
            return False

        try:
            if isinstance(value, dict):
                value = json.dumps(value)

            result = client.set(key, value, ex=expiry)
            return result
        except Exception as e:
            self.logger.error(f"Redis set failed: {e}")
            return False

    def get_redis_value(self, key: str, as_json: bool = False) -> str | dict | None:
        """Get Redis value with error handling"""
        client = self.get_redis_client()
        if not client:
            return None

        try:
            value = client.get(key)
            if value and as_json:
                return json.loads(value)
            return value
        except Exception as e:
            self.logger.error(f"Redis get failed: {e}")
            return None

    def close_connections(self):
        """Close all database connections"""
        if self._postgres_conn and not self._postgres_conn.closed:
            self._postgres_conn.close()
            self.logger.info("PostgreSQL connection closed")

        if self._redis_client:
            self._redis_client.close()
            self.logger.info("Redis connection closed")

class BaseOrchestrator(ABC):
    """
    Base class for AI Task Orchestrator implementations

    Provides common functionality for all orchestrators:
    - Task analysis and complexity assessment
    - Standardized logging and configuration
    - Database connection management
    - Results collection and reporting
    - Error handling patterns
    """

    def __init__(self, task_id: str, config_file: str | None = None):
        self.task_id = task_id
        self.session_id = f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()

        # Initialize core components
        self.config = ConfigurationManager(config_file)
        self.logger = LoggingManager.setup_logging()
        self.db_manager = DatabaseManager(self.config)

        # Task tracking
        self.task_analysis = self._analyze_task()
        self.results = {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "task_analysis": asdict(self.task_analysis),
            "execution_log": [],
            "errors": [],
            "performance_metrics": {}
        }

        self.logger.info(f"🚀 {self.__class__.__name__} initialized")
        self.logger.info(f"📋 Task: {self.task_id}")
        self.logger.info(f"🔍 Complexity: {self.task_analysis.complexity}")
        self.logger.info(f"⏱️ Estimated Time: {self.task_analysis.estimated_time}")

    @abstractmethod
    def _analyze_task(self) -> TaskAnalysis:
        """Implement task analysis following AI Task Orchestrator methodology"""
        pass

    @abstractmethod
    def execute(self) -> dict[str, Any]:
        """Execute the main task logic"""
        pass

    def log_execution_step(self, step: str, status: str, details: dict | None = None):
        """Log execution step with standardized format"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "status": status,  # started, completed, failed
            "details": details or {}
        }

        self.results["execution_log"].append(log_entry)
        self.logger.info(f"📋 {step}: {status}")

        if details:
            for key, value in details.items():
                self.logger.info(f"   {key}: {value}")

    def log_error(self, error: str, exception: Exception | None = None):
        """Log error with standardized format"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "exception": str(exception) if exception else None
        }

        self.results["errors"].append(error_entry)
        self.logger.error(f"❌ {error}")

        if exception:
            self.logger.error(f"   Exception: {exception}")

    def add_performance_metric(self, metric_name: str, value: float | int | str):
        """Add performance metric to results"""
        self.results["performance_metrics"][metric_name] = value
        self.logger.info(f"📊 {metric_name}: {value}")

    def save_results(self, results_dir: str | None = None) -> str:
        """Save execution results to file"""
        if results_dir is None:
            results_dir = self.config.get("system.results_directory", "results")

        results_path = Path(results_dir) / f"{self.session_id}_results.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)

        # Add completion information
        self.results["end_time"] = datetime.now().isoformat()
        self.results["execution_duration"] = (datetime.now() - self.start_time).total_seconds()

        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        self.logger.info(f"📁 Results saved: {results_path}")
        return str(results_path)

    def validate_requirements(self) -> bool:
        """Validate that all requirements are met before execution"""
        self.log_execution_step("Requirements Validation", "started")

        # Check database connections if needed
        if "database" in self.task_analysis.dependencies:
            if not self.db_manager.get_postgres_connection():
                self.log_error("PostgreSQL connection required but not available")
                return False

            if not self.db_manager.get_redis_client():
                self.log_error("Redis connection required but not available")
                return False

        # Check AI services if needed
        if "ai_services" in self.task_analysis.dependencies:
            if not self.config.get("ai.openai_api_key"):
                self.log_error("OpenAI API key required but not configured")
                return False

        self.log_execution_step("Requirements Validation", "completed")
        return True

    def cleanup(self):
        """Cleanup resources after execution"""
        self.db_manager.close_connections()
        self.logger.info("🧹 Cleanup completed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        if exc_type is not None:
            self.log_error(f"Execution failed: {exc_val}", exc_val)

        self.cleanup()

        if exc_type is None:
            self.logger.info("✅ Orchestrator execution completed successfully")
        else:
            self.logger.error("❌ Orchestrator execution failed")

# Utility functions
def generate_session_id(prefix: str = "session") -> str:
    """Generate unique session ID"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}"

def create_results_directory(base_dir: str, task_name: str) -> Path:
    """Create timestamped results directory"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = Path(base_dir) / task_name / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"
