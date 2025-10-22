import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import AddressCreateSchema, AddressUpdateSchema

from .service import ShippingAddressService

__uri__ = 'address'
__blueprint__ = 'address'

address = Blueprint(__uri__, __name__)

service = ShippingAddressService()

@address.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['address.show'])
@filters.filters
def get_all_addresses(self, filter):
    addresses, status = service.get_addresses(None, filter)
    if status == 200:
        return APIResponse.success(addresses, "Addresses retrieved successfully")
    return APIResponse.error("Failed to retrieve addresses", status_code=status)


@address.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['address.show'])
@filters.filters
def get_address(self, filter, id):
    addresses, status = service.get_addresses(id, filter)
    if status == 200:
        return APIResponse.success(addresses, "Address retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Address not found")
    return APIResponse.error("Failed to retrieve address", status_code=status)


@address.route('/', methods=['POST'])
@roles.token_required
@validate_json(AddressCreateSchema)
def add_address(self, validated_data):
    validated_data['user_id'] = self.id  # Set user_id from authenticated user
    address_id = service.add_address(self.id, validated_data)
    if address_id:
        return APIResponse.created({'address_id': address_id}, "Address created successfully")
    return APIResponse.error("Failed to create address", status_code=400)


@address.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['address.edit'])
@validate_json(AddressUpdateSchema)
def update_address(self, validated_data, id):
    message, status = service.update_address(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Address updated successfully")
    elif status == 404:
        return APIResponse.not_found("Address not found")
    return APIResponse.error(message, status_code=status)

@address.route('/<id>', methods=['DELETE'])
@roles.token_required
def delete_address(self, id):
    message, status = service.delete_address(self.id, id)
    if message:
        return APIResponse.success({'msg': 'Address deleted'}, "Address deleted successfully")
    return APIResponse.not_found("Address not found")

@address.route('/validate-shipping', methods=['POST'])
@roles.token_required
def validate_shipping_address_for_products(self):
    """Validate if products can be shipped to the address city"""
    if not request.json:
        return APIResponse.error("Invalid payload", status_code=400)
    
    required_fields = ['address_id', 'product_ids']
    for field in required_fields:
        if field not in request.json:
            return APIResponse.validation_error(f"Missing required field: {field}")
    
    address_id = request.json['address_id']
    product_ids = request.json['product_ids']
    
    if not isinstance(product_ids, list):
        return APIResponse.validation_error("product_ids must be a list")

    message, status = service.validate_shipping_address_for_products(address_id, product_ids)
    
    if status == 200:
        return APIResponse.success(message, "Shipping validation successful")
    return APIResponse.error(message, status_code=status)
