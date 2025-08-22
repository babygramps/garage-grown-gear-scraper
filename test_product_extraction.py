#!/usr/bin/env python3
"""
Test script to debug product data extraction.
"""

from scraper.garage_grown_gear_scraper import GarageGrownGearScraper

def main():
    print("🔍 Testing product data extraction...")
    print("=" * 50)
    
    try:
        scraper = GarageGrownGearScraper()
        
        # Get the page
        page = scraper._make_request('https://www.garagegrowngear.com/collections/sale-1')
        if not page:
            print("❌ Failed to fetch page")
            return False
        
        # Find product elements
        product_elements = page.css(scraper.SELECTORS['product_items'])
        print(f"✅ Found {len(product_elements)} product elements")
        
        if len(product_elements) > 0:
            print(f"\n🔍 Testing extraction on first product...")
            first_element = product_elements[0]
            
            # Test each selector individually
            selectors_to_test = {
                'product_name': '.product-item__title',
                'brand': '.product-item__vendor', 
                'current_price': '.price--highlight [data-money-convertible]',
                'original_price': '.price--compare [data-money-convertible]',
                'sale_label': '.product-label--on-sale',
                'availability': '.product-item__inventory',
                'product_link': '.product-item__title a',
                'image': '.product-item__primary-image img'
            }
            
            print(f"\n📋 Testing individual selectors:")
            for name, selector in selectors_to_test.items():
                element = first_element.css_first(selector)
                if element:
                    text = element.get_all_text().strip()
                    attrs = element.attrib if hasattr(element, 'attrib') else {}
                    print(f"   ✅ {name:15}: '{text}' {attrs}")
                else:
                    print(f"   ❌ {name:15}: Not found")
            
            # Try alternative selectors for missing elements
            print(f"\n🔧 Testing alternative selectors:")
            
            # Alternative link selectors
            alt_link_selectors = ['a', '.product-item__title', '[href]']
            for selector in alt_link_selectors:
                elements = first_element.css(selector)
                if elements:
                    for i, elem in enumerate(elements[:2]):  # Show first 2
                        href = elem.attrib.get('href', 'No href')
                        text = elem.get_all_text().strip()[:50]
                        print(f"   🔗 Link {i+1} ({selector}): {href} | {text}")
            
            # Alternative image selectors
            alt_img_selectors = ['img', '[src]', '.product-item img']
            for selector in alt_img_selectors:
                elements = first_element.css(selector)
                if elements:
                    for i, elem in enumerate(elements[:2]):  # Show first 2
                        src = elem.attrib.get('src', 'No src')
                        alt = elem.attrib.get('alt', 'No alt')
                        print(f"   🖼️  Image {i+1} ({selector}): {src} | {alt}")
            
            # Now test the actual extraction method
            print(f"\n🧪 Testing extract_product_data method:")
            product_data = scraper.extract_product_data(first_element)
            
            if product_data:
                print(f"   ✅ Extraction successful!")
                for key, value in product_data.items():
                    if value:
                        display_value = str(value)[:60]
                        print(f"   📦 {key:20}: {display_value}")
                    else:
                        print(f"   ⚪ {key:20}: (empty)")
            else:
                print(f"   ❌ Extraction returned empty data")
            
            # Test the full scrape_page method
            print(f"\n🚀 Testing full scrape_page method:")
            products = scraper.scrape_page('https://www.garagegrowngear.com/collections/sale-1')
            print(f"   📊 Total products extracted: {len(products)}")
            
            if len(products) > 0:
                valid_products = [p for p in products if p.get('name')]
                print(f"   ✅ Products with names: {len(valid_products)}")
                
                if valid_products:
                    print(f"\n📋 Sample of valid products:")
                    for i, product in enumerate(valid_products[:3]):
                        name = product.get('name', 'No name')[:40]
                        price = product.get('current_price', 'No price')
                        brand = product.get('brand', 'No brand')
                        print(f"   {i+1}. {name} | {brand} | ${price}")
        
        print(f"\n✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()