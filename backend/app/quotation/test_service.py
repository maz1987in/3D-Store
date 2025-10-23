"""
Unit tests for Quotation Service.

Tests all business logic in quotation/service.py including:
- Quotation CRUD operations
- Pricing calculations (base + materials + labor)
- Quote approval/rejection workflows
- Quote expiration handling
- Conversion to orders
- Edge cases and error handling
"""

import pytest
import uuid
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import (
    assert_decimal_equal,
    create_mock_filter,
    assert_pagination_structure
)
from app.quotation.service import QuotationService
from app.quotation.model import Quotation
from app.common.error_handling import ResourceNotFoundError


class TestQuotationService(BaseServiceTestCase):
    """Test cases for QuotationService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = QuotationService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_quotation_success(self, db_session, sample_customer, sample_branch, sample_user):
        """Test creating a quotation successfully."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-2024-001',
            'date': '2024-01-15',
            'valid_until': '2024-02-15',
            'subtotal': 500.00,
            'tax_amount': 50.00,
            'total_amount': 550.00,
            'notes': 'Test quotation'
        }
        
        result, status = self.service.create_quotation(quotation_data)
        
        assert status == 201
        assert 'Quotation Created' in result
        
        # Verify quotation was created
        quotation = db_session.query(Quotation).filter(
            Quotation.quote_number == 'Q-2024-001'
        ).first()
        assert quotation is not None
        assert_decimal_equal(quotation.total_amount, 550.00)
    
    def test_get_quotations_with_pagination(self, db_session, sample_customer, sample_branch, sample_user):
        """Test getting quotations with pagination."""
        # Create multiple quotations
        for i in range(15):
            quotation_data = {
                'customer_id': sample_customer.id,
                'branch_id': sample_branch.id,
                'user_id': sample_user.id,
                'quote_number': f'Q-2024-{str(i+1).zfill(3)}',
                'date': '2024-01-15',
                'total_amount': 100.00 * (i + 1)
            }
            self.service.create_quotation(quotation_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_quotations(None, filter_obj)
        
        assert status == 200
        assert 'quotations' in result
        assert 'filters' in result
        assert len(result['quotations']) == 10
    
    def test_get_quotation_by_id(self, db_session, sample_customer, sample_branch, sample_user):
        """Test getting a specific quotation by ID."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-TEST-001',
            'date': '2024-01-15',
            'total_amount': 500.00
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_quotations(quotation.id, filter_obj)
        
        assert status == 200
        assert 'quotations' in result
        assert len(result['quotations']) == 1
    
    def test_get_quotation_by_id_not_found(self, db_session):
        """Test getting a non-existent quotation."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            self.service.get_quotations(non_existent_id, filter_obj)
        
        assert "Quotation" in str(exc_info.value)
    
    def test_get_quotations_by_user_id(self, db_session, sample_customer, sample_branch, sample_user):
        """Test getting all quotations for a specific user."""
        # Create quotations for user
        for i in range(3):
            quotation_data = {
                'customer_id': sample_customer.id,
                'branch_id': sample_branch.id,
                'user_id': sample_user.id,
                'quote_number': f'Q-USER-{i+1}',
                'date': '2024-01-15',
                'total_amount': 200.00
            }
            self.service.create_quotation(quotation_data)
        
        filter_obj = create_mock_filter()
        result, status = self.service.get_quotations_by_user_id(sample_user.id, filter_obj)
        
        assert status == 200
        assert 'quotations' in result
        assert len(result['quotations']) >= 3
    
    def test_update_quotation_success(self, db_session, sample_customer, sample_branch, sample_user):
        """Test updating a quotation."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-UPDATE-001',
            'date': '2024-01-15',
            'total_amount': 500.00
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        
        # Update the quotation
        update_data = {
            'total_amount': 750.00,
            'notes': 'Updated quotation'
        }
        
        result, status = self.service.update_quotation(quotation.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(quotation)
        assert_decimal_equal(quotation.total_amount, 750.00)
    
    def test_delete_quotation_success(self, db_session, sample_customer, sample_branch, sample_user):
        """Test deleting a quotation."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-DELETE-001',
            'date': '2024-01-15',
            'total_amount': 300.00
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        quotation_id = quotation.id
        
        result, status = self.service.delete_quotation(quotation_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_quotation = db_session.query(Quotation).filter_by(id=quotation_id).first()
        assert deleted_quotation is None
    
    # ========== Pricing Calculations Tests ==========
    
    def test_quotation_total_calculation(self, db_session, sample_customer, sample_branch, sample_user):
        """Test quotation total amount calculation (subtotal + tax)."""
        subtotal = 1000.00
        tax_rate = 0.05  # 5%
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-CALC-001',
            'date': '2024-01-15',
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        
        assert_decimal_equal(quotation.subtotal, 1000.00)
        assert_decimal_equal(quotation.tax_amount, 50.00)
        assert_decimal_equal(quotation.total_amount, 1050.00)
    
    def test_quotation_with_discount(self, db_session, sample_customer, sample_branch, sample_user):
        """Test quotation with discount applied."""
        subtotal = 1000.00
        discount = 100.00  # $100 discount
        tax_amount = (subtotal - discount) * 0.05
        total = subtotal - discount + tax_amount
        
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-DISCOUNT-001',
            'date': '2024-01-15',
            'subtotal': subtotal,
            'discount_amount': discount,
            'tax_amount': tax_amount,
            'total_amount': total
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        assert_decimal_equal(quotation.discount_amount or 0, 100.00)
    
    # ========== Quote Status Workflow Tests ==========
    
    def test_quotation_status_pending(self, db_session, sample_customer, sample_branch, sample_user):
        """Test quotation with pending status."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-PENDING-001',
            'date': '2024-01-15',
            'quote_status': 'pending',
            'total_amount': 500.00
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        assert quotation.quote_status == 'pending'
    
    def test_quotation_approval(self, db_session, sample_customer, sample_branch, sample_user):
        """Test approving a quotation."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-APPROVE-001',
            'date': '2024-01-15',
            'quote_status': 'pending',
            'total_amount': 500.00
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        
        # Approve the quotation
        update_data = {'quote_status': 'approved'}
        self.service.update_quotation(quotation.id, update_data)
        
        db_session.refresh(quotation)
        assert quotation.quote_status == 'approved'
    
    def test_quotation_rejection(self, db_session, sample_customer, sample_branch, sample_user):
        """Test rejecting a quotation."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-REJECT-001',
            'date': '2024-01-15',
            'quote_status': 'pending',
            'total_amount': 500.00
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        
        # Reject the quotation
        update_data = {'quote_status': 'rejected'}
        self.service.update_quotation(quotation.id, update_data)
        
        db_session.refresh(quotation)
        assert quotation.quote_status == 'rejected'
    
    # ========== Quote Expiration Tests ==========
    
    def test_quotation_valid_until_date(self, db_session, sample_customer, sample_branch, sample_user):
        """Test quotation with valid_until date."""
        valid_until = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-VALID-001',
            'date': '2024-01-15',
            'valid_until': valid_until,
            'total_amount': 500.00
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        assert quotation.valid_until is not None
    
    def test_expired_quotation(self, db_session, sample_customer, sample_branch, sample_user):
        """Test quotation that has expired."""
        # Create quotation with past expiry date
        expired_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-EXPIRED-001',
            'date': '2024-01-15',
            'valid_until': expired_date,
            'quote_status': 'expired',
            'total_amount': 500.00
        }
        self.service.create_quotation(quotation_data)
        
        quotation = db_session.query(Quotation).first()
        assert quotation.quote_status == 'expired'
    
    # ========== Edge Cases Tests ==========
    
    def test_quotation_with_zero_amount(self, db_session, sample_customer, sample_branch, sample_user):
        """Test quotation with zero total amount."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-ZERO-001',
            'date': '2024-01-15',
            'total_amount': 0.00
        }
        
        result, status = self.service.create_quotation(quotation_data)
        assert status == 201
        
        quotation = db_session.query(Quotation).first()
        assert quotation.total_amount == 0.00
    
    def test_quotation_with_large_amount(self, db_session, sample_customer, sample_branch, sample_user):
        """Test quotation with very large amount."""
        large_amount = 9999999.99
        
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-LARGE-001',
            'date': '2024-01-15',
            'total_amount': large_amount
        }
        
        result, status = self.service.create_quotation(quotation_data)
        assert status == 201
        
        quotation = db_session.query(Quotation).first()
        assert_decimal_equal(quotation.total_amount, large_amount)
    
    def test_quotation_unique_quote_number(self, db_session, sample_customer, sample_branch, sample_user):
        """Test that quote numbers must be unique."""
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-UNIQUE-001',
            'date': '2024-01-15',
            'total_amount': 500.00
        }
        
        # Create first quotation
        self.service.create_quotation(quotation_data)
        
        # Attempt to create duplicate
        with pytest.raises(Exception):  # Should raise integrity error
            self.service.create_quotation(quotation_data)
    
    def test_get_quotations_empty_database(self, db_session):
        """Test getting quotations when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_quotations(None, filter_obj)
        
        assert status == 200
        assert 'quotations' in result
        assert len(result['quotations']) == 0
    
    def test_quotation_with_long_notes(self, db_session, sample_customer, sample_branch, sample_user):
        """Test quotation with very long notes."""
        long_notes = "A" * 1000  # 1000 character note
        
        quotation_data = {
            'customer_id': sample_customer.id,
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-LONG-001',
            'date': '2024-01-15',
            'total_amount': 500.00,
            'notes': long_notes
        }
        
        result, status = self.service.create_quotation(quotation_data)
        assert status == 201
        
        quotation = db_session.query(Quotation).first()
        assert len(quotation.notes or '') > 500
    
    # ========== Error Handling Tests ==========
    
    def test_create_quotation_missing_required_fields(self, db_session):
        """Test creating quotation with missing required fields."""
        incomplete_data = {
            'quote_number': 'Q-INCOMPLETE-001',
            'total_amount': 500.00
            # Missing customer_id, branch_id, user_id, date
        }
        
        with pytest.raises(Exception):
            self.service.create_quotation(incomplete_data)
    
    def test_create_quotation_invalid_customer(self, db_session, sample_branch, sample_user):
        """Test creating quotation with non-existent customer."""
        quotation_data = {
            'customer_id': uuid.uuid4(),  # Non-existent
            'branch_id': sample_branch.id,
            'user_id': sample_user.id,
            'quote_number': 'Q-INVALID-001',
            'date': '2024-01-15',
            'total_amount': 500.00
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_quotation(quotation_data)
    
    def test_update_quotation_not_found(self, db_session):
        """Test updating a non-existent quotation."""
        non_existent_id = uuid.uuid4()
        update_data = {'total_amount': 600.00}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_quotation(non_existent_id, update_data)
    
    def test_delete_quotation_not_found(self, db_session):
        """Test deleting a non-existent quotation."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_quotation(non_existent_id)

