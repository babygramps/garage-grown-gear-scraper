"""
Unit tests for error handling and monitoring modules.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
import time
from error_handling.exceptions import (
    ScrapingError, ValidationError, DataSanitizationError, 
    SheetsClientError, RetryableError
)
from error_handling.retry_handler import RetryHandler, ExponentialBackoff
from error_handling.monitoring import PerformanceMonitor, MetricsCollector
from error_handling.logging_config import setup_logging, get_logger


class TestCustomExceptions(unittest.TestCase):
    """Test cases for custom exception classes."""
    
    def test_scraping_error(self):
        """Test ScrapingError exception."""
        error = ScrapingError("Test scraping error", url="https://example.com")
        
        self.assertEqual(str(error), "Test scraping error")
        self.assertEqual(error.url, "https://example.com")
        self.assertIsInstance(error, Exception)
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Invalid data", field="name", value="")
        
        self.assertEqual(str(error), "Invalid data")
        self.assertEqual(error.field, "name")
        self.assertEqual(error.value, "")
    
    def test_data_sanitization_error(self):
        """Test DataSanitizationError exception."""
        error = DataSanitizationError("Sanitization failed", data_type="string")
        
        self.assertEqual(str(error), "Sanitization failed")
        self.assertEqual(error.data_type, "string")
    
    def test_sheets_client_error(self):
        """Test SheetsClientError exception."""
        error = SheetsClientError("Sheets API error", error_code=403)
        
        self.assertEqual(str(error), "Sheets API error")
        self.assertEqual(error.error_code, 403)
    
    def test_retryable_error(self):
        """Test RetryableError exception."""
        error = RetryableError("Network timeout", retry_after=5.0)
        
        self.assertEqual(str(error), "Network timeout")
        self.assertEqual(error.retry_after, 5.0)
        self.assertTrue(error.is_retryable())


class TestExponentialBackoff(unittest.TestCase):
    """Test cases for ExponentialBackoff class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.backoff = ExponentialBackoff(
            initial_delay=1.0,
            max_delay=60.0,
            multiplier=2.0,
            jitter=False  # Disable jitter for predictable tests
        )
    
    def test_initial_delay(self):
        """Test initial delay calculation."""
        delay = self.backoff.calculate_delay(0)
        self.assertEqual(delay, 1.0)
    
    def test_exponential_growth(self):
        """Test exponential delay growth."""
        delays = [self.backoff.calculate_delay(i) for i in range(5)]
        expected = [1.0, 2.0, 4.0, 8.0, 16.0]
        
        self.assertEqual(delays, expected)
    
    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        # Calculate delay for high attempt number
        delay = self.backoff.calculate_delay(10)
        self.assertEqual(delay, 60.0)  # Should be capped at max_delay
    
    def test_jitter_enabled(self):
        """Test jitter adds randomness to delay."""
        backoff_with_jitter = ExponentialBackoff(
            initial_delay=1.0,
            max_delay=60.0,
            multiplier=2.0,
            jitter=True
        )
        
        # Calculate multiple delays for same attempt
        delays = [backoff_with_jitter.calculate_delay(1) for _ in range(10)]
        
        # With jitter, delays should vary
        self.assertGreater(len(set(delays)), 1)
        
        # All delays should be within reasonable range
        for delay in delays:
            self.assertGreaterEqual(delay, 1.0)  # At least base delay
            self.assertLessEqual(delay, 4.0)     # At most 2x base delay


