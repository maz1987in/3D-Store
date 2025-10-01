# Security Module

The Security module provides authentication, authorization, and security services for the 3D Store application, ensuring secure access and data protection.

## Overview

This module handles:
- User authentication and session management
- Role-based access control (RBAC)
- Permission management and authorization
- Password security and encryption
- Two-factor authentication (2FA)
- Security logging and monitoring
- API security and rate limiting

## Module Structure

```
security/
├── __init__.py          # Module initialization
├── login.py            # Authentication logic
├── mail.py             # Email security services
├── otp.py              # One-time password services
├── permissions.py      # Permission management
├── roles.py            # Role-based access control
└── swagger.yaml        # API documentation
```

## Models

### UserSession
User session management:
- **Session Info**: `session_id`, `user_id`, `token`, `refresh_token`
- **Device**: `device_type`, `user_agent`, `ip_address`
- **Location**: `country`, `city`, `timezone`
- **Security**: `is_active`, `expires_at`, `last_activity`
- **Metadata**: `created_at`, `updated_at`

### Permission
Granular permission system:
- **Permission Info**: `permission_id`, `name`, `description`, `resource`
- **Actions**: `actions`, `conditions`, `scope`
- **Hierarchy**: `parent_id`, `level`, `path`
- **Metadata**: `created_at`, `updated_at`

### Role
Role-based access control:
- **Role Info**: `role_id`, `name`, `description`, `is_system_role`
- **Permissions**: `permissions` (many-to-many relationship)
- **Hierarchy**: `parent_role_id`, `level`, `inheritance`
- **Metadata**: `created_at`, `updated_at`

### SecurityLog
Security event logging:
- **Log Info**: `log_id`, `user_id`, `event_type`, `severity`
- **Details**: `description`, `ip_address`, `user_agent`
- **Context**: `resource_type`, `resource_id`, `action`
- **Timestamps**: `created_at`, `event_time`

### OTPToken
One-time password tokens:
- **Token Info**: `token_id`, `user_id`, `token`, `token_type`
- **Usage**: `purpose`, `is_used`, `attempts`
- **Security**: `expires_at`, `ip_address`, `device_fingerprint`
- **Metadata**: `created_at`, `updated_at`

### SecurityPolicy
Security policy management:
- **Policy Info**: `policy_id`, `name`, `policy_type`, `is_active`
- **Rules**: `rules`, `conditions`, `actions`
- **Scope**: `applies_to`, `exceptions`, `priority`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password
- `POST /auth/verify-email` - Verify email address

### Two-Factor Authentication
- `POST /auth/2fa/enable` - Enable 2FA
- `POST /auth/2fa/disable` - Disable 2FA
- `POST /auth/2fa/verify` - Verify 2FA code
- `POST /auth/2fa/backup-codes` - Generate backup codes
- `POST /auth/2fa/recovery` - 2FA recovery

### Session Management
- `GET /auth/sessions` - List user sessions
- `GET /auth/sessions/{id}` - Get session details
- `DELETE /auth/sessions/{id}` - Revoke session
- `POST /auth/sessions/revoke-all` - Revoke all sessions

### Permission Management
- `GET /security/permissions` - List permissions
- `GET /security/permissions/{id}` - Get permission details
- `POST /security/permissions` - Create permission
- `PUT /security/permissions/{id}` - Update permission
- `DELETE /security/permissions/{id}` - Delete permission

### Role Management
- `GET /security/roles` - List roles
- `GET /security/roles/{id}` - Get role details
- `POST /security/roles` - Create role
- `PUT /security/roles/{id}` - Update role
- `DELETE /security/roles/{id}` - Delete role
- `POST /security/roles/{id}/permissions` - Assign permissions

### Security Monitoring
- `GET /security/logs` - List security logs
- `GET /security/logs/{id}` - Get log details
- `GET /security/events` - List security events
- `POST /security/events/report` - Report security event

### Security Policies
- `GET /security/policies` - List security policies
- `GET /security/policies/{id}` - Get policy details
- `POST /security/policies` - Create policy
- `PUT /security/policies/{id}` - Update policy
- `DELETE /security/policies/{id}` - Delete policy

## Business Logic

