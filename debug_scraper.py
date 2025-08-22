#!/usr/bin/env python3
"""
Debug script to inspect the actual HTML structure of the page.
"""

from scraper.garage_grown_gear_scraper import GarageGrownGearScraper

def main():
    print("🔍 Debugging scraper - inspecting page structure...")
    print("=" * 60)
    
    try:
        scraper = GarageGrownGearScraper()
        
        # Make a request to get the page
        print("1. Fetching page...")
        page = scraper._make_request('https://www.garagegrowngear.com/collections/sale-1')
        
        if not page:
            print("❌ Failed to fetch page")
            return False
        
        print("✅ Page fetched successfully")
        print(f"   Status: {page.status}")
        
        # Check current selectors
        print(f"\n2. Testing current selectors...")
        selectors = scraper.SELECTORS
        
        for name, selector in selectors.items():
            elements = page.css(selector)
            print(f"   {name:20}: '{selector}' -> {len(elements)} elements")
        
        # Look for common product container patterns
        print(f"\n3. Looking for common product patterns...")
        common_selectors = [
            '.product',
            '.product-item',
            '.product-card',
            '.grid-item',
            '[data-product]',
            '.collection-item',
            '.product-tile',
            '.item',
            '.card'
        ]
        
        for selector in common_selectors:
            elements = page.css(selector)
            if len(elements) > 0:
                print(f"   ✅ Found {len(elements)} elements with: '{selector}'")
            else:
                print(f"   ❌ No elements found with: '{selector}'")
        
        # Check page title and basic structure
        print(f"\n4. Page information...")
        title_element = page.css_first('title')
        if title_element:
            print(f"   Page title: {title_element.get_all_text().strip()}")
        
        # Look for any text that might indicate products or sale items
        print(f"\n5. Looking for sale/product related text...")
        page_text = page.get_all_text().lower()
        
        keywords = ['sale', 'product', 'price', '$', 'add to cart', 'buy now', 'shop', 'collection']
        for keyword in keywords:
            if keyword in page_text:
                count = page_text.count(keyword)
                print(f"   ✅ Found '{keyword}' {count} times")
            else:
                print(f"   ❌ '{keyword}' not found")
        
        # Check if there's a "no products" or "empty collection" message
        empty_messages = ['no products', 'empty collection', 'no items', 'coming soon', 'sold out']
        for message in empty_messages:
            if message in page_text:
                print(f"   ⚠️  Found empty collection indicator: '{message}'")
        
        # Save a sample of the HTML for manual inspection
        print(f"\n6. Saving HTML sample for inspection...")
        html_content = str(page)
        
        # Save first 5000 characters to a file
        with open('page_sample.html', 'w', encoding='utf-8') as f:
            f.write(html_content[:5000])
        print(f"   💾 Saved first 5000 characters to 'page_sample.html'")
        
        print(f"\n✅ Debug completed!")
        print(f"\n💡 Next steps:")
        print(f"   1. Check 'page_sample.html' to see the actual page structure")
        print(f"   2. Look for the correct CSS selectors for products")
        print(f"   3. Update the SELECTORS in garage_grown_gear_scraper.py if needed")
        
    except Exception as e:
        print(f"\n❌ Debug failed with error:")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        return False
    
    return True

if __name__ == "__main__":
    main()