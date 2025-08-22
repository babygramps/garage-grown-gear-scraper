#!/usr/bin/env python3
"""
Example usage of the Garage Grown Gear scraper with change detection.

This example demonstrates how to use the scraper with all features enabled.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AppConfig
from error_handling.logging_config import setup_logging
from data_processing.change_detector import ChangeDetectionOrchestrator
from data_processing.product_data_processor import Product


def create_sample_products():
    """Create sample product data for demonstration."""
    return [
        Product(
            timestamp=datetime.now(),
            name="Sample Hiking Boots",
            brand="OutdoorBrand",
            current_price=89.99,
            original_price=129.99,
            discount_percentage=30.8,
            availability_status="Available",
            rating=4.5,
            reviews_count=127,
            product_url="https://example.com/product1",
            sale_label="Save 31%",
            image_url="https://example.com/image1.jpg"
        ),
        Product(
            timestamp=datetime.now(),
            name="Camping Tent 2-Person",
            brand="CampGear",
            current_price=149.99,
            original_price=199.99,
            discount_percentage=25.0,
            availability_status="Limited",
            rating=4.2,
            reviews_count=89,
            product_url="https://example.com/product2",
            sale_label="Save 25%",
            image_url="https://example.com/image2.jpg"
        ),
        Product(
            timestamp=datetime.now(),
            name="Waterproof Jacket",
            brand="WeatherPro",
            current_price=79.99,
            original_price=119.99,
            discount_percentage=33.3,
            availability_status="Sold out",
            rating=4.7,
            reviews_count=203,
            product_url="https://example.com/product3",
            sale_label="Save 33%",
            image_url="https://example.com/image3.jpg"
        )
    ]


def demonstrate_change_detection():
    """Demonstrate the change detection functionality."""
    print("🔍 Garage Grown Gear Scraper - Change Detection Demo")
    print("=" * 60)
    
    # Set up logging
    logger = setup_logging(level='INFO', console=True, structured=False)
    
    # Create change detection orchestrator
    change_detector = ChangeDetectionOrchestrator(
        price_drop_threshold=20.0,
        webhook_url=None,  # No webhook for demo
        enable_notifications=True,
        history_file="examples/demo_history.json"
    )
    
    # First run - establish baseline
    print("\n📊 First Run - Establishing Baseline")
    print("-" * 40)
    
    sample_products = create_sample_products()
    results1 = change_detector.process_products_and_notify(sample_products)
    
    print(f"Products processed: {results1['total_products']}")
    print(f"New products detected: {results1['new_products']}")
    print(f"Changes detected: {results1['changes_detected']}")
    
    # Second run - simulate price changes
    print("\n📈 Second Run - Simulating Price Changes")
    print("-" * 40)
    
    # Modify products to simulate changes
    modified_products = create_sample_products()
    
    # Price drop on hiking boots
    modified_products[0].current_price = 69.99  # Significant drop
    modified_products[0].discount_percentage = 46.2
    
    # Tent back in stock
    modified_products[1].availability_status = "Available"
    
    # Jacket price increase
    modified_products[2].current_price = 89.99
    modified_products[2].availability_status = "Available"  # Back in stock too
    
    results2 = change_detector.process_products_and_notify(modified_products)
    
    print(f"Products processed: {results2['total_products']}")
    print(f"Changes detected: {results2['changes_detected']}")
    print(f"Price drops: {results2['price_drops']}")
    print(f"Significant price drops: {results2['significant_price_drops']}")
    print(f"Back in stock: {results2['back_in_stock']}")
    print(f"Priority deals: {results2['priority_deals']}")
    print(f"Notification would be sent: {results2['notification_sent']}")
    
    # Show detailed changes
    if results2['changes']:
        print("\n🔄 Detailed Changes:")
        print("-" * 20)
        for change in results2['changes']:
            change_type = change['change_type'].replace('_', ' ').title()
            print(f"• {change_type}: {change['product_name']}")
            if change['old_value'] and change['new_value']:
                if 'price' in change['change_type']:
                    print(f"  ${change['old_value']:.2f} → ${change['new_value']:.2f}")
                    if change.get('change_percentage'):
                        print(f"  ({change['change_percentage']:.1f}% change)")
                else:
                    print(f"  {change['old_value']} → {change['new_value']}")
            print(f"  Priority: {change['priority']}")
            print()
    
    print("✅ Demo completed successfully!")
    print("\nTo run the actual scraper:")
    print("python main.py --dry-run --enable-notifications --price-drop-threshold 20")


def demonstrate_cli_usage():
    """Show example CLI usage commands."""
    print("\n🚀 Example CLI Usage")
    print("=" * 60)
    
    examples = [
        {
            'title': 'Basic dry run',
            'command': 'python main.py --dry-run --spreadsheet-id YOUR_SHEET_ID'
        },
        {
            'title': 'Full run with notifications',
            'command': 'python main.py --enable-notifications --webhook-url YOUR_WEBHOOK_URL --price-drop-threshold 15'
        },
        {
            'title': 'Debug mode with custom settings',
            'command': 'python main.py --log-level DEBUG --max-retries 5 --no-stealth'
        },
        {
            'title': 'Custom history file location',
            'command': 'python main.py --history-file /path/to/custom/history.json'
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        print(f"  {example['command']}")
    
    print("\n📋 Required Environment Variables:")
    print("  SPREADSHEET_ID - Google Sheets spreadsheet ID")
    print("  GOOGLE_SHEETS_CREDENTIALS - Base64 encoded service account JSON")
    print("\n📋 Optional Environment Variables:")
    print("  WEBHOOK_URL - Slack/Discord webhook for notifications")
    print("  LOG_LEVEL - Logging level (DEBUG, INFO, WARNING, ERROR)")
    print("  ENABLE_NOTIFICATIONS - Enable change notifications (true/false)")


if __name__ == "__main__":
    try:
        demonstrate_change_detection()
        demonstrate_cli_usage()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()