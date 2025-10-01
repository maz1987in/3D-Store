from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g, current_app

from app.security import roles, permissions

from .service import SettingService

__uri__ = 'settings'
__blueprint__ = 'settings'

settings = Blueprint(__uri__, __name__)

service = SettingService()

@settings.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(["setting.show"])
@roles.token_required
def get_all_settings(self):
    settings, status = service.get_settings(None)
    return jsonify(settings), status

@settings.route('/<key>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(["setting.show"])
#@roles.token_required
def get_setting(key):
    settings, status = service.get_settings(key)
    return jsonify(settings), status

@settings.route('/category/<category>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(["setting.show"])
@roles.token_required
def get_setting_by_category(self, category):
    settings, status = service.get_settings_by_category(category)
    return jsonify(settings), status

@settings.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['setting.add'])
@roles.token_required
def add_setting(self):
    if not request.json:
        abort(404)    
    message, status = service.create_setting(request.json)
    return jsonify({'msg': message}), status

@settings.route('/<category>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(["setting.edit"])
@roles.token_required
def update_setting(self, category):
    message, status = service.update_setting(category, request.json)
    return jsonify({'msg': message}), status

@settings.route('/key/<key>', methods=['PATCH'])
#@cross_origin()
@roles.token_required
def update_setting_key(self, key):
    message, status = service.update_setting_key(key, request.json)
    return jsonify({'msg': message}), status

@settings.route('/<key>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(["setting.delete"])
@roles.token_required
def delete_setting(self, key):
    message, status = service.delete_setting(key)
    return jsonify({'msg': message}), status

@settings.route('/reconfig', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(["setting.edit"])
@roles.token_required
def reconfig(self):
    message, status = service.setup_config_from_db()
    return jsonify({'msg': message}), status

