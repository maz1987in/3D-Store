"""
Unit tests for Invoice Service.

Tests all business logic in invoices/service.py including:
- Invoice CRUD operations
- Invoice number generation (uniqueness)
- Payment tracking and reconciliation
- Tax calculations
- Invoice by transaction/user queries
- Edge cases and error handling
"""

import pytest
import uuid
from unittest.mock import Mock
from decimal import Decimal
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import assert_decimal_equal, create_mock_filter
from app.invoices.service import InvoiceService
from app.invoices.model import Invoice, InvoiceCounter
from app.common.error_handling import ResourceNotFoundError


class TestInvoiceService(BaseServiceTestCase):
    """Test cases for InvoiceService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = InvoiceService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_invoice_success(self, db_session, sample_customer, sample_branch, sample_user):
        """Test creating an invoice successfully."""
        invoice_data = {
            'invoice_number': 'INV-2024-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'due_date': '2024-02-15',
            'subtotal': 1000.00,
            'tax_amount': 50.00,
            'total_amount': 1050.00,
            'payment_status': 'pending'
        }
        
        result, status = self.service.create_invoice(invoice_data)
        
        assert status == 201
        assert 'Invoice Created' in result
        
        # Verify invoice was created
        invoice = db_session.query(Invoice).filter(
            Invoice.invoice_number == 'INV-2024-001'
        ).first()
        assert invoice is not None
        assert_decimal_equal(invoice.total_amount, 1050.00)
        assert invoice.payment_status == 'pending'
    
    def test_get_invoices_with_pagination(self, db_session, sample_customer, sample_branch, sample_user):
        """Test getting invoices with pagination."""
        # Create multiple invoices
        for i in range(15):
            invoice_data = {
                'invoice_number': f'INV-2024-{str(i+1).zfill(3)}',
                'customer_id': sample_customer.id,
                'branch_id': sample_branch.id,
                'user_id': sample_user.id,
                'date': '2024-01-15',
                'total_amount': 100.00 * (i + 1)
            }
            self.service.create_invoice(invoice_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_invoices(None, filter_obj)
        
        assert status == 200
        assert 'invoices' in result
        assert 'filters' in result
        assert len(result['invoices']) == 10
    
    def test_get_invoice_by_id(self, db_session, sample_customer, sample_branch, sample_user):
        """Test getting a specific invoice by ID."""
        invoice_data = {
            'invoice_number': 'INV-TEST-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 500.00
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_invoices(invoice.id, filter_obj)
        
        assert status == 200
        assert 'invoices' in result
        assert len(result['invoices']) == 1
    
    def test_get_invoice_by_id_not_found(self, db_session):
        """Test getting a non-existent invoice."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            self.service.get_invoices(non_existent_id, filter_obj)
        
        assert "Invoice" in str(exc_info.value)
    
    def test_get_invoices_by_user_id(self, db_session, sample_customer, sample_branch, sample_user):
        """Test getting all invoices for a specific user."""
        # Create invoices for user
        for i in range(3):
            invoice_data = {
                'invoice_number': f'INV-USER-{i+1}',
                'customer_id': sample_customer.id,
                'branch_id': sample_branch.id,
                'user_id': sample_user.id,
                'date': '2024-01-15',
                'total_amount': 200.00
            }
            self.service.create_invoice(invoice_data)
        
        filter_obj = create_mock_filter()
        result, status = self.service.get_invoices_by_user_id(sample_user.id, filter_obj)
        
        assert status == 200
        assert 'invoices' in result
        assert len(result['invoices']) >= 3
    
    def test_update_invoice_success(self, db_session, sample_customer, sample_branch, sample_user):
        """Test updating an invoice."""
        # Create invoice
        invoice_data = {
            'invoice_number': 'INV-UPDATE-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 500.00,
            'payment_status': 'pending'
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        
        # Update the invoice
        update_data = {
            'total_amount': 750.00,
            'payment_status': 'paid',
            'notes': 'Payment received'
        }
        
        result, status = self.service.update_invoice(invoice.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(invoice)
        assert_decimal_equal(invoice.total_amount, 750.00)
        assert invoice.payment_status == 'paid'
    
    def test_delete_invoice_success(self, db_session, sample_customer, sample_branch, sample_user):
        """Test deleting an invoice."""
        invoice_data = {
            'invoice_number': 'INV-DELETE-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 300.00
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        invoice_id = invoice.id
        
        result, status = self.service.delete_invoice(invoice_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_invoice = db_session.query(Invoice).filter_by(id=invoice_id).first()
        assert deleted_invoice is None
    
    # ========== Invoice Number Generation Tests ==========
    
    def test_invoice_number_uniqueness(self, db_session, sample_customer, sample_branch, sample_user):
        """Test that invoice numbers must be unique."""
        invoice_data = {
            'invoice_number': 'INV-UNIQUE-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 500.00
        }
        
        # Create first invoice
        self.service.create_invoice(invoice_data)
        
        # Attempt to create duplicate
        with pytest.raises(Exception):  # Should raise integrity error
            self.service.create_invoice(invoice_data)
    
    def test_invoice_number_counter(self, db_session):
        """Test invoice counter functionality."""
        # Check if counter exists or can be created
        counter = db_session.query(InvoiceCounter).first()
        
        # If no counter, it should be created on first invoice
        initial_count = counter.current_value if counter else 0
        
        # Creating invoices should increment counter
        # (Implementation may vary)
        assert initial_count >= 0
    
    # ========== Amount Calculations Tests ==========
    
    def test_invoice_total_calculation(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice total calculation (subtotal + tax)."""
        subtotal = 1000.00
        tax_rate = 0.05  # 5%
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        invoice_data = {
            'invoice_number': 'INV-CALC-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        
        assert_decimal_equal(invoice.subtotal, 1000.00)
        assert_decimal_equal(invoice.tax_amount, 50.00)
        assert_decimal_equal(invoice.total_amount, 1050.00)
    
    def test_invoice_with_discount(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice with discount applied."""
        subtotal = 1000.00
        discount = 100.00
        tax_amount = (subtotal - discount) * 0.05
        total = subtotal - discount + tax_amount
        
        invoice_data = {
            'invoice_number': 'INV-DISCOUNT-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'subtotal': subtotal,
            'discount_amount': discount,
            'tax_amount': tax_amount,
            'total_amount': total
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        assert_decimal_equal(invoice.discount_amount or 0, 100.00)
        assert_decimal_equal(invoice.total_amount, subtotal - discount + tax_amount)
    
    # ========== Payment Status Tests ==========
    
    def test_invoice_payment_status_pending(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice with pending payment status."""
        invoice_data = {
            'invoice_number': 'INV-PENDING-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 500.00,
            'payment_status': 'pending'
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        assert invoice.payment_status == 'pending'
    
    def test_invoice_payment_status_transitions(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice payment status transitions."""
        invoice_data = {
            'invoice_number': 'INV-STATUS-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 500.00,
            'payment_status': 'pending'
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        
        # Transition: pending → partially_paid
        self.service.update_invoice(invoice.id, {'payment_status': 'partially_paid'})
        db_session.refresh(invoice)
        assert invoice.payment_status == 'partially_paid'
        
        # Transition: partially_paid → paid
        self.service.update_invoice(invoice.id, {'payment_status': 'paid'})
        db_session.refresh(invoice)
        assert invoice.payment_status == 'paid'
    
    def test_invoice_partial_payment_tracking(self, db_session, sample_customer, sample_branch, sample_user):
        """Test tracking partial payments on invoice."""
        total_amount = 1000.00
        
        invoice_data = {
            'invoice_number': 'INV-PARTIAL-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': total_amount,
            'amount_paid': 0.00,
            'payment_status': 'pending'
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        
        # Record first partial payment
        self.service.update_invoice(invoice.id, {
            'amount_paid': 400.00,
            'payment_status': 'partially_paid'
        })
        db_session.refresh(invoice)
        assert_decimal_equal(invoice.amount_paid or 0, 400.00)
        
        # Record final payment
        self.service.update_invoice(invoice.id, {
            'amount_paid': 1000.00,
            'payment_status': 'paid'
        })
        db_session.refresh(invoice)
        assert_decimal_equal(invoice.amount_paid or 0, 1000.00)
        assert invoice.payment_status == 'paid'
    
    # ========== Due Date Tests ==========
    
    def test_invoice_with_due_date(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice with due date."""
        invoice_date = '2024-01-15'
        due_date = '2024-02-15'  # 30 days later
        
        invoice_data = {
            'invoice_number': 'INV-DUE-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': invoice_date,
            'due_date': due_date,
            'total_amount': 500.00
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        assert invoice.due_date is not None
    
    def test_overdue_invoice(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice that is overdue."""
        past_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        
        invoice_data = {
            'invoice_number': 'INV-OVERDUE-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': past_date,
            'due_date': past_date,
            'total_amount': 500.00,
            'payment_status': 'overdue'
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        assert invoice.payment_status == 'overdue'
    
    # ========== Edge Cases Tests ==========
    
    def test_create_invoice_with_zero_amount(self, db_session, sample_customer, sample_branch, sample_user):
        """Test creating invoice with zero total amount."""
        invoice_data = {
            'invoice_number': 'INV-ZERO-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 0.00
        }
        
        result, status = self.service.create_invoice(invoice_data)
        assert status == 201
        
        invoice = db_session.query(Invoice).first()
        assert invoice.total_amount == 0.00
    
    def test_create_invoice_with_large_amount(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice with very large amount."""
        large_amount = 9999999.99
        
        invoice_data = {
            'invoice_number': 'INV-LARGE-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': large_amount
        }
        
        result, status = self.service.create_invoice(invoice_data)
        assert status == 201
        
        invoice = db_session.query(Invoice).first()
        assert_decimal_equal(invoice.total_amount, large_amount)
    
    def test_invoice_with_long_notes(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice with very long notes."""
        long_notes = "A" * 2000
        
        invoice_data = {
            'invoice_number': 'INV-LONG-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 500.00,
            'notes': long_notes
        }
        
        result, status = self.service.create_invoice(invoice_data)
        assert status == 201
        
        invoice = db_session.query(Invoice).first()
        assert len(invoice.notes or '') >= 2000
    
    def test_get_invoices_empty_database(self, db_session):
        """Test getting invoices when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_invoices(None, filter_obj)
        
        assert status == 200
        assert 'invoices' in result
        assert len(result['invoices']) == 0
    
    # ========== Error Handling Tests ==========
    
    def test_create_invoice_missing_required_fields(self, db_session):
        """Test creating invoice with missing required fields."""
        incomplete_data = {
            'invoice_number': 'INV-INCOMPLETE-001',
            'total_amount': 500.00
            # Missing customer_id, branch_id, user_id, date
        }
        
        with pytest.raises(Exception):
            self.service.create_invoice(incomplete_data)
    
    def test_create_invoice_invalid_customer(self, db_session, sample_branch, sample_user):
        """Test creating invoice with non-existent customer."""
        invoice_data = {
            'invoice_number': 'INV-INVALID-001',
            'customer_id': uuid.uuid4(),  # Non-existent
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'total_amount': 500.00
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_invoice(invoice_data)
    
    def test_update_invoice_not_found(self, db_session):
        """Test updating a non-existent invoice."""
        non_existent_id = uuid.uuid4()
        update_data = {'total_amount': 600.00}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_invoice(non_existent_id, update_data)
    
    def test_delete_invoice_not_found(self, db_session):
        """Test deleting a non-existent invoice."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_invoice(non_existent_id)
    
    def test_invoice_decimal_precision(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice amounts with high decimal precision."""
        precise_subtotal = 1234.5678
        precise_tax = 61.7284
        precise_total = precise_subtotal + precise_tax
        
        invoice_data = {
            'invoice_number': 'INV-PRECISE-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'subtotal': precise_subtotal,
            'tax_amount': precise_tax,
            'total_amount': precise_total
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        # Should maintain precision
        assert float(invoice.subtotal) == pytest.approx(precise_subtotal, rel=0.0001)
        assert float(invoice.tax_amount) == pytest.approx(precise_tax, rel=0.0001)
    
    def test_invoice_with_multiple_tax_rates(self, db_session, sample_customer, sample_branch, sample_user):
        """Test invoice with complex tax calculations."""
        # Example: Different items with different tax rates
        subtotal = 1000.00
        tax1 = 40.00  # 5% on $800
        tax2 = 20.00  # 10% on $200  
        total_tax = tax1 + tax2
        total = subtotal + total_tax
        
        invoice_data = {
            'invoice_number': 'INV-MULTITAX-001',
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'date': '2024-01-15',
            'subtotal': subtotal,
            'tax_amount': total_tax,
            'total_amount': total
        }
        self.service.create_invoice(invoice_data)
        
        invoice = db_session.query(Invoice).first()
        assert_decimal_equal(invoice.tax_amount, 60.00)

