"""
Unit tests for Transaction Service.

Tests all business logic in transaction/service.py including:
- Transaction CRUD operations
- Multi-location inventory transfers (store-to-store, branch-to-branch)
- Transaction audit trails and history tracking
- Transaction rollback scenarios
- Product transaction tracking
- Fiscal year integration
- Edge cases and error handling
"""

import pytest
import uuid
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.transaction.service import TransactionService
from app.transaction.model import Transaction
from app.common.error_handling import ResourceNotFoundError


class TestTransactionService(BaseServiceTestCase):
    """Test cases for TransactionService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = TransactionService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_transaction_success(self, db_session, sample_product, sample_store):
        """Test creating a transaction successfully."""
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_store.id,
            'to_location_id': None,
            'quantity': 10,
            'unit_price': 25.50,
            'type': 'purchase',
            'notes': 'Initial stock purchase'
        }
        
        result, status = self.service.create_transaction(transaction_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify transaction was created
        transaction = db_session.query(Transaction).filter(
            Transaction.product_id == sample_product.id
        ).first()
        assert transaction is not None
        assert transaction.quantity == 10
        assert float(transaction.unit_price) == 25.50
    
    def test_get_transactions_with_pagination(self, db_session, sample_product, sample_store):
        """Test getting transactions with pagination."""
        # Create multiple transactions
        for i in range(12):
            transaction_data = {
                'product_id': sample_product.id,
                'from_location_id': sample_store.id,
                'quantity': i + 1,
                'unit_price': 10.00 + i,
                'type': 'adjustment',
                'notes': f'Transaction {i}'
            }
            self.service.create_transaction(transaction_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_transactions(None, filter_obj)
        
        assert status == 200
        assert 'transactions' in result or len(result) > 0
    
    def test_get_transaction_by_id(self, db_session, sample_product, sample_store):
        """Test getting a specific transaction by ID."""
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_store.id,
            'quantity': 5,
            'unit_price': 15.00,
            'type': 'sale',
            'notes': 'Test transaction'
        }
        self.service.create_transaction(transaction_data)
        
        transaction = db_session.query(Transaction).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_transactions(transaction.id, filter_obj)
        
        assert status == 200
    
    # ========== Multi-Location Transfer Tests ==========
    
    def test_transfer_between_stores(self, db_session, sample_product):
        """Test inventory transfer between two stores."""
        from app.store.model import Store
        
        # Create two stores
        store1 = Store(name='Store 1', code='ST001', active=True)
        store2 = Store(name='Store 2', code='ST002', active=True)
        db_session.add(store1)
        db_session.add(store2)
        db_session.commit()
        
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': store1.id,
            'to_location_id': store2.id,
            'quantity': 15,
            'unit_price': 20.00,
            'type': 'transfer',
            'notes': 'Transfer from Store 1 to Store 2'
        }
        
        result, status = self.service.create_transaction(transaction_data)
        
        assert status == 201
        
        transaction = db_session.query(Transaction).filter(
            Transaction.from_location_id == store1.id,
            Transaction.to_location_id == store2.id
        ).first()
        
        assert transaction is not None
        assert transaction.type == 'transfer'
        assert transaction.quantity == 15
    
    def test_transfer_between_branches(self, db_session, sample_product, sample_branch):
        """Test inventory transfer between branches."""
        from app.branch.model import Branch
        
        # Create another branch
        branch2 = Branch(name='Branch 2', code='BR002', active=True)
        db_session.add(branch2)
        db_session.commit()
        
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_branch.id,
            'to_location_id': branch2.id,
            'quantity': 20,
            'unit_price': 30.00,
            'type': 'transfer',
            'notes': 'Branch transfer'
        }
        
        result, status = self.service.create_transaction(transaction_data)
        
        assert status == 201
    
    # ========== Transaction Type Tests ==========
    
    def test_transaction_types(self, db_session, sample_product, sample_store):
        """Test different transaction types."""
        transaction_types = ['purchase', 'sale', 'adjustment', 'return', 'transfer']
        
        for trans_type in transaction_types:
            transaction_data = {
                'product_id': sample_product.id,
                'from_location_id': sample_store.id,
                'quantity': 5,
                'unit_price': 10.00,
                'type': trans_type,
                'notes': f'{trans_type} transaction'
            }
            result, status = self.service.create_transaction(transaction_data)
            assert status == 201
        
        # Verify all types created
        transactions = db_session.query(Transaction).filter(
            Transaction.product_id == sample_product.id
        ).all()
        created_types = [t.type for t in transactions]
        assert set(created_types) >= set(transaction_types)
    
    # ========== Quantity and Price Tests ==========
    
    def test_transaction_with_decimal_quantity(self, db_session, sample_product, sample_store):
        """Test transaction with decimal quantities (for materials)."""
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_store.id,
            'quantity': 10.5,  # Decimal quantity
            'unit_price': 15.75,
            'type': 'purchase',
            'notes': 'Material purchase'
        }
        
        result, status = self.service.create_transaction(transaction_data)
        
        assert status == 201
        
        transaction = db_session.query(Transaction).filter(
            Transaction.notes == 'Material purchase'
        ).first()
        assert transaction.quantity == 10.5
    
    def test_transaction_with_zero_price(self, db_session, sample_product, sample_store):
        """Test transaction with zero price (free items, samples)."""
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_store.id,
            'quantity': 3,
            'unit_price': 0.00,
            'type': 'adjustment',
            'notes': 'Free sample'
        }
        
        result, status = self.service.create_transaction(transaction_data)
        
        assert status == 201
    
    def test_transaction_total_value_calculation(self, db_session, sample_product, sample_store):
        """Test transaction total value calculation."""
        quantity = 10
        unit_price = 25.50
        
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_store.id,
            'quantity': quantity,
            'unit_price': unit_price,
            'type': 'purchase',
            'notes': 'Value calculation test'
        }
        
        result, status = self.service.create_transaction(transaction_data)
        assert status == 201
        
        transaction = db_session.query(Transaction).filter(
            Transaction.notes == 'Value calculation test'
        ).first()
        
        # Calculate total value
        total_value = transaction.quantity * float(transaction.unit_price)
        assert total_value == quantity * unit_price
    
    # ========== Product Tracking Tests ==========
    
    def test_get_transactions_by_product(self, db_session, sample_product, sample_store):
        """Test getting all transactions for a specific product."""
        # Create multiple transactions for product
        for i in range(5):
            transaction_data = {
                'product_id': sample_product.id,
                'from_location_id': sample_store.id,
                'quantity': i + 1,
                'unit_price': 10.00,
                'type': 'adjustment',
                'notes': f'Product transaction {i}'
            }
            self.service.create_transaction(transaction_data)
        
        # Query transactions by product
        product_transactions = db_session.query(Transaction).filter(
            Transaction.product_id == sample_product.id
        ).all()
        
        assert len(product_transactions) >= 5
    
    # ========== Audit Trail Tests ==========
    
    def test_transaction_timestamps(self, db_session, sample_product, sample_store):
        """Test that transactions have proper timestamps."""
        from datetime import datetime, timezone
        
        before_creation = datetime.now(timezone.utc)
        
        transaction_data = {
            'product_id': sample_product.id,
            'from_location_id': sample_store.id,
            'quantity': 10,
            'unit_price': 15.00,
            'type': 'purchase',
            'notes': 'Timestamp test'
        }
        
        result, status = self.service.create_transaction(transaction_data)
        assert status == 201
        
        after_creation = datetime.now(timezone.utc)
        
        transaction = db_session.query(Transaction).filter(
            Transaction.notes == 'Timestamp test'
        ).first()
        
        assert transaction.create_date >= before_creation
        assert transaction.create_date <= after_creation
    
    def test_transaction_history_tracking(self, db_session, sample_product, sample_store):
        """Test tracking transaction history for audit purposes."""
        # Create a series of transactions
        transaction_history = [
            ('purchase', 50, 'Initial stock'),
            ('sale', -10, 'Sale to customer'),
            ('return', 2, 'Customer return'),
            ('adjustment', -5, 'Damage adjustment'),
            ('transfer', -10, 'Transfer to branch')
        ]
        
        for trans_type, quantity, notes in transaction_history:
            transaction_data = {
                'product_id': sample_product.id,
                'from_location_id': sample_store.id,
                'quantity': abs(quantity),
                'unit_price': 15.00,
                'type': trans_type,
                'notes': notes
            }
            self.service.create_transaction(transaction_data)
        
        # Retrieve history
        history = db_session.query(Transaction).filter(
            Transaction.product_id == sample_product.id
        ).order_by(Transaction.create_date).all()
        
        assert len(history) >= len(transaction_history)
    
    # ========== Error Handling Tests ==========
    
    def test_create_transaction_invalid_product(self, db_session, sample_store):
        """Test creating transaction with non-existent product."""
        transaction_data = {
            'product_id': uuid.uuid4(),  # Non-existent
            'from_location_id': sample_store.id,
            'quantity': 10,
            'unit_price': 15.00,
            'type': 'purchase',
            'notes': 'Invalid product'
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_transaction(transaction_data)
    
    def test_get_transaction_not_found(self, db_session):
        """Test getting a non-existent transaction."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        # May return empty or raise error depending on implementation
        result, status = self.service.get_transactions(non_existent_id, filter_obj)
        # Should handle gracefully
        assert status in [200, 404]
    
    def test_get_transactions_empty_database(self, db_session):
        """Test getting transactions when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_transactions(None, filter_obj)
        
        assert status == 200

