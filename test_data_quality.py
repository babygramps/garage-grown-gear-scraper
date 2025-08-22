#!/usr/bin/env python3
"""
Data Quality Testing Script for Garage Grown Gear Scraper
This script demonstrates and tests all the data quality monitoring features.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

from scraper.garage_grown_gear_scraper import GarageGrownGearScraper
from data_processing.product_data_processor import ProductDataProcessor
from error_handling.logging_config import setup_logging

def main():
    print("🔬 DATA QUALITY TESTING SUITE")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Set up logging
    logger = setup_logging(level="INFO", console=True, structured=False)
    
    # Step 1: Run scraper to get fresh data
    print("\n1. 🕷️  SCRAPING FRESH DATA")
    print("-" * 30)
    
    scraper = GarageGrownGearScraper(
        base_url=os.getenv("BASE_URL", "https://www.garagegrowngear.com/collections/sale-1"),
        use_stealth=True,
        max_retries=3,
        enable_performance_monitoring=True
    )
    
    try:
        raw_products = scraper.scrape_all_products()
        print(f"✅ Scraped {len(raw_products)} raw products")
    except Exception as e:
        print(f"❌ Scraping failed: {str(e)}")
        return
    
    # Step 2: Initialize data processor with quality monitoring
    print("\n2. 🔧 INITIALIZING DATA PROCESSOR WITH QUALITY MONITORING")
    print("-" * 55)
    
    processor = ProductDataProcessor(
        enable_performance_monitoring=True,
        enable_quality_monitoring=True,  # This is key!
        batch_size=50
    )
    
    # Step 3: Process data and analyze quality
    print("\n3. 📊 PROCESSING DATA & ANALYZING QUALITY")
    print("-" * 40)
    
    processed_products = processor.process_products(raw_products)
    print(f"✅ Processed {len(processed_products)} products successfully")
    print(f"❌ Failed to process {len(raw_products) - len(processed_products)} products")
    
    # Step 4: Get detailed quality metrics
    print("\n4. 📈 QUALITY METRICS ANALYSIS")
    print("-" * 30)
    
    quality_metrics = processor.get_quality_metrics()
    if quality_metrics:
        print(f"📊 Overall Quality Score: {quality_metrics.quality_score:.1f}/100")
        print(f"📋 Data Completeness: {quality_metrics.completeness_rate:.1f}%")
        print(f"✅ Data Validity: {quality_metrics.validity_rate:.1f}%")
        print(f"📦 Total Products Analyzed: {quality_metrics.total_products}")
        print(f"✅ Valid Products: {quality_metrics.valid_products}")
        print(f"❌ Invalid Products: {quality_metrics.invalid_products}")
        
        # Field completeness breakdown
        print(f"\n📋 Field Completeness Breakdown:")
        print(f"   Missing Names: {quality_metrics.missing_names}")
        print(f"   Missing Prices: {quality_metrics.missing_prices}")
        print(f"   Missing URLs: {quality_metrics.missing_urls}")
        print(f"   Missing Brands: {quality_metrics.missing_brands}")
        print(f"   Missing Availability: {quality_metrics.missing_availability}")
        
        # Data validity breakdown
        print(f"\n✅ Data Validity Breakdown:")
        print(f"   Invalid Prices: {quality_metrics.invalid_prices}")
        print(f"   Invalid URLs: {quality_metrics.invalid_urls}")
        print(f"   Invalid Ratings: {quality_metrics.invalid_ratings}")
        print(f"   Invalid Discounts: {quality_metrics.invalid_discounts}")
        
        # Consistency checks
        print(f"\n🔄 Data Consistency:")
        print(f"   Price Inconsistencies: {quality_metrics.price_inconsistencies}")
        print(f"   Duplicate Products: {quality_metrics.duplicate_products}")
        
        # Summary statistics
        if quality_metrics.avg_price:
            print(f"\n💰 Price Statistics:")
            print(f"   Average Price: ${quality_metrics.avg_price:.2f}")
            if quality_metrics.price_range:
                print(f"   Price Range: ${quality_metrics.price_range['min']:.2f} - ${quality_metrics.price_range['max']:.2f}")
                print(f"   Median Price: ${quality_metrics.price_range['median']:.2f}")
        
        # Brand and availability distribution
        print(f"\n🏷️  Brand Distribution:")
        for brand, count in quality_metrics.brand_distribution.items():
            print(f"   {brand}: {count} products")
        
        print(f"\n📦 Availability Distribution:")
        for status, count in quality_metrics.availability_distribution.items():
            print(f"   {status}: {count} products")
    
    # Step 5: Get comprehensive quality report
    print("\n5. 📄 COMPREHENSIVE QUALITY REPORT")
    print("-" * 35)
    
    quality_report = processor.get_quality_report()
    if quality_report:
        print(f"📅 Report Generated: {quality_report.get('generated_at', 'Unknown')}")
        
        # Recent alerts
        recent_alerts = quality_report.get('recent_alerts', [])
        if recent_alerts:
            print(f"🚨 Recent Quality Alerts ({len(recent_alerts)}):")
            for alert in recent_alerts[-5:]:  # Show last 5 alerts
                severity_emoji = {'low': '💙', 'medium': '🟡', 'high': '🟠', 'critical': '🔴'}
                emoji = severity_emoji.get(alert.get('severity', 'medium'), '⚪')
                print(f"   {emoji} [{alert.get('severity', 'unknown').upper()}] {alert.get('message', 'No message')}")
        else:
            print("✅ No quality alerts - data quality looks good!")
        
        # Alert summary
        alert_summary = quality_report.get('alert_summary', {})
        if alert_summary.get('total_alerts', 0) > 0:
            print(f"\n📊 Alert Summary:")
            print(f"   Total Alerts: {alert_summary.get('total_alerts', 0)}")
            
            by_type = alert_summary.get('by_type', {})
            if by_type:
                print(f"   By Type: {', '.join([f'{k}: {v}' for k, v in by_type.items()])}")
            
            by_severity = alert_summary.get('by_severity', {})
            if by_severity:
                print(f"   By Severity: {', '.join([f'{k}: {v}' for k, v in by_severity.items()])}")
        
        # Historical trends (if available)
        trends = quality_report.get('historical_trends', {})
        if trends:
            print(f"\n📈 Quality Trends:")
            print(f"   Completeness Trend: {trends.get('completeness_trend', 'N/A')}")
            print(f"   Validity Trend: {trends.get('validity_trend', 'N/A')}")
            print(f"   Quality Trend: {trends.get('quality_trend', 'N/A')}")
            print(f"   Average Quality Score: {trends.get('avg_quality_score', 0):.1f}")
        
        # Quality trend assessment
        quality_trend = quality_report.get('quality_trend', {})
        if quality_trend:
            print(f"\n🎯 Quality Assessment:")
            print(f"   Overall Assessment: {quality_trend.get('assessment', 'unknown').upper()}")
            print(f"   Trend: {quality_trend.get('trend', 'unknown').upper()}")
            print(f"   Current Score: {quality_trend.get('current_score', 0):.1f}")
            recommendation = quality_trend.get('recommendation', '')
            if recommendation:
                print(f"   💡 Recommendation: {recommendation}")
    
    # Step 6: Export quality reports
    print("\n6. 💾 EXPORTING QUALITY REPORTS")
    print("-" * 30)
    
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export JSON report
    try:
        json_filename = f"reports/quality_report_{timestamp}.json"
        processor.export_quality_report(json_filename, 'json')
        print(f"✅ JSON report exported: {json_filename}")
        
        # Show file size
        file_size = os.path.getsize(json_filename)
        print(f"   📄 File size: {file_size:,} bytes")
    except Exception as e:
        print(f"❌ Failed to export JSON report: {str(e)}")
    
    # Export CSV report
    try:
        csv_filename = f"reports/quality_metrics_{timestamp}.csv"
        processor.export_quality_report(csv_filename, 'csv')
        print(f"✅ CSV report exported: {csv_filename}")
        
        # Show file size
        file_size = os.path.getsize(csv_filename)
        print(f"   📄 File size: {file_size:,} bytes")
    except Exception as e:
        print(f"❌ Failed to export CSV report: {str(e)}")
    
    # Step 7: Performance statistics
    print("\n7. ⚡ PERFORMANCE STATISTICS")
    print("-" * 28)
    
    perf_stats = processor.get_performance_stats()
    if perf_stats:
        operations = perf_stats.get('operations', {})
        for op_name, op_stats in operations.items():
            print(f"📊 {op_name.replace('_', ' ').title()}:")
            print(f"   Total Runs: {op_stats.get('total_runs', 0)}")
            print(f"   Average Duration: {op_stats.get('average_duration', 0):.3f}s")
            print(f"   Total Duration: {op_stats.get('total_duration', 0):.3f}s")
    
    # Step 8: Summary and recommendations
    print("\n8. 🎯 SUMMARY & RECOMMENDATIONS")
    print("-" * 32)
    
    if quality_metrics:
        score = quality_metrics.quality_score
        
        if score >= 90:
            print("🌟 EXCELLENT: Your data quality is outstanding!")
            print("   ✅ Continue current practices")
            print("   ✅ Consider this a baseline for monitoring")
        elif score >= 80:
            print("👍 GOOD: Your data quality is solid with room for improvement")
            print("   💡 Focus on improving completeness and reducing missing data")
            print("   📊 Monitor trends to prevent quality degradation")
        elif score >= 70:
            print("⚠️  FAIR: Your data quality needs attention")
            print("   🔧 Review data extraction selectors")
            print("   📋 Focus on required field validation")
            print("   🔄 Check for website structure changes")
        else:
            print("🚨 POOR: Your data quality requires immediate attention")
            print("   🛠️  Review scraping logic and selectors")
            print("   📝 Implement additional validation rules")
            print("   🔍 Debug extraction process step by step")
        
        # Specific recommendations based on metrics
        if quality_metrics.missing_prices > 0:
            print(f"   💰 PRIORITY: Fix price extraction ({quality_metrics.missing_prices} missing prices)")
        
        if quality_metrics.missing_names > 0:
            print(f"   🏷️  PRIORITY: Fix name extraction ({quality_metrics.missing_names} missing names)")
        
        if quality_metrics.duplicate_products > 0:
            print(f"   🔄 OPTIMIZE: Remove duplicate detection logic ({quality_metrics.duplicate_products} duplicates)")
    
    print("\n🎉 Data quality testing completed!")
    print("📁 Check the 'reports' folder for detailed quality reports")

if __name__ == "__main__":
    main()
