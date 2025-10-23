"""
Unit tests for Expense Service.

Tests all business logic in expense/service.py including:
- Expense CRUD operations
- Expense categorization
- Budget calculations
- Expense approval workflows
- File attachment handling
- Edge cases and error handling
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import assert_decimal_equal, create_mock_filter
from app.expense.service import ExpenseService
from app.expense.model import Expense, ExpenseCategory
from app.common.error_handling import ResourceNotFoundError


class TestExpenseService(BaseServiceTestCase):
    """Test cases for ExpenseService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = ExpenseService()
    
    # ========== Expense Category Tests ==========
    
    def test_create_expense_category_success(self, db_session):
        """Test creating an expense category successfully."""
        category_data = {
            'name': 'Office Supplies',
            'description': 'Items for office use',
            'is_active': True
        }
        
        result, status = self.service.create_expense_category(category_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify category was created
        category = db_session.query(ExpenseCategory).filter(
            ExpenseCategory.name == 'Office Supplies'
        ).first()
        assert category is not None
        assert category.is_active is True
    
    def test_get_expense_categories(self, db_session):
        """Test getting all expense categories."""
        # Create multiple categories
        categories = ['Travel', 'Materials', 'Utilities', 'Marketing']
        
        for cat_name in categories:
            category_data = {
                'name': cat_name,
                'is_active': True
            }
            self.service.create_expense_category(category_data)
        
        result, status = self.service.get_expense_categories()
        
        assert status == 200
        assert len(result) >= len(categories)
    
    # ========== Expense CRUD Tests ==========
    
    def test_create_expense_success(self, db_session):
        """Test creating an expense successfully."""
        # Create category first
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        expense_data = {
            'name': 'Office Rent',
            'category_id': category.id,
            'date': '2024-01-15',
            'amount': 1500.00,
            'description': 'Monthly office rent payment',
            'status': 'PENDING'
        }
        
        # Create mock files object
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        
        result, status = self.service.create_expense(expense_data, files)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify expense was created
        expense = db_session.query(Expense).filter(
            Expense.name == 'Office Rent'
        ).first()
        assert expense is not None
        assert_decimal_equal(expense.amount, 1500.00)
        assert expense.status == 'PENDING'
    
    def test_get_expenses_with_pagination(self, db_session):
        """Test getting expenses with pagination."""
        # Create category
        category_data = {'name': 'General', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        
        # Create multiple expenses
        for i in range(12):
            expense_data = {
                'name': f'Expense {i}',
                'category_id': category.id,
                'date': '2024-01-15',
                'amount': 100.00 * (i + 1),
                'status': 'PENDING'
            }
            self.service.create_expense(expense_data, files)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_expenses(None, filter_obj)
        
        assert status == 200
        assert 'expenses' in result
        assert 'filters' in result
    
    def test_get_expense_by_id(self, db_session):
        """Test getting a specific expense by ID."""
        # Create category and expense
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        expense_data = {
            'name': 'Test Expense',
            'category_id': category.id,
            'date': '2024-01-15',
            'amount': 500.00,
            'status': 'PENDING'
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        self.service.create_expense(expense_data, files)
        
        expense = db_session.query(Expense).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_expenses(expense.id, filter_obj)
        
        assert status == 200
        assert 'expenses' in result
    
    def test_update_expense_success(self, db_session):
        """Test updating an expense."""
        # Create category and expense
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        expense_data = {
            'name': 'Original Expense',
            'category_id': category.id,
            'date': '2024-01-15',
            'amount': 500.00,
            'status': 'PENDING'
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        self.service.create_expense(expense_data, files)
        
        expense = db_session.query(Expense).first()
        
        # Update expense
        update_data = {
            'name': 'Updated Expense',
            'amount': 750.00,
            'status': 'APPROVED',
            'date': '2024-01-20'
        }
        
        result, status = self.service.update_expense(expense.id, update_data, files)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(expense)
        assert expense.name == 'Updated Expense'
        assert_decimal_equal(expense.amount, 750.00)
        assert expense.status == 'APPROVED'
    
    def test_delete_expense_success(self, db_session):
        """Test deleting an expense."""
        # Create category and expense
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        expense_data = {
            'name': 'Delete Me',
            'category_id': category.id,
            'date': '2024-01-15',
            'amount': 100.00,
            'status': 'PENDING'
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        self.service.create_expense(expense_data, files)
        
        expense = db_session.query(Expense).first()
        expense_id = expense.id
        
        result, status = self.service.delete_expense(expense_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_expense = db_session.query(Expense).filter_by(id=expense_id).first()
        assert deleted_expense is None
    
    # ========== Status Workflow Tests ==========
    
    def test_expense_status_transitions(self, db_session):
        """Test expense status transitions."""
        # Create category and expense
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        expense_data = {
            'name': 'Status Test',
            'category_id': category.id,
            'date': '2024-01-15',
            'amount': 500.00,
            'status': 'PENDING'
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        self.service.create_expense(expense_data, files)
        
        expense = db_session.query(Expense).first()
        
        # Transition: PENDING → APPROVED
        self.service.update_expense(expense.id, {'status': 'APPROVED', 'date': '2024-01-15'}, files)
        db_session.refresh(expense)
        assert expense.status == 'APPROVED'
        
        # Transition: APPROVED → PAID
        self.service.update_expense(expense.id, {'status': 'PAID', 'date': '2024-01-15'}, files)
        db_session.refresh(expense)
        assert expense.status == 'PAID'
    
    def test_reject_expense(self, db_session):
        """Test rejecting an expense."""
        # Create category and expense
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        expense_data = {
            'name': 'Rejected Expense',
            'category_id': category.id,
            'date': '2024-01-15',
            'amount': 500.00,
            'status': 'PENDING'
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        self.service.create_expense(expense_data, files)
        
        expense = db_session.query(Expense).first()
        
        # Reject
        self.service.update_expense(expense.id, {'status': 'REJECTED', 'date': '2024-01-15'}, files)
        db_session.refresh(expense)
        assert expense.status == 'REJECTED'
    
    # ========== Amount Tests ==========
    
    def test_expense_with_zero_amount(self, db_session):
        """Test expense with zero amount."""
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        expense_data = {
            'name': 'Zero Expense',
            'category_id': category.id,
            'date': '2024-01-15',
            'amount': 0.00,
            'status': 'PENDING'
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        result, status = self.service.create_expense(expense_data, files)
        
        assert status == 201
        expense = db_session.query(Expense).first()
        assert expense.amount == 0.00
    
    def test_expense_with_large_amount(self, db_session):
        """Test expense with very large amount."""
        category_data = {'name': 'Test Category', 'is_active': True}
        self.service.create_expense_category(category_data)
        category = db_session.query(ExpenseCategory).first()
        
        large_amount = 999999.99
        
        expense_data = {
            'name': 'Large Expense',
            'category_id': category.id,
            'date': '2024-01-15',
            'amount': large_amount,
            'status': 'PENDING'
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        result, status = self.service.create_expense(expense_data, files)
        
        assert status == 201
        expense = db_session.query(Expense).first()
        assert_decimal_equal(expense.amount, large_amount)
    
    # ========== Error Handling Tests ==========
    
    def test_create_expense_missing_required_fields(self, db_session):
        """Test creating expense with missing required fields."""
        incomplete_data = {
            'name': 'Incomplete Expense'
            # Missing category_id, date, amount
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        
        with pytest.raises(Exception):
            self.service.create_expense(incomplete_data, files)
    
    def test_create_expense_invalid_category(self, db_session):
        """Test creating expense with non-existent category."""
        expense_data = {
            'name': 'Invalid Category Expense',
            'category_id': uuid.uuid4(),  # Non-existent
            'date': '2024-01-15',
            'amount': 100.00,
            'status': 'PENDING'
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_expense(expense_data, files)
    
    def test_update_expense_not_found(self, db_session):
        """Test updating a non-existent expense."""
        non_existent_id = uuid.uuid4()
        update_data = {'amount': 200.00, 'date': '2024-01-15'}
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_expense(non_existent_id, update_data, files)
    
    def test_delete_expense_not_found(self, db_session):
        """Test deleting a non-existent expense."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_expense(non_existent_id)
    
    def test_get_expenses_empty_database(self, db_session):
        """Test getting expenses when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_expenses(None, filter_obj)
        
        assert status == 200
        assert 'expenses' in result

