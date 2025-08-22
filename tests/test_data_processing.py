"""
Tests for data processing and validation functionality.
"""

import unittest
from datetime import datetime
from data_processing import ProductDataProcessor, ValidationError, DataSanitizationError


class TestProductDataProcessor(unittest.TestCase):
    """Test cases for ProductDataProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ProductDataProcessor()
    
    def test_process_valid_product(self):
        """Test processing a valid product."""
        raw_product = {
            'name': 'Test Product',
            'brand': 'Test Brand',
            'current_price': '$29.99',
            'original_price': '$39.99',
            'availability_status': 'Available',
            'rating': '4.5',
            'reviews_count': '123',
            'product_url': 'https://www.garagegrowngear.com/products/test',
            'image_url': 'https://www.garagegrowngear.com/images/test.jpg',
            'sale_label': 'Save 25%'
        }
        
        products = self.processor.process_products([raw_product])
        
        self.assertEqual(len(products), 1)
        product = products[0]
        
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.brand, 'Test Brand')
        self.assertEqual(product.current_price, 29.99)
        self.assertEqual(product.original_price, 39.99)
        self.assertEqual(product.availability_status, 'Available')
        self.assertEqual(product.rating, 4.5)
        self.assertEqual(product.reviews_count, 123)
        self.assertIsNotNone(product.discount_percentage)
    
    def test_process_invalid_product(self):
        """Test processing an invalid product."""
        raw_product = {
            'name': '',  # Empty name should fail validation
            'current_price': 'invalid_price',
            'product_url': 'not_a_url'
        }
        
        products = self.processor.process_products([raw_product])
        
        # Should return empty list due to validation failures
        self.assertEqual(len(products), 0)
    
    def test_price_parsing(self):
        """Test price parsing functionality."""
        # Test valid prices
        self.assertEqual(self.processor.price_parser.parse_price('$29.99'), 29.99)
        self.assertEqual(self.processor.price_parser.parse_price('1,299.00'), 1299.00)
        self.assertEqual(self.processor.price_parser.parse_price('  $45.50  '), 45.50)
        
        # Test invalid prices
        self.assertIsNone(self.processor.price_parser.parse_price(''))
        self.assertIsNone(self.processor.price_parser.parse_price('invalid'))
        self.assertIsNone(self.processor.price_parser.parse_price(None))
    
    def test_discount_calculation(self):
        """Test discount percentage calculation."""
        # Test valid discount
        discount = self.processor.price_parser.calculate_discount_percentage(29.99, 39.99)
        self.assertAlmostEqual(discount, 25.0, places=1)
        
        # Test no discount
        discount = self.processor.price_parser.calculate_discount_percentage(39.99, 39.99)
        self.assertEqual(discount, 0.0)
        
        # Test invalid inputs
        self.assertIsNone(self.processor.price_parser.calculate_discount_percentage(0, 39.99))
        self.assertIsNone(self.processor.price_parser.calculate_discount_percentage(29.99, 0))


if __name__ == '__main__':
    unittest.main()