"""
User Search Service

Handles user search, filtering, and query operations.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from sqlalchemy_filters import apply_pagination

from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import remove_leading_plus
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors
from app.users.repository import UserRepository
from app.users.model import User, Role
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query


class UserSearchService:
    """Service for user search and filtering operations."""
    
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
    def get_users(self, filter_obj) -> tuple:
        """Get users with filtering and pagination."""
        if filter_obj.sort is None:
            filter_obj.sorters = create_sorters('modified_date', 'desc')
        
        # Use repository for paginated user listing
        result = self.user_repo.get_users_with_roles(filter_obj)
        
        return {
            'users': self.get_user_model(result['users']),
            'filters': result['filters']
        }, 200

    @handle_errors("User")
    def get_user_admin(self, user_id: str) -> tuple:
        """Get admin user by ID."""
        user = self.user_repo.get_user_with_roles(user_id)
        if user is None:
            raise ResourceNotFoundError("User")
        
        return self.get_user_model(user), 200

    @handle_errors("User")
    def get_users_by_user_type(self, user_type: str) -> tuple:
        """Get users by user type."""
        users = self.user_repo.get_users_by_type(user_type)
        result = [self.get_user_model(user) for user in users]
        return result, 200

    @handle_errors("User")
    def get_users_by_role(self, role: str) -> tuple:
        """Get users by role."""
        users = self.user_repo.get_users_by_role(role)
        result = [self.get_user_model(user) for user in users]
        return result, 200

    @handle_errors("User")
    def get_user_role_by_id(self, user_id: str) -> tuple:
        """Get user with role by ID."""
        user = self.user_repo.get_user_with_roles(user_id)
        if user is None:
            raise ResourceNotFoundError("User")
        
        return self.get_user_model(user), 200

    @handle_errors("User")
    def search_user(self, param: str, filter_obj) -> tuple:
        """Search users by parameter."""
        mobile = remove_leading_plus(param)
        
        if filter_obj.sort is None:
            filter_obj.sorters = create_sorters('modified_date', 'desc')
        
        # Use repository for user search
        result = self.user_repo.search_users(param, mobile, filter_obj)
        
        return {
            'users': self.get_user_model(result['users']),
            'filters': result['filters']
        }, 200
