"""
Configuration management system for the Garage Grown Gear scraper.
Provides dataclasses for different configuration sections with validation.
"""

from dataclasses import dataclass
from typing import Optional, List
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


@dataclass
class ScraperConfig:
    """Configuration for web scraping operations."""
    base_url: str = "https://www.garagegrowngear.com/collections/sale-1"
    max_retries: int = 6  # More retries for sophisticated blocking
    retry_delay: float = 5.0  # Much longer base delay
    request_timeout: int = 60  # Longer timeout for complex responses
    use_stealth_mode: bool = True
    delay_between_requests: float = 8.0  # Much longer delays between requests
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        """Validate scraper configuration."""
        errors = []
        
        if not self.base_url or not self.base_url.strip():
            errors.append("Base URL is required")
        elif not self.base_url.startswith(('http://', 'https://')):
            errors.append("Base URL must start with http:// or https://")
        
        if self.max_retries < 0:
            errors.append("Max retries must be non-negative")
        elif self.max_retries > 10:
            errors.append("Max retries should not exceed 10 for reasonable performance")
        
        if self.retry_delay < 0:
            errors.append("Retry delay must be non-negative")
        elif self.retry_delay > 60:
            errors.append("Retry delay should not exceed 60 seconds")
        
        if self.request_timeout <= 0:
            errors.append("Request timeout must be positive")
        elif self.request_timeout > 300:
            errors.append("Request timeout should not exceed 300 seconds")
        
        if self.delay_between_requests < 0:
            errors.append("Delay between requests must be non-negative")
        elif self.delay_between_requests > 10:
            errors.append("Delay between requests should not exceed 10 seconds for reasonable performance")
        
        if not self.user_agent or not self.user_agent.strip():
            errors.append("User agent is required")
        
        if errors:
            raise ConfigurationError(f"Scraper configuration errors: {'; '.join(errors)}")


@dataclass
class SheetsConfig:
    """Configuration for Google Sheets integration."""
    spreadsheet_id: str = ""
    sheet_name: str = "Product_Data"
    credentials_file: str = "service_account.json"
    
    def __post_init__(self):
        # Get spreadsheet ID from environment variable if not provided
        if not self.spreadsheet_id:
            self.spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
        
        self.validate()
    
    def validate(self) -> None:
        """Validate Google Sheets configuration."""
        errors = []
        
        if not self.spreadsheet_id:
            errors.append("SPREADSHEET_ID is required but not provided")
        elif not re.match(r'^[a-zA-Z0-9-_]{44}$', self.spreadsheet_id):
            errors.append("SPREADSHEET_ID format appears invalid (should be 44 characters)")
        
        if not self.sheet_name or not self.sheet_name.strip():
            errors.append("Sheet name cannot be empty")
        
        if not self.credentials_file:
            errors.append("Credentials file path is required")
        
        if errors:
            raise ConfigurationError(f"Google Sheets configuration errors: {'; '.join(errors)}")


