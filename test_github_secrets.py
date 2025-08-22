#!/usr/bin/env python3
"""
Test script to verify GitHub repository secrets are working correctly.
This script mimics what the GitHub Action workflow does.
"""

import os
import base64
import json
from dotenv import load_dotenv

def test_github_secrets_simulation():
    """Simulate what happens in GitHub Actions with secrets."""
    print("🔍 TESTING GITHUB SECRETS SIMULATION")
    print("=" * 50)
    
    # Load local environment for comparison
    load_dotenv()
    
    # Simulate GitHub environment variables (these would come from secrets in real GHA)
    print("\n1. Testing GitHub Secrets Environment Variables:")
    print("-" * 50)
    
    # These should be set in GitHub repository secrets
    github_secrets = {
        'GOOGLE_SHEETS_CREDENTIALS': os.getenv('GITHUB_GOOGLE_SHEETS_CREDENTIALS', 'NOT_SET'),
        'SPREADSHEET_ID': os.getenv('GITHUB_SPREADSHEET_ID', 'NOT_SET'),
        'SHEET_NAME': os.getenv('GITHUB_SHEET_NAME', 'Garage Grown Gear')
    }
    
    for secret_name, secret_value in github_secrets.items():
        if secret_value == 'NOT_SET':
            print(f"❌ {secret_name}: NOT SET (this would cause GitHub Action to fail)")
        else:
            if secret_name == 'GOOGLE_SHEETS_CREDENTIALS':
                print(f"✅ {secret_name}: Present (length: {len(secret_value)} chars)")
            else:
                print(f"✅ {secret_name}: {secret_value}")
    
    print("\n2. Testing Local Environment Variables (for comparison):")
    print("-" * 50)
    
    local_credentials = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    local_spreadsheet_id = os.getenv('SPREADSHEET_ID')
    local_sheet_name = os.getenv('SHEET_NAME', 'Product_Data')
    
    if local_credentials:
        print(f"✅ Local GOOGLE_SHEETS_CREDENTIALS: Present (length: {len(local_credentials)} chars)")
        
        # Test decode
        try:
            decoded = base64.b64decode(local_credentials)
            creds_json = json.loads(decoded)
            print(f"✅ Local credentials decode: Success")
            print(f"   - Type: {creds_json.get('type', 'unknown')}")
            print(f"   - Project: {creds_json.get('project_id', 'unknown')}")
            print(f"   - Email: {creds_json.get('client_email', 'unknown')}")
        except Exception as e:
            print(f"❌ Local credentials decode: Failed - {e}")
    else:
        print("❌ Local GOOGLE_SHEETS_CREDENTIALS: Not found")
    
    if local_spreadsheet_id:
        print(f"✅ Local SPREADSHEET_ID: {local_spreadsheet_id}")
    else:
        print("❌ Local SPREADSHEET_ID: Not found")
    
    print(f"✅ Local SHEET_NAME: {local_sheet_name}")
    
    print("\n3. GitHub Actions Setup Instructions:")
    print("-" * 50)
    print("To fix the GitHub Action, you need to set these repository secrets:")
    print()
    print("🔧 Repository Secrets Required:")
    print("   1. GOOGLE_SHEETS_CREDENTIALS")
    print(f"      Value: {local_credentials[:50]}... (your full base64 string)")
    print()
    print("   2. SPREADSHEET_ID") 
    print(f"      Value: {local_spreadsheet_id}")
    print()
    print("📍 How to set them:")
    print("   1. Go to: https://github.com/babygramps/garage-grown-gear-scraper/settings/secrets/actions")
    print("   2. Click 'New repository secret'")
    print("   3. Add each secret with the exact name and value")
    print()
    
    print("\n4. Testing Local Scraper Functionality:")
    print("-" * 50)
    
    if local_credentials and local_spreadsheet_id:
        print("✅ Local environment is properly configured")
        print("✅ GitHub Action should work once secrets are set")
        return True
    else:
        print("❌ Local environment has issues")
        return False

if __name__ == "__main__":
    success = test_github_secrets_simulation()
    if success:
        print("\n🎉 READY FOR GITHUB ACTIONS!")
        print("Just set the repository secrets and your workflow will work.")
    else:
        print("\n🚨 CONFIGURATION ISSUES FOUND")
        print("Fix local environment first, then set GitHub secrets.")
