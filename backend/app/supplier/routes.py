import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import SupplierCreateSchema, SupplierUpdateSchema

from .service import SupplierService

__uri__ = 'suppliers'
__blueprint__ = 'suppliers'

suppliers = Blueprint(__uri__, __name__)

service = SupplierService()

@suppliers.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['supplier.show'])
@filters.filters
def get_all_suppliers(self, filter):
    suppliers, status = service.get_suppliers(None, filter)
    if status == 200:
        return APIResponse.success(suppliers, "Suppliers retrieved successfully")
    return APIResponse.error("Failed to retrieve suppliers", status_code=status)

@suppliers.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['supplier.show'])
@filters.filters
def get_supplier(self, filter, id):
    suppliers, status = service.get_suppliers(id, filter)
    if status == 200:
        return APIResponse.success(suppliers, "Supplier retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Supplier not found")
    return APIResponse.error("Failed to retrieve supplier", status_code=status)

@suppliers.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['supplier.add'])
@validate_json(SupplierCreateSchema)
def add_supplier(self, validated_data):
    message, status = service.create_supplier(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Supplier created successfully")
    return APIResponse.error(message, status_code=status)

@suppliers.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['supplier.edit'])
@validate_json(SupplierUpdateSchema)
def update_supplier(self, validated_data, id):
    message, status = service.update_supplier(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Supplier updated successfully")
    elif status == 404:
        return APIResponse.not_found("Supplier not found")
    return APIResponse.error(message, status_code=status)


@suppliers.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['supplier.delete'])
def delete_supplier(self, id):
    message, status = service.delete_supplier(id)
    if status == 200:
        return APIResponse.success(message, "Supplier deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Supplier not found")
    return APIResponse.error(message, status_code=status)