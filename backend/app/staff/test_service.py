"""
Unit tests for Staff Service.

Tests all business logic in staff/service.py including:
- Staff CRUD operations
- Staff-user associations
- Staff-branch assignments
- Salary management
- ID card expiry tracking
- Edge cases and error handling
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import assert_decimal_equal, create_mock_filter
from app.staff.service import StaffService
from app.staff.model import Staff
from app.common.error_handling import ResourceNotFoundError


class TestStaffService(BaseServiceTestCase):
    """Test cases for StaffService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = StaffService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_staff_success(self, db_session, sample_user, sample_branch):
        """Test creating a staff record successfully."""
        staff_data = {
            'user_id': sample_user.id,
            'nationality': 'Omani',
            'name': 'John Doe',
            'id_card_number': 'ID123456',
            'expiry_date': '2025-12-31',
            'salary': 2500.00,
            'branch_id': sample_branch.id
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        
        result, status = self.service.create_staff(staff_data, files)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify staff was created
        staff = db_session.query(Staff).filter(
            Staff.id_card_number == 'ID123456'
        ).first()
        assert staff is not None
        assert staff.name == 'John Doe'
        assert_decimal_equal(staff.salary, 2500.00)
    
    def test_get_staffs_with_pagination(self, db_session, sample_branch):
        """Test getting staff records with pagination."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        from werkzeug.datastructures import ImmutableMultiDict
        
        files = ImmutableMultiDict([])
        
        # Create multiple staff records
        for i in range(10):
            user = User(
                username=f'staffuser{i}',
                phone=f'+777777777{i}',
                email=f'staff{i}@test.com',
                password=generate_password_hash('test'),
                active=True
            )
            db_session.add(user)
            db_session.commit()
            
            staff_data = {
                'user_id': user.id,
                'name': f'Staff {i}',
                'id_card_number': f'ID{i:05d}',
                'expiry_date': '2025-12-31',
                'salary': 1000.00 * (i + 1),
                'branch_id': sample_branch.id
            }
            self.service.create_staff(staff_data, files)
        
        filter_obj = create_mock_filter(page=1, per_page=5)
        result, status = self.service.get_staffs(None, filter_obj)
        
        assert status == 200
        assert 'staffs' in result
        assert 'filters' in result
    
    def test_update_staff_success(self, db_session, sample_user, sample_branch):
        """Test updating a staff record."""
        # Create staff
        staff_data = {
            'user_id': sample_user.id,
            'name': 'Original Name',
            'id_card_number': 'ID999',
            'expiry_date': '2025-12-31',
            'salary': 2000.00,
            'branch_id': sample_branch.id
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        self.service.create_staff(staff_data, files)
        
        staff = db_session.query(Staff).first()
        
        # Update staff
        update_data = {
            'name': 'Updated Name',
            'salary': 2500.00,
            'expiry_date': '2026-12-31'
        }
        
        result, status = self.service.update_staff(staff.id, update_data, files)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(staff)
        assert staff.name == 'Updated Name'
        assert_decimal_equal(staff.salary, 2500.00)
    
    def test_delete_staff_success(self, db_session, sample_user, sample_branch):
        """Test deleting a staff record."""
        staff_data = {
            'user_id': sample_user.id,
            'name': 'Delete Me',
            'id_card_number': 'IDDEL',
            'expiry_date': '2025-12-31',
            'salary': 2000.00,
            'branch_id': sample_branch.id
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        self.service.create_staff(staff_data, files)
        
        staff = db_session.query(Staff).first()
        staff_id = staff.id
        
        result, status = self.service.delete_staff(staff_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_staff = db_session.query(Staff).filter_by(id=staff_id).first()
        assert deleted_staff is None
    
    # ========== Salary Tests ==========
    
    def test_staff_with_zero_salary(self, db_session, sample_user, sample_branch):
        """Test staff with zero salary."""
        staff_data = {
            'user_id': sample_user.id,
            'name': 'Volunteer',
            'id_card_number': 'IDVOL',
            'expiry_date': '2025-12-31',
            'salary': 0.00,
            'branch_id': sample_branch.id
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        result, status = self.service.create_staff(staff_data, files)
        
        assert status == 201
        staff = db_session.query(Staff).first()
        assert staff.salary == 0.00
    
    def test_staff_salary_update(self, db_session, sample_user, sample_branch):
        """Test updating staff salary."""
        staff_data = {
            'user_id': sample_user.id,
            'name': 'Salary Test',
            'id_card_number': 'IDSAL',
            'expiry_date': '2025-12-31',
            'salary': 2000.00,
            'branch_id': sample_branch.id
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        self.service.create_staff(staff_data, files)
        
        staff = db_session.query(Staff).first()
        
        # Give raise
        update_data = {'salary': 2500.00, 'expiry_date': '2025-12-31'}
        self.service.update_staff(staff.id, update_data, files)
        
        db_session.refresh(staff)
        assert_decimal_equal(staff.salary, 2500.00)
    
    # ========== ID Card Expiry Tests ==========
    
    def test_staff_with_future_expiry(self, db_session, sample_user, sample_branch):
        """Test staff with future ID card expiry."""
        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        staff_data = {
            'user_id': sample_user.id,
            'name': 'Future Expiry',
            'id_card_number': 'IDFUT',
            'expiry_date': future_date,
            'salary': 2000.00,
            'branch_id': sample_branch.id
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        result, status = self.service.create_staff(staff_data, files)
        
        assert status == 201
    
    def test_staff_with_expired_id(self, db_session, sample_user, sample_branch):
        """Test staff with expired ID card."""
        past_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        staff_data = {
            'user_id': sample_user.id,
            'name': 'Expired ID',
            'id_card_number': 'IDEXP',
            'expiry_date': past_date,
            'salary': 2000.00,
            'branch_id': sample_branch.id
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        result, status = self.service.create_staff(staff_data, files)
        
        # Should create but might flag as expired
        assert status == 201
    
    # ========== Error Handling Tests ==========
    
    def test_create_staff_missing_required_fields(self, db_session):
        """Test creating staff with missing required fields."""
        incomplete_data = {
            'name': 'Incomplete Staff'
            # Missing expiry_date and other fields
        }
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        
        with pytest.raises(Exception):
            self.service.create_staff(incomplete_data, files)
    
    def test_get_staff_not_found(self, db_session):
        """Test getting a non-existent staff record."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_staffs(non_existent_id, filter_obj)
    
    def test_update_staff_not_found(self, db_session):
        """Test updating a non-existent staff record."""
        non_existent_id = uuid.uuid4()
        update_data = {'salary': 3000.00, 'expiry_date': '2025-12-31'}
        
        from werkzeug.datastructures import ImmutableMultiDict
        files = ImmutableMultiDict([])
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_staff(non_existent_id, update_data, files)
    
    def test_delete_staff_not_found(self, db_session):
        """Test deleting a non-existent staff record."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_staff(non_existent_id)

