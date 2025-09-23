"""Standardized error formats and user-friendly messages."""

import json
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from plc_orchestrator.utils.errors import OrchestratorError


class ErrorCategory(Enum):
    """Categories of errors for better organization."""

    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    ANALYSIS = "analysis"
    MEMORY = "memory"
    NETWORK = "network"
    PERMISSION = "permission"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


class ErrorLevel(Enum):
    """Error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Context information for errors."""

    operation: str
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorResponse:
    """Standardized error response format."""

    # Core fields
    error_id: str
    category: ErrorCategory
    level: ErrorLevel
    message: str
    user_message: str

    # Additional information
    details: dict[str, Any] | None = None
    suggestions: list[str] = field(default_factory=list)
    documentation_url: str | None = None
    context: ErrorContext | None = None

    # Technical details (not shown to end users)
    exception_type: str | None = None
    traceback: str | None = None

    def to_dict(self, include_technical: bool = False) -> dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "error_id": self.error_id,
            "category": self.category.value,
            "level": self.level.value,
            "message": self.message,
            "user_message": self.user_message,
            "timestamp": datetime.now().isoformat(),
        }

        if self.details:
            result["details"] = self.details

        if self.suggestions:
            result["suggestions"] = self.suggestions

        if self.documentation_url:
            result["documentation_url"] = self.documentation_url

        if self.context:
            result["context"] = {
                "operation": self.context.operation,
                "request_id": self.context.request_id,
            }

        if include_technical:
            result["technical"] = {
                "exception_type": self.exception_type,
                "traceback": self.traceback,
            }

        return result

    def to_json(self, include_technical: bool = False) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(include_technical), indent=2)


