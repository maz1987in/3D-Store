import os
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from app.common import filters
from app.security import roles, permissions
from app.utils.response import APIResponse
from .service import PaymentTransactionsService
from config import FileUploadConfig

__uri__ = 'payment_transactions_transactions'
__blueprint__ = 'payment_transactions'

payment_transactions = Blueprint(__uri__, __name__)

service = PaymentTransactionsService()

@payment_transactions.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
@filters.filters
def get_payment_transactions(self, filter):
    payment_transactions, status = service.get_all_payment_transactions(None, filter)
    if status == 200:
        return APIResponse.success(payment_transactions, "Payment transactions retrieved successfully")
    return APIResponse.error("Failed to retrieve payment transactions", status_code=status)

@payment_transactions.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def get_payment(self, id):
    payment_transactions, status = service.get_all_payment_transactions(id, None)
    if status == 200:
        return APIResponse.success(payment_transactions, "Payment transaction retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Payment transaction not found")
    return APIResponse.error("Failed to retrieve payment transaction", status_code=status)

@payment_transactions.route('/model/<model_type>', defaults={'model_id': None})
@payment_transactions.route('/model/<model_type>/<model_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
@filters.filters
def get_payment_by_model(self, filter, model_type=None, model_id=None):
    payment_transactions = service.get_model_payment_transactions(model_type, model_id, filter)
    return APIResponse.success(payment_transactions, "Model payment transactions retrieved successfully")

@payment_transactions.route('/reference/<reference_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def get_payment_by_reference_id(self, reference_id):
    payment_transactions, status = service.get_payment_transaction_by_reference_id(reference_id)
    if status == 200:
        return APIResponse.success({'payment_transactions': payment_transactions}, "Payment transaction retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Payment transaction not found")
    return APIResponse.error("Failed to retrieve payment transaction", status_code=status)

@payment_transactions.route('/transaction/<gateway_transaction_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def get_payment_by_gateway_transaction_id(self, gateway_transaction_id):
    payment_transactions = service.get_payment_transaction_by_gateway_transaction_id(gateway_transaction_id)
    return APIResponse.success({'payment_transactions': payment_transactions}, "Gateway transaction retrieved successfully")

@payment_transactions.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.add'])
def add_payment(self):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status, pt_id = service.create_payment_transaction(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(pt_id, message or "Payment transaction created successfully")
    return APIResponse.error(message, status_code=status)

@payment_transactions.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.edit'])
def update_payment(self, id):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.update_payment_transaction(id, request.json)
    if status == 200:
        return APIResponse.success(message, "Payment transaction updated successfully")
    elif status == 404:
        return APIResponse.not_found("Payment transaction not found")
    return APIResponse.error(message, status_code=status)

@payment_transactions.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.delete'])
def delete_payment(self, id):
    message, status = service.delete_payment_transaction(id)
    if status == 200:
        return APIResponse.success(message, "Payment transaction deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Payment transaction not found")
    return APIResponse.error(message, status_code=status)


@payment_transactions.route('/check/<reference_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def check_payment_by_reference_id(self, reference_id):
    payment_transactions, status = service.check_payment_transaction_by_reference_id(reference_id)
    if status == 200:
        return APIResponse.success({'payment_transactions': payment_transactions}, "Payment status checked successfully")
    return APIResponse.error("Failed to check payment status", status_code=status)


@payment_transactions.route('/payment_config', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_config.show'])
@filters.filters
def get_payment_config(self, filter):
    payment_config = service.get_payment_config(None, filter)
    return APIResponse.success(payment_config, "Payment configuration retrieved successfully")


@payment_transactions.route('/payment_config', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['payment_config.add'])
def add_payment_config(self):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.create_payment_config(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Payment configuration created successfully")
    return APIResponse.error(message, status_code=status)

@payment_transactions.route('/payment_config/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_config.show'])
def get_payment_config_by_id(self, id):
    payment_transactions = service.get_payment_config(id, None)
    return APIResponse.success(payment_transactions, "Payment configuration retrieved successfully")

@payment_transactions.route('/payment_config/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['payment_config.edit'])
def update_payment_config(self, id):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.update_payment_config(id, request.json)
    if status == 200:
        return APIResponse.success(message, "Payment configuration updated successfully")
    elif status == 404:
        return APIResponse.not_found("Payment configuration not found")
    return APIResponse.error(message, status_code=status)

@payment_transactions.route('/payment_config/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['payment_config.delete'])
def delete_payment_config(self, id):
    message, status = service.delete_payment_config(id)
    if status == 200:
        return APIResponse.success(message, "Payment configuration deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Payment configuration not found")
    return APIResponse.error(message, status_code=status)

@payment_transactions.route('/payment_config/online', methods=['GET'])
#@cross_origin()
@roles.token_required
def get_payment_config_online_defult(self):
    payment_transactions = service.get_payment_config_online_default()
    result = [] 
    for payment in payment_transactions:   
        data = {}   
        data['name'] = payment.name
        result.append(data)
    return APIResponse.success({'payment_transactions': result}, "Online payment configurations retrieved successfully")


@payment_transactions.route('/payment_gateway', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def get_payment_transactions_gateways(self):
    payment_transactions, status = service.get_gateways()
    if status == 200:
        return APIResponse.success({'gateways': payment_transactions}, "Payment gateways retrieved successfully")
    return APIResponse.error("Failed to retrieve payment gateways", status_code=status)

@payment_transactions.route('/payment_gateway', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['payment_config.add'])
def add_payment_gateway(self):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.create_payment_gateway(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Payment gateway created successfully")
    return APIResponse.error(message, status_code=status)

@payment_transactions.route('/payment_gateway/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['payment_config.delete'])
def delete_payment_gateway(self, id):
    message, status = service.delete_payment_gateway(id)
    if status == 200:
        return APIResponse.success(message, "Payment gateway deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Payment gateway not found")
    return APIResponse.error(message, status_code=status)

@payment_transactions.route('/payment_type', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_type.show'])
def get_payment_type(self):
    payment_types = service.get_payment_type()
    payment_types = [payment_type.name for payment_type in payment_types]
    return APIResponse.success({'payment_type': payment_types}, "Payment types retrieved successfully")
