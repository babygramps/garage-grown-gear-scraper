# Google Sheets API Setup Guide

This guide walks you through setting up Google Sheets API credentials for the Garage Grown Gear scraper.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- Basic familiarity with Google Sheets

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "garage-grown-gear-scraper")
5. Click "Create"

## Step 2: Enable Google Sheets API

1. In the Google Cloud Console, make sure your new project is selected
2. Go to "APIs & Services" > "Library"
3. Search for "Google Sheets API"
4. Click on "Google Sheets API" in the results
5. Click "Enable"

## Step 3: Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter a service account name (e.g., "scraper-service-account")
4. Add a description (optional)
5. Click "Create and Continue"
6. Skip the optional steps by clicking "Done"

## Step 4: Generate and Download Credentials

1. In the "Credentials" page, find your service account under "Service Accounts"
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Select "JSON" format
6. Click "Create"
7. The JSON file will be downloaded automatically
8. **Important**: Save this file securely and rename it to `service_account.json`
9. Place the file in your project root directory

## Step 5: Create and Share a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Give it a meaningful name (e.g., "Garage Grown Gear Products")
4. Copy the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
   ```
5. **Important**: Share the spreadsheet with your service account:
   - Click "Share" in the top right
   - Add the service account email (found in your JSON credentials file)
   - Give it "Editor" permissions
   - Click "Send"

## Step 6: Configure Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and set:
   ```env
   SPREADSHEET_ID=your_spreadsheet_id_from_step_5
   CREDENTIALS_FILE=service_account.json
   ```

## Step 7: Test Your Setup

Run the configuration validation script:
```bash
python setup_config.py
```

This will check:
- ✅ Credentials file exists and is valid
- ✅ Spreadsheet ID format is correct
- ✅ All configuration is properly set

## GitHub Actions Setup

If you're using GitHub Actions for automated scraping:

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add these secrets:
   - `GOOGLE_SHEETS_CREDENTIALS`: Base64-encoded content of your JSON credentials file
   - `SPREADSHEET_ID`: Your Google Sheets spreadsheet ID

To encode your credentials file:
```bash
# On Linux/Mac:
base64 -i service_account.json

# On Windows (PowerShell):
[Convert]::ToBase64String([IO.File]::ReadAllBytes("service_account.json"))
```

## Troubleshooting

### Common Issues

**"The caller does not have permission"**
- Make sure you shared the spreadsheet with your service account email
- Check that the service account has "Editor" permissions

**"Credentials file not found"**
- Ensure `service_account.json` is in your project root
- Check the `CREDENTIALS_FILE` environment variable

**"Invalid spreadsheet ID"**
- Verify the spreadsheet ID is exactly 44 characters
- Make sure you copied the ID from the correct part of the URL

**"API not enabled"**
- Ensure Google Sheets API is enabled in your Google Cloud project
- Wait a few minutes after enabling the API

### Getting Help

If you encounter issues:

1. Run `python setup_config.py` for detailed validation
2. Check the error logs for specific error messages
3. Verify all steps in this guide were completed correctly
4. Ensure your Google Cloud project has the Google Sheets API enabled

### Security Best Practices

- **Never commit** your `service_account.json` file to version control
- Add `service_account.json` to your `.gitignore` file
- Use GitHub Secrets for credentials in CI/CD environments
- Regularly rotate your service account keys
- Only grant minimum necessary permissions

## Example Spreadsheet Structure

The scraper will automatically create headers, but your spreadsheet will look like this:

| Timestamp | Product Name | Brand | Current Price | Original Price | Discount % | Availability | Rating | Reviews | Product URL |
|-----------|--------------|-------|---------------|----------------|------------|--------------|--------|---------|-------------|
| 2024-01-15 10:30:00 | Example Product | Brand Name | $29.99 | $49.99 | 40% | Available | 4.5 | 123 | https://... |

The scraper handles all formatting automatically, including:
- Currency formatting for prices
- Percentage formatting for discounts
- Timestamp formatting
- Proper column headers