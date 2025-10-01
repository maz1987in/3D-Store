import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import ShippingAddressService

__uri__ = 'address'
__blueprint__ = 'address'

address = Blueprint(__uri__, __name__)

service = ShippingAddressService()

@address.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['address.show'])
@roles.token_required
@filters.filters
def get_all_addresses(filter,self):
    addresses, status = service.get_addresses(None,filter)
    return jsonify(addresses), status


@address.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['address.show'])
@roles.token_required
@filters.filters
def get_address(filter,self, id):
    addresses, status = service.get_addresses(id, filter)
    return jsonify(addresses), status


@address.route('/', methods=['POST'])
@roles.token_required
def add_address(self):
    if not request.is_json:
        abort(400, 'Request must be JSON')
    data = request.json
    address_id = service.add_address(self.id, data)
    return jsonify({'address_id': address_id}), 201


@address.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['address.edit'])
@roles.token_required
def update_address(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_address(id,request.json)
    return jsonify({'msg': message}), status

@address.route('/<id>', methods=['DELETE'])
@roles.token_required
def delete_address(self, id):
    message, status = service.delete_address(self.id, id)
    if message:
        return jsonify({'msg': 'Address deleted'}), status
    else:
        abort(404, 'Address not found')

@address.route('/validate-shipping', methods=['POST'])
@roles.token_required
def validate_shipping_address_for_products(self):
    """Validate if products can be shipped to the address city"""
    if not request.json:
        abort(400, "Invalid payload")
    
    required_fields = ['address_id', 'product_ids']
    for field in required_fields:
        if field not in request.json:
            abort(400, f"Missing required field: {field}")
    
    address_id = request.json['address_id']
    product_ids = request.json['product_ids']
    
    if not isinstance(product_ids, list):
        abort(400, "product_ids must be a list")

    message, status = service.validate_shipping_address_for_products(address_id, product_ids)

    return jsonify(message), status