### Authentication Flow
1. **Credential Validation**: Validate username/email and password
2. **Account Status Check**: Verify account is active and not locked
3. **Security Checks**: Check for suspicious activity
4. **Session Creation**: Create secure user session
5. **Token Generation**: Generate JWT access and refresh tokens
6. **Security Logging**: Log authentication attempt
7. **Response**: Return user info and tokens

### Password Security
1. **Complexity Requirements**: Enforce strong password policies
2. **Secure Hashing**: Use bcrypt with appropriate salt rounds
3. **Password History**: Prevent reuse of recent passwords
4. **Brute Force Protection**: Implement account lockout
5. **Password Expiry**: Optional password expiration
6. **Reset Flow**: Secure password reset process

### Two-Factor Authentication
1. **TOTP Setup**: Generate TOTP secret and QR code
2. **Backup Codes**: Generate recovery backup codes
3. **SMS Integration**: Send SMS codes for verification
4. **Email Integration**: Send email codes for verification
5. **Recovery Process**: Handle 2FA recovery scenarios
6. **Device Management**: Manage trusted devices

### Role-Based Access Control
1. **Permission Checking**: Check user permissions for resources
2. **Role Hierarchy**: Support role inheritance
3. **Dynamic Permissions**: Runtime permission evaluation
4. **Resource Scoping**: Support resource-specific permissions
5. **Conditional Access**: Support conditional permissions
6. **Audit Logging**: Log all permission checks

### Session Management
1. **Session Creation**: Create secure user sessions
2. **Token Management**: Manage JWT tokens and refresh
3. **Session Validation**: Validate active sessions
4. **Device Tracking**: Track user devices and locations
5. **Session Termination**: Handle session logout and expiry
6. **Security Monitoring**: Monitor for suspicious sessions

### Security Monitoring
1. **Event Logging**: Log all security events
2. **Threat Detection**: Detect suspicious activities
3. **Alert Generation**: Generate security alerts
4. **Incident Response**: Handle security incidents
5. **Compliance Reporting**: Generate compliance reports
6. **Forensic Analysis**: Support security investigations

## Validation Schemas

### LoginSchema
```python
{
    "username_or_email": "string (required)",
    "password": "string (required)",
    "remember_me": "boolean (optional, default false)",
    "device_info": {
        "device_type": "string (optional)",
        "user_agent": "string (optional)",
        "ip_address": "string (optional)"
    }
}
```

### PasswordResetSchema
```python
{
    "email": "string (required, valid email)",
    "reset_token": "string (required)",
    "new_password": "string (required, min 8, max 128)",
    "confirm_password": "string (required, must match new_password)"
}
```

### TwoFactorSchema
```python
{
    "user_id": "uuid (required)",
    "code": "string (required, 6 digits)",
    "method": "string (required, enum: totp|sms|email)",
    "device_fingerprint": "string (optional)"
}
```

### PermissionCreateSchema
```python
{
    "name": "string (required, max 100 chars, unique)",
    "description": "string (required, max 500 chars)",
    "resource": "string (required, max 100 chars)",
    "actions": "array of strings (required)",
    "conditions": "object (optional)",
    "scope": "string (required, enum: global|organization|user)",
    "parent_id": "uuid (optional)"
}
```

### RoleCreateSchema
```python
{
    "name": "string (required, max 100 chars, unique)",
    "description": "string (required, max 500 chars)",
    "is_system_role": "boolean (optional, default false)",
    "permissions": "array of uuids (optional)",
    "parent_role_id": "uuid (optional)",
    "inheritance": "string (optional, enum: full|partial|none)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **AuthenticationException**: For authentication failures
- **AuthorizationException**: For permission denied errors
- **ValidationException**: For input validation errors
- **SecurityException**: For security-related errors
- **SessionException**: For session-related errors

## Dependencies

- **JWT Library**: For token generation and validation
- **Bcrypt**: For password hashing
- **PyOTP**: For TOTP generation and validation
- **Email Service**: For email-based 2FA
- **SMS Service**: For SMS-based 2FA
- **Redis**: For session storage and caching

## Usage Examples

### User Authentication
```python
from app.security.login import AuthService
from app.security.schemas import LoginSchema

