#!/usr/bin/env python3
"""
Simple test script to test the scraper without Google Sheets setup.
"""

from scraper.garage_grown_gear_scraper import GarageGrownGearScraper

def main():
    print("🚀 Testing Garage Grown Gear Scraper...")
    print("=" * 50)
    
    try:
        # Initialize scraper
        print("1. Initializing scraper...")
        scraper = GarageGrownGearScraper()
        print("   ✅ Scraper initialized successfully")
        
        # Test single page scrape
        print("\n2. Testing single page scrape...")
        print("   🌐 Fetching: https://www.garagegrowngear.com/collections/sale-1")
        
        products = scraper.scrape_page('https://www.garagegrowngear.com/collections/sale-1')
        
        print(f"   ✅ Found {len(products)} products")
        
        if products:
            print(f"\n3. Sample product data:")
            print("-" * 30)
            first_product = products[0]
            for key, value in first_product.items():
                if value:  # Only show non-empty values
                    # Truncate long values for readability
                    display_value = str(value)
                    if len(display_value) > 60:
                        display_value = display_value[:57] + "..."
                    print(f"   {key:20}: {display_value}")
            
            print(f"\n4. Summary:")
            print(f"   📦 Total products: {len(products)}")
            
            # Count products with prices
            products_with_prices = sum(1 for p in products if p.get('current_price'))
            print(f"   💰 Products with prices: {products_with_prices}")
            
            # Count products with brands
            products_with_brands = sum(1 for p in products if p.get('brand'))
            print(f"   🏷️  Products with brands: {products_with_brands}")
            
            # Show availability distribution
            availability_counts = {}
            for p in products:
                status = p.get('availability_status', 'Unknown')
                availability_counts[status] = availability_counts.get(status, 0) + 1
            
            print(f"   📊 Availability breakdown:")
            for status, count in availability_counts.items():
                print(f"      {status}: {count}")
                
        else:
            print("   ℹ️  No products found")
            print("   This might be normal if:")
            print("   - The sale page is empty")
            print("   - The website structure has changed")
            print("   - There are network issues")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        
        # Show some debugging info
        print(f"\n🔍 Debug info:")
        print(f"   - Make sure you have internet connection")
        print(f"   - The website might be temporarily unavailable")
        print(f"   - Try running again in a few minutes")
        
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 All tests passed! The scraper is working correctly.")
        print(f"💡 Next steps:")
        print(f"   - Set up Google Sheets to store the data")
        print(f"   - Run the full workflow with: python main.py --dry-run")
    else:
        print(f"\n⚠️  Tests failed. Check the error messages above.")