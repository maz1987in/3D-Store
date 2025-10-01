from flask import Blueprint, abort, request, jsonify
from app.common import filters
from app.security import roles
from .service import ShippingService

__uri__ = 'shipping'
__blueprint__ = 'shipping'
shipping = Blueprint(__uri__, __name__)
service = ShippingService()

@shipping.route('/', methods=['GET'])
@roles.token_required
@filters.filters
def get_all_shipping_info(filter,self):
    """Get all shipping information."""
    result, status = service.get_shipping(None,filter)
    return jsonify(result), status

@shipping.route('/<id>', methods=['GET'])
@roles.token_required
def get_shipping_infoby_id(self, id):
    """Get shipping information by ID."""
    result, status = service.get_shipping(id, None)
    return jsonify(result), status

@shipping.route('/order/<order_id>', methods=['GET'])
@roles.token_required
def get_shipping_info(self, order_id):
    """Get shipping information for a specific order."""
    result, status = service.get_shipping_by_order_id(order_id)
    return jsonify(result), status

@shipping.route('/<order_id>', methods=['POST', 'PUT'])
@roles.token_required
def add_or_update_shipping_info(self, order_id):
    """Create or update shipping information for an order."""
    if not request.json:
        abort(400, "Invalid payload")
    message, status = service.create_or_update_shipping(order_id, request.json)
    return jsonify({'message': message}), status