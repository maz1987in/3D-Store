import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from app.utilities.common_utils import is_valid_uuid
from .schemas import BranchCreateSchema, BranchUpdateSchema

from .service import BranchService

__uri__ = 'branchs'
__blueprint__ = 'branchs'

branchs = Blueprint(__uri__, __name__)

service = BranchService()

@branchs.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['branch.show'])
@filters.filters
def get_all_branchs(self, filter):
    branchs, status = service.get_branchs(None, filter)
    if status == 200:
        return APIResponse.success(branchs, "Branches retrieved successfully")
    return APIResponse.error("Failed to retrieve branches", status_code=status)

@branchs.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['branch.show'])
@filters.filters
def get_branch(self, filter, id):
    if is_valid_uuid(id):
        branchs, status = service.get_branchs(id, filter)
        if status == 200:
            return APIResponse.success(branchs, "Branch retrieved successfully")
        elif status == 404:
            return APIResponse.not_found("Branch not found")
        return APIResponse.error("Failed to retrieve branch", status_code=status)
    return APIResponse.error("Invalid branch ID format", status_code=400)

@branchs.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['branch.add'])
@validate_json(BranchCreateSchema)
def add_branch(self, validated_data):
    message, status = service.create_branch(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Branch created successfully")
    return APIResponse.error(message, status_code=status)

@branchs.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['branch.edit'])
@validate_json(BranchUpdateSchema)
def update_branch(self, validated_data, id):
    message, status = service.update_branch(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Branch updated successfully")
    elif status == 404:
        return APIResponse.not_found("Branch not found")
    return APIResponse.error(message, status_code=status)


@branchs.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['branch.delete'])
def delete_branch(self, id):
    message, status = service.delete_branch(id)
    if status == 200:
        return APIResponse.success(message, "Branch deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Branch not found")
    return APIResponse.error(message, status_code=status)
