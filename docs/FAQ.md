# Frequently Asked Questions (FAQ)

## General Questions

### Q: What is the Garage Grown Gear scraper?
**A:** It's an automated web scraping tool that monitors the Garage Grown Gear sale page, extracts product information (prices, availability, ratings), and saves the data to Google Sheets. It runs automatically on GitHub Actions every 6 hours.

### Q: Is this legal?
**A:** Yes, the scraper only collects publicly available information and follows web scraping best practices:
- Respects robots.txt
- Uses reasonable delays between requests
- Doesn't overload the server
- Only scrapes public product data

### Q: How much does it cost to run?
**A:** The scraper is free to run:
- GitHub Actions provides 2,000 free minutes per month
- Google Sheets API has generous free quotas
- The scraper uses minimal resources (runs for 2-5 minutes every 6 hours)

## Setup and Configuration

### Q: Do I need programming experience?
**A:** Basic familiarity with command line and following instructions is helpful, but the setup script automates most of the process. The detailed guides walk you through each step.

### Q: What Python version do I need?
**A:** Python 3.8 or higher is required. Check your version with:
```bash
python --version
```

### Q: Can I run this on Windows/Mac/Linux?
**A:** Yes, the scraper works on all major operating systems. The setup instructions are the same across platforms.

### Q: How do I get Google Sheets credentials?
**A:** Follow the [Google Sheets Setup Guide](GOOGLE_SHEETS_SETUP.md). The process involves:
1. Creating a Google Cloud project
2. Enabling the Google Sheets API
3. Creating a service account
4. Downloading the JSON credentials file

### Q: Where do I put the credentials file?
**A:** Save the JSON file as `service_account.json` in the project root directory (same folder as `main.py`).

## Usage and Features

### Q: How often does the scraper run?
**A:** By default, it runs every 6 hours when deployed on GitHub Actions. You can also run it manually anytime.

### Q: What data does it collect?
**A:** For each product on sale, it collects:
- Product name and brand
- Current price and original price
- Discount percentage
- Availability status (in stock/sold out)
- Customer rating and review count
- Product URL and image

### Q: Can I change what data is collected?
**A:** Yes, but it requires modifying the code. The CSS selectors in `config.py` define what data is extracted.

### Q: How is the data organized in Google Sheets?
**A:** Each row represents a product at a specific time, with columns for all the collected data. New data is appended, so you can track changes over time.

### Q: Can I use multiple Google Sheets?
**A:** Currently, the scraper writes to one spreadsheet. You can modify the configuration to use different sheets for different purposes.

## Troubleshooting

### Q: The scraper says "No products found" - what's wrong?
**A:** This usually means:
- The sale page has no products currently
- The website structure changed (CSS selectors need updating)
- Network connectivity issues
- The website is blocking requests

Run with debug logging to see more details:
```bash
LOG_LEVEL=DEBUG python main.py
```

### Q: I'm getting "Permission denied" errors with Google Sheets
**A:** Make sure you:
1. Shared your Google Sheet with the service account email
2. Gave the service account "Editor" permissions
3. Used the correct spreadsheet ID

### Q: The scraper is running too slowly
**A:** You can adjust the timing settings in your `.env` file:
```env
DELAY_BETWEEN_REQUESTS=0.5  # Reduce from 1.0 (be respectful)
REQUEST_TIMEOUT=15          # Reduce from 30
```

### Q: GitHub Actions is failing
**A:** Common causes:
- Missing or incorrect GitHub Secrets
- Invalid base64 encoding of credentials
- Quota limits exceeded

Check the Actions logs for specific error messages.

## Customization

### Q: Can I scrape other websites?
**A:** The scraper is specifically designed for Garage Grown Gear. Adapting it for other sites would require:
- Updating the CSS selectors
- Modifying the data extraction logic
- Adjusting for different page structures

### Q: Can I change the scraping schedule?
**A:** Yes, edit the cron expression in `.github/workflows/scraper.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  - cron: '0 */2 * * *'  # Every 2 hours
  - cron: '0 9 * * *'    # Daily at 9 AM
```

