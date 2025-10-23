"""
Integration tests for Payment Workflows.

Tests complete payment processing workflows:
1. Order creation with payment requirement
2. Gateway integration (Ompay/Thawani) transaction
3. Payment confirmation and order update
4. Refund processing and inventory return
5. Partial payment scenarios
6. Payment failure handling and retry logic
"""

import pytest
import uuid
from datetime import datetime, date, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseIntegrationTestCase
from app.order.service import OrderService
from app.payment.service import PaymentService
from app.payment_transaction.service import PaymentTransactionsService
from app.ompay.service import OMPayService
from app.thawani.service import ThawaniService
from app.common.enum import OrderStatusEnum, PaymentStatusEnum


class TestPaymentWorkflows(BaseIntegrationTestCase):
    """Test complete payment processing workflows."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.order_service = OrderService()
        self.payment_service = PaymentService()
        self.payment_transaction_service = PaymentTransactionsService()
        self.ompay_service = OMPayService()
        self.thawani_service = ThawaniService()
    
    # ========== Complete Payment Workflows ==========
    
    def test_order_to_payment_workflow(self, db_session, sample_supplier, sample_user):
        """Test complete order creation to payment confirmation."""
        
        # Step 1: Create order
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 150.00,
            'supplier_id': sample_supplier.id,
            'notes': 'Payment workflow test'
        }
        
        order_result, order_status = self.order_service.create_order(order_data)
        assert order_status == 201
        
        from app.order.model import Order
        order = db_session.query(Order).first()
        
        # Step 2: Create payment transaction
        transaction_data = {
            'requester': sample_user.id,
            'reference_id': f'REF-ORDER-{order.id}',
            'payment_status': PaymentStatusEnum.PENDING.value,
            'amount': 150.00,
            'vat': 22.50,
            'model_type': 'order',
            'model_id': str(order.id),
            'model_action': 'payment',
            'payment_gateway': 'Thawani',
            'payment_type': 'Online'
        }
        
        trans_result, trans_status = self.payment_transaction_service.create_payment_transaction(
            transaction_data
        )
        assert trans_status == 201
        
        # Step 3: Confirm payment
        from app.payment_transaction.model import PaymentTransaction
        payment_tx = db_session.query(PaymentTransaction).first()
        
        confirm_data = {
            'payment_status': PaymentStatusEnum.SUCCESS.value,
            'gateway_transaction_id': 'GW-TX-123456'
        }
        
        confirm_result, confirm_status = self.payment_transaction_service.update_payment_transaction(
            payment_tx.id, confirm_data
        )
        assert confirm_status == 200
        
        # Step 4: Update order status
        update_data = {'status': OrderStatusEnum.PROCESSING.value}
        order_update, order_update_status = self.order_service.update_order(order.id, update_data)
        assert order_update_status == 200
        
        # Verify final state
        db_session.refresh(order)
        db_session.refresh(payment_tx)
        assert order.status == OrderStatusEnum.PROCESSING
        assert payment_tx.payment_status == PaymentStatusEnum.SUCCESS
    
    @patch('app.ompay.service.requests.post')
    def test_ompay_payment_workflow(self, mock_post, db_session, sample_supplier):
        """Test payment workflow through Ompay gateway."""
        
        # Mock successful gateway response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'orderId': 'OM-TEST-123',
            'checkoutUrl': 'https://checkout.ompay.om/pay/OM-TEST-123',
            'status': 'created'
        }
        mock_post.return_value = mock_response
        
        # Create session with Ompay
        session_data = {
            'amount': 100.50,
            'description': 'Test Payment',
            'email': 'customer@test.com',
            'phone': '+96812345678',
            'name': 'Test Customer'
        }
        
        result, status = self.ompay_service.create_session(session_data)
        
        assert status == 200
        assert 'orderId' in result
    
    @patch('app.thawani.service.requests.post')
    @patch('app.thawani.service.url_for')
    def test_thawani_payment_workflow(self, mock_url_for, mock_post, db_session):
        """Test payment workflow through Thawani gateway."""
        
        # Mock URL generation
        mock_url_for.side_effect = lambda *args, **kwargs: f"http://test.com/callback"
        
        # Mock successful gateway response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'session_id': 'TH-TEST-456',
                'status': 'created'
            }
        }
        mock_post.return_value = mock_response
        
        # Create session with Thawani
        session_data = {
            'client_reference_id': 'REF-TEST-123',
            'products': [
                {'name': 'Product 1', 'unit_amount': 10000, 'quantity': 1}
            ]
        }
        
        result, status, client_url = self.thawani_service.create_session(session_data)
        
        assert status == 200
        assert result['data']['session_id'] == 'TH-TEST-456'
        assert client_url is not None
    
    def test_payment_failure_and_retry(self, db_session, sample_supplier, sample_user):
        """Test payment failure and retry workflow."""
        
        # Create order
        order_data = {
            'order_date': date.today().strftime('%Y-%m-%d'),
            'status': OrderStatusEnum.PENDING.value,
            'total_amount': 100.00,
            'supplier_id': sample_supplier.id
        }
        
        order_result, order_status = self.order_service.create_order(order_data)
        assert order_status == 201
        
        from app.order.model import Order
        order = db_session.query(Order).first()
        
        # Create failed payment transaction
        transaction_data = {
            'requester': sample_user.id,
            'reference_id': f'REF-FAIL-{order.id}',
            'payment_status': PaymentStatusEnum.FAILED.value,
            'amount': 100.00,
            'vat': 15.00,
            'model_type': 'order',
            'model_id': str(order.id),
            'model_action': 'payment',
            'payment_gateway': 'Thawani',
            'payment_type': 'Online'
        }
        
        trans_result, trans_status = self.payment_transaction_service.create_payment_transaction(
            transaction_data
        )
        assert trans_status == 201
        
        # Retry payment with new transaction
        retry_transaction_data = {
            'requester': sample_user.id,
            'reference_id': f'REF-RETRY-{order.id}',
            'payment_status': PaymentStatusEnum.SUCCESS.value,
            'amount': 100.00,
            'vat': 15.00,
            'model_type': 'order',
            'model_id': str(order.id),
            'model_action': 'payment',
            'payment_gateway': 'Ompay',
            'payment_type': 'Online'
        }
        
        retry_result, retry_status = self.payment_transaction_service.create_payment_transaction(
            retry_transaction_data
        )
        assert retry_status == 201
        
        # Verify both transactions exist
        from app.payment_transaction.model import PaymentTransaction
        transactions = db_session.query(PaymentTransaction).filter(
            PaymentTransaction.model_id == str(order.id)
        ).all()
        
        assert len(transactions) == 2
        statuses = [t.payment_status for t in transactions]
        assert PaymentStatusEnum.FAILED in statuses
        assert PaymentStatusEnum.SUCCESS in statuses