@dataclass
class LoggingConfig:
    """Configuration for logging system."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_to_file: bool = False
    log_file_path: str = "scraper.log"
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        """Validate logging configuration."""
        errors = []
        
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            errors.append(f"Log level must be one of: {', '.join(valid_levels)}")
        
        if not self.format or not self.format.strip():
            errors.append("Log format cannot be empty")
        
        if self.log_to_file and (not self.log_file_path or not self.log_file_path.strip()):
            errors.append("Log file path is required when log_to_file is True")
        
        if errors:
            raise ConfigurationError(f"Logging configuration errors: {'; '.join(errors)}")


@dataclass
class NotificationConfig:
    """Configuration for notifications and alerts."""
    enable_notifications: bool = False
    webhook_url: Optional[str] = None
    email_notifications: bool = False
    price_drop_threshold: float = 20.0  # Percentage threshold for significant price drops
    
    def __post_init__(self):
        # Get webhook URL from environment variable if not provided
        if not self.webhook_url:
            self.webhook_url = os.getenv("WEBHOOK_URL")
        
        self.validate()
    
    def validate(self) -> None:
        """Validate notification configuration."""
        errors = []
        
        if self.enable_notifications and not self.webhook_url and not self.email_notifications:
            errors.append("When notifications are enabled, either webhook_url or email_notifications must be configured")
        
        if self.webhook_url and not self.webhook_url.startswith(('http://', 'https://')):
            errors.append("Webhook URL must start with http:// or https://")
        
        if self.price_drop_threshold < 0 or self.price_drop_threshold > 100:
            errors.append("Price drop threshold must be between 0 and 100 percent")
        
        if errors:
            raise ConfigurationError(f"Notification configuration errors: {'; '.join(errors)}")


@dataclass
class AppConfig:
    """Main application configuration that combines all config sections."""
    scraper: ScraperConfig
    sheets: SheetsConfig
    logging: LoggingConfig
    notifications: NotificationConfig
    
    @classmethod
    def from_defaults(cls) -> 'AppConfig':
        """Create configuration with default values."""
        return cls(
            scraper=ScraperConfig(),
            sheets=SheetsConfig(),
            logging=LoggingConfig(),
            notifications=NotificationConfig()
        )
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        try:
            scraper_config = ScraperConfig(
                base_url=os.getenv("BASE_URL", ScraperConfig.base_url),
                max_retries=int(os.getenv("MAX_RETRIES", ScraperConfig.max_retries)),
                retry_delay=float(os.getenv("RETRY_DELAY", ScraperConfig.retry_delay)),
                request_timeout=int(os.getenv("REQUEST_TIMEOUT", ScraperConfig.request_timeout)),
                use_stealth_mode=os.getenv("USE_STEALTH_MODE", "true").lower() == "true",
                delay_between_requests=float(os.getenv("DELAY_BETWEEN_REQUESTS", ScraperConfig.delay_between_requests))
            )
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Error parsing scraper configuration from environment: {e}")
        
        try:
            sheets_config = SheetsConfig(
                spreadsheet_id=os.getenv("SPREADSHEET_ID", ""),
                sheet_name=os.getenv("SHEET_NAME", SheetsConfig.sheet_name),
                credentials_file=os.getenv("CREDENTIALS_FILE", SheetsConfig.credentials_file)
            )
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Error parsing sheets configuration from environment: {e}")
        
        try:
            logging_config = LoggingConfig(
                level=os.getenv("LOG_LEVEL", LoggingConfig.level),
                log_to_file=os.getenv("LOG_TO_FILE", "false").lower() == "true",
                log_file_path=os.getenv("LOG_FILE_PATH", LoggingConfig.log_file_path)
            )
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Error parsing logging configuration from environment: {e}")
        
        try:
            notifications_config = NotificationConfig(
                enable_notifications=os.getenv("ENABLE_NOTIFICATIONS", "false").lower() == "true",
                webhook_url=os.getenv("WEBHOOK_URL"),
                email_notifications=os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true",
                price_drop_threshold=float(os.getenv("PRICE_DROP_THRESHOLD", NotificationConfig.price_drop_threshold))
            )
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Error parsing notification configuration from environment: {e}")
        
        return cls(
            scraper=scraper_config,
            sheets=sheets_config,
            logging=logging_config,
            notifications=notifications_config
        )
    
    def validate_all(self) -> List[str]:
        """Validate all configuration sections and return list of errors."""
        errors = []
        
        for config_name, config_obj in [
            ("scraper", self.scraper),
            ("sheets", self.sheets), 
            ("logging", self.logging),
            ("notifications", self.notifications)
        ]:
            try:
                config_obj.validate()
            except ConfigurationError as e:
                errors.append(f"{config_name}: {e}")
        
        return errors


# CSS selectors for scraping based on the provided HTML structure
SELECTORS = {
    'product_items': '.product-item',
    'product_name': '.product-item__title a',
    'brand': '.product-item__vendor',
    'current_price': '.price--highlight [data-money-convertible]',
    'original_price': '.price--compare [data-money-convertible]',
    'sale_label': '.product-label--on-sale',
    'availability': '.product-item__inventory',
    'rating': '.stamped-badge[data-rating]',
    'reviews_count': '.stamped-badge-caption[data-reviews]',
    'product_link': '.product-item__title a',
    'image': '.product-item__primary-image img',
    'pagination_next': '.pagination__next',
    'pagination_items': '.pagination__item'
}