"""
Unit tests for Payment Service.

Tests all business logic in payment/service.py including:
- Payment CRUD operations
- Payment filtering and pagination
- Payment by invoice queries
- Amount calculations
- Edge cases and error handling
"""

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import (
    assert_decimal_equal,
    assert_datetime_close,
    create_mock_filter,
    assert_pagination_structure
)
from app.payment.service import PaymentService
from app.payment.model import Payment
from app.invoices.model import Invoice
from app.common.error_handling import ResourceNotFoundError


class TestPaymentService(BaseServiceTestCase):
    """Test cases for PaymentService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = PaymentService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_payment_success(self, db_session, sample_invoice):
        """Test creating a payment successfully."""
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'credit_card',
            'amount_paid': 100.00,
            'payment_date': '2024-01-15'
        }
        
        result, status = self.service.create_payment(payment_data)
        
        assert status == 201
        assert result == 'Payment Created'
        
        # Verify payment was created in database
        payment = db_session.query(Payment).filter(
            Payment.invoice_id == sample_invoice.id
        ).first()
        assert payment is not None
        assert_decimal_equal(payment.amount_paid, 100.00)
        assert payment.payment_method == 'credit_card'
    
    def test_create_payment_with_different_methods(self, db_session, sample_invoice):
        """Test creating payments with different payment methods."""
        methods = ['cash', 'bank_transfer', 'online', 'check']
        
        for method in methods:
            payment_data = {
                'invoice_id': sample_invoice.id,
                'payment_method': method,
                'amount_paid': 50.00,
                'payment_date': '2024-01-15'
            }
            
            result, status = self.service.create_payment(payment_data)
            assert status == 201
    
    def test_get_payments_with_pagination(self, db_session, sample_invoice):
        """Test getting payments with pagination."""
        # Create multiple payments
        for i in range(15):
            payment_data = {
                'invoice_id': sample_invoice.id,
                'payment_method': 'cash',
                'amount_paid': 10.00 * (i + 1),
                'payment_date': '2024-01-15'
            }
            self.service.create_payment(payment_data)
        
        # Test pagination
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_payments(None, filter_obj)
        
        assert status == 200
        assert 'payments' in result
        assert 'filters' in result
        assert len(result['payments']) == 10
    
    def test_get_payment_by_id(self, db_session, sample_invoice):
        """Test getting a specific payment by ID."""
        # Create a payment
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'credit_card',
            'amount_paid': 150.00,
            'payment_date': '2024-01-15'
        }
        self.service.create_payment(payment_data)
        
        # Get the payment
        payment = db_session.query(Payment).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_payments(payment.id, filter_obj)
        
        assert status == 200
        assert 'payments' in result
        payment_data = result['payments']
        assert payment_data['payment']['id'] == str(payment.id)
    
    def test_get_payment_by_id_not_found(self, db_session):
        """Test getting a non-existent payment."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            self.service.get_payments(non_existent_id, filter_obj)
        
        assert "Payment" in str(exc_info.value)
    
    def test_get_payments_by_invoice_id(self, db_session, sample_invoice):
        """Test getting all payments for a specific invoice."""
        # Create multiple payments for the same invoice
        for i in range(3):
            payment_data = {
                'invoice_id': sample_invoice.id,
                'payment_method': 'cash',
                'amount_paid': 50.00 * (i + 1),
                'payment_date': '2024-01-15'
            }
            self.service.create_payment(payment_data)
        
        result, status = self.service.get_payment_by_invoice_id(sample_invoice.id)
        
        assert status == 200
        assert len(result) == 3
        # Verify all payments are for the correct invoice
        for payment in result:
            assert payment['invoice']['id'] == str(sample_invoice.id)
    
    def test_update_payment_success(self, db_session, sample_invoice):
        """Test updating a payment."""
        # Create a payment
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'cash',
            'amount_paid': 100.00,
            'payment_date': '2024-01-15'
        }
        self.service.create_payment(payment_data)
        
        payment = db_session.query(Payment).first()
        
        # Update the payment
        update_data = {
            'payment_method': 'credit_card',
            'amount_paid': 150.00
        }
        
        result, status = self.service.update_payment(payment.id, update_data, None)
        
        assert status == 200
        assert result == 'Updated'
        
        # Verify updates
        db_session.refresh(payment)
        assert payment.payment_method == 'credit_card'
        assert_decimal_equal(payment.amount_paid, 150.00)
    
    def test_update_payment_not_found(self, db_session):
        """Test updating a non-existent payment."""
        non_existent_id = uuid.uuid4()
        update_data = {'amount_paid': 200.00}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_payment(non_existent_id, update_data, None)
    
    def test_delete_payment_success(self, db_session, sample_invoice):
        """Test deleting a payment."""
        # Create a payment
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'cash',
            'amount_paid': 100.00,
            'payment_date': '2024-01-15'
        }
        self.service.create_payment(payment_data)
        
        payment = db_session.query(Payment).first()
        payment_id = payment.id
        
        # Delete the payment
        result, status = self.service.delete_payment(payment_id)
        
        assert status == 200
        assert result == 'Payment deleted'
        
        # Verify deletion
        deleted_payment = db_session.query(Payment).filter_by(id=payment_id).first()
        assert deleted_payment is None
    
    def test_delete_payment_not_found(self, db_session):
        """Test deleting a non-existent payment."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_payment(non_existent_id)
    
    # ========== Amount Calculations Tests ==========
    
    def test_get_total_payments_amount(self, db_session, sample_invoice):
        """Test calculating total payments amount."""
        # Create multiple payments
        amounts = [100.00, 250.50, 75.25, 50.00]
        for amount in amounts:
            payment_data = {
                'invoice_id': sample_invoice.id,
                'payment_method': 'cash',
                'amount_paid': amount,
                'payment_date': '2024-01-15'
            }
            self.service.create_payment(payment_data)
        
        result, status = self.service.get_total_payments_amount()
        
        assert status == 200
        assert 'total_payments_amount' in result
        expected_total = sum(amounts)
        assert_decimal_equal(result['total_payments_amount'], expected_total)
    
    def test_get_total_payments_amount_no_payments(self, db_session):
        """Test total amount when no payments exist."""
        result, status = self.service.get_total_payments_amount()
        
        assert status == 200
        assert result['total_payments_amount'] == 0.0
    
    # ========== Edge Cases Tests ==========
    
    def test_create_payment_with_zero_amount(self, db_session, sample_invoice):
        """Test creating a payment with zero amount."""
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'cash',
            'amount_paid': 0.00,
            'payment_date': '2024-01-15'
        }
        
        result, status = self.service.create_payment(payment_data)
        
        assert status == 201
        payment = db_session.query(Payment).first()
        assert payment.amount_paid == 0.00
    
    def test_create_payment_with_large_amount(self, db_session, sample_invoice):
        """Test creating a payment with very large amount."""
        large_amount = 9999999.99
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'bank_transfer',
            'amount_paid': large_amount,
            'payment_date': '2024-01-15'
        }
        
        result, status = self.service.create_payment(payment_data)
        
        assert status == 201
        payment = db_session.query(Payment).first()
        assert_decimal_equal(payment.amount_paid, large_amount)
    
    def test_create_payment_with_decimal_precision(self, db_session, sample_invoice):
        """Test payment amount with high decimal precision."""
        precise_amount = 123.4567
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'credit_card',
            'amount_paid': precise_amount,
            'payment_date': '2024-01-15'
        }
        
        result, status = self.service.create_payment(payment_data)
        
        assert status == 201
        payment = db_session.query(Payment).first()
        # Should store with precision
        assert float(payment.amount_paid) == pytest.approx(precise_amount, rel=0.0001)
    
    def test_get_payments_empty_database(self, db_session):
        """Test getting payments when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_payments(None, filter_obj)
        
        assert status == 200
        assert 'payments' in result
        assert len(result['payments']) == 0
    
    def test_get_payment_model_with_null_invoice(self, db_session, sample_invoice):
        """Test payment model when invoice relationship is null."""
        # Create payment
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'cash',
            'amount_paid': 100.00,
            'payment_date': '2024-01-15'
        }
        self.service.create_payment(payment_data)
        
        payment = db_session.query(Payment).first()
        
        # Test with single payment
        model = self.service.get_payment_model(payment)
        assert 'payment' in model
        
        # Test with list of payments
        models = self.service.get_payment_model([payment])
        assert isinstance(models, list)
        assert len(models) > 0
    
    def test_update_payment_partial_data(self, db_session, sample_invoice):
        """Test updating only some fields of a payment."""
        # Create payment
        payment_data = {
            'invoice_id': sample_invoice.id,
            'payment_method': 'cash',
            'amount_paid': 100.00,
            'payment_date': '2024-01-15'
        }
        self.service.create_payment(payment_data)
        
        payment = db_session.query(Payment).first()
        original_method = payment.payment_method
        
        # Update only amount
        update_data = {'amount_paid': 200.00}
        self.service.update_payment(payment.id, update_data, None)
        
        db_session.refresh(payment)
        assert_decimal_equal(payment.amount_paid, 200.00)
        assert payment.payment_method == original_method  # Should not change
    
    def test_multiple_payments_same_invoice(self, db_session, sample_invoice):
        """Test creating multiple partial payments for same invoice."""
        # Scenario: Invoice total is 300, paid in 3 installments
        amounts = [100.00, 100.00, 100.00]
        
        for amount in amounts:
            payment_data = {
                'invoice_id': sample_invoice.id,
                'payment_method': 'cash',
                'amount_paid': amount,
                'payment_date': '2024-01-15'
            }
            result, status = self.service.create_payment(payment_data)
            assert status == 201
        
        # Verify all payments were created
        payments = self.service.get_payment_by_invoice_id(sample_invoice.id)
        assert len(payments[0]) == 3
    
    def test_payment_dates_chronological_order(self, db_session, sample_invoice):
        """Test payments can be created with different dates."""
        dates = ['2024-01-01', '2024-01-15', '2024-02-01']
        
        for date in dates:
            payment_data = {
                'invoice_id': sample_invoice.id,
                'payment_method': 'cash',
                'amount_paid': 50.00,
                'payment_date': date
            }
            result, status = self.service.create_payment(payment_data)
            assert status == 201
        
        # Verify payments exist with different dates
        payments_result = self.service.get_payment_by_invoice_id(sample_invoice.id)
        assert len(payments_result[0]) == 3
    
    # ========== Pagination and Filtering Tests ==========
    
    def test_get_payments_with_sorting(self, db_session, sample_invoice):
        """Test getting payments with sorting."""
        # Create payments with different amounts
        for amount in [50, 150, 100, 200]:
            payment_data = {
                'invoice_id': sample_invoice.id,
                'payment_method': 'cash',
                'amount_paid': float(amount),
                'payment_date': '2024-01-15'
            }
            self.service.create_payment(payment_data)
        
        # Test with sorting
        from app.common.queries import create_sorters
        filter_obj = create_mock_filter()
        filter_obj.sorters = create_sorters('amount_paid', 'asc')
        
        result, status = self.service.get_payments(None, filter_obj)
        
        assert status == 200
        assert 'payments' in result
    
    def test_get_payments_different_page_sizes(self, db_session, sample_invoice):
        """Test pagination with different page sizes."""
        # Create 25 payments
        for i in range(25):
            payment_data = {
                'invoice_id': sample_invoice.id,
                'payment_method': 'cash',
                'amount_paid': 10.00,
                'payment_date': '2024-01-15'
            }
            self.service.create_payment(payment_data)
        
        # Test different page sizes
        for per_page in [5, 10, 20]:
            filter_obj = create_mock_filter(page=1, per_page=per_page)
            result, status = self.service.get_payments(None, filter_obj)
            
            assert status == 200
            assert len(result['payments']) == min(per_page, 25)
    
    # ========== Error Handling Tests ==========
    
    def test_create_payment_missing_required_fields(self, db_session):
        """Test creating payment with missing required fields."""
        incomplete_data = {
            'payment_method': 'cash',
            'amount_paid': 100.00
            # Missing invoice_id and payment_date
        }
        
        with pytest.raises(Exception):  # Should raise KeyError or similar
            self.service.create_payment(incomplete_data)
    
    def test_create_payment_invalid_invoice_id(self, db_session):
        """Test creating payment with non-existent invoice."""
        payment_data = {
            'invoice_id': uuid.uuid4(),  # Non-existent invoice
            'payment_method': 'cash',
            'amount_paid': 100.00,
            'payment_date': '2024-01-15'
        }
        
        # Should handle foreign key constraint
        with pytest.raises(Exception):
            self.service.create_payment(payment_data)

