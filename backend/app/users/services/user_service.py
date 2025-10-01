"""
Refactored User Service

Main service class that coordinates between focused service classes.
This replaces the monolithic UserService with a composition-based approach.
"""

from typing import Dict, Any, Optional, List
from .user_management_service import UserManagementService
from .user_authentication_service import UserAuthenticationService
from .user_role_service import UserRoleService
from .user_search_service import UserSearchService
from .user_statistics_service import UserStatisticsService


class UserService:
    """
    Main User Service that coordinates between focused service classes.
    
    This service acts as a facade, delegating specific responsibilities
    to specialized service classes while maintaining the same public API.
    """
    
    def __init__(self):
        # Initialize focused service classes
        self.management = UserManagementService()
        self.authentication = UserAuthenticationService()
        self.roles = UserRoleService()
        self.search = UserSearchService()
        self.statistics = UserStatisticsService()
    
    # User Management Methods
    def get_user_model(self, users, with_password=False):
        """Convert user objects to JSON format."""
        return self.management.get_user_model(users, with_password)
    
    def is_user_exist(self, phone: str, email: Optional[str] = None) -> bool:
        """Check if user exists by phone or email."""
        return self.management.is_user_exist(phone, email)
    
    def is_user_id_exist(self, user_id: str, user_type: str) -> bool:
        """Check if user with same user_id and user_type exists."""
        return self.management.is_user_id_exist(user_id, user_type)
    
    def create_user(self, data: Dict[str, Any]) -> tuple:
        """Create a new user (sign-up)."""
        return self.management.create_user(data)
    
    def create_user_admin(self, data: Dict[str, Any]) -> tuple:
        """Create a new user by admin."""
        return self.management.create_user_admin(data)
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> tuple:
        """Update user information."""
        return self.management.update_user(user_id, data)
    
    def update_user_admin(self, user_id: str, data: Dict[str, Any]) -> tuple:
        """Update user information by admin."""
        return self.management.update_user_admin(user_id, data)
    
    def add_user_id_image(self, user_id: str, image: str, replace: bool = False) -> tuple:
        """Add or replace user ID image."""
        return self.management.add_user_id_image(user_id, image, replace)
    
    def get_user_by_id(self, user_id: str) -> tuple:
        """Get user by ID."""
        return self.management.get_user_by_id(user_id)
    
    def get_user_json_by_id(self, user_id: str) -> tuple:
        """Get user JSON by ID."""
        return self.management.get_user_json_by_id(user_id)
    
    def delete_user(self, user_id: str) -> tuple:
        """Delete user."""
        return self.management.delete_user(user_id)
    
    def disable_user(self, user_id: str) -> tuple:
        """Disable user account."""
        return self.management.disable_user(user_id)
    
    def enable_user(self, user_id: str) -> tuple:
        """Enable user account."""
        return self.management.enable_user(user_id)
    
    # Authentication Methods
    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Get user by email address."""
        return self.authentication.get_user_by_email(email)
    
    def get_user_by_mobile(self, mobile: str) -> Optional[Any]:
        """Get user by mobile number."""
        return self.authentication.get_user_by_mobile(mobile)
    
    def get_user_by_any(self, param: str, with_password: bool = False) -> tuple:
        """Get user by email or mobile."""
        return self.authentication.get_user_by_any(param, with_password)
    
    def get_user_admin_by_any(self, param: str, with_password: bool = False) -> tuple:
        """Get admin user by email or mobile."""
        return self.authentication.get_user_admin_by_any(param, with_password)
    
    def get_oauth_user(self, provider: str, oauth_id: str) -> Optional[Any]:
        """Get OAuth user by provider and OAuth ID."""
        return self.authentication.get_oauth_user(provider, oauth_id)
    
    def create_oauth_user(self, data: Dict[str, Any]) -> tuple:
        """Create OAuth user."""
        return self.authentication.create_oauth_user(data)
    
    def user_logins(self, data: Dict[str, Any]) -> tuple:
        """Record user login."""
        return self.authentication.user_logins(data)
    
    def user_confirmed_mobile(self, mobile: str) -> tuple:
        """Confirm user mobile number."""
        return self.authentication.user_confirmed_mobile(mobile)
    
    def user_confirmed(self, email: str) -> tuple:
        """Confirm user email address."""
        return self.authentication.user_confirmed(email)
    
    def update_user_password(self, user_id: str, data: Dict[str, Any]) -> tuple:
        """Update user password."""
        return self.authentication.update_user_password(user_id, data)
    
    def forget_password(self, email: str) -> tuple:
        """Send password reset email."""
        return self.authentication.forget_password(email)
    
    def show_logins(self) -> tuple:
        """Get user login history."""
        return self.authentication.show_logins()
    
    # Role and Permission Methods
    def get_roles(self) -> tuple:
        """Get all roles."""
        return self.roles.get_roles()
    
    def get_role_by_id(self, role_id: str) -> tuple:
        """Get role by ID."""
        return self.roles.get_role_by_id(role_id)
    
    def has_role(self, role_ids: List[str], role_name: str) -> bool:
        """Check if user has specific role."""
        return self.roles.has_role(role_ids, role_name)
    
    def add_role(self, data: Dict[str, Any]) -> tuple:
        """Add new role."""
        return self.roles.add_role(data)
    
    def update_role(self, role_id: str, data: Dict[str, Any]) -> tuple:
        """Update role."""
        return self.roles.update_role(role_id, data)
    
    def add_permission(self, data: Dict[str, Any]) -> tuple:
        """Add new permission."""
        return self.roles.add_permission(data)
    
    def get_permissions(self) -> tuple:
        """Get all permissions."""
        return self.roles.get_permissions()
    
    def delete_permission(self, data: Dict[str, Any]) -> tuple:
        """Delete permission."""
        return self.roles.delete_permission(data)
    
    def get_user_roles_ids(self, user_id: str) -> List[str]:
        """Get user role IDs."""
        return self.roles.get_user_roles_ids(user_id)
    
    def check_role_permission(self, permission_names: List[str], user_roles_ids: List[str]) -> bool:
        """Check if user roles have specific permissions."""
        return self.roles.check_role_permission(permission_names, user_roles_ids)
    
    def add_role_permission(self, data: Dict[str, Any]) -> tuple:
        """Add permission to role."""
        return self.roles.add_role_permission(data)
    
    def remove_role_permission(self, role_id: str, permission_id: str) -> tuple:
        """Remove permission from role."""
        return self.roles.remove_role_permission(role_id, permission_id)
    
    def get_roles_permissions(self) -> tuple:
        """Get all role-permission mappings."""
        return self.roles.get_roles_permissions()
    
    # Search and Query Methods
    def get_users(self, filter_obj) -> tuple:
        """Get users with filtering and pagination."""
        return self.search.get_users(filter_obj)
    
    def get_user_admin(self, user_id: str) -> tuple:
        """Get admin user by ID."""
        return self.search.get_user_admin(user_id)
    
    def get_users_by_user_type(self, user_type: str) -> tuple:
        """Get users by user type."""
        return self.search.get_users_by_user_type(user_type)
    
    def get_users_by_role(self, role: str) -> tuple:
        """Get users by role."""
        return self.search.get_users_by_role(role)
    
    def get_user_role_by_id(self, user_id: str) -> tuple:
        """Get user with role by ID."""
        return self.search.get_user_role_by_id(user_id)
    
    def search_user(self, param: str, filter_obj) -> tuple:
        """Search users by parameter."""
        return self.search.search_user(param, filter_obj)
    
    # Statistics and Analytics Methods
    def get_users_statistics(self) -> tuple:
        """Get comprehensive user statistics."""
        return self.statistics.get_users_statistics()
    
    def get_user_growth_analytics(self, days: int = 30) -> tuple:
        """Get user growth analytics for specified days."""
        return self.statistics.get_user_growth_analytics(days)
    
    def get_user_engagement_metrics(self) -> tuple:
        """Get user engagement metrics."""
        return self.statistics.get_user_engagement_metrics()
