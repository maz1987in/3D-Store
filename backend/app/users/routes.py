from datetime import datetime, timezone, timedelta
import json
import jwt
from app.common.json_classes import Oauth
from app.security.login import SECRET_KEY
import requests
from urllib.parse import urlencode

from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g, current_app

from requests_oauthlib import OAuth1Session, OAuth1

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import UserCreateSchema, UserUpdateSchema, PasswordChangeSchema, RoleCreateSchema, PermissionCreateSchema
from app.utilities.common_utils import get_random_digits_value
from app.utilities.request_utils import dump_request

from config import BaseConfig, OAuthConfig

from .service import UserService

__uri__ = 'users'
__blueprint__ = 'users'

users = Blueprint(__uri__, __name__)

service = UserService()

@users.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['user.show.all'])
@filters.filters
def get_users(self, filter):
    result, status = service.get_users(filter)
    if status == 200:
        return APIResponse.success(result, "Users retrieved successfully")
    return APIResponse.error("Failed to retrieve users", status_code=status)

@users.route('/type/<user_type>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['user.show.all'])
def get_users_by_user_type(self, user_type):
    users = service.get_users_by_user_type(user_type)
    return APIResponse.success({'users': users}, f"Users of type {user_type} retrieved successfully")


@users.route('/role/<role>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['user.role.show'])
def get_users_by_role(self, role):
    return jsonify({'users': service.get_users_by_role(role)})

@users.route('/<id>', methods=['GET'])
#@cross_origin()
@roles.token_required
def get_user(self, id):
    user, status = service.get_user_json_by_id(id)
    return jsonify(user), status

@users.route('/<id>/password', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['user.edit'])
@validate_json(PasswordChangeSchema)
def change_user_password(self, validated_data, id):
    message, status = service.update_user_password(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Password changed successfully")
    elif status == 404:
        return APIResponse.not_found("User not found")
    return APIResponse.error(message, status_code=status)

@users.route('/search/<param>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['user.show.all'])
@filters.filters
def search_user(filter,self, param):
    users , status = service.search_user(param,filter)
    return jsonify({'users': users}), status

@users.route('/my', methods=['GET'])
#@cross_origin()
@roles.token_required
def get_my_user(self):
    user, status = service.get_user_json_by_id(self.id)
    return jsonify(user), status

@users.route('/my', methods=['PATCH'])
#@cross_origin()
@roles.token_required
def edit_user(self):
    message, status = service.update_user(self.id, request.json)
    return jsonify({'msg': message}), status

@users.route('/my/image', methods=['POST'])
#@cross_origin()
@roles.token_required
def edit_user_image(self):
    id_card_image = request.files['id_card_image'] if 'id_card_image' in request.files else None

    msg, status = service.add_user_id_image(self.id, id_card_image)
    return jsonify({'msg': msg}), status

@users.route('/image/<id>', methods=['POST'])
@permissions.has_permission(['user.edit'])
def add_user_id_image(self, id):
    id_card_image = request.files['id_card_image'] if 'id_card_image' in request.files else None

    msg, status = service.add_user_id_image(id, id_card_image)
    return jsonify({'msg': msg}), status


@users.route('/admin', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['user.add'])
def add_user_for_admin(self):
    if not request.json:
        abort(404)    
    message, status = service.create_user_admin(request.json)
    return jsonify({'msg': message}), status

@users.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['user.delete'])
def delete_user(self, id):
    message, status = service.delete_user(id)
    if status == 200:
        return APIResponse.success(message, "User deleted successfully")
    elif status == 404:
        return APIResponse.not_found("User not found")
    return APIResponse.error(message, status_code=status)

@users.route('/admin/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['user.edit'])
def edit_user_admin(self, id):
    message, status = service.update_user_admin(id, request.json)
    if status == 200:
        return APIResponse.success(message, "User updated successfully")
    elif status == 404:
        return APIResponse.not_found("User not found")
    return APIResponse.error(message, status_code=status)

@users.route('/admin/loginas/<id>', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['user.loginas'])
def login_as_user(self, id):
    user, status = service.get_user_role_by_id(id)
    if user is None or status != 200:
        return jsonify({'msg': 'User not found'}), 404
        token = jwt.encode({'id': str(user.User.id), 'exp': datetime.now(timezone.utc) + timedelta(days=BaseConfig.JWT_EXPIRATION_DELTA)}, SECRET_KEY, algorithm="HS256")

    return jsonify({ 'token' : token, 'id' : str(user.User.id), 'user_details': user.User.user_details, 'phone': user.User.phone, 'email': user.User.email, 'type': user.Role.name, 'mobile_confirmed_at': user.User.mobile_confirmed_at, 'email_confirmed_at': user.User.email_confirmed_at, 'id_flag': True if user.User.user_id_image else False}), 200

    #return jsonify(token), status

@users.route('/disable/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['user.disable'])
def disable_user(self, id):
    message, status = service.disable_user(id)
    if status == 200:
        return APIResponse.success(message, "User disabled successfully")
    elif status == 404:
        return APIResponse.not_found("User not found")
    return APIResponse.error(message, status_code=status)

@users.route('/enable/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['user.disable'])
def enable_user(self, id):
    message, status = service.enable_user(id)
    if status == 200:
        return APIResponse.success(message, "User enabled successfully")
    elif status == 404:
        return APIResponse.not_found("User not found")
    return APIResponse.error(message, status_code=status)

## roles ##
@users.route('/roles', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['role.show'])
def get_roles(self):
    roles = service.get_roles()
    return APIResponse.success({'roles': roles}, "Roles retrieved successfully")

@users.route('/roles', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['role.add'])
@validate_json(RoleCreateSchema)
def add_role(self, validated_data):
    role_id, status = service.add_role(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created({'role_id': role_id}, "Role created successfully")
    return APIResponse.error("Failed to create role", status_code=status)

@users.route('/roles/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['role.edit'])
def update_role(self, id):
    message, status = service.update_role(id, request.json)
    if status == 200:
        return APIResponse.success(message, "Role updated successfully")
    elif status == 404:
        return APIResponse.not_found("Role not found")
    return APIResponse.error(message, status_code=status)

## permissions ##
@users.route('/permissions', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['permission.show'])
def get_permissions(self):
    permissions = service.get_permissions()
    return APIResponse.success({'permissions': permissions}, "Permissions retrieved successfully")

@users.route('/permissions', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['permission.add'])
def add_permission(self):
    if not request.json:
        abort(404)    
    message, status = service.add_permission(request.json)
    return jsonify({'msg': message}), status

# permissions routes
@users.route('/add-permission', methods=['POST'])
#@cross_origin()
#@roles.token_required
@permissions.has_permission(['permission.add'])
def add_permssion(self):
    message, status = service.add_role_permission(request.json)
    return jsonify({'msg':message}), status

@users.route('/delete-role-permission/<id>/<pid>', methods=['delete'])
#@cross_origin()
#@roles.token_required
@permissions.has_permission(['permission.delete'])
def remove_permssion(self, id, pid):
    message, status = service.remove_role_permission(id, pid)
    return jsonify({'msg':message}), status

@users.route('/roles-permissions', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['role.show'])
def roles_permissions(self):
    data, status = service.get_roles_permissions()
    return jsonify({'roles_permissions': data}), status

@users.route('/delete-permission', methods=['delete'])
#@cross_origin()
#@roles.token_required
@permissions.has_permission(['permission.delete'])
def edit_permssion():
    message, status = service.delete_permission(data=request.get_json())
    return jsonify({'msg':message}), status


# @users.route('/edit-permission', methods=['POST'])
# def edit_permssion():
#     message, status = service.edit_permission_name(data=request.get_json())
#     return jsonify({'msg':message}), status


#login with google
@users.route('/google-login', methods=['GET','POST'])
#@cross_origin()
def auth_google():
    try:
        current_app.logger.error('google-login')
        prams = request.json if request.is_json else request.form.to_dict()
        current_app.logger.error(prams)
        # print all request headers and values to the log
        

        #auth_url = 'https://www.googleapis.com/oauth2/v3/userinfo?alt=json'
        #access_token = prams['access_token']
        #current_app.logger.error(access_token)
        
        #res = requests.post(auth_url,headers={'Authorization':f'Bearer {access_token}'})
        #res_json = res.json()
        #current_app.logger.error(res_json)
        access_token = prams['access_token']
        profile_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'},
        )
        
        profile_response.raise_for_status()
        profile = profile_response.json()
        #print(profile)
        oauth_id = profile.get('sub')

        #oauth_id = res_json.get('sub')
        if oauth_id is None:
            return jsonify({'success':False, 'message':'Sorry can not access your google account'})
        token = service.get_oauth_user('google',oauth_id)
        
        if token:
            return jsonify(token)
        
        if token is None:
            return jsonify({'success': False, 'message': 'User not found', 'status': 404})

        return jsonify({'success':False, 'message':'Sorry can not access your google account'})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'success':False, 'message':str(e)})


@users.route('/google-signup', methods=['GET','POST'])
#@cross_origin()
def auth_google_signup():
    try:
        current_app.logger.error('google-login')
        # print all request headers and values to the log
        #current_app.logger.error(request.__dict__)
        #current_app.logger.error(request.headers)
        #current_app.logger.error(request.cookies)
        #current_app.logger.error(request.data)
        #current_app.logger.error(request.args)
        #current_app.logger.error(request.form)
        #current_app.logger.error(request.json if request.is_json else 'No JSON') 
        #current_app.logger.error(dump_request(request))
        prams = request.json if request.is_json else request.form.to_dict()
        current_app.logger.error(prams)

        #auth_url = 'https://www.googleapis.com/oauth2/v3/userinfo?alt=json'
        #access_token = prams['access_token']
        mobile = prams['phone']
        access_token = prams['access_token']
        
        profile_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'},
        )
        
        profile_response.raise_for_status()
        profile = profile_response.json()
        #print(profile)
        if profile.get('sub') is None:
            return jsonify({'success':False, 'message':'Sorry can not access your google account'})
        oauth = Oauth(profile.get('sub'),None,None,None)
        data = {'email':profile.get('email'),
                'oauth':oauth.to_json(),
                'phone': mobile,
                'role':'Public'}

        token = service.create_oauth_user(data)
        
        if token:
            return jsonify(token)
        
        if token is None:
            return jsonify({'success': False, 'message': 'User not found', 'status': 404})

        return jsonify({'success':False, 'message':'Sorry can not access your google account'})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'success':False, 'message':str(e)})

# twitter login
@users.route('/twitter')
#@cross_origin()
def twitter():
    try:
        oauth = OAuth1(
                    OAuthConfig.OAUTH_TWITTER_CONSUMER_KEY,
                    OAuthConfig.OAUTH_TWITTER_CONSUMER_SECRET
                )

        request_token_url = 'https://api.twitter.com/oauth/request_token'
        data = urlencode({
                            'oauth_callback': OAuthConfig.OAUTH_TWITTER_CALLBACK
        })

        response = requests.post(request_token_url, auth=oauth, data=data)
        response_split = response.text.split('&')
        oauth_token = response_split[0].split('=')[1] 
        
        twitter_redirect_url = (
            f'https://api.twitter.com/oauth/authenticate?oauth_token={oauth_token}'
            )
        return jsonify({'url':twitter_redirect_url})
    except ConnectionError:
        html='<html><body>You have no internet connection</body></html>'
        return  html
    except Exception as e:
        html='<html><body>Something went wrong.Try again.</body></html>'
        return html


# twitter callback
@users.route('/callback/twitter')
#@cross_origin()
def twitter_callback():
    try:
        oauth_token = request.args.get('oauth_token')
        oauth_verifier = request.args.get('oauth_verifier')
        oauth = OAuth1Session(
                        OAuthConfig.OAUTH_TWITTER_CONSUMER_KEY,
                        OAuthConfig.OAUTH_TWITTER_CONSUMER_SECRET,
                        resource_owner_key=oauth_token,
                        verifier=oauth_verifier,
        )
        url = 'https://api.twitter.com/oauth/access_token'
        access_token_data = oauth.post(url, data={})

        res_split = access_token_data.text.split('&')
        oauth_token = res_split[0].split('=')[1]
        oauth_secret = res_split[1].split('=')[1]
        user_id = res_split[2].split('=')[1] if len(res_split) > 2 else None
        user_name = res_split[3].split('=')[1] if len(res_split) > 3 else None
    
        oauth_user = OAuth1Session(client_key=OAuthConfig.OAUTH_TWITTER_CONSUMER_KEY,
                               client_secret=OAuthConfig.OAUTH_TWITTER_CONSUMER_SECRET,
                               resource_owner_key=oauth_token,
                               resource_owner_secret=oauth_secret)
        
        url_user = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        params = {'include_email': 'true'}
        user_data = oauth_user.get(url_user, params=params)
        
        oauth = Oauth(None,None,user_id,None)
        data = {'email':user_data.json().get('email'),
                'oauth':oauth.to_json(),
                'username':user_name,
                'role':'user'}
        
        token = service.create_oauth_user(data)
        if token:   
            return jsonify({'token':token})

        return jsonify({'done':'ok'})
    except ConnectionError:
        return '<html><body>You have no internet connection</body></html>'
    except Exception as e:
        return '<html><body>Something went wrong.Try again.</body></html>'


# apple login
@users.route('/auth/apple',methods=['POST'])
def apple_auth():

    id_token = request.form.get('id_token')
    user_data = request.form.get('user',None)
    username = None
    if user_data:
        user_data = json.loads(user_data)
        firstname = user_data.get('name').get('firstName')
        lastname = user_data.get('name').get('lastName')
        username = firstname+lastname
        
    apple_user_data = jwt.decode(id_token, '',
                                 audience=OAuthConfig.APPLE_CLIENT_ID,  
                                 options={'verify_signature':False})

    email =  apple_user_data.get('email')
    oauth_id = apple_user_data.get('sub')

    oauth = Oauth(None,None,None,oauth_id)

    data = {'email':email,
                'oauth':oauth.to_json(),
                'username':username or 'apple'+email.split('@')[0]+str(get_random_digits_value(4)),
                'role':'user'}
    
    token = service.create_oauth_user(data)
    if token:   
        return jsonify({'token':token})
    
    # need to change in production
    apple_response = '<script> if (window.opener) { window.opener.postMessage("apple_token:%s", "http://localhost:4200/home"); window.close(); }</script>'%id_token

    return jsonify({'message':'Can not create account'})
