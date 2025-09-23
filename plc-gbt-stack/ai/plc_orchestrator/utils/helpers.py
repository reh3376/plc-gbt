"""Helper utilities for the PLC Task Orchestrator."""

import hashlib
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any


def generate_task_id() -> str:
    """
    Generate a unique task ID.

    Returns:
        Unique task ID in format 'task_<timestamp>_<hash>'
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_hash = hashlib.md5(f"{timestamp}_{time.time()}".encode()).hexdigest()[:8]
    return f"task_{timestamp}_{unique_hash}"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "2h 15m 30s"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def extract_keywords(text: str, min_length: int = 3) -> list[str]:
    """
    Extract keywords from text for search and indexing.

    Args:
        text: Input text
        min_length: Minimum keyword length

    Returns:
        List of unique keywords
    """
    # Common stop words to filter out
    stop_words = {
        "the",
        "is",
        "at",
        "which",
        "on",
        "a",
        "an",
        "as",
        "are",
        "was",
        "were",
        "been",
        "be",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "them",
        "their",
        "what",
        "who",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "every",
        "some",
        "any",
        "many",
        "much",
        "few",
        "more",
        "most",
        "less",
        "least",
        "to",
        "from",
        "with",
        "without",
        "for",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "between",
        "under",
        "over",
    }

    # Extract words
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())

    # Filter and deduplicate
    keywords = []
    seen = set()

    for word in words:
        if word not in seen and word not in stop_words and len(word) >= min_length:
            keywords.append(word)
            seen.add(word)

    return keywords


def safe_file_path(base_path: Path, filename: str) -> Path:
    """
    Create a safe file path, preventing directory traversal.

    Args:
        base_path: Base directory path
        filename: Requested filename

    Returns:
        Safe resolved path

    Raises:
        ValueError: If path would escape base directory
    """
    base_path = Path(base_path).resolve()
    requested_path = (base_path / filename).resolve()

    # Ensure the resolved path is within base_path
    if not str(requested_path).startswith(str(base_path)):
        raise ValueError(f"Path traversal attempt detected: {filename}")

    return requested_path


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def merge_dicts(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        update: Dictionary with updates

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def sanitize_code(code: str) -> str:
    """
    Basic code sanitization for validation.

    Args:
        code: Code to sanitize

    Returns:
        Sanitized code
    """
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r"__import__",
        r"exec\s*\(",
        r"eval\s*\(",
        r"compile\s*\(",
        r"globals\s*\(",
        r"locals\s*\(",
        r"vars\s*\(",
        r"open\s*\(",
    ]

    sanitized = code
    for pattern in dangerous_patterns:
        if re.search(pattern, sanitized):
            # Log warning about dangerous pattern
            sanitized = re.sub(pattern, f"# SANITIZED: {pattern}", sanitized)

    return sanitized


def calculate_complexity_score(
    lines_of_code: int, num_files: int, num_dependencies: int, has_tests: bool = False
) -> str:
    """
    Calculate task complexity based on metrics.

    Args:
        lines_of_code: Estimated lines of code
        num_files: Number of files to modify
        num_dependencies: Number of external dependencies
        has_tests: Whether tests are required

    Returns:
        Complexity level (simple, moderate, complex, extensive)
    """
    # Define scoring thresholds
    loc_thresholds = [(100, 1), (500, 2), (1500, 3), (float("inf"), 4)]
    file_thresholds = [(1, 0), (3, 1), (10, 2), (float("inf"), 3)]
    dep_thresholds = [(0, 0), (3, 1), (10, 2), (float("inf"), 3)]

    # Calculate scores using threshold functions
    score = (
        _calculate_threshold_score(lines_of_code, loc_thresholds)
        + _calculate_threshold_score(num_files, file_thresholds)
        + _calculate_threshold_score(num_dependencies, dep_thresholds)
        + (1 if has_tests else 0)
    )

    # Map total score to complexity
    complexity_map = [(3, "simple"), (6, "moderate"), (9, "complex"), (float("inf"), "extensive")]

    return _calculate_threshold_score(score, complexity_map)


def _calculate_threshold_score(
    value: int | float, thresholds: list[tuple[int | float, Any]]
) -> Any:
    """Helper function to calculate score based on thresholds."""
    for threshold, result in thresholds:
        if value <= threshold:
            return result
    return thresholds[-1][1]  # Return last score if no threshold matched


def is_valid_python_identifier(name: str) -> bool:
    """
    Check if a string is a valid Python identifier.

    Args:
        name: String to check

    Returns:
        True if valid identifier
    """
    return name.isidentifier()


def get_file_extension(language: str) -> str:
    """
    Get file extension for a programming language.

    Args:
        language: Programming language name

    Returns:
        File extension with dot
    """
    extensions = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "cpp": ".cpp",
        "c": ".c",
        "go": ".go",
        "rust": ".rs",
        "ruby": ".rb",
        "php": ".php",
        "swift": ".swift",
        "kotlin": ".kt",
        "scala": ".scala",
        "r": ".r",
        "julia": ".jl",
        "matlab": ".m",
        "bash": ".sh",
        "powershell": ".ps1",
        "yaml": ".yml",
        "json": ".json",
        "xml": ".xml",
        "html": ".html",
        "css": ".css",
        "markdown": ".md",
        "sql": ".sql",
    }

    return extensions.get(language.lower(), ".txt")
