"""
User Management Service

Handles core user CRUD operations, user creation, updates, and basic user management.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from flask import url_for, render_template
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from app.common.enum import RoleEnum
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import get_random_value, remove_leading_plus
from app.utilities.request_utils import not_exisit_in_request, str_to_bool
from app.security.mail import generate_confirmation_token, send_email
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors
from app.users.repository import UserRepository
from app.users.model import User, Role


class UserManagementService:
    """Service for core user management operations."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def get_user_model(self, users, with_password=False):
        """Convert user objects to JSON format."""
        if isinstance(users, list):
            result = []
            for user in users:
                if hasattr(user, 'User'):
                    data = user.User.json(with_password=with_password)
                    if hasattr(user, 'Role'):
                        data['roles'] = [role.name for role in user.Role] if isinstance(user.Role, list) else [user.Role.name]
                    result.append(data)
                else:
                    data = user.json(with_password=with_password)
                    if hasattr(user, 'Role'):
                        data['roles'] = [role.name for role in user.Role] if isinstance(user.Role, list) else [user.Role.name]
                    result.append(data)
            return result
        else:
            if hasattr(users, 'User'):
                data = users.User.json(with_password=with_password)
                if hasattr(users, 'Role'):
                    data['roles'] = [role.name for role in users.Role] if isinstance(users.Role, list) else [users.Role.name]
                return data
            else:
                data = users.json(with_password=with_password)
            return data

    @handle_errors("User")
    def is_user_exist(self, phone: str, email: Optional[str] = None) -> bool:
        """Check if user exists by phone or email."""
        # Check by phone first
        user = self.user_repo.get_user_by_phone(phone)
        if user:
            return True
        
        # Check by email if provided
        if email:
            user = self.user_repo.get_user_by_email(email)
            return user is not None
        
        return False

    @handle_errors("User")
    def is_user_id_exist(self, user_id: str, user_type: str) -> bool:
        """Check if user with same user_id and user_type exists."""
        user = self.user_repo.get_user_by_user_id_and_type(user_id, user_type)
        return user is not None

    @handle_errors("User")
    def create_user(self, data: Dict[str, Any]) -> tuple:
        """Create a new user (sign-up)."""
        phone = '{0}{1}'.format(data['code'], remove_leading_plus(data['phone']))
        phone = remove_leading_plus(phone)
        email = data['email'] if data['email'] is not None else None
        user_type = not_exisit_in_request(data, 'user_type', 'USER')
        
        if user_type not in ['USER', 'CORPORATE', 'OWNER']:
            return 'Invalid user type', 400

        if self.is_user_exist(phone, email):
            return 'User already exists', 409
        if 'user_id' in data and self.is_user_id_exist(data['user_id'], user_type):
            return 'User ID already exists', 409

        # Prepare user data for repository
        user_data = {
            'id': uuid.uuid4(),
            'password': data['password'],
            'name': not_exisit_in_request(data, 'name', None),
            'email': email,
            'user_type': user_type,
            'user_details': data['user_details'],
            'language': not_exisit_in_request(data, 'language', 'ARABIC'),
            'user_id': not_exisit_in_request(data, 'user_id', None),
            'phone': phone,
            'username': phone,
            'active': 0,
            'agree': data['agree'],
            'agree_date': datetime.now(timezone.utc)
        }

        # Create user using repository
        user = self.user_repo.create(user_data)

        # Add role using repository
        role_type = data['role'] if data['role'] is not None else 'User'
        self.user_repo.add_role_to_user(user.id, role_type)

        if user:
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('signup.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "[Raheeq App] Please Verify Your Email Address."
            send_email(user.email, subject, html)

        return "Confirmation Email Sent", 200

    @handle_errors("User")
    def create_user_admin(self, data: Dict[str, Any]) -> tuple:
        """Create a new user by admin."""
        with session_scope() as session:
            phone = '{0}{1}'.format(data['code'], remove_leading_plus(data['phone'])) if 'code' in data else remove_leading_plus(data['phone'])
            phone = remove_leading_plus(phone)
            user = User(
                id=uuid.uuid4(),
                password=not_exisit_in_request(data, 'password', get_random_value(8)),
                name=not_exisit_in_request(data, 'name', None),
                email=data['email'],
                user_type=not_exisit_in_request(data, 'user_type'),
                language=not_exisit_in_request(data, 'language', 'ARABIC'),
                phone=phone,
                username=data['username'],
                user_id=not_exisit_in_request(data, 'user_id'),
                user_details=data['user_details'],
                active=str_to_bool(data, 'is_active', False)
            )

            role_type = data['role'] if data['role'] is not None else 'Public'
            role = session.query(Role).filter(Role.name == role_type).first()
            user.roles.append(role)

            session.add(user)
            session.commit()

            return "User Created.", 201

    @handle_errors("User")
    def update_user(self, user_id: str, data: Dict[str, Any]) -> tuple:
        """Update user information."""
        with session_scope() as session:
            user_type = not_exisit_in_request(data, 'user_type', 'USER')
            if user_type not in ['USER', 'CORPORATE', 'OWNER']:
                return 'Invalid user type', 400

            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("User")
                
            user.user_details = data['user_details']
            user.name = not_exisit_in_request(data, 'name', user.name)

            session.commit()
            return "User Updated.", 200

    @handle_errors("User")
    def update_user_admin(self, user_id: str, data: Dict[str, Any]) -> tuple:
        """Update user information by admin."""
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("User")
            
            role = session.query(Role).filter(Role.name == user.roles[0].name).first()
            user.roles.remove(role)

            user.active = str_to_bool(data, 'is_active', user.active)
            user.name = not_exisit_in_request(data, 'name', user.name)
            user.email = not_exisit_in_request(data, 'email', user.email)
            user.user_type = not_exisit_in_request(data, 'user_type', user.user_type)
            user.user_details = not_exisit_in_request(data, 'user_details', user.user_details)
            user.language = not_exisit_in_request(data, 'language', user.language)
            user.user_id = not_exisit_in_request(data, 'user_id', user.user_id)
            user.phone = not_exisit_in_request(data, 'phone', user.phone)
            user.username = not_exisit_in_request(data, 'username', user.username)

            new_role = session.query(Role).filter(Role.name == data['role']).first()
            user.roles.append(new_role)

            session.commit()
            return "User Updated.", 200

    @handle_errors("User")
    def add_user_id_image(self, user_id: str, image: str, replace: bool = False) -> tuple:
        """Add or replace user ID image."""
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("User")

            if user.user_id_image and replace:
                user.user_id_image = image
            elif not user.user_id_image:
                user.user_id_image = image
            else:
                return 'Image already added', 401

            session.commit()
            return "User Updated.", 200

    @handle_errors("User")
    def get_user_by_id(self, user_id: str) -> tuple:
        """Get user by ID."""
        user = self.user_repo.get_user_with_roles(user_id)
        if user is None:
            return None, 404
        return self.get_user_model(user), 200

    @handle_errors("User")
    def get_user_json_by_id(self, user_id: str) -> tuple:
        """Get user JSON by ID."""
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            return None, 404
        return user.json(), 200

    @handle_errors("User")
    def delete_user(self, user_id: str) -> tuple:
        """Delete user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User")
        
        self.user_repo.delete(user_id)
        return "User deleted", 200

    @handle_errors("User")
    def disable_user(self, user_id: str) -> tuple:
        """Disable user account."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User")
        
        self.user_repo.update(user_id, {'active': 0})
        return "User disabled", 200

    @handle_errors("User")
    def enable_user(self, user_id: str) -> tuple:
        """Enable user account."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User")
        
        self.user_repo.update(user_id, {'active': 1})
        return "User enabled", 200
