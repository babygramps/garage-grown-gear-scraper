#!/usr/bin/env python3
"""
Advanced Data Quality Testing and Debugging Features
This script demonstrates advanced quality testing, alerting, and debugging capabilities.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

from scraper.garage_grown_gear_scraper import GarageGrownGearScraper
from data_processing.product_data_processor import ProductDataProcessor
from data_processing.quality_monitor import DataQualityMonitor, DataQualityAlert
from error_handling.logging_config import setup_logging

def test_quality_alerting():
    """Test the quality alerting system with custom thresholds."""
    print("\n🚨 TESTING QUALITY ALERTING SYSTEM")
    print("-" * 40)
    
    # Create a quality monitor with stricter thresholds
    strict_thresholds = {
        'completeness_rate': 95.0,    # Very strict
        'validity_rate': 98.0,        # Very strict
        'quality_score': 90.0,        # High standard
        'duplicate_rate': 2.0,        # Low tolerance
        'missing_price_rate': 5.0,    # Low tolerance
        'invalid_price_rate': 2.0     # Low tolerance
    }
    
    monitor = DataQualityMonitor(alert_thresholds=strict_thresholds)
    
    # Test with sample data that should trigger alerts
    test_products = [
        # Good products
        {'name': 'Product 1', 'current_price': 100.0, 'brand': 'Brand A', 'product_url': 'https://example.com/1', 'availability_status': 'Available'},
        {'name': 'Product 2', 'current_price': 200.0, 'brand': 'Brand B', 'product_url': 'https://example.com/2', 'availability_status': 'Available'},
        {'name': 'Product 3', 'current_price': 300.0, 'brand': 'Brand A', 'product_url': 'https://example.com/3', 'availability_status': 'Available'},
        
        # Products with issues to trigger alerts
        {'name': '', 'current_price': None, 'brand': '', 'product_url': '', 'availability_status': ''},  # Missing data
        {'name': 'Product 5', 'current_price': -50.0, 'brand': 'Brand C', 'product_url': 'not-a-url', 'availability_status': 'Available'},  # Invalid data
        {'name': 'Product 1', 'current_price': 100.0, 'brand': 'Brand A', 'product_url': 'https://example.com/1', 'availability_status': 'Available'},  # Duplicate
    ]
    
    # Analyze the test data
    metrics = monitor.analyze_data_quality(test_products)
    
    print(f"📊 Quality Analysis Results:")
    print(f"   Quality Score: {metrics.quality_score:.1f}/100")
    print(f"   Completeness: {metrics.completeness_rate:.1f}%")
    print(f"   Validity: {metrics.validity_rate:.1f}%")
    print(f"   Total Products: {metrics.total_products}")
    print(f"   Valid Products: {metrics.valid_products}")
    print(f"   Duplicates: {metrics.duplicate_products}")
    
    # Show alerts
    if monitor.alerts:
        print(f"\n🚨 QUALITY ALERTS TRIGGERED ({len(monitor.alerts)}):")
        for alert in monitor.alerts:
            severity_emoji = {'low': '💙', 'medium': '🟡', 'high': '🟠', 'critical': '🔴'}
            emoji = severity_emoji.get(alert.severity, '⚪')
            print(f"   {emoji} [{alert.severity.upper()}] {alert.alert_type}: {alert.message}")
    else:
        print("\n✅ No alerts triggered")
    
    return monitor, metrics

def test_historical_trends():
    """Test historical trend analysis."""
    print("\n📈 TESTING HISTORICAL TREND ANALYSIS")
    print("-" * 35)
    
    monitor = DataQualityMonitor()
    
    # Simulate multiple runs with different quality levels
    test_datasets = [
        # Run 1: High quality
        [{'name': f'Product {i}', 'current_price': 100.0 + i*10, 'brand': 'Brand A', 'product_url': f'https://example.com/{i}', 'availability_status': 'Available'} for i in range(10)],
        
        # Run 2: Medium quality (some missing data)
        [{'name': f'Product {i}' if i < 8 else '', 'current_price': 100.0 + i*10 if i < 9 else None, 'brand': 'Brand A', 'product_url': f'https://example.com/{i}', 'availability_status': 'Available'} for i in range(10)],
        
        # Run 3: Lower quality (more issues)
        [{'name': f'Product {i}' if i < 6 else '', 'current_price': 100.0 + i*10 if i < 7 else None, 'brand': 'Brand A' if i < 8 else '', 'product_url': f'https://example.com/{i}', 'availability_status': 'Available'} for i in range(10)],
        
        # Run 4: Improving quality
        [{'name': f'Product {i}' if i < 9 else '', 'current_price': 100.0 + i*10 if i < 8 else None, 'brand': 'Brand A', 'product_url': f'https://example.com/{i}', 'availability_status': 'Available'} for i in range(10)],
        
        # Run 5: High quality again
        [{'name': f'Product {i}', 'current_price': 100.0 + i*10, 'brand': 'Brand A', 'product_url': f'https://example.com/{i}', 'availability_status': 'Available'} for i in range(10)],
    ]
    
    # Process each dataset
    for i, dataset in enumerate(test_datasets, 1):
        metrics = monitor.analyze_data_quality(dataset)
        print(f"Run {i}: Quality Score {metrics.quality_score:.1f}, Completeness {metrics.completeness_rate:.1f}%, Validity {metrics.validity_rate:.1f}%")
    
    # Get comprehensive quality report with trends
    quality_report = monitor.get_quality_report(include_history=True)
    
    # Show trends
    trends = quality_report.get('historical_trends', {})
    if trends:
        print(f"\n📊 Historical Trends:")
        print(f"   Completeness Trend: {trends.get('completeness_trend', 'N/A')}")
        print(f"   Validity Trend: {trends.get('validity_trend', 'N/A')}")
        print(f"   Quality Trend: {trends.get('quality_trend', 'N/A')}")
        print(f"   Average Quality Score: {trends.get('avg_quality_score', 0):.1f}")
    
    # Show quality assessment
    quality_trend = quality_report.get('quality_trend', {})
    if quality_trend:
        print(f"\n🎯 Quality Assessment:")
        print(f"   Overall Assessment: {quality_trend.get('assessment', 'unknown').upper()}")
        print(f"   Trend Direction: {quality_trend.get('trend', 'unknown').upper()}")
        print(f"   Current Score: {quality_trend.get('current_score', 0):.1f}")
        recommendation = quality_trend.get('recommendation', '')
        if recommendation:
            print(f"   💡 Recommendation: {recommendation}")
    
    return monitor

def test_debug_mode():
    """Test debug mode with enhanced logging."""
    print("\n🐛 TESTING DEBUG MODE")
    print("-" * 20)
    
    # Set up debug logging
    logger = setup_logging(level="DEBUG", console=True, structured=False)
    
    print("✅ Debug logging enabled")
    print("   - This provides detailed information about:")
    print("     • Data extraction process")
    print("     • Validation steps")
    print("     • Quality analysis")
    print("     • Performance metrics")
    print("     • Error details")
    
    # You can run the main scraper with debug logging:
    print("\n💡 To run with debug logging:")
    print("   python main.py --log-level DEBUG --dry-run")
    print("   LOG_LEVEL=DEBUG python main.py")

def test_custom_validation():
    """Test custom validation rules."""
    print("\n🔧 TESTING CUSTOM VALIDATION")
    print("-" * 28)
    
    processor = ProductDataProcessor(enable_quality_monitoring=True)
    
    # Test with various edge cases
    test_cases = [
        # Valid product
        {'name': 'Valid Product', 'current_price': 99.99, 'brand': 'Good Brand', 'product_url': 'https://example.com/valid', 'availability_status': 'Available'},
        
        # Edge cases
        {'name': 'Very Expensive Product', 'current_price': 9999.99, 'brand': 'Luxury Brand', 'product_url': 'https://example.com/expensive', 'availability_status': 'Available'},
        {'name': 'Very Cheap Product', 'current_price': 0.01, 'brand': 'Budget Brand', 'product_url': 'https://example.com/cheap', 'availability_status': 'Available'},
        
        # Invalid cases
        {'name': 'Invalid Price Product', 'current_price': 0, 'brand': 'Test Brand', 'product_url': 'https://example.com/invalid', 'availability_status': 'Available'},
        {'name': 'Negative Price Product', 'current_price': -10.00, 'brand': 'Error Brand', 'product_url': 'https://example.com/negative', 'availability_status': 'Available'},
        {'name': 'Too Expensive Product', 'current_price': 99999.99, 'brand': 'Overpriced Brand', 'product_url': 'https://example.com/overpriced', 'availability_status': 'Available'},
        
        # Missing data
        {'name': '', 'current_price': 50.00, 'brand': 'Missing Name Brand', 'product_url': 'https://example.com/missing', 'availability_status': 'Available'},
        {'name': 'Missing URL Product', 'current_price': 50.00, 'brand': 'Test Brand', 'product_url': '', 'availability_status': 'Available'},
    ]
    
    print("Testing validation rules:")
    for i, test_case in enumerate(test_cases, 1):
        try:
            processed = processor.process_products([test_case])
            if processed:
                print(f"   ✅ Test {i}: PASSED - {test_case.get('name', 'Unnamed')} (${test_case.get('current_price', 'N/A')})")
            else:
                print(f"   ❌ Test {i}: FAILED - {test_case.get('name', 'Unnamed')} (${test_case.get('current_price', 'N/A')})")
        except Exception as e:
            print(f"   💥 Test {i}: ERROR - {str(e)}")

def main():
    print("🔬 ADVANCED DATA QUALITY TESTING SUITE")
    print("=" * 45)
    
    # Load environment
    load_dotenv()
    
    # Test 1: Quality Alerting System
    monitor, metrics = test_quality_alerting()
    
    # Test 2: Historical Trends
    trend_monitor = test_historical_trends()
    
    # Test 3: Debug Mode
    test_debug_mode()
    
    # Test 4: Custom Validation
    test_custom_validation()
    
    # Summary
    print("\n🎉 ADVANCED TESTING COMPLETE")
    print("=" * 30)
    print("✅ Quality alerting system tested")
    print("✅ Historical trend analysis tested")
    print("✅ Debug mode demonstrated")
    print("✅ Custom validation tested")
    
    print("\n💡 ADDITIONAL TESTING OPTIONS:")
    print("1. Run with quality report export:")
    print("   python main.py --export-quality-report --quality-report-format json")
    
    print("\n2. Run with strict monitoring:")
    print("   python main.py --export-quality-report --log-level DEBUG")
    
    print("\n3. Test change detection with quality:")
    print("   python main.py --enable-notifications --dry-run")
    
    print("\n📁 Quality reports are saved in the 'reports' folder")
    print("📊 Use the CSV reports for further analysis in Excel or other tools")

if __name__ == "__main__":
    main()
