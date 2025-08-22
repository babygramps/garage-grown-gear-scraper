#!/usr/bin/env python3
"""
Test runner script for the Garage Grown Gear scraper test suite.

This script provides different test execution modes:
- Unit tests only
- Integration tests only
- All tests
- Performance benchmarks
- Coverage reports
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print(f"\n❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return 1


def run_unit_tests(verbose=False):
    """Run unit tests only."""
    cmd = ["python", "-m", "pytest", "-m", "unit"]
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests only."""
    cmd = ["python", "-m", "pytest", "-m", "integration"]
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Integration Tests")


def run_all_tests(verbose=False):
    """Run all tests."""
    cmd = ["python", "-m", "pytest"]
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "All Tests")


def run_performance_tests(verbose=False):
    """Run performance benchmark tests."""
    cmd = ["python", "-m", "pytest", "-m", "slow"]
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Performance Benchmark Tests")


def run_coverage_tests(verbose=False):
    """Run tests with coverage reporting."""
    cmd = [
        "python", "-m", "pytest",
        "--cov=scraper",
        "--cov=data_processing", 
        "--cov=sheets_integration",
        "--cov=error_handling",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Tests with Coverage")


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function."""
    cmd = ["python", "-m", "pytest", test_path]
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, f"Specific Test: {test_path}")


def check_dependencies():
    """Check if required testing dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-mock", 
        "pytest-cov",
        "responses"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required testing packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required testing dependencies are installed")
    return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Test runner for Garage Grown Gear scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --unit                    # Run unit tests only
  python run_tests.py --integration             # Run integration tests only
  python run_tests.py --all                     # Run all tests
  python run_tests.py --performance             # Run performance benchmarks
  python run_tests.py --coverage                # Run tests with coverage
  python run_tests.py --specific test_scraper.py # Run specific test file
  python run_tests.py --check-deps              # Check dependencies only
        """
    )
    
    parser.add_argument(
        "--unit", 
        action="store_true",
        help="Run unit tests only"
    )
    
    parser.add_argument(
        "--integration",
        action="store_true", 
        help="Run integration tests only"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance benchmark tests"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    
    parser.add_argument(
        "--specific",
        type=str,
        help="Run specific test file or test function"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check if testing dependencies are installed"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Check dependencies first
    if args.check_deps:
        return 0 if check_dependencies() else 1
    
    if not check_dependencies():
        return 1
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Run tests based on arguments
    exit_code = 0
    
    if args.unit:
        exit_code = run_unit_tests(args.verbose)
    elif args.integration:
        exit_code = run_integration_tests(args.verbose)
    elif args.performance:
        exit_code = run_performance_tests(args.verbose)
    elif args.coverage:
        exit_code = run_coverage_tests(args.verbose)
    elif args.specific:
        exit_code = run_specific_test(args.specific, args.verbose)
    elif args.all:
        exit_code = run_all_tests(args.verbose)
    else:
        # Default: run unit tests
        print("No specific test type specified, running unit tests by default")
        print("Use --help to see all available options")
        exit_code = run_unit_tests(args.verbose)
    
    # Summary
    if exit_code == 0:
        print(f"\n🎉 All tests passed successfully!")
    else:
        print(f"\n💥 Tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())