auth_service = AuthService()
login_data = {
    "username_or_email": "user@example.com",
    "password": "SecurePass123!",
    "remember_me": True,
    "device_info": {
        "device_type": "web",
        "user_agent": "Mozilla/5.0...",
        "ip_address": "192.168.1.1"
    }
}

auth_result = auth_service.authenticate(login_data)
# Returns: {"user": user, "access_token": token, "refresh_token": refresh_token}
```

### Two-Factor Authentication
```python
# Enable 2FA
otp_service = OTPService()
totp_secret = otp_service.generate_totp_secret(user_id)
qr_code = otp_service.generate_qr_code(user_id, totp_secret)

# Verify 2FA code
verification_result = otp_service.verify_totp_code(user_id, "123456")

# Generate backup codes
backup_codes = otp_service.generate_backup_codes(user_id)
```

### Permission Management
```python
# Create permission
permission_data = {
    "name": "product.create",
    "description": "Create new products",
    "resource": "product",
    "actions": ["create"],
    "conditions": {"category": "allowed_categories"},
    "scope": "global"
}

permission = permission_service.create_permission(permission_data)

# Check user permission
has_permission = permission_service.user_has_permission(
    user_id, "product.create", resource_id="product-123"
)
```

### Role Management
```python
# Create role
role_data = {
    "name": "product_manager",
    "description": "Product management role",
    "is_system_role": False,
    "permissions": ["permission-uuid-1", "permission-uuid-2"],
    "inheritance": "full"
}

role = role_service.create_role(role_data)

# Assign role to user
role_service.assign_role_to_user(user_id, role_id)

# Check user role
has_role = role_service.user_has_role(user_id, "product_manager")
```

### Session Management
```python
# Create session
session = session_service.create_session(user_id, device_info)

# Validate session
is_valid = session_service.validate_session(session_id)

# Refresh session
new_session = session_service.refresh_session(session_id)

# Revoke session
session_service.revoke_session(session_id)

# Get user sessions
sessions = session_service.get_user_sessions(user_id)
```

### Security Monitoring
```python
# Log security event
security_service.log_event(
    user_id=user_id,
    event_type="login_attempt",
    severity="info",
    description="Successful login",
    ip_address="192.168.1.1"
)

# Get security logs
logs = security_service.get_security_logs(
    user_id=user_id,
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Generate security report
report = security_service.generate_security_report(period="monthly")
```

## Performance Considerations

- **Token Caching**: Cache JWT tokens for performance
- **Session Storage**: Use Redis for session storage
- **Permission Caching**: Cache user permissions
- **Rate Limiting**: Implement rate limiting for security
- **Background Processing**: Process security events in background

## Security Features

### Password Security
- **Complexity Requirements**: Minimum 8 characters, mixed case, numbers, symbols
- **Secure Hashing**: bcrypt with 12+ salt rounds
- **Password History**: Prevent reuse of last 5 passwords
- **Brute Force Protection**: Account lockout after 5 failed attempts
- **Password Expiry**: Optional 90-day password expiration

### Session Security
- **Secure Tokens**: JWT with proper signing and expiration
- **Session Invalidation**: Logout invalidates all sessions
- **Device Tracking**: Track login devices and locations
- **Suspicious Activity**: Detect unusual login patterns
- **Session Timeout**: Automatic session timeout after inactivity

### API Security
- **Rate Limiting**: Protect against brute force attacks
- **CORS Configuration**: Proper cross-origin resource sharing
- **Input Validation**: Validate all API inputs
- **SQL Injection Prevention**: Use parameterized queries
- **XSS Protection**: Sanitize user inputs

## Integration Points

- **User Module**: User management and profiles
- **Email Service**: Email-based authentication
- **SMS Service**: SMS-based authentication
- **Audit System**: Security event logging
- **Monitoring**: Security monitoring and alerting
- **Analytics**: Security analytics and reporting

## Future Enhancements

- **Biometric Authentication**: Fingerprint and face recognition
- **Hardware Tokens**: FIDO2 and WebAuthn support
- **Risk-based Authentication**: AI-powered risk assessment
- **Zero Trust Architecture**: Implement zero trust security model
- **Advanced Threat Detection**: Machine learning threat detection
- **Compliance Automation**: Automated compliance reporting
