#!/usr/bin/env python3
"""
Test script with fixed selectors.
"""

from scraper.garage_grown_gear_scraper import GarageGrownGearScraper

def main():
    print("🔧 Testing with fixed selectors...")
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
            first_element = product_elements[0]
            
            print(f"\n🔍 Testing improved extraction methods:")
            
            # Test improved name extraction
            name_element = first_element.css_first('.product-item__title')
            if name_element:
                # Try different ways to get the text
                name_text = name_element.get_all_text().strip()
                name_attr = name_element.attrib.get('title', '')
                
                # Try getting text from child elements
                child_text = ""
                for child in name_element.css('*'):
                    child_text += child.get_all_text().strip() + " "
                
                print(f"   📝 Name (direct): '{name_text}'")
                print(f"   📝 Name (title attr): '{name_attr}'")
                print(f"   📝 Name (children): '{child_text.strip()}'")
                
                # Try getting the href and extracting name from URL
                href = name_element.attrib.get('href', '')
                if href:
                    # Extract product name from URL
                    url_parts = href.split('/')
                    if len(url_parts) > 0:
                        product_slug = url_parts[-1]
                        # Convert slug to readable name
                        readable_name = product_slug.replace('-', ' ').title()
                        print(f"   📝 Name (from URL): '{readable_name}'")
            
            # Test brand extraction
            brand_element = first_element.css_first('.product-item__vendor')
            if brand_element:
                brand_text = brand_element.get_all_text().strip()
                brand_href = brand_element.attrib.get('href', '')
                print(f"   🏷️  Brand (direct): '{brand_text}'")
                print(f"   🏷️  Brand (href): '{brand_href}'")
                
                # Extract brand from URL
                if brand_href:
                    brand_parts = brand_href.split('/')
                    if len(brand_parts) > 0:
                        brand_slug = brand_parts[-1]
                        readable_brand = brand_slug.replace('-', ' ').title()
                        print(f"   🏷️  Brand (from URL): '{readable_brand}'")
            
            # Test price extraction
            price_element = first_element.css_first('.price--highlight [data-money-convertible]')
            if price_element:
                price_text = price_element.get_all_text().strip()
                price_attr = price_element.attrib.get('data-money-convertible', '')
                print(f"   💰 Price (direct): '{price_text}'")
                print(f"   💰 Price (data attr): '{price_attr}'")
                
                # Try parent element
                parent = price_element.parent
                if parent:
                    parent_text = parent.get_all_text().strip()
                    print(f"   💰 Price (parent): '{parent_text}'")
            
            # Test image extraction
            img_element = first_element.css_first('img')
            if img_element:
                img_src = img_element.attrib.get('src', '')
                img_alt = img_element.attrib.get('alt', '')
                print(f"   🖼️  Image src: '{img_src}'")
                print(f"   🖼️  Image alt: '{img_alt}'")
            
            # Now let's create a custom extraction function
            print(f"\n🧪 Testing custom extraction:")
            
            def extract_product_data_fixed(element):
                """Fixed extraction method."""
                data = {}
                
                # Extract name from URL and alt text
                name_element = element.css_first('.product-item__title')
                if name_element:
                    href = name_element.attrib.get('href', '')
                    if href:
                        # Extract from URL
                        url_parts = href.split('/')
                        if len(url_parts) > 0:
                            product_slug = url_parts[-1]
                            data['name'] = product_slug.replace('-', ' ').title()
                            data['product_url'] = f"https://www.garagegrowngear.com{href}"
                
                # Extract brand from URL
                brand_element = element.css_first('.product-item__vendor')
                if brand_element:
                    href = brand_element.attrib.get('href', '')
                    if href:
                        brand_parts = href.split('/')
                        if len(brand_parts) > 0:
                            brand_slug = brand_parts[-1]
                            data['brand'] = brand_slug.replace('-', ' ').title()
                
                # Extract price from parent element text
                price_element = element.css_first('.price--highlight')
                if price_element:
                    price_text = price_element.get_all_text().strip()
                    # Look for price pattern
                    import re
                    price_match = re.search(r'\$[\d,]+\.?\d*', price_text)
                    if price_match:
                        price_str = price_match.group().replace('$', '').replace(',', '')
                        try:
                            data['current_price'] = float(price_str)
                        except ValueError:
                            pass
                
                # Extract image
                img_element = element.css_first('img')
                if img_element:
                    src = img_element.attrib.get('src', '')
                    if src:
                        if src.startswith('//'):
                            src = 'https:' + src
                        data['image_url'] = src
                        
                        # Use alt text as backup name
                        if not data.get('name'):
                            alt = img_element.attrib.get('alt', '')
                            if alt:
                                data['name'] = alt
                
                # Extract availability
                avail_element = element.css_first('.product-item__inventory')
                if avail_element:
                    avail_text = avail_element.get_all_text().strip()
                    data['availability_status'] = avail_text if avail_text else 'Available'
                else:
                    data['availability_status'] = 'Available'
                
                return data
            
            # Test the fixed extraction
            fixed_data = extract_product_data_fixed(first_element)
            
            print(f"   ✅ Fixed extraction results:")
            for key, value in fixed_data.items():
                if value:
                    display_value = str(value)[:60]
                    print(f"   📦 {key:20}: {display_value}")
            
            # Test on all products
            print(f"\n🚀 Testing on all products:")
            all_products = []
            for i, element in enumerate(product_elements[:5]):  # Test first 5
                product_data = extract_product_data_fixed(element)
                if product_data.get('name'):
                    all_products.append(product_data)
                    name = product_data.get('name', 'No name')[:30]
                    price = product_data.get('current_price', 'No price')
                    brand = product_data.get('brand', 'No brand')[:15]
                    print(f"   {i+1}. {name} | {brand} | ${price}")
            
            print(f"\n📊 Summary: {len(all_products)} products successfully extracted from first 5")
        
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