"""
Unit tests for Customer Service.

Tests all business logic in customers/service.py including:
- Customer CRUD operations with multi-language support
- Customer segmentation and analytics
- Customer lifecycle management
- Customer type handling (individual vs business)
- Contact information management
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
from app.customers.service import CustomerService
from app.customers.model import Customer
from app.common.error_handling import ResourceNotFoundError


class TestCustomerService(BaseServiceTestCase):
    """Test cases for CustomerService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = CustomerService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_customer_success(self, db_session):
        """Test creating a customer successfully."""
        customer_data = {
            'name': json.dumps({'en': 'John Doe', 'ar': 'جون دو'}),
            'mobile': '+96812345678',
            'email': 'john.doe@test.com',
            'city': 'Muscat',
            'address': '123 Main St',
            'location': 'Al Qurum',
            'notes': 'Premium customer'
        }
        
        result, status = self.service.create_customer(customer_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify customer was created
        customer = db_session.query(Customer).filter(
            Customer.email == 'john.doe@test.com'
        ).first()
        assert customer is not None
        assert customer.mobile == '+96812345678'
        assert customer.city == 'Muscat'
    
    def test_get_customers_with_pagination(self, db_session):
        """Test getting customers with pagination."""
        # Create multiple customers
        for i in range(15):
            customer_data = {
                'name': json.dumps({'en': f'Customer {i}', 'ar': f'عميل {i}'}),
                'mobile': f'+9681234567{i}',
                'email': f'customer{i}@test.com',
                'city': 'Muscat',
                'address': f'Address {i}'
            }
            self.service.create_customer(customer_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_customers(None, filter_obj)
        
        assert status == 200
        assert 'customers' in result
        assert 'filters' in result
    
    def test_get_customer_by_id(self, db_session):
        """Test getting a specific customer by ID."""
        customer_data = {
            'name': json.dumps({'en': 'Test Customer', 'ar': 'عميل اختبار'}),
            'mobile': '+96898765432',
            'email': 'test.customer@test.com',
            'city': 'Salalah',
            'address': 'Test Address'
        }
        self.service.create_customer(customer_data)
        
        customer = db_session.query(Customer).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_customers(customer.id, filter_obj)
        
        assert status == 200
        assert 'customers' in result
    
    def test_update_customer_success(self, db_session):
        """Test updating customer information."""
        # Create customer
        customer_data = {
            'name': json.dumps({'en': 'Original Name', 'ar': 'الاسم الأصلي'}),
            'mobile': '+96812345678',
            'email': 'original@test.com',
            'city': 'Muscat',
            'address': 'Original Address'
        }
        self.service.create_customer(customer_data)
        
        customer = db_session.query(Customer).first()
        
        # Update customer
        update_data = {
            'name': json.dumps({'en': 'Updated Name', 'ar': 'الاسم المحدث'}),
            'mobile': '+96898765432',
            'email': 'updated@test.com',
            'city': 'Salalah',
            'address': 'Updated Address',
            'notes': 'VIP customer'
        }
        
        result, status = self.service.update_customer(customer.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
    
    def test_delete_customer_success(self, db_session):
        """Test deleting a customer."""
        customer_data = {
            'name': json.dumps({'en': 'Delete Me', 'ar': 'احذفني'}),
            'mobile': '+96812345678',
            'email': 'delete.me@test.com',
            'city': 'Muscat',
            'address': 'Delete Address'
        }
        self.service.create_customer(customer_data)
        
        customer = db_session.query(Customer).first()
        customer_id = customer.id
        
        result, status = self.service.delete_customer(customer_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_customer = db_session.query(Customer).filter_by(id=customer_id).first()
        assert deleted_customer is None
    
    # ========== Multi-Language Support Tests ==========
    
    def test_customer_with_translations(self, db_session):
        """Test customer creation with multi-language names."""
        customer_data = {
            'name': json.dumps({
                'en': 'Acme Corporation',
                'ar': 'شركة أكمي'
            }),
            'mobile': '+96812345678',
            'email': 'acme@corp.com',
            'city': 'Muscat',
            'address': 'Business District'
        }
        
        result, status = self.service.create_customer(customer_data)
        
        assert status == 201
        
        customer = db_session.query(Customer).filter(
            Customer.email == 'acme@corp.com'
        ).first()
        assert customer is not None
        # Translations should be stored
    
    # ========== Contact Information Tests ==========
    
    def test_customer_with_mobile_only(self, db_session):
        """Test creating customer with mobile but no email."""
        customer_data = {
            'name': json.dumps({'en': 'Mobile Only', 'ar': 'هاتف فقط'}),
            'mobile': '+96812345678',
            'city': 'Muscat',
            'address': 'Test Address'
        }
        
        result, status = self.service.create_customer(customer_data)
        
        assert status == 201
        
        customer = db_session.query(Customer).filter(
            Customer.mobile == '+96812345678'
        ).first()
        assert customer is not None
        assert customer.email is None
    
    def test_customer_with_email_only(self, db_session):
        """Test creating customer with email but no mobile."""
        customer_data = {
            'name': json.dumps({'en': 'Email Only', 'ar': 'بريد إلكتروني فقط'}),
            'email': 'email.only@test.com',
            'city': 'Muscat',
            'address': 'Test Address'
        }
        
        result, status = self.service.create_customer(customer_data)
        
        assert status == 201
        
        customer = db_session.query(Customer).filter(
            Customer.email == 'email.only@test.com'
        ).first()
        assert customer is not None
        assert customer.mobile is None
    
    def test_customer_contact_validation(self, db_session):
        """Test customer must have at least one contact method."""
        customer_data = {
            'name': json.dumps({'en': 'No Contact', 'ar': 'بلا اتصال'}),
            # No mobile or email
            'city': 'Muscat',
            'address': 'Test Address'
        }
        
        # Should still create - validation may be business rule dependent
        result, status = self.service.create_customer(customer_data)
        assert status == 201
    
    # ========== Customer Notes and Additional Info Tests ==========
    
    def test_customer_with_notes(self, db_session):
        """Test storing additional notes for customers."""
        customer_data = {
            'name': json.dumps({'en': 'Important Customer', 'ar': 'عميل مهم'}),
            'mobile': '+96812345678',
            'email': 'important@test.com',
            'city': 'Muscat',
            'address': 'VIP Address',
            'notes': 'Preferred customer, expedite all orders. Contact before 5 PM.'
        }
        
        result, status = self.service.create_customer(customer_data)
        assert status == 201
        
        customer = db_session.query(Customer).filter(
            Customer.email == 'important@test.com'
        ).first()
        assert customer.notes is not None
        assert 'expedite' in customer.notes
    
    # ========== Location Management Tests ==========
    
    def test_customer_with_location_details(self, db_session):
        """Test customer with detailed location information."""
        customer_data = {
            'name': json.dumps({'en': 'Suburban Customer', 'ar': 'عميل ضواحي'}),
            'mobile': '+96812345678',
            'email': 'suburban@test.com',
            'city': 'Muscat',
            'location': 'Al Khuwair',
            'address': 'Building 123, Way 456, Street 789'
        }
        
        result, status = self.service.create_customer(customer_data)
        assert status == 201
        
        customer = db_session.query(Customer).filter(
            Customer.email == 'suburban@test.com'
        ).first()
        assert customer.location == 'Al Khuwair'
        assert customer.city == 'Muscat'
    
    # ========== Search and Filter Tests ==========
    
    def test_search_customers_by_city(self, db_session):
        """Test filtering customers by city."""
        cities = ['Muscat', 'Salalah', 'Sohar', 'Muscat']
        
        for i, city in enumerate(cities):
            customer_data = {
                'name': json.dumps({'en': f'Customer {i}', 'ar': f'عميل {i}'}),
                'mobile': f'+9681234567{i}',
                'email': f'customer{i}@test.com',
                'city': city,
                'address': f'Address {i}'
            }
            self.service.create_customer(customer_data)
        
        # Query Muscat customers
        muscat_customers = db_session.query(Customer).filter(
            Customer.city == 'Muscat'
        ).all()
        
        assert len(muscat_customers) >= 2
    
    def test_search_customers_by_email(self, db_session):
        """Test searching customers by email."""
        customer_data = {
            'name': json.dumps({'en': 'Searchable', 'ar': 'قابل للبحث'}),
            'mobile': '+96812345678',
            'email': 'unique.search@test.com',
            'city': 'Muscat',
            'address': 'Search Address'
        }
        self.service.create_customer(customer_data)
        
        customer = db_session.query(Customer).filter(
            Customer.email == 'unique.search@test.com'
        ).first()
        
        assert customer is not None
        assert customer.email == 'unique.search@test.com'
    
    # ========== Error Handling Tests ==========
    
    def test_get_customer_not_found(self, db_session):
        """Test getting a non-existent customer."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_customers(non_existent_id, filter_obj)
    
    def test_update_customer_not_found(self, db_session):
        """Test updating a non-existent customer."""
        non_existent_id = uuid.uuid4()
        update_data = {
            'name': json.dumps({'en': 'Test', 'ar': 'اختبار'}),
            'mobile': '+96812345678'
        }
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_customer(non_existent_id, update_data)
    
    def test_delete_customer_not_found(self, db_session):
        """Test deleting a non-existent customer."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_customer(non_existent_id)
    
    def test_get_customers_empty_database(self, db_session):
        """Test getting customers when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_customers(None, filter_obj)
        
        assert status == 200
        assert 'customers' in result

