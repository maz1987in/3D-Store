import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse

from .service import LaborService

__uri__ = 'labors'
__blueprint__ = 'labors'

labors = Blueprint(__uri__, __name__)

labor_service = LaborService()

@labors.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['labor.show'])
@filters.filters
def get_all_labors(self, filter):
    labors, status = labor_service.get_labors(None, filter)
    if status == 200:
        return APIResponse.success(labors, "Labor records retrieved successfully")
    return APIResponse.error("Failed to retrieve labor records", status_code=status)

@labors.route('/f/', methods=['GET'])
@roles.token_required
@filters.filters
def get_labors_f(self, filter):
    labors, status = labor_service.get_labors_f(filter)
    if status == 200:
        return APIResponse.success(labors, "Labor records retrieved successfully")
    return APIResponse.error("Failed to retrieve labor records", status_code=status)

@labors.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['labor.show'])
@filters.filters
def get_labor(self, filter, id):
    labors, status = labor_service.get_labors(id, filter)
    if status == 200:
        return APIResponse.success(labors, "Labor record retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Labor record not found")
    return APIResponse.error("Failed to retrieve labor record", status_code=status)

@labors.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['labor.add'])
def add_labor(self):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = labor_service.create_labor(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Labor record created successfully")
    return APIResponse.error(message, status_code=status)

@labors.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['labor.edit'])
def update_labor(self, id):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = labor_service.update_labor(id, request.json)
    if status == 200:
        return APIResponse.success(message, "Labor record updated successfully")
    elif status == 404:
        return APIResponse.not_found("Labor record not found")
    return APIResponse.error(message, status_code=status)


@labors.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['labor.delete'])
def delete_labor(self, id):
    message, status = labor_service.delete_labor(id)
    if status == 200:
        return APIResponse.success(message, "Labor record deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Labor record not found")
    return APIResponse.error(message, status_code=status)

@labors.route('/category/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['labor_category.show'])
@filters.filters
def get_all_labor_categories(self, filter):
    categories, status = labor_service.get_labor_categories(None, filter)
    if status == 200:
        return APIResponse.success(categories, "Labor categories retrieved successfully")
    return APIResponse.error("Failed to retrieve labor categories", status_code=status)

@labors.route('/category/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['labor_category.show'])
@filters.filters
def get_labor_category(self, filter, id):
    categories, status = labor_service.get_labor_categories(id, filter)
    if status == 200:
        return APIResponse.success(categories, "Labor category retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Labor category not found")
    return APIResponse.error("Failed to retrieve labor category", status_code=status)

@labors.route('/category/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['labor_category.add'])
def add_labor_category(self):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = labor_service.create_labor_category(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Labor category created successfully")
    return APIResponse.error(message, status_code=status)

@labors.route('/category/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['labor_category.edit'])
def update_labor_category(self, id):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = labor_service.update_labor_category(id, request.json)
    if status == 200:
        return APIResponse.success(message, "Labor category updated successfully")
    elif status == 404:
        return APIResponse.not_found("Labor category not found")
    return APIResponse.error(message, status_code=status)


@labors.route('/category/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['labor_category.delete'])
def delete_labor_category(self, id):
    message, status = labor_service.delete_labor_category(id)
    if status == 200:
        return APIResponse.success(message, "Labor category deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Labor category not found")
    return APIResponse.error(message, status_code=status)
