import os
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from app.common import filters
from app.security import roles, permissions
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
def get_payment_transactions(filter,self):
    payment_transactions, status = service.get_all_payment_transactions(None,filter)
    return jsonify(payment_transactions), status

@payment_transactions.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def get_payment(self,id):
    payment_transactions, status = service.get_all_payment_transactions(id,None)
    return jsonify(payment_transactions), status

@payment_transactions.route('/model/<model_type>', defaults={'model_id': None})
@payment_transactions.route('/model/<model_type>/<model_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
@filters.filters
def get_payment_by_model(filter,self,model_type=None, model_id=None):
    payment_transactions = service.get_model_payment_transactions(model_type,model_id,filter)
    return jsonify(payment_transactions)

@payment_transactions.route('/reference/<reference_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def get_payment_by_reference_id(self,reference_id):
    payment_transactions, status = service.get_payment_transaction_by_reference_id(reference_id)
    return jsonify({'payment_transactions': payment_transactions}), status

@payment_transactions.route('/transaction/<gateway_transaction_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def get_payment_by_gateway_transaction_id(self, gateway_transaction_id):
    payment_transactions = service.get_payment_transaction_by_gateway_transaction_id(gateway_transaction_id)
    return jsonify({'payment_transactions': payment_transactions})

@payment_transactions.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['payment_transaction.add'])
def add_payment():
    if not request.json :
        abort(404)    
    message, status, pt_id = service.create_payment_transaction(request.json)
    return jsonify(pt_id), status

@payment_transactions.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.edit'])
def update_payment(self, id):
    message, status = service.update_payment_transaction(id, request.json)
    return jsonify({'msg': message}), status

@payment_transactions.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.delete'])
def delete_payment(self, id):
    message, status = service.delete_payment_transaction(id)
    return jsonify({'msg': message}), status


@payment_transactions.route('/check/<reference_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def check_payment_by_reference_id(self,reference_id):
    payment_transactions , status = service.check_payment_transaction_by_reference_id(reference_id)
    return jsonify({'payment_transactions': payment_transactions}), status


@payment_transactions.route('/payment_config', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_config.show'])
@filters.filters
def get_payment_config(filter,self):
    payment_config = service.get_payment_config(None,filter)
    return jsonify(payment_config)


@payment_transactions.route('/payment_config', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['payment_config.add'])
def add_payment_config(self):
    if not request.json :
        abort(404)    
    message, status = service.create_payment_config(request.json)
    return jsonify({'msg': message}), status

@payment_transactions.route('/payment_config/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_config.show'])
def get_payment_config_by_id(self,id):
    payment_transactions = service.get_payment_config(id,None)
    return jsonify(payment_transactions)

@payment_transactions.route('/payment_config/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['payment_config.edit'])
def update_payment_config(self, id):
    message, status = service.update_payment_config(id, request.json)
    return jsonify({'msg': message}), status

@payment_transactions.route('/payment_config/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['payment_config.delete'])
def delete_payment_config(self, id):
    message, status = service.delete_payment_config(id)
    return jsonify({'msg': message}), status

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
    return jsonify({'payment_transactions': result})


@payment_transactions.route('/payment_gateway', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_transaction.show'])
def get_payment_transactions_gateways(self):
    payment_transactions, status = service.get_gateways()
    return jsonify({'gateways' : payment_transactions}), status

@payment_transactions.route('/payment_gateway', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['payment_config.add'])
def add_payment_gateway(self):
    if not request.json :
        abort(404)    
    message, status = service.create_payment_gateway(request.json)
    return jsonify({'msg': message}), status

@payment_transactions.route('/payment_gateway/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['payment_config.delete'])
def delete_payment_gateway(self, id):
    message, status = service.delete_payment_gateway(id)
    return jsonify({'msg': message}), status

@payment_transactions.route('/payment_type', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['payment_type.show'])
def get_payment_type(self):
    payment_types = service.get_payment_type()
    payment_types = [payment_type.name for payment_type in payment_types]
    return jsonify({'payment_type' : payment_types})