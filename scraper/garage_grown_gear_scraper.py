"""
Garage Grown Gear scraper implementation using Scrapling.
"""
import logging
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import re

from scrapling.fetchers import Fetcher
from scrapling.parser import Adaptor
from error_handling.monitoring import PerformanceMonitor, BatchProcessor


class GarageGrownGearScraper:
    """
    Main scraper class for Garage Grown Gear sale page using Scrapling Fetcher.
    """
    
    # CSS selectors based on the HTML structure from the design document
    SELECTORS = {
        'product_items': '.product-item',
        'product_name': '.product-item__title',
        'brand': '.product-item__vendor',
        'current_price': '.price--highlight [data-money-convertible]',
        'original_price': '.price--compare [data-money-convertible]',
        'sale_label': '.product-label--on-sale',
        'availability': '.product-item__inventory',
        'rating': '.stamped-badge[data-rating]',
        'reviews_count': '.stamped-badge-caption[data-reviews]',
        'product_link': '.product-item__title a',
        'image': '.product-item__primary-image img',
        'pagination_next': '.pagination__next',
        'pagination_links': '.pagination a'
    }
    
    def __init__(self, base_url: str = "https://www.garagegrowngear.com/collections/sale-1", 
                 use_stealth: bool = True, max_retries: int = 3, retry_delay: float = 1.0,
                 enable_performance_monitoring: bool = True, batch_size: int = 50,
                 fallback_urls: List[str] = None):
        """
        Initialize the scraper with configuration.
        
        Args:
            base_url: The base URL to scrape
            use_stealth: Whether to use stealth mode headers
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            enable_performance_monitoring: Whether to enable performance monitoring
            batch_size: Batch size for processing large datasets
            fallback_urls: Alternative URLs to try if main URL fails
        """
        self.base_url = base_url
        self.use_stealth = use_stealth
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        
        # Set up fallback URLs
        self.fallback_urls = fallback_urls or [
            "https://www.garagegrowngear.com/collections/sale",
            "https://www.garagegrowngear.com/collections/clearance",
            "https://www.garagegrowngear.com/collections/all?filter.v.availability=1&filter.v.price.gte=&filter.v.price.lte=&sort_by=best-selling"
        ]
        
        # Initialize performance monitoring
        self.performance_monitor = PerformanceMonitor() if enable_performance_monitoring else None
        self.batch_processor = BatchProcessor(batch_size=batch_size)
        
        # Initialize Scrapling Fetcher with enhanced stealth configuration
        self.fetcher = Fetcher()
        
        # Configure Fetcher with proper settings for Scrapling 0.2.99
        try:
            self.fetcher.configure(
                auto_match=True
            )
        except Exception as e:
            self.logger.warning(f"Could not configure fetcher settings: {e}")
            # Fallback to basic configuration
            self.fetcher = Fetcher()
    
    def _simulate_human_behavior(self) -> None:
        """Add small random delays to simulate human browsing behavior."""
        import random
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)
    
    def _establish_session(self) -> bool:
        """
        Visit the homepage first to establish a session and look more natural.
        Returns True if successful, False otherwise.
        """
        homepage_url = "https://www.garagegrowngear.com"
        self.logger.info("Establishing session by visiting homepage first...")
        
        try:
            response = self.fetcher.get(
                homepage_url,
                stealthy_headers=self.use_stealth,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'DNT': '1'
                },
                follow_redirects=True,
                timeout=30
            )
            
            if response.status == 200:
                self.logger.info("Successfully established session")
                # Wait a bit to simulate reading the page
                import random
                time.sleep(random.uniform(1.0, 3.0))
                return True
            else:
                self.logger.warning(f"Failed to establish session: HTTP {response.status}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error establishing session: {str(e)}")
            return False
        
    def _make_request(self, url: str) -> Optional[Adaptor]:
        """
        Make a request with retry logic, stealth headers, and performance monitoring.
        Enhanced with better anti-detection measures.
        
        Args:
            url: URL to fetch
            
        Returns:
            Adaptor object with parsed HTML or None if failed
        """
        request_id = f"request_{int(time.time() * 1000)}"
        
        # Enhanced headers to look more like a real browser
        enhanced_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Fetching URL: {url} (attempt {attempt + 1})")
                
                # Add small delay to simulate human behavior
                if attempt > 0:
                    self._simulate_human_behavior()
                
                # Add referrer to look more natural (simulate coming from Google search)
                if attempt == 0:
                    enhanced_headers['Referer'] = 'https://www.google.com/search?q=garage+grown+gear'
                else:
                    # On retries, use the site's homepage as referrer
                    enhanced_headers['Referer'] = 'https://www.garagegrowngear.com/'
                
                # Use performance monitoring for request timing
                if self.performance_monitor:
                    with self.performance_monitor.request_timer.time_request(request_id, url):
                        response = self.fetcher.get(
                            url,
                            stealthy_headers=self.use_stealth,
                            headers=enhanced_headers,
                            follow_redirects=True,
                            timeout=30
                        )
                else:
                    response = self.fetcher.get(
                        url,
                        stealthy_headers=self.use_stealth,
                        headers=enhanced_headers,
                        follow_redirects=True,
                        timeout=30
                    )
                
                self.logger.info(f"Response status: {response.status} for {url}")
                
                if response.status == 200:
                    self.logger.info(f"Successfully fetched {url}")
                    return response
                elif response.status == 403:
                    self.logger.warning(f"Access forbidden (403) for {url} - website may be blocking requests")
                    # For 403 errors, wait longer before retry
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (3 ** attempt)  # Longer exponential backoff for 403
                        self.logger.info(f"403 error - waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                elif response.status == 429:
                    self.logger.warning(f"Rate limited (429) for {url}")
                    # For rate limiting, wait even longer
                    if attempt < self.max_retries - 1:
                        wait_time = 30 + (self.retry_delay * (2 ** attempt))
                        self.logger.info(f"Rate limited - waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
                    
            except Exception as e:
                self.logger.error(f"Request failed for {url}: {str(e)}")
                
            # Standard retry logic for other errors
            if attempt < self.max_retries - 1:
                wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                self.logger.error(f"Max retries exceeded for {url}")
                    
        return None
    
    def extract_product_data(self, product_element: Adaptor) -> Dict[str, Any]:
        """
        Extract product data from a single product element.
        
        Args:
            product_element: Scrapling Adaptor element containing product data
            
        Returns:
            Dictionary containing extracted product information
        """
        try:
            # Extract product name from URL (more reliable than text content)
            name = ""
            product_url = ""
            name_element = product_element.css_first(self.SELECTORS['product_name'])
            if name_element:
                href = name_element.attrib.get('href', '')
                if href:
                    # Extract name from URL slug
                    url_parts = href.split('/')
                    if len(url_parts) > 0:
                        product_slug = url_parts[-1]
                        name = product_slug.replace('-', ' ').title()
                    product_url = urljoin(self.base_url, href)
            
            # Fallback: try to get name from image alt text
            if not name:
                image_element = product_element.css_first('img')
                if image_element:
                    alt_text = image_element.attrib.get('alt', '')
                    if alt_text:
                        name = alt_text
            
            # Extract brand from URL (more reliable than text content)
            brand = ""
            brand_element = product_element.css_first(self.SELECTORS['brand'])
            if brand_element:
                href = brand_element.attrib.get('href', '')
                if href:
                    # Extract brand from URL
                    brand_parts = href.split('/')
                    if len(brand_parts) > 0:
                        brand_slug = brand_parts[-1]
                        # Clean up brand name
                        if brand_slug.startswith('vendors?q='):
                            brand = brand_slug.replace('vendors?q=', '').replace('-', ' ').title()
                        else:
                            brand = brand_slug.replace('-', ' ').title()
            
            # Extract current price from parent element text
            current_price = None
            current_price_element = product_element.css_first('.price--highlight')
            if current_price_element:
                price_text = current_price_element.get_all_text().strip()
                current_price = self._parse_price(price_text)
            
            # Extract original price
            original_price = None
            original_price_element = product_element.css_first('.price--compare')
            if original_price_element:
                original_price_text = original_price_element.get_all_text().strip()
                original_price = self._parse_price(original_price_text)
            
            # Calculate discount percentage
            discount_percentage = None
            if original_price and current_price and original_price > current_price:
                discount_percentage = round(((original_price - current_price) / original_price) * 100, 2)
            
            # Extract sale label
            sale_label = ""
            sale_label_element = product_element.css_first(self.SELECTORS['sale_label'])
            if sale_label_element:
                sale_label = sale_label_element.get_all_text().strip()
            
            # Extract availability status
            availability_status = "Available"  # Default
            availability_element = product_element.css_first(self.SELECTORS['availability'])
            if availability_element:
                availability_text = availability_element.get_all_text().strip()
                if availability_text:
                    availability_status = self._parse_availability(availability_text)
            
            # Extract rating (keep original logic)
            rating = None
            rating_element = product_element.css_first(self.SELECTORS['rating'])
            if rating_element and rating_element.attrib.get('data-rating'):
                try:
                    rating = float(rating_element.attrib['data-rating'])
                except (ValueError, TypeError):
                    rating = None
            
            # Extract reviews count (keep original logic)
            reviews_count = None
            reviews_element = product_element.css_first(self.SELECTORS['reviews_count'])
            if reviews_element and reviews_element.attrib.get('data-reviews'):
                try:
                    reviews_count = int(reviews_element.attrib['data-reviews'])
                except (ValueError, TypeError):
                    reviews_count = None
            
            # Extract image URL
            image_url = ""
            image_element = product_element.css_first('img')
            if image_element:
                src = image_element.attrib.get('src', '')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.garagegrowngear.com' + src
                    image_url = src
            
            return {
                'name': name,
                'brand': brand,
                'current_price': current_price,
                'original_price': original_price,
                'discount_percentage': discount_percentage,
                'sale_label': sale_label,
                'availability_status': availability_status,
                'rating': rating,
                'reviews_count': reviews_count,
                'product_url': product_url,
                'image_url': image_url
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting product data: {str(e)}")
            return {}
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price string to float value.
        
        Args:
            price_text: Raw price text (e.g., "$19.99", "£15.50")
            
        Returns:
            Float price value or None if parsing fails
        """
        if not price_text:
            return None
            
        try:
            # Remove currency symbols and whitespace, extract numbers
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                return float(price_match.group())
        except (ValueError, AttributeError):
            self.logger.warning(f"Could not parse price: {price_text}")
            
        return None
    
    def _parse_availability(self, availability_text: str) -> str:
        """
        Parse availability status from text.
        
        Args:
            availability_text: Raw availability text
            
        Returns:
            Standardized availability status
        """
        if not availability_text:
            return "Unknown"
            
        availability_lower = availability_text.lower()
        
        if 'sold out' in availability_lower or 'out of stock' in availability_lower:
            return "Sold out"
        elif 'limited' in availability_lower or 'few left' in availability_lower:
            return "Limited"
        elif 'in stock' in availability_lower or 'available' in availability_lower:
            return "Available"
        else:
            return "Available"  # Default assumption
    
    def scrape_page(self, page_url: str) -> List[Dict[str, Any]]:
        """
        Scrape products from a single page with performance monitoring.
        
        Args:
            page_url: URL of the page to scrape
            
        Returns:
            List of product dictionaries
        """
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("scrape_page"):
                return self._scrape_page_internal(page_url)
        else:
            return self._scrape_page_internal(page_url)
    
    def _scrape_page_internal(self, page_url: str) -> List[Dict[str, Any]]:
        """Internal method for scraping a page."""
        page = self._make_request(page_url)
        if not page:
            return []
        
        product_elements = page.css(self.SELECTORS['product_items'])
        self.logger.info(f"Found {len(product_elements)} products on page: {page_url}")
        
        # Use batch processing for large numbers of products
        if len(product_elements) > self.batch_processor.batch_size:
            return self.batch_processor.process_in_batches(
                product_elements, 
                self._extract_products_batch
            )
        else:
            return self._extract_products_batch(product_elements)
    
    def _extract_products_batch(self, product_elements: List[Any]) -> List[Dict[str, Any]]:
        """Extract product data from a batch of elements."""
        products = []
        for product_element in product_elements:
            product_data = self.extract_product_data(product_element)
            if product_data and product_data.get('name'):  # Only add if we got valid data
                products.append(product_data)
        return products
    
    def get_pagination_urls(self, page: Adaptor) -> List[str]:
        """
        Extract pagination URLs from the current page.
        
        Args:
            page: Scrapling Adaptor object of the current page
            
        Returns:
            List of pagination URLs
        """
        pagination_urls = []
        
        try:
            # Find all pagination links
            pagination_elements = page.css(self.SELECTORS['pagination_links'])
            
            for link_element in pagination_elements:
                href = link_element.attrib.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in pagination_urls:
                        pagination_urls.append(full_url)
            
            self.logger.info(f"Found {len(pagination_urls)} pagination URLs")
            
        except Exception as e:
            self.logger.error(f"Error extracting pagination URLs: {str(e)}")
        
        return pagination_urls
    
    def scrape_all_products(self) -> List[Dict[str, Any]]:
        """
        Scrape all products from all pages with pagination handling and performance monitoring.
        
        Returns:
            List of all product dictionaries from all pages
        """
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("scrape_all_products"):
                return self._scrape_all_products_internal()
        else:
            return self._scrape_all_products_internal()
    
    def _scrape_all_products_internal(self) -> List[Dict[str, Any]]:
        """Internal method for scraping all products."""
        all_products = []
        visited_urls = set()
        urls_to_visit = [self.base_url]
        
        self.logger.info(f"Starting scrape of all products from: {self.base_url}")
        
        # Establish session first by visiting homepage
        if not self._establish_session():
            self.logger.warning("Failed to establish session, proceeding anyway...")
        
        # Try main URL first, then fallbacks if it fails
        primary_success = False
        for attempt_url in [self.base_url] + self.fallback_urls:
            self.logger.info(f"Attempting to scrape from: {attempt_url}")
            page = self._make_request(attempt_url)
            
            if page:
                # Update the base URL to the successful one for pagination
                self.base_url = attempt_url
                urls_to_visit = [attempt_url]
                primary_success = True
                self.logger.info(f"Successfully connected to: {attempt_url}")
                break
            else:
                self.logger.warning(f"Failed to connect to: {attempt_url}")
        
        if not primary_success:
            self.logger.error("All URLs failed - unable to scrape any content")
            return all_products
        
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            
            # Avoid infinite loops
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            
            # Scrape current page
            page_products = self.scrape_page(current_url)
            all_products.extend(page_products)
            
            # Optimize memory usage periodically
            if self.performance_monitor and len(all_products) % 200 == 0:
                optimization_result = self.performance_monitor.optimize_performance()
                self.logger.info(f"Memory optimization: {optimization_result}")
            
            # Get pagination URLs for next pages
            page = self._make_request(current_url)
            if page:
                pagination_urls = self.get_pagination_urls(page)
                
                # Add new URLs to visit list
                for url in pagination_urls:
                    if url not in visited_urls and url not in urls_to_visit:
                        urls_to_visit.append(url)
            
            # Add realistic delay between pages to avoid being detected as a bot
            import random
            delay = random.uniform(2.0, 5.0)  # Random delay between 2-5 seconds
            time.sleep(delay)
            self.logger.info(f"Waiting {delay:.1f} seconds before next page")
            
            # Safety check to prevent infinite loops
            if len(visited_urls) > 50:  # Reasonable limit for pagination
                self.logger.warning("Reached maximum page limit, stopping pagination")
                break
        
        self.logger.info(f"Scraping completed. Total products found: {len(all_products)}")
        return all_products
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        if not self.performance_monitor:
            return {}
        
        return self.performance_monitor.get_performance_summary()