class TestRetryHandler(unittest.TestCase):
    """Test cases for RetryHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.retry_handler = RetryHandler(
            max_attempts=3,
            backoff_strategy=ExponentialBackoff(initial_delay=0.1, jitter=False)
        )
    
    @patch('time.sleep')
    def test_execute_success_first_attempt(self, mock_sleep):
        """Test successful execution on first attempt."""
        mock_func = Mock(return_value="success")
        
        result = self.retry_handler.execute(mock_func)
        
        self.assertEqual(result, "success")
        mock_func.assert_called_once()
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    def test_execute_success_after_retries(self, mock_sleep):
        """Test successful execution after retries."""
        mock_func = Mock(side_effect=[Exception("error"), Exception("error"), "success"])
        
        result = self.retry_handler.execute(mock_func)
        
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # 2 retries
    
    @patch('time.sleep')
    def test_execute_max_attempts_exceeded(self, mock_sleep):
        """Test execution when max attempts are exceeded."""
        mock_func = Mock(side_effect=Exception("persistent error"))
        
        with self.assertRaises(Exception) as context:
            self.retry_handler.execute(mock_func)
        
        self.assertEqual(str(context.exception), "persistent error")
        self.assertEqual(mock_func.call_count, 3)  # max_attempts
        self.assertEqual(mock_sleep.call_count, 2)  # max_attempts - 1
    
    @patch('time.sleep')
    def test_execute_with_retryable_error(self, mock_sleep):
        """Test execution with RetryableError."""
        retryable_error = RetryableError("Network timeout", retry_after=2.0)
        mock_func = Mock(side_effect=[retryable_error, "success"])
        
        result = self.retry_handler.execute(mock_func)
        
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)
        mock_sleep.assert_called_once_with(2.0)  # Uses retry_after from error
    
    def test_execute_with_non_retryable_error(self):
        """Test execution with non-retryable error."""
        # Create handler that only retries specific exceptions
        handler = RetryHandler(
            max_attempts=3,
            retryable_exceptions=(ConnectionError,)
        )
        
        mock_func = Mock(side_effect=ValueError("non-retryable"))
        
        with self.assertRaises(ValueError):
            handler.execute(mock_func)
        
        mock_func.assert_called_once()  # Should not retry
    
    @patch('time.sleep')
    def test_execute_with_callback(self, mock_sleep):
        """Test execution with retry callback."""
        callback = Mock()
        mock_func = Mock(side_effect=[Exception("error"), "success"])
        
        result = self.retry_handler.execute(mock_func, retry_callback=callback)
        
        self.assertEqual(result, "success")
        callback.assert_called_once()
        
        # Check callback was called with correct arguments
        call_args = callback.call_args[0]
        self.assertEqual(call_args[0], 1)  # attempt number
        self.assertIsInstance(call_args[1], Exception)  # exception


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor()
    
    @patch('time.time')
    def test_start_timer(self, mock_time):
        """Test starting a timer."""
        mock_time.return_value = 1000.0
        
        self.monitor.start_timer("test_operation")
        
        self.assertIn("test_operation", self.monitor._timers)
        self.assertEqual(self.monitor._timers["test_operation"], 1000.0)
    
    @patch('time.time')
    def test_end_timer(self, mock_time):
        """Test ending a timer and recording duration."""
        mock_time.side_effect = [1000.0, 1005.0]  # 5 second duration
        
        self.monitor.start_timer("test_operation")
        duration = self.monitor.end_timer("test_operation")
        
        self.assertEqual(duration, 5.0)
        self.assertNotIn("test_operation", self.monitor._timers)
    
    def test_end_timer_not_started(self):
        """Test ending a timer that was never started."""
        duration = self.monitor.end_timer("nonexistent_timer")
        
        self.assertIsNone(duration)
    
    @patch('time.time')
    def test_context_manager(self, mock_time):
        """Test using monitor as context manager."""
        mock_time.side_effect = [1000.0, 1003.0]  # 3 second duration
        
        with self.monitor.timer("context_operation") as timer:
            pass  # Simulate some work
        
        self.assertEqual(timer.duration, 3.0)
    
    def test_record_metric(self):
        """Test recording custom metrics."""
        self.monitor.record_metric("products_scraped", 150)
        self.monitor.record_metric("errors_count", 2)
        
        metrics = self.monitor.get_metrics()
        
        self.assertEqual(metrics["products_scraped"], 150)
        self.assertEqual(metrics["errors_count"], 2)
    
    def test_increment_counter(self):
        """Test incrementing counter metrics."""
        self.monitor.increment_counter("page_count")
        self.monitor.increment_counter("page_count")
        self.monitor.increment_counter("page_count", 3)
        
        metrics = self.monitor.get_metrics()
        
        self.assertEqual(metrics["page_count"], 5)
    
    def test_get_metrics(self):
        """Test getting all recorded metrics."""
        self.monitor.record_metric("test_metric", 100)
        self.monitor.increment_counter("test_counter", 5)
        
        metrics = self.monitor.get_metrics()
        
        self.assertIn("test_metric", metrics)
        self.assertIn("test_counter", metrics)
        self.assertEqual(metrics["test_metric"], 100)
        self.assertEqual(metrics["test_counter"], 5)
    
    def test_reset_metrics(self):
        """Test resetting all metrics."""
        self.monitor.record_metric("test_metric", 100)
        self.monitor.increment_counter("test_counter", 5)
        
        self.monitor.reset_metrics()
        
        metrics = self.monitor.get_metrics()
        self.assertEqual(len(metrics), 0)


class TestMetricsCollector(unittest.TestCase):
    """Test cases for MetricsCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = MetricsCollector()
    
    def test_collect_system_metrics(self):
        """Test collecting system metrics."""
        with patch('psutil.cpu_percent', return_value=45.5):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 60.0
                
                metrics = self.collector.collect_system_metrics()
                
                self.assertEqual(metrics["cpu_percent"], 45.5)
                self.assertEqual(metrics["memory_percent"], 60.0)
                self.assertIn("timestamp", metrics)
    
    def test_collect_scraping_metrics(self):
        """Test collecting scraping-specific metrics."""
        scraping_data = {
            "total_products": 150,
            "successful_products": 145,
            "failed_products": 5,
            "pages_scraped": 6,
            "total_duration": 45.2
        }
        
        metrics = self.collector.collect_scraping_metrics(scraping_data)
        
        self.assertEqual(metrics["total_products"], 150)
        self.assertEqual(metrics["success_rate"], 96.67)  # 145/150 * 100
        self.assertEqual(metrics["avg_products_per_page"], 25.0)  # 150/6
        self.assertEqual(metrics["products_per_second"], 3.32)  # 150/45.2
    
    def test_collect_error_metrics(self):
        """Test collecting error metrics."""
        errors = [
            Exception("Network error"),
            ValueError("Invalid data"),
            ConnectionError("Connection failed"),
            ValueError("Another validation error")
        ]
        
        metrics = self.collector.collect_error_metrics(errors)
        
        self.assertEqual(metrics["total_errors"], 4)
        self.assertEqual(metrics["error_types"]["Exception"], 1)
        self.assertEqual(metrics["error_types"]["ValueError"], 2)
        self.assertEqual(metrics["error_types"]["ConnectionError"], 1)
    
    def test_generate_summary_report(self):
        """Test generating summary report."""
        performance_metrics = {
            "scraping_duration": 45.2,
            "products_scraped": 150
        }
        
        system_metrics = {
            "cpu_percent": 45.5,
            "memory_percent": 60.0
        }
        
        error_metrics = {
            "total_errors": 3,
            "error_types": {"ValueError": 2, "ConnectionError": 1}
        }
        
        report = self.collector.generate_summary_report(
            performance_metrics, system_metrics, error_metrics
        )
        
        self.assertIn("Performance Summary", report)
        self.assertIn("System Resources", report)
        self.assertIn("Error Summary", report)
        self.assertIn("150 products", report)
        self.assertIn("45.2 seconds", report)
        self.assertIn("3 errors", report)


