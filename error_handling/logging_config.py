"""
Comprehensive logging configuration for the Garage Grown Gear scraper.
Provides structured logging with different levels and performance tracking.
"""

import logging
import logging.handlers
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)


class PerformanceLogger:
    """Logger for tracking performance metrics during scraping operations."""
    
    def __init__(self, logger_name: str = 'performance'):
        self.logger = logging.getLogger(logger_name)
        self.start_times = {}
        self.metrics = {}
    
    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation."""
        self.start_times[operation_name] = time.time()
        self.logger.info(f"Started operation: {operation_name}")
    
    def end_operation(self, operation_name: str, **extra_metrics) -> float:
        """End timing an operation and log the duration."""
        if operation_name not in self.start_times:
            self.logger.warning(f"No start time found for operation: {operation_name}")
            return 0.0
        
        duration = time.time() - self.start_times[operation_name]
        del self.start_times[operation_name]
        
        # Store metrics
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        
        metric_entry = {
            'duration': duration,
            'timestamp': time.time(),
            **extra_metrics
        }
        self.metrics[operation_name].append(metric_entry)
        
        self.logger.info(
            f"Completed operation: {operation_name}",
            extra={'extra_fields': {
                'duration_seconds': duration,
                'operation': operation_name,
                **extra_metrics
            }}
        )
        
        return duration
    
    def log_metric(self, metric_name: str, value: Any, **extra_data) -> None:
        """Log a custom metric."""
        self.logger.info(
            f"Metric: {metric_name} = {value}",
            extra={'extra_fields': {
                'metric_name': metric_name,
                'metric_value': value,
                **extra_data
            }}
        )
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        if operation_name not in self.metrics:
            return {}
        
        durations = [m['duration'] for m in self.metrics[operation_name]]
        
        return {
            'operation': operation_name,
            'total_runs': len(durations),
            'total_duration': sum(durations),
            'average_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'last_run': self.metrics[operation_name][-1]['timestamp']
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        return {
            operation: self.get_operation_stats(operation)
            for operation in self.metrics.keys()
        }


class ScraperLogger:
    """Main logger class for the scraper application."""
    
    def __init__(
        self,
        name: str = 'garage_grown_gear_scraper',
        level: str = 'INFO',
        log_file: Optional[str] = None,
        use_structured_logging: bool = True,
        console_output: bool = True
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set up formatters
        if use_structured_logging:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Performance logger
        self.performance = PerformanceLogger(f'{name}.performance')
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def debug(self, message: str, **extra_fields) -> None:
        """Log debug message."""
        self._log_with_extra(logging.DEBUG, message, extra_fields)
    
    def info(self, message: str, **extra_fields) -> None:
        """Log info message."""
        self._log_with_extra(logging.INFO, message, extra_fields)
    
    def warning(self, message: str, **extra_fields) -> None:
        """Log warning message."""
        self._log_with_extra(logging.WARNING, message, extra_fields)
    
    def error(self, message: str, exc_info: bool = False, **extra_fields) -> None:
        """Log error message."""
        self._log_with_extra(logging.ERROR, message, extra_fields, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False, **extra_fields) -> None:
        """Log critical message."""
        self._log_with_extra(logging.CRITICAL, message, extra_fields, exc_info=exc_info)
    
    def _log_with_extra(
        self,
        level: int,
        message: str,
        extra_fields: Dict[str, Any],
        exc_info: bool = False
    ) -> None:
        """Log message with extra fields."""
        if extra_fields:
            self.logger.log(
                level,
                message,
                exc_info=exc_info,
                extra={'extra_fields': extra_fields}
            )
        else:
            self.logger.log(level, message, exc_info=exc_info)
    
    def log_scraping_start(self, url: str, total_pages: int = None) -> None:
        """Log the start of a scraping operation."""
        extra_fields = {'url': url, 'operation': 'scraping_start'}
        if total_pages:
            extra_fields['total_pages'] = total_pages
        
        self.info("Starting scraping operation", **extra_fields)
        self.performance.start_operation('full_scrape')
    
    def log_scraping_end(self, products_scraped: int, errors_count: int = 0) -> None:
        """Log the end of a scraping operation."""
        duration = self.performance.end_operation(
            'full_scrape',
            products_scraped=products_scraped,
            errors_count=errors_count
        )
        
        self.info(
            "Scraping operation completed",
            products_scraped=products_scraped,
            errors_count=errors_count,
            duration_seconds=duration,
            operation='scraping_end'
        )
    
    def log_page_scraped(self, page_url: str, products_found: int) -> None:
        """Log completion of a single page scrape."""
        self.info(
            f"Scraped page: {page_url}",
            page_url=page_url,
            products_found=products_found,
            operation='page_scraped'
        )
    
    def log_product_processed(self, product_name: str, success: bool = True) -> None:
        """Log processing of a single product."""
        if success:
            self.debug(
                f"Successfully processed product: {product_name}",
                product_name=product_name,
                operation='product_processed',
                success=True
            )
        else:
            self.warning(
                f"Failed to process product: {product_name}",
                product_name=product_name,
                operation='product_processed',
                success=False
            )
    
    def log_sheets_operation(self, operation: str, success: bool, **extra_data) -> None:
        """Log Google Sheets operations."""
        level = logging.INFO if success else logging.ERROR
        message = f"Google Sheets {operation} {'succeeded' if success else 'failed'}"
        
        extra_fields = {
            'operation': f'sheets_{operation}',
            'success': success,
            **extra_data
        }
        
        self._log_with_extra(level, message, extra_fields)
    
    def log_error_summary(self, error_handler) -> None:
        """Log a summary of errors from the error handler."""
        if hasattr(error_handler, 'get_summary'):
            summary = error_handler.get_summary()
            self.info(
                "Error summary",
                **summary,
                operation='error_summary'
            )
            
            if hasattr(error_handler, 'get_errors_by_type'):
                error_types = error_handler.get_errors_by_type()
                for error_type, errors in error_types.items():
                    self.warning(
                        f"Error type: {error_type}",
                        error_type=error_type,
                        error_count=len(errors),
                        operation='error_type_summary'
                    )


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    structured: bool = True,
    console: bool = True
) -> ScraperLogger:
    """
    Set up logging for the scraper application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        structured: Use structured JSON logging
        console: Enable console output
    
    Returns:
        ScraperLogger: Configured logger instance
    """
    return ScraperLogger(
        level=level,
        log_file=log_file,
        use_structured_logging=structured,
        console_output=console
    )