#!/usr/bin/env python3
"""
Quick verification script to check if data was saved to Google Sheets.
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
    
    client = SheetsClient(config)
    client.authenticate()
    
    # Get all data from the sheet
    result = client.service.spreadsheets().values().get(
        spreadsheetId=config.spreadsheet_id,
        range=f'{config.sheet_name}!A:L'
    ).execute()
    
    values = result.get('values', [])
    print(f'✅ Total rows in sheet "{config.sheet_name}": {len(values)}')
    
    if len(values) > 1:
        print('\n📊 Data verification:')
        headers = values[0] if values else []
        data_rows = values[1:] if len(values) > 1 else []
        
        print(f'   - Headers: {", ".join(headers[:4])}...')
        print(f'   - Data rows: {len(data_rows)}')
        
        if data_rows:
            print('\n🔍 Sample of recent data:')
            for i, row in enumerate(data_rows[-3:], 1):
                if len(row) >= 4:
                    timestamp = row[0][:19] if len(row[0]) > 19 else row[0]  # Truncate timestamp
                    product = row[1][:30] + '...' if len(row[1]) > 30 else row[1]  # Truncate long names
                    brand = row[2] if len(row) > 2 else 'N/A'
                    price = row[3] if len(row) > 3 else 'N/A'
                    print(f'   {i}. {timestamp} | {product} | {brand} | {price}')
        
        print(f'\n🎉 SUCCESS! Data is being saved to Google Sheets!')
        print(f'🔗 View your sheet: https://docs.google.com/spreadsheets/d/{config.spreadsheet_id}')
    else:
        print('⚠️  No data found in the sheet. The sheet might be empty.')

if __name__ == "__main__":
    main()
