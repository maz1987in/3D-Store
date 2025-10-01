"""
Refactored User Service

This service now uses a composition-based approach with focused service classes
for better maintainability and single responsibility principle.

The original monolithic UserService has been refactored into:
- UserManagementService: Core user CRUD operations
- UserAuthenticationService: Authentication, login, password management
- UserRoleService: Role and permission management
- UserSearchService: Search and filtering operations
- UserStatisticsService: Analytics and reporting

This maintains the same public API while improving code organization.
"""

from .services.user_service import UserService