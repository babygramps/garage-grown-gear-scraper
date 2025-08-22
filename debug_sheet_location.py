#!/usr/bin/env python3
"""
Debug script to identify exactly where data is being written in Google Sheets.
"""

from sheets_integration.sheets_client import SheetsClient, SheetsConfig
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    
    config = SheetsConfig(
        spreadsheet_id=os.getenv('SPREADSHEET_ID'),
        sheet_name=os.getenv('SHEET_NAME', 'Product_Data')
    )
    
    print(f"🔍 DEBUGGING GOOGLE SHEETS LOCATION")
    print(f"=" * 50)
    print(f"Spreadsheet ID: {config.spreadsheet_id}")
    print(f"Target Sheet Name: '{config.sheet_name}'")
    print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{config.spreadsheet_id}")
    
    client = SheetsClient(config)
    client.authenticate()
    
    # Get spreadsheet info to see all sheets
    spreadsheet = client.service.spreadsheets().get(
        spreadsheetId=config.spreadsheet_id
    ).execute()
    
    print(f"\n📋 ALL SHEETS IN YOUR SPREADSHEET:")
    sheets = spreadsheet.get('sheets', [])
    for i, sheet in enumerate(sheets, 1):
        sheet_title = sheet['properties']['title']
        sheet_id = sheet['properties']['sheetId']
        print(f"   {i}. '{sheet_title}' (ID: {sheet_id})")
        
        # Check if this sheet has data
        try:
            result = client.service.spreadsheets().values().get(
                spreadsheetId=config.spreadsheet_id,
                range=f"'{sheet_title}'!A:L"
            ).execute()
            
            values = result.get('values', [])
            row_count = len(values)
            print(f"      📊 {row_count} rows of data")
            
            if row_count > 0:
                # Show first few cells to identify content
                first_row = values[0] if values else []
                preview = " | ".join(first_row[:3]) if first_row else "Empty"
                print(f"      🔍 Preview: {preview[:60]}...")
                
        except Exception as e:
            print(f"      ❌ Error reading sheet: {str(e)}")
    
    print(f"\n🎯 EXPECTED VS ACTUAL:")
    print(f"   Expected sheet: '{config.sheet_name}'")
    actual_sheet_names = [sheet['properties']['title'] for sheet in sheets]
    
    if config.sheet_name in actual_sheet_names:
        print(f"   ✅ Target sheet exists!")
        
        # Get data from the target sheet
        result = client.service.spreadsheets().values().get(
            spreadsheetId=config.spreadsheet_id,
            range=f"'{config.sheet_name}'!A:L"
        ).execute()
        
        values = result.get('values', [])
        print(f"   📊 Data in target sheet: {len(values)} rows")
        
        if len(values) > 1:
            print(f"\n✅ DATA FOUND IN CORRECT SHEET!")
            print(f"🔗 Direct link to your sheet:")
            print(f"   https://docs.google.com/spreadsheets/d/{config.spreadsheet_id}/edit#gid={[s['properties']['sheetId'] for s in sheets if s['properties']['title'] == config.sheet_name][0]}")
        else:
            print(f"\n⚠️  Sheet exists but appears empty")
            
    else:
        print(f"   ❌ Target sheet '{config.sheet_name}' not found!")
        print(f"   Available sheets: {actual_sheet_names}")
    
    print(f"\n💡 TROUBLESHOOTING STEPS:")
    print(f"1. Open: https://docs.google.com/spreadsheets/d/{config.spreadsheet_id}")
    print(f"2. Look for the sheet tab named '{config.sheet_name}' at the bottom")
    print(f"3. If you see a different sheet name, check your SHEET_NAME in .env file")
    print(f"4. Make sure you're looking at the correct Google account")

if __name__ == "__main__":
    main()
