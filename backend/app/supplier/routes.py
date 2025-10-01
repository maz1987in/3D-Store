import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import SupplierService

__uri__ = 'suppliers'
__blueprint__ = 'suppliers'

suppliers = Blueprint(__uri__, __name__)

service = SupplierService()

@suppliers.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['supplier.show'])
#@roles.token_required
@filters.filters
def get_all_suppliers(filter):
    suppliers, status = service.get_suppliers(None,filter)
    return jsonify(suppliers), status

@suppliers.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['supplier.show'])
#@roles.token_required
@filters.filters
def get_supplier(filter, id):
    suppliers, status = service.get_suppliers(id, filter)
    return jsonify(suppliers), status

@suppliers.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['supplier.add'])
def add_supplier():
    if not request.json:
        abort(404)
    message, status = service.create_supplier(request.json)
    return jsonify({'msg': message}), status

@suppliers.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['supplier.edit'])
@roles.token_required
def update_supplier(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_supplier(id,request.json)
    return jsonify({'msg': message}), status


@suppliers.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['supplier.delete'])
@roles.token_required
def delete_supplier(self, id):
    message, status = service.delete_supplier(id)
    return jsonify({'msg': message}), status