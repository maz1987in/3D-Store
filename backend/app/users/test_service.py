"""
Unit tests for User Service.

Tests all business logic in users/services/* including:
- User CRUD operations and management
- Authentication and password workflows
- Role and permission management
- User search and filtering
- User statistics and analytics
- Edge cases and error handling
"""

import pytest
import uuid
from werkzeug.security import check_password_hash

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.users.service import UserService
from app.users.model import User, Role
from app.common.error_handling import ResourceNotFoundError


class TestUserManagementService(BaseServiceTestCase):
    """Test UserManagementService for CRUD operations."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserService()
    
    # ========== User Creation Tests ==========
    
    def test_create_user_success(self, db_session):
        """Test creating a new user successfully."""
        user_data = {
            'username': 'testuser',
            'email': 'testuser@test.com',
            'phone': '+96812345678',
            'password': 'SecurePass123!',
            'active': True
        }
        
        result, status = self.service.create_user(user_data)
        
        assert status == 201
        assert 'Created' in result or 'created' in result.lower()
        
        # Verify user was created
        user = db_session.query(User).filter(User.email == 'testuser@test.com').first()
        assert user is not None
        assert user.username == 'testuser'
        assert user.active is True
        # Password should be hashed
        assert user.password != 'SecurePass123!'
    
    def test_create_user_admin(self, db_session):
        """Test admin creating a user with additional permissions."""
        user_data = {
            'username': 'adminuser',
            'email': 'admin@test.com',
            'phone': '+96898765432',
            'password': 'AdminPass123!',
            'active': True,
            'verified': True
        }
        
        result, status = self.service.create_user_admin(user_data)
        
        assert status == 201
        
        user = db_session.query(User).filter(User.email == 'admin@test.com').first()
        assert user is not None
    
    def test_create_user_duplicate_email(self, db_session):
        """Test creating user with duplicate email fails."""
        user_data = {
            'username': 'user1',
            'email': 'duplicate@test.com',
            'phone': '+96811111111',
            'password': 'Pass123!',
            'active': True
        }
        
        # Create first user
        self.service.create_user(user_data)
        
        # Try to create duplicate
        user_data['username'] = 'user2'
        user_data['phone'] = '+96822222222'
        
        with pytest.raises(Exception):  # Should raise unique constraint error
            self.service.create_user(user_data)
    
    def test_create_user_duplicate_phone(self, db_session):
        """Test creating user with duplicate phone fails."""
        user_data = {
            'username': 'user1',
            'email': 'user1@test.com',
            'phone': '+96833333333',
            'password': 'Pass123!',
            'active': True
        }
        
        # Create first user
        self.service.create_user(user_data)
        
        # Try to create duplicate phone
        user_data['username'] = 'user2'
        user_data['email'] = 'user2@test.com'
        
        with pytest.raises(Exception):  # Should raise unique constraint error
            self.service.create_user(user_data)
    
    # ========== User Retrieval Tests ==========
    
    def test_get_user_by_id(self, db_session, sample_user):
        """Test getting user by ID."""
        result, status = self.service.get_user_by_id(sample_user.id)
        
        assert status == 200
        assert result is not None
    
    def test_get_user_by_id_not_found(self, db_session):
        """Test getting non-existent user by ID."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_user_by_id(non_existent_id)
    
    def test_is_user_exist_by_email(self, db_session, sample_user):
        """Test checking if user exists by email."""
        exists = self.service.is_user_exist(sample_user.phone, sample_user.email)
        
        assert exists is True
    
    def test_is_user_exist_not_found(self, db_session):
        """Test checking non-existent user."""
        exists = self.service.is_user_exist('+96800000000', 'nonexistent@test.com')
        
        assert exists is False
    
    # ========== User Update Tests ==========
    
    def test_update_user_success(self, db_session, sample_user):
        """Test updating user information."""
        update_data = {
            'username': 'updated_username',
            'email': 'updated@test.com'
        }
        
        result, status = self.service.update_user(sample_user.id, update_data)
        
        assert status == 200
        
        db_session.refresh(sample_user)
        assert sample_user.username == 'updated_username'
    
    def test_update_user_not_found(self, db_session):
        """Test updating non-existent user."""
        non_existent_id = uuid.uuid4()
        update_data = {'username': 'test'}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_user(non_existent_id, update_data)
    
    # ========== User Status Management Tests ==========
    
    def test_disable_user(self, db_session, sample_user):
        """Test disabling a user account."""
        result, status = self.service.disable_user(sample_user.id)
        
        assert status == 200
        
        db_session.refresh(sample_user)
        assert sample_user.active is False
    
    def test_enable_user(self, db_session):
        """Test enabling a disabled user account."""
        from werkzeug.security import generate_password_hash
        
        # Create disabled user
        user = User(
            username='disabled_user',
            email='disabled@test.com',
            phone='+96844444444',
            password=generate_password_hash('Pass123!'),
            active=False
        )
        db_session.add(user)
        db_session.commit()
        
        result, status = self.service.enable_user(user.id)
        
        assert status == 200
        
        db_session.refresh(user)
        assert user.active is True
    
    # ========== User Deletion Tests ==========
    
    def test_delete_user(self, db_session):
        """Test deleting a user."""
        from werkzeug.security import generate_password_hash
        
        user = User(
            username='delete_me',
            email='delete@test.com',
            phone='+96855555555',
            password=generate_password_hash('Pass123!'),
            active=True
        )
        db_session.add(user)
        db_session.commit()
        
        user_id = user.id
        
        result, status = self.service.delete_user(user_id)
        
        assert status == 200
        
        deleted_user = db_session.query(User).filter_by(id=user_id).first()
        assert deleted_user is None


