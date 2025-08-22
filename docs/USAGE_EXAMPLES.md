# Usage Examples

This document provides practical examples of how to use the Garage Grown Gear scraper in different scenarios.

## 🚀 Basic Usage Examples

### Example 1: First Time Setup

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/garage-grown-gear-scraper.git
cd garage-grown-gear-scraper
pip install -r requirements.txt

# 2. Run setup wizard
python setup_config.py

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run once to test
python main.py
```

### Example 2: Manual Run with Custom Settings

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python main.py

# Run with custom delays (be respectful)
DELAY_BETWEEN_REQUESTS=2.0 python main.py

# Run with different sheet name
SHEET_NAME=Weekly_Sales python main.py
```

### Example 3: Configuration Validation

```bash
# Check if everything is set up correctly
python setup_config.py

# Test specific components
python -c "from config import AppConfig; print(AppConfig.from_env())"
python -c "from sheets_integration.sheets_client import SheetsClient; SheetsClient('service_account.json', 'your_id').authenticate()"
```

## ⚙️ Configuration Examples

### Example 1: Development Configuration

```env
# .env for development
SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
SHEET_NAME=Dev_Testing
LOG_LEVEL=DEBUG
LOG_TO_FILE=true
DELAY_BETWEEN_REQUESTS=2.0
ENABLE_NOTIFICATIONS=false
```

### Example 2: Production Configuration

```env
# .env for production
SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
SHEET_NAME=Production_Data
LOG_LEVEL=INFO
LOG_TO_FILE=false
DELAY_BETWEEN_REQUESTS=1.0
ENABLE_NOTIFICATIONS=true
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PRICE_DROP_THRESHOLD=15.0
```

### Example 3: Performance Optimized Configuration

```env
# Faster scraping (use with caution)
DELAY_BETWEEN_REQUESTS=0.5
REQUEST_TIMEOUT=15
MAX_RETRIES=2
USE_STEALTH_MODE=true
```

### Example 4: Conservative Configuration

```env
# Slower but more reliable
DELAY_BETWEEN_REQUESTS=3.0
REQUEST_TIMEOUT=60
MAX_RETRIES=5
RETRY_DELAY=2.0
```

## 🤖 GitHub Actions Examples

### Example 1: Basic Workflow

```yaml
# .github/workflows/scraper.yml
name: Garage Grown Gear Scraper
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run scraper
        env:
          GOOGLE_SHEETS_CREDENTIALS: ${{ secrets.GOOGLE_SHEETS_CREDENTIALS }}
          SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
        run: python main.py
```

### Example 2: Multiple Schedule Workflow

```yaml
# Run at different intervals
on:
  schedule:
    - cron: '0 9 * * *'    # Daily at 9 AM
    - cron: '0 15 * * *'   # Daily at 3 PM
    - cron: '0 21 * * *'   # Daily at 9 PM
  workflow_dispatch:
```

### Example 3: Conditional Workflow

```yaml
# Only run on weekdays
on:
  schedule:
    - cron: '0 */4 * * 1-5'  # Every 4 hours, Monday-Friday
```

### Example 4: Workflow with Notifications

```yaml
jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run scraper
        env:
          GOOGLE_SHEETS_CREDENTIALS: ${{ secrets.GOOGLE_SHEETS_CREDENTIALS }}
          SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
          ENABLE_NOTIFICATIONS: true
          WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
        run: python main.py
      - name: Notify on failure
        if: failure()
        run: |
          curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"Scraper failed! Check the logs."}' \
            ${{ secrets.WEBHOOK_URL }}
```

## 📊 Data Analysis Examples

### Example 1: Google Sheets Formulas

Add these formulas to your spreadsheet for automatic analysis:

```excel
# Count products by brand (in a summary sheet)
=COUNTIF(Product_Data!C:C,"Patagonia")

# Average discount percentage
=AVERAGE(Product_Data!F:F)

# Find products with >30% discount
=FILTER(Product_Data!A:J, Product_Data!F:F>30)

# Latest price for a specific product
=INDEX(Product_Data!D:D, MATCH(MAX(IF(Product_Data!B:B="Product Name", Product_Data!A:A)), Product_Data!A:A, 0))
```

### Example 2: Google Apps Script Integration

