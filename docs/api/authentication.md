# API Authentication Documentation

This document provides comprehensive information about authentication in the 3D Store API, including JWT token management, role-based access control, and OAuth integration.

## Overview

The 3D Store API uses JWT (JSON Web Tokens) for authentication and authorization. All authenticated endpoints require a valid JWT token in the request header.

### Authentication Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │────────▶│   API    │────────▶│ Database │
│          │◀────────│  Server  │◀────────│          │
└──────────┘         └──────────┘         └──────────┘
     │                     │
     │  1. Login           │
     │────────────────────▶│
     │                     │
     │  2. JWT Token       │
     │◀────────────────────│
     │                     │
     │  3. Request + Token │
     │────────────────────▶│
     │                     │
     │  4. Validate Token  │
     │                     │
     │  5. Response        │
     │◀────────────────────│
```

---

## Authentication Endpoints

### User Registration

**Endpoint**: `POST /3dstore/api/v1/auth/register`

**Description**: Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "phone": "+96812345678",
  "first_name": "John",
  "last_name": "Doe",
  "language": "ENGLISH"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "phone": "+96812345678",
      "first_name": "John",
      "last_name": "Doe",
      "user_type": "USER",
      "language": "ENGLISH",
      "active": true
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Registration successful",
  "status": 200
}
```

**Error Responses**:
- `400 Bad Request` - Validation error
- `409 Conflict` - Email or phone already exists

---

### User Login

**Endpoint**: `POST /3dstore/api/v1/auth/login`

**Description**: Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "user_type": "USER",
      "roles": ["customer"],
      "permissions": ["order.create", "order.view"]
    }
  },
  "message": "Login successful",
  "status": 200
}
```

**Error Responses**:
- `400 Bad Request` - Missing email or password
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account disabled

---

### Token Refresh

**Endpoint**: `POST /3dstore/api/v1/auth/refresh`

**Description**: Refresh an expired access token using a refresh token.

**Request Body**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response** (200 OK):
```json
{
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Token refreshed successfully",
  "status": 200
}
```

**Error Responses**:
- `401 Unauthorized` - Invalid or expired refresh token

---

### Logout

**Endpoint**: `POST /3dstore/api/v1/auth/logout`

**Description**: Invalidate current token and logout user.

**Headers**:
```
x-access-tokens: <jwt_token>
```

**Response** (200 OK):
```json
{
  "data": null,
  "message": "Logout successful",
  "status": 200
}
```

---

### Get Current User

**Endpoint**: `GET /3dstore/api/v1/auth/profile`

**Description**: Get current authenticated user's profile.

**Headers**:
```
x-access-tokens: <jwt_token>
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "phone": "+96812345678",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "USER",
    "language": "ENGLISH",
    "active": true,
    "roles": ["customer"],
    "permissions": ["order.create", "order.view", "product.view"]
  },
  "message": "Success",
  "status": 200
}
```

---

### Password Reset Request

**Endpoint**: `POST /3dstore/api/v1/auth/password-reset-request`

**Description**: Request password reset email.

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "data": null,
  "message": "Password reset email sent",
  "status": 200
}
```

---

### Password Reset

**Endpoint**: `POST /3dstore/api/v1/auth/password-reset`

**Description**: Reset password using reset token.

**Request Body**:
```json
{
  "token": "reset_token_from_email",
  "password": "NewSecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "data": null,
  "message": "Password reset successful",
  "status": 200
}
```

---

### Change Password

**Endpoint**: `POST /3dstore/api/v1/auth/change-password`

**Description**: Change password for authenticated user.

**Headers**:
```
x-access-tokens: <jwt_token>
```

**Request Body**:
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword123!"
}
```

**Response** (200 OK):
```json
{
  "data": null,
  "message": "Password changed successfully",
  "status": 200
}
```

**Error Responses**:
- `400 Bad Request` - Current password incorrect
- `401 Unauthorized` - Invalid token

---

## JWT Token Structure

### Token Format

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCIsImV4cCI6MTcwNjc4NDAwMH0.signature
```

