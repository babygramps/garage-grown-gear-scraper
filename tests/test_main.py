"""
Unit tests for the main orchestration script.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from io import StringIO

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


class TestMainOrchestration(unittest.TestCase):
    """Test cases for main orchestration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = {
            'scraper': {
                'base_url': 'https://www.garagegrowngear.com/collections/sale-1',
                'max_retries': 3,
                'retry_delay': 1.0
            },
            'sheets': {
                'spreadsheet_id': 'test_spreadsheet_id',
                'sheet_name': 'Test_Sheet'
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    @patch('main.setup_logging')
    @patch('main.load_config')
    def test_setup_environment(self, mock_load_config, mock_setup_logging):
        """Test environment setup."""
        mock_load_config.return_value = self.mock_config
        
        config = main.setup_environment()
        
        mock_setup_logging.assert_called_once()
        mock_load_config.assert_called_once()
        self.assertEqual(config, self.mock_config)
    
    @patch('main.GarageGrownGearScraper')
    def test_create_scraper(self, mock_scraper_class):
        """Test scraper creation."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        scraper = main.create_scraper(self.mock_config['scraper'])
        
        mock_scraper_class.assert_called_once_with(
            base_url='https://www.garagegrowngear.com/collections/sale-1',
            max_retries=3,
            retry_delay=1.0
        )
        self.assertEqual(scraper, mock_scraper)
    
    @patch('main.create_sheets_client')
    def test_create_sheets_client_wrapper(self, mock_create_client):
        """Test sheets client creation wrapper."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        client = main.create_sheets_client_wrapper(self.mock_config['sheets'])
        
        mock_create_client.assert_called_once_with(
            'test_spreadsheet_id',
            'Test_Sheet'
        )
        self.assertEqual(client, mock_client)
    
    @patch('main.ProductDataProcessor')
    def test_create_data_processor(self, mock_processor_class):
        """Test data processor creation."""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        processor = main.create_data_processor()
        
        mock_processor_class.assert_called_once()
        self.assertEqual(processor, mock_processor)
    
    def test_scrape_products_success(self):
        """Test successful product scraping."""
        mock_scraper = Mock()
        mock_monitor = Mock()
        
        # Mock successful scraping
        mock_products = [
            {'name': 'Product 1', 'current_price': 29.99},
            {'name': 'Product 2', 'current_price': 19.99}
        ]
        mock_scraper.scrape_all_products.return_value = mock_products
        
        result = main.scrape_products(mock_scraper, mock_monitor)
        
        self.assertEqual(result, mock_products)
        mock_scraper.scrape_all_products.assert_called_once()
        mock_monitor.start_timer.assert_called_with('scraping')
        mock_monitor.end_timer.assert_called_with('scraping')
        mock_monitor.record_metric.assert_called_with('products_scraped', 2)
    
    def test_scrape_products_failure(self):
        """Test product scraping with failure."""
        mock_scraper = Mock()
        mock_monitor = Mock()
        
        # Mock scraping failure
        mock_scraper.scrape_all_products.side_effect = Exception("Scraping failed")
        
        with self.assertRaises(Exception) as context:
            main.scrape_products(mock_scraper, mock_monitor)
        
        self.assertEqual(str(context.exception), "Scraping failed")
        mock_monitor.start_timer.assert_called_with('scraping')
        mock_monitor.end_timer.assert_called_with('scraping')
    
    def test_process_products_success(self):
        """Test successful product processing."""
        mock_processor = Mock()
        mock_monitor = Mock()
        
        raw_products = [
            {'name': 'Product 1', 'current_price': '$29.99'},
            {'name': 'Product 2', 'current_price': '$19.99'}
        ]
        
        # Mock successful processing
        mock_processed = [Mock(), Mock()]
        mock_processor.process_products.return_value = mock_processed
        
        result = main.process_products(raw_products, mock_processor, mock_monitor)
        
        self.assertEqual(result, mock_processed)
        mock_processor.process_products.assert_called_once_with(raw_products)
        mock_monitor.start_timer.assert_called_with('processing')
        mock_monitor.end_timer.assert_called_with('processing')
        mock_monitor.record_metric.assert_called_with('products_processed', 2)
    
    def test_process_products_failure(self):
        """Test product processing with failure."""
        mock_processor = Mock()
        mock_monitor = Mock()
        
        raw_products = [{'name': 'Product 1'}]
        
        # Mock processing failure
        mock_processor.process_products.side_effect = Exception("Processing failed")
        
        with self.assertRaises(Exception) as context:
            main.process_products(raw_products, mock_processor, mock_monitor)
        
        self.assertEqual(str(context.exception), "Processing failed")
        mock_monitor.start_timer.assert_called_with('processing')
        mock_monitor.end_timer.assert_called_with('processing')
    
    def test_save_to_sheets_success(self):
        """Test successful saving to Google Sheets."""
        mock_client = Mock()
        mock_monitor = Mock()
        
        # Mock processed products
        mock_product1 = Mock()
        mock_product1.to_sheets_row.return_value = ['2024-01-01', 'Product 1', 'Brand A', 29.99]
        
        mock_product2 = Mock()
        mock_product2.to_sheets_row.return_value = ['2024-01-01', 'Product 2', 'Brand B', 19.99]
        
        processed_products = [mock_product1, mock_product2]
        
        main.save_to_sheets(processed_products, mock_client, mock_monitor, 'Test_Sheet')
        
        # Verify sheet operations
        mock_client.create_sheet_if_not_exists.assert_called_once_with('Test_Sheet')
        mock_client.append_data.assert_called_once()
        
        # Verify monitoring
        mock_monitor.start_timer.assert_called_with('sheets_upload')
        mock_monitor.end_timer.assert_called_with('sheets_upload')
        mock_monitor.record_metric.assert_called_with('products_saved', 2)
    
    def test_save_to_sheets_empty_products(self):
        """Test saving empty product list to sheets."""
        mock_client = Mock()
        mock_monitor = Mock()
        
        main.save_to_sheets([], mock_client, mock_monitor, 'Test_Sheet')
        
        # Should still create sheet but not append data
        mock_client.create_sheet_if_not_exists.assert_called_once_with('Test_Sheet')
        mock_client.append_data.assert_not_called()
        mock_monitor.record_metric.assert_called_with('products_saved', 0)
    
    def test_save_to_sheets_failure(self):
        """Test saving to sheets with failure."""
        mock_client = Mock()
        mock_monitor = Mock()
        
        # Mock sheet creation failure
        mock_client.create_sheet_if_not_exists.side_effect = Exception("Sheets error")
        
        processed_products = [Mock()]
        
        with self.assertRaises(Exception) as context:
            main.save_to_sheets(processed_products, mock_client, mock_monitor, 'Test_Sheet')
        
        self.assertEqual(str(context.exception), "Sheets error")
        mock_monitor.start_timer.assert_called_with('sheets_upload')
        mock_monitor.end_timer.assert_called_with('sheets_upload')
    
    @patch('main.ChangeDetector')
    def test_detect_changes_success(self, mock_detector_class):
        """Test successful change detection."""
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_monitor = Mock()
        
        processed_products = [Mock(), Mock()]
        
        # Mock change detection results
        mock_changes = {
            'new_products': 1,
            'price_changes': 2,
            'status_changes': 0
        }
        mock_detector.detect_changes.return_value = mock_changes
        
        result = main.detect_changes(processed_products, mock_monitor)
        
        self.assertEqual(result, mock_changes)
        mock_detector.detect_changes.assert_called_once_with(processed_products)
        mock_monitor.start_timer.assert_called_with('change_detection')
        mock_monitor.end_timer.assert_called_with('change_detection')
    
    @patch('main.ChangeDetector')
    def test_detect_changes_failure(self, mock_detector_class):
        """Test change detection with failure."""
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_monitor = Mock()
        
        # Mock change detection failure
        mock_detector.detect_changes.side_effect = Exception("Change detection failed")
        
        processed_products = [Mock()]
        
        with self.assertRaises(Exception) as context:
            main.detect_changes(processed_products, mock_monitor)
        
        self.assertEqual(str(context.exception), "Change detection failed")
        mock_monitor.start_timer.assert_called_with('change_detection')
        mock_monitor.end_timer.assert_called_with('change_detection')
    
    def test_generate_summary_report(self):
        """Test summary report generation."""
        mock_monitor = Mock()
        
        # Mock metrics
        mock_metrics = {
            'products_scraped': 150,
            'products_processed': 145,
            'products_saved': 145,
            'scraping_duration': 30.5,
            'processing_duration': 5.2,
            'sheets_upload_duration': 2.1
        }
        mock_monitor.get_metrics.return_value = mock_metrics
        
        changes = {
            'new_products': 5,
            'price_changes': 12,
            'status_changes': 2
        }
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main.generate_summary_report(mock_monitor, changes)
            
            output = mock_stdout.getvalue()
            
            # Verify report contains key information
            self.assertIn("Scraping Summary Report", output)
            self.assertIn("150 products scraped", output)
            self.assertIn("145 products processed", output)
            self.assertIn("5 new products", output)
            self.assertIn("12 price changes", output)
    
    @patch('main.setup_environment')
    @patch('main.create_scraper')
    @patch('main.create_sheets_client_wrapper')
    @patch('main.create_data_processor')
    @patch('main.PerformanceMonitor')
    @patch('main.scrape_products')
    @patch('main.process_products')
    @patch('main.save_to_sheets')
    @patch('main.detect_changes')
    @patch('main.generate_summary_report')
    def test_main_workflow_success(self, mock_report, mock_detect, mock_save, 
                                 mock_process, mock_scrape, mock_monitor_class,
                                 mock_processor, mock_sheets, mock_scraper, mock_setup):
        """Test complete main workflow success."""
        # Mock all components
        mock_setup.return_value = self.mock_config
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        mock_sheets_instance = Mock()
        mock_sheets.return_value = mock_sheets_instance
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor
        
        # Mock workflow steps
        raw_products = [{'name': 'Product 1'}]
        processed_products = [Mock()]
        changes = {'new_products': 1}
        
        mock_scrape.return_value = raw_products
        mock_process.return_value = processed_products
        mock_detect.return_value = changes
        
        # Run main workflow
        main.main()
        
        # Verify all steps were called
        mock_setup.assert_called_once()
        mock_scraper.assert_called_once()
        mock_sheets.assert_called_once()
        mock_processor.assert_called_once()
        mock_scrape.assert_called_once_with(mock_scraper_instance, mock_monitor)
        mock_process.assert_called_once_with(raw_products, mock_processor_instance, mock_monitor)
        mock_save.assert_called_once_with(processed_products, mock_sheets_instance, mock_monitor, 'Test_Sheet')
        mock_detect.assert_called_once_with(processed_products, mock_monitor)
        mock_report.assert_called_once_with(mock_monitor, changes)
    
    @patch('main.setup_environment')
    @patch('main.create_scraper')
    @patch('main.scrape_products')
    @patch('sys.exit')
    def test_main_workflow_scraping_failure(self, mock_exit, mock_scrape, mock_scraper, mock_setup):
        """Test main workflow with scraping failure."""
        # Mock setup
        mock_setup.return_value = self.mock_config
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        
        # Mock scraping failure
        mock_scrape.side_effect = Exception("Scraping failed")
        
        # Run main workflow
        main.main()
        
        # Verify error handling
        mock_scrape.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('argparse.ArgumentParser')
    def test_parse_arguments(self, mock_parser_class):
        """Test command line argument parsing."""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        
        mock_args = Mock()
        mock_args.config = 'custom_config.json'
        mock_args.verbose = True
        mock_args.dry_run = False
        mock_parser.parse_args.return_value = mock_args
        
        args = main.parse_arguments()
        
        self.assertEqual(args, mock_args)
        mock_parser.add_argument.assert_called()  # Verify arguments were added
    
    @patch('builtins.open')
    @patch('json.load')
    def test_load_config_from_file(self, mock_json_load, mock_open):
        """Test loading configuration from file."""
        mock_json_load.return_value = self.mock_config
        
        config = main.load_config('test_config.json')
        
        mock_open.assert_called_once_with('test_config.json', 'r')
        mock_json_load.assert_called_once()
        self.assertEqual(config, self.mock_config)
    
    @patch('os.getenv')
    def test_load_config_from_env(self, mock_getenv):
        """Test loading configuration from environment variables."""
        # Mock environment variables
        env_vars = {
            'SCRAPER_BASE_URL': 'https://example.com',
            'SCRAPER_MAX_RETRIES': '5',
            'SHEETS_SPREADSHEET_ID': 'env_spreadsheet_id',
            'SHEETS_SHEET_NAME': 'Env_Sheet'
        }
        mock_getenv.side_effect = lambda key, default=None: env_vars.get(key, default)
        
        config = main.load_config_from_env()
        
        self.assertEqual(config['scraper']['base_url'], 'https://example.com')
        self.assertEqual(config['scraper']['max_retries'], 5)
        self.assertEqual(config['sheets']['spreadsheet_id'], 'env_spreadsheet_id')
        self.assertEqual(config['sheets']['sheet_name'], 'Env_Sheet')


if __name__ == '__main__':
    unittest.main()