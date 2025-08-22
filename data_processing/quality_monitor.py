"""
Data quality monitoring and reporting module.

This module provides comprehensive data quality monitoring, validation,
and reporting capabilities for scraped product data.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import json

logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """Data class for storing data quality metrics."""
    timestamp: datetime
    total_products: int = 0
    valid_products: int = 0
    invalid_products: int = 0
    
    # Field completeness metrics
    missing_names: int = 0
    missing_prices: int = 0
    missing_urls: int = 0
    missing_brands: int = 0
    missing_availability: int = 0
    
    # Data validity metrics
    invalid_prices: int = 0
    invalid_urls: int = 0
    invalid_ratings: int = 0
    invalid_discounts: int = 0
    
    # Data consistency metrics
    price_inconsistencies: int = 0
    duplicate_products: int = 0
    
    # Summary statistics
    avg_price: Optional[float] = None
    price_range: Optional[Dict[str, float]] = None
    avg_discount: Optional[float] = None
    availability_distribution: Dict[str, int] = field(default_factory=dict)
    brand_distribution: Dict[str, int] = field(default_factory=dict)
    
    @property
    def completeness_rate(self) -> float:
        """Calculate overall data completeness rate."""
        if self.total_products == 0:
            return 0.0
        
        total_fields = self.total_products * 5  # 5 key fields
        missing_fields = (self.missing_names + self.missing_prices + 
                         self.missing_urls + self.missing_brands + 
                         self.missing_availability)
        
        return ((total_fields - missing_fields) / total_fields) * 100
    
    @property
    def validity_rate(self) -> float:
        """Calculate data validity rate."""
        if self.total_products == 0:
            return 0.0
        
        return (self.valid_products / self.total_products) * 100
    
    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        completeness_weight = 0.4
        validity_weight = 0.4
        consistency_weight = 0.2
        
        completeness_score = self.completeness_rate
        validity_score = self.validity_rate
        
        # Consistency score (penalize duplicates and inconsistencies)
        consistency_issues = self.duplicate_products + self.price_inconsistencies
        consistency_penalty = min(consistency_issues * 2, 50)  # Max 50% penalty
        consistency_score = max(0, 100 - consistency_penalty)
        
        return (completeness_score * completeness_weight + 
                validity_score * validity_weight + 
                consistency_score * consistency_weight)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_products': self.total_products,
            'valid_products': self.valid_products,
            'invalid_products': self.invalid_products,
            'completeness_rate': self.completeness_rate,
            'validity_rate': self.validity_rate,
            'quality_score': self.quality_score,
            'field_completeness': {
                'missing_names': self.missing_names,
                'missing_prices': self.missing_prices,
                'missing_urls': self.missing_urls,
                'missing_brands': self.missing_brands,
                'missing_availability': self.missing_availability
            },
            'data_validity': {
                'invalid_prices': self.invalid_prices,
                'invalid_urls': self.invalid_urls,
                'invalid_ratings': self.invalid_ratings,
                'invalid_discounts': self.invalid_discounts
            },
            'data_consistency': {
                'price_inconsistencies': self.price_inconsistencies,
                'duplicate_products': self.duplicate_products
            },
            'summary_statistics': {
                'avg_price': self.avg_price,
                'price_range': self.price_range,
                'avg_discount': self.avg_discount,
                'availability_distribution': self.availability_distribution,
                'brand_distribution': self.brand_distribution
            }
        }


@dataclass
class DataQualityAlert:
    """Data class for data quality alerts."""
    timestamp: datetime
    alert_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'details': self.details
        }


class DataQualityMonitor:
    """Comprehensive data quality monitoring and reporting system."""
    
    def __init__(self, alert_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize data quality monitor.
        
        Args:
            alert_thresholds: Dictionary of alert thresholds for different metrics
        """
        self.alert_thresholds = alert_thresholds or {
            'completeness_rate': 90.0,  # Alert if completeness < 90%
            'validity_rate': 95.0,      # Alert if validity < 95%
            'quality_score': 85.0,      # Alert if quality score < 85%
            'duplicate_rate': 5.0,      # Alert if duplicates > 5%
            'missing_price_rate': 10.0, # Alert if missing prices > 10%
            'invalid_price_rate': 5.0   # Alert if invalid prices > 5%
        }
        
        self.historical_metrics = []
        self.alerts = []
        self.max_history_size = 100
        
    def analyze_data_quality(self, products: List[Dict[str, Any]]) -> DataQualityMetrics:
        """
        Analyze data quality of a list of products.
        
        Args:
            products: List of product dictionaries to analyze
            
        Returns:
            DataQualityMetrics object with comprehensive quality analysis
        """
        metrics = DataQualityMetrics(timestamp=datetime.now())
        
        if not products:
            return metrics
        
        metrics.total_products = len(products)
        
        # Track various quality aspects
        prices = []
        discounts = []
        seen_products = set()
        duplicate_keys = set()
        
        for product in products:
            # Check completeness
            self._check_field_completeness(product, metrics)
            
            # Check validity
            is_valid = self._check_data_validity(product, metrics, prices, discounts)
            
            if is_valid:
                metrics.valid_products += 1
            else:
                metrics.invalid_products += 1
            
            # Check for duplicates
            product_key = self._generate_product_key(product)
            if product_key in seen_products:
                duplicate_keys.add(product_key)
                metrics.duplicate_products += 1
            else:
                seen_products.add(product_key)
            
            # Collect distribution data
            self._collect_distribution_data(product, metrics)
        
        # Calculate summary statistics
        self._calculate_summary_statistics(prices, discounts, metrics)
        
        # Check for price inconsistencies
        metrics.price_inconsistencies = self._check_price_inconsistencies(products)
        
        # Store metrics in history
        self.historical_metrics.append(metrics)
        if len(self.historical_metrics) > self.max_history_size:
            self.historical_metrics = self.historical_metrics[-self.max_history_size:]
        
        # Generate alerts based on metrics
        self._generate_quality_alerts(metrics)
        
        return metrics
    
    def _check_field_completeness(self, product: Dict[str, Any], 
                                 metrics: DataQualityMetrics) -> None:
        """Check completeness of required fields."""
        if not product.get('name') or not str(product.get('name')).strip():
            metrics.missing_names += 1
        
        if not product.get('current_price') or product.get('current_price') == 0:
            metrics.missing_prices += 1
        
        if not product.get('product_url') or not str(product.get('product_url')).strip():
            metrics.missing_urls += 1
        
        if not product.get('brand') or not str(product.get('brand')).strip():
            metrics.missing_brands += 1
        
        if not product.get('availability_status') or not str(product.get('availability_status')).strip():
            metrics.missing_availability += 1
    
    def _check_data_validity(self, product: Dict[str, Any], 
                           metrics: DataQualityMetrics,
                           prices: List[float], 
                           discounts: List[float]) -> bool:
        """Check validity of data values."""
        is_valid = True
        
        # Check price validity
        current_price = product.get('current_price')
        if current_price is not None:
            try:
                price_float = float(current_price)
                if price_float <= 0 or price_float > 10000:  # Reasonable bounds
                    metrics.invalid_prices += 1
                    is_valid = False
                else:
                    prices.append(price_float)
            except (ValueError, TypeError):
                metrics.invalid_prices += 1
                is_valid = False
        
        # Check URL validity
        product_url = product.get('product_url', '')
        if product_url and not self._is_valid_url(product_url):
            metrics.invalid_urls += 1
            is_valid = False
        
        # Check rating validity
        rating = product.get('rating')
        if rating is not None:
            try:
                rating_float = float(rating)
                if rating_float < 0 or rating_float > 5:
                    metrics.invalid_ratings += 1
                    is_valid = False
            except (ValueError, TypeError):
                metrics.invalid_ratings += 1
                is_valid = False
        
        # Check discount validity
        discount = product.get('discount_percentage')
        if discount is not None:
            try:
                discount_float = float(discount)
                if discount_float < 0 or discount_float > 100:
                    metrics.invalid_discounts += 1
                    is_valid = False
                else:
                    discounts.append(discount_float)
            except (ValueError, TypeError):
                metrics.invalid_discounts += 1
                is_valid = False
        
        return is_valid
    
    def _generate_product_key(self, product: Dict[str, Any]) -> str:
        """Generate a unique key for duplicate detection."""
        name = str(product.get('name', '')).strip().lower()
        brand = str(product.get('brand', '')).strip().lower()
        return f"{brand}:{name}"
    
    def _collect_distribution_data(self, product: Dict[str, Any], 
                                  metrics: DataQualityMetrics) -> None:
        """Collect data for distribution analysis."""
        # Availability distribution
        availability = product.get('availability_status', 'Unknown')
        if availability not in metrics.availability_distribution:
            metrics.availability_distribution[availability] = 0
        metrics.availability_distribution[availability] += 1
        
        # Brand distribution
        brand = product.get('brand', 'Unknown')
        if brand not in metrics.brand_distribution:
            metrics.brand_distribution[brand] = 0
        metrics.brand_distribution[brand] += 1
    
    def _calculate_summary_statistics(self, prices: List[float], 
                                    discounts: List[float],
                                    metrics: DataQualityMetrics) -> None:
        """Calculate summary statistics from collected data."""
        if prices:
            metrics.avg_price = statistics.mean(prices)
            metrics.price_range = {
                'min': min(prices),
                'max': max(prices),
                'median': statistics.median(prices)
            }
        
        if discounts:
            metrics.avg_discount = statistics.mean(discounts)
    
    def _check_price_inconsistencies(self, products: List[Dict[str, Any]]) -> int:
        """Check for price inconsistencies (current > original price)."""
        inconsistencies = 0
        
        for product in products:
            current_price = product.get('current_price')
            original_price = product.get('original_price')
            
            if (current_price is not None and original_price is not None and
                current_price > original_price):
                inconsistencies += 1
        
        return inconsistencies
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
    
    def _generate_quality_alerts(self, metrics: DataQualityMetrics) -> None:
        """Generate alerts based on quality metrics."""
        alerts = []
        
        # Completeness alerts
        if metrics.completeness_rate < self.alert_thresholds['completeness_rate']:
            alerts.append(DataQualityAlert(
                timestamp=datetime.now(),
                alert_type='completeness',
                severity='medium' if metrics.completeness_rate > 80 else 'high',
                message=f"Data completeness rate is {metrics.completeness_rate:.1f}%, below threshold of {self.alert_thresholds['completeness_rate']}%",
                details={'completeness_rate': metrics.completeness_rate}
            ))
        
        # Validity alerts
        if metrics.validity_rate < self.alert_thresholds['validity_rate']:
            alerts.append(DataQualityAlert(
                timestamp=datetime.now(),
                alert_type='validity',
                severity='high' if metrics.validity_rate < 90 else 'medium',
                message=f"Data validity rate is {metrics.validity_rate:.1f}%, below threshold of {self.alert_thresholds['validity_rate']}%",
                details={'validity_rate': metrics.validity_rate}
            ))
        
        # Quality score alerts
        if metrics.quality_score < self.alert_thresholds['quality_score']:
            alerts.append(DataQualityAlert(
                timestamp=datetime.now(),
                alert_type='quality_score',
                severity='critical' if metrics.quality_score < 70 else 'high',
                message=f"Overall quality score is {metrics.quality_score:.1f}, below threshold of {self.alert_thresholds['quality_score']}",
                details={'quality_score': metrics.quality_score}
            ))
        
        # Duplicate alerts
        if metrics.total_products > 0:
            duplicate_rate = (metrics.duplicate_products / metrics.total_products) * 100
            if duplicate_rate > self.alert_thresholds['duplicate_rate']:
                alerts.append(DataQualityAlert(
                    timestamp=datetime.now(),
                    alert_type='duplicates',
                    severity='medium',
                    message=f"Duplicate rate is {duplicate_rate:.1f}%, above threshold of {self.alert_thresholds['duplicate_rate']}%",
                    details={'duplicate_rate': duplicate_rate, 'duplicate_count': metrics.duplicate_products}
                ))
        
        # Missing price alerts
        if metrics.total_products > 0:
            missing_price_rate = (metrics.missing_prices / metrics.total_products) * 100
            if missing_price_rate > self.alert_thresholds['missing_price_rate']:
                alerts.append(DataQualityAlert(
                    timestamp=datetime.now(),
                    alert_type='missing_prices',
                    severity='high',
                    message=f"Missing price rate is {missing_price_rate:.1f}%, above threshold of {self.alert_thresholds['missing_price_rate']}%",
                    details={'missing_price_rate': missing_price_rate, 'missing_count': metrics.missing_prices}
                ))
        
        # Add alerts to history
        self.alerts.extend(alerts)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]
    
    def get_quality_report(self, include_history: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive quality report.
        
        Args:
            include_history: Whether to include historical metrics
            
        Returns:
            Dictionary containing quality report
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'current_metrics': None,
            'recent_alerts': [alert.to_dict() for alert in self.alerts[-10:]],
            'alert_summary': self._get_alert_summary()
        }
        
        if self.historical_metrics:
            report['current_metrics'] = self.historical_metrics[-1].to_dict()
        
        if include_history and len(self.historical_metrics) > 1:
            report['historical_trends'] = self._calculate_trends()
            report['quality_trend'] = self._get_quality_trend()
        
        return report
    
    def _get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of recent alerts."""
        if not self.alerts:
            return {'total_alerts': 0}
        
        alert_counts = Counter(alert.alert_type for alert in self.alerts)
        severity_counts = Counter(alert.severity for alert in self.alerts)
        
        return {
            'total_alerts': len(self.alerts),
            'by_type': dict(alert_counts),
            'by_severity': dict(severity_counts),
            'most_recent': self.alerts[-1].to_dict() if self.alerts else None
        }
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate trends from historical metrics."""
        if len(self.historical_metrics) < 2:
            return {}
        
        recent_metrics = self.historical_metrics[-5:]  # Last 5 runs
        
        completeness_rates = [m.completeness_rate for m in recent_metrics]
        validity_rates = [m.validity_rate for m in recent_metrics]
        quality_scores = [m.quality_score for m in recent_metrics]
        
        return {
            'completeness_trend': self._calculate_trend(completeness_rates),
            'validity_trend': self._calculate_trend(validity_rates),
            'quality_trend': self._calculate_trend(quality_scores),
            'avg_completeness': statistics.mean(completeness_rates),
            'avg_validity': statistics.mean(validity_rates),
            'avg_quality_score': statistics.mean(quality_scores)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple trend calculation
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        diff = second_half - first_half
        
        if abs(diff) < 1.0:  # Less than 1% change
            return 'stable'
        elif diff > 0:
            return 'improving'
        else:
            return 'declining'
    
    def _get_quality_trend(self) -> Dict[str, Any]:
        """Get overall quality trend assessment."""
        if len(self.historical_metrics) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_scores = [m.quality_score for m in self.historical_metrics[-5:]]
        trend = self._calculate_trend(recent_scores)
        
        current_score = recent_scores[-1]
        avg_score = statistics.mean(recent_scores)
        
        assessment = 'good'
        if avg_score < 70:
            assessment = 'poor'
        elif avg_score < 85:
            assessment = 'fair'
        
        return {
            'trend': trend,
            'current_score': current_score,
            'average_score': avg_score,
            'assessment': assessment,
            'recommendation': self._get_quality_recommendation(trend, avg_score)
        }
    
    def _get_quality_recommendation(self, trend: str, avg_score: float) -> str:
        """Get quality improvement recommendation."""
        if avg_score >= 90 and trend in ['stable', 'improving']:
            return "Data quality is excellent. Continue current practices."
        elif avg_score >= 85:
            return "Data quality is good. Monitor for any declining trends."
        elif avg_score >= 70:
            return "Data quality needs improvement. Focus on completeness and validation."
        else:
            return "Data quality is poor. Immediate attention required for data collection and validation processes."
    
    def export_quality_report(self, filepath: str, format: str = 'json') -> None:
        """
        Export quality report to file.
        
        Args:
            filepath: Path to save the report
            format: Export format ('json' or 'csv')
        """
        report = self.get_quality_report()
        
        if format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format.lower() == 'csv':
            # Export metrics to CSV
            import csv
            with open(filepath, 'w', newline='') as f:
                if self.historical_metrics:
                    writer = csv.DictWriter(f, fieldnames=self.historical_metrics[0].to_dict().keys())
                    writer.writeheader()
                    for metrics in self.historical_metrics:
                        writer.writerow(metrics.to_dict())
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Quality report exported to {filepath}")