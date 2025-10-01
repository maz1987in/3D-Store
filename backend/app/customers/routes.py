import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import CustomerService

__uri__ = 'customers'
__blueprint__ = 'customers'

customers = Blueprint(__uri__, __name__)

service = CustomerService()

@customers.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['customer.show'])
@roles.token_required
@filters.filters
def get_all_customers(filter,self):
    customers, status = service.get_customers(None,filter)
    return jsonify(customers), status

@customers.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['customer.show'])
@roles.token_required
@filters.filters
def get_customer(filter,self, id):
    customers, status = service.get_customers(id, filter)
    return jsonify(customers), status

@customers.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['customer.add'])
@roles.token_required
def add_customer(self):
    if not request.json:
        abort(404)
    message, status = service.create_customer(request.json)
    return jsonify({'msg': message}), status

@customers.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['customer.edit'])
@roles.token_required
def update_customer(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_customer(id,request.json)
    return jsonify({'msg': message}), status


@customers.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['customer.delete'])
@roles.token_required
def delete_customer(self, id):
    message, status = service.delete_customer(id)
    return jsonify({'msg': message}), status

# 3D Printing Customer Routes
@customers.route('/<customer_id>/preferences', methods=['GET'])
def get_customer_preferences(customer_id):
    """Get 3D printing preferences for a customer"""
    try:
        from .model import Customer
        from app.utilities.db_utils import get_session_with_retries
        
        with get_session_with_retries() as session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                return jsonify({
                    'status': 404,
                    'message': 'Customer not found',
                    'data': None
                }), 404
            
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': {
                    'preferred_materials': customer.preferred_materials,
                    'quality_preference': customer.quality_preference,
                    'color_preferences': customer.color_preferences,
                    'special_requirements': customer.special_requirements
                }
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving customer preferences: {str(e)}',
            'data': None
        }), 500

@customers.route('/<customer_id>/preferences', methods=['PUT'])
def update_customer_preferences(customer_id):
    """Update 3D printing preferences for a customer"""
    try:
        from .model import Customer
        from app.utilities.db_utils import get_session_with_retries
        from datetime import datetime, timezone
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 400,
                'message': 'No data provided',
                'data': None
            }), 400
        
        with get_session_with_retries() as session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                return jsonify({
                    'status': 404,
                    'message': 'Customer not found',
                    'data': None
                }), 404
            
            # Update preferences
            if 'preferred_materials' in data:
                customer.preferred_materials = data['preferred_materials']
            if 'quality_preference' in data:
                customer.quality_preference = data['quality_preference']
            if 'color_preferences' in data:
                customer.color_preferences = data['color_preferences']
            if 'special_requirements' in data:
                customer.special_requirements = data['special_requirements']
            
            customer.modified_date = datetime.now(timezone.utc)
            session.commit()
            
            return jsonify({
                'status': 200,
                'message': 'Customer preferences updated successfully',
                'data': {
                    'preferred_materials': customer.preferred_materials,
                    'quality_preference': customer.quality_preference,
                    'color_preferences': customer.color_preferences,
                    'special_requirements': customer.special_requirements
                }
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error updating customer preferences: {str(e)}',
            'data': None
        }), 500

@customers.route('/<customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):
    """Get all orders for a specific customer"""
    try:
        from .model import Customer
        from app.order.model import Order
        from app.utilities.db_utils import get_session_with_retries
        
        with get_session_with_retries() as session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                return jsonify({
                    'status': 404,
                    'message': 'Customer not found',
                    'data': []
                }), 404
            
            orders = session.query(Order).filter_by(customer_id=customer_id).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [order.json() for order in orders]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving customer orders: {str(e)}',
            'data': []
        }), 500