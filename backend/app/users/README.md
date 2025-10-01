# Users Module

The Users module manages user accounts, authentication, and authorization in the 3D Store application, supporting multiple user types including customers, staff, and sellers.

## Overview

This module handles:
- User registration and authentication
- Role-based access control (RBAC)
- User profile management
- Password management and security
- User preferences and settings
- Account verification and activation
- User analytics and reporting

## Module Structure

```
users/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── repository.py       # Data access layer (Repository pattern)
├── schemas.py          # Input validation schemas
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### User
Main user entity with the following key attributes:
- **Basic Info**: `username`, `email`, `phone`, `first_name`, `last_name`
- **Authentication**: `password_hash`, `is_active`, `is_verified`, `last_login`
- **Profile**: `avatar_url`, `date_of_birth`, `gender`, `preferred_language`
- **Address**: `addresses` (relationship to Address model)
- **Roles**: `roles` (many-to-many relationship)
- **Metadata**: `created_at`, `updated_at`, `last_activity`

### Role
User roles for access control:
- **Role Info**: `name`, `description`, `is_system_role`
- **Permissions**: `permissions` (many-to-many relationship)
- **Hierarchy**: `parent_role_id`, `level`
- **Metadata**: `created_at`, `updated_at`

### Permission
Granular permissions for fine-grained access control:
- **Permission Info**: `name`, `description`, `resource`, `action`
- **Scope**: `scope` (global, organization, user)
- **Metadata**: `created_at`, `updated_at`

### UserSession
Active user sessions for security management:
- **Session Info**: `session_token`, `user_id`, `ip_address`, `user_agent`
- **Timestamps**: `created_at`, `last_activity`, `expires_at`
- **Metadata**: `is_active`, `device_info`

### UserPreference
User-specific preferences and settings:
- **Preferences**: `preferences` (JSON field for flexible storage)
- **Notifications**: `email_notifications`, `sms_notifications`, `push_notifications`
- **Privacy**: `privacy_settings` (JSON field)
- **UI Settings**: `theme`, `language`, `timezone`

## Repository Layer

The `UserRepository` class provides data access operations for the Users module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[User]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities (roles, sessions)
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(user_id)` - Get user by ID
- `create(user_data)` - Create new user
- `update(user_id, user_data)` - Update existing user
- `delete(user_id)` - Delete user
- `get_all(limit, offset)` - Get all users with pagination

#### User Lookup Methods
- `get_user_by_username(username)` - Get user by username
- `get_user_by_email(email)` - Get user by email address
- `get_user_by_phone(phone)` - Get user by phone number
- `get_user_with_roles(user_id)` - User with associated roles

#### Advanced Query Methods
- `get_users_by_type(user_type)` - Users by type (customer, staff, seller, admin)
- `get_active_users()` - Active users only
- `get_inactive_users()` - Inactive users only
- `get_users_by_language(language)` - Users by language preference
- `get_verified_users()` - Users with verified email addresses
- `get_users_by_registration_date(start_date, end_date)` - Users registered in date range
- `search_users(search_term)` - Search users by name/email/username
- `get_recent_users(limit)` - Most recently registered users

#### User Management
- `activate_user(user_id)` - Activate user account
- `deactivate_user(user_id)` - Deactivate user account
- `update_user_password(user_id, hashed_password)` - Update user password
- `confirm_email(user_id)` - Confirm user's email address
- `confirm_mobile(user_id)` - Confirm user's mobile number
- `get_user_statistics()` - User statistics for dashboard

### Usage Example

