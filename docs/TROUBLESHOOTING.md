# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Garage Grown Gear scraper.

## 🔧 Quick Diagnostics

Run the configuration validation script first:

```bash
python setup_config.py
```

This will check:
- ✅ Python version compatibility
- ✅ Required dependencies
- ✅ Configuration files
- ✅ Google Sheets credentials
- ✅ Environment variables

## 🚨 Common Issues

### Configuration Issues

#### "SPREADSHEET_ID is required but not provided"

**Cause**: Missing or empty `SPREADSHEET_ID` environment variable.

**Solution**:
1. Get your spreadsheet ID from the Google Sheets URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
   ```
2. Add it to your `.env` file:
   ```env
   SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
   ```

#### "Credentials file not found: service_account.json"

**Cause**: Google Sheets API credentials file is missing.

**Solution**:
1. Follow the [Google Sheets Setup Guide](GOOGLE_SHEETS_SETUP.md)
2. Download the JSON credentials file
3. Save it as `service_account.json` in the project root
4. Verify the file exists:
   ```bash
   ls -la service_account.json
   ```

#### "Configuration validation failed"

**Cause**: Invalid configuration values.

**Solution**:
1. Run `python setup_config.py` to see specific errors
2. Check the [Configuration Reference](CONFIGURATION.md) for valid values
3. Common fixes:
   ```env
   # Fix invalid log level
   LOG_LEVEL=INFO  # not "info" or "Info"
   
   # Fix invalid URL
   BASE_URL=https://www.garagegrowngear.com/collections/sale-1  # include https://
   
   # Fix invalid timeout
   REQUEST_TIMEOUT=30  # positive number
   ```

### Google Sheets Issues

#### "The caller does not have permission"

**Cause**: Service account doesn't have access to the spreadsheet.

**Solution**:
1. Open your Google Sheet
2. Click "Share" in the top right
3. Add your service account email (found in `service_account.json`)
4. Give it "Editor" permissions
5. Click "Send"

**Find service account email**:
```bash
# On Linux/Mac:
grep -o '"client_email": "[^"]*"' service_account.json

# On Windows:
findstr "client_email" service_account.json
```

#### "Spreadsheet not found"

**Cause**: Invalid spreadsheet ID or deleted spreadsheet.

**Solution**:
1. Verify the spreadsheet ID is correct (44 characters)
2. Check that the spreadsheet exists and is accessible
3. Ensure you're using the correct Google account

#### "Quota exceeded" or "Rate limit exceeded"

**Cause**: Too many API requests to Google Sheets.

**Solution**:
1. Increase delays in your configuration:
   ```env
   DELAY_BETWEEN_REQUESTS=2.0
   MAX_RETRIES=2
   ```
2. Wait a few minutes before retrying
3. Consider running less frequently

### Web Scraping Issues

#### "Connection timeout" or "Request failed"

**Cause**: Network issues or website blocking.

**Solution**:
1. Check your internet connection
2. Verify the website is accessible in your browser
3. Increase timeout values:
   ```env
   REQUEST_TIMEOUT=60
   RETRY_DELAY=2.0
   ```
4. Enable stealth mode:
   ```env
   USE_STEALTH_MODE=true
   ```

#### "No products found" or "Empty results"

**Cause**: Website structure changed or no products on sale.

**Solution**:
1. Check if there are actually products on the sale page
2. Verify the website URL is correct
3. Check if the website structure changed (CSS selectors may need updating)
4. Run with debug logging:
   ```bash
   LOG_LEVEL=DEBUG python main.py
   ```

#### "Rate limited" or "429 Too Many Requests"

**Cause**: Making requests too quickly.

**Solution**:
1. Increase delay between requests:
   ```env
   DELAY_BETWEEN_REQUESTS=3.0
   ```
2. Reduce retry attempts:
   ```env
   MAX_RETRIES=2
   ```
3. Wait before retrying

### GitHub Actions Issues

#### "Workflow failed" or "Action failed"

**Cause**: Various issues in the automated environment.

**Solution**:
1. Check the GitHub Actions logs for specific errors
2. Verify GitHub Secrets are set correctly:
   - `GOOGLE_SHEETS_CREDENTIALS`
   - `SPREADSHEET_ID`
3. Ensure secrets are base64 encoded properly:
   ```bash
   # Encode credentials
   base64 -i service_account.json
   ```

#### "Secret not found"

**Cause**: GitHub Secrets not configured.

**Solution**:
1. Go to your repository Settings
2. Navigate to Secrets and variables > Actions
3. Add required secrets:
   - `GOOGLE_SHEETS_CREDENTIALS`: Base64-encoded JSON credentials
   - `SPREADSHEET_ID`: Your spreadsheet ID

#### "Python dependencies failed to install"

**Cause**: Issues with package installation in GitHub Actions.

**Solution**:
1. Check if `requirements.txt` is up to date
2. Verify Python version compatibility in workflow file
3. Check for any package conflicts

### Performance Issues

#### "Scraper is too slow"

**Cause**: Conservative delay settings.

**Solution** (use with caution):
```env
# Faster settings (be respectful)
DELAY_BETWEEN_REQUESTS=0.5
REQUEST_TIMEOUT=15
MAX_RETRIES=2
```

#### "High memory usage"

**Cause**: Processing large amounts of data.

**Solution**:
1. Check for memory leaks in logs
2. Restart the scraper periodically
3. Monitor system resources

#### "Frequent timeouts"

**Cause**: Network or server issues.

**Solution**:
```env
# More robust settings
REQUEST_TIMEOUT=60
MAX_RETRIES=5
RETRY_DELAY=3.0
```

## 🔍 Debugging Steps

### 1. Enable Debug Logging

```bash
LOG_LEVEL=DEBUG python main.py
```

This provides detailed information about:
- Configuration loading
- HTTP requests and responses
- Data extraction process
- Google Sheets operations

### 2. Test Individual Components

**Test configuration**:
```python
from config import AppConfig
config = AppConfig.from_env()
print(config)
```

**Test Google Sheets connection**:
```python
from sheets_integration.sheets_client import SheetsClient
client = SheetsClient("service_account.json", "your_spreadsheet_id")
client.authenticate()
```

**Test web scraping**:
```python
from scraper.garage_grown_gear_scraper import GarageGrownGearScraper
scraper = GarageGrownGearScraper()
products = scraper.scrape_page("https://www.garagegrowngear.com/collections/sale-1")
print(f"Found {len(products)} products")
```

### 3. Check System Requirements

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check disk space
df -h

# Check memory usage
free -h  # Linux
# or
Get-Process python | Select-Object WorkingSet  # Windows PowerShell
```

