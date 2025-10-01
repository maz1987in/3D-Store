import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import CartService

__uri__ = 'carts'
__blueprint__ = 'carts'

carts = Blueprint(__uri__, __name__)

service = CartService()

@carts.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['cart.show'])
@roles.token_required
@filters.filters
def get_all_carts(filter,self):
    carts, status = service.get_carts(None,filter)
    return jsonify(carts), status

@carts.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['cart.show'])
@roles.token_required
@filters.filters
def get_cart(filter,self, id):
    carts, status = service.get_carts(id, filter)
    return jsonify(carts), status

@carts.route('/my', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['cart.show'])
@roles.token_required
@filters.filters
def get_user_carts(filter,self):
    carts, status = service.get_carts_my(self.id,filter)
    return jsonify(carts), status

@carts.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['cart.add'])
def add_cart():
    if not request.json:
        abort(404)
    message, status = service.create_cart(request.json)
    return jsonify({'msg': message}), status

@carts.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['cart.edit'])
@roles.token_required
def update_cart(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_cart(id,request.json)
    return jsonify({'msg': message}), status


@carts.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['cart.delete'])
@roles.token_required
def delete_cart(self, id):
    message, status = service.delete_cart(id)
    return jsonify({'msg': message}), status

# add item to cart
@carts.route('/<id>/items', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['cart.add'])
def add_item_to_cart(id):
    if not request.json:
        abort(404)
    message, status = service.create_item(id,request.json)
    return jsonify({'msg': message}), status

# update item in cart
@carts.route('/<id>/items/<item_id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['cart.edit'])
def update_item_in_cart(id,item_id):
    if not request.json:
        abort(404)
    message, status = service.update_item(id,item_id,request.json)
    return jsonify({'msg': message}), status

# delete item from cart
@carts.route('/<id>/items/<item_id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['cart.delete'])
def delete_item_from_cart(id,item_id):
    message, status = service.delete_item(id,item_id)
    return jsonify({'msg': message}), status
# get all items in cart
@carts.route('/<id>/items', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['cart.show'])
def get_items_in_cart(id):
    items, status = service.get_cart_items(id)
    return jsonify(items), status