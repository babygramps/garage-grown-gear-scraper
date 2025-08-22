"""
Main entry point for the Garage Grown Gear scraper.
This file orchestrates the entire scraping workflow: scrape -> process -> store.
"""

import argparse
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import AppConfig
from error_handling.logging_config import setup_logging, ScraperLogger
from error_handling.monitoring import PerformanceMonitor, ScrapingMonitor
from error_handling.retry_handler import RetryHandler
from scraper.garage_grown_gear_scraper import GarageGrownGearScraper
from data_processing.product_data_processor import ProductDataProcessor, Product
from data_processing.change_detector import ChangeDetectionOrchestrator
from data_processing.quality_monitor import DataQualityMonitor
from sheets_integration.sheets_client import SheetsClient, SheetsConfig, ProductDataFormatter


class ScrapingOrchestrator:
    """Main orchestrator class that manages the complete scraping workflow."""
    
    def __init__(self, config: AppConfig, logger: ScraperLogger):
        self.config = config
        self.logger = logger
        self.performance_monitor = PerformanceMonitor()
        self.scraping_monitor = ScrapingMonitor(enable_system_monitoring=True)
        self.retry_handler = RetryHandler(
            max_retries=config.scraper.max_retries,
            base_delay=config.scraper.retry_delay
        )
        
        # Initialize components
        self.scraper = None
        self.data_processor = None
        self.sheets_client = None
        self.change_detector = None
        
    def initialize_components(self) -> bool:
        """Initialize all scraping components."""
        try:
            self.logger.info("Initializing scraping components...")
            
            # Check for GitHub Actions specific configuration
            proxy_list = []
            github_config_file = "github_actions_config.json"
            
            if os.path.exists(github_config_file):
                try:
                    import json
                    with open(github_config_file, 'r') as f:
                        github_config = json.load(f)
                    
                    # Override settings for GitHub Actions
                    if github_config.get('enhanced_delays'):
                        self.config.scraper.max_retries = github_config.get('max_retries', 8)
                        self.config.scraper.retry_delay = github_config.get('base_delay', 10.0)
                    
                    self.logger.info("Applied GitHub Actions enhanced configuration")
                except Exception as e:
                    self.logger.warning(f"Could not load GitHub Actions config: {e}")
            
            # Load proxy list if available
            proxy_file = "proxy_list.txt"
            if os.path.exists(proxy_file):
                try:
                    with open(proxy_file, 'r') as f:
                        proxy_list = [line.strip() for line in f if line.strip()]
                    self.logger.info(f"Loaded {len(proxy_list)} proxies from {proxy_file}")
                except Exception as e:
                    self.logger.warning(f"Could not load proxy list: {e}")
            
            # Initialize scraper with performance monitoring and proxies
            self.scraper = GarageGrownGearScraper(
                base_url=self.config.scraper.base_url,
                use_stealth=self.config.scraper.use_stealth_mode,
                max_retries=self.config.scraper.max_retries,
                retry_delay=self.config.scraper.retry_delay,
                enable_performance_monitoring=True,
                batch_size=50,
                proxy_list=proxy_list
            )
            
            # Initialize data processor with quality monitoring
            enable_quality = not getattr(self.config, 'disable_quality_monitoring', False)
            batch_size = getattr(self.config, 'batch_size', 100)
            
            self.data_processor = ProductDataProcessor(
                enable_performance_monitoring=True,
                enable_quality_monitoring=enable_quality,
                batch_size=batch_size
            )
            
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Initialize change detection system
            self.change_detector = ChangeDetectionOrchestrator(
                price_drop_threshold=self.config.notifications.price_drop_threshold,
                webhook_url=self.config.notifications.webhook_url,
                enable_notifications=self.config.notifications.enable_notifications,
                history_file="data/product_history.json"
            )
            
            # Initialize sheets client
            sheets_config = SheetsConfig(
                spreadsheet_id=self.config.sheets.spreadsheet_id,
                sheet_name=self.config.sheets.sheet_name
            )
            self.sheets_client = SheetsClient(sheets_config)
            
            # Authenticate with Google Sheets
            self.sheets_client.authenticate()
            
            # Ensure sheet exists and is properly formatted
            self.sheets_client.create_sheet_if_not_exists(self.config.sheets.sheet_name)
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}", exc_info=True)
            return False
    
    def scrape_products(self) -> List[Dict[str, Any]]:
        """Scrape all products from the website with comprehensive monitoring."""
        self.logger.info("Starting product scraping...")
        self.performance_monitor.start_operation('scraping')
        self.scraping_monitor.start_scraping_session()
        
        try:
            # Use retry handler for scraping operation
            raw_products = self.retry_handler.execute_with_retry(
                self.scraper.scrape_all_products
            )
            
            # Record scraping metrics
            self.scraping_monitor.record_page_scraped(len(raw_products))
            
            self.performance_monitor.end_operation(
                'scraping',
                products_found=len(raw_products)
            )
            
            self.logger.info(f"Successfully scraped {len(raw_products)} products")
            
            # Log scraper performance stats
            scraper_stats = self.scraper.get_performance_stats()
            if scraper_stats:
                self.logger.info("Scraper performance statistics", **scraper_stats)
            
            return raw_products
            
        except Exception as e:
            self.performance_monitor.end_operation('scraping', success=False)
            self.scraping_monitor.record_error(e, "scraping")
            self.logger.error(f"Scraping failed: {str(e)}", exc_info=True)
            raise
    
    def process_products(self, raw_products: List[Dict[str, Any]]) -> List[Product]:
        """Process and validate scraped product data with quality monitoring."""
        self.logger.info(f"Processing {len(raw_products)} products...")
        self.performance_monitor.start_operation('processing')
        
        try:
            processed_products = self.data_processor.process_products(raw_products)
            
            # Record processing metrics
            for _ in processed_products:
                self.scraping_monitor.record_product_processed(success=True)
            
            failed_count = len(raw_products) - len(processed_products)
            for _ in range(failed_count):
                self.scraping_monitor.record_product_processed(success=False)
            
            self.performance_monitor.end_operation(
                'processing',
                products_processed=len(processed_products),
                success_rate=len(processed_products) / len(raw_products) if raw_products else 0
            )
            
            # Get and log quality metrics
            quality_metrics = self.data_processor.get_quality_metrics()
            if quality_metrics:
                self.logger.info(
                    f"Data quality analysis: Quality score: {quality_metrics.quality_score:.1f}, "
                    f"Completeness: {quality_metrics.completeness_rate:.1f}%, "
                    f"Validity: {quality_metrics.validity_rate:.1f}%"
                )
            
            # Log data processor performance stats
            processor_stats = self.data_processor.get_performance_stats()
            if processor_stats:
                self.logger.info("Data processor performance statistics", **processor_stats)
            
            self.logger.info(f"Successfully processed {len(processed_products)} products")
            return processed_products
            
        except Exception as e:
            self.performance_monitor.end_operation('processing', success=False)
            self.scraping_monitor.record_error(e, "processing")
            self.logger.error(f"Product processing failed: {str(e)}", exc_info=True)
            raise
    
    def detect_changes_and_notify(self, products: List[Product]) -> Dict[str, Any]:
        """Detect changes in products and send notifications if needed."""
        self.logger.info("Detecting changes and generating notifications...")
        self.performance_monitor.start_operation('change_detection')
        
        try:
            change_results = self.change_detector.process_products_and_notify(products)
            
            self.performance_monitor.end_operation(
                'change_detection',
                changes_detected=change_results['changes_detected'],
                notification_sent=change_results['notification_sent']
            )
            
            self.logger.info(
                f"Change detection completed: {change_results['changes_detected']} changes detected, "
                f"notification sent: {change_results['notification_sent']}"
            )
            
            return change_results
            
        except Exception as e:
            self.performance_monitor.end_operation('change_detection', success=False)
            self.logger.error(f"Change detection failed: {str(e)}", exc_info=True)
            return {'changes_detected': 0, 'notification_sent': False, 'error': str(e)}
    
    def store_products(self, products: List[Product]) -> bool:
        """Store processed products in Google Sheets with monitoring."""
        if not products:
            self.logger.warning("No products to store")
            return True
        
        self.logger.info(f"Storing {len(products)} products to Google Sheets...")
        self.performance_monitor.start_operation('storing')
        
        try:
            # Convert products to sheet rows
            sheet_rows = [product.to_sheets_row() for product in products]
            
            # Record sheets operation
            self.scraping_monitor.record_sheets_operation(success=True)
            
            # Use retry handler for sheets operation
            self.retry_handler.execute_with_retry(
                lambda: self.sheets_client.append_data(
                    self.config.sheets.sheet_name,
                    sheet_rows
                )
            )
            
            self.performance_monitor.end_operation(
                'storing',
                products_stored=len(products)
            )
            
            self.logger.info(f"Successfully stored {len(products)} products")
            return True
            
        except Exception as e:
            self.performance_monitor.end_operation('storing', success=False)
            self.scraping_monitor.record_sheets_operation(success=False)
            self.scraping_monitor.record_error(e, "storing")
            self.logger.error(f"Failed to store products: {str(e)}", exc_info=True)
            return False
    
    def run_complete_workflow(self) -> Dict[str, Any]:
        """Execute the complete scraping workflow."""
        workflow_start = datetime.now()
        self.logger.info("Starting complete scraping workflow...")
        
        results = {
            'success': False,
            'start_time': workflow_start.isoformat(),
            'products_scraped': 0,
            'products_processed': 0,
            'products_stored': 0,
            'changes_detected': 0,
            'notification_sent': False,
            'errors': []
        }
        
        try:
            # Step 1: Initialize components
            if not self.initialize_components():
                results['errors'].append("Component initialization failed")
                return results
            
            # Step 2: Scrape products
            raw_products = self.scrape_products()
            results['products_scraped'] = len(raw_products)
            
            if not raw_products:
                self.logger.warning("No products found during scraping")
                results['success'] = True  # Not an error, just no products
                return results
            
            # Step 3: Process products
            processed_products = self.process_products(raw_products)
            results['products_processed'] = len(processed_products)
            
            if not processed_products:
                self.logger.warning("No products passed validation")
                results['errors'].append("All products failed validation")
                return results
            
            # Step 4: Detect changes and send notifications
            change_results = self.detect_changes_and_notify(processed_products)
            results['changes_detected'] = change_results.get('changes_detected', 0)
            results['notification_sent'] = change_results.get('notification_sent', False)
            
            if 'error' in change_results:
                results['errors'].append(f"Change detection error: {change_results['error']}")
            
            # Step 5: Store products
            if self.store_products(processed_products):
                results['products_stored'] = len(processed_products)
                results['success'] = True
            else:
                results['errors'].append("Failed to store products")
            
        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            results['errors'].append(error_msg)
        
        finally:
            # End scraping session and get comprehensive metrics
            session_metrics = self.scraping_monitor.end_scraping_session()
            
            # Log performance summary
            workflow_end = datetime.now()
            results['end_time'] = workflow_end.isoformat()
            results['duration_seconds'] = (workflow_end - workflow_start).total_seconds()
            
            # Generate comprehensive run summary
            quality_metrics = None
            if self.data_processor:
                quality_report = self.data_processor.get_quality_report()
                quality_metrics = quality_report.get('current_metrics')
            
            run_summary = self.scraping_monitor.generate_run_summary(
                products_processed=results.get('products_processed', 0),
                quality_metrics=quality_metrics
            )
            
            # Log comprehensive metrics
            self.logger.info("Session metrics", **session_metrics)
            self.logger.info("Run summary", **run_summary)
            
            # Export quality report if requested and available
            if (getattr(self.config, 'export_quality_report', False) and 
                quality_metrics and results.get('success')):
                try:
                    os.makedirs("reports", exist_ok=True)
                    report_format = getattr(self.config, 'quality_report_format', 'json')
                    report_filename = f"reports/quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{report_format}"
                    self.data_processor.export_quality_report(report_filename, report_format)
                    self.logger.info(f"Quality report exported to {report_filename}")
                except Exception as e:
                    self.logger.warning(f"Failed to export quality report: {str(e)}")
            
            # Log performance metrics
            performance_stats = self.performance_monitor.get_all_stats()
            self.logger.info("Workflow performance summary", **performance_stats)
            
            # Log final results
            self.logger.info("Workflow completed", **results)
        
        return results


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Garage Grown Gear scraper - Monitor sale page and save to Google Sheets"
    )
    
    parser.add_argument(
        '--config-file',
        type=str,
        help='Path to configuration file (optional)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (optional, logs to console by default)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run scraping without storing data to sheets'
    )
    
    parser.add_argument(
        '--max-retries',
        type=int,
        help='Maximum number of retry attempts for failed operations'
    )
    
    parser.add_argument(
        '--base-url',
        type=str,
        help='Override base URL for scraping'
    )
    
    parser.add_argument(
        '--spreadsheet-id',
        type=str,
        help='Override Google Sheets spreadsheet ID'
    )
    
    parser.add_argument(
        '--sheet-name',
        type=str,
        help='Override sheet name (default: Product_Data)'
    )
    
    parser.add_argument(
        '--no-stealth',
        action='store_true',
        help='Disable stealth mode for scraping'
    )
    
    parser.add_argument(
        '--enable-notifications',
        action='store_true',
        help='Enable notifications for significant changes'
    )
    
    parser.add_argument(
        '--webhook-url',
        type=str,
        help='Webhook URL for notifications (e.g., Slack, Discord)'
    )
    
    parser.add_argument(
        '--price-drop-threshold',
        type=float,
        default=20.0,
        help='Percentage threshold for significant price drops (default: 20.0)'
    )
    
    parser.add_argument(
        '--history-file',
        type=str,
        default='data/product_history.json',
        help='Path to product history file for change detection'
    )
    
    parser.add_argument(
        '--export-quality-report',
        action='store_true',
        help='Export detailed quality report after scraping'
    )
    
    parser.add_argument(
        '--quality-report-format',
        choices=['json', 'csv'],
        default='json',
        help='Format for quality report export (default: json)'
    )
    
    parser.add_argument(
        '--disable-quality-monitoring',
        action='store_true',
        help='Disable data quality monitoring and reporting'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for processing large datasets (default: 100)'
    )
    
    return parser.parse_args()