```javascript
// Google Apps Script to send email alerts
function checkForDeals() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  // Find products with >40% discount added in last 24 hours
  const yesterday = new Date(Date.now() - 24*60*60*1000);
  const deals = data.filter(row => {
    const timestamp = new Date(row[0]);
    const discount = parseFloat(row[5]);
    return timestamp > yesterday && discount > 40;
  });
  
  if (deals.length > 0) {
    const message = `Found ${deals.length} great deals:\n` + 
      deals.map(deal => `${deal[1]} - ${deal[5]}% off`).join('\n');
    
    MailApp.sendEmail({
      to: 'your-email@example.com',
      subject: 'Great Deals Alert!',
      body: message
    });
  }
}
```

### Example 3: Python Data Analysis

```python
# analyze_data.py - Analyze scraped data
import pandas as pd
from google.oauth2 import service_account
import gspread

# Connect to Google Sheets
gc = gspread.service_account(filename='service_account.json')
sheet = gc.open_by_key('your_spreadsheet_id').sheet1

# Load data into pandas
data = pd.DataFrame(sheet.get_all_records())
data['Timestamp'] = pd.to_datetime(data['Timestamp'])
data['Current Price'] = data['Current Price'].str.replace('$', '').astype(float)
data['Discount %'] = data['Discount %'].str.replace('%', '').astype(float)

# Analysis examples
print("Top 10 brands by number of products:")
print(data['Brand'].value_counts().head(10))

print("\nAverage discount by brand:")
print(data.groupby('Brand')['Discount %'].mean().sort_values(ascending=False))

print("\nProducts with biggest price drops:")
price_changes = data.groupby('Product Name')['Current Price'].agg(['min', 'max'])
price_changes['Drop %'] = (1 - price_changes['min'] / price_changes['max']) * 100
print(price_changes.sort_values('Drop %', ascending=False).head())
```

## 🔔 Notification Examples

### Example 1: Slack Webhook

```python
# Custom notification script
import requests
import json

def send_slack_notification(deals):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    message = {
        "text": f"🛍️ Found {len(deals)} great deals!",
        "attachments": [
            {
                "color": "good",
                "fields": [
                    {
                        "title": deal['name'],
                        "value": f"{deal['discount']}% off - ${deal['price']}",
                        "short": True
                    }
                    for deal in deals[:5]  # Limit to 5 deals
                ]
            }
        ]
    }
    
    requests.post(webhook_url, json=message)
```

### Example 2: Discord Webhook

```python
def send_discord_notification(deals):
    webhook_url = "https://discord.com/api/webhooks/YOUR/WEBHOOK/URL"
    
    embed = {
        "title": "🛍️ Great Deals Found!",
        "color": 0x00ff00,
        "fields": [
            {
                "name": deal['name'],
                "value": f"{deal['discount']}% off - ${deal['price']}\n[View Product]({deal['url']})",
                "inline": True
            }
            for deal in deals[:6]  # Discord limit
        ]
    }
    
    requests.post(webhook_url, json={"embeds": [embed]})
```

### Example 3: Email Notifications

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(deals):
    sender_email = "your-email@gmail.com"
    sender_password = "your-app-password"
    receiver_email = "recipient@example.com"
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"🛍️ {len(deals)} Great Deals Found!"
    
    body = "Great deals found:\n\n"
    for deal in deals:
        body += f"• {deal['name']} - {deal['discount']}% off (${deal['price']})\n"
        body += f"  {deal['url']}\n\n"
    
    message.attach(MIMEText(body, "plain"))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
```

## 🧪 Testing Examples

### Example 1: Test Configuration

```python
# test_config.py
from config import AppConfig, ConfigurationError
import pytest
import os

def test_valid_config():
    os.environ['SPREADSHEET_ID'] = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    config = AppConfig.from_env()
    assert config.sheets.spreadsheet_id == '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

def test_invalid_spreadsheet_id():
    os.environ['SPREADSHEET_ID'] = 'invalid'
    with pytest.raises(ConfigurationError):
        AppConfig.from_env()
```

### Example 2: Test Scraper

```python
# test_scraper_manual.py
from scraper.garage_grown_gear_scraper import GarageGrownGearScraper

def test_scraper_manually():
    scraper = GarageGrownGearScraper()
    products = scraper.scrape_page("https://www.garagegrowngear.com/collections/sale-1")
    
    print(f"Found {len(products)} products")
    if products:
        print("First product:", products[0])
        
    assert len(products) >= 0  # Should not fail even if no products
```

### Example 3: Test Google Sheets

```python
# test_sheets_manual.py
from sheets_integration.sheets_client import SheetsClient
import os

