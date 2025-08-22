# GitHub Actions Workflow Setup

This document provides setup instructions for the Garage Grown Gear scraper GitHub Actions workflows.

## Required Secrets

The following secrets must be configured in your GitHub repository settings:

### `GOOGLE_SHEETS_CREDENTIALS`
- **Type**: Base64 encoded JSON
- **Description**: Google Service Account credentials for Sheets API access
- **Setup**:
  1. Create a Google Cloud Project
  2. Enable the Google Sheets API
  3. Create a Service Account
  4. Download the JSON key file
  5. Base64 encode the file: `base64 -i service_account.json`
  6. Add the encoded string as a repository secret

### `SPREADSHEET_ID`
- **Type**: String
- **Description**: The ID of the Google Sheets document to write data to
- **Setup**:
  1. Create a new Google Sheet or use an existing one
  2. Share the sheet with your service account email (found in the JSON key)
  3. Extract the spreadsheet ID from the URL: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`

## Workflow Files

### `scraper.yml`
- **Purpose**: Main scraper execution workflow
- **Schedule**: Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
- **Features**:
  - Automatic retry logic (3 attempts by default)
  - Comprehensive error handling and logging
  - Artifact collection for debugging
  - Manual trigger support with debug options
  - Job status reporting and monitoring

### `scraper-health-check.yml`
- **Purpose**: Daily health monitoring of scraper performance
- **Schedule**: Daily at 9:00 AM UTC
- **Features**:
  - Health status reporting
  - Performance monitoring
  - Failure detection and alerting

## Workflow Configuration

### Environment Variables
- `PYTHON_VERSION`: Python version to use (default: 3.11)
- `MAX_RETRIES`: Number of retry attempts for failed runs (default: 3)

### Manual Triggers
Both workflows support manual triggering with optional parameters:
- `debug_mode`: Enable verbose logging
- `retry_count`: Override default retry attempts

## Monitoring and Alerts

### Success Indicators
- Workflow completes without errors
- Artifacts are generated with scraper statistics
- Google Sheets is updated with new data

### Failure Indicators
- All retry attempts exhausted
- Authentication failures
- Network connectivity issues
- Data validation errors

### Artifacts Generated
- `scraper-artifacts-{run_number}`: Logs, statistics, and error reports
- `monitoring-report-{run_number}`: Workflow execution analysis
- `health-report-{run_number}`: Daily health check results

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify `GOOGLE_SHEETS_CREDENTIALS` secret is properly base64 encoded
   - Ensure service account has access to the target spreadsheet
   - Check that Google Sheets API is enabled in your project

2. **Scraping Failures**
   - Website structure may have changed
   - Rate limiting or blocking by target site
   - Network connectivity issues

3. **Workflow Timeouts**
   - Increase timeout values if scraping takes longer than expected
   - Check for infinite loops in pagination handling

### Debugging Steps

1. Enable debug mode in manual workflow trigger
2. Check workflow logs in GitHub Actions tab
3. Download and examine artifacts from failed runs
4. Review error reports and stack traces
5. Test locally with same environment variables

## Security Considerations

- Secrets are automatically masked in workflow logs
- Credentials files are cleaned up after each run
- Service account follows principle of least privilege
- No sensitive data is committed to repository

## Performance Optimization

- Workflows use pip caching to speed up dependency installation
- Artifacts have appropriate retention periods to manage storage
- Health checks run separately to avoid impacting main scraper performance
- Retry logic includes delays to respect rate limits

## Maintenance

- Review workflow performance monthly
- Update Python version and dependencies regularly
- Monitor artifact storage usage
- Adjust scheduling based on data freshness requirements