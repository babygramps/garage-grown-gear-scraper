"""
Retry logic with exponential backoff for handling transient failures.
"""

import time
import random
import logging
from typing import Callable, Any, Type, Tuple, Optional
from functools import wraps

from .exceptions import (
    NetworkError, RateLimitError, SheetsAPIError, QuotaExceededError,
    RetryableError, NonRetryableError
)

logger = logging.getLogger(__name__)


class RetryHandler:
    """Handles retry logic with exponential backoff and jitter."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter to prevent thundering herd
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if an exception should trigger a retry."""
        if attempt >= self.max_retries:
            return False
        
        # Don't retry non-retryable errors
        if isinstance(exception, NonRetryableError):
            return False
        
        # Always retry retryable errors
        if isinstance(exception, RetryableError):
            return True
        
        # Retry specific error types
        retryable_exceptions = (
            NetworkError,
            RateLimitError,
            SheetsAPIError,
            QuotaExceededError,
            ConnectionError,
            TimeoutError
        )
        
        return isinstance(exception, retryable_exceptions)
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute a function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self.should_retry(e, attempt):
                    logger.error(
                        f"Non-retryable error or max retries exceeded: {e}",
                        exc_info=True
                    )
                    raise
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    
                    # Handle rate limiting with specific delay
                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = max(delay, e.retry_after)
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
        
        # If we get here, all retries failed
        logger.error(f"All retry attempts failed. Last error: {last_exception}")
        raise last_exception


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """Decorator for adding retry logic to functions."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_handler = RetryHandler(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter
            )
            return retry_handler.execute_with_retry(func, *args, **kwargs)
        
        return wrapper
    
    return decorator


class GracefulErrorHandler:
    """Handles errors gracefully, allowing processing to continue on individual failures."""
    
    def __init__(self, continue_on_error: bool = True):
        self.continue_on_error = continue_on_error
        self.errors = []
        self.successful_operations = 0
        self.failed_operations = 0
    
    def handle_error(
        self,
        error: Exception,
        context: str = "",
        item_id: str = None
    ) -> bool:
        """
        Handle an error gracefully.
        
        Returns:
            bool: True if processing should continue, False if it should stop
        """
        error_info = {
            'error': error,
            'context': context,
            'item_id': item_id,
            'timestamp': time.time()
        }
        
        self.errors.append(error_info)
        self.failed_operations += 1
        
        logger.error(
            f"Error in {context}" + (f" for item {item_id}" if item_id else "") + f": {error}",
            exc_info=True
        )
        
        # Stop processing for critical errors
        critical_errors = (
            AuthenticationError,
            ConfigurationError,
            NonRetryableError
        )
        
        if isinstance(error, critical_errors):
            logger.critical(f"Critical error encountered: {error}")
            return False
        
        return self.continue_on_error
    
    def record_success(self):
        """Record a successful operation."""
        self.successful_operations += 1
    
    def get_summary(self) -> dict:
        """Get a summary of operations and errors."""
        return {
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'total_operations': self.successful_operations + self.failed_operations,
            'error_count': len(self.errors),
            'success_rate': (
                self.successful_operations / (self.successful_operations + self.failed_operations)
                if (self.successful_operations + self.failed_operations) > 0
                else 0
            )
        }
    
    def has_errors(self) -> bool:
        """Check if any errors were recorded."""
        return len(self.errors) > 0
    
    def get_errors_by_type(self) -> dict:
        """Group errors by their type."""
        error_types = {}
        for error_info in self.errors:
            error_type = type(error_info['error']).__name__
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(error_info)
        return error_types