# Change Detection and Notifications

The Garage Grown Gear scraper includes a comprehensive change detection system that monitors product changes and sends notifications for significant events.

## Features

### Change Detection
- **New Products**: Automatically detects when new products are added to the sale page
- **Price Changes**: Monitors price drops and increases with configurable thresholds
- **Availability Changes**: Tracks when products go in/out of stock
- **Priority Flagging**: Identifies high-priority deals based on significance

### Notification System
- **Webhook Support**: Send notifications to Slack, Discord, or other webhook-compatible services
- **Smart Filtering**: Only sends notifications for significant changes
- **Detailed Summaries**: Provides comprehensive change summaries with statistics

## Configuration

### Environment Variables
```bash
# Enable notifications
ENABLE_NOTIFICATIONS=true

# Webhook URL for notifications (optional)
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Price drop threshold for significant alerts (default: 20%)
PRICE_DROP_THRESHOLD=20.0
```

### Command Line Options
```bash
# Enable notifications
python main.py --enable-notifications

# Set webhook URL
python main.py --webhook-url "https://your-webhook-url"

# Set price drop threshold
python main.py --price-drop-threshold 15.0

# Custom history file location
python main.py --history-file "custom/path/history.json"
```

## Change Types

### 1. New Products
- Triggered when a product appears for the first time
- Priority: Normal
- Notification: Included in summary statistics

### 2. Price Drops
- Triggered when current price is lower than historical price
- Priority: High if drop >= threshold, Normal otherwise
- Notification: High priority drops trigger immediate alerts

### 3. Price Increases
- Triggered when current price is higher than historical price
- Priority: Low
- Notification: Included in summary only

### 4. Availability Changes
- **Sold Out**: Product becomes unavailable
  - Priority: Normal
  - Notification: Included in summary
- **Back in Stock**: Previously sold out product becomes available
  - Priority: High
  - Notification: Triggers immediate alert
- **General Availability**: Other status changes (Limited, etc.)
  - Priority: Low
  - Notification: Summary only

## Notification Triggers

Notifications are sent when any of the following conditions are met:
- One or more priority deals (high priority price drops or back-in-stock items)
- Significant price drops (above threshold)
- Multiple new products (>5)

## Data Storage

### History File
- Location: `data/product_history.json` (configurable)
- Format: JSON with product URL as key
- Cleanup: Automatically removes entries older than 30 days
- Backup: Consider backing up this file for continuity

### Example History Entry
```json
{
  "https://example.com/product": {
    "name": "Product Name",
    "brand": "Brand Name",
    "current_price": 89.99,
    "original_price": 129.99,
    "discount_percentage": 30.8,
    "availability_status": "Available",
    "rating": 4.5,
    "reviews_count": 127,
    "last_seen": "2024-01-15T10:30:00",
    "sale_label": "Save 31%"
  }
}
```

## Webhook Integration

### Slack Integration
1. Create a Slack app and incoming webhook
2. Set the webhook URL in environment variables or CLI
3. Messages will be formatted with emojis and structured data

### Discord Integration
1. Create a Discord webhook in your server
2. Use the webhook URL with the scraper
3. Messages will include formatted change summaries

### Custom Webhooks
The system sends JSON payloads compatible with most webhook services:
```json
{
  "text": "Formatted notification message",
  "username": "Garage Grown Gear Bot",
  "icon_emoji": ":shopping_bags:"
}
```

## Usage Examples

### Basic Change Detection
```bash
# Run with change detection enabled
python main.py --enable-notifications --dry-run
```

### Production Setup
```bash
# Full production run with notifications
python main.py \
  --enable-notifications \
  --webhook-url "$SLACK_WEBHOOK" \
  --price-drop-threshold 15 \
  --log-level INFO
```

### Testing
```bash
# Test change detection with sample data
python examples/example_usage.py
```

## Monitoring and Logs

### Log Messages
- Change detection results are logged with structured data
- Performance metrics include change detection timing
- Error handling for webhook failures

### Metrics Tracked
- Total changes detected
- Changes by type (new, price drop, etc.)
- Notification success/failure rates
- Processing performance

## Best Practices

### 1. Threshold Configuration
- Start with 20% price drop threshold
- Adjust based on typical price variations
- Consider seasonal sales patterns

### 2. History Management
- Regular backups of history file
- Monitor file size growth
- Consider archiving old data

### 3. Notification Frequency
- Avoid notification spam
- Use appropriate thresholds
- Consider time-based filtering for production

### 4. Error Handling
- Monitor webhook delivery success
- Have fallback notification methods
- Log all significant events

## Troubleshooting

### Common Issues

#### No Changes Detected
- Check if history file exists and is readable
- Verify product URLs are consistent
- Ensure sufficient time between runs for changes

#### Webhook Failures
- Verify webhook URL is correct and accessible
- Check network connectivity
- Review webhook service logs

#### False Positives
- Adjust price drop threshold
- Check for data quality issues
- Review product matching logic

### Debug Mode
```bash
# Run with debug logging for troubleshooting
python main.py --log-level DEBUG --dry-run --enable-notifications
```

This will provide detailed logs of the change detection process, including:
- Product comparison details
- Change calculation logic
- Notification decision process
- Webhook delivery attempts