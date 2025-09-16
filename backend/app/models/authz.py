from __future__ import annotations
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, ForeignKey, JSON, UniqueConstraint, DateTime, text
from typing import Optional, Dict, Any

Base = declarative_base()

# --- Core Models ---
class Permission(Base):
    __tablename__ = 'permissions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    service: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    description_i18n: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    from sqlalchemy import DateTime, text
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), server_onupdate=text('CURRENT_TIMESTAMP'))

class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    description_i18n: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    permissions = relationship('RolePermission', back_populates='role', cascade='all, delete-orphan')
    user_roles = relationship('UserRole', back_populates='role', cascade='all, delete-orphan')
    group_roles = relationship('GroupRole', back_populates='role', cascade='all, delete-orphan')
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), server_onupdate=text('CURRENT_TIMESTAMP'))

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)

    role = relationship('Role', back_populates='permissions')
    permission = relationship('Permission')

    __table_args__ = (UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),)

class Group(Base):
    __tablename__ = 'groups'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description_i18n: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    branch_scope: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    roles = relationship('GroupRole', back_populates='group', cascade='all, delete-orphan')
    user_groups = relationship('UserGroup', back_populates='group', cascade='all, delete-orphan')
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), server_onupdate=text('CURRENT_TIMESTAMP'))

class GroupRole(Base):
    __tablename__ = 'group_roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)

    group = relationship('Group', back_populates='roles')
    role = relationship('Role', back_populates='group_roles')

    __table_args__ = (UniqueConstraint('group_id', 'role_id', name='uq_group_role'),)

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(32))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    locale: Mapped[str] = mapped_column(String(8), default='en')
    tz: Mapped[str] = mapped_column(String(64), default='Asia/Muscat')
    user_groups = relationship('UserGroup', back_populates='user', cascade='all, delete-orphan')
    user_roles = relationship('UserRole', back_populates='user', cascade='all, delete-orphan')
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), server_onupdate=text('CURRENT_TIMESTAMP'))

    def set_password(self, raw: str):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(raw)

    def verify_password(self, raw: str) -> bool:
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, raw)

class UserGroup(Base):
    __tablename__ = 'user_groups'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'group_id', name='uq_user_group'),)
    user = relationship('User', back_populates='user_groups')
    group = relationship('Group', back_populates='user_groups')

class UserRole(Base):
    __tablename__ = 'user_roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='uq_user_role'),)
    user = relationship('User', back_populates='user_roles')
    role = relationship('Role', back_populates='user_roles')
