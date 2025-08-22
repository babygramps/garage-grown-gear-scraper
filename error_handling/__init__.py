# Error handling module for the Garage Grown Gear scraper

from .exceptions import (
    ScraperError,
    NetworkError,
    RateLimitError,
    ParsingError,
    DataValidationError,
    SheetsAPIError,
    AuthenticationError,
    QuotaExceededError,
    ConfigurationError,
    RetryableError,
    NonRetryableError
)

from .retry_handler import (
    RetryHandler,
    retry_on_failure,
    GracefulErrorHandler
)

from .logging_config import (
    ScraperLogger,
    PerformanceLogger,
    setup_logging
)

from .monitoring import (
    ScrapingMetrics,
    SystemMonitor,
    ScrapingMonitor
)

__all__ = [
    # Exceptions
    'ScraperError',
    'NetworkError',
    'RateLimitError',
    'ParsingError',
    'DataValidationError',
    'SheetsAPIError',
    'AuthenticationError',
    'QuotaExceededError',
    'ConfigurationError',
    'RetryableError',
    'NonRetryableError',
    
    # Retry and error handling
    'RetryHandler',
    'retry_on_failure',
    'GracefulErrorHandler',
    
    # Logging
    'ScraperLogger',
    'PerformanceLogger',
    'setup_logging',
    
    # Monitoring
    'ScrapingMetrics',
    'SystemMonitor',
    'ScrapingMonitor'
]