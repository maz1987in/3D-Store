import jwt

from flask import request, jsonify, abort, make_response,current_app, g
from werkzeug.security import check_password_hash
from functools import wraps

from app.users.service import UserService
from app.utilities.request_utils import not_exisit_in_request
from config import SecretKey

user_service = UserService()
SECRET_KEY = SecretKey().SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, "HS256")
            current_user, status = user_service.get_user_by_id(data['id'])
            g.user = current_user
            #g.owner = not_exisit_in_request(data,'owner',current_user.id)
        except jwt.ExpiredSignatureError:
                return jsonify({'message': 'token is expired'}), 401
        except Exception as e:
            #current_app.logger.error(e)
            return jsonify({'message': 'token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorator

def has_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if token:
            #return jsonify({'message': 'a valid token is missing'}), 401
            try:
                data = jwt.decode(token, SECRET_KEY, "HS256")
                current_user, status = user_service.get_user_by_id(data['id'])
                g.user = current_user
                #g.owner = not_exisit_in_request(data,'owner',current_user.id)
            #except jwt.ExpiredSignatureError:
            #        return jsonify({'message': 'token is expired'}), 401
            except Exception as e:
                #current_app.logger.error(e)
                return f(*args, **kwargs)
        
        return f(*args, **kwargs)
    return decorator
    
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            if 'x-access-tokens' in request.headers:
                token = request.headers['x-access-tokens']

            if not token:
                return jsonify({'message': 'a valid token is missing'}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                
                current_user,status = user_service.get_user_by_id(data['id'])
                
                user_roles_ids = user_service.get_user_roles_ids(current_user.id)
                has_role = user_service.has_role(user_roles_ids,role)
                #user_role, user_role_status = user_service.get_role_by_id(current_user.role_id)

                if not has_role:
                    return jsonify({'message': 'You dont have permission to access this resource.'}), 401
            except Exception as e:
                return jsonify({'message': 'token is invalid'}), 401
            
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator
