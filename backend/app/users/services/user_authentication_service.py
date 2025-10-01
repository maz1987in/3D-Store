"""
User Authentication Service

Handles user authentication, login, password management, and OAuth operations.
"""

import jwt
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from flask import current_app
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from app.common.constants import HASH_METHOD
from app.common.enum import RoleEnum
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import remove_leading_plus
from app.utilities.request_utils import not_exisit_in_request
from app.security.mail import generate_confirmation_token, send_email
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors
from app.users.repository import UserRepository
from app.users.model import User, Role, Tracking

from extensions import cache
from config import SecretKey

SECRET_KEY = SecretKey().SECRET_KEY


class UserAuthenticationService:
    """Service for user authentication and password management."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    @handle_errors("User")
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.user_repo.get_user_by_email(email)

    @handle_errors("User")
    def get_user_by_mobile(self, mobile: str) -> Optional[User]:
        """Get user by mobile number."""
        mobile = remove_leading_plus(mobile)
        return self.user_repo.get_user_by_phone(mobile)

    @handle_errors("User")
    def get_user_by_any(self, param: str, with_password: bool = False) -> tuple:
        """Get user by email or mobile."""
        mobile = remove_leading_plus(param)
        user = self.user_repo.get_user_by_email_or_phone(param, mobile)
        if user is None:
            return None, 404
        return self._get_user_model(user, with_password), 200

    @handle_errors("User")
    def get_user_admin_by_any(self, param: str, with_password: bool = False) -> tuple:
        """Get admin user by email or mobile."""
        with session_scope() as session:
            mobile = remove_leading_plus(param)
            query = session.query(User, Role).join(User.roles).options(joinedload(User.roles))
            query = query.filter(or_(User.email == param, User.phone == mobile))
            query = query.filter(not_(Role.name == RoleEnum.PUBLIC.value))
            user = query.first()
            if user is None:
                return None, 404
            return self._get_user_model(user, with_password), 200

    @handle_errors("User")
    def get_oauth_user(self, provider: str, oauth_id: str) -> Optional[User]:
        """Get OAuth user by provider and OAuth ID."""
        with session_scope() as session:
            user = session.query(User).filter(
                User.oauth_provider == provider,
                User.oauth_id == oauth_id
            ).first()
            return user

    @handle_errors("User")
    def create_oauth_user(self, data: Dict[str, Any]) -> tuple:
        """Create OAuth user."""
        with session_scope() as session:
            user = User(
                id=uuid.uuid4(),
                name=data['name'],
                email=data['email'],
                oauth_provider=data['provider'],
                oauth_id=data['oauth_id'],
                user_type='USER',
                language='ARABIC',
                phone=data.get('phone'),
                username=data['email'],
                active=1,
                agree=1,
                agree_date=datetime.now(timezone.utc)
            )

            role = session.query(Role).filter(Role.name == 'User').first()
            user.roles.append(role)

            session.add(user)
            session.commit()

            return "OAuth User Created", 201

    @handle_errors("User")
    def user_logins(self, data: Dict[str, Any]) -> tuple:
        """Record user login."""
        with session_scope() as session:
            tracking = Tracking(user_id=data['user_id'], action='login')
            session.add(tracking)
            session.commit()
            return "Login recorded", 200

    @handle_errors("User")
    def user_confirmed_mobile(self, mobile: str) -> tuple:
        """Confirm user mobile number."""
        with session_scope() as session:
            mobile = remove_leading_plus(mobile)
            user = session.query(User).filter(User.phone == mobile).first()
            if not user:
                raise ResourceNotFoundError("User")
            
            user.mobile_confirmed = 1
            user.mobile_confirmed_date = datetime.now(timezone.utc)
            session.commit()
            return "Mobile confirmed", 200

    @handle_errors("User")
    def user_confirmed(self, email: str) -> tuple:
        """Confirm user email address."""
        with session_scope() as session:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                raise ResourceNotFoundError("User")
            
            user.email_confirmed = 1
            user.email_confirmed_date = datetime.now(timezone.utc)
            user.active = 1
            session.commit()
            return "Email confirmed", 200

    @handle_errors("User")
    def update_user_password(self, user_id: str, data: Dict[str, Any]) -> tuple:
        """Update user password."""
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("User")
            
            user.password = generate_password_hash(data['new_password'], method=HASH_METHOD)
            session.commit()
            return "Password updated", 200

    @handle_errors("User")
    def forget_password(self, email: str) -> tuple:
        """Send password reset email."""
        with session_scope() as session:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return "Email not found", 404
            
            token = generate_confirmation_token(email)
            reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
            
            # Send reset email
            subject = "[Raheeq App] Password Reset Request"
            html = f"<p>Click the link to reset your password: <a href='{reset_url}'>Reset Password</a></p>"
            send_email(email, subject, html)
            
            return "Password reset email sent", 200

    @handle_errors("User")
    def show_logins(self) -> tuple:
        """Get user login history."""
        with session_scope() as session:
            logins = session.query(Tracking).filter(Tracking.action == 'login').all()
            return [login.json() for login in logins], 200

    def _get_user_model(self, user, with_password=False):
        """Helper method to convert user to model format."""
        if hasattr(user, 'User'):
            data = user.User.json(with_password=with_password)
            if hasattr(user, 'Role'):
                data['roles'] = [role.name for role in user.Role] if isinstance(user.Role, list) else [user.Role.name]
            return data
        else:
            data = user.json(with_password=with_password)
            return data
