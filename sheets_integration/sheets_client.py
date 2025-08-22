"""
Google Sheets client for the Garage Grown Gear scraper.

This module provides functionality to authenticate with Google Sheets API,
create sheets, and manage data operations with proper formatting.
"""

import os
import json
import base64
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


@dataclass
class SheetsConfig:
    """Configuration for Google Sheets integration."""
    spreadsheet_id: str
    sheet_name: str = "Product_Data"
    credentials_env_var: str = "GOOGLE_SHEETS_CREDENTIALS"


class SheetsClientError(Exception):
    """Custom exception for Google Sheets client errors."""
    pass


class SheetsClient:
    """
    Google Sheets API client with authentication and data operations.
    
    Handles service account authentication, sheet creation, data appending,
    and formatting operations for the scraper data.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, config: SheetsConfig):
        """
        Initialize the SheetsClient with configuration.
        
        Args:
            config: SheetsConfig object with spreadsheet ID and settings
        """
        self.config = config
        self.service = None
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self) -> None:
        """
        Authenticate with Google Sheets API using service account credentials.
        
        Credentials are expected to be base64 encoded JSON in environment variable.
        
        Raises:
            SheetsClientError: If authentication fails or credentials are invalid
        """
        try:
            # Get credentials from environment variable
            credentials_env_var = getattr(self.config, 'credentials_env_var', 'GOOGLE_SHEETS_CREDENTIALS')
            credentials_b64 = os.getenv(credentials_env_var)
            if not credentials_b64:
                raise SheetsClientError(
                    f"Environment variable {credentials_env_var} not found"
                )
            
            # Decode base64 credentials
            try:
                credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
                credentials_dict = json.loads(credentials_json)
            except (ValueError, json.JSONDecodeError) as e:
                raise SheetsClientError(f"Invalid credentials format: {e}")
            
            # Create service account credentials
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict, scopes=self.SCOPES
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            
            # Test the connection
            self._test_connection()
            
            self.logger.info("Successfully authenticated with Google Sheets API")
            
        except HttpError as e:
            raise SheetsClientError(f"Google Sheets API error: {e}")
        except Exception as e:
            raise SheetsClientError(f"Authentication failed: {e}")
    
    def _test_connection(self) -> None:
        """
        Test the connection to Google Sheets API by attempting to read spreadsheet metadata.
        
        Raises:
            SheetsClientError: If connection test fails
        """
        try:
            # Try to get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            self.logger.info(
                f"Connection test successful. Spreadsheet: {spreadsheet.get('properties', {}).get('title', 'Unknown')}"
            )
            
        except HttpError as e:
            if e.resp.status == 404:
                raise SheetsClientError(
                    f"Spreadsheet with ID {self.config.spreadsheet_id} not found"
                )
            elif e.resp.status == 403:
                raise SheetsClientError(
                    "Access denied. Check service account permissions"
                )
            else:
                raise SheetsClientError(f"Connection test failed: {e}")
    
    def is_authenticated(self) -> bool:
        """
        Check if the client is authenticated and ready to use.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.service is not None
    
    def get_spreadsheet_info(self) -> Dict[str, Any]:
        """
        Get information about the spreadsheet.
        
        Returns:
            Dict containing spreadsheet metadata
            
        Raises:
            SheetsClientError: If not authenticated or API call fails
        """
        if not self.is_authenticated():
            raise SheetsClientError("Client not authenticated. Call authenticate() first.")
        
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            return {
                'title': spreadsheet.get('properties', {}).get('title'),
                'sheets': [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])],
                'url': spreadsheet.get('spreadsheetUrl')
            }
            
        except HttpError as e:
            raise SheetsClientError(f"Failed to get spreadsheet info: {e}")
    
    def sheet_exists(self, sheet_name: str) -> bool:
        """
        Check if a sheet with the given name exists in the spreadsheet.
        
        Args:
            sheet_name: Name of the sheet to check
            
        Returns:
            bool: True if sheet exists, False otherwise
        """
        if not self.is_authenticated():
            raise SheetsClientError("Client not authenticated. Call authenticate() first.")
        
        try:
            info = self.get_spreadsheet_info()
            return sheet_name in info['sheets']
        except SheetsClientError:
            return False
    
    def create_sheet(self, sheet_name: str) -> None:
        """
        Create a new sheet in the spreadsheet.
        
        Args:
            sheet_name: Name of the sheet to create
            
        Raises:
            SheetsClientError: If sheet creation fails
        """
        if not self.is_authenticated():
            raise SheetsClientError("Client not authenticated. Call authenticate() first.")
        
        try:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.config.spreadsheet_id,
                body=request_body
            ).execute()
            
            self.logger.info(f"Created sheet: {sheet_name}")
            
        except HttpError as e:
            raise SheetsClientError(f"Failed to create sheet {sheet_name}: {e}")
    
    def create_sheet_if_not_exists(self, sheet_name: str) -> None:
        """
        Create a sheet if it doesn't already exist.
        
        Args:
            sheet_name: Name of the sheet to create
        """
        if not self.sheet_exists(sheet_name):
            self.create_sheet(sheet_name)
            self.setup_headers(sheet_name)
            self.format_sheet(sheet_name)
        else:
            self.logger.info(f"Sheet {sheet_name} already exists")
    
    def setup_headers(self, sheet_name: str) -> None:
        """
        Set up column headers for the product data sheet.
        
        Args:
            sheet_name: Name of the sheet to set up headers for
        """
        headers = [
            'Timestamp',
            'Product Name', 
            'Brand',
            'Current Price',
            'Original Price',
            'Discount %',
            'Availability',
            'Rating',
            'Reviews Count',
            'Product URL',
            'Sale Label',
            'Image URL'
        ]
        
        try:
            range_name = f"{sheet_name}!A1:L1"
            body = {
                'values': [headers]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.config.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            self.logger.info(f"Set up headers for sheet: {sheet_name}")
            
        except HttpError as e:
            raise SheetsClientError(f"Failed to setup headers for {sheet_name}: {e}")
    
    def append_data(self, sheet_name: str, data: List[List[Any]]) -> None:
        """
        Append data rows to the sheet.
        
        Args:
            sheet_name: Name of the sheet to append data to
            data: List of rows, where each row is a list of values
            
        Raises:
            SheetsClientError: If data appending fails
        """
        if not self.is_authenticated():
            raise SheetsClientError("Client not authenticated. Call authenticate() first.")
        
        if not data:
            self.logger.warning("No data to append")
            return
        
        try:
            range_name = f"{sheet_name}!A:L"
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.config.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            rows_added = result.get('updates', {}).get('updatedRows', 0)
            self.logger.info(f"Appended {rows_added} rows to sheet: {sheet_name}")
            
        except HttpError as e:
            raise SheetsClientError(f"Failed to append data to {sheet_name}: {e}")
    
    def format_sheet(self, sheet_name: str) -> None:
        """
        Apply formatting to the sheet for better readability.
        
        Args:
            sheet_name: Name of the sheet to format
        """
        if not self.is_authenticated():
            raise SheetsClientError("Client not authenticated. Call authenticate() first.")
        
        try:
            # Get sheet ID
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                raise SheetsClientError(f"Sheet {sheet_name} not found")
            
            requests = []
            
            # Format header row (bold, background color)
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
            
            # Format price columns (D, E) as currency
            for col_index in [3, 4]:  # Current Price, Original Price
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startColumnIndex': col_index,
                            'endColumnIndex': col_index + 1,
                            'startRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'numberFormat': {
                                    'type': 'CURRENCY',
                                    'pattern': '$#,##0.00'
                                }
                            }
                        },
                        'fields': 'userEnteredFormat.numberFormat'
                    }
                })
            
            # Format discount percentage column (F) as percentage
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startColumnIndex': 5,
                        'endColumnIndex': 6,
                        'startRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'numberFormat': {
                                'type': 'PERCENT',
                                'pattern': '0.0%'
                            }
                        }
                    },
                    'fields': 'userEnteredFormat.numberFormat'
                }
            })
            
            # Auto-resize columns
            requests.append({
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 12
                    }
                }
            })
            
            # Freeze header row
            requests.append({
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id,
                        'gridProperties': {
                            'frozenRowCount': 1
                        }
                    },
                    'fields': 'gridProperties.frozenRowCount'
                }
            })
            
            # Apply all formatting
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.config.spreadsheet_id,
                body=body
            ).execute()
            
            self.logger.info(f"Applied formatting to sheet: {sheet_name}")
            
        except HttpError as e:
            raise SheetsClientError(f"Failed to format sheet {sheet_name}: {e}")
    
    def clear_sheet(self, sheet_name: str, preserve_headers: bool = True) -> None:
        """
        Clear all data from the sheet, optionally preserving headers.
        
        Args:
            sheet_name: Name of the sheet to clear
            preserve_headers: If True, keep the header row
        """
        if not self.is_authenticated():
            raise SheetsClientError("Client not authenticated. Call authenticate() first.")
        
        try:
            start_row = 2 if preserve_headers else 1
            range_name = f"{sheet_name}!A{start_row}:L"
            
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.config.spreadsheet_id,
                range=range_name
            ).execute()
            
            self.logger.info(f"Cleared data from sheet: {sheet_name}")
            
        except HttpError as e:
            raise SheetsClientError(f"Failed to clear sheet {sheet_name}: {e}")


