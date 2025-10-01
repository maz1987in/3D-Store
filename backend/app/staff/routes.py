import json
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import StaffService

__uri__ = 'staffs'
__blueprint__ = 'staffs'

staffs = Blueprint(__uri__, __name__)

service = StaffService()

@staffs.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['staff.show'])
@roles.token_required
@filters.filters
def get_all_staffs(filter, self):
    staffs, status = service.get_staffs(None, filter)
    return jsonify(staffs), status

@staffs.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['staff.show'])
@roles.token_required
@filters.filters
def get_staff(filter, self, id):
    staffs, status = service.get_staffs(id, filter)
    return jsonify(staffs), status

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
        abort(404)
    message, status = service.create_staff(param, request.files)
    return jsonify({'msg': message}), status

@staffs.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['staff.edit'])
@roles.token_required
def update_staff(self, id):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list = dictionary['form']
        param = json.loads(list[0])
    message, status = service.update_staff(id, param, request.files)
    return jsonify({'msg': message}), status

@staffs.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['staff.delete'])
@roles.token_required
def delete_staff(self, id):
    message, status = service.delete_staff(id)
    return jsonify({'msg': message}), status

@staffs.route('/<id>/reindex', methods=['GET'])
#@permissions.has_permission(['staff.show.all', 'staff.show.own'])
@roles.token_required
def reindex_staff(self, id):
    response, status = service.reindex_staff_attachments(id)
    return jsonify(response), status

@staffs.route('/upload/<id>/<int:order>', defaults={'new': None}, methods=['POST'])
@staffs.route('/upload/<id>/<int:order>/<new>', methods=['POST'])
#@permissions.has_permission(['staff.add.all', 'staff.add.own'])
@roles.token_required
def staff_upload_file(self, id, order, new=None):
    if not request.files:
        abort(404)
    is_new = new is not None

    message, files, status = service.upload_staff_files(id, request.files.getlist('file'), order, is_new)
    return jsonify({'msg': message, 'files': files}), status

@staffs.route('/upload/<id>', methods=['DELETE'])
#@permissions.has_permission(['staff.add.all', 'staff.add.own'])
@roles.token_required
def staff_delete_upload_file(self, id):
    message, status = service.delete_staff_file(id)
    return jsonify({'msg': message}), status