import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import StoreCreateSchema, StoreUpdateSchema

from .service import StoreService

__uri__ = 'stores'
__blueprint__ = 'stores'

stores = Blueprint(__uri__, __name__)

service = StoreService()

@stores.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['store.show'])
@filters.filters
def get_all_stores(self, filter):
    stores, status = service.get_stores(None, filter)
    if status == 200:
        return APIResponse.success(stores, "Stores retrieved successfully")
    return APIResponse.error("Failed to retrieve stores", status_code=status)

@stores.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['store.show'])
@filters.filters
def get_store(self, filter, id):
    stores, status = service.get_stores(id, filter)
    if status == 200:
        return APIResponse.success(stores, "Store retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Store not found")
    return APIResponse.error("Failed to retrieve store", status_code=status)

@stores.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['store.add'])
@validate_json(StoreCreateSchema)
def add_store(self, validated_data):
    message, status = service.create_store(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Store created successfully")
    return APIResponse.error(message, status_code=status)

@stores.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['store.edit'])
@validate_json(StoreUpdateSchema)
def update_store(self, validated_data, id):
    message, status = service.update_store(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Store updated successfully")
    elif status == 404:
        return APIResponse.not_found("Store not found")
    return APIResponse.error(message, status_code=status)


@stores.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['store.delete'])
def delete_store(self, id):
    message, status = service.delete_store(id)
    if status == 200:
        return APIResponse.success(message, "Store deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Store not found")
    return APIResponse.error(message, status_code=status)
