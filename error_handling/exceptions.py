"""
Custom exception classes for the Garage Grown Gear scraper.
Provides specific error types for different failure scenarios.
"""

class ScraperError(Exception):
    """Base exception class for all scraper-related errors."""
    pass


class NetworkError(ScraperError):
    """Raised when network-related errors occur during scraping."""
    
    def __init__(self, message: str, status_code: int = None, url: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url


class RateLimitError(NetworkError):
    """Raised when rate limiting is encountered."""
    
    def __init__(self, message: str, retry_after: int = None, url: str = None):
        super().__init__(message, status_code=429, url=url)
        self.retry_after = retry_after


class ParsingError(ScraperError):
    """Raised when HTML parsing fails or expected elements are not found."""
    
    def __init__(self, message: str, selector: str = None, url: str = None):
        super().__init__(message)
        self.selector = selector
        self.url = url


class DataValidationError(ScraperError):
    """Raised when scraped data fails validation checks."""
    
    def __init__(self, message: str, field_name: str = None, field_value: str = None):
        super().__init__(message)
        self.field_name = field_name
        self.field_value = field_value


class SheetsAPIError(ScraperError):
    """Raised when Google Sheets API operations fail."""
    
    def __init__(self, message: str, error_code: str = None, operation: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.operation = operation


class AuthenticationError(SheetsAPIError):
    """Raised when Google Sheets authentication fails."""
    
    def __init__(self, message: str = "Google Sheets authentication failed"):
        super().__init__(message, error_code="AUTH_FAILED", operation="authenticate")


class QuotaExceededError(SheetsAPIError):
    """Raised when Google Sheets API quota is exceeded."""
    
    def __init__(self, message: str = "Google Sheets API quota exceeded"):
        super().__init__(message, error_code="QUOTA_EXCEEDED", operation="api_call")


class ConfigurationError(ScraperError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message)
        self.config_key = config_key


class RetryableError(ScraperError):
    """Base class for errors that should trigger retry logic."""
    pass


class NonRetryableError(ScraperError):
    """Base class for errors that should not trigger retry logic."""
    pass