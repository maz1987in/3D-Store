import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import InventoryCreateSchema, InventoryUpdateSchema, InventoryAdjustmentSchema

from .service import InventoryService

__uri__ = 'inventories'
__blueprint__ = 'inventories'

inventories = Blueprint(__uri__, __name__)

service = InventoryService()

@inventories.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['inventory.show'])
@filters.filters
def get_all_inventories(self, filter):
    inventories, status = service.get_inventories(None, filter)
    if status == 200:
        return APIResponse.success(inventories, "Inventory records retrieved successfully")
    return APIResponse.error("Failed to retrieve inventory records", status_code=status)

@inventories.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['inventory.show'])
@filters.filters
def get_inventory(self, filter, id):
    inventories, status = service.get_inventories(id, filter)
    if status == 200:
        return APIResponse.success(inventories, "Inventory record retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Inventory record not found")
    return APIResponse.error("Failed to retrieve inventory record", status_code=status)

@inventories.route('/products/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['inventory.show'])
@filters.filters
def get_all_inventories_products(self, filter):
    inventories, status = service.get_inventories_products(None, filter)
    if status == 200:
        return APIResponse.success(inventories, "Inventory products retrieved successfully")
    return APIResponse.error("Failed to retrieve inventory products", status_code=status)

@inventories.route('/products/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['inventory.show'])
@filters.filters
def get_inventory_products(self, filter, id):
    inventories, status = service.get_inventories_products(id, filter)
    if status == 200:
        return APIResponse.success(inventories, "Inventory product retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Inventory product not found")
    return APIResponse.error("Failed to retrieve inventory product", status_code=status)


@inventories.route('/status/<id>', methods=['GET'])
def get_inventory_status(id):
    inventories, status = service.get_inventories_status(id)
    if status == 200:
        return APIResponse.success(inventories, "Inventory status retrieved successfully")
    return APIResponse.error("Failed to retrieve inventory status", status_code=status)


@inventories.route('/products/supplier/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['inventory.show'])
@filters.filters
def get_inventories_supplier(self, filter, id):
    inventories, status = service.get_inventories_supplier(id, filter)
    if status == 200:
        return APIResponse.success(inventories, "Supplier inventory retrieved successfully")
    return APIResponse.error("Failed to retrieve supplier inventory", status_code=status)

@inventories.route('/row', methods=['GET'])
@roles.token_required
@filters.filters
def get_inventory_row(self, filter):
    inventories, status = service.get_inventories_grouping(None, filter)
    if status == 200:
        return APIResponse.success(inventories, "Inventory grouping retrieved successfully")
    return APIResponse.error("Failed to retrieve inventory grouping", status_code=status)

@inventories.route('/stock/<store>/<product>', methods=['GET'])
@roles.token_required
def get_inventory_stock(self, store, product):
    inventories, status = service.get_inventories_stock(store, product)
    if status == 200:
        return APIResponse.success(inventories, "Inventory stock retrieved successfully")
    return APIResponse.error("Failed to retrieve inventory stock", status_code=status)

@inventories.route('/inventory/<branch>/<product>', methods=['GET'])
@roles.token_required
def get_inventory_branch(self, branch, product):
    inventories, status = service.get_inventories_branch(branch, product)
    if status == 200:
        return APIResponse.success(inventories, "Branch inventory retrieved successfully")
    return APIResponse.error("Failed to retrieve branch inventory", status_code=status)

@inventories.route('/branch/<branch>', methods=['GET'])
@roles.token_required
@filters.filters
def get_inventory_on_branch(self, filter, branch):
    inventories, status = service.get_inventories_on_branch(branch, filter)
    if status == 200:
        return APIResponse.success(inventories, "Branch inventory retrieved successfully")
    return APIResponse.error("Failed to retrieve branch inventory", status_code=status)

@inventories.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['inventory.add'])
@validate_json(InventoryCreateSchema)
def add_inventory(self, validated_data):
    message, status = service.create_inventory(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Inventory record created successfully")
    return APIResponse.error(message, status_code=status)

@inventories.route('/availablity', methods=['POST'])
#@roles.token_required
def check_inventory():
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.get_products_status(request.json)
    if status == 200:
        return APIResponse.success(message, "Product availability checked successfully")
    return APIResponse.error(message, status_code=status)

@inventories.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['inventory.edit'])
@validate_json(InventoryUpdateSchema)
def update_inventory(self, validated_data, id):
    message, status = service.update_inventory(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Inventory record updated successfully")
    elif status == 404:
        return APIResponse.not_found("Inventory record not found")
    return APIResponse.error(message, status_code=status)


@inventories.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['inventory.delete'])
def delete_inventory(self, id):
    message, status = service.delete_inventory(id)
    if status == 200:
        return APIResponse.success(message, "Inventory record deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Inventory record not found")
    return APIResponse.error(message, status_code=status)