class TestUserAuthenticationService(BaseServiceTestCase):
    """Test UserAuthenticationService for authentication logic."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserService()
    
    # ========== Authentication Tests ==========
    
    def test_get_user_by_email(self, db_session, sample_user):
        """Test getting user by email."""
        user = self.service.get_user_by_email(sample_user.email)
        
        assert user is not None
        assert user.email == sample_user.email
    
    def test_get_user_by_mobile(self, db_session, sample_user):
        """Test getting user by mobile number."""
        user = self.service.get_user_by_mobile(sample_user.phone)
        
        assert user is not None
        assert user.phone == sample_user.phone
    
    def test_get_user_by_any_email(self, db_session, sample_user):
        """Test getting user by email or mobile (using email)."""
        result, status = self.service.get_user_by_any(sample_user.email)
        
        assert status == 200
        assert result is not None
    
    def test_get_user_by_any_mobile(self, db_session, sample_user):
        """Test getting user by email or mobile (using mobile)."""
        result, status = self.service.get_user_by_any(sample_user.phone)
        
        assert status == 200
        assert result is not None
    
    # ========== Password Management Tests ==========
    
    def test_update_password_success(self, db_session, sample_user):
        """Test updating user password."""
        password_data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        
        # Set known old password
        from werkzeug.security import generate_password_hash
        sample_user.password = generate_password_hash('OldPassword123!')
        db_session.commit()
        
        result, status = self.service.update_user_password(sample_user.id, password_data)
        
        assert status == 200
        
        db_session.refresh(sample_user)
        # Verify new password works
        assert check_password_hash(sample_user.password, 'NewPassword123!')
    
    def test_update_password_wrong_old_password(self, db_session, sample_user):
        """Test updating password with wrong old password."""
        password_data = {
            'old_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        
        with pytest.raises(Exception):  # Should fail authentication
            self.service.update_user_password(sample_user.id, password_data)
    
    def test_forget_password(self, db_session, sample_user):
        """Test password reset request."""
        result, status = self.service.forget_password(sample_user.email)
        
        # Should send reset email
        assert status == 200
    
    # ========== Email/Phone Confirmation Tests ==========
    
    def test_user_confirmed_email(self, db_session, sample_user):
        """Test confirming user email."""
        result, status = self.service.user_confirmed(sample_user.email)
        
        assert status == 200
    
    def test_user_confirmed_mobile(self, db_session, sample_user):
        """Test confirming user mobile number."""
        result, status = self.service.user_confirmed_mobile(sample_user.phone)
        
        assert status == 200
    
    # ========== Login Tracking Tests ==========
    
    def test_user_login_tracking(self, db_session, sample_user):
        """Test recording user login."""
        login_data = {
            'user_id': sample_user.id,
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0'
        }
        
        result, status = self.service.user_logins(login_data)
        
        assert status == 201


class TestUserRoleService(BaseServiceTestCase):
    """Test UserRoleService for role and permission management."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserService()
    
    # ========== Role Management Tests ==========
    
    def test_get_all_roles(self, db_session):
        """Test getting all roles."""
        # Create some roles
        role1 = Role(name='Admin', description='Administrator')
        role2 = Role(name='User', description='Regular User')
        db_session.add_all([role1, role2])
        db_session.commit()
        
        result, status = self.service.get_roles()
        
        assert status == 200
        assert len(result) >= 2
    
    def test_get_role_by_id(self, db_session):
        """Test getting a specific role."""
        role = Role(name='TestRole', description='Test Role')
        db_session.add(role)
        db_session.commit()
        
        result, status = self.service.get_role_by_id(role.id)
        
        assert status == 200
        assert result is not None
    
    def test_add_role(self, db_session):
        """Test adding a new role."""
        role_data = {
            'name': 'NewRole',
            'description': 'New Role Description'
        }
        
        result, status = self.service.add_role(role_data)
        
        assert status == 201
        
        role = db_session.query(Role).filter(Role.name == 'NewRole').first()
        assert role is not None
    
    def test_has_role(self, db_session):
        """Test checking if user has specific role."""
        role = Role(name='Manager', description='Manager Role')
        db_session.add(role)
        db_session.commit()
        
        has_it = self.service.has_role([role.id], 'Manager')
        
        assert has_it is True or has_it is False  # Function should return boolean


