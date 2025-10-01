"""
User Repository

This module provides the UserRepository class that implements data access
operations specific to the User entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.users.model import User
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope
from app.common.enum import UserTypeEnum, LanguageEnum
from datetime import datetime, timezone

class UserRepository(BaseRepository[User]):
    """
    Repository class for User entity operations.
    
    Extends BaseRepository with User-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(User)
    
    @handle_errors("UserRepository")
    def get_user_by_username(self, username: str, session: Optional[Session] = None) -> Optional[User]:
        """
        Retrieve a user by username.
        
        Args:
            username: The username to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The user if found, None otherwise
        """
        if session:
            return session.query(User).filter_by(username=username).first()
        
        with session_scope() as session:
            return session.query(User).filter_by(username=username).first()
    
    @handle_errors("UserRepository")
    def get_user_by_email(self, email: str, session: Optional[Session] = None) -> Optional[User]:
        """
        Retrieve a user by email address.
        
        Args:
            email: The email address to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The user if found, None otherwise
        """
        if session:
            return session.query(User).filter_by(email=email).first()
        
        with session_scope() as session:
            return session.query(User).filter_by(email=email).first()
    
    @handle_errors("UserRepository")
    def get_user_by_phone(self, phone: str, session: Optional[Session] = None) -> Optional[User]:
        """
        Retrieve a user by phone number.
        
        Args:
            phone: The phone number to search for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The user if found, None otherwise
        """
        if session:
            return session.query(User).filter_by(phone=phone).first()
        
        with session_scope() as session:
            return session.query(User).filter_by(phone=phone).first()
    
    @handle_errors("UserRepository")
    def get_user_with_roles(self, user_id: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user with their associated roles.
        
        Args:
            user_id: The unique identifier of the user
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing user with roles
        """
        if session:
            user = session.query(User).options(
                joinedload(User.roles)
            ).filter_by(id=user_id).first()
            
            if not user:
                return None
            
            return {
                'user': user,
                'roles': user.roles
            }
        
        with session_scope() as session:
            return self.get_user_with_roles(user_id, session)
    
    @handle_errors("UserRepository")
    def get_users_by_type(self, user_type: UserTypeEnum, session: Optional[Session] = None) -> List[User]:
        """
        Retrieve all users of a specific type.
        
        Args:
            user_type: The type of user to filter by
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of users of the specified type
        """
        if session:
            return session.query(User).filter_by(user_type=user_type).all()
        
        with session_scope() as session:
            return session.query(User).filter_by(user_type=user_type).all()
    
    @handle_errors("UserRepository")
    def get_active_users(self, session: Optional[Session] = None) -> List[User]:
        """
        Retrieve all active users.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of active users
        """
        if session:
            return session.query(User).filter_by(active=True).all()
        
        with session_scope() as session:
            return session.query(User).filter_by(active=True).all()
    
    @handle_errors("UserRepository")
    def get_inactive_users(self, session: Optional[Session] = None) -> List[User]:
        """
        Retrieve all inactive users.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of inactive users
        """
        if session:
            return session.query(User).filter_by(active=False).all()
        
        with session_scope() as session:
            return session.query(User).filter_by(active=False).all()
    
    @handle_errors("UserRepository")
    def get_users_by_language(self, language: LanguageEnum, session: Optional[Session] = None) -> List[User]:
        """
        Retrieve all users with a specific language preference.
        
        Args:
            language: The language preference to filter by
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of users with the specified language preference
        """
        if session:
            return session.query(User).filter_by(language=language).all()
        
        with session_scope() as session:
            return session.query(User).filter_by(language=language).all()
    
    @handle_errors("UserRepository")
    def get_verified_users(self, session: Optional[Session] = None) -> List[User]:
        """
        Retrieve all users with verified email addresses.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of users with verified email addresses
        """
        if session:
            return session.query(User).filter(User.email_confirmed_at.isnot(None)).all()
        
        with session_scope() as session:
            return session.query(User).filter(User.email_confirmed_at.isnot(None)).all()
    
    @handle_errors("UserRepository")
    def get_users_by_registration_date(self, start_date: datetime, end_date: datetime, session: Optional[Session] = None) -> List[User]:
        """
        Retrieve users registered within a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of users registered within the date range
        """
        if session:
            return session.query(User).filter(
                and_(
                    User.create_date >= start_date,
                    User.create_date <= end_date
                )
            ).order_by(desc(User.create_date)).all()
        
        with session_scope() as session:
            return session.query(User).filter(
                and_(
                    User.create_date >= start_date,
                    User.create_date <= end_date
                )
            ).order_by(desc(User.create_date)).all()
    
    @handle_errors("UserRepository")
    def search_users(self, search_term: str, session: Optional[Session] = None) -> List[User]:
        """
        Search users by username, email, or name.
        
        Args:
            search_term: The search term to look for
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of users matching the search term
        """
        if session:
            search_pattern = f"%{search_term}%"
            return session.query(User).filter(
                or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.name.ilike(search_pattern)
                )
            ).all()
        
        with session_scope() as session:
            return self.search_users(search_term, session)
    
    @handle_errors("UserRepository")
    def get_recent_users(self, limit: int = 10, session: Optional[Session] = None) -> List[User]:
        """
        Retrieve the most recently registered users.
        
        Args:
            limit: Maximum number of users to return
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of recent users
        """
        if session:
            return session.query(User).order_by(desc(User.create_date)).limit(limit).all()
        
        with session_scope() as session:
            return session.query(User).order_by(desc(User.create_date)).limit(limit).all()
    
    @handle_errors("UserRepository")
    def activate_user(self, user_id: str, session: Optional[Session] = None) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id: The unique identifier of the user
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if activated successfully
        """
        if session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.active = True
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.activate_user(user_id, session)
    
    @handle_errors("UserRepository")
    def deactivate_user(self, user_id: str, session: Optional[Session] = None) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: The unique identifier of the user
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if deactivated successfully
        """
        if session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.active = False
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.deactivate_user(user_id, session)
    
    @handle_errors("UserRepository")
    def update_user_password(self, user_id: str, hashed_password: str, session: Optional[Session] = None) -> bool:
        """
        Update a user's password.
        
        Args:
            user_id: The unique identifier of the user
            hashed_password: The new hashed password
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.password = hashed_password
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.update_user_password(user_id, hashed_password, session)
    
    @handle_errors("UserRepository")
    def confirm_email(self, user_id: str, session: Optional[Session] = None) -> bool:
        """
        Confirm a user's email address.
        
        Args:
            user_id: The unique identifier of the user
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if confirmed successfully
        """
        if session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.email_confirmed_at = datetime.now(timezone.utc)
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.confirm_email(user_id, session)
    
    @handle_errors("UserRepository")
    def confirm_mobile(self, user_id: str, session: Optional[Session] = None) -> bool:
        """
        Confirm a user's mobile number.
        
        Args:
            user_id: The unique identifier of the user
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if confirmed successfully
        """
        if session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.mobile_confirmed_at = datetime.now(timezone.utc)
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.confirm_mobile(user_id, session)
    
    @handle_errors("UserRepository")
    def get_user_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get user statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing user statistics
        """
        if session:
            total_users = session.query(User).count()
            active_users = session.query(User).filter_by(active=True).count()
            inactive_users = session.query(User).filter_by(active=False).count()
            verified_users = session.query(User).filter(User.email_confirmed_at.isnot(None)).count()
            
            # Count users by type
            user_types = {}
            for user_type in UserTypeEnum:
                count = session.query(User).filter_by(user_type=user_type).count()
                user_types[user_type.value] = count
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'verified_users': verified_users,
                'user_types': user_types
            }
        
        with session_scope() as session:
            return self.get_user_statistics(session)
