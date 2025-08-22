"""
Tests for Google Sheets integration.
"""

import os
import json
import base64
import pytest
from unittest.mock import Mock, patch, MagicMock

from sheets_integration.sheets_client import (
    SheetsClient, 
    SheetsConfig, 
    SheetsClientError,
    create_sheets_client
)


class TestSheetsClient:
    """Test cases for SheetsClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = SheetsConfig(
            spreadsheet_id="test_spreadsheet_id",
            sheet_name="Test_Sheet"
        )
        self.client = SheetsClient(self.config)
    
    def test_init(self):
        """Test SheetsClient initialization."""
        assert self.client.config == self.config
        assert self.client.service is None
        assert not self.client.is_authenticated()
    
    @patch('sheets_integration.sheets_client.build')
    @patch('sheets_integration.sheets_client.service_account')
    def test_authenticate_success(self, mock_service_account, mock_build):
        """Test successful authentication."""
        # Mock credentials
        mock_credentials = Mock()
        mock_service_account.Credentials.from_service_account_info.return_value = mock_credentials
        
        # Mock service
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock successful connection test
        mock_spreadsheet_response = {
            'properties': {'title': 'Test Spreadsheet'}
        }
        mock_service.spreadsheets().get().execute.return_value = mock_spreadsheet_response
        
        # Mock environment variable
        test_credentials = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "test-client-id"
        }
        credentials_b64 = base64.b64encode(json.dumps(test_credentials).encode()).decode()
        
        with patch.dict(os.environ, {'GOOGLE_SHEETS_CREDENTIALS': credentials_b64}):
            self.client.authenticate()
        
        # Verify authentication
        assert self.client.is_authenticated()
        assert self.client.service == mock_service
        
        # Verify service account credentials were created correctly
        mock_service_account.Credentials.from_service_account_info.assert_called_once_with(
            test_credentials, scopes=SheetsClient.SCOPES
        )
        
        # Verify service was built correctly
        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_credentials)
    
    def test_authenticate_missing_env_var(self):
        """Test authentication failure when environment variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SheetsClientError, match="Environment variable GOOGLE_SHEETS_CREDENTIALS not found"):
                self.client.authenticate()
    
    def test_authenticate_invalid_credentials(self):
        """Test authentication failure with invalid credentials."""
        with patch.dict(os.environ, {'GOOGLE_SHEETS_CREDENTIALS': 'invalid_base64'}):
            with pytest.raises(SheetsClientError, match="Invalid credentials format"):
                self.client.authenticate()
    
    @patch('sheets_integration.sheets_client.build')
    @patch('sheets_integration.sheets_client.service_account')
    def test_connection_test_failure(self, mock_service_account, mock_build):
        """Test authentication failure during connection test."""
        # Mock credentials and service
        mock_credentials = Mock()
        mock_service_account.Credentials.from_service_account_info.return_value = mock_credentials
        
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock connection test failure
        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 404
        error = HttpError(mock_response, b'Not found')
        mock_service.spreadsheets().get().execute.side_effect = error
        
        # Mock environment variable
        test_credentials = {"type": "service_account", "project_id": "test"}
        credentials_b64 = base64.b64encode(json.dumps(test_credentials).encode()).decode()
        
        with patch.dict(os.environ, {'GOOGLE_SHEETS_CREDENTIALS': credentials_b64}):
            with pytest.raises(SheetsClientError, match="Spreadsheet with ID test_spreadsheet_id not found"):
                self.client.authenticate()
    
    @patch('sheets_integration.sheets_client.build')
    @patch('sheets_integration.sheets_client.service_account')
    def test_get_spreadsheet_info(self, mock_service_account, mock_build):
        """Test getting spreadsheet information."""
        # Set up authenticated client
        mock_service = Mock()
        self.client.service = mock_service
        
        # Mock spreadsheet response
        mock_response = {
            'properties': {'title': 'Test Spreadsheet'},
            'sheets': [
                {'properties': {'title': 'Sheet1'}},
                {'properties': {'title': 'Sheet2'}}
            ],
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/test_id'
        }
        mock_service.spreadsheets().get().execute.return_value = mock_response
        
        info = self.client.get_spreadsheet_info()
        
        expected = {
            'title': 'Test Spreadsheet',
            'sheets': ['Sheet1', 'Sheet2'],
            'url': 'https://docs.google.com/spreadsheets/d/test_id'
        }
        assert info == expected
    
    def test_get_spreadsheet_info_not_authenticated(self):
        """Test getting spreadsheet info when not authenticated."""
        with pytest.raises(SheetsClientError, match="Client not authenticated"):
            self.client.get_spreadsheet_info()


    @patch('sheets_integration.sheets_client.build')
    @patch('sheets_integration.sheets_client.service_account')
    def test_sheet_exists(self, mock_service_account, mock_build):
        """Test checking if sheet exists."""
        # Set up authenticated client
        mock_service = Mock()
        self.client.service = mock_service
        
        # Mock spreadsheet response
        mock_response = {
            'properties': {'title': 'Test Spreadsheet'},
            'sheets': [
                {'properties': {'title': 'Sheet1'}},
                {'properties': {'title': 'Sheet2'}}
            ],
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/test_id'
        }
        mock_service.spreadsheets().get().execute.return_value = mock_response
        
        assert self.client.sheet_exists('Sheet1') is True
        assert self.client.sheet_exists('NonExistent') is False
    
    def test_create_sheet(self):
        """Test creating a new sheet."""
        # Set up authenticated client
        mock_service = Mock()
        self.client.service = mock_service
        
        self.client.create_sheet('New_Sheet')
        
        # Verify batchUpdate was called with correct parameters
        mock_service.spreadsheets().batchUpdate.assert_called_once()
        call_args = mock_service.spreadsheets().batchUpdate.call_args
        
        assert call_args[1]['spreadsheetId'] == 'test_spreadsheet_id'
        assert 'requests' in call_args[1]['body']
        assert call_args[1]['body']['requests'][0]['addSheet']['properties']['title'] == 'New_Sheet'
    
    @patch.object(SheetsClient, 'sheet_exists')
    @patch.object(SheetsClient, 'create_sheet')
    @patch.object(SheetsClient, 'setup_headers')
    @patch.object(SheetsClient, 'format_sheet')
    def test_create_sheet_if_not_exists_new_sheet(self, mock_format, mock_headers, mock_create, mock_exists):
        """Test creating sheet when it doesn't exist."""
        mock_exists.return_value = False
        
        self.client.create_sheet_if_not_exists('New_Sheet')
        
        mock_create.assert_called_once_with('New_Sheet')
        mock_headers.assert_called_once_with('New_Sheet')
        mock_format.assert_called_once_with('New_Sheet')
    
    @patch.object(SheetsClient, 'sheet_exists')
    @patch.object(SheetsClient, 'create_sheet')
    def test_create_sheet_if_not_exists_existing_sheet(self, mock_create, mock_exists):
        """Test not creating sheet when it already exists."""
        mock_exists.return_value = True
        
        self.client.create_sheet_if_not_exists('Existing_Sheet')
        
        mock_create.assert_not_called()
    
    def test_setup_headers(self):
        """Test setting up column headers."""
        # Set up authenticated client
        mock_service = Mock()
        self.client.service = mock_service
        
        self.client.setup_headers('Test_Sheet')
        
        # Verify values().update was called with correct headers
        mock_service.spreadsheets().values().update.assert_called_once()
        call_args = mock_service.spreadsheets().values().update.call_args
        
        assert call_args[1]['range'] == 'Test_Sheet!A1:L1'
        headers = call_args[1]['body']['values'][0]
        expected_headers = [
            'Timestamp', 'Product Name', 'Brand', 'Current Price', 'Original Price',
            'Discount %', 'Availability', 'Rating', 'Reviews Count', 'Product URL',
            'Sale Label', 'Image URL'
        ]
        assert headers == expected_headers
    
    def test_append_data(self):
        """Test appending data to sheet."""
        # Set up authenticated client
        mock_service = Mock()
        self.client.service = mock_service
        
        # Mock successful append response
        mock_append = Mock()
        mock_append.execute.return_value = {'updates': {'updatedRows': 2}}
        mock_service.spreadsheets().values().append.return_value = mock_append
        
        test_data = [
            ['2024-01-01T12:00:00', 'Product 1', 'Brand A', 29.99, 39.99, 0.25, 'Available', 4.5, 100, 'http://example.com/1'],
            ['2024-01-01T12:01:00', 'Product 2', 'Brand B', 19.99, 24.99, 0.20, 'Available', 4.0, 50, 'http://example.com/2']
        ]
        
        self.client.append_data('Test_Sheet', test_data)
        
        # Verify append was called correctly
        mock_service.spreadsheets().values().append.assert_called_once_with(
            spreadsheetId='test_spreadsheet_id',
            range='Test_Sheet!A:L',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': test_data}
        )
    
    def test_append_data_empty(self):
        """Test appending empty data."""
        # Set up authenticated client
        mock_service = Mock()
        self.client.service = mock_service
        
        self.client.append_data('Test_Sheet', [])
        
        # Verify append was not called
        mock_service.spreadsheets().values().append.assert_not_called()


