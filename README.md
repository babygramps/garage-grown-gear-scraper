# Garage Grown Gear Scraper

A robust, automated web scraping bot that monitors the [Garage Grown Gear sale page](https://www.garagegrowngear.com/collections/sale-1) and saves product data to Google Sheets. Features include change detection, price monitoring, and automated GitHub Actions execution.

## ✨ Features

- 🕷️ **Robust Web Scraping**: Uses Scrapling for reliable data extraction with stealth mode
- 📊 **Google Sheets Integration**: Automatically saves data with proper formatting
- 🔄 **Automated Execution**: Runs on GitHub Actions every 6 hours
- 📈 **Change Detection**: Identifies new products and significant price changes
- 🛡️ **Error Handling**: Comprehensive retry logic and graceful error recovery
- 📝 **Detailed Logging**: Structured logging with configurable levels
- ⚙️ **Flexible Configuration**: Environment-based configuration with validation
- 🧪 **Comprehensive Testing**: Full test suite with unit and integration tests

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google account with access to Google Sheets
- GitHub account (for automated execution)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/garage-grown-gear-scraper.git
cd garage-grown-gear-scraper

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration Setup

Run the automated setup script:

```bash
python setup_config.py
```

This will:
- ✅ Check Python version and dependencies
- ✅ Create `.env` file from template
- ✅ Validate your configuration
- ✅ Provide setup instructions for missing components

### 3. Google Sheets Setup

Follow the detailed guide: [Google Sheets Setup](docs/GOOGLE_SHEETS_SETUP.md)

**Quick version:**
1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create a service account and download JSON credentials
4. Create a Google Sheet and share it with your service account
5. Set `SPREADSHEET_ID` in your `.env` file

### 4. Run the Scraper

```bash
# Run once
python main.py

# Run with debug logging
LOG_LEVEL=DEBUG python main.py
```

## 📁 Project Structure

```
garage-grown-gear-scraper/
├── 📂 scraper/                 # Web scraping modules
│   └── garage_grown_gear_scraper.py
├── 📂 data_processing/         # Data validation and processing
│   ├── product_data_processor.py
│   ├── change_detector.py
│   └── validators.py
├── 📂 sheets_integration/      # Google Sheets API integration
│   └── sheets_client.py
├── 📂 error_handling/          # Error handling and logging
│   ├── exceptions.py
│   ├── logging_config.py
│   ├── monitoring.py
│   └── retry_handler.py
├── 📂 tests/                   # Comprehensive test suite
├── 📂 docs/                    # Documentation
│   ├── GOOGLE_SHEETS_SETUP.md
│   ├── CONFIGURATION.md
│   └── CHANGE_DETECTION.md
├── 📂 .github/workflows/       # GitHub Actions automation
│   └── scraper.yml
├── 📂 examples/                # Usage examples
├── config.py                   # Configuration management
├── main.py                     # Main entry point
├── setup_config.py             # Configuration setup script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Required:**
- `SPREADSHEET_ID`: Your Google Sheets spreadsheet ID
- `CREDENTIALS_FILE`: Path to Google Sheets API credentials

**Optional (with defaults):**
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `DELAY_BETWEEN_REQUESTS`: Delay between requests in seconds (default: 1.0)

See [Configuration Reference](docs/CONFIGURATION.md) for all options.

### Configuration Validation

Validate your setup:

```bash
python setup_config.py
```

## 🤖 GitHub Actions Automation

### Setup

1. Fork this repository
2. Add GitHub Secrets:
   - `GOOGLE_SHEETS_CREDENTIALS`: Base64-encoded credentials JSON
   - `SPREADSHEET_ID`: Your spreadsheet ID

### Workflow

The scraper runs automatically:
- **Schedule**: Every 6 hours
- **Manual**: Via GitHub Actions "Run workflow" button
- **Logs**: Available in GitHub Actions tab

## 📊 Data Output

The scraper creates a Google Sheet with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Timestamp | When data was collected | 2024-01-15 10:30:00 |
| Product Name | Full product name | Patagonia Better Sweater Jacket |
| Brand | Product brand | Patagonia |
| Current Price | Sale price | $89.99 |
| Original Price | Regular price | $149.99 |
| Discount % | Percentage discount | 40% |
| Availability | Stock status | Available / Sold out |
| Rating | Product rating | 4.5 |
| Reviews | Number of reviews | 123 |
| Product URL | Link to product page | https://... |

## 🔍 Change Detection

The scraper automatically detects:
- 🆕 **New products** added to sale
- 💰 **Significant price drops** (configurable threshold)
- 📦 **Stock status changes** (available → sold out)
- 🏷️ **New sale labels** and promotions

See [Change Detection Guide](docs/CHANGE_DETECTION.md) for details.

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_scraper.py

# Run integration tests (requires valid config)
python -m pytest tests/test_integration.py
```

## 📚 Documentation

- 📖 [Google Sheets Setup Guide](docs/GOOGLE_SHEETS_SETUP.md)
- ⚙️ [Configuration Reference](docs/CONFIGURATION.md)
- 🔍 [Change Detection Guide](docs/CHANGE_DETECTION.md)
- 🧪 [Testing Guide](tests/README.md)

## 🛠️ Development

### Local Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug logging
LOG_LEVEL=DEBUG python main.py

# Run tests
python -m pytest

# Validate configuration
python setup_config.py
```

### Adding New Features

1. Follow the existing code structure
2. Add comprehensive tests
3. Update documentation
4. Validate with `python setup_config.py`

## 🐛 Troubleshooting

### Common Issues

**"SPREADSHEET_ID is required but not provided"**
```bash
# Set in .env file
echo "SPREADSHEET_ID=your_spreadsheet_id" >> .env
```

**"Credentials file not found"**
```bash
# Ensure service_account.json exists
ls -la service_account.json
```

**"The caller does not have permission"**
- Share your Google Sheet with the service account email
- Grant "Editor" permissions

**Rate limiting or blocking**
- Increase `DELAY_BETWEEN_REQUESTS` in `.env`
- Enable `USE_STEALTH_MODE=true`

### Getting Help

1. Run `python setup_config.py` for configuration validation
2. Check logs for detailed error messages
3. Review the [troubleshooting guides](docs/)
4. Open an issue with error details and configuration (remove sensitive data)

## 📈 Performance

### Typical Performance

- **Pages per minute**: ~10-15 (with 1s delays)
- **Products per run**: 50-200 (depends on sale inventory)
- **Memory usage**: <100MB
- **Execution time**: 2-5 minutes per run

### Optimization Tips

- Adjust `DELAY_BETWEEN_REQUESTS` for speed vs. politeness
- Use `LOG_LEVEL=WARNING` in production for better performance
- Enable `USE_STEALTH_MODE` to avoid detection

## 🔒 Security & Ethics

### Web Scraping Ethics

- ✅ Respects robots.txt
- ✅ Uses reasonable delays between requests
- ✅ Only scrapes publicly available data
- ✅ Implements proper error handling
- ✅ Uses stealth mode to avoid server overload

### Security Best Practices

- 🔐 Never commit credentials to version control
- 🔐 Use GitHub Secrets for sensitive data
- 🔐 Regularly rotate API keys
- 🔐 Follow principle of least privilege

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- 📖 Check the [documentation](docs/)
- 🐛 Report bugs via [GitHub Issues](https://github.com/yourusername/garage-grown-gear-scraper/issues)
- 💬 Ask questions in [Discussions](https://github.com/yourusername/garage-grown-gear-scraper/discussions)

---

**Disclaimer**: This tool is for educational and personal use only. Please respect the website's terms of service and use responsibly.