class ProductDataFormatter:
    """
    Utility class for formatting product data for Google Sheets.
    """
    
    @staticmethod
    def format_product_row(product_data: Dict[str, Any]) -> List[Any]:
        """
        Format a single product data dictionary into a sheet row.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            List of values formatted for Google Sheets
        """
        return [
            datetime.now().isoformat(),  # Timestamp
            product_data.get('name', ''),
            product_data.get('brand', ''),
            ProductDataFormatter._format_price(product_data.get('current_price')),
            ProductDataFormatter._format_price(product_data.get('original_price')),
            ProductDataFormatter._format_percentage(product_data.get('discount_percentage')),
            product_data.get('availability_status', ''),
            product_data.get('rating'),
            product_data.get('reviews_count'),
            product_data.get('product_url', ''),
            product_data.get('sale_label', ''),
            product_data.get('image_url', '')
        ]
    
    @staticmethod
    def format_products_batch(products_data: List[Dict[str, Any]]) -> List[List[Any]]:
        """
        Format multiple product data dictionaries into sheet rows.
        
        Args:
            products_data: List of product data dictionaries
            
        Returns:
            List of rows formatted for Google Sheets
        """
        return [
            ProductDataFormatter.format_product_row(product)
            for product in products_data
        ]
    
    @staticmethod
    def _format_price(price_value: Any) -> Any:
        """Format price value for sheets (handles None, strings, numbers)."""
        if price_value is None:
            return ''
        
        if isinstance(price_value, str):
            # Try to extract numeric value from string
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_value.replace('$', '').replace(',', ''))
            if price_match:
                try:
                    return float(price_match.group().replace(',', ''))
                except ValueError:
                    return price_value
            return price_value
        
        return price_value
    
    @staticmethod
    def _format_percentage(percentage_value: Any) -> Any:
        """Format percentage value for sheets."""
        if percentage_value is None:
            return ''
        
        if isinstance(percentage_value, str):
            # Remove % sign and convert to decimal
            clean_value = percentage_value.replace('%', '').strip()
            try:
                return float(clean_value) / 100
            except ValueError:
                return percentage_value
        
        if isinstance(percentage_value, (int, float)):
            # Assume it's already a percentage, convert to decimal
            return percentage_value / 100 if percentage_value > 1 else percentage_value
        
        return percentage_value


def create_sheets_client(spreadsheet_id: str, sheet_name: str = "Product_Data") -> SheetsClient:
    """
    Factory function to create and authenticate a SheetsClient.
    
    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        sheet_name: Name of the sheet to work with
        
    Returns:
        Authenticated SheetsClient instance
        
    Raises:
        SheetsClientError: If authentication fails
    """
    config = SheetsConfig(
        spreadsheet_id=spreadsheet_id,
        sheet_name=sheet_name
    )
    
    client = SheetsClient(config)
    client.authenticate()
    
    return client