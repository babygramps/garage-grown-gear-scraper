"""
Integration tests for the complete scraping workflow.
"""

import pytest
import os
import json
import base64
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import modules for integration testing
from scraper.garage_grown_gear_scraper import GarageGrownGearScraper
from data_processing.product_data_processor import ProductDataProcessor
from sheets_integration.sheets_client import SheetsClient, SheetsConfig
from error_handling.monitoring import PerformanceMonitor


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Integration tests for the complete scraping workflow."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.test_config = {
            'scraper': {
                'base_url': 'https://www.garagegrowngear.com/collections/sale-1',
                'max_retries': 2,
                'retry_delay': 0.5,
                'use_stealth': True
            },
            'sheets': {
                'spreadsheet_id': 'test_integration_spreadsheet',
                'sheet_name': 'Integration_Test_Products'
            }
        }
        
        # Sample HTML content for mocking
        self.sample_html = """
        <!DOCTYPE html>
        <html>
        <body>
            <div class="product-item">
                <h3 class="product-item__title">Integration Test Product</h3>
                <div class="product-item__vendor">Test Brand</div>
                <div class="price--highlight">
                    <span data-money-convertible>4999</span>
                </div>
                <div class="price--compare">
                    <span data-money-convertible>6999</span>
                </div>
                <div class="product-label--on-sale">Save 29%</div>
                <div class="product-item__inventory">In stock</div>
                <div class="stamped-badge" data-rating="4.2"></div>
                <div class="stamped-badge-caption" data-reviews="156"></div>
                <a class="product-item__title" href="/products/integration-test-product">Integration Test Product</a>
                <img class="product-item__primary-image" src="/images/integration-test.jpg" alt="Integration Test Product">
            </div>
        </body>
        </html>
        """
    
    @patch('scrapling.fetchers.Fetcher')
    def test_scraper_to_processor_integration(self, mock_fetcher_class):
        """Test integration between scraper and data processor."""
        # Set up mock fetcher
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = self.sample_html
        
        # Mock CSS selectors
        mock_response.css.return_value = [self._create_mock_product_element()]
        mock_response.css_first.return_value = None  # No pagination
        
        mock_fetcher.get.return_value = mock_response
        
        # Create scraper and processor
        scraper = GarageGrownGearScraper(**self.test_config['scraper'])
        processor = ProductDataProcessor()
        
        # Execute scraping
        raw_products = scraper.scrape_all_products()
        
        # Verify raw products
        assert len(raw_products) == 1
        assert raw_products[0]['name'] == 'Integration Test Product'
        assert raw_products[0]['current_price'] == 49.99
        
        # Execute processing
        processed_products = processor.process_products(raw_products)
        
        # Verify processed products
        assert len(processed_products) == 1
        product = processed_products[0]
        assert product.name == 'Integration Test Product'
        assert product.brand == 'Test Brand'
        assert product.current_price == 49.99
        assert product.original_price == 69.99
        assert product.discount_percentage == 28.6  # Approximately 29%
        assert product.availability_status == 'Available'
    
    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    @patch('googleapiclient.discovery.build')
    def test_processor_to_sheets_integration(self, mock_build, mock_credentials):
        """Test integration between data processor and Google Sheets client."""
        # Set up mock Google Sheets service
        mock_service = self._create_mock_sheets_service()
        mock_build.return_value = mock_service
        
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds
        
        # Create test credentials
        test_credentials = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "test-client-id"
        }
        
        # Set up environment
        credentials_b64 = base64.b64encode(json.dumps(test_credentials).encode()).decode()
        
        with patch.dict(os.environ, {'GOOGLE_SHEETS_CREDENTIALS': credentials_b64}):
            # Create sheets client
            config = SheetsConfig(**self.test_config['sheets'])
            sheets_client = SheetsClient(config)
            sheets_client.authenticate()
            
            # Create sample processed products
            processor = ProductDataProcessor()
            sample_raw_data = [{
                'name': 'Integration Test Product',
                'brand': 'Test Brand',
                'current_price': '49.99',
                'original_price': '69.99',
                'availability_status': 'In stock',
                'rating': '4.2',
                'reviews_count': '156',
                'product_url': 'https://example.com/product',
                'image_url': 'https://example.com/image.jpg',
                'sale_label': 'Save 29%'
            }]
            
            processed_products = processor.process_products(sample_raw_data)
            
            # Convert to sheets format
            sheets_data = [product.to_sheets_row() for product in processed_products]
            
            # Test sheets operations
            sheets_client.create_sheet_if_not_exists(config.sheet_name)
            sheets_client.append_data(config.sheet_name, sheets_data)
            
            # Verify sheets operations were called
            mock_service.spreadsheets().get.assert_called()
            mock_service.spreadsheets().values().append.assert_called()
    
    @patch('scrapling.fetchers.Fetcher')
    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    @patch('googleapiclient.discovery.build')
    def test_complete_workflow_integration(self, mock_build, mock_credentials, mock_fetcher_class):
        """Test complete end-to-end workflow integration."""
        # Set up mocks
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = self.sample_html
        mock_response.css.return_value = [self._create_mock_product_element()]
        mock_response.css_first.return_value = None
        
        mock_fetcher.get.return_value = mock_response
        
        mock_service = self._create_mock_sheets_service()
        mock_build.return_value = mock_service
        
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds
        
        # Set up environment
        test_credentials = {"type": "service_account", "project_id": "test"}
        credentials_b64 = base64.b64encode(json.dumps(test_credentials).encode()).decode()
        
        with patch.dict(os.environ, {'GOOGLE_SHEETS_CREDENTIALS': credentials_b64}):
            # Initialize components
            scraper = GarageGrownGearScraper(**self.test_config['scraper'])
            processor = ProductDataProcessor()
            
            config = SheetsConfig(**self.test_config['sheets'])
            sheets_client = SheetsClient(config)
            sheets_client.authenticate()
            
            monitor = PerformanceMonitor()
            
            # Execute complete workflow
            with monitor.timer('complete_workflow'):
                # Step 1: Scrape products
                with monitor.timer('scraping'):
                    raw_products = scraper.scrape_all_products()
                
                # Step 2: Process products
                with monitor.timer('processing'):
                    processed_products = processor.process_products(raw_products)
                
                # Step 3: Save to sheets
                with monitor.timer('sheets_upload'):
                    sheets_client.create_sheet_if_not_exists(config.sheet_name)
                    sheets_data = [product.to_sheets_row() for product in processed_products]
                    sheets_client.append_data(config.sheet_name, sheets_data)
            
            # Verify workflow results
            assert len(raw_products) == 1
            assert len(processed_products) == 1
            
            # Verify monitoring data
            metrics = monitor.get_metrics()
            assert 'complete_workflow_duration' in metrics
            assert 'scraping_duration' in metrics
            assert 'processing_duration' in metrics
            assert 'sheets_upload_duration' in metrics
            
            # Verify all durations are reasonable
            assert metrics['complete_workflow_duration'] > 0
            assert metrics['scraping_duration'] > 0
            assert metrics['processing_duration'] > 0
            assert metrics['sheets_upload_duration'] > 0
    
    def test_error_handling_integration(self):
        """Test error handling across integrated components."""
        from error_handling.retry_handler import RetryHandler
        from error_handling.exceptions import ScrapingError, RetryableError
        
        # Test retry handler with scraper
        retry_handler = RetryHandler(max_attempts=3)
        
        # Mock function that fails twice then succeeds
        call_count = 0
        def mock_scraping_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RetryableError("Network timeout", retry_after=0.1)
            return "success"
        
        with patch('time.sleep'):  # Speed up test
            result = retry_handler.execute(mock_scraping_function)
        
        assert result == "success"
        assert call_count == 3
    
    def _create_mock_product_element(self):
        """Create a mock product element for testing."""
        mock_element = Mock()
        
        # Mock text elements
        mock_name = Mock()
        mock_name.get_all_text.return_value = "Integration Test Product"
        
        mock_brand = Mock()
        mock_brand.get_all_text.return_value = "Test Brand"
        
        mock_price = Mock()
        mock_price.get_all_text.return_value = "$49.99"
        
        mock_original_price = Mock()
        mock_original_price.get_all_text.return_value = "$69.99"
        
        mock_availability = Mock()
        mock_availability.get_all_text.return_value = "In stock"
        
        mock_sale_label = Mock()
        mock_sale_label.get_all_text.return_value = "Save 29%"
        
        # Mock attribute elements
        mock_rating = Mock()
        mock_rating.attrib = {'data-rating': '4.2'}
        
        mock_reviews = Mock()
        mock_reviews.attrib = {'data-reviews': '156'}
        
        mock_link = Mock()
        mock_link.attrib = {'href': '/products/integration-test-product'}
        
        mock_image = Mock()
        mock_image.attrib = {'src': '/images/integration-test.jpg'}
        
        # Set up css_first method
        def css_first_side_effect(selector):
            selector_map = {
                '.product-item__title': mock_name,
                '.product-item__vendor': mock_brand,
                '.price--highlight [data-money-convertible]': mock_price,
                '.price--compare [data-money-convertible]': mock_original_price,
                '.product-item__inventory': mock_availability,
                '.product-label--on-sale': mock_sale_label,
                '.stamped-badge[data-rating]': mock_rating,
                '.stamped-badge-caption[data-reviews]': mock_reviews,
                '.product-item__title a': mock_link,
                '.product-item__primary-image img': mock_image,
            }
            return selector_map.get(selector)
        
        mock_element.css_first.side_effect = css_first_side_effect
        
        return mock_element
    
    def _create_mock_sheets_service(self):
        """Create a mock Google Sheets service for testing."""
        mock_service = Mock()
        
        # Mock spreadsheets operations
        mock_spreadsheets = Mock()
        mock_service.spreadsheets.return_value = mock_spreadsheets
        
        # Mock get operation
        mock_get = Mock()
        mock_get.execute.return_value = {
            'properties': {'title': 'Test Spreadsheet'},
            'sheets': [{'properties': {'title': 'Integration_Test_Products'}}],
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/test_id'
        }
        mock_spreadsheets.get.return_value = mock_get
        
        # Mock batchUpdate operation
        mock_batch_update = Mock()
        mock_batch_update.execute.return_value = {}
        mock_spreadsheets.batchUpdate.return_value = mock_batch_update
        
        # Mock values operations
        mock_values = Mock()
        mock_spreadsheets.values.return_value = mock_values
        
        # Mock update operation
        mock_update = Mock()
        mock_update.execute.return_value = {}
        mock_values.update.return_value = mock_update
        
        # Mock append operation
        mock_append = Mock()
        mock_append.execute.return_value = {'updates': {'updatedRows': 1}}
        mock_values.append.return_value = mock_append
        
        return mock_service


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceBenchmarks:
    """Performance benchmarking tests for the scraping system."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.performance_thresholds = {
            'scraping_time_per_product': 0.5,  # seconds
            'processing_time_per_product': 0.1,  # seconds
            'sheets_upload_time_per_product': 0.2,  # seconds
            'memory_usage_mb': 100,  # MB
            'total_workflow_time': 30  # seconds for 50 products
        }
    
    @patch('scrapling.fetchers.Fetcher')
    def test_scraping_performance_benchmark(self, mock_fetcher_class):
        """Benchmark scraping performance with multiple products."""
        # Create mock fetcher with multiple products
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Create mock response with multiple products
        mock_response = Mock()
        mock_response.status = 200
        
        # Create multiple mock product elements
        mock_products = []
        for i in range(50):  # Test with 50 products
            mock_product = self._create_mock_product_element(f"Product {i}")
            mock_products.append(mock_product)
        
        mock_response.css.return_value = mock_products
        mock_response.css_first.return_value = None  # No pagination
        
        mock_fetcher.get.return_value = mock_response
        
        # Initialize scraper and monitor
        scraper = GarageGrownGearScraper(
            base_url="https://example.com",
            max_retries=1,
            retry_delay=0.1
        )
        monitor = PerformanceMonitor()
        
        # Benchmark scraping
        with monitor.timer('scraping_benchmark'):
            raw_products = scraper.scrape_all_products()
        
        # Verify results
        assert len(raw_products) == 50
        
        # Check performance metrics
        metrics = monitor.get_metrics()
        scraping_duration = metrics['scraping_benchmark_duration']
        time_per_product = scraping_duration / len(raw_products)
        
        # Performance assertions
        assert time_per_product < self.performance_thresholds['scraping_time_per_product'], \
            f"Scraping too slow: {time_per_product:.3f}s per product"
        
        print(f"Scraping Performance: {time_per_product:.3f}s per product")
    
    def test_processing_performance_benchmark(self):
        """Benchmark data processing performance."""
        # Create sample raw products
        raw_products = []
        for i in range(100):  # Test with 100 products
            raw_products.append({
                'name': f'Benchmark Product {i}',
                'brand': f'Brand {i % 10}',
                'current_price': f'${19.99 + i}',
                'original_price': f'${29.99 + i}',
                'availability_status': 'In stock',
                'rating': '4.5',
                'reviews_count': str(100 + i),
                'product_url': f'https://example.com/product-{i}',
                'image_url': f'https://example.com/image-{i}.jpg',
                'sale_label': 'Save 33%'
            })
        
        # Initialize processor and monitor
        processor = ProductDataProcessor()
        monitor = PerformanceMonitor()
        
        # Benchmark processing
        with monitor.timer('processing_benchmark'):
            processed_products = processor.process_products(raw_products)
        
        # Verify results
        assert len(processed_products) == len(raw_products)
        
        # Check performance metrics
        metrics = monitor.get_metrics()
        processing_duration = metrics['processing_benchmark_duration']
        time_per_product = processing_duration / len(processed_products)
        
        # Performance assertions
        assert time_per_product < self.performance_thresholds['processing_time_per_product'], \
            f"Processing too slow: {time_per_product:.3f}s per product"
        
        print(f"Processing Performance: {time_per_product:.3f}s per product")
    
    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    @patch('googleapiclient.discovery.build')
    def test_sheets_upload_performance_benchmark(self, mock_build, mock_credentials):
        """Benchmark Google Sheets upload performance."""
        # Set up mocks
        mock_service = self._create_mock_sheets_service()
        mock_build.return_value = mock_service
        
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds
        
        # Create test data
        test_credentials = {"type": "service_account", "project_id": "test"}
        credentials_b64 = base64.b64encode(json.dumps(test_credentials).encode()).decode()
        
        # Create sample processed products
        from data_processing.product_data_processor import Product
        processed_products = []
        for i in range(50):  # Test with 50 products
            product = Product(
                timestamp=datetime.now(),
                name=f'Benchmark Product {i}',
                brand=f'Brand {i % 10}',
                current_price=19.99 + i,
                original_price=29.99 + i,
                discount_percentage=33.3,
                availability_status='Available',
                rating=4.5,
                reviews_count=100 + i,
                product_url=f'https://example.com/product-{i}',
                sale_label='Save 33%',
                image_url=f'https://example.com/image-{i}.jpg'
            )
            processed_products.append(product)
        
        with patch.dict(os.environ, {'GOOGLE_SHEETS_CREDENTIALS': credentials_b64}):
            # Initialize sheets client and monitor
            config = SheetsConfig(
                spreadsheet_id='benchmark_test_id',
                sheet_name='Benchmark_Products'
            )
            sheets_client = SheetsClient(config)
            sheets_client.authenticate()
            
            monitor = PerformanceMonitor()
            
            # Benchmark sheets upload
            with monitor.timer('sheets_benchmark'):
                sheets_client.create_sheet_if_not_exists(config.sheet_name)
                sheets_data = [product.to_sheets_row() for product in processed_products]
                sheets_client.append_data(config.sheet_name, sheets_data)
            
            # Check performance metrics
            metrics = monitor.get_metrics()
            upload_duration = metrics['sheets_benchmark_duration']
            time_per_product = upload_duration / len(processed_products)
            
            # Performance assertions (more lenient for API calls)
            assert time_per_product < self.performance_thresholds['sheets_upload_time_per_product'], \
                f"Sheets upload too slow: {time_per_product:.3f}s per product"
            
            print(f"Sheets Upload Performance: {time_per_product:.3f}s per product")
    
    @pytest.mark.slow
    def test_memory_usage_benchmark(self):
        """Benchmark memory usage during processing."""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        raw_products = []
        for i in range(1000):  # Test with 1000 products
            raw_products.append({
                'name': f'Memory Test Product {i}' * 10,  # Longer strings
                'brand': f'Brand {i % 50}',
                'current_price': f'${19.99 + i}',
                'original_price': f'${29.99 + i}',
                'availability_status': 'In stock',
                'rating': '4.5',
                'reviews_count': str(100 + i),
                'product_url': f'https://example.com/very-long-product-url-{i}',
                'image_url': f'https://example.com/very-long-image-url-{i}.jpg',
                'sale_label': 'Save 33%'
            })
        
        # Process products
        processor = ProductDataProcessor()
        processed_products = processor.process_products(raw_products)
        
        # Get peak memory usage
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Clean up
        del raw_products
        del processed_products
        gc.collect()
        
        # Performance assertions
        assert memory_increase < self.performance_thresholds['memory_usage_mb'], \
            f"Memory usage too high: {memory_increase:.1f}MB increase"
        
        print(f"Memory Usage: {memory_increase:.1f}MB increase for 1000 products")
    
    def _create_mock_product_element(self, product_name):
        """Create a mock product element for benchmarking."""
        mock_element = Mock()
        
        # Mock text elements
        mock_name = Mock()
        mock_name.get_all_text.return_value = product_name
        
        mock_brand = Mock()
        mock_brand.get_all_text.return_value = "Benchmark Brand"
        
        mock_price = Mock()
        mock_price.get_all_text.return_value = "$29.99"
        
        mock_original_price = Mock()
        mock_original_price.get_all_text.return_value = "$39.99"
        
        mock_availability = Mock()
        mock_availability.get_all_text.return_value = "In stock"
        
        mock_sale_label = Mock()
        mock_sale_label.get_all_text.return_value = "Save 25%"
        
        # Mock attribute elements
        mock_rating = Mock()
        mock_rating.attrib = {'data-rating': '4.5'}
        
        mock_reviews = Mock()
        mock_reviews.attrib = {'data-reviews': '123'}
        
        mock_link = Mock()
        mock_link.attrib = {'href': f'/products/{product_name.lower().replace(" ", "-")}'}
        
        mock_image = Mock()
        mock_image.attrib = {'src': f'/images/{product_name.lower().replace(" ", "-")}.jpg'}
        
        # Set up css_first method
        def css_first_side_effect(selector):
            selector_map = {
                '.product-item__title': mock_name,
                '.product-item__vendor': mock_brand,
                '.price--highlight [data-money-convertible]': mock_price,
                '.price--compare [data-money-convertible]': mock_original_price,
                '.product-item__inventory': mock_availability,
                '.product-label--on-sale': mock_sale_label,
                '.stamped-badge[data-rating]': mock_rating,
                '.stamped-badge-caption[data-reviews]': mock_reviews,
                '.product-item__title a': mock_link,
                '.product-item__primary-image img': mock_image,
            }
            return selector_map.get(selector)
        
        mock_element.css_first.side_effect = css_first_side_effect
        
        return mock_element
    
    def _create_mock_sheets_service(self):
        """Create a mock Google Sheets service for benchmarking."""
        mock_service = Mock()
        
        # Mock spreadsheets operations
        mock_spreadsheets = Mock()
        mock_service.spreadsheets.return_value = mock_spreadsheets
        
        # Mock get operation
        mock_get = Mock()
        mock_get.execute.return_value = {
            'properties': {'title': 'Benchmark Spreadsheet'},
            'sheets': [{'properties': {'title': 'Benchmark_Products'}}],
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/benchmark_id'
        }
        mock_spreadsheets.get.return_value = mock_get
        
        # Mock batchUpdate operation
        mock_batch_update = Mock()
        mock_batch_update.execute.return_value = {}
        mock_spreadsheets.batchUpdate.return_value = mock_batch_update
        
        # Mock values operations
        mock_values = Mock()
        mock_spreadsheets.values.return_value = mock_values
        
        # Mock update operation
        mock_update = Mock()
        mock_update.execute.return_value = {}
        mock_values.update.return_value = mock_update
        
        # Mock append operation (simulate some delay for realism)
        def mock_append_execute():
            time.sleep(0.01)  # Simulate API latency
            return {'updates': {'updatedRows': 1}}
        
        mock_append = Mock()
        mock_append.execute.side_effect = mock_append_execute
        mock_values.append.return_value = mock_append
        
        return mock_service


@pytest.mark.integration
class TestRealWorldScenarios:
    """Integration tests for real-world scenarios and edge cases."""
    
    @patch('scrapling.fetchers.Fetcher')
    def test_pagination_handling_integration(self, mock_fetcher_class):
        """Test pagination handling in real-world scenario."""
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock multiple pages
        page1_response = Mock()
        page1_response.status = 200
        page1_response.css.return_value = [self._create_mock_product("Product 1")]
        
        # Mock pagination links
        mock_link = Mock()
        mock_link.attrib = {'href': '?page=2'}
        page1_response.css.return_value = [mock_link]  # For pagination
        
        page2_response = Mock()
        page2_response.status = 200
        page2_response.css.return_value = [self._create_mock_product("Product 2")]
        page2_response.css.return_value = []  # No more pagination
        
        # Set up fetcher to return different responses
        mock_fetcher.get.side_effect = [page1_response, page1_response, page2_response, page2_response]
        
        # Test scraper with pagination
        scraper = GarageGrownGearScraper(
            base_url="https://example.com/products",
            max_retries=1,
            retry_delay=0.1
        )
        
        with patch('time.sleep'):  # Speed up test
            products = scraper.scrape_all_products()
        
        # Should have products from both pages
        assert len(products) >= 1  # At least one product scraped
    
    def test_error_recovery_integration(self):
        """Test error recovery across integrated components."""
        from error_handling.retry_handler import RetryHandler
        from error_handling.exceptions import RetryableError
        
        # Test scenario: Network fails, then recovers
        retry_handler = RetryHandler(max_attempts=3)
        
        call_count = 0
        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise RetryableError("Network timeout")
            return f"Success after {call_count} attempts"
        
        with patch('time.sleep'):  # Speed up test
            result = retry_handler.execute(failing_operation)
        
        assert result == "Success after 3 attempts"
        assert call_count == 3
    
    def test_data_quality_integration(self):
        """Test data quality handling across the pipeline."""
        # Create mixed quality data
        mixed_data = [
            # Good data
            {
                'name': 'Good Product',
                'brand': 'Good Brand',
                'current_price': '$29.99',
                'original_price': '$39.99',
                'availability_status': 'In stock',
                'rating': '4.5',
                'reviews_count': '123',
                'product_url': 'https://example.com/good-product',
                'image_url': 'https://example.com/good-image.jpg',
                'sale_label': 'Save 25%'
            },
            # Bad data (missing required fields)
            {
                'name': '',  # Empty name
                'current_price': 'invalid',  # Invalid price
                'product_url': 'not-a-url'  # Invalid URL
            },
            # Partially good data
            {
                'name': 'Partial Product',
                'current_price': '$19.99',
                'product_url': 'https://example.com/partial-product',
                # Missing other fields
            }
        ]
        
        processor = ProductDataProcessor()
        processed_products = processor.process_products(mixed_data)
        
        # Should filter out bad data and process good/partial data
        assert len(processed_products) >= 1  # At least good data should pass
        
        # Verify good data was processed correctly
        good_product = next((p for p in processed_products if p.name == 'Good Product'), None)
        assert good_product is not None
        assert good_product.current_price == 29.99
        assert good_product.discount_percentage is not None
    
    def _create_mock_product(self, name):
        """Create a mock product element."""
        mock_element = Mock()
        
        mock_name = Mock()
        mock_name.get_all_text.return_value = name
        
        mock_brand = Mock()
        mock_brand.get_all_text.return_value = "Test Brand"
        
        mock_price = Mock()
        mock_price.get_all_text.return_value = "$29.99"
        
        def css_first_side_effect(selector):
            if '.product-item__title' in selector:
                return mock_name
            elif '.product-item__vendor' in selector:
                return mock_brand
            elif 'price--highlight' in selector:
                return mock_price
            return None
        
        mock_element.css_first.side_effect = css_first_side_effect
        
        return mock_element