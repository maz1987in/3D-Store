from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, g, current_app
from app.common.queries import create_filters
from app.security import roles, permissions
from app.common import filters
from app.utilities.common_utils import equal_to, get_owner_id
from .service import PaymentService


__uri__ = 'payments'
__blueprint__ = 'payments'

payments = Blueprint(__uri__, __name__)

payment_service = PaymentService()


@payments.route('/', methods=['GET'])
@roles.token_required
@filters.filters
def get_all_invoices(filter,self):
    response, status = payment_service.get_payments(None,filter)
    return jsonify({'payments': response}), status

@payments.route('/<id>', methods=['GET'])
def get_payment(id):
    filter = request.args
    result, status = payment_service.get_payments(id, filter)
    return jsonify({'payments': result}), status

@payments.route('/invoice/<invoice_id>', methods=['GET'])
def get_payment_by_invoice_id(invoice_id):
    result, status = payment_service.get_payment_by_invoice_id(invoice_id)
    return jsonify({'payments': result}), status

@payments.route('/', methods=['POST'])
def create_payment():
    data = request.json
    result, status = payment_service.create_payment(data)
    return jsonify({'payments': result}), status

@payments.route('/<id>', methods=['PATCH'])
def update_payment(id):
    data = request.json
    result, status = payment_service.update_payment(id, data)
    return jsonify({'payments': result}), status

@payments.route('/<id>', methods=['DELETE'])
def delete_payment(id):
    result, status = payment_service.delete_payment(id)
    return jsonify({'payments': result}), status
