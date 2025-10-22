import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import CartItemAddSchema, CartItemUpdateSchema, CartCheckoutSchema

from .service import CartService

__uri__ = 'carts'
__blueprint__ = 'carts'

carts = Blueprint(__uri__, __name__)

service = CartService()

@carts.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['cart.show'])
@filters.filters
def get_all_carts(self, filter):
    carts, status = service.get_carts(None, filter)
    if status == 200:
        return APIResponse.success(carts, "Carts retrieved successfully")
    return APIResponse.error("Failed to retrieve carts", status_code=status)

@carts.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['cart.show'])
@filters.filters
def get_cart(self, filter, id):
    carts, status = service.get_carts(id, filter)
    if status == 200:
        return APIResponse.success(carts, "Cart retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Cart not found")
    return APIResponse.error("Failed to retrieve cart", status_code=status)

@carts.route('/my', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['cart.show'])
@filters.filters
def get_user_carts(self, filter):
    carts, status = service.get_carts_my(self.id, filter)
    if status == 200:
        return APIResponse.success(carts, "User carts retrieved successfully")
    return APIResponse.error("Failed to retrieve user carts", status_code=status)

@carts.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['cart.add'])
def add_cart(self):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.create_cart(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Cart created successfully")
    return APIResponse.error(message, status_code=status)

@carts.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['cart.edit'])
def update_cart(self, id):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.update_cart(id, request.json)
    if status == 200:
        return APIResponse.success(message, "Cart updated successfully")
    elif status == 404:
        return APIResponse.not_found("Cart not found")
    return APIResponse.error(message, status_code=status)


@carts.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['cart.delete'])
def delete_cart(self, id):
    message, status = service.delete_cart(id)
    if status == 200:
        return APIResponse.success(message, "Cart deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Cart not found")
    return APIResponse.error(message, status_code=status)

# add item to cart
@carts.route('/<id>/items', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['cart.add'])
@validate_json(CartItemAddSchema)
def add_item_to_cart(self, validated_data, id):
    message, status = service.create_item(id, validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Item added to cart successfully")
    return APIResponse.error(message, status_code=status)

# update item in cart
@carts.route('/<id>/items/<item_id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['cart.edit'])
@validate_json(CartItemUpdateSchema)
def update_item_in_cart(self, validated_data, id, item_id):
    message, status = service.update_item(id, item_id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Cart item updated successfully")
    elif status == 404:
        return APIResponse.not_found("Cart item not found")
    return APIResponse.error(message, status_code=status)

# delete item from cart
@carts.route('/<id>/items/<item_id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['cart.delete'])
def delete_item_from_cart(self, id, item_id):
    message, status = service.delete_item(id, item_id)
    if status == 200:
        return APIResponse.success(message, "Cart item deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Cart item not found")
    return APIResponse.error(message, status_code=status)

# get all items in cart
@carts.route('/<id>/items', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['cart.show'])
def get_items_in_cart(self, id):
    items, status = service.get_cart_items(id)
    if status == 200:
        return APIResponse.success(items, "Cart items retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Cart not found")
    return APIResponse.error("Failed to retrieve cart items", status_code=status)
