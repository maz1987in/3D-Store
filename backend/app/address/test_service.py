"""
Unit tests for Shipping Address Service.

Tests all business logic in address/service.py including:
- Shipping address CRUD operations
- Address validation
- Default address management
- User address management
- International vs domestic addresses
- Edge cases and error handling
"""

import pytest
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.address.service import ShippingAddressService
from app.address.model import ShippingAddress
from app.common.error_handling import ResourceNotFoundError


class TestShippingAddressService(BaseServiceTestCase):
    """Test cases for ShippingAddressService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = ShippingAddressService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_add_address_success(self, db_session, sample_user):
        """Test adding a shipping address successfully."""
        address_data = {
            'address_line1': '123 Main Street',
            'address_line2': 'Apt 4B',
            'city': 'Muscat',
            'state': 'Muscat Governorate',
            'postal_code': '100',
            'country': 'Oman',
            'phone': '+96812345678',
            'label': 'Home'
        }
        
        result, status = self.service.add_address(sample_user.id, address_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify address was created
        address = db_session.query(ShippingAddress).filter(
            ShippingAddress.user_id == sample_user.id
        ).first()
        assert address is not None
        assert address.address_line1 == '123 Main Street'
        assert address.city == 'Muscat'
        assert address.country == 'Oman'
    
    def test_add_address_minimal_data(self, db_session, sample_user):
        """Test adding address with minimal required data."""
        address_data = {
            'address_line1': '456 Simple Street',
            'city': 'TestCity'
        }
        
        result, status = self.service.add_address(sample_user.id, address_data)
        
        assert status == 201
        
        address = db_session.query(ShippingAddress).first()
        assert address.address_line1 == '456 Simple Street'
        assert address.country == 'Oman'  # Default value
    
    def test_get_addresses_with_pagination(self, db_session, sample_user):
        """Test getting addresses with pagination."""
        # Create multiple addresses
        for i in range(8):
            address_data = {
                'address_line1': f'{i * 100 + 100} Street {i}',
                'city': 'TestCity',
                'label': f'Address {i}'
            }
            self.service.add_address(sample_user.id, address_data)
        
        filter_obj = create_mock_filter(page=1, per_page=5)
        result, status = self.service.get_addresses(None, filter_obj)
        
        assert status == 200
        assert 'addresses' in result
        assert 'filters' in result
        assert len(result['addresses']) == 5
    
    def test_get_address_by_id(self, db_session, sample_user):
        """Test getting a specific address by ID."""
        address_data = {
            'address_line1': '789 Test Avenue',
            'city': 'TestCity',
            'label': 'Office'
        }
        self.service.add_address(sample_user.id, address_data)
        
        address = db_session.query(ShippingAddress).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_addresses(address.id, filter_obj)
        
        assert status == 200
        assert 'addresses' in result
        assert result['addresses']['address_line1'] == '789 Test Avenue'
    
    def test_get_user_addresses(self, db_session, sample_user):
        """Test getting all addresses for a user."""
        # Create multiple addresses for user
        for i in range(3):
            address_data = {
                'address_line1': f'Address {i}',
                'city': 'TestCity',
                'label': f'Label {i}'
            }
            self.service.add_address(sample_user.id, address_data)
        
        filter_obj = create_mock_filter()
        result, status = self.service.get_user_addresses(sample_user.id, filter_obj)
        
        assert status == 200
        assert len(result['addresses']) >= 3
    
    def test_update_address_success(self, db_session, sample_user):
        """Test updating a shipping address."""
        # Create address
        address_data = {
            'address_line1': 'Original Street',
            'city': 'OldCity',
            'postal_code': '100'
        }
        self.service.add_address(sample_user.id, address_data)
        
        address = db_session.query(ShippingAddress).first()
        
        # Update address
        update_data = {
            'address_line1': 'Updated Street',
            'city': 'NewCity',
            'postal_code': '200'
        }
        
        result, status = self.service.update_address(address.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(address)
        assert address.address_line1 == 'Updated Street'
        assert address.city == 'NewCity'
        assert address.postal_code == '200'
    
    def test_delete_address_success(self, db_session, sample_user):
        """Test deleting a shipping address."""
        address_data = {
            'address_line1': 'Delete Me Street',
            'city': 'TestCity'
        }
        self.service.add_address(sample_user.id, address_data)
        
        address = db_session.query(ShippingAddress).first()
        address_id = address.id
        
        result, status = self.service.delete_address(address_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_address = db_session.query(ShippingAddress).filter_by(id=address_id).first()
        assert deleted_address is None
    
    # ========== Default Address Tests ==========
    
    def test_set_default_address(self, db_session, sample_user):
        """Test setting a default address."""
        # Create multiple addresses
        for i in range(3):
            address_data = {
                'address_line1': f'Address {i}',
                'city': 'TestCity',
                'is_default': (i == 1)  # Second one is default
            }
            self.service.add_address(sample_user.id, address_data)
        
        # Get addresses
        addresses = db_session.query(ShippingAddress).filter(
            ShippingAddress.user_id == sample_user.id
        ).all()
        
        default_addresses = [a for a in addresses if a.is_default]
        assert len(default_addresses) <= 1  # Should have at most one default
    
    def test_get_default_address(self, db_session, sample_user):
        """Test getting user's default address."""
        # Create addresses with one as default
        for i in range(3):
            address_data = {
                'address_line1': f'Address {i}',
                'city': 'TestCity',
                'is_default': (i == 2)  # Last one is default
            }
            self.service.add_address(sample_user.id, address_data)
        
        result, status = self.service.get_default_address(sample_user.id)
        
        assert status == 200
        assert result is not None
    
    # ========== Validation Tests ==========
    
    def test_address_with_missing_postal_code(self, db_session, sample_user):
        """Test address without postal code."""
        address_data = {
            'address_line1': '123 No Postal Street',
            'city': 'TestCity'
            # No postal_code
        }
        
        result, status = self.service.add_address(sample_user.id, address_data)
        assert status == 201
        
        address = db_session.query(ShippingAddress).first()
        assert address.postal_code is None
    
    def test_international_address(self, db_session, sample_user):
        """Test international shipping address."""
        address_data = {
            'address_line1': '456 International Blvd',
            'city': 'Dubai',
            'state': 'Dubai',
            'postal_code': '12345',
            'country': 'UAE',
            'phone': '+97112345678'
        }
        
        result, status = self.service.add_address(sample_user.id, address_data)
        assert status == 201
        
        address = db_session.query(ShippingAddress).first()
        assert address.country == 'UAE'
        assert address.city == 'Dubai'
    
    def test_address_with_long_street_name(self, db_session, sample_user):
        """Test address with very long street name."""
        long_street = "A" * 300
        
        address_data = {
            'address_line1': long_street,
            'city': 'TestCity'
        }
        
        result, status = self.service.add_address(sample_user.id, address_data)
        assert status == 201
        
        address = db_session.query(ShippingAddress).first()
        assert len(address.address_line1) >= 200
    
    def test_address_with_special_characters(self, db_session, sample_user):
        """Test address with special characters."""
        address_data = {
            'address_line1': "O'Reilly St. & Co., Apt #5-B",
            'city': "Saint-Denis",
            'country': 'France'
        }
        
        result, status = self.service.add_address(sample_user.id, address_data)
        assert status == 201
        
        address = db_session.query(ShippingAddress).first()
        assert "O'Reilly" in address.address_line1
    
    def test_multiple_users_separate_addresses(self, db_session):
        """Test that different users have separate address lists."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        # Create two users
        user1 = User(
            username='addruser1',
            phone='+6666666661',
            email='addr1@test.com',
            password=generate_password_hash('test'),
            active=True
        )
        user2 = User(
            username='addruser2',
            phone='+6666666662',
            email='addr2@test.com',
            password=generate_password_hash('test'),
            active=True
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        # Add addresses for both
        for user in [user1, user2]:
            address_data = {
                'address_line1': f'Address for {user.username}',
                'city': 'TestCity'
            }
            self.service.add_address(user.id, address_data)
        
        # Verify separate addresses
        filter_obj = create_mock_filter()
        user1_addresses, _ = self.service.get_user_addresses(user1.id, filter_obj)
        user2_addresses, _ = self.service.get_user_addresses(user2.id, filter_obj)
        
        assert len(user1_addresses['addresses']) > 0
        assert len(user2_addresses['addresses']) > 0
    
    # ========== Error Handling Tests ==========
    
    def test_add_address_invalid_user(self, db_session):
        """Test adding address for non-existent user."""
        address_data = {
            'address_line1': '123 Test Street',
            'city': 'TestCity'
        }
        
        non_existent_user_id = uuid.uuid4()
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.add_address(non_existent_user_id, address_data)
    
    def test_update_address_not_found(self, db_session):
        """Test updating a non-existent address."""
        non_existent_id = uuid.uuid4()
        update_data = {'city': 'NewCity'}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_address(non_existent_id, update_data)
    
    def test_delete_address_not_found(self, db_session):
        """Test deleting a non-existent address."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_address(non_existent_id)
    
    def test_get_address_by_invalid_id(self, db_session):
        """Test getting address with non-existent ID."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_addresses(non_existent_id, filter_obj)
    
    def test_get_addresses_empty_user(self, db_session, sample_user):
        """Test getting addresses when user has none."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_user_addresses(sample_user.id, filter_obj)
        
        assert status == 200
        assert 'addresses' in result
        assert len(result['addresses']) == 0

