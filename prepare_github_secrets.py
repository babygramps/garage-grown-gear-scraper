#!/usr/bin/env python3
"""
GitHub Secrets Preparation Script
This script helps you prepare the values needed for GitHub repository secrets.
"""

import os
import base64
from dotenv import load_dotenv

def main():
    print("🔧 GITHUB SECRETS PREPARATION")
    print("=" * 35)
    
    # Load environment
    load_dotenv()
    
    print("\n📋 CHECKING YOUR CURRENT CONFIGURATION")
    print("-" * 40)
    
    # Check required environment variables
    required_vars = {
        'GOOGLE_SHEETS_CREDENTIALS': 'Google Sheets API credentials (base64)',
        'SPREADSHEET_ID': 'Google Sheets spreadsheet ID',
        'SHEET_NAME': 'Sheet name (tab name)'
    }
    
    print("✅ Environment variables found:")
    all_present = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'GOOGLE_SHEETS_CREDENTIALS':
                print(f"   {var}: Present (length: {len(value)} chars)")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   ❌ {var}: NOT FOUND")
            all_present = False
    
    if not all_present:
        print("\n🚨 ERROR: Some required environment variables are missing!")
        print("Make sure your .env file is properly configured.")
        return
    
    print("\n🎯 GITHUB REPOSITORY SECRETS TO CREATE")
    print("-" * 40)
    
    print("Go to your GitHub repository > Settings > Secrets and variables > Actions")
    print("Then create these secrets:\n")
    
    # 1. GOOGLE_SHEETS_CREDENTIALS
    credentials = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    print("1️⃣  SECRET NAME: GOOGLE_SHEETS_CREDENTIALS")
    print("   SECRET VALUE (copy this exactly):")
    print(f"   {credentials}")
    print()
    
    # 2. SPREADSHEET_ID
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    print("2️⃣  SECRET NAME: SPREADSHEET_ID")
    print("   SECRET VALUE (copy this exactly):")
    print(f"   {spreadsheet_id}")
    print()
    
    # 3. Optional: SHEET_NAME (if different from default)
    sheet_name = os.getenv('SHEET_NAME', 'Product_Data')
    if sheet_name != 'Product_Data':
        print("3️⃣  SECRET NAME: SHEET_NAME")
        print("   SECRET VALUE (copy this exactly):")
        print(f"   {sheet_name}")
        print("   (This is optional - the workflow is already configured for your sheet name)")
        print()
    
    print("📝 VALIDATION CHECKLIST")
    print("-" * 22)
    
    # Validate credentials format
    try:
        decoded = base64.b64decode(credentials)
        import json
        creds_json = json.loads(decoded)
        
        print("✅ Google Sheets credentials:")
        print(f"   - Format: Valid base64 JSON")
        print(f"   - Type: {creds_json.get('type', 'unknown')}")
        print(f"   - Project: {creds_json.get('project_id', 'unknown')}")
        print(f"   - Email: {creds_json.get('client_email', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Google Sheets credentials: Invalid format - {str(e)}")
    
    # Validate spreadsheet ID
    if len(spreadsheet_id) == 44:
        print("✅ Spreadsheet ID: Correct length (44 characters)")
    else:
        print(f"❌ Spreadsheet ID: Wrong length ({len(spreadsheet_id)} chars, should be 44)")
    
    print("\n🚀 DEPLOYMENT STEPS")
    print("-" * 18)
    print("1. Copy the secret values above")
    print("2. Go to GitHub repo > Settings > Secrets and variables > Actions")
    print("3. Click 'New repository secret' for each one")
    print("4. Paste the exact values (no extra spaces or quotes)")
    print("5. Commit and push your code changes")
    print("6. Go to Actions tab and manually trigger the workflow")
    print("7. Monitor the first run for any issues")
    
    print("\n🔗 HELPFUL LINKS")
    print("-" * 15)
    print(f"📊 Your Google Sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print(f"🔧 GitHub Secrets: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions")
    print(f"⚡ GitHub Actions: https://github.com/YOUR_USERNAME/YOUR_REPO/actions")
    
    print("\n✨ NEXT STEPS")
    print("-" * 12)
    print("After setting up the secrets:")
    print("1. Run: git add .")
    print("2. Run: git commit -m 'Configure GitHub Actions deployment'")
    print("3. Run: git push origin main")
    print("4. Go to GitHub Actions and test the workflow")
    
    print("\n🎉 You're ready to deploy to GitHub Actions!")

if __name__ == "__main__":
    main()
