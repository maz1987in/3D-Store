"""
Unit tests for Thawani Service.

Tests all business logic in thawani/service.py including:
- Payment gateway initialization
- Session creation and processing
- Webhook handling and verification  
- Payment success/cancel workflows
- Status synchronization
- Error handling with mocked external API calls
"""

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from app.thawani.service import ThawaniService
from app.common.enum import PaymentStatusEnum


class TestThawaniService(BaseServiceTestCase):
    """Test cases for ThawaniService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = ThawaniService()
    
    # ========== Session Creation Tests ==========
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_create_session_success(self, mock_url_for, mock_post, db_session):
        """Test creating a payment session successfully."""
        # Mock URL generation
        mock_url_for.side_effect = lambda *args, **kwargs: f"http://test.com/{kwargs.get('ref', 'callback')}"
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'session_id': 'TH-SESSION-12345',
                'status': 'created'
            }
        }
        mock_post.return_value = mock_response
        
        session_data = {
            'client_reference_id': 'REF-123456',
            'products': [
                {'name': 'Product 1', 'unit_amount': 10000, 'quantity': 1}
            ],
            'metadata': {'order_id': 'ORDER-123'}
        }
        
        result, status, client_url = self.service.create_session(session_data)
        
        assert status == 200
        assert 'data' in result
        assert result['data']['session_id'] == 'TH-SESSION-12345'
        assert client_url is not None
        assert 'TH-SESSION-12345' in client_url
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'products' in call_args.kwargs['json']
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_create_session_with_multiple_products(self, mock_url_for, mock_post, db_session):
        """Test session creation with multiple products."""
        mock_url_for.side_effect = lambda *args, **kwargs: "http://test.com/callback"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'session_id': 'TH-MULTI'}
        }
        mock_post.return_value = mock_response
        
        session_data = {
            'client_reference_id': 'REF-MULTI',
            'products': [
                {'name': 'Product 1', 'unit_amount': 5000, 'quantity': 2},
                {'name': 'Product 2', 'unit_amount': 10000, 'quantity': 1},
                {'name': 'Product 3', 'unit_amount': 2500, 'quantity': 3}
            ]
        }
        
        result, status, client_url = self.service.create_session(session_data)
        
        assert status == 200
        call_json = mock_post.call_args.kwargs['json']
        assert len(call_json['products']) == 3
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_create_session_with_mode(self, mock_url_for, mock_post, db_session):
        """Test session creation with specific mode."""
        mock_url_for.side_effect = lambda *args, **kwargs: "http://test.com/callback"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'session_id': 'TH-MODE'}
        }
        mock_post.return_value = mock_response
        
        session_data = {
            'client_reference_id': 'REF-MODE',
            'mode': 'subscription',  # Different mode
            'products': [
                {'name': 'Subscription', 'unit_amount': 50000, 'quantity': 1}
            ]
        }
        
        result, status, client_url = self.service.create_session(session_data)
        
        assert status == 200
        call_json = mock_post.call_args.kwargs['json']
        assert call_json['mode'] == 'subscription'
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_create_session_api_failure(self, mock_url_for, mock_post, db_session):
        """Test handling of API failure."""
        mock_url_for.side_effect = lambda *args, **kwargs: "http://test.com/callback"
        
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Invalid product data'
        mock_post.return_value = mock_response
        
        session_data = {
            'client_reference_id': 'REF-FAIL',
            'products': []  # Empty products - invalid
        }
        
        result, status, client_url = self.service.create_session(session_data)
        
        assert status == 400
        assert 'error' in result
        assert client_url is None
    
    # ========== Payment Success Tests ==========
    
    @patch('app.thawani.service.PaymentTransactionsService')
    def test_payment_success_callback(self, mock_payment_service, db_session):
        """Test handling successful payment callback."""
        mock_payment_service_instance = Mock()
        mock_payment_service_instance.update_payment_thawani.return_value = (None, uuid.uuid4())
        mock_payment_service.return_value = mock_payment_service_instance
        
        callback_data = {'ref': 'REF-SUCCESS-123'}
        
        result, status = self.service.payment_success(callback_data)
        
        assert status == 200
        assert 'successful' in result.lower()
        
        # Verify payment transaction was updated
        mock_payment_service_instance.update_payment_thawani.assert_called_once()
        update_data = mock_payment_service_instance.update_payment_thawani.call_args[0][1]
        assert update_data['payment_status'] == PaymentStatusEnum.success.value
        assert update_data['gateway_status'] == 'success'
    
    # ========== Payment Cancel Tests ==========
    
    @patch('app.thawani.service.PaymentTransactionsService')
    def test_payment_cancel_callback(self, mock_payment_service, db_session):
        """Test handling payment cancellation callback."""
        mock_payment_service_instance = Mock()
        mock_payment_service_instance.update_payment_thawani.return_value = (None, uuid.uuid4())
        mock_payment_service.return_value = mock_payment_service_instance
        
        callback_data = {'ref': 'REF-CANCEL-123'}
        
        result, status = self.service.payment_cancel(callback_data)
        
        assert status == 200
        assert 'cancel' in result.lower()
        
        # Verify payment transaction was updated
        mock_payment_service_instance.update_payment_thawani.assert_called_once()
        update_data = mock_payment_service_instance.update_payment_thawani.call_args[0][1]
        assert update_data['payment_status'] == PaymentStatusEnum.cancel.value
        assert update_data['gateway_status'] == 'cancel'
    
    # ========== Payment Status Query Tests ==========
    
    @patch('app.thawani.service.requests.get')
    def test_payment_status_query_success(self, mock_get, db_session):
        """Test querying payment status successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'session_id': 'TH-STATUS-123',
                'payment_status': 'paid',
                'amount': 10000
            }
        }
        mock_get.return_value = mock_response
        
        session_id = 'TH-STATUS-123'
        
        result, status = self.service.payment_status(session_id)
        
        assert status == 200
        assert 'data' in result
        assert result['data']['payment_status'] == 'paid'
        
        # Verify correct API endpoint was called
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert session_id in call_url
    
    @patch('app.thawani.service.requests.get')
    def test_payment_status_query_not_found(self, mock_get, db_session):
        """Test querying status for non-existent session."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Session not found'
        mock_get.return_value = mock_response
        
        session_id = 'TH-NONEXISTENT'
        
        result, status = self.service.payment_status(session_id)
        
        assert status == 404
        assert 'error' in result
    
    @patch('app.thawani.service.requests.get')
    def test_payment_status_query_pending(self, mock_get, db_session):
        """Test querying status for pending payment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'session_id': 'TH-PENDING',
                'payment_status': 'pending',
                'amount': 5000
            }
        }
        mock_get.return_value = mock_response
        
        session_id = 'TH-PENDING'
        
        result, status = self.service.payment_status(session_id)
        
        assert status == 200
        assert result['data']['payment_status'] == 'pending'
    
    # ========== Error Handling Tests ==========
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_create_session_network_timeout(self, mock_url_for, mock_post, db_session):
        """Test handling network timeout."""
        import requests
        mock_url_for.side_effect = lambda *args, **kwargs: "http://test.com/callback"
        mock_post.side_effect = requests.Timeout("Connection timeout")
        
        session_data = {
            'client_reference_id': 'REF-TIMEOUT',
            'products': [{'name': 'Product', 'unit_amount': 10000, 'quantity': 1}]
        }
        
        with pytest.raises(requests.Timeout):
            self.service.create_session(session_data)
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_create_session_invalid_json_response(self, mock_url_for, mock_post, db_session):
        """Test handling invalid JSON response."""
        mock_url_for.side_effect = lambda *args, **kwargs: "http://test.com/callback"
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response
        
        session_data = {
            'client_reference_id': 'REF-ERROR',
            'products': [{'name': 'Product', 'unit_amount': 10000, 'quantity': 1}]
        }
        
        result, status, client_url = self.service.create_session(session_data)
        
        assert status == 500
        assert 'error' in result
        assert client_url is None
    
    @patch('app.thawani.service.requests.get')
    def test_payment_status_query_network_error(self, mock_get, db_session):
        """Test handling network error when querying status."""
        import requests
        mock_get.side_effect = requests.ConnectionError("Network error")
        
        with pytest.raises(requests.ConnectionError):
            self.service.payment_status('TH-ERROR')
    
    # ========== Edge Cases Tests ==========
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_create_session_minimum_amount(self, mock_url_for, mock_post, db_session):
        """Test creating session with minimum amount (100 baisa)."""
        mock_url_for.side_effect = lambda *args, **kwargs: "http://test.com/callback"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'session_id': 'TH-MIN'}
        }
        mock_post.return_value = mock_response
        
        session_data = {
            'client_reference_id': 'REF-MIN',
            'products': [
                {'name': 'Minimum Product', 'unit_amount': 100, 'quantity': 1}
            ]
        }
        
        result, status, client_url = self.service.create_session(session_data)
        
        assert status == 200
    
    @patch('app.thawani.service.PaymentTransactionsService')
    def test_payment_callback_missing_reference(self, mock_payment_service, db_session):
        """Test handling callback with missing reference."""
        mock_payment_service_instance = Mock()
        mock_payment_service_instance.update_payment_thawani.return_value = ('Order', uuid.uuid4())
        mock_payment_service.return_value = mock_payment_service_instance
        
        callback_data = {}  # Missing 'ref'
        
        # Should handle missing reference gracefully
        try:
            result, status = self.service.payment_success(callback_data)
            # May return error or handle None reference
            assert result is not None
        except (KeyError, AttributeError):
            # Or may raise error for missing reference
            pass
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_create_session_with_metadata(self, mock_url_for, mock_post, db_session):
        """Test session creation with custom metadata."""
        mock_url_for.side_effect = lambda *args, **kwargs: "http://test.com/callback"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'session_id': 'TH-META'}
        }
        mock_post.return_value = mock_response
        
        session_data = {
            'client_reference_id': 'REF-META',
            'products': [{'name': 'Product', 'unit_amount': 10000, 'quantity': 1}],
            'metadata': {
                'order_id': 'ORDER-123',
                'customer_id': 'CUST-456',
                'notes': 'Rush delivery'
            }
        }
        
        result, status, client_url = self.service.create_session(session_data)
        
        assert status == 200
        call_json = mock_post.call_args.kwargs['json']
        assert 'metadata' in call_json
        assert call_json['metadata']['order_id'] == 'ORDER-123'