### Decoded Payload

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "user_type": "USER",
  "roles": ["customer"],
  "exp": 1706784000,
  "iat": 1706697600
}
```

### Token Claims

| Claim | Description | Type |
|-------|-------------|------|
| `id` | User ID | UUID |
| `email` | User email | String |
| `user_type` | User type | String |
| `roles` | User roles | Array |
| `exp` | Expiration time | Unix timestamp |
| `iat` | Issued at time | Unix timestamp |

### Token Expiration

- **Access Token**: 24 hours
- **Refresh Token**: 30 days

---

## Using JWT Tokens

### Including Token in Requests

**Header Name**: `x-access-tokens`

```http
GET /3dstore/api/v1/orders HTTP/1.1
Host: localhost:5000
x-access-tokens: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

### Frontend Implementation (Angular)

```typescript
// In auth.interceptor.ts
intercept(request: HttpRequest<unknown>, next: HttpHandler) {
  const token = localStorage.getItem('auth_token');
  
  if (token) {
    request = request.clone({
      setHeaders: {
        'x-access-tokens': token
      }
    });
  }
  
  return next.handle(request);
}
```

### Frontend Implementation (JavaScript)

```javascript
// Using Fetch API
fetch('http://localhost:5000/3dstore/api/v1/orders', {
  method: 'GET',
  headers: {
    'x-access-tokens': 'your_jwt_token_here',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Role-Based Access Control (RBAC)

### User Types

| User Type | Description | Default Permissions |
|-----------|-------------|---------------------|
| `USER` | Regular customer | View products, create orders |
| `ADMIN` | Administrator | Full system access |
| `MANAGER` | Store manager | Manage orders, inventory |
| `SELLER` | Marketplace seller | Manage own products |
| `STAFF` | Store staff | Basic operations |

### Roles

Roles are assigned to users and define their access level:

- **customer** - Regular customer
- **seller** - Marketplace seller
- **staff** - Store staff member
- **manager** - Store manager
- **admin** - System administrator

### Permissions

Permissions are granular access controls:

**Product Permissions**:
- `product.view` - View products
- `product.create` - Create products
- `product.update` - Update products
- `product.delete` - Delete products

**Order Permissions**:
- `order.view` - View orders
- `order.create` - Create orders
- `order.update` - Update orders
- `order.cancel` - Cancel orders

**Print Job Permissions**:
- `print_job.view` - View print jobs
- `print_job.create` - Create print jobs
- `print_job.manage` - Manage print jobs

**Admin Permissions**:
- `user.manage` - Manage users
- `system.configure` - Configure system
- `reports.view` - View reports

### Permission Check Example

```python
# Backend (Python/Flask)
from app.decorators.permissions import has_permission

@products.route('/', methods=['POST'])
@has_permission(['product.create'])
def create_product():
    # Only users with product.create permission can access
    pass
```

```typescript
// Frontend (Angular)
export class ProductEditComponent {
  canEdit$ = this.authService.hasPermission('product.update');
  