### Q: Can I add notifications?
**A:** Yes, the scraper supports webhook notifications. Set these in your `.env`:
```env
ENABLE_NOTIFICATIONS=true
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PRICE_DROP_THRESHOLD=20.0
```

### Q: Can I filter products by brand or price?
**A:** Currently, the scraper collects all products. You can add filtering logic in the data processing module or filter the data in Google Sheets afterward.

## Performance and Limits

### Q: How many products can it handle?
**A:** The scraper can handle hundreds of products efficiently. It processes them in batches and uses memory-efficient techniques.

### Q: Will I hit API rate limits?
**A:** Unlikely with normal usage. The scraper:
- Uses reasonable delays between requests
- Implements retry logic with backoff
- Respects Google Sheets API quotas

### Q: How much data will be stored?
**A:** Each run typically adds 50-200 rows (depending on sale inventory). Over a year, this might be 50,000-100,000 rows, which is well within Google Sheets limits.

### Q: Can I run multiple instances?
**A:** Yes, but be careful about:
- Rate limiting (use different delays)
- Google Sheets write conflicts
- Respectful scraping practices

## Data and Privacy

### Q: Is the collected data private?
**A:** The data is stored in your Google Sheet, which you control. Make sure to:
- Keep your credentials secure
- Don't share the spreadsheet publicly unless intended
- Follow your organization's data policies

### Q: Can I export the data?
**A:** Yes, Google Sheets allows exporting to various formats (CSV, Excel, PDF). You can also access the data programmatically via the Google Sheets API.

### Q: How long is data retained?
**A:** Data is kept indefinitely in your Google Sheet unless you delete it. You can implement data retention policies by periodically cleaning old data.

## Advanced Usage

### Q: Can I run this on a server instead of GitHub Actions?
**A:** Yes, you can deploy it anywhere Python runs:
- VPS or cloud server
- Raspberry Pi
- Local computer with cron/task scheduler

### Q: Can I integrate this with other tools?
**A:** Yes, the data in Google Sheets can be:
- Connected to data visualization tools (Tableau, Power BI)
- Imported into databases
- Used with Google Apps Script for automation
- Accessed via API for custom applications

### Q: How do I contribute improvements?
**A:** Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Q: Can I use this for commercial purposes?
**A:** Check the license (MIT) and ensure you comply with:
- The website's terms of service
- Your local laws regarding web scraping
- Ethical scraping practices

## Getting Help

### Q: Where can I get support?
**A:** 
1. Check the [documentation](../README.md)
2. Review the [troubleshooting guide](TROUBLESHOOTING.md)
3. Search [GitHub Issues](https://github.com/yourusername/garage-grown-gear-scraper/issues)
4. Create a new issue with details
5. Ask in [GitHub Discussions](https://github.com/yourusername/garage-grown-gear-scraper/discussions)

### Q: How do I report bugs?
**A:** Create a GitHub issue with:
- Detailed description of the problem
- Steps to reproduce
- Error messages and logs
- Your configuration (remove sensitive data)
- System information (OS, Python version)

### Q: Can I request new features?
**A:** Yes! Create a GitHub issue with the "enhancement" label and describe:
- What you'd like to achieve
- Why it would be useful
- How you envision it working

## Best Practices

### Q: How often should I run the scraper?
**A:** The default 6-hour interval is a good balance between:
- Getting timely updates
- Being respectful to the website
- Staying within API limits
- Conserving GitHub Actions minutes

### Q: Should I monitor the scraper?
**A:** Yes, consider:
- Checking GitHub Actions logs periodically
- Setting up notifications for failures
- Monitoring data quality in your spreadsheet
- Watching for website structure changes

### Q: How do I keep the scraper updated?
**A:** 
1. Watch the GitHub repository for updates
2. Review release notes for breaking changes
3. Test updates in a separate environment first
4. Keep your dependencies updated with `pip install -r requirements.txt --upgrade`

Remember: If you can't find an answer here, check the other documentation files or ask for help in the GitHub repository!