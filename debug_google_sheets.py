"""
Debug script to help identify Google Sheets configuration issues.

This script performs comprehensive testing of Google Sheets integration
and provides detailed logging to help troubleshoot data saving issues.
"""

import os
import sys
import json
import base64
import logging
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check if required environment variables are set."""
    logger.info("=== CHECKING ENVIRONMENT VARIABLES ===")
    
    required_vars = [
        'GOOGLE_SHEETS_CREDENTIALS',
        'SPREADSHEET_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            logger.error(f"❌ {var}: NOT SET")
        else:
            logger.info(f"✅ {var}: SET (length: {len(value)} chars)")
    
    # Check optional variables
    optional_vars = [
        'SHEET_NAME',
        'CREDENTIALS_FILE'
    ]
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"ℹ️  {var}: {value}")
        else:
            logger.info(f"ℹ️  {var}: NOT SET (will use default)")
    
    return missing_vars

def validate_credentials_format():
    """Validate the format of Google Sheets credentials."""
    logger.info("=== VALIDATING CREDENTIALS FORMAT ===")
    
    credentials_b64 = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    if not credentials_b64:
        logger.error("❌ GOOGLE_SHEETS_CREDENTIALS not found")
        return False
    
    try:
        # Try to decode base64
        credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
        logger.info("✅ Base64 decoding successful")
        
        # Try to parse JSON
        credentials_dict = json.loads(credentials_json)
        logger.info("✅ JSON parsing successful")
        
        # Check required fields
        required_fields = [
            'type',
            'project_id',
            'private_key_id',
            'private_key',
            'client_email',
            'client_id'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in credentials_dict:
                missing_fields.append(field)
                logger.error(f"❌ Missing required field: {field}")
            else:
                if field == 'private_key':
                    logger.info(f"✅ {field}: Present (length: {len(credentials_dict[field])} chars)")
                else:
                    logger.info(f"✅ {field}: {credentials_dict[field]}")
        
        if missing_fields:
            logger.error(f"❌ Missing required fields: {missing_fields}")
            return False
        
        # Validate service account type
        if credentials_dict.get('type') != 'service_account':
            logger.error(f"❌ Invalid credentials type: {credentials_dict.get('type')} (should be 'service_account')")
            return False
        
        logger.info("✅ Credentials format validation passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Credentials format validation failed: {str(e)}")
        return False

def validate_spreadsheet_id():
    """Validate the spreadsheet ID format."""
    logger.info("=== VALIDATING SPREADSHEET ID ===")
    
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    if not spreadsheet_id:
        logger.error("❌ SPREADSHEET_ID not found")
        return False
    
    logger.info(f"Spreadsheet ID: {spreadsheet_id}")
    logger.info(f"Length: {len(spreadsheet_id)} characters")
    
    # Validate format (should be 44 characters, alphanumeric with dashes/underscores)
    import re
    if not re.match(r'^[a-zA-Z0-9-_]{44}$', spreadsheet_id):
        logger.error("❌ Invalid spreadsheet ID format (should be 44 characters, alphanumeric with dashes/underscores)")
        return False
    
    logger.info("✅ Spreadsheet ID format is valid")
    return True

def test_google_sheets_connection():
    """Test the connection to Google Sheets API."""
    logger.info("=== TESTING GOOGLE SHEETS CONNECTION ===")
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        # Get credentials
        credentials_b64 = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
        credentials_dict = json.loads(credentials_json)
        
        # Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict, 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        logger.info("✅ Service account credentials created successfully")
        
        # Build service
        service = build('sheets', 'v4', credentials=credentials)
        logger.info("✅ Google Sheets service built successfully")
        
        # Test connection by getting spreadsheet metadata
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        title = spreadsheet.get('properties', {}).get('title', 'Unknown')
        sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        
        logger.info(f"✅ Successfully connected to spreadsheet: '{title}'")
        logger.info(f"✅ Available sheets: {sheets}")
        
        return True, service, spreadsheet
        
    except ImportError as e:
        logger.error(f"❌ Missing required Google libraries: {str(e)}")
        logger.error("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False, None, None
    except HttpError as e:
        error_details = e.error_details if hasattr(e, 'error_details') else str(e)
        logger.error(f"❌ Google Sheets API error: {error_details}")
        
        if e.resp.status == 404:
            logger.error("❌ Spreadsheet not found. Check the SPREADSHEET_ID.")
        elif e.resp.status == 403:
            logger.error("❌ Access denied. Make sure the service account has access to the spreadsheet.")
            logger.error("   Share the spreadsheet with the service account email address.")
        
        return False, None, None
    except Exception as e:
        logger.error(f"❌ Connection test failed: {str(e)}")
        return False, None, None

def test_sheet_operations(service, spreadsheet):
    """Test basic sheet operations."""
    logger.info("=== TESTING SHEET OPERATIONS ===")
    
    try:
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        sheet_name = os.getenv('SHEET_NAME', 'Product_Data')
        
        # Check if the target sheet exists
        sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        
        if sheet_name in sheets:
            logger.info(f"✅ Target sheet '{sheet_name}' exists")
        else:
            logger.warning(f"⚠️  Target sheet '{sheet_name}' does not exist")
            logger.info(f"Available sheets: {sheets}")
            
            # Try to create the sheet
            logger.info(f"Attempting to create sheet '{sheet_name}'...")
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            
            logger.info(f"✅ Successfully created sheet '{sheet_name}'")
        
        # Test reading from the sheet
        try:
            range_name = f"{sheet_name}!A1:L10"
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"✅ Successfully read from sheet. Found {len(values)} rows")
            
            if values:
                logger.info(f"First row: {values[0]}")
            
        except Exception as e:
            logger.error(f"❌ Failed to read from sheet: {str(e)}")
        
        # Test writing to the sheet
        try:
            test_data = [
                ['Test Timestamp', 'Test Product', 'Test Brand', '$99.99', '$149.99', '33.3%', 'Available', '4.5', '100', 'https://example.com', 'Sale', 'https://example.com/image.jpg']
            ]
            
            range_name = f"{sheet_name}!A1:L1"
            body = {
                'values': test_data
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"✅ Successfully wrote test data to sheet")
            logger.info(f"Updated {result.get('updatedCells', 0)} cells")
            
        except Exception as e:
            logger.error(f"❌ Failed to write to sheet: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Sheet operations test failed: {str(e)}")
        return False

def test_scraper_integration():
    """Test the integration with the scraper's Google Sheets client."""
    logger.info("=== TESTING SCRAPER INTEGRATION ===")
    
    try:
        from sheets_integration.sheets_client import SheetsClient, SheetsConfig
        
        # Create config
        config = SheetsConfig(
            spreadsheet_id=os.getenv('SPREADSHEET_ID'),
            sheet_name=os.getenv('SHEET_NAME', 'Product_Data')
        )
        
        logger.info(f"✅ Created SheetsConfig: {config}")
        
        # Create client
        client = SheetsClient(config)
        logger.info("✅ Created SheetsClient")
        
        # Test authentication
        client.authenticate()
        logger.info("✅ Authentication successful")
        
        # Test sheet creation
        client.create_sheet_if_not_exists(config.sheet_name)
        logger.info(f"✅ Sheet '{config.sheet_name}' is ready")
        
        # Test data appending
        test_data = [
            [
                datetime.now().isoformat(),
                'Test Product from Scraper',
                'Test Brand',
                '$49.99',
                '$79.99',
                '37.5%',
                'Available',
                '4.2',
                '85',
                'https://example.com/product',
                'Limited Time Sale',
                'https://example.com/image.jpg'
            ]
        ]
        
        client.append_data(config.sheet_name, test_data)
        logger.info("✅ Successfully appended test data using scraper client")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Scraper integration test failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def provide_setup_guidance():
    """Provide guidance on how to set up Google Sheets integration."""
    logger.info("=== SETUP GUIDANCE ===")
    
    logger.info("""
To set up Google Sheets integration:

1. CREATE GOOGLE CLOUD PROJECT:
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing one
   - Enable the Google Sheets API

2. CREATE SERVICE ACCOUNT:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Fill in details and click "Create and Continue"
   - Skip role assignment (optional)
   - Click "Done"

3. CREATE SERVICE ACCOUNT KEY:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the key file

4. CREATE GOOGLE SPREADSHEET:
   - Go to https://sheets.google.com/
   - Create a new spreadsheet
   - Copy the spreadsheet ID from the URL
   - Share the spreadsheet with your service account email
   - Give it "Editor" permissions

5. SET ENVIRONMENT VARIABLES:
   - SPREADSHEET_ID: Your spreadsheet ID (44 characters)
   - GOOGLE_SHEETS_CREDENTIALS: Base64-encoded JSON key content

6. ENCODE CREDENTIALS:
   PowerShell: [Convert]::ToBase64String([IO.File]::ReadAllBytes("path/to/your/key.json"))
   Linux/Mac: base64 -i path/to/your/key.json

Example .env file:
```
SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_SHEETS_CREDENTIALS=eyJ0eXBlIjoic2VydmljZV9hY2NvdW50Ii...
SHEET_NAME=Product_Data
```
""")

