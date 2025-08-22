#!/usr/bin/env python3
"""
Configuration setup and validation script for Garage Grown Gear scraper.
This script helps users set up their configuration and validate it before running the scraper.
"""

import os
import sys
import json
import base64
from pathlib import Path
from typing import Dict, Any

from config import AppConfig, ConfigurationError


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'scrapling',
        'google-api-python-client',
        'google-auth',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    if missing_packages:
        print(f"\nTo install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example_path.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        env_example_path.read_text()
        with open(env_path, 'w') as f:
            f.write(env_example_path.read_text())
        print("✅ Created .env file from .env.example")
        print("⚠️  Please edit .env file with your actual configuration values")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def validate_google_sheets_credentials():
    """Validate Google Sheets credentials setup."""
    credentials_file = os.getenv('CREDENTIALS_FILE', 'service_account.json')
    
    # Check if credentials file exists
    if not Path(credentials_file).exists():
        print(f"❌ Credentials file not found: {credentials_file}")
        print("\nTo set up Google Sheets credentials:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API")
        print("4. Create a service account")
        print("5. Download the JSON key file")
        print(f"6. Save it as '{credentials_file}' in the project root")
        return False
    
    # Try to parse credentials file
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Credentials file missing required fields: {', '.join(missing_fields)}")
            return False
        
        if creds.get('type') != 'service_account':
            print("❌ Credentials file must be for a service account")
            return False
        
        print("✅ Google Sheets credentials file is valid")
        return True
        
    except json.JSONDecodeError:
        print(f"❌ Credentials file is not valid JSON: {credentials_file}")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False


def validate_spreadsheet_id():
    """Validate Google Sheets spreadsheet ID."""
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    if not spreadsheet_id:
        print("❌ SPREADSHEET_ID not set in environment variables")
        print("\nTo get your spreadsheet ID:")
        print("1. Create a new Google Sheet or open existing one")
        print("2. Copy the ID from the URL:")
        print("   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit")
        print("3. Share the sheet with your service account email")
        print("4. Set SPREADSHEET_ID in your .env file")
        return False
    
    # Basic format validation
    if len(spreadsheet_id) != 44:
        print(f"❌ SPREADSHEET_ID appears to have incorrect length: {len(spreadsheet_id)} (expected 44)")
        return False
    
    print("✅ SPREADSHEET_ID format looks correct")
    return True


def validate_configuration():
    """Validate the complete configuration."""
    try:
        config = AppConfig.from_env()
        errors = config.validate_all()
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ All configuration validation passed")
        return True
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error validating configuration: {e}")
        return False


def setup_github_secrets():
    """Provide instructions for setting up GitHub secrets."""
    print("\n📋 GitHub Secrets Setup Instructions:")
    print("=" * 50)
    
    credentials_file = os.getenv('CREDENTIALS_FILE', 'service_account.json')
    
    if Path(credentials_file).exists():
        try:
            with open(credentials_file, 'r') as f:
                creds_content = f.read()
            
            # Encode credentials as base64 for GitHub secrets
            encoded_creds = base64.b64encode(creds_content.encode()).decode()
            
            print("1. Go to your GitHub repository")
            print("2. Navigate to Settings > Secrets and variables > Actions")
            print("3. Add the following secrets:")
            print(f"   - GOOGLE_SHEETS_CREDENTIALS: {encoded_creds[:50]}...")
            print(f"   - SPREADSHEET_ID: {os.getenv('SPREADSHEET_ID', 'your_spreadsheet_id')}")
            print("\n4. The GitHub Actions workflow will use these secrets automatically")
            
        except Exception as e:
            print(f"❌ Error reading credentials for GitHub setup: {e}")
    else:
        print("❌ Set up Google Sheets credentials first")


def main():
    """Main setup and validation function."""
    print("🔧 Garage Grown Gear Scraper Configuration Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_dependencies():
        return False
    
    # Set up configuration files
    if not create_env_file():
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Validate configuration components
    success = True
    
    if not validate_google_sheets_credentials():
        success = False
    
    if not validate_spreadsheet_id():
        success = False
    
    if not validate_configuration():
        success = False
    
    if success:
        print("\n🎉 Configuration setup completed successfully!")
        print("You can now run the scraper with: python main.py")
        
        # Offer GitHub setup instructions
        response = input("\nWould you like to see GitHub Actions setup instructions? (y/n): ")
        if response.lower().startswith('y'):
            setup_github_secrets()
    else:
        print("\n❌ Configuration setup incomplete. Please fix the issues above.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)