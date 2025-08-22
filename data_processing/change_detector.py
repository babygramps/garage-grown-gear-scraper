"""
Change detection and notification system for the Garage Grown Gear scraper.

This module provides functionality to detect new products, price changes,
and availability changes, and generate notifications for significant events.
"""

import json
import os
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

from .product_data_processor import Product


@dataclass
class ProductChange:
    """Represents a change detected in a product."""
    product_url: str
    product_name: str
    change_type: str  # 'new_product', 'price_drop', 'price_increase', 'availability_change', 'sold_out'
    old_value: Any
    new_value: Any
    change_percentage: Optional[float] = None
    timestamp: str = None
    priority: str = 'normal'  # 'low', 'normal', 'high', 'critical'
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class NotificationSummary:
    """Summary of changes for notification purposes."""
    timestamp: str
    total_products: int
    new_products: int
    price_drops: int
    significant_price_drops: int
    sold_out_products: int
    back_in_stock: int
    priority_deals: List[ProductChange]
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class ProductHistoryManager:
    """Manages historical product data for change detection."""
    
    def __init__(self, history_file: str = "product_history.json"):
        self.history_file = Path(history_file)
        self.history = self._load_history()
        self.logger = logging.getLogger(__name__)
    
    def _load_history(self) -> Dict[str, Dict[str, Any]]:
        """Load product history from file."""
        if not self.history_file.exists():
            return {}
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Failed to load history file: {e}")
            return {}
    
    def _save_history(self) -> None:
        """Save product history to file."""
        try:
            # Ensure directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Failed to save history file: {e}")
    
    def get_product_history(self, product_url: str) -> Optional[Dict[str, Any]]:
        """Get historical data for a specific product."""
        return self.history.get(product_url)
    
    def update_product_history(self, product: Product) -> None:
        """Update historical data for a product."""
        product_data = {
            'name': product.name,
            'brand': product.brand,
            'current_price': product.current_price,
            'original_price': product.original_price,
            'discount_percentage': product.discount_percentage,
            'availability_status': product.availability_status,
            'rating': product.rating,
            'reviews_count': product.reviews_count,
            'last_seen': product.timestamp.isoformat(),
            'sale_label': product.sale_label
        }
        
        self.history[product.product_url] = product_data
    
    def save_current_state(self) -> None:
        """Save current state to file."""
        self._save_history()
    
    def cleanup_old_entries(self, days_to_keep: int = 30) -> None:
        """Remove entries older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        urls_to_remove = []
        for url, data in self.history.items():
            try:
                last_seen = datetime.fromisoformat(data.get('last_seen', ''))
                if last_seen < cutoff_date:
                    urls_to_remove.append(url)
            except (ValueError, TypeError):
                # Remove entries with invalid dates
                urls_to_remove.append(url)
        
        for url in urls_to_remove:
            del self.history[url]
        
        if urls_to_remove:
            self.logger.info(f"Cleaned up {len(urls_to_remove)} old history entries")


class ChangeDetector:
    """Detects changes in product data compared to historical data."""
    
    def __init__(self, price_drop_threshold: float = 20.0, history_manager: ProductHistoryManager = None):
        self.price_drop_threshold = price_drop_threshold
        self.history_manager = history_manager or ProductHistoryManager()
        self.logger = logging.getLogger(__name__)
    
    def detect_changes(self, current_products: List[Product]) -> List[ProductChange]:
        """
        Detect changes in current products compared to historical data.
        
        Args:
            current_products: List of current product data
            
        Returns:
            List of detected changes
        """
        changes = []
        current_urls = {product.product_url for product in current_products}
        
        for product in current_products:
            historical_data = self.history_manager.get_product_history(product.product_url)
            
            if historical_data is None:
                # New product
                changes.append(ProductChange(
                    product_url=product.product_url,
                    product_name=product.name,
                    change_type='new_product',
                    old_value=None,
                    new_value=product.current_price,
                    priority='normal'
                ))
            else:
                # Check for changes in existing product
                product_changes = self._detect_product_changes(product, historical_data)
                changes.extend(product_changes)
            
            # Update history with current data
            self.history_manager.update_product_history(product)
        
        # Save updated history
        self.history_manager.save_current_state()
        
        self.logger.info(f"Detected {len(changes)} changes across {len(current_products)} products")
        return changes
    
    def _detect_product_changes(self, current: Product, historical: Dict[str, Any]) -> List[ProductChange]:
        """Detect changes in a single product."""
        changes = []
        
        # Price changes
        old_price = historical.get('current_price')
        if old_price and current.current_price and old_price != current.current_price:
            price_change_pct = ((current.current_price - old_price) / old_price) * 100
            
            if current.current_price < old_price:
                # Price drop
                priority = 'high' if abs(price_change_pct) >= self.price_drop_threshold else 'normal'
                changes.append(ProductChange(
                    product_url=current.product_url,
                    product_name=current.name,
                    change_type='price_drop',
                    old_value=old_price,
                    new_value=current.current_price,
                    change_percentage=abs(price_change_pct),
                    priority=priority
                ))
            else:
                # Price increase
                changes.append(ProductChange(
                    product_url=current.product_url,
                    product_name=current.name,
                    change_type='price_increase',
                    old_value=old_price,
                    new_value=current.current_price,
                    change_percentage=price_change_pct,
                    priority='low'
                ))
        
        # Availability changes
        old_availability = historical.get('availability_status')
        if old_availability and old_availability != current.availability_status:
            if current.availability_status == 'Sold out' and old_availability != 'Sold out':
                changes.append(ProductChange(
                    product_url=current.product_url,
                    product_name=current.name,
                    change_type='sold_out',
                    old_value=old_availability,
                    new_value=current.availability_status,
                    priority='normal'
                ))
            elif old_availability == 'Sold out' and current.availability_status != 'Sold out':
                changes.append(ProductChange(
                    product_url=current.product_url,
                    product_name=current.name,
                    change_type='back_in_stock',
                    old_value=old_availability,
                    new_value=current.availability_status,
                    priority='high'
                ))
            else:
                changes.append(ProductChange(
                    product_url=current.product_url,
                    product_name=current.name,
                    change_type='availability_change',
                    old_value=old_availability,
                    new_value=current.availability_status,
                    priority='low'
                ))
        
        return changes
    
    def generate_summary(self, changes: List[ProductChange], total_products: int) -> NotificationSummary:
        """Generate a summary of changes for notifications."""
        new_products = len([c for c in changes if c.change_type == 'new_product'])
        price_drops = len([c for c in changes if c.change_type == 'price_drop'])
        significant_price_drops = len([
            c for c in changes 
            if c.change_type == 'price_drop' and c.priority in ['high', 'critical']
        ])
        sold_out = len([c for c in changes if c.change_type == 'sold_out'])
        back_in_stock = len([c for c in changes if c.change_type == 'back_in_stock'])
        
        # Priority deals (high priority price drops and back in stock)
        priority_deals = [
            c for c in changes 
            if c.priority in ['high', 'critical'] and c.change_type in ['price_drop', 'back_in_stock']
        ]
        
        return NotificationSummary(
            timestamp=datetime.now().isoformat(),
            total_products=total_products,
            new_products=new_products,
            price_drops=price_drops,
            significant_price_drops=significant_price_drops,
            sold_out_products=sold_out,
            back_in_stock=back_in_stock,
            priority_deals=priority_deals
        )


class NotificationManager:
    """Manages notifications for detected changes."""
    
    def __init__(self, webhook_url: Optional[str] = None, enable_notifications: bool = False, price_drop_threshold: float = 20.0):
        self.webhook_url = webhook_url
        self.enable_notifications = enable_notifications
        self.price_drop_threshold = price_drop_threshold
        self.logger = logging.getLogger(__name__)
    
    def should_send_notification(self, summary: NotificationSummary) -> bool:
        """Determine if a notification should be sent based on the summary."""
        if not self.enable_notifications:
            return False
        
        # Send notification if there are priority deals or significant changes
        return (
            len(summary.priority_deals) > 0 or
            summary.significant_price_drops > 0 or
            summary.back_in_stock > 0 or
            summary.new_products > 5  # Many new products
        )
    
    def create_notification_message(self, summary: NotificationSummary) -> str:
        """Create a formatted notification message."""
        message_parts = [
            f"🛍️ Garage Grown Gear Sale Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"📊 Summary:",
            f"• Total products monitored: {summary.total_products}",
        ]
        
        if summary.new_products > 0:
            message_parts.append(f"• 🆕 New products: {summary.new_products}")
        
        if summary.price_drops > 0:
            message_parts.append(f"• 💰 Price drops: {summary.price_drops}")
        
        if summary.significant_price_drops > 0:
            message_parts.append(f"• 🔥 Significant price drops (>{self.price_drop_threshold}%): {summary.significant_price_drops}")
        
        if summary.back_in_stock > 0:
            message_parts.append(f"• ✅ Back in stock: {summary.back_in_stock}")
        
        if summary.sold_out_products > 0:
            message_parts.append(f"• ❌ Sold out: {summary.sold_out_products}")
        
        # Add priority deals
        if summary.priority_deals:
            message_parts.extend(["", "🎯 Priority Deals:"])
            for deal in summary.priority_deals[:5]:  # Limit to top 5
                if deal.change_type == 'price_drop':
                    message_parts.append(
                        f"• 💸 {deal.product_name}: ${deal.old_value:.2f} → ${deal.new_value:.2f} "
                        f"(-{deal.change_percentage:.1f}%)"
                    )
                elif deal.change_type == 'back_in_stock':
                    message_parts.append(f"• 🔄 {deal.product_name}: Back in stock!")
        
        return "\n".join(message_parts)
    
    def send_notification(self, summary: NotificationSummary) -> bool:
        """Send notification if conditions are met."""
        if not self.should_send_notification(summary):
            self.logger.debug("No notification needed")
            return False
        
        message = self.create_notification_message(summary)
        
        # Log the notification (always)
        self.logger.info("Notification generated:", extra={'notification_message': message})
        
        # Send webhook notification if configured
        if self.webhook_url:
            return self._send_webhook_notification(message)
        
        return True
    
    def _send_webhook_notification(self, message: str) -> bool:
        """Send notification via webhook."""
        try:
            import requests
            
            payload = {
                'text': message,
                'username': 'Garage Grown Gear Bot',
                'icon_emoji': ':shopping_bags:'
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("Webhook notification sent successfully")
                return True
            else:
                self.logger.error(f"Webhook notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            return False


class ChangeDetectionOrchestrator:
    """Orchestrates the complete change detection and notification workflow."""
    
    def __init__(
        self,
        price_drop_threshold: float = 20.0,
        webhook_url: Optional[str] = None,
        enable_notifications: bool = False,
        history_file: str = "product_history.json"
    ):
        self.history_manager = ProductHistoryManager(history_file)
        self.change_detector = ChangeDetector(price_drop_threshold, self.history_manager)
        self.notification_manager = NotificationManager(webhook_url, enable_notifications, price_drop_threshold)
        self.logger = logging.getLogger(__name__)
    
    def process_products_and_notify(self, products: List[Product]) -> Dict[str, Any]:
        """
        Process products for changes and send notifications if needed.
        
        Args:
            products: List of current products
            
        Returns:
            Dictionary with processing results and statistics
        """
        self.logger.info(f"Processing {len(products)} products for changes...")
        
        # Detect changes
        changes = self.change_detector.detect_changes(products)
        
        # Generate summary
        summary = self.change_detector.generate_summary(changes, len(products))
        
        # Send notification if needed
        notification_sent = self.notification_manager.send_notification(summary)
        
        # Clean up old history entries
        self.history_manager.cleanup_old_entries()
        
        results = {
            'total_products': len(products),
            'changes_detected': len(changes),
            'new_products': summary.new_products,
            'price_drops': summary.price_drops,
            'significant_price_drops': summary.significant_price_drops,
            'sold_out_products': summary.sold_out_products,
            'back_in_stock': summary.back_in_stock,
            'priority_deals': len(summary.priority_deals),
            'notification_sent': notification_sent,
            'changes': [change.to_dict() for change in changes]
        }
        
        self.logger.info("Change detection completed", extra=results)
        return results