class ErrorFormatter:
    """Format errors with user-friendly messages."""

    # User-friendly message templates
    USER_MESSAGES = {
        # Configuration errors
        "invalid_environment": "The environment '{env}' is not recognized. Please use: development, staging, production, or test.",
        "missing_api_key": "The {service} API key is required but not provided. Please set {env_var} in your environment.",
        "invalid_url": "The {service} URL is invalid. Please check the format and try again.",
        "connection_failed": "Could not connect to {service}. Please verify the service is running and accessible.",
        # Validation errors
        "invalid_code": "The provided code has syntax errors. Please check line {line} for issues.",
        "missing_requirements": "The implementation is missing {count} required features. See details below.",
        "security_issue": "Security vulnerability detected: {issue}. Please review and fix before proceeding.",
        # Analysis errors
        "task_too_long": "The task description is too long ({length} characters). Please keep it under {max_length} characters.",
        "task_too_vague": "The task description is too vague. Please provide more specific requirements.",
        "unsupported_language": "The language '{language}' is not currently supported. Supported languages: {supported}.",
        # Memory errors
        "memory_unavailable": "The memory system is temporarily unavailable. The operation will continue without historical insights.",
        "memory_quota_exceeded": "Memory storage quota exceeded. Please clean up old data or upgrade your plan.",
        # Resource errors
        "timeout": "The operation took too long and was cancelled after {timeout} seconds.",
        "rate_limit": "Rate limit exceeded. Please wait {retry_after} seconds before trying again.",
        "insufficient_resources": "Insufficient resources to complete the operation. Try reducing the workload.",
        # Generic fallback
        "unknown_error": "An unexpected error occurred. Please try again or contact support if the issue persists.",
    }

    # Suggestion templates
    SUGGESTIONS = {
        "invalid_environment": [
            "Check your .env file or environment variables",
            "Use 'development' for local development",
            "Use 'production' for production deployments",
        ],
        "missing_api_key": [
            "Add {env_var}=your_key to your .env file",
            "Get an API key from {service_url}",
            "Use 'enable_{feature}=false' to disable this feature",
        ],
        "invalid_code": [
            "Check for missing colons, parentheses, or quotes",
            "Ensure proper indentation (4 spaces)",
            "Run a linter to identify syntax issues",
        ],
        "connection_failed": [
            "Verify {service} is running: {check_command}",
            "Check your firewall settings",
            "Ensure the connection URL is correct",
        ],
        "timeout": [
            "Break the task into smaller parts",
            "Increase the timeout setting",
            "Check for infinite loops or blocking operations",
        ],
    }

    # Documentation URLs
    DOC_URLS = {
        "configuration": "https://docs.example.com/configuration",
        "validation": "https://docs.example.com/validation",
        "memory": "https://docs.example.com/memory-system",
        "api_keys": "https://docs.example.com/api-keys",
    }

    @classmethod
    def format_error(
        cls,
        exception: Exception,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: ErrorContext | None = None,
        include_technical: bool = False,
    ) -> ErrorResponse:
        """
        Format an exception into a standardized error response.

        Args:
            exception: The exception to format
            category: Error category
            context: Additional context
            include_technical: Include technical details

        Returns:
            Formatted error response
        """
        # Generate error ID
        error_id = cls._generate_error_id(exception, context)

        # Determine level
        level = cls._determine_level(exception)

        # Get messages
        message = str(exception)
        user_message = cls._get_user_message(exception, message)

        # Get suggestions
        suggestions = cls._get_suggestions(exception)

        # Get documentation URL
        doc_url = cls._get_documentation_url(exception, category)

        # Extract details
        details = cls._extract_details(exception)

        # Create response
        response = ErrorResponse(
            error_id=error_id,
            category=category,
            level=level,
            message=message,
            user_message=user_message,
            details=details,
            suggestions=suggestions,
            documentation_url=doc_url,
            context=context,
        )

        # Add technical details if requested
        if include_technical:
            response.exception_type = type(exception).__name__
            response.traceback = traceback.format_exc()

        return response

    @classmethod
    def _generate_error_id(cls, exception: Exception, context: ErrorContext | None) -> str:
        """Generate unique error ID."""
        import hashlib

        # Use exception type and message for ID
        content = f"{type(exception).__name__}:{str(exception)}"
        if context and context.request_id:
            content += f":{context.request_id}"

        # Generate short hash
        return hashlib.md5(content.encode()).hexdigest()[:8].upper()

    @classmethod
    def _determine_level(cls, exception: Exception) -> ErrorLevel:
        """Determine error severity level."""
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return ErrorLevel.ERROR
        elif isinstance(exception, (ValueError, TypeError)):
            return ErrorLevel.WARNING
        elif isinstance(exception, OrchestratorError):
            # Check for critical errors
            if "critical" in str(exception).lower():
                return ErrorLevel.CRITICAL
            return ErrorLevel.ERROR
        else:
            return ErrorLevel.ERROR

    @classmethod
    def _get_user_message(cls, exception: Exception, default: str) -> str:
        """Get user-friendly message for exception."""
        exception_type = type(exception).__name__

        # Map common exceptions to templates
        if isinstance(exception, ConnectionError):
            service = cls._extract_service_name(str(exception))
            return cls.USER_MESSAGES["connection_failed"].format(service=service)

        elif isinstance(exception, TimeoutError):
            timeout = cls._extract_timeout(str(exception))
            return cls.USER_MESSAGES["timeout"].format(timeout=timeout or "30")

        elif isinstance(exception, ValueError):
            # Check for specific patterns
            if "environment" in str(exception).lower():
                env = cls._extract_environment(str(exception))
                return cls.USER_MESSAGES["invalid_environment"].format(env=env or "unknown")
            elif "api key" in str(exception).lower():
                service = cls._extract_service_name(str(exception))
                env_var = f"{service.upper()}_API_KEY"
                return cls.USER_MESSAGES["missing_api_key"].format(service=service, env_var=env_var)

        # Default to cleaned version of original message
        return cls._clean_technical_message(default)

    @classmethod
    def _get_suggestions(cls, exception: Exception) -> list[str]:
        """Get relevant suggestions for the error."""
        suggestions = []

        if isinstance(exception, ConnectionError):
            service = cls._extract_service_name(str(exception))
            check_cmd = cls._get_check_command(service)
            suggestions = [
                s.format(service=service, check_command=check_cmd)
                for s in cls.SUGGESTIONS["connection_failed"]
            ]

        elif isinstance(exception, TimeoutError):
            suggestions = cls.SUGGESTIONS["timeout"]

        elif "environment" in str(exception).lower():
            suggestions = cls.SUGGESTIONS["invalid_environment"]

        elif "api key" in str(exception).lower():
            service = cls._extract_service_name(str(exception))
            env_var = f"{service.upper()}_API_KEY"
            service_url = cls._get_service_url(service)
            suggestions = [
                s.format(env_var=env_var, service_url=service_url, feature=service.lower())
                for s in cls.SUGGESTIONS["missing_api_key"]
            ]

        return suggestions

    @classmethod
    def _get_documentation_url(cls, exception: Exception, category: ErrorCategory) -> str | None:
        """Get relevant documentation URL."""
        # Check specific error types
        if "api key" in str(exception).lower():
            return cls.DOC_URLS.get("api_keys")

        # Fall back to category
        return cls.DOC_URLS.get(category.value)

    @classmethod
    def _extract_details(cls, exception: Exception) -> dict[str, Any] | None:
        """Extract additional details from exception."""
        details = {}

        # Extract details from OrchestratorError
        if isinstance(exception, OrchestratorError) and hasattr(exception, "details"):
            details.update(exception.details or {})

        # Extract common patterns
        if isinstance(exception, ConnectionError):
            details["service"] = cls._extract_service_name(str(exception))
            details["connection_type"] = "network"

        elif isinstance(exception, TimeoutError):
            details["timeout_seconds"] = cls._extract_timeout(str(exception))
            details["operation_type"] = "async"

        return details if details else None

    # Utility methods
    @staticmethod
    def _extract_service_name(error_message: str) -> str:
        """Extract service name from error message."""
        services = ["redis", "neo4j", "postgresql", "qdrant", "wolframalpha"]
        for service in services:
            if service.lower() in error_message.lower():
                return service.title()
        return "service"

    @staticmethod
    def _extract_environment(error_message: str) -> str | None:
        """Extract environment name from error message."""
        import re

        match = re.search(r"environment[:\s]+(['\"]?)(\w+)\1", error_message, re.I)
        return match.group(2) if match else None

    @staticmethod
    def _extract_timeout(error_message: str) -> int | None:
        """Extract timeout value from error message."""
        import re

        match = re.search(r"(\d+)\s*seconds?", error_message)
        return int(match.group(1)) if match else None

    @staticmethod
    def _get_check_command(service: str) -> str:
        """Get service check command."""
        commands = {
            "Redis": "redis-cli ping",
            "Neo4j": "cypher-shell 'RETURN 1'",
            "PostgreSQL": "psql -c 'SELECT 1'",
            "Qdrant": "curl http://localhost:6333/health",
        }
        return commands.get(service, f"{service.lower()} --version")

    @staticmethod
    def _get_service_url(service: str) -> str:
        """Get service documentation URL."""
        urls = {
            "wolframalpha": "https://products.wolframalpha.com/api/",
            "openai": "https://platform.openai.com/api-keys",
        }
        return urls.get(service.lower(), f"https://{service.lower()}.com")

    @staticmethod
    def _clean_technical_message(message: str) -> str:
        """Clean technical jargon from error message."""
        # Remove file paths
        import re

        message = re.sub(r"[/\\][\w/\\.-]+\.(py|js|ts)", "file", message)

        # Remove memory addresses
        message = re.sub(r"0x[0-9a-fA-F]+", "", message)

        # Remove stack trace indicators
        message = re.sub(r'File ".+", line \d+', "", message)

        # Simplify common technical terms
        replacements = {
            "NoneType": "missing value",
            "KeyError": "missing data",
            "AttributeError": "configuration error",
            "ImportError": "missing dependency",
        }

        for tech, simple in replacements.items():
            message = message.replace(tech, simple)

        return message.strip()


# Convenience function
def format_user_error(
    exception: Exception, operation: str = "unknown", include_suggestions: bool = True
) -> str:
    """
    Format an exception for end-user display.

    Args:
        exception: The exception to format
        operation: What operation was being performed
        include_suggestions: Whether to include suggestions

    Returns:
        User-friendly error message
    """
    context = ErrorContext(operation=operation)
    response = ErrorFormatter.format_error(exception, context=context, include_technical=False)

    # Build message
    parts = [response.user_message]

    if include_suggestions and response.suggestions:
        parts.append("\n\nSuggestions:")
        for i, suggestion in enumerate(response.suggestions, 1):
            parts.append(f"  {i}. {suggestion}")

    if response.documentation_url:
        parts.append(f"\n\nFor more help, see: {response.documentation_url}")

    return "\n".join(parts)