def test_sheets_connection():
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    client = SheetsClient('service_account.json', spreadsheet_id)
    
    # Test authentication
    client.authenticate()
    print("✅ Authentication successful")
    
    # Test writing data
    test_data = [['Test', 'Data', '2024-01-01']]
    client.append_data('Test_Sheet', test_data)
    print("✅ Data write successful")
```

## 🔧 Customization Examples

### Example 1: Custom Data Processing

```python
# custom_processor.py
from data_processing.product_data_processor import ProductDataProcessor

class CustomProcessor(ProductDataProcessor):
    def process_products(self, raw_products):
        # Add custom processing logic
        processed = super().process_products(raw_products)
        
        # Add custom fields
        for product in processed:
            product['deal_score'] = self.calculate_deal_score(product)
            product['category'] = self.categorize_product(product['name'])
        
        return processed
    
    def calculate_deal_score(self, product):
        # Custom scoring algorithm
        discount = product.get('discount_percentage', 0)
        rating = product.get('rating', 0)
        return (discount * 0.7) + (rating * 0.3)
    
    def categorize_product(self, name):
        # Simple categorization
        name_lower = name.lower()
        if any(word in name_lower for word in ['jacket', 'coat']):
            return 'Outerwear'
        elif any(word in name_lower for word in ['shirt', 'tee']):
            return 'Tops'
        else:
            return 'Other'
```

### Example 2: Custom Notifications

```python
# custom_notifications.py
from error_handling.monitoring import NotificationHandler

class CustomNotificationHandler(NotificationHandler):
    def __init__(self, config):
        super().__init__(config)
        self.deal_threshold = 30  # Custom threshold
    
    def process_deals(self, products):
        great_deals = [
            p for p in products 
            if p.get('discount_percentage', 0) >= self.deal_threshold
        ]
        
        if great_deals:
            self.send_deal_alert(great_deals)
    
    def send_deal_alert(self, deals):
        # Custom alert logic
        message = f"🔥 {len(deals)} hot deals found!"
        for deal in deals[:3]:  # Top 3 deals
            message += f"\n• {deal['name']} - {deal['discount_percentage']}% off"
        
        self.send_notification(message)
```

### Example 3: Custom Scheduling

```python
# custom_scheduler.py
import schedule
import time
from main import main

def run_scraper():
    print("Running scheduled scrape...")
    main()
    print("Scrape completed")

# Custom scheduling
schedule.every().day.at("09:00").do(run_scraper)  # 9 AM daily
schedule.every().day.at("15:00").do(run_scraper)  # 3 PM daily
schedule.every().day.at("21:00").do(run_scraper)  # 9 PM daily

# Weekend-only schedule
schedule.every().saturday.at("10:00").do(run_scraper)
schedule.every().sunday.at("10:00").do(run_scraper)

if __name__ == "__main__":
    print("Starting custom scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
```

## 🚀 Deployment Examples

### Example 1: Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run scraper
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  scraper:
    build: .
    environment:
      - SPREADSHEET_ID=${SPREADSHEET_ID}
      - LOG_LEVEL=INFO
    volumes:
      - ./service_account.json:/app/service_account.json:ro
      - ./logs:/app/logs
    restart: unless-stopped
```

### Example 2: Cron Job Deployment

```bash
# Add to crontab (crontab -e)
# Run every 6 hours
0 */6 * * * cd /path/to/scraper && /usr/bin/python3 main.py >> /var/log/scraper.log 2>&1

# Run daily at 9 AM
0 9 * * * cd /path/to/scraper && /usr/bin/python3 main.py

# Run weekdays only at 2 PM
0 14 * * 1-5 cd /path/to/scraper && /usr/bin/python3 main.py
```

### Example 3: Systemd Service

```ini
# /etc/systemd/system/garage-scraper.service
[Unit]
Description=Garage Grown Gear Scraper
After=network.target

[Service]
Type=oneshot
User=scraper
WorkingDirectory=/home/scraper/garage-grown-gear-scraper
ExecStart=/usr/bin/python3 main.py
Environment=PYTHONPATH=/home/scraper/garage-grown-gear-scraper

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/garage-scraper.timer
[Unit]
Description=Run Garage Scraper every 6 hours
Requires=garage-scraper.service

[Timer]
OnCalendar=*-*-* 00,06,12,18:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Enable and start
sudo systemctl enable garage-scraper.timer
sudo systemctl start garage-scraper.timer
sudo systemctl status garage-scraper.timer
```

These examples should help you get started with various use cases and customizations of the Garage Grown Gear scraper!