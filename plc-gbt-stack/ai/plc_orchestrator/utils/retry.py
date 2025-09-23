"""Retry mechanisms and decorators for the orchestrator."""

import asyncio
import functools
import logging
import random
import time
from collections.abc import Callable
from typing import Any, TypeVar

from plc_orchestrator.utils.errors import OrchestratorError

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Retryable exceptions
RETRYABLE_EXCEPTIONS: tuple[type[Exception], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
    asyncio.TimeoutError,
)


class RetryError(OrchestratorError):
    """Raised when all retry attempts fail."""

    def __init__(self, message: str, last_exception: Exception | None = None):
        super().__init__(message)
        self.last_exception = last_exception


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple[type[Exception], ...] | None = None,
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Add randomness to delays to prevent thundering herd
            retryable_exceptions: Tuple of exceptions to retry
        """
        self.max_attempts = max(1, max_attempts)
        self.initial_delay = max(0, initial_delay)
        self.max_delay = max(self.initial_delay, max_delay)
        self.exponential_base = max(1.0, exponential_base)
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or RETRYABLE_EXCEPTIONS

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        # Exponential backoff
        delay = min(self.initial_delay * (self.exponential_base ** (attempt - 1)), self.max_delay)

        # Add jitter if enabled
        if self.jitter:
            delay *= 0.5 + random.random()

        return delay


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] | None = None,
    on_retry: Callable[[Exception, int], None] | None = None,
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Add randomness to delays
        retryable_exceptions: Exceptions to retry
        on_retry: Callback function called on each retry

    Returns:
        Decorated function with retry logic
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            return _retry_sync(func, config, on_retry, *args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            return await _retry_async(func, config, on_retry, *args, **kwargs)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _retry_sync(
    func: Callable[..., T],
    config: RetryConfig,
    on_retry: Callable[[Exception, int], None] | None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute synchronous function with retry logic."""
    last_exception: Exception | None = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            return func(*args, **kwargs)

        except config.retryable_exceptions as e:
            last_exception = e

            if attempt == config.max_attempts:
                # Last attempt failed
                logger.error(
                    f"All {config.max_attempts} retry attempts failed for {func.__name__}: {e}"
                )
                raise RetryError(
                    f"Operation failed after {config.max_attempts} attempts", last_exception=e
                )

            # Calculate delay
            delay = config.calculate_delay(attempt)

            logger.warning(
                f"Retry {attempt}/{config.max_attempts} for {func.__name__} "
                f"after {delay:.1f}s due to: {e}"
            )

            # Call retry callback if provided
            if on_retry:
                try:
                    on_retry(e, attempt)
                except Exception as callback_error:
                    logger.error(f"Error in retry callback: {callback_error}")

            # Wait before retry
            time.sleep(delay)

    # Should never reach here
    raise RetryError(f"Unexpected retry failure for {func.__name__}", last_exception=last_exception)


async def _retry_async(
    func: Callable[..., T],
    config: RetryConfig,
    on_retry: Callable[[Exception, int], None] | None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute asynchronous function with retry logic."""
    last_exception: Exception | None = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            return await func(*args, **kwargs)

        except config.retryable_exceptions as e:
            last_exception = e

            if attempt == config.max_attempts:
                # Last attempt failed
                logger.error(
                    f"All {config.max_attempts} retry attempts failed for {func.__name__}: {e}"
                )
                raise RetryError(
                    f"Operation failed after {config.max_attempts} attempts", last_exception=e
                )

            # Calculate delay
            delay = config.calculate_delay(attempt)

            logger.warning(
                f"Retry {attempt}/{config.max_attempts} for {func.__name__} "
                f"after {delay:.1f}s due to: {e}"
            )

            # Call retry callback if provided
            if on_retry:
                try:
                    if asyncio.iscoroutinefunction(on_retry):
                        await on_retry(e, attempt)
                    else:
                        on_retry(e, attempt)
                except Exception as callback_error:
                    logger.error(f"Error in retry callback: {callback_error}")

            # Wait before retry
            await asyncio.sleep(delay)

    # Should never reach here
    raise RetryError(f"Unexpected retry failure for {func.__name__}", last_exception=last_exception)


class RetryContext:
    """Context manager for retry operations."""

    def __init__(self, config: RetryConfig | None = None):
        """Initialize retry context."""
        self.config = config or RetryConfig()
        self.attempts = 0
        self.last_exception: Exception | None = None

    def __enter__(self):
        """Enter retry context."""
        self.attempts = 0
        self.last_exception = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit retry context."""
        if exc_type and issubclass(exc_type, self.config.retryable_exceptions):
            self.attempts += 1
            self.last_exception = exc_val

            if self.attempts < self.config.max_attempts:
                # Calculate delay and sleep
                delay = self.config.calculate_delay(self.attempts)
                logger.warning(
                    f"Retry {self.attempts}/{self.config.max_attempts} "
                    f"after {delay:.1f}s due to: {exc_val}"
                )
                time.sleep(delay)
                return True  # Suppress exception and retry

            # Max attempts reached
            logger.error(f"All retry attempts failed: {exc_val}")

        return False  # Don't suppress exception


def with_retry(
    func: Callable[..., T] | None = None, *, config: RetryConfig | None = None
) -> Callable[..., T] | Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Flexible retry decorator that can be used with or without arguments.

    Usage:
        @with_retry
        def my_function(): ...

        @with_retry(config=RetryConfig(max_attempts=5))
        def my_function(): ...
    """
    if func is None:
        # Decorator called with arguments
        def decorator(f: Callable[..., T]) -> Callable[..., T]:
            return retry(
                max_attempts=config.max_attempts if config else 3,
                initial_delay=config.initial_delay if config else 1.0,
                max_delay=config.max_delay if config else 60.0,
                exponential_base=config.exponential_base if config else 2.0,
                jitter=config.jitter if config else True,
                retryable_exceptions=config.retryable_exceptions if config else None,
            )(f)

        return decorator
    else:
        # Decorator called without arguments
        return retry()(func)


# Convenience retry configurations
FAST_RETRY = RetryConfig(max_attempts=3, initial_delay=0.1, max_delay=1.0, exponential_base=2.0)

STANDARD_RETRY = RetryConfig(
    max_attempts=3, initial_delay=1.0, max_delay=30.0, exponential_base=2.0
)

PERSISTENT_RETRY = RetryConfig(
    max_attempts=5, initial_delay=2.0, max_delay=120.0, exponential_base=2.0
)

AGGRESSIVE_RETRY = RetryConfig(
    max_attempts=10, initial_delay=0.5, max_delay=300.0, exponential_base=1.5
)
