#!/usr/bin/env python3
"""
Test the full workflow without Google Sheets configuration.
"""

import os
from scraper.garage_grown_gear_scraper import GarageGrownGearScraper
from data_processing.product_data_processor import ProductDataProcessor
from data_processing.change_detector import ChangeDetectionOrchestrator
from error_handling.monitoring import ScrapingMonitor

def main():
    print("🚀 Testing Full Workflow (Dry Run)")
    print("=" * 60)
    
    try:
        # Initialize monitoring
        print("1. Initializing monitoring...")
        scraping_monitor = ScrapingMonitor(enable_system_monitoring=True)
        scraping_monitor.start_scraping_session()
        print("   ✅ Monitoring initialized")
        
        # Initialize scraper with performance monitoring
        print("\n2. Initializing scraper...")
        scraper = GarageGrownGearScraper(
            enable_performance_monitoring=True,
            batch_size=50
        )
        print("   ✅ Scraper initialized with performance monitoring")
        
        # Initialize data processor with quality monitoring
        print("\n3. Initializing data processor...")
        processor = ProductDataProcessor(
            enable_performance_monitoring=True,
            enable_quality_monitoring=True,
            batch_size=100
        )
        print("   ✅ Data processor initialized with quality monitoring")
        
        # Initialize change detector (without notifications)
        print("\n4. Initializing change detector...")
        os.makedirs("data", exist_ok=True)
        change_detector = ChangeDetectionOrchestrator(
            price_drop_threshold=20.0,
            webhook_url="",
            enable_notifications=False,
            history_file="data/test_product_history.json"
        )
        print("   ✅ Change detector initialized")
        
        # Step 1: Scrape products
        print("\n5. Scraping products...")
        raw_products = scraper.scrape_all_products()
        scraping_monitor.record_page_scraped(len(raw_products))
        print(f"   ✅ Scraped {len(raw_products)} products")
        
        # Get scraper performance stats
        scraper_stats = scraper.get_performance_stats()
        if scraper_stats:
            print(f"   📊 Scraper performance: {len(scraper_stats.get('operations', {}))} operations tracked")
        
        # Step 2: Process products
        print("\n6. Processing products...")
        processed_products = processor.process_products(raw_products)
        
        # Record processing results
        for _ in processed_products:
            scraping_monitor.record_product_processed(success=True)
        failed_count = len(raw_products) - len(processed_products)
        for _ in range(failed_count):
            scraping_monitor.record_product_processed(success=False)
        
        print(f"   ✅ Processed {len(processed_products)} products")
        print(f"   ⚠️  Failed to process {failed_count} products")
        
        # Get quality metrics
        quality_metrics = processor.get_quality_metrics()
        if quality_metrics:
            print(f"   📊 Quality Score: {quality_metrics.quality_score:.1f}/100")
            print(f"   📊 Completeness: {quality_metrics.completeness_rate:.1f}%")
            print(f"   📊 Validity: {quality_metrics.validity_rate:.1f}%")
        
        # Step 3: Change detection
        print("\n7. Detecting changes...")
        change_results = change_detector.process_products_and_notify(processed_products)
        print(f"   ✅ Change detection completed")
        print(f"   📊 Changes detected: {change_results.get('changes_detected', 0)}")
        
        # Step 4: Generate reports
        print("\n8. Generating reports...")
        
        # Performance report
        processor_stats = processor.get_performance_stats()
        if processor_stats:
            print(f"   📊 Data processor operations: {len(processor_stats.get('operations', {}))}")
        
        # Quality report
        quality_report = processor.get_quality_report()
        if quality_report:
            print(f"   📊 Quality report generated with {len(quality_report.get('recent_alerts', []))} recent alerts")
        
        # Export quality report
        try:
            os.makedirs("reports", exist_ok=True)
            from datetime import datetime
            report_filename = f"reports/test_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            processor.export_quality_report(report_filename, 'json')
            print(f"   💾 Quality report exported to {report_filename}")
        except Exception as e:
            print(f"   ⚠️  Failed to export quality report: {str(e)}")
        
        # End monitoring session
        session_metrics = scraping_monitor.end_scraping_session()
        
        # Generate run summary
        run_summary = scraping_monitor.generate_run_summary(
            products_processed=len(processed_products),
            quality_metrics=quality_report.get('current_metrics') if quality_report else None
        )
        
        print(f"\n9. Final Summary:")
        print(f"   📦 Products scraped: {len(raw_products)}")
        print(f"   ✅ Products processed: {len(processed_products)}")
        print(f"   📊 Success rate: {(len(processed_products)/len(raw_products)*100):.1f}%")
        print(f"   🔄 Changes detected: {change_results.get('changes_detected', 0)}")
        
        if quality_metrics:
            print(f"   🎯 Quality score: {quality_metrics.quality_score:.1f}/100")
        
        if session_metrics:
            duration = session_metrics.get('scraping_metrics', {}).get('duration_seconds', 0)
            print(f"   ⏱️  Total duration: {duration:.1f} seconds")
        
        # Show sample products
        if processed_products:
            print(f"\n10. Sample Products:")
            for i, product in enumerate(processed_products[:3]):
                name = product.name[:40] if hasattr(product, 'name') else 'Unknown'
                brand = product.brand[:15] if hasattr(product, 'brand') else 'Unknown'
                price = f"${product.current_price:.2f}" if hasattr(product, 'current_price') and product.current_price else 'No price'
                print(f"    {i+1}. {name} | {brand} | {price}")
        
        print(f"\n✅ Full workflow test completed successfully!")
        print(f"\n💡 Next steps:")
        print(f"   - Set up Google Sheets credentials")
        print(f"   - Run: python main.py --dry-run")
        print(f"   - Run: python main.py (for full execution)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow test failed:")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 All workflow components are working correctly!")
    else:
        print(f"\n⚠️  Workflow test failed. Check the error messages above.")