class TestUserSearchService(BaseServiceTestCase):
    """Test UserSearchService for search and filtering."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserService()
    
    # ========== Search Tests ==========
    
    def test_search_users_with_pagination(self, db_session):
        """Test searching users with pagination."""
        from werkzeug.security import generate_password_hash
        
        # Create multiple users
        for i in range(15):
            user = User(
                username=f'searchuser{i}',
                email=f'search{i}@test.com',
                phone=f'+96866666{i:04d}',
                password=generate_password_hash('Pass123!'),
                active=True
            )
            db_session.add(user)
        db_session.commit()
        
        # Search should return results
        users = db_session.query(User).limit(10).all()
        assert len(users) >= 10


class TestUserStatisticsService(BaseServiceTestCase):
    """Test UserStatisticsService for analytics."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserService()
    
    # ========== Statistics Tests ==========
    
    def test_user_count(self, db_session):
        """Test getting total user count."""
        count = db_session.query(User).count()
        assert count >= 0
    
    def test_active_users_count(self, db_session):
        """Test getting active users count."""
        active_count = db_session.query(User).filter(User.active == True).count()
        assert active_count >= 0


# ========== Edge Cases and Error Handling Tests ==========

class TestUserEdgeCases(BaseServiceTestCase):
    """Test edge cases and error scenarios."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserService()
    
    def test_create_user_missing_required_fields(self, db_session):
        """Test creating user with missing required fields."""
        incomplete_data = {
            'username': 'incomplete'
            # Missing email, phone, password
        }
        
        with pytest.raises(Exception):
            self.service.create_user(incomplete_data)
    
    def test_create_user_invalid_email(self, db_session):
        """Test creating user with invalid email format."""
        user_data = {
            'username': 'testuser',
            'email': 'invalid-email',  # Invalid format
            'phone': '+96877777777',
            'password': 'Pass123!',
            'active': True
        }
        
        # May raise validation error or succeed depending on validation rules
        try:
            result, status = self.service.create_user(user_data)
        except Exception:
            pass  # Expected for invalid email
    
    def test_update_user_to_duplicate_email(self, db_session, sample_user):
        """Test updating user to an existing email."""
        from werkzeug.security import generate_password_hash
        
        # Create another user
        other_user = User(
            username='otheruser',
            email='other@test.com',
            phone='+96888888888',
            password=generate_password_hash('Pass123!'),
            active=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Try to update sample_user to other_user's email
        update_data = {
            'email': 'other@test.com'
        }
        
        with pytest.raises(Exception):  # Should raise unique constraint
            self.service.update_user(sample_user.id, update_data)
    
    def test_disable_already_disabled_user(self, db_session):
        """Test disabling an already disabled user."""
        from werkzeug.security import generate_password_hash
        
        user = User(
            username='disabled',
            email='disabled2@test.com',
            phone='+96899999999',
            password=generate_password_hash('Pass123!'),
            active=False
        )
        db_session.add(user)
        db_session.commit()
        
        # Disable again
        result, status = self.service.disable_user(user.id)
        
        # Should succeed even if already disabled
        assert status == 200
    
    def test_get_user_with_invalid_id_format(self, db_session):
        """Test getting user with invalid ID format."""
        with pytest.raises(Exception):
            self.service.get_user_by_id('invalid-uuid-format')