```python
from app.users.repository import UserRepository

# Initialize repository
user_repo = UserRepository()

# Get user by email
user = user_repo.get_user_by_email("user@example.com")

# Get users by type
admin_users = user_repo.get_users_by_type(UserTypeEnum.ADMIN)

# Search users
search_results = user_repo.search_users("john")

# Get user with roles
user_with_roles = user_repo.get_user_with_roles("user-uuid")

# Activate user
user_repo.activate_user("user-uuid")

# Get user statistics
stats = user_repo.get_user_statistics()
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### User Management
- `GET /users` - List users (admin only)
- `GET /users/{id}` - Get user profile
- `PUT /users/{id}` - Update user profile
- `DELETE /users/{id}` - Deactivate user account
- `GET /users/{id}/sessions` - Get user sessions
- `DELETE /users/{id}/sessions/{session_id}` - Revoke session

### Profile Management
- `GET /users/profile` - Get current user profile
- `PUT /users/profile` - Update current user profile
- `POST /users/profile/avatar` - Upload profile avatar
- `GET /users/profile/preferences` - Get user preferences
- `PUT /users/profile/preferences` - Update user preferences

### Role and Permission Management
- `GET /users/roles` - List all roles
- `POST /users/roles` - Create new role
- `PUT /users/roles/{id}` - Update role
- `DELETE /users/roles/{id}` - Delete role
- `GET /users/permissions` - List all permissions
- `POST /users/{id}/roles` - Assign role to user
- `DELETE /users/{id}/roles/{role_id}` - Remove role from user

### Account Verification
- `POST /users/verify-email` - Verify email address
- `POST /users/resend-verification` - Resend verification email
- `POST /users/verify-phone` - Verify phone number
- `POST /users/resend-phone-verification` - Resend phone verification

## Business Logic

### User Registration
1. **Data Validation**: Validate user input using schemas
2. **Duplicate Check**: Check for existing username/email
3. **Password Hashing**: Hash password using secure algorithm
4. **Role Assignment**: Assign default role (customer)
5. **Verification**: Generate email verification token
6. **Welcome Email**: Send welcome email with verification link
7. **Profile Creation**: Create user profile with default settings

### Authentication Flow
1. **Credential Validation**: Validate username/email and password
2. **Account Status Check**: Verify account is active and verified
3. **Session Creation**: Create new user session
4. **Token Generation**: Generate JWT access and refresh tokens
5. **Login Logging**: Log successful login attempt
6. **Response**: Return user info and tokens

### Password Management
1. **Password Validation**: Enforce password complexity rules
2. **Secure Hashing**: Use bcrypt or similar secure hashing
3. **Password History**: Prevent reuse of recent passwords
4. **Reset Flow**: Secure password reset with time-limited tokens
5. **Force Reset**: Force password reset for security reasons

### Role-Based Access Control
1. **Permission Checking**: Check user permissions for resources
2. **Role Hierarchy**: Support role inheritance and hierarchy
3. **Dynamic Permissions**: Runtime permission evaluation
4. **Resource Scoping**: Support for resource-specific permissions
5. **Audit Logging**: Log all permission checks and access attempts

## Validation Schemas

### UserCreateSchema
```python
{
    "username": "string (required, min 3, max 50, unique)",
    "email": "string (required, valid email, unique)",
    "password": "string (required, min 8, max 128)",
    "first_name": "string (required, max 100)",
    "last_name": "string (required, max 100)",
    "phone": "string (optional, valid phone number)",
    "date_of_birth": "date (optional)",
    "gender": "string (optional, enum: male|female|other)",
    "preferred_language": "string (optional, default: en)"
}
```

### UserUpdateSchema
```python
{
    "first_name": "string (optional, max 100)",
    "last_name": "string (optional, max 100)",
    "phone": "string (optional, valid phone number)",
    "date_of_birth": "date (optional)",
    "gender": "string (optional, enum: male|female|other)",
    "preferred_language": "string (optional)",
    "avatar_url": "string (optional, valid URL)"
}
```

### UserLoginSchema
```python
{
    "username_or_email": "string (required)",
    "password": "string (required)",
    "remember_me": "boolean (optional, default false)"
}
```

### PasswordChangeSchema
```python
{
    "current_password": "string (required)",
    "new_password": "string (required, min 8, max 128)",
    "confirm_password": "string (required, must match new_password)"
}
```

### UserProfileSchema
```python
{
    "first_name": "string (optional, max 100)",
    "last_name": "string (optional, max 100)",
    "phone": "string (optional, valid phone number)",
    "date_of_birth": "date (optional)",
    "gender": "string (optional, enum: male|female|other)",
    "preferred_language": "string (optional)",
    "timezone": "string (optional)",
    "notifications": {
        "email": "boolean (optional)",
        "sms": "boolean (optional)",
        "push": "boolean (optional)"
    }
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **AuthenticationException**: For authentication failures
- **AuthorizationException**: For permission denied errors
- **ResourceNotFoundException**: When user not found
- **BusinessLogicException**: For business rule violations

## Dependencies

- **Security Module**: For authentication and authorization
- **Email Module**: For verification and notification emails
- **SMS Module**: For phone verification
- **File Storage**: For profile avatars
- **Caching**: For session management and performance
- **Audit Module**: For security logging

## Usage Examples

### User Registration
```python
from app.users.service import UserService
from app.users.schemas import UserCreateSchema

service = UserService()
user_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+96812345678"
}

user = service.create_user(user_data)
```

### Authentication
```python
# Login user
login_data = {
    "username_or_email": "john@example.com",
    "password": "SecurePass123!"
}

auth_result = service.authenticate_user(login_data)
# Returns: {"user": user, "access_token": token, "refresh_token": refresh_token}
```

### Role Management
```python
# Assign role to user
service.assign_role_to_user(user_id, "seller")

# Check user permission
has_permission = service.user_has_permission(user_id, "product.create")

# Get user roles
roles = service.get_user_roles(user_id)
```

### Profile Management
```python
# Update user profile
profile_data = {
    "first_name": "John",
    "last_name": "Smith",
    "phone": "+96887654321",
    "preferred_language": "ar"
}

service.update_user_profile(user_id, profile_data)

# Upload avatar
avatar_url = service.upload_avatar(user_id, avatar_file)
```

## Security Features

### Password Security
- **Complexity Requirements**: Minimum 8 characters, mixed case, numbers, symbols
- **Secure Hashing**: bcrypt with appropriate salt rounds
- **Password History**: Prevent reuse of last 5 passwords
- **Brute Force Protection**: Account lockout after failed attempts
- **Password Expiry**: Optional password expiration policy

### Session Management
- **Secure Tokens**: JWT with proper signing and expiration
- **Session Invalidation**: Logout invalidates all sessions
- **Device Tracking**: Track login devices and locations
- **Suspicious Activity**: Detect and alert on unusual login patterns

### Account Security
- **Email Verification**: Required for account activation
- **Phone Verification**: Optional two-factor authentication
- **Account Lockout**: Temporary lockout after security violations
- **Audit Logging**: Comprehensive security event logging

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: User sessions and permissions cached
- **Lazy Loading**: User relationships loaded on demand
- **Connection Pooling**: Efficient database connection management
- **Rate Limiting**: API endpoints protected against abuse

## Integration Points

- **Authentication Providers**: OAuth, LDAP integration
- **Email Service**: Verification and notification emails
- **SMS Service**: Phone verification and notifications
- **File Storage**: Profile avatars and documents
- **Audit System**: Security and access logging
- **Analytics**: User behavior and engagement tracking

## Future Enhancements

- **Multi-Factor Authentication**: TOTP, SMS, hardware tokens
- **Social Login**: Google, Facebook, Apple integration
- **Advanced RBAC**: Attribute-based access control (ABAC)
- **User Impersonation**: Admin ability to impersonate users
- **Bulk User Management**: CSV import/export functionality
- **Advanced Analytics**: User journey and behavior analysis
