import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.decorators.validation import validate_json, validate_form_data
from app.utils.response import APIResponse
from .schemas import OrderCreateSchema, OrderUpdateSchema, PrintJobEstimateSchema

from .service import OrderService

__uri__ = 'orders'
__blueprint__ = 'orders'

orders = Blueprint(__uri__, __name__)

service = OrderService()

@orders.route('/', methods=['GET'])
@cross_origin()
@permissions.has_permission(['order.show'])
@filters.filters
def get_all_orders(filter,self):
    orders, status = service.get_orders(None,filter)
    if status == 200:
        return APIResponse.success(orders, "Orders retrieved successfully")
    else:
        return APIResponse.error("Failed to retrieve orders", status_code=status)

@orders.route('/<id>', methods=['GET'])
@cross_origin()
@permissions.has_permission(['order.show'])
@filters.filters
def get_order(filter,self, id):
    orders, status = service.get_orders(id, filter)
    if status == 200:
        return APIResponse.success(orders, "Order retrieved successfully")
    else:
        return APIResponse.error("Failed to retrieve order", status_code=status)

@orders.route('/', methods=['POST'])
@cross_origin()
@permissions.has_permission(['order.add'])
@validate_json(OrderCreateSchema)
def add_order(self, validated_data):
    message, status = service.create_order(validated_data)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)

@orders.route('/<id>', methods=['PATCH'])
@cross_origin()
@permissions.has_permission(['order.edit'])
@validate_json(OrderUpdateSchema)
def update_order(self, validated_data, id):
    message, status = service.update_order(id, validated_data)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)


@orders.route('/<id>', methods=['DELETE'])
@cross_origin()
@permissions.has_permission(['order.delete'])
def delete_order(self, id):
    message, status = service.delete_order(id)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)

# 3D Printing Order Routes
@orders.route('/print/estimate', methods=['POST'])
def estimate_print_cost():
    """Estimate the cost of a 3D print job"""
    try:
        from .model import Order, OrderItem
        from app.product.model import Product, PrintMaterial, PrintSettings, ProductPackaging
        from app.utilities.db_utils import get_session_with_retries
        from datetime import datetime, timezone
        
        data = request.get_json()
        if not data or not all(k in data for k in ['product_id', 'quantity', 'material_id', 'settings_id']):
            return jsonify({
                'status': 400,
                'message': 'Missing required fields: product_id, quantity, material_id, settings_id',
                'data': None
            }), 400
        
        with get_session_with_retries() as session:
            # Get product details
            product = session.query(Product).filter_by(id=data['product_id']).first()
            if not product:
                return jsonify({
                    'status': 404,
                    'message': 'Product not found',
                    'data': None
                }), 404
            
            # Get material details
            material = session.query(PrintMaterial).filter_by(id=data['material_id']).first()
            if not material:
                return jsonify({
                    'status': 404,
                    'message': 'Print material not found',
                    'data': None
                }), 404
            
            # Get settings details
            settings = session.query(PrintSettings).filter_by(id=data['settings_id']).first()
            if not settings:
                return jsonify({
                    'status': 404,
                    'message': 'Print settings not found',
                    'data': None
                }), 404
            
            # Calculate costs
            quantity = data['quantity']
            material_cost = float(material.cost_per_gram) * float(product.material_usage_grams or 0) * quantity
            printing_cost = float(product.base_price) * quantity
            packaging_cost = 0
            
            if data.get('packaging_id'):
                packaging = session.query(ProductPackaging).filter_by(id=data['packaging_id']).first()
                if packaging:
                    packaging_cost = float(packaging.cost) * quantity
            
            total_cost = material_cost + printing_cost + packaging_cost
            
            # Calculate estimated print time
            estimated_time = float(product.print_time_hours or 0) * quantity
            if settings.estimated_time_multiplier:
                estimated_time *= float(settings.estimated_time_multiplier)
            
            return jsonify({
                'status': 200,
                'message': 'Cost estimation successful',
                'data': {
                    'product': product.json(),
                    'material': material.json(),
                    'settings': settings.json(),
                    'packaging': packaging.json() if data.get('packaging_id') and packaging else None,
                    'quantity': quantity,
                    'cost_breakdown': {
                        'material_cost': material_cost,
                        'printing_cost': printing_cost,
                        'packaging_cost': packaging_cost,
                        'total_cost': total_cost
                    },
                    'estimated_print_time_hours': estimated_time,
                    'estimated_completion_date': None  # Would need to calculate based on printer availability
                }
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error estimating print cost: {str(e)}',
            'data': None
        }), 500

@orders.route('/<order_id>/print-jobs', methods=['GET'])
def get_order_print_jobs(order_id):
    """Get all print jobs for a specific order"""
    try:
        from .model import Order
        from app.utilities.db_utils import get_session_with_retries
        
        with get_session_with_retries() as session:
            order = session.query(Order).filter_by(id=order_id).first()
            if not order:
                return jsonify({
                    'status': 404,
                    'message': 'Order not found',
                    'data': []
                }), 404
            
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [job.json() for job in order.print_jobs]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving print jobs: {str(e)}',
            'data': []
        }), 500

@orders.route('/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update the status of an order"""
    try:
        from .model import Order
        from app.utilities.db_utils import get_session_with_retries
        from datetime import datetime, timezone
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'status': 400,
                'message': 'Missing status field',
                'data': None
            }), 400
        
        with get_session_with_retries() as session:
            order = session.query(Order).filter_by(id=order_id).first()
            if not order:
                return jsonify({
                    'status': 404,
                    'message': 'Order not found',
                    'data': None
                }), 404
            
            order.status = data['status']
            order.modified_date = datetime.now(timezone.utc)
            session.commit()
            
            return jsonify({
                'status': 200,
                'message': f'Order status updated to {data["status"]}',
                'data': order.json()
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error updating order status: {str(e)}',
            'data': None
        }), 500

