#!/usr/bin/env python3
"""
Test Google Sheets connection and data writing.
"""

import os
from config import AppConfig  # This loads the .env file
from sheets_integration.sheets_client import SheetsClient, SheetsConfig

def main():
    print("🔍 Testing Google Sheets Connection...")
    print("=" * 50)
    
    try:
        # Initialize sheets client
        print("1. Initializing sheets client...")
        config = SheetsConfig(
            spreadsheet_id=os.getenv('SPREADSHEET_ID'),
            sheet_name='Product_Data'
        )
        client = SheetsClient(config)
        print(f"   ✅ Client initialized with spreadsheet ID: {config.spreadsheet_id}")
        
        # Test authentication
        print("\n2. Testing authentication...")
        client.authenticate()
        print("   ✅ Authentication successful")
        
        # Get spreadsheet info
        print("\n3. Getting spreadsheet info...")
        info = client.get_spreadsheet_info()
        print(f"   📊 Spreadsheet title: {info['title']}")
        print(f"   📋 Available sheets: {info['sheets']}")
        print(f"   🔗 URL: {info['url']}")
        
        # Check if our sheet exists
        print("\n4. Checking if Product_Data sheet exists...")
        sheet_exists = client.sheet_exists('Product_Data')
        print(f"   📋 Product_Data sheet exists: {sheet_exists}")
        
        if not sheet_exists:
            print("   🔧 Creating Product_Data sheet...")
            client.create_sheet_if_not_exists('Product_Data')
            print("   ✅ Sheet created successfully")
        
        # Test writing sample data
        print("\n5. Testing data write...")
        test_data = [
            [
                "2025-08-22T10:45:00",
                "Test Product",
                "Test Brand", 
                "$29.99",
                "$39.99",
                "25%",
                "Available",
                "4.5",
                "123",
                "https://example.com/product",
                "Sale",
                "https://example.com/image.jpg"
            ]
        ]
        
        client.append_data('Product_Data', test_data)
        print("   ✅ Test data written successfully")
        
        print(f"\n✅ All tests passed! Google Sheets integration is working.")
        print(f"🔗 Check your spreadsheet: {info['url']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed:")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        
        # Additional debugging
        print(f"\n🔍 Debug info:")
        print(f"   SPREADSHEET_ID: {os.getenv('SPREADSHEET_ID', 'Not set')}")
        print(f"   GOOGLE_SHEETS_CREDENTIALS: {'Set' if os.getenv('GOOGLE_SHEETS_CREDENTIALS') else 'Not set'}")
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print(f"\n💡 Troubleshooting tips:")
        print(f"   1. Make sure your service account has edit access to the spreadsheet")
        print(f"   2. Check that the spreadsheet ID is correct")
        print(f"   3. Verify the GOOGLE_SHEETS_CREDENTIALS environment variable")
        print(f"   4. Ensure the Google Sheets API is enabled in your project")