### 4. Validate Network Connectivity

```bash
# Test website accessibility
curl -I https://www.garagegrowngear.com/collections/sale-1

# Test Google Sheets API
curl -I https://sheets.googleapis.com/
```

## 📊 Log Analysis

### Understanding Log Messages

**INFO level logs**:
- Normal operation messages
- Progress indicators
- Summary statistics

**WARNING level logs**:
- Recoverable issues
- Missing optional data
- Performance concerns

**ERROR level logs**:
- Failed operations
- Invalid data
- Configuration issues

**DEBUG level logs**:
- Detailed execution flow
- HTTP request/response details
- Data processing steps

### Common Log Patterns

**Successful run**:
```
INFO - Starting scraper...
INFO - Found 45 products on page 1
INFO - Found 32 products on page 2
INFO - Processed 77 total products
INFO - Saved data to Google Sheets
INFO - Scraping completed successfully
```

**Configuration error**:
```
ERROR - Configuration error: SPREADSHEET_ID is required but not provided
```

**Network error**:
```
WARNING - Request failed, retrying in 1.0 seconds (attempt 1/3)
WARNING - Request failed, retrying in 2.0 seconds (attempt 2/3)
ERROR - Max retries exceeded for URL: https://...
```

**Google Sheets error**:
```
ERROR - Google Sheets API error: The caller does not have permission
```

## 🆘 Getting Help

### Before Asking for Help

1. ✅ Run `python setup_config.py`
2. ✅ Check this troubleshooting guide
3. ✅ Review error logs with `LOG_LEVEL=DEBUG`
4. ✅ Test individual components
5. ✅ Search existing GitHub issues

### When Reporting Issues

Include this information:

**System Information**:
```bash
python --version
pip list | grep -E "(scrapling|google|requests)"
```

**Configuration** (remove sensitive data):
```bash
# Show environment variables (remove actual values)
env | grep -E "(SPREADSHEET|LOG|BASE)" | sed 's/=.*/=***/'
```

**Error Logs**:
- Full error message
- Stack trace if available
- Steps to reproduce

**What You've Tried**:
- Configuration changes
- Troubleshooting steps followed
- Workarounds attempted

### Support Channels

1. 📖 Check [documentation](../README.md)
2. 🔍 Search [GitHub Issues](https://github.com/yourusername/garage-grown-gear-scraper/issues)
3. 🆕 Create new issue with template
4. 💬 Ask in [Discussions](https://github.com/yourusername/garage-grown-gear-scraper/discussions)

## 🔧 Advanced Troubleshooting

### Network Debugging

**Check proxy settings**:
```bash
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

**Test with curl**:
```bash
curl -v https://www.garagegrowngear.com/collections/sale-1
```

**Monitor network traffic**:
```bash
# Linux
sudo netstat -tuln | grep python

# Windows
netstat -an | findstr python
```

### Google Sheets API Debugging

**Test API access**:
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file('service_account.json')
service = build('sheets', 'v4', credentials=credentials)
result = service.spreadsheets().get(spreadsheetId='your_id').execute()
print(result.get('properties', {}).get('title'))
```

**Check API quotas**:
1. Go to Google Cloud Console
2. Navigate to APIs & Services > Quotas
3. Check Google Sheets API usage

### Performance Profiling

**Memory profiling**:
```python
import tracemalloc
tracemalloc.start()

# Run your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

**Time profiling**:
```python
import time
import cProfile

# Profile the main function
cProfile.run('main()', 'profile_stats')

# Analyze results
import pstats
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

Remember: Most issues are configuration-related. Start with `python setup_config.py` and work through the validation errors systematically.