def validate_configuration(config: AppConfig) -> List[str]:
    """Validate configuration and return list of errors."""
    errors = []
    
    if not config.sheets.spreadsheet_id:
        errors.append("SPREADSHEET_ID environment variable or --spreadsheet-id argument is required")
    
    if not config.scraper.base_url:
        errors.append("Base URL is required")
    
    # Check for Google Sheets credentials
    credentials_env = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    if not credentials_env:
        errors.append("GOOGLE_SHEETS_CREDENTIALS environment variable is required")
    
    return errors


def main():
    """Main function that orchestrates the entire scraping workflow."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Load configuration from environment and override with CLI args
    config = AppConfig.from_env()
    
    # Apply CLI overrides
    if args.max_retries:
        config.scraper.max_retries = args.max_retries
    if args.base_url:
        config.scraper.base_url = args.base_url
    if args.spreadsheet_id:
        config.sheets.spreadsheet_id = args.spreadsheet_id
    if args.sheet_name:
        config.sheets.sheet_name = args.sheet_name
    if args.no_stealth:
        config.scraper.use_stealth_mode = False
    if args.log_level:
        config.logging.level = args.log_level
    if args.enable_notifications:
        config.notifications.enable_notifications = True
    if args.webhook_url:
        config.notifications.webhook_url = args.webhook_url
    if args.price_drop_threshold:
        config.notifications.price_drop_threshold = args.price_drop_threshold
    
    # Add quality monitoring options to config
    config.disable_quality_monitoring = args.disable_quality_monitoring
    config.batch_size = args.batch_size
    config.export_quality_report = args.export_quality_report
    config.quality_report_format = args.quality_report_format
    
    # Set up logging
    logger = setup_logging(
        level=config.logging.level,
        log_file=args.log_file,
        structured=True,
        console=True
    )
    
    # Validate configuration
    config_errors = validate_configuration(config)
    if config_errors:
        logger.error("Configuration validation failed:")
        for error in config_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    # Log startup information
    logger.info("Starting Garage Grown Gear scraper...")
    logger.info(f"Target URL: {config.scraper.base_url}")
    logger.info(f"Target Sheet: {config.sheets.spreadsheet_id}")
    logger.info(f"Dry run mode: {args.dry_run}")
    
    # Create and run orchestrator
    orchestrator = ScrapingOrchestrator(config, logger)
    
    try:
        if args.dry_run:
            logger.info("Running in dry-run mode - no data will be stored")
            # Initialize components except sheets client
            orchestrator.scraper = GarageGrownGearScraper(
                base_url=config.scraper.base_url,
                use_stealth=config.scraper.use_stealth_mode,
                max_retries=config.scraper.max_retries,
                retry_delay=config.scraper.retry_delay
            )
            orchestrator.data_processor = ProductDataProcessor(
                enable_performance_monitoring=True,
                enable_quality_monitoring=not args.disable_quality_monitoring,
                batch_size=args.batch_size
            )
            orchestrator.change_detector = ChangeDetectionOrchestrator(
                price_drop_threshold=config.notifications.price_drop_threshold,
                webhook_url=config.notifications.webhook_url,
                enable_notifications=False,  # Disable notifications in dry-run
                history_file=args.history_file
            )
            
            # Run scraping, processing, and change detection
            raw_products = orchestrator.scrape_products()
            processed_products = orchestrator.process_products(raw_products)
            change_results = orchestrator.detect_changes_and_notify(processed_products)
            
            logger.info(
                f"Dry run completed: {len(processed_products)} products would be stored, "
                f"{change_results.get('changes_detected', 0)} changes detected"
            )
            
        else:
            # Run complete workflow
            results = orchestrator.run_complete_workflow()
            
            if results['success']:
                logger.info("Scraping workflow completed successfully")
                sys.exit(0)
            else:
                logger.error("Scraping workflow failed")
                for error in results['errors']:
                    logger.error(f"  - {error}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()