class TestLoggingConfig(unittest.TestCase):
    """Test cases for logging configuration."""
    
    def test_setup_logging_default(self):
        """Test default logging setup."""
        with patch('logging.basicConfig') as mock_config:
            setup_logging()
            
            mock_config.assert_called_once()
            call_kwargs = mock_config.call_args[1]
            
            self.assertEqual(call_kwargs['level'], logging.INFO)
            self.assertIn('%(asctime)s', call_kwargs['format'])
    
    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        with patch('logging.basicConfig') as mock_config:
            setup_logging(level=logging.DEBUG)
            
            mock_config.assert_called_once()
            call_kwargs = mock_config.call_args[1]
            
            self.assertEqual(call_kwargs['level'], logging.DEBUG)
    
    def test_get_logger(self):
        """Test getting a configured logger."""
        logger = get_logger("test_module")
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_module")
    
    @patch('logging.FileHandler')
    def test_setup_logging_with_file(self, mock_file_handler):
        """Test logging setup with file output."""
        mock_handler = Mock()
        mock_file_handler.return_value = mock_handler
        
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            setup_logging(log_file="test.log")
            
            mock_file_handler.assert_called_once_with("test.log")
            mock_logger.addHandler.assert_called_once_with(mock_handler)


if __name__ == '__main__':
    unittest.main()