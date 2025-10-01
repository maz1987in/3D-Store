import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utilities.common_utils import is_valid_uuid

from .service import BranchService

__uri__ = 'branchs'
__blueprint__ = 'branchs'

branchs = Blueprint(__uri__, __name__)

service = BranchService()

@branchs.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['branch.show'])
@roles.token_required
@filters.filters
def get_all_branchs(filter,self):
    branchs, status = service.get_branchs(None,filter)
    return jsonify(branchs), status

@branchs.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['branch.show'])
@roles.token_required
@filters.filters
def get_branch(filter,self, id):
    if is_valid_uuid(id):
        branchs, status = service.get_branchs(id, filter)
        return jsonify(branchs), status
    abort(404)

@branchs.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['branch.add'])
@roles.token_required
def add_branch(self):
    if not request.json:
        abort(404)
    message, status = service.create_branch(request.json)
    return jsonify({'msg': message}), status

@branchs.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['branch.edit'])
@roles.token_required
def update_branch(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_branch(id,request.json)
    return jsonify({'msg': message}), status


@branchs.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['branch.delete'])
@roles.token_required
def delete_branch(self, id):
    message, status = service.delete_branch(id)
    return jsonify({'msg': message}), status