  ngOnInit(): void {
    this.canEdit$.subscribe(canEdit => {
      if (!canEdit) {
        this.router.navigate(['/products']);
      }
    });
  }
}
```

---

## OAuth Integration

### Supported Providers

- Google OAuth 2.0
- Apple Sign In
- Twitter OAuth

### Google OAuth

**Endpoint**: `GET /3dstore/api/v1/auth/google`

**Description**: Redirect to Google OAuth login.

**Query Parameters**:
- `redirect_uri` - Callback URL after authentication

**Callback**: `GET /3dstore/api/v1/auth/google/callback`

**Response**: Redirects to frontend with token in URL:
```
http://localhost:4200/auth/callback?token=<jwt_token>&refresh_token=<refresh_token>
```

### Apple OAuth

**Endpoint**: `GET /3dstore/api/v1/auth/apple`

**Description**: Redirect to Apple Sign In.

**Callback**: `GET /3dstore/api/v1/auth/apple/callback`

### Twitter OAuth

**Endpoint**: `GET /3dstore/api/v1/auth/twitter`

**Description**: Redirect to Twitter OAuth login.

**Callback**: `GET /3dstore/api/v1/auth/twitter/callback`

---

## Security Best Practices

### Token Storage

**✅ Recommended**:
- Store tokens in `httpOnly` cookies (most secure)
- Store tokens in `sessionStorage` (for single-tab sessions)
- Encrypt tokens before storing in `localStorage`

**❌ Not Recommended**:
- Plain `localStorage` (vulnerable to XSS)
- URL parameters (tokens visible in logs)
- Unencrypted cookies

### Token Validation

1. **Verify signature**: Ensure token hasn't been tampered with
2. **Check expiration**: Validate `exp` claim
3. **Verify issuer**: Ensure token is from trusted source
4. **Check permissions**: Validate user has required permissions

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Rate Limiting

Authentication endpoints are rate-limited:

- **Login**: 5 attempts per minute per IP
- **Register**: 3 attempts per minute per IP
- **Password Reset**: 3 attempts per hour per email

---

## Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request data |
| 401 | `INVALID_CREDENTIALS` | Wrong email/password |
| 401 | `TOKEN_EXPIRED` | JWT token expired |
| 401 | `INVALID_TOKEN` | Invalid JWT token |
| 403 | `ACCOUNT_DISABLED` | User account disabled |
| 403 | `INSUFFICIENT_PERMISSIONS` | Missing required permissions |
| 409 | `EMAIL_EXISTS` | Email already registered |
| 409 | `PHONE_EXISTS` | Phone already registered |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  },
  "status": 401
}
```

---

## Testing Authentication

### Using cURL

**Login**:
```bash
curl -X POST http://localhost:5000/3dstore/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Authenticated Request**:
```bash
TOKEN="your_jwt_token_here"

curl -X GET http://localhost:5000/3dstore/api/v1/orders \
  -H "x-access-tokens: $TOKEN"
```

### Using Postman

1. **Login** to get token
2. **Set token** in environment variable
3. **Add header** to collection: `x-access-tokens: {{token}}`
4. **Make requests** with automatic token injection

---

## Frontend Integration Example

### Complete Angular Auth Service

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap, map } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenKey = environment.tokenKey;
  private refreshTokenKey = environment.refreshTokenKey;
  private currentUserSubject = new BehaviorSubject<any>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadUserFromStorage();
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/auth/login`, { email, password })
      .pipe(
        tap(response => {
          this.setSession(response.data);
        })
      );
  }

  register(userData: any): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/auth/register`, userData)
      .pipe(
        tap(response => {
          this.setSession(response.data);
        })
      );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    return !!token && !this.isTokenExpired(token);
  }

  hasPermission(permission: string): Observable<boolean> {
    return this.currentUser$.pipe(
      map(user => user?.permissions?.includes(permission) || false)
    );
  }

  hasRole(role: string): Observable<boolean> {
    return this.currentUser$.pipe(
      map(user => user?.roles?.includes(role) || false)
    );
  }

  private setSession(authData: any): void {
    localStorage.setItem(this.tokenKey, authData.token);
    localStorage.setItem(this.refreshTokenKey, authData.refresh_token);
    localStorage.setItem('currentUser', JSON.stringify(authData.user));
    this.currentUserSubject.next(authData.user);
  }

  private loadUserFromStorage(): void {
    const user = localStorage.getItem('currentUser');
    if (user) {
      this.currentUserSubject.next(JSON.parse(user));
    }
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp < Date.now() / 1000;
    } catch {
      return true;
    }
  }
}
```

---

## Additional Resources

- [JWT.io - JWT Decoder](https://jwt.io/)
- [OAuth 2.0 Documentation](https://oauth.net/2/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Last Updated**: January 2025  
**Version**: 1.0.0

