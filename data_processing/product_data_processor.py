"""
Product data processing and validation module.

This module provides functionality to clean, validate, and process
scraped product data from the Garage Grown Gear website.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import logging

from .validators import ProductValidator, ErrorHandler, DataSanitizer
from .quality_monitor import DataQualityMonitor, DataQualityMetrics
from error_handling.monitoring import BatchProcessor, PerformanceMonitor

logger = logging.getLogger(__name__)


@dataclass
class Product:
    """Data model for a product with validation and formatting methods."""
    timestamp: datetime
    name: str
    brand: str
    current_price: float
    original_price: Optional[float]
    discount_percentage: Optional[float]
    availability_status: str
    rating: Optional[float]
    reviews_count: Optional[int]
    product_url: str
    sale_label: Optional[str] = None
    image_url: Optional[str] = None
    
    def to_sheets_row(self) -> List[str]:
        """Convert product data to Google Sheets row format."""
        return [
            self.timestamp.isoformat(),
            self.name,
            self.brand,
            f"${self.current_price:.2f}" if self.current_price else "",
            f"${self.original_price:.2f}" if self.original_price else "",
            f"{self.discount_percentage:.1f}%" if self.discount_percentage else "",
            self.availability_status,
            str(self.rating) if self.rating else "",
            str(self.reviews_count) if self.reviews_count else "",
            self.product_url,
            self.sale_label or "",
            self.image_url or ""
        ]


class PriceParser:
    """Utility class for parsing and handling price strings."""
    
    @staticmethod
    def parse_price(price_str: str) -> Optional[float]:
        """
        Parse a price string and return the numeric value.
        
        Args:
            price_str: Price string like "$29.99", "29.99", "$1,299.00"
            
        Returns:
            Float value of the price or None if parsing fails
        """
        if not price_str or not isinstance(price_str, str):
            return None
            
        # Remove currency symbols, whitespace, and commas
        cleaned = re.sub(r'[$,\s]', '', price_str.strip())
        
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse price: {price_str}")
            return None
    
    @staticmethod
    def calculate_discount_percentage(current_price: float, original_price: float) -> Optional[float]:
        """
        Calculate discount percentage from current and original prices.
        
        Args:
            current_price: Current sale price
            original_price: Original price before discount
            
        Returns:
            Discount percentage or None if calculation not possible
        """
        if not current_price or not original_price or original_price <= 0:
            return None
            
        if current_price >= original_price:
            return 0.0
            
        discount = ((original_price - current_price) / original_price) * 100
        return round(discount, 1)


class ProductDataProcessor:
    """Main class for processing and validating scraped product data."""
    
    def __init__(self, enable_performance_monitoring: bool = True, batch_size: int = 100,
                 enable_quality_monitoring: bool = True):
        self.price_parser = PriceParser()
        self.validator = ProductValidator()
        self.error_handler = ErrorHandler(__name__)
        self.sanitizer = DataSanitizer()
        
        # Performance monitoring and batch processing
        self.performance_monitor = PerformanceMonitor() if enable_performance_monitoring else None
        self.batch_processor = BatchProcessor(batch_size=batch_size)
        
        # Data quality monitoring
        self.quality_monitor = DataQualityMonitor() if enable_quality_monitoring else None
        
    def process_products(self, raw_products: List[Dict[str, Any]]) -> List[Product]:
        """
        Process a list of raw product dictionaries into validated Product objects with batch processing.
        
        Args:
            raw_products: List of raw product data dictionaries
            
        Returns:
            List of validated Product objects
        """
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("process_products", 
                                                          product_count=len(raw_products)):
                return self._process_products_internal(raw_products)
        else:
            return self._process_products_internal(raw_products)
    
    def _process_products_internal(self, raw_products: List[Dict[str, Any]]) -> List[Product]:
        """Internal method for processing products."""
        # Use batch processing for large datasets
        if len(raw_products) > self.batch_processor.batch_size:
            processed_batches = self.batch_processor.process_in_batches(
                raw_products, 
                self._process_product_batch
            )
            # Flatten the results
            processed_products = []
            failed_count = 0
            for batch_result in processed_batches:
                processed_products.extend(batch_result['products'])
                failed_count += batch_result['failed_count']
        else:
            batch_result = self._process_product_batch(raw_products)
            processed_products = batch_result['products']
            failed_count = batch_result['failed_count']
        
        # Log processing summary
        self.error_handler.log_processing_summary(
            len(raw_products), len(processed_products), failed_count
        )
        
        # Perform quality analysis on processed products
        if self.quality_monitor and processed_products:
            # Convert Product objects back to dictionaries for quality analysis
            product_dicts = [self._product_to_dict(product) for product in processed_products]
            quality_metrics = self.quality_monitor.analyze_data_quality(product_dicts)
            
            logger.info(f"Data quality analysis completed. Quality score: {quality_metrics.quality_score:.1f}")
            
            # Log quality alerts if any
            if self.quality_monitor.alerts:
                recent_alerts = self.quality_monitor.alerts[-5:]  # Last 5 alerts
                for alert in recent_alerts:
                    logger.warning(f"Quality Alert [{alert.severity}]: {alert.message}")
        
        return processed_products
    
    def _process_product_batch(self, raw_products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of products and return results with statistics."""
        processed_products = []
        failed_count = 0
        
        for raw_product in raw_products:
            product_name = raw_product.get('name', 'Unknown')
            
            try:
                # Clean the product data
                processed_product = self.clean_product_data(raw_product)
                
                # Validate using comprehensive validator
                validation_result = self.validator.validate_product(processed_product)
                
                # Handle validation results
                if self.error_handler.handle_validation_error(product_name, validation_result):
                    product = self._create_product_object(processed_product)
                    processed_products.append(product)
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                if not self.error_handler.handle_processing_error(product_name, e):
                    break  # Stop processing if critical error
                continue
        
        return {
            'products': processed_products,
            'failed_count': failed_count
        }
    
    def clean_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize product data using enhanced sanitization.
        
        Args:
            product: Raw product data dictionary
            
        Returns:
            Cleaned product data dictionary
        """
        cleaned = {}
        
        try:
            # Clean and validate name using sanitizer
            cleaned['name'] = self.sanitizer.sanitize_string(
                product.get('name', ''), max_length=200, allow_empty=False
            )
        except Exception:
            cleaned['name'] = self._clean_text(product.get('name', ''))
        
        try:
            # Clean and validate brand using sanitizer
            cleaned['brand'] = self.sanitizer.sanitize_string(
                product.get('brand', ''), max_length=100, allow_empty=True
            )
        except Exception:
            cleaned['brand'] = self._clean_text(product.get('brand', ''))
        
        # Parse prices with enhanced error handling
        current_price_str = product.get('current_price', '')
        original_price_str = product.get('original_price', '')
        
        try:
            cleaned['current_price'] = self.sanitizer.sanitize_float(
                current_price_str, min_value=0.01, max_value=10000.0
            )
        except Exception:
            cleaned['current_price'] = self.price_parser.parse_price(current_price_str)
        
        try:
            cleaned['original_price'] = self.sanitizer.sanitize_float(
                original_price_str, min_value=0.01, max_value=10000.0
            )
        except Exception:
            cleaned['original_price'] = self.price_parser.parse_price(original_price_str)
        
        # Calculate discount percentage
        if cleaned['current_price'] and cleaned['original_price']:
            cleaned['discount_percentage'] = self.price_parser.calculate_discount_percentage(
                cleaned['current_price'], cleaned['original_price']
            )
        else:
            cleaned['discount_percentage'] = None
        
        # Clean availability status
        availability = product.get('availability_status', '').strip()
        cleaned['availability_status'] = self._normalize_availability_status(availability)
        
        # Parse rating with sanitization
        try:
            cleaned['rating'] = self.sanitizer.sanitize_float(
                product.get('rating'), min_value=0.0, max_value=5.0
            )
        except Exception:
            cleaned['rating'] = self._parse_rating(product.get('rating'))
        
        # Parse reviews count with sanitization
        try:
            cleaned['reviews_count'] = self.sanitizer.sanitize_integer(
                product.get('reviews_count'), min_value=0, max_value=100000
            )
        except Exception:
            cleaned['reviews_count'] = self._parse_reviews_count(product.get('reviews_count'))
        
        # Clean URLs with enhanced validation
        try:
            cleaned['product_url'] = self.sanitizer.sanitize_url(product.get('product_url', ''))
        except Exception:
            cleaned['product_url'] = self._clean_url(product.get('product_url', ''))
        
        try:
            cleaned['image_url'] = self.sanitizer.sanitize_url(product.get('image_url', ''))
        except Exception:
            cleaned['image_url'] = self._clean_url(product.get('image_url', ''))
        
        # Clean sale label
        try:
            cleaned['sale_label'] = self.sanitizer.sanitize_string(
                product.get('sale_label', ''), max_length=50, allow_empty=True
            )
        except Exception:
            cleaned['sale_label'] = self._clean_text(product.get('sale_label', ''))
        
        # Add timestamp
        cleaned['timestamp'] = datetime.now()
        
        return cleaned
    
    def validate_product_data(self, product: Dict[str, Any]) -> bool:
        """
        Validate that product data meets minimum requirements.
        
        Args:
            product: Cleaned product data dictionary
            
        Returns:
            True if product data is valid, False otherwise
        """
        # Required fields
        required_fields = ['name', 'current_price', 'product_url']
        
        for field in required_fields:
            if not product.get(field):
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate price is positive
        if product['current_price'] <= 0:
            logger.warning(f"Invalid current price: {product['current_price']}")
            return False
        
        # Validate URL format
        if not self._is_valid_url(product['product_url']):
            logger.warning(f"Invalid product URL: {product['product_url']}")
            return False
        
        # Validate rating range if present
        if product.get('rating') is not None:
            if not (0 <= product['rating'] <= 5):
                logger.warning(f"Invalid rating: {product['rating']}")
                return False
        
        return True
    
    def _create_product_object(self, product_data: Dict[str, Any]) -> Product:
        """Create a Product object from validated data."""
        return Product(
            timestamp=product_data['timestamp'],
            name=product_data['name'],
            brand=product_data['brand'],
            current_price=product_data['current_price'],
            original_price=product_data['original_price'],
            discount_percentage=product_data['discount_percentage'],
            availability_status=product_data['availability_status'],
            rating=product_data['rating'],
            reviews_count=product_data['reviews_count'],
            product_url=product_data['product_url'],
            sale_label=product_data['sale_label'],
            image_url=product_data['image_url']
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text fields."""
        if not text or not isinstance(text, str):
            return ""
        return text.strip().replace('\n', ' ').replace('\r', ' ')
    
    def _normalize_availability_status(self, status: str) -> str:
        """Normalize availability status to standard values."""
        if not status:
            return "Unknown"
        
        status_lower = status.lower()
        if 'sold out' in status_lower or 'out of stock' in status_lower:
            return "Sold out"
        elif 'limited' in status_lower or 'few left' in status_lower:
            return "Limited"
        elif 'available' in status_lower or 'in stock' in status_lower:
            return "Available"
        else:
            return "Available"  # Default assumption
    
    def _parse_rating(self, rating_value: Any) -> Optional[float]:
        """Parse rating value to float."""
        if rating_value is None:
            return None
        
        try:
            rating = float(rating_value)
            return rating if 0 <= rating <= 5 else None
        except (ValueError, TypeError):
            return None
    
    def _parse_reviews_count(self, reviews_value: Any) -> Optional[int]:
        """Parse reviews count to integer."""
        if reviews_value is None:
            return None
        
        try:
            # Handle strings like "123 reviews" or "(45)"
            if isinstance(reviews_value, str):
                # Extract numbers from string
                numbers = re.findall(r'\d+', reviews_value)
                if numbers:
                    return int(numbers[0])
            else:
                return int(reviews_value)
        except (ValueError, TypeError):
            return None
        
        return None
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URL."""
        if not url or not isinstance(url, str):
            return ""
        
        url = url.strip()
        
        # Add base URL if relative
        if url.startswith('/'):
            url = f"https://www.garagegrowngear.com{url}"
        
        return url
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        if not url:
            return False
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for data processing operations."""
        if not self.performance_monitor:
            return {}
        
        return self.performance_monitor.get_performance_summary()
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize performance and return optimization results."""
        if not self.performance_monitor:
            return {}
        
        return self.performance_monitor.optimize_performance()
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive data quality report."""
        if not self.quality_monitor:
            return {}
        
        return self.quality_monitor.get_quality_report()
    
    def get_quality_metrics(self) -> Optional[DataQualityMetrics]:
        """Get the latest quality metrics."""
        if not self.quality_monitor or not self.quality_monitor.historical_metrics:
            return None
        
        return self.quality_monitor.historical_metrics[-1]
    
    def export_quality_report(self, filepath: str, format: str = 'json') -> None:
        """Export quality report to file."""
        if self.quality_monitor:
            self.quality_monitor.export_quality_report(filepath, format)
        else:
            logger.warning("Quality monitoring is not enabled")
    
    def _product_to_dict(self, product: 'Product') -> Dict[str, Any]:
        """Convert Product object to dictionary for quality analysis."""
        return {
            'timestamp': product.timestamp,
            'name': product.name,
            'brand': product.brand,
            'current_price': product.current_price,
            'original_price': product.original_price,
            'discount_percentage': product.discount_percentage,
            'availability_status': product.availability_status,
            'rating': product.rating,
            'reviews_count': product.reviews_count,
            'product_url': product.product_url,
            'sale_label': product.sale_label,
            'image_url': product.image_url
        }