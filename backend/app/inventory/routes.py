import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import InventoryService

__uri__ = 'inventories'
__blueprint__ = 'inventories'

inventories = Blueprint(__uri__, __name__)

service = InventoryService()

@inventories.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['inventory.show'])
@roles.token_required
@filters.filters
def get_all_inventories(filter,self):
    inventories, status = service.get_inventories(None,filter)
    return jsonify(inventories), status

@inventories.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['inventory.show'])
@roles.token_required
@filters.filters
def get_inventory(filter,self, id):
    inventories, status = service.get_inventories(id, filter)
    return jsonify(inventories), status

@inventories.route('/products/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['inventory.show'])
#@roles.token_required
@filters.filters
def get_all_inventories_products(filter):
    inventories, status = service.get_inventories_products(None,filter)
    return jsonify(inventories), status

@inventories.route('/products/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['inventory.show'])
#@roles.token_required
@filters.filters
def get_inventory_products(filter, id):
    inventories, status = service.get_inventories_products(id, filter)
    return jsonify(inventories), status


@inventories.route('/status/<id>', methods=['GET'])
def get_inventory_status(id):
    inventories, status = service.get_inventories_status(id)
    return jsonify(inventories), status


@inventories.route('/products/supplier/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['inventory.show'])
#@roles.token_required
@filters.filters
def get_inventories_supplier(filter, id):
    inventories, status = service.get_inventories_supplier(id, filter)
    return jsonify(inventories), status

@inventories.route('/row', methods=['GET'])
@roles.token_required
@filters.filters
def get_inventory_row(filter,self):
    inventories, status = service.get_inventories_grouping(None, filter)
    return jsonify(inventories), status

@inventories.route('/stock/<store>/<product>', methods=['GET'])
@roles.token_required
def get_inventory_stock(self, store, product):
    inventories, status = service.get_inventories_stock(store, product)
    return jsonify(inventories), status

@inventories.route('/inventory/<branch>/<product>', methods=['GET'])
@roles.token_required
def get_inventory_branch(self, branch, product):
    inventories, status = service.get_inventories_branch(branch, product)
    return jsonify(inventories), status

@inventories.route('/branch/<branch>', methods=['GET'])
@roles.token_required
@filters.filters
def get_inventory_on_branch(filter, self, branch):
    inventories, status = service.get_inventories_on_branch(branch, filter)
    return jsonify(inventories), status

@inventories.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['inventory.add'])
def add_inventory():
    if not request.json:
        abort(404)
    message, status = service.create_inventory(request.json)
    return jsonify({'msg': message}), status

@inventories.route('/availablity', methods=['POST'])
#@roles.token_required
def check_inventory():
    if not request.json:
        abort(404)
    message, status = service.get_products_status(request.json)
    return jsonify({'msg': message}), status

@inventories.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['inventory.edit'])
@roles.token_required
def update_inventory(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_inventory(id,request.json)
    return jsonify({'msg': message}), status


@inventories.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['inventory.delete'])
@roles.token_required
def delete_inventory(self, id):
    message, status = service.delete_inventory(id)
    return jsonify({'msg': message}), status