def main():
    """Main debug function."""
    logger.info("🔍 STARTING GOOGLE SHEETS DEBUG ANALYSIS")
    logger.info("=" * 60)
    
    issues_found = []
    
    # Check environment variables
    missing_vars = check_environment_variables()
    if missing_vars:
        issues_found.extend([f"Missing environment variable: {var}" for var in missing_vars])
    
    # Only proceed if we have the required variables
    if not missing_vars:
        # Validate credentials format
        if not validate_credentials_format():
            issues_found.append("Invalid credentials format")
        
        # Validate spreadsheet ID
        if not validate_spreadsheet_id():
            issues_found.append("Invalid spreadsheet ID")
        
        # Test Google Sheets connection
        success, service, spreadsheet = test_google_sheets_connection()
        if not success:
            issues_found.append("Google Sheets connection failed")
        else:
            # Test sheet operations
            if not test_sheet_operations(service, spreadsheet):
                issues_found.append("Sheet operations failed")
            
            # Test scraper integration
            if not test_scraper_integration():
                issues_found.append("Scraper integration failed")
    
    # Summary
    logger.info("=" * 60)
    logger.info("🔍 DEBUG ANALYSIS COMPLETE")
    
    if issues_found:
        logger.error("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            logger.error(f"   {i}. {issue}")
        
        logger.info("\n📋 NEXT STEPS:")
        if missing_vars:
            logger.info("   1. Set up the missing environment variables")
            provide_setup_guidance()
        else:
            logger.info("   1. Review the error messages above")
            logger.info("   2. Check the setup guidance below")
            provide_setup_guidance()
    else:
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("   Google Sheets integration should be working correctly.")
        logger.info("   If data is still not being saved, check the main scraper logs.")

if __name__ == "__main__":
    main()
