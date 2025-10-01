from operator import not_
from os import abort
import jwt
import sqlalchemy as sql
import uuid 
from datetime import datetime, timezone
import string
import random

from flask import url_for, render_template, current_app
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.sqltypes import Unicode
from werkzeug.security import generate_password_hash
from sqlalchemy_filters import apply_pagination
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from app.common.constants import HASH_METHOD
from app.common.enum import RoleEnum
from app.common.error_handling import ResourceNotFoundError
from app.utilities import request_utils
from app.utilities.common_utils import debug_return, get_random_value, remove_leading_plus
from app.utilities.request_utils import not_exisit_in_request, str_to_bool

from extensions import cache
from config import BaseConfig, SecretKey

from .model import User, Role, Tracking, RolePermission, Permission, UserRoles

from app.common import filters_serialization
from app.common.queries import apply_sort, create_sorters, filter_and_sort_query, filter_query, create_filters
from app.security.mail import generate_confirmation_token, send_email
from app.utilities.db_utils import get_session_with_retries, session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

SECRET_KEY = SecretKey().SECRET_KEY

class UserService:
    #def __init__(self):
    #    self.session = get_session_with_retries()

    def get_user_model(self, users, with_password=False):
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

    # check if user with same user_id and user_type exists
    @handle_errors("User")
    def is_user_id_exist(self, user_id, user_type):
        with session_scope() as session:
            user = session.query(User).filter(User.user_id == user_id, User.user_type == user_type).first()
            return user is not None

    # create (sing-up) new user
    @handle_errors("User")
    def create_user(self, data):
        with session_scope() as session:
            phone = '{0}{1}'.format(data['code'], remove_leading_plus(data['phone']))
            phone = remove_leading_plus(phone)
            email = data['email'] if data['email'] is not None else None
            user_type = not_exisit_in_request(data, 'user_type', 'USER')
            if user_type not in ['USER', 'CORPORATE', 'OWNER']:
                return 'Invalid user type', 400

            if self.is_user_exist(phone, email):
                return 'User already exists', 409
            if 'user_id' in data and self.is_user_id_exist(data['user_id'], user_type):
                return 'User ID already exists', 409

            user = User(
                id=uuid.uuid4(),
                password=data['password'],
                name=not_exisit_in_request(data, 'name', None),
                email=email,
                user_type=user_type,
                user_details=data['user_details'],
                language=not_exisit_in_request(data, 'language', 'ARABIC'),
                user_id=not_exisit_in_request(data, 'user_id', None),
                phone=phone,
                username=phone,
                active=0,
                agree=data['agree'],
                agree_date=datetime.now(timezone.utc)
            )

            role_type = data['role'] if data['role'] is not None else 'User'
            role = session.query(Role).filter(Role.name == role_type).first()
            user.roles.append(role)

            session.add(user)
            session.commit()

            if user:
                token = generate_confirmation_token(user.email)
                confirm_url = url_for('signup.confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "[Raheeq App] Please Verify Your Email Address."
                send_email(user.email, subject, html)

            return "Confirmation Email Sent", 200

    @handle_errors("User")
    def is_user_exist(self, phone, email=None):
        with session_scope() as session:
            user = session.query(User).filter(User.phone == phone).first()
            if user:
                return True
            if email:
                user = session.query(User).filter(User.email == email).first()
            return user is not None

    @handle_errors("User")
    def create_user_admin(self, data):
        with session_scope() as session:
            phone = '{0}{1}'.format(data['code'], remove_leading_plus(data['phone'])) if 'code' in data else remove_leading_plus(data['phone'])
            phone = remove_leading_plus(phone)
            user = User(
                id=uuid.uuid4(),
                password=not_exisit_in_request(data, 'password', get_random_value(8)),
                name=not_exisit_in_request(data, 'name', None),
                email=data['email'],
                user_type=not_exisit_in_request(data, 'user_type'),
                language=not_exisit_in_request(data, 'language', 'ARABIC'),
                phone=phone,
                username=data['username'],
                user_id=not_exisit_in_request(data, 'user_id'),
                user_details=data['user_details'],
                active=str_to_bool(data, 'is_active', False)
            )

            role_type = data['role'] if data['role'] is not None else 'Public'
            role = session.query(Role).filter(Role.name == role_type).first()
            user.roles.append(role)

            session.add(user)
            session.commit()

            return "User Created.", 201

    @handle_errors("User")
    def update_user(self, id, data):
        with session_scope() as session:
            user_type = not_exisit_in_request(data, 'user_type', 'USER')
            if user_type not in ['USER', 'CORPORATE', 'OWNER']:
                return 'Invalid user type', 400

            user = session.query(User).filter(User.id == id).first()
            user.user_details = data['user_details']
            user.name = not_exisit_in_request(data, 'name', user.name)

            session.commit()

            return "User Updated.", 200

    @handle_errors("User")
    def add_user_id_image(self, user_id, image, replace=False):
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if user.user_id_image and replace:
                user.user_id_image = image
            elif not user.user_id_image:
                user.user_id_image = image
            else:
                return 'Image already added', 401

            session.commit()
            return "User Updated.", 200
        #finally:
        #    self.session.close()
    @handle_errors("User")
    def update_user_admin(self, id, data):
        with session_scope() as session:
            user = session.query(User).filter(User.id == id).first()
            
            role = session.query(Role).filter(Role.name == user.roles[0].name).first()
            user.roles.remove(role)

            user.active = str_to_bool(data, 'is_active', user.active)
            user.user_type = not_exisit_in_request(data, 'user_type', user.user_type)
            user.language = not_exisit_in_request(data, 'language', 'ARABIC')
            user.user_details = not_exisit_in_request(data, 'user_details', user.user_details)
            user.email = not_exisit_in_request(data, 'email', user.email)
            user.phone = not_exisit_in_request(data, 'phone', user.phone)
            user.username = not_exisit_in_request(data, 'username', user.username)

            role = session.query(Role).filter(Role.name == data['role']).first()
            user.roles.append(role)

            session.commit()

            return "User Updated.", 200

    @handle_errors("User")
    def get_oauth_user(self, provider, oauth_id):
        with session_scope() as session:
            user = session.query(User).filter(User.oauth[provider].as_string() == oauth_id).first()
            
            if not user:
                return None 

            token = jwt.encode({'id': str(user.id), 'exp': datetime.now(timezone.utc) + datetime.timedelta(days=BaseConfig.JWT_EXPIRATION_DELTA)}, SECRET_KEY, "HS256")

            return ({'token': token, 'id': str(user.id), 'user_details': user.user_details, 'phone': user.phone, 'email': user.email, 'type': 'Public', 'mobile_confirmed_at': user.mobile_confirmed_at, 'email_confirmed_at': user.email_confirmed_at})

    @handle_errors("User")
    def create_oauth_user(self, data):
        with session_scope() as session:
            mobile = remove_leading_plus(data['phone'])
            user = session.query(User).filter(User.phone == mobile).first()

            if user:
                user.email = data['email']
                user.email_confirmed_at = datetime.now(timezone.utc)
                user.oauth = data['oauth']
            else:
                user = User(
                    id=uuid.uuid4(),
                    email=data['email'], 
                    phone=mobile, 
                    username=mobile,
                    name=not_exisit_in_request(data, 'name', None),
                    language=not_exisit_in_request(data, 'language', 'ARABIC'),
                    active=1,
                    email_confirmed_at=datetime.now(timezone.utc),
                    mobile_confirmed_at=datetime.now(timezone.utc),
                    oauth=data['oauth']
                )

                role_type = data['role'] if data['role'] is not None else 'Public'
                role = session.query(Role).filter(Role.name == role_type).first()
                user.roles.append(role)

                session.add(user)

            session.commit()
            
            token = jwt.encode({'id': str(user.id), 'exp': datetime.now(timezone.utc) + datetime.timedelta(days=BaseConfig.JWT_EXPIRATION_DELTA)}, SECRET_KEY, "HS256")

            return ({'token': token, 'id': str(user.id), 'user_details': user.user_details, 'phone': user.phone, 'email': user.email, 'type': 'Public', 'mobile_confirmed_at': user.mobile_confirmed_at, 'email_confirmed_at': user.email_confirmed_at})

    @handle_errors("User")
    def get_user_json_by_id(self, id):
        with session_scope() as session:
            user = session.query(User).filter(User.id == id).first()
            if not user:
                return {}, 404
            user_data = {}   
            user_data['id'] = user.id
            user_data['is_active'] = user.active
            user_data['phone'] = user.phone
            user_data['username'] = user.username
            user_data['name'] = user.name
            user_data['email'] = user.email
            user_data['user_id'] = user.user_id
            user_data['user_id_image'] = request_utils.get_media_url(user.user_id_image)
            user_data['user_type'] = user.user_type.value if user.user_type else None
            user_data['language'] = user.language.value if user.language else None
            user_data['mobile_confirmed_at'] = user.mobile_confirmed_at
            user_data['email_confirmed_at'] = user.email_confirmed_at
            user_data['user_details'] = user.user_details
            user_data['roles'] = [role.name for role in user.roles]
            result = {'users': user_data}
            return result, 200
    @handle_errors("User")
    def get_users(self, filter):
        with session_scope() as session:
            query = session.query(User)
            if filter.sort is None:
                filter.sorters = create_sorters('create_date', 'desc')
            query = filter_and_sort_query(filter.filters, filter.sorters, query, User)
            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            users = query.all()
            result_users = []
            for user in users:
                user_data = {
                    'id': user.id,
                    'is_active': user.active,
                    'phone': user.phone,
                    'username': user.username,
                    'name': user.name,
                    'email': user.email,
                    'user_id': user.user_id,
                    'user_id_image': request_utils.get_media_url(user.user_id_image),
                    'user_type': user.user_type.value if user.user_type else None,
                    'language': user.language.value if user.language else None,
                    'mobile_confirmed_at': user.mobile_confirmed_at,
                    'email_confirmed_at': user.email_confirmed_at,
                    'create_date': user.create_date,
                    'modified_date': user.modified_date,
                    'user_details': user.user_details,
                    'roles': [role.name for role in user.roles]
                }
                result_users.append(user_data)
            result = {'users': result_users, 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            return result, 200

    # TODO: remove this method
    @handle_errors("User")
    def get_user_admin(self, id):
        with session_scope() as session:
            if id is None:
                users = session.query(User).all()
            else:
                users = session.query(User).filter(User.id == id).all()
            
            result = []  

            for user in users:
                user_data = {}   
                user_data['id'] = user.id
                user_data['is_active'] = user.active
                user_data['phone'] = user.phone
                user_data['username'] = user.username
                user_data['name'] = user.name
                user_data['email'] = user.email
                user_data['user_id'] = user.user_id
                user_data['user_id_image'] = request_utils.get_media_url(user.user_id_image)
                user_data['user_type'] = user.user_type.value if user.user_type else None
                user_data['language'] = user.language.value if user.language else None
                user_data['role'] = user.roles[0].name if user.roles else ''
                user_data['mobile_confirmed_at'] = user.mobile_confirmed_at
                user_data['email_confirmed_at'] = user.email_confirmed_at
                user_data['user_details'] = user.user_details
                user_data['roles'] = [role.name for role in user.roles]

                result.append(user_data)
            
            return result, 200
    @handle_errors("User")
    def get_users_by_user_type(self, user_type):
        with session_scope() as session:
            users = session.query(User).filter(User.user_type == user_type).all()
            result = []

            for user in users:
                user_data = {}
                user_data['id'] = user.id
                user_data['is_active'] = user.active
                user_data['phone'] = user.phone
                user_data['username'] = user.username
                user_data['name'] = user.name
                user_data['email'] = user.email
                user_data['user_id'] = user.user_id
                user_data['user_id_image'] = request_utils.get_media_url(user.user_id_image)
                user_data['user_type'] = user.user_type.value if user.user_type else None
                user_data['language'] = user.language.value if user.language else None
                result.append(user_data)

            return result, 200

    @handle_errors("User")
    def get_users_by_role(self, role):
        with session_scope() as session:
            users = session.query(User, Role, UserRoles).filter(UserRoles.user_id == User.id, UserRoles.role_id == Role.id).filter(sql.func.lower(Role.name) == sql.func.lower(role)).all()

            result = []

            for user in users:
                user_data = {}
                user_data['id'] = user.User.id
                user_data['phone'] = user.User.phone
                user_data['username'] = user.User.username
                user_data['name'] = user.User.name
                user_data['email'] = user.User.email
                user_data['user_details'] = user.User.user_details

                result.append(user_data)

            return result, 200

    @handle_errors("User")
    def get_user_by_email(self, email):
        with session_scope() as session:
            user = session.query(User, Role).join(User.roles).options(joinedload(User.roles)).filter(User.email == email).first()
            return user

    @handle_errors("User")
    def get_user_admin_by_any(self, param,with_password=False):
        with session_scope() as session:
            mobile = remove_leading_plus(param)
            query = session.query(User, Role).join(User.roles).options(joinedload(User.roles))
            query = query.filter(or_(User.email == param, User.phone == mobile))
            query = query.filter(not_(Role.name == RoleEnum.PUBLIC.value))
            user = query.first()
            if user is None:
                return None, 404
            return self.get_user_model(user, with_password), 200

    @handle_errors("User")
    def get_user_role_by_id(self, id):
        with session_scope() as session:
            query = session.query(User, Role).join(User.roles).options(joinedload(User.roles))
            query = query.filter(User.id == id)
            user = query.first()
            if user is None:
                return None, 404
            return self.get_user_model(user), 200

    @handle_errors("User")
    def get_user_by_any(self, param, with_password=False):
        with session_scope() as session:
            mobile = remove_leading_plus(param)
            query = session.query(User, Role).join(User.roles).options(joinedload(User.roles))
            query = query.filter(or_(User.email == param, User.phone == mobile))
            user = query.first()
            if user is None:
                return None, 404
            return self.get_user_model(user, with_password), 200

    @handle_errors("User")
    def get_user_by_mobile(self, mobile):
        with session_scope() as session:
            mobile = remove_leading_plus(mobile)
            user = session.query(User).filter(User.phone == mobile).first()
            if user is None:
                return None, 404
            return self.get_user_model(user), 200

    @handle_errors("User")
    def get_user_by_id(self, id):
        with session_scope() as session:
            user = session.query(User).filter_by(id=id).first()
            if user is None:
                return None, 404
            return self.get_user_model(user), 200

    @handle_errors("User")
    def user_logins(self, data):
        with session_scope() as session:
            track = Tracking(id=uuid.uuid4(), date=data['date'], status=data['status'], user_id=data['user_id'])
            session.add(track)
            session.commit()
            return "ok", 200

    @handle_errors("User")
    def user_confirmed_mobile(self, mobile):
        with session_scope() as session:
            mobile = remove_leading_plus(mobile)
            user = session.query(User).filter(User.phone == mobile).first()

            if user.active:
                return 'Account already confirmed. Please login.', 200

            user.active = True
            user.mobile_confirmed_at = datetime.now(timezone.utc)
            session.commit()

            return 'Mobile Confirmation Updated!', 200

    @handle_errors("User")
    def user_confirmed(self, email):
        with session_scope() as session:
            user = session.query(User).filter(User.email == email).first()

            if user.active:
                return 'Account already confirmed. Please login.'
            else:
                user.active = True
                user.email_confirmed_at = datetime.now(timezone.utc)
                session.commit()
                return 'You have confirmed your account. Thanks!'

    @handle_errors("User")
    def update_user_password(self, id, data):
        with session_scope() as session:
            user = session.query(User).filter(User.id == id).first()
            if 'password' not in data:
                return 'Password is required', 400
            user.password = data['password']
            session.commit()
            return "Password updated", 200

    @handle_errors("User")
    def forget_password(self, email):
        with session_scope() as session:
            user = session.query(User).filter(User.email == email).first()

            password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            hash_password = generate_password_hash(password, method=HASH_METHOD)

            user.password = hash_password
            user.active = 0
            if not user.email_confirmed_at:
                user.mobile_confirmed_at = datetime.now(timezone.utc)

            session.commit()

            token = generate_confirmation_token(user.email)
            confirm_url = url_for('signup.confirm_email', token=token, _external=True)
            html = render_template('forget.html', new_password=password, confirm_url=confirm_url)
            subject = "New Password"
            send_email(user.email, subject, html)

            return "The new password has been sent via email.", 200

    @handle_errors("User")
    def delete_user(self, id):
        with session_scope() as session:
            user = session.query(User).filter(User.id == id).first()
            if user is None:
                raise ResourceNotFoundError("User")
            session.delete(user)
            session.commit()
            return 'Deleted', 200
        
    @handle_errors("User")
    def disable_user_1(self, id, data):
        with session_scope() as session:
            user = session.query(User).filter(User.id == id).first()

            if user is None:
                raise ResourceNotFoundError("User")
            
            user.active = data['active']
            session.add(user)
            session.commit()

            return 'Disabled', 200

    @handle_errors("User")
    def disable_user(self, id):
        with session_scope() as session:
            user = session.query(User).filter(User.id == id).first()

            if user is None:
                raise ResourceNotFoundError("User")

            user.active = 0
            session.commit()

            return 'Disabled', 200

    @handle_errors("User")
    def enable_user(self, id):
        with session_scope() as session:
            user = session.query(User).filter(User.id == id).first()

            if user is None:
                raise ResourceNotFoundError("User")

            user.active = 1
            session.commit()

            return 'Enabled', 200

    # get all roles
    @handle_errors("Role")
    def get_roles(self):
        with session_scope() as session:
            roles = session.query(Role).all()

            result = [] 

            for role in roles:   
                role_data = {}   
                role_data['id'] = role.id 
                role_data['name'] = role.name
                role_data['description'] = role.description

                result.append(role_data)

            return result

    @handle_errors("Role")
    def get_role_by_id(self, id):
        with session_scope() as session:
            role = session.query(Role).filter(Role.id == id).first()

            if role is None:
                raise ResourceNotFoundError("Role")

            return role

    @handle_errors("Role")
    def has_role(self, role_ids, role_name):
        with session_scope() as session:
            query = session.query(Role).filter(Role.id.in_(role_ids)).filter(Role.name == role_name)
            roles = query.all()
            if not roles:
                return False

            return True

    @handle_errors("Role")
    def add_role(self, data):
        with session_scope() as session:
            role = Role(
                name=data['name'],
                description=not_exisit_in_request(data, 'description', None)
            )  # type: ignore

            session.add(role)
            session.commit()

            return role.id, 201

    @handle_errors("Role")
    def update_role(self, id, data):
        with session_scope() as session:
            role = session.query(Role).filter(Role.id == id).first()
            role.name = data['name']
            role.description = not_exisit_in_request(data, 'description', role.description)

            session.commit()

            return "Role updated", 200
    # Permissions 
    @handle_errors("Permission")
    def add_permission(self, data):
        with session_scope() as session:
            permission = Permission(
                name=data['name'],
                model=not_exisit_in_request(data, 'model', None),
            )
            session.add(permission)
            session.commit()
            return "Permission added", 200

    @handle_errors("Permission")
    def get_permissions(self):
        with session_scope() as session:
            permissions = session.query(Permission).order_by(Permission.name).all()
            result = []
            for permission in permissions:
                data = {
                    'id': permission.id,
                    'name': permission.name,
                    'model': permission.model
                }
                result.append(data)
            return result

    @handle_errors("User")
    @cache.memoize(60 * 60)
    def get_user_roles_ids(self, id):
        with session_scope() as session:
            user = session.query(User).filter(User.id == id).first()
            if user is None:
                return []
            if user.roles:
                return [role.id for role in user.roles]

    @handle_errors("Permission")
    @cache.memoize(60 * 60)
    def check_role_permission(self, permission_names, user_roles_ids):
        with session_scope() as session:
            permissions = session.query(RolePermission, Permission).filter(
                Permission.id == RolePermission.permission_id
            ).filter(
                Permission.name.in_(permission_names)
            ).filter(
                RolePermission.role_id.in_(user_roles_ids)
            ).all()

            if not permissions:
                return False, None

            return True, [permission.Permission.name for permission in permissions]

    @handle_errors("User")
    def show_logins(self):
        with session_scope() as session:
            logins = session.query(Tracking, User).filter(User.id == Tracking.user_id).all()
            result = []
            return result

    @handle_errors("RolePermission")
    def add_role_permission(self, data):
        with session_scope() as session:
            role_permission = RolePermission(role_id=data['role_id'], permission_id=data['permission_id'])
            session.add(role_permission)
            session.commit()
            return "Permission has been added to role", 200

    @handle_errors("RolePermission")
    def remove_role_permission(self, id, pid):
        with session_scope() as session:
            role_permission = session.query(RolePermission).filter(
                RolePermission.role_id == id, RolePermission.permission_id == pid
            ).first()

            if not role_permission:
                raise ResourceNotFoundError("RolePermission")

            session.delete(role_permission)
            session.commit()
            return "Permission has been deleted from role", 200

    @handle_errors("RolePermission")
    def get_roles_permissions(self):
        with session_scope() as session:
            role_permission = session.query(RolePermission).all()
            result = []

            for permission in role_permission:
                data = {}
                data['id'] = permission.id
                data['role_id'] = permission.role_id
                data['permission_id'] = permission.permission_id
                result.append(data)

            return result, 200

    @handle_errors("Permission")
    def delete_permission(self, data):
        with session_scope() as session:
            permission = session.query(Permission).filter(Permission.id == data['permission_id']).first()
            if not permission:
                raise ResourceNotFoundError("Permission")

            session.delete(permission)
            session.query(RolePermission).filter_by(permission_id=permission.id).delete(synchronize_session=False)
            session.commit()
            return "Permission has been deleted", 200

    
    @handle_errors("User")
    def search_user(self, param, filter):
        with session_scope() as session:
            query = session.query(User).filter(
                or_(
                    User.user_details.ilike('%{}%'.format(param)),
                    User.email.ilike('%{}%'.format(param)),
                    User.phone.ilike('%{}%'.format(param)),
                    User.username.ilike('%{}%'.format(param))
                )
            )

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))

            users = query.all()
            
            result_users = []
            for user in users:
                user_data = {}   
                user_data['id'] = user.id
                user_data['phone'] = user.phone
                user_data['username'] = user.username
                user_data['email'] = user.email
                user_data['user_details'] = user.user_details
                result_users.append(user_data)

            result = {'users': result_users, 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            return result, 200

    @handle_errors("User")
    def get_users_statistics(self):
        with session_scope() as session:
            active = session.query(User).filter_by(active=True).count()
            inactive = session.query(User).filter_by(active=False).count()
            total = session.query(User).count()
            return {"active": active, "inactive": inactive, "total": total}, 200
