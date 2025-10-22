# Guide: Enabling Commented Permission Decorators

## Overview

There are **122 commented permission decorators** across the backend codebase. This is a **CRITICAL SECURITY VULNERABILITY** as it allows unauthorized access to protected endpoints.

This guide provides a systematic approach to safely enable these decorators.

## Why Permission Decorators Are Important

Permission decorators provide:
1. **Authentication**: Verify the user is logged in
2. **Authorization**: Verify the user has required permissions
3. **Audit Trail**: Track who accessed what resources
4. **Security**: Prevent unauthorized access to sensitive data

## Prerequisites

Before enabling permission decorators:

1. **Database Setup**: Ensure roles and permissions tables are populated
   ```sql
   SELECT * FROM roles;
   SELECT * FROM permissions;
   SELECT * FROM role_permissions;
   ```

2. **Admin User**: Ensure at least one admin user exists with all permissions

3. **Test Environment**: Never enable in production first - test in development

## Step-by-Step Enablement Process

### Step 1: Verify Permission System Works

Test that the permission system is functional:

```python
# backend/test_permissions.py
from app.users.service import UserService
from app.security.permissions import has_permission
from flask import g

service = UserService()

# Test getting user roles
user_id = "your_test_user_id"
roles = service.get_user_roles_ids(user_id)
print(f"User roles: {roles}")

# Test permission check
permissions = ['user.show.all']
user_roles_ids = service.get_user_roles_ids(user_id)
has_perm, perm = service.check_role_permission(permissions, user_roles_ids)
print(f"Has permission: {has_perm}, Permission: {perm}")
```

### Step 2: Create Permission Seed Data

Ensure all required permissions exist in the database:

```python
# backend/scripts/seed_permissions.py
from app.users.model import Permission, Role, RolePermission
from database import Session

# Define all permissions
PERMISSIONS = [
    # User permissions
    {'model': 'user', 'name': 'user.show.all'},
    {'model': 'user', 'name': 'user.show.own'},
    {'model': 'user', 'name': 'user.add'},
    {'model': 'user', 'name': 'user.edit'},
    {'model': 'user', 'name': 'user.delete'},
    
    # Category permissions
    {'model': 'category', 'name': 'category.show.all'},
    {'model': 'category', 'name': 'category.add'},
    {'model': 'category', 'name': 'category.edit'},
    {'model': 'category', 'name': 'category.delete'},
    
    # Add all other permissions here...
]

session = Session()

for perm_data in PERMISSIONS:
    existing = session.query(Permission).filter(
        Permission.name == perm_data['name']
    ).first()
    
    if not existing:
        perm = Permission(**perm_data)
        session.add(perm)
        print(f"Created permission: {perm_data['name']}")

session.commit()
session.close()
```

### Step 3: Enable Decorators Module by Module

Enable decorators one module at a time to isolate issues.

#### Module Priority Order:

1. **Start with low-risk, read-only modules**:
   - dashboard (viewing statistics)
   - faq (viewing FAQs)

2. **Then core business modules**:
   - category
   - product
   - inventory

3. **Finally critical modules**:
   - users
   - payment
   - transaction

#### Example: Enabling for FAQ Module

**File**: `backend/app/faq/routes.py`

**Before**:
```python
@faq.route('/', methods=['GET'])
@cross_origin()
#@permissions.has_permission(['faq.show.all', 'faq.show'])
def get_all_faq():
    return jsonify(service.get_faq_all())
```

**After**:
```python
@faq.route('/', methods=['GET'])
@cross_origin()
@permissions.has_permission(['faq.show.all', 'faq.show'])
def get_all_faq():
    return jsonify(service.get_faq_all())
```

### Step 4: Test Each Module

After enabling decorators for a module:

1. **Test Without Token** (should fail with 401):
   ```bash
   curl -X GET http://localhost:5000/store3d/api/v1/faq/
   # Expected: {"message": "a valid token is missing"}
   ```

2. **Test With Invalid Token** (should fail with 401):
   ```bash
   curl -X GET http://localhost:5000/store3d/api/v1/faq/ \
     -H "x-access-tokens: invalid_token"
   # Expected: {"message": "token is invalid"}
   ```

3. **Test With Valid Token, No Permission** (should fail with 403):
   ```bash
   curl -X GET http://localhost:5000/store3d/api/v1/faq/ \
     -H "x-access-tokens: <valid_token_without_faq_permission>"
   # Expected: {"message": "Sorry you do not have Permission"}
   ```

4. **Test With Valid Token and Permission** (should succeed):
   ```bash
   curl -X GET http://localhost:5000/store3d/api/v1/faq/ \
     -H "x-access-tokens: <valid_token_with_faq_permission>"
   # Expected: Actual FAQ data
   ```

### Step 5: Handle Common Issues

