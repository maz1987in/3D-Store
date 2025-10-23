from depot.fields.sqlalchemy import UploadedFileField
import uuid
import re
import sqlalchemy as sql
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql.schema import UniqueConstraint
from werkzeug.security import generate_password_hash
from app.common.constants import HASH_METHOD
from app.common.enum import LanguageEnum, UserTypeEnum

from database import Base
from sqlalchemy_utils.types.uuid import UUIDType

class User(Base):
    __tablename__ = 'users'
 
    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    active = sql.Column('is_active', sql.Boolean(), nullable=False, server_default='0', index=True)
    
    username = sql.Column(sql.String(length=255), unique=True, nullable=False)
    phone = sql.Column(sql.String(255), nullable=False, unique=True)
    email = sql.Column(sql.String(255), nullable=True, unique=True)
    user_type = sql.Column(sql.Enum(UserTypeEnum),server_default='USER', index=True)
    language = sql.Column(sql.Enum(LanguageEnum),server_default='ARABIC', index=True)
    user_id = sql.Column(sql.String(255), nullable=True)
    user_id_image = sql.Column(UploadedFileField(upload_storage ='user'), nullable=True)
    # user details as an object (in JSON)
    user_details = sql.Column(sql.JSON)
    name = sql.Column(sql.String(255), nullable=True)
    
    mobile_confirmed_at = sql.Column(sql.DateTime())
    email_confirmed_at = sql.Column(sql.DateTime())
    password = sql.Column(sql.String(255), nullable=False, server_default='')

    agree = sql.Column('is_agree', sql.Boolean(), nullable=False, server_default='0')
    agree_date = sql.Column(sql.DateTime())

    create_date = sql.Column(sql.DateTime(), default=sql.func.now(), index=True)
    modified_date = sql.Column(sql.DateTime(), default=sql.func.now(), onupdate=sql.func.now(), index=True)
    note = sql.Column(sql.String(length=255), server_default=None)

    # Define the relationship to Role via UserRoles
    roles = relationship('Role', secondary='user_roles')

    # Relationship to Tracking
    track = relationship('Tracking')

    ratings = relationship("Rating", back_populates="user")
    # In your User model
    shipping_addresses = relationship("ShippingAddress", back_populates="user", cascade="all, delete-orphan")

    # OAuth unique value for google (sub), for twitter(id)
    oauth = sql.Column(sql.JSON)
    #oauth_id = sql.Column(sql.String(length=255))

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            return None
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Use a raw string (r"...")
            raise AssertionError('Provided email is not an email address')
        return email
    
    @validates('password')
    def set_password(self, key, password): 
        if not password:
            raise AssertionError('Password not provided')
        if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            raise AssertionError('Provided password is not valid')
        if len(password) < 8 or len(password) > 50:
            raise AssertionError('Password must be between 8 and 50 characters')

        return generate_password_hash(password, method=HASH_METHOD)

    def json(self,with_password=False):
        data = {}
        data['id'] = self.id
        data['active'] = self.active
        data['username'] = self.username
        if with_password:
            data['password'] = self.password
        data['name'] = self.name
        data['phone'] = self.phone
        data['email'] = self.email
        data['language'] = self.language
        data['user_details'] = self.user_details
        data['user_type'] = self.user_type.value
        data['user_id'] = self.user_id
        data['user_id_image'] = str(self.user_id_image) if self.user_id_image else None
        data['mobile_confirmed_at'] = self.mobile_confirmed_at
        data['email_confirmed_at'] = self.email_confirmed_at
        data['agree'] = self.agree
        data['agree_date'] = self.agree_date
        data['create_date'] = self.create_date
        data['modified_date'] = self.modified_date
        data['note'] = self.note
        data['shipping_addresses'] = [addr.json() for addr in self.shipping_addresses]
        return data
    
    def for_notification(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['phone'] = self.phone
        data['email'] = self.email
        data['language'] = self.language
        data['user_details'] = self.user_details
        return data
    
    def for_short(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['user_id'] = self.user_id
        data['phone'] = self.phone
        data['user_details'] = self.user_details
        return data

# Define the Role data-model
class Role(Base):
    __tablename__ = 'roles'
    id = sql.Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    name = sql.Column(sql.String(50), unique=True)
    description = sql.Column(sql.String(255))

    # Define the relationship to Permissions via UserRoles
    permissions = relationship('Permission', secondary='role_permissions')

    def json(self):
        data = {}
        data["id"] = self.id
        data["name"] = self.name
        data["description"] = self.description
        return data


# Define the UserRoles association table
class UserRoles(Base):
    __tablename__ = 'user_roles'

    id = sql.Column(UUIDType(binary=False),default=uuid.uuid4, primary_key=True)
    user_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id', ondelete='CASCADE', name='fk_user_roles_user_id'), index=True)
    role_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('roles.id', ondelete='CASCADE', name='fk_user_roles_role_id'), index=True)
    def json(self):
        data = {}
        data["id"] = self.id
        data["user_id"] = self.user_id
        data["role_id"] = self.role_id
        return data


class Tracking(Base):
    __tablename__ = 'login_tracking'

    id = sql.Column(UUIDType(binary=False),default=uuid.uuid4, primary_key=True)
    date = sql.Column(sql.DateTime())
    status = sql.Column(sql.String(length=255))
    others = sql.Column(sql.String(length=255), server_default=None)

    user_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id', ondelete='CASCADE', name='fk_login_tracking_user_id'))

    def json(self):
        data = {}
        data["id"] = self.id
        data["date"] = self.date
        data["status"] = self.status
        data["others"] = self.others
        data["user_id"] = self.user_id
        return data

# Permission Model
class Permission(Base):
    __tablename__ = 'permissions'

    id = sql.Column(UUIDType(binary=False),default=uuid.uuid4, primary_key=True)
    model = sql.Column(sql.String(100), nullable=True)
    name = sql.Column(sql.String(100), unique=True, nullable=False)

    def json(self):
        data = {}
        data["id"] = self.id
        data["model"] = self.model
        data["name"] = self.name
        return data


# Relation Between User and Permissions
class RolePermission(Base):
    __tablename__ = 'role_permissions'
    
    id = sql.Column(UUIDType(binary=False),default=uuid.uuid4, primary_key=True)
    role_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('roles.id', ondelete='CASCADE', name='fk_role_permissions_role_id'), index=True)
    permission_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('permissions.id', ondelete='CASCADE', name='fk_role_permissions_permission_id'),index=True)
    __table_args__ = (sql.UniqueConstraint('role_id', 'permission_id',name='uq_role_permissions'),)

    def json(self):
        data = {}
        data["id"] = self.id
        data["role_id"] = self.role_id
        data["permission_id"] = self.permission_id
        return data
