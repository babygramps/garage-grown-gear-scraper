# Test Suite Documentation

This directory contains comprehensive tests for the Garage Grown Gear scraper project.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── pytest.ini              # Pytest configuration file
├── run_tests.py            # Test runner script
├── README.md               # This documentation
├── test_scraper.py         # Unit tests for scraper module
├── test_data_processing.py # Unit tests for data processing (existing)
├── test_sheets_integration.py # Unit tests for Google Sheets (existing)
├── test_error_handling.py  # Unit tests for error handling
├── test_main.py            # Unit tests for main orchestration
└── test_integration.py     # Integration and performance tests
```

## Test Categories

### Unit Tests
- **test_scraper.py**: Tests for the web scraping functionality
- **test_data_processing.py**: Tests for product data processing and validation
- **test_sheets_integration.py**: Tests for Google Sheets client operations
- **test_error_handling.py**: Tests for error handling and retry mechanisms
- **test_main.py**: Tests for main orchestration and workflow

### Integration Tests
- **test_integration.py**: End-to-end workflow tests and performance benchmarks

## Running Tests

### Prerequisites

Install testing dependencies:
```bash
pip install pytest pytest-mock pytest-cov responses freezegun
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Quick Start

```bash
# Run all unit tests
python tests/run_tests.py --unit

# Run all integration tests  
python tests/run_tests.py --integration

# Run all tests
python tests/run_tests.py --all

# Run with coverage
python tests/run_tests.py --coverage

# Run performance benchmarks
python tests/run_tests.py --performance
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run with coverage
pytest --cov=scraper --cov=data_processing --cov=sheets_integration --cov=error_handling

# Run specific test file
pytest tests/test_scraper.py

# Run specific test function
pytest tests/test_scraper.py::TestGarageGrownGearScraper::test_extract_product_data_complete

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests  
- `@pytest.mark.slow`: Slow running tests (performance benchmarks)

## Test Coverage

The test suite aims for comprehensive coverage of:

### Scraper Module (`test_scraper.py`)
- ✅ HTTP request handling with retries
- ✅ HTML parsing and data extraction
- ✅ Price parsing and validation
- ✅ Availability status parsing
- ✅ Pagination handling
- ✅ Error handling and recovery
- ✅ Complete workflow integration

### Data Processing (`test_data_processing.py`)
- ✅ Product data validation
- ✅ Price parsing and calculation
- ✅ Data sanitization
- ✅ Error handling for invalid data
- ✅ Product object creation

### Google Sheets Integration (`test_sheets_integration.py`)
- ✅ Authentication with service accounts
- ✅ Sheet creation and management
- ✅ Data formatting and upload
- ✅ Error handling for API failures
- ✅ Connection testing

### Error Handling (`test_error_handling.py`)
- ✅ Custom exception classes
- ✅ Retry mechanisms with exponential backoff
- ✅ Performance monitoring
- ✅ Metrics collection
- ✅ Logging configuration

### Main Orchestration (`test_main.py`)
- ✅ Environment setup
- ✅ Component initialization
- ✅ Workflow orchestration
- ✅ Error handling across components
- ✅ Configuration management
- ✅ Command-line argument parsing

### Integration Tests (`test_integration.py`)
- ✅ End-to-end workflow testing
- ✅ Component integration verification
- ✅ Performance benchmarking
- ✅ Memory usage testing
- ✅ Real-world scenario simulation
- ✅ Error recovery testing

## Performance Benchmarks

The test suite includes performance benchmarks with the following thresholds:

- **Scraping**: < 0.5 seconds per product
- **Processing**: < 0.1 seconds per product  
- **Sheets Upload**: < 0.2 seconds per product
- **Memory Usage**: < 100MB increase for 1000 products
- **Total Workflow**: < 30 seconds for 50 products

Run benchmarks with:
```bash
python tests/run_tests.py --performance
```

## Mocking Strategy

The test suite uses comprehensive mocking to:

### External Dependencies
- **Scrapling Fetcher**: Mocked HTTP requests and responses
- **Google Sheets API**: Mocked service and API calls
- **File System**: Mocked file operations where needed
- **Network**: Mocked network calls to avoid external dependencies

### Test Data
- **HTML Content**: Sample HTML structures for parsing tests
- **Product Data**: Realistic product data samples
- **API Responses**: Mock Google Sheets API responses
- **Error Scenarios**: Simulated error conditions

## Fixtures

Shared test fixtures in `conftest.py`:

- `mock_scrapling_response`: Mock Scrapling HTTP response
- `mock_product_element`: Mock HTML product element
- `sample_raw_product_data`: Sample raw product data
- `sample_processed_product`: Sample processed product object
- `mock_sheets_service`: Mock Google Sheets service
- `mock_google_credentials`: Mock Google credentials
- `sample_config`: Sample configuration data
- `mock_performance_monitor`: Mock performance monitor

## Test Data

Test data includes:

### Valid Test Cases
- Complete product data with all fields
- Minimal product data with required fields only
- Various price formats and currencies
- Different availability statuses
- Multiple pagination scenarios

### Invalid Test Cases  
- Missing required fields
- Invalid price formats
- Malformed URLs
- Empty or null values
- Network errors and timeouts

### Edge Cases
- Very long product names
- Special characters in data
- Large datasets (performance testing)
- Concurrent operations
- Rate limiting scenarios

## Continuous Integration

The test suite is designed to run in CI/CD environments:

### GitHub Actions Integration
```yaml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    python tests/run_tests.py --all --coverage
```

### Environment Variables
Tests use environment variables for configuration:
- `GOOGLE_SHEETS_CREDENTIALS`: Base64 encoded service account JSON
- `SPREADSHEET_ID`: Test spreadsheet ID

## Debugging Tests

### Verbose Output
```bash
pytest -v -s
```

### Debug Specific Test
```bash
pytest tests/test_scraper.py::TestGarageGrownGearScraper::test_extract_product_data_complete -v -s
```

### Print Debug Information
Add print statements or use `pytest.set_trace()` for debugging:
```python
def test_something():
    result = some_function()
    print(f"Debug: result = {result}")  # Will show with -s flag
    assert result == expected
