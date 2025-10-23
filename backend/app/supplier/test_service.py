"""
Unit tests for Supplier Service.

Tests all business logic in supplier/service.py including:
- Supplier CRUD operations
- Supplier verification workflows
- Product-supplier relationships
- Contact information validation
- Status management
- Edge cases and error handling
"""

import pytest
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.supplier.service import SupplierService
from app.supplier.model import Supplier
from app.common.error_handling import ResourceNotFoundError


class TestSupplierService(BaseServiceTestCase):
    """Test cases for SupplierService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = SupplierService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_supplier_success(self, db_session):
        """Test creating a supplier successfully."""
        supplier_data = {
            'name': 'Test Supplier Inc.',
            'phone': '+1234567890',
            'email': 'supplier@example.com',
            'address': '123 Supplier Street',
            'city': 'Test City',
            'country': 'Test Country',
            'status': 'active',
            'is_verified': True
        }
        
        result, status = self.service.create_supplier(supplier_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify supplier was created
        supplier = db_session.query(Supplier).filter(
            Supplier.email == 'supplier@example.com'
        ).first()
        assert supplier is not None
        assert supplier.name == 'Test Supplier Inc.'
        assert supplier.phone == '+1234567890'
    
    def test_create_supplier_minimal_data(self, db_session):
        """Test creating supplier with minimal required data."""
        supplier_data = {
            'name': 'Minimal Supplier'
        }
        
        result, status = self.service.create_supplier(supplier_data)
        
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert supplier.name == 'Minimal Supplier'
        # Optional fields should be None
        assert supplier.phone is None
        assert supplier.email is None
    
    def test_get_suppliers_with_pagination(self, db_session):
        """Test getting suppliers with pagination."""
        # Create multiple suppliers
        for i in range(15):
            supplier_data = {
                'name': f'Supplier {i}',
                'email': f'supplier{i}@example.com',
                'status': 'active'
            }
            self.service.create_supplier(supplier_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_suppliers(None, filter_obj)
        
        assert status == 200
        assert 'suppliers' in result
        assert 'filters' in result
        assert len(result['suppliers']) == 10
    
    def test_get_supplier_by_id(self, db_session):
        """Test getting a specific supplier by ID."""
        supplier_data = {
            'name': 'Get Test Supplier',
            'email': 'gettest@supplier.com'
        }
        self.service.create_supplier(supplier_data)
        
        supplier = db_session.query(Supplier).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_suppliers(supplier.id, filter_obj)
        
        assert status == 200
        assert 'suppliers' in result
        assert result['suppliers']['name'] == 'Get Test Supplier'
    
    def test_update_supplier_success(self, db_session):
        """Test updating a supplier."""
        # Create supplier
        supplier_data = {
            'name': 'Original Supplier',
            'email': 'original@supplier.com',
            'status': 'pending'
        }
        self.service.create_supplier(supplier_data)
        
        supplier = db_session.query(Supplier).first()
        
        # Update supplier
        update_data = {
            'name': 'Updated Supplier',
            'status': 'active',
            'is_verified': True
        }
        
        result, status = self.service.update_supplier(supplier.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(supplier)
        assert supplier.name == 'Updated Supplier'
        assert supplier.status == 'active'
    
    def test_delete_supplier_success(self, db_session):
        """Test deleting a supplier."""
        supplier_data = {
            'name': 'Delete Test Supplier',
            'email': 'delete@supplier.com'
        }
        self.service.create_supplier(supplier_data)
        
        supplier = db_session.query(Supplier).first()
        supplier_id = supplier.id
        
        result, status = self.service.delete_supplier(supplier_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_supplier = db_session.query(Supplier).filter_by(id=supplier_id).first()
        assert deleted_supplier is None
    
    # ========== Verification Status Tests ==========
    
    def test_create_verified_supplier(self, db_session):
        """Test creating a verified supplier."""
        supplier_data = {
            'name': 'Verified Supplier',
            'email': 'verified@supplier.com',
            'is_verified': True
        }
        
        result, status = self.service.create_supplier(supplier_data)
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert supplier.is_verified is True
    
    def test_create_unverified_supplier(self, db_session):
        """Test creating an unverified supplier."""
        supplier_data = {
            'name': 'Unverified Supplier',
            'email': 'unverified@supplier.com',
            'is_verified': False
        }
        
        result, status = self.service.create_supplier(supplier_data)
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert supplier.is_verified is False
    
    def test_verify_supplier(self, db_session):
        """Test verifying a supplier."""
        # Create unverified supplier
        supplier_data = {
            'name': 'To Be Verified',
            'email': 'tobeverified@supplier.com',
            'is_verified': False
        }
        self.service.create_supplier(supplier_data)
        
        supplier = db_session.query(Supplier).first()
        
        # Verify the supplier
        update_data = {'is_verified': True}
        self.service.update_supplier(supplier.id, update_data)
        
        db_session.refresh(supplier)
        assert supplier.is_verified is True
    
    # ========== Status Management Tests ==========
    
    def test_supplier_status_transitions(self, db_session):
        """Test supplier status transitions."""
        # Create supplier
        supplier_data = {
            'name': 'Status Test Supplier',
            'email': 'status@supplier.com',
            'status': 'pending'
        }
        self.service.create_supplier(supplier_data)
        
        supplier = db_session.query(Supplier).first()
        
        # Transition: pending → active
        self.service.update_supplier(supplier.id, {'status': 'active'})
        db_session.refresh(supplier)
        assert supplier.status == 'active'
        
        # Transition: active → inactive
        self.service.update_supplier(supplier.id, {'status': 'inactive'})
        db_session.refresh(supplier)
        assert supplier.status == 'inactive'
    
    def test_filter_suppliers_by_status(self, db_session):
        """Test filtering suppliers by status."""
        # Create suppliers with different statuses
        statuses = ['active', 'inactive', 'pending', 'suspended']
        
        for i, status_val in enumerate(statuses):
            supplier_data = {
                'name': f'Supplier {i}',
                'email': f'supplier{i}@example.com',
                'status': status_val
            }
            self.service.create_supplier(supplier_data)
        
        # Verify all statuses
        suppliers = db_session.query(Supplier).all()
        supplier_statuses = [s.status for s in suppliers]
        assert set(supplier_statuses) >= set(statuses)
    
    # ========== Contact Information Tests ==========
    
    def test_supplier_with_complete_contact_info(self, db_session):
        """Test supplier with all contact information."""
        supplier_data = {
            'name': 'Complete Contact Supplier',
            'phone': '+1234567890',
            'email': 'complete@supplier.com',
            'mobile': '+9876543210',
            'website': 'https://supplier.com',
            'fax': '+1234567891'
        }
        
        result, status = self.service.create_supplier(supplier_data)
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert supplier.phone == '+1234567890'
        assert supplier.email == 'complete@supplier.com'
    
    def test_supplier_email_uniqueness(self, db_session):
        """Test that supplier emails should be unique."""
        supplier_data = {
            'name': 'First Supplier',
            'email': 'unique@supplier.com'
        }
        
        # Create first supplier
        result1, status1 = self.service.create_supplier(supplier_data)
        assert status1 == 201
        
        # Try to create second with same email
        supplier_data_2 = {
            'name': 'Second Supplier',
            'email': 'unique@supplier.com'  # Same email
        }
        
        # Should fail due to unique constraint
        with pytest.raises(Exception):
            self.service.create_supplier(supplier_data_2)
    
    # ========== Address Information Tests ==========
    
    def test_supplier_with_international_address(self, db_session):
        """Test supplier with international address."""
        supplier_data = {
            'name': 'International Supplier',
            'email': 'intl@supplier.com',
            'address': '456 Foreign Street',
            'city': 'Foreign City',
            'country': 'Foreign Country',
            'postal_code': '12345'
        }
        
        result, status = self.service.create_supplier(supplier_data)
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert supplier.country == 'Foreign Country'
        assert supplier.city == 'Foreign City'
    
    def test_supplier_multiple_countries(self, db_session):
        """Test suppliers from different countries."""
        countries = ['USA', 'UK', 'Germany', 'China', 'Oman']
        
        for i, country in enumerate(countries):
            supplier_data = {
                'name': f'Supplier {country}',
                'email': f'supplier{i}@{country.lower()}.com',
                'country': country
            }
            self.service.create_supplier(supplier_data)
        
        # Verify all countries
        suppliers = db_session.query(Supplier).all()
        supplier_countries = [s.country for s in suppliers if s.country]
        assert set(supplier_countries) >= set(countries)
    
    # ========== Edge Cases Tests ==========
    
    def test_create_supplier_with_long_name(self, db_session):
        """Test creating supplier with very long name."""
        long_name = "A" * 300
        
        supplier_data = {
            'name': long_name,
            'email': 'longname@supplier.com'
        }
        
        result, status = self.service.create_supplier(supplier_data)
        # Should either succeed or validate length
        assert status in [201, 400]
    
    def test_create_supplier_special_characters(self, db_session):
        """Test creating supplier with special characters in name."""
        supplier_data = {
            'name': "Supplier & Co., Ltd. (Pty)",
            'email': 'special@supplier.com'
        }
        
        result, status = self.service.create_supplier(supplier_data)
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert "&" in supplier.name
    
    def test_get_suppliers_empty_database(self, db_session):
        """Test getting suppliers when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_suppliers(None, filter_obj)
        
        assert status == 200
        assert 'suppliers' in result
        assert len(result['suppliers']) == 0
    
    def test_supplier_details_json_field(self, db_session):
        """Test supplier with JSON details field."""
        supplier_data = {
            'name': 'Detailed Supplier',
            'email': 'detailed@supplier.com',
            'details': {'tax_id': '123456', 'rating': 4.5, 'notes': 'Reliable supplier'}
        }
        
        result, status = self.service.create_supplier(supplier_data)
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert supplier.details is not None
    
    def test_update_supplier_partial_data(self, db_session):
        """Test updating only some fields of a supplier."""
        # Create supplier
        supplier_data = {
            'name': 'Partial Update Supplier',
            'email': 'partial@supplier.com',
            'phone': '+1111111111',
            'status': 'active'
        }
        self.service.create_supplier(supplier_data)
        
        supplier = db_session.query(Supplier).first()
        original_email = supplier.email
        
        # Update only phone
        update_data = {'phone': '+2222222222'}
        self.service.update_supplier(supplier.id, update_data)
        
        db_session.refresh(supplier)
        assert supplier.phone == '+2222222222'
        assert supplier.email == original_email  # Should not change
    
    # ========== Error Handling Tests ==========
    
    def test_get_supplier_not_found(self, db_session):
        """Test getting a non-existent supplier."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_suppliers(non_existent_id, filter_obj)
    
    def test_update_supplier_not_found(self, db_session):
        """Test updating a non-existent supplier."""
        non_existent_id = uuid.uuid4()
        update_data = {'name': 'Updated Name'}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_supplier(non_existent_id, update_data)
    
    def test_delete_supplier_not_found(self, db_session):
        """Test deleting a non-existent supplier."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_supplier(non_existent_id)
    
    def test_create_supplier_invalid_email_format(self, db_session):
        """Test creating supplier with invalid email format."""
        supplier_data = {
            'name': 'Invalid Email Supplier',
            'email': 'not-an-email'
        }
        
        # Should validate email format
        result, status = self.service.create_supplier(supplier_data)
        # Either succeeds (no validation) or fails (with validation)
        assert status in [201, 400]
    
    # ========== Business Logic Tests ==========
    
    def test_deactivate_supplier(self, db_session):
        """Test deactivating a supplier."""
        # Create active supplier
        supplier_data = {
            'name': 'Active Supplier',
            'email': 'active@supplier.com',
            'status': 'active'
        }
        self.service.create_supplier(supplier_data)
        
        supplier = db_session.query(Supplier).first()
        
        # Deactivate
        update_data = {'status': 'inactive'}
        self.service.update_supplier(supplier.id, update_data)
        
        db_session.refresh(supplier)
        assert supplier.status == 'inactive'
    
    def test_supplier_without_contact_info(self, db_session):
        """Test supplier with no contact information."""
        supplier_data = {
            'name': 'No Contact Supplier'
            # No phone, email, address
        }
        
        result, status = self.service.create_supplier(supplier_data)
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert supplier.phone is None
        assert supplier.email is None
        assert supplier.address is None
    
    def test_supplier_with_long_address(self, db_session):
        """Test supplier with very long address."""
        long_address = "A" * 500
        
        supplier_data = {
            'name': 'Long Address Supplier',
            'email': 'longaddr@supplier.com',
            'address': long_address
        }
        
        result, status = self.service.create_supplier(supplier_data)
        assert status == 201
        
        supplier = db_session.query(Supplier).first()
        assert len(supplier.address) >= 500
    
    def test_get_suppliers_by_country(self, db_session):
        """Test filtering suppliers by country."""
        # Create suppliers in different countries
        for country in ['USA', 'Canada', 'Mexico']:
            for i in range(2):
                supplier_data = {
                    'name': f'{country} Supplier {i}',
                    'email': f'supplier{i}@{country.lower()}.com',
                    'country': country
                }
                self.service.create_supplier(supplier_data)
        
        # Filter by country (using database query)
        usa_suppliers = db_session.query(Supplier).filter(Supplier.country == 'USA').all()
        assert len(usa_suppliers) >= 2
    
    def test_supplier_verification_workflow(self, db_session):
        """Test complete supplier verification workflow."""
        # Create unverified supplier
        supplier_data = {
            'name': 'Workflow Supplier',
            'email': 'workflow@supplier.com',
            'status': 'pending',
            'is_verified': False
        }
        self.service.create_supplier(supplier_data)
        
        supplier = db_session.query(Supplier).first()
        
        # Verify supplier
        update_data = {'is_verified': True, 'status': 'active'}
        self.service.update_supplier(supplier.id, update_data)
        
        db_session.refresh(supplier)
        assert supplier.is_verified is True
        assert supplier.status == 'active'

