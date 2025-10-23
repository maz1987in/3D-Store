"""
Unit tests for Payment Transaction Service.

Tests all business logic in payment_transaction/service.py including:
- Transaction creation and logging
- Gateway transaction tracking and reconciliation
- Transaction status updates and webhooks
- Payment gateway configuration management
- Model-based polymorphic associations
- Edge cases and error handling
"""

import pytest
import uuid
from decimal import Decimal
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.payment_transaction.service import PaymentTransactionsService
from app.payment_transaction.model import PaymentTransaction, PaymentGateway, PaymentType, PaymentConfig
from app.common.enum import PaymentStatusEnum
from app.common.error_handling import ResourceNotFoundError


class TestPaymentTransactionService(BaseServiceTestCase):
    """Test cases for PaymentTransactionsService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = PaymentTransactionsService()
    
    # ========== Payment Transaction CRUD Tests ==========
    
    def test_create_payment_transaction_success(self, db_session, sample_user):
        """Test creating a payment transaction successfully."""
        transaction_data = {
            'requester': sample_user.id,
            'reference_id': 'REF-12345-TEST',
            'payment_status': PaymentStatusEnum.PENDING.value,
            'amount': 100.50,
            'vat': 15.00,
            'model_type': 'order',
            'model_id': str(uuid.uuid4()),
            'model_action': 'payment',
            'payment_gateway': 'Thawani',
            'payment_type': 'Online'
        }
        
        result, status = self.service.create_payment_transaction(transaction_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify transaction was created
        transaction = db_session.query(PaymentTransaction).filter(
            PaymentTransaction.reference_id == 'REF-12345-TEST'
        ).first()
        assert transaction is not None
        assert transaction.amount == 100.50
        assert transaction.vat == 15.00
        assert transaction.payment_status == PaymentStatusEnum.PENDING
    
    def test_get_all_payment_transactions_with_pagination(self, db_session, sample_user):
        """Test getting payment transactions with pagination."""
        # Create multiple transactions
        for i in range(15):
            transaction_data = {
                'requester': sample_user.id,
                'reference_id': f'REF-{i}-TEST',
                'payment_status': PaymentStatusEnum.SUCCESS.value,
                'amount': 50.00 + i,
                'vat': 7.50,
                'model_type': 'order',
                'model_action': 'payment',
                'payment_gateway': 'Thawani',
                'payment_type': 'Online'
            }
            self.service.create_payment_transaction(transaction_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_all_payment_transactions(None, filter_obj)
        
        assert status == 200
        assert 'payments' in result
        assert 'filters' in result
    
    def test_get_payment_transaction_by_id(self, db_session, sample_user):
        """Test getting a specific transaction by ID."""
        transaction_data = {
            'requester': sample_user.id,
            'reference_id': 'REF-SPECIFIC-TEST',
            'payment_status': PaymentStatusEnum.SUCCESS.value,
            'amount': 200.00,
            'vat': 30.00,
            'model_type': 'order',
            'model_action': 'payment',
            'payment_gateway': 'Ompay',
            'payment_type': 'Card'
        }
        self.service.create_payment_transaction(transaction_data)
        
        transaction = db_session.query(PaymentTransaction).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_all_payment_transactions(transaction.id, filter_obj)
        
        assert status == 200
        assert 'payments' in result
    
    def test_update_payment_transaction_status(self, db_session, sample_user):
        """Test updating transaction status."""
        # Create transaction with PENDING status
        transaction_data = {
            'requester': sample_user.id,
            'reference_id': 'REF-UPDATE-STATUS',
            'payment_status': PaymentStatusEnum.PENDING.value,
            'amount': 150.00,
            'vat': 22.50,
            'model_type': 'order',
            'model_action': 'payment',
            'payment_gateway': 'Thawani',
            'payment_type': 'Online'
        }
        self.service.create_payment_transaction(transaction_data)
        
        transaction = db_session.query(PaymentTransaction).first()
        
        # Update to SUCCESS
        update_data = {
            'payment_status': PaymentStatusEnum.SUCCESS.value,
            'gateway_transaction_id': 'GW-TX-123456',
            'gateway_status': 'completed'
        }
        
        result, status = self.service.update_payment_transaction(transaction.id, update_data)
        
        assert status == 200
        
        db_session.refresh(transaction)
        assert transaction.payment_status == PaymentStatusEnum.SUCCESS
        assert transaction.gateway_transaction_id == 'GW-TX-123456'
    
    # ========== Gateway Management Tests ==========
    
    def test_get_payment_gateways(self, db_session):
        """Test getting all payment gateways."""
        # Create gateways
        gateway1 = PaymentGateway(name='Thawani')
        gateway2 = PaymentGateway(name='Ompay')
        db_session.add(gateway1)
        db_session.add(gateway2)
        db_session.commit()
        
        result, status = self.service.get_gateways()
        
        assert status == 200
        assert len(result) >= 2
        gateway_names = [g['name'] for g in result]
        assert 'Thawani' in gateway_names
        assert 'Ompay' in gateway_names
    
    def test_create_payment_gateway(self, db_session):
        """Test creating a new payment gateway."""
        gateway_data = {'name': 'NewGateway'}
        
        result, status = self.service.create_payment_gateway(gateway_data)
        
        assert status == 201
        assert 'Created' in result
        
        gateway = db_session.query(PaymentGateway).filter_by(name='NewGateway').first()
        assert gateway is not None
    
    def test_delete_payment_gateway(self, db_session):
        """Test deleting a payment gateway."""
        gateway = PaymentGateway(name='DeleteMe')
        db_session.add(gateway)
        db_session.commit()
        
        result, status = self.service.delete_payment_gateway('DeleteMe')
        
        assert status == 200
        assert 'Deleted' in result
        
        deleted_gateway = db_session.query(PaymentGateway).filter_by(name='DeleteMe').first()
        assert deleted_gateway is None
    
    # ========== Transaction Status Tests ==========
    
    def test_transaction_status_transitions(self, db_session, sample_user):
        """Test transaction status state transitions."""
        statuses = [
            PaymentStatusEnum.PENDING,
            PaymentStatusEnum.SUCCESS,
            PaymentStatusEnum.FAILED,
            PaymentStatusEnum.REFUNDED
        ]
        
        for status_enum in statuses:
            transaction_data = {
                'requester': sample_user.id,
                'reference_id': f'REF-{status_enum.value}-TEST',
                'payment_status': status_enum.value,
                'amount': 100.00,
                'vat': 15.00,
                'model_type': 'order',
                'model_action': 'payment',
                'payment_gateway': 'Thawani',
                'payment_type': 'Online'
            }
            result, status_code = self.service.create_payment_transaction(transaction_data)
            assert status_code == 201
        
        # Verify all statuses were created
        transactions = db_session.query(PaymentTransaction).all()
        transaction_statuses = [t.payment_status for t in transactions]
        assert set(transaction_statuses) >= set(statuses)
    
    # ========== Reference ID Uniqueness Tests ==========
    
    def test_duplicate_reference_id_validation(self, db_session, sample_user):
        """Test that reference IDs must be unique."""
        transaction_data = {
            'requester': sample_user.id,
            'reference_id': 'REF-UNIQUE-TEST',
            'payment_status': PaymentStatusEnum.PENDING.value,
            'amount': 100.00,
            'vat': 15.00,
            'model_type': 'order',
            'model_action': 'payment',
            'payment_gateway': 'Thawani',
            'payment_type': 'Online'
        }
        
        # Create first transaction
        result1, status1 = self.service.create_payment_transaction(transaction_data)
        assert status1 == 201
        
        # Try to create duplicate reference_id
        with pytest.raises(Exception):  # Unique constraint violation
            self.service.create_payment_transaction(transaction_data)
    
    # ========== Amount and VAT Tests ==========
    
    def test_transaction_with_zero_vat(self, db_session, sample_user):
        """Test transaction with zero VAT."""
        transaction_data = {
            'requester': sample_user.id,
            'reference_id': 'REF-ZERO-VAT',
            'payment_status': PaymentStatusEnum.SUCCESS.value,
            'amount': 100.00,
            'vat': 0.00,
            'model_type': 'order',
            'model_action': 'payment',
            'payment_gateway': 'Thawani',
            'payment_type': 'Online'
        }
        
        result, status = self.service.create_payment_transaction(transaction_data)
        
        assert status == 201
        
        transaction = db_session.query(PaymentTransaction).filter(
            PaymentTransaction.reference_id == 'REF-ZERO-VAT'
        ).first()
        assert transaction.vat == 0.00
    
    def test_transaction_amount_calculations(self, db_session, sample_user):
        """Test transaction amount with VAT calculations."""
        base_amount = 100.00
        vat = 15.00
        
        transaction_data = {
            'requester': sample_user.id,
            'reference_id': 'REF-CALC-TEST',
            'payment_status': PaymentStatusEnum.SUCCESS.value,
            'amount': base_amount,
            'vat': vat,
            'model_type': 'order',
            'model_action': 'payment',
            'payment_gateway': 'Ompay',
            'payment_type': 'Card'
        }
        
        result, status = self.service.create_payment_transaction(transaction_data)
        assert status == 201
        
        transaction = db_session.query(PaymentTransaction).filter(
            PaymentTransaction.reference_id == 'REF-CALC-TEST'
        ).first()
        
        total = transaction.amount + transaction.vat
        assert total == 115.00
    
    # ========== Polymorphic Model Association Tests ==========
    
    def test_transaction_model_associations(self, db_session, sample_user):
        """Test polymorphic model associations (order, quotation, etc.)."""
        model_types = ['order', 'quotation', 'invoice', 'refund']
        
        for i, model_type in enumerate(model_types):
            transaction_data = {
                'requester': sample_user.id,
                'reference_id': f'REF-{model_type.upper()}-{i}',
                'payment_status': PaymentStatusEnum.SUCCESS.value,
                'amount': 100.00,
                'vat': 15.00,
                'model_type': model_type,
                'model_id': str(uuid.uuid4()),
                'model_action': 'payment',
                'payment_gateway': 'Thawani',
                'payment_type': 'Online'
            }
            result, status = self.service.create_payment_transaction(transaction_data)
            assert status == 201
        
        # Verify all model types created
        transactions = db_session.query(PaymentTransaction).all()
        transaction_model_types = [t.model_type for t in transactions]
        assert set(transaction_model_types) >= set(model_types)
    
    # ========== Error Handling Tests ==========
    
    def test_create_transaction_invalid_user(self, db_session):
        """Test creating transaction with non-existent user."""
        transaction_data = {
            'requester': uuid.uuid4(),  # Non-existent user
            'reference_id': 'REF-INVALID-USER',
            'payment_status': PaymentStatusEnum.PENDING.value,
            'amount': 100.00,
            'vat': 15.00,
            'model_type': 'order',
            'model_action': 'payment',
            'payment_gateway': 'Thawani',
            'payment_type': 'Online'
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_payment_transaction(transaction_data)
    
    def test_update_transaction_not_found(self, db_session):
        """Test updating a non-existent transaction."""
        non_existent_id = uuid.uuid4()
        update_data = {
            'payment_status': PaymentStatusEnum.SUCCESS.value
        }
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_payment_transaction(non_existent_id, update_data)
    
    def test_get_transaction_not_found(self, db_session):
        """Test getting a non-existent transaction."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_all_payment_transactions(non_existent_id, filter_obj)
        
        # Should return empty result instead of error
        assert status == 200
        assert 'payments' in result
    
    def test_get_transactions_empty_database(self, db_session):
        """Test getting transactions when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_all_payment_transactions(None, filter_obj)
        
        assert status == 200
        assert 'payments' in result

