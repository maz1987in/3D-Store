import jwt 
from datetime import timezone, datetime, timedelta
from app.common.constants import MAX_PASSWORD_LENGTH
from extensions import limiter
from flask_cors import CORS, cross_origin
from flask import Blueprint, redirect, request, jsonify, abort, make_response, current_app, session
import requests
from werkzeug.security import check_password_hash
from app.common.enum import RoleEnum
from app.common.json_classes import Oauth
from app.security import roles

from app.security.mail import confirm_token, generate_confirmation_token
from app.users.service import UserService
from app.utilities.common_utils import get_jwt_exp_delta
from .otp import get_user_otp, verify_OTP
from config import BaseConfig, Config, SecretKey, OAuthConfig
from requests_oauthlib import OAuth2Session
from threading import Thread

login = Blueprint('login', __name__)
SECRET_KEY = SecretKey().SECRET_KEY

service = UserService()

#CORS(login, supports_credentials=True, resources={r"/*": {"origins": BaseConfig.CORS_ORIGINS}})

def log_user_login(data):
    service.user_logins(data)

# login by both mbile or email
@login.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login_any():
    auth = request.authorization
    now = datetime.now(timezone.utc)

    if not auth or not auth.username or not auth.password:
        Thread(target=log_user_login, args=({'date': now, 'status': 'could not verify, 401', 'user_id': None},)).start()
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    if len(auth.password) > MAX_PASSWORD_LENGTH:
        return make_response('Password Too long', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    
    user, user_status = service.get_user_by_any(auth.username, with_password=True)

    if user_status != 200 or user is None:
        Thread(target=log_user_login, args=({'date': now, 'status': 'User not found, 404', 'user_id': None},)).start()
        return make_response('User not found', 404, {'WWW.Authentication': 'Basic realm: "login required"'})
    
    if not user['active']:
        Thread(target=log_user_login, args=({'date': now, 'status': 'User is not active, 401', 'user_id': str(user['id'])},)).start()
        return make_response('User is not active!', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    if check_password_hash(user['password'], auth.password):
        Thread(target=log_user_login, args=({'date': now, 'status': 'ok, 200', 'user_id': str(user['id'])},)).start()
        payload = {'id': str(user['id']), 'exp': datetime.now(timezone.utc) + get_jwt_exp_delta()}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        response = { 'token' : token, 'id' : str(user['id']), 'user_details': user['user_details'], 'phone': user['phone'], 'user_type': user['user_type'], 'email': user['email'], 'type': user['roles'], 'mobile_confirmed_at': user['mobile_confirmed_at'], 'email_confirmed_at': user['email_confirmed_at'], 'name': user['name'], 'registrationDate': user['create_date'], 'role': user['roles'][0]}
        #response['token'] = token
        return jsonify(response), 200
    
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

@login.route('/admin', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login_admin():
    auth = request.authorization
    now = datetime.now(timezone.utc)

    if not auth or not auth.username or not auth.password:
        Thread(target=log_user_login, args=({'date': now, 'status': 'could not verify, 401', 'user_id': None},)).start()
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    if len(auth.password) > MAX_PASSWORD_LENGTH:
        return make_response('Password Too long', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user, status = service.get_user_admin_by_any(auth.username, with_password=True)

    if status != 200 or user is None:
        Thread(target=log_user_login, args=({'date': now, 'status': 'User not found, 404', 'user_id': None},)).start()
        return make_response('User not found', 404, {'WWW.Authentication': 'Basic realm: "login required"'})

    if not user['active']:
        Thread(target=log_user_login, args=({'date': now, 'status': 'User is not active, 401', 'user_id': user['id']},)).start()
        return make_response('User is not active!', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    if check_password_hash(user['password'], auth.password):
        Thread(target=log_user_login, args=({'date': now, 'status': 'ok, 200', 'user_id': user['id']},)).start()
        payload = {
            'id': str(user['id']),
            'exp': datetime.now(timezone.utc) + get_jwt_exp_delta()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        response = {
            'token': token,
            'id': user['id'],
            'role': user['roles'][0],
            'email': user['email'],
            'user_details': user['user_details'],
            'name': user['name']
        }
        return jsonify(response), 200

    Thread(target=log_user_login, args=({'date': now, 'status': 'could not verify, 401', 'user_id': user['id']},)).start()
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

@login.route('/resetpassword', methods=['GET', 'POST'])
#@cross_origin()
@limiter.limit("5 per minute")
@roles.token_required
def login_reset_password(self):
    #current_app.logger.error(request.json)
    message, status = service.update_user_password(self.id, request.json)

    return jsonify({'status': message, 'code': status}), status

@login.route('/forgotpassword/', methods=['POST'])
#@cross_origin()
@limiter.limit("5 per minute")
def login_forgot_password():
    try:
        data = request.json
        forget_password = service.get_user_by_any(data['email'])
        if forget_password is None:
            return jsonify({'response': 'User Not Found.','status': 404}), 404
        message, status = service.forget_password(data['email'])
        return jsonify({'msg': message}), status
        '''
        country_code = data['country_code']
        phone_number = remove_leading_plus(data['phone_number'])
        phone = '{0}{1}'.format(country_code, phone_number)
        local = data['local'] if 'local' in data and data['local'] is not None else Config().DEFAULT_LOCALE

        user = service.get_user_by_mobile(phone)

        if user is None:
            return jsonify({'response': 'User Not Found.','status': 404}), 404

        token = get_user_otp(data, phone, local)

        return jsonify({'token' : token,'status': 200}), 200
        '''
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'response': 'Internal Server Error','status': 400}), 400

## signup ##
signup = Blueprint('signup', __name__)

@signup.route('/', methods=['POST'])
#@cross_origin()
@limiter.limit("3 per minute")
def signup_user():
    if not request.json or not 'phone' in request.json:
        abort(404)
    if not 'role' in request.json:
        abort(404, description="Role not found")

    response, status = service.create_user(request.json)
    return jsonify({'status': response, 'code': status}), status

## signup -> confirm ##
@signup.route('/confirm/<token>')
@limiter.limit("3 per minute")
def confirm_email(token):
    try:
        email = confirm_token(token)
    except Exception as e:
        return 'The confirmation link is invalid or has expired.'
    
    message = service.user_confirmed(email)
    
    return message
