import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import StoreService

__uri__ = 'stores'
__blueprint__ = 'stores'

stores = Blueprint(__uri__, __name__)

service = StoreService()

@stores.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['store.show'])
@roles.token_required
@filters.filters
def get_all_stores(filter,self):
    stores, status = service.get_stores(None,filter)
    return jsonify(stores), status

@stores.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['store.show'])
@roles.token_required
@filters.filters
def get_store(filter,self, id):
    stores, status = service.get_stores(id, filter)
    return jsonify(stores), status

@stores.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['store.add'])
def add_store():
    if not request.json:
        abort(404)
    message, status = service.create_store(request.json)
    return jsonify({'msg': message}), status

@stores.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['store.edit'])
@roles.token_required
def update_store(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_store(id,request.json)
    return jsonify({'msg': message}), status


@stores.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['store.delete'])
@roles.token_required
def delete_store(self, id):
    message, status = service.delete_store(id)
    return jsonify({'msg': message}), status