class TestProductDataFormatter:
    """Test cases for ProductDataFormatter class."""
    
    def test_format_product_row(self):
        """Test formatting a single product row."""
        from sheets_integration.sheets_client import ProductDataFormatter
        
        product_data = {
            'name': 'Test Product',
            'brand': 'Test Brand',
            'current_price': 29.99,
            'original_price': 39.99,
            'discount_percentage': 25,
            'availability_status': 'Available',
            'rating': 4.5,
            'reviews_count': 100,
            'product_url': 'http://example.com/product',
            'sale_label': 'Save 25%',
            'image_url': 'http://example.com/image.jpg'
        }
        
        row = ProductDataFormatter.format_product_row(product_data)
        
        # Check that all expected fields are present (timestamp will be generated)
        assert len(row) == 12
        assert row[1] == 'Test Product'
        assert row[2] == 'Test Brand'
        assert row[3] == 29.99
        assert row[4] == 39.99
        assert row[5] == 0.25  # Percentage converted to decimal
        assert row[6] == 'Available'
        assert row[7] == 4.5
        assert row[8] == 100
        assert row[9] == 'http://example.com/product'
        assert row[10] == 'Save 25%'
        assert row[11] == 'http://example.com/image.jpg'
    
    def test_format_products_batch(self):
        """Test formatting multiple products."""
        from sheets_integration.sheets_client import ProductDataFormatter
        
        products_data = [
            {'name': 'Product 1', 'brand': 'Brand A', 'current_price': 29.99},
            {'name': 'Product 2', 'brand': 'Brand B', 'current_price': 19.99}
        ]
        
        rows = ProductDataFormatter.format_products_batch(products_data)
        
        assert len(rows) == 2
        assert rows[0][1] == 'Product 1'
        assert rows[1][1] == 'Product 2'
    
    def test_format_price_string(self):
        """Test price formatting from string."""
        from sheets_integration.sheets_client import ProductDataFormatter
        
        assert ProductDataFormatter._format_price('$29.99') == 29.99
        assert ProductDataFormatter._format_price('$1,299.99') == 1299.99
        assert ProductDataFormatter._format_price('29.99') == 29.99
        assert ProductDataFormatter._format_price(None) == ''
        assert ProductDataFormatter._format_price('Invalid') == 'Invalid'
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        from sheets_integration.sheets_client import ProductDataFormatter
        
        assert ProductDataFormatter._format_percentage('25%') == 0.25
        assert ProductDataFormatter._format_percentage('25') == 0.25
        assert ProductDataFormatter._format_percentage(25) == 0.25
        assert ProductDataFormatter._format_percentage(0.25) == 0.25
        assert ProductDataFormatter._format_percentage(None) == ''


class TestCreateSheetsClient:
    """Test cases for create_sheets_client factory function."""
    
    @patch('sheets_integration.sheets_client.SheetsClient.authenticate')
    def test_create_sheets_client(self, mock_authenticate):
        """Test factory function creates and authenticates client."""
        client = create_sheets_client("test_id", "Test_Sheet")
        
        assert isinstance(client, SheetsClient)
        assert client.config.spreadsheet_id == "test_id"
        assert client.config.sheet_name == "Test_Sheet"
        mock_authenticate.assert_called_once()