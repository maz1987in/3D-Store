import json
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import StaffCreateSchema, StaffUpdateSchema

from .service import StaffService

__uri__ = 'staffs'
__blueprint__ = 'staffs'

staffs = Blueprint(__uri__, __name__)

service = StaffService()

@staffs.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['staff.show'])
@filters.filters
def get_all_staffs(self, filter):
    staffs, status = service.get_staffs(None, filter)
    if status == 200:
        return APIResponse.success(staffs, "Staff members retrieved successfully")
    return APIResponse.error("Failed to retrieve staff members", status_code=status)

@staffs.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['staff.show'])
@filters.filters
def get_staff(self, filter, id):
    staffs, status = service.get_staffs(id, filter)
    if status == 200:
        return APIResponse.success(staffs, "Staff member retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Staff member not found")
    return APIResponse.error("Failed to retrieve staff member", status_code=status)

@staffs.route('/', methods=['POST'])
#@cross_origin()
@roles.token_required
def add_staff(self):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list = dictionary['form']
        param = json.loads(list[0])

    if not param:
        return APIResponse.validation_error("No staff data provided")
    
    message, status = service.create_staff(param, request.files)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Staff member created successfully")
    return APIResponse.error(message, status_code=status)

@staffs.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['staff.edit'])
def update_staff(self, id):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list = dictionary['form']
        param = json.loads(list[0])
    
    message, status = service.update_staff(id, param, request.files)
    if status == 200:
        return APIResponse.success(message, "Staff member updated successfully")
    elif status == 404:
        return APIResponse.not_found("Staff member not found")
    return APIResponse.error(message, status_code=status)

@staffs.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['staff.delete'])
def delete_staff(self, id):
    message, status = service.delete_staff(id)
    if status == 200:
        return APIResponse.success(message, "Staff member deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Staff member not found")
    return APIResponse.error(message, status_code=status)

@staffs.route('/<id>/reindex', methods=['GET'])
@permissions.has_permission(['staff.show.all', 'staff.show.own'])
def reindex_staff(self, id):
    response, status = service.reindex_staff_attachments(id)
    if status == 200:
        return APIResponse.success(response, "Staff attachments reindexed successfully")
    return APIResponse.error("Failed to reindex staff attachments", status_code=status)

@staffs.route('/upload/<id>/<int:order>', defaults={'new': None}, methods=['POST'])
@staffs.route('/upload/<id>/<int:order>/<new>', methods=['POST'])
@permissions.has_permission(['staff.add.all', 'staff.add.own'])
def staff_upload_file(self, id, order, new=None):
    if not request.files:
        return APIResponse.validation_error("No files provided in the request")
    
    is_new = new is not None
    message, files, status = service.upload_staff_files(id, request.files.getlist('file'), order, is_new)
    
    if status == 200:
        return APIResponse.success({'msg': message, 'files': files}, "Files uploaded successfully")
    return APIResponse.error(message, status_code=status)

@staffs.route('/upload/<id>', methods=['DELETE'])
@permissions.has_permission(['staff.add.all', 'staff.add.own'])
def staff_delete_upload_file(self, id):
    message, status = service.delete_staff_file(id)
    if status == 200:
        return APIResponse.success(message, "File deleted successfully")
    elif status == 404:
        return APIResponse.not_found("File not found")
    return APIResponse.error(message, status_code=status)
