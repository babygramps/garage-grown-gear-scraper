"""
Data validation and error handling utilities.

This module provides comprehensive validation rules and error handling
for product data processing.
"""

import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DataSanitizationError(Exception):
    """Custom exception for data sanitization errors."""
    pass


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.info = []
    
    def add_issue(self, severity: ValidationSeverity, field: str, message: str):
        """Add a validation issue."""
        issue = {
            'field': field,
            'message': message,
            'severity': severity.value
        }
        
        if severity == ValidationSeverity.ERROR:
            self.errors.append(issue)
            self.is_valid = False
        elif severity == ValidationSeverity.WARNING:
            self.warnings.append(issue)
        else:
            self.info.append(issue)
    
    def get_all_issues(self) -> List[Dict[str, str]]:
        """Get all validation issues."""
        return self.errors + self.warnings + self.info
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0


class DataSanitizer:
    """Utility class for data type conversion and sanitization."""
    
    @staticmethod
    def sanitize_string(value: Any, max_length: Optional[int] = None, 
                       allow_empty: bool = True) -> str:
        """
        Sanitize and convert value to string.
        
        Args:
            value: Input value to sanitize
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are allowed
            
        Returns:
            Sanitized string
            
        Raises:
            DataSanitizationError: If sanitization fails
        """
        if value is None:
            if allow_empty:
                return ""
            else:
                raise DataSanitizationError("None value not allowed for required string field")
        
        try:
            # Convert to string and clean
            sanitized = str(value).strip()
            
            # Remove control characters and normalize whitespace
            sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
            sanitized = re.sub(r'\s+', ' ', sanitized)
            
            # Check length
            if max_length and len(sanitized) > max_length:
                sanitized = sanitized[:max_length].strip()
                logger.warning(f"String truncated to {max_length} characters: {sanitized[:50]}...")
            
            # Check if empty when not allowed
            if not allow_empty and not sanitized:
                raise DataSanitizationError("Empty string not allowed for required field")
            
            return sanitized
            
        except Exception as e:
            raise DataSanitizationError(f"Failed to sanitize string: {str(e)}")
    
    @staticmethod
    def sanitize_float(value: Any, min_value: Optional[float] = None, 
                      max_value: Optional[float] = None) -> Optional[float]:
        """
        Sanitize and convert value to float.
        
        Args:
            value: Input value to sanitize
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Sanitized float or None if conversion fails
            
        Raises:
            DataSanitizationError: If sanitization fails validation
        """
        if value is None or value == "":
            return None
        
        try:
            # Handle string values
            if isinstance(value, str):
                # Remove currency symbols and commas
                cleaned = re.sub(r'[$,\s]', '', value.strip())
                if not cleaned:
                    return None
                sanitized = float(cleaned)
            else:
                sanitized = float(value)
            
            # Check bounds
            if min_value is not None and sanitized < min_value:
                raise DataSanitizationError(f"Value {sanitized} below minimum {min_value}")
            
            if max_value is not None and sanitized > max_value:
                raise DataSanitizationError(f"Value {sanitized} above maximum {max_value}")
            
            return sanitized
            
        except ValueError:
            logger.warning(f"Failed to convert to float: {value}")
            return None
        except DataSanitizationError:
            raise
        except Exception as e:
            raise DataSanitizationError(f"Failed to sanitize float: {str(e)}")
    
    @staticmethod
    def sanitize_integer(value: Any, min_value: Optional[int] = None, 
                        max_value: Optional[int] = None) -> Optional[int]:
        """
        Sanitize and convert value to integer.
        
        Args:
            value: Input value to sanitize
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Sanitized integer or None if conversion fails
            
        Raises:
            DataSanitizationError: If sanitization fails validation
        """
        if value is None or value == "":
            return None
        
        try:
            # Handle string values with numbers
            if isinstance(value, str):
                # Extract first number from string
                numbers = re.findall(r'\d+', value.strip())
                if not numbers:
                    return None
                sanitized = int(numbers[0])
            else:
                sanitized = int(float(value))  # Handle float to int conversion
            
            # Check bounds
            if min_value is not None and sanitized < min_value:
                raise DataSanitizationError(f"Value {sanitized} below minimum {min_value}")
            
            if max_value is not None and sanitized > max_value:
                raise DataSanitizationError(f"Value {sanitized} above maximum {max_value}")
            
            return sanitized
            
        except ValueError:
            logger.warning(f"Failed to convert to integer: {value}")
            return None
        except DataSanitizationError:
            raise
        except Exception as e:
            raise DataSanitizationError(f"Failed to sanitize integer: {str(e)}")
    
    @staticmethod
    def sanitize_url(value: Any, require_https: bool = False) -> str:
        """
        Sanitize and validate URL.
        
        Args:
            value: Input URL value
            require_https: Whether to require HTTPS protocol
            
        Returns:
            Sanitized URL string
            
        Raises:
            DataSanitizationError: If URL is invalid
        """
        if not value:
            return ""
        
        try:
            url = str(value).strip()
            
            # Add protocol if missing
            if url and not url.startswith(('http://', 'https://')):
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    url = 'https://www.garagegrowngear.com' + url
                else:
                    url = 'https://' + url
            
            # Validate URL format
            url_pattern = re.compile(
                r'^https?://'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(url):
                raise DataSanitizationError(f"Invalid URL format: {url}")
            
            # Check HTTPS requirement
            if require_https and not url.startswith('https://'):
                raise DataSanitizationError(f"HTTPS required but URL uses HTTP: {url}")
            
            return url
            
        except DataSanitizationError:
            raise
        except Exception as e:
            raise DataSanitizationError(f"Failed to sanitize URL: {str(e)}")


class ProductValidator:
    """Comprehensive validator for product data."""
    
    def __init__(self):
        self.sanitizer = DataSanitizer()
    
    def validate_product(self, product_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete product data.
        
        Args:
            product_data: Product data dictionary to validate
            
        Returns:
            ValidationResult with validation status and issues
        """
        result = ValidationResult()
        
        # Validate required fields
        self._validate_required_fields(product_data, result)
        
        # Validate individual fields
        self._validate_name(product_data.get('name'), result)
        self._validate_brand(product_data.get('brand'), result)
        self._validate_prices(product_data, result)
        self._validate_availability(product_data.get('availability_status'), result)
        self._validate_rating(product_data.get('rating'), result)
        self._validate_reviews_count(product_data.get('reviews_count'), result)
        self._validate_urls(product_data, result)
        
        return result
    
    def _validate_required_fields(self, product_data: Dict[str, Any], 
                                 result: ValidationResult):
        """Validate that required fields are present."""
        required_fields = ['name', 'current_price', 'product_url']
        
        for field in required_fields:
            if field not in product_data or not product_data[field]:
                result.add_issue(
                    ValidationSeverity.ERROR,
                    field,
                    f"Required field '{field}' is missing or empty"
                )
    
    def _validate_name(self, name: Any, result: ValidationResult):
        """Validate product name."""
        try:
            if not name:
                result.add_issue(ValidationSeverity.ERROR, 'name', "Product name is required")
                return
            
            sanitized_name = self.sanitizer.sanitize_string(name, max_length=200, allow_empty=False)
            
            if len(sanitized_name) < 3:
                result.add_issue(ValidationSeverity.WARNING, 'name', 
                               f"Product name is very short: '{sanitized_name}'")
            
        except DataSanitizationError as e:
            result.add_issue(ValidationSeverity.ERROR, 'name', str(e))
    
    def _validate_brand(self, brand: Any, result: ValidationResult):
        """Validate product brand."""
        try:
            if brand:
                sanitized_brand = self.sanitizer.sanitize_string(brand, max_length=100)
                if len(sanitized_brand) < 2:
                    result.add_issue(ValidationSeverity.WARNING, 'brand', 
                                   f"Brand name is very short: '{sanitized_brand}'")
            else:
                result.add_issue(ValidationSeverity.INFO, 'brand', "Brand information not available")
                
        except DataSanitizationError as e:
            result.add_issue(ValidationSeverity.WARNING, 'brand', str(e))
    
    def _validate_prices(self, product_data: Dict[str, Any], result: ValidationResult):
        """Validate price fields."""
        try:
            current_price = self.sanitizer.sanitize_float(
                product_data.get('current_price'), min_value=0.01, max_value=10000.0
            )
            
            if current_price is None:
                result.add_issue(ValidationSeverity.ERROR, 'current_price', 
                               "Valid current price is required")
                return
            
            original_price = self.sanitizer.sanitize_float(
                product_data.get('original_price'), min_value=0.01, max_value=10000.0
            )
            
            # Validate price relationship
            if original_price and current_price > original_price:
                result.add_issue(ValidationSeverity.WARNING, 'prices', 
                               f"Current price (${current_price:.2f}) is higher than original price (${original_price:.2f})")
            
            # Validate discount percentage if present
            discount = product_data.get('discount_percentage')
            if discount is not None:
                try:
                    discount_float = self.sanitizer.sanitize_float(discount, min_value=0.0, max_value=100.0)
                    if discount_float is None or discount_float < 0 or discount_float > 100:
                        result.add_issue(ValidationSeverity.WARNING, 'discount_percentage', 
                                       f"Invalid discount percentage: {discount}")
                except DataSanitizationError:
                    result.add_issue(ValidationSeverity.WARNING, 'discount_percentage', 
                                   f"Invalid discount percentage format: {discount}")
            
        except DataSanitizationError as e:
            result.add_issue(ValidationSeverity.ERROR, 'current_price', str(e))
    
    def _validate_availability(self, availability: Any, result: ValidationResult):
        """Validate availability status."""
        if not availability:
            result.add_issue(ValidationSeverity.WARNING, 'availability_status', 
                           "Availability status not provided")
            return
        
        try:
            sanitized = self.sanitizer.sanitize_string(availability, max_length=50)
            valid_statuses = ['Available', 'Sold out', 'Limited', 'Unknown']
            
            if sanitized not in valid_statuses:
                result.add_issue(ValidationSeverity.INFO, 'availability_status', 
                               f"Unusual availability status: '{sanitized}'")
                
        except DataSanitizationError as e:
            result.add_issue(ValidationSeverity.WARNING, 'availability_status', str(e))
    
    def _validate_rating(self, rating: Any, result: ValidationResult):
        """Validate product rating."""
        if rating is None:
            return  # Rating is optional
        
        try:
            rating_float = self.sanitizer.sanitize_float(rating, min_value=0.0, max_value=5.0)
            if rating_float is None:
                result.add_issue(ValidationSeverity.WARNING, 'rating', 
                               f"Invalid rating format: {rating}")
            
        except DataSanitizationError as e:
            result.add_issue(ValidationSeverity.WARNING, 'rating', str(e))
    
    def _validate_reviews_count(self, reviews_count: Any, result: ValidationResult):
        """Validate reviews count."""
        if reviews_count is None:
            return  # Reviews count is optional
        
        try:
            count = self.sanitizer.sanitize_integer(reviews_count, min_value=0, max_value=100000)
            if count is None:
                result.add_issue(ValidationSeverity.WARNING, 'reviews_count', 
                               f"Invalid reviews count format: {reviews_count}")
            
        except DataSanitizationError as e:
            result.add_issue(ValidationSeverity.WARNING, 'reviews_count', str(e))
    
    def _validate_urls(self, product_data: Dict[str, Any], result: ValidationResult):
        """Validate URL fields."""
        # Validate product URL (required)
        try:
            product_url = product_data.get('product_url')
            if not product_url:
                result.add_issue(ValidationSeverity.ERROR, 'product_url', "Product URL is required")
            else:
                self.sanitizer.sanitize_url(product_url)
                
        except DataSanitizationError as e:
            result.add_issue(ValidationSeverity.ERROR, 'product_url', str(e))
        
        # Validate image URL (optional)
        try:
            image_url = product_data.get('image_url')
            if image_url:
                self.sanitizer.sanitize_url(image_url)
                
        except DataSanitizationError as e:
            result.add_issue(ValidationSeverity.WARNING, 'image_url', str(e))


class ErrorHandler:
    """Centralized error handling for data processing operations."""
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
    
    def handle_validation_error(self, product_name: str, validation_result: ValidationResult) -> bool:
        """
        Handle validation errors for a product.
        
        Args:
            product_name: Name of the product being validated
            validation_result: Validation result with errors and warnings
            
        Returns:
            True if product should be processed despite issues, False if it should be skipped
        """
        if validation_result.has_errors():
            self.logger.error(f"Validation failed for product '{product_name}': {validation_result.errors}")
            return False
        
        if validation_result.warnings:
            self.logger.warning(f"Validation warnings for product '{product_name}': {validation_result.warnings}")
        
        if validation_result.info:
            self.logger.info(f"Validation info for product '{product_name}': {validation_result.info}")
        
        return True
    
    def handle_processing_error(self, product_name: str, error: Exception) -> bool:
        """
        Handle processing errors for a product.
        
        Args:
            product_name: Name of the product being processed
            error: Exception that occurred during processing
            
        Returns:
            True if processing should continue with other products, False if it should stop
        """
        if isinstance(error, (ValidationError, DataSanitizationError)):
            self.logger.error(f"Data error for product '{product_name}': {str(error)}")
            return True  # Continue with other products
        
        self.logger.error(f"Unexpected error processing product '{product_name}': {str(error)}", exc_info=True)
        return True  # Continue with other products by default
    
    def log_processing_summary(self, total_products: int, successful_products: int, 
                             failed_products: int):
        """Log a summary of processing results."""
        success_rate = (successful_products / total_products * 100) if total_products > 0 else 0
        
        self.logger.info(f"Processing complete: {successful_products}/{total_products} products successful "
                        f"({success_rate:.1f}% success rate)")
        
        if failed_products > 0:
            self.logger.warning(f"{failed_products} products failed processing")