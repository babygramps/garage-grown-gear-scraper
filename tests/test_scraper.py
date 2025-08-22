"""
Unit tests for the Garage Grown Gear scraper module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from scrapling.parser import Adaptor
from scraper.garage_grown_gear_scraper import GarageGrownGearScraper


class TestGarageGrownGearScraper(unittest.TestCase):
    """Test cases for GarageGrownGearScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = GarageGrownGearScraper(
            base_url="https://www.garagegrowngear.com/collections/sale-1",
            use_stealth=True,
            max_retries=2,
            retry_delay=0.1  # Faster for tests
        )
    
    def test_init(self):
        """Test scraper initialization."""
        self.assertEqual(self.scraper.base_url, "https://www.garagegrowngear.com/collections/sale-1")
        self.assertTrue(self.scraper.use_stealth)
        self.assertEqual(self.scraper.max_retries, 2)
        self.assertEqual(self.scraper.retry_delay, 0.1)
        self.assertIsNotNone(self.scraper.fetcher)
    
    @patch('scraper.garage_grown_gear_scraper.time.sleep')
    def test_make_request_success(self, mock_sleep):
        """Test successful HTTP request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        
        with patch.object(self.scraper.fetcher, 'get', return_value=mock_response):
            result = self.scraper._make_request("https://example.com")
            
            self.assertEqual(result, mock_response)
            mock_sleep.assert_not_called()  # No retries needed
    
    @patch('scraper.garage_grown_gear_scraper.time.sleep')
    def test_make_request_retry_then_success(self, mock_sleep):
        """Test request that fails once then succeeds."""
        # Mock first failure, then success
        mock_response_fail = Mock()
        mock_response_fail.status = 500
        
        mock_response_success = Mock()
        mock_response_success.status = 200
        
        with patch.object(self.scraper.fetcher, 'get', side_effect=[Exception("Network error"), mock_response_success]):
            result = self.scraper._make_request("https://example.com")
            
            self.assertEqual(result, mock_response_success)
            mock_sleep.assert_called_once_with(0.1)  # One retry delay
    
    @patch('scraper.garage_grown_gear_scraper.time.sleep')
    def test_make_request_max_retries_exceeded(self, mock_sleep):
        """Test request that fails all retry attempts."""
        with patch.object(self.scraper.fetcher, 'get', side_effect=Exception("Network error")):
            result = self.scraper._make_request("https://example.com")
            
            self.assertIsNone(result)
            self.assertEqual(mock_sleep.call_count, 1)  # max_retries - 1
    
    def test_parse_price_valid(self):
        """Test price parsing with valid inputs."""
        test_cases = [
            ("$29.99", 29.99),
            ("$1,299.00", 1299.00),
            ("19.50", 19.50),
            ("£15.99", 15.99),
            ("€25.00", 25.00),
        ]
        
        for price_text, expected in test_cases:
            with self.subTest(price_text=price_text):
                result = self.scraper._parse_price(price_text)
                self.assertEqual(result, expected)
    
    def test_parse_price_invalid(self):
        """Test price parsing with invalid inputs."""
        invalid_inputs = ["", None, "invalid", "free", "N/A"]
        
        for invalid_input in invalid_inputs:
            with self.subTest(invalid_input=invalid_input):
                result = self.scraper._parse_price(invalid_input)
                self.assertIsNone(result)
    
    def test_parse_availability_status(self):
        """Test availability status parsing."""
        test_cases = [
            ("Sold out", "Sold out"),
            ("Out of stock", "Sold out"),
            ("Limited stock", "Limited"),
            ("Few left", "Limited"),
            ("In stock", "Available"),
            ("Available", "Available"),
            ("", "Available"),  # Default
            ("Some other text", "Available"),  # Default
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.scraper._parse_availability(input_text)
                self.assertEqual(result, expected)
    
    def test_extract_product_data_complete(self):
        """Test product data extraction with complete data."""
        # Create mock product element
        mock_element = Mock(spec=Adaptor)
        
        # Mock all the CSS selector results
        mock_name = Mock()
        mock_name.get_all_text.return_value = "Test Product Name"
        
        mock_brand = Mock()
        mock_brand.get_all_text.return_value = "Test Brand"
        
        mock_current_price = Mock()
        mock_current_price.get_all_text.return_value = "$29.99"
        
        mock_original_price = Mock()
        mock_original_price.get_all_text.return_value = "$39.99"
        
        mock_sale_label = Mock()
        mock_sale_label.get_all_text.return_value = "Save 25%"
        
        mock_availability = Mock()
        mock_availability.get_all_text.return_value = "In stock"
        
        mock_rating = Mock()
        mock_rating.attrib = {'data-rating': '4.5'}
        
        mock_reviews = Mock()
        mock_reviews.attrib = {'data-reviews': '123'}
        
        mock_link = Mock()
        mock_link.attrib = {'href': '/products/test-product'}
        
        mock_image = Mock()
        mock_image.attrib = {'src': '/images/test-product.jpg'}
        
        # Set up css_first method to return appropriate mocks
        def css_first_side_effect(selector):
            selector_map = {
                '.product-item__title': mock_name,
                '.product-item__vendor': mock_brand,
                '.price--highlight [data-money-convertible]': mock_current_price,
                '.price--compare [data-money-convertible]': mock_original_price,
                '.product-label--on-sale': mock_sale_label,
                '.product-item__inventory': mock_availability,
                '.stamped-badge[data-rating]': mock_rating,
                '.stamped-badge-caption[data-reviews]': mock_reviews,
                '.product-item__title a': mock_link,
                '.product-item__primary-image img': mock_image,
            }
            return selector_map.get(selector)
        
        mock_element.css_first.side_effect = css_first_side_effect
        
        # Extract product data
        result = self.scraper.extract_product_data(mock_element)
        
        # Verify extracted data
        expected = {
            'name': 'Test Product Name',
            'brand': 'Test Brand',
            'current_price': 29.99,
            'original_price': 39.99,
            'discount_percentage': 25.0,
            'sale_label': 'Save 25%',
            'availability_status': 'Available',
            'rating': 4.5,
            'reviews_count': 123,
            'product_url': 'https://www.garagegrowngear.com/products/test-product',
            'image_url': 'https://www.garagegrowngear.com/images/test-product.jpg'
        }
        
        self.assertEqual(result, expected)
    
    def test_extract_product_data_minimal(self):
        """Test product data extraction with minimal data."""
        # Create mock product element with minimal data
        mock_element = Mock(spec=Adaptor)
        
        mock_name = Mock()
        mock_name.get_all_text.return_value = "Minimal Product"
        
        mock_current_price = Mock()
        mock_current_price.get_all_text.return_value = "$19.99"
        
        mock_link = Mock()
        mock_link.attrib = {'href': '/products/minimal'}
        
        # Set up css_first to return None for most selectors
        def css_first_side_effect(selector):
            selector_map = {
                '.product-item__title': mock_name,
                '.price--highlight [data-money-convertible]': mock_current_price,
                '.product-item__title a': mock_link,
            }
            return selector_map.get(selector)
        
        mock_element.css_first.side_effect = css_first_side_effect
        
        result = self.scraper.extract_product_data(mock_element)
        
        # Verify minimal data extraction
        self.assertEqual(result['name'], 'Minimal Product')
        self.assertEqual(result['current_price'], 19.99)
        self.assertEqual(result['product_url'], 'https://www.garagegrowngear.com/products/minimal')
        self.assertEqual(result['brand'], '')
        self.assertIsNone(result['original_price'])
        self.assertIsNone(result['discount_percentage'])
    
    def test_extract_product_data_error_handling(self):
        """Test product data extraction with errors."""
        # Create mock element that raises exceptions
        mock_element = Mock(spec=Adaptor)
        mock_element.css_first.side_effect = Exception("CSS selector error")
        
        result = self.scraper.extract_product_data(mock_element)
        
        # Should return empty dict on error
        self.assertEqual(result, {})
    
    def test_scrape_page_success(self):
        """Test successful page scraping."""
        # Mock successful request
        mock_page = Mock(spec=Adaptor)
        
        # Mock product elements
        mock_product1 = Mock(spec=Adaptor)
        mock_product2 = Mock(spec=Adaptor)
        mock_page.css.return_value = [mock_product1, mock_product2]
        
        with patch.object(self.scraper, '_make_request', return_value=mock_page):
            with patch.object(self.scraper, 'extract_product_data') as mock_extract:
                mock_extract.side_effect = [
                    {'name': 'Product 1', 'current_price': 29.99},
                    {'name': 'Product 2', 'current_price': 19.99}
                ]
                
                result = self.scraper.scrape_page("https://example.com")
                
                self.assertEqual(len(result), 2)
                self.assertEqual(result[0]['name'], 'Product 1')
                self.assertEqual(result[1]['name'], 'Product 2')
    
    def test_scrape_page_request_failure(self):
        """Test page scraping when request fails."""
        with patch.object(self.scraper, '_make_request', return_value=None):
            result = self.scraper.scrape_page("https://example.com")
            
            self.assertEqual(result, [])
    
    def test_get_pagination_urls(self):
        """Test pagination URL extraction."""
        mock_page = Mock(spec=Adaptor)
        
        # Mock pagination links
        mock_link1 = Mock()
        mock_link1.attrib = {'href': '?page=2'}
        
        mock_link2 = Mock()
        mock_link2.attrib = {'href': '?page=3'}
        
        mock_page.css.return_value = [mock_link1, mock_link2]
        
        result = self.scraper.get_pagination_urls(mock_page)
        
        expected_urls = [
            'https://www.garagegrowngear.com/collections/sale-1?page=2',
            'https://www.garagegrowngear.com/collections/sale-1?page=3'
        ]
        
        self.assertEqual(result, expected_urls)
    
    def test_get_pagination_urls_no_links(self):
        """Test pagination URL extraction when no links found."""
        mock_page = Mock(spec=Adaptor)
        mock_page.css.return_value = []
        
        result = self.scraper.get_pagination_urls(mock_page)
        
        self.assertEqual(result, [])
    
    def test_get_pagination_urls_error(self):
        """Test pagination URL extraction with errors."""
        mock_page = Mock(spec=Adaptor)
        mock_page.css.side_effect = Exception("CSS error")
        
        result = self.scraper.get_pagination_urls(mock_page)
        
        self.assertEqual(result, [])
    
    @patch('scraper.garage_grown_gear_scraper.time.sleep')
    def test_scrape_all_products_single_page(self, mock_sleep):
        """Test scraping all products from a single page."""
        with patch.object(self.scraper, 'scrape_page') as mock_scrape_page:
            with patch.object(self.scraper, '_make_request') as mock_request:
                with patch.object(self.scraper, 'get_pagination_urls') as mock_pagination:
                    
                    # Mock single page with no pagination
                    mock_scrape_page.return_value = [
                        {'name': 'Product 1', 'current_price': 29.99},
                        {'name': 'Product 2', 'current_price': 19.99}
                    ]
                    
                    mock_request.return_value = Mock()
                    mock_pagination.return_value = []  # No more pages
                    
                    result = self.scraper.scrape_all_products()
                    
                    self.assertEqual(len(result), 2)
                    mock_scrape_page.assert_called_once()
                    mock_sleep.assert_called_once_with(1)  # Delay between pages
    
    @patch('scraper.garage_grown_gear_scraper.time.sleep')
    def test_scrape_all_products_multiple_pages(self, mock_sleep):
        """Test scraping all products from multiple pages."""
        with patch.object(self.scraper, 'scrape_page') as mock_scrape_page:
            with patch.object(self.scraper, '_make_request') as mock_request:
                with patch.object(self.scraper, 'get_pagination_urls') as mock_pagination:
                    
                    # Mock multiple pages
                    mock_scrape_page.side_effect = [
                        [{'name': 'Product 1', 'current_price': 29.99}],  # Page 1
                        [{'name': 'Product 2', 'current_price': 19.99}]   # Page 2
                    ]
                    
                    mock_request.return_value = Mock()
                    mock_pagination.side_effect = [
                        ['https://example.com/page2'],  # Page 1 has link to page 2
                        []  # Page 2 has no more links
                    ]
                    
                    result = self.scraper.scrape_all_products()
                    
                    self.assertEqual(len(result), 2)
                    self.assertEqual(mock_scrape_page.call_count, 2)
                    self.assertEqual(mock_sleep.call_count, 2)  # Delay after each page
    
    @patch('scraper.garage_grown_gear_scraper.time.sleep')
    def test_scrape_all_products_infinite_loop_protection(self, mock_sleep):
        """Test protection against infinite loops in pagination."""
        with patch.object(self.scraper, 'scrape_page') as mock_scrape_page:
            with patch.object(self.scraper, '_make_request') as mock_request:
                with patch.object(self.scraper, 'get_pagination_urls') as mock_pagination:
                    
                    # Mock pages that keep returning the same URL (infinite loop scenario)
                    mock_scrape_page.return_value = [{'name': 'Product', 'current_price': 29.99}]
                    mock_request.return_value = Mock()
                    mock_pagination.return_value = ['https://example.com/page2']  # Always same URL
                    
                    result = self.scraper.scrape_all_products()
                    
                    # Should stop due to visited_urls check
                    self.assertGreater(len(result), 0)
                    # Should not call scrape_page more than reasonable number of times
                    self.assertLess(mock_scrape_page.call_count, 10)


if __name__ == '__main__':
    unittest.main()