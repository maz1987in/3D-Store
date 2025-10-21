"""
Modern JSON-based authentication endpoints
Compatible with Angular frontend
"""
import jwt 
from datetime import timezone, datetime, timedelta
from extensions import limiter
from flask_cors import cross_origin
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from threading import Thread

from app.users.service import UserService
from app.utilities.common_utils import get_jwt_exp_delta
from config import SecretKey
from app.utils.response import APIResponse

__uri__ = 'auth'
__blueprint__ = 'auth'

auth = Blueprint(__uri__, __name__)
SECRET_KEY = SecretKey().SECRET_KEY

service = UserService()

def log_user_login(data):
    service.user_logins(data)

@auth.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin()
@limiter.limit("10 per minute")
def json_login():
    """JSON-based login endpoint for modern frontends"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        from database import Session
        from app.users.model import User
        from sqlalchemy import or_
        
        data = request.get_json()
        if not data:
            return APIResponse.error('Request body is required', status_code=400)
        
        # Accept both 'username' and 'email' fields for flexibility
        username = data.get('username') or data.get('email')
        password = data.get('password')
        
        if not username or not password:
            return APIResponse.error('Email/username and password are required', status_code=400)
        now = datetime.now(timezone.utc)
        
        # Direct database query to find user
        session = Session()
        try:
            user = session.query(User).filter(
                or_(User.email == username, User.phone == username, User.username == username)
            ).first()
        finally:
            session.close()
        
        if user is None:
            return APIResponse.error('Invalid credentials', status_code=401)
        
        if not user.active:
            return APIResponse.error('User is not active', status_code=401)
        
        if check_password_hash(user.password, password):
            payload = {
                'id': str(user.id),
                'exp': datetime.now(timezone.utc) + get_jwt_exp_delta()
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            
            response_data = {
                'token': token,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'phone': user.phone,
                    'name': user.name,
                    'user_type': user.user_type.value,
                    'active': user.active
                }
            }
            
            return APIResponse.success(response_data, 'Login successful')
        
        return APIResponse.error('Invalid credentials', status_code=401)
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return APIResponse.error(f'Login failed: {str(e)}', status_code=500)


@auth.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin()
@limiter.limit("5 per minute")
def json_register():
    """JSON-based registration endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password', 'name']):
            return APIResponse.error('Email, password, and name are required', status_code=400)
        
        # Create user
        message, status = service.create_user(data)
        
        if status == 200:
            # Auto-login after registration
            user, user_status = service.get_user_by_any(data['email'], with_password=False)
            
            if user_status == 200 and user:
                payload = {
                    'id': str(user['id']),
                    'exp': datetime.now(timezone.utc) + get_jwt_exp_delta()
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                
                response_data = {
                    'token': token,
                    'user': {
                        'id': str(user['id']),
                        'email': user['email'],
                        'phone': user.get('phone'),
                        'name': user['name'],
                        'user_type': user['user_type'],
                        'roles': user['roles']
                    }
                }
                
                return APIResponse.success(response_data, 'Registration successful')
        
        return APIResponse.error(message, status_code=status)
        
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return APIResponse.error(f'Registration failed: {str(e)}', status_code=500)


@auth.route('/logout', methods=['POST', 'OPTIONS'])
@cross_origin()
def json_logout():
    """JSON-based logout endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # For now, logout is client-side only
    # In the future, you could invalidate tokens here
    return APIResponse.success(message='Logged out successfully')


@auth.route('/profile', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_profile():
    """Get current user profile"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # This would require token authentication
    return APIResponse.error('Not implemented yet', status_code=501)


@auth.route('/refresh', methods=['POST', 'OPTIONS'])
@cross_origin()
def refresh_token():
    """Refresh JWT token"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # This would implement token refresh logic
    return APIResponse.error('Not implemented yet', status_code=501)