```

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=scraper --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## Best Practices

### Writing New Tests
1. Use descriptive test names that explain what is being tested
2. Follow the Arrange-Act-Assert pattern
3. Use appropriate fixtures for setup
4. Mock external dependencies
5. Test both success and failure scenarios
6. Include edge cases and boundary conditions

### Test Organization
1. Group related tests in classes
2. Use appropriate markers (@pytest.mark.unit, etc.)
3. Keep tests independent and isolated
4. Use setup/teardown methods when needed

### Performance Considerations
1. Mock slow operations (network, file I/O)
2. Use small datasets for unit tests
3. Reserve large datasets for performance tests
4. Clean up resources after tests

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Missing Dependencies**
```bash
# Check and install missing packages
python tests/run_tests.py --check-deps
```

**Google Sheets Authentication**
```bash
# Set up test credentials
export GOOGLE_SHEETS_CREDENTIALS="base64_encoded_credentials"
```

**Slow Tests**
```bash
# Skip slow tests
pytest -m "not slow"
```

### Getting Help

1. Check test output for specific error messages
2. Run with verbose output: `pytest -v`
3. Check the test logs and assertions
4. Verify all dependencies are installed
5. Ensure environment variables are set correctly

## Contributing

When adding new functionality:

1. Write tests first (TDD approach)
2. Ensure good test coverage (aim for >90%)
3. Include both unit and integration tests
4. Add performance tests for critical paths
5. Update this documentation as needed
6. Run the full test suite before submitting changes

```bash
# Before submitting changes
python tests/run_tests.py --all --coverage
```