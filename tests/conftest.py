"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
import os
import sys

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_scrapling_response():
    """Create a mock Scrapling response object."""
    mock_response = Mock()
    mock_response.status = 200
    mock_response.text = "<html><body>Test HTML</body></html>"
    return mock_response


@pytest.fixture
def mock_product_element():
    """Create a mock product element for testing extraction."""
    mock_element = Mock()
    
    # Mock text elements
    mock_name = Mock()
    mock_name.get_all_text.return_value = "Test Product"
    
    mock_brand = Mock()
    mock_brand.get_all_text.return_value = "Test Brand"
    
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
    mock_link.attrib = {'href': '/products/test-product'}
    
    mock_image = Mock()
    mock_image.attrib = {'src': '/images/test-product.jpg'}
    
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


@pytest.fixture
def sample_raw_product_data():
    """Sample raw product data for testing."""
    return {
        'name': 'Test Hiking Boots',
        'brand': 'Mountain Gear Co.',
        'current_price': '$89.99',
        'original_price': '$119.99',
        'availability_status': 'In stock',
        'rating': '4.5',
        'reviews_count': '87',
        'product_url': 'https://www.garagegrowngear.com/products/test-hiking-boots',
        'image_url': 'https://www.garagegrowngear.com/images/hiking-boots.jpg',
        'sale_label': 'Save 25%'
    }


@pytest.fixture
def sample_processed_product():
    """Sample processed product object for testing."""
    from data_processing.product_data_processor import Product
    
    return Product(
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        name='Test Hiking Boots',
        brand='Mountain Gear Co.',
        current_price=89.99,
        original_price=119.99,
        discount_percentage=25.0,
        availability_status='Available',
        rating=4.5,
        reviews_count=87,
        product_url='https://www.garagegrowngear.com/products/test-hiking-boots',
        sale_label='Save 25%',
        image_url='https://www.garagegrowngear.com/images/hiking-boots.jpg'
    )


@pytest.fixture
def mock_sheets_service():
    """Create a mock Google Sheets service."""
    mock_service = Mock()
    
    # Mock spreadsheets operations
    mock_spreadsheets = Mock()
    mock_service.spreadsheets.return_value = mock_spreadsheets
    
    # Mock get operation
    mock_get = Mock()
    mock_get.execute.return_value = {
        'properties': {'title': 'Test Spreadsheet'},
        'sheets': [
            {'properties': {'title': 'Sheet1'}},
            {'properties': {'title': 'Product_Data'}}
        ],
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
    
    # Mock clear operation
    mock_clear = Mock()
    mock_clear.execute.return_value = {}
    mock_values.clear.return_value = mock_clear
    
    return mock_service


@pytest.fixture
def mock_google_credentials():
    """Create mock Google service account credentials."""
    mock_credentials = Mock()
    mock_credentials.valid = True
    return mock_credentials


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'scraper': {
            'base_url': 'https://www.garagegrowngear.com/collections/sale-1',
            'max_retries': 3,
            'retry_delay': 1.0,
            'use_stealth': True
        },
        'sheets': {
            'spreadsheet_id': 'test_spreadsheet_id',
            'sheet_name': 'Test_Products'
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }


@pytest.fixture
def mock_performance_monitor():
    """Create a mock performance monitor."""
    mock_monitor = Mock()
    mock_monitor.get_metrics.return_value = {
        'scraping_duration': 30.5,
        'processing_duration': 5.2,
        'sheets_upload_duration': 2.1,
        'products_scraped': 150,
        'products_processed': 145,
        'products_saved': 145
    }
    return mock_monitor


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set test environment variables
    test_env_vars = {
        'GOOGLE_SHEETS_CREDENTIALS': 'dGVzdF9jcmVkZW50aWFscw==',  # base64 encoded 'test_credentials'
        'SPREADSHEET_ID': 'test_spreadsheet_id'
    }
    
    # Store original values
    original_values = {}
    for key, value in test_env_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original values
    for key, original_value in original_values.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_scrapling_fetcher():
    """Create a mock Scrapling Fetcher."""
    mock_fetcher = Mock()
    
    # Mock successful response
    mock_response = Mock()
    mock_response.status = 200
    mock_response.text = "<html><body>Test content</body></html>"
    
    mock_fetcher.get.return_value = mock_response
    
    return mock_fetcher


# Test data constants
TEST_HTML_PRODUCT = """
<div class="product-item">
    <h3 class="product-item__title">Test Product</h3>
    <div class="product-item__vendor">Test Brand</div>
    <div class="price--highlight">
        <span data-money-convertible>2999</span>
    </div>
    <div class="price--compare">
        <span data-money-convertible>3999</span>
    </div>
    <div class="product-label--on-sale">Save 25%</div>
    <div class="product-item__inventory">In stock</div>
    <div class="stamped-badge" data-rating="4.5"></div>
    <div class="stamped-badge-caption" data-reviews="123"></div>
    <a class="product-item__title" href="/products/test-product">Test Product</a>
    <img class="product-item__primary-image" src="/images/test-product.jpg" alt="Test Product">
</div>
"""

TEST_HTML_PAGE = f"""
<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
    <div class="products-grid">
        {TEST_HTML_PRODUCT}
        {TEST_HTML_PRODUCT.replace('Test Product', 'Another Product')}
    </div>
    <div class="pagination">
        <a href="?page=2">2</a>
        <a href="?page=3">3</a>
    </div>
</body>
</html>
"""


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to unit tests
        if "test_unit" in item.nodeid or "/test_" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.nodeid for keyword in ["scrape_all", "full_workflow", "end_to_end"]):
            item.add_marker(pytest.mark.slow)