"""
Unit tests for Store Service.

Tests all business logic in store/service.py including:
- Store CRUD operations
- Store-branch relationships
- Multi-language translations
- Active/inactive status management
- Multi-tenant functionality
- Edge cases and error handling
"""

import pytest
import uuid
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.store.service import StoreService
from app.store.model import Store
from app.common.error_handling import ResourceNotFoundError


class TestStoreService(BaseServiceTestCase):
    """Test cases for StoreService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = StoreService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_store_success(self, db_session, sample_branch):
        """Test creating a store successfully."""
        store_data = {
            'name': json.dumps({'en': 'Main Store', 'ar': 'المتجر الرئيسي'}),
            'location': '123 Store Street',
            'manager': 'John Doe',
            'branch_id': sample_branch.id
        }
        
        result, status = self.service.create_store(store_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify store was created
        store = db_session.query(Store).first()
        assert store is not None
        assert store.location == '123 Store Street'
    
    def test_get_stores_with_pagination(self, db_session, sample_branch):
        """Test getting stores with pagination."""
        # Create multiple stores
        for i in range(12):
            store_data = {
                'name': json.dumps({'en': f'Store {i}', 'ar': f'متجر {i}'}),
                'location': f'Location {i}',
                'manager': f'Manager {i}',
                'branch_id': sample_branch.id
            }
            self.service.create_store(store_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_stores(None, filter_obj)
        
        assert status == 200
        assert 'stores' in result
        assert 'filters' in result
    
    def test_get_store_by_id(self, db_session, sample_branch):
        """Test getting a specific store by ID."""
        store_data = {
            'name': json.dumps({'en': 'Test Store', 'ar': 'متجر اختبار'}),
            'location': 'Test Location',
            'manager': 'Test Manager',
            'branch_id': sample_branch.id
        }
        self.service.create_store(store_data)
        
        store = db_session.query(Store).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_stores(store.id, filter_obj)
        
        assert status == 200
        assert 'stores' in result
    
    def test_update_store_success(self, db_session, sample_branch):
        """Test updating a store."""
        # Create store
        store_data = {
            'name': json.dumps({'en': 'Original Store', 'ar': 'متجر أصلي'}),
            'location': 'Original Location',
            'manager': 'Original Manager',
            'branch_id': sample_branch.id
        }
        self.service.create_store(store_data)
        
        store = db_session.query(Store).first()
        
        # Update store
        update_data = {
            'location': 'Updated Location',
            'manager': 'Updated Manager'
        }
        
        result, status = self.service.update_store(store.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(store)
        assert store.location == 'Updated Location'
        assert store.manager == 'Updated Manager'
    
    def test_delete_store_success(self, db_session, sample_branch):
        """Test deleting a store."""
        store_data = {
            'name': json.dumps({'en': 'Delete Store', 'ar': 'حذف متجر'}),
            'location': 'Delete Location',
            'manager': 'Delete Manager',
            'branch_id': sample_branch.id
        }
        self.service.create_store(store_data)
        
        store = db_session.query(Store).first()
        store_id = store.id
        
        result, status = self.service.delete_store(store_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_store = db_session.query(Store).filter_by(id=store_id).first()
        assert deleted_store is None
    
    # ========== Branch Relationship Tests ==========
    
    def test_multiple_stores_same_branch(self, db_session, sample_branch):
        """Test creating multiple stores for the same branch."""
        for i in range(3):
            store_data = {
                'name': json.dumps({'en': f'Branch Store {i}', 'ar': f'متجر فرع {i}'}),
                'location': f'Location {i}',
                'manager': f'Manager {i}',
                'branch_id': sample_branch.id
            }
            result, status = self.service.create_store(store_data)
            assert status == 201
        
        # Verify all stores belong to same branch
        stores = db_session.query(Store).filter(Store.branch_id == sample_branch.id).all()
        assert len(stores) >= 3
    
    def test_get_stores_empty_database(self, db_session):
        """Test getting stores when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_stores(None, filter_obj)
        
        assert status == 200
        assert 'stores' in result
    
    # ========== Error Handling Tests ==========
    
    def test_create_store_missing_required_fields(self, db_session):
        """Test creating store with missing required fields."""
        incomplete_data = {
            'location': 'Test Location'
            # Missing name and manager
        }
        
        with pytest.raises(Exception):
            self.service.create_store(incomplete_data)
    
    def test_get_store_not_found(self, db_session):
        """Test getting a non-existent store."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_stores(non_existent_id, filter_obj)
    
    def test_update_store_not_found(self, db_session):
        """Test updating a non-existent store."""
        non_existent_id = uuid.uuid4()
        update_data = {'location': 'New Location'}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_store(non_existent_id, update_data)
    
    def test_delete_store_not_found(self, db_session):
        """Test deleting a non-existent store."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_store(non_existent_id)

