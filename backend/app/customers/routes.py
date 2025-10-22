import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import CustomerCreateSchema, CustomerUpdateSchema

from .service import CustomerService

__uri__ = 'customers'
__blueprint__ = 'customers'

customers = Blueprint(__uri__, __name__)

service = CustomerService()

@customers.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['customer.show'])
@filters.filters
def get_all_customers(self, filter):
    customers, status = service.get_customers(None, filter)
    if status == 200:
        return APIResponse.success(customers, "Customers retrieved successfully")
    return APIResponse.error("Failed to retrieve customers", status_code=status)

@customers.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['customer.show'])
@filters.filters
def get_customer(self, filter, id):
    customers, status = service.get_customers(id, filter)
    if status == 200:
        return APIResponse.success(customers, "Customer retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Customer not found")
    return APIResponse.error("Failed to retrieve customer", status_code=status)

@customers.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['customer.add'])
@validate_json(CustomerCreateSchema)
def add_customer(self, validated_data):
    message, status = service.create_customer(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Customer created successfully")
    return APIResponse.error(message, status_code=status)

@customers.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['customer.edit'])
@validate_json(CustomerUpdateSchema)
def update_customer(self, validated_data, id):
    message, status = service.update_customer(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Customer updated successfully")
    elif status == 404:
        return APIResponse.not_found("Customer not found")
    return APIResponse.error(message, status_code=status)


@customers.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['customer.delete'])
def delete_customer(self, id):
    message, status = service.delete_customer(id)
    if status == 200:
        return APIResponse.success(message, "Customer deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Customer not found")
    return APIResponse.error(message, status_code=status)

# 3D Printing Customer Routes
@customers.route('/<customer_id>/preferences', methods=['GET'])
@roles.token_required
def get_customer_preferences(self, customer_id):
    """Get 3D printing preferences for a customer"""
    try:
        from .model import Customer
        from app.utilities.db_utils import get_session_with_retries
        
        with get_session_with_retries() as session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                return APIResponse.not_found("Customer not found")
            
            data = {
                'preferred_materials': customer.preferred_materials,
                'quality_preference': customer.quality_preference,
                'color_preferences': customer.color_preferences,
                'special_requirements': customer.special_requirements
            }
            return APIResponse.success(data, "Customer preferences retrieved successfully")
    except Exception as e:
        return APIResponse.server_error(f'Error retrieving customer preferences: {str(e)}')

@customers.route('/<customer_id>/preferences', methods=['PUT'])
@roles.token_required
def update_customer_preferences(self, customer_id):
    """Update 3D printing preferences for a customer"""
    try:
        from .model import Customer
        from app.utilities.db_utils import get_session_with_retries
        from datetime import datetime, timezone
        
        data = request.get_json()
        if not data:
            return APIResponse.validation_error("No data provided")
        
        with get_session_with_retries() as session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                return APIResponse.not_found("Customer not found")
            
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
            
            result = {
                'preferred_materials': customer.preferred_materials,
                'quality_preference': customer.quality_preference,
                'color_preferences': customer.color_preferences,
                'special_requirements': customer.special_requirements
            }
            return APIResponse.success(result, "Customer preferences updated successfully")
    except Exception as e:
        return APIResponse.server_error(f'Error updating customer preferences: {str(e)}')

@customers.route('/<customer_id>/orders', methods=['GET'])
@roles.token_required
def get_customer_orders(self, customer_id):
    """Get all orders for a specific customer"""
    try:
        from .model import Customer
        from app.order.model import Order
        from app.utilities.db_utils import get_session_with_retries
        
        with get_session_with_retries() as session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                return APIResponse.not_found("Customer not found")
            
            orders = session.query(Order).filter_by(customer_id=customer_id).all()
            return APIResponse.success([order.json() for order in orders], "Customer orders retrieved successfully")
    except Exception as e:
        return APIResponse.server_error(f'Error retrieving customer orders: {str(e)}')
