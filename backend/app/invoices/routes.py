from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, g, current_app
from app.common.queries import create_filters
from app.security import roles, permissions
from app.common import filters
from app.utilities.common_utils import equal_to, get_owner_id
from .service import InvoiceService


__uri__ = 'invoices'
__blueprint__ = 'invoices'

invoices = Blueprint(__uri__, __name__)

service = InvoiceService()

@invoices.route('/', methods=['GET'])
@roles.token_required
@filters.filters
def get_all_invoices(filter,self):
    response, status = service.get_invoices(None,filter)
    return jsonify({'invoices': response}), status

@invoices.route('/<id>', methods=['GET'])
#@cross_origin()
@roles.token_required
def get_invoice_by_id(self, id):
    #response, status = service.get_invoices_by_id(id)
    response, status = service.get_invoices(id, None)
    return jsonify({'invoices': response}), status

@invoices.route('/transaction/<transaction_id>', methods=['GET'])
#@cross_origin()
@roles.token_required
def get_invoice_by_transaction_id(self, transaction_id):
    response, status = service.get_invoices_by_transaction_id(transaction_id)
    if 'invoices.show.my' in g.permission:
        if not equal_to(response['user_id'], self.id):
            abort(403)
    return jsonify({'invoices': response}), status

# get_invoices_by_user_id
@invoices.route('/user/<user_id>', methods=['GET'])
#@cross_origin()
@roles.token_required
@filters.filters
def get_invoices_by_user_id(filter,self, user_id):
    response, status = service.get_invoices_by_user_id(user_id,filter)
   
    return jsonify({'invoices': response}), status
"""
@invoices.route('/customer_mobile/<mobile>', methods=['GET'])
@roles.token_required
@filters.filters
def get_invoices_by_customer_mobile(filter, self, mobile):
    response, status = service.get_invoices_by_customer_mobile(mobile, filter)
    return jsonify({'invoices': response}), status
"""
@invoices.route('/', methods=['POST'])
#@cross_origin()
@roles.token_required
def add_invoice(self):
    if not request.json:
        abort(400)
    response, status, id = service.create_invoice(request.json)
    return jsonify({'status': response, 'id': id}), status

@invoices.route('/return/', methods=['POST'])
#@cross_origin()
@roles.token_required
def create_invoice_refund(self):
    if not request.json:
        abort(400)
    response, status, id = service.create_invoice_refund(request.json)
    return jsonify({'status': response, 'id': id}), status

@invoices.route('/<id>', methods=['PATCH'])
#@cross_origin()
@roles.token_required
def update_invoice(self, id):
    message, status = service.update_invoice(id, request.json)
    return jsonify({'msg': message}), status

@invoices.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['invoices.delete'])
def delete_invoice(self, id):
    message, status = service.delete_invoice(id)
    return jsonify({'msg': message}), status

@invoices.route('/model/<model_type>', defaults={'model_id': None})
@invoices.route('/model/<model_type>/<model_id>', methods=['GET'])
#@cross_origin()
@roles.token_required
@filters.filters
def get_invoice_by_type_and_id_and_filter(filter,self,model_type=None, model_id=None):

    if 'invoices.show.my' in g.permission:
        if filter.queries is not None:
            filter.queries.append('user_id,eq,'+str(get_owner_id()))
        else:
            filter.queries = ['user_id,eq,'+str(get_owner_id())]
        filter.filters = create_filters(filter.queries)
        
    response, status = service.get_invoice_by_type_and_id_and_filter(model_type,model_id,filter)
    return jsonify({'invoices': response}), status