#### Issue 1: "Permission not found"

**Cause**: Permission doesn't exist in database

**Solution**:
```python
# Add missing permission
from app.users.model import Permission
from database import Session

session = Session()
perm = Permission(model='faq', name='faq.show.all')
session.add(perm)
session.commit()
```

#### Issue 2: "User has no roles"

**Cause**: User not assigned to any role

**Solution**:
```python
# Assign user to role
from app.users.model import UserRoles
from database import Session

session = Session()
user_role = UserRoles(user_id=user_id, role_id=role_id)
session.add(user_role)
session.commit()
```

#### Issue 3: "Role has no permissions"

**Cause**: Role exists but has no permissions assigned

**Solution**:
```python
# Assign permission to role
from app.users.model import RolePermission
from database import Session

session = Session()
role_perm = RolePermission(role_id=role_id, permission_id=permission_id)
session.add(role_perm)
session.commit()
```

## Automation Script

Use this script to enable all decorators at once (after testing!):

```python
# backend/scripts/enable_all_permissions.py
import os
import re

def enable_permissions_in_file(filepath):
    """Enable all commented permission decorators in a file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace #@permissions with @permissions
    new_content = re.sub(
        r'#@permissions\.has_permission',
        r'@permissions.has_permission',
        content
    )
    
    if content != new_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")
        return True
    return False

# Find all route files
app_dir = 'backend/app'
updated_files = []

for root, dirs, files in os.walk(app_dir):
    for file in files:
        if file == 'routes.py':
            filepath = os.path.join(root, file)
            if enable_permissions_in_file(filepath):
                updated_files.append(filepath)

print(f"\nTotal files updated: {len(updated_files)}")
for f in updated_files:
    print(f"  - {f}")
```

## Verification Checklist

After enabling all decorators:

- [ ] No commented decorators remain: `grep -r "#@permissions" backend/app/ | wc -l` (should be 0)
- [ ] All tests pass: `python -m pytest`
- [ ] Health check works: `curl http://localhost:5000/health`
- [ ] Can login with admin user
- [ ] Can access admin endpoints
- [ ] Cannot access endpoints without permissions
- [ ] All critical user workflows tested

## Module-by-Module Checklist

Track progress enabling decorators:

### Phase 1: Low Risk (Read-Only)
- [ ] dashboard (10 decorators)
- [ ] faq (5 decorators)

### Phase 2: Core Business
- [ ] category (already enabled - verify)
- [ ] product (verify)
- [ ] inventory (9 decorators)
- [ ] expense (13 decorators)

### Phase 3: Medium Risk
- [ ] customers (5 decorators)
- [ ] company (5 decorators)
- [ ] branch (5 decorators)
- [ ] store (5 decorators)
- [ ] supplier (5 decorators)
- [ ] staff (7 decorators)

### Phase 4: High Risk (Financial/Auth)
- [ ] cart (10 decorators)
- [ ] transaction (5 decorators)
- [ ] payment_transaction (1 decorator)
- [ ] financial (5 decorators)

### Phase 5: Critical (User Management)
- [ ] users (10 decorators)
- [ ] setting (7 decorators)
- [ ] address (3 decorators)

### Phase 6: Additional
- [ ] labor (11 decorators)
- [ ] medias (2 decorators)
- [ ] thawani (if applicable)
- [ ] ompay (if applicable)

## Rollback Plan

If issues occur after enabling:

1. **Immediate**: Re-comment decorators in problematic module
2. **Investigate**: Check logs for specific permission errors
3. **Fix**: Add missing permissions to database
4. **Re-enable**: Try again after fix

## Best Practices

1. **Never enable in production first** - Always test in dev/staging
2. **Enable incrementally** - One module at a time
3. **Test thoroughly** - All CRUD operations
4. **Document issues** - Keep track of problems encountered
5. **Have rollback ready** - Git commit before each change
6. **Communicate** - Inform team of changes

## Permission Naming Convention

Follow this pattern for new permissions:

```
<model>.<action>.<scope>

Examples:
- user.show.all    (show all users)
- user.show.own    (show only own user)
- user.add         (create users)
- user.edit        (update users)
- user.delete      (delete users)
```

## Monitoring After Enablement

Monitor these metrics after enabling:

1. **401 Errors**: Authentication failures
2. **403 Errors**: Authorization failures
3. **Failed Login Attempts**: Potential security issues
4. **Permission Denials**: Users trying unauthorized access

Set up alerts for unusual spikes in these metrics.

## Support

If you encounter issues:

1. Check logs: `tail -f backend/logs/app.log`
2. Verify database: Check roles, permissions, and user_roles tables
3. Test permission system: Use test script from Step 1
4. Review this guide
5. Contact team lead

---

**Remember**: Security is not optional. Take the time to do this properly.


