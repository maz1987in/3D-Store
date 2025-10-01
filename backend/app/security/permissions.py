import jwt
from functools import wraps
import uuid
from flask  import current_app, request, jsonify, g
from sqlalchemy.sql.operators import is_

from app.users.service import UserService
from app.utilities.request_utils import not_exisit_in_request
from config import SecretKey

user_service = UserService()
SECRET_KEY = SecretKey().SECRET_KEY

def has_permission(permission_names):
    def is_authenticated(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            token = None

            if 'x-access-tokens' in request.headers:
                token = request.headers['x-access-tokens']
           
            # Check for the token in the query parameters
            if not token:
                token = request.args.get('token')

            if not token:
                return jsonify({'message': 'a valid token is missing'}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, "HS256")
                current_user = user_service.get_user_by_id(data['id'])
                g.user = current_user
                g.owner = not_exisit_in_request(data,'owner',g.user.id)
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'token is expired'}), 401
            except Exception as e:
                return jsonify({'message': 'token is invalid'}), 401

            user_roles_ids = user_service.get_user_roles_ids(g.user.id)
            

            #print(current_user.__dict__)
            #print('\n'.join(map(str, user_roles_ids))) 
            
            if current_app.config['ENV'] == 'development' and uuid.UUID('c4b0a125-660b-4c20-93f6-385ff3e4847a') in user_roles_ids:
                g.permission = permission_names
                return func(current_user, *args, **kwargs)
             
            is_permitted , permission = user_service.check_role_permission(permission_names, user_roles_ids)
            g.permission = permission
            if (is_permitted):
                return func(current_user, *args, **kwargs)

            return jsonify({'message': 'Sorry you do not have Permission'}), 403 

        return decorated_function
    return is_authenticated
