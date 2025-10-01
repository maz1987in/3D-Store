"""
User Role Service

Handles user roles, permissions, and role-based access control operations.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import joinedload

from app.common.error_handling import ResourceNotFoundError
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors
from app.users.model import User, Role, Permission, RolePermission, UserRoles


class UserRoleService:
    """Service for user role and permission management."""
    
    @handle_errors("Role")
    def get_roles(self) -> tuple:
        """Get all roles."""
        with session_scope() as session:
            roles = session.query(Role).all()
            return [role.json() for role in roles], 200

    @handle_errors("Role")
    def get_role_by_id(self, role_id: str) -> tuple:
        """Get role by ID."""
        with session_scope() as session:
            role = session.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise ResourceNotFoundError("Role")
            return role.json(), 200

    @handle_errors("Role")
    def has_role(self, role_ids: List[str], role_name: str) -> bool:
        """Check if user has specific role."""
        with session_scope() as session:
            role = session.query(Role).filter(Role.name == role_name).first()
            if not role:
                return False
            return role.id in role_ids

    @handle_errors("Role")
    def add_role(self, data: Dict[str, Any]) -> tuple:
        """Add new role."""
        with session_scope() as session:
            role = Role(
                name=data['name'],
                description=data.get('description', ''),
                is_active=data.get('is_active', True)
            )
            session.add(role)
            session.commit()
            return "Role created", 201

    @handle_errors("Role")
    def update_role(self, role_id: str, data: Dict[str, Any]) -> tuple:
        """Update role."""
        with session_scope() as session:
            role = session.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise ResourceNotFoundError("Role")
            
            role.name = data.get('name', role.name)
            role.description = data.get('description', role.description)
            role.is_active = data.get('is_active', role.is_active)
            
            session.commit()
            return "Role updated", 200

    @handle_errors("Permission")
    def add_permission(self, data: Dict[str, Any]) -> tuple:
        """Add new permission."""
        with session_scope() as session:
            permission = Permission(
                name=data['name'],
                description=data.get('description', ''),
                resource=data.get('resource', ''),
                action=data.get('action', ''),
                scope=data.get('scope', 'global')
            )
            session.add(permission)
            session.commit()
            return "Permission created", 201

    @handle_errors("Permission")
    def get_permissions(self) -> tuple:
        """Get all permissions."""
        with session_scope() as session:
            permissions = session.query(Permission).all()
            return [permission.json() for permission in permissions], 200

    @handle_errors("Permission")
    def delete_permission(self, data: Dict[str, Any]) -> tuple:
        """Delete permission."""
        with session_scope() as session:
            permission = session.query(Permission).filter(Permission.id == data['id']).first()
            if not permission:
                raise ResourceNotFoundError("Permission")
            
            session.delete(permission)
            session.commit()
            return "Permission deleted", 200

    @handle_errors("User")
    def get_user_roles_ids(self, user_id: str) -> List[str]:
        """Get user role IDs."""
        with session_scope() as session:
            user_roles = session.query(UserRoles).filter(UserRoles.user_id == user_id).all()
            return [ur.role_id for ur in user_roles]

    @handle_errors("Permission")
    def check_role_permission(self, permission_names: List[str], user_roles_ids: List[str]) -> bool:
        """Check if user roles have specific permissions."""
        with session_scope() as session:
            permissions = session.query(Permission).filter(
                Permission.name.in_(permission_names)
            ).all()
            
            if not permissions:
                return False
            
            role_permissions = session.query(RolePermission).filter(
                RolePermission.role_id.in_(user_roles_ids),
                RolePermission.permission_id.in_([p.id for p in permissions])
            ).all()
            
            return len(role_permissions) > 0

    @handle_errors("RolePermission")
    def add_role_permission(self, data: Dict[str, Any]) -> tuple:
        """Add permission to role."""
        with session_scope() as session:
            role_permission = RolePermission(
                role_id=data['role_id'],
                permission_id=data['permission_id']
            )
            session.add(role_permission)
            session.commit()
            return "Role permission added", 201

    @handle_errors("RolePermission")
    def remove_role_permission(self, role_id: str, permission_id: str) -> tuple:
        """Remove permission from role."""
        with session_scope() as session:
            role_permission = session.query(RolePermission).filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            ).first()
            
            if not role_permission:
                raise ResourceNotFoundError("RolePermission")
            
            session.delete(role_permission)
            session.commit()
            return "Role permission removed", 200

    @handle_errors("RolePermission")
    def get_roles_permissions(self) -> tuple:
        """Get all role-permission mappings."""
        with session_scope() as session:
            role_permissions = session.query(RolePermission).join(
                Role, RolePermission.role_id == Role.id
            ).join(
                Permission, RolePermission.permission_id == Permission.id
            ).all()
            
            result = []
            for rp in role_permissions:
                result.append({
                    'role_id': rp.role_id,
                    'permission_id': rp.permission_id,
                    'role_name': rp.role.name,
                    'permission_name': rp.permission.name
                })
            
            return result, 200
