"""
Example demonstrating Google Sheets integration with the scraper.

This example shows how to use the SheetsClient to save scraped product data
to a Google Sheet with proper formatting.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sheets_integration.sheets_client import create_sheets_client, ProductDataFormatter


def example_usage():
    """
    Example of how to use the Google Sheets integration.
    
    Note: This requires proper Google Sheets API credentials to be set up.
    """
    
    # Example product data (as would come from the scraper)
    sample_products = [
        {
            'name': 'Patagonia Down Sweater Jacket',
            'brand': 'Patagonia',
            'current_price': 179.99,
            'original_price': 229.99,
            'discount_percentage': 22,
            'availability_status': 'Available',
            'rating': 4.8,
            'reviews_count': 156,
            'product_url': 'https://www.garagegrowngear.com/products/patagonia-down-sweater',
            'sale_label': 'Save 22%',
            'image_url': 'https://example.com/image1.jpg'
        },
        {
            'name': 'Arc\'teryx Beta AR Jacket',
            'brand': 'Arc\'teryx',
            'current_price': 449.99,
            'original_price': 599.99,
            'discount_percentage': 25,
            'availability_status': 'Limited Stock',
            'rating': 4.9,
            'reviews_count': 89,
            'product_url': 'https://www.garagegrowngear.com/products/arcteryx-beta-ar',
            'sale_label': 'Save 25%',
            'image_url': 'https://example.com/image2.jpg'
        },
        {
            'name': 'Black Diamond Spot Headlamp',
            'brand': 'Black Diamond',
            'current_price': 29.99,
            'original_price': 39.99,
            'discount_percentage': 25,
            'availability_status': 'Sold Out',
            'rating': 4.6,
            'reviews_count': 234,
            'product_url': 'https://www.garagegrowngear.com/products/bd-spot-headlamp',
            'sale_label': 'Save 25%',
            'image_url': 'https://example.com/image3.jpg'
        }
    ]
    
    try:
        # Create and authenticate sheets client
        # Note: You need to set GOOGLE_SHEETS_CREDENTIALS and have a valid spreadsheet ID
        spreadsheet_id = os.getenv('SPREADSHEET_ID', 'your_spreadsheet_id_here')
        
        print("Creating Google Sheets client...")
        client = create_sheets_client(spreadsheet_id, 'Product_Data')
        
        print("Getting spreadsheet info...")
        info = client.get_spreadsheet_info()
        print(f"Connected to spreadsheet: {info['title']}")
        print(f"Available sheets: {info['sheets']}")
        
        # Create sheet if it doesn't exist
        sheet_name = 'Product_Data'
        print(f"Setting up sheet: {sheet_name}")
        client.create_sheet_if_not_exists(sheet_name)
        
        # Format product data for sheets
        print("Formatting product data...")
        formatted_data = ProductDataFormatter.format_products_batch(sample_products)
        
        print(f"Sample formatted row: {formatted_data[0]}")
        
        # Append data to sheet
        print("Appending data to sheet...")
        client.append_data(sheet_name, formatted_data)
        
        print(f"Successfully added {len(formatted_data)} products to the sheet!")
        print(f"View your data at: {info['url']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo run this example, you need to:")
        print("1. Set up Google Sheets API credentials")
        print("2. Set GOOGLE_SHEETS_CREDENTIALS environment variable (base64 encoded service account JSON)")
        print("3. Set SPREADSHEET_ID environment variable with your Google Sheets ID")
        print("4. Ensure the service account has edit access to the spreadsheet")


def demonstrate_data_formatting():
    """
    Demonstrate the data formatting capabilities without requiring API access.
    """
    print("\n=== Data Formatting Demo ===")
    
    sample_product = {
        'name': 'Test Product',
        'brand': 'Test Brand',
        'current_price': '$29.99',  # String price
        'original_price': 39.99,    # Numeric price
        'discount_percentage': '25%',  # String percentage
        'availability_status': 'Available',
        'rating': 4.5,
        'reviews_count': 100,
        'product_url': 'http://example.com/product',
        'sale_label': 'Save 25%',
        'image_url': 'http://example.com/image.jpg'
    }
    
    formatted_row = ProductDataFormatter.format_product_row(sample_product)
    
    headers = [
        'Timestamp', 'Product Name', 'Brand', 'Current Price', 'Original Price',
        'Discount %', 'Availability', 'Rating', 'Reviews Count', 'Product URL',
        'Sale Label', 'Image URL'
    ]
    
    print("Headers:")
    for i, header in enumerate(headers):
        print(f"  {i+1:2d}. {header}")
    
    print("\nFormatted data row:")
    for i, value in enumerate(formatted_row):
        print(f"  {i+1:2d}. {value} ({type(value).__name__})")
    
    print("\nNote how:")
    print("- String price '$29.99' was converted to float 29.99")
    print("- Percentage '25%' was converted to decimal 0.25")
    print("- Timestamp was automatically added")


if __name__ == "__main__":
    print("Google Sheets Integration Example")
    print("=" * 40)
    
    # Always run the formatting demo
    demonstrate_data_formatting()
    
    # Only run the API example if credentials are available
    if os.getenv('GOOGLE_SHEETS_CREDENTIALS') and os.getenv('SPREADSHEET_ID'):
        print("\n" + "=" * 40)
        example_usage()
    else:
        print("\n" + "=" * 40)
        print("Skipping API example - credentials not configured")
        print("Set GOOGLE_SHEETS_CREDENTIALS and SPREADSHEET_ID to test API integration")