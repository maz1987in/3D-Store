from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g, current_app

from app.security import roles, permissions
from app.utils.response import APIResponse

from .service import SettingService

__uri__ = 'settings'
__blueprint__ = 'settings'

settings = Blueprint(__uri__, __name__)

service = SettingService()

@settings.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(["setting.show"])
def get_all_settings(self):
    settings, status = service.get_settings(None)
    if status == 200:
        return APIResponse.success(settings, "Settings retrieved successfully")
    return APIResponse.error("Failed to retrieve settings", status_code=status)

@settings.route('/<key>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(["setting.show"])
def get_setting(self, key):
    settings, status = service.get_settings(key)
    if status == 200:
        return APIResponse.success(settings, "Setting retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Setting not found")
    return APIResponse.error("Failed to retrieve setting", status_code=status)

@settings.route('/category/<category>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(["setting.show"])
def get_setting_by_category(self, category):
    settings, status = service.get_settings_by_category(category)
    if status == 200:
        return APIResponse.success(settings, "Category settings retrieved successfully")
    return APIResponse.error("Failed to retrieve category settings", status_code=status)

@settings.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['setting.add'])
def add_setting(self):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.create_setting(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Setting created successfully")
    return APIResponse.error(message, status_code=status)

@settings.route('/<category>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(["setting.edit"])
def update_setting(self, category):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.update_setting(category, request.json)
    if status == 200:
        return APIResponse.success(message, "Settings updated successfully")
    elif status == 404:
        return APIResponse.not_found("Setting category not found")
    return APIResponse.error(message, status_code=status)

@settings.route('/key/<key>', methods=['PATCH'])
#@cross_origin()
@roles.token_required
def update_setting_key(self, key):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.update_setting_key(key, request.json)
    if status == 200:
        return APIResponse.success(message, "Setting updated successfully")
    elif status == 404:
        return APIResponse.not_found("Setting not found")
    return APIResponse.error(message, status_code=status)

@settings.route('/<key>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(["setting.delete"])
def delete_setting(self, key):
    message, status = service.delete_setting(key)
    if status == 200:
        return APIResponse.success(message, "Setting deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Setting not found")
    return APIResponse.error(message, status_code=status)

@settings.route('/reconfig', methods=['GET'])
#@cross_origin()
@permissions.has_permission(["setting.edit"])
def reconfig(self):
    message, status = service.setup_config_from_db()
    if status == 200:
        return APIResponse.success(message, "Configuration reloaded successfully")
    return APIResponse.error(message, status_code=status)
