# Configuration Reference

This document provides a comprehensive reference for all configuration options available in the Garage Grown Gear scraper.

## Configuration Files

### Environment Variables (.env)

The primary configuration is done through environment variables. Copy `.env.example` to `.env` and customize the values:

```bash
cp .env.example .env
```

### Configuration Sections

## Scraper Configuration

Controls web scraping behavior and performance.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `BASE_URL` | string | `https://www.garagegrowngear.com/collections/sale-1` | Target URL to scrape |
| `MAX_RETRIES` | integer | `3` | Maximum number of retry attempts for failed requests |
| `RETRY_DELAY` | float | `1.0` | Initial delay between retries (seconds) |
| `REQUEST_TIMEOUT` | integer | `30` | HTTP request timeout (seconds) |
| `USE_STEALTH_MODE` | boolean | `true` | Enable stealth headers and browser simulation |
| `DELAY_BETWEEN_REQUESTS` | float | `1.0` | Delay between consecutive requests (seconds) |

### Validation Rules

- `BASE_URL`: Must start with `http://` or `https://`
- `MAX_RETRIES`: Must be between 0 and 10
- `RETRY_DELAY`: Must be between 0 and 60 seconds
- `REQUEST_TIMEOUT`: Must be between 1 and 300 seconds
- `DELAY_BETWEEN_REQUESTS`: Must be between 0 and 10 seconds

## Google Sheets Configuration

Controls integration with Google Sheets for data storage.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SPREADSHEET_ID` | string | *required* | Google Sheets spreadsheet ID (44 characters) |
| `SHEET_NAME` | string | `Product_Data` | Name of the sheet tab to write data to |
| `CREDENTIALS_FILE` | string | `service_account.json` | Path to Google Sheets API credentials file |

### Validation Rules

- `SPREADSHEET_ID`: Required, must be exactly 44 characters
- `SHEET_NAME`: Cannot be empty
- `CREDENTIALS_FILE`: Must point to a valid JSON credentials file

### Getting Your Spreadsheet ID

The spreadsheet ID is found in the Google Sheets URL:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
```

## Logging Configuration

Controls logging behavior and output formatting.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_TO_FILE` | boolean | `false` | Whether to write logs to a file |
| `LOG_FILE_PATH` | string | `scraper.log` | Path for log file (when LOG_TO_FILE is true) |

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program execution
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for handled exceptions
- `CRITICAL`: Critical errors that may cause program termination

## Notification Configuration

Controls alerts and notifications for significant changes.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_NOTIFICATIONS` | boolean | `false` | Enable notification system |
| `WEBHOOK_URL` | string | *optional* | Webhook URL for notifications |
| `EMAIL_NOTIFICATIONS` | boolean | `false` | Enable email notifications (future feature) |
| `PRICE_DROP_THRESHOLD` | float | `20.0` | Percentage threshold for significant price drops |

### Validation Rules

- `WEBHOOK_URL`: Must start with `http://` or `https://` if provided
- `PRICE_DROP_THRESHOLD`: Must be between 0 and 100

## Advanced Configuration

### CSS Selectors

The scraper uses CSS selectors to extract data from web pages. These are defined in `config.py`:

```python
SELECTORS = {
    'product_items': '.product-item',
    'product_name': '.product-item__title a',
    'brand': '.product-item__vendor',
    'current_price': '.price--highlight [data-money-convertible]',
    'original_price': '.price--compare [data-money-convertible]',
    'sale_label': '.product-label--on-sale',
    'availability': '.product-item__inventory',
    'rating': '.stamped-badge[data-rating]',
    'reviews_count': '.stamped-badge-caption[data-reviews]',
    'product_link': '.product-item__title a',
    'image': '.product-item__primary-image img',
    'pagination_next': '.pagination__next',
    'pagination_items': '.pagination__item'
}
```

**Note**: Only modify these if the website structure changes.

## Configuration Validation

### Automatic Validation

All configuration is automatically validated when the application starts. Invalid configurations will cause the program to exit with detailed error messages.

### Manual Validation

Run the configuration setup script to validate your configuration:

```bash
python setup_config.py
```

This will check:
- Python version compatibility
- Required dependencies
- Configuration file existence
- Google Sheets credentials
- Environment variable values
- Configuration validation rules

## Environment-Specific Configuration

### Development

For local development, use a `.env` file:

```env
# Development settings
LOG_LEVEL=DEBUG
LOG_TO_FILE=true
DELAY_BETWEEN_REQUESTS=2.0
ENABLE_NOTIFICATIONS=false
```

### Production (GitHub Actions)

For production deployment, set environment variables in GitHub Secrets:

- `GOOGLE_SHEETS_CREDENTIALS`: Base64-encoded credentials JSON
- `SPREADSHEET_ID`: Your production spreadsheet ID

Other variables can use defaults or be set in the workflow file.

## Configuration Examples

### Minimal Configuration

```env
# Required only
SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

### Performance Optimized

```env
# Faster scraping (use with caution)
DELAY_BETWEEN_REQUESTS=0.5
REQUEST_TIMEOUT=15
MAX_RETRIES=2
```

### Debug Configuration

```env
# Detailed logging
LOG_LEVEL=DEBUG
LOG_TO_FILE=true
LOG_FILE_PATH=debug.log
```

### Notification Enabled

```env
# With notifications
ENABLE_NOTIFICATIONS=true
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PRICE_DROP_THRESHOLD=15.0
```

## Troubleshooting Configuration

### Common Configuration Errors

**"SPREADSHEET_ID is required but not provided"**
- Set the `SPREADSHEET_ID` environment variable
- Ensure your `.env` file is in the project root

**"Credentials file not found"**
- Verify `service_account.json` exists
- Check the `CREDENTIALS_FILE` path

**"Invalid log level"**
- Use one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Check for typos in the `LOG_LEVEL` variable

**"Base URL must start with http:// or https://"**
- Ensure `BASE_URL` includes the protocol
- Check for extra spaces or characters

### Configuration Debugging

1. Run `python setup_config.py` for comprehensive validation
2. Check the console output for specific error messages
3. Verify environment variables are loaded:
   ```python
   import os
   print(os.getenv('SPREADSHEET_ID'))
   ```
4. Test configuration loading:
   ```python
   from config import AppConfig
   config = AppConfig.from_env()
   print(config)
   ```

## Security Considerations

### Sensitive Information

Never commit these files to version control:
- `.env` (contains configuration)
- `service_account.json` (contains credentials)
- `*.log` (may contain sensitive data)

Add them to `.gitignore`:
```gitignore
.env
service_account.json
*.log
```

### GitHub Secrets

For GitHub Actions, use secrets instead of environment variables:
- Store credentials as `GOOGLE_SHEETS_CREDENTIALS` secret
- Store spreadsheet ID as `SPREADSHEET_ID` secret
- Never log sensitive configuration values

### Credential Rotation

Regularly rotate your Google Sheets service account keys:
1. Create new credentials in Google Cloud Console
2. Update the `service_account.json` file
3. Update GitHub Secrets if using Actions
4. Delete old credentials from Google Cloud Console